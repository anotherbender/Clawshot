# Round 22: Dampé's first race (cs22a)

Branch `r22/dampe`, base `2091387`; model `openai-codex/gpt-6.1-sol`.
Status: first-race repair gate passed; refusal implementation; **not played** until Kareem's Longshot 3.2.0 check.

## Contract and commit boundary

Kareem's 2026-11-24 report is the reproduction: owning a Hookshot selects the second race, leaving the
first-race chest unavailable. The supplied after-both-races save has clear count 2, first-prize spawn history
false and heart-prize history true. No player seed placements are needed for this repair.

- Select the first race until its own chest is opened, independently of Hookshot tier and prior second races.
- Keep the Hookshot/Longshot admission guard and the native second race after first-chest collection.
- Keep `nonprogression_only` in the merge head. The final, separate lift commit is play-held: Claude must not
  merge it until Kareem passes the staged check. Run the required 200/50/50 sweep on that lift.
- First-race logic keeps the native first-race completion rule, not the second race's one-minute condition.
- Production recipes must exercise the complete flow and event registration, including Hookshot and Longshot.

Read: repository rules, README/CONTRIBUTING, roadmap, round 22 overview, architecture, orchestration,
game-data/world-format specifications and decisions; round 21 overview, placement audit, fill and Hammer
records; original guard commit `de36c43` and current `dampe_safety.py`; failure report's aggregate/native
analysis; track finding in Kareem's 0.2.6 notes; public-doc-only feature comparison.

GPL factual lead: sloperinaGZ `docs/FINDINGS.md`, section 1, **Memory and save data** (local facts reference
`work/refs/sloperina-FINDINGS.md`): saved fields are named/hashed, Struct members have dotted names, pouch
stock and acquisition history are distinct. No implementation copied. Native traces and research outputs stay
outside the repository under `E:/OOTRemake/work/r22-dampe/`; the dump and original saves remain read-only.

## Coordination

Posted shared additive edits on `cs-r22`: production-recipe coverage in `tests/test_event_registration.py`,
Dampe-only documentation and world-source lines. No new setting or runtime build. Claude boot-checks;
Kareem performs play. The agent never starts the game.

## Native trigger chain (rule m)

Read from supported build `e0f3ccfa`, `Event/EventFlow/MiniGame_DampeRace.bfevfl.zs`; event names below
are stable node identifiers, not a copied decoded flow. `de36c43` originally wrapped Ready and Start;
the current guard has the corrected native pouch polarity: case 0 held/true, case 1 absent/false.

1. `Ready_Npc_Hylia_Dampe_002_Talk`: Event109 calls InitTalk, Event59 calls TreasureBoxStateReset.
   That entry's Event215 sets treasure state None; Event172/176/160 reset presentation state and Event266
   clears the open-event history. Therefore none is a permanent first-prize collection test.
2. Event18 tests Longshot stock (held → Event243, absent → Event0); Event0 tests Hookshot stock
   (held → Event243, absent → Event5). Event243 reads HeartGeted and selects the second-race offer.
   Event5/50/49 select first-race dialogue (Event6), with choice Event2 → Event120 → Event113/444.
   First-meeting dialogue Event1 also reaches Forest Step02 writer Event97; the other ready/retry calls use
   MiniGame_DampeRace_NextMainChallengeStep (Event13/11/12). Event260/262 do the same item-dependent split
   for the ready NPC's Near lines.
3. Accepting runs native local Ready/Start calls (Event10/155/25). Ready Event16 configures the timer.
   Existing `ClawshotDampeHookshot*` / `ClawshotDampeLongshot*` wrappers admit either tool, refuse neither.
   They do not select a race or grant a tool.
4. Start's setup ends at Event129, acquired-Hookshot history: true → Event131 writes PlayingSecond;
   false → Event287/305 first-start speech → Event130 writes Playing → Event132 writes Forest Step03
   → Event187 clears first-prize spawn history → Event224 starts the timer.
   PlayingSecond instead shows the timer at Event135/142/17. Event188 marks SecondRace_More only on
   that second-mode tail. Event98/157 likewise control timer cleanup from item history.
5. The native successful finish entry stops the timer (Event31), then Event442 tests Hookshot stock.
   Held calls Event379 → MiniGame_DampeRace_Clear → Event35 adds 1 to ClearCount; absent does not.
   Event33 selects first/second finish presentation; native goal/warp/InitTalk joins reach Event339 → Result.
6. Result Event275 branches on ClearCount: 0 → Event277; 1 → Event359/360/303 time tests for the second
   prize; higher counts → Event399 and the native record/HeartGeted paths (Event390/391/392/205/342,
   Event214/222/223). Existing HeartGeted is never cleared by the repair.
7. Event277 tests the first-prize **spawn** history. False → Event276 first-prize speech → Event345–350
   → Event353 sets IsAppearTreasureBox → Event354 sets spawn history true → Event355 sets AppearHookShot
   → Event119/167 transitions to MiniGame_DampeRace_TreasureBoxAppear. This first-prize arm has **no
   one-minute time test**. The finish/course gates are native; the world location keeps its existing `True`
   rule inside the already adult/Hookshot-gated grave.
8. `MiniGame_DampeRace_OpenGoalTBox`: Event114 → Event241 identifies AppearHookShot → Event66 runs
   the ordinary big-chest get → Event121/198 → Event201 sets OpenedHookShot. The ordinary chest contract
   is the permanent Struct Bool `IsTreasureBoxOpen.16041366920820397198`, not the transient treasure enum
   or `HavePlayedEvent.MiniGame_DampeRace_OpenGoalTBox` (explicitly cleared on ready).
9. Native second-prize creation is Event372/428/453 → DampeRace_TreasureBoxHeartPiece → Event368/364/367;
   the usual time/heart-owned checks and chest-open path stay intact. After the first chest opens, the native
   counter increments and Event275's native branch resumes. A prior second-race save keeps its count and
   HeartGeted; recovering the first chest does not reset its second prize.

### Repair decisions (proposed by cs22a)

- Use the existing chest-open Bool, not a new flag: it records actual collection, survives leaving/reloading,
  and distinguishes an unopened spawned chest. Spawn history is true before opening and reset on first start;
  clear count records second races, not first-prize collection. Neither satisfies the requested invariant.
- Retarget the eleven native item selectors above and Event277 to this Bool, retaining native case targets.
  Result gets one local Bool gate: unopened → Event277, opened → native Event275. Thus ClearCount 2 and
  HeartGeted true cannot suppress recovery, and an unopened chest can be earned again.
- Guard Event97/132 with native strict-after Forest Step02/Step03 expressions, preserving their original
  actions for early/equal steps but skipping a rollback when later. Owning an item elsewhere must not rewind
  the Forest quest merely because first-race dialogue/start is now reachable.
- First-mode start clears existing `UnderTheGrave_DampeRace_SecondRace_More` before Event187. Native
  Event188 sets it true on the second-mode tail and nothing on the first tail clears it; re-entering that tail
  on an old save must not retain second-finish presentation. Its native metadata is saved Bool/reset 8/file 0.
  ClearCount, HeartGeted and both chest-open flags are not reset.
- No new saved flag, chest, grant window, placement file, resource dependency or setting. The safety wrappers
  remain item-based admission checks; only native prize/mode selectors become chest-based.
- Native GameData confirms chest Struct member hash 2091338669 → Bool leaf hash 3213152408, default false,
  reset 24, save file 0. Forest strict-after expressions already exist: each reads Step_SageOfForest (hash
  2841849034) and its target step, so no expression or GameData resource is added.


## Verification ledger

- Initial focused run: 51 passed, 1 failed. Printed native Result nodes Event359/360/303 and replay state.
  The test interpreter had Int equal/less reversed; native cases are less/equal/greater = 0/1/2
  (also anchored by the final-trial decrement's existing dump test). Corrected the helper, not game code.
- Next run: 63 passed, 5 failed (the same shared replay assertion in direct + four production recipes).
  Printed the native repeat-prize trace: with a zero best-time fixture, 0:55 is not a record, so an owned
  Heart Piece leads to native AppearRupeeLow, not AppearRupee. Corrected that exact expectation.
- Recovery review then caught native SecondRace_More persisting true on old saves. First start now clears
  that existing mode Bool; replay begins with it true and proves first-mode finish state false.
- Scoped Ruff format/check: passed after applying the exact reported line wrapping with anchored edits.
  No formatter rewrote repository files.


## No-tool refusal: Kareem's choice, 2026-11-24

**Played defect evidence, not repair proof:** Kareem reported two streamers racing a Clawshot seed live
(about 1,000 viewers, four hours in) being confused when accepting Dampé's race without the Hookshot faded
to black instead of starting. They understood only after Kareem explained. In 0.2.7 the native Talk_01
("On your mark...") and move-to-start still precede Clawshot's silent no-tool surface return.

Kareem chose option 2: native Dampé dialogue UI with this exact English line:

> Come back with a Hookshot or Longshot. There's no climbing out of here without one.

The other 15 language archives use our supplied translations/English regional wording, **not native
Nintendo dialogue or verified translations**. No new art, runtime hook, setting or saved flag.

Claude's latest dependency correction: keep the play-held branch unmerged. Add refusal atop
`a7ab10ca3dc0` on `r22/dampe`, not on main. Gate the new head at the end of the queue (requested line 10);
that gate covers merge after play. The earlier post-merge/new-branch plan is superseded.

- Gate the Ready talk immediately after Event109 InitTalk, before Event59 treasure reset, offer-history
  writes, either acceptance speech (Talk_01/Talk_33), or MovetoStartPoint. Thus refusal changes no
  flow-managed race, talk-history, quest or treasure flag; a later held-tool visit starts normally.
- Held Hookshot or Longshot continues to the original reset, selector, speech, positioning and race mode.
- Neither tool runs one waited native EventTalk, then the existing fade-out/surface warp/fade-in. Ready
  and Start keep their backup guards, now sharing the same explained return.
- Append one label in the existing Dampé MSBT through the existing localized archive/style pipeline;
  preserve native dialogue and unrelated messages.

### One final-file play packet

Kareem plays once, after the refusal commit, with the same final flow in all arms. Controls are optional.
Keep the existing B packet unplayed and unchanged; its old flow is not a play target. Build A launchers fresh.

1. A-candidate, one continuous run: start naturally adult with neither tool and no races; talk to Dampé,
   read refusal and confirm surface return. Naturally collect the private seed's Hookshot from the Goron
   City grotto right sign-puzzle pedestal chest, then return to Dampé. Win the first race; leave its chest
   unopened and retry; collect it; then start/finish the second race. No save editing or second A save.
2. B-candidate: copy Kareem's after-both-races save; pull the sword naturally, recover the first prize,
   and check that already-collected second-prize state is retained.

The r16 song-primed fixture is excluded (Claude). A uses the original main first-adult backup:
`save-backups/2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001/slot_01`,
SHA256 `e63eba9d8173c7c03e1e5338c48ec2dc90cbd2f9b2cad1e487022d5cb46c761c`.
Played provenance: `plans/playtest/answers.md`, R8-PEDESTAL; `r18-equipment.md:27` confirms natural adult.
Direct reader: adult, Hookshot/Longshot false/stock 0, count 0, both prizes unopened, first spawn false,
HeartGeted false, and GC right chest unopened. Ocarina of Time stock 1 and Time song acquired, enabling
the native grotto route. No new start-item/free-travel setting or private placement change is needed.
Both arms use identical final mod bytes and Settings(); the old B packet remains untouched.
Estimated, not measured: combined play 30–40 minutes, including GC acquisition and B's natural sword pull.

Claude boot-checks after READY. Runtime mod-load log plus Kareem's gameplay result are still required;
flow replay, MSBT read-back and boot alone do not prove the UI or repair in game.

### Gate receipt for the pre-refusal head

`a7ab10ca3dc0`: format/lint passed; synthetic `4398 passed, 844 skipped` in 750.97 seconds,
`-n 8`, `CLAWSHOT_WORKERS=4`. Authorized restarted dump gate `842 passed, 24 warnings` in 4428 seconds,
`-n 8`, `CLAWSHOT_WORKERS=3`; all three dump variables were scoped to the dump command.
Lock released at 17:03. Claude's headless bootcheck was excluded from player-process detection.
These results do not certify the subsequent refusal commit.

### Current-dump graph closure

External, unmodified AINB decoder used only outside this MIT repository. Current dump confirms
UnderTheGrave_Prefab_6971 node81 binds the first chest Hash 16041366920820397198. Its creation chain
reads AppearHookShot/OpenedHookShot and native appearance/opened signals, not Hookshot ownership.
EventSetting maps MiniGame_DampeRace_TreasureBoxAppear to TreasureBox_Appearance; Event332 sets the
appearance signal. The ownership check in 6971 advances Forest Step03 to Step04 only.

UnderTheGrave_Prefab_0a7f's ownership check gates an approach callback, not racing or prizes:
Npc_Hylia_Dampe_002_Adult_Callback_01 -> GimmickFlow_GraveYard:Dampe_002_Callback_01, ordinary Talk_22
and a callback Bool. It grants nothing and changes neither race mode nor prize state.
Full factual trace: `work/r22-dampe/native-graph-facts-cs22a.md`; decoded game data stays outside the repo.

### Refusal focused proof

- Scoped Ruff format/check passed for the five changed Python files.
- Initial focused run: 52 passed, 1 failed. Printed JPja's donor/refusal prefixes: the refusal starts
  with a highlighted tool name, so its leading tags include the intended highlight after the voice.
  Corrected the test's whole-prefix equality to compare the preserved donor voice; no UI/source change.
- Cause-aimed rerun: **96 passed in 166.54 seconds**, `-n 2`, `CLAWSHOT_WORKERS=1`, with the three dump
  variables scoped to that command. Covered safety, full first/retry/second race replay, all 16 localized
  archives, shared hint/key/Sheik text, and all production event-registration recipes.
- No-tool replay leaves the complete modeled state unchanged. Subsequent natural Hookshot and Longshot
  acquisition both enable first-race completion/prize, including native actor talk-history variants.
  Held-tool first/second race action sequences and state match the pre-refusal flow.
- Final packet target is `work/r22-dampe/final/`; its public writer/read-back and dry-run receipts live
  outside the repository. Full new-head gate is queued at line 10, after cs22f; not claimed by this focus.
  No game launch or visual/play pass is claimed.
