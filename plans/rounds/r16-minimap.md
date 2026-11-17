# Round16 minimap follow-up — cs16b (`r16/minimap`)

## Maintainer direction and played evidence

Claude requested this follow-up on a NEW branch from `6d79e57`, leaving `r16/time` untouched:
RED first; preserve `IsVisitLocation.HyruleField=true` only in the Kaepora skip; audit other skips and
handle only proven lost first-OpenLocationUI effects; stage a roughly two-minute new-game map check.
**The full gate is HELD until Claude explicitly authorizes it after the v4 time check merges.**

Kareem, via Claude: **v4 part1 natural owl PASSED** — owl talk played, minimap showed, Door remained
shut, clock ticked after the real send-off. This does not certify the remaining v4 parts.
Kareem also confirmed the Kaepora-skip Field full map says **unavailable**. cs16c traced the skipped
`Dm_HrlField_0000` panorama's OpenLocationUI effect to `IsVisitLocation.HyruleField`. This player report
is ground truth; cs16b has not launched the game or repeated it.

## Isolation

Worktree: `E:/OOTRemake/clawshot-r16/minimap`, branch `r16/minimap`, base `6d79e57`.
The first herdr creation attempt returned `server_not_running` before creating a workspace;
plain `git worktree add` then created the requested isolated worktree. Claude clarified that agents
must never run herdr/hc, including creation; all further work follows that rule. No time-branch
checkout, tracked-file edit, reset, rebase or merge was made. This worktree has its own `.venv`.

## RED, then one-line production fix

Added `test_kaepora_skip_keeps_the_field_map_available_without_its_panorama` to the existing
`tests/test_fast_start_banner.py`, reusing the synthetic GameData builder. The regression requires
both the panorama's skipped history and the visit effect needed for the Field map; it does not
pretend walking into the Field replays the skipped UI action.

Before any production edit:

`uv run pytest tests/test_fast_start_banner.py::test_kaepora_skip_keeps_the_field_map_available_without_its_panorama -q -p no:cacheprovider`

**1 failed in0.46s**, with the printed payload:
`HavePlayedEvent.Dm_HrlField_0000=true`, `IsVisitLocation.HyruleField=false`.
The TOML stayed unchanged; SHA256 `21eb8f384b91d05f7d586cdab25050b3a00584e913aee379a3a9f34254fed9f3`.
External evidence: `E:/OOTRemake/work/r16-minimap/red-proof.json` and `red-output.txt`.

Then added exactly one production line, under `[setting.kaepora.game_data]`:
`"IsVisitLocation.HyruleField" = true`. No other skip, history, clock input, world rule or setting default
was changed by this fix. This supplies the skipped location UI's native effect for **new games**;
it is not a save-repair pass for an already-played seed.

Focused post-fix command only:
`uv run pytest tests/test_fast_start_banner.py -q -p no:cacheprovider`

**5 passed, 1 skipped in0.22s**. The skip is the existing dump-marked native Saria check, not a native
pass. Both focused runs used `CLAWSHOT_WORKERS=1`; Longshot was running at their stage starts.
No full synthetic suite, dump suite, lint gate or game was run. GREEN proof/log live beside RED.

## Native-derived skip audit and focused proof

Claude supplied facts about UISystemActor's two visit-writing operations; no other randomizer's
code was opened or copied. Replaced the old single-event native Saria assertion with
`test_every_skipped_location_banner_preserves_its_native_visit`. It derives the marked-event
list from the shipped fast-start/always settings, resolves native RSDB EventSetting flowchart,
timeline and companion references, follows literal EventTransition targets, and requires each
lost OpenLocationUI area's visit flag in the setting that suppresses it. A current-small-location
operation fails with its source path rather than silently assigning an assumed area.

Read-only native audit also included the owl chain's unmarked `Dm_HrlField_0005`, derived from
the native wrapper trace. Across eight events and16 routed file references (including timelines
and companions), only `Dm_Kokiri_0045` opens KokiriForest and `Dm_HrlField_0000` opens HyruleField.
No current-small-location operation was found. All six previously undecoded tree/owl timeline
residuals were decoded; no additional missing visit flag was found. Evidence is outside the repo:
`E:/OOTRemake/work/r16-minimap/native-banner-audit.json`.

Focused command, with `OOT_ROMFS=E:/Games/Hookshot/romfs` and `CLAWSHOT_WORKERS=1`:

`uv run pytest tests/test_fast_start_banner.py -q -p no:cacheprovider`

**6 passed in0.49s**, including the native-derived dump check. Only this focused file ran;
the full gate remains held. Ran `uv run ruff format tests/test_fast_start_banner.py` on the changed
test file only. Documentation records the approved side effect: the preserved visit flags reveal
their areas on the pause map before the player visits them. No other production change was needed.

## Staged handoff and separate clock investigation

The already-staged launcher is
`E:/OOTRemake/work/r16-minimap/ingame/Test - minimap-kaepora-v1.bat`; checklist beside it is
`MINIMAP-CHECKLIST-V1.md`. It has one fresh empty user and one isolated two-resource mod.
Its prior dry-run passed; it has not been launched by this agent. Play estimate remains roughly
two minutes excluding startup, unmeasured. Need the maintainer's runtime load lines plus minimap
and pause-map observations; neither is claimed passing. The natural-owl v4 part1 PASS above is
not a played Kaepora-skip minimap pass.

Claude subsequently requested a **no-code** clock/ENV investigation. Results and the proposed
native clear/wait-one-frame/palette-rebuild repair were reported before any clock implementation.
Evidence lives at `E:/OOTRemake/work/r16-clock-timing/observations.md`,
`env-native-trace.json` and `env-reader-detail.json`. ENV selects forced-light palettes for both
ages; an underlying numeric clock stop is not proven. The A-cache hypothesis was refuted.
P4's immutable Jabu source has ENV=false and was unchanged by inspection. No clock implementation,
source save, game folder or runtime was changed; no game was started. Clock implementation and
the full gate remain held for Claude's direction.
