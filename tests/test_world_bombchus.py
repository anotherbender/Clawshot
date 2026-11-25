"""D30 as corrected 2026-11-24: Bombchus need the Bomb Bag, whatever ``free_bombchu_drops`` says.

Kareem, Longshot 3.2.0, a Clawshot 0.2.6 seed: Bombchus bought before the bag showed 0 and could not be used, also
with the Goron's Bracelet; the bought amount appeared with the bag. The setting still picks the supply (on: a found
Bombchus item, and only then are Bombchus explosives; off: a purchase, with ``found_bombchus`` the bag alone).
"""

from functools import cache

import pytest

from clawshot.world import ADULT, CHILD, Search, build_world, load_spec

HELPERS = ("has_bombchus", "found_bombchus", "can_refill_bombchus", "has_explosives", "has_both_explosives")
PACK = "Bombchus (5)"
BOUGHT = "Buy Bombchu (10)"
# Enough of every item for any count a rule reads (100 tokens, key counts), so only the Bomb Bag is missing.
COPIES = 100


def check(helper):
    return f"{helper} check"


def helper_world(free_drops):
    # Synthetic room over the shipped helpers (remake overrides and shops.toml applied), one check per helper.
    spec = load_spec()
    spec.update(
        start="Room",
        goal="True",
        regions=[{"name": "Room", "locations": {check(name): name for name in HELPERS}}],
        locations={check(name): {"type": "Chest"} for name in HELPERS},
    )
    spec["settings"] = {**spec["settings"], "free_bombchu_drops": free_drops}
    return build_world(spec)


def opened(world, items, age):
    return {name.removesuffix(" check") for name in Search(world, items).locations(age)}


def chu_sources(world):
    return sorted(
        name for name in world.items if name.startswith(("Bombchus", "Buy Bombchu")) or name == "Bombchu Drop"
    )


def bag_or_bombs(name, item):
    return (
        "Bomb Bag" in name
        or (item.alias is not None and item.alias[0] == "Bomb Bag")
        or name.startswith(("Bombs (", "Buy Bombs ("))
    )


@cache
def real_world(free_drops):
    spec = load_spec()
    spec["settings"] = {**spec["settings"], "free_bombchu_drops": free_drops}
    world = build_world(spec)
    chus = chu_sources(world)
    # Every other item, the D25 counterfactual: no Bomb Bag, no bomb or Bombchus source.
    base = tuple(
        name
        for name, item in world.items.items()
        if not bag_or_bombs(name, item) and name not in chus
        for _ in range(COPIES)
    )
    return world, base, chus


def reach(search, age):
    return set(search.locations(age)), set(search.regions(age))


@pytest.mark.parametrize("free_drops", [True, False])
@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_no_bombchus_helper_holds_without_the_bag(free_drops, age):
    world = helper_world(free_drops)
    sources = chu_sources(world)
    assert {PACK, BOUGHT, "Bombchus", "Bombchu Drop"} <= set(sources)
    # Kareem's case: Bombchus found and bought, the Bracelet held, no bag.
    assert opened(world, [*sources, "Goron Bracelet"], age) == set()


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_free_drops_supply_is_a_found_item_with_the_bag(age):
    world = helper_world(True)
    assert opened(world, ["Bomb Bag"], age) == set()
    # Buying is not the supply in this mode; the purchase helper itself still needs the bag.
    assert opened(world, ["Bomb Bag", BOUGHT], age) == {"can_refill_bombchus"}
    # Bombchus need no lift strength: explosives with the bag alone.
    found = {"has_bombchus", "found_bombchus", "has_explosives"}
    assert opened(world, ["Bomb Bag", PACK], age) == found
    assert opened(world, ["Bomb Bag", PACK, "Goron Bracelet"], age) == found | {"has_both_explosives"}


@pytest.mark.parametrize("age", [CHILD, ADULT])
def test_without_free_drops_the_supply_is_a_purchase_and_never_explosives(age):
    world = helper_world(False)
    assert opened(world, ["Bomb Bag"], age) == {"found_bombchus"}
    assert opened(world, ["Bomb Bag", PACK], age) == {"found_bombchus"}
    bought = {"found_bombchus", "can_refill_bombchus", "has_bombchus"}
    assert opened(world, ["Bomb Bag", BOUGHT], age) == bought
    # has_explosives here is only the bombs (bag and Bracelet); Bombchus never count.
    assert opened(world, ["Bomb Bag", BOUGHT, "Goron Bracelet"], age) == bought | {"has_explosives"}


@pytest.mark.parametrize("free_drops", [True, False])
def test_bombchus_without_the_bag_open_nothing_in_the_world(free_drops):
    world, base, chus = real_world(free_drops)
    without = Search(world, base)
    with_chus = Search(world, [*base, *chus])
    for age in (CHILD, ADULT):
        assert reach(with_chus, age) == reach(without, age), age
    # The control: with the rest held, the bag (and so bombs) still opens child checks.
    bag = Search(world, [*base, "Bomb Bag"])
    assert set(bag.locations(CHILD)) > set(without.locations(CHILD))


def test_vanilla_bombchus_packs_reached_without_the_bag_open_nothing():
    # The generator's path: unshuffled checks keep their vanilla item (generate.fill.fill) and the search collects
    # them, while D25 screens only shuffled packs. The Wasteland Bombchu Salesman keeps its Bombchus in every seed
    # (keep_vanilla), the 40-token reward unless gifts are shuffled; neither rule needs the bag.
    world, base, _ = real_world(True)
    fixed = {"Wasteland Bombchu Salesman": "Bombchus (10)", "Kak 40 Gold Skulltula Reward": "Bombchus (20)"}
    plain = Search(world, base)
    search = Search(world, base)
    search.collect_spheres(fixed)
    assert search.collected == set(fixed)
    for age in (CHILD, ADULT):
        assert reach(search, age) == reach(plain, age), age


@pytest.mark.parametrize(
    ("location", "tools"),
    [
        ("Spirit Temple Child Climb North Chest", ["Bow"]),
        ("Spirit Temple Map Chest", ["Dins Fire"]),
        ("Spirit Temple GS Lobby", []),
        ("Spirit Temple Sun Block Room Chest", []),
        ("Spirit Temple Sun Block Room Silver Rupee Left", []),
        ("Spirit Temple GS Hall After Sun Block Room", ["Boomerang", "Hookshot"]),
    ],
)
def test_spirit_two_key_local_pack_needs_its_bag_without_gating_the_three_key_route(location, tools):
    world = build_world(load_spec())
    keys = ["Small Key (Spirit Temple)"] * 2
    rule = world.locations[location].rule
    before = Search(world, [*keys, *tools]).inventory(ADULT)
    bag = Search(world, [*keys, *tools, "Bomb Bag"]).inventory(ADULT)
    third_key = Search(world, [*keys, *tools, "Small Key (Spirit Temple)"]).inventory(ADULT)
    assert not rule(before, ADULT, 1), location
    assert rule(bag, ADULT, 1), location
    assert rule(third_key, ADULT, 1), location
