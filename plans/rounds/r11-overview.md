## Round 11 (going public; Hookshot 2.0.12+ loading; keysanity exploration; a UI base)

Kareem agreed, 2026-11-10 ("Yes please, go ahead", and asked for a UI base a contributor can build on,
cross-platform and close to Hookshot's interface). He tests and plays meanwhile: one worker process while
`hookshot.exe` runs, `CLAWSHOT_WORKERS=1` on every pytest run, the gate lock `work/rounds/r11/gate.lock` around full
gates. Four tracks, Bermuda thread `cs-r11`, herdr-core, all on `openai-codex/gpt-6.1-sol`; Claude reviews. New
sections of `plans/03-game-data.md`: 44 (B) and 45 (C); A and D write none. Shared files this round: `README.md`
belongs to A (other tracks post the text they need there on the thread); `docs/seed-pack.md` and the pack templates
to C; `pyproject.toml` and `uv.lock` to D. Test launchers: copy `E:/OOTRemake/tools/test-launcher-template.bat`
(outputs load as a mod, `plans/02-orchestration.md`), never an older launcher. No Hookshot build.

### Track A: going public (`r11/public`, documents only)

Owns `README.md`, `CONTRIBUTING.md`, `.github/`, `docs/logic.md`, `docs/settings.md`, `plans/rounds/r11-public.md`.
1. `README.md` for a newcomer: what Clawshot is and is not (unofficial, no game files, the player's own dump); status
   (what is shuffled today, only what is verified; what is built but held for in-game tests; known issues); playing a
   seed pack (link `docs/seed-pack.md`; Hookshot and emulators); running from source (uv, the commands, settings
   strings); how it is built (AI coding agents directed by Kareem, every change tested in game by him); contributing;
   the Discord invite `https://discord.gg/7R5ZXPcJqn`; credits (`NOTICE`) and licence. The "Day-1 spike" status and
   "Private tester packs" section go; the developer reference now in the README moves to `docs/settings.md`, not
   deleted.
2. `CONTRIBUTING.md`: contributions are MIT (inbound = outbound); no game files or anything generated from the game in
   a PR, issue or attachment (AGENTS.md rule 1); no code from GPL or unlicensed projects and none from NX2navi (rule 7);
   AI assistance is fine and is disclosed (`Assisted-by:` trailer); small single-topic PRs; the gate commands; what
   in-game evidence a behaviour change needs; where to ask. Kareem and his co-owner merge.
3. `.github/ISSUE_TEMPLATE/` (bug report: seed and settings string, runtime and version, where, expected and seen, the
   log; logic question; `config.yml` pointing to the Discord) and `.github/PULL_REQUEST_TEMPLATE.md` (the checklist).
4. `docs/logic.md` for someone porting the logic (an Archipelago world, a tracker): the world data files and remake
   overrides, the rule language, items, settings, location IDs, how a seed is proved beatable, the spoiler's fields,
   each statement with the path it comes from. Say what a multiworld port would still need: items delivered during
   play, which a RomFS mod cannot do without a hook in the runtime.
5. Housekeeping before the flip: the other randomizer author's name leaves `plans/00-roadmap.md` ("another
   randomizer"), one small commit; a scan of the tree for third parties' names or handles and for anything that
   should not be public, reported in the round file (history is not rewritten; Kareem keeps his commit email).

### Track B: keysanity exploration (`r11/keys`)

Owns `plans/rounds/r11-keys.md`, section 44, any new `src/clawshot/patch/keys.py` and its tests.
1. Trace, read only: where each dungeon's small-key and boss-key state is saved, what picking up
   `Item_Dungeon_SmallKey` and `Item_Dungeon_BossKey` writes (the dungeon Link stands in, or a named one) and what the
   locked doors read; the same for maps and compasses.
2. In-game experiments for Kareem (template launcher, checklists): a small key in an overworld chest, one in a chest
   of a dungeon that has no keys, one in another dungeon's chest; which counter moves, if any, and whether the item is
   lost. Choose saves from the save library by reading their flags.
3. If an event or saved-flag write can credit a named dungeon (as the gift patches write flags), prototype one
   per-dungeon key grant in a chest with a test output; otherwise report what blocks it.
4. Until an in-game test passes, building a seed with `dungeon_items = "anywhere"` stops with a message that says why
   (at the CLI and seed pipeline; the fill and its synthetic tests keep the mode).

### Track C: loading in Hookshot 2.0.12+ (`r11/loader`)

Owns `src/clawshot/pack/` (code, templates), `docs/seed-pack.md`, `plans/rounds/r11-loader.md`, section 45.
Facts: answers.md R11-HOOKSHOT-2012. Hookshot's release source is at
`C:/Users/hi/AppData/Local/HookshotBuilder/versions/<version>/HookshotBuilder/tools/` (GPL-3.0: read `host/mods.c` and
`host/prompts.c` for facts, cite them, never copy code).
1. The pack's Play starts the game with `HOS_MODS` (and `HOS_FS_OVERLAY` cleared) so that Hookshot sees exactly one
   mod, the made seed: no links, no second copy of the seed, and neither the `.nup` cache nor any other pack folder may
   count as a mod under Hookshot's rules (a test walks a made pack folder by those rules). A Hookshot without mods
   support must stop Play with a message, never start a vanilla game silently. Emulator steps stay as simple as now.
2. `READ ME FIRST.txt` and `docs/seed-pack.md`: the new known issue (button icons in text are the game's own while a
   seed is loaded); the Hookshot `mods` folder as the manual route and its warning (it uses the main save folder: a
   new game there overwrites the playthrough).
3. Smoke, no game start: a pack built from the romfs and from the `.nup`, Make on each, Play as a dry run printing
   what it would start; the digest unchanged by this track.
4. Report only: what Hookshot would need so a mod's size table keeps the controller icons (a candidate upstream PR).

### Track D: a UI base (`r11/ui`)

Owns `src/clawshot/app/`, `src/clawshot/ui/`, `tests/test_app*.py`, `tests/test_ui*.py`, `docs/ui.md`,
`plans/05-ui.md`, `plans/rounds/r11-ui.md`; `pyproject.toml` and `uv.lock` for one optional extra.
Toolkit (decided by Claude, 2026-11-10; Kareem can overturn): a local web front end, plain HTML, CSS and JavaScript
with no build step, served by a standard-library HTTP server on 127.0.0.1 and shown in an app window through
`pywebview` (BSD-3-Clause, optional extra `ui`) or, without it, the default browser. Reasons: rule 7 excludes Qt
(PySide6 is LGPL), HTML and CSS can follow HookshotBuilder's look closely and are what a UI contributor most likely
knows, and it runs on Windows, Linux, macOS and Steam Deck. Hookshot's own builder is WPF on Windows, with a PySide6
port and a tkinter Linux builder in its repository (GPL-3.0): the look comes from Kareem's screenshots, never from
Hookshot's code, XAML, images or logo.
1. `clawshot.app`, no UI code: a schema of every setting (key, label, kind, choices, default, help, group) built from
   `Settings` and `data/settings.toml`, so no front end hard-codes a setting; validation; the settings string both
   ways; detection of a dump (romfs folder or `.nup`) and of a Hookshot folder and version; a generation job that
   runs off the UI thread with progress stages, cancel and the fill's error text. Unit tests on synthetic worlds.
2. `python -m clawshot.ui`: one window in the manner of Hookshot's in-game menu (Kareem, 2026-11-10, after the first
   renders in the builder's slate look: "match the in-game menus a bit ... style close and remain clean overall"). A
   tan top band with tabs (Game, Settings, Generate), a dark-brown panel of label-and-value rows, amber section
   headers and focus, a description panel that shows the focused row's help text from the schema, a cards grid for
   what to shuffle, a key-hint bar; keyboard and mouse. Flat colours and CSS only: nothing from the game's art or
   fonts, no code or image from Hookshot (GPL-3.0); system font stacks; every asset local, no network request. The
   look's brief with Kareem's reference pictures is `E:/OOTRemake/work/rounds/r11/ui-look.md`. Paths are picked with
   a Browse dialog; a detected Hookshot folder fills in the dump; unavailable options are shown dimmed with their
   reason; plain titles, no slogans.
3. Safety: 127.0.0.1 only, a random port and a per-run token on every call, no cross-origin access, only the UI's own
   static files served, paths validated.
4. Tests through the HTTP server on a synthetic world; the schema test fails for a setting without metadata. Review
   screenshots of each screen from a headless browser into `E:/OOTRemake/work/r11-ui-cs11d/shots/`; no window may
   open on Kareem's screen (a `--no-open` switch; tests never open one).
5. `docs/ui.md` and `plans/05-ui.md`: the architecture, the calls, how to add a setting or restyle, what is not done:
   the base a contributor starts from.

### Track E: release the tested gift checks (`r11/release`; added 2026-11-10 after Kareem's gift tests)

Owns the two entries named below in `src/clawshot/data/world/remake/gifts.toml`, the tests that pin them,
`src/clawshot/pack/resources.toml` if the release reads files the cache lacks, the status lines about these two checks
in `README.md`, `docs/settings.md`, `docs/discord/server-kit.md` and `src/clawshot/pack/templates/READ ME FIRST.txt`,
`plans/rounds/r11-release.md`, and one new subsection at the end of section 40.
Facts: answers.md R10-MARKET-BOTTLE-FIX and R10-DIGGING (both confirmed in game), R10-MINIGAMES-ADULT (confirmed),
R10-MINIGAMES-CHILD (not run yet); section 40; `plans/rounds/r10-gifts.md`.
1. Release (D15) "Market Potion Shop Bottle" and "Graveyard Dampe Gravedigging Tour": remove their `keep_vanilla`
   holds, so `--shuffle Gift` shuffles both. The generator must write the patch Kareem tested and no other: build
   each with the placement of its test (Boomerang) and compare the changed flow files, decompressed, with the tested
   ones in `E:/OOTRemake/work/r10-gifts-cs10a/ingame/mods/market-bottle-fix-next/` and `.../digging-next/` (read
   only). A difference is reported in the round file and that check stays held.
2. Logic: with the bottle shuffled the early fixed bottle is no longer assumed; without Gift shuffle the model of
   section 40 stays. One sweep under the gate lock (seeds 1 to 50, seed 8's settings string and the default
   settings, at most one worker while the game runs): every seed beatable; report the check counts before and after.
3. Names, hints, play note: both locations keep their player-facing name and "where"; the hint classes cover them;
   a test fails if either is missing from the names catalogue.
4. Packs: the dump test that builds from the `.nup` cache alone covers both patches (it names any missing input).
   Seed 8 and seed 10 packs already built are pinned to the source they ship and are not rebuilt.
5. Status wording in the documents this track owns: both checks become shuffled with Gift and confirmed in game,
   with their answers ids.
Not in scope, still held or pending: the first expert gallery wins (untested), the bowling prizes and the child
gallery prize (enabled, Kareem's child test pending), the merchant experiments, Skulltula House rewards.


