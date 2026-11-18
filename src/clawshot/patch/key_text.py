"""Target-dungeon get-window text for dungeon items found outside their own dungeon.

English item and dungeon names are read from the player's dump, never bundled.
Each used family/target gets an appended message pair in every language archive.
Small-key labels and wording remain unchanged for existing settings.
"""

import re
from collections.abc import Iterable
from pathlib import Path

from clawshot.formats import msbt, sarc, zsdic
from clawshot.patch import text
from clawshot.patch.key_targets import DUNGEON_TARGETS, TARGETS, DungeonGrant, KeyTarget
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

GET_TEXT = "EventFlowMsg/Dm_SY_Get.msbt"
GET_MESSAGES = GET_TEXT.removesuffix(".msbt")  # the file as a MessageId names it
LOCATION_TEXT = "LocationMsg/Location.msbt"
KEY_NOUN = "Item_Dungeon_SmallKey_Name"
LABEL = "Clawshot_{family}_{target}_{role}"
ROLES = ("GetMessage", "GetCaption")
MAIN = "{key} ({dungeon})"
CAPTION = "Opens one locked door.\nDungeon: {dungeon}"
CAPTIONS = {
    "SmallKey": CAPTION,
    "BossKey": "Opens the boss door.\nDungeon: {dungeon}",
    "Map": "Dungeon map.\nDungeon: {dungeon}",
    "Compass": "Dungeon compass.\nDungeon: {dungeon}",
}
_TARGET_ID = re.compile(r"[A-Za-z0-9_]+")  # fits a message label and a ``file:label`` MessageId


def _targets(family: str = "SmallKey") -> dict[str, KeyTarget]:
    """Native target IDs supported by the requested family."""
    if family not in CAPTIONS:
        raise PatchError(f"no dungeon-item text family {family!r}")
    targets = TARGETS if family == "SmallKey" else DUNGEON_TARGETS
    by_id: dict[str, KeyTarget] = {}
    for logical in sorted(targets):
        target = targets[logical]
        if not _TARGET_ID.fullmatch(target.id):
            raise PatchError(f"small-key target {logical}: {target.id!r} cannot be part of a message label")
        if by_id.setdefault(target.id, target) != target:
            raise PatchError(f"small-key target ID {target.id} is claimed by {by_id[target.id]} and {target}")
    return by_id


def _known(target_ids: Iterable[str], family: str = "SmallKey") -> dict[str, KeyTarget]:
    """The targets of ``target_ids``, sorted by ID; an unknown ID raises :class:`PatchError`."""
    by_id = _targets(family)
    used = sorted(set(target_ids))
    unknown = [target for target in used if target not in by_id]
    if unknown:
        raise PatchError(f"no small-key target {unknown}")
    return {target: by_id[target] for target in used}


def _labels(target_id: str, family: str = "SmallKey") -> tuple[str, str]:
    main, caption = (LABEL.format(family=family, target=target_id, role=role) for role in ROLES)
    return main, caption


def labels(target_id: str, family: str = "SmallKey") -> tuple[str, str]:
    """Acquisition message and caption IDs for this target and item family."""
    _known([target_id], family)
    main, caption = (f"{GET_MESSAGES}:{label}" for label in _labels(target_id, family))
    return main, caption


def _name(messages: msbt.Msbt, label: str, what: str) -> str:
    """The text of message ``label`` without its tags, its whitespace closed up to single spaces."""
    if label not in messages.messages:
        raise PatchError(f"{what}: no English message labelled {label}")
    name = " ".join(msbt.plain(messages.messages[label]).split())
    if not name:
        raise PatchError(f"{what}: the English message {label} has no text")
    return name


def changes(romfs: str | Path, target_ids: Iterable[str | DungeonGrant]) -> FileChanges:
    """Append named message pairs; bare target IDs denote small keys."""
    grants = sorted(
        {value if isinstance(value, DungeonGrant) else DungeonGrant(value, "SmallKey") for value in target_ids}
    )
    targets = {grant.target: _known([grant.target], grant.family)[grant.target] for grant in grants}
    if not grants:
        return {}
    romfs = Path(romfs)
    archive = text.archive_path(text.NAME_LANGUAGE)
    if not (romfs / archive).is_file():
        raise PatchError(f"no {archive} to read the English names from")
    files = sarc.read(zsdic.Dictionaries.from_romfs(romfs).decompress(archive, (romfs / archive).read_bytes()))
    for member in (LOCATION_TEXT, text.POUCH_TEXT):
        if member not in files:
            raise PatchError(f"{archive}: no message file {member}")
    locations, pouch = msbt.read(files[LOCATION_TEXT]), msbt.read(files[text.POUCH_TEXT])
    owners: dict[str, str] = {}
    additions: dict[str, list[msbt.Part]] = {}
    for grant in grants:
        target_id, family = grant.target, grant.family
        target = targets[target_id]
        key = _name(pouch, f"Item_Dungeon_{family}_Name", text.POUCH_TEXT)
        dungeon = _name(locations, target.location_label, f"{LOCATION_TEXT} (small-key target {target_id})")
        if owners.setdefault(dungeon, target_id) != target_id:
            raise PatchError(f"small-key targets {owners[dungeon]} and {target_id} are both named {dungeon!r}")
        main, caption = _labels(target_id, family)
        additions[main] = [MAIN.format(key=key, dungeon=dungeon)]
        additions[caption] = [CAPTIONS[family].format(dungeon=dungeon)]
    transform = text.add_messages({GET_TEXT: additions})
    return {text.archive_path(language): transform for language in text.languages(romfs)}
