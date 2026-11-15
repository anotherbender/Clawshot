"""The three remake-only token routes: sourced identity, retrieval, clock and cross-age history.

The small temporal harness uses the real loaded route rules/events and helpers, with controlled
pull/return/clock gates. It does not certify the still-unplayed native routes or enable Token fill.
"""

import tomllib

import pytest

from clawshot.census.definitions import load as load_definitions
from clawshot.world import ADULT, CHILD, DATA_DIR, Search, build_world, load_spec, load_world
from clawshot.world.load import apply_overrides
from clawshot.world.rules import DAY, NIGHT

LONE = "HF GS Lone Tree"
TOWER = "LLR GS Tower"
WETLAND = "HF GS Wetland Grotto Crate"
GROTTO = "HF Wetland Grotto"
KILL = "HF Wetland Skullwalltula Defeated"
IDENTITIES = {LONE: 2177746409373494991, TOWER: 2730878115209290675, WETLAND: 9047381233010434881}
PERMITS = ["Route Clock Permit", "Route Pull Permit", "Route Return Permit"]
GEAR = ["Boomerang", "Hookshot", "Bomb Bag", "Goron Bracelet", *PERMITS[:2]]


def pending_spec():
    spec = load_spec()
    path = DATA_DIR / "remake" / "pending" / "token_routes.toml"
    with path.open("rb") as file:
        apply_overrides(spec, [("remake/pending/token_routes.toml", tomllib.load(file))])
    return spec


def route_world(*, adult_start=False, free_travel=False, adult_bombs=False):
    spec = pending_spec()
    spec["start"] = "Route Root"
    spec["settings"].update(
        starting_age="adult" if adult_start else "child",
        free_time_travel=free_travel,
        age_return_region="Route Root",
    )
    spec["items"].update({name: {} for name in PERMITS})
    # Keep the actual route/region rules. Isolate unrelated story routes so an adult's
    # test inventory cannot clear Forest or obtain child explosives through another check.
    for region in spec["regions"]:
        if region["name"] == "Hyrule Field":
            region["exits"] = {GROTTO: region["exits"][GROTTO]}
            region["events"] = {}
        elif region["name"] == "Lon Lon Ranch":
            region["exits"] = {}
            region["events"] = {}
    spec["regions"].append(
        {
            "name": "Route Root",
            "exits": {name: "is_starting_age or Time_Travel" for name in ("Hyrule Field", "Lon Lon Ranch")},
            "events": {
                "Time Flows": "'Route Clock Permit'",
                "Time Travel": "'Route Pull Permit'",
                "Defeat Phantom Ganon": "is_adult and 'Route Return Permit'",
            },
            "locations": {"Route Adult Bomb Bag": {"rule": "is_adult", "type": "Chest", "vanilla": "Bomb Bag"}}
            if adult_bombs
            else {},
        }
    )
    return build_world(spec)


def test_all_100_native_definitions_have_one_live_world_check():
    world = build_world(pending_spec())
    definitions = [d for d in load_definitions() if d.kind == "gold_skulltula"]
    linked = {d.oot_randomizer_name or d.name: d for d in definitions}
    live = {name for name, loc in world.locations.items() if loc.type == "GS Token" and not loc.n64_only}
    assert len(linked) == len(definitions) == 100
    assert set(linked) == live
    for name, source in IDENTITIES.items():
        assert linked[name].id == source
        assert linked[name].area == world.locations[name].area == "HyruleField"
        assert world.locations[name].vanilla == "Gold Skulltula Token"
    for name in ("HF GS Cow Grotto", "LLR GS Rain Shed", "LLR GS Back Wall"):
        assert world.locations[name].n64_only
    # Existing ranch-tree age policy is not relaxed by its native adult placement.
    assert not world.locations["LLR GS Tree"].rule({}, ADULT, NIGHT)


def test_unplayed_routes_are_not_loaded_into_the_production_world():
    current = load_world()
    assert set(IDENTITIES).isdisjoint(current.locations)
    assert sum(loc.type == "GS Token" and not loc.n64_only for loc in current.locations.values()) == 97


@pytest.mark.parametrize("name,weapon", [(LONE, "Kokiri Sword"), (TOWER, "Boomerang")])
def test_child_night_still_needs_the_story_clock_when_tod_is_folded(name, weapon):
    world = route_world()
    search = Search(world, [weapon])
    assert not search.can_access(world.locations[name], CHILD)
    search.collect("Route Clock Permit")
    assert search.can_access(world.locations[name], CHILD)


def test_lone_tree_requires_attack_roll_and_conservative_night():
    world = build_world(pending_spec(), {"ensure_tod_access": True, "deadly_bonks": "ohko"})
    rule = world.locations[LONE].rule
    child = {"Kokiri Sword": 1, "Time Flows": 1}
    assert not rule(child, CHILD, NIGHT)  # OHKO bonk without protection
    protection = {"Fairy": 1, "Bottle": 1}
    assert rule(child | protection, CHILD, NIGHT)
    assert not rule(child | protection, CHILD, DAY)
    assert not rule({"Time Flows": 1} | protection, CHILD, NIGHT)  # no way to kill
    assert rule(protection, ADULT, NIGHT)
    assert not rule(protection, ADULT, DAY)


@pytest.mark.parametrize(
    "age,gear,expected",
    [
        (CHILD, ["Boomerang"], True),
        (CHILD, ["Slingshot"], False),
        (CHILD, ["Hookshot"], False),
        (ADULT, ["Hookshot"], True),
        (ADULT, ["Longshot"], True),
        (ADULT, ["Boomerang"], False),
        (ADULT, ["Bow"], False),
    ],
)
def test_tower_requires_age_appropriate_high_reward_retrieval(age, gear, expected):
    world = build_world(pending_spec(), {"ensure_tod_access": True})
    counts = Search(world, gear).counts | {"Time Flows": 1}
    rule = world.locations[TOWER].rule
    assert rule(counts, age, NIGHT) is expected
    assert not rule(counts, age, DAY)


def test_wetlands_bag_without_child_lift_and_hammer_alone_cannot_open_the_route():
    world = route_world()
    search = Search(world, ["Bomb Bag", "Slingshot"])
    assert not search.can_reach(GROTTO, CHILD)
    assert not search.holds(KILL)
    search.collect("Goron Bracelet")
    assert search.can_reach(GROTTO, CHILD)
    assert search.holds(KILL)
    assert not search.can_access(world.locations[WETLAND], CHILD)
    hammer = Search(route_world(adult_start=True), ["Megaton Hammer"])
    assert not hammer.can_reach(GROTTO, ADULT)


def test_adult_inventory_does_not_replace_the_earlier_child_kill():
    world = route_world(adult_start=True)
    search = Search(world, GEAR)
    assert search.can_reach(GROTTO, ADULT)
    assert not search.can_reach(GROTTO, CHILD)
    assert not search.holds(KILL)
    assert not search.can_access(world.locations[WETLAND], ADULT)
    search.collect("Route Return Permit")
    assert search.holds(KILL)
    assert search.can_access(world.locations[WETLAND], ADULT)


@pytest.mark.parametrize("free_travel", [False, True])
def test_adult_found_explosives_need_real_child_return_before_the_crate(free_travel):
    world = route_world(free_travel=free_travel, adult_bombs=True)
    search = Search(world, [item for item in GEAR if item != "Bomb Bag"])
    placements = {"Route Adult Bomb Bag": "Bomb Bag", WETLAND: "Gold Skulltula Token"}
    search.collect_spheres(placements)
    assert search.counts["Bomb Bag"] == 1
    assert search.holds(KILL) is free_travel
    assert (WETLAND in search.collected) is free_travel
    if not free_travel:
        search.collect("Route Return Permit")
        search.collect_spheres(placements)
        assert search.holds(KILL)
        assert WETLAND in search.collected
    search.collect_spheres(placements)
    assert search.counts["Gold Skulltula Token"] == 1


def test_child_event_survives_pull_and_age_shared_checks_never_pay_twice():
    world = route_world()
    search = Search(world, GEAR)
    placements = {name: "Gold Skulltula Token" for name in IDENTITIES}
    spheres = search.collect_spheres(placements)
    assert search.holds(KILL)
    assert search.can_access(world.locations[WETLAND], ADULT)
    assert not search.can_access(world.locations[WETLAND], CHILD)
    assert all(sum(spheres, []).count(name) == 1 for name in IDENTITIES)
    assert search.counts["Gold Skulltula Token"] == 3
    search.collect("Route Return Permit")
    assert search.collect_spheres(placements) == []
    assert search.can_access(world.locations[TOWER], CHILD)
    assert search.can_access(world.locations[TOWER], ADULT)
    assert search.counts["Gold Skulltula Token"] == 3
