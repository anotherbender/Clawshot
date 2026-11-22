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

Closed 2026-11-22 by Claude. Every play-held track merged after Kareem's checks on Longshot 3.0.0; 0.2.5 shipped
from `b3cd3b8` on 2026-11-21.

| Agent | Track | Outcome | Played (Kareem, Longshot 3.0.0) | Record |
|---|---|---|---|---|
| cs20a | hints | Merged `2c907ef` | All ten stages: scrub offers (four), Great Fairies, altar v3, Skulltula House, Ganondorf subtitle | [hints](r20-hints.md) |
| cs20b | exclude | Merged `ade62dc` | Generator only; sweep 200/200, 0 exhausted | [exclude](r20-exclude.md) |
| cs20c | start | Merged `5ed31bc` | Broad start A/B; A-v2 pause maps after the starting-Kokiri-Sword Saria-state fix | [start](r20-start.md) |
| cs20d | trials | Merged `840e198` | 16-token bridge; zero trials (barrier, lift) on an adjusted save copy; partial 1-5 not played | [trials](r20-trials.md) |
| cs20e | open | Research only `176c2f4` | None (Kareem: not yet) | [open](r20-open.md) |
| cs20f | cows | Records `be0e288`, `7e8ca33` | Cow persistence; Fortress four rescues, card once, Training Ground | [cows](r20-cows.md) |
| cs20g | fill | Candidate rejected; research `f8fb504` | None | [fill](r20-fill.md) |
| cs20h | audit | Merged `df6214b`, `8ff9bf6` | Dodongo's Cavern Scarecrow Skulltula with the Hookshot | [audit](r20-audit.md) |

Contributor PRs merged in the release: #37 (tracker vanilla rows, with maintainer fixes) and #38 (a child's Hylian
Shield beats Deku Scrubs, which Kareem confirmed in game).

**Integration and release gate** on `b3cd3b8` (main plus #37, #38, docs and the version bump): format, lint,
synthetic 4239 passed, dump 827 passed; sweep on main plus #38: 300/300, 0 exhausted (attempts 210/52/52).

**Lessons recorded (skills and checklists):** no Longshot Debug age change in any checklist (it never writes the
era flag; the zero-trials lift fault was traced to the barrier-clear history instead); walk into dungeons for
map checks; a starting item can bypass a story scene's state writes (a starting Kokiri Sword skips Saria's wake
scene); stack two play-held tracks before the second gate; stop a gate on a head that must still rebase.

**Carried to round 21:** partial trials 1-5 unplayed; the Light Arrows scene after Shadow and Spirit is static
evidence only; Very strong hints unplayed; first-try generation failures (4.5% broad); Kakariko rooftops without
the owl (Kareem asking); the tracker reading Darunia's gift from a real save; and Kareem's first 0.2.5 seed: the
Goron City stick pot, the Megaton Hammer, Richard's quest and the tracker layout.
