# Round 22 overview

Brief written 2026-11-24 by Claude; lineup agreed with Kareem the same afternoon, from his first 0.2.6 seed (about
three hours on Longshot 3.2.0), round 21's carry-forward and the 0.2.7 hotfix. Base: `main` = 0.2.7 (`b1081f4`) plus
this record. Thread `cs-r22`; worktrees `E:/OOTRemake/clawshot-r22/<track>`; gate lock
`E:/OOTRemake/work/rounds/r22/gate.lock`. Longshot 3.2.0 (`builds/stable/v3.2.0`) replaced 3.0.0; every staged check
names it.

## Lineup

| Agent | Track | Scope | Ready kind |
|---|---|---|---|
| cs22a | dampe | Dampé offers the first race, and its chest, until that chest is opened, also with a Hookshot or Longshot owned (today the flow runs only the second race then). A save that already ran the second race gets the first race back. After Kareem plays it, a separate commit lifts 0.2.7's non-progression limit on the chest. | play-held |
| cs22b | tracker | Bombchus need the Bomb Bag in the remake (Kareem, 3.2.0): generator and tracker logic stop counting Bombchus without it, and D30 is corrected. A "needs a purchase" marker on checks in logic only through a shop item. Silver rupees mapped so trial endings can show in logic. Sweep. | merge |
| cs22c | shops | Why a potion-shop shelf won't sell a non-bottle item (a Deku Shield at the Kakariko Potion Shop: no message, no sale) and the fix. Then the two tunic gifts (GC Rolling Goron as Adult, ZD King Zora Thawed) shuffle like the other gifts; they wait on the shop fix, so a needed tunic is never on a shelf that can't sell it. | play-held |
| cs22d | logic | Adult Dodongo's Cavern with the Bracelet and Bomb Flowers (Kareem finished it that way before the bag): rule-by-rule evidence, loosening only with a cited trigger chain or a played check; round 21's Hammer-on-flower candidates. Zora's River downstream reads the same wall as upstream (a tightening). Stage the compass-from-Sheik check. Sweep. | play-held |
| cs22e | scenes | The moat window names the shuffled item, not the Ocarina of Time; Talon's Cucco table stops showing milk and a bottle when its prize is shuffled; Saria's doubled ocarina before Gohma (round 21's proposed fix). | play-held |
| cs22f | games | The Lost Woods Skull Kid ocarina game gives its prize on the first win, like the other minigames. An opt-in setting so bombs work without the Goron's Bracelet. The starter's uv hash check works from a PowerShell 7 window. | play-held |
| cs21i | pr41 | Carried from round 21: BBender's PR #41 at `e0156b7` (option 2 by setting, `patch.steps`, a `PatchError` for uncovered placements). Review, merge `main` in, say which packet rows need replay, gate. Targets 0.2.8. | play-held |

Not this round: rebuilding a seed from an older release with the same placements (Kareem: too big for this round);
BBender's floor-songs PR, which follows #41.

## File ownership

- dampe: Dampé's flow patch (`patch/dampe*.py`), the first-race chest's world and location lines, `tests/test_dampe_*`.
- tracker: `tracker/logic.py`, `tracker_logic.toml`, the Bombchus fields in `tracker/state.py`, the marker in
  `ui/static/tracker.*`, `docs/tracker.md`; the Bombchus helpers in `data/world/helpers.toml` and the
  `free_bombchu_drops` setting; decision D30 in `plans/decisions.md`.
- shops: the shop and potion-shop flow patches, the two tunic rows in `gifts.toml` and `gift_rules.toml`.
- logic: Dodongo's Cavern rules (`dodongos_cavern.toml` and its remake overrides), the Zora's River downstream exit,
  the Ice Cavern dungeon-item hold lines.
- scenes: the new `display` field in `gift_rules.toml`, the display rewrite in `gifts.patch_flowchart`, Talon's flow,
  the `Dm_Kokiri_0155` edit.
- games: the Skull Kid flow, the bombs-without-Bracelet setting and its patch, `scripts/start-windows.ps1`.
- pr41: the files PR #41 touches (`patch/getitem.py`, the song get flows, `patch.steps` in the spoiler).
- Shared-additive: `patch/gifts.py` (shops adds the tunics, scenes the display), the `Settings` dataclass in
  `generate/fill.py`, `app/settings.toml`, `data/settings.toml`, `docs/settings.md`, `docs/logic.md`, `README.md`, the
  world TOMLs. Add or change only your own lines; the later-merging track keeps both sides.

## Load rules

The round 20 caps stand:

- Full gates and sweeps only under the gate lock, one at a time, in `work/rounds/r22/gate-order.txt`'s order:
  synthetic `-n 8` with `CLAWSHOT_WORKERS=4`, dump `-n 8` with `CLAWSHOT_WORKERS=3`, sweeps `CLAWSHOT_WORKERS=6`.
- Focused tests outside the lock: at most `-n 2` and `CLAWSHOT_WORKERS=1`, one run per track at a time.
- Only a track's main agent runs pytest, sweeps or seed generation; subagents read and trace.
- With `longshot.exe` or `hookshot.exe` running (exact image name), everything drops to `-n 2`,
  `CLAWSHOT_WORKERS=1`, and no sweep starts.

## Outcome

(Written at round close.)
