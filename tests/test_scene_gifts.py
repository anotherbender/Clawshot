"""Invented split grants: preserve order, register recovery, correct post-add captions."""

import pytest

from clawshot.formats import byml, evfl
from clawshot.patch import items
from clawshot.patch import scene_gifts as scenes
from clawshot.patch.plan import PatchError


def story(check, item="Obj_Heart_Piece"):
    flow, _, grant, display, anchor = scenes.SOURCES[check]
    events = [
        evfl.ActionEvent(grant, 0, 0, params={"Actor": item, "Num": 1, "IsGetEvent": False}),
        evfl.SubFlowEvent(display, scenes.POUCH, "DisplayGetByActorName", params={"ActorName": item}),
        evfl.ActionEvent("Event242", 1, 0),
    ]
    events[1].next = 2 if check == scenes.MOAT else 0
    return evfl.EventFlowFile(
        flow,
        flowchart=evfl.Flowchart(
            flow,
            [
                evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
                evfl.Actor("EventSystemActor", actions=["EventWait"]),
            ],
            events,
            [evfl.EntryPoint("Cut", 1, [1])],
        ),
    )


def patch_story(file, check):
    flow, _, grant, display, anchor = scenes.SOURCES[check]
    return scenes._scene(evfl.write(file), flow=flow, grant=grant, display=display, anchor=anchor)


@pytest.mark.parametrize("check", [scenes.MOAT, scenes.SARIA])
def test_healing_follows_the_given_item_once_and_keeps_the_native_continuation(check):
    before = story(check)
    fc = evfl.read(patch_story(before, check)).flowchart
    _, _, _, _, anchor = scenes.SOURCES[check]
    old = next(event for event in before.flowchart.events if event.name == anchor)
    source = next(event for event in fc.events if event.name == anchor)
    heal = fc.events[source.next]
    assert (heal.flowchart, heal.entry_point, heal.params) == (
        "Dm_SY_Get",
        "CheckHeart",
        {"ActorName": "Obj_Heart_Piece"},
    )
    assert heal.next == old.next
    assert source.next in fc.entry_point("Cut").sub_flow_events
    assert fc.events[0].params == before.flowchart.events[0].params
    assert sum(isinstance(event, evfl.ActionEvent) and event.actor == 0 for event in fc.events) == 1
    window = fc.events[1]
    assert window.entry_point == (scenes.DISPLAY if check == scenes.MOAT else "DisplayGetByActorName")
    with pytest.raises(PatchError, match="already patched"):
        patch_story(evfl.EventFlowFile(fc.name, flowchart=fc), check)


@pytest.mark.parametrize("fault", ["item", "normal_get", "continuation", "display"])
def test_changed_scene_source_is_refused(fault):
    file = story(scenes.MOAT)
    if fault == "item":
        file.flowchart.events[0].params["Actor"] = "Other"
    elif fault == "normal_get":
        file.flowchart.events[0].params["IsGetEvent"] = True
    elif fault == "continuation":
        file.flowchart.events[1].next = evfl.NONE
    else:
        file.flowchart.events[1].entry_point = "GetPouchContentByActorName"
    with pytest.raises(PatchError, match="changed"):
        patch_story(file, scenes.MOAT)


def pouch():
    return evfl.EventFlowFile(
        scenes.POUCH,
        flowchart=evfl.Flowchart(
            scenes.POUCH,
            [
                evfl.Actor(
                    "PouchSystemActor",
                    actions=["EventTriggerSetForGetWindow", "EventTriggerSetHavePlayedGetEvent"],
                    queries=["EventQueryHeartPieceNum"],
                ),
                evfl.Actor("SystemTextNPC", actions=["EventTalk"]),
                evfl.Actor("GameSystemActor", actions=["EventCloseMessageDialog"]),
            ],
            [
                evfl.SwitchEvent("Event56", 0, 0, [(count, count + 2) for count in range(4)]),
                evfl.ActionEvent("Event15", 0, 0, 6, {"Actor": evfl.Argument("ActorName")}),
                *[
                    evfl.ActionEvent(f"Caption{count}", 1, 0, params={"MessageId": f"Piece{count}"})
                    for count in range(1, 5)
                ],
                evfl.SubFlowEvent("Event14", "", "OpenGetWindow"),
                evfl.ActionEvent("Close", 2, 0, 8),
                evfl.SubFlowEvent("Event114", "", "OpenGetWindow_HeartPiece", 9),
                evfl.ActionEvent("MarkShown", 0, 1),
            ],
            [
                evfl.EntryPoint("OpenGetWindow_HeartPiece", 0),
                evfl.EntryPoint("OpenGetWindow", 7, [8]),
                evfl.EntryPoint("DisplayGetByActorName", 1, [6]),
            ],
        ),
    )


@pytest.mark.parametrize("after,caption", [(0, "Piece4"), (1, "Piece1"), (2, "Piece2"), (3, "Piece3")])
def test_post_add_caption_uses_the_piece_received_not_the_next_piece(after, caption):
    before = pouch()
    fc = evfl.read(scenes._post_add_piece_display(evfl.write(before))).flowchart
    assert fc.events[: len(before.flowchart.events)] == before.flowchart.events
    assert fc.entry_points[0] == before.flowchart.entry_points[0]
    setup = fc.events[fc.entry_point(scenes.DISPLAY).main_event]
    assert setup.params == {"Actor": evfl.Argument("ActorName")}
    open_window = fc.events[setup.next]
    window_entry = fc.entry_point(open_window.entry_point)
    close = fc.events[window_entry.main_event]
    assert fc.actors[close.actor].actions[close.action] == "EventCloseMessageDialog"
    piece_call = fc.events[close.next]
    assert fc.events[piece_call.next].name.endswith("MarkShown")
    query = fc.events[fc.entry_point(piece_call.entry_point).main_event]
    assert fc.events[dict(query.cases)[after]].params["MessageId"] == caption


def test_declarations_add_only_the_selected_scene_dependency():
    original = [
        {"__RowId": "Other", "SubFlowList": ["Original"]},
        {"__RowId": "Dm_MelodyGet_Time", "SubFlowList": ["GetPouchContent"]},
    ]
    result = byml.read(scenes._register(byml.write(original), flows=("Dm_MelodyGet_Time",)))
    assert result[0] == original[0]
    assert result[1]["SubFlowList"] == ["Dm_SY_Get", "GetPouchContent"]


def test_vanilla_grants_do_not_add_heals_or_change_native_displays():
    actors = items.loads('[items]\n"Piece of Heart"={actor="Obj_Heart_Piece"}\n')
    assert scenes.changes({}, actors) == {}
    assert scenes.changes({scenes.MOAT: "Ocarina of Time", scenes.SARIA: "Fairy Ocarina"}, actors) == {}


def test_projected_native_tunic_can_generate_at_a_split_scene():
    actors = items.loads('[items]\n"Goron Tunic"={actor="Shop_Armor_Goron"}\n')
    file = story(scenes.SARIA, item="Obj_Armor_Goron")
    transform = scenes.changes({scenes.SARIA: "Goron Tunic"}, actors)[scenes.path(scenes.SOURCES[scenes.SARIA][0])]
    after = evfl.read(transform(evfl.write(file))).flowchart
    assert after.events[0].params["Actor"] == after.events[1].params["ActorName"] == "Obj_Armor_Goron"
    heal = next(event for event in after.events if event.name == scenes.HEAL)
    assert heal.params == {"ActorName": "Obj_Armor_Goron"}
