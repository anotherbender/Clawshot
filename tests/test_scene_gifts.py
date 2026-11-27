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
    events[0].next = 1 if check == scenes.MOAT else evfl.NONE
    events[1].next = 2 if check == scenes.MOAT else 0
    return evfl.EventFlowFile(
        flow,
        flowchart=evfl.Flowchart(
            flow,
            [
                evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
                evfl.Actor("EventSystemActor", actions=["EventWait"]),
                evfl.Actor("Player_Event"),
            ],
            events,
            [evfl.EntryPoint("Cut", 0 if check == scenes.MOAT else 1, [1])],
        ),
    )


def patch_story(file, check):
    flow, _, grant, display, anchor = scenes.SOURCES[check]
    return scenes._scene(evfl.write(file), flow=flow, grant=grant, display=display, anchor=anchor)


def play_story(chart):
    """Model the observed heart-processing replay; display itself never grants."""
    state = {"pieces": 0, "life": 4, "max_life": 24}
    order = []
    index = chart.entry_point("Cut").main_event
    for _ in range(20):
        if index == evfl.NONE:
            return state, order
        event = chart.events[index]
        if isinstance(event, evfl.ActionEvent):
            actor = chart.actors[event.actor]
            operation = actor.actions[event.action]
            if (actor.name, operation) == ("PouchSystemActor", "EventTriggerAddOrRemovePouchContent"):
                state["pieces"] += event.params["Num"]
                order.append("grant")
            elif (actor.name, operation) == ("Player_Event", "EventTriggerHealLifeMax"):
                state["life"] = state["max_life"]
                order.append("heal")
        elif event.flowchart == "GetPouchContent":
            order.append("window")
        elif (event.flowchart, event.entry_point) == ("Dm_SY_Get", "CheckHeart"):
            # The played already-added piece took this coupled path and became two.
            state["pieces"] += 1
            state["life"] = state["max_life"]
            order.append("heal")
        else:
            raise AssertionError(event)
        index = event.next
    raise AssertionError("story did not finish")


@pytest.mark.parametrize("check", [scenes.MOAT, scenes.SARIA])
def test_already_added_piece_is_one_piece_and_heals_fully_without_replaying_heart_processing(check):
    before = story(check)
    after = evfl.read(patch_story(before, check))
    state, order = play_story(after.flowchart)
    assert state == {"pieces": 1, "life": 24, "max_life": 24}
    assert order == (["grant", "window", "heal"] if check == scenes.MOAT else ["window", "grant", "heal"])
    assert after.flowchart.events[0].params == before.flowchart.events[0].params
    with pytest.raises(PatchError, match="already patched"):
        patch_story(after, check)


@pytest.mark.parametrize("fault", ["item", "normal_get", "continuation", "display", "player", "player_instance"])
def test_changed_scene_source_is_refused(fault):
    file = story(scenes.MOAT)
    if fault == "item":
        file.flowchart.events[0].params["Actor"] = "Other"
    elif fault == "normal_get":
        file.flowchart.events[0].params["IsGetEvent"] = True
    elif fault == "continuation":
        file.flowchart.events[1].next = evfl.NONE
    elif fault == "player":
        file.flowchart.actors[2].name = "Other"
    elif fault == "player_instance":
        file.flowchart.actors[2].secondary_name = "Other"
    else:
        file.flowchart.events[1].entry_point = "GetPouchContentByActorName"
    with pytest.raises(PatchError):
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
    actors = items.loads('[items]\n"Goron Tunic"={actor="Obj_Armor_Goron"}\n')
    file = story(scenes.SARIA, item="Obj_Armor_Goron")
    transform = scenes.changes({scenes.SARIA: "Goron Tunic"}, actors)[scenes.path(scenes.SOURCES[scenes.SARIA][0])]
    after = evfl.read(transform(evfl.write(file))).flowchart
    assert after.events[0].params["Actor"] == after.events[1].params["ActorName"] == "Obj_Armor_Goron"
    heal = next(event for event in after.events if event.name == scenes.HEAL)
    assert heal.params == {"ActorName": "Obj_Armor_Goron"}
