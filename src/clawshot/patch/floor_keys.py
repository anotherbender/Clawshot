"""Bottom of the Well and Shadow Temple floor small keys as shuffled sources (Round 18, Track F; ``r18-keys.md``).

Each source keeps its native key, or holds the explicit :data:`PALETTE` reward on a key-shaped pickup that keeps the
native key's whole source contract. Clean room: built from the player's dump and this repository only.

Round 18 hold: only the Well source is admitted by ``generate.key_families``.
Shadow is built, held until a natural pre-room save exists; its adapter remains available
for isolated structural research, not seed options. Its native source stays unchanged.

Native contract (build ``e0f3ccfa``, read-only research in ``work/r18-keys/floor`` and ``work/r17-dungeon-items``):

- Both sources are the one placed ``Obj_Dungeon_SmallKey`` of their dungeon's static Banc. The pack is shared by both
  sources, and its member paths are shared by the four Fortress key packs, so no pack is edited in place.
  ``AlwaysRespawn`` replaces ``Obj_Item_Base``'s ``NoRespawn``: neither Hash has a saved actor row. The native pouch
  grant ``Item_Dungeon_SmallKey`` credits the dungeon Link stands in; no instance override names an event or grant.
- Retirement is the room's level logic, bound by ``AiGroups[].References`` (Id -> Hash) to the actor's
  ``ActorLogicSimpleActor`` node. Well: the key exists until the saved Bool
  ``BottomOfTheWell_Level_Room_03_Get_SmallKey``; its ``Dead`` sets that Bool, ``..._Get_Key`` (the candle riddle's
  gate) and an autosaved room clear. Shadow: the skull pot's ``Dead`` creates the key while
  ``ShadowTemple_Level_Room_13_GetKey`` is false; the key's ``Dead`` sets it. The pot's death also requests
  ``ShadowTemple_Gimmick_Focus_LargeJar_Key``, linked to the key Hash, whose flow actor ``Obj_Dungeon_SmallKey``
  (named by actor file name, which ``QueryGenericGetActorName`` reports apart from the canonical ``ActorName``) plays
  ``Act_Pop`` and ``Rotate_Obj`` from the key's AS. The two room modules are pinned by SHA256, not parsed.
- A moved source therefore keeps all of it: an uncollected reward comes back on every load until its own pickup
  (``Dead``) sets the source's existing Bool, exactly as the key.

A moved source's Banc copy changes only ``Gyaml``, to a source-specific actor :attr:`Source.actor`: a direct child of
``Obj_Dungeon_SmallKey`` (as the native ``Obj_Dungeon_SmallKey_GerudoFortress_01`` is) whose leaf overrides only
``ActorNameRef`` and ``PouchContentRef`` with the reward's native members. The pouch event graph
(``PouchContent_EnableWarp.event.root``) decides push, category and get text from the canonical ``ActorName``, so both
come from the reward; the AI root, death, physics, attention, model, animation and AS stay the key's. A new pack holds
the native key pack byte-identical plus the reward's identity and pouch members (copied) and the new leaf. New rows in
``ActorInfo`` (the key's row with the reward's ``ActorName``, both heap budgets reserved), ``GameActorInfo`` (the
key's) and ``PouchActorInfo`` (the reward's) register it; no existing row changes, no saved row is added, ``RSDB/Tag``
stays unchanged. For Shadow, the reveal flow's key actor is renamed to the source actor: it is used only by the
``LargeJar_Key`` entry, so the flow's file-name binding and the inherited animations stay native.

Palette: a reward must share the key's pickup mechanism (event performer ``PouchContent_PickUpItem_EnableWarp``,
``DropItem`` AI root and death) and have the native ``rupee`` grant shape. Only ``Obj_Rupee_Red`` is admitted;
shields use another performer, hearts ``PouchContentUtuwa``. A placed native key of the source's own dungeon changes
nothing; any other item (another dungeon's key: the grant credits the standing dungeon) is refused.

Built evidence only. Not yet seen in game: the Banc-placed new actor loading, its key-shaped display with red-rupee
text and grant, the Well riddle/room clear and Shadow reveal with it, recovery and Save/Continue retirement.
"""

import copy
import hashlib
from bisect import bisect_left
from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path, PurePosixPath

from clawshot.census.gifts import EVENT_SETTING, FLOW_DIR, FLOW_SUFFIX, FLOW_VERSIONS
from clawshot.census.scan import GAME_DATA_LIST
from clawshot.formats import byml, evfl, sarc, zsdic
from clawshot.patch import actor_packs
from clawshot.patch.actor_packs import actor_member, component_ref, reference, work_path
from clawshot.patch.plan import PatchError
from clawshot.patch.tokens import (
    ACTOR_INFO,
    GAME_ACTOR_INFO,
    LINK_USERS,
    POUCH_ACTOR_INFO,
    POUCH_DEFAULT,
    REGISTRIES,
    canonical,
    grant_family,
    pack_path,
    pouch_grant,
)
from clawshot.patch.write import FileChanges, NewFile
from clawshot.save import murmur3_32

KEY = "Obj_Dungeon_SmallKey"
KEY_PACK = pack_path(KEY)
KEY_GRANT = "Item_Dungeon_SmallKey"
ALWAYS_RESPAWN = "Component/ActorGameDataSetting/AlwaysRespawn.game__component__ActorGameDataSetting.bgyml"
ACTOR_LOGIC = "Work/Logic/NodeDefinition/Node/ActorLogicSimpleActor.aidefn"  # the node level groups bind
ITEM_BASE = "Obj_Item_Base"
IDENTITY = ("ActorNameRef", "PouchContentRef")  # the only components a source actor overrides
MECHANISM = ("EventPerformerRef", "AIInfoRef", "DeathRef", "ActorLogicNodeRef")  # a reward shares the key's
REVEAL_ACTION = "EventPlayASWithClothWarp"
REQUESTER = "EventRequestActor"
ROOM_KEY = "DefaultDungeonRoomIndex"
SAVED_BOOL = (8, 0)  # ResetTypeValue, SaveFileIndex of a saved story Bool
PALETTE_FAMILY = "rupee"
PALETTE = {"Rupees (20)": "Obj_Rupee_Red"}
"""Logic item -> its native reward actor; with the source's own native key, everything a source may hold."""


@dataclass(frozen=True)
class Reveal:
    """A native event revealing the source actor: requested by ``requester`` (linked to the source), run from
    ``entry`` of ``flow``, playing ``animations`` on the flow actor named for the key."""

    requester: int
    event: str  # RequestEventName, an RSDB/EventSetting row
    flow: str
    entry: str
    animations: tuple[str, ...]

    @property
    def path(self) -> str:
        return f"{FLOW_DIR}/{self.flow}{FLOW_SUFFIX}"


@dataclass(frozen=True)
class Source:
    location: str  # the world location
    key: str  # the logic item of its own native key
    id: int  # the placed key's Hash
    banc: str
    room: int  # its DefaultDungeonRoomIndex, its only instance parameter
    group: int  # the AiGroup binding it
    reference: str  # that group's reference Id (and Path) for it
    logic: str  # that group's module, as the group names it
    module: str  # the module's romfs file
    module_sha256: str
    collected: str  # the saved Bool its Dead sets and that retires it
    actor: str  # the source actor a moved reward is placed as
    reveal: Reveal | None = None


WELL = Source(
    "Bottom of the Well Freestanding Key",
    "Small Key (Bottom of the Well)",
    17649154319341333603,
    "Banc/BottomOfTheWell/BottomOfTheWell_Static.bcett.byml.zs",
    3,
    4420455204133201806,
    "Obj_Dungeon_SmallKey_db9c",
    "Logic/Module/BottomOfTheWell_Level_Room_03Prefab/BottomOfTheWell_Level_Room_03Prefab_25d7.logic.module.ain",
    "Logic/BottomOfTheWell_Level_Room_03Prefab_25d7.logic.module.ainb",
    "012abb6f5e9b4b459642b14173bf79fcbc2afcef85e2429e677b6a74c9409ad1",
    "BottomOfTheWell_Level_Room_03_Get_SmallKey",
    "Obj_Dungeon_SmallKey_Floor_BottomOfTheWell",
)
SHADOW = Source(
    "Shadow Temple Freestanding Key",
    "Small Key (Shadow Temple)",
    12562389953863361839,
    "Banc/ShadowTemple/ShadowTemple_Static.bcett.byml.zs",
    13,
    13772315372431787476,
    "KeySmall_e812",
    "Logic/Module/ShadowTemple_Level_Room_B3FB4F_F_Prefab/"
    "ShadowTemple_Level_Room_B3FB4F_F_Prefab_6cf3.logic.module.ain",
    "Logic/ShadowTemple_Level_Room_B3FB4F_F_Prefab_6cf3.logic.module.ainb",
    "aff55f495bddad3853020c7b0f989123b5f9c08e021b244b2b70faa638be8e35",
    "ShadowTemple_Level_Room_13_GetKey",
    "Obj_Dungeon_SmallKey_Floor_ShadowTemple",
    Reveal(
        8582480585789402014,
        "ShadowTemple_Gimmick_Focus_LargeJar_Key",
        "ShadowTemple_Gimmick",
        "LargeJar_Key",
        ("Act_Pop", "Rotate_Obj"),
    ),
)
SOURCES = {source.location: source for source in (WELL, SHADOW)}


def native_inputs() -> tuple[str, ...]:
    """Every romfs file :func:`build` may read, the dictionaries' pack included."""
    paths = [
        "Pack/ZsDic.pack.zs",
        GAME_DATA_LIST,
        KEY_PACK,
        *(pack_path(actor) for actor in sorted(set(PALETTE.values()))),
        *REGISTRIES,
        EVENT_SETTING,
        FLOW_VERSIONS,
    ]
    for source in SOURCES.values():
        paths += [source.banc, source.module, *([source.reveal.path] if source.reveal else [])]
    return tuple(dict.fromkeys(paths))


@dataclass(frozen=True)
class Delivery:
    """``changes`` for the common writer's ``extra_changes`` and ``new_files`` for its ``new_files``."""

    changes: FileChanges
    new_files: Mapping[str, NewFile]  # source actor pack path -> its pack
    actors: Mapping[str, str]  # moved world location -> the source actor its copy now names
    inputs: tuple[str, ...]  # romfs files read, in order


class _Romfs:
    """Read-only, cached access to the dump; a missing file names itself (a working-set gap)."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.dicts = zsdic.Dictionaries.from_romfs(self.root)
        self.inputs: list[str] = []
        self._files: dict[str, bytes] = {}

    def read(self, path: str) -> bytes:
        if path not in self._files:
            file = self.root / PurePosixPath(path)
            if not file.is_file():
                raise PatchError(f"floor key delivery needs {path}, which {self.root} lacks")
            data = file.read_bytes()
            self._files[path] = self.dicts.decompress(path, data) if path.endswith(".zs") else data
            self.inputs.append(path)
        return self._files[path]

    def pack(self, actor: str) -> dict[str, bytes]:
        return sarc.read(self.read(pack_path(actor)))


def _components(sources: actor_packs.Sources, actor: str) -> tuple[dict, list[str]]:
    resolved, chain = actor_packs.resolve(sources, actor_member(actor))
    return dict(resolved.get("Components", {})), chain


def _pouch(sources: actor_packs.Sources, components: Mapping[str, str]) -> dict:
    return actor_packs.resolve_node(sources, reference(components.get("PouchContentRef")) or "", builtin=POUCH_DEFAULT)


def check_key(pack: Mapping[str, bytes]) -> actor_packs.Closure:
    """The native key: its grant, lifecycle, level-logic node and a pack holding its whole reference closure."""
    found = actor_packs.closure([pack], KEY)
    if missing := sorted(set(found.members) - set(pack)):
        raise PatchError(f"{KEY_PACK}: closure members missing from the pack: {missing}")
    components = found.components
    contract = {
        "canonical": canonical(components),
        "grant": _pouch([pack], components).get("PouchActor"),
        "ActorGameDataSetting": components.get("ActorGameDataSetting"),
        "ActorLogicNodeRef": components.get("ActorLogicNodeRef"),
    }
    expected = {
        "canonical": KEY_GRANT,
        "grant": work_path(actor_member(KEY_GRANT)),
        "ActorGameDataSetting": component_ref(ALWAYS_RESPAWN),
        "ActorLogicNodeRef": ACTOR_LOGIC,
    }
    if contract != expected:
        raise PatchError(f"{KEY}: native contract {contract!r}, expected {expected!r}; the dump is modified")
    return found


def check_reward(actor: str, pack: Mapping[str, bytes], key: actor_packs.Closure, pouch_row: Mapping | None) -> None:
    """A palette reward: a native world pickup with the key's pickup mechanism and the admitted grant shape."""
    found = actor_packs.closure([pack], actor)
    _, chain = _components([pack], actor)
    if actor_member(ITEM_BASE) not in chain:
        raise PatchError(f"{actor}: not a native world pickup (no {ITEM_BASE} in {chain!r})")
    mechanism = {name: found.components.get(name) for name in MECHANISM}
    if mechanism != {name: key.components.get(name) for name in MECHANISM}:
        raise PatchError(f"{actor}: pickup mechanism {mechanism!r} is not the key's")
    for name in IDENTITY:
        if not found.components.get(name):
            raise PatchError(f"{actor}: no {name}")
    shape = None if pouch_row is None else grant_family(pouch_row)
    if shape != PALETTE_FAMILY:
        raise PatchError(f"{actor}: native grant shape {shape!r}, not {PALETTE_FAMILY!r}: {pouch_row!r}")


def compose(source: Source, key_pack: Mapping[str, bytes], reward: str, reward_pack: Mapping[str, bytes]) -> NewFile:
    """The source actor's pack: the native key pack, the reward's identity and pouch members, and the new leaf."""
    key = actor_packs.closure([key_pack], KEY)
    donor = actor_packs.closure([reward_pack], reward)
    leaf = {"$parent": work_path(actor_member(KEY)), "Components": {name: donor.components[name] for name in IDENTITY}}
    new = {actor_member(source.actor): byml.write(leaf)}
    sources = [new, key_pack, reward_pack]
    packed = actor_packs.closure(sources, source.actor)
    members = {**key_pack, **packed.members}
    _check_actor(source, reward, sources, packed, key, donor)
    copied = {name: KEY_PACK if name in key_pack else pack_path(reward) for name in members if name not in new}
    data = sarc.write(members)
    if sarc.read(data) != members:
        raise PatchError(f"{source.actor}: the composed pack does not read back")
    return NewFile(data, copied=copied)


def _check_actor(source, reward, sources, packed, key, donor) -> None:
    """Everything but the identity is the key's; the identity and pouch are the reward's; nothing new is needed."""
    expected = {**key.components, **{name: donor.components[name] for name in IDENTITY}}
    if packed.components != expected:
        names = expected.keys() | packed.components.keys()
        changed = sorted(n for n in names if packed.components.get(n) != expected.get(n))
        raise PatchError(f"{source.actor}: components {changed} are neither the key's nor the reward identity")
    chain = _components(sources, source.actor)[1]
    if chain != [*_components(sources, KEY)[1], actor_member(source.actor)]:
        raise PatchError(f"{source.actor}: parent chain {chain!r} is not the key's plus its leaf")
    if canonical(packed.components) != canonical(donor.components):
        raise PatchError(f"{source.actor}: canonical name {canonical(packed.components)!r}, not {reward}'s")
    if _pouch(sources, packed.components) != _pouch(sources, donor.components):
        raise PatchError(f"{source.actor}: pouch is not {reward}'s native pouch")
    if pouch_grant(_pouch(sources, packed.components), packed.components) == work_path(actor_member(KEY_GRANT)):
        raise PatchError(f"{source.actor}: still grants {KEY_GRANT}")
    if extra := sorted(packed.external - key.external - donor.external):
        raise PatchError(f"{source.actor}: references resources neither native pack depends on: {extra}")


def _member(sources: actor_packs.Sources, ref: str | None) -> dict:
    data = actor_packs.find(sources, reference(ref) or "")
    if data is None:
        raise PatchError(f"{ref!r}: no such member in the source packs")
    return byml.read(data)


def _check_display_row(actor: str, row: Mapping, sources, components: Mapping[str, str]) -> None:
    """An ActorInfo row agrees with the actor's components: canonical name, model, animations, effect/sound users."""
    model = _member(sources, components["ModelInfoRef"])
    expected = {
        "ActorName": canonical(components),
        "FmdbName": model.get("FmdbName"),
        "ModelProjectName": model.get("ModelProjectName"),
        "AnimationResources": _member(sources, components["AnimationRef"]).get("AnimationResources"),
    }
    for component, field in LINK_USERS:
        expected[field] = _member(sources, components[component]).get("UserName") if component in components else None
    actual = {field: row.get(field) for field in expected}
    if not byml.same(actual, expected):
        raise PatchError(f"ActorInfo {actor}: {actual!r} disagrees with its components {expected!r}")


def _rows(source: Source, reward: str, registries, sources) -> dict[str, dict]:
    """The source actor's rows: the key's ActorInfo with the reward's name and both heap budgets, the key's
    GameActorInfo, the reward's PouchActorInfo."""
    actor_rows, game_rows, pouch_rows = (registries[path] for path in REGISTRIES)
    for path, name in ((ACTOR_INFO, KEY), (ACTOR_INFO, reward), (GAME_ACTOR_INFO, KEY), (POUCH_ACTOR_INFO, reward)):
        if name not in registries[path]:
            raise PatchError(f"{path}: no native row {name}")
    for path in REGISTRIES:
        if source.actor in registries[path]:
            raise PatchError(f"{path}: row {source.actor} already exists")
    components = _components(sources, source.actor)[0]
    _check_display_row(KEY, actor_rows[KEY], sources, _components(sources, KEY)[0])
    row = copy.deepcopy(actor_rows[KEY])
    row["ActorName"] = actor_rows[reward]["ActorName"]
    heap = row["InstanceHeapSize"]
    row["InstanceHeapSize"] = type(heap)(int(heap) + int(actor_rows[reward]["InstanceHeapSize"]))
    row["__RowId"] = source.actor
    _check_display_row(source.actor, row, sources, components)
    return {
        ACTOR_INFO: row,
        GAME_ACTOR_INFO: {**copy.deepcopy(game_rows[KEY]), "__RowId": source.actor},
        POUCH_ACTOR_INFO: {**copy.deepcopy(pouch_rows[reward]), "__RowId": source.actor},
    }


def _sorted_ids(path: str, table: object) -> list[str]:
    if not isinstance(table, list):
        raise PatchError(f"{path}: not a row table")
    ids = [row.get("__RowId") for row in table]
    keys = [str(name).encode("utf-8") for name in ids]
    if any(not isinstance(name, str) for name in ids) or any(a >= b for a, b in zip(keys, keys[1:], strict=False)):
        raise PatchError(f"{path}: rows are not uniquely sorted by __RowId")
    return ids


def _insert_rows(data: bytes, *, path: str, rows: tuple[dict, ...], donors: Mapping[str, dict]) -> bytes:
    """Insert the source actors' rows at their sorted places by name; rows other steps insert stay, every donor row
    must still be the dump's."""
    document = byml.load(data)
    table = document.root
    ids = _sorted_ids(path, table)
    for name, native in donors.items():
        if name not in ids or not byml.same(table[ids.index(name)], native):
            found = table[ids.index(name)] if name in ids else None
            raise PatchError(f"{path}: row {name} changed since the floor sources were composed: {found!r}")
    for row in sorted(rows, key=lambda r: r["__RowId"].encode("utf-8")):
        ids = [r["__RowId"] for r in table]
        if row["__RowId"] in ids:
            raise PatchError(f"{path}: row {row['__RowId']} already exists")
        table.insert(bisect_left(ids, row["__RowId"].encode("utf-8"), key=lambda i: i.encode("utf-8")), row)
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{path}: changed table does not read back: {difference}")
    return out


def check_placement(tree: Mapping, source: Source) -> dict:
    """The placed native key and every binding the source contract rests on; returns the placed actor."""
    actors = tree.get("Actors") if isinstance(tree, Mapping) else None
    if not isinstance(actors, list):
        raise PatchError(f"{source.banc} has no Actors list")
    found = [a for a in actors if isinstance(a, dict) and a.get("Hash") == source.id]
    if len(found) != 1:
        raise PatchError(f"{source.banc}: {len(found)} actors have Hash {source.id}, expected one {KEY}")
    actor = found[0]
    shape = {
        "Gyaml": actor.get("Gyaml"),
        "Placement": (actor.get("Phive") or {}).get("Placement", {}).get("ID"),
        "Dynamic": dict(actor.get("Dynamic") or {}),
        "bound": {k: actor[k] for k in ("Links", "Name", "Presence") if k in actor},
    }
    if shape != {"Gyaml": KEY, "Placement": source.id, "Dynamic": {ROOM_KEY: source.room}, "bound": {}}:
        raise PatchError(f"{source.banc}: stale source {source.id}: {shape!r}; expected the native {KEY}")
    if any(a.get("Gyaml") == source.actor for a in actors if isinstance(a, dict)):
        raise PatchError(f"{source.banc}: {source.actor} is already placed")
    bindings = [
        (group.get("Hash"), group.get("Logic"), ref.get("Id"), ref.get("Path"))
        for group in tree.get("AiGroups", [])
        for ref in group.get("References", [])
        if ref.get("Reference") == source.id
    ]
    if bindings != [(source.group, source.logic, source.reference, source.reference)]:
        raise PatchError(f"{source.banc}: source {source.id} level-logic bindings {bindings!r} are not the native one")
    for key in ("SimultaneousGroups", "FarDeleteGroups"):
        memberships = [group for group in tree.get(key, []) if source.id in group]
        if len(memberships) != 1 or memberships[0].count(source.id) != 1:
            raise PatchError(f"{source.banc}: source {source.id} has invalid {key}: {memberships!r}")
    linkers = [
        (a.get("Gyaml"), a.get("Hash"), (a.get("Dynamic") or {}).get("RequestEventName"))
        for a in actors
        if isinstance(a, dict) and any(link.get("Dst") == source.id for link in a.get("Links") or [])
    ]
    top = [link for link in tree.get("Links") or [] if source.id in (link.get("Src"), link.get("Dst"))]
    reveal = source.reveal
    expected = [(REQUESTER, reveal.requester, reveal.event)] if reveal else []
    if linkers != expected or top:
        raise PatchError(f"{source.banc}: source {source.id} is linked by {linkers!r} {top!r}, expected {expected!r}")
    return actor


def _set_source(data: bytes, *, source: Source) -> bytes:
    """Name the source actor on the placed key; nothing else changes."""
    document = byml.load(data)
    check_placement(document.root, source)["Gyaml"] = source.actor
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{source.banc}: changed placement does not read back: {difference}")
    return out


def _successors(chart: evfl.Flowchart, event: evfl.Event) -> list[int]:
    out = []
    if isinstance(event, evfl.ForkEvent):
        out += [*event.forks, event.join]
    if isinstance(event, (evfl.SwitchEvent, evfl.SubFlowSwitchEvent)):
        out += [target for _, target in event.cases]
    if (following := getattr(event, "next", evfl.NONE)) != evfl.NONE:
        out.append(following)
    if isinstance(event, (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent)) and event.flowchart in ("", chart.name):
        out += [entry.main_event for entry in chart.entry_points if entry.name == event.entry_point]
    return [index for index in out if index != evfl.NONE]


def reveal_actor(chart: evfl.Flowchart, source: Source) -> int:
    """The reveal flow's one key actor, used only by the reveal entry to play the pinned animations."""
    reveal = source.reveal
    named = [i for i, actor in enumerate(chart.actors) if actor.name in (KEY, source.actor)]
    if len(named) != 1 or chart.actors[named[0]].name != KEY:
        raise PatchError(f"{reveal.flow}: actors {[(i, chart.actors[i].name) for i in named]}; expected one {KEY}")
    index = named[0]
    actor = chart.actors[index]
    if (actor.secondary_name, actor.argument_name, actor.actions, actor.queries) != ("", "", [REVEAL_ACTION], []):
        raise PatchError(f"{reveal.flow}: key actor {actor!r} is not the native reveal member")
    events = chart.events
    users = {
        i for i, e in enumerate(events) if isinstance(e, (evfl.ActionEvent, evfl.SwitchEvent)) and e.actor == index
    }
    played = sorted((events[i].params or {}).get("ASName") for i in users if isinstance(events[i], evfl.ActionEvent))
    if not users or len(played) != len(users) or tuple(played) != tuple(sorted(reveal.animations)):
        raise PatchError(
            f"{reveal.flow}: the key actor plays {played!r} in {len(users)} events, expected {reveal.animations!r}"
        )
    entries = []
    for entry in chart.entry_points:
        seen, todo = set(), [entry.main_event]
        while todo:
            event = todo.pop()
            if event in seen or not 0 <= event < len(chart.events):
                continue
            seen.add(event)
            todo += _successors(chart, chart.events[event])
        if seen & users:
            entries.append((entry.name, users <= seen))
    if entries != [(reveal.entry, True)]:
        raise PatchError(f"{reveal.flow}: key actor events reached from {entries!r}, expected only {reveal.entry!r}")
    return index


def _rename_reveal_actor(data: bytes, *, source: Source) -> bytes:
    """Rename the reveal's key actor to the source actor; nothing else in the flow changes."""
    file = evfl.read(data)
    expected = copy.deepcopy(file)
    expected.flowchart.actors[reveal_actor(file.flowchart, source)].name = source.actor
    out = evfl.write(expected)
    if evfl.read(out) != expected:
        raise PatchError(f"{source.reveal.path}: the renamed flow does not read back")
    return out


def _check_reveal_setting(native: _Romfs, source: Source) -> None:
    """The requested event runs the pinned entry of the flow the game loads at its plain path."""
    reveal = source.reveal
    rows = [row for row in byml.read(native.read(EVENT_SETTING)) if row.get("__RowId") == reveal.event]
    names = [(row.get("FlowchartFileName"), row.get("EntryPointName")) for row in rows]
    if names != [(f"Work/Event/EventFlow/{reveal.flow}.evfc", reveal.entry)]:
        raise PatchError(f"{EVENT_SETTING}: {reveal.event} runs {names!r}, expected {reveal.flow}:{reveal.entry}")
    versions = byml.read(native.read(FLOW_VERSIONS)).get("Versions", {})
    if reveal.flow in {str(name) for name in versions}:
        raise PatchError(f"{FLOW_VERSIONS}: {reveal.flow} is versioned; the game does not load {reveal.path}")


def _check_retirement(native: _Romfs, game_data: Mapping, source: Source) -> None:
    """The source's room module is the pinned one, and its retiring Bool is a saved story Bool."""
    if (digest := hashlib.sha256(native.read(source.module)).hexdigest()) != source.module_sha256:
        raise PatchError(f"{source.module}: SHA256 {digest}, not the inspected module {source.module_sha256}")
    key = murmur3_32(source.collected.encode())
    rows = [row for row in game_data["Data"]["Bool"] if row.get("Hash") == key]
    state = [(row.get("ResetTypeValue"), row.get("SaveFileIndex")) for row in rows]
    if state != [SAVED_BOOL]:
        raise PatchError(f"{GAME_DATA_LIST}: {source.collected} rows {state!r}, expected one saved Bool {SAVED_BOOL}")


def build(romfs: str | Path, placements: Mapping[str, str]) -> Delivery:
    """Delivery for the floor sources' placed logic items (world location -> item, only :data:`SOURCES` names).

    A source holding its own native key changes nothing and reads nothing; a :data:`PALETTE` reward is placed as the
    source's own actor. Validates the native key, the reward, each moved source's placement bindings, room module,
    retiring Bool and (Shadow) reveal event before any output; the returned transforms re-check their inputs."""
    moved: dict[str, str] = {}
    for name, item in sorted(placements.items()):
        source = SOURCES.get(name)
        if source is None:
            raise PatchError(f"{name!r} is not a floor key source ({', '.join(sorted(SOURCES))})")
        if item == source.key:
            continue
        if item not in PALETTE:
            allowed = ", ".join([source.key, *sorted(PALETTE)])
            raise PatchError(f"{name}: {item!r} is not a supported floor key reward ({allowed})")
        moved[name] = PALETTE[item]
    if not moved:
        return Delivery({}, {}, {}, ())
    native = _Romfs(romfs)
    game_data = byml.read(native.read(GAME_DATA_LIST))
    key_pack = native.pack(KEY)
    key = check_key(key_pack)
    tables = {path: byml.read(native.read(path)) for path in REGISTRIES}
    for path, table in tables.items():
        _sorted_ids(path, table)
    registries = {path: {row["__RowId"]: row for row in table} for path, table in tables.items()}
    changes: dict = {}
    new_files: dict[str, NewFile] = {}
    rows: dict[str, list[dict]] = {path: [] for path in REGISTRIES}
    for name, reward in moved.items():
        source = SOURCES[name]
        _check_retirement(native, game_data, source)
        check_placement(byml.read(native.read(source.banc)), source)
        reward_pack = native.pack(reward)
        check_reward(reward, reward_pack, key, registries[POUCH_ACTOR_INFO].get(reward))
        new_files[pack_path(source.actor)] = compose(source, key_pack, reward, reward_pack)
        sources = [sarc.read(new_files[pack_path(source.actor)].data)]
        for path, row in _rows(source, reward, registries, sources).items():
            rows[path].append(row)
        changes[source.banc] = partial(_set_source, source=source)
        if source.reveal is not None:
            _check_reveal_setting(native, source)
            reveal_actor(evfl.read(native.read(source.reveal.path)).flowchart, source)
            changes[source.reveal.path] = partial(_rename_reveal_actor, source=source)
    rewards = sorted(set(moved.values()))
    donors = {ACTOR_INFO: (KEY, *rewards), GAME_ACTOR_INFO: (KEY,), POUCH_ACTOR_INFO: tuple(rewards)}
    for path in REGISTRIES:
        changes[path] = partial(
            _insert_rows,
            path=path,
            rows=tuple(rows[path]),
            donors={name: copy.deepcopy(registries[path][name]) for name in donors[path]},
        )
    actors = {name: SOURCES[name].actor for name in moved}
    return Delivery(changes, new_files, actors, tuple(native.inputs))
