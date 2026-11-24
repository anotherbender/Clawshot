"""Native bridge actor binding and stow donor, on the read-only supported dump."""

import pytest

from clawshot.census.gifts import _successors, reachable
from clawshot.formats import evfl, zsdic
from clawshot.patch import saria_equipment as saria

pytestmark = pytest.mark.dump


def test_native_stow_action_and_bridge_prop_order(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    donor_path = "Event/EventFlow/Dm_DeathMtTrail_0050.bfevfl.zs"
    donor = evfl.read(dictionaries.decompress(donor_path, (romfs / donor_path).read_bytes())).flowchart
    native = next(event for event in donor.events if event.name == "Event5")
    assert donor.actors[native.actor].actions[native.action] == saria.ACTION
    assert native.params == {"EquipState": 0}
    data = dictionaries.decompress(saria.PATH, (romfs / saria.PATH).read_bytes())
    before = evfl.read(data).flowchart
    after = evfl.read(saria.patch(data)).flowchart
    stow = next(i for i, event in enumerate(after.events) if event.name == saria.EVENT)
    bind = next(i for i, event in enumerate(after.events) if event.name == "Event7")
    assert bind in reachable(after, after.entry_point("ready").main_event)
    seen, pending = set(), [after.entry_point("ready").main_event]
    while pending:
        index = pending.pop()
        if index not in seen and index not in (evfl.NONE, stow):
            seen.add(index)
            pending.extend(_successors(after.events[index]))
    assert bind not in seen, "the native prop must not bind before stowing scheduled equipment"
    assert after.entry_points == before.entry_points
    changed = [old.name for old, new in zip(before.events, after.events, strict=False) if old != new]
    assert changed == ["Event18"]
