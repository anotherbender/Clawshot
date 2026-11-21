# Round 20, Track fill — cs20g

Branch `r20/fill`, starting main `acbb903df111bb30609baedac35316b22d43700e`.
Model: `openai-codex/gpt-6.1-sol`. Status: **RESEARCH HANDOFF — rejected; no product changes retained**.
External scripts and receipts: `E:/OOTRemake/work/r20-fill/`.

## Scope and acceptance

Attribute current-main first-attempt failures on broad seeds 0–199 before choosing one
construction change. Round 19's rejected 5 → 23 broad regression is not an accepted
implementation or a baseline to improve upon. Keep all destination, logic, pool and retry
contracts unchanged. Accept only fewer first-attempt failures, zero exhausted seeds and
no rise in median generation time in a matched comparison. Otherwise retain a research
handoff, not the candidate. Any retained fill change additionally needs 200 broad seeds,
50 Defaults and 50 Recommended and the complete round-20 gates on the exact merge head.

No game started, personal seeds opened, saves edited or game/runtime folder written.
This generator-only track does not certify in-game behavior or require a play packet.

## Measurement method

`sweep.py attribution` captures fresh production preparation through `patch.make_seed`
before output writing, including native census contents and gift restrictions. It reuses
only the external capture helper from round 18, not round 19's cached inputs or candidate.
The broad recipe is the exact CS1 in `work/r18-fill/settings.txt`; seeds 0–199.
Production `generate` retains its ordinary ten-attempt bound and final goal/softlock proof.
Every completed seed also checks exact normalized shuffled-item stock.

Errors are observed directly during production attempts, not by a preliminary failing
probe. Each failed restrictive stage prints its item, compatible empty checks, reachable
empty frontier, stage placements, displacement counts and uncollected earlier-stage
progression. The elapsed generation interval includes ordinary preparation, fill, final
proof and hints, excluding the separate stock assertion. Diagnostics run only on errors;
median successful-first-attempt timings do not pay their cost.

All sweeps hold the atomic round-20 gate lock with agent/branch/head recorded and use
`CLAWSHOT_WORKERS=6`; each stage snapshots exact game image names and refuses to start
if Hookshot or Longshot is running. The lock is released in `finally` by its own creator.

## Exclude coordination

cs20g proposed, Claude approved: attach non-progression-only exclusion constraints in
preparation before fill; enforce them in `allowed()` immediately after explicit
`Location.excluded_items`. The return kit, all restrictive stages, palettes, swaps and
filler inherit that predicate. No separate exclusion pre-commit stage is needed.
cs20b owns the narrow exclusion change; additive Settings fields are shared by owner.
An exclusion capacity check must account for holds/palettes and refuse clearly.
Attribution initially changes no product code and instruments stages only externally.

## Results

The locked current-main attribution completed successfully in 493.96 seconds:
**9/200 first failures (4.5%), zero exhausted**, rather than the historical 5/200.
Fresh inputs include round 19's accepted scene/logic changes; the historical cohort
cannot stand in for this current-main measurement.

| Stage | First blocked item | Seeds | Count |
|---|---|---|---:|
| Shared progression | Gold Skulltula Token | 88, 113, 165, 188 | 4 |
| Shared progression | Fairy Ocarina | 140 | 1 |
| Late filler (unlabelled FillError) | Maps/compasses among unplaced items | 5, 8, 180, 181 | 4 |

All five progression errors have reachable empty checks, but none can deliver the
blocked item: Token errors have 6–16 reachable NPC/song/scrub checks; Fairy Ocarina
has four. The twenty progressive copies remain committed in the earlier type-held
stage; 18–20 are uncollected at those frontiers. This is not evidence to widen delivery
eligibility or raise retry/swap bounds. Aimed diagnostics additionally print actual
filler destinations/capacity and reachable occupied checks; they are separate from
the counted production cohort. Full raw payloads: `attribution-rows.jsonl`;
grouping: `attribution-grouping.json`; process/worker receipt:
`attribution-summary.json`. Grouping posted on `cs-r20`.

| Seed | Compatible empty checks (all unreachable) | Reachable empty checks (all incompatible) | Frozen copies uncollected |
|---|---:|---:|---:|
| 88 | 74 | 7 | 20 |
| 113 | 96 | 7 | 18 |
| 140 | 43 | 4 | 20 |
| 165 | 76 | 6 | 20 |
| 188 | 71 | 16 | 18 |

Location attribution: the first three Token frontiers are early NPC gifts, fishing,
Saria and gallery checks; seed 113 also leaves the Near Bridge scrub and 10/20/30
House rewards. Seed 188 additionally leaves several songs, frogs, adult fishing and
digging. The Fairy Ocarina frontier is exactly KF Shopkeeper Gift, Kak 10 Gold
Skulltula Reward, Kak Anju as Child and Kak Man on Roof. Every per-seed location
name and its grouping frequency is in `attribution-grouping.json`.

Late-filler attribution: seed 5 strands the Dodongo map; seed 8 strands Fire/
Shadow/Water compasses and Well/Jabu/Water maps; seed 180 strands the Fire map;
seed 181 strands Fire/Forest compasses. Seeds 5/8/180 leave no chest at all.
Seed 181's sole remaining chest is `Hyrule Field Chest (Obj_Heart_Piece)`, whose
prepared explicit exclusions include every map/compass; it is not spare capacity.
There are respectively 36/43/43/41 other remaining non-chest destinations.
Thus these four failures lose eligible chest capacity to prior stages, rather
than merely choosing the wrong late-filler order. The diagnostic's
`remaining_priority` field is the original filler cohort; actual unplaced items
are parsed from the original FillError in the grouping report.

## Single targeted candidate

Proposed by cs20g after attribution: released **non-progression dungeon items**
(maps/compasses) enter the existing constrained type-held stage. Own-dungeon items
already leave the pool earlier; released progression keys remain in shared
progression. No progressive-copy stage move, shared-progression priority cohort,
destination widening, swap rewrite or retry-bound change from round 19 is reused.
The purpose is to preserve chest capacity before flexible progression consumes it.

Aimed trace confirms the four filler failures are exhausted eligible destinations,
not failure of the Token augmenting matcher: their remaining checks are NPC/song/
scrub/cutscene checks (one seed also has a chest ineligible for the blocked item).
Their unplaced priority items include, respectively, Map (Dodongos Cavern),
Map (Water Temple), Map (Fire Temple), Compass (Forest Temple). Full allowed-location
and occupied-frontier payloads: `trace-failures.jsonl`.

The paired harness alternates main-first on even seeds and candidate-first on odd
seeds, in the same worker and using identical fresh captured production inputs.
Both arms retain full generation and stock checks. Main's fill implementation is
frozen from `acbb903`; the acceptance cohorts remain broad 0–199, Defaults 0–49,
Recommended 0–49. This balanced ordering reduces timing drift relative to measuring
one whole arm before the other; no statistical significance claim is implied.

Candidate commit: `d689a55dc81a8966ed89aecac7d2da6b16a57343` (not READY).
The synthetic four-check map-capacity witness fails on frozen main with
`items left unplaced: ['Map (Temple)']`; the candidate fills it in one attempt
with exact stock and the full two-tool goal. No native failure was called fixture-only.

Focused command (game image check found neither runtime; `CLAWSHOT_WORKERS=1`):
`uv run --with pytest-xdist pytest -n 2 tests/test_fill.py tests/test_generate_tokens.py
tests/test_key_families.py tests/test_dungeon_rewards.py -q`
→ **163 passed, 1 skipped, 29.84 seconds**. The skip is dump coverage, not a pass.
The balanced paired measurement completed; the final rejection is below. No full gate ran.

## Final paired result: reject the candidate

Measured candidate `d689a55dc81a8966ed89aecac7d2da6b16a57343` against
frozen main `acbb903df111bb30609baedac35316b22d43700e`, identical inputs and
seed numbers in both arms. Total paired run: **1,147.09 seconds**. Every stage
reported no running game, six workers and `CLAWSHOT_WORKERS=6`, under the
round-20 gate lock, released on normal completion.

| Recipe | Seeds per arm | First failures main → candidate | Exhausted main → candidate | Median seconds main → candidate | Median paired delta seconds |
|---|---:|---:|---:|---:|---:|
| Broad | 200 | 9 → 9 | 0 → 0 | 12.471 → 12.898 | +0.540 |
| Defaults | 50 | 0 → 0 | 0 → 0 | 4.895 → 4.903 | −0.004 |
| Recommended | 50 | 3 → 3 | 0 → 0 | 8.629 → 8.723 | −0.001 |

Broad mean/max attempts were **1.045 / 2 in both arms**; Defaults **1 / 1**;
Recommended **1.06 / 2**. Main's paired broad arm reproduced all nine
attribution failures. All 600 completed generations passed the production
goal/softlock search and exact normalized shuffled-stock assertion.

Broad recovered seeds: **5, 8, 88, 113, 140, 165, 180, 188**.
Newly first-failing seeds: **2, 26, 47, 138, 150, 167, 187, 195**.
Seed **181** failed in both arms, but changed from late map/compass failure
to Token progression failure. All nine candidate first errors are
`progression: Gold Skulltula Token`. Recommended's same three first errors in
both arms are two Ocarina of Time and one Fairy Ocarina.

**Decision (cs20g, following the round brief): reject.** Broad first-attempt
failures did not drop, and median generation time rose **0.427 seconds
(3.42%)**. The measured positive median paired delta agrees with that direction.
Zero exhausted seeds alone is insufficient. No timing rerun or second candidate
was attempted to seek a passing result. Preset timing differences are small and
paired deltas near zero; no statistical significance claim is made.

The early map stage removes the observed late-filler errors, but replaces them
with equally many Token failures. [INFERENCE] It protects one capacity class at
the expense of shared progression flexibility; it also sends twenty otherwise
fast-filled items through restrictive Search and changes RNG consumption.
This measurement does not separate those effects. The evidence does not justify
merging either this stage move or round 19's broader stage/swap rewrite.

## Research handoff and verification boundary

The candidate line and its candidate-only synthetic regression have been removed.
`fill.py` and `tests/test_fill.py` returned to their original snapshots; the
branch's only net change from its starting main is this round record. The rejected
implementation remains at `d689a55` for reproducible research, **not a merge head
to take alone**. No product change remains, so the round instruction requires
**no full gates**. No READY (merge) product claim, full-gate pass, current-main
rebase/gate claim or in-game acceptance is made.

External retained receipts:

- `sweep.py`, `inputs.pkl`, `baseline_fill.py`: fresh input capture and counted baseline.
- `attribution.log`, `attribution-rows.jsonl`, `attribution-summary.json`,
  `group.py`, `attribution-grouping.json`: all baseline errors and location grouping.
- `trace_failures.py`, `trace-failures.jsonl`: aimed printed capacity/frontier evidence,
  separate from the acceptance counts.
- `map-capacity-baseline.log`, `focused.log`: baseline witness and candidate focus.
- `paired.py`, `paired.log`, `paired-rows.jsonl`, `paired-summary.json`: balanced
  paired timing, all attempt payloads, exact heads, process snapshots and worker counts.

Future work starts from current main, not from either rejected candidate. The
remaining construction issue spans early reachable Chest/Token capacity and
inaccessible frozen opener copies; merely reserving maps early was not a net
improvement. No product-policy question, additional retry allowance or gameplay
loosening was introduced. No game files were added to the output/pack manifest,
and no game, personal seed or save was opened or changed.
