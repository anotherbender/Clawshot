"""Door of Time story writes only move forward: an early first pull keeps Complete and every later scene.

Synthetic flows are invented on the native contracts of the round 16 DoorOfTime audit, never cut from the game.
Dump-marked tests read the real flows and GameData, and compose with the transforms already shipped for them.
The runner follows state-changing events only; engine timing, presentation and save behavior still need play.
"""

from dataclasses import replace
from itertools import product

import pytest

from clawshot.formats import byml, evfl, zsdic
from clawshot.generate import Settings
from clawshot.patch import darunia, door, door_story, gifts, make_seed
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.plan import PatchError
from clawshot.save import key
from clawshot.world.load import load_spec

DOOR = "Event/EventFlow/DoorOfTime.bfevfl.zs"
CASTLE = "Event/EventFlow/Goto_HyruleCastle.bfevfl.zs"
SARIA = "Event/EventFlow/Dm_SY_Ocarina_SariaSong.bfevfl.zs"
ZELDA = "Event/EventFlow/Npc_Hylia_Zelda_Child.bfevfl.zs"
PATHS = (DOOR, CASTLE, SARIA, ZELDA)
# Native Step_DoorOfTime enum order (GameData RawValues, native spelling); IsAfter_X holds strictly after X.
STEPS = (
    "NotReady",
    "Ready",
    "Step01",
    "Step02",
    "Step2_1",
    "Srep2_1_1",
    "Step2_2",
    "Step03",
    "Step04",
    "Step05",
    "Step06",
    "Complete",
)
FIRE = ("NotReady", "Ready", "KakarikoVillageNpc", "Complete")  # invented excerpt around Impa's Fire step
WATER = ("NotReady", "Ready", "Complete")  # invented excerpt
ORDERS = {"DoorOfTime": STEPS, "Get_StoneOfFire": FIRE, "Get_StoneOfWater": WATER}
# ESCAPE_READY's other inputs (see escape_ready) and the drawbridge it gates.
SENDOFF = "HavePlayedEvent.Dm_HrlField_0020"
ESCAPED = "HavePlayedEvent.HyruleField_DoorOfTime_Escape"
BRIDGE = "IsHyruleFieldBridgeClose"
START = {
    "Step_Get_StoneOfForest": "Complete",
    "Step_Get_StoneOfFire": "Ready",
    "Step_Get_StoneOfWater": "Ready",
    SENDOFF: True,
    ESCAPED: False,
    BRIDGE: False,
}
STONES = (("Ready", "Ready"), ("Complete", "Ready"), ("Ready", "Complete"), ("Complete", "Complete"))  # Fire, Water
STORIES = ((False, False), (True, False), (True, True))  # send-off played, escape played
# Every lower DoorOfTime writer: (flow, writer, step written, native next or None for the end).
GUARDS = (
    (DOOR, "Event7", "Step02", "Event62"),
    (DOOR, "Event147", "Step2_1", "Event5"),
    (DOOR, "Event148", "Step2_2", "Event5"),
    (DOOR, "Event37", "Step03", "Event77"),
    (DOOR, "Event12", "Step04", "Event140"),
    (DOOR, "Event14", "Step05", "Event171"),
    (DOOR, "Event57", "Step06", None),
    (CASTLE, "Event32", "Step01", "Event202"),
    (SARIA, "Event172", "Srep2_1_1", None),
    (ZELDA, "Event42", "Srep2_1_1", None),
)
BOUNDARIES = ("before", "equal", "after", "complete")
RAISE = (DOOR, "Event77", "Event4")  # the stone count's bridge raise and its native next
BRIDGE_UP = {"GameDataName": BRIDGE, "Index": -1, "Value": True}
COUNT_RESET = {"GameDataName": "DoorOfTime_GetStoneCount", "Index": -1, "Value": 0}
REFERENCE = {"forward": ("DoorOfTime",), "bridge": True}  # what the door story promises on the native flows

STEP = "EventExecuteProgressChallengeStep"
NOTICE = "EventTriggerShowChallengeProgressUI"
BOOL_EXP = "EventQueryIsGameDataBoolExp"
SET_BOOL = "EventTriggerSetGameDataBool"
SET_INT = "EventTriggerSetGameDataInt"
KEEP_CAMERA = "EventTriggerSendKeepStateMessageToPlayerCamera"
BGM = "EventTriggerSoundStartSceneBgm"
WRITE = {
    "IsWaitEnd": True,
    "IsIgnoreCompletedChallenge": False,
    "IsIgnoreChallengeProgressUI": False,
    "ChallengeName": "DoorOfTime",
}
QUIET = {**WRITE, "IsIgnoreChallengeProgressUI": True}
FIRST = {**QUIET, "IsIgnoreCompletedChallenge": True}  # the courtyard's initial Step01 write
CAMERA = {"KeepManualModeFrame": 120.0, "IsKeepWithRelativePos": False}
WEATHER = {"IsImmTrans": False, "ChangeSpeed": 0}
DOOR_NOTICE = {"ChallengeName": "DoorOfTime", "IsFirstStep": False}
REWARD = ("call", "Dm_SY_GetInEvent", "GetInEvent_Test", {"ActorName": "Item_Test"})


def write(name, step, next_name, params=WRITE):
    return (name, "act", "ChallengeSystemActor", STEP, {**params, "StepName": step}, next_name)


def data(name, action, game_data, value, next_name):
    return (name, "act", "GameDataActor", action, {"GameDataName": game_data, "Index": -1, "Value": value}, next_name)


def ask(name, expression, cases):
    return (name, "ask", "GameDataActor", BOOL_EXP, {"GameDataName": expression}, cases)


def chart(name, actors, rows, entries):
    """An invented flowchart: ``actors`` are (name, actions, queries); rows and entries name their targets."""
    at = {row[0]: i for i, row in enumerate(rows)}
    slots = {actor: i for i, (actor, _, _) in enumerate(actors)}

    def ref(target):
        return evfl.NONE if target is None else at[target]

    events = []
    for event, kind, *rest in rows:
        if kind == "act":
            actor, action, params, target = rest
            who = slots[actor]
            events.append(evfl.ActionEvent(event, who, actors[who][1].index(action), ref(target), params))
        elif kind == "ask":
            actor, query, params, cases = rest
            who = slots[actor]
            branches = [(value, ref(target)) for value, target in cases.items()]
            events.append(evfl.SwitchEvent(event, who, actors[who][2].index(query), branches, params))
        elif kind == "fork":
            forks, join = rest
            events.append(evfl.ForkEvent(event, ref(join), [ref(fork) for fork in forks]))
        elif kind == "join":
            events.append(evfl.JoinEvent(event, ref(rest[0])))
        else:
            flow, entry, params, target = rest
            events.append(evfl.SubFlowEvent(event, flow, entry, ref(target), params))
    return evfl.EventFlowFile(
        f"{name}Test",
        evfl.Flowchart(
            name,
            [evfl.Actor(actor, actions=list(actions), queries=list(queries)) for actor, actions, queries in actors],
            events,
            [evfl.EntryPoint(entry, at[main], [at[call] for call in calls]) for entry, main, calls in entries],
        ),
    )


def door_flow():
    """Send-off, stone count, escape, Song of Time aftermath, door opening and Rauru's Complete."""
    return chart(
        "DoorOfTime",
        [
            ("ChallengeSystemActor", [STEP, NOTICE], []),
            ("GameDataActor", [SET_BOOL, SET_INT], ["EventQueryHavePlayedEvent", BOOL_EXP]),
            ("EventSystemActor", ["EventTransition"], []),
            ("EventWorldManagerController", ["Event_ResetWeatherForFlowchart"], []),
            ("EventCamera", [KEEP_CAMERA], []),
            ("SoundSystemActor", [BGM], []),
        ],
        [
            # Impa's field send-off: Step02, then Fire's own Kakariko step (Darunia's Event62 guard).
            write("Event7", "Step02", "Event62"),
            write("Event62", "KakarikoVillageNpc", None, darunia.STEP_WRITE),
            ("Event65", "act", "EventSystemActor", "EventTransition", {"EventName": "Dm_HrlField_0020"}, "Event7"),
            # A stone count: the first stones step to Step2_1 or Step2_2, all three to Step03.
            ask("Event38", "Get_StoneOfFire_IsCompleted_Exp", {0: "Event39", 1: "Event56"}),
            ask("Event39", "Get_StoneOfWater_IsCompleted_Exp", {0: "Event37", 1: "Event147"}),
            ask("Event56", "Get_StoneOfWater_IsCompleted_Exp", {0: "Event148"}),
            write("Event37", "Step03", "Event77"),
            data("Event77", SET_BOOL, "IsHyruleFieldBridgeClose", True, "Event4"),
            data("Event4", SET_INT, "DoorOfTime_GetStoneCount", 0, None),
            write("Event147", "Step2_1", "Event5"),
            write("Event148", "Step2_2", "Event5"),
            data("Event5", SET_INT, "DoorOfTime_GetStoneCount", 1, None),
            # Zelda's escape: its fork lowers the bridge (native Event78) before Step04, then the weather reset
            # and a registered reward call.
            ("Event89", "fork", ["Event78"], "Event90"),
            data("Event78", SET_BOOL, BRIDGE, False, "Event90"),
            ("Event90", "join", "Event12"),
            write("Event12", "Step04", "Event140"),
            ("Event140", "act", "EventWorldManagerController", "Event_ResetWeatherForFlowchart", WEATHER, "Event111"),
            ("Event111", "call", *REWARD[1:], None),
            # After the Song of Time: camera hold, Step05, the progress notice and field music.
            ("Event204", "act", "EventCamera", KEEP_CAMERA, CAMERA, "Event14"),
            write("Event14", "Step05", "Event171"),
            ("Event171", "act", "ChallengeSystemActor", NOTICE, DOOR_NOTICE, "Event146"),
            ("Event146", "act", "SoundSystemActor", BGM, {"StartType": 2, "BgmName": "BGM_Test"}, None),
            # The door opening ends on Step06.
            ("Event145", "act", "SoundSystemActor", BGM, {"StartType": 0, "BgmName": "BGM_Test"}, "Event57"),
            write("Event57", "Step06", None),
            # Rauru: Complete after the Recovery sub flow, never guarded.
            ("Event102", "call", "", "Recovery", None, "Event93"),
            write("Event93", "Complete", None),
            data("Event76", SET_BOOL, "IsTestRecovered", True, None),
        ],
        [
            ("DoorOfTime_SendOff", "Event65", []),
            ("DoorOfTime_CheckStoneNum", "Event38", []),
            ("DoorOfTime_Escape", "Event89", ["Event111"]),
            ("Dm_MelodyGet_Time_After", "Event204", []),
            ("DoorOfTime_OpenDoor", "Event145", []),
            ("Recovery", "Event76", []),
            ("SageRoom_MeetRauru", "Event102", ["Event102"]),
            ("TestStartsAtAWriter", "Event57", []),  # an entry may name a writer itself
        ],
    )


def castle_flow():
    """The courtyard meeting: Zelda's quest completes, DoorOfTime starts at Step01, then wait/fade/notice/camera."""
    return chart(
        "Goto_HyruleCastle",
        [
            ("ChallengeSystemActor", [STEP, NOTICE], []),
            ("GameDataActor", [SET_BOOL], ["EventQueryIsGameDataBool", BOOL_EXP]),
            ("EventSystemActor", ["EventWait"], []),
            ("UISystemActor", ["EventEventFadeIn"], []),
            ("EventCamera", [KEEP_CAMERA], []),
        ],
        [
            ("Event203", "act", "EventSystemActor", "EventWait", {"IsWaitEnd": True, "Frames": 30}, "Event30"),
            write("Event30", "Complete", "Event32", {**QUIET, "ChallengeName": "Goto_HyruleCastle"}),
            write("Event32", "Step01", "Event202", FIRST),
            ("Event202", "act", "EventSystemActor", "EventWait", {"IsWaitEnd": True, "Frames": 90}, "Event128"),
            ("Event128", "act", "UISystemActor", "EventEventFadeIn", {"Length": 1, "IsWaitEnd": True}, "Event183"),
            ("Event183", "act", "ChallengeSystemActor", NOTICE, {**DOOR_NOTICE, "IsFirstStep": True}, "Event204"),
            ("Event204", "act", "EventCamera", KEEP_CAMERA, CAMERA, None),
        ],
        [("Goto_HyruleCastle_MeetZelda", "Event203", [])],
    )


def stone_talk_flow(name, writer, gate, callers):
    """A Water-stone talk: before Water starts, the quiet Srep2_1_1 write ends the entry."""
    rows = [data(caller, SET_BOOL, f"IsTest{caller}", True, gate) for caller, _ in callers]
    rows += [ask(gate, "Get_StoneOfWater_IsAfter_Ready_Exp", {1: writer}), write(writer, "Srep2_1_1", None, QUIET)]
    return chart(
        name,
        [
            ("GameDataActor", [SET_BOOL, SET_INT], [BOOL_EXP, "EventQueryIsGameDataBool"]),
            ("ChallengeSystemActor", [STEP], []),
        ],
        rows,
        [(entry, caller, []) for caller, entry in callers],
    )


def saria_flow():
    return stone_talk_flow("Dm_SY_Ocarina_SariaSong", "Event172", "Event173", [("Event4", "Story_Check")])


def zelda_flow():
    return stone_talk_flow("Npc_Hylia_Zelda_Child", "Event42", "Event43", [("Event78", "Talk"), ("Event79", "About")])


FLOWS = {DOOR: door_flow, CASTLE: castle_flow, SARIA: saria_flow, ZELDA: zelda_flow}


def escape_ready(state):
    """Model of the door stage's unsaved ``ESCAPE_READY`` row: DoorOfTime past Step2_2, all three stone quests
    complete, the send-off played and the escape unplayed."""
    stones = all(state[f"Step_Get_StoneOf{stone}"] == "Complete" for stone in ("Forest", "Fire", "Water"))
    past = STEPS.index(state["Step_DoorOfTime"]) > STEPS.index("Step2_2")
    return past and stones and state[SENDOFF] and not state[ESCAPED]


def run(fc, start, state, *, orders=ORDERS, forward=(), bridge=False, entry=None):
    """Follow ``fc`` from event ``start``; return its effects and update ``state`` (``Step_<quest>``, data).

    A reference engine never moves the ``forward`` quests back and, with ``bridge``, raises the drawbridge only
    while ``escape_ready``. Sub flow calls are effects, checked against ``entry``'s registrations, not followed.
    Case 0 is a true query, as native gates use it."""
    effects = []
    budget = [1000]

    def holds(params):
        expression = params["GameDataName"]
        if expression == door_story.ESCAPE_READY:
            return escape_ready(state)
        quest, after, step = expression.removesuffix("_Exp").partition("_IsAfter_")
        if after:
            return orders[quest].index(state[f"Step_{quest}"]) > orders[quest].index(step)
        assert expression.endswith("_IsCompleted_Exp"), expression
        return state[f"Step_{expression.removesuffix('_IsCompleted_Exp')}"] == "Complete"

    def dropped(action, params):
        if action == STEP and params["ChallengeName"] in forward:
            order = orders[params["ChallengeName"]]
            return order.index(state[f"Step_{params['ChallengeName']}"]) > order.index(params["StepName"])
        return bridge and action == SET_BOOL and params == BRIDGE_UP and not escape_ready(state)

    def walk(at, stop):
        while at not in (evfl.NONE, stop):
            budget[0] -= 1
            assert budget[0] > 0, effects
            event = fc.events[at]
            params = getattr(event, "params", None) or {}
            if isinstance(event, evfl.SwitchEvent):
                actor = fc.actors[event.actor]
                assert (actor.name, actor.queries[event.query]) == ("GameDataActor", BOOL_EXP), event
                at = dict(event.cases).get(0 if holds(params) else 1, evfl.NONE)
            elif isinstance(event, evfl.ForkEvent):
                for fork in event.forks:
                    walk(fork, event.join)
                at = event.join
            elif isinstance(event, evfl.JoinEvent):
                at = event.next
            elif isinstance(event, evfl.SubFlowEvent):
                assert entry is None or at in entry.sub_flow_events, f"{event.name} is not registered"
                effects.append(("call", event.flowchart, event.entry_point, params))
                at = event.next
            elif isinstance(event, evfl.ActionEvent):
                actor = fc.actors[event.actor]
                action = actor.actions[event.action]
                if not dropped(action, params):
                    if action == STEP:
                        state[f"Step_{params['ChallengeName']}"] = params["StepName"]
                    elif action in (SET_BOOL, SET_INT):
                        state[params["GameDataName"]] = params["Value"]
                    effects.append((actor.name, action, params))
                at = event.next
            else:
                raise AssertionError(f"unmodeled event {event}")

    walk(start, evfl.NONE)
    return effects


def outcome(fc, start, state, **options):
    """Effects and final state from entry point ``start`` (a name) or event ``start`` (an index)."""
    state = dict(state)
    if isinstance(start, str):
        entry = fc.entry_point(start)
        return run(fc, entry.main_event, state, entry=entry, **options), state
    return run(fc, start, state, **options), state


def index(fc, name):
    return next(i for i, event in enumerate(fc.events) if event.name == name)


def named(fc, name):
    return fc.events[index(fc, name)]


def guards_of(path):
    return [guard for guard in GUARDS if guard[0] == path]


def at_boundary(step, boundary):
    i = STEPS.index(step)
    return {"before": STEPS[i - 1], "equal": step, "after": STEPS[i + 1], "complete": "Complete"}[boundary]


def transformed(path, document):
    return evfl.read(door_story.changes()[path](evfl.write(document)))


def check_boundary(old, new, writer, step, tail, boundary, orders=ORDERS):
    """From the writer's index: before/equal run the native write, after/Complete skip it. The tail stays native
    but for the bridge raise, which needs ESCAPE_READY (never with Fire/Water Ready, here always with all three)."""
    current = at_boundary(step, boundary)
    write = ("ChallengeSystemActor", STEP, named(old, writer).params)
    guarded = (write, ("GameDataActor", SET_BOOL, BRIDGE_UP))
    for stones in ("Ready", "Complete"):
        state = {**START, "Step_DoorOfTime": current, "Step_Get_StoneOfFire": stones, "Step_Get_StoneOfWater": stones}
        native_effects, _ = outcome(old, index(old, writer), state, orders=orders)
        assert native_effects[0] == write
        assert bool(native_effects[1:]) == (tail is not None)  # the continuation has effects of its own
        effects, final = outcome(new, index(new, writer), state, orders=orders)
        assert (effects, final) == outcome(old, index(old, writer), state, orders=orders, **REFERENCE)
        assert [e for e in effects if e not in guarded] == [e for e in native_effects if e not in guarded]
        assert (write in effects) == (STEPS.index(current) <= STEPS.index(step))
        assert final["Step_DoorOfTime"] == max(current, step, key=STEPS.index)
        assert final[BRIDGE] is (writer == "Event37" and stones == "Complete")


def guarded_of(path):
    """Every action the story guards in ``path``, with its native next (None for the end)."""
    raises = [(name, tail) for flow, name, tail in (RAISE,) if flow == path]
    return [(writer, tail) for _, writer, _, tail in guards_of(path)] + raises


def guard_shape(path, name, tail, moved):
    """Cases and parameters of the query replacing ``name``, whose action moved to ``moved``."""
    if (path, name) == RAISE[:2]:
        return [(0, moved), (1, tail)], {"GameDataName": door_story.ESCAPE_READY}
    step = next(step for flow, writer, step, _ in GUARDS if (flow, writer) == (path, name))
    cases = [(1, moved)] if tail is None else [(0, tail), (1, moved)]
    return cases, {"GameDataName": f"DoorOfTime_IsAfter_{step}_Exp"}


def assert_only_guarded(native, patched, path):
    """Only the guarded actions change: each becomes a query at its own index, the action moved to the end."""
    old, new = native.flowchart, patched.flowchart
    assert (new.name, new.actors, new.entry_points) == (old.name, old.actors, old.entry_points)
    actor = next(i for i, candidate in enumerate(old.actors) if candidate.name == "GameDataActor")
    query = old.actors[actor].queries.index(BOOL_EXP)
    guarded = {index(old, name): name for name, _ in guarded_of(path)}
    assert len(new.events) == len(old.events) + len(guarded)
    for i, event in enumerate(old.events):
        if i not in guarded:
            assert new.events[i] == event, event.name
            continue
        name = guarded[i]
        moved = index(new, f"ClawshotDoor{name}Write")
        assert moved >= len(old.events)
        assert new.events[moved] == replace(event, name=f"ClawshotDoor{name}Write")
        cases, expression = guard_shape(path, name, None if event.next == evfl.NONE else event.next, moved)
        assert new.events[i] == evfl.SwitchEvent(name, actor, query, cases, expression)


def canonical(fc):
    """``fc`` keyed by event names, so edit orders that append in another order compare equal."""
    names = [event.name for event in fc.events]
    assert len(set(names)) == len(names)

    def ref(i):
        return None if i == evfl.NONE else names[i]

    def form(event):
        if isinstance(event, evfl.ActionEvent | evfl.SwitchEvent):
            actor = fc.actors[event.actor]
            who = (actor.name, actor.secondary_name)
            if isinstance(event, evfl.ActionEvent):
                return ("act", who, actor.actions[event.action], event.params, ref(event.next))
            cases = [(value, ref(target)) for value, target in event.cases]
            return ("ask", who, actor.queries[event.query], event.params, cases)
        if isinstance(event, evfl.ForkEvent):
            return ("fork", [ref(fork) for fork in event.forks], ref(event.join))
        if isinstance(event, evfl.JoinEvent):
            return ("join", ref(event.next))
        if isinstance(event, evfl.SubFlowEvent):
            return ("call", event.flowchart, event.entry_point, event.params, ref(event.next))
        if isinstance(event, evfl.SubFlowSwitchEvent):
            cases = [(value, ref(target)) for value, target in event.cases]
            return ("call-switch", event.flowchart, event.entry_point, event.params, cases)
        return ("return", event.value)

    events = {event.name: form(event) for event in fc.events}
    entries = {
        entry.name: (ref(entry.main_event), [ref(call) for call in entry.sub_flow_events], entry.variables)
        for entry in fc.entry_points
    }
    actors = [
        (
            actor.name,
            actor.secondary_name,
            actor.argument_name,
            actor.params,
            sorted(actor.actions),
            sorted(actor.queries),
            actor.entry_point,
            actor.cut_number,
        )
        for actor in fc.actors
    ]
    return events, entries, actors


def assert_adds_only_the_guards(alone, combined, path):
    """``combined`` is ``alone`` plus this path's guards and moved actions, nothing else."""
    old_events, old_entries, old_actors = canonical(alone)
    new_events, new_entries, new_actors = canonical(combined)
    assert (new_entries, new_actors) == (old_entries, old_actors)
    names = {name for name, _ in guarded_of(path)}
    assert new_events.keys() == old_events.keys() | {f"ClawshotDoor{name}Write" for name in names}
    for name, form in old_events.items():
        if name not in names:
            assert new_events[name] == form, name
    for name, tail in guarded_of(path):
        moved = f"ClawshotDoor{name}Write"
        assert new_events[moved] == old_events[name]
        cases, expression = guard_shape(path, name, tail, moved)
        assert new_events[name] == ("ask", ("GameDataActor", ""), BOOL_EXP, expression, cases)


def assert_composes(source, path, others):
    """Apply ``others`` alone, then after and before the door story; both orders must agree."""
    story = door_story.changes()[path]

    def chain(data):
        for transform in others:
            data = transform(data)
        return data

    alone = evfl.read(chain(source)).flowchart
    after = evfl.read(story(chain(source))).flowchart
    before = evfl.read(chain(story(source))).flowchart
    assert canonical(after) == canonical(before)
    assert_adds_only_the_guards(alone, after, path)
    return alone, after, before


def test_changes_cover_the_four_writer_flows_and_no_game_data():
    assert sorted(door_story.changes()) == sorted(PATHS)
    assert darunia.DOOR_FLOW == door.FLOW == DOOR
    assert door_story.ESCAPE_READY == "Clawshot.Door.EscapeReady"  # the door stage's row, named for both sides


@pytest.mark.parametrize("path", PATHS)
def test_only_the_lower_writers_change_and_every_reference_survives(path):
    out = door_story.changes()[path](evfl.write(FLOWS[path]()))
    assert evfl.write(evfl.read(out)) == out
    assert_only_guarded(FLOWS[path](), evfl.read(out), path)


@pytest.mark.parametrize("path,writer,step,tail", GUARDS)
@pytest.mark.parametrize("boundary", BOUNDARIES)
def test_a_writer_advances_to_its_step_but_never_moves_the_quest_back(path, writer, step, tail, boundary):
    old = FLOWS[path]().flowchart
    check_boundary(old, transformed(path, FLOWS[path]()).flowchart, writer, step, tail, boundary)


@pytest.mark.parametrize("path", PATHS)
def test_every_entry_plays_as_native_on_the_story_reference_engine(path):
    """No DoorOfTime step goes back, and the bridge rises only while the escape may play; the rest is native."""
    old = FLOWS[path]().flowchart
    new = transformed(path, FLOWS[path]()).flowchart
    for entry in old.entry_points:
        for current in STEPS:
            for (fire, water), (sendoff, escaped) in product(STONES, STORIES):
                stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
                state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped}
                expected = outcome(old, entry.name, state, **REFERENCE)
                effects, final = outcome(new, entry.name, state)
                assert (effects, final) == expected, (entry.name, state)
                assert STEPS.index(final["Step_DoorOfTime"]) >= STEPS.index(current)


@pytest.mark.parametrize("current", ("Step06", "Complete"))
def test_skipped_writes_keep_the_reward_camera_and_notice_tails(current):
    state = {**START, "Step_DoorOfTime": current}
    story = transformed(DOOR, door_flow()).flowchart
    escape, escaped = outcome(story, "DoorOfTime_Escape", state)
    assert escape[-1] == REWARD  # the registered reward call after the skipped Step04
    song, sung = outcome(story, "Dm_MelodyGet_Time_After", state)
    assert song[:2] == [("EventCamera", KEEP_CAMERA, CAMERA), ("ChallengeSystemActor", NOTICE, DOOR_NOTICE)]
    meeting, met = outcome(transformed(CASTLE, castle_flow()).flowchart, "Goto_HyruleCastle_MeetZelda", state)
    assert [effect[:2] for effect in meeting] == [
        ("EventSystemActor", "EventWait"),
        ("ChallengeSystemActor", STEP),
        ("EventSystemActor", "EventWait"),
        ("UISystemActor", "EventEventFadeIn"),
        ("ChallengeSystemActor", NOTICE),
        ("EventCamera", KEEP_CAMERA),
    ]
    assert meeting[1][2]["ChallengeName"] == "Goto_HyruleCastle"  # Zelda's own quest still completes
    assert met["Step_Goto_HyruleCastle"] == "Complete"
    for effects, final in ((escape, escaped), (song, sung), (meeting, met)):
        door_writes = [e for e in effects if e[1] == STEP and e[2]["ChallengeName"] == "DoorOfTime"]
        assert door_writes == []
        assert final["Step_DoorOfTime"] == current


@pytest.mark.parametrize("current", ("Step2_2", "Step03", "Step04", "Step06", "Complete"))
@pytest.mark.parametrize("forest", ("Ready", "Complete"))
@pytest.mark.parametrize("sendoff,escaped", STORIES)
def test_the_bridge_rises_only_while_the_escape_may_play(current, forest, sendoff, escaped):
    story = transformed(DOOR, door_flow()).flowchart
    stones = {"Step_Get_StoneOfForest": forest, "Step_Get_StoneOfFire": "Complete", "Step_Get_StoneOfWater": "Complete"}
    state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped}
    effects, final = outcome(story, index(story, "Event77"), state)
    ready = current != "Step2_2" and forest == "Complete" and sendoff and not escaped
    raised = [("GameDataActor", SET_BOOL, BRIDGE_UP)] if ready else []
    assert effects == [*raised, ("GameDataActor", SET_INT, COUNT_RESET)]  # the count tail always runs
    assert final[BRIDGE] is ready
    assert final["Step_DoorOfTime"] == current


@pytest.mark.parametrize("before", ("Step2_2", "Step06", "Complete"))  # natural, song-only opening, early pull
def test_the_bridge_rises_for_the_escape_and_never_after_it(before):
    """Stone counts before the escape, the escape, then later counts (other dungeon callbacks) in one save."""
    natural = before == "Step2_2"
    story, native = transformed(DOOR, door_flow()).flowchart, door_flow().flowchart
    stones = {"Step_Get_StoneOfFire": "Complete", "Step_Get_StoneOfWater": "Complete"}
    state = {**START, **stones, "Step_DoorOfTime": before}
    for _ in range(2):  # the third stone, then another callback before the escape
        _, state = outcome(story, "DoorOfTime_CheckStoneNum", state)
        assert (state[BRIDGE], state["Step_DoorOfTime"]) == (True, "Step03" if natural else before)
        assert state["DoorOfTime_GetStoneCount"] == 0
    escape, state = outcome(story, "DoorOfTime_Escape", state)
    state[ESCAPED] = True  # the engine records the played escape
    assert escape[-1] == REWARD
    assert (state[BRIDGE], state["Step_DoorOfTime"]) == (False, "Step04" if natural else before)
    for _ in range(2):
        again, after = outcome(story, "DoorOfTime_CheckStoneNum", state)
        assert again == [("GameDataActor", SET_INT, COUNT_RESET)]  # no step, no raise; the count tail stays
        assert after == state
    # The native callback rewinds the quest and closes the bridge again, now for good.
    _, old = outcome(native, "DoorOfTime_CheckStoneNum", state)
    assert (old[BRIDGE], old["Step_DoorOfTime"]) == (True, "Step03")


def test_rauru_still_completes_the_quest_from_any_step():
    old = door_flow().flowchart
    new = transformed(DOOR, door_flow()).flowchart
    assert index(new, "Event93") == index(old, "Event93")
    assert named(new, "Event93") == named(old, "Event93")
    assert "ClawshotDoorEvent93Write" not in [event.name for event in new.events]
    for current in STEPS:
        state = {**START, "Step_DoorOfTime": current}
        effects, final = outcome(new, "SageRoom_MeetRauru", state)
        assert (effects, final) == outcome(old, "SageRoom_MeetRauru", state)
        assert final["Step_DoorOfTime"] == "Complete"


def test_the_expression_query_is_registered_once_when_the_actor_lacks_it():
    document = castle_flow()
    actors = document.flowchart.actors
    actors[1].queries = ["EventQueryIsGameDataBool"]
    new = transformed(CASTLE, document).flowchart
    assert [actor.name for actor in new.actors] == [actor.name for actor in actors]
    assert new.actors[1].queries == ["EventQueryIsGameDataBool", BOOL_EXP]
    assert new.actors[1].actions == actors[1].actions
    guard = named(new, "Event32")
    assert (guard.actor, guard.query) == (1, 1)


def _set(name, field, value):
    def mutate(fc):
        named(fc, name).params[field] = value

    return mutate


def _retarget(name, target):
    def mutate(fc):
        named(fc, name).next = index(fc, target)

    return mutate


def _notice_action(fc):
    named(fc, "Event57").action = fc.actors[0].actions.index(NOTICE)


def _rename(fc):
    named(fc, "Event148").name = "Event148Moved"


def _unknown_writer(fc):
    fc.events.append(evfl.ActionEvent("Event300", 0, 0, evfl.NONE, {**WRITE, "StepName": "Step03"}))


def _no_game_data_actor(fc):
    fc.actors[0].name = "GameDataActorTest"


def _bound_game_data_actor(fc):
    fc.actors[0].entry_point = 0


def _second_game_data_actor(fc):
    fc.actors.append(evfl.Actor("GameDataActor"))


def _bridge_end(fc):
    named(fc, "Event77").next = evfl.NONE


@pytest.mark.parametrize(
    "path,mutate,match",
    [
        pytest.param(DOOR, _set("Event7", "StepName", "Step03"), "DoorOfTime/Event7", id="step"),
        pytest.param(DOOR, _set("Event12", "ChallengeName", "Get_StoneOfFire"), "DoorOfTime/Event12", id="quest"),
        pytest.param(CASTLE, _set("Event32", "IsIgnoreCompletedChallenge", False), "Event32", id="first-write"),
        pytest.param(SARIA, _set("Event172", "IsIgnoreChallengeProgressUI", False), "Event172", id="quiet-write"),
        pytest.param(DOOR, _set("Event93", "StepName", "Step06"), "DoorOfTime/Event93", id="complete"),
        pytest.param(DOOR, _retarget("Event14", "Event146"), "Event14.*next 'Event146'", id="tail"),
        pytest.param(ZELDA, _retarget("Event42", "Event43"), "Event42.*next 'Event43'", id="end-tail"),
        pytest.param(DOOR, _notice_action, "DoorOfTime/Event57", id="action"),
        pytest.param(DOOR, _rename, r"\['Event148'\]", id="missing"),
        pytest.param(DOOR, _unknown_writer, r"\['Event300'\]", id="unknown-writer"),
        pytest.param(SARIA, _no_game_data_actor, "GameDataActor", id="no-game-data-actor"),
        pytest.param(ZELDA, _bound_game_data_actor, "GameDataActor", id="bound-game-data-actor"),
        pytest.param(CASTLE, _second_game_data_actor, "GameDataActor", id="two-game-data-actors"),
        pytest.param(DOOR, _set("Event77", "Value", False), "DoorOfTime/Event77", id="bridge-value"),
        pytest.param(DOOR, _bridge_end, "Event77.*next None", id="bridge-tail"),
    ],
)
def test_changed_native_writers_are_refused_with_their_values(path, mutate, match):
    document = FLOWS[path]()
    mutate(document.flowchart)
    with pytest.raises(PatchError, match=match):
        door_story.changes()[path](evfl.write(document))


def test_another_flowchart_and_a_second_application_are_refused():
    with pytest.raises(PatchError, match="DoorOfTime"):
        door_story.changes()[DOOR](evfl.write(castle_flow()))
    for path in PATHS:
        once = door_story.changes()[path](evfl.write(FLOWS[path]()))
        with pytest.raises(PatchError, match="ClawshotDoor"):
            door_story.changes()[path](once)


def test_darunia_fire_guard_composes_in_either_order():
    _, after, before = assert_composes(evfl.write(door_flow()), DOOR, [darunia.changes()[darunia.DOOR_FLOW]])
    native = door_flow().flowchart
    for current in STEPS:
        for fire in FIRE:
            state = {**START, "Step_DoorOfTime": current, "Step_Get_StoneOfFire": fire}
            reference = {"forward": ("DoorOfTime", "Get_StoneOfFire"), "bridge": True}
            expected = outcome(native, "DoorOfTime_SendOff", state, **reference)
            assert outcome(after, "DoorOfTime_SendOff", state) == expected
            assert outcome(before, "DoorOfTime_SendOff", state) == expected
    natural = {**START, "Step_DoorOfTime": "Step01"}
    effects, final = outcome(before, "DoorOfTime_SendOff", natural)
    assert (final["Step_DoorOfTime"], final["Step_Get_StoneOfFire"]) == ("Step02", "KakarikoVillageNpc")
    assert [effect[2]["StepName"] for effect in effects if effect[1] == STEP] == ["Step02", "KakarikoVillageNpc"]


@pytest.fixture(scope="module")
def native(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    flows = {path: dictionaries.decompress(path, (romfs / path).read_bytes()) for path in PATHS}
    data = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))["Data"]
    enums = {int(row["Hash"]): row for row in data["Enum"]}
    orders = {quest: tuple(enums[key(f"Step_{quest}")]["RawValues"]) for quest in ("DoorOfTime", "Get_StoneOfFire")}
    return flows, data, orders


@pytest.fixture(scope="module")
def patched(native):
    flows, _, _ = native
    return {path: door_story.changes()[path](data) for path, data in flows.items()}


@pytest.mark.dump
def test_dump_native_step_order_and_unsaved_strict_predicates(native):
    flows, data, orders = native
    assert orders["DoorOfTime"] == STEPS
    enum = {int(row["Hash"]): row for row in data["Enum"]}[key("Step_DoorOfTime")]
    assert int(enum["DefaultValue"]) == key("NotReady")
    assert [int(value) for value in enum["Values"]] == [key(step) for step in STEPS]
    expressions = {int(row["Hash"]): row for row in data["BoolExp"]}
    for _, _, step, _ in GUARDS:
        row = expressions[key(f"DoorOfTime_IsAfter_{step}_Exp")]
        assert [[int(value) for value in term] for term in row["Values"]] == [
            [12, key("Step_DoorOfTime")],  # native enum-read operand
            [2, key(step)],  # native strict-greater operand
        ]
        assert (int(row["ResetTypeValue"]), int(row["SaveFileIndex"])) == (0, -1)  # derived, never saved
    # Case 0 is the true branch: with Water complete as well, the native stone count steps to Step03.
    fc = evfl.read(flows[DOOR]).flowchart
    gate = named(fc, "Event39")
    assert gate.params == {"GameDataName": "Get_StoneOfWater_IsCompleted_Exp"}
    assert gate.cases == [(0, index(fc, "Event37")), (1, index(fc, "Event147"))]
    assert named(fc, "Event37").params["StepName"] == "Step03"


@pytest.mark.dump
def test_dump_every_native_door_writer_is_guarded_or_the_complete_one(romfs):
    """The loose event flows; the external audit also found no writer in pack members, AINB or other data."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    found = []
    for file in sorted((romfs / "Event/EventFlow").glob("*.bfevfl.zs")):
        path = file.relative_to(romfs).as_posix()
        fc = evfl.read(dictionaries.decompress(path, file.read_bytes())).flowchart
        if fc is None:
            continue
        for event in fc.events:
            params = getattr(event, "params", None) or {}
            if not isinstance(event, evfl.ActionEvent) or params.get("ChallengeName") != "DoorOfTime":
                continue
            if fc.actors[event.actor].actions[event.action] == STEP:
                found.append((path, event.name, params["StepName"]))
    expected = [(path, writer, step) for path, writer, step, _ in GUARDS] + [(DOOR, "Event93", "Complete")]
    assert sorted(found) == sorted(expected)


@pytest.mark.dump
@pytest.mark.parametrize("path", PATHS)
def test_dump_only_the_lower_writers_change(native, patched, path):
    flows, _, _ = native
    out = patched[path]
    assert evfl.write(evfl.read(out)) == out
    assert_only_guarded(evfl.read(flows[path]), evfl.read(out), path)


@pytest.mark.dump
@pytest.mark.parametrize("path,writer,step,tail", GUARDS)
@pytest.mark.parametrize("boundary", BOUNDARIES)
def test_dump_writers_skip_only_their_own_write(native, patched, path, writer, step, tail, boundary):
    flows, _, orders = native
    old, new = evfl.read(flows[path]).flowchart, evfl.read(patched[path]).flowchart
    check_boundary(old, new, writer, step, tail, boundary, {**ORDERS, **orders})


@pytest.mark.dump
@pytest.mark.parametrize("before", ("Step2_2", "Step06", "Complete"))  # natural, song-only opening, early pull
def test_dump_the_bridge_rises_for_the_escape_and_never_after_it(native, patched, before):
    """The real stone count and escape: repeated counts before it raise the bridge, the escape lowers it once."""
    flows, _, orders = native
    orders = {**ORDERS, **orders}
    story, old = evfl.read(patched[DOOR]).flowchart, evfl.read(flows[DOOR]).flowchart
    natural = before == "Step2_2"
    stones = {"Step_Get_StoneOfFire": "Complete", "Step_Get_StoneOfWater": "Complete"}
    state = {**START, **stones, "Step_DoorOfTime": before}
    for _ in range(2):
        _, state = outcome(story, "DoorOfTime_CheckStoneNum", state, orders=orders)
        assert (state[BRIDGE], state["Step_DoorOfTime"]) == (True, "Step03" if natural else before)
    escape, after = outcome(story, "DoorOfTime_Escape", state, orders=orders)
    native_escape, _ = outcome(old, "DoorOfTime_Escape", state, orders=orders)
    step04 = ("ChallengeSystemActor", STEP, named(old, "Event12").params)
    assert escape == (native_escape if natural else [effect for effect in native_escape if effect != step04])
    assert ("GameDataActor", SET_BOOL, {**BRIDGE_UP, "Value": False}) in escape  # native Event78
    state = {**after, ESCAPED: True}  # the engine records the played escape
    assert (state[BRIDGE], state["Step_DoorOfTime"]) == (False, "Step04" if natural else before)
    for _ in range(2):
        again, later = outcome(story, "DoorOfTime_CheckStoneNum", state, orders=orders)
        assert again == [("GameDataActor", SET_INT, COUNT_RESET)]  # no step, no raise; the count tail stays
        assert later == state
    _, rewound = outcome(old, "DoorOfTime_CheckStoneNum", state, orders=orders)
    assert (rewound[BRIDGE], rewound["Step_DoorOfTime"]) == (True, "Step03")  # what the native count would do


def _check_composed(path, alone, composed, orders, forward):
    """From each guarded action and state, ``composed`` plays as ``alone`` on the story's reference engine."""
    for name, _ in guarded_of(path):
        for current, fire, escaped in product(STEPS, ("Ready", "KakarikoVillageNpc", "Complete"), (False, True)):
            stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": "Complete"}
            state = {**START, **stones, "Step_DoorOfTime": current, ESCAPED: escaped}
            expected = outcome(alone, index(alone, name), state, orders=orders, forward=forward, bridge=True)
            for fc in composed:
                assert outcome(fc, index(fc, name), state, orders=orders) == expected, (name, state)


@pytest.mark.dump
def test_dump_darunia_fire_guard_composes_in_either_order(native):
    flows, _, orders = native
    orders = {**ORDERS, **orders}
    _, after, before = assert_composes(flows[DOOR], DOOR, [darunia.changes()[darunia.DOOR_FLOW]])
    old = evfl.read(flows[DOOR]).flowchart
    _check_composed(DOOR, old, (after, before), orders, ("DoorOfTime", "Get_StoneOfFire"))


@pytest.mark.dump
def test_dump_composes_with_a_gift_seed_transforms_in_either_order(romfs, native):
    """Every transform a gift-shuffle seed ships for these flows (Darunia's Event62 guard today)."""
    flows, _, orders = native
    orders = {**ORDERS, **orders}
    settings = Settings(shuffle=("Chest", "Shop", gifts.SHUFFLE, "Scrub", "BossHeart"), songs="song")
    spec, settings, gift_step = gifts.seed_setup(romfs, load_spec(), settings)
    output = make_seed(romfs, 11, settings, spec, extra_steps=[gift_step])
    for path in PATHS:
        others = [
            changes[path]
            for changes in output.extra_changes
            if path in changes and getattr(changes[path], "__module__", None) != door_story.__name__
        ]
        alone, after, before = assert_composes(flows[path], path, others)
        _check_composed(path, alone, (after, before), orders, ("DoorOfTime",))


@pytest.mark.dump
def test_dump_composes_with_song_opening_in_either_order(native):
    flows, _, orders = native
    others = [door.song_flow]
    alone, after, before = assert_composes(flows[DOOR], DOOR, others)
    _check_composed(DOOR, alone, (after, before), {**ORDERS, **orders}, ("DoorOfTime",))
