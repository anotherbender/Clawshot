"""Child song arrivals need an escape held before landing; indoors may use held songs."""

import pytest

from clawshot.generate import FillError, Settings, generate
from clawshot.world import CHILD, Search, build_world, load_spec
from clawshot.world.softlocks import reachable_traps

ARRIVALS = [
    ("Bolero of Fire", "DMC Central Local"),
    ("Requiem of Spirit", "Desert Colossus"),
]
SAFE_SONGS = ["Minuet of Forest", "Serenade of Water", "Nocturne of Shadow", "Prelude of Light"]


@pytest.mark.parametrize("song,landing", ARRIVALS)
@pytest.mark.parametrize("other", [None, "Bolero of Fire", "Requiem of Spirit", "Farores Wind"])
def test_child_arrival_cannot_supply_its_own_escape(song, landing, other):
    spec = load_spec()
    spec["start"] = f"{song} Warp"
    world = build_world(spec)
    items = ["Fairy Ocarina", song, *([other] if other else [])]
    search = Search(world, items)
    spheres = search.collect_spheres(
        {"DMC Child Red Rupee 1": "Minuet of Forest", "Sheik at Colossus": "Minuet of Forest"}
    )
    assert not search.can_reach(landing, CHILD), {"items": items, "spheres": spheres, "child": search.inventory(CHILD)}


@pytest.mark.parametrize("song,landing", ARRIVALS)
@pytest.mark.parametrize("escape", SAFE_SONGS)
def test_child_arrival_accepts_an_already_playable_safe_song(song, landing, escape):
    spec = load_spec()
    spec["settings"]["open_forest"] = "open"
    next(r for r in spec["regions"] if r["name"] == "Root")["exits"] = {f"{song} Warp": "True"}
    world = build_world(spec)
    search = Search(world, ["Fairy Ocarina", escape])
    assert search.can_reach(landing, CHILD)
    assert not [t for t in reachable_traps(search, regions=[landing]) if t.age == CHILD]
    assert not Search(world, [escape]).can_reach(landing, CHILD)


def arrival_fill_spec(song, landing):
    """Two destinations with native arrival rules; no alternate walk into the landing."""
    spec = load_spec()
    dispatch = {r["name"]: r for r in spec["regions"]}
    spec["native_progressive"] = {}
    spec["goal"] = "Test_Goal"
    spec["items"]["Test Goal"] = {"class": "progression"}
    spec["settings"].update(age_return_guarantee=False, softlock_verified_regions=[landing])
    spec["regions"] = [
        {"name": "Root", "exits": {"Root Exits": "age == 'child'"}},
        {
            "name": "Root Exits",
            "exits": {
                "KF Links House": "True",
                f"{song} Warp": dispatch["Root Exits"]["exits"][f"{song} Warp"],
                "Minuet of Forest Warp": dispatch["Root Exits"]["exits"]["Minuet of Forest Warp"],
            },
        },
        {
            "name": "KF Links House",
            "locations": {
                "Instrument": {"type": "NPC", "vanilla": "Fairy Ocarina", "rule": "True"},
                "Arrival Song": {"type": "NPC", "vanilla": song, "rule": "True"},
                "Outside Chest": {"type": "Chest", "vanilla": "Test Goal", "rule": "True"},
            },
        },
        {"name": "Minuet of Forest Warp", "exits": {"KF Links House": "True"}},
        {"name": f"{song} Warp", "exits": {landing: dispatch[f"{song} Warp"]["exits"][landing]}},
        {
            "name": landing,
            "locations": {
                "Landing Chest": {"type": "Chest", "vanilla": "Minuet of Forest", "rule": "True"},
            },
        },
    ]
    spec["locations"] = {}
    spec["shop_price_rules"] = {}
    return spec


@pytest.mark.parametrize("song,landing", ARRIVALS)
def test_fill_places_escape_before_child_warp_only_progression(song, landing):
    spec = arrival_fill_spec(song, landing)
    # Force goal behind arrival. Fill must place the safe song outside, never behind itself.
    spec["regions"][2]["locations"]["Outside Chest"]["excluded_items"] = ["Test Goal"]
    seed = generate(spec, 170031, Settings(forest="open", songs="anywhere"))
    assert seed.placements["Outside Chest"] == "Minuet of Forest"
    assert seed.placements["Landing Chest"] == "Test Goal"
    search = Search(seed.world)
    search.collect_spheres(seed.placements)
    assert search.inventory(CHILD).get("Test Goal") == 1


@pytest.mark.parametrize("song,landing", ARRIVALS)
def test_fill_refuses_escape_song_locked_at_its_own_child_destination(song, landing):
    spec = arrival_fill_spec(song, landing)
    spec["regions"][2]["locations"].pop("Outside Chest")
    spec["goal"] = "Minuet_of_Forest"
    with pytest.raises(FillError):
        generate(spec, 170031, Settings(forest="open", songs="anywhere"))


@pytest.mark.parametrize("room", ["KF Kokiri Shop", "Deku Tree Slingshot Room"])
@pytest.mark.parametrize(
    "instrument,age,safe",
    [("Fairy Ocarina", "child", True), ("Fairy Ocarina", "adult", False), ("Ocarina of Time", "adult", True)],
)
def test_checker_credits_only_age_usable_songs_from_indoors(room, instrument, age, safe):
    spec = load_spec()
    spec["settings"]["open_forest"] = "open"
    next(r for r in spec["regions"] if r["name"] == "Root")["exits"] = {room: "True"}
    next(r for r in spec["regions"] if r["name"] == room)["exits"] = {}
    world = build_world(spec)
    search = Search(world, [instrument, "Prelude of Light"])
    findings = reachable_traps(search, regions=[room])
    actual = [t for t in findings if t.age == age]
    assert (actual == []) == safe, {"room": room, "instrument": instrument, "age": age, "findings": actual}


def test_checker_does_not_credit_an_unheld_song_or_farore_without_a_point():
    spec = load_spec()
    room = "Deku Tree Slingshot Room"
    next(r for r in spec["regions"] if r["name"] == "Root")["exits"] = {room: "True"}
    search = Search(build_world(spec), ["Ocarina of Time", "Farores Wind"])
    assert {(t.age, t.region) for t in reachable_traps(search, regions=[room])} == {
        ("child", room),
        ("adult", room),
    }
