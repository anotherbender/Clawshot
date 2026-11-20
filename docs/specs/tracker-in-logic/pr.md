# Tracker: which open checks are in logic, and manual marks

Spec: `docs/specs/tracker-in-logic/spec.md`; plan: `docs/specs/tracker-in-logic/plan.md`.

## What changes

- **Shared logic world (D15).** `clawshot.patch.logic_world.logic_world(settings)` builds the world the generator
  searched, without the dump: Gift/NPC shuffle's shopkeeper step (`gifts.logic_spec`) and Scrub shuffle's
  wallet-tier rules (`scrubs.logic_spec`, split out of `scrubs.seed_setup`), then `prepare`. `gifts.seed_setup` and
  `make_seed` (through `scrubs.seed_setup`) take those steps from the same functions.
- **Tracker logic layer** (`clawshot.tracker.logic`). For a seed made by this version whose settings rebuild and whose
  every spoiler location exists, the save's holdings become a logic inventory (`data/tracker_logic.toml`), fed to
  `Search` as constructor items like the generator's assumed items. Every open check gains
  `in_logic: {child, adult, either}`, every area its counts, and the state a `logic` object (`available`, `reason`,
  `unknown_items`, `save_age`). The search is rebuilt only when the inventory changes.
- **Manual marks** (`clawshot.tracker.marks`): `tracker-marks.json` beside the preferences.
  Keyed by seed and save folder (every slot in it). POST `tracker-mark` and `tracker-clear-marks` (confirmation required) behind the existing token/Host/Origin checks.
- **Tracker tab**: in/out-of-logic styling, "N in logic" per area, age control (Either default, Follow save, Child,
  Adult; remembered in localStorage when not the default), "Show only in-logic", mark toggles, "Clear manual
  marks". The OBS payload and view are unchanged.
- **Docs**: `docs/tracker.md` "In logic" section; the "nothing is created or changed" sentence reworded (Q1).

## Decisions, and who made them

| Decision | By |
|---|---|
| D1-D8, D10, D12, D13 | BBender, with Claude's recommendation (design interview) |
| D15 shared dump-free builder | proposed by Claude, chosen by BBender, 2026-11-20 |
| D9 marks beside the preferences; D11 default age Either; D14 spoiler-location gate; D16 items as constructor items; D17 story flags; D18 Ruto's Letter follows `has_bottle`; Q1 rewording approved; Q2 held-now only without a known acquired-once flag | main maintainer's review, 2026-11-20 |
| P5.b feed save count minus starting count, so each item counts as the larger of the two | proposed by Claude |
| Bombchus count once found (`IsGet.Item_Bombchu`), since `found_bombchus` asks whether chus were ever found | proposed by Claude: please confirm or reject |
| Hearts: whole hearts beyond the starting three, as four pieces each; loose pieces not counted (the saved piece count's meaning is not established) | proposed by Claude |
| Deku Sticks and Nuts count while at least one is held (`[stock]`: `Buy Deku Stick (1)`, `Buy Deku Nut (5)`, the names the `Sticks`/`Nuts` helpers read); the acquired-once flag is not used, since a new game sets `IsGet.Item_DekuNut` with none held | proposed by Claude after the maintainer's play of seed 212067047 showed bought sticks never counted (the Wolfos grotto stayed out of logic), 2026-11-20 |
| Marks belong to the seed and the save folder (`<save>/<profile>`), not one slot: the remake writes each save to the next slot (slots 05, 01, 00, 02, 03, 04 in six minutes), so per-slot marks vanished on every save. Changes D9's "per seed and save slot"; two playthroughs of one seed in one save folder now share marks | proposed by Claude from the maintainer's report, 2026-11-20: please confirm |
| Magic beans count as held now (planted beans are gone; conservative, D4) | proposed by Claude |
| Ocarina buttons, silver rupees, key rings, Treasure Chest Game keys, bottle contents and shop goods listed unmapped with reasons | proposed by Claude |
| Story steps: `Field Owl Arrival` = `HyruleField_ArriveEntrance`, `Met Child Zelda` = `HavePlayedEvent.Dm_HrlField_0020` (cited in `child_hyrule_castle.toml`); other remake-added story events unmapped | proposed by Claude from the remake data's own sources |
| A missing marks file reads as no marks without a warning (a fresh install has none); an unreadable one warns and is kept | proposed by Claude: the spec asks for a warning on a missing file too; please confirm |
| The app tab now lists every check by name in spoiler-free mode (items stay hidden), so open checks can be styled (6.1) | proposed by Claude: previously names showed only in spoiler mode |
| `either` comes from `can_access(location)` with no age; in this search it always equals child-or-adult, so the test checks the call, not a differing case | finding, plan 6.2 |

## Checks

- `uv run ruff format --check`, `uv run ruff check`: pass.
- `uv run --with pytest-xdist pytest -n auto`: 3902 passed, 505 skipped (baseline before the change: 3806 passed,
  499 skipped).
- Determinism (1.6): spoilers of 12 seeds (Chest, Scrub, Gift, Gift+Scrub x seeds 1-3, full world) hashed before and
  after the refactor: identical.
- **Not run (no dump on the agent's machine)**: `OOT_ROMFS=<romfs> uv run pytest -m dump`, which includes
  `test_make_seed_searches_the_logic_world`, `test_gift_seed_setup_uses_the_shared_step` and `test_seed_dump.py`.
  A maintainer with a dump please run it.

## In-game acceptance (maintainer run; not claimed here)

1. Make a Clawshot Play seed with this build (Gift and Scrub shuffle on gives the most coverage). Start it with
   **Play**, collect a few items, and save.
2. In the **Tracker** tab, **Use selected seed**. Confirm the status says in-logic is available (no reason line).
3. For **Child**, then **Adult**, compare the highlighted checks with what you can actually reach in the game with
   what you hold. Note any check shown in logic that you cannot reach, or out of logic that you can.
4. Buy a shop item. Its check shows `?`; press **Mark done**. It shows "marked done by you", leaves the in-logic list,
   and its item stays hidden with spoilers off.
5. Close and restart Clawshot, track the same seed and slot again: the mark is still there and the item still hidden.
6. Confirm `tracker-marks.json` is in `%APPDATA%/Clawshot` and nothing new appeared in the seed or save folders.
7. Check the OBS URL: no in-logic data, no marks.

Record the result (who, build, what was seen) in the round or PR.

Assisted-by: Claude Opus 5.5
