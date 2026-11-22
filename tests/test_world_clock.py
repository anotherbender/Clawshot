"""The native story clock in logic: it runs only with Impa's send-off AND the Hyrule Field arrival.

Native predicate: work/r16-time/clock-full-predicate-findings.md. 'Met Child Zelda' models the send-off history,
'Field Owl Arrival' the saved arrival flag (the owl, or its restore at the send-off, which lands in the field).
'Time Flows' and both early Doors read the pair; closed's Door keeps its native item gate.
"""

from dataclasses import replace

import pytest

from clawshot.generate import Settings, prepare
from clawshot.generate.fill import return_guarantee_conflict
from clawshot.patch import gifts
from clawshot.world import ADULT, CHILD, Search, build_world, load_spec
from clawshot.world.rules import ALL_TIMES

ARRIVAL = "Field Owl Arrival"
SENDOFF = "Met Child Zelda"
HISTORIES = [
    pytest.param({}, id="neither"),
    pytest.param({ARRIVAL: 1}, id="arrival-only"),
    pytest.param({SENDOFF: 1}, id="sendoff-only"),
    pytest.param({ARRIVAL: 1, SENDOFF: 1}, id="both"),
]
# An early door under the adult-return guarantee needs movable gifts and songs (fill.return_guarantee_conflict).
GIFTS = ("Chest", *gifts.GIFT_TYPES)


@pytest.fixture(scope="module")
def worlds():
    spec = load_spec()
    # Hyrule Field: the child field route; Temple of Time: the child Prelude landing, off the field route.
    return {start: build_world({**spec, "start": start}) for start in ("Hyrule Field", "Temple of Time")}


@pytest.mark.parametrize("age", [CHILD, ADULT])
@pytest.mark.parametrize("history", HISTORIES)
def test_time_flows_needs_both_saved_clock_flags(worlds, history, age):
    world = worlds["Hyrule Field"]
    time_flows = next(event for event in world.regions["HC Garden"].events if event.name == "Time Flows")
    expected = age == CHILD and bool(history.get(ARRIVAL)) and bool(history.get(SENDOFF))
    assert time_flows.rule(history, age, ALL_TIMES) is expected, {"counts": history, "age": age}


def test_field_arrival_comes_before_zelda_without_items_and_night_waits_for_the_sendoff(worlds):
    world = worlds["Hyrule Field"]
    # A child night check with no other gate (Richard also needs the Kakariko gate opened, round 21).
    night = world.locations["Market Night Balcony Wonderitem 1"]
    search = Search(world)
    assert search.holds(ARRIVAL)  # the child field route alone: no Forest completion, no optional item
    assert not search.holds(SENDOFF)
    assert not search.holds("Time Flows")
    assert not search.can_access(night, CHILD)
    search.collect("Weird Egg")
    assert not search.holds(SENDOFF)  # Impa's send-off follows her lesson, which needs Link's own Ocarina
    search.collect("Fairy Ocarina")
    assert search.holds(SENDOFF) and search.holds("Time Flows")
    assert search.can_access(night, CHILD)


def test_a_child_meeting_zelda_off_the_field_route_still_gets_the_arrival(worlds):
    """The send-off itself lands child Link in Hyrule Field, so no route holds the send-off without the arrival."""
    search = Search(worlds["Temple of Time"], ["Weird Egg", "Fairy Ocarina"])
    assert search.holds(SENDOFF)
    assert search.holds(ARRIVAL)
    assert search.holds("Time Flows")


@pytest.mark.parametrize("mode", ["open", "song_only"])
def test_an_early_pull_before_the_field_arrival_cannot_be_returned_from(mode):
    """The arrival is child-only history: adult Link cannot earn it after the pull, so the generator's early first
    pull must already hold it, as the physical Door does."""
    settings, world = prepare(load_spec(), Settings(shuffle=GIFTS, door_of_time=mode))
    everything = [name for name, item in world.items.items() if item.type not in ("Event", "Drop")]
    adult = Search.adult_after_pull(world, everything)
    assert adult.can_reach("Hyrule Field", ADULT)  # adult Link stands in the field, yet cannot earn the arrival
    assert not adult.holds(ARRIVAL)
    kit = world.settings["age_return_fill_inventory"]
    before_arrival = {name: count for name, count in kit.items() if name != ARRIVAL}
    pre_arrival = replace(world, settings={**world.settings, "age_return_fill_inventory": before_arrival})
    assert return_guarantee_conflict(pre_arrival, settings), {"mode": mode, "kit": before_arrival}
