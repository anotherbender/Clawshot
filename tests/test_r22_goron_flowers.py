"""Two played adult Low-lift Bomb Flower uses, not a global rock-strength widening."""

import pytest

from clawshot.generate import Settings, prepare
from clawshot.world import ADULT, CHILD, Search, load_spec


@pytest.fixture(scope="module")
def world():
    spec = load_spec()
    spec["start"] = "Goron City"
    return prepare(spec, Settings())[1]


@pytest.mark.parametrize("strength", ["Goron Bracelet", "Progressive Strength"])
def test_adult_low_lift_opens_played_goron_routes_without_a_bag(world, strength):
    search = Search.adult_after_pull(world, [strength])
    assert search.holds("GC Woods Warp Open")
    assert search.can_reach("GC Woods Warp", ADULT)
    assert search.holds("Stop GC Rolling Goron as Adult")
    assert search.can_access(world.locations["GC Rolling Goron as Adult"], ADULT)
    assert search.can_reach("GC Shop", ADULT)
    assert not search.can_access(world.locations["GC Maze Left Chest"], ADULT)
    assert not search.can_access(world.locations["GC Maze Center Chest"], ADULT)


def test_capacity_without_lift_does_not_stop_the_adult_goron(world):
    search = Search.adult_after_pull(world, ["Progressive Bomb Bag"])
    assert not search.holds("GC Woods Warp Open")
    assert not search.holds("Stop GC Rolling Goron as Adult")


def test_child_cannot_collect_the_adult_gorons_gift_with_the_bracelet(world):
    search = Search.child_only(world, ["Goron Bracelet"])
    assert not search.holds("Stop GC Rolling Goron as Adult")
    assert not search.can_access(world.locations["GC Rolling Goron as Adult"], CHILD)
