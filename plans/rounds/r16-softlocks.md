# Round 16 Track A: softlocks without a save warp

Agent cs16a; branch `r16/softlocks`; base `dd3b4537204cab9f81ccf45d5d590d7fb517c04b`.

## Scope and established evidence

Kareem, 2026-11-16, Longshot rc.4 (roadmap Round 16): no save warp; room transitions autosave. Entering the Deku Tree 2F Slingshot Room without Slingshot, Boomerang or Bow trapped him. No player seed, save or spoiler was opened by this track. No game launched.

Existing native evidence: `Banc/InsideTheDekuTree/InsideTheDekuTree_Static.bcett.byml.zs`, room 2, eye switch `Obj_EyeSwitch_A_02` Hash 9080063866993537303 and falling ladder Hash 2096903280161003875, module `InsideTheDekuTree_Level_Room_C_Prefab_efa7` (`child_deku_tree.toml`; game-data section 12). Keep the shield condition and require the existing exit predicate at entry. Bow remains the pre-existing unverified alternative, not a newly loosened rule.

## Work and verification

Failing-before: `uv run pytest tests/test_softlocks.py -q` => 2 failed, 2 passed. Printed actual state: sphere 1 collected both room chests with only Deku Shield, and the incoming rule was `here(has_shield)`. After requiring the existing exit predicate at entry: `uv run pytest tests/test_softlocks.py tests/test_world_remake.py -q` => 28 passed.

The return checker inspects the initial frontier and every full search sphere, not just the spoiler's progression-filtered rows. `Search.inventory(age)` preserves the independent child prefix. Synthetic regressions cover own-room rewards, future loot, exact arrival time, waiting where time passes, adult items unavailable to child, and refusal through ordinary and external placement APIs. `uv run pytest tests/test_softlocks.py -k "not fixed_real_world" -q` => 11 passed, 27 deselected.

`Root` is an abstract OoTR spawn/warp dispatcher with no physical incoming path. Return anchors are child Link's house or Kokiri Forest, adult Temple of Time, not a fabricated save-warp edge to Root. Scratch scripts/results: `E:/OOTRemake/work/r16-softlocks/`.

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

Direct native probe `uv run python E:/OOTRemake/work/r16-softlocks/slingshot_native.py` passed: room 2 contains the exact existing `Obj_EyeSwitch_A_02` 9080063866993537303 and falling ladder 2096903280161003875. Read-only dump; no generated working-set file is added.

## Native warp evidence for the next slice

Read-only native `Event/EventFlow/Dm_SY_Ocarina.bfevfl.zs`, entry `OcarinaWarp`: Event132 calls `Player_Event.EventQueryPlayerIsAbleWarp`; refusal opens SimpleInfo Type 11 and cancels. The accepting chain checks the Biggoron trade timer and Epona-race subflows, reserves the age-specific Banc arrival, then Event76 requests autosave. External decode citation: `E:/OOTRemake/work/ocarina-autoplay/out/flow_Dm_SY_Ocarina.txt:431-491`; destination arguments at 137-157.

**The opaque native permission query is not evidence that dungeons, buildings or boss rooms allow warping.** No global song-escape edge is added on the strength of a missing flow-side scene check. Existing adult ocarina/age rules remain unchanged. Child Fairy Ocarina + Minuet was played on 2026-11-08 (R6-MINUET); that does not establish every scene or adult Fairy Ocarina use.

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

Build passed (101 files); all four controlled rewards were independently read back from the serialized native child placement; rc.4 launcher **dry-run** passed. No game started. Claude must boot-check the current teleport controls before handoff. Native destination anchors supply the coordinates; no guessed dungeon floor is used. This packet does not certify every boss room or the deferred adult boat/drop routes.

## Output compatibility

Rule changes can change all presets, including Defaults and Token-off. Exact exercised comparisons and cause list will be recorded after the sweep. No version bump by this track.

## In-game boundary

No new gameplay verification claimed. Kareem's observed softlock and prior Boomerang switch observation are played evidence; broader return-path repairs need native/guide citations and staged checks.
