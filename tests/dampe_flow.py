"""Replay Dampé's local control flow, not engine timing or external scenes."""

from clawshot.formats import evfl
from clawshot.patch.dampe_first_race import CHEST_OPEN, SPAWNED

COUNT = "MiniGame_DampeRace_ClearCount"
HEART = "UnderTheGrave_DampeRace_HeartGeted"
TREASURE = "Minigame_DampeRace_TreasureBoxState"
FOREST = "SageOfForest"
STEPS = (
    "NotReady",
    "Ready",
    "Step01",
    "Step02",
    "Step03",
    "Step04",
    "Step05",
    "Step06",
    "Step06_1_0",
    "Step06_1_1",
    "Step06_1_2",
    "Step06_2",
    "Step07",
    "Step08",
    "Step09",
    "Complete",
)


def play(fc, entry, state, owned):
    """Known native query ABI: Bool/pouch true=0, Int less/equal/greater=0/1/2.

    Dialogue picks Yes, NPC talk history picks a repeat talk, camera queries choose
    their close/unobstructed arm. Unknown queries fail rather than invent a route.
    External subflows/transitions are recorded, not interpreted as game proof.
    """
    effects = []
    budget = 2000

    def query(event):
        actor = fc.actors[event.actor]
        name = actor.queries[event.query]
        p = event.params or {}
        if name == "EventQueryIsExistInPouch":
            return 0 if p["Actor"] in owned else 1
        if name == "EventQueryCheckIsGet":
            return 0 if p["ActorName"] in owned else 1
        if name == "EventQueryIsGameDataBool":
            return 0 if state.get(p["GameDataName"], False) else 1
        if name == "EventQueryIsGameDataEnum":
            return 0 if state.get(p["GameDataName"]) == p["Value"] else 1
        if name == "EventQueryIsGameDataBoolExp":
            flag = p["GameDataName"]
            if flag.startswith("SageOfForest_IsAfter_"):
                step = flag.removeprefix("SageOfForest_IsAfter_").removesuffix("_Exp")
                return 0 if STEPS.index(state[FOREST]) > STEPS.index(step) else 1
            assert flag == "MiniGame_DampeRace_IsClearLeastOnce", event
            return 0 if state[COUNT] >= 1 else 1
        if name == "EventQueryGameDataIntBranch":
            return state.get(p["GameDataName"], 0)
        if name == "EventQueryIsGameDataInt":
            a, b = state.get(p["GameDataName"], 0), p["Value"]
            return 0 if a < b else 1 if a == b else 2
        if name == "EventQueryCompareGameDataInt":
            a, b = state.get(p["GameDataA"], 0), state.get(p["GameDataB"], 0)
            assert p["Operator"] in (0, 4), event
            yes = a == b if p["Operator"] == 0 else a < b
            return 0 if yes else 1
        if name == "EventQueryHaveTalked":
            return 0 if state.get("Npc_HaveTalked", True) else 1
        if name in (
            "EventQueryTalkChoice2",
            "EventQueryTalkChoice3",
            "EventQueryIsOnRecentTalkFlag",
            "EventQueryAvoidDuplicationRandomChoice2",
            "EventQueryIsDistanceBetweenActorsClose",
            "EventQueryCameraCheckRayCastForMoveToTarget",
        ):
            return 0
        assert name == "EventQueryMiniGameTimerIsCounting", (event, name)
        return 1

    def walk(index, stop=evfl.NONE):
        nonlocal budget
        while index != evfl.NONE and index != stop:
            budget -= 1
            assert budget > 0, effects
            event = fc.events[index]
            p = getattr(event, "params", None) or {}
            effects.append(event.name)
            if isinstance(event, evfl.SwitchEvent):
                index = dict(event.cases).get(query(event), evfl.NONE)
            elif isinstance(event, evfl.SubFlowSwitchEvent):
                assert (event.flowchart, event.entry_point) == ("NpcCommon", "CheckAlreadyMaskTalked"), event
                index = event.cases[0][1]
            elif isinstance(event, evfl.SubFlowEvent):
                if event.flowchart in ("", fc.name):
                    walk(fc.entry_point(event.entry_point).main_event)
                index = event.next
            elif isinstance(event, evfl.ForkEvent):
                for branch in event.forks:
                    walk(branch, event.join)
                index = event.join
            elif isinstance(event, evfl.JoinEvent):
                index = event.next
            else:
                assert isinstance(event, evfl.ActionEvent), event
                action = fc.actors[event.actor].actions[event.action]
                if action in (
                    "EventTriggerSetGameDataBool",
                    "EventTriggerSetGameDataEnum",
                    "EventTriggerSetGameDataInt",
                ):
                    state[p["GameDataName"]] = p["Value"]
                elif action == "EventTriggerAddOrSubGameDataInt":
                    state[p["GameDataName"]] = state.get(p["GameDataName"], 0) + p["Value"]
                elif action == "EventTriggerCopyGameDataInt":
                    state[p["DstGameDataName"]] = state.get(p["SrcGameDataName"], 0)
                elif action in ("EventExecuteProgressChallengeStep", "EventExecuteRollbackChallengeStep"):
                    state[p["ChallengeName"]] = p.get("StepName", p.get("ChallengeStep"))
                index = event.next

    walk(fc.entry_point(entry).main_event)
    return effects


def assert_first_race_cycle(fc):
    """Each production recipe must recover both tier holders, even after prior races.

    A slow first finish still gets its chest; spawning/leaving is not collection.
    The runtime's ordinary chest-open flag is supplied only after the open entry.
    Then the native second-race path and count resume. No save/game is modified.
    """
    for owned in ({"Item_Hookshot"}, {"Item_Longshot"}, {"Item_Hookshot", "Item_Longshot"}):
        for count, heart, spawned in ((0, False, False), (2, True, False), (2, False, True)):
            state = {
                CHEST_OPEN: False,
                SPAWNED: spawned,
                COUNT: count,
                HEART: heart,
                TREASURE: "None",
                FOREST: "Step06",
                "UnderTheGrave_DampeRace_SecondRace_More": True,
                "MiniGame_TimerMinute": 2,
                "MiniGame_TimerSecond": 10,
                "MiniGame_TimerMilliSecond": 0,
            }
            trace = play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, owned)
            assert "Event131" not in trace, (owned, count, trace)
            assert state["MiniGame_DampeRace"] == "Playing", (owned, count, trace, state)
            assert state[FOREST] == "Step06", (owned, state)
            assert not state["UnderTheGrave_DampeRace_SecondRace_More"], state
            play(fc, "Finish_Npc_Hylia_Dampe_002_StepStart", state, owned)
            assert state[COUNT] == count, (owned, count, state)
            play(fc, "Result", state, owned)
            assert state[TREASURE] == "AppearHookShot", (owned, count, state)
            assert not state[CHEST_OPEN]
            # A second attempt with the spawn history set still offers/spawns the first chest.
            play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, owned)
            assert state["MiniGame_DampeRace"] == "Playing", state
            play(fc, "Finish_Npc_Hylia_Dampe_002_StepStart", state, owned)
            play(fc, "Result", state, owned)
            assert state[TREASURE] == "AppearHookShot", state
            play(fc, "MiniGame_DampeRace_OpenGoalTBox", state, owned)
            assert state[TREASURE] == "OpenedHookShot", state
            state[CHEST_OPEN] = True  # ordinary chest contract, not the transient spawn Bool
            play(fc, "Ready_Npc_Hylia_Dampe_002_Talk", state, owned)
            assert state["MiniGame_DampeRace"] == "PlayingSecond", (owned, count, state)
            assert state[FOREST] == "Step06", state
            state["MiniGame_TimerMinute"], state["MiniGame_TimerSecond"] = 0, 55
            play(fc, "Finish_Npc_Hylia_Dampe_002_StepStart", state, owned)
            assert state[COUNT] == count + 1, (owned, count, state)
            play(fc, "Result", state, owned)
            # This fixture's zero best-time defaults make 0:55 a non-record repeat.
            assert state[TREASURE] == ("AppearRupeeLow" if heart else "AppearHeartPiece"), (owned, count, state)
            assert state[HEART] == heart, state
