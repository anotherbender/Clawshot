"""Settings metadata is a checked contract, not a second set of generator defaults."""

from dataclasses import make_dataclass
from importlib import import_module

import pytest

from clawshot.__main__ import main
from clawshot.app import schema, settings_payload, validate
from clawshot.generate import Settings, generate, prepare
from clawshot.patch.gifts import GIFT_TYPES
from clawshot.world import Search, load_spec

schema_module = import_module("clawshot.app.schema")
FREE = "free_time_travel"
# Chest only, with the default adult-return guarantee: fill.return_guarantee_conflict's refusal.
REFUSED_EARLY_DOORS = {("song_only", False), ("open", False)}


def use_metadata(tmp_path, monkeypatch, section, key, line=None):
    """Load a copy of the app metadata without ``key`` in ``section``, with ``line`` added there if given."""
    current = ""
    lines = []
    for row in schema_module.METADATA_PATH.read_text(encoding="utf-8").splitlines():
        if row.startswith("["):
            current = row.strip("[]")
        if current == section and row.startswith(key + " ="):
            continue
        lines.append(row)
        if line is not None and row == f"[{section}]":
            lines.append(line)
    path = tmp_path / "settings.toml"
    path.write_text("\n".join(lines), encoding="utf-8")
    monkeypatch.setattr(schema_module, "METADATA_PATH", path)


def test_new_setting_without_metadata_refuses_schema(monkeypatch):
    expanded = make_dataclass("ExpandedSettings", [("future_setting", bool, False)], bases=(Settings,), frozen=True)
    monkeypatch.setattr(schema_module, "Settings", expanded)
    with pytest.raises(ValueError):
        schema()


@pytest.mark.parametrize("section, key", [("shuffle", "help"), ("shuffle.choice_help", "Chest")])
def test_missing_setting_or_choice_help_refuses_schema(tmp_path, monkeypatch, section, key):
    use_metadata(tmp_path, monkeypatch, section, key)
    with pytest.raises(ValueError):
        schema()


def test_effective_gift_string_can_be_loaded_back_into_player_controls():
    effective = Settings(shuffle=("Chest", *GIFT_TYPES))
    restored = validate(text=effective.to_string())
    assert restored.shuffle == ("Chest", "Gift")
    assert validate(text=restored.to_string()) == restored


def test_inactive_prices_keep_their_values_and_activate_only_with_their_check_kind():
    inactive = Settings(shuffle=("Chest",), shop_prices="affordable", scrub_prices="fixed", scrub_price=75)
    payload = settings_payload(inactive)
    assert {"shop_slots", "shop_prices", "scrub_prices", "scrub_price"} <= payload["inactive"].keys()
    assert "cheap_deku_shield" not in payload["inactive"]  # independent price patch even without Shop
    replay = Settings.from_string(payload["settings_string"])
    assert replay.scrub_price == 75 and replay.shop_prices == "affordable"
    active = validate(payload["values"] | {"shuffle": ["Chest", "Shop", "Scrub"]})  # form values, as the UI posts
    assert (
        not {"shop_slots", "shop_prices", "scrub_prices", "scrub_price"} & settings_payload(active)["inactive"].keys()
    )
    assert active.scrub_price == 75


def test_fixed_fee_and_zero_shop_shelves_explain_why_prices_have_no_effect():
    selected = Settings(shuffle=("Chest", "Shop", "Scrub"), shop_slots=0, scrub_prices="vanilla")
    inactive = settings_payload(selected)["inactive"]
    assert {"shop_prices", "scrub_price"} <= inactive.keys()
    assert not {"shop_slots", "scrub_prices"} & inactive.keys()


@pytest.mark.parametrize(
    "section, line",
    [
        (FREE, 'logic_override = "open_forest"'),  # supported, but not a boolean
        (FREE, 'logic_override = "open_door_of_time"'),  # OoT-only: no paired game change
        (FREE, 'kind = "choice"'),
        ("cheap_deku_shield", f'logic_override = "{FREE}"'),  # a Settings field cannot also be a switch
    ],
)
def test_switch_metadata_must_present_one_supported_boolean_override(tmp_path, monkeypatch, section, line):
    use_metadata(tmp_path, monkeypatch, section, line.split(" =")[0], line)
    with pytest.raises(ValueError):
        schema()


def test_switch_writes_the_same_settings_string_as_the_cli_override(capsys):
    assert main(["--logic", "free_time_travel=true", "--print-settings"]) == 0
    on = capsys.readouterr().out.strip()
    assert main(["--print-settings"]) == 0
    off = capsys.readouterr().out.strip()
    assert validate({FREE: True}).to_string() == on == Settings(logic={FREE: True}).to_string()
    assert validate({FREE: False}).to_string() == off == "CS1"
    assert validate({FREE: True}) == validate({"logic": {FREE: True}})  # the logic route keeps working


@pytest.mark.parametrize(
    "logic, on",
    [
        (["free_time_travel=true"], True),
        (["free_time_travel=true", "age_return_guarantee=false"], True),
        (["age_return_guarantee=false"], False),
        ([], False),
    ],
)
def test_imported_cli_settings_populate_the_switch_and_replay_unchanged(logic, on, capsys):
    assert main([*(["--logic", *logic] if logic else []), "--print-settings"]) == 0
    text = capsys.readouterr().out.strip()
    payload = settings_payload(validate(text=text))
    assert payload["settings_string"] == text
    assert payload["values"][FREE] is on
    assert payload["values"]["logic"] == Settings.from_string(text).logic
    replay = validate(payload["values"])  # the form posts its values back
    assert replay == Settings.from_string(text) and replay.to_string() == text


def test_explicit_cli_false_survives_form_replay(capsys):
    assert main(["--logic", "free_time_travel=false", "--print-settings"]) == 0
    text = capsys.readouterr().out.strip()
    assert text != "CS1"  # the CLI keeps the explicit value in its string
    payload = settings_payload(validate(text=text))
    assert payload["settings_string"] == text and payload["values"][FREE] is False
    assert validate(payload["values"]).to_string() == text
    assert validate(payload["values"] | {"shop_slots": 3}).logic == {FREE: False}


def test_effective_spoiler_string_restores_the_switch():
    effective, _ = prepare(load_spec(), Settings(door_of_time="song_only", logic={FREE: True}))
    payload = settings_payload(validate(text=effective.to_string()))
    assert payload["values"][FREE] is True
    assert validate(payload["values"]).logic == effective.logic


def test_switch_sets_or_clears_only_its_own_override():
    kept = {"age_return_guarantee": False}
    on = validate({FREE: True, "logic": kept})
    assert on.logic == kept | {FREE: True}
    values = settings_payload(on)["values"]
    assert values["logic"] == kept | {FREE: True} and values[FREE] is True
    # Changing the switch uses its clears metadata, just like the forest/door selectors.
    off = validate(values | {FREE: False, "logic": kept})
    assert off.logic == kept and off.to_string() == Settings(logic=kept).to_string()


@pytest.mark.parametrize("switch", [False, True])
@pytest.mark.parametrize("typed", [False, True])
def test_explicit_logic_override_resynchronizes_the_switch(switch, typed):
    settings = validate({FREE: switch, "logic": {FREE: typed}})
    payload = settings_payload(settings)
    assert settings.logic == {FREE: typed}
    assert payload["values"][FREE] is typed
    assert validate(payload["values"]).to_string() == settings.to_string()


@pytest.mark.parametrize("value", [1, "true", None])
def test_switch_takes_only_a_boolean(value):
    with pytest.raises(ValueError, match="must be a boolean"):
        validate({FREE: value})


@pytest.mark.parametrize("free", [False, True])
@pytest.mark.parametrize("mode", ["closed", "song_only", "open"])
def test_every_door_mode_with_the_switch_generates_or_gets_the_return_refusal(mode, free):
    values = {"door_of_time": mode, FREE: free}
    if (mode, free) in REFUSED_EARLY_DOORS:
        refusal = rf"door_of_time = '{mode}' .*age_return_guarantee.*door_of_time = 'closed'"
        with pytest.raises(ValueError, match=refusal):
            validate(values)
        return
    settings = validate(values)
    assert settings == Settings(door_of_time=mode, logic={FREE: True} if free else {})
    result = generate(load_spec(), 1, settings)  # fill, then the beatability search
    assert (result.world.age_return is None) is free  # free travel replaces the Forest-gated return
    search = Search(result.world)
    search.collect_spheres(result.placements)
    assert search.won()
