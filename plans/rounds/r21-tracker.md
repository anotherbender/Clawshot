# Round 21 track tracker (cs21a): Checks tab, click-to-toggle states, no-save state, leaner OBS

Branch `r21/tracker`, started from `e9bb0d7`. Brief: Kareem's notes from his first 0.2.5 seed
(`E:/OOTRemake/work/rounds/r21/tracker-ui-notes.md`, tracker part only) and Claude's round-21 prompt. No game
behaviour changes: READY kind is merge; Kareem reviews the screenshots below, then uses it on his seed.

## What is built

All in `src/clawshot/ui/static/` (`tracker.js`, `tracker.css`, the app's `index.html` markup, one line of
`app.js`, one colour token in `style.css`) plus `docs/tracker.md` and the Node UI tests. No backend file changed
yet (see "Skip" below).

1. **Checks tab.** A fifth screen, `Checks`, after `Tracker` (Q/E cycle through it). The Tracker tab keeps the seed
   and save controls, the OBS controls, keys, collection and items; the check list moved to Checks.
   - Areas flow in CSS columns of at least 300 px: 2 columns at 1280 wide, 3 at 1920 (measured below), instead of
     the old 175 px grid (3 at 1280, 5 at 1920).
   - Each area heading is a button: click folds the area; **Collapse all** / **Expand all**; folded areas are
     remembered in this browser (`clawshot.tracker.collapsed`).
   - **Show**: All checks (default) / Open checks / Open and in logic (replaces the "Show only in-logic"
     checkbox); **Hide finished areas** hides an area whose every row is collected, marked or skipped. Both are
     remembered in this browser.
   - **In logic for** (Either age / Follow save / Child / Adult) and **Vanilla pick-ups** moved from the top of
     the Tracker tab to the Checks toolbar, beside the list. **Clear manual marks** is now **Clear my marks**.
   - The side panel shows the pointed-at or focused check (sticky until another row is pointed at): title (our
     readable name), our own `where` text (the spoiler's copy of `location_names.toml`), then State, In logic
     (per-age wording: both ages, child only, adult only, "needs a trip between ages", or out of logic, plus a
     short "may be conservative" note when the save left items unread), Save (how the save tracks it, or the
     reason it can't), Area, Kind, Item (only when collected or in spoiler mode, or a vanilla row's usual item)
     and what a click does. No text from any other tracker. The Checks section has no `data-help`, so app.js's
     hover help never overwrites the selection; `#check-details` in the aside is filled by tracker.js and hidden
     whenever the Checks screen is (a MutationObserver on the screen's `hidden`).
2. **States without prefixes.** Rows lost the `✓ ☑ — ?` prefixes and the Mark done / Unmark buttons. Each row is a
   button with a CSS-only marker (no font glyphs or art): filled green = collected (save), filled amber = marked
   done by you, struck grey = skipped by you, green ring = open in logic, dim ring = open out of logic, dashed ring
   = the save can't show it. A legend above the list says the same in words and how clicking works. Clicking a
   row the save can't read (`markable`, PR #39's field, falling back to `collected == null` before #39) marks it
   done; clicking again undoes. Rows the save reads are clickable only when the entry says `skippable`, and then
   send `{check, marked, kind: "skip"}` (contract below). Marks still go through `tracker-mark` and the existing
   marks file. "All checks" brings back a row that "Open checks" hid after a misclick (shown in the screenshots).
3. **No-save state.** While the session status is `waiting` or `no_save_folder`, the Tracker tab replaces keys,
   collection and the item grids with a **No save loaded yet** card naming the watched folder (the duplicate
   waiting warning is dropped); the Checks tab lists the seed's checks plainly with a "No save loaded yet" line,
   no legend, no in-logic styling or notes, and nothing clickable (the backend refuses marks then anyway).
4. **Leaner OBS.**
   - Cells keep a 1 px outline in a faint token (`--outline-faint`, `#6d593b73`) and lose the tile background.
   - Dungeon rows draw only the items the dungeon has in this seed (`has_boss_key`, `has_map`, `has_compass`,
     small keys where the seed total, held or found count is above 0); an empty slot keeps the columns aligned.
     52 cells became 35 on the fixture. The app's key table leaves those cells blank too.
   - Dungeon names: new fragment option `names=short|full|none` and an **OBS dungeon names** select (Short /
     Full / Hidden). Missing or unknown values are `short`. Short names: Deku, Dodongo, Jabu, Forest, Fire, Water,
     Shadow, Spirit, Well, Ice, GTG, Ganon, Fortress (full name stays in the tooltip). Compact width 280 -> 236 px
     (short) / 193 px (hidden).
   - Before any save, OBS draws a new game's empty inventory (dim cells, no dashed outlines, no `?` badges: 126
     before, 0 after) with one "No save yet" line. With a save, a genuinely unread field stays dashed with `?`.
   - Missing items carry no tier/count badges (the stray "0" tier badges), and a held-keys badge of 0 is gone; with
     an icon, the key cell's found/total moved into its bottom-left corner so key cells are as tall as the others.

## Skip (Kareem: "a windmill rupee, a vanilla graveyard heart piece he doesn't want")

Proposal posted 16:39; Claude approved it at 16:40 and moved ownership of `tracker/state.py`, `marks.py`,
`saves.py` to this track once #39 merges ("build the skips backend then, on your branch").

- Marks file: a `skips` table beside `marks`, same seed-identity / save-folder keys; an old build ignores it.
- `TrackerSession.skip(check, on)` for a check the save reads; skips are never auto-dropped by a save read.
- Entries: `skipped: true`; a skipped check leaves the open set (no `in_logic`, out of the area `in_logic` counts);
  `skippable: true` on the checks a skip is offered for.
- `POST tracker-mark` takes `kind: "skip"`; `tracker-clear-marks` clears both tables; OBS strips both.
- The UI side is built and tested against that contract with synthetic snapshots
  (`test_a_check_the_save_reads_can_be_skipped_when_the_backend_offers_it`). Backend: waiting for MAIN MOVED #39.

## Choices made here (cs21a, provisional)

- Row click toggles; pointing (hover or keyboard focus) selects for the side panel. Clicking a row that has no
  action only selects it.
- "Show" defaults to All checks, so nothing disappears on the first click.
- Area counts are computed in the page from the rows ("8 / 23 done · 5 in logic"), so marks and skips count at
  once; vanilla rows count with their area (the old separate "vanilla 0 / 1" part is gone).
- OBS area counts (labelled, all sections) stay as before: `collected / total`.
- Short dungeon names are the default for every OBS URL, labelled or not.
- `plans/tracker-in-logic.md` (BBender's spec) still names the old controls ("Show only in-logic", Mark done,
  Unmark, Clear manual marks); left unedited as his design record. Its behaviour stands: the controls moved to
  the Checks tab under the names in item 1. `docs/tracker.md` is updated.

## Questions for Kareem

From the "Ideas to put to Kareem" list in his notes (each is his call; the parts below marked built were in
Claude's build list for this round):

- **No-save state (built): is the "No save loaded yet" card what you wanted, or should the Tracker tab still draw
  the empty key table and item grid under it?**
- **Checks tab (built) with the whole row as the toggle (built, from your own note "clicking a row toggles it"):
  or do you prefer a small icon button per row, with the row only selecting?**
- **Is the legend's plain-language line enough, or should the old explanation line come back reworded?**
- **OBS tiles: keep the faint outlines (built), or drop them entirely (icons only, dim for missing)?**
- **OBS dungeon names: Short as the default everywhere (built), or Short only with labels off and Full with
  labels on? Are the short names right (Deku, Dodongo, Jabu, Forest, Fire, Water, Shadow, Spirit, Well, Ice, GTG,
  Ganon, Fortress)?**
- **Show default: All checks (built) or Open checks?**
- **Skip only for checks the save tracks (approved design), or also let you skip a check the save can't read
  instead of marking it done?**

## Screenshots (headless Chrome `--headless=new`, synthetic only)

Fixture (never Kareem's seeds or saves): `E:/OOTRemake/work/r21-tracker/make_fixture.py` fills seed 2121001 from
world data only (no dump: `generate.generate` + `generate.spoiler`, broad recipe from
`E:/OOTRemake/work/r18-fill/settings.txt`), UI layout, 500 checks; synthetic saves: `saves-empty/` (no save) and
`saves-mid/` (35% of chests/scrubs/gifts/Skulltulas set, a child inventory, audited save layout). Harness:
`E:/OOTRemake/work/r21-tracker/shots.py <label>`: in-process server, in-memory preferences, APPDATA and
LOCALAPPDATA under the scratch folder, icons decoded from the read-only dump. "Before" ran main `e9bb0d7`'s
`src` (extracted with `git archive` to `E:/OOTRemake/work/r21-tracker/main-e9bb0d7`, on `PYTHONPATH`).

Folders: `E:/OOTRemake/work/r21-tracker/shots/before/` and `.../shots/after/` (PNG plus `metrics.json`).

| View | Before | After |
|---|---|---|
| Tracker tab, no save, 1280 / 1920 | `empty-1280-tracker-top.png`, `empty-1920-tracker-top.png` | same names |
| Check list, no save, 1280 / 1920 | `empty-1280-checks.png`, `empty-1920-checks.png` | same, plus `-checks-detail.png` |
| Tracker tab with save, 1280 / 1920 | `mid-1280-tracker-top.png`, `mid-1920-tracker-top.png` | same names |
| Check list with save, 1280 / 1920 | `mid-1280-checks.png`, `mid-1920-checks.png` | same, plus `-checks-detail.png` |
| Click to mark, Open checks + Hide finished + a folded area | | `mid-1280-checks-marked.png`, `mid-1280-checks-open-collapsed.png` |
| OBS, no save, labels 340 px / compact 300 px | `obs-empty-labels.png`, `obs-empty-compact.png` | same names |
| OBS with save: labels, compact, compact text-only | `obs-mid-labels.png`, `obs-mid-compact.png`, `obs-mid-compact-text.png` | same names |
| OBS names full / hidden | (option did not exist) | `obs-mid-compact-full-names.png`, `obs-mid-compact-no-names.png`, `obs-mid-labels-full-names.png` |

Measured (`metrics.json`): check-list columns 3 -> 2 at 1280 and 5 -> 3 at 1920; rows with a prefix symbol
547 -> 0; Mark done buttons 223 (with save) / 547 (no save) -> 0; OBS dungeon cells 52 -> 35; OBS `?` badges
before any save 126 -> 0; compact OBS 280 x 1914 -> 236 x 1628 px (full names 280 wide, hidden 193), labelled
337 x 3440 -> 337 x 3092; no page errors; no request left 127.0.0.1. The marking flow ran in the page: a click
marked a dashed-ring row (the marks file under the scratch APPDATA), Open checks hid it, All checks showed it, a
second click unmarked it.

## Checks run

- Focused, outside the lock: `CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -q -n 2 tests/test_tracker_*.py
  tests/test_ui.py`: 251 passed, 1 skipped.
- `uv run ruff format --check`, `uv run ruff check`: clean on the changed tests.

Not yet: the skip backend (after MAIN MOVED for #39), the rebase onto it and the full gate.
