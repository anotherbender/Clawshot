# Spec: tracker-in-logic

Status: draft, 2026-11-20. Decisions below were made by BBender in a design interview with Claude (Opus 5.5);
"(rec)" marks where BBender took Claude's recommendation. Revised 2026-11-20: Background corrected and D15 added
after plan item 1.3 found the generator's world is not `validate` + `prepare` alone. Revised 2026-11-20 after the
main maintainer's review: D11 default age is Either; Either is `can_access(location)` with no age; save items go to
the search the way the generator feeds its own (closed return gate); marks live beside the preferences (D9); the
version gate also checks the spoiler's locations (D14); story-flag logic items (2.2); Ruto's Letter follows
`has_bottle` (2.7); Q1 and Q2 answered. Decisions marked "(maint)" are the maintainer's.

## Goal

The Tracker tab shows which of the seed's still-open checks are **in logic** right now: reachable with what the
player's save holds, by the seed's own logic. Checks whose collection the save cannot read (`?`: shops, swap-only
gifts, unset placement-hash pickups, unaudited event gates) can be marked done by hand so they leave the open list.

## Background (what exists)

- `clawshot.world.search.Search(world, items)` answers `can_access(location, age)` per age, and
  `can_access(location)` (no age) for "either age" by the search's own age rules. The constructor adds
  `world.start_items` and then the given items through `collect`. While `world.age_return` is closed the child view
  keeps separate counts (`_child_counts`, `search.py` `__init__`), so "granted to both ages" holds only for items
  fed in this way, not for everything the search later finds; the generator feeds assumed items through the
  constructor (`generate/fill.py`, e.g. `Search(world, [*assumed, *items])`). Events (Master Sword pull, age return,
  dungeon clears) are derived by the search itself.
- The spoiler holds the canonical CS1 `settings_string` and `generator`. `app.schema.validate(text=...)` plus
  `generate.prepare.prepare(spec, settings)` do **not** alone rebuild the `World` the generator searched: before
  `prepare`, the seed pipeline changes the spec, and two of those changes alter reachability (found 2026-11-20 while
  checking plan item 1.3):
  - Gift/NPC shuffle: `patch.gifts.shopkeeper_spec` (applied in `gifts.seed_setup`) turns the shopkeeper's free
    "Deku Shield" event into a placed check. Without it the search grants Deku Shield on reaching the shop.
  - Scrub shuffle: `patch.scrubs.seed_setup` (applied in `make_seed`) adds each one-time sale's wallet tier to its
    rule. Without it unaffordable scrubs read as reachable.
  The other pre-`prepare` changes (gift `restrict_spec`, bowling `n64_only`, `freestanding.restrict_spec`,
  `restrict_event_openings`, drop/freestanding palettes) only set `keep_vanilla`, exclusions, types or fill
  palettes, not reachability. Neither reachability change needs the dump.
- `tracker.state` already reads items, songs, rewards, hearts, tokens, bottles and per-dungeon key counts
  (held and found) from the save, and gives each shuffled check a three-state `collected` (True/False/None).
- The save holds `Sequence_IsChildhood` (Bool, file 0, default true; `plans/rounds/r18-master-sword-design.md`).
  Natural play keeps it right; Longshot's debug age switch does not change it.
- `has_bottle` (`world/rules.py`) is true when any item with `bottle = true` is held, or when `Rutos Letter` is held
  twice or more: one letter held is the letter, not a bottle.
- Some story steps are logic names too (for example `Met Child Zelda` and `Field Owl Arrival`, events in
  `data/world/remake/child_hyrule_castle.toml`).
- User preferences live in `app/preferences.py`'s folder (`%APPDATA%\Clawshot` on Windows, macOS/XDG
  equivalents); the icon cache (`%LOCALAPPDATA%\Clawshot\Cache\icons`) is safe to delete and holds no user data.
- The OBS view already strips `areas[].checks`.

## Decisions

| # | Topic | Decision |
|---|-------|----------|
| D1 | Logic inventory source | The tracker's existing save-read holdings, mapped to logic item names. Not the spoiler's placements. |
| D2 | Items that leave the inventory (trade items, Ruto's Letter, eaten/burnt shields) | Count if held now **or** the save's acquired-once flag is set (rec). An item with no known acquired-once flag counts only when held now, as D4 (Q2 answered (maint)). |
| D3 | Small keys | Use the dungeon's **found** count (including spent keys), not held (rec). |
| D4 | Unknown save fields (`?`) | Item counts as **not held** (rec). |
| D5 | Unknown checks without a manual mark | Count as **not collected** (still open) (rec). |
| D6 | Manual mark effect | Marks the check done (leaves the open list). Does **not** add its item to the logic inventory (rec). |
| D7 | Manual mark spoilers | A marked check's item stays hidden in spoiler-free mode; only spoiler mode or save confirmation shows it (rec). |
| D8 | Which checks can be marked | Only checks whose save state is unknown (`collected is None`). A save-confirmed state wins over and drops a mark. |
| D9 | Mark storage | JSON in Clawshot's preferences folder (beside `app/preferences.py`'s file, not the deletable icon cache), never in seed, save or game folders (rec; folder (maint)). |
| D10 | Mark scope | Per seed (by `output_sha256`, else a hash of the spoiler file) and per save slot (rec). |
| D11 | Age display | Selectable: **Either** (default), Follow save, Child, Adult. Either means `Search.can_access(location)` with no age, so tracker and generator agree. Follow save reads `Sequence_IsChildhood`; unreadable falls back to Either and says so. A chosen option persists until changed (rec; default Either (maint): with Follow save a child would see adult-only checks as out of logic even when they can become adult, and other randomizer trackers count both ages). |
| D12 | Display | Every open check gets an in-logic / out-of-logic style, each area shows "N in logic", and a "Show only in-logic" toggle hides the rest (rec). |
| D13 | OBS | Unchanged in v1 (rec). |
| D14 | Version gate | In-logic is computed only when the spoiler's `generator` equals `clawshot <installed version>` exactly, the world rebuilds from its settings string, and every location named in the spoiler exists in the rebuilt world; otherwise it is disabled with the reason shown, and item tracking continues (rec; location check (maint): `generator` carries no commit, so two builds from `main` with one version can differ in logic). |
| D16 | Save items into the search | The logic inventory is fed to `Search` the way the generator feeds its own assumed items (constructor `items`), so the closed-return-gate child view behaves as in generation (maint). |
| D17 | Story-flag logic items | Story steps that are logic names map to their save flags where the flag is known; otherwise they are listed as unmapped with a reason (maint). |
| D18 | Ruto's Letter and bottles | Follow `has_bottle`: a bottle slot holding the letter counts as the letter only, never also as a bottle (maint). |
| D15 | Logic world source | One shared, dump-free builder of the seed's logic world (the reachability-changing spec steps, then `prepare`) used by both the seed pipeline and the tracker, so the two cannot drift. Proposed by Claude, chosen by BBender over a tracker-side copy of the steps or storing the world in the spoiler (rec). |

## Acceptance criteria

### 1. Logic world

- **1.1** For a seed whose `generator` equals `clawshot <installed version>`, the tracker rebuilds the seed's
  `World` from the spoiler's settings string with the same code path the generator uses: `validate` and then the
  shared logic-world builder (D15).
- **1.5** The shared builder needs no dump. The seed pipeline (`make_seed`, with gift setup) searches a world equal
  in regions, exits, events, locations, location rules and items to the builder's world for the same settings;
  a test shows this on synthetic settings with Gift/NPC and Scrub shuffle on and off.
- **1.6** Introducing the builder changes no generated seed: same seed and settings give a byte-identical output
  folder and spoiler before and after (AGENTS.md rule 4).
- **1.2** The world is built once per loaded seed and cached; save polls do not rebuild it.
- **1.3** When the generator string differs, the settings string is missing, validation/prepare raises, or a
  location named in the spoiler is missing from the rebuilt world (D14), the state carries `logic.available = false` with a human-readable `logic.reason`, no check carries in-logic data, and
  every existing tracker field is unchanged.
- **1.4** The tracker never writes to the seed folder, save folder, game dump or game folder while computing logic.

### 2. Logic inventory

- **2.1** The inventory is built only from the tracker's save-read state (items, upgrades, songs, stones,
  medallions, hearts/pieces, Gold Skulltula token count, bottles, magic, dungeon items), plus the world's starting
  items. Spoiler placements are not used to build it. It is handed to `Search` as the constructor's `items`, the
  way the generator feeds its own assumed items (D16); a test with the age-return gate still closed shows the
  tracker's per-age results equal a search built the generator's way from the same items.
- **2.2** The mapping from tracker cells to logic item names lives in a data file, not in Python branches. Every
  progression item of the world is either mapped or listed as unmapped with a reason; a test fails when a
  progression item is neither. Story steps that are logic names (for example `Met Child Zelda`,
  `Field Owl Arrival`) map to their save flags where the flag is known, else they are listed as unmapped (D17).
- **2.3** Tiered/progressive cells grant as many copies of the progressive logic item as the held tier
  (e.g. Longshot = two Progressive Hookshot).
- **2.4** A trade item, Ruto's Letter or a shield counts as held when the save holds it now or its acquired-once
  flag is set (D2). An item without a known acquired-once flag counts only when held now.
- **2.5** Small keys per dungeon use the found count, including spent keys (D3). Boss keys, maps and compasses use
  their saved flags.
- **2.6** A cell whose save value is unknown contributes nothing (D4), and the state lists those cells in
  `logic.unknown_items` so the UI can say the result may be conservative.
- **2.7** Bottles follow the logic's `has_bottle` (D18): each owned slot without the letter counts as a bottle item;
  a slot holding Ruto's Letter counts as one `Rutos Letter` and not also as a bottle, so the letter is never counted
  twice.

### 3. In-logic per check

- **3.1** A check is **open** when its save state is not collected, or unknown and not manually marked (D5).
- **3.2** For each open check the state reports `in_logic`: `child` and `adult` from
  `Search.can_access(location, age)`, and `either` from `Search.can_access(location)` with no age (not the OR of
  the two).
- **3.3** Collected checks and manually marked checks carry no in-logic flag and never count as in logic.
- **3.4** Each area reports `in_logic` counts for child, adult and either age (either from 3.2's `either`).
- **3.5** The search is recomputed only when the logic inventory changes, not on every poll.
- **3.6** Showing in-logic status reveals no item: an open check's entry contains no `item`/`item_label` unless
  spoiler mode is on, as today.

### 4. Manual marks

- **4.1** In the app tab, a check whose save state is unknown can be toggled between unknown and "marked done by
  you". Checks with a save-confirmed state cannot be marked.
- **4.2** A marked check is shown distinctly from a save-confirmed collected check, and counts as done in area
  counts and the open list.
- **4.3** A mark does not add the check's item to the logic inventory (D6).
- **4.4** In spoiler-free mode a marked check's item stays hidden (D7).
- **4.5** When a later save reads the marked check as collected or not collected, the save's state is used and the
  mark is removed from storage.
- **4.6** Marks are stored as JSON in Clawshot's preferences folder (the parent of
  `app.preferences.user_preferences_path()`: `%APPDATA%\Clawshot` on Windows, macOS/XDG equivalents; not the
  deletable cache folder),
  keyed by seed identity (`output_sha256`, else SHA-256 of the spoiler file) and save slot path. Nothing is written
  in seed, save or game folders.
- **4.7** Marks survive a Clawshot restart and are separate per seed and per slot: a different slot of the same
  seed starts with no marks.
- **4.8** A "Clear manual marks" control removes all marks for the current seed and slot after a confirmation.
- **4.9** The mark endpoint is a POST behind the server's existing token/Host/Origin checks and rejects unknown
  check ids, checks not currently unknown, and requests without a configured seed and slot.
- **4.10** An unreadable or missing marks file is reported as a warning and treated as empty; it is never
  overwritten until the user changes a mark.

### 5. Age selection

- **5.1** The Tracker tab has an age control: Either (default), Follow save, Child, Adult.
- **5.2** Follow save uses Child when `Sequence_IsChildhood` is true and Adult when false. When the Bool is
  unreadable, it uses Either and shows a one-line note.
- **5.3** A chosen option other than the default persists across reloads in the browser (localStorage, every access
  wrapped in try/catch) until the user changes it; the page works when storage is unavailable.
- **5.4** The in-logic styling, area counts and the filter all follow the selected age.

### 6. Display

- **6.1** In Checks by area, each open check is styled in-logic or out-of-logic for the selected age; collected and
  marked checks keep their own styles.
- **6.2** Each area heading shows "N in logic" for the selected age next to its existing counts.
- **6.3** A "Show only in-logic" toggle hides open out-of-logic checks, collected and marked checks; areas with no
  visible check collapse.
- **6.4** When logic is unavailable (1.3), the age control and filter are disabled and the reason is shown; the
  rest of the tab works as today.
- **6.5** When `logic.unknown_items` is not empty, the tab shows one line saying in-logic may be conservative,
  naming the unknown cells.
- **6.6** The OBS view (`tracker-obs`) payload and rendering are unchanged (D13); logic and marks data are not
  included in it.

### 7. Docs and checks

- **7.1** `docs/tracker.md` gains an "In logic" section covering D1–D18 as the player sees them, including that
  Follow save reads `Sequence_IsChildhood`, which Longshot's debug age switch does not change. Its "Nothing is
  created or changed by tracking" statement is reworded to "nothing in your game, seed or save folders" with the
  marks file's location (Q1 approved by the maintainer).
- **7.2** Synthetic-fixture tests cover: version gate (1.3), inventory mapping including tiers, trade
  acquired-once, found keys and unknown fields (2.x), the closed age-return gate (2.1), Ruto's Letter in a bottle
  (2.7), per-age and either-age in-logic on a small custom world (3.x), the spoiler-location gate (1.3), marks
  lifecycle and isolation per seed/slot (4.x), Follow save from `Sequence_IsChildhood` (5.2), and OBS payload
  unchanged (6.6).
- **7.3** `uv run ruff format --check`, `uv run ruff check` and the test suite pass. The suite is run with
  `uv run --with pytest-xdist pytest -n auto` (much faster than plain `pytest`); tests needing a game dump skip
  without one.
- **7.4** In-game acceptance (maintainer run, not by an agent): with a Clawshot Play seed, save after collecting a
  few items, and confirm the Tracker's in-logic list matches what is reachable in game for that age; buy a shop
  item, mark its check, restart Clawshot, and confirm the mark persists and the shop's item is hidden in
  spoiler-free mode.

## Out of scope (v1)

- In-logic in the OBS view.
- Marking save-confirmed checks, or adding a marked check's item to the inventory.
- Live (unsaved) progress; the tracker still reads saved progress only.
- Entrance-aware or hint-aware tracking beyond what the seed's world already encodes.

## Maintainer questions (answered 2026-11-20)

- Q1: Rewording of the "nothing is created or changed by tracking" promise (7.1). **Approved**: "nothing in your
  game, seed or save folders", plus where the marks file lives.
- Q2: Whether the acquired-once rule (D2) should also apply to items without an audited acquired-once flag.
  **Held-now only** for items without a known acquired-once flag, matching D4.
