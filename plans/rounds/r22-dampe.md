# Round 22: Dampé's first race (cs22a)

Branch `r22/dampe`, base `2091387`; model `openai-codex/gpt-6.1-sol`.
Status: A/A2 and B fully played on `09b31db`, including unopened retry; separate progression lift authorized.

## Contract and commit boundary

Kareem's 2026-11-24 report is the reproduction: owning a Hookshot selects the second race, leaving the
first-race chest unavailable. The supplied after-both-races save has clear count 2, first-prize spawn history
false and heart-prize history true. No player seed placements are needed for this repair.

- Select the first race until its own chest is opened, independently of Hookshot tier and prior second races.
- Keep the Hookshot/Longshot admission guard and the native second race after first-chest collection.
- The repair/refusal commits retained `nonprogression_only`. Kareem's full played A/B confirmation on
  2026-11-24 authorizes the final separate lift, with its required 200/50/50 sweep in gate line 10.
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

Kareem played the final flow across A/A2 and B. A2 changed only two private placements; all event resources,
including Dampé, and GameData stayed byte-identical. Original B packet and B profile were unaffected.

1. A/A2, one continuous profile: refusal passed, then the GC route blocked (no remake Time Block).
   A2 moved Hookshot to the closed Shield/ReDead grave chest, swapping junk back to GC. Natural pickup,
   first race/Magic Jar, unopened-chest retry, then second race/Bow and return dialogue all passed.
2. B-candidate: copy Kareem's after-both-races save; pull the sword naturally, recover the first prize,
   and check that already-collected second-prize state is retained.

The r16 song-primed fixture is excluded (Claude). A uses the original main first-adult backup:
`save-backups/2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001/slot_01`,
SHA256 `e63eba9d8173c7c03e1e5338c48ec2dc90cbd2f9b2cad1e487022d5cb46c761c`.
Played provenance: `plans/playtest/answers.md`, R8-PEDESTAL; `r18-equipment.md:27` confirms natural adult.
Direct reader: adult, Hookshot/Longshot false/stock 0, count 0, both prizes unopened, first spawn false,
HeartGeted false, and GC right chest unopened. Ocarina of Time stock 1 and Time song acquired, but the
proposed Time Block route was disproved in play and withdrawn. A2 used the immediately accessible
Shield/ReDead grave (closed, Master Sword stock 1, Sun's Song owned), with no save or settings edits.
Seed 22110101 and Settings() stayed the same; A2 swapped Hookshot with Scrub Business Seed only.

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

## Played results and native saved-state proof — 2026-11-24

Kareem via Claude, Longshot 3.2.0, final `09b31db` flow. Refusal: **“works perfectly.”**
A/A2: with Hookshot, the first race ran and gave Magic Jar; after leaving/returning, the second race gave
“bow”; return dialogue said no more prizes. B: first race offered, Magic Jar, then no-more-prizes dialogue.
These are played results, not conclusions from a boot. The phrase “no more prizes” is the reported dialogue,
not a claim that all native repeat/filler rewards have been disabled.

### Runtime loaded-file proof

All paths below are under `work/r22-dampe/final/ingame/`.

| Played session | Actual log and line | Loaded Dampé resource |
|---|---|---|
| A refusal | `user-dampe-final-22110101-A/longshot_log.txt:1663` | `mods: Event/EventFlow/MiniGame_DampeRace.bfevfl.zs <- .../dampe-final-22110101/...` |
| A2 races | `user-dampe-final-22110101-A/longshot_A2_log.txt:1439` | Same resource from `dampe-a2-22110101` |
| B recovery | `user-dampe-final-22110101-B/longshot_log.txt:2155` | Same resource from `dampe-final-22110101` |

Actual Graveyard Adult Dynamic overrides also appear at A:6725, A2:2170, B:4482 in those respective logs.
Both mods' Dampé SHA256 is `baf862f7715abe5ebfe649c3812b21cf0d7426d7fb6a3f9b08e91b4275efc9c0`.
A2's public-writer/read-back proof confirms all event resources and GameDataList unchanged; no seed marker,
save copy, restore or inventory/age edit was introduced. GC's suspected Hookshot access requirement remains
unverified; only the missing Time Block / failed acquisition route is played evidence.

### Committed saves (read-only native reader)

Permanent first/second chest fields are `IsTreasureBoxOpen.16041366920820397198` and
`IsTreasureBoxOpen.5534919361313859554`. Counts are `MiniGame_DampeRace_ClearCount`.

| Profile snapshot | Saved local time | First open | Second open | Clear count | Hookshot stock | Bow stock | Quiver 40 / 50 |
|---|---|---|---|---|---|---|---|
| A2 before prizes, `slot_02` | 19:05:32 | false | false | 0 | 1 | 0 | 0 / 0 |
| A2 first chest spawned, `slot_03` | 19:08:28 | false | false | 0 | 1 | 0 | 0 / 0 |
| A2 after first chest, `slot_04` | 19:10:59 | true | false | 0 | 1 | 0 | 0 / 0 |
| A2 latest committed, `slot_01` | 19:16:11 | true | true | 1 | 1 | 1 | 0 / 0 |
| B before recovery, `slot_00` | 19:18:26 | false | true | 2 | 1 | 1 | 0 / 0 |
| B latest committed, `slot_02` | 19:23:33 | true | true | 2 | 1 | 1 | 0 / 0 |

Latest A SHA256 `0e3aca2946e0ea37f5b15dbfc8311ef373afec06b567170b9db9d27dbfebf043`;
latest B `7bbae0e6d4575832e44de93372ca1a8f134adb689713ff454f75b3c6192475d2`.
Each latest `save/` file is byte-identical to its corresponding `save-work/` file after graceful process close
(A2 log:23651–23652; B log:13044–13045). All profiles and logs were read only; field report is outside the repo
at `work/r22-dampe/played-save-native-evidence.json`.

**Bow confirmed, not just inferred:** the packet assigns Progressive Quiver. `progressive.py:42–45` maps its
first tier to Bow, granted as Item_Range_Bow and saved under Weapon_Range_Bow. A goes from that weapon's
IsGet=false/stock 0 to true/1 while both medium/large quiver flags and stocks stay false/0. The grant-name
Item_Range_Bow has no independent saved field; a missing field was not treated as false. B already owned Bow
on input and retains it; its second chest and HeartGeted remain true while count stays 2.

### Persistence and unopened retry: limits of the evidence

- Committed disk persistence is confirmed: both permanent chest flags and inventory are in actual `save/`
  files, not just a running process or `save-work/`. A advances count only for the second race; B recovers
  the first prize without resetting/re-awarding the already-collected second prize.
- A distinct in-game Save/Continue or restart after collection is **not established** by these files/logs.
  Both sessions mounted their profile and closed gracefully, but no post-collection reload is logged.
  Do not relabel committed-file proof as a played reload check.
- Unopened retry is **PLAYED PASS**: Kareem explicitly confirmed to Claude on 2026-11-24 that he left the
  first chest unopened and raced again. This supersedes the earlier unreported/model-only assessment and
  closes the native respawn gap; no acceptance waiver or additional replay is needed.
- It also remains covered by `tests/dampe_flow.py:134–176`: CHEST_OPEN=false, win/spawn, retry first
  race/spawn, open, then switch to second. Both tiers/prior-clear states and all production recipes passed
  in the 96-check focus. The modeled replay is corroboration, not the source of the played claim.
- Claude accepted A and B as fully played on the identical final flow and authorized the separate
  progression restriction lift. Durable serialized persistence is proven above; a distinct user
  Save/Continue action is still not independently inferred from the logs.

Played runtime flow remains `09b31db`. The authorized data-only progression lift gets a separate commit
and replaces the gate-line-10 candidate; no rebase onto moved main `a52dc20`. The paired lift sweep uses
the published immutable `5bc5577` baseline, not the moved main.

## Authorized progression lift and queued gate

- Kareem's complete played confirmation authorizes removing only the first chest's `nonprogression_only`
  in `data/world/remake.toml`. Native safety/first-race transforms and every other item/location hold remain.
  Production Defaults/broad-world tests now admit Progressive Hookshot, Quiver and Magic at this chest;
  the generic non-progression rules remain covered by the House-100 and exclusion tests.
- Initial lift focus: 84 passed, 1 failed. Actual Broad dependency/entry checks passed; a static writer
  expectation failed because the changed fill no longer happened to put a shield on a scrub.
- Claude identified the already-landed deterministic fixture in `5bc5577`. Merged exact
  `5bc5577369d429d426dc2059461918e41b5c5302` (merge, not rebase); only `tests/test_event_registration.py`
  changed in the merge. The temporary alternative local fix was reverted entirely before merging.
  No new seed pin or registration allowance was added.
- After that merge: **88 passed in 420.77 seconds**, `-n 2`, `CLAWSHOT_WORKERS=1`, including the previously
  failing Broad contract, all production recipes, first/retry/second recovery, safety and other holds.
  Scoped Ruff format/check passed for the changed/merged Python tests.
- Prepared sweep reuses the published `main-5bc5577-sweep` baseline: exactly 200 Broad, 50 Defaults and
  50 Recommended, seeds `22220000..22220199` / `22220000..22220049`. Metadata verified all 300 baseline
  pairs accepted and exact recipe inputs/effective settings. No seeds were generated by that preflight.
  Candidate digests use the producer's sorted placement-item pairs and canonical sphere JSON.
- The candidate-only sweep checks effective CS1 equality, tracks attempts/exhaustion/digest deltas, and
  requires a nonzero first-chest progression witness. It runs with six workers only under the owned
  line-10 lock, paired with baseline `5bc5577`, never current moved main. No baseline regeneration.
- Gate runner is prepared for that sweep plus format/lint/full synthetic/full dump; three dump variables
  remain confined to the dump command. Player detection excludes Claude's bootchecks; no sweep starts
  with a real player, and game-on test stages cap at `-n 2`/one worker. Failure retains the owned lock for
  diagnosis; successful full completion releases it immediately. No lock or sweep has started yet.

## Line-10 lift gate PASS — 2026-11-25

Claude relayed cs22f's 05:49 PASS/release and authorized line 10. Acquired at 05:50 with explicit Git Bash;
shared lock released at **07:08** after the successful full gate. No rebase or moving-main sweep baseline.

The completed paired sweep used product freeze `70569ae98c289064b32988cce5996d6349028164`, six workers,
and the cached `5bc5577369d429d426dc2059461918e41b5c5302` baseline. **300/300 accepted**, zero exhausted
on either side, in 492.188 seconds. Exact recipe inputs/effective settings matched.

| Recipe | Seeds | Baseline first-attempt failures | Lift first-attempt failures | First-chest progression witnesses |
| --- | ---: | ---: | ---: | ---: |
| Broad | 200 | 0 | 1 | 176 |
| Defaults | 50 | 1 | 2 | 23 |
| Recommended | 50 | 2 | 2 | 31 |

All five candidate first-attempt failures recovered on attempt 2; original FillError payloads remain in
the receipts. Placement and sphere digests changed for all 300 pairs. There were **230 progression
witnesses** at the first chest. No additional generation or unchanged sweep rerun.

Initial whole synthetic gate: 4410 passed, 855 skipped, two failures in the two chest-size variants of
`test_public_seed_preserves_named_key_credit_and_first_weapon_bag`. Their invented archive lacked
`EventFlowMsg/Npc_Hylia_Dampe_002.msbt`, which the real refusal writer requires. Read-only inspection
confirmed that file and its `Talk_37` donor in **all 16 real language archives**; no native text was copied.
Claude authorized adding an entirely invented donor to this fixture only, retaining writer/assertions
and the owned lock, then repeating whole synthetic/format/lint and running dump without repeating sweep.

Test-only successor **`0b4d868297a18d4aef8273009f2381f1b11abda8`** adds four fixture lines; production
files are unchanged from `70569ae98c`. Kept minimal for integration with cs22e's `567b58e` fixture work.
Its full gate passed:

- `uv run ruff format --check`: 566 files already formatted.
- `uv run ruff check`: all checks passed.
- Whole synthetic: **4412 passed, 855 skipped**, 24 warnings, 447.29 seconds; all `OOT_*` unset.
- Whole dump: **853 passed**, 24 warnings, 2999.09 seconds, with the three authorized dump variables.
- Every stage-start player check returned 0. Synthetic: `-n 8`, four workers; dump: `-n 8`, three workers.
- Lock owner checked before release; `LOCK RELEASED` and `GATE PASS` emitted at 07:08.

Receipts (outside repository):
`E:/OOTRemake/work/r22-dampe/gate-70569ae98c289064b32988cce5996d6349028164/sweep/results.json`
and `E:/OOTRemake/work/r22-dampe/gate-0b4d868297a18d4aef8273009f2381f1b11abda8/`
(`format.log`, `lint.log`, `synthetic.log`, `dump.log`, `stages.txt`, `sweep-carried-forward.txt`).
The tested code freeze remains `0b4d868297`; this evidence update is documentation only, not a new code freeze.

## Jabu Compass chest: Ruto hypothesis refuted in play — 2026-11-26

Overnight extension authorized by Claude: new **TEST** seed `2026112512`, public Defaults (`CS1`),
exact main `874f30a24040bbed4ae7223fbfb751fb60174c4d` (Clawshot 0.2.8), Longshot **3.2.0**
(`1f0bf123`). No product edits. Natural child save copied into isolated A/B profiles, **zero save edits**;
Boomerang already owned, room-12 Compass chest unopened. This seed places **Rupees (50)** there,
not a Compass; starting wallet 48/200. Its room-12 opening entry and EventSetting binding remain native.

Kareem's played observations, relayed by Claude, are the presence/reward evidence:

| Arm | Ruto during attempt, reported by Kareem | Played result | Latest committed save | Rupees, baseline → saved |
| --- | --- | --- | --- | --- |
| A | Left outside room 12, in the entryway | Chest opened; purple rupee | `slot_02`, 01:17:58 | 48 → 98 |
| B | Carried into room 12 and set down | Chest opened; purple rupee | `slot_02`, 01:21:37 | 48 → 100 |

Both `checker-last.txt` receipts show `IsTreasureBoxOpen.3510516276638146208=true`,
`InsideJabuJabuBelly_Room12_TBoxDemo=true`, `InsideJabuJabuBelly_Room12_TBoxNearRuto=false`,
room 12 cleared/treasure true, and `IsGet.Obj_Rupee_Purple` false → true.
B's total balance increase is 52, not 50; the extra 2 are not attributed to this chest.
Ruto's saved spawn/liftability is not used as a presence oracle.

Receipts are under `E:/OOTRemake/work/r22-jabu-chest/morning-874f30a/ingame/`,
in `user-jabu-ruto-test-2026112512-A/` and `-B/`. Actual `longshot_log.txt` loaded-file proof:
A/B `InsideJabuJabuBelly_Static.bcett.byml.zs` at lines **555/573**, FocusGimmick **1430/1423**,
big-chest flow **1435/1415**, GetPouchContent **539/561**, NaviChat **5919/4798**.
Both logs line 1 identify Longshot 3.2.0 and line 16 loads exactly this one test mod.
A/B latest save SHA256: `aa6d067083269149023c2cf28ecc9a14210371667f082d5d6fee6d7b41cc8369` /
`34896985c9e11625a40ff9078fae56e93682e385faff0cf263607182318f3b39`.

**Conclusion (Kareem/Claude, corroborated by saved state and runtime loads): Ruto's presence does NOT
gate this chest on exact `874f30a` / Longshot 3.2.0. The “needs Ruto” hypothesis is refuted.**
This is a played purple-rupee case, not certification of every reward, older generator/runtime or save state.
`Event235` participation and `Event243`'s near-Ruto branch alone were not evidence of an opening refusal.
Follow-on failed-VOD investigation is read-only: no lock, seeds, game starts or save/output edits.
