"""Native door overlays: behavioral flow oracle, exact inverse edits, exact written sets and byte masks."""

import hashlib
import itertools
import struct
from copy import deepcopy
from dataclasses import replace

import pytest
from test_door import run_open_flow
from test_door_stage import ARRIVED, CHALLENGE, CLOCK_READY, STEPS, Layout, Stage, evaluate, indexed, node_query

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
ERA_FLOW = "Event/EventFlow/Market_Adult_Field_AdultToChild.bfevfl.zs"
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
# Per mode, the only size-table entries that rise. Closed ships just the shared DoorOfTime ordering repair and the
# two clock transitions (in the send-off and in the Temple's era change).
GROWN = {
    "closed": (DOOR_FLOW, ERA_FLOW),
    "song_only": (DOOR_FLOW, SARIA_FLOW, ZELDA_FLOW, ERA_FLOW, GAME_DATA),
    "open": (DOOR_FLOW, SARIA_FLOW, ZELDA_FLOW, ERA_FLOW, GAME_DATA),
}
# Goto_HyruleCastle (the courtyard's forced Step01 reset) stays native, so no mode writes it.
WRITTEN = {
    "closed": (*GROWN["closed"], SIZE_TABLE),
    "song_only": (*GROWN["song_only"], *STAGE_MODULES, SIZE_TABLE),
    "open": (*GROWN["open"], *STAGE_MODULES, SIZE_TABLE, CHILD_MARKET, COMMON_GATE),
}
FOREST = ("Step_Get_StoneOfForest", "GoInside")  # the Kokiri Emerald quest, still incomplete

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
FIRST_ADULT = "HrlField_HasEnteredFirstTime_Adult"  # the first adult Field arrival's clock hold (B)
# Every mode's forward-only clock transitions, flow -> (query, its write, flag, value written, continuation): the
# send-off sets a missed Field owl arrival after its Step02 write (Event7), before the recount; the Temple's
# adult-to-child era change clears a set first-adult hold after its childhood write Event1, before Event0's travel.
CLOCK = {
    DOOR_FLOW: ("ClawshotClockArrival", "ClawshotClockArrived", ARRIVED, True, RECOUNT[0]),
    ERA_FLOW: ("ClawshotClockChildReturn", "ClawshotClockReturnedChild", FIRST_ADULT, False, "Event0"),
}

COMMON_GATE_SHA256 = "5b4152c4e56bf51b7f2400fbdd6a39e4b506f3104cee49a24f6f49e72eb4d6a4"
POOL = 0x24  # u32: the string pool's file offset; the pool runs to the end of the module
NODES, NODE_SIZE = 0x74, 0x3C  # 60-byte node headers: +8 class name and hash, +0x24 query base and count
GATE_LAYOUT = Layout(COMMON_GATE, 0x18E8, 0x17D8, 0x1734)  # query list, String input records, Bool output words
OR_NODE, CLOCK_NODE = 5, 8  # OperateORFixInputTrue; the Door quest's Step06 comparator, then the clock reader
OR_SOURCES, OR_PLUG = (0x1898, 0x18A0, 0x18A8), 0x938  # the OR's three source records and its generic plug
DOOR_INPUTS = (0x1478, 0x1488)  # ActorLogicGateDoor isOpen and IsSkipAnim source records
COMPARATOR, READER = "HoldChallengeCurrentStepCheckOrder", "HoldGameDataGetBoolExpSimple"
CLASS_SLOT, DEFAULT_SLOT = 0x1A0C, 0x1D54  # node 8's class name and ChallengeName default pool slots
CLASS_TEXT, DEFAULT_TEXT = COMPARATOR.encode() + b"\0", CHALLENGE.encode() + b"\0"
PACKED = b"".join(name.encode() + b"\0" for name in (CLOCK_READY, "GameDataNameBoolExp", "Bool"))
# Every field the open gate may change, from the independent AINB decode: (offset, native, patched).
COMMON_GATE_EDITS = (
    (0x0260, struct.pack("<I", key(COMPARATOR)), struct.pack("<I", key(READER))),  # node 8 class hash
    (0x0938, struct.pack("<i", 4), struct.pack("<i", 8)),  # node 5 OR generic plug: event proxy -> node 8
    (0x0AE0, struct.pack("<I", 3), struct.pack("<I", 1)),  # node 8 Bool output count
    (0x0AF8, struct.pack("<I", 2), struct.pack("<I", 1)),  # node 8 String input count
    (0x177C, struct.pack("<I", 0x800003A2), struct.pack("<I", 0x80000439)),  # node 8 output 0: IsAfter -> Bool
    (0x17E8, struct.pack("<I", 0x3FE), struct.pack("<I", 0x425)),  # node 8 input 0: ChallengeName -> the BoolExp's
    (0x1898, struct.pack("<hh", 4, 1), struct.pack("<hh", 8, 0)),  # OR source: proxy EventBool -> node 8 Bool
    (0x18A8, struct.pack("<hh", 8, 2), struct.pack("<hh", 8, 0)),  # OR source: Step06 IsEqual -> node 8 Bool
    (0x18FC, struct.pack("<H", 4), struct.pack("<H", 8)),  # node 5 query list: 4, 8, 8 -> 8, 8, 8
    (CLASS_SLOT, CLASS_TEXT, READER.encode().ljust(len(CLASS_TEXT), b"\0")),
    (DEFAULT_SLOT, DEFAULT_TEXT, PACKED.ljust(len(DEFAULT_TEXT), b"\0")),  # the predicate, parameter, output names
)


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
    unplayed, checks; the send-off calls that entry between Event7 and Event62. Every mode's clock transitions
    (``CLOCK``): a GameDataActor Bool query whose callers are the native predecessor's; the flag already at its
    value continues, otherwise the write runs first. Early modes: a guard is a GameDataActor query at its writer's
    index: strictly past the step continues to the native next, otherwise the moved native write runs. Song-only also
    enters through the learned-song and clock-gate checks and skips the stone-quest gate Event60. The clock
    transition and shared repair are undone first, so the Event7 guard then shows its native tail."""
    fc = deepcopy(patched.flowchart)
    names = [event.name for event in fc.events]
    count = len(native.flowchart.events)
    guards = GUARDED.get(path, ()) if mode in EARLY else ()
    assert len(set(names)) == len(names), path
    assert names[:count] == [event.name for event in native.flowchart.events], path
    actors = [i for i, actor in enumerate(fc.actors) if actor.name == "GameDataActor"]
    assert len(actors) == 1, path
    actor, queries = actors[0], fc.actors[actors[0]].queries
    added = set()
    call, owner, before, after = RECOUNT
    # Closed: the native Event7 write continues to the send-off's added events; early: the guard's past case and the
    # moved write.
    predecessors = sorted([before, f"ClawshotDoor{before}Write"] if guards else [before])

    def ask(name, query, params, cases):
        event = fc.events[names.index(name)]
        assert event == evfl.SwitchEvent(name, actor, queries.index(query), cases, params), (path, event)

    def restore(name):
        moved = names.index(f"ClawshotDoor{name}Write")
        added.add(names[moved])
        fc.events[names.index(name)] = replace(fc.events[moved], name=name)
        return fc.events[moved]

    def callers(index):
        return [i for i, event in enumerate(fc.events) if index in targets(event)]

    if path in CLOCK:
        query, setter, flag, value, then = CLOCK[path]
        check, sets, resume = names.index(query), names.index(setter), names.index(then)
        params = {"GameDataName": flag, "Index": -1}
        ask(query, "EventQueryIsGameDataBool", params, [(0, resume), (1, sets)] if value else [(0, sets), (1, resume)])
        action = fc.actors[actor].actions.index("EventTriggerSetGameDataBool")
        assert fc.events[sets] == evfl.ActionEvent(setter, actor, action, resume, {**params, "Value": value}), path
        assert callers(sets) == [check], path
        found = callers(check)
        assert sorted(names[i] for i in found) == (predecessors if path == DOOR_FLOW else ["Event1"]), path
        for i in found:
            retarget(fc.events[i], check, resume)
        fc.events[check].cases, fc.events[sets].next = [], evfl.NONE  # detached; dropped with every addition
        added |= {query, setter}
    if path == DOOR_FLOW:
        entry_name, first = COUNTER
        escape_check = names.index(COUNT_ESCAPE)
        ask(COUNT_SENDOFF, "EventQueryHavePlayedEvent", {"EventName": "Dm_HrlField_0020"}, [(0, escape_check)])
        escape = {"EventName": "HyruleField_DoorOfTime_Escape"}
        ask(COUNT_ESCAPE, "EventQueryHavePlayedEvent", escape, [(1, names.index(first))])
        counter = fc.entry_point(entry_name)
        assert counter.main_event == names.index(COUNT_SENDOFF), path
        counter.main_event = names.index(first)
        for kept in ("Event77", after):  # the stone count's bridge raise and the send-off's Fire write
            assert fc.events[names.index(kept)] == native.flowchart.events[names.index(kept)], (path, kept)
        recount = names.index(call)
        call_event = evfl.SubFlowEvent(call, "", entry_name, names.index(after))
        assert fc.events[recount] == call_event, (path, fc.events[recount])
        assert [entry.name for entry in fc.entry_points if recount in entry.sub_flow_events] == [owner], path
        fc.entry_point(owner).sub_flow_events.remove(recount)
        found = callers(recount)
        assert sorted(names[i] for i in found) == predecessors, path
        for i in found:
            retarget(fc.events[i], recount, names.index(after))
        added |= {COUNT_SENDOFF, COUNT_ESCAPE, call}
    for writer, step, tail in guards:
        moved = names.index(f"ClawshotDoor{writer}Write")
        cases = [(1, moved)] if tail is None else [(0, names.index(tail)), (1, moved)]
        ask(writer, "EventQueryIsGameDataBoolExp", {"GameDataName": f"DoorOfTime_IsAfter_{step}_Exp"}, cases)
        assert restore(writer).params["StepName"] == step, (path, writer)
    if mode == "song_only" and path == DOOR_FLOW:
        learned, clock = names.index("ClawshotDoorLearnedTime"), names.index("ClawshotDoorClockReady")
        added |= {names[learned], names[clock]}
        song_params = {"GameDataName": "IsGet.Item_Melody_TimeSong", "Index": -1}
        ask("ClawshotDoorLearnedTime", "EventQueryIsGameDataBool", song_params, [(0, clock)])
        clock_params = {"GameDataName": CLOCK_READY}  # the native stone gate Event60's query, on the clock gate
        ask("ClawshotDoorClockReady", "EventQueryIsGameDataBoolExp", clock_params, [(0, names.index("Event18"))])
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
    native_game = byml.load(dictionaries.decompress(door.GAME_DATA_LIST, (romfs / door.GAME_DATA_LIST).read_bytes()))
    new_game = byml.load(
        dictionaries.decompress(door.GAME_DATA_LIST, (out / "romfs" / door.GAME_DATA_LIST).read_bytes())
    )
    rows = indexed(new_game.root)

    def expression(name, state):  # the written GameData's own BoolExp rows
        return evaluate(rows, key(name), state)

    # The Forest stone quest stays incomplete throughout: the door needs the owl arrival and the send-off, not it.
    # The send-off left the Door quest at Step02, so the opening's forward-only Step06 guard writes.
    for learned, recommended, opened, arrived, sendoff in itertools.product((False, True), repeat=5):
        state = {door.TIME_SONG: learned, door.OPENED: opened, ARRIVED: arrived, door.SENDOFF: sendoff}
        state |= {FOREST[0]: FOREST[1], "Step_DoorOfTime": "Step02"}
        scenes, writes = run_open_flow(patched.flowchart, state, expression=expression, recommended=recommended)
        success = learned and recommended and not opened and arrived and sendoff
        assert scenes == (["Dm_TimeTemple_0010"] if success else []), state
        assert (door.OPENED in writes) == success
        assert ("Step_DoorOfTime" in writes) == success
        assert not {ARRIVED, door.SENDOFF} & set(writes), "the door forges a clock input"
        assert not any(name.startswith("Step_Get_Stone") or name.startswith("IsGet.") for name in writes)
        if success:
            assert state["Step_DoorOfTime"] == "Step06"
            assert run_open_flow(patched.flowchart, deepcopy(state), expression=expression) == ([], [])
    # The altar's song reaction is invalid once opened or while the clock waits.
    for opened, arrived, sendoff in itertools.product((False, True), repeat=3):
        state = {door.OPENED: opened, ARRIVED: arrived, door.SENDOFF: sendoff, FOREST[0]: FOREST[1]}
        assert expression(door.REACTION, state) is (opened or not (arrived and sendoff)), state
    native = evfl.read(dictionaries.decompress(DOOR_FLOW, (romfs / DOOR_FLOW).read_bytes()))
    # Other entries, grants, first pull, Rauru and repeat travel untouched beyond the guards.
    assert unpatch_story(native, patched, DOOR_FLOW, mode="song_only") == native

    assert new_game.byte_order == native_game.byte_order
    native_hashes = {row["Hash"] for row in native_game.root["Data"]["BoolExp"]}
    added = [row for row in new_game.root["Data"]["BoolExp"] if row["Hash"] not in native_hashes]
    gates = (door_story.ESCAPE_READY, door_stage.MOAT_READY, door_stage.MOAT_AREAS_DONE, door_stage.CLOCK_READY)
    assert {row["Hash"] for row in added} == {key(name) for name in (age.SHEIK_PRESENCE, *gates)}
    assert all(row["SaveFileIndex"] == -1 and row["ResetTypeValue"] == 0 for row in added)
    new_game.root["Data"]["BoolExp"][:] = [
        row for row in new_game.root["Data"]["BoolExp"] if row["Hash"] in native_hashes
    ]
    old_reaction = next(row for row in native_game.root["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
    new_reaction = next(row for row in new_game.root["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
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
    """Every mode: the DoorOfTime ordering repair and the two clock transitions. Early modes add the nine
    forward-only writers and, song-only, the door entry. Nothing else in any written flow."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    root, _ = overlay(mode)
    for path in (*GUARDED, ERA_FLOW):
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


def string_references(module, start, length):
    """Every 4-aligned u32 before the pool that names ANY byte of [start, start + length) (the start, an interior
    byte or a suffix), as a pool offset or a file offset; bit 31 (a Bool output's connected flag) is masked. Every
    string reference this module holds is such a word (all 171 string reads of the independent decode)."""
    pool = struct.unpack_from("<I", module, POOL)[0]
    found = []
    for offset in range(0, pool, 4):
        value = struct.unpack_from("<I", module, offset)[0] & 0x7FFFFFFF
        if start - pool <= value < start - pool + length or start <= value < start + length:
            found.append(offset)
    return found


def test_open_gate_rewrites_pool_slots_only_its_node_reads(romfs, overlay):
    """No reader of any byte of node 8's class name and ChallengeName default slots but node 8, before or after;
    afterwards its one String input and Bool output also name the parameter and output packed after the predicate.

    A NUL-terminated read reaches a slot byte only by starting inside the slot (every such start is scanned, so
    suffix and interior aliases count) or by starting earlier and running in, which the NUL before it stops."""
    native = (romfs / COMMON_GATE).read_bytes()
    root, _ = overlay("open")
    patched = (root / COMMON_GATE).read_bytes()
    pool = struct.unpack_from("<I", native, POOL)[0]
    assert pool == struct.unpack_from("<I", patched, POOL)[0] == 0x1948
    assert native[-1] == 0 and all(32 <= byte < 127 or byte == 0 for byte in native[pool:]), "pool is only text"
    for slot, content in ((CLASS_SLOT, CLASS_TEXT), (DEFAULT_SLOT, DEFAULT_TEXT)):
        assert native.count(content[:-1]) == 1 and native[slot : slot + len(content)] == content, f"{slot:#x}"
        assert native[slot - 1] == 0, f"an earlier pool string runs into the slot at {slot:#x}"
    header = NODES + NODE_SIZE * CLOCK_NODE
    comparator = struct.pack("<I", key(COMPARATOR))
    assert [i for i in range(len(native) - 3) if native[i : i + 4] == comparator] == [header + 12]  # its own hash
    assert struct.pack("<I", key(CHALLENGE)) not in native
    descriptor = struct.unpack_from("<I", native, header + 0x14)[0]
    record = GATE_LAYOUT.strings + 16 * struct.unpack_from("<I", native, descriptor + 0x60)[0]  # first String input
    word = GATE_LAYOUT.outputs + 4 * struct.unpack_from("<I", native, descriptor + 0x48)[0]  # first Bool output
    for module, defaults in ((native, [record + 12]), (patched, [word, record, record + 12])):
        assert string_references(module, CLASS_SLOT, len(CLASS_TEXT)) == [header + 8]
        assert string_references(module, DEFAULT_SLOT, len(DEFAULT_TEXT)) == defaults


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


def door_signals(module, stage, state, *, proxy):
    """The door's isOpen and IsSkipAnim: node 5's OR (its True output) over its three source records, each read
    through its node's query list, plug, class and output; ``proxy`` is the stone scene's request (EventBool).
    The comparator and BoolExp reader evaluate as in the stage tests (``Stage.native``, on ``stage``'s GameData).
    The native OR also drives IsSkipAnim: automatic opening must not run the stone scene."""
    base, count = struct.unpack_from("<2H", module, NODES + NODE_SIZE * OR_NODE + 0x24)
    queries = [struct.unpack_from("<H", module, GATE_LAYOUT.queries + 4 * i)[0] for i in range(base, base + count)]
    sources = [struct.unpack_from("<hh", module, offset) for offset in OR_SOURCES]
    assert struct.unpack_from("<i", module, OR_PLUG)[0] == sources[0][0], "stale OR plug"
    values = []
    for node, output in sources:
        assert node in queries, f"OR input node {node} is not evaluated; queries {queries}"
        cls, strings, outputs = node_query(module, GATE_LAYOUT, node)
        name, active = outputs[output]
        assert active, f"node {node} output {name!r} is inactive"
        if cls == "ActorLogicEventProxyRequestActor":
            assert name == "EventBool", name
            values.append(proxy)
        else:
            values.append(stage.native(cls, strings, state)[name])
    for offset in DOOR_INPUTS:
        assert struct.unpack_from("<hh", module, offset) == (OR_NODE, 1)  # the OR's True output
    return (any(values),) * len(DOOR_INPUTS)


def test_door_signals_read_the_native_door(romfs):
    """The evaluator's own oracle check on the unpatched module: the stone scene's request, or the Door quest at
    Step06 or later, opens the native door."""
    native = (romfs / COMMON_GATE).read_bytes()
    assert hashlib.sha256(native).hexdigest() == COMMON_GATE_SHA256
    stage = Stage("native", {}, {}, {"Data": {"Bool": [], "BoolExp": [], "Enum": []}})
    for step, proxy in itertools.product(STEPS, (False, True)):
        want = proxy or STEPS.index(step) >= STEPS.index("Step06")
        assert door_signals(native, stage, {"Step_DoorOfTime": step}, proxy=proxy) == (want, want), (step, proxy)


@pytest.mark.parametrize("arrived,sendoff", itertools.product((False, True), repeat=2))
def test_open_door_opens_on_the_field_clock_alone(romfs, overlay, arrived, sendoff):
    """Open mode's written door module and GameData, the Forest stone quest incomplete: the owl arrival and the
    send-off together open the door at every Door step, scene request or not; either alone keeps it shut."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    root, _ = overlay("open")
    module = (root / COMMON_GATE).read_bytes()
    stage = Stage("open", {}, {}, byml.read(dictionaries.decompress(GAME_DATA, (root / GAME_DATA).read_bytes())))
    for step, proxy in itertools.product(STEPS, (False, True)):
        state = {"Step_DoorOfTime": step, FOREST[0]: FOREST[1], ARRIVED: arrived, door.SENDOFF: sendoff}
        actual = door_signals(module, stage, state, proxy=proxy)
        assert actual == (arrived and sendoff,) * 2, {"step": step, "proxy": proxy, "signals": actual}


def test_open_auto_gate_disables_the_later_song_scene(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(door.GAME_DATA_LIST, (romfs / door.GAME_DATA_LIST).read_bytes())
    rows = indexed(byml.read(door.changes({}, mode="open")[door.GAME_DATA_LIST](raw)))
    # At Step05, unopened is normally a valid song trigger even if the open-mode
    # physical gate already opened. No once flag/quest must be forged to disable it.
    for opened in (False, True):
        assert evaluate(rows, key(door.REACTION), {door.OPENED: opened}) is True
