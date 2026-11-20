"""Master Sword shuffle in a seed (Round 19, cs19c; ``plans/rounds/r18-master-sword-design.md`` sections 7-9).

Opt-in (``Settings.shuffle_master_sword``), off by default. The world declares the logic setting
``shuffle_master_sword`` (``world.toml``, false) and the helper ``adult_sword``: an adult holding an owned durable blade
(Master Sword or Biggoron Sword; the breakable Giant's Knife never counts), or any adult while the setting is false.
Every rule whose adult branch assumed OoT Randomizer's always-held Master Sword reads ``adult_sword``
(``data/world/remake/master_sword.toml`` and the entries it lists), with child-only weapons gated to the child and the
alternatives each rule names kept for the adult. Off, the setting is a constant false, so each such rule folds to its
translated form: the same logic.

:func:`prepare_spec` sets the setting to the seed's choice; logic naming it must agree, as ``door_of_time`` must
(``clawshot.generate.prepare``), so only the option that also writes the runtime makes adult rules swordless. Off,
nothing changes: no pedestal check, the same spec, pool and output. On:

1. ``free_time_travel`` must be on. cs19c's conservative boundary: a swordless adult may be unable to clear the Forest
   Temple, the native child-return gate, and this module adds no other post-pull guarantee.
2. The first pull becomes its own check, :data:`PEDESTAL` (:data:`TYPE`), beside the world's first-pull event
   (``age_pull_event``; OoT Randomizer's 'Master Sword Pedestal', Overworld.json:1326) with that event's rule, giving
   :data:`ITEM`: the shuffled pool holds exactly one Master Sword. The time-travel event, Rauru's reward slot and the
   first-arrival song stay separate. ``clawshot.generate.fill.shuffled_locations`` shuffles :data:`TYPE` with the
   setting; it is never a ``shuffle`` kind.

:func:`restrict_settings` then holds :data:`ITEM` to :data:`ITEM_DESTINATIONS` (the chest adapter; no gift, shop,
scrub, floor or Skulltula grant of a ``Weapon_*`` actor is proven) and the pedestal to :func:`pedestal_items`: the
plain single grants its standard ``GetPouchContentByActorName`` route (``clawshot.patch.master_sword``) can give.
Explicit settings may narrow these holds, never widen them. The fill places the pedestal in its palette stage and the
Master Sword in the type-held stage, as for every other held item. Built, not played.
"""

import tomllib
from collections.abc import Mapping
from dataclasses import replace
from functools import cache
from pathlib import Path
from typing import Any

from clawshot.generate.fill import SHOP_ONLY_PREFIX, SWORD_PEDESTAL_SOURCE, FillError, Settings
from clawshot.progressive import CHAINS, FAMILY_BY_ITEM
from clawshot.world.load import WorldError
from clawshot.world.model import World

SETTING = "shuffle_master_sword"
"""The world's logic setting ``adult_sword`` and the finale rules read; a seed sets it to its own choice."""
TRAVEL = "free_time_travel"
TYPE = SWORD_PEDESTAL_SOURCE
"""The pedestal check's location type: shuffled only by the setting (``clawshot.generate.fill.shuffled_locations``)."""
PEDESTAL = "Master Sword Pedestal"
"""OoT Randomizer's name for the first pull (LocationList.py; Overworld.json:1326)."""
ITEM = "Master Sword"
ITEM_DESTINATIONS = ("Chest",)
SOURCE = (
    "Round 19 cs19c (plans/rounds/r18-master-sword-design.md section 9.1): the first pull's one ownership writer, "
    "DoorOfTime/Event115 (census 'DoorOfTime Event115 (Weapon_Sword_Master)'), as its own check; OoT Randomizer "
    "location 'Master Sword Pedestal' (Overworld.json:1326), whose rule is the first-pull event's."
)
ITEM_ACTORS = Path(__file__).resolve().parents[1] / "data" / "item_actors.toml"


@cache
def _actor_items() -> frozenset[str]:
    """The logic items with one native actor (``item_actors.toml``), the actor the pedestal's get route names."""
    with ITEM_ACTORS.open("rb") as stream:
        return frozenset(tomllib.load(stream)["items"])


def prepare_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """``spec`` with the logic setting set to ``settings.shuffle_master_sword`` and, when on, the pedestal check.

    Unchanged when the shuffle is off. Raises :class:`FillError` for logic naming the setting with another value, and
    when the shuffle is on without ``free_time_travel`` or in a world that cannot hold it; :class:`WorldError` when
    the world's own setting is not false."""
    chosen = settings.shuffle_master_sword
    if SETTING in settings.logic and settings.logic[SETTING] is not chosen:
        raise FillError(f"{SETTING} logic must agree with the seed's {SETTING} setting")
    world_settings = spec.get("settings", {})
    if SETTING not in world_settings:
        if chosen:
            raise FillError(f"Master Sword shuffle needs a world with the logic setting {SETTING!r}")
        return spec
    if world_settings[SETTING] is not False:
        raise WorldError(f"the world's own {SETTING} must be false; a seed chooses it")
    if not chosen:
        return spec
    if settings.logic.get(TRAVEL, world_settings.get(TRAVEL, False)) is not True:
        raise FillError(
            f"Master Sword shuffle needs {TRAVEL} (Free time travel) on: an adult without a sword may not reach "
            "the Forest Temple's native return to child."
        )
    entries = [*spec.get("locations", {}).items()]
    entries += [entry for region in spec["regions"] for entry in region.get("locations", {}).items()]
    if clash := sorted({name for name, info in entries if name == PEDESTAL or _type(info) == TYPE}):
        raise FillError(f"the world already has {clash}, so the Master Sword pedestal cannot become a {TYPE} check")
    if ITEM not in spec.get("items", {}):
        raise FillError(f"Master Sword shuffle needs the item {ITEM!r} in the world")
    event = world_settings.get("age_pull_event")
    holders = [region for region in spec["regions"] if event in region.get("events", {})]
    if len(holders) != 1:
        raise FillError(f"Master Sword shuffle needs one region holding the first-pull event {event!r}")
    [holder] = holders
    rule = holder["events"][event]
    rule = rule["rule"] if isinstance(rule, Mapping) else rule
    return {
        **spec,
        "settings": {**world_settings, SETTING: True},
        "locations": {**spec.get("locations", {}), PEDESTAL: {"type": TYPE, "vanilla": ITEM, "source": SOURCE}},
        "regions": [
            {**region, "locations": {**region.get("locations", {}), PEDESTAL: rule}} if region is holder else region
            for region in spec["regions"]
        ],
    }


def _type(info: Any) -> Any:
    return info.get("type") if isinstance(info, Mapping) else None


def pedestal_items(world: World) -> tuple[str, ...]:
    """The items the pedestal may give, in world order: a plain ``Item`` with one native actor (``item_actors.toml``),
    never the Master Sword itself, a progressive copy or tier (no dispatcher reads owned tiers there), a dungeon item
    (its credit is source-bound to chests), a token or bought goods (shop shelves only)."""
    actors = _actor_items()
    return tuple(
        name
        for name, item in world.items.items()
        if name in actors
        and name != ITEM
        and item.type == "Item"
        and item.dungeon is None
        and not item.tier
        and name not in CHAINS
        and name not in FAMILY_BY_ITEM
        and name not in world.progressive
        and not name.startswith(SHOP_ONLY_PREFIX)
    )


def restrict_settings(world: World, settings: Settings) -> Settings:
    """``settings`` with :data:`ITEM` held to :data:`ITEM_DESTINATIONS` and :data:`TYPE` checks to
    :func:`pedestal_items`, each intersected with what the settings already give (a replayed effective settings string
    gives the same); unchanged when the shuffle is off."""
    if not settings.shuffle_master_sword:
        return settings
    admitted = pedestal_items(world)
    given = settings.location_type_items.get(TYPE)
    if given is not None and (unsafe := sorted(set(given) - set(admitted))):
        raise FillError(
            f"location_type_items gives the Master Sword pedestal {unsafe}, which its standard get cannot grant; "
            f"admitted: {list(admitted)}"
        )
    palette = tuple(item for item in admitted if given is None or item in given)
    if not palette:
        raise FillError("location_type_items gives the Master Sword pedestal no item")
    held = dict(settings.item_location_types)
    for item, kinds in held.items():
        if TYPE in kinds and item not in palette:
            raise FillError(f"item_location_types holds {item!r} to the Master Sword pedestal, which cannot give it")
    hold = held.get(ITEM)
    kinds = tuple(kind for kind in ITEM_DESTINATIONS if hold is None or kind in hold)
    if not kinds:
        raise FillError(
            f"{ITEM} may go only to {list(ITEM_DESTINATIONS)} checks, but item_location_types holds it to "
            f"{list(hold or ())}"
        )
    held[ITEM] = kinds
    return replace(
        settings,
        location_type_items={**settings.location_type_items, TYPE: palette},
        item_location_types=held,
    )
