"""Played reflected-beam Beamos kill; not a generic Mirror Shield explosive substitute."""

import pytest

from clawshot.generate import Settings, prepare
from clawshot.world import ADULT, CHILD, Search, load_spec


def starting_at(region, *, sword_shuffle=False):
    spec = load_spec()
    spec["start"] = region
    return prepare(spec, Settings(shuffle_master_sword=sword_shuffle, logic={"free_time_travel": sword_shuffle}))[1]


@pytest.mark.parametrize(
    "tool", [("Mirror Shield",), ("Megaton Hammer",), ("Progressive Bomb Bag", "Progressive Strength")]
)
def test_anubis_hall_beamos_accepts_each_played_adult_kill(tool):
    world = starting_at("Spirit Temple Anubis Room")
    assert not Search.adult_after_pull(world).can_reach("Spirit Temple Beyond Anubis Room", ADULT)
    assert Search.adult_after_pull(world, tool).can_reach("Spirit Temple Beyond Anubis Room", ADULT)


@pytest.mark.parametrize("items", [("Mirror Shield",), ("Mirror Shield", "Goron Tunic")])
def test_gtg_beamos_chest_and_lava_route_keep_their_other_requirements(items):
    world = starting_at("Gerudo Training Ground Lobby")
    search = Search.adult_after_pull(world, items)
    assert search.can_access(world.locations["Gerudo Training Ground Beamos Chest"], ADULT)
    assert search.can_reach("Gerudo Training Ground Lava Room Front", ADULT) is ("Goron Tunic" in items)


@pytest.mark.parametrize("age,items", [(CHILD, ("Mirror Shield", "Kokiri Sword")), (ADULT, ("Hylian Shield",))])
def test_child_mirror_and_ordinary_shield_cannot_supply_the_beamos_kill(age, items):
    world = starting_at("Gerudo Training Ground Lobby")
    constructor = Search.child_only if age == CHILD else Search.adult_after_pull
    assert not constructor(world, items).can_access(world.locations["Gerudo Training Ground Beamos Chest"], age)


def test_swordless_mirror_kill_does_not_defeat_the_other_gtg_enemies():
    world = starting_at("Gerudo Training Ground Lobby", sword_shuffle=True)
    items = ["Mirror Shield", "Goron Tunic"]
    search = Search.adult_after_pull(world, items)
    assert not search.can_access(world.locations["Gerudo Training Ground Beamos Chest"], ADULT)
    assert not search.can_reach("Gerudo Training Ground Lava Room Front", ADULT)
    search = Search.adult_after_pull(world, [*items, "Master Sword"])
    assert search.can_access(world.locations["Gerudo Training Ground Beamos Chest"], ADULT)
    assert search.can_reach("Gerudo Training Ground Lava Room Front", ADULT)


def test_mirror_shield_does_not_break_the_shadow_beamos_rooms_cracked_wall():
    world = starting_at("Shadow Temple First Beamos")
    items = ["Mirror Shield", *("Small Key (Shadow Temple)" for _ in range(5))]
    assert not Search.adult_after_pull(world, items).can_reach("Shadow Temple Huge Pit", ADULT)
