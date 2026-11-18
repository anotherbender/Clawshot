## Round 3 (M2's first playable mini-seed)

Three tracks. Bermuda thread `cs-r3`. Each track writes `plans/rounds/r3-<track>.md`. Read `03-game-data.md`
(sections 9 and 10 are new) and `decisions.md` (D15-D17) first.

### Track A: seed output (`r3/seed`)

Owns `src/clawshot/patch/`, `src/clawshot/data/item_actors.toml`, `src/clawshot/__main__.py`,
`src/clawshot/generate/` (extending what is there), `tests/test_patch*.py`, `tests/test_seed*.py`,
`plans/rounds/r3-seed.md`. Consumes `census` and `world` as they are on `main`; changes there go through the
thread.

1. `item_actors.toml`: for every item the fill can place in the first seeds (fixed items, D16), the remake actor a
   chest's `Drop__DropActor` takes (e.g. `Kokiri Sword` -> `Item_Sword_Kokiri`, `Rupees (5)` -> `TBox_Rupee_Blue`,
   the Deku Tree's map and compass). Derive the pairs from linked locations (census `vanilla_item` against OoT
   Randomizer's vanilla item for the same `oot_randomizer_name`) and check each actor exists in `Pack/Actor`. A
   test fails for any placeable item with no actor.
2. The patch plan: from a seed's placements, per location, every file and actor `Hash` to change (all copies:
   child and adult, `Static`/`Dynamic`, `Alternative`; census `files`), the new `Drop__DropActor`, and story
   overrides removed (`GetEventName`, as round 2 showed works). The plan lists, per removed override, the story
   state it set (`03-game-data.md` and `r2-census.md` have the Kokiri Sword's); where a seed must restore it, say
   how (event flow or flag) and leave it as a finding if no data path exists yet.
3. The writer: `python -m clawshot --romfs <dump> --seed <n> --out <dir>` writes `<dir>/romfs/...` (changed files
   only, through `formats`) and `<dir>/spoiler.json`; chests only (D15); the Treasure Chest Game boxes stay
   vanilla (D17). A `dump` test reads every written file back and checks it differs from the original only where
   the plan says (field-level diff, as `E:/OOTRemake/work/r1-test/check_mod.py` does) and prints each file's size
   change.
4. Output for Kareem, outside the repo: three seeds of the Kokiri Forest / Lost Woods / Deku Tree slice in
   `E:/OOTRemake/work/r3-seed/seed-<n>/`, each with its spoiler log, and a short play note per seed (where the
   Kokiri Sword and Slingshot are). These are played from a new game, so note what a player needs to reach the Deku
   Tree (Mido's check).

### Track B: census and formats (`r3/census`)

Owns `src/clawshot/census/`, `src/clawshot/data/locations.toml`, `src/clawshot/formats/rstb.py` (new),
`tests/test_census*.py`, `tests/test_rstb*.py`, `plans/rounds/r3-census.md`, and a new section 11 of
`plans/03-game-data.md`.

1. Gold Skulltulas: link the 97 that keep their N64 checks to their OoT Randomizer names (area, room, position
   and the guide facts in `03-game-data.md` section 9; the guides' text is in `E:/OOTRemake/work/r3/`, local
   only). Mark the 3 gone ones for track C (post their OoT Randomizer names) and give the 3 new ones readable
   names. List what you could not link and why.
2. The Treasure Chest Game reward chest: a field or kind that lets the generator shuffle it while the 11 game boxes
   stay vanilla (D17). Post what you chose.
3. `formats/rstb`: read and write the resource size table (`System/Resource/ResourceSizeTable.Product.111.
   Nin_Ounce_NVN2.rsizetable.zs`, round 1 track C found the game opens it), with a function giving the entry a
   changed file needs (the formula in `03-game-data.md`; check it against the table for every Banc file and report
   any that don't fit). Synthetic tests and a `dump` round-trip test. Post when it is on your branch: track A uses
   it.
4. Freestanding major items: find an actor that can show a major item lying in the world without the crash round
   2 hit with `Obj_Arrow_Fire` (section 10): compare its actor pack and placement (its `AiGroups` logic module)
   with `Obj_Rupee_Red` and the other `Obj_` pickups; then make test mod folders (outside the repo,
   `E:/OOTRemake/work/r3-census/`) for the Lon Lon Ranch tower heart piece, which Kareem has a save right before
   (`E:/OOTRemake/work/save-backups/2026-11-07_llr-tower-before-pickup`). Also say whether a red rupee placed
   over a heart piece saves a flag (the save reader on his copies: section 10 says neither Hash was set after the
   pickup).

### Track C: world port (`r3/world`)

Owns `src/clawshot/world/`, `src/clawshot/data/world/`, `tests/test_world*.py`, `plans/04-world-format.md`,
`plans/rounds/r3-world.md`, `NOTICE`.

1. Port the rest of OoT Randomizer's world (overworld and every dungeon, vanilla dungeon layouts) with the
   translator; credit the files in `NOTICE`.
2. The remake's differences, as overrides kept apart from the translated files (round 2's finding): the
   requirement changes and N64-only checks in `03-game-data.md` sections 5 and 9 (Gold Skulltulas that need the
   Megaton Hammer or the Hookshot now, the swapped Great Fairies, the gone Gold Skulltulas once track B posts
   them), and each dungeon's key count and key locations from the census (the Water Temple has 4 keys in chests
   against OoT Randomizer's 6). List each override with its source.
3. The vanilla placement is beatable (the beatability search on the vanilla world), and 200 seeds with the
   default settings are beatable, as tests.
4. Every OoT Randomizer location of a type the census covers either has a remake ID or an `n64_only` reason (the
   round 2 test, now over the whole world); the pending list it prints goes in the round file.

### After round 3

Kareem plays track A's mini-seeds and track B's freestanding test. Round 4: the whole-game seed (track A's writer
over track C's world), event gifts (EVFL), and the size table written by the patch.

**Round 3 result (2026-11-07):** census, size table, world port and seed writer merged. In game: freestanding Hylian
and Deku Shields work (`03-game-data.md` section 11). Seed 3 was **not beatable**: the Slingshot was in the Deku Tree
basement chest, and in the remake the Slingshot is needed to leave the Slingshot room and to climb to the top floor
(from where the basement opens), which OoT Randomizer's N64 logic doesn't require. OoT Randomizer's dungeon logic
can't be trusted for the remake until each area is checked against the remake.

