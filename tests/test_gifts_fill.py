"""Dungeon keys keep their bootstrap slots before bag-gated ammo is placed (D25); Granny's potion never enters an
ordinary gift pool."""

from collections import Counter

from clawshot.generate import Settings, generate, prepare
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import gifts

GIFTS = Settings(shuffle=("Chest", "NPC"))


def test_ammo_prefill_cannot_consume_the_only_early_dungeon_key_slot():
    spec = {
        "start": "Start",
        "goal": "Small_Key_Temple",
        "items": {
            "Bomb Bag": {},
            "Small Key (Temple)": {"type": "SmallKey"},
            "Bombs (5)": {"class": "normal"},
            "Bombchus (5)": {},
        },
        "regions": [
            {
                "name": "Start",
                "locations": {"Bag": {"rule": "True", "type": "Chest", "vanilla": "Bomb Bag"}},
                "exits": {"Temple": "Bomb_Bag"},
            },
            {
                "name": "Temple",
                "dungeon": "Temple",
                "locations": {
                    "Entrance Key": {"rule": "True", "type": "Chest", "vanilla": "Small Key (Temple)"},
                    "Locked Bombs": {"rule": "Small_Key_Temple", "type": "Chest", "vanilla": "Bombs (5)"},
                    "Locked Bombchus": {"rule": "Small_Key_Temple", "type": "Chest", "vanilla": "Bombchus (5)"},
                },
            },
        ],
    }
    seed = generate(spec, 0, Settings(), attempts=1)
    assert seed.placements["Bag"] == "Bomb Bag"
    assert seed.placements["Entrance Key"] == "Small Key (Temple)"
    assert {seed.placements[name] for name in ("Locked Bombs", "Locked Bombchus")} == {
        "Bombs (5)",
        "Bombchus (5)",
    }
    sphere_of = {name: index for index, sphere in enumerate(seed.spheres) for name in sphere}
    assert sphere_of["Bag"] < sphere_of["Entrance Key"]
    assert all(sphere_of["Entrance Key"] < sphere_of[name] for name in ("Locked Bombs", "Locked Bombchus"))


def test_type_held_song_is_placed_before_flexible_progression_can_depend_on_it():
    # The real Gift seed exposed Storms -> bag -> adult-only remaining song slots.
    # Keep the type-restricted song ahead of flexible items, not only shop-native items.
    spec = {
        "start": "Start",
        "goal": "Storms and Bomb_Bag and Hammer",
        "items": {"Bomb Bag": {}, "Hammer": {}, "Storms": {"type": "Song"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Early Chest": {"rule": "True", "type": "Chest", "vanilla": "Bomb Bag"},
                    "Storms Chest": {"rule": "Storms", "type": "Chest", "vanilla": "Hammer"},
                    "Bag Song": {"rule": "Bomb_Bag", "type": "Song", "vanilla": "Storms"},
                },
            }
        ],
    }
    settings = Settings(
        shuffle=("Chest", "Song"),
        item_location_types={"Storms": ("Song",)},
        exclusive_location_types=("Song",),
    )
    seed = generate(spec, 2, settings, attempts=1)
    assert seed.placements == {"Early Chest": "Bomb Bag", "Storms Chest": "Hammer", "Bag Song": "Storms"}
    sphere_of = {name: index for index, sphere in enumerate(seed.spheres) for name in sphere}
    assert sphere_of["Early Chest"] < sphere_of["Bag Song"] < sphere_of["Storms Chest"]


def test_type_held_ammo_still_requires_an_independent_bag():
    spec = {
        "start": "Start",
        "goal": "Bomb_Bag",
        "items": {"Bomb Bag": {}, "Bombs (5)": {"class": "normal"}, "Rupee": {"class": "normal"}},
        "regions": [
            {
                "name": "Start",
                "locations": {
                    "Open A": {"rule": "True", "type": "Chest", "vanilla": "Bomb Bag"},
                    "Open B": {"rule": "True", "type": "Chest", "vanilla": "Rupee"},
                    "Bag Required": {"rule": "Bomb_Bag", "type": "Chest", "vanilla": "Bombs (5)"},
                },
            }
        ],
    }
    settings = Settings(item_location_types={"Bombs (5)": ("Chest",)})
    for number in range(20):
        seed = generate(spec, number, settings, attempts=1)
        assert seed.placements["Bag Required"] == "Bombs (5)", (number, seed.placements)
        sphere_of = {name: index for index, sphere in enumerate(seed.spheres) for name in sphere}
        bag = next(name for name, item in seed.placements.items() if item == "Bomb Bag")
        assert sphere_of[bag] < sphere_of["Bag Required"]


def granny_world(*, pinned=False):
    """A tiny world with Granny's native Blue Potion sale beside ordinary gift and chest sources."""
    granny = {"type": "NPC", "vanilla": "Blue Potion"}
    if pinned:
        granny["keep_vanilla"] = "explicit identity pin"
    sources = {
        gifts.GRANNY_CHECK: granny,
        "Hammer Gift": {"type": "NPC", "vanilla": "Hammer"},
        "Rupee Gift": {"type": "NPC", "vanilla": "Rupees (5)"},
        "Boots Chest": {"type": "Chest", "vanilla": "Boots"},
    }
    return {
        "start": "Start",
        "goal": "Hammer",
        "items": {
            "Blue Potion": {"type": "Item", "class": "progression"},
            "Rupees (5)": {"type": "Item", "class": "normal"},
            "Hammer": {"type": "Item", "class": "progression"},
            "Boots": {"type": "Item", "class": "progression"},
        },
        "locations": sources,
        "regions": [{"name": "Start", "locations": {name: "True" for name in sources}}],
    }


def test_ordinary_gift_pool_trades_granny_potion_for_one_more_five_rupees():
    native = granny_world()
    assert gifts.logic_spec(native, Settings(shuffle=("Chest",))) == native  # no gift shuffle: the native sale
    spec = gifts.logic_spec(native, GIFTS)
    assert native["locations"][gifts.GRANNY_CHECK]["vanilla"] == "Blue Potion"  # the source spec is not changed
    assert gifts.logic_spec(spec, GIFTS) == spec
    _, world = prepare(spec, GIFTS)
    shuffled = shuffled_locations(world, GIFTS)
    assert gifts.GRANNY_CHECK in shuffled and len(shuffled) == len(native["locations"])
    pool = Counter(world.locations[name].vanilla for name in shuffled)
    assert pool == Counter({"Hammer": 1, "Boots": 1, gifts.GRANNY_POOL_ITEM: 2})
    for number in range(10):
        seed = generate(spec, number, GIFTS, attempts=1)
        assert len(seed.placements) == len(native["locations"])
        assert Counter(seed.placements.values()) == pool, (number, seed.placements)


def test_identity_pin_keeps_granny_native_potion_at_granny_and_out_of_the_fill():
    spec = gifts.logic_spec(granny_world(pinned=True), GIFTS)
    _, world = prepare(spec, GIFTS)
    shuffled = shuffled_locations(world, GIFTS)
    assert gifts.GRANNY_CHECK not in shuffled
    assert "Blue Potion" not in {world.locations[name].vanilla for name in shuffled}
    for number in range(10):
        seed = generate(spec, number, GIFTS, attempts=1)
        assert [name for name, item in seed.placements.items() if item == "Blue Potion"] == [gifts.GRANNY_CHECK]
        moved = Counter(seed.placements[name] for name in seed.shuffled)
        assert moved == Counter({"Hammer": 1, "Boots": 1, "Rupees (5)": 1}), (number, seed.placements)
