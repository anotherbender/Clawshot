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
| 1 | P1 (21217000) | Trials count 1 end to end; Very strong hints, 10 stones on the route; zero-stone bridge on approach | 1A, 1B, 1C | 45-70 min | staged, dry runs pass, boot check owed (Claude) |
| - | Darunia tracker | Tracker reads `Dm_Goron_0030` from real saves | none | 0 | **checked by agent** (below) |
| 2 | C1 control (21217000, six trials) | Native six beams and line; only if P1 is unclear | one | 8-10 min | staged |
| 3 | P2 (21217026) | Count 2: a non-final core keeps the tower shut, the last opens it | 2A-2D | 55-85 min | staged |
| 4 | P3 (21217020), P4 (21217041), P5 (21217007) | Counts 3, 4, 5: beams and line at entry, first core keeps the tower shut; P3 can finish | 3A-3D, 4A-4C, 5A-5C | 40-60 min each (P3 full +20-30) | staged; question 1 |
| 5 | P6 (21217201) | Light Arrows scene with only Shadow and Spirit awakened; vanilla bridge after it; count 5 at entry | 6A-6G | 3-4.5 h | staged, optional; question 2 |

All packets: Forest open, Door of Time open, free time travel, fast start `intro saria kaepora`, Chest shuffle,
+3 hearts (P6 +7). P1-P5 and C1: bridge `stones` count 0. P6: vanilla bridge. Exact settings strings: each mod's
`spoiler.json` (`settings_string`); build script `build_seeds.sh` (P1-P5, C1) and the P6 command in this file's
receipts below.

## Why every count needs its own New Game

`trials_count` writes only new-game initial values (`patch/trials.py` `initial_values`: the skipped trials'
`InsideGanonCastle_Dungeon_BarrierRemove_<trial>` Bools and `InsideGanonCastle_Dungeon_Barrier_Count`). A save
stores those fields, so an existing save keeps its own values (r20-trials.md, "new-game defaults do not migrate
played saves"). Every count therefore needs a New Game and the natural route to adult (no Debug age change):
Malon/Talon/courtyard/Zelda, Impa's send-off, the open Door, the Master Sword. That route is parts A and B
(25-40 min together) of every trials packet. A natural adult save (the control) can only show count 6.

Trial choice: each packet's seed was picked (`generate/trials.py` `remaining`) so its remaining trials are the
cheapest ones a New Game can clear with supported starting items (`starting.py` `CHOICES`): Forest (Bow, Din's
Fire, Light Arrows), Shadow (adds Longshot, Hover Boots, Megaton Hammer), Fire (adds Goron Tunic, Golden
Gauntlets). Water needs a bottle and Spirit Bombchus, Light the Lens; none is a supported start, so P4/P5 stop
after Forest. Golden Gauntlets imply the Bracelet, which validation accepts only with free time travel (on).

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

## Questions

1. **Trials counts 3, 4 and 5: each needs its own New Game and the 25-40 minute route to adult before 10-15
   minutes of castle checks, and each adds only a different starting value over P1 and P2. Play them (P3-P5,
   about 2-3 hours), skip them, or accept one documented save edit of P1's adult save (setting the count and
   pre-removed trials to each count's new-game values, the same edit in both arms)?** Proposed by cs21g: skip
   unless P2 fails; the save edit forges exactly what the tested writer sets, so it adds little.
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
`ingame/CHECKLIST.md`, 25 launchers in `ingame/`. Seeds were built at `CLAWSHOT_WORKERS=1` with no game running,
one at a time; no gate, sweep or full suite (no product behaviour changed).

## Played

Nothing in this track was played in game. Boot checks of the seven mods are Claude's.
