"""A scene replacement must really grant once, without entering cinematic context."""

import copy
from dataclasses import replace
from types import SimpleNamespace

import pytest

from clawshot.formats import byml, evfl
from clawshot.patch import keys, ocarina
from clawshot.patch import scene_handoff as handoff
from clawshot.patch.plan import PatchError


class AnimationWait(AssertionError):
    pass


def state(*, child=False, selected="", fairy=0, time=0):
    return {
        "Sequence_IsChildhood": child,
        ocarina.EQUIPPED: selected,
        "stock": {ocarina.FAIRY: fairy, ocarina.TIME: time},
        "IsGet." + ocarina.TIME: True,  # history is deliberately unrelated to selection/stock
    }


def run(charts, rows, flow, entry, current, *, stop_native=False, data_only=False):
    trace = []
    transitions = []
    budget = 2000

    def execute(flow, entry_name, arguments, contexts):
        nonlocal budget
        chart = charts[flow]
        entry = chart.entry_point(entry_name)
        index = entry.main_event
        while index != evfl.NONE:
            budget -= 1
            assert budget > 0, (flow, entry_name, index, trace)
            event = chart.events[index]
            params = {
                key: arguments[str(value)] if isinstance(value, evfl.Argument) else value
                for key, value in (getattr(event, "params", None) or {}).items()
            }
            trace.append((flow, event.name))
            if isinstance(event, evfl.ReturnEvent):
                return event.value
            if isinstance(event, evfl.SubFlowEvent | evfl.SubFlowSwitchEvent):
                assert index in entry.sub_flow_events, (flow, entry_name, event)
                target = event.flowchart or flow
                if (
                    data_only
                    and target == keys.POUCH
                    and event.entry_point in {"OpenGetWindow", "OpenRupeeUIIfNeed", "CloseRupeeUIIfNeed"}
                ):
                    # Execute native grant/data nodes; rendering/message windows are not an engine simulation.
                    index = event.next
                    continue
                result = execute(target, event.entry_point, arguments | params, contexts)
                index = (
                    dict(event.cases).get(result, evfl.NONE)
                    if isinstance(event, evfl.SubFlowSwitchEvent)
                    else event.next
                )
                continue
            actor = chart.actors[event.actor]
            if isinstance(event, evfl.SwitchEvent):
                operation = actor.queries[event.query]
                if operation == "EventQueryIsGameDataBool":
                    answer = bool(current.get(params["GameDataName"], False))
                elif operation == "EventQueryHavePlayedEvent":
                    answer = bool(current.get("HavePlayedEvent." + params["EventName"], False))
                elif operation == "EventQueryIsGameDataString64":
                    answer = current.get(params["GameDataName"], "") == params["Value"]
                elif operation == "EventQueryIsGameDataBoolExp":
                    answer = bool(current.get(params["GameDataName"], False))
                elif operation == "EventQueryIsGameDataInt":
                    value = current.get(params["GameDataName"], 0)
                    result = 0 if value < params["Value"] else 1 if value == params["Value"] else 2
                    index = dict(event.cases).get(result, evfl.NONE)
                    continue
                elif operation == "EventQueryPlayerIsChild":
                    answer = current["Sequence_IsChildhood"]
                elif operation == "EventQueryTimeDivision":
                    index = dict(event.cases).get(current.get("time_division", 0), evfl.NONE)
                    continue
                elif operation == "EventQueryIsAutoSavePouchContent" and data_only:
                    answer = False
                elif operation == "EventQueryIsExistInPouch":
                    answer = current["stock"].get(params["Actor"], 0) >= params["Num"]
                elif operation == "EventQueryIsHeartPiece":
                    answer = params["ActorName"] == "Obj_Heart_Piece"
                elif operation == "EventQueryIsMaxLifeUpPouchContent":
                    answer = params["ActorName"] == "Obj_Heart_Container"
                elif operation == "EventQueryIsFairy":
                    answer = params["ActorName"] == "Obj_Fairy"
                elif operation == "EventQueryIsRecoverHeartOrMpActor":
                    answer = params["ActorName"] in {"Obj_Heart", "Obj_MagicJar_Small", "Obj_MagicJar_Large"}
                else:
                    raise AssertionError((operation, params))
                index = dict(event.cases).get(0 if answer else 1, evfl.NONE)
                continue
            operation = actor.actions[event.action]
            if stop_native and actor.name == "Player_Event":
                return "native"
            if operation == "EventTransition":
                name = params["EventName"]
                row = rows[name]
                transitions.append(name)
                execute(row["flow"], row["entry"], {}, (*contexts, name))
            elif operation == "SyntheticPoseWait":
                if stop_native:
                    return "native"
                usable = any(current["stock"].get(actor, 0) > 0 for actor in (ocarina.FAIRY, ocarina.TIME))
                if not usable:
                    raise AnimationWait((contexts, trace))
            elif operation == "EventTriggerAddOrRemovePouchContent":
                content = params["Actor"]
                current["stock"][content] = current["stock"].get(content, 0) + params["Num"]
                current["IsGet." + content] = True
                current.setdefault("grants", []).append((content, params["Num"], contexts))
            elif operation == "EventTriggerRecoverByCureItem":
                assert current["stock"].get(params["ActorName"], 0) > 0, "recovery must follow the grant"
                current.setdefault("heals", []).append(params["ActorName"])
                current["life"] = current["max_life"]
            elif operation == "EventTriggerSetGameDataBool":
                current[params["GameDataName"]] = params["Value"]
            elif operation == "EventExecuteProgressChallengeStep":
                current["Step_" + params["ChallengeName"]] = params["StepName"]
            elif operation == "EventTriggerSetGameDataString64":
                current[params["GameDataName"]] = params["Value"]
            elif operation == "EventTriggerAddOrSubGameDataInt":
                name = params["GameDataName"]
                current[name] = current.get(name, 0) + params["Value"]
            elif operation == "EventTriggerSetForGetWindow":
                current["UI_MessageTargetActorName"] = params["Actor"]
            elif operation == "EventTriggerSetEventBool":
                current["requester_bool"] = params["Bool"]
            elif operation == "EventTrigger_SetTime":
                current["world_time"] = params
            elif data_only and operation in {
                "EventTriggerRequestAutoSave",
                "EventReserveBancChange",
                "EventWait",
                "EventTriggerShowChallengeProgressUI",
                "EventTriggerZeldaNotesSimpleAddNPCTalkCount",
                "EventTriggerZeldaNotesRequestSendDailyScreenShot",
            }:
                current.setdefault("effects", []).append((operation, params))
            else:
                raise AssertionError((operation, params))
            index = event.next
        return None

    execute(flow, entry, {}, ())
    return trace, transitions


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    """Invented actors/events; real EVFL and BYML serialization and full compiler."""
    scene = handoff.Scene(
        "example",
        "Synthetic location",
        "Caller",
        "Main",
        "Begin",
        "Tail",
        "no_ocarina",
        ("NativeScene/Gift",),
        ("NativeScene/Before",),
        ("NativeScene/After",),
        ("NativeScene",),
        "HavePlayedEvent.NativeScene",
    )
    game = evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"])
    pouch = evfl.Flowchart(
        keys.POUCH,
        [copy.deepcopy(game), evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"])],
        [evfl.ActionEvent("Add", 1, 0, params={"Actor": evfl.Argument("ActorName"), "Num": 1})],
        [evfl.EntryPoint("GetPouchContentByActorName", 0)],
    )
    healing = evfl.Flowchart(
        "Dm_SY_Get",
        [
            evfl.Actor(
                "PouchSystemActor",
                actions=["EventTriggerRecoverByCureItem"],
                queries=["EventQueryIsHeartPiece"],
            )
        ],
        [
            evfl.SwitchEvent("Heart", 0, 0, [(0, 1)], {"ActorName": evfl.Argument("ActorName")}),
            evfl.ActionEvent("Recover", 0, 0, params={"ActorName": evfl.Argument("ActorName")}),
        ],
        [evfl.EntryPoint("CheckHeart", 0)],
    )
    native = evfl.Flowchart(
        "NativeScene",
        [
            copy.deepcopy(game),
            evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
            evfl.Actor("Player_Event", actions=["SyntheticPoseWait"]),
            evfl.Actor("ChallengeSystemActor", actions=["EventExecuteProgressChallengeStep"]),
        ],
        [
            evfl.ActionEvent("Pose", 2, 0, 1),
            evfl.ActionEvent("Before", 0, 0, 2, {"GameDataName": "Synthetic.Before", "Value": True}),
            evfl.ActionEvent("Gift", 1, 0, 3, {"Actor": "Item_Boomerang", "Num": 1}),
            evfl.ActionEvent("After", 3, 0, params={"ChallengeName": "Synthetic", "StepName": "Complete"}),
        ],
        [evfl.EntryPoint("Main", 0)],
    )
    caller = evfl.Flowchart(
        "Caller",
        [evfl.Actor("EventSystemActor", actions=["EventTransition"]), copy.deepcopy(game)],
        [
            evfl.ActionEvent("Begin", 0, 0, 1, {"EventName": "NativeScene"}),
            evfl.ActionEvent("Tail", 1, 0, params={"GameDataName": "Synthetic.CallerTail", "Value": True}),
        ],
        [evfl.EntryPoint("Main", 0)],
    )
    original = {
        chart.name: evfl.EventFlowFile(chart.name, flowchart=chart) for chart in (pouch, native, caller, healing)
    }
    for name, document in original.items():
        path = tmp_path / keys.flow_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(evfl.write(document))
    settings = [
        {"__RowId": handoff.DONOR, "EventSettingComponentList": "SyntheticOrdinaryEvent", "ExtraResources": {}},
        {
            "__RowId": "SyntheticRequest",
            "FlowchartFileName": "Work/Event/EventFlow/Caller.evfc",
            "EntryPointName": "Main",
        },
    ]
    analyzed = [{"__RowId": handoff.DONOR}, {"__RowId": "SyntheticRequest"}]
    for relative, rows in ((keys.SETTINGS, settings), (keys.ANALYZED, analyzed)):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(byml.dump(byml.Document(rows)))
    monkeypatch.setattr(handoff, "load", lambda: (scene,))
    monkeypatch.setattr(
        handoff.zsdic.Dictionaries, "from_romfs", lambda _: SimpleNamespace(decompress=lambda p, data: data)
    )

    def build(*, changed_scene=scene):
        monkeypatch.setattr(handoff, "load", lambda: (changed_scene,))
        result = handoff.build(tmp_path, skip_saria_farewell=True)
        charts = {name: copy.deepcopy(document.flowchart) for name, document in original.items()}
        for name in charts:
            path = keys.flow_path(name)
            if path in result.changes:
                charts[name] = evfl.read(result.changes[path]((tmp_path / path).read_bytes())).flowchart
        charts[handoff.FLOW] = evfl.read(result.new_files[handoff.FLOW_PATH].data).flowchart
        rows = {
            "NativeScene": {"flow": "NativeScene", "entry": "Main"},
            handoff._event_name(scene): {"flow": handoff.FLOW, "entry": scene.name},
        }
        return result, charts, rows

    return scene, original, build


@pytest.mark.parametrize("child", [False, True])
@pytest.mark.parametrize("selected", ["", ocarina.FAIRY, ocarina.TIME, "InvalidInstrument"])
@pytest.mark.parametrize("fairy,time", [(0, 0), (1, 0), (0, 1), (1, 1)])
def test_actual_grant_or_native_lesson_follows_either_ocarina_stock(fixture, child, selected, fairy, time):
    scene, original, build = fixture
    _, charts, rows = build()
    current = state(child=child, selected=selected, fairy=fairy, time=time)
    usable = bool(fairy or time)
    if not usable:
        with pytest.raises(AnimationWait):
            run(
                {name: document.flowchart for name, document in original.items()},
                rows,
                "Caller",
                "Main",
                copy.deepcopy(current),
            )
    trace, transitions = run(charts, rows, "Caller", "Main", current)
    assert ("NativeScene" in transitions) is usable
    assert (handoff._event_name(scene) in transitions) is not usable
    assert current["IsGet.Item_Boomerang"] is True
    assert current["stock"]["Item_Boomerang"] == 1
    assert current["Synthetic.Before"] and current["Synthetic.CallerTail"]
    assert current["Step_Synthetic"] == "Complete"
    if not usable:
        assert ("NativeScene", "Pose") not in trace
        assert current["HavePlayedEvent.NativeScene"] is True
        assert all("NativeScene" not in contexts for _, _, contexts in current["grants"])
        run(charts, rows, "Caller", "Main", current)
        assert current["stock"]["Item_Boomerang"] == 1  # source completion, not item ownership, gates re-entry


def test_native_caller_events_and_other_entries_are_not_rewired(fixture):
    _, original, build = fixture
    _, charts, _ = build()
    assert charts["Caller"].events[: len(original["Caller"].flowchart.events)] == original["Caller"].flowchart.events
    assert charts["NativeScene"] == original["NativeScene"].flowchart
    assert not any(
        actor.name in {"Player_Event", "EventCamera", "PouchContentGuestPerformer"}
        for actor in charts[handoff.FLOW].actors
    )


def test_shuffled_reward_does_not_also_learn_the_vanilla_song(fixture):
    _, _, build = fixture
    _, charts, rows = build()
    current = state()
    run(charts, rows, "Caller", "Main", current)
    assert current["stock"]["Item_Boomerang"] == 1
    assert not current.get("IsGet.Item_Melody_ForestMinuet", False)


def test_changed_early_boundary_and_cinematic_retained_effect_are_refused(fixture):
    scene, _, build = fixture
    with pytest.raises(PatchError, match="expected one event MissingCut"):
        build(changed_scene=replace(scene, cut="MissingCut"))
    with pytest.raises(PatchError, match="unaudited retained effect"):
        build(changed_scene=replace(scene, before=("NativeScene/Pose",)))


@pytest.mark.parametrize("trigger", [False, True])
def test_conditional_native_write_keeps_false_pin_and_runs_before_the_grant(fixture, trigger):
    scene, documents, _ = fixture
    native = documents["NativeScene"].flowchart
    native.actors[0].queries.append("EventQueryIsGameDataBool")
    start = len(native.events)
    native.events.extend(
        [
            evfl.SwitchEvent(
                "Conditional",
                0,
                0,
                [(0, start + 1)],
                {"GameDataName": "IsGet.Item_Boomerang"},
            ),
            evfl.ActionEvent(
                "ConditionalWrite",
                0,
                0,
                params={"GameDataName": "Synthetic.Conditional", "Value": True},
            ),
        ]
    )
    native.entry_points.append(evfl.EntryPoint("Conditional", start))
    scene = replace(scene, before=(*scene.before, "NativeScene/@Conditional"))
    plain = evfl.Flowchart(handoff.FLOW)
    handoff._plain_entry(plain, scene, documents)
    plain = evfl.read(evfl.write(evfl.EventFlowFile(handoff.FLOW, flowchart=plain))).flowchart
    charts = {name: document.flowchart for name, document in documents.items()} | {handoff.FLOW: plain}
    current = state()
    current["IsGet.Item_Boomerang"] = trigger
    run(charts, {}, handoff.FLOW, scene.name, current)
    assert current["IsGet.Item_Boomerang"] is True
    assert current["stock"]["Item_Boomerang"] == 1
    assert current.get("Synthetic.Conditional", False) is trigger


@pytest.mark.parametrize("usable", [False, True])
def test_direct_scene_admission_preserves_original_history_on_native_and_plain_arms(fixture, usable):
    scene, documents, _ = fixture
    scene = replace(scene, flow="NativeScene", entry="Main", cut="Pose", resume="", request="NativeScene")
    source = documents["NativeScene"].flowchart
    source.actors.append(evfl.Actor("EventSystemActor", actions=["EventTransition"]))
    handoff._usable(documents[keys.POUCH].flowchart)
    plain = evfl.Flowchart(handoff.FLOW)
    handoff._plain_entry(plain, scene, documents)
    handoff._admission(plain, scene, source)
    charts = {name: document.flowchart for name, document in documents.items()} | {handoff.FLOW: plain}
    rows = {
        handoff.PREFIX + "Native_" + scene.name: {"flow": "NativeScene", "entry": "Main"},
        handoff._event_name(scene): {"flow": handoff.FLOW, "entry": scene.name},
    }
    current = state(selected=ocarina.TIME if usable else "", time=int(usable))
    _, transitions = run(charts, rows, handoff.FLOW, scene.name + "Admission", current)
    expected = handoff.PREFIX + "Native_" + scene.name if usable else handoff._event_name(scene)
    assert transitions == [expected]
    assert current["stock"]["Item_Boomerang"] == 1
    # The native row is requested under a different name. Its automatic history
    # cannot retire the original requester; explicit completion must do that.
    assert current["HavePlayedEvent.NativeScene"] is True


def test_skipped_scene_heals_a_heart_reward_after_one_grant_and_never_again(fixture):
    scene, documents, _ = fixture
    source = documents["NativeScene"].flowchart
    source.events[2].params["Actor"] = "Obj_Heart_Piece"
    plain = evfl.Flowchart(handoff.FLOW)
    handoff._plain_entry(plain, scene, documents)
    charts = {name: document.flowchart for name, document in documents.items()} | {handoff.FLOW: plain}
    current = state()
    current.update(life=4, max_life=12)
    run(charts, {}, handoff.FLOW, scene.name, current)
    assert current["stock"]["Obj_Heart_Piece"] == 1
    assert current["life"] == 12
    assert current["heals"] == ["Obj_Heart_Piece"]
    run(charts, {}, handoff.FLOW, scene.name, current)
    assert current["stock"]["Obj_Heart_Piece"] == 1
    assert current["heals"] == ["Obj_Heart_Piece"]
