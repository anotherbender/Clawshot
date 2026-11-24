"""Seeds from placements chosen elsewhere (another placer's fill, such as an Archipelago multiworld's). Synthetic
worlds from test_generate and test_world_tiers, and the repository's own logic data for the spoiler's opening route."""

import re

import pytest
from test_generate import chest, dungeon_world
from test_world_tiers import BYPASS, strength_spec

from clawshot.generate import FillError, Settings, from_placements, generate, prepare, spoiler, tokens
from clawshot.generate.fill import shuffled_locations
from clawshot.generate.tokens import SOURCE_TYPE
from clawshot.world import build_world
from clawshot.world.load import load_spec

STAND_IN = "Stand-in"
"""An item a placer puts where it has no item of this world's to give (another player's, in a multiworld)."""


def _world_spec():
    spec = dungeon_world()
    spec["items"] = {**spec["items"], STAND_IN: {"class": "normal"}}
    return spec


def test_given_placements_fill_the_shuffled_locations_and_keep_the_rest_vanilla():
    spec = _world_spec()
    settings = Settings(shuffle=("Chest",), dungeon_items="anywhere")
    reference = generate(spec, 7, settings)
    placements = dict.fromkeys(reference.shuffled, STAND_IN)
    out = from_placements(spec, 7, settings, placements)
    assert out.shuffled == reference.shuffled
    assert all(out.placements[name] == STAND_IN for name in out.shuffled)
    assert {name: item for name, item in out.placements.items() if name not in out.shuffled} == {
        name: item for name, item in reference.placements.items() if name not in reference.shuffled
    }
    assert out.spheres == [] and out.hints == ()


def test_placements_that_do_not_fit_the_world_are_refused_by_name():
    spec = _world_spec()
    settings = Settings(shuffle=("Chest",))  # own_dungeon: the Temple's key may not leave the Temple
    world = build_world(spec)
    shuffled = shuffled_locations(world, settings)
    placements = dict.fromkeys(shuffled, STAND_IN)
    placements["Village Chest"] = "Small Key (Temple)"
    placements["Nowhere"] = "Sword"
    other = next(name for name in shuffled[:-1] if name != "Village Chest")
    placements[other] = "No Such Item"
    del placements[shuffled[-1]]
    with pytest.raises(FillError) as error:
        from_placements(spec, 1, settings, placements)
    text = str(error.value)
    assert "not a shuffled location: Nowhere" in text
    assert f"no item given for {shuffled[-1]}" in text
    assert "Village Chest: may not hold 'Small Key (Temple)'" in text
    assert f"{other}: unknown item 'No Such Item'" in text


def test_a_seed_from_given_placements_has_no_opening_route_instead_of_failing_the_spoiler():
    """The real world has the child opening milestone; with no spheres there is no witness to replay, and the
    spoiler's opening_route is null (as its contract allows) rather than "no child opening witness"."""
    spec = load_spec()
    settings = Settings(shuffle=("Chest",))
    world = build_world(spec)
    placements = {name: world.locations[name].vanilla for name in shuffled_locations(world, settings)}
    # D25: a native bomb pack goes only where the Bomb Bag is guaranteed, which not every vanilla chest is.
    placements = {
        name: "Rupees (5)" if item.startswith(("Bombs (", "Bombchus (")) else item for name, item in placements.items()
    }
    # Round 22: Dampe's first-race chest never opens, so it takes no progression; its vanilla Hookshot swaps with a
    # vanilla junk chest instead.
    dampe, junk = "Graveyard Dampe Race Hookshot Chest", "KF Midos Top Left Chest"
    placements[dampe], placements[junk] = placements[junk], placements[dampe]
    out = from_placements(spec, 1, settings, placements)
    assert all(out.placements[name] == item for name, item in placements.items())
    assert spoiler(out)["opening_route"] is None


def test_external_copies_remain_chest_only_and_native_quest_rewards_stay_at_their_source():
    spec = load_spec()
    settings = Settings(shuffle=("Chest", "NPC"))
    settings, world = prepare(spec, settings)
    placements = dict.fromkeys(shuffled_locations(world, settings), "Rupees (5)")
    chest = next(name for name in placements if world.locations[name].type == "Chest")
    gift = next(name for name in placements if world.locations[name].type == "NPC")
    placements[chest] = "Progressive Hookshot"
    out = from_placements(spec, 1, settings, placements)
    assert out.placements[chest] == "Progressive Hookshot"
    assert out.world.progressive_copies_only
    placements[gift] = placements.pop(chest)
    placements[chest] = "Rupees (5)"
    with pytest.raises(FillError, match="may not hold 'Progressive Hookshot'"):
        from_placements(spec, 1, settings, placements)
    chest_settings = Settings()
    _, chest_world = prepare(spec, chest_settings)
    chest_placements = dict.fromkeys(shuffled_locations(chest_world, chest_settings), "Rupees (5)")
    chest_only = from_placements(spec, 1, chest_settings, chest_placements)
    assert chest_only.placements["GC Darunias Joy"] == "Goron Bracelet"


def test_a_higher_tier_supplied_before_its_lower_tier_is_refused():
    """The fill's tier screen (``fill.with_screens``) is set before a supplied assignment is checked."""
    spec = strength_spec()
    settings = Settings(shuffle=("Chest",))
    with pytest.raises(FillError, match="Open A: may not hold 'Golden Gauntlets'"):
        from_placements(spec, 1, settings, BYPASS)
    safe = {**BYPASS, "Open A": "Silver Gauntlets", "Boulder Chest": "Golden Gauntlets"}
    assert from_placements(spec, 1, settings, safe).placements["Boulder Chest"] == "Golden Gauntlets"


def test_a_lower_tier_in_another_world_still_has_to_come_first():
    """This world's own Silver Gauntlets may arrive from another game at any time, so the Golden ones must still wait
    behind them; behind them they are accepted without a local route to either."""
    spec = strength_spec()
    settings = Settings(shuffle=("Chest",))
    remote = {**BYPASS, "Boulder Chest": "Rupees (5)"}  # the Silver Gauntlets are placed in another game's world
    with pytest.raises(FillError, match="Open A: may not hold 'Golden Gauntlets'"):
        from_placements(spec, 1, settings, remote)
    behind = {**remote, "Open A": "Rupees (5)", "Boulder Chest": "Golden Gauntlets"}
    out = from_placements(spec, 1, settings, behind)
    assert out.placements["Boulder Chest"] == "Golden Gauntlets"
    assert "Silver Gauntlets" not in out.placements.values()


def bomb_spec() -> dict:
    """A Bomb Bag, an unrelated Hammer bypass and a chest only the bag opens."""
    return {
        "start": "Start",
        "goal": "Bomb_Bag",
        "items": {"Bomb Bag": {}, "Hammer": {}, "Bombs (5)": {"class": "normal"}, "Rupee": {"class": "normal"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Bag": chest("Bomb Bag"),
                    "Hammer": chest("Hammer"),
                    "Bypass": chest("Rupee", "Bomb_Bag or Hammer"),
                    "Bag Required": chest("Bombs (5)", "Bomb_Bag"),
                },
            }
        ],
    }


def test_a_supplied_bomb_pack_needs_a_guaranteed_bag_even_when_the_bag_is_remote():
    """D25 at every supplied location, with the fill's own counterfactual: a pack never counts as a bag, and a bag
    in another game's world never makes a bag-free source safe. No local beatability is asked for."""
    spec = bomb_spec()
    settings = Settings()
    bypass = {"Bag": "Bomb Bag", "Hammer": "Hammer", "Bypass": "Bombs (5)", "Bag Required": "Rupee"}
    with pytest.raises(FillError, match=r"Bypass: may not hold 'Bombs \(5\)'"):
        from_placements(spec, 1, settings, bypass)
    behind = {**bypass, "Bypass": "Rupee", "Bag Required": "Bombs (5)"}
    assert from_placements(spec, 1, settings, behind).placements["Bag Required"] == "Bombs (5)"
    remote = {**behind, "Bag": "Rupee"}  # the Bomb Bag is placed in another game's world
    out = from_placements(spec, 1, settings, remote)
    assert out.placements["Bag Required"] == "Bombs (5)" and "Bomb Bag" not in out.placements.values()
    with pytest.raises(FillError, match=r"Bypass: may not hold 'Bombs \(5\)'"):
        from_placements(spec, 1, settings, {**remote, "Bypass": "Bombs (5)", "Bag Required": "Rupee"})


def test_a_bomb_pack_supplied_at_a_chest_open_from_the_start_is_refused():
    spec = load_spec()
    settings = Settings()
    _, world = prepare(spec, settings)
    placements = dict.fromkeys(shuffled_locations(world, settings), "Rupees (5)")
    placements["KF Midos Top Left Chest"] = "Bombs (5)"
    with pytest.raises(FillError, match=r"KF Midos Top Left Chest: may not hold 'Bombs \(5\)'"):
        from_placements(spec, 1, settings, placements)


def skulltula_spec(ammo: str, container: str, starting: tuple[str, ...] = ()) -> dict:
    """A container, an unrelated Hammer bypass and two Gold Skulltulas, one only the container opens; the native
    containers a new game ``starting`` with (``token_starting_containers``), none unless given."""
    gate = f"'{container}'"
    return {
        "start": "Start",
        "goal": gate,
        "settings": {"token_starting_containers": list(starting)},
        "items": {container: {}, "Hammer": {}, ammo: {}, "Rupees (5)": {"class": "normal"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Container Chest": chest(container),
                    "Hammer Chest": chest("Hammer"),
                    "Bypass GS": {"rule": f"{gate} or Hammer", "type": SOURCE_TYPE, "vanilla": "Rupees (5)"},
                    "Container GS": {"rule": gate, "type": SOURCE_TYPE, "vanilla": ammo},
                },
            }
        ],
    }


@pytest.mark.parametrize(
    ("ammo", "container"),
    [
        ("Arrows (5)", "Bow"),
        ("Arrows (10)", "Quiver (40)"),
        ("Bombs (5)", "Bomb Bag"),
        ("Bombchus (5)", "Bomb Bag"),
        ("Deku Nuts (5)", "Deku Nut Capacity"),
        ("Deku Stick (1)", "Deku Stick Capacity"),
    ],
)
def test_supplied_skulltula_ammo_needs_its_container_here_or_in_another_world(ammo, container):
    """Every admitted ammo pickup, Bombchus included, under the container screen (D25 for bomb packs): a Skulltula
    only its container opens takes it, the container placed here or in another game's world; the Hammer bypass is
    refused either way, since a remote container is not a guarantee."""
    spec = skulltula_spec(ammo, container)
    settings = Settings(shuffle=("Chest", tokens.SHUFFLE))
    behind = {"Container Chest": container, "Hammer Chest": "Hammer", "Bypass GS": "Rupees (5)", "Container GS": ammo}
    assert from_placements(spec, 1, settings, behind).placements["Container GS"] == ammo
    remote_container = {**behind, "Container Chest": "Rupees (5)"}  # placed in another game's world
    assert from_placements(spec, 1, settings, remote_container).placements["Container GS"] == ammo
    for container_placement in (behind, remote_container):
        bypass = {**container_placement, "Bypass GS": ammo, "Container GS": "Rupees (5)"}
        with pytest.raises(FillError, match=re.escape(f"Bypass GS: may not hold '{ammo}'")):
            from_placements(spec, 1, settings, bypass)


@pytest.mark.parametrize(
    ("ammo", "container", "accepted"),
    [("Deku Nuts (5)", "Deku Nut Capacity", True), ("Deku Stick (1)", "Deku Stick Capacity", False)],
)
def test_a_new_game_s_empty_nut_bag_lets_supplied_nuts_skip_the_capacity_gate(ammo, container, accepted):
    """The native new game's empty Nut Bag is an existing container: nuts may go where the Hammer bypasses the capacity
    upgrade. Sticks have no such bag and still need theirs."""
    spec = skulltula_spec(ammo, container, starting=("nut",))
    settings = Settings(shuffle=("Chest", tokens.SHUFFLE))
    bypass = {"Container Chest": container, "Hammer Chest": "Hammer", "Bypass GS": ammo, "Container GS": "Rupees (5)"}
    if accepted:
        assert from_placements(spec, 1, settings, bypass).placements["Bypass GS"] == ammo
    else:
        with pytest.raises(FillError, match=re.escape(f"Bypass GS: may not hold '{ammo}'")):
            from_placements(spec, 1, settings, bypass)
