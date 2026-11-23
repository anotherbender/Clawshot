"""The song get effects on the player's dump (plan 8.2-8.5, 8.9): the step's output decodes to the data file's values
and keeps every native user, effect, member and row; a seed with moved songs writes them all and places no pickup;
a seed without one writes none of them; the same seed gives the same folder in two processes."""

import math
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import pytest
from test_elink_dump import decoded_users

from clawshot.formats import byml, elink, rstb, sarc, vfx, zsdic
from clawshot.generate import Settings
from clawshot.patch import getitem, gifts, make_seed, songs, write_seed
from clawshot.patch import items as item_actors
from clawshot.patch.plan import Plan
from clawshot.patch.shops import actor_path, member_path
from clawshot.patch.write import write
from clawshot.world.load import load_spec

EFFECTS = songs.load_effects()
SONG_SEED = ("--seed", "4242", "--shuffle", "Chest", "Gift", "--songs", "anywhere")  # all twelve songs move
FEATURE_FILES = (
    songs.ELINK,
    songs.STATIC,
    *(getitem.pack_path(s) for s in getitem.SONG_MODELS),
    *(getitem.pack_path(songs.pickup_name(s)) for s in getitem.SONG_MODELS),
)


@pytest.fixture(scope="module")
def applied(romfs):
    """The step built on the dump and every change applied to its native file."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    delivery = songs.build(romfs)
    native = {path: dicts.decompress(path, (romfs / path).read_bytes()) for path in delivery.changes}
    return delivery, native, {path: transform(native[path]) for path, transform in delivery.changes.items()}


@pytest.mark.dump
def test_dump_elink_users_decode_to_the_data_file_and_natives_stay(applied):
    """2.1: the twelve users' calls carry the values of data/song_effects.toml; every native user is unchanged."""
    _, native, out = applied
    before, after = elink.decode(native[songs.ELINK]), elink.decode(out[songs.ELINK])
    names = before.user_names()
    assert decoded_users(after, names) == decoded_users(before, names)
    for song, effect in EFFECTS.songs.items():
        user = songs.user_name(song)
        if isinstance(effect, songs.NonWarpEffect):
            for key in ("Wait", "GetDemo"):
                params = after.call_params(user, key)
                assert params["RuntimeAssetName"] == effect.effect and params["Scale"] == pytest.approx(effect.scale)
                assert params["Bone"] == "Root"
            assert after.call_params(user, "GetDemo")["PositionY"] == 0.0
            continue
        calls = after.calls(user)
        for key, place, condition in (
            ("Wait", effect.floor, EFFECTS.floor_condition),
            ("GetDemo", effect.get_pose, EFFECTS.get_pose_condition),
        ):
            kind, first, last = after.container(user, key)
            assert (kind, last - first) == (3, 8)
            for i in range(9):
                child, call = after.call_params(user, first + i), calls[first + i]
                assert call.condition == condition and child["Bone"] == "Root"
                assert child["RuntimeAssetName"] == (songs.SPARK, songs.AURA, songs.LIGHT)[min(i // 4, 2)]
                colour = (place.sparks, place.aura, place.light)[min(i // 4, 2)]
                assert (child["Red"], child["Green"], child["Blue"]) == pytest.approx(colour)
                assert (child["Scale"], child["PositionY"]) == pytest.approx((place.scale, place.position_y))
                assert (child["RotationX"], child["LifeScale"]) == pytest.approx((effect.rotation_x, effect.life_scale))
                radius = effect.ring_radius if i < 8 else 0.0
                angle = math.radians(90 * (i % 4))
                assert child["PositionX"] == pytest.approx(radius * math.cos(angle), abs=1e-6)


@pytest.mark.dump
def test_dump_static_gets_the_clones_and_keeps_every_effect(applied):
    """2.2"""
    _, native, out = applied
    before, after = byml.read(native[songs.STATIC])["PtclBin"].data, byml.read(out[songs.STATIC])["PtclBin"].data
    names = vfx.effect_names(before)
    assert vfx.effect_names(after) == names + list(songs.CLONES)
    for name, keep in songs.CLONES.items():
        assert vfx.emitters(after, name) == list(keep)
    assert [n for n in names if vfx.effect_bytes(after, n) != vfx.effect_bytes(before, n)] == []
    vfx.check(after, dict.fromkeys(songs.CLONES, songs.CHARGE))


@pytest.mark.dump
def test_dump_song_packs_and_rows(applied):
    """2.3: each song pack changed as the record says and otherwise native; its row shows the ocarina."""
    _, native, out = applied
    rows = {row["__RowId"]: row for row in byml.read(out[songs.ACTOR_INFO])}
    native_rows = {row["__RowId"]: row for row in byml.read(native[songs.ACTOR_INFO])}
    for song, ocarina in getitem.SONG_MODELS.items():
        path = getitem.pack_path(song)
        old, new = sarc.read(native[path]), sarc.read(out[path])
        param = member_path(actor_path(song))
        components = byml.read(new[param])["Components"]
        assert components["XLinkRef"] == songs.XLINK and components["ASRef"] == "?AS/Item_Common.root.asb"
        model = member_path(components["ModelInfoRef"])
        assert byml.read(new[model])["FmdbName"] == ocarina
        added = {getitem.animation_member(song), songs.elink_member(song), member_path(components["ASInfoRef"])}
        assert set(new) == set(old) | added
        assert {n for n in old if new[n] != old[n]} == {param, model}
        for field in getitem.MODEL_FIELDS:
            assert rows[song][field] == native_rows[ocarina][field]
        assert rows[song]["ELinkUserName"] == songs.user_name(song)


@pytest.mark.dump
def test_dump_pickup_packs_and_rows(applied):
    """2.4: the twelve pickups and their rows in all three tables."""
    delivery, _, out = applied
    for path in (songs.ACTOR_INFO, songs.GAME_ACTOR_INFO, songs.POUCH_ACTOR_INFO):
        ids = [row["__RowId"] for row in byml.read(out[path])]
        assert {songs.pickup_name(s) for s in getitem.SONG_MODELS} <= set(ids), path
    for song in getitem.SONG_MODELS:
        pack = sarc.read(delivery.new_files[getitem.pack_path(songs.pickup_name(song))].data)
        components = byml.read(pack[member_path(actor_path(songs.pickup_name(song)))])["Components"]
        assert components["ActorNameRef"] == f"?ActorSystem/ActorName/{song}.engine__actor__ActorName.bgyml"
        assert byml.read(pack[songs.elink_member(songs.pickup_name(song))]) == {"UserName": songs.user_name(song)}


@pytest.fixture(scope="module")
def song_seed(romfs, tmp_path_factory):
    out = tmp_path_factory.mktemp("song-seed")
    # As the CLI builds a Gift seed (clawshot.__main__): the gift setup first, then make_seed.
    settings = Settings(shuffle=("Chest", "Gift"), songs="anywhere")
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
    output = make_seed(romfs, 4242, settings, spec, extra_steps=[step])
    written = write_seed(output, romfs, out)
    return output, {info.path: info for info in written}, out


@pytest.mark.dump
def test_dump_a_seed_with_moved_songs_writes_every_feature_file_and_places_no_pickup(romfs, song_seed):
    """2.1-2.4 in a seed: the files are written, .100 is not, and no placement file names a pickup (S3)."""
    output, files, out = song_seed
    assert songs.moved_songs(output.seed.placements, output.seed.world, item_actors.load())
    assert set(FEATURE_FILES) <= set(files)
    assert "ELink2/elink2.Product.100.belnk.zs" not in files
    assert songs.ELINK in output.extra_changes[-1]  # last on ActorInfo and the song packs
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    for path in files:
        if path.startswith("Banc/"):
            assert b"Obj_Clawshot_Melody_" not in dicts.decompress(path, (out / "romfs" / path).read_bytes()), path
    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    static = files[songs.STATIC]
    assert table.get(songs.STATIC) == rstb.required_size(songs.STATIC, static.new_size)  # own formula, no margin


@pytest.mark.dump
def test_dump_a_seed_without_moved_songs_writes_none_of_the_feature_files(romfs, tmp_path):
    output = make_seed(romfs, seed=4242, settings=Settings())
    assert not songs.moved_songs(output.seed.placements, output.seed.world, item_actors.load())
    assert all(songs.ELINK not in step for step in output.extra_changes)
    assert not set(FEATURE_FILES) & set(output.new_files)


@pytest.mark.dump
def test_dump_song_seed_same_folder_in_two_processes(romfs, tmp_path):
    """2.8: same seed, settings and version, two processes with different hash seeds: identical folders, the song
    files among them."""

    def run(hash_seed):
        out = tmp_path / f"run{hash_seed}"
        argv = [sys.executable, "-m", "clawshot", "--romfs", str(romfs), "--out", str(out), *SONG_SEED]
        result = subprocess.run(argv, capture_output=True, text=True, env={**os.environ, "PYTHONHASHSEED": hash_seed})
        assert result.returncode == 0, result.stderr
        return {p.relative_to(out).as_posix(): p.read_bytes() for p in sorted(out.rglob("*")) if p.is_file()}

    with ThreadPoolExecutor(2) as pool:
        first, second = pool.map(run, ("1", "2"))
    assert first == second
    named = (songs.ELINK, songs.STATIC, getitem.pack_path("Item_Melody_SunSong"))
    for path in (*named, getitem.pack_path(songs.pickup_name("Item_Melody_FireBolero"))):
        assert f"romfs/{path}" in first, path


@pytest.mark.dump
def test_dump_song_step_sizes_every_changed_and_new_member(romfs, tmp_path):
    """3.4 on the dump (replaces test_getitem_dump's oracle for the removed mesh swap): written through the common
    writer alone, every entry is the native one kept or raised to its formula, every new resource gets its formula,
    copied members keep the entry of what they copy, and the song ModelInfo keeps its native entry plus its rounded
    growth."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    delivery = songs.build(romfs)
    out = tmp_path / "songs"
    written = write(Plan([], [], []), romfs, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)
    original = rstb.read(dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    table = rstb.read(dicts.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    assert all(table.hashes[crc] >= entry for crc, entry in original.hashes.items())
    for info in written:
        if info.path == rstb.TABLE_PATH:
            continue
        need = rstb.required_size(info.path, info.new_size)
        assert table.get(info.path) == (need if info.entry is None else max(info.entry, need)), info.path
    for song in getitem.SONG_MODELS:
        path = getitem.pack_path(song)
        old = sarc.read(dicts.decompress(path, (romfs / path).read_bytes()))
        new = sarc.read(dicts.decompress(path, (out / "romfs" / path).read_bytes()))
        param = member_path(actor_path(song))
        components = byml.read(new[param])["Components"]
        need = rstb.required_size(param, len(new[param]), len(components))
        assert table.get(param) == max(original.get(param), need)
        model = member_path(components["ModelInfoRef"])
        growth = max(0, ((len(new[model]) + 31) // 32 - (len(old[model]) + 31) // 32) * 32)
        assert table.get(model) == original.get(model) + growth
        animation, link = getitem.animation_member(song), songs.elink_member(song)
        assert table.get(animation) == rstb.required_size(animation, len(new[animation]), resources=2)
        assert table.get(link) == rstb.required_size(link, len(new[link]))
        assert table.get(member_path(components["ASInfoRef"])) == original.get(member_path(components["ASInfoRef"]))
    for path, file in delivery.new_files.items():
        members = sarc.read(file.data)
        for name, source in file.copied.items():
            native = original.get(name)
            assert table.get(name) >= native, (path, name, source)
        for name in set(members) - set(file.copied):
            assert original.get(name) is None and table.get(name) is not None, name
