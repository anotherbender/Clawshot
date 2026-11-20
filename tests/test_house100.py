"""The first hundred-token reward is junk by default and explicitly progression-eligible only on opt-in."""

from dataclasses import replace

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


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_opt_in_allows_a_required_reward_through_fill_and_external_assignments(shuffle):
    settings = Settings(shuffle=shuffle, shuffle_100_token_reward=True)
    spec = gift_spec()
    # A held progression item has exactly this NPC destination; fill cannot hide it in a chest.
    settings = replace(settings, item_location_types={"Boomerang": ("NPC",)})
    seed = generate(spec, 7, settings)
    assert seed.placements[HOUSE] == "Boomerang"
    assert spec["regions"][0]["locations"][HOUSE]["nonprogression_only"] is True
    supplied = {HOUSE: "Boomerang", "Chest A": "Rupees (5)", "Chest B": "Hylian Shield"}
    assert from_placements(spec, 7, settings, supplied).placements == supplied


@pytest.mark.parametrize("shuffle", SHUFFLES)
def test_opt_in_retains_explicit_exclusions_and_other_junk_checks(shuffle):
    spec = gift_spec()
    locations = spec["regions"][0]["locations"]
    locations[HOUSE]["excluded_items"] = ["Boomerang"]
    locations["Other Gift"] = {"rule": "True", "type": "NPC", "vanilla": "Rupees (5)", "nonprogression_only": True}
    settings, world = prepare(spec, Settings(shuffle=shuffle, shuffle_100_token_reward=True))
    assert not allowed(world, settings, HOUSE, "Boomerang")
    assert allowed(world, settings, HOUSE, "Hylian Shield")
    assert not allowed(world, settings, "Other Gift", "Hylian Shield")


@pytest.mark.parametrize("token", [False, True])
def test_production_hundred_gate_requires_every_token_even_with_opt_in(token):
    from clawshot.world import ADULT, CHILD, Search

    settings = Settings(
        shuffle=("Chest", "NPC", "Token") if token else ("Chest", "NPC"),
        shuffle_100_token_reward=True,
    )
    settings, world = prepare(load_spec(), settings)
    assert allowed(world, settings, HOUSE, "Megaton Hammer")
    rule = world.locations[HOUSE].rule
    for age in (CHILD, ADULT):
        assert not rule(Search(world, ["Gold Skulltula Token"] * 99).counts, age, 1)
        assert rule(Search(world, ["Gold Skulltula Token"] * 100).counts, age, 1)


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


@pytest.mark.dump
def test_native_opt_in_rewrites_only_the_first_reward_not_its_completion_or_repeat(romfs):
    from clawshot.census import definitions
    from clawshot.census.gifts import scan_gifts
    from clawshot.formats import evfl, zsdic
    from clawshot.generate.fill import shuffled_locations
    from clawshot.patch import gifts, items

    settings = Settings(shuffle=("Chest", "Gift"), shuffle_100_token_reward=True)
    spec, settings, _ = gifts.seed_setup(romfs, load_spec(), settings)
    settings, world = prepare(spec, settings)
    assert HOUSE in shuffled_locations(world, settings)
    assert world.locations[HOUSE].vanilla == "Rupees (200)"
    assert allowed(world, settings, HOUSE, "Megaton Hammer")
    path = "Event/EventFlow/GatheringTokenGold.bfevfl.zs"
    step = gifts.seed_step(
        [HOUSE],
        scan_gifts(romfs),
        definitions.load(),
        gifts.load(),
        items.load(),
        {HOUSE: "Rupees (200)"},
        {"GatheringTokenGold": path},
    )
    changes = step({HOUSE: "Megaton Hammer"})
    assert set(changes) == {path}
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = dictionaries.decompress(path, (romfs / path).read_bytes())
    before, after = evfl.read(original), evfl.read(changes[path](original))
    native = next(event for event in before.flowchart.events if event.name == "Event215")
    changed = next(event for event in after.flowchart.events if event.name == "Event215")
    assert native.params["TakenRewardActor"] == "Obj_Rupee_Gold"
    assert changed.params["TakenRewardActor"] == "Item_Hammer"
    changed.params["TakenRewardActor"] = native.params["TakenRewardActor"]
    assert before == after
