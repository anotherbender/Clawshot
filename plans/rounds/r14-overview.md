## Round 14 (tracker; Longshot; story fixes; progressive items)

Kareem agreed, 2026-11-13, after 0.2.0 was published ("all three or four are fine ... full speed ahead"). He is not
playing today apart from the checks a track asks for, so full gates may use `CLAWSHOT_WORKERS=3`; drop to 1 whenever
`hookshot.exe` or `longshot.exe` runs. One heavy job at a time under `work/rounds/r14/gate.lock`. Four tracks,
Bermuda thread `cs-r14`, herdr-core, all on `openai-codex/gpt-6.1-sol`; Claude reviews and merges, and bumps the
version (none of the tracks does). New sections of `plans/03-game-data.md`: 46 (C) and 47 (D); A and B write none.
Shared files: `README.md` and the pack templates belong to B (other tracks post the text they need on the thread);
`src/clawshot/ui/static/*` and `ui/server.py` are shared by A and B: B changes the Game tab and Play, A adds its own
tab and files and only small hooks in the shared ones. Merge order: B, C, D, A. Hookshot's GitHub repository has
been offline since 2026-11-13; Longshot (`git.magicbean.dev/MagicBeanDev/Longshot`, GPL-3.0, a fork of Hookshot) is
the active one. GPL sources (Hookshot, Longshot, sloperinaGZ): facts only, cited, never code.

### Track A: item tracker (`r14/tracker`, issue #16)

Owns a new `src/clawshot/tracker/` package, new tracker files under `src/clawshot/ui/static/`, `tests/test_tracker*.py`,
`docs/tracker.md`, `plans/rounds/r14-tracker.md`; small hooks in `ui/server.py`, `index.html`, `app.js`; one optional
dependency in `pyproject.toml`/`uv.lock` if icon decoding needs it.
1. `clawshot.tracker`, no UI code: from a seed's output (its spoiler and settings) and a save (`clawshot.save`), what
   the player holds (tiers, songs, stones and medallions, hearts, tokens), and per dungeon the small keys held and
   found out of the seed's total, plus boss key, map and compass; checks collected per area. D38: keys per dungeon
   first. Synthetic-save tests.
2. Which save: the seed's own save folder from Play, or a folder the player picks (Longshot and emulator players);
   the newest slot, with a choice. It updates on each game save without a reload.
3. A Tracker tab, and the same page standalone for an OBS Browser Source (compact, transparent option). Spoiler-free
   by default; showing locations is opt-in.
4. Icons decoded at run time from the player's own dump (`romfs/UI/Tex/Icon`), cached outside the repository, never
   shipped; flat CSS fallback without them. Own decoder from format facts or MIT/BSD libraries only.
5. One in-game check for Kareem: play a few chests with the tracker beside the game.

### Track B: Longshot (`r14/longshot`, issues #23 and #18)

Owns `src/clawshot/pack/hookshot.py`, `pack/runtime.py`, `app/play.py`, `app/paths.py`, `app/inputs.toml`,
`app/preferences.py`, the Game tab and Play in `ui/static/*`, `README.md`, `docs/ui.md`, `docs/seed-pack.md`, the pack
templates, `tests/test_app*.py`/`test_runtime*.py`/`test_hookshot*.py`, `plans/rounds/r14-longshot.md`.
1. Detect a Longshot game folder (`bin/longshot.exe`, `bin/longshot` on Linux, its version file) and a Longshot
   Launcher folder (its newest build), as well as Hookshot; the player can choose which.
2. Play starts the chosen game with the seed as its only mod, its own `--user` folder, and that game's update check
   off. Running-game detection knows both names.
3. Docs and templates name both, with the manual steps (mods folder, a New Game in an empty slot).
4. #18, short term: a "Copy for Discord" button (the string in backticks) and the backticks advice in the docs.
5. One in-game check for Kareem: Play a seed on Longshot from the app.

### Track C: story fixes (`r14/story`, issues #21 and #22)

Owns `src/clawshot/data/fast_start.toml`, the Hyrule Field, Market and Hyrule Castle world files, the matching
`patch/gamedata.py` changes, `tests/test_fast_start*.py` and new story tests, section 46, `plans/rounds/r14-story.md`.
1. #22: from the game data, the exact conditions of Zelda's escape after the three stones; then logic that requires
   them (or a fix that makes them always met), so no seed asks for an unreachable Ocarina of Time.
2. #21: what starts Hyrule Field's music, and a Kaepora skip that leaves it working.
3. Every offered fast-start combination still generates; sweep before handoff.
4. One in-game check for Kareem covering both.

### Track D: progressive items (`r14/progressive`, issue #13; replaces D16 for these items if it works)

Owns the item pool and fill changes, the chest-event patch for progressive grants, item names, hints and play-note
text for them, `tests/test_progressive*.py`, section 47, `plans/rounds/r14-progressive.md`.
1. Feasibility first, on Hookshot then Longshot from chests: a chest event that checks what is owned and grants the
   next tier, as 0.2.0's named small keys do; whether the model and name shown follow the granted tier.
2. Then the chains Kareem confirms (provisional: Hookshot, strength, scales, wallets; bags and magic if they fit),
   in every check kind that can carry them; others keep fixed items or are restricted, and say so.
3. Logic and fill treat progressive copies as counted tiers; the fixed-tier placement rule stays for fixed items.
4. Sweep and gates; one in-game check for Kareem.

### Track E: quest-step audit (`r14/steps`, issue #25; added 2026-11-13 at Kareem's request)

Owns section 48, `tests/test_story_steps*.py`, `plans/rounds/r14-steps.md`, and fixes only in world files no other track
owns this round. Kareem: "do we need to go through the rest of the quests/Threads of Time to make sure no other steps
are gating things we don't realize yet?" Three step gates were found by players (Mido, the Gerudo guards, Zelda's
escape).
1. A scripted census of every read and write of a quest step in the romfs (AI modules, event flows, GameData
   expressions and where they are used), with what each gates.
2. Each read classified against our logic and fast-start skips; flagged: logic granting access on an item where the
   game asks for a step, and steps advanced only by a native hand-over the randomizer replaces.
3. Section 48 and a full table; a failing test and a proposed fix for each confirmed mismatch. Track C keeps the
   Zelda, Door of Time and Kaepora fixes.

### After round 14

Done 2026-11-14; released as 0.2.1 the same day (tag `v0.2.1`, `5e16847`). All five tracks merged: B (Longshot
Detect and Play, carried-over game options; #18, #23, #24), C (Kaepora music, Met Child Zelda gating Zelda's escape,
Saria and the closed Door; #21, #22), D (progressive items, always on, chest copies only, D40; #13), A (tracker and
its OBS view; #16), E (quest-step audit: Zora's River walls, Epona, the Bombchu Shop, Darunia's gift, refused
logic-only overrides; #25), plus the forward-only Fire quest writes (#27). Every in-game check ran on Longshot (D41).
Not done here: the progressive chest's rising model still shows the base tier, and several copies granted inside one
chest event read stale ownership (seeds place one copy per chest).

