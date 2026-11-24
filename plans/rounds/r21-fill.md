# Round 21, Track fill — cs21h

Branch `r21/fill`, starting main `e9bb0d77270fbc92a455df53dac1f4099b6bc859` (0.2.5 plus the round 20 close records).
Model: `anthropic/claude-opus-5-5`. Status: **READY (merge) `37572a9`**: candidate 2 accepted, full gate passed.
External scripts and receipts: `E:/OOTRemake/work/r21-fill/`.

No game started, personal seed opened, save edited or game/runtime folder written. This is a generator-only
track: fill construction changes, no change to `allowed`, logic, pool, destinations, retry bound or game output
format. It needs no play packet (READY kind: merge).

## Method (round 20's, unchanged)

- Inputs: fresh production preparation captured through `patch.make_seed` before output writing
  (`work/r18-dungeon-items/fill_probe.inputs`, seed 2306988613), from this worktree at `e9bb0d7` (`inputs-head.txt`),
  into `work/r21-fill/inputs.pkl`. Recipes: broad = the exact CS1 in `work/r18-fill/settings.txt`, seeds 0–199;
  Defaults and Recommended (`app/presets.toml`), seeds 0–49.
- Each generation is production `generate()` with its ten-attempt bound, the final goal/softlock proof and the
  exact normalized shuffled-stock assertion. Every failed attempt's FillError is recorded with its stage payload
  (remaining items, swaps, reachable compatible occupied checks by contents, empty check types; for late filler,
  the stranded items and chest contents by class).
- Main's arm is a byte copy of `e9bb0d7`'s `generate/fill.py` (`baseline_fill.py`, sha256 `ad3c7ee5…`); the
  attribution run loads it explicitly whatever the worktree holds.
- Paired comparison (`paired.py`): identical inputs and seed numbers, main-first on even seeds and candidate-first
  on odd seeds, in the same worker; first failures, exhausted seeds, mean/max attempts, median seconds and median
  paired delta per recipe.
- All sweeps under `work/rounds/r21/gate.lock` (owner.txt written with the mkdir), `CLAWSHOT_WORKERS=6`, six
  workers, game image check per stage; the lock is released in `finally` by its creator.

## Main re-measure (2026-11-22 17:29–17:37, under the lock)

Frozen main fill (`baseline_fill.py` = `e9bb0d7`'s `fill.py`; owner.txt showed the branch head `bd059b0` because
the script ran from this worktree, but the attribution arm loads the frozen copy explicitly). Broad 0–199, six
workers, `CLAWSHOT_WORKERS=6`, no game running. Receipts: `attribution.log`, `attribution-rows.jsonl`,
`attribution-summary.json`, `attribution-grouping.json` (from `group.py`).

**10/200 first failures (5.0%), 0 exhausted, mean 1.05 / max 2 attempts, median 14.56 s.** Round 20 measured
9/200 on `acbb903`; eight of its nine seeds fail again (140 no longer does), plus 51, 110 and 196.

| Cause | Seeds | What the payload shows |
|---|---|---|
| Shared progression, `Gold Skulltula Token` | 51, 88, 110, 113, 188 | 5–16 reachable empty checks, all NPC/Song/Scrub/Cutscene; the reachable checks a token may take hold tokens (10–35 each) plus 0–5 others, and a token never swaps with a token |
| Late filler, released map/compass stranded | 5, 8, 180, 181, 196 | 0–1 empty chest left (seeds 8 and 181: one chest, not allowed for the item); shuffled chests hold 156–158 progression items; 36–45 NPC/Song/Cutscene/Scrub checks still empty, later filled with junk |

Same two causes as round 20, with the same proportions. Both are construction order, not capacity: the token
frontiers have 68–97 allowed empty checks that cannot be reached yet, and the filler failures leave 36–45 empty
non-chest checks that flexible progression could have taken instead of the last chests.

## Candidate (`137daca`, rebased from `bd059b0` onto `f7ba65f`, a doc-only main move)

Proposed by cs21h from the round 20 and 21 payloads. Two changes in `generate/fill.py`, neither touching `allowed`,
logic, pools, swaps or the retry bound:

1. **Tokens first.** In the shared progression stage, items held only to Chest and Token checks (the Gold
   Skulltula Token) are placed right after native displays, while most progression is still assumed and every
   chest and Skulltula can be reached. Placed in seeded order among the rest, the last copies found the reachable
   chests and Skulltulas filled by earlier copies.
2. **Chest reserve.** The shared progression stage gets the later filler list. Once the empty chests are no more
   than the items only a chest can take (this stage's and the filler's: released keys, maps, compasses), any other
   item puts its non-chest candidates first. Same pattern as the existing shop-refill reserve; only the order of
   reachable candidates changes.

Defaults and Recommended do not shuffle Token, so (1) does not apply to them; (2) can apply to any recipe once
chests run short.

Spec change (proposed by cs21h, for Claude's review): `plans/04-world-format.md` stage 6 said "Token items retain
the same seeded random candidate ordering as other progression; no weight or reserved quota" (round 19). The
candidate changes the *item* order (tokens after native displays, before the rest) and adds the chest reserve; each
item's candidate locations keep their seeded order and no quota is added. Stage 6 now says so.

Synthetic witness `test_flexible_progression_leaves_the_last_chest_to_a_released_map` (`tests/test_fill.py`, round
20's four-check shape): frozen main fails it with `no beatable fill in 1 attempts; last: items left unplaced:
['Map (Temple)']` (`map-witness-main.log`); the candidate passes it, with a tool still landing in a spare chest in
some seeds.

Focused run, no game running, `CLAWSHOT_WORKERS=1`: `uv run --with pytest-xdist pytest -n 2 -q tests/test_fill.py
tests/test_generate_tokens.py tests/test_key_families.py tests/test_dungeon_rewards.py tests/test_age_fill.py
tests/test_gifts_fill.py tests/test_house100.py tests/test_progressive_logic.py tests/test_custom_token_composition.py
tests/test_generate.py tests/test_tokens.py tests/test_reward_bridge.py` → **375 passed, 10 skipped (dump), 26.28 s**
(`focused-1.log`). Smoke runs of the candidate on round 20's nine failing broad seeds, single process: all nine
filled on the first attempt (not a measurement).

Cost proxy (not a timing claim; wall clock was unusable beside cs21b's full gate): one `fill` attempt each, broad
inputs, seeds 0–4 and 6, profiled call counts candidate/main = 0.996, 0.957, 0.956, 0.942, 0.948, 0.973. Tokens
first does not make the fill do more work per attempt.

Paired run: placed 9th in `gate-order.txt` (after cs21c).

Rebased onto `3667df5` (sticks merged, MAIN MOVED 22:59); main's `fill.py` is still byte-identical to
`baseline_fill.py`. Inputs recaptured from `3667df5` into `inputs.pkl` (they differ from the `e9bb0d7` capture,
kept as `inputs-e9bb0d7.pkl`). Focused run again (same command, no game running): **375 passed, 10 skipped,
27.98 s** (`focused-3.log`). The paired run's main arm on these inputs is the after-sticks re-measure of main.

Rebased again onto `ff78b5e` (tracker, no generator/data change) and `b1d510d` (npcs logic: Richard, Cojiro); main's
`fill.py` still byte-identical to `baseline_fill.py`. Inputs recaptured from `b1d510d` (`inputs.pkl`; the `3667df5`
capture kept as `inputs-3667df5.pkl`). Before the paired run: rebase onto the main of that moment, recapture if it
moved, rerun the focused command.

## Handoff (2026-11-23 10:30)

- Branch `r21/fill`, head `f896b98` on main `b1d510d`: `fill: tokens first in shared progression; keep the last
  chests for maps` (product change + witness test) and three plans-only commits.
- Checked: main re-measure on `e9bb0d7` (10/200 broad first failures, 0 exhausted); synthetic witness fails on main,
  passes on the candidate; focused 375 passed / 10 skipped after each rebase; call-count proxy 0.94–1.00x.
- Not yet checked: the paired comparison (the acceptance measurement), the after-sticks re-measure of main (its
  main arm), the 200/50/50 sweep and the full gate. Gate order at 10:24: cs21c, cs21e, then cs21h; and no sweep
  while `longshot.exe` runs (Kareem playing) or until it has been closed 10 minutes.
- Decision rule fixed in advance: accept only if broad first failures drop, zero exhausted in every recipe, and
  Defaults/Recommended do not get worse; otherwise reject and leave this file as the research record, with the
  candidate reverted.

## Paired run 1: candidate 1 rejected (2026-11-23 17:46–18:03, under the lock)

Head `fe4bccd` (candidate 1 = `5f6e2e1`'s change rebased) on main `aeba6df`; main arm = `baseline_fill.py` (still
byte-identical to main's `fill.py`); inputs recaptured from `aeba6df` (identical to the `5078acb` capture,
compared field by field). Six workers, `CLAWSHOT_WORKERS=6`, no game running at any stage; 1,015.85 s; lock
released by its creator. Receipts: `paired-r21.log`, `paired-r21-rows.jsonl`, `paired-r21-summary.json`.

| Recipe | Seeds per arm | First failures main → candidate | Exhausted | Mean / max attempts main → candidate | Median s main → candidate | Median paired delta s |
|---|---:|---:|---:|---|---|---:|
| Broad | 200 | 6 → 14 | 0 → 0 | 1.04 / 3 → 1.07 / 2 | 10.808 → 10.509 | +0.023 |
| Defaults | 50 | 0 → 0 | 0 → 0 | 1 / 1 → 1 / 1 | 5.175 → 5.235 | +0.004 |
| Recommended | 50 | 2 → 2 | 0 → 0 | 1.04 / 2 → 1.04 / 2 | 9.385 → 9.460 | −0.037 |

**After-sticks (and npcs, PR #40, hammer, pr39-accept) re-measure of main, `aeba6df`: broad 6/200 first failures
(3.0%), 0 exhausted** — 4 `Gold Skulltula Token`, 1 `Small Key (Forest Temple)`, 1 `Small Key (Fire Temple)`, all
shared progression; no late map/compass failure. Before sticks (`e9bb0d7`, above): 10/200. Defaults 0/50,
Recommended 2/50 (both `Kokiri Sword`, seeds 36 and 45, unchanged by the candidate). [INFERENCE] The drop from 10
to 6 comes from the merged logic changes moving placements (Claude quoted cs21e's sweep at 14/200 on its own
seeds and inputs; the counts are not comparable across those cohorts).

**Decision (cs21h, under the rule fixed at 10:30): reject candidate 1.** Broad rose 6 → 14.
Recovered seeds 17, 122, 138, 157, 172, 195: tokens first removed every shared-progression failure, keys included.
Introduced 8, 14, 19, 34, 60, 89, 105, 112, 152, 159, 167, 169, 191, 199: all fourteen are late filler with a
map or compass stranded.

Printed cause (`trace_filler.py`, `trace-filler-candidate.jsonl`, single process): tokens placed first put about
61 of 100 tokens in chests (seed 8: 61 chests, 39 Skulltulas), so chests run short; the reserve was then off by one
or two in every one of the fourteen. Two undercounts: (a) the Ice Cavern map and compass counted as flexible because
one non-chest check in their dungeon (`Sheik in Ice Cavern`) may take them, so two items rode on one slot that
was usually taken anyway; (b) chests no map may take (`Hyrule Field Chest (Obj_Heart_Piece)`, explicit exclusions)
counted as supply. Each failing seed had 18–20 empty chests for 20 maps/compasses at the filler.

## Candidate 2 (aimed at the printed cause)

Same two changes; only the reserve's accounting in `_chest_bound` changes:

- A released dungeon item always counts as needing a chest (outside its dungeon only a chest takes it; a stray
  in-dungeon check does not make it flexible).
- Supply is the empty chests every chest-needing item may take; when tight, other items put those chests last
  (other checks, then chests none of them may take, are tried first).

Effective reserve sizes at stage entry (seed 1): broad 155 of 156 empty chests counted, 64 chest-needing copies;
Defaults 89 of 89 with every item chest-needing (Chest-only shuffle: the reserve never reorders anything);
Recommended 0 chest-needing items (own-dungeon keys: the reserve never fires).

Aimed check (same tracer, single process, first attempt of each seed): **19 of the 20 seeds** that failed in
either arm of paired run 1 now fill (`trace-filler-candidate2.jsonl`). The residual, seed 89: 20 empty chests,
19 usable by maps, 20 maps. The reserve was on for 74 of 217 steps, but late flexible items (Pieces of Heart,
Din's Fire, Zelda's Lullaby, Fairy Ocarina) still took chests when no other reachable check was left. The reserve
is an order preference, not a guarantee. Not a measurement; only the paired run counts.

Focused (same command, no game running): **375 passed, 10 skipped, 23.26 s** (`focused-6.log`); ruff clean.
Candidate files kept: `candidate1_fill.py`, `candidate2_fill.py`.

## Paired run 2: candidate 2 accepted (2026-11-23 18:12–18:30, under the lock)

Claude placed this one rerun (rule 9, after the printed cause) at 18:11. Head `1673def` on main `aeba6df`; same
frozen main fill, same `aeba6df` inputs and seed numbers as run 1. Six workers, `CLAWSHOT_WORKERS=6`, no game running
at any stage; 1,080.97 s. Receipts: `paired-r21b.log`, `paired-r21b-rows.jsonl`, `paired-r21b-summary.json`.

| Recipe | Seeds per arm | First failures main → candidate | Exhausted | Mean / max attempts main → candidate | Median s main → candidate | Median paired delta s |
|---|---:|---:|---:|---|---|---:|
| Broad | 200 | 6 → 1 | 0 → 0 | 1.04 / 3 → 1.005 / 2 | 11.884 → 11.589 | −0.270 |
| Defaults | 50 | 0 → 0 | 0 → 0 | 1 / 1 → 1 / 1 | 4.873 → 4.869 | −0.006 |
| Recommended | 50 | 2 → 2 | 0 → 0 | 1.04 / 2 → 1.04 / 2 | 9.532 → 9.457 | +0.046 |

Broad recovered 17, 122, 138, 157, 172, 195 (all of main's: four Token, two small keys); introduced 89 only, the
late map/compass residual the aimed trace predicted. Recommended's two are the same seeds (36, 45) and error
(`Kokiri Sword`) in both arms. Main's arm reproduced run 1's six failures exactly. All 600 completed generations
passed the production goal/softlock search and the exact normalized shuffled-stock assertion.

**Decision (cs21h, under the rule fixed at 10:30): accept.** Broad first failures dropped 6 → 1 (3.0% → 0.5%), zero
exhausted in every recipe, Defaults and Recommended unchanged. Nothing reachable changes: `allowed`, logic, pools,
swaps and the ten-attempt bound are untouched; only the order of items (tokens first) and of reachable candidates
(the chest reserve) changes, and every seed still passes the beatability search. Placements change, as expected.

Rule (2) sweep: Claude agreed (17:47) that the candidate arm counts as the sweep on this exact head: 200 broad + 50
Defaults + 50 Recommended, 0 exhausted. The change adds no option, so no extra recipe applies.

## Full gate on `1673def` (same hold; 20:10–20:57)

The first gate run (18:30) died with the session at ~18:35, synthetic at 99%, no result; the lock then sat idle,
held by cs21h, until 20:09 (posted on the thread). Rerun detached, logs `work/r21-fill/gate/` (`gate.log`):

- `ruff format --check`: 558 files already formatted; `ruff check`: all checks passed.
- Synthetic `-n 8`, `CLAWSHOT_WORKERS=4`: **4389 passed, 838 skipped, 423.35 s**.
- Dump `-n 8`, `CLAWSHOT_WORKERS=3`, `OOT_ROMFS`, `OOT_NUP`, `OOT_DUMP` as the round brief: **830 passed, 5 errors,
  2484.21 s**. All five are the setup of `tests/test_getitem_ocarina_dump.py` (PR #40's file), printed payload:
  `placements do not fit this world: LW Gift from Saria: may not hold 'Gold Skulltula Token'`.

Cause: the fixture took seed 7's placements and swapped whatever sat in `KF Midos Top Left Chest` into the Fairy
Ocarina's source. Under the new fill that chest holds a Gold Skulltula Token, which a gift may not take. The fixture
depended on the fill's incidental placement, not on anything the test checks. Fix (cs21h, own commit on top; BBender's
commit and the maintainer commit untouched): when the source may not take the chest's item, it goes through the first
chest holding non-progression that the source may take. Verified on the real dump (same three variables, `-n 2`,
`CLAWSHOT_WORKERS=1`, no game running): **6 passed, 179.91 s** (`ocarina-dump-fix.log`). Not a re-pin: the seed stays
7 and every assertion is unchanged.

Dump stage rerun on `37572a9` (test fix `7694c08`, touching only `tests/test_getitem_ocarina_dump.py`, +20 −2, plus
this plans commit), 21:04–21:53 under the lock, `-n 8`, `CLAWSHOT_WORKERS=3`, all three variables, no game running:
**835 passed, 2919.75 s** (`work/r21-fill/gate2/dump.log`). With the synthetic/format/lint pass on `1673def`
(unaffected by a dump-only test), the gate is complete.

## Handoff

- READY (merge): `r21/fill` head `37572a9` on main `aeba6df`. Product: `5f6e2e1` (tokens first, chest reserve) +
  `1673def` (reserve accounting); test fix `7694c08`; the rest plans-only.
- Measured: broad first-try failures 6/200 → 1/200, 0 exhausted in all three recipes, Defaults and Recommended
  unchanged; generator-only, nothing to play.
- For review: `plans/04-world-format.md` stage 6 now describes the item order and the chest reserve.
- Next for cs21h: `r21/dungeon-hold` from main after this merges (Claude, 2026-11-23).

## Lock note

cs21h took the lock at 17:29 out of turn: a retry loop acquired it when the directory was free, not on the
predecessor's LOCK RELEASED. Claude allowed the attribution to finish; the chained paired run was cancelled before
it started. From then on cs21h acquires only on its predecessor's LOCK RELEASED.

## Dungeon hold (branch `r21/dungeon-hold`, from main `efdea7c`)

Asked by Claude after Kareem approved cs21j's tightening (`r21-placement-audit.md` section 6), 2026-11-23. A
tightening: no play check (the loosening test, a compass from Sheik's lesson, goes in round 22's batch).

Change (`generate/fill.py`): `allowed()` holds `SmallKey`, `BossKey`, `GanonBossKey`, `Map` and `Compass` to Chest
checks in every mode, inside their own dungeon too (`CHEST_HELD_DUNGEON_TYPES`). Choices made by cs21h:

- **Exception: a released floor-key source** (`KeyPickup`, today only the Well) may still hold its own native small
  key. That is the game's own pickup, already palette-limited to its key or a red rupee (`key_families`), played on
  Longshot rc.7 (docs/settings.md). Every native source of these types is a Chest or one of those two floor keys
  (census: 65 Chest, 2 Collectable).
- **Ganon's boss key included** (same rationale, a further tightening); **key rings and silver rupees excluded**:
  they have no chest grant and keep their own-dungeon rule (`test_generate_dungeon_areas.py` pins that).

Before the change, `allowed()` let these types take (printed by a scan of every shuffled non-chest location):
Sheik in Ice Cavern (Map, Compass) with Gift + songs anywhere, broad recipe included; with Freestanding or Scrub
shuffled and no Freestanding palette, the Well's floor rupees (Map, Compass, keys), Fire/Ganon's Castle recovery
hearts (boss keys) and the Dodongo's Cavern and Jabu scrubs (Map, Compass). Defaults and Recommended: none.

Tests:

- New synthetic `test_dungeon_items_go_only_to_chests_even_beside_other_kinds_in_their_dungeon` (`tests/test_fill.py`):
  a dungeon with four chests, a lesson, an NPC and a scrub, every mode, ten seeds each. Main's fill fails it at
  `own_dungeon` seed 0 (`Boss Key (Temple)` on a non-chest check).
- New dump `tests/test_dungeon_hold_dump.py`: cs21j's seed 1 (Chest + Gift, songs anywhere) through `gifts.seed_setup`
  and `make_seed`. Main's fill: `{'Sheik in Ice Cavern': 'Compass (Ice Cavern)'}`; with the hold: passes.
- Three contract tests pinned the old rule (own dungeon takes these types at any kind) and are updated to the new one:
  `test_generate_tokens.py` (palette-free Skulltula), `test_key_model.py` (`Forest Floor`),
  `test_generate_dungeon_areas.py` (`Temple Floor`).
- Focused, no game running, `-n 2`, `CLAWSHOT_WORKERS=1` (20 fill/key/dungeon files): **513 passed**.

Docs: `docs/settings.md` (dungeon items paragraph), `plans/04-world-format.md` (placement modes).

Sweep and full gate on `806de40`, one hold under the lock, 22:05–23:10, no game running at any stage (receipts in
`work/r21-fill/`: `hold-hold.log`, `hold-sweep.log`, `hold-rows.jsonl`, `hold-summary.json`, `hold-gate/`). Inputs
recaptured from `efdea7c` (`inputs-hold.pkl`). Every completed seed also asserted the exact normalized stock and that
no held type sits at a non-chest, non-floor-key-source check: all 350 completed.

| Recipe | Seeds | Exhausted | First failures | Mean / max attempts | Median s |
|---|---:|---:|---:|---|---:|
| Broad | 200 | 0 | 1 (seed 89, late map/compass, as on main) | 1.005 / 2 | 10.03 |
| Defaults | 50 | 0 | 0 | 1 / 1 | 4.25 |
| Recommended | 50 | 0 | 2 (36, 45, `Kokiri Sword`, as on main) | 1.04 / 2 | 7.56 |
| Chest + Gift, songs anywhere | 50 | 0 | 0 | 1 / 1 | 5.70 |

The fourth recipe is cs21j's reproduction recipe: the broad recipe already shuffles Gift with songs anywhere, so
"broad with Gift and songs anywhere" would have repeated it.

Gate: `ruff format --check` 560 files already formatted; `ruff check` clean; synthetic `-n 8`/4 **5166 passed, 63
skipped, 795.28 s**; dump `-n 8`/3 with `OOT_ROMFS`, `OOT_NUP`, `OOT_DUMP` **836 passed, 2633.17 s** (one more than
main: the new seed-1 regression).

**READY (merge)** `r21/dungeon-hold` (gated head `806de40`, plus this plans-only commit). A tightening; built, nothing
to play. The loosening check (a compass from Sheik's lesson) is round 22's.
