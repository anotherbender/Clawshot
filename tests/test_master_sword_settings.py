"""Master Sword shuffle settings: default off, CLI/CS1/app plumbing and the conservative round-19 boundary
(shuffled chests, plus free time travel checked by app validation and generation). Built, not played."""

import base64
import json
import zlib

import pytest

from clawshot.__main__ import main
from clawshot.app.schema import presets, settings_payload, validate
from clawshot.generate import FillError, Settings, prepare
from clawshot.settings import DEFAULTS
from clawshot.world.load import load_spec

FIELD = "shuffle_master_sword"
FREE = "free_time_travel"
ON = Settings(shuffle_master_sword=True, logic={FREE: True})


@pytest.fixture(scope="module")
def spec():
    return load_spec()


def _payload(text: str) -> dict:
    """The JSON overrides inside a CS1 string."""
    if text == "CS1":
        return {}
    data = text.removeprefix("CS1.")
    return json.loads(zlib.decompress(base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))))


def _encode(overrides: dict) -> str:
    """A hand-made CS1 string, bypassing Settings, as a stale or edited share string would arrive."""
    compressed = zlib.compress(json.dumps(overrides, sort_keys=True, separators=(",", ":")).encode("utf-8"), 9)
    return "CS1." + base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")


def _printed(capsys, *argv: str) -> str:
    assert main([*argv, "--print-settings"]) == 0
    return capsys.readouterr().out.strip()


def test_default_is_off_and_existing_strings_and_spoiler_settings_keep_their_bytes(capsys):
    assert DEFAULTS[FIELD] is False
    assert Settings().shuffle_master_sword is False
    assert Settings.from_string("CS1").shuffle_master_sword is False
    assert Settings().to_string() == "CS1"
    assert FIELD not in Settings().as_dict()  # absent when off, like shuffle_hideout_keys
    for settings in (Settings(shuffle=("Chest", "Shop")), Settings(logic={FREE: True}), Settings(dungeon_rewards=True)):
        text = settings.to_string()
        assert FIELD not in _payload(text) and FIELD not in settings.as_dict()
        assert Settings.from_string(text) == settings
        assert Settings.from_string(text).shuffle_master_sword is False
    assert _printed(capsys) == "CS1"
    assert _printed(capsys, "--no-shuffle-master-sword") == "CS1"


def test_cli_accepts_with_free_time_travel_and_replays_unchanged(capsys):
    text = _printed(capsys, "--shuffle-master-sword", "--logic", "free_time_travel=true")
    assert _payload(text) == {FIELD: True, "logic": {FREE: True}}
    settings = Settings.from_string(text)
    assert settings == ON and settings.to_string() == text
    assert _printed(capsys, "--settings", text) == text
    off = Settings.from_string(_printed(capsys, "--settings", text, "--no-shuffle-master-sword"))
    assert off.shuffle_master_sword is False and off.logic == {FREE: True}
    assert Settings.from_string(_printed(capsys, "--settings", off.to_string(), "--shuffle-master-sword")) == ON


@pytest.mark.parametrize("shuffle", [["Gift"], ["Shop", "Scrub"]])
def test_cli_strings_and_settings_refuse_master_sword_without_shuffled_chests(capsys, shuffle):
    argv = ["--shuffle", *shuffle, "--shuffle-master-sword", "--logic", "free_time_travel=true", "--print-settings"]
    with pytest.raises(SystemExit) as refused:
        main(argv)
    assert refused.value.code == 2 and "Chest" in capsys.readouterr().err
    with pytest.raises(SystemExit) as replayed:
        main(["--settings", ON.to_string(), "--shuffle", *shuffle, "--print-settings"])
    assert replayed.value.code == 2 and "Chest" in capsys.readouterr().err
    with pytest.raises(ValueError, match="Chest"):
        Settings(shuffle=tuple(shuffle), shuffle_master_sword=True, logic={FREE: True})
    with pytest.raises(ValueError, match="invalid settings string"):
        Settings.from_string(_encode({"shuffle": shuffle, FIELD: True, "logic": {FREE: True}}))


@pytest.mark.parametrize("value", [1, "true", None])
def test_master_sword_shuffle_takes_only_a_boolean(value):
    with pytest.raises(ValueError, match="boolean"):
        Settings(shuffle_master_sword=value, logic={FREE: True})
    with pytest.raises(ValueError, match="must be a boolean"):
        validate({FIELD: value, FREE: True})
    with pytest.raises(ValueError, match="invalid settings string"):
        Settings.from_string(_encode({FIELD: value, "logic": {FREE: True}}))


@pytest.mark.parametrize("logic", [{}, {FREE: False}])
def test_app_and_generation_refuse_master_sword_without_free_time_travel(spec, capsys, logic):
    settings = Settings(shuffle_master_sword=True, logic=logic)  # constructible: the app switch may still add travel
    with pytest.raises(FillError, match=FREE):
        prepare(spec, settings)  # seed generation compiles every seed through prepare()
    with pytest.raises(ValueError, match=FREE):
        validate({FIELD: True, "logic": logic}, spec=spec)
    with pytest.raises(ValueError, match=FREE):
        validate(text=settings.to_string(), spec=spec)
    # --print-settings only encodes, as for every other generation-time check; the string is refused at generation.
    printed = _printed(capsys, "--shuffle-master-sword", *(["--logic", "free_time_travel=false"] if logic else []))
    assert Settings.from_string(printed) == settings


def test_app_refuses_the_switch_turned_off_with_master_sword_shuffle(spec):
    with pytest.raises(ValueError, match=FREE):
        validate({FIELD: True, FREE: False}, spec=spec)


def test_app_accepts_either_free_time_travel_route_and_replays(spec):
    by_switch = validate({FIELD: True, FREE: True}, spec=spec)
    by_logic = validate({FIELD: True, "logic": {FREE: True}}, spec=spec)
    assert by_switch == by_logic == ON
    payload = settings_payload(by_switch)
    assert payload["values"][FIELD] is True and payload["values"][FREE] is True
    assert FIELD not in payload["inactive"]
    assert payload["settings_string"] == ON.to_string()
    assert validate(payload["values"], spec=spec) == ON
    assert validate(text=payload["settings_string"], spec=spec) == ON


def test_app_marks_the_setting_inactive_and_refuses_it_without_chests(spec):
    inactive = settings_payload(Settings(shuffle=("Gift",)))["inactive"]
    assert inactive[FIELD] == "Shuffle chests to move the Master Sword."
    with pytest.raises(ValueError, match="Chest"):
        validate({"shuffle": ["Gift"], FIELD: True, FREE: True}, spec=spec)


def test_presets_keep_master_sword_shuffle_off(spec):
    assert all(preset["values"][FIELD] is False for preset in presets(spec=spec))


def test_sliced_world_without_pedestal_is_refused_at_validation(spec):
    with pytest.raises(ValueError, match="Temple of Time pedestal"):
        validate(
            {"areas": ["KokiriForest"], "goal": "True", FIELD: True, FREE: True},
            spec=spec,
        )
