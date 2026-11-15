"""Read-only checker of an approved Gold Skulltula diagnostic packet: forced rewards at chosen Skulltula sources,
played from an accepted checkpoint (plans/rounds/r15-scrub-tokens.md). Reward-family packets force non-token rewards;
route packets may also keep a source's native token. It compares one packet save with that checkpoint and says, for
one phase of the packet, whether the saved state is what the manifest requires.

    uv run python -m tools.token_packets.token_family_packet --manifest <json> --baseline <sav> --save <sav>
        --phase <phase>

Prints one JSON report (:func:`check_packet`); exit 0 pass, 1 fail, 2 unknown (a record a check needs is absent),
3 contract error (bad manifest, unreadable file, a phase the manifest does not list, a baseline other than the accepted
checkpoint or not in the manifest's ``baseline`` state, a save of another layout). The conventions are those of the
core packet checker (:mod:`tools.token_packets.token_packet`). Files are opened read-only; nothing is ever written.

Manifest: a JSON object with these fields (:func:`parse_manifest`); other keys, at the top or in an assignment, are
packet metadata and ignored:

- ``build``: ``"e0f3ccfa"``, the only supported build;
- ``save_version``, ``save_type``: the accepted checkpoint's header version and ``Bool64bitKey`` type hash, a save's
  only layout identity; every save checked must have both;
- ``baseline_sha256``: the accepted checkpoint's SHA256;
- ``source_hashes``: the 100 native primary ``Enemy_Skulltula_Gold`` Hashes (``token_packet.census_sources``), JSON
  integers or decimal strings;
- ``assignments``: the forced rewards, ``{"id": <decimal source Hash>, "name", "family", "actor"}``: a source of
  ``source_hashes`` at most once, the location's name, the reward family and the reward's actor. A native token is
  declared as family ``token`` with actor ``Item_Token_Gold`` and only so: that actor in another family, another actor
  in that family, or the world token ``Obj_Token_Gold`` as an actor, is refused;
- ``phases``: phase name -> ``{"completed": [<assignment id>, ...], "fields": [{"name", "kind", "value"}, ...]}``,
  including ``baseline``, whose ``completed`` is empty. A field's ``name`` is a GameDataList name (read by its murmur3
  key) or an integer raw key; ``kind`` is ``int`` (a signed 32-bit value), ``bool`` or ``enum`` (the raw key of the
  current value, the murmur3 of its name; ``clawshot.save.Save.enum_value``). Every phase lists at least one field.

Saved records (spec sections 2.1 and 2.3; ``token_packet``):

- a Skulltula source is committed when both its ``Bool64bitKey`` records are set: its Hash H and the companion H xor 2.
  The save lists only set keys, so with the section present a record is set or unset; one without the other is
  ``partial``;
- tokens: ``PouchData.Item_Token_Gold.StockNum``, the native stock, never a count of sources.

Checks. The baseline, in ``baseline`` scope (anything but a pass there is a contract error): its SHA256 and layout are
the manifest's, its token stock is recorded, every assigned source is unset and every ``baseline`` field has its value.
The phase's save, in ``save`` scope: the token stock is the baseline's plus one per native-token assignment the phase
lists in ``completed`` (no other reward adds a token, and there is no other way to expect one); each assigned source is
committed exactly when the phase lists it in ``completed`` (``partial`` fails); every field of the phase has its value;
and both records of every other source are as in the baseline. ``None`` is unknown, a record the save lacks or every
value of a save whose identity does not match the manifest; it is never read as false or zero.

A pass is saved-state consistency for that packet only: not a played proof, not the admission of a family or a route
to production fill and not a continued playthrough of a seed.
"""

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clawshot import save
from tools.token_packets.token_packet import (
    BUILD,
    CONTRACT_ERROR,
    EXIT_CODES,
    FAIL,
    PARTIAL,
    PASS,
    SET,
    SOURCE_COUNT,
    TOKEN,
    TOKEN_STOCK,
    UNKNOWN,
    UNSET,
    Check,
    ManifestError,
    Pair,
    companion,
    verdict,
)

TOOL = "tools.token_packets.token_family_packet"
MANIFEST_FIELDS = ("build", "save_version", "save_type", "baseline_sha256", "source_hashes", "assignments", "phases")
ASSIGNMENT_FIELDS = ("id", "name", "family", "actor")
BASELINE = "baseline"
INT, BOOL, ENUM = "int", "bool", "enum"
KINDS = {INT: save.INT, BOOL: save.BOOL, ENUM: save.ENUM}
TOKEN_FAMILY = "token"  # a source that keeps its native token: declared with actor TOKEN and only so
WORLD_TOKEN = "Obj_Token_Gold"  # the native token's world actor, never an assignment's actor
SCOPE = (
    "Gold Skulltula diagnostic packet: forced rewards (reward families, or native tokens on a route) at chosen "
    "Skulltula sources on a historical checkpoint; a pass is saved-state consistency only, not a played proof, not "
    "a family's or a route's admission to production fill and not a continued seed"
)


@dataclass(frozen=True)
class Field:
    """One typed saved value a phase requires."""

    name: str | int  # a GameDataList name, or a raw key
    kind: str  # int, bool or enum
    value: int | bool

    @property
    def key(self) -> int:
        return save.key(self.name)

    @property
    def record(self) -> str:
        label = self.name if isinstance(self.name, str) else f"key 0x{self.name:08x}"
        return f"{save.TYPES[KINDS[self.kind]]} {label}"

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "kind": self.kind, "key": self.key, "value": self.value}


@dataclass(frozen=True)
class Assignment:
    source: int
    name: str
    family: str
    actor: str

    def to_json(self) -> dict[str, Any]:
        return {"id": str(self.source), "name": self.name, "family": self.family, "actor": self.actor}

    @property
    def native_token(self) -> bool:
        return self.family == TOKEN_FAMILY


@dataclass(frozen=True)
class Phase:
    completed: frozenset[int]  # assigned sources committed by this phase
    fields: tuple[Field, ...]


@dataclass(frozen=True)
class Manifest:
    build: str
    save_version: int
    save_type: int
    baseline_sha256: str  # lower-case hex
    source_hashes: tuple[int, ...]  # sorted
    assignments: tuple[Assignment, ...]  # in manifest order
    phases: Mapping[str, Phase]  # in manifest order

    def assigned(self) -> frozenset[int]:
        return frozenset(a.source for a in self.assignments)

    def tokens_added(self, phase: str) -> int:
        """Native tokens the phase has collected: its ``completed`` native-token assignments."""
        completed = self.phases[phase].completed
        return sum(a.native_token and a.source in completed for a in self.assignments)


def _unsigned(value: object, what: str, bits: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 1 << bits:
        raise ManifestError(f"{what} must be an unsigned {bits}-bit integer, not {value!r}")
    return value


def _decimal(value: object, what: str) -> int:
    """A canonical decimal string (ASCII digits, no sign or leading zero) of an unsigned 64-bit integer."""
    if not isinstance(value, str) or not re.fullmatch(r"0|[1-9][0-9]*", value) or int(value) >= 1 << 64:
        raise ManifestError(f"{what} must be a decimal string of an unsigned 64-bit integer, not {value!r}")
    return int(value)


def _text(value: object, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{what} must be a non-empty string, not {value!r}")
    return value


def _sources(listed: object) -> tuple[int, ...]:
    if not isinstance(listed, list):
        raise ManifestError(f"source_hashes must be a list, not {type(listed).__name__}")
    hashes = [_decimal(h, "a source Hash") if isinstance(h, str) else _unsigned(h, "a source Hash", 64) for h in listed]
    sources = set(hashes)
    if len(hashes) != SOURCE_COUNT or len(sources) != SOURCE_COUNT:
        raise ManifestError(
            f"source_hashes holds {len(hashes)} Hashes, {len(sources)} distinct; expected {SOURCE_COUNT} distinct"
        )
    clashes = sorted(h for h in sources if companion(h) in sources)
    if clashes:
        raise ManifestError(f"source Hashes whose companion (Hash xor 2) is another source: {clashes}")
    if 0 in sources | {companion(h) for h in sources}:
        raise ManifestError("a source record would be key 0, the Bool64bitKey list's terminator")
    return tuple(sorted(sources))


def _assignments(listed: object, sources: Iterable[int]) -> tuple[Assignment, ...]:
    if not isinstance(listed, list) or not listed:
        raise ManifestError(f"assignments must be a non-empty list, not {listed!r}")
    known, out, seen = set(sources), [], set()
    for n, row in enumerate(listed):
        where = f"assignments[{n}]"
        if not isinstance(row, Mapping):
            raise ManifestError(f"{where} must be an object, not {type(row).__name__}")
        missing = [name for name in ASSIGNMENT_FIELDS if name not in row]
        if missing:
            raise ManifestError(f"{where}: missing {missing}")
        source = _decimal(row["id"], f"{where}.id")
        if source not in known:
            raise ManifestError(f"{where}.id {source} is not one of source_hashes")
        if source in seen:
            raise ManifestError(f"{where}.id {source} is assigned twice")
        seen.add(source)
        actor = row["actor"]
        if not isinstance(actor, str) or not re.fullmatch(r"[A-Za-z0-9_]+", actor) or actor == WORLD_TOKEN:
            raise ManifestError(f"{where}.actor {actor!r} must be a pouch or pickup actor name, not {WORLD_TOKEN}")
        name, family = _text(row["name"], f"{where}.name"), _text(row["family"], f"{where}.family")
        if (family == TOKEN_FAMILY) != (actor == TOKEN):
            raise ManifestError(
                f"{where}: family {family!r} with actor {actor!r}; a native token is family {TOKEN_FAMILY!r} with "
                f"actor {TOKEN} and only so"
            )
        out.append(Assignment(source, name, family, actor))
    return tuple(out)


def _field(raw: object, where: str) -> Field:
    if not isinstance(raw, Mapping):
        raise ManifestError(f"{where} must be an object, not {type(raw).__name__}")
    missing = [name for name in ("name", "kind", "value") if name not in raw]
    if missing:
        raise ManifestError(f"{where}: missing {missing}")
    name, kind, value = raw["name"], raw["kind"], raw["value"]
    if isinstance(name, int) and not isinstance(name, bool):
        if not 0 < name < 1 << 32:
            raise ManifestError(f"{where}.name: a raw key must be a nonzero unsigned 32-bit integer, not {name}")
    else:
        name = _text(name, f"{where}.name")
    if kind not in KINDS:
        raise ManifestError(f"{where}.kind must be one of {', '.join(KINDS)}, not {kind!r}")
    if kind == BOOL:
        if not isinstance(value, bool):
            raise ManifestError(f"{where}.value must be true or false for a bool field, not {value!r}")
    elif kind == INT:
        if isinstance(value, bool) or not isinstance(value, int) or not -(1 << 31) <= value < 1 << 31:
            raise ManifestError(f"{where}.value must be a signed 32-bit integer for an int field, not {value!r}")
    else:
        _unsigned(value, f"{where}.value (an enum value's raw key)", 32)
    return Field(name, kind, value)


def _phases(raw: object, assigned: frozenset[int]) -> dict[str, Phase]:
    if not isinstance(raw, Mapping) or BASELINE not in raw:
        raise ManifestError(f"phases must be an object that includes {BASELINE!r}")
    out = {}
    for name, body in raw.items():
        where = f"phases[{name!r}]"
        _text(name, "a phase name")
        if not isinstance(body, Mapping) or "completed" not in body or "fields" not in body:
            raise ManifestError(f"{where} must be an object with completed and fields")
        listed = body["completed"]
        if not isinstance(listed, list):
            raise ManifestError(f"{where}.completed must be a list, not {type(listed).__name__}")
        completed = [_decimal(i, f"{where}.completed entry") for i in listed]
        if len(set(completed)) != len(completed):
            raise ManifestError(f"{where}.completed lists a source twice")
        stray = sorted(set(completed) - assigned)
        if stray:
            raise ManifestError(f"{where}.completed names unassigned source(s) {stray}")
        if name == BASELINE and completed:
            raise ManifestError(f"{where}.completed must be empty: an assigned source starts uncollected")
        fields = body["fields"]
        if not isinstance(fields, list) or not fields:
            raise ManifestError(f"{where}.fields must be a non-empty list")
        parsed = tuple(_field(f, f"{where}.fields[{n}]") for n, f in enumerate(fields))
        records = [(f.kind, f.key) for f in parsed]
        if len(set(records)) != len(records):
            raise ManifestError(f"{where}.fields names one saved record twice")
        out[name] = Phase(frozenset(completed), parsed)
    return out


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
    sources = _sources(raw["source_hashes"])
    assignments = _assignments(raw["assignments"], sources)
    phases = _phases(raw["phases"], frozenset(a.source for a in assignments))
    return Manifest(BUILD, version, save_type, digest.lower(), sources, assignments, phases)


def load_manifest(path: str | Path) -> Manifest:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ManifestError(f"{path}: not JSON ({error})") from error
    return parse_manifest(raw)


@dataclass(frozen=True)
class Snapshot:
    """The packet's records in one save. ``identity`` lists why the save does not match the manifest; when it is
    not empty every value is None."""

    sha256: str
    version: int | None
    save_type: int | None
    identity: tuple[str, ...]
    tokens: int | None
    pairs: Mapping[int, Pair]  # every manifest source, by Hash
    parsed: save.Save | None  # None when ``identity`` is not empty

    def value(self, field: Field) -> int | bool | None:
        if self.parsed is None:
            return None
        if field.kind == INT:
            return self.parsed.int_value(field.key)
        if field.kind == BOOL:
            return self.parsed.flag(field.key)
        return self.parsed.enum_value(field.key)

    def to_json(self, manifest: Manifest, phase: Phase) -> dict[str, Any]:
        assigned = manifest.assigned()
        others = [pair.state for source, pair in self.pairs.items() if source not in assigned]
        return {
            "sha256": self.sha256,
            "version": self.version,
            "save_type": self.save_type,
            "trusted": not self.identity,
            "identity": list(self.identity),
            "tokens": {"record": TOKEN_STOCK, "stock": self.tokens},
            "assigned_sources": {str(a.source): self.pairs[a.source].to_json() for a in manifest.assignments},
            "other_sources": {"count": len(others), **{s: others.count(s) for s in (SET, UNSET, PARTIAL, UNKNOWN)}},
            "fields": [{**field.to_json(), "value": self.value(field)} for field in phase.fields],
        }


def snapshot(data: bytes, manifest: Manifest) -> Snapshot:
    """Read the packet's records from save bytes (``clawshot.save.read``). A save that does not read, or whose
    version, type or ``Bool64bitKey`` section does not match the manifest, gives every value None."""
    digest = hashlib.sha256(data).hexdigest()
    unknown = {h: Pair(h, None, None) for h in manifest.source_hashes}
    try:
        parsed = save.read(data)
    except save.SaveError as error:
        return Snapshot(digest, None, None, (f"unreadable save: {error}",), None, unknown, None)
    identity = []
    if parsed.version != manifest.save_version:
        identity.append(f"save version 0x{parsed.version:x}, manifest 0x{manifest.save_version:x}")
    if parsed.save_type is None:
        identity.append("no Bool64bitKey section: the Skulltula source records are unknown")
    elif parsed.save_type != manifest.save_type:
        identity.append(f"save type 0x{parsed.save_type:08x}, manifest 0x{manifest.save_type:08x}")
    if identity:
        return Snapshot(digest, parsed.version, parsed.save_type, tuple(identity), None, unknown, None)
    pairs = {h: Pair(h, parsed.is_set(h), parsed.is_set(companion(h))) for h in manifest.source_hashes}
    return Snapshot(digest, parsed.version, parsed.save_type, (), parsed.int_value(TOKEN_STOCK), pairs, parsed)


def _why(snap: Snapshot) -> str:
    return "; ".join(snap.identity) if snap.identity else "no such record in the save"


def _source(scope: str, assignment: Assignment, pair: Pair, committed: bool, snap: Snapshot) -> Check:
    check_id = f"source.{assignment.source}"
    want, state = (SET if committed else UNSET), pair.state
    records = (
        f"{assignment.name} ({assignment.family}, {assignment.actor}): Bool64bitKey {pair.source} and its companion "
        f"{companion(pair.source)} (Hash xor 2)"
    )
    if state == UNKNOWN:
        return Check(check_id, scope, UNKNOWN, want, state, f"{records}: {_why(snap)}")
    if state == PARTIAL:
        records += f": only the {'Hash' if pair.primary else 'companion'} record is set"
    return Check(check_id, scope, PASS if state == want else FAIL, want, state, records)


def _field_check(scope: str, field: Field, snap: Snapshot) -> Check:
    check_id = f"field.{field.kind}.{field.name}"
    actual = snap.value(field)
    if actual is None:
        return Check(check_id, scope, UNKNOWN, field.value, None, f"{field.record}: {_why(snap)}")
    return Check(check_id, scope, PASS if actual == field.value else FAIL, field.value, actual, field.record)


def baseline_checks(manifest: Manifest, baseline: Snapshot) -> list[Check]:
    """The packet's starting state in the baseline: its token stock recorded (every phase compares with it), every
    assigned source unset and every ``baseline`` field as the manifest says."""
    recorded = baseline.tokens is not None
    tokens = Check(
        "tokens",
        "baseline",
        PASS if recorded else UNKNOWN,
        "recorded",
        baseline.tokens,
        f"{TOKEN_STOCK}: {'the stock every phase compares with' if recorded else _why(baseline)}",
    )
    start = manifest.phases[BASELINE]
    return [
        tokens,
        *(_source("baseline", a, baseline.pairs[a.source], False, baseline) for a in manifest.assignments),
        *(_field_check("baseline", field, baseline) for field in start.fields),
    ]


def _tokens(baseline: Snapshot, current: Snapshot, added: int) -> Check:
    """The stock is the baseline's plus ``added``, the phase's completed native-token assignments; no other reward
    adds a token."""
    detail = f"{TOKEN_STOCK}: the baseline's plus {added} native token(s) the phase has collected"
    expected = None if baseline.tokens is None else baseline.tokens + added
    if current.tokens is None or expected is None:
        return Check("tokens", "save", UNKNOWN, expected, current.tokens, f"{detail}; {_why(current)}")
    return Check("tokens", "save", PASS if current.tokens == expected else FAIL, expected, current.tokens, detail)


def _other_sources(manifest: Manifest, baseline: Snapshot, current: Snapshot) -> Check:
    assigned = manifest.assigned()
    others = [source for source in manifest.source_hashes if source not in assigned]
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


def phase_checks(manifest: Manifest, phase: str, baseline: Snapshot, current: Snapshot) -> list[Check]:
    """The phase ``phase`` of the manifest in ``current``, against ``baseline``."""
    want = manifest.phases[phase]
    return [
        _tokens(baseline, current, manifest.tokens_added(phase)),
        *(
            _source("save", a, current.pairs[a.source], a.source in want.completed, current)
            for a in manifest.assignments
        ),
        *(_field_check("save", field, current) for field in want.fields),
        _other_sources(manifest, baseline, current),
    ]


def contract_issues(manifest: Manifest, baseline: Snapshot, current: Snapshot) -> list[str]:
    issues = []
    if baseline.sha256 != manifest.baseline_sha256:
        issues.append(f"baseline SHA256 {baseline.sha256}, manifest {manifest.baseline_sha256}")
    issues += [f"baseline: {issue}" for issue in baseline.identity]
    issues += [f"save: {issue}" for issue in current.identity]
    return issues


def check_packet(manifest: Manifest, baseline_data: bytes, save_data: bytes, phase: str) -> dict[str, Any]:
    """The JSON-able report of one packet phase: verdict, exit code, contract issues, every check and both
    snapshots."""
    if phase not in manifest.phases:
        raise ValueError(f"phase {phase!r} is not one of the manifest's: {', '.join(manifest.phases)}")
    baseline, current = snapshot(baseline_data, manifest), snapshot(save_data, manifest)
    contract = contract_issues(manifest, baseline, current)
    checks = [*baseline_checks(manifest, baseline), *phase_checks(manifest, phase, baseline, current)]
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
        "assignments": [a.to_json() for a in manifest.assignments],
        "completed": sorted(str(s) for s in manifest.phases[phase].completed),
        "native_tokens_completed": manifest.tokens_added(phase),
        "baseline": baseline.to_json(manifest, manifest.phases[BASELINE]),
        "save": current.to_json(manifest, manifest.phases[phase]),
        "same_bytes_as_baseline": baseline.sha256 == current.sha256,
        "scope": SCOPE,
    }


def _read_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _contract_error(phase: str, issue: str) -> dict[str, Any]:
    return {
        "tool": TOOL,
        "phase": phase,
        "verdict": CONTRACT_ERROR,
        "exit_code": EXIT_CODES[CONTRACT_ERROR],
        "contract": [issue],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=f"python -m {TOOL}",
        description="Check a Gold Skulltula reward-family packet save (read-only; JSON report).",
    )
    parser.add_argument("--manifest", required=True, type=Path, help="family packet manifest (JSON)")
    parser.add_argument("--baseline", required=True, type=Path, help="the accepted checkpoint's progress.sav")
    parser.add_argument("--save", required=True, type=Path, help="the packet phase's progress.sav")
    parser.add_argument("--phase", required=True, help="the manifest phase the save was taken at")
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
        baseline_data = _read_bytes(args.baseline)
        save_data = _read_bytes(args.save)
    except (OSError, ManifestError) as error:
        result = _contract_error(args.phase, str(error))
    else:
        if args.phase in manifest.phases:
            result = check_packet(manifest, baseline_data, save_data, args.phase)
        else:
            result = _contract_error(
                args.phase, f"phase {args.phase!r} is not one of the manifest's: {', '.join(manifest.phases)}"
            )
    result["paths"] = {"manifest": str(args.manifest), "baseline": str(args.baseline), "save": str(args.save)}
    print(json.dumps(result, indent=2))
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
