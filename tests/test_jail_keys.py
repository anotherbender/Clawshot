"""Synthetic key pack composition and native guard-source inverse diffs; no extracted fixtures."""

import copy

import pytest

from clawshot.formats import byml, evfl, rstb, sarc, zsdic
from clawshot.generate.key_families import HIDEOUT_SOURCES
from clawshot.patch import actor_packs, jail_keys
from clawshot.patch.actor_packs import actor_member, component_ref, reference, work_path
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.tokens import ACTOR_INFO, POUCH_ACTOR_INFO, POUCH_DEFAULT, canonical
from clawshot.patch.write import write

KEY_IDENTITY = "ActorSystem/ActorName/Item_Dungeon_SmallKey.engine__actor__ActorName.bgyml"
REWARD_IDENTITY = "ActorSystem/ActorName/Obj_Rupee_Red.engine__actor__ActorName.bgyml"
KEY_POUCH = "Component/PouchContentParam/NativeKey.game__component__PouchContentParam.bgyml"
REWARD_POUCH = "Component/PouchContentParam/NativeReward.game__component__PouchContentParam.bgyml"


def synthetic_pack(actor, *, reward=False):
    identity = REWARD_IDENTITY if reward else KEY_IDENTITY
    pouch = REWARD_POUCH if reward else KEY_POUCH
    fields = (
        {"IsBundle": True, "BundleActorNum": byml.I32(20), "DefaultAutoGet": True, "IsPlayGetEventPouchMax": True}
        if reward
        else {"PouchActor": work_path(actor_member("Item_Dungeon_SmallKey")), "SpecialDeal": byml.U32(17)}
    )
    return {
        actor_member(actor): byml.write(
            {
                "Components": {
                    "ActorNameRef": component_ref(identity),
                    "PouchContentRef": component_ref(pouch),
                    "AIInfoRef": "?AI/Native.ainb",
                    "ASRef": "?AS/Native.asb",
                    "ActorGameDataSetting": "?AlwaysRespawn.bgyml",
                }
            }
        ),
        identity: byml.write({"Name": "synthetic identity"}),
        pouch: byml.write({"$parent": work_path(POUCH_DEFAULT), **fields}),
        "AI/Native.ainb": b"synthetic pickup callback, not game bytes",
        "AS/Native.asb": b"synthetic key animation, not game bytes",
    }


def test_reward_identity_does_not_change_key_retirement_or_shared_pouch():
    actor = next(iter(jail_keys.SOURCE_IDS))
    source = synthetic_pack(actor)
    donor = synthetic_pack(jail_keys.DONOR, reward=True)
    changed = sarc.read(jail_keys.retarget_pack(sarc.write(source), actor, jail_keys.DONOR, donor))
    components = actor_packs.resolve([changed], actor_member(actor))[0]["Components"]
    assert canonical(components) == jail_keys.DONOR
    assert components["AIInfoRef"] == "?AI/Native.ainb"
    assert components["ASRef"] == "?AS/Native.asb"
    assert components["ActorGameDataSetting"] == "?AlwaysRespawn.bgyml"
    for path, data in source.items():
        if path != actor_member(actor):
            assert changed[path] == data
    pouch = actor_packs.resolve_node([changed], reference(components["PouchContentRef"]), builtin=POUCH_DEFAULT)
    assert pouch["IsBundle"] is True and pouch["BundleActorNum"] == 20
    assert "SpecialDeal" not in pouch and "PouchActor" not in pouch
    assert KEY_POUCH in changed and changed[KEY_POUCH] == source[KEY_POUCH]
    with pytest.raises(PatchError, match="native small-key identity"):
        jail_keys.retarget_pack(sarc.write(changed), actor, jail_keys.DONOR, donor)


def source_contract():
    actors, groups, events = [], [], []
    for actor, (resting, event_id, group) in jail_keys.SOURCE_IDS.items():
        instance = f"SmallKeyForEvent_{actor[-2:]}"
        actors.extend([{"Hash": resting, "Gyaml": actor}, {"Hash": event_id, "Gyaml": actor, "Name": instance}])
        groups.append({"Hash": group, "References": [{"Reference": resting}]})
        events.append(
            evfl.SubFlowEvent(
                "synthetic",
                "",
                "GerudoThiefDropKey",
                evfl.NONE,
                {"Obj_SmallKey": evfl.ActorIdentifier(actor, instance)},
            )
        )
    return {"Actors": actors, "AiGroups": groups}, evfl.Flowchart("synthetic", events=events)


@pytest.mark.parametrize("stale", ["resting", "event", "restoration", "drop_binding"])
def test_each_jail_reward_requires_both_placed_forms_and_its_drop_binding(stale):
    tree, chart = source_contract()
    jail_keys.check_sources(tree, chart)
    if stale == "resting":
        tree["Actors"].pop(0)
    elif stale == "event":
        tree["Actors"][1]["Name"] = "another instance"
    elif stale == "restoration":
        tree["AiGroups"][0]["References"] = []
    else:
        chart.events[0].params["Obj_SmallKey"] = evfl.ActorIdentifier("another actor")
    with pytest.raises(PatchError):
        jail_keys.check_sources(tree, chart)


def test_unadmitted_jail_reward_is_refused_before_any_source_is_read(tmp_path):
    with pytest.raises(PatchError, match="not an admitted jail-key pickup reward"):
        jail_keys.build(tmp_path / "absent", {next(iter(HIDEOUT_SOURCES)): "Bow"})


@pytest.mark.dump
def test_native_jail_adapters_only_change_reward_packs_and_identity_tables(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path):
        return dictionaries.decompress(path, (romfs / path).read_bytes())

    placements = {name: jail_keys.REWARD for name in HIDEOUT_SOURCES}
    native = jail_keys.build(romfs, {name: jail_keys.KEY for name in HIDEOUT_SOURCES})
    assert not native.changes
    delivery = jail_keys.build(romfs, placements)
    packs = {f"Pack/Actor/{actor}.pack.zs" for actor in jail_keys.SOURCE_IDS}
    assert set(delivery.changes) == packs | {ACTOR_INFO, POUCH_ACTOR_INFO}
    original_rows = {path: byml.read(read(path)) for path in (ACTOR_INFO, POUCH_ACTOR_INFO)}
    for path in packs:
        actor = path.rsplit("/", 1)[1].removesuffix(".pack.zs")
        original = sarc.read(read(path))
        changed = sarc.read(delivery.changes[path](read(path)))
        before = actor_packs.resolve([original], actor_member(actor))[0]["Components"]
        after = actor_packs.resolve([changed], actor_member(actor))[0]["Components"]
        assert canonical(after) == jail_keys.DONOR
        for component in set(before) - {"ActorNameRef", "PouchContentRef"}:
            assert after[component] == before[component]
        assert all(changed[name] == data for name, data in original.items() if name != actor_member(actor))
        old_root = byml.read(original[actor_member(actor)])
        new_root = byml.read(changed[actor_member(actor)])
        for field in ("ActorNameRef", "PouchContentRef"):
            new_root["Components"].pop(field)
            old_root["Components"].pop(field, None)
        assert byml.same(new_root, old_root)
    for path, original in original_rows.items():
        changed = byml.read(delivery.changes[path](read(path)))
        donor = next(row for row in original if row["__RowId"] == jail_keys.DONOR)
        for before, after in zip(original, changed, strict=True):
            if before["__RowId"] not in jail_keys.SOURCE_IDS:
                assert byml.same(before, after)
            elif path == ACTOR_INFO:
                assert after["ActorName"] == jail_keys.DONOR
                assert after["InstanceHeapSize"] >= before["InstanceHeapSize"]
                inverse = copy.deepcopy(after)
                inverse["ActorName"] = before["ActorName"]
                inverse["InstanceHeapSize"] = before["InstanceHeapSize"]
                assert byml.same(inverse, before)
            else:
                assert byml.same(after, {**donor, "__RowId": before["__RowId"]})
    out = tmp_path / "key-mod"
    write(Plan([], [], []), romfs, out, extra_changes=(delivery.changes,))
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    for path in packs:
        changed = sarc.read(dictionaries.decompress(path, (out / "romfs" / path).read_bytes()))
        for name, data in changed.items():
            if "/Clawshot_" in name:
                assert table.get(name) >= rstb.required_size(name, len(data))
            if name.endswith(rstb.ACTOR_PARAM):
                node = byml.read(data)
                assert table.get(name) >= rstb.required_size(name, len(data), len(node.get("Components", {})))
