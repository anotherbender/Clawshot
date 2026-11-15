"""Build the accepted forced token diagnostic, not a randomized or beatable seed.

This composes the independent pickup mechanism with existing chest/Gift writers.
It does not change fill or world logic and is independent of production settings.
"""

import argparse
import hashlib
import json
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from clawshot import save
from clawshot.census.definitions import load as load_definitions
from clawshot.census.gifts import scan_gifts
from clawshot.census.scan import GAME_DATA_LIST, read_romfs_byml, scan
from clawshot.formats import zsdic
from clawshot.patch import gifts, tokens
from clawshot.patch.events import REMOVE
from clawshot.patch.events import load as load_events
from clawshot.patch.plan import ChestChange, PatchError, Plan
from clawshot.patch.write import check_output_folder, check_romfs, write
from clawshot.token_packet import CHEST_HASH, CORE_SOURCES, HOUSE_FLAG

CHECKPOINT_SHA256 = "450eaf011b5654ce5f6e4a2bf7dc1d79feb68efaae5153203fb0339e11e4b8b7"
HOUSE_CHECK = "Kak 10 Gold Skulltula Reward"
HOUSE_ACTOR = "Item_Hammer"


def _source_records(romfs: Path, dictionaries: zsdic.Dictionaries, census) -> list[int]:
    sources = [location for location in census if location.kind == "gold_skulltula"]
    hashes = sorted(location.id for location in sources)
    copies = sum(len(location.files) for location in sources)
    if len(hashes) != 100 or len(set(hashes)) != 100 or copies != 114:
        raise PatchError(f"native Skulltula identities: {len(hashes)} sources, {copies} copies, hashes={hashes}")
    data = read_romfs_byml(romfs, dictionaries, GAME_DATA_LIST)["Data"]
    records = {int(row["Hash"]): row for row in data["Bool64bitKey"]}
    for source in hashes:
        for identity in (source, source ^ 2):
            row = records.get(identity)
            if row is None or (int(row["ResetTypeValue"]), int(row["SaveFileIndex"])) != (24, 0):
                raise PatchError(f"native source {source}, collection record {identity}: {row!r}")
    bools = {int(row["Hash"]): row for row in data["Bool"]}
    for name in (f"IsTreasureBoxOpen.{CHEST_HASH}", HOUSE_FLAG):
        row = bools.get(save.key(name))
        if row is None or int(row["SaveFileIndex"]) != 0:
            raise PatchError(f"native core completion record {name}: {row!r}")
    return hashes


def _chest(census) -> Plan:
    found = [location for location in census if location.id == CHEST_HASH]
    if len(found) != 1 or found[0].kind != "chest":
        raise PatchError(f"designated token chest {CHEST_HASH}: {found!r}")
    location = found[0]
    event = load_events().get(location.event)
    if location.event is not None and event is None:
        raise PatchError(f"token chest has an unknown native event: {location!r}")
    kept = event if event is not None and event.patch != REMOVE else None
    return Plan(
        [
            ChestChange(
                "KF Storms Grotto Chest",
                location.id,
                "KF Storms Grotto Chest",
                location.files,
                location.actor,
                "Gold Skulltula Token",
                location.vanilla_item,
                "Item_Token_Gold",
                event if kept is None else None,
                kept_event=kept,
            )
        ],
        [],
        [],
    )


def build(romfs: Path, checkpoint: Path, out: Path, *, revision: str) -> dict:
    """Build one immutable diagnostic mod plus a checker/changed-resource manifest."""
    check_romfs(romfs)
    check_output_folder(romfs, out)
    if not revision.strip():
        raise PatchError("the diagnostic requires an explicit source revision")
    checkpoint_bytes = checkpoint.read_bytes()
    digest = hashlib.sha256(checkpoint_bytes).hexdigest()
    if digest != CHECKPOINT_SHA256:
        raise PatchError(f"core checkpoint SHA256 {digest}, expected {CHECKPOINT_SHA256}: {checkpoint}")
    baseline = save.read(checkpoint_bytes)
    if baseline.save_type is None:
        raise PatchError("the core checkpoint has no Bool64bitKey section")
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    census = scan(romfs)
    source_hashes = _source_records(romfs, dictionaries, census)
    delivery = tokens.build(
        romfs,
        {CORE_SOURCES["tree"]: "Item_Boomerang", CORE_SOURCES["tower"]: "Obj_Shield_Hylian"},
        census,
        rewards={"Item_Boomerang": "fixed_major", "Obj_Shield_Hylian": "equipment"},
    )
    native_gifts = scan_gifts(romfs)
    house = gifts.plan({HOUSE_CHECK: HOUSE_ACTOR}, native_gifts, load_definitions(), gifts.load())
    house_files = {step.flow: step.file for change in house for step in change.steps}
    written = write(
        _chest(census),
        romfs,
        out,
        extra_changes=(
            delivery.changes,
            gifts.file_changes(house, house_files),
            gifts.skulltula_hint_changes(romfs, {HOUSE_CHECK: HOUSE_ACTOR}),
        ),
        new_files=delivery.new_files,
    )
    manifest = {
        "kind": "forced core diagnostic; not a randomized or beatable seed",
        "build": "e0f3ccfa",
        "accepted_facts_amendment": "9e5008e",
        "generator_version": version("clawshot"),
        "source_revision": revision,
        "implementation_sha256": {
            path.relative_to(Path(__file__).parent).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(__file__).parent.rglob("*.py"))
        },
        "seed": None,
        "settings": "accepted Phase 1 forced assignments; independent of production Token settings",
        "baseline_sha256": digest,
        "baseline_save": str(checkpoint.resolve()),
        "save_version": baseline.version,
        "save_type": baseline.save_type,
        "source_hashes": source_hashes,
        "house_actor": HOUSE_ACTOR,
        "assignments": {
            "LLR GS Tree": "Item_Boomerang",
            "LLR GS Tower": "Obj_Shield_Hylian",
            "HF GS Lone Tree": "native token, unchanged",
            "KF Storms Grotto Chest": "Item_Token_Gold",
            HOUSE_CHECK: HOUSE_ACTOR,
        },
        "written": [asdict(file) for file in written],
        "unplayed": True,
        "independent_gameplay_lead": "ootrr (REALAZK); no code copied",
    }
    (out / "token-packet.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
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
        parser.exit(2, f"token diagnostic: {error}\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
