# Round 22, track logic (cs22d)

Branch `r22/logic`, gated base `5bc5577` (initial base `2091387`). Work/research and staged packets:
`E:/OOTRemake/work/r22-logic/`. No game or boot check run by this agent. Runtime for every new checklist:
**Longshot 3.2.0**, stable `builds/stable/v3.2.0/bin/longshot.exe`.

Product commits before final rebase/gate: `5b6041f` downstream wall; `fb3b676` explicit Ice gift credit (admission
held); `55a6568` reflected Beamos kills; `0440ac8` two Goron flower uses; `387df4c` adult DC flower/arrows.
Ice and three paired DC physics checks are staged, dry-run/read-back verified, **built, not played**.
Gate complete on frozen product `84582cc`; test-contract/receipt-only child follows. See final READY below.

## Scope and acceptance

1. Audit every Dodongo's Cavern explosives rule against adult-accessible Bomb Flowers and its target's damage/material
   and trigger chain. Loosen only with an end-to-end native chain or played check (rule h). Include round 21's two
   Hammer-on-growing-flower candidates. Stage unresolved routes, preferring a natural adult pre-Bomb-Bag backup.
2. Mirror the upstream Zora's River wall predicate downstream. Tightening; no new play needed.
3. Stage an Ice Cavern compass from Sheik's lesson, with Gift and songs anywhere. Keep the round-21 chest hold until
   Kareem plays it; any loosening is a separate final commit after the pass.
4. Before READY: rule-2 sweep (200 broad, 50 Defaults, 50 Recommended; paired placement/sphere digests, plus binding
   cohort if standard placements are unchanged), then ordered exact-head gate. Completed; see final READY.

## Played facts, not new certifications

- Kareem, Longshot 3.2.0, Clawshot 0.2.6, 2026-11-24: entered Dodongo's Cavern as adult, progressed with Goron's
  Bracelet and Bomb Flowers until finding the Bomb Bag, then finished. The tracker credited none before the bag.
  This does not itemize every chest, side route or Hammer-chain puzzle.
- Kareem, Longshot 3.0.0, 2026-11-23: a Hammer hit explodes a Bomb Flower where it grows. It does not establish
  carrying one, reaching the staircase's flower, or opening either candidate chain (`r21-hammer.md:227-243`).
- Kareem, Longshot 3.2.0, 0.2.6: coming downstream from Domain/Lost Woods, met the invisible wall and bomb rocks.
  He could return through Lost Woods/Field. No additional play requested for this tightening.

### Authorized played-save strength inspection

Claude authorized save-only inspection of `work/tester-reports/2026-11-24-kareem-seed-1942692550/user/save/`
`5a3c9e1f0b7d24680000000000000001/slot_00..05`. `played_strength.py` copied only `progress.sav` and `caption.sav`
first to `work/r22-logic/played-save-copies/`, then read those copies; source progress hashes matched afterwards.
No seed metadata or placements were read in this inspection.

All six retained snapshots have `IsGet.Armor_Child_Gauntlet_Goron=true`,
`PouchData.Armor_Child_Gauntlet_Goron.StockNum=1`, both adult Silver/Gold canonical ownership flags false and
stocks zero, and `PlayerStatus.LiftGrade=3655598229` (`Low`). Slots 00 and 02 have `Sequence_IsChildhood=false`.
All retained snapshots are already post-bag: small and medium bags owned, capacity 30,
`IsTreasureBoxOpen.12161709650443144121=true`. They do not preserve the pre-bag moment.

`HavePlayedEvent.Dm_Goron_0030=false` in all six copies. Thus native Darunia-source Bracelet ownership is **not**
established; a chest strength copy is the likely source **[INFERENCE]**, and R14 already counts that copy as adult
strength. Do not claim that R14 caused the tracker symptom. R14's global source/copy policy stays unchanged.
The played physical capability is precise: adult Link with the Bracelet/Low, no adult gauntlets, lifted and carried
the cavern's Bomb Flowers before obtaining the Bomb Bag (Kareem's report); these later saves corroborate the
strength type/state, not the earlier bag state. Native fruit lift requirement is Low (`03-game-data.md` 30–31).

### Scope choice and round-23 adult-flower candidates

Claude offered either class-wide adult Low-lift flower widening or scoped changes with other candidates recorded.
**cs22d chooses audited DC routes plus the two explicitly played Goron City routes** (added to scope by Claude at
15:25). No global R14 policy changes for bag bombs, boulders, silver rocks or requirements above Low. A raw strength
copy already counts as adult lift; the new case is the fixed native Bracelet without a counted copy, with the same
canonical actor/Low lift. Native fruit prompts are age-independent; provenance does not change that actor's lift.

The remaining round-23 candidates are `GC Medigoron`, `GC Medigoron Pot`, `GC Medigoron Gossip Stone`, and its
`Fairy` event. They are **not newly admitted routes**:
Identify each explosive target and trace its flower transport/ignition, damage and
trigger before replacing a strength term. The adult Dynamic file does place `Obj_BombFlower_A_03`, including
11013514348003146524 and 3562235230987271562 on the upper ring, 9706505068154001370 and 7238665186396676143 on the
middle ring, and 3836103259887876426, 18242055162326079420, 12870355935252220470 by the lower northern passage
(`work/r21-hammer/placed.json`). Coordinates alone do not establish a target or a carry path.
The child-only shop/pot/rolling rules and child scripted cavern-entry flower are not adult candidates.
Death Mountain's adult Bomb Flowers in that inventory are inside the Storms grotto (y 58), not the child-only
scripted entrance flower above the cavern; no new surface flower route is inferred.

## Dodongo's Cavern audit and changes

Source: read-only supported dump, existing r21 damage inventory plus fresh pack/AiGroup/graph readback. Research:
`work/r22-logic/dc-flowers-audit.md`, `dc_flower_targets.json`, `dc_aigroups.json`, `dc_merged_rules_now.json`,
`dump_ainb.py`, `packs.py`. GPL `ainb` decoder was used unmodified outside the repo; facts only. No OoTR/SoH code.

### Flower -> blocker chain and capability boundary

`Obj_BombFlower_A_02` (chain plant) and `_A_03` (loose plant) create/regrow `_A_01` fruit at runtime via
`ActorHolderParam/Obj_BombFlower_Grass` (`BombFlower_Fruit`, AutoRecreate). Its lift grade is **Low**, and
`Obj_BombFlower_Fruit.root` nodes87-93 check `IsGet.Armor_Child_Gauntlet_Goron` for the pickup prompt without an age
test. All DC placements share one Banc; none of these flowers is in an age-conditioned group. Existing flower carry
routes below stay on the same floor (target/flower height delta -0.8 to +1.3 m); no remote ledge route is added.

Fruit damage `BombFlower_Fruit`: Hammer/Arrow/Fire/Hookshot/other named attacks rate1, Bomb rate0, life1.
Damage -> `IsHit AND IsOnDamageType` -> `OneShotDeathRequestDeath`; lifting or direct-fire contact also starts
the fuse. Chemistry material `BombFruit` is explosive, blast `BombFruit_ExplodeBlast`: Blast/Explosion,
StrongFire, size4.3, Bomb attack power2. Bag bombs and Bombchus share that blast/material. This alone does **not**
prove an explosion ignites all timed candles or starts the multi-flower manager; those alternatives stay held.

Every ordinary wall below inherits `WallCrack`: `CrackStoneObject` Bomb100/Hammer100, life6, Arrow/Fire0;
`CrackObjectCommon` death removes wall/collision. A carried fruit's Bomb attack therefore kills that wall, unlike
merely hitting a distant plant. Each row identifies the local transport already admitted by the old Strength branch.
`dc_bomb_flower = Progressive_Strength_Upgrade or (is_adult and 'Goron Bracelet')` changes only its lift capability,
not a flower's location/transport or the global count. Child source policy remains R14's.

### Every explosives/Strength rule (effective overrides included)

`Strength` below means the old `Progressive_Strength_Upgrade` clause; `DC flower` is its new local helper.
Distances are placement distances, not a new transport proof. Unmatched/N64-only checks remain unshuffled.

| Rule | Blocker / trigger | Flower(s), Hash; method | Disposition |
|---|---|---|---|
| Beginning -> Lobby | WallCrack17059737893961516233, room0 | 12361535549877235172 /12696080931756852015, 9.8/11.6m; carry | Strength -> DC flower; Hammer already accepted |
| Lobby Fairy | WallCrack5587238701582185492, room1 | 971877315955590573,18m; carry | DC flower; song/bottle retained |
| Lobby Gossip Stone | same wall | same carried flower | DC flower; `here` retained |
| Map Chest | WallCrack5641837233975145227 (-23.3,99.8,-38) | 18295893136718890181,11.7m; carry | DC flower |
| Room1 Blue-Rupee Chest | WallCrack14106977092420306644 (-22.8,99.8,-8) | 18295893136718890181,21.1m; carry | DC flower |
| Lobby -> Lower Right Side | WallCrack4200731794857161328 (29.25,98.7,-8), room1/2 opening | 971877315955590573,15m; carry | `has_explosives or Strength` -> `can_blast_or_smash or dc_bomb_flower` |
| Lobby -> Torch Room | room9 ledge -> free reverse side of room8 door | no explosive target | Existing adult ledge clause **not newly certified**; staged |
| Lobby -> Staircase Room | room8 candles -> room8/9 door -> room9 switch -> staircase shutter | lit candle14652077694215389560 (48.5,100,-51.5) | **Plain adult Bow played**; replace Fire-Arrows/sword guard with usable Bow |
| Lower Right Side -> Torch Room | room5 Lizalfos counter8075926014768809555 -> shutter9415944883117694992 | no flower in arena | Adult weapon/Bow added; child-only weapons age-guarded |
| Torch Room scrub | WallCrack14949303250999372259 (63,100.5,-83.5) | 10492269415332841231,11.1m; carry | DC flower |
| Compass Chest | WallCrack8412887615091849594 (-49,101.7,-14) | room10 1336635945291484747,~13m; carry | DC flower; nearer room11 flowers are on far side, not assumed reachable |
| Staircase -> Climb | manager10474712916684003797 -> Dm_DodongoCave_0010 -> stair swap | loose3319219522422689056 /1336635945291484747 carried to bed | Strength -> DC flower only; **Hammer startup held** |
| Climb Bomb Bag scrubs L/R | neither exists | none | N64-only; unchanged |
| Room10 Seed Chest | WallCrack13980282214128670992 (-49,115.8,-64) | nearest17.4m,12m below | No flower alternative added; blast/Hammer retained |
| Climb -> Before Upper Lizalfos | WallCrack4510904998256755578 (56.8,114.8,-7.8) | 2675786713662170296,8.5m, by block2195788520120900949; carry | DC flower |
| Upper Lizalfos -> Bomb Bag Ledge | pair1539353330400110799 /2541558834648863509, then eyes12790243399538496729 /13951311116548645685 | no arena flower | Played usable adult Bow kill; eye weapon still required |
| Room5 / Room16 reward chests | DodongoCavern_Gimmick_DefeatLizalfos01/02 | no arena flower | Adult Bow kill added, other weapons retained |
| Bomb Bag Ledge <-> Far Bridge | WallCrack13202633467597206724 (30.2,115,-23) | nearest19.2–22.1m and below ledge | No new flower route; blast/Hammer retained |
| End of Bridge Chest | WallCrack17959350160153264456 | nearest15.9m,13m below | No new flower route |
| GS Alcove Above Stairs | WallCrack1823997448213534774 | nearest28m,13m below | No new flower route |
| Far Bridge -> Mouth | eye sockets CrackWall_A_02 2004617935862037354 /13465518230305690104 | nearest17–24m,9.4m below | Explosives retained; no in-place Hammer/flower reach inferred |
| GS Back Room | CrackWall_A_01 5992355133787479731 | none | Blast/Hammer retained |
| Defeat King Dodongo | floor921376187402048479, then native bomb-targeting fight | room22 plants16232085853275649945 /14326755281814874501 /13131113113479567980 /3488340387747474622 | Fight Strength -> DC flower only; floor, slash and shortcuts unchanged; never Hammer as fight substitute |
| Death Mountain -> Beginning | adult files have no entrance boulder | scripted flower12145309744777105449 is **child-only** | Existing `Strength or is_adult` retained |

King's existing fruit alternative is the same `_A_01` with native `Bomb` actor tag; boss
`PerceptionSetTargetBomb` accepts ground, uncarried Bomb-tagged actors and ignores Bombchus. No flower from the
boss room is assumed to open the room21 floor above it (18.6m vertical separation). The existing floor predicate
therefore remains intact, as does r21's King Dodongo exception.

### Played corrections that explain the pre-bag model failure

Kareem clarified on 2026-11-24 (Longshot3.2.0,0.2.6, adult): **ordinary arrows through the lit candle lit the three
timed candles**. Native room8 placements are 7766157973751052842 (36.2,100,-59.7),
3412578102610136516 (40.8,100,-41.1),1677399996748274653 (49.5,100,-64.1); permanent lit candle
14652077694215389560 is the matching local source [placement identification from the dump, not a reported Hash].
All three Burning -> `DodongoCavern_Level_Room_08_Prefab_c4aa` -> EventRequest13693449133434520250
`DodongoCavern_Gimmick_CandleStickShutter` -> saved `DodongoCavern_CandleStick` -> lattice18414161731649864422 opens
into room9. Step switch3719343789467822676 (25,103,-23) -> EventRequest14837698052107380326
`DodongoCavern_Gimmick_SwitchShutter_Room01` -> saved `DodongoCavern_StepSwitch_01` -> shutter9691562485383977530
unbars its lobby-side lattice3133131671431381109. The candle door and staircase door are **not the same door**.

The rule now reads `at(Torch Room, (is_child and Sticks) or can_use(Dins_Fire) or can_use(Bow))`; it models that
route, not a free adult ledge bypass. Old source text incorrectly associated the candles directly with the stairs;
source corrected, old R20 guard removed because his plain-arrow play supersedes it.

Kareem also explicitly confirmed the upper Lizalfos arrow kill. Bombchus were used too, but may have followed the
bag; **arrows are the bagless evidence**. Native `Enemy_MiddleBoss_Lizalfos` Arrow1.0, Hookshot0; the death counter
opens the reward/exit. Same actor/table supports the lower pair. Add `can_use(Bow)` to both fights and reward
chests, preserve the timed eye passage's Bow/Slingshot requirement. Copied saves independently show canonical
`IsGet.Weapon_Sword_Master=false`, Master stock0, all other canonical swords false/0, Bow owned; no nonexistent
`Item_Sword_Master` key was substituted. Saves do not identify the killer or age by themselves; his report does.

### Round21's two Hammer-on-growing-flower candidates

1. **Lobby -> Lower Right Side:** r21's chain premise was wrong. The chain manager is room10's staircase puzzle,
   not the lobby. This exit breaks WallCrack4200731794857161328 by its ordinary death chain; widen to Hammer on
   the played WallCrack class, not on a speculative flower chain. Nothing left to test for that Hammer widening.
2. **Staircase -> Climb:** manager10474712916684003797 is linked to sixteen `_A_02` bed plants; requires four
   explosions within three frames, then event15736379894023753157 runs `Dm_DodongoCave_0010`, replacing stair
   7755736649088098775 with900149935771582689. Fruit damage plus the trigger after manager success is known;
   how one struck fruit starts the manager's chain is not closed by AINB. Front fruits371439288973712559 /
   13867111007212989923 are near bed floor height (bed y103.6, fruit103.7, nearby floor103.2) [reach inference].
   **No Hammer alternative admitted** before the staged check. Kareem's r21 flower explosion proves only ignition
   where it grows, not this chain or reach.

### Goron City: two played adult flower routes

Claude brought these in from the deferred list after Kareem's explicit play (Longshot3.2.0,0.2.6, adult,
strength-copy Bracelet, before bag). He carried flowers to open **GC -> Lost Woods** and to stop **Rolling Goron**.
Exact selected flower was not reported; candidate local sources below are from the actual adult placements.

| Event | Before | Added case | Native local flowers / target |
|---|---|---|---|
| GC Woods Warp Open | blast/smash, Din, Bow, Strength or child fire | `is_adult and 'Goron Bracelet'` | eastern `_A_03`9706505068154001370 (15.5,106.4,0.9),7238665186396676143 (14.2,106.6,-3.8); target Obj_Goron_BrokenRock_A_01 8668774813841012997 (16.1,104.9,-1.6) |
| Stop GC Rolling Goron as Adult | `is_adult and (Strength or explosives or Bow or Din trick)` | fixed `'Goron Bracelet'` inside adult gate | middle-ring `_A_03`7043415660827355832 (-18.8,105,-9.1),2438703331718758676 (-3.1,104.8,13.9),9316970488062789031 (-7.8,104.8,10.9), eastern pair above |

Both use the same spawned fruit/Low lift; the rock inherits the WallCrack damage/death contract. Goron stop's full
native reaction need not be invented: his **played stop** is the evidence. These are in `adult_goron_city.toml`;
gift delivery stays cs22c's ownership. Other adult flower rules and all non-Low rocks remain as listed above.

## Beamos: reflected Mirror Shield beam (played)

Kareem, Longshot3.2.0,0.2.6, adult **before bombs or Hammer**: used the Mirror Shield to redirect a Beamos beam
back onto the Beamos, killing it outright. **Active redirection, not a passive block.** No new play needed for this
class alternative; the other enemy/heat/weapon predicates remain.

Native corroboration (`beamos_trace.py`, `beamos-trace.json`, r14 decoded-cache hashes):
`Enemy_Beamos` and `_For_High_Place` life2; generic damage rates Hammer85358548=1, Bomb3237216321=1,
Beam4190899072=1. `BeamosBeam` attack power2, DamageType Beam. The generic table alone proves neither aim nor
reflection. Global `Enemy_Beamos.root` node4 `ExecuteBeamDevice`, node69 `QueryBeamosGetMirrorShieldInfo`
returns IsReflect/ShieldPos (used by nodes225/244 and look-position245). `BeamosBeam.root` node6 checks guarded
shield subtype5; Mirror's root nodes0/1/4 select, execute and calculate reflection. Mirror PostUpdate nodes0/7/12
update the reflected-light direction/control/chemical forward matrix. Its material `Weapon_Shield_Mirror`
IsIrradiate=true emits `LightReflect`, ElementType Light3346875365. Beam and reflected Light are distinct native
types; special engine collision/reflection handling was not fully disassembled. **The kill widening rests on the
played result**, not an assertion that the damage table alone closes that engine path.

| Consumer from r21 inventory | Effective change / status |
|---|---|
| Spirit Anubis Room -> Beyond Anubis (S1) | `can_blast_or_smash or can_use(Mirror_Shield)`; ground pair12328217772424437690 /15096857207894283138 |
| GTG Beamos Chest (G1) | `(can_blast_or_smash or can_use(Mirror_Shield)) and other fight`; actor2867582777575272608 |
| GTG Lobby -> Lava Room Front (G2) | same kill inside `here`, then retained Goron Tunic; same actor |
| `can_kill_beamos`, `can_kill_beamos_with_bomb_flower` | Mirror alternative added; soul/explosives/flower clauses unchanged. Neither helper currently has a world consumer. |
| Spirit Central -> Colossus Hands (S2), Big Mirror -> Before Boss (S3) | Target unidentified (possible cracked wall), **not a proved Beamos-kill rule**, unchanged |
| Early Adult Spirit -> Boulder Room (S4), child Spirit climb-wall clauses (S5) | Switch / wall, not Beamos kill; unchanged, no high-Beamos Hammer reach claimed |
| Ganon Spirit Trial Crystal Switch Chest (C1) | Switch, not Beamos kill; unchanged |
| Shadow First Beamos -> Huge Pit | WallCrack17091353075401231102, not a Beamos kill; **Mirror does not replace its explosives** |
| Colossus Grotto chest (D1) | Its rule reads no kill (`True`); unresolved appearance question retained, not silently widened |

This inventories all explicit helper reads and every r21 Beamos candidate, distinguishing the non-kill cases.
No global `has_explosives` or blast/smash change. `can_use(Mirror_Shield)` prevents child use; GTG still requires
its other fight weapon with Master Sword shuffle and its heat protection for the lava route.

## Zora's River downstream

`remake/child_zora_river.toml` adds `Zora River -> ZR Front`, `was = "True"`, matching upstream:
`can_blast_or_smash or 'Zora River Domain Arrival'`. Generated `zora_river.toml` stays untouched.

Evidence: `03-game-data.md` section 48; native `ZoraRiver_Common_08f0` nodes 1/3/4/10/11/12/13 create their walls iff
NOT (`Zorariver_BrokenRock_Broken` OR Water == Step03 OR Water > Step03). Both entrance rocks' deaths set that Bool.
The common geometry is not directional. Existing source event models the real river-to-Domain transition, not mere
Domain reachability or a former reward. Existing paired adult check showed Ready/false blocked, Step03/false open,
including reload. This change mirrors that condition and Kareem's downstream failure; no new gameplay patch.

Regression coverage extends `tests/test_story_steps_river.py`: start inside the river at each age, reject no tool,
Bag without strength and child Hammer; accept age-usable bomb kit, adult Hammer, or saved Domain-arrival event.
Existing upstream, Lost Woods and reverse Domain tests retained. Focused command:
`CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2 tests/test_story_steps_river.py`:
**24 passed in 5.96 s**. No game running at stage start.

## Ice Cavern: explicit gift dungeon credit (built, not played)

Claude superseded the initial main-runtime-only check at 15:26: the native trace predicts no credit, so build the
fix and stage candidate versus main instead. The **chest-only hold stays in the merge head**. Only a later, separate
commit after Kareem's pass may admit Map/Compass at this lesson; keys/boss keys remain held.

### Native chain and implementation

- Iron Boots chest **6859289214373847284**, `SageOfWater_MelodyGet_Water`, runs `SageOfWater:IceCavern_WaterSerenade`:
  chest item at Event60, then Event281/283 starts `Dm_MelodyGet_Water`. That lesson's Event29 calls
  `GetPouchContent:GetPouchContentByActorName`. The later source/Water-quest writes remain at this chest.
- The generic pouch body sets the get window, adds the actor, and autosaves; it never calls
  `GameSystemActor.EventGetDungeonCompass`. `Item_Dungeon_Compass` is `NotPushToPouch`. Native big-chest Event26
  (index22), `EventGetDungeonCompass`, calls **0x028caff0 -> 0x03283060** and writes the current dungeon's compass
  flag. Source: `r11-keys.md:29`, `r13-dungeon-items.md:17-31`, `r18-dungeon-items.md:96-105`; independent facts-only
  lead sloperinaGZ `docs/FINDINGS.md` sections1/5.8 (local `work/refs/sloperina-FINDINGS.md`).
- Target credit is **`DungeonInfo.IceCavern.IsGetCompass`**, save key **0xea1846e6**; generic acquisition history
  **`IsGet.Item_Dungeon_Compass`**, **0x14fcc563**, is different. A natural native-chest compass save has the former
  true and the latter false. The adult pause map also needs `HavePlayedEvent.Dm_TimeTemple_0065`, true in this fixture.
- `patch/gifts.py` derives same-dungeon Map/Compass targets in `seed_setup`, using the existing
  `key_targets.DungeonGrant.field` contract also used by chest grants. After the actual gift step returns, the existing
  `_set_flag_after` machinery writes that existing dungeon Bool, then resumes the unchanged native continuation.
  No ordinary key, boss key, off-dungeon gift, extra item grant, new saved field or new event dependency is added.
  No `plan.py` edit was needed; shared-file notices preceded `gifts.py` changes.
- Native read-back tests cover both Map and Compass and the retained admission hold. Existing production
  `test_event_registration.py` recipes already cover the `gifts` writer; the new path adds only a GameDataActor
  action, not a subflow/transition. Its held assignment is exercised by the production `seed_setup` step directly
  and the staged external-placement packet, not disguised as a normally generated fill.

### Paired packet READY for Claude's boot check

Private diagnostic seed **22040003**, Chest + Gift, songs anywhere. Explicit assignments are a diagnostic external
placement, not a certified solo fill: every other reward is a five-rupee filler; the Iron Boots chest itself gives
only that filler, and **Sheik gives the compass**. The research-only admission bypass is exactly that source/item.
The permanent fill hold remains unchanged. These private diagnostic assignments reveal nothing about Kareem's seeds.

| Arm | Launcher under `E:/OOTRemake/work/r22-logic/` | Source | Expected |
|---|---|---|---|
| Candidate | `r22-ice-candidate-next.bat` | this track, explicit post-grant dungeon write | compass on Ice pause map; native dungeon flag true |
| Control | `r22-ice-control-next.bat` | main `2091387` archive | same compass text/history, no dungeon credit (predicted, not played) |

Both use **Longshot 3.2.0**, pinned stable executable, exactly one mod, `HOS_FS_OVERLAY` unset. Mod folders are
`ingame/mods/<launcher-name-without-.bat>/<same-name>/`. The dry-run copied only this fixture into each private
`ingame/user-<name>/save/<UID>/`; original source hash stayed unchanged. No game or boot was started by cs22d.

Source: natural `save-backups/2026-11-10_1402-main-fire-hammer/save/<UID>/slot_04`, hash
`f4a9198059dd571cd07b6f4eed6f230a19e01b4e24af42f1bc1c748ed475847c`. Thumbnail viewed:
`work/r22-logic/thumbs/2026-11-10_1402-main-fire-hammer__slot_04.jpg` (adult Link with Hammer, Fire Temple statue).
Adult naturally; Time Ocarina equipped, empty bottle B, no Zora Tunic or Iron Boots; Ice chests, lesson, generic
compass history and dungeon compass flag all clear. No save edit. Prefer this over the shorter test-lineage Ice save.

**Checklist, each arm separately (20–30 minutes per arm estimated, not timed; two launchers split the 40–60-minute
pair at the natural quit/restart boundary):**

1. After Claude boot-checks, launch candidate, Continue the Hammer/statue thumbnail. Only Debug Teleport/clock allowed;
   **never Debug age change**. Teleport to Zora's Domain/Fountain outside the dungeon, then **walk in through Ice
   Cavern's entrance**. Do not teleport into the dungeon.
2. Play the Ice route: gather the first silver-rupee set, use the empty bottle for Blue Fire, melt the route, solve the
   push-block/silver-rupee room, defeat the White Wolfos, and reach the Iron Boots chest. Keep the native Map chest
   **11498802739257120175** and Compass chest **13542013937093159888** closed; neither is the tested source.
   The native chest contents are harmless filler in this packet; do not substitute either for Sheik's lesson.
3. Open the Iron Boots chest (its reward is five rupees), complete Sheik's lesson using the equipped Ocarina, and
   record the compass get text. After control returns, open the pause map. **Candidate pass:** the Ice compass
   indicator is present. The map itself was not granted, so unexplored layout is not the acceptance criterion.
4. Walk out to Fountain and back in through the entrance, then re-open the pause map. Save, quit, Continue and check
   the indicator again. Lesson must not repeat; chest remains open. If any arm takes longer than 30 minutes, stop at
   a safe save point in its private copy and resume that same launcher later; never use the other arm's save.
5. Claude/cs22d reads only the private packet save: **`DungeonInfo.IceCavern.IsGetCompass=true`** after the lesson and
   reload, versus false initially. Also record `IsGet.Item_Dungeon_Compass`; its text/history alone is **not** a pass.
   `inspect_packet_save.py` is the read-only reader. Control should keep the dungeon flag false despite generic
   history true; a different result is evidence to report, not to hide.
6. Quit, launch control, repeat 1–5 on its independent original save. Do not use a candidate save as the control.
   Loading proof in each `ingame/user-<name>/longshot_log.txt`:
   `mods: Event/EventFlow/Dm_MelodyGet_Water.bfevfl.zs <- ...<arm>...`. Record any crash, stuck scene or repeat.

Verification observed: both template launchers passed `CLAWSHOT_DRY_RUN=1 cmd.exe /d /c <launcher>`; no
`hookshot.exe` target. `prove_ice_packet.py` read back both mods: same settings, save hash and placement digest;
**only** `Dm_MelodyGet_Water.bfevfl.zs` and the resource-size table differ. Candidate Event29 -> existing GameData
set-true action -> the control's exact native continuation; control has no dungeon-credit write. Each arm has
156 runtime files. Receipts: `r22-ice-*-next-manifest.json`, `ice-readback-proof.json`. No new resource/pack-list entry.

Fact-only source/save survey: `work/r22-logic/save-findings.md`, `scan_saves.py`, `saves-scan.jsonl` (2963 slots,
777 distinct saves); no GPL implementation or decoded data in the repo.

## Unresolved DC physics packets (built, not played)

All use **Longshot 3.2.0**, current Longshot template, pinned stable executable, one mod only, overlay unset.
Each pair is this track versus main `2091387`, identical explicit assignments. These checks measure the game's own
physics: neither arm patches flowers, candles, switches, collision or Hammer damage. Both arms should therefore
behave alike; the old logic is not an in-game gate. The paired controls remain available.

### Saves and packet boundaries

The save survey found **no natural adult pre-bag save** in `save-backups`: natural adult main-game saves already
finished DC as child. Best unedited alternative is test-lineage
`2026-11-19_133536-r18-door-v2-15/<UID>/slot_05`, SHA256
`60cc357a68fbae9b29813d8b81df56f21b42f97138e419f7edc9003f208611f0`. It came from the natural child
`2026-11-07_1630/slot_01`; Kareem played the owned-Stones Door packet and **pulled the sword naturally**, with no
age/inventory/flag cheats (`r18-rewards.md:594-601`). It is adult (`Sequence_IsChildhood=false`), Bracelet1,
Master Sword1, Slingshot1, no Bow/fire items/Hammer/bag tier/bombs/Bombchus. Time Ocarina equipped.
Its kit stones/Fire Medallion and two already-open lobby chests are disclosed test history, not vanilla progression.
The entrance wall and two western alcoves are already broken, so these packets cannot retest them. Candles,
staircase and Bomb Bag chest remain unused. Thumbnail viewed:
`work/r22-logic/thumbs/2026-11-19_133536-r18-door-v2-15__slot_05.jpg`, Link on the Temple of Time pedestal dais.

Hammer fixture requires **one documented item grant**, identical in both arms, because no naturally Hammer-owned
save has the staircase unsolved. `stage_hammer_save.py` creates `work/r22-logic/fixture-hammer/` from that source:
only `IsGet.Item_Hammer` (Bool0x7227efd8) and `PouchData.Item_Hammer.StockNum` (Int0x1aafdb66) change 0->1.
Age, story, chest Bools, all Bool64 actor flags and every other entry are unchanged; original hash verified intact.
Fixture hash `a8fc96aa2fb086de42a6d7a2303d171faa32fa9abc1feba6d856bc5acc4b1e89`, proof `hammer-save-proof.json`.
No debug inventory or age change is prescribed. Hammer packets enable already-played free time travel so a normal
child return/sword pull can prepare the candle door if the adult ledge is impassable; both arms get the same option.

| Check | Launchers under `work/r22-logic/` (candidate/control) | Private seed | Save / estimated play |
|---|---|---|---|
| Ledge + optional Hookshot arch | `r22-ledge-{candidate,control}-next.bat` | 22040004 | natural main-fire-hammer slot04, no edits; ~5–8min/arm |
| Adult flower blast -> timed candle | `r22-dc-{candidate,control}-next.bat` | 22040001 | naturally-aged Door-v2 adult pre-bag, no edits; ~10–15min/arm |
| Hammer on growing staircase fruit | `r22-hammer-{candidate,control}-next.bat` | 22040002 | same pre-bag source + single Hammer grant; ~10min/arm if ledge works, 20–30min/arm with native child prep |

Long checks are separate launchers at the arm boundary; do not combine saves. Time is estimated, not measured.
If an arm exceeds 30 minutes, save its private copy at a safe point and resume that same launcher later.
Claude boot-checks first. No game or boot was started by cs22d.

### Ledge checklist — Longshot 3.2.0

1. Launch candidate, Continue the natural adult Hammer/statue thumbnail. Teleport only to the mountain outside
   DC, then walk through the entrance. No Debug age change, inventory or flag edits.
2. On the lobby's east side, south of the Gossip Stone alcove, find the archway to the elevated floor-switch
   passage. Try to jump/grab/climb onto that ledge **without items**. Report standing on the switch, or inability
   to climb it; do not infer success from the staircase door, which this main-game save already opened.
3. If bare climbing fails, try the owned Hookshot on the archway and report whether it actually carries Link up.
   Native ledge top is y103 versus floor100; adult parameter limit2.81m, collision not decoded. Neither result is
   assumed by this packet. The test decides the existing adult ledge clause and a possible Hookshot alternative.
4. Quit. Repeat with control's independent original copy. Expected same physics. Save/reload optional for a pure
   climb observation; the source switch is already set, so its persistence is **not** this check.

### Flower/candle checklist — Longshot 3.2.0

1. Launch candidate, Continue Temple pedestal thumbnail. This is adult from a real pull; no Debug age change.
   Teleport to the mountain outside DC and walk in. **No Bomb Bag, bombs, Bombchus, Bow, fire spell or Hammer.**
2. From the lobby, carry a local flower to the eastern lower-right cracked wall, then follow that route, defeat
   the lower Lizalfos with the already-owned Master Sword, and reach room8's three timed candles. Do not rely on
   the unplayed lobby ledge. Stay adult and do not light them as child.
3. Use the flower near the far candle: plant8988246658738172741 (49.9,100,-70.1), candle1677399996748274653
   (49.5,100,-64.1), about6m apart. Carry its fruit, set it down next to that **unlit** candle, and stand clear.
   Record whether the blast lights the candle. A flower exploding without the candle burning is a failure of this
   proposed ignition method, not a pass. Do not keep repeating unchanged failures.
4. If it lights, test whether all three can be lit within their 15-second window using carried flowers only.
   Record separately: one candle ignites; all three lit; room8->9 door opens; stepping on room9's floor switch
   opens the staircase door. Do not substitute arrows (that method already passed in Kareem's seed).
5. If the door opens, Save/Continue and re-enter through DC's entrance; record `DodongoCavern_CandleStick` and
   `DodongoCavern_StepSwitch_01` from the private save. Quit; repeat on control's independent original copy.
   Expected same native result. This check does not certify using a flower on a distant ledge or skull-eye socket.

### Hammer staircase checklist — Longshot 3.2.0

1. Launch candidate, Continue Temple pedestal thumbnail. Adult pre-bag plus the documented Hammer grant; no
   other inventory/story edit. If the ledge check passed bare climbing, use that normal route to the room9
   switch, then enter the staircase room. **Do not start the flower bed by throwing anything at it.**
2. If the adult cannot reach that switch without a fire method, prepare it through normal age travel:
   return the sword at the pedestal to become child (free time travel is enabled in both arms), obtain native
   Deku Sticks from the Kokiri shop or a Deku Baba using the already-owned Kokiri Sword, enter DC, clear the
   lower route with the Slingshot/sword, light the candles with a lit Stick, and stand on the room9 switch.
   Leave the staircase bed untouched. Leave the dungeon, return to the Temple and **pull the sword naturally**
   to become adult; return through DC's entrance. Never use Longshot's Debug age change.
3. Verify that the staircase is still raised. At the front of the sixteen-flower bed, hit a growing bulb once
   with the Hammer (front plants371439288973712559 /13867111007212989923, fruit just above the floor).
   Do not pick up/throw a flower or use bombs. Record three distinct results: bulb explodes; row/bed chains;
   staircase lowers and can be climbed. **Pass requires the last, not merely the explosion.**
4. Save, leave/re-enter through the entrance and Continue; record the stair remaining down and
   `HavePlayedEvent.Dm_DodongoCave_0010=true` in the private save. If ignition fails, stop/report the exact
   fruit/position and which of the three steps failed, not repeated swings.
5. Quit and repeat with control's independent identical Hammer fixture. Both should behave alike: no native
   Hammer/flower code differs. The current logic **does not** count Hammer for this staircase until this pass.

All DC loading logs: each `ingame/user-r22-<check>-<arm>-next/longshot_log.txt` must show
`mods: Banc/DodongoCavern/DodongoCavern_{Static,Dynamic}.bcett.byml.zs <- ...<arm>...`.
`prove_dc_packets.py` passed: each pair has identical settings, explicit assignments, source-save hash and every
runtime-file digest. File counts per arm: flower/candle116, Hammer117, ledge116; **5228 non-chest actor instances
per pair** plus all AiGroups match the native dump. Source save hashes remain intact. Six launcher dry runs passed:
pinned stable3.2.0 executable, separate private user folders, exactly one mod each, overlay unset. No game started.
Each manifest lists both DC Banc files for the loading proof. **READY for Claude's boot check**, then Kareem's play;
the unresolved physics alternatives remain held regardless of generator/gate results.

## Focused verification and decisions

- ZR regression:24 passed.
- Initial combined synthetic focus:210 passed,2 skipped,1 old sword-off comparison failure. Printed payload showed
  Mirror Shield accepted by the new Beamos rule but not the comparison's r21 kill contract; updated that contract.
- Native-enabled focus:216 passed,3 failed. Both Map/Compass native credit cases passed. Two new DC cases supplied
  fixed `Bow` in a copies-only seed world: printed adult inventory had no Bow count, while `Progressive Quiver`
  aliases Bow1. Fixtures now supply that raw copy, not change product logic. A child Bow-only matrix case could
  not reach the torch room at all; supply child Bracelet/Slingshot to isolate the intended candle refusal.
- Cause-directed DC/ranged/Hammer/Master-Sword rerun: **104 passed in24.25s**. No game running.
- Targeted ruff format/check passed before the last fixture-layout change; subsequent post-rebase/gate results below.
- No new setting, version bump, saved field or game-resource filename. The explicit Ice gift credit is a runtime
  repair; its admission loosening remains a separate final commit after the paired play. All other loosenings cite
  native trigger/Low-lift chains or Kareem's attributed play; the staircase Hammer and ledge/flower ignition stay held.

## Exact-head gate preparation

Rebased onto current main `5bc5577` (deterministic scrub-shield event-registration coverage; no seed re-pin).
Focused native-enabled run after rebase: **223 passed in396.23s**, `-n2`, `CLAWSHOT_WORKERS=1`, all three dump
environment paths from the round brief. Files: `test_story_steps_river`, the three `test_r22_*` logic suites,
`test_gift_dungeon_items`, `test_master_sword_logic`, `test_ranged_pickups`, `test_world_remake_hammer`,
`test_gifts`, `test_gifts_dump`, **`test_event_registration`**. Log: `work/r22-logic/rebased-focus.log`.
The Hammer fixture's starting flags were also printed: adult; candle, room9 switch and staircase event all false.

Queued sweep plan, not results: paired current-main/head,200 Broad +50 Defaults +50 Recommended per arm, plus50
`BroadAdultFlowers` per arm. The added cohort opens forest/door, shuffles the Master Sword, enables free travel,
and starts with Time Ocarina/Lullaby/Saria's Song/Bow. Compare opaque placement/sphere digests and bagless adult
Bracelet+Bow DC chest-access counts; no placement lists published. Generator exhaustions must be zero.
This plan completed on2026-11-25 under the assigned lock; exact results and the test-only correction follow.

## Urgent GC grotto and sign puzzle correction (Claude/Kareem, 2026-11-24)

This supersedes FROZEN `446e2f5`; both corrections ship together. No rebase onto later main: Claude will merge the
gated head with `--no-ff`. Audit-only slot3b is separate from this track's full gate at6.

### Played facts and copied save inventory

- Kareem2026-11-24: **no Time Block anywhere in Goron City**. He does not remember whether he had the Hookshot
  on the grotto visit; Hover Boots was a question, not a played route. No Hookshot/Longshot/Hover route is claimed
  as verified from that recollection.
- `plans/playtest/answers.md`, XC07/XC08 GC sign puzzle,2026-11-09: wrong order creates the left green chest and
  locks attempts until leaving/re-entering Goron City; correct order creates the right purple chest. This proves
  the puzzle was visited, not its entry method.
- Copied30 natural main slots **before parsing**, then read only the copies; every source SHA256 is unchanged.
  No seed, spoiler, `save-work` or live game profile was read. Proofs:
  `work/r22-logic/{nov09,nov10}-main-save-copies/inventory-proof.json`.

| Backup | Slots | Era | Hookshot | Longshot | Hover Boots | Green opened | Purple opened |
|---|---:|---|---:|---:|---:|---|---|
| Nov09_0954 main-after-jabu | 6 | child | 0 | 0 | 0 | false | false |
| Nov09_1022 main-adult-first | 6 | 2 adult /4 child | 0 | 0 | 0 | false | false |
| Nov09_1347 main-after-forest | 6 | adult | 1 | 0 | 0 | false | false |
| Nov10_1254 main-fire-temple | 6 | adult | 1 | 0 | 0 | true | false |
| Nov10_1402 main-fire-hammer | 6 | adult | 1 | 0 | 0 | true | false |

Fields: `PouchData.Item_Hookshot.StockNum`, `PouchData.Item_Longshot.StockNum`,
`PouchData.Armor_Adult_HoverBoot.StockNum`, `Sequence_IsChildhood`;
chests `IsTreasureBoxOpen.9159710900681116662` and `.10944569637726152230`.
The opened green chest in the successor saves corroborates an actual grotto visit. Under normal permanent-item
ownership it excludes Longshot/Hover Boots as necessary for that historical approach; it **does not prove the
Hookshot was used**, nor supply a staged Longshot3.2.0 route proof. Both Nov10 batches also own Goron Tunic1.

### Current native trace

Direct current-romfs read: all four `Banc/GoronCity/GoronCity_{Adult,Child}_{Static,Dynamic}.bcett.byml.zs`,
2609 actor instances total, **zero** `TimeBlock`/`SongOfTime` placements. Current proof:
`work/r22-logic/gc-native-placement-facts.json`. The GC logic/event cache has no Time Block reference; the global
Time Block ocarina flow requires contact with an existing block, not creation of a GC block. This corroborates
Kareem's absence report, not a claim to have exhaustively decoded every ActorHolder.

Real targets: A_01 hashes13785392151857853269 at(-40.615,114.735,32.550),
7261889099542506008 at(-29.839,111.245,30.990),11469250601875506713 at(-16.495,112.235,28.800);
entry trigger10542229093882165730 at(-40,114,28). All are in the GC native files, not inferred N64 blocks.
Current `dm_pack.py <actor> .bgyml` decoding of both target and both weapon packs succeeded:

| Native parameter | Value |
|---|---|
| `Obj_HookShotTarget_A_01` physical entity `EnableSubLayerHitMask` | `HitOnlyHookshot` |
| Its physical box `MaterialPresets` | `Wall_StickHookshot` (with Metal/camera filter) |
| `Component/HookshotParam/Weapon_Range_Hookshot.game__component__HookshotParam.bgyml:Range` | 10m |
| Corresponding Longshot override `Range` | 20m |

Target-center gaps are11.43/13.56m, **not** a proof of Longshot-only access: standing/shot-origin offsets,
approach terrain and landing clearance remain unverified. Hookable surfaces prove target class, not the complete
path to the entry trigger. No Hover Boots alternative is admitted. Full native component output stays outside
the repo: `work/r22-logic/gc-grapple-native.txt`; the earlier cache's Effect-v5 errors were not a limit on these
current bgyml decodes.

### Decision and scope

**cs22d, under Claude's explicit fallback instruction:** no end-to-end approach is proved, so native
`Goron City -> GC Grotto Platform = False`, the strictest rule tolerated by the focused native production recipes.
Both inherited Time Block clauses disappear from native logic: inbound and the outbound Song-of-Time+Longshot
term. Other outbound damage/defense terms stay. Ported N64 reference text remains unchanged; guarded remake
overrides follow the existing convention.

All six modelled grotto locations are out of reach from the overworld. The three inherited scrub checks and
beehive have no native actors/census targets; they gain no destinations. The green failure chest remains
`keep_vanilla`, out of logic and unshuffled. The native purple solution chest remains a shuffled destination,
but its unproved region cannot supply progression; non-progression filler is allowed. Reopen only after an
access method is established, not on an item-ownership guess.

Separately, Kareem2026-11-24 played **swords, bombs and Hookshot** completing the sign puzzle. Replace the
solution chest's `True`/“needs no item” with
`can_use(Kokiri_Sword) or adult_sword or (is_adult and Giants_Knife) or Bombs or can_use(Hookshot)`.
This includes usable Master/Biggoron/Kokiri swords and Giant's Knife for a strike, ordinary usable bombs,
Hookshot/Longshot; excludes Hammer, Bombchus, Bow, Slingshot, Boomerang and magic until played. The chest attack
rule is tested from inside the grotto independently of the entry exclusion.

### Verification and hotfix measurement

Initial focus:32 passed/3 failed. Printed causes: two fixtures enabled the remake's unverified/locked
`logic_goron_grotto` trick; a “Bombchus-only” fixture also supplied a usable bomb bag+strength, so ordinary bombs
correctly satisfied the new rule. Removed impossible trick settings and isolated Bombchus without usable bombs.
After the conservative entry decision, cause-directed native-enabled focus:
**47 passed in235.44s**, `-n2`, `CLAWSHOT_WORKERS=1`, including `test_event_registration.py`; targeted format/lint
passed. No coverage seed re-pin. These production recipes tolerate the region exclusion; full gate/sweep pending.

Audit helper `work/r22-logic/grotto_audit.py` changes **only original main's inbound SoT alternative**, keeping its
old Hookshot/hazard branch, return rule, sign `True`, settings and placements. This is deliberately narrower than
the conservative candidate: it measures the released-model SoT risk without confounding the other tightenings.
Two constructed placement oracles (no generation) pass: a required Hookshot inside the grotto becomes a genuine
self-lock; an outside Hookshot preserves the goal and is not misclassified. Oracle setup first printed
`Rule.fn` init=False and `World.age_return` property constructor errors; corrected fixture construction uses
`Rule.test` and settings. Real audit worlds retain every actual return guarantee.

Claude assigned audit-only slot3b after cs22b's explicit release. Regenerate exactly the shared main5bc standard300,
cross-check every placement/sphere digest and effective setting against its immutable cache, then count by recipe:
required grotto items lost under the isolated tightening; goal failures/joint dependencies; Hookshot-family
placements or its only logical route inside the grotto; mere delays separately. Errors/incomplete rows are never
zero-risk results. Publish counts only and release immediately. This is model-based hotfix evidence, **not**
an assertion that a particular seed was proved unwinnable in game. Full gate remains line6 after cs22g.

### Audit3b result — main5bc, standard300

Ran only after cs21i's explicit22:48 `LOCK RELEASED`, Claude's authorization and stage-start player0.
Owned audit lock22:50–23:02; released immediately after measurement. **300/300 complete**, no errors/exhaustions;
every placement/sphere digest and effective settings match the immutable shared baseline. No baseline goal or
sphere-replay mismatches. Generation/audit646.609s (command wall683.24s). Frozen product head84582cc is unchanged.

| Recipe | Seeds | Required item lost with SoT removed / goal fails | Additional early-return refusal | Hookshot-family item in grotto | That item lost | Hookshot or its only logical route through grotto |
|---|---:|---:|---:|---:|---:|---:|
| Broad | 200 | 13 | 0 | 1 | 1 | 13 |
| Defaults | 50 | 0 | 1 | 1 | 0 | 0 |
| Recommended | 50 | 2 | 1 | 9 | 2 | 2 |
| Total | 300 | 15 | 2 | 11 | 3 | 15 |

“Required” is a leave-one-out goal proof, not merely `Item.progression`. Each of the15 goal-breaking seeds
loses a required grotto item under the isolated no-SoT rule; zero joint-only goal failures. A Hookshot-family
placement inside is **not automatically a lock**: another copy/path can open the retained Hookshot branch.
Required-but-still-obtainable items were merely delayed in17 Broad,27 Defaults and12 Recommended location cases.
These delay counts are item/location cases, not additional broken seeds.

The additional Defaults/Recommended case each still satisfies the bare goal but `check_beatable` rejects at
`fill.py:1282`. Its `Search.won()` additionally requires `return_safe`: these are earliest-pull return-guarantee
failures, not a `softlock` observer exception or an audit error. The redacted payload says6 placed items never
reachable; no placement names were published. Thus the proper acceptance oracle rejects17/300 counterfactual
seeds, of which15 lose the goal itself. This quantifies a released-model risk; the real game's unproved approach
could differ, so it does not label17 actual played seeds unwinnable.

Immutable evidence: `work/r22-logic/grotto-audit-main-5bc5577/{rows.jsonl,results.json}` and the sibling `.log`.
Source revision5bc5577369d429d426dc2059461918e41b5c5302, standard lists22220000..22220199 Broad and
22220000..22220049 each Defaults/Recommended. Audit changed no product files, output mod, source baseline or
player data. **Hotfix release decision remains Claude/Kareem's**;15 goal-critical dependencies are sufficient
reason not to dismiss the inherited Time Block assumption as harmless.

Lock-acquisition safety: full runner now calls an explicit `if ! mkdir; then exit73; fi` helper before owner write.
Actual helper passed held/free temporary-directory cases; the held sentinel owner was unchanged. No real lock
was tested outside an authorized turn. Audit acquisition itself used exclusive Python `Path.mkdir`.
This is a round-receipt edit only; keep frozen84582cc for the later sweep/full gate, no rebase/refreeze.

### Line6 full gate — frozen product84582cc (2026-11-25, cs22d)

Started00:38 after cs22g's00:37 explicit release and Claude's go. Exclusive fail-closed acquisition; player0
before acquisition, each sweep, synthetic and dump. No rebase/refreeze or product-source edit.

| Recipe | Seeds/arm | Main first-try failures | Head first-try failures | Exhausted main/head | Changed placement/sphere digests |
|---|---:|---:|---:|---:|---:|
| Broad | 200 | 0 | 0 | 0/0 | 200/200 |
| Defaults | 50 | 1 | 0 | 0/0 | 50/50 |
| Recommended | 50 | 2 | 2 | 0/0 | 50/50 |
| BroadAdultFlowers | 50 | 0 | 0 | 0/0 | 50/50 |

**350 accepted/arm, zero exhausted**. Reused immutable standard300 main; executed only extra50 main
(117.984s) and350 candidate (665.156s), six workers. Standard seed/settings/serialization equality checks
passed. Every adult Bracelet+Bow/no-Bag probe changes reachable DC chests0→7 (all50 extra-cohort cases).
Placement/sphere churn is for the combined branch, not attribution solely to the grotto change; audit3b is
the separate isolated no-SoT counterfactual.

Full format/lint passed (567 formatted files). Synthetic at `-n 8`, `CLAWSHOT_WORKERS=4`: **4454 passed,
841 skipped, one failure** in506.09s. Printed failure was exactly the held GC grotto Purple#2 chest, not a
generator failure: the older vanilla-all-chests contract still expected it reachable despite the intentional
unproved-entry hold. cs22d updated only that test's explicit expected missing chest and its explanation.
The goal, boss-room, all other chest reachability and exact keep-vanilla exclusions remain enforced.
This is a test-contract correction, no product delta or broadened blanket exemption.

The changed test initially required Ruff's printed assertion layout; applied that exact formatting via patch.
Changed-file format/lint then passed; isolated affected test **1 passed in2.38s**, player0, one worker.
No passed synthetic case or sweep was repeated. Dump started01:04 after fresh player0,
`-n 8`, `CLAWSHOT_WORKERS=3`, with the existing read-only r19 sword-layered dump and configured romfs/NUP.
Dump **838 passed**,24 existing parametrization warnings,3483.27s (58m03s); command wall3489.40s.
Verified exact owner and removed only our lock, then posted **LOCK RELEASED at02:02**. No product changes,
unchanged reruns, game launches or writes into player/dump folders. Receipts are under
`work/r22-logic/gate-84582ccd329379d4b35611d0a3b75898a973ca8a/`.

## READY — merge-backed versus play-held boundary (cs22d, 2026-11-25)

**Gate complete on product84582cc, baseline5bc5577.** Paired350/arm zero exhausted; full format/lint passed;
synthetic4454 passed/841 skipped plus the sole corrected contract passed in isolation; dump838 passed.
The final child changes only `tests/test_world_data.py` and this receipt, not product behavior/settings.
The historical failed synthetic run is retained, not relabeled a green full rerun. Lock released02:02.

### Merge-head loosenings: attributed play and exact scope

Reports below are **Kareem via Claude**, not new checks run by cs22d. New2026-11-24 reports were on
**Longshot3.2.0, Clawshot0.2.6**; their method/runtime/context is recorded in this round's sections above.
Do not treat unplayed class members as separately played targets.
The played-save audit corroborates Bracelet/Low, **not native Darunia-source provenance**. The added fixed-source
adult case rests on the identical native actor's age-independent Low pickup check plus that played capability;
it is not relabeled a separate played native-gift acquisition.

1. **Adult Low/Bracelet Bomb Flower use in DC.** Report2026-11-24: adult carried the cavern's flowers before
   finding the Bomb Bag, with Goron's Bracelet and no adult gauntlets. `dc_bomb_flower` adds the fixed native
   Bracelet adult case, backed by the age-independent Low pickup and identified native carry/blocker chains.
   Exact changed consumers: Beginning→Lobby; Lobby Fairy; Lobby Gossip Stone; Map Chest; Room1 Blue-Rupee Chest;
   Lobby→Lower Right Side; Torch Room scrub; Compass Chest; Staircase→Climb; Climb→Before Upper Lizalfos;
   King Dodongo's existing flower fight alternative. It does **not** add flowers to a remote floor, socket or ledge.
   The report is a pre-bag progression report, not a claim he separately certified every listed check; the per-target
   native chains are in the DC audit table. Global R14 strength/copy policy and child policy are unchanged.
2. **Two adult GC flower uses.** Report2026-11-24: before the bag, adult carried flowers with the Bracelet to
   open the **Lost Woods shortcut** and **stop Rolling Goron**. Added fixed-Bracelet case only to
   `GC Woods Warp Open` and `Stop GC Rolling Goron as Adult`; local adult flower placements corroborate transport.
   This is not a general GC/Medigoron flower widening, and gift delivery is not changed here.
3. **Plain Bow through DC's lit candle.** Report2026-11-24: ordinary arrows through the already-lit candle
   lit the three timed candles. `Lobby→Staircase Room` now accepts usable Bow via `at(Torch Room, ...)`, retaining
   child Sticks and Din alternatives. Native candle→room8/9 door→room9 switch→staircase shutter chain is identified.
   This does not certify the separate bare-climb ledge or a flower blast lighting candles.
4. **Adult Bow/Lizalfos capability.** Report2026-11-24: explicitly killed the **upper Lizalfos with arrows**;
   the later Bombchu use is not used as bagless evidence. Adds usable adult weapons/Bow to
   Lower Right Side→Torch Room, Upper Lizalfos→Bomb Bag Ledge, and Room5/Room16 reward chests.
   **Update2026-11-25, Kareem via Claude: he also killed the lower Lizalfos pair with the Bow. Lower-pair Bow
   is now played evidence, not merely the original same-actor damage/death-counter extrapolation.**
   Adult weapon class has Kareem's2026-11-22 Hammer-as-weapon report (`r21-hammer.md:15-18,62`); eye timing/weapon
   gates remain. The canonical swordless inventory corroborates capability state, not the killer.
5. **Active Mirror Shield reflection kills Beamos.** Report2026-11-24: adult, before bombs/Hammer, redirected
   the beam **back onto its Beamos and killed it**; a passive block is not the claimed method.
   Added usable Mirror Shield to Spirit Anubis Room→Beyond Anubis, GTG Beamos Chest, GTG Lobby→Lava Room Front,
   and the two Beamos helpers (currently no consumers). GTG's other fight/heat gates remain. No wall, switch,
   unidentified target, or high-Beamos reach alternative is inferred; the native reflection collision is not
   claimed fully reverse-engineered. The kill is played; Kareem explicitly approved the named Spirit/GTG
   extrapolations on2026-11-25 (exact words below), not a claim of separate play at every target.
6. **Hammer at DC Lobby→Lower Right Side.** This is the ordinary identified WallCrack, **not** a growing-flower
   chain. Class play: Kareem2026-11-22 on0.2.5, Hammer broke bomb boulders and the DMT chest/Skulltula walls
   (`tracker-ui-notes.md`, recorded in `r21-hammer.md:15-18,49,66-70`). The new target inherits the same
   damage→death→collision-removal chain. Kareem explicitly approved this extrapolation on2026-11-25
   (exact words below); do not relabel his assumption as a separately played DC wall break.

### Held: do not merge an admission loosening from the staged packets

- **Ice lesson Map/Compass gift admission:** remains chest-only in normal fill. The merge head contains the
  explicit same-dungeon flag-credit writer repair, but that code is **not an in-game pass** and does not lift
  admission. Candidate/control `r22-ice-{candidate,control}-next.bat` must show the Ice compass pause indicator
  and `DungeonInfo.IceCavern.IsGetCompass` surviving exit/reload, with native loading-log proof. Any admission
  change is a separate commit only after Kareem's pass. Keys/boss keys remain held.
- **DC ledge / optional Hookshot arch:** `r22-ledge-{candidate,control}-next.bat`; bare jump/grab and arch transport
  remain unproved. The old adult ledge clause is unchanged, **not newly certified** by this merge or the sweep.
- **DC carried-flower blast ignites the timed candles:** `r22-dc-{candidate,control}-next.bat`; must show ignition,
  all three timed, then the door and room9 switch/shutter result. Plain-arrow play does not prove this.
- **Hammer starts the staircase flower-bed manager:** `r22-hammer-{candidate,control}-next.bat`; must chain and
  lower the stairs with persistence. Kareem's2026-11-23 Longshot3.0.0 hit exploding one growing flower proves only
  that first explosion. No Hammer startup alternative is in the merge head.
- Other remote-flower routes, upper floor/skull-eye substitutions, Medigoron candidates and unidentified Beamos
  targets remain unchanged/deferred. GC grotto approach is now **False**, not certified by Hookshot/Hover speculation.

The Ice pair and three DC pairs are built/dry-run/read-back verified, **not played or booted by cs22d**.
Claude already boot-checked all eight arms on Longshot3.2.0 after their15:30–16:10 builds:
`bootcheck-batch2/3`,16:33/16:44; each crash0, fatal0, save1, one mod. They are in the shared
`work/rounds/r22/PLAY.md`. Earlier “READY for Claude boot” wording is superseded; **no boot rerun needed**.
Candidates need play; controls are optional at Claude's call. Boot checks do not lift the held physics/admission rules.
Exact launcher/save/loading-log/checklist boundaries are in their sections above. Do not ask Kareem to repeat the
already-attributed played methods merely to merge those backed changes; only the held alternatives need new play.
ZR downstream mirroring, GC grotto closure and the GC sign attack rule are **tightenings**, not new loosenings.
Sign attacks accept only played swords/Bombs/Hookshot family; Hammer/Bombchus/other ranged remain unproved.

## Kareem's acceptance ruling — 2026-11-25, via Claude

Kareem **ACCEPTS the by-analogy cases** in the already-gated logic track:

- DC's **lower Lizalfos pair with the Bow is played**: Claude explicitly relayed that Kareem did kill this pair
  with the Bow. This supersedes the earlier lower-pair-only-by-analogy classification, including the corresponding
  lower fight/reward admission; the upper pair and plain-arrow candle reports remain as recorded.
- Exact wall words: **“Hammer I assume would have broken that wall yeah”**. Accepted for the identified
  DC Lobby→Lower Right Side wall. This is approval of the native/class inference, **not a fresh played wall break**.
- Exact reflection words: **“Mirror Shield can extrapolate, yeah”**. Accepted for Spirit Anubis Room→Beyond Anubis,
  GTG Beamos Chest and GTG Lobby→Lava Room Front, retaining their other fight/heat gates.

The conditional literal-only draft was discarded using scoped edits; all ten affected files returned to gated
bfbb00e35d and its external conditional patch was deleted. Nothing from that draft was committed. This receipt
changes documentation only; product remains gated84582cc, with bfbb00e35d's prior test/receipt-only child.
Ice lesson admission, ledge/arch transport, carried-flower candle ignition and Hammer staircase startup remain
play-held; this acceptance does not silently admit those distinct alternatives.

Claude's ordering remains: **logic merges as gated only after0.2.8 is published** (the broader round becomes0.2.9).
No logic merge, rebase, refreeze, runtime launch or candidate edit was performed by cs22d.

## 0.2.8 hotfix release-candidate gate — PASS

Separate detached candidate `1d3f1ff6da6feaf73978799d497d037b5aaac017`,
`E:/OOTRemake/work/r28-release/cand`: v0.2.7 plus the no-ff hotfix merge, deterministic scrub-shield test port,
and Release0.2.8 version/docs bump. **No candidate product edits or reruns.** Claude's fix-branch prerequisite
finished55 passed/exit0 before acquisition. Owned gate lock09:24–10:36, explicit fail-closed mkdir acquisition,
player0 at acquisition and every stage start, then exact-owner removal and **LOCK RELEASED10:36**.

1. Candidate impact standard300: **0 broken,0 exhausted**,604.563s, six workers. Actual entry remains False;
   independent goal/return/softlock oracle accepts every seed with all grotto placements withheld and identical
   spheres; neither grotto region/check contributes. The old main-only Hookshot-branch auditor was not misused.
2. Paired200 Broad/50 Defaults/50 Recommended against immutable5bc5577: exact inputs/effective settings/seed keys;
   reuse those audited candidate digests, no duplicate generation and no baseline regeneration. All300 placement
   and sphere digests differ. All17 prior-risk cases have new accepted placements: Broad13, Defaults1, Recommended3.
   Candidate first-try failures0/1/1 versus main0/1/2; zero exhaustion both arms. “17 rerolled” describes changed
   placements, not17 failed fill attempts (candidate302 total attempts).
3. Full format/lint passed:561 files already formatted.
4. Whole synthetic, **every OOT_* unset**, `uv run --locked --extra ui --with pytest-xdist pytest -n 8`,
   `CLAWSHOT_WORKERS=4`: **4425 passed,838 skipped**,24 existing parametrization warnings,474.09s.
5. Full dump with configured read-only romfs/NUP/r19 sword-layered dump, `--extra ui`, `-n 8`,
   `CLAWSHOT_WORKERS=3`: **836 passed**,24 existing warnings,3207.18s. Command wall for the complete chain4329.21s.

All pytest output, stage game counts and audit/pair JSON are retained outside the repository:
`work/r22-logic/release-0.2.8-1d3f1ff/{synthetic.log,dump.log,load-stages.log,impact.json,impact-rows.jsonl,paired.json}`.
Candidate is ready for Claude's publication decision; this is generator/model and dump evidence, not new in-game
proof of a grotto approach. GC model/platform/location scope and lack of native scrub/beehive destinations remain
as recorded above and were sent separately for the release notes' spoiler review.
