# Tracker auto checks: maintainer play checklist

Played acceptance for `gift_rules.toml` `track` entries (spec `plans/tracker-auto-checks.md` D2, 7.1, 7.2).
Every entry ships `accepted = false` (provisional: the tracker reads it, but keeps **Mark done** and the player's
marks). A maintainer switches one to `accepted = true`, with `played_by = "<who>, <build>, <date>"`, only from a run
recorded here, never from the marks oracle alone (7.2). The static evidence for each row is
`plans/tracker-auto-checks-audit.md`. Agents do not start the game or write to a game folder (AGENTS rule 3).

## Setup (once per run)

1. Generate a seed with this Clawshot version (the tracker reads track flags only for seeds whose `generator` is the
   installed version, D8) and Gift shuffle on, so the gifts below give shuffled items.
2. Play it through the runtime (Longshot, or Hookshot). Confirm the seed loaded: the runtime log shows
   `mods: <file> <- <path>` for the seed's files (rule 3). Note the runtime and its build.
3. Open the Tracker tab on the seed and its save folder. Keep it on the newest slot (the game writes each save to the
   next slot of the folder, so marks and reads follow the folder).

## For each row

- **Before**: save in game just before the gift (at the NPC, before the minigame or cutscene). Run
  `python -m clawshot.tracker.audit <seed folder>` (newest slot; `--slot N` for another). Expect the row's field
  `=false`, `-> not collected`, and in the Tracker tab the check open (`—`, in-logic styling) with **Mark done**
  offered. An `absent` field means the save is from another game build: stop and note it.
- **Grant**: get the gift once, in the normal way, and save.
- **After**: run the audit again. Expect the field `=true`, `-> collected`, and in the Tracker tab the check `✓`
  with its reward shown even in spoiler-free mode (4.1), and no **Mark done**. With a mark set before, the audit
  says `agree` and the mark is gone after the tracker's next read.
- **Also, where it applies**: a repeat of the gift (talk again, replay the minigame) leaves the field true and gives
  the native repeat prize. For a cutscene row (`HavePlayedEvent.*`), skip the cutscene with the game's skip button
  on a second save made before it and confirm the field still turns true with the item given; for Sheik and the
  songs also try the seed's owl skips and fast start where they pass the cutscene (audit note 6).
- **Record**: the row's result, who, the runtime and its build, the date. A pass lets a maintainer set that entry to
  `accepted = true` with `played_by`; a failure moves the gift to the spec's "Stays manual" list with what was seen.

| Gift | Field the save holds | What to do in game | Field before -> after |
|---|---|---|---|
| DMT Biggoron | `Step_SubEvent_GetSwordBigGoron` == `Complete` | Biggoron's Receipt Reward: Death Mountain summit (adult): after the eye-drop wait (about three days), show Biggoron his receipt | false -> true |
| Deku Theater Mask of Truth | `LostWood_ScrubForestStage_TrueMaskEventLaunched` | Deku Theater Mask of Truth: Lost Woods Forest Stage, the hole at the back of the Business Scrub meadow (child): wear the Mask of Truth on stage | false -> true |
| Deku Theater Skull Mask | `LostWood_ScrubForestStage_SkullMaskEventLaunched` | Deku Theater Skull Mask: Lost Woods Forest Stage, the hole at the back of the Business Scrub meadow (child): wear the Skull Mask on stage | false -> true |
| GC Darunias Joy | `HavePlayedEvent.Dm_Goron_0030` | Darunia's Dance: Goron City, Darunia's chamber on the bottom floor, its door opened with Zelda's Lullaby (child): play Saria's Song for Darunia | false -> true |
| GC Rolling Goron as Child | `GoronCity_GetBombBag_fromGoron006` | Rolling Goron (Child): Goron City (child, Bomb Bag): blow up the Goron who rolls endlessly round the ring tunnel by the challenge sign | false -> true |
| GF HBA 1000 Points | `MiniGame_HorsebackArchery_GotaHeart` | Horseback Archery 750 Points: Gerudo Fortress horseback archery range by the Proving Grounds sign (adult, on Epona): score 750 points in one round, not the N64's 1,000 | false -> true |
| GF HBA 1500 Points | `MiniGame_HorseBackArchery_Get_Quiver` | Horseback Archery 1400 Points: Gerudo Fortress horseback archery range by the Proving Grounds sign (adult, on Epona): score 1,400 points in one round, not the N64's 1,500 | false -> true |
| Graveyard Dampe Gravedigging Tour | `GraveYard_DiggingHoleTour_Drop_HeartPiece` | Graveyard: Dampe Digging Reward: As child at night after meeting Zelda, lead Dampe to the graveyard's digging spots and pay for digs until the heart-prize result. The temporary heart prop is presentation; the event gives the shuffled reward once. | false -> true |
| HC Zeldas Letter | `HavePlayedEvent.Dm_HrlCastle_0050` | Zelda in the Castle Courtyard: Hyrule Castle courtyard (child): sneak past the guards and talk to Zelda at the window | false -> true |
| HF Ocarina of Time Item | `HavePlayedEvent.Dm_MelodyGet_Time` | Ocarina in the Castle Moat: Hyrule Field at the Castle Town drawbridge (child, after meeting Zelda and Impa at the castle and completing the three Spiritual Stones): approach from the field for Zelda's escape, then pick the glint out of the moat | false -> true |
| Kak 10 Gold Skulltula Reward | `KakarikoVillage_GatheringTokenGold_GetReward10` | House of Skulltula 10 Tokens: Kakariko Village, House of Skulltula (cobwebbed house with the blue door): show the cursed family 10 Gold Skulltula tokens | false -> true |
| Kak 20 Gold Skulltula Reward | `KakarikoVillage_GatheringTokenGold_GetReward20` | House of Skulltula 20 Tokens: Kakariko Village, House of Skulltula: show the cursed family 20 tokens | false -> true |
| Kak 30 Gold Skulltula Reward | `KakarikoVillage_GatheringTokenGold_GetReward30` | House of Skulltula 30 Tokens: Kakariko Village, House of Skulltula: show the cursed family 30 tokens | false -> true |
| Kak 40 Gold Skulltula Reward | `KakarikoVillage_GatheringTokenGold_GetReward40` | House of Skulltula 40 Tokens: Kakariko Village, House of Skulltula: show the cursed family 40 tokens | false -> true |
| Kak 50 Gold Skulltula Reward | `KakarikoVillage_GatheringTokenGold_GetReward50` | House of Skulltula 50 Tokens: Kakariko Village, House of Skulltula: show the cursed family 50 tokens | false -> true |
| Kak Anju as Child | `MiniGame_CatchCucco_IsCompleted` | Cucco Lady's Runaway Cuccos: Kakariko Village, the Cucco Lady's pen (child): bring back all 7 runaway Cuccos | false -> true |
| Kak Man on Roof | `Npc_Hylia_001_IsGetHeartPiece` | Man on the Kakariko Roof: Kakariko Village (adult): from the Potion Shop's back exit, Hookshot to the roof with the seated man and talk to him. | false -> true |
| Kak Shooting Gallery Reward | `MiniGame_HitTarget_Kakariko_Get_Quiver` | Kakariko Archery Gallery: Kakariko Village Shooting Gallery (adult, Fairy Bow): break all 10 targets in one 30-Rupee round | false -> true |
| LH Adult Fishing | `MiniGame_Fishing_GetGoldScale` | Fishing Pond Adult Prize: Lake Hylia Fishing Pond (adult): rent a rod, catch a prize-sized fish with the normal lure and show it to the pond keeper; guides disagree on the exact length threshold. | false -> true |
| LH Child Fishing | `MiniGame_Fishing_GetHeartPiece` | Fishing Pond Child Prize: Lake Hylia Fishing Pond (child): rent a rod, catch a prize-sized fish with the normal lure and show it to the pond keeper. | false -> true |
| LH Lab Dive | `Npc_Hylia_045_HasDived` | Lakeside Lab Deep Dive: Lake Hylia, Lakeside Laboratory's indoor tank (Golden Scale, no Iron Boots): dive to the grate at the bottom and surface for the scientist | false -> true |
| LLR Talons Chickens | `IsClear_Minigame_FindOutCucco` | Talon's Cucco Game: Lon Lon Ranch house (child, after waking Talon at the castle): pick out his 3 special Cuccos within 30 seconds | false -> true |
| LW Gift from Saria | `HavePlayedEvent.Dm_Kokiri_0155` | Saria's Farewell Gift: Kokiri Forest exit toward Hyrule Field (child, after the Great Deku Tree): Saria stops Link on his way out of the forest. | false -> true |
| LW Ocarina Memory Game | `Minigame_SkullKidSession_IsGetHeartPiece` | Skull Kids' Ocarina Game: Lost Woods (child): from the Kokiri entrance follow the music right and drop to the lower stumps; the third round of the Skull Kids' melody game (earlier rounds pay rupees) | false -> true |
| LW Skull Kid | `Npc_SkullKid_Child_IsGetHeartPiece` | Skull Kid's Stump Song: Lost Woods (child): first left from the Kokiri entrance, the grove by the stream; play Saria's Song to the Skull Kid on the tall stump | false -> true |
| LW Target in Woods | `LostWood_HitTargetOfDekuScrub_FirstClear` | Lost Woods Slingshot Target: Lost Woods (child): right of the Kokiri entrance, stand on the stump and hit the target's centre three times; a Deku Scrub pays out | false -> true |
| Market Bombchu Bowling First Prize | `MiniGame_BombchuBowling_ClearFirstTime` | Bombchu Bowling First Prize: Child Market, Bombchu Bowling after Dodongo's Cavern: with Gift shuffle, the first win. Unshuffled, the native bomb-bag upgrade is the second win. | false -> true |
| Market Bombchu Bowling Second Prize | `MiniGame_BombchuBowling_ClearSecondTime` | Bombchu Bowling Second Prize: Child Market, Bombchu Bowling after Dodongo's Cavern: with Gift shuffle, the second win. Unshuffled, the native heart prize is the third win. | false -> true |
| Market Lost Dog | `Step_SubEvent_FindRichard` == `Complete` | Richard the Lost Dog: Hyrule Castle Town back alley (child, night): find Richard, the white dog, and lead him back to his owner. | false -> true |
| Market Potion Shop Bottle | `Npc_Hylia_020_Shop_Item_Bottle_Present` | Market: Potion Shop Bottle Tutorial: As child, enter the Market Potion Shop by day and accept the owner's bottle tutorial. Vanilla gives an empty bottle before the bug-catching lesson; a shuffled reward ends the bottle-only lesson after the gift. | false -> true |
| Market Shooting Gallery Reward | `MiniGame_HitTarget_HrlCity_Get_BulletBag` | Market Slingshot Gallery: Hyrule Castle Town Market (child, day), Shooting Gallery across the plaza from the Happy Mask Shop: hit all 10 targets with the Fairy Slingshot | false -> true |
| Sheik at Colossus | `HavePlayedEvent.Dm_MelodyGet_Spilit` | Sheik at the Desert Colossus: Evil Desert Colossus (adult, first arrival): Sheik near the Spirit Temple entrance | false -> true |
| Sheik at Temple | `HavePlayedEvent.Dm_MelodyGet_Shine` | Sheik in the Temple of Time: Temple of Time (adult, after the Forest Temple): Sheik's harp lesson by the pedestal | false -> true |
| Sheik in Forest | `HavePlayedEvent.Dm_MelodyGet_Forest` | Sheik in the Sacred Grove: Sacred Grove (adult, past the Moblins): Sheik at the warp platform before the Forest Temple steps | false -> true |
| Sheik in Ice Cavern | `HavePlayedEvent.Dm_MelodyGet_Water` | Sheik in the Ice Cavern (1F): Ice Cavern, the Iron Boots chest room past the White Wolfos (adult): Sheik appears once the chest is opened | false -> true |
| Sheik in Kakariko | `HavePlayedEvent.Dm_MelodyGet_Shadow` | Sheik in Burning Kakariko: Kakariko Village (adult, after the Water Temple per the guides): Sheik's lesson on the village bridge after the fire and shadow cutscene | false -> true |
| Song from Impa | `HavePlayedEvent.Dm_MelodyGet_Zelda` | Impa's Courtyard Song: Hyrule Castle courtyard (child): talk to Impa after Zelda's letter and repeat her melody | false -> true |
| Song from Malon | `HavePlayedEvent.Dm_MelodyGet_Epona` | Malon's Paddock Song: Lon Lon Ranch paddock (child, day, after waking Talon): talk to Malon singing to young Epona and play her song back | false -> true |
| Song from Ocarina of Time | `HavePlayedEvent.Dm_MelodyGet_Time` | Zelda's Moat Lesson: Hyrule Field at the Castle Town drawbridge (child, after meeting Zelda and Impa at the castle and completing the three Spiritual Stones): Zelda's lesson follows taking the Ocarina from the moat | false -> true |
| Song from Royal Familys Tomb | `RoyalFamilyTomb_MelodyGet_Clear` | Royal Family's Tomb Tablet: Kakariko Graveyard (child): open the Royal Family's Tomb at the back with Zelda's Lullaby and read the tablet in the last chamber. | false -> true |
| Song from Saria | `HavePlayedEvent.Dm_MelodyGet_Saria` | Saria in the Sacred Grove: Sacred Grove (Sacred Forest Meadow), the clearing at the top of the stairs (child, after meeting Zelda): Saria on her stump | false -> true |
| ToT Light Arrows Cutscene | `HavePlayedEvent.Dm_TimeTemple_0130` | Zelda Revealed in the Temple: Temple of Time (adult): return once the other sages are awake (guides: all five adult temples) and Sheik reveals herself as Zelda | false -> true |
| ZD Diving Minigame | `MiniGame_Diving_Cleared` | Zora Diving Game: Zora's Domain (child): take the passage left of King Zora's throne room to the Zora above the waterfall and win his diving game. | false -> true |
| ZD King Zora Thawed | `SageOfWater_KingZora_adult_Talk_Event198` | King Zora Thawed: Zora's Domain throne room, frozen (adult): melt King Zora's ice with Blue Fire | false -> true |
| ZR Frogs Eponas Song | `MiniGame_FrogTenors_EponaSong` | Zora's River Frogs: Epona's Song: Zora's River frog stumps (child): play Epona's Song for the first time | false -> true |
| ZR Frogs Ocarina Game | `MiniGame_FrogTenors_InsectRepellent` | Zora's River Frog Chorus: Zora's River, the frogs' stumps in the alcove partway up the river (child): after growing the frogs with songs, win their bug-note game | false -> true |
| ZR Frogs Sarias Song | `MiniGame_FrogTenors_SariaSong` | Zora's River Frogs: Saria's Song: Zora's River frog stumps (child): play Saria's Song for the first time | false -> true |
| ZR Frogs Song of Time | `MiniGame_FrogTenors_TimeSong` | Zora's River Frogs: Song of Time: Zora's River frog stumps (child): play the Song of Time for the first time | false -> true |
| ZR Frogs Suns Song | `MiniGame_FrogTenors_SunSong` | Zora's River Frogs: Sun's Song: Zora's River frog stumps (child): play the Sun's Song for the first time | false -> true |
| ZR Frogs Zeldas Lullaby | `MiniGame_FrogTenors_ZeldaLullaby` | Zora's River Frogs: Zelda's Lullaby: Zora's River frog stumps (child): play Zelda's Lullaby for the first time | false -> true |
| ZR Frogs in the Rain | `MiniGame_FrogTenors_StormSong` | Zora's River Frogs: Song of Storms: Zora's River frog stumps (child): play the Song of Storms for the first time | false -> true |

## Results

| Gift | Result | Who, runtime build, date |
|---|---|---|
