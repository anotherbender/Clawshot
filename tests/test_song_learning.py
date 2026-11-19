"""No-instrument lessons must complete without leaving a parallel player pose waiting."""

from copy import deepcopy

import pytest

from clawshot.census.gifts import reachable
from clawshot.formats import evfl
from clawshot.formats.zsdic import Dictionaries
from clawshot.patch import song_learning


def lesson():
    return evfl.EventFlowFile(
        "Dm_SY_Ocarina",
        evfl.Flowchart(
            "Dm_SY_Ocarina",
            actors=[
                evfl.Actor(
                    "Player_Event", actions=["EventTriggerSetOwnAsInstrumentPlayer", "EventPlayerPlayOcarinaFree"]
                ),
                evfl.Actor("GameDataActor", queries=["EventQueryIsGameDataBool"]),
                evfl.Actor("OcarinaSystemActor", actions=["EventWaitOcarinaInputForLearning"]),
            ],
            events=[
                evfl.ActionEvent("Event175", 0, 0, 1),
                evfl.ForkEvent("Event38", 4, [2, 3]),
                evfl.ActionEvent("Event40", 2, 0, params={"MelodyType": evfl.Argument("MelodyType")}),
                evfl.ActionEvent("Event154", 0, 1),
                evfl.JoinEvent("Event37"),
            ],
            entry_points=[evfl.EntryPoint("LearningOcarinaFollowExample", 0)],
        ),
    )


def input_fork(fc, owned):
    index = fc.entry_point("LearningOcarinaFollowExample").main_event
    while index != evfl.NONE:
        event = fc.events[index]
        if isinstance(event, evfl.SwitchEvent):
            # Native Bool query results: true=0, false=1.
            index = dict(event.cases)[0 if event.params["GameDataName"] in owned else 1]
        elif isinstance(event, evfl.ForkEvent):
            return True
        else:
            index = event.next
    return False


@pytest.mark.parametrize(
    ("child", "owned", "expected"),
    [
        (True, set(), False),
        (False, set(), False),
        (True, {"IsGet.Item_Ocarina_Fairy"}, True),
        (False, {"IsGet.Item_Ocarina_Fairy"}, False),
        (True, {"IsGet.Item_Ocarina_Time"}, True),
        (False, {"IsGet.Item_Ocarina_Time"}, True),
        (True, {"IsGet.Item_Ocarina_Fairy", "IsGet.Item_Ocarina_Time"}, True),
        (False, {"IsGet.Item_Ocarina_Fairy", "IsGet.Item_Ocarina_Time"}, True),
    ],
)
def test_learning_never_starts_input_or_parallel_pose_without_an_instrument(child, owned, expected):
    fc = evfl.read(song_learning.patch(evfl.write(lesson()))).flowchart
    flags = owned | ({"Sequence_IsChildhood"} if child else set())
    assert input_fork(fc, flags) is expected, {"child": child, "owned": owned, "expected_input": expected}


@pytest.mark.dump
def test_native_learning_bypasses_only_presentation_and_preserves_all_other_entries(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    before = evfl.read(dictionaries.decompress(song_learning.FLOW, (romfs / song_learning.FLOW).read_bytes()))
    after = evfl.read(song_learning.patch(evfl.write(before)))
    fc = before.flowchart
    setup = fc.events[fc.entry_point("LearningOcarinaFollowExample").main_event]
    fork = fc.events[setup.next]
    skipped = reachable(fc, setup.next)
    assert {
        fc.actors[e.actor].actions[e.action] for i in skipped if isinstance(e := fc.events[i], evfl.ActionEvent)
    } == {
        "EventWaitOcarinaInputForLearning",
        "EventTalk",
        "EventTriggerPlayerRequestLookAtTheFrontLock",
        "EventPlayerPlayOcarinaFree",
    }
    assert all(not isinstance(fc.events[i], evfl.SubFlowEvent) for i in skipped)
    # Complete typed-tree equality, not merely unchanged writes: no unrelated
    # free-play, warp, Scarecrow, demonstration, automatic grant or cleanup edit.
    expected = deepcopy(before)
    expected.flowchart.events[fc.entry_point("LearningOcarinaFollowExample").main_event].next = len(fc.events)
    expected.flowchart.events.extend(after.flowchart.events[len(fc.events) :])
    assert after == expected
    assert after.flowchart.events[fork.join] == fc.events[fork.join]


@pytest.mark.dump
def test_native_bool_query_result_codes_gate_age_usable_playback(romfs):
    dictionaries = Dictionaries.from_romfs(romfs)
    donor_path = "Event/EventFlow/MiniGame_DampeRace.bfevfl.zs"
    donor = evfl.read(dictionaries.decompress(donor_path, (romfs / donor_path).read_bytes())).flowchart
    query = next(event for event in donor.events if event.name == "Event50")
    assert donor.actors[query.actor].queries[query.query] == "EventQueryIsGameDataBool"
    setter = donor.events[dict(query.cases)[1]]
    assert donor.actors[setter.actor].actions[setter.action] == "EventTriggerSetGameDataBool"
    assert setter.params["GameDataName"] == query.params["GameDataName"]
    assert setter.params["Value"] is True
    assert donor.events[dict(query.cases)[0]].name == "Event75"
    # The first-talk false branch sets the flag; the already-talked true branch does not.
    native = dictionaries.decompress(song_learning.FLOW, (romfs / song_learning.FLOW).read_bytes())
    patched = evfl.read(song_learning.patch(native)).flowchart
    assert input_fork(patched, set()) is False
    assert input_fork(patched, {"IsGet.Item_Ocarina_Time"}) is True
    assert input_fork(patched, {"IsGet.Item_Ocarina_Fairy"}) is False
    assert input_fork(patched, {"IsGet.Item_Ocarina_Fairy", "Sequence_IsChildhood"}) is True
