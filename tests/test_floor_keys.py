"""Well and Shadow floor key sources (clawshot.patch.floor_keys, Round 18 Track F).

Synthetic tests build a dump in code at the sources' pinned paths: packs, registries, placements and flow copy the
native *shapes* the module validates (names, references, inheritance, bindings), never game bytes; the two room
modules are opaque synthetic bytes whose digests stand in for the pinned native ones. Tests marked ``dump`` read
the player's real dump (``OOT_ROMFS``) and compare every output with the original files. Data and structure
evidence only; gameplay is the staged Longshot check.
"""

import dataclasses
import hashlib
from pathlib import PurePosixPath

import pytest

from clawshot.census import definitions as census_definitions
from clawshot.census.gifts import EVENT_SETTING, FLOW_VERSIONS
from clawshot.census.scan import FREESTANDING, GAME_DATA_LIST, scan
from clawshot.formats import byml, evfl, rstb, sarc, zsdic
from clawshot.formats.byml import F32, I32, U32, U64
from clawshot.patch import actor_packs
from clawshot.patch import floor_keys as fk
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.tokens import ACTOR_INFO, GAME_ACTOR_INFO, POUCH_ACTOR_INFO, POUCH_DEFAULT, REGISTRIES
from clawshot.patch.write import write
from clawshot.save import murmur3_32
from clawshot.world.load import load_world

WELL, SHADOW = fk.WELL.location, fk.SHADOW.location
RUPEE = "Obj_Rupee_Red"
BOTH = {WELL: "Rupees (20)", SHADOW: "Rupees (20)"}
NATIVE_ENTRY = 4096
MODULE_BYTES = {
    fk.WELL.module: b"AIB synthetic well room module",
    fk.SHADOW.module: b"AIB synthetic shadow room module",
}
POT, ANCHOR, DESTINATION = 501, 502, 503  # synthetic neighbours of the sources


def actor(name):
    return actor_packs.actor_member(name)


def work(member):
    return actor_packs.work_path(member)


def ref(member):
    return actor_packs.component_ref(member)


def w(tree):
    return byml.write(tree)


def name_ref(name):
    return f"?ActorSystem/ActorName/{name}.engine__actor__ActorName.bgyml"


ENABLE_WARP = (
    "Component/EventPerformerParam/PouchContent_PickUpItem_EnableWarp.engine__component__EventPerformerParam.bgyml"
)
PICK_UP = "Component/EventPerformerParam/PouchContent_PickUpItem.engine__component__EventPerformerParam.bgyml"
DROP_AI = "AI/AIInfo/DropItem.engine__actor__AIInfo.bgyml"
DROP_DEATH = "Component/DeathParam/DropItem.game__component__DeathParam.bgyml"
EVENT_GRAPH = "AI/PouchContent_EnableWarp.event.root.ainb"
KEY_POUCH = "Component/PouchContentParam/KeyItemSmallKey.game__component__PouchContentParam.bgyml"
RUPEE_POUCH = "Component/PouchContentParam/Obj_Rupee_Red.game__component__PouchContentParam.bgyml"
RUPEE_DEFAULT = "Component/PouchContentParam/RupeeDefault.game__component__PouchContentParam.bgyml"
KEY_MODEL = "Component/ModelInfo/Obj_Dungeon_SmallKey.engine__component__ModelInfo.bgyml"
KEY_ANIMATION = "Component/AnimationParam/Obj_Dungeon_SmallKey.engine__component__AnimationParam.bgyml"
KEY_ELINK = "Component/ELink/Obj_Dungeon_SmallKey.engine__component__ELinkParam.bgyml"
KEY_PHYSICS = "Component/Physics/Obj_Dungeon_SmallKey.engine__component__PhysicsParam.bgyml"
RUPEE_MODEL = "Component/ModelInfo/Obj_Rupee_Red.engine__component__ModelInfo.bgyml"
BASE_COMPONENTS = {
    "AIInfoRef": ref(DROP_AI),
    "ActorGameDataSetting": ref("Component/ActorGameDataSetting/NoRespawn.game__component__ActorGameDataSetting.bgyml"),
    "ActorLogicNodeRef": fk.ACTOR_LOGIC,
    "ActorNameRef": name_ref("Obj_Item_Base"),
    "DeathRef": ref(DROP_DEATH),
    "EventPerformerRef": ref(PICK_UP),
}
KEY_COMPONENTS = {
    "ASRef": "?AS/Obj_Dungeon_SmallKey.root.asb",
    "ActorGameDataSetting": ref(fk.ALWAYS_RESPAWN),
    "ActorNameRef": name_ref(fk.KEY_GRANT),
    "AnimationRef": ref(KEY_ANIMATION),
    "ELinkRef": ref(KEY_ELINK),
    "EventPerformerRef": ref(ENABLE_WARP),
    "ModelInfoRef": ref(KEY_MODEL),
    "PhysicsRef": ref(KEY_PHYSICS),
    "PouchContentRef": ref(KEY_POUCH),
}
RUPEE_COMPONENTS = {
    "ASRef": "?AS/Item_Rupee_Green.root.asb",
    "ActorNameRef": name_ref(RUPEE),
    "EventPerformerRef": ref(ENABLE_WARP),
    "ModelInfoRef": ref(RUPEE_MODEL),
    "PouchContentRef": ref(RUPEE_POUCH),
}


def shared():
    """Members every Obj_Item_Base pickup pack holds, one content per path (as in the game)."""
    return {
        actor("Obj_Item_Base"): w({"Components": BASE_COMPONENTS}),
        DROP_AI: w({"RootAIRef": "Work/AI/Root/DropItem.root.ain"}),
        DROP_DEATH: w({"DeathProcedures": "Work/System/CombinationDataTableData/DropItem.gyml"}),
        PICK_UP: w({"AlwaysEventMember": True}),
        ENABLE_WARP: w(
            {"$parent": work(PICK_UP), "EventUniqueAin": "Work/AI/Root/Event/PouchContent_EnableWarp.event.root.ain"}
        ),
        EVENT_GRAPH: b"AIB synthetic pouch event graph, opaque",
    }


def key_pack():
    return {
        **shared(),
        actor(fk.KEY): w({"$parent": work(actor("Obj_Item_Base")), "Components": KEY_COMPONENTS}),
        KEY_POUCH: w({"$parent": work(POUCH_DEFAULT), "DefaultAutoGet": True, "PouchActor": work(actor(fk.KEY_GRANT))}),
        KEY_MODEL: w({"FmdbName": fk.KEY, "ModelProjectName": fk.KEY}),
        KEY_ANIMATION: w({"AnimationResources": [{"ModelProjectName": "Obj_Dungeon_SmallKey_Animation"}]}),
        KEY_ELINK: w({"UserName": fk.KEY}),
        KEY_PHYSICS: w({"ControllerSetPath": "Work/Phive/ControllerSetParam/KeySmall.phive__ControllerSetParam.gyml"}),
        "Phive/ControllerSetParam/KeySmall.phive__ControllerSetParam.bgyml": w({"Body": "Body"}),
    }


def rupee_pack():
    return {
        **shared(),
        actor(RUPEE): w({"$parent": work(actor("Obj_Item_Base")), "Components": RUPEE_COMPONENTS}),
        RUPEE_POUCH: w(
            {
                "$parent": work(RUPEE_DEFAULT),
                "BundleActor": work(actor("Obj_Rupee_Green")),
                "BundleActorNum": I32(20),
                "IsBundle": True,
            }
        ),
        RUPEE_DEFAULT: w({"$parent": work(POUCH_DEFAULT), "DefaultAutoGet": True, "IsPlayGetEventPouchMax": True}),
        RUPEE_MODEL: w({"FmdbName": "Obj_Rupee", "ModelProjectName": "Obj_Rupee"}),
    }


def actor_rows():
    def row(name, actor_name, model, animation, heap, link):
        return {
            "ActorName": actor_name,
            "AnimationResources": [{"ModelProjectName": animation}] if animation else None,
            "CalcRadius": F32(45.0),
            "ELinkUserName": link,
            "FmdbName": model,
            "InstanceHeapSize": U32(heap),
            "ModelProjectName": model,
            "PreActorRenderInfoHeapSize": U32(7000),
            "__RowId": name,
        }

    rows = [
        row("Obj_A_Filler", "Obj_A_Filler", "Obj_A", "Obj_A_Animation", 10, "Obj_A"),
        row(fk.KEY, fk.KEY_GRANT, fk.KEY, "Obj_Dungeon_SmallKey_Animation", 1000, fk.KEY),
        row(RUPEE, RUPEE, "Obj_Rupee", None, 2000, None),
    ]
    for item in rows:  # an absent field is no field, as a native row omits it
        for field in ("AnimationResources", "ELinkUserName"):
            if item[field] is None:
                del item[field]
    return rows


def game_actor_rows():
    return [
        {"__RowId": "Obj_A_Filler"},
        {"MainRigidBodyLayer": "SmallObject", "__RowId": fk.KEY},
        {"IsRespawn": True, "MainRigidBodyLayer": "SmallObject", "__RowId": RUPEE},
    ]


def pouch_rows():
    return [
        {
            "BundleActorNum": I32(1),
            "PouchCategory": "KeyItem",
            "PouchGetType": "Large",
            "PouchSpecialDeal": "SmallKey",
            "PouchStockable": True,
            "PouchTabCategory": "KeyItem",
            "__RowId": fk.KEY,
        },
        {
            "BundleActor": work(actor("Obj_Rupee_Green")),
            "BundleActorNum": I32(20),
            "PouchCategory": "Rupee",
            "PouchGetType": "Small",
            "PouchSpecialDeal": "None",
            "PouchTabCategory": "KeyItem",
            "__RowId": RUPEE,
        },
    ]


def game_data():
    rows = [
        {
            "DefaultValue": False,
            "Hash": U32(murmur3_32(s.collected.encode())),
            "ResetTypeValue": I32(8),
            "SaveFileIndex": I32(0),
        }
        for s in (fk.WELL, fk.SHADOW)
    ]
    return {"Data": {"Bool": rows}}


def banc_tree(source):
    key = {
        "Dynamic": {fk.ROOM_KEY: I32(source.room)},
        "Gyaml": fk.KEY,
        "Hash": U64(source.id),
        "Phive": {"Placement": {"ID": U64(source.id)}},
        "Translate": [F32(1.0), F32(2.0), F32(3.0)],
    }
    actors = [
        {"Gyaml": "DungeonRoomCenterAnchor", "Hash": U64(ANCHOR), "Translate": [F32(0.0), F32(0.0), F32(0.0)]},
        key,
    ]
    references = [{"Id": "Anchor_1", "Path": "Anchor_1", "Reference": U64(ANCHOR)}]
    references.append({"Id": source.reference, "Path": source.reference, "Reference": U64(source.id)})
    if source.reveal:
        actors.append({"Gyaml": "Obj_ShadowTemple_SkullPot_A_01", "Hash": U64(POT)})
        actors.append(
            {
                "Dynamic": {"RequestEventName": source.reveal.event},
                "Gyaml": fk.REQUESTER,
                "Hash": U64(source.reveal.requester),
                "Links": [
                    {
                        "Dst": U64(source.id),
                        "Gyaml": "Reference",
                        "Name": "Reference",
                        "Src": U64(source.reveal.requester),
                    },
                    {
                        "Dst": U64(DESTINATION),
                        "Gyaml": "Reference",
                        "Name": "Reference",
                        "Src": U64(source.reveal.requester),
                    },
                ],
            }
        )
        references.append({"Id": "Pot_1", "Path": "Pot_1", "Reference": U64(POT)})
    group = [U64(ANCHOR), U64(source.id)]
    return {
        "Actors": actors,
        "AiGroups": [{"Hash": U64(source.group), "Logic": source.logic, "References": references}],
        "FarDeleteGroups": [list(group)],
        "SimultaneousGroups": [list(group)],
    }


def reveal_flow(*, other_uses_key=False):
    actors = [
        evfl.Actor("EventSystemActor", actions=["EventWait"]),
        evfl.Actor(fk.KEY, actions=[fk.REVEAL_ACTION]),
        evfl.Actor("Npc_Navi", actions=["EventPlayAS"]),
    ]
    events = [
        evfl.ActionEvent("Event0", 0, 0, next=1, params={"Frame": I32(10)}),
        evfl.ActionEvent("Event1", 1, 0, next=2, params={"ASName": "Act_Pop", "IsWaitEnd": True}),
        evfl.ActionEvent("Event2", 1, 0, params={"ASName": "Rotate_Obj", "IsWaitEnd": False}),
        evfl.ActionEvent("Event3", 2, 0, params={"ASName": "Talk"}),
    ]
    if other_uses_key:
        events[3] = evfl.ActionEvent("Event3", 2, 0, next=2, params={"ASName": "Talk"})
    entries = [evfl.EntryPoint(fk.SHADOW.reveal.entry, 0), evfl.EntryPoint("Other_Gimmick", 3)]
    return evfl.EventFlowFile(
        fk.SHADOW.reveal.flow, flowchart=evfl.Flowchart(fk.SHADOW.reveal.flow, actors, events, entries)
    )


def event_settings():
    reveal = fk.SHADOW.reveal
    return [
        {"EntryPointName": "Other_Gimmick", "FlowchartFileName": "Work/Event/EventFlow/X.evfc", "__RowId": "A_Event"},
        {
            "EntryPointName": reveal.entry,
            "FlowchartFileName": f"Work/Event/EventFlow/{reveal.flow}.evfc",
            "__RowId": reveal.event,
        },
    ]


def put(root, path, data):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    dictionaries = zsdic.Dictionaries.from_romfs(root)
    target.write_bytes(dictionaries.compress(path, data) if path.endswith(".zs") else data)


def raw(root, path):
    data = (root / path).read_bytes()
    return zsdic.Dictionaries.from_romfs(root).decompress(path, data) if path.endswith(".zs") else data


def edit_byml(root, path, change, byte_order="little"):
    tree = byml.read(raw(root, path))
    change(tree)
    put(root, path, byml.write(tree, byte_order))


def edit_pack(root, owner, name, change):
    path = fk.pack_path(owner)
    pack = sarc.read(raw(root, path))
    tree = byml.read(pack[name])
    change(tree)
    pack[name] = byml.write(tree)
    put(root, path, sarc.write(pack))


@pytest.fixture
def world(tmp_path, zsdic_pack, monkeypatch):
    sources = {
        location: dataclasses.replace(source, module_sha256=hashlib.sha256(MODULE_BYTES[source.module]).hexdigest())
        for location, source in fk.SOURCES.items()
    }
    monkeypatch.setattr(fk, "SOURCES", sources)
    root = tmp_path / "romfs"
    (root / "Pack").mkdir(parents=True)
    (root / "Pack/ZsDic.pack.zs").write_bytes(zsdic_pack)
    table = rstb.ResourceSizeTable()
    for owner, pack in ((fk.KEY, key_pack()), (RUPEE, rupee_pack())):
        put(root, fk.pack_path(owner), sarc.write(pack))
        table.set(fk.pack_path(owner), 1 << 20)
        for name in pack:
            table.set(name, NATIVE_ENTRY)
    for path, rows in zip(REGISTRIES, (actor_rows(), game_actor_rows(), pouch_rows()), strict=True):
        put(root, path, byml.write(rows))
        table.set(path, 1 << 20)
    put(root, GAME_DATA_LIST, byml.write(game_data(), "big"))
    put(root, EVENT_SETTING, byml.write(event_settings()))
    put(root, FLOW_VERSIONS, byml.write({"Versions": {"SomeVersionedFlow": "110"}}))
    put(root, fk.SHADOW.reveal.path, evfl.write(reveal_flow()))
    table.set(fk.SHADOW.reveal.path, 1 << 20)
    for source in sources.values():
        put(root, source.banc, byml.write(banc_tree(source)))
        put(root, source.module, MODULE_BYTES[source.module])
        table.set(source.banc, 1 << 20)
    put(root, rstb.TABLE_PATH, rstb.write(table))
    return root


def changed(world, delivery, path):
    return delivery.changes[path](raw(world, path))


def source_pack(delivery, source):
    return sarc.read(delivery.new_files[fk.pack_path(source.actor)].data)


# --- the public contract -------------------------------------------------------------------------------------------


def test_the_palette_and_sources_are_explicit():
    assert fk.PALETTE == {"Rupees (20)": RUPEE}
    assert {name: source.key for name, source in fk.SOURCES.items()} == {
        "Bottom of the Well Freestanding Key": "Small Key (Bottom of the Well)",
        "Shadow Temple Freestanding Key": "Small Key (Shadow Temple)",
    }
    assert len({source.actor for source in fk.SOURCES.values()}) == len(fk.SOURCES)


def test_sources_are_the_census_definitions_and_world_locations():
    defined = {d.id: d for d in census_definitions.load()}
    world = load_world()
    for name, source in fk.SOURCES.items():
        definition = defined[str(source.id)] if str(source.id) in defined else defined[source.id]
        assert (definition.kind, definition.oot_randomizer_name, definition.vanilla_item) == (
            FREESTANDING,
            name,
            fk.KEY,
        )
        assert PurePosixPath(source.banc).parts[1] == definition.area
        assert world.locations[name].vanilla == source.key
    assert "Rupees (20)" in world.items


def test_native_inputs_are_unique_and_name_every_source_file():
    inputs = fk.native_inputs()
    assert len(inputs) == len(set(inputs))
    for source in fk.SOURCES.values():
        assert {source.banc, source.module} <= set(inputs)
    assert {fk.KEY_PACK, fk.pack_path(RUPEE), fk.SHADOW.reveal.path, *REGISTRIES} <= set(inputs)


def test_native_keys_change_nothing_and_read_nothing(tmp_path):
    delivery = fk.build(tmp_path / "absent", {WELL: fk.WELL.key, SHADOW: fk.SHADOW.key})
    assert delivery == fk.Delivery({}, {}, {}, ())


@pytest.mark.parametrize(
    ("placements", "message"),
    [
        ({"KF Midos Top Left Chest": "Rupees (20)"}, "is not a floor key source"),
        (
            {WELL: fk.SHADOW.key},
            "is not a supported floor key reward",
        ),  # another dungeon's key credits the standing one
        ({SHADOW: "Small Key (Thieves Hideout)"}, "is not a supported floor key reward"),
        ({WELL: "Progressive Hookshot"}, "is not a supported floor key reward"),
        ({SHADOW: "Hylian Shield"}, "is not a supported floor key reward"),
        ({WELL: "Piece of Heart"}, "is not a supported floor key reward"),
    ],
)
def test_unsupported_sources_and_items_are_refused_before_reading(tmp_path, placements, message):
    with pytest.raises(PatchError, match=message):
        fk.build(tmp_path / "absent", placements)


# --- a moved source --------------------------------------------------------------------------------------------------


def test_a_moved_well_source_changes_only_its_gyaml_and_registers_its_actor(world):
    delivery = fk.build(world, {WELL: "Rupees (20)", SHADOW: fk.SHADOW.key})
    assert set(delivery.changes) == {fk.WELL.banc, *REGISTRIES}
    assert set(delivery.new_files) == {fk.pack_path(fk.WELL.actor)}
    assert delivery.actors == {WELL: fk.WELL.actor}
    after = byml.read(changed(world, delivery, fk.WELL.banc))
    placed = next(a for a in after["Actors"] if a["Hash"] == fk.WELL.id)
    assert placed.pop("Gyaml") == fk.WELL.actor
    expected = banc_tree(fk.SOURCES[WELL])
    del next(a for a in expected["Actors"] if a["Hash"] == fk.WELL.id)["Gyaml"]
    assert byml.same(after, expected)  # Hash, room, level-logic reference, groups: all native


def test_the_source_actor_is_a_key_child_with_the_rewards_identity_and_native_pouch(world):
    delivery = fk.build(world, BOTH)
    native_key, native_rupee = key_pack(), rupee_pack()
    for source in fk.SOURCES.values():
        file = delivery.new_files[fk.pack_path(source.actor)]
        pack = sarc.read(file.data)
        leaf = byml.read(pack[actor(source.actor)])
        assert leaf == {
            "$parent": work(actor(fk.KEY)),
            "Components": {"ActorNameRef": name_ref(RUPEE), "PouchContentRef": ref(RUPEE_POUCH)},
        }
        assert set(pack) - set(file.copied) == {actor(source.actor)}
        for name, owner in file.copied.items():
            assert owner in (fk.KEY_PACK, fk.pack_path(RUPEE))
            assert pack[name] == (native_key if owner == fk.KEY_PACK else native_rupee)[name]
        assert set(native_key) <= set(pack)  # the whole native key pack, graph-only members included
        assert {name for name, owner in file.copied.items() if owner != fk.KEY_PACK} == {RUPEE_POUCH, RUPEE_DEFAULT}
        components, chain = actor_packs.resolve([pack], actor(source.actor))
        key_components = actor_packs.resolve([native_key], actor(fk.KEY))[0]["Components"]
        assert chain == [actor("Obj_Item_Base"), actor(fk.KEY), actor(source.actor)]
        assert components["Components"] == {
            **key_components,
            "ActorNameRef": name_ref(RUPEE),
            "PouchContentRef": ref(RUPEE_POUCH),
        }
        pouch = actor_packs.resolve_node([pack], RUPEE_POUCH, builtin=POUCH_DEFAULT)
        assert (pouch.get("PouchActor"), pouch["IsBundle"], pouch["BundleActorNum"]) == (None, True, 20)


def test_registry_rows_keep_every_native_row_and_add_key_display_with_reward_identity(world):
    delivery = fk.build(world, BOTH)
    native = {ACTOR_INFO: actor_rows(), GAME_ACTOR_INFO: game_actor_rows(), POUCH_ACTOR_INFO: pouch_rows()}
    actors = sorted(source.actor for source in fk.SOURCES.values())
    for path in REGISTRIES:
        after = byml.read(changed(world, delivery, path))
        ids = [row["__RowId"] for row in after]
        assert ids == sorted(ids, key=lambda i: i.encode("utf-8"))
        assert byml.same([row for row in after if row["__RowId"] not in actors], native[path])
        rows = {row["__RowId"]: row for row in after}
        key_row = {row["__RowId"]: row for row in native[path]}
        for name in actors:
            new = dict(rows[name])
            del new["__RowId"]
            if path == ACTOR_INFO:
                expected = {**key_row[fk.KEY], "ActorName": RUPEE, "InstanceHeapSize": U32(3000)}
            elif path == GAME_ACTOR_INFO:
                expected = dict(key_row[fk.KEY])
            else:
                expected = dict(key_row[RUPEE])
            del expected["__RowId"]
            assert byml.same(new, expected)


def test_registry_insertion_keeps_rows_another_step_inserted_but_refuses_a_changed_donor(world):
    delivery = fk.build(world, BOTH)
    table = byml.read(raw(world, POUCH_ACTOR_INFO))
    table.insert(1, {"PouchCategory": "Rupee", "__RowId": "Obj_GoldSkulltulaDrop_Item"})
    after = byml.read(delivery.changes[POUCH_ACTOR_INFO](byml.write(table)))
    assert "Obj_GoldSkulltulaDrop_Item" in [row["__RowId"] for row in after]
    table[-1]["BundleActorNum"] = I32(50)
    with pytest.raises(PatchError, match="row Obj_Rupee_Red changed"):
        delivery.changes[POUCH_ACTOR_INFO](byml.write(table))


def test_the_shadow_reveal_flow_renames_only_its_key_actor(world):
    delivery = fk.build(world, {SHADOW: "Rupees (20)"})
    assert set(delivery.changes) == {fk.SHADOW.banc, fk.SHADOW.reveal.path, *REGISTRIES}
    after = evfl.read(changed(world, delivery, fk.SHADOW.reveal.path))
    expected = reveal_flow()
    expected.flowchart.actors[1].name = fk.SHADOW.actor
    assert after == expected
    tree = byml.read(changed(world, delivery, fk.SHADOW.banc))
    requester = next(a for a in tree["Actors"] if a["Hash"] == fk.SHADOW.reveal.requester)
    assert requester["Links"][0]["Dst"] == fk.SHADOW.id  # the reveal's link to the source is the same Hash


def test_transforms_recheck_their_inputs_and_refuse_a_second_application(world):
    delivery = fk.build(world, BOTH)
    for path in (fk.WELL.banc, fk.SHADOW.reveal.path, ACTOR_INFO):
        once = changed(world, delivery, path)
        with pytest.raises(PatchError):
            delivery.changes[path](once)


def test_build_is_deterministic(world):
    first = fk.build(world, BOTH)
    second = fk.build(world, dict(reversed(list(BOTH.items()))))
    assert {p: f.data for p, f in first.new_files.items()} == {p: f.data for p, f in second.new_files.items()}
    assert set(first.changes) == set(second.changes)
    for path in first.changes:
        assert changed(world, first, path) == changed(world, second, path)


def test_inputs_are_named_by_native_inputs(world):
    delivery = fk.build(world, BOTH)
    assert set(delivery.inputs) <= set(fk.native_inputs())
    assert set(fk.native_inputs()) - set(delivery.inputs) == {"Pack/ZsDic.pack.zs"}


def test_the_common_writer_writes_the_source_packs_with_copy_provenance(world, tmp_path):
    delivery = fk.build(world, BOTH)
    out = tmp_path / "out"
    written = write(Plan([], [], []), world, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)
    paths = {info.path for info in written}
    assert {*delivery.changes, *delivery.new_files, rstb.TABLE_PATH} == paths
    dictionaries = zsdic.Dictionaries.from_romfs(world)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    for source in fk.SOURCES.values():
        path = fk.pack_path(source.actor)
        assert dictionaries.decompress(path, (out / "romfs" / path).read_bytes()) == delivery.new_files[path].data
        assert table.get(actor(source.actor)) is not None
        assert table.get(RUPEE_POUCH) == NATIVE_ENTRY  # copied members keep their native entries


# --- refused dumps ---------------------------------------------------------------------------------------------------


def _first_key(tree, source):
    return next(a for a in tree["Actors"] if a.get("Hash") == source.id)


def _set(mapping, key, value):
    mapping[key] = value


def _register_source(table):
    table.append({"__RowId": fk.WELL.actor})
    table.sort(key=lambda row: row["__RowId"])


STALE = {
    "source Gyaml": (
        lambda root: edit_byml(root, fk.WELL.banc, lambda t: _set(_first_key(t, fk.WELL), "Gyaml", RUPEE)),
        "stale source",
    ),
    "instance drop override": (
        lambda root: edit_byml(
            root, fk.WELL.banc, lambda t: _set(_first_key(t, fk.WELL)["Dynamic"], "Drop__DropActor", RUPEE)
        ),
        "stale source",
    ),
    "named instance": (
        lambda root: edit_byml(root, fk.SHADOW.banc, lambda t: _set(_first_key(t, fk.SHADOW), "Name", "Key")),
        "stale source",
    ),
    "level reference": (
        lambda root: edit_byml(
            root, fk.WELL.banc, lambda t: _set(t["AiGroups"][0]["References"][1], "Id", "Obj_Rupee_Red_0000")
        ),
        "level-logic bindings",
    ),
    "level module": (
        lambda root: edit_byml(root, fk.SHADOW.banc, lambda t: _set(t["AiGroups"][0], "Logic", "Logic/Other.ain")),
        "level-logic bindings",
    ),
    "group membership": (
        lambda root: edit_byml(root, fk.WELL.banc, lambda t: t["SimultaneousGroups"].append([U64(fk.WELL.id)])),
        "invalid SimultaneousGroups",
    ),
    "reveal link": (
        lambda root: edit_byml(root, fk.SHADOW.banc, lambda t: t["Actors"][-1]["Links"].pop(0)),
        "is linked by",
    ),
    "module bytes": (lambda root: put(root, fk.WELL.module, b"AIB another module"), "not the inspected module"),
    "retiring Bool": (
        lambda root: edit_byml(
            root, GAME_DATA_LIST, lambda t: _set(t["Data"]["Bool"][1], "ResetTypeValue", I32(0)), "big"
        ),
        "expected one saved Bool",
    ),
    "key identity": (
        lambda root: edit_pack(
            root, fk.KEY, actor(fk.KEY), lambda t: _set(t["Components"], "ActorNameRef", name_ref("Item_Other"))
        ),
        "native contract",
    ),
    "key lifecycle": (
        lambda root: edit_pack(root, fk.KEY, actor(fk.KEY), lambda t: t["Components"].pop("ActorGameDataSetting")),
        "native contract",
    ),
    "reward performer": (
        lambda root: edit_pack(
            root, RUPEE, actor(RUPEE), lambda t: _set(t["Components"], "EventPerformerRef", ref(PICK_UP))
        ),
        "pickup mechanism",
    ),
    "reward grant shape": (
        lambda root: edit_byml(root, POUCH_ACTOR_INFO, lambda t: _set(t[1], "PouchGetType", "Large")),
        "native grant shape",
    ),
    "registered source actor": (
        lambda root: edit_byml(root, GAME_ACTOR_INFO, _register_source),
        "already exists",
    ),
    "unsorted registry": (
        lambda root: edit_byml(root, ACTOR_INFO, lambda t: t.reverse()),
        "not uniquely sorted",
    ),
    "reveal entry": (
        lambda root: edit_byml(root, EVENT_SETTING, lambda t: _set(t[1], "EntryPointName", "Other_Gimmick")),
        "runs",
    ),
    "versioned reveal flow": (
        lambda root: edit_byml(root, FLOW_VERSIONS, lambda t: _set(t["Versions"], fk.SHADOW.reveal.flow, "110")),
        "is versioned",
    ),
    "shared reveal actor": (
        lambda root: put(root, fk.SHADOW.reveal.path, evfl.write(reveal_flow(other_uses_key=True))),
        "key actor events reached from",
    ),
}


@pytest.mark.parametrize("stale", sorted(STALE))
def test_stale_native_inputs_fail_before_output_with_values(world, stale):
    change, message = STALE[stale]
    change(world)
    with pytest.raises(PatchError, match=message):
        fk.build(world, BOTH)


def test_a_reward_with_another_pickup_mechanism_is_refused_even_if_admitted(world, monkeypatch):
    """A palette entry is not trusted: the reward must still share the key's performer, AI and death."""
    shield = {
        **shared(),
        actor("Obj_Shield_Hylian"): w(
            {
                "$parent": work(actor("Obj_Item_Base")),
                "Components": {"ActorNameRef": name_ref("Weapon_Shield_Hylian"), "PouchContentRef": ref(RUPEE_POUCH)},
            }
        ),
        RUPEE_POUCH: rupee_pack()[RUPEE_POUCH],
        RUPEE_DEFAULT: rupee_pack()[RUPEE_DEFAULT],
    }
    put(world, fk.pack_path("Obj_Shield_Hylian"), sarc.write(shield))
    monkeypatch.setattr(fk, "PALETTE", {"Hylian Shield": "Obj_Shield_Hylian"})
    with pytest.raises(PatchError, match="pickup mechanism"):
        fk.build(world, {WELL: "Hylian Shield"})


# --- the player's dump -----------------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def original(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path):
        data = (romfs / path).read_bytes()
        return dictionaries.decompress(path, data) if path.endswith(".zs") else data

    return read


@pytest.fixture(scope="module")
def dump_delivery(romfs):
    return fk.build(romfs, BOTH)


@pytest.mark.dump
def test_dump_every_input_exists(romfs):
    assert [path for path in fk.native_inputs() if not (romfs / path).is_file()] == []


@pytest.mark.dump
def test_dump_sources_are_the_census_floor_keys(romfs):
    census = {location.id: location for location in scan(romfs)}
    for source in fk.SOURCES.values():
        location = census[source.id]
        assert (location.kind, location.actor, tuple(location.files)) == (FREESTANDING, fk.KEY, (source.banc,))


@pytest.mark.dump
def test_dump_moved_sources_change_only_gyaml_flow_actor_and_new_rows(original, dump_delivery):
    delivery = dump_delivery
    assert set(delivery.changes) == {fk.WELL.banc, fk.SHADOW.banc, fk.SHADOW.reveal.path, *REGISTRIES}
    for source in fk.SOURCES.values():
        before, after = (
            byml.read(original(source.banc)),
            byml.read(delivery.changes[source.banc](original(source.banc))),
        )
        changes = [
            (a["Hash"], a["Gyaml"], b["Gyaml"])
            for a, b in zip(before["Actors"], after["Actors"], strict=True)
            if a != b
        ]
        assert changes == [(source.id, fk.KEY, source.actor)]
        _first_key(after, source)["Gyaml"] = fk.KEY
        assert byml.same(before, after)
    flow = original(fk.SHADOW.reveal.path)
    before, after = evfl.read(flow), evfl.read(delivery.changes[fk.SHADOW.reveal.path](flow))
    renamed = [
        (i, a.name, b.name)
        for i, (a, b) in enumerate(zip(before.flowchart.actors, after.flowchart.actors, strict=True))
        if a != b
    ]
    assert [(name, new) for _, name, new in renamed] == [(fk.KEY, fk.SHADOW.actor)]
    after.flowchart.actors[renamed[0][0]].name = fk.KEY
    assert after == before
    for path in REGISTRIES:
        native = byml.read(original(path))
        rows = byml.read(delivery.changes[path](original(path)))
        added = {source.actor for source in fk.SOURCES.values()}
        assert byml.same([row for row in rows if row["__RowId"] not in added], native)
        assert len(rows) == len(native) + len(added)


@pytest.mark.dump
def test_dump_source_packs_are_native_key_packs_plus_one_leaf(original, dump_delivery):
    key = sarc.read(original(fk.KEY_PACK))
    rupee = sarc.read(original(fk.pack_path(RUPEE)))
    key_components = actor_packs.resolve([key], actor(fk.KEY))[0]["Components"]
    rupee_components = actor_packs.resolve([rupee], actor(RUPEE))[0]["Components"]
    for source in fk.SOURCES.values():
        file = dump_delivery.new_files[fk.pack_path(source.actor)]
        pack = sarc.read(file.data)
        assert set(pack) - set(file.copied) == {actor(source.actor)}
        for name, owner in file.copied.items():
            assert pack[name] == {fk.KEY_PACK: key, fk.pack_path(RUPEE): rupee}[owner][name]
        assert set(key) <= set(pack)
        components = actor_packs.resolve([pack], actor(source.actor))[0]["Components"]
        identity = {name: rupee_components[name] for name in fk.IDENTITY}
        assert components == {**key_components, **identity}
        assert fk.canonical(components) == RUPEE
        for name in ("AIInfoRef", "ASRef", "AnimationRef", "ModelInfoRef", "PhysicsRef", "ActorGameDataSetting"):
            assert components[name] == key_components[name]


@pytest.mark.dump
def test_dump_the_common_writer_writes_both_sources(romfs, dump_delivery, tmp_path):
    out = tmp_path / "out"
    written = write(
        Plan([], [], []), romfs, out, extra_changes=(dump_delivery.changes,), new_files=dump_delivery.new_files
    )
    assert {info.path for info in written} == {*dump_delivery.changes, *dump_delivery.new_files, rstb.TABLE_PATH}
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for path, file in dump_delivery.new_files.items():
        assert dictionaries.decompress(path, (out / "romfs" / path).read_bytes()) == file.data


@pytest.mark.dump
def test_dump_native_keys_change_nothing(romfs):
    assert fk.build(romfs, {WELL: fk.WELL.key, SHADOW: fk.SHADOW.key}) == fk.Delivery({}, {}, {}, ())
