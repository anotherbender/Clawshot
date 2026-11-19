# Round 18 Track G — story flows (cs18g)

Agent/model: `openai-codex/gpt-6.1-sol`; branch `r18/story`; starting main `2ba2f9a`.
Status: implementation frozen at `580927e66a`; **built, not played**. No game launched; no played seed opened or save changed.

## Requested scope and provenance

Kareem's 2026-11-18 play observations are the repros: missing-ocarina Minuet cannot accept shoulder notes;
Dampé's shuffled race can trap an adult without a Hookshot; Kaepora still speaks at four sites despite the skip.
He wants optional skip-button dialogue, not missing Talon/Zelda/Impa/Saria encounters. Pedestal Rauru/Sheik belong
to Track E. Intake read from the private round directory; no played seed contents read.

## Song lesson safety

`patch/song_learning.py` applies independently of Gift shuffle and fast-start choices. Shared
`Dm_SY_Ocarina:LearningOcarinaFollowExample` still binds the performer. It then tests
`IsGet.Item_Ocarina_Fairy` / `IsGet.Item_Ocarina_Time`: either owned takes the untouched native fork; neither goes
to its native return join. The entire interactive fork is bypassed, **not just the note-input leaf**: leaving
its parallel free-playing pose running could itself hang. The demonstration, automatic song performance,
message cleanup, native/shared grant and the caller's actual (possibly shuffled) grant remain unchanged.

Native evidence, build `e0f3ccfa`: entry setup `Event175` (index178) originally reaches fork `Event38` (index11),
join `Event37` (index10). Bypassed actions are only learning input, empty dialogue, player look lock and
free-playing pose; the transform refuses any other effect/branch in that region. No GameData write or grant
is bypassed. The shared entry is called by all twelve song families (Sun has two calls), not Scarecrow's
free-form learning. Every native event/index and entry remains; only the setup's next and two appended ownership
queries differ. Automatic-play grants remain subject to the existing Gift-shuffle suppression, unchanged.

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
| Saria farewell speech | `Dm_Kokiri_0145` | Native encounter/cuts and caller sequence; separate gift flow `Dm_Kokiri_0155` is untouched |

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
Only the six story flows and their required resource-size entries may differ in RomFS; spoiler/play-note
settings provenance must be explicitly accounted for. No unrelated output delta is accepted.

Research scripts and decoded ledgers stay in `E:/OOTRemake/work/r18-story/`, never in this repository.

## Combined staged controls

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
