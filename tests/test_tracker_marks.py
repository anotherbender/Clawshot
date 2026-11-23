"""Manual marks storage (``clawshot.tracker.marks``): JSON beside the preferences, per seed and per save slot."""

import hashlib
import json

import pytest
from test_tracker_logic import write_seed

from clawshot.app import preferences
from clawshot.tracker import load_seed, marks, seeds
from clawshot.tracker.seeds import Place

SLOT_A, SLOT_B = "C:/saves/slot_00/progress.sav", "C:/saves/slot_01/progress.sav"


@pytest.fixture
def folder(tmp_path, monkeypatch):
    """The preferences folder, redirected into the test's own folder."""
    prefs = tmp_path / "prefs"
    monkeypatch.setattr(preferences, "user_preferences_path", lambda: prefs / "paths.json")
    return prefs


# 7.1 (4.6)
def test_marks_live_beside_the_preferences(folder):
    assert marks.marks_path() == folder / marks.MARKS_FILE
    store = marks.MarkStore()
    store.set("seed", SLOT_A, "Test Chest", True)
    assert (folder / marks.MARKS_FILE).is_file()
    assert "Cache" not in str(marks.marks_path())


def test_seed_identity_is_the_output_hash_else_the_spoilers(tmp_path, monkeypatch):
    monkeypatch.setattr(seeds, "location_index", lambda: {"Child Chest": Place("Field", None, "Chest")})
    root = write_seed(tmp_path)
    assert marks.seed_identity(load_seed(root)) == "cd" * 32
    (root / "clawshot-seed.json").unlink()
    raw = load_seed(root / "seed")
    assert marks.seed_identity(raw) == hashlib.sha256((root / "seed" / "spoiler.json").read_bytes()).hexdigest()


# 7.2 (4.7)
def test_marks_survive_a_reload_and_are_separate_per_seed_and_slot(folder):
    store = marks.MarkStore()
    store.set("seed-1", SLOT_A, "Shop Item", True)
    store.set("seed-1", SLOT_A, "Other Shop", True)
    again = marks.MarkStore()
    assert again.marks("seed-1", SLOT_A) == {"Shop Item", "Other Shop"}
    assert again.marks("seed-1", SLOT_B) == frozenset()
    assert again.marks("seed-2", SLOT_A) == frozenset()
    again.set("seed-1", SLOT_A, "Shop Item", False)
    assert marks.MarkStore().marks("seed-1", SLOT_A) == {"Other Shop"}


def test_clear_and_drop(folder):
    store = marks.MarkStore()
    for check in ("A", "B", "C"):
        store.set("seed-1", SLOT_A, check, True)
    store.set("seed-1", SLOT_B, "A", True)
    store.drop("seed-1", SLOT_A, ["B", "Z"])
    assert marks.MarkStore().marks("seed-1", SLOT_A) == {"A", "C"}
    assert store.clear("seed-1", SLOT_A) == 2
    assert marks.MarkStore().marks("seed-1", SLOT_A) == frozenset()
    assert marks.MarkStore().marks("seed-1", SLOT_B) == {"A"}


# 7.3 (4.10)
@pytest.mark.parametrize("content", [b"{not json", b"[1, 2]", b"\xff\xfe"])
def test_an_unreadable_file_warns_reads_as_empty_and_is_kept(folder, content):
    folder.mkdir()
    path = folder / marks.MARKS_FILE
    path.write_bytes(content)
    store = marks.MarkStore()
    assert store.marks("seed-1", SLOT_A) == frozenset()
    assert store.warning.startswith(marks.WARNING_PREFIX)
    assert str(folder) not in store.warning  # no local path: it can reach a stream overlay's log or a screenshot
    store.drop("seed-1", SLOT_A, ["A"])  # nothing marked: nothing changes, nothing written
    assert path.read_bytes() == content
    store.set("seed-1", SLOT_A, "A", True)  # the user changed a mark: now it is written
    assert marks.MarkStore().marks("seed-1", SLOT_A) == {"A"}


def test_a_missing_file_reads_as_empty_and_is_not_created_by_reading(folder):
    store = marks.MarkStore()
    assert store.marks("seed-1", SLOT_A) == frozenset()
    assert store.warning == ""
    assert not folder.exists()


# 7.4 (P7.a)
def test_writes_are_atomic_and_deterministic(folder, monkeypatch):
    store = marks.MarkStore()
    store.set("seed-b", SLOT_B, "Zeta", True)
    store.set("seed-a", SLOT_A, "Beta", True)
    store.set("seed-a", SLOT_A, "Alpha", True)
    text = (folder / marks.MARKS_FILE).read_text(encoding="utf-8")
    data = json.loads(text)
    assert list(data["marks"]) == ["seed-a", "seed-b"]
    assert data["marks"]["seed-a"][SLOT_A] == ["Alpha", "Beta"]
    other = marks.MarkStore(folder / "copy.json")
    for seed_id, slot, check in (("seed-a", SLOT_A, "Alpha"), ("seed-b", SLOT_B, "Zeta"), ("seed-a", SLOT_A, "Beta")):
        other.set(seed_id, slot, check, True)
    assert (folder / "copy.json").read_text(encoding="utf-8") == text
    assert sorted(p.name for p in folder.iterdir()) == ["copy.json", marks.MARKS_FILE]  # no temporary file left

    def fail(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(marks.os, "replace", fail)
    with pytest.raises(OSError):
        store.set("seed-a", SLOT_A, "Gamma", True)
    assert (folder / marks.MARKS_FILE).read_text(encoding="utf-8") == text  # the old file is untouched
    assert sorted(p.name for p in folder.iterdir()) == ["copy.json", marks.MARKS_FILE]


# Round 21: skips, a second table beside the marks.
def test_skips_are_a_separate_table_that_drop_never_touches_and_clear_empties(folder):
    store = marks.MarkStore()
    store.set("seed-1", SLOT_A, "Shop Item", True)
    store.set("seed-1", SLOT_A, "Windmill Rupee", True, table=marks.SKIPS)
    again = marks.MarkStore()
    assert again.marks("seed-1", SLOT_A) == {"Shop Item"}
    assert again.marks("seed-1", SLOT_A, table=marks.SKIPS) == {"Windmill Rupee"}
    again.drop("seed-1", SLOT_A, ["Windmill Rupee", "Shop Item"])  # a save read drops marks only
    assert marks.MarkStore().marks("seed-1", SLOT_A, table=marks.SKIPS) == {"Windmill Rupee"}
    assert marks.MarkStore().marks("seed-1", SLOT_A) == frozenset()
    assert again.clear("seed-1", SLOT_A) == 1
    assert json.loads((folder / marks.MARKS_FILE).read_text(encoding="utf-8")) == {"version": 1, "marks": {}}


def test_a_file_without_skips_keeps_its_bytes_and_an_old_file_reads(folder):
    folder.mkdir()
    old = (
        '{\n  "marks": {\n    "seed-1": {\n      "C:/saves": [\n        "A"\n      ]\n    }\n  },\n  "version": 1\n}\n'
    )
    (folder / marks.MARKS_FILE).write_text(old, encoding="utf-8")
    store = marks.MarkStore()
    assert store.marks("seed-1", "C:/saves") == {"A"} and store.marks("seed-1", "C:/saves", table=marks.SKIPS) == set()
    store.set("seed-1", "C:/saves", "B", True, table=marks.SKIPS)
    store.set("seed-1", "C:/saves", "B", False, table=marks.SKIPS)
    assert (folder / marks.MARKS_FILE).read_text(encoding="utf-8") == old
