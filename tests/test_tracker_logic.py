"""The tracker's in-logic layer (``clawshot.tracker.logic``) on a tiny synthetic world: nothing comes from the game."""

import json
import os

import pytest
from test_tracker_state import build_save, parse

from clawshot.generate import Settings
from clawshot.tracker import TrackerSession, build_state, load_seed, seeds
from clawshot.tracker import logic as tracker_logic
from clawshot.tracker.seeds import Place, installed_version

# A two-age world with the age-return gate closed until adult clears the forest (``age_return_event``).
SPEC = {
    "start": "Root",
    "goal": "Victory",
    "settings": {"starting_age": "child", "age_return_event": "Forest Clear", "age_return_region": "Temple"},
    "items": {name: {} for name in ("Hookshot", "Boomerang", "Key")},
    "regions": [
        {"name": "Root", "exits": {"Field": "age == starting_age or 'Time Travel'"}},
        {
            "name": "Field",
            "exits": {"Temple": "True", "Child Ledge": "age == 'child' and Boomerang"},
            "locations": {
                "Adult Chest": {"rule": "age == 'adult'", "type": "Chest"},
                "Child Chest": {"rule": "age == 'child'", "type": "Chest"},
                "Boomerang Chest": {"rule": "Boomerang", "type": "Chest"},
            },
            "events": {"Forest Clear": "age == 'adult' and Key"},
        },
        {"name": "Temple", "events": {"Time Travel": "True"}},
        {
            "name": "Child Ledge",
            "locations": {"Ledge Chest": {"rule": "True", "type": "Chest"}},
            "events": {"Victory": "True"},
        },
    ],
}
PLACEMENTS = {
    "Adult Chest": "Key",
    "Child Chest": "Boomerang",
    "Boomerang Chest": "Hookshot",
    "Ledge Chest": "Rupees (5)",
}
PLACES = {name: Place("Field", None, "Chest") for name in PLACEMENTS}
GENERATOR = f"clawshot {installed_version()}"


@pytest.fixture
def world(monkeypatch):
    """The tracker's places and logic world come from :data:`SPEC`."""
    monkeypatch.setattr(seeds, "location_index", lambda: PLACES)
    monkeypatch.setattr(tracker_logic, "world_spec", lambda: SPEC)
    return SPEC


def write_seed(tmp_path, *, placements=None, generator=GENERATOR, settings_string="", name="seed-1"):
    root = tmp_path / name
    (root / "seed").mkdir(parents=True)
    spoiler = {
        "generator": generator,
        "seed": 1,
        "settings_string": Settings().to_string() if settings_string == "" else settings_string,
        "settings": {"shuffle": ["Chest"]},
        "placements": PLACEMENTS if placements is None else placements,
        "locations": {
            name: {"name": name, "where": "Field", "ids": [str(100 + i)]} for i, name in enumerate(PLACEMENTS)
        },
    }
    if spoiler["settings_string"] is None:
        del spoiler["settings_string"]
    (root / "seed" / "spoiler.json").write_text(json.dumps(spoiler), encoding="utf-8")
    manifest = {"seed": 1, "output_sha256": "cd" * 32}
    (root / "clawshot-seed.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


def entries(state):
    return {check["id"]: check for area in state["areas"] for check in area["checks"]}


# 3.5 (P3.a)
def test_seed_exposes_settings_string_and_generator(tmp_path, world):
    seed = load_seed(write_seed(tmp_path))
    assert seed.settings_string == Settings().to_string()
    assert seed.generator == GENERATOR
    assert seed.metadata["settings_string"] == seed.settings_string
    missing = load_seed(write_seed(tmp_path, settings_string=None, generator=None, name="bare"))
    assert (missing.settings_string, missing.generator) == (None, None)


# 3.1
def test_same_version_rebuilds_the_world_from_the_settings_string(tmp_path, world):
    loaded = tracker_logic.load_world(load_seed(write_seed(tmp_path)))
    assert loaded.available and loaded.reason is None
    assert sorted(loaded.world.locations) == sorted(PLACEMENTS)
    assert loaded.settings.shuffle == Settings().shuffle


# 3.3
@pytest.mark.parametrize(
    ("options", "reason"),
    [
        ({"generator": "clawshot 0.0.1"}, "clawshot 0.0.1"),
        ({"generator": None}, "generator"),
        ({"settings_string": None}, "settings string"),
        ({"settings_string": "CS1-not-a-string"}, "settings"),
        ({"placements": {**PLACEMENTS, "Gone Chest": "Key"}}, "Gone Chest"),
    ],
)
def test_logic_unavailable_with_a_reason(tmp_path, world, options, reason):
    loaded = tracker_logic.load_world(load_seed(write_seed(tmp_path, **options)))
    assert loaded.available is False and loaded.world is None
    assert reason in loaded.reason


def test_builder_exception_disables_logic(tmp_path, world, monkeypatch):
    def broken(settings, spec=None, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(tracker_logic, "logic_world", broken)
    loaded = tracker_logic.load_world(load_seed(write_seed(tmp_path)))
    assert loaded.available is False and "boom" in loaded.reason


@pytest.mark.parametrize("options", [{"generator": "clawshot 0.0.1"}, {"placements": {**PLACEMENTS, "Gone": "Key"}}])
def test_unavailable_logic_leaves_every_existing_field_unchanged(tmp_path, world, options):
    seed = load_seed(write_seed(tmp_path, **options))
    save = parse({"IsTreasureBoxOpen.100": True})
    plain = build_state(seed, save)
    with_logic = build_state(seed, save, logic=tracker_logic.SeedLogic(tracker_logic.load_world(seed)))
    logic = with_logic.pop("logic")
    assert with_logic == plain
    assert logic["available"] is False and logic["reason"]
    assert not any("in_logic" in check for check in entries(with_logic).values())


# 3.6
def test_spoiler_location_gate(tmp_path, world):
    good = tracker_logic.load_world(load_seed(write_seed(tmp_path)))
    assert good.available
    placements = {**PLACEMENTS, "Missing One": "Key", "Missing Two": "Key"}
    bad = tracker_logic.load_world(load_seed(write_seed(tmp_path, placements=placements, name="bad")))
    assert not bad.available
    assert "Missing One" in bad.reason


# 3.2
def test_world_is_built_once_per_loaded_seed(tmp_path, world, monkeypatch):
    calls = []
    real = tracker_logic.logic_world
    monkeypatch.setattr(tracker_logic, "logic_world", lambda s, spec=None, **kw: calls.append(1) or real(s, spec, **kw))
    root = write_seed(tmp_path)
    slot = root / "user" / "save" / "1" / "slot_00"
    slot.mkdir(parents=True)
    progress = slot / "progress.sav"
    progress.write_bytes(build_save({"IsTreasureBoxOpen.100": False}))
    session = TrackerSession()
    session.configure(root)
    for value in (True, False, True):
        progress.write_bytes(build_save({"IsTreasureBoxOpen.100": value}))
        stat = progress.stat()
        os.utime(progress, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))
        assert session.snapshot()["state"]["logic"]["available"]
        session.snapshot()
    assert calls == [1]
    session.configure(root)
    session.snapshot()
    assert calls == [1, 1]


def test_rutos_letter_autotracks_a_new_saved_pickup_not_an_unchanged_reload(tmp_path, world, monkeypatch):
    field = SPEC["regions"][1]
    letter = "LH Underwater Item"
    spec = {
        **SPEC,
        "items": {**SPEC["items"], "Rutos Letter": {"class": "progression"}},
        "regions": [
            SPEC["regions"][0],
            {
                **field,
                "exits": {**field["exits"], "Child Ledge": "age == 'child' and (Boomerang or Rutos_Letter)"},
                "locations": {
                    **field["locations"],
                    letter: {"rule": "True", "type": "Collectable", "vanilla": "Rutos Letter"},
                },
            },
            *SPEC["regions"][2:],
        ],
    }
    monkeypatch.setattr(tracker_logic, "world_spec", lambda: spec)
    monkeypatch.setattr(seeds, "location_index", lambda: PLACES | {letter: Place("Lake Hylia", None, "Collectable")})
    root = write_seed(tmp_path)
    slot = root / "user" / "save" / "1" / "slot_00"
    slot.mkdir(parents=True)
    progress = slot / "progress.sav"
    flags = {valid: False for _, valid, _ in tracker_logic.state.BOTTLE_SLOTS}
    flags["IsGet.Item_Bottle_Letter"] = False
    progress.write_bytes(build_save(flags))
    session = TrackerSession()
    session.configure(root)

    def collected(current):
        state = current.snapshot()["state"]
        assert state["logic"]["available"], state["logic"]
        return next(c["collected"] for a in state["vanilla_areas"] for c in a["checks"] if c["id"] == letter)

    assert collected(session) is False
    reloaded = TrackerSession()
    reloaded.configure(root)
    assert collected(reloaded) is False
    # A natural after-Jabu save also confirms this native acquisition flag survives changed bottle contents.
    progress.write_bytes(build_save(flags | {"IsGet.Item_Bottle_Letter": True}))
    stat = progress.stat()
    os.utime(progress, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))
    assert collected(session) is True
    reloaded.configure(root)
    assert collected(reloaded) is True


# 3.4
def tree(path):
    return {
        str(p.relative_to(path)): (p.stat().st_mtime_ns, p.stat().st_size, p.is_file() and p.read_bytes())
        for p in sorted(path.rglob("*"))
    }


def test_computing_logic_writes_nothing(tmp_path, world):
    root = write_seed(tmp_path)
    slot = root / "user" / "save" / "1" / "slot_00"
    slot.mkdir(parents=True)
    (slot / "progress.sav").write_bytes(build_save({"IsTreasureBoxOpen.100": True}))
    before = tree(tmp_path)
    session = TrackerSession()
    session.configure(root)
    assert session.snapshot()["state"]["logic"]["available"]
    assert tree(tmp_path) == before


# --- Task 6: in-logic per check.
CHEST_FLAGS = {name: f"IsTreasureBoxOpen.{100 + i}" for i, name in enumerate(PLACEMENTS)}


def logic_state(tmp_path, bools=None, ints=None, *, show_locations=False, name="seed-1"):
    seed = load_seed(write_seed(tmp_path, name=name))
    logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    return build_state(seed, parse(bools or {}, ints or {}), show_locations=show_locations, logic=logic), logic


def open_save(**collected):
    """Every chest's flag present: False (open) unless named True here."""
    return {flag: collected.get(name.replace(" ", "_"), False) for name, flag in CHEST_FLAGS.items()}


# 6.1, 6.2
def test_open_checks_carry_per_age_and_either_in_logic(tmp_path, world):
    state, _ = logic_state(tmp_path, open_save())
    checks = entries(state)
    assert checks["Child Chest"]["in_logic"] == {"child": True, "adult": False, "either": True}
    assert checks["Adult Chest"]["in_logic"] == {"child": False, "adult": True, "either": True}
    assert checks["Boomerang Chest"]["in_logic"] == {"child": False, "adult": False, "either": False}
    assert checks["Ledge Chest"]["in_logic"] == {"child": False, "adult": False, "either": False}
    held, _ = logic_state(tmp_path, open_save(), {"PouchData.Item_Boomerang.StockNum": 1}, name="held")
    assert entries(held)["Ledge Chest"]["in_logic"] == {"child": True, "adult": False, "either": True}
    assert entries(held)["Boomerang Chest"]["in_logic"] == {"child": True, "adult": True, "either": True}


def test_unknown_checks_are_open(tmp_path, world):
    state, _ = logic_state(tmp_path)  # no chest flags: every check unknown
    assert all(c["collected"] is None and "in_logic" in c for c in entries(state).values())


def test_either_comes_from_the_no_age_call(tmp_path, world, monkeypatch):
    calls = []
    real = tracker_logic.Search.can_access

    def spy(self, location, age=None):
        calls.append((location.name, age))
        return age is None or real(self, location, age)

    monkeypatch.setattr(tracker_logic.Search, "can_access", spy)
    state, _ = logic_state(tmp_path, open_save())
    assert ("Boomerang Chest", None) in calls
    assert entries(state)["Boomerang Chest"]["in_logic"] == {"child": False, "adult": False, "either": True}


# 6.3, 6.4
def test_collected_checks_carry_no_in_logic_and_areas_count_by_age(tmp_path, world):
    state, _ = logic_state(tmp_path, open_save(Child_Chest=True))
    checks = entries(state)
    assert "in_logic" not in checks["Child Chest"]
    [area] = state["areas"]
    assert area["in_logic"] == {"child": 0, "adult": 1, "either": 1}


# 6.5
def test_search_reruns_only_when_the_inventory_changes(tmp_path, world, monkeypatch):
    built = []
    real = tracker_logic.Search

    def counting(*args, **kwargs):
        built.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(tracker_logic, "Search", counting)
    seed = load_seed(write_seed(tmp_path))
    logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    for collected in (False, True, False):  # the checks change, the inventory does not
        build_state(seed, parse(open_save(Child_Chest=collected)), logic=logic)
    assert len(built) == 1
    build_state(seed, parse(open_save(), {"PouchData.Item_Boomerang.StockNum": 1}), logic=logic)
    assert len(built) == 2


# 6.6
def test_in_logic_reveals_no_item(tmp_path, world):
    state, _ = logic_state(tmp_path, open_save())
    assert all("item" not in c and "item_label" not in c for c in entries(state).values())
    shown, _ = logic_state(tmp_path, open_save(), show_locations=True, name="shown")
    assert entries(shown)["Child Chest"]["item"] == "Boomerang"


# 6.7 (P6.a)
def test_state_logic_object(tmp_path, world):
    state, _ = logic_state(tmp_path, open_save())
    logic = state["logic"]
    assert set(logic) == {"available", "reason", "unknown_items", "save_age"}
    assert logic["available"] is True and logic["reason"] is None
    assert "hookshot" in logic["unknown_items"]
    assert "available" in tracker_logic.__doc__ and "unknown_items" in tracker_logic.__doc__


# --- Task 8: manual marks in the state.
def unknown_child_chest():
    """Every chest flag present except the Child Chest's: that check reads unknown."""
    bools = open_save()
    del bools[CHEST_FLAGS["Child Chest"]]
    return bools


# 8.1
def test_marked_check_is_marked_not_collected_and_done(tmp_path, world):
    seed = load_seed(write_seed(tmp_path))
    logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    state = build_state(seed, parse(unknown_child_chest()), logic=logic, marks=frozenset({"Child Chest"}))
    entry = entries(state)["Child Chest"]
    assert entry["marked"] is True and entry["collected"] is None
    assert "in_logic" not in entry
    [area] = state["areas"]
    assert (area["marked"], area["collected"], area["unknown"]) == (1, 0, 1)
    assert area["in_logic"]["child"] == 0  # the marked check is done: not in the open list
    plain = build_state(seed, parse(unknown_child_chest()), logic=logic)
    assert "marked" not in entries(plain)["Child Chest"] and plain["areas"][0]["marked"] == 0


def test_marks_on_save_confirmed_checks_are_ignored(tmp_path, world):
    seed = load_seed(write_seed(tmp_path))
    state = build_state(seed, parse(open_save()), marks=frozenset({"Child Chest"}))
    assert "marked" not in entries(state)["Child Chest"] and state["areas"][0]["marked"] == 0


# 8.2
def test_a_mark_adds_nothing_to_the_inventory(tmp_path, world):
    seed = load_seed(write_seed(tmp_path))
    save = parse(unknown_child_chest())
    logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    marked = build_state(seed, save, logic=logic, marks=frozenset({"Child Chest"}))
    plain = build_state(seed, save, logic=logic)
    # The Child Chest holds the Boomerang: marking it must not open the Boomerang Chest.
    assert entries(marked)["Boomerang Chest"]["in_logic"] == entries(plain)["Boomerang Chest"]["in_logic"]
    assert entries(marked)["Boomerang Chest"]["in_logic"]["either"] is False


# 8.3
def test_a_marked_checks_item_stays_hidden_without_spoilers(tmp_path, world):
    seed = load_seed(write_seed(tmp_path))
    state = build_state(seed, parse(unknown_child_chest()), marks=frozenset({"Child Chest"}))
    assert "item" not in entries(state)["Child Chest"] and "item_label" not in entries(state)["Child Chest"]
    shown = build_state(seed, parse(unknown_child_chest()), marks=frozenset({"Child Chest"}), show_locations=True)
    assert entries(shown)["Child Chest"]["item"] == "Boomerang"


# 8.4
@pytest.fixture
def marks_folder(tmp_path, monkeypatch):
    from clawshot.app import preferences

    prefs = tmp_path / "prefs"
    monkeypatch.setattr(preferences, "user_preferences_path", lambda: prefs / "paths.json")
    return prefs


def session_with_save(tmp_path, bools):
    root = write_seed(tmp_path)
    slot = root / "user" / "save" / "1" / "slot_00"
    slot.mkdir(parents=True)
    progress = slot / "progress.sav"
    progress.write_bytes(build_save(bools))
    session = TrackerSession()
    session.configure(root)
    return session, progress


def resave(progress, bools):
    progress.write_bytes(build_save(bools))
    stat = progress.stat()
    os.utime(progress, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))


@pytest.mark.parametrize("value", [True, False])
def test_a_save_confirmed_state_replaces_and_removes_the_mark(tmp_path, world, marks_folder, value):
    from clawshot.tracker import marks

    session, progress = session_with_save(tmp_path, unknown_child_chest())
    session.mark("Child Chest", True)
    assert entries(session.snapshot()["state"])["Child Chest"]["marked"] is True
    resave(progress, {**unknown_child_chest(), CHEST_FLAGS["Child Chest"]: value})
    entry = entries(session.snapshot()["state"])["Child Chest"]
    assert entry["collected"] is value and "marked" not in entry
    assert marks.MarkStore().marks("cd" * 32, str(progress.parent.parent)) == frozenset()


def test_marks_follow_the_game_into_its_next_save_slot(tmp_path, world, marks_folder):
    """The remake writes each save to the next slot of its save folder: marks belong to the folder, not the slot."""
    session, progress = session_with_save(tmp_path, unknown_child_chest())
    session.mark("Child Chest", True)
    following = progress.parent.parent / "slot_01" / "progress.sav"
    following.parent.mkdir()
    resave(following, unknown_child_chest())
    snapshot = session.snapshot()
    assert snapshot["selected_slot"] == "slot_01"
    assert entries(snapshot["state"])["Child Chest"]["marked"] is True
    again = TrackerSession()  # a restart of Clawshot
    again.configure(progress.parents[4])
    assert entries(again.snapshot()["state"])["Child Chest"]["marked"] is True


def test_a_failed_marks_update_warns_and_the_save_still_wins(tmp_path, world, marks_folder, monkeypatch):
    """A marks file that can't be rewritten must not freeze the tracker on old data (review of PR #36)."""
    from clawshot.tracker import marks

    session, progress = session_with_save(tmp_path, unknown_child_chest())
    session.mark("Child Chest", True)

    def fail(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(marks.os, "replace", fail)
    resave(progress, {**unknown_child_chest(), CHEST_FLAGS["Child Chest"]: True})
    snapshot = session.snapshot()
    assert snapshot["status"] == "ok"
    assert entries(snapshot["state"])["Child Chest"]["collected"] is True
    assert any(w.startswith(marks.WARNING_PREFIX) for w in snapshot["state"]["warnings"])
    resave(progress, {**unknown_child_chest(), CHEST_FLAGS["Child Chest"]: False})
    assert entries(session.snapshot()["state"])["Child Chest"]["collected"] is False  # still follows new saves


def test_obs_leaves_out_marks_warnings(tmp_path, world, marks_folder):
    from clawshot.tracker import marks
    from clawshot.ui.tracker import TrackerController

    marks_folder.mkdir()
    (marks_folder / marks.MARKS_FILE).write_bytes(b"{not json")
    controller = TrackerController()
    controller.session, _ = session_with_save(tmp_path, unknown_child_chest())
    app = controller.snapshot()
    assert any(w.startswith(marks.WARNING_PREFIX) for w in app["state"]["warnings"] + app.get("warnings", []))
    obs = controller.snapshot(obs=True)
    shown = obs["state"]["warnings"] + obs.get("warnings", [])
    assert not any(str(w).startswith(marks.WARNING_PREFIX) for w in shown)


# 10.1 (5.2)
@pytest.mark.parametrize(("value", "age"), [(True, "child"), (False, "adult"), (None, None)])
def test_save_age_reads_sequence_is_childhood(tmp_path, world, value, age):
    bools = open_save() | ({} if value is None else {"Sequence_IsChildhood": value})
    state, _ = logic_state(tmp_path, bools)
    assert state["logic"]["save_age"] == age


# --- Task 12: the OBS view is unchanged.
def test_obs_payload_is_unchanged_by_logic_and_marks(tmp_path, world, marks_folder, monkeypatch):
    import json as json_module

    from clawshot.ui.tracker import TrackerController

    def obs_payload(*, logic, mark):
        if not logic:
            monkeypatch.setattr(tracker_logic, "load_world", lambda seed: tracker_logic.LogicWorld(False, "off"))
        controller = TrackerController()
        session, _ = session_with_save(tmp_path / ("on" if logic else "off"), unknown_child_chest())
        controller.session = session
        if mark:
            session.mark("Child Chest", True)
        return controller.snapshot(obs=True)

    with_feature = obs_payload(logic=True, mark=True)
    without = obs_payload(logic=False, mark=False)
    assert "logic" not in with_feature["state"]
    text = json_module.dumps(with_feature)
    assert "in_logic" not in text and "marked" not in text
    assert [sorted(area) for area in with_feature["state"]["areas"]] == [["collected", "name", "total", "unknown"]]
    for payload in (with_feature, without):
        payload["state"]["seed"].pop("root"), payload["state"]["seed"].pop("seed_dir")
        payload.pop("seed_path")
        payload.pop("revision")  # the mark changed the app's state once more
    assert with_feature == without


# 14.3 (P14.a)
def test_same_seed_save_and_marks_give_equal_json(tmp_path, world):
    import json as json_module

    seed = load_seed(write_seed(tmp_path))
    save = parse(unknown_child_chest(), {"PouchData.Item_Boomerang.StockNum": 1})
    marks = frozenset({"Child Chest"})

    def build():
        logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
        return json_module.dumps(build_state(seed, save, logic=logic, marks=marks), sort_keys=True)

    assert build() == build()


# --- Round 21: skips (plans/rounds/r21-tracker.md).
def test_a_skipped_check_leaves_the_open_set_and_only_read_not_collected_checks_skip(tmp_path, world):
    seed = load_seed(write_seed(tmp_path))
    logic = tracker_logic.SeedLogic(tracker_logic.load_world(seed))
    skips = frozenset({"Child Chest", "Boomerang Chest"})
    state = build_state(seed, parse(open_save(Boomerang_Chest=True)), logic=logic, skips=skips)
    child, boomerang = entries(state)["Child Chest"], entries(state)["Boomerang Chest"]
    assert child["skippable"] is True and child["skipped"] is True and "in_logic" not in child
    assert boomerang["collected"] is True and "skipped" not in boomerang and "skippable" not in boomerang
    [area] = state["areas"]
    assert area["skipped"] == 1 and area["in_logic"]["child"] == 0
    unknown = build_state(seed, parse(unknown_child_chest()), logic=logic, skips=skips)
    assert "skippable" not in entries(unknown)["Child Chest"] and "skipped" not in entries(unknown)["Child Chest"]


def test_skips_survive_save_reads_and_clear_marks_removes_them(tmp_path, world, marks_folder):
    session, progress = session_with_save(tmp_path, open_save(Boomerang_Chest=True))
    with pytest.raises(ValueError, match="only a check the save reads"):
        session.skip("Boomerang Chest", True)  # collected: nothing to skip
    with pytest.raises(ValueError, match="already says"):
        session.mark("Child Chest", True)  # read by the save: a skip, not a mark
    session.skip("Child Chest", True)
    resave(progress, open_save(Boomerang_Chest=True))
    assert entries(session.snapshot()["state"])["Child Chest"]["skipped"] is True  # a save read keeps it
    session.skip("Child Chest", False)
    assert "skipped" not in entries(session.snapshot()["state"])["Child Chest"]
    session.skip("Child Chest", True)
    session.clear_marks()
    assert "skipped" not in entries(session.snapshot()["state"])["Child Chest"]
