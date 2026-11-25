"""Played first-race recovery admits progression; native tool admission and other holds remain."""

import pytest
from dampe_flow import FOREST, STEPS, assert_first_race_cycle, play

from clawshot.formats import byml, evfl
from clawshot.formats.zsdic import Dictionaries
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import allowed
from clawshot.patch import dampe_first_race, dampe_safety
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.save import key
from clawshot.world import load_spec

FIRST_RACE = "Graveyard Dampe Race Hookshot Chest"
SECOND_RACE = "Graveyard Dampe Race Freestanding PoH"
SHUFFLES = [("Chest",), ("Chest", "Freestanding", "NPC", "Token", "Song")]


@pytest.mark.parametrize("shuffle", SHUFFLES)
@pytest.mark.parametrize("item", ["Progressive Hookshot", "Progressive Quiver", "Progressive Magic"])
def test_played_first_race_accepts_progression_in_production(shuffle, item):
    settings, world = prepare(load_spec(), Settings(shuffle=shuffle))
    assert world.items[item].progression
    assert allowed(world, settings, FIRST_RACE, item)
    assert allowed(world, settings, FIRST_RACE, "Rupees (5)")


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_the_second_race_chest_is_not_restricted(shuffle):
    _settings, world = prepare(load_spec(), Settings(shuffle=shuffle))
    assert "Progressive Hookshot" not in world.locations[SECOND_RACE].excluded_items


@pytest.mark.dump
def test_native_first_race_recovers_every_tier_and_prior_second_race(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    fc = evfl.read(dampe_first_race.patch(dampe_safety.patch(raw))).flowchart
    assert_first_race_cycle(fc)


@pytest.mark.dump
def test_first_race_forest_writes_advance_early_steps_without_regressing_late_steps(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    fc = evfl.read(dampe_first_race.patch(raw)).flowchart
    for step in STEPS:
        state = {FOREST: step, dampe_first_race.CHEST_OPEN: False, "Npc_HaveTalked": False}
        play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, {"Item_Hookshot"})
        assert state[FOREST] == ("Step03" if STEPS.index(step) <= STEPS.index("Step03") else step), state


@pytest.mark.dump
def test_race_repair_preserves_native_prizes_and_every_unrelated_action(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    before = evfl.read(raw).flowchart
    after = evfl.read(dampe_first_race.patch(raw)).flowchart
    selectors = {
        "Event0",
        "Event18",
        "Event61",
        "Event98",
        "Event129",
        "Event157",
        "Event260",
        "Event262",
        "Event277",
        "Event442",
        "Event443",
        "Event444",
    }
    changed = selectors | {"Event97", "Event132"}
    for original, patched in zip(before.events, after.events, strict=False):
        if original.name not in changed:
            assert patched == original, original.name
        elif original.name in selectors:
            assert patched.cases == original.cases, original.name
    for entry in before.entry_points:
        patched = after.entry_point(entry.name)
        assert patched.sub_flow_events == entry.sub_flow_events, entry.name
        if entry.name != "Result":
            assert patched == entry, entry.name


@pytest.mark.dump
def test_collection_gate_is_an_existing_permanent_chest_flag_and_forest_guards_exist(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    data = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))["Data"]
    root = next(row for row in data["Struct"] if row["Hash"] == key("IsTreasureBoxOpen"))
    member = next(row for row in root["DefaultValue"] if row["Hash"] == key("16041366920820397198"))
    leaf = next(row for row in data["Bool"] if row["Hash"] == member["Value"])
    assert (leaf["DefaultValue"], leaf["ResetTypeValue"], leaf["SaveFileIndex"]) == (False, 24, 0), leaf
    forest = next(row for row in data["Enum"] if row["Hash"] == key("Step_SageOfForest"))
    assert tuple(forest["RawValues"]) == STEPS
    for step in ("Step02", "Step03"):
        expression = next(row for row in data["BoolExp"] if row["Hash"] == key(f"SageOfForest_IsAfter_{step}_Exp"))
        assert expression["Values"] == [[12, key("Step_SageOfForest")], [2, key(step)]], expression
