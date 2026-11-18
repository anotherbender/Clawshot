"""Kaepora's optional dialogue omission must preserve every other path and both flights."""

from copy import deepcopy

import pytest

from clawshot.formats import evfl
from clawshot.formats.zsdic import Dictionaries
from clawshot.patch import owl_skips


def projected(fc, omitted=()):
    """Compare control-flow by stable names, erasing only the specified speech nodes."""
    missing = set(omitted)

    def target(index):
        while index != evfl.NONE and fc.events[index].name in missing:
            index = fc.events[index].next
        return None if index == evfl.NONE else fc.events[index].name

    nodes = {}
    for event in fc.events:
        if event.name in missing:
            continue
        node = deepcopy(event)
        if hasattr(node, "next"):
            node.next = target(node.next)
        if hasattr(node, "cases"):
            node.cases = [(value, name) for value, index in node.cases if (name := target(index)) is not None]
        if isinstance(node, evfl.ForkEvent):
            node.join = target(node.join)
            node.forks = [name for index in node.forks if (name := target(index)) is not None]
        nodes[event.name] = node
    entries = {
        entry.name: (target(entry.main_event), [fc.events[i].name for i in entry.sub_flow_events], entry.variables)
        for entry in fc.entry_points
    }
    return nodes, entries


def test_omitting_a_fork_speech_leaf_keeps_its_flag_branch():
    fc = evfl.Flowchart(
        "Example",
        actors=[evfl.Actor("Npc_Kaepora", actions=["EventTalk"]), evfl.Actor("GameDataActor", actions=["SetFlag"])],
        events=[
            evfl.ForkEvent("Fork", 3, [1, 2]),
            evfl.ActionEvent("Speech", 0, 0, params={"ChoiceNumber": 0}),
            evfl.ActionEvent("Flag", 1, 0, params={"Value": True}),
            evfl.JoinEvent("Join"),
        ],
        entry_points=[evfl.EntryPoint("Main", 0)],
    )
    scene = owl_skips.OwlScene("Example", "Npc_Kaepora", ("Speech",))
    result = evfl.read(owl_skips.omit_lines(evfl.write(evfl.EventFlowFile("Example", fc)), scene)).flowchart
    assert projected(result) == projected(fc, scene.lines)
    assert result.events[0].forks == [1]
    assert result.events[1].params == {"Value": True}


@pytest.mark.dump
@pytest.mark.parametrize("scene", owl_skips.SCENES, ids=lambda scene: scene.flow)
def test_native_owl_skip_preserves_every_non_dialogue_action_and_edge(romfs, scene):
    dictionaries = Dictionaries.from_romfs(romfs)
    original = dictionaries.decompress(scene.path, (romfs / scene.path).read_bytes())
    before = evfl.read(original).flowchart
    after = evfl.read(owl_skips.omit_lines(original, scene)).flowchart
    expected, entries = projected(before, scene.lines)
    for offer, donor in scene.shorter:
        expected[offer].params[owl_skips.MESSAGE] = expected[donor].params[owl_skips.MESSAGE]
    assert after.actors == before.actors
    assert projected(after) == (expected, entries)
    talks = [
        e
        for e in after.events
        if isinstance(e, evfl.ActionEvent)
        and after.actors[e.actor].name == scene.speaker
        and after.actors[e.actor].actions[e.action] == owl_skips.TALK
    ]
    assert {event.name for event in talks} == set(scene.offers)
    assert all(event.params[owl_skips.CHOICES] > 0 for event in talks)
    # A/S and all visit/meet/history writes remain native actions/caller effects;
    # the omission cannot remove or reorder one anywhere in the graph.
