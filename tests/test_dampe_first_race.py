"""Dampe's first-race chest never opens in a Clawshot seed, so it may only hold non-progression items.

The race needs a Hookshot or Longshot (``patch/dampe_safety``) and the native flow then always runs the second race
(``MiniGame_DampeRace_ClearCount`` rises at every finish while the Hookshot is owned), so the first-race chest never
spawns. Kareem saw it in game on 0.2.6 (2026-11-24); work/r22-dampe/report.md measured 93 of 400 seeds broken.
"""

import pytest

from clawshot.generate import FillError, Settings, from_placements, generate, prepare
from clawshot.generate.fill import _swap, allowed
from clawshot.world import build_world, load_spec

FIRST_RACE = "Graveyard Dampe Race Hookshot Chest"
SECOND_RACE = "Graveyard Dampe Race Freestanding PoH"
SHUFFLES = [("Chest",), ("Chest", "Freestanding", "NPC", "Token", "Song")]


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_no_production_progression_item_may_go_to_the_first_race_chest(shuffle):
    settings, world = prepare(load_spec(), Settings(shuffle=shuffle))
    assert world.items["Progressive Hookshot"].progression
    assert "Progressive Hookshot" in world.locations[FIRST_RACE].excluded_items
    unsafe = [
        item for item, info in world.items.items() if info.progression and allowed(world, settings, FIRST_RACE, item)
    ]
    assert not unsafe, unsafe
    assert allowed(world, settings, FIRST_RACE, "Rupees (5)")


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_the_second_race_chest_is_not_restricted(shuffle):
    _settings, world = prepare(load_spec(), Settings(shuffle=shuffle))
    assert "Progressive Hookshot" not in world.locations[SECOND_RACE].excluded_items


def race_spec():
    return {
        "start": "Root",
        "goal": "Boomerang and Hylian_Shield",
        "items": {"Boomerang": {}, "Hylian Shield": {}, "Rupees (5)": {"class": "normal"}},
        "regions": [
            {
                "name": "Root",
                "locations": {
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Boomerang"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Hylian Shield"},
                    FIRST_RACE: {"rule": "True", "type": "Chest", "vanilla": "Rupees (5)", "nonprogression_only": True},
                },
            }
        ],
    }


def test_a_seed_puts_only_junk_in_the_first_race_chest():
    for seed_number in range(1, 9):
        seed = generate(race_spec(), seed_number, Settings(shuffle=("Chest",)))
        assert seed.placements[FIRST_RACE] == "Rupees (5)"


def test_external_assignments_cannot_put_progression_in_the_first_race_chest():
    supplied = {FIRST_RACE: "Boomerang", "Chest A": "Rupees (5)", "Chest B": "Hylian Shield"}
    with pytest.raises(FillError, match=FIRST_RACE):
        from_placements(race_spec(), 7, Settings(shuffle=("Chest",)), supplied)


def test_a_swap_cannot_move_progression_into_the_first_race_chest():
    world = build_world(race_spec())
    placements = {FIRST_RACE: "Rupees (5)", "Chest A": "Boomerang"}
    before = dict(placements)
    assert _swap(world, Settings(shuffle=("Chest",)), placements, [FIRST_RACE], "Hylian Shield", [], {}) is None
    assert placements == before
