"""Light Arrow story follows awakening completion, never shuffled reward ownership."""

from collections import Counter

import pytest

from clawshot.generate import Settings, prepare
from clawshot.world import ADULT, CHILD, build_world, load_spec


@pytest.mark.parametrize("rewards", [False, True])
@pytest.mark.parametrize("bridge", ["vanilla", "stones", "medallions", "rewards"])
def test_light_arrow_scene_requires_both_native_completions_not_owned_rewards(rewards, bridge):
    _, world = prepare(load_spec(), Settings(dungeon_rewards=rewards, bridge=bridge))
    rule = world.locations["ToT Light Arrows Cutscene"].rule
    medals = Counter({f"{name} Medallion": 1 for name in ("Light", "Forest", "Fire", "Water", "Shadow", "Spirit")})
    assert not rule(medals, ADULT, 1)
    completed = Counter({"Defeat Bongo Bongo": 1, "Defeat Twinrova": 1})
    assert rule(completed, ADULT, 1)
    assert not rule(completed, CHILD, 1)
    for missing in completed:
        without = completed.copy()
        del without[missing]
        assert not rule(without + medals, ADULT, 1), missing


def test_direct_world_and_default_bridge_separate_story_from_light_arrows():
    world = build_world(load_spec())
    story = next(event.rule for event in world.events if event.name == "Clawshot Light Arrow Story")
    completed = Counter({"Defeat Bongo Bongo": 1, "Defeat Twinrova": 1})
    assert story(completed, ADULT, 1)
    assert not story(Counter({"Shadow Medallion": 1, "Spirit Medallion": 1}), ADULT, 1)
    bridge = next(
        edge.rule for edge in world.regions["Ganons Castle Grounds"].exits if edge.target == "Ganons Castle Ledge"
    )
    assert not bridge(completed + Counter({"Light Arrows": 1}), ADULT, 1)
    assert bridge(completed + Counter({"Clawshot Light Arrow Story": 1}), ADULT, 1)


@pytest.mark.parametrize("rewards", [False, True])
@pytest.mark.parametrize(
    "event_name",
    [f"{trial} Trial Clear" for trial in ("Forest", "Fire", "Water", "Shadow", "Spirit", "Light")] + ["Triforce"],
)
def test_all_trials_and_finale_still_require_usable_light_arrows(rewards, event_name):
    _, world = prepare(load_spec(), Settings(dungeon_rewards=rewards))
    inventory = Counter({name: 20 for name in world.items if name != "Light Arrows"})
    rule = next(event.rule for event in world.events if event.name == event_name)
    assert not rule(inventory, ADULT, 1), rule.text
    assert rule(inventory + Counter({"Light Arrows": 1}), ADULT, 1), rule.text
