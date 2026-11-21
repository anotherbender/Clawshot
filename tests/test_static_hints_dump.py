"""Native static hints preserve unrelated messages and the existing purchase/grant contracts."""

import copy

import pytest

from clawshot.formats import evfl, msbt, sarc, zsdic
from clawshot.patch import items, scrubs, text

pytestmark = pytest.mark.dump


def test_scrub_offers_distinguish_shared_heart_sellers_and_keep_purchase_gates(romfs):
    placements = {
        "HF Deku Scrub Grotto": "Boomerang",
        "DMC Deku Scrub": "Megaton Hammer",
        "LW Deku Scrub Near Bridge": "Rupees (20)",
        "LW Deku Scrub Grotto Front": "Deku Nut Capacity",
    }
    table = items.load()
    prices = {name: 17 for name in placements}
    changes = text.scrub_hint_changes(romfs, placements, table, prices)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    base = scrubs.changes({name: table.actor(item) for name, item in placements.items()}, prices=prices)
    source = dictionaries.decompress(scrubs.PATH, (romfs / scrubs.PATH).read_bytes())
    prior = evfl.read(base[scrubs.PATH](source))
    changed = evfl.read(changes[scrubs.PATH](evfl.write(prior)))
    expected = copy.deepcopy(prior)
    by_name = {event.name: event for event in changed.flowchart.events}
    for check, sale in scrubs.SALES.items():
        for event_name, _ in sale.grants:
            old = next(event for event in expected.flowchart.events if event.name == event_name)
            new = by_name[event_name]
            assert new.params["ActorName"] == table.actor(placements[check])
            assert new.params["Price"] == 17
            assert new.params["SellerMessageId"] == f"{scrubs.OFFER_FILE}:{scrubs.OFFER_LABELS[check]}"
            new.params["SellerMessageId"] = old.params["SellerMessageId"]
    assert changed == expected  # branches, payment, refusal, completion and grant routing stay intact
    names = text.item_names(romfs, placements.values(), table)
    file = f"{scrubs.OFFER_FILE}.msbt"
    assert set(changes) == {scrubs.PATH, *(text.archive_path(lang) for lang in text.languages(romfs))}
    for language in text.languages(romfs):
        path = text.archive_path(language)
        raw = dictionaries.decompress(path, (romfs / path).read_bytes())
        original, result = sarc.read(raw), sarc.read(changes[path](raw))
        old, new = msbt.read(original[file]), msbt.read(result[file])
        assert set(new.messages) - old.messages.keys() == set(scrubs.OFFER_LABELS.values())
        for check, item in placements.items():
            parts = new.messages.pop(scrubs.OFFER_LABELS[check])
            visible = msbt.plain(parts).replace("\n", " ")
            assert names[item] in visible and "17 rupees" in visible
            assert "Piece of Heart" not in visible
        assert new == old
        result[file] = original[file]
        assert result == original


def test_no_scrub_preview_resources_when_no_once_sales_are_selected(tmp_path):
    assert text.scrub_hint_changes(tmp_path, {"unrelated chest": "Boomerang"}, items.load(), {}) == {}
