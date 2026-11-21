# Round 20 — trials and token bridge (cs20d)

Branch `r20/trials`; initial base `acbb903`, integrated base `ade62dc`; model `openai-codex/gpt-6.1-sol`.
Research/output: `E:/OOTRemake/work/r20-trials/`. Native dump read-only.
Agent launched no game, wrote no runtime folder, opened no personal seed and changed no original save.
Every behavior change remains **built, not played** until Kareem's paired **Longshot 3.0.0** check.

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
