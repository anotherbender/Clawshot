"""Native static hints preserve unrelated messages and the existing purchase/grant contracts."""

import copy

import pytest

from clawshot.formats import evfl, msbt, sarc, zsdic
from clawshot.generate import Seed, Settings, prepare
from clawshot.generate import hints as stone_hints
from clawshot.generate.rewards import catalog
from clawshot.patch import gifts, items, scrubs, text
from clawshot.world.load import load_spec

pytestmark = pytest.mark.dump


def visible(parts):
    return "".join(part if isinstance(part, str) else " " if part == text.PAGE_BREAK else "" for part in parts).replace(
        "\n", " "
    )


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


def test_altar_and_ganondorf_name_regions_not_checks_or_junk_in_every_language(romfs):
    settings, world = prepare(load_spec(), Settings(dungeon_rewards=True, bridge="medallions", bridge_count=4))
    slots = catalog()["slots"]
    rewards = [slot["item"] for slot in slots.values()]
    placements = {name: rewards[(i + 1) % len(rewards)] for i, name in enumerate(slots)}
    placements["Kak 20 Gold Skulltula Reward"] = "Light Arrows"
    placements["Kak 10 Gold Skulltula Reward"] = "Rupees (20)"
    seed = Seed(world, 20200121, settings, placements, list(placements), [])
    table = items.load()
    changes = text.static_hint_changes(romfs, seed, table)
    names = text.item_names(romfs, rewards, table)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    assert set(changes) == {text.archive_path(lang) for lang in text.languages(romfs)}
    for path, transform in changes.items():
        raw = dictionaries.decompress(path, (romfs / path).read_bytes())
        before, after = sarc.read(raw), sarc.read(transform(raw))
        altar = msbt.read(after[text.ALTAR_MESSAGES])
        parts = altar.messages[text.ALTAR_LABEL]
        shown = visible(parts)
        for source in slots:
            area = stone_hints.area_name(stone_hints.hint_area(world, world.locations[source].region))
            assert f"{names[placements[source]]}: {area}." in shown
        assert "4 medallions" in shown and "own all three Spiritual Stones" in shown
        assert "Rupees" not in shown and "Kak 20" not in shown
        original = msbt.read(before[text.ALTAR_MESSAGES])
        altar.messages[text.ALTAR_LABEL] = original.messages[text.ALTAR_LABEL]
        assert altar == original
        after[text.ALTAR_MESSAGES] = before[text.ALTAR_MESSAGES]

        ganondorf = msbt.read(after[text.GANONDORF_MESSAGES])
        clue = ganondorf.messages[text.GANONDORF_LABEL]
        assert "Kakariko Village" in msbt.plain(clue).replace("\n", " ")
        assert text.PAGE_BREAK not in clue  # fixed native subtitle duration: no third row or second page
        rows = msbt.plain(clue).split("\n")
        assert len(rows) <= 2 and max(map(len, rows)) <= 35
        original = msbt.read(before[text.GANONDORF_MESSAGES])
        ganondorf.messages[text.GANONDORF_LABEL] = original.messages[text.GANONDORF_LABEL]
        assert ganondorf == original
        after[text.GANONDORF_MESSAGES] = before[text.GANONDORF_MESSAGES]
        assert after == before


def test_all_freed_sons_name_the_seed_rewards_without_native_item_advice(romfs):
    chosen = {10: "Rupees (20)", 20: "Boomerang", 30: "Megaton Hammer", 40: "Hookshot", 50: "Heart Container"}
    table = items.load()
    changes = gifts.skulltula_hint_changes(
        romfs, {f"Kak {count} Gold Skulltula Reward": table.actor(item) for count, item in chosen.items()}
    )
    names = text.item_names(romfs, chosen.values(), table)
    expected = {
        "Npc_SkullDad": ("Talk_28", "Talk_23", "Talk_24", "Talk_25", "Talk_26"),
        "Npc_Hylia_029": ("Talk_12", "Talk_13", "Talk_14", "Talk_15", "Talk_16", "Talk_17", "Talk_18", "Talk_19"),
        "Npc_Hylia_028": (
            "Talk_11",
            "Talk_14",
            "Talk_08",
            "Talk_02",
            "Talk_03",
            "Talk_01",
            "Talk_09",
            "Talk_10",
            "Talk_07",
        ),
        "Npc_Hylia_027": ("Talk_06", "Talk_14", "Talk_05", "Talk_03", "Talk_04"),
        "Npc_Hylia_026": ("Talk_09", "Talk_14", "Talk_06", "Talk_05", "Talk_12", "Talk_10"),
        "Npc_Hylia_025": ("Talk_00", "Talk_01", "Talk_11"),
    }
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for path, transform in changes.items():
        raw = dictionaries.decompress(path, (romfs / path).read_bytes())
        before, after = sarc.read(raw), sarc.read(transform(raw))
        documents = {actor: msbt.read(after[f"EventFlowMsg/{actor}.msbt"]) for actor in expected}
        for count, actor, label in (
            (10, "Npc_Hylia_029", "Talk_13"),
            (20, "Npc_Hylia_028", "Talk_08"),
            (30, "Npc_Hylia_029", "Talk_15"),
            (30, "Npc_Hylia_027", "Talk_05"),
            (40, "Npc_Hylia_026", "Talk_06"),
            (50, "Npc_Hylia_025", "Talk_00"),
        ):
            shown = visible(documents[actor].messages[label])
            assert names[chosen[count]] in shown
            assert not any(stale in shown for stale in ("500", "1,000", "Bombchu", "Echo Gem", "equip it"))
        assert names[chosen[10]] in visible(documents["Npc_Hylia_029"].messages["Talk_17"])
        assert names[chosen[30]] in visible(documents["Npc_Hylia_029"].messages["Talk_17"])
        for actor, labels in expected.items():
            file = f"EventFlowMsg/{actor}.msbt"
            original, changed = msbt.read(before[file]), documents[actor]
            for label in labels:
                assert text.keep_style(changed.messages[label], []) == text.keep_style(original.messages[label], [])
                changed.messages[label] = original.messages[label]
            assert changed == original
            after[file] = before[file]
        assert after == before


def test_fairy_prerequisite_text_is_gift_only_and_never_redirects_to_death_mountain(romfs):
    settings, world = prepare(load_spec(), Settings())
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    seed = Seed(world, 20200121, settings, {}, [], [])
    assert text.static_hint_changes(romfs, seed, items.load()) == {}
    seed.shuffled.append("DMT Great Fairy Reward")
    assert text.static_hint_changes(romfs, seed, items.load()) == {}
    seed.shuffled.append("HC Great Fairy Reward")
    changes = text.static_hint_changes(romfs, seed, items.load())
    for archive_path, transform in changes.items():
        source = dictionaries.decompress(archive_path, (romfs / archive_path).read_bytes())
        before, after = sarc.read(source), sarc.read(transform(source))
        original, changed = msbt.read(before[text.FAIRY_MESSAGES]), msbt.read(after[text.FAIRY_MESSAGES])
        for label in ("Talk_00", "Talk_01", "Talk_02"):
            shown = visible(changed.messages[label])
            assert "Death Mountain" not in shown
            if label != "Talk_00":
                assert "Din's Fire" in shown
            changed.messages[label] = original.messages[label]
        assert changed == original
        after[text.FAIRY_MESSAGES] = before[text.FAIRY_MESSAGES]
        assert after == before
