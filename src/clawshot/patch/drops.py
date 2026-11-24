"""Boss-heart pickups, retaining the room's spawn and persistence wiring.

BossHeart destinations accept the explicit native palette (:data:`NATIVE_ITEMS`) plus the ocarinas' and songs' world
actors (:func:`floor_items`; ocarina-song-drops-everywhere), never inventory-only Item_* actors or the bare
known-crashing Obj_Arrow_Fire. The song and ocarina floor actors are built from Obj_Arrow_Fire's pack
(``patch.songs``, ``patch.ocarina_pickup``); BBender kept them for floors (2026-11-24). The ocarinas stay out of the
palette as their arrow-based actors passed in game (:data:`FLOOR_OCARINAS`). See r7-drops.md for the eight
Logic_Create gates and the pending King Dodongo Save/Continue check.
"""

from collections.abc import Mapping, Sequence
from dataclasses import replace

from clawshot.census.definitions import Definition
from clawshot.census.scan import HEART_CONTAINER, Location
from clawshot.formats import byml
from clawshot.generate import Settings
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import getitem, ocarina_pickup, songs
from clawshot.patch import items as item_actors
from clawshot.patch.items import ItemActors
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges
from clawshot.world.model import World

SHUFFLE = "BossHeart"
HEART = "Obj_Heart_Container"
# Logical grants, not chest actors: Rupees (20) uses a native Obj_ pickup here.
NATIVE_ITEMS = {
    "Heart Container": HEART,
    "Piece of Heart": "Obj_Heart_Piece",
    "Deku Shield": "Obj_Shield_Deku",
    "Hylian Shield": "Obj_Shield_Hylian",
    "Rupees (20)": "Obj_Rupee_Red",
}
# World actors beyond the native palette (ocarina-song-drops-everywhere 1.4): the ocarinas' and songs' generated
# floor actors, which a seed placing them also writes.
OCARINA_PICKUPS = {
    "Ocarina of Time": ocarina_pickup.PICKUPS[ocarina_pickup.TIME],
    "Fairy Ocarina": ocarina_pickup.PICKUPS[ocarina_pickup.FAIRY],
}
# Ocarinas admitted to floors (plan 16.4). The native Obj_Ocarina_Time and the first Fairy actor built on it had an
# invisible box Link hangs on (BBender, run F1, 2026-11-24); the arrow-based actors passed with the floor lift, glow and
# T1-a receipt: Fairy at Queen Gohma's heart, Time at Kakariko's cow-pen heart piece, no box, played at once (BBender,
# runs G1 and TG2, 2026-11-24, Longshot stable v3.1.1).
FLOOR_OCARINAS: frozenset[str] = frozenset(OCARINA_PICKUPS)
PICKUPS = frozenset(
    {
        *NATIVE_ITEMS.values(),
        *OCARINA_PICKUPS.values(),
        *(songs.pickup_name(song) for song in getitem.SONG_MODELS),
    }
)
"""Every actor a floor writer may put on a saved heart."""
LIFTED = PICKUPS - frozenset(NATIVE_ITEMS.values())
"""The generated ocarina and song floor actors: their model sits on its centre, so a floor writer lifts them."""
FLOOR_LIFT = 0.3
"""Metres a lifted pickup floats above the heart's spot. The ocarinas sat very low, one clipping into the Kakariko
cow-pen roof (BBender, run G1, 2026-11-24); 0.3 m is a first value for BBender to judge in game."""


def place(path: str, actor: dict, pickup: str) -> None:
    """Swap a placed heart ``actor`` to ``pickup``; a :data:`LIFTED` pickup also rises :data:`FLOOR_LIFT`."""
    actor["Gyaml"] = pickup
    if pickup not in LIFTED:
        return
    translate = actor.get("Translate")
    if not isinstance(translate, list) or len(translate) != 3:
        raise PatchError(f"{path}: heart {actor.get('Hash')} has no Translate to lift: {translate!r}")
    translate[1] = type(translate[1])(float(translate[1]) + FLOOR_LIFT)


def floor_items(world: World, settings: Settings, actors: ItemActors) -> dict[str, str]:
    """Logic item -> the world actor a floor check (BossHeart, Freestanding) shows for it: the native palette, the
    admitted ocarinas (:data:`FLOOR_OCARINAS`) and, with ``songs = anywhere``, the twelve songs; only items the world
    has."""
    extra = {item: actor for item, actor in OCARINA_PICKUPS.items() if item in FLOOR_OCARINAS}
    if settings.songs == "anywhere":
        extra |= {
            item: songs.pickup_name(actor) for item, actor in actors.actors.items() if actor in getitem.SONG_MODELS
        }
    return {**NATIVE_ITEMS, **{item: actor for item, actor in extra.items() if item in world.items}}


def changes(placements: Mapping[int, str], census: Sequence[Location]) -> FileChanges:
    """Replace saved heart actors by Hash on every copy, never their script groups."""
    locations = {loc.id: loc for loc in census}
    files: dict[str, dict[int, str]] = {}
    for actor_id, pickup in placements.items():
        loc = locations.get(actor_id)
        if loc is None or loc.kind != HEART_CONTAINER or loc.actor != HEART or not loc.has_save_flag:
            raise PatchError(f"{actor_id}: not a saved boss Heart Container")
        if pickup not in PICKUPS:
            raise PatchError(f"{actor_id}: {pickup!r} is not a supported boss-heart pickup")
        for path in loc.files:
            files.setdefault(path, {})[actor_id] = pickup
    return {path: _transform(path, targets) for path, targets in sorted(files.items())}


def _transform(path: str, targets: Mapping[int, str]):
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        tree = document.root
        edits = []
        for actor_id, pickup in targets.items():
            found = [a for a in tree.get("Actors", []) if a.get("Hash") == actor_id]
            if len(found) != 1 or found[0].get("Gyaml") != HEART:
                raise PatchError(f"{path}: stale boss heart {actor_id}: {found!r}")
            references = [
                ref
                for group in tree.get("AiGroups", [])
                for ref in group.get("References", [])
                if ref.get("Reference") == actor_id
            ]
            if len(references) != 1 or not references[0].get("Id", "").startswith(HEART + "_"):
                raise PatchError(f"{path}: heart {actor_id} lost its native logic binding: {references!r}")
            for key in ("SimultaneousGroups", "FarDeleteGroups"):
                memberships = [group for group in tree.get(key, []) if actor_id in group]
                if len(memberships) != 1 or memberships[0].count(actor_id) != 1:
                    raise PatchError(f"{path}: heart {actor_id} has invalid {key}: {memberships!r}")
            edits.append((found[0], pickup))
        for actor, pickup in edits:
            place(path, actor, pickup)
        out = byml.dump(document)
        if byml.difference(tree, byml.read(out)) is not None:
            raise PatchError(f"{path}: changed boss hearts do not read back")
        return out

    return transform


def seed_setup(
    world: World,
    settings: Settings,
    census: Sequence[Location],
    definitions: Sequence[Definition],
    vanilla: Mapping[str, str],
):
    """Restrict BossHeart destinations to :func:`floor_items` (``Settings.location_type_items``), intersecting a
    palette already given. The fill fills them from that palette first; no other item can reach them."""
    shuffled = shuffled_locations(world, settings)
    checks = [name for name in shuffled if world.locations[name].type == SHUFFLE]
    locations = {loc.id: loc for loc in census}
    linked = {}
    for name in checks:
        found = [d for d in definitions if d.kind == HEART_CONTAINER and (d.oot_randomizer_name or d.name) == name]
        if len(found) != 1 or found[0].id not in locations:
            raise PatchError(f"{name}: expected one census boss heart")
        loc = locations[found[0].id]
        if loc.kind != HEART_CONTAINER or loc.actor != HEART or not loc.has_save_flag:
            raise PatchError(f"{name}: not a saved native boss heart")
        linked[name] = loc.id
    pickups = floor_items(world, settings, item_actors.load())
    palettes = dict(settings.location_type_items)
    palette = [item for item in pickups if item in palettes.get(SHUFFLE, pickups)]
    pickups = {item: pickups[item] for item in palette}
    settings = replace(settings, location_type_items={**palettes, SHUFFLE: tuple(palette)})

    def step(placements: Mapping[str, str]) -> FileChanges:
        targets = {}
        for name, actor_id in linked.items():
            item = placements[name]
            if item not in pickups:
                raise PatchError(f"{name}: {item!r} has no boss-heart pickup in this seed's palette")
            if (pickup := pickups[item]) != HEART:
                targets[actor_id] = pickup
        return changes(targets, census)

    return settings, step
