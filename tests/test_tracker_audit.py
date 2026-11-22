"""Spec tracker-auto-checks section 6: ``python -m clawshot.tracker.audit`` compares a save's track flags with the
player's marks, read-only, on synthetic seeds, saves and marks."""

import os

import pytest
from test_tracker_state import build_save
from test_tracker_track import DOG, PLACEMENTS, SARIA, SKULL_KID, make_seed
from test_tracker_track import places as places

from clawshot import save
from clawshot.save import murmur3_32
from clawshot.tracker import audit, load_seed
from clawshot.tracker import marks as tracker_marks

ACCOUNT = "0123456789abcdef0123456789abcdef"


def write_slot(root, number, bools, steps=None, tick=10):
    enums = {save.key(name): murmur3_32(step.encode()) for name, step in (steps or {}).items()}
    folder = root / "user" / "save" / ACCOUNT / f"slot_{number:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "progress.sav"
    path.write_bytes(build_save(bools, extra={save.ENUM: enums} if enums else None))
    os.utime(path, ns=(tick * 10**9, tick * 10**9))
    return path


def mark(root, marks_file, *names):
    store = tracker_marks.MarkStore(marks_file)
    seed_id = tracker_marks.seed_identity(load_seed(root))
    for name in names:
        store.set(seed_id, str(root / "user" / "save" / ACCOUNT), name, True)


def run(capsys, *args):
    code = audit.main([str(a) for a in args])
    return code, capsys.readouterr().out.splitlines()


def line(out, name):
    return next(row for row in out if row.startswith(name + ":"))


def test_one_line_per_track_gift_with_flags_result_mark_and_verdict(tmp_path, places, capsys):
    root = make_seed(tmp_path)
    write_slot(root, 0, {SKULL_KID: True, SARIA: False})
    marks_file = tmp_path / "marks.json"
    mark(root, marks_file, "LW Skull Kid")
    code, out = run(capsys, root, "--marks", marks_file)
    assert code == 0, out
    assert line(out, "LW Skull Kid") == f"LW Skull Kid: {SKULL_KID}=true -> collected; marked: yes; agree"
    assert line(out, "Song from Saria") == f"Song from Saria: {SARIA}=false -> not collected; marked: no; agree"
    assert line(out, "Market Lost Dog") == f"Market Lost Dog: {DOG}==Complete=absent -> unknown; marked: no; unknown"
    assert not [row for row in out if row.startswith(("Song from Windmill", "Test Chest", "Test Shop Item"))]
    assert out[-1] == "0 disagreements"


def test_a_marked_gift_read_not_collected_disagrees_and_exits_1(tmp_path, places, capsys):
    root = make_seed(tmp_path)
    write_slot(root, 0, {SKULL_KID: True, SARIA: False}, {DOG: "Step01"})
    marks_file = tmp_path / "marks.json"
    mark(root, marks_file, "Song from Saria")
    code, out = run(capsys, root, "--marks", marks_file)
    assert code == 1
    assert line(out, "Song from Saria").endswith("-> not collected; marked: yes; disagree")
    assert line(out, "LW Skull Kid").endswith("-> collected; marked: no; no-mark")  # maybe a mark never made
    assert line(out, "Market Lost Dog") == f"Market Lost Dog: {DOG}==Complete=false -> not collected; marked: no; agree"
    assert out[-1] == "1 disagreement"


def test_it_writes_nothing(tmp_path, places, capsys):
    root = make_seed(tmp_path)
    write_slot(root, 0, {SKULL_KID: True})
    marks_file = tmp_path / "marks.json"
    mark(root, marks_file, "LW Skull Kid", "Song from Saria")

    def files():
        return {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in sorted(tmp_path.rglob("*")) if p.is_file()}, sorted(
            tmp_path.rglob("*")
        )

    before = files()
    for args in ((root, "--marks", marks_file), (root, "--marks", marks_file, "--spoilers", "--slot", "0")):
        run(capsys, *args)
    assert files() == before


def test_rewards_only_with_spoilers(tmp_path, places, capsys):
    root = make_seed(tmp_path)
    write_slot(root, 0, {SKULL_KID: True})
    marks_file = tmp_path / "none.json"
    _, plain = run(capsys, root, "--marks", marks_file)
    assert not any(PLACEMENTS[name] in row for row in plain for name in PLACEMENTS)
    _, shown = run(capsys, root, "--marks", marks_file, "--spoilers")
    assert line(shown, "LW Skull Kid").endswith(f"; reward: {PLACEMENTS['LW Skull Kid']}")


def test_a_seed_from_another_version_gets_the_note_and_is_still_audited(tmp_path, places, capsys):
    root = make_seed(tmp_path, generator="clawshot 0.0.1")
    write_slot(root, 0, {SKULL_KID: True})
    code, out = run(capsys, root, "--marks", tmp_path / "none.json")
    assert code == 0
    assert any("need a seed made by" in row for row in out)
    assert line(out, "LW Skull Kid").startswith(f"LW Skull Kid: {SKULL_KID}=true -> collected")


def test_slot_choice(tmp_path, places, capsys):
    root = make_seed(tmp_path)
    write_slot(root, 0, {SKULL_KID: True}, tick=10)
    write_slot(root, 1, {SKULL_KID: False}, tick=20)  # newest
    marks_file = tmp_path / "none.json"
    assert "=false" in line(run(capsys, root, "--marks", marks_file)[1], "LW Skull Kid")
    assert "=true" in line(run(capsys, root, "--marks", marks_file, "--slot", "0")[1], "LW Skull Kid")


@pytest.mark.parametrize("problem", ["no seed", "no save", "bad marks", "no such slot"])
def test_unreadable_inputs_exit_2_with_one_line(tmp_path, places, capsys, problem):
    root = make_seed(tmp_path)
    marks_file = tmp_path / "marks.json"
    args = [root, "--marks", marks_file]
    if problem != "no save":
        write_slot(root, 0, {SKULL_KID: True})
    if problem == "no seed":
        args[0] = tmp_path / "missing"
    if problem == "bad marks":
        marks_file.write_text("{not json", encoding="utf-8")
    if problem == "no such slot":
        args += ["--slot", "7"]
    code = audit.main([str(a) for a in args])
    captured = capsys.readouterr()
    assert code == 2
    assert len(captured.err.strip().splitlines()) == 1 and captured.err.startswith("error: ")
