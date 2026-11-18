## Round 6 (M2 settings string and readable spoilers; M3 hints, scrubs and tokens begin)

Kareem agreed, 2026-11-08 ("go ahead and continue"); he plays `seed-shop-7` meanwhile. Four tracks, Bermuda thread
`cs-r6`, herdr-core. New sections of `plans/03-game-data.md`: 20 (A), 21 (B), 22 (C), 23 (D), each appended in number
order. The round 5 rules on shared files carry over (a small change to another track's file is its own commit,
posted). No Hookshot build. Track C runs on the default Claude model, the others on `openai-codex/gpt-6.1-sol`.

### Track A: readable locations (`r6/names`)

Owns `src/clawshot/data/location_names.toml` (new), the spoiler and play-note code (`spoiler()` in
`src/clawshot/generate/__init__.py`), `tests/test_names*.py`, `plans/rounds/r6-names.md`, section 20.

1. For every shuffled location (chests first, then shops, gifts, the Great Fairies): a short player-facing name and a
   one-line "where" (area, room, what you see; dungeon room numbers mean nothing to a player), from the placement
   data (positions, the room's doors and landmarks) and guides (facts only, cite the URL). Mido's house, settled in
   game: walking in, the far-left chest is Hash `4555665598794293658` (OoT Randomizer's "KF Midos Top Right Chest")
   and the far-right one `9725242744547055868` ("Top Left"); say how the middle two map.
2. Every place where an OoT Randomizer name was matched to a remake chest by position or by guess (track C's
   symmetric pairs: Goron City maze blue chests, Gerudo Training Ground lobby and heavy-block chests, Spirit
   invisible pair, Fire's timed scarecrow-room chests; Mido's house): is the match only a label, or do the
   vanilla item or the rule differ between the pair? List any that change logic.
3. The spoiler and the play note show the player-facing name and "where" next to the OoT Randomizer name. A test
   that every shuffled location has both.

### Track B: settings (`r6/settings`)

Owns `src/clawshot/generate/fill.py`'s `Settings` and `src/clawshot/__main__.py`, the price part of
`src/clawshot/patch/shops.py`, `src/clawshot/data/settings.toml` (new), `tests/test_settings*.py`,
`plans/rounds/r6-settings.md`, section 21.

1. A settings string (M2): every setting (shuffled kinds, dungeon items, logic options, fast start, free travel, the
   return guarantee, the new ones below) in one short string; `--settings <string>` and `--print-settings`; the
   spoiler records it; the same string and seed give byte-identical files (a test). Defaults written in one place.
2. `songs`: `song` (default, D23) or `anywhere`. Gift items allowed in chests: a list in `settings.toml` of actors
   seen working in a chest (the Fairy Ocarina, the Song of Storms so far), each with its source; only those leave
   gift locations.
3. Prices: `shop_prices` = `vanilla` or `affordable` (every shuffled shop item 10 rupees, as Ship of Harkinian and
   OoT Randomizer offer), and `cheap_deku_shield` (the Kokiri shop's Deku Shield at 10 rupees whether or not shops
   are shuffled; default on, provisional: Kareem counted 36 guaranteed free-standing rupees in the forest outside
   Mido's house and seed 22 needed nearly all of them). Through `GoodsList` `PriceOffset`, which the shop tests showed
   working; the logic's wallet rules use the patched price. One test output in `E:/OOTRemake/work/r6-settings/`.

### Track C: text and Gossip Stones (`r6/hints`, Claude)

Owns `src/clawshot/formats/msbt.py` (new), `src/clawshot/census/hints.py` (new), `src/clawshot/patch/text.py`
(new), `tests/test_msbt*.py`, `tests/test_hints*.py`, `plans/rounds/r6-hints.md`, section 22.

1. `formats/msbt`: read and write the game's message files (round 4 read them for the Great Fairies' lines with a
   scratch script) from the format, no GPL code. Every message file in the dump round-trips (byte-identical or
   tree-equal, say which) in a `dump` test.
2. A census of Gossip Stones: every stone (Banc actor), how it picks its text (actor parameter, flow, message id),
   and whether it needs the Mask of Truth; the other hint givers (Sheik, the owl, the Kakariko Skulltula house).
3. Item-get text: what decides the get window's text and model for an item from a chest, an NPC and a shop (the song
   in a chest showed a green rupee), and how a patch would name an item in an NPC's line.
4. One test output (`E:/OOTRemake/work/r6-hints/`): a Gossip Stone Kareem can reach early saying a custom line, with
   what he should see. A short design note for hints in round 7 (OoT Randomizer's hint kinds, which fit the remake).

### Track D: scrubs and Skulltula tokens (`r6/tokens`)

Owns `src/clawshot/patch/scrubs.py` and `src/clawshot/patch/tokens.py` (new), `tests/test_scrub*.py`,
`tests/test_token*.py`, `plans/rounds/r6-tokens.md`, section 23.

1. Deku Scrubs (21 in the census): how each sells (actor parameters, flow, price), which are one-time checks, and a
   patch that changes one scrub's item; a test output.
2. Gold Skulltula tokens: how a token is given (the enemy's death, the token actor, its flag), whether a token's
   actor can be swapped for another item (OoT Randomizer's tokensanity), and the House of Skulltula rewards as gift
   checks (are they in the gift census?). A patch and a test output for one early token, if the data allows it.
3. Both as locations the fill can use behind `--shuffle Scrub` and `--shuffle Token` (off), only for what passed
   review; their in-game tests decide the defaults later.

### Track E: the Castle Town shop crash (`r6/shopfix`, added 2026-11-08)

Owns `src/clawshot/patch/shops.py` (except the price code, track B's), `tests/test_shop*.py`,
`plans/rounds/r6-shopfix.md`, a section 24.

Kareem's `seed-shop-7` crashed on entering Castle Town as child (Hookshot v2.0.1, log
`E:/OOTRemake/work/r5-seed/user-seed-shop-7/hookshot_log.txt`, line ~24488): thread `GeneralFormatAsync_`, write to
guest `0x10`, x6/x7 holding the ASCII `Component/ShopPa`; just before, the overlay served `Market_Child_Static` and
the seller packs `Npc_Hylia_021_Shop_Child`, `_018_` and `_020_`. The Kokiri shop's changed packs worked in the
same run and in the round 5 tests.

1. Find the cause from the data, without the game: diff the seed's three Market packs (and the Kakariko and other
   shops' packs it writes) against the dump's, field by field; check every reference a changed `ShopParam`
   (`GoodsList`, boards, group memberships removed by round 5's `dc037c8`) makes against what the pack and the
   placement still provide. Name the change that leaves a null.
2. Bisect outputs for Kareem in `E:/OOTRemake/work/r6-shopfix/` (new game is too slow: use a copy of a save that
   is a child near Castle Town, from `E:/OOTRemake/work/save-backups/`): each Market pack alone, and the suspected
   change reverted, each with what he should see.
3. Fix the patch, with a dump test that reproduces the bad reference, and regenerate the seed as
   `E:/OOTRemake/work/r5-seed/seed-shop-7b/` (same seed and settings) with a launcher; never touch `seed-shop-7`
   or `user-seed-shop-7`.

### Track F: findings from play (`r6/play`, added 2026-11-08)

Owns the round 4 logic files `src/clawshot/data/world/remake/child_*.toml` (no other track this round), their
tests, `plans/playtest/answers.md`, `plans/rounds/r6-play.md`.

Kareem's `seed-shop-7` run (2026-11-08), each to settle against the data and apply with `source` and a test:
1. The Deku Tree: the Boomerang hits the switch that opens the Slingshot room's exit and reaches the top floor, as
   the Slingshot does (round 4's rules ask for the Slingshot only); the Boomerang stuns Gohma. Check each against
   the placement data (the switch and target actors) and change the rules to `Slingshot or Boomerang` where the
   data agrees.
2. The castle moat is shallow: the Ocarina of Time needs no Silver Scale (playtest question; check the HF rules).
3. The Kokiri shopkeeper gave a free Deku Shield after Mido (Kareem held the Kokiri Sword and a Hylian Shield; the
   slot also sold one at 40): round 5's `present_DekuSheld` route. Find its exact conditions and model it (a free
   Deku Shield event after Mido, under those conditions), and say whether it is a check to shuffle later.
4. Record each in `plans/playtest/answers.md` and section 12.

### After round 6

**Round 6 result (2026-11-08):** all six tracks merged (`main` a786358; 511 tests, 68 dump tests).
- A, names: a sourced player-facing catalogue (335 checks); spoilers carry the names and a `play-note.md` with a
  logic-built opening route, shelf positions and prices.
- B, settings: one settings string (`--settings`, recorded in the spoiler, byte-identical replay); songs anywhere
  (opt-in, all 12); `shop_prices` and `cheap_deku_shield` (on); forest closed by default with `closed_deku` and
  `open` (D24); a fill fix that keeps held-item priority when shops are shuffled.
- C, hints: `formats/msbt` (8,640 message files in 16 languages round-trip byte-identical); 40 Gossip Stones
  catalogued; `patch/text`; a custom stone line test output.
- D, scrubs: `--shuffle Scrub` for the four one-time sale families (nine copies; repeat vendors stay vanilla); Gold
  Skulltula tokens not shuffled (a replaced token has no persistence).
- E, shop crash: shuffled shop goods grew a file inside the seller pack past its size-table entry; the writer now
  raises nested entries (game-confirmed in Castle Town, purchases work). Shop refills stay in shops; bomb and
  Bombchu pickups only where the Bomb Bag is guaranteed (D25); Buy Blue Fire only where the game sells it.
  `seed-shop-7b` is seed-shop-7 with the size fix only, for Kareem's save.
- F, play findings: the Boomerang works for the Deku Tree's switches, the vine wall and Gohma; the Kokiri
  shopkeeper's free Deku Shield (repeats while none is equipped) is a logic event, not a check; the moat needs no
  scale.

Waiting on Kareem in game: `seed-shop-7b`; `free_time_travel` after his first Master Sword pull; the logic-session
route cards. The Minuet, closed-Deku, price and Gossip Stone tests passed (2026-11-08; the Fairy Ocarina from a
chest shows no model).

For round 7 (to agree with Kareem): hints on Gossip Stones (track C's design note); gift items in chests as each is
tested, and get-item models for gift items from chests (songs show a green rupee, the Fairy Ocarina
none); a once-only gate for the shopkeeper's shield so it can be a check; boss Heart Containers as checks; token
persistence; the advanced options (bomb pickups as bags, open Deku) as Kareem asks for them.

