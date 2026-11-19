"""Consumer-visible reward/completion separation and source-preserving native grants."""

from collections import Counter
from copy import deepcopy
from dataclasses import replace

import pytest

from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import allowed, shuffled_locations
from clawshot.generate.rewards import catalog
from clawshot.patch import rewards
from clawshot.world.load import load_spec


@pytest.fixture(scope="module")
def reward_world():
    return prepare(load_spec(), Settings(dungeon_rewards=True))


def test_rewards_are_exclusively_reward_slots(reward_world):
    settings, world = reward_world
    slots = catalog()["slots"]
    assert set(slots).issubset(shuffled_locations(world, settings))
    for name in world.locations:
        if name in slots:
            assert not allowed(world, settings, name, "Boomerang")
        else:
            for slot in slots.values():
                assert not allowed(world, settings, name, slot["item"]), (name, slot["item"])
    for source in slots:
        for slot in slots.values():
            assert allowed(world, settings, source, slot["item"])


def test_owned_door_is_separate_from_native_completion_readers(reward_world):
    _, world = reward_world
    all_rewards = Counter({slot["item"]: 1 for slot in catalog()["slots"].values()})
    door = next(edge.rule for edge in world.regions["Temple of Time"].exits if edge.target == "Beyond Door of Time")
    kit = Counter({"Ocarina": 2, "Song of Time": 1, "Met Child Zelda": 1})
    assert door(kit + all_rewards, "child", 1)
    completed = Counter({f"Defeat {boss}": 1 for boss in ("Queen Gohma", "King Dodongo", "Barinade")})
    assert not door(kit + completed, "child", 1)
    assert not door(kit + Counter({"Kokiri Emerald": 3}), "child", 1)
    for missing in kit:
        without = kit.copy()
        del without[missing]
        assert not door(without + all_rewards, "child", 1), missing
    assert not door(Counter({"Ocarina": 1, "Song of Time": 1, "Met Child Zelda": 1}) + all_rewards, "child", 1)
    moat_completed = Counter({"Defeat King Dodongo": 1, "Defeat Barinade": 1})
    for name in ("HF Ocarina of Time Item", "Song from Ocarina of Time"):
        assert not world.locations[name].rule(kit + all_rewards, "child", 1), name
        assert world.locations[name].rule(kit + moat_completed, "child", 1), name
    lacs = world.locations["ToT Light Arrows Cutscene"].rule
    assert not lacs(all_rewards, "adult", 1)
    last_sages = Counter({"Defeat Bongo Bongo": 1, "Defeat Twinrova": 1})
    assert lacs(last_sages, "adult", 1)
    prelude = world.locations["Sheik at Temple"].rule
    assert not prelude(all_rewards, "adult", 1)
    assert prelude(Counter({"Defeat Phantom Ganon": 1}), "adult", 1)


def test_bridge_story_is_not_light_arrow_ownership(reward_world):
    _, world = reward_world
    bridge = next(
        edge.rule for edge in world.regions["Ganons Castle Grounds"].exits if edge.target == "Ganons Castle Ledge"
    )
    assert not bridge(Counter({"Shadow Medallion": 1, "Spirit Medallion": 1, "Light Arrows": 1}), "adult", 1)
    assert bridge(Counter({"Defeat Bongo Bongo": 1, "Defeat Twinrova": 1, "Clawshot Light Arrow Story": 1}), "adult", 1)
    for event in world.events:
        if event.name.endswith("Trial Clear"):
            assert not event.rule(Counter(), "adult", 1), event.name


def test_return_guarantee_remembers_owned_stones_not_optional_completions(reward_world):
    from clawshot.generate.fill import return_guarantee_conflict

    settings, world = reward_world
    inventory = world.settings["age_return_fill_inventory"]
    door = next(edge.rule for edge in world.regions["Temple of Time"].exits if edge.target == "Beyond Door of Time")
    assert door(inventory, "child", 1), inventory
    assert not any(name.startswith("Defeat ") for name in inventory), inventory
    assert return_guarantee_conflict(world, settings) is None
    _, early = prepare(load_spec(), Settings(dungeon_rewards=True, door_of_time="open"))
    assert not any(name.startswith("Defeat ") for name in early.settings["age_return_fill_inventory"])


@pytest.mark.parametrize("mode,maximum", [("stones", 3), ("medallions", 6), ("rewards", 9)])
def test_bridge_settings_count_bounds_and_codec(mode, maximum):
    settings = Settings(dungeon_rewards=True, bridge=mode, bridge_count=maximum)
    assert Settings.from_string(settings.to_string()) == settings
    for count in (-1, maximum + 1, True, 1.5):
        with pytest.raises(ValueError, match="bridge_count"):
            replace(settings, bridge_count=count)


def synthetic_flow(slot):
    return evfl.EventFlowFile(
        slot["flow"],
        evfl.Flowchart(
            slot["flow"],
            actors=[evfl.Actor("GameSystemActor", actions=["EventTriggerZeldaNotesRequestSendDailyScreenShot"])],
            events=[
                evfl.SubFlowEvent(
                    slot["event"], "GetPouchContent", "GetPouchContentByActorName", params={"ActorName": slot["actor"]}
                ),
                evfl.ActionEvent(
                    slot["notes"], 0, 0, params={"TypeID": "get_item", "TargetID": slot["actor"], "Frame": 2}
                ),
                evfl.SubFlowEvent("Completion", "NativeSage", "Finish"),
            ],
            entry_points=[evfl.EntryPoint("Start", 0)],
        ),
    )


@pytest.mark.parametrize("slot", list(catalog()["slots"].values()), ids=list(catalog()["slots"]))
def test_reward_swap_preserves_completion_and_presentation_bindings(slot):
    doc = synthetic_flow(slot)
    before = deepcopy(doc)
    actor = "Item_Stone_Water" if slot["actor"] != "Item_Stone_Water" else "Item_Medal_Light"
    result = evfl.read(rewards.transform(slot, actor)(evfl.write(doc)))
    assert result.flowchart.events[0].params == {"ActorName": actor}
    assert result.flowchart.events[1].params["TargetID"] == actor
    result.flowchart.events[0].params = before.flowchart.events[0].params
    result.flowchart.events[1].params = before.flowchart.events[1].params
    assert result == before


@pytest.mark.dump
def test_native_all_reward_grants_change_only_the_awarded_identity(romfs):
    slots = catalog()["slots"]
    items = [slot["item"] for slot in slots.values()]
    placements = dict(zip(slots, items[1:] + items[:1], strict=True))
    changes = rewards.changes(romfs, placements)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for name, slot in slots.items():
        for version in ("", ".110") if "version" in slot else ("",):
            path = f"Event/EventFlow/{slot['flow']}{version}.bfevfl.zs"
            raw = dictionaries.decompress(path, (romfs / path).read_bytes())
            before = evfl.read(raw)
            after = evfl.read(changes[path](raw))
            for event in after.flowchart.events:
                if event.name == slot["event"]:
                    assert event.params == {
                        "ActorName": next(s["actor"] for s in slots.values() if s["item"] == placements[name])
                    }
                    event.params = {"ActorName": slot["actor"]}
                elif event.name == slot["notes"]:
                    event.params["TargetID"] = slot["actor"]
            assert after == before, path
