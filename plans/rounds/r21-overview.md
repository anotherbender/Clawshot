# Round 21 overview

Brief written 2026-11-22 by Claude; lineup agreed with Kareem the same evening ("go ahead and start"), from his
first 0.2.5 seed, round 20's carry-forward and BBender's two new PRs. Base: `main` = 0.2.5 (`b3cd3b8`) plus the
round 20 close records. Thread `cs-r21`; worktrees `E:/OOTRemake/clawshot-r21/<track>`; gate lock
`E:/OOTRemake/work/rounds/r21/gate.lock`.

## Lineup

| Agent | Track | Scope | Ready kind |
|---|---|---|---|
| cs21a | tracker | The tracker's layout from Kareem's notes: a Checks tab with check details in the side panel, fewer columns, collapsible areas and "hide completed", click-to-toggle done/skip instead of prefixes and Mark done buttons, a no-save state, the age selector beside the checks; a leaner OBS overlay (no tiles, only the dungeon items a dungeon has, shorter or hideable names). Builds on PR #39's state fields once merged. | merge |
| cs21b | pr39 | Review and fix BBender's PR #39 (the tracker reads gifts from the game's once-flags), our commits on top of his; maintainer decisions to Claude. | merge |
| cs21c | pr40 | Review and fix BBender's PR #40 (chest ocarinas show their get model, every seed); stage Kareem's check on Longshot 3.0.0 and our dump. | play-held |
| cs21d | sticks | Remove the pot-only Deku Stick sources (Goron City, Zora's Domain, Bottom of the Well) from logic, after checking each in the remake data; sweep. | merge |
| cs21e | hammer | The Megaton Hammer in the remake does what bombs do (Kareem, in game) and works as an adult weapon: widen the rules with per-rule evidence, keep King Dodongo's exception, stage checks for what his play didn't cover; sweep. | play-held |
| cs21f | npcs | Richard the Lost Dog's real trigger in the remake (the lady at the Market entrance; at night both are home); Cojiro needs Epona freed (Anju's line): fix only if anything beyond the vanilla trade chain reads it. | merge or play-held |
| cs21g | checks | Stage the pending play checks (partial trials 1-5, the Light Arrows scene after Shadow and Spirit, Very strong hints, the tracker reading Darunia's gift) and fix the round 20 doc gaps. No product code. | research |
| cs21h | fill | Second attempt at first-try generation failures (4.5% broad: late map/compass filler and token placement), from round 20's research handoff; re-measure after the sticks change. | merge |

## File ownership

- tracker: `ui/static/tracker.{js,css,html}`, the app's Tracker tab markup and the new Checks tab, `docs/tracker.md`
  layout text, UI tests. Backend fields (`tracker/state.py`, `tracker/marks.py`) belong to pr39 until #39 merges;
  post the field you need on the thread.
- pr39: the files PR #39 touches (`gift_rules.toml` `track`, `tracker/state.py`, `tracker/marks.py`, the audit CLI).
- pr40: the files PR #40 touches (`patch/getitem.py`, the ocarina packs, the rstb rule, `pack/source.py`).
- sticks: the `Deku Stick Drop` events in `data/world/*.toml` and their remake overrides.
- hammer: the explosive and adult-combat rules it widens, any helper it adds in `data/world/helpers.toml`.
- npcs: the Richard and Cojiro rules and their location notes.
- checks: `work/` staging and the round 20 doc lines it fixes.
- fill: the fill algorithm in `generate/fill.py`; the `Settings` dataclass is shared-additive.
- Shared files (`app/settings.toml`, `data/settings.toml`, `docs/settings.md`, `docs/logic.md`, `README.md`, the
  world TOMLs): add or change only your own lines; the later-merging track keeps both sides on rebase.

## Load rules

Kareem isn't playing tonight, but the round 20 caps stand (they keep Claude's watchers alive):

- Full gates and sweeps only under the gate lock, one at a time: synthetic `-n 8` with `CLAWSHOT_WORKERS=4`,
  dump `-n 8` with `CLAWSHOT_WORKERS=3`, sweeps `CLAWSHOT_WORKERS=6`.
- Focused tests outside the lock: at most `-n 2` and `CLAWSHOT_WORKERS=1`, one run per track at a time.
- Only a track's main agent runs pytest, sweeps or seed generation; subagents read and trace.
- With `longshot.exe` or `hookshot.exe` running (exact image name), everything drops to `-n 2`,
  `CLAWSHOT_WORKERS=1`, and no sweep starts.

## Outcome

Closed 2026-11-24 by Claude. Released **0.2.6** (2026-11-24, tag `v0.2.6` = `1330185`) and the **0.2.7** hotfix the
same day (`v0.2.7` = `b1081f4`). Checks were played on Longshot 3.0.0 until the launcher replaced it with 3.2.0
(2026-11-24); Clawshot's mods boot on 3.2.0 (main and PR #41's candidate).

| Track | Outcome | Played | Record |
|---|---|---|---|
| cs21a tracker | Merged `ff78b5e`: Checks tab, row toggles and skips, leaner OBS overlay, Longshot 3.1 `save-work` fix. | Kareem's 0.2.6 seed (3.2.0) | [r21-tracker](r21-tracker.md) |
| cs21b pr39 | PR #39 merged `47505ff`; ten gift rows accepted from play (`aeba6df`). | Kareem, 3.0.0, seed 921101 | [r21-pr39](r21-pr39.md) |
| cs21c pr40 | PR #40 merged `99743ca`; follow-up `7f4070a`: Saria's doubled ocarina is the remake's own, before Gohma only (fix proposed for round 22). | Kareem, 3.0.0 (arms 10/11) | [r21-pr40](r21-pr40.md) |
| cs21d sticks | Merged `3667df5`: pot-only Deku Stick and Nut sources out of logic; child Gold Skulltulas need a kill. | no (tightening) | [r21-sticks](r21-sticks.md) |
| cs21e hammer | Merged `5078acb`: the Megaton Hammer counts as explosives and an adult weapon where the remake allows; King Dodongo kept. | Kareem, 3.0.0 | [r21-hammer](r21-hammer.md) |
| cs21f npcs | Merged `b1d510d`: Richard needs the Kakariko gate open; Cojiro needs Epona freed. | no (tightening) | [r21-npcs](r21-npcs.md) |
| cs21g checks | Merged `f7ba65f`, `e8dc77d`, `566c159`: round 20's staged checks, Darunia's tracker read, trials counts 1 and 2 played. | Kareem, 3.0.0 | [r21-checks](r21-checks.md) |
| cs21h fill | Merged `1b27482` (the chest reserve keeps first-try fills from running dry) and `aded22d` (keys, maps and compasses stay in chests; Ice Cavern tightened). | no | [r21-fill](r21-fill.md) |
| cs21i pr41 | Carried into round 22: BBender switched to option 2 (by setting) on 2026-11-24; targets 0.2.8. | Kareem, 3.0.0 (first head) | round 22 |
| cs21j placement-audit | Merged `efdea7c`: every placement limit with its evidence class. | no (doc) | [r21-placement-audit](r21-placement-audit.md) |

**Release gates.** 0.2.6 on `1330185`: 300-seed sweep 0 exhausted; synthetic 4391 passed; dump 836 passed. 0.2.7 on
`b1081f4`: Dampé sweep 0 of 400 unfinishable (93 before); 300-seed sweep 0 exhausted; synthetic 4398 passed; dump on
`1329d78` (identical `src/`) plus the two re-pinned test files.

**Lessons recorded.**
- A location whose native flow branches on owning its own vanilla item can be unreachable once that item is placed
  elsewhere. Dampé's flow runs only the second race when a Hookshot or Longshot is owned, so the first-race chest never
  appears; since 0.2.3 about one seed in four could put a required item there (0.2.7 limits it to non-progression;
  round 22 fixes the flow). Trace such branches before a location takes progression.
- A logic or fill change that moves placements can drop a pinned test seed's coverage
  (`tests/test_event_registration.py`'s scrub-shield seed): re-pin with a placement search, confirmed in the dump tier.
- The first-start check must run with Windows PowerShell's own module path: an inherited PowerShell 7 path hides
  `Get-FileHash` and the starter reports a wrong hash (round 22 makes the starter independent of it).
