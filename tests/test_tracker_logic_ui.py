"""The Checks tab's in-logic display, age control, list controls, manual marks and side panel: the shipped tracker.js
under Node."""

import pytest
from test_tracker_options import NODE, render_tracker

from clawshot.ui.server import ASSETS, STATIC

pytestmark = pytest.mark.skipif(NODE is None, reason="Node is needed only for frontend rendering tests")
AGE_KEY = "clawshot.tracker.age"


def check(check_id, collected, in_logic=None, *, marked=False, markable=None):
    entry = {"id": check_id, "label": check_id, "where": "", "kind": "chest", "dungeon": None, "collected": collected}
    if collected is None if markable is None else markable:
        entry["markable"] = True  # as tracker.state sets it: every unknown check, or a provisional "not collected"
    if in_logic is not None:
        entry["in_logic"] = dict(zip(("child", "adult", "either"), in_logic, strict=True))
    if marked:
        entry["marked"] = True
    return entry


def snapshot(*, available=True, reason=None, save_age="child", unknown_items=()):
    """Two areas: Field (child-only, adult-only, collected, marked) and Lake (one open check in logic for neither)."""
    field = [
        check("Child Chest", False, (True, False, True)),
        check("Adult Chest", None, (False, True, True)),
        check("Done Chest", True),
        check("Shop Item", None, marked=True),
    ]
    lake = [check("Far Chest", False, (False, False, False))]
    areas = [
        {"name": "Field", "collected": 1, "total": 4, "unknown": 2, "marked": 1, "checks": field},
        {"name": "Lake", "collected": 0, "total": 1, "unknown": 0, "marked": 0, "checks": lake},
    ]
    if not available:
        for area in areas:
            for entry in area["checks"]:
                entry.pop("in_logic", None)
    else:
        for area in areas:
            area["in_logic"] = {
                age: sum(bool(c.get("in_logic", {}).get(age)) for c in area["checks"])
                for age in ("child", "adult", "either")
            }
    state = {
        "seed": {"seed": 1},
        "dungeons": [],
        "items": [{"id": "hookshot", "group": "upgrades", "label": "Hookshot", "held": None, "max_tier": 2}],
        "songs": [],
        "rewards": [],
        "hearts": {},
        "tokens": None,
        "skulltula_checks": {"collected": 0, "total": 0, "unknown": 0},
        "areas": areas,
        "show_locations": False,
        "warnings": [],
        "logic": {"available": available, "reason": reason, "unknown_items": list(unknown_items), "save_age": save_age},
    }
    return {"status": "ok", "state": state, "slots": [], "selected_slot": "slot_00", "revision": 1, "warnings": []}


def tab(tmp_path, snap=None, **page):
    return render_tracker(tmp_path, snap or snapshot(), obs=False, **page)


def classes(rendered):
    return {entry["id"]: entry for entry in rendered["checks"]}


def styled(rendered, name):
    entry = classes(rendered)[name]["className"].split()
    if "tracker-check-in-logic" in entry:
        return "in"
    if "tracker-check-out-of-logic" in entry:
        return "out"
    if "tracker-check-collected" in entry:
        return "collected"
    if "tracker-check-marked" in entry:
        return "marked"
    return "plain"


# 10.2 (5.1)
def test_age_control_defaults_to_either(tmp_path):
    rendered = tab(tmp_path)
    assert (rendered["controls"]["age"]["value"], rendered["controls"]["age"]["disabled"]) == ("either", False)
    assert styled(rendered, "Child Chest") == "in" and styled(rendered, "Adult Chest") == "in"
    assert styled(rendered, "Far Chest") == "out"


# 10.3 (5.2)
def test_follow_save_uses_the_saves_age_or_either_with_a_note(tmp_path):
    follow = [{"id": "tracker-age", "value": "save", "event": "change"}]
    rendered = tab(tmp_path, snapshot(save_age="adult"), actions=follow)
    assert styled(rendered, "Child Chest") == "out" and styled(rendered, "Adult Chest") == "in"
    assert not any("Follow save" in note for note in rendered["notes"])
    unreadable = tab(tmp_path, snapshot(save_age=None), actions=follow)
    assert styled(unreadable, "Child Chest") == "in" and styled(unreadable, "Adult Chest") == "in"
    assert [note for note in unreadable["notes"] if "Follow save" in note] and len(unreadable["notes"]) == 1


# 10.4 (5.3)
def test_a_non_default_age_persists_and_storage_may_be_unavailable(tmp_path):
    chosen = tab(tmp_path, actions=[{"id": "tracker-age", "value": "child", "event": "change"}])
    assert chosen["storage"] == {AGE_KEY: "child"}
    back = tab(
        tmp_path, storage={AGE_KEY: "child"}, actions=[{"id": "tracker-age", "value": "either", "event": "change"}]
    )
    assert back["storage"] == {}
    restored = tab(tmp_path, storage={AGE_KEY: "adult"})
    assert restored["controls"]["age"]["value"] == "adult"
    assert tab(tmp_path, storage={AGE_KEY: "nonsense"})["controls"]["age"]["value"] == "either"
    private = tab(tmp_path, storage=None, actions=[{"id": "tracker-age", "value": "adult", "event": "change"}])
    assert private["controls"]["age"]["value"] == "adult"
    assert styled(private, "Child Chest") == "out"


# 10.5 (5.4), 11.1 (6.1), 11.2 (6.2)
@pytest.mark.parametrize(
    ("age", "child_chest", "adult_chest", "counts"),
    [("child", "in", "out", (1, 0)), ("adult", "out", "in", (1, 0)), ("either", "in", "in", (2, 0))],
)
def test_styles_and_area_counts_follow_the_age(tmp_path, age, child_chest, adult_chest, counts):
    rendered = tab(tmp_path, actions=[{"id": "tracker-age", "value": age, "event": "change"}])
    assert (styled(rendered, "Child Chest"), styled(rendered, "Adult Chest")) == (child_chest, adult_chest)
    assert styled(rendered, "Done Chest") == "collected"
    assert styled(rendered, "Shop Item") == "marked"
    heads = [head["text"] for head in rendered["areaHeads"]]
    assert [f"{n} in logic" in head for head, n in zip(heads, counts, strict=True)] == [True, True]


# 11.3 (6.3)
def test_show_only_in_logic_hides_the_rest_and_collapses_empty_areas(tmp_path):
    rendered = tab(
        tmp_path,
        actions=[
            {"id": "tracker-age", "value": "child", "event": "change"},
            {"id": "tracker-show", "value": "logic", "event": "change"},
        ],
    )
    shown = {name for name, entry in classes(rendered).items() if entry["shown"]}
    assert shown == {"Child Chest"}
    assert [head["shown"] for head in rendered["areaHeads"]] == [True, False]


# 11.4 (6.4)
def test_unavailable_logic_disables_the_controls_and_says_why(tmp_path):
    rendered = tab(tmp_path, snapshot(available=False, reason="This seed was made by clawshot 0.0.1"))
    assert rendered["controls"]["age"]["disabled"] and {"value": "logic", "disabled": True} in rendered["showOptions"]
    assert [note for note in rendered["notes"] if "clawshot 0.0.1" in note]
    assert {styled(rendered, name) for name in ("Child Chest", "Adult Chest", "Far Chest")} == {"plain"}
    assert not any("in logic" in head["text"] for head in rendered["areaHeads"])


# 11.5 (6.5); round 21: the unread items are named in the side panel's In logic row, not above the list.
def test_unknown_items_say_in_logic_may_be_conservative(tmp_path):
    point = [{"check": "Child Chest", "event": "pointerover"}]
    rendered = tab(tmp_path, snapshot(unknown_items=["hookshot", "Forest Temple small keys"]), actions=point)
    assert not [note for note in rendered["notes"] if "conservative" in note]
    body = rendered["details"]["body"]
    assert "May be conservative" in body and "Hookshot" in body and "Forest Temple small keys" in body
    assert "conservative" not in tab(tmp_path, actions=point)["details"]["body"]


# 11.6 (4.1, 4.2, 4.8); round 21: the row itself is the toggle, no Mark done button.
def test_clicking_a_check_the_save_cannot_read_marks_it(tmp_path):
    rendered = tab(tmp_path, actions=[{"check": "Adult Chest", "event": "click"}])
    actionable = {name for name, entry in classes(rendered).items() if not entry["disabled"]}
    assert actionable == {"Adult Chest", "Shop Item"}  # only checks the save cannot read
    assert rendered["posts"] == [{"route": "tracker-mark", "body": {"check": "Adult Chest", "marked": True}}]
    unmark = tab(tmp_path, actions=[{"check": "Shop Item", "event": "click"}])
    assert unmark["posts"] == [{"route": "tracker-mark", "body": {"check": "Shop Item", "marked": False}}]
    for read in ("Child Chest", "Done Chest", "Far Chest"):  # read by the save: clicking only selects
        assert tab(tmp_path, actions=[{"check": read, "event": "click"}])["posts"] == []


def test_a_markable_not_collected_check_has_the_toggle_and_keeps_in_logic_styling(tmp_path):
    """tracker-auto-checks 3.2: a provisional track read of "not collected" stays open with Mark done; marked, it
    shows as marked done like a marked unknown check. Round 21: the row itself is the toggle."""
    snap = snapshot()
    lake = snap["state"]["areas"][1]["checks"]
    lake.append(check("Maybe Gift", False, (True, True, True), markable=True))
    lake.append(check("Kept Gift", False, markable=True, marked=True))
    rendered = tab(tmp_path, snap, actions=[{"check": "Maybe Gift", "event": "click"}])
    found = classes(rendered)
    assert not found["Maybe Gift"]["disabled"] and styled(rendered, "Maybe Gift") == "in"
    assert not found["Kept Gift"]["disabled"] and styled(rendered, "Kept Gift") == "marked"
    assert found["Far Chest"]["disabled"]  # not collected without markable: no toggle
    assert rendered["posts"] == [{"route": "tracker-mark", "body": {"check": "Maybe Gift", "marked": True}}]
    unmark = tab(tmp_path, snap, actions=[{"check": "Kept Gift", "event": "click"}])
    assert unmark["posts"] == [{"route": "tracker-mark", "body": {"check": "Kept Gift", "marked": False}}]


def test_clear_marks_asks_first(tmp_path):
    clear = [{"id": "tracker-clear-marks", "event": "click"}]
    assert tab(tmp_path, actions=clear, confirm=False)["posts"] == []
    assert tab(tmp_path, actions=clear, confirm=True)["posts"] == [
        {"route": "tracker-clear-marks", "body": {"confirmed": True}}
    ]


def test_check_names_without_spoilers_show_no_items(tmp_path):
    rendered = tab(tmp_path)
    assert all(":" not in entry["text"] for entry in rendered["checks"])


def test_obs_shows_no_checks_or_controls(tmp_path):
    rendered = render_tracker(tmp_path, snapshot(), obs=True)
    assert rendered["checks"] == [] and rendered["notes"] == []
    assert set(rendered["controls"].values()) == {None} and rendered["legend"] == [] and rendered["details"] is None


# 11.7 (P11.a): no new static file; the three tracker assets stay the served ones.
def test_no_new_static_files():
    tracker_files = sorted(name for name in STATIC if name.startswith("tracker"))
    assert tracker_files == ["tracker.css", "tracker.html", "tracker.js"]
    assert sorted(p.name for p in ASSETS.glob("tracker*")) == tracker_files


# --- Task 16: vanilla pick-ups (D19, 8.6).
VANILLA_KEY = "clawshot.tracker.vanilla"


def with_vanilla(**options):
    """The snapshot plus a vanilla row in Field (open, in logic for child) and a vanilla-only Fountain area."""
    snap = snapshot(**options)
    row = check("Letter Pickup", False, (True, False, True)) | {"vanilla": True, "item": "Rutos Letter"}
    row["item_label"] = "Ruto's Letter"
    far = check("Fountain Pickup", False, (False, False, False)) | {"vanilla": True, "item": "Silver Scale"}
    snap["state"]["vanilla_areas"] = [
        {
            "name": "Field",
            "collected": 0,
            "total": 1,
            "unknown": 0,
            "marked": 0,
            "checks": [row],
            "in_logic": {"child": 1, "adult": 0, "either": 1},
        },
        {
            "name": "Fountain",
            "collected": 0,
            "total": 1,
            "unknown": 0,
            "marked": 0,
            "checks": [far],
            "in_logic": {"child": 0, "adult": 0, "either": 0},
        },
    ]
    return snap


def test_vanilla_rows_show_in_their_area_by_default_with_a_tag(tmp_path):
    rendered = tab(tmp_path, with_vanilla())
    assert rendered["controls"]["vanilla"] == {"checked": True, "disabled": False}
    letter = classes(rendered)["Letter Pickup"]
    assert "tracker-check-vanilla" in letter["className"] and "vanilla" in letter["text"]
    assert "Ruto's Letter" in letter["text"] and styled(rendered, "Letter Pickup") == "in"
    assert styled(rendered, "Fountain Pickup") == "out"
    heads = [head["text"] for head in rendered["areaHeads"]]
    assert heads == ["2 / 5 done · 3 in logic", "0 / 1 done · 0 in logic", "0 / 1 done · 0 in logic"]


def test_the_vanilla_toggle_hides_them_and_is_remembered(tmp_path):
    hide = [{"id": "tracker-vanilla", "checked": False, "event": "change"}]
    rendered = tab(tmp_path, with_vanilla(), actions=hide)
    assert "Letter Pickup" not in classes(rendered) and len(rendered["areaHeads"]) == 2
    assert rendered["storage"] == {VANILLA_KEY: "hidden"}
    restored = tab(tmp_path, with_vanilla(), storage={VANILLA_KEY: "hidden"})
    assert restored["controls"]["vanilla"]["checked"] is False
    back = tab(
        tmp_path,
        with_vanilla(),
        storage={VANILLA_KEY: "hidden"},
        actions=[{"id": "tracker-vanilla", "checked": True, "event": "change"}],
    )
    assert back["storage"] == {} and "Letter Pickup" in classes(back)
    private = tab(tmp_path, with_vanilla(), storage=None, actions=hide)
    assert "Letter Pickup" not in classes(private)


def test_show_only_in_logic_applies_to_vanilla_rows(tmp_path):
    only = [{"id": "tracker-show", "value": "logic", "event": "change"}]
    rendered = classes(tab(tmp_path, with_vanilla(), actions=only))
    assert rendered["Letter Pickup"]["shown"] is True
    assert rendered["Fountain Pickup"]["shown"] is False


def test_vanilla_toggle_is_disabled_without_logic(tmp_path):
    rendered = tab(tmp_path, with_vanilla(available=False, reason="old seed"))
    assert rendered["controls"]["vanilla"]["disabled"] is True
    assert "Letter Pickup" not in classes(rendered)


# --- Round 21: the Checks tab's states, legend, list controls, no-save state and side panel.
SHOW_KEY, FINISHED_KEY, COLLAPSED_KEY = (
    "clawshot.tracker.show",
    "clawshot.tracker.hide-finished",
    "clawshot.tracker.collapsed",
)


def test_rows_have_no_prefix_symbols_and_the_legend_names_each_state(tmp_path):
    rendered = tab(tmp_path)
    assert not [entry["text"] for entry in rendered["checks"] if entry["text"][:1] in "?—✓☑"]
    [legend] = rendered["legend"]
    assert all(word in legend["text"] for word in ("Collected", "Marked", "In logic", "Out of logic", "Mark by hand"))
    assert "Skipped" not in legend["text"] and legend["shown"]  # no check offers a skip


def marked(snap, name, key="marked"):
    for area in snap["state"]["areas"]:
        for entry in area["checks"]:
            if entry["id"] == name:
                entry[key] = True
                entry.pop("in_logic", None)
    return snap


def test_open_checks_hides_finished_rows_and_all_checks_brings_back_a_misclick(tmp_path):
    rendered = tab(
        tmp_path,
        after=marked(snapshot(), "Adult Chest"),
        actions=[
            {"id": "tracker-show", "value": "open", "event": "change"},
            {"check": "Adult Chest", "event": "click"},  # marked by mistake
        ],
    )
    assert {name for name, entry in classes(rendered).items() if entry["shown"]} == {"Child Chest", "Far Chest"}
    assert rendered["storage"] == {SHOW_KEY: "open"}
    undo = tab(
        tmp_path,
        marked(snapshot(), "Adult Chest"),
        storage={SHOW_KEY: "open"},
        actions=[
            {"id": "tracker-show", "value": "all", "event": "change"},
            {"check": "Adult Chest", "event": "click"},
        ],
    )
    assert classes(undo)["Adult Chest"]["shown"] and styled(undo, "Adult Chest") == "marked"
    assert undo["posts"] == [{"route": "tracker-mark", "body": {"check": "Adult Chest", "marked": False}}]
    assert undo["storage"] == {}


def test_a_check_the_save_reads_can_be_skipped_when_the_backend_offers_it(tmp_path):
    snap = snapshot()
    snap["state"]["areas"][0]["checks"][0]["skippable"] = True  # Child Chest: read by the save, not collected
    rendered = tab(tmp_path, snap, actions=[{"check": "Child Chest", "event": "click"}])
    assert rendered["posts"] == [
        {"route": "tracker-mark", "body": {"check": "Child Chest", "marked": True, "kind": "skip"}}
    ]
    assert "Skipped" in rendered["legend"][0]["text"]
    skipped = marked(snapshot(), "Child Chest", "skipped")
    undo = tab(tmp_path, skipped, actions=[{"check": "Child Chest", "event": "click"}])
    assert "tracker-check-skipped" in classes(undo)["Child Chest"]["className"]
    assert undo["posts"] == [
        {"route": "tracker-mark", "body": {"check": "Child Chest", "marked": False, "kind": "skip"}}
    ]
    assert "1 in logic" in undo["areaHeads"][0]["text"]  # a skipped check leaves the in-logic count


def test_areas_collapse_and_remember_it_and_finished_areas_can_hide(tmp_path):
    fold = tab(tmp_path, actions=[{"class": "tracker-area-head", "index": 0, "event": "click"}])
    assert [entry["shown"] for entry in fold["checks"]] == [False] * 4 + [True]
    assert fold["storage"] == {COLLAPSED_KEY: '["Field"]'}
    restored = tab(tmp_path, storage={COLLAPSED_KEY: '["Field", "Gone"]'})
    assert [entry["shown"] for entry in restored["checks"]] == [False] * 4 + [True]
    expand = tab(
        tmp_path, storage={COLLAPSED_KEY: '["Field"]'}, actions=[{"id": "tracker-expand-all", "event": "click"}]
    )
    assert all(entry["shown"] for entry in expand["checks"]) and expand["storage"] == {}
    folded = tab(tmp_path, actions=[{"id": "tracker-collapse-all", "event": "click"}])
    assert folded["storage"] == {COLLAPSED_KEY: '["Field","Lake"]'}
    done = snapshot()
    done["state"]["areas"][1]["checks"][0] |= {"collected": True}
    done["state"]["areas"][1]["checks"][0].pop("in_logic")
    hidden = tab(tmp_path, done, actions=[{"id": "tracker-hide-finished", "checked": True, "event": "change"}])
    assert [head["shown"] for head in hidden["areaHeads"]] == [True, False]
    assert hidden["storage"] == {FINISHED_KEY: "1"}


def unsaved(snap):
    snap["status"] = "waiting"
    snap["selected_slot"] = None
    snap["warnings"] = ["No save in this folder yet: save in the game to start tracking."]
    return snap


def waiting(**options):
    return unsaved(snapshot(**options))


def test_before_any_save_the_tabs_say_so_instead_of_unknown_rows(tmp_path):
    rendered = tab(
        tmp_path,
        waiting(unknown_items=["hookshot"]),
        actions=[{"check": "Adult Chest", "event": "click"}],
    )
    assert rendered["noSave"] and "No save loaded yet" in rendered["noSave"][0]
    assert rendered["cells"] == [] and rendered["counts"] == []  # no wall of unknown items
    assert "No save loaded yet" in rendered["checksStatus"][0]
    assert all(entry["disabled"] for entry in rendered["checks"]) and rendered["posts"] == []
    assert {styled(rendered, name) for name in ("Child Chest", "Adult Chest", "Far Chest")} == {"plain"}
    assert rendered["notes"] == [] and not rendered["legend"][0]["shown"]
    assert all(rendered["controls"][name]["disabled"] for name in ("age", "show", "finished", "clear"))
    assert [head["text"] for head in rendered["areaHeads"]] == ["4 checks", "1 checks"]


def test_the_side_panel_shows_the_pointed_checks_directions_save_and_logic(tmp_path):
    snap = snapshot(unknown_items=["hookshot"])
    adult = snap["state"]["areas"][0]["checks"][1]
    adult |= {"where": "Field, behind the big tree", "reason": "shop slots restock and keep no sold record"}
    idle = tab(tmp_path, snap)
    assert idle["details"]["title"] == "Checks" and idle["details"]["shown"]
    rendered = tab(tmp_path, snap, actions=[{"check": "Adult Chest", "event": "pointerover"}])
    details = rendered["details"]
    assert (details["title"], details["text"]) == ("Adult Chest", "Field, behind the big tree")
    assert "In logic as adult; child can't reach it yet" in details["body"]
    assert "May be conservative" in details["body"]
    assert "Your save can't show this check (shop slots restock and keep no sold record)" in details["body"]
    assert "Area" in details["body"] and "Field" in details["body"] and "marks it done" in details["body"]
    assert rendered["posts"] == []  # pointing only selects
    done = tab(tmp_path, snap, actions=[{"check": "Done Chest", "event": "pointerover"}])["details"]
    assert "Collected (your save)" in done["body"] and "records this chest once it is opened" in done["body"]


def test_rows_drop_their_areas_prefix_and_the_panel_keeps_the_full_name(tmp_path):
    snap = snapshot()
    names = {
        "Lake Hylia": [
            "LH GS Bean Patch",
            "Lake Hylia: Island Chest",
            "Lake Hylia Underwater Rupee 1",
            "Zora Shop Item",
        ],
        "Land outside Ganon's Castle": ["OGC GS"],
        "Jabu-Jabu's Belly": ["Jabu Jabus Belly GS Near Boss", "KF Odd Row"],
    }
    snap["state"]["areas"] = [
        {"name": area, "checks": [check(name, False) for name in rows]} for area, rows in names.items()
    ]
    rendered = tab(tmp_path, snap, actions=[{"check": "LH GS Bean Patch", "event": "pointerover"}])
    assert [entry["text"] for entry in rendered["checks"]] == [
        "Skulltula: Bean Patch",
        "Island Chest",
        "Underwater Rupee 1",
        "Zora Shop Item",
        "Skulltula",
        "Skulltula: Near Boss",
        "KF Odd Row",  # another area's code stays
    ]
    assert rendered["details"]["title"] == "LH GS Bean Patch"


def test_obs_never_shows_warnings(tmp_path):
    snap = snapshot()
    snap["warnings"] = ["Cannot confirm this save belongs to this seed: neither adds saved flags."]
    snap["state"]["warnings"] = ["The save has none of this seed's chest records."]
    assert render_tracker(tmp_path, snap, obs=True)["warnings"] == [""]
    assert "Cannot confirm" in tab(tmp_path, snap)["warnings"][0]


def source_snapshot():
    snap = snapshot()
    # The adult has a direct route; only the child route borrows an adult-supplied resource.
    snap["state"]["areas"][0]["checks"][0]["in_logic"]["adult"] = True
    snap["state"]["areas"][0]["checks"][0]["assumed_sources"] = {
        "child": [
            {
                "item": "Deku Nut Drop",
                "sources": [
                    {
                        "region": "KF Outside Deku Tree",
                        "ages": ["adult"],
                        "rule": "can_use(Bow)",
                    }
                ],
            }
        ],
        "adult": [],
        "either": [],
    }
    return snap


def test_source_marker_follows_the_selected_age_and_names_the_derived_source_not_a_reward(tmp_path):
    actions = [
        {"id": "tracker-age", "value": "child", "event": "change"},
        {"check": "Child Chest", "event": "pointerover"},
    ]
    rendered = tab(tmp_path, source_snapshot(), actions=actions)
    row = classes(rendered)["Child Chest"]
    assert "tracker-check-needs-source" in row["className"]
    assert "Deku Nuts" not in row["text"]  # details, not the check's hidden reward
    body = rendered["details"]["body"]
    assert "Needs a source" in body and "Deku Nuts (Deku Nut Drop)" in body
    assert "Deku Babas in Kokiri Forest, outside the Deku Tree, as adult" in body
    assert "Not saved stock" in body and "One sufficient route" in body
    either = tab(
        tmp_path, source_snapshot(), actions=actions + [{"id": "tracker-age", "value": "either", "event": "change"}]
    )
    assert "tracker-check-needs-source" not in classes(either)["Child Chest"]["className"]
    assert "Needs a source" not in either["details"]["body"]
    assert "Needs a source" in rendered["legend"][0]["text"]


@pytest.mark.parametrize("done", ["collected", "marked", "skipped"])
def test_finished_checks_never_show_a_stale_source_marker(tmp_path, done):
    snap = source_snapshot()
    snap["state"]["areas"][0]["checks"][0][done] = True
    rendered = tab(tmp_path, snap, storage={AGE_KEY: "child"})
    assert "tracker-check-needs-source" not in classes(rendered)["Child Chest"]["className"]


# --- Round 22 (tracker-2): open-first rows, area readiness and after-event notes, Darunia's empty bonus, purchases.
def area_with(name, *checks, **extra):
    return {"name": name, "checks": list(checks), **extra}


def pickup(check_id, collected, in_logic=None, **extra):
    """A vanilla row as tracker.logic sends it: read from the inventory and tagged with its usual item."""
    return check(check_id, collected, in_logic) | {"kind": "other", "vanilla": True, "item": "Heart", **extra}


def listing(areas, vanilla=(), **options):
    """The snapshot with these seed ``areas`` and ``vanilla`` areas in place of Field and Lake."""
    snap = snapshot(**options)
    snap["state"]["areas"] = list(areas)
    snap["state"]["vanilla_areas"] = list(vanilla)
    if not options.get("available", True):
        for group in (*snap["state"]["areas"], *snap["state"]["vanilla_areas"]):
            for entry in group["checks"]:
                entry.pop("in_logic", None)
    return snap


AGE_ORDER = ("child", "adult", "either")


def at_age(age, *more):
    return [{"id": "tracker-age", "value": age, "event": "change"}, *more]


def notes_by_area(rendered, kind):
    """Area name -> its heading's ``kind`` ("ready" or "after") note texts, for each area that shows one."""
    return {head["name"]: head[kind] for head in rendered["areaHeads"] if head[kind]}


def ordering():
    return listing(
        [
            area_with(
                "Field",
                check("Got Chest", True),
                check("Adult Chest", False, (False, True, True)),
                check("Mine", None, marked=True),
                check("Child Chest", False, (True, False, True)),
                check("Skipped Chest", False) | {"skipped": True},
                check("Far Chest", False, (False, False, False)),
                check("Odd Row", False),  # no logic data: open, not in logic
                check("Both Gift", None, (True, True, True)),  # the save can't show it: open, in logic
            ),
            area_with("Lake", check("Lake Got", True), check("Lake Chest", False, (True, True, True))),
        ],
        [area_with("Field", pickup("Letter Pickup", False, (True, False, True)))],
    )


@pytest.mark.parametrize(
    ("age", "field_open"),
    [
        ("child", ["Child Chest", "Both Gift", "Letter Pickup", "Adult Chest", "Far Chest", "Odd Row"]),
        ("adult", ["Adult Chest", "Both Gift", "Child Chest", "Far Chest", "Odd Row", "Letter Pickup"]),
        ("either", ["Adult Chest", "Child Chest", "Both Gift", "Letter Pickup", "Far Chest", "Odd Row"]),
    ],
)
def test_each_area_lists_open_in_logic_rows_then_other_open_rows_then_finished_ones(tmp_path, age, field_open):
    """Per area and stable: the seed's order holds within each group, vanilla rows included; areas keep theirs."""
    rendered = tab(tmp_path, ordering(), actions=at_age(age))
    finished = ["Got Chest", "Mine", "Skipped Chest"]
    assert [row["id"] for row in rendered["checks"]] == [*field_open, *finished, "Lake Chest", "Lake Got"]


def test_before_any_save_rows_keep_the_seeds_order(tmp_path):
    rendered = tab(tmp_path, unsaved(ordering()))
    assert [row["id"] for row in rendered["checks"]] == [
        *("Got Chest", "Adult Chest", "Mine", "Child Chest", "Skipped Chest", "Far Chest", "Odd Row", "Both Gift"),
        *("Lake Got", "Lake Chest"),
    ]


def readiness(**options):
    return listing(
        [
            area_with("Forest", check("Kid Chest", False, (True, False, True)), check("Forest Got", True)),
            area_with("Peak", check("Grown Chest", False, (False, True, True)), check("Peak Mark", None, marked=True)),
            area_with("River", check("Trip Chest", False, (False, False, True))),
            area_with("Lake", check("Lake Chest", False, (True, True, True)), check("Lake Far", False, (False,) * 3)),
            area_with("Shrine", check("Shrine Chest", False, (True, True, True)), check("Shrine Odd", False)),
            area_with("Done", check("Done Got", True), check("Done Skip", False) | {"skipped": True}),
        ],
        **options,
    )


@pytest.mark.parametrize(
    ("age", "ready"),
    [("child", ["Forest"]), ("adult", ["Peak"]), ("either", ["Forest", "Peak", "River"]), ("save", ["Peak"])],
)
def test_an_area_whose_every_remaining_check_is_in_logic_for_the_age_says_so(tmp_path, age, ready):
    """Finished rows leave the area; a remaining row out of logic or without logic data, or none remaining (Done),
    keeps the note off."""
    rendered = tab(tmp_path, readiness(save_age="adult"), actions=at_age(age))
    assert notes_by_area(rendered, "ready") == dict.fromkeys(ready, ["All in logic"])


def test_vanilla_rows_count_toward_an_areas_readiness(tmp_path):
    snap = listing(
        [
            area_with("Field", check("Field Got", True)),
            area_with("Lake", check("Lake Chest", False, (True, True, True))),
        ],
        [
            area_with("Field", pickup("Field Pickup", False, (True, False, True))),
            area_with("Lake", pickup("Lake Pickup", False, (False, False, False))),
            area_with("Fountain", pickup("Fountain Pickup", None, (True, True, True))),
        ],
    )
    ready = {age: list(notes_by_area(tab(tmp_path, snap, actions=at_age(age)), "ready")) for age in AGE_ORDER}
    assert ready == {"child": ["Field", "Fountain"], "adult": ["Fountain"], "either": ["Field", "Fountain"]}


def test_readiness_judges_the_whole_area_not_the_rows_a_filter_or_fold_leaves_shown(tmp_path):
    expected = dict.fromkeys(["Forest", "Peak", "River"], ["All in logic"])
    shows = {
        show: tab(tmp_path, readiness(), actions=[{"id": "tracker-show", "value": show, "event": "change"}])
        for show in ("open", "logic")
    }
    assert {show: notes_by_area(rendered, "ready") for show, rendered in shows.items()} == {
        "open": expected,
        "logic": expected,
    }
    shown = {name for name, row in classes(shows["logic"]).items() if row["shown"]}
    assert {"Lake Chest", "Shrine Chest"} <= shown and not {"Lake Far", "Shrine Odd"} & shown
    folded = tab(tmp_path, readiness(), storage={COLLAPSED_KEY: '["Forest"]'})
    assert notes_by_area(folded, "ready") == expected and not classes(folded)["Kid Chest"]["shown"]


GOHMA, GUARD = "Defeat Queen Gohma", "Show Zelda's Letter to the Kakariko guard"


def gated(**options):
    """Areas closed until a saved event; per age, tracker.logic names the undone events that would open a check."""
    return listing(
        [
            area_with(
                "Forest",
                check("Forest Far", False, (False, False, False)),
                check("Forest Got", True),
                after_events={"child": [GOHMA], "adult": [], "either": [GOHMA]},
            ),
            area_with(
                "Kakariko",
                check("Kak Grown", False, (False, True, True)),
                after_events={"child": [GUARD], "adult": [], "either": []},
            ),
            area_with(
                "Lake",
                check("Lake Far", False, (False, False, False)),
                after_events={"child": [GOHMA], "adult": [], "either": [GOHMA]},
            ),
            area_with("Field", check("Field Chest", False, (True, True, True))),
        ],
        [
            area_with(
                "Forest",
                pickup("Forest Pickup", False, (False, False, False)),
                after_events={"child": [GOHMA, GUARD], "adult": [], "either": []},
            ),
            area_with("Lake", pickup("Lake Pickup", False, (True, False, True))),  # in logic: Lake needs no event
            area_with(
                "Market",
                pickup("Market Pickup", False, (False, False, False)),
                after_events={"child": [GUARD], "adult": [], "either": [GUARD]},
            ),
        ],
        **options,
    )


def test_an_area_with_nothing_in_logic_names_the_saved_event_that_would_open_it(tmp_path):
    renders = {age: tab(tmp_path, gated(), actions=at_age(age)) for age in AGE_ORDER}
    after = {age: notes_by_area(rendered, "after") for age, rendered in renders.items()}
    [forest] = after["child"].pop("Forest")  # seed and vanilla rows' events, each named once
    assert forest.startswith("After: ") and forest.count(GOHMA) == 1 and GUARD in forest
    assert after == {
        "child": {"Kakariko": ["After: " + GUARD], "Market": ["After: " + GUARD]},
        "adult": {},
        "either": {"Forest": ["After: " + GOHMA], "Market": ["After: " + GUARD]},
    }
    assert notes_by_area(renders["child"], "ready") == {"Field": ["All in logic"]}  # never both on one area


def test_without_a_save_or_logic_no_area_says_ready_or_after(tmp_path):
    child = {AGE_KEY: "child"}
    shown = tab(tmp_path, gated(), storage=child)
    assert notes_by_area(shown, "ready") and notes_by_area(shown, "after")
    for snap in (unsaved(gated()), gated(available=False, reason="old seed")):
        rendered = tab(tmp_path, snap, storage=child)
        assert (notes_by_area(rendered, "ready"), notes_by_area(rendered, "after")) == ({}, {})


def goron_city(*, empty=True):
    """Goron City with Darunia's vanilla bonus: empty while the save owns the child's Bracelet (as tracker.logic sends
    it), else an open vanilla row in logic for the child."""
    bonus = {"item": "Goron Bracelet", "item_label": "Goron's Bracelet", "kind": "gift"}
    if empty:
        darunia = pickup("GC Darunias Joy", True, basis="empty_bonus", empty=True, **bonus)
    else:
        darunia = pickup("GC Darunias Joy", False, (True, False, True), basis="inventory", **bonus)
    return listing(
        [area_with("Goron City", check("GC Pot", None, (True, True, True)), check("GC Maze", False, (True,) * 3))],
        [area_with("Goron City", darunia, pickup("GC Rock Pickup", False, (True, True, True)))],
    )


def test_darunias_empty_vanilla_bonus_is_its_own_inferred_state_not_a_collected_check(tmp_path):
    child = {AGE_KEY: "child"}
    rendered = tab(tmp_path, goron_city(), storage=child, actions=[{"check": "GC Darunias Joy", "event": "click"}])
    row = classes(rendered)["GC Darunias Joy"]
    assert "tracker-check-empty" in row["className"] and "tracker-check-collected" not in row["className"]
    assert row["disabled"] and rendered["posts"] == [] and rendered["storage"] == child  # no action, nothing kept
    details = rendered["details"]
    assert details["rows"]["State"] == "Empty vanilla bonus" and "Click" not in details["rows"]
    assert "Collected" not in details["body"]
    assert "Inferred" in details["rows"]["Save"] and "not a permanent mark" in details["rows"]["Save"]
    assert details["rows"]["Kind"] == "Gift"
    assert "Empty bonus" in rendered["legend"][0]["text"]
    # Finished: after the open rows, off the remaining count, hidden by Open checks.
    assert [entry["id"] for entry in rendered["checks"]] == ["GC Pot", "GC Maze", "GC Rock Pickup", "GC Darunias Joy"]
    assert rendered["areaHeads"][0]["text"] == "1 / 4 done · 3 in logic"
    assert notes_by_area(rendered, "ready") == {"Goron City": ["All in logic"]}
    show_open = [{"id": "tracker-show", "value": "open", "event": "change"}]
    open_only = tab(tmp_path, goron_city(), storage=child, actions=show_open)
    assert not classes(open_only)["GC Darunias Joy"]["shown"]
    # Reversible: the next snapshot without the Bracelet (here, the answer to a mark) shows the bonus open again.
    unread = tab(
        tmp_path,
        goron_city(),
        after=marked(goron_city(empty=False), "GC Pot"),
        storage=child,
        actions=[{"check": "GC Pot", "event": "click"}],
    )
    assert unread["posts"] == [{"route": "tracker-mark", "body": {"check": "GC Pot", "marked": True}}]
    assert styled(unread, "GC Darunias Joy") == "in"
    assert "tracker-check-empty" not in classes(unread)["GC Darunias Joy"]["className"]
    assert "Empty bonus" not in unread["legend"][0]["text"]


@pytest.mark.parametrize("budget", ["saved rupees", "wallet capacity"])
@pytest.mark.parametrize("rule", ["True", "is_child"])
def test_a_purchase_source_names_the_shop_price_and_budget_and_no_reward(tmp_path, budget, rule):
    snap = snapshot()
    purchase = {"location": "KF Shop Item 7", "shop": "KF Shop", "price": 40, "budget": budget}
    source = {"region": "KF Kokiri Shop", "ages": ["child"], "rule": rule, "purchase": purchase}
    needs = [{"item": "Buy Deku Shield", "sources": [source]}]
    snap["state"]["areas"][0]["checks"][0]["assumed_sources"] = {"child": needs, "adult": [], "either": needs}
    rendered = tab(
        tmp_path, snap, storage={AGE_KEY: "child"}, actions=[{"check": "Child Chest", "event": "pointerover"}]
    )
    row = classes(rendered)["Child Chest"]
    assert "tracker-check-needs-source" in row["className"] and row["text"] == "Child Chest"
    rows = rendered["details"]["rows"]
    words = rows["Needs a source"]
    assert "KF Shop" in words and "40 rupees" in words and budget in words and "Deku Babas" not in words
    assert ", as child" in words and "(True)" not in words
    assert not {"Item", "Usual item"} & set(rows)  # the check's own reward stays hidden
