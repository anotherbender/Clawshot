"""The opt-in bomb lift patch changes bomb use, not bag ownership or Bomb Flower strength."""

import pytest

from clawshot.__main__ import main
from clawshot.app.schema import settings_payload, validate
from clawshot.generate import Settings
from clawshot.world import ADULT, CHILD, Search, build_world, load_spec

OPTION = "bombs_without_bracelet"
ROUTES = {
    "Bomb wall": "Bombs",
    "Bomb item": "can_use(Bombs)",
    "Explosives": "has_explosives",
    "Rock": "can_blast_or_smash",
    "Octorok": "can_kill_octorok_with_bombs",
    "Flower": "Progressive_Strength_Upgrade",
}


def option_world(enabled):
    spec = load_spec()
    spec.update(
        start="Room",
        goal="True",
        regions=[{"name": "Room", "locations": ROUTES}],
        locations={name: {"type": "Chest"} for name in ROUTES},
    )
    return build_world(spec, {OPTION: enabled})


@pytest.mark.parametrize("age", [CHILD, ADULT])
@pytest.mark.parametrize("enabled", [False, True])
def test_only_bag_bombs_lose_strength_requirement(enabled, age):
    world = option_world(enabled)
    bag = Search(world, ["Bomb Bag"])
    empty = Search(world)
    for name in ROUTES:
        assert not empty.can_access(world.locations[name], age), name
        assert bag.can_access(world.locations[name], age) is (enabled and name != "Flower"), name
    bag.collect("Goron Bracelet")
    assert all(bag.can_access(world.locations[name], age) for name in ROUTES)


@pytest.mark.parametrize("enabled", [False, True])
def test_bombchu_supply_does_not_inherit_bomb_strength_option(enabled):
    world = option_world(enabled)
    chus = Search(world, ["Bomb Bag", "Bombchus (5)"])
    for age in (CHILD, ADULT):
        assert chus.can_access(world.locations["Explosives"], age)
        assert not chus.can_access(world.locations["Flower"], age)


@pytest.mark.parametrize("enabled", [False, True])
def test_cli_and_app_replay_the_same_selected_bomb_capability(enabled, capsys):
    assert main(["--logic", f"{OPTION}={str(enabled).lower()}", "--print-settings"]) == 0
    text = capsys.readouterr().out.strip()
    imported = validate(text=text)
    values = settings_payload(imported)["values"]
    assert values[OPTION] is enabled
    assert validate(values).to_string() == text
    selected = validate({OPTION: enabled})
    assert selected.logic.get(OPTION, False) is enabled
    assert Settings.from_string(selected.to_string()) == selected
    world = option_world(values[OPTION])
    assert Search(world, ["Bomb Bag"]).can_access(world.locations["Bomb wall"], CHILD) is enabled


@pytest.mark.parametrize("value", [1, "true", None])
def test_bomb_option_refuses_non_booleans(value):
    with pytest.raises(ValueError, match="must be a boolean"):
        validate({OPTION: value})
    with pytest.raises(ValueError, match="isn't supported"):
        validate({"logic": {OPTION: value}})
