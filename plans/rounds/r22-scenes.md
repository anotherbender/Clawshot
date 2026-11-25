# Round 22 scenes (cs22e)

Branch `r22/scenes`, base main `2091387`; agent `openai-codex/gpt-6.1-sol`.
Rebased onto main `5bc5577` before FROZEN, retaining its deterministic scrub-shield coverage (no seed re-pin). Rebased product commits: `9e5b97a` gift displays; `4678e95` bridge equipment; `826e726` Talon; `97e0304` native recovery, private caption lifecycle and integration.

## Scope and status

**2026-11-25, Longshot 3.2.0:** moat/Saria heart recovery and Talon's presentation/reward checks **PLAYED PASS**. The pre-Gohma ocarina double persists; both ineffective equipment interventions are withdrawn. Targets **0.2.9**, without rebasing to later main. New full gate required after removal; no sweep.

1. Bind the moat and Saria window-only display steps to their shuffled grants.
2. Trace Talon's milk table prop and prize advertisements; native model substitution if supported, otherwise remove the prop and write neutral Clawshot strings.
3. Document native pre-Gohma Saria's doubled ocarina; withdraw the ineffective stow/apply writer rather than ship inert code.
4. Resolve native healing for silent grants and match native verbs where possible; otherwise explicitly record the remaining issue.

No edits to `patch/getitem.py` or song-get flows owned by PR #41. Changes to shared `patch/gifts.py`/`gift_rules.toml` are display-only. Cross-track integration requests posted on `cs-r22` before shared-file changes.

## Evidence and decisions

Prior evidence: `r21-pr40.md`, proposed round-22 display and Saria fixes; `r21-pr39.md`, presentation findings. Kareem reproduced doubled pre-Gohma Saria with no mod and main in arms 10/11 on **Longshot 3.0.0**, 2026-11-23 (`r21-pr40.md:353-365`). This is not a no-mod 3.2.0 claim; do not repeat as an agent-side reproduction.

Research scripts and decoded facts stay outside the repository at `E:/OOTRemake/work/r22-scenes/`. GameData layout reference: sloperinaGZ `docs/FINDINGS.md`, section 1, read from `work/refs/sloperina-FINDINGS.md` (GPL, facts only; no source reused).

Native display event shape cannot be verified by the dump-free `gifts.loads(text)` API. Proposed implementation: loads validates display references; application validates exact `GetPouchContent:DisplayGetByActorName` and literal vanilla `ActorName` against the grant, refusing mismatches. Raw progressive copies are chest-only under the current contract, so no independent scene tier resolution is introduced.

Implemented display bindings: `HF Ocarina of Time Item` → `Dm_MelodyGet_Time/Event229`; `LW Gift from Saria` → `Dm_Kokiri_0155/Event77`. Gift transforms rewrite only each existing native window's `ActorName`, using the same actor as the silent grant; native ocarina props stay untouched. Literal mismatches, other subflows and argument-valued actors are refused.

**Withdrawn after failed v1/v2 play:** `patch/saria_equipment.py` stowed bridge `Npc_Kokiri_Saria_Child [KokiriForest_ArriveLostWood]` via `EventTriggerChangeAIScheduleEquipState {EquipState: 0}` before Event3/7, with immediate application added in `963d113`. Both attempts had no visible effect. The entire writer, registration and exclusive tests are removed; this historical description is not a shipped fix.

Working-set coverage: `pack/resources.toml` already includes `Event/EventFlow/*.bfevfl.zs`; both display flows, Saria's now-always-written flow and the native action donor are in that existing list. No new native input outside the working set yet.

Claude confirmed PR #41 `e0156b7` changes no flowcharts; these native display edits do not overlap it. Only registration additions in `patch/__init__.py` are shared. Proceeding without waiting for #41; `patch/getitem.py` and `patch/songs.py` remain untouched.

### Talon's Cucco first-prize presentation

Native trace: `Minigame_FindOutCucco/Event23` is the first prize, gated by `IsClear_Minigame_FindOutCucco`; Event304 is the genuine repeat milk refill and Event244 the genuine 30-rupee milk sale. The table prop is `Item_OrnamentalBottle_Milk`, Name `LonLon_Milk`, Hash `11457557478267217151` in `Banc/HyruleField/HyruleField_Child_Static.bcett.byml.zs`; Talon Hash `13992935491369868918` has its sole Reference link. Static scan found no native arbitrary-item table display; this is the only placed `Item_*` prop and only `Item_Ornamental*` actor pack.

`patch/talon.py`, only for a first reward other than native `Bottle with Milk`: remove the prop plus that link, bypass Event340/125/341's look-at/camera/milk-description beat and Event413's recap, by redirecting Event263/Event315. No grant, completion flag, sale or repeat-reward change. `Talk_29` and `Talk_09_2` use neutral Clawshot text; `Talk_28` describes the still-real 30-rupee milk sale without assuming the shuffled prize was a bottle. English in all 16 language archives, preserving opening voice/expression tags; no game text/art copied into source.

Decision proposed by cs22e: remove the prop for the whole seed, including after winning, rather than invent a physics-prop Presence condition just to restore milk later. This is the user's authorized removal fallback, not a new model or item restriction. Remaining unverified cosmetic surface: Talon's authored hand-over animation may still mime a milk bottle; no table-model substitute is created. Full trace is external `talon-findings.md`.

The separate Talon transform composes after gifts and before source-bound compilers; it does not overwrite gifts' flow or Skulltula hint transforms. Native inputs are already in the Banc/Event/Mals working-set patterns. Its event writer is covered by the broad production recipe.

### Original native recovery investigation (superseded by the played count correction below)

Native `Dm_SY_Get:CheckHeart` is the appropriate verb: twelve `Dm_SY_GetInEvent` callers invoke it immediately after their grant (e.g. Event29→Event342, Event90→Event386). It contains no grant, get window, model or autosave. Its heart path reserves the gauge, shows it, waits 30 frames, invokes `PouchSystemActor.EventTriggerRecoverByCureItem {ActorName}`, waits 3 frames, then starts recovery alongside a 120-frame wait. No forced unconditional `HealLifeMax` is used.

- **Piece of Heart (all four counts) and Heart Container:** native HeartPiece/HeartContainer classification selects that recovery path. Fourth-piece conversion is not in this subflow [inference: handled by the pouch add].
- **Recovery hearts and magic jars:** native `EventQueryIsRecoverHeartOrMpActor` selects recovery [inference from the code-level predicate and existing receive-event use]; native CureParam values are one heart, 60 MP (small), 120 MP (large).
- **Fairy:** excluded by this subflow's fairy query; this does not say the fairy's separate pickup/auto-revive code cannot heal.
- **Spells, single/double Magic Meter, Double Defense, ocarinas and other non-cures:** no generic recovery actions in this path. Great Fairy meter animations are separate, not a reason to heal every gift.

`patch/scene_gifts.py` appends the native CheckHeart call after the moat's window and after Saria's silent add, using the actual grant actor. Relevant entry-point subflow indices and the two `GameAnalyzedEventInfo` rows declare `Dm_SY_Get`. The native scene grant timing stays unchanged. `Clawshot_SceneGet` now also calls CheckHeart after its ordinary safe grants, so the no-ocarina moat and skipped farewell do not lose recovery. In-game recovery timing and heart-gauge visibility remain play-held; heart rewards may extend a scene by the native recovery wait.

**Plan discrepancy and approved correction (Claude, thread 2026-11-24 15:38; provisional, Kareem may overturn):** round 21 said the moat's post-add heart caption was correct. Native ordinary windows instead run before the add, with query cases 0/1/2/3 selecting first/second/third/fourth. The moat adds at scene start. A private `GetPouchContent:ClawshotDisplayHeartPieceAfterGrant` clone rotates post-add cases 0→fourth, 1→first, 2→second, 3→third, and sets the native window target. Only the moat's Piece-of-Heart display calls it; the shared native entry and all native events remain untouched. Saria already displays before adding. The checklist records the count before pickup and the exact message/caption on both arms to settle the inference by play.

The private display clones the native display wrapper, window dispatch and heart-caption entry together. It retains native dialog closing and the post-window history/caption-save tail, rather than jumping directly into caption text. No original event or entry point is rewritten in GetPouchContent.

The recovery consumer reads the gift writer's actual paired native actor, rather than resolving the logical item a second time. This preserves cs22c's Shop-tunic→Obj-grant projection at Saria/the moat; the grant and display must still be literal and agree.

Static qualification to the round-21 display rationale: `GetPouchContent:OpenGetWindow_End` retains history/caption-save actions, and some item-specific windows reach `OpenGetWindow_EarlyFadeOut/Event58`. The correction preserves that native lifecycle rather than inventing a normal get demo in the scene. The staged Piece/Bottle branches are text-only; other reward-specific window/fade combinations are not individually played.

Native trace: external `heal/heal-trace.txt`, `Dm_SY_Get`, `GetPouchContent`, `Dm_SY_GetInEvent`, `PouchSystemActor.event.root.ainb` classification nodes 45/46 and 183/182; PouchActorInfo SpecialDeal 3 (HeartContainer), 9 (HeartPiece). dt-12345's AINB decoder was used unmodified outside the repository, facts only, no GPL source copied. Other bare song-get cutscene grants remain outside this presentation ticket; `getitem.py`/`songs.py` are untouched.


## Verification

- Synthetic, `CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2 tests/test_gifts.py tests/test_gift_display.py tests/test_saria_equipment.py`: **75 passed**.
- Native/synthetic focused, `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2 tests/test_gift_display.py tests/test_saria_equipment.py tests/test_gift_display_dump.py tests/test_saria_equipment_dump.py tests/test_gifts_dump.py`: **28 passed** (125.74 s).
- Ruff format/check clean for the six new/changed gift-display and Saria source/test files after correcting the printed formatting differences.
- Native display scan finds exactly the two declared split gift windows; both vanilla gift transforms are byte-identical; moved grants/windows agree. Saria's native bind is unreachable without traversing stow. Full-gate receipts are per-head (below).
- Default production registration: `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -m dump -n 2 tests/test_event_registration.py -k 'production_seed and defaults'`: **1 passed** (41.08 s), no added dependency gaps.
- Talon synthetic/native and broad registration: `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2 tests/test_talon.py tests/test_talon_dump.py tests/test_event_registration.py -k 'not production_seed or broad'`: **35 passed** (157.55 s), ruff format/check clean.
- Recovery/handoff focused: **93 passed, 1 failed** on first run. The failing new synthetic test changed only its in-memory source, while the fixture builder read the unchanged serialized Boomerang source. Printed values: memory Actor=Obj_Heart_Piece, disk Actor=Item_Boomerang, compiled grant ActorName=Item_Boomerang. The native two-heart display/recovery/dependency test and all native handoff tests passed in that run. Corrected the regression to compile the modified synthetic document directly; targeted regression plus broad production registration then **2 passed** (144.18 s), ruff clean.
- Private caption lifecycle proof, including all four post-add counts and native recovery/dependency composition: **14 passed** (23.25 s). Final actual-native-actor projection edge regression plus caption/recovery dump proof: **15 passed** (19.97 s), ruff clean.
- The first two focused starts had no game process. A later focused stage observed `longshot.exe` and retained the low caps (`-n 2`, workers 1). Every full-gate stage uses the same exact-image check; CIM records command lines but exempts no game process from the low caps. No fill/logic/destination change; no sweep required.
- Final post-rebase complete changed-contract run (13 gift/display/equipment/Talon/recovery/handoff/registration files, native dump enabled): **218 passed** in **345.34 s**, `-n 2` / workers 1. Whole-repo ruff: **574 files already formatted**, **all checks passed**. `post-rebase-focused.txt` is the transcript. Current local main confirmed `5bc5577`; exact-image process probe returned none. No coverage re-pin.

## Staged checks

**READY (play-held) packet posted 2026-11-24 16:14.** Private diagnostics **922501** (Saria Bottle) and **922502** (Saria heart), paired main `2091387` controls and no-mod Saria control. All four outputs have **155 files / 24 raw beatability replay spheres**. All nine launcher dry-runs exited 0 against **Longshot 3.2.0**; `launcher-dry-runs.txt` records the exact user/mod paths. Launcher grep found no `hookshot.exe`; overlay is cleared. No game started by this agent, no original save edit, no staged output rewritten.

Read-only save eligibility: prior round's pre-Gohma New Game save on Link's porch (`work/r21-pr40/saves/pre-gohma-newgame/.../slot_01`) has both ocarina stocks 0, farewell unplayed, max life 12 and heart pieces 0. The natural after-Jabu backup (`save-backups/2026-11-09_0954-main-after-jabu/.../slot_05`) has moat and Talon uncollected, Fairy Ocarina stock 1, max life 24 and heart pieces 0. Farore's Wind stock 0. No save edits needed; healing can be checked by taking damage normally.

First packet construction refused a direct Bottle↔Saria swap: Saria held Fairy Ocarina, while the three Bottle donors were show-item gifts that exclude ocarinas (printed source list in `build-main-v1.log`). A compatible chest supplies a pool-preserving three-location cycle; production admission is not bypassed. Each candidate consumes its control's identical placement file, with `check_beatable` after the diagnostic swaps.

Main control packet `work/r22-scenes/main-v1`: **155 files**, **24 beatability spheres** after the three pool-preserving diagnostic cycles. Parsed written flows show exactly the old display mismatch: moat grants `Obj_Heart_Piece` but displays `Item_Ocarina_Time`; Saria grants `Item_Bottle` but displays `Item_Ocarina_Fairy`; Talon grants `Item_FaroreWind`. Main control remains `2091387`.

Save detail: porch BottleA–E valid count **0**; child river count **2**, Farore stock **0**, **58 rupees**. The Talon checklist has Kareem collect enough rupees normally before paid failure/sale/repeat checks; never edit the save.

`packet-resource-proof-v2.jsonl`: each pair has **235 identical placements / 23 identical serialized progression spheres**, equal placement/sphere digests (**0 differing digests** across the two pairs). Exactly **24 expected presentation resources** differ per pair: Field placement; five event flows (including the safe handoff); the analyzed table; 16 language archives; size table. Read-back confirms both grant/display actors, recovery calls, bridge stow, removed milk prop and all neutral messages. First proof attempt failed only because the comparison helper tried to decompress the raw 6,957-byte AIB sequence (`41494220`); corrected that helper's format branch and reran only the proof, not the successful builds/dry-runs.

### Packet checklist (Longshot 3.2.0; play-held)

Detailed steps and required resource log lines: `E:/OOTRemake/work/r22-scenes/ingame/CHECKLIST.md`. No agent boot or gameplay. Each launcher copies its one source save once into its own `save/` tree and loads only its private mod; the no-mod arm has an empty, runtime-checked mods folder. `HOS_FS_OVERLAY` is cleared. Teleport/clock only; no era, inventory, flag or health cheats. No original save edits.

- **Required first: 05 candidate, moat** (5–7 min): window, count and heal on the natural river save with Fairy stock 1. Take damage normally, collect no other piece. Record **piece count before: ___; health before: ___; exact message/caption: ___; health after: ___**. Baseline 0 pieces; expect first-piece caption, 0→1, recovery, normal scene/lesson exit, no Time Ocarina grant and no repeat after Continue. If optional control 04 is needed, record those same fields there (old Time window/no heal).
- **Required second: 02 candidate, pre-Gohma Saria Bottle + doubled-prop fix** (3–4 min): walk from porch without Gohma; one prop, Bottle window, bottle count 0→1 and no ocarina; Field exit/Continue persist. This one arm covers both presentation fixes.
- **Required third: 09 candidate, Saria recovery** (4–5 min), private **922502**, Piece of Heart instead of Bottle via a pool-preserving shopkeeper swap. Take damage normally before bridge; record count/caption/health. Expect native first-piece window, 0→1 piece, native in-C01 recovery, one prop, next cut and field exit finish, no ocarina or repeat after Continue.
- **Required fourth: 07 candidate, Talon** (10–15 min): empty table, neutral offer/recap, no missing-prop camera beat; decline/fail gives nothing; first win Farore's Wind, bottle count stays two; genuine 30-rupee milk sale and repeat refill work; re-entry/Continue retain once state. Natural 58 rupees: gather at least 70 normally.
- **Optional controls only if a candidate looks wrong:** 04 moat; 01 Saria Bottle/prop, then 03 no-mod only if needed to isolate the remake fault; 08 Saria recovery; 06 Talon. All use the same packet recipe/save as their candidate (03 deliberately has no mod). Preserve both-arm moat before-count/exact-caption records whenever a control is played.

**Required only: 25–35 minutes**, in order **05 → 02 → 09 → 07**. **All nine arms: 40–55 minutes**, longest arm 10–15 minutes. Claude requested optional controls rather than routinely replaying them (2026-11-24). Report unexpected controls, wrong caption, residual gauge, stale hand-over model, hang or missing load proof. **Built, not played**; only Kareem's loading-log-plus-game observation establishes a pass.

## Frozen gate evidence and handoff

Before freezing: current-main rebase and one focused run of all changed gift/scene contracts plus `tests/test_event_registration.py` in the dump tier. No fill, location, destination or logic change: no placement sweep. New native reads/writes are already in the existing pack working-set patterns; the full dump stage includes `tests/test_pack_nup_dump.py` with all three dump variables.

The serialized run writes immutable receipts to `E:/OOTRemake/work/r22-scenes/gate/<FROZEN full head>/receipt.json`, with `format.txt`, `lint.txt`, `synthetic.txt`, `dump.txt`. These contain the exact commands, exit codes, elapsed times and game-process checks. Gate command: `uv run python E:/OOTRemake/work/r22-scenes/run_gate.py <FROZEN full head>`; only after Claude assigns the turn and the previous agent posts LOCK RELEASED. No lock retry loop. Without a game image synthetic uses `-n 8` / workers 4, dump `-n 8` / workers 3. Any exact `hookshot.exe`/`longshot.exe` image, including a bootcheck, drops both to `-n 2` / workers 1.

All four successful stage receipts and the final thread handoff are required for a full-gate claim. Keep this exact frozen head after the gate: its per-head receipts and thread carry final gate results without a later evidence-only commit changing the merge head. Nothing here establishes in-game success; Kareem's required candidate rows remain play-held until reported.

## Played failures and authorized correction (2026-11-24)

Kareem played v1 on **Longshot 3.2.0**, relayed by Claude. Detailed immutable read-only receipt: `work/r22-scenes/played-2026-11-24.md`; extracted save fields and exact candidate load lines: `played-05-02-20261124.json`. No played profile, original save, log or mod was written during inspection.

- **05 moat: window/heal/exit pass; single-grant FAIL.** Input pieces 0, one heart of damage. Correct Piece-of-Heart text and health refill; gauge disappeared before the lesson; scene ended normally. No second get window/notification. But input/private slots 05/00 have 0 pieces and completed slots 01/02 have **2**, not 1; MaxLife 24, Time stock 0, Fairy stock 1, moat false→true. Adjacent song is fixed Song of Time, so treat this as our silent double add. Native load lines: 73 analyzed table, 542 GetPouchContent, 2731 Dm_MelodyGet_Time, 2735 Clawshot_SceneGet. The caption alone does **not** settle the one-ahead question; other counts and main control remain unplayed.
- **02 farewell: Bottle/window/no-ocarina/no-repeat pass; prop FAIL.** Completed slots 02/03 have one Bottle, both ocarina stocks 0, farewell true; source/private slots 01/00 have zero Bottles/farewell false. Load lines: 74 analyzed table, 541 GetPouchContent, 3211 Dm_Kokiri_0155. Kareem clarified **two** props: red pinned to her right hand from the start, plus Fairy in both hands. Intended native order is Fairy alone, hand it over, then reach behind for red. EquipState0 did not achieve that. Earlier inference from the ambiguous “still” that one expected prop remained is withdrawn.
- **09 in progress:** Mido blocks the Deku Babas. Do not open this diagnostic's Kokiri Sword chest (Fairy Ocarina); taking damage from the rolling crawlspace boulder preserves the no-instrument state. No result recorded yet.

Claude authorized fixes on this branch, **re-freeze**, and fresh versioned packets for **only changed arms**, preserving all played v1 artifacts. Old frozen `137f6de` is defective/play-held and must not receive the full gate. Talon07 is unaffected. Actual-player caps remain `-n 2` / workers 1; no sweep while the game runs.

### V2 corrections and focused proof

- `a20e1ab`: already-added `Obj_Heart_Piece`/`Obj_Heart_Container` now use **Player_Event.EventTriggerHealLifeMax**, not CheckHeart's SpecialDeal-coupled heart processing. Eight actual native callers have no params: Defeat_Ganon/Event29, DmF_SY_GameOver/Event65, DoorOfTime/Event70, LinkSleepInBed/Event124/53/304, Npc_Dream/Event52, TriForcePoint/Event28. The ordinary handoff copies DoorOfTime's native player binding (no event model/AS) for this HP-only action. Existing Num1, source grant point and private caption clone stay unchanged. Other recovery actors retain their native cure path.
- `963d113`: Saria's native event root exposes both the one-shot **OneShotAIScheduleOverWriteEquipmentState** and parameterless **EventAIScheduleSetEquipmentState → ExecuteAIScheduleSetEquipmentState**. V2 sets the override to 0 **then explicitly applies equipment** before Event3/7. The field schedule does not apply its pending write during the movie [inference consistent with the played v1 no-op]; this is now requested directly, without guessing an Accessory1 dynamic-slot enum. Native gift/red prop participation, bone binding and later cuts are unchanged. Visible success remains for Kareem to establish.
- Native pack/EVFL facts: external `heal/player_saria_v2.txt`, `heal/actor-event-v2/`; only unmodified external AINB decoding, no GPL code copied. Native leaf implementation/fourth-piece conversion was not established by a stalled Ghidra analysis (stopped after 25 minutes); no such proof is claimed.
- Corrected native-enabled focus (scene gifts, equipment, handoff, all five production registration cases): **116 passed / 163.16 s**, `-n 2` / workers 1; **574 formatted**, lint clean. `v2-focused.txt`. Updated consumer-state regressions catch the observed second-piece replay and a suspended schedule whose visible accessory remains until immediate application. Removed the misleading action-name-only “CheckHeart has no grant” test.
- Read-only natural-backup search: **2,962 parsed / 0 read errors**. Every three-piece save had already completed the moat; no eligible unedited fourth-piece fixture. No extra arm or save edit added. The 3→fourth/container conversion remains **unplayed**, not declared working from a model test.
- Corrected String64 active-ocarina receipt (`played-05-02-active-20261124.json`): all arm05 slots retain Fairy active; all arm02 slots have no active ocarina. Both retain Time stock 0 and Time IsGet false. The original integer getter's nulls were not interpreted as active-slot absence.

**V2 READY (play-held), 20:39:** fresh `candidate-v2`/`candidate-heart-v2`, each **155 files / 24 replay spheres**; identical v1/main **235 placements / 23 serialized progression spheres** (zero placement/sphere differences). Read-back `packet-v2-resource-proof.jsonl`: exactly **five** v1→v2 changed resources — Clawshot_SceneGet, Dm_Kokiri_0155, Dm_MelodyGet_Time, analyzed table, size table. Talon flow, Field Banc and all 16 language archives are byte-identical, so no Talon recheck.

Only **05b → 02b → 09b**, **15–20 minutes**, longest 7 minutes, with **new v2 mod/profile paths** and `ingame/CHECKLIST-v2.md`. All three approved-template Longshot 3.2.0 launcher dry-runs returned **0** (`launcher-v2-dry-runs.txt`), cleared overlay and selected their one private output. Existing main/no-mod controls and Talon07 stay untouched; every v1 played file is preserved. V2 is **built, not played**. Claude boot-checks first; keep the failed v1 evidence rather than overwriting it.

New exact FROZEN head will include these receipts after the tested product commits above. No main rebase: retained the authorized 5bc5577 provenance despite later MAIN MOVED. Await Claude's revised conditional order/explicit predecessor release; full gate only, no sweep, all stages fixed at **-n 2 / workers 1** under the real-player directive. The old 137f6de gate is superseded.

## Authorized test-only gate repair

The first full gate on `11ddd531bbb76f761ab8f437f152b0bc9ab5f195` passed format/lint, then synthetic stopped with **4448 passed, 848 skipped, 2 failed**. Both public named-key/chest cases lacked the new `DoorOfTime` HP-only donor in their invented world. Adding that wholly synthetic donor exposed unrelated temple/Darunia quest transforms and the empty farewell's cinematic equipment transform; printed payloads identified each native-event requirement. The fixture now explicitly isolates those unrelated writers, as it already does ocarina get-model presentation, while retaining the real named-key, first-weapon bag, handoff and receipt compilers and every existing assertion. No production code, game data, placements, output packets or staged profiles change.

Claude authorized a **test-only successor freeze** above `11ddd53`, retaining the owned lock, with a fresh **whole synthetic** run plus format/lint and dump on the new head; the failed head's receipts remain immutable. This supersedes the preceding real-player fixed-cap note: every stage probes exact game images; game absent means synthetic `-n 8` / workers 4 and dump `-n 8` / workers 3, while any game image drops to `-n 2` / workers 1. All three dump variables are removed before synthetic and restored only for dump. Merge still waits for Kareem's v2 play.

Fixture repair proposed by cs22e; printed-cause isolated public-seed rerun: **2 passed in 0.57 s**, changed-file format and lint clean. These isolated results are not substituted for the authorized new whole synthetic run.

## V2 played acceptance and withdrawn equipment intervention

Kareem's report relayed by Claude, **2026-11-25, Longshot 3.2.0**:

- **05b moat PASS:** one Piece of Heart in inventory and full health.
- **09b Saria heart PASS:** Piece-of-Heart window, immediate full heal, one piece in inventory.
- **07 Talon PASS:** no milk prop or milk/bottle prize wording; declining or failing gives nothing. Winning gives **Farore's Wind**, present in inventory, with **two bottles still owned**. Later dialogue warns that subsequent wins have no prize or offers the real **30-rupee milk sale**; bought milk fills a bottle and drinks normally.
- **02b/09b Saria prop FAIL, unchanged from v1:** the red-gem ocarina is pinned to her right hand from the start while she holds the green-gem Fairy Ocarina in both hands. Close-ups were reported by Kareem; this agent does not claim an independent visual observation. `963d113` had no visible effect.

The Known-issue claim is sourced to the **played** pre-Gohma no-mod/main pair in `plans/rounds/r21-pr40.md:353-365`, not merely Kareem's earlier vanilla memory. Its original arm10 launcher selects **Longshot 3.0.0**, clears overlay and uses `mods/none-empty`; its archived log line12 says `mods: none in .../none-empty` (SHA-256 `71151d53d079b9fca2d00908ad6ab0c86e4adad25b2fcdde486bac53b04eae9d`). The source's actor/schedule trace (`:309-350`) explains a carried accessory alongside the cinematic prop, but the precise engine cause remains an inference. There is no separate no-mod 3.2.0 observation.

**Decision proposed by cs22e under Claude's “no inert code” instruction:** remove the entire unsuccessful equipment writer, not only `963d113`'s apply step and leave the failed v1 stow. Delete both exclusive test files and registration/coverage/mock references. The suspended-schedule model assumed the native command's visible effect; v2 disproves that model, so it is deleted rather than re-pinned. Keep native props/schedule, the played heart/caption corrections, Talon changes and all key/bag/handoff/receipt behavior. The README Known issue now distinguishes native 3.0.0 evidence from persistence in the 3.2.0 candidate.

**No additional play requested:** archived no-mod control already establishes this pre-Gohma issue's native origin. Optional03 could provide a runtime-specific 3.2.0 comparison, but is not necessary to remove the failed intervention; do not interrupt shops. No played profile, save, log, mod or packet is rewritten, and no game is started by the agent. The 3-to-fourth-piece/container edge remains unplayed.

Prior gate **567b58ee67c92b53e2eaef98c55ea0e7e1a40a32** passed: format/lint, **4450 synthetic passed / 848 skipped**, **845 dump passed**; lock released at04:31. Its test-only fixture repair remains. Those immutable receipts are not a gate claim for the subsequent equipment-writer removal; the replacement freeze requires the full serialized gate, without a placement sweep.

Removal focus: **129 passed, 1 failed** in180.51s. Printed broad-registration failure: `master_sword` received an empty `ItemActors` table for `Scrub Business Seed`. The public-key fixture patched the shared loader while `master_sword` was lazily imported; its `from ...items import load as item_actors` retained the fake loader after teardown. Repair scoped the invented empty table to `make_seed`'s local module alias instead, leaving the shared loader untouched. This is test isolation, not a seed re-pin or production actor fallback. A deterministic same-process run of the two public-key cases followed by broad native registration exercises that order.

Ordered fixture-isolation proof: **3 passed / 132.25 s**, one process/workers1, with native dump enabled (public-key cases first, then broad production registration). Changed Python format/lint: **3 files formatted, all checks passed**. `work/r22-scenes/withdraw-stow-focused.txt` preserves the initial printed failure; `withdraw-stow-isolation-proof.txt` preserves its cause-directed correction. No unchanged retry or seed re-pin.

### Read-only durable v2 receipts

`work/r22-scenes/played-v2-20261125.json` records actual typed values, full SHA-256s/mtimes and exact runtime load lines for **all 14 save slots and their 14 save-work counterparts**, plus the two source backups. Every save/work pair is byte-identical; each log ends with window-close and completed file-write shutdown. All three logs identify **Longshot v3.2.0, source1f0bf123**, and exactly one private candidate mod (154 RomFS files). No played file was written.

| Arm | Before/source and early slots | Completed slots | Durable result |
|---|---|---|---|
| 05b moat | source/00/05: pieces0, moat false | 01/02: pieces1, moat true | **0→1**, MaxLife24 unchanged; Fairy stock1/active, Time stock0/IsGet false |
| 09b Saria | source/00/01: pieces0, farewell false | 02/03: pieces1, farewell true | **0→1**, MaxLife12 unchanged; both ocarina stocks0, active empty, Gohma scene false |
| 07 Talon | source/00/01/05: Farore stock0/IsGet false, clear false | 02/03/04: Farore stock1/IsGet true, clear true | **0→1 Farore's Wind**, bottles **2→2**; BottleB Empty in02, Half Milk in03/04; BottleA Bug throughout |

These snapshots support durable grants/counts, not exact refusal/failure timing or visual/heal observations; those are Kareem's report above. In particular, unchanged MaxLife is not evidence of current full health.

Load proof (line numbers in each private profile's `longshot_log.txt`, arrows point into its corresponding candidate's `romfs`): **05b** mod12 (`candidate-v2`), analyzed75, GetPouchContent551, Clawshot_SceneGet7337, Dm_MelodyGet_Time7338; **09b** mod14 (`candidate-heart-v2`), analyzed74, GetPouchContent540, Dm_Kokiri_0155 at3460; **07** mod13 (`candidate-v1`, Talon unchanged across v2), Mals/USen77, Minigame_FindOutCucco1255, HyruleField_Child_Static2089. Complete paths and log hashes are in the JSON receipt.
