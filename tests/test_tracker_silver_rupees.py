"""Silver rupees from the save (round 22): a puzzle's own saved clear Bool counts as its whole group in the logic
inventory (``data/tracker_logic.toml`` ``[silver_rupees]``). Synthetic saves only; the evidence for each flag is in
its ``source`` and in the round's receipt (read-only dump)."""

from collections import Counter

import pytest
from test_tracker_state import parse

from clawshot.generate import Settings
from clawshot.patch.logic_world import logic_world
from clawshot.tracker import logic as tracker_logic
from clawshot.tracker import seeds
from clawshot.world import ADULT, Search, load_spec

# World group -> saved completion Bool (17 puzzles; the two slopes sets share one group/clear).
AUDITED = {
    "Silver Rupee (Bottom of the Well Basement)": "BottomOfTheWell_Level_Room_09_A_SilverRupee_GetAll",
    "Silver Rupee (Ice Cavern Spinning Scythe)": "IceCavern_Room05_Unlocked",
    "Silver Rupee (Ice Cavern Push Block)": "IceCavern_Room06_Unlocked",
    "Silver Rupee (Gerudo Training Ground Slopes)": "GerudoTrainingGround_Dungeon_Room02_SilverRupee",
    "Silver Rupee (Gerudo Training Ground Water)": "GerudoTrainingGround_Dungeon_Room09_SilverRupee",
    "Silver Rupee (Gerudo Training Ground Lava)": "HavePlayedEvent.GerudoTrainingGround_06_SilverToken_Unlock",
    "Silver Rupee (Ganons Castle Forest Trial)": "InsideGanonCastle_Dungeon_Room03_SilverRupee",
    "Silver Rupee (Ganons Castle Fire Trial)": "InsideGanonCastle_Dungeon_Room10_SilverRupee",
    "Silver Rupee (Ganons Castle Light Trial)": "InsideGanonCastle_Dungeon_Room14_SilverRupee",
    "Silver Rupee (Ganons Castle Spirit Trial)": "InsideGanonCastle_Dungeon_Room16_SilverRupee",
    "Silver Rupee (Shadow Temple Scythe Shortcut)": "ShadowTemple_RoomB2FC_Cleared",
    "Silver Rupee (Shadow Temple Huge Pit)": "ShadowTemple_Level_Room_09_Clear_B",
    "Silver Rupee (Shadow Temple Invisible Spikes)": "ShadowTemple_RoomB3FB4FE_Cleared_01",
    "Silver Rupee (Spirit Temple Child Early Torches)": "SpiritTemple_Room05_BoardNet_On",
    "Silver Rupee (Spirit Temple Sun Block)": "SpiritTemple_Room10_Candle_On",
    "Silver Rupee (Spirit Temple Adult Boulders)": "SpiritTemple_Room16_Unlocked",
}
FOREST = "Silver Rupee (Ganons Castle Forest Trial)"
FIRE = "Silver Rupee (Ganons Castle Fire Trial)"
ENDING = "Ganons Castle Forest Trial Ending"


@pytest.fixture(scope="module")
def mapping():
    return tracker_logic.load_mapping()


@pytest.fixture(scope="module")
def castle():
    """A seed's logic world (the tracker's own builder) entered at the castle's trial hub, as
    tests/test_world_remake_adult_ganons_castle.py does, so that only the trial's own rules decide."""
    spec = load_spec()
    spec["start"] = "Ganons Castle Main"
    return logic_world(Settings(), spec)[1]


def seed():
    folder = seeds.Path("seed")
    return seeds.Seed(folder, folder, folder / "spoiler.json", None, "raw", {}, ())


def stock(actor, count=1):
    return {f"PouchData.{actor}.StockNum": count}


def inv(world, bools=None, ints=None):
    return tracker_logic.inventory(seed(), parse(bools or {}, ints or {}), world)


def test_each_count_is_the_world_group(castle, mapping):
    groups = Counter(loc.vanilla for loc in castle.locations.values() if loc.vanilla in castle.items)
    for name, puzzle in mapping.silver_rupees.items():
        assert castle.items[name].type == "SilverRupee"
        assert puzzle.count == groups[name] == 5, name
    # Every live world group is mapped; a group no world location holds is never counted.
    silver = {name for name, item in castle.items.items() if item.type == "SilverRupee" and groups[name]}
    assert silver == set(mapping.silver_rupees)
    assert all(name in mapping.unmapped for name in castle.items if name.startswith("Silver Rupee Pouch"))


@pytest.mark.parametrize("name", sorted(AUDITED))
def test_a_saved_clear_counts_the_whole_group_and_nothing_else_does(castle, name):
    flag = AUDITED[name]
    cleared = inv(castle, {flag: True})
    assert cleared.counts[name] == 5 and name not in cleared.unknown
    assert not [other for other in cleared.counts if other.startswith("Silver Rupee") and other != name]
    # Not cleared: the save says so, nothing counts and nothing is unknown.
    open_ = inv(castle, {flag: False})
    assert name not in open_.counts and name not in open_.unknown
    # Unread: conservative (D4), and listed.
    unread = inv(castle)
    assert name not in unread.counts and name in unread.unknown


def test_lava_encounter_history_does_not_count_as_finishing_the_puzzle(castle):
    result = inv(castle, {"HavePlayedEvent.GerudoTrainingGround_06_SilverToken_Appear": True})
    name = "Silver Rupee (Gerudo Training Ground Lava)"
    assert name not in result.counts and name in result.unknown


# The Forest trial's own rules (remake/adult_ganons_castle.toml): its wind room needs Din's Fire with a Hookshot,
# its ending five silver rupees, the Song of Time, Hover Boots and a Hookshot.
GEAR_BOOLS = {"IsGet.Item_Melody_TimeSong": True}
GEAR_INTS = (
    stock("Item_Hookshot")
    | stock("Item_Ocarina_Time")
    | stock("Armor_Adult_HoverBoot")
    | stock("Item_DinFire")
    | {"PlayerStatus.MPMax": 240}
)


def ending(world, bools, ints=GEAR_INTS):
    result = inv(world, GEAR_BOOLS | bools, ints)
    return result, Search(world, tracker_logic.search_items(result, world)).can_reach(ENDING, ADULT)


def test_the_forest_trial_ending_is_in_logic_only_with_the_rooms_saved_clear(castle):
    result, reached = ending(castle, {AUDITED[FOREST]: True})
    assert result.counts[FOREST] == 5 and reached
    # Not cleared, or only another trial's room cleared: the floor's rupees are not the tracker's to count.
    assert not ending(castle, {AUDITED[FOREST]: False})[1]
    other, reached = ending(castle, {AUDITED[FOREST]: False, AUDITED[FIRE]: True})
    assert other.counts[FIRE] == 5 and FOREST not in other.counts and not reached
    # The flag missing from the save: unknown, and conservatively out of logic.
    missing, reached = ending(castle, {})
    assert FOREST in missing.unknown and not reached


@pytest.mark.parametrize(
    ("bools", "ints"),
    [
        ({"IsGet.Item_Melody_TimeSong": False}, GEAR_INTS),
        ({}, GEAR_INTS | stock("Armor_Adult_HoverBoot", 0)),
        ({}, GEAR_INTS | stock("Item_Hookshot", 0)),
    ],
    ids=["no Song of Time", "no Hover Boots", "no Hookshot"],
)
def test_the_saved_clear_does_not_stand_in_for_the_trials_gear(castle, bools, ints):
    result, reached = ending(castle, {AUDITED[FOREST]: True} | bools, ints)
    assert result.counts[FOREST] == 5 and not reached
