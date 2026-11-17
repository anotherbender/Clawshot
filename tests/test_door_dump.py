"""Native door overlays: behavioral flow oracle, exact inverse edits, exact written sets and byte masks."""

import hashlib
import struct
from copy import deepcopy
from dataclasses import replace

import pytest
from test_door import run_open_flow

from clawshot.formats import byml, evfl, rstb, zsdic
from clawshot.patch import age, door, door_stage, door_story
from clawshot.patch.plan import Plan
from clawshot.patch.write import write
from clawshot.save import key

pytestmark = pytest.mark.dump

MODES = ("closed", "song_only", "open")
EARLY = ("song_only", "open")
DOOR_FLOW = "Event/EventFlow/DoorOfTime.bfevfl.zs"
SARIA_FLOW = "Event/EventFlow/Dm_SY_Ocarina_SariaSong.bfevfl.zs"
ZELDA_FLOW = "Event/EventFlow/Npc_Hylia_Zelda_Child.bfevfl.zs"
GAME_DATA = "GameData/GameDataList.Product.110.byml.zs"
SIZE_TABLE = "System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs"
CHILD_MARKET = "Banc/Market/Market_Child_Static.bcett.byml.zs"
COMMON_GATE = "Logic/Market_Common_f252.logic.module.ainb"
STAGE_MODULES = (
    "Logic/HyruleField_Child_Prefab_0ce5.logic.module.ainb",
    "Logic/HyruleField_Child_Prefab_32f7.logic.module.ainb",
    "Logic/HyruleField_Child_Prefab_91f9.logic.module.ainb",
    "Logic/HyruleField_Child_Prefab_9e35.logic.module.ainb",
)
# Per mode, the only size-table entries that rise. Closed ships just the shared DoorOfTime ordering repair.
GROWN = {
    "closed": (DOOR_FLOW,),
    "song_only": (DOOR_FLOW, SARIA_FLOW, ZELDA_FLOW, GAME_DATA),
    "open": (DOOR_FLOW, SARIA_FLOW, ZELDA_FLOW, GAME_DATA),
}
# Goto_HyruleCastle (the courtyard's forced Step01 reset) stays native, so no mode writes it.
WRITTEN = {
    "closed": (*GROWN["closed"], SIZE_TABLE),
    "song_only": (*GROWN["song_only"], *STAGE_MODULES, SIZE_TABLE),
    "open": (*GROWN["open"], *STAGE_MODULES, SIZE_TABLE, CHILD_MARKET, COMMON_GATE),
}

# The nine lower DoorOfTime writers (native audit): flow -> (writer, step it writes, native next or None).
GUARDED = {
    DOOR_FLOW: (
        ("Event7", "Step02", "Event62"),
        ("Event147", "Step2_1", "Event5"),
        ("Event148", "Step2_2", "Event5"),
        ("Event37", "Step03", "Event77"),
        ("Event12", "Step04", "Event140"),
        ("Event14", "Step05", "Event171"),
        ("Event57", "Step06", None),
    ),
    SARIA_FLOW: (("Event172", "Srep2_1_1", None),),
    ZELDA_FLOW: (("Event42", "Srep2_1_1", None),),
}
# Every mode's DoorOfTime ordering repair; Event77's raise and Event62's Fire write stay native. The stone-counter
# entry first needs the send-off played and the escape unplayed; the send-off recounts between its quest write
# Event7 and Event62.
COUNTER = ("DoorOfTime_CheckStoneNum", "Event38")  # the entry and its native main event
COUNT_SENDOFF, COUNT_ESCAPE = "ClawshotDoorCountSendoff", "ClawshotDoorCountEscape"
RECOUNT = ("ClawshotDoorSendoffRecount", "DoorOfTime_SendOff", "Event7", "Event62")  # call, owner, before, after

COMMON_GATE_SHA256 = "5b4152c4e56bf51b7f2400fbdd6a39e4b506f3104cee49a24f6f49e72eb4d6a4"
POOL = 0x24  # u32: the string pool's file offset; the pool runs to the end of the module
NODES, NODE_SIZE = 0x74, 0x3C  # 60-byte node headers: +8 class name and hash, +0x14 parameter descriptor
READER = "HoldGameDataGetBoolSimple"  # node 6: the unused native Bool reader the gate rebinds
STRING_INPUTS = 0x17D8  # 16-byte String input records: name, s16 node, s16 output, flags, default
REBOUND = 0x1D23  # the pool slot the open gate renames
OLD_NAME = b"Market_Child_TimeTempleDoor_Opened\0"
NEW_NAME = b"HavePlayedEvent.Dm_HrlField_0020\0\0\0"
# Every field the open gate may change, from the independent AINB decode: (offset, native, patched).
COMMON_GATE_EDITS = (
    (0x0938, struct.pack("<i", 4), struct.pack("<i", 6)),  # node 5 OR generic plug: event proxy -> reader
    (0x1770, struct.pack("<I", 0x39D), struct.pack("<I", 0x8000039D)),  # node 6 "Bool" output, bit 31 connected
    (0x1898, struct.pack("<hh", 4, 1), struct.pack("<hh", 6, 0)),  # OR source: proxy EventBool -> node 6 Bool
    (0x18A0, struct.pack("<hh", 8, 0), struct.pack("<hh", 6, 0)),  # OR source: Step06 IsAfter -> node 6 Bool
    (0x18A8, struct.pack("<hh", 8, 2), struct.pack("<hh", 6, 0)),  # OR source: Step06 IsEqual -> node 6 Bool
    (0x18FC, struct.pack("<H", 4), struct.pack("<H", 6)),  # node 5 query dependencies: 4, 8, 8 -> 6
    (0x1900, struct.pack("<H", 8), struct.pack("<H", 6)),
    (0x1904, struct.pack("<H", 8), struct.pack("<H", 6)),
    (REBOUND, OLD_NAME, NEW_NAME),  # node 6 GameDataNameBool default: the door's opened flag -> the send-off
)


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


@pytest.fixture(scope="module")
def overlay(romfs, tmp_path_factory):
    """Each mode's standalone overlay, written once: (its romfs folder, the resources write reported)."""
    cache = {}

    def get(mode):
        if mode not in cache:
            out = tmp_path_factory.mktemp(mode) / "out"
            cache[mode] = (out / "romfs", door.write(romfs, out, mode=mode))
        return cache[mode]

    return get


def targets(event):
    """Every event index ``event`` continues to."""
    cases = [target for _, target in getattr(event, "cases", ())]
    return [getattr(event, "next", evfl.NONE), getattr(event, "join", evfl.NONE), *cases, *getattr(event, "forks", ())]


def retarget(event, old, new):
    """Point ``event``'s continuations to ``old`` at ``new`` instead."""
    if getattr(event, "next", None) == old:
        event.next = new
    if isinstance(event, evfl.SwitchEvent):
        event.cases = [(value, new if target == old else target) for value, target in event.cases]


def unpatch_story(native, patched, path, *, mode):
    """``patched`` with exactly ``mode``'s intended edits undone, each checked first; all else must equal ``native``.

    Every mode repairs the DoorOfTime order: the stone-counter entry starts with send-off played, then escape
    unplayed, checks; the send-off calls that entry between Event7 and Event62. Early modes: a guard is a
    GameDataActor query at its writer's index: strictly past the step continues to the native next, otherwise the
    moved native write runs. Song-only also enters through the learned-song and send-off checks and skips the
    stone-quest gate Event60. The shared repair is undone first, so the Event7 guard then shows its native tail."""
    fc = deepcopy(patched.flowchart)
    names = [event.name for event in fc.events]
    count = len(native.flowchart.events)
    guards = GUARDED[path] if mode in EARLY else ()
    assert len(set(names)) == len(names), path
    assert names[:count] == [event.name for event in native.flowchart.events], path
    actors = [i for i, actor in enumerate(fc.actors) if actor.name == "GameDataActor"]
    assert len(actors) == 1, path
    actor, queries = actors[0], fc.actors[actors[0]].queries
    added = set()

    def ask(name, query, params, cases):
        event = fc.events[names.index(name)]
        assert event == evfl.SwitchEvent(name, actor, queries.index(query), cases, params), (path, event)

    def restore(name):
        moved = names.index(f"ClawshotDoor{name}Write")
        added.add(names[moved])
        fc.events[names.index(name)] = replace(fc.events[moved], name=name)
        return fc.events[moved]

    if path == DOOR_FLOW:
        entry_name, first = COUNTER
        escape_check = names.index(COUNT_ESCAPE)
        ask(COUNT_SENDOFF, "EventQueryHavePlayedEvent", {"EventName": "Dm_HrlField_0020"}, [(0, escape_check)])
        escape = {"EventName": "HyruleField_DoorOfTime_Escape"}
        ask(COUNT_ESCAPE, "EventQueryHavePlayedEvent", escape, [(1, names.index(first))])
        counter = fc.entry_point(entry_name)
        assert counter.main_event == names.index(COUNT_SENDOFF), path
        counter.main_event = names.index(first)
        call, owner, before, after = RECOUNT
        for kept in ("Event77", after):  # the stone count's bridge raise and the send-off's Fire write
            assert fc.events[names.index(kept)] == native.flowchart.events[names.index(kept)], (path, kept)
        recount = names.index(call)
        call_event = evfl.SubFlowEvent(call, "", entry_name, names.index(after))
        assert fc.events[recount] == call_event, (path, fc.events[recount])
        assert [entry.name for entry in fc.entry_points if recount in entry.sub_flow_events] == [owner], path
        fc.entry_point(owner).sub_flow_events.remove(recount)
        callers = [i for i, event in enumerate(fc.events) if recount in targets(event)]
        # Closed: the native write continues to the call; early: the guard's past case and the moved write.
        expected_callers = [before, f"ClawshotDoor{before}Write"] if guards else [before]
        assert sorted(names[i] for i in callers) == sorted(expected_callers), path
        for i in callers:
            retarget(fc.events[i], recount, names.index(after))
        added |= {COUNT_SENDOFF, COUNT_ESCAPE, call}
    for writer, step, tail in guards:
        moved = names.index(f"ClawshotDoor{writer}Write")
        cases = [(1, moved)] if tail is None else [(0, names.index(tail)), (1, moved)]
        ask(writer, "EventQueryIsGameDataBoolExp", {"GameDataName": f"DoorOfTime_IsAfter_{step}_Exp"}, cases)
        assert restore(writer).params["StepName"] == step, (path, writer)
    if mode == "song_only" and path == DOOR_FLOW:
        learned, sendoff = names.index("ClawshotDoorLearnedTime"), names.index("ClawshotDoorSendoff")
        added |= {names[learned], names[sendoff]}
        song_params = {"GameDataName": "IsGet.Item_Melody_TimeSong", "Index": -1}
        ask("ClawshotDoorLearnedTime", "EventQueryIsGameDataBool", song_params, [(0, sendoff)])
        sendoff_params = {"GameDataName": "HavePlayedEvent.Dm_HrlField_0020", "Index": -1}
        ask("ClawshotDoorSendoff", "EventQueryIsGameDataBool", sendoff_params, [(0, names.index("Event18"))])
        entry = fc.entry_point("DoorOfTime_OpenDoor")
        assert entry.main_event == learned
        entry.main_event = names.index("Event18")
        predecessor = fc.events[names.index("Event92")]
        assert predecessor.next == names.index("Event69")
        predecessor.next = names.index("Event60")
    assert sorted(names[count:]) == sorted(added), path
    del fc.events[count:]
    return evfl.EventFlowFile(patched.name, fc, patched.timeline)


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
    native = evfl.read(dictionaries.decompress(DOOR_FLOW, (romfs / DOOR_FLOW).read_bytes()))
    # Other entries, grants, first pull, Rauru and repeat travel untouched beyond the guards.
    assert unpatch_story(native, patched, DOOR_FLOW, mode="song_only") == native

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


@pytest.mark.parametrize("mode", MODES)
def test_each_mode_writes_exactly_its_resources(romfs, overlay, mode):
    """Each mode writes its literal set; only its grown files' size entries rise."""
    root, written = overlay(mode)
    expected = sorted(WRITTEN[mode])
    assert sorted(file.path for file in written) == expected
    on_disk = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    assert on_disk == expected
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    native = rstb.read(dictionaries.decompress(SIZE_TABLE, (romfs / SIZE_TABLE).read_bytes()))
    table = rstb.read(dictionaries.decompress(SIZE_TABLE, (root / SIZE_TABLE).read_bytes()))
    assert (table.version, table.names) == (native.version, native.names)
    digests = native.hashes.keys() | table.hashes.keys()
    changed = {digest for digest in digests if native.hashes.get(digest) != table.hashes.get(digest)}
    assert changed == {rstb.path_hash(path) for path in GROWN[mode]}
    for path in GROWN[mode]:
        size = len(dictionaries.decompress(path, (root / path).read_bytes()))
        assert table.get(path) >= rstb.required_size(path, size)


@pytest.mark.parametrize("mode", MODES)
def test_story_flows_change_only_the_intended_events(romfs, overlay, mode):
    """Every mode: the DoorOfTime ordering repair. Early modes add the nine forward-only writers and, song-only,
    the door entry. Nothing else in any written flow."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    root, _ = overlay(mode)
    for path in GUARDED:
        if path not in WRITTEN[mode]:
            continue
        native = evfl.read(dictionaries.decompress(path, (romfs / path).read_bytes()))
        patched = evfl.read(dictionaries.decompress(path, (root / path).read_bytes()))
        assert unpatch_story(native, patched, path, mode=mode) == native, path


def test_open_common_gate_changes_no_byte_outside_its_explicit_fields(romfs, overlay):
    native = (romfs / COMMON_GATE).read_bytes()
    assert hashlib.sha256(native).hexdigest() == COMMON_GATE_SHA256
    root, _ = overlay("open")
    patched = (root / COMMON_GATE).read_bytes()
    assert len(patched) == len(native)
    mask = set()
    for offset, old, new in COMMON_GATE_EDITS:
        field = set(range(offset, offset + len(old)))
        assert len(new) == len(old) and not mask & field, f"{offset:#x}"
        mask |= field
        assert native[offset : offset + len(old)] == old, f"native field {offset:#x}"
        assert patched[offset : offset + len(new)] == new, f"patched field {offset:#x}"
    assert [f"{i:#x}" for i in range(len(native)) if i not in mask and patched[i] != native[i]] == []


def slot_references(module, pool, start, length):
    """Every byte offset whose little-endian u16 names ANY byte of [start, start + length) (the start, an interior
    byte or a suffix), as a pool offset or a file offset. Any u16 or u32 reference, at any alignment, has such a
    window; the whole module is scanned."""
    found = []
    for offset in range(len(module) - 1):
        value = struct.unpack_from("<H", module, offset)[0]
        if start - pool <= value < start - pool + length or start <= value < start + length:
            found.append(offset)
    return found


def text(module, offset):
    return module[offset : module.index(b"\0", offset)].decode()


def test_open_gate_renames_a_pool_slot_only_its_reader_uses(romfs, overlay):
    """No reader of any byte of the renamed pool string but node 6's GameDataNameBool default, before or after.

    A NUL-terminated read reaches a slot byte only by starting inside the slot (every such start is scanned, so
    suffix and interior aliases count) or by starting earlier and running in, which the NUL before it stops."""
    native = (romfs / COMMON_GATE).read_bytes()
    root, _ = overlay("open")
    patched = (root / COMMON_GATE).read_bytes()
    pool = struct.unpack_from("<I", native, POOL)[0]
    assert pool == struct.unpack_from("<I", patched, POOL)[0] == 0x1948
    assert native[-1] == 0 and all(32 <= byte < 127 or byte == 0 for byte in native[pool:]), "pool is only text"
    assert native.count(OLD_NAME[:-1]) == 1 and native[REBOUND : REBOUND + len(OLD_NAME)] == OLD_NAME
    assert native[REBOUND - 1] == 0, "an earlier pool string runs into the slot"
    assert struct.pack("<I", key(OLD_NAME[:-1].decode())) not in native  # nor any hashed reference
    default = STRING_INPUTS + 12
    for module in (native, patched):
        assert slot_references(module, pool, REBOUND, len(OLD_NAME)) == [default]
        header = NODES + NODE_SIZE * 6
        name, digest = struct.unpack_from("<2I", module, header + 8)
        assert (text(module, pool + name), digest) == (READER, key(READER))
        descriptor = struct.unpack_from("<I", module, header + 0x14)[0]
        assert struct.unpack_from("<2I", module, descriptor + 0x60) == (0, 1)  # its one String input: record 0
        name, node, output, flags, value = struct.unpack_from("<IhhII", module, STRING_INPUTS)
        assert text(module, pool + name) == "GameDataNameBool" and pool + value == REBOUND
        assert (node, output, flags) == (-1, 0, 0x800000)  # unwired: it reads its default
    assert text(native, REBOUND) == OLD_NAME[:-1].decode()
    assert text(patched, REBOUND) == "HavePlayedEvent.Dm_HrlField_0020"


def test_open_native_door_and_first_pull_need_no_quest_forgery(romfs, overlay):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    root, _ = overlay("open")
    original = byml.load(dictionaries.decompress(door.PLACEMENT, (romfs / door.PLACEMENT).read_bytes()))
    patched = byml.load(dictionaries.decompress(door.PLACEMENT, (root / door.PLACEMENT).read_bytes()))
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
def test_open_door_waits_for_real_sendoff_not_quest_progress_or_a_scene_request(overlay, sendoff, step, proxy):
    root, _ = overlay("open")
    actual = door_signals((root / COMMON_GATE).read_bytes(), sendoff=sendoff, step=step, proxy=proxy)
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
