"""Every split gift display is declared; native grant/window pairs change together."""

import pytest

from clawshot.census import definitions
from clawshot.census.gifts import FLOW_VERSIONS, flow_files, scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, zsdic
from clawshot.patch import gifts

pytestmark = pytest.mark.dump


@pytest.fixture(scope="module")
def context(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    versions = read_romfs_byml(romfs, dictionaries, FLOW_VERSIONS)["Versions"]
    files = flow_files(romfs, {str(k): str(v) for k, v in versions.items()})
    census = scan_gifts(romfs)
    charts = {}
    for flow in sorted({gift.flow for gift in census}):
        path = files[flow]
        charts[flow] = dictionaries.decompress(path, (romfs / path).read_bytes())
    return census, files, charts


def test_every_literal_display_in_a_gift_flow_is_declared(context):
    _, _, charts = context
    found = set()
    for flow, data in charts.items():
        for event in evfl.read(data).flowchart.events:
            if (
                isinstance(event, evfl.SubFlowEvent)
                and (event.flowchart, event.entry_point) == ("GetPouchContent", "DisplayGetByActorName")
                and isinstance((event.params or {}).get("ActorName"), str)
                and not isinstance(event.params["ActorName"], evfl.Argument)
            ):
                found.add(f"{flow}/{event.name}")
    declared = [ref for rule in gifts.load().values() for ref in rule.display]
    assert found == set(declared)
    assert len(declared) == len(set(declared)), "a display cannot belong to two grants"


@pytest.mark.parametrize(
    "check,item",
    [("HF Ocarina of Time Item", "Obj_Heart_Piece"), ("LW Gift from Saria", "Item_Bottle")],
)
def test_native_display_and_grant_change_together_and_vanilla_is_identical(context, check, item):
    census, files, charts = context
    rules = gifts.load()
    [change] = gifts.plan({check: item}, census, definitions.load(), rules)
    for flow in gifts.flows_changed([change]):
        data = charts[flow]
        fc = evfl.read(gifts.file_changes([change], files)[files[flow]](data)).flowchart
        for step in change.steps:
            if step.flow == flow:
                assert next(e for e in fc.events if e.name == step.event).params[step.param] == item
        for ref in change.rule.display:
            if ref.split("/")[0] == flow:
                assert next(e for e in fc.events if e.name == ref.split("/")[1]).params["ActorName"] == item
        vanilla = change.steps[0].vanilla_item
        [unchanged] = gifts.plan({check: vanilla}, census, definitions.load(), rules)
        assert gifts.file_changes([unchanged], files)[files[flow]](data) == data
