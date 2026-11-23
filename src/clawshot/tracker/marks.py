"""Checks the player marked done or skipped by hand.

- **Marks** (spec ``tracker-in-logic`` D6-D10): a check the save cannot read (``collected is None``: shops,
  swap-only gifts, unset placement-hash pickups) leaves the open list once marked done. A save that later reads the
  check drops its mark.
- **Skips** (round 21, plans/rounds/r21-tracker.md): a check the save does read, which the player won't collect (a
  windmill rupee), leaves the open list once skipped. A save read never drops a skip; only the player does.

    store = MarkStore()                                    # tracker-marks.json beside the preferences
    store.set(seed_identity(seed), save_folder, "KF Shop Item 1", True)
    store.marks(seed_identity(seed), save_folder)          # -> frozenset of check ids
    store.set(seed_identity(seed), save_folder, "Kak Windmill Rupee", True, table=SKIPS)

The file lives in Clawshot's preferences folder, the parent of ``app.preferences.user_preferences_path()``
(``%APPDATA%\\Clawshot`` on Windows, ``~/Library/Application Support/Clawshot``, ``$XDG_CONFIG_HOME/clawshot``), not
in the deletable icon cache and never in a seed, save or game folder. Both tables are keyed by seed identity
(:func:`seed_identity`) and save folder (the game moves through its slots); ``skips`` is written only when it holds
something, so a file without skips keeps its old bytes (a build from before skips reads ``marks`` and ignores
``skips``). An unreadable file is reported in :attr:`MarkStore.warning`, read as no marks and left as it is until a
mark changes; a missing file is simply no marks yet. Writes go to a temporary file in the same folder, then replace
the old file, with sorted keys and lists, so the same marks give the same bytes.
"""

import hashlib
import json
import os
import threading
from collections.abc import Iterable
from pathlib import Path
from tempfile import NamedTemporaryFile

from clawshot.app import preferences
from clawshot.tracker.seeds import Seed

MARKS_FILE = "tracker-marks.json"
VERSION = 1
MARKS, SKIPS = "marks", "skips"
TABLES = (MARKS, SKIPS)
Tables = dict[str, dict[str, dict[str, list[str]]]]  # table -> seed identity -> save folder -> sorted check ids


# Every marks warning starts with this, so the OBS view can leave them out (they name local files, D13).
WARNING_PREFIX = "Manual marks (tracker-marks.json in Clawshot's preferences folder)"


def marks_path() -> Path:
    """``tracker-marks.json`` in the preferences folder."""
    return preferences.user_preferences_path().parent / MARKS_FILE


def seed_identity(seed: Seed) -> str:
    """The seed's manifest ``output_sha256``, else the SHA-256 of its spoiler file (D10)."""
    digest = seed.metadata.get("output_sha256")
    if isinstance(digest, str) and digest:
        return digest
    return hashlib.sha256(seed.spoiler_path.read_bytes()).hexdigest()


class MarkStore:
    """The marks file, read once and rewritten whenever a mark changes. Thread-safe."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else marks_path()
        self.warning = ""
        self._lock = threading.RLock()
        self._data: Tables | None = None

    def _load(self) -> Tables:
        if self._data is not None:
            return self._data
        self._data = {table: {} for table in TABLES}
        try:
            raw = self.path.read_bytes()
        except FileNotFoundError:
            return self._data
        except OSError as error:
            self.warning = f"{WARNING_PREFIX} could not be read ({type(error).__name__}); none are shown."
            return self._data
        try:
            data = json.loads(raw.decode("utf-8"))
            self._data = {
                table: {
                    str(seed_id): {str(slot): sorted({str(c) for c in checks}) for slot, checks in slots.items()}
                    for seed_id, slots in (data[table] if table == MARKS else data.get(table, {})).items()
                }
                for table in TABLES
            }
        except (UnicodeDecodeError, ValueError, KeyError, TypeError, AttributeError) as error:
            self.warning = (
                f"{WARNING_PREFIX} could not be read ({type(error).__name__}); none are shown, and the "
                "file is kept until you change a mark."
            )
        return self._data

    def marks(self, seed_id: str, slot: str, *, table: str = MARKS) -> frozenset[str]:
        with self._lock:
            return frozenset(self._load()[table].get(seed_id, {}).get(slot, ()))

    def set(self, seed_id: str, slot: str, check: str, marked: bool, *, table: str = MARKS) -> None:
        with self._lock:
            current = set(self.marks(seed_id, slot, table=table))
            changed = current | {check} if marked else current - {check}
            if changed != current:
                self._store({table: changed}, seed_id, slot)

    def drop(self, seed_id: str, slot: str, checks: Iterable[str]) -> None:
        """Remove marks the save now confirms (4.5); writes only when one was marked. Skips are never dropped."""
        with self._lock:
            current = set(self.marks(seed_id, slot))
            if current & set(checks):
                self._store({MARKS: current - set(checks)}, seed_id, slot)

    def clear(self, seed_id: str, slot: str) -> int:
        """Remove every mark and skip of this seed and slot; returns how many there were."""
        with self._lock:
            count = sum(len(self.marks(seed_id, slot, table=table)) for table in TABLES)
            if count:
                self._store(dict.fromkeys(TABLES, set()), seed_id, slot)
            return count

    def _store(self, changes: dict[str, Iterable[str]], seed_id: str, slot: str) -> None:
        data = {table: {key: dict(slots) for key, slots in seeds.items()} for table, seeds in self._load().items()}
        for table, checks in changes.items():
            checks = sorted(checks)
            slots = data[table].setdefault(seed_id, {})
            if checks:
                slots[slot] = checks
            else:
                slots.pop(slot, None)
                if not slots:
                    data[table].pop(seed_id)
        self._write(data)
        self._data, self.warning = data, ""

    def _write(self, data: Tables) -> None:
        record = {"version": VERSION, MARKS: data[MARKS], **({SKIPS: data[SKIPS]} if data[SKIPS] else {})}
        text = json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=self.path.parent, prefix=".tracker-marks-", delete=False
        ) as stream:
            stream.write(text)
            temporary = Path(stream.name)
        try:
            os.replace(temporary, self.path)
        except OSError:
            temporary.unlink(missing_ok=True)
            raise
