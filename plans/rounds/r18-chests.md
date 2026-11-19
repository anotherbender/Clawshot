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

Completed **400/400 rows** (200 seeds per isolated arm), `CLAWSHOT_WORKERS=12`, no game
present at stage start. Owned lock: 18:16:29–18:34:56. Source is preserved main `945c996`
plus exact `55b1307` components, not the new round-18 world. All 125 old partial rows
reproduced exactly; original partial/baseline files remain unchanged.

**Gift holds raised first-attempt failures; chest admissions did not.** Matched seeds 0–124:

| Variant | First-attempt failures | Mean production attempts |
|---|---:|---:|
| Main `945c996` (preserved baseline) | 51/125 (40.8%) | 1.752 |
| Three chests only | 50/125 (40.0%) | 1.808 |
| Gift holds plus normal-held staging only | 86/125 (68.8%) | 2.992 |

Full 200-seed arms: chests **77** first failures, **zero** exhausted, mean **1.785** attempts;
gifts **137** first failures, **one** exhausted, mean **2.890**. Bottle/Milk account for
**75/137 (54.7%)** gift first errors, versus zero for chests/baseline. All first errors are
progression reachability failures, not Token filler capacity. The isolated arms are not additive:
the accepted combined round-17 head's preserved 125-seed baseline had 64 first failures and
zero exhausted. Its result must not be conflated with the isolated gift arm.

Only isolated gift seed50 exhausted: first Bottle, **81 allowed/123 left, 49 other items,
zero empty reachable**; attempt10 Bottle with Milk, **51 allowed/83 left, nine other items,
zero empty reachable**. Exact first/final and all ten error payloads are retained; no unchanged rerun.

**[INFERENCE; cs18d's proposal, not implemented]** Newly Token-held bottle progression loses
reachable compatible slots late in the shared stage. Because this family dominates, measure
most-constrained-first ordering for non-token held progression *within the existing shared,
swap-capable progression stage*, preserving native-display order and seeded ties. Do not freeze
it into an early batch (the existing mixed sword/Token regression forbids that), weaken holds,
weight Token share, increase retries or special-case Bottle. No fill change this round.

**Claude accepted the attribution on 2026-11-19 and deferred this ordering proposal to round 19.**
Round 19 should measure the proposal against the preserved identical cohorts and the combined
production recipes, retaining the mixed sword/Token regression. No ordering implementation,
new experiment, retry increase or fill-policy change belongs to this round.

Full method, paired comparisons, every error and source hashes:
`E:/OOTRemake/work/r18-chests/attribution/REPORT.md`;
immutable raw `attribution/raw/attribution-400.json` and `.rows.jsonl`.
This historical attribution is separate from the required round-18 acceptance sweep.

## Shooting galleries — research only

Both galleries have expert modes, but **neither has a native unique first-expert prize**.
Every perfect expert win pays direct wallet rupees: Market (child) **30**, Kakariko (adult) **70**,
including the first. No item actor, get-item scene or saved expert-win flag exists. Static data
research only; no new played result is claimed.

Native `Event/EventFlow/MiniGame_HitTarget.bfevfl.zs`: `RewardTalk` selects `Child_Reward` /
`Adult_Reward`. Normal first prizes use saved `HrlCity_Get_BulletBag` / `Kakariko_Get_Quiver`
flags and Medium/Large bag/quiver branches. After normal completion, `IsHardMode` routes
Event202 (30) / Event599 (70) through `GetRupy_HitTarget` to Event597's direct rupee increase.
Expert selection appears only after that gallery's normal prize; fees remain child10/adult30.
Market rents a Slingshot; adult Kakariko requires Bow. Galleries close 20:00–06:00.
`MiniGame_HitTarget_IsHardMode` is unsaved session state, not first-win persistence.

Clawshot's two first-expert locations are an **artificial once-only-check experiment**, with
new D22 saved flags and Rupees (20) pool contributions, already held by `keep_vanilla` under
every setting. Normal prizes stay shuffled and played; expert 30/70 payouts stay unchanged.
Existing round-10 held packet was not accepted for expert wins; no old packet is promoted.

**Claude accepted this research on 2026-11-18: no unique prizes; expert galleries stay off.**
No expert code is built, released or removed this round; no future release is promised in user docs.
Detailed native nodes, census/patch/hold references and packet caveats:
`E:/OOTRemake/work/r18-chests/gallery/REPORT.md` (read-only probe scripts beside it).

## Acceptance and handoff

Claude's revised sequence (2026-11-19): wait for cs18a's explicit **`A FROZEN <head>`**,
then rebase this merge-only head (played chest admissions and attribution/research docs,
**without issue #11**) onto that frozen A head. Rerun focused A/D tests before taking the lock.
Under `gate.lock`, run **200 broad + 50 Defaults + 50 Recommended**, zero exhausted,
covering the combined **A+D** stack, then **one** exact-stack-head format/lint/full
synthetic/full dump gate. Post **READY (merge)** with that stack head only after all pass.
Issue #11 follows on top as a separate **READY (play-held)** head.

The old C-on-main automatic runner `bg_8` was cancelled before any rebase, generation,
sweep or gate acquisition; it must not race the new stack sequence. Attribution was its
only predecessor heavy run. No replacement automatic main-triggered runner is active.
Authoritative commands, process snapshots and results will be external under `work/r18-chests/`.

## Issue #11 — separate play-held layer

Issue read and claimed by comment before edits. Existing world metadata already maps the native
forty-token source to `Bombchus (20)` and `Item_BombchuBundle_Large`, but explicitly holds it pending
controlled play. Implementation, regression coverage, second sweep and main control are on top of the
merge delivery only. Any built candidate/control remains **not played** until Kareem checks it on rc.7.

### Authorized diagnostic fixture preparation

Claude explicitly authorized scanning `work/save-backups` read-only, then a token-count-only
test-copy edit if no natural ≥40/unclaimed source exists (2026-11-18, current conversation).
`scan_reward40_saves.py`: **2487** progress files read, **2385** unclaimed40, **zero** natural
≥40/unclaimed40 matches. No placement/spoiler files were opened.

Chosen natural backup: `work/save-backups/2026-11-09_1022-main-adult-first/save/`
`5a3c9e1f0b7d24680000000000000001/slot_01` (adult just after first sword pull).
It has 15 tokens, Hammer unowned, and the native 10/20/30/40 reward flags unset.
Copied only that slot plus account/options to `work/r18-chests/reward40-fixture`.
The original progress file is additionally backed up in the fixture as
`progress.sav.before-token-edit`.

The **only** changed value is Int section2, `PouchData.Item_Token_Gold.StockNum`,
key **0x04735978**, **15 → 40**, value offset **89588**. Exactly byte89588 differs;
all other bytes, caption files and original source remain identical. Native threshold40 and
every completion/ownership/story field are untouched. Proof: `prepare_fixture.py` output and
`reward40-fixture.json`. This is declared diagnostic inventory setup, not a naturally earned
forty-token playthrough. Candidate and main control will each start from identical isolated copies.
The corrected nested-rc.7 launcher template was re-read after Claude's fix.
