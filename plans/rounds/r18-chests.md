# Round 18 — Track D: chests and reward follow-up (cs18d)

Agent: `openai-codex/gpt-6.1-sol`; branch `r18/chests`; initial main `2ba2f9a`.

## Scope and safety

Merge delivery: admit the nine played chest-hunt routes, finish round-17 generation attribution,
and research shooting-gallery expert prizes without building them. A separate on-top delivery
handles issue #11 and remains **READY (play-held)** until Kareem plays its candidate and main control.
No fill change, new option, version bump, runtime launch, merge or push by this track.

Dump is read-only. Scripts, decoded facts and generated diagnostic output live under
`E:/OOTRemake/work/r18-chests/`; no played seed or original save is opened or changed.
Heavy work serializes under `E:/OOTRemake/work/rounds/r18/gate.lock`, owned lock only.

## Played chest admissions

Evidence: Kareem's finished-save observations, forwarded by Claude in
`E:/OOTRemake/work/r17-chests/CHEST-HUNT-ANSWERS-2.md` (2026-11-18), and the round-17
canonical-pair ruling in `r17-chests-tokens.md`. Nine spots add **ten** canonical checks:
the tent grotto contains two chests. Ordinary shuffled chests increase **168 → 178 of 184**.

| Spot / check | Admitted route, in addition to the region's existing access |
|---|---|
| 3 South Field grove | Adult; open air; no Poe kill, note or tool |
| 4 North Field tree | Adult; open air; no Poe kill, note or tool |
| 5 Lake southwest shore | Adult and `Water Temple Clear`; no Poe kill |
| 6 Lake island grave grotto | Existing fishing-island access, push gravestone; usable Din's Fire plus child Sticks or adult Bow; alternatively usable adult Fire Arrows |
| 8 Valley tent red / green | Existing adult Song of Storms entrance; no Lens; adult red is canonical |
| 9 Valley underwater seed | Existing Silver Gauntlets boulder entrance plus usable Iron Boots; ignore Octoroks |
| 10 Fortress underground | Adult with existing fortress-grounds access; curtained door, left to uncovered hole; no added Card, Storms or attack requirement |
| 11 Fountain masonry | Existing `can_use(Scarecrow)`: adult, Hookshot, song and age-usable Ocarina |
| 12 Well room 11 seed | Child, playable Lullaby for the hall, usable Lens for the hidden hole |

**Policy attribution:** rules follow Kareem's answers. Claude requires Lens at the Well despite
Kareem's successful blind jump; no trick option is added. Fortress grounds retain the existing
access rule, as directed. Adult Desert Colossus reverse walking belongs to Track A, not this patch.

### Native-data checks

`uv run python E:/OOTRemake/work/r18-chests/check_routes.py` completed read-only in 6.23 s.
External evidence: `route-data.json`, `gravestone-graphs.json`; earlier source trace:
`E:/OOTRemake/work/r17-chests/spawn-report.md` sections 3–6 and 8–12.

- All three Field/Lake red chests exist **only** in `HyruleField_Adult_Dynamic`. The full lake
  also exists as child, but **this shore chest does not**: the child layer has pots there.
  Therefore no child admission or spawn edit. Thread post records this intersection of played
  access and native presence rather than silently treating lake-full as chest-present.
- Lake full uses the existing `'Water Temple Clear'` event (`water_temple.toml`, Morpha completion),
  not ownership of the Water Medallion. Island grotto no longer inherits N64's free entrance;
  its override reuses the existing `LH Fishing Island` route including child bean history.
  Both ages place the pushable `Obj_Tombstone_A_03` over the hole; no extra opener is required.
- Four candles are ANDed by `HidingHole_Level_Hole_30_Prefab_9583` node 4; each native
  `ExtinguishTime=15`, `FireWeakTime=5` (seconds), initially unlit. The fourth is behind the entrance.
  The accepted fire combinations are Kareem's played answer, not a radius/timer inference.
  `can_use` keeps Din's/Fire Arrow magic and age/weapon requirements.
- Valley underwater Hash `6463521162691873710` is at y=-22.60 in the water-plane grotto;
  the entrance rock is `Obj_LiftRock_B_01`, Silver Gauntlets. Existing entry is from `GV Grotto Ledge`.
- Fortress entrance is native room-02 `HidingHole_Entry_01`, at (34.5,113.5,-65.4), among
  curtained/interior props; Kareem identified its grounds doorway. No new guard/card policy.
- The Well chest remains in Main Area but also asks Lullaby, matching the existing hall's
  underwater/Lens chest routes. No small key, Dead Hand kill or speculative combat requirement.
- Adult red Valley Hash `18413589940135955604` is canonical; child Hash `6205043616869463865`
  stays `False`/vanilla. The green chest and both-age island chest each have one shared Hash.
  KF inaccessible copy, normal/missable windmill, Goron failure and Dampé repeats remain held.
- All admitted placement resources already belong to the established layered working set;
  **no new fixture file** is required. Reuse `work/rounds/r16/time-layered-dump`.

### Focused proof and diagnosed failures

`CLAWSHOT_WORKERS=1 uv run pytest tests/test_world_chest_hunt.py
 tests/test_world_data.py::test_all_other_vanilla_checks_with_keys_and_an_escape_tool -q --tb=short`:
**68 passed in 34.98 s**. Every admitted chest has a route regression; pair pool membership is checked.
The vanilla oracle no longer exempts any newly admitted chest and still collects every chest.

Initial test-harness failures printed the missing-exits region dictionaries; some leaf regions omit
`exits`, so the isolating helper now reads an empty mapping there. Subsequent printed route states
showed an abstract one-tier Ocarina was not adult-usable, and the boulder exit's parent was
`GV Grotto Ledge`, not `Gerudo Valley`. Corrected test inventories/route roots, not production rules.
No failed test was weakened, reclassified or reseeded.

## Generation attribution

Two original 200-seed arms are being rerun from the exact preserved round-17 implementations,
not the new round-18 chest world: main `945c996` plus three chests only versus main plus gift holds
and normal-held staging only. Old 125-row evidence is preserved. No fill edit is authorized here.
Final raw rows, process snapshots, cause classification and comparison will be recorded before freeze.

## Shooting galleries — research only

Native expert/advanced mode and prize findings are being traced against the active game flows.
No expert check is released, no option is added, and both existing expert holds stay default-off.

## Acceptance and handoff

The supplied broad recipe uses `all_anywhere`, a reported broken path on initial main. Its sweep
must wait for Track C's merge rather than rerun that known failure unchanged. Then this track rebases
onto current main and runs 200 broad + 50 Defaults + 50 Recommended under the lock, zero exhausted,
followed by focused tests and one exact-head format/lint/full synthetic/full dump gate.
Authoritative commands, process snapshots and results will be external under `work/r18-chests/`.

## Issue #11 — separate play-held layer

Issue read and claimed by comment before edits. Existing world metadata already maps the native
forty-token source to `Bombchus (20)` and `Item_BombchuBundle_Large`, but explicitly holds it pending
controlled play. Implementation, regression coverage, second sweep and main control are on top of the
merge delivery only. Candidate/control are built, **not played**, until Kareem checks them on rc.7.
