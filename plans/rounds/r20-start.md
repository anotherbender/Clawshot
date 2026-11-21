# Round 20 — starting inventory (cs20c)

Branch `r20/start`, base `acbb903df111bb30609baedac35316b22d43700e`.
Model: `openai-codex/gpt-6.1-sol`. Research and generated artifacts:
`E:/OOTRemake/work/r20-start/`. **Implemented, built/not played; not READY.**
No game started; no player seed, original save or runtime folder written.

## Contract and provisional choices

Kareem requested default-off chosen items/songs, extra hearts, full wallet and dungeon maps/compasses.
Initial values must affect only New Game, not migrate or reset existing saves.
Every selected starting item is owned by logic before the first check; an equivalent shuffled pool copy
is replaced by junk, keeping the number of checks and pool size fixed, as requested (OoTR policy fact:
`work/r20-planning/feature-compare.md`, public-document sources only; no OoTR/SoH code opened).

**Provisional proposal by cs20c:** fields `starting_items=[]`, `starting_hearts=0` (extra hearts),
`starting_full_wallet=false`. Concrete progressive tiers represent a prefix of the family, never an
additional independently summed fixed tier. No arbitrary save-field editor. Unsafe/untraced choices
are refused with a clear error rather than accepted as inventory-only story completion.

## Initial-values extension hook (posted early on cs-r20)

Reuse `gamedata.FastStartSetting(name, default=False, skips=..., state=..., source=...,
logic=None, game_data={existing_field: typed_value}, flow_edits=())`; append to `chosen` before the
single `gamedata.changes(chosen)` in `patch.make_seed`. The existing planner validates native field
identity, reset bit, type, enum members and conflicting assignments. Initial changes compose before
Gift's extra Bools. Open/trials own their entries; neither creates a competing GameData writer.
No new hook abstraction is needed for Bool/Int/Enum entries.

Inventory additionally needs audited native New Game sequence handling: reset defaults are not the
last writer. `Sequence/Opening` runs `SetPouchAndStatusForGameStart` before creating Link/playing
opening events; that module writes three-heart health and establishes the small wallet/tunics.
Existing Nut Bag1/Nuts0 initialization is already a native ordered pouch push. It must remain
byte-identical with all new options off. Native upgrade grants are preferable to guessing derived
capacity/equipment fields; the implementation orders native grants after the original root completes.

## Feasibility sources

- `plans/03-game-data.md` sections14,19,30–31,37–38,44,46–49.
- `plans/rounds/r13-item-grants.md`: new-game native pouch sequence, container/quantity contracts,
  canonical identities, direct capacity/lift/depth behavior and item-bar initialization.
- `plans/rounds/r19-scenes.md`: stock-only ocarina lesson dispatch; either instrument keeps a native
  lesson at either age. Owning a song is not a source-history or quest-completion write.
- `plans/rounds/r19-sword.md`: owned canonical sword plus positive stock, era stash/restore and
  cinematic create/wait hazards; no normal item window inside a running scene/fade.
- `plans/rounds/r19-lacs.md`: actual Shadow/Spirit awakening chain, not medal ownership.
- `E:/OOTRemake/work/refs/sloperina-FINDINGS.md` (GPL documentation, facts only), section1
  (GameData, pouch stock/history, String64 equipment selectors), section5.7 (upgrades require pouch
  identity and numeric capability), section5.8 (map/compass Bools and explored-room display).
  No implementation copied. Native independent verification and field table follow below.

## Feasibility table posted before implementation

Fresh independent native decode: unmodified research-only `ainb` 0.2.16 outside the repository.
Reproducers/JSON are under `work/r20-start/`; no decoder implementation or game tree is copied here.
`SetPouchAndStatusForGameStart` SHA256 matches the production fingerprint. Its root is Simultaneous,
so added progression grants must run **after** all native children complete, not race MPMax=0.

| Field(s), canonical identities | New Game value / last writer | Other consumers and consequence | Implementation boundary |
|---|---|---|---|
| `PouchData.<identity>.StockNum` | Native reset5 clears reset32 Ints to0; native pouch push establishes stock | Inventory menu, pouch-existence lesson guard, progressive selection and item use read actual stock; `IsGet` alone is insufficient | Never force through bit8 default hook; native positive pushes after setup |
| `IsGet.<identity>` | Saved Bool reset8 false; native pouch addition marks acquired | Item menu, world/story gates and progressive bonus checks; not source/scene completion | Let native grant set it; never set `HavePlayedEvent` to manufacture a pickup |
| `Weapon_Sword_Kokiri`, `Weapon_Sword_Master`, `Weapon_Sword_Biggoron` stock/history | Sword acquisition actor canonicalizes to real weapon | Mido needs equipped Kokiri plus shield; era swap saves/restores owned blades; Master cinematic waits must not request unowned gear | No fabricated equip/history; Master requires the existing experimental shuffle and free-travel policy |
| `Weapon_Shield_Deku/Hylian/Mirror`; `Armor_Adult_Goron/Zora/HeavyBoot/HoverBoot` stock/history | Native equipment mapping from acquisition actor | Pause equipment and per-age gear use; shield shop tutorial follows purchase, not mere ownership | Pouch ownership, manual menu equip; no purchase/tutorial/story flag precompletion |
| `Item_Boomerang`, `Item_Hammer`, `Item_Hookshot/Longshot`, `Weapon_Range_SlingShot/Bow` stock/history | Native pushes; ranged weapons need a separate bag | Item menu/bar and combat; wrong-age items must not be assigned to live buttons | Keep the played Nut Bag1/Nuts0 initialization; establish weapon companions before weapon |
| `PlayerStatus.EquipWeapon/EquipShield/EquipArmor/EquipBoot/EquipOcarina` | Native saved String64 selectors and equipment sync, not acquired history | Live equipment creation, songs and era stash/restore | Ocarina selector needs explicit verified initialization; no unrelated forced equip |
| `Item_Ocarina_Fairy/Time` stock/history | Native push | Round19 lesson guard accepts either positive stock at either age; active playing uses `EquipOcarina` | Preserve lessons; Time must remain selected after later Fairy; no lesson history initialized |
| `Item_Melody_ZeldaLullaby/EponaSong/SariaSong/SunSong/TimeSong/StormSong` | `IsGet` saved Bool; songs have no stock cell | Playing, frog checks and dialogue; Epona requires Malon's source, not remote song; Windmill owns four source-local ownership queries | Native ownership only; Windmill queries use existing first-lesson history; all twelve caller continuations retained |
| `Item_Melody_ForestMinuet/FireBolero/WaterSerenade/SpiritRequiem/ShadowNocturne/LightPrelude` | Same `IsGet` acquisition | Warp access separate from movie history; Serenade source is Ice chest; Prelude source is Forest completion plus real scene | No Ice/Forest completion or Sheik-deletion flags; retain caller continuations |
| `PouchContentMaxNum.Bomb`, `Item_BombBag_Small/Medium/Large` | Native capacity expansion20/30/40 | Bomb/Bombchu counts; bombs additionally require child Bracelet/adult strength (D30) | Progressive prefix, native bag grant; no new Bombchu ownership from a bag |
| `PouchContentMaxNum.Arrow`, `Item_Quiver_Small/Medium/Large`, `Item_Arrow_Normal.StockNum` | Native bag30/40/50, native full stock declaration | Bow ownership is independent; ammo refills cannot establish it | Companion bag then Bow; selected upgrade implies complete prefix |
| `PouchContentMaxNum.DekuSeed`, `Item_BulletBag_Small/Medium/Large`, `Item_DekuSeed.StockNum` | Native bag30/40/50, native full stock declaration | Slingshot ownership independent | Companion bag then Slingshot, complete prefix |
| `PouchContentMaxNum.DekuNut/DekuStick`, `Item_NutBag_*`, `Item_StickBag_*`, counted ammo | Small20/10; medium30/20; large40/30. Small bags do not refill; medium/large declare full stock | Ammo usability and container screens; no assumption that a refill grants its bag | Existing zero-nut setup retained; arbitrary raw-ammo choices refused unless container/quantity contract admitted |
| `Armor_Child_Gauntlet_Goron`, `Armor_Adult_Gauntlet_Silver/Gold`, `PlayerStatus.LiftGrade` | Native grant writes Low/Middle/High; initial None, no sequence overwrite | Bomb lifting and strength gates; child Bracelet is independent across era change; lower native strength can downgrade | Ordered full prefix; existing source bonus guards retained; child ownership explicit |
| `Item_Scale_Silver/Gold`, `PlayerStatus.DiveDepth` | Native depth expansion; default Float3.0, no sequence overwrite | Diving ability/menu; native lower scale can downgrade | Native prefix and existing bonus guards, never a guessed Float default |
| `Item_FairyBless_MP/MPDouble`, magic sources, `PlayerStatus.MP/MPMax/MPEconomy` | Native setup writes0; grants establish240/480 live saved capacity (PouchActorInfo metadata24/48) | Magic use/HUD/progressive selector; spell/Lens/arrows provide meter floor | Ordered grants after setup; never race initializer0; Lens active-equipment side effects require explicit review |
| `Item_FairyBless_DefenseDouble`, `PlayerStatus.IsDefenseUP` | Native grant; initial Bool false, no sequence overwrite | Damage reduction and collection menu | Native acquisition, no fairy source completion |
| `PlayerStatus.Life/MaxLife` | Int12 overwritten by initializer nodes4/5, literal value offsets0x11c8/0x11e8 | Health HUD, damage and healing; Continue only raises Life to12 if below12, not MaxLife | Patch both native quarter-heart literals to4×(3+extra); no fake acquired boss heart/source |
| `Item_Wallet_Small/Medium/Large`, `PouchContentMaxNum.Rupee` | Native node7 pushes Small200; upgrades500/1000 | Shop/fee affordability and menu use pouch identity plus capacity | Choose native initial wallet tier; prevent transient small-capacity ambiguity before full balance |
| `PlayerStatus.CurrentRupee` | Saved Int reset8 default0; no initializer write | Live balance/payment; rupee pouch stock is not the money counter | Full-wallet default equals selected native capacity200/500/1000; no repeating refill or existing-save edit |
| `DungeonInfo.<dungeon>.IsGetMap/IsGetCompass` | Saved Bool reset8 false; no initializer write | Map screen reads on open; a real explored room/door entry is still needed (FINDINGS5.8) | Existing default hook sets selected Bools; no generic dungeon-item pouch grant |
| `DungeonInfo.<dungeon>.SmallKeyNum/SmallKeyTotalNum/IsGetSmallKeyOnce/IsGetBossKey` | Saved reset8 zero/false; native source-bound key handler updates named dungeon | Locks spend remaining only; acquired total/once distinct | Not offered as starts in this track; generic pouch push cannot credit a dungeon |
| Trade, Gerudo Card, stones/medallions, bottle special cells, masks, source histories/quest enums | Separate native contracts, not interchangeable `StockNum` assignments | Shared trade UI can hide child Cucco/Letter; card alone does not clear guards; rewards do not complete sages; bottles use special valid/content cells | Refuse unsupported choices, never substitute inventory for story completion; final supported list follows concrete native checks |

Dungeon targets for ordinary map/compass options: `InsideTheDekuTree`, `DodongoCavern`,
`InsideJabuJabuBelly`, `ForestTemple`, `FireTemple`, `WaterTemple`, `ShadowTemple`, `SpiritTemple`,
`BottomOfTheWell`, `IceCavern`. GTG/castle have no ordinary map/compass pool items; no invented options.
`GerudoFortress`/`FinalBattleField` schema rows are not evidence of a normal map/compass grant.

Source/story effects remain distinct: starting Lullaby/Time/ocarina does not finish Impa's send-off,
starting Epona's Song does not advance `Get_Epona`, starting Prelude does not clear Forest or delete Sheik,
and starting a sword does not set era/pedestal/first-pull history. Gameplay remains unplayed.


## Verification and staging

Native/cache focus: **12 passed** (272.07s, n2/internal1); after current-main rebase, inventory/start/fast-start
focus: **34 passed** (5.39s, n2/internal1), including the approved exact Bracelet advice.
Actual CLI with two selected starts, +3 hearts and full wallet emitted a CS1 recipe successfully.
Exact-head byte parity, sweeps and full gate remain pending; assigned gate turn4 follows cs20h's explicit release.
All changed game behavior is **built, not played** until the paired checks below pass.

### Implemented contract

- CLI, settings codec, shared app schema and actual browser controls expose the same default-off fields.
  Headless Playwright exercised item selection, extra hearts, full wallet and resulting CS1;
  screenshot `work/r20-start/ui-start-on.png`. Owned browser/server were closed; no visible Chrome remains.
- Positive native pouch grants run after the complete original New Game initializer. Bags precede ranged weapons,
  every upgrade prefix is ordered, native MP setup cannot overwrite a starting spell's meter, and native health
  literals become six full hearts for the staged +3 setting. No ordinary get window or new event is added.
- Initial-values hook also accepts bounded existing String64 selectors, so a starting ocarina is active.
  Selected map/compass flags and wallet balance use the same typed, reset-validated hook as other initial values.
- The four Windmill ownership queries use existing first-lesson history when Storms is prelearned; cases and
  continuations are unchanged. A production event-registration recipe covers this writer.
- Provisional pool proposal above is implemented: only shuffled copies become red rupees; fixed native sources
  remain. Starting songs use the existing ordered song palette, not a post-fill repair.

### Starting strength and the adult-return bound

The native cache recipe exposed a real safety issue: all progression and Triforce were reachable, but the
earliest-pull return oracle failed. Printed minimum inventory had Saria0, `return_open=false`, adult Mido=false.
Starting the Bracelet bypasses native Darunia acquisition, so the old closed-door inherited Saria assumption
is no longer justified. Own catalog data `starting_return_bypasses` removes that inherited count and adds Saria
to existing return-kit families. The final earliest-pull oracle and fill stages are unchanged.

Defaults + starting Bracelet alone is refused when Saria stays at its fixed child source. Starting Saria too,
Gift/song shuffle, or free time travel resolves this generator limitation; no invisible song is granted.
The same applies to a higher starting strength prefix. Claude approved the narrow Bracelet-only refusal advice
on cs-r20 (2026-11-20); every other refusal retains its existing text. A regression pins the requested sentence.
The Broad sweep retains two songs and exercises forward-placed Saria; fixed-song presets also start Saria,
explicitly recorded in each CS1 receipt. All-off preparation returns before any new bound/pool transformation.

### Paired Longshot 3.0.0 play check

Private seed `20032021`; candidate starts Kokiri Sword, Deku Shield, Boomerang, Slingshot, Bomb Bag,
Goron Bracelet, Hookshot, Ocarina of Time, Zelda's Lullaby, Song of Storms, Adult Wallet,
Deku Tree map/compass, three extra hearts and a full wallet. Both arms use existing open forest,
open Door and free time travel to keep the check bounded; this does not grant Zelda/Impa's source history.
Control is built from exported actual main with the starting fields absent. Output heads/hashes are recorded
externally by the packet builder; packet build and launcher dry run remain pending.

Launchers under `E:/OOTRemake/work/r20-start/`:

| Arm | Part A | Part B (same private profile) |
|---|---|---|
| Candidate | `candidate-A-inventory.bat` | `candidate-B-lessons-era.bat` |
| Main control | `main-control-A-inventory.bat` | `main-control-B-lessons-era.bat` |

Every launcher pins **Longshot 3.0.0** stable, one packet-owned mod, unset `HOS_FS_OVERLAY` and an initially
empty packet-owned save folder. A and B share only their own arm's profile. No natural save can demonstrate
New Game initialization; no original save is read or edited. Never replace a profile with an edited save.
If restarting after a failure, keep the failed profile/log and ask for a new packet profile rather than deleting it.

**Part A, candidate 8–12 minutes; control 4–8 minutes (estimates, not timed in game):**

1. Run the arm's A launcher, select New Game. Candidate: six full hearts, 500 rupees; control: three hearts,
   native 0 balance and none of the chosen starting gear/songs/maps. Existing zero-nut initialization stays.
   Pause: candidate has the listed child/adult equipment and both songs; no precompleted lesson is claimed.
2. Candidate: equip Kokiri Sword/Deku Shield manually, assign/fire Slingshot and Boomerang outside the house,
   lift a liftable rock and use a bomb. Expect native bag/counts and actual actions, not just menu icons.
   Do not use debug item, quest, inventory or age edits. Adult Hookshot is checked in B.
3. Both: walk through the real Deku Tree entrance (open-forest option permits control without a sword).
   Open its dungeon map. Candidate's map/compass must display for that real entered dungeon; control lacks them.
   Do not teleport directly inside an unexplored room and interpret a blank map as a field failure.
4. Candidate: spend a known amount at a shop and note the remaining rupees. Both: leave forest normally,
   complete Saria's bridge handoff and Field owl encounter. Candidate must keep Time active after Fairy;
   control receives/uses Fairy normally. Save in the Field and quit. Keep A's log before running B.

**Part B, each arm 20–30 minutes (estimate; separate natural Continue break):**

1. Continue that arm. Candidate retains six-heart capacity and the noted post-purchase balance; initialization
   must not refill the wallet. Both retain ordinary save progress. No save edits.
2. Follow the native Malon egg/Talon/courtyard route and meet Zelda. Clock adjustment for hatching is allowed;
   teleport/clock only, never inventory, quest, age or completion changes. Finish Impa's actual lesson/send-off.
   Candidate's already-owned Lullaby must not skip, strand or loop the lesson. Control learns it normally.
3. Enter Temple of Time normally and pull the unshuffled Master Sword. Candidate must not lose its stored
   child Kokiri Sword; adult gear can be equipped/used. Fire Hookshot, and verify Time remains the active
   instrument in candidate (Fairy in control). Native era change and cinematic must finish with control returned.
4. Go to the adult Windmill and use the ocarina for the first Song of Storms lesson. Candidate already owns
   Storms but must still receive the first native lesson and return control; main learns Storms normally.
   Talk again: ordinary post-lesson dialogue, not a repeated first lesson. Save/Continue once if anything differs.

**Pass evidence:** preserve each launcher's `user-*/longshot_log.txt`; changed resource load lines must show
`mods: <file> <- <packet path>` for GameData, `SetPouchAndStatusForGameStart` and the candidate Windmill flow
when exercised. Record inventory/heart/balance, lesson results, scene handoffs and adult transition observations.
No gameplay result or runtime-load proof is claimed by this staged packet alone.
