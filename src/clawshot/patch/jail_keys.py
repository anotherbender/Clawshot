"""Retarget a scripted key pickup without changing its source lifecycle or key-shaped display.

The source's actor file name, root AI, physics, animations and event performer remain
native. Its canonical inventory identity and pouch semantics come from the reward.
Per-source pouch members prevent different rewards sharing one resource path. This
is built evidence only; source retirement and get presentation still require play.
"""

import copy
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from clawshot.formats import byml, evfl, sarc, zsdic
from clawshot.patch import actor_packs
from clawshot.patch.actor_packs import actor_member, component_ref, reference, work_path
from clawshot.patch.plan import PatchError
from clawshot.patch.tokens import ACTOR_INFO, POUCH_ACTOR_INFO, POUCH_DEFAULT, canonical, pouch_grant
from clawshot.patch.write import FileChanges

BANC = "Banc/GerudoFortress/GerudoFortress_Adult_Static.bcett.byml.zs"
RESCUE = "Event/EventFlow/SageOfSpirit_RescueCarpenter.bfevfl.zs"
KEY = "Small Key (Thieves Hideout)"
REWARD = "Rupees (20)"
DONOR = "Obj_Rupee_Red"
# Resting copy, event copy, and native level group: one source identity, not two checks.
SOURCE_IDS = {
    "Obj_Dungeon_SmallKey_GerudoFortress_01": (14727159573379044362, 5126034700935231136, 11882204925587333348),
    "Obj_Dungeon_SmallKey_GerudoFortress_02": (5303541637929200213, 12946017077004046962, 15045816986991301442),
    "Obj_Dungeon_SmallKey_GerudoFortress_03": (1406667554698159711, 7337789119684854050, 13268068063108307630),
    "Obj_Dungeon_SmallKey_GerudoFortress_04": (10731814783987785199, 18396961731144479654, 13818546422727077026),
}


@dataclass(frozen=True)
class Delivery:
    changes: FileChanges
    inputs: tuple[str, ...]


def native_inputs() -> tuple[str, ...]:
    return (
        BANC,
        RESCUE,
        ACTOR_INFO,
        POUCH_ACTOR_INFO,
        f"Pack/Actor/{DONOR}.pack.zs",
        *(f"Pack/Actor/{actor}.pack.zs" for actor in SOURCE_IDS),
    )


def check_sources(tree: Mapping, chart: evfl.Flowchart) -> None:
    """Audit all placed/event forms without changing any guard, rescue, door or saved source flag."""
    for actor, (resting, event_id, group_id) in SOURCE_IDS.items():
        copies = [a for a in tree.get("Actors", []) if a.get("Gyaml") == actor]
        expected = {(resting, None), (event_id, f"SmallKeyForEvent_{actor[-2:]}")}
        actual = {(int(a["Hash"]), a.get("Name")) for a in copies}
        if actual != expected or len(copies) != 2:
            raise PatchError(f"{BANC}: stale jail source {actor}: {actual!r}, expected {expected!r}")
        groups = [g for g in tree.get("AiGroups", []) if g.get("Hash") == group_id]
        if len(groups) != 1 or resting not in {ref.get("Reference") for ref in groups[0].get("References", [])}:
            raise PatchError(f"{actor}: missing native restoration group {group_id}: {groups!r}")
        identifier = evfl.ActorIdentifier(actor, f"SmallKeyForEvent_{actor[-2:]}")
        calls = [
            e
            for e in chart.events
            if isinstance(e, evfl.SubFlowEvent)
            and e.entry_point == "GerudoThiefDropKey"
            and (e.params or {}).get("Obj_SmallKey") == identifier
        ]
        if len(calls) != 1:
            raise PatchError(f"{RESCUE}: {actor} has {len(calls)} native drop-event bindings")


def build(romfs: str | Path, placements: Mapping[str, str]) -> Delivery:
    """Retarget each guard's three pickup forms via its original actor pack, never its defeat/rescue flow."""
    from clawshot.generate.key_families import HIDEOUT_SOURCES

    if unknown := placements.keys() - HIDEOUT_SOURCES.keys():
        raise PatchError(f"unknown Fortress key sources: {sorted(unknown)}")
    assignments = {}
    for name, item in sorted(placements.items()):
        if item not in (KEY, REWARD):
            raise PatchError(f"{name}: {item!r} is not an admitted jail-key pickup reward")
        if item == REWARD:
            assignments[HIDEOUT_SOURCES[name]] = DONOR
    if not placements:
        return Delivery({}, ())
    root = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(root)
    inputs = []

    def read(path: str) -> bytes:
        inputs.append(path)
        return dictionaries.decompress(path, (root / path).read_bytes())

    check_sources(byml.read(read(BANC)), evfl.read(read(RESCUE)).flowchart)
    changes = dict(registry_changes(root, assignments))
    inputs.extend(changes)
    if assignments:
        donor_pack = sarc.read(read(f"Pack/Actor/{DONOR}.pack.zs"))
        for actor in sorted(assignments):
            path = f"Pack/Actor/{actor}.pack.zs"
            original = read(path)
            replacement = retarget_pack(original, actor, DONOR, donor_pack)
            changes[path] = _pack_transform(path, original, replacement)
    return Delivery(changes, tuple(inputs))


def _pack_transform(path: str, original: bytes, replacement: bytes):
    def transform(data: bytes) -> bytes:
        if sarc.read(data) != sarc.read(original):
            raise PatchError(f"{path}: native jail-key pack changed before retargeting")
        return replacement

    return transform


def retarget_pack(data: bytes, actor: str, donor_actor: str, donor_pack: Mapping[str, bytes]) -> bytes:
    """Keep the key's resource identity; change only its canonical name and pouch grant."""
    pack = sarc.read(data)
    before = actor_packs.resolve([pack], actor_member(actor))[0]["Components"]
    donor = actor_packs.resolve([donor_pack], actor_member(donor_actor))[0]["Components"]
    if canonical(before) != "Item_Dungeon_SmallKey":
        raise PatchError(f"{actor}: expected the native small-key identity, got {canonical(before)!r}")
    source_pouch = actor_packs.resolve_node([pack], reference(before["PouchContentRef"]), builtin=POUCH_DEFAULT)
    if source_pouch.get("PouchActor") != work_path(actor_member("Item_Dungeon_SmallKey")):
        raise PatchError(f"{actor}: expected the native key pouch, got {source_pouch!r}")
    pouch = actor_packs.resolve_node([donor_pack], reference(donor["PouchContentRef"]), builtin=POUCH_DEFAULT)
    if grant := pouch_grant(pouch, donor):
        pouch["PouchActor"] = grant
    member = f"Component/PouchContentParam/Clawshot_{actor}.game__component__PouchContentParam.bgyml"
    if member in pack:
        raise PatchError(f"{actor}: source-specific pouch already exists")
    pack[member] = byml.write({"$parent": work_path(POUCH_DEFAULT), **pouch})
    identity = reference(donor["ActorNameRef"])
    # ActorName resources can be resident/external; preserve the donor's native reference.
    if identity in donor_pack:
        if identity in pack and pack[identity] != donor_pack[identity]:
            raise PatchError(f"{actor}: conflicting canonical identity member {identity}")
        pack[identity] = donor_pack[identity]
    document = byml.load(pack[actor_member(actor)])
    components = document.root.setdefault("Components", {})
    components["ActorNameRef"] = donor["ActorNameRef"]
    components["PouchContentRef"] = component_ref(member)
    pack[actor_member(actor)] = byml.dump(document)
    after = actor_packs.resolve([pack], actor_member(actor))[0]["Components"]
    unchanged = set(before) - {"ActorNameRef", "PouchContentRef"}
    if any(after.get(key) != before[key] for key in unchanged):
        raise PatchError(f"{actor}: retargeting changed a native source component")
    result = sarc.write(pack)
    if sarc.read(result) != pack:
        raise PatchError(f"{actor}: retargeted pickup pack does not read back")
    return result


def registry_changes(romfs: str | Path, assignments: Mapping[str, str]) -> FileChanges:
    """Keep native display/physics rows; match cached identity/pouch metadata to the new grant."""
    if not assignments:
        return {}
    root = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(root)
    changes = {}
    for path in (ACTOR_INFO, POUCH_ACTOR_INFO):
        rows = byml.read(dictionaries.decompress(path, (root / path).read_bytes()))
        indexed = {row["__RowId"]: row for row in rows}
        if len(indexed) != len(rows):
            raise PatchError(f"{path}: duplicate actor rows")
        edits = {}
        for source, donor in sorted(assignments.items()):
            if source not in indexed or donor not in indexed:
                raise PatchError(f"{path}: missing key source/reward row {source}/{donor}")
            old, reward = indexed[source], indexed[donor]
            if path == ACTOR_INFO:
                new = {
                    **copy.deepcopy(old),
                    "ActorName": reward["ActorName"],
                    "InstanceHeapSize": type(old["InstanceHeapSize"])(
                        int(old["InstanceHeapSize"]) + int(reward["InstanceHeapSize"])
                    ),
                }
            else:
                new = {**copy.deepcopy(reward), "__RowId": source}
            edits[source] = (old, new)
        changes[path] = _registry_transform(path, edits)
    return changes


def _registry_transform(path: str, edits: Mapping[str, tuple[dict, dict]]):
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        positions = {row["__RowId"]: i for i, row in enumerate(document.root)}
        for name, (old, new) in edits.items():
            index = positions.get(name)
            if index is None or not byml.same(document.root[index], old):
                found = None if index is None else document.root[index]
                raise PatchError(f"{path}: stale key pickup row {name}: {found!r}")
            document.root[index] = copy.deepcopy(new)
        result = byml.dump(document)
        if not byml.same(byml.read(result), document.root):
            raise PatchError(f"{path}: retargeted key rows do not read back")
        return result

    return transform
