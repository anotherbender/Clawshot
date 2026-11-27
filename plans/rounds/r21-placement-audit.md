# Round 21: placement audit (cs21j)

Research track, read-only. Branch `r21/placement-audit` from main `aeba6df`. No product code changed, so no gates
ran. Kareem's ask (2026-11-23): "I would ideally like everything to be able to be shuffled anywhere ... having songs as
floor pickups (replacing Heart Pieces, Rupees, Recovery Hearts etc) would be great. We can examine our current
distribution and limitations to see if they were tested or assumed."

Evidence classes used below:

- **PLAYED**: an in-game check, with who, the runtime and the date.
- **DUMP**: read from the game's files.
- **INHERITED**: taken from OoT Randomizer's or Ship of Harkinian's public docs, not checked by us.
- **ASSUMED**: no record found.
- **STALE**: the written reason no longer holds.

"Policy" marks a product call rather than a game fact.

## How this was checked

- Code read at `aeba6df`. Every limit below is a branch of `generate/fill.py:384-428` (`allowed()`), or a setting
  that feeds it.
- Three read-only scout passes traced the round files, `03-game-data.md`, `decisions.md` and `playtest/answers.md`.
  I spot-checked every citation I use below against the file.
- Research scripts are in `E:/OOTRemake/work/r21-placement-audit/`. They read the dump and write nothing to it.
  - `types.py`: location types in the world.
  - `matrix.py`: the real seed setup chain (`gifts.seed_setup` then `make_seed`, stopped before the fill), then
    `allowed()` for every pool item at every shuffled location.
  - `kinds.py`: lists each gift, scrub, song and floor location.
  - `icecheck.py`: six fill-only seeds.
- One seed was written to scratch at `E:/OOTRemake/work/r21-placement-audit/ice-seed1`:
  `--shuffle Chest Gift --songs anywhere`, seed 1. Neither game was running at any point (tasklist checked).
- PR #41 (`refs/review/pr-41`, head `49fb1b2`) was read from git only: `plans/song-get-effects.md`,
  `patch/songs.py` and the `patch/__init__.py` hook. Nothing was built from it.
- Not done:
  - No pytest, sweep or seed batch.
  - No game started, nothing staged for Kareem.
  - No OoTR or SoH code opened. Their facts come from `E:/OOTRemake/work/r20-planning/feature-compare.md`.

## 1. Location kinds today

Counts come from the world at `aeba6df`. "Live" means it has a remake item and is neither `n64_only` nor
`keep_vanilla`. Some kinds keep further rows vanilla when their setting is applied at seed time; those counts are
from `matrix.py`.

| Kind (world type) | Live / shuffled | Setting (default) | Status | Why the rest stay vanilla (class) |
|---|---|---|---|---|
| Chests (`Chest`) | 178 of 217 | `Chest` (on) | location | 10 Treasure Chest Game boxes plus its reward (D17, policy). Six trap chests are item-less (D10, DUMP). Copies that are noncanonical or missable (DUMP, Kareem 2026-11-17). The sign-puzzle failure chest (Kareem 2026-11-09). |
| NPC gifts (`NPC`) | 37 of 75 | `Gift` (off) | location | Trade chain and child trade cell (R13, D31: PLAYED). Gerudo card (D39: PLAYED). Merchants and expert galleries "await Kareem's result" (ASSUMED, pending since round 8 or 10); the three merchants are since admitted (round 22, `r22-merchants.md`). Others "not changeable yet" (`patch/gift_rules.toml`; DUMP, no movable grant step). |
| Cutscene gifts (`Cutscene`) | 8 of 9 | `Gift` | location | Five Great Fairies, Saria's gift, the Light Arrows scene. "Gift from Sages" holds no item. |
| Song lessons (`Song`) | 12 of 12 | `Gift` | location | (none held vanilla) |
| Dungeon rewards (`Boss` becomes `DungeonReward`) | 9 incl. Rauru | `dungeon_rewards` (off) | location | Stay vanilla when off. |
| Shops (`Shop`) | 64 (8 shops x 8 shelves) | `Shop` (off), `shop_slots` | location | Mask shop loans stay (8 `MaskShop` rows, not a choice). |
| Scrubs (`Scrub`, `GrottoScrub`) | 4 one-time sales | `Scrub` (off) | location | 12 repeat vendors are held (`patch/scrubs.py`; DUMP §23). 18 rows are `n64_only` (DUMP). |
| Gold Skulltulas (`GS Token` becomes `Token`) | 100 | `Token` (off, needs Chest) | location | 3 `n64_only`. |
| 100-token reward | 1 (the NPC row above) | `shuffle_100_token_reward` (off) | location, junk only | `nonprogression_only` (policy, issue #12). The lift was PLAYED: Kareem, Longshot 3.0.0, 2026-11-20 (`r19-tokens.md`). |
| Boss hearts (`BossHeart`) | 8 | `BossHeart` (off) | location | (none) |
| Floor Heart Pieces (`Collectable` becomes `Freestanding`) | 14 of 28 | `Freestanding` (off) | location | 7 `n64_only` (DUMP). The other N64 `Collectable` rows are unlinked or are keys (below). |
| Well floor key (`KeyPickup`) | 1 | `dungeon_items` set to `anywhere` or `all_anywhere` | location | Shadow's floor key is held: built, but no natural pre-room save (ASSUMED, `r19-keys.md:109-110`). The Training Ground floor key stays native. |
| Fortress jail keys (`HideoutKeyPickup`) | 4 | `shuffle_hideout_keys` (off) | location | Four torch rows are `n64_only`. |
| Master Sword pedestal (`SwordPedestal`) | 1 | `shuffle_master_sword` (off; needs Chest and free time travel) | location | (none) |
| Loose rupees, recovery hearts, ammo (`Freestanding`) | 0 of 155 | (none) | never | No census kind, and no physical remake-to-logic link per row. Their saved type24/save0 flags exist (DUMP §36). The 155 is OoTR's count (INHERITED). The remake has 112 rupee and 25 heart Hashes (DUMP, `r10-pots.md`). |
| Pots, crates, small crates, flying pots | 0 of 442 | (none) | never | reset88 flags and table-driven drops (DUMP §43). A thrown pot dropped its Piece of Heart out of reach (PLAYED, round 10, `r10-pots.md:284-303`). |
| Beehives, rupee towers, wonder items, silver rupees | 0 of 249 | (none) | never | No census kind (DUMP). Silver rupees use puzzle AI (DUMP §36). |
| Cows | no rows | (none) | never | D11. A shared research Bool persisted (PLAYED 2026-11-21, `r20-cows.md`). A per-cow identity is still missing. |
| Treasure Chest Game boxes and keys, DreamWorld, Gossip Stone fairies | (none) | (none) | never | D17 and D12 (policy). Fairies are logic events from the translator, never locations (`04-world-format.md:574-575`). The two fishing prizes are shuffled NPC rows; the loach prize is held "not changeable yet". |

Unshuffled kinds still keep their own native items. With every kind on, a seed shuffles 431 locations (`matrix.py`
broad recipe, below).

## 2. Where each item can go today

This is the most liberal recipe that validates. Every kind is shuffled, with `songs=anywhere`,
`dungeon_items=all_anywhere`, Fortress keys, Master Sword shuffle, `free_time_travel` and the 100-token lift on.
Numbers are destinations that `allowed()` accepts out of that kind's total (`matrix-broad.json`). Seed screens (D25
bomb packs, tier order) narrow this further per seed.

| Item family | Chest 178 | NPC 37 / Cut 8 / Song 12 | Scrub 4 | Shop 64 | Token 100 | Floor 14 + 8 | Pedestal |
|---|---|---|---|---|---|---|---|
| 12 songs | yes | yes | yes | no | no | no | no |
| Fairy Ocarina | yes | NPC 1, Cut 2, Song 12 (direct and `GetPouchContent` scenes only) | no | no | no | no | no |
| Ocarina of Time | yes | as Fairy | no | no | yes | no | no |
| Majors with a native chest actor (Boomerang, Hammer, both boots, Lens, Mirror Shield, Kokiri Sword, Din's Fire, Ice Arrows) | yes | yes | yes | no | yes | no | yes |
| Gift-only items (Biggoron Sword, Bottle, Milk bottle, Double Defense, Farore's Wind, Nayru's Love, Light Arrows, Stone of Agony, Rupees (200)) | **no** | yes | no | no | yes | no | no |
| Bombchus (20) | no | yes | no | no | no | no | no |
| 8 progressive families | **only** | no | no | no | no | no | no |
| Deku and Hylian Shield | yes | yes | yes | yes (own shelves) | yes | **yes** | yes |
| Heart Container, Piece of Heart | yes | yes | yes | no | yes | **yes** | yes |
| Rupees (20) | yes | yes | yes | no | yes | **yes**, plus both key-source palettes | yes |
| Goron and Zora Tunic | yes | yes | yes | 40 shelves | yes | no | yes |
| Other junk (rupees 1/5/50, nuts, stick, arrows 5, magic jar, Scrub Business Seed) | yes | yes | yes | no | yes | no | yes |
| Bombs (5), Arrows (10), Bombchus (5) | yes (D25) | yes | yes | yes | yes | no | yes |
| 31 `Buy ...` goods | no | no | no | **only** | no | no | no |
| Deku Stick and Nut Capacity | no | no | **only** | no | no | no | no |
| Gold Skulltula Token | yes | no | no | no | yes | no | no |
| Master Sword | **only** | no | no | no | no | no | no |
| Dungeon keys, maps, compasses | in their dungeon's chests (own) or any of 177 chests (released). Well key also on its floor source. **Ice Cavern map and compass also at Sheik in Ice Cavern** (section 6) | | | | | | |
| Fortress jail keys | yes | no | no | no | no | jail sources only | no |
| Stones and medallions (`dungeon_rewards`) | reward slots only, both ways | | | | | | |

With defaults (`songs=song`), Song lessons take only songs and songs go nowhere else (`exclusive_location_types`).

## 3. Every limit and its evidence

`fill.py` lines are at `aeba6df`.

| # | Limit | Code | Class | Evidence | Still holds? |
|---|---|---|---|---|---|
| 1 | Songs only at song lessons by default (`songs=song`). Lessons take only songs. | `data/settings.toml:32`; `patch/gifts.py:1229,1237,1270-1272`; `fill.py:415-419` | Policy (D23, D24) + INHERITED (OoTR's default `shuffle_song_items='song'`) | D23: Storms from a chest, played on chest Fairy Ocarina (Kareem 2026-11-08). D24 keeps "songs on song spots" as the vanilla-like default. | The safety reason is **STALE**; it stands as a product default. Songs seen working off the lessons: chest (Storms, Minuet; Kareem 2026-11-08), Bombchu Bowling (Storms, Epona's) and the Kakariko gallery (Epona's) (R10-MINIGAMES, Kareem 2026-11-10), a one-time scrub (Storms; Kareem, Longshot rc.3, 2026-11-14, `r15-scrub-tokens.md:86`), chests and the Kokiri gift with PR #41 visuals (Sun's, Bolero, Lullaby, Minuet, Prelude; BBender, Longshot v3.1.1, 2026-11-23). Never seen outside a lesson: Serenade, Requiem, Nocturne, Song of Time. They rest on the shared `Item_Melody_*` grant (`data/settings.toml:81-82`, ASSUMED). |
| 2 | `songs=anywhere` releases songs to Chest, NPC, Cutscene, Song and Scrub only | follows from rows 4, 6, 9 and 11 | (see those rows) | | |
| 3 | A lesson's automatic scene needs either ocarina in logic | `data/world/remake/song_lessons.toml` | PLAYED | Adult with the Fairy Ocarina at Minuet (Kareem 2026-11-20, `r19-scenes.md:85,303`) | Yes |
| 4 | Floor and boss-heart checks take only 5 native pickups: Heart Container, Piece of Heart, Deku Shield, Hylian Shield, red rupee | `patch/drops.py:23-29`; `patch/freestanding.py:17,99-135` | PLAYED for the five (King Dodongo Hylian Shield: Kareem, Hookshot 2.0.1, 2026-11-08, §27. LLR tower Hylian Shield: R8-FREESTANDING). DUMP: songs and most majors have no native `Obj_` floor actor (§11, §36). | D27 "majors on the floor crash (#287, section 11)" is **STALE / overbroad**. The crash is one actor, `Obj_Arrow_Fire`, swapped onto the LLR tower heart: 3 of 3 crashes, Hookshot `main-ba594da`, 2026-11-07. The record is §10 (not §11) and infers "needs its logic group". The same evening a Hylian and a Deku Shield worked on the floor (§10). Since then inventory-only majors have been delivered by **composed** pickups: Boomerang (Kareem, rc.3, 2026-11-14) and Ocarina of Time (BBender, 2026-11-22, `chest-ocarina-model.md` C3/C4), both at Skulltulas. PR #41's song pickups were collected in the Temple of Time (BBender, v3.1.1, 2026-11-23). What still holds: a floor check shows only an actor that exists and has been proven at that kind of site. |
| 5 | Floor kinds cover only the 14 saved heart pieces and the 8 boss hearts | `patch/freestanding.py:22-23,26-47,50-51`; `census/scan.py` | DUMP | §36: other floor families either lack per-row remake-to-logic links (rupees, hearts) or have no saved Hash and `AlwaysRespawn` (keys) | Yes |
| 6 | Gift-only items stay off chests unless their actor is a native chest actor or in `chest_verified` | `patch/gifts.py:1253-1277`; `data/settings.toml:62-79` | Gate rule: PLAYED per admitted actor (6 entries, Kareem 2026-11-08 and 2026-11-09). The hold on the rest: **ASSUMED** (conservative; no failure recorded) | D23; §26 | Holds as a gate. Nobody has tried Light Arrows, Nayru's, Farore's, Stone of Agony, Double Defense, Biggoron, Bottle or Rupees (200) in a chest. Each needs one chest check. |
| 7 | No ocarina at a show-item hand-over (45 gift wrappers) or a scrub | `data/settings.toml:84-86`; `patch/gifts.py:1148-1160` | Ocarina of Time: PLAYED (gallery crash, German and English, Hookshot 2.0.14, `r11-ocarina.md`). Fairy: ASSUMED by analogy (`r11-ocarina.md:271-276`). | | Not retested on Longshot or after PR #40 changed the ocarina packs and ActorInfo |
| 8 | Ocarinas allowed at the direct and `GetPouchContent` scenes (Saria, moat, lessons, Light Arrows) | same, by wrapper class | Saria (Ocarina of Time) PLAYED (BBender 2026-11-22, PR #40 4.7). Lessons and the Light Arrows scene: ASSUMED from the wrapper class (`r11-ocarina.md:92-93`). | | |
| 9 | Shops sell only items with a native shop display, each on its own shelves | `fill.py:393-398`; `data/shops.toml` `[items]` | PLAYED (D21: a stand-in display left the shield on sale, Kareem 2026-11-08) + DUMP | | Yes. No song, key, heart piece or major can be shelved. |
| 10 | `Buy ...` goods only on shelves | `fill.py:50-54,405-406`; `generate/prepare.py:112` | DUMP (no grant adapter: `NotPushToPouch` fills an owned bottle) | Round 15 family table | Yes |
| 11 | Scrubs: only the 4 one-time sales shuffle; any non-ocarina item may be sold there | `patch/scrubs.py:54-88,315-344` | DUMP §23 + PLAYED (Storms 2026-11-14; adult Mirror Shield purchase, rc.7, 2026-11-19) | | Yes |
| 12 | Deku Stick and Nut Capacity only at scrubs | `patch/scrubs.py:26,326-328` | ASSUMED ("held until tested in chests") | | **Partly STALE**: Nut capacity was PLAYED at a Skulltula (`token_rewards.toml:34`, families-1, rc.3) and both are in the Token palette, but this hold removes Token |
| 13 | Skulltulas take only the 36 `REWARDS` | `generate/tokens.py:95`; `data/token_rewards.toml` | PLAYED per family (rc.3 packets, 2026-11-14 and 2026-11-15). Members beyond the one played per family: ASSUMED (structural siblings) | | Yes |
| 14 | No songs, Fairy Ocarina, progressive copies, keys, maps, compasses, trade items, card or `Buy` goods at Skulltulas | `token_rewards.toml:15-18`; `tokens.py:84` | Songs: ASSUMED (policy: "keep their existing holds"). Fairy: DUMP (no native world donor; the `Item_` ocarinas lack AnimationRef). Copies: DUMP (row 16). | | Songs could follow once PR #41's pickup exists as a donor. The Fairy reason should be re-read after PR #40, which changes the ocarina packs [INFERENCE]. |
| 15 | The token item goes only to Chest and Token | `tokens.py:41` | DUMP ("no exact-one native grant proven" elsewhere) + PLAYED (chest token: Kareem, rc.3) | | Yes |
| 16 | Progressive copies are chest-only | `data/world/world.toml:143-159`; `fill.py:410-411`; `generate/progressive.py:76-91` | DUMP (`r14-progressive.md:20-26`, §47: only a chest event reads owned tiers before the get window) + PLAYED (§47 full pass, 2026-11-13) | | Yes. This is the hardest limit on "anything anywhere": a floor, gift or Skulltula can never pick the tier. |
| 17 | Released dungeon items outside their dungeon: chests only. Key rings and silver rupees never leave. | `fill.py:41-48,424-428`; `patch/plan.py:235-263` | DUMP (`r17-dungeon-items.md` §2: credit is a source-bound chest event) + PLAYED (remote map, compass and boss key, 2026-11-18, `r18-dungeon-items.md:60-64`; display, rc.7, 2026-11-19) | | Yes. `04-world-format.md:381` ("not yet been played") and `fill.py:47` ("built, not played") are **STALE**. |
| 18 | Inside its own dungeon a dungeon item may go to any allowed kind | `fill.py:425` | ASSUMED | (section 6) | Matters only at Sheik in Ice Cavern |
| 19 | Fortress keys: chests (named grant) or jail sources | `fill.py:29-38,420-423`; `generate/key_families.py:68-81` | PLAYED (Kareem, Longshot 3.0.0, 2026-11-21, `r20-cows.md`) | | Yes |
| 20 | The Well floor key's source gives its own key or Rupees (20) on a key-shaped actor | `key_families.py:58-81`; `patch/floor_keys.py` | PLAYED (check11, Kareem, 2026-11-19, `r18-keys.md:496-501`) | | Yes. Shadow is held: ASSUMED, no save. |
| 21 | The Master Sword goes only to chests; the pedestal takes plain single items | `generate/swords.py:44-50,117-169` | PLAYED (v4, Kareem, 3.0.0, 2026-11-20, `r19-sword.md`) + ASSUMED (no other `Weapon_*` grant was tried) | | Yes |
| 22 | Stones and medallions only at reward slots, and reward slots take only them | `fill.py:400-404`; `generate/rewards.py:68-83` | DUMP (`r18-rewards.md` reader table) + PLAYED (first-pull and Door refusal, 2026-11-19/20) | | Yes |
| 23 | Bomb and Bombchu packs only where the Bomb Bag is already needed; ammo at Skulltulas needs its container | `fill.py:55-69`; `_container_forbidden` | PLAYED (D25: unusable chest bombs, Kareem, round 7) | | Yes |
| 24 | The 100-token reward is junk unless opted in | `remake/gifts.toml:63`; `tokens.py:92-110` | Policy + PLAYED (lift, 2026-11-20) | | Yes |
| 25 | Excluded locations take no progression | `generate/prepare.py:92-109` | Generator only (sweep 200/200, `r20-exclude.md`) | | Yes |
| 26 | `Missable` type takes no progression | `fill.py:407-408` | (no data) | | **Dead**: no location has this type; the one missable windmill copy is `keep_vanilla` [INFERENCE: unused guard] |
| 27 | Egg, Letter, Gerudo card and adult trade items never enter the pool | `patch/gift_rules.toml`; `remake/gifts.toml` | PLAYED (D31: Egg lost to the Letter, round 8; D39; R13 reports) | | Yes |
| 28 | Starting songs leave songs on song checks; starting items swap pool copies for junk | `generate/start.py:46-74` | INHERITED (OoTR's documented policy, `r20-start.md:15`) + PLAYED (broad start A/B, 2026-11-21) | | Yes |
| 29 | Never open the normal get window inside a running scene, fade or NPC reaction (rule f) | every grant adapter | PLAYED (cows v1 froze at an appended get, 2026-11-20, `r19-cows.md:95-124`; Ocarina of Time gallery crash, row 7) | | Yes. Native pickups (heart piece AI, token and floor-key `POLICY` gets) are on the safe side. |

Fill order (D32 to D34, `04-world-format.md:424-470`): own-dungeon items (small keys, then boss keys, then maps and
compasses); the return kit; the floor and other palettes; type-held items (songs, refills, gift items, copies); D25
bomb packs; shared progression; Skulltula filler match; the rest. Each stage's order came from failure counts in
sweeps (`r8-fill.md`; `r18-dungeon-items.md` §1), and two later reorders lost in paired sweeps (`r19-fill.md`,
`r20-fill.md`). If songs move to floor checks, they sit in the palette stage (D33) ahead of the type-held stage.

## 4. Songs, keys, ocarinas and upgrades on the floor

**How a floor check shows its item today.** The 14 heart pieces and 8 boss hearts change only `Gyaml` (the actor name)
on every age copy of the placement, by Hash (`freestanding.py:54-96`, `drops.py:32-76`). Hash, physics, groups and
anchors stay. The new actor brings its own model, AI and get event. The pickup's own saved type24/save0 Bool, keyed by
the Hash, keeps it from coming back (§36). The get is the native touch pickup, so rule (f) is met. That is why the
palette holds only native `Obj_` pickups. **Persistence is played only for King Dodongo and the LLR tower**; §36
calls that "the precedent, not proof" for every site, and no underwater site has been played.

**PR #41.** It builds `Obj_Clawshot_Melody_<Song>` for all twelve songs, from `Obj_Arrow_Fire`'s pack with
`GameParameterTableRef`, `SLinkRef` and `CaptureRef` dropped (`songs.py:40,46`). Each takes the song's
ocarina model, a PouchContent pointing at the song, and copies of `Obj_Arrow_Fire`'s ActorInfo and GameActorInfo
rows. Seeds write these packs only when a song has moved and place them nowhere (`patch/__init__.py` hook). BBender
placed two of them as **new actors** in the Temple of Time (test script only). Both were collected with A, showed
the get pose, and taught the song (Longshot v3.1.1, 2026-11-23; `song-get-effects.md` 4.4). That run was not
started from Claude's launcher, so its `mods:` lines are not on record.

**What songs on the 14 floor heart pieces would need** (the smallest step toward Kareem's ask):

1. PR #41 merged.
2. Generator: a new song-on-floor option (default off, rule i), allowed only with `songs=anywhere`. It adds the twelve
   songs to the `Freestanding` palette, and `freestanding.changes` maps a song to `songs.pickup_name(song)`. No logic
   change: collecting needs no ocarina and runs no lesson.
3. Dump work before any play:
   - Diff the melody pickup's AI and groups against the `Obj_Arrow_Fire` placement that crashed 3 of 3 at the LLR
     tower. The crash was inferred to come from a missing logic group, and the heart pieces are ungrouped (§10).
   - Show which Bool the arrow-derived AI writes on collection. r8 lists Fire Arrows as "reset24/file0"
     (`r8-freestanding.md:95`); whether a Gyaml swap keeps the heart's Hash Bool is unknown.
   - Add the 12 packs and the changed RSDB rows to the pack resource list and pass `tests/test_pack_nup_dump.py`
     (rule a).
4. A play check on Longshot 3.0.0, with a control launcher from main that shows a heart piece. Song at the **LLR tower
   heart** (the crash site; round 8's pre-pickup ranch backup is a natural child save): no crash on load, the pickup shows,
   the song is learned, and it does not come back after leaving, reloading, or Save and Continue. A second launcher
   for one underwater site (ZF Bottom) later.
5. A sweep (rule 2): 200 broad seeds with the option on, plus 50 Defaults and 50 Recommended.

**Boss hearts** (8 more sites): the same actor, but under each room's `Logic_Create` spawn gate and AiGroup binding.
`drops.py` refuses a pickup without those memberships. The risk is higher than at the free-standing hearts. A dump
check plus one boss room (King Dodongo has a played precedent).

**Loose rupees and recovery hearts** (112 + 25 remake Hashes) have saved flags but no census kind and no physical link
to a logic row (§36). Making them locations is census and logic work for every row before anything can stand on them.
It is the biggest gain in floor sites, and it needs no play to start.

**Keys on the floor.** Native floor keys have no saved actor Hash and respawn always: level logic owns their lifetime
(§36). A key on a heart-piece site would need a composed key pickup saved by the site's Hash, the mirror image of
`floor_keys.py`, plus a once-only play check. A small key outside its dungeon also needs source-bound credit, which only
chests carry today (row 17). Low value against high risk.

**Ocarinas on the floor.** A native `Obj_Ocarina_Time` exists. The composed Skulltula drop of it was PLAYED (BBender,
2026-11-22). A floor-site version would follow PR #41's recipe. Fairy Ocarina: no native world donor (row 14).

**Upgrades on the floor.**

- Progressive families: no. Only a chest reads the owned tier before the get window (row 16), so this stays out of
  reach without engine code.
- Fixed majors (Boomerang, Hammer, boots, Lens, spells, bottles, Biggoron Sword): PR #41's recipe (an
  `Obj_Arrow_Fire` base, the item's model and PouchContent) does not depend on the item. The Skulltula composition
  already delivered Boomerang, Din's Fire and Ocarina of Time in play. A general `Obj_Clawshot_<Item>` floor pickup is
  the route to "anything on the floor" except tiers and keys [INFERENCE: each family still needs its own play, as the
  token families did].

**The reverse: a Piece of Heart or rupee at a song location.** Already allowed whenever `songs=anywhere` and gifts
are shuffled: lessons stop being exclusive, and any item the gift stage admits may go there (matrix). PLAYED:
Boomerang from the Minuet lesson (Kareem, Longshot 3.0.0, 2026-11-20, `r19-scenes.md:85,303`). Rupees (20) at Zelda's
moat scene (BBender's seed, 2026-11-22, PR #40 4.6). A Piece of Heart at a lesson goes through the same
`GetPouchContent` grant: not played, [INFERENCE] same path. Nothing to build.

## 5. To lift next (value to "anything anywhere" against risk)

| # | Lift | Value | Risk | Needs |
|---|---|---|---|---|
| 1 | Songs on the 14 floor heart pieces (opt-in, `songs=anywhere`) | His stated ask; PR #41 already built the actors | Medium: `Obj_Arrow_Fire` crash history, persistence unknown | PR #41 merge; dump diff and Bool trace (section 4 step 3); generator option; LLR tower check plus control; sweep |
| 2 | Cheap generator-only lifts | Small, but each takes away an ASSUMED limit | Low | (a) Add Token to the capacity hold (row 12; played at a Skulltula). Sweep. (b) One chest check per gift-only item (row 6), adding `chest_verified` entries; this unlocks chests and scrubs for 9 items. (c) Re-read the Fairy-at-Skulltula reason and retest the ocarina hand-over crash after PR #40 (rows 7, 14). |
| 3 | Songs at Gold Skulltulas | 100 more song sites | Medium | PR #41's pickup as the composition donor; a `song` family in `token_rewards.toml`; one played Skulltula song |
| 4 | Songs at boss hearts | 8 sites | Medium-high (spawn gates) | Dump check of the `Logic_Create` binding with the new actor; one boss-room play |
| 5 | General fixed-major floor pickups (`Obj_Clawshot_<Item>`) | Majors on every floor site | Medium per family | Extend PR #41's recipe; one play per family; same persistence proof as 1 |
| 6 | Loose rupees and recovery hearts as locations | About 137 new floor sites for everything above | Low game risk, large data job | Census kind plus per-row logic links (no play to start); then the item-on-site checks of 1 and 5 |
| 7 | Keys on floor sites | Low | High (respawning keys, credit) | Composed saved key pickup; once-only play |
| (never) | Progressive tiers off chests; pots and crates | | | Engine code (row 16); pot identity and drop physics (§43) |

## 6. Finding: Ice Cavern map and compass can land on Sheik's lesson

With `Gift` shuffled and `songs=anywhere`, the lessons are no longer exclusive. Row 18 lets an own-dungeon item take
any kind inside its dungeon, so `Map (Ice Cavern)` and `Compass (Ice Cavern)` may go to `Sheik in Ice Cavern`. It
happens: `icecheck.py` seed 1 (`--shuffle Chest Gift --songs anywhere`) placed **Compass (Ice Cavern)** there, and the
full seed built without error (`ice-seed1/spoiler.json`). Seeds 2 to 6 did not.

The lesson grants through `GetPouchContent` with the generic `Item_Dungeon_Compass`. Off-area and small-chest dungeon
items get explicit `DungeonInfo.<target>` writes because the generic actor alone is not trusted to credit them
(`patch/plan.py:276-278`). A lesson gets no such write. Whether the compass credits Ice Cavern this way has never been
played, and the tracker reads the same flags [INFERENCE].

No other dungeon has a non-chest gift location inside it. Skulltula, floor and boss-heart palettes already keep
dungeon items out. Neither preset is affected: Recommended keeps `songs=song`.

The safe fix is a tightening: hold the `Map`, `Compass`, `SmallKey` and `BossKey` types to `Chest` everywhere. That is
a one-line hold in `allowed()` or a type hold in prepare, plus a sweep. `fill.py` belongs to the fill track, so I post
it on the thread rather than change it.

**Question for Kareem: tighten (dungeon items in chests only), or stage a play check of a compass from Sheik's
lesson?**

## 7. Questions for Kareem

- **May songs become floor pickups in seeds (BBender's open question, `song-get-effects.md` "Open")? If yes:
  opt-in, only with "songs anywhere", starting with the 14 floor heart pieces, with boss hearts and Skulltulas after
  their own checks?**
- **Ice Cavern map and compass at Sheik's lesson: tighten, or play-check (section 6)?**

## 8. Doc drift seen (not fixed; other owners)

- `decisions.md` D27 cites "section 11" for the floor crash; the record is §10, and it covers one actor
  (`Obj_Arrow_Fire`), not majors in general.
- `04-world-format.md:381` and `fill.py:47`: `all_anywhere` delivery has been played since (row 17).
- `fill.py:407`: the `Missable` guard matches no location.
- `E:/OOTRemake/work/r20-planning/feature-compare.md`: written before round 20. It still lists starting inventory,
  trials count, excluded locations and the token bridge as "no".

## Handoff

- Branch `r21/placement-audit`: this file only. No product code, so no gates.
- Checked: code at `aeba6df`; the matrix and kind listings from the real seed setup chain over the dump; six fill-only
  seeds and one built seed (scratch, outside the repo); every evidence citation above spot-read.
- Not checked: anything in game. No launcher staged. PR #41 was read, not built.
- Left for others: the Ice Cavern tightening (fill owner, section 6); the "to lift next" items once Kareem picks.
