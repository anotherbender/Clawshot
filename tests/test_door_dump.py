"""Native door overlays: behavioral flow oracle, exact inverse edits and composed GameData."""

import struct
from copy import deepcopy

import pytest
from test_door import run_open_flow

from clawshot.formats import byml, evfl, rstb, zsdic
from clawshot.patch import age, door, door_stage, door_story
from clawshot.patch.plan import Plan
from clawshot.patch.write import write
from clawshot.save import key

pytestmark = pytest.mark.dump


def reaction_value(values, flags):
    stack = []
    for command in values:
        if command[0] == 0:
            stack.append(flags[command[1]])
        elif command[0] == 5:
            stack.append(not stack.pop())
        elif command[0] == 4:
            right, left = stack.pop(), stack.pop()
            stack.append(left or right)
        else:
            pytest.fail(f"unexpected altar opcode: {command!r}")
    assert len(stack) == 1, stack
    return stack[0]


def test_song_only_native_output_keeps_play_once_and_all_other_story_paths(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    out = tmp_path / "song-only"
    write(
        Plan([], [], []),
        romfs,
        out,
        extra_changes=[age.changes({}, free_time_travel=True), door.changes({}, mode="song_only")],
    )
    patched = evfl.read(dictionaries.decompress(door.FLOW, (out / "romfs" / door.FLOW).read_bytes()))
    for learned, recommended, opened, sendoff in [
        (True, True, False, False),
        (True, True, False, True),
        (False, True, False, True),
        (True, False, False, True),
        (True, True, True, True),
    ]:
        state = {door.TIME_SONG: learned, door.OPENED: opened, door.SENDOFF: sendoff}
        scenes, writes = run_open_flow(patched.flowchart, state, recommended=recommended)
        success = learned and recommended and not opened and sendoff
        assert scenes == (["Dm_TimeTemple_0010"] if success else [])
        assert (door.OPENED in writes) == success
        assert ("Step_DoorOfTime" in writes) == success
        assert not any(name.startswith("Step_Get_Stone") or name.startswith("IsGet.") for name in writes)
        if success:
            assert run_open_flow(patched.flowchart, deepcopy(state)) == ([], [])

    native_game = byml.load(dictionaries.decompress(door.GAME_DATA_LIST, (romfs / door.GAME_DATA_LIST).read_bytes()))
    new_game = byml.load(
        dictionaries.decompress(door.GAME_DATA_LIST, (out / "romfs" / door.GAME_DATA_LIST).read_bytes())
    )
    assert new_game.byte_order == native_game.byte_order
    native_hashes = {row["Hash"] for row in native_game.root["Data"]["BoolExp"]}
    added = [row for row in new_game.root["Data"]["BoolExp"] if row["Hash"] not in native_hashes]
    assert {row["Hash"] for row in added} == {
        key(name)
        for name in (age.SHEIK_PRESENCE, door_story.ESCAPE_READY, door_stage.MOAT_READY, door_stage.MOAT_AREAS_DONE)
    }
    assert all(row["SaveFileIndex"] == -1 and row["ResetTypeValue"] == 0 for row in added)
    new_game.root["Data"]["BoolExp"][:] = [
        row for row in new_game.root["Data"]["BoolExp"] if row["Hash"] in native_hashes
    ]
    old_reaction = next(row for row in native_game.root["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
    new_reaction = next(row for row in new_game.root["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
    for opened in (False, True):
        for sendoff in (False, True):
            flags = {key(door.OPENED): opened, key(door.SENDOFF): sendoff}
            assert reaction_value(new_reaction["Values"], flags) is (opened or not sendoff)
    new_reaction["Values"] = old_reaction["Values"]
    assert byml.same(native_game.root, new_game.root)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (out / "romfs" / rstb.TABLE_PATH).read_bytes()))
    for path in (age.PLACEMENT, door.FLOW, door.GAME_DATA_LIST):
        size = len(dictionaries.decompress(path, (out / "romfs" / path).read_bytes()))
        assert table.get(path) >= rstb.required_size(path, size)


def test_open_native_door_and_first_pull_need_no_quest_forgery(romfs, tmp_path):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    out = tmp_path / "open"
    door.write(romfs, out, mode="open")
    original = byml.load(dictionaries.decompress(door.PLACEMENT, (romfs / door.PLACEMENT).read_bytes()))
    patched = byml.load(dictionaries.decompress(door.PLACEMENT, (out / "romfs" / door.PLACEMENT).read_bytes()))
    old_group = next(group for group in original.root["AiGroups"] if group["Hash"] == door.DRAW_GROUP)
    new_group = next(group for group in patched.root["AiGroups"] if group["Hash"] == door.DRAW_GROUP)
    assert new_group["Logic"] == age.UNGATED_LOGIC
    assert {ref["Id"]: ref["Reference"] for ref in new_group["References"]} == {
        "EventRequestActor_7a32": 17385100471140562353,
        "CheckAttentionActor_8348": 1016238122178870176,
    }
    new_group.clear()
    new_group.update(old_group)
    assert byml.same(original.root, patched.root)
    assert original.byte_order == patched.byte_order
    # Closed is the actual no-patch control, not another state-setting route.
    assert door.write(romfs, tmp_path / "closed", mode="closed") == []


def door_signals(module, *, sendoff, step, proxy):
    """Evaluate the supported native gate graph, including its query/output dependencies.

    Offsets are independently audited against the native AINB, not a copied decoder.
    The native OR also drives IsSkipAnim: automatic opening must not run the stone scene.
    """
    flag = module[0x1D23 : module.index(b"\0", 0x1D23)].decode()
    threshold = module[0x1DA0 : module.index(b"\0", 0x1DA0)].decode()
    steps = ["NotReady", "Ready", "Step01", "Step02", "Step03", "Step04", "Step05", "Step06", "Complete"]
    comparison = steps.index(step) - steps.index(threshold)
    values = {(4, 1): proxy, (8, 0): comparison > 0, (8, 2): comparison == 0}
    queries = [struct.unpack_from("<H", module, offset)[0] for offset in (0x18FC, 0x1900, 0x1904)]
    if 6 in queries:
        assert struct.unpack_from("<I", module, 0x1770)[0] & (1 << 31), "clock reader output is inactive"
        values[6, 0] = {"HavePlayedEvent.Dm_HrlField_0020": sendoff, door.OPENED: True}[flag]
    sources = [struct.unpack_from("<hh", module, offset) for offset in (0x1898, 0x18A0, 0x18A8)]
    assert struct.unpack_from("<i", module, 0x938)[0] == sources[0][0], "stale OR plug"
    assert all(node in queries for node, _ in sources), "unevaluated gate input"
    opened = any(values[source] for source in sources)
    signals = []
    for offset in (0x1478, 0x1488):  # ActorLogicGateDoor isOpen / IsSkipAnim.
        assert struct.unpack_from("<hh", module, offset) == (5, 1)
        signals.append(opened)
    return tuple(signals)


@pytest.mark.parametrize("sendoff", [False, True])
@pytest.mark.parametrize(
    "step,proxy", [("NotReady", False), ("Ready", False), ("Step01", False), ("Step06", True), ("Complete", True)]
)
def test_open_door_waits_for_real_sendoff_not_quest_progress_or_a_scene_request(romfs, sendoff, step, proxy):
    module = next(file for file in door.build(romfs, mode="open") if file.path == door.DOOR_LOGIC)
    actual = door_signals(module.content, sendoff=sendoff, step=step, proxy=proxy)
    assert actual == (sendoff, sendoff), {"sendoff": sendoff, "step": step, "proxy": proxy, "signals": actual}


def test_open_auto_gate_disables_the_later_song_scene(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(door.GAME_DATA_LIST, (romfs / door.GAME_DATA_LIST).read_bytes())
    patched = byml.load(door.changes({}, mode="open")[door.GAME_DATA_LIST](raw))
    row = next(row for row in patched.root["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
    # At Step05, unopened is normally a valid song trigger even if the open-mode
    # physical gate already opened. No once flag/quest must be forged to disable it.
    for opened in (False, True):
        assert reaction_value(row["Values"], {key(door.OPENED): opened}) is True
