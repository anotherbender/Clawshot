"""Native dropped-stick age gate: an adult weapon cannot supply child sticks through shared inventory."""

import pytest

from clawshot.generate import Settings
from clawshot.patch.logic_world import logic_world
from clawshot.world import Search, load_world
from clawshot.world.rules import ADULT, CHILD, DAY


@pytest.mark.parametrize("shuffled_sword", [False, True])
def test_every_stick_drop_event_rejects_the_adult_even_with_all_weapons(shuffled_sword):
    world = load_world({"shuffle_master_sword": shuffled_sword})
    counts = dict.fromkeys(world.items, 9)
    events = [event for event in world.events if event.name == "Deku Stick Drop"]
    assert events
    for event in events:
        assert not event.rule(counts, ADULT, DAY), event.region


def test_child_baba_stick_sources_need_the_kokiri_sword_not_an_unproven_boomerang_yield():
    world = load_world()
    regions = {"KF Outside Deku Tree", "Deku Tree Lobby", "Forest Temple NW Outdoors", "Forest Temple NE Outdoors"}
    for event in world.events:
        if event.name == "Deku Stick Drop" and event.region in regions:
            assert not event.rule({}, CHILD, DAY), event.region
            assert event.rule({"Kokiri Sword": 1}, CHILD, DAY), event.region
            assert not event.rule({"Boomerang": 1}, CHILD, DAY), event.region


def test_early_adult_sword_no_longer_arms_weaponless_child_skulltulas():
    _, world = logic_world(
        Settings(
            forest="open",
            door_of_time="open",
            shuffle_master_sword=True,
            logic={"free_time_travel": True},
        )
    )
    search = Search(world, ["Met Child Zelda", "Master Sword"])
    assert search.can_reach("KF Outside Deku Tree", ADULT)
    assert not search.inventory(CHILD).get("Deku Stick Drop")
    targets = ("HF GS Lone Tree", "LLR GS Tree", "Market GS Guard House", "HC GS Tree")
    for name in targets:
        assert not search.can_access(world.locations[name], CHILD), name
    search.collect("Buy Deku Stick (1)")
    for name in targets:
        assert search.can_access(world.locations[name], CHILD), name


@pytest.mark.parametrize("weapon", ["Master Sword", "Bow", "Bombchus (5)"])
def test_nut_sources_accept_real_adult_kills_without_an_assumed_sword(weapon):
    world = load_world({"shuffle_master_sword": True})
    inventory = Search(world, [weapon, "Bomb Bag"]).inventory(ADULT)
    for event in world.events:
        if event.name == "Deku Nut Drop" and event.rule.text != "False":
            assert not event.rule({}, ADULT, DAY), event.region
            assert event.rule(inventory, ADULT, DAY), (event.region, weapon)
