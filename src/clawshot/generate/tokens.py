"""Gold Skulltula shuffle in a seed (Round 15, issue #30; ``plans/rounds/r15-tokens-spec.md`` with its section 9).

``Token`` is an explicit shuffle kind, off by default (presets unchanged). Off, nothing here applies: Skulltulas
stay ``GS Token`` checks that keep their native token. On:

1. :func:`prepare_spec` makes every ``GS Token`` check of the spec a ``Token`` check. Each is one physical
   Skulltula (every age/Alternative copy of it is the same check), so the pool gets exactly one token per live
   source, never a bonus. All 100 native sources are live after Kareem's rc.3 route packet passed
   (Claude, 2026-11-14); age/Alternative copies still count once.
2. :func:`restrict_settings` holds a ``Token`` check to :data:`REWARDS` (``location_type_items``) and the token
   item to Chest and Token checks (``item_location_types``), so no fill stage, swap or filler can put anything
   else there or a token anywhere else. Explicit settings may narrow these, never widen them: a palette naming
   other items, a token hold outside those kinds, or another item held to Token checks is refused.

:data:`REWARDS` comes from ``data/token_rewards.toml``: each admitted logic item, the native actor whose grant the
check delivers and its native grant family, admitted by played evidence (:data:`ADMITTED_FAMILIES`). The writer
(``clawshot.patch.tokens``) checks each member's native grant shape before any output. Bought goods (``Buy ...``)
are never members: the fill keeps them on shop shelves in every seed (``clawshot.generate.fill.SHOP_ONLY_PREFIX``).

The always-progressive contract needs shuffled chests (``clawshot.generate.progressive.normalize_pool``), so a
selection without Chest, Token alone included, is refused as before.
"""

import tomllib
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any

from clawshot.generate.fill import SHOP_ONLY_PREFIX, FillError, Settings
from clawshot.progressive import CHAINS, FAMILY_BY_ITEM
from clawshot.world.model import World

SHUFFLE = "Token"
"""The shuffle kind, and the location type its checks take in a seed's world."""
SOURCE_TYPE = "GS Token"
"""The world data's (OoT Randomizer's) type of a Gold Skulltula check."""
TOKEN_ITEM = "Gold Skulltula Token"
TOKEN_DESTINATIONS = ("Chest", SHUFFLE)
"""The check kinds a token item may go to: no exact-one native grant is proven for gifts, scrubs, shops or floors."""
ADMITTED_FAMILIES = frozenset(
    {"token", "fixed_major", "equipment", "bottle", "rupee", "heart_piece", "heart_container", "fixed_capacity"}
)
DATA = Path(__file__).resolve().parents[1] / "data" / "token_rewards.toml"


def _load(path: Path = DATA) -> dict[str, tuple[str, str]]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    families = data.get("families", {})
    if set(families) != ADMITTED_FAMILIES or not all(isinstance(text, str) and text for text in families.values()):
        raise ValueError(f"{path.name}: [families] must give the evidence for exactly {sorted(ADMITTED_FAMILIES)}")
    rewards = {}
    for item, info in data.get("rewards", {}).items():
        actor, family, source = (info.get(key) for key in ("actor", "family", "source"))
        if not all(isinstance(value, str) and value for value in (actor, family, source)):
            raise ValueError(f"{path.name}: {item}: needs actor, family and source")
        if family not in ADMITTED_FAMILIES:
            raise ValueError(f"{path.name}: {item}: family {family!r} is not admitted")
        if item in CHAINS or item in FAMILY_BY_ITEM:
            raise ValueError(f"{path.name}: {item}: progressive copies and tiers go only to chests")
        if item.startswith(SHOP_ONLY_PREFIX):
            raise ValueError(f"{path.name}: {item}: bought goods go only to shop shelves")
        if (family == "token") != (item == TOKEN_ITEM):
            raise ValueError(f"{path.name}: {item}: only {TOKEN_ITEM!r} is the token family")
        rewards[item] = (actor, family)
    if TOKEN_ITEM not in rewards:
        raise ValueError(f"{path.name}: {TOKEN_ITEM!r} must be admitted")
    return dict(sorted(rewards.items()))


REWARDS: Mapping[str, tuple[str, str]] = MappingProxyType(_load())
"""Logic item -> (native actor, grant family): the only items a ``Token`` check may give."""


def _retyped(info: Any) -> Any:
    return {**info, "type": SHUFFLE} if isinstance(info, Mapping) and info.get("type") == SOURCE_TYPE else info


def prepare_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """``spec`` with every ``GS Token`` check a ``Token`` check when the seed shuffles ``Token``; unchanged when off.

    The type may be given under ``[locations]`` or with the region's rule; both are retyped. Held and N64-only
    checks are retyped too, but stay unshuffled as for any kind."""
    if SOURCE_TYPE in settings.shuffle:
        raise FillError(f"{SOURCE_TYPE!r} is not a shuffle kind: Gold Skulltulas are shuffled with {SHUFFLE!r}")
    if SHUFFLE not in settings.shuffle:
        return spec
    entries = [*spec.get("locations", {}).items()]
    entries += [entry for region in spec.get("regions", ()) for entry in region.get("locations", {}).items()]
    clash = sorted({name for name, info in entries if isinstance(info, Mapping) and info.get("type") == SHUFFLE})
    if clash:
        raise FillError(f"the world already has {SHUFFLE!r} checks, so Gold Skulltulas cannot take that kind: {clash}")
    return {
        **spec,
        "locations": {name: _retyped(info) for name, info in spec.get("locations", {}).items()},
        "regions": [
            {**region, "locations": {name: _retyped(info) for name, info in region["locations"].items()}}
            if "locations" in region
            else region
            for region in spec.get("regions", ())
        ],
    }


def restrict_settings(world: World, settings: Settings) -> Settings:
    """``settings`` with ``Token`` checks held to :data:`REWARDS` and the token to :data:`TOKEN_DESTINATIONS`, each
    intersected with what the settings already give (a replayed effective settings string gives the same);
    unchanged when the seed does not shuffle ``Token``."""
    if SHUFFLE not in settings.shuffle:
        return settings
    for item in REWARDS:
        info = world.items.get(item)
        if info is not None and (info.dungeon is not None or info.type not in ("Item", "Token")):
            raise FillError(f"token_rewards.toml admits {item!r}, a {info.type} item, which keeps its own holds")
    given = settings.location_type_items.get(SHUFFLE)
    if given is not None and (unsafe := sorted(set(given) - set(REWARDS))):
        raise FillError(
            f"location_type_items gives Token checks {unsafe}, which a Gold Skulltula cannot give; "
            f"admitted: {list(REWARDS)}"
        )
    palette = tuple(item for item in REWARDS if given is None or item in given)
    if not palette:
        raise FillError("location_type_items gives Token checks no item")
    held = dict(settings.item_location_types)
    for item, kinds in held.items():
        if SHUFFLE in kinds and item not in REWARDS:
            raise FillError(f"item_location_types holds {item!r} to Token checks, which cannot give it")
    hold = held.get(TOKEN_ITEM)
    kinds = tuple(kind for kind in TOKEN_DESTINATIONS if hold is None or kind in hold)
    if not kinds:
        raise FillError(
            f"{TOKEN_ITEM} may go only to {list(TOKEN_DESTINATIONS)} checks, but item_location_types holds it to "
            f"{list(hold or ())}"
        )
    held[TOKEN_ITEM] = kinds
    return replace(
        settings,
        location_type_items={**settings.location_type_items, SHUFFLE: palette},
        item_location_types=held,
    )
