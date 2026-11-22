"""Spec tracker-auto-checks 5.3: the track-flag path checker (``track_paths``) on built flowcharts, passing and
failing cases (plan P9.b)."""

from track_paths import Flag, check, cut_reaches, writers

from clawshot.formats.evfl import (
    NONE,
    ActionEvent,
    Actor,
    Argument,
    EntryPoint,
    Flowchart,
    ForkEvent,
    JoinEvent,
    SubFlowEvent,
    SwitchEvent,
)

F = Flag("bool", "Npc_Test_Given")


def actors():
    game_data = Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"], queries=["EventQueryIsGameDataBool"])
    system = Actor("GameSystemActor", actions=["EventWait"], queries=["EventQueryTalkChoice2"])
    return [game_data, system]


def set_bool(name, flag, nxt=NONE, value=True):
    return ActionEvent(name, 0, 0, next=nxt, params={"GameDataName": flag, "Index": -1, "Value": value})


def ask(name, flag, true, false):
    return SwitchEvent(name, 0, 0, [(0, true), (1, false)], {"GameDataName": flag, "Index": -1})


def give(name, nxt=NONE, item="Item_Old"):
    return SubFlowEvent(name, "Wrap", "Give", next=nxt, params={"ActorName": item})


def wait(name, nxt=NONE):
    return ActionEvent(name, 1, 0, next=nxt, params={"Frames": 1})


def flow(events, entries=(("Talk", 0),)):
    return Flowchart("Npc_Test", actors(), events, [EntryPoint(n, i) for n, i in entries])


def test_a_flag_set_with_the_grant_and_a_repeat_that_resets_nothing_pass():
    fc = flow(
        [
            ask("Event0", F.name, 3, 1),  # given already: a repeat talk; else the grant
            give("Event1", 2),
            set_bool("Event2", F.name),
            wait("Event3", 4),
            set_bool("Event4", F.name),  # re-sets an already set flag on the repeat path: not a fault
        ]
    )
    assert check(fc, F, ["Event1"]) == []
    assert writers(fc, F) == ["Event2", "Event4"]


def test_a_flag_set_on_a_path_that_skips_the_grant_is_reported():
    fc = flow(
        [
            ask("Event0", "Other_Flag", 1, 3),
            give("Event1", 2),
            set_bool("Event2", F.name),
            set_bool("Event3", F.name),  # first talk: set without the grant
        ]
    )
    [fault] = check(fc, F, ["Event1"])
    assert fault.startswith("Npc_Test: flag without grant for Npc_Test_Given") and "Event0 > Event3" in fault


def test_a_grant_that_can_end_without_the_flag_is_reported():
    choice = SwitchEvent("Event1", 1, 0, [(0, 2), (1, 3)])
    fc = flow([give("Event0", 1), choice, set_bool("Event2", F.name), wait("Event3")])
    [fault] = check(fc, F, ["Event0"])
    assert fault.startswith("Npc_Test: grant without flag") and "Event0 > Event1 > Event3" in fault


def test_a_reset_after_the_grant_is_reported():
    fc = flow([give("Event0", 1), set_bool("Event1", F.name, 2), set_bool("Event2", F.name, value=False)])
    assert [f.split(" for ")[0] for f in check(fc, F, ["Event0"])] == ["Npc_Test: grant without flag"]


def test_a_flag_passed_as_a_call_argument_is_followed_into_the_callee():
    fc = flow(
        [
            SubFlowEvent("Event0", "", "Teach", params={"GameDataName": F.name}),  # the grant: a frog-song call
            ask("Event1", Argument("GameDataName"), 4, 2),
            wait("Event2", 3),
            set_bool("Event3", Argument("GameDataName")),
            wait("Event4"),  # already taught: talk and leave
        ],
        entries=(("Talk", 0), ("Teach", 1)),
    )
    assert writers(fc, F) == ["Event0"]  # the call site passing the flag; the walk follows it in
    assert check(fc, F, ["Event0"]) == []


def test_a_minigame_call_grants_only_where_it_hands_over_its_item_argument():
    success = SwitchEvent("Event1", 1, 0, [(0, 2), (1, 4)])
    fc = flow(
        [
            SubFlowEvent("Event0", "", "Game", params={"ActorName": "Obj_Heart_Piece"}),  # census step
            success,
            SubFlowEvent("Event2", "Wrap", "Give", next=3, params={"ActorName": Argument("ActorName")}),
            set_bool("Event3", F.name),
            wait("Event4"),  # failed: nothing handed over, flag unset
        ],
        entries=(("Talk", 0), ("Game", 1)),
    )
    assert check(fc, F, ["Event0"], param={"Event0": "ActorName"}) == []
    assert check(fc, F, ["Event0"]) != []  # without the argument the call itself is the grant: Failed is a fault


def test_an_invariant_prunes_a_walk_the_game_cannot_take():
    fc = flow(
        [
            ask("Event0", "First", 4, 1),  # first win not yet recorded: the first prize
            give("Event1", 2),
            ask("Event2", "Second", 5, 3),
            set_bool("Event3", "First"),
            wait("Event4"),
            wait("Event5"),
        ]
    )
    first = Flag("bool", "First")
    assert check(fc, first, ["Event1"]) != []  # Second true with First false is only impossible by the invariant
    assert check(fc, first, ["Event1"], invariants=[("Second", True, "First", True)]) == []


def test_a_cut_must_reach_its_grant_on_every_walk():
    fc = flow([wait("Event0", 1), give("Event1", 2), wait("Event2")], entries=(("EntryPoint0", NONE), ("C01", 0)))
    assert cut_reaches(fc, ["Event1"]) == []
    branch = SwitchEvent("Event0", 1, 0, [(0, 1), (1, 2)])
    fc = flow([branch, give("Event1"), wait("Event2")], entries=(("C01", 0),))
    assert cut_reaches(fc, ["Event1"]) == ["Npc_Test: cut C01 can end at Event2 without a grant ['Event1']"]
    assert cut_reaches(fc, ["Event9"]) == ["Npc_Test: grant step(s) ['Event9'] are gone"]
    # A Fork runs every branch before its Join: a grant in one branch is reached, an idle branch's end is not an end.
    fork = ForkEvent("Event0", join=3, forks=[1, 2])
    fc = flow([fork, give("Event1"), wait("Event2"), JoinEvent("Event3", next=4), wait("Event4")], (("C01", 0),))
    assert cut_reaches(fc, ["Event1"]) == []
