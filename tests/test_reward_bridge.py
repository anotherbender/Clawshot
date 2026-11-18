"""Ganon's Castle rainbow bridge: the counted-rewards threshold, the AllSage Step01 guard, the staged module.

The behavior tests are synthetic (no romfs). Every valid threshold of stones/medallions/rewards is checked
against an independent model over all 512 ownership subsets of the nine rewards, with every subset granted
twice in both orders (a reward's saved Bool is set however often it is granted) and with a finished save's
completion flags set; ``add_eligibility`` gets a synthetic GameDataList in the native row shapes the patch
pins; ``light_arrow_story`` gets a synthetic AllSage holding Event10's completion, the Event11 write, one
plain GameDataActor (with and without the expression query natively registered) and unrelated events and
entry points. The dump tests read the real romfs: the flow patch inverts exactly, the module patch rewrites
only node4's default slot (node3, the Player contacts and the history/latch nodes pinned native) and the real
GameDataList gains only the generated rows. Pinned layout facts are build e0f3ccfa's, like the door tests'.
EventQueryIsGameDataBoolExp reads 0 for true and 1 for false (the door guards' convention).
"""

import itertools
import struct
from copy import deepcopy
from dataclasses import replace

import pytest
from test_door_dump import string_references
from test_door_stage import evaluate, indexed, text

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import reward_bridge
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.save import key

GANON_STEPS = (
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
NINE = (*reward_bridge.STONES, *reward_bridge.MEDALLIONS)
COUNTED = ("stones", "medallions", "rewards")
ELIGIBLE = "Clawshot.BridgeEligible"  # the unsaved expression the staged module's node4 reads
PAST_STEP01 = "Defeat_Ganon_IsAfter_Step01_Exp"  # native, strict: Step02 or later
MOVED = "ClawshotBridgeEvent11Write"  # the native Step01 write, appended behind the guard
FLOW = "Event/EventFlow/AllSage.bfevfl.zs"
MODULE = "Logic/GanonCastle_Level_Field_00_Prefab_14ba.logic.module.ainb"
CHALLENGE_ACTOR, STEP_ACTION = "ChallengeSystemActor", "EventExecuteProgressChallengeStep"
READ_EXPRESSION = "EventQueryIsGameDataBoolExp"
GAME_DATA_ACTOR = "GameDataActor"
COMPLETE = {
    "ChallengeName": "AllSage",
    "StepName": "Complete",
    "IsWaitEnd": True,
    "IsIgnoreCompletedChallenge": False,
    "IsIgnoreChallengeProgressUI": False,
}
WRITE = {
    "ChallengeName": "Defeat_Ganon",
    "StepName": "Step01",
    "IsWaitEnd": True,
    "IsIgnoreCompletedChallenge": False,
    "IsIgnoreChallengeProgressUI": False,
}

# A finished save's quests, awakenings, scenes, barrier and non-reward items: none of it is a reward.
COMPLETION = {
    "Step_Defeat_Ganon": "Complete",
    "Step_AllSage": "Complete",
    "Step_DoorOfTime": "Complete",
    "Defeat_Ganon_IsAfter_Step02_Exp": True,
    "AllSage_IsAfter_Step02_Exp": True,
    "AllSage_IsCompleted_Exp": True,
    "Get_StoneOfForest_IsCompleted_Exp": True,
    "Get_StoneOfFire_IsCompleted_Exp": True,
    "Get_StoneOfWater_IsCompleted_Exp": True,
    "SageOfForest_IsCompleted_Exp": True,
    "SageOfFire_IsCompleted_Exp": True,
    "SageOfWater_IsCompleted_Exp": True,
    "SageOfShadow_IsCompleted_Exp": True,
    "SageOfSpirit_IsCompleted_Exp": True,
    "SageOfLight_IsCompleted_Exp": True,
    "HavePlayedEvent.Dm_Awake_Spirit": True,
    "HavePlayedEvent.Dm_Awake_Shadow": True,
    "HavePlayedEvent.Dm_InsideGanonCastle_0000": True,
    "IsGet.Item_Arrow_Light": True,
    "IsGet.Item_Sword_Master": True,
    "IsGet.Item_Melody_TimeSong": True,
    "AllSage_AwakeSageCount": 6,
    "Barrier_Count": 0,
    "DoorOfTime_GetStoneCount": 3,
}

# Pinned layout facts of the native bridge module, build e0f3ccfa (the independent decode behind the patch).
POOL, NODES, NODE_SIZE = 0x24, 0x74, 0x3C  # u32 string pool offset; 60-byte node headers from 0x74
NODE_COUNT = 15
NODE3_RECORD, NODE4_RECORD = 0x11A8, 0x11B8  # node3's and node4's only String inputs, 16 bytes apart
NATIVE_READ = "Defeat_Ganon_IsAfter_Ready_Exp"  # node4's 31-byte default slot: the only bytes the patch rewrites
# (class, query base, query count) per node: node0 requests the rainbow event, nodes 2/12 the Player contacts
# node13 ANDs with the player guard (node14), node3 the strict Step01 expression, node4 the eligibility, node8
# the event's saved history, node10 the latch ORing it with the live EX1, nodes 1/11 the approach areas.
NATIVE_NODES = (
    ("ActorLogicEventRequestActor", 0, 1),
    ("ActorLogicAreaActor", 1, 1),
    ("HoldActorObserverBySensorHitInfo", 14, 1),
    ("HoldGameDataGetBoolExpSimple", 0, 0),
    ("HoldGameDataGetBoolExpSimple", 0, 0),
    ("OperateAND", 2, 2),
    ("OperateAND", 4, 1),
    ("ActorLogicSimpleActor", 5, 1),
    ("HoldGameDataHavePlayedEvent", 0, 0),
    ("ActorLogicSimpleActor", 6, 2),
    ("OperateORFixInputTrue", 8, 2),
    ("ActorLogicAreaActor", 10, 1),
    ("HoldActorObserverBySensorHitInfo", 15, 1),
    ("OperateAND", 11, 3),
    ("HoldPlayerrCheckEventQueryPlayerState", 0, 0),
)


def owned(grants) -> dict[str, bool]:
    """The saved ownership state after a grant sequence: a reward's Bool is set, never counted per grant."""
    state = {f"IsGet.{actor}": False for actor in NINE}
    for actor in grants:
        state[f"IsGet.{actor}"] = True
    return state


def threshold_index(mode: str, count: int) -> dict:
    """threshold_rows as the evaluator's index; only the counted rewards' ownership Bools exist to be read, so a
    read of anything else (a completion flag, another family's reward) fails the evaluator's own oracle."""
    rows = reward_bridge.threshold_rows(mode, count)
    return {
        "Bool": {key(f"IsGet.{actor}"): {} for actor in reward_bridge.identities(mode)},
        "BoolExp": {key(name): {"Values": values} for name, values in rows.items()},
        "Enum": {},
    }


@pytest.mark.parametrize("mode", COUNTED)
def test_eligible_is_at_least_count_distinct_rewards_over_every_subset(mode):
    """All 512 ownership subsets of the nine rewards at every valid count (0 is the documented tautology), each
    subset granted twice in both orders: ELIGIBLE reads exactly 'at least count of mode's rewards were
    acquired', counting only that mode's rewards."""
    identities = set(reward_bridge.identities(mode))
    wrong = []
    for count in range(reward_bridge.max_count(mode) + 1):
        rows = threshold_index(mode, count)
        for held in itertools.product((False, True), repeat=len(NINE)):
            subset = {actor for actor, got in zip(NINE, held, strict=True) if got}
            grants = [*subset, *sorted(subset, reverse=True)]  # every reward granted again, in another order
            want = len(subset & identities) >= count
            if evaluate(rows, key(ELIGIBLE), owned(grants)) is not want:
                wrong.append((count, sorted(subset)))
    assert not wrong, f"{mode}: {len(wrong)} wrong states, first {wrong[:3]}"


@pytest.mark.parametrize("mode", COUNTED)
def test_completion_flags_alone_cannot_satisfy_a_count(mode):
    """A finished save's quests, awakenings, barrier, scenes and non-reward items (Light Arrows included) set
    every flag but the nine rewards': the bridge stays closed. The other families' rewards do not count either,
    and one reward short of the count still reads closed while count of them opens it."""
    identities = reward_bridge.identities(mode)
    other = [actor for actor in NINE if actor not in identities]
    for count in range(1, reward_bridge.max_count(mode) + 1):
        rows = threshold_index(mode, count)
        assert evaluate(rows, key(ELIGIBLE), owned(()) | COMPLETION) is False, (mode, count)
        if other:
            assert evaluate(rows, key(ELIGIBLE), owned(other[:count]) | COMPLETION) is False, (mode, count)
        assert evaluate(rows, key(ELIGIBLE), owned(identities[: count - 1]) | COMPLETION) is False, (mode, count)
        assert evaluate(rows, key(ELIGIBLE), owned(identities[:count]) | COMPLETION) is True, (mode, count)


def test_rows_stay_within_the_native_envelope():
    """Every threshold's rows stay inside the native envelope the module documents: at most 26 commands, a
    BoolExp read nested at most 3 rows deep, and only the counted rewards' ownership Bools ever read (the
    measured maxima: 13 commands, the 3-row chain of rewards 9)."""

    def chain(rows, reverse, name):
        return 1 + max(
            (chain(rows, reverse, reverse[command[1]]) for command in rows[name] if command[0] == 10), default=0
        )

    for mode in COUNTED:
        for count in range(reward_bridge.max_count(mode) + 1):
            rows = reward_bridge.threshold_rows(mode, count)
            reverse = {key(name): name for name in rows}
            reads = set()
            for name, values in rows.items():
                assert len(values) <= 26, (mode, count, name, len(values))
                assert chain(rows, reverse, name) <= 3, (mode, count, name)
                reads |= {command[1] for command in values if command[0] == 0}
            assert reads <= {key(f"IsGet.{actor}") for actor in reward_bridge.identities(mode)}, (mode, count)


# The synthetic GameDataList.


def synthetic_game_data() -> dict:
    """The native-shaped rows the bridge reads (the nine saved ownership Bools, the strict Step01 expression
    and its quest Enum), plus unrelated saved and unsaved rows and the save layout metadata, built here."""

    def saved_bool(name, default=False):
        return {
            "DefaultValue": default,
            "Hash": byml.U32(key(name)),
            "ResetTypeValue": byml.I32(8),
            "SaveFileIndex": byml.I32(0),
        }

    def unsaved_expression(name, commands):
        return {
            "Hash": byml.U32(key(name)),
            "ResetTypeValue": byml.I32(0),
            "SaveFileIndex": byml.I32(-1),
            "Values": [[byml.U64(op), byml.U64(key(operand))] for op, operand in commands],
        }

    def saved_enum(name, values):
        return {
            "DefaultValue": byml.U32(key(values[0])),
            "Hash": byml.U32(key(name)),
            "RawValues": list(values),
            "ResetTypeValue": byml.I32(8),
            "SaveFileIndex": byml.I32(0),
            "Values": [byml.U64(key(value)) for value in values],
        }

    return {
        "Data": {
            "Bool": [saved_bool(f"IsGet.{actor}") for actor in NINE]
            + [saved_bool("IsGet.Item_Arrow_Light", True), saved_bool("Unrelated.Saved")],
            "BoolExp": [
                unsaved_expression(PAST_STEP01, ((12, "Step_Defeat_Ganon"), (2, "Step01"))),
                unsaved_expression("Unrelated.Expression", ((0, "Unrelated.Saved"),)),
            ],
            "Enum": [
                saved_enum("Step_Defeat_Ganon", GANON_STEPS),
                saved_enum("Step_DoorOfTime", ("NotReady", "Ready", "Step01", "Complete")),
            ],
            "Int": [
                {
                    "DefaultValue": byml.I32(0),
                    "Hash": byml.U32(key("AllSage_AwakeSageCount")),
                    "ResetTypeValue": byml.I32(8),
                    "SaveFileIndex": byml.I32(0),
                }
            ],
        },
        "MetaData": {"AllDataSaveOffset": byml.I32(64), "SaveDataOffsetPos": [byml.I32(16)]},
    }


BRIDGE_CASES = (("stones", 3), ("medallions", 4), ("rewards", 1), ("rewards", 9))


@pytest.mark.parametrize("mode,count", BRIDGE_CASES)
def test_add_eligibility_appends_only_unsaved_rows_and_keeps_the_save_layout(mode, count):
    """A synthetic GameDataList in the native shapes: exactly the threshold rows are appended (ELIGIBLE last),
    each unsaved (reset 0, save file -1); every native row, the unrelated rows and the save layout metadata
    stay put, and the appended rows still count ownership."""
    tree = synthetic_game_data()
    before = deepcopy(tree)
    reward_bridge.add_eligibility(tree, mode, count)
    assert byml.same(tree["MetaData"], before["MetaData"])
    want = reward_bridge.threshold_rows(mode, count)
    for kind, rows in before["Data"].items():
        assert byml.same(tree["Data"][kind][: len(rows)], rows), kind
        assert len(tree["Data"][kind]) == len(rows) + (len(want) if kind == "BoolExp" else 0), kind
    added = tree["Data"]["BoolExp"][len(before["Data"]["BoolExp"]) :]
    assert [int(row["Hash"]) for row in added] == [key(name) for name in want]
    for row, name in zip(added, want, strict=True):
        assert sorted(row) == ["Hash", "ResetTypeValue", "SaveFileIndex", "Values"]
        assert byml.same([row["ResetTypeValue"], row["SaveFileIndex"]], [byml.I32(0), byml.I32(-1)])
        assert byml.same(row["Values"], [[byml.U64(word) for word in command] for command in want[name]])
    assert int(added[-1]["Hash"]) == key(ELIGIBLE)
    rows = indexed(tree)
    identities = reward_bridge.identities(mode)
    for held, want_value in (((), False), (identities[: count - 1], False), (identities[:count], True), (NINE, True)):
        assert evaluate(rows, key(ELIGIBLE), owned(held)) is want_value, held


@pytest.mark.parametrize("initial", [False, True])
def test_a_fast_start_initial_ownership_is_kept_and_counted(initial):
    """The ownership Bools' initial values may be set by a fast start; either is accepted and kept, and the
    rows read the saved flag, so a New Game that starts with the Emerald held already counts it once."""
    tree = synthetic_game_data()
    row = next(row for row in tree["Data"]["Bool"] if int(row["Hash"]) == key("IsGet.Item_Stone_Forest"))
    row["DefaultValue"] = initial
    before = deepcopy(tree)
    reward_bridge.add_eligibility(tree, "stones", 1)
    rows = indexed(tree)
    new_game = {f"IsGet.{actor}": rows["Bool"][key(f"IsGet.{actor}")]["DefaultValue"] for actor in NINE}
    assert evaluate(rows, key(ELIGIBLE), new_game) is initial
    del tree["Data"]["BoolExp"][len(before["Data"]["BoolExp"]) :]
    assert byml.same(tree, before)


# The synthetic AllSage.


def synthetic_all_sage(*, native_query: bool) -> bytes:
    """The native AllSage shape the patch pins, built here: an unrelated wait before Event10's AllSage
    completion and Event11's Defeat_Ganon Step01 write, an unrelated trailing event with its own entry point,
    and the one plain GameDataActor, with or without the expression query natively registered."""
    actors = [
        evfl.Actor(CHALLENGE_ACTOR, actions=[STEP_ACTION]),
        evfl.Actor(
            GAME_DATA_ACTOR,
            queries=["EventQueryIsGameDataBool", READ_EXPRESSION] if native_query else ["EventQueryIsGameDataBool"],
        ),
        evfl.Actor("EventSystemActor", actions=["EventWait"]),
    ]
    events = [
        evfl.ActionEvent("Event9", 2, 0, next=1, params={"IsWaitEnd": True, "Frames": 1}),
        evfl.ActionEvent("Event10", 0, 0, next=2, params=COMPLETE),
        evfl.ActionEvent("Event11", 0, 0, next=evfl.NONE, params=WRITE),
        evfl.ActionEvent("Event12", 2, 0, next=evfl.NONE, params={"IsWaitEnd": True, "Frames": 2}),
    ]
    flowchart = evfl.Flowchart(
        "AllSage",
        actors=actors,
        events=events,
        entry_points=[evfl.EntryPoint("AllSage", main_event=0), evfl.EntryPoint("Epilogue", main_event=3)],
    )
    return evfl.write(evfl.EventFlowFile("AllSage", flowchart))


def execute_story(flowchart, initial_step):
    rows = indexed(synthetic_game_data())
    state = {"Step_Defeat_Ganon": initial_step, "Step_AllSage": "Step02"}
    at = flowchart.entry_points[0].main_event
    while at != evfl.NONE:
        event = flowchart.events[at]
        actor = flowchart.actors[event.actor]
        if isinstance(event, evfl.SwitchEvent):
            assert actor.queries[event.query] == READ_EXPRESSION
            value = evaluate(rows, key(event.params["GameDataName"]), state)
            at = dict(event.cases).get(0 if value else 1, evfl.NONE)
        else:
            action = actor.actions[event.action]
            if action == STEP_ACTION:
                state["Step_" + event.params["ChallengeName"]] = event.params["StepName"]
            else:
                assert action == "EventWait"
            at = event.next
    return state


@pytest.mark.parametrize("native_query", [False, True])
def test_initial_ready_becomes_step01_and_no_step02_or_later_regresses(native_query):
    """Every Defeat_Ganon state through the guard: the false case (1) runs the moved write, so NotReady, Ready
    and Step01 itself all end at Step01; past Step01 no case matches and the entry ends as it natively does
    after Event11, so the quest never moves back."""
    fc = evfl.read(reward_bridge.light_arrow_story(synthetic_all_sage(native_query=native_query))).flowchart
    for step in GANON_STEPS:
        state = execute_story(fc, step)
        expected = "Step01" if GANON_STEPS.index(step) <= GANON_STEPS.index("Step01") else step
        assert state == {"Step_AllSage": "Complete", "Step_Defeat_Ganon": expected}, step


# The real romfs.


@pytest.fixture(scope="module")
def dictionaries(romfs):
    return zsdic.Dictionaries.from_romfs(romfs)


@pytest.fixture(scope="module")
def native_flow(romfs, dictionaries) -> bytes:
    return dictionaries.decompress(FLOW, (romfs / FLOW).read_bytes())


@pytest.fixture(scope="module")
def native_game_data(romfs, dictionaries) -> bytes:
    return dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes())


@pytest.fixture(scope="module")
def native_module(romfs) -> bytes:
    return (romfs / MODULE).read_bytes()


@pytest.mark.dump
def test_all_sage_changes_only_the_writer_its_target_and_the_query(native_flow):
    """Exactly: Event11 becomes the strict-Step01 query whose false case runs the unchanged native write
    appended last, the plain GameDataActor gains the expression query when it lacks it, and undoing those
    edits returns the native file (every event, actor and registration equal)."""
    native = evfl.read(native_flow)
    patched = evfl.read(reward_bridge.light_arrow_story(native_flow))
    assert (patched.name, patched.timeline) == (native.name, native.timeline)
    fc, original = patched.flowchart, native.flowchart
    count = len(original.events)
    names = [event.name for event in fc.events]
    assert len(set(names)) == len(names)
    assert names[:count] == [event.name for event in original.events]
    assert names[count:] == [MOVED]
    at = names.index("Event11")
    reader = [i for i, actor in enumerate(fc.actors) if actor.name == GAME_DATA_ACTOR and not actor.secondary_name]
    assert len(reader) == 1
    moved = fc.events[count]
    assert moved == replace(original.events[at], name=MOVED)
    assert fc.events[at] == evfl.SwitchEvent(
        "Event11",
        reader[0],
        fc.actors[reader[0]].queries.index(READ_EXPRESSION),
        [(1, count)],
        {"GameDataName": PAST_STEP01},
    )
    for i in range(count):
        if i != at:
            assert fc.events[i] == original.events[i], names[i]  # Event10's completion and every other event
    assert len(fc.actors) == len(original.actors)
    for i, actor in enumerate(fc.actors):
        if i == reader[0]:
            assert actor.queries in (original.actors[i].queries, original.actors[i].queries + [READ_EXPRESSION])
        else:
            assert actor == original.actors[i], i
    assert fc.entry_points == original.entry_points
    restored = deepcopy(fc)
    restored.events[at] = replace(moved, name="Event11")
    queries = restored.actors[reader[0]].queries
    if queries != original.actors[reader[0]].queries:
        assert queries == original.actors[reader[0]].queries + [READ_EXPRESSION]
        queries.pop()
    del restored.events[count:]
    assert evfl.EventFlowFile(native.name, restored, native.timeline) == native


@pytest.mark.dump
def test_the_module_patch_rewrites_only_node4s_default_slot(native_module):
    """Same length; the only changed bytes are node4's own 31-byte native default slot, which stays referenced
    solely by its record's default word; node3 still reads the strict Step01 expression and every node header,
    the Player contacts and the history/latch nodes included, stays byte-for-byte native."""
    native = native_module
    patched = reward_bridge.stage(native)
    assert len(patched) == len(native)
    pool = struct.unpack_from("<I", native, POOL)[0]
    assert native[-1] == 0 and all(32 <= byte < 127 or byte == 0 for byte in native[pool:]), "pool is only text"
    assert struct.unpack_from("<I", native, 0x10)[0] == NODE_COUNT
    _, _, _, _, default = struct.unpack_from("<IhhII", native, NODE4_RECORD)
    slot, size = pool + default, len(NATIVE_READ) + 1
    changed = {offset for offset in range(len(native)) if patched[offset] != native[offset]}
    mask = set(range(slot, slot + size))
    assert changed <= mask, sorted(hex(offset) for offset in changed - mask)
    assert native[slot : slot + size] == NATIVE_READ.encode() + b"\0"
    assert patched[slot : slot + size] == ELIGIBLE.encode().ljust(size, b"\0")
    assert native[slot - 1] == patched[slot - 1] == 0, "an earlier pool string runs into the slot"
    assert struct.unpack_from("<IhhII", patched, NODE4_RECORD) == struct.unpack_from("<IhhII", native, NODE4_RECORD)
    for module in (native, patched):  # node4's default word stays the slot's only reader, before and after
        assert string_references(module, slot, size) == [NODE4_RECORD + 12]
    name, source, output, flags, node3_default = struct.unpack_from("<IhhII", patched, NODE3_RECORD)
    assert (text(patched, pool + name), (source, output, flags)) == ("GameDataNameBoolExp", (-1, 0, 0x800000))
    assert text(patched, pool + node3_default) == PAST_STEP01
    for node, (cls, query_base, query_count) in enumerate(NATIVE_NODES):
        header = NODES + NODE_SIZE * node
        at, digest = struct.unpack_from("<2I", patched, header + 8)
        assert (text(patched, pool + at), digest) == (cls, key(cls)), node
        assert struct.unpack_from("<2H", patched, header + 0x24) == (query_base, query_count), node


@pytest.mark.dump
@pytest.mark.parametrize("mode,count", (("stones", 3), ("medallions", 1), ("medallions", 4), ("rewards", 9)))
def test_the_real_game_data_gains_only_the_threshold_rows(native_game_data, mode, count):
    """The real GameDataList through the patch transform: every native row, default and the save layout
    metadata stay, exactly the generated unsaved BoolExp rows are appended last, and on the real tree they
    still count ownership; the flow transform is always paired with them."""
    raw = native_game_data
    changes = reward_bridge.changes(mode=mode, count=count)
    native = byml.read(raw)
    patched = byml.read(changes[GAME_DATA_LIST](raw))
    want = reward_bridge.threshold_rows(mode, count)
    trimmed = deepcopy(patched)
    del trimmed["Data"]["BoolExp"][len(native["Data"]["BoolExp"]) :]
    assert byml.same(trimmed, native)  # every saved flag, default, other row and the save layout metadata
    added = patched["Data"]["BoolExp"][len(native["Data"]["BoolExp"]) :]
    assert [int(row["Hash"]) for row in added] == [key(name) for name in want]
    for row in added:
        assert sorted(row) == ["Hash", "ResetTypeValue", "SaveFileIndex", "Values"]
        assert byml.same([row["ResetTypeValue"], row["SaveFileIndex"]], [byml.I32(0), byml.I32(-1)])
    rows = indexed(patched)
    identities = reward_bridge.identities(mode)
    for held, want_value in (((), False), (identities[:count], True), (NINE, True)):
        assert evaluate(rows, key(ELIGIBLE), owned(held)) is want_value, held
