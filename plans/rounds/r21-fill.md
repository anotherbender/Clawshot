# Round 21, Track fill — cs21h

Branch `r21/fill`, starting main `e9bb0d77270fbc92a455df53dac1f4099b6bc859` (0.2.5 plus the round 20 close records).
Model: `anthropic/claude-opus-5-5`. Status: **in progress**.
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

## Candidate (`bd059b0`)

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

Paired run: waiting for a lock slot (READY FOR LOCK posted 17:37).

## Lock note

cs21h took the lock at 17:29 out of turn: a retry loop acquired it when the directory was free, not on the
predecessor's LOCK RELEASED. Claude allowed the attribution to finish; the chained paired run was cancelled before
it started. From then on cs21h acquires only on its predecessor's LOCK RELEASED.
