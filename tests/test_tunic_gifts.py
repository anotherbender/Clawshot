"""Tunic gifts contribute the same inventory items as shops, with native gift actors."""

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.gifts import Gift
from clawshot.formats import evfl
from clawshot.generate import Settings
from clawshot.generate.fill import allowed
from clawshot.patch import gifts, items
from clawshot.world import build_world


@pytest.mark.parametrize(
    "check,flow,event,item,native",
    [
        ("GC Rolling Goron as Adult", "SageOfFire", "Event18", "Goron Tunic", "Obj_Armor_Goron"),
        ("ZD King Zora Thawed", "SageOfWater", "Event242", "Zora Tunic", "Obj_Armor_Zora"),
    ],
)
def test_tunic_source_is_shuffled_but_its_scene_keeps_the_native_grant(check, flow, event, item, native):
    step = Gift(
        f"{flow}/{event}",
        "npc_gift",
        flow,
        "flow",
        ("Talk",),
        event,
        "Dm_SY_GetInEvent:GetInEvent_NotTurn",
        "ActorName",
        native,
        "",
    )
    definitions = [Definition(step.id, "npc_gift", "", check, native, check)]
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {item: {}, "Boomerang": {}},
            "regions": [{"name": "Root", "locations": {check: {"type": "NPC", "vanilla": item, "rule": "True"}}}],
        }
    )
    actors = items.load()
    rules = gifts.load()
    assert gifts.seed_checks(world, [step], definitions, rules, actors) == [check]
    for target, expected in ((actors.actor(item), native), ("Item_Boomerang", "Item_Boomerang")):
        [change] = gifts.plan({check: target}, [step], definitions, rules)
        chart = evfl.Flowchart(
            flow,
            events=[
                evfl.SubFlowEvent(
                    event, "Dm_SY_GetInEvent", "GetInEvent_NotTurn", 1, {"ActorName": native, "IsNpcEventStarter": True}
                ),
                evfl.ReturnEvent("AfterNativeHandover", 0),
            ],
            entry_points=[evfl.EntryPoint("Talk", 0, [0])],
        )
        gifts.patch_flowchart(chart, flow, [change])
        assert chart.events[0].params == {"ActorName": expected, "IsNpcEventStarter": True}
        assert chart.events[0].next == 1
        assert chart.events[0].entry_point == "GetInEvent_NotTurn"
        assert chart.events[1] == evfl.ReturnEvent("AfterNativeHandover", 0)
        assert change.new_flag is None


@pytest.mark.parametrize("item", ["Goron Tunic", "Zora Tunic"])
def test_a_tunic_added_by_gift_shuffle_keeps_existing_shop_and_chest_destinations(item):
    world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {item: {}},
            "settings": {"native_shop_items": [item]},
            "regions": [
                {
                    "name": "Root",
                    "locations": {
                        "Gift": {"type": "NPC", "vanilla": item, "rule": "True"},
                        "Chest": {"type": "Chest", "vanilla": item, "rule": "True"},
                        "Shelf": {"type": "Shop", "vanilla": item, "rule": "True"},
                    },
                }
            ],
        }
    )
    held = gifts.held_items(world, [item], items.load(), set())
    assert held == {}
    settings = Settings(item_location_types=held)
    for location in ("Gift", "Chest", "Shelf"):
        assert allowed(world, settings, location, item)
