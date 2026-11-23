"""Spec tracker-auto-checks 1.3 (D1): ``track`` in gift_rules.toml is tracker-only, so the same seed, settings and
version give a byte-identical output folder with and without it (AGENTS rule 4)."""

import dataclasses
from pathlib import Path

import pytest

from clawshot.__main__ import main
from clawshot.census.definitions import Definition
from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.formats.evfl import ActionEvent, Actor, EntryPoint, EventFlowFile, Flowchart, SubFlowEvent
from clawshot.patch import gifts
from clawshot.patch import items as item_actors

FLOWS = ("Npc_Swap", "Npc_Skip")
TRACK = '\ntrack = [{ bool = "Npc_Done", source = "Npc/Event2; audit", accepted = false }]'
RULES = """
[check."Swap Check"]
class = "swap"
{track}

[check."Skip Check"]
class = "rewrite"
skip = ["Npc_Skip/Event2"]
{track}
"""


def flow(name: str) -> bytes:
    game_data = Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"], queries=["EventQueryIsGameDataBool"])
    pouch = Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"])
    events = [
        SubFlowEvent("Event0", "Wrap", "Give", next=1, params={"ActorName": "Item_Old"}),
        ActionEvent("Event1", 0, 0, next=2, params={"GameDataName": "Npc_Done", "Index": -1, "Value": True}),
        ActionEvent("Event2", 1, 0, next=3, params={"Actor": "Item_Old", "Num": 1}),
        ActionEvent("Event3", 0, 0, params={"GameDataName": "Npc_After", "Index": -1, "Value": True}),
    ]
    return evfl.write(
        EventFlowFile(name, flowchart=Flowchart(name, [game_data, pouch], events, [EntryPoint("Talk", 0)]))
    )


def output_folder(root: Path, text: str) -> dict[str, bytes]:
    """Write the gift step's files for one fixed placement into ``root``; return relative path -> bytes."""
    rules = gifts.loads(text)
    steps = [
        Gift(f"{name}/Event0", "npc_gift", name, "f", ("Talk",), "Event0", "Wrap:Give", "ActorName", "Item_Old", "")
        for name in FLOWS
    ]
    checks = {"Npc_Swap": "Swap Check", "Npc_Skip": "Skip Check"}
    defs = [Definition(s.id, "npc_gift", "", "n", s.vanilla_item, checks[s.flow]) for s in steps]
    actors = item_actors.loads('[items]\nOld = { actor = "Item_Old" }\nNew = { actor = "Item_New" }\n')
    shuffled = sorted(checks.values())
    step = gifts.seed_step(
        shuffled, steps, defs, rules, actors, dict.fromkeys(shuffled, "Old"), {f: f"Event/{f}.bfevfl" for f in FLOWS}
    )
    for path, transform in sorted(step(dict.fromkeys(shuffled, "New")).items()):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(transform(flow(Path(path).stem)))
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def test_track_entries_leave_the_synthetic_output_folder_byte_identical(tmp_path):
    with_track = gifts.loads(RULES.format(track=TRACK))
    assert all(rule.track for rule in with_track.values())
    before = output_folder(tmp_path / "without", RULES.format(track=""))
    after = output_folder(tmp_path / "with", RULES.format(track=TRACK))
    assert sorted(before) == ["Event/Npc_Skip.bfevfl", "Event/Npc_Swap.bfevfl"]
    assert before == after


def _folder(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


@pytest.mark.dump
def test_dump_the_real_rules_give_the_same_seed_folder_without_track(romfs, tmp_path, monkeypatch):
    real = gifts.load()
    assert any(rule.track for rule in real.values()), "gift_rules.toml carries no track entry yet"
    args = ["--romfs", str(romfs), "--seed", "12345", "--shuffle", "Chest", "Gift", "Scrub", "Token"]
    assert main([*args, "--out", str(tmp_path / "with")]) == 0
    stripped = {name: dataclasses.replace(rule, track=()) for name, rule in real.items()}
    monkeypatch.setattr(gifts, "load", lambda path=gifts.RULES_TOML: stripped)
    assert main([*args, "--out", str(tmp_path / "without")]) == 0
    with_track, without = _folder(tmp_path / "with"), _folder(tmp_path / "without")
    assert sorted(with_track) == sorted(without)
    assert [path for path in with_track if with_track[path] != without[path]] == []
