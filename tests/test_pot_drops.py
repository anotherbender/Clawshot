"""Pots never supply Deku Sticks or Nuts in logic (Kareem, 2026-11-22; plans/rounds/r21-sticks.md)."""

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec

# A child who walks to Goron City and Zora's Domain with no weapon: forest open, no sword, sticks, Slingshot,
# Boomerang, bombs or magic.
WEAPONLESS = ["Fairy Ocarina", "Zeldas Lullaby", "Sarias Song", "Progressive Scale", "Goron Bracelet", "Zeldas Letter"]


def test_a_weaponless_child_at_the_stick_pots_cannot_attack():
    spec = load_spec()
    spec["settings"]["open_forest"] = "open"
    world = build_world(spec)
    search = Search(world, WEAPONLESS)
    assert search.can_reach("Goron City", CHILD) and search.can_reach("Zoras Domain", CHILD)
    lone_tree = world.locations["HF GS Lone Tree"]  # a child token behind can_child_attack
    assert not search.holds("Deku Stick Drop")
    assert not search.holds("Deku Nut Drop")
    assert not search.can_access(lone_tree, CHILD)
    search.collect("Kokiri Sword")  # the Deku Babas a weapon kills still drop both
    assert search.holds("Deku Stick Drop") and search.holds("Deku Nut Drop")
    assert search.can_access(lone_tree, CHILD)


@pytest.mark.parametrize(
    ("region", "age"),
    [
        ("Goron City", CHILD),
        ("Zoras Domain", CHILD),
        ("Bottom of the Well Main Area", CHILD),
        ("Jabu Jabus Belly Past Big Octo", CHILD),
        ("Child Spirit Before Locked Door", CHILD),
        ("Graveyard Dampes Grave", ADULT),
        ("Haunted Wasteland", ADULT),
        ("Shadow Temple Beginning", ADULT),
        ("Ganons Castle Spirit Trial Ending", ADULT),
    ],
)
def test_no_pot_region_supplies_sticks_or_nuts(region, age):
    spec = load_spec()
    spec["settings"]["starting_age"] = age
    spec["start"] = "Pot Audit Start"
    spec["regions"].append({"name": "Pot Audit Start", "exits": {region: "is_starting_age"}})
    search = Search(build_world(spec))
    assert search.can_reach(region, age)
    assert not search.holds("Deku Stick Drop")
    assert not search.holds("Deku Nut Drop")
