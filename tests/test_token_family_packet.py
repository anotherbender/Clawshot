"""The Gold Skulltula packet checker (``clawshot.token_family_packet``) on synthetic saves built here and read by the
real parser: a four-family packet and a native-token route packet played phase by phase, then one departure at a time
from them."""

import copy
import hashlib
import json
import os
import struct
from dataclasses import dataclass, field

import pytest

from clawshot import save
from clawshot import token_family_packet as fp
from clawshot.save import BOOL, BOOL64, ENUM, INT, murmur3_32
from clawshot.tracker.state import BOTTLE_SLOTS

VERSION = 0x2D80EB
SAVE_TYPE = 0xA3DB7114
TREE, TOWER, WINDOW, LONE = 341792603838029977, 2730878115209290675, 15889002414176907668, 2177746409373494991
WETLAND = 9047381233010434881  # spec section 4: HF GS Wetland Grotto Crate
OTHERS = tuple(10**18 + 4 * i for i in range(95))  # bit 1 clear: no companion is another source
SOURCES = (TREE, TOWER, WINDOW, LONE, WETLAND, *OTHERS)
DONE = OTHERS[5]  # collected before the checkpoint
UNRELATED = 4242  # a Bool64bitKey flag of no Skulltula
BOOM, HEART_PIECE, TOKEN = "Item_Boomerang", "Obj_Heart_Piece", "Item_Token_Gold"
RUPEES, MAX_LIFE = "PlayerStatus.CurrentRupee", "PlayerStatus.MaxLife"
_, BOTTLE_B_VALID, BOTTLE_B_ITEM = BOTTLE_SLOTS[1]  # BottleB's owned Bool and content Enum, by raw key
EMPTY, MILK, HALF_MILK = (murmur3_32(name.encode()) for name in ("Empty", "MaxMilk", "HalfMilk"))
ROUTE = ("baseline", "tree-collected", "tower-collected", "window-collected", "lone-collected")
ORDER = (TREE, TOWER, WINDOW, LONE)
SHIELD = "Weapon_Shield_Hylian"  # the saved item of the Obj_Shield_Hylian pickup
NOTE12, CHILDHOOD = "HaveReadHrlField_Note12_Enemy", "Sequence_IsChildhood"
# Route phases: (name, completed sources, the child's wall kill recorded, child).
TRIP = (
    ("baseline", (), False, True),
    ("lone-collected", (LONE,), False, True),
    ("wall-killed", (LONE,), True, True),
    ("tower-collected", (LONE, TOWER), True, False),
    ("wetland-collected", (LONE, TOWER, WETLAND), True, False),
)
ROUTE_TOKENS = 30  # the route checkpoint's token stock
MISSING = object()


def stock(actor: str) -> str:
    return f"PouchData.{actor}.StockNum"


@dataclass
class State:
    bools: dict = field(default_factory=dict)
    ints: dict = field(default_factory=dict)
    enums: dict = field(default_factory=dict)
    keys: set = field(default_factory=set)

    def encode(self, *, version=VERSION, save_type=SAVE_TYPE, bool64=True, terminate=True) -> bytes:
        """tests/test_save.py's layout: header, Bool, Int and Enum sections, then the Bool64bitKey section and its
        sparse list of set keys. Names are hashed; an int name is a raw key."""

        def entry(name, value):
            key = name if isinstance(name, int) else murmur3_32(name.encode())
            return struct.pack("<II", key, int(value) & 0xFFFFFFFF)

        table = b""
        for section, values in ((BOOL, self.bools), (INT, self.ints), (ENUM, self.enums)):
            table += struct.pack("<II", 0, section) + b"".join(entry(n, v) for n, v in values.items())
        end = save.HEADER_SIZE + len(table) + (16 if bool64 else 0)
        data = b""
        if bool64:
            table += struct.pack("<II", 0, BOOL64) + struct.pack("<II", save_type, end)
            data = b"".join(struct.pack("<Q", k) for k in sorted(self.keys))
            data += struct.pack("<Q", 0) if terminate else b""
        return struct.pack("<III", save.MAGIC, version, end).ljust(save.HEADER_SIZE, b"\0") + table + data

    def collect(self, source: int) -> None:
        self.keys |= {source, source ^ 2}


def checkpoint() -> State:
    """A fresh ranch checkpoint: 9 tokens, no Boomerang, one heart piece, BottleB not owned, the four assigned
    sources unset, one other source already collected."""
    return State(
        bools={
            f"IsGet.{BOOM}": False,
            f"IsGet.{TOKEN}": True,
            BOTTLE_B_VALID: False,
            "IsVisitLocation.LonLonRanch": False,
        },
        ints={stock(BOOM): 0, stock(HEART_PIECE): 1, MAX_LIFE: 12, stock(TOKEN): 9, RUPEES: 37},
        enums={BOTTLE_B_ITEM: EMPTY},
        keys={DONE, DONE ^ 2, UNRELATED},
    )


def played(phase: str) -> State:
    """The packet played up to ``phase``, with unrelated play (a visit, another Bool64bitKey flag) on top."""
    state, step = checkpoint(), ROUTE.index(phase)
    if step >= 1:
        state.bools["IsVisitLocation.LonLonRanch"] = True
        state.keys.add(UNRELATED + 8)
        state.collect(TREE)
        state.ints[stock(BOOM)] += 1
        state.bools[f"IsGet.{BOOM}"] = True
    if step >= 2:
        state.collect(TOWER)
        state.ints[stock(HEART_PIECE)] += 1
    if step >= 3:
        state.collect(WINDOW)
        state.bools[BOTTLE_B_VALID] = True
        state.enums[BOTTLE_B_ITEM] = MILK
    if step >= 4:
        state.collect(LONE)
        state.ints[RUPEES] += 20
    return state


BASELINE = checkpoint().encode()


def entry(name, kind, value) -> dict:
    return {"name": name, "kind": kind, "value": value}


def phase_fields(step: int) -> list[dict]:
    milk = step >= 3
    return [
        entry(stock(BOOM), "int", int(step >= 1)),
        entry(f"IsGet.{BOOM}", "bool", step >= 1),
        entry(stock(HEART_PIECE), "int", 1 + (step >= 2)),
        entry(MAX_LIFE, "int", 12),
        entry(BOTTLE_B_VALID, "bool", milk),
        entry(BOTTLE_B_ITEM, "enum", MILK if milk else EMPTY),
        entry(RUPEES, "int", 37 + 20 * (step >= 4)),
    ]


def manifest_dict(baseline: bytes = BASELINE, **changes) -> dict:
    raw = {
        "build": "e0f3ccfa",
        "save_version": VERSION,
        "save_type": SAVE_TYPE,
        "baseline_sha256": hashlib.sha256(baseline).hexdigest(),
        "source_hashes": list(SOURCES),
        "assignments": [
            {"id": str(TREE), "name": "LLR GS Tree", "family": "fixed_major", "actor": BOOM},
            {"id": str(TOWER), "name": "LLR GS Tower", "family": "heart_piece", "actor": HEART_PIECE},
            {"id": str(WINDOW), "name": "LLR GS House Window", "family": "bottle", "actor": "Item_Bottle_Milk"},
            {"id": str(LONE), "name": "HF GS Lone Tree", "family": "rupee", "actor": "Item_Rupee_Red"},
        ],
        "phases": {
            phase: {"completed": [str(s) for s in ORDER[:step]], "fields": phase_fields(step)}
            for step, phase in enumerate(ROUTE)
        },
    }
    raw.update(changes)
    return {k: v for k, v in raw.items() if v is not MISSING}


MANIFEST = fp.parse_manifest(manifest_dict())


def run(state: State | bytes, phase: str, manifest=MANIFEST, baseline=BASELINE, **options) -> dict:
    data = state if isinstance(state, bytes) else state.encode(**options)
    return fp.check_packet(manifest, baseline, data, phase)


def by_id(report: dict, scope: str = "save") -> dict:
    return {c["id"]: c for c in report["checks"] if c["scope"] == scope}


@pytest.mark.parametrize("phase", ROUTE)
def test_played_packet_passes_every_phase(phase):
    report = run(played(phase), phase)
    assert (report["verdict"], report["exit_code"], report["contract"]) == ("pass", 0, [])
    assert report["counts"]["fail"] == report["counts"]["unknown"] == 0
    checks = by_id(report)
    step = ROUTE.index(phase)
    for n, source in enumerate(ORDER):
        assert checks[f"source.{source}"]["actual"] == ("set" if n < step else "unset")
    assert checks["tokens"]["actual"] == checks["tokens"]["expected"] == 9
    assert checks["sources.others"]["status"] == "pass"
    assert len([c for c in checks if c.startswith("field.")]) == len(phase_fields(step))
    assert report["save"]["other_sources"] == {"count": 96, "set": 1, "unset": 95, "partial": 0, "unknown": 0}
    assert report["same_bytes_as_baseline"] is (phase == "baseline")
    assert [a["family"] for a in report["assignments"]] == ["fixed_major", "heart_piece", "bottle", "rupee"]
    assert "not a played proof" in report["scope"] and report["native_tokens_completed"] == 0
    json.dumps(report)


def test_each_reward_family_is_read_from_its_own_typed_records():
    checks = by_id(run(played("lone-collected"), "lone-collected"))
    assert checks[f"field.int.{stock(BOOM)}"]["actual"] == 1
    assert checks[f"field.int.{stock(HEART_PIECE)}"]["actual"] == 2
    assert checks[f"field.bool.{BOTTLE_B_VALID}"]["actual"] is True
    assert checks[f"field.enum.{BOTTLE_B_ITEM}"]["actual"] == MILK
    assert checks[f"field.int.{RUPEES}"]["actual"] == 57
    assert checks[f"field.enum.{BOTTLE_B_ITEM}"]["detail"] == f"Enum key 0x{BOTTLE_B_ITEM:08x}"


def test_grant_without_completion_and_completion_without_grant_fail():
    granted = played("tree-collected")
    granted.keys -= {TREE, TREE ^ 2}
    report = run(granted, "tree-collected")
    assert (report["verdict"], report["exit_code"]) == ("fail", 1)
    assert by_id(report)[f"source.{TREE}"] | {"detail": ""} == {
        "id": f"source.{TREE}",
        "scope": "save",
        "status": "fail",
        "expected": "set",
        "actual": "unset",
        "detail": "",
    }
    completed = played("tree-collected")
    completed.ints[stock(BOOM)] = 0
    completed.bools[f"IsGet.{BOOM}"] = False
    checks = by_id(run(completed, "tree-collected"))
    assert checks[f"source.{TREE}"]["status"] == "pass"
    assert [checks[f"field.{k}"]["status"] for k in (f"int.{stock(BOOM)}", f"bool.IsGet.{BOOM}")] == ["fail", "fail"]


def test_partial_pairs_fail_and_name_the_set_record():
    partial = played("tree-collected")
    partial.keys.discard(TREE)
    check = by_id(run(partial, "tree-collected"))[f"source.{TREE}"]
    assert (check["status"], check["actual"]) == ("fail", "partial")
    assert check["detail"].endswith("only the companion record is set")
    early = played("tree-collected")
    early.keys.add(TOWER)  # an uncompleted source with one record
    check = by_id(run(early, "tree-collected"))[f"source.{TOWER}"]
    assert (check["status"], check["expected"], check["actual"]) == ("fail", "unset", "partial")
    assert check["detail"].endswith("only the Hash record is set")


def test_other_sources_must_keep_both_records_and_unrelated_flags_do_not_matter():
    for extra in ({OTHERS[0], OTHERS[0] ^ 2}, {OTHERS[1] ^ 2}):
        state = played("tower-collected")
        state.keys |= extra
        check = by_id(run(state, "tower-collected"))["sources.others"]
        assert check["status"] == "fail" and [row["hash"] for row in check["actual"]] == [min(extra) & ~2]
    undone = played("tower-collected")
    undone.keys -= {DONE}  # a source collected before the checkpoint loses a record
    assert by_id(run(undone, "tower-collected"))["sources.others"]["actual"][0]["hash"] == DONE
    unrelated = played("tower-collected")
    unrelated.keys.add(UNRELATED + 12)
    unrelated.bools["IsVisitLocation.KokiriForest"] = True
    assert run(unrelated, "tower-collected")["verdict"] == "pass"


def test_token_stock_must_stay_the_baselines_and_absent_is_unknown():
    bonus = played("tree-collected")
    bonus.ints[stock(TOKEN)] = 10
    check = by_id(run(bonus, "tree-collected"))["tokens"]
    assert (check["status"], check["expected"], check["actual"]) == ("fail", 9, 10)
    absent = played("tree-collected")
    del absent.ints[stock(TOKEN)]
    report = run(absent, "tree-collected")
    assert (report["verdict"], report["exit_code"]) == ("unknown", 2)
    assert (by_id(report)["tokens"]["status"], by_id(report)["tokens"]["actual"]) == ("unknown", None)


def test_absent_or_mistyped_fields_are_unknown_never_zero_or_false():
    no_content = played("window-collected")
    del no_content.enums[BOTTLE_B_ITEM]
    report = run(no_content, "window-collected")
    check = by_id(report)[f"field.enum.{BOTTLE_B_ITEM}"]
    assert (report["verdict"], check["status"], check["actual"]) == ("unknown", "unknown", None)
    assert "no such record" in check["detail"]
    moved = played("window-collected")
    del moved.ints[stock(HEART_PIECE)]
    moved.bools[stock(HEART_PIECE)] = True  # the name in the Bool section is not the Int record
    check = by_id(run(moved, "window-collected"))[f"field.int.{stock(HEART_PIECE)}"]
    assert (check["status"], check["actual"]) == ("unknown", None)
    unset = played("window-collected")
    del unset.bools[BOTTLE_B_VALID]
    assert by_id(run(unset, "window-collected"))[f"field.bool.{BOTTLE_B_VALID}"]["actual"] is None


def test_bottle_owned_flag_and_content_are_checked_separately():
    half = played("window-collected")
    half.enums[BOTTLE_B_ITEM] = HALF_MILK
    check = by_id(run(half, "window-collected"))[f"field.enum.{BOTTLE_B_ITEM}"]
    assert (check["status"], check["expected"], check["actual"]) == ("fail", MILK, HALF_MILK)
    not_owned = played("window-collected")
    not_owned.bools[BOTTLE_B_VALID] = False
    checks = by_id(run(not_owned, "window-collected"))
    assert checks[f"field.bool.{BOTTLE_B_VALID}"]["status"] == "fail"
    assert checks[f"field.enum.{BOTTLE_B_ITEM}"]["status"] == "pass"


@pytest.mark.parametrize(
    ("options", "issue"),
    [
        ({"version": VERSION + 1}, "save version"),
        ({"save_type": SAVE_TYPE ^ 1}, "save type"),
        ({"bool64": False}, "no Bool64bitKey section"),
        ({"terminate": False}, "unreadable save"),
    ],
)
def test_a_save_of_another_layout_is_a_contract_error_with_every_value_unknown(options, issue):
    report = run(played("lone-collected"), "lone-collected", **options)
    assert (report["verdict"], report["exit_code"]) == ("contract_error", 3)
    assert any(c.startswith("save: ") and issue in c for c in report["contract"])
    assert {c["status"] for c in by_id(report).values()} == {"unknown"}
    assert report["save"]["trusted"] is False and report["save"]["tokens"]["stock"] is None
    assert all(f["value"] is None for f in report["save"]["fields"])
    assert {c["status"] for c in by_id(report, "baseline").values()} == {"pass"}


def test_baseline_must_be_the_accepted_unmodified_checkpoint_in_its_manifest_state():
    edited = checkpoint()
    edited.bools["IsVisitLocation.LonLonRanch"] = True
    report = run(played("baseline"), "baseline", baseline=edited.encode())
    assert report["verdict"] == "contract_error" and "baseline SHA256" in report["contract"][0]

    wrong = manifest_dict()
    wrong["phases"]["baseline"]["fields"][0]["value"] = 1  # the manifest says a Boomerang is already owned
    report = run(played("tree-collected"), "tree-collected", manifest=fp.parse_manifest(wrong))
    assert (report["verdict"], report["contract"]) == ("contract_error", [])
    assert by_id(report, "baseline")[f"field.int.{stock(BOOM)}"]["status"] == "fail"

    for change in ("collected", "no stock", "no field"):
        start = checkpoint()
        if change == "collected":
            start.collect(TOWER)
        elif change == "no stock":
            del start.ints[stock(TOKEN)]
        else:
            del start.ints[MAX_LIFE]
        data = start.encode()
        report = run(played("tree-collected"), "tree-collected", fp.parse_manifest(manifest_dict(data)), data)
        bad = [c for c in by_id(report, "baseline").values() if c["status"] != "pass"]
        assert report["verdict"] == "contract_error" and len(bad) == 1, change

    other = fp.parse_manifest(manifest_dict(save_version=VERSION + 1))
    report = run(played("baseline"), "baseline", manifest=other)
    assert {c.split(":")[0] for c in report["contract"]} == {"baseline", "save"}


def edit(path, value):
    def apply(raw):
        target = raw
        for key in path[:-1]:
            target = target[key]
        if value is MISSING:
            del target[path[-1]]
        else:
            target[path[-1]] = value

    return apply


TREE_FIELDS = ("phases", "tree-collected", "fields")
WORLD_ROW = {"id": str(TREE), "name": "LLR GS Tree"}  # an assignment's identity, family and actor added per case


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (edit(("phases",), MISSING), r"missing \['phases'\]"),
        (edit(("build",), "0000"), "only build"),
        (edit(("save_version",), True), "unsigned 32-bit"),
        (edit(("save_type",), 1 << 32), "unsigned 32-bit"),
        (edit(("baseline_sha256",), "abc"), "64 hex"),
        (edit(("source_hashes",), list(SOURCES[:-1])), "expected 100 distinct"),
        (edit(("source_hashes",), [*SOURCES[:-1], TREE]), "expected 100 distinct"),
        (edit(("source_hashes",), [*SOURCES[:-1], TREE ^ 2]), "companion"),
        (edit(("source_hashes",), [*SOURCES[:-1], 2]), "key 0"),
        (edit(("source_hashes", 4), "01000"), "decimal string"),
        (edit(("source_hashes", 4), -1), "unsigned 64-bit"),
        (edit(("source_hashes", 4), 1.5), "unsigned 64-bit"),
        (edit(("assignments",), []), "non-empty list"),
        (edit(("assignments", 0), "LLR GS Tree"), "must be an object"),
        (edit(("assignments", 0, "id"), TREE), "decimal string"),
        (edit(("assignments", 0, "id"), "123"), "not one of source_hashes"),
        (edit(("assignments", 1, "id"), str(TREE)), "assigned twice"),
        (edit(("assignments", 0, "actor"), TOKEN), "a native token is family 'token'"),  # misdeclared family
        (edit(("assignments", 0, "family"), "token"), "a native token is family 'token'"),  # misdeclared actor
        (edit(("assignments", 0), {**WORLD_ROW, "family": "Token", "actor": TOKEN}), "a native token is family"),
        (edit(("assignments", 0, "actor"), "Obj_Token_Gold"), "not Obj_Token_Gold"),
        (edit(("assignments", 0), {**WORLD_ROW, "family": "token", "actor": "Obj_Token_Gold"}), "not Obj_Token_Gold"),
        (edit(("assignments", 0, "actor"), "Item Boomerang"), "pouch or pickup actor name"),
        (edit(("assignments", 0, "family"), " "), "non-empty string"),
        (edit(("assignments", 0, "name"), MISSING), r"missing \['name'\]"),
        (edit(("phases",), []), "includes 'baseline'"),
        (edit(("phases", "baseline"), MISSING), "includes 'baseline'"),
        (edit(("phases", "baseline", "completed"), [str(TREE)]), "must be empty"),
        (edit(("phases", "tree-collected"), {"completed": []}), "with completed and fields"),
        (edit(("phases", "tree-collected", "completed"), str(TREE)), "completed must be a list"),
        (edit(("phases", "tree-collected", "completed"), [str(OTHERS[0])]), "unassigned"),
        (edit(("phases", "tree-collected", "completed"), [str(TREE), str(TREE)]), "twice"),
        (edit(TREE_FIELDS, []), "non-empty list"),
        (edit((*TREE_FIELDS, 0), [stock(BOOM), "int", 1]), "must be an object"),
        (edit((*TREE_FIELDS, 0, "value"), MISSING), r"missing \['value'\]"),
        (edit((*TREE_FIELDS, 0, "kind"), "float"), "kind must be one of"),
        (edit((*TREE_FIELDS, 1, "value"), 1), "true or false"),
        (edit((*TREE_FIELDS, 0, "value"), True), "signed 32-bit"),
        (edit((*TREE_FIELDS, 0, "value"), 1 << 31), "signed 32-bit"),
        (edit((*TREE_FIELDS, 5, "value"), -1), "unsigned 32-bit"),
        (edit((*TREE_FIELDS, 0, "name"), 0), "nonzero unsigned 32-bit"),
        (edit((*TREE_FIELDS, 0, "name"), ""), "non-empty string"),
        (edit((*TREE_FIELDS, 2, "name"), murmur3_32(stock(BOOM).encode())), "one saved record twice"),
    ],
)
def test_manifest_schema_errors_name_the_first_problem(change, message):
    raw = manifest_dict()
    change(raw)
    with pytest.raises(fp.ManifestError, match=message):
        fp.parse_manifest(raw)


def test_manifest_accepts_decimal_sources_ignores_metadata_and_is_order_independent():
    with pytest.raises(fp.ManifestError, match="JSON object"):
        fp.parse_manifest([])
    decimal = manifest_dict(source_hashes=[str(h) for h in reversed(SOURCES)], notes="packet 1", rep="Tree bootstrap")
    decimal["assignments"][0]["proof"] = "core packet"
    parsed = fp.parse_manifest(decimal)
    assert parsed == MANIFEST
    assert parsed.source_hashes == tuple(sorted(SOURCES))
    raw_key = manifest_dict()
    raw_key["phases"]["tree-collected"]["fields"][0]["name"] = murmur3_32(stock(BOOM).encode())
    state = played("tree-collected")
    assert run(state, "tree-collected", fp.parse_manifest(raw_key))["checks"] != run(state, "tree-collected")["checks"]
    assert run(state, "tree-collected", fp.parse_manifest(raw_key))["verdict"] == "pass"
    assert json.dumps(run(state, "tree-collected", parsed)) == json.dumps(run(state, "tree-collected"))
    with pytest.raises(ValueError, match="not one of the manifest's"):
        run(state, "reload")


def route_checkpoint() -> State:
    """A child route checkpoint: 30 tokens, no Hylian Shield, the wall Skullwalltula alive, the three route sources
    unset, one other source already collected."""
    return State(
        bools={NOTE12: False, CHILDHOOD: True, f"IsGet.{SHIELD}": False, f"IsGet.{TOKEN}": True},
        ints={stock(TOKEN): ROUTE_TOKENS, stock(SHIELD): 0},
        keys={DONE, DONE ^ 2, UNRELATED},
    )


def route_played(phase: str) -> State:
    """The route played up to ``phase``: each native token collected adds one to the stock, the shield none."""
    _, completed, killed, child = next(stage for stage in TRIP if stage[0] == phase)
    state = route_checkpoint()
    state.bools[NOTE12], state.bools[CHILDHOOD] = killed, child
    for source in completed:
        state.collect(source)
        if source == TOWER:
            state.ints[stock(SHIELD)] += 1
            state.bools[f"IsGet.{SHIELD}"] = True
        else:
            state.ints[stock(TOKEN)] += 1
    return state


ROUTE_BASELINE = route_checkpoint().encode()


def route_manifest() -> dict:
    def fields(completed, killed, child):
        shield = TOWER in completed
        return [
            entry(NOTE12, "bool", killed),
            entry(CHILDHOOD, "bool", child),
            entry(stock(SHIELD), "int", int(shield)),
            entry(f"IsGet.{SHIELD}", "bool", shield),
        ]

    return manifest_dict(
        ROUTE_BASELINE,
        assignments=[
            {"id": str(LONE), "name": "HF GS Lone Tree", "family": "token", "actor": TOKEN},
            {"id": str(TOWER), "name": "LLR GS Tower", "family": "equipment", "actor": "Obj_Shield_Hylian"},
            {"id": str(WETLAND), "name": "HF GS Wetland Grotto Crate", "family": "token", "actor": TOKEN},
        ],
        phases={
            name: {"completed": [str(s) for s in completed], "fields": fields(completed, killed, child)}
            for name, completed, killed, child in TRIP
        },
    )


ROUTE_MANIFEST = fp.parse_manifest(route_manifest())


def route(state: State, phase: str) -> dict:
    return run(state, phase, ROUTE_MANIFEST, ROUTE_BASELINE)


@pytest.mark.parametrize(
    ("phase", "added"), [(name, sum(source != TOWER for source in completed)) for name, completed, *_ in TRIP]
)
def test_route_expects_one_token_per_collected_native_token_source(phase, added):
    report = route(route_played(phase), phase)
    assert (report["verdict"], report["exit_code"], report["native_tokens_completed"]) == ("pass", 0, added)
    check = by_id(report)["tokens"]
    assert (check["expected"], check["actual"]) == (ROUTE_TOKENS + added, ROUTE_TOKENS + added)
    assert ROUTE_MANIFEST.tokens_added(phase) == added and MANIFEST.tokens_added("lone-collected") == 0


def test_route_token_stock_departures_fail():
    source_only = route_played("lone-collected")
    source_only.ints[stock(TOKEN)] = ROUTE_TOKENS  # the source committed, no token added
    check = by_id(route(source_only, "lone-collected"))["tokens"]
    assert (check["status"], check["expected"], check["actual"]) == ("fail", ROUTE_TOKENS + 1, ROUTE_TOKENS)

    double = route_played("lone-collected")
    double.ints[stock(TOKEN)] += 1  # two tokens from one source
    assert by_id(route(double, "lone-collected"))["tokens"]["status"] == "fail"

    bonus = route_played("tower-collected")
    bonus.ints[stock(TOKEN)] += 1  # the shield's source pays a token as well
    check = by_id(route(bonus, "tower-collected"))["tokens"]
    assert (check["status"], check["expected"], check["actual"]) == ("fail", ROUTE_TOKENS + 1, ROUTE_TOKENS + 2)

    stock_only = route_checkpoint()
    stock_only.ints[stock(TOKEN)] += 1  # a token without its source committing
    checks = by_id(route(stock_only, "lone-collected"))
    assert (checks["tokens"]["status"], checks[f"source.{LONE}"]["status"]) == ("pass", "fail")

    for added, status in ((2, "pass"), (1, "fail"), (3, "fail")):
        both = route_played("wetland-collected")
        both.ints[stock(TOKEN)] = ROUTE_TOKENS + added
        assert by_id(route(both, "wetland-collected"))["tokens"]["status"] == status, added


def test_route_fields_record_the_childs_wall_kill_and_the_age():
    alive = route_played("wall-killed")
    alive.bools[NOTE12] = False
    assert by_id(route(alive, "wall-killed"))[f"field.bool.{NOTE12}"]["status"] == "fail"
    child = route_played("tower-collected")
    child.bools[CHILDHOOD] = True
    assert by_id(route(child, "tower-collected"))[f"field.bool.{CHILDHOOD}"]["status"] == "fail"
    unrecorded = route_played("wetland-collected")
    del unrecorded.bools[NOTE12]
    report = route(unrecorded, "wetland-collected")
    assert (report["verdict"], by_id(report)[f"field.bool.{NOTE12}"]["actual"]) == ("unknown", None)


def test_cli_reports_json_and_exit_codes_without_touching_its_inputs(tmp_path, capsys):
    manifest = tmp_path / "family-packet.json"
    manifest.write_text(json.dumps(manifest_dict()), encoding="utf-8")
    baseline = tmp_path / "baseline.sav"
    baseline.write_bytes(BASELINE)
    good, bad, unknown = (tmp_path / f"{name}.sav" for name in ("good", "bad", "unknown"))
    good.write_bytes(played("tower-collected").encode())
    bonus = played("tower-collected")
    bonus.ints[stock(TOKEN)] = 10
    bad.write_bytes(bonus.encode())
    no_stock = played("tower-collected")
    del no_stock.ints[stock(HEART_PIECE)]
    unknown.write_bytes(no_stock.encode())
    inputs = (manifest, baseline, good, bad, unknown)
    before = {path: (path.read_bytes(), os.stat(path).st_mtime_ns) for path in inputs}

    def cli(*args, phase="tower-collected", manifest_path=manifest, save_path=good):
        argv = ["--manifest", str(manifest_path), "--baseline", str(baseline), "--save", str(save_path)]
        code = fp.main([*argv, "--phase", phase, *args])
        report = json.loads(capsys.readouterr().out)
        assert report["exit_code"] == code and report["paths"]["save"] == str(save_path)
        return code, report

    assert cli()[0] == 0
    assert cli(save_path=bad)[0] == 1
    assert cli(save_path=unknown)[0] == 2
    code, report = cli(phase="reload")
    assert (code, report["verdict"]) == (3, "contract_error") and "baseline, tree-collected" in report["contract"][0]
    assert cli(save_path=tmp_path / "missing.sav")[0] == 3
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert cli(manifest_path=broken)[0] == 3
    schema = tmp_path / "schema.json"
    schema.write_text(json.dumps(manifest_dict(build="0000")), encoding="utf-8")
    code, report = cli(manifest_path=schema)
    assert code == 3 and "only build" in report["contract"][0]
    assert {path: (path.read_bytes(), os.stat(path).st_mtime_ns) for path in inputs} == before


def test_reports_are_deterministic():
    state = played("window-collected")
    first = json.dumps(run(state, "window-collected"))
    shuffled = manifest_dict(source_hashes=list(reversed(SOURCES)))
    assert json.dumps(run(state, "window-collected", fp.parse_manifest(shuffled))) == first
    assert json.dumps(run(copy.deepcopy(state), "window-collected")) == first
