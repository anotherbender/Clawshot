# Round 19 Track scenes — cs19a

Agent/model: `openai-codex/gpt-6.1-sol`; branch `r19/scenes`; base `d9deb65`.
Status: staged, not played; corrected-head full gate pending after printed fixture/startup failures. Not READY.
The round overview and this track file were absent at intake; the user brief supplies round scope.

## Mechanism proposed before broad edits

One scene-handoff compiler, driven by entries in a scene data file. Each entry names:

- the stable world check and native grant (`flow/event`), not an item hard-coded in Python;
- the **caller** flow/entry and early cut point before any instrument pose, dialogue or parallel lesson;
- the native continuation after the omitted sequence;
- the ordered native state-write event references to retain, plus explicit histories of omitted event transitions;
- activation: no active age-usable instrument (always enabled), or the separate default-off `skip_saria_farewell` setting.

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

Active instrument means `PlayerStatus.EquipOcarina` **and** the selected instrument's current pouch stock, not
historical `IsGet` or the maximum owned tier. Fairy is permitted only for child; Time at either age. Empty, other,
missing-stock and adult-Fairy selections take plain-get. Queries are shared in `GetPouchContent`, avoiding new
GameData actors in cinematic callers. Native query ABI must be pinned with native examples.
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

No Track A rule relaxation, fill algorithm, placement restriction, location or logic change is planned. Any safe
no-instrument proof will produce a proposal only; logic remains conservatively instrument-gated in this track.
A small Settings-only `generate/fill.py` edit was requested on the thread before touching its owner's file.
The Saria option must round-trip through CLI, CS1, spoiler and the schema-driven app, default off.
Existing `pack/resources.toml` already includes all `Event/EventFlow/*.bfevfl.zs`; any new non-covered input will
be named there and in a private layered fixture, never written into the shared dump.

Required staged Longshot 3.0.0 checks, each with an identical main-control packet: adult Minuet with only Fairy
(control freezes), one child lesson with no instrument, and Saria's bridge with option on. Use natural archived
save copies where possible; disclose at most one unavoidable same-value edit in both arms. No player seed/save
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
