"""The core packet checker (``tools.token_packets.token_packet``) on synthetic saves built here and read by the real
parser: the packet played step by step, then one departure at a time from it."""

import hashlib
import json
import struct
from dataclasses import dataclass, field

import pytest

from clawshot import save
from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import zsdic
from clawshot.save import BOOL, BOOL64, INT, murmur3_32
from tools.token_packets import token_packet as tp

VERSION = 0x2D80EB
SAVE_TYPE = 0xA1B2C3D4
TREE, TOWER, CONTROL = 341792603838029977, 2730878115209290675, 2177746409373494991
CONTROL_COMPANION = 2177746409373494989  # spec section 2.1: Lone Tree's companion record
CHEST = "IsTreasureBoxOpen.14818888396401495482"
HOUSE = "KakarikoVillage_GatheringTokenGold_GetReward10"
OTHERS = tuple(10**18 + 4 * i for i in range(97))  # bit 1 clear: no companion is another source
DONE = OTHERS[5]  # collected before the checkpoint (like the Market guard-house source)
UNRELATED = 4242  # a Bool64bitKey flag of no Skulltula
ROUTE = (
    "baseline",
    "tree-abandoned",
    "tree-reloaded-uncollected",
    "tree-collected",
    "tower-collected",
    "control-collected",
    "chest-opened",
    "house-claimed",
    "reload",
)
MISSING = object()


def stock(actor: str) -> str:
    return f"PouchData.{actor}.StockNum"


def encode(
    bools: dict,
    ints: dict,
    keys: set[int],
    *,
    version: int = VERSION,
    save_type: int = SAVE_TYPE,
    bool64: bool = True,
    terminate: bool = True,
) -> bytes:
    """tests/test_save.py's layout: header, Bool and Int sections, then the Bool64bitKey section and its key list.
    Names are hashed; an int name is a raw key."""

    def entry(name, value):
        return struct.pack("<II", name if isinstance(name, int) else murmur3_32(name.encode()), value & 0xFFFFFFFF)

    table = struct.pack("<II", 0, BOOL) + b"".join(entry(n, int(v)) for n, v in bools.items())
    table += struct.pack("<II", 0, INT) + b"".join(entry(n, v) for n, v in ints.items())
    keys_data = b""
    table_end = save.HEADER_SIZE + len(table) + (16 if bool64 else 0)
    if bool64:
        table += struct.pack("<II", 0, BOOL64) + struct.pack("<II", save_type, table_end)
        keys_data = b"".join(struct.pack("<Q", k) for k in sorted(keys)) + (struct.pack("<Q", 0) if terminate else b"")
    header = struct.pack("<III", save.MAGIC, version, table_end).ljust(save.HEADER_SIZE, b"\0")
    return header + table + keys_data


@dataclass
class State:
    bools: dict = field(default_factory=dict)
    ints: dict = field(default_factory=dict)
    keys: set = field(default_factory=set)

    def encode(self, **options) -> bytes:
        return encode(self.bools, self.ints, self.keys, **options)

    def collect(self, source: int) -> None:
        self.keys |= {source, source ^ 2}

    def grant(self, actor: str) -> None:
        self.ints[stock(actor)] += 1
        self.bools[f"IsGet.{actor}"] = True


def checkpoint() -> State:
    """The packet's starting state: 9 tokens, no Boomerang, Hylian Shield or Hammer ever owned, chest closed, House 10
    unclaimed, the core sources unset, one other source already collected."""
    items = ("Item_Boomerang", "Weapon_Shield_Hylian", "Item_Hammer", "Item_Wallet_Medium", "Item_Wallet_Large")
    return State(
        bools={
            CHEST: False,
            HOUSE: False,
            "IsGet.Item_Token_Gold": True,
            "IsGet.Weapon_Shield_Deku": True,
            "IsVisitLocation.LonLonRanch": False,
            **{f"IsGet.{actor}": False for actor in items},
        },
        ints={stock("Item_Token_Gold"): 9, "PlayerStatus.CurrentRupee": 37, **{stock(actor): 0 for actor in items}},
        keys={DONE, DONE ^ 2, UNRELATED},
    )


def played(phase: str) -> State:
    """Section 6's core packet played up to ``phase``, with unrelated play (rupees, a visit, another flag) on top."""
    state, step = checkpoint(), ROUTE.index(phase)
    state.ints["PlayerStatus.CurrentRupee"] += 5 * step
    if step >= 1:
        state.bools["IsVisitLocation.LonLonRanch"] = True
        state.keys.add(UNRELATED + 8)
    if step >= 3:
        state.collect(TREE)
        state.grant("Item_Boomerang")
    if step >= 4:
        state.collect(TOWER)
        state.grant("Weapon_Shield_Hylian")
    if step >= 5:
        state.collect(CONTROL)
        state.ints[stock("Item_Token_Gold")] = 10
    if step >= 6:
        state.bools[CHEST] = True
        state.ints[stock("Item_Token_Gold")] = 11
    if step >= 7:
        state.bools[HOUSE] = True
        state.grant("Item_Hammer")
    return state


BASELINE = checkpoint().encode()


def manifest_dict(**changes) -> dict:
    raw = {
        "build": "e0f3ccfa",
        "save_version": VERSION,
        "save_type": SAVE_TYPE,
        "baseline_sha256": hashlib.sha256(BASELINE).hexdigest(),
        "source_hashes": [TREE, TOWER, CONTROL, *OTHERS],
        "house_actor": "Item_Hammer",
    }
    raw.update(changes)
    return {k: v for k, v in raw.items() if v is not MISSING}


MANIFEST = tp.parse_manifest(manifest_dict())


def run(state: State | bytes, phase: str, baseline: bytes = BASELINE, manifest: tp.Manifest = MANIFEST) -> dict:
    data = state.encode() if isinstance(state, State) else state
    report = tp.check_packet(manifest, baseline, data, phase)
    json.dumps(report)  # JSON-able as printed
    return report


def by_id(report: dict) -> dict:
    return {(c["scope"], c["id"]): c for c in report["checks"]}


def failing(report: dict, scope: str = "save") -> set[str]:
    return {c["id"] for c in report["checks"] if c["scope"] == scope and c["status"] != "pass"}


@pytest.mark.parametrize(
    "changes",
    [
        {"build": "1db6e63"},
        {"house_actor": MISSING},
        {"save_version": True},
        {"save_type": 1 << 32},
        {"baseline_sha256": "abc"},
        {"source_hashes": [TREE, TOWER, CONTROL, *OTHERS[:-1]]},
        {"source_hashes": [TREE, TOWER, CONTROL, *OTHERS[:-1], TREE]},
        {"source_hashes": [TREE, TOWER, *OTHERS, 10**18 + 4 * 97]},
        {"source_hashes": [TREE, TOWER, CONTROL, *OTHERS[:-1], OTHERS[0] ^ 2]},
        {"source_hashes": [TREE, TOWER, CONTROL, *OTHERS[:-1], 14818888396401495482]},
        {"source_hashes": [TREE, TOWER, CONTROL, *OTHERS[:-1], str(OTHERS[-1])]},
        {"house_actor": "Item_Wallet_Medium"},
        {"house_actor": "Item_Token_Gold"},
        {"house_actor": "Item_Boomerang"},
    ],
)
def test_manifest_contract_is_enforced(changes):
    with pytest.raises(tp.ManifestError):
        tp.parse_manifest(manifest_dict(**changes))


def test_the_token_stock_record_is_the_native_key():
    state = played("baseline")
    count = state.ints.pop(stock("Item_Token_Gold"))
    state.ints[74668408] = count  # spec section 2.3: the native key of the saved token stock
    assert tp.snapshot(state.encode(), MANIFEST).tokens == 9


@pytest.mark.parametrize(
    "phase", ["tree-abandoned", "tree-collected", "tower-collected", "control-collected", "chest-opened", "reload"]
)
def test_the_played_packet_passes_every_step(phase):
    report = run(played(phase), phase)
    assert report["contract"] == [] and failing(report, "baseline") == set()
    assert (report["verdict"], report["exit_code"], failing(report)) == ("pass", 0, set())
    assert report["counts"] == {"pass": len(report["checks"]), "fail": 0, "unknown": 0}


def test_snapshot_reports_every_packet_record():
    snap = run(played("house-claimed"), "house-claimed")["save"]
    assert snap["trusted"] is True and snap["identity"] == []
    assert (snap["tokens"]["stock"], snap["tokens"]["isget"]) == (11, True)
    assert snap["core_sources"]["control"] == {
        "hash": CONTROL,
        "companion_hash": CONTROL_COMPANION,
        "primary_set": True,
        "companion_set": True,
        "state": "set",
    }
    assert {name: pair["state"] for name, pair in snap["core_sources"].items()} == dict.fromkeys(tp.CORE_SOURCES, "set")
    assert (snap["chest"]["open"], snap["house10"]["claimed"]) == (True, True)
    assert snap["items"] == {
        "boomerang": {"actor": "Item_Boomerang", "stock": 1, "isget": True},
        "hylian_shield": {"actor": "Weapon_Shield_Hylian", "stock": 1, "isget": True},
        "house": {"actor": "Item_Hammer", "stock": 1, "isget": True},
    }
    assert snap["wallets"] == {
        "Item_Wallet_Medium": {"actor": "Item_Wallet_Medium", "stock": 0, "isget": False},
        "Item_Wallet_Large": {"actor": "Item_Wallet_Large", "stock": 0, "isget": False},
    }
    assert snap["rupees"] == 37 + 5 * ROUTE.index("house-claimed")
    assert snap["other_sources"] == {"count": 97, "set": 1, "unset": 96, "partial": 0, "unknown": 0}


@pytest.mark.parametrize(
    ("played_phase", "checked_phase", "failed"),
    [
        ("tree-collected", "tree-abandoned", {"source.tree", "item.boomerang"}),
        ("tree-reloaded-uncollected", "tree-collected", {"source.tree", "item.boomerang"}),
        ("tower-collected", "tree-collected", {"source.tower", "item.hylian_shield"}),
        ("tower-collected", "control-collected", {"tokens", "source.control"}),
        ("chest-opened", "control-collected", {"tokens", "chest"}),
        ("house-claimed", "chest-opened", {"house10", "item.house"}),
        ("chest-opened", "reload", {"house10", "item.house"}),
    ],
)
def test_a_save_of_another_step_fails_exactly_what_differs(played_phase, checked_phase, failed):
    report = run(played(played_phase), checked_phase)
    assert (report["verdict"], report["exit_code"], failing(report)) == ("fail", 1, failed)


@pytest.mark.parametrize(
    ("phase", "keys_removed", "keys_added"),
    [
        ("tree-collected", {TREE ^ 2}, set()),  # collection wrote one record
        ("tree-collected", {TREE}, set()),
        ("tree-abandoned", set(), {TREE}),  # the kill half-committed the source
    ],
)
def test_a_partial_source_pair_fails(phase, keys_removed, keys_added):
    state = played(phase)
    state.keys = (state.keys - keys_removed) | keys_added
    report = run(state, phase)
    check = by_id(report)[("save", "source.tree")]
    assert (check["status"], check["actual"]) == ("fail", "partial")
    assert failing(report) == {"source.tree"}


def test_the_control_companion_is_hash_xor_2_not_hash_plus_2():
    assert tp.companion(CONTROL) == CONTROL_COMPANION != CONTROL + 2
    state = played("control-collected")
    state.keys = (state.keys - {CONTROL_COMPANION}) | {CONTROL + 2}
    report = run(state, "control-collected")
    check = by_id(report)[("save", "source.control")]
    assert (check["status"], check["expected"], check["actual"]) == ("fail", "set", "partial")
    assert report["save"]["core_sources"]["control"]["companion_set"] is False
    assert failing(report) == {"source.control"}


def test_the_token_chest_completes_no_other_source():
    state = played("chest-opened")
    state.collect(OTHERS[0])
    report = run(state, "chest-opened")
    assert failing(report) == {"sources.others"}
    assert by_id(report)[("save", "sources.others")]["actual"] == [
        {
            "hash": OTHERS[0],
            "baseline": {"primary_set": False, "companion_set": False},
            "save": {"primary_set": True, "companion_set": True},
        }
    ]


def test_the_token_chest_counts_independently_of_sources():
    without_control = played("chest-opened")
    without_control.keys -= {CONTROL, CONTROL_COMPANION}
    without_control.ints[stock("Item_Token_Gold")] = 10  # only the chest's token
    assert failing(run(without_control, "chest-opened")) == {"tokens", "source.control"}
    uncounted = played("chest-opened")
    uncounted.ints[stock("Item_Token_Gold")] = 10  # chest open, count unchanged
    assert failing(run(uncounted, "chest-opened")) == {"tokens"}


@pytest.mark.parametrize("phase", ["tree-collected", "tower-collected"])
def test_a_non_token_reward_adds_no_token(phase):
    state = played(phase)
    state.ints[stock("Item_Token_Gold")] += 1
    assert failing(run(state, phase)) == {"tokens"}


def test_a_token_paid_in_place_of_the_boomerang_fails():
    state = played("tree-reloaded-uncollected")
    state.collect(TREE)
    state.ints[stock("Item_Token_Gold")] = 10
    assert failing(run(state, "tree-collected")) == {"tokens", "item.boomerang"}


@pytest.mark.parametrize(
    ("granted", "committed", "failed"),
    [
        (True, False, {"source.tree"}),
        (False, True, {"item.boomerang"}),
        (False, False, {"source.tree", "item.boomerang"}),
    ],
)
def test_first_pickup_separates_reward_delivery_from_source_completion(granted, committed, failed):
    state = played("tree-reloaded-uncollected")
    if granted:
        state.grant("Item_Boomerang")
    if committed:
        state.collect(TREE)
    report = run(state, "tree-collected")
    assert failing(report) == failed
    assert report["save"]["tokens"]["stock"] == 9
    assert report["save"]["items"]["boomerang"]["stock"] == int(granted)
    assert report["save"]["core_sources"]["tree"]["state"] == ("set" if committed else "unset")


@pytest.mark.parametrize(
    ("section", "name", "value", "failed"),
    [
        ("ints", stock("Item_Hammer"), 2, "item.house"),  # the House paid again
        ("ints", stock("Item_Boomerang"), 2, "item.boomerang"),  # a re-collected reward granted again
        ("ints", stock("Item_Token_Gold"), 12, "tokens"),  # a token paid twice
        ("ints", stock("Item_Wallet_Medium"), 1, "wallets"),  # a wallet with the House reward
        ("bools", "IsGet.Item_Wallet_Large", True, "wallets"),
        ("bools", CHEST, False, "chest"),  # the chest closed again
        ("bools", HOUSE, False, "house10"),  # the House 10 reward claimable again
    ],
)
def test_reload_duplicates_bonuses_and_reverted_flags_fail(section, name, value, failed):
    state = played("reload")
    getattr(state, section)[name] = value
    report = run(state, "reload")
    assert by_id(report)[("save", failed)]["status"] == "fail"
    assert (report["verdict"], failing(report)) == ("fail", {failed})


def test_a_source_lost_on_reload_fails():
    state = played("reload")
    state.keys -= {TOWER, TOWER ^ 2}
    assert failing(run(state, "reload")) == {"source.tower"}


@pytest.mark.parametrize(
    ("section", "name", "check_id"),
    [
        ("bools", CHEST, "chest"),
        ("bools", HOUSE, "house10"),
        ("ints", stock("Item_Token_Gold"), "tokens"),
        ("bools", "IsGet.Item_Hammer", "item.house"),
        ("ints", stock("Weapon_Shield_Hylian"), "item.hylian_shield"),
        ("ints", stock("Item_Wallet_Large"), "wallets"),
        ("bools", "IsGet.Item_Wallet_Medium", "wallets"),
    ],
)
def test_a_missing_record_is_unknown_never_false_or_zero(section, name, check_id):
    state = played("reload")
    del getattr(state, section)[name]
    report = run(state, "reload")
    check = by_id(report)[("save", check_id)]
    values = check["actual"].values() if isinstance(check["actual"], dict) else [check["actual"]]
    flat = [v for value in values for v in (value.values() if isinstance(value, dict) else [value])]
    assert check["status"] == "unknown" and None in flat
    assert (report["verdict"], report["exit_code"], failing(report)) == ("unknown", 2, {check_id})


@pytest.mark.parametrize(
    "options",
    [
        {"bool64": False},
        {"version": VERSION + 1},
        {"save_type": SAVE_TYPE ^ 1},
        {"terminate": False},
    ],
)
def test_a_save_of_another_layout_is_a_contract_error_with_every_value_unknown(options):
    report = run(played("reload").encode(**options), "reload")
    assert (report["verdict"], report["exit_code"]) == ("contract_error", 3)
    snap = report["save"]
    assert snap["trusted"] is False
    assert (snap["tokens"]["stock"], snap["chest"]["open"], snap["house10"]["claimed"]) == (None, None, None)
    assert {pair["state"] for pair in snap["core_sources"].values()} == {"unknown"}
    assert {item["stock"] for item in snap["items"].values()} == {None}
    assert snap["other_sources"]["unknown"] == 97
    assert {c["status"] for c in report["checks"] if c["scope"] == "save"} == {"unknown"}


def test_a_baseline_other_than_the_accepted_checkpoint_is_a_contract_error():
    report = run(played("baseline"), "baseline", baseline=played("tree-abandoned").encode())
    assert (report["verdict"], report["exit_code"]) == ("contract_error", 3)


@pytest.mark.parametrize(
    ("section", "name", "value", "check_id", "status"),
    [
        ("ints", stock("Item_Hammer"), 1, "item.house", "fail"),  # the House item already owned
        ("bools", "IsGet.Item_Boomerang", True, "item.boomerang", "fail"),
        ("ints", stock("Item_Token_Gold"), 10, "tokens", "fail"),
        ("bools", CHEST, True, "chest", "fail"),
        ("ints", stock("Item_Hammer"), MISSING, "item.house", "unknown"),
    ],
)
def test_a_baseline_outside_the_starting_state_is_a_contract_error(section, name, value, check_id, status):
    state = checkpoint()
    if value is MISSING:
        del getattr(state, section)[name]
    else:
        getattr(state, section)[name] = value
    data = state.encode()
    manifest = tp.parse_manifest(manifest_dict(baseline_sha256=hashlib.sha256(data).hexdigest()))
    report = run(data, "baseline", baseline=data, manifest=manifest)
    assert report["contract"] == [] and report["same_bytes_as_baseline"] is True
    assert (report["verdict"], report["exit_code"]) == ("contract_error", 3)
    assert by_id(report)[("baseline", check_id)]["status"] == status
    assert failing(report, "baseline") == {check_id}


def test_cli_prints_json_exits_by_verdict_and_writes_nothing(tmp_path, capsys):
    (tmp_path / "manifest.json").write_text(json.dumps(manifest_dict()), encoding="utf-8")
    (tmp_path / "bad-manifest.json").write_text(json.dumps(manifest_dict(build="0")), encoding="utf-8")
    (tmp_path / "baseline.sav").write_bytes(BASELINE)
    (tmp_path / "chest.sav").write_bytes(played("chest-opened").encode())
    unknown = played("chest-opened")
    del unknown.bools[CHEST]
    (tmp_path / "unknown.sav").write_bytes(unknown.encode())
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.iterdir()}

    def cli(manifest: str, save_name: str, phase: str) -> tuple[int, str, int]:
        args = ["--manifest", str(tmp_path / manifest), "--baseline", str(tmp_path / "baseline.sav")]
        code = tp.main([*args, "--save", str(tmp_path / save_name), "--phase", phase])
        out = json.loads(capsys.readouterr().out)
        assert out["paths"]["save"] == str(tmp_path / save_name)
        return code, out["verdict"], out["exit_code"]

    assert cli("manifest.json", "chest.sav", "chest-opened") == (0, "pass", 0)
    assert cli("manifest.json", "chest.sav", "house-claimed") == (1, "fail", 1)
    assert cli("manifest.json", "unknown.sav", "chest-opened") == (2, "unknown", 2)
    assert cli("bad-manifest.json", "chest.sav", "chest-opened") == (3, "contract_error", 3)
    assert cli("manifest.json", "absent.sav", "chest-opened") == (3, "contract_error", 3)
    assert {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.iterdir()} == before


@pytest.mark.dump
def test_the_checked_records_exist_in_the_native_game_data(romfs):
    """The real census satisfies the manifest contract, every source record the checker reads is a saved
    Bool64bitKey row (so a key absent from a save's list is unset, not missing), and every named record is a saved
    Bool or Int of progress.sav."""
    census = scan(romfs)
    sources = tp.census_sources(census)
    manifest = tp.parse_manifest(manifest_dict(source_hashes=list(sources)))
    assert [loc.kind for loc in census if loc.id == tp.CHEST_HASH] == ["chest"]
    data = read_romfs_byml(romfs, zsdic.Dictionaries.from_romfs(romfs), GAME_DATA_LIST)["Data"]
    rows64 = {int(row["Hash"]): row for row in data["Bool64bitKey"]}
    records = [h for source in manifest.source_hashes for h in (source, tp.companion(source))]
    missing = [h for h in records if h not in rows64]
    unsaved = {
        h: (rows64[h].get("ResetTypeValue"), rows64[h].get("SaveFileIndex"))
        for h in records
        if h in rows64 and (rows64[h].get("ResetTypeValue") != 24 or rows64[h].get("SaveFileIndex") != 0)
    }
    print(f"{len(sources)} sources, {len(records)} records; missing {missing}; not (24, 0): {unsaved}")
    assert not missing and not unsaved
    actors = [*manifest.actors().values(), *tp.WALLETS]
    named = {
        "Bool": [tp.CHEST_FLAG, tp.HOUSE_FLAG, f"IsGet.{tp.TOKEN}", *(f"IsGet.{a}" for a in actors)],
        "Int": [tp.TOKEN_STOCK, tp.RUPEES, *(stock(a) for a in actors)],
    }
    for list_type, names in named.items():
        rows = {int(row["Hash"]): row for row in data[list_type]}
        found = {name: rows.get(save.key(name), {}).get("SaveFileIndex") for name in names}
        print(list_type, found)
        assert found == dict.fromkeys(names, 0)
