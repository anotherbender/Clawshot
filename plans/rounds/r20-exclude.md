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
- First integrated focus invocation exited5 with no collection: the historical rejected round-19
  `tests/test_fill_holds.py` does not exist on main. The printed path inventory established that cause;
  the corrected file set below did not change or narrow any existing test.

## Focused and browser proof

`git rebase main` on implementation `c1c1ccf36f` reported up to date (`acbb903`).
Core aimed focus: **11 passed, 4 deselected in 2.50s** (selection skips the app consumers).
Integrated command, `CLAWSHOT_WORKERS=1`, no running game:

```sh
uv run --with pytest-xdist pytest tests/test_excluded_locations.py tests/test_app_location_picker.py \
  tests/test_app_schema.py tests/test_app.py tests/test_ui.py tests/test_fill.py tests/test_house100.py \
  tests/test_settings_house100.py tests/test_key_families.py tests/test_gifts_fill.py -n 2 -q
```

**157 passed, 3 dump tests skipped in 54.97s**. Receipt: `integrated-focused-v2.log`.
Subsequent cleanup removes one newly added metadata-wiring test; consumer regressions remain.
Scoped Ruff: eight changed Python files already formatted, lint passed.

Actual isolated app surface: area groups, search auto-expansion, readable/canonical names, selected and
hidden-selected counts, and hidden check retention were observed. Selecting Frog Game plus House100 now
returned HTTP200 and the decoded actual UI CS1 contained exactly both names. No JS errors. The server
used in-memory preferences and an empty external library root; no player seed directory was scanned.
Both servers/tabs were closed. After Claude's new headless-only steering, the browser tool's owned
browser was closed with `all=true, kill=true`; process inspection found no Chrome matching omp/debug/headless.
No more omp browser calls will be used for this track.

Claude approved extracting `gifts.movable_checks(world, rules)` as shared dump-free eligibility:
native `seed_checks` and app capacity validation now use one predicate, not two copies. This is a
pure refactor of native eligibility. Required **all-output SHA-256 parity** against frozen main for
two Gift and two Recommended seeds is pending under the gate lock.

The first sweep acquisition found cs20g's paired-sweep lock and exited75; no seeds started and no foreign
lock was removed. Heavy acceptance will use six sweep workers, then eight xdist workers with internal
four (synthetic) / three (dump), downshifted if a game is running.

## Broad recipe conflict found at validation

The first locked broad recipe included **Market Treasure Chest Game Reward**, as a literal reading of
"every minigame". Validation correctly refused it before any fill attempt: it is held vanilla by D17,
and `data/world/items.toml:91` classifies its special `Piece of Heart (Treasure Chest Game)` as progression
(alias to a Piece of Heart). No hold/classification is changed by this track. The initial recipe errors
are retained in `sweep-v1/` and are not exhausted fill attempts or passing sweep evidence.

**Product question (cs20b proposal, posted 23:03): may the realistic acceptance list mean every
shuffle-eligible minigame, plus all frogs and House rewards, omitting the held Treasure Chest Game
reward?** Keeping the native hold and refusing an impossible exclusion is safer than silently changing
the pool, reclassifying the item or claiming this fixed source became skippable.

**Resolved by Claude (engineering call, standing hold rule): approved.** The acceptance list omits only
the held Treasure Chest Game reward; no native hold or item classification changes. The approved list
has31 checks: the other minigames, all seven frogs and all six House rewards. The harness now preflights
each native-prepared recipe once before dispatching seeds, so an invalid recipe stops before a cohort.

Initial `sweep-v1` completed50 Defaults (0 first failures, mean/max1, zero exhausted) and50 Recommended
(3 first failures, mean1.06/max2, zero exhausted). Its200 broad jobs all refused the invalid list with
**zero fill attempts**; the generic harness called those `exhausted=200`, but the recorded zero attempt
counts establish pre-fill validation refusals, not failed ten-attempt fills. This is not an accepted broad sweep.

Picker follow-up: permanently held/fixed-progression sources are omitted using the ordinary preparation
and shared gift eligibility with all supported shuffle options enabled. Future-shufflable sources remain
selectable; recipe-dependent holds/capacity are still validated. In particular the held TCG reward and
its held key-room checks are not offered, while the fixed non-progression expert-gallery reward remains.

Aimed follow-up: **57 passed in27.21s**, `CLAWSHOT_WORKERS=1`, `pytest -n2` on
`test_app_location_picker.py`, `test_excluded_locations.py`, `test_app_schema.py`.
Explicit **Playwright Chrome `headless=True`, `--headless=new`** proof then passed: held TCG progression
controls absent, normal expert prize present, Frog+House100 actual CS1 publication, hidden selection
retention and zero JS errors. Screenshot: external `headless-picker.png`; receipt: `headless-picker.log`.
No browser tool was used for this follow-up; the headless browser and isolated in-memory server closed.
