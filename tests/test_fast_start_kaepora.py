"""The skipped Hyrule Field owl must leave what his talk would: field music (section 46) and the clock's arrival."""

import pytest
from test_fast_start import flag, h

from clawshot.formats import byml, zsdic
from clawshot.patch import door, gamedata
from clawshot.save import murmur3_32

FIELD_PANORAMA = "HavePlayedEvent.Dm_HrlField_0000"
OWL_TALK = "HavePlayedEvent.Dm_HrlField_0010"
ARRIVED = "HyruleField_ArriveEntrance"  # A
ADULT_HOLD = "HrlField_HasEnteredFirstTime_Adult"  # B
SENDOFF = "HavePlayedEvent.Dm_HrlField_0020"  # S: Impa's field send-off
CASTLE = "Step_Goto_HyruleCastle"
STEPS = ["NotReady", "Ready", "Step01", "Step02", "Complete"]
CLOCK_STATE = (ARRIVED, ADULT_HOLD, SENDOFF, OWL_TALK, CASTLE)

# The native ordinary clock update 0x3cdf70 (build e0f3ccfa), executed instruction by instruction on synthetic
# memory in round 16 (rounds/r16-time.md), outside menu/event pauses and the Meet_DekuTree Ready override:
# - stop helper 0x345c020 stops it without A (read at 0x345c114..0x345c1d0) or with B (0x345c294..0x345c350);
# - a stopped clock takes 0x345c450's fixed time from the table at 0x3c834e8: 06:00 without A, 20:00 with A and B;
# - without S (0x3ce2a8..0x3ce2c4) it advances only up to 15:00 (0x3ce620..0x3ce650, helper 0x3420da0).
DAY = 24 * 3600
STOPPED = (6 * 3600, 20 * 3600)
CAP = 15 * 3600
TICK = 2  # seconds per update at the proof's synthetic frame rate
AFTERNOON = CAP - 1  # 14:59:59
FROZEN_MORNING = (STOPPED[0],) * 2
CAPPED = (CAP, CAP)
RUNNING = (CAP + 1, CAP + 3)


def ordinary_clock(state: dict, seconds: int = AFTERNOON, updates: int = 2) -> tuple[int, ...]:
    """The clock's seconds after each of ``updates`` ordinary updates."""
    samples = []
    for _ in range(updates):
        if not state[ARRIVED] or state[ADULT_HOLD]:
            seconds = STOPPED[state[ARRIVED]]
        elif not state[SENDOFF] and (CAP - seconds) % DAY <= TICK:
            seconds = CAP
        else:
            seconds = (seconds + TICK) % DAY
        samples.append(seconds)
    return tuple(samples)


def owl_can_play(state: dict) -> bool:
    """Native HyruleField_Child_Prefab_de5f requests the owl's event while Dm_HrlField_0010 is unplayed, and node5
    deletes its area once Goto_HyruleCastle is past Step01. The event sets A (Goto_HyruleCastle Event153)."""
    return not state[OWL_TALK] and STEPS.index(state[CASTLE]) <= STEPS.index("Step01")


def game_data_list(names) -> bytes:
    """Synthetic GameDataList: each named Bool false (as in the game), the castle quest NotReady."""
    tree = {
        "Data": {
            "Bool": [flag(name, False) for name in dict.fromkeys(names) if name != CASTLE],
            "Int": [],
            "Enum": [{**flag(CASTLE, h("NotReady")), "RawValues": STEPS, "Values": [h(step) for step in STEPS]}],
        }
    }
    return byml.write(tree, "big")


def initial_value(data: bytes, name: str) -> bool | str:
    """A new game's value of ``name``: a Bool's value or an Enum's step name."""
    lists, key = byml.read(data)["Data"], murmur3_32(name.encode())
    ((kind, entry),) = [(kind, row) for kind in ("Bool", "Enum") for row in lists.get(kind, []) if row["Hash"] == key]
    return entry["RawValues"][entry["Values"].index(entry["DefaultValue"])] if kind == "Enum" else entry["DefaultValue"]


def new_game(skips: list[str]) -> dict:
    """The clock inputs a new game starts with, through a closed-Door seed's GameDataList steps in their order."""
    chosen = [*gamedata.load_always(), *gamedata.select(gamedata.load(), skips)]
    data = game_data_list([*CLOCK_STATE, *(name for setting in chosen for name in setting.game_data)])
    for step in (gamedata.changes(chosen), door.changes({}, mode="closed")):
        if transform := step.get(gamedata.GAME_DATA_LIST):
            data = transform(data)
    return {name: initial_value(data, name) for name in CLOCK_STATE}


@pytest.mark.parametrize("skip", [False, True])
def test_kaepora_skip_writes_the_field_music_release_history(skip):
    settings = gamedata.load()
    data = game_data_list([FIELD_PANORAMA, *settings["kaepora"].game_data])
    written = gamedata.patch_initial_values(data, gamedata.select(settings, ["kaepora"] if skip else []))
    assert initial_value(written, FIELD_PANORAMA) is skip


@pytest.mark.parametrize("skip", [False, True])
def test_kaepora_skip_lets_the_clock_run_after_the_real_sendoff(skip):
    """Closed Door, no first-adult hold. Played, the owl sets A before his demos; skipped, the new game must hold it.

    The send-off changes only S: no story-side restoration of A is assumed."""
    state = new_game(["kaepora"] if skip else [])
    owl_plays = owl_can_play(state)
    if owl_plays:
        state[ARRIVED] = True
    before = ordinary_clock(state)
    state[SENDOFF] = True
    after = ordinary_clock(state)
    assert (owl_plays, before, after) == (not skip, CAPPED, RUNNING), {
        "skip": skip,
        "state": state,
        "owl_plays": owl_plays,
        "before_sendoff": before,
        "after_sendoff": after,
    }
    # The same field state without A stays at 06:00 whatever Impa does.
    assert ordinary_clock({**state, ARRIVED: False}) == FROZEN_MORNING


@pytest.mark.dump
def test_native_kaepora_output_ends_the_field_panorama_mute_range(romfs, tmp_path):
    out = tmp_path / "kaepora"
    gamedata.write(romfs, out, ["kaepora"])
    path = gamedata.GAME_DATA_LIST
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    assert initial_value(dictionaries.decompress(path, (out / "romfs" / path).read_bytes()), FIELD_PANORAMA)
