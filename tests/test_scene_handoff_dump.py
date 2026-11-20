"""Native serialized data/grant execution; message rendering and gameplay remain play-held."""

import os
from pathlib import Path

import pytest
from test_scene_handoff import run, state

from clawshot.census import definitions
from clawshot.census.gifts import FLOW_VERSIONS, flow_files, scan_gifts
from clawshot.census.scan import read_romfs_byml
from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import bags, door, gifts, keys, ocarina
from clawshot.patch import scene_handoff as handoff

pytestmark = pytest.mark.dump

NATIVE_REWARDS = {
    "forest": "Item_Melody_ForestMinuet",
    "fire": "Item_Melody_FireBolero",
    "water": "Item_Melody_WaterSerenade",
    "shadow": "Item_Melody_ShadowNocturne",
    "shine": "Item_Melody_LightPrelude",
    "spirit": "Item_Melody_SpiritRequiem",
    "impa": "Item_Melody_ZeldaLullaby",
    "epona": "Item_Melody_EponaSong",
    "saria_song": "Item_Melody_SariaSong",
    "sun": "Item_Melody_SunSong",
    "time": "Item_Melody_TimeSong",
    "storm": "Item_Melody_StormSong",
    "storm_back": "Item_Melody_StormSong",
    "saria_farewell": ocarina.FAIRY,
}


@pytest.fixture(scope="module", params=[False, True], ids=["native", "moved"])
def compiled(request):
    if not os.environ.get("OOT_ROMFS"):
        pytest.skip("OOT_ROMFS is not set")
    root = Path(os.environ["OOT_ROMFS"])
    dictionaries = zsdic.Dictionaries.from_romfs(root)
    scenes = handoff.load()
    prior = []
    if request.param:
        moves = {scene.check: "Item_Boomerang" for scene in scenes}
        moves["HF Ocarina of Time Item"] = "Item_Melody_EponaSong"
        files = flow_files(root, read_romfs_byml(root, dictionaries, FLOW_VERSIONS)["Versions"])
        prior.append(gifts.file_changes(gifts.plan(moves, scan_gifts(root), definitions.load(), gifts.load()), files))
    prior.append(door.changes({}, mode="closed"))
    result = handoff.build(root, skip_saria_farewell=True, prior_changes=prior)
    changes = (*prior, result.changes, bags.changes(root))
    changes += (ocarina.changes(root, prior_changes=changes),)

    def read(path):
        data = dictionaries.decompress(path, (root / path).read_bytes())
        for step in changes:
            if path in step:
                data = step[path](data)
        return data

    names = {keys.POUCH, *(scene.flow for scene in scenes)}
    names.update(ref.split("/")[0] for scene in scenes for ref in (*scene.grants, *scene.before, *scene.after))
    charts = {name: evfl.read(read(keys.flow_path(name))).flowchart for name in sorted(names)}
    charts[handoff.FLOW] = evfl.read(result.new_files[handoff.FLOW_PATH].data).flowchart
    rows = {
        row["__RowId"]: {
            "flow": Path(row["FlowchartFileName"]).stem,
            "entry": row.get("EntryPointName") or "EntryPoint0",
        }
        for row in byml.load(read(keys.SETTINGS)).root
        if row.get("FlowchartFileName")
    }
    return request.param, scenes, charts, rows


@pytest.mark.parametrize("name", NATIVE_REWARDS)
def test_each_lesson_and_farewell_really_grants_effective_reward_once(compiled, name):
    moved, scenes, charts, rows = compiled
    scene = next(scene for scene in scenes if scene.name == name)
    current = state(child=True)
    run(charts, rows, handoff.FLOW, name, current, data_only=True)
    expected = "Item_Boomerang" if moved else NATIVE_REWARDS[name]
    assert current["stock"].get(expected) == 1, (name, current)
    assert current["IsGet." + expected] is True
    assert current[scene.once] is True, (name, current)
    if moved and NATIVE_REWARDS[name].startswith("Item_Melody_"):
        assert not current.get("IsGet." + NATIVE_REWARDS[name], False), (name, current)
    if name == "time":
        other = "Item_Melody_EponaSong" if moved else ocarina.TIME
        assert current["stock"].get(other) == 1, current
    run(charts, rows, handoff.FLOW, name, current, data_only=True)
    assert current["stock"][expected] == 1, (name, current)
    assert len(current["grants"]) == (2 if name == "time" else 1), current


@pytest.mark.parametrize(
    "name,child,selected,fairy",
    [("forest", False, ocarina.FAIRY, 1), ("epona", True, "", 0), ("saria_farewell", True, "", 0)],
)
def test_staged_target_callers_never_enter_pose_or_cinematic_context(compiled, name, child, selected, fairy):
    moved, scenes, charts, rows = compiled
    scene = next(scene for scene in scenes if scene.name == name)
    current = state(child=child, selected=selected, fairy=fairy)
    trace, transitions = run(charts, rows, scene.flow, scene.entry, current, data_only=True)
    expected = "Item_Boomerang" if moved else NATIVE_REWARDS[name]
    assert current["stock"].get(expected) == 1, (name, current, trace)
    assert current["IsGet." + expected]
    assert transitions == [handoff._event_name(scene)], (name, transitions)
    assert all(contexts == (handoff._event_name(scene),) for _, _, contexts in current["grants"])
    if name == "saria_farewell":
        assert current["requester_bool"] and current["HyruleField_ChangeENV"]
        assert current["HavePlayedEvent.Dm_Kokiri_0150"] and current["HavePlayedEvent.Dm_Kokiri_0155"]
        assert any(operation == "EventReserveBancChange" for operation, _ in current["effects"])
    run(charts, rows, scene.flow, scene.entry, current, data_only=True)
    assert current["stock"][expected] == 1, (name, current)
