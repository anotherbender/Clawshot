# Round 17 Track A: bug fixes

Agent cs17a (`openai-codex/gpt-6.1-sol`), branch `r17/bugs`, base `fcd5f2a`.

## Evidence and causes (posted before rules)

Kareem, 2026-11-17: warp songs work indoors; child Bolero arrival cannot walk out of Death Mountain Crater. Child Requiem/Colossus remains **unplayed**, not a confirmed physical trap. No game is launched by this track; no player's seeds or saves are read or changed.

1. Translated `root.toml`: Bolero dispatcher enters `DMC Central Local` unconditionally. Its child exits reach only `DMC Central Nearby`; walking exits to upper/lower crater and Fire Temple require adult. `child_death_mountain_crater.toml` changes the scrub reward, not that arrival. Fill could therefore count child warp-pad rewards without any escape. No proven child walking exit is added.
2. Requiem dispatcher likewise enters `Desert Colossus` unconditionally. The modeled reverse desert is not evidence of a child walking escape in this remake. Treat it conservatively until played.
3. `world.softlocks.reachable_traps` reverses only explicit physical edges. Song dispatchers have no incoming edges from indoor rooms, so held usable songs were not counted as returns. Kareem's new played indoor-song fact permits these diagnostic edges; Farore's Wind ownership still proves no saved point.

Cause list posted to `cs-r17` before changing logic; Claude accepted it. Both child arrival guards now require a playable safe-destination warp (Minuet, Serenade, Nocturne or Prelude), not the other unresolved arrival, not a song obtained at the destination itself. Rules live in `remake/child_warp_returns.toml`; translated data is untouched. The checker reuses compiled `Root Exits` rules through `softlock_warp_regions`, including indoor rooms, never a spawn or Farore point.

## Integration boundary

Claude explicitly authorized the item-3 docs-only merge of `r17/child-sword` (`7308a83`); merge commit `806ad8c` precedes implementation. No main merge or push. `patch/equipment.py` inserts three nodes after the original Event8 wait and before Event0: compare incoming candidate, query pouch ownership, clear only an unowned `Weapon_Sword_Kokiri` candidate. No age/quest/ownership grant, no shield/timing change, no other fallback. All seed compilers include it, with free time travel on or off.

## Pending in-game questions

**Kareem: can child Link walk out of the Requiem/Desert Colossus landing, without using any warp song? One minute: attempt the reverse desert route; stop after a minute rather than taking a long detour. Until answered, logic requires an already usable safe warp.**

**Child sword guard check (three minutes, after Claude boot-check): fresh new game, no Kokiri Sword ownership, early sword pull and return to child: nothing equipped. Then obtain the real Kokiri Sword and confirm equip/attack works. Use an empty isolated save folder; no inventory or quest cheats.**

### Staged packet and isolation

`E:/OOTRemake/work/r17-bugs/ingame/Test - child-return-colossus.bat`, checklist `ingame/checklist.md`, controlled own recipe **170032**. Built through `make_seed`/`write_seed` (111 resources), **not a certified solo seed** because it uses explicit experimental placements. Current Longshot template resolves `builds/*/bin/longshot.exe` (installed rc.7), clears HOS_FS_OVERLAY and selects exactly `mods/child-return-colossus/child-return-colossus/romfs`. Empty isolated `user-child-return-colossus/save`; no account/options/progress copied. Claude must boot-check; this track did not launch a game.

Three Mido kit chests give Time Ocarina, Minuet and Requiem; the native KF sword chest stays Sword and is left unopened until after return. Six serialized child/adult kit actor copies were independently read back; the written native sword chest retains `Item_Sword_Kokiri` and `Get_StoneOfForest_GetSword`. Written equipment guard was decoded and checked; launcher dry-run passed. Native Temple destination coordinates are in the external checklist. Three-minute sword interaction and one-minute Colossus route attempt exclude setup/loading; no inventory/quest/age cheats.

Required game proof: `mods: Event/EventFlow/ReplaceEquipmentForEraChange.bfevfl.zs <- <this packet path>` plus the actual unowned-empty and owned-usable results. Colossus needs an actual child route/barrier observation. Neither code/test output nor a pickup model counts as played acceptance.

## Output/default changes

No preset/setting defaults or version changed by this track. Always-on safety changes apply to **newly generated output**, including Token-off Defaults: child Bolero/Requiem arrival frontier is stricter, so placements can cascade; every new seed also contains the sword guard. Existing seeds/saves are not rewritten or repaired.

First Play now copies Longshot's `longshot_options.ini` as well as option/account saves, **only when creating the seed user**, never overwriting an existing seed file. Launcher detection previously selected a build directory with no `user`; copying now follows the launcher's actual shared user root, fixing `.sav` inheritance too. Hookshot gets no new ini behavior. Portable Windows: `<launcher-data>/user`; installed Windows: `%APPDATA%/Longshot`; Linux: `$XDG_DATA_HOME/longshot` or `~/.local/share/longshot` (portable AppImage home supported). Standalone ini stays sourced beside the game. Files are read-only sources; progress slots are never opened. Facts-only sources: Longshot `host/options_path.c` / README *Where the files go*; LongshotLauncher `Core/MakeGameCommand.cs` (`GamePlay.UserFolder`), `Core/Saves.cs` (`SaveEnvironment.LongshotUser`), `Core/LauncherHome.cs` (`PortableUser`, `Resolve`). No GPL code copied.

Tracker stock already appeared on every surface. Skulltula source completion only appeared within mixed area totals, omitted by compact OBS. New `skulltula_checks = {collected,total,unknown}` stays separate from token stock and is shown in the Collection/quest section on the tab and labelled/compact OBS. Token-off has no extra display; no preset or save-format change.

## Verification

### Failing-first and narrow proof

- Warp regressions first observed child landings collecting their own escape: Bolero `DMC Child Red Rupee 1`, Requiem `Sheik at Colossus`. Instrument-less arrival also passed incorrectly. Indoor checker failure printed reached rooms despite a held age-usable Prelude. The tiny fill fixture's first two setup errors (invalid hints value, leftover shop-price rules) were printed and corrected, not called product failures. After fixes: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_softlock_warps.py -q --tb=short`: **27 passed**. Covers all four safe songs and their real graph return certificates, no instrument, both hazardous songs together, Farore-only, destination-owned escape, indoor age permissions, successful fill placing escape outside before required destination progression, and refusal when the only escape song is behind its own landing.
- `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest tests/test_child_sword.py -q --tb=short`: failing first through actual `make_seed` composition, `EquipWeapon = Weapon_Sword_Kokiri` with no pouch ownership. After: **16 passed** (synthetic and native). Actual default-seed compiler path is covered; native full-entry fallback and saved candidates are compared with native effects, owned Sword/Master/other/empty candidates preserved, no ownership changes. Written transform round-trips and fails closed on changed anchors/double application.
- Runtime first: **14 failed, 45 passed, 1 skipped**, printing empty copy lists for launcher roots and absent ini carry-over. After: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_pack_options.py tests/test_pack_loader.py tests/test_ui_games.py -q --tb=short`: **59 passed, 1 skipped**. Windows portable/installed, Linux/AppImage, standalone, missing ini, Hookshot, creation-only and never-overwrite behavior; no real game launched.
- Tracker first: **2 failed, 17 passed**, missing backend source count and text on four rendered surfaces. After: `CLAWSHOT_WORKERS=1 uv run pytest tests/test_tracker_tokens.py tests/test_tracker_options.py -q --tb=short`: **19 passed**. Own native seed **17005** (`Chest Token`, 265 checks, 100 Skulltula sources) at `E:/OOTRemake/work/r17-bugs/tracker-tokens/seed-17005`; browser uses an explicitly synthetic save: five completed sources, one partial/unknown, token stock three. New app tab and OBS tabs were observed before/after; final tab and icon-loaded labels-off compact view show `Gold Skulltulas 3` separately from `Skulltula checks 5 / 100 (1 unknown)`. Compact line visible in 264px content at 290px viewport; no horizontal scroll. Screenshots: `tracker-tokens/shots/fixed-tab-collection.webp`, `compact-icons-collection-290.png`; servers/tabs closed. No player saves read.

### Full gate

One serialized final gate remains pending. `OOT_ROMFS=E:/Games/Hookshot/romfs`, `OOT_NUP=E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup`, `OOT_DUMP=E:/OOTRemake/work/rounds/r16/time-layered-dump`. No working-set file added: existing `Event/EventFlow/*.bfevfl.zs` cache pattern already includes `ReplaceEquipmentForEraChange`; checked that exact file is present in the supplied layered fixture.

Stage-start tasklist controls worker caps; game was running during narrow proofs, so all used `CLAWSHOT_WORKERS=1`. Heavy work waits for atomic owned `E:/OOTRemake/work/rounds/r17/gate.lock`; no other agent's lock removed.
