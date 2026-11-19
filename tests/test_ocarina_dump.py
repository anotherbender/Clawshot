"""The real grant routes retain ownership and continuation while the selected instrument stays monotone."""

import copy

import pytest
from test_ocarina import run, state

from clawshot.census import definitions
from clawshot.census.gifts import scan_gifts
from clawshot.formats import evfl, zsdic
from clawshot.patch import bags, gifts, ocarina
from clawshot.patch.keys import flow_path


@pytest.fixture(scope="module")
def native_context(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    prior = bags.changes(romfs)
    changes = ocarina.changes(romfs, prior_changes=[prior])

    def read(path):
        data = dictionaries.decompress(path, (romfs / path).read_bytes())
        if path in prior:
            data = prior[path](data)
        return data

    pouch_path = flow_path("GetPouchContent")
    pouch = evfl.read(changes[pouch_path](read(pouch_path))).flowchart
    cases = []
    # Audit every literal Fairy and every native positive argument-driven
    # receipt with a current message target, not a hand-maintained event list.
    for path in sorted((romfs / "Event/EventFlow").glob("*.bfevfl.zs")):
        relative = path.relative_to(romfs).as_posix()
        data = read(relative)
        original = evfl.read(data).flowchart
        if original is None:
            continue
        targets = []
        for index, event in enumerate(original.events):
            if not isinstance(event, evfl.ActionEvent) or not event.params:
                continue
            actor = original.actors[event.actor]
            if actor.name != "PouchSystemActor" or actor.actions[event.action] != "EventTriggerAddOrRemovePouchContent":
                continue
            content, amount = event.params.get("Actor"), event.params.get("Num")
            if (
                type(amount) is int
                and amount > 0
                and (
                    content == ocarina.FAIRY
                    or isinstance(content, evfl.Argument)
                    and event.params.get("IsSetMessageTargetActorName") is True
                )
            ):
                targets.append(index)
        if targets:
            changed = evfl.read(changes[relative](data)).flowchart if relative in changes else original
            cases.append((original, changed, targets))
    return pouch, cases


@pytest.mark.dump
@pytest.mark.parametrize("time_owned", [False, True])
@pytest.mark.parametrize("buffered", [False, True])
def test_every_native_fairy_capable_receipt_keeps_inventory_and_selects_the_highest_owned_instrument(
    native_context, time_owned, buffered
):
    pouch, cases = native_context
    for original, changed, targets in cases:
        for target in targets:
            before = state(time=int(time_owned), historical=time_owned, selected=ocarina.TIME if time_owned else "")
            after = copy.deepcopy(before)
            onward = original.events[target].next
            native_trace = run(
                {original.name: original}, original, before, start=target, stop=onward, buffered=buffered
            )
            charts = {"GetPouchContent": pouch, changed.name: changed}
            trace = run(charts, changed, after, start=target, stop=onward, buffered=buffered)
            assert after["stock"] == before["stock"], (original.name, original.events[target].name)
            assert after["flags"] == before["flags"]
            assert [row for row in trace if row[0] == "add"] == native_trace
            expected = ocarina.TIME if time_owned else ocarina.FAIRY
            assert after["strings"][ocarina.EQUIPPED] == after["live"] == expected


@pytest.mark.dump
def test_fairy_moved_to_a_direct_time_source_is_protected_after_gift_rewrites(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    moves = gifts.plan(
        {"LW Gift from Saria": ocarina.TIME, "HF Ocarina of Time Item": ocarina.FAIRY},
        scan_gifts(romfs),
        definitions.load(),
        gifts.load(),
    )
    files = {name: flow_path(name) for name in gifts.flows_changed(moves)}
    gift_changes = gifts.file_changes(moves, files)
    prior = [gift_changes, bags.changes(romfs)]
    transforms = ocarina.changes(romfs, prior_changes=prior)

    def read(path):
        data = dictionaries.decompress(path, (romfs / path).read_bytes())
        for changes in prior:
            if path in changes:
                data = changes[path](data)
        return data

    pouch_path = flow_path("GetPouchContent")
    pouch = evfl.read(transforms[pouch_path](read(pouch_path))).flowchart
    path = flow_path("Dm_MelodyGet_Time")
    data = read(path)
    before = evfl.read(data).flowchart
    after = evfl.read(transforms[path](data)).flowchart
    target = next(index for index, event in enumerate(before.events) if event.name == "Event70")
    native_state, patched_state = state(), state()
    baseline = run({before.name: before}, before, native_state, start=target, stop=before.events[target].next)
    trace = run(
        {"GetPouchContent": pouch, after.name: after},
        after,
        patched_state,
        start=target,
        stop=before.events[target].next,
    )
    assert patched_state["stock"] == native_state["stock"]
    assert patched_state["flags"] == native_state["flags"]
    assert [row for row in trace if row[0] == "add"] == baseline
    assert patched_state["live"] == ocarina.TIME
    assert flow_path("Dm_Kokiri_0155") not in transforms
