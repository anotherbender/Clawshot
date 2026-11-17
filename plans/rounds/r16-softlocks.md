# Round 16 Track A: softlocks without a save warp

Agent cs16a; branch `r16/softlocks`; base `dd3b4537204cab9f81ccf45d5d590d7fb517c04b`.

## Scope and established evidence

Kareem, 2026-11-16, Longshot rc.4 (roadmap Round 16): no save warp; room transitions autosave. Entering the Deku Tree 2F Slingshot Room without Slingshot, Boomerang or Bow trapped him. No player seed, save or spoiler was opened by this track. No game launched.

Existing native evidence: `Banc/InsideTheDekuTree/InsideTheDekuTree_Static.bcett.byml.zs`, room 2, eye switch `Obj_EyeSwitch_A_02` Hash 9080063866993537303 and falling ladder Hash 2096903280161003875, module `InsideTheDekuTree_Level_Room_C_Prefab_efa7` (`child_deku_tree.toml`; game-data section 12). Keep the shield condition and require the existing exit predicate at entry. Bow remains the pre-existing unverified alternative, not a newly loosened rule.

## Work and verification

Failing-before: `uv run pytest tests/test_softlocks.py -q` => 2 failed, 2 passed. Printed actual state: sphere 1 collected both room chests with only Deku Shield, and the incoming rule was `here(has_shield)`. After requiring the existing exit predicate at entry: `uv run pytest tests/test_softlocks.py tests/test_world_remake.py -q` => 28 passed.

The return checker inspects the initial frontier and every full search sphere, not just the spoiler's progression-filtered rows. `Search.inventory(age)` preserves the independent child prefix. Synthetic regressions cover own-room rewards, future loot, exact arrival time, waiting where time passes, adult items unavailable to child, and refusal through ordinary and external placement APIs. `uv run pytest tests/test_softlocks.py -k "not fixed_real_world" -q` => 11 passed, 27 deselected.

Actual fill smoke (synthetic, `E:/OOTRemake/work/r16-softlocks/fill_entry_smoke.py`): own-dungeon map/compass, two gated room chests, one outside slot and `goal = True`. The generator placed the sole escape tool outside, then collected both room chests in the next sphere; scoped/raw audit was empty. The already-met goal prevents mistaking a goal check for the fill's self-lock prevention.

`Root` is an abstract OoTR spawn/warp dispatcher with no physical incoming path. Return anchors are child Link's house or Kokiri Forest, adult Temple of Time, not a fabricated save-warp edge to Root. Scratch scripts/results: `E:/OOTRemake/work/r16-softlocks/`.

Full serialized gates passed on `5e63216` (original `dd3b453` base): Ruff format/check; synthetic **2886 passed, 215 skipped**; real dump **212 passed, 2889 deselected**. Dump duration: 5842.04 s. Native profile preparation also proved exact seed-0 production placement equality for Defaults (165 shuffled), Token-on (265), Recommended (297) and Gift (221).

Integration direction (Claude, current conversation): rebase this slice onto `af6a7b4`, the pack-reader-only fix, then run Ruff and the synthetic suite. No second full dump run on this branch: the final dump gate runs once on the linear stack top, after cs16b. Rebased gate logs are `E:/OOTRemake/work/r16-softlocks/gate-rebased-{format,lint,synthetic}.log`; the tested rebased head and results are posted to `cs-r16`.

## Triage and accepted first slice

Maintainer direction (Claude, current conversation): physical safe anchors, not Root; if ordinary return debt dominates, land the evidenced-trap slice with full gates and leave ordinary returns for the next slice. This slice enforces the Slingshot Room certificate. The raw whole-world checker remains diagnostic; it is **not an all-world softlock-free certificate**.

Initial diagnostic snapshot posted to `cs-r16` before broad rules: 595 raw trials (Defaults 200, an unexpanded Recommended alias 200, keys-anywhere 195), zero failures at that point, **161 raw region-age groups**. This was useful graph triage, **not valid Gift-preset coverage**: the completed run exposed the setup mismatch below. Counts are distinct region-age groups, not confirmed physical softlocks:

| Family | Raw region-age groups |
|---|---:|
| Overworld / Spirit / abstract | 53 |
| Dodongo | 13 |
| Fire | 10 |
| Forest | 13 |
| Ganon | 23 |
| Gerudo Training Ground | 11 |
| Ice | 4 |
| Shadow | 13 |
| Water | 14 |
| Well | 4 |
| Jabu | 3 |

1. **Confirmed physical trap:** Slingshot Room (Kareem's played observation, native switch/ladder identities). Zero reports after its entry guard in the snapshot.
2. **Missing-return candidates, not proved physical traps:** numerous translated one-way subregions, including Impa's cow section, mask-shop storefront, spinning pot, crater Pierre strip, Fortress roof/kitchen, Fountain underwater/cave, and dungeon corridors. An absent graph exit alone is **not** evidence of a physical trap. No reverse edges or new entry restrictions are fabricated for them in this slice.
3. **Held-escape/one-way candidates:** child Bolero/crater and Requiem/Colossus arrivals, crater ladder/Pierre drops, downstream dungeon drops and boss antechambers. Native permission/return evidence is required before classifying or guarding them. These remain next-slice findings, not silently suppressed errors.

Initial raw records: `E:/OOTRemake/work/r16-softlocks/sweep-before.jsonl` and `sweep-before-summary.json`. The 1,800-attempt run finished in 2718.5 s: 1,600 generated, 200 open-Door return-kit refusals. `Gift` is an overlay-setup alias, not a world location type; pure `generate` does not expand it. Recommended/Gift/open-Door therefore need corrected coverage rather than counting that run as nine real presets.

Real-dump proof of that cause: native `gifts.seed_setup` plus production `make_seed` generated open-Door seed 0 with 297 shuffled checks. A frozen logic-profile replay initially differed because `restrict_event_openings` was incorrectly given the already-restricted final world. Printed payload identified the missing source-bound exclusions at the Hyrule Field heart-piece chest. Rebuilding restrictions from the pre-restriction world restored **exact native placement equality**. The corrected profile contains only logic/settings/native item identities outside the repo; sweep workers read no dump.

Permanent tests separate six dump-free world modes from the three actual Gift preset paths (`test_softlocks_dump.py`), which call native Gift preparation and the production seed compiler. No fake Gift-alias coverage or expected-failure pin remains.

Dump-free replay was exercised, not assumed: `dump_free_profile_smoke.py` installed a Python audit hook before importing the generator and denied access to both native input roots. Frozen open-Door seed 0 still generated 297 shuffled checks and an empty evidenced-region failure list, with zero forbidden input reads. The corrected 600-seed run completed under the gate lock using this same JSON-only path: Recommended, Gift and open-Door, each seeds 0–199, **zero generation errors and zero Slingshot certificate failures**. Raw diagnostic region-age groups were respectively 167, 164 and 168; these remain graph debt, not confirmed player traps. Records: `sweep-corrected.jsonl` and `sweep-corrected-summary.json` in the scratch directory.

Direct native probe `uv run python E:/OOTRemake/work/r16-softlocks/slingshot_native.py` passed: room 2 contains the exact existing `Obj_EyeSwitch_A_02` 9080063866993537303 and falling ladder 2096903280161003875. Read-only dump; no generated working-set file is added.

## Native warp evidence for the next slice

Read-only native `Event/EventFlow/Dm_SY_Ocarina.bfevfl.zs`, entry `OcarinaWarp`: Event132 calls `Player_Event.EventQueryPlayerIsAbleWarp`; refusal opens SimpleInfo Type 11 and cancels. The accepting chain checks the Biggoron trade timer and Epona-race subflows, reserves the age-specific Banc arrival, then Event76 requests autosave. External decode citation: `E:/OOTRemake/work/ocarina-autoplay/out/flow_Dm_SY_Ocarina.txt:431-491`; destination arguments at 137-157.

**The opaque native permission query is not evidence that dungeons, buildings or boss rooms allow warping.** No global song-escape edge is added on the strength of a missing flow-side scene check. Existing adult ocarina/age rules remain unchanged. Child Fairy Ocarina + Minuet was played on 2026-11-08 (R6-MINUET); that does not establish every scene or adult Fairy Ocarina use.

Data settled one tempting boss-barrier false lead without gameplay: `Pack/Actor/FldObj_AirWall_OnlyDungeonBossGohma.pack.zs`, member `Phive/RigidBodyEntityParam/FldObj_AirWall_OnlyDungeonBossGohma.phive__RigidBodyEntityParam.bgyml`, uses `EnableSubLayerHitMask = HitOnlyDungeonBossGohma`; its dedicated-enemy parent uses `HitOnlyCharacter` / `HitOnlyEnemyWithDedicatedAirWall`. That actor is not evidence of a player-trapping wall. No extra live door test or permissive edge is justified by its name. The remaining probe tests the opaque warp-permission predicate, not an assumed player collision.

The pack binding was checked end to end: actor `Components.PhysicsRef` selects the child PhysicsParam; its `ControllerSetPath` selects the Gohma controller; `RigidBodyEntityNamePathAry` binds `Body_0` to the same Gohma-only RigidBodyEntityParam. This is the active referenced body, not an unused similarly named member.

Farore's Wind has a native saved-point and MP interface (`EventQueryIsExistWarpPointForFaroreWind`, `EventQueryPlayerIsEnoughMPFaroreWindWarp`, `EventSetFaroreWindPoint` in the native action/query inventory); the remake warp guide also describes explicitly setting a point first: <https://game8.co/games/Zelda-Ocarina-of-Time/archives/637425>. Ownership alone is not an escape certificate; first-slice checker never credits the abstract Farore dispatcher. No native permission threshold or point-persistence claim is made from symbol names alone.

## Next-slice evidence/probe queue

Strongest candidates to settle with native data or remake guide before proposing entry changes:

- Child Bolero arrival at the crater: existing Central/Nearby cycle lacks an age-usable walk out; determine the actual ladder/climb/heat route, not a tunic assumption.
- Child Requiem arrival at the Colossus: establish reverse desert traversal and whether a held safe-destination song is necessary.
- Boss entries versus defeat/blue-warp requirements; one-way Shadow boat and Water/Fire/Jabu drops: determine physical backtracking and any local escape switch.
- Ordinary no-exit graph islands (pot, cow section, roof, courtyard, dungeon corridors): obtain plain same-scene walk-back evidence. Graph absence alone does not enter bucket 1.

No repeated Slingshot test: Claude explicitly removed that checklist; its launcher/checklist were deleted. Its generated isolated seed is CLI smoke evidence only.

### Data/guide findings that narrow the probe

- [Eurogamer crater guide](https://www.eurogamer.net/zelda-ocarina-of-time-death-mountain-crater), Gold Skulltula #2 / Heart Piece #2: child Bolero arrival and a heat timer are documented; the guide does **not** establish a walk out. No child tunic assumption or new reverse edge follows.
- [Eurogamer Mirage Desert guide](https://www.eurogamer.net/zelda-ocarina-of-time-mirage-desert), Adult timeline: forward sand-wave/target and Lens/ghost route are described. It does **not** establish child reverse traversal.
- Jabu `Depths -> Past Big Octo` requires a damaging stick/sword after Boomerang stun (`r4-logic-child.md:1186-1228`, Nintendo Life/IGN). The northwest-hole evidence describes the **upper Skulltula ledge**, not every place folded into the Depths region; the old open question is not proof of no return. Actual seed 7 diagnostics still flag Depths/Past Big Octo at the final 22-sphere inventory, demonstrating structural graph debt. No whole-Depths entry restriction is invented.
- Fire pillar-lowered route already carries Hammer/Time prerequisites (`r4-logic-adult.md:112-140`; Nintendo Life Fire guide); Phantom Ganon's normal approach carries Bow through the Poe events. Those implications are not a new second physical-trap observation.
- Water river exit has native Longshot targets; Shadow has a post-boat permanent bombed-pillar crossing (`03-game-data.md` sections 13 Water/Shadow). A Shadow return-bell ride and boss-door reopen behavior remain unplayed in the remake. These need further native room/door mapping before requesting more gameplay.

### One combined residual-unknown probe (staged, unplayed)

`E:/OOTRemake/work/r16-softlocks/ingame/Test - return-probe.bat`, checklist `return-probe-checklist.md`. **25–35 minutes**. Fresh empty `user-return-probe` save; no player progress copied. Current Longshot template, pinned rc.4, HOS_FS_OVERLAY unset, exactly one selected mod. Controlled external placements provide a small early song/ocarina kit; **not a certified solo seed**. No seed contents are committed here.

Stages: (A) Minuet permission from building, dungeon lobby and idle/active Gohma arena, since `EventQueryPlayerIsAbleWarp` is opaque; (B) actual child Bolero landing, immediate safe-song escape and a timed plain-return inspection; (C) actual child Requiem landing, safe-song escape and a bounded reverse-desert check. The checklist keeps an outside manual checkpoint for experiment recovery, never as a logic escape. Only teleport/clock cheats; no item/quest grants.

The control requires actually walking from Minuet's Meadow arrival back to **Kokiri Forest** with the same kit, not merely seeing a successful warp. The existing model permits `Sacred Forest Meadow -> SFM Entryway -> LW Beyond Mido -> LW Forest Exit -> Kokiri Forest` without extra equipment (direct Search/BFS smoke observed this path). That is model evidence, not a new physical-walk verification; a native gate mismatch stops the packet before calling Minuet a safe escape.

Build passed (101 files); all four controlled rewards were independently read back from the serialized native child placement; rc.4 launcher **dry-run** passed. No game started. Claude must boot-check the current teleport controls before handoff. Native destination anchors supply the coordinates; no guessed dungeon floor is used. This packet does not certify every boss room or the deferred adult boat/drop routes.

## Output compatibility

The cause list was posted to `cs-r16` before rule changes. The only placement rule changed is Slingshot Room entry: fill cannot count its chests before an age-usable existing escape tool is available. This changes the fill frontier and can cascade subsequent placements. No version bump by this track.

Native-prepared seed-0 comparisons against the previous entry rule:

| Mode | Changed placements |
|---|---:|
| Defaults (Token off) | 0 |
| Recommended (Token off) | 75 |
| Token on | 185 |

Defaults seed 0 retained its placement SHA-256; this is not a promise of unchanged output for other seeds. Exact before/after digests are in `E:/OOTRemake/work/r16-softlocks/placement-impact.json`.

## In-game boundary

No new gameplay verification claimed. Kareem's observed softlock and prior Boomerang switch observation are played evidence; broader return-path repairs need native/guide citations and staged checks.

## Completed dump-free world-mode diagnostics

Each column covers seeds 0–199 (200 generated and audited); Slingshot certificate failures: **0 in every column**. These are counts of seeds with a graph return failure at any sphere, deduplicated by age/region, not confirmed physical traps. Canonical spawn/song dispatcher nodes are excluded. Remaining logic proxies, terminal states and ordinary missing exits still need triage. These six modes use the committed world model; real Gift modes are reported separately after native preparation.

| Age | Region | Defaults | Keys anywhere | Shop | Token on | Open Forest | Free travel |
|---|---|---:|---:|---:|---:|---:|---:|
| adult | `Adult Spirit Temple Climb` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Beyond Door of Time Skippable Locations` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Child Spirit Before Locked Door` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Child Spirit Temple Climb` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Colossus Great Fairy Fountain` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Colossus Grotto` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `DMC Central Nearby` | 176 | 170 | 104 | 175 | 177 | 154 |
| adult | `DMC Pierre Platform` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Desert Colossus` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Desert Colossus From Spirit Lobby` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Desert Colossus Hands` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Dodongos Cavern Before Upper Lizalfos` | 11 | 22 | 15 | 55 | 11 | 65 |
| adult | `Dodongos Cavern Bomb Bag Ledge` | 0 | 0 | 0 | 44 | 0 | 0 |
| adult | `Dodongos Cavern Climb` | 5 | 14 | 8 | 27 | 4 | 34 |
| adult | `Dodongos Cavern Far Bridge` | 0 | 0 | 0 | 44 | 0 | 0 |
| adult | `Dodongos Cavern Lobby` | 0 | 0 | 0 | 44 | 0 | 0 |
| adult | `Dodongos Cavern Lower Right Side` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Dodongos Cavern Staircase Room` | 5 | 14 | 8 | 49 | 4 | 34 |
| adult | `Dodongos Cavern Torch Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Dodongos Cavern Upper Lizalfos` | 0 | 0 | 0 | 41 | 0 | 0 |
| adult | `Early Adult Spirit Temple` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Before Boss` | 75 | 57 | 85 | 85 | 75 | 79 |
| adult | `Fire Temple Big Lava Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Boulder Maze Lower` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Boulder Maze Upper` | 200 | 198 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Elevator Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Flame Maze` | 142 | 184 | 154 | 146 | 140 | 150 |
| adult | `Fire Temple Lower Locked Door` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Narrow Path Room` | 200 | 198 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Near Boss` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Fire Temple Upper` | 89 | 69 | 106 | 96 | 88 | 94 |
| adult | `Forest Temple Basement` | 62 | 78 | 62 | 57 | 62 | 57 |
| adult | `Forest Temple Before Boss` | 62 | 78 | 62 | 57 | 62 | 57 |
| adult | `Forest Temple Block Push Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple Bow Region` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple Central Area` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple Falling Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple Frozen Eye Switch Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple NE Outdoors` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple NW Outdoors` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple NW Outdoors Freestandings` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple Outdoors High Balconies` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple Outside Upper Ledge` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Forest Temple Straightened Hall` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `GF Above Jail Child Locations` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `GF Roof Gold Skulltula` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganondorf Boss Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Deku Scrubs` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Fire Trial` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Fire Trial Ending` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Forest Trial` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Forest Trial Ending` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Forest Trial Wind Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Light Trial` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Light Trial Boulder Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Light Trial Ending` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Main` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Shadow Trial` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Shadow Trial Ending` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Shadow Trial First Gap` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Shadow Trial Second Gap` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Spirit Trial` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Spirit Trial Ending` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Spirit Trial Second Room Back` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Spirit Trial Second Room Front` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Tower` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Tower Below Boss` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Water Trial` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ganons Castle Water Trial Ending` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Boulder Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Central Maze Right` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Eye Statue Lower` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Eye Statue Upper` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Hammer Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Heavy Block Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Lava Room Back` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Lava Room Front` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Like Like Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Underwater` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Gerudo Training Ground Water Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Hideout Kitchen Pots` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ice Cavern Behind Ice Walls` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ice Cavern End` | 110 | 120 | 116 | 81 | 109 | 87 |
| adult | `Ice Cavern Map Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Ice Cavern Spinning Scythe Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Kak Impas House Near Cow` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple 3 Spinning Pots Rupees` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple After Wind` | 193 | 198 | 193 | 189 | 193 | 193 |
| adult | `Shadow Temple Before Boss` | 55 | 107 | 67 | 55 | 55 | 56 |
| adult | `Shadow Temple Beginning` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple Beyond Boat` | 55 | 107 | 67 | 55 | 55 | 56 |
| adult | `Shadow Temple Beyond Boat Scarecrow` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple Beyond Boat SoT Block` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple Boat` | 55 | 107 | 67 | 55 | 55 | 56 |
| adult | `Shadow Temple Falling Spikes` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple First Beamos` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple Huge Pit` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Shadow Temple Invisible Spikes` | 199 | 200 | 199 | 200 | 199 | 199 |
| adult | `Shadow Temple Wind Tunnel` | 193 | 198 | 193 | 189 | 193 | 193 |
| adult | `Spirit Temple Anubis Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Spirit Temple Before Boss` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Spirit Temple Beyond Anubis Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Spirit Temple Big Mirror Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Spirit Temple Boulder Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Spirit Temple Central Chamber` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Spirit Temple Lobby` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Twinrova Blue Warp` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Twinrova Boss Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Wasteland Near Colossus` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Before Boss` | 186 | 192 | 169 | 179 | 189 | 142 |
| adult | `Water Temple Boss Key Chest Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Central Bow Target` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Cracked Wall` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Dark Link Region` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Dive` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Dragon Statue` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple East Geyser Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Falling Platform Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Lowered Water Levels` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple Middle Water Level` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple North Basement` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple River` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `Water Temple South Basement` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `ZF Hidden Cave` | 200 | 200 | 200 | 200 | 200 | 200 |
| adult | `ZF Underwater` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Beyond Door of Time Skippable Locations` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Bottom of the Well Behind Fake Walls` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Bottom of the Well Behind Locked Doors` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Bottom of the Well Left Side` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Bottom of the Well Main Area` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Child Spirit Before Locked Door` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Child Spirit Temple Beyond Metal Bridges` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Child Spirit Temple Climb` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Colossus Great Fairy Fountain` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `DMC Central Local` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `DMC Central Nearby` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `DMC Ladder Area Nearby` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `DMC Pierre Platform` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Deliver Rutos Letter Region` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Desert Colossus` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Desert Colossus From Spirit Lobby` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Desert Colossus Hands` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Dodongos Cavern Before Upper Lizalfos` | 105 | 142 | 111 | 147 | 122 | 107 |
| child | `Dodongos Cavern Bomb Bag Ledge` | 36 | 49 | 45 | 97 | 44 | 45 |
| child | `Dodongos Cavern Climb` | 105 | 142 | 111 | 147 | 122 | 107 |
| child | `Dodongos Cavern Lobby` | 105 | 142 | 111 | 147 | 122 | 107 |
| child | `Dodongos Cavern Lower Right Side` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Dodongos Cavern Staircase Room` | 105 | 142 | 111 | 147 | 122 | 107 |
| child | `Dodongos Cavern Torch Room` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Dodongos Cavern Upper Lizalfos` | 36 | 49 | 45 | 97 | 44 | 45 |
| child | `GC Spinning Pot` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `GF Above Jail Child Locations` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `HC Garden Skippable Locations` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Jabu Jabus Belly Depths` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Jabu Jabus Belly Main` | 17 | 11 | 16 | 12 | 43 | 13 |
| child | `Jabu Jabus Belly Past Big Octo` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Kak Impas House Near Cow` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Market Mask Shop Storefront` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Spirit Temple Central Chamber` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Spirit Temple Lobby` | 200 | 200 | 200 | 200 | 200 | 200 |
| child | `Wasteland Near Colossus` | 200 | 200 | 200 | 200 | 200 | 200 |

