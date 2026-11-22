"""The ocarina get model composed with every other step that grows ``ActorInfo``, through the common writer.

The synthetic seed is the custom-item and Skulltula composition (``test_custom_token_composition``: the real
producers); the floor-key and jail-key rows are stand-ins inserted the way those steps insert theirs (sorted by
``__RowId``). The ocarina step runs last, as ``make_seed`` registers it."""

import pytest
from test_custom_token_composition import CUSTOM_ACTORS, PICKUPS, write_combined
from test_custom_token_composition import combined as combined
from test_getitem import ocarina_pack
from test_tokens import edit_byml, put, raw
from test_tokens import world as world

from clawshot.formats import byml, rstb, sarc
from clawshot.formats.byml import I32
from clawshot.patch import getitem, tokens
from clawshot.patch.shops import actor_path, member_path

STAND_INS = ("Obj_Clawshot_FloorKeyStandIn", "Obj_Clawshot_JailKeyStandIn")
PARAM_ENTRY = 5200  # below what the patched actor parameter needs, so the writer must raise it


def insert_row(name):
    def transform(data):
        document = byml.load(data)
        document.root.append({"__RowId": name, "ActorName": name, "InstanceHeapSize": I32(1)})
        document.root.sort(key=lambda row: row["__RowId"].encode("utf-8"))
        return byml.dump(document)

    return {tokens.ACTOR_INFO: transform}


@pytest.fixture
def ocarina_world(combined):
    """The composition romfs plus the two ocarina rows and packs and the files the fix names."""

    def add_rows(rows):
        rows.extend({"__RowId": a, "ActorName": a, "CalcPriority": "After"} for a in getitem.OCARINAS)
        rows.append({"__RowId": getitem.SARIA_PROP, "ActorName": getitem.SARIA_PROP})
        rows.sort(key=lambda row: row["__RowId"].encode("utf-8"))

    edit_byml(combined, tokens.ACTOR_INFO, add_rows)

    def add_game_rows(rows):  # the token step needs both registries to list the same rows
        rows.extend({"__RowId": actor, "IsRespawn": False} for actor in (*getitem.OCARINAS, getitem.SARIA_PROP))
        rows.sort(key=lambda row: row["__RowId"].encode("utf-8"))

    edit_byml(combined, tokens.GAME_ACTOR_INFO, add_game_rows)
    sizes = rstb.read(raw(combined, rstb.TABLE_PATH))
    for actor in getitem.OCARINAS:
        pack = ocarina_pack(actor)
        put(combined, getitem.pack_path(actor), sarc.write(pack))
        sizes.set(getitem.pack_path(actor), 1 << 20)
        for name in pack:
            sizes.set(name, PARAM_ENTRY)
    for path in getitem.OCARINA_DUMP_FILES:
        put(combined, path, b"synthetic")
    put(combined, rstb.TABLE_PATH, rstb.write(sizes))
    return combined


@pytest.fixture
def composed(ocarina_world, tmp_path):
    steps = (*map(insert_row, STAND_INS), getitem.ocarina_changes(ocarina_world))
    return write_combined(ocarina_world, tmp_path / "seed", later_steps=steps)


def test_every_actor_info_edit_lands_and_the_ocarina_step_runs_last(composed):
    steps = composed.output.extra_changes
    assert steps[-1][tokens.ACTOR_INFO] is getitem.patch_ocarina_actor_info
    expected = composed.native(tokens.ACTOR_INFO)
    for step in steps[:-1]:
        if transform := step.get(tokens.ACTOR_INFO):
            expected = transform(expected)
    expected = byml.read(expected)
    for row in expected:
        if row["__RowId"] in getitem.OCARINAS:
            del row["CalcPriority"]
        if row["__RowId"] == getitem.SARIA_PROP:
            row["CalcPriority"] = "After"
    after = byml.read(composed.read(tokens.ACTOR_INFO))
    assert byml.same(after, expected), byml.difference(after, expected)
    ids = {row["__RowId"] for row in after}
    native = {row["__RowId"] for row in byml.read(composed.native(tokens.ACTOR_INFO))}
    # Rows from the token pickups, the custom items and both stand-ins, on top of every native row.
    assert native < ids and set(STAND_INS) <= ids
    assert set(CUSTOM_ACTORS) <= ids and set(PICKUPS) <= ids


def test_ocarina_packs_and_size_entries_are_written(composed):
    original = rstb.read(composed.native(rstb.TABLE_PATH))
    table = rstb.read(composed.read(rstb.TABLE_PATH))
    for actor in getitem.OCARINAS:
        pack = sarc.read(composed.read(getitem.pack_path(actor)))
        param = member_path(actor_path(actor))
        components = byml.read(pack[param])["Components"]
        assert components["AnimationRef"] == "?" + getitem.animation_member(actor)
        # Two more own components, sized by the actor parameter formula; the native entry was short.
        needed = rstb.required_size(param, len(pack[param]), len(components))
        assert table.get(param) == needed > original.get(param) == PARAM_ENTRY
        # The new member: the measured AnimationParam rule with two AnimationResources entries.
        animation = getitem.animation_member(actor)
        assert table.get(animation) == (len(pack[animation]) + 31) // 32 * 32 + 5096 + 2 * 88
        # The copied performer keeps the native entry of the member it copies.
        assert table.get(getitem.PERFORMER) == original.get(getitem.PERFORMER) is not None
    info = composed.files[tokens.ACTOR_INFO]
    assert table.get(tokens.ACTOR_INFO) == max(info.entry, rstb.required_size(tokens.ACTOR_INFO, info.new_size))
    assert table.get(tokens.ACTOR_INFO) >= original.get(tokens.ACTOR_INFO)
