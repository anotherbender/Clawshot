"""Map/compass gift credit follows the grant and preserves its native continuation."""

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.gifts import Gift
from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import allowed
from clawshot.patch import gifts
from clawshot.patch.items import ItemActors
from clawshot.patch.key_targets import DungeonGrant
from clawshot.world import load_spec


@pytest.mark.parametrize("family", ["Map", "Compass"])
def test_dungeon_credit_is_after_the_gift_and_before_its_completion(family):
    name, flow = "Temple Lesson", "SyntheticLesson"
    path = "Event/EventFlow/SyntheticLesson.bfevfl.zs"
    actors = [evfl.Actor("GameDataActor", actions=[gifts.SET_ACTION])]
    chart = evfl.Flowchart(
        flow,
        actors=actors,
        events=[
            evfl.SubFlowEvent("Grant", "GetPouchContent", "GetPouchContentByActorName", 1, {"ActorName": "Item_Song"}),
            evfl.ActionEvent("Complete", 0, 0, params={"GameDataName": "LessonComplete", "Index": -1, "Value": True}),
        ],
        entry_points=[evfl.EntryPoint("Lesson", 0, [0])],
    )
    gift = Gift(
        f"{flow}/Grant",
        "npc_gift",
        flow,
        path,
        ("Lesson",),
        "Grant",
        "GetPouchContent:GetPouchContentByActorName",
        "ActorName",
        "Item_Song",
        "",
    )
    definition = Definition(gift.id, "npc_gift", "", name, "Item_Song", name)
    item = f"{family} (Temple)"
    step = gifts.seed_step(
        [name],
        [gift],
        [definition],
        {name: gifts.Rule(name, gifts.SWAP)},
        ItemActors({"Song": "Item_Song", item: f"Item_Dungeon_{family}"}, {}, {}),
        {name: "Song"},
        {flow: path},
        dungeon_grants={(name, item): DungeonGrant("Temple", family)},
    )
    original = evfl.write(evfl.EventFlowFile(flow, flowchart=chart))
    result = evfl.read(step({name: item})[path](original)).flowchart
    grant = result.events[0]
    assert grant.params["ActorName"] == f"Item_Dungeon_{family}"
    credit = result.events[grant.next]
    assert result.actors[credit.actor].name == "GameDataActor"
    assert result.actors[credit.actor].actions[credit.action] == gifts.SET_ACTION
    assert credit.params == {"GameDataName": f"DungeonInfo.Temple.IsGet{family}", "Index": -1, "Value": True}
    assert credit.next == 1
    assert result.events[credit.next].params["GameDataName"] == "LessonComplete"
    assert step({name: "Song"}) == {}


@pytest.mark.dump
@pytest.mark.parametrize("family", ["Map", "Compass"])
def test_production_ice_lesson_credits_its_dungeon_but_does_not_lift_the_hold(romfs, family):
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), Settings(shuffle=("Chest", "Gift"), songs="anywhere"))
    _, world = prepare(spec, settings)
    name = "Sheik in Ice Cavern"
    item = f"{family} (Ice Cavern)"
    assert not allowed(world, settings, name, item)
    placements = {name: location.vanilla for name, location in world.locations.items()}
    placements[name] = item
    transforms = step(placements)
    path = "Event/EventFlow/Dm_MelodyGet_Water.bfevfl.zs"
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = dictionaries.decompress(path, (romfs / path).read_bytes())
    before = evfl.read(original).flowchart
    result = evfl.read(transforms[path](original)).flowchart
    old = next(event for event in before.events if event.name == "Event29")
    grant = next(event for event in result.events if event.name == "Event29")
    assert grant.params["ActorName"] == f"Item_Dungeon_{family}"
    credit = result.events[grant.next]
    assert credit.params == {"GameDataName": f"DungeonInfo.IceCavern.IsGet{family}", "Index": -1, "Value": True}
    assert result.actors[credit.actor].name == "GameDataActor"
    assert result.actors[credit.actor].actions[credit.action] == gifts.SET_ACTION
    assert credit.next == old.next
    assert not any(
        (event.params or {}).get("GameDataName") == f"DungeonInfo.ForestTemple.IsGet{family}"
        for event in result.events
        if isinstance(event, evfl.ActionEvent)
    )
