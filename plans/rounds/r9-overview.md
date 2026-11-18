## Round 9 (M2 seeds that play cleanly; testers)

Kareem agreed, 2026-11-09 ("Sounds good, please do"); he plays seed 8 (`work/r8-full`) meanwhile, so the CPU rule
holds the whole round: one worker process at a time while `hookshot.exe` runs. Three tracks, Bermuda thread `cs-r9`,
herdr-core, all on `openai-codex/gpt-6.1-sol`; Claude reviews. New sections of `plans/03-game-data.md`: 37 (A) to 39
(C), in number order. Shared files as in rounds 5 to 8 (small isolated commits; `generate/fill.py` changes only with
a post). Seed 8's findings may be routed to any track during the round. No Hookshot build.

### Track A: the item bar and age-locked items (`r9/itembar`)

Owns `plans/rounds/r9-itembar.md`, section 37, any new `src/clawshot/patch/itembar.py` and its tests.
1. Trace the remake's item bar (one ZR item; R cycles the bar; the Items menu greys out items Link's age cannot use)
   from the game data: what adds an item to the bar when it is obtained, what rebuilds it on load, and where the age
   restriction lives. Kareem (seed 8): the Bow from a chest joined the bar as child, item use jammed until Save and
   Continue, loading zones did not clear it, and after the reload the Bow was off the bar. Backup:
   `save-backups/2026-11-09_1423-seed8-bow-lock`. Table every button item with its usable age.
2. If a data change prevents it (the item not added, or the bar rebuilt at the get), patch it behind a default-on
   setting, with tests and a new-game test output: child takes the Bow from a Mido chest; an adult takes the
   Slingshot or Boomerang. A checklist for Kareem.
3. Otherwise: the play note says to Save and Continue after obtaining an item Link's age cannot use, listing those
   items when the seed places one where the other age reaches it first; propose (do not build) a get-text line and a
   fill setting that keeps age-locked button items out of such locations, with their costs, for Kareem.

### Track B: Sheik and free time travel (`r9/sheik`)

Owns `src/clawshot/patch/age.py`, `plans/rounds/r9-sheik.md`, section 38, Sheik's text patch and tests.
1. Trace what puts Sheik at the Temple of Time pedestal before the Forest Temple and what the Prelude of Light scene
   sets when it moves him (Kareem: Sheik stays until entering the room after the Forest Temple plays the scene; the
   speedrunners say the Forest Medallion triggers it). Compare `save-backups/2026-11-09_1022-main-adult-first`
   (adult, before the Forest Temple) with `2026-11-09_1347-main-after-forest` (before Phantom Ganon to after the
   scene). Say whether the gate reads the medallion item or a sage flag (matters when rewards are shuffled).
2. Extend `free_time_travel` (section 16) so an adult before the Forest Temple can return to child: Sheik not in the
   way and the pedestal usable, while the Prelude of Light check (Sheik at Temple) still plays after the Forest
   Medallion. Logic for the setting; a test output on a copy of the adult-first backup with a checklist.
3. Sheik's line there sends the player to Kakariko for the Hookshot. In seeds, rewrite it through `patch/text` to name
   where the seed's Hookshot is (as a static hint) or to drop the Hookshot; all 16 language archives get the English
   (D26). Tests.

### Track C: seed packs and map floors (`r9/seedpack`)

Owns a new `src/clawshot/pack/`, `docs/seed-pack.md`, `plans/rounds/r9-seedpack.md`, section 39 and their tests;
`src/clawshot/data/location_names.toml` for item 2 (posted small commits).
1. Seed packs for invited testers (Kareem: ready-made seeds, code not hidden): `python -m clawshot.pack --settings
   <CS1> --seed <n> --out <zip>` builds a zip with Clawshot's source and data (no plans), `Make seed.bat` and
   `Play seed.bat`. Make asks once for the tester's romfs and Hookshot folders, checks the game version (the dump
   build, `e0f3ccfa`) before anything else, runs the generator with `uv`, and checks the output against a digest the
   pack records (same string, seed and version give the same bytes). Play starts `<Hookshot>\bin\hookshot.exe` with
   `HOOKSHOT_NO_UPDATE_CHECK=1` and its own user folder, and stops if that exe is missing. No game file and nothing
   derived from one goes in the zip except that digest. A pack for seed 8's settings, made in a scratch folder and
   compared with `work/r8-full/seed-full-8`; `docs/discord/server-kit.md`'s tester guide brought in line.
2. Dungeon directions name the pause map's floor (1F, 2F, B1...), taken from the game data (room to map floor), so
   play notes match what the player sees; facts from guides only to cross-check (Kareem's Fire Temple maps: 16 chests,
   5 Gold Skulltulas).

### Round 9 result (2026-11-09)

All three tracks merged; main `90ef730`, gates 761 passed / 89 skipped, dump 88.
- A item bar: the save keeps the selected bar item and the load-time rebuild filters by age; no data action rebuilds
  it at a pickup, so seeds ship the fallback: `play-note.md` tells the player to Save and Continue and lists the
  seed's age-locked items the wrong age reaches first (seed 8: 10). Kareem reproduced the lock on Lichii (game
  behaviour). A get-text line and a fill setting are proposed in `plans/rounds/r9-itembar.md` for Kareem.
- B Sheik: Temple Sheik follows Forest quest completion (`SageOfForest_IsCompleted_Exp`), not the medallion; "Sheik
  at Temple" now needs `'Defeat Phantom Ganon'`. `free_time_travel` (default off) opens the pedestal and hides Temple
  Sheik until Forest completion; Kareem's test pending (`work/r9-sheik-cs9b/ingame`). Every seed's Sheik names the
  seed's Hookshot location in all 16 languages.
- C seed packs and floors: `python -m clawshot.pack` builds a private source-only zip with `Make seed.bat` (version
  check first, Hookshot optional) and `Play seed.bat`; a pack replayed seed 8 byte for byte. Emulator steps in
  `docs/seed-pack.md` (Lichii confirmed). Dungeon directions name the pause-map floor (134 chests, from MapParam).
- From play: the guard house crashes are Hookshot#1112 (commented with Kareem's OK); test pools now cap their workers
  (`c9e2e2b`).

First public test seed (Kareem, 2026-11-09, after another randomizer posted a ready-made rando in the Lichii server without
trouble): seed 10 with seed 8's settings (Chest, Shop, Gift, Scrub, BossHeart), main `ceaada4`, pack
`work/r9-packs/clawshot-seed-10.zip` (`READ ME FIRST.txt` with the Discord link). Chosen because Bombchu Bowling's
random Second Prize holds a 1-rupee filler (seeds 9 to 16 checked; the First Prize stays the vanilla Bomb Bag).
Make replayed it end to end from a fresh extract: Verified seed 10, 10 wrong-age warnings in its play note.

