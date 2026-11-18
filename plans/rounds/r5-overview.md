## Round 5 (M2 whole-game chest seeds; M3 shops and gifts begin)

Five tracks. Bermuda thread `cs-r5`. Tracks run in herdr-core (`hc`). Each track writes `plans/rounds/r5-<track>.md`.
New sections of `plans/03-game-data.md`: 16 (track A), 17 (track B), 18 (track C), 19 (track D); each track appends
only its own section, after the last one on `main` when it rebases. No Hookshot build this round.

Shared files: `src/clawshot/data/locations.toml` is written by `python -m clawshot.census.write_locations`; tracks C
and D may both change it (C chest names, D gift entries). On a rebase conflict there, rerun the writer on the
rebased tree instead of hand-merging. `src/clawshot/patch/__init__.py` and `src/clawshot/__main__.py` are track C's;
tracks B and D wire their kind into a seed in their own last commit, after Claude says track C's item 1 is on
`main` (one call in `make_seed`, one `--shuffle` value), so the merge conflict is a few lines. A change a track
needs in another track's file: post it on the thread; if it is small, make it as its own commit that touches only
that, and say so in the post.

### Track A: age travel (`r5/age`)

Owns `src/clawshot/world/search.py`, `src/clawshot/world/model.py`, `tests/test_world_search*.py`,
`tests/test_age*.py`, `plans/rounds/r5-age.md`, and section 16.

1. Settle from the data and sources when the remake lets Link change age: what the first Master Sword pull needs
   (spiritual stones, the Ocarina of Time, the Song of Time, the Door of Time), and when adult Link can put the sword
   back. Round 4's track B read a walkthrough saying only after the Forest Temple. Look at the Temple of Time and
   Master Sword event flows (`clawshot.formats.evfl`), the flags they ask (`GameDataList`), and the save reader on
   Kareem's save backups (all still child-era on 2026-11-08; he is playing to adult Link now, and a save taken after
   the first pull will follow). Cite the flow, entry and flag.
2. If returning is gated, model it in the search: an item found as adult before the gate opens is not usable as
   child until the gate opens. Tests: a seed that needs an adult-found item as child before the gate is not
   beatable; the same after the gate is.
3. The softlock this creates: a player who pulls the sword early can be stuck as adult if the gate needs something
   only a child can get. Propose a rule in the round file (for example: everything adult needs to open the gate is
   reachable as adult with what a child can collect before the first pull, or a setting below), with its test.
4. If one flag opens the return (a `GameDataList` default like round 4's fast start), write it as a setting in
   `src/clawshot/data/fast_start.toml` (`free_time_travel`, off) and its dump test; with it on, the search treats
   age changes as free, as OoT Randomizer does. Kareem decides the default.

### Track B: Deku Shield and shops (`r5/shops`)

Owns `src/clawshot/patch/shops.py` (new), `src/clawshot/data/shops.toml` (new), `tests/test_shop*.py`,
`plans/rounds/r5-shops.md`, and section 17. D19: the Deku Shield and shop contents are shuffled.

1. Every shop in the data: its slots (the 128 `shop_slot` census entries), what decides each slot's item, price, text
   and stock (actor parameters, `RSDB` rows, the shop's event flow), how buying gives the item, and the Kokiri
   shopkeeper's Deku Shield entry (`Npc_*_Shop_*`, section 15) and the tutorial after buying the shield. Wallet sizes
   are section 12's (200/500/1000). Write it as `shops.toml` (each shop and slot: Banc, Hash, vanilla item, price)
   with a dump test that reads every slot.
2. How one slot is changed to sell another item: the display object, the item given, the price, the name and
   description text; which items have a shop display object and which don't. Two test outputs outside the repo
   (`E:/OOTRemake/work/r5-shops/`): the Kokiri shop's Deku Shield slot selling another item (one with a display
   object), and the Deku Shield in a Kokiri Forest chest (the chest actor exists: `item_actors.toml`), each with what
   Kareem should see, including whether the shield's tutorial plays for the other item.
3. The shield in the logic: with shops vanilla, the Deku Shield is bought (as now); with `--shuffle Shop`, the Kokiri
   shield slot is a location and the shield is in the pool, so Mido's rule (sword and shield) puts it before him and
   the Mido skip lets it go anywhere. Prices as wallet requirements. Tests for both.
4. Last, after Claude's word: wire `--shuffle Shop` into `make_seed` (one commit).

### Track C: whole-game chest seeds (`r5/seeds`)

Owns `src/clawshot/generate/`, `src/clawshot/patch/{__init__,plan,write,items,events}.py`,
`src/clawshot/patch/chest_events.toml`, `src/clawshot/data/item_actors.toml`, `src/clawshot/__main__.py`,
`tests/test_generate*.py`, `tests/test_patch*.py`, `plans/rounds/r5-seeds.md`, and section 18.

1. First, small, its own commit, posted: `make_seed` takes a list of extra patch steps (a callable per kind:
   placements in, file changes out) so tracks B and D add theirs without touching the chest code. Claude merges it
   early.
2. Every chest a location: 119 census chests have no OoT Randomizer name (the remake's extra chests, D12:
   shuffled, Business Seeds filler; Dream World out). Give each a world location in its region (in
   `src/clawshot/data/world/remake/extra_<area>.toml`, new files; the loader reads them), with the rule to reach it
   and its source, or a reason it stays out. A test that every chest is a location or listed as excluded.
3. Chest events: for every chest whose `GetEventName` the patch removes (the Kokiri Sword's, others in
   `chest_events.toml`), what story state the event set (flags, quest steps) and the patch's way to set it anyway;
   a dump test per event.
4. Fast start in seeds: the seed's `GameDataList` gets the fast-start settings (D18: the intro skip by default, the
   others as settings), and the Mido skip removes Mido's requirement from the logic (OoT Randomizer's `open_forest`
   covers Mido and the forest exit together; the remake's exit gate is separate: check what the skip changes).
5. Three whole-game chest seeds for Kareem (`E:/OOTRemake/work/r5-seed/seed-<n>/`, launchers copied from
   `E:/OOTRemake/work/r3-seed/`, never run), each beatable, with its spoiler and a short note of the route the search
   found. Check every written file against the size table. After track A's model is on `main`, Claude asks for them
   to be made again.

### Track D: gifts through the flows (`r5/gifts`, Opus)

Owns `src/clawshot/patch/gifts.py` (new), `src/clawshot/census/gifts.py`, `src/clawshot/formats/evfl.py`,
`tests/test_gift*.py`, `tests/test_evfl*.py`, `plans/rounds/r5-gifts.md`, and section 19.

1. For every gift step in the census (148): what else in the flows reads the vanilla item (an `IsGet.<item>` used
   as "already given", or as a gate elsewhere: the Great Fairies use `IsGet.Item_DinFire` both ways, section 12), and
   the flag to use instead so the check gives its item once and gates stay as the logic models them. Class each
   gift: item swap only; swap plus flag rewrite; needs more (songs' play-along, cutscenes). A table in section 19.
2. `patch/gifts.py`: change a gift step's item (and the flag rewrites) for the first two classes, with dump tests
   that each changed flow round-trips and differs only in the intended steps.
3. Test outputs outside the repo (`E:/OOTRemake/work/r5-gifts/`): round 4's Talon test, plus three early-game gifts
   (a child NPC gift, a Great Fairy, one song if any is in class one or two), each with what Kareem should see and
   which save to start from (`E:/OOTRemake/work/save-backups/`, read with `clawshot.save`; a new game is fine).
4. Last, after Claude's word: wire `--shuffle Gift` into `make_seed` for the gifts that passed review (one commit).

### Track E: the in-game logic session (`r5/playtest`)

Owns `plans/playtest/` (new) and `plans/rounds/r5-playtest.md`; no code.

1. Every question for an in-game check in the round files (`plans/rounds/r*-*.md`, the **bold** ones) and in
   `03-game-data.md`, deduplicated: what to do, where, at which age and progress, what to watch, and what each
   answer changes (the rule file and key, or the fact to record).
2. A route: `plans/playtest/session-<n>.md`, the questions in the order a player meets them, grouped so one sitting
   covers an area. Kareem's saves (`E:/OOTRemake/work/save-backups/`, read with `clawshot.save`) say what his
   main game can reach now; questions that need later progress go in a later session.
3. Where a mod makes a question cheaper (an item placed where the question needs it), prepare it outside the repo
   (`E:/OOTRemake/work/r5-playtest/`) with a launcher copied from `E:/OOTRemake/work/r2-test/`, never run.
4. `plans/playtest/answers.md`: one line per question for Claude to fill in after the session.

### After round 5

**Round 5 result (2026-11-08):** all five tracks merged (`main` 6f7cbf0; 381 tests, 46 dump tests).
- A, age travel: the remake keeps adult Link adult until the Forest sage (`SageOfForest_IsCompleted_Exp` gates the
  pedestal); the search is chronological; `age_return_guarantee` on by default (D20, Kareem) and built into the fill;
  `free_time_travel` (a pedestal patch, off) waits for its in-game test after Kareem's first pull.
- B, shops: all 128 shelves traced; `--shuffle Shop` with native-display items only (D21); in game the slot swap
  and a chest Deku Shield work, a stand-in display does not, slots restock; Mido takes any shield.
- C, seeds: all 184 chests accounted for (164 shuffled, 20 excluded until their routes are known); four kept story
  wrappers; fast start in seeds; seeds 3, 7, 22 (Chest) and shop-7 (Chest+Shop) in `E:/OOTRemake/work/r5-seed/`,
  regenerated from `main` byte-identical.
- D, gifts: 79 gift checks classed; `--shuffle Gift` for 45 swaps plus the Great Fairies (new saved Bools, D22,
  worked on an old save) and the songs' play-along; songs and the Fairy Ocarina work from chests (D23).
- E, playtest: 197 questions in 17 route sessions with prepared mods (`plans/playtest/`).

For round 6 (to agree with Kareem): player-facing location descriptions for spoilers (Mido's chests are mirrored
against the N64 names); a "songs anywhere" setting; gift items in chests as each is tested; the logic-session
answers as they come; the rupee economy for early shop purchases.

