"""Native adult Goron City token and grotto approaches."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec


def test_goron_city_ceiling_token_needs_hookshot():
    spec = load_spec()
    spec["start"] = "Goron City"
    world = build_world(spec)
    search = Search(world, ["Bow"])
    token = world.locations["GC GS Center Platform"]
    assert not search.can_access(token, ADULT)
    search.collect("Hookshot")
    assert search.can_access(token, ADULT)


@pytest.mark.parametrize("damage", ["normal", "quadruple", "ohko"])
def test_goron_grotto_cannot_use_the_missing_time_block(damage):
    spec = load_spec()
    spec["start"] = "Goron City"
    world = build_world(spec, {"damage_multiplier": damage})
    search = Search.adult_after_pull(world, ["Ocarina of Time", "Song of Time", "Goron Tunic"])
    assert not search.can_reach("GC Grotto Platform", ADULT)


@pytest.mark.parametrize(
    "items",
    [
        ["Hookshot", "Goron Tunic"],
        ["Longshot", "Goron Tunic"],
        ["Hover Boots", "Goron Tunic"],
        ["Hookshot", "Longshot", "Hover Boots", "Goron Tunic", "Ocarina of Time", "Song of Time"],
    ],
)
def test_unproved_goron_grotto_approaches_stay_out_of_progression_logic(items):
    spec = load_spec()
    spec["start"] = "Goron City"
    world = build_world(spec)
    search = Search.adult_after_pull(world, items)
    assert not search.can_reach("GC Grotto Platform", ADULT)
    assert not search.can_reach("GC Grotto", ADULT)
    assert not search.can_access(world.locations["Goron City Chest (TBox_Rupee_Purple) #2"], ADULT)


def test_child_cannot_use_the_adult_goron_grotto_approach():
    spec = load_spec()
    spec["start"] = "Goron City"
    world = build_world(spec)
    search = Search.child_only(world, ["Hookshot", "Goron Tunic", "Ocarina of Time", "Song of Time"])
    assert not search.can_reach("GC Grotto Platform", CHILD)


@pytest.mark.parametrize(
    ("age", "items"),
    [
        (CHILD, ["Kokiri Sword"]),
        (ADULT, ["Master Sword"]),
        (ADULT, ["Biggoron Sword"]),
        (ADULT, ["Giants Knife"]),
        (ADULT, ["Hookshot"]),
        (ADULT, ["Longshot"]),
        (CHILD, ["Bomb Bag", "Goron Bracelet"]),
        (ADULT, ["Bomb Bag", "Progressive Strength"]),
    ],
)
def test_sign_solution_accepts_only_proven_usable_attack_methods(age, items):
    spec = load_spec()
    spec["start"] = "GC Grotto"
    world = build_world(spec, {"shuffle_master_sword": True})
    search = Search.child_only(world, items) if age == CHILD else Search.adult_after_pull(world, items)
    assert search.can_access(world.locations["Goron City Chest (TBox_Rupee_Purple) #2"], age)


@pytest.mark.parametrize(
    ("age", "items"),
    [
        (ADULT, []),
        (ADULT, ["Megaton Hammer"]),
        (ADULT, ["Bombchus (10)", "Progressive Strength"]),
        (ADULT, ["Bow"]),
        (ADULT, ["Slingshot"]),
        (ADULT, ["Boomerang"]),
        (ADULT, ["Dins Fire", "Magic Meter"]),
        (ADULT, ["Kokiri Sword"]),
        (CHILD, ["Master Sword"]),
        (CHILD, ["Hookshot"]),
        (ADULT, ["Bomb Bag"]),
    ],
)
def test_sign_solution_rejects_unplayed_or_unusable_attacks(age, items):
    spec = load_spec()
    spec["start"] = "GC Grotto"
    world = build_world(spec, {"shuffle_master_sword": True})
    search = Search.child_only(world, items) if age == CHILD else Search.adult_after_pull(world, items)
    assert not search.can_access(world.locations["Goron City Chest (TBox_Rupee_Purple) #2"], age)
