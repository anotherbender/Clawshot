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
- Well and Shadow floor keys: join the existing small-keys-anywhere modes if their
  source contracts can be preserved. Own-dungeon mode retains them unchanged.
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

Small-key-anywhere output changes by admitting the two floor sources. The jail
option changes its pool only when enabled. Both release modes now refuse Chest-off
recipes rather than silently offering keys with no named-grant destination.
Defaults and Recommended keep own-dungeon mode and jail keys off; no version bump
was made (maintainer-owned). The stable native source names also replace the four
unlinked torch-named key checks in the model.

## Staged Longshot checks (unplayed)

Packets are focused diagnostics, **not generated/beatable seeds**. Built by the
same external `stage_packets.py` against actual main `2ba2f9a` and candidate
`5d5dae738b`; all emitted chest bindings and resources read back. No inventory,
quest, rescue, source-collection or game-start defaults are patched.

| Family | Launcher under `E:/OOTRemake/work/r18-keys/ingame/` | Main control / candidate |
|---|---|---|
| Well | `Test - well - main-control.bat`, `Test - well - candidate.bat` | Both give one named Well key in Mido's top-left chest. Main floor pickup remains a key; candidate floor pickup gives 20 rupees, no additional key. |
| Shadow | `Test - shadow - main-control.bat`, `Test - shadow - candidate.bat` | Both give one named Shadow key in Mido's top-left chest. Main skull-pot pickup remains a key; candidate gives 20 rupees, no additional key. |
| Fortress | `Test - fortress - main-control.bat`, `Test - fortress - candidate.bat` | All four Mido chests. Main can encode only its existing generic chest key: no Fortress target/credit. Candidate names and credits four Fortress keys; guard floor rewards give rupees instead of extra keys. |

The Fortress control limitation is intentional and explicit: main has no
`shuffle_hideout_keys` option or named Fortress target. It is its native generic
chest-key path, not a fabricated main target write. Its guards retain their native
keys. The paired checks expose the missing family support, not an invented claim
that vanilla guard keys themselves were broken.

Each launcher is adapted from the current Longshot template (including current
`builds/channel/version/bin` layout), selects exactly one real mod folder,
clears `HOS_FS_OVERLAY` and uses a separate packet-owned user folder. Actual
`CLAWSHOT_DRY_RUN=1` via `cmd.exe`: **all six exit 0**, selecting rc.7; proof
`ingame/launcher-dryruns.json`. No game start/boot performed.

**Fixture status:** only empty packet-owned users are staged at present. Requested
approved natural pre-source save copies on the thread; none opened or edited.
Short checks need copies with source uncollected, the relevant age/tools/story
state reached naturally, and the packet's Mido chests unopened. Claude must supply
or approve those copies and boot-check before handing the short route to Kareem.
The empty users are safe new-game launchers, not a claim that those prerequisites
have already been reached. From new games the full natural-age/quest routes take
hours; no short estimate applies without the fixture.

### Acceptance checklist

Run each control first, then start the candidate from an independent copy of the
same pre-check snapshot. Do not reuse the control's progress. Teleport/clock only;
no age, inventory, quest, guard-defeat or source-collected cheats.

1. **Remote credit** (2–4 minutes per prepared pair). Open the indicated Mido
   chest(s), confirm target-named text on candidate keys, save and Continue.
   Enter the target naturally or via the allowed teleport and inspect its key
   counter. Well/Shadow both controls and candidates add one to the target.
   Fortress main generic keys must not credit Fortress; candidate adds exactly four.
   No source-collected/carpenter/card completion may appear from remote credit.
2. **Well floor** (5–10 minutes per prepared pair). Reach the native room-3
   source with the puzzle still unsolved. Solve it. Leave the reward uncollected,
   leave/re-enter and Save/Continue: it must recover. Collect it: main adds the
   native Well key; candidate adds 20 rupees, not a key. Re-enter and reload again:
   no duplicate. Spend a real Well key at an unopened native lock; save/reload
   retains remaining/found inventory separately.
3. **Shadow floor** (5–10 minutes per prepared pair). With bombs, break the
   native large skull pot in room 13. The reveal must finish (`Act_Pop`/`Rotate_Obj`),
   not hang. Repeat the uncollected recovery and collected no-repeat checks above.
   Main gives a key; candidate gives 20 rupees and leaves the key count unchanged.
   Spend a native Shadow lock key and reload; no extra grant appears.
4. **All four Fortress guards/rescues** (15–25 minutes per prepared pair).
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
5. **Loading proof and saved values.** Record `mods: <resource> <- <packet path>`
   for the Kokiri chest Banc and candidate source resources:
   Well/Shadow native Banc plus generated `Obj_Dungeon_SmallKey_Floor_<area>` pack;
   Shadow additionally `Event/EventFlow/ShadowTemple_Gimmick.bfevfl.zs`;
   Fortress the four `Obj_Dungeon_SmallKey_GerudoFortress_0N.pack.zs` files.
   Check target `SmallKeyNum`, `SmallKeyTotalNum`, `IsGetSmallKeyOnce`, source
   collection Bools and carpenter counters/Spirit step on the packet's saved copy.
   Models/text/HUD alone are not ownership or once-only proof.

With all prerequisites prepared: **45–80 minutes for all three control/candidate
pairs**, including all four rescues twice, reloads and loading/save inspection (estimate, not measured).
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
