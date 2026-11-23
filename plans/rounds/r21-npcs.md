# Round 21, track npcs (cs21f): Richard's quest and Cojiro's readers

Agent cs21f, branch `r21/npcs`, base `e9bb0d7`. Brief: [r21-overview.md](r21-overview.md) (lineup row cs21f).
Static research only: nothing here was played. Research scripts and decoded output are in
`E:/OOTRemake/work/r21-npcs/` (`flowdump.py`, `findrefs.py`, `ainbdump.py`, `gamedata_rows.py`; the AINB reads use
round 14's decoded cache `work/r14-steps/ainb/cache`, made with dt-12345's GPL decoder outside the repository; the
flows use round 1's decoded `evfl_all.json`; GameDataList, AI schedules and the Challenge table are read from the
dump with Clawshot's own readers). Build `e0f3ccfa`.

## Outcome

| Item | Change | Kind | Evidence |
|---|---|---|---|
| Richard the Lost Dog (`Market Lost Dog`) | rule gains `'Kakariko Village Gate Open'`; location note rewritten | tightening | static chain below, cited end to end; not played |
| Cojiro (`Cojiro Access`) | rule gains `Epona` | tightening | Kareem in game on 0.2.5; readers listed below |

Both are tightenings (rule (h): safe without play), so no staged check: **READY (merge)** once the sweep and the
gate pass. Files: `src/clawshot/data/world/remake/child_market.toml`, `src/clawshot/data/world/remake/gifts.toml`,
`src/clawshot/data/location_names.toml` (two `where` notes), `docs/logic.md` (one paragraph).

## 1. Richard the Lost Dog: the remake's trigger

**Short version.** In the remake Richard goes missing only after Zelda's Letter has been shown to the guard at
Kakariko's Death Mountain gate (`Npc_Hylia_Soldier_003_GateOpen`). Before that the woman (`Npc_Hylia_052_Child`)
keeps her own Richard: by day both stand at the north end of the Market square, at night both are inside her house
in the back alley. That is exactly what Kareem saw on 0.2.5 before and after Zelda and Impa. Once the gate is open,
her quest schedule puts her in the square at night and a findable Richard roams the back alley at night; leading
him to her at night gives the Heart Piece. OoT Randomizer's `is_child and at_night` (with our `'Time Flows'`)
misses the gate.

### The chain, from placement to the give

Placements are `Banc/Market/Market_Child_Static.bcett.byml.zs` (Hash; coordinates in metres, y up). Logic modules
are the placement file's `AiGroups` (`Logic/Module/...`), decoded node indices as printed by `ainbdump.py`.

1. **Actors.** The woman `Npc_Hylia_052_Child` 10930310377621137817 at (8.1, 100.0, -2.9). Four
   `Animal_Dog_Richard_01`: her own 4292840208460850313 at (8.8, 100.1, 0.7) (module `Market_Child_Prefab_f3a2`,
   reference `Animal_Dog_Richard_01_db8b`) and three findable ones, 2049679476173821084 (-53.8, 97.3, 19.5),
   14327379207017884455 (-56.4, 97.3, 1.3), 14347642661140999207 (9.0, 100.1, 1.9) (module
   `HrlMarket_Child_Dog_Prefab_7574`, references `_0b93`, `_b4e2`, `_77c5`). None has a `Presence` entry; their
   existence is set by the modules. Her links: AnchorAction1 (8.0, 100.1, -2.8), AnchorAction2 (-53.4, 97.9, 28.4)
   inside the house behind `Obj_Door_NPCHouseA` (-51.1, 97.8, 23.9), AnchorAction3 (1.7, 100.1, 26.6) (the
   `HeartPieceAnchor` `SubEvent_FindRichard_GetHeartPiece` sits at (1.66, 100.09, 26.60)), AnchorAction4
   (-5.6, 100.1, 41.8), AnchorAction5 (-3.4, 100.2, 20.1), `Richard_Stay`, `SubEvent_FindRichard_Link_Stay`.
   For orientation: the Hyrule Field entrance `StartPos Market_Entrance` is at (-1.7, 102.2, 65.8), the castle road
   exit at (-2.0, 100.1, -16.1).
2. **The gate flag.** `Npc_Hylia_Soldier_003_GateOpen` (Bool, default false, saved) is written true only by
   `Npc_Hylia_Soldier_003` entry `ShowItem_ZeldaLetter` Event3 and by `Dm_Kakariko_0010` Event18 (the scene of the
   Kakariko gate guard reading Zelda's Letter, `Item_ZeldaLetter` bound to his hand). No AINB writes it (all 914
   flows and 5036 decoded AINB searched with `findrefs.py`). The world already models this act as
   `Kakariko Village Gate Open` = `is_child and Zeldas_Letter` (`kakariko.toml:14`, Overworld.json:1708); world
   `open_kakariko` is fixed at `closed`.
3. **Before the gate: no findable Richard.** `HrlMarket_Child_Dog_Prefab_7574`: nodes 0, 1, 7 (the three findable
   Richards) have `Logic_Create` from OR nodes 31, 26, 27, which take AND nodes 3, 4, 9 =
   `GateOpen` (node 2) AND NOT `SubEvent_FindRichard_RichardRivival` (nodes 29, 30) AND
   `SubEvent_FindRichard_RandomAppear_01/02/03` (nodes 5, 6, 8). When the AND is false a stray (`Animal_Dog_White`/
   `Brown`) is created in that slot instead (nodes 23, 25, 28 from the False outputs).
   `Market_Child_Prefab_f3a2` node 2 (her own Richard) has `Logic_Delete` from node 17 = `GateOpen` AND NOT
   `RichardRivival`: her own dog exists until the gate opens and comes back after the quest.
4. **Her schedule before the quest** (`Component/AIScheduleParam/Npc_Hylia_052_Child...bgyml`, enum names resolved
   as MurmurHash3: `Noon`, `Night`, `Free`, `Action1..5`, `Wander1`, `GoBackHome`): default 06:00 `Noon` at her
   placement (AnchorAction1, `ArrivalAS` `Act_CallDog`), 19:00 `Night` `Action2` (inside the house). Her own Richard
   (`Animal_Dog_Richard_01` schedule, branch `IsReverseCondition` on `Market_Npc_Hylia_052_Child_RunningRichard`):
   06:00 `Action1` (AnchorAction1 (8.9, 100.1, -1.1), beside her), 19:00 `Action2` (AnchorAction2 (-54.7, 97.9, 26.9),
   the house). This is Kareem's night observation. **Kareem confirmed (via Claude, 2026-11-22): on that seed he had
   never shown Zelda's Letter to the Kakariko gate guard**, which fits this chain.
5. **The quest.** RSDB Challenge row `Work/Challenge/SubEvent_FindRichard` (`work/r14-steps/challenges.json`):
   `DependFlagName` = `Npc_Hylia_Soldier_003_GateOpen`; steps `NotReady` (default) -> `Ready` -> `Step01` ->
   `Complete` (GameDataList enum `Step_SubEvent_FindRichard`). The flag also gates Ready [inference: all five
   challenges with a `DependFlagName` follow a story prerequisite, e.g. `MiniGame_HorseRace` on Epona,
   `SubEvent_GetFireArrow` on the Water Temple; not needed for the rule, item 3 already gates the dog]. Step
   participants' schedules, `Pack/AIScheduleParam.pack.zs` `SubEvent_FindRichard_Ready_Npc_Hylia_052_Child`
   (Step01 inherits it): `Free` 06:00 `Wander1` (her guide rail, back alley to the square, `Act_LookingFor`), 15:00
   `Action4`, 17:00 `Action5`, 19:00 `Action3` (1.7, 100.1, 26.6) until morning.
   `SubEvent_FindRichard_Ready_Animal_Dog_Richard_01`: `Noon` 05:00 `GoBackHome`, `Night` 21:00 `Wander1` (the three
   findable Richards' guide rails all lie at x -58..-29, the lower western streets that hold her house door);
   once `Market_Npc_Hylia_052_Child_RichardGoHome` is set, `Action3`.
6. **Bringing him.** `Market_Npc_Hylia_052_Child_BringRichard` (unsaved Bool) is set true only by
   `HrlMarket_Child_Dog_Prefab_7574` node 10, driven by OR node 11 of the three findable Richards' `IsTakenAway`
   (following Link); `BringDog` likewise for the strays (nodes 16-18). Her own Richard is not in that OR.
7. **The talk and the give.** `SubEvent_FindRichard` entry `Ready_Npc_Hylia_052_Child_Talk`: on the first talk
   (`Market_Npc_Hylia_052_Child_IsAfterFirstExplain` false) she explains and checks `BringRichard`; after that,
   `EventQueryTimeDivision` case 0 is daytime chat (`RichardTalk_Wander`), case 1 is `nightTalk_moving` -> Event14
   `BringRichard`. Case 1 is night: `Npc_Goron_012_Child`'s case 1 is `NightTalk`, and her own retry branch
   (`Npc_Hylia_052_Child` `Market_SubEvent_FindRichard_Retry_Talk`) says on case 0 that she searches by day and
   Link should search at night. The give: `SubEvent_FindRichard_ClearEvent` -> Event50
   `SubEvent_FindRichard_IsCompleted_Exp` (BoolExp `Step_SubEvent_FindRichard` vs `Complete`; case 0 = true) ->
   case 1 Event16 `NpcCommon_HandOver_NpcToPlayer_NoDisplay` `Obj_Heart_Piece` (the census check
   `SubEvent_FindRichard/Event16`), Event55 `SubEvent_FindRichard_GetHeartPiece`, Event32 step `Complete`; later
   finds (case 0) give Event73 `Obj_Rupee_Blue`. `ClearEvent` has exactly three callers, each behind a
   `BringRichard` true branch: `SubEvent_FindRichard` Event52 (after Event14), Event131 (after Event129) and
   `Npc_Hylia_052_Child` Event37 (after Event36, the 72-hour retry).
8. **After the quest.** `ClearEvent_Ending` clears the three `RandomAppear` flags, sets
   `Market_SubEvent_FindRichard_MadamSayThankyou`, the found-time stamp and `RichardRivival` (her own dog returns);
   `FindRichard_ResetTimeCheck` resets it after 72 in-game hours for the blue-rupee repeat (BoolExp
   `Market_SubEvent_FindRichard_Retry` = NOT `RichardGoHome` AND completed).

### Rule

`is_child and (at_night and 'Time Flows') and 'Kakariko Village Gate Open'` (was OoT Randomizer's
`is_child and at_night`, Overworld.json:1682). Items 2, 3, 6 and 7 make the gate flag necessary for the Heart
Piece: a **tightening**, so rule (h) needs no played check. Night stays: the night branch and the night schedules
(items 5, 7) are the only cited route; whether a first-ever talk by day with Richard in tow would also pay (the
first-talk branch has no time test) is not claimed, and Richard is scheduled away by day.

Not cited, and not relied on: what sets `SubEvent_FindRichard_RandomAppear_01/02/03` (default false, reset bits 9,
saved; no flow or AINB writes them true) is engine code [inference: one is picked when the area loads, so one of the
three Richards appears]. If none were ever set the Heart Piece would be unobtainable; this has never been seen and
the check has been in logic since round 4. No in-game check is staged for it (the rule change does not rest on it).

**Location note** (`location_names.toml`): child, night, after showing Zelda's Letter to the Kakariko gate guard;
from 21:00 Richard roams the back alley; lead him to his owner, who waits in the square at night.

**Kareem, optional when he next plays a child seed (not a staged check):** after showing the letter, go to the
Market after 21:00: the woman should stand in the square, south of its centre, and a Richard should be in the back
alley; before showing it, nothing changes (both home at night).

## 2. Cojiro: what reads the trade events

Kareem, in game on 0.2.5: woken adult Talon complains about Ingo and stays; Anju by day says Link woke him but
still has to help him. The chain's flows were not researched (instruction: vanilla up to the Biggoron Sword).

Readers of `Wake Up Adult Talon` (kakariko.toml:139), `Cojiro Access` (:13), `Odd Mushroom Access`
(lost_woods.toml:13), `Odd Potion Access` (kakariko.toml:280) and the later trade events (searched over `src/`,
`tests/` and the data):

| Event | Read by | Part of the vanilla chain? |
|---|---|---|
| `Wake Up Adult Talon` | `Cojiro Access` | yes |
| `Cojiro Access` | `Kak Anju Trade Pocket Cucco` (kakariko.toml:22, keep_vanilla R13); `Odd Mushroom Access` | yes |
| `Odd Mushroom Access` | `LW Trade Cojiro` (lost_woods.toml:23, gift class `more`); `Odd Potion Access` | yes |
| `Odd Potion Access` | `Kak Granny Trade Odd Mushroom` (:283, keep_vanilla); `Poachers Saw Access`; **`Kak Granny Buy Blue Potion`** (kakariko.toml:285, remake/gifts.toml:98) | the potion sale is **not** a trade step: a separate location (keep_vanilla since round 8, gift class `rewrite`, vanilla item `Blue Potion`, class progression) |
| `Poachers Saw` ... `Eyedrops Access` | the next trade location and event each (`LW Trade Odd Potion`, `GV Trade Poachers Saw`, `DMT Trade Broken Sword`, `ZD Trade Prescription`, `LH Trade Eyeball Frog`, `DMT Trade Eyedrops`) | yes |
| (chain's end) `Claim Check`, vanilla at `DMT Trade Eyedrops` | **`DMT Biggoron`** = `is_adult and Claim_Check` (death_mountain_trail.toml:49): a **shuffled** location (gift class `rewrite`) and an **always hint** (`data/hints.toml` `always`) | no |

So more than the chain and its tracker rows depends on them: the shuffled, always-hinted `DMT Biggoron` (through the
vanilla Claim Check) and Granny's potion sale (directly). Per the brief, `Cojiro Access` gains Epona:
`is_adult and at_day and 'Wake Up Adult Talon' and Epona` (`remake/gifts.toml`; `Epona` is the existing event,
`remake/child_lon_lon_ranch.toml`). Tightening, from Kareem's play. Not known (flows not researched): whether Talon
must be woken again after Epona is freed; the logic only needs both events, which never un-happen.
The `Kak Anju Trade Pocket Cucco` note now says "by day, once Talon is woken and Epona freed".

## Decisions made here

- Richard: add the Kakariko gate event, keep night (cs21f, from the cited chain; tightening).
- Cojiro: add `Epona` (cs21f per the brief's rule, from Kareem's play; tightening).
- No staged check: neither change loosens logic (cs21f).

## Checks

**Focused tests** (outside the lock, `-n 2`, `CLAWSHOT_WORKERS=1`, no game running), 13 world/name/hint/tracker
files: 176 passed, 6 skipped, 1 failed. The failure was `test_world_clock.py::
test_field_arrival_comes_before_zelda_without_items_and_night_waits_for_the_sendoff`, which used Richard only as a
"child night check" probe (`can_access` false after the send-off, payload: the new rule text). The probe is now
`Market Night Balcony Wonderitem 1` (`is_child and (at_night and 'Time Flows')`, no other gate); the test's
contract (night waits for the send-off) is unchanged. Rerun with the new test: 3 passed.

**New test** `test_world_remake.py::test_richard_waits_for_the_kakariko_gate_and_cojiro_for_epona`: with every
vanilla item but Zelda's Letter, Time Flows holds, the gate event does not and Richard is out of logic; with every
item but Epona's Song, Talon is woken, Epona is not and Anju's Cojiro trade is out of logic; with everything, both
are in logic. With `e9bb0d7`'s two override files it fails at the Richard assertion (`assert not True`); with only
the base `gifts.toml` it fails at the Cojiro assertion; on head it passes. `ruff format --check`, `ruff check`:
clean.

**Rebases while frozen.** `ff6504e` (on `f7ba65f`) -> `534f490` (on `e8dc77d`, PR #39) -> `f25c4a3` (on `3667df5`,
sticks) -> `f426b94` (on `ff78b5e`, tracker). Focused world/name tests after each: 43, 44, 44, 44 passed; ruff clean.

**Sweep** (gate lock held by cs21f from 23:59, no game running, 6 workers; `E:/OOTRemake/work/r21-npcs/sweep.py`,
canonical native-prepared recipes as round 20's audit, seeds 21060000+): run on `f25c4a3` (main `3667df5`).
Main then moved to `ff78b5e` (tracker, UI and docs only: no file under `data/`, `generate/` or `world/`); Claude
ruled the sweep stands and the gate runs on the rebased head. The gate runner refuses unless our patch outside this
file is byte-identical to the swept one.

| Recipe | Seeds | Accepted | Exhausted | First-try failures (seeds) | Max attempts |
|---|---|---|---|---|---|
| Broad (CS1, `work/r18-fill/settings.txt`) | 200 | 200 | 0 | 4 (21060041, 074, 111, 144) | 2 |
| Defaults | 50 | 50 | 0 | 1 (21060004) | 2 |
| Recommended | 50 | 50 | 0 | 3 (21060004, 012, 036) | 2 |

Sweep 463 s of generation, stage 490.5 s, exit 0. Rows: `work/r21-npcs/sweep-rows.jsonl`, `sweep-results.json`.

**Full gate** on the head after this receipt (same hold): result in `work/r21-npcs/gate-results.json` and the
`cs-r21` handoff.
