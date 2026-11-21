# Round 20 — trials and token bridge (cs20d)

Branch `r20/trials`; base `acbb903`; model `openai-codex/gpt-6.1-sol`.
Research/output: `E:/OOTRemake/work/r20-trials/`. Native dump read-only.
No game launched, runtime folder written, personal seed opened or original save changed.
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
  private paired staged checks bridge3 and trials0; one serialized exact-head full gate.

## Research prerequisites and coordination

Read README, CONTRIBUTING, roadmap/architecture/orchestration/game-data/world-format/decisions,
round20 ownership, round19 tokens and LACS records, and the public-docs-only feature comparison.
GPL factual reference only: `work/refs/sloperina-FINDINGS.md`, section1 (GameData types, reset/save
metadata, Struct members), section5.7 (upgrades need matching pouch identity), section5.8
(map/compass native flags and menu refresh). No GPL code or OoTR/SoH code used.

cs20c hook confirmed: append `FastStartSetting(name, default=False, skips, state, source,
logic=None, game_data={existing_field: typed_value}, flow_edits=())` to `chosen` before
`gamedata.changes(chosen)`. No separate initial-values writer. Exact entries pending native trace.
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

Sweeps, paired packets, default all-file parity and exact-head full gate still pending.
No READY or in-game claim.
