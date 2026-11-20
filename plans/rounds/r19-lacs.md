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
- Research `probe_scene.py`, external `scene-probe.json` records the native grant
  and last-sage reader values. No decoded game data is committed.
- No new output resource paths: existing Gift scene and native writer only;
  no pack-manifest or layered-dump additions required.

## Natural save / controlled play check

Read-only survey in progress. No played result is claimed. If no natural adult
snapshot with Spirit+Shadow awakening scenes complete and LACS still pending exists,
record that absence rather than clearing story history or inventory to fabricate one.

## Sweep and final gate

Pending current-main rebase, focused verification and the serialized gate lock.
Required recipes: the exact broad CS1 in `work/r18-fill/settings.txt` (200 seeds),
Defaults (50), Recommended (50), zero exhausted. No new option is being added.
External driver/receipts live under `work/r19-lacs/`; no game data enters Git.

## Handoff status

Implementation and initial focused/native proof complete; boss-key regression
review, natural-save result, final sweep/full gate and READY handoff pending.
