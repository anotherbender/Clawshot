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

## Main re-measure

(pending)

## Candidate

(pending)
