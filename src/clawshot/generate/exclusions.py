"""Capacity validation for player exclusions, under the ordinary placement predicate."""

from collections.abc import Mapping

from clawshot.generate.fill import FillError, Settings, allowed, shuffled_locations, with_screens
from clawshot.generate.progressive import normalize_pool
from clawshot.world.model import World
from clawshot.world.rules import ADULT, CHILD
from clawshot.world.search import Search


def _check_capacity(
    world: World, settings: Settings, locations: list[str], pool: list[str], fixed: Mapping[str, str]
) -> None:
    """Prove a full delivery-capacity matching without committing any placements.

    The existing ordered stages and final oracles still place/prove progression. Checking every slot, not just
    counting junk, preserves the capacity needed by held items, shop refills, native palettes and dungeon items.
    """
    families = world.settings.get("age_return_fill_families", ())
    kit = world.age_return is not None and world.settings.get("age_return_guarantee", False) and families
    maximal = Search(world, [*pool, *fixed.values()]) if kit else None
    bypass = world.settings.get("age_return_bypass_families", ())
    compatible = {}
    for item in dict.fromkeys(pool):
        info = world.items[item]
        family = info.alias[0] if info.alias is not None else item
        compatible[item] = [
            name
            for name in locations
            if allowed(world, settings, name, item)
            and (
                not kit
                or family not in families
                or (
                    maximal.can_access(world.locations[name], ADULT)
                    and (family not in bypass or not maximal.can_access(world.locations[name], CHILD))
                )
            )
        ]
    assigned: dict[str, int] = {}

    def match(index: int, seen: set[str]) -> bool:
        candidates = compatible[pool[index]]
        for name in candidates:
            if name not in seen and name not in assigned:
                assigned[name] = index
                return True
        for name in candidates:
            if name in seen:
                continue
            seen.add(name)
            previous = assigned[name]
            if match(previous, seen):
                assigned[name] = index
                return True
        return False

    for index in sorted(range(len(pool)), key=lambda index: len(compatible[pool[index]])):
        if not match(index, set()):
            item = pool[index]
            raise FillError(
                f"Excluded locations make this item pool impossible: no compatible capacity for {item!r}. "
                "Remove exclusions or change the shuffled kinds/song placement. "
                f"Excluded: {list(settings.excluded_locations)}",
                stage="excluded locations",
                item=item,
                allowed=tuple(compatible[item]),
            )


def validate_fixed(world: World, settings: Settings, fixed: Mapping[str, str]) -> None:
    bad = [name for name in settings.excluded_locations if name in fixed and world.items[fixed[name]].progression]
    if bad:
        raise FillError(
            f"Excluded locations still hold unshuffled progression: {bad}. "
            "Shuffle those checks or remove them from the exclusion list.",
            stage="excluded locations",
        )


def validate_exclusions(world: World, settings: Settings, vanilla: Mapping[str, str] | None = None) -> None:
    """Refuse impossible capacity before retries, using the normalized pool and native overrides when available."""
    if not settings.excluded_locations:
        return
    vanilla = dict(vanilla or {})
    vanilla.update(normalize_pool(world, settings, vanilla))
    locations = shuffled_locations(world, settings)
    moving = set(locations)
    fixed = {
        name: vanilla.get(name, loc.vanilla)
        for name, loc in world.locations.items()
        if name not in moving and loc.n64_only is None and vanilla.get(name, loc.vanilla) is not None
    }
    validate_fixed(world, settings, fixed)
    pool = [vanilla.get(name, world.locations[name].vanilla) for name in locations]
    _check_capacity(with_screens(world, locations, pool, fixed), settings, locations, pool, fixed)
