"""Early door story stage: Zelda's escape and the moat Ocarina keep working in any quest order.

Both early modes let the first pull write Complete (song_only's opening already writes Step06) before the
three-stone escape. The behavior tests read the door's public ``build``/``changes`` output, or the native
module while the build does not supply it yet, and evaluate every consumer input the stage re-sources
against an independent model of the quest order. Node reads are pinned native layout facts of build
e0f3ccfa (node table, query list, String input and Bool output tables), not a general AINB parser.
"""

import hashlib
import itertools
import struct
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

import pytest

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch import door, door_story
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.plan import PatchError
from clawshot.save import key

EARLY = ("song_only", "open")
STEPS = (
    "NotReady",
    "Ready",
    "Step01",
    "Step02",
    "Step2_1",
    "Srep2_1_1",
    "Step2_2",
    "Step03",
    "Step04",
    "Step05",
    "Step06",
    "Complete",
)
CHALLENGE = "Work/Challenge/DoorOfTime.game__challenge__Challenge.gyml"
SENDOFF = "HavePlayedEvent.Dm_HrlField_0020"
ESCAPED = "HavePlayedEvent.HyruleField_DoorOfTime_Escape"
COLLECTED = "HavePlayedEvent.Dm_MelodyGet_Time"
STONES = ("Step_Get_StoneOfForest", "Step_Get_StoneOfFire", "Step_Get_StoneOfWater")
ESCAPE_READY = door_story.ESCAPE_READY
MOAT_READY = "Clawshot.Door.MoatReady"
MOAT_AREAS_DONE = "Clawshot.Door.MoatAreasDone"
ADDED = (ESCAPE_READY, MOAT_READY, MOAT_AREAS_DONE)
BOOL_EXP = "HoldGameDataGetBoolExpSimple"

POOL, NODES, NODE_SIZE = 0x24, 0x74, 0x3C  # string pool offset field; 60-byte node headers from 0x74
NODE_PARAMS, NODE_QUERIES = 0x14, 0x24  # header: parameter descriptor offset; u16 query base, u16 count
BOOL_OUTPUTS, STRING_INPUTS = 0x48, 0x60  # descriptor: (u32 base, u32 count) into each table


@dataclass(frozen=True)
class Layout:
    path: str
    queries: int  # query list: u16 node, u16 zero
    strings: int  # String inputs: name, s16 source node, s16 output, flags, default (16 bytes)
    outputs: int  # Bool outputs: name, bit 31 active


LAYOUTS = {
    "0ce5": Layout("Logic/HyruleField_Child_Prefab_0ce5.logic.module.ainb", 0xA98, 0xA44, 0x9F8),
    "91f9": Layout("Logic/HyruleField_Child_Prefab_91f9.logic.module.ainb", 0x59C, 0x57C, 0x54C),
    "9e35": Layout("Logic/HyruleField_Child_Prefab_9e35.logic.module.ainb", 0x6DC, 0x678, 0x654),
    "32f7": Layout("Logic/HyruleField_Child_Prefab_32f7.logic.module.ainb", 0x1250, 0x1130, 0x10BC),
}


@dataclass(frozen=True)
class Input:
    module: str
    consumer: int
    source: int  # source record: s16 node, s16 output
    name: str | None  # the Bool input's name (None: one source of a multi-source input)
    plug: int | None  # its generic plug record (s32 node, name), when it has one


ESCAPE_AREA = Input("0ce5", 0, 0x8BC, "Logic_Create", 0x340)  # the escape's trigger area
STORM = Input("9e35", 4, 0x638, "BoolMulti", 0x534)  # OR feeding the storm weather area's creation
OCARINA = Input("91f9", 2, 0x510, "Logic_Create", 0x39C)  # the moat Ocarina actor
AIRWALL = Input("32f7", 13, 0x1090, "Logic_Create", 0xD80)  # the moat air wall
AREAS = (  # the moat sensor areas' deletion
    Input("32f7", 0, 0xEF0, "Logic_Delete", 0x4A8),
    Input("32f7", 10, 0x1010, "Logic_Delete", 0xB58),
    Input("32f7", 11, 0x1040, "Logic_Delete", 0xC14),
    Input("32f7", 12, 0x1070, "Logic_Delete", 0xCD0),
)
MOAT_EVENT = tuple(Input("32f7", 6, source, None, None) for source in (0x11F8, 0x1200, 0x1208))  # OperateAND
EVENT_TRIGGER = Input("32f7", 2, 0xF40, "EventRequestTrigger", 0x5FC)  # the moat event request <- AND True
INPUTS = (ESCAPE_AREA, STORM, OCARINA, AIRWALL, *AREAS, *MOAT_EVENT, EVENT_TRIGGER)


def text(module: bytes, offset: int) -> str:
    return module[offset : module.index(b"\0", offset)].decode()


def u32(module: bytes, offset: int) -> int:
    return struct.unpack_from("<I", module, offset)[0]


def node_query(module: bytes, layout: Layout, node: int) -> tuple[str, dict[str, str], list[tuple[str, bool]]]:
    """A node's class, String inputs (name -> default) and Bool outputs (name, active)."""
    header = NODES + NODE_SIZE * node
    pool = u32(module, POOL)
    name, digest = struct.unpack_from("<2I", module, header + 8)
    cls = text(module, pool + name)
    assert digest == key(cls), f"{layout.path} node {node}: class {cls!r} carries hash {digest:#x}"
    params = u32(module, header + NODE_PARAMS)
    string_base, string_count = struct.unpack_from("<2I", module, params + STRING_INPUTS)
    output_base, output_count = struct.unpack_from("<2I", module, params + BOOL_OUTPUTS)
    strings = {}
    for index in range(string_base, string_base + string_count):
        name, source, _, _, default = struct.unpack_from("<IhhII", module, layout.strings + 16 * index)
        assert source == -1, f"{layout.path} node {node}: String input {index} is wired to node {source}"
        strings[text(module, pool + name)] = text(module, pool + default)
    words = struct.unpack_from(f"<{output_count}I", module, layout.outputs + 4 * output_base)
    return cls, strings, [(text(module, pool + (word & 0x7FFFFFFF)), bool(word >> 31)) for word in words]


@dataclass(frozen=True)
class Story:
    """Primitive saved state: the Door of Time step, the three stone quests and three scene histories."""

    step: str
    stones: tuple[bool, bool, bool] = (True, True, True)
    sendoff: bool = True
    escaped: bool = False
    collected: bool = False

    def state(self) -> dict[str, str | bool]:
        stones = {name: "Complete" if done else "Ready" for name, done in zip(STONES, self.stones, strict=True)}
        histories = {SENDOFF: self.sendoff, ESCAPED: self.escaped, COLLECTED: self.collected}
        return {"Step_DoorOfTime": self.step, **stones, **histories}


def stories():
    for step, stones, sendoff, escaped, collected in itertools.product(
        STEPS, itertools.product((False, True), repeat=3), (False, True), (False, True), (False, True)
    ):
        yield Story(step, stones, sendoff, escaped, collected)


def outcome(escape: bool, moat: bool, gone: bool) -> dict[str, object]:
    return {
        "escape_area": escape,
        "storm": escape,
        "moat_ocarina": moat,
        "moat_airwall": moat,
        "moat_event": moat,
        "areas_gone": (gone,) * len(AREAS),
    }


def expected(story: Story) -> dict[str, object]:
    """Independent model: the escape waits for the counted stones (Step03 or any later step), all three stone
    quests and the send-off, and plays once; the moat follows the escape (Step04 or later), once; its sensor
    areas leave only after the collection, at Step05 or later."""
    at = STEPS.index(story.step)
    prepared = all(story.stones) and story.sendoff
    escape = prepared and at >= STEPS.index("Step03") and not story.escaped
    moat = prepared and at >= STEPS.index("Step04") and story.escaped and not story.collected
    return outcome(escape, moat, at >= STEPS.index("Step05") and story.collected)


def evaluate(rows: dict[str, dict[int, dict]], digest: int, state: dict) -> bool:
    """A GameData BoolExp: 0 Bool, 10 BoolExp, 3 AND, 4 OR, 5 NOT; 1 (equal) or 12 (after) an Enum, then 2 its
    literal. Every Bool and Enum read must be part of the primitive state."""
    names = {key(name): name for name in state}
    commands = list(rows["BoolExp"][digest]["Values"])
    stack: list[bool] = []
    while commands:
        op, *operand = commands.pop(0)
        if op == 0:
            assert operand[0] in rows["Bool"], f"BoolExp {digest:#x} reads a missing Bool {operand[0]:#x}"
            stack.append(state[names[operand[0]]])
        elif op == 10:
            stack.append(evaluate(rows, operand[0], state))
        elif op in (1, 12):
            enum = rows["Enum"][operand[0]]
            literal_op, literal = commands.pop(0)
            assert literal_op == 2, f"BoolExp {digest:#x}: enum read without its literal"
            current = list(enum["RawValues"]).index(state[names[operand[0]]])
            wanted = list(enum["Values"]).index(literal)
            stack.append(current == wanted if op == 1 else current > wanted)
        elif op in (3, 4):
            right, left = stack.pop(), stack.pop()
            stack.append(left and right if op == 3 else left or right)
        elif op == 5:
            stack.append(not stack.pop())
        else:
            pytest.fail(f"BoolExp {digest:#x}: unmodelled opcode {op}")
    assert len(stack) == 1, f"BoolExp {digest:#x} leaves {stack}"
    return stack[0]


def indexed(tree: dict) -> dict[str, dict[int, dict]]:
    return {kind: {int(row["Hash"]): row for row in tree["Data"][kind]} for kind in ("Bool", "BoolExp", "Enum")}


class Stage:
    """One mode's story modules (native where the build supplies none) and its GameData tree."""

    def __init__(self, mode: str, modules: dict[str, bytes], built: dict, tree: dict):
        self.mode, self.modules, self.built, self.tree = mode, modules, built, tree
        self.rows = indexed(tree)

    def source(self, item: Input) -> tuple[int, int]:
        return struct.unpack_from("<hh", self.modules[item.module], item.source)

    def read(self, item: Input, state: dict, *, outside: bool = True) -> bool:
        """The Bool an input sees; its source node must be evaluated (query list) and plugged where it has a plug."""
        module, layout = self.modules[item.module], LAYOUTS[item.module]
        pool = u32(module, POOL)
        node, output = self.source(item)
        where = f"{self.mode} {item}"
        if item.name is not None:
            assert text(module, pool + u32(module, item.source - 4)) == item.name, f"{where}: moved input record"
        base, count = struct.unpack_from("<2H", module, NODES + NODE_SIZE * item.consumer + NODE_QUERIES)
        queries = [struct.unpack_from("<H", module, layout.queries + 4 * i)[0] for i in range(base, base + count)]
        assert node in queries, f"{where}: source node {node} is not evaluated; queries {queries}"
        if item.plug is not None:
            plugged = struct.unpack_from("<i", module, item.plug)[0]
            assert (plugged, text(module, pool + u32(module, item.plug + 4))) == (node, item.name), f"{where}: plug"
        cls, strings, outputs = node_query(module, layout, node)
        assert 0 <= output < len(outputs), f"{where}: output {output} of {outputs}"
        name, active = outputs[output]
        assert active, f"{where}: node {node} output {name!r} is inactive"
        if cls == "HoldActorObserverBySensorHitInfo":
            assert name == "IsNotHit", f"{where}: sensor output {name!r}"
            return outside
        if cls == "OperateAND":
            assert (node, name) == (MOAT_EVENT[0].consumer, "True"), f"{where}: AND {node} output {name!r}"
            return all(self.read(source, state, outside=outside) for source in MOAT_EVENT)
        values = self.native(cls, strings, state)
        assert [name for name, _ in outputs] == list(values), f"{where}: {cls} outputs {outputs}"
        return values[name]

    def native(self, cls: str, strings: dict[str, str], state: dict) -> dict[str, bool]:
        """Outputs of the native query classes, in their native order."""
        if cls == "HoldChallengeCurrentStepCheckOrder":
            assert strings.keys() == {"ChallengeName", "ChallengeStepName"}, strings
            assert strings["ChallengeName"] == CHALLENGE, strings
            at, step = STEPS.index(state["Step_DoorOfTime"]), STEPS.index(strings["ChallengeStepName"])
            return {"IsAfter": at > step, "IsBefore": at < step, "IsEqual": at == step}
        if cls == "HoldGameDataHavePlayedEvent":
            assert strings.keys() == {"EventName"}, strings
            played = state[f"HavePlayedEvent.{strings['EventName']}"]
            return {"HavePlayed": played, "NoPlay": not played}
        if cls == BOOL_EXP:
            assert strings.keys() == {"GameDataNameBoolExp"}, strings
            return {"Bool": evaluate(self.rows, key(strings["GameDataNameBoolExp"]), state)}
        pytest.fail(f"{self.mode}: unmodelled query class {cls} {strings}")

    def signals(self, story: Story, *, outside: bool = True) -> dict[str, object]:
        state = story.state()
        return {
            "escape_area": self.read(ESCAPE_AREA, state),
            "storm": self.read(STORM, state),
            "moat_ocarina": self.read(OCARINA, state),
            "moat_airwall": self.read(AIRWALL, state),
            "moat_event": self.read(EVENT_TRIGGER, state, outside=outside),
            "areas_gone": tuple(self.read(area, state) for area in AREAS),
        }


def native_game_data(romfs: Path) -> bytes:
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    return dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes())


@pytest.fixture(scope="module", params=EARLY)
def stage(request, romfs) -> Stage:
    mode = request.param
    built = {file.path: file for file in door.build(romfs, mode=mode)}
    modules = {
        name: built[layout.path].content if layout.path in built else (romfs / layout.path).read_bytes()
        for name, layout in LAYOUTS.items()
    }
    tree = byml.read(door.changes({}, mode=mode)[GAME_DATA_LIST](native_game_data(romfs)))
    return Stage(mode, modules, built, tree)


CASES = {
    "native escape at Step03": (Story("Step03"), outcome(True, False, False)),
    "native moat at Step04": (Story("Step04", escaped=True), outcome(False, True, False)),
    "native collection at Step05": (Story("Step05", escaped=True, collected=True), outcome(False, False, True)),
    "first pull wrote Complete before the escape": (Story("Complete"), outcome(True, False, False)),
    "song-only opening wrote Step06 before the pull": (Story("Step06"), outcome(True, False, False)),
    "Complete after the escape, moat Ocarina pending": (Story("Complete", escaped=True), outcome(False, True, False)),
    "Complete reload after the collection": (
        Story("Complete", escaped=True, collected=True),
        outcome(False, False, True),
    ),
    "Step06 reload after the collection": (Story("Step06", escaped=True, collected=True), outcome(False, False, True)),
    "stones not yet counted at Step2_2": (Story("Step2_2"), outcome(False, False, False)),
    "Forest stone missing": (Story("Complete", stones=(False, True, True)), outcome(False, False, False)),
    "Fire stone missing": (Story("Complete", stones=(True, False, True)), outcome(False, False, False)),
    "Water stone missing": (Story("Complete", stones=(True, True, False)), outcome(False, False, False)),
    "Fire stone missing after the escape": (
        Story("Complete", stones=(True, False, True), escaped=True),
        outcome(False, False, False),
    ),
    "send-off missing": (Story("Complete", sendoff=False), outcome(False, False, False)),
    "send-off missing after the escape": (Story("Complete", sendoff=False, escaped=True), outcome(False, False, False)),
    "send-off missing at native Step03": (Story("Step03", sendoff=False), outcome(False, False, False)),
}


@pytest.mark.dump
@pytest.mark.parametrize("case", CASES)
def test_escape_and_moat_follow_the_story_in_any_quest_order(stage, case):
    story, want = CASES[case]
    assert stage.signals(story) == want, {"mode": stage.mode, "case": case, "story": story}


@pytest.mark.dump
def test_every_story_state_matches_the_independent_model(stage):
    wrong = []
    for story in stories():
        if (actual := stage.signals(story)) != (want := expected(story)):
            wrong.append((story, actual, want))
        if stage.signals(story, outside=False)["moat_event"]:
            wrong.append((story, "moat event while the player stands in a sensor area"))
    assert not wrong, f"{stage.mode}: {len(wrong)} wrong states, first {wrong[:3]}"


@pytest.mark.dump
def test_moat_gate_and_kept_area_dependencies(stage, romfs):
    """The air wall and the event AND read the moat gate, the areas their own predicate; every other pinned
    source keeps its native node and output, and each module keeps its length."""
    native = {name: (romfs / layout.path).read_bytes() for name, layout in LAYOUTS.items()}
    assert {name: len(module) for name, module in stage.modules.items()} == {n: len(m) for n, m in native.items()}
    gates = {}
    for item in INPUTS:
        node, _ = stage.source(item)
        cls, strings, _ = node_query(stage.modules[item.module], LAYOUTS[item.module], node)
        gates[item] = (cls, strings.get("GameDataNameBoolExp"))
    for item in (ESCAPE_AREA, STORM):
        assert gates[item] == (BOOL_EXP, ESCAPE_READY), (stage.mode, item, gates[item])
    for item in (OCARINA, AIRWALL, *MOAT_EVENT[1:]):
        assert gates[item] == (BOOL_EXP, MOAT_READY), (stage.mode, item, gates[item])
    for item in AREAS:
        assert gates[item] == (BOOL_EXP, MOAT_AREAS_DONE), (stage.mode, item, gates[item])
    assert stage.source(AIRWALL) == stage.source(MOAT_EVENT[1]) == stage.source(MOAT_EVENT[2])
    kept = (*AREAS, MOAT_EVENT[0], EVENT_TRIGGER)
    assert [stage.source(item) for item in kept] == [struct.unpack_from("<hh", native["32f7"], i.source) for i in kept]


@pytest.mark.dump
def test_stage_modules_keep_their_length_and_native_allocation(stage, romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    for layout in LAYOUTS.values():
        assert layout.path in stage.built, f"{stage.mode}: build does not supply {layout.path}"
        file, size = stage.built[layout.path], len((romfs / layout.path).read_bytes())
        assert (file.size, file.new_size, len(file.content)) == (size, size, size)
        assert file.entry == table.get(layout.path) >= size


@pytest.mark.dump
def test_added_rows_are_unsaved_and_every_other_row_is_native(stage, romfs):
    native = byml.read(native_game_data(romfs))
    patched = deepcopy(stage.tree)
    rows = patched["Data"]["BoolExp"]
    added = [row for row in rows if row["Hash"] in {key(name) for name in ADDED}]
    assert sorted(row["Hash"] for row in added) == sorted(key(name) for name in ADDED), added
    for row in added:
        fields = [row["Hash"], row["ResetTypeValue"], row["SaveFileIndex"]]
        assert byml.same(fields, [byml.U32(row["Hash"]), byml.I32(0), byml.I32(-1)]), row
        rows.remove(row)
    old = next(row for row in native["Data"]["BoolExp"] if row["Hash"] == key(door.REACTION))
    new = next(row for row in rows if row["Hash"] == key(door.REACTION))
    new["Values"] = old["Values"]  # the altar reaction is the door mode's own pinned change
    assert byml.same(native, patched)  # every saved flag, default, other row and the save layout metadata


@pytest.mark.dump
def test_closed_door_has_no_story_stage(romfs):
    assert not {file.path for file in door.build(romfs, mode="closed")} & {x.path for x in LAYOUTS.values()}
    assert GAME_DATA_LIST not in door.changes({}, mode="closed")


# Implementation units: synthetic inputs only, the helper imported inside each test.


def synthetic_game_data() -> dict:
    """The native-shaped rows the stage reads, plus unrelated saved and unsaved rows, built here."""

    def enum(name, values):
        return {
            "DefaultValue": byml.U32(key(values[0])),
            "Hash": byml.U32(key(name)),
            "RawValues": list(values),
            "ResetTypeValue": byml.I32(8),
            "SaveFileIndex": byml.I32(0),
            "Values": [byml.U64(key(value)) for value in values],
        }

    def bool_exp(name, values):
        return {
            "Hash": byml.U32(key(name)),
            "ResetTypeValue": byml.I32(0),
            "SaveFileIndex": byml.I32(-1),
            "Values": [[byml.U64(op), byml.U64(key(operand))] for op, operand in values],
        }

    def saved(name, default=False, kind=bool):
        value = default if kind is bool else byml.I32(default)
        return {
            "DefaultValue": value,
            "Hash": byml.U32(key(name)),
            "ResetTypeValue": byml.I32(8),
            "SaveFileIndex": byml.I32(0),
        }

    stone_steps = ("NotReady", "Ready", "Step01", "Complete")
    after = [
        bool_exp(f"DoorOfTime_IsAfter_{step}_Exp", [(12, "Step_DoorOfTime"), (2, step)])
        for step in ("Step2_2", "Step03", "Step04", "Step05")
    ]
    done = [
        bool_exp(f"Get_StoneOf{stone}_IsCompleted_Exp", [(1, f"Step_Get_StoneOf{stone}"), (2, "Complete")])
        for stone in ("Forest", "Fire", "Water")
    ]
    return {
        "Data": {
            "Bool": [saved(SENDOFF), saved("Unrelated.Saved", True), saved(ESCAPED), saved(COLLECTED)],
            "BoolExp": [after[3], *after[:3], *done],
            "Enum": [enum("Step_DoorOfTime", STEPS), *(enum(name, stone_steps) for name in STONES)],
            "Int": [saved("Unrelated.Int", 3, int)],
        },
        "MetaData": {"AllDataSaveOffset": byml.I32(64), "SaveDataOffsetPos": [byml.I32(16)]},
    }


def test_expressions_follow_the_independent_model():
    from clawshot.patch import door_stage

    assert (door_stage.MOAT_READY, door_stage.MOAT_AREAS_DONE) == (MOAT_READY, MOAT_AREAS_DONE)
    tree = synthetic_game_data()
    door_stage.add_expressions(tree)
    rows = indexed(tree)
    wrong = []
    for story in stories():
        want = expected(story)
        actual = {name: evaluate(rows, key(name), story.state()) for name in ADDED}
        model = {ESCAPE_READY: want["escape_area"], MOAT_READY: want["moat_ocarina"]}
        if actual != {**model, MOAT_AREAS_DONE: want["areas_gone"][0]}:
            wrong.append((story, actual))
    assert not wrong, wrong[:3]


def test_expressions_add_only_three_unsaved_rows():
    from clawshot.patch import door_stage

    tree = synthetic_game_data()
    before = deepcopy(tree)
    door_stage.add_expressions(tree)
    native_count = len(before["Data"]["BoolExp"])
    added = tree["Data"]["BoolExp"][native_count:]
    assert [row["Hash"] for row in added] == [key(name) for name in ADDED]
    for row in added:
        assert sorted(row) == ["Hash", "ResetTypeValue", "SaveFileIndex", "Values"]
        fields = [row["Hash"], row["ResetTypeValue"], row["SaveFileIndex"]]
        assert byml.same(fields, [byml.U32(row["Hash"]), byml.I32(0), byml.I32(-1)])
        assert all(isinstance(value, byml.U64) for command in row["Values"] for value in command)
    del tree["Data"]["BoolExp"][native_count:]
    assert byml.same(tree, before)


def _drop(name):
    def mutate(tree):
        for rows in tree["Data"].values():
            rows[:] = [row for row in rows if row["Hash"] != key(name)]

    return mutate


def _edit(kind, name, field, value):
    def mutate(tree):
        next(row for row in tree["Data"][kind] if row["Hash"] == key(name))[field] = value

    return mutate


STALE_GAME_DATA = {
    "Fire stone completion missing": _drop("Get_StoneOfFire_IsCompleted_Exp"),
    "Step03 threshold retargeted": _edit(
        "BoolExp",
        "DoorOfTime_IsAfter_Step03_Exp",
        "Values",
        [[byml.U64(12), byml.U64(key("Step_DoorOfTime"))], [byml.U64(2), byml.U64(key("Step05"))]],
    ),
    "send-off no longer saved": _edit("Bool", SENDOFF, "SaveFileIndex", byml.I32(-1)),
    "escape history default changed": _edit("Bool", ESCAPED, "DefaultValue", True),
    "Door steps reordered": _edit("Enum", "Step_DoorOfTime", "RawValues", [*STEPS[:7], "Step04", "Step03", *STEPS[9:]]),
}


@pytest.mark.parametrize("stale", STALE_GAME_DATA)
def test_expressions_refuse_changed_native_inputs(stale):
    from clawshot.patch import door_stage

    tree = synthetic_game_data()
    STALE_GAME_DATA[stale](tree)
    before = deepcopy(tree)
    with pytest.raises(PatchError, match="changed native"):
        door_stage.add_expressions(tree)
    assert byml.same(tree, before)


@pytest.mark.parametrize("kind", ["Bool", "BoolExp", "Int"])
def test_expressions_refuse_a_taken_hash(kind):
    from clawshot.patch import door_stage

    tree = synthetic_game_data()
    taken = {"Hash": byml.U32(key(MOAT_READY)), "ResetTypeValue": byml.I32(0), "SaveFileIndex": byml.I32(-1)}
    tree["Data"][kind].append(taken)
    with pytest.raises(PatchError, match=MOAT_READY):
        door_stage.add_expressions(tree)


def test_expressions_refuse_a_second_application():
    from clawshot.patch import door_stage

    tree = synthetic_game_data()
    door_stage.add_expressions(tree)
    with pytest.raises(PatchError, match=ESCAPE_READY):
        door_stage.add_expressions(tree)


SYNTHETIC = "Logic/Synthetic_Prefab_0000.logic.module.ainb"
OLD_CLASS = "HoldChallengeCurrentStepCheckOrder"
SYNTHETIC_POOL = 0x100


def synthetic_module() -> tuple[bytearray, dict[str, int]]:
    """A tiny stand-in at its own pinned offsets: one comparator with its String inputs and Bool outputs, and
    one consumer source record. Built here; no game bytes."""
    names = (OLD_CLASS, "ChallengeName", CHALLENGE, "ChallengeStepName", "Step03")
    names += ("IsAfter", "IsBefore", "IsEqual", "Logic_Create")
    blob, index = b"", {}
    for name in names:
        index[name] = len(blob)
        blob += name.encode() + b"\0"
    data = bytearray(SYNTHETIC_POOL + len(blob))
    struct.pack_into("<I", data, POOL, SYNTHETIC_POOL)
    data[SYNTHETIC_POOL:] = blob
    struct.pack_into("<2I", data, 0x40, index[OLD_CLASS], key(OLD_CLASS))
    struct.pack_into("<IhhII", data, 0x60, index["ChallengeName"], -1, 0, 0x800000, index[CHALLENGE])
    struct.pack_into("<IhhII", data, 0x70, index["ChallengeStepName"], -1, 0, 0x800000, index["Step03"])
    struct.pack_into("<3I", data, 0x80, index["IsAfter"], index["IsBefore"], index["IsEqual"] | 1 << 31)
    struct.pack_into("<2I", data, 0x90, 2, 3)  # String input count, Bool output count
    struct.pack_into("<IhhI", data, 0xA0, index["Logic_Create"], 3, 2, 0)  # consumer reads (node 3, IsEqual)
    return data, index


def synthetic_spec(data: bytes, predicate: str = ESCAPE_READY):
    from clawshot.patch import door_stage

    query = door_stage._Query(
        predicate=predicate,
        node=3,
        name=0x40,
        old_class=OLD_CLASS,
        string=0x60,
        strings=(("ChallengeName", CHALLENGE), ("ChallengeStepName", "Step03")),
        output=0x80,
        outputs=(("IsAfter", False), ("IsBefore", False), ("IsEqual", True)),
        string_count=0x90,
        output_count=0x94,
    )
    return door_stage._Module(
        SYNTHETIC, hashlib.sha256(data).hexdigest(), (query,), sources=((0xA4, (3, 2), (3, 0)),), plugs=(), queries=()
    )


def synthetic_romfs(tmp_path: Path, zsdic_pack: bytes, data: bytes, entry: int | None) -> Path:
    root = tmp_path / "romfs"
    dictionaries = zsdic.Dictionaries.from_pack(zsdic_pack)
    table = rstb.ResourceSizeTable()
    if entry is not None:
        table.set(SYNTHETIC, entry)
    files = {
        zsdic.PACK_PATH: zsdic_pack,
        rstb.TABLE_PATH: dictionaries.compress(rstb.TABLE_PATH, rstb.write(table)),
        SYNTHETIC: bytes(data),
    }
    for path, content in files.items():
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_bytes(content)
    return root


def test_build_substitutes_the_query_in_place(tmp_path, zsdic_pack, monkeypatch):
    from clawshot.patch import door_stage

    data, index = synthetic_module()
    monkeypatch.setattr(door_stage, "_MODULES", (synthetic_spec(data),))
    [file] = door_stage.build(synthetic_romfs(tmp_path, zsdic_pack, data, 4096))
    content, pool = file.content, SYNTHETIC_POOL
    assert (file.path, file.size, file.new_size, file.entry) == (SYNTHETIC, len(data), len(data), 4096)
    assert len(content) == len(data)
    name, digest = struct.unpack_from("<2I", content, 0x40)
    assert (name, text(content, pool + name), digest) == (index[OLD_CLASS], BOOL_EXP, 0x5E74D96E)
    parameter, _, _, _, default = struct.unpack_from("<IhhII", content, 0x60)
    assert (text(content, pool + parameter), text(content, pool + default)) == ("GameDataNameBoolExp", ESCAPE_READY)
    word = u32(content, 0x80)
    assert (text(content, pool + (word & 0x7FFFFFFF)), word >> 31) == ("Bool", 1)
    assert struct.unpack_from("<2I", content, 0x90) == (1, 1)
    assert struct.unpack_from("<hh", content, 0xA4) == (3, 0)
    changed = {offset for offset in range(len(data)) if content[offset] != data[offset]}
    default_slot = pool + index[CHALLENGE]
    allowed = {*range(0x44, 0x48), *range(0x60, 0x64), *range(0x80, 0x84), *range(0x90, 0x98), *range(0xA4, 0xA8)}
    allowed |= {*range(pool, pool + len(OLD_CLASS) + 1), *range(default_slot, default_slot + len(CHALLENGE) + 1)}
    assert changed <= allowed, sorted(hex(offset) for offset in changed - allowed)


def _stale_class(data, index):
    data[SYNTHETIC_POOL : SYNTHETIC_POOL + len(OLD_CLASS)] = OLD_CLASS[:-1].encode() + b"X"


def _stale_default(data, index):
    struct.pack_into("<I", data, 0x6C, index["Step03"])


def _stale_wiring(data, index):
    struct.pack_into("<hh", data, 0x64, 2, 0)


def _stale_count(data, index):
    struct.pack_into("<I", data, 0x90, 3)


def _stale_output(data, index):
    struct.pack_into("<I", data, 0x88, index["IsEqual"])


def _stale_source(data, index):
    struct.pack_into("<hh", data, 0xA4, 3, 1)


STALE_MODULES = {
    "class": (_stale_class, "class"),
    "String input default": (_stale_default, "String input"),
    "String input wiring": (_stale_wiring, "String input"),
    "String input count": (_stale_count, "count"),
    "inactive output": (_stale_output, "Bool output"),
    "consumer source": (_stale_source, "source"),
}


@pytest.mark.parametrize("stale", STALE_MODULES)
def test_build_refuses_a_changed_module(tmp_path, zsdic_pack, monkeypatch, stale):
    from clawshot.patch import door_stage

    data, index = synthetic_module()
    mutate, message = STALE_MODULES[stale]
    mutate(data, index)
    monkeypatch.setattr(door_stage, "_MODULES", (synthetic_spec(data),))  # the fingerprint follows the change
    with pytest.raises(PatchError, match=message):
        door_stage.build(synthetic_romfs(tmp_path, zsdic_pack, data, 4096))


def test_build_refuses_an_unpinned_fingerprint(tmp_path, zsdic_pack, monkeypatch):
    from clawshot.patch import door_stage

    data, _ = synthetic_module()
    monkeypatch.setattr(door_stage, "_MODULES", (synthetic_spec(data),))
    data[0x30] ^= 1
    with pytest.raises(PatchError, match="fingerprint"):
        door_stage.build(synthetic_romfs(tmp_path, zsdic_pack, data, 4096))


def test_build_refuses_a_predicate_beyond_the_native_slot(tmp_path, zsdic_pack, monkeypatch):
    from clawshot.patch import door_stage

    data, _ = synthetic_module()
    monkeypatch.setattr(door_stage, "_MODULES", (synthetic_spec(data, "Clawshot.Door." + "Long" * 10),))
    with pytest.raises(PatchError, match="does not fit"):
        door_stage.build(synthetic_romfs(tmp_path, zsdic_pack, data, 4096))


@pytest.mark.parametrize("entry", [None, SYNTHETIC_POOL])
def test_build_refuses_a_missing_or_short_allocation(tmp_path, zsdic_pack, monkeypatch, entry):
    from clawshot.patch import door_stage

    data, _ = synthetic_module()
    monkeypatch.setattr(door_stage, "_MODULES", (synthetic_spec(data),))
    with pytest.raises(PatchError, match="allocation"):
        door_stage.build(synthetic_romfs(tmp_path, zsdic_pack, data, entry))


def test_helper_pins_exactly_the_modules_the_behavior_tests_read():
    from clawshot.patch import door_stage

    assert [module.path for module in door_stage._MODULES] == [layout.path for layout in LAYOUTS.values()]
