"""Silent grant and native window must agree; synthetic scene data only."""

from dataclasses import replace

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.patch import gifts, items

FLOW = "Dm_Test"
PATH = "test.bfevfl"
STEP = Gift(f"{FLOW}/Grant", "event_gift", FLOW, PATH, ("Start",), "Grant", "direct", "Actor", "Item_Old", "")


def scene():
    return evfl.EventFlowFile(
        FLOW,
        flowchart=evfl.Flowchart(
            FLOW,
            [evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"])],
            [
                evfl.ActionEvent("Grant", 0, 0, 1, {"Actor": "Item_Old", "Num": 1, "IsGetEvent": False}),
                evfl.SubFlowEvent(
                    "Window", "GetPouchContent", "DisplayGetByActorName", params={"ActorName": "Item_Old"}
                ),
            ],
            [evfl.EntryPoint("Start", 0, [1])],
        ),
    )


def rule():
    return gifts.loads(f'[check.Prize]\nclass = "swap"\ndisplay = ["{FLOW}/Window"]')["Prize"]


def test_swap_pairs_silent_grant_and_window_without_changing_the_scene():
    file = scene()
    expected = scene()
    expected.flowchart.events[0].params["Actor"] = "Item_New"
    expected.flowchart.events[1].params["ActorName"] = "Item_New"
    data = evfl.write(file)
    patched = gifts.flow_transform(FLOW, [gifts.GiftChange(rule(), (STEP,), "Item_New")])(data)
    assert evfl.read(patched) == expected


def test_vanilla_assignment_writes_no_flow_and_keeps_native_bytes():
    definitions = [Definition(STEP.id, "event_gift", "", "prize", "Item_Old", "Prize")]
    actors = items.loads('[items]\nOld = {actor="Item_Old"}\nNew = {actor="Item_New"}\n')
    step = gifts.seed_step(["Prize"], [STEP], definitions, {"Prize": rule()}, actors, {"Prize": "Old"}, {FLOW: PATH})
    assert step({"Prize": "Old"}) == {}
    data = evfl.write(scene())
    same_item = gifts.flow_transform(FLOW, [gifts.GiftChange(rule(), (STEP,), "Item_Old")])(data)
    assert same_item == data
    result = evfl.read(step({"Prize": "New"})[PATH](data)).flowchart
    assert result.events[0].params["Actor"] == result.events[1].params["ActorName"] == "Item_New"


@pytest.mark.parametrize(
    "event",
    [
        evfl.SubFlowEvent("Window", "Other", "DisplayGetByActorName", params={"ActorName": "Item_Old"}),
        evfl.SubFlowEvent("Window", "GetPouchContent", "GetPouchContentByActorName", params={"ActorName": "Item_Old"}),
        evfl.SubFlowEvent("Window", "GetPouchContent", "DisplayGetByActorName", params={"ActorName": "Item_Other"}),
        evfl.SubFlowEvent(
            "Window", "GetPouchContent", "DisplayGetByActorName", params={"ActorName": evfl.Argument("Item_Old")}
        ),
        evfl.SubFlowEvent("Window", "GetPouchContent", "DisplayGetByActorName"),
        evfl.ActionEvent("Window", 0, 0, params={"ActorName": "Item_Old"}),
    ],
)
def test_refuses_stale_or_nonliteral_display(event):
    file = scene()
    file.flowchart.events[1] = event
    with pytest.raises(gifts.GiftPatchError, match="expected DisplayGetByActorName with literal ActorName"):
        gifts.patch_flowchart(file.flowchart, FLOW, [gifts.GiftChange(rule(), (STEP,), "Item_New")])


def test_display_in_another_flow_is_included_and_uses_the_grant_actor():
    change = gifts.GiftChange(replace(rule(), display=("WindowFlow/Window",)), (STEP,), "Item_New")
    assert gifts.flows_changed([change]) == [FLOW, "WindowFlow"]
    file = scene()
    file.flowchart.events = file.flowchart.events[1:]
    gifts.patch_flowchart(file.flowchart, "WindowFlow", [change])
    assert file.flowchart.events[0].params == {"ActorName": "Item_New"}


@pytest.mark.parametrize("value", ['"Dm_Test/Window"', "1", "[1]", '["invalid"]', '["F/E", "F/E"]'])
def test_refuses_invalid_display_rules(value):
    with pytest.raises(gifts.GiftPatchError, match="display|not '<flow>/<event>'"):
        gifts.loads(f'[check.Prize]\nclass = "swap"\ndisplay = {value}')
