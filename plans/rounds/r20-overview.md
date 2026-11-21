# Round 20 overview

Brief written 2026-11-20 22:30 by Claude; lineup agreed with Kareem the same evening (from the
OoTR/SoH feature comparison in `E:/OOTRemake/work/r20-planning/feature-compare.md`, public docs only).
Base: `main` = 0.2.4 plus PR #36 (BBender's tracker in-logic view, `plans/tracker-in-logic.md`).
Thread `cs-r20`; worktrees `E:/OOTRemake/clawshot-r20/<track>`; gate lock `E:/OOTRemake/work/rounds/r20/gate.lock`.

## Lineup

| Agent | Track | Scope | Ready kind |
|---|---|---|---|
| cs20a | hints | Static hint text: scrubs and merchants name the seed's item, Temple of Time altar, Ganondorf's Light Arrows hint, House of Skulltula rewards, Great Fairies that wait on Din's Fire. Extra hint distributions as a stretch. | play-held |
| cs20b | exclude | Exclude locations: a player-chosen list that never holds progression. Generator and settings only. | merge |
| cs20c | start | Starting inventory (items, songs, hearts, full wallet, maps/compasses) as new-game initial values. Feasibility first. | play-held |
| cs20d | trials | Ganon's trials count (0-6) and a Gold Skulltula token-count bridge. Research first. | play-held |
| cs20e | open | Open Zora's Fountain and Kakariko gate as new-game quest state. Research first; research-only is a fine outcome. | play-held |
| cs20f | cows | Cow persistence probe with a visible signal, plus a staged Gerudo Fortress four-rescue packet. Research and staging. | play-held |
| cs20g | fill | Second attempt at first-try generation failures (main baseline about 2.5% of broad seeds). | merge |
| cs20h | audit | Logic and data audit, tightening only: BBender's Kakariko windmill and cow-shed reports, then N64 ranged-collection rules; docs aligned with main. | merge |

Out of this round: the Shadow Temple floor key stays vanilla (no save before its room exists; Kareem's call on
2026-11-20). The tracker's layout (a possible Checks tab) and PR #37 wait for Kareem's look at the tracker.

## File ownership

- hints: `generate/hints.py`, `data/hints.toml`, `patch/text.py`, `patch/get_text.py`, scrub and merchant text
  in `patch/scrubs.py` / `patch/shops.py`, and the altar, Ganondorf, House of Skulltula and Great Fairy messages.
- exclude: the exclusion setting and its validation, `generate/prepare.py` for exclusion, its UI field.
- start: `patch/start_items.py`, the initial-values part of `patch/gamedata.py`, the starting-inventory settings.
  open and trials add their initial values through start's hook (post the exact entries on the thread).
- trials: Ganon's Castle trial and barrier flows, `patch/reward_bridge.py` and the bridge condition.
- open: the new open-fountain and open-gate settings and their logic.
- cows: cow actors and flows, any new saved GameDataList entries, `patch/jail_keys.py` for the Fortress packet.
- fill: `generate/fill.py` (everyone else posts on the thread before touching it).
- audit: the logic and location-data lines it tightens, with evidence; `docs/` alignment with main.
- Shared files (`app/settings.toml`, `data/settings.toml`, `docs/settings.md`, `README.md`): add only your own
  entries; the later-merging track keeps both sides on rebase.

## Load rules for this round

Round 19 pinned the PC at 99% overnight and dropped Claude's watchers. This round runs lighter:

- Full gates and sweeps only under the gate lock, one at a time: synthetic `-n 8` with `CLAWSHOT_WORKERS=4`,
  dump `-n 8` with `CLAWSHOT_WORKERS=3`, sweeps `CLAWSHOT_WORKERS=6`.
- Focused tests outside the lock: at most `-n 2` and `CLAWSHOT_WORKERS=1`, one run per track at a time.
- Only a track's main agent runs pytest, sweeps or seed generation; subagents read and trace.
- With `longshot.exe` or `hookshot.exe` running (exact image name), everything drops to `-n 2`,
  `CLAWSHOT_WORKERS=1`, and no sweep starts.

## Outcome

(Written at round close.)
