# Round 21, Track checks — cs21g

Branch `r21/checks`, base `e9bb0d7` (0.2.5 plus the round 20 close records). Model: `anthropic/claude-opus-5-5`.
Kind: research (staging only). Staging and receipts: `E:/OOTRemake/work/r21-checks/` (launchers, checklist and
mods in `ingame/`). No game started, nothing written under `E:/Games/Hookshot` or any Longshot folder, no player
seed opened, no save edited. Save backups were read and copied, never written.

## Scope

Stage round 20's owed play checks (r20-overview.md, "Carried to round 21"): partial trials counts 1-5, the Light
Arrows scene after Shadow and Spirit, Very strong hints, and the tracker reading Darunia's gift from a real save.
Fix round 20 doc gaps; list round 20's other unplayed claims as questions.

## Result in one table

Ordered by what Kareem gets for his time. All launchers pin **Longshot 3.0.0** stable
(`builds\stable\v3.0.0\bin\longshot.exe`), one mod, `HOS_FS_OVERLAY` empty, private profile per packet; no
launcher references `hookshot.exe` (grep). Times are estimates, not measured. Entry point:
`E:/OOTRemake/work/r21-checks/ingame/START HERE.md`; steps and expected results: `ingame/CHECKLIST.md`.

| # | Packet (seed) | Covers | Parts | Time | Status |
|---|---|---|---|---|---|
| 1 | P1 (21217000) | New Game writer at count 1 (beams, line); Very strong hints, 10 stones; zero-stone bridge | 1A, 1B, 1C | 45-70 min | **played 2026-11-23**: stones PASS, entry PASS; Forest end not finishable with P1's items |
| 1b | S1 (castle save + one edit; mod of seed 21217000) | Count 1 end: Forest trial, barrier scene, pots, elevator, Continue | one | 15-25 min | staged, dry run pass, boot check owed (Claude) |
| - | Darunia tracker | Tracker reads `Dm_Goron_0030` from real saves | none | 0 | **checked by agent** (below) |
| 2 | C1 control (21217000, six trials) | Native six beams and line; only if P1 is unclear | one | 8-10 min | staged |
| 3 | S2 (castle save + one edit; mod of seed 21217026) | Count 2: a non-final core keeps the tower shut | S2-a (S2-b withdrawn) | 10-15 min | **S2-a played PASS**; S2-b needs Golden Gauntlets |
| 4 | S3, S4, S5 (same save; mods of seeds 21217020, 21217041, 21217007) | Counts 3, 4, 5: beams and line at entry, first core keeps the tower shut | one each | 10-15 min each | staged (replace New Game P3-P5) |
| - | S2 control (same edited save, seed 21217026 built with six trials) | Same beams from the save, native line | one | 5-8 min | staged, optional |
| - | P2-P5 New Game route | As S2-S5 plus each count's New Game writer | `ingame/new-game-route/` | 3-5 h in all | not recommended: starts miss the Forest trial's items |
| 5 | P6 (21217201) | Light Arrows scene with only Shadow and Spirit awakened; vanilla bridge after it; count 5 at entry | 6A-6G | 3-4.5 h | staged, optional; question 2 |

All packets: Forest open, Door of Time open, free time travel, fast start `intro saria kaepora`, Chest shuffle,
+3 hearts (P6 +7). P1-P5 and C1: bridge `stones` count 0. P6: vanilla bridge. Exact settings strings: each mod's
`spoiler.json` (`settings_string`); build script `build_seeds.sh` (P1-P5, C1) and the P6 command in this file's
receipts below.

## Why every count needs its own New Game (without a save edit)

Superseded for counts 2-5 by the save route below; this explains the New Game route that P1 and the alternatives use.

`trials_count` writes only new-game initial values (`patch/trials.py` `initial_values`: the skipped trials'
`InsideGanonCastle_Dungeon_BarrierRemove_<trial>` Bools and `InsideGanonCastle_Dungeon_Barrier_Count`). A save
stores those fields, so an existing save keeps its own values (r20-trials.md, "new-game defaults do not migrate
played saves"). Every count therefore needs a New Game and the natural route to adult (no Debug age change):
Malon/Talon/courtyard/Zelda, Impa's send-off, the open Door, the Master Sword. That route is parts A and B
(25-40 min together) of every trials packet. A natural adult save (the control) can only show count 6.

Trial choice: each packet's seed was picked (`generate/trials.py` `remaining`) so its remaining trials looked
cheapest to clear with supported starting items (`starting.py` `CHOICES`). **That choice was wrong (found in play,
2026-11-23):** it read the base `data/world/ganons_castle.toml`, not the remake overrides in
`data/world/remake/adult_ganons_castle.toml` that main's logic applies on top (round 4, commit `522c4ad`). The
effective rules (printed with `world.load.load_world`) need Song of Time, Hover Boots and a Hookshot for the
Forest trial's onward door and Golden Gauntlets for the Shadow trial's end and the Fire trial's door. P1-P5's
starts do not cover them; see "Play results and castle research" below.

What each count adds: P1 alone already shows all six beam removals (five pre-set, Forest by its own core) and the
last-core tail at count 1. P2 is the only packet showing that a non-final core keeps the tower shut, i.e. that
the counter starts at N. P3-P5 differ from P2 only in the starting value.

## Static verification of the staged bytes

`verify_packets.py` reads each staged mod's own `GameDataList` defaults and USen first-view line
(`verify-packets.json`):

| Mod | Count default | Pre-removed | All-clear / 0090 defaults | First-view line |
|---|---:|---|---|---|
| r21-trials1 | 1 | Fire, Water, Shadow, Spirit, Light | false / false | Trials remaining: Forest. |
| r21-trials-control | 6 | none | false / false | native Rauru line |
| r21-trials2 | 2 | Fire, Water, Spirit, Light | false / false | Trials remaining: Forest, Shadow. |
| r21-trials3 | 3 | Water, Spirit, Light | false / false | Trials remaining: Forest, Fire, Shadow. |
| r21-trials4 | 4 | Water, Light | false / false | Trials remaining: Forest, Fire, Shadow, Spirit. |
| r21-trials5 | 5 | Water | false / false | Trials remaining: Forest, Fire, Shadow, Spirit, Light. |
| r21-lacs | 5 | Shadow | false / false | Trials remaining: Forest, Fire, Water, Spirit, Light. |

Determinism: P1 built twice from the same head, all 142 files byte-identical (`trials1-first-build.sha256`).
P1 vs C1 (same seed, trials 6): same 142 paths; differences are placements (the tower rule changes fill),
`GameDataList`, the 16 `Mals` archives, the size table, spoiler and play note. Full per-file SHA-256 per mod:
`mod-manifests.json` (source head `e9bb0d77`). Launcher dry runs: 25/25 exit 0 (`launcher-dry-runs.json`); the
control's copied save equals its source (SHA-256 `dd3126bf...`).

## Very strong hints

Bundled into P1: ten stones on the child route (Kokiri Forest three, Lost Woods bridge, Hyrule Castle two, Temple
of Time courtyard four) with the expected text from the spoiler in the checklist. No control: the distribution
only changes which hint each stone gets; the stone writer is the one Balanced uses (played since round 7), so a
Balanced arm would show different texts and prove nothing. Seed 21217000's distribution: 40 stones, woth 6,
barren 14, item 13, random 5, sometimes 2 (weights woth 8, barren 4, item 4; woth is capped by the seed's
required areas). This is a generator observation, not a play claim.

## Darunia's gift in the tracker: checked from real saves

The tracker side needs no game: the question was whether main's tracker picks `HavePlayedEvent.Dm_Goron_0030` up
from a real save (tracker-in-logic.md Q6, "Unconfirmed"). A read-only scan (`scan_saves.py`) found a game-written
pair from Kareem's Longshot play on 2026-11-13 (`save-backups/2026-11-13_150340-...-darunia-3`, newest slot
`slot_05`, flag false; `...150502-...-darunia-4`, newest `slot_00`, flag true). `darunia_tracker.py` copies each
into a private folder and runs main's `TrackerSession` (private marks file) on private default seed 21217100,
where `GC Darunias Joy` keeps its vanilla item:

| Save | Flag | Row "Darunia's Dance: Goron Bracelet" | Logic inventory Goron Bracelet |
|---|---|---|---|
| before | false | collected false ("—"), basis inventory | 0 |
| after | true | collected true ("✓"), basis inventory | 1 |

Headless Chrome (`darunia_ui.py`, in-memory preferences) shows the same rows in the Tracker tab:
`E:/OOTRemake/work/r21-checks/darunia/ui-before.png` and `ui-after.png` (viewed). Receipts
`darunia-tracker-result.json`, `darunia/ui-proof.json`. Both reads warn that the save cannot be tied to the seed
(expected: the saves come from another seed); in-logic counts were not compared for that reason. Not covered:
a live save being written while the tracker watches (same reader, same file format). PR #39 (cs21b) may change
how gifts are read; rerun `darunia_tracker.py` after it merges.

## Light Arrows scene: why only P6 is honest

Native trigger (r19-lacs.md): AllSage Event25/26 read `HavePlayedEvent.Dm_Awake_Spirit` and `.Dm_Awake_Shadow`;
EscapeDungeon Event130/139 dispatch the last-sage sequence; the Temple trigger reads AllSage Step02. A check only
discriminates if the scene plays with Shadow and Spirit awakened while Forest, Fire or Water is not.

- Natural saves: today's read-only scan of every backup without a played-seed name (`scan-all.jsonl`, 747
  distinct `progress.sav` contents) agrees with round 19's survey: 28 have both late awakenings, all 28 with the
  scene already played and Forest, Fire and Water also done; none has only one late awakening; no save holds a
  partial trial count (only 6 and 0). The latest natural pre-scene saves (2026-11-11 after Water) have Forest,
  Fire and Water done, so finishing Shadow and Spirit there cannot tell the new logic from the old.
- A save edit setting the two awakening Bools would skip what the awakening scenes themselves write (the last-sage
  dispatch, AllSage steps), so it would test the reader, not the chain: not honest.
- P6 is a New Game with supported starting items for both temples (no Light Arrows), Lens of Truth in a Goron City
  chest (silver boulders), keys in their own temples. It adds a negative step (after Shadow only: no scene) and,
  after the scene, the vanilla bridge forming and the castle at five trials (so P5 can be skipped).
  P6 command: seed 21217201, `--forest open --door-of-time open --skip intro saria kaepora --logic
  free_time_travel=true --starting-hearts 7 --trials-count 5 --starting-items "Ocarina of Time" "Nocturne of
  Shadow" "Requiem of Spirit" "Zeldas Lullaby" "Song of Storms" Bow "Dins Fire" Longshot "Hover Boots" "Iron
  Boots" "Silver Gauntlets" "Mirror Shield" "Bomb Bag (40)" "Megaton Hammer" "Magic Meter (Double)"`.

## Control launchers

Rule (1) asks for a control per check. Only the trials change castle behaviour on main: C1 is the same seed and
settings with six trials, on a copy of the natural adult save `2026-11-11_2050-main-after-water/.../slot_04`
(Lon Lon Ranch), optional per round 20's play-budget rule (controls only for unclear results). Very strong (same
writer), Darunia (no game behaviour) and the Light Arrows scene (logic-only change; the scene is native) get none.

## Doc gaps fixed

- `src/clawshot/data/settings.toml:8-10`: the evidence comment still capped the Fortress at one rescue; now records
  the 2026-11-21 Longshot 3.0.0 four-rescue pass (r20-cows.md "Played acceptance"). Comment only; focused
  `tests/test_settings.py` 15 passed, `tests/test_app_schema.py` 34 passed (`-n 2`, `CLAWSHOT_WORKERS=1`).
- Every other round 20 claim in `docs/`, `README.md` and `settings.toml` matches the records (scout sweep:
  partial trials, Very strong and the Light Arrows scene still say not played; zero trials, token bridge, start,
  hints, cows and Fortress say what was played).

## Save route for counts 2-5 (Claude's request, 2026-11-22, from Kareem's question)

Kareem asked whether a trials save can replace the New Game route. `scan_castle_saves.py` read every non-seed backup
(including `2026-11-20_real-longshot-profile-copy`) for adult saves with Light Arrows, count 6, no trial removed
and all-clear false (`scan-castle.jsonl`). The real-profile copy is past the trials in all six slots (count 0,
all-clear true). Exactly one save qualifies: `2026-11-17_213402-r17-chest-hunt-main-save-1/<uid>/slot_05`, a
game-written autosave of 2026-11-16 12:42, caption **InsideGanonCastle**, Light Arrows scene played, the first-view
scene `Dm_InsideGanonCastle_0003` **not** played, 0090 false, Ganon's boss key not held. Its inventory (main's
tracker reader) covers Forest and Shadow and every trial entry: Fairy Bow, Light and Fire Arrows, Din's Fire,
Longshot, Hover Boots, Megaton Hammer, Lens, Mirror Shield, Goron Tunic, 3 Bombchus, 2 bottles, double magic,
12 hearts; Silver (not Golden) Gauntlets.

**The edit** (`make_save_profiles.py`, proof `save-edit-proof.json`): per profile, a copy of that slot with
`InsideGanonCastle_Dungeon_Barrier_Count = N` and `InsideGanonCastle_Dungeon_BarrierRemove_<trial> = true` for each
trial the packet's seed skips. The values are taken from `patch/trials.initial_values(seed, N)` and asserted equal
to the expected set; in-place u32 changes only, same file length; re-parsed diffs equal the intended entries
exactly (count 2: 5 entries/5 bytes; 3: 4/4; 4: 3/3; 5: 2/2); Bool64 keys unchanged; source SHA-256 `5b95d18a...`
unchanged after. Both S2 arms carry the identical edited file (SHA-256 `0f61f64e...`). Profiles are prepared once;
the S launchers never recopy and stop if the prepared save is missing. Mods: the existing `r21-trials2`..`5`
(their trial text matches the edits' subsets) and a new `r21-trials2-control` (seed 21217026, P2 settings, six
trials; verified count 6, no removals, native line).

| Route | Counts 2-5 | Kareem's time |
|---|---|---|
| New Game (P2-P5) | four New Games, 25-40 min each to adult, then castle | 3-5 h |
| Save (S2-S5) | Continue inside the castle | S2 25-35 min, S3-S5 10-15 min each: 55-80 min |

**What the edit route cannot prove:** (1) the New Game writer: that a New Game on the build starts with those
values. P1 proves it end to end at count 1; the other counts use the same writer, and each staged build's
defaults are checked statically (`verify-packets.json`). (2) The early castle entry of a New Game seed (count
bridge before the Light Arrows story); the save has the story and the vanilla bridge done. P1 covers it once.
(3) The control cannot separate build from save for castle behaviour: with the same edit both arms hold the same
state, so they differ only in the first-view line. What it does prove: the game's own castle reading a partial
state as the writer sets it: which beams stay, the counter starting at N (a non-final core keeps the tower shut),
the last-core scene, pots, elevator and persistence, plus the build's line.

**Proposal (cs21g):** P1 stays end to end as the New Game proof; S2 replaces P2 (both trials); S3-S5 replace P3-P5
at entry plus one trial. The New Game route stays in `ingame/new-game-route/`.

## Play results and castle research (2026-11-23)

**Results** (Kareem, Longshot 3.0.0, via Claude): see "Played" below. Two failures were staging errors, not game
or logic faults: P1-1C's Forest trial and S2-b's Shadow trial need items those packets lacked.

**Trial names, beams and doors are right** (read-only dump, `castle_actors.py`, `castle_links.py`,
`castle-actors.json`). Each trial's last room holds its `Obj_InsideGanonCastle_Core_*` and a
`Gimmick_ArrowLight_BarrierRemove_<trial>` module that writes `InsideGanonCastle_Dungeon_BarrierRemove_<trial>`,
and each core room's door carries `InsideGanonCastle_LookBarrierFromDoor_<trial>`:

| Trial | Rooms (core) | Hall door (x, z) | Core module |
|---|---|---|---|
| Forest | 2, 3, (4) | (16.1, 7.8) | Room_04_Prefab_0198 |
| Water | 5, 6, (7) | (33.0, -21.0) | Room_07_Prefab_bb4c |
| Shadow | 8, (9) | (16.1, -49.8) | Room_09_Prefab_676e |
| Fire | 10, (11) | (-16.1, -49.9) | Room_11_Prefab_fe03 |
| Light | 12-14, (15) | (-33.1, -21.0) | Room_15_Prefab_98a7 |
| Spirit | 16, 17, (18) | (-16.1, 7.8) | Room_18_Prefab_bd08 |

**Golden boulders.** `LiftableParam.LiftGrade` hashes resolve (murmur3) to `None` (Obj_LiftRock_A), `Middle`
(Obj_LiftRock_B: the silver-gauntlet rocks in Desert Colossus, Gerudo Valley, Zora's Fountain, Goron City) and
`High` (Obj_LiftRock_C, only in `GanonCastle_Static`, the Great Fairy's golden block, and inside the castle).
Four High rocks in the castle:

| Rock (Hash) | Where | Effect |
|---|---|---|
| Obj_LiftRock_C_01 `7808482170470849591` | Hall, 1.8 m before the Light door | saved by `InsideGanonCastle_Dungeon_Room01_LiftRock` (Room_01_Prefab_cbd5) |
| Obj_LiftRock_C_01 `6251811700274725607` | Hall, 1.8 m before the **Fire** door | saved by `HavePlayedEvent.Dm_InsideGanonCastle_0035` (Room_01_Prefab_99d3) |
| Obj_LiftRock_C_01 `3853917559410573871` | Fire room 10, among its silver rupees | the "Inside Pillar" rupee |
| Obj_LiftRock_C_05 `8144266723486145695` | Shadow room 8, beside the Golden Gauntlets chest `17657623307936361670` | Room_08_Prefab_7f41 binds it to player air wall `12553345302708464522`; beyond, floor switch `8991881348786264121` sets `InsideGanonCastle_Dungeon_Room08_HummerSwitch` and opens core-door lattice `13976063739260614866` (Room_08_Prefab_4fac) |

Kareem's report (a golden boulder before the Light trial, one inside the Shadow trial, and one in the Fire trial)
matches: the Fire trial has two (its door and its pillar).

**Forest fan room (room 3):** Song of Time block `11362469908826992779` with its sign, under a silver rupee by the
entrance; extending platform `5390936718397577672` moved by floor switch `7606689984675378176`
(`InsideGanonCastle_Dungeon_Room03_StepSwitch` -> `ExtendingPlatform_ON`, Room_03_Prefab_fbb4) carrying grapple
target `13035196076992852431`; grapple target `8131019826575446689` over the entry door; five silver rupees open the
core door (`Room03_SilverRupee`, Room_03_Prefab_71a7).

**Main's logic already has all of this.** `data/world/remake/adult_ganons_castle.toml` (round 4, `522c4ad`, with
`tests/test_world_remake_adult_ganons_castle.py`) overrides the base file, and `load_world` gives: Fire door
`can_use(Golden_Gauntlets) and (tunic)`; Shadow ending `can_use(Golden_Gauntlets) and (lens or Longshot+Hover)`;
Forest ending `5 silver rupees and can_play(Song_of_Time) and can_use(Hover_Boots) and can_use(Hookshot)`; the Fire
pillar rupees at `ganons_castle.toml:169,171` stand. No logic change: the tightening slot Claude offered was
withdrawn after this was posted. Lesson: take a packet's starting items from `load_world`, never the base toml.

**S1 (built).** The castle save with the count-1 edit (`make_save_profiles.py`: count 1, Fire/Water/Shadow/Spirit/
Light pre-cleared, 6 entries/6 bytes, SHA-256 `1fc145d0...`, identical in both arms), mod `r21-trials1`, control
`r21-trials-control` (same seed, six trials). Its gear meets the effective Forest rule: Ocarina of Time, Song of
Time, Hover Boots, Longshot, Din's Fire, Fire and Light Arrows (main's tracker reader on that save), and Kareem
finished this trial from the same save in S2-a. Launchers `S1 count 1 Forest to the tower.bat` and
`S1 control six-trial build (optional).bat`; 32/32 dry runs exit 0.

**Tracker note (for the tracker owners, not changed here):** `tracker_logic.toml:427` leaves silver rupees unmapped
("no audited save field"), so the tracker's in-logic search never reaches a trial ending (here "Ganons Castle Forest
Trial Ending" stays unreachable on the S1 save, whose gear finishes it in play). Each castle room has a saved clear Bool
(`InsideGanonCastle_Dungeon_Room03_SilverRupee`, `Room10_`, `Room14_`, `Room16_`) worth auditing.

## Questions

1. ~~Counts 3-5: New Game, skip, or a documented save edit?~~ Superseded by the save route above (Claude's request):
   S2-S5 from Kareem's own castle save with one documented edit; P1 keeps the New Game proof.
2. **The Light Arrows check (P6) costs 3-4.5 hours of Shadow and Spirit play. Play it, or leave the logic on its
   static evidence and have Kareem report if his own seed ever gives him Shadow and Spirit before the other
   three?** Proposed by cs21g: the watch item; P6 stays staged.
3. **The seed play note says "Starts are built, not played"**, but round 20's starting-inventory packets passed in
   game (A/B and A-v2). That line is generator output (product text, changes seed bytes): change it in a product
   track, or keep it because only the packet's items were played?
4. **`data/tracker_logic.toml` (`[story."Goron Bracelet"]` source) and `docs/tracker.md` still say the real-save
   read is unconfirmed.** This track confirmed it from real saves (above); the owners (pr39 for the tracker data,
   tracker for its docs) can update the line, or keep it until Kareem sees it live.

Round 20 claims still unplayed and not covered by these packets (scout inventory, each is evidence for retained
rules, research, or text layout, not a new round 20 behaviour unless noted):

5. **r20-audit.md:121-201 ranged-pickup rows ("range unplayed": Boomerang/Hookshot ranges and exact remake
   routes for about 50 Skulltulas, rupees and silver rupees) and :348-361 switch questions Q1-Q20: stage any?**
   These keep imported rules; nothing new shipped on them.
6. **r20-audit.md:22-23: the four shipped tightenings (Windmill heart piece, Graveyard Boomerang branch, Ice
   Cavern blue rupee, Dodongo torch room) rest on static evidence; tightening is safe, so no play planned. Agree?**
7. **Kakariko rooftops without the owl (r20-audit.md:71-74): still Kareem's question to answer.**
8. **The late first Forest-exit ordering (r20-audit.md:374-377, docs/settings.md:619-620) stays unplayed: stage it?**
9. **Cow persistence covers one shared Bool, not per-cow completion or cow shuffle (r20-cows.md:160-171, :200);
   no cow behaviour shipped. Keep as research?**
10. **Open Zora's Fountain / Kakariko gate (r20-open.md): research only, no setting; Kareem: "not yet". Keep?**
11. **Round 20 text (trial line, hints, altar) was played in English only; the 15 other languages are dump
    read-back only (r20-trials.md:222-223, r20-hints.md:42-44). Accept, or stage one non-English look?**

## Receipts (all under `E:/OOTRemake/work/r21-checks/`)

`build_seeds.sh`, `build-seeds.log`, `make_launchers.py`, `launcher-dry-runs.json`, `mod-manifests.json`,
`verify_packets.py`, `verify-packets.json`, `trials1-first-build.sha256`, `scan_saves.py`, `scan-main.jsonl`,
`scan-all.jsonl`,
`darunia_tracker.py`, `darunia-tracker-result.json`, `darunia_ui.py`, `darunia/ui-before.png`,
`darunia/ui-after.png`, `darunia/ui-proof.json`, `readout.py` (post-play save read-out), `ingame/START HERE.md`,
`ingame/CHECKLIST.md`, 31 launchers (17 in `ingame/`, the 14 New Game P2-P5 alternatives in
`ingame/new-game-route/`), `scan_castle_saves.py`, `scan-castle.jsonl`, `make_save_profiles.py`,
`save-edit-proof.json`.
Seeds were built at `CLAWSHOT_WORKERS=1` with no game running, one at a time; no gate, sweep or full suite (no
product behaviour changed).

## Played

Kareem, Longshot 3.0.0, 2026-11-23 (via Claude): P1-1A/1B all ten Very strong stone texts correct; P1-1C entry
PASS (one Forest beam, "Trials remaining: Forest.", no pots), its Forest trial not finishable (mis-staged); S2-a
PASS (Forest trial done, Forest beam down, Shadow beam and tower barrier stay); S2-b not finishable (Golden
Gauntlets). Boot checks of the S1 launchers are Claude's.
