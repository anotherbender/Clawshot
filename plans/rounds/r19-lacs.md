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

Pending current-main rebase, focused verification and the serialized gate lock.
Required recipes: the exact broad CS1 in `work/r18-fill/settings.txt` (200 seeds),
Defaults (50), Recommended (50), zero exhausted. No new option is being added.
External driver/receipts live under `work/r19-lacs/`; no game data enters Git.

## Handoff status

Implementation and initial focused/native proof complete; boss-key regression
review, natural-save result, final sweep/full gate and READY handoff pending.
