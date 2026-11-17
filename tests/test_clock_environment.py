"""Clock environment: the first-Field light never outlives Impa's real send-off, and a played owl panorama or
send-off keeps the Forest exit from setting it again.

The Forest exit (Goto_HyruleCastle ``KokiriForest_ArriveLostWood``) sets the saved first-Field light
(``HyruleField_ChangeENV``) on its way to the Field; only Kaepora's owl arrival clears it natively, after its
panorama, then waits a frame and rebuilds the conditional palette. A save whose owl arrival was skipped or missed can
keep the light set past the send-off, where the field lighting stays fixed; the Forest exit's requester reads only
Saria's farewell history, so a first bridge crossing can also come after the send-off, once the owl's area is gone.
Every door mode ships two repairs: the send-off returns a set light to the ordinary one in the owl's order, whatever
the arrival, and the Forest exit sets the light only while neither the panorama nor the send-off has played.
Synthetic flows are invented on the native contracts of the round 16 clock audit, never cut from the game;
dump-marked tests read the real flows. Engine timing and the light itself still need play.
"""

from copy import deepcopy
from dataclasses import replace
from itertools import product

import pytest
from test_door_story import (
    ARRIVE,
    ARRIVED,
    BANC_CHANGE,
    CASTLE,
    DOOR,
    ESCAPED,
    FIRST_FIELD,
    FOREST_EXIT,
    HAVE_PLAYED,
    LIT,
    MEET_ZELDA,
    MODES,
    ORDERS,
    OWL_ARRIVAL,
    PANORAMA,
    PANORAMA_SCENE,
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
    UNLIT,
    castle_flow,
    courtyard,
    door_flow,
    flows_for,
    index,
    named,
    outcome,
    reach,
    reference,
    synthetic,
)

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import door
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.plan import PatchError
from clawshot.save import key

CLEARED = UNLIT[0]
ARRIVAL = ("GameDataActor", SET_BOOL, ARRIVE)
# The send-off's light repair, after its arrival repair and before its recount: query, clear, wait, rebuild.
REPAIR = (
    "ClawshotClockEnvironment",
    "ClawshotClockClearedEnvironment",
    "ClawshotClockWaitEnvironment",
    "ClawshotClockRebuildEnvironment",
)
MOVED = "ClawshotClockFirstFieldENV"  # the castle guard's moved light write
SENT = "ClawshotClockFirstFieldSendoff"  # the castle guard's played send-off query, after the moved write
FAREWELL, LIGHT_WRITE, TRAVEL = "Event44", "Event218", "Event42"  # Saria's farewell scene, the light, the travel
OWL_FIRST, OWL_NEXT = "Event153", "Event12"  # the owl arrival's Field arrival write, its scene after the light
OWL_SCENE = "Dm_HrlField_0005"
FRESH = {PANORAMA: False, ARRIVED: False, FIRST_FIELD: False}  # a new save
SKIPPED = {PANORAMA: True, ARRIVED: True, FIRST_FIELD: False}  # the Kaepora skip's start history (fast-start data)
SEND_OFF = "DoorOfTime_SendOff"


def relit_at(effects):
    """Where ``effects`` return to the ordinary light in the owl's order."""
    return [i for i in range(len(effects)) if effects[i : i + len(UNLIT)] == UNLIT]


def owl_light(fc):
    """The owl arrival's actions from its Field arrival write to the scene after its light, as the runner records
    them; the real owl continues into forks the runner does not model."""
    effects, at = [], index(fc, OWL_FIRST)
    while fc.events[at].name != OWL_NEXT:
        event = fc.events[at]
        assert isinstance(event, evfl.ActionEvent), event
        actor = fc.actors[event.actor]
        effects.append((actor.name, actor.actions[event.action], event.params or {}))
        at = event.next
    return effects


def light_entries(fc):
    """The door entries that can run the send-off's light repair."""
    repair = {index(fc, name) for name in REPAIR}
    return [entry.name for entry in fc.entry_points if reach(fc, entry.main_event) & repair]


def test_the_send_off_clears_a_set_first_field_light_then_waits_and_rebuilds():
    """The arrival already set, so only the light is repaired: cleared, one frame, rebuilt, before the recount."""
    for mode in MODES:
        flows, _ = synthetic(mode)
        state = {**START, "Step_DoorOfTime": "Step01", SENDOFF: False, ARRIVED: True, FIRST_FIELD: True}
        effects, final = outcome(flows[DOOR], SEND_OFF, state, scenes=True)
        assert effects.count(CLEARED) == 1, (mode, effects)
        at = effects.index(CLEARED)
        assert effects[at : at + 3] == UNLIT, mode
        scene = next(i for i, e in enumerate(effects) if e[1] == TRANSITION and e[2]["EventName"] == SENDOFF_SCENE)
        step02 = next(i for i, e in enumerate(effects) if e[1] == STEP and e[2]["StepName"] == "Step02")
        assert scene < step02 < at < effects.index(RECOUNT), mode
        assert final[FIRST_FIELD] is False and final[ARRIVED] is True, mode


def test_a_played_owl_panorama_keeps_the_forest_exit_from_setting_the_first_field_light():
    """Everything else the Forest exit does, its travel last, stays native."""
    for mode in MODES:
        flows, base = synthetic(mode)
        state = {**START, PANORAMA: True, SENDOFF: False, FIRST_FIELD: False}
        effects, final = outcome(flows[CASTLE], FOREST_EXIT, state, scenes=True)
        native, _ = outcome(base[CASTLE], FOREST_EXIT, state, scenes=True)
        assert LIT in native
        assert effects == [effect for effect in native if effect != LIT], mode
        assert final[FIRST_FIELD] is False, mode


def test_a_first_forest_exit_after_the_send_off_keeps_the_ordinary_light():
    """The owl never met (Lost Woods shortcuts, then the courtyard and the send-off, whose fallback set the arrival):
    the first bridge crossing afterwards plays the Forest exit, whose requester reads only Saria's farewell history.
    Nothing would clear the light again, so it is never set; everything else, its travel last, stays native."""
    for mode in MODES:
        flows, base = synthetic(mode)
        state = {**START, PANORAMA: False, SENDOFF: True, ARRIVED: True, FIRST_FIELD: False}
        effects, final = outcome(flows[CASTLE], FOREST_EXIT, state, scenes=True)
        native, _ = outcome(base[CASTLE], FOREST_EXIT, state, scenes=True)
        assert LIT in native
        assert effects == [effect for effect in native if effect != LIT], mode
        assert final[FIRST_FIELD] is False, mode


def check_send_off(flows, base, mode, orders=ORDERS):
    """Impa's real send-off ends a set first-Field light once, whatever the arrival and the quest step: after its
    scene, its Step02 and a missing arrival's write, the light is cleared, a frame passes and the palette is rebuilt,
    before the recount. An unset light adds nothing; no other effect or history differs."""
    for arrived, lit, current, (fire, water) in product((False, True), (False, True), ("Step01", "Complete"), STONES):
        stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
        state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: False, ARRIVED: arrived, FIRST_FIELD: lit}
        effects, final = outcome(flows[DOOR], SEND_OFF, state, orders=orders, scenes=True)
        promised = outcome(base[DOOR], SEND_OFF, state, orders=orders, scenes=True, **reference(mode))
        assert (effects, final) == promised, state
        unlit, plain = outcome(flows[DOOR], SEND_OFF, {**state, FIRST_FIELD: False}, orders=orders, scenes=True)
        assert relit_at(effects) == ([effects.index(CLEARED)] if lit else []), state
        if lit:
            at = effects.index(CLEARED)
            assert (effects[:at] + effects[at + len(UNLIT) :], final) == (unlit, plain), state
            scene = next(i for i, e in enumerate(effects) if e[1] == TRANSITION and e[2]["EventName"] == SENDOFF_SCENE)
            step02 = [i for i, e in enumerate(effects) if e[1] == STEP and e[2]["StepName"] == "Step02"]
            assert scene < at < effects.index(RECOUNT) and all(i < at for i in step02), state
            assert arrived or effects.index(ARRIVAL) < at, state
        else:
            assert (effects, final) == (unlit, plain), state
        assert final[FIRST_FIELD] is False and final[ARRIVED] is True and final[SENDOFF] is True
        again, repeated = outcome(flows[DOOR], SEND_OFF, final, orders=orders, scenes=True)
        assert CLEARED not in again and ARRIVAL not in again and repeated[FIRST_FIELD] is False


@pytest.mark.parametrize("mode", MODES)
def test_the_send_off_ends_the_first_field_light_whatever_the_arrival_and_step(mode):
    check_send_off(*synthetic(mode), mode)


@pytest.mark.parametrize("mode", MODES)
def test_no_other_door_entry_touches_the_first_field_light(mode):
    flows, base = synthetic(mode)
    assert light_entries(flows[DOOR]) == [SEND_OFF]
    histories = product((False, True), repeat=3)  # send-off, escape, Field arrival
    for entry, current, (sendoff, escaped, arrived) in product(base[DOOR].entry_points, STEPS, histories):
        if entry.name == SEND_OFF:
            continue
        state = {**START, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped, ARRIVED: arrived}
        state[FIRST_FIELD] = True
        effects, final = outcome(flows[DOOR], entry.name, state)
        assert (effects, final) == outcome(base[DOOR], entry.name, state, **reference(mode)), (entry.name, state)
        assert final[FIRST_FIELD] is True and CLEARED not in effects, entry.name


def check_forest_exit(flows, base, orders=ORDERS):
    """From Saria's farewell or the light write itself, the Forest exit sets the first-Field light only while
    neither the owl panorama nor the send-off has played; either history keeps the save's light, whatever the
    arrival. Its other effects, the Field travel last, are native, and replaying it changes nothing more."""
    new, old = flows[CASTLE], base[CASTLE]
    for start, played, sent, lit in product((FAREWELL, LIGHT_WRITE), (False, True), (False, True), (False, True)):
        plays = set()
        for arrived in (False, True):
            state = {**START, PANORAMA: played, SENDOFF: sent, FIRST_FIELD: lit, ARRIVED: arrived}
            effects, final = outcome(new, index(new, start), state, orders=orders, scenes=True)
            native, plain = outcome(old, index(old, start), state, orders=orders, scenes=True)
            assert (effects, final) == outcome(old, index(old, start), state, orders=orders, scenes=True, light=True)
            assert LIT in native
            if played or sent:
                assert (effects, final) == ([e for e in native if e != LIT], {**plain, FIRST_FIELD: lit}), state
            else:  # the native first Forest exit
                assert (effects, final) == (native, plain), state
            assert final[FIRST_FIELD] is (lit or not (played or sent))
            assert effects[-1] == native[-1] and effects[-1][1] == BANC_CHANGE  # the native Field travel, last
            assert outcome(new, index(new, start), final, orders=orders, scenes=True) == (effects, final)
            plays.add(repr(effects))
        assert len(plays) == 1  # the arrival changes nothing


def check_owl_arrival(flows, base):
    """The owl arrival keeps its native return to the ordinary light: its Field arrival, the panorama and the owl's
    scene, then the light cleared, a frame's wait and the palette rebuilt, before its next scene."""
    light = owl_light(flows[CASTLE])
    assert light == owl_light(base[CASTLE])
    assert light[0] == ARRIVAL and light[-len(UNLIT) :] == UNLIT
    assert [effect[2]["EventName"] for effect in light if effect[1] == TRANSITION] == [PANORAMA_SCENE, OWL_SCENE]


@pytest.mark.parametrize("mode", MODES)
def test_the_forest_exit_lights_the_field_only_before_the_owl_panorama_and_the_send_off(mode):
    flows, base = synthetic(mode)
    check_forest_exit(flows, base)
    entries = (FOREST_EXIT, "TestStartsAtTheFirstFieldWrite")  # an entry naming the write still reaches it
    for entry, played, sent in product(entries, (False, True), (False, True)):
        state = {**START, PANORAMA: played, SENDOFF: sent, FIRST_FIELD: False}
        promised = outcome(base[CASTLE], entry, state, **reference(mode, CASTLE))
        assert outcome(flows[CASTLE], entry, state) == promised, (entry, played, sent)


@pytest.mark.parametrize("mode", MODES)
def test_the_owl_arrival_and_the_courtyard_stay_native(mode):
    flows, base = synthetic(mode)
    check_owl_arrival(flows, base)
    assert courtyard(flows[CASTLE]) == courtyard(base[CASTLE])
    for played, lit, arrived in product((False, True), repeat=3):
        state = {**START, PANORAMA: played, FIRST_FIELD: lit, ARRIVED: arrived}
        got = outcome(flows[CASTLE], OWL_ARRIVAL, state, scenes=True)
        assert got == outcome(base[CASTLE], OWL_ARRIVAL, state, scenes=True), state
        assert (got[1][FIRST_FIELD], got[1][PANORAMA], got[1][ARRIVED]) == (False, True, True)


# Each route: (start history, the entries in play order, the one that returns the light to the ordinary one, or
# None when it is never set). The late route meets neither the owl nor the bridge before the send-off.
ROUTES = {
    "natural owl": (FRESH, (FOREST_EXIT, OWL_ARRIVAL, MEET_ZELDA, SEND_OFF), OWL_ARRIVAL),
    "Kaepora skip": (SKIPPED, (FOREST_EXIT, MEET_ZELDA, SEND_OFF), None),
    "owl missed": (FRESH, (FOREST_EXIT, MEET_ZELDA, SEND_OFF), SEND_OFF),
    "first Forest exit after the send-off": (FRESH, (MEET_ZELDA, SEND_OFF, FOREST_EXIT), None),
    "light kept by an older build": ({**SKIPPED, FIRST_FIELD: True}, (MEET_ZELDA, SEND_OFF), SEND_OFF),
}


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("route", ROUTES)
def test_every_route_ends_with_the_ordinary_light(mode, route):
    flows, _ = synthetic(mode)
    history, entries, relit = ROUTES[route]
    state = {**START, "Step_DoorOfTime": "NotReady", SENDOFF: False, **history}
    for entry in entries:
        before = state
        effects, state = outcome(flows[DOOR if entry == SEND_OFF else CASTLE], entry, state, scenes=True)
        assert len(relit_at(effects)) == (entry == relit), (entry, effects)
        if entry == FOREST_EXIT:
            assert state[FIRST_FIELD] is (before[FIRST_FIELD] or not (before[PANORAMA] or before[SENDOFF]))
    assert (state[FIRST_FIELD], state[ARRIVED], state[SENDOFF]) == (False, True, True)
    assert state["Step_DoorOfTime"] == "Step02"


def runners(fc, at):
    """The events and entries that continue to event ``at``."""
    found = [
        event.name
        for event in fc.events
        if at in [target for _, target in getattr(event, "cases", ())] or getattr(event, "next", evfl.NONE) == at
    ]
    return found + [entry.name for entry in fc.entry_points if at in (entry.main_event, *entry.sub_flow_events)]


def unlight_castle(fc):
    """The exact inverse of the castle guard: the moved light write returns to its own index, the appended send-off
    query goes, and the played-history query, registered for the guard and read by nothing else, is dropped."""
    fc = deepcopy(fc)
    at, moved, sent, onward = (index(fc, name) for name in (LIGHT_WRITE, MOVED, SENT, TRAVEL))
    guard, write = fc.events[at], fc.events[moved]
    actor = fc.actors[guard.actor]
    assert (moved, sent) == (len(fc.events) - 2, len(fc.events) - 1)
    histories = ((at, PANORAMA_SCENE, [(0, onward), (1, sent)]), (sent, SENDOFF_SCENE, [(0, onward), (1, moved)]))
    for i, history, cases in histories:
        ask = fc.events[i]
        assert isinstance(ask, evfl.SwitchEvent) and ask.actor == guard.actor, ask
        assert (actor.name, actor.queries[ask.query], ask.params, ask.cases) == (
            "GameDataActor",
            HAVE_PLAYED,
            {"EventName": history},
            cases,
        )
    assert write.next == onward and (runners(fc, moved), runners(fc, sent)) == ([SENT], [LIGHT_WRITE])
    fc.events[at] = replace(write, name=LIGHT_WRITE)
    del fc.events[moved:]
    asks = [event for event in fc.events if isinstance(event, evfl.SwitchEvent) and event.actor == guard.actor]
    assert guard.query == len(actor.queries) - 1 and all(event.query != guard.query for event in asks)
    actor.queries.pop()
    return fc


def test_the_castle_guard_is_exactly_invertible():
    native = evfl.write(castle_flow())
    for mode in MODES:
        shipped = door.changes({}, mode=mode)[CASTLE](native)
        assert evfl.write(evfl.read(shipped)) == shipped
        document = evfl.read(shipped)
        document.flowchart = unlight_castle(document.flowchart)
        assert evfl.write(document) == native, mode


def _set(name, field, value):
    def mutate(fc):
        named(fc, name).params[field] = value

    return mutate


def _retarget(name, target):
    def mutate(fc):
        named(fc, name).next = index(fc, target)

    return mutate


def _renamed(name):
    def mutate(fc):
        named(fc, name).name = f"{name}Moved"

    return mutate


def _second_game_data_actor(fc):
    fc.actors.append(evfl.Actor("GameDataActor"))


CASTLE_REFUSALS = [
    pytest.param(_set(LIGHT_WRITE, "Value", False), LIGHT_WRITE, id="light-value"),
    pytest.param(_set(LIGHT_WRITE, "GameDataName", "HyruleField_Test"), LIGHT_WRITE, id="light-name"),
    pytest.param(_retarget(LIGHT_WRITE, "Event203"), LIGHT_WRITE, id="light-next"),
    pytest.param(_set(TRAVEL, "NextBanc", "HyruleField_Adult"), TRAVEL, id="travel-place"),
    pytest.param(_set(TRAVEL, "NextStartPos", "HyruleField_Test"), TRAVEL, id="travel-position"),
    pytest.param(_renamed(LIGHT_WRITE), rf"\['{LIGHT_WRITE}'\]", id="missing-light"),
    pytest.param(_renamed(TRAVEL), rf"\['{TRAVEL}'\]", id="missing-travel"),
    pytest.param(_second_game_data_actor, "GameDataActor", id="two-game-data-actors"),
]


@pytest.mark.parametrize("mutate,match", CASTLE_REFUSALS)
def test_a_changed_native_forest_exit_light_is_refused(mutate, match):
    document = castle_flow()
    mutate(document.flowchart)
    for mode in MODES:
        with pytest.raises(PatchError, match=match):
            door.changes({}, mode=mode)[CASTLE](evfl.write(document))


def test_another_flowchart_and_a_second_castle_guard_are_refused():
    transform = door.changes({}, mode="closed")[CASTLE]
    with pytest.raises(PatchError, match="Goto_HyruleCastle"):
        transform(evfl.write(door_flow()))
    with pytest.raises(PatchError, match=MOVED):
        transform(transform(evfl.write(castle_flow())))


# Real data.

BANC_ARRIVE = "Event/EventFlow/Dm_SY_BancChangeArrive.bfevfl.zs"
DEKU_TREE = "Event/EventFlow/Meet_DekuTree.bfevfl.zs"
FIRST_ADULT = "HrlField_HasEnteredFirstTime_Adult"


@pytest.fixture(scope="module")
def native(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    paths = (DOOR, CASTLE, BANC_ARRIVE, DEKU_TREE)
    flows = {path: dictionaries.decompress(path, (romfs / path).read_bytes()) for path in paths}
    game_data = byml.read(dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes()))["Data"]
    enums = {int(row["Hash"]): row for row in game_data["Enum"]}
    quests = ("DoorOfTime", "Get_StoneOfFire", "Get_StoneOfWater")
    orders = {quest: tuple(enums[key(f"Step_{quest}")]["RawValues"]) for quest in quests}
    return dictionaries, flows, {**ORDERS, **orders}, game_data


@pytest.mark.dump
def test_dump_native_light_and_query_cases(native):
    """The light is saved; the Forest exit sets it right before the Field travel, the owl clears it in
    the order the send-off copies. Case 0 is true: a native played-history switch replays its own scene on case 1,
    and the native first-adult clearer clears its own flag on case 0."""
    _, flows, _, game_data = native
    row = {int(row["Hash"]): row for row in game_data["Bool"]}[key(FIRST_FIELD)]
    assert int(row["SaveFileIndex"]) >= 0, row
    fc = evfl.read(flows[CASTLE]).flowchart
    farewell, light, travel = (named(fc, name) for name in (FAREWELL, LIGHT_WRITE, TRAVEL))
    assert (farewell.next, light.next, travel.next) == (index(fc, LIGHT_WRITE), index(fc, TRAVEL), evfl.NONE)
    assert (fc.actors[light.actor].name, fc.actors[light.actor].actions[light.action], light.params) == LIT
    assert fc.actors[travel.actor].actions[travel.action] == BANC_CHANGE
    assert (travel.params["NextBanc"], travel.params["NextStartPos"]) == (
        "HyruleField_Child",
        "HyruleField_FrontOfLostWoodBridge",
    )
    check_owl_arrival({CASTLE: fc}, {CASTLE: fc})
    replays = []  # (flow, switch, case) where a played-history switch plays the very scene it asked about
    for path in (BANC_ARRIVE, DEKU_TREE):
        flow = evfl.read(flows[path]).flowchart
        for event in flow.events:
            if not isinstance(event, evfl.SwitchEvent) or flow.actors[event.actor].queries[event.query] != HAVE_PLAYED:
                continue
            for case, target in event.cases:
                scene = flow.events[target] if target != evfl.NONE else None
                if not isinstance(scene, evfl.ActionEvent):
                    continue
                action = flow.actors[scene.actor].actions[scene.action]
                if action == TRANSITION and scene.params["EventName"] == event.params["EventName"]:
                    replays.append((path, event.name, case))
    assert replays and {case for *_, case in replays} == {1}, replays
    flow = evfl.read(flows[BANC_ARRIVE]).flowchart
    clearer = named(flow, "Event257")
    assert flow.actors[clearer.actor].queries[clearer.query] == READ_BOOL
    assert clearer.params["GameDataName"] == FIRST_ADULT
    cleared = flow.events[dict(clearer.cases)[0]]
    assert flow.actors[cleared.actor].actions[cleared.action] == SET_BOOL
    assert (cleared.params["GameDataName"], cleared.params["Value"]) == (FIRST_ADULT, False)


@pytest.mark.dump
@pytest.mark.parametrize("mode", MODES)
def test_dump_the_real_send_off_ends_the_first_field_light(native, mode):
    """Every other real door entry is checked by reach: the reference engine models only the story's events."""
    _, flows, orders, _ = native
    shipped, base = flows_for({DOOR: flows[DOOR]}, mode)
    check_send_off(shipped, base, mode, orders)
    assert light_entries(shipped[DOOR]) == [SEND_OFF]


@pytest.mark.dump
@pytest.mark.parametrize("mode", MODES)
def test_dump_the_real_forest_exit_owl_and_courtyard(native, mode):
    _, flows, orders, _ = native
    shipped, base = flows_for({CASTLE: flows[CASTLE]}, mode)
    check_forest_exit(shipped, base, orders)
    check_owl_arrival(shipped, base)
    assert courtyard(shipped[CASTLE]) == courtyard(base[CASTLE])


@pytest.mark.dump
def test_dump_the_castle_guard_is_exactly_invertible(native):
    _, flows, _, _ = native
    for mode in MODES:
        shipped = door.changes({}, mode=mode)[CASTLE](flows[CASTLE])
        assert evfl.write(evfl.read(shipped)) == shipped
        document = evfl.read(shipped)
        document.flowchart = unlight_castle(document.flowchart)
        assert evfl.write(document) == flows[CASTLE], mode  # every unrelated byte and path is native


def _light_writers(path, data):
    """(flow, event, value written) for every first-Field light write in ``data``."""
    fc = evfl.read(data).flowchart
    return [
        (path, event.name, event.params["Value"])
        for event in (fc.events if fc is not None else ())
        if isinstance(event, evfl.ActionEvent)
        and fc.actors[event.actor].actions[event.action] == SET_BOOL
        and (event.params or {}).get("GameDataName") == FIRST_FIELD
    ]


@pytest.mark.dump
def test_dump_only_the_send_off_and_the_castle_guard_write_the_light(romfs, native):
    """The audit's full-resource scan found no other writer in packs, AINB or GameData expressions."""
    dictionaries, _, _, _ = native
    flows = {}
    for file in sorted((romfs / "Event/EventFlow").glob("*.bfevfl.zs")):
        path = file.relative_to(romfs).as_posix()
        data = dictionaries.decompress(path, file.read_bytes())
        if path in (DOOR, CASTLE) or FIRST_FIELD.encode() in data:
            flows[path] = data
    native_writers = sorted(row for path, data in flows.items() for row in _light_writers(path, data))
    assert native_writers == [(CASTLE, "Event217", False), (CASTLE, LIGHT_WRITE, True)]
    expected = sorted([(CASTLE, "Event217", False), (CASTLE, MOVED, True), (DOOR, REPAIR[1], False)])
    for mode in MODES:
        changes = door.changes({}, mode=mode)
        shipped = {path: changes[path](data) if path in changes else data for path, data in flows.items()}
        assert sorted(row for path, data in shipped.items() for row in _light_writers(path, data)) == expected, mode
