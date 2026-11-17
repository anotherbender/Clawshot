# Round 16 Track B — time of day (#32)

Agent: cs16b (`openai-codex/gpt-6.1-sol`), branch `r16/time`. Original base `dd3b453`; rebased first onto `.nup`-only `af6a7b4`, then cleanly onto cs16a's posted `f93cd4b1b77dd676e724a1b2d4070c47b412594f`. Closed-output comparisons use that A head; all four full gates run at the combined stack top.

## Scope and safety

Investigate native clock/Sun's Song and early Door state; failing regressions first; protect both early modes without losing the escape/moat checks; prove closed output identity and measure early-mode changes; stage Longshot v3.0.0-rc.5 acceptance. No version bump or game launch by this agent.

Issue #32 was read through `gh issue view 32` (no comment). The report distinguishes worldwide stuck night after the first sword pull on 0.2.1 from Gerudo Fortress stuck day on 0.2.0. These are observations, not yet one proven cause. The attachment downloaded successfully using plain `curl -L --fail` (2,738,232 bytes); all log material, research, generated mods and any staged saves remain exclusively under `E:/OOTRemake/work/r16-time/`. No private log paths/usernames are reproduced here.

## Confirmed cause and decisions

The native clock reads saved Bool `HavePlayedEvent.Dm_HrlField_0020` (Hash `0x53efe6f6`), Impa's **field send-off**, not merely courtyard contact. At text `0x3ce2a8..0x3ce2c4` it branches away from ordinary advancement while false; `0x3ce620..0x3ce650` supplies a fixed 54000-second (15:00) fallback. This proves the missing-unlock freeze. The exact presentation path that leaves the reported world at night is not established from the tester's log; a log does not contain the save. Actual sword/arrival timelines and their subtimelines contain no time-setting action. Sun's Song's day/night query and visual time request are distinct from ordinary progression.


Sanitized attachment inspection: one log, 27,836,602 uncompressed bytes; one `mods:` line each for `GameData/GameDataList.Product.110.byml.zs`, `Event/EventFlow/DoorOfTime.bfevfl.zs`, `Logic/Market_Common_f252.logic.module.ainb`, and `Banc/Market/Market_Child_Static.bcett.byml.zs`. No adult Market or Bootup override was logged; no line contained `error`. This proves those resources loaded, not the player's saved quest state.

Decoded issue settings: both seeds use `door_of_time=open`, native/default reverse travel and the same broad non-Shop/non-Token shuffle kinds. 0.2.1 uses `forest=open`, default intro skip; 0.2.0 uses `forest=closed_deku` and `deku_tree,intro,saria` skips. Neither selects the Kaepora skip.

### Product provenance

- **Kareem, relayed by Claude, 2026-11-16:** in `open`, the **Door itself**, not a pedestal presence gate, stays shut until the real send-off; then opens without songs or stones. Back-room/Time Travel logic must match.
- **Claude's explicit choice, confirmed 2026-11-17:** protect **both** early modes. `song_only` also requires the send-off, while keeping the learned Song of Time and either child ocarina. The initial closed-output identity requirement was subsequently superseded by the approved shared ordering repair below; closed placements and spoilers must remain identical to `f93cd4b`.
- **Claude, 2026-11-17:** pre-existing escape/moat loss after an early pull is in scope. Permit late quest states with native Fire/Water completion, real send-off and unplayed-event conditions, and make the nine late Door writes forward-only; retain the courtyard reset.
- **Claude, latest linear-stack instruction:** after cs16a finishes its current gates and posts its af6-based rebased head, rebase this track onto that head. Run all four gates at the stack top; main moves once. Closed output identity compares against **cs16a's head**, not af6/dd3, because A's Slingshot logic can legitimately change placements.
- **Not a save repair.** This prevents new freezes; it does not repair already-frozen saves. Never swap a played pre-send-off adult save to the new output on a save-compatibility assumption. No send-off/history/default is forged.

The send-off flag is not clock-only: `ZoraRiver_Child_Prefab_07cf` node5 reads it; nodes6/8/9 combine it with Saria's lesson history to create the river owl/contact/request area, removed after `Dm_ZoraRiver_0005`. Native hash materializations also exist at `0x41ea7c/0x41eacc` and `0x345c968/0x345c9b8`. The physical/altar gate avoids all early history writes and cannot skip Impa's shuffled song source.

Direct Prelude teleport is not a back-room bypass: native `Dm_SY_Ocarina` Event20 selects child `Market_Child` / `LightPrelude`; StartPos Hash `4578708010518158057` in `Market_Child_Dynamic` lands in the front hall, before the stone altar and Door. Read-only placement inspection compared that anchor with the actual Door and sword; no warp permission assumption or new warp restriction was needed.

### Release seed and mode evidence

Private app regeneration reproduced both issue hashes exactly: 0.2.1 seed332751819 `D70084C06D92`; 0.2.0 seed1582717117 `42523F62EDFE`. For 0.2.1, spoiler search reaches Time Travel in sphere0 but Met Child Zelda/Time Flows only in sphere1: a pre-Zelda first pull was permitted. The attachment's loaded mod files all belong to the reproduced output. Main's pre-fix placements differ from the release after earlier fill changes; never compare release/main save compatibility by seed number.

`song_only` was also unsafe with a shuffled Time song: it explicitly bypassed the quest-progress gate, so the song need not come from the moat. A new failing case showed both the native song-opening flow and world back-room rule accepting that pre-send-off inventory. `closed` retains its native post-escape/song route. Open Forest/free return/intro/Saria/Deku/Kaepora skips do not set the clock-unlock history; open Forest facilitates the early route, and free return alone does not repair it.

Fortress-only daytime is separate: the native adult Fortress world parameter uses a fixed daytime environment. Neither release overrides that resource. A day-looking Fortress is not evidence of a worldwide stopped clock; compare Hyrule Field/Graveyard. The worldwide clock issue is not attributed to the Fortress palette.

## Late Door transitive audit and repair

Read-only supported NUP inventory: **914 event files (653 flowcharts,261 timelines),11707 loose/packed AINBs,149463 BYML members,8385 packs**. The transitive closure from `Step_DoorOfTime` plus opened/reaction state has15 keys and223 matched rows. Full decoded ledger remains private at `work/r16-time/door-progression-audit.json`, not in this repository.

| Late reader | Dependency and treatment |
|---|---|
| Physical gate `Market_Common_f252` node8 | Native >=Step06; `open` instead uses real send-off via node6/node5. Both gate `isOpen` and `IsSkipAnim` consume it. |
| Child pedestal `Market_Child_Prefab_e700` node2 | Exact Step06; already replaced by the native ungated attention module in open. Song-only retains its native opening/Step06. |
| Altar actor `Obj_TimeTemple_SpiritStoneBase_A_01` ReplaceEventParam | `Market_Child_TimeTempleDoor_OcarinaReacts`: song-only invalid until send-off or after opened; open always invalid, so the already-open Door does not run the stone scene. |
| `DoorOfTime` Event60/Event67; `Dm_SY_Ocarina_SariaSong` Event12/65 | `IsAfter_Step04`; native expression stays unchanged and Complete satisfies it. |
| `HidingHole_Level_Hole_23_Prefab_5d28` node18 | `IsAfter_Step05` gates the shared Forest/Fire Time-block interaction, not a grotto reward. Complete satisfies it; block disappearance/once flags stay native. |
| `Dm_SY_Ocarina_SariaSong` Event72 | `IsAfter_Step06`; unchanged, satisfied by Complete. |
| `Market_Child_Prefab_b715` node2 | Door completed expression; native first-pull Event93 still sets Complete, and late callbacks cannot undo it. |
| `HyruleField_Child_Prefab_0ce5` node3 / `_9e35` node3 | Exact Step03 escape sensor/weather: extend through guarded late-stage readiness, including Step06/Complete, native Fire/Water completion, send-off and unplayed escape. |
| `HyruleField_Child_Prefab_91f9` node0 | Exact Step04 moat ocarina: extend through guarded late-stage readiness, requiring escaped and unplayed Time-melody source, not ownership of shuffled rewards. |
| `HyruleField_Child_Prefab_32f7` nodes4/5 | Moat areas/airwall/area-out event must also remain usable until the late pickup; prevent premature airwalls and delete after the actual source is collected. |
| Running Man `_592d` node3 and NPC/talk/presence selectors | Native exact Step04 / after-Step03 presentation windows remain unchanged; their complete-state behavior predates the fix. |
| Sheik, adult return, Light Arrows, Ganon bridge | No late-Door condition in the resource closure: Temple Sheik/return use Forest completion; first-arrival history and Light Arrows/bridge conditions remain native. |

Native15-key binary audit (LE32 literals, MOVZ/MOVN+MOVK, all3 segments, with known-positive clock control) recovered direct `IsAfter_Step2_2` at `0x3e4048..0x3e4058`, `IsCompleted` at `0x32279cc..0x32279dc`, and8 key-table entries around `0x3f0aa30..0x3f0adc0`. Original expressions are unchanged; Complete satisfies their after predicates and remains completed. This method does **not** prove absence of every dynamically synthesized/lookup native reference.

The pre-existing loss is real in data: first pull reaches native Event93 Complete, but the escape sensor requires exact03 and moat actor exact04. The R10 “Step04 or later escape” inference is superseded by R14's exact-step audit. `Recovery` only restores life/MP/UI; it does not recover a skipped story step. Do not rely on undocumented `IsIgnoreCompletedChallenge` behavior.

Nine lower Door writers are guarded at their own event index, preserving continuation: `DoorOfTime` Event7/147/148/37/12/14/57, `Dm_SY_Ocarina_SariaSong` Event172, and `Npc_Hylia_Zelda_Child` Event42. Native strict `IsAfter_<target>` skips only backward writes; equality retains native behavior. `Goto_HyruleCastle` Event32 remains entirely native: its forced Step01 reset is necessary before Impa. First-pull Event93 Complete stays untouched. In all modes the stone counter waits for actual send-off, reruns after that send-off, and stops after escape; no early or repeated bridge raise.

The altar suppression is **new** versus `dd3b453` open. It skips only the native opening transition `Dm_TimeTemple_0010`, opened write and Step06 write; Step05 belongs to the later moat song aftermath and is not suppressed. The noon setter is escape Event34, retained unchanged, not the opening scene. Earlier research suggestions to the contrary were corrected before implementation.

## Verification

- Initial open-gate/world regressions failed before the physical gate/logic change, then17 targeted cases passed. Independent native decoder verified the intended common-gate rewrite, unchanged quest reader, same length/allocation and no saved-default/history change.
- New song-only send-off regression: **2 failed,14 passed** before; **16 passed** after the targeted flow/rule correction. Actual CLI help exercised.
- Actual isolated browser UI: selected both modes, read rendered send-off help and visually checked fitting labels. No normal preferences/save roots or game were opened. Proof/screenshot remain private.
- Actual post-pull native-stage RED: both early modes at Complete/all stones/send-off/unplayed escape had no escape/storm and all four moat areas deleted (**2 failed**). Same public-path cases after integration: **2 passed**.
- Post-af6 targeted synthetic: **150 passed,93 deselected in11.33s**, including forward-only boundaries, repeated callbacks and readiness truth tables.
- Independent full native decoder/writer oracle passed in7.62s: all four story modules equal exactly the specified graph deltas, same lengths/native allocations; three typed unsaved predicates only; actual integrated `door.write` outputs in both modes; closed no stage output. Private `story-native-gate-proof.json`.
- Working-set integration correction: the initial1271-file coverage only covered the old manifest, not the four new story inputs. `pack/resources.toml` now includes all four. Private fixture `E:/OOTRemake/work/rounds/r16/time-layered-dump` preserves1275 supplied physical files unchanged, adds only the four pinned native AINBs, and covers all1275 effective inputs with none missing (`extended-fixture-proof.json`). No source/game write.
- Clean rebase onto cs16a's posted `f93cd4b` completed. On code head `02238bd`, all13 serial real-app/CLI generations passed against the private extended fixture; every run checked game processes and used workers4. No gameplay behavior is claimed verified.
- Real-app default-return regression: first generation refused because the early-mode kit omitted the newly compulsory send-off. Both new feasibility regressions failed with their printed minimums; after carrying only `Met Child Zelda` into both data profiles,2 passed. No optional inventory or guarantee relaxation; native generations subsequently passed. The obsolete exact-minimum copy assertion was removed, not re-pinned.
- After that repair the real app exposed a separate missing temporary-ROMFS input (`HyruleField_Child_Prefab_0ce5`); adding all four story modules to the manifest fixed this actual staging failure. The existing cache-only native mode oracle exercises both early modes; no wiring-only test was added.
- All required full gates passed on frozen combined head `8c689222099e56225ff65c41f2d943203ddd76fb`: Ruff format413 files, lint all checks passed, synthetic **3029 passed/319 skipped** (604.47s), native dump **316 passed/3032 deselected** (5707.81s). No source edits during gates. Each stage checked game processes and selected workers4; dump supplied `OOT_ROMFS`, `OOT_NUP` and the private extended `OOT_DUMP`. Logs and head/command records: private `stack-f93cd4b-gates-v1/`. Owned lock released immediately afterwards.
- The post-gate commit changes only this round's evidence; production, test and resource-manifest bytes remain those exercised above. Left: Claude review/linear-stack merge and Kareem's gameplay acceptance, not another agent game launch.

### Generated-output controls

Seed332751819; identical per-row settings and source for A `f93cd4b` versus B `02238bd`. Exact per-file/key digests and route facts: private `stack-f93cd4b-v4/`.

| Door | Free return | Placements equal | Spheres equal | All output bytes equal | B hash |
|---|---|---|---|---|---|
| open | off | yes | no | no | `EA34AF469E46` |
| open | on | yes | no | no | `9B55C96C991F` |
| song_only | off | yes | yes | no | `15A14C913355` |
| song_only | on | yes | yes | no | `CF10861E7D6D` |
| closed | off | yes | yes | yes | `C2D8B0E7E2E4` |
| closed | on | yes | yes | yes | `9F309CC92795` |

Closed spoilers are also exact. Early-mode effective settings/strings change with the compulsory-story minimum; open spheres and their replay-derived metadata change too. The actual open-mode app/CLI outputs are byte-identical. Corrected open search records send-off, Time Flows and Time Travel together at sphere1, not Time Travel at sphere0 before send-off. These controls do not authorize swapping an arbitrary played seed/save.

## In-game acceptance

Claude reports Longshot `v3.0.0-rc.5`, source `013b1d3a`, installed in place in the pinned `builds/v3.0.0-rc.4` folder on2026-11-16; launcher paths stay unchanged. His2026-11-17 02:09 thread report boot-checked all four **superseded v2** overlays: crash0, every mod found (11–13 RomFS files each). This does not certify the rebuilt v3 overlays, which require fresh startup and gameplay checks by Claude/Kareem.

Final controls are staged under `E:/OOTRemake/work/r16-time/ingame/`; exact directions and Claude-only boot commands are in `TIME-CHECKLIST.md`. All four approved-template launchers passed `CLAWSHOT_DRY_RUN=1`; read-only reporter exercised all four actual user copies; every source checksum and native story/age/location remained unchanged. No game launch by this agent. The pre-Zelda source is the authentic castle corridor immediately before the courtyard; the order source is authentic Jabu Water Step11, Forest/Fire Complete, before the third stone and first pull.

| Launcher suffix | Progress words changed | Mod resources | Control |
|---|---:|---:|---|
| `time-gate-open-v3` | 1 | See `acceptance-v3-proof.json` | Pre-Zelda; only Sun's Song staged, Fairy Ocarina native, no Time Ocarina/song. |
| `time-gate-songonly-v3` | 2 | See proof | Same pre-Zelda source; Sun's Song and learned Time song staged. |
| `time-order-open-v3` | 0 | See proof | Exact pre-third-stone progress copy; both moat rewards remain vanilla progression. |
| `time-order-songonly-v3` | 3 | See proof | Time song/Time Ocarina stock staged; moat item becomes Hammer and song becomes Hookshot, both absent initially. |

All test overlays enable free return **only for a quick child return**; production default stays off. Checklist covers both pre-/post-send-off modes, native Impa reward, clock/Sun's Song, first pull before Barinade's stone, later escape and both moat grants, Door remaining open/no second stone scene, save/reload/no repeats/no moat airwall. One gate control estimated5–10min; both10–20min; each late-order control15–25min; all four40–70min, unmeasured in game. Claude boot-checks, Kareem supplies runtime `mods:` load lines plus observations. Do not teleport to DreamWorld/BarinadeStage as a substitute for the real boss.

### Harness failures, not accepted-settings failures

The baseline runner's `extra` step was a private send-off consumer audit, **not seed generation**. It failed at `audit_sendoff_readers.py:49` with `BymlError: unsupported BYML value type 0xa1` while decoding an unrelated value. After byte prefiltering target references before parsing, the rerun succeeded (3.8s); all baseline seed generations succeeded. Later broad Door audit prefiltering also required document-endian/word-aligned hash candidates to exclude an unaligned opposite-endian match inside an Effect binary payload. No production format support or accepted settings were weakened.

The fourth acceptance profile initially failed in its private harness: `flow_files(R,FLOW_VERSIONS)` passed the resource-path string instead of the parsed mapping (`AttributeError: 'str' object has no attribute 'get'`). The first three successful profiles were not overwritten or rerun; explicit resume verified them and completed only the remaining native gift overlay/launcher after parsing `Versions`. Final four-profile proof passed. This was not seed generation or an accepted-settings failure.

The first stack-control harness passed a version-labelled `Clawshot-0.2.1:CS1...` string directly to CLI `--settings`, which requires bare `CS1`; rc2 printed the exact parser error and no generation ran. Prefix handling was corrected in the private harness. This is distinct from the subsequent two real-app integration failures recorded above. Every failed output remains private; no unchanged failure was retried.

## Review follow-up on46b8d72

Claude requested the native courtyard Step01 reset, exact native byte/file/string and unrelated-path oracles, explicit kit/label contracts, rebuilt v3 profiles, then one gate run. The native counter reads Fire/Water, not Forest; the added Forest predicate is removed. Proposed by cs16b from that native trace, in response to the review.

**Claude approved completing the ordering repair in every reachable Door mode, including closed with shuffled songs.** Native Fire/Water completion callbacks are the only original counter callers; both before Zelda can raise the bridge, and the courtyard reset/send-off leaves Step02 without another clear callback. The physical bridge obstruction remains **[INFERENCE]** from native actor Presence, not an in-game observation. The repair suppresses counter effects before the real send-off, calls the native counter afterward, and ignores later calls after actual escape. No completion, inventory, or history is forged.

The closed-mode child-only trace is `E:\OOTRemake\work\r16-time\closed-pre-courtyard-logic-proof.json`: `Met Child Zelda`, Time Travel and Zelda's Letter are held at zero; all six warp songs and Farore's Wind are excluded. A shuffled Lullaby is eligible in `KF Kokiri Sword Chest`; King Dodongo is reachable through Lost Woods → GC Woods Warp → Goron City → Death Mountain, and Barinade through Lost Woods → Zora River → Zora's Domain → Fountain. This is prepared-native rule reachability with placeable-pool inventory, **not a generated placement or in-game proof**.

Historical-save scan:262 eligible native/test backup families,1,059 freshly decoded slots, no authentic Fire+Water-complete/send-off-unplayed match. No extra pre-Zelda-two-stones v3 profile is staged; that order has native-flow/logic data proof only. Existing played/randomizer/foreign seed families were excluded; no save was written by the scan. Evidence:`historical-both-before-zelda-proof.json`.

Closed comparison **passes** against preserved successful `f93cd4b` app generations with the same seed/settings, for both free-return values: placements, spheres and spoiler bytes are identical; no files added/removed. Exactly `Event/EventFlow/DoorOfTime.bfevfl.zs` (shared history-gated counter, post-send-off recount and entry registration) and `System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs` (only that flow's allocation) change. Exact comparisons: `review-v3-closed/proof.json`.

### Final test-only closure and verification provenance

Runtime source is frozen at `81bf50f`. The four v3 overlays were built from that head, all launcher dry runs passed, and actual isolated user saves were read back without writes; `acceptance-v3-proof.json` records their hashes. Nothing in the test-only closure changes source or requires rebuilding those successful overlays.

The **single full gate** at `81bf50f` passed repository format/lint and synthetic tests (`3073 passed,364 skipped`). The full real-dump run returned `357 passed,4 failed`: all failures were the old Darunia shared emulator rejecting the newly reached native `EventQueryHavePlayedEvent` in `ClawshotDoorCountSendoff`. Every other dump test, including all-mode stone ordering, courtyard reset, bridge and native-byte oracles, passed. Logs/results:`E:\OOTRemake\work\r16-time\review-v3-gates`.

The test-only fix records actual completed-transition history, reads native Fire/Water completion and integer writes, and checks that an already-won Fire stone is counted at send-off (Step2_1/count1), rather than bypassing the recount or retaining its obsolete Step02 expectation. The native default count2 is present in both reference and patched initial states, preserving the vanilla-order state comparison.

**Claude explicitly accepted this closure and proof scope:** final-head repository-wide `ruff format --check`, `ruff check` and the **full synthetic suite**, plus a real-dump targeted rerun of all three shared-emulator consumer modules (`test_story_steps_darunia.py`, `test_story_steps_fire.py`, `test_story_steps_darunia_dump.py`). Targeted results and exact harness hashes:`review-v3-harness-closure/proof.json`; final-head checks:`review-v3-final-head/proof.json`. Handoff must show `git diff 81bf50f..HEAD` contains only tests and docs.

**No second full dump:** the357 passing dump tests exercised identical production source; only the two emulator/contract test files and this evidence document change afterward. The targeted real-dump run closes their affected contracts, and the full synthetic rerun covers other consumers. This is not a claim that the original full dump had no failures, nor a gameplay PASS. v3 startup/load proof and player observations remain pending.

Targeted real-dump closure **passes:97 tests**, all three consumer modules, with matching narrow format/lint checks. The unchanged harness file hashes are recorded in that proof and checked again for final-head verification; no v3 overlay rebuild is needed because production source is still the frozen `81bf50f`.

## rc.7 played results and clock follow-up (2026-11-17)

Kareem's observations, relayed by Claude, supersede the earlier pending-acceptance wording above. Longshot is
`v3.0.0-rc.7`; its current launcher executable is under `builds/rc/bin`. This agent did not launch the game.

| Played control | Accepted result | Remaining failure |
|---|---|---|
| `time-gate-open-v3` | **Gate PASS:** shut before Zelda; Zelda's Letter, Impa's Lullaby and the Field send-off played; Door open afterward. | **Clock FAIL:** no ordinary Field progression; Sun's Song changes appearance then snaps back. Captured state has A false despite real send-off. |
| `time-order-open-v3` | **Order repair PASS:** Door open; first-pull scenes played; Barinade completed; Zelda's escape still played after the early pull; moat granted both Ocarina of Time and Song of Time; return to adult worked. | **Clock FAIL under B's hold:** night after the drawbridge scene and Sun's Song still snaps back. Claude's corrected snapshot read has A/S true and ENV false throughout; B becomes true after first pull. The earlier A-false attribution was wrong. |

The new order evidence is preserved in private backups matching
`work/save-backups/2026-11-17_*-r16-time-order-open-v3-*`; the earlier gate evidence uses the corresponding
`time-gate-open-v3` families. These are player observations, not replacement automated oracles.
**Kareem's product note:** “a lot of cutscenes, they need to go.” Deferred to a later cutscene-skip track;
no additional scene suppression is authorized in this round.

### Full predicate and limits of the night diagnosis

The earlier send-off-only explanation is withdrawn. A is saved Bool `HyruleField_ArriveEntrance`
(`0x804aec99`), S is `HavePlayedEvent.Dm_HrlField_0020`, and B is
`HrlField_HasEnteredFirstTime_Adult`. Outside normal pause/explicit-time overrides, native stop helper
`0x345c020` stops when `!R && (!A || B)`; unrestricted story cycling needs `R || (A && S && !B)`.
R is the special live `Meet_DekuTree == Ready` override, not Forest-stone completion.
In the ordinary, non-override update branch, missing A selects 21600 seconds (06:00); A present with B selects
72000 (20:00). Without S, otherwise-running time clamps at 54000 (15:00). Native update also has explicit-world/
timeline branches before the fixed-time selector: world flags bits24/25 feed clock offset0x58, distinct from
ordinary base time at0x28. The original synthetic replay covered the ordinary branch, not all live overrides.

The captured gate save is child, A false, B false, S true, `Meet_DekuTree=Complete`, Castle Complete and Door
Step02: stopped clock follows directly, but **20:00/B does not follow from those saved inputs**.
Night appearance alone cannot identify the live clock value or prove B true. Kareem's reported night/snap-back
remains ground truth; a differing live override/environment is not established merely by the save.
The immutable pre-courtyard source already has A false, `_0000`/`_0010` true, `_0005` false and
`HyruleField_ChangeENV=true`; the played gate copy retains that environment flag. Its current Kaepora setting
being off does not undo inherited progress. The history pattern resembles the old partial skip, but its provenance
is **[INFERENCE]** about that particular historical save, not a claim that Kareem selected that skip for this test.
Claude subsequently confirmed all four of Kareem's own seeds use the Kaepora skip. The authentic Jabu source has
A true; Claude's corrected read of played order snapshots1–28 agrees: **A=true, S=true, ENV=false throughout**,
**B=false at1, B=true from5 onward**. That20:00/snap-back is exactly the B hold, not A.
Private immutable-source proof: `clock-control-source-state.json`; played snapshot facts are Claude's report.

The native escape flow's sole time setter is `DoorOfTime` Event34,
`EventWorldManagerController.EventTrigger_SetTime(TimeHour=12, TimeMin=0)`: **noon, not night**.
An ordinary stopped update with A/S true and B true then selects20:00, so the scene's appearance afterward does
not imply an arbitrary-time A hold. The original issue's stuck-night association with an escape remains
**[INFERENCE]** without its saved B/override state. This corrects the interim night-from-A hypothesis.

The native B clearer is `Dm_SY_BancChangeArrive` entry `Dm_SY_BancChangeArrive_HyruleField_02`:
Event257 queries B; true goes to Event434 (`B=false`), then Event550 fade-out, Event555 two updates,
Event552 fade-in and Event99's camera subflow. Its EventSetting uses the same entry and NoPauseEvent.
Its sole requesting actor is the normal **adult Market→Field exit**:
`Banc/Market/Market_Adult_Static.bcett.byml`, hash8090100398624302801,
`Common_FieldDungeonEntranceSet_bad1`. Player contact requests the arrival with no quest-step guard.
The child exit, a warp and immediate Temple return bypass it. The old v3 checklist permitted that bypass;
it did not require this native clearer. B remains natively clearable by walking this adult exit.

**0.2.2 known-fix item:** Kaepora fast start omits `HyruleField_ArriveEntrance=true`, a native effect of the
skipped first Field owl. Users selecting that skip, **including closed Door mode**, can retain the native
missing-A clock stop after Zelda/Impa's real send-off. Restore that skip effect; do not advertise repair of
existing saved progress. Claude confirmed the affected skip is selected in all four of Kareem's own seeds.

### Completed safety audit and approved implementation

The initial no-edits safety hold was resolved before production edits. Fresh data/BoolExp closure and all
three native executable segments found B's only data reader at its arrival-clear query. Its native readers
are the clock stop, fixed-time selector and `Game.WorldMgr` inspection getter: **no check, spawn or story-step
reader was found**. Preserve the native0055 set and adult Market exit. Claude approved one additional,
conditional clear only after the Temple's adult→child flow sets `Sequence_IsChildhood=true`; timer-blocked
returns and adult warps remain native. No load-time/global clear or product save-repair pass.

A is **not clock-only**: in addition to the clock/inspection readers, native code packs it into a saved-Bool
condition snapshot. No data reader or additional writer was found. Restoring A after the real send-off
reproduces native post-owl state for every known consumer; it does not pretend other scenes were played.
Fresh requester/flow tracing corrected the first route audit: the normal Field→Market arrival can advance
Castle to `Step02_01` without the owl, deleting its sensor. Thus a Door-only A lock would strand a natural
route. The real send-off must restore missing A in **every** mode, without other history writes.

Approved scope (Claude, before coding): one unsaved A AND S expression for both early gates; matching
`Field Owl Arrival` logic and early return minima; independent Kaepora RED/fix; missing-A restoration at
the real send-off; B clear only in `Market_Adult_Field_AdultToChild`; retain the order repair. Closed's item
gate, first-adult scenes and ordinary adult Market clearer stay native. ClockTransitions/ClockGate/ClockLogic
implemented those slices; integration, staging and the frozen gate remain this agent's responsibility.

Plan/estimate posted before implementation: implementation/staging60–90 minutes, frozen synthetic10–15,
full dump90–110 based on prior measured runs. Recheck inherited `CLAWSHOT_WORKERS` and game/stream processes
at **each stage start**, reducing to one worker during play/streaming. Stage natural-owl and explicit-Kaepora
new games, adult Market walk-out and immediate child return; then freeze and run one complete synthetic
plus complete dump gate. Game boot/play evidence remains Kareem's/Claude's; this agent never starts the game.

### Adult-before-Talon trade-cell answer

cs16b's report-only audit found **no offered-setting route remaining** under the approved gates. Both early
modes need the real send-off; closed still needs native Door quest progress. The courtyard requires Castle
Step04, whose only native writer is the Talon wake movie. Free time travel only relaxes adult return;
Forest openness/skips and a child Prelude landing do not bypass that first-pull story gate.

The trade cell itself is unchanged: adult trade variants still hide the Cucco, so Letter-before-adult-trade
guidance remains. D31/R13 keep trade rewards out of the pool. The two apparent hold gaps,
`LW Trade Cojiro` and `ZD Trade Prescription`, are `gift_rules.toml` class `more`, excluded by
`gifts.seed_checks`; they do not introduce pooled variants. Actual CLI
`--logic adult_trade_shuffle=true --print-settings` refused with exit2 (unsupported native patch).
No trade-policy edit was made. Releasing trade items or adding an earlier first-pull route requires reopening
this audit; old/debug/cross-seed saves are outside the offered-settings claim.

### v4 staging and closed-output evidence

Standalone Kaepora RED at942a903: `test_kaepora_skip_lets_the_clock_run_after_the_real_sendoff`
gave **1 failed, 1 passed** before the TOML fix; the selected skip remained at06:00 after the real-send-off
history while the native-owl control ran. Full printed inputs and the unmodified TOML hash are in
`work/r16-time/kaepora-arrival-red/`. The independent regression deliberately does not use the new
send-off fallback, so that fallback cannot hide another skip omission.

Two actual app generations (seed332751819, closed + Kaepora, free travel off/on) passed in78.02/78.59s.
Against their preserved942a903 controls, **settings, placements, spheres and raw spoiler.json are unchanged**.
Both add `romfs/Event/EventFlow/Market_Adult_Field_AdultToChild.bfevfl.zs`; both change exactly:

- `romfs/Event/EventFlow/DoorOfTime.bfevfl.zs`
- `romfs/GameData/GameDataList.Product.110.byml.zs`
- `romfs/System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs`

No files are removed. The GameData delta was decoded from those existing outputs only, with **no extra
generation or test run** (Claude's request): the sole value change in the complete typed tree is
`Data/Bool[Hash=0x804aec99]` (`HyruleField_ArriveEntrance`), `DefaultValue=false→true`.
Hash2152393881, reset8, save index0 and every other key/row/header stay identical, including S/B.
Decompressed sizes stay1,463,136B without free travel and1,463,228B with it. Both profiles select Kaepora;
the all-mode runtime flow repairs use existing A/B keys, and the new unsaved ClockReady row is early-mode
only. No extra skip-off generation was run. Evidence: `work/r16-time/closed-gamedata-entry-diff.json`
and `clock-v4-closed-output/candidate-proof.json`.

Four isolated v4 overlays/profiles passed launcher dry runs; no game was started. Their private checklist,
`work/r16-time/ingame/TIME-CHECKLIST-V4.md`, has exactly four short parts, estimated35–55min in game
(not measured). The historical corridor genuinely starts A/S/B=false; the historical pre-third-stone
Jabu save genuinely starts A/S=true, B=false. **No A/B/S, age, quest or scene-history save edit is needed
or performed.** Only the disclosed inventory/D-pad words change on private copies, verified against
the full original save trees and source hashes. Fresh profiles contain no savedata.

The old installed `builds/v3.0.0-rc.4/bin/longshot.exe` path was removed; the first staging attempt stopped
before writes and printed that path. After correcting only the pin to the discovered
`builds/rc/bin/longshot.exe`, staging completed in60.45s. Native0055/adult-arrival writer files are not
shipped. All stages checked inherited workers and process pressure; OBS was active, so the app/staging
runs used one worker. The only pre-freeze formatter pass left all11 owned Python files unchanged.
Boot, runtime `mods:` load lines, live clock progression and actual save persistence remain **unplayed**.

The first frozen gate at e78b214 passed full format checking, then stopped at lint:
`SIM102`, `tests/test_clock_transitions.py:381`, nested writer-filter conditions. Neither synthetic
nor dump pytest started. cs16b printed the diagnostic and combined only those conditions, with no
production-code, staged-output or acceptance-scope change; the cause-targeted refreeze follows.
