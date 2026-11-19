# Round 18, Track F: key families (cs18f)

Branch `r18/keys`, starting at `2ba2f9a`. Model: `openai-codex/gpt-6.1-sol`.
Research and generated packets: `E:/OOTRemake/work/r18-keys/` only. No player's seed
opened, no game started, no writes to a game/runtime directory. No version bump.

## Early answer: Gerudo Training Ground

Posted to `cs-r18` at 17:11 on 2026-11-18. **The native admission contract does not
query membership-card possession.** Guard 004's schedule suppresses normal talk
until `SageOfSpirit` is past Step01. After that clearance, the native
`Open_TrainingGround` flow charges 30 rupees and opens the gate. A normal vanilla
playthrough obtains the card in the same required captain scene, so this is **not**
evidence of a normal pre-rescue/no-card route. A card alone does not supply clearance.
No bypass was played; existing adult-plus-card logic remains conservative while D39
keeps the captain and card vanilla.

Evidence: `r13-gerudo-card.md` section 3; refreshed read-only native
`Npc_Gerudo_004.bfevfl.zs`: Event88 checks 30 rupees, Event123 deducts 30,
Event0 sets `GerudoFortress_TrainingGroundGateOpend`, Event109 sets
`GerudoTrainingGround_Gate`, Event111 advances `SubEvent_GetIceArrow/Step00`.
External reproduction: `survey_jail.py`, `jail-survey.json`. The schedule/clearance
trace remains the exact source cited by the r13 investigation, not a claim of play.

## Adapter decisions and invariants

Kareem requested both families, 2026-11-18:

- Fortress jail keys: separate default-off `shuffle_hideout_keys` setting. Four
  source identities, not eight placed checks. Played fact: each guard drops its
  key and Link picks it up from the floor; no hand-over is substituted.
- Well floor key joins the existing small-keys-anywhere modes; own-dungeon mode
  retains it unchanged. **Claude's superseding round decision:** Shadow stays vanilla,
  **built, held until a natural pre-room save exists**. Its structural adapter is
  retained but absent from the active generation source allowlist.
- Source rewards use the smallest supported palette: **Rupees (20)** or their own
  native key. Proposed by cs18f from native source/pouch evidence. This releases
  keys into supported shuffled chests without claiming arbitrary-major delivery.
  Red rupees share the key's exact `PouchContent_PickUpItem_EnableWarp` performer;
  shields use another performer, hearts use Utuwa. Those families are not admitted.
- A replacement retains the native key-shaped floor model/animation, but uses the
  red rupee's canonical identity and pouch semantics. Its text/grant must name the
  actual reward. This intentional display limit needs the staged play check.
- Preserve source root, death/retirement wiring, physical identity, guard defeat,
  uncollected restoration, every carpenter rescue and native jail-door spending.
  A Fortress key found in a chest credits only the three Fortress inventory leaves;
  it must not mark a guard reward collected or rescue a carpenter.
- D39 remains absolute: card and captain check stay vanilla; preserve
  `Meet_FourCarpenter_ClearEvent`, the card grant and Spirit Step02. Card possession
  alone is not fortress clearance.

All behavior changes are **built, not played** until Kareem accepts the matched
candidate/control checks on Longshot rc.7. No READY claim yet.

## Built evidence

- `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest
  tests/test_key_families.py tests/test_jail_keys.py tests/test_floor_keys.py
  tests/test_key_model.py tests/test_key_bindings.py tests/test_write_new_files.py
  tests/test_world_census.py tests/test_names.py tests/test_key_text.py -q`
  → **149 passed, 44.57 s**. Includes real-dump source/registry inverse diffs,
  source-pack output sizing, every language's named Fortress messages and a static
  grant executor proving that four chest keys alter only Fortress inventory.
- First focused run printed seven failures: wrong positional `SubFlowEvent`
  construction in the new synthetic test; a synthetic output reader incorrectly
  looking for an unmodified dictionary in the mod; an unsorted deliberately stale
  registry fixture failing before its intended collision; and the names oracle
  not yet including the six newly supported sources. Corrected the printed causes.
  The subsequent real-dump writer/source tests above passed; no native failure was
  dismissed as a fixture without that proof.
- Ruff check passes. The formatter's final two trailing blank lines were removed
  after its exact diagnostic; subsequent `ruff format --check` reports
  **433 files already formatted**, and `ruff check` reports **All checks passed**.
- Actual settings UI, isolated empty external seed library and in-memory
  preferences: observed jail switch off, enabled it through its On button,
  observed the updated settings string and built/unplayed/key-shaped help.
  Selected Small keys anywhere, unchecked Chests: the page displayed
  `dungeon_items 'anywhere' moves keys only into shuffled chests: shuffle Chest`.
  Own browser/server closed; throwaway harness deleted. No personal seed library read.
- Own layered dump fixture:
  `E:/OOTRemake/work/rounds/r18/keys-time-layered-dump`, copied from the supplied
  r16 fixture. Seven additions: the two source room modules and
  `Obj_Dungeon_SmallKey` plus four Fortress source actor packs. Full list and
  reproduction: external `fixture-inputs.json`, `supplement_fixture.py`.
  Original dump and r16 fixture unchanged.

### Conservative mapping / compatibility

**Proposed by cs18f:** use four native source names (`Gerudo Fortress Jail Key
01`–`04`) linked to the resting actor Hashes. Their event copies remain unlinked
representations, not additional checks. No suffix-to-torch-room equality is
asserted. Each source's logic requires all four inherited guard-access events
until that correspondence is proved. Carpenter rules still require their guard
and all four keys; the captain/card check remains vanilla. This is conservative
logic, not a runtime restriction on when a player can pick up a reward.

Small-key-anywhere output changes by admitting the Well floor source only. The jail
option changes its pool only when enabled. Both release modes now refuse Chest-off
recipes rather than silently offering keys with no named-grant destination.
Defaults and Recommended keep own-dungeon mode and jail keys off; no version bump
was made (maintainer-owned). The stable native source names also replace the four
unlinked torch-named key checks in the model.

## Staged Longshot checks (unplayed)

Packets are focused diagnostics, **not generated/beatable seeds**. The same external
`stage_packets.py` builds control and candidate. Well/Fortress v2 use frozen main
`2ba2f9a` and candidate `5f78dc7ef3`; Shadow has no staged play check this round.
All emitted chest bindings read back. No inventory, quest, rescue, source-
collection or game-start defaults are patched.

| Family | Launcher under `E:/OOTRemake/work/r18-keys/ingame/` | Main control / candidate |
|---|---|---|
| Well | `Test - well - main-control.bat`, `Test - well - candidate.bat` | **v2:** both give one named Well key in the naturally closed Zora River open-grotto chest. Main floor pickup remains a key; candidate floor pickup gives 20 rupees, no additional key. |
| Fortress | `Test - fortress - main-control.bat`, `Test - fortress - candidate.bat` | **v2:** DMT chest, GC maze center/right and DMC upper grotto. Main's existing generic chest keys do not target Fortress; candidate credits four named Fortress keys. Candidate guard floor rewards give rupees instead of extra keys. |

The Fortress control limitation is intentional and explicit: main has no
`shuffle_hideout_keys` option or named Fortress target. It is its native generic
chest-key path, not a fabricated main target write. Its guards retain their native
keys. The paired checks expose the missing family support, not an invented claim
that vanilla guard keys themselves were broken.

Each launcher is adapted from the current Longshot template (including current
`builds/channel/version/bin` layout), selects exactly one real mod folder,
clears `HOS_FS_OVERLAY` and uses a separate packet-owned user folder.
The four current v2 launchers exit **0** in real `cmd.exe` dry runs on rc.7:
`ingame/well-natural-dryruns.json`, `ingame/fortress-natural-dryruns.json`.
No game start/boot performed.

**Fixture status:** Claude authorized read-only backup selection without further
approval. Well and Fortress each have two isolated, byte-identical natural-slot
copies and retargeted v2 packets (details below). Shadow is held, not a preparation task.
No backup or current played user/seed is modified/read by a launcher. No test-copy
edit was needed. Claude still boot-checks before handing a route to Kareem;
dry-run success is not a claim that a slot or resource loaded in game.

### Acceptance checklist

Run each control first, then start the candidate from an independent copy of the
same pre-check snapshot. Do not reuse the control's progress. Teleport/clock only;
no age, inventory, quest, guard-defeat or source-collected cheats.

1. **Remote credit.** Open the selected fixture's indicated remote chest(s),
   confirm target-named text on candidate keys, save and Continue.
   Enter the target naturally or via the allowed teleport and inspect its key
   counter. Well/Shadow both controls and candidates add one to the target.
   Fortress main generic keys must not credit Fortress; candidate adds exactly four.
   No source-collected/carpenter/card completion may appear from remote credit.
2. **Well floor.** Reach the native room-3
   source with the puzzle still unsolved. Solve it. Leave the reward uncollected,
   leave/re-enter and Save/Continue: it must recover. Collect it: main adds the
   native Well key; candidate adds 20 rupees, not a key. Re-enter and reload again:
   no duplicate. Spend a real Well key at an unopened native lock; save/reload
   retains remaining/found inventory separately.
3. **All four Fortress guards/rescues** (split into B1/B2 below).
   Start before every guard/source/rescue. After remote candidate keys, guards
   must remain hostile and the captain/card scene must not have happened.
   Defeat each guard, observe the floor drop (not a hand-over), leave one
   uncollected for the re-entry/reload recovery test, then pick up each reward.
   Candidate gives one red-rupee reward per identity, no fifth key; main keeps
   native keys. Spend the four candidate keys on the normal jail doors and
   actually rescue all four carpenters. Do not bypass fights or shutters.
   The captain must appear once at the fourth rescue, run
   `Meet_FourCarpenter_ClearEvent`, give the unchanged card and advance Spirit
   Step02; ordinary guards clear only then. Re-entry and Continue must retain
   rescues, spent keys and card without duplicate floor rewards or scene.
4. **Loading proof and saved values.** Record `mods: <resource> <- <packet path>`
   for the packet's remote chest Bancs and candidate source resources:
   Well native Banc plus `Obj_Dungeon_SmallKey_Floor_BottomOfTheWell` pack;
   Fortress the four `Obj_Dungeon_SmallKey_GerudoFortress_0N.pack.zs` files.
   Check target `SmallKeyNum`, `SmallKeyTotalNum`, `IsGetSmallKeyOnce`, source
   collection Bools and carpenter counters/Spirit step on the packet's saved copy.
   Models/text/HUD alone are not ownership or once-only proof.

Per-check estimates are in the natural-fixture sections below. They are not
measured play timings, and the full set of both variants takes longer than one check.
No acceptance was played. Stop a pair if its main control does not show the
expected baseline and hand Claude the loading evidence/state; do not interpret
a non-reproducing control as a passing fix.

## End-to-end generation / tracker smoke

Own seed `180618`, Chest + small keys anywhere + jail keys on: native preparation,
fill, beatability and writer passed, **174 shuffled checks, 23 spheres, 116 resources**.
All six source replacement adapters were exercised. External `seed-smoke-proof.json`
records the effective recipe; this is not a player's seed or a played claim.

Tracker now includes Fortress remaining/found/seed-total inventory and reads the
six pickups' named native collection Bools, not their absent actor-Hash records.
`CLAWSHOT_WORKERS=1 uv run pytest tests/test_tracker_state.py
tests/test_tracker_http.py tests/test_key_families.py -q` → **37 passed, 14.61 s**.
The own smoke seed loads with Fortress total **4**, and its six source checks
resolve to the expected named Bools. No save was needed/read for that smoke.

## Coordinator hold

Per Claude's revised order, cancelled automatic runner `bg_16`. Its retained
output shows only the wait for Track C on main `2ba2f9a`; no sweep or gate started.
Cancellation inspection found no remaining runner/sweep processes and no gate lock.
The external verification driver is now manual-only: requires the explicit
`MAIN FINAL` commit, refuses a mismatched/unrebased main, and never watches main,
rebases, waits for a free lock or retries lock acquisition automatically.

A and D merge first. No rebase, sweep or full gate until Claude posts `MAIN FINAL`
and assigns F its lock turn. Only non-lock work meanwhile. Prior focused and
staging evidence remains built/unplayed; no READY claim.

## Natural Fortress fixture

Read-only `clawshot.save` scan: **2,487 progress files / 643 distinct contents**.
Selected earliest qualifying natural slot by the timestamp stored in `caption.sav`:

`E:/OOTRemake/work/save-backups/2026-11-09_1347-main-after-forest/save/5a3c9e1f0b7d24680000000000000001/slot_02/progress.sav`

- Saved **2026-11-09 18:29:45 UTC**, Forest Temple; snapshot label
  `2026-11-09_1347-main-after-forest`. Natural main playthrough before Phantom Ganon,
  not Kareem's current seed; provenance `plans/00-roadmap.md:860–864`.
- `Sequence_IsChildhood=false`; `IsGet.Weapon_Sword_Master=true`,
  `PouchData.Weapon_Sword_Master.StockNum=1`; exact `IsGet.Item_Hookshot=true`,
  `PouchData.Item_Hookshot.StockNum=1`; Bow owned/stock **1**, arrows **27**,
  bombs **10**, `PlayerStatus.MaxLife=24` (six hearts).
- `Step_SageOfSpirit=Ready`. No scanned save has Step01. **Normal preparation,
  not an edit:** talk to the Gerudo Valley carpenter boss and answer Yes;
  `Npc_Hylia_012_Adult/Event121` advances Ready→Step01 and places the carpenters.
  No Epona/Longshot; use the permitted teleport to the tent.
- For **013–016**: `GerudoFortress_AppearGerudoThief_Npc_Hylia_NNN_Adult`,
  `GerudoFortress_DestroyGerudoThief_Npc_Hylia_NNN_Adult`,
  `GerudoFortress_IsAfterHelpCarpenter_Npc_Hylia_NNN_Adult`,
  `GerudoFortress_CloseShutter_Npc_Hylia_NNN_Adult` and
  `InsideTheRoom_Npc_Hylia_NNN_Adult` are all **false**.
- `IsGet_SmallKey_GerudoFortress.SmallKey01..04=false`;
  `GerudoFortress_BattleGerudoThief=false`;
  `Enemy_MiddleBoss_GerudoThief_DefeatNum=0`; all four
  `HavePlayedEvent.GerudoFortress_MiddleBossLose[_02/_03/_04]=false`;
  `GerudoFortress_WarpPoint01..04_ClearEvent=false`.
- `GerudoFortress_Meet_FourCarpenter_NumOfCarpenterFound=0`,
  `...NumOfCarpenterHelped=0`, `...NumOfCarpenterHelped_02=4` (native default).
  Card `IsGet.Item_Token_Gerudo=false`, stock **0**;
  `HavePlayedEvent.Meet_FourCarpenter_ClearEvent=false`,
  `HavePlayedEvent.Dm_Gerudo_0025=false`;
  `GerudoFortress_GoToPrison_AfterClear=false`,
  `Gerudo_phantomdesert_gate=false`,
  `GerudoFortress_TrainingGroundGateOpend=false`.
- `DungeonInfo.GerudoFortress.SmallKeyNum=0`, `SmallKeyTotalNum=0`,
  `IsGetSmallKeyOnce=false`.
- All four Mido `IsTreasureBoxOpen.<Hash>` values are **true** in every geared
  adult candidate. Rather than edit four flags, **retargeted both packets** to
  naturally closed small chests: DMT `9809508929088891725`, GC maze center
  `1176975953041865014`, GC maze right `14647422914070455120`, DMC upper grotto
  `1158729434763801603`; all four `IsTreasureBoxOpen.<Hash>=false` in this slot.
  Known debug-edited `r16-water*` and another player's `lichii` sources excluded.

Full measured inputs/provenance and earlier-candidate failures:
`E:/OOTRemake/work/r18-keys/fixtures/jail_fixture_report.json`.
Progress SHA256 `fdf3a69b171f5df9c83d8efce932bd5eb44b4f64857ac90a52e69b78d7a8e2f6`.
Copied only this `slot_02` (progress + caption), plus same-user `account.sav` and
`option.sav`, into `ingame/user-r18-keys-fortress-{main-control,candidate}-natural-v2`.
Each copy reads back equal with `clawshot.save`, file SHA256s match and exactly one
progress slot exists. **Copy edits: none.** Proof:
`ingame/fortress_selection-copy-proof.json`.

v2 controls are rebuilt from a detached **2ba2f9a** worktree (7 resources); candidate
**5f78dc7ef3** (34 resources). All chest bindings read back. Both updated `.bat`
launchers exit **0** in real `cmd.exe` dry runs and select rc.7, the matching v2
mod and the isolated natural profile; `ingame/fortress-natural-dryruns.json`.

### Short Fortress route (split, estimates; unplayed)

Run each main control first, then its candidate from its independent copy.

- **A, remote credit: 6–10 minutes per variant.** Before loading Valley/Fortress,
  teleport to DMT, bomb its cracked wall and open the chest; bomb the rock at the
  end of GC's upper west maze middle corridor, open both chests; teleport to the
  DMC upper-rim rock, bomb/drop into its grotto and open the fourth. No Goron
  Tunic: do not linger in the crater. Save/Continue. Candidate Fortress counter
  **4/4/true**; control **0/0/false**. Record all 14 dungeon counters too: the
  control's generic key might retain another loaded dungeon's target (unplayed),
  so do not claim it vanished. Source/guard/rescue/card values remain untouched.
- **B1, first two guards: 8–12 minutes per variant, continuing A.** Teleport to
  Fortress, walk back into the Valley's far side and talk to the tent boss/Yes
  to reach Step01 (no broken-bridge crossing). Fight the one-torch guard:
  observe its floor drop, leave it, re-enter and Save/Continue to prove recovery,
  then collect it, spend a real key and rescue. Repeat guard/pickup/door/rescue in
  the two-torch jail. Main gets native keys; candidate gets red rupees, no extra
  keys. Save. Four remote keys alone must not clear guards or grant the card.
- **B2, remaining guards/card: 8–12 minutes per variant, continuing B1.**
  Four-torch jail, then three-torch jail via the kitchen (Hookshot/Bow).
  Fight/collect/spend/rescue each; fourth rescue gives the captain once, unchanged
  card and Spirit Step02, only then normal guards clear. Re-enter and Continue:
  no repeated reward/scene; rescues and spent-key counts retained.

Each playable segment is estimated below 20 minutes, not the entire multi-variant family.
All source identities and all four rescues remain covered; no bypass or save edit.

## Natural Well fixture

Selected earliest qualifying natural slot by decoded caption save time:

`E:/OOTRemake/work/save-backups/2026-11-13_084401-longshot-transferred/slot_05/progress.sav`

- Caption **2026-11-12 14:57:43**, Kakariko Village child; source is Kareem's
  transferred Longshot snapshot (`plans/rounds/r14-story.md:138`), no documented
  save edit. Earlier slots 03/04 (14:55:29 / 14:56:22) have not drained the Well.
- `Sequence_IsChildhood=true`;
  `Npc_Hylia_009_Child_IsStormSongPlayed=true`,
  `HavePlayedEvent.Dm_Kakariko_0050=true`, `IsVisitLocation.BottomOfTheWell=false`.
- `BottomOfTheWell_Level_Room_03_Get_SmallKey=false`,
  `...Room_03_Get_Key=false`, `...Room_03_Coffin_Open=false`,
  `...Room_02_BurnedAny=false`, `...Room_02_BurnedGimmick=false`,
  `...Room_00_A_Clear=false`: both pickup and puzzle are untouched.
- `DungeonInfo.BottomOfTheWell.SmallKeyNum=0`, `SmallKeyTotalNum=0`,
  `IsGetSmallKeyOnce=false`.
- `IsGet.Weapon_Sword_Kokiri=true`, stock **1**;
  `PouchData.Item_DekuStick.StockNum=10`; bombs **9**;
  `IsGet.Item_DinFire=true`, `PlayerStatus.MPMax=240`;
  Storm Song and Zelda's Lullaby owned. No Lens; it is not needed to perform the
  room-3 source/reload test.
- `IsChainLockDoorOpen.3180753716225647997=false` (east, into room 4),
  `.15964434394101837654=false` (west, into room 5).
- `PlayerStatus.CurrentRupee=99`; large wallet. Candidate reward should give
  **119** if no rupees are spent/picked up en route; use the measured pre-pickup
  balance rather than assuming the route cannot change it.
- Mido chest already open. Selected replacement `8838426083116998768`,
  **Zora River open-grotto chest**, `IsTreasureBoxOpen.<Hash>=false`;
  small chest, no event override, native child/adult copies. Well key chest
  `8397646530660039355` is also still closed if a further native key is needed.

Full measured keys/values and exclusions:
`E:/OOTRemake/work/r18-keys/fixtures/floor_report.json`.
Progress SHA256 `9da25b865f91f8ca53eab3a899685c8a56e34763d84b05b97865aa097f0fdeac`.
Copied only `slot_05` (progress + caption) plus the flat source's `account.sav` /
`option.sav` into `ingame/user-r18-keys-well-{main-control,candidate}-natural-v2`
under `save/5a3c9e1f0b7d24680000000000000001/`. Copy SHA256/readback matches,
exactly one progress slot per profile. **Copy edits: none.**
Proof: `ingame/well_selection-copy-proof.json`.

### Short Well route (split, estimates; unplayed)

- **Remote credit: 3–5 minutes per variant.** Teleport to Zora River's open
  grotto, open the retargeted chest, Save/Continue: Well held/found **1/1**, first
  key true; floor source/puzzle remain untouched.
- **Floor lifecycle/spend: 10–15 minutes per variant, continuing remote credit.**
  Walk from Kakariko into the drained well, main-floor west doorway to room 3.
  Solve the coffin/candlestick puzzle with the naturally held sword/sticks/fire
  (native candlestick death opens the coffin; exact action still unplayed).
  Leave the pickup, re-enter, Save/Continue: recovery. Collect: main adds one
  Well key, candidate adds 20 rupees and no key. Re-enter/reload: no duplicate.
  Spend a real key at either untouched chain lock; Save/Continue retains the
  remaining count while found count does not decrease.

Well v2 main-control/candidate packets read back **24 / 29 resources**. Both
updated launchers exit **0** in real rc.7 `cmd.exe` dry runs, selecting their
matching v2 mod and natural profile; `ingame/well-natural-dryruns.json`.

## Shadow floor hold — superseding scope

Claude: keep the Shadow Temple floor key vanilla this round, **built, held until
a natural pre-room save exists**. No Shadow preparation is handed to Kareem.

The read-only backup scan found no natural pre-room-13 snapshot. Longshot rc.7's
only Shadow teleport destination is `ShadowTemple_Arrive` (entrance), not an
arbitrary room. The closest natural adult/Hookshot/bombs snapshot is the same
2026-11-09 `slot_02` used by Fortress. Its two entrance-path key doors and the
room-12 silver-rupee shutter are closed; no single-value edit can produce the
needed state. Exact measured inputs and native destination/gate evidence remain
outside the repo in `fixtures/floor_shadow_teleport.json`.

Implementation: removed Shadow from `generate.key_families.FLOOR_SOURCES` and the
active floor reward palette. Across own-dungeon, small-key-anywhere and
all-anywhere, its world check stays `Collectable`, keeps its native Shadow key and
is never shuffled. Other ordinary Shadow chest keys retain their existing setting.
The isolated adapter and structural tests remain available for research, but no
seed option selects it. Settings UI/help and `docs/settings.md` name this hold.

Removed all Shadow play/preparation launchers, generated Shadow mod folders and
packet-owned Shadow user copies. No original/backup save was edited; no game was
started. Well/Fortress packets, source metadata and untouched natural copies remain.
The requested long preparation was **not played** and is not a scheduled check.

Focused post-hold contract proof:
`CLAWSHOT_WORKERS=1 uv run pytest tests/test_key_families.py -q`
→ **15 passed, 4.95 s**. Existing parameterized coverage now checks that Shadow
is native and absent from the shuffled checks in every exposed key mode.
The later sweep and single full gate must run on this no-Shadow head, after
`MAIN FINAL` and the assigned lock turn.

Post-hold native generation/writer smoke (own seed **180618**, small keys anywhere
and Fortress jail keys on) passed beatability and emitted **173 shuffled checks,
27 spheres, 116 resources**. All five admitted source rewards were red rupees.
Shadow remained native: source type `Collectable`, native Shadow key, not shuffled,
no new Shadow floor pack, no reveal-flow transform. Its native placed actor reads
back **unchanged**, even though ordinary shuffled chests rewrite the same Banc.
Proof: `E:/OOTRemake/work/r18-keys/no-shadow-smoke-proof.json`.

Actual isolated browser UI: Dungeon items' visible help states the Well/Fortress
scope and **“built, held until a natural pre-room save exists”** for Shadow.
Screenshot `E:/OOTRemake/work/r18-keys/held-shadow-ui-proof.webp`. Empty external
library and in-memory preferences only; own browser/server closed and throwaway
smoke scripts deleted. Targeted formatter: **4 files left unchanged**.
The staged packet CLI now rejects `--kind shadow` with exit **2**, so it cannot
accidentally recreate the withdrawn play packet.

## Switch polarity receipt (Claude's 09:37 steer)

**No F-authored Bool/pouch guard or new conditional algorithm.** Well/jail
retargets add no switches. Fortress named grants reuse main's existing
`add_grant_helper` and native-clone algorithm unchanged; the only new target is
the three `DungeonInfo.GerudoFortress` inventory leaves.

| Appended/reused switch | Cases | Evidence |
|---|---|---|
| `GetPouchContent/ClawshotKeyWasZero` | Int comparison: **0 less**, **1 equal**, **2 greater**. Comparing remaining keys with zero: 1→`ClawshotKeyOnce` then total/remaining increments; 0/2→increments directly. This is **not Bool polarity**. | Same helper on baseline `2ba2f9a`; native `GetPouchContent/Event10` compares its counter with 4: 0→Event19, 1/2→Event25. |
| 52 native-cloned switches listed below | Every original case value, query and parameters preserved. Each case goes to the corresponding native successor cloned in the same mode; no 0/1 inversion is authored. | Native original with the same `EventN` in the same flow; complete per-switch case/target receipt outside repo. |
| Pouch truth anchor (not added by F) | `ReplaceEquipmentForEraChange/Event12`, `Weapon_Shield_Deku`, Num=1: **0 held→Event8**, **1 absent→Event18**. | Read directly from the native flow; no new `EventQueryIsExistInPouch` or `EventQueryIsGameDataBool` node in F's emitted clone set. Bool comparisons retain **0=true, 1=false**. |

Every emitted cloned switch has prefix `Clawshot_GerudoFortress_content_` and
the following native event suffix (the original native switch is its example):

- `Dm_SY_TreasureboxSmall` (31): `Event50`, `152`, `125`, `17`, `6`, `108`, `159`,
  `116`, `198`, `197`, `21`, `30`, `54`, `33`, `48`, `47`, `57`, `118`, `101`,
  `46`, `66`, `96`, `70`, `168`, `58`, `111`, `177`, `171`, `203`, `185`, `204`.
- `GetPouchContent` (21): `Event67`, `86`, `79`, `99`, `85`, `78`, `60`, `56`, `4`,
  `73`, `70`, `52`, `36`, `10`, `26`, `41`, `29`, `17`, `87`, `88`, `89`.

Actual staged v2 candidate audit: **53 switches**, including the one reused
integer helper. All copied queries/parameters/case values match the original
native nodes. Full numeric case→successor maps and native counterparts:
`E:/OOTRemake/work/r18-keys/switch-polarity-proof.json`; no decoded flow dump is
vendored. The proof initially used the shorthand `ReplaceEquipment` as a file
name; the printed missing path was resolved to actual
`ReplaceEquipmentForEraChange.bfevfl.zs`, then the corrected proof passed.

Expanded the existing consumer regression to first key, already-held keys and
all-keys-spent states. It now asserts **after each pickup**, not only after four:
the very first zero→one grant must immediately set the first-key flag; found and
held counts grow independently; source, rescue, Spirit and other-dungeon state
stay untouched. This catches a wrong equal-zero case that a later pickup could
otherwise mask.

`CLAWSHOT_WORKERS=1 uv run pytest
tests/test_key_bindings.py::test_fortress_named_grants_only_credit_inventory_not_guard_or_rescue_state -q`
→ **3 passed, 0.45 s**. Scoped format check **1 file already formatted**; scoped
Ruff **All checks passed**. No gameplay/source/packet change was needed.
