"""Door of Time story writes only move the quest forward, so an early first pull keeps its Complete.

Native facts (whole-dump audit, round 16): eleven ``EventExecuteProgressChallengeStep`` actions write the
``DoorOfTime`` quest. ``SageRoom_MeetRauru``'s Event93 writes ``Complete`` and stays native. The other ten
each become a ``GameDataActor`` ``EventQueryIsGameDataBoolExp`` on the native strict
``DoorOfTime_IsAfter_<step>_Exp`` at the writer's own index. True (already past the step) continues straight
to the write's native next; false (before or at the step) runs the original write, appended as
``ClawshotDoor<event>Write`` with that same next. Callers, entry points and sub flow registrations keep their
indices, and the continuations (rewards, camera, progress notices, other quests' writes) stay native. No saved
flag, default or actor is added. An end continuation has no true case, the native shape of every switch.

``DoorOfTime``: send-off Event7 (Step02, then Fire's Event62), stone count Event147 and Event148 (Step2_1 and
Step2_2, then Event5) and Event37 (Step03, then Event77), escape Event12 (Step04, then Event140), the Song of
Time aftermath Event14 (Step05, then notice Event171) and the door opening Event57 (Step06, end).
``Goto_HyruleCastle`` Event32 (Step01, then Event202), ``Dm_SY_Ocarina_SariaSong`` Event172 and
``Npc_Hylia_Zelda_Child`` Event42 (native spelling ``Srep2_1_1``, end).

The stone count's Event77 raises the field drawbridge (``IsHyruleFieldBridgeClose`` true, then Event4's count);
only the escape's Event78 lowers it. Once Step03 is forward-only, a stone count after the escape would raise it
for good, so Event77 becomes the same kind of query on ``ESCAPE_READY``: true runs the moved raise, false goes
straight to Event4. That unsaved BoolExp belongs to the door stage (DoorOfTime past Step2_2, all three stone
quests complete, the send-off played, ``HyruleField_DoorOfTime_Escape`` unplayed); this module only reads it.
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
    "Event/EventFlow/Goto_HyruleCastle.bfevfl.zs": (
        ("Event32", "Step01", "Event202", {**_QUIET, "IsIgnoreCompletedChallenge": True}),
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


def _forward(path: str, data: bytes) -> bytes:
    """Guard the lower DoorOfTime writes and bridge raise of ``path``; keep references and native continuations."""
    document = evfl.read(data)
    fc = document.flowchart
    flow = path.rsplit("/", 1)[-1].removesuffix(".bfevfl.zs")
    if fc is None or fc.name != flow:
        raise PatchError(f"Door of Time: {path} holds no {flow} flowchart")
    guards = _GUARDS[path]
    bridge = (_BRIDGE[path],) if path in _BRIDGE else ()
    pinned = (*guards, _COMPLETE[path]) if path in _COMPLETE else guards
    renamed = {f"{_PREFIX}{name}Write" for name, *_ in (*guards, *bridge)}
    if done := [event.name for event in fc.events if event.name in renamed]:
        raise PatchError(f"Door of Time: {flow} is already patched: {done}")
    index = {event.name: i for i, event in enumerate(fc.events)}
    if missing := [name for name, *_ in (*pinned, *bridge) if name not in index]:
        raise PatchError(f"Door of Time: {flow} lacks native events {missing}")
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
    for name, _, _ in bridge:
        at = index[name]
        raise_bridge = fc.events[at]
        # True (the escape may play now) runs the moved raise; false continues at its native next.
        cases = [(0, len(fc.events)), (1, raise_bridge.next)]
        fc.events[at] = evfl.SwitchEvent(name, actor, query, cases, {"GameDataName": ESCAPE_READY})
        raise_bridge.name = f"{_PREFIX}{name}Write"
        fc.events.append(raise_bridge)
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"Door of Time: {path} does not read back as the edited flow")
    return result


def _transform(path: str) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        return _forward(path, data)

    return transform


def changes() -> FileChanges:
    """Forward-only DoorOfTime writes and the escape-bound bridge raise, for both early door modes.

    Composes with Darunia's Event62 guard in either order. The door stage must add the ``ESCAPE_READY`` row."""
    return {path: _transform(path) for path in _GUARDS}
