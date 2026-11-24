"""T1-a (plan 17): an ocarina from a world pickup is playable at once. A world pickup grants in ``Dm_SY_Get`` with
``PouchContentGuestPerformer.EventTriggerAddOwnToPouch``, which never created the instrument's equipment actor; the
native moat Ocarina of Time is followed by a movie that adds ``Item_Ocarina_Time`` again by name. The receipt patch
does the same right after the pickup's own add. Synthetic flowcharts built in code (hard rule 1)."""

import copy

import pytest

from clawshot.formats import evfl
from clawshot.patch import ocarina, ocarina_pickup
from clawshot.patch.plan import PatchError

FAIRY, TIME = ocarina_pickup.FAIRY, ocarina_pickup.TIME
TARGET = "UI_MessageTargetActorName"


def flow() -> evfl.Flowchart:
    actors = [
        evfl.Actor(
            "PouchContentGuestPerformer", actions=["EventTriggerSetOwnNameToMessage", "EventTriggerAddOwnToPouch"]
        ),
        evfl.Actor("UISystemActor", actions=["EventTriggerRequestOpenPickUpWindow"]),
        evfl.Actor("PouchSystemActor", actions=["EventTriggerRecoverByCureItem"], queries=["EventQueryIsFairy"]),
        evfl.Actor("GameDataActor", queries=["EventQueryIsGameDataInt"]),
    ]
    return evfl.Flowchart(
        ocarina_pickup.RECEIPT_FLOW,
        actors=actors,
        events=[
            evfl.ActionEvent("Name", 0, 0, 1),
            evfl.ActionEvent("AddOwn", 0, 1, 2),
            evfl.ActionEvent("Window", 1, 0, evfl.NONE, {"ActorName": evfl.Argument("ActorName")}),
        ],
        entry_points=[evfl.EntryPoint("PouchAddItem", 0)],
    )


def run(chart: evfl.Flowchart, own: str) -> list:
    """Walk from the entry: the pickup's own add sets the message target to its ActorName (``own``)."""
    state, trace, at = {}, [], 0
    for _ in range(50):
        if at == evfl.NONE:
            return trace
        event = chart.events[at]
        actor = chart.actors[event.actor]
        if isinstance(event, evfl.SwitchEvent):
            query = actor.queries[event.query]
            assert query == "EventQueryIsGameDataString64"
            answer = state.get(event.params["GameDataName"]) == event.params["Value"]
            at = dict(event.cases)[0 if answer else 1]
            continue
        action = actor.actions[event.action]
        if action == "EventTriggerSetOwnNameToMessage":
            state[TARGET] = own
        trace.append((action, copy.deepcopy(event.params)))
        at = event.next
    raise AssertionError(trace)


@pytest.mark.parametrize("own", [FAIRY, TIME])
def test_an_ocarina_pickup_is_added_again_by_name_after_its_own_add(own):
    chart = flow()
    ocarina_pickup.patch_receipt(chart)
    trace = run(chart, own)
    actions = [action for action, _ in trace]
    assert actions == [
        "EventTriggerSetOwnNameToMessage",
        "EventTriggerAddOwnToPouch",
        "EventTriggerAddOrRemovePouchContent",
        "EventTriggerRequestOpenPickUpWindow",
    ]
    assert trace[2][1] == {
        "Actor": own,
        "Num": 1,
        "IsEquipDIrect": False,
        "IsSetMessageTargetActorName": True,
        "IsGetEvent": False,
    }


@pytest.mark.parametrize("own", ["Item_Heart_Piece", "Item_Melody_ZeldaLullaby", "Item_Boomerang"])
def test_other_pickups_run_as_before(own):
    chart = flow()
    ocarina_pickup.patch_receipt(chart)
    assert run(chart, own) == run(flow(), own)


def test_the_fairy_add_gets_the_keep_time_helper_and_the_flow_reads_back():
    """``ocarina.changes`` patches every literal Fairy add of a flow a prior step changed; this one is such an add."""
    chart = flow()
    ocarina_pickup.patch_receipt(chart)
    assert [chart.events[i].name for i in ocarina._targets(chart)] == [ocarina_pickup.RECEIPT_PREFIX + FAIRY]
    document = evfl.EventFlowFile(chart.name, flowchart=chart)
    assert evfl.read(evfl.write(document)) == document


def test_a_flow_without_one_own_add_or_already_patched_is_refused():
    chart = flow()
    chart.events[1] = evfl.ActionEvent("AddOwn", 0, 0, 2)
    with pytest.raises(PatchError, match="AddOwnToPouch"):
        ocarina_pickup.patch_receipt(chart)
    chart = flow()
    ocarina_pickup.patch_receipt(chart)
    with pytest.raises(PatchError, match="already"):
        ocarina_pickup.patch_receipt(chart)


def test_receipt_changes_patch_the_dump_flow(tmp_path, zsdic_pack):
    from test_songs import write_romfs

    from clawshot.patch import keys

    path = keys.flow_path(ocarina_pickup.RECEIPT_FLOW)
    write_romfs(tmp_path, zsdic_pack, {path: evfl.write(evfl.EventFlowFile(flow().name, flowchart=flow()))})
    changes = ocarina_pickup.receipt_changes(tmp_path)
    assert list(changes) == [path]
    data = evfl.write(evfl.EventFlowFile(flow().name, flowchart=flow()))
    patched = evfl.read(changes[path](data)).flowchart
    assert run(patched, FAIRY)[2][0] == "EventTriggerAddOrRemovePouchContent"
    with pytest.raises(PatchError, match="changed"):
        changes[path](evfl.write(evfl.EventFlowFile("Other", flowchart=evfl.Flowchart("Other"))))
