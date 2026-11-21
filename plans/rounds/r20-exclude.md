# Round 20, Track exclude — cs20b

Branch `r20/exclude`, base `acbb903df111bb30609baedac35316b22d43700e` (0.2.4 plus PR #36).
Model: `openai-codex/gpt-6.1-sol`. Status: implementation in progress; not READY yet.
External receipts: `E:/OOTRemake/work/r20-exclude/`.

## Scope and agreed design

Player-selected `Settings.excluded_locations`, empty by default. Canonical world names are sorted/deduplicated
and replay through CS1; CLI `--exclude-locations` accepts quoted names, and an empty flag clears a replayed list.
App picker: areas, search and persistent checked selections. Spoiler and play note name the list.

Claude's explicit 2026-11-20 thread/steering decision **supersedes the brief's early ordered-stage line**:
constraint-only, no new pre-commit fill stage. `prepare.py` compiles progression names into each selected
location's existing `excluded_items`. Existing `allowed()` enforces the constraint through the return kit,
palettes, held stages, safe swaps, filler and external placements. `fill.py` changes only our additive
Settings field/list validation/serialization; no algorithm changes. cs20g owns any later fill change.

Validation-time bipartite capacity matching uses the same `allowed()` predicate after holds, palettes and
screens, rather than counting unusable junk. It commits no placements and consumes no RNG. The native final
pool is checked before fill retries, with native overrides and progressive normalization. Unknown/N64-only
non-check names are refused; fixed progression cannot silently ignore an exclusion. Fixed non-progression
checks may stay on a recipe's list. Inability to construct/prove the remaining seed still refuses generation,
with the list and final fill error. Existing independent return-kit and beatability proofs are unchanged.

Facts only: both OoTR and SoH publicly offer excluded locations; reference
`E:/OOTRemake/work/r20-planning/feature-compare.md`, Logic and tricks table / Gaps item 2, sourced there to
<https://wiki.ootrandomizer.com/index.php?title=Readme> and <https://www.shipofharkinian.com/randomizer>.
No source from either project was opened or copied.

## Checks and acceptance

Pending focused tests, actual app surface, current-main rebase, locked full gates and sweep:
200 broad seeds using `work/r18-fill/settings.txt` plus realistic minigame/frog/House exclusions;
50 Defaults and 50 Recommended, zero exhausted required. Record first-attempt errors as well.

No new game resource/patch, no pack input change, no staged game check required. No game started, no
personal seed/save opened or modified, no writes to a game/runtime directory. This is generator/settings
work, not a new claim about played native grants. Intended READY kind: **READY (merge)** after gates.

## First-attempt findings (retained)

- Initial focused collection failed before tests: the picker's new top-level tracker import formed
  `schema -> tracker.__init__ -> tracker.saves -> tracker.logic -> schema.validate`. Printed traceback
  located the cycle; the picker moved its presentation-only location-index import inside its cached helper.
- Initial actual browser selection of Frog Game plus House100 returned HTTP400: capacity for
  `Buy Magic Bean` was missing. Raw `Gift` expansion incorrectly counted the unsupported bean merchant as
  shuffled; native `gifts.seed_setup` would keep that source vanilla. This is a dump-free validation bug,
  not an exclusion-capacity failure. The fix must use public gift admission/holds for validation and preserve
  the final native-pool check. Search, area expansion, selected counts and hidden checked selections were
  visually observed, but CS1 persistence was **not** successful on this attempt.
