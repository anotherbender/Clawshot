"""Door of Time story order: the quest moves only forward after an early pull, and any stone order reaches the escape.

Synthetic flows are invented on the native contracts of the round 16 DoorOfTime audit, never cut from the game.
Dump-marked tests read the real flows and GameData, and compose with the transforms already shipped for them.
The runner follows state-changing events only; engine timing, presentation and save behavior still need play.

Every door mode ships the order repair: the stone count raises the field drawbridge only once Impa's real
send-off has played and never after the escape, and the send-off counts the stones again, so Fire and Water won
before the courtyard (whose native Step01 always stays) still reach Step03 and the escape. The early modes also
keep every lower DoorOfTime write forward-only.
"""

from copy import deepcopy
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
STORY = (DOOR, SARIA, ZELDA)  # the flows the early door story changes
PATHS = (*STORY, CASTLE)  # every flow holding a native DoorOfTime write
MODES = ("closed", "song_only", "open")
EARLY = MODES[1:]
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
SENDOFF_SCENE = "Dm_HrlField_0020"  # Impa's field send-off
ESCAPE_EVENT = "HyruleField_DoorOfTime_Escape"
SENDOFF = f"HavePlayedEvent.{SENDOFF_SCENE}"
ESCAPED = f"HavePlayedEvent.{ESCAPE_EVENT}"
BRIDGE = "IsHyruleFieldBridgeClose"
OPENED = "Market_Child_TimeTempleDoor_Opened"
OPENING = "HavePlayedEvent.Dm_TimeTemple_0010"
TIME_SONG = "IsGet.Item_Melody_TimeSong"
START = {
    "Step_Get_StoneOfForest": "Complete",
    "Step_Get_StoneOfFire": "Ready",
    "Step_Get_StoneOfWater": "Ready",
    SENDOFF: True,
    ESCAPED: False,
    BRIDGE: False,
    OPENED: False,
    OPENING: False,
    TIME_SONG: True,
}
STONES = (("Ready", "Ready"), ("Complete", "Ready"), ("Ready", "Complete"), ("Complete", "Complete"))  # Fire, Water
# Every lower DoorOfTime writer the early modes guard: (flow, writer, step written, native next or None).
GUARDS = (
    (DOOR, "Event7", "Step02", "Event62"),
    (DOOR, "Event147", "Step2_1", "Event5"),
    (DOOR, "Event148", "Step2_2", "Event5"),
    (DOOR, "Event37", "Step03", "Event77"),
    (DOOR, "Event12", "Step04", "Event140"),
    (DOOR, "Event14", "Step05", "Event171"),
    (DOOR, "Event57", "Step06", None),
    (SARIA, "Event172", "Srep2_1_1", None),
    (ZELDA, "Event42", "Srep2_1_1", None),
)
# The native writers every mode keeps: the courtyard's forced Step01, which returns any stone or Saria advance
# before Zelda to the exact step Impa waits for, and Rauru's Complete.
NATIVE = ((CASTLE, "Event32", "Step01"), (DOOR, "Event93", "Complete"))
BOUNDARIES = ("before", "equal", "after", "complete")
COUNT = "DoorOfTime_CheckStoneNum"
STONE_COUNT = "DoorOfTime_GetStoneCount"  # native GameData Int; every save starts at its DefaultValue 2
BRIDGE_UP = {"GameDataName": BRIDGE, "Index": -1, "Value": True}
RECOUNT = ("call", "", COUNT, {})  # the send-off's own stone count, as the runner records the call

STEP = "EventExecuteProgressChallengeStep"
NOTICE = "EventTriggerShowChallengeProgressUI"
BOOL_EXP = "EventQueryIsGameDataBoolExp"
READ_BOOL = "EventQueryIsGameDataBool"
HAVE_PLAYED = "EventQueryHavePlayedEvent"
MELODY = "EventQueryIsRecommendedMelody"
SET_BOOL = "EventTriggerSetGameDataBool"
SET_INT = "EventTriggerSetGameDataInt"
TRANSITION = "EventTransition"
KEEP_CAMERA = "EventTriggerSendKeepStateMessageToPlayerCamera"
SAVE_POINT = "EventTriggerCameraSavePoint"
DUCKING = "EventSoundRequestDucking"
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


def scene(name, event_name, next_name):
    return (name, "act", "EventSystemActor", TRANSITION, {"EventName": event_name}, next_name)


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
    """Impa's lesson and send-off, stone count, escape, Song of Time aftermath, door opening and Rauru's Complete."""
    return chart(
        "DoorOfTime",
        [
            ("ChallengeSystemActor", [STEP, NOTICE], []),
            ("GameDataActor", [SET_BOOL, SET_INT], [HAVE_PLAYED, BOOL_EXP, READ_BOOL]),
            ("EventSystemActor", [TRANSITION], []),
            ("EventWorldManagerController", ["Event_ResetWeatherForFlowchart"], []),
            ("EventCamera", [KEEP_CAMERA, SAVE_POINT], []),
            ("SoundSystemActor", [BGM, DUCKING], []),
            ("GameSystemActor", [], [MELODY]),
        ],
        [
            # Impa's talk at exactly Step01 plays Zelda's Lullaby lesson; her field send-off writes Step02, then
            # Fire's own Kakariko step (Darunia's Event62 guard).
            scene("Event21", "Dm_MelodyGet_Zelda", None),
            write("Event7", "Step02", "Event62"),
            write("Event62", "KakarikoVillageNpc", None, darunia.STEP_WRITE),
            scene("Event65", SENDOFF_SCENE, "Event7"),
            # A stone count: Fire or Water alone steps to Step2_1 or Step2_2, both to Step03 and the bridge raise.
            ask("Event38", "Get_StoneOfFire_IsCompleted_Exp", {0: "Event39", 1: "Event56"}),
            ask("Event39", "Get_StoneOfWater_IsCompleted_Exp", {0: "Event37", 1: "Event147"}),
            ask("Event56", "Get_StoneOfWater_IsCompleted_Exp", {0: "Event148", 1: "Event6"}),
            write("Event37", "Step03", "Event77"),
            data("Event77", SET_BOOL, BRIDGE, True, "Event4"),
            data("Event4", SET_INT, "DoorOfTime_GetStoneCount", 0, None),
            write("Event147", "Step2_1", "Event5"),
            write("Event148", "Step2_2", "Event5"),
            data("Event5", SET_INT, "DoorOfTime_GetStoneCount", 1, None),
            data("Event6", SET_INT, "DoorOfTime_GetStoneCount", 2, None),
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
            # The door opening: the quest gate (past Step04), the saved opened flag, the opening's history and the
            # played song, then the opening scene, the opened write, music and Step06.
            ("Event18", "act", "EventCamera", SAVE_POINT, None, "Event27"),
            ("Event27", "call", "Dm_SY_Ocarina", "PlayOcarinaSequence", {"MelodyType": 4}, "Event92"),
            ("Event92", "act", "SoundSystemActor", DUCKING, None, "Event60"),
            ask("Event60", "DoorOfTime_IsAfter_Step04_Exp", {0: "Event69"}),
            ("Event69", "ask", "GameDataActor", READ_BOOL, {"GameDataName": OPENED, "Index": -1}, {1: "Event58"}),
            ("Event58", "ask", "GameDataActor", HAVE_PLAYED, {"EventName": "Dm_TimeTemple_0010"}, {1: "Event28"}),
            ("Event28", "ask", "GameSystemActor", MELODY, None, {0: "Event17"}),
            scene("Event17", "Dm_TimeTemple_0010", "Event53"),
            data("Event53", SET_BOOL, OPENED, True, "Event145"),
            ("Event145", "act", "SoundSystemActor", BGM, {"StartType": 0, "BgmName": "BGM_Test"}, "Event57"),
            write("Event57", "Step06", None),
            # Rauru: Complete after the Recovery sub flow, never guarded.
            ("Event102", "call", "", "Recovery", None, "Event93"),
            write("Event93", "Complete", None),
            data("Event76", SET_BOOL, "IsTestRecovered", True, None),
        ],
        [
            ("Step01_Npc_Hylia_Impa_Child_Talk", "Event21", []),
            ("DoorOfTime_SendOff", "Event65", []),
            (COUNT, "Event38", []),
            ("DoorOfTime_Escape", "Event89", ["Event111"]),
            ("Dm_MelodyGet_Time_After", "Event204", []),
            ("DoorOfTime_OpenDoor", "Event18", ["Event27"]),
            ("Recovery", "Event76", []),
            ("SageRoom_MeetRauru", "Event102", ["Event102"]),
            ("TestStartsAtAWriter", "Event57", []),  # an entry may name a writer itself
        ],
    )


def castle_flow():
    """The courtyard meeting: Zelda's quest completes, the forced DoorOfTime Step01, then wait/fade/notice/camera."""
    return chart(
        "Goto_HyruleCastle",
        [
            ("ChallengeSystemActor", [STEP, NOTICE], []),
            ("GameDataActor", [SET_BOOL], [READ_BOOL, BOOL_EXP]),
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
            ("GameDataActor", [SET_BOOL, SET_INT], [BOOL_EXP, READ_BOOL]),
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


def run(fc, start, state, *, orders=ORDERS, forward=(), order=False, scenes=False, entry=None):
    """Follow ``fc`` from event ``start``; return its effects and update ``state`` (``Step_<quest>``, data).

    Case 0 is a true query, as native gates use it; the requested melody is always the one played. Sub flow calls
    are effects, checked against ``entry``'s registrations; only a call of this flowchart's own stone count is
    followed. With ``scenes``, a transition records its event's ``HavePlayedEvent`` history as it plays
    [INFERENCE: the send-off's history is set before its flow continues; native clock and gates read it].

    A reference engine models the story's promises on a flow without them: it never moves the ``forward`` quests
    back; with ``order`` the stone count entry runs only after the send-off and before the escape, and the
    send-off's Step02 (native Event7) is followed by that count before its native continuation."""
    effects = []
    budget = [2000]

    def holds(actor, query, params):
        if (actor, query) == ("GameSystemActor", MELODY):
            return True
        assert actor == "GameDataActor", (actor, query, params)
        if query == HAVE_PLAYED:
            return state[f"HavePlayedEvent.{params['EventName']}"]
        if query == READ_BOOL:
            return state[params["GameDataName"]]
        assert query == BOOL_EXP, (query, params)
        expression = params["GameDataName"]
        quest, after, step = expression.removesuffix("_Exp").partition("_IsAfter_")
        if after:
            return orders[quest].index(state[f"Step_{quest}"]) > orders[quest].index(step)
        assert expression.endswith("_IsCompleted_Exp"), expression
        return state[f"Step_{expression.removesuffix('_IsCompleted_Exp')}"] == "Complete"

    def dropped(action, params):
        if action == STEP and params["ChallengeName"] in forward:
            steps = orders[params["ChallengeName"]]
            return steps.index(state[f"Step_{params['ChallengeName']}"]) > steps.index(params["StepName"])
        return False

    def count():
        if not order or (state[SENDOFF] and not state[ESCAPED]):
            walk(fc.entry_point(COUNT).main_event, evfl.NONE)

    def walk(at, stop):
        while at not in (evfl.NONE, stop):
            budget[0] -= 1
            assert budget[0] > 0, effects
            event = fc.events[at]
            params = getattr(event, "params", None) or {}
            if isinstance(event, evfl.SwitchEvent):
                actor = fc.actors[event.actor]
                true = holds(actor.name, actor.queries[event.query], params)
                at = dict(event.cases).get(0 if true else 1, evfl.NONE)
            elif isinstance(event, evfl.ForkEvent):
                for fork in event.forks:
                    walk(fork, event.join)
                at = event.join
            elif isinstance(event, evfl.JoinEvent):
                at = event.next
            elif isinstance(event, evfl.SubFlowEvent):
                assert entry is None or at in entry.sub_flow_events, f"{event.name} is not registered"
                effects.append(("call", event.flowchart, event.entry_point, params))
                if event.flowchart in ("", fc.name) and event.entry_point == COUNT:
                    walk(fc.entry_point(COUNT).main_event, evfl.NONE)
                at = event.next
            elif isinstance(event, evfl.ActionEvent):
                actor = fc.actors[event.actor]
                action = actor.actions[event.action]
                if not dropped(action, params):
                    if action == STEP:
                        state[f"Step_{params['ChallengeName']}"] = params["StepName"]
                    elif action in (SET_BOOL, SET_INT):
                        state[params["GameDataName"]] = params["Value"]
                    elif action == TRANSITION and scenes:
                        state[f"HavePlayedEvent.{params['EventName']}"] = True
                    effects.append((actor.name, action, params))
                if order and (fc.name, event.name) == ("DoorOfTime", "Event7"):
                    effects.append(RECOUNT)
                    count()
                at = event.next
            else:
                raise AssertionError(f"unmodeled event {event}")

    if order and entry is not None and entry.name == COUNT:
        count()
    else:
        walk(start, evfl.NONE)
    return effects


def outcome(fc, start, state, **options):
    """Effects and final state from entry point ``start`` (a name) or event ``start`` (an index)."""
    state = dict(state)
    if isinstance(start, str):
        entry = fc.entry_point(start)
        return run(fc, entry.main_event, state, entry=entry, **options), state
    return run(fc, start, state, **options), state


def reference(mode, path=DOOR):
    """What the door story promises for a ``mode`` seed on the flow without it: the order repair on the door flow
    in every mode, and forward-only lower writes in the early modes (never the courtyard's)."""
    forward = ("DoorOfTime",) if mode in EARLY and path in STORY else ()
    return {"forward": forward, "order": path == DOOR}


STORY_ONLY = {"forward": ("DoorOfTime",), "order": True}  # the early door story alone, on the door flow


def index(fc, name):
    return next(i for i, event in enumerate(fc.events) if event.name == name)


def named(fc, name):
    return fc.events[index(fc, name)]


def flows_for(sources, mode):
    """``sources`` (path -> bytes) as a ``mode`` seed ships them, and the same without the door story's edits:
    the door mode's changes (song_only's altar flow under the story), then Darunia's Fire guard on the door flow
    (every seed has it, after the door changes); a flow neither changes stays native."""
    changes = door.changes({}, mode=mode)
    fire = darunia.changes()[darunia.DOOR_FLOW]
    shipped, base = {}, {}
    for path, data in sources.items():
        new = changes[path](data) if path in changes else data
        old = door.song_flow(data) if (mode, path) == ("song_only", DOOR) else data
        if path == DOOR:
            new, old = fire(new), fire(old)
        shipped[path], base[path] = evfl.read(new).flowchart, evfl.read(old).flowchart
    return shipped, base


def synthetic(mode):
    """The four synthetic writer flows as a ``mode`` seed ships them, and without the door story."""
    return flows_for({path: evfl.write(build()) for path, build in FLOWS.items()}, mode)


def guards_of(path):
    return [guard for guard in GUARDS if guard[0] == path]


def at_boundary(step, boundary):
    i = STEPS.index(step)
    return {"before": STEPS[i - 1], "equal": step, "after": STEPS[i + 1], "complete": "Complete"}[boundary]


def transformed(path, document, early=True):
    return evfl.read(door_story.changes(early=early)[path](evfl.write(document)))


def counted(state):
    """Independent model of the native stone count: the step its Fire and Water quests lead to, or None."""
    fire, water = (state[f"Step_Get_StoneOf{stone}"] == "Complete" for stone in ("Fire", "Water"))
    return {(True, True): "Step03", (True, False): "Step2_1", (False, True): "Step2_2"}.get((fire, water))


def latest(*steps):
    return max((step for step in steps if step), key=STEPS.index)


def scenes_of(effects):
    return [effect[2]["EventName"] for effect in effects if effect[1] == TRANSITION]


def escape_ready(state, mode):
    """Independent model of the escape area: closed keeps the native area at exactly Step03; the early stage's
    predicate wants Step03 or later, the Fire and Water quests the count reads, the send-off and no escape yet."""
    at = STEPS.index(state["Step_DoorOfTime"])
    if mode == "closed":
        return at == STEPS.index("Step03")
    stones = all(state[f"Step_Get_StoneOf{stone}"] == "Complete" for stone in ("Fire", "Water"))
    return at > STEPS.index("Step2_2") and stones and state[SENDOFF] and not state[ESCAPED]


def door_opens(flows, state, mode, orders=ORDERS):
    """Whether the Door of Time opens now, the Time song learned: the shipped altar flow decides in closed and
    song_only; open's physical door module reads the send-off history (door.build rebinds it)."""
    if mode == "open":
        return state[door.SENDOFF]
    effects, _ = outcome(flows[DOOR], "DoorOfTime_OpenDoor", state, orders=orders)
    return "Dm_TimeTemple_0010" in scenes_of(effects)


def expected_story(old, path, early=True):
    """``old`` with exactly the contracted edits. Early modes: each lower writer becomes a strict IsAfter query at
    its own index and its write moves to the end, native next kept. The door flow in every mode: the counter
    entry first asks for the played send-off, then for an unplayed escape, before native Event38 (a missing case
    ends it); the send-off's Step02 continues through its own registered count, then native Event62."""
    fc = deepcopy(old)
    actor = next(i for i, candidate in enumerate(fc.actors) if candidate.name == "GameDataActor")
    queries = fc.actors[actor].queries
    moved = {}
    for _, name, step, _ in guards_of(path) if early else ():
        at = index(fc, name)
        write = fc.events[at]
        moved[name] = len(fc.events)
        fc.events.append(replace(write, name=f"ClawshotDoor{name}Write"))
        cases = [(1, moved[name])] if write.next == evfl.NONE else [(0, write.next), (1, moved[name])]
        expression = {"GameDataName": f"DoorOfTime_IsAfter_{step}_Exp"}
        fc.events[at] = evfl.SwitchEvent(name, actor, queries.index(BOOL_EXP), cases, expression)
    if path == DOOR:
        sendoff, escape, recount = range(len(fc.events), len(fc.events) + 3)
        counter = fc.entry_point(COUNT)
        played = queries.index(HAVE_PLAYED)
        fc.events += [
            evfl.SwitchEvent("ClawshotDoorCountSendoff", actor, played, [(0, escape)], {"EventName": SENDOFF_SCENE}),
            evfl.SwitchEvent(
                "ClawshotDoorCountEscape", actor, played, [(1, counter.main_event)], {"EventName": ESCAPE_EVENT}
            ),
            evfl.SubFlowEvent("ClawshotDoorSendoffRecount", "", COUNT, index(fc, "Event62"), None),
        ]
        counter.main_event = sendoff
        fc.entry_point("DoorOfTime_SendOff").sub_flow_events.append(recount)
        if early:
            named(fc, "Event7").cases = [(0, recount), (1, moved["Event7"])]
            fc.events[moved["Event7"]].next = recount
        else:
            named(fc, "Event7").next = recount
    return fc


def check_boundary(old, new, writer, step, tail, boundary, orders=ORDERS):
    """From the writer's index: before/equal run the native write, after/Complete skip it. The tail stays native
    but for the send-off's own stone count after Event7, which waits for the send-off and ends with the escape."""
    current = at_boundary(step, boundary)
    write = ("ChallengeSystemActor", STEP, named(old, writer).params)
    for (sendoff, escaped), (fire, water) in product(product((False, True), repeat=2), STONES):
        stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
        state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped}
        native_effects, _ = outcome(old, index(old, writer), state, orders=orders)
        assert native_effects[0] == write
        assert bool(native_effects[1:]) == (tail is not None)  # the continuation has effects of its own
        effects, final = outcome(new, index(new, writer), state, orders=orders)
        assert (effects, final) == outcome(old, index(old, writer), state, orders=orders, **STORY_ONLY)
        assert (write in effects) == (STEPS.index(current) <= STEPS.index(step))
        assert (RECOUNT in effects) == (writer == "Event7")
        recounted = writer == "Event7" and sendoff and not escaped
        assert final["Step_DoorOfTime"] == latest(current, step, counted(state) if recounted else None)
        assert final[BRIDGE] is (writer == "Event37" or (recounted and counted(state) == "Step03"))


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


def assert_composes(source, path, others, early=True):
    """Apply ``others`` alone, then after and before the door story; both orders must agree and add exactly the
    contracted edits to ``others`` alone."""
    story = door_story.changes(early=early)[path]

    def chain(data):
        for transform in others:
            data = transform(data)
        return data

    alone = evfl.read(chain(source)).flowchart
    after = evfl.read(story(chain(source))).flowchart
    before = evfl.read(chain(story(source))).flowchart
    assert canonical(after) == canonical(before)
    assert canonical(after) == canonical(expected_story(alone, path, early))
    return alone, after, before


def check_composed(path, alone, composed, orders, early=True):
    """From each changed event or entry and each state, ``composed`` plays as promised on ``alone``."""
    starts = [index(alone, name) for _, name, _, _ in guards_of(path)] if early else []
    if path == DOOR:
        starts += [COUNT, "DoorOfTime_SendOff", *(() if early else (index(alone, "Event7"),))]
    options = {"forward": ("DoorOfTime",) if early else (), "order": path == DOOR}
    fires = ("Ready", "KakarikoVillageNpc", "Complete")
    for start, current, fire, sendoff, escaped in product(starts, STEPS, fires, (False, True), (False, True)):
        stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": "Complete"}
        state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped}
        expected = outcome(alone, start, state, orders=orders, **options)
        for flow in composed:
            assert outcome(flow, start, state, orders=orders) == expected, (start, state)


def flow_name(path):
    return path.rsplit("/", 1)[-1].removesuffix(".bfevfl.zs")


CHANGES = [pytest.param(path, True, id=f"early-{flow_name(path)}") for path in STORY]
CHANGES.append(pytest.param(DOOR, False, id="every-mode-DoorOfTime"))


@pytest.mark.parametrize("path,early", CHANGES)
def test_only_the_contracted_events_change_and_every_reference_survives(path, early):
    out = door_story.changes(early=early)[path](evfl.write(FLOWS[path]()))
    assert evfl.write(evfl.read(out)) == out
    assert evfl.read(out).flowchart == expected_story(FLOWS[path]().flowchart, path, early)


@pytest.mark.parametrize("path,writer,step,tail", GUARDS)
@pytest.mark.parametrize("boundary", BOUNDARIES)
def test_a_writer_advances_to_its_step_but_never_moves_the_quest_back(path, writer, step, tail, boundary):
    old = FLOWS[path]().flowchart
    check_boundary(old, transformed(path, FLOWS[path]()).flowchart, writer, step, tail, boundary)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("path", PATHS)
def test_every_entry_plays_as_promised_on_the_reference_engine(mode, path):
    """In every mode the stone count waits for the send-off and ends with the escape, and the send-off counts
    again; the early modes never move DoorOfTime back; everything else, the courtyard included, is native."""
    flows, base = synthetic(mode)
    new, old = flows[path], base[path]
    if path == CASTLE or (mode == "closed" and path != DOOR):
        assert new == old
    for entry, current in product(old.entry_points, STEPS):
        for (fire, water), (sendoff, escaped) in product(STONES, product((False, True), repeat=2)):
            stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
            state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped}
            effects, final = outcome(new, entry.name, state)
            assert (effects, final) == outcome(old, entry.name, state, **reference(mode, path)), (entry.name, state)
            if mode in EARLY and path in STORY:
                assert STEPS.index(final["Step_DoorOfTime"]) >= STEPS.index(current)


@pytest.mark.parametrize("current", ("Step06", "Complete"))
def test_skipped_writes_keep_the_reward_camera_and_notice_tails(current):
    state = {**START, "Step_DoorOfTime": current}
    story = transformed(DOOR, door_flow()).flowchart
    escape, escaped = outcome(story, "DoorOfTime_Escape", state)
    assert escape[-1] == REWARD  # the registered reward call after the skipped Step04
    song, sung = outcome(story, "Dm_MelodyGet_Time_After", state)
    assert song[:2] == [("EventCamera", KEEP_CAMERA, CAMERA), ("ChallengeSystemActor", NOTICE, DOOR_NOTICE)]
    for effects, final in ((escape, escaped), (song, sung)):
        door_writes = [e for e in effects if e[1] == STEP and e[2]["ChallengeName"] == "DoorOfTime"]
        assert door_writes == []
        assert final["Step_DoorOfTime"] == current


# Steps the courtyard can meet: the quest's first ones, and stone or Saria advances a save made before the order
# repair may carry.
BEFORE_ZELDA = ("NotReady", "Ready", "Step2_1", "Srep2_1_1", "Step2_2", "Step03")


def check_courtyard(flows, base, orders=ORDERS):
    """The shipped courtyard is the native one, and its forced Step01 brings back the exact step Impa waits for."""
    assert flows[CASTLE] == base[CASTLE]
    for current in BEFORE_ZELDA:
        state = {**START, "Step_DoorOfTime": current, SENDOFF: False}
        effects, final = outcome(flows[CASTLE], "Goto_HyruleCastle_MeetZelda", state, orders=orders)
        writes = [effect[2] for effect in effects if effect[1] == STEP]
        assert [(write["ChallengeName"], write["StepName"]) for write in writes][-1] == ("DoorOfTime", "Step01")
        assert (final["Step_DoorOfTime"], final["Step_Goto_HyruleCastle"]) == ("Step01", "Complete")
        lesson, _ = outcome(flows[DOOR], "Step01_Npc_Hylia_Impa_Child_Talk", final, orders=orders)
        assert scenes_of(lesson) == ["Dm_MelodyGet_Zelda"]  # Impa's exact-Step01 lesson plays


@pytest.mark.parametrize("mode", MODES)
def test_the_courtyard_stays_native_and_returns_the_quest_to_step01(mode):
    check_courtyard(*synthetic(mode))


def check_count_gate(flows, base, mode, orders=ORDERS):
    """No stone count before the real send-off (no Step2_x/Step03, bridge or count value, so no closed escape area
    before the courtyard) and none after the escape (no rewind, no second raise); in between, the native count.
    The count never reads Forest."""
    histories, forests = list(product((False, True), repeat=2)), ("Ready", "Complete")
    for current, (fire, water), forest, (sendoff, escaped) in product(STEPS, STONES, forests, histories):
        stones = {"Step_Get_StoneOfForest": forest, "Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
        state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped}
        effects, final = outcome(flows[DOOR], COUNT, state, orders=orders)
        if not sendoff or escaped:
            assert (effects, final) == ([], state), state
            continue
        main = base[DOOR].entry_point(COUNT).main_event
        assert (effects, final) == outcome(base[DOOR], main, state, orders=orders, **reference(mode)), state
        step = counted(state)
        assert final["Step_DoorOfTime"] == (latest(current, step) if mode in EARLY else step or current)
        assert final[BRIDGE] is (step == "Step03")


@pytest.mark.parametrize("mode", MODES)
def test_the_stone_count_waits_for_the_send_off_and_ends_with_the_escape(mode):
    check_count_gate(*synthetic(mode), mode)


def check_send_off(flows, base, mode, orders=ORDERS):
    """Impa's real send-off writes Step02, counts the stones it may have missed (none before it), then runs
    Fire's native Kakariko continuation; Fire stays Complete when the stone came first."""
    for fire, water in STONES:
        stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
        state = {**START, **stones, "Step_DoorOfTime": "Step01", SENDOFF: False}
        effects, final = outcome(flows[DOOR], "DoorOfTime_SendOff", state, orders=orders, scenes=True)
        promised = outcome(base[DOOR], "DoorOfTime_SendOff", state, orders=orders, scenes=True, **reference(mode))
        assert (effects, final) == promised, state
        assert scenes_of(effects)[0] == SENDOFF_SCENE and final[SENDOFF]
        steps = [
            (i, effect[2]["ChallengeName"], effect[2]["StepName"])
            for i, effect in enumerate(effects)
            if effect[1] == STEP
        ]
        recount = effects.index(RECOUNT)
        assert steps[0][1:] == ("DoorOfTime", "Step02") and steps[0][0] < recount
        fire_steps = [(i, step) for i, quest, step in steps if quest == "Get_StoneOfFire"]
        assert [step for _, step in fire_steps] == ([] if fire == "Complete" else ["KakarikoVillageNpc"])
        assert all(i > recount for i, _ in fire_steps)  # Fire's native Kakariko continuation follows the count
        assert final["Step_DoorOfTime"] == (counted(state) or "Step02")
        assert final["Step_Get_StoneOfFire"] == ("Complete" if fire == "Complete" else "KakarikoVillageNpc")
        assert final[BRIDGE] is (counted(state) == "Step03")


@pytest.mark.parametrize("mode", MODES)
def test_the_send_off_counts_the_stones_won_before_it(mode):
    check_send_off(*synthetic(mode), mode)


# Stones won before the courtyard, in order; Saria's song plays where it writes (Fire done, Water not started).
HISTORIES = {
    "vanilla": (),
    "Fire first": ("Fire",),
    "Water first": ("Water",),
    "Fire then Water": ("Fire", "Water"),
    "Water then Fire": ("Water", "Fire"),
}


def play_in_order(flows, base, history, mode, orders=ORDERS):
    """One save in story order on the shipped ``flows``: ``history``'s stones before Zelda, the courtyard, Impa's
    lesson and send-off, Saria's song where it writes, the remaining stones, the escape and a later count. Every
    scene plays as promised on ``base`` and meets the independent milestones; the vanilla order is native but for
    the send-off's own count."""

    def play(path, start, state, *, native=not history):
        """``start`` on the shipped flow, as promised on ``base``; with ``native``, as the flow without the order
        repair plays it too."""
        entries = [entry.name for entry in flows[path].entry_points]
        begin = start if start in entries else index(flows[path], start)
        got = outcome(flows[path], begin, state, orders=orders, scenes=True)
        promised = outcome(base[path], begin, state, orders=orders, scenes=True, **reference(mode, path))
        assert got == promised, (path, start, state)
        if native:
            plain = {"forward": reference(mode, path)["forward"]}
            assert got == outcome(base[path], begin, state, orders=orders, scenes=True, **plain), (path, start)
        return got

    def saria(state):
        """Saria's song writes Srep2_1_1 natively only with Fire complete, Water not started, before Step2_2."""
        fire, water = (state[f"Step_Get_StoneOf{stone}"] for stone in ("Fire", "Water"))
        counted_yet = STEPS.index(state["Step_DoorOfTime"]) > STEPS.index("Step2_2")
        if fire == "Complete" and water in ("NotReady", "Ready") and not counted_yet:
            effects, state = play(SARIA, "Event4", state)
            assert state["Step_DoorOfTime"] == "Srep2_1_1", effects
        return state

    state = {**START, "Step_DoorOfTime": "NotReady", SENDOFF: False, STONE_COUNT: 2}
    for stone in history:
        state = {**state, f"Step_Get_StoneOf{stone}": "Complete"}
        effects, state = play(DOOR, COUNT, state)
        assert effects == []  # no count before the send-off: no step, no bridge, no closed escape area
    assert (state["Step_DoorOfTime"], state[BRIDGE]) == ("NotReady", False)
    assert not escape_ready(state, mode) and not door_opens(flows, state, mode, orders)
    _, state = play(CASTLE, "Goto_HyruleCastle_MeetZelda", state)
    assert state["Step_DoorOfTime"] == "Step01"  # the native reset: Impa waits at exactly Step01
    assert not door_opens(flows, state, mode, orders)
    lesson, state = play(DOOR, "Step01_Npc_Hylia_Impa_Child_Talk", state)
    assert scenes_of(lesson) == ["Dm_MelodyGet_Zelda"]
    before = state
    sendoff, state = play(DOOR, "DoorOfTime_SendOff", state, native=False)
    assert scenes_of(sendoff)[0] == SENDOFF_SCENE and state[SENDOFF] and RECOUNT in sendoff
    if not history:  # vanilla: native but for the count's own call and its restatement of the unchanged count
        forward = reference(mode)["forward"]
        effects, plain = outcome(base[DOOR], "DoorOfTime_SendOff", before, orders=orders, scenes=True, forward=forward)
        counts = [e for e in sendoff if e[1] == SET_INT and e[2]["GameDataName"] == STONE_COUNT]
        assert [counter[2]["Value"] for counter in counts] == [before[STONE_COUNT]] == [2]  # native Event6
        assert [effect for effect in sendoff if effect != RECOUNT and effect not in counts] == effects
        assert state == plain
    assert state["Step_DoorOfTime"] == (counted(state) or "Step02")
    assert state[BRIDGE] is (counted(state) == "Step03")
    assert door_opens(flows, state, mode, orders) is (mode in EARLY)
    state = saria(state)
    for stone in ("Fire", "Water"):
        if state[f"Step_Get_StoneOf{stone}"] != "Complete":
            state = {**state, f"Step_Get_StoneOf{stone}": "Complete"}
            _, state = play(DOOR, COUNT, state)
            state = saria(state)
    assert (state["Step_DoorOfTime"], state[BRIDGE]) == ("Step03", True)
    assert escape_ready(state, mode)
    escape, state = play(DOOR, "DoorOfTime_Escape", state)
    state = {**state, ESCAPED: True}  # the engine records the played escape
    assert ("GameDataActor", SET_BOOL, {**BRIDGE_UP, "Value": False}) in escape
    assert (state["Step_DoorOfTime"], state[BRIDGE]) == ("Step04", False)
    assert not escape_ready(state, mode)
    for _ in range(2):  # a later count, as a repeated stone callback would run it
        again, later = play(DOOR, COUNT, state, native=False)
        assert (again, later) == ([], state)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("history", HISTORIES)
def test_any_stone_order_reaches_impa_the_send_off_and_the_escape(mode, history):
    play_in_order(*synthetic(mode), HISTORIES[history], mode)


# (mode, quest step before the counts): the natural Step2_2, and in the early modes the song-only opening's
# Step06 and an early pull's Complete.
AROUND_THE_ESCAPE = [("closed", "Step2_2"), *product(EARLY, ("Step2_2", "Step06", "Complete"))]


def check_bridge_around_the_escape(flows, base, before, orders=ORDERS):
    """Counts after the send-off raise the bridge (and write Step03 where it is the next step), the escape lowers
    it once, and later counts change nothing at all, where the count without the repair rewinds and raises it."""
    natural = before == "Step2_2"
    stones = {"Step_Get_StoneOfFire": "Complete", "Step_Get_StoneOfWater": "Complete"}
    state = {**START, **stones, "Step_DoorOfTime": before}
    for _ in range(2):  # the second stone, then another callback before the escape
        _, state = outcome(flows[DOOR], COUNT, state, orders=orders)
        assert (state[BRIDGE], state["Step_DoorOfTime"]) == (True, "Step03" if natural else before)
    escape, state = outcome(flows[DOOR], "DoorOfTime_Escape", state, orders=orders)
    state = {**state, ESCAPED: True}  # the engine records the played escape
    assert ("GameDataActor", SET_BOOL, {**BRIDGE_UP, "Value": False}) in escape  # native Event78
    assert (state[BRIDGE], state["Step_DoorOfTime"]) == (False, "Step04" if natural else before)
    for _ in range(2):
        assert outcome(flows[DOOR], COUNT, state, orders=orders) == ([], state)
    _, rewound = outcome(base[DOOR], COUNT, state, orders=orders)
    assert (rewound[BRIDGE], rewound["Step_DoorOfTime"]) == (True, "Step03")


@pytest.mark.parametrize("mode,before", AROUND_THE_ESCAPE)
def test_the_bridge_rises_for_the_escape_and_never_after_it(mode, before):
    check_bridge_around_the_escape(*synthetic(mode), before)


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
    document = zelda_flow()
    fc = document.flowchart
    gate = named(fc, "Event43")  # this variant's Water gate reads a saved Bool instead
    fc.actors[0].queries = [READ_BOOL]
    gate.query, gate.params = 0, {"GameDataName": "IsTestWaterStarted", "Index": -1}
    new = transformed(ZELDA, document).flowchart
    assert [actor.name for actor in new.actors] == [actor.name for actor in fc.actors]
    assert new.actors[0].queries == [READ_BOOL, BOOL_EXP]
    assert new.actors[0].actions == fc.actors[0].actions
    guard = named(new, "Event42")
    assert (guard.actor, guard.query) == (0, 1)


def _set(name, field, value):
    def mutate(fc):
        named(fc, name).params[field] = value

    return mutate


def _retarget(name, target):
    def mutate(fc):
        named(fc, name).next = index(fc, target)

    return mutate


def _entry_main(entry, target):
    def mutate(fc):
        fc.entry_point(entry).main_event = index(fc, target)

    return mutate


def _register_send_off_call(fc):
    fc.entry_point("DoorOfTime_SendOff").sub_flow_events.append(index(fc, "Event111"))


def _no_counter(fc):
    fc.entry_points = [entry for entry in fc.entry_points if entry.name != COUNT]


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


_REFUSALS = [
    (DOOR, _set("Event7", "StepName", "Step03"), "DoorOfTime/Event7", "step"),
    (DOOR, _set("Event12", "ChallengeName", "Get_StoneOfFire"), "DoorOfTime/Event12", "quest"),
    (SARIA, _set("Event172", "IsIgnoreChallengeProgressUI", False), "Event172", "quiet-write"),
    (DOOR, _set("Event93", "StepName", "Step06"), "DoorOfTime/Event93", "complete"),
    (DOOR, _retarget("Event14", "Event146"), "Event14.*next 'Event146'", "tail"),
    (DOOR, _retarget("Event7", "Event38"), "Event7.*next 'Event38'", "send-off-tail"),
    (ZELDA, _retarget("Event42", "Event43"), "Event42.*next 'Event43'", "end-tail"),
    (DOOR, _notice_action, "DoorOfTime/Event57", "action"),
    (DOOR, _rename, r"\['Event148'\]", "missing"),
    (DOOR, _unknown_writer, r"\['Event300'\]", "unknown-writer"),
    (SARIA, _no_game_data_actor, "GameDataActor", "no-game-data-actor"),
    (ZELDA, _bound_game_data_actor, "GameDataActor", "bound-game-data-actor"),
    (SARIA, _second_game_data_actor, "GameDataActor", "two-game-data-actors"),
    (DOOR, _second_game_data_actor, "GameDataActor", "two-door-game-data-actors"),
    (DOOR, _set("Event77", "Value", False), "DoorOfTime/Event77", "bridge-value"),
    (DOOR, _bridge_end, "Event77.*next None", "bridge-tail"),
    (DOOR, _entry_main(COUNT, "Event39"), "counter/send-off", "counter-entry"),
    (DOOR, _entry_main("DoorOfTime_SendOff", "Event7"), "counter/send-off", "send-off-entry"),
    (DOOR, _register_send_off_call, "counter/send-off", "send-off-registration"),
    (DOOR, _no_counter, COUNT, "no-counter"),
]
REFUSALS = [
    pytest.param(path, mutate, match, early, id=f"{name}-{'early' if early else 'every-mode'}")
    for path, mutate, match, name in _REFUSALS
    for early in (True, False)
    if early or path == DOOR
]


@pytest.mark.parametrize("path,mutate,match,early", REFUSALS)
def test_changed_native_events_are_refused_with_their_values(path, mutate, match, early):
    document = FLOWS[path]()
    mutate(document.flowchart)
    with pytest.raises(PatchError, match=match):
        door_story.changes(early=early)[path](evfl.write(document))


def test_another_flowchart_and_a_second_application_are_refused():
    for early in (True, False):
        changes = door_story.changes(early=early)
        with pytest.raises(PatchError, match="DoorOfTime"):
            changes[DOOR](evfl.write(castle_flow()))
        for path, transform in changes.items():
            once = transform(evfl.write(FLOWS[path]()))
            with pytest.raises(PatchError, match="ClawshotDoor"):
                transform(once)
    shared = door_story.changes(early=False)[DOOR](evfl.write(door_flow()))
    with pytest.raises(PatchError, match="ClawshotDoor"):  # the early story never doubles the shared repair
        door_story.changes()[DOOR](shared)


@pytest.mark.parametrize("early", (True, False))
def test_darunia_fire_guard_composes_in_either_order(early):
    fire = darunia.changes()[darunia.DOOR_FLOW]
    alone, after, before = assert_composes(evfl.write(door_flow()), DOOR, [fire], early)
    check_composed(DOOR, alone, (after, before), ORDERS, early)
    natural = {**START, "Step_DoorOfTime": "Step01"}
    for flow in (after, before):
        effects, final = outcome(flow, "DoorOfTime_SendOff", natural)
        assert (final["Step_DoorOfTime"], final["Step_Get_StoneOfFire"]) == ("Step02", "KakarikoVillageNpc")
        assert [effect[2]["StepName"] for effect in effects if effect[1] == STEP] == ["Step02", "KakarikoVillageNpc"]
        assert RECOUNT in effects


@pytest.fixture(scope="module")
def native(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    flows = {path: dictionaries.decompress(path, (romfs / path).read_bytes()) for path in PATHS}
    data = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))["Data"]
    enums = {int(row["Hash"]): row for row in data["Enum"]}
    quests = ("DoorOfTime", "Get_StoneOfFire", "Get_StoneOfWater")
    orders = {quest: tuple(enums[key(f"Step_{quest}")]["RawValues"]) for quest in quests}
    return flows, data, {**ORDERS, **orders}


@pytest.fixture(scope="module")
def patched(native):
    flows, _, _ = native
    edits = [*((path, True) for path in STORY), (DOOR, False)]
    return {(path, early): door_story.changes(early=early)[path](flows[path]) for path, early in edits}


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
def test_dump_every_native_door_writer_is_guarded_or_kept_native(romfs):
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
    expected = [(path, writer, step) for path, writer, step, _ in GUARDS] + list(NATIVE)
    assert sorted(found) == sorted(expected)


@pytest.mark.dump
@pytest.mark.parametrize("path,early", CHANGES)
def test_dump_only_the_contracted_events_change(native, patched, path, early):
    flows, _, _ = native
    out = patched[path, early]
    assert evfl.write(evfl.read(out)) == out
    assert evfl.read(out).flowchart == expected_story(evfl.read(flows[path]).flowchart, path, early)


@pytest.mark.dump
@pytest.mark.parametrize("path,writer,step,tail", GUARDS)
@pytest.mark.parametrize("boundary", BOUNDARIES)
def test_dump_writers_skip_only_their_own_write(native, patched, path, writer, step, tail, boundary):
    flows, _, orders = native
    old, new = evfl.read(flows[path]).flowchart, evfl.read(patched[path, True]).flowchart
    check_boundary(old, new, writer, step, tail, boundary, orders)


@pytest.mark.dump
@pytest.mark.parametrize("mode", MODES)
def test_dump_the_courtyard_stays_native_and_returns_the_quest_to_step01(native, mode):
    flows, _, orders = native
    check_courtyard(*flows_for(flows, mode), orders)


@pytest.mark.dump
@pytest.mark.parametrize("mode", MODES)
def test_dump_the_stone_count_waits_for_the_send_off_and_ends_with_the_escape(native, mode):
    flows, _, orders = native
    check_count_gate(*flows_for(flows, mode), mode, orders)


@pytest.mark.dump
@pytest.mark.parametrize("mode", MODES)
def test_dump_the_send_off_counts_the_stones_won_before_it(native, mode):
    flows, _, orders = native
    check_send_off(*flows_for(flows, mode), mode, orders)


@pytest.mark.dump
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("history", HISTORIES)
def test_dump_any_stone_order_reaches_impa_the_send_off_and_the_escape(native, mode, history):
    """The real flows; Saria's song starts at its talk before the Water gate, where her native story check
    routes with Fire complete, Water incomplete and the quest not past Step2_2."""
    flows, _, orders = native
    play_in_order(*flows_for(flows, mode), HISTORIES[history], mode, orders)


@pytest.mark.dump
@pytest.mark.parametrize("mode,before", AROUND_THE_ESCAPE)
def test_dump_the_bridge_rises_for_the_escape_and_never_after_it(native, mode, before):
    flows, _, orders = native
    check_bridge_around_the_escape(*flows_for(flows, mode), before, orders)


@pytest.mark.dump
@pytest.mark.parametrize("early", (True, False))
def test_dump_darunia_fire_guard_composes_in_either_order(native, early):
    flows, _, orders = native
    alone, after, before = assert_composes(flows[DOOR], DOOR, [darunia.changes()[darunia.DOOR_FLOW]], early)
    check_composed(DOOR, alone, (after, before), orders, early)


@pytest.mark.dump
def test_dump_composes_with_a_gift_seed_transforms_in_either_order(romfs, native):
    """Every transform a gift-shuffle seed ships for these flows but the door story's own (Darunia's guards today)."""
    flows, _, orders = native
    settings = Settings(shuffle=("Chest", "Shop", gifts.SHUFFLE, "Scrub", "BossHeart"), songs="song")
    spec, settings, gift_step = gifts.seed_setup(romfs, load_spec(), settings)
    output = make_seed(romfs, 11, settings, spec, extra_steps=[gift_step])
    for path, early in [*((path, True) for path in STORY), (DOOR, False)]:
        others = [
            changes[path]
            for changes in output.extra_changes
            if path in changes and getattr(changes[path], "__module__", None) != door_story.__name__
        ]
        alone, after, before = assert_composes(flows[path], path, others, early)
        check_composed(path, alone, (after, before), orders, early)


@pytest.mark.dump
def test_dump_composes_with_song_opening_in_either_order(native):
    flows, _, orders = native
    alone, after, before = assert_composes(flows[DOOR], DOOR, [door.song_flow])
    check_composed(DOOR, alone, (after, before), orders)
