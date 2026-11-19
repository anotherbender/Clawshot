# Round 18: Mido's completed-castle schedule (#35)

cs18a; branch `r18/mido`, base main `d3ce136`. Claude authorized implementation on 2026-11-19 for 0.2.3, otherwise round 19 with a known-issue note. Claude owns the release/version decision.

## Contract

With Mido kept, change only his completed-castle schedule condition to:

`Goto_HyruleCastle_IsCompleted_Exp AND NOT KokiriForest_Npc_Kokiri_Mido_Child_Blocker`.

Other schedule rows, anchor positions, equipment checks, event entries and quest writers remain native. No additional proven orphaning path was identified for those rows. No placement/settings/logic change and no seed sweep. Open/legacy-Mido-skipped seeds retain their existing behavior.

The native actor relocates rather than despawns. Early Zelda can activate its C5 late Talk while the separate saved wall flag remains true; that Talk cannot clear it. Full read-only evidence and privacy-safe reporter guidance: `E:/OOTRemake/work/r18-issue35/findings.md`. The stranger's paths, usernames and data are never copied into this repository.

## Implementation and proof

Implemented `patch/mido_schedule.py`, paired by production `make_seed` only when `forest != open`.
The fast-start-only low-level writer remains a partial flag/flow tool, not a full seed generator.
The child schedule's single completed-castle `ConditionFlag` becomes `Clawshot.Mido.AfterClear`;
all other rows/actions/entries remain native. The unsaved BoolExp is exactly native postfix
`[[10,266250874],[0,1345285354],[5],[3]]`, with U32 hash 2886058494, I32 reset 0/save index -1
and U64 command words. Source completion/Bool rows, enum ordering and hash availability are checked.
Five native expressions use that opcode shape; two are already AISchedule conditions.

Schedule raw bytes **3256 -> 3244**; its measured RSTB allocation stays **13824** through `BuiltFile`.
No generic BGYML size formula is added: native schedule overheads are not constant. GameDataList gains
one computed row, no saved defaults or layout change; its normal writer raises the RSTB entry.
With only this expression, raw **1462888 -> 1462980**, required allocation **1463272**.
Other GameData transforms compose normally; open/Mido-skipped output emits neither new resource nor row.

Fail first: public `make_seed` + `write_seed` overlay selected C5 with castle Complete and blocker true:
**1 failed in 59.32 s**. The payload prints the native condition and primitive state.
After the implementation: **50 passed in 154.88 s**, single-worker, native dump enabled:

```sh
CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest \
  tests/test_mido_schedule.py tests/test_mido_schedule_dump.py tests/test_fast_start_mido.py \
  tests/test_fast_start_mido_dump.py tests/test_settings_forest.py tests/test_settings_forest_dump.py -q --tb=short
```

These cover the native component round trip/exact inverse edit, all castle-step/saved-blocker states,
unchanged saved layout, source drift/hash collisions, actual public written allocations and open-mode
passthrough, alongside existing native equipment/clear contracts. Formatting completed; scoped lint
initially found one overlong fixture string, fixed by literal concatenation; scoped lint then **passed**.
External logs: `work/r18-issue35/mido-{red,focused}.log`. No game result or placement sweep is claimed.

## Play packet

Candidate and base-main control, approximately ten minutes. Prefer an existing natural pre-clear child save with Zelda met and the saved wall still true. Only if none exists, Claude permits one documented edit on a natural early save: `Step_Goto_HyruleCastle=Complete`, identically in both arms. No inventory/position/other quest edits. Original saves and game outputs remain read-only.

Check control's absent/relocated Mido plus wall; candidate's gate-position Mido; equipment refusal; sword+shield native talk; wall clearance, tree-mouth access and reload. Packet must name plain landmarks in `CHECKLIST.md`. Agents do not launch the game; Claude boot-checks and Kareem plays.

## Gate queue

No lock acquisition before the combined F+G owner releases it and our assigned turn. Focused checks first; full gate queued behind F and G. No sweep is needed for this non-placement change. Not READY; runtime repair unplayed.
