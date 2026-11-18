## Round 10 (M3 more gift checks; age-travel settings; `.nup` packs; pots exploration)

Kareem agreed, 2026-11-09 ("please go ahead"); he plays seed 8 meanwhile, so one worker process at a time while
`hookshot.exe` runs (`CLAWSHOT_WORKERS=1` on every gate run). Four tracks, Bermuda thread `cs-r10`, herdr-core, all on
`openai-codex/gpt-6.1-sol`; Claude reviews. New sections of `plans/03-game-data.md`: 40 (A) to 43 (D), in number
order. Shared files as before (small isolated commits, posted). No Hookshot build.

### Track A: gift checks (`r10/gifts`)

Owns `src/clawshot/patch/gifts.py`, `patch/gift_rules.toml`, `data/world/remake/gifts.toml`, `census/gifts.py`,
`tests/test_gifts*`, `plans/rounds/r10-gifts.md`, section 40.
1. Release the seven frog checks into `--shuffle Gift` (Kareem's experiment passed, answers.md R8-FROGS): drop their
   holds; the five song prizes enter the pool as Rupees (20) (OoT Randomizer's item; the native prize varies).
2. The Market Potion Shop's child bottle (answers.md R9-SEED8-MARKET; round 4 listed it as unclear,
   `Npc_Hylia_020_Shop_Child`, entry `Item_Bottle_TutorialEvent_Talk`, section 15): trace its conditions and saved
   gate, add it to the census and as a gift check (an early bottle in logic: child, its real conditions), a swap
   patch, and a test on a save copy that has not had it, with a checklist.
3. Bombchu Bowling, deterministic as OoT Randomizer: the first win gives First Prize, the second win Second Prize,
   later wins the native filler; both shuffled under Gift (the opening stays `'Defeat King Dodongo'`). Then the
   shooting galleries' normal and expert prizes (Kareem: an expert tier exists): the same if the flows allow, else
   a report. Test outputs with checklists.
4. Dampé's gravedigging heart piece (the remake reworks the tour): trace its grant and add it as a once-only check if
   the flow allows.

### Track B: age travel (`r10/agetravel`)

Owns `src/clawshot/patch/age.py`, a new Door of Time patch module, their logic overrides and tests,
`plans/rounds/r10-agetravel.md`, section 41.
1. `free_time_travel` first-pull bug (answers.md R9-FIRST-PULL): Sheik's first adult scene plays without him. Keep the
   placed Temple Sheik while `Dm_TimeTemple_0050` has not played, and from Forest completion until the Prelude; find
   what the skipped dialogue sets (Kareem's test user `work/r9-sheik-cs9b/ingame/user-free-time-travel-next` holds the
   save after the broken scene); a test from an older child autosave.
2. D35: `door_of_time` = closed (default) | song_only | open. Trace the `DoorOfTime` flow and its gates (the stones,
   the Ocarina of Time, the Song of Time); patch song_only and open; logic for each; the settings string and CLI;
   test outputs per mode on a child save copy with fewer than three stones, with a checklist.

### Track C: `.nup` dumps in seed packs (`r10/nup`)

Owns `src/clawshot/pack/`, any NUP reader module, `docs/seed-pack.md`, the pack's `READ ME FIRST.txt`,
`plans/rounds/r10-nup.md`, section 42.
1. Make accepts a `.nup` file (the dump format Hookshot's builder, Lichii and EglantinePS5 read) as well as an
   extracted romfs folder. Use a55uka's NUP reader (MIT; a dependency if published, else vendored with its licence and a
   `NOTICE` entry). Version check first, from inside the `.nup`. Generation reads either source (a read-through layer,
   or a pack-local cache of only the files it needs, on the tester's own disk and never in a zip). Tests with a
   synthetic `.nup` fixture (no game data in the repository); a real read-only check against Kareem's `.nup` in
   `E:/Games/Hookshot`. Docs and the readme updated.

### Track D: pots and loose rupees (`r10/pots`, exploration)

Owns `plans/rounds/r10-pots.md`, section 43, any new `src/clawshot/patch/pots.py` and its tests.
1. Census the remake's pots, crates and loose (ground) rupees: actors, how a pot's drop is set, counts per area, and
   OoT Randomizer's names for them where they exist.
2. Find whether a pot or loose rupee can give a shuffled item through the game's own pickups (as round 8's boss hearts
   and floor heart pieces do, D33), and which items.
3. If it can: a `Pot` (and rupee) shuffle type behind the settings string, logic from OoT Randomizer's pot and rupee
   locations, tests and a test output with a checklist. If not: a report of what blocks it. Another randomizer
   (Lichii Discord) shuffles pot drops; its zip has no licence: never open, read or use it.

### Round 10 Track D result (merged `5653956`, docs only)

Pots (530), crates (50), ground rupees (112) and floor recovery hearts (25) censused (section 43,
`plans/rounds/r10-pots.md`). Kareem's tests: ground rupees and their replacements grant cleanly (Kokiri Piece of
Heart, grotto Hylian Shield); a pot's drop can be any native pickup, but a thrown pot drops where it breaks (a Piece
of Heart stranded on a tree, lost), and the game records only the pot's destruction, not the drop's collection.
Later-round candidates: (1) `Rupee` and `RecoveryHeart` shuffle types (all saved permanently, reset24, NoRespawn;
names: remake positions and regions, OoT Randomizer names only where exact; Saria's house has separate child and
adult hearts, so decide 7 or 14 checks); still to test: return and Save and Continue repeat steps. (2) Pots and
crates only with a per-pot D22 Bool set on collecting that pot's own drop, recoverable delivery (placed position or
direct grant), and ideally a marked pot model (eight native models exist; contrast unchecked), as Kareem described
Ship of Harkinian doing. No seed switch shipped.

### Round 10 result (2026-11-10)

All four tracks merged; main `809b421`. Last full review gates (track C, on top of A, B and D): 816 passed / 110
skipped, dump 109 (with `OOT_NUP`).
- A gifts: the seven frog checks, deterministic Bombchu Bowling (first win, second win, then filler) and the normal
  shooting-gallery prizes are in `--shuffle Gift`. Held until Kareem's tests pass (D15): the Market Potion Shop
  bottle (first build crashed on re-entry, R10-MARKET-BOTTLE; `market-bottle-fix-next` untested), Dampé's digging
  reward, the first expert gallery wins (Rupees (20), Kareem's choice). Launchers in `work/r10-gifts-cs10a/ingame`.
- B age travel: `free_time_travel` first-pull fix confirmed in game (R10-FIRST-PULL-FIXED). `door_of_time` =
  closed (default, D35) | song_only | open, with logic; all three passed a first in-game check on
  2026-11-10 (answers.md R10-DOOR-*); the early Zelda escape after an early pull is still untested. Adult
  songs now need the Ocarina of Time (from the item-bar age table, not an in-game test); seeds 8 and 10 re-checked
  beatable under it.
- C `.nup`: Make reads a `.nup` dump or a romfs folder; a55uka's reader vendored (MIT, `NOTICE`). The cache list is
  data (`pack/resources.toml`) and a dump test builds every shuffle kind and setting from the cache alone (16 rows,
  door modes included), naming any missing input.
- D pots: docs only, see "Round 10 Track D result".
- From play: the Goron City sign-puzzle solution chest is shuffled, its failure chest stays vanilla (`1432705`;
  165 of 184 chests shuffled). Test launchers enable Hookshot's cheat Teleport (`c3a5c0a`).

### After round 10 (candidates, not started)

- Going public (Kareem, 2026-11-10: "the right move once we clean things up"; his commit email stays as is). One
  docs track: README rewritten for newcomers (it still says "Day-1 spike" and "private tester packs"),
  `CONTRIBUTING.md` (MIT inbound, no game files or game-derived output, AI use disclosed, no unlicensed sources, how
  to run the gates), issue templates and a PR checklist, `docs/logic.md` for porters (world data, rule language,
  location IDs; an Archipelago port also needs a client that delivers items during play, which a RomFS mod cannot
  do), another randomizer author's name removed from this file. Then Kareem flips visibility; `main` protected;
  Greenferret added when he returns.
- Keysanity (Kareem, 2026-11-10; section 44 and R11-KEY-* answers). Played: a generic key
  outside a dungeon is lost; in keyless Deku or keyed Fire it credits that dungeon, including
  a native big chest and persistence on reload. The default own-dungeon mode therefore has
  plain-key evidence for both chest sizes. Named Forest writes from child/adult overworld
  small chests persist and open a native Forest lock; the later native key still counts.
  The named big-chest redirect in Deku **failed before opening**, not a generic-big-key failure.
  `--dungeon-items anywhere` remains refused by CLI/seed pipeline; settings/fill retain it.
  It still needs **(1)** a working named big-chest path plus the cross-dungeon pickup test,
  **(2)** pickup text identifying the target (English in every language, English dungeon names
  read from the dump at generation, never shipped), **(3)** the D38 Tracker tab reading the
  seed's own save. Arbitrary source binding and other named dungeon-item families remain
  outside these small-key proofs; no production keysanity release is claimed.
- A fresh public seed pack from merged main (seed 10's zip predates round 10; `.nup` support needs a new pack).

