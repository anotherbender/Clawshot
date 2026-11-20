"""Replace a scene at its caller boundary, never grant inside its animation graph.

The data names the early cut, native resume, grant and ordered retained effects.
A separate ordinary FlowchartEvent runs the shared GetPouchContent get window and
actual pouch add. Native cinematic entries never start on the replacement path.
Usable-instrument callers retain their entire original graph.
"""

import copy
import tomllib
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from clawshot.census.gifts import reachable
from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import keys, ocarina
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges, NewFile

DATA = Path(__file__).with_name("scene_handoffs.toml")
FLOW = "Clawshot_SceneGet"
FLOW_PATH = keys.flow_path(FLOW)
USABLE = "ClawshotSceneUsableOcarina"
DONOR = "KokiriForest_ArriveLostWood"  # ordinary FlowchartEvent, PlayerPos, no animation resources
PREFIX = "ClawshotScene"


@dataclass(frozen=True)
class Scene:
    name: str
    check: str
    flow: str
    entry: str
    cut: str
    resume: str
    condition: str
    grants: tuple[str, ...]
    before: tuple[str, ...]
    after: tuple[str, ...]
    histories: tuple[str, ...]
    once: str
    request: str = ""  # direct EventSetting admission, when no non-cinematic caller exists
    caller_before: tuple[str, ...] = ()  # effects needing the original event starter's binding


def load(path: Path = DATA) -> tuple[Scene, ...]:
    rows = tomllib.loads(path.read_text(encoding="utf-8"))["scene"]
    result = []
    names = set()
    fields = {field for field in Scene.__dataclass_fields__}
    for row in rows:
        row = {"request": "", "caller_before": [], **row}
        if set(row) != fields or row["name"] in names:
            raise PatchError(f"scene handoff: duplicate name or invalid fields: {row}")
        names.add(row["name"])
        for field in ("grants", "before", "after"):
            if any(not isinstance(ref, str) or ref.count("/") != 1 for ref in row[field]):
                raise PatchError(f"scene handoff: invalid {field}: {row}")
        if row["condition"] not in ("no_ocarina", "skip_saria_farewell"):
            raise PatchError(f"scene handoff: unsupported condition: {row}")
        result.append(Scene(**{key: tuple(value) if isinstance(value, list) else value for key, value in row.items()}))
    return tuple(result)


def _index(chart: evfl.Flowchart, name: str) -> int:
    matches = [i for i, event in enumerate(chart.events) if event.name == name]
    if len(matches) != 1:
        raise PatchError(f"scene handoff: {chart.name}: expected one event {name}, got {matches}")
    return matches[0]


def _encode(document: evfl.EventFlowFile) -> bytes:
    data = evfl.write(document)
    if evfl.read(data) != document:
        raise PatchError(f"scene handoff: {document.name}: written flow differs")
    return data


def _flow_transform(before: evfl.EventFlowFile, after: evfl.EventFlowFile):
    data = _encode(after)

    def transform(raw: bytes) -> bytes:
        if evfl.read(raw) != before:
            raise PatchError(f"scene handoff: {before.name}: prior transforms changed")
        return data

    return transform


def _table_transform(before: byml.Document, after: byml.Document):
    data = byml.dump(after)
    if byml.load(data) != after:
        raise PatchError("scene handoff: written event registry differs")

    def transform(raw: bytes) -> bytes:
        if byml.load(raw) != before:
            raise PatchError("scene handoff: prior event registry changed")
        return data

    return transform


def _usable(chart: evfl.Flowchart) -> None:
    """Native equality/Bool/pouch ABI: 0=true/held; explicit return 0=usable."""
    if any(entry.name == USABLE for entry in chart.entry_points):
        raise PatchError("scene handoff: instrument helper already installed")
    game, string = keys._operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataString64")
    _, boolean = keys._operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataBool")
    pouch, held = keys._operation(chart, "PouchSystemActor", "queries", "EventQueryIsExistInPouch")
    start = len(chart.events)
    chart.events.extend(
        [
            evfl.SwitchEvent(
                USABLE + "Time",
                game,
                string,
                [(0, start + 1), (1, start + 2)],
                {"GameDataName": ocarina.EQUIPPED, "Index": -1, "Value": ocarina.TIME},
            ),
            evfl.SwitchEvent(
                USABLE + "TimeHeld",
                pouch,
                held,
                [(0, start + 5), (1, start + 6)],
                {"Actor": ocarina.TIME, "Num": 1},
            ),
            evfl.SwitchEvent(
                USABLE + "Fairy",
                game,
                string,
                [(0, start + 3), (1, start + 6)],
                {"GameDataName": ocarina.EQUIPPED, "Index": -1, "Value": ocarina.FAIRY},
            ),
            evfl.SwitchEvent(
                USABLE + "FairyHeld",
                pouch,
                held,
                [(0, start + 4), (1, start + 6)],
                {"Actor": ocarina.FAIRY, "Num": 1},
            ),
            evfl.SwitchEvent(
                USABLE + "Child",
                game,
                boolean,
                [(0, start + 5), (1, start + 6)],
                {"GameDataName": "Sequence_IsChildhood", "Index": -1},
            ),
            evfl.ReturnEvent(USABLE + "Yes", 0),
            evfl.ReturnEvent(USABLE + "No", 1),
        ]
    )
    chart.entry_points.append(evfl.EntryPoint(USABLE, start))


def _operation(
    chart: evfl.Flowchart, original: evfl.Flowchart, actor_index: int, operation: str, kind: str = "actions"
) -> tuple[int, int]:
    donor = original.actors[actor_index]
    if donor.entry_point != evfl.NONE or donor.secondary_name:
        raise PatchError(f"scene handoff: scoped retained-effect actor {donor}")
    matches = [i for i, actor in enumerate(chart.actors) if actor.name == donor.name]
    if not matches:
        actor = copy.deepcopy(donor)
        actor.actions, actor.queries = [], []
        chart.actors.append(actor)
        matches = [len(chart.actors) - 1]
    index = matches[0]
    operations = getattr(chart.actors[index], kind)
    if operation not in operations:
        operations.append(operation)
    return index, operations.index(operation)


def _event_name(scene: Scene) -> str:
    return f"{FLOW}_{scene.name}"


def _entry_reachable(chart: evfl.Flowchart, entry_name: str) -> set[int]:
    """Include local subentries when updating a request row's preload declarations."""
    seen, entries = set(), [entry_name]
    visited = set()
    while entries:
        name = entries.pop()
        if name in visited:
            continue
        visited.add(name)
        nodes = reachable(chart, chart.entry_point(name).main_event)
        seen.update(nodes)
        for index in nodes:
            event = chart.events[index]
            if isinstance(event, evfl.SubFlowEvent | evfl.SubFlowSwitchEvent) and event.flowchart in ("", chart.name):
                entries.append(event.entry_point)
    return seen


def _admission(chart: evfl.Flowchart, scene: Scene, source: evfl.Flowchart) -> None:
    """A direct scene request gets a normal-event dispatcher; the native row becomes its child."""
    system = next(i for i, actor in enumerate(source.actors) if actor.name == "EventSystemActor")
    actor, transition = _operation(chart, source, system, "EventTransition")
    data_actor = next(i for i, actor in enumerate(source.actors) if actor.name == "GameDataActor")
    data, set_bool = _operation(chart, source, data_actor, "EventTriggerSetGameDataBool")
    start = len(chart.events)
    chart.events.extend(
        [
            evfl.SubFlowSwitchEvent(
                PREFIX + scene.name + "Admission",
                keys.POUCH,
                USABLE,
                [(0, start + 1), (1, start + 2)],
            ),
            evfl.ActionEvent(
                PREFIX + scene.name + "Native",
                actor,
                transition,
                start + 3,
                params={
                    "EventName": PREFIX + "Native_" + scene.name,
                    "IsWaitEnd": True,
                    "SpecialEventActionType": 1,
                    "FadeInTypeEventEnd": 0,
                },
            ),
            evfl.ActionEvent(
                PREFIX + scene.name + "Plain",
                actor,
                transition,
                params={
                    "EventName": _event_name(scene),
                    "IsWaitEnd": True,
                    "SpecialEventActionType": 1,
                    "FadeInTypeEventEnd": 0,
                },
            ),
            evfl.ActionEvent(
                PREFIX + scene.name + "NativeHistory",
                data,
                set_bool,
                params={"GameDataName": "HavePlayedEvent." + scene.request, "Index": -1, "Value": True},
            ),
        ]
    )
    chart.entry_points.append(evfl.EntryPoint(scene.name + "Admission", start, [start]))


def _plain_entry(chart: evfl.Flowchart, scene: Scene, documents: dict[str, evfl.EventFlowFile]) -> None:
    """Read effective rewards and retain ordered effects, including conditional data-only callbacks.

    ``flow/event`` retains that action only. ``flow/@entry`` projects a native
    callback's conditional state writes while discarding its speech/camera/poses.
    Queries and branch values are native, not a second Python story rule.
    """

    def source(ref: str):
        flow, name = ref.split("/")
        original = documents[flow].flowchart
        if original is None:
            raise PatchError(f"scene handoff: {ref}: expected a flowchart")
        return original, original.events[_index(original, name)]

    def append(event: evfl.Event) -> int:
        index = len(chart.events)
        event.name = PREFIX + scene.name + event.name + f"_{index}"
        chart.events.append(event)
        return index

    def state_action(original: evfl.Flowchart, event: evfl.ActionEvent) -> bool:
        actor = original.actors[event.actor]
        operation = actor.actions[event.action]
        return (
            actor.name in {"GameDataActor", "ChallengeSystemActor"}
            or (
                actor.name in {"GameSystemActor", "EventSystemActor"}
                and operation
                in {
                    "EventWait",
                    "EventTriggerZeldaNotesSimpleAddNPCTalkCount",
                    "EventTriggerZeldaNotesRequestSendDailyScreenShot",
                }
            )
            or actor.name == "EventWorldManagerController"
            and operation == "EventTrigger_SetTime"
        )

    def copy_action(original: evfl.Flowchart, event: evfl.ActionEvent, onward: int) -> int:
        actor = original.actors[event.actor]
        ai, operation = _operation(chart, original, event.actor, actor.actions[event.action])
        return append(evfl.ActionEvent(event.name + "Keep", ai, operation, onward, copy.deepcopy(event.params)))

    def project(flow: str, start: int, onward: int) -> int:
        original = documents[flow].flowchart
        memo = {}
        active = set()

        def call(target: int, continuation: int) -> int:
            if target == evfl.NONE:
                return continuation
            name = PREFIX + scene.name + "Effects" + str(len(chart.entry_points))
            calls = [
                i
                for i in sorted(reachable(chart, target))
                if isinstance(chart.events[i], evfl.SubFlowEvent | evfl.SubFlowSwitchEvent)
            ]
            chart.entry_points.append(evfl.EntryPoint(name, target, calls))
            return append(evfl.SubFlowEvent("Effects", "", name, continuation))

        def walk(index: int, stop: int = evfl.NONE) -> int:
            if index in (evfl.NONE, stop):
                return evfl.NONE
            key = index, stop
            if key in memo:
                return memo[key]
            if key in active:
                raise PatchError(f"scene handoff: cyclic retained callback {flow}/{original.events[index].name}")
            active.add(key)
            event = original.events[index]
            if isinstance(event, evfl.ActionEvent):
                next_index = walk(event.next, stop)
                actor = original.actors[event.actor]
                operation = actor.actions[event.action]
                if actor.name == "EventSystemActor" and operation == "EventTransition":
                    event_name = (event.params or {}).get("EventName")
                    if not isinstance(event_name, str) or isinstance(event_name, evfl.Argument):
                        raise PatchError(f"scene handoff: callback has a dynamic omitted event: {event}")
                    data_actor = next(i for i, actor in enumerate(original.actors) if actor.name == "GameDataActor")
                    ai, set_bool = _operation(chart, original, data_actor, "EventTriggerSetGameDataBool")
                    target = append(
                        evfl.ActionEvent(
                            event.name + "History",
                            ai,
                            set_bool,
                            next_index,
                            {"GameDataName": "HavePlayedEvent." + event_name, "Index": -1, "Value": True},
                        )
                    )
                elif state_action(original, event) and operation != "EventWait":
                    target = copy_action(original, event, next_index)
                else:
                    if actor.name == "PouchSystemActor":
                        raise PatchError(f"scene handoff: callback contains an unclassified pouch effect: {event}")
                    target = next_index
            elif isinstance(event, evfl.JoinEvent):
                target = walk(event.next, stop)
            elif isinstance(event, evfl.ForkEvent):
                continuation = walk(event.join, stop)
                branches = [walk(branch, event.join) for branch in event.forks]
                retained_branches = [branch for branch in branches if branch != evfl.NONE]
                # One state stream amid presentation branches retains its exact
                # order. Never invent an ordering between parallel state writers.
                if len(retained_branches) > 1:
                    raise PatchError(f"scene handoff: parallel callback state needs explicit ordered effects: {event}")
                target = call(retained_branches[0], continuation) if retained_branches else continuation
            elif isinstance(event, evfl.SubFlowEvent):
                continuation = walk(event.next, stop)
                if event.flowchart in ("", flow) and not event.params:
                    target = call(walk(original.entry_point(event.entry_point).main_event), continuation)
                elif event.flowchart == "Common_Camera_Pln":
                    callee = documents[event.flowchart].flowchart
                    pure = reachable(callee, callee.entry_point(event.entry_point).main_event)
                    if any(
                        not isinstance(callee.events[i], evfl.ActionEvent | evfl.JoinEvent | evfl.SwitchEvent)
                        or isinstance(callee.events[i], evfl.ActionEvent)
                        and (
                            state_action(callee, callee.events[i])
                            or callee.actors[callee.events[i].actor].name == "PouchSystemActor"
                        )
                        for i in pure
                    ):
                        raise PatchError(f"scene handoff: camera callback has unaudited effects: {event}")
                    target = continuation
                else:
                    raise PatchError(f"scene handoff: callback needs explicit retained effects: {flow}/{event.name}")
            elif isinstance(event, evfl.SwitchEvent | evfl.SubFlowSwitchEvent):
                cases = [(value, walk(target, stop)) for value, target in event.cases]
                if all(target == evfl.NONE for _, target in cases):
                    target = evfl.NONE
                elif isinstance(event, evfl.SwitchEvent):
                    actor = original.actors[event.actor]
                    if actor.name not in {
                        "GameDataActor",
                        "ChallengeSystemActor",
                        "PouchSystemActor",
                        "EventWorldManagerController",
                    } and not (
                        actor.name == "Player_Event" and actor.queries[event.query] == "EventQueryPlayerIsChild"
                    ):
                        raise PatchError(f"scene handoff: callback requires a cinematic query: {event}")
                    ai, query = _operation(chart, original, event.actor, actor.queries[event.query], "queries")
                    target = append(evfl.SwitchEvent(event.name, ai, query, cases, copy.deepcopy(event.params)))
                else:
                    callee_name = event.flowchart or flow
                    callee = documents[callee_name].flowchart
                    entry = callee.entry_point(event.entry_point)
                    pure = reachable(callee, entry.main_event)
                    if any(
                        not isinstance(callee.events[i], evfl.ReturnEvent)
                        and not (
                            isinstance(callee.events[i], evfl.SwitchEvent)
                            and callee.actors[callee.events[i].actor].name == "GameDataActor"
                        )
                        for i in pure
                    ):
                        raise PatchError(f"scene handoff: retained predicate is not data-only: {event}")
                    target = append(
                        evfl.SubFlowSwitchEvent(
                            event.name, callee_name, event.entry_point, cases, copy.deepcopy(event.params)
                        )
                    )
            else:
                raise PatchError(f"scene handoff: callback needs explicit retained effects: {flow}/{event.name}")
            active.remove(key)
            memo[key] = target
            return target

        # Keep real subflow return boundaries: an omitted query pin returns from
        # its callback, not from the handoff containing the reward and histories.
        return call(walk(start), onward)

    def retained(ref: str, onward: int) -> int:
        flow, name = ref.split("/")
        original = documents[flow].flowchart
        if name.startswith("@"):
            return project(flow, original.entry_point(name[1:]).main_event, onward)
        if name.startswith("?"):
            return project(flow, _index(original, name[1:]), onward)
        original, event = source(ref)
        if not isinstance(event, evfl.ActionEvent) or not state_action(original, event):
            raise PatchError(f"scene handoff: unaudited retained effect {ref}: {event}")
        return copy_action(original, event, onward)

    game = documents[keys.POUCH].flowchart
    data_actor = next(i for i, actor in enumerate(game.actors) if actor.name == "GameDataActor")
    ai, set_bool = _operation(chart, game, data_actor, "EventTriggerSetGameDataBool")
    _, query = _operation(chart, game, data_actor, "EventQueryIsGameDataBool", "queries")
    onward = evfl.NONE
    for history in reversed(scene.histories):
        onward = append(
            evfl.ActionEvent(
                "History",
                ai,
                set_bool,
                onward,
                {"GameDataName": "HavePlayedEvent." + history, "Index": -1, "Value": True},
            )
        )
    for ref in reversed(scene.after):
        onward = retained(ref, onward)
    for number, ref in reversed(list(enumerate(scene.grants))):
        original, event = source(ref)
        if isinstance(event, evfl.SubFlowEvent) and (event.flowchart, event.entry_point) == (
            keys.POUCH,
            "GetPouchContentByActorName",
        ):
            content = (event.params or {}).get("ActorName")
        elif isinstance(event, evfl.ActionEvent):
            actor = original.actors[event.actor]
            params = event.params or {}
            if (actor.name, actor.actions[event.action], params.get("Num")) != (
                "PouchSystemActor",
                "EventTriggerAddOrRemovePouchContent",
                1,
            ):
                raise PatchError(f"scene handoff: unsupported source grant {ref}: {event}")
            content = params.get("Actor")
        else:
            raise PatchError(f"scene handoff: unsupported source grant {ref}: {event}")
        if not isinstance(content, str) or isinstance(content, evfl.Argument) or not content:
            raise PatchError(f"scene handoff: {ref}: reward is not a literal actor: {content!r}")
        onward = append(
            evfl.SubFlowEvent(
                f"Grant{number}",
                keys.POUCH,
                "GetPouchContentByActorName",
                onward,
                {"ActorName": content},
            )
        )
    for ref in reversed(scene.before):
        onward = retained(ref, onward)
    start = append(
        evfl.SwitchEvent(
            "Once",
            ai,
            query,
            [(0, evfl.NONE), (1, onward)],
            {"GameDataName": scene.once, "Index": -1},
        )
    )
    calls = [
        i
        for i in sorted(reachable(chart, start))
        if isinstance(chart.events[i], evfl.SubFlowEvent | evfl.SubFlowSwitchEvent)
    ]
    chart.entry_points.append(evfl.EntryPoint(scene.name, start, calls))


@dataclass(frozen=True)
class Handoff:
    changes: FileChanges
    new_files: dict[str, NewFile]


def build(
    romfs: str | Path,
    *,
    skip_saria_farewell: bool = False,
    prior_changes: Sequence[FileChanges] = (),
) -> Handoff:
    scenes = [scene for scene in load() if scene.condition == "no_ocarina" or skip_saria_farewell]
    root = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(root)

    def read(path: str) -> bytes:
        data = dictionaries.decompress(path, (root / path).read_bytes())
        for changes in prior_changes:
            if path in changes:
                data = changes[path](data)
        return data

    names = {keys.POUCH, *(scene.flow for scene in scenes)}
    names.update(ref.split("/")[0] for scene in scenes for ref in (*scene.grants, *scene.before, *scene.after))
    originals = {name: evfl.read(read(keys.flow_path(name))) for name in sorted(names)}
    if any(
        isinstance(event, evfl.SubFlowEvent) and event.flowchart == "Common_Camera_Pln"
        for document in originals.values()
        for event in document.flowchart.events
    ):
        originals["Common_Camera_Pln"] = evfl.read(read(keys.flow_path("Common_Camera_Pln")))
    documents = copy.deepcopy(originals)
    _usable(documents[keys.POUCH].flowchart)
    plain = evfl.Flowchart(FLOW)
    for scene in scenes:
        chart = documents[scene.flow].flowchart
        if chart is None:
            raise PatchError(f"scene handoff: no caller flowchart {scene.flow}")
        if scene.request:
            if chart.entry_point(scene.entry).main_event != _index(chart, scene.cut):
                raise PatchError(f"scene handoff: direct admission changed: {scene}")
            _plain_entry(plain, scene, originals)
            _admission(plain, scene, chart)
            continue
        entry = chart.entry_point(scene.entry)
        cut = _index(chart, scene.cut)
        seen = reachable(chart, entry.main_event)
        if cut not in seen:
            raise PatchError(f"scene handoff: {scene.flow}:{scene.entry}: cut is outside its caller: {scene.cut}")
        resume = evfl.NONE if not scene.resume else _index(chart, scene.resume)
        system, transition = keys._operation(chart, "EventSystemActor", "actions", "EventTransition")
        call = len(chart.events)
        chart.events.append(
            evfl.ActionEvent(
                PREFIX + scene.name + "Handoff",
                system,
                transition,
                resume,
                {
                    "EventName": _event_name(scene),
                    "IsWaitEnd": True,
                    "SpecialEventActionType": 1,
                    "FadeInTypeEventEnd": 0,
                },
            )
        )
        prefix = call
        for name in reversed(scene.caller_before):
            effect = copy.deepcopy(chart.events[_index(chart, name)])
            if not isinstance(effect, evfl.ActionEvent) or (
                chart.actors[effect.actor].name,
                chart.actors[effect.actor].actions[effect.action],
            ) not in {
                ("EventRequestActor", "EventTriggerSetEventBool"),
                ("GameDataActor", "EventTriggerSetGameDataBool"),
            }:
                raise PatchError(f"scene handoff: unaudited caller-bound effect: {scene.flow}/{name}: {effect}")
            effect.name = PREFIX + scene.name + "Before" + name
            effect.next = prefix
            prefix = len(chart.events)
            chart.events.append(effect)
        if scene.condition == "no_ocarina":
            guard = len(chart.events)
            chart.events.append(
                evfl.SubFlowSwitchEvent(PREFIX + scene.name + "Usable", keys.POUCH, USABLE, [(0, cut), (1, prefix)])
            )
            replacement = guard
        else:
            replacement = prefix
        # The Ice Cavern's chest must finish before dispatching its separate
        # song check. Only a serial cut is admitted; never launch a get in a fork.
        if entry.main_event == cut:
            entry.main_event = replacement
        else:
            incoming = [i for i in sorted(seen) if getattr(chart.events[i], "next", evfl.NONE) == cut]
            if not incoming or any(
                cut in [target for _, target in getattr(chart.events[i], "cases", ())]
                or isinstance(chart.events[i], evfl.ForkEvent)
                and cut in [chart.events[i].join, *chart.events[i].forks]
                for i in seen
            ):
                raise PatchError(f"scene handoff: cut is not a serial caller boundary: {scene}")
            for index in incoming:
                chart.events[index].next = replacement
        if scene.condition == "no_ocarina":
            for native_entry in chart.entry_points:
                if replacement in reachable(chart, native_entry.main_event):
                    native_entry.sub_flow_events.append(replacement)
        _plain_entry(plain, scene, originals)
    changes = {
        keys.flow_path(name): _flow_transform(originals[name], documents[name])
        for name in sorted(documents)
        if documents[name] != originals[name]
    }
    # Keep preload/child-event declarations consistent with each rewritten caller.
    settings = byml.load(read(keys.SETTINGS))
    analyzed = byml.load(read(keys.ANALYZED))
    changed_settings, changed_analyzed = copy.deepcopy(settings), copy.deepcopy(analyzed)
    donor = next(row for row in settings.root if row["__RowId"] == DONOR)
    analysis_donor = next(row for row in analyzed.root if row["__RowId"] == DONOR)
    by_analysis = {row["__RowId"]: row for row in changed_analyzed.root}
    for scene in scenes:
        event = _event_name(scene)
        if any(row["__RowId"] == event for row in changed_settings.root):
            raise PatchError(f"scene handoff: event already registered: {event}")
        row = copy.deepcopy(donor)
        row.update(__RowId=event, FlowchartFileName=f"Work/Event/EventFlow/{FLOW}.evfc", EntryPointName=scene.name)
        changed_settings.root.append(row)
        row = copy.deepcopy(analysis_donor)
        row.pop("ChildEventList", None)
        calls = _entry_reachable(plain, scene.name)
        subflows = sorted(
            {
                plain.events[i].flowchart
                for i in calls
                if isinstance(plain.events[i], evfl.SubFlowEvent | evfl.SubFlowSwitchEvent)
                and plain.events[i].flowchart
            }
        )
        row.update(__RowId=event, SubFlowList=subflows)
        changed_analyzed.root.append(row)
        if scene.request:
            source_row = next(row for row in changed_settings.root if row["__RowId"] == scene.request)
            native_row = copy.deepcopy(source_row)
            native_row["__RowId"] = PREFIX + "Native_" + scene.name
            changed_settings.root.append(native_row)
            native_analysis = copy.deepcopy(by_analysis[scene.request])
            native_analysis["__RowId"] = native_row["__RowId"]
            changed_analyzed.root.append(native_analysis)
            source_row.clear()
            source_row.update(copy.deepcopy(donor))
            source_row.update(
                __RowId=scene.request,
                FlowchartFileName=f"Work/Event/EventFlow/{FLOW}.evfc",
                EntryPointName=scene.name + "Admission",
            )
            source_analysis = by_analysis[scene.request]
            source_analysis.clear()
            source_analysis.update(copy.deepcopy(analysis_donor))
            source_analysis.update(
                __RowId=scene.request,
                SubFlowList=[keys.POUCH],
                ChildEventList=[event, native_row["__RowId"]],
            )
            continue
        for caller in changed_settings.root:
            if Path(caller.get("FlowchartFileName", "")).stem != scene.flow:
                continue
            entry_name = caller.get("EntryPointName") or "EntryPoint0"
            chart = documents[scene.flow].flowchart
            try:
                entry = chart.entry_point(entry_name)
            except KeyError as error:
                raise PatchError(f"scene handoff: caller registry has no entry: {caller}") from error
            added = _index(chart, PREFIX + scene.name + "Handoff")
            if added not in _entry_reachable(chart, entry.name):
                continue
            analysis = by_analysis[caller["__RowId"]]
            analysis["ChildEventList"] = sorted(set(analysis.get("ChildEventList", ())) | {event})
            if scene.condition == "no_ocarina":
                analysis["SubFlowList"] = sorted(set(analysis.get("SubFlowList", ())) | {keys.POUCH})
    for table in (changed_settings, changed_analyzed):
        table.root.sort(key=lambda row: row["__RowId"])
    changes[keys.SETTINGS] = _table_transform(settings, changed_settings)
    changes[keys.ANALYZED] = _table_transform(analyzed, changed_analyzed)
    return Handoff(changes, {FLOW_PATH: NewFile(_encode(evfl.EventFlowFile(FLOW, flowchart=plain)))})
