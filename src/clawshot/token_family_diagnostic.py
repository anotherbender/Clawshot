"""Build an approved reward-family packet (``--packet 1`` or ``2``), not a randomized seed or admission proof.

Packet 1 (played): the historical ranch checkpoint; six representatives plus the played Boomerang bootstrap occupy
seven accessible child sources. Packet 2: the untouched approved after-Forest slot04 (the route packet's checkpoint);
six representatives, no bootstrap, collected after a native return to child. The external isolated launcher copies
the checkpoint, which is never edited. Production admission is independent: each packet declares its diagnostic
actors explicitly.
"""

import argparse
import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path, PurePosixPath

from clawshot import save, token_route_diagnostic
from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import sarc, zsdic
from clawshot.patch import actor_packs, tokens
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import check_output_folder, check_romfs, write
from clawshot.token_diagnostic import CHECKPOINT_SHA256
from clawshot.token_family_packet import check_packet, parse_manifest
from clawshot.token_packet import census_sources

AGE = token_route_diagnostic.AGE  # the native child flag the route packet checks
AFTER_FOREST_SHA256 = token_route_diagnostic.CHECKPOINT_SHA256  # the approved after-Forest slot04

# Ordered route, not census indices. Fields below describe native saved inventory effects.
ASSIGNMENTS = (
    (341792603838029977, "LLR GS Tree", "Item_Boomerang", "fixed_major", "boomerang"),
    (2730878115209290675, "LLR GS Tower", "Obj_Heart_Piece", "heart_piece", "heart-piece"),
    (15889002414176907668, "LLR GS House Window", "Item_Bottle_Milk", "bottle", "milk-bottle"),
    (2177746409373494991, "HF GS Lone Tree", "Obj_Rupee_Red", "rupee", "rupees"),
    (11629189455828560791, "Kak GS Near Gate Guard", "Obj_Heart_Container", "heart_container", "heart-container"),
    (15118290503807073158, "Kak GS Watchtower", "Item_NutBag_Medium", "fixed_capacity", "nut-capacity"),
    (17067594426901953848, "KF GS Know It All House", "Item_BombchuBundle_Small", "bombchu", "bombchus"),
)
BOTTLE_SLOTS = (
    (4087145488, 2101927798),
    (1046250, 517805642),
    (4131066260, 3087823016),
    (3085980366, 3837899260),
    (3799716717, 912136531),
)
ACTORS = (
    "Item_Boomerang",
    "Obj_Heart_Piece",
    "Item_NutBag_Medium",
    "Item_DekuNut",
    "Item_Bombchu",
    "Item_Wallet_Medium",
    "Item_Wallet_Large",
)
INTS = (
    "PlayerStatus.CurrentRupee",
    "PlayerStatus.MaxLife",
    *(f"PouchData.{actor}.StockNum" for actor in ACTORS),
)
BOOLS = (*("IsGet." + actor for actor in ACTORS), "IsGet.Item_Bottle_Milk")

# Packet 2, in route order (plans/rounds/r15-scrub-tokens.md). Use a native world donor where available;
# the Magic Jar is Obj_MagicJar_Large, not its Tbox_ wrapper or a Buy refill. Families are native
# patch.tokens.FAMILIES shapes, which tokens.build re-checks.
TREE, TOWER, WINDOW, LONE, GATE, WATCHTOWER = (
    341792603838029977,
    2730878115209290675,
    15889002414176907668,
    2177746409373494991,
    11629189455828560791,
    15118290503807073158,
)
ASSIGNMENTS_2 = (
    (TREE, "LLR GS Tree", "Item_BombchuBundle_Small", "bombchu"),
    (TOWER, "LLR GS Tower", "Item_DinFire", "spell"),
    (WINDOW, "LLR GS House Window", "Item_GlassTruth", "lens"),
    (LONE, "HF GS Lone Tree", "Obj_MagicJar_Large", "magic_recovery"),
    (GATE, "Kak GS Near Gate Guard", "Item_AgonyStone", "agony_stone"),
    (WATCHTOWER, "Kak GS Watchtower", "Obj_Rupee_Gold", "gold_rupee"),
)
CHU, DIN, LENS, AGONY = "Item_Bombchu", "Item_DinFire", "Armor_GlassTruth", "Item_AgonyStone"
# What each built pickup's effective pouch grants: a PouchActor (the saved identity) or a bundle of its BundleActor.
GRANTS_2 = {
    "Item_BombchuBundle_Small": ("BundleActor", CHU),
    "Item_DinFire": ("PouchActor", DIN),
    "Item_GlassTruth": ("PouchActor", LENS),  # the canonical ActorName: Armor_GlassTruth
    "Obj_MagicJar_Large": ("PouchActor", "Obj_MagicJar_Large"),  # native world donor, not a chest wrapper
    "Item_AgonyStone": ("PouchActor", AGONY),
    "Obj_Rupee_Gold": ("BundleActor", "Obj_Rupee_Green"),
}
RUPEES, MAX_LIFE = "PlayerStatus.CurrentRupee", "PlayerStatus.MaxLife"
MAGIC_MAX, MAGIC = "PlayerStatus.MPMax", "PlayerStatus.MP"
BOMB_MAX, WALLET_MAX = "PouchContentMaxNum.Bomb", "PouchContentMaxNum.Rupee"
QUESTS = ("Step_SageOfForest", "Step_DoorOfTime")
# Saved magic is ten times a PouchActorInfo MPMax: raw PlayerStatus.MPMax 240 is the 24 meter and 480 the 48 double
# (r14 progressive play: MPDouble raised 240 to 480; tracker [SL1]). PlayerStatus.MP uses the same unit (backups: a full
# meter saves MP 240 of 240, 480 of 480). MPMaxUP raises an empty meter only (r13 grant audit).
MAGIC_SAVE_SCALE = 10
OWNED_2 = (
    CHU,
    "Item_BombBag_Small",
    "Item_BombBag_Medium",
    "Item_BombBag_Large",
    "Item_Boomerang",
    DIN,
    LENS,
    AGONY,
    "Item_Wallet_Medium",
    "Item_Wallet_Large",
    "Item_FairyBless_MP",
    "Item_FairyBless_MPDouble",
)


def _stock(actor: str) -> tuple[str, str]:
    return "int", f"PouchData.{actor}.StockNum"


def _got(actor: str) -> tuple[str, str]:
    return "bool", f"IsGet.{actor}"


CARRIED_2 = (
    *(key for actor in OWNED_2 for key in (_stock(actor), _got(actor))),
    *(("int", name) for name in (RUPEES, WALLET_MAX, MAX_LIFE, MAGIC_MAX, BOMB_MAX)),
    ("bool", AGE),
    *(("enum", name) for name in QUESTS),
)
# Recorded at the baseline only: current magic varies with timing (the jar's full refill is checked in its own phase
# only), and the pickups' own identities' IsGet may or may not be written by the native grant; never predicted.
OBSERVED_2 = (
    ("int", MAGIC),
    _got("Item_BombchuBundle_Small"),
    _got("Obj_MagicJar_Large"),
    _got("Obj_Rupee_Gold"),
)
REQUIRED_2 = {
    ("bool", AGE): False,
    **{("enum", name): save.key("Complete") for name in QUESTS},
    ("int", RUPEES): 148,
    ("int", WALLET_MAX): 500,
    ("int", MAX_LIFE): 28,
    ("int", MAGIC_MAX): 0,
    ("int", BOMB_MAX): 20,
    _stock("Item_Boomerang"): 1,
    _got("Item_Boomerang"): True,
    _stock("Item_BombBag_Small"): 1,
    _got("Item_BombBag_Small"): True,
    **{_stock(actor): 0 for actor in (CHU, DIN, LENS, AGONY)},
    **{_got(actor): False for actor in (CHU, DIN, LENS, AGONY)},
}
# Native PouchActorInfo values the phases rest on: (actor, field) -> value (an actor reference by its actor name).
NATIVE_2 = {
    ("Item_BombchuBundle_Small", "BundleActor"): CHU,
    (CHU, "MaxNumGameData"): "Bomb",
    (CHU, "SmallBagActor"): "Item_BombBag_Small",
    ("Item_DinFire", "ExpansionAvility"): "MPMaxUP",
    ("Item_GlassTruth", "ExpansionAvility"): "MPMaxUP",
    ("Obj_MagicJar_Large", "PouchSpecialDeal"): "NotPushToPouch",
    ("Obj_MagicJar_Large", "ExpansionAvility"): None,
    ("Obj_MagicJar_Large", "MPMax"): None,
    ("Obj_Rupee_Gold", "BundleActor"): "Obj_Rupee_Green",
    ("Obj_Rupee_Green", "MaxNumGameData"): "Rupee",
}
COUNTS_2 = (
    ("Item_BombchuBundle_Small", "BundleActorNum"),
    ("Item_DinFire", "MPMax"),
    ("Item_GlassTruth", "MPMax"),
    ("Obj_MagicJar_Large", "MPRecover"),
    ("Obj_Rupee_Gold", "BundleActorNum"),
)


def _fields(values: dict[tuple[str, str | int], int | bool]) -> list[dict]:
    return [
        {"name": name, "kind": kind, "value": value}
        for (kind, name), value in sorted(values.items(), key=lambda row: (row[0][0], str(row[0][1])))
    ]


def _baseline_fields(baseline: save.Save) -> dict[tuple[str, str | int], int | bool]:
    values = {}
    for kind, names, read in (
        ("int", INTS, baseline.int_value),
        ("bool", BOOLS, baseline.flag),
        ("bool", tuple(valid for valid, _ in BOTTLE_SLOTS), baseline.flag),
        ("enum", tuple(content for _, content in BOTTLE_SLOTS), baseline.enum_value),
    ):
        for name in names:
            value = read(name)
            if value is None:
                raise PatchError(f"families-1 baseline missing {kind} {name!r}")
            values[kind, name] = value
    required = {
        ("int", "PlayerStatus.CurrentRupee"): 68,
        ("int", "PlayerStatus.MaxLife"): 16,
        ("int", "PouchData.Item_Boomerang.StockNum"): 0,
        ("int", "PouchData.Obj_Heart_Piece.StockNum"): 0,
        ("int", "PouchData.Item_NutBag_Medium.StockNum"): 0,
        ("int", "PouchData.Item_Bombchu.StockNum"): 0,
        ("bool", BOTTLE_SLOTS[0][0]): True,
        **{("bool", valid): False for valid, _ in BOTTLE_SLOTS[1:]},
    }
    wrong = {
        str(key): {"expected": expected, "actual": values.get(key)}
        for key, expected in required.items()
        if values.get(key) != expected
    }
    if wrong:
        raise PatchError(f"families-1 checkpoint preconditions differ: {wrong}")
    return values


def _phases(initial: dict[tuple[str, str | int], int | bool]) -> dict:
    values = dict(initial)
    completed = []
    phases = {"baseline": {"completed": [], "fields": _fields(values)}}
    changes = (
        {("int", "PouchData.Item_Boomerang.StockNum"): 1, ("bool", "IsGet.Item_Boomerang"): True},
        {("int", "PouchData.Obj_Heart_Piece.StockNum"): 1, ("bool", "IsGet.Obj_Heart_Piece"): True},
        {
            ("bool", BOTTLE_SLOTS[1][0]): True,
            ("enum", BOTTLE_SLOTS[1][1]): save.key("MaxMilk"),
            ("bool", "IsGet.Item_Bottle_Milk"): True,
        },
        {("int", "PlayerStatus.CurrentRupee"): 88},
        {("int", "PlayerStatus.MaxLife"): 20},
        {
            ("int", "PouchData.Item_NutBag_Medium.StockNum"): 1,
            ("bool", "IsGet.Item_NutBag_Medium"): True,
            ("int", "PouchData.Item_DekuNut.StockNum"): 30,
        },
        {("int", "PouchData.Item_Bombchu.StockNum"): 5, ("bool", "IsGet.Item_Bombchu"): True},
    )
    for (source, _, _, _, phase), change in zip(ASSIGNMENTS, changes, strict=True):
        values.update(change)
        completed.append(str(source))
        phases[phase] = {"completed": list(completed), "fields": _fields(values)}
        if phase == "boomerang":
            phases["heart-abandoned"] = {"completed": list(completed), "fields": _fields(values)}
    phases["reload"] = {"completed": list(completed), "fields": _fields(values)}
    values.update({("int", "PouchData.Item_Bombchu.StockNum"): 4, ("enum", BOTTLE_SLOTS[1][1]): save.key("Empty")})
    phases["used"] = {"completed": list(completed), "fields": _fields(values)}
    phases["used-reload"] = {"completed": list(completed), "fields": _fields(values)}
    return phases


def _plan_1(baseline: save.Save, romfs: Path, dictionaries: zsdic.Dictionaries) -> tuple[dict, dict]:
    return _phases(_baseline_fields(baseline)), {}


def _actor_name(value: object) -> object:
    """``Work/Actor/X.engine__actor__ActorParam.gyml`` -> ``X``; anything else as it is (plain ints for byml ints)."""
    if isinstance(value, str) and value.startswith("Work/Actor/"):
        return PurePosixPath(value).name.split(".", 1)[0]
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else value


def _baseline_2(baseline: save.Save) -> tuple[dict, dict]:
    """The fields every phase carries and the baseline-only observations, all read from the save, never defaulted."""
    read = {"int": baseline.int_value, "bool": baseline.flag, "enum": baseline.enum_value}
    values = {}
    for kind, name in (*CARRIED_2, *OBSERVED_2):
        value = read[kind](name)
        if value is None:
            raise PatchError(f"families-2 baseline missing {kind} {name!r}")
        values[kind, name] = value
    wrong = {
        str(key): {"expected": expected, "actual": values[key]}
        for key, expected in REQUIRED_2.items()
        if values[key] != expected
    }
    if wrong:
        raise PatchError(f"families-2 checkpoint preconditions differ: {wrong}")
    observed = {key: values.pop(key) for key in OBSERVED_2}
    return values, observed


def _native_2(rows: Mapping[str, Mapping]) -> dict[str, dict]:
    """The native PouchActorInfo values the phases rest on, refused unless they are the ones the design read."""
    facts: dict[str, dict] = {}
    for actor, key in (*NATIVE_2, *COUNTS_2):
        if actor not in rows:
            raise PatchError(f"families-2: no native PouchActorInfo row {actor}")
        facts.setdefault(actor, {})[key] = _actor_name(rows[actor].get(key))
    wrong = {
        f"{actor}.{key}": {"expected": expected, "actual": facts[actor][key]}
        for (actor, key), expected in NATIVE_2.items()
        if facts[actor][key] != expected
    }
    for actor, key in COUNTS_2:
        value = facts[actor][key]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            wrong[f"{actor}.{key}"] = {"expected": "a positive integer", "actual": value}
    if facts["Item_GlassTruth"]["MPMax"] != facts["Item_DinFire"]["MPMax"]:
        wrong["Item_GlassTruth.MPMax"] = {
            "expected": f"Din's Fire's tier {facts['Item_DinFire']['MPMax']}",
            "actual": facts["Item_GlassTruth"]["MPMax"],
        }
    if wrong:
        raise PatchError(f"families-2 native rows differ: {wrong}")
    return facts


def _phases_2(carried: dict, observed: dict, facts: Mapping[str, Mapping]) -> dict:
    """Cumulative saved state in route order. Current magic varies with timing.
    The jar's full-refill check requires the explicitly bounded partial-meter precondition in the checklist."""
    chus = carried[_stock(CHU)] + facts["Item_BombchuBundle_Small"]["BundleActorNum"]
    magic = facts["Item_DinFire"]["MPMax"] * MAGIC_SAVE_SCALE
    rupees = carried["int", RUPEES] + facts["Obj_Rupee_Gold"]["BundleActorNum"]
    if chus > carried["int", BOMB_MAX]:
        raise PatchError(f"families-2: {chus} Bombchus exceed {BOMB_MAX} {carried['int', BOMB_MAX]}")
    if rupees > carried["int", WALLET_MAX]:
        raise PatchError(f"families-2: {rupees} rupees exceed {WALLET_MAX} {carried['int', WALLET_MAX]}")
    steps = (  # phase, source it completes, carried changes, fields checked in that phase only
        ("child-ready", None, {("bool", AGE): True}, {}),
        ("bombchu-collected", TREE, {_stock(CHU): chus, _got(CHU): True}, {}),
        ("bombchu-used", None, {_stock(CHU): chus - 1}, {}),
        ("din-abandoned", None, {}, {}),
        ("din-collected", TOWER, {_stock(DIN): 1, _got(DIN): True, ("int", MAGIC_MAX): magic}, {}),
        ("lens-collected", WINDOW, {_stock(LENS): 1, _got(LENS): True}, {}),
        ("magic-spent", None, {}, {}),
        ("jar-collected", LONE, {}, {("int", MAGIC): magic}),
        ("agony-collected", GATE, {_stock(AGONY): 1, _got(AGONY): True}, {}),
        ("gold-collected", WATCHTOWER, {("int", RUPEES): rupees}, {}),
        ("reload", None, {}, {}),
        ("used", None, {}, {}),
        ("used-reload", None, {}, {}),
    )
    if [step[1] for step in steps if step[1] is not None] != [source for source, *_ in ASSIGNMENTS_2]:
        raise PatchError("families-2 phases do not collect the assignments in route order")
    values, completed = dict(carried), []
    phases = {"baseline": {"completed": [], "fields": _fields({**values, **observed})}}
    for name, source, change, only in steps:
        values.update(change)
        if source is not None:
            completed.append(str(source))
        phases[name] = {"completed": list(completed), "fields": _fields({**values, **only})}
    return phases


def _obligations_2(facts: Mapping[str, Mapping]) -> dict[str, str]:
    """What saved state cannot show, per phase: the parent's visual and before/after checks."""
    recover = facts["Obj_MagicJar_Large"]["MPRecover"]
    gold = facts["Obj_Rupee_Gold"]["BundleActorNum"]
    rupees, wallet = REQUIRED_2["int", RUPEES], REQUIRED_2["int", WALLET_MAX]
    magic = facts["Item_DinFire"]["MPMax"] * MAGIC_SAVE_SCALE
    minimum = max(0, magic - recover)
    return {
        "child-ready": "Native Master Sword pedestal return to child; no age cheat.",
        "bombchu-collected": "Save right after the ranch tree pickup, before any Bombchu use; the get names Bombchus.",
        "bombchu-used": "Use exactly one Bombchu (it runs and explodes), then save.",
        "din-abandoned": (
            "Night: kill the tower Skulltula, leave its high pickup uncollected, leave the ranch or reload, then save."
        ),
        "din-collected": (
            "Return: recover the remaining drop or retrigger the source if needed, then Boomerang-retrieve it. "
            f"Report whether the magic gauge appears and read {MAGIC} from this save (not predicted)."
        ),
        "lens-collected": "Night window pickup: the get names the Lens of Truth.",
        "magic-spent": (
            "Set and briefly toggle the Lens (view changes, gauge drains), then turn it off and save; "
            f"read {MAGIC} m0: require {minimum} < m0 < {magic}, not merely any partial gauge. Stop if outside "
            "that range; do not consume more magic before the jar."
        ),
        "jar-collected": (
            "Lone tree jar: save immediately with Lens off and no further magic use. For the required small "
            f"pre-pickup deficit (m0 > {minimum}), expect full {MAGIC} == {MAGIC_MAX}; native MPRecover is "
            f"{recover}. Report m0 -> m1 and the visible refill; this is not a claim one jar fills every empty meter."
        ),
        "agony-collected": (
            "Any time after this pickup: equip the Echo Gem, Map-Teleport and bomb open (a bomb, never a Bombchu) the "
            "child wooded Near Kak grotto (cover -156,144,338) and approach its native AgonyStoneReactArea "
            "17897764476642920225 at (-149.06,128.84,320.78); report the effect. Never kill or collect its Gold "
            "12007978132755687032 (the checker's other-source conservation). Kakariko child static has no react area."
        ),
        "gold-collected": (
            f"Gold Rupee get: rupees exactly +{gold} inside wallet capacity {wallet} (checker {rupees} -> "
            f"{rupees + gold})."
        ),
        "reload": "Save and Continue: every grant and completion kept.",
        "used": (
            f"After reload cast Din's Fire and toggle the Lens again (still usable), then save; {MAGIC} not predicted."
        ),
        "used-reload": "Save and Continue after use: same saved state.",
    }


def _plan_2(baseline: save.Save, romfs: Path, dictionaries: zsdic.Dictionaries) -> tuple[dict, dict]:
    carried, observed = _baseline_2(baseline)
    rows = {row["__RowId"]: row for row in read_romfs_byml(romfs, dictionaries, tokens.POUCH_ACTOR_INFO)}
    facts = _native_2(rows)
    return _phases_2(carried, observed, facts), {
        "native_rows": facts,
        "magic_save_scale": MAGIC_SAVE_SCALE,
        "baseline_only": [{"name": name, "kind": kind} for kind, name in OBSERVED_2],
        "proof_obligations": _obligations_2(facts),
        "estimate": "16-19 minutes, not timed",
    }


def _grants_2(delivery: tokens.Delivery, manifest: Mapping) -> dict:
    """Each built pickup's effective pouch grant, refused unless it is the identity or bundle the phases expect."""
    facts = manifest["native_rows"]
    packs = {file.path: file.data for file in delivery.new_files}
    found, wrong = {}, {}
    for item, (key, expected) in GRANTS_2.items():
        pickup = delivery.pickups[item]
        members = sarc.read(packs[tokens.pack_path(pickup)])
        components = actor_packs.resolve([members], actor_packs.actor_member(pickup))[0]["Components"]
        pouch = actor_packs.resolve_node(
            [members], actor_packs.reference(components["PouchContentRef"]), builtin=tokens.POUCH_DEFAULT
        )
        grant = {name: _actor_name(pouch.get(name)) for name in ("PouchActor", "BundleActor", "BundleActorNum")}
        grant["IsBundle"] = bool(pouch.get("IsBundle"))
        found[item] = {"pickup": pickup, **grant}
        bundle = key == "BundleActor"
        count = facts[item]["BundleActorNum"] if bundle else None
        if grant[key] != expected or grant["IsBundle"] != bundle or (bundle and grant["BundleActorNum"] != count):
            wrong[item] = {"expected": {key: expected, "IsBundle": bundle, "BundleActorNum": count}, "built": grant}
    if wrong:
        raise PatchError(f"families-2 built pickups grant otherwise: {wrong}")
    return {"built_grants": found}


@dataclass(frozen=True)
class Packet:
    sha256: str
    assignments: tuple[tuple[int, str, str, str], ...]  # source, name, actor, family
    manifest: str  # the checker manifest's file name in the output folder
    kind: str
    plan: Callable[[save.Save, Path, zsdic.Dictionaries], tuple[dict, dict]]  # phases, further manifest keys
    built: Callable[[tokens.Delivery, Mapping], dict]  # further manifest keys from the built pickups


PACKETS = {
    1: Packet(
        CHECKPOINT_SHA256,
        tuple(row[:4] for row in ASSIGNMENTS),
        "token-families.json",
        "forced families-1 diagnostic; not a randomized or beatable seed",
        _plan_1,
        lambda delivery, manifest: {},
    ),
    2: Packet(
        AFTER_FOREST_SHA256,
        ASSIGNMENTS_2,
        "token-families-2.json",
        "forced families-2 diagnostic; not a randomized or beatable seed",
        _plan_2,
        _grants_2,
    ),
}


def build(romfs: Path, checkpoint: Path, out: Path, *, revision: str, packet: int = 1) -> dict:
    """Validate the packet's historical baseline before writing real native resources and checker metadata."""
    if packet not in PACKETS:
        raise PatchError(f"families packet {packet!r}: known packets {sorted(PACKETS)}")
    spec, label = PACKETS[packet], f"families-{packet}"
    check_romfs(romfs)
    check_output_folder(romfs, out)
    if not revision.strip():
        raise PatchError("the families diagnostic requires an explicit source revision")
    original = checkpoint.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != spec.sha256:
        raise PatchError(f"{label} checkpoint SHA256 {digest}, expected {spec.sha256}")
    baseline = save.read(original)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    phases, extra = spec.plan(baseline, romfs, dictionaries)
    census = scan(romfs)
    sources = census_sources(census)
    tokens.check_save_rows(read_romfs_byml(romfs, dictionaries, GAME_DATA_LIST), sources)
    manifest = {
        "kind": spec.kind,
        "build": "e0f3ccfa",
        "baseline_sha256": digest,
        "baseline_save": str(checkpoint.resolve()),
        "save_version": baseline.version,
        "save_type": baseline.save_type,
        "source_hashes": list(sources),
        "assignments": [
            {"id": str(source), "name": name, "actor": actor, "family": family}
            for source, name, actor, family in spec.assignments
        ],
        "phases": phases,
        **extra,
        "generator_version": version("clawshot"),
        "source_revision": revision,
        "implementation_sha256": {
            path.relative_to(Path(__file__).parent).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(__file__).parent.rglob("*.py"))
        },
        "seed": None,
        "settings": "approved forced family representatives, not production family admission",
        "unplayed": True,
        "debug_policy": (
            "Map Teleport, clock, movement/access Noclip only; no inventory, flag or age cheats; no logic-route claim"
        ),
    }
    preflight = check_packet(parse_manifest(manifest), original, original, "baseline")
    if preflight["verdict"] != "pass":
        raise PatchError(f"{label} baseline checker: {json.dumps(preflight)}")
    by_source = {location.id: location for location in census}
    for source, name, _, _ in spec.assignments:
        location = by_source[source]
        if location.ages not in ("child", "both"):
            raise PatchError(f"{label} child source {name}: {location}")
    delivery = tokens.build(
        romfs,
        {source: actor for source, _, actor, _ in spec.assignments},
        census,
        rewards={actor: family for _, _, actor, family in spec.assignments},
    )
    manifest.update(spec.built(delivery, manifest))
    written = write(Plan([], [], []), romfs, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)
    manifest["written"] = [asdict(file) for file in written]
    manifest["required_pickup_loads"] = [tokens.pack_path(name) for name in sorted(delivery.pickups.values())]
    (out / spec.manifest).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--romfs", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--packet", type=int, choices=sorted(PACKETS), default=1)
    args = parser.parse_args()
    try:
        manifest = build(args.romfs, args.checkpoint, args.out, revision=args.revision, packet=args.packet)
    except (OSError, ValueError) as error:
        parser.exit(2, f"token families diagnostic: {error}\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
