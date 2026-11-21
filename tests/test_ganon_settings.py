"""Trial-state/logic agreement and native token-counter bridge boundaries; synthetic fixtures only."""

from collections import Counter
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest
from test_reward_bridge import synthetic_game_data

from clawshot.__main__ import main
from clawshot.app.schema import validate
from clawshot.formats import byml, msbt, sarc, zsdic
from clawshot.generate import Settings, generate, play_note, prepare, spoiler
from clawshot.generate.trials import TRIALS, remaining
from clawshot.patch import gamedata, reward_bridge, trials
from clawshot.save import key
from clawshot.tracker import logic as tracker_logic
from clawshot.tracker.seeds import Seed, installed_version

TOWER_RULE = " and ".join(f"(skipped_trials[{name}] or '{name} Trial Clear')" for name in TRIALS)
SPEC = {
    "start": "Root",
    "goal": "True",
    "items": {"Rupees (5)": {}},
    "flags": {"skipped_trials": {name: False for name in TRIALS}},
    "regions": [
        {
            "name": "Root",
            "exits": {"Tower": TOWER_RULE},
            "events": {name + " Trial Clear": "False" for name in TRIALS},
            "locations": {"Early Chest": {"rule": "True", "type": "Chest", "vanilla": "Rupees (5)"}},
        },
        {"name": "Tower"},
    ],
}


def trial_tree():
    def row(name, default):
        return {
            "Hash": byml.U32(key(name)),
            "DefaultValue": default,
            "ResetTypeValue": byml.I32(8),
            "SaveFileIndex": byml.I32(0),
        }

    return {
        "Data": {
            "Bool": [row(trials.REMOVAL + name, False) for name in TRIALS] + [row(trials.ALL_CLEAR, False)],
            "Int": [row(trials.COUNT, byml.I32(6))],
            "Enum": [],
        },
        "MetaData": {"Unrelated": byml.I32(17)},
    }


@pytest.mark.parametrize("count", range(7))
def test_skipped_native_cores_match_tower_logic_and_saved_count(count):
    for number in (0, 20202004, 20202024):
        tree = trial_tree()
        before = deepcopy(tree)
        changes = gamedata.plan_game_data(tree, trials.initial_values(number, count))
        gamedata.apply_game_data(tree, changes)
        _, world = prepare(SPEC, Settings(trials_count=count), seed=number)
        active = remaining(number, count)
        state = {
            name: next(row["DefaultValue"] for row in tree["Data"]["Bool"] if row["Hash"] == key(trials.REMOVAL + name))
            for name in TRIALS
        }
        assert world.settings["skipped_trials"] == state
        assert sum(not done for done in state.values()) == count
        assert tree["Data"]["Int"][0]["DefaultValue"] == count
        clear = next(row["DefaultValue"] for row in tree["Data"]["Bool"] if row["Hash"] == key(trials.ALL_CLEAR))
        assert clear is (count == 0)
        gate = world.regions["Root"].exits[0].rule
        completed = Counter({name + " Trial Clear": 1 for name in active})
        assert gate(completed, "adult", 1)
        for name in active:
            without = completed.copy()
            del without[name + " Trial Clear"]
            assert not gate(without, "adult", 1), (number, count, name)
        for change in changes:
            kind = "Int" if change.name == trials.COUNT else "Bool"
            row = next(row for row in tree["Data"][kind] if row["Hash"] == key(change.name))
            old = next(row for row in before["Data"][kind] if row["Hash"] == key(change.name))
            row["DefaultValue"] = old["DefaultValue"]
        assert byml.same(tree, before)


def test_partial_seed_tracker_rebuild_matches_generator_and_discloses_names(monkeypatch):
    settings = Settings(trials_count=3)
    out = generate(SPEC, 20202004, settings)
    log = spoiler(out)
    active = log["ganon_trials"]["remaining"]
    assert active == list(remaining(out.seed, 3))
    assert all(name in play_note(out, log) for name in active)
    tracker_seed = Seed(
        Path("."),
        Path("."),
        Path("spoiler.json"),
        None,
        "raw",
        {"generator": f"clawshot {installed_version()}", "seed": out.seed, "settings_string": out.settings.to_string()},
        (),
    )
    monkeypatch.setattr(tracker_logic, "world_spec", lambda: SPEC)
    rebuilt = tracker_logic.load_world(tracker_seed)
    assert rebuilt.available, rebuilt.reason
    assert rebuilt.world.settings == out.world.settings
    actual_gate = rebuilt.world.regions["Root"].exits[0].rule
    generated_gate = out.world.regions["Root"].exits[0].rule
    for flags in (Counter(), Counter({name + " Trial Clear": 1 for name in active})):
        assert actual_gate(flags, "adult", 1) == generated_gate(flags, "adult", 1)


@pytest.mark.parametrize("value", [-1, 7, True, 1.5])
def test_invalid_trial_count_is_refused(value):
    with pytest.raises(ValueError, match="trials_count"):
        Settings(trials_count=value)


def token_tree():
    tree = synthetic_game_data()
    tree["Data"]["Int"].append(
        {
            "Hash": byml.U32(key(reward_bridge.TOKEN_STOCK)),
            "DefaultValue": byml.I32(0),
            "ResetTypeValue": byml.I32(32),
            "SaveFileIndex": byml.I32(0),
        }
    )
    tree["Data"]["Struct"] = [
        {
            "Hash": byml.U32(key(parent)),
            "DefaultValue": [{"Hash": byml.U32(key(member)), "Value": byml.U32(key(parent + "." + member))}],
            "ResetTypeValue": byml.I32(0),
            "SaveFileIndex": byml.I32(-1),
        }
        for parent, member in (("PouchData", "Item_Token_Gold"), ("PouchData.Item_Token_Gold", "StockNum"))
    ]
    return tree


def int_expression(commands, stock):
    """Independent native Int predicate evaluator: less-than Int, signed literal, NOT."""
    values = iter(commands)
    stack = []
    for op, *args in values:
        if op == 18:
            literal_op, literal = next(values)
            assert literal_op == 16 and type(literal) is byml.I32
            assert args == [key("PouchData.Item_Token_Gold.StockNum")]
            stack.append(stock < literal)
        elif op == 5:
            stack.append(not stack.pop())
        else:
            pytest.fail(f"unexpected native opcode {op}")
    assert len(stack) == 1
    return stack[0]


def test_native_stock_threshold_over_every_count_and_stock_preserves_saved_layout():
    for count in range(101):
        tree = token_tree()
        before = deepcopy(tree)
        reward_bridge.add_eligibility(tree, "tokens", count)
        added = tree["Data"]["BoolExp"].pop()
        assert added["SaveFileIndex"] == -1 and added["ResetTypeValue"] == 0
        assert byml.same(tree, before)
        for stock in range(101):
            assert int_expression(added["Values"], stock) is (stock >= count), (count, stock)


def test_token_bridge_logic_counts_items_not_source_completion():
    from clawshot.world import load_spec

    _, world = prepare(load_spec(), Settings(bridge="tokens", bridge_count=3, shuffle=("Chest", "Token")))
    gate = next(
        edge.rule for edge in world.regions["Ganons Castle Grounds"].exits if edge.target == "Ganons Castle Ledge"
    )
    assert not gate(Counter({"Gold Skulltula Token": 2, "Defeat Queen Gohma": 1}), "adult", 1)
    assert gate(Counter({"Gold Skulltula Token": 3}), "adult", 1)
    # A chest's token is the same item even when no Skulltula is collected.
    search_spec = {
        "start": "Root",
        "goal": "True",
        "items": {"Gold Skulltula Token": {}},
        "regions": [
            {
                "name": "Root",
                "locations": {
                    str(i): {"rule": "True", "vanilla": "Gold Skulltula Token", "type": "Chest"} for i in range(3)
                },
            }
        ],
    }
    from clawshot.world import Search, build_world

    search = Search(build_world(search_spec))
    search.collect_spheres({str(i): "Gold Skulltula Token" for i in range(3)})
    assert gate(search.counts, "adult", 1)


def test_new_settings_replay_through_cli_and_form(capsys):
    args = ["--bridge", "tokens", "--bridge-count", "3", "--trials-count", "2", "--print-settings"]
    assert main(args) == 0
    selected = Settings.from_string(capsys.readouterr().out.strip())
    assert selected.bridge == "tokens" and selected.bridge_count == 3 and selected.trials_count == 2
    assert validate({"bridge": "tokens", "bridge_count": 3, "trials_count": 2}) == selected
    for bad in (-1, 101, True, 0.5):
        with pytest.raises(ValueError, match="bridge_count"):
            replace(selected, bridge_count=bad)


@pytest.mark.dump
@pytest.mark.parametrize("count", [0, 1, 3, 5, 6])
def test_native_trial_defaults_and_barrier_message_change_only_selected_state(romfs, count):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = gamedata.GAME_DATA_LIST
    raw = dictionaries.decompress(path, (romfs / path).read_bytes())
    before = byml.read(raw)
    chosen = trials.initial_values(20202004, count)
    result = byml.read(gamedata.patch_initial_values(raw, chosen))
    changes = gamedata.plan_game_data(before, chosen)
    for change in changes:
        kind = "Int" if change.name == trials.COUNT else "Bool"
        row = next(row for row in result["Data"][kind] if row["Hash"] == key(change.name))
        assert row["DefaultValue"] == change.new
        old = next(row for row in before["Data"][kind] if row["Hash"] == key(change.name))
        row["DefaultValue"] = old["DefaultValue"]
    assert byml.same(result, before)
    for path, transform in trials.changes(romfs, seed=20202004, count=count).items():
        original = dictionaries.decompress(path, (romfs / path).read_bytes())
        files = sarc.read(original)
        after = sarc.read(transform(original))
        old = msbt.read(files[trials.MESSAGE_FILE])
        new = msbt.read(after[trials.MESSAGE_FILE])
        visible = msbt.plain(new.messages[trials.MESSAGE])
        active = remaining(20202004, count)
        assert all(name in visible for name in active)
        assert all(name not in visible for name in TRIALS if name not in active)
        new.messages[trials.MESSAGE] = old.messages[trials.MESSAGE]
        assert new == old
        after[trials.MESSAGE_FILE] = files[trials.MESSAGE_FILE]
        assert after == files


@pytest.mark.dump
def test_native_counter_path_and_comparator_oracle(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = gamedata.GAME_DATA_LIST
    raw = dictionaries.decompress(path, (romfs / path).read_bytes())
    tree = byml.read(raw)
    anchor = next(row for row in tree["Data"]["BoolExp"] if row["Hash"] == key("MiniGame_DampeRace_IsClearLeastOnce"))
    assert byml.same(
        anchor["Values"],
        [[byml.U64(18), byml.U64(key("MiniGame_DampeRace_ClearCount"))], [byml.U64(16), byml.I32(1)], [byml.U64(5)]],
    )
    before = deepcopy(tree)
    reward_bridge.add_eligibility(tree, "tokens", 3)
    added = tree["Data"]["BoolExp"].pop()
    assert int_expression(added["Values"], 2) is False
    assert int_expression(added["Values"], 3) is True
    assert byml.same(tree, before)
