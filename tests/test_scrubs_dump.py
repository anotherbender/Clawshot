import copy

import pytest
from test_scrub_shields import OUTCOMES, run
from test_scrubs import guard_destination, restore_offer_guard

from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import evfl, zsdic
from clawshot.patch import bags, scrub_shields, scrubs
from clawshot.patch.items import load
from clawshot.save import murmur3_32


@pytest.mark.dump
def test_once_sales_change_all_copies_and_tiers_but_no_price_or_saved_gate(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    data = dicts.decompress(scrubs.PATH, (romfs / scrubs.PATH).read_bytes())
    before = evfl.read(data)
    placements = {name: "Item_Boomerang" for name in scrubs.SALES}
    after = evfl.read(scrubs.changes(placements)[scrubs.PATH](data))
    restored = copy.deepcopy(after)
    index = {e.name: e for e in restored.flowchart.events}
    for sale in scrubs.SALES.values():
        for name, old in sale.grants:
            assert index[name].params["ActorName"] == "Item_Boomerang"
            index[name].params["ActorName"] = old
        if sale.selection:
            assert index[sale.selection].params["Value"] == "Item_Boomerang"
            index[sale.selection].params["Value"] = "Obj_Heart_Piece"
    restore_offer_guard(restored.flowchart)
    assert restored == before
    gd = read_romfs_byml(romfs, dicts, GAME_DATA_LIST)
    flags = {int(e["Hash"]): e for e in gd["Data"]["Bool"]}
    locations = {loc.id: loc for loc in scan(romfs)}
    for sale in scrubs.SALES.values():
        flag = flags[murmur3_32(sale.flag.encode())]
        assert (int(flag["SaveFileIndex"]), int(flag["ResetTypeValue"])) == (0, 8)
        for actor_id in sale.ids:
            loc = locations[actor_id]
            assert loc.kind == "scrub"
            for path in loc.files:
                tree = read_romfs_byml(romfs, dicts, path)
                actor = next(a for a in tree["Actors"] if int(a["Hash"]) == actor_id)
                entry = actor["Dynamic"]["TalkEventName"]
                settings = read_romfs_byml(romfs, dicts, "RSDB/EventSetting.Product.111.rstbl.byml.zs")
                row = next(r for r in settings if r["__RowId"] == entry)
                assert scrubs.FLOW in row["FlowchartFileName"]
                # Every physical copy still reaches the shared, changed family flow.
                assert any(ep.name == row["EntryPointName"] for ep in after.flowchart.entry_points)
    print(f"four once-sale families / nine actor copies: {len(data)} -> {len(evfl.write(after))} bytes")


@pytest.mark.dump
def test_whole_seed_assigns_one_item_to_every_tier_and_copy_without_changing_prices(romfs, tmp_path):
    from clawshot.generate import Settings
    from clawshot.patch import make_seed, write_seed

    output = make_seed(romfs, 7, Settings(shuffle=("Chest", "Scrub")))
    write_seed(output, romfs, tmp_path / "seed")
    dicts, actors = zsdic.Dictionaries.from_romfs(romfs), load()
    data = dicts.decompress(scrubs.PATH, (romfs / scrubs.PATH).read_bytes())
    written = dicts.decompress(scrubs.PATH, (tmp_path / "seed" / "romfs" / scrubs.PATH).read_bytes())
    before, after = evfl.read(data), evfl.read(written)
    index = {e.name: e for e in after.flowchart.events}
    native = {e.name: e for e in before.flowchart.events}
    assert set(output.seed.shuffled) & scrubs.SALES.keys() == scrubs.SALES.keys()
    for check, sale in scrubs.SALES.items():
        item = actors.actor(output.seed.placements[check])
        for name, old in sale.grants:
            assert index[name].params["ActorName"] == item
            assert index[name].params["Price"] == sale.price
            assert index[name].params["SellerMessageId"] == f"{scrubs.OFFER_FILE}:{scrubs.OFFER_LABELS[check]}"
            index[name].params["ActorName"] = old
            index[name].params["SellerMessageId"] = native[name].params["SellerMessageId"]
        if sale.selection:
            assert index[sale.selection].params["Value"] == item
            index[sale.selection].params["Value"] = "Obj_Heart_Piece"
    restore_offer_guard(after.flowchart)
    assert after == before
    for name in output.seed.shuffled:
        if output.seed.placements[name] in scrubs.CAPACITIES:
            assert name in scrubs.SALES


@pytest.mark.dump
def test_unshuffled_scrubs_guard_every_empty_or_hidden_offer_before_shop_ui(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    data = dicts.decompress(scrubs.PATH, (romfs / scrubs.PATH).read_bytes())
    before = evfl.read(data)
    changed = scrubs.changes({})[scrubs.PATH](data)
    after = evfl.read(changed)
    for incoming in ("Event192", "Event334"):
        for offers in (
            (("Item_Test", True),) * 3,
            (("", False),) * 3,
            (("Item_Test", True), ("", False), ("Item_Test", False)),
        ):
            expected = "Event119" if any(actor and not hidden for actor, hidden in offers) else "Event395"
            assert guard_destination(after.flowchart, incoming, offers) == expected
    restore_offer_guard(after.flowchart)
    assert after == before


def _flow(romfs, dicts, path):
    return evfl.read(dicts.decompress(path, (romfs / path).read_bytes()))


def _successors(event):
    if isinstance(event, (evfl.SwitchEvent, evfl.SubFlowSwitchEvent)):
        return [index for _, index in event.cases]
    if isinstance(event, evfl.ForkEvent):
        return [*event.forks, event.join]
    return [getattr(event, "next", evfl.NONE)]


def _reaches(fc, entry, target):
    """Whether ``entry`` reaches the event at ``target``, entering same-flow sub-calls."""
    todo, seen, entries = [fc.entry_point(entry).main_event], set(), {entry}
    while todo:
        index = todo.pop()
        if index == target:
            return True
        if not 0 <= index < len(fc.events) or index in seen:
            continue
        seen.add(index)
        event = fc.events[index]
        todo.extend(_successors(event))
        if (
            isinstance(event, (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent))
            and event.flowchart in ("", fc.name)
            and event.entry_point not in entries
        ):
            entries.add(event.entry_point)
            todo.append(fc.entry_point(event.entry_point).main_event)
    return False


@pytest.mark.dump
def test_scrub_shield_wait_is_scrub_only_and_ends_for_every_equip_outcome(romfs):
    """The real scrub helper must finish an inventory-only shield receipt, regardless of equipped gear."""
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    native = _flow(romfs, dicts, scrub_shields.PATH)
    fc = native.flowchart
    helper = next(i for i, event in enumerate(fc.events) if event.name == "Event444")
    reaching = {entry.name for entry in fc.entry_points if _reaches(fc, entry.name, helper)}
    assert reaching == {"DekuShield_GetAndEquipCheck", "GetInEvent_NotTurn_2DShop"}
    callers = set()
    for path in sorted((romfs / "Event/EventFlow").glob("*.bfevfl.zs")):
        other = _flow(romfs, dicts, path.relative_to(romfs).as_posix()).flowchart
        for event in other.events if other else ():
            if (
                isinstance(event, (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent))
                and event.flowchart == scrub_shields.FLOW
                and event.entry_point in reaching
            ):
                callers.add(other.name)
    assert callers == {"Enemy_Scrub_Business_Common", "Enemy_Scrub_Business_Dream"}
    for equipped in ({0: "Weapon_Shield_Mirror"}, {}):
        assert run(fc, "Item_Shield_Mirror", equipped) == (None, [("Item_Shield_Mirror", False)])
    data = dicts.decompress(scrub_shields.PATH, (romfs / scrub_shields.PATH).read_bytes())
    after = evfl.read(bags.handover_transform(scrub_shields.transform(data))).flowchart
    for content in ("Item_Shield_Mirror", "TBox_Shield_Deku", "TBox_Shield_Hylian"):
        for equipped, frames in OUTCOMES.values():
            assert run(after, content, equipped) == (frames, [(content, False)])
    restored = evfl.read(scrub_shields.transform(data))
    events = restored.flowchart.events
    add = next(event for event in events if event.name == "Event442")
    wait = next(event for event in events if event.name == "Event513")
    add.next = next(i for i, event in enumerate(events) if event.name == "Event514")
    wait.next = next(i for i, event in enumerate(events) if event.name == "Event509")
    assert restored == native


@pytest.mark.dump
def test_shield_rewards_are_the_pouch_shield_rows(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    rows = read_romfs_byml(romfs, dicts, "RSDB/PouchActorInfo.Product.111.rstbl.byml.zs")
    shields = {row["__RowId"] for row in rows if row.get("PouchCategory") == "Shield"}
    assert shields == scrub_shields.SHIELDS
    table = load()
    assert {item for item, actor in table.actors.items() if actor in shields} == {
        "Deku Shield",
        "Hylian Shield",
        "Mirror Shield",
    }
    # The helper's "Item_Shield_Mirror" check names the pouch row; both ages equip Weapon_Shield_Mirror.
    mirror = next(row for row in rows if row["__RowId"] == "Item_Shield_Mirror")
    for age in ("ChildEquipment", "AdultEquipment"):
        assert mirror[age].startswith("Work/Actor/Weapon_Shield_Mirror.")
