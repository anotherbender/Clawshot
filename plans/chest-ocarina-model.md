# Chest ocarinas: the missing get model (found 2026-11-22)

Investigation by Claude with BBender, 2026-11-22. Clawshot `main` at `b3cd3b8`, dump 1.1.1 (update v131072),
Longshot v3.1.1 (source `63363428`). Claude drove the game through Longshot's control bridge with BBender's
permission for this investigation, and BBender watched the window. Observations marked *(BBender)* are BBender's. Every
other claim is backed by the screenshots listed under "Evidence". Written as the handoff for the implementation; the
implementation (feature `ocarina-get-model`, PR #40) and its in-game results follow under "Implementation decisions".

## The problem

A Fairy Ocarina or Ocarina of Time found in a chest gives the right text and a working instrument, but no model
appears in the get pose. Rounds 6 to 11 tried several things (`03-game-data.md` sections 26 and 33,
`rounds/r7-getitem.md`, `rounds/r8-getitem.md`, `rounds/r11-ocarina.md`, `playtest/answers.md` rows R6-MINUET,
R7-GETITEM and R8-GETITEM), and none worked. Known-issue wording: `README.md:236`, `docs/settings.md:305`,
`docs/ui.md:411`, `src/clawshot/pack/templates/READ ME FIRST.txt`, `docs/discord/server-kit.md:181`.

## The fix (shown in game for both ocarinas, small chests)

Both parts are needed. Either one alone leaves the ocarina invisible.

1. **`RSDB/ActorInfo.Product.111.rstbl.byml.zs`**: delete the `CalcPriority` field (value `After`) from the
   `Item_Ocarina_Fairy` and `Item_Ocarina_Time` rows. That's the only `ActorInfo` field needed. Adding
   `AnimationResources` or the egg's heap sizes changes nothing without it, and isn't needed with it.
2. **Each ocarina pack** (`Pack/Actor/Item_Ocarina_{Fairy,Time}.pack.zs`), in
   `Actor/Item_Ocarina_X.engine__actor__ActorParam.bgyml` `Components`:
   - `EventPerformerRef` → `?Component/EventPerformerParam/PouchContent.engine__component__EventPerformerParam.bgyml`
     (native value `.../Common...`). **This makes the model appear** (static).
   - add `ASRef` → `?AS/Item_Common.root.asb` (a loose file in the game; no pack member needed).
   - add `AnimationRef` → `?Component/AnimationParam/Item_Ocarina_X.engine__component__AnimationParam.bgyml`, a
     **new member** containing exactly
     `{"AnimationResources": [{"ModelProjectName": "Item_Common_Animation"}, {"ModelProjectName": "Item_Ocarina_X_Animation"}]}`.
     `ASRef` + `AnimationRef` make it **spin**. The ocarina's own `Item_Ocarina_X_Animation` (a native model
     animation file with one `Pose_Common` clip on `Skl_Root`, referenced by nothing in the game) gives the
     **flat orientation that matches the inventory view** *(BBender asked for this)*.
   - add the `PouchContent` EventPerformerParam member to the pack (copy it from any pack that holds it, e.g.
     `Item_Boomerang`. It's a native file under its native path, the same way `custom_items.py` reuses donor members).
   - Everything else stays native. **All equipment components stay** (`AccessoryRef`, `BlackboardRef`, `DeathRef`,
     `ActorPositionCalculatorRef`, `ELinkRef`, `SystemSetting: GameActorAfter`, `OcarinaParam`). With the full fix
     the Fairy Ocarina still played songs normally *(BBender)*.

Not needed (tested): `ASInfoRef` (Item_GetDemo), `PhysicsRef`, `LODRef`, a `$parent` of `Item_EventObject_Base`,
`PouchActorInfo.PouchSpecialDeal` (changing `Ocarina` to `None` did nothing), `ActorInfo` heap sizes or
`AnimationResources`.

**Building the new member is not copying game data.** It's two animation names, built in code (a BYML dict),
like location definitions name actors. The repo holds only the code and names. The generator writes the member
into the player's output folder. Don't copy and edit a native AnimationParam's bytes (the experiment did; `src/`
shouldn't).

## Why earlier attempts failed

- Round 7 switched `EventPerformerRef` to `PouchContent` but kept `CalcPriority: After` in `ActorInfo`.
  That's half of the fix.
- Round 8 staged the `Dm_Item_Ocarina_*` cutscene props through the chest flow. It was never needed: the chest
  flows (`Dm_SY_TreasureboxSmall` Event6 `EventTriggerModelBindForItemGetDemo`, Event12 `EventPlayAS
  Rotate_GetDemo`) are generic and have no ocarina branch.
- What explains the experiments, though not proven in engine code: `CalcPriority: After` (equipment
  that follows Link's hand) keeps the actor from being shown by the get pose. The `Common` performer has no
  get-pose bind. And without an animation set, `Rotate_GetDemo` has nothing to play, so the model is static.
- The odd downward tilt seen mid-experiment came from borrowing `Item_Boomerang`'s AnimationParam, whose
  `Item_Boomerang_Animation` has its own `Pose_GetDemo`. Other items do the same: `Pouch_Longshot.root.asb` is
  `Item_Common` with `Pose_GetDemo_Longshot`.

## Evidence (in-game runs, Kokiri Forest, child, small chests)

Test mod: the KF Kokiri Sword chest (`16757992849254467386`), Mido's bottom-right (`12786193094758345086`) and
bottom-left (`10831981390482426294`) chests moved next to Link's ladder (experiment only), holding Ocarina of Time
at x = -31 and Fairy Ocarina at x = -28. The Weird Egg was the control (its model shows). Every run's log has
`mods: <file> <- <path>` for each changed file.

| Run | Ocarina | Pack change | ActorInfo change | Result |
|---|---|---|---|---|
| baseline | both | none | none | no model; egg control shows above Link's head |
| A (graftA1) | Time | full display graft* | none | no model |
| C1 | Time | none | `PouchSpecialDeal` → `None` (PouchActorInfo) | no model |
| C1 | Fairy | full graft* | AnimationResources, no CalcPriority, Boomerang heaps | **shows, spins** |
| D1 | Time | none | same as C1 Fairy | no model |
| D1 | Fairy | full graft*, equipment kept | same as C1 Fairy | **shows, spins**; plays songs *(BBender)* |
| E | Time / Fairy | full graft* | AnimationResources only / heaps only | no model / no model |
| F | Time | full graft* | no CalcPriority only | **shows** |
| F | Fairy | full graft* | AnimationResources + heaps (CalcPriority kept) | no model |
| G | Time | none | no CalcPriority | no model |
| G | Fairy | full graft* | no CalcPriority | **shows** |
| H2 | Time | ASInfoRef, ASRef, AnimationRef | no CalcPriority | no model |
| H2 | Fairy | EventPerformerRef, PhysicsRef, LODRef | no CalcPriority | **shows** |
| K | Time | EventPerformerRef | no CalcPriority | **shows, static** *(BBender)* |
| K | Fairy | PhysicsRef | no CalcPriority | no model |
| L | Time | EventPerformerRef, ASInfoRef, ASRef, AnimationRef (Boomerang's) | no CalcPriority | shows, spins *(BBender)*, tilted |
| L | Fairy | EventPerformerRef, ASRef, AnimationRef (Boomerang's) | no CalcPriority | shows, spins *(BBender)*, tilted |
| M | both | EventPerformerRef, ASRef, (empty Dummy or no) AnimationRef | no CalcPriority, AnimationResources [Item_Common_Animation] | shows, static *(BBender)* |
| N2 | Time | EventPerformerRef, ASRef, own AnimationParam [Common + Item_Ocarina_Time_Animation] | no CalcPriority | shows, spins, flat |
| N2 | Fairy | EventPerformerRef, ASRef, own AnimationParam [Common only] | no CalcPriority | shows, looked static and off |
| **O** | **both** | **EventPerformerRef, ASRef, own AnimationParam [Common + own animation]** | **no CalcPriority** | **shows, spins, flat like the inventory** |

\* "full graft" = `ASInfoRef`, `ASRef`, `AnimationRef` (Boomerang's), `EventPerformerRef`, `PhysicsRef`, `LODRef`.
Runs B, H, I and J are left out: a script bug wrote the ActorParam before applying the variant, so they were the full
graft again (consistent with the table). Screenshots: `C:/Users/bened/ootr/work/ocarina-model/evidence/<run>/`
(game images, not for the repo).

Side observation: the Fairy Ocarina received after the Ocarina of Time became the equipped instrument. That's the
native special deal, which `src/clawshot/patch/ocarina.py` (issue #34) already corrects in every seed. The experiment
mods didn't include it.

## Implementation notes

- **Where:** `src/clawshot/patch/getitem.py` owns get-item models. Its `changes(romfs, actors)` is an unwired
  experiment API (song model swaps plus the round-8 ocarina prop staging, which this finding shows is unnecessary).
  The only part used in seeds is `member_growth`, imported by `patch/write.py:13`. Whether to remove the round-8 prop
  code and wire the song models is for the maintainers. Seed recipes are assembled in `src/clawshot/patch/__init__.py`
  (`ocarina.changes` at about line 273 is the neighbour to follow).
- **Size table:**
  - The changed ActorParam is covered: `write()` raises its entry with `rstb.ACTOR_PARAM_OVERHEAD` +
    48 per own component (the ocarina gains two: `ASRef`, `AnimationRef`).
  - The **new AnimationParam member has no formula**: `rstb.required_size` raises "no size formula for
    Component/AnimationParam/...". Measure it on the dump: for every native `*.engine__component__AnimationParam.bgyml`
    pack member, compare the table entry with its size, then add the suffix to `rstb.OVERHEAD` with a `dump` test, as
    the other formulas were added. The experiment used a made-up 8192-byte entry.
  - ActorInfo has its own formula (`OWN_FORMULA`) and only shrinks here. The writer never lowers entries.
- **ActorInfo edit:** the row is found by `__RowId`. `custom_items.py` already reads and writes this table (rows
  sorted by `__RowId`). Only delete `CalcPriority` from the two ocarina rows.
- **Scope (a product call):** apply to every seed, or only when a chest holds an ocarina? Dropping `CalcPriority:
  After` also affects the ocarina in Link's hand and in native cutscenes. Not yet checked: Saria's gift cutscene
  (`Dm_Kokiri_0155`, binds the instrument to `Weapon_L`), Zelda's Ocarina of Time scene, and playing the ocarina
  (any lag behind the hand).
- **Docs to update once it's played:** the known-issue lines listed under "The problem", and `docs/settings.md`'s
  chest-verified wording.
- Tests: synthetic packs and rows built in the test (no game bytes). A `dump` test that the patched packs and
  ActorInfo read back, differ from native only in the listed fields, and the new member's entry matches the measured
  formula.

## Implementation decisions (feature `ocarina-get-model`, 2026-11-22)

| # | Decision | Proposed by |
|---|---|---|
| D1 | Feature name `ocarina-get-model` | BBender |
| D2 | Every seed, not only seeds with a chest ocarina | BBender (Claude had recommended chest-only) |
| D3 | Remove the round-8 ocarina prop staging; song model swaps stay as they are | Claude, accepted |
| D4 | Mixed in-game QA: Claude through the control bridge (permission asked again), BBender the native scenes | Claude, accepted |
| D5 | A broken native scene or get path: stop and report; BBender decides | Claude, accepted |
| D6 | Ocarinas at show-item hand-overs and the Fairy Ocarina at Skulltulas: not decided, left open | BBender |
| D7 | No guessed AnimationParam size entry: stop if no constant fits | Claude, accepted |
| D8 | One branch, one PR | Claude, accepted |

Round 21 maintainers' review (Claude, 2026-11-22, pending Kareem): D2 changed to seeds that put an ocarina in a chest,
so other seeds keep the native farewell (`plans/rounds/r21-pr40.md`, Q1).

## AnimationParam size entry (measured 2026-11-22, plan task 2)

Measured by Claude on dump 1.1.1 (update v131072), Clawshot `b3cd3b8`, with a research script outside the
repository: every unique `*.engine__component__AnimationParam.bgyml` member of every `Pack/Actor/*.pack.zs` (544,
all with a size-table entry, none differing between packs; sizes 20 to 472 bytes).

**No single constant fits** (D7). Entry minus the size rounded to 32:

| Overhead | Members | Own `AnimationResources` entries |
|---|---|---|
| 5096 | 28 | 0 (25 with no fields, 1 with only `$parent`, 2 with an empty list) |
| 5184 | 256 | 1 |
| 5272 | 220 | 2 |
| 5360 | 34 | 3 |
| 5448 | 2 | 4 |
| 5536 | 2 | 5 |
| 5624 | 1 | 6 |
| 5800 | 1 | 8 |

Every one of the 544 fits **5096 + 88 per entry of the file's own `AnimationResources` list**, whether or not it
has a `$parent` (38 do), the same shape as the actor parameter rule (5144 + 48 per own component). The ocarinas'
new member has two entries, so its entry is its size rounded to 32 + 5272. BBender accepted the per-entry rule
(proposed by Claude, 2026-11-22); it is `rstb.ANIMATION_PARAM*`, checked against all 544 by `tests/test_rstb_dump.py`.

## In-game results for the implementation (feature `ocarina-get-model`)

Build: branch `feature/ocarina-get-model` (uncommitted, on `b3cd3b8`), dump 1.1.1 (update v131072), Longshot
v3.1.1.

| Check | Seed | Who | Result |
|---|---|---|---|
| 4.1 Small chests, both ocarinas | A (below) | Claude, 2026-11-22, run `ocarina-qa/runs/A1` | Pass: both models show in the get pose, spin, and lie flat like the inventory view (`first_sheet.png`, `second_sheet.png`) |
| 4.3 Ocarina of Time first, then Fairy Ocarina | A | Claude, 2026-11-22, run A1 | Pass (equipped): `PlayerStatus.EquipOcarina` stays `Item_Ocarina_Time` after the Fairy chest; `IsGet` of both is 1 |
| 4.4 Playing afterwards, child and adult | A | BBender, 2026-11-22, in run A1 after both chests (adult by the bridge's age switch) | Pass: BBender played the ocarina as child and adult; it was the Ocarina of Time (the equipped one), in Link's hands with no offset or glitch. No song was learned on this save, so songs themselves were not played. (The bridge's D-pad `UP` did nothing there: the `at-chests` save has `ActionGuide_IsEnd.Navi` = 0.) |
| 4.8 Save and Continue | A | Claude (flags) and BBender (play), 2026-11-22, run A1 relaunched | Pass: the game's autosave (slot 04, adult) continued after a relaunch with `IsGet` of both ocarinas 1, `EquipOcarina` = `Item_Ocarina_Time`, the pack loaded again (`mods:` line), and BBender played it. The Fairy Ocarina cannot be selected in the item menu while the Ocarina of Time is owned (BBender); taken as the game's single ocarina slot, not checked against a run without this feature. Spec 4.8's "both usable" is open for BBender |
| 4.2 Big chest (`Obj_TBox_A_02`, `Dm_SY_Treasurebox`): Fairy Ocarina | B (below) | Claude, 2026-11-22, run `ocarina-qa/runs/B2` (B1's burst ended before the get pose) | Pass: after the big chest's climb-in, the Fairy Ocarina rises, spins and lies flat (`big_sheet.png` frames 7-17); `IsGet.Item_Ocarina_Fairy` 1 |
| 4.7 Ocarina of Time at a direct story grant (`LW Gift from Saria`, gift shuffle) | B | BBender, 2026-11-22, run B2 (Claude teleported Link to Hyrule Field entrance 1, which arrived at the bridge) | **Open (D5, stopped):** the handed-over ocarina looked completely fine. **Saria's own ocarina (red triangle) stayed stuck in her hand** while she presented the gift, overlapping it (BBender's screenshot); it looked normal again when she played it later. **The line said "You got the Fairy Ocarina ... poured her heart into it"** although the grant was the Ocarina of Time. Grant: after the scene `IsGet.Item_Ocarina_Time` 1 and `EquipOcarina` = `Item_Ocarina_Time` (Claude, flags), `HavePlayedEvent.Dm_Kokiri_0155` 1 |
| 4.7 comparison: the same seed B built on `main` (`b3cd3b8`, no ocarina get model) | B-main | BBender (scene) and Claude (build, run `ocarina-qa/runs/B3main`), 2026-11-22 | Saria holds **one** ocarina, normally (BBender's screenshot); the "You got the Fairy Ocarina" line is the same. The big chest shows **no** ocarina model there (`B3main/shots/big_sheet.png`), as before the fix. Outputs B and B-main differ only in the two ocarina packs, ActorInfo and the size table; `Dm_Kokiri_0155` is byte-identical |
| 4.7 isolation V1: ActorInfo change only (B-main + seed B's ActorInfo; ocarina packs vanilla) | V1 | BBender (scene) and Claude (build, run `ocarina-qa/runs/V1`), 2026-11-22 | **Overlap reproduced:** two ocarinas overlapping in Saria's hands; her red one looks normal once she actually plays it. Removing `CalcPriority` alone causes it |
| 4.7 isolation V2: ocarina packs changed only (seed B with B-main's ActorInfo, `CalcPriority` kept) | V2 | BBender (scene and chest) and Claude (build, run `ocarina-qa/runs/V2`), 2026-11-22 | **One ocarina, normal.** The Fairy Ocarina in the big chest was **not visible** (expected: the investigation needs both changes, runs F/G) |
| 4.7 fix V3: full feature + `CalcPriority: After` on `Dm_Item_Ocarina_Fairy_Saria` | V3 | BBender (played everything; Claude only launched and teleported), 2026-11-22, run `ocarina-qa/runs/V3` | **Pass:** the big chest showed the Fairy Ocarina normally, and the farewell had no glitch (Saria's own ocarina normal throughout) |
| 4.7 Ocarina of Time as a Skulltula reward (`Deku Tree GS Basement Gate`, generated pickup `Obj_GoldSkulltulaDrop_Obj_Ocarina_Time` from `Obj_Ocarina_Time`) | C (below) | BBender (played; Claude launched and teleported), 2026-11-22, run `ocarina-qa/runs/C3` | Grant passes: "You found the Ocarina of Time!", `IsGet.Item_Ocarina_Time` 1, `EquipOcarina` = `Item_Ocarina_Time`. The dropped pickup showed the Ocarina of Time model correctly (one, upright). **No model seen during the mid-air get** (BBender; camera behind Link). `Item_Ocarina_Time.pack.zs` was **not loaded** in this run (no `mods:` line), so the get never created the instrument actor and this feature's pack change was not involved; ActorInfo was loaded. Whether the get shows a model without this feature: not compared |
| 4.7 Ocarina of Time as a Skulltula reward, standing get (`Deku Tree GS Compass Room`) | C2 (base seed 8, as C but this location) | BBender (played; Claude launched and teleported), 2026-11-22, run `ocarina-qa/runs/C4` | **Pass:** Link holds up the Ocarina of Time model with "You found the Ocarina of Time!" (BBender's screenshot); `IsGet.Item_Ocarina_Time` 1, `EquipOcarina` = `Item_Ocarina_Time`. `Item_Ocarina_Time.pack.zs` again not loaded: the get shows the drop actor's model, so the gate run's missing model was the mid-air get. Observation for the token feature, not this one: the dropped `Obj_GoldSkulltulaDrop_Obj_Ocarina_Time` floats without spinning (a token spins) |
| 4.5 re-check: native Saria gift with the prop fix (current build) | D (seed 4242 current build; test copy: Mido's chests give the three stones) | BBender (played; Claude launched, relaunched and teleported), 2026-11-22, run `ocarina-qa/runs/D1` | **Fail (D5, stopped):** still glitched. Two ocarinas overlapping while Saria presents the gift, and later **her red ocarina shown twice, merged into one odd shape** at her chest (BBender's screenshots). Differences from V3 (clean): the gift is the native Fairy Ocarina (V3: Ocarina of Time via gift shuffle), and the Fairy Ocarina was **not** owned before the scene (V3: from the big chest first) |
| 4.5 experiment D2: as D, plus `CalcPriority: After` on `Npc_Equipment_009` and `Dm_Item_Ocarina_Fairy` (every row sharing the Fairy Ocarina's model project except the instrument) | D2 | BBender (played; Claude launched and teleported), 2026-11-22, run `ocarina-qa/runs/D2` | **Fail:** still glitched. Experiments stopped (BBender's call before the run) |
| 4.5 experiment E: as D (prop row only, like V3), plus the Fairy Ocarina in the big chest where the save stands (test copy); native farewell gift (Fairy) | E | BBender (played; Claude launched and teleported), 2026-11-22, run `ocarina-qa/runs/E1` | **Clean:** no glitch. `IsGet.Item_Ocarina_Fairy` 1 and `EquipOcarina` = Fairy before the farewell |
| 4.5 Native Saria gift (`Dm_Kokiri_0155`) | 4242, default settings (Chest shuffled, gifts vanilla), output `C:/Users/bened/ootr/work/ocarina-qa/manual-4242` | BBender, 2026-11-22 | Pass: the cutscene looked normal; playing the ocarina afterwards was normal |

Seed A: `ocarina-qa/tools/build_seed.py`, Chest + Token + Gift, base seed 1 with `KF Midos Bottom Right Chest` =
Ocarina of Time and `KF Midos Bottom Left Chest` = Fairy Ocarina forced (`make_seed(placements=...)`). The generator's
output (`ocarina-qa/A/seed`) is untouched; the game ran a copy (`ocarina-qa/A/mod/qa`) in which only the three KF
chests moved next to Link's house (the investigation's positions, so the `at-chests` save stands at them; the two
Banc files' size entries raised in the copy's table). Run A1's log has `mods: <file> <- <path>` for
`RSDB/ActorInfo.Product.111.rstbl.byml.zs`, `Pack/Actor/Item_Ocarina_Fairy.pack.zs` and
`Pack/Actor/Item_Ocarina_Time.pack.zs`. Longshot launched windowed (BBender watching).

Seed B: the same tool and base seed 1, with `KF Kokiri Sword Chest` = Fairy Ocarina and `LW Gift from Saria` = Ocarina
of Time forced; the same three KF chests moved in the run copy only.

**Run B2, Saria's farewell: what the flow says** (Claude, from `Dm_Kokiri_0155` native and in seed B). Two ocarina
actors take part: `Dm_Item_Ocarina_Fairy_Saria`, a cutscene prop bound to Saria's `Weapon_R` (Event7; its pack is not
changed by this feature), and `Item_Ocarina_Fairy`, the gift bound to `Player_Event`'s `Weapon_L` (Event93; changed by
this feature: no `CalcPriority`, PouchContent performer, ASRef/AnimationRef). Seed B's only change to the flow is
the gift step's pouch add (Event68: `Item_Ocarina_Time` for `Item_Ocarina_Fairy`); the shown gift model and the
native message stay the Fairy Ocarina's. Not yet known: whether either observation also happens **without** this
feature (the same seed built on `main`), or in the native gift (4.5, BBender saw nothing odd there but did not look
for it). Next oracle proposed by Claude: replay the farewell with seed B built on `main` (`b3cd3b8`) and compare.

**Result of the comparison (D5, stopped for BBender):** the second ocarina overlapping in Saria's hands **is caused
by this feature** (present with it in B2, absent without it in B3main, everything else equal). The "You got the Fairy
Ocarina" line is **not** (same without it): gift shuffle changes only the pouch add of the native farewell. Which part
of the change shows the extra ocarina (the ActorInfo row without `CalcPriority`, the PouchContent performer, or the
ASRef/AnimationRef) is not yet isolated; the flow's candidate is `Item_Ocarina_Fairy` (Event100 participates, Event93
binds it to Link's `Weapon_L`), which may now be drawn before it is bound. The native Saria gift (4.5, seed 4242) runs
the same flow apart from Event68, so it probably shows the same; BBender reported it normal but did not look for
this.

Isolation runs (Claude, 2026-11-22; BBender watched the scene): variants of seed B in `ocarina-qa/V1` and `V2`, the
big chest moved to where the `at-chests` save stands (no walking; `tools/move_chests.py`), size entries raised in the
copies where a swapped file needed it (V2's ActorInfo: 1941016 -> 1941048). The farewell starts by teleporting from
Kokiri Forest to Hyrule Field (bridge destination 1), which crosses the bridge.

**Isolation result (D5, for BBender):** the glitch comes from **removing `CalcPriority` from ActorInfo** (V1 shows it
with vanilla packs; V2 with the changed packs and `CalcPriority` kept does not). What glitches (BBender): not the gift,
which Saria holds correctly, but **Saria's own red ocarina**, `Dm_Item_Ocarina_Fairy_Saria`, from the scene's start
until she takes it from her back; from then on it looks vanilla. That prop's pack and row are not changed (no
`CalcPriority`, `GameActorDefault`, no `$parent`), but it **shares the model project `Item_Ocarina_Fairy`** (Fmdb
`Item_Ocarina_Fairy_Saria`) with the gift actor, whose row loses `CalcPriority: After`. [Inference, not shown in
engine code] the gift no longer updating "After" changes when the shared model/animation resource is posed, and the
prop follows it until it gets its own pose. Every seed plays this farewell unless `skip_saria_farewell` is on (that
setting skips the movie). Zelda's `Dm_MelodyGet_Time` (4.6) has not been checked for the same with the Ocarina of
Time.

**Fix (BBender's call, proposed by Claude, 2026-11-22):** the generator also sets `CalcPriority: After` on the
`Dm_Item_Ocarina_Fairy_Saria` row (native: no `CalcPriority`), shown clean in V3. The other rows sharing the ocarina
model projects keep their native rows (`Dm_Item_Ocarina_Fairy`, `Dm_Item_Ocarina_Time`, `Npc_Equipment_009`,
`Obj_Ocarina_Time`, `Obj_Ocarina_Time_A_01`, all without `CalcPriority`); none was seen to glitch, and Zelda's scene
(4.6, `Dm_Item_Ocarina_Time` likely) is still to be played.

Seed C: base seed 8 (`SONGS=anywhere`), `Deku Tree GS Basement Gate` = Ocarina of Time, `KF Kokiri Sword Chest` =
Kokiri Sword (moved where the save stands; Mido's chests stay in his house: moved small chests floated where the
ground drops), `KF Midos Bottom Right Chest` = Progressive Slingshot, `KF Midos Bottom Left Chest` = Deku Shield,
`KF Midos Top Left Chest` = Saria's Song (BBender wanted to see a song from a chest).

**State after D2 (for BBender's D5 decision):** removing `CalcPriority: After` from the two instrument rows (needed
for the chest model: runs F/G, V2) makes Saria's ocarinas glitch in her farewell: overlapping while she presents
the gift, and her red ocarina doubled/merged at her chest. `CalcPriority: After` on Saria's prop row was clean once
(V3: gift-shuffled Ocarina of Time, Fairy Ocarina already owned from a chest) but not in the native case (D: Fairy
Ocarina as the gift, not owned before), and not with `After` on every row sharing the model project either (D2).
[Inference] the V3 pass depended on its conditions (another gift, or the Fairy actor already loaded), not on the prop
row. No fix found; the branch still carries the prop-row edit (to be kept or dropped with the decision).

**After E (Claude, 2026-11-22):** with the prop row, the farewell is clean when the Fairy Ocarina was obtained from a
chest earlier in the same session (V3, E) and glitched when it was not (D, D2), whatever the farewell grants (V3
Ocarina of Time, E Fairy). Without the prop row it glitches even with the Fairy Ocarina obtained earlier (B2). Not
separated: owning the Fairy Ocarina vs its actor or resources having been created/loaded in this session (V3 and E
opened the chest minutes before, on the same map). In a normal seed the farewell is usually where the Fairy
Ocarina is first obtained, so the glitch case is the common one.

**Decision (BBender, 2026-11-22, D5):** ship it as a **known cosmetic issue**. The chest fix stays in every seed,
and so does the prop row (it helps when the Fairy Ocarina was obtained before the farewell). The glitch in Saria's
farewell is documented with the known issues; `skip_saria_farewell` avoids the movie. No further experiments (the
open "owned vs loaded" question, experiment F, was offered and declined).

## In-game acceptance (the investigation's list; results above, 4.6 Zelda's scene not yet played)

1. A real generated seed (not the experiment mod) with both ocarinas in chests: model visible, spinning, flat.
   Ocarina of Time then Fairy Ocarina: the Ocarina of Time stays equipped (`patch/ocarina.py`), songs kept.
2. An ocarina in a **big chest** (`Dm_SY_Treasurebox`; its bind order differs from the small chest's, see round 8).
3. Playing the ocarina afterwards: songs work, and the instrument stays in Link's hand without lag.
4. Native gifts unchanged: Saria's Fairy Ocarina cutscene, Zelda's Ocarina of Time.
5. Save and Continue: both ocarinas still in the pouch and usable.

## Tooling (how these runs were made, to repeat or extend them)

Durable copy (outside the repo): `C:/Users/bened/ootr/work/ocarina-model/`: `tools/`, `saves/at-chests/` (a save
standing in front of the moved Time chest; load it with the `a-chests` mod of any experiment, e.g. `mods/O/`),
`mods/<run>/`, `evidence/<run>/`.

- **Longshot control bridge:** `~/git/Longshot/scripts/longshot_ctl.py` (docs
  `docs/dev/reference/control-bridge.md`). Launch windowed with your own settings file, a private mods folder and the
  saved spot:
  `python -I scripts/longshot_ctl.py launch <game dir> --user <new dir> --save <ocarina-model>/saves/at-chests
  --slot 01 --run <new dir> --env HOS_MODS=<mods dir> --env HOS_FS_TRACE=1 --env HOS_OPTIONS_FILE=<...>/tools/options.ini
  --env HOS_ENV_FILE=<...>/tools/empty-env.txt --ready present`.
- `tools/mk.sh NAME "TIME_SPEC" "FAIRY_SPEC" -- RSDB_EDITS...` builds `mods/NAME` (chest mod + `build_graft.py` +
  `build_rsdb.py`). Spec: `Actor:strip,...:sys:add,...`, where `add` lists components to graft and `Anim=A+B` makes a
  new AnimationParam. RSDB edit: `Table:Row:Field=JSON`, `=-` deletes, `=@OtherRow` copies.
- `tools/run_exp.sh NAME MODS_DIR` loads the save, opens the Time chest and then the Fairy chest with screenshot
  bursts, and writes contact sheets. `tools/ctl.py` is a closed-loop walker (`walk X Z ...`), `push YAW FRAMES`,
  `burst`. `tools/actor_dump.py` and `tools/flowdump.py` dump resolved actor params and event flows (output is game
  data: keep it outside the repo).
- Gotchas:
  - `--profile test` forces headless; the flight cheat needs a focused window.
  - `--save` needs `account.sav` beside the slot.
  - A presses on the title screen can open the chest the save stands at, so wait for `prompt == Open`.
  - `clawshot.patch.write` is shadowed by the `write` function re-exported from `clawshot.patch`; use `importlib`.
  - Use a fresh run folder for each launch.
