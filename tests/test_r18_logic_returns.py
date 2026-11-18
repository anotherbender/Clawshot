"""Played Dampé trap and Kareem's warp-only Colossus policy; no save-warp assumptions."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec
from clawshot.world.softlocks import reachable_traps

RACE_REWARDS = ("Graveyard Dampe Race Hookshot Chest", "Graveyard Dampe Race Freestanding PoH")
ESCAPES = ("Minuet of Forest", "Serenade of Water", "Nocturne of Shadow", "Prelude of Light")


@pytest.mark.parametrize("reward", RACE_REWARDS)
def test_dampe_reward_cannot_supply_its_own_escape(reward):
    spec = load_spec()
    spec["start"] = "Graveyard"
    search = Search(build_world(spec))
    spheres = search.collect_spheres({reward: "Hookshot"})
    assert not search.can_access(search.world.locations[reward], ADULT), {
        "reward": reward,
        "spheres": spheres,
        "adult": search.inventory(ADULT),
    }


@pytest.mark.parametrize("tool", ["Hookshot", "Longshot"])
def test_dampe_has_a_real_windmill_return_without_song_of_time(tool):
    spec = load_spec()
    next(r for r in spec["regions"] if r["name"] == "Root")["exits"] = {"Graveyard Dampes Grave": "is_adult"}
    world = build_world(spec)
    search = Search(world, [tool])
    assert search.can_reach("Kak Windmill", ADULT)
    assert search.inventory(ADULT).get("Dampes Windmill Access") == 1
    assert all(search.can_access(world.locations[name], ADULT) for name in RACE_REWARDS)
    assert not [t for t in reachable_traps(search, regions=["Graveyard Dampes Grave"]) if t.age == ADULT]


def test_dampe_does_not_invent_a_reverse_race_or_song_of_time_escape():
    spec = load_spec()
    spec["start"] = "Graveyard Dampes Grave"
    search = Search(build_world(spec), ["Ocarina of Time", "Song of Time"])
    assert not search.can_reach("Graveyard", ADULT), search.reached[ADULT]
    assert not search.can_reach("Kak Windmill", ADULT), search.reached[ADULT]


@pytest.mark.parametrize("age,instrument", [(CHILD, "Fairy Ocarina"), (ADULT, "Ocarina of Time")])
@pytest.mark.parametrize("arrival", ["Requiem of Spirit Warp", "Wasteland Near Colossus"])
@pytest.mark.parametrize("escape", [None, *ESCAPES])
def test_every_external_colossus_arrival_needs_a_preheld_usable_escape(age, instrument, arrival, escape):
    spec = load_spec()
    spec["start"] = arrival
    spec["settings"]["open_forest"] = "open"
    items = [instrument, "Requiem of Spirit", *([escape] if escape else [])]
    world = build_world(spec)
    search = Search(world, items)
    # The landing's own lesson/reward must not bootstrap its escape.
    search.collect_spheres({"Sheik at Colossus": "Prelude of Light"})
    assert search.can_reach("Desert Colossus", age) == (escape is not None), {
        "age": age,
        "arrival": arrival,
        "items": items,
        "inventory": search.inventory(age),
    }


@pytest.mark.parametrize("instrument", [None, "Fairy Ocarina"])
def test_adult_colossus_does_not_borrow_child_instrument(instrument):
    spec = load_spec()
    spec["start"] = "Requiem of Spirit Warp"
    search = Search(build_world(spec), ["Prelude of Light", *([instrument] if instrument else [])])
    assert not search.can_reach("Desert Colossus", ADULT), search.inventory(ADULT)


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_colossus_checker_does_not_certify_reverse_desert_walking(age):
    spec = load_spec()
    next(r for r in spec["regions"] if r["name"] == "Root")["exits"] = {"Desert Colossus": "True"}
    world = build_world(spec)
    search = Search(world, ["Longshot", "Hover Boots", "Lens of Truth", "Magic Meter"])
    assert not search.can_reach("Wasteland Near Colossus", age), search.reached[age]
    assert any(t.age == age and t.region == "Desert Colossus" for t in reachable_traps(search)), {
        "age": age,
        "findings": reachable_traps(search),
    }
