# Round 18, Track E — rewards and bridge (cs18e)

Branch `r18/rewards`, base `2ba2f9a`; model `openai-codex/gpt-6.1-sol`.
Research and staged output: `E:/OOTRemake/work/r18-rewards/`. Dump read-only.
No game started; no player seed or save opened. All behavior remains unplayed.

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
| Door of Time `DoorOfTime/Event38,39,56` | Fire/Water stone **quest completion**, not owned stones; `DoorOfTime_GetStoneCount` counts remaining quests | Preserve completion unless maintainers explicitly select ownership. Open/song-only modes retain their existing send-off/clock contract. Logic must stop treating shuffled stones as a completion proxy. |
| Door/altar scene | DoorOfTime stages, `Market_Child_TimeTempleDoor_Opened`, melody/clock/history guards | Stay story-driven; never complete a stone quest by finding its reward. |
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

**Accepted by Claude, 2026-11-18:** keep every completion reader native, including
the closed Door. Ownership drives only the explicit bridge count. Reward-on logic
must use the three child dungeon completions for the closed Door and Shadow/Spirit
awakenings for LACS. No new Door flow transform is added by Track E.

**Open question for Kareem (morning): should the closed Door follow owned stones
instead?** This round deliberately retains completion; changing that is a separate
product decision, not a consequence of moving the three reward actors.
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

Reader contract accepted; reward/bridge implementation, Master Sword design and
isolated controls are built. Focused proof passed; required sweep and full gate
remain pending the Track C fill fix on current local main. No READY claim yet.

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
- First native-generation attempt printed a real construction error: the closed-door
  adult-return bound forgot the three mandatory child completions after replacing its
  stone proxy. Printed search state: Forest defeat true, adult pedestal unreachable
  because the Door rule lacked Gohma/Barinade completion. Added those **necessarily
  completed before a closed-door pull** events to its data-bound minimum inventory,
  never to early doors or native saved flags. The aimed rebuild passed.
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

### Checklist for Claude to boot-check, then Kareem to play on Longshot rc.7

Use only these launchers, one mod each; `HOS_FS_OVERLAY` is unset. Debug **Teleport
and clock only**. Do not use inventory, quest, age, noclip or collection cheats.
Stop on a mismatch; retain the isolated profile and log, never repair a failure.
For each candidate capture `mods: <file> <- <path>` for the named flow/module and the
actual inventory/result. Native scene models alone are not an acquisition oracle.

1. **First pull — 5–8 min per arm.** `Test - first-pull - medals 2 - control.bat`,
   then its `candidate.bat`. Continue the sole original child snapshot, approach the
   open pedestal and pull normally. Control: Light Medallion; candidate:
   **Fire Medallion, no Light Medallion**, plus the native Master Sword and song/story
   continuation. Source emblem remains Light in both. Inspect owned items, Save and
   Continue; re-enter the Temple. No second reward or skipped native first-arrival
   scene. Loaded resource: `Dm_SageRoom_0005.bfevfl.zs`.
2. **N−1 / N boundary — 2–4 min per arm.** `Test - one-medallion - medals 2 -
   candidate.bat`: continue, Teleport to adult castle approach, walk across both
   native contact areas. One owned Light medal is below two: **no bridge**.
   Separately run `... medals 1 - control.bat` (same natural profile, vanilla
   bridge: **no bridge**) and `... medals 1 - candidate.bat`: exactly one meets one,
   so the native rainbow scene/bridge must appear without Light Arrows or the
   Shadow/Spirit awakenings. Leave/re-enter, Save and Continue: bridge remains.
   Loaded resource: `Logic/GanonCastle_Level_Field_00_Prefab_14ba.logic.module.ainb`.
3. **Adult reward and completion separation — 8–15 min per arm.** `Test -
   forest-warp - medals 2 - control.bat`, then `candidate.bat`. Continue the natural
   pre-warp Forest snapshot; enter the real blue warp (fight Phantom Ganon if the
   snapshot is before his last phase; estimate includes that). Control grants Forest;
   candidate grants **Shadow**, with Forest medal still absent. Native sage scene,
   forest restoration, Prelude and normal return-to-child pedestal must still work.
   Save/Continue and re-enter: no second medal. Candidate now owns Light+Shadow:
   castle approach must open at two, despite Spirit awakening and Light Arrows absent;
   control's vanilla bridge must remain closed. Loaded reward:
   `Dm_Awake_Forest_Get.110.bfevfl.zs`. Use normal native travel, not an age cheat.
4. **Inside boundary — additional 5–10 min, candidate only.** After the early bridge,
   enter normally. With no Light Arrows, ordinary arrows must not clear a trial core;
   no trial-clear Bool/count is pre-cleared by the bridge. Do not spend time finishing
   the castle. This checks that early entry is not a trial skip.

Total short packet, including both controls: **35–65 minutes**, plus 5–10 minutes
for the optional inside boundary. This does **not** include a new child dungeon run
or naturally completing the two late sages; neither is hidden inside a short estimate.

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
