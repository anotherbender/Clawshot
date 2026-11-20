"""Checks the player marked done by hand (spec ``tracker-in-logic`` D6-D10): a check the save cannot read
(``collected is None``: shops, swap-only gifts, unset placement-hash pickups) leaves the open list once marked.

    store = MarkStore()                                    # tracker-marks.json beside the preferences
    store.set(seed_identity(seed), save_folder, "KF Shop Item 1", True)
    store.marks(seed_identity(seed), save_folder)          # -> frozenset of check ids

The file lives in Clawshot's preferences folder, the parent of ``app.preferences.user_preferences_path()``
(``%APPDATA%\\Clawshot`` on Windows, ``~/Library/Application Support/Clawshot``, ``$XDG_CONFIG_HOME/clawshot``), not
in the deletable icon cache and never in a seed, save or game folder. Marks are keyed by seed identity
(:func:`seed_identity`) and save folder (the game moves through its slots). An unreadable file is reported in
:attr:`MarkStore.warning`, read as no marks and left as it is until a mark changes; a missing file is simply no
marks yet. Writes go to a temporary file in the same folder, then replace the old file, with sorted keys and lists,
so the same marks give the same bytes.
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
        self._data: dict[str, dict[str, list[str]]] | None = None

    def _load(self) -> dict[str, dict[str, list[str]]]:
        if self._data is not None:
            return self._data
        self._data = {}
        try:
            raw = self.path.read_bytes()
        except FileNotFoundError:
            return self._data
        except OSError as error:
            self.warning = f"Manual marks could not be read from {self.path} ({error}); none are shown."
            return self._data
        try:
            data = json.loads(raw.decode("utf-8"))
            table = data["marks"]
            self._data = {
                str(seed_id): {str(slot): sorted({str(c) for c in checks}) for slot, checks in slots.items()}
                for seed_id, slots in table.items()
            }
        except (UnicodeDecodeError, ValueError, KeyError, TypeError, AttributeError) as error:
            self.warning = (
                f"Manual marks could not be read from {self.path} ({type(error).__name__}); none are shown, and the "
                "file is kept until you change a mark."
            )
        return self._data

    def marks(self, seed_id: str, slot: str) -> frozenset[str]:
        with self._lock:
            return frozenset(self._load().get(seed_id, {}).get(slot, ()))

    def set(self, seed_id: str, slot: str, check: str, marked: bool) -> None:
        with self._lock:
            current = set(self.marks(seed_id, slot))
            changed = current | {check} if marked else current - {check}
            if changed != current:
                self._store(seed_id, slot, changed)

    def drop(self, seed_id: str, slot: str, checks: Iterable[str]) -> None:
        """Remove marks the save now confirms (4.5); writes only when one was marked."""
        with self._lock:
            current = set(self.marks(seed_id, slot))
            if current & set(checks):
                self._store(seed_id, slot, current - set(checks))

    def clear(self, seed_id: str, slot: str) -> int:
        """Remove every mark of this seed and slot; returns how many there were."""
        with self._lock:
            current = self.marks(seed_id, slot)
            if current:
                self._store(seed_id, slot, set())
            return len(current)

    def _store(self, seed_id: str, slot: str, checks: Iterable[str]) -> None:
        checks = sorted(checks)
        data = {key: dict(slots) for key, slots in self._load().items()}
        slots = data.setdefault(seed_id, {})
        if checks:
            slots[slot] = checks
        else:
            slots.pop(slot, None)
            if not slots:
                data.pop(seed_id)
        self._write(data)
        self._data, self.warning = data, ""

    def _write(self, data: dict[str, dict[str, list[str]]]) -> None:
        text = json.dumps({"version": VERSION, "marks": data}, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
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
