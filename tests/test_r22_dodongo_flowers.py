"""Adult Bracelet + ordinary Bow reaches the bag without inventory explosives or a sword."""

import pytest

from clawshot.generate import Settings, prepare
from clawshot.world import ADULT, CHILD, Search, load_spec

PRE_BAG_CHESTS = (
    "Dodongos Cavern Map Chest",
    "Dodongo Cavern Room 1 Chest (TBox_Rupee_Blue)",
    "Dodongo Cavern Room 5 Chest (TBox_Rupee_Red)",
    "Dodongos Cavern Compass Chest",
    "Dodongos Cavern Bomb Flower Platform Chest",
    "Dodongo Cavern Room 16 Chest (Item_ScrubBusinessSeed)",
    "Dodongos Cavern Bomb Bag Chest",
)


@pytest.fixture(scope="module")
def world():
    spec = load_spec()
    spec["start"] = "Dodongos Cavern Beginning"
    return prepare(spec, Settings(shuffle_master_sword=True, logic={"free_time_travel": True}))[1]


@pytest.mark.parametrize("strength", ["Goron Bracelet", "Progressive Strength"])
def test_adult_flowers_and_plain_arrows_reach_the_bag_without_bag_or_sword(world, strength):
    search = Search.adult_after_pull(world, [strength, "Progressive Quiver"])
    for name in PRE_BAG_CHESTS:
        assert search.can_access(world.locations[name], ADULT), name
    assert not search.holds("Bomb Bag")
    assert not search.holds("Master Sword")
    assert not search.can_reach("Dodongos Cavern Far Bridge", ADULT)
    assert not search.can_access(world.locations["Dodongo Cavern Room 10 Chest (Item_ScrubBusinessSeed)"], ADULT)
    assert not search.holds("Defeat King Dodongo")


def test_bracelet_without_a_candle_method_or_eye_weapon_does_not_reach_the_bag(world):
    search = Search.adult_after_pull(world, ["Goron Bracelet"])
    assert search.can_access(world.locations["Dodongos Cavern Map Chest"], ADULT)
    assert not search.can_reach("Dodongos Cavern Staircase Room", ADULT)
    assert not search.can_access(world.locations["Dodongos Cavern Bomb Bag Chest"], ADULT)


def test_capacity_without_lift_cannot_open_the_initial_flower_wall(world):
    assert not Search.adult_after_pull(world, ["Progressive Bomb Bag", "Progressive Quiver"]).can_reach(
        "Dodongos Cavern Lobby", ADULT
    )


def test_child_bow_is_not_an_adult_candle_or_eye_method(world):
    search = Search.child_only(world, ["Goron Bracelet", "Progressive Quiver"])
    assert not search.can_access(world.locations["Dodongos Cavern Bomb Bag Chest"], CHILD)


def test_hammer_opens_the_lower_right_wall_but_not_the_unplayed_flower_chain():
    spec = load_spec()
    spec["start"] = "Dodongos Cavern Lobby"
    _, world = prepare(spec, Settings())
    search = Search.adult_after_pull(world, ["Megaton Hammer"])
    assert search.can_reach("Dodongos Cavern Lower Right Side", ADULT)
    spec["start"] = "Dodongos Cavern Staircase Room"
    _, world = prepare(spec, Settings())
    assert not Search.adult_after_pull(world, ["Megaton Hammer"]).can_reach("Dodongos Cavern Climb", ADULT)
