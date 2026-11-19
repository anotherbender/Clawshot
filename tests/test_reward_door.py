"""Closed Door of Time with dungeon rewards shuffled: owned Spiritual Stones open it; the early story keeps it open.

Contract (Kareem via Claude, 2026-11-19; round16 #32 kept): the altar's Event60 reads the unsaved
``Market_Child_TimeTempleDoor_OcarinaReacts`` row, which becomes NOT(the three owned stones, the Ocarina of Time, the
learned Song of Time and Impa's real send-off) OR opened; false continues to the native latch, opening history,
recommended song, scene, latch write and Step06. The early modes' forward-only Door/Saria/Zelda guards, their four
unsaved stage rows and the four Field story modules ship too: a pull before the Fire and Water quests never rewinds
the quest, and the escape and moat still wait for those completions. Never the open pedestal or Temple door module.
Rewards off, and both early modes either way, ship exactly what they did.

Synthetic flows and GameData are invented on the native contracts of test_door, test_door_story and test_door_stage,
whose engines this file reuses. Dump-marked tests read the real flows, GameData and modules through the public
``door.changes``/``build``/``write`` and ``make_seed``. Engine timing, presentation and save behavior still need play.
"""

import hashlib
from functools import cache
from itertools import product

import pytest
from test_door import run_open_flow, synthetic_flow
from test_door_dump import (
    COMMON_GATE,
    COMMON_GATE_SHA256,
    ERA_FLOW,
    SIZE_TABLE,
    STAGE_MODULES,
    door_signals,
    unpatch_story,
)
from test_door_stage import (
    ADDED,
    COLLECTED,
    ESCAPE_READY,
    LAYOUTS,
    MOAT_AREAS_DONE,
    MOAT_READY,
    SCENE_GATES,
    Stage,
    evaluate,
    expected,
    indexed,
    stories,
    synthetic_game_data,
)
from test_door_story import (
    ARRIVED,
    BRIDGE,
    CASTLE,
    COUNT,
    DOOR,
    ESCAPED,
    FLOWS,
    MODES,
    ORDERS,
    PATHS,
    SARIA,
    START,
    STEP,
    STEPS,
    STONES,
    STORY,
    ZELDA,
    check_bridge_around_the_escape,
    check_count_gate,
    check_courtyard,
    check_send_off,
    door_flow,
    index,
    latest,
    outcome,
    reach,
    reference,
)

from clawshot.formats import byml, evfl, rstb, zsdic
from clawshot.generate import Settings
from clawshot.patch import darunia, door, make_seed
from clawshot.patch.gamedata import GAME_DATA_LIST
from clawshot.patch.plan import PatchError
from clawshot.save import key

BOOLS = (False, True)
OWNED_STONES = ("IsGet.Item_Stone_Forest", "IsGet.Item_Stone_Fire", "IsGet.Item_Stone_Water")
TIME_OCARINA = "IsGet.Item_Ocarina_Time"
FAIRY_OCARINA = "IsGet.Item_Ocarina_Fairy"  # never enough: the door wants the Ocarina of Time
TIME_SONG = "IsGet.Item_Melody_TimeSong"
SENDOFF = "HavePlayedEvent.Dm_HrlField_0020"  # Impa's real send-off
REQUIREMENTS = (*OWNED_STONES, TIME_OCARINA, TIME_SONG, SENDOFF)
OPENED = "Market_Child_TimeTempleDoor_Opened"  # the saved once-only latch
SCENE = "Dm_TimeTemple_0010"  # the opening scene
OPENING = f"HavePlayedEvent.{SCENE}"  # its saved history
REACTION = "Market_Child_TimeTempleDoor_OcarinaReacts"  # unsaved; true means the altar does not react
STEP_GATE = "DoorOfTime_IsAfter_Step04_Exp"  # native Event60's read
QUESTS = tuple(f"Step_Get_StoneOf{stone}" for stone in ("Forest", "Fire", "Water"))  # stone quest completion
# Native REACTION, build e0f3ccfa: not exactly Step05, or opened. Commands are (opcode, operand names...).
NATIVE_REACTION = ((1, "Step_DoorOfTime"), (2, "Step05"), (5,), (0, OPENED), (4,))
GUARDED_STEPS = ("Step02", "Step2_1", "Srep2_1_1", "Step2_2", "Step03", "Step04", "Step05", "Step06")
EARLY_STORY = "open"  # test_door_story's reference engine: the early modes' shared forward-only story
# A reward-on closed seed writes song_only's set: the story flows, GameData, the four stage modules and the table.
GROWN = (DOOR, SARIA, ZELDA, ERA_FLOW, CASTLE, GAME_DATA_LIST)
WRITTEN = (*GROWN, *STAGE_MODULES, SIZE_TABLE)
SEED = 180501  # the track's own native seed (r18-rewards.md), never a player seed


def bits(values):
    return "".join("1" if value else "0" for value in values)


def saved_bool(name: str) -> dict:
    return {
        "DefaultValue": False,
        "Hash": byml.U32(key(name)),
        "ResetTypeValue": byml.I32(8),
        "SaveFileIndex": byml.I32(0),
    }


def expression_row(name: str, commands) -> dict:
    """An unsaved BoolExp row as the game stores it."""
    return {
        "Hash": byml.U32(key(name)),
        "ResetTypeValue": byml.I32(0),
        "SaveFileIndex": byml.I32(-1),
        "Values": [[byml.U64(op), *(byml.U64(key(operand)) for operand in operands)] for op, *operands in commands],
    }


def after_row(step: str) -> dict:
    return expression_row(f"DoorOfTime_IsAfter_{step}_Exp", ((12, "Step_DoorOfTime"), (2, step)))


def game_data() -> dict:
    """test_door_stage's native-shaped rows plus the altar's: the six saved inputs, the Fairy Ocarina, the latch and
    the opening history, the native reaction and every strict Door step row the forward guards read."""
    tree = synthetic_game_data()
    data = tree["Data"]
    present = {int(row["Hash"]) for rows in data.values() for row in rows}
    names = (*REQUIREMENTS, FAIRY_OCARINA, OPENED, OPENING)
    data["Bool"] += [saved_bool(name) for name in names if key(name) not in present]
    data["BoolExp"].append(expression_row(REACTION, NATIVE_REACTION))
    missing = [step for step in GUARDED_STEPS if key(f"DoorOfTime_IsAfter_{step}_Exp") not in present]
    data["BoolExp"] += [after_row(step) for step in missing]
    return tree


def reward_changes():
    return door.changes({}, mode="closed", dungeon_rewards=True)


def closed_changes():
    return door.changes({}, mode="closed")


def written(changes) -> dict:
    """The synthetic GameData as ``changes`` ship it; untouched where they do not change it."""
    data = byml.write(game_data())
    return byml.read(changes[GAME_DATA_LIST](data) if GAME_DATA_LIST in changes else data)


@cache
def reward_rows():
    return indexed(written(reward_changes()))


def synthetic_sources() -> dict[str, bytes]:
    return {path: evfl.write(build()) for path, build in FLOWS.items()}


def ship(sources, changes):
    """``sources`` (path -> decompressed flow) as a seed with ``changes`` ships them, and as they are; the door flow
    with Darunia's Fire guard either way, as every seed composes it (``test_door_story.flows_for``)."""
    fire = darunia.changes()[darunia.DOOR_FLOW]
    shipped, base = {}, {}
    for path, data in sources.items():
        new = changes[path](data) if path in changes else data
        old = data
        if path == DOOR:
            new, old = fire(new), fire(old)
        shipped[path], base[path] = evfl.read(new).flowchart, evfl.read(old).flowchart
    return shipped, base


@cache
def altars():
    """The owned altar twice: the pure Event60 edit on test_door's native-shaped chain (Step06 always written), and
    the full synthetic story as a reward-on closed seed ships it (Step06 behind its forward guard)."""
    shipped, _ = ship(synthetic_sources(), reward_changes())
    gate = evfl.read(door._owned_stone_flow(evfl.write(synthetic_flow()))).flowchart
    return ((gate, False), (shipped[DOOR], True))


def open_door(fc, rows, state, *, recommended=True):
    """The altar's song from ``state``: (scenes, saved writes, state after), BoolExp read from ``rows``."""
    after = dict(state)
    scenes, writes = run_open_flow(
        fc, after, expression=lambda name, now: evaluate(rows, key(name), now), recommended=recommended
    )
    return scenes, writes, after


def opened_writes(step: str, guarded: bool) -> list[str]:
    """The opening's saved writes: the latch, then Step06 unless a forward guard sees the quest already past it."""
    past = guarded and STEPS.index(step) > STEPS.index("Step06")
    return [OPENED] if past else [OPENED, "Step_DoorOfTime"]


def door_writes(effects):
    return [effect for effect in effects if effect[1] == STEP and effect[2]["ChallengeName"] == "DoorOfTime"]


def content(dictionaries, root, path) -> bytes:
    data = (root / path).read_bytes()
    return dictionaries.decompress(path, data) if path.endswith(".zs") else data


def reaction_of(tree: dict) -> dict:
    return next(row for row in tree["Data"]["BoolExp"] if row["Hash"] == key(REACTION))


# The altar: ownership, not completion; once; the recommended song.


@pytest.mark.parametrize("owned", list(product(BOOLS, repeat=len(REQUIREMENTS))), ids=bits)
def test_the_altar_opens_exactly_with_the_six_inputs_once_and_on_the_recommended_song(owned):
    """Every subset of the stones, Time ocarina, song and send-off, against the latch, the opening history, the
    recommended melody, the Door step, stone quest completion, the Fairy Ocarina and the Field owl arrival."""
    rows = reward_rows()
    inputs = dict(zip(REQUIREMENTS, owned, strict=True))
    steps = ("Step01", "Step02", "Step05", "Complete")
    for (fc, guarded), opened, played, recommended, noise, step, quest in product(
        altars(), BOOLS, BOOLS, BOOLS, BOOLS, steps, ("Ready", "Complete")
    ):
        state = {**inputs, OPENED: opened, OPENING: played, FAIRY_OCARINA: noise, ARRIVED: noise}
        state |= {"Step_DoorOfTime": step, **dict.fromkeys(QUESTS, quest)}
        scenes, writes, after = open_door(fc, rows, state, recommended=recommended)
        success = all(owned) and not opened and not played and recommended
        assert scenes == ([SCENE] if success else []), state
        assert writes == (opened_writes(step, guarded) if success else []), state
        assert {name: after[name] for name in (*REQUIREMENTS, *QUESTS)} == {
            name: state[name] for name in (*REQUIREMENTS, *QUESTS)
        }, "the door forged an input or a quest"


@pytest.mark.parametrize("stones", list(product(BOOLS, repeat=3)), ids=bits)
def test_owned_stones_open_the_door_where_completed_quests_alone_do_not(stones):
    """Each stone ownership subset at every Door step and stone quest completion state, the rest of the kit owned:
    rewards on, the three owned stones open it with any quest incomplete and completion without them never does;
    rewards off, the same states open on the native Door step alone (past Step04), whatever is owned."""
    rows = reward_rows()
    off_rows = indexed(written(closed_changes()))
    off, _ = ship(synthetic_sources(), closed_changes())
    kit = {**dict(zip(OWNED_STONES, stones, strict=True)), TIME_OCARINA: True, TIME_SONG: True, SENDOFF: True}
    kit |= {OPENED: False, OPENING: False}
    for step, quests in product(STEPS, product(("Ready", "Complete"), repeat=3)):
        state = {**kit, "Step_DoorOfTime": step, **dict(zip(QUESTS, quests, strict=True))}
        for fc, _ in altars():
            assert bool(open_door(fc, rows, state)[0]) is all(stones), state
        native = STEPS.index(step) > STEPS.index("Step04")
        assert bool(open_door(off[DOOR], off_rows, state)[0]) is native, state


def test_the_opening_plays_once_and_then_the_altar_never_reacts():
    rows = reward_rows()
    full = {**dict.fromkeys(REQUIREMENTS, True), OPENED: False, OPENING: False, "Step_DoorOfTime": "Step02"}
    full |= dict.fromkeys(QUESTS, "Ready")
    for fc, _ in altars():
        scenes, writes, after = open_door(fc, rows, full)
        assert (scenes, writes, after[OPENED], after["Step_DoorOfTime"]) == (
            [SCENE],
            [OPENED, "Step_DoorOfTime"],
            True,
            "Step06",
        )
        assert open_door(fc, rows, after)[:2] == ([], [])  # the saved latch refuses a replay
        assert open_door(fc, rows, {**full, OPENING: True})[:2] == ([], [])  # so does the opening's history alone
        assert open_door(fc, rows, full, recommended=False)[:2] == ([], [])  # another melody
    for owned in product(BOOLS, repeat=len(REQUIREMENTS)):
        assert evaluate(rows, key(REACTION), {**dict(zip(REQUIREMENTS, owned, strict=True)), OPENED: True}) is True


def test_the_altar_reaction_is_exactly_the_opening_refusal():
    """REACTION, read with only the six inputs and the latch (any other Bool or Enum read fails), is true exactly
    when the altar refuses a recommended song with the opening unplayed; both altars agree in every state."""
    rows = reward_rows()
    for values in product(BOOLS, repeat=len(REQUIREMENTS) + 1):
        minimal = dict(zip((*REQUIREMENTS, OPENED), values, strict=True))
        reaction = evaluate(rows, key(REACTION), minimal)
        assert reaction is (minimal[OPENED] or not all(values[:-1])), minimal
        for (fc, _), played, recommended in product(altars(), BOOLS, BOOLS):
            state = {**minimal, OPENING: played, "Step_DoorOfTime": "Step02"}
            scenes, _, _ = open_door(fc, rows, state, recommended=recommended)
            assert bool(scenes) is (not reaction and not played and recommended), state


# Exact inverse: the existing early story and stage, Event60 and the reaction's values aside.


def test_only_event60_changes_on_the_existing_early_story():
    """The pure gate edit changes Event60 alone. A reward-on closed seed's story flows are open mode's guarded story
    (the round16 edits) with only that event changed; no other event, entry, actor or flow differs."""
    original = synthetic_flow()
    gated = evfl.read(door._owned_stone_flow(evfl.write(original)))
    assert gated.flowchart.events[3] == evfl.SwitchEvent("Event60", 0, 0, [(1, 4)], {"GameDataName": REACTION})
    gated.flowchart.events[3] = original.flowchart.events[3]
    assert gated == original
    reward, early = reward_changes(), door.changes({}, mode="open")
    for path, data in synthetic_sources().items():
        shipped, story = evfl.read(reward[path](data)), evfl.read(early[path](data))
        if path == DOOR:
            fc = story.flowchart
            at = index(fc, "Event60")
            native = fc.events[at]
            assert native.params == {"GameDataName": STEP_GATE}
            owned = evfl.SwitchEvent(
                "Event60", native.actor, native.query, [(1, index(fc, "Event69"))], {"GameDataName": REACTION}
            )
            assert shipped.flowchart.events[at] == owned
            shipped.flowchart.events[at] = native
        assert shipped == story, path


def test_written_game_data_is_the_early_stage_with_only_the_reaction_changed():
    source = game_data()
    new = written(reward_changes())
    early = written(door.changes({}, mode="song_only"))
    assert not byml.same(reaction_of(new)["Values"], reaction_of(early)["Values"])
    reaction_of(new)["Values"] = reaction_of(early)["Values"]
    assert byml.same(new, early)  # the four stage rows, every saved row and default, the save layout
    count = len(source["Data"]["BoolExp"])
    added = new["Data"]["BoolExp"][count:]
    assert [row["Hash"] for row in added] == [key(name) for name in ADDED]
    assert all((row["ResetTypeValue"], row["SaveFileIndex"]) == (0, -1) for row in added)
    del new["Data"]["BoolExp"][count:]
    reaction_of(new)["Values"] = reaction_of(source)["Values"]
    assert byml.same(new, source)


@pytest.mark.parametrize("mode", MODES)
def test_the_reward_flag_changes_only_the_closed_door(mode):
    """Both early modes are unchanged with rewards on; the closed door ships the guarded story, never the
    open-mode ungated pedestal."""
    sources = {**synthetic_sources(), GAME_DATA_LIST: byml.write(game_data())}

    def shipped(changes):
        return {path: change(sources[path]) for path, change in changes.items() if path in sources}

    off = door.changes({}, mode=mode, dungeon_rewards=False)
    on = door.changes({}, mode=mode, dungeon_rewards=True)
    if mode == "closed":
        assert on.keys() == door.changes({}, mode="song_only").keys()
        assert door.PLACEMENT not in on and shipped(on) != shipped(off)
    else:
        assert on.keys() == off.keys() and shipped(on) == shipped(off)


# The story around an owned opening: forward-only, the escape and moat still on quest completion.


@pytest.mark.parametrize("path", PATHS)
def test_every_other_entry_plays_as_the_early_story_promises(path):
    """Every entry but the altar's (tested above) plays on the reference engine as the early modes' story promises;
    the Door quest never moves back."""
    flows, base = ship(synthetic_sources(), reward_changes())
    new, old = flows[path], base[path]
    for entry, current in product(old.entry_points, STEPS):
        if (path, entry.name) == (DOOR, "DoorOfTime_OpenDoor"):
            continue
        for (fire, water), (sendoff, escaped) in product(STONES, product(BOOLS, repeat=2)):
            stones = {"Step_Get_StoneOfFire": fire, "Step_Get_StoneOfWater": water}
            state = {**START, **stones, "Step_DoorOfTime": current, SENDOFF: sendoff, ESCAPED: escaped}
            effects, final = outcome(new, entry.name, state)
            promised = outcome(old, entry.name, state, **reference(EARLY_STORY, path))
            assert (effects, final) == promised, (entry.name, state)
            if path in STORY:
                assert STEPS.index(final["Step_DoorOfTime"]) >= STEPS.index(current)


def test_counts_send_off_courtyard_and_bridge_keep_the_early_story_promises():
    flows, base = ship(synthetic_sources(), reward_changes())
    check_courtyard(flows, base)
    check_count_gate(flows, base, EARLY_STORY)
    check_send_off(flows, base, EARLY_STORY)
    for before in ("Step2_2", "Step06", "Complete"):
        check_bridge_around_the_escape(flows, base, before)


def test_an_owned_opening_before_the_quests_keeps_every_later_scene_and_never_rewinds():
    """Stones owned from elsewhere, no stone quest complete: the door opens right after the send-off and Rauru
    completes the quest. The later Fire and Water quests still count, raise the bridge, ready the escape, then the
    moat, then retire its areas; nothing writes the Door quest back. The existing closed repair alone would rewind
    the same count to Step03."""
    flows, _ = ship(synthetic_sources(), reward_changes())
    fc, rows = flows[DOOR], reward_rows()
    state = {**START, **dict.fromkeys(REQUIREMENTS, True), "Step_DoorOfTime": "Step02", COLLECTED: False}
    state |= dict.fromkeys(QUESTS, "Ready")

    def ready(now):
        return tuple(evaluate(rows, key(name), now) for name in (ESCAPE_READY, MOAT_READY, MOAT_AREAS_DONE))

    assert ready(state) == (False, False, False)
    scenes, writes, state = open_door(fc, rows, state)
    assert (scenes, writes, state["Step_DoorOfTime"]) == ([SCENE], [OPENED, "Step_DoorOfTime"], "Step06")
    _, state = outcome(fc, "SageRoom_MeetRauru", state)  # the first pull
    assert state["Step_DoorOfTime"] == "Complete"
    assert ready(state) == (False, False, False)  # completion, not the owned stones, readies the escape
    late = state
    for stone in ("Fire", "Water"):
        state = {**state, f"Step_Get_StoneOf{stone}": "Complete"}
        effects, state = outcome(fc, COUNT, state)
        assert door_writes(effects) == [] and state["Step_DoorOfTime"] == "Complete"
    assert state[BRIDGE] is True
    assert ready(state) == (True, False, False)
    effects, state = outcome(fc, "DoorOfTime_Escape", state)
    state = {**state, ESCAPED: True}  # the engine records the played escape
    assert door_writes(effects) == [] and (state["Step_DoorOfTime"], state[BRIDGE]) == ("Complete", False)
    assert ready(state) == (False, True, False)
    effects, state = outcome(fc, "Dm_MelodyGet_Time_After", state)
    state = {**state, COLLECTED: True}  # the engine records the moat's song scene
    assert door_writes(effects) == [] and state["Step_DoorOfTime"] == "Complete"
    assert ready(state) == (False, False, True)
    assert outcome(fc, COUNT, state) == ([], state)
    assert open_door(fc, rows, state)[:2] == ([], [])
    closed, _ = ship(synthetic_sources(), closed_changes())
    both = {**late, "Step_Get_StoneOfFire": "Complete", "Step_Get_StoneOfWater": "Complete"}
    assert outcome(closed[DOOR], COUNT, both)[1]["Step_DoorOfTime"] == "Step03"


def test_escape_and_moat_readiness_follow_quest_completion_never_owned_stones():
    rows = reward_rows()
    wrong = []
    for story, owned in product(stories(), BOOLS):
        state = {**story.state(), **dict.fromkeys(OWNED_STONES, owned), TIME_OCARINA: owned}
        want = expected(story)
        model = (want["escape_area"], want["moat_ocarina"], want["areas_gone"][0])
        actual = tuple(evaluate(rows, key(name), state) for name in SCENE_GATES)
        if actual != model:
            wrong.append((story, owned, actual))
    assert not wrong, wrong[:3]


# Refusals.


def _gate_reads(fc):
    fc.events[index(fc, "Event60")].params = {"GameDataName": "DoorOfTime_IsAfter_Step03_Exp"}


def _gate_target(fc):
    fc.events[index(fc, "Event60")].cases = [(0, index(fc, "Event58"))]


def _latch(fc):
    fc.events[index(fc, "Event69")].params = {"GameDataName": "Unrelated.Saved", "Index": -1}


@pytest.mark.parametrize("mutate", [_gate_reads, _gate_target, _latch])
def test_a_changed_native_opening_gate_is_refused(mutate):
    document = door_flow()
    mutate(document.flowchart)
    with pytest.raises(PatchError, match="owned-stone door"):
        reward_changes()[DOOR](evfl.write(document))


def test_a_changed_reaction_or_a_second_application_is_refused():
    changes = reward_changes()
    with pytest.raises(PatchError, match="owned-stone door"):
        changes[DOOR](changes[DOOR](evfl.write(door_flow())))
    with pytest.raises(PatchError, match="altar reaction"):
        changes[GAME_DATA_LIST](changes[GAME_DATA_LIST](byml.write(game_data())))
    tree = game_data()
    reaction_of(tree)["Values"][1] = [byml.U64(2), byml.U64(key("Step04"))]
    with pytest.raises(PatchError, match="altar reaction"):
        changes[GAME_DATA_LIST](byml.write(tree))


@pytest.mark.parametrize("mode", ["unsupported", None])
def test_bad_modes_are_refused_with_rewards_shuffled(mode, tmp_path):
    with pytest.raises(PatchError, match="unknown"):
        door.changes({}, mode=mode, dungeon_rewards=True)
    with pytest.raises(PatchError, match="unknown"):
        door.build(tmp_path, mode=mode, dungeon_rewards=True)


# Native dump: the real flows, GameData and modules through the public patch.


@pytest.fixture(scope="module")
def native(romfs):
    """The dictionaries, the real story flows (decompressed), GameData and its quest step orders."""
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    flows = {path: dictionaries.decompress(path, (romfs / path).read_bytes()) for path in PATHS}
    game = dictionaries.decompress(GAME_DATA_LIST, (romfs / GAME_DATA_LIST).read_bytes())
    enums = {int(row["Hash"]): row for row in byml.read(game)["Data"]["Enum"]}
    quests = ("DoorOfTime", "Get_StoneOfFire", "Get_StoneOfWater")
    orders = {quest: tuple(enums[key(f"Step_{quest}")]["RawValues"]) for quest in quests}
    return dictionaries, flows, game, {**ORDERS, **orders}


@pytest.fixture(scope="module")
def overlays(romfs, tmp_path_factory):
    """Each standalone overlay, written once: (its romfs folder, the resources write reported)."""
    cache = {}

    def get(mode, rewards):
        if (mode, rewards) not in cache:
            out = tmp_path_factory.mktemp(f"{mode}-{rewards}") / "out"
            cache[mode, rewards] = (out / "romfs", door.write(romfs, out, mode=mode, dungeon_rewards=rewards))
        return cache[mode, rewards]

    return get


@pytest.mark.dump
def test_dump_the_gate_reads_saved_native_bools_and_only_the_altar_reaches_it(native):
    """The six inputs, the Fairy Ocarina, the latch and the opening history are saved native Bools, false from New
    Game; the reaction and the strict Door step rows are this file's synthetic ones. Native Event60 follows the
    played song (Event92) and precedes the latch, history and recommended-melody checks; no other entry reaches it."""
    _, flows, game, _ = native
    data = byml.read(game)["Data"]
    bools = {int(row["Hash"]): row for row in data["Bool"]}
    for name in (*REQUIREMENTS, FAIRY_OCARINA, OPENED, OPENING):
        assert byml.same(bools[key(name)], saved_bool(name)), name
    expressions = {int(row["Hash"]): row for row in data["BoolExp"]}
    assert byml.same(expressions[key(REACTION)], expression_row(REACTION, NATIVE_REACTION))
    for step in GUARDED_STEPS:
        assert byml.same(expressions[key(f"DoorOfTime_IsAfter_{step}_Exp")], after_row(step)), step
    fc = evfl.read(flows[DOOR]).flowchart

    def at(name):
        return index(fc, name)

    def asks(event):
        actor = fc.actors[event.actor]
        return actor.name, actor.queries[event.query], event.params, event.cases

    entry = fc.entry_point("DoorOfTime_OpenDoor")
    assert entry.main_event == at("Event18") and fc.events[at("Event18")].next == at("Event27")
    assert fc.events[at("Event27")].next == at("Event92") and fc.events[at("Event92")].next == at("Event60")
    data_actor = "GameDataActor"
    gate = (data_actor, "EventQueryIsGameDataBoolExp", {"GameDataName": STEP_GATE}, [(0, at("Event69"))])
    assert asks(fc.events[at("Event60")]) == gate
    latch = (data_actor, "EventQueryIsGameDataBool", {"GameDataName": OPENED, "Index": -1}, [(1, at("Event58"))])
    assert asks(fc.events[at("Event69")]) == latch
    history = (data_actor, "EventQueryHavePlayedEvent", {"EventName": SCENE}, [(1, at("Event28"))])
    assert asks(fc.events[at("Event58")]) == history
    melody = asks(fc.events[at("Event28")])
    assert melody[:2] == ("GameSystemActor", "EventQueryIsRecommendedMelody") and [c for c, _ in melody[3]] == [0]
    reaching = [other.name for other in fc.entry_points if at("Event60") in reach(fc, other.main_event)]
    assert reaching == ["DoorOfTime_OpenDoor"]


@pytest.mark.dump
def test_dump_written_altar_opens_on_ownership_where_rewards_off_needs_completion(native, overlays):
    dictionaries, _, game, _ = native
    root, _ = overlays("closed", True)
    off_root, _ = overlays("closed", False)
    on = evfl.read(content(dictionaries, root, DOOR)).flowchart
    off = evfl.read(content(dictionaries, off_root, DOOR)).flowchart
    rows = indexed(byml.read(content(dictionaries, root, GAME_DATA_LIST)))
    assert not (off_root / GAME_DATA_LIST).exists()
    native_rows = indexed(byml.read(game))
    for owned, step, quest in product(
        product(BOOLS, repeat=len(REQUIREMENTS)), ("Step02", "Step05", "Complete"), ("Ready", "Complete")
    ):
        state = {**dict(zip(REQUIREMENTS, owned, strict=True)), OPENED: False, OPENING: False}
        state |= {"Step_DoorOfTime": step, **dict.fromkeys(QUESTS, quest)}
        scenes, writes, after = open_door(on, rows, state)
        assert scenes == ([SCENE] if all(owned) else []), state
        assert writes == (opened_writes(step, True) if all(owned) else []), state
        if all(owned):
            assert after["Step_DoorOfTime"] == latest(step, "Step06")
            assert open_door(on, rows, after)[:2] == ([], [])
        native_scenes, _, _ = open_door(off, native_rows, state)
        assert bool(native_scenes) is (STEPS.index(step) > STEPS.index("Step04")), state
    full = {**dict.fromkeys(REQUIREMENTS, True), OPENED: False, OPENING: False, "Step_DoorOfTime": "Step02"}
    full |= dict.fromkeys(QUESTS, "Ready")
    assert open_door(on, rows, full, recommended=False)[:2] == ([], [])
    assert open_door(on, rows, {**full, OPENED: True})[:2] == ([], [])
    assert open_door(on, rows, {**full, OPENING: True})[:2] == ([], [])
    for values in product(BOOLS, repeat=len(REQUIREMENTS) + 1):
        minimal = dict(zip((*REQUIREMENTS, OPENED), values, strict=True))
        assert evaluate(rows, key(REACTION), minimal) is (minimal[OPENED] or not all(values[:-1])), minimal


@pytest.mark.dump
def test_dump_reward_door_writes_the_early_story_set_without_the_physical_door(romfs, native, overlays):
    dictionaries = native[0]
    root, written_files = overlays("closed", True)
    song_root, song_files = overlays("song_only", False)
    expected_paths = sorted(WRITTEN)
    assert sorted(file.path for file in written_files) == expected_paths == sorted(file.path for file in song_files)
    on_disk = sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file())
    assert on_disk == expected_paths
    assert not {door.PLACEMENT, COMMON_GATE} & set(on_disk)
    for path in (SARIA, ZELDA, ERA_FLOW, CASTLE, *STAGE_MODULES):
        assert content(dictionaries, root, path) == content(dictionaries, song_root, path), path
    native_table = rstb.read(dictionaries.decompress(SIZE_TABLE, (romfs / SIZE_TABLE).read_bytes()))
    table = rstb.read(dictionaries.decompress(SIZE_TABLE, (root / SIZE_TABLE).read_bytes()))
    assert (table.version, table.names) == (native_table.version, native_table.names)
    digests = native_table.hashes.keys() | table.hashes.keys()
    changed = {digest for digest in digests if native_table.hashes.get(digest) != table.hashes.get(digest)}
    assert changed == {rstb.path_hash(path) for path in GROWN}
    for path in GROWN:
        assert table.get(path) >= rstb.required_size(path, len(content(dictionaries, root, path)))


@pytest.mark.dump
def test_dump_door_flow_is_the_early_story_with_only_event60_owned(native, overlays):
    dictionaries, flows, _, _ = native
    root, _ = overlays("closed", True)
    open_root, _ = overlays("open", False)
    shipped = evfl.read(content(dictionaries, root, DOOR))
    story = evfl.read(content(dictionaries, open_root, DOOR))
    fc = story.flowchart
    at = index(fc, "Event60")
    gate = fc.events[at]
    owned = evfl.SwitchEvent("Event60", gate.actor, gate.query, [(1, index(fc, "Event69"))], {"GameDataName": REACTION})
    assert shipped.flowchart.events[at] == owned
    shipped.flowchart.events[at] = gate
    assert shipped == story
    native_flow = evfl.read(flows[DOOR])
    assert unpatch_story(native_flow, shipped, DOOR, mode=EARLY_STORY) == native_flow


@pytest.mark.dump
def test_dump_game_data_is_the_early_stage_with_only_the_reaction_changed(native, overlays):
    dictionaries, _, game, _ = native
    root, _ = overlays("closed", True)
    song_root, _ = overlays("song_only", False)
    new = byml.load(content(dictionaries, root, GAME_DATA_LIST))
    early = byml.load(content(dictionaries, song_root, GAME_DATA_LIST))
    old = byml.load(game)
    assert new.byte_order == early.byte_order == old.byte_order
    reaction_of(new.root)["Values"] = reaction_of(early.root)["Values"]
    assert byml.same(new.root, early.root)
    rows = new.root["Data"]["BoolExp"]
    hashes = {key(name) for name in ADDED}
    added = [row for row in rows if row["Hash"] in hashes]
    assert sorted(row["Hash"] for row in added) == sorted(hashes)
    assert all((row["ResetTypeValue"], row["SaveFileIndex"]) == (0, -1) for row in added)
    rows[:] = [row for row in rows if row["Hash"] not in hashes]
    reaction_of(new.root)["Values"] = reaction_of(old.root)["Values"]
    assert byml.same(old.root, new.root)  # every saved flag, default, other row and the save layout metadata


@pytest.mark.dump
@pytest.mark.parametrize("mode", ("song_only", "open"))
def test_dump_both_early_modes_are_byte_identical_with_reward_shuffle(overlays, mode):
    def files(root):
        return {path.relative_to(root).as_posix(): path.read_bytes() for path in root.rglob("*") if path.is_file()}

    off_root, off_files = overlays(mode, False)
    on_root, on_files = overlays(mode, True)
    assert on_files == off_files and files(on_root) == files(off_root)


@pytest.mark.dump
def test_dump_the_real_story_keeps_the_early_promises_around_an_owned_opening(native):
    _, flows, _, orders = native
    shipped, base = ship(flows, reward_changes())
    check_courtyard(shipped, base, orders)
    check_count_gate(shipped, base, EARLY_STORY, orders)
    check_send_off(shipped, base, EARLY_STORY, orders)
    for before in ("Step2_2", "Step06", "Complete"):
        check_bridge_around_the_escape(shipped, base, before, orders)


@pytest.mark.dump
def test_dump_escape_and_moat_follow_quest_completion_after_an_owned_opening(romfs, native):
    """The built Field modules are song_only's (never the Temple door module) and, with the written GameData, every
    story state plays the escape and moat as the independent model says: Fire and Water completion, not ownership."""
    _, _, game, _ = native
    built = door.build(romfs, mode="closed", dungeon_rewards=True)
    assert built == door.build(romfs, mode="song_only")
    by_path = {file.path: file for file in built}
    assert sorted(by_path) == sorted(layout.path for layout in LAYOUTS.values())
    modules = {name: by_path[layout.path].content for name, layout in LAYOUTS.items()}
    stage = Stage("closed+rewards", modules, by_path, byml.read(reward_changes()[GAME_DATA_LIST](game)))
    wrong = []
    for story in stories():
        if (actual := stage.signals(story)) != (want := expected(story)):
            wrong.append((story, actual, want))
        if stage.signals(story, outside=False)["moat_event"]:
            wrong.append((story, "moat event while the player stands in a sensor area"))
    assert not wrong, f"{len(wrong)} wrong states, first {wrong[:3]}"


@pytest.mark.dump
def test_dump_the_native_temple_door_stays_open_after_an_owned_opening(romfs, native):
    """The unwritten Temple door module opens on the owned opening's Step06 and stays open through the late Fire
    and Water count; the existing closed repair alone would rewind the quest to Step03 and shut it."""
    _, flows, game, orders = native
    module = (romfs / COMMON_GATE).read_bytes()
    assert hashlib.sha256(module).hexdigest() == COMMON_GATE_SHA256
    shipped, _ = ship(flows, reward_changes())
    closed, _ = ship(flows, closed_changes())
    rows = indexed(byml.read(reward_changes()[GAME_DATA_LIST](game)))
    reader = Stage("native", {}, {}, {"Data": {"Bool": [], "BoolExp": [], "Enum": []}})
    state = {**START, **dict.fromkeys(REQUIREMENTS, True), "Step_DoorOfTime": "Step02"}
    state |= dict.fromkeys(QUESTS, "Ready")
    assert door_signals(module, reader, state, proxy=False) == (False, False)
    scenes, _, state = open_door(shipped[DOOR], rows, state)
    assert (scenes, state["Step_DoorOfTime"]) == ([SCENE], "Step06")
    assert door_signals(module, reader, state, proxy=False) == (True, True)
    for current in ("Step06", "Complete"):  # Complete: Rauru's native write at the first pull
        late = {**state, "Step_DoorOfTime": current, "Step_Get_StoneOfFire": "Complete"}
        late["Step_Get_StoneOfWater"] = "Complete"
        effects, counted = outcome(shipped[DOOR], COUNT, late, orders=orders)
        assert door_writes(effects) == [] and (counted["Step_DoorOfTime"], counted[BRIDGE]) == (current, True)
        assert door_signals(module, reader, counted, proxy=False) == (True, True)
        _, rewound = outcome(closed[DOOR], COUNT, late, orders=orders)
        assert rewound["Step_DoorOfTime"] == "Step03"
        assert door_signals(module, reader, rewound, proxy=False) == (False, False)


@pytest.mark.dump
def test_dump_a_reward_seed_ships_the_owned_door_with_its_story_and_stage(romfs, native):
    """A real reward-on closed seed (make_seed): its composed door flow and GameData open on ownership, not
    completion; its late Door, Saria and Zelda writes cannot rewind a pulled quest; the escape still waits for the
    quests; it ships the four stage modules and never the Temple door module."""
    _, flows, game, orders = native
    output = make_seed(romfs, SEED, Settings(dungeon_rewards=True, door_of_time="closed"))

    def composed(path):
        data = flows.get(path, game)
        for changes in output.extra_changes:
            if path in changes:
                data = changes[path](data)
        return data

    fc = evfl.read(composed(DOOR)).flowchart
    rows = indexed(byml.read(composed(GAME_DATA_LIST)))
    stage = door.build(romfs, mode="closed", dungeon_rewards=True)
    shipped = {file.path: file for file in output.fast_start_files}
    assert [shipped.get(file.path) for file in stage] == stage
    assert COMMON_GATE not in shipped
    kit = {TIME_OCARINA: True, TIME_SONG: True, SENDOFF: True, OPENED: False, OPENING: False}
    for owned, step, quest in product(BOOLS, ("Step02", "Step05"), ("Ready", "Complete")):
        state = {**kit, **dict.fromkeys(OWNED_STONES, owned), "Step_DoorOfTime": step, **dict.fromkeys(QUESTS, quest)}
        assert bool(open_door(fc, rows, state)[0]) is owned, state
    pulled = {**START, "Step_DoorOfTime": "Complete", "Step_Get_StoneOfFire": "Complete"}
    pulled["Step_Get_StoneOfWater"] = "Complete"
    effects, counted = outcome(fc, COUNT, pulled, orders=orders)
    assert door_writes(effects) == [] and counted["Step_DoorOfTime"] == "Complete"
    for path, writer in ((SARIA, "Event172"), (ZELDA, "Event42")):
        talk = evfl.read(composed(path)).flowchart
        assert outcome(talk, index(talk, writer), pulled, orders=orders) == ([], pulled), path
    escape = {"Step_DoorOfTime": "Complete", "Step_Get_StoneOfFire": "Complete", "Step_Get_StoneOfWater": "Complete"}
    escape |= {SENDOFF: True, ESCAPED: False}
    assert evaluate(rows, key(ESCAPE_READY), escape) is True
    assert evaluate(rows, key(ESCAPE_READY), {**escape, "Step_Get_StoneOfWater": "Ready"}) is False
