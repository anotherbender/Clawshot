"""Replay the memory game's serial reward boundary; no minigame engine or game-data fixture."""

from copy import deepcopy

import pytest

from clawshot.census.gifts import Gift
from clawshot.formats import evfl, zsdic
from clawshot.patch import gifts

FLOW = gifts.SKULL_KID_FLOW
PATH = f"Event/EventFlow/{FLOW}.bfevfl.zs"
FLAG = gifts.SKULL_KID_FLAG
GRADE = "Minigame_SkullKidSession_CurrentGradeSoundNumForSession"
RALLY = "Minigame_SkullKidSession_CurrentRallyCount"


def change(item="Item_Boomerang"):
    step = Gift(
        f"{FLOW}/Event24",
        "npc_gift",
        FLOW,
        "synthetic",
        ("Win",),
        "Event24",
        "Dm_SY_GetInEvent:GetInEvent_NotTurn_NotNpc",
        "ActorName",
        "Obj_Heart_Piece",
        "",
    )
    return gifts.GiftChange(gifts.load()[gifts.SKULL_KID_CHECK], (step,), item)


def reward_chart():
    names = [
        "Event178",
        "Event9",
        "Event10",
        "Event11",
        "Event12",
        "Event22",
        "Event23",
        "Event24",
        "Event58",
        "Event64",
        "Event68",
        "Event154",
        "Event244",
        "Event243",
        "End",
    ]
    index = {name: i for i, name in enumerate(names)}

    def action(name, key, value, target, boolean=False):
        return evfl.ActionEvent(
            name, 0, int(boolean), index[target], {"GameDataName": key, "Index": -1, "Value": value}
        )

    def grant(name, item, target):
        return evfl.SubFlowEvent(
            name,
            "Dm_SY_GetInEvent",
            "GetInEvent_NotTurn_NotNpc",
            index[target],
            {"ActorName": item, "IsNpcEventStarter": False},
        )

    events = [
        evfl.JoinEvent("Event178", index["Event9"]),
        evfl.SwitchEvent(
            "Event9",
            0,
            0,
            [(0, index["Event244"]), (1, index["Event10"]), (2, index["Event10"])],
            {"GameDataName": GRADE, "Value": 6, "Index": -1},
        ),
        evfl.SwitchEvent(
            "Event10",
            0,
            0,
            [(0, index["Event243"]), (1, index["Event68"]), (2, index["End"])],
            {"GameDataName": GRADE, "Value": 8, "Index": -1},
        ),
        action("Event11", GRADE, 6, "Event22"),
        action("Event12", GRADE, 8, "Event23"),
        grant("Event22", "Obj_Rupee_Blue", "End"),
        grant("Event23", "Obj_Rupee_Red", "End"),
        grant("Event24", "Obj_Heart_Piece", "Event58"),
        action("Event58", FLAG, True, "End", boolean=True),
        evfl.SwitchEvent(
            "Event64", 0, 1, [(0, index["Event154"]), (1, index["Event24"])], {"GameDataName": FLAG, "Index": -1}
        ),
        action("Event68", RALLY, 1, "Event64"),
        grant("Event154", "Obj_Rupee_Blue", "End"),
        evfl.JoinEvent("Event244", index["Event11"]),
        evfl.JoinEvent("Event243", index["Event12"]),
        evfl.JoinEvent("End"),
    ]
    return evfl.Flowchart(
        FLOW,
        [
            evfl.Actor(
                "GameDataActor",
                actions=["EventTriggerSetGameDataInt", "EventTriggerSetGameDataBool"],
                queries=["EventQueryIsGameDataInt", "EventQueryIsGameDataBool"],
            )
        ],
        events,
        [evfl.EntryPoint("Win", 0)],
    )


def first_win(fc):
    data = evfl.write(evfl.EventFlowFile(FLOW, flowchart=fc))
    return evfl.read(gifts.skull_kid_changes()[PATH](data)).flowchart


def replay(fc, state, *, entry="Win", boundary=None):
    """Native bool/int branches, state writes and grants; stop before a new dialogue/game choice."""
    index = boundary if boundary is not None else fc.entry_point(entry).main_event
    state = dict(state)
    rewards = []
    for _ in range(100):
        if index == evfl.NONE:
            return state, rewards
        event = fc.events[index]
        if isinstance(event, evfl.SwitchEvent):
            query = fc.actors[event.actor].queries[event.query]
            if query == "EventQueryIsGameDataBool":
                case = 0 if state.get(event.params["GameDataName"], False) else 1
            elif query == "EventQueryIsGameDataInt":
                value = state[event.params["GameDataName"]]
                expected = event.params["Value"]
                case = 0 if value < expected else 1 if value == expected else 2
            else:
                assert rewards, (event.name, query)
                return state, rewards
            index = dict(event.cases)[case]
            continue
        if isinstance(event, evfl.ForkEvent):
            assert rewards, event.name
            return state, rewards
        if isinstance(event, evfl.ActionEvent):
            actor = fc.actors[event.actor]
            if actor.name == "GameDataActor" and actor.actions[event.action] in (
                "EventTriggerSetGameDataBool",
                "EventTriggerSetGameDataInt",
            ):
                state[event.params["GameDataName"]] = event.params["Value"]
        elif isinstance(event, evfl.SubFlowEvent):
            assert event.flowchart == "Dm_SY_GetInEvent", event
            rewards.append(event.params["ActorName"])
        else:
            assert isinstance(event, evfl.JoinEvent), event
        index = event.next
    raise AssertionError("Reward path did not finish")


@pytest.mark.parametrize("item", ["Item_Boomerang", "Obj_Heart_Piece"])
def test_first_complete_win_gives_prize_once_and_native_repeat_after_reload(item):
    fc = first_win(reward_chart())
    gifts.patch_flowchart(fc, FLOW, [change(item)])
    first, rewards = replay(fc, {GRADE: 5, FLAG: False, RALLY: 3})
    assert rewards == [item]
    assert first == {GRADE: 8, FLAG: True, RALLY: 1}
    # Serialize the graph and retain saved state, as a subsequent session does.
    restored = evfl.read(evfl.write(evfl.EventFlowFile(FLOW, flowchart=fc))).flowchart
    repeat, rewards = replay(restored, first)
    assert rewards == ["Obj_Rupee_Blue"]
    assert repeat == first


@pytest.mark.parametrize("grade", [5, 6, 8])
def test_previously_claimed_source_retains_native_dispatch_for_each_grade(grade):
    native = reward_chart()
    patched = first_win(deepcopy(native))
    gifts.patch_flowchart(patched, FLOW, [change()])
    state = {GRADE: grade, FLAG: True, RALLY: 3}
    assert replay(patched, state) == replay(native, state)


def test_unshuffled_prize_also_uses_first_win_without_changing_other_native_steps():
    native = reward_chart()
    patched = first_win(native)
    changed = {a.name for a, b in zip(native.events, patched.events, strict=False) if a != b}
    assert changed == {"Event178"}
    assert patched.entry_points == native.entry_points
    assert patched.actors == native.actors
    state, rewards = replay(patched, {GRADE: 5, FLAG: False, RALLY: 3})
    assert rewards == ["Obj_Heart_Piece"]
    assert state == {GRADE: 8, FLAG: True, RALLY: 1}


@pytest.mark.dump
def test_real_flow_first_win_native_repeat_and_exact_delta(romfs):
    path = f"Event/EventFlow/{FLOW}.bfevfl.zs"
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    data = dictionaries.decompress(path, (romfs / path).read_bytes())
    native = evfl.read(data).flowchart
    normalized = gifts.skull_kid_changes()[PATH](data)
    patched = evfl.read(gifts.flow_transform(FLOW, [change()])(normalized)).flowchart
    changed = {a.name for a, b in zip(native.events, patched.events, strict=False) if a != b}
    assert changed == {"Event178", "Event24"}
    assert patched.entry_points == native.entry_points
    assert patched.actors == native.actors
    boundary = next(i for i, e in enumerate(patched.events) if e.name == "Event178")
    state, rewards = replay(patched, {GRADE: 5, FLAG: False, RALLY: 3}, boundary=boundary)
    assert rewards == ["Item_Boomerang"]
    assert state == {GRADE: 8, FLAG: True, RALLY: 1}
    assert replay(patched, state, boundary=boundary) == replay(native, state, boundary=boundary)


@pytest.mark.dump
def test_same_item_gift_shuffle_still_moves_prize_to_first_win(romfs):
    from clawshot.census import definitions
    from clawshot.patch.items import load

    path = f"Event/EventFlow/{FLOW}.bfevfl.zs"
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    data = dictionaries.decompress(path, (romfs / path).read_bytes())
    step = gifts.seed_step(
        [gifts.SKULL_KID_CHECK],
        change().steps,
        definitions.load(),
        gifts.load(),
        load(),
        {gifts.SKULL_KID_CHECK: "Piece of Heart"},
        {FLOW: path},
    )
    changes = step({gifts.SKULL_KID_CHECK: "Piece of Heart"})
    data = gifts.skull_kid_changes()[PATH](data)
    patched = evfl.read(changes[path](data) if path in changes else data).flowchart
    boundary = next(i for i, event in enumerate(patched.events) if event.name == "Event178")
    state, rewards = replay(patched, {GRADE: 5, FLAG: False, RALLY: 3}, boundary=boundary)
    assert rewards == ["Obj_Heart_Piece"]
    assert state == {GRADE: 8, FLAG: True, RALLY: 1}


@pytest.mark.dump
def test_default_seed_writes_first_win_for_its_unshuffled_heart_piece(romfs, tmp_path):
    from clawshot.generate import Settings
    from clawshot.patch import make_seed, write_seed

    settings = Settings(areas=("KokiriForest", "LostWood", "InsideTheDekuTree"), goal="'Defeat Queen Gohma'")
    output = make_seed(romfs, 7, settings)
    write_seed(output, romfs, tmp_path / "default")
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    data = dictionaries.decompress(PATH, (tmp_path / "default/romfs" / PATH).read_bytes())
    patched = evfl.read(data).flowchart
    boundary = next(i for i, event in enumerate(patched.events) if event.name == "Event178")
    state, rewards = replay(patched, {GRADE: 5, FLAG: False, RALLY: 3}, boundary=boundary)
    assert rewards == ["Obj_Heart_Piece"]
    assert state == {GRADE: 8, FLAG: True, RALLY: 1}
    assert replay(patched, state, boundary=boundary)[1] == ["Obj_Rupee_Blue"]
