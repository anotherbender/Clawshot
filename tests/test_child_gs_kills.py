"""Child Gold Skulltulas that pop out of a tree or crate, or wait on Kakariko's walls, must be killed
(Kareem, 2026-11-22; plans/rounds/r21-sticks.md)."""

import pytest

from clawshot.world import CHILD, Search, build_world, load_spec


@pytest.mark.parametrize(
    ("token", "region"),
    [
        ("LLR GS Tree", "Lon Lon Ranch"),
        ("Market GS Guard House", "Market Guard House"),
        ("ZF GS Tree", "Zoras Fountain"),
        ("Kak GS House Under Construction", "Kakariko Village"),
        ("Kak GS Skulltula House", "Kakariko Village"),
        ("Kak GS Near Gate Guard", "Kakariko Village"),
        ("Kak GS Tree", "Kakariko Village"),
    ],
)
def test_a_child_token_needs_a_kill(token, region):
    spec = load_spec()
    spec["settings"]["starting_age"] = CHILD
    spec["settings"]["gold_skulls_ignore_daytime"] = True  # night is not what this tests
    spec["start"] = "GS Audit Start"
    spec["regions"].append({"name": "GS Audit Start", "exits": {region: "is_starting_age"}})
    world = build_world(spec)
    search = Search(world)
    assert search.can_reach(region, CHILD)
    assert not search.can_access(world.locations[token], CHILD)
    search.collect("Slingshot")
    assert search.can_access(world.locations[token], CHILD)
