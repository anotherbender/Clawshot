"""Ganon's Castle rainbow bridge: native story, distinct owned rewards, or native Gold Skulltula token stock.

    file_changes = changes(mode="medallions", count=4)   # romfs path -> decompressed transform
    built = build(romfs, mode="medallions", count=4)     # the bridge logic module, same length

``vanilla`` (count 0) changes nothing. ``stones`` (0..3), ``medallions`` (0..6, Rauru's Light Medallion included)
and ``rewards`` (0..9) count distinct rewards; ``tokens`` (0..100) counts native token stock, including chests.

Native facts, build e0f3ccfa (r17-dungeon-items.md sections 3-4, r18-rewards.md; reproducers in
``E:/OOTRemake/work/r18-rewards/``). ``GanonCastle_Level_Field_00_Prefab_14ba``: node4
(``HoldGameDataGetBoolExpSimple``) reads ``Defeat_Ganon_IsAfter_Ready_Exp``, node3 ``..._IsAfter_Step01_Exp``,
whose node6 False output node5 ANDs with node4 to create both approach areas and the appear point. Node13 ANDs the
two Player contacts with a player-state query and requests ``GanonCastle_Adult_Field_Rainbow`` (node0); that flow
(``Defeat_Ganon`` Event1) writes Step02 after ``Dm_InsideGanonCastle_0000`` and its EX1. Node10 creates the bridge
from the event's saved history (node8) or the live EX1: the durable latch. Only node4's input changes, to
``ELIGIBLE``, written over its own 31-byte default slot (file 0x15FA). Its record's default word (0x11C4) is the
only reference to any byte of that slot; sensors, player guard, event, upper guard, latch and trials stay native.

Ownership is ``IsGet.<reward>``: saved (reset 8, file 0), set by the game whenever the item enters the pouch
(plans/03-game-data.md section 19). The nine rewards are nonconsumable KeyItems; a Bool counts once however often a
reward is granted. No completion, sage count, awakening, quest or barrier state is read or written. Thresholds are
unsaved BoolExp rows over groups of three (stones; Forest/Fire/Water; Shadow/Spirit/Light): flat "at least k" rows
per group, then one pairwise fold per further group. They stay within the native envelope of all 884 native rows
(at most 26 commands, BoolExp reads nested at most 3 deep; 327 native forward reads show name resolution does not
depend on row order). Count 0 is a tautology: native BoolExp has no literal.

Order: AllSage Event11 is the only ``Defeat_Ganon`` Step01 writer, the rainbow Event1 the only Step02 writer;
castle flows write Step03 to Complete. Natively the bridge needs Step01, so Step01 always precedes Step02. Opened
early, the bridge lets the Temple's Light Arrow scene follow Step02 or any castle step, and whether a progress call
moves a quest back is not established natively (03-game-data.md section 14; a separate rollback action exists).
Event11 therefore becomes a query of native strict ``Defeat_Ganon_IsAfter_Step01_Exp``: past Step01 the flow ends
as it natively does after Event11, otherwise the native write runs (``door_story`` convention). Event10's AllSage
completion runs first, unchanged. The Temple trigger (``Market_Adult_Prefab_c668``) reads only AllSage exactly
Step02, so an early bridge neither blocks nor replays the Light Arrow scene; once past Step01, node3 keeps the
approach and the rainbow from returning. Readers of the earlier Step02 outside the castle: an idle fishing line
(``MiniGame_Fishing`` Event175). Not a general AINB writer.
"""

import hashlib
import struct
from collections.abc import Callable
from itertools import combinations
from pathlib import Path

from clawshot.formats import byml, evfl, rstb, zsdic
from clawshot.patch.gamedata import GAME_DATA_LIST, BuiltFile
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges
from clawshot.save import key

STONES = ("Item_Stone_Forest", "Item_Stone_Fire", "Item_Stone_Water")
MEDALLIONS = (
    "Item_Medal_Forest",
    "Item_Medal_Fire",
    "Item_Medal_Water",
    "Item_Medal_Shadow",
    "Item_Medal_Spirit",
    "Item_Medal_Light",
)
_GROUPS = (("Stones", STONES), ("ForestFireWater", MEDALLIONS[:3]), ("ShadowSpiritLight", MEDALLIONS[3:]))
MODES = {"vanilla": (), "stones": _GROUPS[:1], "medallions": _GROUPS[1:], "rewards": _GROUPS, "tokens": ()}
ELIGIBLE = "Clawshot.BridgeEligible"  # unsaved BoolExp the bridge module's node4 reads
FLOW = "Event/EventFlow/AllSage.bfevfl.zs"
MODULE = "Logic/GanonCastle_Level_Field_00_Prefab_14ba.logic.module.ainb"
TOKEN_STOCK = "PouchData.Item_Token_Gold.StockNum"
# Native MiniGame_DampeRace_IsClearLeastOnce uses NOT(Int < 1): r20-trials.md.
_INT_LESS, _INT_LITERAL = 18, 16

_PREFIX = "Clawshot.Bridge."  # the threshold rows ELIGIBLE reads
# Native BoolExp postfix opcodes: 0 reads a Bool, 10 a BoolExp; 3 ANDs, 4 ORs, 5 negates.
_BOOL, _AND, _OR, _NOT, _EXPRESSION = 0, 3, 4, 5, 10
_STEP = "Step_Defeat_Ganon"
_STEPS = (
    "NotReady",
    "Ready",
    "Step01",
    "Step02",
    "Step03",
    "Step04",
    "Step05",
    "Step06",
    "Step07",
    "Step08",
    "Step09",
    "Complete",
)
PAST_STEP01 = "Defeat_Ganon_IsAfter_Step01_Exp"  # native, strict: Step02 or later
_PAST_STEP01_ROW = {
    "Hash": byml.U32(key(PAST_STEP01)),
    "ResetTypeValue": byml.I32(0),
    "SaveFileIndex": byml.I32(-1),
    "Values": [[byml.U64(12), byml.U64(key(_STEP))], [byml.U64(2), byml.U64(key("Step01"))]],
}

_FLOWCHART = "AllSage"
_CHALLENGE_ACTOR, _STEP_ACTION = "ChallengeSystemActor", "EventExecuteProgressChallengeStep"
_GAME_DATA_ACTOR, _READ_EXPRESSION = "GameDataActor", "EventQueryIsGameDataBoolExp"
_WRITE = {
    "ChallengeName": "Defeat_Ganon",
    "StepName": "Step01",
    "IsWaitEnd": True,
    "IsIgnoreCompletedChallenge": False,
    "IsIgnoreChallengeProgressUI": False,
}
_COMPLETE = {**_WRITE, "ChallengeName": "AllSage", "StepName": "Complete"}
_WRITER, _BEFORE = "Event11", "Event10"
MOVED = "ClawshotBridgeEvent11Write"  # the native Step01 write, appended behind the guard

_SHA256 = "664185f723caca93a62fc13004015ed8e9722303a86fbcb6ec861e6fdd6c112f"
_POOL = 0x24  # u32: the string pool's file offset
_NODE_NAME = 0x164 + 8  # node4 header: pool-relative class name, then its murmur3
_CLASS = "HoldGameDataGetBoolExpSimple"
_RECORD = 0x11B8  # node4's only String input: name, s16 source node, s16 output, flags, default
_USES_DEFAULT = (-1, 0, 0x800000)
_PARAMETER = "GameDataNameBoolExp"
_NATIVE_READ = "Defeat_Ganon_IsAfter_Ready_Exp"


def max_count(mode: str) -> int:
    """The largest valid count of ``mode``: 0, 3, 6, 9 or 100."""
    if mode not in MODES:
        raise PatchError(f"unknown bridge mode {mode!r}")
    if mode == "tokens":
        return 100
    return sum(len(actors) for _, actors in MODES[mode])


def identities(mode: str) -> tuple[str, ...]:
    """The reward actors ``mode`` counts, in group order."""
    max_count(mode)
    return tuple(actor for _, actors in MODES[mode] for actor in actors)


def _check(mode: str, count: int) -> bool:
    """Whether ``mode`` changes the game; refuses an unknown mode or a non-integer/out-of-range count."""
    top = max_count(mode)
    if type(count) is not int or not 0 <= count <= top:
        raise PatchError(f"bridge {mode}: count must be an integer 0..{top}, not {count!r}")
    return mode != "vanilla"


def threshold_rows(mode: str, count: int) -> dict[str, list[list[int]]]:
    """Name -> postfix commands of the unsaved rows; ``ELIGIBLE`` is true exactly when at least ``count`` of
    ``mode``'s rewards were ever acquired. Empty for ``vanilla``."""
    if not _check(mode, count):
        return {}
    if mode == "tokens":
        return {ELIGIBLE: [[_INT_LESS, key(TOKEN_STOCK)], [_INT_LITERAL, count], [_NOT]]}
    groups = MODES[mode]
    if count == 0:
        first = key(f"IsGet.{groups[0][1][0]}")
        return {ELIGIBLE: [[_BOOL, first], [_BOOL, first], [_NOT], [_OR]]}
    rows: dict[str, list[list[int]]] = {}

    def emit(name: str, terms: list[list[tuple[int, str]]]) -> tuple[int, str]:
        """``name`` := OR of the ANDed reads of each term."""
        if name not in rows:
            values = []
            for index, term in enumerate(terms):
                for position, (op, operand) in enumerate(term):
                    values.append([op, key(operand)])
                    if position:
                        values.append([_AND])
                if index:
                    values.append([_OR])
            rows[name] = values
        return _EXPRESSION, name

    def group(i: int, k: int) -> tuple[int, str] | None:
        """At least ``k`` of group ``i``'s rewards; None for 0 (always)."""
        label, actors = groups[i]
        if not k:
            return None
        chosen = combinations(actors, k)
        return emit(f"{_PREFIX}{label}{k}", [[(_BOOL, f"IsGet.{actor}") for actor in pick] for pick in chosen])

    def fold(i: int, k: int) -> tuple[int, str] | None:
        """At least ``k`` of groups 0..``i``'s rewards; None for 0 (always)."""
        if not k or not i:
            return group(i, k)
        below = sum(len(actors) for _, actors in groups[:i])
        terms = []
        for lower in range(max(0, k - len(groups[i][1])), min(k, below) + 1):
            terms.append([read for read in (fold(i - 1, lower), group(i, k - lower)) if read is not None])
        return emit(_PREFIX + "".join(label for label, _ in groups[: i + 1]) + str(k), terms)

    _, top = fold(len(groups) - 1, count)
    rows[ELIGIBLE] = rows.pop(top)  # nothing else reads the top row
    return rows


def add_eligibility(tree: dict, mode: str, count: int) -> None:
    """Append ``mode``'s threshold rows to a loaded GameDataList root.

    Checks first every native row read (each reward's saved ``IsGet``, whose initial value a fast start may set,
    and the strict Step01 expression with its quest Enum that the Temple guard reads); refuses a second application
    or a hash already taken. No other row, default or the save layout metadata changes."""
    rows = threshold_rows(mode, count)
    data = tree["Data"]
    if mode == "tokens":
        # Resolve the same nested path GameDataActor's native token query reads; no new saved field.
        name = "PouchData"
        for member in ("Item_Token_Gold", "StockNum"):
            found = [row for row in data["Struct"] if row["Hash"] == key(name)]
            members = [row for row in found[0]["DefaultValue"] if row["Hash"] == key(member)] if len(found) == 1 else []
            name += "." + member
            if len(members) != 1 or members[0]["Value"] != key(name):
                raise PatchError(f"bridge: changed native token path {name}: {found!r}")
        found = [row for row in data["Int"] if row["Hash"] == key(TOKEN_STOCK)]
        if len(found) != 1 or not byml.same(
            found[0],
            {
                "Hash": byml.U32(key(TOKEN_STOCK)),
                "DefaultValue": byml.I32(0),
                "ResetTypeValue": byml.I32(32),
                "SaveFileIndex": byml.I32(0),
            },
        ):
            raise PatchError(f"bridge: changed native token counter: {found!r}")
    for actor in identities(mode):
        name = f"IsGet.{actor}"
        found = [row for row in data["Bool"] if row.get("Hash") == key(name)]
        native = {"Hash": byml.U32(key(name)), "ResetTypeValue": byml.I32(8), "SaveFileIndex": byml.I32(0)}
        if (
            len(found) != 1
            or type(found[0].get("DefaultValue")) is not bool
            or not byml.same({field: v for field, v in found[0].items() if field != "DefaultValue"}, native)
        ):
            raise PatchError(f"bridge: changed native ownership Bool {name}: {found!r}")
    found = [row for row in data["BoolExp"] if row.get("Hash") == key(PAST_STEP01)]
    if len(found) != 1 or not byml.same(found[0], _PAST_STEP01_ROW):
        raise PatchError(f"bridge: changed native BoolExp {PAST_STEP01}: {found!r}")
    steps = [row for row in data["Enum"] if row.get("Hash") == key(_STEP)]
    if (
        len(steps) != 1
        or list(steps[0].get("RawValues", ())) != list(_STEPS)
        or list(steps[0].get("Values", ())) != [key(step) for step in _STEPS]
    ):
        raise PatchError(f"bridge: changed native Enum {_STEP}: {steps!r}")
    added = {key(name): name for name in rows}
    if taken := sorted({added[row["Hash"]] for entries in data.values() for row in entries if row["Hash"] in added}):
        raise PatchError(f"bridge: GameData already holds {taken} (applied twice or a hash collision)")
    for name, values in rows.items():
        data["BoolExp"].append(
            {
                "Hash": byml.U32(key(name)),
                "ResetTypeValue": byml.I32(0),
                "SaveFileIndex": byml.I32(-1),
                "Values": [
                    [byml.U64(command[0]), byml.I32(command[1])]
                    if command[0] == _INT_LITERAL
                    else [byml.U64(word) for word in command]
                    for command in values
                ],
            }
        )


def _game_data(mode: str, count: int) -> Callable[[bytes], bytes]:
    def transform(data: bytes) -> bytes:
        document = byml.load(data)
        add_eligibility(document.root, mode, count)
        result = byml.dump(document)
        if (difference := byml.difference(document.root, byml.read(result))) is not None:
            raise PatchError(f"bridge: written GameDataList does not read back: {difference}")
        return result

    return transform


def light_arrow_story(data: bytes) -> bytes:
    """``AllSage`` (decompressed) with Event11's Defeat_Ganon Step01 write skipped once the quest is past Step01.

    The writer's index becomes the query, so Event10 and every registration keep their targets; false (case 1)
    runs the appended native write, true has no case and ends the entry, as Event11 natively does."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != _FLOWCHART:
        raise PatchError(f"bridge: {FLOW} holds no {_FLOWCHART} flowchart")
    if any(event.name == MOVED for event in fc.events):
        raise PatchError(f"bridge: {FLOW} is already patched")
    index = {event.name: i for i, event in enumerate(fc.events)}
    if _WRITER not in index or _BEFORE not in index:
        raise PatchError(f"bridge: {FLOW} lacks native {_BEFORE}/{_WRITER}")

    def challenge_write(event: evfl.Event, params: dict, next_index: int) -> bool:
        if not isinstance(event, evfl.ActionEvent):
            return False
        actor = fc.actors[event.actor]
        action = (actor.name, actor.secondary_name, actor.actions[event.action])
        return action == (_CHALLENGE_ACTOR, "", _STEP_ACTION) and event.params == params and event.next == next_index

    at = index[_WRITER]
    write, before = fc.events[at], fc.events[index[_BEFORE]]
    if not challenge_write(write, _WRITE, evfl.NONE) or not challenge_write(before, _COMPLETE, at):
        raise PatchError(f"bridge: changed native {_BEFORE} -> {_WRITER}: {before!r}, {write!r}")
    writers = [
        event.name
        for event in fc.events
        if isinstance(event, evfl.ActionEvent)
        and fc.actors[event.actor].name == _CHALLENGE_ACTOR
        and (event.params or {}).get("ChallengeName") == _WRITE["ChallengeName"]
    ]
    if writers != [_WRITER]:
        raise PatchError(f"bridge: {FLOW} has unknown Defeat_Ganon writes {writers}")
    readers = [i for i, actor in enumerate(fc.actors) if actor.name == _GAME_DATA_ACTOR and not actor.secondary_name]
    if len(readers) != 1:
        raise PatchError(f"bridge: {FLOW} has {len(readers)} plain {_GAME_DATA_ACTOR} actors")
    queries = fc.actors[readers[0]].queries
    if _READ_EXPRESSION not in queries:
        queries.append(_READ_EXPRESSION)
    appended = len(fc.events)
    fc.events[at] = evfl.SwitchEvent(
        _WRITER, readers[0], queries.index(_READ_EXPRESSION), [(1, appended)], {"GameDataName": PAST_STEP01}
    )
    write.name = MOVED
    fc.events.append(write)
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"bridge: {FLOW} does not read back as the edited flow")
    return result


def _text(data: bytes, offset: int) -> str:
    end = data.find(b"\0", offset)
    return data[offset:end].decode("ascii", "replace") if end >= 0 else "<unterminated>"


def stage(data: bytes) -> bytes:
    """The native bridge module with node4 reading ``ELIGIBLE``: same length, one pool slot rewritten."""
    where = f"bridge: {MODULE}"
    if (digest := hashlib.sha256(data).hexdigest()) != _SHA256:
        raise PatchError(f"{where}: native module fingerprint changed (sha256 {digest})")
    pool = struct.unpack_from("<I", data, _POOL)[0]
    class_index, class_hash = struct.unpack_from("<2I", data, _NODE_NAME)
    if _text(data, pool + class_index) != _CLASS or class_hash != key(_CLASS):
        raise PatchError(f"{where}: node4 is no longer {_CLASS}")
    name, source, output, flags, default = struct.unpack_from("<IhhII", data, _RECORD)
    record = (_text(data, pool + name), (source, output, flags), _text(data, pool + default))
    if record != (_PARAMETER, _USES_DEFAULT, _NATIVE_READ):
        raise PatchError(f"{where}: changed node4 String input {record!r}")
    slot, size = pool + default, len(_NATIVE_READ) + 1
    if data[slot - 1] != 0 or len(ELIGIBLE) + 1 > size:
        raise PatchError(f"{where}: {ELIGIBLE!r} does not replace the {size}-byte native slot alone")
    content = bytearray(data)
    content[slot : slot + size] = ELIGIBLE.encode().ljust(size, b"\0")
    return bytes(content)


def changes(*, mode: str = "vanilla", count: int = 0) -> FileChanges:
    """Decompressed transforms for ``clawshot.patch.write``; vanilla changes nothing."""
    if not _check(mode, count):
        return {}
    return {GAME_DATA_LIST: _game_data(mode, count), FLOW: light_arrow_story}


def build(romfs: str | Path, *, mode: str = "vanilla", count: int = 0) -> list[BuiltFile]:
    """The bridge module for an ownership mode, within its native allocation; vanilla builds nothing."""
    if not _check(mode, count):
        return []
    romfs = Path(romfs)
    data = (romfs / MODULE).read_bytes()
    content = stage(data)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    entry = table.get(MODULE)
    if entry is None or entry < len(content):
        raise PatchError(f"bridge: {MODULE}: missing/short native allocation {entry!r}")
    return [BuiltFile(MODULE, content, len(data), len(content), entry)]
