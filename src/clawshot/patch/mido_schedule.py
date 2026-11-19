"""Keep Mido's equipment Talk available when Zelda is met before his wall clears (#35).

Only the completed-castle schedule changes. Its short predicate fits the original
BGYML allocation; the unsaved BoolExp composes through the ordinary GameData writer.
"""

from pathlib import Path

from clawshot.formats import byml, rstb, zsdic
from clawshot.patch.gamedata import GAME_DATA_LIST, BuiltFile
from clawshot.patch.mido import BLOCKER
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges
from clawshot.save import key

SCHEDULE = "Component/AIScheduleParam/Npc_Kokiri_Mido_Child.game__component__AIScheduleParam.bgyml"
CASTLE_COMPLETE = "Goto_HyruleCastle_IsCompleted_Exp"
AFTER_CLEAR = "Clawshot.Mido.AfterClear"
CASTLE_STEP = "Step_Goto_HyruleCastle"
_STEPS = (
    "NotReady",
    "Ready",
    "Step01",
    "Step02",
    "Step02_01",
    "Step03",
    "Step03_01",
    "Step03_02",
    "Step04",
    "Complete",
)
_TALK = "Work/Event/EventSetting/Npc_Kokiri_Mido_Child_C5_T.engine__event__EventSettingParam.gyml"


def _expression(name: str, commands: list[list[int]]) -> dict:
    return {
        "Hash": byml.U32(key(name)),
        "ResetTypeValue": byml.I32(0),
        "SaveFileIndex": byml.I32(-1),
        "Values": [[byml.U64(value) for value in command] for command in commands],
    }


def _written(document: byml.Document) -> bytes:
    result = byml.dump(document)
    if difference := byml.difference(document.root, byml.read(result)):
        raise PatchError(f"Mido schedule: BYML failed read-back: {difference}")
    return result


def guard_schedule(data: bytes) -> bytes:
    """Replace only the native C5 condition; preserve all other rows, actions and entries."""
    document = byml.load(data)
    rows = [row for row in document.root["ConditionalSchedule"] if row.get("ConditionFlag") == CASTLE_COMPLETE]
    if len(rows) != 1:
        raise PatchError(f"Mido schedule: expected one completed-castle row: {rows!r}")
    row = rows[0]
    if (
        not any(event.get("EventName") == _TALK for event in row.get("EventEntry", ()))
        or len(row.get("ActionSchedule", ())) != 1
        or row["ActionSchedule"][0].get("ActionType") != key("Action4")
    ):
        raise PatchError(f"Mido schedule: changed native C5 action/entry: {row!r}")
    row["ConditionFlag"] = AFTER_CLEAR
    result = _written(document)
    if len(result) > len(data):
        raise PatchError(f"Mido schedule: native-size rewrite grew {len(data)} -> {len(result)} bytes")
    return result


def add_expression(data: bytes) -> bytes:
    """Add one unsaved native postfix expression, without changing saved rows or defaults."""
    document = byml.load(data)
    rows = document.root["Data"]
    sources = {
        "BoolExp": (CASTLE_COMPLETE, _expression(CASTLE_COMPLETE, [[1, key(CASTLE_STEP)], [2, key("Complete")]])),
        "Bool": (
            BLOCKER,
            {
                "DefaultValue": True,
                "Hash": byml.U32(key(BLOCKER)),
                "ResetTypeValue": byml.I32(8),
                "SaveFileIndex": byml.I32(0),
            },
        ),
    }
    for kind, (name, expected) in sources.items():
        found = [row for row in rows[kind] if row.get("Hash") == key(name)]
        if len(found) != 1 or not byml.same(found[0], expected):
            raise PatchError(f"Mido schedule: changed native {kind} {name}: {found!r}")
    steps = [row for row in rows["Enum"] if row.get("Hash") == key(CASTLE_STEP)]
    if (
        len(steps) != 1
        or steps[0].get("RawValues") != list(_STEPS)
        or steps[0].get("Values") != [key(step) for step in _STEPS]
    ):
        raise PatchError(f"Mido schedule: changed native castle steps: {steps!r}")
    if any(row.get("Hash") == key(AFTER_CLEAR) for entries in rows.values() for row in entries):
        raise PatchError(f"Mido schedule: {AFTER_CLEAR} already exists (duplicate application or hash collision)")
    # Native postfix: read BoolExp, read saved Bool, NOT, AND. No saved repair flag.
    rows["BoolExp"].append(_expression(AFTER_CLEAR, [[10, key(CASTLE_COMPLETE)], [0, key(BLOCKER)], [5], [3]]))
    return _written(document)


def changes(*, kept: bool) -> FileChanges:
    return {GAME_DATA_LIST: add_expression} if kept else {}


def build(romfs: str | Path, *, kept: bool) -> list[BuiltFile]:
    """Keep the measured native schedule allocation; never infer a general BGYML formula."""
    if not kept:
        return []
    romfs = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    table = rstb.read(dictionaries.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes()))
    original = (romfs / SCHEDULE).read_bytes()
    entry = table.get(SCHEDULE)
    if entry is None or len(original) > entry:
        raise PatchError(f"Mido schedule: missing/short native allocation: size={len(original)}, entry={entry}")
    changed = guard_schedule(original)
    return [BuiltFile(SCHEDULE, changed, len(original), len(changed), entry)]
