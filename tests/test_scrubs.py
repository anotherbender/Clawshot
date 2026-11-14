import copy
from itertools import product

import pytest

from clawshot.formats import evfl
from clawshot.patch import scrubs
from clawshot.patch.plan import PatchError


def fixture():
    events = []
    for sale in scrubs.SALES.values():
        for name, old in sale.grants:
            events.append(
                evfl.SubFlowEvent(
                    name, "", "SimpleShopSub_Scrub_Business_OneTime", params={"ActorName": old, "Price": sale.price}
                )
            )
        if sale.selection:
            events.append(
                evfl.ActionEvent(
                    sale.selection, 0, 0, params={"GameDataName": "Shop_SelectItemName", "Value": "Obj_Heart_Piece"}
                )
            )
    events.append(evfl.ActionEvent("Once", 0, 1, params={"GameDataName": "Saved", "Value": True}))
    start = len(events)
    for name in ("Event192", "Event334"):
        events.append(
            evfl.SubFlowEvent(
                name,
                "",
                "Unopened_Check",
                start + 2,
                {
                    "GameData_Item": "Scrub_Business_TempItemName_02",
                    "GameDate_Unopend": "Enemy_Scrub_Business_Unopened03",
                },
            )
        )
    events.extend(
        [
            evfl.ActionEvent("Event119", 2, 0, params={"IsDisplayHeartGauge": True}),
            evfl.ActionEvent(
                "Event395",
                1,
                0,
                start + 4,
                {
                    "IsWaitEnd": True,
                    "IsCloseDialog": True,
                    "ChoiceNumber": 0,
                    "MessageId": "EventFlowMsg/Enemy_Event:Enemy_Scrub_Business_Common_018",
                },
            ),
            evfl.ActionEvent("Event140", 1, 1),
        ]
    )
    return evfl.Flowchart(
        scrubs.FLOW,
        [
            evfl.Actor(
                "GameDataActor",
                actions=["EventTriggerSetGameDataString64", "EventTriggerSetGameDataBool"],
                queries=["EventQueryIsGameDataBool", "EventQueryIsGameDataString64"],
            ),
            evfl.Actor("Enemy_Scrub_Business", actions=["EventTalk", "EventScrubBusinessOnIsFinishDoEvent"]),
            evfl.Actor("UISystemActor", actions=["EventTriggerSetDisplayHeartGauge"]),
        ],
        events,
        [],
    )


def guard_destination(fc, incoming, offers):
    state = {}
    for slot, (actor, hidden) in enumerate(offers):
        state[f"Scrub_Business_TempItemName_{slot:02}"] = actor
        state[f"Enemy_Scrub_Business_Unopened{slot + 1:02}"] = hidden
    index = next(e for e in fc.events if e.name == incoming).next
    while isinstance(event := fc.events[index], evfl.SwitchEvent):
        params = event.params
        value = state[params["GameDataName"]]
        query = fc.actors[event.actor].queries[event.query]
        answer = value == params["Value"] if query == "EventQueryIsGameDataString64" else value
        index = dict(event.cases)[0 if answer else 1]
    return event.name


def restore_offer_guard(fc):
    """Undo only the added guard, retaining every original native event for inverse comparison."""
    target = next(i for i, e in enumerate(fc.events) if e.name == "Event119")
    added = [e for e in fc.events if e.name.startswith("ClawshotScrubOffer")]
    assert len(added) == 6
    first = fc.events.index(added[0])
    assert fc.events[first:] == added
    for name in ("Event192", "Event334"):
        event = next(e for e in fc.events if e.name == name)
        assert event.next == first
        event.next = target
    del fc.events[first:]


@pytest.mark.parametrize("offers", tuple(product((("", False), ("Item_Test", True), ("Item_Test", False)), repeat=3)))
@pytest.mark.parametrize("incoming", ["Event192", "Event334"])
def test_no_offers_exit_before_shop_ui_but_any_visible_offer_keeps_native_purchase_path(offers, incoming):
    fc = fixture()
    scrubs.patch_flowchart(fc, {})
    fc = evfl.read(evfl.write(evfl.EventFlowFile(fc.name, flowchart=fc))).flowchart
    expected = "Event119" if any(actor and not hidden for actor, hidden in offers) else "Event395"
    assert guard_destination(fc, incoming, offers) == expected


def test_all_tiers_and_shared_copies_receive_one_reward_without_changing_gates():
    before = fixture()
    file = evfl.EventFlowFile(scrubs.FLOW, flowchart=copy.deepcopy(before))
    placements = dict(zip(scrubs.SALES, ("Item_A", "Item_B", "Item_C", "Item_D"), strict=True))
    after = evfl.read(scrubs.changes(placements)[scrubs.PATH](evfl.write(file))).flowchart
    index = {e.name: e for e in after.events}
    for check, sale in scrubs.SALES.items():
        for name, old in sale.grants:
            assert index[name].params["ActorName"] == placements[check]
            index[name].params["ActorName"] = old
        if sale.selection:
            assert index[sale.selection].params["Value"] == placements[check]
            index[sale.selection].params["Value"] = "Obj_Heart_Piece"
    restore_offer_guard(after)
    assert after == before


@pytest.mark.parametrize("broken", ["grant", "price", "selection", "missing"])
def test_stale_contract_fails_before_mutation(broken):
    fc = fixture()
    if broken == "missing":
        fc.events.pop(1)
    elif broken == "selection":
        fc.events[1].params["Value"] = "Item_Wrong"
    else:
        fc.events[0].params["ActorName" if broken == "grant" else "Price"] = "Wrong"
    before = copy.deepcopy(fc)
    with pytest.raises(PatchError):
        scrubs.patch_flowchart(fc, {"HF Deku Scrub Grotto": "Item_New"})
    assert fc == before


def test_repeat_vendor_is_not_a_once_check():
    with pytest.raises(PatchError):
        scrubs.changes({"LW Deku Scrub Near Deku Theater Left": "Item_New"})


@pytest.mark.parametrize("broken", ["incoming", "target", "goodbye", "finish", "query"])
def test_stale_empty_offer_path_refuses_before_changing_rewards(broken):
    fc = fixture()
    index = {event.name: event for event in fc.events}
    if broken == "incoming":
        index["Event192"].next = evfl.NONE
    elif broken == "target":
        index["Event119"].params["IsDisplayHeartGauge"] = False
    elif broken == "goodbye":
        index["Event395"].params["IsCloseDialog"] = False
    elif broken == "finish":
        index["Event395"].next = evfl.NONE
    else:
        fc.actors[0].queries.remove("EventQueryIsGameDataBool")
    before = copy.deepcopy(fc)
    with pytest.raises(PatchError):
        scrubs.patch_flowchart(fc, {"HF Deku Scrub Grotto": "Item_New"})
    assert fc == before
