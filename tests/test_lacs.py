"""Native Light Arrows scene is an ordinary Gift, not a Ganon boss-key award."""

import pytest

from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings, prepare
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import gifts
from clawshot.world.load import load_spec


@pytest.mark.dump
@pytest.mark.parametrize("rewards", [False, True])
def test_native_lacs_gift_shuffles_without_changing_trigger_or_story_writes(romfs, rewards):
    spec, settings, step = gifts.seed_setup(
        romfs, load_spec(), Settings(shuffle=("Chest", "Gift"), dungeon_rewards=rewards)
    )
    _, world = prepare(spec, settings)
    name = "ToT Light Arrows Cutscene"
    assert name in shuffled_locations(world, settings)
    assert world.locations[name].vanilla == "Light Arrows"
    placements = {name: location.vanilla for name, location in world.locations.items()}
    baseline = step(placements)
    placements[name] = "Boomerang"
    changes = step(placements)
    path = "Event/EventFlow/Dm_TimeTemple_0130.bfevfl.zs"
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    raw = dictionaries.decompress(path, (romfs / path).read_bytes())
    before = evfl.read(raw)
    after = evfl.read(changes[path](raw))
    grant = next(event for event in after.flowchart.events if event.name == "Event85")
    assert (grant.flowchart, grant.entry_point, grant.params) == (
        "GetPouchContent",
        "GetPouchContentByActorName",
        {"ActorName": "Item_Boomerang"},
    )
    grant.params["ActorName"] = "Item_Arrow_Light"
    assert after == before  # Every branch, binding, history/flag write and timeline stays native.
    assert "Event/EventFlow/AllSage.bfevfl.zs" not in changes
    # Identity merchants normalize their saved checks; LACS adds no state beyond that baseline.
    game_data = gifts.GAME_DATA_LIST
    raw = dictionaries.decompress(game_data, (romfs / game_data).read_bytes())
    assert changes[game_data](raw) == baseline[game_data](raw)
