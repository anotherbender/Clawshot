# Round 18, Track E — rewards and bridge (cs18e)

Branch `r18/rewards`, base `2ba2f9a`; model `openai-codex/gpt-6.1-sol`.
Research and staged output: `E:/OOTRemake/work/r18-rewards/`. Dump read-only.
No game started; backups are read-only, and no current player seed or original save is modified. All behavior remains unplayed.

## Reader table — posted before implementation

Kareem's 2026-11-18 decisions: default-off shuffle among the nine reward slots,
including Rauru; bridge default vanilla or an N-of-stones/medallions/rewards gate;
Light Arrows remain necessary inside; Master Sword shuffle is design only.

This separates reward ownership, boss death, blue-warp use and completed story scenes.
Evidence: supported native build `e0f3ccfa`, all event flows and Logic/Sequence string
references scanned read-only on 2026-11-18, plus the exact node traces in
`r17-dungeon-items.md` sections 3–4. A string scan is not a claim to have exhaustively
disassembled native code. Native inventory/menu consumers still need that audit.

| Reader / exact site | Actual state checked | Contract for this build |
|---|---|---|
| Inventory/get windows, reward pouch actors | Nine separate `PouchData.Item_Stone_*.StockNum` / `Item_Medal_*` and `IsGet.*`; ordinary nonconsumable KeyItems | Follow the shuffled reward; never grant the displaced vanilla reward as well. |
| Door stone counter `DoorOfTime/Event38,39,56` | Fire/Water stone **quest completion**, not owned stones; `DoorOfTime_GetStoneCount` counts remaining quests | Preserve completion for escape/moat ordering. This counter is not the shuffled closed Door's eligibility reader. |
| Closed Door opening `DoorOfTime/Event60` and altar reaction | Native quest-stage gate plus opened/melody/history guards | With shuffled rewards, require three owned stones, Time ocarina, learned Time song and real send-off. Retain native scene/once latch; never complete a stone quest by finding its reward. With vanilla rewards, main-exact. Open/song-only retain #32. |
| Blue warps: `Dm_SY_BancChange_EscapeDungeon` | Child/adult quest completion, first-clear routing; adult completion writes Event199/40/41/73/141 | Stay completion-driven. Boss kill, heart pickup, warp and reward grant are distinct operations. |
| Sage count: EscapeDungeon Event249/251/252/253/267 | `AllSage_AwakeSageCount -= 1` after sage routes | Stay completed-sage count, not owned medal count. |
| Prelude/return pedestal: `Market_Adult_Prefab_edc2`, `_89da` | `SageOfForest_IsCompleted_Exp` | Stay Forest completion; free-time-travel remains separate. Forest medal ownership does not unlock Prelude or pretend Phantom Ganon died. |
| Light Arrows readiness: `AllSage/Event25,26` via EscapeDungeon Event130/139 | BOTH `HavePlayedEvent.Dm_Awake_Spirit` and `.Dm_Awake_Shadow`; Event20 writes AllSage Step02 | Stay native scene completion. Finding Shadow/Spirit medals alone does not summon Zelda. |
| Temple Light Arrows trigger: `Market_Adult_Prefab_c668` node2 | AllSage exactly Step02; contact requests `Market_Adult_Field_GetArrowLight` | Stay native; actual grant is `Dm_TimeTemple_0130/Event85`. AllSage Event10 completes its quest, Event11 advances Defeat_Ganon Step01. |
| Vanilla bridge: `GanonCastle_Level_Field_00_Prefab_14ba` nodes3/4 | Defeat_Ganon Ready-to-Step01 interval (Step01 after Light Arrow story), not medals | Default stays native. Configurable mode replaces eligibility only with unique reward ownership. |
| Persistent bridge: same module nodes8/10 | Rainbow event history OR its EX1; rainbow flow Event1 writes Defeat_Ganon Step02 | Preserve real bridge scene/latch/reload; early bridge must neither suppress nor regress late Light Arrow story. |
| Six trial cores: `Gimmick_ArrowLight_BarrierRemove_*`, native `ActorLogicInsideGanonCastleCore` | Light-Arrow core interaction; each native clear writes its own removal Bool and decrements Barrier_Count | Stay native. Bridge never grants arrows, clears a trial or changes this count. Native core damage predicate requires independent verification beyond its name. |
| Tower: `InsideGanonCastle_Common_e780`, room1 `_4ab0`, `_75af`; `Defeat_Ganon/Event606,778` | Six trial-removal Bools, Barrier_Count≤0, all-barrier-clear and final scene history | Stay trial completion. Boss key ownership is independent. |
| World restoration / room retirement: Deku, Fire, Water and overworld modules | `Get_StoneOf*_IsCompleted_Exp` / `SageOf*_IsCompleted_Exp`, not reward stock | Stay completion-driven: forest restoration, lake/Domain state, Gorons and cleared dungeon actors must not follow the shuffled reward. |
| Shop availability: `DisplayShop/Event327,372,526`, Bowling Event137, native Market/Bowling modules | Fire stone quest completion | Stay completion-driven, including bombchu/bomb stock and minigame availability. |
| Fishing Event836/204/32/322, Bonooru Event31, Zora NPCs | Water sage completion | Stay restoration/dialogue-driven, not Water Medallion ownership. |
| `Dm_SY_BancChangeArrive`, `Dm_SY_BancChangeGo`, `Dm_MelodyGet_Shine`, `Dm_SY_Ocarina_SariaSong`, NPC dialogue / Navi | Corresponding stone/sage quest completion | Stay completion-driven; do not retarget story/dialogue to reward actors. Track G owns its song flows. |
| Gerudo captain/carpenters/card | Four rescues and native captain scene; Spirit Step02, not Spirit medal or card stock | Preserve D39 and every rescue/guard state; reward shuffle does not write them. |
| Reward cutscene models, Ruto display, Zelda Notes requests | Fixed source scene actors/instances; separate from grant | Review presentation separately. Native sage/story scene remains; actual get window and acquisition must name the shuffled reward honestly. |

**Initial acceptance, 2026-11-18 (superseded for the closed Door):** Claude kept all
completion readers native pending Kareem's morning ownership decision.

**Kareem's decision, relayed by Claude 2026-11-19:** with reward shuffle on, the
closed Door needs the three **owned** shuffled Spiritual Stones plus the existing
Ocarina of Time, learned Song of Time and real send-off. Track E owns the Door flow.
The former open question is resolved. Other completion readers, including LACS
awakenings, restoration, Prelude and escape/moat, stay completion-driven. Preserve
every round16 #32 behavior; reward-vanilla output stays main-exact.
### Bridge / Light Arrows dispute

Native data does **not** check Shadow+Spirit medallion ownership to start Light Arrows.
It checks the two awakening-scene histories. The subsequent Temple story advances
Defeat_Ganon Step01, enabling the bridge approach event; that event's history creates
the durable bridge. Replacing the medallion grants alone changes neither trigger.
Neither `AllSage_AwakeSageCount` nor the six-trial barrier count is a reward counter.
These are data findings, not played confirmation and not a claim about another
randomizer's patched behavior.

### Native trial-core evidence, beyond the module name

The six `Obj_InsideGanonCastle_Core_{A..F}_01.pack.zs` packs carry the same
`Life/DamageParameters/Obj_InsideGanonCastle_Core_A_01.game__life__DamageParameters.bgyml`.
Its external damage exception selects element **Light** (murmur3 key `3346875365`);
its embedded design rationale specifies destruction by Light Arrows only.
`NormalArrow.pack.zs`, `GameBalance/AttackParam/NormalArrow.game__gamebalance__AttackParam.bgyml`,
has a distinct Light-element attack variant; ordinary arrows have no damage element.
Thus this requirement is supported by actual core and projectile data, not merely
the `Gimmick_ArrowLight_*` wrapper's name. The six native core-clear/count writers
are untouched by both new options. This is static evidence, not a played core test.

### Working-set addition

The existing round16 layered fixture lacks the bridge module and nine reward actor
packs now referenced by the actor catalogue. Created the track's own fixture at
`E:/OOTRemake/work/rounds/r18/rewards-layered-dump`, copied from that fixture and
extended read-only from the supported dump with **ten missing resources**: the
bridge module and `Item_Stone_{Forest,Fire,Water}` /
`Item_Medal_{Forest,Fire,Water,Shadow,Spirit,Light}` packs. The production working-set
manifest explicitly includes the module; actor packs are derived from the catalogue.
All 1285 required inputs exist in this private fixture. The locked dump gate will
use it as OOT_DUMP, keeping the shared round16 fixture unchanged.

## Work status

Reward/bridge and owned-stone Door implementations and isolated controls are built.
Rebased MAIN FINAL focus and the aimed lesson integration fix are verified below.
**READY** — tested head `3a33864d0eeca8c1a490dfaa25d17dd51bf9cf9c`, rebased onto merged F+G `8fadebf`. Counting **300/300, zero exhausted**; one full format/lint/synthetic/dump gate passes (**3768 passed/489 skipped**, **486 dump passed**). E token lock released. Door v2 positive played PASS; two-Stone refusal and other unplayed coverage remain play-held.

## Implementation and observed focused proof

- `data/dungeon_rewards.toml` identifies the nine stable flow/event slots and their
  ordinary pouch actors. Active adult `.110` files and their base copies are patched.
  Only the grant's ActorName and Zelda Notes acquisition TargetID change. Source
  cutscene actor bindings/animations remain native emblems; get window/inventory name
  the shuffled reward. Ruto's earlier Sapphire display remains a display, not a grant.
- `generate/rewards.py` composes data-only completion rules when either feature is
  enabled. Reward locations are a closed `DungeonReward` palette in both directions;
  advanced item/type restrictions cannot release rewards or admit ordinary items there.
  The explicit bridge uses unique ownership built-ins, not completion counts.
- Historical construction fix before the 2026-11-19 Door decision: the completion-gated
  closed-door adult-return bound forgot mandatory child completions. Printed search
  values identified the missing events; adding them made the aimed rebuild pass.
  The ownership decision supersedes that reward-on minimum: it now carries only
  the three necessarily owned stones, not assumed child completions. Vanilla-reward
  completion-based preparation and every early-door kit remain unchanged.
- Native seed `180501`, reward shuffle on, default other options: nine-slot
  permutation generated, beatability **27 spheres**, **118 written resources**.
  This is the track's own output, not a player seed. No play claim.
- Focused synthetic `CLAWSHOT_WORKERS=1 uv run pytest tests/test_dungeon_rewards.py
  -m 'not dump' -q`: **15 passed, 1 deselected** before the added return-bound
  regression. Native `OOT_ROMFS=E:/Games/Hookshot/romfs ... -m dump -q`:
  **1 passed, 15 deselected**, inverse comparison of all fourteen grant files.
  Final focused coverage will include the new regression and bridge tests.
- Browser smoke, isolated empty library, actual Settings page: reward toggle On
  changed the settings string; stones count 4 displayed the explicit 0–3 refusal;
  count 3 applied. Both rows/help rendered in a screenshot. No personal seed library,
  game or generated output was opened. Twelve staged launchers dry-ran with exit0;
  the runtime was not started. The throwaway UI server/script were removed.

## Isolated played-check staging (not played)

Base: `E:/OOTRemake/work/r18-rewards/ingame/`. Each launcher has its own isolated
profile, containing exactly the chosen original slot plus its account/options.
Input `progress.sav` bytes were hash-compared after copying; no flags, inventory,
quest stages, position, age or equipment were edited.

`scan_saves.py` read **2487 archived slots**, with zero parse errors. It preferred
chronologically earliest natural-name candidates, excluding known test/debug/crash
backups; selected three old natural-run snapshots, never the current seed.
Initial lookup printed absent Slingshot data because its canonical name is
`Weapon_Range_SlingShot`, not `Item_Range_SlingShot`; corrected the query before
selection. All selection/rejection values remain in external `save-survey.json`.

| Stage | Selected original path below `E:/OOTRemake/work/save-backups/` | Original file date | Required input predicates observed |
|---|---|---|---|
| First pull | `2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001/slot_02` | 2026-11-09 10:22:06.376 | Childhood=true; Door=Step06; Master Sword=false; Light medal=false; Rauru history=false; all three child quests Complete; AllSage/Defeat_Ganon Ready. |
| One-medallion bridge boundary | `2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001/slot_01` | 2026-11-09 10:22:06.359 | Childhood=false; Master Sword=true; exactly Light medal owned; five other medals=false; Light Arrows=false; rainbow history=false; Shadow/Spirit awakening histories=false; AllSage Step01; Defeat_Ganon Ready. |
| Forest pre-warp | `2026-11-09_1347-main-after-forest/save/5a3c9e1f0b7d24680000000000000001/slot_03` | 2026-11-09 13:47:30.883 | Childhood=false; Forest quest Step09; Forest awakening=false; Forest/Shadow medals=false; Light medal=true; Master Sword/Bow/Hookshot=true; rainbow/Shadow/Spirit histories=false; Light Arrows=false; Defeat_Ganon Ready. |

No natural **child warp-ready** or **both-last-sages-completed but pre-LACS/bridge**
snapshot matched the predicates; those controls are **dropped**, not fabricated.
Earlier child saves stop at DungeonStart, not a ready blue warp. The late story-order
case remains a static/synthetic proof and must not be reported as played.

Candidate packets `r18-rewards-medals-{1,2}-candidate` each have eighteen resources:
fourteen reward files, AllSage, GameDataList, the bridge module and size table.
They are patch-only diagnostics, not full shuffled seeds. Rauru gives Fire Medallion;
Forest gives Shadow Medallion. Both are absent in their selected input profiles.
All nine assignments form a permutation; nothing outside the reward/bridge features
is changed. Main controls were separately built using the actual main
`clawshot.patch.write` at **2ba2f9a**, with the same native source packet/profile but
without this feature: seventeen native resources, byte-identical decompressed inputs.
Control digest: `2626b64c0e721f5f845cc254a30d4eabc0f99411d83f23d8a5b20768bd9cd3a8`.
Exact candidate digests and paths are in external `stage-proof.json`.

### PRIMARY checklist — candidate unknowns only, at most 20 minutes

Current play instructions:
`E:/OOTRemake/work/r18-rewards/CHECKLIST.md`.
Three short numbered checks use two existing candidate launchers: Rauru grants
Fire without Light and persists; that newly acquired Fire is below the two-medal
bridge threshold; the separate Light-only natural profile meets threshold one
before the late story. Estimated 11–18 minutes, unmeasured, hard stop at 20.
Runtime overlay lines and actual inventory/result are required, not scene models.

Claude's play-time steer drops every control and vanilla-equivalent observation
from the current request. No vanilla first pull, Door D1/D2, trials or clock
detour. Forest's changed reward/completion reader remains a separate unknown,
not an extra hidden 8–15 minutes in PRIMARY. No rebuild, save edit or launcher
change; original staging provenance above remains historical evidence.

## Frozen implementation checks and design handoff

- Final focused synthetic command:
  `CLAWSHOT_WORKERS=1 uv run pytest tests/test_dungeon_rewards.py
  tests/test_reward_bridge.py tests/test_app_schema.py tests/test_settings_native_logic.py
  -m 'not dump' -q` → **837 passed, 7 deselected, 231.08 s**.
- Native reward/bridge command:
  `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest
  tests/test_dungeon_rewards.py tests/test_reward_bridge.py -m dump -q`
  → **7 passed, 31 deselected, 18.26 s**.
- The bridge oracle executes every 512-reward ownership subset against every valid
  threshold, checks completion-without-ownership refusal and duplicates, and executes
  the emitted AllSage guard through every native Defeat_Ganon step. Native inverse
  tests preserve source events, save layout and the bridge module outside its one
  input string slot. These are offline proofs, not native played results.
- Scoped Ruff initially printed one unused test-loop value; removed the unused
  binding. Also applied Ruff's exact whitespace recommendations through anchored edits.
  Scoped format and lint then passed on all ten changed Python files.
- [Master Sword shuffle design](r18-master-sword-design.md) is **design only**:
  no setting, placement source, item or runtime transform was added for it. It maps
  first-pull grants, era defaults/restores, pose equips, the proposed swordless
  capability deltas and finale admission. A solver-only Master Sword win requirement
  would still allow a native forced equip/re-grant: the design therefore requires a
  real pre-fight ownership admission guard, not fake ownership or a hidden free sword.
  The 25 lost checks are a hypothetical maximal graph comparison, not played remake
  combat facts or a generated seed.
- **Master Sword product question for Kareem:** keep the existing fill-side
  child-return guarantee with an adult-reachable sword, or explicitly require the
  existing free-time-travel option? This design recommends no silent free-travel
  change. Posted to the round thread; nothing needs an overnight answer.

The required sweep will enable reward shuffle **and** a count bridge throughout:
200 broad-recipe seeds (including the two reported fill failures after the fix),
50 Defaults and 50 Recommended. Count modes rotate through stones3, medallions6 and
rewards9. Preparation uses the real native gift/floor/shop/chest policy and pool,
then the production fill and beatability oracle. No safety restriction is removed.
External receipts: `E:/OOTRemake/work/r18-rewards/sweep-results.json` and
`sweep-rows.jsonl`. They will identify the actual tested head and exhausted counts.

## Revised gate order — Claude, 2026-11-19

- Automatic main-change watcher cancelled; its obsolete external script removed.
- Main advancing is **not** authorization to rebase or acquire `gate.lock`.
- Wait for Claude's explicit **MAIN FINAL** thread post after A and D merge, then
  rebase onto that main, rerun focused checks and follow the assigned lock order
  for the required sweep and one full gate. Until then, non-lock work only.
- Existing receipts and staged controls describe their recorded heads, not the
  future MAIN FINAL. Sweep, full gate and READY remain pending; no played result
  is claimed.

## Owned-stone closed Door follow-up — Kareem via Claude, 2026-11-19

- The rule is data in `dungeon_rewards.toml`: the reward-on closed exit uses three
  distinct owned stones, Time ocarina, learned Time song and the real send-off.
  The native completion helper remains in use for escape/moat sources; LACS,
  restoration and Prelude remain completion-driven.
- `DoorOfTime/Event60` reads the existing unsaved altar **invalid** predicate with
  its false branch. That predicate is `not(all three owned stones and Time ocarina
  and learned Time song and real send-off) or opened`. The ordinary play,
  recommended-melody check, scene history, opening scene, latch and Step06 stay.
  Six native saved Bool inputs were printed and checked in build e0f3ccfa; no
  inventory, quest completion, send-off history or saved default is fabricated.
- The native trace exposed why changing only Event60 would be unsafe: this Door
  can open before the escape/moat. Late unguarded count writes could regress
  Step06/Complete, while exact-Step03/04 Field readers could strand both sources.
  Reward-on closed therefore reuses the **existing #32** nine forward-only guards
  and four Field story modules, with their native completion/history predicates.
  It does not use open mode's physical-door module or ungated pedestal.
- Rewards off still selects the original main transforms and modules in every
  Door mode. Open and song-only are unchanged even with reward shuffle on.
- With a closed Door and a nine-slot-only reward pool, a beatable first pull must
  find all three stones in the three child reward slots; adult slots and Rauru are
  beyond that pull. This follows from the selected gate and pool, not an extra
  restriction or a relaxed fill guarantee.

### Door output/UI proof and natural controls

Reward-vanilla **Door overlays** were generated from actual main `05823385d9` and
the candidate working source: every output path and byte matches for closed
(4 resources), song-only (11) and open (13), including each size table. Receipt:
`work/r18-rewards/door-off-main-proof-v1/proof.json`. This is a Door-output
comparison, not a whole-seed comparison or a full gate.

Actual isolated browser Settings smoke: updated help renders with owned stones,
Time ocarina/song and the real send-off; selecting On sets reward shuffle true and
changes the settings string. Screenshot `work/r18-rewards/owned-door-help.webp`.
The empty-library service/tab were closed; no personal preferences or seed library used.

The Door scan decoded **72 slots in 12 natural-name families**, read-only, with
before/after hashes; 564 excluded families were not opened. Family provenance is
name-based, not independently certified gameplay history. Full input ledger:
`work/r18-rewards/door/door-save-scan.json`.

All candidate paths below are relative to `E:/OOTRemake/work/save-backups/`, ending
in `/save/5a3c9e1f0b7d24680000000000000001/<slot>/progress.sav`.
Every row is child, Door closed, opening/first-pull scenes unplayed, three owned
stones (stock 1 each), real send-off played, child castle and all three child
quests Complete, A=true, B=false and ENV=false.

| Backup family / slot | File date, 2026-11-09 | Door step | Time ocarina / learned Time song | Escape / moat played | Selection |
|---|---|---|---|---|---|
| `2026-11-09_0954-main-after-jabu` / `slot_01` | 09:54:59.759 | Step03 | false / false | false / false | **D2**, earliest continuity candidate |
| `2026-11-09_0954-main-after-jabu` / `slot_03` | 09:54:59.765 | Step03 | false / false | false / false | later, unused |
| `2026-11-09_0954-main-after-jabu` / `slot_05` | 09:54:59.781 | Step03 | false / false | false / false | later, unused |
| `2026-11-09_0954-main-after-jabu` / `slot_04` | 09:54:59.818 | Step03 | false / false | false / false | later, unused |
| `2026-11-09_1022-main-adult-first` / `slot_03` | 10:22:06.360 | Step03 | false / false | false / false | later, unused |
| `2026-11-09_1022-main-adult-first` / `slot_05` | 10:22:06.362 | Step03 | false / false | false / false | later, unused |
| `2026-11-09_1022-main-adult-first` / `slot_00` | 10:22:06.363 | Step05 | true / true | true / true | **D1**, only positive candidate |

Selected progress SHA-256:
D1 `847c8216d06558a0037043769a95a7c77c32bc8c2f705702e9b1ac473fedd82b`;
D2 `8820e1dec52cb39894361fa7a6874a7ef9b4cd5ad16a2b3778a2d6e15dc77e48`.
Each arm has only its chosen slot plus account/options in an isolated user profile;
all copied files match their originals. No inventory, quest, age or history edits.

Packet: `work/r18-rewards/door/CHECKLIST.md`, four launchers under its `ingame/`.
This is a **Door-only diagnostic**, not a generated reward seed: Rauru and other
reward grants remain vanilla. Candidate uses the reward-on closed Door transform;
actual main `05823385d9` control keeps main's closed repair, with native identity
copies for candidate-only paths. Both arms write the same eleven resources.
Four launcher dry runs exited 0 against rc.7; this is not a boot or play pass.

- **D1:** child just inside Market gate; both arms must open once with the Time
  ocarina/song, grant nothing at the Door, retain the latch through leave/re-entry
  and Save & Continue, and never replay. **5–8 min per arm**.
- **D2:** child in Zora's Domain before escape/moat; both arms must retain native
  escape, both moat rewards, no airwall loss, then once-only Door opening and reload.
  **10–15 min per arm**.
- Optional adult first pull / real walk to Field / #32 clock and Sun's Song:
  **5–8 min per arm**. Do not debug-set the clock during these checks.
- Total Door packet **30–46 min**, plus **10–16 min** optional, unmeasured in game.
  Require each runtime's own mods-load lines and the observations; no agent starts it.

**Dropped, no natural state:** playable fewer-than-three-stones refusal, learned-song
but missing-send-off/Time-ocarina refusal, main-opens/candidate-refuses discriminator,
and early pull followed by a late escape/moat. Do not fabricate these states. D1's
natural ownership and completion agree, so it cannot distinguish the two gates;
D2 proves only native-order continuity if played. Distinguishing/late-order cases
remain offline coverage, not played acceptance.

Additional non-lock proof: eleven scenarios executed against the transformed native
Door flow and its written GameData: owned-three without child completion opens;
each missing stone, missing Time ocarina/song/send-off, completion without ownership,
opened latch, played scene and wrong melody refuse; successful replay is inert.
Only the native opened latch and Door Step06 were written, never child quests.
The first harness omitted the explicit opened=False primitive; the strict evaluator
printed missing hash `1920740541`, identified as the opened Bool. Adding that
missing harness input made the aimed run pass; production code was not changed.

Read-only source check confirms `IsGet.Item_Melody_SunSong=true` in **both** D1
and D2 selected saves, so their optional Sun's Song observation has its prerequisite.
The reward-on moat logic also retains #32's **Fire/Water completion only**, not a
new Forest-completion or owned-stones condition.

End-to-end, non-lock CLI smoke:
`CLAWSHOT_WORKERS=1 uv run python -m clawshot --romfs E:/Games/Hookshot/romfs
--seed 180519 --dungeon-rewards --bridge medallions --bridge-count 6
--out E:/OOTRemake/work/r18-rewards/owned-door-seed-180519`
completed: **177 shuffled locations, 20 spheres, 123 files**, including the four
Field story modules. Beatability passed before writing; no game was launched.
Log: `work/r18-rewards/owned-door-seed-smoke.log`.

Scoped Ruff initially printed two whitespace diffs and one test-only SIM401;
applied those exact fixes (including `flows.get(path, game)`). All five changed
Python files then passed format and lint. Removed default-vs-explicit-false
tautologies from the new tests; actual-main byte identity is the external proof above.

### Final focused Door verification

`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest
tests/test_reward_door.py tests/test_dungeon_rewards.py tests/test_door.py
tests/test_door_story.py tests/test_door_stage.py tests/test_door_dump.py
tests/test_clock_environment.py tests/test_clock_transitions.py
tests/test_reward_bridge.py tests/test_story_steps_darunia.py
tests/test_story_steps_fire.py tests/test_story_steps_darunia_dump.py -q`
→ **722 passed, 3 existing parametrization deprecation warnings, 249.81 s**.
No skipped native coverage in this focused command. It exercises ownership versus
completion, Ocarina/song/send-off refusal, recommendation and once-only guards,
forward-only late writers, escape/moat and native physical-door continuity, inverse
flow/GameData/module masks, shared Darunia consumers and a real `make_seed` path.
Log: `work/r18-rewards/owned-door-focused.log`. This is not the held full gate.

The formatter changed only the Door function-signature line wrapping after packet
staging. A fresh build from final source SHA-256
`1d230ac11525225d64b548c55623ecdeddb84195d96a9c93af232b1a85ec846c`
matches **all eleven staged candidate files byte for byte**; no launcher, profile
or staged mod needed replacement. Receipt:
`work/r18-rewards/door/formatter-output-proof.json`.

## Switch polarity audit — Claude's 2026-11-19 steer

**CORRECT: 0=true, 1=false.** No production or packet correction needed.
Every switch rewritten by Track E uses `GameDataActor.EventQueryIsGameDataBoolExp`;
none adds `EventQueryIsExistInPouch`. Reward grant swaps add no switches. The bridge
module and Field modules read Bool outputs, not event-switch integer cases.

Native examples in supported `DoorOfTime`:

- **BoolExp:** Event38 tests Fire quest Complete; 0→Event39, 1→Event56. Water
  completion at Event39/56 then yields 0 remaining (Event37→77→4) when both are
  complete, or 2 remaining (Event6) when neither is complete. Native Event60's
  strict after-Step04 true branch is also 0→Event69; false ends.
- **Bool:** Event69 reads the saved opened latch. False **1**→Event58 continues
  opening; true **0** has no case and ends. Event53 sets that same latch true.
- **History:** Event23 reads `Dm_TimeTemple_0040`. Played **0**→Event22 invokes
  repeat `Market_Child_Field_ChildToAdult`; unplayed **1**→Event141 starts first pull.
  Event58 similarly uses unplayed **1**→Event28, already-played **0** ends.

The following is the complete Track E rewrite/reuse list. Every row uses the
BoolExp polarity demonstrated by native Event38/39/56 and Event60 above; missing
case means the entry ends. The nine round16 writer guards are reused unchanged,
including Event7's existing clock/recount continuation.

| Flow / switch | Predicate | Case 0: true | Case 1: false |
|---|---|---|---|
| DoorOfTime / Event60 | altar reaction **invalid** | end; refuse | Event69; ordinary opening checks |
| AllSage / Event11 | Defeat_Ganon strictly past Step01 | end; no rollback | ClawshotBridgeEvent11Write |
| DoorOfTime / Event7 | Door strictly past Step02 | ClawshotClockArrival | ClawshotDoorEvent7Write |
| DoorOfTime / Event147 | Door strictly past Step2_1 | Event5 | ClawshotDoorEvent147Write |
| DoorOfTime / Event148 | Door strictly past Step2_2 | Event5 | ClawshotDoorEvent148Write |
| DoorOfTime / Event37 | Door strictly past Step03 | Event77 | ClawshotDoorEvent37Write |
| DoorOfTime / Event12 | Door strictly past Step04 | Event140 | ClawshotDoorEvent12Write |
| DoorOfTime / Event14 | Door strictly past Step05 | Event171 | ClawshotDoorEvent14Write |
| DoorOfTime / Event57 | Door strictly past Step06 | end | ClawshotDoorEvent57Write |
| Dm_SY_Ocarina_SariaSong / Event172 | Door strictly past Srep2_1_1 | end | ClawshotDoorEvent172Write |
| Npc_Hylia_Zelda_Child / Event42 | Door strictly past Srep2_1_1 | end | ClawshotDoorEvent42Write |

Main's inherited send-off/count, arrival/environment, child-return and once/history
switches retain their existing mappings. The reward-vanilla all-mode byte comparison
and reward-on inverse oracle above cover those unchanged paths. No pouch-query
polarity is guessed or introduced by this track.

Added native assertion
`test_reward_door.py::test_dump_emitted_switch_polarity_matches_native_once_and_stone_counter_examples`
pins the native Bool/history/counter examples, all eleven emitted guard mappings
and strict bridge-step boundary outcomes. Targeted command with
`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest <that-node> -q`
→ **1 passed, 0.92 s**; new test file format/lint passed. Earlier **722 passed**
remain valid: this follow-up changes only tests and this evidence, not source or mods.

## MAIN FINAL rebase and lesson integration

Claude authorized rebase onto **e241a85**, third in lock order after G and F.
Clean rebase produced `430918afe59c6083a4f77950a4868ceae7682680`.
No lock acquisition until Claude's message after cs18f READY.

The rebased focused command added `test_app_schema.py` and
`test_settings_native_logic.py` to the previous Door/reward/#32 consumers:
**1528 passed, 1 failed**, 393.61 s. Printed failure:
Prelude now requires `is_adult and Defeat Phantom Ganon and Ocarina and
(is_child or (Ocarina,2))`; the old test supplied only Forest completion.
Updated the contract assertion to retain MAIN FINAL's adult Time-ocarina gate,
and made the medallion-only refusal include a usable instrument so it tests the
ownership/completion distinction rather than accidentally missing another input.

Printing the other prepared lesson rules exposed a real integration bug: E's
completion replacements erased MAIN FINAL's age-usable instrument condition for
Nocturne and the moat Time-song lesson, in both reward and count-only modes.
Restored that clause in the two data rules, with `song_lessons.toml` provenance.
The pre-lesson moat **item** stays instrument-free, as the native grant precedes
the lesson. Added reward-only, count-only and combined-option regressions; no
native flow, module, staged mod or save changes.

Current working-set coverage is **1285 required, zero missing** in E's existing
private layered fixture (`main-final-working-set.json`). Reward-vanilla Door
overlays were compared again against actual MAIN FINAL
`e241a857048db995aaba7ae23b7ee52ac15fb92e`: closed, song-only and open are byte-identical
(`door-off-main-final-proof-v1/proof.json`). Both checks used the rebased head above.

Aimed post-fix command:
`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest
tests/test_dungeon_rewards.py tests/test_song_lessons.py
tests/test_r18_logic_returns.py tests/test_app_schema.py
tests/test_settings_native_logic.py
tests/test_reward_door.py::test_dump_a_reward_seed_ships_the_owned_door_with_its_story_and_stage -q`
→ **919 passed, 213.35 s**. This covers the changed rules, every baseline lesson,
return construction, app/settings validation and a real native reward seed. The
1528 other rebased focused passes remain recorded above; no unchanged rerun.
New test-file format/lint passed. Receipt:
`work/r18-rewards/main-final-lesson-fix-focus.log`.

Only the two logic clauses and their test/docs changed after the rebase failure;
Door/bridge flow code and all staged diagnostic mod bytes are unchanged.

### Lock-order update — Claude

B and D passed Kareem's play. Their stack, gated by cs18d, now goes immediately
after cs18g, followed by cs18f, then cs18e. E waits for cs18d's READY and F's
completed turn before taking `gate.lock`. No automatic runner or lock acquisition.

## Natural post-send-off owned-Door discriminator — Claude's revised steer

The proposed New Game replay was superseded: preserve the real send-off, but
do not spend Kareem's time repeating Talon, Zelda or Impa. Use a natural
post-send-off save with fewer than three owned Stones and child completions,
then acquire the missing kit from actual chests; drop the check if none exists.

Reused the existing 72-slot natural-name scan rather than scanning the same
2487 backups again. **23 slots qualify** (15 with one Stone/one child completion,
8 with two/two). Selected earliest `2026-11-07_1630/slot_01`, child in Goron City.
Fresh read and copied profile match the original progress SHA256
`ddda83d54c31961dc2ca0da79fb46307e72cadcddd7ba17745c108b52fd6ac85`.
Mido's blocker is already false. Natural source values:

| Input | Source |
|---|---|
| A `HyruleField_ArriveEntrance` | true |
| S real `Dm_HrlField_0020` send-off | true |
| B `HrlField_HasEnteredFirstTime_Adult` | false |
| ENV `HyruleField_ChangeENV` | false |
| Owned Stones / child completions | Emerald only / Deku only |
| Fire / Water quest | `DodongoCavernOpne` / `Ready` (both incomplete) |
| Door / escape / moat | Step02 closed / unplayed / unplayed |
| Time ocarina / Time song | absent / absent |

No source clock, inventory, flag, position, quest or age edits. Saved flags do
not certify the live clock. Four ordinary Mido chest Hashes are absent from the
source's collected-key list; the checklist still requires actual chest
availability as the first runtime observation, never a repair if already open.
The Kokiri Sword chest is unnecessary because this source already owns Emerald.

Built from frozen **ea50018295450f035ed8367fe546d9309e7aa4f8**, seed **180520**,
closed Door, rewards on, forest open and free time travel on for the requested
early round trip. Four fixed diagnostic bonus grants:
Mido Top Left Time ocarina, Top Right Time song, Bottom Left Ruby, Bottom Right
Sapphire. Production's reward-only admission stays unchanged; the normal nine
reward slots retain their permutation. The bonus checks exist in the world
before the **normal full-goal fill and beatability proof**; the same production
chest planner writes their physical actors afterward.

Observed: **183 shuffled locations, 21 spheres, 130 files**, all four chest
actors read back correctly in both child/adult Banc copies, nine-slot reward
permutation asserted, original/copy files hash-equal. Romfs digest
`51389848b2bc60a38a3ce1250e36c8bc63ee9a08ad6a27092fdd37d104bc3d72`.
This certifies the full-seed model, not an entire randomized playthrough on this
old save. Explicit diagnostic pins are not encoded by a public settings string.

Two setup failures were printed and corrected before any successful fill:
`free_time_travel` belongs in `Settings.logic`, not the constructor's keywords;
the always-progressive pool requires Chest shuffle, not `shuffle=()`.
The aimed build then passed in **83.29 s**. No production change, lock or full
gate; exactly one successful seed built.

Packet: `E:/OOTRemake/work/r18-rewards/door-owned-natural-v1/`.
Launcher: `ingame/Test - owned Door - natural candidate.bat`.
`packet-proof.json`, `source-proof.json`, `build-chest-pool.log` and
`launcher-dryrun.json` retain receipts. Actual launcher dry-run selects Longshot
rc.7, its own unchanged save copy and one mod; no game launch. The isolated
`read_state.py` was exercised and printed the original ownership/quest/clock
state with no `mods:` lines yet (unplayed, not a loading pass).

Candidate route: teleport to Forest entrance, obtain four missing items,
teleport to Market entrance, walk to Temple, play Time song, observe opening
with Fire/Water incomplete; pull/return child once and observe no premature
escape/moat or Door re-close. **7–9 minutes estimated/unmeasured, cap 10**.
Optional **+2 minutes** is worthwhile with entrance teleports: leave Sapphire
shut, show two-Stone refusal, retrieve it, then show three-Stone admission.
No Talon/Zelda/Impa replay, controls, fake save or dungeon-completion shortcut.
The later completion-triggered escape/moat remains outside this short check.
Launcher posted to `cs-r18` at 11:47. **Built, not played; Claude boot-checks.**

## Door v1 BLOCKED in play → verified closed-chest v2

Claude relayed Kareem's played result: Mido's four chests were already open in
the exact natural source, so no kit could be acquired. **V1 is BLOCKED, not a
Door feature pass.** Do not rerun it. Its 23 matching saves were only
story/inventory candidates, not certified usable kit fixtures.

Cause: E read absence from the raw Bool64 collection list, which does **not**
certify a chest's open state. Track F's `fixtures/jail_chests.py:36` uses the
actual named Bool: `save.flag("IsTreasureBoxOpen.<actor Hash>")`. E now requires
explicit **false**, never None or missing-key absence. Kareem's observation is
the repro; no Mido recheck was run. V1's played output/profile remain untouched.

Same original `2026-11-07_1630/slot_01` and full SHA recorded above. Source has
native Bracelet, Kokiri Sword, Fairy Ocarina, Sun's Song and Zelda's Letter;
**no Bomb Bag or Bombchus**, so Track F's adult bomb-dependent DMT/GC/DMC
collection route cannot simply be copied. Selected four child-capable sites:

| Actual named open Bool suffix | Raw Bool | Child access without kit | Grant |
|---|---|---|---|
| `8291119063305855945` | 0 / false | true | Time ocarina |
| `8607798771661947511` | 0 / false | true | Time song |
| `16912540161937823130` | 0 / false | true | Goron Ruby |
| `9622128545943056087` | 0 / false | true | Zora Sapphire |

All names are `IsTreasureBoxOpen.<suffix>`. Their 32-bit flag keys and raw
values are in v2 `source-proof.json`; the copied candidate's separate
`staged-state.json` prints all four false as well. A child-only Search uses only
actual source-owned prerequisites, no kit or adult finds. The first grave
probe printed false access because the fresh-start search had not inherited
the source's already-achieved Time Flows event. Printing counts showed the
missing event; supplying it from the already-verified natural A/S/B/ENV
predicate makes all four reachable. No source flag or production logic edit.

Plain landmarks: the two cracked-wall alcoves on the **west side of Dodongo's
first giant-skull hall**, by the sealed central door: **north** Time ocarina,
**south** Time song. Nearby native Bomb Flowers plus the owned Bracelet
provide access, with no Bomb Bag. Then Kakariko Graveyard at night (native
Sun's Song is owned): standing at the Royal Tomb entrance facing out over the
graveyard, nearest row of seven graves, **fourth from right, unmarked ReDead
grave** Ruby; **leftmost / seventh from right, enemy-free grave** Sapphire.
Native Kokiri Sword handles the ReDead; Sun's Song may stun it.

New packet, never an in-place rebuild:
`E:/OOTRemake/work/r18-rewards/door-owned-natural-v2/`.
Launcher: `ingame/Test - owned Door - natural candidate v2.bat`.
Same seed 180520, settings and frozen production source as v1; build HEAD
**d023843e0fa9008f8554d3446890b3003a608911** is only v1 evidence docs after
the frozen production base ea50018295. Full-goal fill and beatability pass:
**183 shuffled locations, 21 spheres, 124 resources**, 137.66 s. Nine-slot
reward permutation and four physical chest actors read back correctly.
Digest `3073cf48c8a381b3d199468ff32e24460394e91d9dd75147d18957693ca47686`.

Actual launcher dry-run passes on rc.7 with only the new v2 mod/user. Original
and copied save hashes remain identical; read-only v2 helper prints closed
chests, natural A/S=true B/ENV=false and no runtime `mods:` lines yet. No game
boot, full gate, lock, inventory/clock/quest/age edits or reset chests.
Posted the full launcher and plain landmarks to `cs-r18` at **12:56**.
Checklist retains Door opening, early adult/child round trip, persistence and
optional two-Stone refusal; target 8–10 minutes, hard stop 10. **Built/unplayed.**

## Door v2 PLAYED PASS; final gate authorized after D

Claude relayed Kareem's result: the kit was collected from the two Dodongo
alcoves and the two graves. With all three Stones owned, the Door opened
while Dodongo and Jabu were not done, stayed open, and no castle escape/moat
scene played. **Owned-Stone Door positive PLAYED PASS.** The optional
two-Stone refusal was **NOT played**; do not count it as a game pass.
No additional round-trip/persistence result is inferred beyond that report.

The real v2 `longshot_log.txt` independently supplies `mods: ... <- ...`
lines for DoorOfTime, GameDataList, the Dodongo Dynamic/Static and Graveyard
Child Dynamic/Static Banc files, and all four Field modules. Retained in
`work/r18-rewards/door-owned-natural-v2/played-load-proof.json`. This is
loading evidence plus Kareem's reported result, not an agent-run game.

Latest order supersedes the prior wait for F: **D's running B+D gate → E → F**,
because F's fix still needs play. Claude authorized E to take the lock when
D releases it, complete one full gate on the frozen code, and post READY
with its exact head; docs-only commits after the code are permitted.
The outstanding settings sweep stays serialized with E's gate. No rebase or
production change. Claude subsequently corrected the concurrency policy: at
each stage start, freshly check for `longshot.exe` or `hookshot.exe`. Without
either game, sweep/synthetic use outer parallelism 12 and
`CLAWSHOT_WORKERS=12`; dump uses `-n 12` and `CLAWSHOT_WORKERS=4`. With either
game running, that stage uses outer parallelism 4 (`-n 4` for pytest) and
`CLAWSHOT_WORKERS=1`. No blanket one-worker cap or cross-stage cached check.

## Rebased final verification after B+D main moved

Claude reported B+D passed on `d3ce136b46991b009a8aa897e56903e98554e799`
(synthetic 3528 passed/441 skipped; dump 438), merged and pushed as main.
Per the new instruction, E stopped the obsolete `d2b3617` sweep, rotated
its ownership token before cancellation, and **retained the same lock
without a release/reacquire gap**. No old-head full gate was admitted;
the old sweep and driver records are archived under
`work/r18-rewards/obsolete-d2b3617/` and do not count toward readiness.

`git rebase d3ce136b46991b009a8aa897e56903e98554e799` replayed all 12 E
commits cleanly with no conflict. Frozen rebased verification head:
**`ac4dd8602d43971ddedafa582e6034e7b5961342`**.

Focused synthetic command: `uv run --with pytest-xdist pytest
tests/test_dungeon_rewards.py tests/test_reward_bridge.py
tests/test_reward_door.py tests/test_door_story.py
tests/test_song_lessons.py -m 'not dump' -n 4 -q`, with
`CLAWSHOT_WORKERS=1` and dump inputs unset. Actual stage-start process
snapshot found a game running; **308 passed in 9.86 s**, exit 0.
Receipts: `work/r18-rewards/rebased-focus.log` and
`rebased-focus-results.json`.

The retained-lock driver's 300-seed sweep completed but FAILED; its full gate
was subsequently started separately, then stopped immediately on Claude's
instruction. The results below supersede that attempted verification.

## Failed sweep, released gate, reward palette repair

Frozen `ac4dd8602d43971ddedafa582e6034e7b5961342` completed 300 seeds:

| Recipe | Seeds | Exhausted |
|---|---:|---:|
| Broad | 200 | 146 |
| Defaults | 50 | 0 |
| Recommended | 50 | 14 |

All 1600 printed failed fill attempts ended in `progression`; 1386/1460
broad and 136/140 recommended attempts failed on a Spiritual Stone.
The full gate was stopped as Claude instructed; E verified its token and
released `gate.lock` for F+G. **No gate pass or READY is claimed.**
No unchanged sweep rerun, retry increase or accepted-settings relaxation.

Read-only hypothesis check, no dump generation: with all non-reward items
assumed, zero or two Stones leave only Gohma, King Dodongo and Barinade
reachable; all three open all nine reward sources. Thus normal closed-Door
seeds must put the three Stones on the child bosses. The implementation was
not a random-permutation check: `_fill_restrictive` already removes the
current item from its assumed inventory. The bug was **stage ordering**:
`allowed()` imposed a closed reward palette, but preparation never
registered that palette. Earlier ordinary type-held stages assumed all
unplaced Stones and could strand a child-boss prerequisite behind the Door.
The later progression stage could not swap items out of those earlier stages.

Repair: derive the reward palette with the existing restriction convention,
then let `_fill_palettes` place it before ordinary type-held items. Its
assumed base excludes the nine rewards; the normal restrictive search handles
the remaining stage items and excludes the current reward. No new placer,
retry constant, location, native patch or completion/ownership rule.
Reward shuffle off returns the original settings unchanged.

Proof: **55 passed** in the focused reward module, including 36 fully
synthetic consumer cases (three-Stone, six-medallion and Light-only gates;
12 seeds each; exactly one fill attempt). They verify the ordinary child
prerequisite, nine-item permutation and independently searched full goal.
An old-behavior ablation fails 14 of those cases; seed 0's Stone case passed
and was not misreported as a counterexample. The initial synthetic fixture's
missing top-level `locations` produced a printed KeyError and was corrected
in the fixture, not hidden by a production fallback.
Narrow ruff format/check both pass.

Printed failed broad seed `18051000`, bridge nine rewards, now passes with
normal beatability in **two attempts, 22 spheres, 27.25 s**; one aimed rerun
after the cause-directed code change. Receipt:
`work/r18-rewards/reward-palette-aimed.json`.

Claude's latest order: F+G holds the gate and changes key placements.
The **counting** 300-seed zero-exhausted sweep and one full gate must both
run after E rebases onto F+G's merged main and freezes that new head.
No old-head counting sweep is queued. Sweep rows now record actual effective
`Seed.settings`, not their pre-prepare inputs.

For early signal only, Claude separately authorized **60 broad + 20
Recommended**, without a lock, on the current fixed head
`ab20970590617e270d2723817f0f7ee1ae850774`. Outer and internal workers are
capped at four, reduced to one if Longshot/Hookshot runs at that recipe's
stage start. The early sample omits the already-proved aimed `18051000`
smoke; all three bridge modes are sampled. Results must report exhausted
counts and mean fill attempts across **all** seeds (including exhausted
attempts), and are **NON-COUNTING**. Completed results follow.

## Authorized early signal completed — NON-COUNTING

Source head **`ab20970590617e270d2723817f0f7ee1ae850774`**.
No lock acquired or touched. Both recipe-start snapshots found no game;
outer parallelism four, `CLAWSHOT_WORKERS=4`.

| Recipe | Seeds | Exhausted | Mean attempts, all seeds | Maximum attempts |
|---|---:|---:|---:|---:|
| Broad | 60 | 0 | 1.1166667 (67/60) | 3 |
| Recommended | 20 | 0 | 1.0 | 1 |

Broad took 199.95 s, Recommended 63.67 s. Every seed completed normal
full-goal beatability and the nine-reward permutation assertion. Receipts:
`work/r18-rewards/early-palette-ab209705/results.json`, `broad-rows.jsonl`,
`recommended-rows.jsonl`; driver log `early-palette-signal.log`.
Exhausted counts and mean attempts posted to `cs-r18` at 15:18.

This is an early signal only, **not the counting 300 or a gate pass**.
No retry limit increased. F+G changes key placements, so E must rebase onto
their merged main, freeze the new head, then run the counting 300 with zero
exhausted and one full gate. **Not READY; no old-head counting run queued.**

## Final F+G merged integration and frozen counting run

Claude supplied pushed main **`8fadebf16b4087f735da2738d116645e47de3a7d`**
and authorized the free lock. E acquired it once, retained it through rebase
and focus, and adopted the same token for final verification.

Rebase replayed all 14 E commits. The first commit had the seven reported
conflicts plus `patch/__init__.py` and `test_pack_nup_dump.py`; the owned-Door
commit conflicted again in patch composition, and the reward-staging repair
conflicted again in `generate/prepare.py`. All were composed, not resolved
by taking whole files:

- Keep F's jail setting/default/CLI, Chest requirement and key source types;
  add E's reward/bridge options and reward shuffle type alongside them.
- Compose `rewards.prepare_spec` and `key_families.prepare_spec`.
- Compose token/reward/progressive restrictions, then retain F's outer
  `key_families.restrict_settings`; it copies and augments the same palette
  dictionary instead of losing `DungeonReward`. The existing palette fill
  still precedes ordinary type-held progression.
- Keep G's Dampe safety/story-dialogue patches, add E's owned-Door arguments
  and bridge changes, and retain both F's and E's dump resource modes.

Integrated frozen verification head:
**`3a33864d0eeca8c1a490dfaa25d17dd51bf9cf9c`**.
Focused synthetic E reward/bridge/Door/story/lesson suites plus F key-family,
floor/jail/model/binding/text and fill/gifts-fill/age-fill suites:
**487 passed in 18.25 s**, exit 0. No game at stage start:
`-n 12`, `CLAWSHOT_WORKERS=12`. Receipt:
`work/r18-rewards/focused-fg-integration.json` and `.log`.
Scoped formatting of four resolved Python files and lint both pass.

The private `work/rounds/r18/fg-rewards-layered-dump` clones F's completed
fixture and adds only E's bridge module and nine actor packs from the
read-only RomFS. **All 1292 current working-set inputs present**, none missing;
fixture/original digests equal. F's fixture, the original dump, all game
folders and played outputs are unchanged. Receipt `fg-fixture-proof.json`.

The counting run is **200 broad + 50 Defaults + 50 Recommended**. Broad
keeps all-anywhere dungeon items and explicitly enables Fortress jail keys,
so it exercises the newly composed key/reward palettes. Presets retain
their own F key defaults. All three recipes enable E rewards and closed
Door, cycling the three count-bridge modes with their maximum counts.
The driver rechecks game processes separately at sweep/synthetic/dump
stage starts, stops without a full gate on any exhausted seed, and
otherwise performs **one** full format/lint/synthetic/dump gate. Receipts
go to `work/r18-rewards/counting-3a33864d0eec/`; no earlier-head evidence is
substituted. The actual counting and one full gate both passed, recorded below.

## READY — final counting and one full gate passed

**Exact tested code head: `3a33864d0eeca8c1a490dfaa25d17dd51bf9cf9c`.**
Based on pushed F+G main `8fadebf16b4087f735da2738d116645e47de3a7d`.
This receipt is docs-only after that frozen head; no post-gate code change.

| Counting recipe | Passed | Exhausted | Maximum attempts |
|---|---:|---:|---:|
| Broad, all-anywhere + Fortress keys + E options | 200 | 0 | 3 |
| Defaults + E options | 50 | 0 | 1 |
| Recommended + E options | 50 | 0 | 1 |

Normal fill/beatability and nine-reward permutation checks ran for every
seed. Counting sweep exited 0 in 380.97 s. No retry increase or seed
substitution, no old-head/early-signal evidence reused.

One full gate on that same frozen head, all exit 0:

| Stage | Command | Observed result |
|---|---|---|
| Format | `uv run ruff format --check` | passed |
| Lint | `uv run ruff check` | passed |
| Synthetic | `uv run --with pytest-xdist pytest -n 12` | 3768 passed, 489 skipped, 36 warnings; 256.06 s |
| Native dump | `uv run --with pytest-xdist pytest -m dump -n 12` | 486 passed, 36 warnings; 1455.07 s |

Fresh game-process checks were false independently at sweep, synthetic and
dump starts. Sweep/synthetic used outer 12 / `CLAWSHOT_WORKERS=12`; dump
used `-n 12` / `CLAWSHOT_WORKERS=4`. Native dump used the read-only original
RomFS/NUP plus E's complete combined F+G/reward fixture. The retained E lock
was released only after both counting and the full gate passed, matching
token `236d0f6179144d2b9a81766532c79e96`. No game launched.

Receipts under `work/r18-rewards/counting-3a33864d0eec/`:
`sweep-results.json`, `sweep-rows.jsonl`, `gate-results.json`,
`serialized-results.json`, per-stage logs and driver logs.
Top-level driver transcript: `work/r18-rewards/counting-integrated-run.log`.
Gate logs retain all 36 warnings. Skipped coverage in the synthetic run is
not misrepresented as a pass.

**READY, with remaining in-game coverage play-held.** Default-off feature
status unchanged. Door v2's positive owned-Stone opening, stayed-open
state and no premature escape/moat remain Kareem's reported played pass
with retained native loading evidence. Optional two-Stone refusal was
**not played**; no broader randomized-playthrough claim is made.
