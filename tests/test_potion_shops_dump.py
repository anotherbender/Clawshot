"""The real potion seller's native dialogue hooks cover the full shuffled shop palette."""

import pytest

from clawshot.census.hints import flow_path
from clawshot.formats import evfl, msbt, sarc, zsdic
from clawshot.patch import shops, text

pytestmark = pytest.mark.dump


@pytest.mark.parametrize(
    "language",
    [
        "CNzh",
        "EUde",
        "EUen",
        "EUes",
        "EUfr",
        "EUit",
        "EUnl",
        "EUpl",
        "EUru",
        "JPja",
        "KRko",
        "TWzh",
        "USen",
        "USes",
        "USfr",
        "USpt",
    ],
)
def test_native_nonbottle_sale_dialogue_is_present_in_every_language(romfs, language):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = text.archive_path(language)
    original = dictionaries.decompress(path, (romfs / path).read_bytes())
    before = sarc.read(original)
    after = sarc.read(shops.potion_messages(original))
    native = msbt.read(before[shops.POTION_MESSAGES]).messages
    messages = msbt.read(after[shops.POTION_MESSAGES]).messages
    # Every original bottle line and all other message files survive exactly.
    assert {label: messages[label] for label in native} == native
    assert {p: data for p, data in after.items() if p != shops.POTION_MESSAGES} == {
        p: data for p, data in before.items() if p != shops.POTION_MESSAGES
    }
    # These are the consumer-facing offer, capacity, ownership and no-container paths,
    # not merely a check that the writer emitted its own constant list.
    for label in (
        "Shop_01_Shield_Adult",
        "Shop_03",
        "Shop_04",
        "Shop_05",
        "Shop_06",
        "Shop_08",
        "Shop_09",
        "Shop_09_04",
        "Shop_09_05",
        "Shop_10",
        "Shop_12",
        "Shop_15",
        "Shop_16",
        "Shop_21",
        "Shop_31",
        "Shop_32",
        "Shop_41",
        "Shop_42",
    ):
        assert messages[label], (language, label)
    path = flow_path(romfs, "DisplayShop")
    chart = evfl.read(dictionaries.decompress(path, (romfs / path).read_bytes())).flowchart
    for name in (
        "Event554",
        "Event78",
        "Event98",
        "Event45",
        "Event300",
        "Event301",
        "Event316",
        "Event323",
        "Event324",
        "Event326",
        "Event225",
        "Event227",
        "Event118",
    ):
        event = next(event for event in chart.events if event.name == name)
        label = event.params["MessageId"].split(":")[1]
        assert event.params["ChangeMstxtForActor"] is True
        assert label in messages, (language, name, label)


@pytest.mark.parametrize("shop", shops.POTION_SHOPS)
def test_all_potion_shelves_register_dialogue_for_native_nonbottle_sales(romfs, shop):
    slots = [slot for slot in shops.load() if slot.shop == shop]
    palette = shops.native_items()
    languages = {text.archive_path(language) for language in text.languages(romfs)}
    # Both normal and Alternative Kakariko actors are covered; no slot-local fix.
    for name in dict.fromkeys(slot.location for slot in slots):
        for item in (
            "Deku Shield",
            "Hylian Shield",
            "Goron Tunic",
            "Zora Tunic",
            "Buy Heart",
            "Buy Magic Jar",
            "Buy Arrows (10)",
            "Buy Bombs (5) for 35 Rupees",
            "Buy Deku Seeds (10)",
        ):
            changes = shops.changes(romfs, {name: palette[item]["display"]})
            assert languages <= changes.keys(), (shop, name, item)
    bottle_only = shops.changes(romfs, {slots[0].location: "Shop_Bottle_Bug"})
    assert not languages.intersection(bottle_only)
