# Tracker auto checks: track-flag audit (D2)

Evidence for `plans/tracker-auto-checks.md` decision D2 and plan task 4: for every candidate gift, the
event that sets its native flag, and whether it is set on exactly the paths that run the check's grant. Only flag,
flow and event names are recorded here, never game data (AGENTS rule 1). `gift_rules.toml` `track` sources point
to this file.

**Who, build, date.** Claude (agent, for BBender), static read of a 1.1.1 romfs dump (`EventFlowFileEntry`
versions as the game loads them), 2026-11-22. Not played: every entry ships `accepted = false` until a maintainer
run (`plans/tracker-auto-checks-play.md`, spec 7.1/7.2).

**Method.** A read-only research script outside the repository (no GPL code; it uses this repository's `evfl`
reader, `census.gifts.scan_gifts`, `gifts.check_steps` and `gifts.plan`/`patch_flowchart`) walks each grant flow
from every entry the game or another flow can start (an `EventSetting` row's entry, a cross-flow call, or an entry
no local call uses). Walks expand local sub-flow calls with a call stack, run all branches of a Fork before its
Join, and follow a Bool query only on the branch that agrees with what the walk already set or read (case 0 is
true). A **pass** needs both:

- no walk runs a grant step (any of the check's census steps) and ends without the flag's writer, and
- no walk runs the writer while the flag is still unset and ends without a grant step;

and no flow other than the grant flow writes the flag (reads are fine). The same walk runs over the vanilla flows
and over the flows patched for the check (`gifts.plan` with a shuffled item, every candidate at once): column
"vanilla/patched". Quest entries test `EventExecuteProgressChallengeStep` with that `ChallengeName` and
`StepName`. For `played` entries the flag is the engine's `HavePlayedEvent.<row>`, written when the event ends
(`plans/03-game-data.md`, facts list, inference); the test is that the row exists and every walk of the cut entry
that holds the grant reaches it. What engine code (not flows) writes is out of reach of this audit; the played
check covers it.

| Gift | Track entry | Grant step(s) | Setting event | vanilla/patched | Result |
|---|---|---|---|---|---|
| LW Skull Kid | bool `Npc_SkullKid_Child_IsGetHeartPiece` | Npc_SkullKid_Child/Event71 | Npc_SkullKid_Child/Event10 | PASS/PASS | pass |
| LW Ocarina Memory Game | bool `Minigame_SkullKidSession_IsGetHeartPiece` | Npc_SkullKid_Child_02/Event24 | Npc_SkullKid_Child_02/Event58 | PASS/PASS | pass |
| LW Target in Woods | bool `LostWood_HitTargetOfDekuScrub_FirstClear` | Dm_LostWood_0040/Event17, Dm_LostWood_0040/Event30 | Dm_LostWood_0040/Event84 | PASS/PASS | pass |
| Deku Theater Mask of Truth | bool `LostWood_ScrubForestStage_TrueMaskEventLaunched` | LostWood_ScrubForestStageElder_TrueMaskFirst/Event2, LostWood_ScrubForestStageElder_TrueMaskFirst/Event31 | LostWood_ScrubForestStageElder_TrueMaskFirst/Event25 | PASS/PASS | pass |
| Deku Theater Skull Mask | bool `LostWood_ScrubForestStage_SkullMaskEventLaunched` | LostWood_ScrubForestStageElder_SkullMaskFirst/Event29, LostWood_ScrubForestStageElder_SkullMaskFirst/Event32 | LostWood_ScrubForestStageElder_SkullMaskFirst/Event0 | PASS/PASS | pass |
| GC Rolling Goron as Child | bool `GoronCity_GetBombBag_fromGoron006` | Npc_Goron_006_Child/Event58, Npc_Goron_006_Child/Event92 | Npc_Goron_006_Child/Event1 | PASS/PASS | pass |
| GC Rolling Goron as Adult | bool `SageOfFire_Step02_DaruniaJr_FirstTalked` | SageOfFire/Event18 | SageOfFire/Event251, SageOfFire/Event144 | CHECK/CHECK | fail (see below) |
| GF HBA 1000 Points | bool `MiniGame_HorsebackArchery_GotaHeart` | Minigame_HorsebackArchery/Event322 | Minigame_HorsebackArchery/Event124 | PASS/PASS | pass |
| GF HBA 1500 Points | bool `MiniGame_HorseBackArchery_Get_Quiver` | Minigame_HorsebackArchery/Event319, Minigame_HorsebackArchery/Event320 | Minigame_HorsebackArchery/Event115 | PASS/PASS | pass |
| Kak 10 Gold Skulltula Reward | bool `KakarikoVillage_GatheringTokenGold_GetReward10` | GatheringTokenGold/Event398 | GatheringTokenGold/Event199 | PASS/PASS | pass |
| Kak 20 Gold Skulltula Reward | bool `KakarikoVillage_GatheringTokenGold_GetReward20` | GatheringTokenGold/Event75 | GatheringTokenGold/Event192 | PASS/PASS | pass |
| Kak 30 Gold Skulltula Reward | bool `KakarikoVillage_GatheringTokenGold_GetReward30` | GatheringTokenGold/Event194 | GatheringTokenGold/Event197 | PASS/PASS | pass |
| Kak 40 Gold Skulltula Reward | bool `KakarikoVillage_GatheringTokenGold_GetReward40` | GatheringTokenGold/Event200 | GatheringTokenGold/Event216 | PASS/PASS | pass |
| Kak 50 Gold Skulltula Reward | bool `KakarikoVillage_GatheringTokenGold_GetReward50` | GatheringTokenGold/Event219 | GatheringTokenGold/Event213 | PASS/PASS | pass |
| Kak Anju as Child | bool `MiniGame_CatchCucco_IsCompleted` | Minigame_CatchCucco/Event181 | Minigame_CatchCucco/Event143 | PASS/PASS | pass: the other set re-sets an already set flag on the repeat-play path (note 1) |
| Kak Anju as Adult | bool `GetSwordBigGoron_IsAfterFirstTalk_Npc_Hylia_049_Adult` | Npc_Hylia_049_Adult/Event264 | Npc_Hylia_049_Adult/Event41 | CHECK/CHECK | fail (see below) |
| Kak Man on Roof | bool `Npc_Hylia_001_IsGetHeartPiece` | Npc_Hylia_001_Adult/Event4 | Npc_Hylia_001_Adult/Event11 | PASS/PASS | pass |
| Kak Shooting Gallery Reward | bool `MiniGame_HitTarget_Kakariko_Get_Quiver` | MiniGame_HitTarget/Event242, MiniGame_HitTarget/Event381 | MiniGame_HitTarget/Event185 | PASS/PASS | pass |
| LH Child Fishing | bool `MiniGame_Fishing_GetHeartPiece` | MiniGame_Fishing/Event573, MiniGame_Fishing/Event821 | MiniGame_Fishing/Event572, MiniGame_Fishing/Event848 | PASS/PASS | pass |
| LH Adult Fishing | bool `MiniGame_Fishing_GetGoldScale` | MiniGame_Fishing/Event579, MiniGame_Fishing/Event822 | MiniGame_Fishing/Event578, MiniGame_Fishing/Event850 | PASS/PASS | pass |
| LH Lab Dive | bool `Npc_Hylia_045_HasDived` | Npc_Hylia_045_Child/Event113 | Npc_Hylia_045_Child/Event83 | PASS/PASS | pass |
| LLR Talons Chickens | bool `IsClear_Minigame_FindOutCucco` | Minigame_FindOutCucco/Event23 | Minigame_FindOutCucco/Event89 | PASS/PASS | pass |
| Market Bombchu Bowling First Prize | bool `MiniGame_BombchuBowling_ClearFirstTime` | MiniGame_BombchuBowling/Event304, MiniGame_BombchuBowling/Event306 | MiniGame_BombchuBowling/Event89 | CHECK/CHECK | pass by invariant (note 2) |
| Market Bombchu Bowling Second Prize | bool `MiniGame_BombchuBowling_ClearSecondTime` | MiniGame_BombchuBowling/Event143 | MiniGame_BombchuBowling/Event90 | CHECK/PASS | pass on the patched flow (patch reorders prizes; note 2) |
| Market Shooting Gallery Reward | bool `MiniGame_HitTarget_HrlCity_Get_BulletBag` | MiniGame_HitTarget/Event378, MiniGame_HitTarget/Event241 | MiniGame_HitTarget/Event72 | PASS/PASS | pass |
| Market Potion Shop Bottle | bool `Npc_Hylia_020_Shop_Item_Bottle_Present` | Npc_Hylia_020_Shop_Child/Event171 | Npc_Hylia_020_Shop_Child/Event14 | PASS/PASS | pass |
| Graveyard Dampe Gravedigging Tour | bool `GraveYard_DiggingHoleTour_Drop_HeartPiece` | Npc_Hylia_Dampe_001/Event628 | Npc_Hylia_Dampe_001/Event357 | PASS/PASS | pass |
| Song from Royal Familys Tomb | bool `RoyalFamilyTomb_MelodyGet_Clear` | Dm_MelodyGet_Sun_03/Event34 | GimmickFlow_RoyalFamilyTomb/Event28 | -/- | pass across flows (note 4) |
| ZD Diving Minigame | bool `MiniGame_Diving_Cleared` | MiniGame_Diving/Event21 | MiniGame_Diving/Event64 | PASS/PASS | pass |
| ZD King Zora Thawed | bool `SageOfWater_KingZora_adult_Talk_Event198` | SageOfWater/Event242 | SageOfWater/Event69 | PASS/PASS | pass |
| ZR Frogs Ocarina Game | bool `MiniGame_FrogTenors_InsectRepellent` | MiniGame_FrogTenors/Event161, MiniGame_FrogTenors/Event75 | MiniGame_FrogTenors/Event151 | CHECK/CHECK | pass: the unflagged walk is the minigame's Failed branch, no item (note 3) |
| ZR Frogs in the Rain | bool `MiniGame_FrogTenors_StormSong` | MiniGame_FrogTenors/Event384 | MiniGame_FrogTenors/Event112 | PASS/PASS | pass |
| ZR Frogs Zeldas Lullaby | bool `MiniGame_FrogTenors_ZeldaLullaby` | MiniGame_FrogTenors/Event172 | MiniGame_FrogTenors:TeachNewMusic/Event164 (argument) | -/- | pass (note 5) |
| ZR Frogs Eponas Song | bool `MiniGame_FrogTenors_EponaSong` | MiniGame_FrogTenors/Event220 | MiniGame_FrogTenors:TeachNewMusic/Event164 (argument) | -/- | pass (note 5) |
| ZR Frogs Sarias Song | bool `MiniGame_FrogTenors_SariaSong` | MiniGame_FrogTenors/Event221 | MiniGame_FrogTenors:TeachNewMusic/Event164 (argument) | -/- | pass (note 5) |
| ZR Frogs Suns Song | bool `MiniGame_FrogTenors_SunSong` | MiniGame_FrogTenors/Event222 | MiniGame_FrogTenors:TeachNewMusic/Event164 (argument) | -/- | pass (note 5) |
| ZR Frogs Song of Time | bool `MiniGame_FrogTenors_TimeSong` | MiniGame_FrogTenors/Event223 | MiniGame_FrogTenors:TeachNewMusic/Event164 (argument) | -/- | pass (note 5) |
| LW Gift from Saria | played `Dm_Kokiri_0155` | Dm_Kokiri_0155/Event68 | cut [; started by Goto_HyruleCastle/Event44 | PASS/PASS | pass (note 6) |
| Song from Saria | played `Dm_MelodyGet_Saria` | Dm_MelodyGet_Saria/Event109 | cut [; started by SacredForestMeadow/Event0 | PASS/PASS | pass (note 6) |
| Song from Malon | played `Dm_MelodyGet_Epona` | Dm_MelodyGet_Epona/Event11 | cut [; started by SubEvent_GetEponaSong/Event1 | PASS/PASS | pass (note 6) |
| Song from Impa | played `Dm_MelodyGet_Zelda` | Dm_MelodyGet_Zelda/Event111 | cut [; started by DoorOfTime/Event21 | PASS/PASS | pass (note 6) |
| Sheik in Forest | played `Dm_MelodyGet_Forest` | Dm_MelodyGet_Forest/Event22 | cut [; started by SageOfForest/Event13 | PASS/PASS | pass (note 6) |
| Sheik in Kakariko | played `Dm_MelodyGet_Shadow` | Dm_MelodyGet_Shadow/Event21 | cut [; started by Dm_SY_BancChangeArrive/Event68 | PASS/PASS | pass (note 6) |
| Sheik in Ice Cavern | played `Dm_MelodyGet_Water` | Dm_MelodyGet_Water/Event29 | cut [; started by SageOfWater/Event281, SageOfWater/Event283 | PASS/PASS | pass (note 6) |
| Sheik at Colossus | played `Dm_MelodyGet_Spilit` | Dm_MelodyGet_Spilit/Event17 | cut [; started by a logic module | PASS/PASS | pass (note 6) |
| Sheik at Temple | played `Dm_MelodyGet_Shine` | Dm_MelodyGet_Shine/Event53 | cut [; started by AllSage/Event37 | PASS/PASS | pass (note 6) |
| HF Ocarina of Time Item | played `Dm_MelodyGet_Time` | Dm_MelodyGet_Time/Event70 | cut [; started by DoorOfTime/Event15 | PASS/PASS | pass (note 6) |
| Song from Ocarina of Time | played `Dm_MelodyGet_Time` | Dm_MelodyGet_Time/Event4 | cut [; started by DoorOfTime/Event15 | PASS/PASS | pass (note 6) |
| ToT Light Arrows Cutscene | played `Dm_TimeTemple_0130` | Dm_TimeTemple_0130/Event85 | cut [; started by AllSage/Event17 | PASS/PASS | pass (note 6) |
| HC Zeldas Letter | played `Dm_HrlCastle_0050` | Dm_HrlCastle_0050/Event59 | cut [; started by Goto_HyruleCastle/Event31 | PASS/PASS | pass (note 6) |
| GC Darunias Joy | played `Dm_Goron_0030` | Dm_Goron_0030/Event127 | cut [; started by Get_StoneOfFire/Event31 | PASS/PASS | pass (note 6) |
| Market Lost Dog | quest == Complete `SubEvent_FindRichard` | SubEvent_FindRichard/Event16 | SubEvent_FindRichard/Event32 | PASS/PASS | pass |
| Market 10 Big Poes | quest == Complete `SubEvent_GhostShop` | Npc_Hylia_048_BottleShop/Event329 | Npc_Hylia_048_BottleShop/Event48 | CHECK/CHECK | fail (see below) |
| DMT Biggoron | quest == Complete `SubEvent_GetSwordBigGoron` | Npc_Goron_Biggoron_Adult/Event123 | Npc_Goron_Biggoron_Adult/Event89 | PASS/PASS | pass |
| Kak 100 Gold Skulltula Reward | quest == Complete `GatheringTokenGold` | GatheringTokenGold/Event215 | GatheringTokenGold/Event232 | CHECK/CHECK | fail (see below) |
| HC Malon Egg | quest == Complete `Goto_HyruleCastle` | Goto_HyruleCastle/Event35 | Goto_HyruleCastle/Event30 | CHECK/CHECK | fail (see below) |

**Notes.**

1. *Kak Anju as Child.* `Minigame_CatchCucco/Event46` reads `MiniGame_CatchCucco_IsCompleted`; when true the flow
   gives the repeat red rupee and later passes Event143 again, which sets the already set flag. No walk sets it
   from unset without the bottle grant Event181.
2. *Bombchu Bowling.* The patch reorders the prizes (`gifts._bowling_order`): first win -> first prize, second ->
   second prize. `MiniGameClearCount` sets `ClearFirstTime` (Event89) when it is unset, else `ClearSecondTime`
   (Event90). The only first-prize walk without Event89 needs `ClearSecondTime` true while `ClearFirstTime` is false;
   Event90 is the only writer of `ClearSecondTime` and runs only after Event88 reads `ClearFirstTime` true, and
   nothing resets `ClearFirstTime`, so that walk cannot happen. The spec's worry about Second Prize: the patch's
   added `ClearThirdTime` write (heart marker) does not touch `ClearSecondTime`. Vanilla walks are not
   representative here (vanilla prizes are not tied to the win count).
3. *ZR Frogs Ocarina Game.* The census steps Event161/Event75 call `MushiToriGame` with the reward as an argument;
   the walk past them without Event151 is the `Failed` branch (`EventQueryIsSuccessFrog`), which hands over nothing.
4. *Song from Royal Familys Tomb.* The flag is written in `GimmickFlow_RoyalFamilyTomb/Event28`, after
   `Event15` calls `CheckStone_To_MelodyGet_Sun`; every walk of that entry reaches `Event57`, the transition to
   `Dm_MelodyGet_Sun_03`, the only flow with the song's grant (the other `Dm_MelodyGet_Sun_*` variants have no flow
   file). The `no_ocarina` scene handoff keeps this caller (`scene_handoffs.toml` scene `sun`). Event28 is the only
   writer. Spec background: one seed reads it true with no mark, likely a mark never made.
5. *Frog songs.* Each step calls `MiniGame_FrogTenors:TeachNewMusic` with `GameDataName = <flag>`; inside,
   Event167 reads the flag (true: talk and leave, no reward), and on false the reward runs, then Event164 sets the
   argument flag on every path. No flow names these flags elsewhere. The patch rewrites this reward graph
   (`gifts._frog_song`); the patched-flow dump test (spec 5.1) re-checks it.
6. *Cutscene gifts and skips (spec 4.2).* `HavePlayedEvent.<row>` is written when the event ends. Patch-side skips
   keep it: the `no_ocarina` and `skip_saria_farewell` scene handoffs write `HavePlayedEvent.<history>` after the
   grants (`patch/scene_handoff.py`, histories after grants; `scene_handoffs.toml` lists `Dm_MelodyGet_Forest` ...
   `Dm_Kokiri_0150`/`_0155`); the song `skip` entries take out `Dm_SY_Ocarina` play-along steps, not the cutscene.
   Not shown statically: that a player's in-game cutscene skip still runs the grant's cut and writes the flag, and
   when an owl skip or `fast_start` removes a cutscene. The play checklist covers both. HC Zeldas Letter
   (`Dm_HrlCastle_0050`) and GC Darunias Joy (`Dm_Goron_0030`) are the flows the spec left to find. HF Ocarina of
   Time Item and Song from Ocarina of Time share `Dm_MelodyGet_Time` (grants in `EntryPoint0` and `C10`); each check
   carries its own entry.

**Failed: stay manual (spec D7).**

| Gift | Candidate | Why |
|---|---|---|
| GC Rolling Goron as Adult | `SageOfFire_Step02_DaruniaJr_FirstTalked` | First-talk flag: `SageOfFire/Event251` sets it on the crying-talk walk (`Event130`, `Npc_Goron_DaruniaJr_IsCrying`) that ends without the grant Event18. |
| Kak Anju as Adult | `GetSwordBigGoron_IsAfterFirstTalk_Npc_Hylia_049_Adult` | `Npc_Hylia_049_Adult/Event41` sets it on a first-talk walk without the grant Event264, and the grant also runs on a walk without it. |
| Market 10 Big Poes | quest `SubEvent_GhostShop` == `Complete` | `Npc_Hylia_048_BottleShop/Event48` follows the Gold Rupee handover Event330 (`Sell_AfterCheckingLoseMoney_900`); the bottle grant Event329 can end without it. |
| Kak 100 Gold Skulltula Reward | quest `GatheringTokenGold` == `Complete` | `GatheringTokenGold/Event232` is set on a walk without the grant Event215 (`TakenReward_Common_Event_200Rupee`), and Event215 runs on walks without it. |
| HC Malon Egg | quest `Goto_HyruleCastle`, steps found in the grant flow | Step03 (`Event46`) passes the path test, but the quest moves on (Step03_02, Complete), so an "equals Step03" read (D6) would turn false again after the egg; Complete, Step02, Step02_01 and Step03_02 fail the path test. An "at or past a step" read is a product call (spec open questions). |
