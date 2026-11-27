"""Pickup actors are canonical without renaming native shelves or their tracker icons."""

import pytest

from clawshot.census.scan import scan_trees
from clawshot.formats import byml
from clawshot.patch import items, shops
from clawshot.tracker import icons
from clawshot.world import build_world

TUNICS = (
    ("Goron Tunic", "Obj_Armor_Goron", "Shop_Armor_Goron", "Armor_Adult_Goron"),
    ("Zora Tunic", "Obj_Armor_Zora", "Shop_Armor_Zora", "Armor_Adult_Zora"),
)


@pytest.mark.parametrize("item,native,shelf,icon", TUNICS)
def test_tunic_pickup_and_shelf_spellings_reverse_to_the_same_item(item, native, shelf, icon):
    actors = items.load()
    world = build_world({"start": "Root", "goal": "True", "items": {item: {}}, "regions": [{"name": "Root"}]})
    assert actors.actor(item) == native
    for actor in (native, shelf):
        assert actors.item(actor, None, world.items) == item


@pytest.mark.parametrize("item,native,shelf,icon", TUNICS)
def test_native_tunic_shelves_keep_census_shop_and_tracker_identity(item, native, shelf, icon):
    tree = {
        "Actors": [
            {
                "Hash": byml.U64(101),
                "Gyaml": shelf,
                "Translate": [byml.F32(1.0), byml.F32(2.0), byml.F32(3.0)],
                "Dynamic": {"ShopItemIndex": byml.I32(3)},
            }
        ]
    }
    [location] = scan_trees({"Banc/Test/Test_Adult_Static.bcett.byml.zs": tree}, flags=[])
    assert (location.id, location.kind, location.actor, location.vanilla_item, location.shop_slot) == (
        101,
        "shop_slot",
        shelf,
        shelf,
        3,
    )
    assert shops.native_items()[item]["display"] == shelf
    assert icons.icon_id(native) == icons.icon_id(location.actor) == icon
