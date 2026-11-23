# Tracker auto checks (BBender)

Design record for reading gift checks from the game's own once-flags in the Tracker, contributed by BBender.
Player guide: [tracker guide](../docs/tracker.md#in-logic) ("Gifts read automatically"). Part 1 is the spec,
Part 2 the implementation plan. Evidence: [static audit](tracker-auto-checks-audit.md); played acceptance:
[maintainer checklist](tracker-auto-checks-play.md).

## Part 1: spec

Status: draft, 2026-11-22. Decisions below were made by BBender in a design interview with Claude (Opus 5.5);
maintainers may revisit them in review. Revised 2026-11-22 after plan task 4's audit: five candidates failed and
moved to "Stays manual" with the reason.

### Goal

Read gift checks that the tracker shows as `?` today from flags the game already saves, so players stop marking
them by hand. Reader and data only: no change to seeds, the patch, the save layout or the game runtime.

### Background (what exists)

In seed-2445192976 (325 checks, newest save slot_04) the tracker could not read 129 checks: 64 shop slots, 48 gifts
(read method `none`, "this gift keeps no saved record of being given") and 17 boss hearts and freestanding Pieces of
Heart (unset placement Hash, "not certified"). The player's `tracker-marks.json` holds mostly shops and gifts.

`patch/gift_rules.toml` already names a native once-flag for most of those gifts in its free-text `gate` evidence,
but the tracker only reads `flag` (`tracker/seeds.py` `_gift_record`). A read-only probe of the player's real saves
found:

- Gate Bools, for example `Minigame_SkullKidSession_IsGetHeartPiece`: True for every gift the player marked, False for
  every unmarked one (two seeds).
- `HavePlayedEvent.<cutscene flow>` for song and cutscene gifts, for example `Dm_MelodyGet_Zelda` for Song from Impa:
  matched the marks in seed-2445192976.
- Quest enum `Step_SubEvent_FindRichard` equal to `Complete` exactly where Lost Dog was marked.
- One possible mismatch: Song from Royal Familys Tomb reads True but is unmarked in seed-2369611282, probably a mark
  the player never made.

This is supporting evidence only. It is not the audit or the played acceptance required below.

In scope: a structured, tracker-only `track` record per gift in `gift_rules.toml`, how the tracker reads it, how
marks behave with it, a dump test on patched event flows, a read-only audit CLI, docs, and a maintainer play
checklist.

### Decisions

| # | Topic | Decision |
|---|-------|----------|
| D1 | Where native flags live | A new `track` field per gift in `gift_rules.toml`. `flag` and `gate` are not reused or parsed. The patch ignores `track`. |
| D2 | Evidence for a flag | A track flag needs an event-flow audit (set at the grant, on no other path, with the source cited) and a played confirmation by a maintainer (AGENTS rule 3). Until it is played, it ships marked provisional. |
| D3 | Flag False or missing | When a track flag is present and False, the check is not collected (shown open, given in-logic styling). When the save has no such field, the check stays `?`. |
| D4 | Marks on provisional flags | Provisional flags keep marks. True means collected and drops the mark. False means not collected, but **Mark done** stays available and a mark is not dropped. Accepted flags behave like chests: False drops the mark and no button is shown. |
| D5 | Patch safety | A dump test on the patched event flows proves each track flag is still set after the grant. |
| D6 | Flag kinds | Saved Bool, `HavePlayedEvent.<flow>`, and a quest step enum equal to a named value. |
| D7 | Gifts without a native flag | Stay `?` and markable. The spec lists them. |
| D8 | Version gate | Track flags apply only to seeds whose `generator` equals the installed Clawshot version. Other seeds keep today's reads, with a one-line note. |
| D9 | Display | No visible difference between provisional and accepted reads in the tab or OBS. Only the mark behavior differs. |
| D10 | Played acceptance | A maintainer checklist plus a read-only CLI `python -m clawshot.tracker.audit` that compares a save's track flags with that seed's manual marks. |
| D11 | Several entries on one gift | Combine as any-of, like `named_bool`: any True means collected; all present and False means not collected; any missing with none True means `?`. |
| D12 | Spoilers | An auto-collected gift shows its reward in spoiler-free mode, as opened chests do. Marked checks, and checks a provisional flag reads as False, keep their reward hidden. |
| D13 | Acceptance target | Per gift, from the lists below. There is no numeric target. |

### Data format

Each `[check."<name>"]` table may hold `track`, a list of one or more entries. Each entry has exactly one kind key
(`bool`, `played` or `quest`), plus `source` and `accepted`:

```toml
track = [{ bool = "Minigame_SkullKidSession_IsGetHeartPiece", source = "<flow/event that sets it; audit ref>", accepted = false }]
track = [{ played = "Dm_MelodyGet_Zelda", source = "...", accepted = false }]       # reads HavePlayedEvent.Dm_MelodyGet_Zelda
track = [{ quest = "SubEvent_FindRichard", step = "Complete", source = "...", accepted = false }]  # Step_<quest> == murmur3(step)
```

`accepted = true` also requires `played_by` (who, which build, date).

### Gift list

Candidates are from `gate` evidence and the probe. "Seen" means the probe agreed with the player's marks in a real
save. Every row still needs the D2 audit. A candidate that fails its audit moves to "Stays manual" with the reason.

**Saved Bool**

| Gift | Candidate flag | Seen |
|---|---|---|
| LW Skull Kid | `Npc_SkullKid_Child_IsGetHeartPiece` | False/unmarked |
| LW Ocarina Memory Game | `Minigame_SkullKidSession_IsGetHeartPiece` | yes |
| LW Target in Woods | `LostWood_HitTargetOfDekuScrub_FirstClear` | yes |
| Deku Theater Mask of Truth | `LostWood_ScrubForestStage_TrueMaskEventLaunched` | |
| Deku Theater Skull Mask | `LostWood_ScrubForestStage_SkullMaskEventLaunched` | |
| GC Rolling Goron as Child | `GoronCity_GetBombBag_fromGoron006` | yes |
| GC Rolling Goron as Adult | `SageOfFire_Step02_DaruniaJr_FirstTalked` (a first-talk flag: check it is not set before the grant) | |
| GF HBA 1000 Points | `MiniGame_HorsebackArchery_GotaHeart` | False/unmarked |
| GF HBA 1500 Points | `MiniGame_HorseBackArchery_Get_Quiver` | False/unmarked |
| Kak 10/20/30/40/50 Gold Skulltula Reward | `KakarikoVillage_GatheringTokenGold_GetReward10` … `50` | False/unmarked |
| Kak Anju as Child | `MiniGame_CatchCucco_IsCompleted` | yes |
| Kak Anju as Adult | `GetSwordBigGoron_IsAfterFirstTalk_Npc_Hylia_049_Adult` (check its timing) | |
| Kak Man on Roof | `Npc_Hylia_001_IsGetHeartPiece` | yes |
| Kak Shooting Gallery Reward | `MiniGame_HitTarget_Kakariko_Get_Quiver` | False/unmarked |
| LH Child Fishing | `MiniGame_Fishing_GetHeartPiece` | False/unmarked |
| LH Adult Fishing | `MiniGame_Fishing_GetGoldScale` | False/unmarked |
| LH Lab Dive | `Npc_Hylia_045_HasDived` (check it is not set by the dive alone) | False/unmarked |
| LLR Talons Chickens | `IsClear_Minigame_FindOutCucco` | yes |
| Market Bombchu Bowling First Prize | `MiniGame_BombchuBowling_ClearFirstTime` | False/unmarked |
| Market Bombchu Bowling Second Prize | `MiniGame_BombchuBowling_ClearSecondTime` (the patch also sets `ClearThirdTime` here) | False/unmarked |
| Market Shooting Gallery Reward | `MiniGame_HitTarget_HrlCity_Get_BulletBag` | yes |
| Market Potion Shop Bottle | `Npc_Hylia_020_Shop_Item_Bottle_Present` | yes |
| Graveyard Dampe Gravedigging Tour | `GraveYard_DiggingHoleTour_Drop_HeartPiece` | yes |
| Song from Royal Familys Tomb | `RoyalFamilyTomb_MelodyGet_Clear` | yes (one possibly forgotten mark) |
| ZD Diving Minigame | `MiniGame_Diving_Cleared` | yes |
| ZD King Zora Thawed | `SageOfWater_KingZora_adult_Talk_Event198` | |
| ZR Frogs Ocarina Game | `MiniGame_FrogTenors_InsectRepellent` | False/unmarked |
| ZR Frogs in the Rain | `MiniGame_FrogTenors_StormSong` | yes |
| ZR Frogs Zeldas Lullaby / Eponas Song / Sarias Song / Suns Song / Song of Time | `MiniGame_FrogTenors_ZeldaLullaby` / `_EponaSong` / `_SariaSong` / `_SunSong` / `_TimeSong` | Lullaby yes; others False/unmarked |

**`HavePlayedEvent.<flow>`**

| Gift | Candidate flow | Seen |
|---|---|---|
| LW Gift from Saria | `Dm_Kokiri_0155` | yes |
| Song from Saria | `Dm_MelodyGet_Saria` | yes |
| Song from Malon | `Dm_MelodyGet_Epona` | yes |
| Song from Impa | `Dm_MelodyGet_Zelda` | yes |
| Sheik in Forest | `Dm_MelodyGet_Forest` | False/unmarked |
| Sheik in Kakariko | `Dm_MelodyGet_Shadow` | False/unmarked |
| Sheik in Ice Cavern | `Dm_MelodyGet_Water` | False/unmarked |
| Sheik at Colossus | `Dm_MelodyGet_Spilit` | False/unmarked |
| Sheik at Temple | `Dm_MelodyGet_Shine` | False/unmarked |
| HF Ocarina of Time Item, Song from Ocarina of Time | `Dm_MelodyGet_Time` (one cutscene gives both) | False/unmarked |
| ToT Light Arrows Cutscene | `Dm_TimeTemple_0130` | False/unmarked |
| HC Zeldas Letter, GC Darunias Joy | flow to be found in the audit | |

The audit must cover when `HavePlayedEvent` is written (event start or end) and whether a cutscene the seed skips
(owl skips, fast start, patch `skip`) still writes it.

**Quest step**

| Gift | Quest, step | Seen |
|---|---|---|
| Market Lost Dog | `SubEvent_FindRichard`, `Complete` | yes |
| Market 10 Big Poes | `SubEvent_GhostShop`, `Complete` | not complete/unmarked |
| DMT Biggoron | `SubEvent_GetSwordBigGoron`, `Complete` | not complete/unmarked |
| Kak 100 Gold Skulltula Reward | `GatheringTokenGold`, `Complete` | not complete/unmarked |
| HC Malon Egg | `Goto_HyruleCastle`, step to be found in the audit | |

**Stays manual (D7):** DMT Trade Broken Sword, DMT Trade Eyedrops, GV Trade Poachers Saw, Kak Anju Trade Pocket
Cucco, Kak Granny Trade Odd Mushroom, LW Trade Odd Potion (each hand-in only takes an item; no flag), every shop
slot, and any candidate above that fails its audit. `more`-class gifts are not shuffled gifts and are unchanged.

Failed the D2 audit (2026-11-22, [tracker-auto-checks-audit.md](tracker-auto-checks-audit.md)), so also manual:

- GC Rolling Goron as Adult: `SageOfFire_Step02_DaruniaJr_FirstTalked` is set on a first (crying) talk that gives
  nothing.
- Kak Anju as Adult: `GetSwordBigGoron_IsAfterFirstTalk_Npc_Hylia_049_Adult` is set on a first talk without the
  grant, and the grant can run without it.
- Market 10 Big Poes: `SubEvent_GhostShop` reaches `Complete` on the Gold Rupee route, not after the bottle.
- Kak 100 Gold Skulltula Reward: `GatheringTokenGold` reaches `Complete` on a path without the reward, and the
  reward runs without it.
- HC Malon Egg: no `Goto_HyruleCastle` step is both set at the egg and kept afterwards (the quest moves past
  Step03); an "at or past a step" read would be a new product call.

### Acceptance criteria

#### 1. Data and validation

- **1.1** `gift_rules.toml` accepts an optional `track` list. Each entry has exactly one of `bool`, `played` or
  `quest`; `quest` also needs `step`. Every entry needs a non-empty `source` and a boolean `accepted`, and
  `accepted = true` needs `played_by`. Anything else fails `gifts.load()` with an error naming the check.
- **1.2** A check that has a `flag`, or that the patch gives an added `Clawshot.Gift.*` flag, may not also have
  `track`. Loading fails if it does.
- **1.3** The patch's output does not change: the same seed, settings and version give a byte-identical output folder
  before and after this feature (rule 4). This is shown by a test.
- **1.4** Every gift in the Saved Bool, HavePlayedEvent and Quest step lists that passed its audit has a `track`
  entry whose `source` cites the setting event (flow/event, or EventSetting row) and the audit record. The ones that
  failed are listed under "Stays manual" with the reason.

#### 2. Reading the save

- **2.1** A gift with `track` reads `bool` as `save.flag(name)`, `played` as `save.flag("HavePlayedEvent." + flow)`,
  and `quest` as `save.enum_value("Step_" + quest) == murmur3_32(step)`.
- **2.2** Entries combine any-of (D11): any True means collected; all present and False means not collected; missing
  fields with none True means `?`, with a reason naming the missing field.
- **2.3** Track flags are used only when the seed's `generator` equals `clawshot <installed version>` (D8). Otherwise
  the gift keeps today's read, and the tracker shows one warning line saying auto-read gifts need a seed made by this
  version.
- **2.4** The check's `method` and `kind` stay as they are for gifts without `track`. Chest, token, scrub and
  placement-Hash reads are unchanged, shown by the existing tests passing unmodified.
- **2.5** In-logic holdings are unchanged: collecting a gift never adds its item to what is held (the save's inventory
  stays the only source).

#### 3. Marks

- **3.1** Accepted flag reads False: the check shows as not collected, **Mark done** is not offered, and an existing
  mark is dropped, as for chests today.
- **3.2** Provisional flag reads False: the check shows as not collected (open, with in-logic styling), **Mark done**
  or **Unmark** is still offered, a mark set on it is kept and counted, and its reward stays hidden in spoiler-free
  mode.
- **3.3** Any track flag reads True: collected, and an existing mark is dropped.
- **3.4** The state JSON carries what the UI needs to offer the button for a provisional False check, without exposing
  which flag or that it is provisional (D9). The OBS view is unchanged.
- **3.5** Tests cover 3.1 to 3.3 with synthetic saves and an in-memory mark store, including a mark surviving several
  polls on a provisional False.

#### 4. Spoilers and display

- **4.1** A gift read as collected shows its reward in spoiler-free mode, as an opened chest does. Marked checks and
  provisional False checks do not.
- **4.2** No new styling or label distinguishes provisional from accepted reads in the tab or OBS (D9).

#### 5. Patched-flow dump test

- **5.1** A test marked `dump` builds the patched event flows for the gift checks (any shuffled item) and asserts, for
  every `bool` and `quest` track entry, that the flow still writes that flag or quest step on every path after the
  check's grant step, and on no path that skips the grant.
- **5.2** For every `played` entry, the test asserts the EventSetting row `<flow>` exists and that the patch neither
  removes nor skips the check's grant step in that flow.
- **5.3** The test skips without `OOT_ROMFS` and passes with it. A synthetic test runs the checker logic on a built
  flowchart.

#### 6. Audit CLI (oracle)

- **6.1** `python -m clawshot.tracker.audit <seed folder> [--slot N] [--marks <file>]` prints one line per gift with
  `track`: name, each flag and its value, the combined result, whether the default marks file marks it for that seed,
  and `agree`, `disagree` or `no-mark`. It ends with a count of disagreements.
- **6.2** It is read-only: it writes nothing to the seed, the save folder or the marks file, and never starts the
  game. A test asserts that the files are unchanged afterwards.
- **6.3** It follows the tracker's spoiler rule: no rewards are printed unless `--spoilers` is given.
- **6.4** It exits 0 with no disagreements and 1 with any disagreement. Tests use synthetic saves and marks.

#### 7. Played acceptance (maintainer run)

- **7.1** `plans/` gains a checklist with one row per track entry: what to do in game, which save to read, and what
  the tracker and `clawshot.tracker.audit` should show before and after the grant. It says to confirm the seed loaded
  through the runtime's `mods: <file> <- <path>` log line (rule 3).
- **7.2** A flag is switched to `accepted = true` only from a recorded maintainer run (`played_by`), never from the
  marks oracle alone.

#### 8. Docs and checks

- **8.1** `docs/tracker.md` lists which gift kinds are read automatically, that some still need **Mark done**
  (trades, shops), the provisional mark behavior, that reading needs a seed made by this version, and that collected
  gifts show their rewards like chests.
- **8.2** `uv run ruff format --check`, `uv run ruff check`, `uv run pytest`, and
  `OOT_ROMFS=<romfs> uv run pytest -m dump` pass.
- **8.3** No game data enters the repository. Fixtures are synthetic, and only flag names, flow/event names and
  sources are committed (rule 1).

### Out of scope (later specs)

- Patch receipt flags (`Clawshot.Gift.*` for trade hand-ins, `Clawshot.Shop.<slot>` for shops). These change seeds and
  the save layout and need a maintainer product call.
- A live layer through Longshot's control bridge (`HOS_CONTROL`). The randomizer stays agnostic to Hookshot and
  Longshot for now.
- The heart-pickup persistence audit, and a Longshot PR exposing Bool64 flags in `subscribe`.
- Shops in general, which stay manual.

### Maintainer questions (open)

- Q1: When the audit is ambiguous (Rolling Goron as Adult, Anju as Adult, Lab Dive, Zelda's Letter, Darunia's Joy,
  Malon Egg), should the gift stay manual or ship provisional? The audit (task 4) left none ambiguous: Rolling Goron
  as Adult, Anju as Adult and Malon Egg failed and stay manual; Lab Dive, Zelda's Letter and Darunia's Joy passed and
  ship provisional.
- Q2: Is the D8 version gate too strict for players on a patch release whose gift flows did not change?
- Q3: `plans/tracker-in-logic.md` D8 and 4.5 say a save-confirmed state always wins over and drops a mark; D4 here
  (BBender, newer) keeps marks on a provisional "not collected". Built per D4; tracker-in-logic.md needs a
  maintainer note if D4 stands.

## Part 2: plan

Spec: Part 1 above. Criteria keep the spec's identifiers (e.g. `1.3`); criteria added by this plan are marked `P`
(e.g. `P3.a`). Decisions D1–D13 are BBender's; nothing here reopens them. Touch points found in the code:

- `src/clawshot/patch/gifts.py` (rule loading), `src/clawshot/patch/gift_rules.toml` (data)
- `src/clawshot/tracker/seeds.py` (`_gift_record`, `_classify`, `Check`)
- `src/clawshot/tracker/state.py` (`collected`, `_check_entry`), `src/clawshot/tracker/saves.py` (`_build` mark drop,
  `mark`), `src/clawshot/tracker/logic.py` (`_flag_open`)
- `src/clawshot/ui/static/tracker.js`
- new `src/clawshot/tracker/audit.py`, `docs/tracker.md`, new `plans/` evidence and checklist

Tests run with `uv run --with pytest-xdist pytest -n auto`; dump tests skip without `OOT_ROMFS`.

1. [x] Check prerequisites and baseline
    1.1 [x] `uv run pytest -n auto` passes on `main` before any change; the count of passed/skipped tests is noted in the PR. Run on main + rebased vanilla-rows (the base at the time): 4224 passed, 829 skipped, 1 failed (`test_ui.py::test_concurrent_output_creation_is_not_overwritten_or_cleaned`, unrelated, passes alone).
    1.2 [x] `OOT_ROMFS` points at a read-only romfs dump and `uv run pytest -m dump -n auto` passes on `main`. 1.1.1 dump: 767 passed, 60 skipped.
    1.3 [x] A baseline output folder for a fixed seed, settings and version is generated outside the repository, for the 1.3 comparison. Seed 12345, `--shuffle Chest Gift Scrub Token`, in the agent's scratchpad.
    1.4 [x] No code/plan disagreement found between the spec and `plans/` (tracker plans `plans/tracker-in-logic.md`, `plans/rounds/r14-tracker.md`); any found is raised to the maintainers before coding (AGENTS). One raised: Q3 (tracker-in-logic D8 and 4.5 against D4). Implemented per D4.

2. [x] Add the `track` field to gift rule loading (`patch/gifts.py`)
    2.1 [x] 1.1 `gift_rules.toml` accepts an optional `track` list. Each entry has exactly one of `bool`, `played` or `quest`; `quest` also needs `step`. Every entry needs a non-empty `source` and a boolean `accepted`, and `accepted = true` needs `played_by`. Anything else fails `gifts.load()` with an error naming the check.
    2.2 [x] 1.2 A check that has a `flag`, or that the patch gives an added `Clawshot.Gift.*` flag, may not also have `track`. Loading fails if it does.
    2.3 [x] P2.a `track` is added to `FIELDS`; `Rule` carries it as an immutable tuple of entries (frozen dataclass `TrackEntry` with `kind`, `name`, `step`, `source`, `accepted`, `played_by`).
    2.4 [x] D1 No patch code path reads `Rule.track`: `plan()` and every flow edit are unchanged, shown by a grep in the PR and by 3.1.
    2.5 [x] P2.b Unit tests in `tests/test_gifts.py` cover each 1.1 / 1.2 rejection with synthetic TOML (missing kind, two kinds, `quest` without `step`, empty `source`, non-bool `accepted`, `accepted = true` without `played_by`, `track` beside `flag`, `track` on a check with an added flag) and one valid entry of each kind.

3. [x] Prove the patch output does not change
    3.1 [x] 1.3 The same seed, settings and version give a byte-identical output folder before and after this feature (rule 4), shown by a test.
    3.2 [x] P3.a The 1.3 test builds the output twice from synthetic rules, once with `track` entries added and once without, and compares the folders byte for byte (no game data needed); a `dump` variant does the same over the real rules when `OOT_ROMFS` is set.
    3.3 [x] P3.b The manual comparison against the 1.3 baseline folder from task 1 is reported in the PR as identical. Seed 12345, `--shuffle Chest Gift Scrub Token`, 1.1.1 dump: the folder before the change and after the track data (195 files incl. spoiler) are identical (`diff -rq`, 2026-11-22).

4. [x] Audit every candidate gift (D2) and record the result
    4.1 [x] D2 For each candidate in the spec's Saved Bool, HavePlayedEvent and Quest step lists, the setting event (flow/event or EventSetting row) is found in the dump by a read-only research script kept outside the repository, and it is shown to set the flag at the grant and on no other path.
    4.2 [x] D2 The audit answers for `played` flows when `HavePlayedEvent` is written (event start or end), and whether a cutscene the seed skips (owl skips, fast start, patch `skip`) still writes it. Statically: written at event end (`plans/03-game-data.md` facts); patch-side skips (`no_ocarina`, `skip_saria_farewell` handoffs) write it after the grant; song `skip` entries take out only `Dm_SY_Ocarina` play-along steps. Not shown statically, left to the play checklist: the player's in-game cutscene skip, owl skips and `fast_start` (audit note 6).
    4.3 [x] D2 The flows to be found (HC Zeldas Letter, GC Darunias Joy) and the HC Malon Egg quest step are named, or the gift moves to "Stays manual" with the reason.
    4.4 [x] Q1 The flagged candidates (GC Rolling Goron as Adult first-talk, Kak Anju as Adult timing, LH Lab Dive dive-alone, Market Bombchu Bowling Second Prize `ClearThirdTime`) each get an explicit pass/fail with evidence; ambiguous ones are put to the maintainers (Q1), not decided. Result: Rolling Goron as Adult and Anju as Adult fail (first-talk flags), Lab Dive and both Bowling prizes pass (Bowling by an invariant, audit note 2); none was left ambiguous.
    4.5 [x] P4.a The audit record (per gift: flag, flow/event, result, who, build, date) is written to a `plans/` evidence file ([tracker-auto-checks-audit.md](tracker-auto-checks-audit.md)), holding only flag, flow and event names, never game data (rule 1, 8.3).
    4.6 [x] P4.b The spec's "Stays manual" list is updated with every candidate that failed, with its reason.

5. [x] Add the `track` data to `gift_rules.toml`
    5.1 [x] 1.4 Every gift that passed its audit has a `track` entry whose `source` cites the setting event and the audit record; the ones that failed are listed under "Stays manual" with the reason. 51 checks (35 bool, 14 played, 2 quest); 5 failed, listed in Part 1.
    5.2 [x] D2 Every entry ships `accepted = false`; none is accepted in this change (7.2).
    5.3 [x] P5.a Multi-check cutscenes (HF Ocarina of Time Item and Song from Ocarina of Time) each carry their own `track` entry for the shared flow.
    5.4 [x] P5.b `gifts.load()` loads the real file without error, and a test asserts every `track` check name exists in the rules and is not class `more`.

6. [x] Read track flags in the tracker (`tracker/seeds.py`, `tracker/state.py`)
    6.1 [x] 2.1 A gift with `track` reads `bool` as `save.flag(name)`, `played` as `save.flag("HavePlayedEvent." + flow)`, and `quest` as `save.enum_value("Step_" + quest) == murmur3_32(step)`.
    6.2 [x] 2.2 Entries combine any-of (D11): any True means collected; all present and False means not collected; missing fields with none True means `?`, with a reason naming the missing field.
    6.3 [x] 2.3 Track flags are used only when the seed's `generator` equals `clawshot <installed version>` (D8). Otherwise the gift keeps today's read, and the tracker shows one warning line.
    6.4 [x] 2.4 The check's `method` and `kind` stay as they are for gifts without `track`; chest, token, scrub and placement-Hash reads are unchanged. One existing assertion changed: `test_seed_checks_kinds_and_dungeon_totals` expected LW Skull Kid as `("gift", "none")`; it now has a track entry, so `("gift", "track")`. Every other existing tracker test passes unmodified.
    6.5 [x] 2.5 In-logic holdings are unchanged: collecting a gift never adds its item to what is held.
    6.6 [x] P6.a `Check` gains the track entries and a `provisional` flag (true when any entry is `accepted = false`); a new read method constant `TRACK` is used only for gifts with `track` under 6.3.
    6.7 [x] P6.b The D8 warning appears once per state, not once per gift, and only when the seed has at least one `track` gift.
    6.8 [x] P6.c Tests use synthetic saves for each kind, each D11 combination, a quest on another step, a missing enum field, and a seed from another generator version. In `tests/test_tracker_track.py` (new file, reusing `test_tracker_state.build_save`).

7. [x] Mark behavior (`tracker/state.py`, `tracker/saves.py`)
    7.1 [x] 3.1 Accepted flag reads False: not collected, **Mark done** is not offered, and an existing mark is dropped, as for chests today.
    7.2 [x] 3.2 Provisional flag reads False: not collected (open, with in-logic styling), **Mark done** or **Unmark** is still offered, a mark set on it is kept and counted, and its reward stays hidden in spoiler-free mode.
    7.3 [x] 3.3 Any track flag reads True: collected, and an existing mark is dropped.
    7.4 [x] 3.4 The state JSON carries what the UI needs to offer the button for a provisional False check, without exposing which flag or that it is provisional (D9). The OBS view is unchanged.
    7.5 [x] 3.5 Tests cover 3.1 to 3.3 with synthetic saves and an in-memory mark store, including a mark surviving several polls on a provisional False. In `tests/test_tracker_track.py` with `MemoryMarks`, an in-memory stand-in for `MarkStore`.
    7.6 [x] P7.a `SaveWatcher._build` drops a mark only when the check is collected, or not collected by an accepted read; `SaveWatcher.mark` accepts a provisional False check instead of refusing it as "the save already says".
    7.7 [x] P7.b The button field is generic (`markable: true`) and is set on every `?` check too (vanilla `?` rows included), so its presence does not reveal a provisional read (D9); `tracker.js` offers the button from it.
    7.8 [x] P7.c A marked provisional False check is counted under `marked` and treated as done by `logic.annotate` exactly as a marked `?` check. `logic._flag_open` treats an entry's own `marked` as done (entries carry it only where markable), so vanilla rows and seed checks share one rule.
    7.9 [x] P7.d `tests/test_tracker_http.py` shows `POST` mark/unmark succeeds on a provisional False check and is refused on an accepted False check.

8. [x] Spoilers and display
    8.1 [x] 4.1 A gift read as collected shows its reward in spoiler-free mode, as an opened chest does. Marked checks and provisional False checks do not.
    8.2 [x] 4.2 No new styling or label distinguishes provisional from accepted reads in the tab or OBS (D9).
    8.3 [x] P8.a A test compares the state JSON of an accepted False and a provisional False check and finds them identical except for the button field; no CSS class or label is added in `tracker.css`/`tracker.html`.

9. [x] Patched-flow dump test
    9.1 [x] 5.1 A test marked `dump` builds the patched event flows for the gift checks (any shuffled item) and asserts, for every `bool` and `quest` track entry, that the flow still writes that flag or quest step on every path after the grant step, and on no path that skips the grant.
    9.2 [x] 5.2 For every `played` entry, the test asserts the EventSetting row `<flow>` exists and that the patch neither removes nor skips the grant step in that flow.
    9.3 [x] 5.3 The test skips without `OOT_ROMFS` and passes with it; a synthetic test runs the checker on a built flowchart. With the 1.1.1 dump: 51 entries of 51 gifts pass on the patched flows.
    9.4 [x] P9.a The path checker lives in one place used by both the synthetic and the dump test; on failure it prints the flow, the grant event and the offending path (AGENTS rule 9). `tests/track_paths.py` (`check`, `cut_reaches`), used by `tests/test_track_paths.py` and `tests/test_track_paths_dump.py`; the dump test lists every fault, each with its walk.
    9.5 [x] P9.b The synthetic test includes failing cases: a flowchart where the flag is set on a path that skips the grant, and one where it is not set after the grant; both are reported.

10. [x] Audit CLI `python -m clawshot.tracker.audit`
    10.1 [x] 6.1 Prints one line per gift with `track`: name, each flag and its value, the combined result, whether the default marks file marks it, and `agree`, `disagree` or `no-mark`; ends with a count of disagreements. Added a fourth verdict `unknown` for a gift whose save lacks a flag field (proposed by Claude, for the maintainers).
    10.2 [x] 6.2 It is read-only: it writes nothing to the seed, the save folder or the marks file, and never starts the game. A test asserts that the files are unchanged afterwards.
    10.3 [x] 6.3 No rewards are printed unless `--spoilers` is given.
    10.4 [x] 6.4 It exits 0 with no disagreements and 1 with any disagreement. Tests use synthetic saves and marks.
    10.5 [x] P10.a It reuses `tracker.seeds.load_seed`, `tracker.saves` slot choice and `tracker.marks.MarkStore` read paths rather than reimplementing them; the save folder default is the tracker's own.
    10.6 [x] P10.b A seed from another generator version prints the D8 note and still reports the flags, so a maintainer can audit older saves.
    10.7 [x] P10.c Unreadable inputs (no seed, no save, bad marks file) exit 2 with a one-line error, distinct from a disagreement.

11. [x] Played acceptance checklist (maintainer run)
    11.1 [x] 7.1 [tracker-auto-checks-play.md](tracker-auto-checks-play.md) has one row per track entry: what to do in game, which save to read, and what the tracker and `clawshot.tracker.audit` should show before and after the grant. It says to confirm the seed loaded through the runtime's `mods: <file> <- <path>` log line (rule 3).
    11.2 [x] 7.2 A flag is switched to `accepted = true` only from a recorded maintainer run (`played_by`), never from the marks oracle alone.
    11.3 [x] P11.a The checklist is linked from the roadmap index, and the agent does not start the game or write to a game folder (rule 3).

12. [ ] Docs and done
    12.1 [x] 8.1 `docs/tracker.md` "Gifts read automatically" lists which gift kinds are read automatically, that some still need **Mark done** (trades, shops), the provisional mark behavior, that reading needs a seed made by this version, and that collected gifts show their rewards like chests.
    12.2 [x] 8.2 `uv run ruff format --check`, `uv run ruff check`, `uv run pytest`, and `OOT_ROMFS=<romfs> uv run pytest -m dump` pass. On origin/main 0.2.5 (2026-11-22): ruff clean; pytest 4298 passed, 831 skipped; dump 769 passed, 60 skipped.
    12.3 [x] 8.3 No game data enters the repository. Fixtures are synthetic, and only flag names, flow/event names and sources are committed (rule 1).
    12.4 [ ] P12.a The PR lists every decision made along the way and who proposed it, and repeats Q1–Q3 with any maintainer answers (AGENTS definition of done).
    12.5 [ ] P12.b Commits are small and scoped, add named paths only, and carry an `Assisted-by: <model>` trailer; the PR is MIT-compatible and contains no game files, saves or logs.

### Decisions made during implementation (Claude, 2026-11-22; for the maintainers' review)

- Branch base: first stacked on a local rebase of `feature/tracker-vanilla-rows`; moved onto `main` (0.2.5, with
  PR #37) once that merged (BBender's call). Vanilla `?` rows get `markable` too, and the mark drop and lookup go
  through `every_check`.
- Loading also refuses `track` on a class `more` rule (never shuffled); the spec only named `flag` and added flags.
- Audit method (task 4): a static walk over vanilla and patched flows. A pass needs the flag on exactly the grant's
  paths and no other flow writing it ([audit](tracker-auto-checks-audit.md)). Five candidates failed and stay manual.
  None was left ambiguous, so Q1 has no case pending.
- HC Malon Egg: a D6 equality read on an intermediate quest step would turn false again, so it stays manual rather
  than adding an "at or past a step" read (a product call).
- Mark state: a generic `markable: true` on every check that can be marked (all `?` checks, plus provisional "not
  collected"), used by the server and `tracker.js`; `logic._flag_open` treats an entry's own `marked` as done.
- Button tooltip reworded to fit both cases: "The save may not show this check: mark it done once you have it" /
  "Show this check as the save reads it again".
- Audit CLI: a fourth verdict `unknown` (a flag field missing from the save), not counted as a disagreement;
  `no-mark` (collected but unmarked) is not counted either.
- The D8 warning reads "Gifts read from the game's own flags need a seed made by clawshot <v>; this seed's gifts are
  read as before." and is shown once, only when the seed holds a gift with track entries.
- One existing assertion changed (6.4). The tracker tests live in `tests/test_tracker_track.py`, the path checker in
  `tests/track_paths.py`.
