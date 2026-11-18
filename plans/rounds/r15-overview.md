## Round 15 (castle's pull requests; tracker overlay; free time travel in the app; scrub softlock; token shuffle)

Kareem agreed, 2026-11-14, after 0.2.1 was published: "we keep going". He plays the small-keys-anywhere community
seed 24 beside this round, so every gate uses `CLAWSHOT_WORKERS=1` while `longshot.exe` or `hookshot.exe` runs (3
otherwise), one heavy job at a time under `work/rounds/r15/gate.lock`, and the long dump gates go when he is away.
Nobody opens seed 24's spoiler or names its contents. Bermuda thread `cs-r15`, herdr-core, tracks on
`openai-codex/gpt-6.1-sol`; Claude reviews, merges and bumps the version. In-game checks run on Longshot (D41).

### Track A: castle's pull requests (`r15/castle`; #5, #4, #20, then #6)

Kareem: rebase them ourselves and keep castle's (mysterypaintwo) authorship; castle is not asked to do more. Each PR
is rebased onto main in its own stack (#5 then #6; #4 then #20). Conflicts are resolved inside castle's commits, so
he stays their author; adaptations to what main gained since 2026-11-12 (Longshot Detect and Play, the tracker,
progressive items, the quest-step fixes) are separate commits of the track's own. Each PR's own tests plus full
gates; #20 is checked read-only against Kareem's `.nx` dump; #6 changes the game and gets one in-game check. Claude
pushes the rebased stacks to the PR branches (maintainer edits are allowed) and merges, so each PR closes as merged.

### Track B: tracker overlay and free time travel in the app (`r15/ui`)

1. The OBS view is too wide and too big (Kareem, 2026-11-14). A vertical layout of a few columns, a column count
   option, and a toggle that hides names and tiers so icons sit close together. Dungeon keys, boss key, map and
   compass use the game's own icons (`Item_Dungeon_*` in `UI/Tex/Icon`) with the text fallback. The in-app tab's
   layout stays.
2. `free_time_travel` (CLI-only and experimental since 0.1.1) becomes an app setting with the same label and
   help, in the settings string as today.

### Track C: token shuffle, research and specification (`r15/tokens-spec`; clean room, step 1 of 2)

REALAZK reports (ootrr issue 6, 2026-11-14) that a generated Gold Skulltula token actor with a borrowed collection
callback works in game, and that an uncollected token makes the Skulltula come back. ootrr is GPL. Track C may read
it and our own dump and experiments (sections 11, 23 and 27, D27) and writes a facts-only specification; it writes
no Clawshot code. The implementer never opens ootrr. Credit "ootrr (REALAZK)".

### Track D: scrub softlock, then token shuffle from C's specification (`r15/scrub-tokens`)

1. #26: in the Lost Woods scrub grotto near Sacred Forest Meadow, one scrub offers nothing, and talking to it a
   second time leaves an invisible text box. Reproduce, find the cause, fix, and stage an in-game check.
2. After C's specification is accepted: Gold Skulltula tokens as a shuffle option, built only from that
   specification and our own sources (D never opens `E:/OOTRemake/work/refs/ootrr-azk` or ootrr on GitHub).

### After round 15

Done 2026-11-15; not released yet (main `f84b5ae`). All four tracks merged:
- A: castle's #5, #6, #4 and #20, merged as one linear series under his name (main `e5fe7e2`).
- B: the compact OBS tracker view and free time travel in the app.
- C: the clean-room token specification.
- D: the #26 scrub guard (`d66d35f`), then Gold Skulltula token shuffle (`3e2dd50`, final families `f84b5ae`).

Token shuffle:
- Off by default; presets are unchanged.
- All 100 Skulltulas are locations, including HF Lone Tree, HF Wetland Grotto Crate and LLR Tower.
- 40 items in 19 families can sit at a Skulltula as a real pickup, each admitted after a played packet on Longshot
  rc.3.
- Bombchus and ammo follow D25 and the container rules.
- The 100-token reward is junk-only, with Token on or off.
- Gates on `f84b5ae`: synthetic 2855, dump 203, a 1500-seed sweep with no fill failure. Token-off output is
  byte-identical to `3e2dd50`.

Seeds differ from 0.2.1 (the #26 guard and the three native Skulltula checks), so the next release needs new
community seeds.

Open:
- #32: the time of day sticks with the Door of Time open, from a tester on 0.2.1 and 0.2.0.
- #31: the `.nup` reader size cap.
- #6's in-game check of the Nothing and other-player get windows.
- Gift-held items (bottles, Double Defense, Stone of Agony, Rupees (200)) never reach Skulltulas.
- Tokens fill about 56% of Skulltula slots; this is structural.
- Longshot moved to rc.4 on 2026-11-15; seed 25 boots on it, but nothing has been played on rc.4 yet.

