"""Text patches: change message lines, name an item in a line, let Gossip Stones speak without the Mask of Truth.

Where the game's text comes from (``03-game-data.md`` section 22):

- Every line is a message in ``Mals/<language>.Product.110.sarc.zs``, an archive of MSBT files; a flow shows it by
  ``MessageId: "<file without .msbt>:<label>"``. :func:`edit_messages` gives the transform that replaces messages
  in one language's archive (decompressed bytes in and out, as :data:`clawshot.patch.write.FileChanges` expects);
  :func:`add_messages` the one that appends new labels to a file the archive already holds.
- An item's texts are labelled by its actor's ``ActorName`` component (:func:`text_key`), in
  ``ActorMsg/PouchContent.msbt``: ``<key>_Name``, ``_Caption``, ``_GetMessage``, ``_GetCaption``, ... The get
  window shows ``Dm_SY_Get:GetMessage`` and ``GetCaption``, whose only content is a run-time tag (group 2, types
  23 and 19) for the item being given, so it names whatever item a chest, gift or shop gives. To name an item in
  another line, :func:`item_name` returns that language's ``<key>_Name`` (text and grammar tags), to put into the
  line; the line then reads right in each language it is built for.
- A stone's line is the ``GossipStone`` message labelled with its placement name; the flow asks for the Mask of
  Truth first. :func:`gossip_without_mask` re-points those two questions so every answer leads on.
- **Hints** (round 7): :func:`hint_changes` writes each stone's hint (from ``clawshot.generate.hints``) into the
  ``GossipStone`` messages of every language archive given, wrapped to the stone's box (two rows a page) in the
  stone's own style, the filled-in names coloured; with stones that speak without the mask, the flow edit too. The
  text is English in every language (D26, Kareem); item names are the game's English ones (:func:`item_names`).
"""

from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from clawshot.census import hints
from clawshot.formats import byml, evfl, msbt, sarc, zsdic
from clawshot.formats.msbt import Part, Tag
from clawshot.generate import hints as stone_hints
from clawshot.generate.hints import FIELD_END, FIELD_START
from clawshot.patch.items import ItemActors
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

if TYPE_CHECKING:
    from clawshot.generate import Seed

ARCHIVE = "Mals/{language}.Product.110.sarc.zs"
POUCH_TEXT = "ActorMsg/PouchContent.msbt"
ACTOR_PACK = "Pack/Actor/{actor}.pack.zs"
NAME_LANGUAGE = "USen"  # the language whose item names the hint text uses
HINT_WIDTH = 60  # characters a row; the game's own stone lines are at most 65
HINT_ROWS = 2  # rows a page, as every stone line has
COLOUR = (0, 3)  # the colour tag (group 0, type 3); its parameter is the colour
HIGHLIGHT = b"\x00\x00"  # the colour other lines give a name they stress
# What ends a highlight: every one of USen's 3046 highlights that ends in its line ends with this colour, never by
# naming the line's own colour again. The stones' own ``01 00`` does not end one (seed-shop-7c, Kareem: the text
# stayed highlighted to the end of the line).
RESET = b"\xff\xff"
PAGE_BREAK = Tag(0, 4, b"")
SHEIK_MESSAGES = "EventFlowMsg/Npc_Hylia_Sheik_Adult.msbt"
SHEIK_TOOL_LABELS = ("Talk_01", "Talk_03")
ALTAR_MESSAGES = "EventFlowMsg/SignboardWood.msbt"
ALTAR_LABEL = "TempleOfTime_000"
GANONDORF_MESSAGES = "EventFlowMsg/Dm_InsideGanonCastle_BossIn.msbt"
GANONDORF_LABEL = "Dm_InsideGanonCastle_BossIn_Text_013_b"
FAIRY_MESSAGES = "EventFlowMsg/Dm_FairyFountain_Power.msbt"
GATED_FAIRY_CHECKS = (
    "HC Great Fairy Reward",
    "ZF Great Fairy Reward",
    "DMC Great Fairy Reward",
    "Colossus Great Fairy Reward",
    "OGC Great Fairy Reward",
)


def archive_path(language: str) -> str:
    return ARCHIVE.format(language=language)


def languages(romfs: str | Path) -> list[str]:
    """The message languages in the dump (``USen``, ``EUen``, ...), sorted."""
    return sorted(p.name.split(".")[0] for p in (Path(romfs) / "Mals").glob("*.Product.110.sarc.zs"))


def edit_messages(edits: Mapping[str, Mapping[str, Sequence[Part]]]) -> Callable[[bytes], bytes]:
    """The transform of one language archive that sets ``edits[file][label]`` as each message's parts.

    Only existing messages are replaced; a missing file or label raises :class:`PatchError`. The archive and every
    changed file are read back before the bytes are returned."""

    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        for name in sorted(edits):
            if name not in files:
                raise PatchError(f"no message file {name} in the archive")
            document = msbt.read(files[name])
            for label, parts in edits[name].items():
                if label not in document.messages:
                    raise PatchError(f"{name}: no message labelled {label}")
                document.messages[label] = msbt.normalized(list(parts))
            written = msbt.write(document)
            if msbt.read(written) != document:
                raise PatchError(f"{name}: the written file does not read back as the edited messages")
            files[name] = written
        out = sarc.write(files)
        if sarc.read(out) != files:
            raise PatchError("the written archive does not read back as the edited files")
        return out

    return transform


def add_messages(additions: Mapping[str, Mapping[str, Sequence[Part]]]) -> Callable[[bytes], bytes]:
    """The transform of one language archive that appends ``additions[file][label]`` as new messages.

    Each file must already be in the archive and each label must be new to it: a missing file or a label it already
    holds raises :class:`PatchError`, so nothing native or already added is overwritten. The old messages keep their
    order and index and the file its bucket count; the new labels follow in sorted order; every other member stays
    as it was. Each changed file is read back, and removing exactly the added labels must write the original file
    again; then the archive is read back."""

    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        for name in sorted(additions):
            if name not in files:
                raise PatchError(f"no message file {name} in the archive")
            document = msbt.read(files[name])
            labels = sorted(additions[name])
            taken = [label for label in labels if label in document.messages]
            if taken:
                raise PatchError(f"{name}: messages labelled {taken} are already there")
            added = {label: msbt.normalized(list(additions[name][label])) for label in labels}
            expected = msbt.Msbt({**document.messages, **added}, document.buckets)
            written = msbt.write(expected)
            back = msbt.read(written)
            if back != expected or list(back.messages) != list(expected.messages):
                raise PatchError(f"{name}: the written file does not read back as the old messages, then the new")
            kept = {label: parts for label, parts in back.messages.items() if label not in added}
            if msbt.write(msbt.Msbt(kept, back.buckets)) != files[name]:
                raise PatchError(f"{name}: removing the added labels does not give back the original file")
            files[name] = written
        out = sarc.write(files)
        if sarc.read(out) != files:
            raise PatchError("the written archive does not read back as the files with the added messages")
        return out

    return transform


def text_key(pack: Mapping[str, bytes], actor: str) -> str:
    """The name ``actor``'s texts are labelled by: its ``ActorNameRef`` component, the nearest along its ``$parent``
    chain inside ``pack`` (the actor pack's files), else the actor's own name."""
    name = f"Actor/{actor}.engine__actor__ActorParam.bgyml"
    seen = set()
    while name in pack and name not in seen:
        seen.add(name)
        tree = byml.read(pack[name])
        ref = str((tree.get("Components") or {}).get("ActorNameRef", ""))
        if ref:
            return ref.rsplit("/", 1)[-1].split(".", 1)[0]
        parent = str(tree.get("$parent", ""))
        name = "Actor/" + parent.rsplit("/", 1)[-1].replace(".gyml", ".bgyml") if parent else ""
    return actor


def read_text_key(romfs: str | Path, actor: str, dicts: zsdic.Dictionaries | None = None) -> str:
    romfs = Path(romfs)
    path = ACTOR_PACK.format(actor=actor)
    if not (romfs / path).is_file():
        raise PatchError(f"no actor pack {path}")
    dicts = dicts or zsdic.Dictionaries.from_romfs(romfs)
    return text_key(sarc.read(dicts.decompress(path, (romfs / path).read_bytes())), actor)


def item_name(pouch_text: msbt.Msbt, key: str) -> list[Part]:
    """The parts of ``<key>_Name`` in one language's ``ActorMsg/PouchContent.msbt``: the item's name as that
    language writes it, grammar tags included."""
    label = f"{key}_Name"
    if label not in pouch_text.messages:
        raise PatchError(f"{POUCH_TEXT}: no message labelled {label}")
    return list(pouch_text.messages[label])


def keep_style(original: Sequence[Part], parts: Sequence[Part]) -> list[Part]:
    """``parts`` after the tags ``original`` opens with (a Gossip Stone's colour, size and voice), so a new line
    keeps the look of the one it replaces."""
    lead: list[Part] = []
    for part in original:
        if isinstance(part, str):
            break
        lead.append(part)
    return lead + list(parts)


def _is_mask_gate(gate: hints.TalkGate) -> bool:
    return hints.MASK_OF_TRUTH in dict(gate.params).values()


def gossip_without_mask(flowchart: evfl.Flowchart) -> list[str]:
    """Let every Gossip Stone speak whether or not Link has or wears the Mask of Truth: each Mask of Truth question
    on the way to the stone's line sends every answer where the needed one went. Edits ``flowchart`` in place and
    returns the names of the events changed."""
    gates = [gate for gate in hints.talk_gates(flowchart) if _is_mask_gate(gate)]
    if not gates:
        raise PatchError(f"{flowchart.name}: no Mask of Truth question on the way to the stone's line")
    by_name = {event.name: event for event in flowchart.events}
    for gate in gates:
        event = by_name[gate.event]
        target = dict(event.cases)[gate.case]
        event.cases = [(value, target) for value, _ in event.cases]
    left = [gate for gate in hints.talk_gates(flowchart) if _is_mask_gate(gate)]
    if left:
        raise PatchError(f"{flowchart.name}: Mask of Truth questions left after the edit: {left}")
    return [gate.event for gate in gates]


def gossip_flow_transform(data: bytes) -> bytes:
    """The ``GossipStone`` flow file (decompressed) with :func:`gossip_without_mask` applied, read back checked."""
    document = evfl.read(data)
    if document.flowchart is None:
        raise PatchError("the GossipStone flow holds no flowchart")
    gossip_without_mask(document.flowchart)
    written = evfl.write(document)
    if evfl.read(written) != document:
        raise PatchError("the written GossipStone flow does not read back as the edited flow")
    return written


def item_names(romfs: str | Path, items: Iterable[str], table: ItemActors) -> dict[str, str]:
    """Each logic item's name as :data:`NAME_LANGUAGE` writes it (its ``<key>_Name``, without grammar tags); an item
    without an actor in ``table`` keeps its logic name.

    A progressive family (``clawshot.progressive.CHAINS``) keeps its family label ("Progressive Hookshot"): its
    native grant and get-window name depend on the tier owned when it is opened, so the base actor's name would be
    wrong for every later copy. No actor pack is read for a family, and none at all when no item needs game text."""
    from clawshot.progressive import CHAINS

    names = {}
    wanted = []
    for item in sorted(set(items)):
        actor = None if item in CHAINS else table.actors.get(item)
        if actor is None:
            names[item] = item
        else:
            wanted.append((item, actor))
    if not wanted:
        return names
    romfs = Path(romfs)
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    archive = archive_path(NAME_LANGUAGE)
    pouch = msbt.read(sarc.read(dicts.decompress(archive, (romfs / archive).read_bytes()))[POUCH_TEXT])
    for item, actor in wanted:
        names[item] = msbt.plain(item_name(pouch, read_text_key(romfs, actor, dicts)))
    return dict(sorted(names.items()))


def _rows(text: str, width: int) -> list[str]:
    """``text`` broken into rows of at most ``width`` visible characters (the field marks take no room)."""
    rows: list[str] = []
    row = ""
    for word in text.split():
        candidate = f"{row} {word}" if row else word
        if row and len(candidate.replace(FIELD_START, "").replace(FIELD_END, "")) > width:
            rows.append(row)
            candidate = word
        row = candidate
    return [*rows, row] if row else rows


def stone_line(original: Sequence[Part], text: str, width: int = HINT_WIDTH, rows: int = HINT_ROWS) -> list[Part]:
    """A stone's line saying ``text`` in the look of ``original``: its opening tags first (voice, size, colour), rows
    of at most ``width`` characters, ``rows`` to a page, each new page reopening the size and colour, and the names
    between :data:`~clawshot.generate.hints.FIELD_START` and ``FIELD_END`` in the highlight colour, each closed with
    :data:`RESET` as the game's own lines close theirs."""
    lead = keep_style(original, [])
    style = [tag for tag in lead if isinstance(tag, Tag) and tag.group == 0]
    lines = _rows(text, width)
    pages = ["\n".join(lines[i : i + rows]) for i in range(0, len(lines), rows)]
    parts: list[Part] = list(lead)
    for index, page in enumerate(pages):
        if index:
            parts += [PAGE_BREAK, *style]
        for char in page:
            if char == FIELD_START:
                parts.append(Tag(*COLOUR, HIGHLIGHT))
            elif char == FIELD_END:
                parts.append(Tag(*COLOUR, RESET))
            elif parts and isinstance(parts[-1], str):
                parts[-1] += char
            else:
                parts.append(char)
    return parts


def _altar_line(original: Sequence[Part], lines: Sequence[str]) -> list[Part]:
    """Keep rewards/conditions atomic within the observed native 48-character, three-row sign envelope."""
    if any(len(line) > 48 for line in lines):
        raise PatchError(f"altar line exceeds the 48-character envelope: {lines}")
    lead = keep_style(original, [])
    style = [tag for tag in lead if isinstance(tag, Tag) and tag.group == 0]
    parts = list(lead)
    for offset in range(0, len(lines), 2):
        if offset:
            parts.extend([PAGE_BREAK, *style])
        parts.append("\n".join(lines[offset : offset + 2]))
    return parts


def stone_lines_transform(lines: Mapping[str, str]) -> Callable[[bytes], bytes]:
    """The transform of one language archive giving each stone label in ``lines`` its new line (:func:`stone_line`,
    in that archive's style of the stone)."""

    def transform(data: bytes) -> bytes:
        files = sarc.read(data)
        if hints.GOSSIP_MESSAGES not in files:
            raise PatchError(f"no message file {hints.GOSSIP_MESSAGES} in the archive")
        originals = msbt.read(files[hints.GOSSIP_MESSAGES]).messages
        missing = sorted(set(lines) - set(originals))
        if missing:
            raise PatchError(f"{hints.GOSSIP_MESSAGES}: no message labelled {missing}")
        parts = {label: stone_line(originals[label], text) for label, text in lines.items()}
        return edit_messages({hints.GOSSIP_MESSAGES: parts})(data)

    return transform


def hint_changes(
    romfs: str | Path, lines: Mapping[str, str], language_names: Sequence[str], *, without_mask: bool
) -> FileChanges:
    """The files a seed's hints change: each language archive's stone lines (``lines``: label -> marked text) and,
    with ``without_mask``, the ``GossipStone`` flow so stones speak without the Mask of Truth."""
    changes: dict[str, Callable[[bytes], bytes]] = {}
    if lines:
        transform = stone_lines_transform(lines)
        changes.update({archive_path(language): transform for language in language_names})
    if without_mask:
        changes[hints.flow_path(romfs, hints.GOSSIP_FLOW)] = gossip_flow_transform
    return changes


def sheik_hint_changes(romfs: str | Path, hookshot_locations: Sequence[str]) -> FileChanges:
    """Replace both vanilla tool directions with a true seed location (or omit the tool for a slice).

    English in all language archives follows D26, independently of Gossip Stone mode or free travel.
    Only the placed NPC's two tool messages change; his dialogue flow and the Prelude scene stay native.
    """
    if hookshot_locations:
        location = min(hookshot_locations)
        line = f"Seek the Hookshot at {FIELD_START}{location}{FIELD_END}."
    else:
        line = "There are many paths ahead. Choose your next destination with care."

    def transform(data: bytes) -> bytes:
        archive = sarc.read(data)
        if SHEIK_MESSAGES not in archive:
            raise PatchError(f"no message file {SHEIK_MESSAGES} in the archive")
        messages = msbt.read(archive[SHEIK_MESSAGES]).messages
        missing = sorted(set(SHEIK_TOOL_LABELS) - messages.keys())
        if missing:
            raise PatchError(f"{SHEIK_MESSAGES}: no message labelled {missing}")
        edits = {label: stone_line(messages[label], line) for label in SHEIK_TOOL_LABELS}
        return edit_messages({SHEIK_MESSAGES: edits})(data)

    return {archive_path(language): transform for language in languages(romfs)}


def scrub_hint_changes(
    romfs: str | Path, placements: Mapping[str, str], table: ItemActors, prices: Mapping[str, int]
) -> FileChanges:
    """Source-specific sale previews, English in every language, with no vanilla-item claims.

    Only selected once-sales participate. Repeat merchants keep their native text and gates.
    Prices are the same effective fixed prices used by the sale writer, not inferred from text.
    """
    from clawshot.patch import scrubs

    selected = {name: item for name, item in placements.items() if name in scrubs.SALES}
    if not selected:
        return {}
    names = item_names(romfs, selected.values(), table)
    lines = {
        scrubs.OFFER_LABELS[name]: f"I offer {FIELD_START}{names[item]}{FIELD_END} for {prices[name]} rupees. Buy it?"
        for name, item in selected.items()
    }
    file = f"{scrubs.OFFER_FILE}.msbt"

    def transform(data: bytes) -> bytes:
        archive = sarc.read(data)
        if file not in archive:
            raise PatchError(f"no message file {file} in the archive")
        messages = msbt.read(archive[file]).messages
        native = "Enemy_Scrub_Business_Heart_01"
        if native not in messages:
            raise PatchError(f"{file}: no message labelled {native}")
        # Conservative NPC envelope: two rows of forty English characters per page.
        additions = {label: stone_line(messages[native], line, width=40, rows=2) for label, line in lines.items()}
        return add_messages({file: additions})(data)

    return {
        **{archive_path(language): transform for language in languages(romfs)},
        **scrubs.offer_changes(tuple(selected)),
    }


def static_hint_changes(romfs: str | Path, seed: "Seed", table: ItemActors) -> FileChanges:
    """Altar reward regions/conditions and Ganondorf's bounded battle-intro clue.

    Both existing hint modes keep NPC/sign text readable normally; only stones require
    the mask. No event/timeline, saved state, grant or window is changed here.
    """
    from clawshot.generate.rewards import catalog

    lines: dict[str, dict[str, str]] = {}

    def region(name: str) -> str:
        location = seed.world.locations[name]
        area = stone_hints.hint_area(seed.world, location.region)
        if area is None:
            raise PatchError(f"{name}: no region-level hint area")
        return stone_hints.area_name(area)

    if seed.settings.dungeon_rewards or seed.settings.bridge != "vanilla":
        rewards = {slot["item"] for slot in catalog()["slots"].values()}
        placed = [(name, item) for name, item in seed.placements.items() if item in rewards]
        names = item_names(romfs, (item for _, item in placed), table)
        pages = [f"{names[item]}: {region(name).removeprefix('the ')}" for name, item in placed]
        if seed.settings.door_of_time == "closed":
            stones = "3 Spiritual Stones" if seed.settings.dungeon_rewards else "finish the 3 stone quests"
            pages.extend(
                [
                    f"Door: {stones}",
                    "Door: Ocarina of Time + Song of Time",
                    "Door: finish Impa's send-off",
                    "Door: play Song of Time here",
                ]
            )
        else:
            pages.extend(["Door: finish Impa's send-off", "Door: reach Hyrule Field"])
            pages.append(
                "Door: play Song of Time with an ocarina"
                if seed.settings.door_of_time == "song_only"
                else "Door: no items needed"
            )
        if seed.settings.bridge == "vanilla":
            pages.extend(["Bridge: awaken Shadow and Spirit sages", "Bridge: return here for Zelda's story"])
        elif seed.settings.bridge_count == 0:
            pages.append("Bridge: no items required.")
        else:
            nouns = {
                "stones": ("Spiritual Stone", "Spiritual Stones"),
                "medallions": ("medallion", "medallions"),
                "rewards": ("dungeon reward", "dungeon rewards"),
                "tokens": ("Gold Skulltula token", "Gold Skulltula tokens"),
            }
            noun = nouns[seed.settings.bridge][seed.settings.bridge_count != 1]
            pages.append(f"Bridge: own {seed.settings.bridge_count} {noun}.")
        lines[ALTAR_MESSAGES] = {ALTAR_LABEL: "\n".join(pages)}

    if any(name in seed.shuffled for name in GATED_FAIRY_CHECKS):
        # TriForcePoint's no-Din branch shares these Navi lines across all five
        # fountains. SpecialAbility2 (Death Mountain Trail) bypasses that branch.
        lines[FAIRY_MESSAGES] = {
            "Talk_00": "There is power here, but this fountain's gift must wait.",
            "Talk_01": "Return once you own Din's Fire. It may be among any of this seed's shuffled rewards.",
            "Talk_02": "You need to own Din's Fire before this fountain can offer its gift. Return once you find it.",
        }

    if "Light Arrows" in seed.world.start_items:
        light = "You began with the Light Arrow."
    else:
        sources = [name for name, item in seed.placements.items() if item == "Light Arrows"]
        light = f"Light Arrow: {region(sources[0])}." if sources else None
    if light is not None:
        # This is a timed subtitle (native clip38, 296 frames), not a paginated NPC box.
        if len(_rows(light, 35)) > 2:
            raise PatchError("Ganondorf's Light Arrow clue exceeds its two-row subtitle")
        lines[GANONDORF_MESSAGES] = {GANONDORF_LABEL: light}
    if not lines:
        return {}

    def transform(data: bytes) -> bytes:
        archive = sarc.read(data)
        edits = {}
        for file, labels in lines.items():
            if file not in archive:
                raise PatchError(f"no message file {file} in the archive")
            originals = msbt.read(archive[file]).messages
            if missing := sorted(labels.keys() - originals.keys()):
                raise PatchError(f"{file}: no messages labelled {missing}")
            width = 35 if file == GANONDORF_MESSAGES else 40
            edits[file] = {
                label: _altar_line(originals[label], line.splitlines())
                if file == ALTAR_MESSAGES
                else stone_line(originals[label], line, width=width, rows=2)
                for label, line in labels.items()
            }
        return edit_messages(edits)(data)

    return {archive_path(language): transform for language in languages(romfs)}
