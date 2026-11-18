"""Interim song-lesson rule: each of the twelve Dm_MelodyGet_* lessons needs an age-usable Ocarina.

The lessons always run their play-along (Dm_SY_Ocarina LearningOcarinaFollowExample waits for Link's own playing)
before the song step, even when Gift shuffle changes the reward. Fairy Ocarina is child-only, Ocarina of Time
both ages (remake/age_ocarina.toml). Events that the game writes only after a lesson ('Met Child Zelda' after
Impa's, the Ice Cavern Water-quest step after Sheik's) must match; rewards given before a lesson must not.
"""

import pytest

from clawshot.generate.progressive import prepare_spec
from clawshot.world import ADULT, CHILD, Search, build_world, load_spec
from clawshot.world.rules import ALL_TIMES, DAY

FAIRY = "Fairy Ocarina"
TIME = "Ocarina of Time"
STONES = {"Kokiri Emerald": 1, "Goron Ruby": 1, "Zora Sapphire": 1}
MEDALLIONS = {"Forest Medallion": 1, "Fire Medallion": 1, "Water Medallion": 1}
MET_ZELDA = "Met Child Zelda"
ICE_SOURCE = "Ice Cavern End Chest Access"
MALON_ROUTE = "<Malon's Talon wake-up subrule>"  # resolved from the compiled rule's reads

# (location, age, the location's existing non-instrument prerequisites, time of day)
LESSONS = [
    ("Sheik at Colossus", CHILD, {}, ALL_TIMES),
    ("Sheik at Colossus", ADULT, {}, ALL_TIMES),
    ("Sheik at Temple", ADULT, {"Defeat Phantom Ganon": 1}, ALL_TIMES),
    ("Sheik in Crater", ADULT, {}, ALL_TIMES),
    ("Sheik in Forest", ADULT, {}, ALL_TIMES),
    ("Sheik in Ice Cavern", ADULT, {}, ALL_TIMES),
    ("Sheik in Ice Cavern", CHILD, {"Slingshot": 1}, ALL_TIMES),
    ("Sheik in Kakariko", ADULT, MEDALLIONS, ALL_TIMES),
    ("Song from Impa", CHILD, {}, ALL_TIMES),
    ("Song from Malon", CHILD, {MALON_ROUTE: 1}, DAY),
    ("Song from Ocarina of Time", CHILD, STONES | {MET_ZELDA: 1}, ALL_TIMES),
    ("Song from Royal Familys Tomb", ADULT, {}, ALL_TIMES),
    ("Song from Royal Familys Tomb", CHILD, {"Kokiri Sword": 1}, ALL_TIMES),
    ("Song from Saria", CHILD, {MET_ZELDA: 1}, ALL_TIMES),
    ("Song from Windmill", ADULT, {}, ALL_TIMES),
]
ADULT_ONLY = {"Sheik at Temple", "Sheik in Crater", "Sheik in Forest", "Sheik in Kakariko", "Song from Windmill"}
CHILD_ONLY = {"Song from Malon", "Song from Ocarina of Time", "Song from Saria"}


def lesson_id(row):
    return f"{row[0]}-{row[1]}"


@pytest.fixture(scope="module")
def world():
    return build_world(load_spec())


@pytest.fixture(scope="module")
def held(world):
    """The counts each real instrument item gives (its own name plus the Ocarina tier)."""
    out = {}
    for name in (FAIRY, TIME):
        counts = Search(world, [name]).inventory(CHILD)
        out[name] = {key: counts[key] for key in (name, "Ocarina")}
    return out


def prerequisites(world, location, ready):
    if MALON_ROUTE not in ready:
        return dict(ready)
    route = next(name for name in world.locations[location].rule.reads if "Subrule" in name)
    return {route: 1}


def usable(age):
    return [FAIRY, TIME] if age == CHILD else [TIME]


def event(world, region, name):
    return next(e for e in world.regions[region].events if e.name == name)


@pytest.mark.parametrize("row", LESSONS, ids=lesson_id)
def test_lesson_refuses_link_without_an_instrument(world, row):
    location, age, ready, time = row
    counts = prerequisites(world, location, ready)
    assert not world.locations[location].rule(counts, age, time), {"location": location, "age": age, "counts": counts}


@pytest.mark.parametrize("row", LESSONS, ids=lesson_id)
def test_lesson_accepts_an_age_usable_ocarina(world, held, row):
    location, age, ready, time = row
    for instrument in usable(age):
        counts = prerequisites(world, location, ready) | held[instrument]
        assert world.locations[location].rule(counts, age, time), {"location": location, "age": age, "counts": counts}


@pytest.mark.parametrize("row", [row for row in LESSONS if row[1] == ADULT], ids=lesson_id)
def test_adult_lesson_refuses_the_child_only_fairy_ocarina(world, held, row):
    location, age, ready, time = row
    counts = prerequisites(world, location, ready) | held[FAIRY]
    assert not world.locations[location].rule(counts, age, time), {"location": location, "counts": counts}


@pytest.mark.parametrize("row", LESSONS, ids=lesson_id)
def test_lesson_keeps_its_existing_source_and_age_prerequisites(world, held, row):
    location, age, ready, time = row
    rule = world.locations[location].rule
    if ready:
        assert not rule(held[TIME], age, time), {"location": location, "missing": ready}
    full = prerequisites(world, location, ready) | held[TIME] | held[FAIRY]
    if location in ADULT_ONLY:
        assert not rule(full, CHILD, time), location
    if location in CHILD_ONLY:
        assert not rule(full, ADULT, time), location


def test_impa_sendoff_needs_the_completed_lesson_instrument(world, held):
    sendoff = event(world, "HC Garden Skippable Locations", MET_ZELDA).rule
    assert not sendoff({}, CHILD, ALL_TIMES)
    for instrument in (FAIRY, TIME):
        assert sendoff(held[instrument], CHILD, ALL_TIMES), instrument
    assert not sendoff(held[TIME], ADULT, ALL_TIMES)


def test_castle_route_holds_the_sendoff_only_with_an_instrument():
    spec = load_spec()
    spec["start"] = "Hyrule Field"
    world = build_world(spec)
    search = Search(world, ["Weird Egg"])
    assert search.can_reach("HC Garden", CHILD)
    assert not search.holds(MET_ZELDA), search.inventory(CHILD)
    assert not search.holds("Time Flows")
    assert not search.can_access(world.locations["Song from Impa"], CHILD)
    search.collect(FAIRY)
    assert search.holds(MET_ZELDA) and search.holds("Time Flows")
    assert search.can_access(world.locations["Song from Impa"], CHILD)


def test_ice_quest_step_needs_the_completed_lesson_instrument(world, held):
    source = event(world, "Ice Cavern End", ICE_SOURCE).rule
    assert not source({}, ADULT, ALL_TIMES)
    assert not source(held[FAIRY], ADULT, ALL_TIMES)
    assert source(held[TIME], ADULT, ALL_TIMES)
    assert not source({"Slingshot": 1}, CHILD, ALL_TIMES)
    assert not source(held[FAIRY], CHILD, ALL_TIMES)  # the existing child weapon prerequisite stays
    assert source({"Slingshot": 1} | held[FAIRY], CHILD, ALL_TIMES)


@pytest.mark.parametrize("instrument,lesson_done", [(None, False), (FAIRY, False), (TIME, True)])
def test_iron_boots_chest_reward_precedes_the_serenade_lesson(instrument, lesson_done):
    spec = load_spec()
    spec["start"] = "Ice Cavern End"
    spec["settings"]["starting_age"] = "adult"
    world = build_world(spec)
    search = Search(world, [instrument] if instrument else [])
    rewards = {"Ice Cavern Iron Boots Chest": "Rupees (5)", "Sheik in Ice Cavern": "Rupees (20)"}
    search.collect_spheres(rewards)
    assert "Ice Cavern Iron Boots Chest" in search.collected  # Dm_SY_Treasurebox runs before Dm_MelodyGet_Water
    assert ("Sheik in Ice Cavern" in search.collected) is lesson_done
    assert search.holds(ICE_SOURCE) is lesson_done


def test_moat_ocarina_reward_precedes_the_time_lesson(world):
    # Dm_MelodyGet_Time Event70 gives the HF Ocarina of Time Item before C08/C09's lesson.
    ready = STONES | {MET_ZELDA: 1}
    assert world.locations["HF Ocarina of Time Item"].rule(ready, CHILD, ALL_TIMES)
    assert not world.locations["Song from Ocarina of Time"].rule(ready, CHILD, ALL_TIMES)


def test_seed_world_reads_the_same_instrument_ages():
    world = build_world(dict(prepare_spec(load_spec())))
    fairy, time = ({name: 1, "Ocarina": tier} for name, tier in ((FAIRY, 1), (TIME, 2)))
    windmill = world.locations["Song from Windmill"].rule
    assert not windmill(fairy, ADULT, ALL_TIMES)
    assert windmill(time, ADULT, ALL_TIMES)
    sendoff = event(world, "HC Garden Skippable Locations", MET_ZELDA).rule
    assert not sendoff({}, CHILD, ALL_TIMES)
    assert sendoff(fairy, CHILD, ALL_TIMES)
