"""Spec tracker-auto-checks 5.1-5.3 on the player's dump: with every tracked gift check patched to a shuffled item,
each ``track`` flag is still set on exactly the grant's paths (``bool``, ``quest``), and each ``played`` cutscene
row exists and its grant cut still reaches the grant (the patch neither removes nor skips it). Evidence:
``plans/tracker-auto-checks-audit.md``."""

import copy
from pathlib import PurePosixPath

import pytest
from track_paths import Flag, check, cut_reaches, writers

from clawshot.census import definitions
from clawshot.census.gifts import EVENT_SETTING, FLOW_VERSIONS, flow_files, scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import evfl, zsdic
from clawshot.patch import gifts

NEW_ITEM = "Item_Boomerang"
# Walks the game cannot take, each a fact of the flows (audit note 2): MiniGameClearCount sets ClearSecondTime only
# after reading ClearFirstTime true, and nothing resets ClearFirstTime.
INVARIANTS = {
    "Market Bombchu Bowling First Prize": [
        ("MiniGame_BombchuBowling_ClearSecondTime", True, "MiniGame_BombchuBowling_ClearFirstTime", True)
    ],
}


@pytest.fixture(scope="module")
def patched(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    versions = {str(k): str(v) for k, v in read_romfs_byml(romfs, dicts, FLOW_VERSIONS)["Versions"].items()}
    flows = {}
    for flow, path in flow_files(romfs, versions).items():
        tree = evfl.read(dicts.decompress(path, (romfs / path).read_bytes()))
        if tree.flowchart is not None:
            flows[flow] = tree.flowchart
    rules = gifts.load()
    tracked = {name: rule for name, rule in rules.items() if rule.track}
    census = scan_gifts(romfs)
    changes = gifts.plan(dict.fromkeys(tracked, NEW_ITEM), census, definitions.load(), rules)
    for flow in gifts.flows_changed(changes):
        flows[flow] = copy.deepcopy(flows[flow])
        gifts.patch_flowchart(flows[flow], flow, changes)
    rows = {str(row["__RowId"]): row for row in read_romfs_byml(romfs, dicts, EVENT_SETTING)}
    external: dict[str, set[str]] = {}
    for row in rows.values():
        if "FlowchartFileName" in row and "EntryPointName" in row:
            external.setdefault(PurePosixPath(str(row["FlowchartFileName"])).stem, set()).add(
                str(row["EntryPointName"])
            )
    for flow, fc in flows.items():
        for event in fc.events:
            if isinstance(event, evfl.SubFlowEvent) and event.flowchart and event.flowchart != flow:
                external.setdefault(event.flowchart, set()).add(event.entry_point)
    steps = gifts.check_steps(census, definitions.load())
    return flows, rows, external, steps, tracked


def _transitions(fc: evfl.Flowchart, target: str) -> list[str]:
    """Events of ``fc`` that start the event (cutscene) ``target``."""
    return [
        e.name
        for e in fc.events
        if isinstance(e, evfl.ActionEvent)
        and fc.actors[e.actor].actions[e.action] == "EventTransition"
        and (e.params or {}).get("EventName") == target
    ]


@pytest.mark.dump
def test_dump_every_track_flag_follows_its_grant_in_the_patched_flows(patched):
    flows, rows, external, steps, tracked = patched
    faults, checked = [], 0
    for name, rule in sorted(tracked.items()):
        grant_flows = {s.flow for s in steps[name]}
        assert len(grant_flows) == 1, (name, grant_flows)
        [grant_flow] = grant_flows
        grants = [s.event for s in steps[name]]
        for skipped in rule.skip:
            assert skipped not in {f"{grant_flow}/{g}" for g in grants}, (name, skipped)  # 5.2: never the grant
        for entry in rule.track:
            checked += 1
            if entry.kind == "played":  # 5.2
                row = rows.get(entry.name)
                if row is None or PurePosixPath(str(row.get("FlowchartFileName"))).stem != grant_flow:
                    faults.append(f"{name}: no EventSetting row {entry.name} for the grant flow {grant_flow}")
                    continue
                faults += [f"{name}: {f}" for f in cut_reaches(flows[grant_flow], grants)]
                continue
            flag = Flag(entry.kind, entry.name, entry.step)  # 5.1
            homes = sorted(flow for flow, fc in flows.items() if writers(fc, flag))
            if len(homes) != 1:
                faults.append(f"{name}: {flag.key} is set in {homes}, expected one flow")
                continue
            [home] = homes
            if home == grant_flow:
                in_home = grants
            else:  # the writer's flow starts the grant's cutscene, whose cut must then always grant
                in_home = _transitions(flows[home], grant_flow)
                faults += [f"{name}: {f}" for f in cut_reaches(flows[grant_flow], grants)]
                if not in_home:
                    faults.append(f"{name}: {home} sets {flag.key} but never starts {grant_flow}")
                    continue
            param = {s.event: s.param for s in steps[name] if s.param}
            faults += [
                f"{name}: {f}"
                for f in check(
                    flows[home],
                    flag,
                    in_home,
                    external=external.get(home, ()),
                    param=param if home == grant_flow else {},
                    invariants=INVARIANTS.get(name, ()),
                )
            ]
    print(f"{checked} track entries of {len(tracked)} gifts checked against the patched flows")
    assert faults == [], "\n".join(faults)
