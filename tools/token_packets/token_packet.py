"""Read-only checker of the Gold Skulltula core diagnostic packet: Phase 1 of plans/rounds/r15-tokens-spec.md
(section 9, amendment 1) played as section 6's core packet. It compares one packet save with the accepted checkpoint
the packet starts from and says, for one step of the packet, whether the saved state is what that step requires.

    uv run python -m tools.token_packets.token_packet --manifest <json> --baseline <sav> --save <sav> --phase <phase>

Prints one JSON report (:func:`check_packet`); exit 0 pass, 1 fail, 2 unknown (a record a check needs is absent),
3 contract error (bad manifest, unreadable file, a baseline other than the accepted checkpoint or not in the packet's
starting state, a save of another layout). Files are opened read-only; nothing is ever written.

Manifest: a JSON object containing these required checker fields (:func:`parse_manifest`).
Other packet metadata is ignored:

- ``build``: ``"e0f3ccfa"``, the only supported build;
- ``save_version``, ``save_type``: the accepted checkpoint's header version and ``Bool64bitKey`` type hash. A save
  carries no build id; these are its only layout identity, and every save checked must have both;
- ``baseline_sha256``: the accepted checkpoint's SHA256;
- ``source_hashes``: the 100 native primary ``Enemy_Skulltula_Gold`` Hashes (:func:`census_sources`);
- ``house_actor``: the pouch name of the House 10 reward, neither the token, a wallet nor the packet's other
  rewards (the packet assigns ``Item_Hammer``).

Saved records (spec sections 2.1, 2.3 and 6; [S6], [S19] and [S44] of :mod:`clawshot.tracker.state`):

- tokens: ``PouchData.Item_Token_Gold.StockNum`` (key 74668408), the native stock the House reads; never a count
  of sources;
- a Skulltula source is committed when both its ``Bool64bitKey`` records are set: its Hash H and the companion
  H xor 2 (XOR, not H+2: Lone Tree's companion is 2177746409373494989). The save lists only set keys, so with the
  section present a record is set or unset; one record without the other is ``partial``;
- the designated KF Storms Grotto Chest: Bool ``IsTreasureBoxOpen.14818888396401495482``;
- House 10: Bool ``KakarikoVillage_GatheringTokenGold_GetReward10``;
- rewards: ``PouchData.<name>.StockNum`` and ``IsGet.<name>`` of ``Item_Boomerang``, ``Weapon_Shield_Hylian`` (the
  saved item of the ``Obj_Shield_Hylian`` pickup) and the House actor; the same two records of the native wallet
  upgrades ``Item_Wallet_Medium`` (the vanilla House 10 reward) and ``Item_Wallet_Large``. The rupees
  (``PlayerStatus.CurrentRupee``) are reported, never checked: unrelated native play does not fail a step.

``None`` is unknown: a record the save lacks, or every value of a save whose identity does not match the manifest.
It is never read as false or zero.

Steps (:data:`EXPECTATIONS`; each is checked against the baseline, so stock checks are "exactly one more than the
baseline" or "as in the baseline"):

- ``baseline``, ``tree-abandoned``, ``tree-reloaded-uncollected``: 9 tokens, no core source committed, chest
  closed, House 10 unclaimed, no reward granted;
- ``tree-collected``: LLR GS Tree committed, Boomerang granted, still 9 tokens;
- ``tower-collected``: LLR GS Tower committed too, Hylian Shield granted, still 9;
- ``control-collected``: HF GS Lone Tree committed too, 10 tokens;
- ``chest-opened``: chest open, 11 tokens, no further source;
- ``house-claimed``, ``reload``: House 10 claimed, the House actor granted once, still 11 tokens.

In every step the other 97 sources keep both records as in the baseline, and both wallet upgrades keep their stock
and ``IsGet`` (no wallet capacity from any packet reward, the House 10 reward included).

The packet is a diagnostic: forced assignments on a historical checkpoint. A pass is saved-state consistency for that
packet only, not a played proof, not ordinary fill and not a continued playthrough of a new seed. That a Skulltula
source commits on collection rather than on the kill was first reported as a gameplay lead by ootrr (REALAZK);
nothing here comes from its source.
"""

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from clawshot import save
from clawshot.census.scan import GOLD_SKULLTULA, Location

TOOL = "tools.token_packets.token_packet"
BUILD = "e0f3ccfa"
CORE_SOURCES = {"tree": 341792603838029977, "tower": 2730878115209290675, "control": 2177746409373494991}
CHEST_HASH = 14818888396401495482
CHEST_FLAG = f"IsTreasureBoxOpen.{CHEST_HASH}"
HOUSE_FLAG = "KakarikoVillage_GatheringTokenGold_GetReward10"
HOUSE_ACTOR = "Item_Hammer"
TOKEN = "Item_Token_Gold"
TOKEN_STOCK = f"PouchData.{TOKEN}.StockNum"
BOOMERANG = "Item_Boomerang"
HYLIAN_SHIELD = "Weapon_Shield_Hylian"
WALLETS = ("Item_Wallet_Medium", "Item_Wallet_Large")  # the native wallet upgrades (Small is the starting wallet)
RUPEES = "PlayerStatus.CurrentRupee"
SOURCE_COUNT = 100
COMPANION_XOR = 2
ITEM_ROLES = ("boomerang", "hylian_shield", "house")
MANIFEST_FIELDS = ("build", "save_version", "save_type", "baseline_sha256", "source_hashes", "house_actor")
NOT_HOUSE_ACTORS = frozenset({TOKEN, "Item_Wallet_Small", *WALLETS, BOOMERANG, HYLIAN_SHIELD})

SET, UNSET, PARTIAL, UNKNOWN = "set", "unset", "partial", "unknown"
PASS, FAIL, CONTRACT_ERROR = "pass", "fail", "contract_error"
EXIT_CODES = {PASS: 0, FAIL: 1, UNKNOWN: 2, CONTRACT_ERROR: 3}
DIAGNOSTIC = (
    "Phase 1 core diagnostic packet: forced assignments (Boomerang at LLR GS Tree, Hylian Shield at LLR GS Tower, "
    "HF GS Lone Tree as the token control, a token in KF Storms Grotto Chest, a non-token House 10 reward) on a "
    "historical checkpoint; a pass is saved-state consistency only, not a played proof, not ordinary fill and not a "
    "continued seed"
)


def companion(source: int) -> int:
    """The second saved record of a Skulltula source: its Hash xor 2 (spec section 2.1)."""
    return source ^ COMPANION_XOR


@dataclass(frozen=True)
class Expectation:
    tokens: int  # PouchData.Item_Token_Gold.StockNum
    committed: frozenset[str]  # CORE_SOURCES names with both records set
    chest_open: bool
    house10: bool
    granted: frozenset[str]  # ITEM_ROLES granted once since the baseline


_START = Expectation(9, frozenset(), False, False, frozenset())
_TREE = Expectation(9, frozenset({"tree"}), False, False, frozenset({"boomerang"}))
_TOWER = Expectation(9, frozenset({"tree", "tower"}), False, False, frozenset({"boomerang", "hylian_shield"}))
_CONTROL = replace(_TOWER, tokens=10, committed=frozenset(CORE_SOURCES))
_CHEST = replace(_CONTROL, tokens=11, chest_open=True)
_HOUSE = replace(_CHEST, house10=True, granted=_CHEST.granted | {"house"})
EXPECTATIONS: dict[str, Expectation] = {
    "baseline": _START,
    "tree-abandoned": _START,
    "tree-reloaded-uncollected": _START,
    "tree-collected": _TREE,
    "tower-collected": _TOWER,
    "control-collected": _CONTROL,
    "chest-opened": _CHEST,
    "house-claimed": _HOUSE,
    "reload": _HOUSE,
}
PHASES = tuple(EXPECTATIONS)


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class Manifest:
    build: str
    save_version: int
    save_type: int
    baseline_sha256: str  # lower-case hex
    source_hashes: tuple[int, ...]  # sorted
    house_actor: str

    def actors(self) -> dict[str, str]:
        """Pouch name of each rewarded item, by :data:`ITEM_ROLES` role."""
        return {"boomerang": BOOMERANG, "hylian_shield": HYLIAN_SHIELD, "house": self.house_actor}


def _unsigned(value: object, what: str, bits: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 1 << bits:
        raise ManifestError(f"{what} must be an unsigned {bits}-bit integer, not {value!r}")
    return value


def parse_manifest(raw: object) -> Manifest:
    """Validate a decoded manifest object (module docstring); :class:`ManifestError` names the first problem."""
    if not isinstance(raw, Mapping):
        raise ManifestError(f"the manifest must be a JSON object, not {type(raw).__name__}")
    missing = [field for field in MANIFEST_FIELDS if field not in raw]
    if missing:
        raise ManifestError(f"manifest fields: missing {missing}")
    if raw["build"] != BUILD:
        raise ManifestError(f"build {raw['build']!r}: only build {BUILD} is supported")
    version = _unsigned(raw["save_version"], "save_version", 32)
    save_type = _unsigned(raw["save_type"], "save_type", 32)
    digest = raw["baseline_sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
        raise ManifestError(f"baseline_sha256 must be 64 hex digits, not {digest!r}")
    listed = raw["source_hashes"]
    if not isinstance(listed, list):
        raise ManifestError(f"source_hashes must be a list, not {type(listed).__name__}")
    hashes = [_unsigned(h, "a source Hash", 64) for h in listed]
    sources = set(hashes)
    if len(hashes) != SOURCE_COUNT or len(sources) != SOURCE_COUNT:
        raise ManifestError(
            f"source_hashes holds {len(hashes)} Hashes, {len(sources)} distinct; expected {SOURCE_COUNT} distinct"
        )
    absent = {name: h for name, h in CORE_SOURCES.items() if h not in sources}
    if absent:
        raise ManifestError(f"source_hashes lacks core source(s) {absent}")
    clashes = sorted(h for h in sources if companion(h) in sources)
    if clashes:
        raise ManifestError(f"source Hashes whose companion (Hash xor 2) is another source: {clashes}")
    records = sources | {companion(h) for h in sources}
    if 0 in records:
        raise ManifestError("a source record would be key 0, the Bool64bitKey list's terminator")
    if CHEST_HASH in records:
        raise ManifestError(f"the designated chest's Hash {CHEST_HASH} is a source record")
    house = raw["house_actor"]
    if not isinstance(house, str) or not re.fullmatch(r"[A-Za-z0-9_]+", house) or house in NOT_HOUSE_ACTORS:
        raise ManifestError(
            f"house_actor {house!r} must be a pouch name other than {TOKEN}, a wallet, {BOOMERANG} or {HYLIAN_SHIELD}"
        )
    return Manifest(BUILD, version, save_type, digest.lower(), tuple(sorted(sources)), house)


def load_manifest(path: str | Path) -> Manifest:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ManifestError(f"{path}: not JSON ({error})") from error
    return parse_manifest(raw)


def census_sources(census: Iterable[Location]) -> tuple[int, ...]:
    """The native primary Gold Skulltula Hashes of a census (:func:`clawshot.census.scan.scan`), sorted: the
    manifest's ``source_hashes``."""
    return tuple(sorted({location.id for location in census if location.kind == GOLD_SKULLTULA}))


@dataclass(frozen=True)
class Pair:
    """Both saved records of one Skulltula source."""

    source: int
    primary: bool | None  # the Hash's Bool64bitKey record is set
    companion: bool | None  # the companion's (Hash xor 2) record is set

    @property
    def state(self) -> str:
        if self.primary is None or self.companion is None:
            return UNKNOWN
        if self.primary and self.companion:
            return SET
        return PARTIAL if self.primary or self.companion else UNSET

    def records(self) -> dict[str, bool | None]:
        return {"primary_set": self.primary, "companion_set": self.companion}

    def to_json(self) -> dict[str, Any]:
        return {"hash": self.source, "companion_hash": companion(self.source), **self.records(), "state": self.state}


@dataclass(frozen=True)
class Item:
    actor: str  # pouch name
    stock: int | None  # PouchData.<actor>.StockNum
    isget: bool | None  # IsGet.<actor>


@dataclass(frozen=True)
class Snapshot:
    """The packet's records in one save. ``identity`` lists why the save does not match the manifest; when it is
    not empty every value is None."""

    sha256: str
    version: int | None
    save_type: int | None
    identity: tuple[str, ...]
    tokens: int | None
    token_isget: bool | None
    pairs: Mapping[int, Pair]  # every manifest source, by Hash
    chest_open: bool | None
    house10: bool | None
    items: Mapping[str, Item]  # by ITEM_ROLES role
    wallets: Mapping[str, Item]  # by WALLETS pouch name
    rupees: int | None

    @property
    def trusted(self) -> bool:
        return not self.identity

    def core(self, name: str) -> Pair:
        return self.pairs[CORE_SOURCES[name]]

    def to_json(self) -> dict[str, Any]:
        core = set(CORE_SOURCES.values())
        others = [pair.state for source, pair in self.pairs.items() if source not in core]
        return {
            "sha256": self.sha256,
            "version": self.version,
            "save_type": self.save_type,
            "trusted": self.trusted,
            "identity": list(self.identity),
            "tokens": {"record": TOKEN_STOCK, "stock": self.tokens, "isget": self.token_isget},
            "core_sources": {name: self.core(name).to_json() for name in CORE_SOURCES},
            "chest": {"hash": CHEST_HASH, "record": CHEST_FLAG, "open": self.chest_open},
            "house10": {"record": HOUSE_FLAG, "claimed": self.house10},
            "items": {role: asdict(item) for role, item in self.items.items()},
            "wallets": {name: asdict(item) for name, item in self.wallets.items()},
            "rupees": self.rupees,
            "other_sources": {"count": len(others), **{s: others.count(s) for s in (SET, UNSET, PARTIAL, UNKNOWN)}},
        }


def _unknown_snapshot(
    digest: str, manifest: Manifest, version: int | None, save_type: int | None, identity: tuple[str, ...]
) -> Snapshot:
    return Snapshot(
        sha256=digest,
        version=version,
        save_type=save_type,
        identity=identity,
        tokens=None,
        token_isget=None,
        pairs={h: Pair(h, None, None) for h in manifest.source_hashes},
        chest_open=None,
        house10=None,
        items={role: Item(actor, None, None) for role, actor in manifest.actors().items()},
        wallets={wallet: Item(wallet, None, None) for wallet in WALLETS},
        rupees=None,
    )


def _stock(parsed: save.Save, actor: str) -> int | None:
    return parsed.int_value(f"PouchData.{actor}.StockNum")


def snapshot(data: bytes, manifest: Manifest) -> Snapshot:
    """Read the packet's records from save bytes (``clawshot.save.read``). A save that does not read, or whose
    version, type or ``Bool64bitKey`` section does not match the manifest, gives every value None."""
    digest = hashlib.sha256(data).hexdigest()
    try:
        parsed = save.read(data)
    except save.SaveError as error:
        return _unknown_snapshot(digest, manifest, None, None, (f"unreadable save: {error}",))
    identity = []
    if parsed.version != manifest.save_version:
        identity.append(f"save version 0x{parsed.version:x}, manifest 0x{manifest.save_version:x}")
    if parsed.save_type is None:
        identity.append("no Bool64bitKey section: the Skulltula source records are unknown")
    elif parsed.save_type != manifest.save_type:
        identity.append(f"save type 0x{parsed.save_type:08x}, manifest 0x{manifest.save_type:08x}")
    if identity:
        return _unknown_snapshot(digest, manifest, parsed.version, parsed.save_type, tuple(identity))
    return Snapshot(
        sha256=digest,
        version=parsed.version,
        save_type=parsed.save_type,
        identity=(),
        tokens=parsed.int_value(TOKEN_STOCK),
        token_isget=parsed.flag(f"IsGet.{TOKEN}"),
        pairs={h: Pair(h, parsed.is_set(h), parsed.is_set(companion(h))) for h in manifest.source_hashes},
        chest_open=parsed.flag(CHEST_FLAG),
        house10=parsed.flag(HOUSE_FLAG),
        items={
            role: Item(actor, _stock(parsed, actor), parsed.flag(f"IsGet.{actor}"))
            for role, actor in manifest.actors().items()
        },
        wallets={wallet: Item(wallet, _stock(parsed, wallet), parsed.flag(f"IsGet.{wallet}")) for wallet in WALLETS},
        rupees=parsed.int_value(RUPEES),
    )


@dataclass(frozen=True)
class Check:
    id: str
    scope: str  # "baseline" (the packet's starting state) or "save" (the step)
    status: str  # pass, fail or unknown
    expected: Any
    actual: Any
    detail: str

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


def _why(snap: Snapshot) -> str:
    return "; ".join(snap.identity) if snap.identity else "no such record in the save"


def _value(check_id: str, scope: str, record: str, expected: object, actual: object, snap: Snapshot) -> Check:
    if actual is None:
        return Check(check_id, scope, UNKNOWN, expected, None, f"{record}: {_why(snap)}")
    return Check(check_id, scope, PASS if actual == expected else FAIL, expected, actual, record)


def _pair(scope: str, name: str, pair: Pair, committed: bool, snap: Snapshot) -> Check:
    want, state = (SET if committed else UNSET), pair.state
    records = f"Bool64bitKey {pair.source} and its companion {companion(pair.source)} (Hash xor 2)"
    if state == UNKNOWN:
        return Check(f"source.{name}", scope, UNKNOWN, want, state, f"{records}: {_why(snap)}")
    if state == PARTIAL:
        records += f": only the {'Hash' if pair.primary else 'companion'} record is set"
    return Check(f"source.{name}", scope, PASS if state == want else FAIL, want, state, records)


def _item(scope: str, role: str, reference: Item, current: Item, granted: bool, snap: Snapshot) -> Check:
    """``reference`` is the baseline's item for a step, a never-owned item (stock 0, IsGet false) for the baseline."""
    check_id = f"item.{role}"
    record = f"PouchData.{current.actor}.StockNum, IsGet.{current.actor}"
    actual = {"stock": current.stock, "isget": current.isget}
    if reference.stock is None or (not granted and reference.isget is None):
        return Check(check_id, scope, UNKNOWN, None, actual, f"{record}: unknown in the baseline")
    if granted:
        expected = {"stock": reference.stock + 1, "isget": True}
    else:
        expected = {"stock": reference.stock, "isget": reference.isget}
    if current.stock is None or current.isget is None:
        return Check(check_id, scope, UNKNOWN, expected, actual, f"{record}: {_why(snap)}")
    if scope == "baseline":
        meaning = "never owned before the packet"
    else:
        meaning = f"{'granted exactly once' if granted else 'not granted'} since the baseline"
    return Check(check_id, scope, PASS if actual == expected else FAIL, expected, actual, f"{record}: {meaning}")


def _wallets(baseline: Snapshot, current: Snapshot) -> Check:
    expected = {name: {"stock": item.stock, "isget": item.isget} for name, item in baseline.wallets.items()}
    actual = {name: {"stock": item.stock, "isget": item.isget} for name, item in current.wallets.items()}
    detail = "wallet upgrades' StockNum and IsGet as in the baseline: no packet reward grants wallet capacity"
    if any(None in values.values() for side in (expected, actual) for values in side.values()):
        why = "; ".join(current.identity) or "a wallet record is absent from the baseline or the save"
        return Check("wallets", "save", UNKNOWN, expected, actual, f"{detail}; {why}")
    return Check("wallets", "save", PASS if actual == expected else FAIL, expected, actual, detail)


def _other_sources(baseline: Snapshot, current: Snapshot) -> Check:
    core = set(CORE_SOURCES.values())
    others = [source for source in baseline.pairs if source not in core]
    detail = f"both records of the {len(others)} other Skulltula sources as in the baseline"
    pairs = [(baseline.pairs[s], current.pairs[s]) for s in others]
    if any(UNKNOWN in (before.state, after.state) for before, after in pairs):
        why = "; ".join(filter(None, (*baseline.identity, *current.identity)))
        return Check("sources.others", "save", UNKNOWN, [], None, f"{detail}; {why}")
    changed = [
        {"hash": before.source, "baseline": before.records(), "save": after.records()}
        for before, after in pairs
        if before.records() != after.records()
    ]
    return Check("sources.others", "save", FAIL if changed else PASS, [], changed, detail)


def baseline_checks(baseline: Snapshot) -> list[Check]:
    """The packet's starting state in the baseline: 9 tokens, no core source, chest closed, House 10 unclaimed and
    no rewarded item ever owned (stock 0, IsGet false), including the chosen House actor."""
    start = EXPECTATIONS["baseline"]
    return [
        _value("tokens", "baseline", TOKEN_STOCK, start.tokens, baseline.tokens, baseline),
        *(_pair("baseline", name, baseline.core(name), False, baseline) for name in CORE_SOURCES),
        _value("chest", "baseline", CHEST_FLAG, start.chest_open, baseline.chest_open, baseline),
        _value("house10", "baseline", HOUSE_FLAG, start.house10, baseline.house10, baseline),
        *(
            _item("baseline", role, Item(item.actor, 0, False), item, False, baseline)
            for role, item in baseline.items.items()
        ),
    ]


def phase_checks(phase: str, baseline: Snapshot, current: Snapshot) -> list[Check]:
    """The step ``phase`` (:data:`PHASES`) in ``current``, against ``baseline``."""
    want = EXPECTATIONS[phase]
    return [
        _value("tokens", "save", TOKEN_STOCK, want.tokens, current.tokens, current),
        *(_pair("save", name, current.core(name), name in want.committed, current) for name in CORE_SOURCES),
        _value("chest", "save", CHEST_FLAG, want.chest_open, current.chest_open, current),
        _value("house10", "save", HOUSE_FLAG, want.house10, current.house10, current),
        *(
            _item("save", role, baseline.items[role], current.items[role], role in want.granted, current)
            for role in ITEM_ROLES
        ),
        _wallets(baseline, current),
        _other_sources(baseline, current),
    ]


def contract_issues(manifest: Manifest, baseline: Snapshot, current: Snapshot) -> list[str]:
    issues = []
    if baseline.sha256 != manifest.baseline_sha256:
        issues.append(f"baseline SHA256 {baseline.sha256}, manifest {manifest.baseline_sha256}")
    issues += [f"baseline: {issue}" for issue in baseline.identity]
    issues += [f"save: {issue}" for issue in current.identity]
    return issues


def verdict(contract: Iterable[str], checks: Iterable[Check]) -> str:
    """contract_error when the inputs are not what the manifest says (including a baseline check that does not
    pass), else fail when a check fails, else unknown when one is unknown, else pass."""
    checks = list(checks)
    if list(contract) or any(c.scope == "baseline" and c.status != PASS for c in checks):
        return CONTRACT_ERROR
    statuses = {c.status for c in checks}
    return FAIL if FAIL in statuses else UNKNOWN if UNKNOWN in statuses else PASS


def check_packet(manifest: Manifest, baseline_data: bytes, save_data: bytes, phase: str) -> dict[str, Any]:
    """The JSON-able report of one packet step: verdict, exit code, contract issues, every check and both
    snapshots."""
    if phase not in EXPECTATIONS:
        raise ValueError(f"phase {phase!r} is not one of {', '.join(PHASES)}")
    baseline, current = snapshot(baseline_data, manifest), snapshot(save_data, manifest)
    contract = contract_issues(manifest, baseline, current)
    checks = [*baseline_checks(baseline), *phase_checks(phase, baseline, current)]
    result = verdict(contract, checks)
    return {
        "tool": TOOL,
        "build": manifest.build,
        "phase": phase,
        "verdict": result,
        "exit_code": EXIT_CODES[result],
        "contract": contract,
        "counts": {status: sum(c.status == status for c in checks) for status in (PASS, FAIL, UNKNOWN)},
        "checks": [c.to_json() for c in checks],
        "baseline": baseline.to_json(),
        "save": current.to_json(),
        "same_bytes_as_baseline": baseline.sha256 == current.sha256,
        "house_actor": manifest.house_actor,
        "scope": DIAGNOSTIC,
    }


def _read_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=f"python -m {TOOL}", description="Check a Gold Skulltula core packet save (read-only; JSON report)."
    )
    parser.add_argument("--manifest", required=True, type=Path, help="packet manifest (JSON)")
    parser.add_argument("--baseline", required=True, type=Path, help="the accepted checkpoint's progress.sav")
    parser.add_argument("--save", required=True, type=Path, help="the packet step's progress.sav")
    parser.add_argument("--phase", required=True, choices=PHASES, help="the packet step the save was taken at")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        baseline_data = _read_bytes(args.baseline)
        save_data = _read_bytes(args.save)
    except (OSError, ManifestError) as error:
        exit_code = EXIT_CODES[CONTRACT_ERROR]
        result = {"tool": TOOL, "phase": args.phase, "verdict": CONTRACT_ERROR, "exit_code": exit_code}
        result["contract"] = [str(error)]
    else:
        result = check_packet(manifest, baseline_data, save_data, args.phase)
    result["paths"] = {"manifest": str(args.manifest), "baseline": str(args.baseline), "save": str(args.save)}
    print(json.dumps(result, indent=2))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
