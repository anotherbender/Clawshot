"""World receipts preserve native rewards and keep the highest owned ocarina on both presentation paths."""

import copy
from collections import Counter

import pytest
from test_ocarina import fixture as pouch_fixture
from test_songs import write_romfs

from clawshot.formats import evfl
from clawshot.patch import keys, ocarina, ocarina_pickup
from clawshot.patch.plan import PatchError

FAIRY, TIME = ocarina_pickup.FAIRY, ocarina_pickup.TIME
TARGET = "UI_MessageTargetActorName"
FLOW_NAMES = ("Dm_SY_Get", "Dm_SY_Get_WithoutPlayer")


def flow(name="Dm_SY_Get") -> evfl.Flowchart:
    presentation = "EventPlayAS" if name == "Dm_SY_Get_WithoutPlayer" else "EventTriggerModelBindForItemGetDemo"
    actors = [
        evfl.Actor(
            "PouchContentGuestPerformer",
            actions=[
                "EventTriggerSetOwnNameToMessage",
                "EventTriggerAddOwnToPouch",
                presentation,
                "EventGoOffstageForUser",
            ],
        ),
        evfl.Actor("UISystemActor", actions=["EventTriggerRequestOpenPickUpWindow"]),
        evfl.Actor("GameSystemActor", actions=["EventTriggerRequestAutoSave"]),
        evfl.Actor("PouchSystemActor", queries=["EventQueryIsAutoSavePouchContent"]),
    ]
    if name == "Dm_SY_Get":
        actors.append(evfl.Actor("GameDataActor", queries=["EventQueryIsGameDataInt"]))
    return evfl.Flowchart(
        name,
        actors=actors,
        events=[
            evfl.ActionEvent(
                "Presentation",
                0,
                2,
                1,
                {"ASName": "Disappear_Common"} if name == FLOW_NAMES[1] else None,
            ),
            evfl.ActionEvent("Name", 0, 0, 2),
            evfl.ActionEvent("AddOwn", 0, 1, 3),
            evfl.ActionEvent("Window", 1, 0, 4, {"ActorName": evfl.Argument("ActorName")}),
            evfl.ActionEvent("Cleanup", 0, 3, 5),
            evfl.ActionEvent("Autosave", 2, 0, evfl.NONE),
        ],
        entry_points=[evfl.EntryPoint("Pickup", 0)],
    )


@pytest.fixture
def receipts(tmp_path, zsdic_pack):
    native = {}
    for name in FLOW_NAMES:
        native[keys.flow_path(name)] = evfl.write(evfl.EventFlowFile(name, flowchart=flow(name)))
    for name in ("GetPouchContent", "Dm_SY_GetInEvent", "Dm_Kokiri_0155", "Dm_MelodyGet_Time"):
        chart = pouch_fixture()
        chart.name = name
        native[keys.flow_path(name)] = evfl.write(evfl.EventFlowFile(name, flowchart=chart))
    write_romfs(tmp_path, zsdic_pack, native)
    receipt_changes = ocarina_pickup.receipt_changes(tmp_path)
    keep_time = ocarina.changes(tmp_path, prior_changes=(receipt_changes,))
    charts = {}
    for path, data in native.items():
        for changes in (receipt_changes, keep_time):
            if path in changes:
                data = changes[path](data)
        document = evfl.read(data)
        assert evfl.read(evfl.write(document)) == document
        charts[document.flowchart.name] = document.flowchart
    return native, charts, receipt_changes


def state(*, time=1, fairy=0, historical_time=True):
    owned = {item for item, amount in ((TIME, time), (FAIRY, fairy)) if amount}
    history = owned | ({TIME} if historical_time else set())
    selected = TIME if time else FAIRY if fairy else ""
    return {
        "stock": Counter({TIME: time, FAIRY: fairy}),
        "flags": {"IsGet." + item for item in history},
        "history": set(history),
        "strings": {ocarina.EQUIPPED: selected},
        "live": selected,
        "own_adds": 0,
        "cleanup": 0,
        "presentation": [],
        "autosaves": [],
    }


def run(charts, name, own, current, *, buffered=True):
    """Model native clamped grants and the observed raw-own-add/saved-selector versus live-equipment split.

    Explicit selector writes can be buffered until a frame passes, as in test_ocarina.
    The native own-add grants history but does not create live equipment; the named add does.
    """
    here, at = charts[name], charts[name].entry_point("Pickup").main_event
    pending, stack = {}, []
    env = {"ActorName": own}
    for _ in range(200):
        if at == evfl.NONE:
            if not stack:
                return
            here, at, env = stack.pop()
            continue
        event = here.events[at]
        if isinstance(event, evfl.SubFlowEvent):
            stack.append((here, event.next, env))
            values = {
                key: env[str(value)] if isinstance(value, evfl.Argument) else value
                for key, value in (event.params or {}).items()
            }
            env = {**env, **values}
            here = charts[event.flowchart or here.name]
            at = here.entry_point(event.entry_point).main_event
            continue
        params = {
            key: env[str(value)] if isinstance(value, evfl.Argument) else value
            for key, value in (event.params or {}).items()
        }
        actor = here.actors[event.actor]
        if isinstance(event, evfl.SwitchEvent):
            query = actor.queries[event.query]
            if query == "EventQueryIsExistInPouch":
                answer = current["stock"][params["Actor"]] >= params["Num"]
            else:
                assert query == "EventQueryIsGameDataString64", event
                answer = current["strings"].get(params["GameDataName"], "") == params["Value"]
            at = dict(event.cases)[0 if answer else 1]
            continue
        action = actor.actions[event.action]
        if action == "EventTriggerSetOwnNameToMessage":
            current["strings"][TARGET] = own
        elif action in ("EventTriggerAddOwnToPouch", "EventTriggerAddOrRemovePouchContent"):
            raw = action == "EventTriggerAddOwnToPouch"
            item, amount = (own, 1) if raw else (params["Actor"], params["Num"])
            current["stock"][item] += amount
            if item in (FAIRY, TIME):
                current["stock"][item] = min(1, current["stock"][item])
                current["strings"][ocarina.EQUIPPED] = item
                if not raw:
                    current["live"] = item
            current["flags"].add("IsGet." + item)
            if raw or params["IsGetEvent"]:
                current["history"].add(item)
            if raw:
                current["own_adds"] += 1
            elif params["IsSetMessageTargetActorName"]:
                current["strings"][TARGET] = item
        elif action == "EventTriggerSetGameDataString64":
            (pending if buffered else current["strings"])[params["GameDataName"]] = params["Value"]
        elif action == "EventWait":
            current["strings"].update(pending)
            pending.clear()
        elif action == "EventTriggerSyncPlayerEquipmentAndPouch":
            current["live"] = current["strings"][ocarina.EQUIPPED]
        elif action == "EventGoOffstageForUser":
            current["cleanup"] += 1
            current["flags"].add("SourceConsumed")
        elif action == "EventTriggerRequestAutoSave":
            current["autosaves"].append(
                {
                    "selector": current["strings"][ocarina.EQUIPPED],
                    "live": current["live"],
                    "stock": copy.deepcopy(current["stock"]),
                    "flags": set(current["flags"]),
                    "history": set(current["history"]),
                }
            )
        else:
            assert action in (
                "EventPlayAS",
                "EventTriggerModelBindForItemGetDemo",
                "EventTriggerRequestOpenPickUpWindow",
            ), event
            current["presentation"].append((action, params))
        at = event.next
    raise AssertionError((here.name, at, current))


def native_result(native, name, own, before, *, buffered):
    chart = evfl.read(native[keys.flow_path(name)]).flowchart
    current = copy.deepcopy(before)
    run({name: chart}, name, own, current, buffered=buffered)
    return current


def assert_native_reward_and_continuation(after, native):
    for key in ("stock", "flags", "history", "presentation"):
        assert after[key] == native[key], (key, after, native)
    assert after["own_adds"] == native["own_adds"] == 1
    assert after["cleanup"] == native["cleanup"] == 1
    assert len(after["autosaves"]) == len(native["autosaves"]) == 1
    for key in ("stock", "flags", "history"):
        assert after["autosaves"][0][key] == native["autosaves"][0][key]


@pytest.mark.parametrize("name", FLOW_NAMES)
@pytest.mark.parametrize("buffered", [False, True])
@pytest.mark.parametrize("fairy", [0, 1])
def test_fairy_after_time_keeps_saved_and_live_time_through_cleanup_and_autosave(receipts, name, buffered, fairy):
    native, charts, _ = receipts
    before = state(fairy=fairy)
    original = native_result(native, name, FAIRY, before, buffered=buffered)
    after = copy.deepcopy(before)
    run(charts, name, FAIRY, after, buffered=buffered)
    assert_native_reward_and_continuation(after, original)
    assert after["stock"] == Counter({TIME: 1, FAIRY: 1})
    assert after["strings"][TARGET] == FAIRY
    assert after["strings"][ocarina.EQUIPPED] == after["live"] == TIME
    assert after["autosaves"][0]["selector"] == after["autosaves"][0]["live"] == TIME


@pytest.mark.parametrize("name", FLOW_NAMES)
@pytest.mark.parametrize("buffered", [False, True])
@pytest.mark.parametrize("historical_time", [False, True])
def test_fairy_without_time_stock_never_grants_or_selects_time(receipts, name, buffered, historical_time):
    native, charts, _ = receipts
    before = state(time=0, historical_time=historical_time)
    original = native_result(native, name, FAIRY, before, buffered=buffered)
    after = copy.deepcopy(before)
    run(charts, name, FAIRY, after, buffered=buffered)
    assert_native_reward_and_continuation(after, original)
    assert after["stock"] == Counter({TIME: 0, FAIRY: 1})
    assert after["strings"][ocarina.EQUIPPED] == after["live"] == FAIRY
    assert after["autosaves"][0]["selector"] == after["autosaves"][0]["live"] == FAIRY


@pytest.mark.parametrize("name", FLOW_NAMES)
@pytest.mark.parametrize("buffered", [False, True])
def test_first_time_receipt_is_usable_before_autosave(receipts, name, buffered):
    native, charts, _ = receipts
    before = state(time=0, fairy=1, historical_time=False)
    original = native_result(native, name, TIME, before, buffered=buffered)
    after = copy.deepcopy(before)
    run(charts, name, TIME, after, buffered=buffered)
    assert_native_reward_and_continuation(after, original)
    assert after["strings"][TARGET] == TIME
    assert after["strings"][ocarina.EQUIPPED] == after["live"] == TIME
    assert after["autosaves"][0]["selector"] == after["autosaves"][0]["live"] == TIME


@pytest.mark.parametrize("name", FLOW_NAMES)
@pytest.mark.parametrize("own", ["Item_Heart_Piece", "Item_Melody_ZeldaLullaby", "Item_Boomerang"])
def test_other_receipts_preserve_native_rewards_presentation_and_selection(receipts, name, own):
    native, charts, _ = receipts
    before = state(fairy=1)
    original = native_result(native, name, own, before, buffered=True)
    after = copy.deepcopy(before)
    run(charts, name, own, after)
    assert after == original


@pytest.mark.parametrize("name", FLOW_NAMES)
def test_a_flow_without_one_own_add_or_already_patched_is_refused(name):
    chart = flow(name)
    chart.events[2] = evfl.ActionEvent("AddOwn", 0, 0, 3)
    with pytest.raises(PatchError, match="AddOwnToPouch"):
        ocarina_pickup.patch_receipt(chart)
    chart = flow(name)
    ocarina_pickup.patch_receipt(chart)
    with pytest.raises(PatchError, match="already"):
        ocarina_pickup.patch_receipt(chart)


@pytest.mark.parametrize("name", FLOW_NAMES)
def test_each_receipt_transform_refuses_a_changed_source(receipts, name):
    _, _, changes = receipts
    other = evfl.write(evfl.EventFlowFile("Other", flowchart=flow("Other")))
    with pytest.raises(PatchError, match="source changed"):
        changes[keys.flow_path(name)](other)
