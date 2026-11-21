# Round 20 — trials and token bridge (cs20d)

Branch `r20/trials`; initial base `acbb903`, integrated base `ade62dc`; model `openai-codex/gpt-6.1-sol`.
Research/output: `E:/OOTRemake/work/r20-trials/`. Native dump read-only.
Agent launched no game, wrote no runtime folder, opened no personal seed and changed no original save.
Historical acceptance/staging receipts below are superseded by the current played verdict and follow-up.

**Current played verdict (Kareem via Claude, 2026-11-21):** bridge PASS: closed at15,
native scene at16, persisted; saved stock16, River chest open, bridge history=true.
Zero-trial check is **BLOCKED**: barrier gone, central elevator unavailable. Saved Count0,
all six removals=true, AllBarrierClear=true,0090 history=false. The old checklist's debug-age
toggle left `Sequence_IsChildhood=true`; Claude confirms this known incomplete toggle.
Treat age as a confound, not proof the lift bug is count0. Old assertions below that the
last-core movie was unneeded cover barrier/pots only and are withdrawn for tower access.
Claude cancelled the age-only probe; the next check uses the zero-only history fix and an explicitly approved short two-Bool TEST-COPY, pending restage/boot/gate.

## Requested contract

- Ganon's trials count 0–6; 6/default preserves native behavior. Trace each native saved completion,
  barrier and tower-door predicates before deciding feasibility. Use existing initial values through
  cs20c's `gamedata.FastStartSetting` hook, or patch the condition without new saved flags.
  Partial counts must name the trials remaining in a barrier or hint message.
- Bridge `tokens`: `bridge_count` 0–100, compares native `PouchData.Item_Token_Gold.StockNum`.
  Counts token items, including shuffled chest tokens, never defeated Skulltula sources; spends nothing.
  Default remains `bridge = vanilla`, count0. cs20a informed on `cs-r20` for altar text.
- Sweeps with each new value enabled: broad200, Defaults50, Recommended50, zero exhausted;
  private paired staged checks bridge16 (Claude superseded3 to avoid save edits) and trials0; one serialized exact-head full gate.

## Research prerequisites and coordination

Read README, CONTRIBUTING, roadmap/architecture/orchestration/game-data/world-format/decisions,
round20 ownership, round19 tokens and LACS records, and the public-docs-only feature comparison.
GPL factual reference only: `work/refs/sloperina-FINDINGS.md`, section1 (GameData types, reset/save
metadata, Struct members), section5.7 (upgrades need matching pouch identity), section5.8
(map/compass native flags and menu refresh). No GPL code or OoTR/SoH code used.

cs20c hook confirmed: append `FastStartSetting(name, default=False, skips, state, source,
logic=None, game_data={existing_field: typed_value}, flow_edits=())` to `chosen` before
`gamedata.changes(chosen)`. No separate initial-values writer. Native entries are verified below.
Shared Settings changes are limited to own fields/validation/serialization; fill algorithm untouched.

**Partial-trial selection, provisional decision by Claude (Kareem may overturn in the morning):**
select N remaining trials from a dedicated deterministic seed stream, independent of fill RNG.
Same seed and settings string select the same trials. Spoiler, play note and blocked-barrier
text name them. Count6 stays native; count0 clears all.

Claude approved seed-aware `prepare(..., seed=0)` preview, with actual seed passed by generation
and tracker reconstruction. Required proof: default6 ignores seed and matches main's complete
output hashes on several private seeds; tracker rebuild matches a partial-trials generated world;
spoiler records the selected trials. No player-controlled derived `skipped_trials` override.

## Findings

Read-only native `Defeat_Ganon.bfevfl.zs`: Light/Forest/Water/Shadow/Fire/Spirit
completion writers are Event3/7/11/15/19/23, setting
`InsideGanonCastle_Dungeon_BarrierRemove_<trial> = true`. Each path decrements
`InsideGanonCastle_Dungeon_Barrier_Count` once (Event68/69/70/79/83/93).
GameDataList: all six existing Bools are defaultfalse/reset8/save0; count is
Int default6/reset8/save0. `InsideGanonCastle_IsAllBarrierClear` is defaultfalse/reset8/save0,
written by native Event778; Event606 compares the count to0.

Room01 module `_4ab0` node9 reads Count, node10 compares to0, output2 is **Equal**;
node12 ANDs that equality with node11's current-room query and drives room-step clear (node8).
Room01 `_75af` node6 reads AllBarrierClear and deletes the tower's barrier actor (node0).
Its separate node1 reads `HavePlayedEvent.Dm_InsideGanonCastle_0090` only to create four pots.
Common module `_e780` reads all six removal Bools (nodes30/32/34/36/38/40) to hide their
beams and light their native symbols/tubes. Core-room modules use the same removal state.

The last-core common tail calls `Defeat_Ganon:InsideGanonCastle_Dungeon_BarrierRemove_All`
(Event581). That entry accepts Count<=0 at Event606, sets AllBarrierClear at Event778,
then plays0090 and advances the quest. With zero trials there is **no core to invoke it**.
Corrected hook contract posted to cs20c: skipped removal Bools=true, Count=N, and existing
AllBarrierClear=true **only for N=0**. This deliberately omits the unneeded last-core movie;
no history or quest step is forged. With partial counts, the real final core still owns that scene.
The tower entry shutter references the room1 barrier and its room1 native clear; tower boss-key
door remains a separate key check. This is static data evidence, not played.

Read-only scan of all native EVFL trial-state writers found no false/reset writer:
Defeat_Ganon plus each short core movie only set the corresponding removal Bool true.
The native new-game pouch sequence has no references to these Castle fields. This supports
initial values, not a claim to have exhaustively disassembled runtime writes.

Blocked-barrier message: `Dm_InsideGanonCastle_0003/Event11` asks
`EventFlowMsg/Dm_InsideGanonCastle_0003:Dm_InsideGanonCastle_0003_Text_002_b`.
Both area and door first-view routes invoke that scene. Partial seeds name the selected
remaining trials in this existing message in every language, using existing pagination.
Count0 says no trials remain; count6 changes neither text nor native state.

Token stock: native Struct `PouchData` -> `Item_Token_Gold` -> `StockNum` resolves the
saved Int key0x04735978, default0/reset32/save0. The native BoolExp
`MiniGame_DampeRace_IsClearLeastOnce` uses `NOT(Int < 1)`: op18 reads the Int,
op16 carries an **I32** literal, op5 negates. Token mode mirrors that native shape for
StockNum>=N in one **unsaved** BoolExp, retaining the existing bridge scene/latch and
late Light Arrow story guard. Logic counts `Gold Skulltula Token` items from any supported
source, including chests; it never counts killed/collected Skulltula source flags.
Evidence: external `native-predicates.json`, `native-probe.log`; historical native graph
facts under `work/r17-dungeon-items/reward-graphs/` (facts only, no decoder code reused).

## Verification and staging

Implemented `trials_count`0–6 (default6 omitted from serialization), `bridge=tokens` with
count0–100, CLI/CS1/app controls, seeded world preparation, native initial-state hook,
remaining-trial text, spoiler/play note, and seed-aware tracker reconstruction.
No fill algorithm or native event flow is changed by trials. Existing resource patterns
already cover all inputs; pack parity matrix now includes token bridge, zero and partial trials.

Initial focused native/synthetic run: **123 passed,9 failed**. Printed failures were invented
fixture location entries lacking their required `rule` key. Added those keys; aimed run:
**20 passed,1 failed**, now printing the fixture's impossible locked Tower chest (all trial
events deliberately false). Removed only that unrelated chest from the synthetic fixture;
the actual tower gate and all of its subset assertions remain. Aimed tracker/generator parity
test then **1 passed**. Native initial-value/text inverses and token counter oracle passed
in both earlier runs. Receipts `focused.log`, `focused-fixture-fix.log`.

Scoped formatter/check: passed after splitting the printed native-counter metadata dict
and import group; repository formatter identified one short `logic_world` signature wrap,
now corrected. No formatter wrote repository files.

Actual UI proof: **Chrome --headless=new only**, Playwright headless, in-memory Preferences.
Native controls selected token bridge3 and trials3, asynchronously published a valid replayable
settings string, with clear new-game/built-not-played help. Screenshot inspected:
`work/r20-trials/ui-settings.png`; receipt `ui-proof.json`. Browser/server closed.
No omp browser tool, visible Chrome window, user preferences or player seed paths used.

Post-rebase focus on local main176c2f4: **132/132 passed** in20.63s, native RomFS set,
`-n2`, `CLAWSHOT_WORKERS=1`. Subsequent narrow boundary correction refuses partial-trial tracker
reconstruction without a seed number while leaving default6 independent of it. Zero-trial text
also replaces the native preceding “blocked” line; the scene's six tube actors always exist
(`Logic_Create=true`), so it does not require a deleted barrier actor. No scene/flow edit added.

### Ordered acceptance and completed sweep receipt (2026-11-20/21)

The original2100-seed proposal was cancelled **before acquiring a lock or generating a seed**.
The auto-retry waiter was cancelled while cs20b owned the lock. The driver never auto-retries.
Claude's final handoff required both cs20b's passing gate/release and MAIN MOVED to `ade62dc`.
Rebased before acquisition; additive exclusion/trial serialization and note conflicts retained both sides.
Post-integration focus: **132 passed in19.78s**, native RomFS, `-n2`, internal workers1.
Frozen parity/sweep head: `125f3a543df33b1f193adf17c07ee1e9083835a7`.
Estimated parity+sweep30–40minutes; observed **1371.21s (22m51s)**, six workers, no game.
Claude approved one round-file-only receipt commit after the sweep, then the exact-head full
gate on that final head if source/test bytes are unchanged. No extra matrix before that gate.

| Recipe | Accepted seeds | trials_count | Token threshold | First-attempt failures | Attempts | Exhausted |
|---|---:|---:|---:|---:|---:|---:|
| Exact broad CS1 | 200 | 0 | 3 | 9 | 209 | 0 |
| Exact broad CS1 | 200 | 3 | 40 | 10 | 211 | 0 |
| Defaults | 50 | 3 | 20 | 0 | 50 | 0 |
| Recommended | 50 | 3 | 20 | 1 | 51 | 0 |

All500 accepted; maximum3 attempts. Each seed passed production beatability, exact normalized
item-stock conservation, all100 token items collectible, correct remaining-trial count and
seed-aware preparation agreement. Broad partial covered all20 possible three-trial subsets;
each preset covered16. Per-seed attempt/rejection counts and failed-first seed IDs are retained;
internal retry exception messages are **not** retained. No unchanged rerun or extra matrix.
Receipts: `sweep-500/results.json`, `sweep-500.log`, `main-moved-focused.log`.

Default6 all-file parity: actual main `ade62dcfa3a3ce14495d52bc5a3ca79a1f029e66`
versus the frozen candidate above, every output-path SHA256 identical:

| Private default seed | Files per arm |
|---|---:|
| 20202004 | 122 |
| 20202014 | 121 |
| 20202024 | 120 |

The all101 threshold synthetic test covers numeric comparison boundaries without an oversized sweep.
Driver: `work/r20-trials/sweep.py --ordered-turn`; full gate: `gate.py --continue-owned-lease`.
The same owned lease continues through the round-file receipt and full gate; no game/build/boot.

### Private paired checks (built and boot-checked; castle behavior unplayed)

Production builders ran before turn2 at internal workers1, through each actual writer.
Both arms share explicit placements, native admission checks and beatability search.
Packet source heads are main `479ed443603b70f43e9e4612da18ad05db5169f9` and candidate
`89fa90080890094055c047e286ccbe434206a591`, before the exclude integration above.
Bridge seed20202014 already put a token in Zora's River's open-grotto chest:
`bridge-shared-recipe.json` records **no placement swap**. This exercises chest token stock,
not a Skulltula kill counter. Claude changed the staged threshold to16 against the natural
first-adult Nov9 save's15 tokens; **no save edit ships**. Both fixture copies equal the source
SHA256 `e63eba9d8173c7c03e1e5338c48ec2dc90cbd2f9b2cad1e487022d5cb46c761c`.
`bridge-fixture-proof.json`: edited=false, differing_bytes=[]; original source untouched.
The abandoned15→2 fixture and partial failed output are outside every launch root.
Initial main staging failed on the writer's unsupported AINB RSTB size formula when serving
the native bridge module as an identity change. Printed path/error are in `staging.log`.
The control-only builder now uses `BuiltFile` with the native allocation, as production
bridge staging already does; the aimed rerun built all four arms successfully.
Trials seed20202004 starts each profile empty, testing real new-game defaults, not save repair.

Folder `E:/OOTRemake/work/r20-trials/ingame/`; launcher names:
`Test - bridge main.bat`, `Test - bridge candidate.bat`,
`Test - trials main.bat`, `Test - trials candidate.bat`.
All pin **Longshot 3.0.0** stable, use one mod and unset HOS_FS_OVERLAY.
Checklist `ingame/CHECKLIST.md`; **15–22minutes per paired check**, unmeasured, each under30minutes.
Bridge: closed at15; chest token gives16; native-story control stays closed, candidate rainbow scene
and bridge should open; chest/counter/latch must persist through Continue. Trials: one explicitly permitted
debug age change to adult in each new game, entrance teleport, normal tower shutter/barrier approach;
Require control blocked and zero-trials candidate passage without a core; verify save/Continue persistence.
If stable runtime offers no age change, stop rather than edit a save or invent another fixture.
Inspector `inspect_packet.py <bridge|trials> --played` checks only these isolated saved states.

All four private launcher dry-runs returned0. `packet-proof.log` establishes paired native-data
differences and initial fixtures only; it does not establish gameplay. Full per-file SHA256 maps
are in `packet-{bridge|trials}-{main|candidate}.json`. Representative GameData fingerprints:

| Arm | GameData/GameDataList.Product.110.byml.zs SHA256 |
|---|---|
| Both main controls | `2d8ee35ce896597362e799123a2a834597ce19ba62a58209547adb94fd1addc7` |
| Bridge candidate | `52818e3bc8119ec90b9f4e756db0a9bc0316e1e54f97d95217b487ab29dcb30e` |
| Trials candidate | `a0e77181b6360031aa4725cb363ceaed1cc7982d0919d4dfcdbca70c39cae413` |

Claude boot-checked all four arms on **Longshot3.0.0**, source `87cb36aa`:
`work/r20-trials/bootcheck-results.txt`, cited in the checklist.
Every arm: crash0/fatal0, save mounted, exactly one mod.

| Pair (both arms) | Written output files per arm | Boot RomFS entries per arm |
|---|---:|---:|
| Bridge | 150 | 191 |
| Trials | 121 | 160 |

Logs prove modded GameData loaded in all arms and the native new-game initializer loaded
in both trials arms. Bridge trigger, barrier/tower passage and save/Continue remain **unplayed**.
Partial-trial play, late Light Arrow story order, every language's visual layout and a complete
shuffled playthrough are not claimed.

### Final gate handoff

This is the one approved round-file-only receipt after the sweep. Source/tests must remain
byte-identical to the frozen sweep head; show `git diff --stat <sweep-head> HEAD -- src tests`
empty, then run `gate.py --continue-owned-lease` on this receipt commit without releasing.
Its exact-head command/count/exit evidence belongs in `work/r20-trials/gate/results.json`
and stage logs. No gate pass or READY is claimed before that run; report its observed result
without another documentation commit. No agent game launch or player-save edit is authorized.

### Post-gate candidate identity proof (Claude requested, 2026-11-21)

Claude accepted gate head `79f936419e628a39ad1576ab169ef999f998daad` but holds trials
unmerged until Kareem plays both bridge and trials pairs. Claude owns any later main-merge
redo and dump rerun; this request did not authorize another rebase, gate or game launch.

Rebuilt both candidate mods from that exact gated head at **one worker**, no lock, with the
same seeds, settings strings and saved placement inputs as the staged `89fa900` candidates.
Compared SHA256 for every actual staged/rebuilt output path, including play note, spoiler,
all native resources and resource-size table:

| Candidate | Seed | Identical files | Added/removed/changed |
|---|---:|---:|---:|
| Bridge | 20202014 | 150 | 0 |
| Trials | 20202004 | 121 | 0 |

Receipts: `work/r20-trials/gated-candidate-rebuild-79f9364/results.json` (complete old/new
file digests) and `gated-candidate-rebuild-79f9364.log`. Every supplied placement is unchanged.
The initial harness incorrectly compared the partial recipe with the complete prepared map.
Printed bridge values showed278 supplied entries,1334 prepared entries, no missing or changed
supplied entries; the extras were native/default checks. Corrected the input-preservation
assertion and performed one aimed rerun; the every-file comparison was not weakened.
Failed-attempt log and diagnostic are preserved under `gated-candidate-rebuild-failed-placement-invariant*`.

Both sets are byte-identical. Staged mods, launchers and profiles were left untouched;
no restage or replacement-byte boot check is needed. `ingame/START HERE.md` now cites this
proof alongside Claude's four-arm boot receipt and per-arm time budgets. Existing boots
cover the same candidate bytes; bridge/barrier/tower/Continue behavior remains **unplayed**.


### Played follow-up: natural adulthood and voice alternatives (Claude requested)

Natural-adult staging uses existing supported settings `forest=open`, `door_of_time=open`,
`fast_start=[intro,saria,kaepora]`, `trials_count=0`, Master Sword unshuffled.
Open Door is **not** immediate: its existing CLOCK_READY expression requires both
`HyruleField_ArriveEntrance` (supplied by Kaepora skip) and the real Impa field send-off
`HavePlayedEvent.Dm_HrlField_0020` (not forged by any chosen skip).
Leave the forest normally to receive Saria's Fairy Ocarina; Saria wake-up skip grants no instrument.
Play Malon's fixed Egg/Chicken -> Talon -> courtyard -> Zelda/Impa lesson -> real send-off;
then enter the Temple and pull the Master Sword. Native DoorOfTime Event115 grants the sword,
Event98 swaps era equipment, Event103 writes `Sequence_IsChildhood=false`; finish Rauru and
adult Sheik scenes. Verify the saved age flag before the castle approach. Do not transplant the
failed debug-age save into this check, write an age flag, or skip the real send-off.
Sources: `plans/rounds/r16-time.md`, `plans/rounds/r18-master-sword-design.md`,
`src/clawshot/patch/door_stage.py`, `src/clawshot/data/fast_start.toml`.
Allow **30–50 minutes**, unmeasured: approximately15–30 to become adult, then10–15 for
castle/lift/persistence checks plus launch/loading margin. No under30-minute claim.

**Voiced first-view text — maintainer options, not a silent product change:**

1. **Keep the current replacement.** It correctly reports the selected trials, but Kareem
   confirmed Rauru's existing voice-over says different words. Voice is not stored in MSBT;
   changing text does not change the native movie's audio. This preserves the present patch
   and presentation mismatch; it is not fixed by an MSBT tag.
2. **Move “no trials remain” to a non-voiced message, restoring the movie's native text.**
   A concrete existing candidate is Navi balloon407: Defeat_Ganon's FromDoor first-view tail
   Event483 already calls `Npc_Navi.EventNaviRequestBallonMessage(Index=407)`. Its standard
   Navi bubble is non-voiced. Its exact message label is not yet decoded: r12 documents the
   512-key lookup method but did not resolve407. Also it is door-route/first-view-only;
   the area route has no such balloon. Resolve its key and choose equivalent coverage before
   implementing this option. Do not invent a message ID or claim current code uses it.

No voice option is selected by this investigation. The lift/age fix and candidate restage
must not silently move hints, mute the native scene, or bypass story/era transitions.


### Lift predicate and five-minute TEST-COPY isolate (latest Claude instruction)

The actual lift is `Obj_InsideGanonCastle_ElevatedFloor_A_01`, actor
Hash16225864798665712662 in `Banc/InsideGanonCastle/InsideGanonCastle_Static.bcett.byml.zs`.
Room01 AI group16848031393208115130 uses module `_e183`, binding lift instance `_f1b6`.
Its placement is Y128.42958, direction(0,-1,0), distance26.4; this is not the barrier or shutter.

Fresh decode of the current native `_e183` module confirms the exact missing gate:
node9 `HoldGameDataGetBoolSimple(HavePlayedEvent.Dm_InsideGanonCastle_0090)` output0
drives node4 `ActorLogicAreaActor(Area_725e).Logic_Create`. That is the **call/target-floor
sensor**, Hash5467824123512662099, not creation of the lift itself. Node4 SensorHitInfo
feeds node5's player observer; node5 IsHit output0 feeds node1
`ActorLogicElevatorLift_A_00.IsTargetFloor`. Node1 Logic_Create is independently defaulttrue.
Other contact/pulse gates drive force-warp/boarding behavior. History=false disables the
call area even though Count0 and AllBarrierClear remove the central barrier.

The history field is an existing saved Bool (Hash2809946991, native defaultfalse,
reset8/save0). No named age/era field appears in the castle scene-module/flow scan;
the lift actor parameter tables contain no age condition, and its root AINB contains no
`Sequence_IsChildhood`, `IsAdult`, `EventQueryPlayerIsChild`, `GameDataNameBool` or `CurrentEra`.
This does not prove absence of an opaque engine-era cache. The standalone unmodified
research decoder hit its own ParseWarning constructor bug on that root's expression
section; no library/engine code was patched to hide the failure. Scene-module edges were
decoded successfully from the current native file; do not confuse string evidence with
a successful root-expression decode.
Facts: `lift-followup/lift-predicate-proof.json`, `lift-node-evidence.json`,
`lift-placement-pack.json`, `lift-actor-parameters.json`, `lift-actor-decoder-facts.json`.

Partial counts retain the real final core: native `_All` tail Event774->606 accepts Count<=0,
then Event778 sets AllBarrierClear and Event27 plays0090 before Step04. With at least one
real core, history can become true natively; count0 runs no core. A zero-only initialization
of the existing history Bool is the minimal candidate fix **if the age-isolate probe fails**;
do not apply it or claim sufficiency before the requested probe.

**TEST-COPY ready, not played:** copied the entire played candidate profile to new
`ingame/user-r20-trials-TEST-COPY-adult`. Modified only latest castle save's
`Sequence_IsChildhood=true->false`, byte offset72068. Parsed entry diff is exactly that
one Bool; raw diff exactly one byte; all other copied files and original profile hashes
are unchanged.0090 history remains false. No production mod, source behavior, inventory,
quest flag or original save was changed. Proof: `lift-followup/age-testcopy-proof.json`.
Launcher `ingame/Test - trials TEST-COPY adult flag.bat` pins Longshot3.0.0 and the unchanged
original candidate mod, passed DRYRUN; Claude boot-checks, Kareem Continues the latest
castle save and tests the normal entrance->tower lift route, about5 minutes.
No New Game, debug age or teleport into/above the tower. `START HERE.md` points to this probe.

Gate policy for any later fix: each stage checks for a running Hookshot/Longshot process;
if one is active, wait10 minutes and check again, never start that stage during the game.
No production fix, new-game rebuild or gate has been started while this probe is pending.


### Exhaustive reader census and zero-only fix (supersedes age-only probe)

Claude cancelled the age-only probe after the lift predicate was established. Its launcher
was renamed `.bat.disabled`; the unused copy/proof remain research evidence.
The short replacement route was explicitly approved in the form (`short_test_copy`):
a NEW copy of the played profile, with only `Sequence_IsChildhood=false` and0090 history=true.
This avoids the30–50minute replay but does not claim to prove natural adulthood.

Parent closed the scouts' execution/coverage gaps with a **complete current-ROMFS scan**:
186583 files,340076 decompressed leaf resources,10454 archives,102185 zstd frames,
51053366981 bytes scanned, zero errors. No large-file skip; plain large files streamed.
All914 EVFL files were parsed freshly (653 flowcharts,261 timelines). All884 BoolExp
rows and their transitive BoolExp references were checked: no history-expression alias.
The only numeric GameData occurrences are the Bool definition and
Struct `HavePlayedEvent` member `Dm_InsideGanonCastle_0090` pointing at that SAME Bool,
not another expression or independent reader.

**Every data-defined reader of the history field:**

| Reader | Effect of zero's new true initial value |
|---|---|
| `Room_01_Prefab_e183`, node9 -> node4 `Area_725e.Logic_Create` -> node5 -> lift node1 `IsTargetFloor` | Creates the lift call/target-floor sensor; normal player contact can request descent/boarding. Does not create the always-present lift actor. |
| `Room_01_Prefab_75af`, node1 -> nodes2–5 `Logic_Create` | Creates the four native post-finale pots `Obj_Pot_A_06_b559`, `_aea3`, `_f0f5`, `_f42d` at room load. Their existing loot becomes available earlier; contents are untouched. Not merely a cosmetic effect. |

No other loose or packed asset contains the full saved-field name. Bare0090 matches are
movie, voice, camera, effect, animation, sound/message resources and registry records,
plus Defeat_Ganon Event27's transition; they are not additional field-reading gates.
Native0090 itself has no history query. The engine's generic event-history recording is
not an explicit event-flow writer. This census covers native data, not an assertion that
arbitrary engine C++ never consults history. Receipts:
`lift-followup/history-asset-inventory.json`, `history-flow-and-hash-inventory.json`,
`history-expression-aliases.json`, plus the decoded node evidence above.

**Implemented minimal fix:** only `count==0` additionally initializes existing
`HavePlayedEvent.Dm_InsideGanonCastle_0090=true` through the shared new-game hook.
This completes the skipped barrier-clear presentation state; no barrier-clear movie
plays when there is no barrier. Existing AllBarrierClear/removal/count handling stays.
Counts1–6 do not change this history or AllBarrierClear default; partial counts therefore
wait for the real last core, whose native count<=0 tail sets clear before playing0090.
No new flag, quest step, production age value, event flow, actor binding or runtime patch.

**Focused native/synthetic proof:139 passed in29.83s**, game-free, `-n2`, internal workers1.
The extended saved-state regression catches missing zero history and premature partial
history. New native regression covers0–6, checks the actual GameData history/age defaults,
and for1–5 traverses the native count<=0 all-tail to the clear writer then0090 transition.
The production age row remains byte/tree-identical; TEST-COPY repair is separate.
Receipt `lift-followup/focused.log`; no unchanged failing rerun.

Approved fixed TEST-COPY prepared separately at `user-r20-trials-TEST-COPY-lift-fixed`:
original profile hashes unchanged; only latest castle progress.sav changed, exactly two
Bool entries/two bytes: age offset72068 true->false, history offset1884 false->true.
Proof `lift-followup/fixed-testcopy-proof.json`. This also supplies the corrected zero
state to an existing save, because new-game defaults do not migrate played saves.
No inventory, quest, core/counter/all-clear or other saved field was changed.

Only the trials candidate was rebuilt with its SAME seed/settings/placement inputs:
121 files, seed20202004. Natural-adult/open-Door settings were not added. Bridge and
control arms stayed untouched; the played packet is archived outside the repository.
The canonical `ingame/Test - trials candidate.bat` now selects the fixed TEST-COPY;
Longshot3.0.0 DRYRUN passed. Normal lift ride and Save/Continue remain unplayed.

### Rebased lift follow-up: ordered parity and full gate PASS

Claude requested the rebase, no new sweep (placements unchanged), three default6 seeds,
one count0 difference proof and a full game-free gate. Fix/source head
`b234e3e0e00364b9cc934b83dfb4a5248fe86f53` is based on main
`be0e288b1adce87db512dd162435da37f140e52b`. Post-rebase focused native checks:14 passed.

Actual main and candidate outputs were rebuilt at one worker, checking game absence
before every seed. **Every output file**, including metadata, matches by relative path
and SHA256 for each default6 seed:

| Seed | Identical files per arm |
|---|---:|
| 20202004 | 124 |
| 20202014 | 122 |
| 20202024 | 119 |

For count0 seed20202004, actual pre-fix code
`0b665b0ee77adc26c580184e3be77dc46df1483b` on the SAME main was also built.
Across121 files only `romfs/GameData/GameDataList.Product.110.byml.zs` changes.
Its only tree difference is `HavePlayedEvent.Dm_InsideGanonCastle_0090.DefaultValue`
false->true; restoring that Bool makes the entire BYML tree identical.
Receipt: `E:/OOTRemake/work/r20-trials/lift-followup/parity-results.json`.

**Older played-packet distinction:** rebasing also changes `spoiler.json` because the
unchanged Windmill heart-piece placement moves from reachable sphere1 to10 under main's
logic correction. No placement moved. The receipt preserves both played-packet hashes;
stale spoiler bytes were NOT copied back to manufacture an all-file identity claim.
The fix-only history proof above uses actual old code on the same corrected baseline.

cs20c explicitly posted LOCK RELEASED at13:09. cs20d acquired only afterward, retained
one lease through parity and all four gate stages, and posted LOCK RELEASED at14:15.
All stages ran on frozen `b234e3e0`; per-stage tasklists show no Hookshot/Longshot game.
The600-second game-wait policy remained enabled; no waits were needed. No new sweep.

| Full gate | Observed result |
|---|---|
| `uv run ruff format --check` | 527 files already formatted |
| `uv run ruff check` | All checks passed |
| Synthetic `uv run --with pytest-xdist pytest -n8` | 4196 passed,819 skipped,24 warnings;440.25s |
| Dump `uv run --with pytest-xdist pytest -m dump -n8` | 816 passed,24 warnings;3099.46s |

Synthetic internal workers4; dump internal workers3. Dump used the read-only native
ROMFS/NUP and r19 layered-dump paths recorded by the gate script.
Receipt: `E:/OOTRemake/work/r20-trials/lift-followup/gate/results.json`; stage logs alongside.
This final round-note update is receipt-only, after the gate; source/tests remain those
of the gated fix commit.

Claude's fixed-candidate **boot PASS** is
`E:/OOTRemake/work/r20-trials/bootcheck-lift-fixed.txt`: Longshot3.0.0/source87cb36aa,
160 RomFS entries, crash0/fatal0, save mounted, one mod; modded GameData and initializer
both loaded. Cited in `ingame/START HERE.md` and `CHECKLIST.md`. Boot is not lift gameplay.
**4b gameplay PASS (Kareem, reported by Claude):** elevator is down, works and carries
Link up; it can be sent up unoccupied and returns down; the working state persists
after Save/Continue. This completes the approved fixed TEST-COPY's lift/persistence
check. No debug-age rerun or longer natural-adult route is needed for this question.
Do not infer natural adulthood, arbitrary old-save migration, partial-trial gameplay
or a full playthrough from this fixture.

### Integration with merged starting inventory (main5ed31bc)

Claude moved main to `5ed31bc` after starting inventory's played PASS and requested a
feature-preserving rebase, light trials/starting-inventory focus, an actual combined
count0/starting-items seed and a new full game-free gate after cs20a; no sweep.
The rebase completed. Conflicts were additive/compositional, resolved retaining:

- `Settings.as_dict`: both starting-items/health/wallet and non-default trials count.
- Generated play notes/imports: both starting inventory and remaining-trials sections.
- Preparation imports: both starting pool replacement and seeded trial selection.
- Native initialization: both starting-item initial values and trial initial values;
  `prepare` receives the seed so native and logic trial choices remain aligned.

Integration source head: `1260abf9a5b08063fd735dfebad6a51f04254dab`.
Both features are retained and the requested light proofs passed, with game absence
checked before each stage:

- `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest
  -n2 tests/test_ganon_settings.py tests/test_starting_inventory.py`: **41 passed in36.69s**,
  including the native tests from both files. Receipt:
  `E:/OOTRemake/work/r20-trials/start-integration/focused.log`.
- Actual `make_seed`/`write_seed`, seed20202034, count0, starting Kokiri Sword, Slingshot,
  Giant Wallet and Zelda's Lullaby, plus2 extra hearts and full wallet: **118 files built**.
  Settings string round-trips with both sets of options. Built GameData reads0090 history
  true, rupees1000, Zelda lesson-history false. Initial ownership contains all four choices;
  the written native initializer grants Kokiri Sword, Zelda's Lullaby, the wallet tiers
  and Bullet Bag before Slingshot, and supplies20 quarter-hearts. This checks the actual
  composed output, not independent patches or a fake build. Receipt/file hashes:
  `E:/OOTRemake/work/r20-trials/start-integration/combined-results.json`.

The combined seed is proof-only outside the repository; it does not replace Kareem's
played mod/profile or claim combined-settings gameplay. No new sweep or runtime change.
Gate-order line10 queues cs20d after cs20a's explicit LOCK RELEASED; no lease is taken
until that post. The new full gate retains per-stage no-game checks and600-second waits.
This pre-gate evidence commit changes only the round note; integrated source/tests are
those checked at1260abf9.

### Final pre-gate integration: hints49a503fd49 + starting inventory + trials

Claude requested rebasing onto hints before the single final gate, rather than gating
on5ed31bc and requiring a third gate after hints merge. Rebase onto frozen hints
`49a503fd49493204da6fad526c03639a9f4a553f` completed cleanly, without conflicts.
The overlapping settings documentation, CLI, app metadata and patch composition retain
all three features. Checked integration source: `02b73ff0808f7351324013cdc10e2bb9099e8bc7`.

**102 focused tests passed in127.76s**, `-n2`, internal workers1, native ROMFS enabled,
with no game running. Coverage files:

- `test_ganon_settings.py`, `test_starting_inventory.py`.
- `test_hints_settings.py`, `test_app_schema.py`, `test_hints_select.py`.
- `test_static_hints_dump.py`, `test_gifts_rewards_dump.py`, `test_scrubs_dump.py`,
  `test_shop_settings_dump.py`.

These include the changed hints CLI/app contract and the native altar/Ganondorf,
Skulltula reward, scrub preview and shop/fee composition contracts.
Receipt: `E:/OOTRemake/work/r20-trials/start-integration/hints-49a503fd49/focused.log`.

The combined seed20202034 was rebuilt fresh on this integrated source, with count0,
the same four starting items/+2hearts/full wallet, and hints `very_strong`: **118 files**.
Written history=true, rupees1000, Zelda lesson-history=false; the initializer contains
the native sword/song/wallet grants, Bullet Bag before Slingshot and20 quarter-hearts.
Settings round-trip and initial ownership checks passed. No staged played mod/save changed.
Receipt/file hashes:
`E:/OOTRemake/work/r20-trials/start-integration/hints-49a503fd49/combined-results.json`.

**Final freeze/merge contract (Claude):** hints merges first, trials second, with the
trials merge tree identical to its gated tree. This note is committed BEFORE gating.
No repository edits or receipt-only commit follow the gate. Final stage verdicts,
tasklists and logs are recorded outside the repository in
`E:/OOTRemake/work/r20-trials/start-integration/hints-49a503fd49/gate/`.
The final full gate starts only after cs20a explicitly posts LOCK RELEASED, checks for
a running game before every stage, and waits600seconds if needed; no sweep.
The runner checks hints still points to49a503fd49 before acquiring and before each
stage. If hints changes, stop and rebase again before treating the gate as valid.


