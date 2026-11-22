"""Spec tracker-auto-checks sections 2-4: gifts read from the native once-flags in ``gift_rules.toml`` ``track``."""

import json
from pathlib import Path

import pytest
from test_tracker_state import build_save

from clawshot import save
from clawshot.patch import gifts
from clawshot.save import murmur3_32
from clawshot.tracker import build_state, load_seed, seeds
from clawshot.tracker.seeds import Place, installed_version

PLACES = {
    "LW Skull Kid": Place("Lost Woods", None, "NPC"),  # real rules: bool Npc_SkullKid_Child_IsGetHeartPiece
    "Song from Saria": Place("Sacred Forest Meadow", None, "Song"),  # played Dm_MelodyGet_Saria
    "Market Lost Dog": Place("Market", None, "NPC"),  # quest SubEvent_FindRichard == Complete
    "Song from Windmill": Place("Kakariko Village", None, "Song"),  # flag HavePlayedEvent.Dm_MelodyGet_Storm
    "Test Chest": Place("Test", None, "Chest"),
    "Test Shop Item": Place("Market", None, "Shop"),
}
PLACEMENTS = {
    "LW Skull Kid": "Piece of Heart",
    "Song from Saria": "Hookshot",
    "Market Lost Dog": "Bow",
    "Song from Windmill": "Bolero of Fire",
    "Test Chest": "Rupees (50)",
    "Test Shop Item": "Buy Arrows (10)",
}
LOCATIONS = {"Test Chest": {"name": "Test Chest", "where": "Test", "ids": ["123"]}}
PATCH = {"changes": [{"location": "Test Chest", "id": "123", "chest": "Obj_TBox_A_01"}], "unchanged": []}
SKULL_KID = "Npc_SkullKid_Child_IsGetHeartPiece"
SARIA = "HavePlayedEvent.Dm_MelodyGet_Saria"
DOG = "Step_SubEvent_FindRichard"
THIS_VERSION = f"clawshot {installed_version()}"


@pytest.fixture
def places(monkeypatch):
    monkeypatch.setattr(seeds, "location_index", lambda: PLACES)
    return PLACES


def make_seed(tmp_path, *, generator=THIS_VERSION, placements=PLACEMENTS, name="seed"):
    root = tmp_path / name
    (root / "seed").mkdir(parents=True)
    spoiler = {
        "generator": generator,
        "seed": 1,
        "settings_string": "CS1-test",
        "placements": placements,
        "locations": LOCATIONS,
        "patch": PATCH,
    }
    (root / "seed" / "spoiler.json").write_text(json.dumps(spoiler), encoding="utf-8")
    (root / "clawshot-seed.json").write_text(json.dumps({"seed": 1, "output_sha256": "ab" * 32}), encoding="utf-8")
    return root


def game_save(bools=None, steps=None) -> save.Save:
    """A synthetic save with named Bools and quest-step enums (``Step_<quest>`` -> murmur3 of the step name)."""
    enums = {save.key(name): murmur3_32(step.encode()) for name, step in (steps or {}).items()}
    return save.read(build_save(bools, extra={save.ENUM: enums} if enums else None))


def checks(state):
    return {check["id"]: check for area in state["areas"] for check in area["checks"]}


def test_track_gifts_read_by_track_and_every_other_read_unchanged(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    by_name = {check.location: check for check in seed.checks}
    for name in ("LW Skull Kid", "Song from Saria", "Market Lost Dog"):
        assert (by_name[name].kind, by_name[name].method, by_name[name].provisional) == ("gift", seeds.TRACK, True)
        assert by_name[name].track == gifts.load()[name].track
    assert (by_name["Song from Windmill"].method, by_name["Song from Windmill"].track) == (seeds.NAMED_BOOL, ())
    assert by_name["Test Chest"].method == seeds.NAMED_BOOL and by_name["Test Shop Item"].method == seeds.NO_RECORD
    assert not by_name["Song from Windmill"].provisional
    assert not [w for w in seed.warnings if "need a seed made by" in w]


def test_each_kind_reads_its_own_save_field(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    given = checks(build_state(seed, game_save({SKULL_KID: True, SARIA: True}, {DOG: "Complete"})))
    assert [given[n]["collected"] for n in ("LW Skull Kid", "Song from Saria", "Market Lost Dog")] == [True] * 3
    assert {given[n]["basis"] for n in ("LW Skull Kid", "Song from Saria", "Market Lost Dog")} == {seeds.TRACK}
    open_ = checks(build_state(seed, game_save({SKULL_KID: False, SARIA: False}, {DOG: "Step01"})))
    assert [open_[n]["collected"] for n in ("LW Skull Kid", "Song from Saria", "Market Lost Dog")] == [False] * 3


def test_a_missing_field_is_unknown_naming_the_field(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    found = checks(build_state(seed, game_save({SARIA: False})))
    assert found["LW Skull Kid"]["collected"] is None and SKULL_KID in found["LW Skull Kid"]["reason"]
    assert found["Market Lost Dog"]["collected"] is None and DOG in found["Market Lost Dog"]["reason"]
    assert found["Song from Saria"]["collected"] is False
    assert checks(build_state(seed, None))["LW Skull Kid"]["collected"] is None


TWO = gifts.loads(
    """
[check."LW Skull Kid"]
class = "swap"
track = [
  { bool = "Flag_A", source = "s", accepted = false },
  { quest = "Quest_B", step = "Complete", source = "s", accepted = true, played_by = "p" },
]
"""
)


@pytest.mark.parametrize(
    ("bools", "steps", "expected", "named"),
    [
        ({"Flag_A": True}, {}, True, None),  # any True: collected, though the quest field is missing
        ({}, {"Step_Quest_B": "Complete"}, True, None),
        ({"Flag_A": False}, {"Step_Quest_B": "Step01"}, False, None),  # all present and False
        ({"Flag_A": False}, {}, None, "Step_Quest_B"),  # one missing, none True: unknown naming it
        ({}, {}, None, "Flag_A"),
    ],
)
def test_entries_combine_any_of(tmp_path, places, monkeypatch, bools, steps, expected, named):
    monkeypatch.setattr(seeds, "_gift_rules", lambda: TWO)
    seed = load_seed(make_seed(tmp_path, placements={"LW Skull Kid": "Piece of Heart"}))
    [check] = seed.checks
    assert check.method == seeds.TRACK and check.provisional  # one provisional entry makes the check provisional
    entry = checks(build_state(seed, game_save(bools, steps)))["LW Skull Kid"]
    assert entry["collected"] is expected
    if named:
        assert named in entry["reason"]


def test_an_all_accepted_check_is_not_provisional(tmp_path, places, monkeypatch):
    accepted = gifts.loads(
        '[check."LW Skull Kid"]\nclass = "swap"\n'
        'track = [{ bool = "Flag_A", source = "s", accepted = true, played_by = "p" }]\n'
    )
    monkeypatch.setattr(seeds, "_gift_rules", lambda: accepted)
    [check] = load_seed(make_seed(tmp_path, placements={"LW Skull Kid": "Piece of Heart"})).checks
    assert (check.method, check.provisional) == (seeds.TRACK, False)


def test_a_seed_from_another_version_keeps_todays_reads_with_one_warning(tmp_path, places):
    seed = load_seed(make_seed(tmp_path, generator="clawshot 0.0.1"))
    by_name = {check.location: check for check in seed.checks}
    assert (by_name["LW Skull Kid"].method, by_name["LW Skull Kid"].track) == (seeds.NO_RECORD, ())
    assert by_name["Song from Windmill"].method == seeds.NAMED_BOOL
    notes = [w for w in seed.warnings if "need a seed made by" in w]
    assert len(notes) == 1 and THIS_VERSION in notes[0]
    found = checks(build_state(seed, game_save({SKULL_KID: True})))
    assert found["LW Skull Kid"]["collected"] is None  # today's read: no record
    assert build_state(seed, None)["warnings"].count(notes[0]) == 1
    # No track gift in the seed: no such note, only the usual version warning.
    plain = load_seed(make_seed(tmp_path, generator="clawshot 0.0.1", placements={"Test Chest": "Bow"}, name="x"))
    assert not [w for w in plain.warnings if "need a seed made by" in w]
    assert [w for w in plain.warnings if "made by clawshot 0.0.1" in w]


def test_collected_gifts_add_nothing_to_what_is_held(tmp_path, places):
    seed = load_seed(make_seed(tmp_path))
    given = build_state(seed, game_save({SKULL_KID: True, SARIA: True}, {DOG: "Complete"}))
    not_given = build_state(seed, game_save({SKULL_KID: False, SARIA: False}, {DOG: "Step01"}))
    for group in ("items", "songs", "rewards", "hearts", "tokens"):
        assert given[group] == not_given[group], group


# --- marks (spec 3.x, plan task 7) -------------------------------------------------------------------------------

ACCOUNT = "0123456789abcdef0123456789abcdef"
MIXED = gifts.loads(
    """
[check."LW Skull Kid"]
class = "swap"
track = [{ bool = "Flag_P", source = "s", accepted = false }]

[check."Song from Saria"]
class = "swap"
track = [{ bool = "Flag_A", source = "s", accepted = true, played_by = "p" }]
"""
)


class MemoryMarks:
    """An in-memory stand-in for ``tracker.marks.MarkStore``."""

    warning = ""

    def __init__(self):
        self.data: dict[tuple[str, str], set[str]] = {}

    def marks(self, seed_id, slot):
        return frozenset(self.data.get((seed_id, slot), ()))

    def set(self, seed_id, slot, check, marked):
        (self.data.setdefault((seed_id, slot), set()).add if marked else self.data.get((seed_id, slot), set()).discard)(
            check
        )

    def drop(self, seed_id, slot, checks):
        self.data.get((seed_id, slot), set()).difference_update(checks)

    def clear(self, seed_id, slot):
        return len(self.data.pop((seed_id, slot), ()))


@pytest.fixture
def mixed(tmp_path, places, monkeypatch):
    """A seed whose LW Skull Kid reads a provisional flag and Song from Saria an accepted one; a session on it."""
    from clawshot.tracker import TrackerSession

    monkeypatch.setattr(seeds, "_gift_rules", lambda: MIXED)
    root = make_seed(tmp_path)
    store = MemoryMarks()
    session = TrackerSession(marks=store)

    def write(bools, tick):
        slot = root / "user" / "save" / ACCOUNT / "slot_00"
        slot.mkdir(parents=True, exist_ok=True)
        path = slot / "progress.sav"
        path.write_bytes(build_save(bools))
        import os

        os.utime(path, ns=(tick * 1_000_000_000, tick * 1_000_000_000))

    return root, session, store, write


def entry(snapshot, name):
    return checks(snapshot["state"])[name]


def test_a_provisional_false_check_stays_open_markable_and_keeps_its_mark_over_polls(mixed):
    root, session, store, write = mixed
    write({"Flag_P": False, "Flag_A": False}, 10)
    session.configure(root)
    open_ = entry(session.snapshot(), "LW Skull Kid")
    assert (open_["collected"], open_.get("markable"), "marked" in open_) == (False, True, False)
    marked = session.mark("LW Skull Kid", True)
    kid = entry(marked, "LW Skull Kid")
    assert (kid["collected"], kid["marked"], kid["markable"]) == (False, True, True)
    assert "item" not in kid  # spoiler-free: a mark never shows the reward (4.1)
    area = next(a for a in marked["state"]["areas"] if a["name"] == "Lost Woods")
    assert area["marked"] == 1
    for tick in (11, 12, 13):  # several polls of a re-saved, still-false save: the mark survives
        write({"Flag_P": False, "Flag_A": False}, tick)
        assert entry(session.snapshot(), "LW Skull Kid")["marked"] is True
    assert "LW Skull Kid" in next(iter(store.data.values()))
    unmarked = session.mark("LW Skull Kid", False)
    assert "marked" not in entry(unmarked, "LW Skull Kid")


def test_an_accepted_false_check_refuses_marks_and_drops_an_old_one(mixed):
    root, session, store, write = mixed
    write({"Flag_P": False, "Flag_A": False}, 10)
    session.configure(root)
    saria = entry(session.snapshot(), "Song from Saria")
    assert saria["collected"] is False and "markable" not in saria
    with pytest.raises(ValueError, match="already says"):
        session.mark("Song from Saria", True)
    seed_id, folder = session._seed_id, session._marks_folder
    store.set(seed_id, folder, "Song from Saria", True)  # a mark from before the read, as for chests
    write({"Flag_P": False, "Flag_A": False}, 11)
    assert "marked" not in entry(session.snapshot(), "Song from Saria")
    assert "Song from Saria" not in store.marks(seed_id, folder)


def test_a_true_track_flag_collects_and_drops_the_mark(mixed):
    root, session, store, write = mixed
    write({"Flag_P": False, "Flag_A": False}, 10)
    session.configure(root)
    session.mark("LW Skull Kid", True)
    seed_id, folder = session._seed_id, session._marks_folder
    write({"Flag_P": True, "Flag_A": True}, 11)
    now = session.snapshot()
    for name in ("LW Skull Kid", "Song from Saria"):
        got = entry(now, name)
        assert got["collected"] is True and "marked" not in got and "markable" not in got
        assert got["item"] == PLACEMENTS[name]  # collected gifts show their reward, as opened chests do (4.1)
    assert store.marks(seed_id, folder) == frozenset()


def test_provisional_and_accepted_reads_differ_only_in_the_button_field(mixed):
    root, session, _, write = mixed
    write({"Flag_P": False, "Flag_A": False}, 10)
    session.configure(root)
    snap = session.snapshot()
    same = ("id", "label", "where", "dungeon")
    kid = {k: v for k, v in entry(snap, "LW Skull Kid").items() if k not in same}
    saria = {k: v for k, v in entry(snap, "Song from Saria").items() if k not in same}
    assert kid.pop("markable") is True
    assert kid == saria
    unknown = entry(snap, "Test Shop Item")
    assert unknown["collected"] is None and unknown["markable"] is True  # every `?` check carries it too (D9)
    text = json.dumps(snap["state"]["areas"])  # the check entries; the snapshot's paths hold the test's name
    assert "provisional" not in text and "accepted" not in text and "Flag_P" not in text and "Flag_A" not in text
    static = Path(seeds.__file__).parents[1] / "ui" / "static"
    for name in ("tracker.js", "tracker.css", "tracker.html"):
        page = (static / name).read_text(encoding="utf-8") if (static / name).exists() else ""
        assert "provisional" not in page.lower() and "accepted" not in page.lower(), name  # no label or style (D9)


def test_logic_counts_a_marked_check_as_done_whatever_its_read():
    from clawshot.tracker import logic as tracker_logic

    done = [
        {"id": "A", "collected": False, "marked": True},  # a marked provisional false read
        {"id": "B", "collected": None, "marked": True},
        {"id": "C", "collected": True},
    ]
    assert tracker_logic._flag_open(done, None, None, frozenset()) == dict.fromkeys(tracker_logic.AGE_KEYS, 0)
    assert all("in_logic" not in check for check in done)
