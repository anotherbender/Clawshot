# Round 17, Track B: dungeon items and rewards (cs17b)

Branch `r17/dungeon-items`, base `fcd5f2a` (0.2.2). Model: openai-codex/gpt-6.1-sol.
Research/output only under `E:/OOTRemake/work/r17-dungeon-items/`; dump read-only.
No player seed/save opened, no game started, no runtime folder written. No version bump.

## 1. Small keys audit — first

**Answer to Kareem: no. Gerudo Training Ground is already included, all nine keys.**
“Small keys anywhere” currently releases the eight ordinary dungeon families into shuffled
**chests**, not every object named a small key. The missing sources are the Well and Shadow
floor keys, the four Fortress jail keys, and the Treasure Chest Game's session keys.

| Native family | Native sources | Shuffled today / anywhere | Why not / what it would take |
|---|---|---|---|
| Forest Temple | 5 chests | Yes, all 5 | Existing named Forest grant; default keeps them home. |
| Fire Temple | 8 chests | Yes, all 8 | No starting/free ninth key in this remake. |
| Water Temple | 4 chests | Yes, all 4 | N64 six-key count is capped to remake four. |
| Spirit Temple | 5 chests | Yes, all 5 | Outdoor statue hands require named credit, already supported. |
| Shadow Temple | 4 chests + 1 skull-pot floor key | Chests yes (4); floor no | `Collectable` source is not an admitted heart-piece `Freestanding` adapter. Needs source-specific collection/spawn/once-only trace and arbitrary-reward delivery; retain its native key/logic until then. |
| Bottom of the Well | 1 chest + 1 floor key | Chest yes (1); floor no | Same source-adapter gap. World's inherited vanilla labels include a second key chest, but native `remake_vanilla` corrects that chest's actual reward; do not count it twice. |
| Gerudo Training Ground / Proving Grounds | 9 chests | Yes, all 9 | The inherited name “Freestanding Key” is now chest Hash `1883068192328530224`, not a missing floor source. |
| Ganon's Castle | 1 chest | Yes (1) | N64 two-key count is capped to remake one. |
| Thieves' Hideout / Gerudo Fortress | 4 jail-key identities (`Obj_Dungeon_SmallKey_GerudoFortress_01..04`), placed event/drop representations | No | `HideoutSmallKey`, not `SmallKey`; no mapped logical dungeon/named target adapter. Need four guard/drop/check identities, rescue/door/event-state trace, canonical fortress credit and grant replacement, then source and reload tests. Eight census placements are not eight obtainable keys. Gerudo Membership Card remains native per D39. |
| Treasure Chest Game | Salesman's entry key + 5 winning room keys (`Obj_MiniGame_SmallKey`) | No | `TCGSmallKey`; native minigame/session flow, D17 keeps room boxes vanilla. Needs an explicit product decision plus session/reset/door accounting and source adapter, not generic DungeonInfo writes. |
| Deku Tree, Dodongo's Cavern, Jabu-Jabu, Ice Cavern | No small-key sources | Not applicable | Saved DungeonInfo fields existing does not create collectible keys. |

Evidence: read-only `audit_keys.py` scans the supported dump and the loaded world;
`data/item_actors.toml:84–91`, `patch/key_targets.py`, `generate/fill.py` (`allowed`,
`shuffled_locations`), `data/world/remake.toml` key caps and D17, and
`remake/adult_gerudo_training_ground.toml` identify the nine-key correspondence.
Actual chest pool: **37 small keys** (5+8+4+5+4+1+9+1); two native floor keys stay fixed.
No new in-game evidence is claimed; prior played named-key gates are in r12-keys.
**Product decision (Claude relaying Kareem, 2026-11-17): follow OoT Randomizer's split.
The existing small-key setting should include Well/Shadow floor keys if their sources can safely
carry items; otherwise explicitly hold them. Fortress jail keys get their own default-off setting.
Treasure Chest Game keys remain research-only, owned by cs17c. Priority: #14, floor keys, jail keys,
then reward/bridge plans.**

## 2. Maps, compasses and boss keys (#14)

**Provisional #14 setting design (cs17b, posted to thread): add `dungeon_items=all_anywhere`
as a combined experimental opt-in, while `own_dungeon` and small-key-only `anywhere` retain
their meanings and presets/defaults do not change. All supported dungeon families remain
chest-only when sent outside their dungeon.**

Saved state is not pouch stock: each `DungeonInfo.<target>` has reset8/save0 Bools
`IsGetMap`, `IsGetCompass`, `IsGetBossKey`. The ten map/compass target pairs are Deku,
Dodongo, Jabu, Forest, Fire, Water, Spirit, Shadow, Well and Ice Cavern. Boss keys belong
to Forest, Fire, Water, Spirit, Shadow and Ganon's Castle. Generic item actors have no
dungeon argument. Big chest native actions resolve the live dungeon component; small
chests omit map/compass/boss credit (`NotPushToPouch`), repaired on main since r13.

The existing source-bound compiler can write another dungeon's saved Bool without changing
the standing dungeon. This is a data-only grant path, not an exefs/runtime patch.
Off-area text now names both the family and target dungeon using English names read
from the dump; no copied game text. Off-area boss pickups must not animate the *standing*
dungeon's boss-key indicator. Own native grants and their played indicator remain intact.
Even a chest retaining the same generic actor must rebind if the logical target changes.
Native-source contracts are checked for every physical copy before fill.

Prior in-game evidence, not replayed here: r13 maps/compasses literal target writes saved
and filled pause-map boxes/markers; native boss helper saved credit, displayed the pickup
indicator and opened the Forest boss door normally. **Off-dungeon map/compass/boss-key
delivery in this new mode is built evidence only until Kareem plays the packet.**

### Native consumers and the presentation boundary

Fresh read-only trace: `native-consumers-findings.md`, `na.py`, native disassembly and graph
catalogs under the external research root. Addresses below are native `e0f3ccfa` VAs, not
copied GPL runtime code.

| Consumer/writer | Exact contract |
|---|---|
| Current component and saved accessors | `0xb2af20` / `0xb2afc0`, component `+0x268` selects live DungeonInfo. Map/compass/boss getters `0x3282be0` / `0x3282c40` / `0x3282ca0` re-read GameData, no ownership cache. |
| Native grants | Map `0x28cb1c0` → `0x3282fe0`; compass `0x28caff0` → `0x3283060`; boss `0x28cae10` → `0x32830e0`. No target argument. Boss additionally sets an unsaved panel-animation request (`0xfa99a9b8`). |
| Boss door | `BossDoorChainLock.root`: `QueryDungeonIsGetBossKey` (`0x29ebd70`) reads the standing dungeon's live saved Bool. Opening writes `IsChainLockDoorOpen.<controller ID>`; it does **not** consume the boss key. **[INFERENCE, strong]** a remote literal write satisfies this same predicate after entering its target. |
| Map screen | `UIMapMenuScreen` open `0x33e12c0`, refresh `0x33e4200`: current map/compass/boss fields read into `+0x1538/39/3a`. Map/compass layout `0x58b300`; four-item icon row `0xb29240`. Literal map/compass menus already played in r13. |
| Boss icon | `OneShotSetDisplayBossKey` `0x2932e50` forces current screen `+0x235b`, not ownership. Persistent boss panel `0x587260` has additional room/mode predicates. A literal boss grant does **not** guarantee an icon; r13's literal trial showed none. No target-dungeon indicator is invented. |
| Get windows | Actor-generic `GetPouchContent`/`EventTriggerSetForGetWindow` supplies native item presentation. Generic saved `IsGet.Item_Dungeon_*` is not the door/map ownership oracle. Named replacement text is required outside the target. |

Ganon's boss key normalizes to `DungeonInfo.InsideGanonCastle.IsGetBossKey`, not a
separate pouch item. The struct has other non-item members; the six key/map fields listed
in r11 were not a claim that the entire struct has only six members.

### keysanity clarification — released 0.2.2 is unaffected

The native world's `keysanity` lives in `spec.flags`, while old `prepare` normalized only
`spec.settings`. **This is inert metadata in stock 0.2.2, not a broken native grant.**
Read-only traversal printed **zero live rule strings reading keysanity**. The sole
translated use (`fire_temple.toml:15`) is overridden by `adult_fire_temple.toml:9–12`:
eight acquired Fire keys AND Hammer in every mode. Native credit, door spending, HUD,
reloads and beatability have no dependency on this missing normalization. The earlier
played anywhere gates are consistent; this finding does not make those seeds unfinishable.
After Claude requested the player-facing proof, cs17b preserved old `anywhere` behavior
and effective settings. Only new `all_anywhere` normalizes native flag metadata to true;
synthetic specs exposing a settings entry retain the existing normalization.

### Built packet and observed offline checks

- New own test seed **170214**, input-pinned three Forest items to Mido's house; full goal
  and normal beatability oracle retained. `stage-14-proof.json`: **113 resources, 22 spheres**,
  emitted chest-binding readback and target fields passed. v2 RomFS digest:
  `3bb5397aab51fb5e5c04942432942f754950a84d8ee880be4c79d526fd28f6c6`.
- Current output: `E:/OOTRemake/work/r17-dungeon-items/ingame/mods/r17-dungeon-items-170214-v2/r17-dungeon-items-170214-v2`.
  No fixture working-set additions: all changed resource paths already used by the existing
  dungeon-item, progressive, door and text pipeline.
- Launcher: `ingame/Test - dungeon items 170214.bat`, adapted from the current Longshot
  template, one real mod, `HOS_FS_OVERLAY` cleared, only a new empty user folder. Actual
  `CLAWSHOT_DRY_RUN=1` via cmd: **exit 0**, selected `builds/rc/bin/longshot.exe`; no boot.
- `ingame/CHECK-DUNGEON-ITEMS.md`: **5–8 minutes** for child pickups, named windows,
  Save/Continue and Forest map/compass menu. Literal boss-door acceptance requires adult
  and a valid B2F approach; deliberately **not included in the short estimate**.
  Claude boot-checks; Kareem plays. No need for Kareem before his morning session.
- Actual browser surface: selected the experimental option, saw the changed settings
  string/help, and unchecked Chests; UI displayed the explicit chest-required refusal.
  Discovery used an isolated empty seed library; no personal seed was opened.
- Initial staging attempt printed late priority filler unplaced: map/compass pins had only
  banned the items elsewhere, not reserved their destination from earlier progression.
  Printed destination/type/class values, then added the reciprocal input exclusions.
  The aimed rebuild passed. No fill-policy relaxation, fake grant or goal bypass.
- Focused grant/plan/text regressions:
  `CLAWSHOT_WORKERS=1 uv run pytest tests/test_dungeon_item_plan.py tests/test_dungeon_items.py tests/test_key_text.py -m 'not dump' -q`
  → **107 passed, 1 deselected, 2.23 s**.

### Added key-source priorities: explicit holds, not ineffective toggles

**Holds accepted by Claude, 2026-11-17: Well/Shadow floor keys and Fortress jail keys
are adapter plans only this round. The existing small-key mode will absorb Well/Shadow
sources once their actual pickup contracts are safe. Fortress gets a separate default-off
setting only with its complete source adapter. No ineffective toggle is exposed.**

All ten placed floor/jail representations use `AlwaysRespawn` and have **no saved actor
Hash**. `KeyItemSmallKey` carries `PouchActor=Item_Dungeon_SmallKey`; no per-instance
grant/event override exists. Ordinary saved-heart `Gyaml` replacement is not their contract.

| Source | Exact writer/reader and why held | What a safe adapter needs |
|---|---|---|
| Well floor key, Hash `17649154319341333603` | AiGroup `4420455204133201806`, `BottomOfTheWell_Level_Room_03Prefab_25d7`, ref `Obj_Dungeon_SmallKey_db9c`: level logic deletes on `BottomOfTheWell_Level_Room_03_Get_SmallKey`; pickup `Dead` sets that Bool and `_Get_Key`, then room-clear autosave. Both saved reset8/file0. | **[INFERENCE]** a native floor-palette reward may preserve this `Dead` retirement. Must establish replacement pickup death, missing-Hash save behavior (or add its permanent saved row), riddle retirement and Save/Continue. Until that source check, keep its native Well key. No arbitrary-major floor grant assumed. |
| Shadow floor key, Hash `12562389953863361839` | AiGroup `13772315372431787476`, `ShadowTemple_Level_Room_B3FB4F_F_Prefab_6cf3`: skull-pot death AND NOT `ShadowTemple_Level_Room_13_GetKey` creates key; key death sets it. Reveal flow `ShadowTemple_Gimmick:LargeJar_Key` binds actor `Obj_Dungeon_SmallKey`, plays `Act_Pop`/`Rotate_Obj`. | Source-specific reveal-event clone with valid actor binding/animation plus once-only pickup/room-clear proof. Blind replacement can hang or break reveal. This is a data-side candidate, not proof that a runtime hook is required. |
| Four Fortress jail identities | Thief drop, `SmallKeyForEvent_01..04` event copy, resting copy are three representations of each check. Root AI `Obj_Dungeon_SmallKey_GerudoFortress_0x.root` on `QueryDeathIsDead`, reason10, writes `IsGet_SmallKey_GerudoFortress.SmallKey0x`. Level logic recreates resting key while thief Destroy AND NOT that Bool. Rescue flow binds all four actor/instance names. | A per-identity actor-pack reward adapter could preserve names, key-shaped display and retirement while changing `PouchContentParam.PouchActor`; this is **unproven**, not impossible with data. Must cover all three representations, item-category/SpecialDeal semantics, duplicate prevention, all four rescues and normal jail-door spending/reload before admission. Plain actor/drop replacement loses retirement and can duplicate rewards. |

Fortress destination writes would use
`DungeonInfo.GerudoFortress.SmallKeyNum/SmallKeyTotalNum/IsGetSmallKeyOnce`;
`DungeonParam.GerudoFortress_Adult.TargetGameData` selects that struct, and ordinary
jail locks spend its remaining count. **[INFERENCE]** existing named-key delivery can
extend to that target. Inventory credit does not replace the source's four collected
Bools or carpenter rescue. Gerudo Pass stays native (D39). Treasure Chest Game remains
cs17c's research-only scope.

**Played fact (Kareem via Claude, 2026-11-17): each of the four Fortress jail keys is
dropped by the defeated guard and picked up from the floor, not handed over.** The
third guard lacking an explicit Banc DropActor override is not a missing key: the played
floor-drop fact wins over that incomplete placement-only view.

Future Fortress adapter invariants:

1. Treat each guard's floor pickup as one check across its drop/event/resting forms.
   Only **collecting the replacement reward** sets that source's existing
   `IsGet_SmallKey_GerudoFortress.SmallKey0x`; guard defeat alone must not retire an
   uncollected reward. Preserve its native corpse/drop, shutters, actor/instance bindings
   and restoration behavior.
2. A Fortress key found elsewhere changes only the three Fortress inventory leaves.
   It must **not** mark a guard reward collected, fake a guard defeat, increment rescued
   carpenters, or pre-clear the fortress. Model the native jail/guard gates, not a
   conjectured early-key bypass.
3. Preserve the native four-carpenter sequence and its Found/Helped counters, per-room
   carpenter states and ordinary jail-door key spending. After all four rescues, retain
   the captain's **`Meet_FourCarpenter_ClearEvent`**, including both the Gerudo Card grant
   and progression of `SageOfSpirit` to **Step02**. Do not substitute possession checks,
   default flags or another grant for this scene.
4. Keep D39's card check and card outside every shuffle pool. A moved card does not clear
   guards; Clawshot depends on that native scene, not card inventory. Acceptance must
   cover all four floor rewards, refusal/re-entry/Save–Continue, actual four rescues and
   the captain scene/card/Spirit Step02/cleared guards once, with no extra key source.

## 3. Dungeon rewards

### Native grants and distinct state

Read-only reproducers: `survey_rewards.py`, `decode_rewards.py`, `reward_state.py`;
external catalogs `reward-flow-hits.json`, `possession-reader-events.json`,
`reward-state-fields.json`, `completion-gate-graphs.json` and decoded `reward-graphs/`.
All event-flow files were scanned, including base and `.110` versions; no other
randomizer's code was used. The Discord observation supplied by Kareem is accepted as
a fact; the independent native trace below explains it.

These nine actors are ordinary native `KeyItem`s (`PouchSpecialDeal=None`,
`PouchGetType=Large`), unlike dungeon maps/keys. Native `GetPouchContent` grants them
through `PouchSystemActor.EventTriggerAddOrRemovePouchContent` with `Num=1`.
They have saved pouch stock (`PouchData.<actor>.StockNum`, reset32/file0) and separate
saved acquisition Bools (`IsGet.<actor>`, reset8/file0). They are not
`DungeonInfo.IsGetBossKey`, dungeon-clear flags, or the sage-count quest counter.

| Reward | Actual native granting flow/event |
|---|---|
| Kokiri Emerald | `Dm_Kokiri_0130/Event22` → `GetPouchContentByActorName(Item_Stone_Forest)` after Gohma blue warp |
| Goron Ruby | `Dm_DeathMtTrail_0025/Event26` → `Item_Stone_Fire`, in the post-Dodongo/Darunia sequence |
| Zora Sapphire | `Dm_ZoraFountain_0030/Event3` → `Item_Stone_Water`, after Barinade/blue warp. `Dm_InsideJabu_Jabu_0030.110/Event181` calls **DisplayRutoGetByActorName**, a display, not a second grant. |
| Forest / Fire / Water medallion | `Dm_Awake_Forest_Get.110/Event13`, `Dm_Awake_Fire_Get.110/Event13`, `Dm_Awake_Water_Get.110/Event13` → corresponding `Item_Medal_*` |
| Shadow / Spirit medallion | `Dm_Awake_Shadow_Get.110/Event3`, `Dm_Awake_Spirit_Get.110/Event14` → corresponding `Item_Medal_*` |
| Light medallion | `Dm_SageRoom_0005/Event48` → `Item_Medal_Light` during the first Master Sword/Rauru sequence; no Light dungeon boss |

The active five adult reward files are `.110` according to
`EventFlowFileEntry.Product.110`; the base copies have matching reward sites but
patching only base would miss the active grants. The boss heart is a separate check.
`Dm_SY_BancChange_EscapeDungeon` retains first-clear/sage/completion sequencing:
Forest `Event199`, Fire `Event40`, Water `Event41`, Shadow `Event73`, Spirit
`Event141` advance their sage quests to Complete; child quest completion uses
`Event1`/`Event46`/`Event77`. Its five `AllSage_AwakeSageCount -= 1` writes
(`Event249/251/252/253/267`) count **completed sage sequences**, default5, not medals.

### Requested gate readers — possession versus completion

| Gate/reader | What it actually reads and who writes that state | Shuffle consequence |
|---|---|---|
| Door of Time stones | `DoorOfTime:DoorOfTime_CheckStoneNum` `Event38/39/56` reads `Get_StoneOfFire_IsCompleted_Exp` and `Get_StoneOfWater_IsCompleted_Exp`, backed by `Step_Get_StoneOf*`; normal route already assumes Forest. Both clear → `Event37` advances DoorOfTime Step03. `Event4/5/6` set `DoorOfTime_GetStoneCount` to 0/1/2 **remaining Fire/Water quests**, not total stones owned. | Moving three stone actors does not update this gate. Do not reuse this counter for a bridge threshold. A reward-ownership Door must check all three actual stone identities and preserve the real Zelda/Impa/clock chain. |
| Door opening and altar | `DoorOfTime_OpenDoor`: quest beyond Step04, melody4/recommended song, unopened/history guards; native door/altar logic follows DoorOfTime Step06, not stone pouch entries. `Event53` sets `Market_Child_TimeTempleDoor_Opened`; `Event57` writes Step06. | Separate source progression from ownership and from visual altar stones. Never fake stone-quest Complete to get an early door. Existing round16 send-off/recount/clock fixes must compose unchanged. |
| Temple Sheik / Prelude and child return | `Market_Adult_Prefab_edc2` and native pedestal `_89da` read `SageOfForest_IsCompleted_Exp`; completion writer is EscapeDungeon `Event199`. Current `remake/sheik.toml` already models `'Defeat Phantom Ganon'`, not Forest Medallion; free travel patches only the return restriction/presence. | Preserve completion here unless maintainers explicitly change it. A found Forest Medallion must not fake Forest clear or Prelude. |
| Last-two-sages → Light Arrows | EscapeDungeon **`Event130` and `Event139`** transition to EventSetting **`SageRoom_Allsage_LastSage`**, flow `AllSage:SageRoom_AllSage_LastSage`. Its **`Event25`/`Event26` read `HavePlayedEvent.Dm_Awake_Spirit` AND `HavePlayedEvent.Dm_Awake_Shadow`**, auto-recorded when those awakening scenes finish. `Event8` plays `Dm_SageRoom_0010`; `Event20` advances AllSage Step02. These are completion-coupled **scene-history** Bools, not medallions, and not simply both quest enums. | Exact explanation of Kareem's supplied observation: changing either `_Get` reward leaves both awakening-history readers true. Stock medallions are irrelevant to this trigger. |
| Temple Light-Arrow scene | `Market_Adult_Prefab_c668` node2 requires **AllSage exactly Step02**, area contact requests `Market_Adult_Field_GetArrowLight`; `AllSage` runs its Temple sequence, including `Dm_TimeTemple_0130/Event85`'s actual `Item_Arrow_Light` grant. `AllSage/Event10` writes AllSage Complete and **`Event11` writes Defeat_Ganon Step01**. `_50e3` separately gates the earlier Step01 scene; `_7f43` Sheik deletion reads Prelude's saved Bool. | Merely replacing medal grants leaves Light Arrows on native completion. Ownership-driven LACS requires a new eligibility/readiness trigger, not just a different item string. |
| Rainbow bridge | `GanonCastle_Level_Field_00_Prefab_14ba` reads `Defeat_Ganon_IsAfter_Ready_Exp` and NOT `Defeat_Ganon_IsAfter_Step01_Exp` (effectively native Step01 interval). Writer above is the Light-Arrow story chain, not possession. Detail in item4. | Native last-two completion → Temple scene → Step01 can open the bridge even with shuffled medals absent. No bridge stock-medallion reader was found. |
| Six Ganon trials | `Gimmick_ArrowLight_BarrierRemove_{Forest_00_3ea1,Fire_00_7ae6,Water_00_2f94,Shadow_00_30ca,Spirit_00_47c2,01_ed01}` wrap native **`ActorLogicInsideGanonCastleCore`**. Per-trial `Defeat_Ganon` entries set `InsideGanonCastle_Dungeon_BarrierRemove_<element>` true and decrement saved `...Barrier_Count` (default6). The six removal writers are `Event7/19/11/15/23/3`; decrements `Event68/79/69/70/93/83`. | These barriers track **trial clear**, not the matching medallion. No reward-ownership query appears in those data wrappers. Native core damage internals were not fully disassembled; do not turn the module's Light-Arrow name into a new medal requirement. |
| Tower barrier readers | `InsideGanonCastle_Common_e780` reads all six removal Bools (nodes30/32/34/36/38/40); room1 `_4ab0` reads `...Barrier_Count` at node9 and compares it; flow `Event606` tests count≤0, then `Event778` writes `InsideGanonCastle_IsAllBarrierClear`. Room1 `_75af` reads this Bool and `HavePlayedEvent.Dm_InsideGanonCastle_0090`. | Reward shuffle/bridge settings must not decrement this counter, set these clear Bools, or skip trials. Ganon boss-key ownership remains separate again. |

Current native-world logic deliberately uses all five medal names for LACS
(`remake/adult_temple_of_time.toml`) as a conservative proxy for the documented completed
sage route. With native rewards this is conservative; **it becomes wrong after reward
shuffle**. The bridge's translated vanilla helper also reads Shadow+Spirit+Light Arrows.
Do not enable reward shuffle without replacing these proxy rules with the chosen native
or ownership predicates. No current reward shuffle is enabled by this branch.

### Proposed implementation, not built this round

**Product questions (cs17b): shuffle only among the nine dungeon-reward slots, or put
rewards into the wider item pool? Include Rauru's Light Medallion as one of the six medals
and nine rewards (recommended: yes)? Should vanilla Door/LACS remain completion-driven,
or should shuffled reward ownership drive them? The bridge's configurable ownership
condition is separate from the Light-Arrow grant condition.**

1. Start with an explicit default-off reward-only pool and stable census flow/event IDs.
   Admit the nine ordinary pouch actors, all active file versions, correct one-time
   grant sites, separate boss hearts, and the first-pull Light slot. Preserve native
   blue warps, sage-history, completion, world restoration, carpenter/card and time travel.
2. Patch the actual item grant, not the awakening/completion state. Review fixed
   cutscene actors/model binds as well as the get window: a one-string grant swap is
   not proof of correct sage/stone presentation.
3. For ownership gates, use the nine real nonconsumable reward identities, not
   `AllSage_AwakeSageCount`, scene histories or forced quest completion. Make Door,
   LACS and bridge trigger changes **together with matching logic**, not merely a
   solver setting. Keep Prelude and Forest-return completion separate.
4. Required oracle: each reward granted once in active `.110` routes; source inverse
   diffs and readback; each actual ownership subset versus each chosen gate; native
   completion must not pass an ownership gate without rewards, and early rewards must
   not complete dungeons. Preserve second sword pull, late Prelude and six trials.
   In game: displaced stone + adult medal + Light slot, completion without owned
   Shadow/Spirit medals, early owned medals without completion, re-entry/reload.

**Data-only assessment:** the nine grants themselves are ordinary data-side pouch calls,
and ownership predicates/area triggers have data-side candidates. A complete reward
shuffle is **not yet proven safe merely by changing those strings**: the coupled
Door/AllSage/bridge triggers and scene bindings need the above cutover. Per the requested
research-first scope, this branch contains a plan, not a partially wired reward feature.

## 4. Ganon's Castle condition

### Exact native bridge chain

1. `Dm_SY_BancChange_EscapeDungeon` enters each sage sequence; its Shadow/Spirit routes
   request `SageRoom_Allsage_LastSage`. `AllSage/Event25` + `Event26` read the two
   awakening histories, then `Event20` writes **AllSage Step02**.
2. `Market_Adult_Prefab_c668` node2 reads **AllSage Step02**; its area contact requests
   `Market_Adult_Field_GetArrowLight`. Native Temple scenes grant Light Arrows; ending
   `AllSage/Event10` completes AllSage and **Event11 advances Defeat_Ganon to Step01**.
3. `Logic/GanonCastle_Level_Field_00_Prefab_14ba.logic.module.ainb`:
   node4 reads `Defeat_Ganon_IsAfter_Ready_Exp`, node3
   `Defeat_Ganon_IsAfter_Step01_Exp`; nodes5/6 create both approach areas when the
   lower predicate is true and upper predicate false. Node13 ANDs the two Player-area
   contacts and native player-state query (enum2, meaning not asserted here); node0
   requests **`GanonCastle_Adult_Field_Rainbow`**.
4. EventSetting maps that name to **`Defeat_Ganon:GanonCastle_Adult_Field_Rainbow`**.
   It preloads InsideGanonCastle (`Event770`), participates the player, sets event Bool
   (`Event701`), plays **`Dm_InsideGanonCastle_0000`** (`Event0`), then sets
   **EventBoolEX1** (`Event759`) and **Defeat_Ganon Step02** (`Event1`).
5. Node10 `OperateORFixInputTrue` creates the bridge actor
   `Obj_GanonCastle_Bridge_A_01_60c4` from **HavePlayedEvent of the rainbow event**
   (node8) OR that event's EX1. Native history is saved reset8/file0 and supplies the
   durable reload path. That is the bridge's actual saved latch, not medal count.

`Defeat_Ganon` quest expressions are unsaved BoolExp over saved `Step_Defeat_Ganon`;
the rainbow event history is a different saved Bool. Neither
`AllSage_AwakeSageCount` (default5) nor trial `Barrier_Count` (default6) counts held
rewards. Do not repurpose them.

### Data-side N-of-rewards design

**Proposed product contract (cs17b, not decided): default `vanilla` retains the exact
completion/story chain. Opt-in `stones N` allows 0..3, `medallions N` 0..6,
`rewards N` 0..9, counting unique possessed rewards, including Light if approved.
Should Light Arrows also be required to open the bridge, or only later to clear trials?
Recommendation: the chosen count alone controls entry; native trial/Bow/Magic/Light-Arrow
requirements remain, and LACS has its own explicitly chosen rule.**

- Define an unsaved `Clawshot.BridgeEligible` BoolExp from **saved reward ownership**.
  Do not maintain an increment-only saved counter: duplicate grants, arbitrary source
  order and reload must not inflate it. Native `IsGet.Item_Stone_*`/`IsGet.Item_Medal_*`
  are permanent acquisition identities; confirm equivalence with actual pouch stock
  for all nine before selecting them as the ownership oracle. These KeyItems are
  nonconsumable, but a temporary DreamWorld inventory must not open the real bridge.
- Native BoolExp already supports Bool/BoolExp operands and AND/OR/NOT (round10's
  played presence patch). A bounded threshold can use small deterministic DP rows:
  “at least k among first i” = previous threshold OR (owned i AND previous k−1).
  At most a small 9×9 table, no exponential combination list or runtime code patch.
  Handle N=0 as true; reject out-of-range/noninteger values before generation.
- Patch **only this bridge module's eligibility string input** (node4) to the new
  expression, retaining its approach sensors, player-state guard, event lifecycle,
  upper-stage guard and durable history latch. A hash-pinned, exact same-slot AINB
  string substitution is a data-only candidate as used by the existing Door patch;
  prove decoded graph delta, length/allocation and all references. Do not globally
  redefine native Defeat_Ganon expressions or initialize AllSage/Defeat_Ganon complete.
- The native rainbow flow can then run on an earlier quest state. **Unresolved safety
  edge:** its Step02 writer may precede the later Light-Arrow chain's Step01 writer.
  Establish forward-only progression and no scene suppression/regression; if this
  cannot be proven, refuse that setting rather than silently require the old completion
  route or fake completed sages. This ordering is why the plan is not advertised built.
- Add a top-level validated bridge setting with UI/CLI/CS1 support and an explicit
  native transform, not raw `--logic bridge=...`. Current native validation correctly
  refuses those unpaired logic overrides. Preserve defaults/presets. Logic uses the
  existing `has_stones`, `has_medallions`, `has_dungeon_rewards` predicates with the
  same selected identities and threshold; early castle access must still model all
  trial, Ganon-key and combat requirements.
- Proof before admission: all 512 ownership subsets × threshold/mode boundaries;
  duplicate ownership counts once; N−1 refusal, N acceptance; completion-without-
  rewards refusal and rewards-before-completion acceptance; temporary inventory,
  first bridge event, reload latch and late AllSage order. Decode exact native inverse
  changes, update the common resource-size table, and run a staged isolated Longshot
  N−1/N/Save–Continue check. No changes to the six trial-cleared flags/counter.

**Conclusion:** bridge eligibility has a concrete data-only route; safe early-story
ordering and the ownership oracle still need proof. This round delivers the exact
writers/readers and implementation plan, not an exposed bridge setting.

## Verification and handoff

Frozen build head before the full gate: `4224b5d0de5e4cf8c3705f271e0f02da9fe58d7a`.
The serialized gate waited for cs17c's measurement and cs17a's gate, then passed
format/lint. Synthetic output: **3253 passed, 371 skipped, one stale plan-shape failure**.
Its printed diff was the same-actor Fire Key Chest gaining the now-required off-area
target binding. That test artificially put a Forest key into Fire in `own_dungeon`
and required the plan to omit it, encoding the old wrong-credit behavior rather than a
valid generated own-dungeon placement. Removed that implementation-only test, not a
player-facing assertion: existing `test_native_placements_need_no_new_binding`
already covers unchanged local grants for all four families, and
`test_another_dungeons_key_in_a_key_chest_changes_while_its_own_stays` covers off-area
small-key credit. No Track B runtime code changed after that freeze.

### Rebased merge candidate

Claude moved main to `6ec4fdb` with Track A and directed a rebase before the full gate.
Cancelled the queued old-base corrective runner; the shared lock belonged to cs17c,
not this track, and was left untouched. No child pytest process remained.
`git rebase 6ec4fdb` completed cleanly.

Rebased focused command (`CLAWSHOT_WORKERS=1`, dump variables unset):
`uv run pytest tests/test_dungeon_item_plan.py tests/test_dungeon_items.py
tests/test_generate_dungeon_areas.py tests/test_key_text.py tests/test_key_model.py
tests/test_settings_native_logic.py tests/test_app_schema.py`
→ **959 passed, 2 skipped in 151.21 seconds**. Both runtime process counts were zero.

The merge candidate is frozen after this documentation update, before the full gate.
Gate commands use the requested xdist settings and existing round16 layered dump;
`E:/OOTRemake/work/r17-dungeon-items/gate-results.json` and `gate-{stage}.log`
retain the observed per-stage process checks, worker counts, exits and test output.
**Full rebased gate passed on `8454bd79905b39164ba024c75c31eb37633a7a99`:**

| Check | Observed result |
|---|---|
| `uv run ruff format --check` | exit0 |
| `uv run ruff check` | exit0 |
| `CLAWSHOT_WORKERS=12 uv run --with pytest-xdist pytest -n 12` | 3301 passed, 378 skipped; 221.41s |
| `CLAWSHOT_WORKERS=4 uv run --with pytest-xdist pytest -m dump -n 12` | 375 passed; 1079.10s |

The dump stage used all three requested dump variables and the existing round16
layered fixture; no additional fixture files were needed. Both pytest stages reported
36 existing iterator-parametrization deprecation warnings. No game process was present
at any stage start; the owned lock was released by the runner's finally block.
This final handoff update changes documentation only; runtime and tests remain those
of the passing frozen head.

**READY for review, not an in-game acceptance claim.** The experimental default-off
`all_anywhere` mode is built, generated/beatability/readback checked and UI-smoked.
Seed170214-v2's isolated Longshot packet is under
`E:/OOTRemake/work/r17-dungeon-items/ingame/`:
`Test - dungeon items 170214.bat` and `CHECK-DUNGEON-ITEMS.md`.
Claude must boot-check it; Kareem must show loaded-file proof plus named pickup,
destination map/compass/boss-door behavior and Save–Continue. No game was started,
and no player seed/save was opened or changed.

Accepted remaining scope: Well/Shadow floor keys and Fortress guard-dropped jail keys
are adapter plans only, preserving the four-rescue/card scene; Treasure Chest Game is
held and owned by cs17c. Reward shuffle and N-of-rewards bridge conditions are plans,
not exposed settings. Their unresolved product calls and native proof edges are above.
