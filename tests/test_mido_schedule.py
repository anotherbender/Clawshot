"""Synthetic quest/saved-wall states; native layout and public composition live in the dump tests."""

from copy import deepcopy

import pytest
from test_door_stage import evaluate, indexed

from clawshot.formats import byml
from clawshot.patch import mido_schedule as patch
from clawshot.patch.mido import BLOCKER
from clawshot.patch.plan import PatchError
from clawshot.save import key

STEPS = ["NotReady", "Ready", "Step01", "Step02", "Step02_01", "Step03", "Step03_01", "Step03_02", "Step04", "Complete"]


def expression(name, values):
    return {
        "Hash": byml.U32(key(name)),
        "ResetTypeValue": byml.I32(0),
        "SaveFileIndex": byml.I32(-1),
        "Values": [[byml.U64(value) for value in command] for command in values],
    }


def game_data():
    return {
        "MetaData": {"SaveDataOffsetPos": [byml.I32(12), byml.I32(24)]},
        "Data": {
            "Bool": [
                {
                    "Hash": byml.U32(key(BLOCKER)),
                    "DefaultValue": True,
                    "ResetTypeValue": byml.I32(8),
                    "SaveFileIndex": byml.I32(0),
                }
            ],
            "BoolExp": [expression(patch.CASTLE_COMPLETE, [[1, key(patch.CASTLE_STEP)], [2, key("Complete")]])],
            "Enum": [
                {
                    "Hash": byml.U32(key(patch.CASTLE_STEP)),
                    "RawValues": STEPS,
                    "Values": [byml.U64(key(step)) for step in STEPS],
                    "DefaultValue": byml.U32(key("Step02")),
                    "ResetTypeValue": byml.I32(8),
                    "SaveFileIndex": byml.I32(0),
                }
            ],
        },
    }


def schedule():
    return {
        "ConditionalSchedule": [
            {"ConditionFlag": "OtherNativeCondition", "ActionSchedule": [{"ActionType": byml.U32(key("Action2"))}]},
            {
                "ConditionFlag": patch.CASTLE_COMPLETE,
                "ActionSchedule": [{"ActionType": byml.U32(key("Action4")), "StartTime": 0}],
                "EventEntry": [
                    {
                        "EventName": (
                            "Work/Event/EventSetting/Npc_Kokiri_Mido_Child_C5_T."
                            "engine__event__EventSettingParam.gyml"
                        )
                    }
                ],
            },
        ],
        "DefaultSchedule": {"ActionSchedule": [{"StartTime": 0}]},
    }


@pytest.mark.parametrize("castle", ["Step01", "Step02", "Complete"])
@pytest.mark.parametrize("blocked", [False, True])
def test_late_schedule_waits_for_actual_clear_not_quest_or_default_state(castle, blocked):
    # Saved state, not the new-game default: clearing the wall enables the normal late schedule.
    rows = indexed(byml.read(patch.add_expression(byml.write(game_data(), "big"))))
    state = {patch.CASTLE_STEP: castle, BLOCKER: blocked}
    assert evaluate(rows, key(patch.AFTER_CLEAR), state) is (castle == "Complete" and not blocked)


def test_schedule_preserves_other_rows_actions_entries_and_byte_order():
    original = schedule()
    changed = byml.load(patch.guard_schedule(byml.write(original, "big")))
    assert changed.byte_order == "big"
    changed.root["ConditionalSchedule"][1]["ConditionFlag"] = patch.CASTLE_COMPLETE
    assert byml.same(changed.root, original)


def test_new_expression_does_not_migrate_defaults_or_saved_layout():
    original = game_data()
    changed = byml.read(patch.add_expression(byml.write(original)))
    [new] = [row for row in changed["Data"]["BoolExp"] if row["Hash"] == key(patch.AFTER_CLEAR)]
    assert new["SaveFileIndex"] == -1 and new["ResetTypeValue"] == 0
    assert all(type(value) is byml.U64 for command in new["Values"] for value in command)
    changed["Data"]["BoolExp"].remove(new)
    assert byml.same(changed, original)


@pytest.mark.parametrize("kind", ["Bool", "BoolExp"])
def test_expression_hash_collision_cannot_retarget_saved_state(kind):
    tree = game_data()
    tree["Data"][kind].append({"Hash": byml.U32(key(patch.AFTER_CLEAR))})
    with pytest.raises(PatchError, match="hash collision"):
        patch.add_expression(byml.write(tree))


@pytest.mark.parametrize("changed_source", ["blocker", "completion", "steps"])
def test_changed_native_sources_are_refused(changed_source):
    tree = deepcopy(game_data())
    if changed_source == "blocker":
        tree["Data"]["Bool"][0]["DefaultValue"] = False
    elif changed_source == "completion":
        tree["Data"]["BoolExp"][0]["Values"][1][1] = byml.U64(key("Step02"))
    else:
        tree["Data"]["Enum"][0]["RawValues"] = ["Complete", "Step02"]
    with pytest.raises(PatchError, match="changed native"):
        patch.add_expression(byml.write(tree))


def test_changed_late_action_is_not_silently_guarded():
    tree = schedule()
    tree["ConditionalSchedule"][1]["ActionSchedule"][0]["ActionType"] = byml.U32(key("Action3"))
    with pytest.raises(PatchError, match="changed native C5"):
        patch.guard_schedule(byml.write(tree))
