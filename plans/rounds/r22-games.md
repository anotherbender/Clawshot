# Round 22 games (cs22f)

Branch `r22/games`, base main `2091387` (0.2.7). Work and decoded research:
`E:/OOTRemake/work/r22-games/`. Nothing has been played by this agent; all changed game behavior is
**built, not played**, pending Kareem on **Longshot 3.2.0**. No game boot or writes to game folders/saves.

## Scope and decisions

- Kareem requests `LW Ocarina Memory Game`'s prize on the first won round, once, in every seed,
  shuffled or vanilla; later sessions retain native behavior. No setting for this timesaver.
- `bombs_without_bracelet` is a default-off boolean logic override, using the existing `free_time_travel`
  UI/schema convention (no second settings mechanism). CLI: `--logic bombs_without_bracelet=true`.
  Only bag bombs lose strength; bag capacity, Bomb Flowers and Bombchus remain separate.
  cs22b owns Bombchu helpers; contract posted on `cs-r22` (2026-11-24).
- Starter uses .NET SHA-256 rather than module-dependent `Get-FileHash`.
- UI replies quietly drop client disconnects; application OSErrors still return 400 (item 4, merge-kind).
- Scope confirmed by Claude relaying Kareem's ask, **2026-11-24**: first-win applies in every seed,
  including Defaults without Gift and an unchanged vanilla Heart Piece. Supersedes the initial Gift-only
  interpretation; one always-on transform now precedes gift substitution and its bag guards.

## Public facts and provenance

Read only Goggles of Truth's public README and CHANGELOG (no code):
[README, Quality of Life](https://github.com/AbyssDragonModding/Goggles-of-Truth/blob/main/README.md#quality-of-life)
lists optional Bag Bombs without Goron Bracelet, and an always-on one-song Lost Woods game.
[CHANGELOG, 0.7.0 Added](https://github.com/AbyssDragonModding/Goggles-of-Truth/blob/main/CHANGELOG.md#070---2026-11-21)
describes giving all three rewards and raising session length to 8; that is not our requested behavior
(first shuffled reward, later sessions native). The changelog also records the option's rename to
`bag_bombs_no_bracelet` in 0.6.0 Changed. These are external feature facts, not our in-game evidence.

Before tracing, read sloperinaGZ's GPL facts-only `docs/FINDINGS.md`, local copy
`work/refs/sloperina-FINDINGS.md`, section 1 Memory and save data / GameData and section 2 Game files:
GameData is hashed typed fields; actor/event data supplies the native trigger chain. No implementation copied.

## Starter SHA-256 (complete)

`scripts/start-windows.ps1` streams the archive through `System.Security.Cryptography.SHA256`, converts its
bytes to lowercase hex and disposes the stream and hasher in `finally`. The pinned digest, mismatch refusal,
check-before-unpack/run ordering, and cleanup are unchanged. Removed the obsolete source-text test pinning
`Get-FileHash`; `tests/test_ui_bootstrap_windows.py` exercises the real installer offline with a synthetic
compiled executable in a synthetic zip, correct and corrupt digests, normal and PS7-only module paths.

Verification:

- `CLAWSHOT_WORKERS=1 uv run --offline --with pytest-xdist pytest -n 2 tests/test_ui_bootstrap.py tests/test_ui_bootstrap_windows.py tests/test_ui_release.py`: **14 passed** (4.01 s).
- Built the actual release ZIP with `clawshot.ui.release.build`, extracted independently into
  `work/r22-games/starter-release/clean-normal/Clawshot-0.2.7` and `clean-ps7/Clawshot-0.2.7`.
  Windows PowerShell **5.1.26100.9818**, `-NoProfile`: each ran the shipped installer prefix (stopped before UI
  dependencies), downloaded only the official pinned uv release URL, verified/unpacked/ran uv successfully.
  Normal module path: WindowsPowerShell Modules; contaminated path: only `C:/Program Files/PowerShell/7/Modules`.
  Both exit **0**, empty stderr, `uv 0.13.7 (316c827e0 2026-11-03 x86_64-pc-windows-msvc)` and `BOOTSTRAP PASS`.
  `UV_OFFLINE=true`; no Python/dependency downloads or GUI launched. Results: `starter-release/smoke-results.json`.
- Initial scratch harness failed because dynamic ScriptBlock creation clears automatic `$PSScriptRoot`;
  printed empty-path Split-Path error, then corrected harness to execute the unchanged installer prefix as a
  real `.ps1` beside the shipped script. The corrected run above passed both paths. This was harness-only.

## Bag bombs: implementation and native chain

- `Item_Bomb`'s own actor parameter `Components.LiftableRef` names
  `Component/LiftableParam/Item_Bomb.game__component__LiftableParam.bgyml`, whose `LiftGrade` is Low,
  U32 `3655598229`. `patch/bombs.py` copies that component to the private
  `Clawshot_BagBomb` member, changes only its U32 grade to None (`3069107721`), and redirects only
  `Item_Bomb`'s reference. Original shared component bytes stay identical. Off returns no transforms.
- Isolation matters: `Obj_BombFlower_A_01` also embeds the original `Item_Bomb` component; its
  `Obj_BombFlower_Fruit` component inherits that path but explicitly requires Low. No flower pack changes;
  a private name avoids relying on pack-load order / shared-resource caching [cache risk is an inference].
- Native end-to-end use gate: the bag's pouch component supplies bomb capacity and `Item_Bomb` ammunition;
  the equipped bomb's pre-lift runs `0x027e2c50 -> 0x02e50760 -> 0x02e50570`, comparing required <= available
  at `0x02e506ac..b0`. Player override `0x02e878d0` reads `PlayerStatus.LiftGrade` as None/Low/Middle/High =
  0/1/2/3. Failure cancels pre-lift. Existing read-only native trace:
  `plans/03-game-data.md` section 30 / `plans/rounds/r7-play.md`; independent metadata audit:
  `work/r22-games/lift-audit.txt`. This is the specific requirement patched, not an inferred inventory fix.
  Kareem's original comparison (D30) observed failure before Bracelet and success after. The new grade is
  still **built, not played** until the Longshot 3.2.0 candidate/control check.
- Logic changes only the `Bombs` helper's strength term, preserving Bomb Bag and every other helper arm.
  Bomb Flowers/local strength rules and cs22b's independent Bombchu bag requirement remain separate.
- New native input `Pack/Actor/Item_Bomb.pack.zs` is in `pack/resources.toml`; the cache-only matrix has an
  option-on row. Own fixture: `work/rounds/r22/games-layered-dump`, copied from the read-only round-19 fixture
  plus this file in its newest update. No source fixture/dump file modified.

### Shared RSTB file / PR #41

Read `git -C E:/OOTRemake/Clawshot diff main refs/review/pr-41-latest -- src/clawshot/formats/rstb.py`
at Claude's request before editing. Our changes are separate additive `OWN_FORMULA` entries directly after
GameDataList, not BBender's ELink/effect entries or dispatch/signature lines. Either merge order retains both.
Audited **8373 actor packs**, **36 unique LiftableParam members**, **zero inconsistent duplicate members**,
and **8 distinct shape-dependent overheads**. Therefore no generic suffix formula was added. The native bomb
member is 992 bytes, allocation 7168: rounded32 +6176. Its private same-shape clone has the same parsed
allocation; only the grade changes. `formats/rstb.py` registers these two specific paths.
Research: `lift-size-audit.py`, `lift-size-audit.json` / `.log`. A shape-count model fits 36/36, but is not
production API: unnecessary for this fixed-shape copy. Tests check the real writer's private allocation against
the native donor's RSTB entry, along with exact member isolation and default-off empty output.

### Focused logic/UI evidence

- First settings/schema/native run: **851 passed, 4 failed** (111.46 s). The four new fixture assertions
  misnamed `can_kill_beamos_with_bomb_flower` as flower-only: printed helper is
  `has_soul(Beamos) and (has_explosives or Progressive_Strength_Upgrade)`. Changed only the fixture's flower
  route to the actual strength-only lift predicate, preserving production helpers; targeted run **11 passed**.
- `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run --offline --with pytest-xdist pytest -n 2 tests/test_bomb_lift_patch.py tests/test_bombs_option.py`: **16 passed** (15.34 s), before writer allocation tests added.
- Actual app under `--no-open`, isolated APPDATA/LOCALAPPDATA, headless Chromium only: Defaults starts Off;
  On produces the exact CLI string for `logic.bombs_without_bracelet=true`; Off returns to CS1; importing
  explicit false preserves it and shows Off. Zero page errors. Screenshots viewed:
  `work/r22-games/ui-shots/bombs-on.png`, `bombs-off-import.png`; assertions/results in `ui-shots/result.json`.
  Native dialogs/Play disabled; server stopped after proof. Scratch harness corrections: installed Chromium
  revision 1234 rather than missing 1255, lowercase preset id, locator assertions rather than string-eval
  waits blocked by CSP, and version-wrapped share strings rather than raw CS1. No production workaround.
- Read-only scan of **54 natural vanilla backup slots**: child ocarina/no-memory-prize candidates exist;
  none has bomb stock with LiftGrade None. No save modified; `natural-saves.json` records selection fields.

## Skull Kid: first complete win

Native flow `Npc_SkullKid_Child_02`, build e0f3ccfa (`skull-graph.txt`, repo EVFL reader):

- Session input result Event5 success passes the successful-rally reaction fork, join43, wait63 and
  Event6 (`EventQueryIsPlayedCurrentGradeSoundNumForSession`). Only completing the current grade reaches
  wait228 -> success fork38 -> join112 -> Navi249/69 -> success talk fork177 -> **join178**.
- Join178 originally continues to Event9 / Event10, comparing the saved grade with 6 / 8.
  First grade (<6) sets grade6 (Event11), resets rally count, then gives Blue Rupee (Event22);
  second (<8) sets grade8 (Event12) and gives Red Rupee (Event23).
  Grade8 resets rally (Event68), turns Navi (Event241), and queries the native prize Bool (Event64).
  False gives Event24; true gives repeat Blue Rupee (Event154).
- Event24 calls `Dm_SY_GetInEvent:GetInEvent_NotTurn_NotNpc` (vanilla Heart Piece); Event58 sets
  `Minigame_SkullKidSession_IsGetHeartPiece=true`, then native Navi239, talk93 and rollback26 return Ready.
  No native reward ownership test gates that grant; it reads the independent once-flag.
- `_skull_kid_first_win` adds a once-switch **after join178**, not inside any reaction/fade fork.
  Already collected -> original Event9 dispatch unchanged. Unclaimed -> cloned native grade8 write,
  then the native Event68 -> 241 -> 64 -> 24 -> 58 -> Ready chain. This matches the native post-prize
  state, so later sessions play the native longer grade with its Blue Rupee; it does not also give
  the earlier two rupees. Grade8 state selection proposed by cs22f to preserve native post-prize behavior.
- `gifts.skull_kid_changes()` is registered once in `make_seed` for every seed, independently of Gift.
  It pins the native reward boundary before Gift substitution/bag guards; no double normalization or same-item case.
  No setting: Kareem's every-seed first-win request, relayed by Claude on 2026-11-24.
- The logic rule `lost_woods.toml:25` still requires all five ocarina buttons. The native graph sends a
  grade length to the random-note engine, with no per-grade button restriction; no evidence fewer buttons
  suffice. No translated data or location access rule changed.
- Exactly one additional native event edge changes (join178), plus the existing gift item substitution;
  two local state/query nodes are appended. No new external subflow or entry point; all registry
  dependencies were already reachable from the same native entries. Defaults and existing production Gift
  recipes exercise the writer; event-registration dump coverage still runs before FROZEN.

`tests/test_skull_kid_first_win.py` replays first grade, once-flag, native repeat state, pre-collected
grades and a serialized graph; the dump variant checks exact native delta and the real reward tail.
It also exercises vanilla Gift assignments and the public Defaults writer's unchanged Heart Piece.
Native failure and decline edges remain byte/graph-identical (whole-flow exact-delta assertion).
Initial Gift-only focused command with `OOT_ROMFS` and workers1/-n2: **67 passed** (14.02 s), before
the same-item regression and every-seed clarification. Current all-seed proof is pending below.
The broad gift oracle checks only gift substitution; first-win's own exact-delta oracle checks join178.

Stopped the superseded pre-rebase shared-contract run after the every-seed clarification, before source
changes. It collected 1099 cases, reached >91%, displayed one unreported failure and then a worker crash
(`OSError: [Errno 22] Invalid argument`); no failure payload or node id survived, and lastfailed cache was
empty. Not counted as a pass or classified as fixture/load-only. Post-rebase focus will use verbose,
fail-fast output so any remaining failure prints its node and values immediately.

## UI disconnect polish (item 4, merge-kind)

`Handler.reply` catches `ConnectionError` only around sending headers/body and closes the request quietly.
JSON serialization and application calls remain outside that boundary: real application `OSError`, including
an application-raised `ConnectionResetError`, still produces its existing 400. Authorization/static/API/error
responses all share the guarded writer; no second response is attempted on a departed socket.

`tests/test_ui_disconnect.py` supplies a socket whose `sendall` raises aborted/reset/broken-pipe errors,
separately during headers and body. It asserts one response attempt, no 400 conversion, no stderr, and
unchanged application-error JSON. `CLAWSHOT_WORKERS=1 uv run --offline pytest -q tests/test_ui_disconnect.py`:
**8 passed** (0.49 s). No in-game check needed.

## Private Longshot 3.2.0 checks (built, not played)

Working root `E:/OOTRemake/work/r22-games`; only the named output mod is enabled, overlay unset.
Launchers come from the required Longshot template. Claude boot-checks; Kareem plays. No Debug age change.
Detailed outside-repo checklist: `CHECKLIST.md`. Each pair is an independent sitting under 30 minutes.

| Check | Candidate / main-control launchers | Private seed / setup | Time including control |
|---|---|---|---|
| First won song | `r22-skull-candidate-v1.bat` / `r22-skull-control-v1.bat` | 22060101; Chest + Gift; forest exit open (`closed_deku`), starting Fairy Ocarina; pool-preserving placement gives Boomerang at memory game | 20–25 min |
| Bag bombs | `r22-bomb-candidate-v2.bat` / `r22-bomb-control-v1.bat` | 22060102; both start Bomb Bag + Boomerang, no Bracelet; option on only in candidate; New Game in empty profiles | 12–15 min |

Skull Kid save: identical untouched copies of the natural child `2026-11-08_0802-before-adult` slot00,
in Kokiri Forest, Fairy Ocarina equipped (`PlayerStatus.EquipOcarina=Item_Ocarina_Fairy`), Boomerang absent,
prize Bool false, grade5, Bracelet already held. Each profile exposes only this slot; no save field edits.

Skull checklist:
1. Candidate Continue; walk into Lost Woods to the two Skull Kids' lower stumps. Decline once, then start
   and deliberately miss: neither gives the prize.
2. Retry and win the first complete short song. Expect Boomerang immediately, not Blue/Red Rupees first.
   Confirm control returns; equip and throw it.
3. Leave/re-enter and win another session: native longer song, Blue Rupee, no duplicate. Save, quit,
   relaunch/Continue; Boomerang remains usable. Repeat after reload if needed to show once-only behavior.
4. Control Continue from its independent original copy; first complete win gives old Blue Rupee, not
   Boomerang. Optional second/third rounds: Red Rupee, then Boomerang. Save and quit; report actual rounds.
5. Both logs must show `mods: Event/EventFlow/Npc_SkullKid_Child_02.bfevfl.zs <- <that arm>`.
   Read the candidate save's native once-flag afterward; do not edit it.

Bomb checklist:
1. Candidate New Game; confirm Bomb Bag, bombs and Boomerang, no Bracelet. Take out a bag bomb,
   hold/place/throw it and see the explosion without the native refusal. Use Boomerang afterward.
2. Optional isolation: Teleport to child Goron City; an ordinary Bomb Flower should still refuse lifting.
   Do not use the special Dodongo's Cavern entrance flower/boulder as a bag-bomb test; no Darunia reward.
3. Save, quit, relaunch/Continue: still no Bracelet; another bag bomb works.
4. Control New Game with its identical starting inventory: bag bomb has the old refusal/raise-cancel,
   Boomerang still works. Save and quit; report both arms and the ordinary flower if tried.
5. Candidate log must show `mods: Pack/Actor/Item_Bomb.pack.zs <- <candidate>`. Control must load its
   GameDataList mod but have no Item_Bomb override (native main pack).

Initial diagnostic staging rejected the Boomerang swap under the fully closed forest: printed replay
showed only two spheres (39/13 checks), memory game unreachable, and both ocarinas outside the forest.
The old early Boomerang was needed before that target. No unproved output was written. Corrected packet
recipe in both arms opens the forest exit and starts Fairy Ocarina (matching the natural save); same private
seed, no code/logic bypass. This is a staging recipe correction proposed by cs22f, not a product default.

### Packet construction / dry-run proof

Both arms built from canonical `make_seed`, pool-preserving validated external placements, an explicit
beatability replay, then the production `write_seed`; no partial/unproved packet was written.
Control source is main `2091387`; later `4f4ff42` / `5bc5577` are docs/test-only changes, no game code.

| Pair | Control files / spheres | Candidate files / spheres | Placements |
|---|---|---|---|
| Skull Kid | 158 / 24 | 158 / 24 | identical |
| Bag bombs (candidate v2 / control v1) | 119 / 26 | 121 / 26 | identical |

Readback compares every output game-file SHA-256. Skull pair differs only in its event flow and RSTB;
both Event24 actors are `Item_Boomerang`, only candidate retargets join178. Bomb v2 differs in Item_Bomb,
the now-always-on Skull Kid flow, and RSTB; private bomb grade is None, original is Low; no control override.
Both Skull profiles match the four copied original save files byte-for-byte; bomb profiles have no progress
save. No edited save or unrelated slot. All four `cmd.exe` launchers with `CLAWSHOT_DRY_RUN=1` exit 0,
name the exact Longshot 3.2.0 executable, unset overlay and enable only their own mod. No game started.
Research results: `packet-verification-skull-v1.json`, `packet-verification-bomb-v2.json`;
the versioned per-arm settings/manifests remain outside the repo. Old bomb v1/profile preserved, not reused.
Posted both pairs for Claude's boot-check / Kareem's play batch; neither behavior is claimed played.

Every-seed clarification: applied the current always-on transform to the staged Skull main-control flow;
its result is byte-identical to the staged candidate (`91bd2e1119a67fbe15e4d0d2d43384717d61413d491785a0acf16561710d8a51`).
No Skull packet/save rewrite was needed. Bomb v2 was rebuilt through production, adding the unshuffled
first-win Heart Piece flow; dry-run/readback passed with the unchanged main control. No game boot.
The first every-seed native/public Defaults + Gift focused run passed **68 tests** (137.82 s), before
pinning normalization ahead of Gift/bag guards. Final post-rebase ordered-pipeline contracts follow below.

## Post-rebase focused contracts

Rebased game work onto main `5bc5577`, retaining the new deterministic scrub-shield registration recipe
unchanged. Post-rebase application focus printed **1 failed, 133 passed** (80.26 s):
`tests/test_app.py::test_schema_is_exhaustive_and_replay_preserves_values` still expected only
`free_time_travel`; actual schema correctly exposed that and `bombs_without_bracelet`.
Updated the exhaustive public-schema contract with the new option; no production workaround.
Cause-aimed full application/shared/UI rerun: **949 passed** (198.46 s), workers1 / -n2.
Includes every `test_app*.py` / `test_ui*.py`, settings, native-logic validation and bomb option contracts.
All four Windows installer cases and all eight disconnect cases pass; full log:
`work/r22-games/focused-app-schema-fixed.log`. Native output/parity/registration focus is now running.

Player detection now uses CIM exact names excluding `*bootcheck*`, as Claude instructed on the thread.
It initially reported one player, then zero at the successful rerun. Focused caps stay -n2/workers1;
no sweep has started.

## Remaining work

Post-rebase focused shared/native contracts, FROZEN gate queue, locked full gates and at least
200 broad + 50 Defaults + 50 Recommended seeds, with main digests and a binding cohort.
