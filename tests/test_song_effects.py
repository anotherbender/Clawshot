"""The song effect values (``data/song_effects.toml``): complete, in range, and a malformed file names the problem."""

import re

import pytest

from clawshot.patch import getitem, songs

TEXT = songs.EFFECTS_TOML.read_text(encoding="utf-8")


def test_the_data_file_holds_all_twelve_songs():
    effects = songs.load_effects()
    assert set(effects.songs) == set(getitem.SONG_MODELS)
    assert "BBender" in effects.source and "SONGS3" in effects.source
    assert (effects.floor_condition, effects.get_pose_condition) == (0xF20, 0x4FC0)
    for song, effect in effects.songs.items():
        assert isinstance(effect, songs.WarpEffect) == (getitem.SONG_MODELS[song] == getitem.TIME), song


def test_values_as_confirmed_in_game():
    effects = songs.load_effects()
    lullaby = effects.songs["Item_Melody_ZeldaLullaby"]
    assert lullaby == songs.NonWarpEffect("Ply_Ocarina_Correct_ZeldaLullaby_00", 0.3)
    minuet = effects.songs["Item_Melody_ForestMinuet"]
    assert (minuet.ring_radius, minuet.rotation_x, minuet.life_scale) == (0.12, -1.5708, 0.5)
    assert minuet.floor == songs.Place(0.6, -0.15, (0.1, 1.5, 0.1), (0.05, 0.75, 0.05), (0.015, 0.225, 0.015))
    assert minuet.get_pose.aura == (0.065, 0.975, 0.065)
    assert minuet.get_pose.light == (0.0195, 0.2925, 0.0195)  # E8: 0.3 of the aura colour
    prelude = effects.songs["Item_Melody_LightPrelude"]
    assert prelude.floor.light == (0.6, 0.5, 0.35) and prelude.get_pose.light == (0.18, 0.15, 0.105)


def without_section(text: str, header: str) -> str:
    """``text`` without the TOML table ``[header]`` (up to the next table)."""
    return re.sub(rf"\[{re.escape(header)}\]\n(?:[^\[].*\n|\n)*", "", text)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda t: without_section(t, "songs.Item_Melody_SunSong"), "Item_Melody_SunSong: missing"),
        (lambda t: t.replace("light = [0.6, 0.5, 0.35]\n", "", 1), "Item_Melody_LightPrelude: floor.light"),
        (lambda t: t.replace("aura = [12.0, 0.0, 0.6]", "aura = [12.0, 0.0]", 1), "ShadowNocturne: floor.aura"),
        (lambda t: t.replace("scale = 0.3\n", 'scale = "big"\n', 1), "Item_Melody_ZeldaLullaby: scale"),
        (lambda t: t.replace("scale = 0.3\n", "scale = 0.0\n", 1), "Item_Melody_ZeldaLullaby: scale"),
        (lambda t: t.replace("scale = 0.6\n", "scale = true\n", 1), "Item_Melody_ForestMinuet: floor.scale"),
        (lambda t: t.replace("ring_radius = 0.12", "ring_radius = -0.1", 1), "Item_Melody_ForestMinuet: ring_radius"),
        (lambda t: t.replace("life_scale = 0.5", "life_scale = 0", 1), "Item_Melody_ForestMinuet: life_scale"),
        (lambda t: t.replace("sparks = [0.1, 1.5, 0.1]", "sparks = [-0.1, 1.5, 0.1]", 1), "ForestMinuet: floor.sparks"),
        (lambda t: t.replace('kind = "warp"', 'kind = "non_warp"', 1), "Item_Melody_ForestMinuet: kind"),
        (lambda t: t.replace('kind = "non_warp"', 'kind = "loud"', 1), "Item_Melody_ZeldaLullaby: kind"),
        (lambda t: t.replace('effect = "Ply_Ocarina_Correct_SunSong_00"\n', "", 1), "Item_Melody_SunSong: effect"),
        (lambda t: t + '\n[songs.Item_Melody_Extra]\nkind = "non_warp"\n', "Item_Melody_Extra: not a song"),
        (lambda t: t.replace("floor = 0xF20", "floor = -1", 1), "conditions: floor"),
        (lambda t: t.replace("source = ", "sauce = ", 1), "source"),
    ],
)
def test_a_malformed_file_names_the_song_and_key(change, message):
    text = change(TEXT)
    assert text != TEXT
    with pytest.raises(songs.SongEffectsError, match=re.escape(message)):
        songs.parse_effects(text)
