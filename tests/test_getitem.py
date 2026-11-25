"""Presentation changes must not alter the item being granted or its pouch behavior."""

import copy
from functools import partial

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.patch import getitem
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.shops import actor_path, member_path
from clawshot.patch.write import write


def actor_pack(actor):
    model = f"Component/ModelInfo/{actor}.engine__component__ModelInfo.bgyml"
    root = {"Components": {"ModelInfoRef": "?" + model, "EventPerformerRef": "?" + getitem.PERFORMER}}
    name = "Obj_Rupee"
    pack = {
        member_path(actor_path(actor)): byml.write(root),
        model: byml.write({"FmdbName": name, "ModelProjectName": name}),
        "PouchContent": byml.write({"PouchActor": actor, "SpecialDeal": "unchanged"}),
    }
    pack[getitem.PERFORMER] = byml.write({"Native": True})
    return sarc.write(pack), model


def swap_model(data, *, actor):
    """The song's ModelInfo pointed at its ocarina and nothing else: the substitution ``member_growth`` sizes (the
    song step, ``patch.songs``, makes it among its other edits)."""
    pack = sarc.read(data)
    model = member_path(byml.read(pack[member_path(actor_path(actor))])["Components"]["ModelInfoRef"])
    tree = byml.load(pack[model])
    tree.root["FmdbName"] = tree.root["ModelProjectName"] = getitem.SONG_MODELS[actor]
    pack[model] = byml.dump(tree)
    return sarc.write(pack)


def test_structural_growth_cannot_borrow_a_string_substitution_allocation():
    actor = "Item_Melody_StormSong"
    before, model = actor_pack(actor)
    pack = sarc.read(swap_model(before, actor=actor))
    tree = byml.read(pack[model])
    tree["NewArray"] = [byml.I32(1)]
    pack[model] = byml.write(tree)
    with pytest.raises(PatchError):
        getitem.member_growth(before, sarc.write(pack))


def test_common_writer_reserves_nested_model_growth_without_lowering_other_entries(tmp_path, zsdic_pack):
    actor = "Item_Melody_StormSong"
    before, model = actor_pack(actor)
    # Put the synthetic original exactly on a size bucket boundary.
    pack = sarc.read(before)
    pack[model] = byml.write(byml.read(pack[model]) | {"Padding": ""})
    before = sarc.write(pack)
    transform = partial(swap_model, actor=actor)
    after = sarc.read(transform(before))
    old = sarc.read(before)
    delta = ((len(after[model]) + 31) // 32 - (len(old[model]) + 31) // 32) * 32
    assert delta > 0
    romfs = tmp_path / "dump"
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    path = getitem.pack_path(actor)
    for name, content in ((zsdic.PACK_PATH, zsdic_pack), (path, dictionaries.compress(path, before))):
        (romfs / name).parent.mkdir(parents=True, exist_ok=True)
        (romfs / name).write_bytes(content)
    table = rstb.ResourceSizeTable()
    table.set(model, 6000)
    table.set(path, 1 << 20)
    table.set("Unrelated", 1234)
    table_path = romfs / rstb.TABLE_PATH
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_bytes(dictionaries.compress(rstb.TABLE_PATH, rstb.write(table)))
    out = tmp_path / "out"
    write(Plan([], [], []), romfs, out, extra_changes=({path: transform},))
    result = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    expected = copy.deepcopy(table)
    expected.set(model, 6000 + delta)
    assert result == expected


def ocarina_rows():
    def row(name, **fields):
        return {"__RowId": name, "ActorName": name, "InstanceHeapSize": byml.U32(100), **fields}

    return [
        row("Item_Boomerang", CalcPriority="After"),
        row(getitem.FAIRY, CalcPriority="After"),
        row("Obj_TokenPickup_Custom"),
        row(getitem.TIME, CalcPriority="After"),
        row(getitem.SARIA_PROP),
    ]


def test_ocarina_actor_info_moves_calc_priority_from_the_instruments_to_saria_prop():
    rows = ocarina_rows()
    result = getitem.patch_ocarina_actor_info(byml.write(rows, byte_order="big"))
    assert byml.byte_order(result) == "big"
    after = byml.read(result)
    expected = copy.deepcopy(rows)
    del expected[1]["CalcPriority"], expected[3]["CalcPriority"]
    # Saria's prop shares the Fairy Ocarina's model project; it now calculates after, as the instrument did.
    expected[4]["CalcPriority"] = "After"
    assert byml.same(after, expected), byml.difference(after, expected)


def test_ocarina_actor_info_needs_no_row_order_or_native_snapshot():
    # Rows added by earlier steps (custom items, tokens, keys) and a different order change nothing.
    rows = [*reversed(ocarina_rows()), {"__RowId": "Clawshot_Added", "ActorName": "Clawshot_Added"}]
    after = byml.read(getitem.patch_ocarina_actor_info(byml.write(rows)))
    assert [row["__RowId"] for row in after] == [row["__RowId"] for row in rows]
    by_id = {row["__RowId"]: row for row in after}
    assert "CalcPriority" not in by_id[getitem.FAIRY] and "CalcPriority" not in by_id[getitem.TIME]
    assert by_id["Item_Boomerang"]["CalcPriority"] == "After"
    assert by_id[getitem.SARIA_PROP]["CalcPriority"] == "After"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda rows: rows.pop(1), "Item_Ocarina_Fairy: no ActorInfo row"),
        (lambda rows: rows.pop(3), "Item_Ocarina_Time: no ActorInfo row"),
        (lambda rows: rows[1].pop("CalcPriority"), "Item_Ocarina_Fairy: CalcPriority is None"),
        (lambda rows: rows[3].__setitem__("CalcPriority", "Before"), "Item_Ocarina_Time: CalcPriority is 'Before'"),
        (lambda rows: rows.pop(4), "Dm_Item_Ocarina_Fairy_Saria: no ActorInfo row"),
        (lambda rows: rows[4].__setitem__("CalcPriority", "After"), "Dm_Item_Ocarina_Fairy_Saria: CalcPriority is"),
    ],
)
def test_ocarina_actor_info_refuses_a_changed_native_row(change, message):
    rows = ocarina_rows()
    change(rows)
    with pytest.raises(PatchError, match=message):
        getitem.patch_ocarina_actor_info(byml.write(rows))


COMMON = "Component/EventPerformerParam/Common.engine__component__EventPerformerParam.bgyml"
NATIVE_POUCH_PERFORMER = byml.write({"Synthetic": "pouch performer"})


def ocarina_pack(actor, **components):
    """A native-shaped ocarina pack: equipment components, the Common performer, no animation."""
    own = {
        "AccessoryRef": f"?Component/AccessoryParam/{actor}.game__component__AccessoryParam.bgyml",
        "BlackboardRef": "?Component/Blackboard/BlackboardInfo/EquipmentCommon.engine__component__BlackboardInfo.bgyml",
        "EventPerformerRef": "?" + COMMON,
        "ModelInfoRef": f"?Component/ModelInfo/{actor}.engine__component__ModelInfo.bgyml",
        "SystemSetting": "?ActorSystem/ActorSystemSetting/GameActorAfter.engine__actor__ActorSystemSetting.bgyml",
    }
    own.update(components)
    own = {key: value for key, value in own.items() if value is not None}
    return {
        member_path(actor_path(actor)): byml.write({"Components": own}),
        f"Component/AccessoryParam/{actor}.game__component__AccessoryParam.bgyml": byml.write({"Hand": "L"}),
        COMMON: byml.write({"Common": True}),
        f"Component/ModelInfo/{actor}.engine__component__ModelInfo.bgyml": byml.write({"FmdbName": actor}),
    }


def donor_pack(**extra):
    return sarc.write({getitem.PERFORMER: NATIVE_POUCH_PERFORMER, "Other/Donor.bgyml": b"not copied", **extra})


@pytest.mark.parametrize("actor", getitem.OCARINAS)
def test_ocarina_pack_gets_pouch_performer_animation_set_and_own_animation(actor):
    before = ocarina_pack(actor)
    result = getitem.patch_ocarina_pack(sarc.write(before), actor=actor, donor=donor_pack())
    after = sarc.read(result)
    assert sarc.write(after) == result  # 1.7: the pack reads back
    animation = f"Component/AnimationParam/{actor}.engine__component__AnimationParam.bgyml"
    assert getitem.animation_member(actor) == animation
    # 4.3/4.4: exactly two members are added, the performer byte-identical to the donor's; no other member changes.
    assert sorted(set(after) - set(before)) == sorted([animation, getitem.PERFORMER])
    assert after[getitem.PERFORMER] == NATIVE_POUCH_PERFORMER
    # 4.2: the new member is built in code, in this order.
    assert byml.read(after[animation]) == {
        "AnimationResources": [
            {"ModelProjectName": "Item_Common_Animation"},
            {"ModelProjectName": f"{actor}_Animation"},
        ]
    }
    assert after[animation] == getitem.animation_param(actor)
    # 4.1: the component diff.
    param = member_path(actor_path(actor))
    old, new = byml.read(before[param])["Components"], byml.read(after[param])["Components"]
    assert new == old | {
        "EventPerformerRef": "?" + getitem.PERFORMER,
        "ASRef": "?AS/Item_Common.root.asb",
        "AnimationRef": "?" + animation,
    }
    for name in before:
        if name != param:
            assert after[name] == before[name], name


@pytest.mark.parametrize(
    ("components", "donor", "message"),
    [
        ({"EventPerformerRef": "?" + getitem.PERFORMER}, donor_pack(), "EventPerformerRef is"),
        ({"EventPerformerRef": None}, donor_pack(), "EventPerformerRef is None"),
        ({"ASRef": "?AS/Item_Common.root.asb"}, donor_pack(), "already has ASRef"),
        ({"AnimationRef": "?Component/AnimationParam/X.bgyml"}, donor_pack(), "already has AnimationRef"),
        ({}, sarc.write({"Other/Donor.bgyml": b""}), "donor Item_Boomerang has no"),
    ],
)
def test_ocarina_pack_refuses_a_changed_native_pack_or_donor(components, donor, message):
    actor = getitem.FAIRY
    with pytest.raises(PatchError, match=message):
        getitem.patch_ocarina_pack(sarc.write(ocarina_pack(actor, **components)), actor=actor, donor=donor)


@pytest.mark.parametrize("extra", ["animation", "performer"])
def test_ocarina_pack_refuses_members_it_would_add(extra):
    actor = getitem.TIME
    pack = ocarina_pack(actor)
    name = getitem.animation_member(actor) if extra == "animation" else getitem.PERFORMER
    pack[name] = b"already there"
    with pytest.raises(PatchError, match="already holds"):
        getitem.patch_ocarina_pack(sarc.write(pack), actor=actor, donor=donor_pack())


def ocarina_romfs(root, zsdic_pack, *, missing=None):
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    files = {zsdic.PACK_PATH: zsdic_pack}
    donor = getitem.pack_path(getitem.DONOR)
    files[donor] = dictionaries.compress(donor, donor_pack())
    for actor in getitem.OCARINAS:
        path = getitem.pack_path(actor)
        files[path] = dictionaries.compress(path, sarc.write(ocarina_pack(actor)))
    files.pop(missing, None)
    for name, content in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_bytes(content)
    return dictionaries


def test_ocarina_changes_touch_actor_info_and_both_packs(tmp_path, zsdic_pack):
    dictionaries = ocarina_romfs(tmp_path, zsdic_pack)
    assert getitem.OCARINA_DUMP_FILES == (
        "AS/Item_Common.root.asb.zs",
        "Model/Item_Common_Animation.anim.bfres.zs",
        "Model/Item_Ocarina_Fairy_Animation.anim.bfres.zs",
        "Model/Item_Ocarina_Time_Animation.anim.bfres.zs",
    )
    changes = getitem.ocarina_changes(tmp_path)
    assert sorted(changes) == sorted([getitem.ACTOR_INFO, *map(getitem.pack_path, getitem.OCARINAS)])
    for actor in getitem.OCARINAS:
        path = getitem.pack_path(actor)
        native = dictionaries.decompress(path, (tmp_path / path).read_bytes())
        assert sarc.read(changes[path](native))[getitem.PERFORMER] == NATIVE_POUCH_PERFORMER


def test_ocarina_changes_refuse_a_dump_without_the_donor_pack(tmp_path, zsdic_pack):
    ocarina_romfs(tmp_path, zsdic_pack, missing="Pack/Actor/Item_Boomerang.pack.zs")
    with pytest.raises(PatchError, match=r"Pack/Actor/Item_Boomerang\.pack\.zs"):
        getitem.ocarina_changes(tmp_path)


def test_no_chest_props_are_staged_and_the_unwired_song_swap_is_gone():
    # The round-8 prop staging is gone: no seed changes Dm_SY_TreasureboxSmall or Dm_SY_Treasurebox for ocarinas.
    assert not hasattr(getitem, "patch_chest_flow") and not hasattr(getitem, "CHEST_FLOWS")
    # The song mesh swap is replaced by the song get effects (patch.songs, spec song-get-effects S11).
    assert not any(hasattr(getitem, name) for name in ("changes", "patch_pack", "patch_actor_info"))


def test_native_inputs_name_every_dump_file_the_ocarina_step_reads():
    inputs = getitem.native_inputs()
    assert len(inputs) == len(set(inputs))
    assert set(inputs) == {
        "Pack/ZsDic.pack.zs",
        getitem.ACTOR_INFO,
        getitem.pack_path(getitem.DONOR),
        *map(getitem.pack_path, getitem.OCARINAS),
    }


def test_ocarina_changes_need_nothing_beyond_their_native_inputs(tmp_path, zsdic_pack):
    # The synthetic romfs holds only what ocarina_romfs writes; every file it writes is a declared input.
    ocarina_romfs(tmp_path, zsdic_pack)
    present = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file()}
    assert present <= set(getitem.native_inputs())
    assert getitem.ocarina_changes(tmp_path)


def test_the_app_working_set_holds_the_ocarina_inputs():
    from types import SimpleNamespace

    from clawshot.pack.source import resource_spec, working_files

    wanted = working_files(SimpleNamespace(files=[]), resource_spec())
    assert set(getitem.native_inputs()) <= wanted, sorted(set(getitem.native_inputs()) - wanted)


@pytest.mark.parametrize(
    ("shuffle", "runs"),
    [
        (("Chest", "Gift"), True),
        (("Chest", "Gift", "Token"), True),
        (("Chest", "NPC", "Song", "Cutscene", "Boss"), True),  # Gift as the types it expands to
        (("Chest",), False),  # the defaults: no ocarina can reach a chest
        (("Chest", "Token"), False),
        (("Gift",), False),  # gifts move, chests stay: no ocarina can reach a chest
        ((), False),
    ],
)
def test_the_ocarina_get_model_runs_when_chest_and_gift_shuffle_are_both_on(shuffle, runs):
    assert getitem.chest_ocarinas_possible(shuffle) is runs


def test_only_a_chest_holding_an_ocarina_asks_for_the_get_model():
    from clawshot.patch.items import ItemActors

    actors = ItemActors(
        actors={"Fairy Ocarina": getitem.FAIRY, "Ocarina of Time": getitem.TIME, "Bow": "Item_Bow"}, sources={}
    )
    placements = {"Chest A": "Bow", "Chest B": "Ocarina of Time", "Saria": "Fairy Ocarina", "Chest C": "Nothing"}
    chests = ["Chest A", "Chest B", "Chest C"]
    assert getitem.chest_ocarinas(placements, chests, actors) == ["Chest B"]
    # An ocarina outside a chest (a gift, its vanilla spot) does not count.
    assert getitem.chest_ocarinas(placements, ["Chest A", "Chest C"], actors) == []
