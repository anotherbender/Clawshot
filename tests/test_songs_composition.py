"""The song get effects composed with every other step on the same files, through the common writer (plan 8.6-8.8).

The synthetic seed is the custom-item, Skulltula and ocarina composition (``test_getitem_composition``: the real
custom-item, token and ocarina producers; floor- and jail-key rows as stand-ins), plus what the song step reads. The
song step runs last, as ``make_seed`` registers it."""

import pytest
from synthetic_effects import HEART_USERS, build_table
from test_custom_token_composition import CUSTOM_ACTORS, PICKUPS, write_combined
from test_custom_token_composition import combined as combined
from test_getitem_composition import STAND_INS, insert_row
from test_getitem_composition import ocarina_world as ocarina_world
from test_songs import AS_INFO, arrow_pack, heart_pack, song_pack, static_doc
from test_tokens import edit_byml, put, raw
from test_tokens import world as world

from clawshot.formats import byml, elink, rstb, sarc, vfx
from clawshot.formats.byml import F32, I32
from clawshot.patch import getitem, songs, tokens
from clawshot.patch.shops import actor_path, member_path

SONG_PARAM_ENTRY = 5300  # below what the grown song ActorParam needs, so the writer must raise it
MODEL_ENTRY = 4000
MEMBER_ENTRY = 6000


@pytest.fixture
def song_world(ocarina_world):
    """The composition romfs plus the song step's inputs: ELink table, static, song and donor packs, rows."""
    root = ocarina_world
    put(root, songs.ELINK, build_table(HEART_USERS))
    put(root, songs.STATIC, static_doc())
    sizes = rstb.read(raw(root, rstb.TABLE_PATH))
    for path in (songs.ELINK, songs.STATIC):
        sizes.set(path, rstb.required_size(path, len(raw(root, path))))
    packs = {songs.EFFECT_DONOR: heart_pack(), songs.PICKUP_DONOR: arrow_pack()}
    packs.update({song: song_pack(song) for song in getitem.SONG_MODELS})
    for actor, pack in packs.items():
        put(root, getitem.pack_path(actor), sarc.write(pack))
        sizes.set(getitem.pack_path(actor), 1 << 20)
        for name in pack:
            sizes.set(name, MEMBER_ENTRY)
    for song in getitem.SONG_MODELS:
        sizes.set(member_path(actor_path(song)), SONG_PARAM_ENTRY)
        sizes.set(f"Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml", MODEL_ENTRY)
    put(root, rstb.TABLE_PATH, rstb.write(sizes))

    model = {"ModelAabbMin": [F32(-1.0)] * 3, "ModelAabbMax": [F32(1.0)] * 3}
    heaps = {"InstanceHeapSize": I32(1000), "PreActorRenderInfoHeapSize": I32(200)}

    def add_rows(rows):
        for row in rows:
            if row["__RowId"] in getitem.OCARINAS:
                row.update(FmdbName=row["__RowId"], ModelProjectName=row["__RowId"], **model, **heaps)
        rows.extend(
            {"__RowId": s, "ActorName": s, "FmdbName": "Obj_Rupee", "ModelProjectName": "Obj_Rupee", **model, **heaps}
            for s in getitem.SONG_MODELS
        )
        rows.append({"__RowId": songs.PICKUP_DONOR, "ActorName": "Item_Arrow_Fire", "SLinkUserName": "X", **heaps})
        rows.sort(key=lambda row: row["__RowId"].encode("utf-8"))

    edit_byml(root, tokens.ACTOR_INFO, add_rows)

    def add_game_rows(rows):  # the token step needs both registries to list the same rows
        rows.extend({"__RowId": actor, "IsRespawn": False} for actor in (*getitem.SONG_MODELS, songs.PICKUP_DONOR))
        rows.sort(key=lambda row: row["__RowId"].encode("utf-8"))

    edit_byml(root, tokens.GAME_ACTOR_INFO, add_game_rows)

    def add_pouch_rows(rows):
        rows.extend({"__RowId": song, "Category": "Melody"} for song in getitem.SONG_MODELS)
        rows.sort(key=lambda row: row["__RowId"].encode("utf-8"))

    edit_byml(root, tokens.POUCH_ACTOR_INFO, add_pouch_rows)
    return root


@pytest.fixture
def composed(song_world, tmp_path):
    delivery = songs.build(song_world)
    steps = (*map(insert_row, STAND_INS), getitem.ocarina_changes(song_world), delivery.changes)
    return write_combined(song_world, tmp_path / "seed", later_steps=steps, later_files=delivery.new_files)


def chain(composed, path):
    """The native file through every registered step that changes it, in order."""
    data = composed.native(path)
    for step in composed.output.extra_changes:
        if transform := step.get(path):
            data = transform(data)
    return data


def test_every_edit_lands_in_order_and_the_song_step_runs_last(composed):
    steps = composed.output.extra_changes
    assert songs.ELINK in steps[-1] and steps[-1][songs.ACTOR_INFO] is songs.patch_actor_info
    for path in (*tokens.REGISTRIES, songs.ELINK, songs.STATIC, *map(getitem.pack_path, getitem.SONG_MODELS)):
        assert composed.read(path) == chain(composed, path), path
    rows = {row["__RowId"]: row for row in byml.read(composed.read(tokens.ACTOR_INFO))}
    native = {row["__RowId"] for row in byml.read(composed.native(tokens.ACTOR_INFO))}
    pickups = {songs.pickup_name(s) for s in getitem.SONG_MODELS}
    assert set(rows) == native | set(STAND_INS) | set(CUSTOM_ACTORS) | set(PICKUPS) | pickups
    for actor in getitem.OCARINAS:  # the ocarina get model's edit is kept under the song step's
        assert "CalcPriority" not in rows[actor]
    for song, ocarina in getitem.SONG_MODELS.items():
        assert rows[song]["FmdbName"] == ocarina and rows[song]["ELinkUserName"] == songs.user_name(song)
    for path in tokens.REGISTRIES:
        ids = [row["__RowId"] for row in byml.read(composed.read(path))]
        assert ids == sorted(set(ids), key=lambda name: name.encode("utf-8")), path
        assert pickups <= set(ids), path


def test_every_changed_file_reads_back(composed):
    """8.8: the written ELink table, effect file, packs and tables decode to what the steps built."""
    table = elink.decode(composed.read(songs.ELINK))
    assert table.encode() == composed.read(songs.ELINK)
    assert {songs.user_name(s) for s in getitem.SONG_MODELS} <= set(table.user_names())
    static = byml.load(composed.read(songs.STATIC))
    assert static.version == 5 and byml.dump(static) == composed.read(songs.STATIC)
    vfx.check(static.root["PtclBin"].data, dict.fromkeys(songs.CLONES, songs.CHARGE))
    for path in (*tokens.REGISTRIES, *map(getitem.pack_path, getitem.SONG_MODELS), *composed.output.new_files):
        data = composed.read(path)
        if path.endswith(".pack.zs"):
            members = sarc.read(data)
            assert sarc.write(members) == data, path
            for name, content in members.items():
                if name.endswith(".bgyml"):
                    byml.read(content)
        else:
            assert byml.write(byml.read(data)) == data, path


def test_every_new_or_changed_entry_uses_its_formula_and_none_is_lowered(composed):
    """8.7: song and pickup members, the ELink table, static and the tables; every native entry kept or raised."""
    original = rstb.read(composed.native(rstb.TABLE_PATH))
    table = rstb.read(composed.read(rstb.TABLE_PATH))
    for crc, entry in original.hashes.items():
        assert table.hashes[crc] >= entry, hex(crc)
    for path in (songs.ELINK, songs.STATIC, *tokens.REGISTRIES):
        need = rstb.required_size(path, len(composed.read(path)))
        assert table.get(path) == max(original.get(path), need), path
    for song, ocarina in getitem.SONG_MODELS.items():
        pack = sarc.read(composed.read(getitem.pack_path(song)))
        param = member_path(actor_path(song))
        components = byml.read(pack[param])["Components"]
        need = rstb.required_size(param, len(pack[param]), len(components))
        assert table.get(param) == need > SONG_PARAM_ENTRY
        animation = getitem.animation_member(song)
        assert table.get(animation) == rstb.required_size(animation, len(pack[animation]), resources=2)
        link = songs.elink_member(song)
        assert table.get(link) == (len(pack[link]) + 31) // 32 * 32 + 5064
        assert table.get(AS_INFO) == MEMBER_ENTRY  # the heart container's member, native entry
        model = f"Component/ModelInfo/{song}.engine__component__ModelInfo.bgyml"
        before = sarc.read(composed.native(getitem.pack_path(song)))[model]
        growth = max(0, ((len(pack[model]) + 31) // 32 - (len(before) + 31) // 32) * 32)
        assert table.get(model) == MODEL_ENTRY + growth
        pickup = songs.pickup_name(song)
        path = getitem.pack_path(pickup)
        new = composed.output.new_files[path]
        members = sarc.read(new.data)
        assert table.get(path) == rstb.required_size(path, len(new.data))
        pickup_param = member_path(actor_path(pickup))
        count = len(byml.read(members[pickup_param])["Components"])
        assert table.get(pickup_param) == rstb.required_size(pickup_param, len(members[pickup_param]), count)
        pouch = songs.pouch_member(pickup)
        assert table.get(pouch) == rstb.required_size(pouch, len(members[pouch]))
        assert table.get(songs.elink_member(pickup)) == rstb.required_size(
            songs.elink_member(pickup), len(members[songs.elink_member(pickup)])
        )
        for name in new.copied:  # copied members keep the entry of the member they copy
            assert table.get(name) == (MODEL_ENTRY + growth if name == model else original.get(name)), name
        assert byml.read(members[model])["FmdbName"] == ocarina
