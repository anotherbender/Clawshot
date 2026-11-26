"""Bag bombs get a private no-strength component; shared native lift data stays intact."""

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.formats.byml import U32
from clawshot.patch import bombs
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import write


def native_pack(*, grade=bombs.LOW, ref="?" + bombs.NATIVE_LIFT):
    return {
        bombs.ACTOR: byml.write({"Components": {"LiftableRef": ref, "OtherRef": "unchanged"}}),
        bombs.NATIVE_LIFT: byml.write({"LiftGrade": U32(grade), "SyntheticOffset": 17}),
        "synthetic-untouched": b"not a BYML",
    }


def assert_isolated_patch(before):
    after = sarc.read(bombs.transform(sarc.write(before)))
    assert set(after) == set(before) | {bombs.BAG_LIFT}
    for name in before.keys() - {bombs.ACTOR}:
        assert after[name] == before[name], name
    expected_actor = byml.read(before[bombs.ACTOR])
    expected_actor["Components"]["LiftableRef"] = "?" + bombs.BAG_LIFT
    assert byml.read(after[bombs.ACTOR]) == expected_actor
    expected_lift = byml.read(before[bombs.NATIVE_LIFT])
    expected_lift["LiftGrade"] = U32(bombs.NONE)
    assert byml.read(after[bombs.BAG_LIFT]) == expected_lift
    return after


def test_bag_bomb_changes_only_private_lift_component():
    after = assert_isolated_patch(native_pack())
    # Even a second actor resolving the old shared member still requires Low.
    assert byml.read(after[bombs.NATIVE_LIFT])["LiftGrade"] == bombs.LOW


@pytest.mark.parametrize("grade,ref", [(bombs.NONE, "?" + bombs.NATIVE_LIFT), (bombs.LOW, "changed")])
def test_changed_native_contract_is_refused(grade, ref):
    with pytest.raises(PatchError, match="stale"):
        bombs.transform(sarc.write(native_pack(grade=grade, ref=ref)))


def test_already_patched_pack_is_refused():
    with pytest.raises(PatchError, match="already present"):
        bombs.transform(bombs.transform(sarc.write(native_pack())))


@pytest.mark.dump
def test_real_bomb_pack_keeps_shared_flower_component_native(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    before = sarc.read(dictionaries.decompress(bombs.PACK, (romfs / bombs.PACK).read_bytes()))
    after = assert_isolated_patch(before)
    flower_path = "Pack/Actor/Obj_BombFlower_A_01.pack.zs"
    flower = sarc.read(dictionaries.decompress(flower_path, (romfs / flower_path).read_bytes()))
    fruit = "Component/LiftableParam/Obj_BombFlower_Fruit.game__component__LiftableParam.bgyml"
    assert flower[bombs.NATIVE_LIFT] == after[bombs.NATIVE_LIFT]
    assert byml.read(flower[fruit])["LiftGrade"] == bombs.LOW


@pytest.mark.dump
@pytest.mark.parametrize("enabled", [False, True])
def test_writer_sizes_private_component_and_leaves_default_output_empty(romfs, tmp_path, enabled):
    output = tmp_path / "mod"
    write(Plan([], [], []), romfs, output, extra_changes=(bombs.changes(enabled=enabled),))
    output = output / "romfs"
    paths = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    assert paths == ({bombs.PACK, rstb.TABLE_PATH} if enabled else set())
    if enabled:
        dictionaries = zsdic.Dictionaries.from_romfs(romfs)
        table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (output / rstb.TABLE_PATH).read_bytes()))
        pack = sarc.read(dictionaries.decompress(bombs.PACK, (output / bombs.PACK).read_bytes()))
        assert len(pack[bombs.BAG_LIFT]) == len(pack[bombs.NATIVE_LIFT])
        native = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
        assert rstb.required_size(bombs.NATIVE_LIFT, len(pack[bombs.NATIVE_LIFT])) == native.get(bombs.NATIVE_LIFT)
        assert table.get(bombs.BAG_LIFT) == native.get(bombs.NATIVE_LIFT)
        assert table.get(bombs.PACK) >= rstb.required_size(bombs.PACK, len(sarc.write(pack)))
