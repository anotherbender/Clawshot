"""Player exclusions preserve stock, delivery restrictions and solo proofs; synthetic resources only."""

from collections import Counter
from dataclasses import replace

import pytest

from clawshot.__main__ import main
from clawshot.app.schema import validate
from clawshot.generate import FillError, Settings, from_placements, generate, play_note, prepare, spoiler
from clawshot.generate.exclusions import validate_exclusions
from clawshot.generate.fill import allowed
from clawshot.world.search import Search


def world_spec():
    return {
        "start": "Start",
        "goal": "Tool",
        "items": {"Tool": {}, "Coin": {"class": "normal"}, "Heart": {"class": "priority"}},
        "regions": [
            {
                "name": "Start",
                "area": "Village",
                "locations": {
                    "Early": {"rule": "True", "type": "Chest", "vanilla": "Tool"},
                    "Game": {"rule": "Tool", "type": "Chest", "vanilla": "Coin"},
                    "Prize": {"rule": "True", "type": "Chest", "vanilla": "Heart"},
                },
            }
        ],
    }


def test_excluded_checks_never_take_progression_and_stock_and_goal_survive():
    settings = Settings(excluded_locations=("Game", "Prize"))
    for number in range(12):
        seed = generate(world_spec(), number, settings, attempts=1)
        assert seed.placements["Early"] == "Tool", seed.placements
        assert Counter(seed.placements.values()) == Counter(("Tool", "Coin", "Heart"))
        search = Search(seed.world)
        search.collect_spheres(seed.placements)
        assert search.won()
        assert spoiler(seed)["excluded_locations"] == ["Game", "Prize"]
        note = play_note(seed)
        assert "## Excluded locations\n" in note and "- Game\n" in note and "- Prize\n" in note


def test_exclusion_string_is_canonical_and_replays_behavior():
    settings = Settings(excluded_locations=("Prize", "Game", "Game"))
    restored = Settings.from_string(settings.to_string())
    assert restored == Settings(excluded_locations=("Game", "Prize"))
    assert generate(world_spec(), 4, restored).placements == generate(world_spec(), 4, settings).placements
    assert Settings.from_string("CS1").excluded_locations == ()
    assert "excluded_locations" not in Settings().as_dict()


@pytest.mark.parametrize("names", ["Game", [None], 1])
def test_names_must_be_a_list_of_strings(names):
    with pytest.raises(ValueError, match="excluded_locations must be a list of names"):
        Settings(excluded_locations=names)


def test_unknown_name_is_refused_by_generator_and_app():
    settings = Settings(excluded_locations=("Gmae",))
    with pytest.raises(FillError, match="Unknown excluded locations.*Gmae"):
        generate(world_spec(), 1, settings)
    with pytest.raises(ValueError, match="Unknown excluded locations.*Gmae"):
        validate({"excluded_locations": ["Gmae"]}, spec=world_spec())


def test_impossible_count_is_refused_before_fill_with_a_clear_message():
    settings = Settings(excluded_locations=("Early", "Game", "Prize"))
    with pytest.raises(FillError, match="Excluded locations make this item pool impossible.*Tool"):
        generate(world_spec(), 1, settings)
    with pytest.raises(ValueError, match="Excluded locations make this item pool impossible"):
        validate({"excluded_locations": list(settings.excluded_locations)}, spec=world_spec())


def test_capacity_reserves_held_filler_instead_of_counting_unusable_junk():
    spec = world_spec()
    spec["regions"][0]["locations"]["Prize"]["type"] = "BossHeart"
    settings = Settings(
        shuffle=("Chest", "BossHeart"),
        excluded_locations=("Early", "Game"),
        location_type_items={"BossHeart": ("Coin", "Heart")},
        item_location_types={"Coin": ("BossHeart",), "Heart": ("BossHeart",)},
    )
    effective, world = prepare(spec, settings)
    with pytest.raises(FillError, match="Excluded locations make this item pool impossible"):
        validate_exclusions(world, effective)


def test_external_assignment_cannot_bypass_exclusion_or_existing_delivery_rules():
    spec = world_spec()
    spec["regions"][0]["locations"]["Game"]["excluded_items"] = ["Heart"]
    settings = Settings(excluded_locations=("Game",))
    effective, world = prepare(spec, settings)
    assert not allowed(world, effective, "Game", "Tool")
    assert not allowed(world, effective, "Game", "Heart")
    assert allowed(world, effective, "Game", "Coin")
    with pytest.raises(FillError, match="Game: may not hold 'Tool'"):
        from_placements(spec, 1, settings, {"Game": "Tool", "Early": "Coin", "Prize": "Heart"})


def test_unshuffled_progression_cannot_silently_ignore_an_exclusion():
    spec = world_spec()
    spec["regions"][0]["locations"]["Early"]["keep_vanilla"] = "synthetic native hold"
    with pytest.raises(FillError, match="Excluded locations still hold unshuffled progression.*Early"):
        generate(spec, 1, Settings(excluded_locations=("Early",)))
    # An unshuffled non-progression check is safe and stays listed, for reusable settings recipes.
    spec["regions"][0]["locations"]["Game"]["keep_vanilla"] = "synthetic native hold"
    seed = generate(spec, 1, Settings(excluded_locations=("Game",)))
    assert seed.placements["Game"] == "Coin"


def test_native_pool_override_is_used_by_capacity_validation():
    spec = world_spec()
    settings = Settings(excluded_locations=("Game", "Prize"))
    with pytest.raises(FillError, match="Excluded locations make this item pool impossible"):
        generate(spec, 1, settings, vanilla={"Prize": "Tool"})


def test_cli_checks_unknown_names_and_can_clear_a_replayed_list(capsys):
    with pytest.raises(SystemExit) as error:
        main(["--exclude-locations", "not a location", "--print-settings"])
    assert error.value.code == 2
    assert "Unknown excluded locations" in capsys.readouterr().err
    text = Settings(excluded_locations=("not a location",)).to_string()
    assert main(["--settings", text, "--exclude-locations", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).excluded_locations == ()


def test_app_custom_world_and_string_replay_keep_the_exclusion_contract():
    settings = validate({"excluded_locations": ["Game"]}, spec=world_spec())
    replay = validate(text=settings.to_string(), spec=world_spec())
    assert generate(world_spec(), 2, replay).placements["Game"] != "Tool"
    assert replace(replay, excluded_locations=()).to_string() == "CS1"


def test_exclusions_cannot_spend_the_return_kits_only_adult_destinations():
    spec = world_spec()
    spec["settings"] = {
        "starting_age": "child",
        "age_return_event": "Forest Clear",
        "age_return_region": "Field",
        "age_pull_event": "Time Travel",
        "age_return_guarantee": True,
        "age_return_fill_families": ["Tool"],
        "age_return_fill_inventory": {},
    }
    spec["start"] = "Root"
    spec["goal"] = "'Forest Clear'"
    field = spec["regions"][0]
    field["name"] = "Field"
    field["events"] = {"Time Travel": "age == 'child'", "Forest Clear": "age == 'adult' and Tool"}
    field["locations"]["Early"]["rule"] = "age == 'child'"
    field["locations"]["Game"]["rule"] = "age == 'adult'"
    field["locations"]["Prize"]["rule"] = "age == 'adult'"
    spec["regions"].insert(0, {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}})
    settings = Settings(excluded_locations=("Game", "Prize"))
    # Globally enough junk, but the sole progression slot is child-only. No weakened return guarantee.
    with pytest.raises(FillError, match="Excluded locations make this item pool impossible.*Tool"):
        generate(spec, 1, settings)


def test_house100_progression_opt_in_does_not_override_a_player_exclusion():
    spec = world_spec()
    check = spec["regions"][0]["locations"].pop("Game")
    check.update(type="NPC", nonprogression_only=True)
    house = "Kak 100 Gold Skulltula Reward"
    spec["regions"][0]["locations"][house] = check
    settings = Settings(shuffle=("Chest", "NPC"), shuffle_100_token_reward=True, excluded_locations=(house,))
    with pytest.raises(FillError, match="Kak 100 Gold Skulltula Reward: may not hold 'Tool'"):
        from_placements(spec, 1, settings, {"Early": "Coin", "Prize": "Heart", house: "Tool"})
