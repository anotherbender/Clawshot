"""House100 is junk by policy, not because three native Skulltulas were absent from the logic."""

import pytest

from clawshot.generate import FillError, Settings, from_placements, generate, prepare
from clawshot.generate.fill import _swap, allowed
from clawshot.world import build_world, load_spec

HOUSE = "Kak 100 Gold Skulltula Reward"
SHUFFLES = [("Chest", "NPC"), ("Chest", "NPC", "Token")]


def gift_spec():
    return {
        "start": "Root",
        "goal": "Boomerang and Hylian_Shield",
        "items": {
            "Boomerang": {},
            "Hylian Shield": {},
            "Rupees (5)": {"class": "normal"},
        },
        "regions": [
            {
                "name": "Root",
                "locations": {
                    "Chest A": {"rule": "True", "type": "Chest", "vanilla": "Boomerang"},
                    "Chest B": {"rule": "True", "type": "Chest", "vanilla": "Hylian Shield"},
                    HOUSE: {"rule": "True", "type": "NPC", "vanilla": "Rupees (5)", "nonprogression_only": True},
                },
            }
        ],
    }


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_every_production_progression_item_is_refused_at_house100(shuffle):
    settings, world = prepare(load_spec(), Settings(shuffle=shuffle))
    unsafe = [item for item, info in world.items.items() if info.progression and allowed(world, settings, HOUSE, item)]
    assert not unsafe, unsafe
    assert world.items["Stone of Agony"].progression
    assert allowed(world, settings, HOUSE, "Rupees (5)")


@pytest.mark.parametrize("shuffle", SHUFFLES)
@pytest.mark.parametrize("palette", [False, True])
def test_a_gift_seed_keeps_the_reachable_hundred_reward_junk(shuffle, palette):
    # Even an explicit NPC palette offering progression cannot widen the data policy.
    options = {"location_type_items": {"NPC": ("Boomerang", "Hylian Shield", "Rupees (5)")}} if palette else {}
    seed = generate(gift_spec(), 7, Settings(shuffle=shuffle, **options))
    assert seed.placements[HOUSE] == "Rupees (5)"
    assert {seed.placements["Chest A"], seed.placements["Chest B"]} == {"Boomerang", "Hylian Shield"}


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_external_assignments_cannot_opt_house100_into_progression(shuffle):
    supplied = {HOUSE: "Boomerang", "Chest A": "Rupees (5)", "Chest B": "Hylian Shield"}
    with pytest.raises(FillError, match=HOUSE):
        from_placements(gift_spec(), 7, Settings(shuffle=shuffle), supplied)


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_type_held_progression_cannot_take_house100(shuffle):
    with pytest.raises(FillError, match="Boomerang"):
        generate(gift_spec(), 7, Settings(shuffle=shuffle, item_location_types={"Boomerang": ("NPC",)}))


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_swap_cannot_replace_house100_junk_with_progression(shuffle):
    world = build_world(gift_spec())
    placements = {HOUSE: "Rupees (5)", "Chest A": "Boomerang"}
    before = dict(placements)
    assert _swap(world, Settings(shuffle=shuffle), placements, [HOUSE], "Hylian Shield", [], {}) is None
    assert placements == before


@pytest.mark.dump
@pytest.mark.parametrize("token", [False, True])
def test_native_gift_seed_puts_nonprogression_at_house100(romfs, token):
    from clawshot.patch import gifts, make_seed

    settings = Settings(shuffle=("Chest", "Gift", "Token") if token else ("Chest", "Gift"))
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
    output = make_seed(romfs, 7, settings, spec, extra_steps=(step,))
    item = output.seed.placements[HOUSE]
    assert HOUSE in output.seed.shuffled
    assert not output.seed.world.items[item].progression, item
