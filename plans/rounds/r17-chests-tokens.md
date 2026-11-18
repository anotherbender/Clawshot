# Round 17 — Track C: held chests and tokens (cs17c)

Base: `fcd5f2a95a69be2110c4a5806aa5c2d6975f8990`, branch `r17/chests-tokens`.
Agent: `openai-codex/gpt-6.1-sol`. Started 2026-11-17.

## Scope and safety

Research the twelve spots in `E:/OOTRemake/work/r17-chests/CHEST-HUNT.md` before Kareem's answers; admit only confirmed one-time checks, with regression coverage. Never count Kokiri/Lost Woods ledge, normal/Alternative windmill, or child/adult Valley invisible copies twice. Goron City's failure chest and Dampé's repeat rupees remain held deliberately.

Stage D17's held Treasure Chest Game prize experiment with a fresh agent-owned seed and isolated empty saves; research room-key tracking. Identify Ganon Castle's mimic actors from native data. Measure Token destination bias across seeds/presets, evaluate fill-side improvement and gift-held items without widening unplayed reward admission.

No game or user seed/save is opened or started. Native files are read-only. Research scripts, decoded data and test mods stay outside the repository under `E:/OOTRemake/work/r17-chests/` and `E:/OOTRemake/work/r17-tokens/`. Nothing writes into Hookshot/Longshot folders. Claude boot-checks; Kareem supplies all game observations.

## Held chest spawn research
Evidence: `E:/OOTRemake/work/r17-chests/spawn-report.md`, reproduced once by `spawn_probe.py` (19 s, completed).
Read-only Banc placements, actor packs, event flows, GameDataList and the external round-14 decoded AINB cache
(`ainb` used unmodified; GPL facts only). No executable/collision mesh inspected and no route played by this agent.

Initial research before played answers (subsequent admissions are recorded below):

| Hunt spot | Native spawn/entrance evidence | Initial played proof needed |
|---|---|---|
| Forest bridge ledge | Unconditional chest; no nearby placed traversal helper. KF and LW copies align under one scene offset. | Climb, age/tools, safe return and scene actually loaded. |
| Ranch tower high chest | Unconditional; child movable-box puzzle and Sun's Song fairy-note logic do not spawn it. | Climb, age/tools and safe return; not the floor Heart Piece. |
| South Field grove | Adult-only unconditional chest. Nearby Poe has no link; child note describes butterfly/stick fairy puzzle. | Presence/opening and route on an adult visit. |
| North Field tree | Adult-only unconditional chest. Child note's read flag has no spawning reader; tree hint is separate. | Presence/opening and route. |
| Lake southwest shore | Adult-only unconditional chest; child note/pots and adult Poe are separate. | Route at actual lake water/story state. |
| Lake island grave grotto | **Four**, not three, timed candles; all must be burning together. `HidingHole_Level_Hole_30_Prefab_9583` drives `Gimmick_TreasureBoxAppear_Magic_bce2`. | Actual fire method, age, timing and return. |
| Windmill | Unconditional in each adult layout; lamps nearby, no dedicated hook target. | Actual grapple/climb and safe return; variant identity below. |
| Valley tent grotto | Shared cover `Land_Gerudo_HidingHoleCover_A_02`, graph `Gimmick_Ocarina_Appearance_01_GerudoValley/..._eb46`, Storms-disappearance flow. | Storms opening/entry in each played age; Lens requirement for red chest. |
| Valley Octorok grotto | `Obj_LiftRock_B_01` sits on its entrance; own attack identifier specifies Silver Gauntlets. Old register's “silver rock gone” conflicts with this data. | Adult lift/entry/return; not an ordinary dive inference. |
| Fortress underground | Uncovered hole in `GerudoFortress_Level_Room_02/..._5d06`, near guards/interior props; landing/exit below. | Which outdoor doorway reaches room 02 and safe guard/return route. |
| Fountain ruin | Pierre appears at chest height; call area below, Hookshot-aim reaction on Pierre. | Scarecrow/Hookshot route and return; this route is [INFERENCE], not yet a rule. |
| Well room 11 | Fake floor has no player collision; chest beyond it. | Jump/edge path across the hole and safe return; corridor width not proved. |

Lake candle details: `Obj_CandleStick_TimeExtinguish_A_01` has a 15-second burn timer (last five weak);
none starts lit, no local fire source was found. Graph ANDs four Burning outputs, then saves
`LakeHylia_secretHole_appearTreasureBox`, shared across ages. Din's Fire/Fire Arrows or a carried lit stick are
**candidate methods**, not verified solutions. Do not turn that list into an OR rule without play.

### Copy safety and canonical identity

The three presumed-copy pairs have different actor Hashes and distinct saved `IsTreasureBoxOpen` children:

| Pair | Actor Hashes |
|---|---|
| KF / Lost Woods ledge | `4349272251343787229` / `17479747339356189279` |
| Windmill normal / Alternative | `11929552275106311978` / `13080955777249750889` |
| Valley invisible adult / child | `18413589940135955604` / `6205043616869463865` |

The native chest reader/writer uses its own `InstanceIDString`: `AI/Obj_TBox_A_01.root.ainb` node 2,
`TreasureBox.module.ainb` node 1, `TreasureBox.event.root.ainb` nodes 5–7. No placement sync/reference or event-flow
override was found. **[INFERENCE]** they could pay separately; this is not proof of two legitimate checks.
The user policy remains one check at most per pair, never two pool contributions.

Kakariko's entrance selector uses `Sequence_IsAlternative_KakarikoAdult`; the expression depends on adult
and completed Forest/Fire/Water sage quests. **[INFERENCE]** normal windmill becomes permanently unavailable after
those three completions. Never release its normal copy as unrestricted progression on the strength of its route alone.
The Valley green chest, ranch chest, candle chest and other same-Hash age copies do share their native identity.

**Ruling — Claude, 2026-11-17:** each pair admits exactly **one** canonical copy, chosen for non-missable
availability and the simplest verified rule. Its other copy keeps its vanilla rupee and stays out of logic,
like Dampé's repeats. Independent native flags do not authorize two shuffled checks.

- **Windmill:** Alternative Hash `13080955777249750889` is canonical. When its route is confirmed, its rule must
  require adult plus completion of Forest, Fire and Water sages, alongside the verified traversal tools.
  Normal Hash `11929552275106311978` remains vanilla permanently because it is missable.
- **Forest ledge — updated by Kareem/Claude's first hunt answer:** Kokiri Forest Hash `4349272251343787229`
  is **never canonical**. Kareem found the KF side unreachable and hit a death plane while noclipping toward it.
  Only Lost Woods Hash `17479747339356189279` could qualify, pending its own safe route. The earlier KF tie-break
  is superseded; KF stays permanently vanilla/out of logic.
- **Valley invisible chest:** choose after Kareem's route answers, preferring the confirmed age; if equal, use
  adult Hash `18413589940135955604`, leaving the child copy vanilla.

The ruling resolves pool identity, not unplayed access. No `False` access rule is released until Kareem confirms
the route. Regression coverage on admission must prove the canonical gate and the other copy's exclusion from
logic/pool. Goron failure and both Dampé repeat-rupee holds remain deliberately unchanged.
First hunt answers received: KF side is unreachable (above). Windmill chest existence/visibility is still being
checked near the hanging lamps; no spawn/Presence/link condition exists on either placed adult chest.

### First-answer follow-up: death plane and windmill visibility

Kareem's noclip/death-plane observation is ground truth; no attempt was made to reproduce it by starting the game.
The native follow-up (`followup_probe.py`, `area_roles.py`; external `out/followup-probe.json` and
`out/area-roles.json`) found no nearby placed Area linked to a named **player-kill** module. The bridge's nearby
groups are `Common_FieldDungeonEntranceSet_bad1`, `GossipStoneWithFairySpirit_d931` and
`Gimmick_AreaContact_FallDown_Item_d715`; the last is an **item** fall trigger, not proof of a player death plane.
The chest is within the nominal bounds of a GroupID 1 `AreaCullingTargetArea` near that ledge; culling is not
death. **The KF kill/void volume itself is not identified.** Collision meshes/materials and executable bounds
were not inspected, so attributing his death to a specific volume would be speculation.

Windmill: the actor is a real `Obj_TBox_A_01` with purple rupees at Banc `(5.56, 130.17, 41.43)`, about 21 m above
the Heart Piece. Both normal and Alternative adult Dynamic files contain it at effectively the same transform;
the scene table lists both as actual adult scenes, not a demo-only layer. The chest has no Presence, SpawnType,
Room/layer annotation, link or AiGroup reference; neither scene file has a special Phive placement group.
There is **no data-backed puzzle trigger explaining a missing chest**. Occlusion, placement inside/above unused
geometry, or a runtime placement/culling condition are **[INFERENCE]**, not established causes. No unsafe spawn
patch or invented route is made; Alternative remains held while Kareem checks rendering near the lamps.

### Played admissions — first batch

Kareem, finished-save routes, forwarded by Claude on 2026-11-17:

| Canonical check | Admitted requirement |
|---|---|
| Lost Woods purple bridge ledge | Adult and the existing Lost Woods `here(can_plant_bean)` child-planting event |
| Ranch tower high seed chest | Adult and usable Hookshot |
| Windmill Alternative purple chest | Adult, usable Longshot, Defeat Phantom Ganon, Defeat Volvagia and Defeat Morpha |

The bridge spot is real, not invented: `Obj_SmallFarm_A_01` Hash `5234955674857122897` and adult
`Obj_SmallFarm_A_03` Hash `8765528183303847440`, native `LostWood_Common_f395`. World `lost_woods.toml` already
uses `here(can_plant_bean)` for the bridge exit; the rule compiler deduplicates that exact region/subrule pair.
This preserves child planting followed by adult riding, without adding a new bean spot or allowing adult-owned
beans to stand in for child history. KF remains permanently vanilla.

Tower route is Hookshot to a vine wall, then climb; not the floor Heart Piece. Windmill route is Longshot to a
rooftop, then Longshot to the windmill ladder and climb. Hookshot is **not** admitted there. Alternative is the
one post-three-sages canonical check; normal remains permanently vanilla.

`CLAWSHOT_WORKERS=1 uv run pytest tests/test_world_chest_hunt.py -q`: **14 passed in 6.89 s**.
Tests cover child history, age/tool gates, each missing sage, owned medallions not replacing quest completion,
and only one pool contribution per pair. Three checks join the shuffle (165 → 168); their existing Banc files
were already in the working set. More hunt answers will batch before the final commit/gate.


## Treasure Chest Game

Packet: `E:/OOTRemake/work/r17-chests/tcg-170317/`, launcher `Test - tcg-170317.bat`, checklist `CHECKLIST.md`,
manifest `manifest.json`, post-play reader `read_state.py`. Research report: `E:/OOTRemake/work/r17-chests/tcg-report.md`.

**170317 is an agent-owned diagnostic identifier, not a generated full seed.** Existing
`clawshot.tools.swap_chest` has no randomness/settings: one `Drop__DropActor` field changes at prize
Hash `16881481538337649070`, Heart Piece → Boomerang. Ten room boxes and the repeat red-rupee prize remain
field-for-field vanilla; the prize's native open event, Lens preview and owner dialogue are unchanged.
The external packet's field-restoration/determinism checks passed; native decompressed size is unchanged and
the existing size entry covers it, so exactly one Banc resource ships and no size table.

Launcher derives from `E:/OOTRemake/tools/test-launcher-template-longshot.bat`, locates rc.7 in `builds/*/bin`,
accepts only the identified rc.7 executable, clears `HOS_FS_OVERLAY`, and loads one mod only. Dry run resolved the
rc.7 executable without starting it. This track created an empty packet-only save UID and temp folder under
`user-tcg-170317`; no original saves or played seeds were copied/read. **Not booted or played.**

### Kareem checklist / Claude boot-check handoff

Estimate **15–25 minutes**, plus shader warm-up; optional repeat-prize check adds about five minutes.
Claude boot-checks only once the running game is closed; then hands over the external full checklist.

1. New game, child. Collect 16 rupees from Mido's four vanilla chests; do not obtain another Boomerang.
2. Teleport to child Market, set night (~22:00), enter Treasure Chest Shop, inspect native “Piece of Heart” prize text.
3. Pay 10 rupees and use the owner's key on door one.
4. **Explicit diagnostic exception:** No-clip flight only to cross the next five locked doors, then land and turn it
   off before opening the prize. No inventory, flags, quantity, age or quest edits. This tests contents, **not a native
   five-room victory**; without Lens, five independent 50/50 rooms make a fresh-save test much longer.
5. Open final chest: expect Boomerang model/text, no heart-piece/MaxLife increase, then the owner's win dialogue.
   Equip and throw the Boomerang outside. Capture any freeze, duplicate notice or unexpected heart screen.
6. **Manual save** after the dialogue, quit/Continue, verify Boomerang usable and first-clear state persisted.
   Debug-mode autosave suppression is documented upstream; Claude must confirm rc.7 controls/behavior.
7. Optional after native 12-hour cooldown: another paid approach gives the vanilla Red Rupee, not another Boomerang.
   If Set time cannot advance that cooldown, record it as untested rather than editing flags.

Required log proof: rc.7 version/source, exactly one mod, and
`mods: Banc/Market/Market_Child_Static.bcett.byml.zs <- .../tcg-170317/romfs/...`.
After play, `read_state.py` reads **only this packet's save**, checking `MiniGame_ChoiceTreasure_IsClear`,
Boomerang ownership, no heart-piece stock and unchanged initial life.

### Keys: session state, not dungeon small keys

Native sources: `Event/EventFlow/MiniGame_SequentialChoiceTreasure.bfevfl.zs`,
`MiniGame_SequentialChoiceTreasure_cbde`, `..._BoxShuffle_84ca`, `MiniGame_ChainLockedDoor_cce0`,
`AI/Obj_HrlCity_Shop_DoorChainLock_A_01.root.ainb`, `AI/Obj_MiniGame_SmallKey.root.ainb`, and GameDataList.

- `MiniGame_SmallKeyNum` is an unsaved Int (`SaveFileIndex=-1`); `Obj_MiniGame_SmallKey` is NotPushToPouch.
  No saved per-room key item/counter exists.
- Owner hand-over and winning boxes reach flow Event55's +1, separately from the item's pickup display.
  Six locks each subtract one; the owner supplies the first, five winning room boxes supply the rest.
- End/retry zero the count; Ready re-locks doors, respawns boxes and independently rerolls each pair 50/50.
  Room boxes are repeat-open actors, not one-time checks.
- Saved `MiniGame_ChoiceTreasure_IsClear` selects first Heart Piece chest versus repeat Red Rupee chest.

**Conclusion:** current key shuffling is not feasible by merely admitting a SmallKey actor or changing chest
contents. Persistent shuffling would need saved key state, reset/door changes, fixed box identities and once-only
collection, including untested AINB changes. Those changes are not planned or implemented.
D17's prize-only swap is structurally feasible but remains held for the game result.

**Ruling — Claude, 2026-11-17:** retain the native Heart Piece Lens preview and owner's Piece of Heart line
when the prize shuffles. Document both as a **known cosmetic mismatch**, matching Dampé/Bombchu Bowling policy.
**No persistent-key mode.** The staged packet already follows this ruling; room keys and repeat boxes stay vanilla.

Magic-item admission remains unproved: minigame grant branch selection and magic-meter initialization need their
own evidence. A possible native autosave-before-IsClear window is [INFERENCE], not patched.

## Ganon Castle mimic chests

Native/static identification, not a replay of Kareem's observation: `Obj_TBox_A_04`, with
`ActorLogicTrapTreasureBox`, is an object trap, not an enemy or shuffled reward. Four instances in
`Banc/InsideGanonCastle/InsideGanonCastle_Static.bcett.byml.zs`:

| Hash | Room / trial |
|---|---|
| `3253191540272036329` | 5 / Water |
| `11406545451127340703` | 12 / Light |
| `17726220643880970879` | 12 / Light |
| `5732331492537302993` | 12 / Light |

`Gimmick_TrapTreasureBox_Set_cbc2` requests `TrapTreasureBoxOpen`; `Dm_SY_TreasureboxSmall:TrapOpen`
kicks the chest, waits 45 frames and signals its attack. The actor's attack component specifies **Frozen**.
No `Drop__DropActor`, no ordinary chest-open struct child, no one-time item grant. Its object affiliation,
one life point, destruction component and green-rupee drop table explain a breakable trap; **[INFERENCE]**
hitting it destroys it for a green rupee. The opening graph records its own auto-generated state and removes
the event requester. The 240-frame rattle parameter is consistent with the opening/closing tell.

Two same-kind traps exist in GTG room 10 and Spirit room 18. D10 remains unchanged: all six stay outside checks.
Whether a specific room-12 Hash matches an N64 “first/second/third” label was not established.
Sources and exact pack/graph sections are in external `spawn-report.md` “Ganon's Castle mimic chests”.

## Token fill and gift-held rewards
### Baseline cause (native/static; not a game result)

`E:/OOTRemake/work/r17-tokens/measure.py --label inventory` builds the production native pool:
Gift setup, one-time Scrubs, floor policies, native chest links/event openings, progressive normalization and
the existing tier/container screens. Inventory captured before these changes in `inventory.json`.

| Recipe with Token | Shuffled checks | Token copies | Dungeon-item copies | Progressive copies |
|---|---:|---:|---:|---:|
| Defaults | 265 | 100 | 63 | 20 |
| Recommended | 397 | 100 | 63 | 20 |
| Recommended, small keys anywhere | 397 | 100 | 63 | 20 |
| All kinds, open Forest/Door, free travel, songs anywhere | 411 | 100 | 63 | 20 |

In this pre-admission measurement snapshot, every recipe has exactly 165 Chest and 100 Token destinations.
The three later played admissions intentionally increase chest capacity; the paired figures below isolate the
fill/gift-hold changes on the earlier identical world, not a predicted final-world percentage.
Shop/NPC/Song/Scrub/floor checks enlarge the pool, not token destinations. Whole-pool fractions are not a uniform
sampler target.
Gold Skulltula Token is progression: all 100 copies enter shared assumed fill, before late non-progression matching.
Own-dungeon items, the return kit, chest-only progressive copies and D25 bomb/ammo placements consume capacity first.
The late Skulltula filler matcher cannot undo those progression token placements.

Every Skulltula has the same 40-item catalogue, intersected with its location exclusions, item-kind holds and
counterfactual container screen (`allowed`). Progressive copies/tiers, keys/maps/compasses, songs, Fairy Ocarina,
trade cells, Gerudo Pass and Buy/shop stock are not admitted. Common admitted groups are equipment/fixed majors,
bottles, rupees, hearts, magic/spells/arrows, Lens/Echo Gem/Defense, seed and Time Ocarina; catalogue membership is
not pool presence. In Defaults, arrows of both admitted sizes each fit only one screened Skulltula, Bombs (5) and
Bombchus (5) each fit fifteen, Nuts fit all hundred, and Sticks fit none. Shared scarce slots cannot each take every
otherwise-compatible ammo copy. These are conservative fill-screen results, not new gameplay route findings.

Adding admitted **filler** alone need not lower token percentage: tokens are already placed before filler.
More admitted progression may compete differently, but no percentage is guaranteed. More ordinary chest checks
would increase actual token capacity; more Gift/Shop checks do not directly do so. No item or check type is admitted
merely to improve this metric.

### Candidate implementation

Proposed by cs17c: weighted random ordering only for token-item candidates with Token on, chest weight 2 and
Skulltula weight 1. This is a soft preference, not a reserved quota or hard exclusion. The same reachability,
`allowed`, safe swap, container and beatability checks remain. Token-off takes the original random-shuffle branch.
No new setting, item, location, token copy or native grant family.

### Gift-held follow-up

Prior maintainer acceptance: `r15-scrub-tokens.md:938–951` explicitly calls for Token destinations for these
independently played families while retaining chest safety. Recommended's native pool contains Bottle ×3, Milk
Bottle ×1, Double Defense ×1, Echo Gem ×1, gold rupee ×1. Previously all seven copies had derived
`Boss/Cutscene/NPC` holds and zero Skulltula destinations. The new derived hold adds **Token only**, only with
Token selected and catalogue admission present. They do not become chest-safe. Scrub-only fixed Nut/Stick upgrades
retain their separate holds. No new game proof is claimed: the existing rc.3 family packets remain the grant evidence.

### Paired native measurement result

Serialized under the owned round-17 gate lock, one worker while Longshot ran. Agent-owned seeds
`170300–170319`, twenty per recipe per implementation; **160/160 generated and passed beatability**.
This means no exhausted generation, not a claim of zero internal retries. Baseline uses the retained base fill
and legacy gift holds; candidate uses weighting plus the played Token extension. Native setup and check/pool counts
are identical across each pair. Logs/results: `baseline.log/.json`, `candidate.log/.json`, `measure-processes.txt`.

| Recipe (+Token) | Baseline native tokens /100 Skulltulas | Candidate native tokens /100 Skulltulas |
|---|---:|---:|
| Defaults | 57.75 | 47.80 |
| Recommended | 57.15 | 48.95 |
| Recommended, small keys anywhere | 53.70 | 47.05 |
| All kinds, open Forest/Door, free travel, songs anywhere | 56.90 | 47.45 |

Defaults contains none of the newly released gift-held copies, so its reduction demonstrates the sampler change
independently of that follow-up. No target percentage is promised.

Recommended's twenty candidate seeds actually placed the formerly gift-held items at Skulltulas:

| Item | Baseline draws | Candidate draws |
|---|---:|---:|
| Empty bottles | 0 | 33 |
| Milk bottle | 0 | 10 |
| Double Defense | 0 | 13 |
| Echo Gem | 0 | 13 |
| Gold rupee | 0 | 8 |

Effective holds remain `Boss/Cutscene/NPC/Token`, never Chest. Defaults has zero such draws because those items
are absent from its pool, not because the new destinations failed.

Output changes: Token-on fill/gift holds, and newly admitted chests with **Token either on or off**. The planned
Token-off comparison isolates old versus new **fill on the same current world**; it does not claim byte identity
to released 0.2.2 after adding checks. No version bump made here; maintainer release handling is required.
Final gates pending; not READY.

## Verification and handoff

Focused proof: `tests/test_world_chest_hunt.py`, `tests/test_generate_tokens.py` and `tests/test_settings_songs.py`. New synthetic coverage
checks soft weighted placement without self-locking, exact item/token conservation, and each formerly gift-held
reward actually reaching a Skulltula without becoming chest-safe (including normal-class Defense/gold rupee
through late filler). Existing scarce-arrow and shared-progression regressions remain unchanged.

Existing native coverage `test_every_admitted_member_has_its_native_shape_and_a_checked_pickup` already exercises
every catalogue donor, including these five item names. No new native input or working-set file is required;
reuse `E:/OOTRemake/work/rounds/r16/time-layered-dump`.

The old-base gate began on `45946c8a62`: targeted **103 passed in 6.11 s**; format printed one
required one-line `build_world` call, fixed exactly as printed. Claude then required stopping that
gate and rebasing onto Track A's merged main, `6ec4fdb`; the stopped gate is not final acceptance.
Only cs17c's owned lock was released. Its logs remain under `old-base-551d869/`.

Rebase onto `6ec4fdb` was clean: `5d8135aa4aca37a9dc715f958cf1db246f8a22c7`.
Focused tests on that rebased code: **117 passed in 11.51 s**; no game process present,
`CLAWSHOT_WORKERS=4`, serialized with the round-17 lock and no dump inputs.
Evidence: `E:/OOTRemake/work/r17-tokens/rebased-focused.log`.

**Final gate held by Claude's instruction:** Track B merges first; then rebase onto it and wait
for Claude's word before freezing and running the full gate. No final gate is queued or running.
Stage-start process checks and required worker caps remain mandatory. Same-world Token-off byte
comparison and final gate logs belong under `E:/OOTRemake/work/r17-tokens/`.
No agent-started game test is claimed. Played route evidence above belongs to Kareem; the TCG packet is unplayed.
