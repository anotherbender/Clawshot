"""Build the approved three-route diagnostic from the untouched after-Forest slot04.

No route is admitted by this builder. Native age transitions and the child's real wall kill
remain gameplay obligations; no flag, age, inventory or source lifecycle is patched.
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
from clawshot.token_family_packet import check_packet, parse_manifest
from clawshot.token_packet import census_sources

CHECKPOINT_SHA256 = "e36c32a6156c07f9f4b1d8c3f5ea12a101984e16e51b05744712df36b5ce6bd3"
LONE = 2177746409373494991
TOWER = 2730878115209290675
WETLAND = 9047381233010434881
CHILD_KILL = "HaveReadHrlField_Note12_Enemy"
AGE = "Sequence_IsChildhood"
ASSIGNMENTS = (
    (LONE, "HF GS Lone Tree", "Item_Token_Gold", "token"),
    (TOWER, "LLR GS Tower", "Obj_Shield_Hylian", "equipment"),
    (WETLAND, "HF GS Wetland Grotto Crate", "Item_Token_Gold", "token"),
)


def build(romfs: Path, checkpoint: Path, out: Path, *, revision: str) -> dict:
    """Build real source selectors, preserving native crates, bindings and child flag flow."""
    check_romfs(romfs)
    check_output_folder(romfs, out)
    if not revision.strip():
        raise PatchError("the route diagnostic requires an explicit source revision")
    original = checkpoint.read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest != CHECKPOINT_SHA256:
        raise PatchError(f"route checkpoint SHA256 {digest}, expected {CHECKPOINT_SHA256}")
    baseline = save.read(original)
    fields = []
    for name, kind, expected in (
        (AGE, "bool", False),
        (CHILD_KILL, "bool", False),
        ("Step_SageOfForest", "enum", save.key("Complete")),
        ("Step_DoorOfTime", "enum", save.key("Complete")),
    ):
        read = baseline.flag if kind == "bool" else baseline.enum_value
        actual = read(name)
        if actual != expected:
            raise PatchError(f"route {kind} {name}: actual {actual!r}, expected {expected!r}")
        fields.append({"name": name, "kind": kind, "value": expected})
    for actor in ("Item_Boomerang", "Item_Hookshot", "Item_BombBag_Small", "Item_Gauntlet_Goron"):
        if baseline.flag("IsGet." + actor) is not True:
            # Native child strength is explicitly associated with the canonical actor.
            canonical = "Armor_Child_Gauntlet_Goron" if actor == "Item_Gauntlet_Goron" else actor
            if baseline.flag("IsGet." + canonical) is not True:
                raise PatchError(f"route inventory {actor}: no native acquired record")
    bombs = baseline.int_value("PouchData.Item_Bomb.StockNum")
    if bombs is None or bombs < 2:
        raise PatchError(f"route needs usable native bombs for both ages: stock {bombs!r}")
    shield_stock = baseline.int_value("PouchData.Weapon_Shield_Hylian.StockNum")
    shield_get = baseline.flag("IsGet.Weapon_Shield_Hylian")
    if shield_stock is None or shield_get is None:
        raise PatchError(f"route baseline shield records missing: {shield_stock!r}, {shield_get!r}")
    inventory_fields = [
        {"name": "PouchData.Weapon_Shield_Hylian.StockNum", "kind": "int", "value": shield_stock},
        {"name": "IsGet.Weapon_Shield_Hylian", "kind": "bool", "value": shield_get},
    ]
    # This approved profile already has a Hylian Shield. The native repeated/full-pouch
    # interaction must still complete this source, not manufacture a second shield.
    if shield_stock != 1 or shield_get is not True:
        raise PatchError(f"route needs its documented owned-shield state: {shield_stock!r}, {shield_get!r}")
    census = scan(romfs)
    source_hashes = census_sources(census)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    tokens.check_save_rows(read_romfs_byml(romfs, dictionaries, GAME_DATA_LIST), source_hashes)
    phases = {}

    def phase(name: str, *, child: bool, wall: bool, completed: tuple[int, ...]) -> None:
        named = [
            {
                **field,
                "value": child if field["name"] == AGE else wall if field["name"] == CHILD_KILL else field["value"],
            }
            for field in fields
        ]
        phases[name] = {"completed": [str(source) for source in completed], "fields": [*named, *inventory_fields]}

    phase("baseline", child=False, wall=False, completed=())
    phase("adult-before-child", child=False, wall=False, completed=())
    phase("child-ready", child=True, wall=False, completed=())
    phase("child-wall-killed", child=True, wall=True, completed=())
    phase("tower-abandoned", child=True, wall=True, completed=())
    phase("lone-collected", child=True, wall=True, completed=(LONE,))
    phase("adult-ready", child=False, wall=True, completed=(LONE,))
    phase("tower-collected", child=False, wall=True, completed=(LONE, TOWER))
    phase("wetland-abandoned", child=False, wall=True, completed=(LONE, TOWER))
    phase("wetland-reloaded", child=False, wall=True, completed=(LONE, TOWER))
    phase("wetland-collected", child=False, wall=True, completed=(LONE, TOWER, WETLAND))
    phase("reload", child=False, wall=True, completed=(LONE, TOWER, WETLAND))
    phase("child-revisit", child=True, wall=True, completed=(LONE, TOWER, WETLAND))
    manifest = {
        "kind": "forced three-route diagnostic; not a randomized or beatable seed",
        "build": "e0f3ccfa",
        "baseline_sha256": digest,
        "baseline_save": str(checkpoint.resolve()),
        "save_version": baseline.version,
        "save_type": baseline.save_type,
        "source_hashes": list(source_hashes),
        "assignments": [
            {"id": str(source), "name": name, "actor": actor, "family": family}
            for source, name, actor, family in ASSIGNMENTS
        ],
        "phases": phases,
        "generator_version": version("clawshot"),
        "source_revision": revision,
        "implementation_sha256": {
            path.relative_to(Path(__file__).parent).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(__file__).parent.rglob("*.py"))
        },
        "seed": None,
        "settings": "approved forced routes; native flag/age/appearance/crate logic untouched",
        "unplayed": True,
        "debug_policy": (
            "Map Teleport, clock, movement/access Noclip only; no inventory, flag or age cheats; route actions native"
        ),
    }
    preflight = check_packet(parse_manifest(manifest), original, original, "baseline")
    if preflight["verdict"] != "pass":
        raise PatchError(f"route baseline checker: {json.dumps(preflight)}")
    delivery = tokens.build(
        romfs,
        {source: actor for source, _, actor, _ in ASSIGNMENTS},
        census,
        rewards={actor: family for _, _, actor, family in ASSIGNMENTS},
    )
    written = write(Plan([], [], []), romfs, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)
    manifest["written"] = [asdict(file) for file in written]
    manifest["required_pickup_loads"] = [tokens.pack_path(name) for name in sorted(delivery.pickups.values())]
    (out / "token-routes.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
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
        parser.exit(2, f"token route diagnostic: {error}\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
