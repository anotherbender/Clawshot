# Round 22 tracker — cs22b

Branch `r22/tracker`, base `2091387`, model `openai-codex/gpt-6.1-sol`. Intended ready kind: merge.
Scratch: `E:/OOTRemake/work/r22-tracker/`. No game started; no writes to game folders, player seeds or saves.

## Scope and evidence

1. Bombchus require the Bomb Bag in generator and tracker logic, independent of `free_bombchu_drops`.
   Kareem, Longshot 3.2.0, Clawshot 0.2.6, 2026-11-24: bought Bombchus showed zero and were unusable before
   the bag, even with Goron's Bracelet (no strength-refusal animation); the bought amount appeared with the bag.
   Source: `work/rounds/r22/kareem-0.2.6-play.md`, Kareem's answers (non-spoiler section).
   Correct D30 as explicitly assigned by the round brief. Tightening only; no play packet.
2. Derived-resource source marker (rescoping below), preserving reachability; headless UI checks and screenshots.
3. Silver-rupee native save flags, cited, with synthetic fixture coverage for trial endings.

## Marker rescope (Claude, 2026-11-24; provisional)

Observed on base `2091387`, not an inference: `tracker/logic.py:555-560` constructs `Search(world, search_items(inv,
world))` without collecting any locations; `inventory:257-262` grants `Buy Deku Stick (1)` only for positive saved
`Item_DekuStick` stock. `world/search.py` derives events but collects placed shop items only via `collect_spheres`.
A source-only probe printed no `Buy*` helper definitions and no `Buy*` world events in the prepared Defaults world;
the Wolfos rule reads `Buy Deku Stick (1)`, `(5)` and `Deku Stick Drop` as ordinary counts.
Claude corrected the brief: do not add accessible-shop closure. Instead mark a check reachable only through
a derived resource/event item absent from saved inventory. The side panel names its event, source regions,
supplying age and rule. This is provisional; Kareem may overturn it.

Implemented as counterfactual searches over the same world/inventory with only resource grants withheld.
Story and age events remain. One deterministic sufficient resource set is reported (not every alternative);
all reachable regions granting those resources are named, with their supplying ages. The authoritative
search and all `in_logic` values are unchanged. Explanations/searches are cached until inventory changes.
No unchecked reward or shop placement is read.

## Adult Baba sticks: additional tightening approved by Claude

Kareem's play facts (Longshot 3.2.0, Clawshot 0.2.6, 2026-11-24): a sideways sword slash gives a stick;
Bow and bomb kills give nuts, including as adult. In that play he held no adult sword (Master Sword shuffled,
not found). Child Boomerang stick yield remains unproven, conservatively removed at Claude's request.

Read-only dump facts (`baba_trace.py`, `baba/selected-graphs.json`, `baba/node-chain-summary.txt`):

- `Banc/KokiriForest/KokiriForest_Adult_Dynamic.bcett.byml.zs` has 14 `Enemy_Dekubaba`.
- `Pack/Actor/Enemy_Dekubaba.pack.zs`, `Component/ActorHolderParam/Enemy_Dekubaba...` binds
  `DekuStickDrop` to `Enemy_Dekubaba_DekuStickDrop`. `AI/Dekubaba.action.interruptdie.module.ainb`
  node 16 (`OneShotActorHolderTryCancelSleepActor`, key `DekuStickDrop`) activates it.
- The child actor's `Drop/DropSubTable/Enemy_Dekubaba_DekuStickDrop...` gives `Obj_DekuStick`, count 1,
  probability 100, `IsReplace = true`.
- `GameParameter/DropGlobalParam/Default.game__drop__DropGlobalParam.bgyml`,
  `DropLotteryMasterData.DropUnlockCondition`: `Obj_DekuStick` requires `Sequence_IsChildhood`.
  `ReplaceSetting` targets it to `Obj_Rupee_Green` (condition hashes 1827360415 and 8566081).
- The same table gates `Obj_DekuNut` on `Get_StoneOfForest_IsAfter_GoInside_Exp`, **not** childhood.
  Thus no adult nut prohibition is inferred. Adult Bow/bomb nut supply is played, not merely metadata.
- `Obj_DekuStick` pouch component targets `Item_DekuStick`, auto-pickup/stock enabled and small Stick Bag link.
  This does not bypass the drop-unlock/replacement table.

Native layout facts were read first from sloperinaGZ `docs/FINDINGS.md`, section 1 *GameData*, *Saved or not,
and what resets a field*, and *Save files* (`work/refs/sloperina-FINDINGS.md`); no GPL code copied.
Cached native AINB JSON is game-derived research outside this repository; only identifiers/facts enter it.

Changes: four live Stick Drop overrides moved out of `remake/master_sword.toml` into `remake/baba_drops.toml`,
all `is_child and Kokiri_Sword`; the other three pot-only paths remain false. Child Boomerang no longer supplies
sticks. Nut rules retain real combat predicates, add played adult Bow/bomb routes, and never assume a sword with
Master Sword shuffle. No gameplay bytes are patched; optional game confirmation is not a gate.

### Settings-only, no-save reproduction

Only the explicitly permitted `settings_string` key was read from the player-report spoiler; no placements,
save, or other report-folder contents were read. Its relevant settings: forest open, Door open, free time travel,
Master Sword shuffled. `initial_sources.py` uses synthetic inventories, not the player's inventory.

- Fresh new game: zero child GS and no adult access (open Door still needs the Zelda send-off).
- Fairy Ocarina + Weird Egg derives the send-off and reaches adult; with no weapon, zero child GS.
- Synthetic send-off history + Master Sword: before tightening, child HF Lone Tree, LLR Tree, Market Guard House
  and HC Tree all derive `Deku Stick Drop` from KF Outside Deku Tree **as adult**.
- Synthetic send-off + Hammer adds DMC Crate through that same adult supply.
- After the adult-stick tightening, every case above has zero child GS; the adult can still reach Kokiri Forest.
  Receipt: `initial-sources.json` and before/after stdout files under scratch.

The Master Sword/Hammer cases identify an unsafe logic route, not the exact cause of Kareem's observed inventory:
he reports neither child weapons nor an adult sword. No contrary inventory is inferred from synthetic probes.
One earlier thread post prematurely predicted that Fairy Ocarina alone opened adult; its completed probe did not,
and the next post explicitly corrected it.

## Checks and handoff

Rebased onto current local main `5bc5577`; focused and real-dump registration contracts pass (receipts below).
Final 1280/1920 browser screenshots pass. Ordered paired sweeps and full gate remain.

## Bombchu generator safety and local shortcuts

The initial safety claim was only partly correct (base `2091387`, file:line):

- `generate/fill.py:67-68,799-846` screens shuffled Bombs/Bombchus packs against a search with all bag/pack
  alternatives removed; `ammo` at line 839 is taken from the shuffled pool. `allowed` and `with_screens`
  enforce that at every fill/external-placement path (`:400,849-885,932-947,1173`).
- `Buy ...` refills are Shop-only (`fill.py:59-63`); with free drops on, buying alone supplies only the refill
  predicate, not `found_bombchus`. No world event supplies `Bombchu Drop`.
- But fixed locations start with their vanilla rewards (`fill.py:1166-1170`) and beatability collects them
  (`:1279`). D25 does not screen those rewards. The Wasteland Bombchu Salesman always stays vanilla
  (`remake/gifts.toml:98-102`; `haunted_wasteland.toml:76` gives Bombchus (10)); its Hover Boots/Longshot access
  and jumpslash do not need the bag. The 40-token House reward is another fixed pack without Gift shuffle.
  Therefore the generator could count a fixed pack as explosives before the bag, not merely the tracker.

`remake/bombchus.toml` guards found/usable supply; `shops.toml` guards refill capability (the shop catalog is
applied after remake overrides, so that line must change there). The tracker cell separately requires its
held bag; its item tile still displays the saved stock/history, not invented usability.

`free_bombchu_drops` retains its supply meaning: on, found Bombchus supply the capability and count as explosives;
off, a refill source supplies it and Bombchus do not count in `has_explosives`/`has_both_explosives`.
Every branch now needs the bag. All production seeds use the on default; it is not an exposed player option
(`settings.py:25-35`, `data/settings.toml:91-97`). Direct world tests cover both settings.

Spirit's two-key `free_bombchu_drops` branches also assumed its local chest pack without the bag. Eighteen
translated live location rules gain a bag guard on that branch only (`remake/bombchu_shortcuts.toml`), plus the
two existing overrides in `adult_spirit_temple.toml`. Three-key, projectile and other non-Bombchu routes remain.
The absent East chest stays `n64_only` and has no additional override. Regression cases cover both two-key
bag refusal/acceptance and the unchanged three-key route.

## Silver-rupee flags

`tracker_logic.toml [silver_rupees]` maps all 16 live logical groups to saved completion Bools, five per group.
Every entry cites its native room/counter binding, completion trigger chain and GameDataList key.
All are default false, reset 8, save index 0 (progress.sav). True grants five; false grants none; absent is
unknown and grants none. No per-rupee Bool64 inference, partial progress, pouch ownership or placement lookup.

| Group | Saved completion Bool |
|---|---|
| Castle Forest | `InsideGanonCastle_Dungeon_Room03_SilverRupee` |
| Castle Fire | `InsideGanonCastle_Dungeon_Room10_SilverRupee` |
| Castle Light | `InsideGanonCastle_Dungeon_Room14_SilverRupee` |
| Castle Spirit | `InsideGanonCastle_Dungeon_Room16_SilverRupee` |
| Well Basement | `BottomOfTheWell_Level_Room_09_A_SilverRupee_GetAll` |
| Ice Scythe | `IceCavern_Room05_Unlocked` |
| Ice Push Block | `IceCavern_Room06_Unlocked` |
| GTG Slopes | `GerudoTrainingGround_Dungeon_Room02_SilverRupee` |
| GTG Water | `GerudoTrainingGround_Dungeon_Room09_SilverRupee` |
| GTG Lava | `HavePlayedEvent.GerudoTrainingGround_06_SilverToken_Unlock` |
| Shadow Scythe | `ShadowTemple_RoomB2FC_Cleared` |
| Shadow Huge Pit | `ShadowTemple_Level_Room_09_Clear_B` |
| Shadow Invisible Spikes | `ShadowTemple_RoomB3FB4FE_Cleared_01` |
| Spirit Child Torches | `SpiritTemple_Room05_BoardNet_On` |
| Spirit Sun Block | `SpiritTemple_Room10_Candle_On` |
| Spirit Adult Boulders | `SpiritTemple_Room16_Unlocked` |

Audit: 85 native silver rupees in 17 physical puzzles. GTG room 2 has two five-rupee entrance-side sets
that set one room clear and then remove both sets: the world's five count once. The 15 flags' only live writers
follow their counters' `AllGet`, directly or through the requested unlock event; no writer clears them.
Receipt `silver/audit_silver.py`, `silver/audit.json`; native AINB decode cache (5036 graphs), 915 flows and 167
Banc files examined by the audit. No new decoder or game started.

**GTG lava completion history (cs22b, traced):** the autogen clear key is still not guessed. Instead, the saved
`HavePlayedEvent.GerudoTrainingGround_06_SilverToken_Unlock` Bool proves all five were collected: the only Banc
caller is `EventRequestActor` Hash5973768131564127645; room06 module n12 counter (all five links) drives it only on
`AllGet`. There is no EVFL subflow caller. `GerudoTrainingGround_Gimmick` unlock entry follows
Event101 -> Event102 -> Event127 (`ShadowTemple_Gimmick/Silver_Tolken_Finish`) -> Event96 -> Event420 ->
Event419 `EventTriggerSetEventBool(true)` -> module n18's autogen clear. The history itself is saved
(GameDataList Bool Hash2670094484/defaultfalse/reset8/save0); the appear event is not completion evidence.
Receipts `silver/lava-callers.txt`, `silver/lava-unlock-chain.txt` supplement the original audit.
Six named groups have no remake/world puzzle. All live groups and all four castle silver puzzles are mapped.
The fixture proves the Forest ending needs its own saved clear plus gear, not another room flag/unread field;
GTG lava's encounter/appear history must not credit its rupees.

## Focused and headless proof

- First marker/inventory focused run: 55 passed (`-n 2`, workers 1).
- Supply/world contracts: 119 passed, one failure was the implementation-only `len(entries) > 90` assertion
  after moving four stick overrides out of the sword file. Deleted that file-count assertion, not its behavioral
  comparisons; the specific fold test then passed. No source-text contract was re-pinned.
- Integrated focused tracker, world supply, sword, settings and app-schema checks: **473 passed, 1 skipped**,
  130.73 seconds (`CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2 -q tests/test_tracker*.py
  tests/test_baba_drops.py tests/test_world_bombchus.py tests/test_world_remake_bombs.py tests/test_shop_logic.py
  tests/test_master_sword_logic.py tests/test_settings.py tests/test_app_schema.py`).
- Final complete silver mapping: 29 passed with tracker logic-data contracts; targeted format/lint clean.
- After rebasing onto main `5bc5577`: **204 focused passed** in 95.25 seconds; **5 dump event-registration
  passed** in 240.72 seconds, including its deterministic scrub-shield coverage (no re-pin).
  Logs: `focused-main5bc.txt`, `registration-main5bc.txt` in the external work folder.
- Source-marker regression cases exercise cross-age sources, transitive exit gates, alternatives versus
  conjunctions, saved stock, inventory invalidation and finished rows. Reachability is compared with direct Search.
- Headless Chromium (`source_shots.py`): shipped page, loopback server, synthetic backend snapshot, no page errors
  or external requests. Source diamond about 11.3 px after rotation; age selection removes it when that view
  needs no source. Screenshots were viewed: `shots/source-child-1280.png`, `source-child-1920.png`,
  `source-either-1280.png` (also `source-either-1920.png`), under `E:/OOTRemake/work/r22-tracker/`.
  These are renderer fixtures, not game observations; the final fixture uses played adult nut supply.

## Sweep recipe

Prepared `sweep.py`: canonical native `make_seed` setup captured before generation/output; six workers under the
ordered gate lock. Paired main/head rows retain only placement/sphere digests and counts, not placements.
Broad 200, Defaults 50, Recommended 50; plus 100 EarlyAdultShuffledChus and 50 EarlyAdultVanillaGifts:
broad with Master Sword shuffle and starting Hover Boots, Longshot, Hammer and Ocarina of Time, no child weapon
or Bomb Bag starting. The latter removes Gift shuffle, retaining the House's vanilla Bombchus too.
Both keep free drops on. Recipe admission was validated without generating any seed.

Implementation commits before rebase: `fe2647bbd9` (world supply rules/D30), `9dc1f313dd` (tracker sources/silver flags).
No runtime resource is newly read or emitted, so no pack-resource or working-set fixture addition is needed.
