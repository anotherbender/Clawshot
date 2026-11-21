# Round 20 — open Fountain / Kakariko gate (cs20e)

Agent/model: `cs20e`, `openai-codex/gpt-6.1-sol`; branch `r20/open`.
Baseline: `acbb903df111bb30609baedac35316b22d43700e` (0.2.4 plus PR #36).

**Research-only handoff; no product changes, settings, logic relaxation, seeds or staged game packet.**
Implementation remains held on the explicit consumer/behavior questions below. Nothing here is a played claim.

## Scope and ownership

Research King Zora's moved state (adult only or both ages), the child Death Mountain Trail guard/gate,
and every other consumer of their saved quest state before selecting initial values. Do not set an entire
quest Complete merely to open an entrance. D39 is the precedent for shared quest-step side effects.

- Read the supplied repository rules, README, CONTRIBUTING, roadmap, round-20 overview, architecture,
  orchestration, game-data/world-format specifications, decisions, relevant round-19 audit/scenes records,
  round-14 step audit, and the round-20 public-docs feature comparison.
- Facts-only GPL lead: external `work/refs/sloperina-FINDINGS.md`, section 1 (GameData/saves), 5.7 (upgrades),
  5.8 (maps/compasses); no implementation copied. Native AINB decoding is the prior unmodified decoder's
  external research output, not code imported into Clawshot. No OoTR/SoH/ootrr source or diff opened.
- cs20c owns `patch/start_items.py` and the initial-values part of `patch/gamedata.py`. Their thread contract:
  append `gamedata.FastStartSetting(name, default=False, skips, state, source, logic=None,
  game_data={existing_field: typed_value}, flow_edits=())` to `chosen` before its single `gamedata.changes`
  composition. It checks existing type/reset/enum/conflict contracts. No separate GameData writer.
- Shared additive Settings fields are allowed by Claude's ownership clarification; no fill-algorithm ownership.
  No cross-track source file has been edited.

## Native provenance and inventory

All research artifacts are outside the repository under `E:/OOTRemake/work/r20-open/`.
The full earlier native census is `work/r14-steps/` (build `e0f3ccfa`); this round rechecked the selected inputs
against the current read-only supported dump rather than accepting an earlier narrative as proof.

| Saved Enum | Field hash | Native default | Reset / save index | Dependent BoolExps | AINB read occurrences | EVFL reads | BYML/resource reads | Participant dispatch reads |
|---|---|---|---|---|---|---|---|---|
| `Step_Get_StoneOfFire` | `268612710` | `NotReady` | 8 / 0 | 22 | 71 | 79 | 64 | 21 |
| `Step_Get_StoneOfWater` | `1539965606` | `NotReady` | 8 / 0 | 20 | 57 | 37 | 24 | 23 |

Counts are census occurrences, not distinct gameplay gates; module propagation, opposite actor pins,
packed copies and unused outputs are retained. Both enums are shared saved quest progress, not age-specific flags.
The selected inventories also retain Fire's 18 EVFL + 2 AINB write/action rows and 8 configuration references,
and Water's 19 EVFL + 2 AINB write/action rows and 21 configuration references.

Observed read-only checks (no pytest/gates/seed generation):

- `uv run python E:/OOTRemake/work/r20-open/probe_state.py`: passed. Native GameDataList and Challenge
  SHA-256 exactly match the cached census; complete selected expression closure equals the earlier closure.
  Receipt: `native-state-proof.json`; full selected rows: `Get_StoneOfFire-reader-inventory.json` and
  `Get_StoneOfWater-reader-inventory.json`.
- `uv run python E:/OOTRemake/work/r20-open/verify_readers.py`: passed. All 45 selected AINB occurrences,
  including actor-pack members, match original decoded-input SHA-256. Selected native EVFL/Banc/loose schedules
  and the schedule pack match the earlier native manifest. Receipt: `reader-freshness-proof.json`.
- `uv run python E:/OOTRemake/work/r20-open/verify_resources.py`: passed. All 49 selected BYML/resource
  inputs, including packed attention, NPC schedules, shop parameters, Navi and UI metadata, match the prior
  decompressed-input SHA-256. Receipt: `resource-freshness-proof.json`.

- Native hook-contract probe (inline `uv run python`, no output file): a hypothetical
  `{'Step_Get_StoneOfFire': 'DeathMtTrailIn'}` entry passed `plan_game_data` and the composable
  `patch_initial_values` write/read-back. Only type/reset/enum/serialization was proved, not persistence,
  actor placement or gameplay. Posted explicitly as unapproved; cs20c must not integrate it on our behalf.
- `uv run python E:/OOTRemake/work/r20-open/compare_boundaries.py`: passed. The hypothetical Fire candidate
  crosses three primitive BoolExp boundaries (`Ready`, `KakarikoVillageNpc`, `KakarikoVillageLetter`),
  not Fire completion or the Darunia/dungeon thresholds. Water candidates `Step07`/`Step08`/`Step09` cross
  nine/ten/eleven earlier primitive predicates respectively. This is not whole-composite or runtime evaluation.
  Receipt: `predicate-boundaries.json`.

The original census covered all 914 EVFL files, 11,707 loose/packed AINB occurrences (5,036 distinct),
149,463 BYML resources and transitive BoolExp dependencies, with zero decode errors. It explicitly retains
unbound contexts/dead outputs and does not semantically decode every nonstructured binary. Enumeration and
freshness do not establish each reader's safe behavior under a synthetic initial state.

## Early-writer hazard already observed

`Dm_SY_BancChangeArrive:Goto_ZoraDomain` Event44/45 writes Water `Step03`/`Step03_Impa` after the first-arrival
movie according to `Get_StoneOfWater_MeetImpa`; the callback has no comparison against current Water progress.
`Get_StoneOfWater:StoneOfWater_TalkWithImpa` Event64 writes `Step01`. An advanced initial value alone does not
prove the Fountain remains open after native first visits. Current Fire monotonic patches are not Water guards.

Fire's analogous `DoorOfTime:DoorOfTime_SendOff` Event62 is already guarded by
`patch/darunia.py::_door_changes`; the native Impa/Field tail is retained. That does not prove all gate readers safe.

## Reader table and proposal

The complete occurrence table is external `reader-index.csv` (376 rows, 133 quest/layer/source groups);
`reader-source-index.json` groups it by source without dropping unused or unbound rows.
The following is the human reader ledger. "Unchanged" refers to the specified candidate boundary, not a played
guarantee. Sixteen EVFL occurrences lack a scene binding in the older joined table; these remain explicit
research limitations, not permission to initialize either quest.

| Reader family | Native evidence | Consequence / outstanding proof |
|---|---|---|
| Kakariko shutter variants | `KakarikoVillage_Child_OpenGate_Prefab_1fcc` node2 tests Fire before `DeathMtTrailIn`; `...GateClose_Prefab_6b8b` node2 tests after `KakarikoVillageLetter` | `DeathMtTrailIn` selects the alternate shutter placement. The second graph also binds BootUp to its ground-control moving output; its module name alone does not prove the physical gate open. |
| Guard's Letter phase | `RSDB/Challenge` Fire participants at exact `KakarikoVillageNpc` / `KakarikoVillageLetter`, with two packed Soldier003 schedules | The candidate skips these schedules, falling back to the common/mask schedules. Must account for optional Letter presentation, mask sale and schedule priority, not merely the shutter's predicate. |
| Other guard/Navi readers | `Npc_Hylia_Soldier_001` Event18; packed Navi `NpcKakariko002`; Field `...NaviChat_f576` node6 | Soldier001 changes dialogue after the Letter phase; Navi's after-NPC predicate crosses too. The Field OR output has no connected consumer in the census. No claim that chatter is unchanged. |
| Fire's later consumers | Goron City / DMT / Dodongo modules and Goron schedules; Market Bombchu door/bowling/stock; NPC, Fairy and get-window dialogue | Candidate remains below `DeathMtTrailNpc`, Goron room/dance/dungeon and Complete thresholds. It is not Darunia's gift, Fire clear or Bombchu access. Full occurrence/source tables retain each later comparator and configuration reference. |
| Impa / Zelda / Door / Saria shared story | `HyruleCastle_Prefab_b02d` nodes2/4; `DoorOfTime` Event38/39/56/62; `Npc_Hylia_Zelda_Child`; `Dm_SY_Ocarina_SariaSong` | The repeat Water-guide Impa uses exact Water `Ready` plus Fire `Complete`, a different actor from the first lesson/send-off. Advanced Water loses that exact-Ready branch. Fire's send-off write is already monotone, but Water's callbacks are not. Zelda/Door/Saria also retain their own step-chain readers; possession of a moved item is not story completion. |
| King Zora, child and adult collision | child utility node2/10/11 and adult utility node54/55/53 in the King Zora actor packs | Both test Water after `Step06` together with `Npc_Zora_KingZora_child_EnableClothCollidable`, switching cloth floor/wall branches. `Step07` crosses this predicate at both ages; it is not an adult-only flag or, by itself, proof of the moved anchor. |
| King Zora schedules / attention | Water's exact-step King child participant schedules, adult `SageOfWater` schedules, packed King attention clients | Early child schedules are replaced by Step07's family, and lock-on/talk predicates also change. Adult thaw/tunic/Prescription belongs to the separate Sage/trade chains; do not initialize their completion to open a passage. Movement/anchor and cold adult state remain separate proof obligations. |
| Letter acquisition and use | `Get_StoneOfWater` Event289/290; `Dm_SY_LetterBottle` Event12 | At hypothetical Step07, acquiring the Letter can write `Step05_01` (Event22), and using it can write `Step06` (Event56); both are backwards writes. The bottle scene takes another branch after Step05_01. A new default alone does not preserve the skipped phase or define an empty-bottle policy. |
| Diving / Zora NPCs / River | Water Event293/471; `ZoraDomain_Child_Prefab_ab5e` node5; Zora schedules; `ZoraRiver_Common_08f0` | Diving callbacks can write Step05; Zora004's entrance position/flag changes across Step04; River walls disappear at or after Step03 even with unbroken rocks. Opening the Fountain by shared progress also opens the Field-side River passage. |
| Jabu / Ruto / Barinade | packed Jabu AI, Fountain41c4, Jabu room00/02/05/06/07/15 and prefab0b28, Ruto attention/saved-spawn configuration, boss module; Water Event217 | Later progress drives Jabu/Ruto source and room state, boss doorway/spawn and completion. Step07 is not a substitute for these later steps; do not preset Step09+ or Complete to get a convenient king/entry state. |
| Other Water dialogue / UI / dispatch | Hylia/Zora talk flows, `GetPouchContent` Event41, Challenge menu/Navi metadata, all 23 participant dispatch occurrences | Fire-Stone get text checks Water Complete; candidate Step07 leaves that false. Dialogue, exact schedules, UI references and preload metadata remain in the source index rather than being misreported as independent opening flags. |

**Proposal (cs20e): research-only handoff; keep every shipped setting/default and the public
non-default-logic refusal unchanged.** Neither a shared Water Enum nor the gate's Fire Enum is a demonstrated
standalone opening flag. The Water rewinds are concrete native branch evidence; no in-game failure is invented.

**Product question for maintainers:** may an open-Fountain mode also skip the child Letter/Impa guide phases
and open the River's Field barrier, or must those remain independent? An adult-only value cannot be selected
from a shared Enum merely by naming the setting "adult". A separate age-specific consumer design needs review.

**Product question for maintainers:** may open-gate skip the guard's exact Letter-phase schedules and alter its
Navi/other-guard chatter, provided Zelda's actual Letter, Impa send-off, mask quest and Darunia stay native?
Do not choose the answer by silently changing additional quest defaults.

## Logic boundary (not changed)

Current native validation refuses unpaired non-default `open_kakariko` and `zora_fountain` logic overrides.
The translated model already has these prospective abstractions; their existence is not native evidence:

| Proposed mode | Model change needed after native proof | Invariants to retain |
|---|---|---|
| Fountain closed (default) | Keep today's `zora_fountain='closed'` behavior | Child Letter delivery, diving reward, fish/Jabu and adult access remain native |
| Fountain adult only | `zora_fountain='adult'` on both Domain/behind-King edges | Child Letter delivery remains required; no automatic thaw, tunic, trade or Water Temple clear |
| Fountain both ages | `zora_fountain='open'` on both Domain/behind-King edges | Opening the passage is not completing Jabu, granting Sapphire, consuming Letter or granting a bottle |
| Kakariko gate closed (default) | Keep today's `open_kakariko='closed'` behavior | Zelda/Letter/Impa/clock and vanilla guard sequence unchanged |
| Kakariko gate open | `open_kakariko='open'`; the existing Root event and both behind-gate edges support it | Do not mark Fire complete, grant Zelda's Letter, open Darunia's room or bypass his source |

The translated files remain generated data; any eventual additional corrections belong in sourced remake
overrides. Public Settings/allowlist/CS1/app wiring must follow the native implementation, never precede it.

## Disposition and implementation prerequisites

No product code, setting schema, validation allowlist, logic, fill, location, destination, resource manifest or
version changed. No initial values were appended to production `chosen`; no cs20c-owned file was edited.
The existing hook's constructor shape is resolved, but a safe consumer contract is not.

No seed or mod was generated; no natural or edited save was opened for this track; no launcher or game
was started. There is **no staged packet to ask Kareem to play**, and no new in-game observation.
Existing played River-wall evidence is attributed to round 14, not to this investigation.

Per the explicit research-only rule, no Ruff/full pytest/dump gate, gate-lock acquisition, or seed sweep was run.
The read-only probes above are the observed checks. A sweep cannot authorize an unproved native trigger chain.

Implementation remains conditional on:

1. A reviewed per-mode contract for the coupled readers in the table, including Letter/bottle and optional
   guard/mask behavior; default closed/off and all unsupported values refused until their native arm exists.
2. The King's actual start-anchor/rail/placement selection at each age, not only the cloth predicate.
   Adult-only access must not alter the child's shared quest progress. Do not thaw the Domain, grant the tunic
   or clear Water Temple just to move the adult obstacle.
3. A complete Water monotonic-writer design preserving native continuations, source rewards and later Jabu/Ruto
   progression. First arrival, Letter pickup/use, diving and Impa are separate callbacks, not one generic skip.
   Gate's fallback/quest/mask schedule priority and repeat show-Letter behavior also need a full consumer proof.
4. Production mode wiring through cs20c's single initial-values hook, not a second GameData patcher.
   Apply only the approved entries before `gamedata.changes(chosen)`; preserve other tracks' additive settings.
5. Focused/native production-path proof, including exact-step events and wrong/refused inputs, then the round's
   gated 200 broad + 50 Defaults + 50 Recommended sweep for each enabled mode, zero exhausted seeds.
   Rebase to the current local main and rerun focused checks before that full gate.
6. Private-seed candidate/control packets built from the same recipe, control from main, using the current
   template and **Longshot 3.0.0** only. Cover initial approach, both directions, each relevant age, native
   Letter/diving/guard/Impa continuations, delayed completion, re-entry and Save/Continue; record actual
   resource-load lines and in-game results. Do not use a successful model sweep as a substitute.

Proposed by cs20e; no product decision is attributed to Kareem or Claude. The bold questions above are queued
on `cs-r20` and require no overnight action. Research-only was explicitly allowed in the track brief.

## Handoff

This branch contributes only this research record. The full occurrence index, provenance receipts and
reproducers stay under `E:/OOTRemake/work/r20-open/`; no game data is committed.
The reader inventory is complete within the documented native census, but consumer safety is **not** certified:
unbound contexts, exact-step schedule priority and King's start-anchor behavior remain stated limits.
That is why no mode was exposed, no logic was loosened, and no initial value was submitted for production.

Checks completed: native Enum/reset/save metadata and BoolExp closure; selected EVFL/AINB/BYML input hashes;
candidate hook type/reset/enum/write-read-back; primitive predicate crossings; complete read/source indexing.
No full suites, sweeps, boot checks or game checks were run. No browser tool, Chrome session or screenshot used.
The commit/head and these limits are reported on `cs-r20`; maintainers may merge the evidence independently
of any future play-held implementation.
