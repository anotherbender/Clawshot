"""A Fairy receipt keeps native inventory changes without demoting the usable Time instrument."""

import copy
from collections import Counter

import pytest

from clawshot.formats import evfl
from clawshot.patch import ocarina
from clawshot.patch.plan import PatchError

POUCH = "GetPouchContent"


def fixture(*, literal=False, amount=1, message=True):
    actors = [
        evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
        evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"]),
        evfl.Actor("GameSystemActor", actions=["EventWait"]),
        evfl.Actor("UISystemActor", actions=["EventTriggerSyncPlayerEquipmentAndPouch"]),
    ]
    chart = evfl.Flowchart(
        POUCH,
        actors=actors,
        events=[
            evfl.ActionEvent(
                "Give",
                0,
                0,
                1,
                {
                    "Actor": ocarina.FAIRY if literal else evfl.Argument("ActorName"),
                    "Num": amount,
                    "IsEquipDIrect": False,
                    "IsSetMessageTargetActorName": message,
                    "IsGetEvent": True,
                },
            ),
            evfl.ActionEvent("Once", 1, 0, 2, {"GameDataName": "CheckCollected", "Value": True, "Index": -1}),
            evfl.ActionEvent(
                "Cleanup", 1, 0, evfl.NONE, {"GameDataName": "CleanupFinished", "Value": True, "Index": -1}
            ),
        ],
        entry_points=[evfl.EntryPoint("Receipt", 0)],
    )
    return chart


def patch(chart):
    helper = copy.deepcopy(chart) if chart.name == POUCH else fixture()
    ocarina._add_helper(helper)
    if chart.name == POUCH:
        chart = helper
    ocarina.patch_grants(chart)
    if chart.name != POUCH:
        return {chart.name: chart, POUCH: helper}
    return {POUCH: chart}


def run(charts, chart, state, *, content=ocarina.FAIRY, start=0, stop=None, buffered=True):
    """Native add model: own the item and select a newly received ocarina, independently of direct-equip.

    Explicit GameData writes can be frame-buffered. Native add/message-target state
    is established by the grant; the helper's wait must commit before live sync.
    """
    pending, stack, trace = {}, [], []
    here, at = chart, start
    env = {"ActorName": content, "IsGetInEvent": True}
    for _ in range(300):
        if not stack and at == stop:
            return trace
        if at == evfl.NONE:
            if not stack:
                state["strings"].update(pending)
                return trace
            here, at, env = stack.pop()
            continue
        event = here.events[at]
        if isinstance(event, evfl.SubFlowEvent):
            stack.append((here, event.next, env))
            target = charts[event.flowchart or here.name]
            values = {
                key: env[str(value)] if isinstance(value, evfl.Argument) else value
                for key, value in (event.params or {}).items()
            }
            env = {**env, **values}
            here, at = target, target.entry_point(event.entry_point).main_event
            continue
        params = {
            key: env[str(value)] if isinstance(value, evfl.Argument) else value
            for key, value in (event.params or {}).items()
        }
        actor = here.actors[event.actor]
        if isinstance(event, evfl.SwitchEvent):
            query = actor.queries[event.query]
            if query == "EventQueryIsExistInPouch":
                answer = state["stock"][params["Actor"]] >= params["Num"]
            else:
                assert query == "EventQueryIsGameDataString64", (here.name, event)
                answer = state["strings"].get(params["GameDataName"], "") == params["Value"]
            at = dict(event.cases)[0 if answer else 1]
            continue
        assert isinstance(event, evfl.ActionEvent), event
        action = actor.actions[event.action]
        if action == "EventTriggerAddOrRemovePouchContent":
            trace.append(("add", copy.deepcopy(params)))
            item, quantity = params["Actor"], params["Num"]
            state["stock"][item] += quantity
            if quantity > 0:
                state["flags"].add("IsGet." + item)
                if item in (ocarina.FAIRY, ocarina.TIME):
                    state["strings"][ocarina.EQUIPPED] = item
                    state["live"] = item
            if params["IsSetMessageTargetActorName"]:
                state["strings"]["UI_MessageTargetActorName"] = item
        elif action == "EventTriggerSetGameDataString64":
            (pending if buffered else state["strings"])[params["GameDataName"]] = params["Value"]
        elif action == "EventWait":
            state["strings"].update(pending)
            pending.clear()
        elif action == "EventTriggerSyncPlayerEquipmentAndPouch":
            state["live"] = state["strings"].get(ocarina.EQUIPPED, "")
            trace.append(("sync", state["live"]))
        else:
            assert action == "EventTriggerSetGameDataBool", (here.name, event)
            if params["Value"]:
                state["flags"].add(params["GameDataName"])
            else:
                state["flags"].discard(params["GameDataName"])
        at = event.next
    raise AssertionError((here.name, at, state, trace))


def state(*, time=1, historical=True, selected=ocarina.TIME):
    return {
        "stock": Counter({ocarina.TIME: time, ocarina.FAIRY: 0}),
        "flags": {"IsGet." + ocarina.TIME} if historical else set(),
        "strings": {ocarina.EQUIPPED: selected},
        "live": selected,
    }


@pytest.mark.parametrize("buffered", [False, True])
@pytest.mark.parametrize("literal", [False, True])
@pytest.mark.parametrize("selected", [ocarina.TIME, ocarina.FAIRY, ""])
def test_fairy_add_keeps_time_usable_without_changing_native_stock_flags_or_cleanup(buffered, literal, selected):
    original = fixture(literal=literal)
    charts = patch(copy.deepcopy(original))
    before, after = state(selected=selected), state(selected=selected)
    native = run({POUCH: original}, original, before, buffered=buffered)
    trace = run(charts, charts[POUCH], after, buffered=buffered)
    assert after["stock"] == before["stock"] == Counter({ocarina.TIME: 1, ocarina.FAIRY: 1})
    assert (
        after["flags"]
        == before["flags"]
        == {"IsGet." + ocarina.TIME, "IsGet." + ocarina.FAIRY, "CheckCollected", "CleanupFinished"}
    )
    assert [row for row in trace if row[0] == "add"] == native
    assert after["strings"][ocarina.EQUIPPED] == after["live"] == ocarina.TIME


@pytest.mark.parametrize("buffered", [False, True])
@pytest.mark.parametrize("historical", [False, True])
def test_historical_time_without_stock_does_not_grant_or_select_it(buffered, historical):
    charts = patch(fixture())
    current = state(time=0, historical=historical, selected="")
    trace = run(charts, charts[POUCH], current, buffered=buffered)
    assert current["stock"] == Counter({ocarina.TIME: 0, ocarina.FAIRY: 1})
    assert current["live"] == current["strings"][ocarina.EQUIPPED] == ocarina.FAIRY
    assert not any(row[0] == "sync" for row in trace)
    assert ("IsGet." + ocarina.TIME in current["flags"]) is historical


@pytest.mark.parametrize("content", [ocarina.TIME, "Item_Boomerang", "Obj_Rupee_Green"])
def test_other_rewards_do_not_repair_or_change_an_existing_fairy_selection(content):
    original = fixture()
    charts = patch(copy.deepcopy(original))
    native, current = state(selected=ocarina.FAIRY), state(selected=ocarina.FAIRY)
    before = run({POUCH: original}, original, native, content=content)
    after = run(charts, charts[POUCH], current, content=content)
    assert current == native
    assert after == before


def test_first_fairy_then_time_remains_native():
    original = fixture()
    charts = patch(copy.deepcopy(original))
    native, current = state(time=0, historical=False, selected=""), state(time=0, historical=False, selected="")
    for content in (ocarina.FAIRY, ocarina.TIME):
        before = run({POUCH: original}, original, native, content=content)
        after = run(charts, charts[POUCH], current, content=content)
        assert current == native
        assert after == before


def test_direct_movie_grant_needs_no_new_movie_actor_and_retains_source_once_write():
    source = fixture(literal=True, message=False)
    source.name = "SyntheticSaria"
    source.actors = source.actors[:2]
    charts = patch(source)
    current = state()
    run(charts, source, current)
    assert current["stock"] == Counter({ocarina.TIME: 1, ocarina.FAIRY: 1})
    assert {"CheckCollected", "CleanupFinished"} <= current["flags"]
    assert current["live"] == ocarina.TIME


@pytest.mark.parametrize("amount", [-1, 0])
def test_removal_and_zero_quantity_keep_native_behavior(amount):
    source = fixture(literal=True, amount=amount)
    before = copy.deepcopy(source)
    ocarina.patch_grants(source)
    assert source == before


def test_stale_dynamic_identity_and_double_patch_are_refused():
    with pytest.raises(PatchError, match="message identity"):
        ocarina.patch_grants(fixture(message=False))
    chart = fixture()
    ocarina.patch_grants(chart)
    with pytest.raises(PatchError, match="already"):
        ocarina.patch_grants(chart)
