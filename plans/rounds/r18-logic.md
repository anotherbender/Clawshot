# Round 18 Track A: logic safety

Agent cs18a (`openai-codex/gpt-6.1-sol`), branch `r18/logic`, initial main `2ba2f9a`.

## Causes (before changing rules)

1. **Dampé (Kareem, played 2026-11-18):** adult cannot return after the first race; the windmill-side escape requires Hookshot. The translated `graveyard.toml` folds start, race, goal and exit into `Graveyard Dampes Grave`, gives it a free Graveyard return, and requires Song of Time rather than Hookshot for the windmill. Both first-race Hookshot chest and second-race Heart Piece inherit this false return. Native Banc/flow boundary trace is in progress; no rule changed before this cause post.
2. **Colossus (Kareem ruling, 2026-11-18):** both ages must leave by a different usable warp song; reverse Wasteland walking is impractical. Translated `Desert Colossus -> Wasteland Near Colossus = True` falsely certifies escape. Round 17's Requiem guard explicitly exempts adults and only guards the warp dispatcher, not walking arrivals. The checker correctly reuses age/instrument-sensitive song rules, but still credits that false reverse walking edge. All external adult arrivals need a pre-held usable escape; neither Requiem itself nor child-only Fairy Ocarina is an adult escape.

## Scope and evidence standard

Logic-only changes; no gameplay event patches, game launch, player seed or save access. Existing played reports are the repro. New logic is built/tested, not a claim of new in-game behavior. Track G owns forced-scene safety (Dampé and twelve song lessons). Native game data is read-only; research output stays under `E:/OOTRemake/work/r18-logic/`.


## Dampé boundary facts and Track G handoff

Read-only native build `e0f3ccfa`, `Banc/Graveyard/Graveyard_Adult_{Static,Dynamic}.bcett.byml.zs` and
`Event/EventFlow/MiniGame_DampeRace.bfevfl.zs`. No game launched. Decoded research stays outside the repo.

| Physical part | Native identifiers / boundary | Logic treatment |
|---|---|---|
| Race start | StartPos `4`, `5`, `6` at x22–24/y78.6/z−10.9; start shutter Hash `15463667043472836912`, x27.4/y78.6/z−11 | Included in `Graveyard Dampes Grave`; conservative Hookshot guard before the entire descent |
| Start shutter | `UnderTheGrave_Prefab_eb77` opens only during `Playing` or `PlayingSecond` | No asserted reverse-race return after finishing |
| Race end | Final timed shutter Hash `9791590597827914786`, x8.54/y80.97/z77.63; goal sensor x6.29/y80.92/z77.78; `UnderTheGrave_Prefab_6971` sets `Finish` | Same existing grave region; no extra region needed because both rewards need the same prior escape |
| First-race chest | Hash `16041366920820397198`, x−6/y82.5/z77.7, `Item_Hookshot`, `MiniGame_DampeRace_OpenGoalTBox` | Cannot supply its own entry tool |
| Second-race Heart Piece | Hash `5534919361313859554`, same goal position/event; `Minigame_DampeRace_TreasureBoxState` distinguishes prizes | Same pre-held Hookshot requirement, not a safer separate race |
| Windmill-side climb | Dynamic `Obj_HookShotTarget_A_01` Hash `14424380246501499337`, x−26.2/y92.1/z77.6 | Grave → windmill and `Dampes Windmill Access` event require usable Hookshot, not Song of Time |
| Outside the one-way section | Static transition Hash `1143018541481239924`, x−40.6/y99.7/z77.6, `UnderTheGrave_DampeReset` → `KakarikoWindmill_GraveYardSide` | `Kak Windmill` remains reachable normally from Kakariko; no blanket Hookshot requirement on it |

Goal-shutter force-close wiring is in native `UnderTheGrave_Prefab_6971` and `UnderTheGrave_Parts_10_Prefab_916f`.
The start/goal/forward-target facts were posted on `cs-r18` before the rule edits for Track G's physical entry/start
guard. Flow return-to-start calls exist for failure/retry, not an unconditional post-prize walking exit; they do not
invalidate Kareem's played trap. Native geometry also has a reciprocal windmill-side transition; whether it is
physically reachable from the ordinary windmill floor without the grapple climb is not established by actor
presence alone. No invented reverse edge is added.

## Fail-first evidence so far

- `CLAWSHOT_WORKERS=1 uv run pytest tests/test_r18_logic_returns.py -q --tb=short`: **10 failed, 19 passed**.
  Payloads show both race rewards supplying their own Hookshot, adult Requiem/walking arrivals admitting
  destination-supplied escape, adult Fairy/no-instrument acceptance, and checker-creditable reverse desert walking.
- After data fixes, that file plus `tests/test_softlock_warps.py`: **56 passed** (26.87 s).
- The existing vanilla all-check oracle then failed its goal: printed frontier showed grave inaccessible, no
  Hookshot, and adult dungeon checks blocked. Its explicit escape-tool bootstrap now includes Hookshot as well
  as Slingshot/keys, matching the two intentional vanilla self-locks; the standalone oracle **passed** (3.65 s).
- Logs: `E:/OOTRemake/work/r18-logic/{returns-red,returns-green,vanilla-oracle-red}.log`.

## Interim lessons and source events

Kareem's Minuet report is **played evidence**, not merely an inference: without an Ocarina the shoulder
notes did not work; with a debug Ocarina of Time the same play-back finished (2026-11-18 intake). The other
eleven lessons were traced in native data, not newly played. All twelve source checks now require
`Ocarina and (is_child or (Ocarina, 2))`, preserving existing route/age prerequisites; Malon's translated rule
already required a child Ocarina. Adult Fairy Ocarina is not usable. Existing overrides were changed in place;
the eight previously unoverridden checks live in `remake/song_lessons.toml`.

Native lesson → song grant order (each is `Dm_MelodyGet_<suffix>`, event numbers):

| Check | Lesson events | Song grant |
|---|---|---|
| Sheik at Colossus | Spilit 8, 9, 19 | 17 |
| Sheik at Temple | Shine 12, 13, 23 | 53 |
| Sheik in Crater | Fire 2, 3, 91 | 192 |
| Sheik in Forest | Forest 7, 9, 32 | 22 |
| Sheik in Ice Cavern | Water 16, 2, 14 | 29 |
| Sheik in Kakariko | Shadow 12, 13, 23 | 21 |
| Song from Impa | Zelda 27, 49, 50 | 111 |
| Song from Malon | Epona 2, 7, 3 | 11 |
| Song from Ocarina of Time | Time 83, 92, 93 | 4 |
| Song from Royal Familys Tomb | Sun child 0, 106, 107; adult 3, 145, 146 | Sun_03 34 |
| Song from Saria | Saria 135, 85, 86 | 109 |
| Song from Windmill | Storm first input 36; then 6, 9, 13 | 29 |

The shared `LearningOcarinaFollowExample` waits for Link's input. Existing Gift patches remove only its
add-song step, not the interactive lesson. Track G owns the gameplay repair.

Two persistent events are written **after** a lesson and receive the same guard:

- `Met Child Zelda`: native `DoorOfTime` Event124's after-lesson send-off, or `DoorOfTime_AreaOut`
  Event68 → Event131 after `HavePlayedEvent.Dm_MelodyGet_Zelda`. Before it, Impa stops Link and walks him back.
- `Ice Cavern End Chest Access`: `SageOfWater:IceCavern_WaterSerenade` writes `SageOfWater_GetWaterSerenade`
  and Step05/Step04 only after the Water lesson. The Iron Boots chest reward occurs before that lesson.

Likewise native `Dm_MelodyGet_Time` Event70 gives the moat Ocarina before its lesson. Neither pre-lesson reward
is newly instrument-gated. A no-instrument player still needs Track G's scene fix; logic cannot prevent
someone walking out of logic into an automatic scene. Open-mode return-kit bounds stay conservative:
the existing door/age-fill tests passed without changing their header inventory assumptions.

Fail-first lesson tests: **28 failed, 34 passed**; eleven source checks and both post-lesson events failed.
Malon already passed; Windmill failed only the adult/Fairy case. Afterward **62 passed** before removing one
tautological coverage-count test. Related existing source fixtures initially gave **9 failed, 39 passed**
because they omitted the real instrument; those fixtures now carry it without weakening their route assertions.
The lesson/story/clock/Ice/Sheik/shopkeeper/Epona set then gave **110 passed**. Existing door/age-fill/world/
token-route/warp/return tests gave **209 passed, 1 warning**. Final integrated returns + lessons + vanilla oracle:
**93 passed** (21.61 s). Native research and exact logs: `work/r18-logic/song-lessons/`; final parent proof:
`E:/OOTRemake/work/r18-logic/integrated-focused.log`.

## Whole-world one-way audit

Method and records: `E:/OOTRemake/work/r18-logic/one-way/`. No player seeds/saves read and no game launched.
The round-16 checker ran over the vanilla oracle frontiers and **120 deterministic item-accumulation orders**
without warp songs, retaining the age-specific inventory. Omitting songs exposes walking traps that an already
held indoor warp would mask. That snapshot found **114 region/age groups**, **87** persisting at full walking
inventory; it predates the final desert-leg correction and lesson guards and is not a seed acceptance sweep.
Its vanilla oracle omitted the newly required upfront Hookshot, so that oracle's early stop is not counted as
complete vanilla coverage; the corrected independent oracle passed above.

A second diagnostic enumerated every region reachable with full native inventory (**182 child / 300 adult**),
then asked for a return with warp songs withheld from every such arrival. This deliberately bypasses entry
guards only to enumerate structural return debt, not to certify an actual unsafe entry. It found **120**
structural region/age groups. Union with the transient-frontier findings is **147**; all are already in the
round-16 ledger's **161** groups. The fourteen prior-only groups (adult Dodongo ledges/lobby, the Shadow main/
boat/boss route and child final Wasteland leg) remain in the questions below rather than disappearing because
the new warp guards prevent a songless natural arrival. Ordinary no-exit proxy regions are not silently ignored.

One additional **proved policy consequence** was fixed: the first Colossus walking guard was too late.
`Wasteland Near Crate -> Wasteland Near Colossus = True`, while the reverse needs the unverified
`logic_reverse_wasteland` trick. Guarding only Near Colossus → Colossus stranded the final desert leg.
Fail-first test: **2 failed**, printing the songless reached tail at both ages. The guard now sits before
Near Crate → Near Colossus, native onward access stays free, and the certificate includes the final leg.
This follows Kareem's reverse-desert ruling, not invented traversal evidence. All four safe songs are tested.

Slingshot Room remains conservatively guarded. Kareem/ZFG's bridge-trigger bypass is a movement trick,
not a logic relaxation in this track. No further physical return edge is proved by a missing graph edge or a
door actor's presence alone. The following is the **complete residual ledger**, grouped by shared question.
Braced lists expand the common region prefix; ages are explicit. None blocks these evidenced logic fixes.

### Unresolved region questions

- **Bottom of the Well (child): which ordinary doors/ladders return Main Area, Behind Fake Walls,
  Behind Locked Doors and Left Side to the entrance after a drop?** Native key/door presence does not establish
  back-side opening; no broad Lens/key entry union is invented.
- **Crater: can child climb out from `DMC Ladder Area Nearby` or either-age `DMC Pierre Platform`, and can adult
  leave `DMC Central Nearby` without Tunic after arriving from Central Local?** Child Central Local/Nearby
  warp arrivals are already guarded by round 17; ladder/Pierre drops are separate unresolved entries.
- **Dodongo (both ages): what reopens the return from `Dodongos Cavern {Lower Right Side, Torch Room}` and the
  eye/bridge route `{Before Upper Lizalfos, Climb, Staircase Room, Bomb Bag Ledge, Upper Lizalfos, Lobby}`?
  Adult `Far Bridge` is also retained from round 16.** Frontier rescues include adult Bow and child Bombchus;
  this does not prove those tools are physically mandatory before entry rather than a missing return edge.
- **Fire (adult): can the player backtrack from `Fire Temple {Near Boss, Big Lava Room, Elevator Room,
  Boulder Maze Lower, Boulder Maze Upper, Narrow Path Room, Flame Maze, Upper, Lower Locked Door, Before Boss}`?
  Does the upper drop require Hammer to leave, and does the boss antechamber really need the boss key to escape?**
  The current graph can certify some returns only through boss completion; native back-side door mapping remains open.
- **Forest (adult): what are the physical return routes from `Forest Temple {Central Area, Block Push Room,
  Bow Region, Frozen Eye Switch Room, Falling Room, NE Outdoors, NW Outdoors, NW Outdoors Freestandings,
  Outdoors High Balconies, Outside Upper Ledge, Straightened Hall, Basement, Before Boss}`?**
  Many remain graph islands even with every tool, so guarding all of them on later dungeon rewards would be an
  unsupported overrestriction. Basement/boss-key and courtyard/drop paths need distinct evidence.
- **Fortress: can adult return from `GF Roof Gold Skulltula`, and do `Hideout Kitchen Pots` and either-age
  `GF Above Jail Child Locations` describe physical rooms or collection-only proxies?** Above-jail child PoH is
  absent in the remake; a proxy's missing exit is not itself a player trap. No borrowed save-warp edge is added.
- **Training Ground (adult): which native return doors connect `Gerudo Training Ground {Boulder Room,
  Heavy Block Room, Like Like Room, Central Maze Right, Eye Statue Upper, Eye Statue Lower, Hammer Room,
  Lava Room Front, Lava Room Back, Water Room, Underwater}` back to Lobby?** Heavy-block/eye/drop identity
  and maze back-side locks remain unresolved; existing conservative reward gates are preserved.
- **Goron City (child): is `GC Spinning Pot` only a remote collection proxy, or an entered space with a return?**
  No physical trapped player is established by the reward subregion having no exits.
- **Hyrule Castle (child): is `HC Garden Skippable Locations` purely the lesson/send-off proxy?**
  Its story event is now instrument-gated; a physical return to Field is the send-off, not a free graph reverse.
- **Ice (adult): are `Ice Cavern {Spinning Scythe Room, Behind Ice Walls, Map Room, End}` backtrackable through
  already melted walls, or do return paths consume another Blue Fire?** The graph relies on onward progress
  and, at End, an adult jump/slash condition. Persistent melting and actual room boundaries need evidence.
- **Ganon's Castle (adult): which return doors connect `Ganons Castle Main`, all six named Trial/Ending
  regions, Forest Trial Wind Room, Light Trial Boulder Room, Shadow Trial First Gap/Second Gap,
  Spirit Trial Second Room Front/Back, Deku Scrubs, Tower and Tower Below Boss?**
  These are graph-wide ordinary-return debt, not twenty separate proved player traps.
- **Ganondorf Boss Room: can a player leave or warp after the fight starts without the fight's damage/stun
  tools?** Native `InsideGanonCastle_Level_Room_26_Prefab_48f0` forwards `Defeat_Ganon` Step05 to
  `Enemy_DungeonBoss_Ganondorf_Prefab_f52a`: the downstairs door's lock tracks battle creation and the boss
  chain-lock module also has `LockPlusZ=True`. This is positive lock evidence, but active-boss warp permission,
  exact stun/damage alternatives and which side of the boundary our region denotes are not proved.
- **Jabu (child): what returns `Jabu Jabus Belly {Main, Depths, Past Big Octo}` after their drops?**
  Main's graph can require Boomerang to escape; Depths/Past Big Octo remain structural islands. Prior guide
  evidence describes an upper Skulltula ledge, not the entire folded Depths region.
- **Kakariko (both ages): is `Kak Impas House Near Cow` only a remote-collection proxy?**
  Neither incoming house-side collection rule establishes an actual one-way player crossing.
- **Market: are either-age `Beyond Door of Time Skippable Locations` and child `Market Mask Shop Storefront`
  collection/story proxies rather than physical rooms?** Their zero-exit structure alone cannot justify a new gate.
- **Shadow (adult): can the boat be ridden back, and which physical drops need tools to return from
  `Shadow Temple {Beginning, First Beamos, Huge Pit, Invisible Spikes, Falling Spikes, Wind Tunnel, After Wind,
  Boat, Beyond Boat, Before Boss, Beyond Boat Scarecrow, Beyond Boat SoT Block, 3 Spinning Pots Rupees}`?**
  The forward bombed-pillar crossing is documented; return-bell and back-side boss-door behavior are not.
- **Spirit (adult): which native returns connect `Early Adult Spirit Temple`, `Adult Spirit Temple Climb`,
  `Child Spirit Before Locked Door`, `Child Spirit Temple Climb`, `Spirit Temple {Lobby, Central Chamber,
  Anubis Room, Beyond Anubis Room, Big Mirror Room, Boulder Room, Before Boss}`, Twinrova Boss Room and
  Twinrova Blue Warp? Child: `Child Spirit {Before Locked Door, Temple Beyond Metal Bridges, Temple Climb}`,
  `Spirit Temple {Lobby, Central Chamber}`?** Colossus/Hands/From Spirit Lobby/fountain/grotto arrivals inherit
  the proved pre-held escape-song invariant; internal dungeon backtracking remains separate graph debt.
- **Water (adult): which routes leave `Water Temple {Lowered Water Levels, Middle Water Level, Dive,
  Central Bow Target, Cracked Wall, Dark Link Region, Dragon Statue, East Geyser Room, Falling Platform Room,
  North Basement, South Basement, River, Boss Key Chest Room, Before Boss}` after drops and water changes?**
  River's native Longshot targets support the existing exit requirement; they do not prove every alternate
  reverse route or that the region's entry lacked a safe ledge. Do not infer whole-dungeon entry restrictions.
- **Zora Domain (child): is `Deliver Rutos Letter Region` only a story-effect proxy?**
  It has no physical-room identity; missing return cannot prove a player trap.
- **Zora Fountain (adult): can `ZF Hidden Cave` and `ZF Underwater` return with the already-required entry
  equipment, and are their graph regions just collection reach?** Boots/tunic/gauntlets/Lens are already
  entry prerequisites; actor positions alone do not prove or disprove surfacing/backtracking.
- **Windmill reciprocal transition:** can an unequipped adult reach the upper windmill → grave transition
  from the ordinary windmill floor? Track G received both transition hashes; no reverse edge or ordinary
  windmill Hookshot gate is invented.

Questions posted to `cs-r18` with this round file as the full ledger. No other new walking return is asserted,
and no whole-physical-world softlock-free claim is made. The required seed sweep separately checks every
inventory sphere with the production certificate and retains raw whole-world diagnostics for review.

## Verification and handoff

All four logic items are implemented with fail-first proof; native boundary handoff and complete residual
question ledger are above. Remaining acceptance: rebase onto main's Track C fill fix, locked 200 broad + 50
Defaults + 50 Recommended sweep, then current-main rebase/focused proof and one exact-head full gate.
The broad recipe is the unmodified CS1 in `work/r18-fill/settings.txt` (`dungeon_items=all_anywhere`).
Canonical `make_seed` preparation is captured immediately before `generate`, including native Gift expansion,
chest identity/event restrictions and floor palettes; sweep workers then run that actual prepared generator.
No generated mod, player seed or save is read/written. Logs/receipts are external under `work/r18-logic/`.
No new working-set resource is needed: this track changes logic and synthetic tests only.
No READY claim yet; final handoff requires every receipt to pass. No separate play-held behavior patch is in scope.
