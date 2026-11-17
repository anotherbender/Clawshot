"""Skipped location banners must retain the visit state that makes the area's map available."""

import pytest
from test_fast_start_kaepora import FIELD_PANORAMA, game_data_list, initial_value

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import gamedata
from clawshot.save import key

VISIT = "IsVisitLocation.KokiriForest"


@pytest.mark.parametrize("skips", [[], ["intro"], ["saria"], ["intro", "saria"]])
def test_saria_skip_marks_only_its_missing_area_banner_visited(skips):
    names = [
        "HavePlayedEvent.Dm_Kokiri_0045",
        "HavePlayedEvent.Dm_Kokiri_0050",
        "HavePlayedEvent.Dm_Kokiri_0060",
        "KokiriForest_LinkHouseDoor_Open",
        "HaveTalked.Npc_Kokiri_Saria_Child",
        VISIT,
        "IsVisitLocation.HyruleField",
    ]
    rows = [{"Hash": byml.U32(key(name)), "DefaultValue": False, "ResetTypeValue": byml.I32(8)} for name in names]
    data = byml.write({"Data": {"Bool": rows, "Int": [], "Enum": []}}, "big")
    result = byml.read(gamedata.patch_initial_values(data, gamedata.select(gamedata.load(), skips)))
    flags = {row["Hash"]: row["DefaultValue"] for row in result["Data"]["Bool"]}
    assert flags[key(VISIT)] is ("saria" in skips)
    assert flags[key("IsVisitLocation.HyruleField")] is False


def test_kaepora_skip_keeps_the_field_map_available_without_its_panorama():
    """The skipped Dm_HrlField_0000 opens Hyrule Field's location UI; walking in does not replace that effect."""
    settings = gamedata.load()
    visit = "IsVisitLocation.HyruleField"
    data = game_data_list([visit, *settings["kaepora"].game_data])
    written = gamedata.patch_initial_values(data, gamedata.select(settings, ["kaepora"]))
    values = {name: initial_value(written, name) for name in (FIELD_PANORAMA, visit)}
    assert values[FIELD_PANORAMA] is True  # the panorama will not run and open the map
    assert values[visit] is True, values


@pytest.mark.dump
def test_every_skipped_location_banner_preserves_its_native_visit(romfs):
    """Derive lost banner effects from native event routing, including timeline companions."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = "RSDB/EventSetting.Product.111.rstbl.byml.zs"
    routes = {row["__RowId"]: row for row in byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))}
    documents = {}
    for setting in [*gamedata.load().values(), *gamedata.load_always()]:
        pending = {
            name.removeprefix("HavePlayedEvent.")
            for name, value in setting.game_data.items()
            if name.startswith("HavePlayedEvent.") and value is True
        }
        seen = set()
        required = {}
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            seen.add(name)
            route = routes[name]
            references = [
                route[field] for field in ("FlowchartFileName", "TimelineFileName") if route.get(field)
            ] + route.get("SubTimelineNames", [])
            for reference in references:
                path = reference.removeprefix("Work/").rsplit(".", 1)[0] + ".bfevfl.zs"
                if path not in documents:
                    documents[path] = evfl.read(dictionaries.decompress(path, (romfs / path).read_bytes()))
                document = documents[path]
                actions = []
                if document.flowchart is not None:
                    fc = document.flowchart
                    actions.extend(
                        (fc.actors[event.actor].actions[event.action], event.params or {})
                        for event in fc.events
                        if isinstance(event, evfl.ActionEvent)
                    )
                if document.timeline is not None:
                    timeline = document.timeline
                    actions.extend(
                        (timeline.actors[clip.actor].actions[clip.action], clip.params or {}) for clip in timeline.clips
                    )
                for operation, params in actions:
                    if operation == "EventTransition" and isinstance(params.get("EventName"), str):
                        pending.add(params["EventName"])
                    assert operation != "EventTriggerOpenCurrentSmallLocationUI", (
                        setting.name,
                        path,
                        "Resolve the current small location before suppressing its banner",
                    )
                    if operation == "EventTriggerOpenLocationUI":
                        area = params["LocationName"].removeprefix("Work/Location/").split(".", 1)[0]
                        required[f"IsVisitLocation.{area}"] = path
        for visit, source in required.items():
            assert setting.game_data.get(visit) is True, (setting.name, source, visit)
