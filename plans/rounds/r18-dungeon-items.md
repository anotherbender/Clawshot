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
Focused fill regressions: **26 passed**.

### READY (merge): frozen verification head

`ab6b66daea4956ef0443fb43fe4015f635906126`, rebased onto the round's main.
The locked production-prepared sweep forced `all_anywhere` for every recipe:

| Recipe | Seeds | Exhausted |
| --- | ---: | ---: |
| Kareem's broad settings | 500 | 0 |
| Defaults | 50 | 0 |
| Recommended | 50 | 0 |

Broad seeds include **2306988613 and 12345**. Native destination preparation
remains enabled; every successful generation retains ordinary beatability.
Normal bounded retries are unchanged: first-attempt failures were 148/3/5 by
recipe, but none exhausted the existing ten-attempt limit.

One exact-head gate, with no running game: Ruff format and lint **pass**;
synthetic **3322 passed, 378 skipped**; full dump oracle **375 passed**.
The 36 pytest iterator-parametrization warnings are recorded in the logs.
The shared `gate.lock` was held throughout the sweep/gates and released.

External evidence: `sweep-meta.json` (full recipes), `sweep.jsonl` (every seed,
attempt and result), `sweep-summary.json`, `gate-run.log`, `gate-results.json`,
and `gate-{format,lint,synthetic,dump}.log`. No generated game files enter Git.
The subsequent evidence-only round update changes no gated implementation.

## 2. Off-area pause map grant — play-held

Played facts (Kareem, 2026-11-18): remote Forest map/compass ownership Bools save,
but the pause map remains unavailable after normal entry and with the era control.
The remote Forest boss key opened the boss door with the normal open action.
Debug Teleport skips first-entry title cards; debug age leaves Sequence_IsChildhood
true. The previous visit/era controls did not restore the map.

### Read-only save comparison

Executed `di_mapflags.py` against all 102 slots in the 17 assigned natural
chest-hunt snapshots and all six slots of the assigned played test user.
`di-mapflags.json` / `.log` stay outside the repository. A follow-on native/event
string corpus resolves map-related field names and the UI reader's literal
hashes (`map-flag-corpus.json`, `map-flag-corpus-hashes.log`).

Played slot01 and the natural Forest-map saves agree on all three Forest ownership
Bools (true), remaining small keys (0), and the eighth DungeonInfo member (UInt31).
The actual unknown member hash is `0x05b159d1`, not the typo `0x05b15ad1` in the
old research note. Its full saved key is `0x4321ac04`. The differing small-key
total/first-key fields are 5/true naturally versus 0/false in the test, not map
ownership. BossRetryNum is unsaved and absent in both.

Generic `IsGet.Item_Dungeon_Map/Compass/BossKey` are **false in both** sets;
adding those is not a demonstrated repair. The natural Forest map chest is open
and its source history is true, while the test's source chest remains closed.
Those correlated differences are not proof of a map-chest-open predicate.
Natural `Step_SageOfForest=Complete`; test is Step05. The edited test is adult
and visited Forest Temple, matching the user report.

### Native reader explains the exact observed message

**No missing map-grant field has been found. Adding story history to a map grant
would be a symptom workaround and is not implemented.**

Read-only native disassembly of the supported dump establishes:

1. Map action `0x28cb1c0` calls `0x3282fe0`: sets the live dungeon's IsGetMap,
   then records acquisition in the item log. Compass is the equivalent
   `0x28caff0` → `0x3283060`. The map-source wrappers add no hidden grant writes.
   Forest's EventSetting has the native typo `ForesetTemple_GetMap`; every map
   wrapper was surveyed, not only correctly spelled names.
2. Visible-map gate `0xb27d70` independently checks **actual player IsChild**.
   If adult, it requires `HavePlayedEvent.Dm_TimeTemple_0065`
   (struct `0x2b05cbb9`, member `0xc367dcdc`). Missing/false returns false at
   `0xb27f9c`, irrespective of the owned map Bool.
3. That history is **true in the natural adult save, false in played slot01**.
   Merely changing Sequence_IsChildhood cannot satisfy it.
4. The failed gate takes `0x33e2e88`, chooses `MapMessage_01`, then passes it to
   `0x33e4880`. The player's native USen `LayoutMsg/MapMenu_00.msbt` resolves
   that exact label to **“Unavailable right now.”**
5. IsChild provenance is not inferred from the edited save: `0x32a53f8` calls
   player query `0x4b6db0`, stores through stack+0x226 and `0x32a8064` into the
   UI cache+0x5c0. That query uses the PlayerGameParam property returned by
   `0x410510`; reflection at `0xe20170..0xe201a0` binds this same property to
   **IsChild**. Player_Child's own parameter sets it true. It is not the
   saved Sequence_IsChildhood Bool.

Artifacts: `dis-map-global-gate.txt`, `dis-map-reader-chain.txt`,
`dis-map-reader-tails.txt`, `dis-map-disabled-animation.txt`,
`dis-map-animation-names.txt`, `dis-cached-age-query.txt`,
`dis-is-child-binding.txt`, `cache-child-byte-stores.txt`,
`dis-scene-cache-prefix.txt`, `map-message-labels.txt`, and
`map-wrappers-all.json`, all under the external research root.

**Conclusion:** the supplied debug-adult checkpoint fails a native UI readiness
gate independently of the remote grant. Its unavailable message does not prove
a missing grant write. This is static cause evidence, not an invented in-game
retest or a claim that every remote map combination has been played.

### Child packet and acceptance boundary

Main-built packet: `ingame/mods/r18-deku-map-main-control/r18-deku-map-main-control`.
Seed180214 pins Deku map/compass to Mido top-left/top-right chests; forest/Mido
open, ordinary child walk into the tree, no age/teleport/inventory changes.
Full ordinary beatability and emitted binding/placement readback passed:
104 resources, 22 spheres; digest
`907f60b677e93dd7dcf7fdf7f3ca69c20e264669bb3537325ad681c4a0faf060`.
Proof records the actual imported main source path, not this worktree.

Launcher `ingame/control-main-deku-map.bat`; checklist `ingame/CHECK-DEKU-MAP.md`.
Actual cmd dry-run passed and selected Longshot rc.7. The installation now nests
`builds/rc/v3.0.0-rc.7/bin/longshot.exe`, so the copied template needed a second
channel/version discovery loop; no runtime file was edited. A first unmodified
discovery failed and printed the missing-path cause before that correction.
The launcher uses exactly one mod, clears HOS_FS_OVERLAY, and creates only its
own empty user/save folder. No game was started.

Allow 5–8 minutes including new-game menus, pickups, walking entry, pause-map and
Save–Continue. Claude boot-checks first. The refreshed shared-template launcher
dry-run selects rc.7. The checklist now predicts availability for a normal child:
this is a discriminating control, not a claim to reproduce the debug-adult bug.
Any continued unavailability must retain this clean saved-state/loading proof.

**Acceptance proposal (cs18c, posted to thread): run this no-debug child control
before authorizing any additional map-grant state. If it passes, retain the
current grant; do not fake Dm_TimeTemple_0065 or a native map chest's open flag.
If it fails, retain the played saved-state/loading proof and investigate that
clean reproduction.** No separate “fixed” packet or READY (play-held) grant head
is fabricated: no grant-code change is supported by the current evidence.
