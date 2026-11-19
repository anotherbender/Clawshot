# Round 18 Track G — story flows (cs18g)

Agent/model: `openai-codex/gpt-6.1-sol`; branch `r18/story`; starting main `2ba2f9a`.
Status: built, unplayed. Exact-head release status is governed by `final-gate-proof.json` and the release criterion below.

## Requested scope and provenance

Kareem's 2026-11-18 play observations are the repros: missing-ocarina Minuet cannot accept shoulder notes;
Dampé's shuffled race can trap an adult without a Hookshot; Kaepora still speaks at four sites despite the skip.
He wants optional skip-button dialogue, not missing Talon/Zelda/Impa/Saria encounters. Pedestal Rauru/Sheik belong
to Track E. Intake read from the private round directory; no played seed contents read.

## Song lesson safety

`patch/song_learning.py` applies independently of Gift shuffle and fast-start choices. Shared
`Dm_SY_Ocarina:LearningOcarinaFollowExample` still binds the performer. It then tests
`IsGet.Item_Ocarina_Time`: owned takes the untouched native fork at either age. Fairy Ocarina ownership counts
only when `Sequence_IsChildhood` is true; otherwise it takes the native return join. The entire interactive
fork is bypassed, **not just the note-input leaf**: leaving
its parallel free-playing pose running could itself hang. The demonstration, automatic song performance,
message cleanup, native/shared grant and the caller's actual (possibly shuffled) grant remain unchanged.

Native evidence, build `e0f3ccfa`: entry setup `Event175` (index178) originally reaches fork `Event38` (index11),
join `Event37` (index10). Bypassed actions are only learning input, empty dialogue, player look lock and
free-playing pose; the transform refuses any other effect/branch in that region. No GameData write or grant
is bypassed. The shared entry is called by all twelve song families (Sun has two calls), not Scarecrow's
free-form learning. Every native event/index and entry remains; only the setup's next and three appended
ownership/age queries differ. Automatic-play grants remain subject to existing Gift-shuffle suppression, unchanged.

## Optional story speech

`skippable_story=false` by default, separate from fast-start; CLI `--skippable-story` /
`--no-skippable-story`, CS1 and app switch. No logic or placement rule changes.

Native mechanism: `EventSystemActor.EventTriggerSkipAcceptStart` with `SpecialEventActionType=3`, and
`EventTriggerSkipEnd` with `SpecialEventActionType=4` (`FadeInType=0`), as used in Great Fairy flows; Water Temple
flows use the same actions. The default EventSetting component lists for these scenes do not disable skipping.
The new transform brackets only linear, non-choice `EventTalk` / `EventTalkIgnoreSameTalkAS` chains.
Every encounter, choice, animation/cut, item grant and flag write stays outside each skip region. All incoming
edges still reach the original index, which now opens the region; no entry/subflow registration changes.

| Encounter | Effective native flow | What remains outside speech regions |
|---|---|---|
| Talon wake-up | `Dm_HrlCastle_0020.110` | Castle Step04, Malon disappearance, `Talon_AfterWakeUp`, progress UI and NPC talk-count action |
| Zelda before/after movies | `Dm_HrlCastle_0035`, `Dm_HrlCastle_0050` | All choice menus/branches, `ThatsallTalk` writes, Letter grant and caller quest transitions |
| Impa lesson / Field send-off | `Dm_MelodyGet_Zelda`, `Dm_HrlField_0020` | Lullaby/shuffled grant, note-count action, native send-off completion and caller clock repairs |

Choices deliberately still require an answer; enabling skip does not silently pick one. Individual speech spans
rather than an entire encounter are the skip unit. Runtime button/fade/parallel-animation behavior remains a
play acceptance check, not an automated claim.

## Dampé physical safety

Track A supplied the boundary evidence: the starting shutter opens only during `Playing`/`PlayingSecond`;
both prizes lie beyond the goal shutter; the forward target and upper windmill exit require a Hookshot.
The race's `4`/`5`/`6` resets are below the one-way descent. A bare start refusal would therefore be unsafe.

Preferred implementation: `patch/dampe_safety.py` gates both shared `MiniGame_DampeRace_Ready` and
`MiniGame_DampeRace_Start` before their original first action. Native `EventQueryIsExistInPouch` checks
`Item_Hookshot` OR `Item_Longshot`. Owned takes the exact original path. Neither uses native fade-out,
`EventPlayerWarpToStarterLinkAnchor`, fade-in actions, with the warp retargeted from reset `4` to existing
surface `StartPos` **`GraveYard_KakarikoSide`**, Hash98411543249690399. No race/timer, grant, quest or save
write lies in the refusal path. The normal NPC ready/retry callers terminate after the guarded Ready call.
Every original event and all other entries remain unchanged. No new placement, geometry, actor or flag.
This is a start gate plus a necessary safe refusal return, not an inventory grant or a completed race.

Fallback evaluated, not selected: hold the first prize to Progressive Hookshot. Its native first reward
`Item_Hookshot`, chest Hash16041366920820397198, is why vanilla always has an escape tool after the first race.
The fallback would require pinning that source while retaining the progressive dispatcher/no-downgrade behavior;
it would reduce shuffle freedom and not itself prevent entry into the lower lobby. The explicit admission/
surface-return gate preserves both shuffled prizes. If play rejects the anchor-return protocol, this fallback
must replace it before merge; there is no claimed automatic fallback or shipped fixed-prize change.
Track A's conservative entry/exit rules remain separate; this patch does not relax them.

## Kaepora audit and safe extension

With `kaepora` selected, nine later flows omit **only the owl's non-choice speech**. Scenes still start and
complete natively, so automatic played history and actor meeting state are not forged. Stable event-name
projection proves every other action, branch, subflow, parameter and continuation survives. NPC flight choices
remain yes/no, using their native shorter repeat prompt; their destination/conditions remain unchanged.

| Reported site | Native flow | State / skipping decision |
|---|---|---|
| Kakariko approach before castle | `Dm_HrlField_0030` | No explicit saved/quest/map write. Native `HavePlayedEvent` and meeting lifecycle remain; owl speech omitted. Neither clock A nor S is written. |
| First child castle, before Malon | `Dm_HrlCastle_0000` | `Event13` opens Hyrule Castle's location UI, supplying its visit/map state. Retained exactly, with native history; speech omitted. No A/S write. |
| Lake approach | `Dm_HrlField_0050` | No explicit saved/quest/map write; native history retained. Speech omitted; no A/S write. |
| Lake talk/flight NPC | `Npc_Kaepora_LakeHylia` | `NPC_LakeHrl_0010_JustBeforeTalk` writes Event35/37 retained; both `Dm_LakeHrl_0010`/`0011` transitions retained, with offers. No A/S or map-visit write. |
| Death Mountain summit NPC | `Npc_Kaepora_DeathMountainTrail` | Talk_Event1/2/46 `HaveTalked_Special` writes (Event19/9/48/50), GlassTruth flag Event7, Din's-Fire query, flight transition Event5 and Kakariko reservation Event45 all retained. **Flight remains available.** No A/S or map-visit write. |

The same safe omission also covers valley approach `Dm_HrlField_0040`, later Lost Woods `Dm_LostWood_0000`,
and Zora River `Dm_ZoraRiver_0000`/`0005`: no explicit saved/quest/map write removed. Mask/Lens responses by
`Npc_EventStarter` remain. The old first-Field skip's A/music/visit preservation and real Impa send-off S are
unchanged. Research ledgers stay private under `work/r18-story/owls/`.

## Verification so far

`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest tests/test_song_learning.py tests/test_story_dialogue.py tests/test_settings.py tests/test_app.py -q`:
**43 passed in13.46s**. Includes supported-dump song exact-tree delta oracle and all six speech-flow region audits:
no skip region contains a grant, flag action, branch, subflow or choice; all non-speech events and entries equal
native. Synthetic no-/Fairy-/Time-ocarina branches exercise the whole-fork distinction.

Integrated focused run (all four new modules and `test_fast_start*.py`, real dump):
**103 passed,1 failed in143.17s**. Failure was the new anchor test indexing native `Translate` as a map.
Printed the real anchor (list, Y98.0143), corrected only that assertion; **7 Dampé tests passed in0.31s**.
All eight new Python files then passed scoped Ruff format/check. No production behavior changed for this fix.
Actual isolated browser UI showed the default-off switch, enabled it, and displayed the updated CS1/help without
opening player seed roots. Actual CLI on/off replay returned the enabled CS1 and then `CS1` defaults.

**Claude's 2026-11-18 steer supersedes the300-seed sweep:** no placement/logic change. Instead prove ten
production on/off pairs (five broad, five Recommended), then one full gate. Exact raw spoiler identity cannot
coexist with honest option/CS1 provenance; retain those fields and compare every other field byte-equivalently.
Only the five current story flows and their required resource-size entries may differ in RomFS; spoiler/play-note
settings provenance must be explicitly accounted for. No unrelated output delta is accepted.

Research scripts and decoded ledgers stay in `E:/OOTRemake/work/r18-story/`, never in this repository.

## Initial packet (withdrawn; historical evidence)

Packet: `E:/OOTRemake/work/r18-story/ingame/STORY-CHECKLIST.md`. Two template-derived rc.7 launchers:
`Test - story-main-control.bat` and `Test - story-candidate.bat`. Each has exactly its own diagnostic mod, no
overlay, and a distinct **initially empty** test-user save folder. Both actual `cmd.exe` dry runs exit0 and
resolve `builds/rc/v3.0.0-rc.7/bin/longshot.exe`; neither starts it. Claude must boot-check; Kareem plays.

Control source is an immutable archive of actual main `2ba2f9a507`; candidate source `580927e66a`.
Both have36 files, identical diagnostic Saria/Impa/Sheik rewards and a blue-rupee first Dampé prize.
`packet-delta-proof.json` proves the only byte differences are our17 flow files and the resource size table.
Both have the same existing forest shortcuts/open-Door setup; these are diagnostic packets, not beatable seeds.

No approved track save copies were supplied. The primary plan therefore starts two New Games: **60–100min
total, unmeasured**; optional later-owl coverage adds10–20min. Child checks take15–25min each, adult checks5–10min
each, flight/reload coverage10–20min. No setup or product answer is needed from Kareem before morning.
The checklist explicitly permits temporary control-only ocarina recovery and later flight-only inventory setup;
neither is represented as natural progression proof. Quest/history/save-state edits remain forbidden.
`report_saved_state.py` reads only these two newly created test-user roots after play; never normal player saves.

All twelve lessons share the statically audited entry; live no-ocarina controls target Impa and Minuet.
The four reported owl sites, real summit flight, Talon/Zelda/Impa/Saria skip-button behavior, grants, histories,
Save/Continue, no-tool surface refusal and Hookshot-positive race remain **unplayed acceptance**, not passes.
If the native warp/fade refusal fails in play, replace it with the documented fixed-prize fallback before merge.

Candidate/main manifests, source archive, file hashes, launcher logs, packet delta proof and all scripts remain
private under `work/r18-story/`. The control deliberately stays on pre-fix main; Track C's fill-only fix does not
change these diagnostic flows. Final gate/head/readiness will be pinned separately after current-main rebase.

## 2026-11-19 gate hold

Claude's new order supersedes the automatic main-change trigger: runner `bg_11` was cancelled while its recorded
state was still `waiting_for_fill_on_main`; it had not acquired the gate lock or run the paired proof.
No gate acquisition, paired generation or full gate is authorized until Claude posts **MAIN FINAL** after
Tracks A/D merge and assigns lock order. Then rebase onto that final main, rerun focused checks, perform the
previously authorized ten on/off pairs and one full gate. Non-lock work only meanwhile.
Implementation/packet commits remain `580927e66a` / `6b88c3c9fa`; **not READY** before those checks complete.

## 2026-11-19 native guard corrections

Fixture research found two errors before any full gate or play claim:

- Native Bool/pouch queries return **0=true/held, 1=false/absent** (`plans/03-game-data.md`, native query conventions).
  Initial song/race guards and their synthetic interpreters all inverted this convention. Initial positive
  test counts therefore did not prove the intended branch semantics. Both production guards and interpreters
  now use the native convention; both-tools race admission is covered as well as either-tool/absent cases.
- Fairy Ocarina is child-only (`plans/04-world-format.md`, section37). A Fairy-only adult is a no-usable-ocarina
  lesson case, even though its ownership/stock are true/1. The shared guard now checks age usability.
  The new regression printed `child=False, Fairy owned, expected_input=False` against the old guard and failed;
  the corrected eight-way age/ownership matrix passes.

After both corrections, `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest
tests/test_song_learning.py tests/test_dampe_safety.py -q`: **18 passed in0.61s**, including native readback/
unchanged-event/surface-anchor oracles. Four-file Ruff format/check pass after correcting one reported format
layout. No unchanged pytest rerun. This is still built, not played; it is not the full gate.

Old candidate `580927e66a` is withdrawn and its launcher removed. Its stored files remain only historical
research evidence, never the new short-packet source. Actual-main control `2ba2f9a` remains valid.
Claude now authorizes selecting earliest qualifying slots under `work/save-backups` read-only with
`clawshot.save`; copy only one slot plus account/options per isolated profile. Never use the current seed or
edit a backup. A single declared test-copy value edit is permitted only if no natural slot satisfies the case.
Natural source predicates, paths/dates and short per-check estimates are being recorded for the replacement packet.

## Saria scope resolved by Claude, 2026-11-19

Kareem meant the **bridge farewell**, not post-Gohma `Dm_Kokiri_0145`. The latter has been removed from the
option; no post-Gohma change is shipped. The initial six-flow counts and old packet labels above are historical,
not proof of the corrected five-flow scope.

Native bridge evidence: `Dm_Kokiri_0150` is a timeline, with13 `VoicePlayActor.EventStartVoice` clips carrying
`IsWaitEnd=true`, and no `EventTalk` actions. `Dm_Kokiri_0155` is its animated grant flow, also with no `EventTalk`;
it includes the real pouch grant at Event68. The proved SkipAccept/SkipEnd implementation brackets linear
non-choice Talk actions only. That proof does **not** establish safe native skipping of the bridge timeline/
gift-animation sequence; blindly wrapping it could omit or reorder the grant/caller continuation.

**Claude's explicit scope decision:** leave the bridge unchanged for round18; round19 replaces the whole
sequence with standard item-get presentation, preserving the same Saria check and grant. This is not a claim
that native timeline skipping is impossible. No unproved timeline skip or grant-suppressing workaround ships.
CLI/app/docs now promise only Talon, child Zelda and Impa speech. Saria's bridge source may still exercise the
existing shuffled Boomerang grant/no-ocarina path; it is not a round18 skip acceptance check.

After narrowing: real-dump story/settings/app focus **38 passed in10.51s**; changed Python files pass scoped
Ruff format/check. Actual CLI help now lists Talon/Zelda/Impa only. Isolated actual browser UI showed default
Off, the revised help explicitly excluding Saria's bridge gift, and native On updated the switch and CS1.
The isolated server/tab were stopped; no player seed root or game process was opened.

## Pre-final packet and selected save provenance

Pre-final entry: `E:/OOTRemake/work/r18-story/ingame/QUICK-CHECKLIST.md`. Its selected archives below remain
the inputs for the required final-head rebuild; **do not boot the old packet in place of that rebuild**.
Old launchers were removed/checklists archived; old test users were not overwritten/deleted.
Pre-final candidate source `48dcae826b`, control `2ba2f9a507`:35 files each, exactly16 flow differences plus
the size table (`packet-v3-delta-proof.json`); no `Dm_Kokiri_0145`. Saria remains outside round18.

Read-only scan:2487 archived progress files/643 distinct contents. Player-seed-labelled backups and contradictory
story state were excluded from selection. For child cases, identical contents use their earliest backup-directory
copy, then candidates sort by original file mtime/path. The short-start predicate (caption/nearby native stage)
is explicit in `fixtures/child-selection.json`; fresh Kokiri starts do not masquerade as close castle fixtures.
Adult ordering is earliest file mtime then path. Both source date and backup-label date are retained.
`fixtures/packet-current-input.json` pins selected input flags/int/enum/hash values; no missing flag is treated as false.

In the following table paths are below `E:/OOTRemake/work/save-backups/`; `U` means the literal directory
`5a3c9e1f0b7d24680000000000000001`. Dates are original progress-file local mtimes, not the backup label.
`H(X)` abbreviates `HavePlayedEvent.Dm_X`; item pairs mean `IsGet.Item_*` / `PouchData.Item_*.StockNum`.

| Check | Exact selected archive slot | Progress date/time | Required input values |
|---|---|---|---|
| Minuet/no usable adult instrument; no-tool Dampé; Longshot-only diagnostic | `2026-11-17_155416-r16-time-walk-songonly-v4-9/U/slot_02` | `2026-11-17T15:54:03-05:00` | Adult; H(TimeTemple_0065)=true; Master Sword owned; Fairy=true/1, Time=false/0; H(MelodyGet_Forest)=false; Storm Song unowned; adult Mido blocker=true. Hookshot=false/0, Longshot=false/0; race Ready, treasure None, clear count0; both prize named Bools=false. |
| Talon | `2026-11-13_133739-r14-story-courtyard-saria-next-7/U/slot_03` | `2026-11-13T13:37:35` | Child, Castle grounds, Weird Egg1/Cucco0; Goto Step03; Talon_AfterWakeUp=false; H(HrlCastle_0020/0035/0050)=false; Letter unowned; Door NotReady; lesson/send-off unplayed; Epona Song unowned. Fairy=true/1, Time=false/0. |
| Both Zelda dialogues | `2026-11-13_134002-r14-story-courtyard-saria-next-9/U/slot_05` | `2026-11-13T13:39:54` | Child, Castle grounds; Goto Step04; Door NotReady; H(HrlCastle_0035/0050)=false; Letter=false/0. |
| Owned-Fairy Impa speech/lesson/send-off | `2026-11-13_134414-r14-story-courtyard-saria-next-11/U/slot_01` | `2026-11-13T13:44:05` | Child, courtyard exit; Goto Complete; Door Step01; Letter=true/1; Fairy=true/1, Time=false/0; lesson/send-off false; Epona Song unowned. |
| Castle owl/banner/map | `2026-11-13_133630-r14-story-courtyard-saria-next-5/U/slot_02` | `2026-11-13T13:36:22` | Child, Market; H(HrlCastle_0000)=false; IsVisitLocation.HyruleCastle=false; Goto Step02_01; Door NotReady. |
| Kakariko/Lake approach owls | `2026-11-11_122357-r12-keygate1-8/U/slot_04` | `2026-11-11T12:23:52` | Child, Field-adjacent; Door NotReady (before Zelda); H(HrlField_0030/0050)=false; Lake visit=false; Castle owl/visit=false. First Field0010 may still play. |
| Summit flight | `2026-11-13_084401-longshot-transferred/slot_03` | `2026-11-13T08:44:01` | Child, Kakariko; Din's Fire=true/1; bombs9; Get_StoneOfFire Complete (gate passed); summit Talk_Event1/2/46=false; H(DeathMtTrail_0030/0035)=false. No new inventory edit needed. |
| Lake NPC offer/flight | `2026-11-13_140428-r14-story-escape-ready-next-2/U/slot_00` | `2026-11-13T14:04:22` | Child, Field-adjacent; Goto Complete; Lake visit=true/from-valley=true; H(TimeTemple_0086)=false; H(LakeHrl_0010/0011)=false; JustBeforeTalk=false. |
| Unedited bridge-to-Impa no-ocarina route (long) | `2026-11-13_132832-r14-story-music-next-2/U/slot_00` | `2026-11-13T13:28:28` | Child; Fairy=false/0, Time=false/0; lesson/send-off/Epona Song unplayed/unowned; no Letter/Zelda history; Door NotReady. Unedited natural route only; not a short courtyard fixture. |

The adult source's first pull, age, ocarina stock and untouched race happened in play, but it is **not pristine**:
its r16 ancestor had Sun/Time song ownership flags added before its played song-only Door opening.
That inherited setup is disclosed, not called an untouched vanilla route. No new copy edits for negative
adult checks; no fake age or first-pull history. Minuet needs teleport past native adult Mido; presentation
coverage only. The old source already had a Fairy Ocarina; its adult unusability is the relevant test.

Only the optional Longshot case retains a new single-value test-copy edit (identical in both variants):

- **Longshot-only:** no natural Longshot-only save exists (0; all48 holders also have Hookshot).
  `PouchData.Item_Longshot.StockNum` Int **0→1**, value offset86700; only byte86700 changes.
  `IsGet.Item_Longshot` remains false: inventory-inconsistent, explicitly diagnostic. Native control must
  establish a usable Longshot/admission first; otherwise invalid fixture, never a patch pass.
- **No-ocarina Impa:** exact native Door=Step01, no usable instrument, unplayed lesson/send-off/Epona and
  metadata yielded **0 eligible natural matches** among185 cached distinct no-ocarina children.
  Receipt: `fixtures/impa-native-step01-absence.json`. A considered Door-only priming copy changed
  NotReady (`0x57b849f0`)→Step01 (`0xeb62add9`) at93156–93159, but was **withdrawn**: it does not remove
  the physical Talon/courtyard barriers. It is not a valid short fixture and its launchers were removed.
  The unedited bridge source remains available for the full native route, **20–30min per variant,
  unmeasured**, not claimed under20min. No second flag/item edit or fake courtyard teleport is hidden.

Pre-final `fixtures/packet-final-input-staging-proof.json` records22 actual cmd dry runs exit0, rc.7.
Two were the subsequently withdrawn priming attempt, not current acceptance cases. Source hashes stayed
unchanged; one slot plus account/options only, captions/metadata equal, declared copy edits isolated.
The read-only reporter confirmed initial enum/stock values, not an in-game result. No game launched.

Fixed-destination metadata in rc.7 `longshot.exe` (read-only file offsets484729176–484731522) names
HyruleCastle→HyruleCastle_Entrance, SacredForestMeadow→OutsideOfForestTemple,
DeathMountainTrail→MountainTrail_KakarikoSide. Arbitrary coordinate/courtyard teleports are not assumed.
Minuet uses the supported Meadow destination then walks into its sensor; summit requires the normal climb.
Short pair estimates remain unmeasured: Talon4–8, Zelda10–16, owned-Fairy Impa8–14, Minuet6–12,
no-tool Dampé6–12, Castle owl4–8, Field owls10–18, summit12–20, Lake flight10–16, optional Longshot6–12.
Use separate short sessions; no claim the complete matrix fits20min. The child no-ocarina natural route
is the explicit longer exception, not silently shortened or called played.
Every played pass still needs runtime loaded-file proof plus the actual outcome and persistence check.

## Complete added-switch polarity ledger

Claude's09:37 instruction requires native evidence and tests for every added switch.
**B:** native `MiniGame_DampeRace/Event50`, `EventQueryIsGameDataBool(HaveTalked...Talk_Event6)`:
case0→Event75 (repeat path), case1→Event49, which sets that same flag true for the first meeting.
**P:** native `ReplaceEquipmentForEraChange/Event12`, `EventQueryIsExistInPouch(Weapon_Shield_Deku,1)`:
case0→Event8 wait/preserve; case1→Event18 clears `PlayerStatus.AnotherEraEquipShield` to empty.
Native race corroboration: Event18(Longshot)0→Event243/1→Event0; Event0(Hookshot)0→Event243/1→Event5 first intro.

| Added switch | Case0 (true/held) | Case1 (false/absent) | Native ABI anchor |
|---|---|---|---|
| ClawshotTimeOcarinaLearning | Native input fork | Fairy query | B |
| ClawshotFairyOcarinaLearning | Child query | Native return join | B |
| ClawshotChildOcarinaLearning | Native input fork | Native return join | B |
| ClawshotDampeHookshotMiniGame_DampeRace_Ready | Original Ready first action | Longshot Ready query | P |
| ClawshotDampeLongshotMiniGame_DampeRace_Ready | Original Ready first action | Surface fade/warp return | P |
| ClawshotDampeHookshotMiniGame_DampeRace_Start | Original Start first action | Longshot Start query | P |
| ClawshotDampeLongshotMiniGame_DampeRace_Start | Original Start first action | Surface fade/warp return | P |

No other switches are added: story speech adds only actions; owl rewrites preserve native query/case values
and redirect only omitted speech edges. Existing native projection/unchanged-event oracles cover those.
New real-dump tests `test_native_bool_query_result_codes_gate_age_usable_playback` and
`test_native_pouch_result_codes_admit_either_tool_before_original_race_actions` assert B/P and exercise the
patched native forks/entries with that ABI; **2 passed,18 deselected in0.43s**, scoped style clean.
The eight age/ownership synthetic cases and eight race entry/tool combinations already passed after correction.
These tests change no production code or packets beyond `48dcae826b`; pre-final staged bytes remain pinned to it.

## Authorized final gate and release criterion

Claude explicitly released **MAIN FINAL `e241a85`**, G first in lock order: rebase, rerun focus, then one
owned lock across the ten-pair identity proof and one full gate. No automatic main-change watcher is used.
The exact frozen head, stage outputs/counts and result are recorded privately in
`E:/OOTRemake/work/r18-story/final-gate-proof.json`; pair details remain in `pair-proof.json`.
**Release criterion, not a pre-test claim:** READY (play-held) only when that exact-head gate record says
passed and all10 identity pairs pass. Gameplay remains unplayed. Post the observed result, release our
lock, then rebuild the short packet from the gated head as Claude ordered; its final manifest/hash proof
is `packet-gated-proof.json`. A missing/failed proof never means READY.
