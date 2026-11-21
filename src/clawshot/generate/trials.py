"""Seeded remaining trials, independent of placement RNG (round20 provisional policy)."""

import random
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from clawshot.generate.fill import Settings

TRIALS = ("Forest", "Fire", "Water", "Shadow", "Spirit", "Light")


def remaining(seed: int, count: int) -> tuple[str, ...]:
    """Canonical-order selection from a dedicated stream; six is exactly the native set."""
    if type(count) is not int or not 0 <= count <= 6:
        raise ValueError("trials_count must be an integer from 0 to 6")
    if count == 6:
        return TRIALS
    selected = random.Random(f"clawshot.trials.v1:{seed}").sample(TRIALS, count)
    return tuple(name for name in TRIALS if name in selected)


def prepare_spec(spec: Mapping[str, Any], settings: "Settings", seed: int) -> Mapping[str, Any]:
    """The native tower rule reads precisely the trials the output leaves uncleared."""
    if settings.trials_count == 6:
        return spec
    active = remaining(seed, settings.trials_count)
    skipped = {name: name not in active for name in TRIALS}
    if "skipped_trials" in settings.logic and settings.logic["skipped_trials"] != skipped:
        raise ValueError("skipped_trials is selected by trials_count and the seed; remove that logic override")
    return {**spec, "flags": {**spec.get("flags", {}), "skipped_trials": skipped}}
