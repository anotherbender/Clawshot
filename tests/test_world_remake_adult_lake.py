"""Lake Hylia remake entrance and post-Water access."""

from dataclasses import replace

import pytest

from clawshot.generate import FillError
from clawshot.generate.fill import check_beatable
from clawshot.generate.progressive import prepare_spec
from clawshot.world import ADULT, Search, build_world, load_spec

ICE_SOURCE = "Ice Cavern End Chest Access"
CYCLE_PLACEMENTS = {
    "Song from Impa": "Rupees (5)",
    "ZD Diving Minigame": "Rupees (20)",
    "LH Adult Fishing": "Rupees (5)",
    "Water Temple Map Chest": "Zeldas Lullaby",
    "Water Temple Torches Chest": "Map (Water Temple)",
    "Water Temple Central Pillar Chest": "Progressive Scale",
    "Water Temple Longshot Chest": "Progressive Scale",
    "KF Midos Top Left Chest": "Small Key (Water Temple)",
    "KF Midos Top Right Chest": "Progressive Hookshot",
    "KF Midos Bottom Left Chest": "Iron Boots",
    "Ice Cavern Iron Boots Chest": "Rupee (1)",
}


@pytest.fixture(scope="module")
def cycle_world():
    spec = dict(prepare_spec(load_spec()))
    spec["start"] = "Lake Hylia"
    spec["goal"] = "at('Water Temple Lobby', True)"
    spec["settings"].update(starting_age="adult", door_of_time="open")
    world = build_world(spec)
    withheld = {"Zeldas Lullaby", "Progressive Scale", "Triforce", "Triforce Piece"}
    withheld.update(name for name, item in world.items.items() if item.alias and item.alias[0] == "Progressive Scale")
    # Isolate the cycle, not other shortages: twelve covers dungeon keys and Ice silver rupees.
    inventory = tuple(
        name
        for name, item in world.items.items()
        if item.type not in {"Event", "Drop"} and name not in withheld
        for _ in range(12)
    )
    return replace(world, start_items=(*world.start_items, *inventory))


def test_golden_scale_does_not_substitute_for_water_entry_boots():
    spec = load_spec()
    spec["start"] = "Lake Hylia"
    world = build_world(spec)
    # Completed Ice history isolates the physical Boots requirement.
    search = Search(world, ["Longshot", "Golden Scale", "Zora Tunic", ICE_SOURCE])
    assert not search.can_reach("Water Temple Lobby", ADULT)
    search.collect("Iron Boots")
    assert search.can_reach("Water Temple Lobby", ADULT)


def test_low_water_scarecrow_does_not_grant_fire_arrows():
    spec = load_spec()
    spec["start"] = "Lake Hylia"
    world = build_world(spec)
    search = Search(world, ["Bow", "Longshot", "Ocarina of Time", "Scarecrow Song"])
    arrows = world.locations["LH Sun"]
    assert not search.can_access(arrows, ADULT)
    search.collect("Water Temple Clear")
    assert search.can_access(arrows, ADULT)


def test_water_entry_rejects_its_own_ice_access_items(cycle_world):
    with pytest.raises(FillError, match="the goal cannot be reached"):
        check_beatable(cycle_world, CYCLE_PLACEMENTS)


def test_outside_lullaby_repairs_the_water_ice_cycle(cycle_world):
    repaired = dict(CYCLE_PLACEMENTS)
    repaired["KF Midos Top Left Chest"], repaired["Water Temple Map Chest"] = (
        repaired["Water Temple Map Chest"],
        repaired["KF Midos Top Left Chest"],
    )
    collected = {name for sphere in check_beatable(cycle_world, repaired) for name in sphere}
    assert {"Ice Cavern Iron Boots Chest", "Water Temple Map Chest"} <= collected


@pytest.mark.parametrize(
    "gear",
    [
        ["Hookshot", "Iron Boots"],
        ["Hookshot", "Iron Boots", "Ocarina of Time", "Serenade of Water"],
    ],
)
def test_early_equipment_and_serenade_do_not_replace_the_ice_source(gear):
    spec = load_spec()
    spec["start"] = "Lake Hylia"
    world = build_world(spec)
    search = Search(world, gear)
    assert not search.can_access(world.locations["Ice Cavern Iron Boots Chest"], ADULT)
    assert not search.holds(ICE_SOURCE)
    assert not search.can_reach("Water Temple Lobby", ADULT)


def test_junk_chest_and_song_rewards_still_complete_the_ice_source():
    spec = load_spec()
    spec["start"] = "Ice Cavern End"
    spec["settings"]["starting_age"] = "adult"
    world = build_world(spec)
    search = Search(world)
    rewards = {"Ice Cavern Iron Boots Chest": "Rupees (5)", "Sheik in Ice Cavern": "Rupees (20)"}
    search.collect_spheres(rewards)
    assert set(rewards) <= search.collected
    assert search.holds(ICE_SOURCE)
    assert not search.holds("Iron Boots")
    assert not search.holds("Serenade of Water")


def test_entering_ice_does_not_complete_the_end_chest_source():
    spec = load_spec()
    spec["start"] = "Ice Cavern Beginning"
    spec["settings"]["starting_age"] = "adult"
    world = build_world(spec)
    search = Search(world, ["Hookshot", "Iron Boots", "Ocarina of Time", "Serenade of Water"])
    assert search.can_reach("Ice Cavern Beginning", ADULT)
    assert not search.can_access(world.locations["Ice Cavern Iron Boots Chest"], ADULT)
    assert not search.holds(ICE_SOURCE)


def test_completed_ice_and_boots_do_not_replace_hookshot():
    spec = load_spec()
    spec["start"] = "Lake Hylia"
    world = build_world(spec)
    search = Search(world, [ICE_SOURCE, "Iron Boots"])
    assert not search.can_reach("Water Temple Lobby", ADULT)
    search.collect("Hookshot")
    assert search.can_reach("Water Temple Lobby", ADULT)
