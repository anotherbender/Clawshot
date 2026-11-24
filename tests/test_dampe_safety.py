"""Tool admission remains separate from chest-open-based first/second race selection."""

import pytest
from dampe_flow import COUNT, FOREST, HEART, play

from clawshot.formats import byml, evfl
from clawshot.formats.zsdic import Dictionaries
from clawshot.patch import dampe_first_race, dampe_safety


def race():
    return evfl.EventFlowFile(
        "MiniGame_DampeRace",
        evfl.Flowchart(
            "MiniGame_DampeRace",
            actors=[
                evfl.Actor("PouchSystemActor", queries=["EventQueryIsExistInPouch"]),
                evfl.Actor("UISystemActor", actions=["EventEventFadeOut", "EventEventFadeIn"]),
                evfl.Actor("Player_Event", actions=["EventPlayerWarpToStarterLinkAnchor", "EventPlayerMoveToAnchor"]),
                evfl.Actor(
                    "ChallengeSystemActor",
                    actions=["EventTriggerMiniGameTimerSetting", "StartRace"],
                    queries=["EventQueryMiniGameTimerIsCounting"],
                ),
                evfl.Actor("Npc_EventStarter", actions=["EventTalk"]),
            ],
            events=[
                evfl.ActionEvent("Timer", 3, 0),
                evfl.ActionEvent("Start", 3, 1),
                evfl.ActionEvent("Event92", 1, 0, 3, {"Color": 0, "Length": 1}),
                evfl.ActionEvent("Event90", 2, 0, 4, {"ActorName": "StartPos", "InstanceName": "4"}),
                evfl.ActionEvent("FadeIn", 1, 1, params={"Color": 0, "Length": 1}),
                evfl.SwitchEvent("Event59", 3, 0, [(1, 6)]),
                evfl.SwitchEvent("Event444", 0, 0, [(0, 7), (1, 7)], {"Actor": "Item_Hookshot", "Num": 1}),
                evfl.ActionEvent(
                    "Event3",
                    4,
                    0,
                    8,
                    {"MessageId": "EventFlowMsg/Npc_Hylia_Dampe_002:Talk_01", "ChoiceNumber": 0},
                ),
                evfl.ActionEvent("Move", 2, 1, 0),
                evfl.SubFlowEvent("Event109", flowchart="InitTalk", entry_point="InitTalk", next=5),
            ],
            entry_points=[
                evfl.EntryPoint(dampe_safety.ENTRIES[0], 0),
                evfl.EntryPoint(dampe_safety.ENTRIES[1], 1),
                evfl.EntryPoint("Accept", 9),
            ],
        ),
    )


def actions(fc, entry, owned):
    index = fc.entry_point(entry).main_event
    out = []
    while index != evfl.NONE:
        event = fc.events[index]
        if isinstance(event, evfl.SwitchEvent):
            # Native pouch query results: held=0, absent=1.
            query = fc.actors[event.actor].queries[event.query]
            if query == "EventQueryMiniGameTimerIsCounting":
                code = 1
            else:
                assert query == "EventQueryIsExistInPouch", event
                code = 0 if event.params["Actor"] in owned else 1
            index = dict(event.cases)[code]
        elif isinstance(event, evfl.SubFlowEvent):
            assert (event.flowchart, event.entry_point) == ("InitTalk", "InitTalk"), event
            index = event.next
        else:
            out.append((fc.actors[event.actor].actions[event.action], event.params))
            index = event.next
    return out


@pytest.mark.parametrize("entry", dampe_safety.ENTRIES)
@pytest.mark.parametrize("owned", [set(), {"Item_Hookshot"}, {"Item_Longshot"}, {"Item_Hookshot", "Item_Longshot"}])
def test_start_or_refusal_always_has_a_safe_destination(entry, owned):
    fc = evfl.read(dampe_safety.patch(evfl.write(race()))).flowchart
    trace = actions(fc, entry, owned)
    if owned:
        assert [name for name, _ in trace] == [
            "EventTriggerMiniGameTimerSetting" if entry.endswith("Ready") else "StartRace"
        ]
    else:
        assert [name for name, _ in trace] == [
            "EventTalk",
            "EventEventFadeOut",
            "EventPlayerWarpToStarterLinkAnchor",
            "EventEventFadeIn",
        ]
        assert trace[0][1]["MessageId"] == dampe_safety.REFUSAL_MESSAGE
        assert trace[0][1]["IsWaitEnd"] is True
        assert trace[2][1]["InstanceName"] == dampe_safety.SURFACE


@pytest.mark.parametrize("owned", [set(), {"Item_Hookshot"}, {"Item_Longshot"}])
def test_acceptance_explains_refusal_before_start_speech_or_positioning(owned):
    fc = evfl.read(dampe_safety.patch(evfl.write(race()))).flowchart
    trace = actions(fc, "Accept", owned)
    if owned:
        assert [name for name, _ in trace] == [
            "EventTalk",
            "EventPlayerMoveToAnchor",
            "EventTriggerMiniGameTimerSetting",
        ]
        assert trace[0][1]["MessageId"] == "EventFlowMsg/Npc_Hylia_Dampe_002:Talk_01"
    else:
        assert [name for name, _ in trace] == [
            "EventTalk",
            "EventEventFadeOut",
            "EventPlayerWarpToStarterLinkAnchor",
            "EventEventFadeIn",
        ]
        assert trace[0][1]["MessageId"] == dampe_safety.REFUSAL_MESSAGE
        assert trace[0][1]["IsWaitEnd"] is True
        assert trace[2][1]["InstanceName"] == dampe_safety.SURFACE


@pytest.mark.dump
def test_native_refusal_explains_and_returns_to_a_real_surface_anchor(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    original = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    after = evfl.read(dampe_safety.patch(original))
    for entry in dampe_safety.ENTRIES:
        trace = actions(after.flowchart, entry, set())
        assert [name for name, _ in trace] == [
            "EventTalk",
            "EventEventFadeOut",
            "EventPlayerWarpToStarterLinkAnchor",
            "EventEventFadeIn",
        ]
        assert trace[0][1]["MessageId"] == dampe_safety.REFUSAL_MESSAGE
        assert trace[0][1]["IsWaitEnd"] is True
        assert trace[2][1]["InstanceName"] == dampe_safety.SURFACE
    path = "Banc/Graveyard/Graveyard_Adult_Dynamic.bcett.byml.zs"
    placed = byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))["Actors"]
    anchors = [a for a in placed if a.get("Gyaml") == "StartPos" and a.get("Name") == dampe_safety.SURFACE]
    assert len(anchors) == 1, anchors
    assert anchors[0]["Hash"] == 98411543249690399
    # This is the existing Kakariko-side surface spawn, not the race's reset "4".
    assert float(anchors[0]["Translate"][1]) > 97


@pytest.mark.dump
def test_native_pouch_result_codes_admit_either_tool_before_original_race_actions(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    donor_path = "Event/EventFlow/ReplaceEquipmentForEraChange.bfevfl.zs"
    donor = evfl.read(dictionaries.decompress(donor_path, (romfs / donor_path).read_bytes())).flowchart
    query = next(event for event in donor.events if event.name == "Event12")
    assert donor.actors[query.actor].queries[query.query] == "EventQueryIsExistInPouch"
    held = donor.events[dict(query.cases)[0]]
    absent = donor.events[dict(query.cases)[1]]
    assert donor.actors[held.actor].actions[held.action] == "EventWait"
    assert donor.actors[absent.actor].actions[absent.action] == "EventTriggerSetGameDataString64"
    assert absent.params["GameDataName"] == "PlayerStatus.AnotherEraEquipShield"
    assert absent.params["Value"] == ""
    # Native held=0 preserves equipment; absent=1 clears it. Apply that ABI to the new gates.
    native = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    before = evfl.read(native).flowchart
    after = evfl.read(dampe_safety.patch(native)).flowchart
    for entry in dampe_safety.ENTRIES:
        for owned in ({"Item_Hookshot"}, {"Item_Longshot"}, {"Item_Hookshot", "Item_Longshot"}):
            index = after.entry_point(entry).main_event
            while isinstance(event := after.events[index], evfl.SwitchEvent):
                index = dict(event.cases)[0 if event.params["Actor"] in owned else 1]
            assert index == before.entry_point(entry).main_event, (entry, owned, after.events[index])


@pytest.mark.dump
@pytest.mark.parametrize("entry", dampe_safety.ENTRIES)
def test_first_race_repair_preserves_the_no_tool_refusal(romfs, entry):
    dictionaries = Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    before = evfl.read(dampe_safety.patch(raw)).flowchart
    after = evfl.read(dampe_first_race.patch(dampe_safety.patch(raw))).flowchart
    assert actions(after, entry, set()) == actions(before, entry, set())


@pytest.mark.dump
@pytest.mark.parametrize("opened", [False, True])
def test_native_ready_talk_refuses_before_acceptance_and_positioning(romfs, opened):
    dictionaries = Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    fc = evfl.read(dampe_first_race.patch(dampe_safety.patch(raw))).flowchart
    state = {FOREST: "Complete", COUNT: 2, HEART: True, dampe_first_race.CHEST_OPEN: opened}
    initial = state.copy()
    trace = play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, set())
    assert "ClawshotDampeNoToolTalk" in trace
    assert trace.index("ClawshotDampeNoToolTalk") < trace.index("ClawshotDampeSurfaceFadeOut")
    assert not {"Event3", "Event67", "Event286", "Event149", "Event16", "Event130", "Event131"}.intersection(trace)
    assert state == initial


@pytest.mark.dump
@pytest.mark.parametrize("owned", [{"Item_Hookshot"}, {"Item_Longshot"}])
@pytest.mark.parametrize("talked", [False, True])
def test_refusal_then_natural_tool_acquisition_keeps_the_first_race_available(romfs, owned, talked):
    dictionaries = Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    fc = evfl.read(dampe_first_race.patch(dampe_safety.patch(raw))).flowchart
    state = {
        FOREST: "Step06",
        COUNT: 0,
        HEART: False,
        dampe_first_race.CHEST_OPEN: False,
        "Npc_HaveTalked": talked,
        "MiniGame_TimerMinute": 2,
        "MiniGame_TimerSecond": 10,
        "MiniGame_TimerMilliSecond": 0,
    }
    initial = state.copy()
    refusal = play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, set())
    assert "ClawshotDampeNoToolTalk" in refusal
    assert state == initial  # no race, treasure, quest or offer-history writes
    # Native actor talk history may remember the interaction; neither variant may block racing.
    state["Npc_HaveTalked"] = True
    play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, owned)
    assert state["MiniGame_DampeRace"] == "Playing"
    play(fc, "Finish_Npc_Hylia_Dampe_002_StepStart", state, owned)
    play(fc, "Result", state, owned)
    assert state[COUNT] == 0
    assert state["Minigame_DampeRace_TreasureBoxState"] == "AppearHookShot"


@pytest.mark.dump
@pytest.mark.parametrize("owned", [{"Item_Hookshot"}, {"Item_Longshot"}])
@pytest.mark.parametrize("opened", [False, True])
def test_held_tools_keep_both_native_race_action_sequences(romfs, owned, opened):
    dictionaries = Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(dampe_safety.FLOW, (romfs / dampe_safety.FLOW).read_bytes())
    before = evfl.read(dampe_first_race.patch(raw)).flowchart
    after = evfl.read(dampe_first_race.patch(dampe_safety.patch(raw))).flowchart
    initial = {FOREST: "Complete", COUNT: 2, HEART: True, dampe_first_race.CHEST_OPEN: opened}
    states, actions_seen = [], []
    for fc in (before, after):
        state = initial.copy()
        trace = play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, owned)
        named = {event.name: event for event in fc.events}
        actions_seen.append(
            [
                (fc.actors[event.actor].name, fc.actors[event.actor].actions[event.action], event.params)
                for name in trace
                if isinstance(event := named[name], evfl.ActionEvent)
            ]
        )
        states.append(state)
    assert states[1] == states[0]
    assert states[1]["MiniGame_DampeRace"] == ("PlayingSecond" if opened else "Playing")
    assert actions_seen[1] == actions_seen[0]
