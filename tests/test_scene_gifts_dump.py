"""Real native split grants compose with display/heal registration and private captions."""

import pytest
from test_event_registration import World, dump_events

from clawshot.census import definitions
from clawshot.census.gifts import reachable, scan_gifts
from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import gifts, items
from clawshot.patch import scene_gifts as scenes

pytestmark = pytest.mark.dump


def test_native_heart_grants_declare_their_recovery_and_preserve_shared_caption_entry(romfs):
    native, files = dump_events(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    actors = items.load()
    placements = {scenes.MOAT: "Piece of Heart", scenes.SARIA: "Piece of Heart"}
    swaps = gifts.plan(
        {name: actors.actor(item) for name, item in placements.items()},
        scan_gifts(romfs),
        definitions.load(),
        gifts.load(),
    )
    patches = [gifts.file_changes(swaps, files), scenes.changes(placements, actors)]
    charts = dict(native.charts)
    analysis = native.analyzed
    for path in sorted(set().union(*(patch.keys() for patch in patches))):
        data = dictionaries.decompress(path, (romfs / path).read_bytes())
        for patch in patches:
            if path in patch:
                data = patch[path](data)
        if path == scenes.ANALYZED:
            analysis = byml.read(data)
        else:
            chart = evfl.read(data).flowchart
            charts[chart.name] = chart
    patched = World(charts, native.settings, analysis)
    assert patched.gaps() - native.gaps() == set()
    for flow, _, grant, display, anchor in scenes.SOURCES.values():
        chart = charts[flow]
        events = {event.name: event for event in chart.events}
        heal = events[scenes.HEAL]
        assert (heal.flowchart, heal.entry_point, heal.params) == (
            "Dm_SY_Get",
            "CheckHeart",
            {"ActorName": "Obj_Heart_Piece"},
        )
        assert chart.events[events[anchor].next] == heal
        assert events[grant].params["Actor"] == events[display].params["ActorName"] == "Obj_Heart_Piece"
    before, after = native.charts[scenes.POUCH], charts[scenes.POUCH]
    assert after.events[: len(before.events)] == before.events
    assert after.entry_points[: len(before.entry_points)] == before.entry_points
    # Follow each native caption branch in the specialized clone (default includes a local call).
    entry = after.entry_point(scenes.DISPLAY)
    setup = after.events[entry.main_event]
    assert setup.params == {"Actor": evfl.Argument("ActorName")}
    query = after.events[after.entry_point(scenes.DISPLAY + "Caption").main_event]
    expected = {0: "FourthGetCaption", 1: "GetCaption", 2: "SecondGetCaption", 3: "ThirdGetCaption"}
    for count, target in query.cases:
        branch = [after.events[i] for i in reachable(after, target)]
        messages = [(event.params or {}).get("MessageId", "") for event in branch]
        if count == 1:
            assert any(
                isinstance(event, evfl.SubFlowEvent) and event.entry_point == "DefaultGetMessage" for event in branch
            )
        else:
            assert any(message.endswith("Obj_Heart_Piece_" + expected[count]) for message in messages)


def test_native_checkheart_has_recovery_but_no_grant_window_model_or_autosave(romfs):
    native, _ = dump_events(romfs)
    chart = native.charts["Dm_SY_Get"]
    events = [chart.events[i] for i in reachable(chart, chart.entry_point("CheckHeart").main_event)]
    actions = {
        chart.actors[event.actor].actions[event.action] for event in events if isinstance(event, evfl.ActionEvent)
    }
    assert actions == {
        "EventTriggerReserveRecoverOrAddHeartGauge",
        "EventTriggerSetDisplayHeartGauge",
        "EventWait",
        "EventTriggerRecoverByCureItem",
        "EventStartRecoverOrAddHeartGauge",
    }
    assert not any(isinstance(event, evfl.SubFlowEvent) for event in events)
    recover = [
        event
        for event in events
        if isinstance(event, evfl.ActionEvent)
        and chart.actors[event.actor].actions[event.action] == "EventTriggerRecoverByCureItem"
    ]
    assert [event.params for event in recover] == [{"ActorName": evfl.Argument("ActorName")}]
    assert chart.events[chart.entry_point("CheckHeart").main_event].name == "Event145"
    names = {event.name: event for event in chart.events}
    assert [chart.events[target].name for _, target in names["Event145"].cases] == ["Event156", "Event149"]
    assert chart.events[dict(names["Event149"].cases)[0]].name == "Event156"
