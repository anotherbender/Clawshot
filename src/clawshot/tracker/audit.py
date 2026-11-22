"""Compare a save's native gift flags (``gift_rules.toml`` ``track``) with the player's manual marks, read-only.

    python -m clawshot.tracker.audit <seed folder> [--save-folder <folder>] [--slot N] [--marks <file>] [--spoilers]

One line per gift of the seed whose rule has ``track``: each flag and its value, the combined result (any true:
collected; all false: not collected; else unknown), whether the marks file marks it for this seed and save folder,
and a verdict:

- ``agree``: marked and collected, or neither;
- ``disagree``: marked, but the flags say not collected (the flag or the mark is wrong);
- ``no-mark``: collected by the flags but not marked (a mark never made, or a flag set without the gift);
- ``unknown``: the save has no field for a flag, so nothing can be compared.

It ends with the number of disagreements and exits 1 when there are any, 0 otherwise, 2 when the seed, the save or
the marks file cannot be read. It reads the seed, one ``progress.sav`` and the marks file only: it writes nothing and
never starts the game (spec tracker-auto-checks section 6, the oracle for the maintainer's played check). Rewards
are printed only with ``--spoilers``, as in the tracker. A seed made by another version is audited all the same,
after the tracker's note that it reads such seeds' gifts as before.
"""

import argparse
import sys
from pathlib import Path

from clawshot import save as save_format
from clawshot.tracker import marks as tracker_marks
from clawshot.tracker.saves import _marks_key, choose_slot, list_slots, read_complete
from clawshot.tracker.seeds import SeedError, _gift_rules, load_seed
from clawshot.tracker.state import track_field, track_value


class AuditError(Exception):
    pass


def _value(value: bool | None) -> str:
    return "absent" if value is None else "true" if value else "false"


def _field(entry) -> str:
    return track_field(entry) + (f"=={entry.step}" if entry.kind == "quest" else "")


def verdict(collected: bool | None, marked: bool) -> str:
    if collected is None:
        return "unknown"
    if marked:
        return "agree" if collected else "disagree"
    return "no-mark" if collected else "agree"


def audit(
    seed_path: Path, slot: int | None, marks_file: Path | None, spoilers: bool, save_folder: Path | None = None
) -> tuple[list[str], int]:
    """(output lines, disagreements). ``save_folder`` defaults to the seed's own ``user`` folder, as in the tracker."""
    try:
        seed = load_seed(seed_path)
    except (SeedError, OSError) as error:
        raise AuditError(f"cannot read the seed: {error}") from error
    folder = save_folder if save_folder is not None else seed.user_path
    if folder is None:
        raise AuditError(f"{seed.root}: no save folder beside this seed (give --save-folder)")
    chosen = choose_slot(list_slots(folder), slot)
    if chosen is None:
        which = "no save slot" if slot is None else f"no save slot {slot}"
        raise AuditError(f"{folder}: {which} with a progress.sav")
    try:
        parsed = read_complete(Path(chosen["path"]).read_bytes())
    except (save_format.SaveError, OSError) as error:
        raise AuditError(f"{chosen['path']}: {error}") from error
    store = tracker_marks.MarkStore(marks_file)
    marked = store.marks(tracker_marks.seed_identity(seed), _marks_key(chosen["path"]))
    if store.warning:
        raise AuditError(store.warning)
    lines = [w for w in seed.warnings if "need a seed made by" in w]
    lines.append(f"seed {seed.metadata.get('seed')} ({seed.generator}); save {chosen['path']}")
    rules = _gift_rules()
    disagreements = 0
    for check in seed.checks:
        rule = rules.get(check.location)
        if rule is None or not rule.track:
            continue
        values = [track_value(entry, parsed) for entry in rule.track]
        collected = True if any(values) else False if all(v is not None for v in values) else None
        is_marked = check.location in marked
        result = verdict(collected, is_marked)
        disagreements += result == "disagree"
        flags = ", ".join(f"{_field(e)}={_value(v)}" for e, v in zip(rule.track, values, strict=True))
        state = {True: "collected", False: "not collected", None: "unknown"}[collected]
        text = f"{check.location}: {flags} -> {state}; marked: {'yes' if is_marked else 'no'}; {result}"
        if spoilers:
            text += f"; reward: {check.item_label or check.item}"
        lines.append(text)
    lines.append(f"{disagreements} disagreement{'' if disagreements == 1 else 's'}")
    return lines, disagreements


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m clawshot.tracker.audit", description=__doc__.split("\n\n")[0])
    parser.add_argument("seed", type=Path, help="the seed's output folder (or its seed folder or spoiler.json)")
    parser.add_argument(
        "--save-folder",
        type=Path,
        help="the folder holding the save slots, as chosen in the Tracker tab (default: the seed's user folder)",
    )
    parser.add_argument("--slot", type=int, help="the save slot number (default: the newest)")
    parser.add_argument(
        "--marks", type=Path, help="the marks file (default: tracker-marks.json beside the preferences)"
    )
    parser.add_argument("--spoilers", action="store_true", help="also print each gift's reward")
    args = parser.parse_args(argv)
    try:
        lines, disagreements = audit(args.seed, args.slot, args.marks, args.spoilers, args.save_folder)
    except AuditError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 1 if disagreements else 0


if __name__ == "__main__":
    sys.exit(main())
