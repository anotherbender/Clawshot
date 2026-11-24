"""The logic inventory a save gives (``clawshot.tracker.logic.inventory``): synthetic saves, the generator's world."""

import json
from collections import Counter

import pytest
from test_tracker_logic import SPEC
from test_tracker_state import parse

from clawshot import save
from clawshot.generate import Settings
from clawshot.patch.logic_world import logic_world
from clawshot.tracker import logic as tracker_logic
from clawshot.tracker import seeds
from clawshot.tracker import state as tracker_state
from clawshot.tracker.seeds import Check
from clawshot.world import Search, build_world
from clawshot.world.rules import ADULT, CHILD

LETTER, EMPTY = (save.murmur3_32(name.encode()) for name in ("Letter", "Empty"))


@pytest.fixture(scope="module")
def world():
    return logic_world(Settings(shuffle=("Chest", "Gift", "Scrub", "Shop", "Token")))[1]


def seed(checks=(), **totals):
    folder = seeds.Path("seed")
    return seeds.Seed(folder, folder, folder / "spoiler.json", None, "raw", {}, tuple(checks), **totals)


def stock(actor, count=1):
    return {f"PouchData.{actor}.StockNum": count}


def bottles(*contents):
    """Bools and Enums for owned bottle slots holding ``contents`` (Enum keys); the other slots not owned."""
    bools, enums = {}, {}
    for n, (_slot, valid, content) in enumerate(tracker_state.BOTTLE_SLOTS):
        bools[valid] = n < len(contents)
        enums[content] = contents[n] if n < len(contents) else EMPTY
    return bools, enums


def inv(world, bools=None, ints=None, enums=None, **totals):
    return tracker_logic.inventory(
        seed(**totals), parse(bools or {}, ints or {}, extra={save.ENUM: enums or {}}), world
    )


# 5.1
def test_inventory_comes_from_the_save_not_the_spoiler(world):
    ints = stock("Item_Boomerang") | stock("Item_Hookshot")
    checks = [
        Check("Test Chest", "Test", "", "Test", None, "chest", item, item, "named_bool", ("IsTreasureBoxOpen.1",))
        for item in ("Megaton Hammer", "Light Arrows")
    ]
    one = tracker_logic.inventory(seed(checks[:1]), parse({}, ints), world)
    two = tracker_logic.inventory(seed(checks[1:]), parse({}, ints), world)
    assert one == two
    assert one.counts["Boomerang"] == 1 and one.counts["Progressive Hookshot"] == 1
    assert "Megaton Hammer" not in one.counts and "Light Arrows" not in one.counts


def test_tier_cells_grant_chain_copies(world):
    counts = inv(world, ints=stock("Item_Hookshot") | stock("Item_Longshot") | stock("Item_Wallet_Small")).counts
    assert counts["Progressive Hookshot"] == 2
    assert "Progressive Wallet" not in counts  # the small wallet is starting equipment
    counts = inv(world, ints=stock("Item_Quiver_Large")).counts
    assert "Progressive Quiver" not in counts  # a quiver without the bow is not the bow
    counts = inv(world, ints=stock("Item_Quiver_Large") | stock("Weapon_Range_Bow")).counts
    assert counts["Progressive Quiver"] == 3


# 5.2
@pytest.mark.parametrize(
    ("actor", "item"),
    [("Item_WeirdEgg", "Weird Egg"), ("Item_PoacherSaw", "Poachers Saw"), ("Weapon_Shield_Deku", "Deku Shield")],
)
def test_trade_items_and_shields_count_when_held_or_once_acquired(world, actor, item):
    assert inv(world, {f"IsGet.{actor}": True}, stock(actor)).counts[item] == 1
    assert inv(world, {f"IsGet.{actor}": True}, stock(actor, 0)).counts[item] == 1
    assert item not in inv(world, {f"IsGet.{actor}": False}, stock(actor, 0)).counts


def test_rutos_letter_counts_when_held_or_once_acquired(world):
    held, enums = bottles(LETTER)
    assert inv(world, held | {"IsGet.Item_Bottle_Letter": True}, enums=enums).counts["Rutos Letter"] == 1
    none, enums = bottles()
    assert inv(world, none | {"IsGet.Item_Bottle_Letter": True}, enums=enums).counts["Rutos Letter"] == 1
    assert "Rutos Letter" not in inv(world, none | {"IsGet.Item_Bottle_Letter": False}, enums=enums).counts


def test_items_without_an_acquired_once_rule_count_only_when_held(world):
    assert "Boomerang" not in inv(world, {"IsGet.Item_Boomerang": True}, stock("Item_Boomerang", 0)).counts
    assert inv(world, {"IsGet.Item_Boomerang": True}, stock("Item_Boomerang")).counts["Boomerang"] == 1


@pytest.mark.parametrize("remaining", [0, 10])
def test_bought_bombchus_need_the_bag_even_when_ever_acquired(remaining):
    world = logic_world(Settings())[1]
    bought = stock("Item_Bombchu", remaining) | {
        f"PouchData.Item_BombBag_{size}.StockNum": 0 for size in ("Small", "Medium", "Large")
    }
    history = {"IsGet.Item_Bombchu": True}
    before = inv(world, history, bought)
    assert "Bombchus" not in before.counts
    # Keep the inventory display truthful even when this stock cannot yet be used.
    cell = next(c for c in tracker_state.items(parse(history, bought)) if c["id"] == "bombchus")
    assert cell["count"] == remaining and cell["ever"] is True
    after = inv(world, history, bought | stock("Item_BombBag_Small"))
    assert after.counts["Bombchus"] == 1


# Q6: seed child logic takes the Goron Bracelet from Darunia's gift only. The tracker reads the gift from its cutscene's
# saved Bool (patch/darunia.py SOURCE); a copy Bracelet or adult gauntlets (the strength cell) never stand in for it.
DARUNIA = "HavePlayedEvent.Dm_Goron_0030"
STRENGTH = (("Armor_Child_Gauntlet_Goron", 1), ("Armor_Adult_Gauntlet_Silver", 2), ("Armor_Adult_Gauntlet_Gold", 3))


def test_goron_bracelet_comes_from_darunias_gift_only(world):
    gift = inv(world, {DARUNIA: True})
    assert gift.counts["Goron Bracelet"] == 1 and "Progressive Strength" not in gift.counts
    for actor, tier in STRENGTH:
        counts = inv(world, {DARUNIA: False}, stock(actor)).counts
        assert counts["Progressive Strength"] == tier and "Goron Bracelet" not in counts, actor
    unread = inv(world, ints=stock("Armor_Child_Gauntlet_Goron"))
    assert "Goron Bracelet" not in unread.counts and "story: Goron Bracelet" in unread.unknown
    # Were Darunia's gift ever shuffled, the flag would only say that check was done.
    darunia = Check("GC Darunias Joy", "Darunia", "", "Goron City", None, "gift", "x", "x", "named_bool", (DARUNIA,))
    shuffled = tracker_logic.inventory(seed([darunia]), parse({DARUNIA: True}, {}), world)
    assert "Goron Bracelet" not in shuffled.counts and "story: Goron Bracelet" not in shuffled.unknown


@pytest.mark.parametrize(
    ("actor", "item"), [("Item_DekuStick", "Buy Deku Stick (1)"), ("Item_DekuNut", "Buy Deku Nut (5)")]
)
def test_held_sticks_and_nuts_count_as_the_helpers_item(world, actor, item):
    # Sticks/Nuts (helpers.toml) read these names; a bought stick leaves only the stock behind.
    assert inv(world, {f"IsGet.{actor}": True}, stock(actor, 3)).counts[item] == 1
    # A new game marks nuts as found with none held, so the acquired-once flag alone is not having them.
    assert item not in inv(world, {f"IsGet.{actor}": True}, stock(actor, 0)).counts
    assert {"Deku Sticks", "Deku Nuts"} <= set(inv(world).unknown)
    assert "Deku Sticks" not in inv(world, ints=stock("Item_DekuStick", 0)).unknown


def test_sticks_open_the_wolfos_grotto_chest(world):
    # The reported seed: sticks bought in the Kokiri shop are what the Wolfos grotto chest needs as child.
    rule = world.locations["SFM Wolfos Grotto Chest"].rule
    assert "Buy Deku Stick (1)" in rule.reads


# 5.3
def test_small_keys_use_the_found_count_and_dungeon_flags(world):
    prefix = "DungeonInfo.ForestTemple."
    counts = inv(
        world,
        {prefix + "IsGetBossKey": True, prefix + "IsGetMap": False},
        {prefix + "SmallKeyNum": 1, prefix + "SmallKeyTotalNum": 4},
        small_keys={"Forest Temple": 5},
        boss_keys={"Forest Temple": 1},
    ).counts
    assert counts["Small Key (Forest Temple)"] == 4
    assert counts["Boss Key (Forest Temple)"] == 1


# 5.4
def test_unknown_cells_contribute_nothing_and_are_listed(world):
    result = inv(world, ints=stock("Item_Boomerang"))
    assert result.counts["Boomerang"] == 1
    assert "boomerang" not in result.unknown
    assert {"hookshot", "hammer", "bottles", "hearts", "tokens"} <= set(result.unknown)
    assert "Progressive Hookshot" not in result.counts
    assert list(result.unknown) == sorted(result.unknown)


def test_unknown_dungeon_items_are_listed_only_for_the_seeds_own(world):
    result = inv(world, small_keys={"Forest Temple": 5})
    assert "Forest Temple small keys" in result.unknown
    assert not [name for name in result.unknown if "Fire Temple" in name]


# 5.5
def test_bottles_follow_has_bottle():
    world = build_world(
        {
            "start": "Root",
            "goal": "Victory",
            "items": {"Bottle": {"bottle": True}, "Rutos Letter": {}},
            "regions": [
                {"name": "Root", "locations": {"Needs Bottle": {"rule": "has_bottle", "type": "Chest"}}},
            ],
        }
    )
    target = world.locations["Needs Bottle"]

    def counts_and_access(*contents, ever=False):
        bools, enums = bottles(*contents)
        result = inv(world, bools | {"IsGet.Item_Bottle_Letter": ever}, enums=enums)
        items = tracker_logic.search_items(result, world)
        return result.counts, Search(world, items).can_access(target)

    counts, access = counts_and_access(LETTER)
    assert counts == {"Rutos Letter": 1} and access is False
    counts, access = counts_and_access(LETTER, EMPTY)
    assert counts == {"Bottle": 1, "Rutos Letter": 1} and access is True
    counts, access = counts_and_access(LETTER, ever=True)
    assert counts["Rutos Letter"] == 1  # the letter is counted once, held and once acquired


# 5.6 (P5.a)
def test_inventory_is_a_sorted_deterministic_multiset(world):
    bools, enums = bottles(EMPTY, LETTER)
    ints = stock("Item_Hookshot") | stock("Item_Boomerang") | {"PlayerStatus.MaxLife": 24}
    one, two = inv(world, bools, ints, enums), inv(world, bools, ints, enums)
    assert one.as_json() == two.as_json()
    assert list(one.counts) == sorted(one.counts)
    assert json.loads(one.as_json())["counts"]["Piece of Heart"] == 12
    assert tracker_logic.search_items(one, world) == sorted(tracker_logic.search_items(one, world))


# 5.7: the closed age-return gate, on the tiny two-age world.
def test_save_items_go_to_the_search_as_the_generator_feeds_them():
    world = build_world(SPEC)
    assert world.age_return is not None
    result = inv(world, ints=stock("Item_Boomerang"))
    items = tracker_logic.search_items(result, world)
    assert items == ["Boomerang"]
    direct = Search(world, items)
    logic = tracker_logic.SeedLogic(tracker_logic.LogicWorld(True, None, Settings(), world))
    tracker = logic.search(result)
    for location in world.locations.values():
        for age in (CHILD, ADULT, None):
            assert tracker.can_access(location, age) == direct.can_access(location, age), (location.name, age)
    # The child-only ledge is reached with the save's Boomerang, though the return gate is closed.
    assert tracker.can_access(world.locations["Ledge Chest"], CHILD)
    assert not tracker.holds("Forest Clear")


# 5.8 (P5.b)
def test_starting_items_are_not_counted_twice():
    world = build_world(SPEC)
    world.start_items = ("Boomerang",)
    held = inv(world, ints=stock("Item_Boomerang"))
    assert held.counts == {"Boomerang": 1}
    assert tracker_logic.search_items(held, world) == []
    assert Search(world, tracker_logic.search_items(held, world)).counts["Boomerang"] == 1
    # Two held beyond one starting copy: one more is fed, so the search counts the larger of the two.
    beans = build_world({**SPEC, "items": {**SPEC["items"], "Magic Bean": {}}})
    beans.start_items = ("Magic Bean",)
    fed = tracker_logic.search_items(inv(beans, ints=stock("Item_MagicBean", 3)), beans)
    assert Counter(fed) == Counter({"Magic Bean": 2})
    assert Search(beans, fed).counts["Magic Bean"] == 3
