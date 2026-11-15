"""Build an approved reward-family packet, not a randomized seed or admission proof.

Packet 1 (played) uses the historical ranch checkpoint and a Boomerang bootstrap. Packets 2 and 3 use
the untouched approved after-Forest slot04. Packet 3 tests six child rewards then adult/Bow Ice Arrows.
The external isolated launcher copies the checkpoint, which is never edited. Production admission is
independent: each packet declares its diagnostic actors explicitly.
"""

import argparse
import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path, PurePosixPath

from clawshot import save
from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import sarc, zsdic
from clawshot.patch import actor_packs, tokens
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import check_output_folder, check_romfs, write
from tools.token_packets import token_route_diagnostic
from tools.token_packets.token_diagnostic import CHECKPOINT_SHA256, implementation_sha256
from tools.token_packets.token_family_packet import check_packet, parse_manifest
from tools.token_packets.token_packet import census_sources

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

# Packet 3 keeps the six played packet2 source routes and adds one native adult rooftop source.
IMPA = 3310819903461047792
ASSIGNMENTS_3 = (
    (TREE, "LLR GS Tree", "Obj_ArrowBundle_Medium", "refill"),
    (TOWER, "LLR GS Tower", "Item_BombBundle_Small", "refill"),
    (WINDOW, "LLR GS House Window", "TBox_DekuNutBundle", "refill"),
    (LONE, "HF GS Lone Tree", "Item_DekuStickBundle_Small", "refill"),
    (GATE, "Kak GS Near Gate Guard", "Item_FairyBless_DefenseDouble", "double_defense"),
    (WATCHTOWER, "Kak GS Watchtower", "Obj_ScrubBusinessSeed", "scrub_seed"),
    (IMPA, "Kak GS Above Impas House", "Item_Arrow_Ice", "magic_arrow"),
)
GRANTS_3 = {
    "Obj_ArrowBundle_Medium": ("BundleActor", "Item_Arrow_Normal"),
    "Item_BombBundle_Small": ("BundleActor", "Item_Bomb"),
    "TBox_DekuNutBundle": ("BundleActor", "Item_DekuNut"),
    "Item_DekuStickBundle_Small": ("BundleActor", "Item_DekuStick"),
    "Item_FairyBless_DefenseDouble": ("PouchActor", "Item_FairyBless_DefenseDouble"),
    "Obj_ScrubBusinessSeed": ("PouchActor", "Item_ScrubBusinessSeed"),
    "Item_Arrow_Ice": ("PouchActor", "Item_Arrow_Ice"),
}
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

# Packet3 starts with every real weapon/container already present. Full nuts/sticks need native consumption
# before a measurable +3 refill; no diagnostic edits stock or grants a bag.
ARROW, BOMB, NUT, STICK = "Item_Arrow_Normal", "Item_Bomb", "Item_DekuNut", "Item_DekuStick"
ICE, DEFENSE, SEED, BOW = (
    "Item_Arrow_Ice",
    "Item_FairyBless_DefenseDouble",
    "Item_ScrubBusinessSeed",
    "Weapon_Range_Bow",
)
AMMO_3 = {
    "Obj_ArrowBundle_Medium": (ARROW, "Arrow", "Item_Quiver_Small", 5),
    "Item_BombBundle_Small": (BOMB, "Bomb", "Item_BombBag_Small", 5),
    "TBox_DekuNutBundle": (NUT, "DekuNut", "Item_NutBag_Small", 3),
    "Item_DekuStickBundle_Small": (STICK, "DekuStick", "Item_StickBag_Small", 3),
}
OWNED_3 = (
    BOW,
    "Item_Hookshot",
    "Item_Quiver_Small",
    "Item_NutBag_Small",
    "Item_StickBag_Small",
    ARROW,
    BOMB,
    NUT,
    STICK,
    ICE,
    DEFENSE,
    SEED,
)
CAPS_3 = {
    f"PouchContentMaxNum.{name}": cap for name, cap in (("Arrow", 30), ("Bomb", 20), ("DekuNut", 20), ("DekuStick", 10))
}
CARRIED_3 = tuple(
    dict.fromkeys(
        (
            *CARRIED_2,
            *(key for actor in OWNED_3 for key in (_stock(actor), _got(actor))),
            *(("int", name) for name in CAPS_3),
        )
    )
)
OBSERVED_3 = (("int", MAGIC), ("int", "PlayerStatus.Life"))
REQUIRED_3 = {
    **REQUIRED_2,
    **{("int", name): value for name, value in CAPS_3.items()},
    **{
        _stock(actor): 1
        for actor in (BOW, "Item_Hookshot", "Item_Quiver_Small", "Item_NutBag_Small", "Item_StickBag_Small")
    },
    **{
        _got(actor): True
        for actor in (
            BOW,
            "Item_Hookshot",
            "Item_Quiver_Small",
            "Item_NutBag_Small",
            "Item_StickBag_Small",
            ARROW,
            BOMB,
            NUT,
            STICK,
            SEED,
        )
    },
    _stock(ARROW): 20,
    _stock(BOMB): 10,
    _stock(NUT): 20,
    _stock(STICK): 10,
    _stock(SEED): 2,
    **{_stock(actor): 0 for actor in (ICE, DEFENSE)},
    **{_got(actor): False for actor in (ICE, DEFENSE)},
    ("int", MAGIC): 0,
    ("int", "PlayerStatus.Life"): 28,
}


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
            "Equip the Echo Gem and observe its native reaction at an uncollected source. Kareem's accepted rc.3 "
            "packet2 result: reaction at Kakariko watchtower after collecting the Gem at the gate source. "
            "The earlier claim that child Kakariko could not react was a disproved inference; the wooded grotto "
            "was not visited. Do not collect any source outside this packet."
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


def _baseline_3(baseline: save.Save) -> tuple[dict, dict]:
    read = {"int": baseline.int_value, "bool": baseline.flag, "enum": baseline.enum_value}
    values = {}
    for kind, name in (*CARRIED_3, *OBSERVED_3):
        value = read[kind](name)
        if value is None:
            raise PatchError(f"families-3 baseline missing {kind} {name!r}")
        values[kind, name] = value
    wrong = {
        str(key): {"expected": want, "actual": values[key]} for key, want in REQUIRED_3.items() if values[key] != want
    }
    if wrong:
        raise PatchError(f"families-3 checkpoint preconditions differ: {wrong}")
    observed = {key: values.pop(key) for key in OBSERVED_3}
    return values, observed


def _native_3(rows: Mapping[str, Mapping]) -> dict:
    expected = {}
    for donor, (actor, capacity, bag, count) in AMMO_3.items():
        expected[donor, "BundleActor"] = actor
        expected[donor, "BundleActorNum"] = count
        expected[actor, "SmallBagActor"] = bag
        expected[actor, "MaxNumGameData"] = capacity
    expected.update(
        {
            ("Obj_ScrubBusinessSeed", "FixedMaxNum"): 30,
            ("Obj_ScrubBusinessSeed", "PouchStockable"): True,
            (DEFENSE, "PouchSpecialDeal"): "FairyBlessDefenseDouble",
            (ICE, "ExpansionAvility"): "MPMaxUP",
            (ICE, "MPMax"): 24,
            (ICE, "AssignableItem"): "IceArrow",
            (ICE, "ShootableActor"): "NormalArrow",
        }
    )
    facts, wrong = {}, {}
    for (actor, key), want in expected.items():
        actual = _actor_name(rows.get(actor, {}).get(key))
        facts.setdefault(actor, {})[key] = actual
        if actual != want:
            wrong[f"{actor}.{key}"] = {"expected": want, "actual": actual}
    if wrong:
        raise PatchError(f"families-3 native rows differ: {wrong}")
    return facts


def _phases_3(carried: dict, observed: dict, facts: Mapping) -> dict:
    arrows = carried[_stock(ARROW)] + facts["Obj_ArrowBundle_Medium"]["BundleActorNum"]
    bombs = carried[_stock(BOMB)] + facts["Item_BombBundle_Small"]["BundleActorNum"]
    magic = facts[ICE]["MPMax"] * MAGIC_SAVE_SCALE
    steps = (
        ("child-ready", None, {("bool", AGE): True}),
        ("ammo-ready", None, {_stock(NUT): 17, _stock(STICK): 7}),
        ("arrows-collected", TREE, {_stock(ARROW): arrows}),
        ("bombs-collected", TOWER, {_stock(BOMB): bombs}),
        ("nuts-collected", WINDOW, {_stock(NUT): 17 + facts["TBox_DekuNutBundle"]["BundleActorNum"]}),
        ("sticks-collected", LONE, {_stock(STICK): 7 + facts["Item_DekuStickBundle_Small"]["BundleActorNum"]}),
        ("damage-before", None, {_stock(BOMB): bombs - 1}),
        ("defense-collected", GATE, {_stock(DEFENSE): 1, _got(DEFENSE): True}),
        ("damage-after", None, {_stock(BOMB): bombs - 2}),
        ("seed-collected", WATCHTOWER, {_stock(SEED): carried[_stock(SEED)] + 1}),
        ("seed-used", None, {}),  # native use without a purchase does not consume the seed (Kareem, rc.3)
        ("reload", None, {}),
        ("adult-ready", None, {("bool", AGE): False}),
        ("ice-abandoned", None, {}),
        ("ice-collected", IMPA, {_stock(ICE): 1, _got(ICE): True, ("int", MAGIC_MAX): magic}),
        ("ice-used", None, {_stock(ARROW): arrows - 1}),
        ("used-reload", None, {}),
    )
    if [source for _, source, _ in steps if source is not None] != [row[0] for row in ASSIGNMENTS_3]:
        raise PatchError("families-3 phases do not collect the assignments in route order")
    values, completed = dict(carried), []
    phases = {"baseline": {"completed": [], "fields": _fields({**values, **observed})}}
    for name, source, change in steps:
        values.update(change)
        if source is not None:
            completed.append(str(source))
        phases[name] = {"completed": list(completed), "fields": _fields(values)}
    return phases


def _plan_3(baseline: save.Save, romfs: Path, dictionaries: zsdic.Dictionaries) -> tuple[dict, dict]:
    carried, observed = _baseline_3(baseline)
    rows = {row["__RowId"]: row for row in read_romfs_byml(romfs, dictionaries, tokens.POUCH_ACTOR_INFO)}
    facts = _native_3(rows)
    return _phases_3(carried, observed, facts), {
        "native_rows": facts,
        "magic_save_scale": MAGIC_SAVE_SCALE,
        "baseline_only": [{"name": name, "kind": kind} for kind, name in OBSERVED_3],
        "observations": [
            {"kind": "int", "name": "PlayerStatus.Life", "purpose": "matched damage before/after Double Defense"},
            {"kind": "int", "name": MAGIC, "purpose": "actual Ice Arrow magic spend"},
        ],
        "proof_obligations": {
            "child-ready": "Native pedestal return to child; no age cheat.",
            "ammo-ready": "Measure three nuts/sticks consumed natively: require17/7; a swing may not consume stock.",
            "arrows-collected": "Actual Arrows5 get:20->25, quiver30 and owned Bow unchanged.",
            "bombs-collected": "Actual Bombs5 get:10->15, Bomb Bag/cap20 unchanged (D25).",
            "nuts-collected": "Logical Nuts5 label is native bundle3:17->20, cap20 unchanged.",
            "sticks-collected": "Logical Stick1 label is native bundle3:7->10, cap10 unchanged.",
            "damage-before": "Record raw Life immediately before/after one unguarded bomb blast at a clear flat spot.",
            "defense-collected": "Observe native Double Defense presentation; saved ownership is not effect proof.",
            "damage-after": (
                "Same comparable unguarded blast/position: record Life loss d1 and require0<d1<d0. "
                "No guessed engine defense flag or assumed exact multiplier; reject zero/mismatched hits."
            ),
            "seed-collected": "Actual native Scrub Business Seed stock2->3; own world donor, not Magic Bean.",
            "seed-used": "Assign/use without buying: see the native effect; stock stays3, not2 (Kareem, rc.3).",
            "reload": "Save and Continue; every completed source and grant persists.",
            "adult-ready": "Native pedestal return to adult with the checkpoint's real Bow, no age/inventory cheat.",
            "ice-abandoned": "Kill night rooftop source, abandon pickup, leave/reload; source pair stays unset.",
            "ice-collected": "Recover/retrigger and Hookshot-retrieve Ice Arrows; native magic floor raw240.",
            "ice-used": "Adult with Bow: one visible Ice Arrow projectile/effect, Arrow25->24 and actual MP spend.",
            "used-reload": "Save and Continue; all7 assigned pairs persist, other93 source pairs unchanged; token18.",
        },
        "estimate": "17-19 minutes, not timed; stop at20 and retain partial evidence",
    }


def _plan_ocarina(baseline: save.Save, romfs: Path, dictionaries: zsdic.Dictionaries) -> tuple[dict, dict]:
    values = _baseline_fields(baseline)
    time, fairy, song = "Item_Ocarina_Time", "Item_Ocarina_Fairy", "Item_Melody_SunSong"
    required = {
        ("bool", AGE): True,
        _stock(time): 0,
        _got(time): False,
        _stock(fairy): 1,
        _got(fairy): True,
        _got(song): True,
    }
    read = {"int": baseline.int_value, "bool": baseline.flag}
    actual = {key: read[key[0]](key[1]) for key in required}
    if actual != required:
        raise PatchError(f"ocarina-time S1 preconditions: expected {required}, actual {actual}")
    # Fairy stock belongs to the baseline, not a prediction of native instrument replacement semantics.
    observed = {key: actual.pop(key) for key in (_stock(fairy), _got(fairy))}
    values.update(actual)
    phases = {"baseline": {"completed": [], "fields": _fields({**values, **observed})}}
    values.update({_stock(time): 1, _got(time): True})
    for phase in ("time-collected", "song-played", "reload"):
        phases[phase] = {"completed": [str(TREE)], "fields": _fields(values)}
    rows = {row["__RowId"]: row for row in read_romfs_byml(romfs, dictionaries, tokens.POUCH_ACTOR_INFO)}
    if rows.get("Obj_Ocarina_Time", {}).get("PouchSpecialDeal") != "Ocarina":
        raise PatchError(f"ocarina-time native row changed: {rows.get('Obj_Ocarina_Time')}")
    return phases, {
        "native_rows": {"Obj_Ocarina_Time": {"PouchSpecialDeal": "Ocarina"}},
        "baseline_only": [{"kind": key[0], "name": key[1]} for key in observed],
        "proof_obligations": {
            "time-collected": "Fresh S1: roll ranch tree, kill, collect new Ocarina of Time; no Boomerang bootstrap.",
            "song-played": (
                "Equip the new Time ocarina and play the already-known Sun's Song; native recognition/time change. "
                "No clock cheat during this proof. Ownership alone is not a playable-instrument proof."
            ),
            "reload": "Save and Continue: Time ocarina still owned, source pair committed, token9 unchanged.",
        },
        "estimate": "about3 minutes, not timed",
    }


def _grants(delivery: tokens.Delivery, manifest: Mapping, expected_grants: Mapping) -> dict:
    """Each built pickup's effective pouch grant, refused unless it is the identity or bundle the phases expect."""
    facts = manifest["native_rows"]
    packs = {path: file.data for path, file in delivery.new_files.items()}
    found, wrong = {}, {}
    for item, (key, expected) in expected_grants.items():
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
        raise PatchError(f"family packet built pickups grant otherwise: {wrong}")
    return {"built_grants": found}


def _grants_2(delivery: tokens.Delivery, manifest: Mapping) -> dict:
    return _grants(delivery, manifest, GRANTS_2)


@dataclass(frozen=True)
class Packet:
    sha256: str
    assignments: tuple[tuple[int, str, str, str], ...]  # source, name, actor, family
    manifest: str  # the checker manifest's file name in the output folder
    kind: str
    plan: Callable[[save.Save, Path, zsdic.Dictionaries], tuple[dict, dict]]  # phases, further manifest keys
    built: Callable[[tokens.Delivery, Mapping], dict]  # further manifest keys from the built pickups
    adult_sources: tuple[int, ...] = ()


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
    3: Packet(
        AFTER_FOREST_SHA256,
        ASSIGNMENTS_3,
        "token-families-3.json",
        "forced families-3 diagnostic; not a randomized or beatable seed",
        _plan_3,
        lambda delivery, manifest: _grants(delivery, manifest, GRANTS_3),
        (IMPA,),
    ),
    4: Packet(
        CHECKPOINT_SHA256,
        ((TREE, "LLR GS Tree", "Obj_Ocarina_Time", "ocarina"),),
        "token-ocarina-time.json",
        "forced Ocarina of Time first-grant diagnostic; not a randomized seed",
        _plan_ocarina,
        lambda delivery, manifest: _grants(
            delivery, manifest, {"Obj_Ocarina_Time": ("PouchActor", "Item_Ocarina_Time")}
        ),
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
        "implementation_sha256": implementation_sha256(),
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
        age = "adult" if source in spec.adult_sources else "child"
        if location.ages not in (age, "both"):
            raise PatchError(f"{label} {age} source {name}: {location}")
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
