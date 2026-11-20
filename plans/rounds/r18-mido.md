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
External logs: `work/r18-issue35/mido-{red,focused}.log`. No placement sweep is needed; played evidence below.

## Play packet

Packet staged at `E:/OOTRemake/work/r18-mido/ingame/CHECKLIST.md`, approximately ten minutes, plain
landmarks and two template-derived CRLF launchers: `01-main-control.bat`, then `02-candidate.bat`.
Initial CLI dry runs initialized identical isolated saves without launching the game, but incorrectly
resolved Hookshot. Claude corrected both launchers using the nested Longshot finder from the
r18-issue34 packet and reports corrected dry runs resolve **Longshot rc.7**. All play checks and future
packets use that Longshot template, with `longshot_log.txt`; the original launcher proof is historical
save-identity evidence, not rc.7 proof. Claude subsequently reported check 14 **PLAYED PASS**;
the observations below are maintainer-reported, not an agent-run game check.

Control is the **public generated overlay from d3ce136** preserved by the failing regression; candidate
is the corresponding passing public overlay from implementation `421ef418389c9348d5bd89e25a41a8f298928ff4`.
Both are Chest-only seed 35 / bridge-only / four fast-start skips. All **178 placements are identical**;
only the child schedule, the one unsaved GameData expression and its RSTB allocation differ.
`work/r18-mido/overlay-proof.json` checks every resource and the exact inverse GameData/RSTB delta.

No already-castle-complete natural pre-clear fixture was found in the selected research inventory.
Final source is the natural r13 native-Mido sword-only snapshot `2026-11-12_113925-r13-faststart-native-6`.
The **only** final-fixture mutation is `Step_Goto_HyruleCastle Ready -> Complete`, four bytes
92996–92999. Saved blocker true; child; early meeting Step02; mouth/seen-0070 false; sword naturally owned,
no shield; **21 rupees**. Full parent comparison verifies unchanged inventory, position, all other
entries/key sets, version, size and auxiliary files. Fixture SHA256:
`d15a7402ef0905271f38cce69ff25754af1bc97f701613ddb8d5b2fc4b2a745a`.
Both arms copy `work/r18-mido/fixture/v2-save` unchanged; `final-fixture-proof.json` and
`launcher-proof.json` record this. The first both-equipped fixture was superseded, never launched:
the final check does not depend on an unproved ability to unequip an owned item.

Fixture history is r13 seed 7, not the test overlays' seed 35. This is an explicitly bounded Mido
mechanism experiment: **no chest/randomized checks**. Prove sword-only refusal, buy the fixed unshuffled
10-rupee Deku Shield, equip the pair, then prove physical crossing/open mouth/reload. The original
save's bridge remains closed; that is outside this gate check. No inventory, position, Zelda-history
or other quest edit is concealed. No Slingshot or Gohma play is needed.

## Check 14 — PLAYED PASS

Claude reported Kareem's check 14 pass: main had no Mido at the guard spot and retained the invisible
wall. Candidate kept Mido blocking the passage, refused sword-only Link, and opened the way after
the shield; the tree mouth was open. After reload Mido walked along the tunnel toward the Deku Tree,
stopped at his native late spot and remained talkable; the wall stayed gone. The played saves showed
the blocker false, mouth open and 0070 seen. This confirms the predicted post-clear relocation is
normal, rather than an orphaned blocker. No game was launched or save edited by cs18a for this check.

## Gate queue

Claude's current integration base is main `2d9ddefa2c16d5205f6a52d29a98d6c62c4b22b9` (F+G and E merged).
On check 14's pass, cs18a is authorized to wait for cs18b's posted rebased head on that base, then
stack Mido on cs18b, resolve `patch/__init__.py` additively, run focused tests and freeze the exact
stacked head. **cs18b alone drives one combined full gate**; cs18a takes no lock and runs no separate
gate or sweep. Do not rebase onto an unposted or stale cs18b head. Full gate remains pending; no READY
claim until the combined gate passes. The original implementation is
`421ef418389c9348d5bd89e25a41a8f298928ff4`; integration evidence follows when available.
