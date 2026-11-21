"""The excluded-locations picker: the bundled world's checks as choices, names left to the selected world."""

import pytest

from clawshot.app import schema, settings_payload, validate
from clawshot.generate.names import load as load_names
from clawshot.tracker import location_index
from clawshot.world import build_world, load_spec

KEY = "excluded_locations"
CHEST = "KF Kokiri Sword Chest"
SONG = "Song from Impa"  # Zelda's Lullaby, one of the twelve song checks


def picker() -> dict:
    return next(row for row in schema() if row["key"] == KEY)


def test_choices_are_the_bundled_worlds_item_checks_with_readable_labels_and_areas():
    row = picker()
    world = build_world(load_spec())
    live = {name for name, loc in world.locations.items() if loc.n64_only is None and loc.vanilla is not None}
    assert row["kind"] == "multi" and row["display"] == "locations" and list(row["default"]) == []
    assert len(row["choices"]) == len(live) and set(row["choices"]) == live
    catalog, places = load_names(), location_index()
    described = [name for name in row["choices"] if name in catalog]
    assert row["choices"][: len(described)] == described  # described checks lead, undescribed pots/rupees follow
    options = {option["value"]: option for option in row["options"]}
    assert options[CHEST]["label"] == catalog[CHEST].name != CHEST
    assert options[CHEST]["help"] == catalog[CHEST].where
    for name, option in options.items():
        assert option["area"] == places[name].area and option["type"] == world.locations[name].type
        assert option["help"].strip() and not option["disabled"]


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
