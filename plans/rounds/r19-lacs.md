# Round 19 — lacs (cs19g)

Branch `r19/lacs`, base `d9deb65`; model `openai-codex/gpt-6.1-sol`.
Research/output only: `E:/OOTRemake/work/r19-lacs/`. Dump read-only.
No game started, runtime folder written, personal seed opened or original save changed.

## Product contract and findings

Kareem, 2026-11-19: Ganon's Castle boss key follows the other boss keys;
the Temple Light Arrows scene is an ordinary late check, never a special boss-key award.
No new option and no version bump.

### Ganon boss-key modes

`vanilla` is **not** an offered `dungeon_items` value on main. The CLI/app offer
`own_dungeon`, `anywhere`, `all_anywhere`; validation refuses literal `vanilla` with
the supported choices. Vanilla chest behavior means leaving `Chest` unshuffled.
Do not add a fourth setting or reinterpret existing recipes to answer a naming mismatch.

| Mode | Ganon boss key on main | Other boss keys | Change needed |
|---|---|---|---|
| Vanilla / Chest not shuffled | Native Tower boss-key chest | Native source chests | None |
| `own_dungeon` | Shuffled within physical Ganon's Castle/Tower Banc | Shuffled within their own physical dungeon | None found |
| `anywhere` | Still Castle/Tower only; this mode releases small keys only | Still their own dungeon | None found |
| `all_anywhere` | Released to supported shuffled chests, including overworld | Same release to supported shuffled chests | None found |

Evidence: `world/model.py` includes `GanonBossKey` in dungeon-item types;
`world/load.py` derives `Ganons Castle` from its item name;
`remake/extra_ganon_tower.toml` attributes Tower to that dungeon;
`generate/fill.py` `is_restricted`, `allowed`, `shuffled_locations` and the dungeon
stage order include Ganon's key in the same policies as ordinary `BossKey`.
The native field remains `DungeonInfo.InsideGanonCastle.IsGetBossKey`.
No fill/prepare edits or new boss-key grant mechanism are needed.

### Light Arrows gift and native readers

Already shuffled by Gift on main: `gift_rules.toml` class `swap`, census identity
`Dm_TimeTemple_0130/Event85`, vanilla actor `Item_Arrow_Light`, world `Cutscene`.
The native `GetPouchContentByActorName` wrapper gives the placed actor; no source
adapter, extra saved flag or special boss-key assignment is required.
The existing Light Arrows gift-only hold remains unchanged; this does not invent
chest support or admit dungeon items to ordinary gifts.

The bug was **logic**, not a missing shuffled location: with rewards vanilla and
vanilla bridge, the model still asked for five owned medals and for owned Light
Arrows at the bridge. Reward shuffle/count bridges already used native completion.

Changed `remake/adult_temple_of_time.toml` to apply in all modes:

- LACS: adult plus completed Shadow and Spirit awakening routes, represented by
  existing `Defeat Bongo Bongo` / `Defeat Twinrova` completion events.
- Separate `Clawshot Light Arrow Story` event at Temple of Time with that trigger.
- Vanilla rainbow bridge follows that story, independently of its gift's identity.
- Removed duplicate conditional LACS/story/vanilla-bridge rules from
  `dungeon_rewards.toml` and `generate/rewards.py`. Explicit count bridges retain
  their unique owned-reward predicates.
- Six trial-clear rules and the finale still require **usable Light Arrows**;
  Castle Tower still requires six trial completions and its own boss key.

Native evidence: `AllSage/Event25,26` read
`HavePlayedEvent.Dm_Awake_Spirit` AND `.Dm_Awake_Shadow`, not medals;
EscapeDungeon `Event130/139` dispatch the last-sage sequence;
`Market_Adult_Prefab_c668` requires AllSage Step02;
`AllSage/Event10,11` complete the story and advance Defeat_Ganon Step01;
the bridge module `_14ba` reads that stage. The trial-core Light-element damage
contract is recorded in `r18-rewards.md`. Those resources/writes are unchanged.
No `Defeat_Ganon` transform was added (sword owns its finale guard).

## Focused proof

- `CLAWSHOT_WORKERS=1 uv run pytest tests/test_world_remake_adult_time.py
  tests/test_dungeon_rewards.py -m 'not dump' -q`:
  **78 passed, 1 deselected**, 22.92 s pytest time.
- `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest
  tests/test_lacs.py -m dump -q`: **2 passed**, 33.91 s.
  Production Gift setup admits the check with rewards both on/off. Swapping it to
  Boomerang and restoring only Event85's ActorName yields the entire original
  native event tree: every branch, binding, timeline and flag write is preserved.
  Gift output does not touch AllSage or add GameDataList state for LACS.
- Same explicit Gift diagnostic assignment built using actual local main
  `d9deb65` imports and candidate imports: **all 24 decompressed resource outputs
  byte-identical**, including the LACS scene. Receipt `parity-main.json` /
  `parity-candidate.json`. Only the world rule differs. This is not a whole-seed
  comparison and not an in-game result.
- Actual CLI `uv run python -m clawshot --dungeon-items vanilla --print-settings`
  exits **2**, naming `own_dungeon`, `anywhere`, `all_anywhere` as valid choices.
- Scoped Ruff format/check on the four changed Python files: **pass**.
- Research `probe_scene.py`, external `scene-probe.json` records the native grant
  and last-sage reader values. No decoded game data is committed.
- No new output resource paths: existing Gift scene and native writer only;
  no pack-manifest or layered-dump additions required.

## Natural save / controlled play check

**No qualifying natural late pre-LACS save exists in the permitted archives.**
Read-only `scan_late_saves.py` decoded **2,787 files / 693 distinct contents**, zero
parse errors; excluded every path with a seed-named component. No file has AllSage
Step02. All 102 files with Shadow/Spirit awakenings have both, but already have
LACS history true, Light Arrows owned and AllSage Complete. Since the round18 survey,
311 additional files in 103 backup folders are all test-round backups, not new
natural playthrough snapshots.

Closest natural pre-LACS family: `save-backups/2026-11-11_2050-main-after-water`
(all six slots), adult, Forest/Fire/Water awakened, Shadow/Spirit Ready, no Light
Arrows and LACS unplayed. Reaching a real LACS-ready save requires playing both last
temples and saving before returning to the Temple of Time; no short time estimate
is claimed.

The natural r17 chest-hunt snapshot
`2026-11-17_213402-r17-chest-hunt-main-save-1/.../slot_02` has the Tower boss-key
chest closed, no Ganon boss key, all six trials cleared and both last sages done,
but LACS already played. The survey read every Castle chest through
`save.flag('IsTreasureBoxOpen.<Hash>')`; Tower Hash `17092385671602176550` false,
the other eleven true in that exact slot. It is unsuitable for a LACS comparison.

No paired launcher is fabricated, no story/inventory/era edits are applied and no
non-discriminating packet is presented as a LACS check. The existing runtime Gift
packet is identical to main; this track changes only modeled logic and adds
regressions, so it requires no **new game-behavior** play gate. A future LACS
acceptance check must use **Longshot 3.0.0**, a genuine pending-scene save, matched
main/candidate assignments, load-log proof and saved reward/story/reload checks.
External provenance: `save-survey-findings.json`, `save-survey-summary.json`,
`save-survey.json`. **Nothing was played.**

## Sweep and final gate

Rebased onto current local main `d9deb65` (`git rebase main`: already up to date).
Post-rebase locked focus on implementation head `471901008ecdfb62cfae62faa0bf7236ccd454d5`:
**134 passed / 4 deselected** synthetic (24.57 s), **2 passed / 2 deselected**
native (22.03 s). Includes ordinary/Ganon boss-key source admission and generated
placement parity regressions, LACS trigger, bridge, trials/finale and reward contracts.

Locked native-prepared sweep: **300/300; zero exhausted**, 410.72 s wall time.
No new option or recipe modification. Same production Gift/scrub/floor/chest
setup, source-contract restrictions, ordinary fill retries and beatability oracle.

| Recipe | Passed | Exhausted | Maximum attempts |
|---|---:|---:|---:|
| Exact broad CS1, `work/r18-fill/settings.txt` | 200 | 0 | 3 |
| Defaults | 50 | 0 | 1 |
| Recommended | 50 | 0 | 2 |

Broad seeds include `2306988613`, `12345`, and `19070000..19070197`;
Defaults `19071000..19071049`; Recommended `19072000..19072049`.
Receipts `sweep-results.json`, `sweep-rows.jsonl`, `sweep-gate-results.json`,
`gate-focused.log`, `gate-focused-native.log`, `gate-sweep.log` under
`E:/OOTRemake/work/r19-lacs/`. No game running at each stage start;
12 workers; own token lock released after the sweep. Subsequent changes are
round-record evidence only, not implementation or tests.

The **one full gate** runs on the final committed merge head, with per-stage
`tasklist` and token-owned `work/rounds/r19/gate.lock` serialization:

1. `uv run ruff format --check`
2. `uv run ruff check`
3. `CLAWSHOT_WORKERS=12 uv run --with pytest-xdist pytest -n 12`
4. `CLAWSHOT_WORKERS=4 uv run --with pytest-xdist pytest -m dump -n 12`

If a game runs, both pytest stages use `-n 4` / workers1 instead. Native inputs:
`OOT_ROMFS=E:/Games/Hookshot/romfs`,
`OOT_NUP=E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup`,
`OOT_DUMP=E:/OOTRemake/work/r18-issue34/combined-layered-dump` (read-only).
No working-set additions. The exact-head results and durations are retained in
`full-gate-results.json` plus `gate-{format,lint,synthetic,dump}.log`;
the completion thread handoff reports their observed counts, not an assumed pass.

## Handoff status

Implementation commit `65804b12fd`; runtime/save evidence `471901008e`;
this final record adds sweep proof only. **READY (merge)** is authorized only
after all four final gate stages exit0 on the exact head named in the completion
post. No in-game acceptance claim: no qualifying natural pending-LACS save exists,
and the existing scene/Gift resource packet is byte-identical to main. No new
game-behavior patch needs a play-held merge; changed generated placements still
depend on the ordinary oracle, not a claim that a full playthrough was observed.

## MAIN MOVED — f5c679d rebase and replacement gate

Claude's 2026-11-20 steer supersedes the initial d9deb65 READY receipt above.
Rebased onto `f5c679d` (0.2.3 release candidate). The sole conflict was
`docs/settings.md`: kept main's newly played reward/bridge/closed-Door evidence
and this track's ordinary-Gift LACS paragraph, removing the stale blanket
"built, not played" statement for the round18 options. Main's withdrawn
`skippable_story` implementation and validation refusal stay intact.

Main's `generate/fill.py` delta only rejects enabled `skippable_story`; no fill
ordering, destination policy, world logic or LACS implementation changed in
the rebase. Per Claude's steer, the recorded 300/300 zero-exhaustion sweep is
retained, not repeated for release documentation/version/validation changes.

The rebased focused set and **one replacement full gate** have separate receipts
under `E:/OOTRemake/work/r19-lacs/f5c679d-regate/`; the original gate logs remain
unchanged. Commands, native inputs and process-based worker limits are the same
as above. The completion thread must name the rebased exact tested head; the
old `ed5054a789` READY no longer authorizes merging.

Full-gate acceptance follows the round19 rule: retain any original UI/Node
deadline failure and load evidence, then require that exact node to pass
isolated before accepting it; never silently relabel an exit1 suite as exit0.
No timeout widening or unrelated implementation change is authorized here.
Merge remains blocked until 0.2.3 is published. No new in-game claim or save
fixture is introduced by this rebase.

## Accepted native-chain proof and merge — 2026-11-20

Claude accepted the complete event-data chain and merged `c7dbc2b6` into main
as merge commit `fa9d7ac`; main's intervening commits were documentation-only.
**Lacs DONE. Static event data, no played minimum.**
The following is the accepted proof, not an in-game two-sage-route claim.

Native citations (paths below are relative to the read-only RomFS):

- `Event/EventFlow/DoorOfTime.bfevfl.zs`, Event101 (first-pull Rauru scene) ->
  Event96 boots `Market_Adult_AllSage_Start`.
  `RSDB/EventSetting.Product.111.rstbl.byml.zs`, that row, maps directly to
  `AllSage:Market_Adult_AllSage_Start`.
- `Event/EventFlow/AllSage.bfevfl.zs`, first-adult entry:
  Event9 -> Event0 -> Event2 -> Event74 -> Event153 -> Event1 ->
  **Event18 writes AllSage Step01** -> Event19 initializes SageOfForest Step01.
  No branch requires Forest, Fire or Water completion. The Forest write is
  initialization, not a completion prerequisite.
- `Event/EventFlow/Dm_SY_BancChange_EscapeDungeon.bfevfl.zs`, Shadow sage-room
  path Event301 -> Event127 -> Event111 (awakening) -> Event126 (reward) ->
  **Event130**; Spirit path Event302 -> Event144 -> Event133 (awakening) ->
  Event143 (reward) -> Event141 -> Event177 -> **Event139**.
  Both dispatch `SageRoom_Allsage_LastSage`, without other-sage or count tests.
- EventSetting row `SageRoom_Allsage_LastSage` maps directly to
  `AllSage:SageRoom_AllSage_LastSage`. Its entire entry is
  **Event25** (`HavePlayedEvent.Dm_Awake_Spirit`) true ->
  **Event26** (`HavePlayedEvent.Dm_Awake_Shadow`) true ->
  **Event8** (`Dm_SageRoom_0010`) -> **Event20 writes AllSage Step02**.
  The intervening movie and its Effect/Env child timelines contain no state
  queries; their registrations add no Forest/Fire/Water eligibility condition.
- `Logic/Market_Adult_Prefab_c668.logic.module.ainb`, nodes0-4:
  AllSage Step02 plus Player contact requests the Light Arrows scene.
  No medal, Prelude, awake-count or other-sage input exists in that module.
- Forest Event199/208 and Fire/Water Event291/292 with Event306/307/308/311
  in EscapeDungeon belong to separate intermediate quest-log branches, not
  predecessors of the last-sage entry. Spirit's awake-count decrement,
  Event267, occurs after its last-sage dispatch Event139.

Full read-only inspection record:
`E:/OOTRemake/work/r19-lacs/LACS-STEP02-CHAIN.md`.
The five-temple guide route is sufficient, not the minimum event predicate.
No implementation change, replacement sweep, gate or game run was needed for
this accepted proof. This follow-up changes only the round record.
