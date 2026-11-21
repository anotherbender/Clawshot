"""The excluded-locations picker: the bundled world's checks as choices, names left to the selected world."""

import pytest

from clawshot.app import schema, settings_payload, validate

KEY = "excluded_locations"
CHEST = "KF Kokiri Sword Chest"
SONG = "Song from Impa"  # Zelda's Lullaby, one of the twelve song checks


def picker() -> dict:
    return next(row for row in schema() if row["key"] == KEY)


@pytest.mark.parametrize("names", [[CHEST], (CHEST,)])
def test_list_or_tuple_of_names_validates_and_replays(names):
    settings = validate({KEY: names})
    assert settings.excluded_locations == (CHEST,)
    payload = settings_payload(settings)
    assert list(payload["values"][KEY]) == [CHEST]
    assert validate(text=payload["settings_string"]) == settings


@pytest.mark.parametrize("value", [CHEST, [1], None])
def test_names_must_be_a_list_of_strings(value):
    with pytest.raises(ValueError, match="Excluded locations must be a list of location names"):
        validate({KEY: value})


def test_unshuffled_progression_is_refused():
    with pytest.raises(ValueError, match="unshuffled progression"):
        validate({KEY: [SONG]})  # Chest only: the song check keeps Zelda's Lullaby


def test_gift_exclusions_check_expanded_gift_kinds_and_the_default_song_hold():
    values = {"shuffle": ["Chest", "Gift"], KEY: [SONG]}
    assert validate({**values, "songs": "anywhere"}).excluded_locations == (SONG,)
    with pytest.raises(ValueError, match="Excluded locations make this item pool impossible"):
        validate({**values, "songs": "song"})  # twelve songs held to twelve song checks, one now excluded


def test_realistic_gift_list_is_not_refused_for_gifts_that_stay_vanilla():
    # The bean seller is a "more" gift: it stays vanilla, so its shop-only bean needs no room on a shelf.
    frogs = [name for name in picker()["choices"] if name.startswith("ZR Frogs")]
    names = [*frogs, "Kak 100 Gold Skulltula Reward"]
    settings = validate({"shuffle": ["Chest", "Gift"], KEY: names})
    assert settings.excluded_locations == tuple(sorted(names))
