"""Clock transitions: Impa's real send-off restores a missing Field arrival, and a real return to child ends a
pending first-adult hold.

The native clock runs ordinarily only with the Field owl arrival (``HyruleField_ArriveEntrance``), the send-off
history and no first-adult hold (``HrlField_HasEnteredFirstTime_Adult``). Routes that reach the courtyard without
the owl lack the arrival; the hold, set by the first adult arrival, is natively cleared only by walking from the
adult Market into the Field. Synthetic flows are invented on the native contracts of the round 16 clock audit, never
cut from the game; dump-marked tests read the real flows. Engine timing and the clock itself still need play.
"""

from copy import deepcopy
from itertools import product

import pytest
from test_door_story import (
    ARRIVE,
    ARRIVED,
    DOOR,
    EARLY,
    ESCAPED,
    MODES,
    ORDERS,
    READ_BOOL,
    RECOUNT,
    SENDOFF,
    SENDOFF_SCENE,
    SET_BOOL,
    START,
    STEP,
    STEPS,
    STONES,
    TRANSITION,
    chart,
    data,
    door_flow,
    door_opens,
    flows_for,
    index,
    named,
    outcome,
    reference,
    scene,
    synthetic,
)

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import door, door_story
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.plan import PatchError
from clawshot.save import key

ERA = "Event/EventFlow/Market_Adult_Field_AdultToChild.bfevfl.zs"
ERA_ENTRY = "Market_Adult_Field_AdultToChild"
FIRST_ADULT = "HrlField_HasEnteredFirstTime_Adult"
CHILDHOOD = "Sequence_IsChildhood"
FIRST_RETURN = "Market_Adult_Firsttime_GobacktoChild"  # the travel's own once flag
TIMER = "EventQueryMiniGameTimerIsCounting"
TRAVEL = "EventReserveBancChange"
PRELOAD = "EventTriggerBancRequestBeforehandLoad"
LOOK = "EventTriggerPlayerRequestLookAtTheFrontLock"
SWAP = "ReplaceEquipmentForEraChange"
TO_CHILD = {"IsWaitEnd": True, "NextBanc": "Market_Child", "BootEventName": "Dm_TimeTemple_0075", "FadePattern": 2}
CLEAR = ("GameDataActor", SET_BOOL, {"GameDataName": FIRST_ADULT, "Index": -1, "Value": False})
AGE = ("GameDataActor", SET_BOOL, {"GameDataName": CHILDHOOD, "Index": -1, "Value": True})
ARRIVAL = ("GameDataActor", SET_BOOL, ARRIVE)
CLOCK_NAMES = ("ClawshotClockChildReturn", "ClawshotClockReturnedChild")


def clock_runs(state):
    """The native ordinary clock, without its live Deku override: arrival, send-off, no first-adult hold."""
    return state[ARRIVED] and state[SENDOFF] and not state[FIRST_ADULT]


def era_flow():
    """The Temple's adult-to-child travel: preload, timer check (a running mini-game timer ends it), the scene, the
    registered equipment swap, the childhood write, the reserved travel to the child Market, then its once flag."""
    return chart(
        "Market_Adult_Field_AdultToChild",
        [
            ("GameSystemActor", [TRAVEL, PRELOAD], []),
            ("GameDataActor", [SET_BOOL], [READ_BOOL]),
            ("EventSystemActor", [TRANSITION], []),
            ("ChallengeSystemActor", [], [TIMER]),
            ("Player_Event", [LOOK], []),
        ],
        [
            ("Event0", "act", "GameSystemActor", TRAVEL, dict(TO_CHILD), "Event12"),
            data("Event1", SET_BOOL, CHILDHOOD, True, "Event0"),
            scene("Event2", "Dm_TimeTemple_0070", "Event7"),
            ("Event7", "call", SWAP, SWAP, None, "Event1"),
            ("Event8", "act", "Player_Event", LOOK, {"IsImmediate": False}, "Event2"),
            ("Event3", "ask", "GameDataActor", READ_BOOL, {"GameDataName": FIRST_RETURN, "Index": -1}, {1: "Event9"}),
            data("Event9", SET_BOOL, FIRST_RETURN, True, None),
            ("Event10", "ask", "ChallengeSystemActor", TIMER, None, {1: "Event8"}),
            scene("Event11", "SubEvent_TimerCheck_ToChild", "Event10"),
            ("Event6", "act", "GameSystemActor", PRELOAD, {"BancPath": "Work/Test/Market_Child.json"}, "Event11"),
            ("Event12", "act", "Player_Event", LOOK, {"IsImmediate": True}, "Event3"),
        ],
        [(ERA_ENTRY, "Event6", ["Event7"])],
    )


def ship_era(document, mode):
    return evfl.read(door.changes({}, mode=mode)[ERA](evfl.write(document))).flowchart


def travel(fc, state, *, timer=False):
    """Follow the era entry from its start; its effects and the state after. Case 0 is a true query; ``timer`` is a
    running mini-game timer. Only registered sub flow calls are allowed."""
    state, effects = dict(state), []
    entry = fc.entry_point(ERA_ENTRY)
    at = entry.main_event
    for _ in range(100):
        if at == evfl.NONE:
            return effects, state
        event = fc.events[at]
        params = getattr(event, "params", None) or {}
        if isinstance(event, evfl.SwitchEvent):
            actor = fc.actors[event.actor]
            query = actor.queries[event.query]
            if query == TIMER:
                true = timer
            else:
                assert (actor.name, query, params["Index"]) == ("GameDataActor", READ_BOOL, -1), event
                true = state[params["GameDataName"]]
            at = dict(event.cases).get(0 if true else 1, evfl.NONE)
        elif isinstance(event, evfl.SubFlowEvent):
            assert at in entry.sub_flow_events, f"{event.name} is not registered"
            effects.append(("call", event.flowchart, event.entry_point))
            at = event.next
        else:
            assert isinstance(event, evfl.ActionEvent), event
            actor = fc.actors[event.actor]
            action = actor.actions[event.action]
            if action == SET_BOOL:
                state[params["GameDataName"]] = params["Value"]
            effects.append((actor.name, action, params))
            at = event.next
    raise AssertionError(effects)


def unclock_era(fc):
    """The exact inverse of the child-return splice: the age write continues to its target again."""
    fc = deepcopy(fc)
    first = index(fc, CLOCK_NAMES[0])
    assert [event.name for event in fc.events[first:]] == list(CLOCK_NAMES)
    assert named(fc, "Event1").next == first
    named(fc, "Event1").next = dict(fc.events[first].cases)[1]
    del fc.events[first:]
    return fc


ADULT = {CHILDHOOD: False, FIRST_RETURN: False, FIRST_ADULT: False, ARRIVED: True, SENDOFF: True}


def check_child_return(native, shipped):
    """A real return clears only a set hold, right after the native age write; every other effect stays native."""
    for hold, once, timer in product((False, True), repeat=3):
        state = {**ADULT, FIRST_ADULT: hold, FIRST_RETURN: once}
        before, plain = travel(native, state, timer=timer)
        effects, final = travel(shipped, state, timer=timer)
        if timer:  # the running timer ends the travel before any age change: nothing is cleared
            assert (effects, final) == (before, plain) and final[CHILDHOOD] is False
            continue
        assert final == {**plain, FIRST_ADULT: False} and final[CHILDHOOD] is True
        at = before.index(AGE) + 1
        assert effects == (before[:at] + [CLEAR] + before[at:] if hold else before)
        assert clock_runs(final)
        assert clock_runs(plain) is not hold  # the native travel keeps a set hold on the child
        later = {**final, CHILDHOOD: False}  # back to adult without a new first arrival, then a later return
        assert travel(shipped, later) == travel(native, later)


@pytest.mark.parametrize("mode", MODES)
def test_a_real_return_to_child_clears_only_a_pending_first_adult_hold(mode):
    check_child_return(era_flow().flowchart, ship_era(era_flow(), mode))


def test_the_child_return_splice_is_exactly_invertible():
    native = evfl.write(era_flow())
    shipped = door_story.changes()[ERA](native)
    assert evfl.write(evfl.read(shipped)) == shipped
    document = evfl.read(shipped)
    document.flowchart = unclock_era(document.flowchart)
    assert evfl.write(document) == native


def check_send_off(flows, base, mode, orders=ORDERS):
    """Impa's real send-off sets a missing Field arrival once: after its scene and Step02, before its own stone
    count and Fire's continuation. Every other effect, the count and the steps are those of an owl-met send-off."""
    for arrived, current, (fire, water) in product((False, True), ("Step01", "Complete"), STONES):
        stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
        state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: False, ARRIVED: arrived, FIRST_ADULT: False}
        effects, final = outcome(flows[DOOR], "DoorOfTime_SendOff", state, orders=orders, scenes=True)
        promised = outcome(base[DOOR], "DoorOfTime_SendOff", state, orders=orders, scenes=True, **reference(mode))
        assert (effects, final) == promised, state
        owl, met = outcome(flows[DOOR], "DoorOfTime_SendOff", {**state, ARRIVED: True}, orders=orders, scenes=True)
        assert ([effect for effect in effects if effect != ARRIVAL], final) == (owl, met)
        assert effects.count(ARRIVAL) == (not arrived) and effects.count(RECOUNT) == 1
        if not arrived:
            write = effects.index(ARRIVAL)
            scenes = [i for i, e in enumerate(effects) if e[1] == TRANSITION and e[2]["EventName"] == SENDOFF_SCENE]
            step02 = [i for i, e in enumerate(effects) if e[1] == STEP and e[2]["StepName"] == "Step02"]
            assert scenes[0] < write < effects.index(RECOUNT)
            assert all(i < write for i in step02)  # the send-off's own Step02, unless already past it
        assert clock_runs(final)
        if current == "Step01":
            assert door_opens(flows, final, mode, orders) is (mode in EARLY)
        again, repeated = outcome(flows[DOOR], "DoorOfTime_SendOff", final, orders=orders, scenes=True)
        assert ARRIVAL not in again and repeated[ARRIVED] is True


@pytest.mark.parametrize("mode", MODES)
def test_the_real_send_off_restores_a_missing_field_arrival(mode):
    check_send_off(*synthetic(mode), mode)


def check_other_entries(flows, base, mode, orders=ORDERS):
    """Without the owl, every door entry plays as promised, and only the real send-off writes the arrival."""
    for entry, current, (fire, water), (sendoff, escaped) in product(
        base[DOOR].entry_points, STEPS, STONES, product((False, True), repeat=2)
    ):
        stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
        state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped, ARRIVED: False}
        effects, final = outcome(flows[DOOR], entry.name, state, orders=orders)
        expected = outcome(base[DOOR], entry.name, state, orders=orders, **reference(mode))
        assert (effects, final) == expected, (entry.name, state)
        assert final[ARRIVED] is (entry.name == "DoorOfTime_SendOff")


def clock_entries(fc):
    """The entries that can run a clock event, through their branches and calls of this flowchart's entries."""
    clock = {i for i, event in enumerate(fc.events) if event.name.startswith("ClawshotClock")}

    def reaches(start):
        seen, todo = set(), [start]
        while todo:
            at = todo.pop()
            if at == evfl.NONE or at in seen:
                continue
            seen.add(at)
            event = fc.events[at]
            if isinstance(event, evfl.SwitchEvent | evfl.SubFlowSwitchEvent):
                todo += [target for _, target in event.cases]
            elif isinstance(event, evfl.ForkEvent):
                todo += [*event.forks, event.join]
            elif not isinstance(event, evfl.ReturnEvent):
                todo.append(event.next)
            if isinstance(event, evfl.SubFlowEvent | evfl.SubFlowSwitchEvent) and event.flowchart in ("", fc.name):
                todo.append(fc.entry_point(event.entry_point).main_event)
        return bool(seen & clock)

    return [entry.name for entry in fc.entry_points if reaches(entry.main_event)]


@pytest.mark.parametrize("mode", MODES)
def test_no_other_door_entry_writes_the_arrival(mode):
    flows, base = synthetic(mode)
    assert clock_entries(flows[DOOR]) == ["DoorOfTime_SendOff"]
    check_other_entries(flows, base, mode)


def _send_off_scene(fc):
    named(fc, "Event65").params["EventName"] = "Dm_HrlField_Test"


def _send_off_skips_step02(fc):
    named(fc, "Event65").next = index(fc, "Event62")


@pytest.mark.parametrize("mutate", (_send_off_scene, _send_off_skips_step02))
@pytest.mark.parametrize("early", (True, False))
def test_a_send_off_that_no_longer_plays_its_scene_into_step02_is_refused(mutate, early):
    document = door_flow()
    mutate(document.flowchart)
    with pytest.raises(PatchError, match="send-off no longer plays Dm_HrlField_0020"):
        door_story.changes(early=early)[DOOR](evfl.write(document))


def _era_set(name, field, value):
    def mutate(fc):
        named(fc, name).params[field] = value

    return mutate


def _era_next(name, target):
    def mutate(fc):
        named(fc, name).next = index(fc, target)

    return mutate


def _era_entry(fc):
    fc.entry_points[0].main_event = index(fc, "Event11")


def _era_unregistered(fc):
    fc.entry_points[0].sub_flow_events = []


def _era_rename(fc):
    named(fc, "Event0").name = "Event0Moved"


def _era_second_actor(fc):
    fc.actors.append(evfl.Actor("GameDataActor"))


ERA_REFUSALS = [
    pytest.param(_era_set("Event1", "Value", False), "age change", id="age-value"),
    pytest.param(_era_set("Event1", "GameDataName", "Sequence_IsTest"), "age change", id="age-name"),
    pytest.param(_era_next("Event1", "Event12"), "age change", id="age-next"),
    pytest.param(_era_next("Event7", "Event0"), "age change", id="swap-next"),
    pytest.param(_era_set("Event0", "NextBanc", "Market_Adult"), "age change", id="travel-place"),
    pytest.param(_era_set("Event0", "BootEventName", "Dm_Test"), "age change", id="travel-scene"),
    pytest.param(_era_rename, r"\['Event0'\]", id="missing"),
    pytest.param(_era_entry, "entries", id="entry"),
    pytest.param(_era_unregistered, "entries", id="registration"),
    pytest.param(_era_second_actor, "GameDataActor", id="two-game-data-actors"),
]


@pytest.mark.parametrize("mutate,match", ERA_REFUSALS)
def test_a_changed_native_child_return_is_refused(mutate, match):
    document = era_flow()
    mutate(document.flowchart)
    with pytest.raises(PatchError, match=match):
        door_story.changes()[ERA](evfl.write(document))


def test_another_flowchart_and_a_second_child_return_are_refused():
    transform = door_story.changes()[ERA]
    with pytest.raises(PatchError, match="holds no Market_Adult_Field_AdultToChild"):
        transform(evfl.write(door_flow()))
    with pytest.raises(PatchError, match="ClawshotClockChildReturn"):
        transform(transform(evfl.write(era_flow())))


# Real data.


@pytest.fixture(scope="module")
def native(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    flows = {path: dictionaries.decompress(path, (romfs / path).read_bytes()) for path in (DOOR, ERA)}
    game_data = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))["Data"]
    enums = {int(row["Hash"]): row for row in game_data["Enum"]}
    quests = ("DoorOfTime", "Get_StoneOfFire", "Get_StoneOfWater")
    orders = {quest: tuple(enums[key(f"Step_{quest}")]["RawValues"]) for quest in quests}
    return dictionaries, flows, {**ORDERS, **orders}, game_data


@pytest.mark.dump
def test_dump_a_real_return_to_child_clears_only_a_pending_hold(native):
    _, flows, _, _ = native
    shipped = door_story.changes()[ERA](flows[ERA])
    assert evfl.write(evfl.read(shipped)) == shipped
    document = evfl.read(shipped)
    document.flowchart = unclock_era(document.flowchart)
    assert evfl.write(document) == flows[ERA]  # every unrelated byte and path is native
    check_child_return(evfl.read(flows[ERA]).flowchart, evfl.read(shipped).flowchart)


@pytest.mark.dump
@pytest.mark.parametrize("mode", MODES)
def test_dump_the_real_send_off_restores_a_missing_field_arrival(native, mode):
    """Every other real door entry is checked by reach: the reference engine models only the story's events."""
    _, flows, orders, _ = native
    shipped, base = flows_for({DOOR: flows[DOOR]}, mode)
    check_send_off(shipped, base, mode, orders)
    assert clock_entries(shipped[DOOR]) == ["DoorOfTime_SendOff"]


def _bool_writers(path, data):
    """(flow, event, saved name, value) for every arrival or first-adult write in ``data``."""
    fc = evfl.read(data).flowchart
    rows = []
    for event in fc.events if fc is not None else ():
        params = getattr(event, "params", None) or {}
        if (
            isinstance(event, evfl.ActionEvent)
            and fc.actors[event.actor].actions[event.action] == SET_BOOL
            and params.get("GameDataName") in (ARRIVED, FIRST_ADULT)
        ):
            rows.append((path, event.name, params["GameDataName"], params["Value"]))
    return rows


@pytest.mark.dump
def test_dump_only_the_send_off_and_the_child_return_add_clock_writes(romfs, native):
    """The external audit's full-resource scan found no other writer in packs, AINB or GameData expressions."""
    dictionaries, _, _, game_data = native
    rows = {int(row["Hash"]): row for row in game_data["Bool"]}
    for name in (ARRIVED, FIRST_ADULT):  # saved and unset on a new game: the fallback writes only what is missing
        row = rows[key(name)]
        assert row["DefaultValue"] is False and int(row["SaveFileIndex"]) >= 0, row
    flows = {}
    for file in sorted((romfs / "Event/EventFlow").glob("*.bfevfl.zs")):
        path = file.relative_to(romfs).as_posix()
        data = dictionaries.decompress(path, file.read_bytes())
        if path in (DOOR, ERA) or ARRIVED.encode() in data or FIRST_ADULT.encode() in data:
            flows[path] = data
    native_writers = sorted(row for path, data in flows.items() for row in _bool_writers(path, data))
    assert native_writers == [
        ("Event/EventFlow/Dm_SY_BancChangeArrive.bfevfl.zs", "Event434", FIRST_ADULT, False),
        ("Event/EventFlow/Dm_TimeTemple_0055.bfevfl.zs", "Event252", FIRST_ADULT, True),
        ("Event/EventFlow/Goto_HyruleCastle.bfevfl.zs", "Event153", ARRIVED, True),
    ]
    added = [
        (DOOR, "ClawshotClockArrived", ARRIVED, True),
        (ERA, "ClawshotClockReturnedChild", FIRST_ADULT, False),
    ]
    for mode in MODES:
        changes = door.changes({}, mode=mode)
        assert not {path for path, *_ in native_writers} & changes.keys()  # the native writers ship unchanged
        shipped = {path: changes[path](data) if path in changes else data for path, data in flows.items()}
        writers = sorted(row for path, data in shipped.items() for row in _bool_writers(path, data))
        assert writers == sorted(native_writers + added), mode
