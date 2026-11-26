"""Talon's Cucco game presentation on the read-only supported dump: the traced native shapes still hold."""

import pytest

from clawshot.census import definitions
from clawshot.census.gifts import reachable, scan_gifts
from clawshot.formats import byml, evfl, msbt, sarc, zsdic
from clawshot.patch import gifts, talon, text

pytestmark = pytest.mark.dump


def _read(romfs, dictionaries, path):
    return dictionaries.decompress(path, (romfs / path).read_bytes())


def _live(fc):
    return {fc.events[i].name for entry in fc.entry_points for i in reachable(fc, entry.main_event)}


def test_flow_after_the_gift_swap_drops_only_the_prop_beat_and_recap_line(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    changes = gifts.plan({talon.CHECK: "Item_Boomerang"}, scan_gifts(romfs), definitions.load(), gifts.load())
    swapped = gifts.flow_transform(talon.FLOW, changes)(_read(romfs, dictionaries, talon.FLOW_PATH))
    before, after = evfl.read(swapped).flowchart, evfl.read(talon.patch_flow(swapped)).flowchart
    changed = [old.name for old, new in zip(before.events, after.events, strict=True) if old != new]
    assert changed == [talon.RECENT, talon.RECAP_GATE]
    assert (after.actors, after.entry_points) == (before.actors, before.entry_points)
    assert _live(after) == _live(before) - set(talon.SKIPPED)
    assert set(talon.SKIPPED) <= _live(before)


def test_prize_lines_and_the_prop_belong_to_talons_flow_alone(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    needles = [f"{talon.TALON}:{label}".encode() for label in talon.USERS]
    needles += [talon.PROP.encode(), talon.PROP_NAME.encode()]
    found = {}
    for path in sorted((romfs / "Event/EventFlow").glob("*.bfevfl.zs")):
        relative = path.relative_to(romfs).as_posix()
        data = dictionaries.decompress(relative, path.read_bytes())
        for needle in needles:
            if needle in data:
                found.setdefault(needle, []).append(relative)
    assert found == {needle: [talon.FLOW_PATH] for needle in needles}


def test_the_milk_prop_and_only_its_reference_are_removed(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    native = _read(romfs, dictionaries, talon.BANC_PATH)
    before, after = byml.read(native), byml.read(talon.patch_banc(native))
    host = {a["Hash"]: a for a in after["Actors"]}[talon.TALON_HASH]
    old_host = {a["Hash"]: a for a in before["Actors"]}[talon.TALON_HASH]
    assert len(after["Actors"]) == len(before["Actors"]) - 1
    assert host["Links"] == [link for link in old_host["Links"] if link["Dst"] != talon.PROP_HASH]
    assert len(host["Links"]) == len(old_host["Links"]) - 1
    others = [a for a in before["Actors"] if a["Hash"] not in (talon.PROP_HASH, talon.TALON_HASH)]
    assert [a for a in after["Actors"] if a["Hash"] != talon.TALON_HASH] == others
    assert {k: v for k, v in after.items() if k != "Actors"} == {k: v for k, v in before.items() if k != "Actors"}


def test_native_english_advertises_milk_and_every_language_takes_the_lines(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for language in text.languages(romfs):
        data = _read(romfs, dictionaries, text.archive_path(language))
        files, patched = sarc.read(data), sarc.read(talon.patch_text(data))
        native, after = (msbt.read(archive[talon.MESSAGES]).messages for archive in (files, patched))
        assert sorted(label for label in native if native[label] != after[label]) == sorted(talon.LINES), language
        assert [name for name in files if files[name] != patched[name]] == [talon.MESSAGES], language
        if language == text.NAME_LANGUAGE:
            for label in talon.LINES:
                assert "milk" in msbt.plain(native[label]).lower(), label
            assert "bottle" in msbt.plain(native[talon.SHOWCASE_LABEL]).lower()
