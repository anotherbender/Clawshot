"""Precollected inventory and deterministic pool replacement, before the fill.

Starting items are not story completion. Native fixed bonuses stay at unshuffled
checks; only copies actually in the shuffled pool are replaced by junk.
"""

from collections import Counter
from collections.abc import Mapping
from dataclasses import replace

from clawshot import starting
from clawshot.generate.fill import FillError, Settings, shuffled_locations
from clawshot.progressive import FAMILY_BY_ITEM
from clawshot.settings import CATALOG
from clawshot.world.model import World


def prepare(world: World, settings: Settings) -> tuple[Settings, World]:
    if not settings.starting_items and not settings.starting_hearts:
        return settings, world
    fixed = starting.prefixes(settings.starting_items)
    if missing := sorted(set(fixed) - world.items.keys()):
        raise FillError(f"Starting inventory is not in this world: {missing}")
    counts = starting.copies(settings.starting_items)
    if missing := sorted(set(counts) - world.progressive.keys()):
        raise FillError(f"Starting upgrades need native progressive chains: {missing}")
    held = (*fixed, *counts.elements(), *("Heart Container" for _ in range(settings.starting_hearts)))
    if settings.starting_hearts and "Heart Container" not in world.items:
        raise FillError("Starting hearts need Heart Container in this world's item table")
    world = replace(world, start_items=(*world.start_items, *held))
    inventory = dict(world.settings.get("age_return_fill_inventory", {}))
    families = list(world.settings.get("age_return_fill_families", ()))
    for item, inherited in CATALOG.get("starting_return_bypasses", {}).items():
        if item in held:
            for dependency in inherited:
                inventory.pop(dependency, None)
                if dependency not in families:
                    families.append(dependency)
    world = replace(
        world,
        settings={
            **world.settings,
            "age_return_fill_inventory": inventory,
            "age_return_fill_families": families,
        },
    )
    # Missing songs leave junk, never extra copies of other songs. Use the existing
    # ordered palette stage rather than a post-fill repair or a new fill exception.
    if settings.songs == "song" and set(settings.starting_items).intersection(starting.SONGS):
        palette = tuple(item for item, info in world.items.items() if info.type == "Song") + (starting.JUNK,)
        prior = settings.location_type_items.get("Song")
        if prior is not None:
            palette = tuple(item for item in palette if item in prior)
        settings = replace(
            settings,
            exclusive_location_types=tuple(kind for kind in settings.exclusive_location_types if kind != "Song"),
            location_type_items={**settings.location_type_items, "Song": palette},
        )
    return settings, world


def replace_pool(world: World, settings: Settings, vanilla: Mapping[str, str]) -> dict[str, str]:
    """Remove one pooled copy per initial item/tier; preserve world order and pool size."""
    if not settings.starting_items and not settings.starting_hearts:
        return {}
    wanted = Counter(item for item in settings.starting_items if item not in FAMILY_BY_ITEM)
    wanted.update(starting.copies(settings.starting_items))
    wanted["Heart Container"] += settings.starting_hearts
    overrides = {}
    for name in shuffled_locations(world, settings):
        item = vanilla.get(name, world.locations[name].vanilla)
        if wanted[item]:
            overrides[name] = starting.JUNK
            wanted[item] -= 1
    return overrides
