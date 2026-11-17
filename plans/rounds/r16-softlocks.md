# Round 16 Track A: softlocks without a save warp

Agent cs16a; branch `r16/softlocks`; base `dd3b4537204cab9f81ccf45d5d590d7fb517c04b`.

## Scope and established evidence

Kareem, 2026-11-16, Longshot rc.4 (roadmap Round 16): no save warp; room transitions autosave. Entering the Deku Tree 2F Slingshot Room without Slingshot, Boomerang or Bow trapped him. No player seed, save or spoiler was opened by this track. No game launched.

Existing native evidence: `Banc/InsideTheDekuTree/InsideTheDekuTree_Static.bcett.byml.zs`, room 2, eye switch `Obj_EyeSwitch_A_02` Hash 9080063866993537303 and falling ladder Hash 2096903280161003875, module `InsideTheDekuTree_Level_Room_C_Prefab_efa7` (`child_deku_tree.toml`; game-data section 12). Keep the shield condition and require the existing exit predicate at entry. Bow remains the pre-existing unverified alternative, not a newly loosened rule.

## Work and verification

Failing-before: `uv run pytest tests/test_softlocks.py -q` => 2 failed, 2 passed. Printed actual state: sphere 1 collected both room chests with only Deku Shield, and the incoming rule was `here(has_shield)`. After requiring the existing exit predicate at entry: `uv run pytest tests/test_softlocks.py tests/test_world_remake.py -q` => 28 passed.

The return checker inspects the initial frontier and every full search sphere, not just the spoiler's progression-filtered rows. `Search.inventory(age)` preserves the independent child prefix. Synthetic regressions cover own-room rewards, future loot, exact arrival time, waiting where time passes, adult items unavailable to child, and refusal through ordinary and external placement APIs. `uv run pytest tests/test_softlocks.py -k "not fixed_real_world" -q` => 11 passed, 27 deselected.

`Root` is an abstract OoTR spawn/warp dispatcher with no physical incoming path. Return anchors are the actual spawn rooms (child Link's house, adult Temple of Time), not a fabricated save-warp edge to Root. Abstract-only nodes will be explicitly classified. Native warp permission research and the serialized 1,800-seed before-repair sweep are running. Scratch scripts/results: `E:/OOTRemake/work/r16-softlocks/`.

## Triage and accepted first slice

Maintainer direction (Claude, current conversation): physical safe anchors, not Root; if ordinary return debt dominates, land the evidenced-trap slice with full gates and leave ordinary returns for the next slice. This slice enforces the Slingshot Room certificate. The raw whole-world checker remains diagnostic; it is **not an all-world softlock-free certificate**.

Snapshot posted to `cs-r16` before broad rules: 595 completed seed/preset pairs (Defaults 200, Recommended 200, keys-anywhere 195), zero fill failures, **161 raw region-age groups**. Counts below are distinct region-age groups, not confirmed physical softlocks:

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

Full machine-readable per-region/per-preset records and counts stay outside the repository at `E:/OOTRemake/work/r16-softlocks/sweep-before.jsonl` and `sweep-before-summary.json` (the latter is written when the sweep completes). This is logic-only research, not a player spoiler.

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

Only residual data-opaque cases belong in **one combined fresh-isolated-save probe**, after these traces. No repeated Slingshot test: Claude explicitly removed that checklist; its launcher/checklist were deleted. The generated isolated seed remains only as CLI smoke evidence, not a request for Kareem's time. Combined probe staging and estimate will be recorded here after the remaining evidence arrives.

## Output compatibility

Rule changes can change all presets, including Defaults and Token-off. Exact exercised comparisons and cause list will be recorded after the sweep. No version bump by this track.

## In-game boundary

No new gameplay verification claimed. Kareem's observed softlock and prior Boomerang switch observation are played evidence; broader return-path repairs need native/guide citations and staged checks.
