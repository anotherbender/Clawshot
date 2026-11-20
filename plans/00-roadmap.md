# Roadmap

Priority (Kareem, 2026-11-07): a stable solo randomizer first. Archipelago waits until seeds are solid.

## Milestones

| | What | Done when |
|---|---|---|
| **M0** | formats and the day-1 risk check | every placement file round-trips; a swapped chest gives its new item in game |
| **M1** | check census | every check in the game has a stable ID and its vanilla item; differences from OoT Randomizer's list are written down |
| **M2** | first playable seeds | chest shuffle with logic, spoiler log, settings string; Kareem and his co-owner finish a seed |
| **M3** | the rest of the shuffle | NPC and song gifts, shops, scrubs, Skulltula tokens, item-get text, Gossip Stone hints |
| **M4** | code features | a hook API in Hookshot upstream; progressive items, arbitrary item models, entrance shuffle |
| Later | Archipelago world and client; settings GUI; race seeds | |

Day-1 numbers from the spike (raw placements, not deduplicated): 267 chests in 72 files; 41 without a drop
parameter; major items found in chests include the Hookshot, Longshot, Megaton Hammer, Bow, Slingshot, Boomerang,
Iron and Hover Boots, Lens of Truth, Kokiri Sword, Mirror Shield, Ice Arrows and both gauntlets.

## Round index

Read **the roadmap index plus your round's file** before starting a track: this index holds milestones and
standing backlogs; `rounds/r<N>-overview.md` holds the round brief and outcome, and
`rounds/r<N>-<track>.md` holds your track's evidence and handoff.
Historical briefs are preserved verbatim, including old paths, commands and unplayed claims; they are not
current instructions. Their bare document names retain the original `plans/` context.
The standing Settings backlog below was separated from round 8, not discarded.

| Round | Dates | What merged / recorded status | Round file |
|---|---|---|---|
| 1 | 2026-11-07 | Formats and chest swap, game-data research; runtime mod-loader track pending at recorded outcome. | [Round 1](rounds/r1-overview.md) |
| 2 | 2026-11-07 | Census, save reader and first world engine. | [Round 2](rounds/r2-overview.md) |
| 3 | 2026-11-07 | Census, resource-size table, world port and seed writer; mini-seed exposed remake logic mismatch. | [Round 3](rounds/r3-overview.md) |
| 4 | 2026-11-07–08 | Child/adult remake logic, fast start, EVFL and gift census. | [Round 4](rounds/r4-overview.md) |
| 5 | 2026-11-08 | Age model, shops, whole-game chests, gifts and playtest routes. | [Round 5](rounds/r5-overview.md) |
| 6 | 2026-11-08 | Names, settings strings, text/hints, scrubs, nested size repair and played logic corrections. | [Round 6](rounds/r6-overview.md) |
| 7 | 2026-11-08–09 | Gossip hints, get models, boss hearts, gift gates and bomb-strength logic. | [Round 7](rounds/r7-overview.md) |
| 8 | 2026-11-09 | Fill robustness, get models, shops, gift experiments and freestanding native pickups. | [Round 8](rounds/r8-overview.md) |
| 9 | 2026-11-09 | Age-item warnings, Sheik/free travel, seed packs and map floors. | [Round 9](rounds/r9-overview.md) |
| 10 | 2026-11-09–10 | More gifts, Door/time-travel settings, NUP input and pots research. | [Round 10](rounds/r10-overview.md) |
| 11 | 2026-11-10 | Public docs, mod loading, keysanity research, UI base and tested gift release; no consolidated outcome in old roadmap. | [Round 11](rounds/r11-overview.md) |
| 12 | 2026-11-11 | Public polish, named small keys and physical dungeon attribution; indexed from track records, no old round section. | [Round 12](rounds/r12-overview.md) |
| 13 | 2026-11-12 | Fast-start/guide fixes, item grants, dungeon-item repairs and vanilla Gerudo-card policy; indexed from track records. | [Round 13](rounds/r13-overview.md) |
| 14 | 2026-11-13–14 | Longshot, tracker, story/quest-step fixes and progressive items; released 0.2.1. | [Round 14](rounds/r14-overview.md) |
| 15 | 2026-11-14–15 | Contributor PRs, compact tracker/free-travel UI, scrub guard and token shuffle. | [Round 15](rounds/r15-overview.md) |
| 16 | 2026-11-16–17 | Softlock entry guard, clock chain, NUP cap, minimap and Water precaution; released 0.2.2. | [Round 16](rounds/r16-overview.md) |
| 17 | 2026-11-17–18 | Warp guards, unproven sword guard, options copy, tracker counts, experimental dungeon mode, three chests and Token holds; main `2ba2f9a`. | [Round 17](rounds/r17-overview.md) |
| 18 | 2026-11-18–19 | Repairs, more checks, key/reward options and bounded played acceptance; released 0.2.3. | [Round 18](rounds/r18-overview.md) |
| 19 | 2026-11-19–20 | Scene handoffs (no-ocarina lessons, Saria farewell), Light Arrows logic, 100-token reward, Master Sword shuffle, startup-test fix; cows research, fill rejected; 0.2.4 candidate. | [Round 19](rounds/r19-overview.md) |


## Settings backlog (Ship of Harkinian's lists, shown by Kareem 2026-11-09)

Reference for later rounds and presets; feasibility marked [inference] is unverified. RomFS-only (D14) rules out
anything needing engine code.
- **Have:** songs anywhere; forest closed/`closed_deku`/open; dungeon items in their own dungeon or anywhere; Gossip
  Stone hints without the mask (`always`) or with it, `balanced` distribution; scrubs; shops and prices; boss hearts.
- **Likely through saved flags or flows** [inference, each needs research and an in-game test]: Door of Time open
  (the `DoorOfTime` flow counts the stones); Zora's Fountain open (King Zora moved); Jabu-Jabu open; Gerudo Fortress
  fast carpenters; skip Ganon's trials; skip child stealth, the Epona race, planting beans; start with maps and
  compasses; full wallets; Big Poe count; Rainbow Bridge conditions (the bridge's check); separate small key, boss key
  and Fortress key settings (logic and fill only).
- **Text, through `patch/text`:** static hints at Dampé's diary, the Skulltula House, merchants, Malon, the frogs,
  Saria, warp-song destinations; the Temple of Time altar and Ganondorf need their text traced first (round 6 note).
- **Research first:** random or adult starting age; shuffled dungeon rewards (round 7 researched how they are given);
  dungeon and boss entrance shuffle (whether Banc exits name their destination).
- **Needs engine code, out of reach:** ice traps, keyrings, boss and Ganon souls, Triforce Hunt, Ganon's boss key
  given by a reward count, Blue Fire and Sunlight Arrows, Bunny Hood speed, masks as adult.

