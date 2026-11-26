"""Reported pickup and native distance-switch false reachability."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def starting_at(region, age, **settings):
    spec = load_spec()
    spec["settings"]["starting_age"] = age
    spec["settings"].update(settings)
    spec["start"] = "Pickup Audit Start"
    spec["regions"].append({"name": "Pickup Audit Start", "exits": {region: "is_starting_age"}})
    return build_world(spec)


@pytest.mark.parametrize("items", [["Boomerang"], ["Boomerang", "Dampes Windmill Access"]])
def test_child_boomerang_or_adult_arrival_history_cannot_collect_windmill_pickup(items):
    world = starting_at("Kak Windmill", CHILD)
    search = Search(world, items)
    assert search.can_reach("Kak Windmill", CHILD)
    assert not search.can_access(world.locations["Kak Windmill Freestanding PoH"], CHILD)


def test_windmill_pickup_keeps_adult_dampe_hookshot_approach():
    world = starting_at("Graveyard", ADULT)
    search = Search(world)
    pickup = world.locations["Kak Windmill Freestanding PoH"]
    assert not search.can_access(pickup, ADULT)
    search.collect("Hookshot")
    assert search.holds("Dampes Windmill Access")
    assert search.can_access(pickup, ADULT)


def test_adult_windmill_floor_alone_does_not_supply_the_upper_platform():
    world = starting_at("Kak Windmill", ADULT)
    assert not Search(world).can_access(world.locations["Kak Windmill Freestanding PoH"], ADULT)


def test_graveyard_heart_keeps_longshot_ledge_route_not_child_boomerang():
    child = starting_at("Graveyard", CHILD)
    assert not Search(child, ["Boomerang"]).can_access(child.locations["Graveyard Freestanding PoH"], CHILD)
    adult = starting_at("Graveyard", ADULT)
    search = Search(adult, ["Hookshot"])
    pickup = adult.locations["Graveyard Freestanding PoH"]
    assert not search.can_access(pickup, ADULT)
    search.collect("Longshot")
    assert search.can_access(pickup, ADULT)


def test_cow_shed_pickup_keeps_its_separate_rooftop_route():
    world = starting_at("Kakariko Village", ADULT)
    pickup = world.locations["Kak Impas House Freestanding PoH"]
    search = Search(world)
    assert not search.can_access(pickup, ADULT)
    search.collect("Hookshot")
    assert search.can_access(pickup, ADULT)


@pytest.mark.parametrize(
    ("age", "items", "reachable"),
    [
        (ADULT, [], False),
        (ADULT, ["Bow"], True),
        (ADULT, ["Deku Stick Drop"], False),
        (ADULT, ["Dins Fire", "Magic Meter"], True),
        (ADULT, ["Fire Arrows", "Bow", "Magic Meter"], True),
        (CHILD, ["Goron Bracelet", "Deku Stick Drop"], True),
        (CHILD, ["Goron Bracelet", "Slingshot", "Bow"], False),
    ],
)
def test_dodongo_torch_exit_needs_fire_or_played_plain_adult_arrows(age, items, reachable):
    world = starting_at("Dodongos Cavern Lobby", age)
    search = Search(world, items)
    assert search.can_reach("Dodongos Cavern Torch Room", age)
    assert search.can_reach("Dodongos Cavern Staircase Room", age) is reachable


def test_dodongo_plain_arrows_light_the_candles_without_a_shuffled_sword():
    world = starting_at("Dodongos Cavern Lobby", ADULT, shuffle_master_sword=True)
    search = Search(world, ["Bow"])
    assert search.can_reach("Dodongos Cavern Torch Room", ADULT)
    assert search.can_reach("Dodongos Cavern Staircase Room", ADULT)


@pytest.mark.parametrize(
    ("age", "items", "reachable"),
    [
        (ADULT, [], False),
        (ADULT, ["Hookshot"], True),
        (ADULT, ["Longshot"], True),
        (CHILD, ["Hookshot"], False),
    ],
)
def test_dodongo_scarecrow_token_accepts_played_plain_hookshot_route(age, items, reachable):
    world = starting_at("Dodongos Cavern Lower Right Side", age)
    search = Search(world, items)
    assert search.can_access(world.locations["Dodongos Cavern GS Scarecrow"], age) is reachable
