"""Dampé's no-tool refusal (``text.dampe_refusal_changes``): one new message per language archive, in his own look,
each language's own translation and tool names, nothing native touched."""

import unicodedata

import pytest

from clawshot.formats import msbt, sarc, zsdic
from clawshot.formats.msbt import Msbt, Tag
from clawshot.patch import dampe_safety, text
from clawshot.patch.plan import PatchError

NAME, LABEL = dampe_safety.REFUSAL_MESSAGE.split(":")
FILE = f"{NAME}.msbt"
ENGLISH = "Come back with a Hookshot or Longshot. There's no climbing out of here without one."
LANGUAGES = (
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
)
VOICE = Tag(3, 0, b"\x0f\x00\x00")
HIGHLIGHT, RESET = Tag(0, 3, b"\x00\x00"), Tag(0, 3, b"\xff\xff")
NATIVE = {
    "Talk_01": [Tag(3, 0, b"\x10\x01\x00"), Tag(4, 0, b"\x06\x00LaughL\x00"), "Let's go.", Tag(0, 4), "Ready..."],
    text.DAMPE_DONOR: [VOICE, "Race again?"],
    "0003": ["I want to race!"],
}
# The words the refusal highlights: each language's own Hookshot and Longshot, declined where its sentence needs.
NAMES = {
    "CNzh": ["钩索", "长钩索"],
    "EUde": ["Wurfhaken", "Fern-Wurfhaken"],
    "EUen": ["Hookshot", "Longshot"],
    "EUes": ["gancho", "supergancho"],
    "EUfr": ["grappin", "super grappin"],
    "EUit": ["arpione", "super arpione"],
    "EUnl": ["grijphaak", "supergrijphaak"],
    "EUpl": ["hakownicą", "dalekosiężnicą"],
    "EUru": ["крюкострелом", "мощным крюкострелом"],
    "JPja": ["フックショット", "ロングフック"],
    "KRko": ["후크샷", "롱샷"],
    "TWzh": ["鉤索", "長鉤索"],
    "USen": ["Hookshot", "Longshot"],
    "USes": ["gancho", "supergancho"],
    "USfr": ["grappin", "supergrappin"],
    "USpt": ["gancho", "supergancho"],
}
DECLINED = ("EUpl", "EUru")  # their names stand in the instrumental, not as the pouch writes them


def archive(messages=NATIVE, file=FILE):
    return sarc.write(
        {
            file: msbt.write(Msbt(dict(messages), buckets=7)),
            "EventFlowMsg/Npc_Hylia_Dampe_001.msbt": msbt.write(Msbt({"Talk_00": ["Another Dampé"]}, buckets=1)),
            "Other/Unrelated.bin": b"unrelated",
        }
    )


def romfs_with(root, languages=LANGUAGES):
    """A dump holding just the named language archives (the changes only list them; each transform is given bytes)."""
    (root / "Mals").mkdir()
    for language in languages:
        (root / text.archive_path(language)).write_bytes(b"")
    return root


def refusal(changes, language, data=None):
    """The added message after ``language``'s change of ``data`` (a synthetic Dampé archive by default)."""
    out = sarc.read(changes[text.archive_path(language)](archive() if data is None else data))
    return msbt.read(out[FILE]).messages[LABEL]


def pages(parts):
    """The message as the box shows it: each page's rows, without the tags."""
    shown, page = [], ""
    for part in parts:
        if part == text.PAGE_BREAK:
            shown.append(page.split("\n"))
            page = ""
        elif isinstance(part, str):
            page += part
    return [*shown, page.split("\n")]


def highlighted(parts):
    """The words between the highlight colour and its reset."""
    words, word = [], None
    for part in parts:
        if part == HIGHLIGHT:
            word = ""
        elif part == RESET:
            words.append(word)
            word = None
        elif isinstance(part, str) and word is not None:
            word += part
    return words


def columns(row):
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in row)


def test_both_english_archives_say_the_exact_refusal_in_dampes_plain_voice(tmp_path):
    changes = text.dampe_refusal_changes(romfs_with(tmp_path))
    assert set(changes) == {text.archive_path(language) for language in LANGUAGES}
    for language in ("USen", "EUen"):
        parts = refusal(changes, language)
        assert parts[0] == VOICE and isinstance(parts[1], str)  # the donor's voice only: no laugh, no donor text
        assert " ".join(" ".join(rows) for rows in pages(parts)) == ENGLISH
        assert highlighted(parts) == ["Hookshot", "Longshot"]


def test_every_language_reads_back_its_own_translation_within_two_rows_of_forty_columns(tmp_path):
    changes = text.dampe_refusal_changes(romfs_with(tmp_path))
    for language in LANGUAGES:
        parts = refusal(changes, language)
        shown = pages(parts)
        assert parts[0] == VOICE
        assert highlighted(parts) == NAMES[language], language
        assert all(1 <= len(rows) <= 2 for rows in shown), (language, shown)
        assert all(0 < columns(row) <= 40 for rows in shown for row in rows), (language, shown)
        if language not in ("USen", "EUen"):
            plain = msbt.plain(parts)
            assert "Hookshot" not in plain and "climbing" not in plain, language  # translated, no English fallback


def test_native_messages_and_every_other_member_stay_as_they_were(tmp_path):
    changes = text.dampe_refusal_changes(romfs_with(tmp_path, ["USen"]))
    data = archive()
    before = sarc.read(data)
    after = sarc.read(changes[text.archive_path("USen")](data))
    assert {name: content for name, content in after.items() if name != FILE} == {
        name: content for name, content in before.items() if name != FILE
    }
    document = msbt.read(after[FILE])
    assert list(document.messages) == [*NATIVE, LABEL]
    assert {label: document.messages[label] for label in NATIVE} == NATIVE
    assert document.buckets == 7
    kept = Msbt({label: parts for label, parts in document.messages.items() if label != LABEL}, document.buckets)
    assert msbt.write(kept) == before[FILE]


@pytest.mark.parametrize(
    ("data", "match"),
    [
        (archive({"Talk_01": NATIVE["Talk_01"]}), text.DAMPE_DONOR),
        (archive(file="EventFlowMsg/Npc_Hylia_Dampe_Other.msbt"), "no message file"),
        (archive({**NATIVE, LABEL: ["taken"]}), "already there"),
    ],
)
def test_a_missing_donor_or_file_or_a_label_already_there_is_refused(tmp_path, data, match):
    changes = text.dampe_refusal_changes(romfs_with(tmp_path, ["USen"]))
    with pytest.raises(PatchError, match=match):
        changes[text.archive_path("USen")](data)


def test_a_language_without_a_translation_is_refused_rather_than_given_english(tmp_path):
    with pytest.raises(PatchError, match="EUsv"):
        text.dampe_refusal_changes(romfs_with(tmp_path, ["USen", "EUsv"]))


@pytest.mark.parametrize(
    ("language", "page"),
    [
        ("USen", "a row that runs past the forty columns of his box"),
        ("JPja", "ニイチャン" * 4 + "ダ"),  # 21 wide characters: 42 columns
        ("USen", "one\ntwo\nthree"),
    ],
)
def test_a_page_beyond_two_rows_of_forty_columns_is_refused(tmp_path, monkeypatch, language, page):
    monkeypatch.setitem(text.DAMPE_REFUSAL, language, (page,))
    changes = text.dampe_refusal_changes(romfs_with(tmp_path, [language]))
    with pytest.raises(PatchError, match="exceeds"):
        changes[text.archive_path(language)](archive())


@pytest.mark.dump
def test_dump_every_archive_gains_only_the_refusal_in_the_donor_voice_with_its_own_tool_names(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    changes = text.dampe_refusal_changes(romfs)
    assert set(changes) == {text.archive_path(language) for language in LANGUAGES}
    for language in LANGUAGES:
        path = text.archive_path(language)
        data = dicts.decompress(path, (romfs / path).read_bytes())
        before, after = sarc.read(data), sarc.read(changes[path](data))
        assert {name: content for name, content in after.items() if name != FILE} == {
            name: content for name, content in before.items() if name != FILE
        }
        native = msbt.read(before[FILE]).messages
        document = msbt.read(after[FILE])
        assert list(document.messages) == [*native, LABEL]
        assert {label: document.messages[label] for label in native} == native
        parts = document.messages[LABEL]
        assert parts[0] == native[text.DAMPE_DONOR][0], language  # voice, before any first-word highlight
        assert highlighted(parts) == NAMES[language], language
        if language not in DECLINED:
            pouch = msbt.read(before[text.POUCH_TEXT]).messages
            own = [msbt.plain(pouch[f"{key}_Name"]).lower() for key in ("Item_Hookshot", "Item_Longshot")]
            assert [name.lower() for name in NAMES[language]] == own, language
