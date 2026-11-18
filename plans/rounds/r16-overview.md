## Round 16 (softlocks without a save warp; time of day with the Door of Time open; `.nup` cap)

Kareem handed over the PC overnight on 2026-11-16, after playing a self-generated seed from main on Longshot rc.4.
Bermuda thread `cs-r16`; tracks on `openai-codex/gpt-6.1-sol`; Claude reviews, merges and bumps the version. Full
suites serialize under `work/rounds/r16/gate.lock`. `CLAWSHOT_WORKERS=4` while the game is closed (Kareem's offer
for overnight runs), 1 while `longshot.exe` or `hookshot.exe` runs. Nobody opens his seed's spoiler.

Facts from his run (2026-11-16):
- The remake has no save warp. It autosaves on every room change, and Load offers the autosave and the manual
  saves. A room the player can enter but not leave is a real softlock: he loaded an older save.
- In the Deku Tree Slingshot Room (2F, the Deku Scrub room), he had no Slingshot, Boomerang or Bow, and was locked
  in. Our override already gates the way out (`child_deku_tree.toml`, eye switch `Obj_EyeSwitch_A_02`), but not the
  way in. So the fill counted both chests as reachable with only a shield, and put the dungeon's map and compass
  there.
- OoT Randomizer's logic assumes a save warp exists. Any one-way move it allows may trap a remake player.

### Track A: softlocks (`r16/softlocks`)

1. Fix the Slingshot Room. The way in requires the way out; the vanilla Slingshot-in-its-own-chest case is a
   self-lock the fill must not produce. Add a failing test first.
2. Audit the whole world for the same trap. Build a checker that, for many seeds and presets (Defaults,
   Recommended, keys anywhere, Gift, Shop, Token, open Door and open Forest), walks the playthrough sphere by
   sphere. At each step it lists every reachable region from which the start can't be reached again with the items
   held. Warp songs and Farore's Wind count only when held, and only where the remake allows them (inside
   dungeons and buildings?). Report each finding with evidence from data and the guide: a real trap gets an entry
   rule like item 1; a missing return edge in our world gets a new exit with evidence. The checker becomes a test
   that holds for the sweep.
3. Settings and generation must refuse rather than produce a seed with a reachable trap.

### Track B: time of day stuck with the Door of Time open (#32)

A tester on 0.2.1 and 0.2.0 (Linux, Longshot rc.3; log attached to the issue) reports that after pulling the
Master Sword with the Door of Time open, it stayed night across the whole world. Sun's Song set it back to night.
On a 0.2.0 seed, the day was stuck instead. Kareem's current seed has the Door open.
- Find the cause in data: what the day cycle reads, and what the open-Door patch writes or skips.
- Fix it. Prove the fix offline: if it's a patch-only change, placements stay identical for the same seed and
  settings.
- Stage a short in-game check on Longshot.

### Track C: `.nup` reader size cap (#31)

Cap each file's declared size and hash it block by block, as the `.nx` reader does since `4617fb5`. Add tests,
including a crafted oversized entry that is refused before allocation.

### Outcome (released as 0.2.2, 2026-11-17)

- Track A merged: Slingshot Room entry guard, softlock checker and scoped refusal (`33e8895`..`f93cd4b`).
- Track C merged as `af6a7b4`; #31 closed.
- Track B grew into the clock chain and merged as `ef0d932`; #32 closed. The Field clock needs the owl's
  `HyruleField_ArriveEntrance`, Impa's send-off `Dm_HrlField_0020`, no first-adult hold
  `HrlField_HasEnteredFirstTime_Adult`, and `HyruleField_ChangeENV` false (the first-visit palette pins the sun).
  Open and song-only Doors wait for the send-off. The send-off restores the owl flags and clears ENV; the
  forest exit no longer sets ENV once the owl or send-off has played; returning to child clears the hold; the
  stone counter recounts after the send-off in every mode; the escape and moat play after an early pull. Played
  on Longshot rc.7 (v4/v5 checks).
- Follow-ups merged as `ed9f257`: the Kaepora skip marks Hyrule Field visited (map and minimap), and a Water Temple
  precaution requires the Ice Cavern end-chest source (unmodded debug check: the switch doesn't latch pre-quest;
  exact predicate unproven).
- Gates now run with `uv run --with pytest-xdist pytest -n 12`: synthetic about 4 min, dump about 25 min.
- Plans for round 17 on branches: `r17/skip-zelda` (`763cfcf`) and `r17/child-sword` (`7308a83`).
- No community seeds for 0.2.2 (Kareem: players generate their own).
