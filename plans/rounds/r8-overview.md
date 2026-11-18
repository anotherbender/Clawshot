## Round 8 (M2 dependable seeds; M3 more checks: gifts, freestanding, shops)

Kareem agreed, 2026-11-09 ("let's go on please"); he plays `seed-shop-7c` and his main save meanwhile. Five tracks,
Bermuda thread `cs-r8`, herdr-core. New sections of `plans/03-game-data.md`: 32 (A) to 36 (E), in number order. The
round 5 to 7 rules on shared files carry over (`generate/fill.py` belongs to track A this round; other tracks post
small isolated commits to it). No Hookshot build. Track A runs on the default Claude model, the others on
`openai-codex/gpt-6.1-sol`. Kareem showed Ship of Harkinian's shuffle settings for reference; its options that need
engine code (shuffling swim, grab, climb, crawl, ocarina buttons, Roc's Feather, skeleton key) are out of reach for
RomFS-only mods (D14).

### Track A: dependable fill (`r8/fill`, Claude)

Owns `src/clawshot/generate/fill.py`, `tests/test_generate*.py`, `tests/test_fill*.py`, `plans/rounds/r8-fill.md`,
section 32.
1. Measure: fill attempts for 200 seeds in each mode (Chest; Chest+Shop; Chest+Shop+Gift; with Scrub and BossHeart;
   the default string), printing the item, the allowed locations left and the frontier at every failed attempt.
   Round 7's Chest+Shop+Gift seed 7 needed all 10 attempts.
2. Fix the causes the measurements show, the way OoT Randomizer's fill handles them (`Fill.py`: order, restrictive
   fill, its swap and retry rules at 526b4c8d), with a failing-before test for each; no relaxed rules or added
   attempts. Target: every mode's first attempt succeeds for at least 95% of the 200 seeds and none needs more than 3.

### Track B: get-item models (`r8/getitem`)

Owns `src/clawshot/patch/getitem.py`, the chest-allowed list in `src/clawshot/data/settings.toml`,
`tests/test_getitem*.py`, `plans/rounds/r8-getitem.md`, section 33.
1. The Fairy Ocarina from a chest shows no model (round 7, game-confirmed after the bind change). Find why from the
   data (the ocarina's ModelInfo, the get window's bind actions, how a gift's own presentation differs) and fix it.
2. One new-game test output with the Fairy Ocarina and the gift items not yet seen in a chest (Zelda's Letter, the
   Weird Egg, the Gerudo Membership Card, Epona's Song, the Ocarina of Time, the masks a seed could place), each with
   what Kareem should see. The allowed list grows only with his results.

### Track C: shops (`r8/shops`)

Owns `src/clawshot/patch/shops.py`, the Kokiri shopkeeper's gift patch in `src/clawshot/patch/gifts.py` (posted
small commits; track D owns the rest of the file this round), `tests/test_shop*.py`, `plans/rounds/r8-shops.md`,
section 34.
1. The Kokiri shopkeeper's gift window (D28): keep a shuffled gift available until collected, past Gohma and the
   castle visit, through the merchant's flow (an existing flag first, else a new saved Bool, D22); unshuffled stays
   vanilla. A new-game test output that skips him until after Gohma. D28's restriction lifts only after Kareem's
   result.
2. Settings like Ship of Harkinian's: `shop_slots` (0 to 8 shuffled shelves per shop, the rest vanilla; default all
   eight) and `scrub_prices` (`vanilla` or `fixed` with a price), through the settings string, with tests.

### Track D: more gift checks (`r8/gifts`)

Owns `src/clawshot/patch/gifts.py` (except track C's part), `src/clawshot/patch/gift_rules.toml`,
`src/clawshot/census/gifts.py`, `tests/test_gift*.py`, `plans/rounds/r8-gifts.md`, section 35.
From Ship of Harkinian's list, the checks the remake's flows can give: the 14 cows (milk with Epona's Song), the
Skulltula House rewards (10 to 50 tokens; 100 if the flow allows), the frogs (the song prizes and the two rewards),
and the merchants (Medigoron's Giant's Knife, the carpet salesman's Bombchus, Granny's potion). For each: the census
(flow, event, saved flag, repeat behaviour), the swap through the existing gift machinery (D22 once-gates), logic
rules, and a test output on a fitting save copy or new game. Each joins `--shuffle Gift` only after Kareem's result.

### Track E: freestanding items with native pick-ups (`r8/freestanding`)

Owns `src/clawshot/patch/freestanding.py` (new), `tests/test_freestanding*.py`, `plans/rounds/r8-freestanding.md`,
section 36.
1. The freestanding locations (the 36 heart-piece anchors first, then other placed pick-ups): actor, saved flag,
   respawn behaviour, and whether a native floor pick-up from D27's palette (Heart Container, Piece of Heart, Deku
   Shield, Hylian Shield, red rupee) can stand in, as the King Dodongo test showed.
2. `--shuffle Freestanding` (off) restricted to that palette, logic and tests; one test output (an early heart piece
   swapped for a shield), with what Kareem should see, including after Save and Continue.

### Round 8 result (2026-11-09)

All five tracks merged; main `14d7a26`, gates 721 passed / 86 skipped, dump 85.
- A fill: every mode 200/200 seeds on the first attempt, none unbeatable (D32 keys first, D33 type palettes, D34
  Archipelago's safe swap). Before: all kinds 0%, gifts 9.5%.
- B get-item models: gift items in chests show their models and text (Letter, Egg, Card confirmed by Kareem); the two
  ocarinas still show none (cosmetic; parked).
- C shops: `shop_slots`, fixed scrub fees; the shopkeeper's gift persists past Gohma and the castle (Kareem's test),
  so it holds any item (D28 lifted).
- D gifts: frog prizes, Skulltula House rewards and three merchant sales built behind in-game acceptance (not in
  `--shuffle Gift` yet); D31 keeps the Weird Egg and Zelda's Letter vanilla (one shared trade cell).
- E freestanding: floor heart pieces and boss hearts take native pickups; Kareem confirmed the ranch tower shield.

### After round 8

Round 9 candidate from play: `free_time_travel` also needs Sheik moved: as adult before the Forest Temple, Sheik
stands at the pedestal with a Talk prompt in the way (Kareem, 2026-11-09). Trace Sheik's Temple of Time placement
and its gate, and patch both before the pedestal test. Speedrunners (via Kareem, 2026-11-09): Sheik leaves once the Forest
Medallion is held, not after the Minuet; trace whether that reads the medallion item or the sage flag, which matters once
rewards are shuffled.
Kareem (2026-11-09, after the Forest Temple): Sheik stays at the pedestal until entering the room plays the Prelude
of Light scene, then leaves. `free_time_travel` must therefore clear Sheik's pre-Forest placement or that scene's
gate as well as the pedestal's; saves from before Phantom Ganon to after the scene are in
`save-backups/2026-11-09_1347-main-after-forest` for the trace.
Also from play: Sheik's second line there sends the player to Kakariko for the Hookshot (its vanilla place). In a seed
it should name where the Hookshot is (a static hint through `patch/text`, like Dampé's diary) or say nothing about it.

Claude builds a fresh full seed with every game-confirmed setting (Chest, Shop, Gift, Scrub, BossHeart as proven;
hints; forest closed; cheap Deku Shield) for Kareem's first full playthrough.

Round 9 candidate (Kareem, 2026-11-09): label dungeon checks in `location_names.toml` with the pause map's floor
(1F to 5F), so play notes match what the player sees. Kareem's Fire Temple floor maps (a guide's, facts only) show
16 chests and 5 Gold Skulltulas, as the census has, the two remake chests being the timed 5F trio's extra pair.
Derive floors from game data (room index to map floor) [inference: the map data holds it; not traced].

Round 9 candidate (seed 8 play, Kareem 2026-11-09): adult-only items obtained as child lock the item buttons. The
Bow from a chest auto-equipped as child; afterwards the Boomerang and Deku Sticks could not be used until save and
reload. Trace the remake's age gate for button items and the get-time auto-assign (player and pouch data, the get
flow); fix in data if it lives there, otherwise document the reload workaround and consider which items (Bow,
Hookshot, Hammer and others) need it. Backup: `save-backups/2026-11-09_1423-seed8-bow-lock`.
Detail (Kareem): loading zones do not clear it, Save and Continue does; at pickup the Bow joined the ZR item bar though
greyed out for child, and the reload removed it from the bar. Test the reverse too (adult picking up the Slingshot or
Boomerang). Fallbacks if no data fix: the play note and get text tell the player to Save and Continue, or a setting
keeps age-locked button items out of locations the other age reaches first.

Round 10 candidates (seed 8 play, Kareem 2026-11-09):
- The Market Potion Shop's child bottle (the owner gives an empty bottle, Link catches a bug in the shop, the owner
  fills it with Red Potion) is a remake-only check missing from the census; round 4 listed it as unclear
  (`Npc_Hylia_020_Shop_Child`, entry `Item_Bottle_TutorialEvent_Talk`, section 15). The remake has five bottles, not
  four. Trace it, add it as a gift check and to the logic as an early bottle (its conditions: child, day, no bottle
  yet?), and an in-game test.
- Bombchu Bowling opens after Dodongo's Cavern (round 4 already has `'Defeat King Dodongo'`; players online agree). The
  remake picks among five prizes at random (players online: a heart piece and a Bomb Bag upgrade among them; the
  flow's `Clear{First,Second,Third}Time` flags exist). Make it deterministic as OoT Randomizer does: the first win
  gives First Prize, the second win Second Prize, later wins the filler prizes; an in-game test. Same question for
  the shooting galleries' normal and expert prizes (Kareem: an expert tier exists).

- Release the seven frog checks into `--shuffle Gift` (Kareem's frog experiment passed, 2026-11-09, answers.md R8-FROGS):
  drop their `keep_vanilla` holds in `remake/gifts.toml`; the five song prizes enter the pool as Rupees (20), OoT
  Randomizer's vanilla item for them (the native prize varies 5 to 30). The Skulltula House previews passed too; the
  40 reward stays held until tested; merchants wait for Kareem's main save.
- Dampé's gravedigging heart piece (Kareem asked, 2026-11-09): not in `--shuffle Gift` yet (logic has it, child at
  night after Time Flows; the remake reworks the tour, Link leads Dampé to the spot). Trace its grant and add it as a
  gift check if the flow allows a once-only swap.
- Door of Time setting (Kareem, 2026-11-09: he expected door and pedestal open from the start, as Ship of Harkinian
  offers; free time travel alone still leaves the three Spiritual Stones, the Ocarina of Time and the Song of Time
  between child and adult). `door_of_time` = closed (vanilla) | song_only | open, through the `DoorOfTime` flow and
  its gates; logic for each; the default is Kareem's call (asked 2026-11-09). With it, decide whether
  `free_time_travel` becomes default on (after the first-pull boundary test).
- `free_time_travel` first-pull bug (Kareem, 2026-11-09, answers.md R9-FIRST-PULL): with the patch, Sheik's first adult
  scene plays without him (dialogue skipped). Keep the placed Temple Sheik for `Dm_TimeTemple_0050` (present while it
  has not played, or after Forest completion until the Prelude), check flags the skipped dialogue sets, and retest
  from an older child autosave; the pedestal may stay blocked until he leaves after that first scene.

Later-round candidate (Kareem, 2026-11-09, seed 8: "we need a check/item tracker"): **D38 makes
this a Tracker tab of the UI**, reading the **seed's own save folder**, not an independent page
watching the player's main autosave. Resolve collected state by actor/check kind: chests use
named `IsTreasureBoxOpen.<Hash>` Bools; ordinary loose pickups use their saved placement-Hash
Bool64 state; gifts and scripted actors use their audited event/state flags (section 44).
A universal raw-Hash test falsely labels opened chests unclaimed. Read the seed's spoiler and
save to show checks by area, owned items and remaining keys per dungeon (its first job), and
checks currently in logic without naming unfound items. Update on saves; PopTracker/EmoTracker
export remains a later option. D38 and section 44 distinguish this from the native current-
dungeon-only map/key display.

