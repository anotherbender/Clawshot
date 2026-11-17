# R16 Water Temple safety gate

Branch: `r16/water-gate`, based on main `af6a7b4534e0864fe109cbbe3bece4f638cd1db2`.

## Approved decision and evidence boundary

Claude, 2026-11-17, precaution pending a played pre-Ice check; Kareem informed.
Claude's 0.2.2 decision requires the real Ice Cavern end-chest source before Water Temple entry, in addition to
Hookshot and Iron Boots. The basis is the cited tester video
showing a pre-Ice underwater Hookshot hit with no response, plus cs16c's conditional placement cycle.

This is a **logic safety constraint**, not a proved explanation of the native rejection or a runtime door patch.
No OOTRR source was opened or fetched.

### Played follow-up (Kareem, 2026-11-17)

- Build/setup: **rc.7, UNMODDED, fresh new game**. Debug made Link adult, supplied Hookshot and Iron
  Boots, and teleported him to adult Lake Hylia.
- Observation: submerged at the entrance, Hookshot **does not latch onto the switch target**.
  This is a failed latch, not an established accepted hit that the switch ignored.
- Boundary: this played Debug-made state is **consistent with the Ice gate**, not proof that the
  end-chest source or a particular quest step/flag is the exact predicate. Normal progression and
  a Clawshot seed overlay were not exercised. The precaution stands; native latchability needs tracing.

### Read-only native follow-up

- The target's physical collision shape already declares `Wall_StickHookshot` on one of its two
  cylinders: `Pack/Actor/Obj_LakeHrl_SwitchHit_A_01.pack.zs`,
  `Phive/ShapeParam/Obj_LakeHrl_SwitchHit_A_01__Physical.phive__ShapeParam.bgyml`.
  This proves a static material declaration, not that the live body is enabled or the shot contacts it.
- The retained placement audit found one Static target/shutter pair per age, no Dynamic copies,
  and no placement Presence/quest condition on either. The nearby Hookshot air wall instead uses
  `NOT WaterTemple_Room07_00` (the interior Longshot-chest state), not an Ice quest condition.
- `HyruleField_LakeHylia_Common_Prefab_6a9d` node6 defaults target Active/create to true and delete
  to false. Its declared BootUp/ForceControl inputs use the entrance demo/request and equipped-Boots
  state. The quest's `IsAfter Step05` path opens the shutter and writes the demo-played flag;
  **Step06 or later is therefore a confounded latch test**, not a post-Ice control.
- Target AINB node40, `ExecuteGimmickSetIsHitEffectiveAtackFlag`, takes the damage-query result,
  not a quest-step input. Its name is not evidence of a quest-driven latch-attribute toggle.
- A fresh read-only decode of `RSDB/GameSafetySetting.Product.111.rstbl.byml.zs` found Water safety
  rows with escape-range/area settings, not a declared latchability or collision toggle.

These data checks do not identify a quest/flag that changes native Hookshot latching.

The installed native function index has addresses/sizes without names, and the build no longer retains
lifted `code_*.c`; the latch implementation was not identified. The rc.7 source survey found no explicit
quest-driven Hookshot latch patch. This does **not** exclude a port/Debug-state contribution: rc.7 does
patch physics solver stepping (`nx2/oot_patches.py:602-609`). An unmodded observation alone cannot
distinguish native quest gating from those alternatives.

The retained native Ice wrapper sets `SageOfWater_GetWaterSerenade=true` in both branches, then writes
the saved `Step_SageOfWater` enum (native enum Hash `1443521711`):

| Ice completion branch | Step | Saved enum value |
|---|---|---:|
| No prior King Zora gift and no Zora Tunic | Step04 | 670458110 |
| Prior King Zora gift or Zora Tunic owned | Step05 | 1558058783 |

References: `SageOfWater` Event127/Event243 select the branch, Event284/Event285 set the source Bool,
and Event282/Event280 advance the quest. Enum values are from the native `Step_SageOfWater` definition,
not ordinal indices. Step05 is the latest pre-entry quest control; setting it alone is not the same
as executing the Ice source wrapper, and no success of a latch test is inferred from these writes.

## Changes

- `remake/adult_lake_hylia.toml` adds `Ice Cavern End Chest Access` in the real source's region. Its rule mirrors
  `Ice Cavern Iron Boots Chest` access (`ice_cavern.toml:91`), not the shuffled item. Physical source:
  `Banc/IceCavern/IceCavern_Static.bcett.byml.zs`, Hash `6859289214373847284`.
- Lake Hylia -> Water Temple Lobby requires that event AND usable Hookshot AND usable Iron Boots. No equipment,
  reward, quest-step initialization or native flow was changed. Junk chest/song rewards still permit the source.
- Existing Boot-substitution coverage supplies completed Ice history so it continues to isolate the physical
  Boots requirement. New checks cover early H+I/Serenade, junk rewards, the real end rather than Ice arrival,
  the separate Hookshot requirement and the cycle/repair.
- `docs/logic.md` and `plans/03-game-data.md` label the gate as a precaution and retain the unplayed boundary.

The regression uses the real copy-only world and reachability oracle for Chest/Gift, songs anywhere,
small keys anywhere and an open Door. Unrelated inventory isolates the cycle: Lullaby in Water's Map
Chest; both scale copies in its Central Pillar/Longshot chests;
Impa/diving/fishing donors give junk. An eleven-slot local permutation moves Boots/Hookshot outside Ice/Water
and preserves the item stock. The Water-approach goal rejects it; moving Lullaby to Mido's top-left chest makes
both the real Ice source and Water checks collectible. This is a local model counterexample, not a generated
bad seed or a claim that every settings combination has that cycle.

## Focused verification

All commands used `CLAWSHOT_WORKERS=1` while the game was running, as instructed:

```sh
CLAWSHOT_WORKERS=1 uv run ruff format --check tests/test_world_remake_adult_lake.py
CLAWSHOT_WORKERS=1 uv run ruff check tests/test_world_remake_adult_lake.py
CLAWSHOT_WORKERS=1 uv run pytest tests/test_world_remake_adult_lake.py tests/test_world_data.py::test_the_whole_world_is_ported tests/test_world_data.py::test_vanilla_placement_is_beatable
```

Results: one file already formatted; Ruff passed; **11 passed in 12.10 s**. The two world checks confirm the event
is defined/connected and the documented vanilla-placement oracle remains beatable.

A fresh Python process separately exercised the loaded world/Search without importing the tests:

- Early H+I+usable Serenade: no source, no Water access.
- Real end chest and Sheik both give junk: source earned, no Boots or Serenade granted.
- Actual earned source history carried to the Lake search with H+I: source count 1, Water reachable.

No game launch, native-file/output modification, full generation, seed sweep, full suite or dump gate was run.
Full gates are intentionally deferred to Claude after r16/time merges and this branch is rebased.

## Remaining acceptance

**Pending:** identify the native latchability condition and isolate it with a controlled quest/flag
change. Kareem's rc.7 unmodded Debug-state failure above is played evidence, not a normal-progression
or modded Clawshot certification. A modded check still needs build/overlay identity, quest/source/played
flags and the runtime's seed-resource loading proof. The logic guard does not itself change what the
physical switch accepts. No version bump is included;
Claude owns the combined 0.2.2 integration/release.

## rc.7 Debug capability and next played comparison

**No quest-step editor exists in rc.7 Debug.** The twelve Debug tools cover player/travel/camera,
inventory and time (`gpu/vk/vk_menu.cpp:1734-1766,1961`). Inventory's **Quest** section is a list of
quest items and songs, not quest progress (`gpu/vk/oot_cheat_items.h:73-93`).
Paths here are relative to the installed rc.7 `LongshotBuilder/tools` directory.

In `host/hos_main.c:767-777,807-820`, the Serenade toggle writes only the learned-song Bool
`0x3fa63986`, not source Bool `SageOfWater_GetWaterSerenade` (`0x85114ae5`) or a quest step.
The writer at `:1148-1160` is Bool-only. Thus **there is no Debug menu value to set for a one-step
latch proof**. Step05 (`1558058783`, `0x5cde171f`) is a native pre-entry control value, not an available
UI setting and not a proven latch predicate. The raw-memory bridge is not a quest editor; no memory
write, save edit or runtime patch was attempted or proposed as this read-only follow-up.

The next non-invasive played comparison is to retain the same Debug-made adult/equipment state,
complete the **real Ice Cavern end-chest story sequence**, return to adult Lake Hylia, and repeat
the same submerged shot. Record whether it latches and whether the entrance demo starts/bars open.
A changed outcome supports the precaution, but changes a story-state bundle plus scene loading;
it does not isolate a particular quest step, source Bool, song Bool or collision attribute.
Do not substitute Debug's Serenade toggle, or Step06+/entrance-demo initialization, for the source.

If the existing read-only control bridge is already enabled, its `oot` subscription can watch
`Step_SageOfWater`, `SageOfWater_GetWaterSerenade`, learned-song Bool `0x3fa63986`, and
`HavePlayedEvent.Dm_WaterTemple_0000` before/after that comparison (`host/oot_state_tap.c`).
No game or Debug action was performed by the investigating agents.

## Approved stacked integration (2026-11-17)

Claude signalled the rebase onto `r16/minimap` `c6f550961935129df040374f9370ef688586224e`, which is
above `r16/time` `ef0d9321b3d0d8734850204f760e8f59ccb8995f`. The single Water commit replayed cleanly;
no production rule or test changes were needed.

Post-rebase focused tests: **11 passed in 8.71 s**, using `-n 4` and `CLAWSHOT_WORKERS=1` because
Longshot was present at stage start. The old vanilla-oracle node ID had been renamed by the base:
the first selection returned no tests; collect-only printed the missing ID, then the corrected
selection below passed. No unchanged failing command was rerun.

```sh
CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 4 tests/test_world_remake_adult_lake.py tests/test_world_data.py::test_the_whole_world_is_ported tests/test_world_data.py::test_all_other_vanilla_checks_with_keys_and_an_escape_tool
```

This supersedes the earlier full-gate deferral. Claude authorized **one** complete gate on the frozen
stacked head, serialized under `work/rounds/r16/gate.lock`: format, lint, full synthetic, full dump.
Each stage checks both `longshot.exe` and `hookshot.exe`. Either present means `CLAWSHOT_WORKERS=1`
and pytest `-n 4`; otherwise synthetic uses workers12/`-n 12`, dump workers4/`-n 12`.
Dump inputs are the real romfs/NUP and the same extended fixture used by the successful v5 stack:
`OOT_DUMP=E:/OOTRemake/work/rounds/r16/time-layered-dump`, not the older pre-time working set.
Synthetic clears all three dump-input variables.

The exact frozen head/tree, tracked-file hashes, stage commands/process snapshots/logs and results
are external evidence under `E:/OOTRemake/work/r16-water-gate/stack-c6f5509-single-gate-v1/`.
No source, tests or documentation will change after this pre-gate evidence commit is frozen.
READY is a gate handoff only: **merge waits for Kareem's v5 result and two-minute minimap check**.
