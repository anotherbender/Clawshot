# Round 20 — Logic/data audit and docs (cs20h)

Agent/model: `cs20h`, `openai-codex/gpt-6.1-sol`; branch `r20/audit`.
Base: `ade62dc` (current main, excludes merged; trials play-held/unmerged). Status: sweep PASS; exact-head final gate/READY outcome is in the external receipt and `cs-r20` handoff.
No version bump, runtime patch, game launch, player seed/save access or game-folder write.

## Evidence boundary and method

- Read the supplied AGENTS rules, README, CONTRIBUTING, roadmap/round overview, architecture,
  orchestration, game-data/world-format plans, decisions, r19 audit/docs/overview and tracker plan.
- Native source: supported `e0f3ccfa` dump at `E:/Games/Hookshot/romfs`, read only.
  Research scripts/decoded output: `E:/OOTRemake/work/r20-audit/`, never committed.
- GPL lead: [sloperinaGZ FINDINGS](https://github.com/PracticeROM/sloperina/blob/master/docs/FINDINGS.md),
  local facts-only snapshot `work/refs/sloperina-FINDINGS.md`, sections 1 (typed/saved GameData),
  2 (game-file layout), 5.7 (upgrade identities versus capacities), 5.8 (DungeonInfo ownership).
  Read before tracing; no GPL implementation copied. Used the existing unmodified AINB decoder's
  `r14-steps/ainb` native cache, not its implementation source. No OoTR/SoH source was opened;
  their comparison facts came only from the supplied `r20-planning/feature-compare.md`.
- Scope: distance pickup branches (including token drops), and distance switch activation.
  Combat-only ranged alternatives and grapple traversal are distinguished below, not treated as
  proof that a projectile fetches an item. N64 tricks remain disabled; absent evidence is not a
  contradiction and supplies no new route. All new conclusions are static data evidence, except
  BBender's explicitly attributed report. Nothing new was played by Kareem in this track.

## 1. BBender reports — Discord, 2026-11-20

### Windmill platform: confirmed false child logic; tightened

`Kak Windmill Freestanding PoH` is native `Obj_Heart_Piece` Hash **13389209437182306002**,
linked from `HeartPieceAnchor` **3518965357024502806**. The same pickup is in all three
`Banc/KakarikoVillage/KakarikoVillage_{Child,Adult,Adult_Alternative}_Static.bcett.byml.zs`
files, at approximately (1.48,108.90,37.52), with no Dynamic/Presence override and no AiGroup binding.
It is separate from the musician's song and the high windmill chest.

The translated rule allowed usable Boomerang. BBender could not collect it that way in the remake;
this is the reproduction, not something an agent needs to replay. Native corroboration:
`Pack/Actor/Obj_Heart_Piece.pack.zs`, `Actor/Obj_Heart_Piece.engine__actor__ActorParam.bgyml`
explicitly sets **LiftableRef to empty**, overriding `Obj_Item_Base`'s liftable component.
`Weapon_Boomerang.pack.zs`, `AI/Item_Boomerang.root.ainb` node19 uses
`ExecutePlayerAttractObject`; it does not establish a special heart-piece grant route.
`Obj_Heart_Piece.root.ainb` handles native pickup/death, not a separate Boomerang receipt.
**[INFERENCE]** the missing liftable component explains the report; the report itself establishes
that the old child route must not be certified.

`remake/ranged_pickups.toml` now requires adult age and the existing Dampé approach (or the
still-disabled adult movement trick). Explicit adult age also stops a persistent adult arrival
history from becoming a child traversal permission after age return. `dampe_returns.toml` already
requires usable Hookshot for the grave descent and windmill exit: native target **14424380246501499337**
and transition **1143018541481239924**; Kareem played the no-return/Hookshot boundary in round18.
No ordinary windmill room, song or high-chest gate is changed. Public directions now name this route.

### Cow-shed roof: exists; retain identity and current route

`Kak Impas House Freestanding PoH` is native `Obj_Heart_Piece` Hash **17926402522258180222**,
linked from anchor **1051454338871863592**, in **all three** of the same Static files. Placement is
approximately (-44.07,107.97,112.00), behind `Land_Kakariko_House_A_01` (Impa's house); no
Dynamic/Presence override or AiGroup binding hides or substitutes it. Its anchor is not the
rooftop man's anchor **1416092057268113387**, which instead names
`Npc_Hylia_001_IsGetHeartPiece` and is in the Dynamic files.

Do **not** delete this check or alias it to the rooftop gift. Both the native pickup and separate
map anchor exist. `child_kakariko.toml` already removed the N64 construction-site/cucco entry;
child access is the Din's-Fire-gated summit owl → Impa roof → ledge, adult access the Hookshot
roof route. Native placement establishes identity, not a complete collision/climb proof. Prior
remake guide evidence is cited in that override ([Eurogamer Kakariko](https://www.eurogamer.net/zelda-ocarina-of-time-kakariko-village)).
The catalogue source is refreshed with the three-file evidence; its stable ID and label stay.
Historical played corroboration is narrower: in round2 Kareem **saw the substituted red rupee
through the gate** at this Hash, but did not reach it (`plans/03-game-data.md`, section10,
2026-11-07). This refutes a wholly invented source, not the unresolved roof route.

**Question for Kareem/BBender (not blocking tightening): from Impa's roof, is the gated shed-roof
pickup visible/collectible, and does a normal child ladder/cucco route work without the summit owl?**
The latter would loosen logic and is not implemented without a played check. Existing historical
KAK03/AO01 questions are not silently converted to passes.

## 2. Other pickup tightenings

- **Graveyard upper-ledge heart** Hash **2157466067026784951** exists in Child/Adult Static;
  same non-liftable `Obj_Heart_Piece`. Remove its N64 `logic_graveyard_poh` Boomerang retrieval
  branch (already disabled by native validation). Preserve adult bean/Longshot ledge traversal
  and crate requirement. The grapple is a route to the ledge, not a remote heart fetch.
- **Ice Cavern Frozen Blue Rupee:** mark `n64_only`. Fresh read of both native placement files
  finds ten `Obj_RupeeToken_Silver`, **zero ordinary rupee actors**. Existing
  `child_ice_cavern.toml` already excluded the three N64 ledge rupees for the same reason; their
  remake replacement is chest **4128092231168513176**. Red-ice pots are not a loose blue pickup.
  No new physical identity, floor palette, pool item or game file is introduced.

## 3. Ranged pickup inventory

Audit artifact: `collection-inventory.json` (81 syntactic N64 pickup candidates),
`collection-physical.json` (55 census-linked native identities), `pickups.py`, native pack reports.
Each table row is one imported rule; generated TOML is never hand-edited. Effective rules include
all remake overrides. Full expressions below preserve disabled branches so no candidate is hidden.

Evidence keys:

- **T:** linked `Enemy_Skulltula_Gold` placement(s) in the listed Banc area;
  native `Obj_Token_Gold` retains `Component/LiftableParam/Obj_Item_Token_Gold...`, including a
  `Shootable_Hook` attachment offset; Boomerang and hook graphs call `ExecutePlayerAttractObject`.
  Mechanism supported, **not every range/collision route played**. R15 ranch tower retrieval was
  played with child Boomerang/adult Hookshot ([r15 source/route evidence](r15-scrub-tokens.md)).
  Per-location guide/override evidence is linked in the last column; unchanged N64 range alone
  is not promoted to remake proof.
- **H:** non-liftable heart-piece pack above; tightened. Native shield/rupee replacements may
  have different liftability; conservative source logic must work for the native heart too.
- **R:** ordinary rupees/recovery hearts retain inherited liftability; no contradiction in the
  general fetch mechanism. These N64 rows have **no exact native census correspondence**, stay
  unshuffled, and their particular position/range is **unverified**, not certified.
  Fresh Banc checks find no ordinary rupee placements in LostWood and no non-boss heart
  placements in ForestTemple/SpiritTemple; this does not rule out scripted or breakable drops.
  Their N64 rows are not promoted to physical checks from a generic liftable pack.
- **S:** silver-rupee puzzle actor has **no LiftableRef**; a Hookshot rule can mean player traversal
  to a target instead of fetching the rupee. Existing dungeon route evidence is retained;
  direct remote pickup is **not established**, and no invented route is added.
- **N:** absent native source; excluded already or in this track.
- **C:** effective ranged clause is combat/block breaking or traversal rather than item fetch.
  No physical range inference made from it.

| Imported check | Effective requirement | Native remake evidence / disposition |
|---|---|---|
| `Bottom of the Well GS West Inner Room` | `Boomerang` | T — 7460556442932201772; BottomOfTheWell. [`bottom_of_the_well.toml`](../../src/clawshot/data/world/bottom_of_the_well.toml); range unplayed. |
| `Bottom of the Well GS East Inner Room` | `Boomerang` | T — 12165938013608963606; BottomOfTheWell. [`bottom_of_the_well.toml`](../../src/clawshot/data/world/bottom_of_the_well.toml); range unplayed. |
| `Bottom of the Well GS Like Like Cage` | `Boomerang` | T — 3889761319471426870; BottomOfTheWell. [`child_bottom_of_the_well.toml`](../../src/clawshot/data/world/remake/child_bottom_of_the_well.toml). |
| `DMT Rock Red Rupee` | `is_child and (here(can_blast_or_smash) or (logic_boomerang_boulders and Boomerang))` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`death_mountain_trail.toml`](../../src/clawshot/data/world/death_mountain_trail.toml); range unplayed. |
| `DMT Rock Blue Rupee` | `is_child and (has_explosives or (logic_boomerang_boulders and Boomerang))` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`death_mountain_trail.toml`](../../src/clawshot/data/world/death_mountain_trail.toml); range unplayed. |
| `DMT GS Bean Patch` | `can_plant_bugs and can_child_attack and (Progressive_Strength_Upgrade or (logic_dmt_soil_gs and can_use(Boomerang)))` | C/T — 17425319789138387506; DeathMountainTrail. [`child_death_mountain_trail.toml`](../../src/clawshot/data/world/remake/child_death_mountain_trail.toml). |
| `Deku Tree GS Basement Back Room` | `here(has_fire_source_with_torch or can_use(Bow)) and here(can_blast_or_smash) and (can_use(Boomerang) or can_use(Hookshot))` | T — 17501688996789643983; InsideTheDekuTree. [`deku_tree.toml`](../../src/clawshot/data/world/deku_tree.toml); range unplayed. |
| `Colossus GS Tree` | `(can_use(Longshot) or can_use(Boomerang)) and (at_night or gold_skulls_ignore_daytime)` | T — 15057756765324812936; DesertColossus. [`adult_desert_colossus.toml`](../../src/clawshot/data/world/remake/adult_desert_colossus.toml). |
| `Colossus GS Hill` | `is_adult and (at_night or gold_skulls_ignore_daytime) and (here(can_plant_bean) or Longshot or (logic_colossus_gs and Hookshot))` | T — 11160993739666517210; DesertColossus. [`desert_colossus.toml`](../../src/clawshot/data/world/desert_colossus.toml); range unplayed. |
| `Dodongos Cavern GS Side Room Near Lower Lizalfos` | `adult_sword or has_explosives or (is_child and (Sticks or Slingshot or Boomerang or Kokiri_Sword))` | C/T — 1171854281537584829; DodongoCavern. [`master_sword.toml`](../../src/clawshot/data/world/remake/master_sword.toml). |
| `Dodongos Cavern GS Scarecrow` | `can_use(Hookshot) or can_use(Scarecrow) or can_use(Longshot) or (logic_dc_scarecrow_gs and (is_adult or can_child_attack))` | T — 960362013021648957; DodongoCavern. [`dodongos_cavern.toml`](../../src/clawshot/data/world/dodongos_cavern.toml). **Played plain Hookshot: Kareem,2026-11-21, via Claude; follow-up below.** |
| `Dodongos Cavern GS Vines Above Stairs` | `at('Dodongos Cavern Climb', can_use(Slingshot) or can_use(Boomerang) or can_use(Bow) or can_use(Hookshot)) or (logic_dc_vines_gs and can_use(Longshot))` | C/T — 8470399761714006011; DodongoCavern. [`child_dodongos_cavern.toml`](../../src/clawshot/data/world/remake/child_dodongos_cavern.toml). |
| `Dodongos Cavern GS Alcove Above Stairs` | `has_explosives` | C/T — 4565265801822094851; DodongoCavern. [`child_dodongos_cavern.toml`](../../src/clawshot/data/world/remake/child_dodongos_cavern.toml). |
| `Fire Temple GS Scarecrow Climb` | `can_use(Scarecrow) or (logic_fire_scarecrow and Longshot)` | C/T — 5556173334779815044; FireTemple. [`fire_temple.toml`](../../src/clawshot/data/world/fire_temple.toml); range unplayed. |
| `Fire Temple GS Scarecrow Top` | `can_use(Scarecrow) or (logic_fire_scarecrow and Longshot)` | C/T — 9172014785497046138; FireTemple. [`fire_temple.toml`](../../src/clawshot/data/world/fire_temple.toml); range unplayed. |
| `Forest Temple GS First Room` | `(is_adult and (Hookshot or Bow or Bombs)) or (is_child and (Boomerang or Slingshot)) or has_bombchus or can_use(Dins_Fire) or (logic_forest_first_gs and (Bombs or can_jumpslash))` | C/T — 11081821111317815057; ForestTemple. [`forest_temple.toml`](../../src/clawshot/data/world/forest_temple.toml); range unplayed. |
| `Forest Temple GS Lobby` | `can_use(Hookshot) or can_use(Boomerang)` | T — 17612196129225973969; ForestTemple. [`forest_temple.toml`](../../src/clawshot/data/world/forest_temple.toml); range unplayed. |
| `Forest Temple GS Level Island Courtyard` | `can_use(Longshot) or at('Forest Temple Outside Upper Ledge', can_use(Hookshot) or can_use(Boomerang))` | T — 10970805784153267902; ForestTemple. [`forest_temple.toml`](../../src/clawshot/data/world/forest_temple.toml); range unplayed. |
| `Forest Temple GS Raised Island Courtyard` | `can_use(Scarecrow)` | C/T — 2014780391754316762; ForestTemple. [`adult_forest_temple.toml`](../../src/clawshot/data/world/remake/adult_forest_temple.toml). |
| `Forest Temple GS Basement` | `can_use(Hookshot) or can_use(Boomerang)` | T — 3072474196008424241; ForestTemple. [`forest_temple.toml`](../../src/clawshot/data/world/forest_temple.toml); range unplayed. |
| `Ganons Castle Light Trial Silver Rupee Center Top` | `Hookshot` | S — native puzzle family; retained traversal, direct fetch unproved. [`ganons_castle.toml`](../../src/clawshot/data/world/ganons_castle.toml); range unplayed. |
| `Ganons Castle Spirit Trial Silver Rupee Ceiling` | `can_use(Hookshot) or (logic_spirit_trial_hookshot and can_jumpslash)` | S — native puzzle family; retained traversal, direct fetch unproved. [`ganons_castle.toml`](../../src/clawshot/data/world/ganons_castle.toml); range unplayed. |
| `GF GS Archery Range` | `can_use(Hookshot) and Gerudo_Membership_Card and (at_night or gold_skulls_ignore_daytime)` | T — 13037049463363052038; GerudoFortress. [`gerudo_fortress.toml`](../../src/clawshot/data/world/gerudo_fortress.toml); range unplayed. |
| `Gerudo Training Ground Boulder Room Silver Rupee Ceiling` | `can_use(Hookshot) or logic_gtg_without_hookshot` | S — native puzzle family; retained traversal, direct fetch unproved. [`gerudo_training_ground.toml`](../../src/clawshot/data/world/gerudo_training_ground.toml); range unplayed. |
| `Gerudo Training Ground Lava Room Silver Rupee Hookshot Target` | `Hookshot` | S — native puzzle family; retained traversal, direct fetch unproved. [`gerudo_training_ground.toml`](../../src/clawshot/data/world/gerudo_training_ground.toml); range unplayed. |
| `GV GS Small Bridge` | `can_use(Boomerang) and (at_night or gold_skulls_ignore_daytime)` | T — 15265071047503310220; GerudoValley. [`gerudo_valley.toml`](../../src/clawshot/data/world/gerudo_valley.toml); range unplayed. |
| `GV GS Behind Tent` | `can_use(Hookshot) and (at_night or gold_skulls_ignore_daytime)` | T — 13584527502619061465; GerudoValley. [`gerudo_valley.toml`](../../src/clawshot/data/world/gerudo_valley.toml); range unplayed. |
| `GV GS Pillar` | `can_use(Hookshot) and (at_night or gold_skulls_ignore_daytime)` | T — 11535915511003753934; GerudoValley. [`gerudo_valley.toml`](../../src/clawshot/data/world/gerudo_valley.toml); range unplayed. |
| `Graveyard Freestanding PoH` | `is_adult and can_break_crate and (here(can_plant_bean) or Longshot)` | H — 2157466067026784951; tightened above. [`ranged_pickups.toml`](../../src/clawshot/data/world/remake/ranged_pickups.toml). |
| `Graveyard GS Wall` | `can_use(Boomerang) and ((at_night and 'Time Flows') or gold_skulls_ignore_daytime)` | T — 229475726653285413; Graveyard. [`child_graveyard.toml`](../../src/clawshot/data/world/remake/child_graveyard.toml). |
| `Wasteland GS` | `can_use(Hookshot) or can_use(Boomerang)` | T — 14910672274965350769; HountedWasteland. [`haunted_wasteland.toml`](../../src/clawshot/data/world/haunted_wasteland.toml); range unplayed. |
| `HC GS Storms Grotto` | `(can_blast_or_smash or (is_child and logic_castle_storms_gs)) and (can_use(Boomerang) or can_use(Hookshot))` | T — 9162653017526462607; HyruleCastle. [`hyrule_castle.toml`](../../src/clawshot/data/world/hyrule_castle.toml); range unplayed. |
| `HF GS Cow Grotto` | `has_fire_source and (can_use(Hookshot) or can_use(Boomerang))` | N — absent, excluded. [`hyrule_field.toml`](../../src/clawshot/data/world/hyrule_field.toml); range unplayed. |
| `HF GS Near Kak Grotto` | `has_explosives and (can_use(Boomerang) or can_use(Hookshot))` | T — 12007978132755687032; HyruleField. [`hyrule_field.toml`](../../src/clawshot/data/world/hyrule_field.toml); range unplayed. |
| `Ice Cavern Frozen Blue Rupee` | `Blue_Fire or logic_ice_frozen_rupee or (logic_boomerang_boulders and can_use(Boomerang))` | N — absent, excluded. [`ranged_pickups.toml`](../../src/clawshot/data/world/remake/ranged_pickups.toml). |
| `Ice Cavern GS Spinning Scythe Room` | `can_use(Hookshot) or can_use(Boomerang)` | T — 7165255787572043804; IceCavern. [`ice_cavern.toml`](../../src/clawshot/data/world/ice_cavern.toml); range unplayed. |
| `Ice Cavern Push Block Room Red Rupee 1` | `can_play(Song_of_Time) or can_use(Boomerang)` | N — absent, excluded. [`child_ice_cavern.toml`](../../src/clawshot/data/world/remake/child_ice_cavern.toml). |
| `Ice Cavern Push Block Room Red Rupee 2` | `can_play(Song_of_Time) or can_use(Boomerang)` | N — absent, excluded. [`child_ice_cavern.toml`](../../src/clawshot/data/world/remake/child_ice_cavern.toml). |
| `Ice Cavern Push Block Room Red Rupee 3` | `can_play(Song_of_Time) or can_use(Boomerang)` | N — absent, excluded. [`child_ice_cavern.toml`](../../src/clawshot/data/world/remake/child_ice_cavern.toml). |
| `Ice Cavern GS Heart Piece Room` | `can_use(Hookshot) or can_use(Boomerang)` | T — 1612219105489330028; IceCavern. [`ice_cavern.toml`](../../src/clawshot/data/world/ice_cavern.toml); range unplayed. |
| `Ice Cavern GS Push Block Room` | `can_use(Hookshot) or can_use(Boomerang) or (logic_ice_block_gs and can_use(Hover_Boots))` | T — 14822647495538506998; IceCavern. [`ice_cavern.toml`](../../src/clawshot/data/world/ice_cavern.toml); range unplayed. |
| `Jabu Jabus Belly GS Lobby Basement Lower` | `can_use(Boomerang) or can_use(Hookshot)` | T — 13852835165271311030; InsideJabuJabuBelly. [`jabu_jabus_belly.toml`](../../src/clawshot/data/world/jabu_jabus_belly.toml); range unplayed. |
| `Jabu Jabus Belly GS Lobby Basement Upper` | `can_use(Boomerang) or can_use(Hookshot)` | T — 11283202900158580106; InsideJabuJabuBelly. [`child_jabu_jabus_belly.toml`](../../src/clawshot/data/world/remake/child_jabu_jabus_belly.toml). |
| `Kak GS Watchtower` | `is_child and ((at_night and 'Time Flows') or gold_skulls_ignore_daytime) and (Slingshot or has_bombchus or (logic_kakariko_tower_gs and (Sticks or Kokiri_Sword)))` | C/T — 15118290503807073158; KakarikoVillage. [`child_kakariko.toml`](../../src/clawshot/data/world/remake/child_kakariko.toml). |
| `Kak Windmill Freestanding PoH` | `is_adult and (logic_windmill_poh or 'Dampes Windmill Access')` | H — 13389209437182306002; tightened above. [`ranged_pickups.toml`](../../src/clawshot/data/world/remake/ranged_pickups.toml). |
| `KF GS House of Twins` | `is_adult and (at_night or gold_skulls_ignore_daytime) and (Hookshot or (logic_adult_kokiri_gs_hovers and Hover_Boots) or logic_adult_kokiri_gs_nothing)` | T — 7116603238806634901; KokiriForest. [`kokiri_forest.toml`](../../src/clawshot/data/world/kokiri_forest.toml); range unplayed. |
| `LH GS Lab Wall` | `is_child and ((at_night and 'Time Flows') or gold_skulls_ignore_daytime) and (Boomerang or (logic_lab_wall_gs and (Sticks or Kokiri_Sword)))` | T — 13944703896577680014; HyruleField. [`child_lake_hylia.toml`](../../src/clawshot/data/world/remake/child_lake_hylia.toml). |
| `LH GS Tree` | `can_use(Longshot) and (at_night or gold_skulls_ignore_daytime)` | T — 789492162651991711; HyruleField. [`lake_hylia.toml`](../../src/clawshot/data/world/lake_hylia.toml); range unplayed. |
| `LH GS Lab Crate` | `Iron_Boots and can_use(Hookshot) and (deadly_bonks != 'ohko' or Fairy or (can_use(Nayrus_Love) and not shuffle_interior_entrances))` | T — 7388645484070660331; HyruleField. [`lake_hylia.toml`](../../src/clawshot/data/world/lake_hylia.toml); range unplayed. |
| `LLR GS House Window` | `can_use(Boomerang) and ((at_night and 'Time Flows') or gold_skulls_ignore_daytime)` | T — 15889002414176907668; HyruleField. [`child_lon_lon_ranch.toml`](../../src/clawshot/data/world/remake/child_lon_lon_ranch.toml). |
| `LLR GS Back Wall` | `can_use(Boomerang) and (at_night or gold_skulls_ignore_daytime)` | N — absent, excluded. [`lon_lon_ranch.toml`](../../src/clawshot/data/world/lon_lon_ranch.toml); range unplayed. |
| `LW Underwater Green Rupee 1` | `is_child and (can_dive or Boomerang)` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW Underwater Green Rupee 2` | `is_child and (can_dive or Boomerang)` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW Underwater Green Rupee 3` | `is_child and (can_dive or Boomerang)` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW Underwater Green Rupee 4` | `is_child and (can_dive or Boomerang)` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW Underwater Green Rupee 5` | `is_child and (can_dive or Boomerang)` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW Underwater Green Rupee 6` | `is_child and (can_dive or Boomerang)` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW Underwater Green Rupee 7` | `is_child and (can_dive or Boomerang)` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW Under Boulder Blue Rupee` | `can_blast_or_smash or (logic_boomerang_boulders and can_use(Boomerang))` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `LW GS Above Theater` | `is_adult and (at_night or gold_skulls_ignore_daytime) and (here(can_plant_bean) or (logic_lost_woods_gs_bean and Hookshot and (Longshot or Bow or has_bombchus or can_use(Dins_Fire))))` | C/T — 4335656213162247230; LostWood. [`lost_woods.toml`](../../src/clawshot/data/world/lost_woods.toml); range unplayed. |
| `SFM GS` | `can_use(Hookshot) and (at_night or gold_skulls_ignore_daytime)` | T — 14473218207379268379; SacredForestMeadow. [`sacred_forest_meadow.toml`](../../src/clawshot/data/world/sacred_forest_meadow.toml); range unplayed. |
| `Shadow Temple GS Falling Spikes Room` | `Progressive_Strength_Upgrade or Hookshot` | T — 15148554628675590606; ShadowTemple. [`adult_shadow_temple.toml`](../../src/clawshot/data/world/remake/adult_shadow_temple.toml). |
| `Shadow Temple Freestanding Key` | `(Silver_Rupee_Shadow_Temple_Invisible_Spikes, 5) and (Bombs or (logic_shadow_freestanding_key and has_bombchus))` | C — native skull-pot/explosive source; no remote item-fetch permission. [`adult_shadow_temple.toml`](../../src/clawshot/data/world/remake/adult_shadow_temple.toml). |
| `Shadow Temple Invisible Spikes Silver Rupee Ledge` | `Hookshot` | S — native puzzle family; retained traversal, direct fetch unproved. [`shadow_temple.toml`](../../src/clawshot/data/world/shadow_temple.toml); range unplayed. |
| `Shadow Temple Invisible Spikes Silver Rupee Right` | `Hookshot` | S — native puzzle family; retained traversal, direct fetch unproved. [`shadow_temple.toml`](../../src/clawshot/data/world/shadow_temple.toml); range unplayed. |
| `Shadow Temple Invisible Spikes Silver Rupee Left` | `Hookshot` | S — native puzzle family; retained traversal, direct fetch unproved. [`shadow_temple.toml`](../../src/clawshot/data/world/shadow_temple.toml); range unplayed. |
| `Shadow Temple Invisible Spikes Silver Rupee Near Ledge` | `Hookshot` | S — native puzzle family; retained traversal, direct fetch unproved. [`shadow_temple.toml`](../../src/clawshot/data/world/shadow_temple.toml); range unplayed. |
| `Shadow Temple GS Near Ship` | `can_use(Distant_Scarecrow)` | C/T — 8823884712433934372; ShadowTemple. [`adult_shadow_temple.toml`](../../src/clawshot/data/world/remake/adult_shadow_temple.toml). |
| `Spirit Temple GS Metal Fence` | `Boomerang or (logic_spirit_fence_gs and Kokiri_Sword) or (((Silver_Rupee_Spirit_Temple_Child_Early_Torches, 5) or logic_spirit_fence_gs) and (Sticks or has_explosives or Slingshot or can_use(Dins_Fire)))` | T — 10530233152473742636; SpiritTemple. [`spirit_temple.toml`](../../src/clawshot/data/world/spirit_temple.toml); range unplayed. |
| `Spirit Temple GS Lobby` | `(Small_Key_Spirit_Temple, 3) or spirit_temple_shortcuts or has_explosives or ((Small_Key_Spirit_Temple, 2) and free_bombchu_drops)` | C/T — 12959656942046734931; SpiritTemple. [`adult_spirit_temple.toml`](../../src/clawshot/data/world/remake/adult_spirit_temple.toml). |
| `Spirit Temple GS Hall After Sun Block Room` | `(is_child and Boomerang and (Small_Key_Spirit_Temple, 5)) or (is_adult and Hookshot and ((Small_Key_Spirit_Temple, 3) or spirit_temple_shortcuts)) or (Boomerang and Hookshot and (has_explosives or ((Small_Key_Spirit_Temple, 2) and free_bombchu_drops)))` | T — 10127391959410674946; SpiritTemple. [`spirit_temple.toml`](../../src/clawshot/data/world/spirit_temple.toml); range unplayed. |
| `Spirit Temple Shifting Wall Recovery Heart 1` | `Hookshot` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`spirit_temple.toml`](../../src/clawshot/data/world/spirit_temple.toml); range unplayed. |
| `Spirit Temple Shifting Wall Recovery Heart 2` | `Hookshot` | R — unshuffled/unlinked N64 pickup; exact remake route unverified. [`spirit_temple.toml`](../../src/clawshot/data/world/spirit_temple.toml); range unplayed. |
| `Water Temple GS Central Pillar` | `can_use(Longshot)` | T — 11571778270592589517; WaterTemple. [`adult_water_temple.toml`](../../src/clawshot/data/world/remake/adult_water_temple.toml). |
| `Water Temple GS Falling Platform Room` | `has_explosives` | C/T — 4399424945134189769; WaterTemple. [`adult_water_temple.toml`](../../src/clawshot/data/world/remake/adult_water_temple.toml). |
| `Water Temple GS River` | `(Iron_Boots and (Zora_Tunic or logic_fewer_tunic_requirements)) or (logic_water_river_gs and Longshot and (Bow or has_bombchus))` | C/T — 15506432733081566465; WaterTemple. [`water_temple.toml`](../../src/clawshot/data/world/water_temple.toml); range unplayed. |
| `ZR GS Near Raised Grottos` | `can_use(Hookshot) and (at_night or gold_skulls_ignore_daytime)` | T — 10917372215719266172; ZoraRiver. [`zora_river.toml`](../../src/clawshot/data/world/zora_river.toml); range unplayed. |
| `ZR GS Above Bridge` | `can_use(Hookshot) and (at_night or gold_skulls_ignore_daytime)` | T — 9450239379321634455; ZoraRiver. [`zora_river.toml`](../../src/clawshot/data/world/zora_river.toml); range unplayed. |
| `ZD GS Frozen Waterfall` | `can_use(Hookshot) and (at_night or gold_skulls_ignore_daytime)` | T — 9600417828645642589; ZoraDomain. [`adult_zoras_domain.toml`](../../src/clawshot/data/world/remake/adult_zoras_domain.toml). |
| `ZF GS Above the Log` | `can_use(Boomerang) and ((at_night and 'Time Flows') or gold_skulls_ignore_daytime)` | T — 7152962033963346563; ZoraFountain. [`child_zoras_fountain.toml`](../../src/clawshot/data/world/remake/child_zoras_fountain.toml). |
| `ZF GS Hidden Cave` | `Hookshot and (at_night or gold_skulls_ignore_daytime)` | T — 9537398183107003742; ZoraFountain. [`zoras_fountain.toml`](../../src/clawshot/data/world/zoras_fountain.toml); range unplayed. |

Additional regional pickup proxies (not location-rule matches):

| Rule | Remake evidence / disposition |
|---|---|
| `Lost Woods -> LW Underwater Entrance`: child `(can_dive or Boomerang)` | Only proxy check `LW Underwater Shortcut Green Rupee`; same unlinked/unshuffled ordinary-rupee boundary R. It does not bypass the separate scale/Boots river transition. No new access. |
| `Forest Temple NW Outdoors -> NW Outdoors Freestandings`: `logic_forest_courtyard_hearts and can_use(Boomerang)` | Two courtyard recovery-heart rows; R. Trick remains off; upper-ledge walking entrance remains. No remote heart-piece permission. |
| Remake `LLR GS Tower`: child Boomerang/adult Hookshot | Native Hash 2730878115209290675; `remake/token_routes.toml`, r15 played recovery/retrieval. Kept unchanged; included to distinguish actual remake token evidence from N64-only rows. |

**Answered by Kareem, remake play2026-11-21 (relayed by Claude): the Dodongo scarecrow
token, Hash960362013021648957, is reachable with the plain Hookshot.** This supersedes the
earlier unplayed range question. Add `can_use(Hookshot)`; retain the Scarecrow, Longshot and
disabled-trick branches. Marker6350453570889535478 and earlier guides do not override the
player's observed route. This is a narrowly played-supported loosening, not inferred range.

## 4. Distance switches

Read-only SwitchAudit inventory, integrated/corrected by cs20h. Detailed scratch matrix:
`E:/OOTRemake/work/r20-audit/switch-audit.md`; effective loaded-rule inventory:
`effective-ranged-rules.json` beside it. No OoTR/SoH code, game, seed or save was opened.
The table distinguishes actor admission from a particular room's range/timing; unknown is not played.

### Native target contracts

- **E (eye):** `Obj_EyeSwitch_A_02`, `_A_03`, `_A_05`, `_GlassTruth_A_02` share
  `Obj_EyeSwitch_A_02.root.ainb` (`828aa92ba43c…`); the timed `_A_05` graph (`e069065dbf3e…`)
  has the same filter. External damage types 6/14/15 pass, type16 is gated by `isHitHookShot`,
  and `IsFreeze` blocks the hit. Numeric weapon/type mapping is not proved merely by counting
  accepted enum values. Parent pack decoding resolves the scout's missing default:
  **all four packs set `isHitHookShot=true`**, overriding the graph's false default.
  No instance override was found in the cited placements. This establishes the named Hookshot
  gate's default, not a new physical Hookshot route. Played Boomerang on the room-2 Deku eye:
  [game-data section 12](../03-game-data.md), [DT01](../playtest/answers.md).
- **K (crystal):** `Obj_SwitchHit_*`, Jabu hit switches and the Lake entrance switch share
  `SwitchHitOnce.root.ainb` (`802968ce4930…`); attack admission reaches native
  `_LocalModule_8237c653e758`, not a decoded graph predicate. Parent decoding of the common
  SwitchHit pack adds no weapon-type whitelist; **do not invent one**.
  Played Jabu tonsil: bombs failed, Slingshot/Boomerang worked, Bombchus untested
  ([answers](../playtest/answers.md)). Lake Hookshot latch has the separately played
  [Ice end-chest gate](r16-water-gate.md).
- **F (fire):** candle graphs `BurnAndLockOnAttentionControlCandlestick` (`0145b909a66d…`)
  and `Obj_CandleStick_TimeExtinguish_A_01` (`c99030c10e49…`) use fire-contact and
  lit-Deku-Stick requests, not sword ownership or age. Ordinary arrows need an existing flame.
  Played Lake grotto: Din's lights three; child Sticks or adult Bow through a lit torch
  lights the fourth; adult Fire Arrows also works (`remake/extra_hyrule_field.toml`).
  That proves the mechanism there, not every other room's geometry/timer.
- **U (sun):** `Obj_Sun_A_01` graph (`b07f1a3df9f2…`) controls sun position/effect but has no
  decoded damage filter. The Fire Arrows trigger chain remains unmapped; no new route.

### Per-rule matrix

Paths are under `src/clawshot/data/world/`; remake filenames under `remake/`.
“Kept” means no new contradiction established, **not** full played certification.
Key counts, traversal and age conditions outside the named ranged clause remain unchanged.

| ID / rule (source) | Effective ranged clause / native evidence / disposition |
|---|---|
| DT1 Lobby → Slingshot Room (`deku_tree.toml`; `child_deku_tree.toml`) | Shield + usable Slingshot/Boomerang/Bow; E, room2 eye Hash9080063866993537303. Played Boomerang. Existing escape-tool tightening kept. |
| DT2 Slingshot Room → Lobby (`child_deku_tree.toml`) | Same tools/eye, ladder2096903280161003875. Played Boomerang return; Bow retained, not newly played. |
| DT3 Basement → Back Room (`child_deku_tree.toml`) | Fire + usable Slingshot/Boomerang/Bow; E, room5 eye10433048972954508847, same pack/filter/event as room2. Existing Boomerang clause kept; room5 range unplayed (Q1). |
| JB1 Beginning → Main (`child_jabu_jabus_belly.toml`) | Usable Slingshot/Boomerang/Bow/Hookshot replaces `can_use_projectile`; K, tonsil2499231676847862528. Played Slingshot/Boomerang; failed bombs already removed. Adult clauses cannot currently reach Jabu; no new certification (Q2). |
| JB2 Before Boss → Barinade (`jabu_jabus_belly.toml`) | Boomerang; ranged/explosive tricks remain disabled. K, barrier switch15394400859097041900; guide says curve around barrier. Kept. |
| DC1 Lobby → Torch Room (`dodongos_cavern.toml`) | Adult room admission unchanged; do not conflate entering with solving its exit. |
| **DC2 Lobby → Staircase Room** (`child_dodongos_cavern.toml`, formerly `master_sword.toml`) | **Tightened:** at Torch Room, child Sticks or usable Din's or (`adult_sword` + usable Fire Arrows). F, exact three-candle/shutter chain below. Adult sword/age alone removed; existing shuffled-sword guard retained. |
| DC3 Before Upper Lizalfos → Upper Lizalfos (`dodongos_cavern.toml`) | Child Slingshot (disabled skip trick) or usable Bow; E, timed eye16825617597899075770, room14, LimitTime10. Kept; Boomerang is Q4, not added. |
| DC4 Upper Lizalfos → Bomb Bag Ledge (`child_dodongos_cavern.toml`) | Existing combat clause + usable Slingshot/Bow; E, room17 eyes12790243399538496729 and13951311116548645685, LimitTime10, two fire walls. Kept. |
| DC5 Ledge → Upper Lizalfos (`child_dodongos_cavern.toml`) | Usable Slingshot/Bow through the same two eyes; kept. |
| FT1 Central Area → NE Outdoors (`forest_temple.toml`) | Usable Bow/Slingshot; site not mapped to a remake actor. E is only the generic filter; kept as Q5, not proof of child temple access. |
| FT2 Eye Switch Chest (`forest_temple.toml`) | Strength + usable Bow/Slingshot; census guide identifies gold eye behind metal grating (`location_names.toml`). E; kept. |
| FT3 Block Push Room → Straightened Hall (`adult_forest_temple.toml`) | Existing3 keys + usable Bow; guide eye above twisted-corridor entrance. E; kept. |
| FT4 Frozen Eye Room → Falling Room (`adult_forest_temple.toml`) | Usable Bow; native frozen-eye gate E, guide arrow through lit torch F. Din's alternative already removed; Q6, not restored. |
| FT5 Basement → Before Boss (`adult_forest_temple.toml`) | Usable Bow added by existing override for rotating-basement eye; kept. |
| FR1 Elevator → Boulder Maze Lower (`adult_fire_temple.toml`) | Existing3 keys/Strength + explosives/Bow/Hookshot. Ranged-switch actor not mapped; K weapon acceptance not established. Kept/Q7. |
| FR2 Compass Chest (`adult_fire_temple.toml`) | Narrow Path Room + usable Bow, guide thin-walkway eye, chest16713240760352215634 room16. E; kept. |
| FR3 Map Chest (`adult_fire_temple.toml`) | Existing override is True in Boulder Maze Lower; N64 Bow/6-key alternative already replaced. No ranged claim retained. |
| WT1 Raise Water Level (`adult_water_temple.toml`) | Hookshot + Lullaby +2 keys; old Bow/projectile alternatives already replaced by remake routing. Kept. |
| WT2 Lowered → Middle (`adult_water_temple.toml`) | Hookshot + Lullaby +1 key; old Bow/Din's alternatives already replaced. Kept. |
| WT3 Central Bow Target, Lowered/Middle (`adult_water_temple.toml`) | Lowered False; Middle Bow + Longshot + Iron Boots + Strength. Guide north eye then Longshot target; E plus traversal. Kept; disabled child-Slingshot trick adds no route. |
| WT4 Torches Chest (`water_temple.toml`) | Bow/Din's or child Stick/Sword/Magic branch retained. F requires a flame, but remake room/lit-torch source is unmapped; Q8, no speculative removal. |
| WT5 Dragon Statue/exit (`water_temple.toml`) | Existing Bow + survival/Boots conditions; remake notes mention eye-gate exit but exact counterpart unmapped. Kept/Q9. |
| WT6 River Chest (`adult_water_temple.toml`) | N64 Bow check already `n64_only`: no chest in remodeled rapids. |
| SP1 Lobby → Child Beyond Bridges (`spirit_temple.toml`) | Boomerang/Slingshot (Bombchu trick off), plus combat/silver-rupee conditions. Guide gap crystal lowered as bridge by Boomerang; K. Slingshot range unproved; kept/Q10. |
| SP2 Early Adult → Boulder Room (`spirit_temple.toml`) | Bow/Hookshot/Bombchus; Bombs trick off. Guide ceiling crystal; K acceptance for Bombchus unknown. Kept/Q11. |
| SP3 Child Climb North Chest (`spirit_temple.toml`) | `has_projectile(child/adult/both)` branches remain. Guide high crystal; K does not prove explosive rejection. Proposed key-branch deletion rejected below; Q12. East chest already N64-only. |
| SP4 Map Chest (`spirit_temple.toml`) | Existing age/key/fire/Sticks clauses; ordinary-Bow trick disabled. F, guide “any fire” on unlit torch. Kept. |
| SP5 Sun Block Chest (`adult_spirit_temple.toml`) | Existing window-light override replaces N64 torch/Bow branches; no ranged clause retained. |
| SP6 Anubis → Big Mirror Room (`spirit_temple.toml`) |5 keys + Longshot/Bombchu or explosive/stun + Bow/Hookshot/Hammer combination (wall trick off). Exact remake target unmapped; kept/Q13. |
| SP7 Boss Key Chest (`spirit_temple.toml`) | Lullaby + Bow + Hookshot; E for eye, guide says **Longshot** to lowered platform. That discrepancy is Q14; no geometry-by-eye fix. |
| SH1 Beyond Boat → Before Boss (`adult_shadow_temple.toml`) | Existing Bombs bridge override replaces N64 Bow/statue trick. Kept. |
| SH2 Spike Walls Left / Boss Key Chest (`adult_shadow_temple.toml`) | Existing5 keys + Din's, F. Fire Arrow/chain alternatives are Q15, not added. |
| SH3 Shadow entry (`graveyard.toml`) | Din's; Fire Arrow trick disabled. F; Q15. |
| GT1 Lobby Left/Right Chests (`adult_gerudo_training_ground.toml`) | Bow/Slingshot + Lens; E eye11495024771723587729, chest2436665354602612279. Existing conservative union for Lens west/Bow east kept. |
| GT2 Near Scarecrow Chest (`adult_gerudo_training_ground.toml`) | Bow + distant Scarecrow or Tunic/Hookshot/Lens route; guide floor eye-statue puzzle. E; kept. |
| GT3 Eye Statue Chest / Eye Statue Lower (`gerudo_training_ground.toml`) | Bow / Hammer+Bow; guide shoot statue eyes. E; kept. |
| GT4 Heavy Block → Like Like (`adult_gerudo_training_ground.toml`) | Silver Gauntlets + Bow + Lens; Lens-only eye10731754838093134223. E; kept. |
| GT5 Room10 seed chest (`extra_gerudo_training_ground.toml`) | Bow; E eye13939821958157812040. Hookshot default now resolved, but physical route not added (Q16). |
| GC1 Shadow First Gap (`adult_ganons_castle.toml`) | Longshot or Bow through existing lit torch; F, guide plus played Lake mechanism. Existing override kept; not new site play. |
| GC2 Shadow Second Gap (`ganons_castle.toml`) | Hover Boots or fire source; F. Bow chain not claimed. Kept. |
| GC3 Forest Wind Room (`ganons_castle.toml`) | Fire Arrows or Din's+(Bow/Hookshot); exact switch/torch site unmapped. Kept/Q17. |
| GC4 Spirit Crystal Chest (`ganons_castle.toml`) | Jumpslash or explosives; K, crystal6129545652928979383 room17; guide instead describes Torch Slugs. Trigger identity remains Q18. |
| GC5 Spirit Second Room Back (`ganons_castle.toml`) | Bombchus, grated switch; r4 adult audit kept it. K acceptance opaque; kept/Q11. |
| GC6 Spirit Ending (`adult_ganons_castle.toml`) | Existing adult Bow/Mirror + fire-source tightening for web; fire gate kept, not a new projectile-hit assertion. |
| OW1 LH Sun (`adult_lake_hylia.toml`) | Water Temple Clear + Bow, replacing Scarecrow alternative; U, guide dawn sun then swim. Existing rule kept/Q19. |
| OW2 Lake → Water Lobby (`adult_lake_hylia.toml`) | Hookshot + Iron Boots + Ice end-chest access; K plus played source gate. Kept. |
| OW3 Lake grotto chest (`extra_hyrule_field.toml`) | Din's+(child Sticks/adult Bow) or Fire Arrows; F, **played there** 2026-11-18. Kept. |
| OW4 Wasteland Chest (`haunted_wasteland.toml`) | Fire source; F general contract, site unmapped. Kept, no new route. |
| OW5 Royal Tomb chest (`graveyard.toml`) | N64 torch chest already excluded; real song-source combat is separate. |

Shared helpers: `can_use_projectile` includes explosives; its active token users are in the pickup
table, and its Jabu/Water switch users are already overridden above. `has_projectile(for_age)`
has an unconditional explosives disjunct; its only remaining non-excluded switch-check user is
Spirit Climb North (SP3); East is N64-only, Sun-on-Floor token has its remake override.
There is no `can_hit_switch`/`can_hit_eye_switches` helper.

Excluded from **switch** classification, not forgotten: DC mouth “eyes” are bombable
`Obj_DodongoCave_CrackWall_A_02` sockets (disabled Bombchu trick), DC staircase is a bomb-flower
chain, combat/painting/Poe/minigame targets are not switches, and pots/crates/wonderitems are
not freestanding retrieval. Tokens are inventoried in section3. Jabu's room13 chest has the
existing Boomerang-stopped swaying-floor rule, not a crystal-switch weapon claim.

### Applied tightening and rejected inference

**DC room8, proposed by SwitchAudit, corrected/integrated by cs20h:** parent readback follows
three timed-candle hashes7766157973751052842/3412578102610136516/1677399996748274653
to shutter18414161731649864422 and AiGroup13744671784328157797.
`DodongoCavern_Level_Room_08_Prefab_c4aa` (`1aadc586f8d5…`) ANDs their Burning outputs,
requests `DodongoCavern_Gimmick_CandleStickShutter` through actor13693449133434520250,
then saves `DodongoCavern_CandleStick`. Room entry remains unchanged.
The scout missed r19's effective `adult_sword` override; the first focused run printed that
duplicate-owner cause. The final override is owned once by `child_dodongos_cavern.toml`;
the obsolete sword-only placeholder is removed from `master_sword.toml`.
This is no longer a pure sword-on/off equivalence rewrite, so it belongs with native DC logic,
not in that test's source-enumerated rewrite inventory. No existing test was edited/deleted.
Dedicated reachability tests cover default fire/no-fire and shuffled-sword refusal/ownership.
Fire Arrows retain `adult_sword` as a conjunct: **subset of the prior effective rule even with
Master Sword shuffle on**. Swordless Fire Arrows and ordinary-Bow torch chaining require a
separate loosening decision; neither is added.

**Spirit key-free branch, proposed by SwitchAudit, rejected by cs20h:** owning projectiles for
both ages may represent cross-age solving; the region already needs its entry key. The native
attack filter/physical door chain does not establish that this branch is invalid or that3/5
keys are required for every route. Do not delete an inherited branch from syntactic suspicion
or guide prose alone. No key-count, helper or explosive-admission change made.

### Questions (nonblocking; no loosening applied)

- **Q1–Q4:** Can Boomerang physically hit Deku basement room5 and DC timed eyes within their
  timers? Do Bombchus hit Jabu's tonsil? What do Jabu room18/14 switches11882875599582784398/
  14718944193576846777 open? Existing conservative rules remain.
- **Q5–Q9:** Identify Forest NE courtyard eye, Fire elevator ranged switch, Water Torches Chest
  and dragon-statue targets; establish their native routes. Is there a lit flame for the Water
  bare-Bow branch? Does Din's melt Forest eye ice? No newly certified route.
- **Q10–Q14:** Confirm Spirit gap Slingshot range; Bombchu acceptance on Spirit/Ganon crystal
  switches; North Climb explosive/cross-age route; Anubis→mirror target; Boss Key Hookshot
  versus guide Longshot requirement. No range estimate or public-prose correction substituted.
- **Q15–Q19:** Shadow fire-arrow/torch-chain alternatives; physical Hookshot eye routes (the
  pack default itself is now resolved true); Forest Trial target; Spirit chest crystal versus
  Slug trigger; Lake dawn-sun native trigger. All retained as questions, not new access.
- **Q20:** Can ordinary adult Bow chain the DC timed candles in time? Can swordless Fire
  Arrows solve this path when Master Sword is shuffled? Native fire admission is not a played
  room traversal, so both possible loosenings stay out of scope.

## 5. Docs alignment

README/settings/logic aligned with released 0.2.4 + PR36, without other r20 feature text:
round19 lesson/farewell, LACS, House100 and Master Sword boundaries retained. Tracker docs now
explain shared dump-free logic preparation, saved inventory, age/filter semantics, version/location
gate, manual marks and unchanged OBS view; no played acceptance claimed. Corrected README's obsolete
progressive-unplayed claim using r14's played result (`r14-progressive.md:436-445`, six saved tops,
load lines and Continue; FULL PASS accepted by Claude). Proposed by DocsAlign, integrated by cs20h.
Lighting wording stays conservative: r16's broad round outcome says v4/v5 passed, but the later
explicit r18 docs review retracts that claim and the detailed r16 track ends at staging.
cs20h retained the lighting-unplayed disclaimer and removed logic.md's contradictory broad claim.

**Question for Claude (nonblocking): does a separate accepted v5 lighting play receipt exist beyond
r16's summary?** Until located, no new played certification; the late Forest-exit ordering stays
separately unplayed. Posted on `cs-r20`; no action needed from Kareem overnight.

## 6. Verification and handoff

Focused reachability: `CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2
tests/test_ranged_pickups.py tests/test_world_remake_play.py -q`: **31 passed in 37.47s**.
Game process check: no exact `hookshot.exe` or `longshot.exe` image. No unchanged rerun.
Read-only Markdown target/fragment check: **173 relative links, zero errors** before the final
switch/doc additions. Final link check follows source freeze.
Final four-document check after switch integration: **177 relative links, zero errors**.

DC regression follow-through (only cause-directed reruns):
- First combined run:37 loader failures, printed duplicate torch-exit owner
  `remake/master_sword.toml`; no unrelated failure diagnosis substituted.
- After single-owner correction:86 passed,2 failed. Printed one child fixture lacking usable
  explosives and the pure sword-rewrite off-equivalence assertion for a now-native fire rule.
- Native fire override moved to the DC owner; obsolete sword-only override removed.
  Existing Master Sword test source was not changed. Six cause-targeted nodes passed;
  remaining child fixture still failed because remake bombs also require Strength.
- Printed compact Search counts/rule reads and `remake/bombs.toml` established that prerequisite.
  The child torch scenario now uses real Goron Bracelet + Sticks (no bogus `Bombs` item);
  its isolated node **passed in1.37s**. No production bomb/search behavior changed.
- Post-rebase combined focus: **88 passed in18.58s**, `-n2`, `CLAWSHOT_WORKERS=1`,
  including `tests/test_master_sword_logic.py`; no game image running.

No new pack input resource or game-behavior patch: no paired launcher needed for these model
tightenings. Nothing requires Kareem overnight. No new check is called played here.
Logic and catalogue changes can change newly generated placements/spoilers/play notes for the same
recipe; existing outputs and saves are untouched. Maintainers own the next version bump.

### Gate admission order (Claude, 2026-11-20 23:02)

`work/rounds/r20/gate-order.txt`: cs20b exclude, then cs20d trials, then cs20h audit.
Audit acquires only after **cs20d posts LOCK RELEASED**, not from observing a missing lock.
No audit auto-retry waiter was running when this rule arrived; only read-only SwitchAudit remained.
The external runner exits rather than retries a held lock and now requires a manual
`--after-cs20d-lock-released` admission argument after that thread receipt is read.
Source freeze/current-main rebase/focused verification still precede the gate.

### Frozen sweep and sole pre-gate receipt (2026-11-21)

Explicit predecessor admission: cs20d's **01:56 LOCK RELEASED**. Current-main rebase retained
both exclusion docs and tracker docs in the one additive settings conflict. Frozen source/test head:
`4bd3dc4f4b38fd240ab5ddebd6f1c9b0597648d9` (rebased audit commits `9abc703`, `4bd3dc4`).
Focused88/88 passed before atomic acquisition of this track's lease. The notification watcher
could not acquire the lock; no out-of-turn waiter or additional matrix ran.

Canonical native setup uses `make_seed`'s actual prepared spec/settings/vanilla map and Gift
setup when selected, then stops before output writing. Same original broad CS1 in
`work/r18-fill/settings.txt`; no new option was added. Defaults/Recommended are actual app
presets. Private seeds20200000–20200199 (Broad),20200000–20200049 (each preset).
Six workers; no game at stage start; one retained lease through sweep, this receipt and gate.

| Recipe | Accepted | Exhausted | First-attempt failures | Attempts |
|---|---:|---:|---:|---:|
| Broad |200/200|0|10 (5%)|210|
| Defaults |50/50|0|2 (4%)|52|
| Recommended |50/50|0|2 (4%)|52|

All300 accepted, **zero exhausted**, max2 attempts. Sweep work505.969s; canonical setup plus
sweep stage537.547s, exit0. First failures are retry counts, not retained internal exception
payloads: no extra rerun was made to reconstruct discarded exceptions.
Broad retry seeds:20200024,20200032,20200043,20200055,20200093,20200165,20200170,
20200173,20200185,20200189; Defaults20200040/20200043; Recommended20200027/20200029.
Full normalized CS1 recipes, per-seed counts and completion receipts remain outside the repo:
`E:/OOTRemake/work/r20-audit/sweep-results.json`, `sweep-rows.jsonl`, `sweep.log`.
No output mod folder, player seed or save was written.

This is the **one round-file-only receipt** authorized by Claude at23:07 after the sweep and
before the full gate. Source/tests remain frozen; the receipt delta is checked before gate.
The final-head format/lint, synthetic `-n8/internal4`, then native dump `-n8/internal3`
write exact HEAD, commands, exit codes and durations to `work/r20-audit/gate-results.json`
and `format.log`, `lint.log`, `synthetic.log`, `dump.log`. The dump uses the required real
RomFS/NUP and read-only r19 sword-layered fixture; no new resource or fixture file is needed.
This paragraph does **not** preclaim those future results. Final **READY (merge)** requires
all four gate stages to pass; the exact tested head/results and LOCK RELEASED are posted on
`cs-r20`. No gameplay acceptance is being deferred or promoted by this logic-only track.

## 7. Played Scarecrow Hookshot follow-up (2026-11-21)

Requested/authorized by Claude from Kareem's played remake answer: the Dodongo's Cavern
Scarecrow Gold Skulltula is reachable with the **plain Hookshot**. Rebased onto requested
main`f8fb504`; add only `can_use(Hookshot)` to the translated source rule, preserving every
existing alternative. The inline source comment cites Kareem/date; generated-file header
now acknowledges cited remake corrections. No actor/source identity, setting or patch changes.
`docs/logic.md` names no Longshot requirement for this check, so it is unchanged.

Regression coverage: adult without a retrieval tool remains refused; plain Hookshot works
without Song/Longshot; existing Longshot works; child cannot use adult Hookshot. No new played
claim beyond Kareem's answer and no control launcher/game patch is needed.

Gate turn6, nobody ahead (Claude). At **every stage** check exact `longshot.exe`/`hookshot.exe`;
if present, start no heavy job and wait/retry every10 minutes. Broad200 + Defaults50 +
Recommended50 and the full gate remain mandatory. Prior audit receipts above are historical,
not this follow-up's verification. Follow-up receipts/scripts live separately under
`E:/OOTRemake/work/r20-audit/followup/` so previous gate evidence is preserved.
Focused verification: `CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n2
tests/test_ranged_pickups.py -q`: **18 passed in4.97s**; exact game-image check clear.
Status: source ready; new game-free serialized sweep/full gate pending.
