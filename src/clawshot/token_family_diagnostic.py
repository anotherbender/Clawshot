"""Build the approved first reward-family packet, not a randomized seed or admission proof.

The historical ranch checkpoint is copied by the external isolated launcher, never edited.
Six unplayed representatives plus the played Boomerang bootstrap occupy seven accessible
sources. Production admission is independent: this declares its diagnostic actors explicitly.
"""

import argparse
import hashlib
import json
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from clawshot import save
from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import zsdic
from clawshot.patch import tokens
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import check_output_folder, check_romfs, write
from clawshot.token_diagnostic import CHECKPOINT_SHA256
from clawshot.token_family_packet import check_packet, parse_manifest
from clawshot.token_packet import census_sources

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


def build(romfs: Path, checkpoint: Path, out: Path, *, revision: str) -> dict:
    """Validate the historical baseline before writing real native resources and checker metadata."""
    check_romfs(romfs)
    check_output_folder(romfs, out)
    if not revision.strip():
        raise PatchError("the families diagnostic requires an explicit source revision")
    original = checkpoint.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != CHECKPOINT_SHA256:
        raise PatchError(f"families-1 checkpoint SHA256 {digest}, expected {CHECKPOINT_SHA256}")
    baseline = save.read(original)
    initial = _baseline_fields(baseline)
    census = scan(romfs)
    sources = census_sources(census)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    tokens.check_save_rows(read_romfs_byml(romfs, dictionaries, GAME_DATA_LIST), sources)
    manifest = {
        "kind": "forced families-1 diagnostic; not a randomized or beatable seed",
        "build": "e0f3ccfa",
        "baseline_sha256": digest,
        "baseline_save": str(checkpoint.resolve()),
        "save_version": baseline.version,
        "save_type": baseline.save_type,
        "source_hashes": list(sources),
        "assignments": [
            {"id": str(source), "name": name, "actor": actor, "family": family}
            for source, name, actor, family, _ in ASSIGNMENTS
        ],
        "phases": _phases(initial),
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
            "Map Teleport, clock, movement/access Noclip only; "
            "no inventory, flag or age cheats; no logic-route claim"
        ),
    }
    preflight = check_packet(parse_manifest(manifest), original, original, "baseline")
    if preflight["verdict"] != "pass":
        raise PatchError(f"families-1 baseline checker: {json.dumps(preflight)}")
    by_source = {location.id: location for location in census}
    for source, name, _, _, _ in ASSIGNMENTS:
        location = by_source[source]
        if location.ages not in ("child", "both"):
            raise PatchError(f"families-1 child source {name}: {location}")
    delivery = tokens.build(
        romfs,
        {source: actor for source, _, actor, _, _ in ASSIGNMENTS},
        census,
        rewards={actor: family for _, _, actor, family, _ in ASSIGNMENTS},
    )
    written = write(Plan([], [], []), romfs, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)
    manifest["written"] = [asdict(file) for file in written]
    manifest["required_pickup_loads"] = [tokens.pack_path(name) for name in sorted(delivery.pickups.values())]
    (out / "token-families.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--romfs", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    try:
        manifest = build(args.romfs, args.checkpoint, args.out, revision=args.revision)
    except (OSError, ValueError) as error:
        parser.exit(2, f"token families diagnostic: {error}\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
