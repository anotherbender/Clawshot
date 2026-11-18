## Round 2 (M1 census and the generator's engine)

Two tracks, launched while round 1 track C finishes. Bermuda thread `cs-r2`. Each track writes
`plans/rounds/r2-<track>.md`. Read `plans/03-game-data.md` first: it is the map of the data.

### Track A: census (`r2/census`)

Owns `src/clawshot/census/`, `src/clawshot/data/locations.toml`, `tests/test_census*.py`,
`plans/rounds/r2-census.md`. Uses `clawshot.formats` (byml, zsdic) as it is on `main`; if it needs a change there,
post on the thread.

1. `clawshot.census.scan(romfs) -> list[Location]`: every placement check in the game. A `Location` has `id` (the
   actor `Hash`), `kind` (`chest`, `treasure_game_box`, `gold_skulltula`, `freestanding` (heart pieces, small
   keys), `heart_container`, `scrub`, `shop_slot`), `area` (Banc folder), `room` where the data has one, `files`
   (every placement file holding that `Hash`), `ages` (child, adult or both), `position`, `vanilla_item` (actor
   name), `event` (`GetEventName` override or none) and `has_save_flag` (a `Bool64bitKey` with that `Hash` in
   `GameDataList`). Excluded by decision: trap chests, pedestals, `DreamWorld`, cows (D10-D12). Event gifts are not
   in this round (they need EVFL).
2. `src/clawshot/data/locations.toml`: the committed definitions (D5): `id`, `kind`, `area`, `name` (a readable,
   unique name), `vanilla_item`, and `oot_randomizer_name` where one N64 check is the same check (OoT Randomizer
   `LocationList.py`, MIT, cite the commit). Match by area, kind, vanilla item and room/order; leave
   `oot_randomizer_name` empty where unsure and list those in the round file. A tool writes the file from the dump;
   names may be edited by hand afterwards. A `dump` test checks the file and `scan()` agree (same IDs, kinds,
   vanilla items).
3. Counts in the round file per kind and area, against `03-game-data.md`; OoT Randomizer checks with no match here,
   and checks here with no match there.
4. In-game test outputs for Kareem, outside the repo (`E:/OOTRemake/work/r2-census/`), one mod folder each, with
   where to go and what he should see, for a new game:
   - **Freestanding item:** a freestanding Heart Piece reachable early by child Link, with its actor (`Gyaml`)
     changed to another pickup. Make two variants: a rupee pickup the game already places in the world, and a
     major item (find which actor, if any, the game uses for a major item lying in the world; say what you found).
     Its `Hash`, and so its save flag, stays.
   - **Story override removed:** the Kokiri Sword chest holding `TBox_Rupee_Red` with its `GetEventName` removed,
     so the default open event plays. Note in the round file what story state `Get_StoneOfForest_GetSword` sets
     (from the research's event-flow notes), since a seed must still set it.

### Track B: world engine (`r2/world`)

Owns `src/clawshot/world/`, `src/clawshot/generate/`, `src/clawshot/data/world/`, `tests/test_world*.py`,
`tests/test_generate*.py`, `plans/04-world-format.md`, `plans/rounds/r2-world.md`, and `NOTICE` (for OoT Randomizer
credits).

1. `plans/04-world-format.md` and its loader: regions, exits, locations and events in data files, with requirements
   in a small rule language (items and counts, age, time of day, events, helper rules defined in data). Pick the
   rule syntax so OoT Randomizer's region JSON (`data/World/*.json`, MIT) translates mechanically; write the
   translation tool rather than translating by hand.
2. Reachability: from a start state, the regions and locations reachable for each age, with age changes through
   the Temple of Time as an event.
3. The fill: OoT Randomizer's assumed fill (restricted items first, then progression, then the rest), seeded with
   `random.Random(seed)`, and the beatability search (`01-architecture.md`) run on every seed. Spoiler log as JSON
   (seed, settings, placements, the sphere order). Determinism test: same seed and settings give the same bytes.
4. Tests on synthetic worlds built in the tests (no game data): a world that is beatable, one that is not, key
   doors, an item reachable only as adult, every seed of 200 beatable.
5. Port OoT Randomizer's regions for Kokiri Forest, the Lost Woods and the Deku Tree with the tool from item 1
   (credit the files and commit in `NOTICE`). Locations stay under their OoT Randomizer names; track A's
   `oot_randomizer_name` links them to the remake's IDs. After track A's `locations.toml` is on `main` (Claude
   will tell you): a test that every OoT Randomizer location in the ported regions either has a remake ID or is
   listed as N64-only in `03-game-data.md`.

### After round 2

Kareem runs track A's in-game outputs. Round 3: EVFL, MSBT and the resource size table (formats), event gifts in
the census, the rest of the world port with the remake's Gold Skulltula positions and key counts, and the patch
plan (what changes in which file per placement, story overrides replaced).

**Round 2 result (2026-11-07):** in game, the chest without its story event gave its rupee with no sword or
cutscene; freestanding heart pieces became red rupees (Kakariko seen, Lon Lon picked up); Fire Arrows as a
freestanding pickup crashed three times out of three (`03-game-data.md` section 10). Census (477 checks), save
reader and world engine (Kokiri Forest, Lost Woods, Deku Tree) are on `main`.

