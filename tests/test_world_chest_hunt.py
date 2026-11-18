"""Played chest hunts: real routes, child history and one canonical copy per pair."""

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
FIELD_CHESTS = tuple(f"Hyrule Field Chest (TBox_Rupee_Red) #{i}" for i in (1, 2))
LAKE_SHORE = "Hyrule Field Chest (TBox_Rupee_Red) #3"
LAKE_TORCHES = "Hyrule Field Chest (TBox_Rupee_Red) #4"
VALLEY_RED = "Gerudo Valley Chest (TBox_Rupee_Red) [Adult]"
VALLEY_CHILD_COPY = "Gerudo Valley Chest (TBox_Rupee_Red) [Child]"
VALLEY_GREEN = "Gerudo Valley Chest (TBox_Rupee_Green)"
VALLEY_UNDERWATER = "Gerudo Valley Chest (Item_ScrubBusinessSeed)"
FORTRESS = "Gerudo Fortress Chest (TBox_Rupee_Red)"
FOUNTAIN = "Zora Fountain Chest (TBox_Rupee_Purple)"
WELL = "Bottom Of The Well Room 11 Chest (Item_ScrubBusinessSeed)"
PART_TWO = (
    *FIELD_CHESTS,
    LAKE_SHORE,
    LAKE_TORCHES,
    VALLEY_RED,
    VALLEY_GREEN,
    VALLEY_UNDERWATER,
    FORTRESS,
    FOUNTAIN,
    WELL,
)
PULL, RETURN = "Hunt Pull Permit", "Hunt Return Permit"


def starting_at(region, age, exits=()):
    spec = load_spec()
    spec["start"] = "Hunt Root"
    spec["settings"].update(starting_age=age, age_return_region="Hunt Root")
    spec["items"].update({PULL: {}, RETURN: {}})
    # Isolate the actual chest/bean rules from unrelated routes that could supply
    # time travel or clear a sage with the test inventory. Keep the existing bean
    # bridge exit, whose here(can_plant_bean) event the ledge must reuse.
    for data in spec["regions"]:
        kept = (("LW Bridge",) if region == "Lost Woods" else exits) if data["name"] == region else ()
        data["exits"] = {name: rule for name, rule in data.get("exits", {}).items() if name in kept}
        data["events"] = {}
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
    assert selected & {VALLEY_RED, VALLEY_CHILD_COPY} == {VALLEY_RED}
    assert set(PART_TWO) <= selected


@pytest.mark.parametrize("name", FIELD_CHESTS)
@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_field_open_air_chests_need_only_their_native_adult_layer(name, age):
    world = starting_at("Hyrule Field", age)
    assert Search(world).can_access(world.locations[name], age) is (age == ADULT)


@pytest.mark.parametrize(
    ("age", "gear", "expected"),
    [
        (CHILD, [], False),
        (CHILD, ["Water Temple Clear"], False),
        (ADULT, [], False),
        (ADULT, ["Water Medallion"], False),
        (ADULT, ["Water Temple Clear"], True),
    ],
)
def test_lake_shore_chest_needs_native_adult_layer_and_full_lake(age, gear, expected):
    world = starting_at("Lake Hylia", age)
    assert Search(world, gear).can_access(world.locations[LAKE_SHORE], age) is expected


@pytest.mark.parametrize(
    ("age", "gear", "expected"),
    [
        (CHILD, ["Dins Fire"], False),
        (CHILD, ["Buy Deku Stick (1)"], False),
        (CHILD, ["Dins Fire", "Buy Deku Stick (1)"], True),
        (CHILD, ["Dins Fire", "Bow"], False),
        (CHILD, ["Fire Arrows", "Bow", "Magic Meter"], False),
        (ADULT, ["Dins Fire"], False),
        (ADULT, ["Dins Fire", "Buy Deku Stick (1)"], False),
        (ADULT, ["Bow"], False),
        (ADULT, ["Dins Fire", "Bow"], True),
        (ADULT, ["Fire Arrows", "Magic Meter"], False),
        (ADULT, ["Fire Arrows", "Bow", "Magic Meter"], True),
    ],
)
def test_lake_four_torches_need_a_first_flame_and_a_way_to_reach_the_fourth(age, gear, expected):
    world = starting_at("LH Grotto", age)
    assert Search(world, gear).can_access(world.locations[LAKE_TORCHES], age) is expected


@pytest.mark.parametrize(
    ("age", "gear", "expected"),
    [
        (CHILD, ["Dins Fire", "Buy Deku Stick (1)"], True),
        (ADULT, ["Dins Fire", "Bow"], False),
        (ADULT, ["Dins Fire", "Bow", "Water Temple Clear"], True),
        (ADULT, ["Dins Fire", "Bow", "Hookshot", "Scarecrow Song", "Ocarina of Time"], True),
        (ADULT, ["Dins Fire", "Bow", "Hookshot", "Scarecrow Song"], False),
    ],
)
def test_lake_grotto_also_requires_the_existing_island_route(age, gear, expected):
    world = starting_at("Lake Hylia", age, exits=("LH Grotto",))
    assert Search(world, gear).can_access(world.locations[LAKE_TORCHES], age) is expected


def test_child_planted_lake_bean_opens_the_adult_gravestone_route():
    world = starting_at("Lake Hylia", CHILD, exits=("LH Grotto", "LH Fishing Island"))
    search = Search(world, ["Buy Magic Bean", "Dins Fire", "Bow", PULL])
    assert search.can_access(world.locations[LAKE_TORCHES], ADULT)
    adult_world = starting_at("Lake Hylia", ADULT, exits=("LH Grotto", "LH Fishing Island"))
    assert not Search(adult_world, ["Buy Magic Bean", "Dins Fire", "Bow"]).can_access(
        adult_world.locations[LAKE_TORCHES], ADULT
    )


@pytest.mark.parametrize("name", [VALLEY_RED, VALLEY_GREEN])
@pytest.mark.parametrize(
    ("age", "gear", "expected"),
    [
        (CHILD, ["Ocarina", "Song of Storms"], False),
        (ADULT, [], False),
        (ADULT, ["Song of Storms"], False),
        (ADULT, ["Ocarina"], False),
        (ADULT, ["Fairy Ocarina", "Song of Storms"], False),
        (ADULT, ["Ocarina of Time", "Song of Storms"], True),
    ],
)
def test_tent_grotto_chests_need_adult_storms_but_not_lens(name, age, gear, expected):
    world = starting_at("GV Fortress Side", age, exits=("GV Storms Grotto",))
    search = Search(world, gear)
    assert search.can_access(world.locations[name], age) is expected
    assert not search.can_access(world.locations[VALLEY_CHILD_COPY], age)


@pytest.mark.parametrize(
    ("age", "gear", "expected"),
    [
        (CHILD, ["Silver Gauntlets", "Iron Boots"], False),
        (ADULT, ["Iron Boots"], False),
        (ADULT, ["Goron Bracelet", "Iron Boots"], False),
        (ADULT, ["Megaton Hammer", "Iron Boots"], False),
        (ADULT, ["Silver Gauntlets"], False),
        (ADULT, ["Silver Gauntlets", "Iron Boots"], True),
        (ADULT, ["Golden Gauntlets", "Iron Boots"], True),
    ],
)
def test_valley_underwater_chest_needs_silver_rock_access_and_iron_boots(age, gear, expected):
    world = starting_at("GV Grotto Ledge", age, exits=("GV Octorok Grotto",))
    assert Search(world, gear).can_access(world.locations[VALLEY_UNDERWATER], age) is expected


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_fortress_underground_chest_uses_grounds_access_without_card_or_storms(age):
    world = starting_at("Gerudo Fortress", age)
    assert Search(world).can_access(world.locations[FORTRESS], age) is (age == ADULT)


@pytest.mark.parametrize("missing", ["Hookshot", "Scarecrow Song", "Ocarina of Time"])
def test_fountain_masonry_chest_needs_each_piece_of_the_scarecrow_route(missing):
    world = starting_at("Zoras Fountain", ADULT)
    gear = ["Hookshot", "Scarecrow Song", "Ocarina of Time"]
    search = Search(world, [item for item in gear if item != missing])
    assert not search.can_access(world.locations[FOUNTAIN], ADULT)
    search.collect(missing)
    assert search.can_access(world.locations[FOUNTAIN], ADULT)
    child_world = starting_at("Zoras Fountain", CHILD)
    assert not Search(child_world, gear).can_access(child_world.locations[FOUNTAIN], CHILD)


@pytest.mark.parametrize("missing", ["Lens of Truth", "Zeldas Lullaby", "Ocarina"])
def test_well_hidden_hole_needs_the_hall_song_and_claudes_lens_guard(missing):
    world = starting_at("Bottom of the Well Main Area", CHILD)
    gear = ["Lens of Truth", "Zeldas Lullaby", "Ocarina"]
    search = Search(world, [item for item in gear if item != missing])
    assert not search.can_access(world.locations[WELL], CHILD)
    search.collect(missing)
    assert search.can_access(world.locations[WELL], CHILD)
    adult_world = starting_at("Bottom of the Well Main Area", ADULT)
    assert not Search(adult_world, gear).can_access(adult_world.locations[WELL], ADULT)
