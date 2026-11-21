"""Skip selected trial cores through existing new-game state; no new saved flags.

Native evidence: plans/rounds/r20-trials.md. Partial counts retain the real last-core
scene, counter decrement and all-clear writer. Zero initializes the native all-clear
Bool because no last core will run. Scene history and quest steps are never forged.
"""

from clawshot.formats import msbt, sarc
from clawshot.generate.trials import TRIALS, remaining
from clawshot.patch import gamedata, text
from clawshot.patch.write import FileChanges

REMOVAL = "InsideGanonCastle_Dungeon_BarrierRemove_"
COUNT = "InsideGanonCastle_Dungeon_Barrier_Count"
ALL_CLEAR = "InsideGanonCastle_IsAllBarrierClear"
MESSAGE_FILE = "EventFlowMsg/Dm_InsideGanonCastle_0003.msbt"
MESSAGE = "Dm_InsideGanonCastle_0003_Text_002_b"
ZERO_MESSAGE = "Dm_InsideGanonCastle_0003_Text_001_b"


def initial_values(seed: int, count: int) -> list[gamedata.FastStartSetting]:
    active = remaining(seed, count)
    if count == 6:
        return []
    values: dict[str, bool | int | str] = {REMOVAL + name: True for name in TRIALS if name not in active}
    values[COUNT] = count
    if count == 0:
        values[ALL_CLEAR] = True
    return [
        gamedata.FastStartSetting(
            name="ganon_trials",
            default=False,
            skips="Selected Ganon's Castle trial cores",
            state="Existing skipped-core completion Bools and matching remaining count; zero also clears the barrier",
            source="plans/rounds/r20-trials.md: native Defeat_Ganon core writes and room01 barrier/door readers",
            logic="The native tower rule requires only the selected remaining trials",
            game_data=values,
            flow_edits=(),
        )
    ]


def changes(romfs, *, seed: int, count: int) -> FileChanges:
    active = remaining(seed, count)
    if count == 6:
        return {}
    line = "Trials remaining: " + ", ".join(active) + "." if active else "No trials remain. The tower barrier is gone."

    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        messages = msbt.read(files[MESSAGE_FILE]).messages
        edits = {MESSAGE: text.stone_line(messages[MESSAGE], line)}
        if not active:
            edits[ZERO_MESSAGE] = text.stone_line(messages[ZERO_MESSAGE], "The way into the tower has been opened.")
        return text.edit_messages({MESSAGE_FILE: edits})(data)

    return {text.archive_path(language): transform for language in text.languages(romfs)}
