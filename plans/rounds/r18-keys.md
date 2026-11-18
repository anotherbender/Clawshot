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
