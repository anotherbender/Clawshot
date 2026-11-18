"""No save warp: entering a room must not depend on its own escape-tool reward."""

import pytest

from clawshot.generate import FillError, Settings, from_placements, generate
from clawshot.world import CHILD, Search, build_world, load_spec
from clawshot.world.softlocks import audit, reachable_traps


@pytest.mark.parametrize(
    "rewards",
    [
        ("Slingshot", "Boomerang"),
        ("Map (Deku Tree)", "Compass (Deku Tree)"),
    ],
)
def test_slingshot_room_cannot_supply_its_own_entry_tool(rewards):
    spec = load_spec()
    spec["start"] = "Deku Tree Lobby"
    world = build_world(spec)
    placements = dict(zip(("Deku Tree Slingshot Chest", "Deku Tree Slingshot Room Side Chest"), rewards, strict=True))
    search = Search(world, ["Deku Shield"])
    spheres = search.collect_spheres(placements)
    assert not search.can_reach("Deku Tree Slingshot Room", CHILD), {
        "rewards": placements,
        "spheres": spheres,
        "inventory": search.counts,
    }
    assert spheres == []


@pytest.mark.parametrize("weapon", ["Slingshot", "Boomerang"])
def test_slingshot_room_remains_accessible_with_usable_exit_tool(weapon):
    spec = load_spec()
    spec["start"] = "Deku Tree Lobby"
    world = build_world(spec)
    search = Search(world, ["Deku Shield", weapon])
    assert search.can_reach("Deku Tree Slingshot Room", CHILD)
    assert all(
        search.can_access(world.locations[name], CHILD)
        for name in ("Deku Tree Slingshot Chest", "Deku Tree Slingshot Room Side Chest")
    )


def trap_spec(*, escape="Tool", time_rule=False):
    return {
        "start": "Home",
        "goal": "True",
        "items": {"Tool": {}, "Junk": {"class": "normal"}},
        "settings": {},
        "flags": {"ensure_tod_access": time_rule},
        "regions": [
            {"name": "Home", "exits": {"Pit": "True"}},
            {
                "name": "Pit",
                "exits": {"Home": escape},
                "locations": {"Pit Chest": {"type": "Chest", "vanilla": "Tool", "rule": "True"}},
            },
        ],
    }


def trap_world(**kwargs):
    return build_world(trap_spec(**kwargs))


def test_audit_catches_trap_before_its_own_reward_not_only_after_final_sphere():
    findings = audit(trap_world(), {"Pit Chest": "Tool"})
    assert {(t.sphere, t.age, t.region) for t in findings} == {
        (0, "child", "Pit"),
        (0, "adult", "Pit"),
    }


def test_audit_does_not_assume_future_loot_or_a_save_warp():
    findings = audit(trap_world(), {"Pit Chest": "Junk"})
    assert {(t.sphere, t.age, t.region) for t in findings} == {
        (index, age, "Pit") for index in (0, 1) for age in ("child", "adult")
    }


def test_return_route_retains_arrival_time_instead_of_borrowing_night_exit():
    findings = reachable_traps(Search(trap_world(escape="at_night", time_rule=True)))
    assert {(t.age, t.region, t.time) for t in findings} == {
        ("child", "Pit", "day"),
        ("adult", "Pit", "day"),
    }


def test_adult_escape_tool_does_not_rescue_independent_child_prefix():
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {"Tool": {}},
            "helpers": {"is_child": "age == 'child'", "is_adult": "age == 'adult'"},
            "settings": {
                "age_return_event": "Return Open",
                "age_return_region": "Home",
                "age_pull_event": "Time Travel",
                "softlock_anchors": {"child": "Home", "adult": "Home"},
                "softlock_virtual_regions": ["Root"],
            },
            "regions": [
                {"name": "Root", "exits": {"Home": "True"}},
                {
                    "name": "Home",
                    "events": {"Time Travel": "is_child", "Return Open": "False"},
                    "exits": {"Pit": "is_child"},
                    "locations": {"Adult Tool": {"rule": "is_adult", "type": "Chest", "vanilla": "Tool"}},
                },
                {"name": "Pit", "exits": {"Home": "Tool"}},
            ],
        }
    )
    search = Search(world)
    search.collect_spheres({"Adult Tool": "Tool"})
    assert search.inventory("adult").get("Tool") == 1
    assert not search.inventory("child").get("Tool")
    assert {(t.age, t.region) for t in reachable_traps(search)} == {("child", "Pit")}


@pytest.mark.parametrize("external", [False, True])
def test_generation_refuses_a_reachable_trap_even_when_the_goal_is_already_met(external):
    spec = trap_spec()
    spec["settings"]["softlock_anchors"] = {"child": "Home", "adult": "Home"}
    with pytest.raises(FillError, match="reachable softlock after sphere 0: child: Pit"):
        if external:
            from_placements(spec, 0, Settings(), {"Pit Chest": "Tool"})
        else:
            generate(spec, 0, Settings())


def test_unverified_missing_returns_stay_visible_as_diagnostics():
    spec = trap_spec()
    spec["settings"].update(
        softlock_anchors={"child": "Home", "adult": "Home"},
        softlock_verified_regions=["Home"],
    )
    seed = generate(spec, 0, Settings())
    findings = audit(seed.world, seed.placements)
    assert {(t.sphere, t.age, t.region) for t in findings} == {
        (0, "child", "Pit"),
        (0, "adult", "Pit"),
    }
    assert audit(seed.world, seed.placements, regions=("Home",)) == []


def test_waiting_where_time_passes_is_a_real_return_path():
    spec = trap_spec(escape="at_night", time_rule=True)
    spec["regions"][1]["time_passes"] = True
    assert reachable_traps(Search(build_world(spec))) == []


def test_any_physical_anchor_for_the_current_age_is_sufficient():
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "settings": {
                "softlock_anchors": {"child": ["House", "Forest"], "adult": ["Temple"]},
                "softlock_virtual_regions": ["Root"],
            },
            "regions": [
                {"name": "Root", "exits": {"Forest": "age == 'child'"}},
                {"name": "Forest", "exits": {"Pit": "True"}},
                {"name": "Pit", "exits": {"Forest": "True"}},
                {"name": "House"},
                {"name": "Temple"},
            ],
        }
    )
    assert reachable_traps(Search(world)) == []


# Gift is an overlay-setup alias, not a world location type. Its actual presets
# are exercised through native gift preparation in test_softlocks_dump.py.
PRESETS = {
    "Defaults": Settings(),
    "keys anywhere": Settings(dungeon_items="anywhere"),
    "Shop": Settings(shuffle=("Chest", "Shop")),
    "Token on": Settings(shuffle=("Chest", "Token")),
    "open Forest": Settings(forest="open"),
    "free time travel": Settings(logic={"free_time_travel": True}),
}


@pytest.mark.parametrize("preset", PRESETS)
@pytest.mark.parametrize("number", [0, 7, 42])
def test_fixed_real_world_seeds_have_no_evidenced_reachable_traps(preset, number):
    # Keep the evidenced scope explicit so a production-scope regression cannot hide a known trap.
    # Ordinary missing returns still remain diagnostic.
    seed = generate(load_spec(), number, PRESETS[preset])
    assert (
        audit(
            seed.world,
            seed.placements,
            regions=(
                "Deku Tree Slingshot Room",
                "Graveyard Dampes Grave",
                "Wasteland Near Colossus",
                "Desert Colossus",
            ),
        )
        == []
    ), (preset, number)
