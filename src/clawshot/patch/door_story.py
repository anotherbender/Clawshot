"""Preserve late Door of Time progress without breaking the native courtyard reset.

Native facts (whole-dump audit, round 16): eleven ``EventExecuteProgressChallengeStep`` actions write the
``DoorOfTime`` quest. Rauru's Event93 writes ``Complete`` and stays native. Goto_HyruleCastle Event32 also
stays native: its forced Step01 reset is required by Impa's exact-Step01 lesson after pre-courtyard stone
or Saria callbacks. In early modes the other nine writes become queries on native strict
``DoorOfTime_IsAfter_<step>_Exp``: already past the target, continue to the native next; otherwise run
the original appended write. Native rewards, notices and other quests' writes retain their behavior.

``DoorOfTime``: send-off Event7 (Step02, then Fire's Event62), stone count Event147/Event148 (Step2_1/Step2_2,
then Event5) and Event37 (Step03, then Event77), escape Event12 (Step04, then Event140), Time-song aftermath
Event14 (Step05, then Event171) and opening Event57 (Step06, end). ``Dm_SY_Ocarina_SariaSong`` Event172 and
``Npc_Hylia_Zelda_Child`` Event42 write native ``Srep2_1_1``.

In every door mode, stone counting waits for the real send-off and stops after the once-only escape.
This prevents premature Step03/bridge raising, including the native closed-mode escape sensor. The
send-off recounts before Event62, preserving Darunia's independently guarded Fire continuation. The
counter's original branches, bridge write and count values stay native; no saved history is forged.

Two clock transitions ship in every mode too. The native clock runs only with the Hyrule Field owl arrival
(``HyruleField_ArriveEntrance``, set natively only by the owl's Goto_HyruleCastle Event153), the send-off's
history and no first-adult hold (``HrlField_HasEnteredFirstTime_Adult``). Routes that reach the courtyard
without that owl leave the arrival unset, so after the send-off scene (Event10) and its Step02 the arrival is
asked and, only when unset, set before the recount. The first-adult hold is set by Dm_TimeTemple_0055 and
cleared natively when adult Link walks from the Market to the Field; ``Market_Adult_Field_AdultToChild``
clears it as well, right after its native ``Sequence_IsChildhood`` write, so a real return to child never
keeps the hold. At the send-off, an independent guard also clears a set ``HyruleField_ChangeENV``, waits one
frame and rebuilds the conditional environment palette, as the skipped owl does. The Forest exit sets this
first-arrival environment only while the Field panorama is unplayed. No other history, quest or inventory is written.
"""

from collections.abc import Callable

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

ESCAPE_READY = "Clawshot.Door.EscapeReady"  # the door stage's unsaved BoolExp: Zelda's escape may play now

_ARRIVED = "HyruleField_ArriveEntrance"  # saved Bool, the Field owl arrival the native clock reads
_FIRST_ADULT = "HrlField_HasEnteredFirstTime_Adult"  # saved Bool, the first adult arrival's clock hold
_FIRST_ENV = "HyruleField_ChangeENV"  # saved Bool: first-arrival fixed lighting, cleared by the owl
_PANORAMA = "Dm_HrlField_0000"
_CASTLE_FLOW = "Event/EventFlow/Goto_HyruleCastle.bfevfl.zs"
_WAIT = "EventWait"
_REBUILD_ENV = "Event_RebuildConditionEnvTimePalette"
_CLOCK = "ClawshotClock"
_CHALLENGE = "DoorOfTime"
_PREFIX = "ClawshotDoor"
_GAME_DATA_ACTOR = "GameDataActor"
_READ_EXPRESSION = "EventQueryIsGameDataBoolExp"
_READ_HISTORY = "EventQueryHavePlayedEvent"
_READ_BOOL = "EventQueryIsGameDataBool"
_SET_BOOL = "EventTriggerSetGameDataBool"
_ESCAPE_EVENT = "HyruleField_DoorOfTime_Escape"
_SENDOFF_EVENT = "Dm_HrlField_0020"
_COUNTER = "DoorOfTime_CheckStoneNum"
_SENDOFF = "DoorOfTime_SendOff"
_CHALLENGE_ACTOR = "ChallengeSystemActor"
_STEP_ACTION = "EventExecuteProgressChallengeStep"
_WRITE = {
    "IsWaitEnd": True,
    "IsIgnoreCompletedChallenge": False,
    "IsIgnoreChallengeProgressUI": False,
    "ChallengeName": _CHALLENGE,
}
_QUIET = {**_WRITE, "IsIgnoreChallengeProgressUI": True}
_DOOR_FLOW = "Event/EventFlow/DoorOfTime.bfevfl.zs"
# Per flow: (writer, step written, its native next or None for the end, its native parameters but StepName).
_GUARDS = {
    _DOOR_FLOW: (
        ("Event7", "Step02", "Event62", _WRITE),
        ("Event147", "Step2_1", "Event5", _WRITE),
        ("Event148", "Step2_2", "Event5", _WRITE),
        ("Event37", "Step03", "Event77", _WRITE),
        ("Event12", "Step04", "Event140", _WRITE),
        ("Event14", "Step05", "Event171", _WRITE),
        ("Event57", "Step06", None, _WRITE),
    ),
    "Event/EventFlow/Dm_SY_Ocarina_SariaSong.bfevfl.zs": (("Event172", "Srep2_1_1", None, _QUIET),),
    "Event/EventFlow/Npc_Hylia_Zelda_Child.bfevfl.zs": (("Event42", "Srep2_1_1", None, _QUIET),),
}
_COMPLETE = {_DOOR_FLOW: ("Event93", "Complete", None, _WRITE)}
# (event, its native parameters, its native next): the drawbridge raise behind Step03.
_BRIDGE = {_DOOR_FLOW: ("Event77", {"GameDataName": "IsHyruleFieldBridgeClose", "Index": -1, "Value": True}, "Event4")}
_ERA_FLOW = "Event/EventFlow/Market_Adult_Field_AdultToChild.bfevfl.zs"
_ERA = "Market_Adult_Field_AdultToChild"  # its flowchart and only entry, requested by the Master Sword pedestal
_ERA_SWAP = "ReplaceEquipmentForEraChange"  # the registered equipment sub flow, native Event7, before the age write
_CHILDHOOD = {"GameDataName": "Sequence_IsChildhood", "Index": -1, "Value": True}  # native Event1, then Event0
_TO_CHILD = {"NextBanc": "Market_Child", "BootEventName": "Dm_TimeTemple_0075"}  # native Event0's travel


def _op(fc: evfl.Flowchart, event: evfl.Event) -> str | None:
    if not isinstance(event, evfl.ActionEvent | evfl.SwitchEvent):
        return None
    actor = fc.actors[event.actor]
    name = actor.actions[event.action] if isinstance(event, evfl.ActionEvent) else actor.queries[event.query]
    return f"{actor.name}{'/' + actor.secondary_name if actor.secondary_name else ''}.{name}"


def _native_writers(fc: evfl.Flowchart) -> list[str]:
    """Every DoorOfTime step action not added by Clawshot, whatever its actor's secondary name."""
    return [
        event.name
        for event in fc.events
        if isinstance(event, evfl.ActionEvent)
        and not event.name.startswith("Clawshot")
        and fc.actors[event.actor].name == _CHALLENGE_ACTOR
        and fc.actors[event.actor].actions[event.action] == _STEP_ACTION
        and (event.params or {}).get("ChallengeName") == _CHALLENGE
    ]


def _native_actor(fc: evfl.Flowchart, name: str) -> int:
    found = [i for i, actor in enumerate(fc.actors) if actor.name == name]
    if len(found) != 1 or fc.actors[found[0]].secondary_name or fc.actors[found[0]].entry_point != evfl.NONE:
        unexpected = [fc.actors[i] for i in found]
        raise PatchError(f"Door of Time: {fc.name} lacks its one native {name}: {unexpected!r}")
    return found[0]


def _slot(names: list[str], name: str) -> int:
    if name not in names:
        names.append(name)
    return names.index(name)


def _next_name(fc: evfl.Flowchart, event: evfl.Event) -> str | None:
    return fc.events[event.next].name if isinstance(event, evfl.ActionEvent) and event.next != evfl.NONE else None


def _plays_sendoff(fc: evfl.Flowchart, start: int, writer: int) -> bool:
    """Whether the plain action chain from ``start`` plays the send-off scene before it reaches ``writer``."""
    at, played, seen = start, False, set()
    while at != writer:
        event = fc.events[at] if at != evfl.NONE and at not in seen else None
        if not isinstance(event, evfl.ActionEvent):
            return False
        seen.add(at)
        scene = _op(fc, event) == "EventSystemActor.EventTransition"
        played = played or (scene and (event.params or {}).get("EventName") == _SENDOFF_EVENT)
        at = event.next
    return played


def _forward(path: str, data: bytes, *, early: bool) -> bytes:
    """Repair counted-stone ordering in every mode; guard late quest writes only in early modes."""
    document = evfl.read(data)
    fc = document.flowchart
    flow = path.rsplit("/", 1)[-1].removesuffix(".bfevfl.zs")
    if fc is None or fc.name != flow:
        raise PatchError(f"Door of Time: {path} holds no {flow} flowchart")
    guards = _GUARDS[path] if early else ()
    bridge = (_BRIDGE[path],) if path in _BRIDGE else ()
    pinned = (*_GUARDS[path], _COMPLETE[path]) if path in _COMPLETE else _GUARDS[path]
    renamed = {f"{_PREFIX}{name}Write" for name, *_ in guards}
    if path == _DOOR_FLOW:
        renamed.update(f"{_PREFIX}{name}" for name in ("CountSendoff", "CountEscape", "SendoffRecount"))
        renamed.update(
            f"{_CLOCK}{name}"
            for name in ("Arrival", "Arrived", "Environment", "ClearedEnvironment", "WaitEnvironment", "RebuildEnvironment")
        )
    if done := [event.name for event in fc.events if event.name in renamed]:
        raise PatchError(f"Door of Time: {flow} is already patched: {done}")
    index = {event.name: i for i, event in enumerate(fc.events)}
    if missing := [name for name, *_ in (*pinned, *bridge) if name not in index]:
        raise PatchError(f"Door of Time: {flow} lacks native events {missing}")
    sendoff_write = None
    if path == _DOOR_FLOW:
        entries = {entry.name: entry for entry in fc.entry_points}
        if missing := [name for name in (_COUNTER, _SENDOFF) if name not in entries]:
            raise PatchError(f"Door of Time: {flow} lacks native entries {missing}")
        counter, sendoff = entries[_COUNTER], entries[_SENDOFF]
        if (
            fc.events[counter.main_event].name != "Event38"
            or fc.events[sendoff.main_event].name != "Event65"
            or sendoff.sub_flow_events
        ):
            raise PatchError(f"Door of Time: changed counter/send-off entries: {counter!r}, {sendoff!r}")
        if not _plays_sendoff(fc, sendoff.main_event, index["Event7"]):
            raise PatchError(f"Door of Time: {flow} send-off no longer plays {_SENDOFF_EVENT} straight into Event7")
        sendoff_write = fc.events[index["Event7"]]
    for name, step, tail, params in pinned:
        write = fc.events[index[name]]
        next_name = _next_name(fc, write)
        if (
            not isinstance(write, evfl.ActionEvent)
            or _op(fc, write) != f"{_CHALLENGE_ACTOR}.{_STEP_ACTION}"
            or write.params != {**params, "StepName": step}
            or next_name != tail
        ):
            raise PatchError(f"Door of Time: changed native {flow}/{name}: {write!r}, next {next_name!r}")
    for name, params, tail in bridge:
        raise_bridge = fc.events[index[name]]
        next_name = _next_name(fc, raise_bridge)
        if (
            not isinstance(raise_bridge, evfl.ActionEvent)
            or _op(fc, raise_bridge) != f"{_GAME_DATA_ACTOR}.{_SET_BOOL}"
            or raise_bridge.params != params
            or next_name != tail
        ):
            raise PatchError(f"Door of Time: changed native {flow}/{name}: {raise_bridge!r}, next {next_name!r}")
    if unknown := sorted(set(_native_writers(fc)) - {name for name, _, _, _ in pinned}):
        raise PatchError(f"Door of Time: {flow} has unknown native DoorOfTime writes {unknown}")
    actor = _native_actor(fc, _GAME_DATA_ACTOR)
    query = _slot(fc.actors[actor].queries, _READ_EXPRESSION)
    for name, step, _, _ in guards:
        at = index[name]
        write = fc.events[at]
        # Reuse the writer's index for the query, so callers and entry registrations need no rewiring.
        # True means strictly past the step; equality still takes the native write. An end continuation
        # has no true case: no native switch names the absent event, a missing case ends the entry.
        appended = len(fc.events)
        cases = [(1, appended)] if write.next == evfl.NONE else [(0, write.next), (1, appended)]
        expression = {"GameDataName": f"{_CHALLENGE}_IsAfter_{step}_Exp"}
        fc.events[at] = evfl.SwitchEvent(name, actor, query, cases, expression)
        write.name = f"{_PREFIX}{name}Write"
        fc.events.append(write)
    if path == _DOOR_FLOW:
        history_query = _slot(fc.actors[actor].queries, _READ_HISTORY)
        read_bool = _slot(fc.actors[actor].queries, _READ_BOOL)
        set_bool = _slot(fc.actors[actor].actions, _SET_BOOL)
        system = _native_actor(fc, "EventSystemActor")
        world = _native_actor(fc, "EventWorldManagerController")
        wait = _slot(fc.actors[system].actions, _WAIT)
        rebuild = _slot(fc.actors[world].actions, _REBUILD_ENV)
        first = len(fc.events)
        recount, arrival = first + 2, first + 3
        environment = first + 5
        arrived = {"GameDataName": _ARRIVED, "Index": -1}
        fc.events.extend(
            [
                evfl.SwitchEvent(
                    f"{_PREFIX}CountSendoff",
                    actor,
                    history_query,
                    [(0, first + 1)],
                    {"EventName": _SENDOFF_EVENT},
                ),
                evfl.SwitchEvent(
                    f"{_PREFIX}CountEscape",
                    actor,
                    history_query,
                    [(1, counter.main_event)],
                    {"EventName": _ESCAPE_EVENT},
                ),
                evfl.SubFlowEvent(f"{_PREFIX}SendoffRecount", "", _COUNTER, index["Event62"], None),
                # The send-off scene has played: an owl-less route still lacks the arrival the clock reads.
                evfl.SwitchEvent(f"{_CLOCK}Arrival", actor, read_bool, [(0, environment), (1, first + 4)], arrived),
                evfl.ActionEvent(f"{_CLOCK}Arrived", actor, set_bool, environment, {**arrived, "Value": True}),
                # Independent of A: old owl-skipped saves can already have A but still force first-arrival light.
                evfl.SwitchEvent(
                    f"{_CLOCK}Environment",
                    actor,
                    read_bool,
                    [(0, environment + 1), (1, recount)],
                    {"GameDataName": _FIRST_ENV, "Index": -1},
                ),
                evfl.ActionEvent(
                    f"{_CLOCK}ClearedEnvironment",
                    actor,
                    set_bool,
                    environment + 2,
                    {"GameDataName": _FIRST_ENV, "Index": -1, "Value": False},
                ),
                evfl.ActionEvent(
                    f"{_CLOCK}WaitEnvironment", system, wait, environment + 3, {"IsWaitEnd": True, "Frames": 1}
                ),
                evfl.ActionEvent(f"{_CLOCK}RebuildEnvironment", world, rebuild, recount, None),
            ]
        )
        counter.main_event = first
        sendoff.sub_flow_events.append(recount)
        # Hook before Event62: its native end and Darunia's guard remain untouched in either edit order.
        sendoff_write.next = arrival
        if early:
            guard = fc.events[index["Event7"]]
            guard.cases = [(case, arrival if case == 0 else target) for case, target in guard.cases]
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"Door of Time: {path} does not read back as the edited flow")
    return result


def _first_field(data: bytes) -> bytes:
    """Do not re-enable the first-arrival palette after the native panorama has already played."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "Goto_HyruleCastle":
        raise PatchError(f"Door of Time: {_CASTLE_FLOW} holds no Goto_HyruleCastle flowchart")
    if done := [event.name for event in fc.events if event.name.startswith(_CLOCK)]:
        raise PatchError(f"Door of Time: Goto_HyruleCastle is already patched: {done}")
    index = {event.name: i for i, event in enumerate(fc.events)}
    if missing := [name for name in ("Event218", "Event42") if name not in index]:
        raise PatchError(f"Door of Time: Goto_HyruleCastle lacks native events {missing}")
    at, onward = index["Event218"], index["Event42"]
    writer, travel = fc.events[at], fc.events[onward]
    if (
        not isinstance(writer, evfl.ActionEvent)
        or _op(fc, writer) != f"{_GAME_DATA_ACTOR}.{_SET_BOOL}"
        or writer.params != {"GameDataName": _FIRST_ENV, "Index": -1, "Value": True}
        or writer.next != onward
        or not isinstance(travel, evfl.ActionEvent)
        or _op(fc, travel) != "GameSystemActor.EventReserveBancChange"
        or (travel.params or {}).get("NextBanc") != "HyruleField_Child"
        or (travel.params or {}).get("NextStartPos") != "HyruleField_FrontOfLostWoodBridge"
    ):
        raise PatchError(f"Door of Time: changed native first Field arrival: {writer!r}, {travel!r}")
    actor = _native_actor(fc, _GAME_DATA_ACTOR)
    query = _slot(fc.actors[actor].queries, _READ_HISTORY)
    fc.events[at] = evfl.SwitchEvent(
        writer.name, actor, query, [(0, onward), (1, len(fc.events))], {"EventName": _PANORAMA}
    )
    writer.name = f"{_CLOCK}FirstFieldENV"
    fc.events.append(writer)
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"Door of Time: {_CASTLE_FLOW} does not read back as the edited flow")
    return result


def _child_return(data: bytes) -> bytes:
    """Clear a pending first-adult hold once the Temple has made Link a child again, then travel natively."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != _ERA:
        raise PatchError(f"Door of Time: {_ERA_FLOW} holds no {_ERA} flowchart")
    if done := [event.name for event in fc.events if event.name.startswith(_CLOCK)]:
        raise PatchError(f"Door of Time: {_ERA} is already patched: {done}")
    index = {event.name: i for i, event in enumerate(fc.events)}
    if missing := [name for name in ("Event6", "Event7", "Event1", "Event0") if name not in index]:
        raise PatchError(f"Door of Time: {_ERA} lacks native events {missing}")
    entries = [entry for entry in fc.entry_points if entry.name == _ERA]
    if [(entry.main_event, entry.sub_flow_events) for entry in entries] != [(index["Event6"], [index["Event7"]])]:
        raise PatchError(f"Door of Time: changed {_ERA} entries: {fc.entry_points!r}")
    swap, age, travel = (fc.events[index[name]] for name in ("Event7", "Event1", "Event0"))
    if (
        not isinstance(swap, evfl.SubFlowEvent)
        or (swap.flowchart, swap.entry_point, swap.next) != (_ERA_SWAP, _ERA_SWAP, index["Event1"])
        or not isinstance(age, evfl.ActionEvent)
        or _op(fc, age) != f"{_GAME_DATA_ACTOR}.{_SET_BOOL}"
        or age.params != _CHILDHOOD
        or age.next != index["Event0"]
        or not isinstance(travel, evfl.ActionEvent)
        or _op(fc, travel) != "GameSystemActor.EventReserveBancChange"
        or {name: (travel.params or {}).get(name) for name in _TO_CHILD} != _TO_CHILD
    ):
        raise PatchError(f"Door of Time: changed native {_ERA} age change: {swap!r}, {age!r}, {travel!r}")
    actor = _native_actor(fc, _GAME_DATA_ACTOR)
    read_bool = _slot(fc.actors[actor].queries, _READ_BOOL)
    set_bool = _slot(fc.actors[actor].actions, _SET_BOOL)
    hold, clear = len(fc.events), len(fc.events) + 1
    held = {"GameDataName": _FIRST_ADULT, "Index": -1}
    # The native Field clearer's shape (Dm_SY_BancChangeArrive Event257/434): only a set hold is cleared.
    fc.events += [
        evfl.SwitchEvent(f"{_CLOCK}ChildReturn", actor, read_bool, [(0, clear), (1, age.next)], held),
        evfl.ActionEvent(f"{_CLOCK}ReturnedChild", actor, set_bool, age.next, {**held, "Value": False}),
    ]
    age.next = hold
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"Door of Time: {_ERA_FLOW} does not read back as the edited flow")
    return result


def _transform(path: str, *, early: bool) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        return _forward(path, data, early=early)

    return transform


def changes(*, early: bool = True) -> FileChanges:
    """Shared stone-order repair and clock transitions, plus late-write guards when the Door may open early.

    The courtyard reset is native. Event62 and its tail stay compatible with Darunia in either edit order."""
    paths = _GUARDS if early else (_DOOR_FLOW,)
    return {
        **{path: _transform(path, early=early) for path in paths},
        _ERA_FLOW: _child_return,
        _CASTLE_FLOW: _first_field,
    }
