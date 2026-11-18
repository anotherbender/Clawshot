## Round 7 (M3 hints, get-item models, boss hearts, gift follow-ups)

Kareem agreed, 2026-11-08 ("Yes, please do"); he plays `seed-shop-7b` and his main save meanwhile. Four tracks,
Bermuda thread `cs-r7`, herdr-core. New sections of `plans/03-game-data.md`: 25 (A), 26 (B), 27 (C), 28 (D), each
appended in number order after 24. The round 5 and 6 rules on shared files carry over (a small change to another
track's file is its own commit, posted; `patch/__init__.py`, `generate/fill.py`, `settings.toml`,
`item_actors.toml` and the CLI are shared). No Hookshot build. Track A runs on the default Claude model, the others
on `openai-codex/gpt-6.1-sol`. Every in-game test is one launcher with its own user folder and a short checklist;
save-copy tests name the save they copy from `E:/OOTRemake/work/save-backups/`.

### Track A: hints (`r7/hints`, Claude)

Owns `src/clawshot/generate/hints.py` (new), the hint step in `src/clawshot/patch/text.py`, `tests/test_hints*.py`,
`plans/rounds/r7-hints.md`, section 25. Round 6's design note (`plans/rounds/r6-hints.md`, "Design note: hints in
round 7") is the spec:
1. Gossip Stones as hint locations in the world (a non-item kind; OoT Randomizer's `HintStone` regions and rules
   through `STONE_LINKS`, the four remake-only stones by hand), one label per stone.
2. Hint selection: Way of the Hero, barren ("foolish") areas, item and `always`/`sometimes` location hints, junk;
   a hint goes only on a stone reachable where it matters. Names from the round 6 catalogue; area names from the
   world's hint areas. Clawshot's own wording (no copied text).
3. Settings through the settings string: `hints` = `always` (stones speak without the Mask of Truth) or `mask`
   (vanilla), and the distribution. Provisional default `always`, English text written to every language archive;
   both are questions for Kareem.
4. A `make_seed` step, the hints in the spoiler and the play note, a dump test that every hint names a placed item
   at a reachable stone. Test output: `E:/OOTRemake/work/r7-hints/seed-shop-7c/`, which is `seed-shop-7b` plus hint
   text only (same placements, hints chosen from its spoiler under current logic; every non-text file byte-identical
   to 7b's), with a launcher that continues from his `user-seed-shop-7b` save copy.

### Track B: get-item models and gift items in chests (`r7/getitem`)

Owns `src/clawshot/patch/getitem.py` (new), the chest-allowed list in `src/clawshot/data/settings.toml`,
`tests/test_getitem*.py`, `plans/rounds/r7-getitem.md`, section 26.
1. What picks the model in the get window for an item from a chest (round 6: `Item_Melody_*` ModelInfo is
   `Obj_Rupee`, so a song shows a green rupee; the Fairy Ocarina from a chest shows no model, text correct). Trace
   both from the data and name the field each reads.
2. A patch so each gift item that can land in a chest shows a fitting native model (an ocarina for the ocarinas; a
   native note or song model for songs if the game has one, else say so and propose one); no new assets.
3. Gift items in chests: list the gift items not yet seen working in a chest; one test output (new game, Kokiri
   Forest and Mido's chests) holding as many of them as fit, each with what Kareem should see; the allowed list grows
   only with his results.

### Track C: boss Heart Containers and Gold Skulltula tokens (`r7/drops`)

Owns `src/clawshot/patch/drops.py` (new), `src/clawshot/patch/tokens.py`, `tests/test_drops*.py`,
`tests/test_token*.py`, `plans/rounds/r7-drops.md`, section 27.
1. The 8 boss Heart Containers (`Obj_Heart_Container` in each boss room's Banc): how each spawns after the boss, its
   saved flag, and which items can replace it without round 2's freestanding crash (#287 signature: majors need their
   object or script group). Propose a location kind with a native-actor restriction, as D21 does for shops.
2. A test output on a save copy before a boss (King Dodongo: check `2026-11-08_1114-main-dodongo`; say if no backup
   fits): the Heart Container swapped for a safe item, with what Kareem should see, including after Save and Continue.
3. Gold Skulltula tokens: round 6 found a replaced token lacks the `OneShotGoldTokenDeadAfter` callback (section 23).
   Is there a way to keep the token actor and change what it grants, or to keep the callback? A test output only if
   the data supports one; else say what is missing.
4. `--shuffle BossHeart` (off) for what passed review; their in-game tests decide.

### Track D: the shopkeeper's shield as a check, and the Treasure Chest Game (`r7/gifts`)

Owns `src/clawshot/patch/gifts.py`, `tests/test_gift*.py`, `plans/rounds/r7-gifts.md`, section 28.
1. The Kokiri shopkeeper's free Deku Shield repeats while none is equipped (round 6, track F, `r6-play.md`). Add a
   once-only gate on both grant branches (an existing flag first, else a new saved Bool, D22) so it becomes a gift
   check; keep the vanilla repeat when unshuffled. Logic: the free shield event stays as it is when unshuffled.
   Test output (new game) with the check given a different item, and what Kareem sees on a second visit.
2. The Treasure Chest Game reward chest (D17, kept vanilla): a contents-swap test output on a save copy of a child
   near Castle Town (the round 6 Castle Town tests used one), with what he should see. It joins the shuffle only
   after his result.
3. The 9 boss rewards (stones and medallions): research only: how each is given (the blue warp and its cutscene,
   flags, the Temple of Time's checks of quest steps rather than items, section 19), and what shuffling them would
   need. No patch.

### Track E: hints never name junk (`r7/hintfix`, added 2026-11-08)

Owns `src/clawshot/generate/hints.py`, `tests/test_hints*.py`, `plans/rounds/r7-hintfix.md`, section 29.
1. D29: item, `always`, `sometimes` and random hints name only items worth having (progression items, Pieces of Heart
   and Heart Containers, non-progression upgrades such as wallets and capacity upgrades); never rupees, ammo, refills,
   `Buy` items, recovery hearts or bottle contents. Define the class once from the world's item data, with a test
   that no location hint names junk over many seeds and that barren hints are unchanged.
2. Rebuild Kareem's test output as `E:/OOTRemake/work/r7-hints/seed-shop-7c-next/` (7b's placements, only text files
   differ from 7b; never write to `seed-shop-7c`, which he plays; Claude swaps it in). List the 40 lines.

### Track F: graveyard and bombs from play (`r7/play`, added 2026-11-08)

Owns `src/clawshot/data/world/remake/child_graveyard.toml`, the graveyard rows of
`src/clawshot/data/location_names.toml`, `tests/test_world_remake_play.py`, `plans/playtest/answers.md`,
`plans/rounds/r7-play.md`, section 30.
1. The child graveyard's three pull-back graves (`Land_Graveyard_HidingHoleJoint_A_01` at x 4.0 z 5.7, x 21.5 z 11.2,
   x 21.4 z 23.2 in `Graveyard_Child_Dynamic`). Kareem, from the Royal Family's Tomb: the fourth grave from the right
   (unmarked) holds a ReDead and a chest (the shield grave, `Obj_TBox_A_06` 16912540161937823130); another (marked)
   grave holds a cracked wall (`WallCrack` 9366825990748670811 at (3.9, 83.9, 27.0) in `Graveyard_Child_Static`).
   What is behind the cracked wall, and is any of it a check? Rewrite the three graves' "where" so a player standing
   at the tomb entrance finds each, and check the heart-piece grave's rule (`True`) against the data.
2. Bombs from a chest pack: in Kareem's `seed-shop-7c` save (read only:
   `E:/OOTRemake/work/r7-hints/user-seed-shop-7c`, newest slot) a shop bomb bundle from a chest gave
   `IsGet.Item_BombBag_Small` and 20 bombs; bombs equip, but Link raises one for a few frames and the action cancels.
   His main save, where bombs work, is copied at `E:/OOTRemake/work/save-backups/2026-11-08_2140-main-jabu`. Find
   what makes bombs usable (compare the two saves' bomb and pouch entries by GameDataList name; trace the player's
   bomb action condition), and say whether the real Bomb Bag (KF Storms Grotto chest in 7b/7c) will make bombs work
   on his 7c save or leave him without bombs. No save edits; if a fix is needed, propose it in the round file.
3. What a vanilla chest gives when its item is already owned (the shield grave's `TBox_Shield_Hylian` with the
   Hylian Shield held; Kareem got 20 rupees from that grave while the graveyard had loaded vanilla files).
4. Record each in `plans/playtest/answers.md`, the catalogue and section 30.

### Track G: bombs need Goron's Bracelet (`r7/bombs`, added 2026-11-08)

Owns the remake helper overrides for explosives (wherever the world's remake overrides keep them; small posted
commits to shared world files), `tests/test_world_remake_bombs.py`, `plans/rounds/r7-bombs.md`, section 31.
1. D30: every rule that uses bombs (OoT Randomizer's `Bombs`/`has_bombs`, the bomb half of `has_explosives` and
   `can_blast_or_smash`, `can_use(Bombs)`, bomb-only tricks) also needs lift grade Low: Goron's Bracelet as child, any
   strength upgrade as adult. Which items grant `LiftGradeUP` at which grade: from `PouchActorInfo`/`ExpansionAvility`
   (section 30), per age. Bombchus and Bomb Flowers keep their own rules (check Bomb Flowers already need strength).
   Overrides with `was` and `source`, never edits to the translated OoT Randomizer files.
2. Tests: a synthetic world where bombs without the Bracelet reach nothing new; the seed 7 matrix (Chest,
   Chest+Shop, Chest+Shop+Gift, the default string) still generates within the existing bound (print attempts and
   spheres); the 200-seed default beatability test passes; 7b's 228 placements still replay to a win.
3. List, from those seeds, how often the first bomb use moved later, and any rule that now cannot be met.

### After round 7

**Round 7 result (2026-11-08/09):** all seven tracks merged (`main` 739b930; 619 tests, 78 dump tests).
- A, hints: the 40 Gossip Stones as hint locations; Way of the Hero, barren, item, `always`/`sometimes`, random and
  junk hints; `hints` = `always` (default, D26) or `mask`; English text in every language archive. In game
  (`seed-shop-7c`): the stones speak without the mask; the highlight colour now ends after each name.
- B, get-item models: the get window's model traced; the Song of Storms shows an ocarina stand-in, Din's Fire and
  the Adult's Wallet work from chests; the Fairy Ocarina still shows no model.
- C, boss hearts and tokens: `--shuffle BossHeart` (off) with native floor pick-ups only (D27), game-confirmed at
  King Dodongo; a token's pouch reference does not decide its grant, so tokens stay unshuffled.
- D, gift follow-ups: the Kokiri shopkeeper's gift is a once-only check holding only items no seed needs (D28,
  game-confirmed); the fill places items in order of restriction; the Treasure Chest Game swap is built, untested;
  the nine boss rewards researched.
- E, hints never name junk (D29).
- F, from play: the graveyard's three graves (the fairy wall split from the shield grave); an owned Hylian Shield
  turns that chest into a red rupee, which the seed's patch overrides; bombs need lift strength.
- G, bombs need Goron's Bracelet in logic (D30); helper overrides in the remake files.

Waiting on Kareem in game: bombs before and after Darunia's Bracelet on `seed-shop-7c`; the Jabu-Jabu switch with
Bombchus; the Treasure Chest Game swap; `free_time_travel` after his first Master Sword pull; the route cards.

For round 8 (to agree with Kareem): fill robustness (Chest+Shop+Gift seed 7 needed all 10 attempts); the Fairy
Ocarina's get model; a fresh full seed with every proven setting for a real playthrough; extending the shopkeeper's
window (D28); token shuffle by another route; the boss rewards; run and sprint speeds from the animations (optional).

