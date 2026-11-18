# Round 18, Track E — Master Sword shuffle design (cs18e SwordDesign)

Design only. Branch `r18/rewards`, base `2ba2f9a`. Per Kareem's 2026-11-18 decision
(`plans/rounds/r18-rewards.md`), Master Sword shuffle is **design only**: no setting is
added, no build flag or test is enabled, and nothing in this document is implemented or
played. Product contract being designed: **the adult has no sword until the Master Sword
item is found; the Temple of Time pedestal still moves time in both directions.**

Evidence base: supported native dump `e0f3ccfa`, read-only. Research files live under
`E:/OOTRemake/work/r18-rewards/sword/` (`sword-flow-hits.json`, `sword-gamedata.json`,
`sword-pouch.json`, `sword-graph-hits.json`, `sword-logic.json`/`.txt`, `traces.txt`,
`flows/*.txt`, plus the `scan_sword.py` / `dump_flows.py` / `trace.py` / `sword_logic.py`
read-only tooling that produced them). This session re-verified key facts directly against
the dump: entry-point mappings for `Dm_TimeTemple_0085` (live EVFL parse), pedestal
prefab logic strings (`Market_Child_Prefab_e700`, `Market_Adult_Prefab_89da`,
`Market_Child_Prefab_0fe5`, `Market_Adult_Prefab_50e3`), a whole-`Event/EventFlow`
string scan for `DoorOfTime_Draw` / `SageRoom_MeetGanondorf` / `Dm_TimeTemple_0040`
(which appear only inside `DoorOfTime.bfevfl` itself and in `Dm_TimeTemple_0040*.bfevfl`),
and a fresh re-dump of every flow file, byte-identical to the prior worker's dumps.

This document quotes only symbol names, event numbers and parameter values — facts about
the executable data — plus rule *names* from the MIT-licensed OoT Randomizer-derived logic
tables already vendored in this repository. No game asset, dialogue, model or decoded bulk
content is copied.

## 1. Scope fences

In scope: the Master Sword item only (`Weapon_Sword_Master`). This design leaves the
nine reward slots and completion readers alone. The Kokiri Sword retains its existing
shuffle policy and child-only usability; it is **not** made fixed by this proposal.
Other adult blades remain usable when actually owned: the contract forbids a free
Master Sword, not a legitimately found Biggoron Sword. Final-battle source operations
remain native only behind the ownership admission gate proposed in section 9.4.

## 2. Pin-reading convention used below

The flow dumps print raw switch pins (`cases=0->…,1->…`). Across these files **pin 0 is
the true/hit pin**. Verified three independent ways: `Dm_TimeTemple_0075` `Event0`
(`EventQueryHavePlayedEvent Dm_TimeTemple_0075`) routes pin 0 to the `Played` sub-entry
and pin 1 to `First`; `ReplaceEquipmentForEraChange` `Event4`/`Event10` fill weapon
defaults exactly on the empty-string and child pins; and `DoorOfTime`
`Event38/39/56` stone counting matches the semantics already accepted in the r18 reader
table (`DoorOfTime_GetStoneCount` = remaining quests). Where this document says
"played"/"not played" or "equipped"/"not equipped", it means that verified mapping.

## 3. Native state model (facts)

From `GameData/GameDataList.Product.110.byml.zs` (`sword-gamedata.json`):

| Field | Type | Save | Notes |
|---|---|---|---|
| `PlayerStatus.EquipWeapon` / `PlayerStatus.AnotherEraEquipShield`-family | String64 | file 0 | Current era / other era equipped-actor names; four fields (`EquipWeapon`, `AnotherEraEquipWeapon`, `EquipShield`, `AnotherEraEquipShield`) |
| `PlayerWeaponBeforeForceEquipMasterSword` | String64 | **SaveFileIndex -1** | Stash of the pre-demo weapon around forced Master Sword equips; not a per-file save field |
| `IsGet.Weapon_Sword_Master` | Bool | file 0 | Ownership bit |
| `PouchData.Weapon_Sword_Master.StockNum` | Int | file 0, ResetTypeValue 32 | Pouch stock |
| `Sequence_IsChildhood` | Bool | file 0 | Era selector, default true |
| `Step_DoorOfTime` | Enum | file 0 | `NotReady…Complete`; `Complete` is written by `DoorOfTime/Event93` after the first-pull chain |

There is **no** `IsGet.Item_Sword_Master`, `PouchData.Item_Sword_Master.StockNum`,
`IsGet.Weapon_Sword_Long` or `PouchData.Weapon_Sword_Long.StockNum` row: the Master Sword
is a `Weapon_*` pouch actor only. `HavePlayedEvent.Dm_TimeTemple_0050/0055/0070/0075` and
`Dm_SageRoom_0005` exist as ordinary scene-history bools.

From `RSDB/PouchActorInfo.Product.111.rstbl.byml.zs` and
`UI/Pouch/PouchTable/PouchTable.game__ui__PouchTable.bgyml` (`sword-pouch.json`):

- `Weapon_Sword_Master`: `PouchCategory` Weapon, `PouchGetType` **Small**, `WeaponType`
  SmallSword, `WeaponSubType` MasterSword, `EquipmentPerformance` 2,
  `IsAutoSaveAfterGet` true, sheath `Weapon_Sheath_070`; no `ActionGuideType`, no
  `AdultEquipment`/`ChildEquipment` override. `PouchTable.EquipmentArray` marks it
  `IsUsableAdult` only.
- `Weapon_Sword_Biggoron`, `Weapon_Sword_Giant`, `Weapon_Sword_BrokenGiant`: LargeSword
  rows, all `IsUsableAdult`; `Item_Sword_*` wrappers exist for get/trade handling
  (`Item_Sword_Kokiri` uses `ActionGuideType` AttackByWeapon). `Weapon_Sword_Kokiri` is
  `IsUsableChild` only.
- Get-window precedent: `GetPouchContent` exposes `DisplayGetByActorName` /
  `GetPouchContentByActorName*` entries whose grant event
  (`PouchSystemActor.EventTriggerAddOrRemovePouchContent`, actor passed as the
  `ActorName` variable) is fully actor-parameterized, and a dedicated
  `OpenGetWindow_Sword_Biggoron` entry exists with a second-get message row
  (`ActorMsg/PouchContent:Weapon_Sword_Biggoron_SecondGetMessage`). No equivalent
  second-get row exists for `Weapon_Sword_Master`; `IsGetEvent:false` on the native
  first-pull grant means the native pull plays no get window at all.

## 4. First pull — exact native chain

Gate (read-only strings, `Logic/Market_Child_Prefab_e700.logic.module.ainb`): the child
pedestal actor `Obj_TimeTemple_MasterSword_A_01_e482` exposes `ReceiveDoAction` through
`EventRequestActor_0b2e/_7fe2`, conditioned by `HoldChallengeCurrentStepCheckOrder`
against `Work/Challenge/DoorOfTime.game__challenge__Challenge.gyml` (`Step06`,
IsEqual/IsBefore/IsAfter) and `Work/Challenge/AllSage…` (`Ready`). The sword-discovery
scene when the child first enters is separate:
`Logic/Market_Child_Prefab_0fe5` plays `Dm_TimeTemple_0020` (see also
`DoorOfTime/DoorOfTime_DiscoverySword`, `Event159`) and writes the bool
`Market_Child_FoundMasterSword` plus
`Market_Child_TimeTemple_DeleteLightShaft_FirstTime_00`.

Chain (`flows/DoorOfTime.txt`, verified by `trace.py`):

1. `DoorOfTime/DoorOfTime_Draw` → `Event23`
   `EventQueryHavePlayedEvent{Dm_TimeTemple_0040}`.
   - **Not played (pin 1) — first pull**: `Event141` (beforehand-load SageRoom) →
     `Event104` → `Event99` `EventTransition Dm_TimeTemple_0030` (pull cinematic, no
     state writes of its own) → `Event97` `EventReserveBancChange{SageRoom,
     BootEventName SageRoom_MeetGanondorf}`.
   - **Played (pin 0) — repeat travel**: `Event22`
     `EventTransition Market_Child_Field_ChildToAdult` (section 5).
2. `DoorOfTime/SageRoom_MeetGanondorf`: `Event143` (load SageRoom) → `Event94`
   `EventTransition Dm_TimeTemple_0040` → `Event186` wait 180 → **`Event115`
   `PouchSystemActor.EventTriggerAddOrRemovePouchContent{Actor Weapon_Sword_Master,
   Num 1, IsEquipDIrect true, IsSetMessageTargetActorName true, IsGetEvent false}`** —
   the one and only first-pull ownership writer — → `Event98`
   `ReplaceEquipmentForEraChange` → `Event103` `Sequence_IsChildhood=false` → `Event144`
   BancChange SageRoom / `SageRoom_MeetRauru`.
3. `DoorOfTime/SageRoom_MeetRauru`: `Event142` (load Market_Adult) → `Event95`
   `Dm_SageRoom_0000` → `Event101` `Dm_SageRoom_0005` (Rauru/Light scene; contains no
   sword operation) → `Event96` BancChange Market_Adult /
   `Market_Adult_AllSage_Start` → `Event102` Recovery → `Event93` `DoorOfTime Complete`.
4. `AllSage/Market_Adult_AllSage_Start`: `Event9` `Dm_TimeTemple_0050` (timeline) →
   `Event0` `Dm_TimeTemple_0055` (Sheik dialogue) — the two-event first adult arrival
   already accepted in r10 (`plans/rounds/r10-agetravel.md`).

Corrected research-script limitation: the reader parses both demos as **timelines**;
`dump_flows.py` incorrectly dereferenced their absent flowchart and raised AttributeError.
The aimed timeline inspection succeeded: `_0040` has 129 clips (including three
`Dm_Sword_Master.EventModelBind` clips), `_0050` has 92 clips (including Player
`EventTriggerEquipmentUserRequestChangeState`, slot0/state1). No canonical sword-pouch
grant appears in those root clips. Their Effect/Env subtimelines and native actor-code
internals are not exhaustively audited; do not mistake that limit for a format failure.

## 5. Repeat draws / era travel — exact writers

Two symmetric field flows drive the pedestal after the first pull:

- `Market_Child_Field_ChildToAdult` (child → adult): `Event9` load Market_Adult →
  `Event2` `EventTransition Dm_TimeTemple_0080` (child binds the pedestal sword
  `Land_HrlCity_MasterSword` to `Dm_Locator`, `C01_Player_Trans`, sword-shine XLinks; no
  pouch/equip state writes) → `Event3` `ReplaceEquipmentForEraChange` → `Event1`
  `Sequence_IsChildhood=false` → `Event4` `EventQueryIsExistInPouch{Armor_Adult_Gauntlet_Silver}`
  → `Event7` `HavePlayedEvent.Dm_TimeTemple_0088` → boot `Dm_TimeTemple_0085`
  (default / gauntlet-owning-but-0088-unplayed) or `Dm_TimeTemple_0088` (gauntlets owned
  and 0088 already played once).
- `Market_Adult_Field_AdultToChild` (adult → child): `Event6` load Market_Child → timer
  guard (`SubEvent_TimerCheck_ToChild`, `EventQueryMiniGameTimerIsCounting`) → `Event8`
  look-lock → `Event2` `EventTransition Dm_TimeTemple_0070` → `Event7`
  `ReplaceEquipmentForEraChange` → `Event1` `Sequence_IsChildhood=true` → `Event0`
  BancChange Market_Child / boot `Dm_TimeTemple_0075`.

Arrival/departure demos that touch sword equipment:

| Flow / entry | Events | Operation |
|---|---|---|
| `Dm_TimeTemple_0070` (adult stabs sword back) | `Event3` | Copy `PlayerStatus.EquipWeapon` → `PlayerWeaponBeforeForceEquipMasterSword` |
| | `Event13`/`Event27`/`Event4`/`Event26` | If `Weapon_Sword_Master` not equipped (pin 1): fork `EventTriggerEquipmentUserRequestCreateStaticEquipment{Weapon_Sword_Master, DynamicEquipmentState 1}` + re-check; then `Event15` ChangeState (slot 4) |
| `Dm_TimeTemple_0075` (child arrival) | `Event0`/`Event25`/`Event26` | `HavePlayedEvent` pick of `Played` vs `First` sub-entries; pedestal model participate only |
| `Dm_TimeTemple_0085` (adult arrival, default) | entry `other` → `Event15` fork → `Event11` warp → `Event30/31/37` | Three `EventQueryPlayerIsEquipWeapon` checks (Biggoron/Giant/BrokenGiant, all "not equipped" pins) guard `Event9` `EventTriggerPlayerRequestCreateDynamicEquipmentNoRelationPouch{Weapon_Sword_Master}` |
| | entry `C01` → `Event10`/`Event12`/`Event5` | ChangeState then `EventTriggerPlayerEquipDynamicEquipmentFromPouch` (re-equip the pouch weapon) |
| `Dm_TimeTemple_0088` (gauntlet first-arrival variant) | `Event35` | Copy `PlayerStatus.EquipWeapon` → `PlayerWeaponBeforeForceEquipMasterSword` |
| | `Event29`/`Event32`/`Event28`/`Event31`/`Event27` | If Master not equipped: fork `CreateStaticEquipment{Weapon_Sword_Master}` + re-check; ChangeState slot 4; also sets `HavePlayedEvent_Gauntlet_Silver_First` (`Event10`) |

`ReplaceEquipmentForEraChange` (`flows/ReplaceEquipmentForEraChange.txt`) is the era
equipment swap: `Event0/1` swap `EquipWeapon`↔`AnotherEraEquipWeapon`, `Event2/3` the
shields; when the other-era weapon string is empty, `Event4`+`Event10` fill a default —
`Event5` writes **`Weapon_Sword_Master`** for the adult side, `Event11` writes
`Weapon_Sword_Kokiri` for the child side; `Event6` pin "childhood" routes `Event7`:
Copy `PlayerWeaponBeforeForceEquipMasterSword` → `AnotherEraEquipWeapon`, restoring the
pre-demo adult weapon. Two facts matter for this design:

1. **The native weapon defaults are unconditional.** `Event5` arms any newly-adult
   player regardless of pouch contents. This is one free-weapon writer, not the only
   risk: the demos above also construct pouch-independent pose equipment. Track B's
   current Kokiri return repair is separate; a future Master Sword option must build
   on that merged equipment path, not restore the old native swap implementation.
2. `PlayerWeaponBeforeForceEquipMasterSword` is written only by `Dm_TimeTemple_0070
   Event3` and `Dm_TimeTemple_0088 Event35`, and read only by
   `ReplaceEquipmentForEraChange Event7`; it is `SaveFileIndex -1`, so it is not a
   durable per-save restore source.

The parsed event-flow scan found no additional Master Sword grant/equip/removal sites
beyond these and the finale sites below. This is not exhaustive native-code coverage:
the Effect/Env subtimelines and native actor logic remain explicit audit limits.

## 6. Story / final-battle forced equipment (audited data-flow sites)

These create or remove Master Sword equipment for scenes; they never write ownership
except the two pouch operations marked:

| Site (flow / entry) | Events | Operation |
|---|---|---|
| `Dm_SY_BancChangeArrive/KakarikoVillage_Arrive` (burning Kakariko arrival) | `Event37` | `CreateStaticEquipment{Weapon_Sword_Master}` before `Dm_Kakariko_0030`; `Event496` Unequip after; BancChange `KakarikoVillage_Adult/KakarikoVillage_FlashbackScenes` |
| `AllSage/Market_Adult_Field_GetArrowLight` (Light Arrows scene) | `Event175` | `CreateStaticEquipment{Weapon_Sword_Master}` ahead of the `Dm_TimeTemple_0090/0095/0110/0115/0125` chain; `Event165` Unequip |
| `Defeat_Ganon/InsideGanonCastle_Dungeon_BossAppear_2` | `Event785` Unequip → `Event33` `CreateStaticEquipment{Weapon_Sword_Master}` → `Event66` `EventQueryPlayerIsEquipWeapon{Weapon_Sword_Master}` | Ganondorf arena entry arms the sword and then waits on it; `Event59` `EventTriggerRemoveWeaponKeepSheath{Weapon_Sword_Master}` strips it again at the Ganon transition (Step08) |
| `Defeat_Ganon/InsideGanonCastle_Dungeon_BossDie_1` | `Event217` | `CreateStaticEquipment{Weapon_Sword_Master}` before `Dm_InsideGanonCastle_BossOut` |
| `Defeat_Ganon/InsideGanonCastle_Dungeon_Boss_GetMasterSword` | `Event657` | Dream-world-aware in-fight sword-retrieval entry (dream pin routes to `DreamWorld_CreateWarp`) |
| `Dm_FinalBattle_0010/PlayerAddPouchAndEquip` | `Event137` sets `FinalBattleField_ShouldDeleteMasterSword=true` → `Event173` **`AddOrRemovePouchContent{Weapon_Sword_Master, Num 1, IsEquipDIrect false}`** → `Event260` `CreateStaticEquipment` → `Event256` ChangeState | The only *other* ownership writer: a native safety re-grant of the sword for the finale |
| `Dm_FinalBattle_BossOut.110/C01` | `Event62` SW equipped Biggoron → `Event205` `CreateDynamicEquipmentNoRelationPouch{Weapon_Sword_Master}` → `Event207` wait-create → `Event252` PlayerDrawn → `Event164` `EventTriggerPlayerEquipmentMasterSwordNotShine` → `Event54` `Weapon_Sword_Master.EventTriggerModelBind` | The Ganon pick-up pose; explicitly pouch-independent |
| `DreamBossStage.110/Rematch_Ganon_Start` and `/Ganon_GD_Reset` | `Event548` `RemoveWeaponKeepSheath{Weapon_Sword_Master}`; `Event483` resets `FinalBattleField_ShouldDeleteMasterSword=false` together with the `HavePlayedEvent.Dm_FinalBattle_*` resets | Boss-rush/dream rematch handling |
| `Logic/Enemy_DungeonBoss_Ganon_Prefab_4524.logic.module.ainb` | strings `FinalBattleField_ShouldDeleteMasterSword`, `Obj_GanonCastle_MasterSword_A_01_6b5d`, `Weapon_Sword_Master_5f14` | The Ganon arena's dropped-sword object and its delete flag live in actor logic, not in a flow |

Peripheral readers of the *equipped* sword (no ownership effect): `Dm_SY_GetInEvent/
BigGoronSword_GetAndEquipCheck` (`Event635/630/634/632` polls equipped
Master/Biggoron around the Biggoron hand-over), `Dm_WaterTemple_0015/C09`
(`Event137/114/129/130`, Navi targeting by equipped blade),
`Common_Dungeon_OpenShutterMove` (`Event298`, equipped-Biggoron branch),
`Enemy_Scrub_Business_Dream` (`Event40/42/263/264`, equipped Giant/Biggoron checks),
`Dm_FinalBattle_BossOut.110 Event62`, `Dm_TimeTemple_0085 Event20/22/36`. The full scan
counted 66 `EventQueryPlayerIsEquipWeapon` events across all flows. Big-sword inventory
writers for reference: `Npc_Goron_Biggoron_Adult Event96/106` (remove Giant/BrokenGiant
during the trade), `SimpleShop Event115` (remove BrokenGiant on repurchase of
`Shop_Sword_Giant`).

## 7. Public logic — implicit adult-armed helpers

Current public logic state (`src/clawshot/data/world/`): there is **no** `Master Sword`
item in `items.toml` (Kokiri Sword, Giants Knife, Biggoron Sword exist); the pedestal is
modelled as the `Beyond Door of Time` region event `"Time Travel" = "True"`
(`temple_of_time.toml`, OoT Randomizer `Overworld.json:1326`); `tracker/state.py:162`
already maps `master_sword` ↔ actor `Weapon_Sword_Master`. The rule graph therefore
assumes every adult holds the Master Sword, exactly like the native data does.

The counterfactual spec (`sword_logic.py`, read-only) defines
`adult_sword = "is_adult and (Master_Sword or Biggoron_Sword or Giants_Knife)"` and
rewrites the bare `is_adult` idiom in **40 helpers** (changed-rule count 90 total,
`sword-logic.json`): `can_cut_shrubs`, `can_stun_deku`, `can_mow_the_lawn`,
`can_jumpslash`, the `can_kill_*` family (armos, biri, bari, tailsparan, stinger,
tektite, skulltula, wolfos, redead, keese, keese_stationary, scrub, blue_bubble,
green_bubble, floormaster, wallmaster, like_like, lizalfos, lizalfos_with_bombs,
dinolfos, withered_deku_baba, dodongo, dodongo_with_bomb_flower, gohma_larva,
baby_dodongo, stalfos, iron_knuckle, guay, flare_dancer, torch_slug, freezard), and the
glitch helpers `can_isg`, `can_lunge_storage`, `can_oi_with_item`, `can_gdv_stick`,
`can_js_clip`. Five helpers were deliberately **not** rewritten (armed-irrelevant):
`can_leave_forest`, `has_shield`, `can_shield`, `can_ride_epona`, `is_adult`. Five
hand-reviewed rules carry explicit sword
requirements (citations as recorded in the research): `Defeat Phantom Ganon`
(Bosses.json:92), `Defeat Morpha` (Bosses.json:141), `Defeat Twinrova` (Bosses.json:194),
`Triforce` = Light_Arrows and Master_Sword (`Defeat_Ganon` BossAppear_2
`Event33`/`Event66` wait on an equipped Master Sword; Bosses.json:267), and the
`Water Temple Falling Platform Room -> Dark Link Region` exit
(`remake/adult_water_temple.toml`). This is a **proposal attached to the future option**;
none of it is applied to the shipped tables.

## 8. Counterfactual reachability — hypothetical, data-only, NOT approved logic

Method: `sword_logic.py` builds the vendored rule graph twice, once natively and once
with the section-7 rewrite. It uses a maximal vanilla-named pool from every world
location, **including unsupported/N64-only definitions**, withholding adult swords in
the proposed view. This is not the production pool or a generated seed. The results
are hypothetical, unplayed capability deltas, not approved remake combat logic.

| Run (pool) | any-reachable | adult | child | wins |
|---|---:|---:|---:|---|
| base (1410 items) | 1395 | 952 | 705 | yes |
| none (1408, no adult sword) | 1370 | 921 | 695 | no |
| none + Biggoron Sword | 1395 | 952 | 705 | no |
| none + Master Sword | 1395 | 952 | 705 | yes |
| none, no Megaton Hammer | 1333 | 880 | 695 | no |
| base, no Megaton Hammer | 1355 | 908 | 705 | no |

Events lost with no adult sword: `Defeat Morpha`, `Defeat Phantom Ganon`,
`Defeat Twinrova`, `Triforce`, `Water Temple Clear`. Named checks that become
unreachable (25, by region): Beyond Door of Time — *Sheik at Temple*; Death Mountain —
*DMT GS Above Dodongos Cavern*; Death Mountain Summit — *DMT GS Falling Rocks Path*;
HF Inside Fence Grotto — *HF Deku Scrub Grotto*; Hyrule Field — *Hyrule Field Chest
(Obj_Heart_Piece)*; Kak Windmill — *Kakariko Village Chest (TBox_Rupee_Purple)*
[Adult Alternative]; Lake Hylia — *LH Sun*; Morpha Boss Room — *Morpha*, *Water Temple
Morpha Heart*; Phantom Ganon Boss Room — *Forest Temple Phantom Ganon Heart*,
*Phantom Ganon*; Twinrova Boss Room — *Spirit Temple Twinrova Heart*, *Twinrova*;
Water Temple Dark Link Region — *Like Like Pot 1/2*, *Water Temple Longshot Chest*;
Water Temple River — *GS River*, *River Chest*, *River Pot 1/2*, *Recovery Heart 1–4*;
ZD Shop — *Item 4*. Eight further checks are lost to the adult only while the child
still reaches them: *HF GS Lone Tree* and *ZD Shop Item 1/2/3/5/6/7/8*.

Retained alternate weapons, from the same analysis: a single **Biggoron Sword restores
every location above** (bgs run equals base; only the `Triforce` win event stays lost —
the final battle requires the Master Sword itself), and **Giants Knife counts the same**
in the rule graph (break-to-BrokenGiant is not modelled; that durability gap is a known
inaccuracy of this analysis). Removing the Megaton Hammer on top of the sword loses more
locations (1370→1333) but **no additional events** (`nohammer_extra_lost_events` empty);
the hammer is not an adult-sword substitute for any boss/event rule.

## 9. Implementation boundaries (design, not implemented)

### 9.1 Source-safe grant
The pedestal gets a separate first-pull item location; its time-travel event, Rauru's
nine-reward-pool slot and the native first-arrival song remain separate. Master Sword
shuffle must not put an ordinary item into Rauru's closed reward palette.
When the pedestal holds a different item, replace `DoorOfTime/Event115` with a
source-bound standard get pipeline that grants that item once, presents its correct
window and does not force-equip arbitrary replacement gear. A blind Actor string swap
retaining the native sword's `IsEquipDIrect=true` is insufficient.

The relocated Master Sword must be granted **at its actual found location**, through
a destination adapter validated for `Weapon_Sword_Master`; never keep a hidden sword
grant at the pedestal as well. Its canonical ownership is `IsGet.Weapon_Sword_Master`
and `PouchData.Weapon_Sword_Master.StockNum`. Chest/gift presentation for this weapon
is unplayed and must pass its own source/window/equipment check before admission.
No second-get message row exists; select an existing supported get-window route or
author the needed text row, then verify it. Do not advertise an unproven adapter.

### 9.2 Autoequip + time travel
The pedestal keeps time travelling: `DoorOfTime_Draw` routing, `Dm_TimeTemple_0030`,
`Dm_TimeTemple_0040`, the Rauru/AllSage chain, `Sequence_IsChildhood` flips, both field
flows retain their real quest/era transitions. Required edits include the first-pull
grant above and ownership checks before **every** restore/default that can arm an
unowned sword, including `ReplaceEquipmentForEraChange Event5/7` and the pose-demo
boundaries. Check the actual candidate weapon: preserve an owned Biggoron/Giant blade,
not merely Master-Sword ownership. An empty adult slot stays empty.
The demos (`Dm_TimeTemple_0085 Event9`, `0088 Event28`, `0070 Event4`) may still need
a temporary cinematic prop for the native pose. It must be removed/restored before
playable control returns, without writing ownership or replacing another owned blade.
That lifetime is unverified; test first arrival, both return directions, Save/Continue
and reload. Do not leave it as a ship-time question or assume a model is harmless.

### 9.3 Child-return guarantee
Native adult→child travel is gated by `SageOfForest_IsCompleted_Exp`
(`Logic/Market_Adult_Prefab_89da`, per the r18 reader table; free-time-travel from r10
removes that gate when enabled). The counterfactual shows `Defeat Phantom Ganon` is
unreachable without an adult sword, so an unarmed adult who has not cleared Forest
cannot return to child natively. Two boundaries satisfy the guarantee, and choosing
between them is **Kareem's open decision**, not this document's: (a) fill-side — the
filler must place the Master Sword reachable from the post-pull adult state without
child return; or (b) option-side — enable the existing free-time-travel return pedestal
whenever sword shuffle is on. Either way, `Market_Adult_Field_AdultToChild`,
`Dm_TimeTemple_0070/0075` and `Sequence_IsChildhood` stay native; the guarantee is
reachability, never a new flow.

### 9.4 Ganon requirements
Require real Master Sword ownership **before the final-battle admission surface**,
not merely in the final `Triforce` rule. Otherwise a swordless player could enter and
receive the native forced equip/re-grant, violating the shuffle contract even if the
solver refuses to count that win. The proposed native admission guard must refuse or
return the player safely before the irreversible fight starts, with matching entrance
logic; the exact outside-arena trigger needs a data trace before implementation.
Behind that gate, retain the native finale poses, dropped-sword retrieval, removal
and `Dm_FinalBattle_0010/Event173` restore of an already owned blade. Biggoron alone
must not satisfy that ownership gate. Never fake ownership to make a scene proceed.

### 9.5 Stays native, explicitly
`DoorOfTime` challenge steps and `Event93 Complete`; the door's stone-completion readers
(`Event38/39/56`, `DoorOfTime_GetStoneCount`); `Market_Child_FoundMasterSword`,
`Dm_TimeTemple_0020`, light-shaft flags; the Kokiri Sword and all child-era equipment;
shield-era swap logic; `PlayerWeaponBeforeForceEquipMasterSword` lifecycle; boss-rush
dream resets.

## 10. Staged-control plan (estimates only; nothing enabled)

No setting, build flag or test exists for this design; the following is the honest
control plan for whenever it is implemented, following the in-game test-state rules:
backups scanned read-only, test states are copies of one natural slot plus account and
options into an isolated profile, and any stage without a natural candidate is dropped
rather than fabricated. Packet counts are estimates; every stage ends in Kareem playing,
not agent claims.

- **A. First pull with the sword elsewhere** (planning estimate **5–10 min per arm**):
  Use a natural child snapshot at DoorOfTime Step06 with no first-pull history; the
  2026-11-09 main-adult-first child copy selected in `r18-rewards.md` is one example.
  The diagnostic seed places the Master Sword away and a legal item at the pedestal. Observe:
  (0030/0040/Rauru/0050/0055), pedestal item granted through the standard get window,
  adult arrives unarmed, `IsGet.Weapon_Sword_Master` false in the tracker.
- **B. Unarmed adult traversal** (planning estimate **15–30 min**, using stage A's output):
  No natural vanilla adult should be unarmed from lack of ownership. Obtain that
  candidate state by playing stage A forward, never by deleting saved ownership.
  Vanilla-adult saves serve as the comparison control. Observe: era swap does not arm the
  player (9.2 guard), big-sword/hammer alternatives still work, no pose sword persists
  after `0085/0088/0070` demos (the unverified risk in 9.2).
- **C. Child return and repeat crossing** (planning estimate **10–15 min**): adult saves from stage B;
  return-gate behavior per the 9.3 decision, repeat crossings in both directions, save
  and reload mid-cycle (`PlayerWeaponBeforeForceEquipMasterSword` is unsaved — check a
  reload during a demo-forced state does not strand an armed visual).
- **D. Finale** (planning estimate **20–40+ min** from a suitable natural save, otherwise dropped):
  Use a natural castle-era snapshot from the shuffled run. If none exists, drop that
  control rather than manufacture its story, inventory or boss state.

## 11. Audit status

The native **code** audit for this feature is incomplete: no native binary or
disassembly claim is made anywhere above, and nothing here should be read as one. All
evidence is data-layer (event flows, GameData tables, RSDB pouch rows, ainb logic
strings) from dump `e0f3ccfa`, scanned read-only on 2026-11-18. The separate native
reward binary audit is owned by the parent and is not appended here.
