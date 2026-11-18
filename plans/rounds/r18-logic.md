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
## Verification and handoff

Pending fail-first regressions, exact native region facts, complete one-way audit, required 200 broad + 50 Defaults + 50 Recommended locked sweep, current-main rebase and one full gate. No READY claim yet.
