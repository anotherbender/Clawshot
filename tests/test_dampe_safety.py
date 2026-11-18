"""A no-Hookshot refusal must leave Link outside, not below the one-way descent."""

from copy import deepcopy

import pytest

from clawshot.formats import byml, evfl
from clawshot.formats.zsdic import Dictionaries
from clawshot.patch import dampe_safety


def race():
    return evfl.EventFlowFile(
        "MiniGame_DampeRace",
        evfl.Flowchart(
            "MiniGame_DampeRace",
            actors=[
                evfl.Actor("PouchSystemActor", queries=["EventQueryIsExistInPouch"]),
                evfl.Actor("UISystemActor", actions=["EventEventFadeOut", "EventEventFadeIn"]),
                evfl.Actor("Player_Event", actions=["EventPlayerWarpToStarterLinkAnchor"]),
                evfl.Actor("ChallengeSystemActor", actions=["EventTriggerMiniGameTimerSetting", "StartRace"]),
            ],
            events=[
                evfl.ActionEvent("Timer", 3, 0),
                evfl.ActionEvent("Start", 3, 1),
                evfl.ActionEvent("Event92", 1, 0, 3, {"Color": 0, "Length": 1}),
                evfl.ActionEvent("Event90", 2, 0, 4, {"ActorName": "StartPos", "InstanceName": "4"}),
                evfl.ActionEvent("FadeIn", 1, 1, params={"Color": 0, "Length": 1}),
            ],
            entry_points=[evfl.EntryPoint(dampe_safety.ENTRIES[0], 0), evfl.EntryPoint(dampe_safety.ENTRIES[1], 1)],
        ),
    )


def actions(fc, entry, owned):
    index = fc.entry_point(entry).main_event
    out = []
    while index != evfl.NONE:
        event = fc.events[index]
        if isinstance(event, evfl.SwitchEvent):
            index = dict(event.cases)[int(event.params["Actor"] in owned)]
        else:
            out.append((fc.actors[event.actor].actions[event.action], event.params))
            index = event.next
    return out


@pytest.mark.parametrize("entry", dampe_safety.ENTRIES)
@pytest.mark.parametrize("owned", [set(), {"Item_Hookshot"}, {"Item_Longshot"}])
def test_start_or_refusal_always_has_a_safe_destination(entry, owned):
    fc = evfl.read(dampe_safety.patch(evfl.write(race()))).flowchart
    trace = actions(fc, entry, owned)
    if owned:
        assert [name for name, _ in trace] == [
            "EventTriggerMiniGameTimerSetting" if entry.endswith("Ready") else "StartRace"
        ]
    else:
        assert [name for name, _ in trace] == [
            "EventEventFadeOut",
            "EventPlayerWarpToStarterLinkAnchor",
            "EventEventFadeIn",
        ]
        assert trace[1][1]["InstanceName"] == dampe_safety.SURFACE


@pytest.mark.dump
def test_native_race_guard_keeps_every_original_event_and_returns_to_a_real_surface_anchor(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    original = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    before = evfl.read(original)
    after = evfl.read(dampe_safety.patch(original))
    assert after.flowchart.events[: len(before.flowchart.events)] == before.flowchart.events
    expected = deepcopy(before)
    for entry in dampe_safety.ENTRIES:
        expected.flowchart.entry_point(entry).main_event = after.flowchart.entry_point(entry).main_event
    expected.flowchart.events.extend(after.flowchart.events[len(before.flowchart.events) :])
    assert expected == after
    for entry in dampe_safety.ENTRIES:
        trace = actions(after.flowchart, entry, set())
        assert [name for name, _ in trace] == [
            "EventEventFadeOut",
            "EventPlayerWarpToStarterLinkAnchor",
            "EventEventFadeIn",
        ]
        assert trace[1][1]["InstanceName"] == dampe_safety.SURFACE
    path = "Banc/Graveyard/Graveyard_Adult_Dynamic.bcett.byml.zs"
    placed = byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))["Actors"]
    anchors = [a for a in placed if a.get("Gyaml") == "StartPos" and a.get("Name") == dampe_safety.SURFACE]
    assert len(anchors) == 1, anchors
    assert anchors[0]["Hash"] == 98411543249690399
    # This is the existing Kakariko-side surface spawn, not the race's reset "4".
    assert float(anchors[0]["Translate"][1]) > 97
