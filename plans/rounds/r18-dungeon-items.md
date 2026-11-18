# Round 18, Track C: dungeon items (cs18c)

Branch `r18/dungeon-items`; initial base `2ba2f9a`. Model: openai-codex/gpt-6.1-sol.
Research and generated packets: `E:/OOTRemake/work/r18-dungeon-items/` only.
No game started, personal seed opened, original save modified, or runtime folder written.

## 1. Urgent all_anywhere generation failure

Kareem's failures on seeds 2306988613 and 12345 are the reproduction. The diagnostic
`fill_probe.py` captured the exact production-prepared native inputs, then printed
one instrumented fill attempt for 2306988613; `fill-probe.log` retains the values.

**Cause proven: late ordinary filler consumes the map/compass chest destinations,
not a total shortage of safe destinations or a need to widen the grant families.**
Before the final filler stage: 20 empty chests, 20 unplaced maps/compasses, plus
23 NPC, 8 Song, 5 Cutscene and 2 Scrub destinations. Shop mode combined
`priority + rest` into a stack popped from its end. Ordinary rupees/seeds therefore
went before the priority maps/compasses. At failure 14 map/compass copies had zero
allowed remaining destinations; Arrows (10) still had 15 allowed destinations, but
the filler stopped on the blocked map/compass. Its unplaced-arrow message is a
consequence, not a separate missing arrow destination.

Change: put ordinary filler before priority in that stack, retaining the existing
native-shop-display ordering. No destination admission changes, no fallback grant,
no extra attempts, no gameplay patch. Boss keys remain chest-bound outside home;
the played normal boss-door acceptance remains unchanged. This changes placements
for Shop recipes; no version bump on this branch (maintainer-owned).

Regression: a synthetic two-chest/two-gift/shop world must place its map/compass
in the only safe chests and coins on gifts, in one attempt across 20 seeds.
Focused checks, rebased head, full gate and 500+ seed sweep results: pending.

## 2. Off-area pause map grant — play-held

Played facts (Kareem, 2026-11-18): remote Forest map/compass ownership Bools save,
but the pause map remains unavailable after normal entry and with the era control.
The remote Forest boss key opened the boss door with the normal open action.
Debug Teleport skips first-entry title cards; debug age leaves Sequence_IsChildhood
true. Neither fact explains the remaining map failure after the controls.

Read-only save comparison and native writer/availability tracing in progress.
The subsequent check must put Deku map + compass in Kokiri Forest chests and walk
into the tree as child, without debug age or teleport. It ships with a main-built
control launcher and remains built, not played, until Kareem runs it.
