"""Ocarinas at show-item hand-overs and scrubs get the ocarina get model (ocarina-song-drops-everywhere, O6).

Synthetic worlds only: which gift steps create the item actor is decided by ``gifts.restrict_spec`` (the same
source that applies ``[hand_over]``), and ``getitem.get_model_ocarinas`` reads that mark from the world.
"""

import pytest

from clawshot.census.gifts import DIRECT, Gift
from clawshot.patch import getitem, gifts
from clawshot.patch.items import ItemActors
from clawshot.world.load import WorldError, build_world

HAND_OVER = "Dm_SY_GetInEvent:GetInEvent_NotTurn_NotNpc"
POUCH = "GetPouchContent:GetPouchContentByActorName"
ACTORS = ItemActors(
    actors={"Fairy Ocarina": getitem.FAIRY, "Ocarina of Time": getitem.TIME, "Bow": "Item_Bow"}, sources={}
)


def gift_step(call):
    return Gift("Test/Event0", "npc_gift", "Test", "Test.bfevfl.zs", ("Talk",), "Event0", call, "Actor", "", "")


def world():
    places = {
        "Chest": {"type": "Chest", "vanilla": "Bow", "rule": "True"},
        "Hand Over": {"type": "NPC", "vanilla": "Bow", "rule": "True"},
        "Story Grant": {"type": "NPC", "vanilla": "Bow", "rule": "True"},
        "Pouch Scene": {"type": "Song", "vanilla": "Bow", "rule": "True"},
        "Sale": {"type": "Scrub", "vanilla": "Bow", "rule": "True"},
        "Grotto Sale": {"type": "GrottoScrub", "vanilla": "Bow", "rule": "True"},
        "Held Gift": {"type": "NPC", "vanilla": "Bow", "rule": "True"},
    }
    spec = {
        "start": "Root",
        "goal": "True",
        "items": {"Fairy Ocarina": {}, "Ocarina of Time": {}, "Bow": {}},
        "regions": [{"name": "Root", "locations": places}],
        "locations": {name: {"type": info["type"]} for name, info in places.items()},
    }
    steps = {
        "Hand Over": (gift_step(HAND_OVER),),
        "Story Grant": (gift_step(DIRECT),),
        "Pouch Scene": (gift_step(POUCH),),
        "Held Gift": (gift_step(HAND_OVER),),
    }
    shuffled = ["Hand Over", "Story Grant", "Pouch Scene"]
    return build_world(gifts.restrict_spec(spec, shuffled, steps))


def test_restrict_spec_marks_the_locations_whose_grant_creates_the_item_actor():
    marked = {name for name, location in world().locations.items() if location.hand_over}
    # Shuffled show-item hand-overs and every scrub sale; not direct or GetPouchContent grants, chests, or gifts that
    # stay vanilla.
    assert marked == {"Hand Over", "Sale", "Grotto Sale"}


def test_hand_over_must_be_a_boolean():
    spec = {
        "start": "Root",
        "goal": "True",
        "items": {"Bow": {}},
        "regions": [{"name": "Root", "locations": {"Gift": {"type": "NPC", "vanilla": "Bow", "rule": "True"}}}],
        "locations": {"Gift": {"hand_over": "yes"}},
    }
    with pytest.raises(WorldError, match="hand_over"):
        build_world(spec)


@pytest.mark.parametrize("item", ["Fairy Ocarina", "Ocarina of Time"])
@pytest.mark.parametrize("place", ["Hand Over", "Sale", "Grotto Sale", "Chest"])
def test_an_ocarina_at_a_chest_hand_over_or_scrub_asks_for_the_get_model(item, place):
    placements = {name: "Bow" for name in world().locations}
    placements[place] = item
    assert getitem.get_model_ocarinas(placements, world(), ACTORS) == [place]


@pytest.mark.parametrize("item", ["Fairy Ocarina", "Ocarina of Time"])
@pytest.mark.parametrize("place", ["Story Grant", "Pouch Scene"])
def test_an_ocarina_only_at_a_direct_or_pouch_grant_needs_no_get_model(item, place):
    placements = {name: "Bow" for name in world().locations}
    placements[place] = item
    assert getitem.get_model_ocarinas(placements, world(), ACTORS) == []


def test_no_ocarina_at_any_such_location_needs_no_get_model():
    placements = {name: "Bow" for name in world().locations}
    assert getitem.get_model_ocarinas(placements, world(), ACTORS) == []


def test_every_ocarina_location_is_reported_in_world_order():
    placements = {name: "Bow" for name in world().locations}
    placements |= {"Sale": "Fairy Ocarina", "Chest": "Ocarina of Time"}
    assert getitem.get_model_ocarinas(placements, world(), ACTORS) == ["Chest", "Sale"]


def test_an_empty_hand_over_list_still_marks_and_loads(monkeypatch):
    from clawshot.settings import CATALOG

    monkeypatch.setitem(CATALOG, "hand_over", {**CATALOG["hand_over"], "excluded_items": []})
    locations = world().locations
    assert {name for name, location in locations.items() if location.hand_over} == {"Hand Over", "Sale", "Grotto Sale"}
    assert all(location.excluded_items == () for location in locations.values())


@pytest.mark.parametrize(
    "shuffle, expected",
    [
        (("Chest", "Gift"), True),
        (("Gift",), True),  # hand-overs alone show the ocarina's item actor
        (("NPC", "Scrub"), True),
        (("Chest", "Scrub"), False),  # no Gift kind: the ocarinas stay at their story places
        ((), False),
    ],
)
def test_the_get_model_runs_whenever_an_ocarina_can_show_its_item_actor(shuffle, expected):
    """Wider than PR #41's ``chest_ocarinas_possible`` (Chest and Gift): hand-overs and scrub sales show the item
    actor too, and without the get model a hand-over crashed (R11, run 4.1)."""
    assert getitem.shown_ocarinas_possible(shuffle) is expected
    if expected and "Chest" in shuffle:
        assert getitem.chest_ocarinas_possible(shuffle)
