## Round 4 (remake logic, fast start, event flows)

Four tracks. Bermuda thread `cs-r4`. Tracks run in herdr-core (`hc`), not old herdr panes. Each track writes
`plans/rounds/r4-<track>.md`.

### Track A: remake logic, child areas (`r4/logic-child`)

Owns `src/clawshot/world/load.py` (item 1 only), `src/clawshot/data/world/remake.toml`,
`src/clawshot/data/world/remake/` (new), `tests/test_world_remake*.py`, `plans/rounds/r4-logic-child.md`, and
section 12 of `plans/03-game-data.md` (child areas).

1. First, small, its own commit, posted: the loader also reads every `src/clawshot/data/world/remake/*.toml` after
   `remake.toml` (sorted by name; a location or exit set in two files is an error), so the two logic tracks write
   separate files. Claude merges it early.
2. Deku Tree, from seed 3: the Slingshot is needed to leave the Slingshot room and to reach the top floor. Model it
   (overrides with `source`), add a test that a Slingshot in the basement chest is not beatable, and say in the
   round file how a player who enters the Slingshot room without it gets out (Kareem is asked whether reloading
   puts him at the dungeon entrance); if he can't, the room must not be a trap: propose the rule.
3. Then every child-reachable area: Kokiri Forest, Lost Woods, Sacred Forest Meadow, Hyrule Field, Lon Lon Ranch,
   Market, Hyrule Castle, Kakariko, Graveyard, Death Mountain Trail and Crater (child side), Goron City, Zora's
   River, Domain and Fountain, Lake Hylia, and the dungeons Deku Tree, Dodongo's Cavern, Jabu-Jabu's Belly, Bottom
   of the Well, Ice Cavern. For each OoT Randomizer rule, check it against the remake: published remake
   walkthroughs and guides (cite each URL; facts only, no copied text), the census and `03-game-data.md`, and the
   placement data where it settles a question (a target, ladder, block or door in the Banc files). Write overrides
   in `src/clawshot/data/world/remake/child_<area>.toml`, each with `source`.
4. The round file lists per area: rules checked and unchanged, rules changed (with source), and what could not be
   settled from sources (a question for an in-game check, in **bold**).
5. Remake the three mini-seeds (`E:/OOTRemake/work/r4-seed/seed-<n>/`, the round 3 command with the new logic) once
   item 2 is in, with play notes, and check each is beatable under the new rules.

### Track B: remake logic, adult areas (`r4/logic-adult`)

Owns `src/clawshot/data/world/remake/adult_*.toml`, `tests/test_world_remake_adult*.py`,
`plans/rounds/r4-logic-adult.md`, and section 13 of `plans/03-game-data.md` (adult areas).

Track A's item 3 for the adult side: the Forest, Fire, Water, Shadow and Spirit Temples, Gerudo Training Ground,
Ganon's Castle and Tower, Gerudo Valley and Fortress, the Haunted Wasteland, Desert Colossus, Death Mountain
Crater (adult side), and adult-only rules in the shared overworld areas. Same sources, same output, files named
`adult_<area>.toml`. Until track A's loader change is on main, test with it applied locally; don't commit it.
The Water Temple's key count already differs (`03-game-data.md`).

### Track C: fast start (`r4/fast-start`)

Owns `src/clawshot/patch/gamedata.py` (new), `src/clawshot/data/fast_start.toml` (new), `tests/test_fast_start*.py`,
`plans/rounds/r4-fast-start.md`, and section 14 of `plans/03-game-data.md`.

1. What a new game sets and plays before the player has control: the initial values in
   `GameData/GameDataList.Product.110.byml.zs` (big-endian BYML, read and written by `formats.byml`), the event
   flows that run (`HavePlayedEvent.*` flags), and which flags gate the opening cutscenes (the intro, Navi waking
   Link, the Deku Tree's talk, Mido's block, Zelda's courtyard, Kaepora Gaebora). The save reader on Kareem's save
   copies shows which flags a played game has set.
2. A patch that changes `GameDataList`'s initial values so a new game skips the intro (and, as separate settings,
   the other cutscenes found, each named in `fast_start.toml` with what it skips and what state it must still set).
   Default: skip the intro only. A dump test that the written file differs only in the chosen entries.
3. Test outputs for Kareem, outside the repo (`E:/OOTRemake/work/r4-fast-start/`): skip the intro alone, and the
   intro plus the others found, each with what he should see on a new game.

### Track D: event flows and gifts (`r4/evfl`)

Owns `src/clawshot/formats/evfl.py` (new), `src/clawshot/census/` (gifts), `src/clawshot/data/locations.toml`,
`tests/test_evfl*.py`, `tests/test_census*.py`, `plans/rounds/r4-evfl.md`, and section 15 of `plans/03-game-data.md`.

1. `formats/evfl`: read and write `.bfevfl` event flows (our own implementation from the format; no code from the
   GPL evfl library, which round 1's scripts used: don't read its source). Round-trip every flow in the dump
   byte-identical or tree-equal (say which), in a `dump` test.
2. The census of gifts: every flow step that gives an item by name (round 1 found the pattern; `03-game-data.md`
   section 3), as locations of kind `npc_gift`, `song`, `event_gift` with the flow, entry and step, the vanilla
   item and the OoT Randomizer name where it is the same check. Count them against OoT Randomizer's NPC, song and
   cutscene checks.
3. How a gift's item would be changed in the flow (the step's item name, the text it shows), as a finding with one
   example written to `E:/OOTRemake/work/r4-evfl/` for a later in-game test; no seed writes flows yet.

### After round 4

Kareem tests the mini-seeds on the corrected Deku Tree logic and the fast-start outputs. Round 5: whole-game
chest seeds over the checked logic, gifts through the flows, and in-game checks for the logic questions.

Engine questions from track B for round 5 (`plans/rounds/r4-logic-adult.md`): (1) the Forest Temple walkthrough
says the remake lets adult Link return to child only after the Forest Temple; the search shares one inventory
across ages and can't tell an adult-found item used as child before that, so it needs an age-travel model, not a
data gate; (2) Great Fairies: settled from the data by track A's item 6 (`03-game-data.md` section 12): Din's
Fire opens the other five, fees are fixed per fairy, wallets hold 200/500/1000, every magic item carries the
magic meter. The adult rules keep conservative routes where the remake is
unproven (stricter than the game, never looser); their in-game questions are in bold in the round file.

**Round 4 result (2026-11-08):** all four tracks merged (`main` 7a46b04; 297 tests, 25 dump tests). Every child
and adult area checked against the remake (track A 125 changed rules over 21 child areas plus the Deku Tree; track
B the adult areas and temples, the phantom Fire Temple key removed); fast start passed in game (D18); EVFL
reader/writer and the gift census (148 gift steps). About 85 logic questions only play can answer, kept with
stricter rules until then. Round 5 (Kareem agreed, 2026-11-08): the age-travel model, Deku Shield and shops
(D19), whole-game chest seeds, gifts through the flows, an organised in-game logic session; most tracks on
`openai-codex/gpt-6.1-sol`, Opus for one track and for review.

