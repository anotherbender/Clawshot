"""Early Door of Time story stage: Zelda's escape and the moat Ocarina play in any quest order.

Both early door modes let the first pull write ``Complete`` (song_only's opening already writes ``Step06``)
before the three-stone escape. Four native Hyrule Field modules key the escape and the moat on the exact
quest step (``HoldChallengeCurrentStepCheckOrder`` on DoorOfTime, ``IsEqual`` Step03 or Step04), so any later
step would strand both scenes and their checks. Each such query becomes the native
``HoldGameDataGetBoolExpSimple`` on one of three unsaved BoolExp rows (reset 0, save -1); no saved flag,
default or save layout changes:

- ``ESCAPE_READY`` (owned by ``door_story``): DoorOfTime past Step2_2, the three stone quests Complete, the
  send-off played, the escape unplayed. Read by 0ce5 node3 (the escape area) and 9e35 node3 (its storm).
- ``MOAT_READY``: DoorOfTime past Step03, the same stones and send-off, the escape played, ``Dm_MelodyGet_Time``
  unplayed. Read by 91f9 node0 (the moat Ocarina actor) and 32f7 node5, which was the escape history and now
  drives the moat air wall (node13) and the moat event's AND (node6). Scene histories, never Ocarina or song
  ownership: either gift may be shuffled.
- ``MOAT_AREAS_DONE``: DoorOfTime past Step04 and ``Dm_MelodyGet_Time`` played. Read by 32f7 node4, whose
  output deletes the four moat sensor areas: uncollected, they stay through Step06/Complete, even before the
  escape, while the air wall and the event wait for ``MOAT_READY``.

Native facts, build e0f3ccfa, independently decoded (whole-file SHA-256 pins). The string pool's offset is the
u32 at 0x24. A node header's Name field is a pool-relative class name followed by its murmur3. A String input
record holds its name, source and flags (node -1: its default), and its default; a Bool output word holds its
pool-relative name with bit 31 set when connected. Each substitution is in place, same length: the class
name is rewritten in its own pool slot (35 bytes; the new name needs 29), and the predicate,
``GameDataNameBoolExp`` and ``Bool`` are packed into the old ChallengeName default's slot (58 bytes). The first
String input and Bool output point at them and both counts drop to one; the now-unreferenced records stay.
32f7 node5's own class slot (28 bytes) is too short, so it shares node4's rewritten class, parameter and output
names and takes ``MOAT_READY`` in its old default slot (30 bytes). No other reference points into any
rewritten slot. Source records, node13's generic plug and its query list entry move from node4's IsEqual to
node5. Not a general AINB writer.
"""

import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch.door_story import ESCAPE_READY
from clawshot.patch.gamedata import BuiltFile
from clawshot.patch.plan import PatchError
from clawshot.save import key

MOAT_READY = "Clawshot.Door.MoatReady"  # unsaved BoolExp: the moat Ocarina, its air wall and event may play
MOAT_AREAS_DONE = "Clawshot.Door.MoatAreasDone"  # unsaved BoolExp: the moat sensor areas may go
ESCAPED = "HavePlayedEvent.HyruleField_DoorOfTime_Escape"
COLLECTED = "HavePlayedEvent.Dm_MelodyGet_Time"

_SENDOFF = "HavePlayedEvent.Dm_HrlField_0020"
_AFTER = {step: f"DoorOfTime_IsAfter_{step}_Exp" for step in ("Step2_2", "Step03", "Step04")}  # strictly past
_STONES = {stone: f"Get_StoneOf{stone}_IsCompleted_Exp" for stone in ("Forest", "Fire", "Water")}
_STEP = "Step_DoorOfTime"
_STEPS = (
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
_CHALLENGE = "Work/Challenge/DoorOfTime.game__challenge__Challenge.gyml"
_COMPARATOR = "HoldChallengeCurrentStepCheckOrder"
_CLASS = "HoldGameDataGetBoolExpSimple"
_PARAMETER = "GameDataNameBoolExp"
_OUTPUT = "Bool"
_POOL = 0x24  # u32: the string pool's file offset
_ACTIVE = 1 << 31  # Bool output word: connected
_USES_DEFAULT = (0xFFFF, 0x800000)  # String input: source node -1, output 0; flags
# Native BoolExp postfix opcodes: 0 reads a Bool, 10 a BoolExp, 3 ANDs, 5 negates; 1 (equal) and 12 (after)
# read an Enum against the literal that 2 gives.
_BOOL, _AND, _NOT, _EXPRESSION = 0, 3, 5, 10


def _native_expression(name: str, commands: tuple[tuple[int, str], ...]) -> tuple[str, dict]:
    return "BoolExp", {
        "Hash": byml.U32(key(name)),
        "ResetTypeValue": byml.I32(0),
        "SaveFileIndex": byml.I32(-1),
        "Values": [[byml.U64(op), byml.U64(key(operand))] for op, operand in commands],
    }


def _history(name: str) -> tuple[str, dict]:
    return "Bool", {
        "DefaultValue": False,
        "Hash": byml.U32(key(name)),
        "ResetTypeValue": byml.I32(8),
        "SaveFileIndex": byml.I32(0),
    }


# Every native row the three expressions read, exactly as the game has it.
_SOURCES = {
    **{name: _native_expression(name, ((12, _STEP), (2, step))) for step, name in _AFTER.items()},
    **{
        name: _native_expression(name, ((1, f"Step_Get_StoneOf{stone}"), (2, "Complete")))
        for stone, name in _STONES.items()
    },
    **{name: _history(name) for name in (_SENDOFF, ESCAPED, COLLECTED)},
}
_PREPARED = (*((_EXPRESSION, stone, False) for stone in _STONES.values()), (_BOOL, _SENDOFF, False))
# (opcode, name, negated) reads, ANDed left to right.
_EXPRESSIONS = {
    ESCAPE_READY: ((_EXPRESSION, _AFTER["Step2_2"], False), *_PREPARED, (_BOOL, ESCAPED, True)),
    MOAT_READY: (
        (_EXPRESSION, _AFTER["Step03"], False),
        *_PREPARED,
        (_BOOL, ESCAPED, False),
        (_BOOL, COLLECTED, True),
    ),
    MOAT_AREAS_DONE: ((_EXPRESSION, _AFTER["Step04"], False), (_BOOL, COLLECTED, False)),
}


def _postfix(reads: tuple[tuple[int, str, bool], ...]) -> list[list[byml.U64]]:
    values = []
    for index, (op, name, negated) in enumerate(reads):
        values.append([byml.U64(op), byml.U64(key(name))])
        if negated:
            values.append([byml.U64(_NOT)])
        if index:
            values.append([byml.U64(_AND)])
    return values


def add_expressions(tree: dict) -> None:
    """Append the stage's three unsaved BoolExp rows to a loaded GameDataList root.

    Checks every native row they read (and the DoorOfTime step order) first; refuses a second application or
    a hash already taken. No other row, default or the save layout metadata changes.
    """
    data = tree["Data"]
    for name, (kind, expected) in _SOURCES.items():
        found = [row for row in data[kind] if row.get("Hash") == expected["Hash"]]
        if len(found) != 1 or not byml.same(found[0], expected):
            raise PatchError(f"Door of Time stage: changed native {kind} {name}: {found!r}")
    steps = [row for row in data["Enum"] if row.get("Hash") == key(_STEP)]
    if (
        len(steps) != 1
        or list(steps[0].get("RawValues", ())) != list(_STEPS)
        or list(steps[0].get("Values", ())) != [key(step) for step in _STEPS]
    ):
        raise PatchError(f"Door of Time stage: changed native Enum {_STEP}: {steps!r}")
    added = {key(name): name for name in _EXPRESSIONS}
    if taken := sorted({added[row["Hash"]] for rows in data.values() for row in rows if row.get("Hash") in added}):
        raise PatchError(f"Door of Time stage: GameData already holds {taken} (applied twice or a hash collision)")
    for name, reads in _EXPRESSIONS.items():
        data["BoolExp"].append(
            {
                "Hash": byml.U32(key(name)),
                "ResetTypeValue": byml.I32(0),
                "SaveFileIndex": byml.I32(-1),
                "Values": _postfix(reads),
            }
        )


@dataclass(frozen=True)
class _Query:
    """A native query node rewritten in place as ``HoldGameDataGetBoolExpSimple`` on ``predicate``."""

    predicate: str
    node: int
    name: int  # header Name field: pool-relative class name, then its murmur3
    old_class: str
    string: int  # first String input record: name, source and flags, default
    strings: tuple[tuple[str, str], ...]  # native (name, default) of each String input
    output: int  # first Bool output word
    outputs: tuple[tuple[str, bool], ...]  # native (name, connected) of each Bool output
    string_count: int  # u32 String input count in its parameter descriptor
    output_count: int  # u32 Bool output count in its parameter descriptor


@dataclass(frozen=True)
class _Module:
    path: str
    sha256: str
    nodes: tuple[_Query, ...]  # the first packs the shared names into its default slot; later ones reuse them
    sources: tuple[tuple[int, tuple[int, int], tuple[int, int]], ...] = ()  # s16 node, s16 output: native, new
    plugs: tuple[tuple[int, int, int], ...] = ()  # s32 generic plug node: offset, native, new
    queries: tuple[tuple[int, int, int], ...] = ()  # u16 query list entry: offset, native, new


def _comparator(
    predicate: str,
    node: int,
    name: int,
    string: int,
    step: str,
    output: int,
    counts: tuple[int, int],
    *,
    after_connected: bool = False,
) -> _Query:
    """A DoorOfTime step comparator: inputs ChallengeName and ChallengeStepName ``step``; IsEqual connected."""
    return _Query(
        predicate=predicate,
        node=node,
        name=name,
        old_class=_COMPARATOR,
        string=string,
        strings=(("ChallengeName", _CHALLENGE), ("ChallengeStepName", step)),
        output=output,
        outputs=(("IsAfter", after_connected), ("IsBefore", False), ("IsEqual", True)),
        string_count=counts[0],
        output_count=counts[1],
    )


_MODULES = (
    _Module(  # the escape's ActorArea creation
        "Logic/HyruleField_Child_Prefab_0ce5.logic.module.ainb",
        "517a59804ef86bfd41e8253d629fe3c57602abec07341179b7e48896b74f04c3",
        (_comparator(ESCAPE_READY, 3, 0x130, 0xA54, "Step03", 0xA20, (0x500, 0x4E8)),),
        sources=((0x8BC, (3, 2), (3, 0)),),
    ),
    _Module(  # the moat Ocarina actor's creation
        "Logic/HyruleField_Child_Prefab_91f9.logic.module.ainb",
        "d8ff3f34424ceffb156fa836d10fe520d000bf8ee48e7af786e914841129987d",
        (_comparator(MOAT_READY, 0, 0x7C, 0x57C, "Step04", 0x54C, (0x200, 0x1E8)),),
        sources=((0x510, (0, 2), (0, 0)),),
    ),
    _Module(  # the escape storm's weather area, through its OR
        "Logic/HyruleField_Child_Prefab_9e35.logic.module.ainb",
        "57faaad0de355b77e314b63d81d6a6d25b22fc4e2efa0233563419a8c6b0352a",
        (_comparator(ESCAPE_READY, 3, 0x130, 0x698, "Step03", 0x664, (0x44C, 0x434)),),
        sources=((0x638, (3, 2), (3, 0)),),
    ),
    _Module(  # the moat: four sensor areas' deletion (node4), air wall and event (node5)
        "Logic/HyruleField_Child_Prefab_32f7.logic.module.ainb",
        "06a8c4ecf15d58a9a595d29b3019e788cd155b6509945e45573375597719154c",
        (
            _comparator(MOAT_AREAS_DONE, 4, 0x16C, 0x1140, "Step04", 0x10EC, (0x70C, 0x6F4), after_connected=True),
            _Query(
                predicate=MOAT_READY,
                node=5,
                name=0x1A8,
                old_class="HoldGameDataHavePlayedEvent",
                string=0x1160,
                strings=(("EventName", "HyruleField_DoorOfTime_Escape"),),
                output=0x10F8,
                outputs=(("HavePlayed", True), ("NoPlay", False)),
                string_count=0x7B0,
                output_count=0x798,
            ),
        ),
        sources=((0x1090, (4, 2), (5, 0)), (0x1208, (4, 2), (5, 0))),  # air wall creation; the event AND's third
        plugs=((0xD80, 4, 5),),  # the air wall's generic plug
        queries=((0x1278, 4, 5),),  # the air wall's query list entry, so node5 is evaluated
    ),
)


def _text(data: bytes, offset: int) -> str:
    end = data.find(b"\0", offset)
    return data[offset:end].decode("ascii", "replace") if end >= 0 else "<unterminated>"


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _stage(module: _Module, data: bytes) -> bytes:
    """``data`` with ``module``'s query substitutions and rebinds, the same length, after checking each native
    value it replaces."""
    where = f"Door of Time stage: {module.path}"
    if (digest := hashlib.sha256(data).hexdigest()) != module.sha256:
        raise PatchError(f"{where}: native module fingerprint changed (sha256 {digest})")
    content = bytearray(data)
    pool = _u32(data, _POOL)
    shared = None  # pool indices of the rewritten class, parameter and output names
    for query in module.nodes:
        node = f"{where} node {query.node}"
        class_index, class_hash = struct.unpack_from("<2I", data, query.name)
        found = _text(data, pool + class_index)
        if found != query.old_class or class_hash != key(query.old_class):
            raise PatchError(f"{node}: native class {found!r} (hash {class_hash:#x}), expected {query.old_class!r}")
        strings = []
        for index in range(len(query.strings)):
            name, _, _, default = struct.unpack_from("<4I", data, query.string + 16 * index)
            strings.append((_text(data, pool + name), _text(data, pool + default)))
        wiring = struct.unpack_from("<2I", data, query.string + 4)
        if strings != list(query.strings) or wiring != _USES_DEFAULT:
            raise PatchError(f"{node}: changed native String input {strings!r}, source/flags {wiring}")
        words = struct.unpack_from(f"<{len(query.outputs)}I", data, query.output)
        outputs = [(_text(data, pool + (word & ~_ACTIVE)), bool(word & _ACTIVE)) for word in words]
        if outputs != list(query.outputs):
            raise PatchError(f"{node}: changed native Bool output {outputs!r}")
        counts = (_u32(data, query.string_count), _u32(data, query.output_count))
        if counts != (len(query.strings), len(query.outputs)):
            raise PatchError(f"{node}: changed native String/Bool count {counts}")
        default = _u32(data, query.string + 12)
        slot = len(query.strings[0][1]) + 1
        if shared is None:
            packed = b"".join(name.encode() + b"\0" for name in (query.predicate, _PARAMETER, _OUTPUT))
            class_slot = len(query.old_class) + 1
            if len(packed) > slot or len(_CLASS) + 1 > class_slot:
                raise PatchError(f"{node}: {query.predicate!r} with its names does not fit the native slots")
            content[pool + class_index : pool + class_index + class_slot] = _CLASS.encode().ljust(class_slot, b"\0")
            content[pool + default : pool + default + slot] = packed.ljust(slot, b"\0")
            parameter = default + len(query.predicate) + 1
            shared = (class_index, parameter, parameter + len(_PARAMETER) + 1)
        else:
            predicate = query.predicate.encode() + b"\0"
            if len(predicate) > slot:
                raise PatchError(f"{node}: {query.predicate!r} does not fit the {slot}-byte native default slot")
            content[pool + default : pool + default + slot] = predicate.ljust(slot, b"\0")
        class_index, parameter, output = shared
        struct.pack_into("<2I", content, query.name, class_index, key(_CLASS))
        struct.pack_into("<I", content, query.string, parameter)
        struct.pack_into("<I", content, query.output, output | _ACTIVE)
        struct.pack_into("<I", content, query.string_count, 1)
        struct.pack_into("<I", content, query.output_count, 1)
    for offset, native, new in module.sources:
        if (found := struct.unpack_from("<2h", data, offset)) != native:
            raise PatchError(f"{where}: changed native source record {offset:#x}: {found}, expected {native}")
        struct.pack_into("<2h", content, offset, *new)
    for offset, native, new in module.plugs:
        if (found := struct.unpack_from("<i", data, offset)[0]) != native:
            raise PatchError(f"{where}: changed native generic plug {offset:#x}: node {found}, expected {native}")
        struct.pack_into("<i", content, offset, new)
    for offset, native, new in module.queries:
        if (found := struct.unpack_from("<H", data, offset)[0]) != native:
            raise PatchError(f"{where}: changed native query list entry {offset:#x}: node {found}, expected {native}")
        struct.pack_into("<H", content, offset, new)
    return bytes(content)


def build(romfs: str | Path) -> list[BuiltFile]:
    """The four story modules for both early door modes: same length, within their native allocations."""
    romfs = Path(romfs)
    staged = []
    for module in _MODULES:
        data = (romfs / module.path).read_bytes()
        staged.append((module.path, len(data), _stage(module, data)))
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    built = []
    for path, size, content in staged:
        entry = table.get(path)
        if entry is None or entry < len(content):
            raise PatchError(f"Door of Time stage: {path}: missing/short native allocation {entry!r}")
        built.append(BuiltFile(path, content, size, len(content), entry))
    return built
