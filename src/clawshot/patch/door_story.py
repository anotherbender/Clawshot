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
"""

from collections.abc import Callable

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

ESCAPE_READY = "Clawshot.Door.EscapeReady"  # the door stage's unsaved BoolExp: Zelda's escape may play now

_CHALLENGE = "DoorOfTime"
_PREFIX = "ClawshotDoor"
_GAME_DATA_ACTOR = "GameDataActor"
_READ_EXPRESSION = "EventQueryIsGameDataBoolExp"
_READ_HISTORY = "EventQueryHavePlayedEvent"
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
_BRIDGE_ACTION = "EventTriggerSetGameDataBool"
# (event, its native parameters, its native next): the drawbridge raise behind Step03.
_BRIDGE = {_DOOR_FLOW: ("Event77", {"GameDataName": "IsHyruleFieldBridgeClose", "Index": -1, "Value": True}, "Event4")}


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


def _game_data_actor(fc: evfl.Flowchart) -> int:
    found = [i for i, actor in enumerate(fc.actors) if actor.name == _GAME_DATA_ACTOR]
    if len(found) != 1 or fc.actors[found[0]].secondary_name or fc.actors[found[0]].entry_point != evfl.NONE:
        unexpected = [fc.actors[i] for i in found]
        raise PatchError(f"Door of Time: {fc.name} lacks its one native {_GAME_DATA_ACTOR}: {unexpected!r}")
    return found[0]


def _slot(names: list[str], name: str) -> int:
    if name not in names:
        names.append(name)
    return names.index(name)


def _next_name(fc: evfl.Flowchart, event: evfl.Event) -> str | None:
    return fc.events[event.next].name if isinstance(event, evfl.ActionEvent) and event.next != evfl.NONE else None


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
            or _op(fc, raise_bridge) != f"{_GAME_DATA_ACTOR}.{_BRIDGE_ACTION}"
            or raise_bridge.params != params
            or next_name != tail
        ):
            raise PatchError(f"Door of Time: changed native {flow}/{name}: {raise_bridge!r}, next {next_name!r}")
    if unknown := sorted(set(_native_writers(fc)) - {name for name, _, _, _ in pinned}):
        raise PatchError(f"Door of Time: {flow} has unknown native DoorOfTime writes {unknown}")
    actor = _game_data_actor(fc)
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
        first = len(fc.events)
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
            ]
        )
        counter.main_event = first
        sendoff.sub_flow_events.append(first + 2)
        # Hook before Event62: its native end and Darunia's guard remain untouched in either edit order.
        sendoff_write.next = first + 2
        if early:
            guard = fc.events[index["Event7"]]
            guard.cases = [(case, first + 2 if case == 0 else target) for case, target in guard.cases]
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"Door of Time: {path} does not read back as the edited flow")
    return result


def _transform(path: str, *, early: bool) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        return _forward(path, data, early=early)

    return transform


def changes(*, early: bool = True) -> FileChanges:
    """Shared stone-order repair, plus late-write guards when the Door may open early.

    The courtyard reset is native. Event62 and its tail stay compatible with Darunia in either edit order."""
    paths = _GUARDS if early else (_DOOR_FLOW,)
    return {path: _transform(path, early=early) for path in paths}
