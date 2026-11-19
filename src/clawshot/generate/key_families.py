"""Key families a seed's settings release from their native sources (Round 18, Track F; ``plans/rounds/r18-keys.md``,
``plans/rounds/r17-dungeon-items.md`` section 2).

Native floor-pickup key families leave their place only through settings, never a raw ``shuffle`` kind
(:func:`clawshot.generate.fill.key_source_types`):

- the Bottom of the Well floor key (:data:`FLOOR_SOURCES`), with ``dungeon_items`` ``anywhere`` or
  ``all_anywhere`` and ``Chest`` shuffled. ``own_dungeon`` leaves it native;
- the four Gerudo Fortress jail keys (:data:`HIDEOUT_SOURCES`) with ``shuffle_hideout_keys`` (default off, needs
  ``Chest``; Kareem, 2026-11-18).

The Shadow floor adapter is built, held until a natural pre-room save exists (Claude, Round 18).
Its check remains ``Collectable`` with its native key under every setting.

A seed:

1. :func:`prepare_spec` retypes exactly those checks, after checking each is still the native key source, from
   ``Collectable`` to :data:`FLOOR_KEY_SOURCE` or :data:`HIDEOUT_KEY_SOURCE`; off, the spec is unchanged;
2. :func:`restrict_settings` holds each type to :data:`PALETTES` (``location_type_items``): :data:`REPLACEMENT` or the
   source's own native key, intersected with a palette the settings already give. Every released key enters the
   pool, and the fill trades a displaced red rupee to its source.

Palette evidence (cs18f with the floor-key adapter, read-only native packs, ``E:/OOTRemake/work/r18-keys/``
``jail-survey.json``): a replacement keeps the native key-shaped floor actor, its root and death retirement, and
swaps only the pouch identity. ``Obj_Rupee_Red`` shares the key's ``PouchContent_PickUpItem_EnableWarp`` performer,
``DropItem`` death and AI; shields use another performer and hearts the Utuwa grant, so neither is admitted. No major,
progressive copy or other key goes to a key source before an in-game proof. The fill's dungeon rule keeps each floor
key to its own source (another dungeon's key leaves its dungeon only into a chest); the palettes keep Fortress keys
off floor sources and floor keys off jail sources. ``fill.allowed`` sends a Fortress key only to a chest (named
Fortress grant, ``clawshot.patch.key_targets.HIDEOUT``) or a jail source (its native key).

Jail sources (``data/world/remake/hideout_keys.toml``): four native identities, eight census copies. Each
``Obj_Dungeon_SmallKey_GerudoFortress_0N`` has one resting copy (linked in ``data/locations.toml``) and one
``SmallKeyForEvent_0N`` event copy present after its guard's defeat; the guard's drop is a third representation.
Which identity stands in which torch-named jail is not established, so each check needs all four guards' defeat, a
conservative rule, and the inherited torch-named checks are retired. A key found elsewhere credits only the Fortress
inventory: carpenter rescues still need their own guard's defeat and all four keys, and the D39 card stays vanilla.
"""

from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType
from typing import Any

from clawshot.generate.fill import (
    FLOOR_KEY_SOURCE,
    HIDEOUT_KEY_SOURCE,
    HIDEOUT_SMALL_KEY,
    SMALL_KEY,
    FillError,
    Settings,
    key_source_types,
)
from clawshot.world.model import World

NATIVE_TYPE = "Collectable"
"""The world data's (OoT Randomizer's) type of every key source while its family stays native."""
REPLACEMENT = "Rupees (20)"
"""The only reward a key source gives besides its own native key."""
HIDEOUT_KEY = "Small Key (Thieves Hideout)"
FLOOR_SOURCES: Mapping[str, str] = MappingProxyType(
    {
        "Bottom of the Well Freestanding Key": "Small Key (Bottom of the Well)",
    }
)
"""Released floor-key check -> native key (Well census Hash 17649154319341333603, room 3).
Shadow's built adapter is deliberately absent: no setting releases its source."""
HIDEOUT_SOURCES: Mapping[str, str] = MappingProxyType(
    {f"Gerudo Fortress Jail Key 0{n}": f"Obj_Dungeon_SmallKey_GerudoFortress_0{n}" for n in range(1, 5)}
)
"""Jail-key check -> its native source identity, the actor all its representations share."""
PALETTES: Mapping[str, tuple[str, ...]] = MappingProxyType(
    {
        FLOOR_KEY_SOURCE: (REPLACEMENT, *FLOOR_SOURCES.values()),
        HIDEOUT_KEY_SOURCE: (REPLACEMENT, HIDEOUT_KEY),
    }
)


def _sources(settings: Settings) -> dict[str, tuple[str, str]]:
    """Each check the settings release -> (its seed type, its native key)."""
    kinds = key_source_types(settings)
    out = {}
    if FLOOR_KEY_SOURCE in kinds:
        out.update({name: (FLOOR_KEY_SOURCE, key) for name, key in FLOOR_SOURCES.items()})
    if HIDEOUT_KEY_SOURCE in kinds:
        out.update({name: (HIDEOUT_KEY_SOURCE, HIDEOUT_KEY) for name in HIDEOUT_SOURCES})
    return out


def prepare_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """``spec`` with each released key source retyped; unchanged when the settings release none. A world without a
    source (a synthetic world) keeps going without it; a source that is no longer its native key is refused."""
    sources = _sources(settings)
    if not sources:
        return spec
    entries = [*spec.get("locations", {}).items()]
    entries += [entry for region in spec.get("regions", ()) for entry in region.get("locations", {}).items()]
    kinds = set(PALETTES)
    if clash := sorted({name for name, info in entries if isinstance(info, Mapping) and info.get("type") in kinds}):
        raise FillError(f"the world already has key-source checks {clash}; only key_families may type them")
    for name, (_, key) in sources.items():
        info = spec.get("locations", {}).get(name)
        if info is not None and (info.get("type") != NATIVE_TYPE or info.get("vanilla") != key):
            raise FillError(
                f"{name}: expected the native {key!r} {NATIVE_TYPE} source, "
                f"not a {info.get('type')!r} check holding {info.get('vanilla')!r}"
            )

    def retyped(name: str, info: Any) -> Any:
        return {**info, "type": sources[name][0]} if name in sources and isinstance(info, Mapping) else info

    return {
        **spec,
        "locations": {name: retyped(name, info) for name, info in spec.get("locations", {}).items()},
        "regions": [
            {**region, "locations": {name: retyped(name, info) for name, info in region["locations"].items()}}
            if "locations" in region
            else region
            for region in spec.get("regions", ())
        ],
    }


def _check_source(world: World, name: str, key: str) -> None:
    """A source keeps its native key reachable at itself: a floor source inside its key's dungeon, a jail key without
    a logic dungeon (its own source's native grant, ``fill.allowed``)."""
    info = world.items.get(key)
    if info is None:
        raise FillError(f"{name}: the world does not know its native key {key!r}")
    loc = world.locations[name]
    if loc.vanilla != key:
        raise FillError(f"{name}: holds {loc.vanilla!r}, not its native key {key!r}")
    if info.type == HIDEOUT_SMALL_KEY:
        if info.dungeon is not None:
            raise FillError(f"{key}: a Fortress key has no logic dungeon, not {info.dungeon!r}")
        return
    region = world.regions[loc.region]
    if info.type != SMALL_KEY or region.dungeon != info.dungeon or loc.area != region.area:
        raise FillError(f"{name}: not a {info.dungeon} small-key source inside its dungeon")


def restrict_settings(world: World, settings: Settings) -> Settings:
    """``settings`` with each released key-source type held to its :data:`PALETTES` entry, intersected with what the
    settings already give (a replayed effective settings string gives the same); unchanged when none is released.

    Explicit settings may narrow a palette, never widen it, and each source must keep its own key or
    :data:`REPLACEMENT`; an item held to a key-source type outside its palette is refused."""
    present = {loc.type for loc in world.locations.values()}
    kinds = [kind for kind in key_source_types(settings) if kind in present]
    if not kinds:
        return settings
    palettes = dict(settings.location_type_items)
    for kind in kinds:
        admitted = tuple(item for item in PALETTES[kind] if item in world.items)
        given = palettes.get(kind)
        if given is not None and (unsafe := sorted(set(given) - set(admitted))):
            raise FillError(
                f"location_type_items gives {kind} checks {unsafe}, which a key source cannot give; admitted: "
                f"{list(admitted)}"
            )
        palette = tuple(item for item in admitted if given is None or item in given)
        sources = FLOOR_SOURCES if kind == FLOOR_KEY_SOURCE else dict.fromkeys(HIDEOUT_SOURCES, HIDEOUT_KEY)
        for name, loc in world.locations.items():
            if loc.type != kind:
                continue
            if name not in sources:
                raise FillError(f"{name}: a {kind} check that is no known key source")
            _check_source(world, name, sources[name])
            if loc.vanilla not in palette and REPLACEMENT not in palette:
                raise FillError(f"location_type_items leaves {name} neither its own key nor {REPLACEMENT}")
        palettes[kind] = palette
        for item, held in settings.item_location_types.items():
            if kind in held and item not in palette:
                raise FillError(f"item_location_types holds {item!r} to {kind} checks, which cannot give it")
    return replace(settings, location_type_items=palettes)
