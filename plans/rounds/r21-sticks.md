# Round 21, track sticks (cs21d): pot-only Deku Stick and Nut sources out of logic; child tokens need a kill

Branch `r21/sticks`, base `e9bb0d7`. Ready kind: **READY (merge)** (logic tightening, no game file changes, nothing to
play). Scratch and research scripts: `E:/OOTRemake/work/r21-sticks/` (`probe.py` Banc scan, `tables.py` pack drop
tables, `dropglobal.json`, `symptom.py`, `tracker_check.py`, `gs_audit.py`, `sphere0.py`, `cand.py`, `recipes.py`,
`sweep.py`, `run_sweeps.sh`, `run_sweeps2.sh`).

## Why

Kareem's first 0.2.5 seed showed every child Skulltula behind `can_child_attack` and the Sacred Forest Meadow Wolfos gate
in logic with no child weapon. The one source: OoT Randomizer's Goron City "Stick Pot" event
(`goron_city.toml:21`, `"Deku Stick Drop" = "is_child"`), which feeds the `Sticks` helper (`helpers.toml:29`; the
shop catalog's override in `shops.toml` `[helpers]` reads it too) and so `can_child_attack`. Kareem, in game,
2026-11-22: the pot exists and drops one Deku Stick, farmable only by leaving and re-entering. **Decision (Kareem):
remove pot-only Deku Stick sources from logic.** Deku Baba drops that already need a weapon stay.

## Change 1: pot drops (`9d68e50`)

- `src/clawshot/data/world/remake/pot_drops.toml` (new): 13 event overrides, `rule = "False"` with `was` and a
  per-event `source`. The translated files stay untouched (`test_world_translate.py` compares them byte for byte).
- `tests/test_pot_drops.py` (new): a weaponless child (forest open; Ocarina, Lullaby, Saria's Song, Silver Scale,
  Bracelet, Letter) reaches Goron City and Zora's Domain but holds neither event and cannot reach `HF GS Lone Tree`;
  a Kokiri Sword brings both back (Deku Babas). Nine pot regions entered directly hold neither event. **All ten cases
  fail on `e9bb0d7`** (base copy at `E:/OOTRemake/work/r21-sticks/base-e9bb0d7`, a `git archive`) and pass on the head.
- `docs/logic.md`: a paragraph on how a child gets sticks and nuts in logic, after the ranged-pickup audit.

## Dump evidence (build `e0f3ccfa`, every non-DreamWorld `Banc/*/*.bcett.byml.zs`, read-only)

How a pot drops (round 10, `r10-pots.md`, rechecked here in `Pack/Actor/Obj_Pot_A_03.pack.zs`): Banc `Dynamic`
`Drop__DropActor` names a fixed pickup, `Drop__DropTable` one of the pack's tables; neither means
`DropTable_ResourceSupply_00`. Its rows (resource types, weight out of 100): heart 20, magic 20, range weapon 20,
nut 20, bomb 20, **stick 0**. `GameParameter/DropGlobalParam/Default` `DropUnlockCondition` gates nut drops on
`Get_StoneOfForest_IsAfter_GoInside_Exp` and stick drops on `Sequence_IsChildhood`; `ReplaceSetting` turns either into
a green rupee under conditions not decoded here. `DropTable_Obj_DekuStick` / `DropTable_Obj_DekuNut` give one stick /
one nut at 100. Pots' save flags are ResetType 88 (they come back on every visit, `03-game-data.md` section 6).

Across the whole game, **no pot names `Obj_DekuNut` or `DropTable_Obj_DekuNut`**. Pots naming a stick: Goron City
(two, child), Zora's Domain (one, child and adult-alternative copies) and Zora's River (one, child and adult; no
OoT Randomizer event there). Other fixed stick/nut placements outside pots and shops: Deku Tree basement grass
(`Obj_Plant_Grass_A_01`/`_Respawn` Hashes 16523077681389688437 and 2540384747854371104, room 7,
`DropTable_Obj_DekuStick`), and one floor stick and nut at Lake Hylia by the Zora buildings (`HyruleField_Child_Static`
`Obj_DekuStick` 8980892284071798868, `Obj_DekuNut` 9807262312429560898, ResetType 24, once only).
Deku Babas (`Enemy_Dekubaba`, `_Withered`): pack drop table `DropTable_Dekubaba_DekuNut`, one nut at 100 on a head
hit; the stick comes from the `Enemy_Dekubaba_DekuStickDrop` animation and effect [inference: not traced through
the AI graph].

## Per event

OoT Randomizer data cited from our translated files (their `# file:line` comments; OoT Randomizer's code was not opened).

| Region (file:line) | OoTR (source) | OoTR rule | Remake there | Result |
|---|---|---|---|---|
| Goron City (`goron_city.toml:21`) | Stick Pot (Overworld.json:2228) | `is_child` | `GoronCity_Child_Static` `Obj_Pot_A_03` 16954699510563627060 `Drop__DropActor Obj_DekuStick` (beside `EventRequestActor` `DekuStick_Stolen` and `Npc_Goron_004_Child_DekuStick_Near`); `GoronCity_Child_Dynamic` `Obj_Pot_A_03` 10324626920382966851 `DropTable_Obj_DekuStick`; no adult copy | **Removed**: pot only, one stick per visit (Kareem, in game) |
| Zoras Domain (`zoras_domain.toml:20`) | Stick Pot (Overworld.json:2632) | `is_child` | `ZoraDomain_Child_Dynamic` `Obj_Pot_A_04` 9081708815728257714 `DropTable_Obj_DekuStick` (adult-alternative copy 7245442263071117107; sticks unlock only in childhood) | **Removed**: same kind as Goron City |
| Zoras Domain (`:22`) | Nut Pot (Overworld.json:2633) | `True` | four chance pots and the stick pot per copy; no nut pot | **Removed**: chance only |
| Bottom of the Well Main Area (`bottom_of_the_well.toml:24`) | Stick Pot (Bottom of the Well.json:52) | `True` | 48 `Obj_Pot_A_08`(/`_Respawn`): MagicJar, Heart, Bomb and `Drop_ResourceSupply_BeforeBoss` tables, 18 with none (stick weight 0), one fixed blue rupee; **no stick pot**. One `Enemy_Dekubaba` 14156286471211114919 (room 5) | **Removed**; the Baba is not added (a loosening needs a played check) |
| Bottom of the Well Main Area (`:26`) | Nut Pot (:53) | `True` | no nut pot; chance pots | **Removed** |
| Ganons Castle Spirit Trial Ending (`ganons_castle.toml:288`) | Nut Pot (Ganons Castle.json:266) | `True` | no nut pot in `InsideGanonCastle` (fixed MagicJar/Fairy; MagicJar, RangeWeapon and before-boss tables whose candidates are magic, range weapon, bomb, heart); chance pots | **Removed** |
| Graveyard Dampes Grave (`graveyard.toml:84`) | Nut Pot (Overworld.json:2057) | `True` | the Graveyard Banc (Dampé's grave rooms `Land_DampeGrave_*` are in its adult files) has no pot at all | **Removed**: no source |
| Haunted Wasteland (`haunted_wasteland.toml:30`) | Nut Pot (Overworld.json:1125) | `True` | four `Obj_Pot_A_05` per age: two Heart, two MagicJar tables | **Removed**: no source |
| HC Storms Grotto (`hyrule_castle.toml:105`) | Nut Pot (Overworld.json:3097) | `can_blast_or_smash` | `HyruleCastle` Banc: six pots, no drop parameter (chance) | **Removed** |
| HF Cow Grotto (`hyrule_field.toml:115`) | Nut Pot (Overworld.json:3030) | `has_fire_source` | no nut pot in `HyruleField` (blue rupees, a fairy, two chance pots); the floor nut above is at Lake Hylia, not here | **Removed** |
| Jabu Jabus Belly Past Big Octo (`jabu_jabus_belly.toml:69`) | Nut Pot (Jabu Jabus Belly.json:62) | `True` | no nut pot; `Drop_ResourceSupply_BeforeBoss_PotChild`/`_PotChildHeart` pots list nut and stick among second candidates beside heart and magic (a lottery, not a guaranteed nut) | **Removed** |
| Shadow Temple Beginning (`shadow_temple.toml:24`) | Nut Pot (Shadow Temple.json:28) | `True` | no nut pot (fixed rupees and a fairy; MagicJar, Heart, Bomb, before-boss tables); chance pots | **Removed** |
| Child Spirit Before Locked Door (`spirit_temple.toml:59`) | Nut Pot (Spirit Temple.json:56) | `True` | no nut pot (Heart, Bomb, RangeWeapon tables); chance pots | **Removed** |
| KF Outside Deku Tree (`kokiri_forest.toml:77,79`) | Deku Baba Sticks/Nuts (Overworld.json:225-226) | weapon | `KokiriForest_Child_Dynamic` five `Enemy_Dekubaba_Withered`; adult 14 `Enemy_Dekubaba` | **Kept** (`master_sword.toml`) |
| Deku Tree Lobby (`deku_tree.toml:13,15`) | Deku Baba Sticks/Nuts (Deku Tree.json:12-13) | weapon | `InsideTheDekuTree_Dynamic` room 0: three `Enemy_Dekubaba` | **Kept** (`master_sword.toml`) |
| Forest Temple NW / NE Outdoors (`forest_temple.toml:56,58,94,96`) | Deku Baba Sticks/Nuts (Forest Temple.json:48-49, 89-90) | weapon | `ForestTemple_Dynamic` rooms 12 and 14: two `Enemy_Dekubaba` each | **Kept** (`master_sword.toml`) |

Removing the nut pots too (Kareem's decision names sticks): **provisional, cs21d**, from the same reasoning: a pot
returns a nut at most once per visit and, in the remake, only by chance. Tightening only.

## What else reads the events

`grep` over `src`, `tests`, `docs`: the helpers `Sticks`/`Nuts` (`helpers.toml:28-29` and the shop catalog's
`shops.toml` `[helpers]`, which wins at load), `generate/fill.py:67-68` (the ammo families used for D25's
container rule: reads the name, not a region), `items.toml` (the event items), `tracker_logic.toml` `[unmapped]`
("event: the search derives it") and tests that hand the event over directly (`test_ranged_pickups.py`,
`test_master_sword_logic.py`) or expect it from Babas (`test_world_data.py:95`). Nothing else names a region's pot.

**Tracker:** `tracker/logic.py` rebuilds the seed's world with `patch.logic_world` (the generator's builder), so the
in-logic view follows with no tracker change; a save's held sticks still count (`[stock.Item_DekuStick]`).
`tracker_check.py` on that builder, the weaponless child above: head `stick False nut False`, child tokens in logic
`LLR GS Rain Shed` (n64_only, never placed), `LLR GS Tree`, `Market GS Guard House`; `e9bb0d7` adds
`Dodongos Cavern GS Side Room Near Lower Lizalfos`, `HC GS Tree`, `HF GS Lone Tree`.

## Checks run

- `uv run ruff format --check`, `uv run ruff check`: clean.
- `CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2 tests/test_pot_drops.py`: 10 passed (head), 10 failed
  (`e9bb0d7` copy, each `holds('Deku Stick Drop')` or `holds('Deku Nut Drop')` true).
- Focused logic suite, same caps (`test_pot_drops`, `test_world_remake*`, `test_master_sword_logic`,
  `test_ranged_pickups`, `test_tracker_logic*`, `test_logic_world`, `test_world_rules`, `test_world_search`,
  `test_world_census`, `test_shop_logic`, `test_sheik_logic`, `test_progressive_logic`, `test_r18_logic_returns`,
  `test_world_token_routes`, `test_hints_world`): 508 passed, 6 skipped in 89.68 s. No game running at each stage.
- After change 2 (`7b62729`): the same suite plus `test_child_gs_kills`, `test_world_tiers`, `test_world_clock`:
  551 passed, 6 skipped in 114.5 s. `test_child_gs_kills.py` fails 7/7 on the `e9bb0d7` copy.
- Rebased on main `e8dc77d` (`0a2bc9f`), focused subset (`test_pot_drops`, `test_child_gs_kills`, `test_world_remake*`,
  `test_master_sword_logic`, `test_ranged_pickups`, `test_tracker_logic*`, `test_logic_world`, `test_world_rules`,
  `test_world_search`, `test_world_census`, `test_shop_logic`, `test_world_token_routes`): 422 passed, 6 skipped.
- Sweep and full gate: below.

## Change 2: child Gold Skulltulas need a kill

Claude, 2026-11-22, from Kareem's play: the Lon Lon Ranch tree and Market guard-house Gold Skulltulas pop out after
the bonk/crate and still need killing; many early child tokens need a sword, Slingshot or Boomerang. In the dump
each is an `Enemy_Skulltula_Gold` (LLR 341792603838029977, Market 8942465719711548237, ZF 17355397719442343054, all
`Enemy_Skulltula_Gold_AppearPopOut`; Kakariko's four as their sources in `child_kakariko.toml` say), the enemy whose
death creates the token (`patch/tokens.py` `check_source`: `LifeDepleted` drops it).

**Audit** (`gs_audit.py`). Pass 1: a child holding every pool item except a way to kill (no sword, Slingshot,
Boomerang, sticks, bombs or Bombchus, Din's, Hammer; Master Sword shuffled and absent, so adult Babas give no sticks),
forest and door open: every GS token the search lets the child take. Pass 2: every region opened to the child, so
only a token's own rule is tested (adult-only tokens show up there as noise). Before the change, pass 1 listed:

| Token | Rule | Result |
|---|---|---|
| `LLR GS Tree` | `is_child and can_bonk` | `+ can_child_attack` (`remake/child_gs_kills.toml`; Kareem, played) |
| `Market GS Guard House` | `is_child and can_break_crate` | `+ can_child_attack` (same file; Kareem, played) |
| `ZF GS Tree` | `is_child and can_bonk` | `+ can_child_attack` (same file; same pop-out actor, not played) |
| `Kak GS House Under Construction`, `Kak GS Skulltula House`, `Kak GS Near Gate Guard` | `is_child and ((at_night and 'Time Flows') or gold_skulls_ignore_daytime)` | `+ can_child_attack` (`remake/child_kakariko.toml`, the existing entries) |
| `Kak GS Tree` | the same `and can_bonk` | `+ can_child_attack` (same) |
| `LW GS Bean Patch Near Theater` | `can_plant_bugs and (can_child_attack or (shuffle_scrubs == 'off' and Deku_Shield))` | Kept: the shield path is a kill (reflected scrub nut), question below |
| `LLR GS Rain Shed` | `is_child and (at_night or ...)` | `n64_only` (never placed); unchanged |

After: pass 1 lists only the last two. Pass 2's only child token without a kill, `Jabu Jabus Belly GS Water Switch
Room` (`True`), sits behind `Jabu Jabus Belly Main`, whose entry needs the Slingshot or Boomerang
(`child_jabu_jabus_belly.toml`), so a child there always has a kill. `can_child_attack` is the kill other child token
rules use (KF GS Know It All House, ZR GS Ladder, LH GS Small Island); `tests/test_child_gs_kills.py` (7 cases:
no item fails, a Slingshot passes) fails 7/7 on `e9bb0d7` and passes on the head.

## Why main and head placed the same items

Claude asked whether any seed's placements moved. The first paired sweep (`9d68e50`, pots only) kept no placements;
spot checks did: Defaults 20200000-20200003 (`place_diff.py`) and the NoEarlySticks experiment below, seeds
20200000-20200003, both with the door open and closed (`cand.py`), were placement-identical between `e9bb0d7` and
`9d68e50`. Not sphere 0: `Buy Deku Stick (1)` is first held in sphere 1-3 in all three standard recipes (`sphere0.py`,
seeds 20200000-20200002 each). The cause is the fill: the two stick purchases are shop-held items
placed in the type-held stage before the general fill (D33), and the general fill's assumed inventory holds every
unplaced progression item, child weapons included (`fill._assumable`). A pot stick can only change a placement when
the last child weapon is being placed and no stick shop is reachable without it; no checked seed hit that. What the
pots did change is the playthrough: on `e9bb0d7`, `Deku Stick Drop` is held a sphere or more earlier (`sphere0.py`:
sphere 1 against 2-7), which is what the tracker's in-logic view (Kareem's seed) and the spoiler's spheres show.

So the final sweep records three digests per seed (placements, spheres, hints) for main `e9bb0d7`, the pots-only
commit `9d68e50` and the final head, on the standard recipes plus **NoEarlySticks** (100 seeds; `recipes.py`): the
broad recipe with the Master Sword shuffled, the Door of Time closed and both stick purchases allowed only in adult
Kakariko's shops (the shop catalog's `item_locations`, set on the prepared spec: an experiment, not a player option).
On `9d68e50` it puts the first child stick purchase in sphere 7-10.

## Sweep (rule 2)

Identical seeds in every arm (r20's ranges: Broad 20200000-20200199, Defaults and Recommended 20200000-20200049,
NoEarlySticks 20200000-20200099), canonical `make_seed` preparation, broad CS1 from
`E:/OOTRemake/work/r18-fill/settings.txt`, the app's presets, 6 workers, under the gate lock, no game running.
`sweep.py` counts fill attempts and keeps each failed attempt's message; rows and summaries in
`E:/OOTRemake/work/r21-sticks/sweep-{main,head}/` (first run) and `sweep2-{main,pots,head}/` (second run).

**First run (17:04-17:28):** main `e9bb0d7` against pots-only `9d68e50`, standard recipes: identical outcomes.

**Second run (21:26-22:00):** main `e9bb0d7`, pots-only `9d68e50`, head `7b62729` (rebased unchanged as `0a2bc9f`:
main's moves to `e8dc77d` touch no world, fill, shop or logic-doc file), each 400 seeds:

| Recipe | Arm | Accepted | Exhausted | First-try failures | Attempts | Max |
|---|---|---:|---:|---:|---:|---:|
| Broad | main / pots / head | 200/200 each | 0 | 10 (5.0%) each | 210 | 2 |
| Defaults | main / pots / head | 50/50 each | 0 | 2 (4%) each | 52 | 2 |
| Recommended | main / pots / head | 50/50 each | 0 | 2 (4%) each | 52 | 2 |
| NoEarlySticks | main / pots / head | 100/100 each | 0 | 13 (13%) each | 114 | 3 |

Same retry seeds in every arm: Broad 20200024, 032, 043, 055, 093, 165, 170, 173, 185, 189 (four "no reachable
location for 'Gold Skulltula Token'", six "items left unplaced" with late maps/compasses and ammo); Defaults 040,
043; Recommended 027, 029; NoEarlySticks 009, 012, 024, 029, 035, 040, 062, 063, 070, 077, 088, 089, 097. **For
cs21h: this change leaves main's first-try failure rate exactly as it was (Broad 10/200).**

Seeds whose digest differs (counts only, both arms accepted):

| Recipe | main vs pots: placements / spheres / hints | pots vs head | main vs head |
|---|---|---|---|
| Broad (200) | 0 / 3 / 0 | 0 / 200 / 0 | 0 / 200 / 0 |
| Defaults (50) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Recommended (50) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| NoEarlySticks (100) | 0 / 22 / 0 | 0 / 100 / 0 | 0 / 100 / 0 |

No placement moved in any of the 400 seeds, as the fill analysis above predicts: both changes only tighten rules the
general fill evaluates with every unplaced child weapon assumed. The pots change moves the playthrough's spheres in
3 Broad and 22 NoEarlySticks seeds; the token change moves them in every seed that shuffles tokens (Broad,
NoEarlySticks; Defaults and Recommended keep tokens vanilla). Hints read the same.

## Not in logic, for later (no change made)

- Loose sticks: Deku Tree basement grass, the Lake Hylia floor stick and nut, the Bottom of the Well Deku Baba. Each
  would be a loosening: a played check first.
- **Kareem: nut pots were removed with the stick pots (provisional, cs21d; Claude recommends keeping them out, as
  no pot holds a fixed nut; asked Kareem on 2026-11-22). Keep that?**
- **Kareem: `LW GS Bean Patch Near Theater` keeps OoT Randomizer's second way, `shuffle_scrubs == 'off' and
  Deku_Shield` (the nearby scrub's nut, reflected by the shield, kills the Skulltula). A kill, so left; never checked
  in the remake. Drop it unless played?**

## In game

Nothing to play: only logic data changed; no game file differs from main's output for the same placement
[inference: no patch code touched]. A seed made after this change simply never counts on a pot stick or nut.
