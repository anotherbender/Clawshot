"""Gold Skulltula shuffle in the fill (Round 15): the Token kind, its admitted rewards and every refusal.

Synthetic worlds exercise the real fill and beatability search; the whole world exercises the real ``prepare`` and
the fill's own placement predicate. No game resources, no seed sweep: each forced shape below holds for any fill.
"""

import random
from collections import Counter
from dataclasses import replace

import pytest

from clawshot.__main__ import main
from clawshot.app import schema, validate
from clawshot.generate import FillError, Settings, from_placements, generate, prepare
from clawshot.generate.fill import SHOP_ONLY_PREFIX, allowed, fill, shuffled_locations
from clawshot.generate.tokens import (
    REWARDS,
    SHUFFLE,
    SOURCE_TYPE,
    TOKEN_DESTINATIONS,
    TOKEN_ITEM,
)
from clawshot.progressive import FAMILY_BY_ITEM
from clawshot.world.load import build_world, load_spec

GS = SOURCE_TYPE
SPILL = ("GS A", "GS B", "GS C", "GS D")
FORCED = {"Boomerang": (SHUFFLE,), "Hylian Shield": (SHUFFLE,)}
ADMITTED_RUPEES = "Rupees (5)"  # a member of the admitted rupee family
FAIRY = "Fairy Ocarina"  # its ocarina family is admitted through Ocarina of Time; it has no world pickup to give
CARD = "Gerudo Membership Card"  # keeps its own holds, never a Skulltula reward


def spill_spec(other: str = "Chest") -> dict:
    """Four Skulltulas, two chests (Boomerang, Hylian Shield) and two checks of ``other`` kind (the Fairy Ocarina,
    which the goal needs, and the Gerudo card: neither is a Skulltula reward)."""
    return {
        "start": "Start",
        "goal": "Boomerang and Hylian_Shield and Fairy_Ocarina and (Gold_Skulltula_Token, 4)",
        "items": {
            TOKEN_ITEM: {"type": "Token"},
            "Boomerang": {},
            "Hylian Shield": {},
            FAIRY: {},
            CARD: {},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {
                    **{name: {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM} for name in SPILL},
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Boomerang"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Hylian Shield"},
                    "Other A": {"rule": "True", "type": other, "vanilla": FAIRY},
                    "Other B": {"rule": "True", "type": other, "vanilla": CARD},
                },
            }
        ],
    }


def temple_spec(held: str | None = None) -> dict:
    """A dungeon whose Skulltulas could take its small key by area, and an overworld chest with the Fairy Ocarina."""
    temple = {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM}
    return {
        "start": "Start",
        "goal": "Small_Key_Temple and Fairy_Ocarina and (Gold_Skulltula_Token, 3)",
        "items": {
            TOKEN_ITEM: {"type": "Token"},
            "Small Key (Temple)": {"type": "SmallKey", "dungeon": "Temple"},
            ADMITTED_RUPEES: {"class": "normal"},
            FAIRY: {},
        },
        "regions": [
            {
                "name": "Start",
                "exits": {"Temple": "True"},
                "locations": {
                    "Start Chest": {"rule": "True", "type": "Chest", "vanilla": FAIRY},
                    "Start GS": {**temple, **({"keep_vanilla": held} if held else {})},
                },
            },
            {
                "name": "Temple",
                "dungeon": "Temple",
                "locations": {
                    "Temple Chest": {"rule": "True", "type": "Chest", "vanilla": "Small Key (Temple)"},
                    "Temple GS 1": temple,
                    "Temple GS 2": temple,
                },
            },
        ],
    }


def tokens_at(seed, kind: str) -> list[str]:
    return [name for name in seed.shuffled if seed.world.locations[name].type == kind]


GOODS = ("Buy Heart", "Buy Arrows (10)", "Buy Fish")  # a recovery good, an ammo refill, a bottle content
SHELVES = tuple(f"Shelf {i}" for i in range(len(GOODS)))
SHOP_TOKEN = Settings(shuffle=("Chest", "Shop", SHUFFLE))


def shop_spec() -> dict:
    """Two Skulltulas, two chests and three shelves selling bought goods."""
    return {
        "start": "Start",
        "goal": "Boomerang and (Gold_Skulltula_Token, 2)",
        "settings": {"native_shop_items": list(GOODS)},
        "items": {
            TOKEN_ITEM: {"type": "Token"},
            "Boomerang": {},
            "Rupees (5)": {"class": "normal"},
            **{good: {"class": "normal"} for good in GOODS},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "GS A": {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM},
                    "GS B": {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM},
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Boomerang"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Rupees (5)"},
                    **{
                        shelf: {"rule": "True", "type": "Shop", "vanilla": good}
                        for shelf, good in zip(SHELVES, GOODS, strict=True)
                    },
                },
            }
        ],
    }


def test_a_skulltula_reward_and_a_chest_token_in_one_seed_keep_one_token_per_source():
    seed = generate(spill_spec(), 3, Settings(shuffle=("Chest", SHUFFLE), item_location_types=FORCED))
    assert tokens_at(seed, SHUFFLE) == list(SPILL)
    assert not tokens_at(seed, GS)
    assert sorted(seed.placements[name] for name in SPILL) == sorted(["Boomerang", "Hylian Shield", *[TOKEN_ITEM] * 2])
    chests = ("Chest A", "Chest B", "Other A", "Other B")  # all four are chests here
    assert Counter(seed.placements[name] for name in chests) == Counter({TOKEN_ITEM: 2, FAIRY: 1, CARD: 1})
    assert Counter(seed.placements.values())[TOKEN_ITEM] == len(SPILL)  # no bonus token, none lost


@pytest.mark.parametrize("other", ["Scrub", "NPC", "BossHeart", "Freestanding", "Song"])
def test_tokens_spill_only_into_chests_never_another_shuffled_kind(other):
    settings = Settings(shuffle=("Chest", other, SHUFFLE), item_location_types=FORCED)
    seed = generate(spill_spec(other), 5, settings)
    assert [seed.placements[name] for name in ("Chest A", "Chest B")] == [TOKEN_ITEM, TOKEN_ITEM]
    assert sorted(seed.placements[name] for name in ("Other A", "Other B")) == sorted([FAIRY, CARD])
    assert seed.settings.item_location_types[TOKEN_ITEM] == TOKEN_DESTINATIONS


@pytest.mark.parametrize("dungeon_items", ["own_dungeon", "anywhere"])
def test_small_keys_and_unadmitted_items_never_take_a_skulltula_even_in_their_dungeon(dungeon_items):
    spec = temple_spec()
    settings = Settings(shuffle=("Chest", SHUFFLE), dungeon_items=dungeon_items)
    effective, world = prepare(spec, settings)
    unheld = replace(effective, location_type_items={})
    assert not allowed(world, unheld, "Temple GS 1", "Small Key (Temple)")  # the dungeon-item hold stops it too
    assert not allowed(world, effective, "Temple GS 1", "Small Key (Temple)")
    assert allowed(world, effective, "Temple GS 1", ADMITTED_RUPEES)
    assert not allowed(world, effective, "Temple GS 1", FAIRY)
    seed = generate(spec, 1, settings)
    assert {seed.placements[name] for name in ("Start GS", "Temple GS 1", "Temple GS 2")} == {TOKEN_ITEM}
    assert {seed.placements["Start Chest"], seed.placements["Temple Chest"]} == {"Small Key (Temple)", FAIRY}


def test_off_leaves_skulltulas_native_and_the_settings_untouched():
    spec = spill_spec()
    seed = generate(spec, 3, Settings(shuffle=("Chest",)))
    assert tokens_at(seed, SHUFFLE) == [] and tokens_at(seed, GS) == []
    assert {seed.placements[name] for name in SPILL} == {TOKEN_ITEM}
    assert all(seed.world.locations[name].type == GS for name in SPILL)
    assert seed.settings == Settings(shuffle=("Chest",))  # no Token palette or hold enters an off seed's string


def test_a_held_skulltula_keeps_its_native_token_outside_the_pool():
    seed = generate(temple_spec(held="route not yet played"), 2, Settings(shuffle=("Chest", SHUFFLE)))
    assert "Start GS" not in seed.shuffled and seed.placements["Start GS"] == TOKEN_ITEM
    assert tokens_at(seed, SHUFFLE) == ["Temple GS 1", "Temple GS 2"]
    pool = Counter(seed.placements[name] for name in seed.shuffled)
    assert pool[TOKEN_ITEM] == 2 and Counter(seed.placements.values())[TOKEN_ITEM] == 3  # counted once each


def test_effective_settings_replay_to_the_same_constraints_and_seed():
    seed = generate(spill_spec(), 3, Settings(shuffle=("Chest", SHUFFLE), item_location_types=FORCED))
    replay = Settings.from_string(seed.settings.to_string())
    assert replay.location_type_items[SHUFFLE] == tuple(REWARDS)
    assert prepare(spill_spec(), replay)[0] == seed.settings
    assert generate(spill_spec(), 3, replay).placements == seed.placements


@pytest.mark.parametrize(
    "settings, message",
    [
        (Settings(shuffle=("Chest", GS)), "not a shuffle kind"),
        (Settings(shuffle=("Chest", SHUFFLE), location_type_items={SHUFFLE: (FAIRY,)}), "cannot give"),
        (Settings(shuffle=("Chest", SHUFFLE), item_location_types={TOKEN_ITEM: ("NPC",)}), "may go only to"),
        (Settings(shuffle=("Chest", SHUFFLE), item_location_types={FAIRY: ("Chest", SHUFFLE)}), "cannot give it"),
        (Settings(shuffle=("Chest", SHUFFLE), item_location_types={CARD: (SHUFFLE,)}), "cannot give it"),
    ],
)
def test_explicit_settings_cannot_widen_what_a_skulltula_may_give(settings, message):
    with pytest.raises(FillError, match=message):
        prepare(spill_spec(), settings)


def test_bought_goods_stay_on_shop_shelves_beside_skulltulas_and_chests():
    seed = generate(shop_spec(), 4, SHOP_TOKEN)
    assert sorted(seed.placements[shelf] for shelf in SHELVES) == sorted(GOODS)
    assert tokens_at(seed, SHUFFLE) == ["GS A", "GS B"]
    assert {seed.placements[name] for name in ("GS A", "GS B")} <= {TOKEN_ITEM, "Boomerang", ADMITTED_RUPEES}
    effective, world = prepare(shop_spec(), SHOP_TOKEN)
    for good in GOODS:
        assert effective.item_location_types[good] == ("Shop",)
        for name in ("GS A", "Chest A"):
            assert not allowed(world, effective, name, good)
            assert not allowed(world, Settings(), name, good)  # the fill rule needs no setting
        assert allowed(world, Settings(), SHELVES[0], good)


@pytest.mark.parametrize("shuffle", [("Chest", "Shop", SHUFFLE), ("Chest", SHUFFLE)])
@pytest.mark.parametrize(
    "override",
    [
        {"item_location_types": {"Buy Heart": ("Chest",)}},
        {"item_location_types": {"Buy Heart": ("Shop", SHUFFLE)}},
        {"location_type_items": {"Chest": ("Boomerang", "Buy Heart", "Rupees (5)", TOKEN_ITEM)}},
        {"location_type_items": {SHUFFLE: ("Buy Heart", TOKEN_ITEM)}},
    ],
)
def test_raw_settings_cannot_move_a_bought_good_off_the_shelves(shuffle, override):
    with pytest.raises(FillError, match="bought goods"):
        prepare(shop_spec(), Settings(shuffle=shuffle, **override))


def test_replay_keeps_bought_goods_on_the_shelves():
    seed = generate(shop_spec(), 4, SHOP_TOKEN)
    replay = Settings.from_string(seed.settings.to_string())
    assert {good: replay.item_location_types[good] for good in GOODS} == dict.fromkeys(GOODS, ("Shop",))
    assert prepare(shop_spec(), replay)[0] == seed.settings
    assert generate(shop_spec(), 4, replay).placements == seed.placements


def test_the_whole_world_keeps_every_bought_good_on_shop_shelves():
    shuffle = ("Chest", "Shop", "Scrub", "BossHeart", "Freestanding", SHUFFLE)
    effective, world = prepare(load_spec(), Settings(shuffle=shuffle))
    goods = [item for item in world.items if item.startswith(SHOP_ONLY_PREFIX)]
    assert goods and all(effective.item_location_types[good] == ("Shop",) for good in goods)
    for settings in (effective, Settings()):
        kinds = {
            location.type
            for name, location in world.locations.items()
            for good in goods
            if allowed(world, settings, name, good)
        }
        assert kinds == {"Shop"}


# Claude's Round 15 played additions, exercised through placement below.
ADDED = (
    "Rupees (200)",
    "Arrows (5)",
    "Arrows (10)",
    "Bombs (5)",
    "Deku Nuts (5)",
    "Deku Stick (1)",
    "Bombchus (5)",
    "Magic Jar",
    "Dins Fire",
    "Farores Wind",
    "Nayrus Love",
    "Ice Arrows",
    "Light Arrows",
    "Lens of Truth",
    "Stone of Agony",
    "Double Defense",
    "Scrub Business Seed",
    "Ocarina of Time",
)
ADDED_PROGRESSION = (
    "Bombchus (5)",
    "Dins Fire",
    "Farores Wind",
    "Nayrus Love",
    "Ice Arrows",
    "Light Arrows",
    "Lens of Truth",
    "Stone of Agony",
    "Ocarina of Time",
)
"""The added members the world data counts as progression; the others are junk there."""
# The members the core and families-1 packets admitted before them, unchanged.
EARLIER = (
    TOKEN_ITEM,
    "Boomerang",
    "Megaton Hammer",
    "Hylian Shield",
    "Deku Shield",
    "Mirror Shield",
    "Kokiri Sword",
    "Biggoron Sword",
    "Iron Boots",
    "Hover Boots",
    "Goron Tunic",
    "Zora Tunic",
    "Bottle",
    "Bottle with Milk",
    "Rupee (1)",
    "Rupees (5)",
    "Rupees (20)",
    "Rupees (50)",
    "Piece of Heart",
    "Heart Container",
    "Deku Nut Capacity",
    "Deku Stick Capacity",
)
# Plain items that keep their own policy and are never Skulltula rewards, beside every other kind (songs, keys, maps,
# compasses, shop stock), the bought goods, and the progressive copies and tiers: the Fairy Ocarina, the Gerudo card,
# and the child and adult trade sequences' items.
EXCLUDED = (
    FAIRY,
    CARD,
    "Weird Egg",
    "Chicken",
    "Zeldas Letter",
    "Keaton Mask",
    "Skull Mask",
    "Spooky Mask",
    "Bunny Hood",
    "Mask of Truth",
    "Goron Mask",
    "Zora Mask",
    "Gerudo Mask",
    "Pocket Egg",
    "Pocket Cucco",
    "Cojiro",
    "Odd Mushroom",
    "Odd Potion",
    "Poachers Saw",
    "Broken Sword",
    "Prescription",
    "Eyeball Frog",
    "Eyedrops",
    "Claim Check",
)


def test_the_whole_world_holds_every_skulltula_to_exactly_the_admitted_members_and_tokens_to_chests():
    spec = load_spec()
    effective, world = prepare(spec, Settings(shuffle=("Chest", SHUFFLE)))
    native = prepare(spec, Settings())[1]
    sources = [name for name, loc in native.locations.items() if loc.type == GS]
    assert sources and [name for name in sources if world.locations[name].type == SHUFFLE] == sources
    assert not any(loc.type == GS for loc in world.locations.values())
    live = {name for name in sources if native.locations[name].n64_only is None}
    assert live <= set(shuffled_locations(world, effective))
    assert set(EXCLUDED) <= set(world.items) and world.progressive
    own_kind = {name for name, item in world.items.items() if item.type not in ("Item", "Token")}
    assert {"Song", "SmallKey", "BossKey", "Map", "Compass", "Shop"} <= {world.items[name].type for name in own_kind}
    bought = {name for name in world.items if name.startswith(SHOP_ONLY_PREFIX)}
    kept = {*EXCLUDED, *own_kind, *bought, *world.progressive, *(set(FAMILY_BY_ITEM) & set(world.items))}
    expected = {*EARLIER, *ADDED}
    for name in live:
        given = {item for item in world.items if allowed(world, effective, name, item)}
        assert given == expected and not given & kept, name
    kinds = {loc.type for name, loc in world.locations.items() if allowed(world, effective, name, TOKEN_ITEM)}
    assert kinds == set(TOKEN_DESTINATIONS)


# Each admitted ammo pickup, Bombchus included, and an independent container that guarantees it.
AMMO = {
    "Arrows (5)": "Bow",
    "Arrows (10)": "Bow",
    "Bombs (5)": "Bomb Bag",
    "Bombchus (5)": "Bomb Bag",
    "Deku Nuts (5)": "Deku Nut Capacity",
    "Deku Stick (1)": "Deku Stick Capacity",
}


def member_spec(item: str, *, guaranteed: bool = True) -> dict:
    """An open Skulltula and one behind the item's container where it is ammo (open too otherwise), a chest with the
    container (or rupees) and one with an unrelated Hammer, which also opens the gated Skulltula unless ``guaranteed``.
    No native bag is assumed."""
    container = AMMO.get(item)
    chest = container or ADMITTED_RUPEES
    gate = f"'{container}'" if container else "True"
    goal = "(Gold_Skulltula_Token, 1)"
    if container:
        goal += f" and {gate}"
    if item in ADDED_PROGRESSION:
        goal += f" and '{item}'"
    return {
        "start": "Start",
        "goal": goal,
        "items": {
            TOKEN_ITEM: {"type": "Token"},
            item: {} if item in ADDED_PROGRESSION else {"class": "normal"},
            chest: {} if container else {"class": "normal"},
            "Hammer": {},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Open GS": {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM},
                    "Gated GS": {"rule": gate if guaranteed else f"{gate} or Hammer", "type": GS, "vanilla": item},
                    "Container Chest": {"rule": "True", "type": "Chest", "vanilla": chest},
                    "Hammer Chest": {"rule": "True", "type": "Chest", "vanilla": "Hammer"},
                },
            }
        ],
    }


def member_settings(item: str) -> Settings:
    return Settings(shuffle=("Chest", SHUFFLE), item_location_types={item: (SHUFFLE,)})


@pytest.mark.parametrize("item", list(ADDED))
def test_each_added_member_goes_to_a_skulltula_and_another_placer_may_put_it_there(item):
    spec = member_spec(item)
    seed = generate(spec, 1, member_settings(item))
    (where,) = [name for name in seed.shuffled if seed.placements[name] == item]
    assert seed.world.locations[where].type == SHUFFLE
    assert where == "Gated GS" or item not in AMMO  # ammo only where its container is guaranteed
    vanilla = Counter(location["vanilla"] for location in spec["regions"][0]["locations"].values())
    assert Counter(seed.placements.values()) == vanilla  # no pool item becomes a container or weapon
    supplied = {name: seed.placements[name] for name in seed.shuffled}
    assert from_placements(spec, 1, member_settings(item), supplied).placements[where] == item


@pytest.mark.parametrize("item", list(AMMO))
def test_added_ammo_held_to_skulltulas_fails_where_every_one_bypasses_its_container(item):
    with pytest.raises(FillError):
        generate(member_spec(item, guaranteed=False), 1, member_settings(item), attempts=1)


def test_forest_closed_seed7_shared_bow_slot_uses_only_one_arrow_bundle():
    """The traced cohort had two arrow sizes competing for one guaranteed-Bow Skulltula."""
    spec = {
        "start": "Start",
        "goal": "Bow and (Gold_Skulltula_Token, 2)",
        "items": {
            TOKEN_ITEM: {"type": "Token"},
            "Bow": {},
            "Arrows (5)": {"class": "normal"},
            "Arrows (10)": {"class": "normal"},
            ADMITTED_RUPEES: {"class": "normal"},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Small Arrow Chest": {"rule": "True", "type": "Chest", "vanilla": "Arrows (5)"},
                    "Open GS": {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM},
                    "Bow Chest": {"rule": "True", "type": "Chest", "vanilla": "Bow"},
                    "Bow GS": {"rule": "Bow", "type": GS, "vanilla": TOKEN_ITEM},
                    "Large Arrow Chest": {"rule": "True", "type": "Chest", "vanilla": "Arrows (10)"},
                    "Rupee Chest": {"rule": "True", "type": "Chest", "vanilla": ADMITTED_RUPEES},
                },
            }
        ],
    }
    settings = Settings(shuffle=("Chest", SHUFFLE), item_location_types={TOKEN_ITEM: ("Chest",)})
    seed = generate(spec, 7, settings, attempts=1)
    assert seed.placements["Open GS"] == ADMITTED_RUPEES
    assert seed.placements["Bow GS"] in {"Arrows (5)", "Arrows (10)"}
    assert Counter(seed.placements.values()) == Counter(
        {TOKEN_ITEM: 2, "Bow": 1, "Arrows (5)": 1, "Arrows (10)": 1, ADMITTED_RUPEES: 1}
    )


def test_mixed_keys_anywhere_seed7_keeps_token_and_sword_in_shared_progression():
    """Freezing Sword on the gated GS sends its token to the only starter chest, stranding Boomerang."""
    spec = {
        "start": "Start",
        "goal": "Kokiri_Sword and Boomerang and Fairy_Ocarina and Gold_Skulltula_Token",
        "items": {TOKEN_ITEM: {"type": "Token"}, "Kokiri Sword": {}, "Boomerang": {}, FAIRY: {}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Starter Chest": {"rule": "True", "type": "Chest", "vanilla": FAIRY},
                    "Gated GS": {"rule": "Boomerang", "type": GS, "vanilla": TOKEN_ITEM},
                    "Late Chest A": {
                        "rule": "Kokiri_Sword",
                        "type": "Chest",
                        "vanilla": "Boomerang",
                        "excluded_items": [TOKEN_ITEM],
                    },
                    "Late Chest B": {
                        "rule": "Kokiri_Sword",
                        "type": "Chest",
                        "vanilla": "Kokiri Sword",
                        "excluded_items": [TOKEN_ITEM],
                    },
                },
            }
        ],
    }
    seed = generate(spec, 7, Settings(shuffle=("Chest", SHUFFLE), dungeon_items="anywhere"), attempts=1)
    assert seed.placements["Starter Chest"] == "Kokiri Sword"
    assert seed.placements["Gated GS"] == TOKEN_ITEM
    assert {seed.placements["Late Chest A"], seed.placements["Late Chest B"]} == {"Boomerang", FAIRY}


def test_app_offers_token_with_chest_and_refuses_token_alone():
    option = next(o for row in schema() if row["key"] == "shuffle" for o in row["options"] if o["value"] == SHUFFLE)
    assert not option["disabled"]
    assert validate({"shuffle": ["Chest", SHUFFLE]}).shuffle == ("Chest", SHUFFLE)
    with pytest.raises(ValueError, match="Chest"):
        validate({"shuffle": [SHUFFLE]})


@pytest.mark.parametrize(
    "values",
    [
        {"shuffle": ["Chest", "Gift", SHUFFLE]},
        {"shuffle": ["Chest", "Shop", "Gift", "Scrub", "BossHeart", "Freestanding", SHUFFLE]},
        {"shuffle": ["Chest", "Gift", SHUFFLE], "songs": "anywhere", "dungeon_items": "anywhere"},
        {"shuffle": ["Chest", SHUFFLE], "logic": {"free_time_travel": True}},
    ],
)
def test_app_accepts_token_with_every_offered_combination(values):
    settings = validate(values)
    assert validate(text=settings.to_string()) == settings


def test_cli_spelling_and_replay_match_the_app(capsys):
    assert main(["--print-settings", "--shuffle", "Chest", SHUFFLE]) == 0
    text = capsys.readouterr().out.strip()
    assert Settings.from_string(text).shuffle == ("Chest", SHUFFLE) == validate(text=text).shuffle
    assert main(["--print-settings", "--settings", text]) == 0
    assert capsys.readouterr().out.strip() == text


# The fill's own container screen, given raw palettes without prepare: every ammo family it screens, Deku Seeds too,
# though seeds are no Skulltula reward (a generic screen check, not admission).
AMMO_CONTAINERS = (
    ("Bombs (5)", "Bomb Bag"),
    ("Bombchus (5)", "Bomb Bag"),
    ("Arrows (5)", "Bow"),
    ("Arrows (10)", "Quiver (40)"),
    ("Deku Seeds (30)", "Slingshot"),
    ("Deku Nuts (5)", "Deku Nut Capacity"),
    ("Deku Stick (1)", "Deku Stick Capacity"),
)


def container_world(ammo, container, *, guaranteed=True, starting=()):
    """A container, an unrelated bypass item, and two Skulltulas; no native bag is assumed."""
    gate = f"'{container}'"
    return build_world(
        {
            "start": "Start",
            "goal": gate,
            "settings": {"token_starting_containers": list(starting)},
            "items": {container: {}, "Hammer": {}, ammo: {}, "Rupee": {"class": "normal"}},
            "regions": [
                {
                    "name": "Start",
                    "locations": {
                        "Container Chest": {"rule": "True", "type": "Chest", "vanilla": container},
                        "Hammer Chest": {"rule": "True", "type": "Chest", "vanilla": "Hammer"},
                        "Bypass GS": {"type": SHUFFLE, "rule": f"{gate} or Hammer", "vanilla": "Rupee"},
                        "Container GS": {
                            "type": SHUFFLE,
                            "rule": gate if guaranteed else f"{gate} or Hammer",
                            "vanilla": ammo,
                        },
                    },
                }
            ],
        }
    )


def container_settings(ammo, *, palette=True):
    return Settings(
        shuffle=("Chest", SHUFFLE),
        location_type_items={SHUFFLE: (ammo, "Rupee")} if palette else {},
        item_location_types={ammo: (SHUFFLE,)},
    )


@pytest.mark.parametrize(("ammo", "container"), AMMO_CONTAINERS)
@pytest.mark.parametrize("palette", [True, False])
def test_skulltula_ammo_requires_its_container_even_with_an_unrelated_bypass(ammo, container, palette):
    world = container_world(ammo, container)
    placements = fill(world, container_settings(ammo, palette=palette), random.Random(0))
    assert placements["Container GS"] == ammo
    assert placements["Bypass GS"] == "Rupee"
    # The ammo placement changes no pool item into a container or weapon.
    assert Counter(placements.values()) == Counter({ammo: 1, container: 1, "Hammer": 1, "Rupee": 1})


@pytest.mark.parametrize(("ammo", "container"), AMMO_CONTAINERS)
def test_skulltula_palette_refuses_ammo_when_every_source_can_bypass_its_container(ammo, container):
    world = container_world(ammo, container, guaranteed=False)
    with pytest.raises(FillError):
        fill(world, container_settings(ammo), random.Random(0))


def test_existing_empty_nut_bag_allows_a_refill_without_a_capacity_upgrade():
    world = container_world("Deku Nuts (5)", "Deku Nut Capacity", guaranteed=False, starting=("nut",))
    placements = fill(world, container_settings("Deku Nuts (5)"), random.Random(0))
    assert (
        sum(item == "Deku Nuts (5)" for name, item in placements.items() if world.locations[name].type == SHUFFLE) == 1
    )
