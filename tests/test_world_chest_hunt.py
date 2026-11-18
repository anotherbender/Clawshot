"""Kareem's round-17 chest hunt: real routes, child history and one canonical copy per pair."""

import pytest

from clawshot.generate import Settings
from clawshot.generate.fill import shuffled_locations
from clawshot.world import ADULT, CHILD, Search, build_world, load_spec, load_world

LEDGE = "Lost Wood Chest (TBox_Rupee_Purple)"
KF_COPY = "Kokiri Forest Chest (TBox_Rupee_Purple)"
TOWER = "Hyrule Field Chest (Item_ScrubBusinessSeed)"
WINDMILL = "Kakariko Village Chest (TBox_Rupee_Purple) [Adult Alternative]"
NORMAL_COPY = "Kakariko Village Chest (TBox_Rupee_Purple) [Adult]"
SAGES = ("Defeat Phantom Ganon", "Defeat Volvagia", "Defeat Morpha")
PULL, RETURN = "Hunt Pull Permit", "Hunt Return Permit"


def starting_at(region, age):
    spec = load_spec()
    spec["start"] = "Hunt Root"
    spec["settings"].update(starting_age=age, age_return_region="Hunt Root")
    spec["items"].update({PULL: {}, RETURN: {}})
    # Isolate the actual chest/bean rules from unrelated routes that could supply
    # time travel or clear a sage with the test inventory. Keep the existing bean
    # bridge exit, whose here(can_plant_bean) event the ledge must reuse.
    for data in spec["regions"]:
        if data["name"] == region:
            data["exits"] = {"LW Bridge": data["exits"]["LW Bridge"]} if region == "Lost Woods" else {}
            data["events"] = {}
        elif data["name"] == "LW Bridge":
            data["exits"] = {}
    spec["regions"].append(
        {
            "name": "Hunt Root",
            "exits": {region: "is_starting_age or Time_Travel"},
            "events": {"Time Travel": repr(PULL), "Defeat Phantom Ganon": repr(RETURN)},
        }
    )
    return build_world(spec)


def test_adult_beans_do_not_replace_child_planting_at_the_existing_bridge_spot():
    world = starting_at("Lost Woods", ADULT)
    search = Search(world, ["Buy Magic Bean", PULL])
    assert search.can_reach("Lost Woods", ADULT)
    assert not search.can_reach("Lost Woods", CHILD)
    assert not search.can_access(world.locations[LEDGE], ADULT)
    search.collect(RETURN)
    assert search.can_reach("Lost Woods", CHILD)
    assert search.can_access(world.locations[LEDGE], ADULT)
    assert not search.can_access(world.locations[LEDGE], CHILD)


def test_child_planted_bridge_bean_survives_the_pull_and_cannot_pay_the_kf_copy():
    world = starting_at("Lost Woods", CHILD)
    search = Search(world, ["Buy Magic Bean"])
    assert not search.can_access(world.locations[LEDGE], CHILD)
    assert not search.can_access(world.locations[LEDGE], ADULT)
    search.collect(PULL)
    assert search.can_access(world.locations[LEDGE], ADULT)
    search.collect_spheres({LEDGE: "Rupees (50)", KF_COPY: "Rupees (50)"})
    assert search.counts["Rupees (50)"] == 1
    assert search.collected == {LEDGE}


@pytest.mark.parametrize(
    ("age", "gear", "expected"),
    [
        (CHILD, [], False),
        (CHILD, ["Hookshot"], False),
        (ADULT, [], False),
        (ADULT, ["Hookshot"], True),
        (ADULT, ["Longshot"], True),
    ],
)
def test_ranch_tower_chest_requires_adult_vine_retrieval(age, gear, expected):
    world = starting_at("LLR Tower", age)
    assert Search(world, gear).can_access(world.locations[TOWER], age) is expected


@pytest.mark.parametrize("missing", SAGES)
def test_alternative_windmill_needs_every_real_sage_completion(missing):
    world = starting_at("Kak Windmill", ADULT)
    search = Search(world, ["Longshot", *(sage for sage in SAGES if sage != missing)])
    assert not search.can_access(world.locations[WINDMILL], ADULT)
    search.collect(missing)
    assert search.can_access(world.locations[WINDMILL], ADULT)
    assert not search.can_access(world.locations[NORMAL_COPY], ADULT)


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_hookshot_does_not_replace_the_played_longshot_windmill_route(age):
    world = starting_at("Kak Windmill", age)
    assert not Search(world, ["Hookshot", *SAGES]).can_access(world.locations[WINDMILL], age)


def test_owned_medallions_do_not_replace_the_alternative_scene_story_gate():
    world = starting_at("Kak Windmill", ADULT)
    assert not Search(world, ["Longshot", "Forest Medallion", "Fire Medallion", "Water Medallion"]).can_access(
        world.locations[WINDMILL], ADULT
    )


def test_played_chest_pairs_contribute_only_the_canonical_checks_to_the_fill_pool():
    world = load_world()
    selected = set(shuffled_locations(world, Settings()))
    assert {LEDGE, TOWER, WINDMILL} <= selected
    assert selected & {LEDGE, KF_COPY} == {LEDGE}
    assert selected & {WINDMILL, NORMAL_COPY} == {WINDMILL}
