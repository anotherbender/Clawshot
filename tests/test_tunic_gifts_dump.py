"""Native grants, pouch identity and gift setup for the two tunic checks."""

import pytest

from clawshot.census import definitions
from clawshot.census.gifts import scan_gifts
from clawshot.formats import byml, evfl, zsdic
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import allowed, shuffled_locations
from clawshot.patch import gifts, items, shops
from clawshot.world.load import load_spec

pytestmark = pytest.mark.dump
TUNICS = (
    ("GC Rolling Goron as Adult", "Goron Tunic", "SageOfFire", "Event18", "GetInEvent_NotTurn"),
    ("ZD King Zora Thawed", "Zora Tunic", "SageOfWater", "Event242", "GetInEvent_NotTurn_PosCamera"),
)


def test_tunic_shop_and_native_gift_actors_credit_identical_pouch_equipment(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = shops.POUCH_TABLE
    rows = {row["__RowId"]: row for row in byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))}
    for item in ("Goron Tunic", "Zora Tunic"):
        shop, native = shops.native_items()[item]["display"], items.load().actor(item)
        assert {k: v for k, v in rows[shop].items() if k != "__RowId"} == {
            k: v for k, v in rows[native].items() if k != "__RowId"
        }


def test_production_gift_setup_keeps_both_tunic_checks_and_shop_destinations(romfs):
    spec, settings, step = gifts.seed_setup(
        romfs, load_spec(), Settings(shuffle=("Chest", "Shop", "Gift"), shop_prices="affordable")
    )
    _, world = prepare(spec, settings)
    shuffled = shuffled_locations(world, settings)
    placements = {name: location.vanilla for name, location in world.locations.items()}
    for name, item, *_ in TUNICS:
        assert name in shuffled
        assert world.locations[name].keep_vanilla is None
        assert allowed(world, settings, "Kak Potion Shop Item 3", item)
        placements[name] = "Boomerang"
    transforms = step(placements)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for _, _, flow, event_name, wrapper in TUNICS:
        path = next(path for path in transforms if path.endswith(f"/{flow}.bfevfl.zs"))
        original = dictionaries.decompress(path, (romfs / path).read_bytes())
        before = evfl.read(original).flowchart
        after = evfl.read(transforms[path](original)).flowchart
        grant = next(event for event in after.events if event.name == event_name)
        assert isinstance(grant, evfl.SubFlowEvent)
        assert (grant.flowchart, grant.entry_point, grant.params["ActorName"]) == (
            "Dm_SY_GetInEvent",
            wrapper,
            "Item_Boomerang",
        )
        native = next(event for event in before.events if event.name == event_name)
        assert grant.next == native.next
        # No new scene, window, reaction or wait is inserted around the native grant.
        assert after.entry_points == before.entry_points
        assert len(after.events) == len(before.events)


@pytest.mark.parametrize("target", ["Goron Tunic", "Zora Tunic"])
def test_a_shuffled_tunic_uses_its_native_obj_actor_at_either_gift(romfs, target):
    census = scan_gifts(romfs)
    actors = items.load()
    changes = gifts.plan({name: actors.actor(target) for name, *_ in TUNICS}, census, definitions.load(), gifts.load())
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for change in changes:
        [grant] = change.steps
        transform = gifts.file_changes([change], {grant.flow: grant.file})[grant.file]
        raw = dictionaries.decompress(grant.file, (romfs / grant.file).read_bytes())
        chart = evfl.read(transform(raw)).flowchart
        event = next(event for event in chart.events if event.name == grant.event)
        assert event.params["ActorName"] == "Obj_Armor_" + ("Goron" if target == "Goron Tunic" else "Zora")
