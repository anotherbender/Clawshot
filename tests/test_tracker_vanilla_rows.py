"""Vanilla rows (spec tracker-in-logic D19, section 8): fixed vanilla pick-ups the seed does not shuffle, on a tiny
synthetic world. Nothing comes from the game."""

import copy
import json
from types import SimpleNamespace

import pytest
from test_tracker_logic import GENERATOR, PLACES
from test_tracker_state import build_save, parse

from clawshot.generate import Settings
from clawshot.generate.fill import shuffled_locations
from clawshot.patch.logic_world import logic_world
from clawshot.tracker import TrackerSession, build_state, load_seed, seeds
from clawshot.tracker import logic as tracker_logic
from clawshot.tracker.seeds import Place

BOOMERANG = "PouchData.Item_Boomerang.StockNum"

# test_tracker_logic's world plus fixed pick-ups: the child's Boomerang (which opens the Child Ledge, like Ruto's
# Letter opens Jabu-Jabu), two Lens pick-ups (an item given twice, which an event reads), a non-progression trinket
# and a progression item no rule reads (like a seed's fixed Silver Scale).
SPEC = copy.deepcopy(__import__("test_tracker_logic").SPEC)
SPEC["items"] |= {"Lens of Truth": {}, "Trinket": {"class": "normal"}, "Bonus Scale": {}}
SPEC["regions"][1]["locations"] |= {
    "Boomerang Pickup": {"rule": "age == 'child'", "type": "NPC", "vanilla": "Boomerang"},
    "Lens Pickup A": {"rule": "True", "type": "NPC", "vanilla": "Lens of Truth"},
    "Lens Pickup B": {"rule": "True", "type": "NPC", "vanilla": "Lens of Truth"},
    "Trinket Pickup": {"rule": "True", "type": "NPC", "vanilla": "Trinket"},
    "Bonus Pickup": {"rule": "True", "type": "NPC", "vanilla": "Bonus Scale"},
}
SPEC["regions"][1]["events"] |= {"Truth Seen": "'Lens of Truth'"}
# The Boomerang is not shuffled: only its vanilla pick-up gives it.
PLACEMENTS = {
    "Adult Chest": "Key",
    "Child Chest": "Hookshot",
    "Boomerang Chest": "Rupees (5)",
    "Ledge Chest": "Rupees (5)",
}
VANILLA_PLACES = PLACES | {"Boomerang Pickup": Place("Lake", None, "NPC")}


@pytest.fixture
def world(monkeypatch):
    monkeypatch.setattr(seeds, "location_index", lambda: VANILLA_PLACES)
    monkeypatch.setattr(tracker_logic, "world_spec", lambda: SPEC)
    return SPEC


def write_seed(tmp_path, placements=PLACEMENTS, *, generator=GENERATOR, name="seed-1"):
    root = tmp_path / name
    (root / "seed").mkdir(parents=True)
    spoiler = {
        "generator": generator,
        "seed": 1,
        "settings_string": Settings().to_string(),
        "settings": {"shuffle": ["Chest"]},
        "placements": placements,
        "locations": {
            name: {"name": name, "where": "Field", "ids": [str(100 + i)]} for i, name in enumerate(placements)
        },
    }
    (root / "seed" / "spoiler.json").write_text(json.dumps(spoiler), encoding="utf-8")
    (root / "clawshot-seed.json").write_text(json.dumps({"seed": 1, "output_sha256": "ef" * 32}), encoding="utf-8")
    return root


def state_for(tmp_path, ints=None, *, placements=PLACEMENTS, marks=frozenset(), name="seed-1", logic=None):
    seed = load_seed(write_seed(tmp_path, placements, name=name))
    logic = logic or tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    return build_state(seed, parse({}, ints or {}), logic=logic, marks=marks), seed, logic


def shuffled(state):
    return {check["id"]: check for area in state["areas"] for check in area["checks"]}


def vanilla(state):
    return {check["id"]: check for area in state["vanilla_areas"] for check in area["checks"]}


# 16.2 (8.1)
def test_rows_are_unshuffled_unique_progression_pick_ups(tmp_path, world):
    state, seed, logic = state_for(tmp_path, {BOOMERANG: 0})
    assert list(vanilla(state)) == ["Boomerang Pickup"]
    every = tracker_logic.vanilla_rows(seed, logic.loaded.world, "all")
    assert [row.location for row in every] == ["Boomerang Pickup", "Lens Pickup A", "Lens Pickup B"]
    with pytest.raises(ValueError, match="scope"):
        tracker_logic.vanilla_rows(seed, logic.loaded.world, "some")


# B1: a row only for an item the seed's logic reads; any other cannot change what is in logic.
def test_an_item_no_rule_reads_gets_no_row(tmp_path, world, monkeypatch):
    state, seed, logic = state_for(tmp_path, {BOOMERANG: 0})
    world = logic.loaded.world
    reads = tracker_logic.logic_reads(world)
    assert {"Boomerang", "Lens of Truth"} <= reads and "Bonus Scale" not in reads
    assert "Bonus Pickup" not in vanilla(state)
    assert "Bonus Pickup" not in {row.location for row in tracker_logic.vanilla_rows(seed, world, "all")}
    monkeypatch.setattr(tracker_logic, "logic_reads", lambda world: None)  # reads unknown: nothing is ruled out
    assert "Bonus Pickup" in {row.location for row in tracker_logic.vanilla_rows(seed, world)}


@pytest.fixture(scope="module")
def chest_only():
    """A Chest-only seed's real logic world (dump-free) and a seed whose checks are its shuffled locations."""
    settings, world = logic_world(Settings(shuffle=("Chest",)))
    names = shuffled_locations(world, settings)
    return SimpleNamespace(checks=[SimpleNamespace(location=name, item="Rupees (5)") for name in names]), world


# B1 on a seed's world: the native chains count only copies, so their fixed tiers are a bonus no rule reads.
IGNORED_TIERS = {
    "ZD Diving Minigame": "Silver Scale",
    "LH Adult Fishing": "Golden Scale",
    "Kak 10 Gold Skulltula Reward": "Adult Wallet",
    "Kak 30 Gold Skulltula Reward": "Giant Wallet",
    "HC Great Fairy Reward": "Magic Meter (Single)",
    "DMC Great Fairy Reward": "Magic Meter (Double)",
}


def test_fixed_native_tiers_the_logic_ignores_get_no_row(chest_only, monkeypatch):
    seed, world = chest_only
    assert world.progressive_copies_only
    reads = tracker_logic.logic_reads(world)
    assert reads is not None and "Progressive Scale" in reads
    rows = {row.location: row.item for row in tracker_logic.vanilla_rows(seed, world)}
    for location, item in IGNORED_TIERS.items():
        assert world.locations[location].vanilla == item and item not in reads
        assert location not in rows, location
    # Fixed gates the logic reads keep their rows.
    assert rows["LH Underwater Item"] == "Rutos Letter"
    assert rows["GC Darunias Joy"] == "Goron Bracelet"
    assert rows["LLR Talons Chickens"] == "Bottle with Milk"  # has_bottle reads every bottle
    # Without the filter the ignored tiers would be rows: the test is not vacuous.
    monkeypatch.setattr(tracker_logic, "logic_reads", lambda world: None)
    assert set(IGNORED_TIERS) <= {row.location for row in tracker_logic.vanilla_rows(seed, world)}


def test_search_counts_follow_the_search(chest_only):
    _, world = chest_only
    # A fixed Bow is a bonus in a copies-only world: the search keeps the name for its chain copies.
    assert tracker_logic.search_counts(world, "Bow") == frozenset()
    assert tracker_logic.search_counts(world, "Fairy Ocarina") == {"Fairy Ocarina", "Ocarina"}
    assert tracker_logic.search_counts(world, "Silver Scale") == {"Silver Scale"}


def test_rows_are_built_once_per_loaded_seed(tmp_path, world, monkeypatch):
    calls, readings = [], []
    real, real_sources = tracker_logic.vanilla_rows, tracker_logic._unknown_sources
    monkeypatch.setattr(tracker_logic, "vanilla_rows", lambda *a: calls.append(1) or real(*a))
    # How each row's item is read from the inventory is worked out with the rows, not again on every poll.
    monkeypatch.setattr(tracker_logic, "_unknown_sources", lambda m: readings.append(1) or real_sources(m))
    _, seed, logic = state_for(tmp_path, {BOOMERANG: 0})
    for held in (0, 1, 0):
        build_state(seed, parse({}, {BOOMERANG: held}), logic=logic)
    assert len(calls) == 1 and len(readings) == 1


def test_no_rows_while_logic_is_unavailable(tmp_path, world):
    seed = load_seed(write_seed(tmp_path, generator="clawshot 0.0.0"))
    logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    state = build_state(seed, parse({}, {BOOMERANG: 0}), logic=logic)
    assert state["logic"]["available"] is False and "vanilla_areas" not in state


# 16.3 (8.2)
def test_a_row_names_its_place_and_item_without_spoilers(tmp_path, world):
    state, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    assert state["show_locations"] is False
    row = vanilla(state)["Boomerang Pickup"]
    assert row | {"in_logic": None} == {
        "id": "Boomerang Pickup",
        "label": "Boomerang Pickup",
        "where": "",
        "kind": "other",
        "dungeon": None,
        "collected": False,
        "basis": "inventory",
        "vanilla": True,
        "item": "Boomerang",
        "item_label": "Boomerang",
        "skippable": True,  # round 21: read as not held, so the player may skip it
        "in_logic": None,
    }
    assert [area["name"] for area in state["vanilla_areas"]] == ["Lake"]


# 16.4, 16.6 (8.3, 8.4): the gate is open and in logic, the gated check out; holding the item flips both.
def test_a_fixed_gate_item_shows_open_then_collected(tmp_path, world):
    before, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    row = vanilla(before)["Boomerang Pickup"]
    assert row["collected"] is False
    assert row["in_logic"] == {"child": True, "adult": False, "either": True}
    assert shuffled(before)["Ledge Chest"]["in_logic"]["child"] is False
    assert before["vanilla_areas"][0]["in_logic"] == {"child": 1, "adult": 0, "either": 1}

    after, _, _ = state_for(tmp_path, {BOOMERANG: 1}, name="held")
    row = vanilla(after)["Boomerang Pickup"]
    assert row["collected"] is True and "in_logic" not in row
    assert shuffled(after)["Ledge Chest"]["in_logic"]["child"] is True
    assert after["vanilla_areas"][0]["collected"] == 1


def test_an_unreadable_item_is_unknown_with_a_reason(tmp_path, world):
    state, _, _ = state_for(tmp_path)  # no Boomerang stock in the save
    row = vanilla(state)["Boomerang Pickup"]
    assert row["collected"] is None and row["basis"] is None and "could not be read" in row["reason"]
    assert "in_logic" in row  # unknown and unmarked is open (3.1)


# S1: a shuffled check can give the item when one of the shuffled locations' own (vanilla) items is it: the pool the
# settings give. The items the spoiler placed are never read, so rows depend on the settings only.
def test_an_item_a_shuffled_check_can_give_is_unknown(tmp_path, world, monkeypatch):
    spec = copy.deepcopy(SPEC)
    spec["regions"][1]["locations"]["Child Chest"]["vanilla"] = "Lens of Truth"  # a shuffled check's own item
    monkeypatch.setattr(tracker_logic, "world_spec", lambda: spec)
    _, seed, logic = state_for(tmp_path, {BOOMERANG: 1})
    world = logic.loaded.world
    rows = {row.location: row for row in tracker_logic.vanilla_rows(seed, world, "all")}
    assert rows["Lens Pickup A"].shared and rows["Lens Pickup B"].shared and not rows["Boomerang Pickup"].shared
    inv = tracker_logic.Inventory({"Lens of Truth": 1}, ())
    collected, reason = tracker_logic.vanilla_collected(rows["Lens Pickup A"], inv, world)
    assert collected is None and "shuffled check" in reason


def test_rows_never_read_the_placed_items(tmp_path, world):
    plain, seed, logic = state_for(tmp_path, {BOOMERANG: 1})
    # The same shuffled locations with other items: the Boomerang now in a chest, per the spoiler.
    placements = PLACEMENTS | {"Boomerang Chest": "Boomerang"}
    moved, other, _ = state_for(tmp_path, {BOOMERANG: 1}, placements=placements, name="moved")
    world = logic.loaded.world
    assert tracker_logic.vanilla_rows(seed, world, "all") == tracker_logic.vanilla_rows(other, world, "all")
    assert vanilla(plain) == vanilla(moved) and vanilla(moved)["Boomerang Pickup"]["collected"] is True


def test_a_tier_is_shared_only_by_a_check_that_can_reach_it(chest_only):
    seed, world = chest_only
    # Saria's Fairy Ocarina (Ocarina 1) shuffled cannot give the Ocarina of Time (Ocarina 2), and the reverse can.
    saria = SimpleNamespace(checks=[*seed.checks, SimpleNamespace(location="LW Gift from Saria", item="Rupees (5)")])
    rows = {row.location: row for row in tracker_logic.vanilla_rows(saria, world)}
    assert "LW Gift from Saria" not in rows and rows["HF Ocarina of Time Item"].shared is False
    drawbridge = SimpleNamespace(checks=[*seed.checks, SimpleNamespace(location="HF Ocarina of Time Item", item="x")])
    rows = {row.location: row for row in tracker_logic.vanilla_rows(drawbridge, world)}
    assert "HF Ocarina of Time Item" not in rows and rows["LW Gift from Saria"].shared is True


def bare_seed():
    """A tracker seed with no shuffled checks, for reading synthetic saves into the logic inventory."""
    folder = seeds.Path("seed")
    return seeds.Seed(folder, folder, folder / "spoiler.json", None, "raw", {}, ())


# 8.3 (16.4): a fixed tier counts once its chain reaches it. In a seed's world only the Ocarina keeps fixed tiers
# (Fairy Ocarina = Ocarina 1, Ocarina of Time = Ocarina 2), and the save's ocarina cell shows the highest one held.
FAIRY, TIME = "PouchData.Item_Ocarina_Fairy.StockNum", "PouchData.Item_Ocarina_Time.StockNum"


def test_a_fixed_tier_counts_its_chain(chest_only):
    seed, world = chest_only
    rows = {row.location: row for row in tracker_logic.vanilla_rows(seed, world)}
    fairy, time = rows["LW Gift from Saria"], rows["HF Ocarina of Time Item"]
    assert world.items[fairy.item].alias == ("Ocarina", 1) and world.items[time.item].alias == ("Ocarina", 2)
    assert world.items[fairy.item].tier and world.items[time.item].tier

    def collected(ints):
        inv = tracker_logic.inventory(bare_seed(), parse({}, ints), world)
        return [tracker_logic.vanilla_collected(row, inv, world) for row in (fairy, time)]

    assert collected({FAIRY: 0, TIME: 0}) == [(False, None), (False, None)]
    assert collected({FAIRY: 1, TIME: 0}) == [(True, None), (False, None)]
    # The Ocarina of Time replaces Saria's ocarina in the save: her row still counts as taken.
    assert collected({FAIRY: 0, TIME: 1}) == [(True, None), (True, None)]
    assert [state for state, _ in collected({})] == [None, None]  # the ocarina cell was not read


# Q6: Darunia's row reads the gift's cutscene flag (HavePlayedEvent.Dm_Goron_0030); a copy Bracelet does not count.
def test_darunias_gift_row_reads_its_cutscene_flag(chest_only):
    seed, world = chest_only
    [row] = [row for row in tracker_logic.vanilla_rows(seed, world) if row.location == "GC Darunias Joy"]

    def collected(bools, ints=None):
        inv = tracker_logic.inventory(bare_seed(), parse(bools, ints or {}), world)
        return tracker_logic.vanilla_collected(row, inv, world)

    assert collected({"HavePlayedEvent.Dm_Goron_0030": True}) == (True, None)
    copy_bracelet = {"PouchData.Armor_Child_Gauntlet_Goron.StockNum": 1}
    assert collected({"HavePlayedEvent.Dm_Goron_0030": False}, copy_bracelet) == (False, None)
    assert collected({}, copy_bracelet)[0] is None  # the flag was not read


# 16.5 (8.3): unknown rows take manual marks like any unknown check, and a save-confirmed state drops the mark.
@pytest.fixture
def marks_folder(tmp_path, monkeypatch):
    from clawshot.app import preferences

    prefs = tmp_path / "prefs"
    monkeypatch.setattr(preferences, "user_preferences_path", lambda: prefs / "paths.json")
    return prefs


def test_unknown_rows_can_be_marked_and_known_rows_cannot(tmp_path, world, marks_folder):
    root = write_seed(tmp_path)
    progress = root / "user" / "save" / "1" / "slot_00" / "progress.sav"
    progress.parent.mkdir(parents=True)
    progress.write_bytes(build_save({}))  # no Boomerang stock: the row is unknown
    session = TrackerSession()
    session.configure(root)
    session.mark("Boomerang Pickup", True)
    row = vanilla(session.snapshot()["state"])["Boomerang Pickup"]
    assert row["marked"] is True and "in_logic" not in row
    assert session.snapshot()["state"]["vanilla_areas"][0]["marked"] == 1

    progress.write_bytes(build_save({}, {BOOMERANG: 1}))
    import os

    stat = progress.stat()
    os.utime(progress, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))
    row = vanilla(session.snapshot()["state"])["Boomerang Pickup"]
    assert row["collected"] is True and "marked" not in row
    with pytest.raises(ValueError, match="already says"):
        session.mark("Boomerang Pickup", True)


# 16.7 (8.5): the seed's own checks and area counts are the same with and without vanilla rows.
def test_shuffled_checks_and_area_counts_are_unchanged(tmp_path, world, monkeypatch):
    with_rows, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    monkeypatch.setattr(tracker_logic, "vanilla_rows", lambda *a: ())
    without, _, _ = state_for(tmp_path, {BOOMERANG: 0}, name="without")
    assert without["vanilla_areas"] == [] and with_rows["vanilla_areas"]
    assert with_rows["areas"] == without["areas"]
    assert with_rows["skulltula_checks"] == without["skulltula_checks"]


# 16.9 (8.7)
def test_obs_payload_has_no_vanilla_rows(tmp_path, world, marks_folder):
    from clawshot.ui.tracker import TrackerController

    root = write_seed(tmp_path)
    progress = root / "user" / "save" / "1" / "slot_00" / "progress.sav"
    progress.parent.mkdir(parents=True)
    progress.write_bytes(build_save({}, {BOOMERANG: 0}))
    controller = TrackerController()
    controller.session = TrackerSession()
    controller.session.configure(root)
    assert controller.snapshot()["state"]["vanilla_areas"]
    obs = controller.snapshot(obs=True)
    assert "vanilla_areas" not in obs["state"] and "Boomerang Pickup" not in json.dumps(obs)


# 16.10 (P14.a)
def test_same_seed_and_save_give_equal_json(tmp_path, world):
    first, _, _ = state_for(tmp_path, {BOOMERANG: 0})
    second, _, _ = state_for(tmp_path, {BOOMERANG: 0}, name="again")
    for state in (first, second):
        state["seed"].pop("root"), state["seed"].pop("seed_dir")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
