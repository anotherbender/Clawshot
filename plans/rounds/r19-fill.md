# Round 19, Track fill — cs19b

Branch `r19/fill`, starting main `d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`.
Model: `openai-codex/gpt-6.1-sol`. Status: **NOT WORTH IT — rejected; do not merge this branch.**
External scripts and receipts: `E:/OOTRemake/work/r19-fill/`.
No game started, personal seed opened, save changed or game/runtime folder written.
No new game resources, pack inputs, options, location admissions or version change.

## Attribution and cause

Accepted historical attribution: `r18-chests.md:82–118` and external
`work/r18-chests/attribution/REPORT.md`. Its 200-seed isolated gift arm had
137 first failures, including 75 Bottle/Milk failures, versus 77 first failures
and no bottle errors for the chest-only arm. 61 of the 75 bottle failures had
zero empty reachable checks; this was not Token filler capacity. Those isolated
old-source numbers are not the round-19 combined-main baseline. The accepted
round-17 combined 500-seed residual was 27.8% first failures / 1.568 attempts.

The hold extension moved bottle progression from the constrained type-held stage
into shared progression, correctly retaining safe swaps with its openers. It
also lost the former most-constrained-first ordering. Shared progression took
seeded order (after native display preference): flexible items could consume the
last early gift/Skulltula and leave bottle-only routes inaccessible.

A fully synthetic eight-check witness prints the exact late cycle, not just a
candidate count. Both Bottle and Milk variants, seed 3, fail on baseline:

- The only immediately reachable check is Starter Gift. Flexible Fairy Ocarina
  consumes it; all remaining checks need the bottle, sword or Boomerang.
- Bottle can safely displace the ocarina there. Replacing the ocarina while the
  bottle is not assumed displaces the bottle again: the same two items cycle.
- The existing twice-per-displaced-name limit is exhausted. One allowed empty
  Skulltula remains, none reachable. `trace-regression.log` retains each swap,
  assumed inventory, placements and displacement counts for both bottle kinds.

This is a construction-order problem, not justification for more swaps/retries,
a bottle spelling exception, chest admission, or weaker reachability.

## Initial candidate (rejected in isolation)

Proposed by cs19b, following cs18d's accepted measurement proposal: within the
**same shared progression stage**, place non-Token item holds by increasing
number of currently empty compatible destinations (`allowed`, including screens
and source exclusions). Preserve the existing priority/native-display ordering
and stable seeded ties. Token items retain their seeded order; no token weight,
quota or early frozen cohort. Recompute capacity once per distinct held item at
stage entry, not once per copy/search. Displaced items still go next through the
existing safe swap; the swap bound and ten fill attempts are unchanged.

Round-18 stage composition is retained: own-dungeon/return-kit stages, native
palettes including DungeonReward and the released Well/Fortress source palettes,
ordinary type-held items, bag-gated ammo, then shared progression. Preparation's
composed restrictions are reused unchanged; no second hold derivation is added.
A separate matched integration cohort explicitly enables reward shuffle,
Fortress keys, all-anywhere, closed owned-Stones Door and nine-reward bridge.

Regressions in `tests/test_fill_holds.py` exercise both bottle kinds through
`generate(..., attempts=1)`, exact item stock, unchanged destination checks and
independent goal search. Baseline ablation fails both with printed state above.
Existing mixed sword/Token shared-stage, native-display/bootstrap, reward
palette and key-family tests remain in the focused run.

## Measurements and checks

Final matched results and the stop decision are below. The counting recipes are the exact round-18 broad CS1
(`work/r18-fill/settings.txt`), Defaults and Recommended; seed numbers 0–199,
0–49 and 0–49 respectively, identical in both arms. Baseline is main's frozen
`fill.py` (`baseline_fill.py`) loaded against identical captured production
inputs. Native preparation is captured through `patch.make_seed`, before any
output writing, including real census/actor contents and gift restrictions.
Every generation runs ordinary beatability and exact normalized shuffled-stock
assertions. No preliminary failed probe is counted twice; production attempts
are observed directly. Each row records all FillError payloads and item counts
per destination type, allowing item-share changes to be reported.

All completed sweeps serialized under the round-19 gate lock; process snapshots
and workers are recorded per recipe. No full gate or READY is claimed.

## Acceptance boundary

This track changes fill construction only, not native behavior, logic or grant
eligibility. No new play packet is required for merge; existing built-not-played
feature labels remain. Automated beatability is a model proof, not a claim that
Kareem played these generated seeds. No product restriction was removed.

## Rejected ordering-only measurement

Implementation `09361fd492` is **not READY**. The mandatory matched sweep
completed, zero exhausted in either arm, but ordering alone worsened broad:
5/200 → 16/200 first failures (2.5% → 8.0%), mean 1.035 → 1.100, max 3 → 4.
Defaults remained 0/50, mean/max 1; Recommended remained 2/50, mean 1.04/max 2.
The extra integrated 24 improved 4 → 3 first failures, mean 1.2083 → 1.125.
No result is hidden or substituted for the acceptance cohort.

Printed new broad causes: eight Token progression errors, one Fire small-key
error, seven late filler failures including a map/compass. `native-5.log`
also prints the already-placed, uncollected progressive copies: every weapon,
bag, scale and wallet copy was committed in the earlier type-held stage,
outside shared swaps. Reordering gifts alone cannot relocate those assumed
openers. This evidence motivates revising stage membership, not retry bounds.

The initial combined focus was interrupted by its accidentally retained
300-second tool deadline after the printed 83% milestone, with no assertion failure.
The two new regressions separately passed (2 passed, 1.92 seconds). A concurrent
load snapshot reported 100% CPU. The final focus will have no supervisor
deadline and will run after the sweep, before the full-gate lock.

## Revised stage composition and safe-swap choice

The historical stress cohort uses current main, Recommended plus Token and small
keys anywhere, seeds 0–124 in each arm. Baseline: 45 first failures / 1.624 mean /
5 max, including 28 Bottle and 10 Milk first errors. Ordering-only: 25 first
failures / 1.240 mean / 4 max, including five Bottle and five Milk errors.
Neither exhausted. This confirms the bottle improvement without disguising the
mandatory broad regression. Immutable copies are `ordering-only-*` and
`ordering-stress-*`; new measurements must not overwrite the negative evidence.

The revised construction keeps Chest-held progression (notably native progressive
copies) in the same shared stage as Token-held gifts **when Token is shuffled**.
Normal holds, songs, shop refills, bag-gated ammo, own-dungeon/return-kit stages,
and all early location palettes retain their stages and restrictions.
No preparation policy changes are needed: `prepare` already composes reward,
token, progressive and key-family restrictions correctly.

A second synthetic four-check witness proves the frozen-opener cause: Tool is
Chest-only, Bottle is Token-only, the only GS needs Tool, and the second chest
needs Bottle. Freezing Tool in that second chest strands Bottle even though a
valid placement has Tool in the starter chest. Six seeded cases retain the full
goal and unique valid assignment, not a source-text/wiring assertion.

Sharing the stage alone printed a second cause in three cases: Tool had no
compatible empty destination (the free check was an NPC); swaps cycled Tool
and Token rather than moving flexible Boomerang from a chest to that NPC.
Safe swaps now prefer a displacement with a **proved immediately reachable empty
compatible destination after the current item is placed**, otherwise preserving
the original first-safe fallback. The proof never assumes the displaced copy;
the old twice-per-name bound, stage-local scope and no-RNG fallback remain.
Temporary placements are restored in `finally`. Every caller passes its actual
empty-stage destinations; source exclusions still use unchanged `allowed`.

Aimed verification: 12 passed in 1.34 seconds (eight new bottle/opener cases,
old mixed sword/Token, two House100 exclusions, unsupported progressive source).
The formerly failed broad seed 5 now fills first attempt and independently wins
in 20 spheres / 1333 total placements (`aimed-native-5.log`). This is an aimed
native-model rerun after the printed cause, not a played claim or full sweep.
The next mandatory sweep attempt found cs19d's owned gate lock and exited 75;
it started no generation and touched no other agent's lock.

Revised integrated focus (no tool deadline, `CLAWSHOT_WORKERS=1`):
`pytest tests/test_fill_holds.py tests/test_generate_tokens.py tests/test_gifts_fill.py
tests/test_fill.py tests/test_age_fill.py tests/test_dungeon_rewards.py
tests/test_key_families.py tests/test_house100.py tests/test_progressive_logic.py -q`
→ **246 passed, 3 dump tests skipped, 42.26 seconds**. No native failure was
labelled fixture-only; the full real-dump gate remains required.

## Completing the shared-capacity invariant

The second measured construction (`81f03ed702`) reduced historical stress to
9/125 first failures (7.2%), mean 1.080 / max 3, including only one Bottle and
two Milk first errors; zero exhausted. Its mandatory broad still regressed:
13/200 first failures, mean 1.075 / max 3 (seven map/compass filler failures,
three Token, one Fire key, one Strength and one Slingshot). Integration was
5/24, mean 1.250 / max 3; presets unchanged. It is also **rejected**, not READY.
`stage-only-*` preserves those rows before the next candidate.

The remaining capacity bug is concrete: late normal/priority maps and compasses
cannot use spare NPC gifts once progression has consumed their chests. The
round-18 filler ordering repair places priority before other filler, but cannot
recover a chest already consumed in the preceding progression stage. A synthetic
four-check all-anywhere world prints this exact Map failure in eight of twelve
seeds (`priority-capacity-before.log`), with no gate or game file involved.
Released keys likewise have implicit chest restrictions, not necessarily an
`item_location_types` entry; counting explicit holds alone misses them.

The complete candidate therefore counts **actual `allowed` capacity for every
distinct non-Token shared item**, including implicit dungeon/source constraints,
and includes priority items in the shared stage when Token is shuffled. Existing
priority-before-progression ordering protects their slots; safe swaps can still
move them if a key or opener needs an earlier chest. Their item classification,
pool count, native grant and `allowed` destinations do not change. Ordinary
normal filler remains unassumed. No extra retry or reserved Token quota is added.

Complete candidate `b41e88edf4` was rebased onto unchanged local main and reran
the integrated focused command above: **258 passed, 3 dump tests skipped,
58.61 seconds**. All twelve priority-capacity cases now pass. One incidental
starter-loot assertion was removed: the printed alternative Kokiri Sword
starter also opens the full required route; exact stock, eligibility, one
attempt and independent full-goal proof remain, rather than re-pinning the RNG.

The next serialized measurement attempt found cs19d's full-gate lock and did
not start generation. The agent now waits for the lock-directory deletion
event, then makes one atomic sweep acquisition attempt; it neither polls a
running suite nor deletes another owner's lock. No full gate has run here yet.

## Final matched result: NOT WORTH IT (2026-11-20)

Claude's morning cutoff supersedes the planned stress/full-gate work: stop if
this candidate does not clearly beat **current main**, with zero exhausted.
The stale lock-deletion watcher was cancelled. The morning sweep acquired its
own lock, completed normally in 483.36 seconds, and released that lock. All four
stage-start process snapshots reported no running game; workers were 12 only
while this agent held the lock. No focused tests ran outside that lock this morning.

Measured source head: `b41e88edf48913937fdb850cf8980f600202c9b6`.
Baseline remains main `d9deb65`'s frozen fill against identical captured native
inputs. Each arm uses the same numbered seeds, settings and normalized stock.

| Recipe | Seeds per arm | First failures: main → candidate | Mean attempts: main → candidate | Max attempts: main → candidate | Exhausted: main → candidate |
|---|---:|---|---:|---:|---:|
| Broad | 200 | 5 (2.5%) → 23 (11.5%) | 1.035 → 1.125 | 3 → 3 | 0 → 0 |
| Defaults | 50 | 0 (0%) → 0 (0%) | 1.000 → 1.000 | 1 → 1 | 0 → 0 |
| Recommended | 50 | 2 (4%) → 2 (4%) | 1.040 → 1.060 | 2 → 3 | 0 → 0 |
| Reward/key integration | 24 | 4 (16.67%) → 6 (25%) | 1.2083 → 1.4167 | 3 → 4 | 0 → 0 |

Broad pairing: four baseline first failures recovered, **22 newly first-failing
seeds**, one failing in both arms. Candidate first errors were 22 Gold
Skulltula Token and one Progressive Scale. Integration first errors were five
Token and one Slingshot. These printed production errors reject the candidate;
the old 27.8% residual is not the acceptance baseline. No further fix, stress
rerun or full gate was attempted after this result, per the explicit cutoff.

The construction also moves item shares; admission rules and item stock remain
unchanged. Selected broad Skulltula-destination shares (percentage of all such
checks, not percentage of an item's copies):

| Item | Main % | Candidate % | Change, percentage points |
|---|---:|---:|---:|
| Gold Skulltula Token | 44.165 | 46.900 | +2.735 |
| Bottle | 1.785 | 2.000 | +0.215 |
| Bottle with Milk | 0.590 | 0.630 | +0.040 |
| Piece of Heart | 8.205 | 9.375 | +1.170 |
| Rupees (20) | 6.830 | 4.850 | -1.980 |

Complete receipts under `E:/OOTRemake/work/r19-fill/`:

- `morning-candidate.log`, `candidate-rows.jsonl`, `candidate-summary.json`:
  all 324 candidate seeds, attempt payloads, exact-stock assertions and process snapshots.
- `baseline-rows.jsonl`, `baseline-summary.json`: matched current-main arm.
- `morning-comparison.log`, `comparison.json`: per-recipe metrics and seed pairing.
- `all-item-share-changes.csv`: all **625 changed item/destination share cells**;
  `token-share-changes.md`: every changed Skulltula share. Comparison excludes
  the older candidate's stress rows because their measured head does not match.
- `complete-focused.log`: 258 passed / 3 dump skips before measurement;
  `ruff format --diff src/clawshot/generate/fill.py tests/test_fill_holds.py`:
  both files already formatted.

**Handoff: NOT WORTH IT. Do not merge the implementation commits or claim READY.**
Keep main unchanged. Historical attribution and synthetic witnesses are retained
as rejected research, not a production improvement. No game was played, no
personal seed/save or game/runtime folder was touched, and no full-gate pass is
claimed. The gate is released; no watcher or heavy job remains from this track.
