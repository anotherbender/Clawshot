"""Released gifts contribute their placed item, not an assumed early bottle; Granny's pool item is Rupees (5)."""

import pytest

from clawshot.census import definitions
from clawshot.census.gifts import Gift
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import gifts
from clawshot.patch import items as item_actors
from clawshot.patch.items import ItemActorError
from clawshot.world.load import load_spec
from clawshot.world.search import Search

RELEASED = (gifts.MARKET_BOTTLE_CHECK, gifts.DAMPE_CHECK)
GIFTS = Settings(shuffle=("Chest", *gifts.GIFT_TYPES))
# A synthetic census step shaped like Granny's: her native sale refills a bottle with Item_Bottle_BluePotion.
GRANNY_STEP = Gift(
    "Npc_Hylia_053_Adult/Event12",
    "npc_gift",
    "Npc_Hylia_053_Adult",
    "synthetic/Npc_Hylia_053_Adult.bfevfl",
    ("Buy_BluePotion", "Talk"),
    "Event12",
    "Dm_SY_GetInEvent:GetInEventInBottle_BlueBottleShop",
    "ActorName",
    "Item_Bottle_BluePotion",
    "",
)


def granny_checks(world):
    """Whether the seed's gift step may move Granny, given her native census step and the real item table."""
    return gifts.seed_checks(world, [GRANNY_STEP], definitions.load(), gifts.load(), item_actors.load())


@pytest.mark.parametrize("shuffle", [("Chest",), ("Chest", *gifts.GIFT_TYPES)])
def test_bottle_access_uses_the_selected_reward_not_a_fixed_early_bottle(shuffle):
    spec = load_spec()
    spec["start"] = "Market Potion Shop"
    shop = next(region for region in spec["regions"] if region["name"] == spec["start"])
    shop["locations"]["Bottle-dependent probe"] = {"rule": "has_bottle", "type": "NPC"}
    _, world = prepare(spec, Settings(shuffle=shuffle))
    selected = shuffled_locations(world, Settings(shuffle=shuffle))
    gift_shuffle = "NPC" in shuffle
    assert all((name in selected) is gift_shuffle for name in RELEASED)
    # Isolate this source: no other fixed bottle or later route can mask an assumed grant.
    item = "Boomerang" if gift_shuffle else world.locations[gifts.MARKET_BOTTLE_CHECK].vanilla
    search = Search(world)
    search.collect_spheres({gifts.MARKET_BOTTLE_CHECK: item})
    assert search.counts.get("Bottle", 0) == (0 if gift_shuffle else 1)
    assert search.counts.get("Boomerang", 0) == int(gift_shuffle)
    # A bottle-dependent check must not open merely because the merchant was collected.
    assert search.can_access(world.locations["Bottle-dependent probe"], "child") is not gift_shuffle


def test_branch_admits_merchants_but_keeps_expert_galleries_vanilla():
    _, world = prepare(load_spec(), Settings(shuffle=gifts.GIFT_TYPES))
    selected = set(shuffled_locations(world, Settings(shuffle=gifts.GIFT_TYPES)))
    assert set(RELEASED) <= selected
    for name in gifts.GALLERY_EXPERT_CHECKS.values():
        assert name not in selected, name
        assert world.locations[name].keep_vanilla, name
    for name in ("GC Medigoron", "Wasteland Bombchu Salesman", gifts.GRANNY_CHECK):
        assert name in selected, name
        assert not world.locations[name].keep_vanilla, name


def test_ordinary_gift_world_replaces_only_granny_potion_with_five_rupees():
    native = load_spec()
    _, before = prepare(gifts.shopkeeper_spec(native), GIFTS)
    _, after = prepare(gifts.logic_spec(native, GIFTS), GIFTS)
    assert after.locations.keys() == before.locations.keys()
    changed = {
        name: (before.locations[name].vanilla, location.vanilla)
        for name, location in after.locations.items()
        if location.vanilla != before.locations[name].vanilla
    }
    assert changed == {gifts.GRANNY_CHECK: ("Blue Potion", gifts.GRANNY_POOL_ITEM)}
    assert all(location.vanilla != "Blue Potion" for location in after.locations.values())
    # The same checks shuffle, so the pool keeps its size; only Granny's contribution differs.
    assert gifts.GRANNY_CHECK in shuffled_locations(after, GIFTS)
    assert shuffled_locations(after, GIFTS) == shuffled_locations(before, GIFTS)
    # Her native refill still moves without any item-table alias for the potion.
    with pytest.raises(ItemActorError):
        item_actors.load().actor("Blue Potion")
    assert granny_checks(after) == [gifts.GRANNY_CHECK]


def test_identity_pin_holds_granny_native_potion_out_of_the_ordinary_pool():
    spec = load_spec()
    granny = {**spec["locations"][gifts.GRANNY_CHECK], "keep_vanilla": "explicit identity pin"}
    spec["locations"] = {**spec["locations"], gifts.GRANNY_CHECK: granny}
    _, world = prepare(gifts.logic_spec(spec, GIFTS), GIFTS)
    assert [name for name, location in world.locations.items() if location.vanilla == "Blue Potion"] == [
        gifts.GRANNY_CHECK
    ]
    assert gifts.GRANNY_CHECK not in shuffled_locations(world, GIFTS)
    assert granny_checks(world) == []


@pytest.mark.parametrize("shuffle", [("Chest",), ("Chest", *gifts.GIFT_TYPES)])
def test_forty_token_reward_contributes_twenty_bombchus_only_with_gifts(shuffle):
    settings, world = prepare(load_spec(), Settings(shuffle=shuffle))
    name = "Kak 40 Gold Skulltula Reward"
    assert world.locations[name].vanilla == "Bombchus (20)"
    assert (name in shuffled_locations(world, settings)) is ("NPC" in shuffle)
