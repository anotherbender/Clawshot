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
    point = [{"class": "tracker-check", "index": 0, "event": "pointerover"}]
    rendered = tab(tmp_path, snapshot(unknown_items=["hookshot", "Forest Temple small keys"]), actions=point)
    assert not [note for note in rendered["notes"] if "conservative" in note]
    body = rendered["details"]["body"]
    assert "May be conservative" in body and "Hookshot" in body and "Forest Temple small keys" in body
    assert "conservative" not in tab(tmp_path, actions=point)["details"]["body"]


# 11.6 (4.1, 4.2, 4.8); round 21: the row itself is the toggle, no Mark done button.
def test_clicking_a_check_the_save_cannot_read_marks_it(tmp_path):
    rendered = tab(tmp_path, actions=[{"class": "tracker-check", "index": 1, "event": "click"}])
    actionable = {name for name, entry in classes(rendered).items() if not entry["disabled"]}
    assert actionable == {"Adult Chest", "Shop Item"}  # only checks the save cannot read
    assert rendered["posts"] == [{"route": "tracker-mark", "body": {"check": "Adult Chest", "marked": True}}]
    unmark = tab(tmp_path, actions=[{"class": "tracker-check", "index": 3, "event": "click"}])
    assert unmark["posts"] == [{"route": "tracker-mark", "body": {"check": "Shop Item", "marked": False}}]
    for collected in (0, 2, 4):  # read by the save (not collected, collected): clicking only selects
        assert tab(tmp_path, actions=[{"class": "tracker-check", "index": collected, "event": "click"}])["posts"] == []


def test_a_markable_not_collected_check_has_the_toggle_and_keeps_in_logic_styling(tmp_path):
    """tracker-auto-checks 3.2: a provisional track read of "not collected" stays open with Mark done; marked, it
    shows as marked done like a marked unknown check. Round 21: the row itself is the toggle."""
    snap = snapshot()
    lake = snap["state"]["areas"][1]["checks"]
    lake.append(check("Maybe Gift", False, (True, True, True), markable=True))
    lake.append(check("Kept Gift", False, markable=True, marked=True))
    rows = [entry["id"] for entry in tab(tmp_path, snap)["checks"]]
    rendered = tab(
        tmp_path, snap, actions=[{"class": "tracker-check", "index": rows.index("Maybe Gift"), "event": "click"}]
    )
    found = classes(rendered)
    assert not found["Maybe Gift"]["disabled"] and styled(rendered, "Maybe Gift") == "in"
    assert not found["Kept Gift"]["disabled"] and styled(rendered, "Kept Gift") == "marked"
    assert found["Far Chest"]["disabled"]  # not collected without markable: no toggle
    assert rendered["posts"] == [{"route": "tracker-mark", "body": {"check": "Maybe Gift", "marked": True}}]
    unmark = tab(
        tmp_path, snap, actions=[{"class": "tracker-check", "index": rows.index("Kept Gift"), "event": "click"}]
    )
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
            {"class": "tracker-check", "index": 1, "event": "click"},  # Adult Chest, marked by mistake
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
            {"class": "tracker-check", "index": 1, "event": "click"},
        ],
    )
    assert classes(undo)["Adult Chest"]["shown"] and styled(undo, "Adult Chest") == "marked"
    assert undo["posts"] == [{"route": "tracker-mark", "body": {"check": "Adult Chest", "marked": False}}]
    assert undo["storage"] == {}


def test_a_check_the_save_reads_can_be_skipped_when_the_backend_offers_it(tmp_path):
    snap = snapshot()
    snap["state"]["areas"][0]["checks"][0]["skippable"] = True  # Child Chest: read by the save, not collected
    rendered = tab(tmp_path, snap, actions=[{"class": "tracker-check", "index": 0, "event": "click"}])
    assert rendered["posts"] == [
        {"route": "tracker-mark", "body": {"check": "Child Chest", "marked": True, "kind": "skip"}}
    ]
    assert "Skipped" in rendered["legend"][0]["text"]
    skipped = marked(snapshot(), "Child Chest", "skipped")
    undo = tab(tmp_path, skipped, actions=[{"class": "tracker-check", "index": 0, "event": "click"}])
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


def waiting(**options):
    snap = snapshot(**options)
    snap["status"] = "waiting"
    snap["selected_slot"] = None
    snap["warnings"] = ["No save in this folder yet: save in the game to start tracking."]
    return snap


def test_before_any_save_the_tabs_say_so_instead_of_unknown_rows(tmp_path):
    rendered = tab(
        tmp_path,
        waiting(unknown_items=["hookshot"]),
        actions=[{"class": "tracker-check", "index": 1, "event": "click"}],
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
    rendered = tab(tmp_path, snap, actions=[{"class": "tracker-check", "index": 1, "event": "pointerover"}])
    details = rendered["details"]
    assert (details["title"], details["text"]) == ("Adult Chest", "Field, behind the big tree")
    assert "In logic as adult; child can't reach it yet" in details["body"]
    assert "May be conservative" in details["body"]
    assert "Your save can't show this check (shop slots restock and keep no sold record)" in details["body"]
    assert "Area" in details["body"] and "Field" in details["body"] and "marks it done" in details["body"]
    assert rendered["posts"] == []  # pointing only selects
    done = tab(tmp_path, snap, actions=[{"class": "tracker-check", "index": 2, "event": "pointerover"}])["details"]
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
    rendered = tab(tmp_path, snap, actions=[{"class": "tracker-check", "index": 0, "event": "pointerover"}])
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
        {"class": "tracker-check", "index": 0, "event": "pointerover"},
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
