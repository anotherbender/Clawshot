# Round 19 Track scenes — cs19a

Agent/model: `openai-codex/gpt-6.1-sol`; branch `r19/scenes`; current code base `f5c679d` (original base `d9deb65`).
Status: **GATE DONE; candidate boot checks PASS; gameplay pending**. Kareem plays the v2 candidates first; controls optional. READY awaits his play.
The round overview and this track file were absent at intake; the user brief supplies round scope.

## Mechanism proposed before broad edits

One scene-handoff compiler, driven by entries in a scene data file. Each entry names:

- the stable world check and native grant (`flow/event`), not an item hard-coded in Python;
- the **caller** flow/entry and early cut point before any instrument pose, dialogue or parallel lesson;
- the native continuation after the omitted sequence;
- the ordered native state-write event references to retain, plus explicit histories of omitted event transitions;
- activation: both ocarina stocks zero (always enabled), or the separate default-off `skip_saria_farewell` setting.

The caller dispatches to a per-check entry in one generated `Clawshot_SceneGet` flow, registered as an ordinary
`FlowchartEvent` at `PlayerPos`, with no animation resources (native donor: `KokiriForest_ArriveLostWood`).
The omitted cinematic event never starts on this arm. Its Link poses/camera/forks therefore cannot remain
running around the grant. The new normal event calls `GetPouchContent:GetPouchContentByActorName`, the same
shared actor-name get-window and actual pouch-add used by native song checks. No ShowItem performer, AP/runtime
receive event, second grant implementation or cutscene-skip-button wrapper is involved.

The compiler reads the effective source grant after Gift rewrites and calls that shared entry with the actual
placed actor. Ordered effective source writes and omitted histories follow that grant; the caller resumes at its
named native tail. State is not reconstructed from item ownership. New subflow calls are registered in each entry
that reaches them, and both event registries receive the normal event/preload declarations. Usable-instrument
arms retain their entire original caller and cinematic graphs; the added dispatch is outside both.

Current rule (Kareem, 2026-11-20): native lesson if **either** ocarina has pouch stock, at either age.
Selection and historical `IsGet` do not participate. Only zero stock for both instruments takes plain-get.
The original active-selector/child-only-Fairy premise was disproved by the played adult-Fairy Minuet control.
Pouch queries are shared in `GetPouchContent`, avoiding new GameData actors in cinematic callers.
Minuet's early dispatch must precede Event107 `C08-Ocarina-Hold` (`IsWaitEnd=true`), not just Event9's later shared
learning call. All twelve lessons need the same treatment, with Time's two distinct rewards and Sun's multi-file
sequence explicitly represented. Caller quest/send-off/chest continuations remain native.

Saria's option targets the bridge `Dm_Kokiri_0150` timeline **and** `Dm_Kokiri_0155` animated grant, not village
`0145` or the opening-door fast-start setting. Its data entry must bridge both transitions, retain their played
histories and every source write, grant the location's actual reward once, and resume the original caller tail.
Exact admitted identifiers and retained effects are in `src/clawshot/patch/scene_handoffs.toml`.

**Flag wording question (posted to thread):** a shuffled lesson must not also learn its vanilla song. Existing
Gift patches suppress the play-auto song add and redirect Bolero's independent `IsGet` write to scene history.
Proposed interpretation of “keep song learned”: retain those effective writes, learn a song when it is the actual
placed item, and preserve source histories/once/quest writes; do not create a second vanilla-song reward. This
follows the current item/logic contract, not a new pool policy.

### Priority lifecycle correction (Claude/Kareem, before implementation)

The initial 21:26 proposal did not yet establish a safe event context. Claude relayed cs19h's ootrr public-text
audit: a generic get inside Sheik/Great Fairy animation contexts gave **nothing**, and their changelog names a
Bolero crash. The 21:45 caller-boundary/ordinary-event revision above supersedes an in-scene splice. Reaching a
get call is not a grant proof. Synthetic/native focused tests must execute the actual pouch add and assert
ownership/stock effects; staged checks must inspect saved `IsGet` and stock plus the in-game result.

Observed focused proof: `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest
tests/test_scene_handoff.py tests/test_scene_handoff_dump.py -q --tb=short --maxfail=1`:
**55 passed in 15.43s**. Synthetic fixtures exercise selection/age/current-stock and the native pose control.
Real-dump tests serialize and execute the shared native pouch-add after Gift, Door, bag and selector transforms:
all 14 admitted rows, native and moved rewards, actual modeled stock/IsGet, no extra vanilla song, both Time
rewards, source-once replay, and the three early caller targets. Message rendering is deliberately not modeled;
these are data/grant execution proofs, not engine behavior or saved-state/gameplay acceptance.

The first conditional-write regression found a real compiler bug: an omitted native query pin returned from
the whole replacement before granting. Projected callbacks now retain local subflow return boundaries,
including within local calls and retained fork branches; no guessed query-result domains or forced true pins.
Native UI/history operations missing from the diagnostic interpreter were added only after their exact
operation/parameter payloads printed. The final focused run above passed without suppressing unknown operations.

CLI smoke: default false; explicit on -> CS1 -> settings dictionary -> explicit off all passed.
The actual schema-driven browser surface was opened, observed default Off, toggled On and screenshotted;
its isolated library root was `work/r19-scenes/ui-empty-seeds`, never the player's library.

## Scope fences and verification plan

Original scope held Track A unchanged. Kareem's 2026-11-20 follow-up explicitly authorizes removing the
adult Time-only lesson restriction: either ocarina is sufficient; all non-instrument prerequisites stay intact.
A small Settings-only `generate/fill.py` edit was requested on the thread before touching its owner's file.
The Saria option must round-trip through CLI, CS1, spoiler and the schema-driven app, default off.
Existing `pack/resources.toml` already includes all `Event/EventFlow/*.bfevfl.zs`; any new non-covered input will
be named there and in a private layered fixture, never written into the shared dump.

Original staged checks were adult-Fairy Minuet, child no-instrument lesson, and Saria farewell-on.
The Minuet control **did not freeze**: it played the native lesson and gave Boomerang. The replacement packet
uses the same archived adult save, with exactly one stock edit for its missing-instrument arm. No player seed/save
writes. Stage from the current Longshot template; Claude boot-checks and Kareem plays. Exact paths, state
predicates, loaded-file evidence and unmeasured time estimates will be recorded before handoff.

Full gate: rebase to current local main and rerun focus; atomic owned `r19/gate.lock`; Ruff format/check,
synthetic xdist and dump xdist with required RomFS/NUP/layered fixture and stage-start game-process checks.
The user requires sweeps if fill/destinations/locations/logic change; any scope decision and observed counts
will be recorded here. Never label static or automated output as gameplay acceptance.

## Evidence read

`README.md`, `CONTRIBUTING.md`, roadmap index, architecture, orchestration, game-data/world-format specifications,
`decisions.md`, round-18 story/logic/equipment and Master Sword design, and external issue-34 findings.
Key ground truth: round-18 story check12 failed and every late no-ocarina guard was withdrawn; active selector is
separate from ownership. Issue34's accepted receipt fix is already in main and is not a lesson-safety proof.

## Admission details and limits

All twelve no-instrument lessons use the mechanism; Storm has two native callers, making thirteen lesson rows.
Saria farewell is the fourteenth row and is included only when its default-off option is enabled.
The source data records early caller cuts, effective grants, ordered writes, local projected callbacks, source
histories, resume points and (for directly requested Spirit) ordinary-event admission before the cinematic
context exists. The compiler rejects cyclic callbacks, multiple parallel state streams, scoped effect actors,
dynamic rewards and unaudited external effect callbacks rather than inventing behavior.

Notable retained native behavior: Ice Cavern's independent chest finishes before dispatch; its own quest branches
are preserved. Prelude's pre-grant Door progress check remains before the placed reward. Sun preserves the native
age/story/time selection, selected omitted histories and day/night write. Time retains its separate item and song
checks plus the native forward-only aftermath. Saria preserves the bound requester's event Bool before dispatch,
both movie histories after the grant and the effective Door-transformed palette/travel tail at Event218.
The generated ordinary event contains no Link pose/camera/ShowItem performer or cinematic animation resources.

`generate/fill.py` changes only Settings declaration/type checking/serialization; no fill, item destinations,
locations or logic rules change. The new option is carried by CLI, CS1, spoiler and app metadata.
The new output flow is synthesized, not read from a dump. All native donor/caller/callback inputs, including
`Common_Camera_Pln`, are already included by the pack resource list's event-flow glob; its comment now names that
contract. Cache-only package generation includes a new Saria-on mode. No game data belongs in the repository.

## Other scene checks: coverage proposal only

| Scene family | What an additional general skip needs; not implemented |
|---|---|
| Six Sheik songs | The no-instrument arm is admitted now. An optional always-skip/usable-instrument arm would reuse those cuts and effective grants, retain Sheik count/quest/history/cleanup and the Ice chest, and needs each scene's engine grant/persistence check. |
| Great Fairies | Audit each caller before the animation context; normalize its donor-specific GreatFairy handover to an effective literal reward; retain fountain once flags, magic-meter birth/capacity and source quest effects. Prove magic and non-magic shuffled rewards grant outside that context. No new Fairy skip or grant-shape extension here. |
| Rauru at the first pull | Coordinate with Track sword: isolate presentation from the first-pull state machine. Keep sword receipt, real age/era-equipment transition, Rauru's shuffled dungeon reward, Door completion, Sheik admission and SageRoom/Market travel. Never replace the entire first-pull chain with one item call. |
| Impa | Reuse the admitted lesson cut only for an additional usable-instrument skip; keep Letter/courtyard prerequisites and the native NPC/send-off/Field-clock continuation. Skipping the entire encounter needs a separately audited broader cut. |
| Malon | Reuse the admitted lesson boundary, retain Get_Epona completion and the native source guard. A no-instrument staging route cannot assume she will accept an ocarina-show interaction without one. |
| Windmill | Reuse both admitted adult caller boundaries before free play; preserve played/once state, windmill high-speed/slowdown writes and the man-side aftermath. An always-skip arm needs independent usable-instrument controls. |
| Royal tomb | Reuse the admitted early monument call, retaining age/story/time branches, selected multi-file movie histories, time toggle, outer monument completion and autosave. Test both ages and both time divisions before offering general skips. |

**Proposal, not a rule change (cs19a):** after Kareem proves the staged no-instrument grants, source completion,
control behavior and Save/Continue persistence, Track A may consider removing only lessons' instrument
presentation requirement. Retain all real access/song-use requirements and the moat's separate checks.
Current logic remains unchanged; automated execution does not authorize that relaxation.

## Public-text corroboration (facts only)

No ootrr source or diff was opened or copied. Primary pages read:

- [PR #11, Summary/Saria's gift/Tutorials](https://github.com/ootrando/ootrr/pull/11):
  reports a played plain non-ocarina bridge gift, an earlier bridge get-call hang, and a separate first-Field
  ocarina tutorial without an instrument. Its described implementation is not assumed to be Clawshot's.
- [PR #42, story-scene bullets](https://github.com/ootrando/ootrr/pull/42): names Saria's requester Bool,
  both scene flags and Field palette flag; reports moving the presentation/grant to the trigger and keeping
  quest writes. Clawshot retains its own effective native travel/clock tail rather than copying that policy.
- [0.7.0 release description, Fixes](https://github.com/ootrando/ootrr/releases/tag/v0.7.0):
  explicitly names a Sheik-at-Bolero crash and standard-item-get scene replacements. It also says much remains
  unplayed. This is risk evidence, not a grant or gameplay proof for this implementation.

## Staged save inputs and fixture decision

Packet root: `E:/OOTRemake/work/r19-scenes/ingame/`; launchers explicitly pin **Longshot 3.0.0 stable**,
use the current two-depth template finder, unset `HOS_FS_OVERLAY`, and point `HOS_MODS` to one mod only.
No launcher starts a game during preparation. The packet is a forced-assignment diagnostic on archived
checkpoints, not a generated seed, beatability claim or a continued player seed.

Three shared diagnostic assignments in both arms: Forest and Impa -> Boomerang; Saria bridge -> Ocarina of Time.
The Time reward is intentionally non-vanilla at Saria. **[INFERENCE]** its receipt should supply the instrument
for the unrelated native first-Field tutorial; both remain unplayed. No tutorial patch is hidden in this track.
All three target rewards begin unowned with stock zero.

Six isolated users were created, each holding only its selected archived slot plus unchanged account/options.
Source hashes were asserted unchanged. `ingame/save-input-proof.json` records full provenance and field values.

| Check | Archived source below `work/save-backups/` | Input state / edits |
|---|---|---|
| Adult Minuet | `2026-11-17_155416-r16-time-walk-songonly-v4-9/.../slot_02` | Natural adult, active Fairy, Fairy true/1, Time false/0, Forest scene unplayed; no new edits. Its r16 ancestry had Sun/Time ownership priming before the played song-only Door; not called pristine vanilla. |
| Child Impa | `2026-11-13_134414-r14-story-courtyard-saria-next-11/.../slot_01` | Native child courtyard exit, Door Step01, Zelda lesson/send-off unplayed. The one permitted new field edit is Fairy `StockNum` 1->0, value offset **82196**, exactly byte82196 changed, identical in both arms. Active selector Fairy and historical IsGet=true remain, explicitly inventory-inconsistent diagnostic input; Time false/0. No age or story edits. |
| Saria bridge | `2026-11-13_132832-r14-story-music-next-2/.../slot_00` | Natural child, empty selector, both instruments false/0, both bridge histories false; no edits. |

**Fixture choice (cs19a, posted):** round18 established zero natural exact-Step01/no-ocarina courtyard-ready
matches. Use the allowed single stock-field edit, not a second story/age edit or a claimed short natural route.
The unedited long route remains possible in principle but the separate Field tutorial is an additional unproved
hazard; no unsupported teleport through courtyard barriers is prescribed.

The reporter is `E:/OOTRemake/work/r19-scenes/check_packet.py`: input identity checks, and later actual saved
reward stock/IsGet, source histories and runtime `mods: <file> <- <path>` evidence. It never asserts visual
acceptance. Candidate/control launchers and a human checklist accompany the eventual gated mod bytes.

## Pinned code, packet and first gate receipt

Production code head: `979e471c5e59c66a7744b53a37e31c9fb50c9f91`. Explicit rebase onto current local main
`d9deb65cedf841495ef3bbe2fb2d1083fa42bb43` was up to date. Post-rebase focused scene/native/settings/app checks:
**101 passed in 76.36s**. This includes explicit original-request history completion after Spirit's renamed
native child returns; otherwise that usable-instrument arm could leave the original requester active.

Actual public Recommended seed7 smoke, Saria skip on: **311 shuffled checks,174 files written**;
new scene flow present and spoiler setting true. This used the real RomFS and complete downstream key,
progressive, bag, selector, writer and size-table pipeline, not just isolated handoff compilation.

Packet: `work/r19-scenes/ingame/CHECKLIST.md`; **six input identity reports passed and six actual cmd dry runs
exited0**, pinned to Longshot 3.0.0 stable. Controls import the archived main source; candidates the production
head above. Control mods contain10 files, candidate mods22; hashes and imported source paths are recorded in
`packet-build-proof.json`. No game was started. Pair estimates remain unmeasured: Minuet6–12min, Impa8–14min,
Saria6–12min. Do not present their combined matrix as a sub20min check.

First full gate acquired its own lock after Track sword released it. Ruff: **485 files formatted**, lint passed.
Synthetic: **3826 passed,535 skipped,2 failed,1 error in286.69s**. Dump/sweeps did not start.
Receipt/logs: `work/r19-scenes/gate-979e471c5e/`. The runner released only its matching owned lock.

Printed causes and responses (cs19a):

- Both key/bag public-pipeline failures attempted to read missing `AllSage.bfevfl.zs` from an invented, chest-only
  resource fixture. The fixture now supplies one invented scene, ordinary donor registration and actor-name
  entry and selects those synthetic data rows; the real handoff/key/bag compilers still run. No no-op build mock,
  production missing-file fallback or key assertion was introduced. An intermediate fixture attempt printed its
  missing EventSystemActor; adding that explicit synthetic actor fixed it. The two original nodes then passed
  **2/2 in3.46s**.
- App-play setup expired its existing20s worker join while validation was still pending under12-way load.
  The exact isolated node passed **1/1 in19.94s**. Stage-start process evidence includes MsMpEng's roughly805MB
  working set but no readable CPU counter; Defender CPU causation is not established. **[INFERENCE]** startup/load
  sensitivity, not an established scene or app behavior failure. No app code or timeout was changed.

The cause-fixed gate is required; this failed receipt is not renamed a pass.

### Corrected-head native gate findings

Head `80cbbca3c76b09ea47e54633cb09983458bea4a8` rebased cleanly; **60 focused checks passed in30.46s**.
An actual small-keys-anywhere Recommended seed7 additionally compiled **33 named-key bindings**,2912 shared
events and312 shuffled checks against the real RomFS with Saria on. The missing inputs were confined to the
invented fixture; no production missing-file fallback was added.

The corrected full synthetic invocation had **3826 passed,535 skipped,three20s pending-start failures**
(one UI-sharing node and two app-library fixture cases). Those exact three nodes passed in isolation
**3/3 in3.67s** under an owned lock, per the round's startup/load rule. The original invocation remains failed
in its receipt; it is not represented as a clean full-suite run.

The subsequent full native run had **523 passed,9 failed in1984.41s**, no skipped tests. The NUP/cache-only
matrix is among the passed nodes. Sweeps did not start because the runner stopped and released its matching lock.
Receipts: `work/r19-scenes/gate-80cbbca3c7/` and `gate-80cbbca3c7-resume/`.

All nine printed native failures concern test contracts/oracles for the new production flow. Cause-specific
updates (cs19a, posted before editing), with production code unchanged:

- The three seed-writer cases now include generated resources in the exact file set and verify their bytes,
  native absence and exact size-table allocations instead of assuming all output overwrites native files.
- Token tests assert only their own pickup/actor-pack contribution, not that unrelated generated resources
  cannot exist. Every generated file still receives byte/native-absence/allocation checks; archive-member
  allocation checks apply only to actor packs, not EVFL files.
- The shared child Darunia/Saria interpreter now follows real SubFlowSwitch/Return nodes and explicit active
  instrument stock. The meadow positive control supplies a child-usable Fairy selection; source-grant and
  later-Fire non-regression assertions stay intact.
- Raw Gift/Door edits still face the original commutativity oracle. The snapshot scene compiler is explicitly
  ordered after Door, and the test now additionally checks the actual full production order's quest/clock
  outcomes rather than illegally moving that compiler before the source snapshot it consumes.

Revised oracle focus (shared Darunia/Fire synthetic consumers plus native meadow and production-order Door):
**55 passed in118.63s**. The remaining exact-file-set/actor-pack contracts are included in the next native gate.

## Final automated gate — READY, play-held

Tested head: `8c8d90df5c934aa9505ef9bc1b8084c0c834ce76`, rebased onto current local main `d9deb65`.
Required after-rebase focus: **55 passed in117.51s**. Production remains the packet's pinned `979e471c5e`;
subsequent changes are synthetic/native test-contract repairs and this evidence record only.

The owned full gate recorded no running Hookshot/Longshot at each phase. Format: **485 files pass**; lint: pass.
Full synthetic invocation: **3828 passed,535 skipped,one startup error in261.68s**. The sole error was
`test_ui_plan_has_one_mod_private_saves_and_unsets_overlay` at its existing20s join with validation still pending.
Under the round's startup/load rule, that exact node passed alone **1/1 in1.04s** on the same head. The full
invocation remains failed in its original receipt; no timeout or production code was changed.

Full native invocation: **532 passed,zero skipped in1907.81s**, including native-root, NUP/cache-only and
private layered-dump coverage. Pytest used12 workers with `CLAWSHOT_WORKERS=4`; isolated startup used1.

Saria skip was enabled for all three sweep recipes; bounded fill behavior and beatability validation stayed enabled.

| Recipe | Seeds | Exhausted/failed | Fill attempts |
|---|---:|---:|---:|
| Broad | 200 | 0 | 207 |
| Defaults | 50 | 0 | 50 |
| Recommended | 50 | 0 | 52 |

The sweep used12 workers and330.906s of measured sweep time; its enclosing stage took363.469s.
The gate reports `passed` and the owned lock was absent after completion. Receipts, including load/process
snapshots and exact settings strings:

- `E:/OOTRemake/work/r19-scenes/gate-8c8d90df5c/gate-results.json` — original format/lint/full synthetic.
- `E:/OOTRemake/work/r19-scenes/gate-8c8d90df5c-resume/gate-results.json` — exact-node isolation, native and sweep.
- The latter's `sweep/sweep-results.json`, `sweep-rows.jsonl` and `sweep-preparation.json`.

Play handoff: `E:/OOTRemake/work/r19-scenes/ingame/CHECKLIST.md`, with six Longshot3.0.0 launchers for three
candidate/control pairs: adult-Fairy Minuet, child-stock0 Impa and Saria farewell on. Candidate game bytes remain
pinned to `979e471c5e`, controls to `d9deb65`; no production change occurred during fixture repairs. The checklist
discloses the single Impa stock edit, archived-save ancestry, unmeasured per-pair estimates, required loaded-file
lines, real reward stock, source histories, Save/Continue/re-entry and clean native continuation checks.

**No game was launched by cs19a. READY means ready for the staged maintainer play, not gameplay acceptance.**
Claude boot-checks; Kareem verifies visuals/control/persistence. Track A's instrument requirement stays unchanged.
Other scene applicability and required evidence remain listed above, without implementing those broader skips.

## Played results and stock-only correction — 2026-11-20

Kareem reports all three original candidates **PASS**: Minuet immediately gave Boomerang with correct text
and no scene; Impa immediately gave Boomerang without the lesson, then completed the normal Field send-off;
Saria gave Ocarina of Time with correct text and went straight to Field without the farewell. Saria briefly
popping into view is cosmetic. These are Kareem's actual observations, not agent-replayed checks.

The Minuet **control also passed its native lesson with adult Fairy Ocarina** and gave Boomerang. Together
with r18 issue34's adult Sun's Song observation, this disproves this track's original adult-Fairy softlock
premise. Earlier control-freeze predictions and age/selector dispatch descriptions are superseded.
The actual missing-instrument softlock is zero stock of both ocarinas.

Kareem's requested correction: keep encounters with either instrument; check current pouch stock only.
The shared guard now uses two native pouch queries and returns native for either stock>=1, independent
of age, selection and historical ownership. Source grants/continuations and the separate Saria option
are unchanged. The lesson-specific logic overlays likewise admit either ocarina at either age, retaining
their original age/story/combat/source predicates and conservative no-instrument requirement.

Rebuild Minuet in a **fresh** packet: adult Fairy stock1 keeps the native lesson; the same archived save
with exactly one disclosed Fairy `StockNum`1->0 edit takes the normal-get skip. No age, selector, IsGet,
story or Time-stock edits. Old played packets/users and source archives remain untouched.
Corrected dispatch, logic sweep, full gate and Claude's new boot-check remain pending at this entry.

### Corrected focused proof

`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest tests/test_scene_handoff.py
tests/test_scene_handoff_dump.py tests/test_song_lessons.py tests/test_sheik_logic.py
tests/test_dungeon_rewards.py::test_owned_door_is_separate_from_native_completion_readers
tests/test_dungeon_rewards.py::test_completion_overrides_retain_either_ocarina_song_lessons
tests/test_story_steps_darunia.py tests/test_story_steps_fire.py -q --tb=short --maxfail=1`:
**190 passed in21.20s**. Edited Python format/lint checks also pass.

The stock matrix covers child/adult, empty/Fairy/Time/invalid selections and independent stock combinations;
historical Time ownership is deliberately true even for stock0. Real native serialized Minuet routes with adult
Fairy reach the unchanged caller's first `Player_Event` action (`Event26`, `EventTriggerPlayerEventStartWithDrawn`),
not the replacement event. Stock0 reaches the real shared grant path. Existing ordinary grant/once/continuation
checks stay intact. The initial new native positive assertion stopped at that first Player action before the
movie transition; its printed payload identified the correct native boundary, now asserted directly.

Lesson-specific source overlays, Ice/Impa post-lesson events and dungeon-reward/count-bridge rule copies now
accept Fairy as adult. No-instrument lesson refusal and non-instrument prerequisites remain covered.
Ordinary `can_play*`/Mido/warp policy and genuine Door-of-Time item requirements are unchanged; their
age-metadata rationale is not presented as proof that adult Fairy cannot play lessons.

## Corrected gate and Minuet boot-check handoff

**Gated code/merge head: `84e5b261de238af7986264264d019ce9586d19e3`.**
Rebased onto main `f5c679d532b688ea1a98a5ffb158a821454ce07d` (0.2.3); main's withdrawn
`skippable_story` remains hidden and refused at validation. Settings conflicts retained that withdrawal
while adding the separate Saria option; no old speech-skip feature was restored.
Claude explicitly waived another rebase for main's later docs-only `b1aa1a1` audit.
Post-rebase focus: **190 passed in22.30s**. Settings/schema withdrawal coverage: **48 passed in40.20s**.

One owned initial sweep, with Saria skip enabled for all recipes and bounded fill/beatability checks intact:

| Recipe | Seeds passed | Exhausted | Fill attempts |
|---|---:|---:|---:|
| Broad | 200 | 0 | 207 |
| Defaults | 50 | 0 | 50 |
| Recommended | 50 | 0 | 52 |

The sweep measured399.593s (enclosing stage436.031s); it was not repeated after main's docs-only advance
or during the startup isolation continuation. All phase-start game snapshots were empty.
Full format: **484 files pass**; lint: pass. Full synthetic: **3840 passed,536 skipped,one error in272.89s**.
The error was setup of
`tests/test_app_play.py::test_saved_seed_plan_does_not_need_the_original_game_files[deleted]`:
its existing20s join expired with `status=running`, validation still pending. This is the original failed
invocation, not a relabelled green full suite.

Claude reviewed that the Play implementation was untouched and accepted a conditional load diagnosis:
**contention is an inference, not proof**. His condition was three exact-node isolated passes on the same
head, stopping at the first isolated failure without widening the timeout, plus a passing native suite.
All three completed under owned serialization, on `84e5b261`, with `CLAWSHOT_WORKERS=1`:

| Isolated run | Result | Pytest seconds |
|---|---|---:|
| 1, native continuation | PASS | 1.23 |
| 2, retained turn | PASS | 9.86 |
| 3, retained turn | PASS | 1.83 |

No source or timeout edits occurred between these runs. No full synthetic retry was made.
**Full native suite: 533 passed,zero skipped in2154.74s**, including native-root, NUP/cache-only and
private layered-dump coverage. Native used12 pytest workers/internal4; no game was running at stage start.
The turn was retained for runs2–3 as Claude instructed; after they completed, the owned lock was released
and `LOCK RELEASED` was posted before any further gate acquisition. Lacs is next in Claude's ordered queue.

Receipts, with exact commands, environments, settings, individual logs and phase load evidence:

- `E:/OOTRemake/work/r19-scenes/gate-stock-84e5b261de/gate-results.json` — sweep, format, lint, failed full synthetic.
- `E:/OOTRemake/work/r19-scenes/gate-stock-84e5b261de/sweep/sweep-results.json` — all300 successful seed rows.
- `E:/OOTRemake/work/r19-scenes/gate-stock-84e5b261de-resume/gate-results.json` — isolated run1 and full native.
- `E:/OOTRemake/work/r19-scenes/startup-three-84e5b261de/results.json` — all three isolated runs, retaining run1.

### Fresh Minuet packet for Claude

`E:/OOTRemake/work/r19-scenes/ingame-minuet-stock-v2/CHECKLIST.md`
names four Longshot3.0.0 launchers: two input conditions, each with current-main control and corrected candidate.
Controls were rebuilt from an isolated export of `f5c679d`; candidates pin the gated `84e5b261` code.
Both candidates have identical22-file mods; both controls have10-file mods; exactly one mod per launcher.
All **four cmd dry runs and four exact-input reports passed**. No agent started Longshot.

- `fairy-native`: naturally adult, Fairy selected/IsGet=true/stock1, Time false/stock0; **no new save edit**.
  Both control and candidate must keep the native lesson and grant Boomerang with correct text.
- `no-ocarina-skip`: same archived adult input, with **only Fairy StockNum1->0**, identical in control/candidate.
  Exactly byte **82196** differs; selection, historical ownership, age, story and Time stock are unchanged.
  Candidate must skip the lesson and give Boomerang normally. Observe the control's actual old lesson behavior;
  the inconsistent ownership history does not justify promising it must freeze.

`packet-proof.json` pins code, input, mod hashes and the stock edit. The original archive and all earlier
played packets/users were untouched. The source's r16 ancestry includes Sun/Time ownership priming before
its played song-only Door; not called pristine vanilla. Mido still blocks: the disclosed named Meadow
teleport is presentation coverage, not a route-access proof. Unmeasured estimate:6–12min per input condition.
The read-only `check_minuet_stock_v2.py` reports input identity and saved-state/load evidence; after play it
uses the newest saved slot. Songs have no stock field here, so extra vanilla Minuet is checked by IsGet,
not an invented zero-stock requirement.

**READY is for Claude's boot-check, then Kareem's new paired play.** The earlier three played candidate
passes stand; this corrected dispatch has automated routing proof, not a claimed new gameplay pass.
Kareem must see native adult-Fairy versus plain-get stock0, correct item/text/stock, clean controls, source
completion and no duplicate after Save/Continue/re-entry. Saria's brief reported pop-in remains cosmetic and
unchanged. No general encounter skip, generic song-playing/warp relaxation or Door item relaxation was added.

## Claude's v2 boot checks — gameplay still pending

Claude reports both Minuet stock-v2 **candidate boot checks PASS** on Longshot3.0.0:
**27 RomFS entries each, crash0**. This is boot evidence, not observation of the lesson/grant branches.
Scenes gate is ticked DONE; no new gate or sweep is required for this evidence-only update.

Kareem's current list is **candidates first, controls optional**. The v2 checklist reflects that priority.
Claude renamed the old played Minuet launchers under `work/r19-scenes/ingame` to
`OLD v1 (played) - ...`; those names are left intact and must not be confused with the v2 packet.
The corrected code/packet remains pinned to `84e5b261`; no code, saves or mods changed here.
**READY awaits Kareem's v2 play**, including native lesson with Fairy stock1 versus normal-get skip
with both stocks0, correct reward/text, clean controls and persistence. No new gameplay pass is claimed.
