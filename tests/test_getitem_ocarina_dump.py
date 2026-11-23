"""The chest ocarinas' get model in a real generated seed, against the dump (plans/chest-ocarina-model.md, run O).

A Chest + Gift + Token seed with both ocarinas in chests, so ActorInfo also carries another step's rows; every
difference from the dump is named. A seed with no ocarina in a chest carries none of it (Q1 option b)."""

import pytest

from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.generate import Settings
from clawshot.patch import getitem, gifts, make_seed, ocarina, write_seed
from clawshot.patch.shops import actor_path, member_path
from clawshot.world.load import load_spec

SETTINGS = Settings(shuffle=("Chest", "Gift", "Token"))
# Both ocarinas go to these chests (swapped with what the fill put there), whatever the fill chose.
CHESTS = {"KF Midos Top Left Chest": "Fairy Ocarina", "KF Midos Top Right Chest": "Ocarina of Time"}
# Steps allowed to change ActorInfo rows besides the ocarina step: they add rows of their own.
ROW_STEPS = {
    "clawshot.patch.tokens",
    "clawshot.patch.custom_items",
    "clawshot.patch.floor_keys",
    "clawshot.patch.jail_keys",
}


def chest_ocarina_seed(romfs):
    """As the CLI builds a Gift seed (``gifts.seed_setup``), then both ocarinas swapped into :data:`CHESTS`."""
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), SETTINGS)
    filled = make_seed(romfs, 7, settings, spec, extra_steps=[step])
    placements = {name: filled.seed.placements[name] for name in filled.seed.shuffled}
    for chest, item in CHESTS.items():
        source = next(name for name, placed in placements.items() if placed == item)
        placements[source], placements[chest] = placements[chest], item
    return make_seed(romfs, 7, settings, spec, extra_steps=[step], placements=placements)


@pytest.fixture(scope="module")
def seed(romfs, tmp_path_factory):
    output = chest_ocarina_seed(romfs)
    assert {name: output.seed.placements[name] for name in CHESTS} == CHESTS
    out = tmp_path_factory.mktemp("ocarina-seed")
    written = {info.path: info for info in write_seed(output, romfs, out)}
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path, root=None):
        root = romfs if root is None else out / "romfs"
        return dictionaries.decompress(path, (root / path).read_bytes())

    return output, written, read, lambda path: read(path, out)


@pytest.mark.dump
def test_a_seed_without_a_chest_ocarina_keeps_the_native_rows_and_packs(romfs, tmp_path):
    output = make_seed(romfs, 7, Settings(shuffle=("Chest", "Token")))  # Chest-only kinds: no ocarina in the pool
    written = {info.path for info in write_seed(output, romfs, tmp_path / "seed")}
    assert not written & set(map(getitem.pack_path, getitem.OCARINAS)), sorted(written)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    rows = byml.read(
        dictionaries.decompress(getitem.ACTOR_INFO, (tmp_path / "seed/romfs" / getitem.ACTOR_INFO).read_bytes())
    )
    by_id = {row["__RowId"]: row for row in rows}
    assert [by_id[actor].get("CalcPriority") for actor in getitem.OCARINAS] == ["After", "After"]
    assert "CalcPriority" not in by_id[getitem.SARIA_PROP]


def step_module(transform):
    function = getattr(transform, "func", transform)
    return function.__module__


@pytest.mark.dump
def test_a_chest_ocarina_seed_runs_the_ocarina_step_last_on_its_files(seed):
    output, written, _, _ = seed
    paths = (getitem.ACTOR_INFO, *map(getitem.pack_path, getitem.OCARINAS))
    for path in paths:
        assert path in written, f"{path} is not in the output"
        touching = [i for i, step in enumerate(output.extra_changes) if path in step]
        last = output.extra_changes[touching[-1]][path]
        assert step_module(last) == getitem.__name__, (
            path,
            [step_module(output.extra_changes[i][path]) for i in touching],
        )
    # It comes after ocarina.changes (the Time-stays-equipped receipts) in the recipe.
    steps = [{step_module(t) for t in step.values()} for step in output.extra_changes]
    assert max(i for i, m in enumerate(steps) if ocarina.__name__ in m) < len(steps) - 1
    assert steps[-1] == {getitem.__name__}


@pytest.mark.dump
def test_actor_info_differs_from_the_dump_only_by_the_calc_priorities_and_named_steps_rows(seed):
    output, _, native, written = seed
    other = [step[getitem.ACTOR_INFO] for step in output.extra_changes[:-1] if getitem.ACTOR_INFO in step]
    names = sorted({step_module(transform) for transform in other})
    print(f"ActorInfo row steps before the ocarina step: {names}")
    assert set(names) <= ROW_STEPS, names
    expected = native(getitem.ACTOR_INFO)
    for transform in other:
        expected = transform(expected)
    expected_rows = byml.read(expected)
    before = {row["__RowId"] for row in byml.read(native(getitem.ACTOR_INFO))}
    assert [row["__RowId"] for row in expected_rows if row["__RowId"] not in before], "a Token seed adds pickup rows"
    for row in expected_rows:
        if row["__RowId"] in getitem.OCARINAS:
            assert row.pop("CalcPriority") == "After", row["__RowId"]
        if row["__RowId"] == getitem.SARIA_PROP:
            assert "CalcPriority" not in row, row
            row["CalcPriority"] = "After"
    after = byml.read(written(getitem.ACTOR_INFO))
    difference = byml.difference(after, expected_rows)
    assert difference is None, difference
    # 1.7: the written table reads back to the same tree.
    assert byml.same(byml.read(byml.dump(byml.load(written(getitem.ACTOR_INFO)))), after)


@pytest.mark.dump
@pytest.mark.parametrize("actor", getitem.OCARINAS)
def test_ocarina_pack_differs_from_native_only_by_the_get_model(seed, actor):
    _, _, native, written = seed
    path = getitem.pack_path(actor)
    before, data = sarc.read(native(path)), written(path)
    after = sarc.read(data)
    assert sarc.write(after) == data, f"{path} does not read back"
    donor = sarc.read(native(getitem.pack_path(getitem.DONOR)))
    animation = getitem.animation_member(actor)
    added = sorted(set(after) - set(before))
    assert added == sorted([animation, getitem.PERFORMER]), added
    assert not set(before) - set(after), sorted(set(before) - set(after))
    assert after[getitem.PERFORMER] == donor[getitem.PERFORMER], "PouchContent performer is not the donor's bytes"
    assert byml.read(after[animation]) == {
        "AnimationResources": [
            {"ModelProjectName": "Item_Common_Animation"},
            {"ModelProjectName": f"{actor}_Animation"},
        ]
    }, byml.read(after[animation])
    param = member_path(actor_path(actor))
    old, new = byml.read(before[param]), byml.read(after[param])
    expected = {
        **old["Components"],
        "EventPerformerRef": "?" + getitem.PERFORMER,
        "ASRef": "?" + getitem.ANIMATION_SET,
        "AnimationRef": "?" + animation,
    }
    assert old["Components"]["EventPerformerRef"] == "?" + getitem.COMMON_PERFORMER
    difference = byml.difference(new, {**old, "Components": expected})
    assert difference is None, difference
    changed = sorted(name for name in before if name != param and after[name] != before[name])
    assert changed == [], changed


@pytest.mark.dump
def test_ocarina_size_entries(seed, romfs):
    _, _, native, written = seed
    original = rstb.read(native(rstb.TABLE_PATH))
    table = rstb.read(written(rstb.TABLE_PATH))
    for actor in getitem.OCARINAS:
        pack = sarc.read(written(getitem.pack_path(actor)))
        param = member_path(actor_path(actor))
        components = len(byml.read(pack[param])["Components"])
        needed = rstb.required_size(param, len(pack[param]), components)
        assert table.get(param) == max(original.get(param), needed), (param, original.get(param), needed)
        animation = getitem.animation_member(actor)
        assert original.get(animation) is None, animation
        entry = rstb.required_size(animation, len(pack[animation]), resources=2)
        assert table.get(animation) == entry, (animation, table.get(animation), entry)
        print(f"{actor}: ActorParam {original.get(param)} -> {table.get(param)}, AnimationParam {entry}")
    assert table.get(getitem.PERFORMER) == original.get(getitem.PERFORMER) is not None
    assert table.get(getitem.ACTOR_INFO) >= original.get(getitem.ACTOR_INFO)
    for path in getitem.OCARINA_DUMP_FILES:
        assert (romfs / path).is_file(), path
