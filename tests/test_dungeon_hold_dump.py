"""Dungeon items stay in chests in a real Gift seed with songs anywhere (round 21, cs21j's audit section 6)."""

import pytest

from clawshot.generate import Settings
from clawshot.generate.fill import CHEST_HELD_DESTINATIONS, CHEST_HELD_DUNGEON_TYPES
from clawshot.patch import gifts, make_seed
from clawshot.world.load import load_spec


@pytest.mark.dump
def test_a_gift_seed_with_songs_anywhere_puts_no_dungeon_item_on_a_lesson(romfs):
    # Seed 1 of this recipe put Compass (Ice Cavern) on Sheik in Ice Cavern before the hold.
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), Settings(shuffle=("Chest", "Gift"), songs="anywhere"))
    seed = make_seed(romfs, 1, settings, spec, extra_steps=[step]).seed
    world = seed.world
    misplaced = {
        name: item
        for name, item in seed.placements.items()
        if name in seed.shuffled
        and world.items[item].type in CHEST_HELD_DUNGEON_TYPES
        and world.locations[name].type not in CHEST_HELD_DESTINATIONS
    }
    assert misplaced == {}
    assert world.items[seed.placements["Sheik in Ice Cavern"]].type not in CHEST_HELD_DUNGEON_TYPES
