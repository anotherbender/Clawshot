"""The 100-token reward opt-in (issue #12) through its real consumers: CS1, the CLI and the app's form/HTTP API."""

import base64
import json
import zlib

import pytest
from test_app import synthetic_run, synthetic_spec
from test_ui import request, running_server

from clawshot.__main__ import main
from clawshot.app import Jobs, schema, settings_payload, validate
from clawshot.generate import Settings
from clawshot.patch.gifts import GIFT_TYPES
from clawshot.ui.server import Application

KEY = "shuffle_100_token_reward"
OPTED = Settings(shuffle=("Chest", "Gift"), shuffle_100_token_reward=True)


def cs1(payload: dict) -> str:
    """A settings string as a client encodes it, independent of ``Settings.to_string``."""
    data = zlib.compress(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(), 9)
    return "CS1." + base64.urlsafe_b64encode(data).decode().rstrip("=")


def test_strings_without_the_field_decode_off_and_keep_their_bytes():
    assert Settings.from_string("CS1").shuffle_100_token_reward is False
    older = cs1({"shuffle": ["Chest", "Gift"]})
    decoded = Settings.from_string(older)
    assert decoded.shuffle_100_token_reward is False
    assert decoded.to_string() == older


@pytest.mark.parametrize("shuffle", [("Chest", "Gift"), ("Chest", *GIFT_TYPES), ("NPC",)])
def test_opt_in_round_trips_with_gift_or_its_expanded_npc(shuffle):
    settings = Settings(shuffle=shuffle, shuffle_100_token_reward=True)
    text = settings.to_string()
    restored = Settings.from_string(text)
    assert restored == settings and restored.shuffle_100_token_reward is True
    assert restored.to_string() == text
    assert Settings.from_string(cs1({"shuffle": list(shuffle), KEY: True})) == settings


@pytest.mark.parametrize("shuffle", [("Chest",), ("Chest", "Token"), ("Chest", "Song", "Cutscene", "Boss"), ()])
def test_opt_in_without_gift_shuffle_is_refused(shuffle):
    with pytest.raises(ValueError, match="shuffle Gift"):
        Settings(shuffle=shuffle, shuffle_100_token_reward=True)
    with pytest.raises(ValueError, match="shuffle Gift"):
        Settings.from_string(cs1({"shuffle": list(shuffle), KEY: True}))


@pytest.mark.parametrize("value", [1, 0, "true", None])
def test_only_a_boolean_is_accepted(value):
    with pytest.raises(ValueError, match="must be a boolean"):
        Settings(shuffle=("Chest", "Gift"), shuffle_100_token_reward=value)
    with pytest.raises(ValueError, match="must be a boolean"):
        Settings.from_string(cs1({"shuffle": ["Chest", "Gift"], KEY: value}))
    with pytest.raises(ValueError, match="must be a boolean"):
        validate({"shuffle": ["Chest", "Gift"], KEY: value})


def test_cli_flag_sets_it_and_explicit_off_overrides_a_string(capsys):
    assert main(["--shuffle", "Chest", "Gift", "--shuffle-100-token-reward", "--print-settings"]) == 0
    text = capsys.readouterr().out.strip()
    assert text == OPTED.to_string()
    assert main(["--settings", text, "--print-settings"]) == 0
    assert capsys.readouterr().out.strip() == text
    assert main(["--settings", text, "--no-shuffle-100-token-reward", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()) == Settings(shuffle=("Chest", "Gift"))


@pytest.mark.parametrize(
    "argv",
    [
        ["--shuffle-100-token-reward"],  # default shuffle is Chest only
        ["--settings", OPTED.to_string(), "--shuffle", "Chest"],  # dropping Gift from a string that opted in
    ],
)
def test_cli_refuses_the_opt_in_without_gift(argv, capsys):
    with pytest.raises(SystemExit) as exited:
        main([*argv, "--print-settings"])
    assert exited.value.code == 2
    assert "shuffle Gift" in capsys.readouterr().err


def test_app_switch_is_inactive_until_gift_is_shuffled():
    row = next(row for row in schema() if row["key"] == KEY)
    assert (row["kind"], row["group"], row["default"]) == ("boolean", "Items", False)
    assert KEY in settings_payload(Settings())["inactive"]
    assert KEY not in settings_payload(Settings(shuffle=("Chest", "Gift")))["inactive"]


def test_app_form_replay_and_effective_string_match_the_cli(capsys):
    assert main(["--shuffle", "Chest", "Gift", "--shuffle-100-token-reward", "--print-settings"]) == 0
    text = capsys.readouterr().out.strip()
    chosen = validate({"shuffle": ["Chest", "Gift"], KEY: True})
    assert chosen.to_string() == text
    payload = settings_payload(chosen)
    assert payload["values"][KEY] is True and validate(payload["values"]) == chosen
    effective = Settings(shuffle=("Chest", *GIFT_TYPES), shuffle_100_token_reward=True)
    assert validate(text=effective.to_string()) == chosen
    with pytest.raises(ValueError, match="shuffle Gift"):
        validate(payload["values"] | {"shuffle": ["Chest"]})


def test_http_settings_route_keeps_presets_off_and_refuses_the_opt_in_without_gift():
    with running_server(Application(Jobs(synthetic_run), spec=synthetic_spec())) as server:
        status, _, config = request(server, "schema")
        assert status == 200 and config["values"][KEY] is False  # the Recommended preset
        assert all(preset["values"][KEY] is False for preset in config["presets"])
        status, _, chosen = request(server, "settings", {"values": {"shuffle": ["Chest", "Gift"], KEY: True}})
        assert status == 200 and chosen["values"][KEY] is True and KEY not in chosen["inactive"]
        assert Settings.from_string(chosen["settings_string"]).shuffle_100_token_reward is True
        replay = request(server, "settings", {"settings_string": chosen["settings_string"]})[2]
        assert replay["values"] == chosen["values"]
        status, _, refused = request(server, "settings", {"values": {"shuffle": ["Chest"], KEY: True}})
        assert status == 400 and "shuffle Gift" in refused["error"]
