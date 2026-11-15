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
from clawshot.generate import FillError, Settings, generate, prepare
from clawshot.generate.fill import SHOP_ONLY_PREFIX, allowed, fill, shuffled_locations
from clawshot.generate.tokens import (
    REWARDS,
    SHUFFLE,
    SOURCE_TYPE,
    TOKEN_DESTINATIONS,
    TOKEN_ITEM,
)
from clawshot.world.load import build_world, load_spec

GS = SOURCE_TYPE
SPILL = ("GS A", "GS B", "GS C", "GS D")
FORCED = {"Boomerang": (SHUFFLE,), "Hylian Shield": (SHUFFLE,)}
ADMITTED_RUPEES = "Rupees (5)"  # a member of the admitted rupee family
UNPLAYED = "Rupees (200)"  # gold_rupee: an unplayed family, outside the Token rewards


def spill_spec(other: str = "Chest") -> dict:
    """Four Skulltulas, two chests (Boomerang, Hylian Shield) and two checks of ``other`` kind (gold rupees)."""
    return {
        "start": "Start",
        "goal": "Boomerang and Hylian_Shield and (Gold_Skulltula_Token, 4)",
        "items": {
            TOKEN_ITEM: {"type": "Token"},
            "Boomerang": {},
            "Hylian Shield": {},
            UNPLAYED: {"class": "normal"},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {
                    **{name: {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM} for name in SPILL},
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Boomerang"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Hylian Shield"},
                    "Other A": {"rule": "True", "type": other, "vanilla": UNPLAYED},
                    "Other B": {"rule": "True", "type": other, "vanilla": UNPLAYED},
                },
            }
        ],
    }


def temple_spec(held: str | None = None) -> dict:
    """A dungeon whose Skulltulas could take its small key by area, and an overworld chest."""
    temple = {"rule": "True", "type": GS, "vanilla": TOKEN_ITEM}
    return {
        "start": "Start",
        "goal": "Small_Key_Temple and (Gold_Skulltula_Token, 3)",
        "items": {
            TOKEN_ITEM: {"type": "Token"},
            "Small Key (Temple)": {"type": "SmallKey", "dungeon": "Temple"},
            ADMITTED_RUPEES: {"class": "normal"},
            UNPLAYED: {"class": "normal"},
        },
        "regions": [
            {
                "name": "Start",
                "exits": {"Temple": "True"},
                "locations": {
                    "Start Chest": {"rule": "True", "type": "Chest", "vanilla": UNPLAYED},
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
    assert Counter(seed.placements[name] for name in chests) == Counter({TOKEN_ITEM: 2, UNPLAYED: 2})
    assert Counter(seed.placements.values())[TOKEN_ITEM] == len(SPILL)  # no bonus token, none lost


@pytest.mark.parametrize("other", ["Scrub", "NPC", "BossHeart", "Freestanding", "Song"])
def test_tokens_spill_only_into_chests_never_another_shuffled_kind(other):
    settings = Settings(shuffle=("Chest", other, SHUFFLE), item_location_types=FORCED)
    seed = generate(spill_spec(other), 5, settings)
    assert [seed.placements[name] for name in ("Chest A", "Chest B")] == [TOKEN_ITEM, TOKEN_ITEM]
    assert [seed.placements[name] for name in ("Other A", "Other B")] == [UNPLAYED, UNPLAYED]
    assert seed.settings.item_location_types[TOKEN_ITEM] == TOKEN_DESTINATIONS


@pytest.mark.parametrize("dungeon_items", ["own_dungeon", "anywhere"])
def test_small_keys_and_unadmitted_filler_never_take_a_skulltula_even_in_their_dungeon(dungeon_items):
    spec = temple_spec()
    settings = Settings(shuffle=("Chest", SHUFFLE), dungeon_items=dungeon_items)
    effective, world = prepare(spec, settings)
    unheld = replace(effective, location_type_items={})
    assert allowed(world, unheld, "Temple GS 1", "Small Key (Temple)")  # in its dungeon: only the palette stops it
    assert not allowed(world, effective, "Temple GS 1", "Small Key (Temple)")
    assert allowed(world, effective, "Temple GS 1", ADMITTED_RUPEES)
    assert not allowed(world, effective, "Temple GS 1", UNPLAYED)
    seed = generate(spec, 1, settings)
    assert {seed.placements[name] for name in ("Start GS", "Temple GS 1", "Temple GS 2")} == {TOKEN_ITEM}
    assert {seed.placements["Start Chest"], seed.placements["Temple Chest"]} == {"Small Key (Temple)", UNPLAYED}


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
        (Settings(shuffle=("Chest", SHUFFLE), location_type_items={SHUFFLE: (UNPLAYED,)}), "cannot give"),
        (Settings(shuffle=("Chest", SHUFFLE), item_location_types={TOKEN_ITEM: ("NPC",)}), "may go only to"),
        (Settings(shuffle=("Chest", SHUFFLE), item_location_types={UNPLAYED: ("Chest", SHUFFLE)}), "cannot give it"),
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


def test_the_whole_world_holds_every_skulltula_to_admitted_rewards_and_tokens_to_chests():
    spec = load_spec()
    effective, world = prepare(spec, Settings(shuffle=("Chest", SHUFFLE)))
    native = prepare(spec, Settings())[1]
    sources = [name for name, loc in native.locations.items() if loc.type == GS]
    assert sources and [name for name in sources if world.locations[name].type == SHUFFLE] == sources
    assert not any(loc.type == GS for loc in world.locations.values())
    live = {name for name in sources if native.locations[name].n64_only is None}
    assert live <= set(shuffled_locations(world, effective))
    for name in live:
        given = {item for item in world.items if allowed(world, effective, name, item)}
        assert TOKEN_ITEM in given and given <= set(REWARDS), name
    copies = set(world.progressive)
    assert copies and not any(allowed(world, effective, name, copy) for name in live for copy in copies)
    kinds = {loc.type for name, loc in world.locations.items() if allowed(world, effective, name, TOKEN_ITEM)}
    assert kinds == set(TOKEN_DESTINATIONS)


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
    with pytest.raises(FillError, match=SHUFFLE):
        fill(world, container_settings(ammo), random.Random(0))


def test_existing_empty_nut_bag_allows_a_refill_without_a_capacity_upgrade():
    world = container_world("Deku Nuts (5)", "Deku Nut Capacity", guaranteed=False, starting=("nut",))
    placements = fill(world, container_settings("Deku Nuts (5)"), random.Random(0))
    assert (
        sum(item == "Deku Nuts (5)" for name, item in placements.items() if world.locations[name].type == SHUFFLE) == 1
    )
