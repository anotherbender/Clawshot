"""Derived supply annotations use counterfactual searches, not extra inventory or placed rewards."""

from test_tracker_logic_inventory import seed
from test_tracker_state import parse

from clawshot.generate import Settings
from clawshot.tracker.logic import LogicWorld, SeedLogic
from clawshot.world import Search, build_world


def source_world():
    return build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {
                "Kokiri Sword": {},
                "Boomerang": {},
                "Buy Deku Stick (1)": {"type": "Shop"},
                "Deku Stick Drop": {"type": "Drop"},
                "Deku Nut Drop": {"type": "Drop"},
                "Story Open": {"type": "Event"},
            },
            "helpers": {
                "Sticks": "Buy_Deku_Stick_1 or Deku_Stick_Drop",
                "Nuts": "Deku_Nut_Drop",
            },
            "regions": [
                {
                    "name": "Root",
                    "events": {
                        "Deku Stick Drop": "age == 'child' and Kokiri_Sword",
                        "Deku Nut Drop": "age == 'adult' and Boomerang",
                        "Story Open": "True",
                    },
                    "exits": {"Far": "Sticks", "Other Grove": "True"},
                    "locations": {
                        "Sticks": {"type": "Chest", "rule": "Sticks"},
                        "Either supply": {"type": "Chest", "rule": "Sticks or Nuts"},
                        "Both supplies": {"type": "Chest", "rule": "Sticks and Nuts"},
                        "Child nut check": {"type": "Chest", "rule": "age == 'child' and Nuts"},
                        "Story check": {"type": "Chest", "rule": "Story_Open"},
                    },
                },
                {
                    "name": "Far",
                    "locations": {"Past stick gate": {"type": "Chest", "rule": "True"}},
                },
                {"name": "Other Grove", "events": {"Deku Stick Drop": "age == 'child' and Kokiri_Sword"}},
            ],
        }
    )


def annotate(logic, ints=None, **finished):
    entries = [{"id": name, "collected": finished.get(name, False)} for name in logic.loaded.world.locations]
    state = {"areas": [{"checks": entries}]}
    logic.annotate(state, seed(), parse({}, ints or {}))
    return {entry["id"]: entry for entry in entries}


def tracker(world):
    return SeedLogic(LogicWorld(True, None, Settings(), world))


def stock(actor):
    return {f"PouchData.{actor}.StockNum": 1}


def test_derived_supply_names_reachable_regions_and_the_source_age_without_changing_logic():
    world = source_world()
    logic = tracker(world)
    rows = annotate(logic, stock("Item_Boomerang"))
    expected = Search(world, ["Boomerang"])
    for name, row in rows.items():
        assert row["in_logic"] == {
            age: expected.can_access(world.locations[name], None if age == "either" else age)
            for age in ("child", "adult", "either")
        }
    [resource] = rows["Child nut check"]["assumed_sources"]["child"]
    assert resource == {
        "item": "Deku Nut Drop",
        "sources": [{"region": "Root", "ages": ["adult"], "rule": "age == 'adult' and Boomerang"}],
    }
    assert "assumed_sources" not in rows["Story check"]
    assert "assumed_sources" not in rows["Sticks"]  # inaccessible, not an assumed shopping route
    assert "Buy Deku Stick (1)" not in expected.inventory("child")


def test_supply_beyond_an_exit_is_explained_and_all_reachable_sources_are_named():
    rows = annotate(tracker(source_world()), stock("Weapon_Sword_Kokiri"))
    [resource] = rows["Past stick gate"]["assumed_sources"]["child"]
    assert resource["item"] == "Deku Stick Drop"
    assert [(source["region"], source["ages"]) for source in resource["sources"]] == [
        ("Root", ["child"]),
        ("Other Grove", ["child"]),
    ]


def test_alternatives_show_one_sufficient_route_while_conjunctions_keep_both_resources():
    rows = annotate(tracker(source_world()), stock("Weapon_Sword_Kokiri") | stock("Item_Boomerang"))
    either = rows["Either supply"]["assumed_sources"]["child"]
    both = rows["Both supplies"]["assumed_sources"]["child"]
    assert [entry["item"] for entry in either] == ["Deku Nut Drop"]
    assert {entry["item"] for entry in both} == {"Deku Stick Drop", "Deku Nut Drop"}


def test_held_stock_needs_no_source_and_a_new_save_invalidates_the_explanation():
    logic = tracker(source_world())
    sword = stock("Weapon_Sword_Kokiri")
    assert "assumed_sources" in annotate(logic, sword)["Past stick gate"]
    held = annotate(logic, sword | stock("Item_DekuStick"))
    assert held["Past stick gate"]["in_logic"]["child"]
    assert "assumed_sources" not in held["Past stick gate"]
    assert "assumed_sources" not in held["Sticks"]
    assert "assumed_sources" not in annotate(logic, sword, Sticks=True)["Sticks"]
