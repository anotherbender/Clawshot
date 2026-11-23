# Round 21, track hammer (cs21e): the Megaton Hammer as explosives and as an adult weapon

Agent cs21e, branch `r21/hammer`, base `e9bb0d7`. Built, not played: nothing in this file was run in game by the
agent. Research scripts and decoded data stay outside the repo in `E:/OOTRemake/work/r21-hammer/` (`inventory.py`,
`placed.py`, `damage.py`, `analyze.py`, `near.py`, `walls.py`, `table.py`; outputs `inventory.json`, `placed.json`,
`damage.json`, `rates.json`, `rule-table.md`).

## Ask

Kareem, in game on 0.2.5 (tracker-ui-notes.md, 2026-11-22): the remake's Megaton Hammer breaks everything bombs are
needed for (boulders, bomb grottos, the Death Mountain Trail chest and Skulltula "among others") and works as an adult
weapon. Count it as explosives and as an adult weapon, except King Dodongo (bombs, or Bomb Flowers with the Goron
Bracelet). Per class, with evidence; rule (h) for anything widened. Later the same day (via Claude): **the Beamos is
uncertain and matters in the Spirit Temple: keep it out of the widening, list every Beamos-gated rule, stage the check
where a natural adult save reaches a Beamos with the Hammer.**

## Method

1. **Inventory.** `inventory.py` loads the merged world spec (`load_spec`, overrides applied) and lists every region
   rule (location, event, exit) and helper whose names include `Bombs`, `Bomb_Bag`, `has_explosives`,
   `has_both_explosives`, `can_blast_or_smash`, `can_break_mud_wall`, `can_open_bomb_grotto`, `has_bombchus`,
   `Megaton_Hammer` or `adult_sword`: **211 world rules and 76 helpers** (the brief's "about 320 lines" counted raw
   text lines, comments and trick branches included). Reads: `has_explosives` 86, `can_blast_or_smash` 56,
   `adult_sword` 47, `Megaton_Hammer` 20, `has_bombchus` 17, `Bombs` 14; `can_break_mud_wall` and
   `can_open_bomb_grotto` are read by no world rule.
2. **Damage-type names.** The remake keys `DamageRates` by murmur3-32 (seed 0) of the attack type's name, the hash
   the save keys use: murmur3("Hammer") = 85358548 (also `Weapon_Hammer`'s `EquipmentType`, its
   `PouchContentParam` `ActionGuideType` and `AssignableItem`), murmur3("Bomb") = 3237216321. Also named: Hookshot,
   Boomerang, Arrow, Fire, Ice, Electric, Water, Beam, Gust, Body, Shield, Shockwave, Bottle, Spike; 12 keys stay
   unnamed (the sword's among them).
3. **Damage tables.** `placed.py` lists every actor placed in any `Banc/**/*.bcett.byml.zs` (7457 names);
   `damage.py` decodes each one's `Pack/Actor/<name>.pack.zs` (SARC; the research BYML reader
   `work/r14-steps/byml_research.py`) and keeps `Life/DamageParameters`, `LifeParameters`,
   `ReactionForHammerAttack` and the `ActorParam` parent chain.
4. **Which object a rule means.** `near.py`/`walls.py` place each census check (by actor Hash) next to every
   bomb-breakable actor in its area; exits and events use the override's own source or the only candidate actor.
   A rule widens only when its explosive target is identified as one actor of a class the data and Kareem's play
   cover. Otherwise it is kept and listed.

## What the data says, per class

| Class | Actors (placed) | Hammer rate | Bomb rate | Life | Kareem's play covers | Verdict |
|---|---|---:|---:|---:|---|---|
| Cracked wall | `WallCrack` (DMT, DMC, DC, GC, Graveyard, HC, Shadow, ZF, Ganon's collapse); `Obj_{DodongoCave,FireTemple,ShadowTemple,SpiritTemple,WaterTemple,GerudoTrainingGround,DesertColossus,CrumblingGanonCastle}_CrackWall_*` | 100 | 100 | 6 | yes: the DMT Chest wall `WallCrack 12869454506934697528` (1.4 from the chest) and the DMT GS Near Kak wall `WallCrack 1600448280623797586` (3.7) | widen |
| Cracked floor | `Obj_DodongoCave_CrackFloor_A_01`, `Obj_FireTemple_CrackFloor_A_01` | 100 | 100 | 6 | same table (inherit WallCrack) | widen (Fire); DC's is King Dodongo's, kept |
| Boulder | `Obj_BrokenRock_A_01/_A_02`, `Obj_Goron_BrokenRock_A_01` (inherit WallCrack) | 100 | 100 | 6 | yes: boulders | already `can_blast_or_smash` wherever an adult goes |
| Bomb grotto cover | `Land_{HrlField,Kakariko,SacredForest,Zora}_HidingHoleCover_*` (`Land_HidingHoleCover_BrokenBomb_Base`) | 100 | 100 | 6 | yes: bomb grottos | widen (HF Wetland Grotto); the rest already |
| Rock circle / lift rock | `Obj_LiftRock_A_01/_A_03` | 100 | 100 | 1 | | no explosives-only rule reads them |
| Mud wall | none (no rule reads `can_break_mud_wall`) | | | | | none |
| Ice pillar, crate, Ganon rubble | `Obj_BrokenIcePillar_*`, `Obj_BrokenBox_*`, `Obj_GanonCastle_BrokenRubble_*` | 100 | 100 | 1-6 | | already Hammer (`can_break_crate`) or in no explosives rule |
| Pot | `Obj_Pot_A_*` | 1 | 100 | 1 | | in no explosives rule |
| Shadow skull pot | `Obj_ShadowTemple_SkullPot_A_01` | **0** | 100 | | | **kept** (data says no) |
| Spider web | `Obj_InsideTheDekuTree_SpiderWeb_A_02`, `Obj_InsideGanonCastle_SpiderWeb_A_01` | **0** | 100 | | | **kept** |
| Icicle, candlestick, beehive | `Obj_FallingIcicle_*`, `Obj_Well_CandleStick_A_03`, `Obj_Kokiri_Beehive_A_01` | **0** | 100 / 1 | | | **kept** (no rule widened) |
| Bomb Flower | flower `Obj_BombFlower_A_02/_A_03` (no damage table); fruit `Obj_BombFlower_A_01`: `BombFlower_Fruit` Hammer 1.0, Bomb 0.0, MaxLife 1, material `BombFruit` `IsExplode` | 1 (fruit) | 0 (fruit) | 1 | Kareem, Longshot 3.0.0, 2026-11-23: a Hammer hit blew a flower up in place | **kept** this round; round 22 candidates listed below |
| Switch | eye switches (`Obj_EyeSwitch_*`, no damage table); Hammer switches already Hammer-only; crystal switch (`can_jumpslash` names the Hammer) | | | | no | eye-switch rules **kept** |
| Enemy | every `Enemy_*` an enemy rule names: a generic table, Hammer 1.0 = Bomb 1.0 (Freezard 99, Torch Slug 100); only Jabu's tentacles have Hammer 0 | 1+ | 1 | | yes: "works as an adult weapon" | widen non-boss fights (`adult_weapon`) |
| Beamos | `Enemy_Beamos`, `Enemy_Beamos_For_High_Place`: the generic enemy table (every named type 1.0), so the table does not say why N64's Beamos needed explosives; it respawns on area reload (`ActorGameDataSetting BancResetNoItemWarp`) | 1 | 1 | 2 | Kareem, Longshot 3.0.0, 2026-11-23: one Hammer hit destroys an `Enemy_Beamos` (both arms) | ground Beamos **widened** (S1, G1, G2); high Beamos kept (out of reach) |
| Boss | King Dodongo, Phantom Ganon, Morpha, Bongo Bongo, Twinrova: Hammer 1.0 (Kotake/Koume 0, Bomb 0 too) | 1 | 1 | | no | **kept**: King Dodongo by Kareem's word; the others' reflect, nucleus and eye steps are not damage-table facts, and no natural save reaches them unbeaten |

The WallCrack table is specific, not generic: `CrackStoneObject` gives Hammer and Bomb 100, Bottle 1, and 0 to every
other named type (Arrow, Hookshot, Boomerang, Fire, Ice, Electric, Water, Beam, Gust, Body, Shield, Shockwave, Spike)
and to all but one unnamed key. `ReactionForHammerAttack/StaticCrackObject` sets `IsHammerThrough`. A wall's death
runs `DeathParam CrackObjectCommon` and the wall leaves with its collision and NavMeshCut obstacle, so a wall's chain
is damage, death, open. Every class member inherits `Work/Actor/WallCrack` (`damage.json`, `actor` field).
Placement-level parameters were not searched for per-instance damage overrides [inference: none known; the river
rocks' were checked in round 14].

## Changes

- `world.toml` `[helpers] adult_weapon = "adult_sword or can_use(Megaton_Hammer)"`. Off (no Master Sword shuffle) it
  folds to `is_adult`, so default seeds' logic is unchanged by the enemy class; on, a swordless adult with the Hammer
  counts as armed for ordinary enemies.
- `remake/hammer.toml` (new): the eight translated rules widened, each naming its actor: DMC Gossip Stone and its
  fairy, ZF Great Fairy Fountain, Fire Temple Big Lava Room Blocked Door Chest, GS Boulder Maze, Boulder Maze
  Shortcut Chest, Shadow Temple First Beamos -> Huge Pit, After Wind Hidden Chest.
- In the files that already own the entry (rule only, `was` kept, a comment or source note added): DC Room 1 and
  Room 10 chests, GS Alcove Above Stairs, both sides of the Bomb Bag ledge wall (`extra_dodongo_cavern.toml`,
  `child_dodongos_cavern.toml`); Water Temple South Basement, East Geyser Room, GS Falling Platform Room, Boss Key
  Chest Room (`adult_water_temple.toml`); Graveyard Fairy Grave fairy (`child_graveyard.toml`); HF Wetland Grotto
  (`token_routes.toml`). Enemy fights: 25 entries in `master_sword.toml` plus HF GS Lone Tree, Kak Redead Grotto
  Chest, Forest Temple Lobby -> Central Area, GTG Lava Room Front (fight part only), Ice Cavern End Chest Access,
  Sheik in Ice Cavern, Song from Royal Family's Tomb, DC Room 5/16 chests and Upper Lizalfos -> Bomb Bag Ledge,
  Water Dark Link: 36 rules.
- Water Temple walls: each guide places a bomb by hand at the wall, so Link stands on a floor there; a bomb cannot be
  set underwater, so the Hammer can be swung at the same spot [inference from the guides; the walls in Kareem's saves
  are already broken, so not testable on a natural save].
- Shadow Temple First Beamos -> Huge Pit is a wall widening, not a Beamos one: its explosives open
  `Obj_ShadowTemple_CrackWall_A_03` 6 units behind the first Beamos; nothing in the rule kills the Beamos
  [inference: the Hammer user walks past the Beamos to the wall, as a bomb user must to set a bomb there].
- Tests: `tests/test_world_remake_hammer.py` (new): widened rules open with the adult Hammer and with bombs, not for
  the child; skull pots, webs, King Dodongo and the skull-eye exit stay closed to the Hammer; with Master Sword shuffle
  a swordless adult fights enemies with the Hammer and bosses still need a blade; off is unchanged.
  `tests/test_world_token_routes.py`: the wetlands contract now expects the adult Hammer to open the cover (it pinned
  the opposite). `tests/test_master_sword_logic.py`: the sword-rewrite collector accepts `adult_weapon`.
  `tests/test_world_remake_play.py`: the fairy-grave test pinned "Hammer alone does not open the wall"; r7 wrote it
  for an *unverified* Hammer (r7-play.md: "not an unverified Hammer alternative"), not one seen to fail. It now
  expects the Hammer to open the `WallCrack` and the fairies to still need a Bottle.
- `docs/logic.md`: one paragraph (own lines).
- Kareem's call (2026-11-23, via Claude), not a Hammer class: `LW GS Bean Patch Near Theater` drops OoT Randomizer's
  `shuffle_scrubs == 'off' and Deku_Shield` way (the scrub's nut reflected into the Skulltula): players cannot be
  assumed to know it. Now `can_plant_bugs and can_child_attack` (`remake/child_gs_kills.toml`, which cs21d's
  question in `r21-sticks.md` pointed at); test `tests/test_child_gs_kills.py`. A tightening; the sweep includes it.

## Beamos-gated rules (ground Beamos widened after Kareem's check, 2026-11-23)

Placed Beamos (`walls.py`): Spirit Temple `Enemy_Beamos` 8232607517064124082 (33.6,104.7,-30.7),
12328217772424437690 (18.2,129.7,-28.5), 15096857207894283138 (40.2,130.0,-29.0) and five
`Enemy_Beamos_For_High_Place` (Sun Block Room hall, west hallway, y 130.8-131.0); GTG 2867582777575272608 (the
Beamos Chest's room); Dodongo's Cavern lobby 442957803672926269, 3345842154209982809, 5092443976113997317; Shadow
Temple 1748567630123051400 (first Beamos) and 4966197794818826898 (falling spikes room); Ganon's Castle two
`Enemy_Beamos` and two high ones; Desert Colossus 16367174076614975674; Bottom of the Well one (child only).

| # | Rule | Explosives read | Beamos | Status |
|---|---|---|---|---|
| S1 | Spirit Temple Anubis Room -> Spirit Temple Beyond Anubis Room (`spirit_temple.toml`, Spirit Temple.json:259) | `has_explosives` | `Enemy_Beamos` 12328217772424437690 and 15096857207894283138 at y 130 between the Anubis room and the Beyond Anubis checks (Near Four Armos Chest 21.7 away); the region's own pot is "Spirit Temple Beamos Hall Pot" | **widened** (`remake/hammer.toml`, Kareem's check); the Beamos is the likely target [inference from position]; behind it: Near Four Armos Chest, both Hallway Invisible Chests, Mirror Shield Chest |
| S2 | Spirit Temple Central Chamber -> Desert Colossus Hands (Spirit Temple.json:229) | `is_adult and has_explosives` | target not identified: this Beamos pair or `Obj_SpiritTemple_CrackWall_A_02` (-10.6,157.1,-27.5) | **kept** |
| S3 | Spirit Temple Big Mirror Room -> Spirit Temple Before Boss (Spirit Temple.json:296) | `has_explosives and Mirror_Shield` | target not identified: the CrackWall above is the nearer candidate | **kept** |
| S4 | Early Adult Spirit Temple -> Spirit Temple Boulder Room | `Bombs` only with a trick (a switch) | `Enemy_Beamos` 8232607517064124082 stands near the Boulder Room GS | not Beamos-gated (Bow, Hookshot or Bombchus hit the switch) |
| S5 | Spirit Sun Block Room / west hallway rules | age-unknown `has_explosives` (the child's climb wall) | five `Beamos_For_High_Place` on ledges | not Beamos-gated; a high Beamos is out of Hammer reach anyway |
| G1 | Gerudo Training Ground Beamos Chest (`master_sword.toml`) | `has_explosives and (adult_weapon or ...)` | 2867582777575272608 at 0.0 from the chest | **widened**: `can_blast_or_smash and (adult_weapon or ...)` (Kareem's check) |
| G2 | Gerudo Training Ground Lobby -> Lava Room Front (`adult_gerudo_training_ground.toml`) | `here(has_explosives and (adult_weapon or ...))` | the same Beamos (the Lava Room is past the Beamos room) | **widened**: `here(can_blast_or_smash and ...)` (Kareem's check) |
| C1 | Ganon's Castle Spirit Trial Crystal Switch Chest | `can_jumpslash or has_explosives` | `Enemy_Beamos` 10314802415333902283 16.6 away | already Hammer through `can_jumpslash`; unchanged |
| D1 | Desert Colossus Chest (TBox_Rupee_Purple), region Colossus Grotto | none: rule `True` | `Enemy_Beamos` 16367174076614975674 at 0.1 from the chest | **finding, not changed:** if this chest appears only once the Beamos dies, its `True` is too loose; question below |

**Beamos staged check (built, not played).** No natural save with the Hammer reaches the Spirit Temple: of every
backup holding the Hammer, none has the Silver Gauntlets or the Mirror Shield (scan of `save-backups/*/slot_*/
progress.sav`, `IsGet.Item_Hammer` with `IsGet.Item_Gauntlet_Silver` / `IsGet.Item_Shield_Mirror`; the
`r18-mirror-adult-*` saves have the Mirror Shield chest's playthrough but no Hammer). The nearest Beamos an adult with
the Hammer walks to is in **Dodongo's Cavern's lobby**, on `2026-11-11_2050-main-after-water` slot_04 (his main game,
adult: `Sequence_IsChildhood` false; Hammer, Longshot, Bomb Bag, Master Sword). The lobby's three are `Enemy_Beamos`,
the same actor and damage table as Spirit's S1 pair and GTG's G1/G2, so a pass covers the ground-Beamos class: S1,
G1 and G2. It does not settle S2/S3 (their target is not identified) or the high Beamos (out of reach). Packet and
checklist: see "Staged checks" below.

## Kept, with the reason

- **King Dodongo** (`Defeat King Dodongo`): Kareem's exception. His floor (`Obj_DodongoCave_CrackFloor_A_01`, Hammer
  100) would open to the Hammer by data, but the whole rule is left as it is.
- **Data says no:** Shadow Temple GS Triple Giant Pot, 3 Spinning Pots Rupees, Freestanding Key (skull pots, Hammer
  0); Invisible Floormaster Chest, its pots and the spinning-pots wonder item (web, Hammer 0).
- **Not one of the covered actors:** DC Far Bridge -> Mouth (bombs into the skull's eyes), DC Staircase -> Climb
  (Bomb Flower staircase), Fire Temple Elevator Room -> Boulder Maze Lower (a ranged switch), the Spirit lower adult
  switch, Ganon's Spirit Trial Bombchu hole, Bombchu Bowling, and the Bombchu-as-projectile rules.
- **Beamos:** S2 and S3 (target not identified), the high Beamos (out of reach); D1 is a question.
- **Target not identified (left as is, tightening-safe):** SFM chest and gossip stone (the only cover is 24 away and
  18 above, the "unverified top hole"), HF GS Near Kak Grotto (inside the grotto; Hyrule Field's webs are Hammer 0),
  DC Lobby -> Lower Right Side, DC Lower Right Side -> Torch Room, Fire Temple Flame Maze -> Upper ("Bomb exposes
  Flare Dancer": no WallCrack-family actor there) and the Megaton Hammer Chest, Spirit S2/S3, Shadow Temple Beyond
  Boat -> Before Boss (the pillar is most likely `Obj_ShadowTemple_CrackWall_A_02` at (-127.6,41.9,-43.2), but that
  its death lowers the bridge is untraced and no natural save reaches it).
- **Spirit Temple age-unknown terms** (20 rules: central chamber pots, rupees, chests, GS): their `has_explosives`
  stands for the child's way in through the climb wall; the Hammer is the adult's, so it cannot stand in for it.
- **Child only** (31 rules: Bottom of the Well, Deku Tree, Hyrule Castle grounds, child Goron City and Spirit
  routes): the Hammer is an adult item (`can_use`), so nothing changes there.
- **Rolling Goron as adult:** no Goron damage data, and Kareem's save has him stopped already.
- **Bosses:** see the class table.

## Questions for Kareem

- **Boss fights with the Hammer (Phantom Ganon, Morpha, Bongo Bongo, Twinrova; only matters with Master Sword
  shuffle): count it? No natural save reaches one unbeaten, so it would need a seed played that far.**
- **Desert Colossus Chest (TBox_Rupee_Purple) in the Colossus grotto sits on a Beamos: does it appear only once the
  Beamos is destroyed? If yes, its rule tightens to the Beamos kill (bombs).**

## Staged checks

One packet, **played by Kareem on Longshot 3.0.0, 2026-11-23: PASS**, both arms the same. One Hammer hit destroyed
a Beamos in Dodongo's Cavern; a Hammer hit on a Bomb Flower blew it up (observation for round 22, below). He has
never seen the boulder in front of Dodongo's Cavern as an adult (see the DC entrance boulder below). The ground
Beamos (S1, G1, G2) widened in its own commit after the pass.

- Game: **Longshot 3.0.0** stable (`builds\stable\v3.0.0\bin\longshot.exe`, pinned in both launchers; no
  `hookshot.exe` in either). `HOS_FS_OVERLAY` stays unset; each launcher loads one mod through `HOS_MODS`.
- Candidate: `E:\OOTRemake\work\r21-hammer\hammer-beamos-next.bat`, mod
  `work\r21-hammer\ingame\mods\hammer-beamos-next\hammer-beamos-next` (this branch, private seed **21050101**,
  Defaults, 121 files).
- Control: `E:\OOTRemake\work\r21-hammer\hammer-beamos-control-next.bat`, mod
  `...\hammer-beamos-control-next\hammer-beamos-control-next` (main `e9bb0d7` from `git archive`, same seed and
  settings, 116 files). The change is logic only (80 of 178 placements differ between the two spoilers); neither
  packet touches the Beamos, the Bomb Flowers or the Hammer, so **both arms should show the same in-game result**:
  the result is the game's own.
- Save: a copy of `save-backups\2026-11-11_2050-main-after-water`, slot_04 (his main game, natural adult: Hammer,
  Longshot, Bomb Bag, Master Sword; `Sequence_IsChildhood` false). The launcher copies it into its own test folder on
  first start; nothing writes to his saves. Its thumbnail: adult Link holding up a Gold Skulltula token at night by
  the wooden fence outside Lon Lon Ranch. No Debug age change: the save is adult already.

Checklist (candidate first):

1. Start `hammer-beamos-next.bat`. Continue the save (adult Link by the Lon Lon Ranch fence, token pose).
2. Debug > Teleport to Death Mountain Trail (or Goron City) and walk to Dodongo's Cavern; only Teleport and the clock
   are allowed. Walk in through its entrance. If the boulder in front of it is still there, break it with the Hammer
   (that is the boulder class, already shown on 0.2.5; note whether it broke).
3. Near the start (the dump places three Beamos in the cavern's opening rooms; any Beamos will do), find a Beamos (the
   spinning one-eyed statue that fires a beam). Put the Megaton Hammer on
   a button. Using only the Hammer (no bombs, no sword), walk up to the Beamos and hit it, up to three times.
   **Pass:** it is destroyed (blows up as it does from a bomb). **Fail:** the Hammer bounces or it takes no damage.
   If one Beamos fails, try a second one once.
4. Observation for the next round (not this track's pass or fail): hit a Bomb Flower's bulb in that room with the
   Hammer without picking it up. Does it explode?
5. Quit (saving is fine; it is a test copy). The log `work\r21-hammer\ingame\user-hammer-beamos-next\longshot_log.txt`
   should hold `mods: <file> <- ...hammer-beamos-next...` lines.
6. Control: start `hammer-beamos-control-next.bat` and repeat steps 1-3 only. Expected: the same result as the
   candidate. A different result means something in a packet matters after all: stop and report.

Honest time: about 10 minutes for the candidate (load, teleport, walk in, a few swings, the flower) and 5 for the
control, 15 in all; add 5 if the teleport list has no stop near the mountain. Claude boot-checks both packets first.

What a pass covers, by class: the ground Beamos (`Enemy_Beamos`) in Spirit S1 (the Anubis room's Beamos hall, the
likely target of its explosives; both Beamos there are this actor) and GTG G1 and G2. Not covered: S2 and S3 (their
target is unidentified), the high Beamos (out of Hammer reach), D1 (a question, not a widening).

**Dodongo's Cavern entrance boulder (Kareem: never seen as an adult).** The dump agrees: the boulder
`Obj_DeathMtTrail_BrokenRock_A_01` 9966036182374691433 (-47.6,108.9,-19.7) and its scripted Bomb Flower
`Obj_BombFlower_Grass_For_Break_Obj_DeathMtTrail_BrokenRock_A_01` 12145309744777105449 are placed only in
`DeathMountainTrail_Child_Static`; neither is in `DeathMountainTrail_Adult_Static` (467 actors) or `_Adult_Dynamic`
(1715), both indexed. The rule already says so: Death Mountain -> Dodongos Cavern Beginning is
`Progressive_Strength_Upgrade or is_adult` (`remake/child_death_mountain_trail.toml`, cs 2026-11-07: "no boulder in
the adult files"), so the adult needs nothing and there is nothing to loosen. The boulder has no damage table (a
scripted break), so the child side stays Bracelet-only, as before.

## Round 22 candidates: a Hammer hit on a Bomb Flower (no widening now)

Kareem, Longshot 3.0.0, 2026-11-23: a Hammer hit on a Bomb Flower in Dodongo's Cavern blew it up. The data agrees
in kind: the flower's fruit `Obj_BombFlower_A_01` (`BombFlower_Fruit`) takes Hammer 1.0, MaxLife 1, material
`BombFruit` `IsExplode` (class table above). That covers a flower exploding **where it grows**; it does not carry
one anywhere. Rules where such an in-place explosion is the whole requirement and the Hammer is not already accepted
(scan of every world rule reading explosives with the Strength upgrade or citing a flower, on this head):

| Rule | Today | Why a candidate | What round 22 must show |
|---|---|---|---|
| Dodongos Cavern Staircase Room -> Dodongos Cavern Climb (Dodongos Cavern.json, translated) | `has_explosives or Progressive_Strength_Upgrade or can_use(Dins_Fire) or (logic_dc_staircase and can_use(Bow))` | Din's Fire and the Bow already count: igniting the staircase room's flowers where they grow is enough. The nearest flowers to the Compass Chest are `Obj_BombFlower_A_03` 5389039009500383537 and 2287781480195487715 at y 111, about 7 above the chest (y 104) [heights from the dump; Hammer reach not known] | that the adult reaches a flower there with the Hammer and the staircase falls |
| Dodongos Cavern Lobby -> Dodongos Cavern Lower Right Side (translated) | `has_explosives or Progressive_Strength_Upgrade` | the lobby holds the cavern's only `BombFlowerChainExplosionManager` 10474712916684003797 (-49,105,-43.5) on `Land_DodongoCave_BombFlowerBed_A_01`; if that chain is what opens the lower right side, a hit on its first flower is the whole requirement [inference: which blocker the rule means is not identified, table row 90] | which blocker the rule means, then that a Hammer hit sets the chain off and opens it |

Not candidates: King Dodongo (Kareem's exception), the child-only flower rules (GC Spinning Pot, GC Shop and the
child Rolling Goron, the cavern's entrance boulder: the Hammer is the adult's), Stop GC Rolling Goron as Adult (a
bomb or flower at a rolling Goron, not a flower in place), and the lobby rules that already read
`can_blast_or_smash or Progressive_Strength_Upgrade`.

## Sweep and gates

Rebased onto main `b1d510d` (sticks 3667df5, tracker ff78b5e and npcs merged). The only conflict was `docs/logic.md`
(two new paragraphs at one spot; both kept, sticks' first). The world rules those merges added read no explosives or
adult weapon; the one explosive rule they touched (`HC Storms Grotto` Deku Nut Drop, was `can_blast_or_smash`) is
closed by sticks and is not in the table below. Focused tests on `b1d510d` + this track (`-n 2`, workers 1, game
running): 252 passed, 312 skipped (dump tests without `OOT_ROMFS`); ruff format and check clean.

Pending, in one gate-lock hold, all on the frozen head (`work/r21-hammer/sweep.py`, workers 6, script outside the
repo): 200 broad + 50 Defaults + 50 Recommended (seeds 21050000+), plus 50 broad with Master Sword shuffle on (the
only setting where `adult_weapon` differs from `is_adult`), then the full gate (synthetic `-n 8`/workers 4, dump
`-n 8`/workers 3).

## Every rule, by class

Columns: the inventory index, the region, the rule's kind and name, the class, the verdict ("widened", "kept",
"already Hammer" for rules that already read `can_blast_or_smash` or the Hammer, "child only", "no change" for trick
branches and Hammer-only rules) and the file that owns the rule now. Ground-Beamos rows widened after Kareem's check.

| # | Region | Kind | Name | Class | Verdict | Object / note | File |
|---|---|---|---|---|---|---|---|
| 0 | KF Outside Deku Tree | event | Deku Stick Drop | enemy | widened | Deku Babas | master_sword.toml |
| 1 | KF Outside Deku Tree | event | Deku Nut Drop | enemy | widened | Deku Babas | master_sword.toml |
| 2 | Lost Woods | exit | LW Near Shortcuts Grotto | boulder | already Hammer | LW BrokenRock_A_01 | translated |
| 3 | LW Beyond Mido | location | LW Under Boulder Blue Rupee | boulder | already Hammer | LW BrokenRock_A_01 | translated |
| 4 | LW Beyond Mido | location | LW GS Above Theater | projectile (trick) | no change | Bombchus as a ranged weapon in a trick branch | translated |
| 5 | LW Beyond Mido | exit | LW Scrubs Grotto | boulder | already Hammer | LW BrokenRock | translated |
| 6 | Sacred Forest Meadow | location | Sacred Forest Meadow Chest (Item_ScrubBusinessSeed) | unresolved | kept | explosive target unidentified: cover 24 away and 18 above the chest (the unverified top hole) | extra_sacred_forest_meadow.toml |
| 7 | Sacred Forest Meadow | location | SFM Song of Time Clearing Gossip Stone | unresolved | kept | as the SFM chest | hint_stones.toml |
| 8 | SFM Wolfos Grotto | location | SFM Wolfos Grotto Chest | enemy | widened | Wolfos | master_sword.toml |
| 9 | Hyrule Field | location | HF GS Lone Tree | enemy | widened | Gold Skulltula | token_routes.toml |
| 10 | Hyrule Field | exit | HF Southeast Grotto | grotto cover | already Hammer | HidingHoleCover | translated |
| 11 | Hyrule Field | exit | HF Open Grotto | grotto cover | already Hammer |  | child_hyrule_field.toml |
| 12 | Hyrule Field | exit | HF Inside Fence Grotto | grotto cover | already Hammer |  | child_hyrule_field.toml |
| 13 | Hyrule Field | exit | HF Cow Grotto | boulder | already Hammer | adult needs the Hammer itself | child_hyrule_field.toml |
| 14 | Hyrule Field | exit | HF Near Market Grotto | grotto cover | already Hammer |  | translated |
| 15 | Hyrule Field | exit | HF Fairy Grotto | grotto cover | already Hammer |  | translated |
| 16 | Hyrule Field | exit | HF Near Kak Grotto | grotto cover | already Hammer |  | child_hyrule_field.toml |
| 17 | Hyrule Field | exit | HF Wetland Grotto | grotto cover | widened | Land_HrlField_HidingHoleCover_A_01 2786334400301738354 | token_routes.toml |
| 18 | HF Near Kak Grotto | location | HF GS Near Kak Grotto | unresolved | kept | inside the grotto; HF webs are Hammer 0.0; target not identified | remake.toml |
| 19 | GV Fortress Side | location | GV Chest | Hammer | no change | Hammer-only already | translated |
| 20 | GV Fortress Side | exit | GV Crate Ledge | trick | no change | trick branch | translated |
| 21 | Hideout 1 Torch Jail | event | Hideout 1 Torch Jail Gerudo | enemy | widened | Gerudo guard | master_sword.toml |
| 22 | Hideout 2 Torches Jail | event | Hideout 2 Torches Jail Gerudo | enemy | widened | Gerudo guard | master_sword.toml |
| 23 | Hideout 3 Torches Jail | event | Hideout 3 Torches Jail Gerudo | enemy | widened | Gerudo guard | master_sword.toml |
| 24 | Hideout 4 Torches Jail | event | Hideout 4 Torches Jail Gerudo | enemy | widened | Gerudo guard | master_sword.toml |
| 25 | Desert Colossus | exit | Colossus Great Fairy Fountain | cracked wall | already Hammer | Obj_DesertColossus_CrackWall_A_01 (r4 cs4b) | adult_desert_colossus.toml |
| 26 | Market Bombchu Bowling | location | Market Bombchu Bowling First Prize | minigame | kept | Bombchu Bowling | child_market.toml |
| 27 | Market Bombchu Bowling | location | Market Bombchu Bowling Second Prize | minigame | kept | Bombchu Bowling | child_market.toml |
| 28 | Market Bombchu Bowling | location | Market Bombchu Bowling Bomb | minigame | kept | Bombchu Bowling | child_market.toml |
| 29 | Hyrule Castle Grounds | exit | HC Great Fairy Fountain | cracked wall | child only (no change) | HC WallCrack; Hyrule Castle Grounds is child only | translated |
| 30 | HC Storms Grotto | location | HC GS Storms Grotto | cracked wall | child only (no change) | HC storms grotto WallCrack x3; child area | translated |
| 31 | HC Storms Grotto | location | HC Storms Grotto Pot 1 | cracked wall | child only (no change) |  | translated |
| 32 | HC Storms Grotto | location | HC Storms Grotto Pot 2 | cracked wall | child only (no change) |  | translated |
| 33 | HC Storms Grotto | location | HC Storms Grotto Pot 3 | cracked wall | child only (no change) |  | translated |
| 34 | HC Storms Grotto | location | HC Storms Grotto Pot 4 | cracked wall | child only (no change) |  | translated |
| 35 | HC Storms Grotto | location | HC Storms Grotto Gossip Stone | cracked wall | child only (no change) |  | translated |
| 36 | HC Storms Grotto | event | Fairy | cracked wall | child only (no change) |  | translated |
| 37 | HC Storms Grotto | event | Bugs | cracked wall | child only (no change) |  | translated |
| 38 | HC Storms Grotto | event | Deku Nut Drop | cracked wall | child only (no change) |  | translated |
| 39 | Kakariko Village | location | Kak GS Watchtower | projectile | child only (no change) | Bombchus ranged, child | child_kakariko.toml |
| 40 | Kakariko Village | location | Kak Bomb Grotto Gossip Stone | grotto cover | already Hammer | Kakariko HidingHoleCover | hint_stones.toml |
| 41 | Kakariko Village | exit | Kak Odd Medicine Rooftop | projectile (trick) | no change |  | child_kakariko.toml |
| 42 | Kak Redead Grotto | location | Kak Redead Grotto Chest | enemy | widened | ReDeads | child_kakariko.toml |
| 43 | Graveyard Royal Familys Tomb | location | Song from Royal Familys Tomb | enemy | widened | Keese/ReDeads | song_lessons.toml |
| 44 | Death Mountain | location | DMT Chest | cracked wall | already Hammer | WallCrack 12869454506934697528; PLAYED by Kareem | translated |
| 45 | Death Mountain | location | DMT Freestanding PoH | bean soil (child here()) | no change | here() needs a child bean; the Hammer cannot help | translated |
| 46 | Death Mountain | location | DMT Rock Red Rupee | boulder | child only (no change) |  | translated |
| 47 | Death Mountain | location | DMT Rock Blue Rupee | boulder | child only (no change) |  | translated |
| 48 | Death Mountain | location | DMT GS Near Kak | cracked wall | already Hammer | WallCrack 1600448280623797586; PLAYED by Kareem | translated |
| 49 | Death Mountain | location | DMT GS Above Dodongos Cavern | Hammer | no change |  | translated |
| 50 | Death Mountain | exit | Death Mountain Summit | boulder | already Hammer |  | translated |
| 51 | Death Mountain Summit | location | DMT GS Falling Rocks Path | Hammer | no change |  | translated |
| 52 | Death Mountain Summit | exit | DMT Cow Grotto | boulder | already Hammer |  | translated |
| 53 | Death Mountain Summit | exit | DMT Great Fairy Fountain | boulder | already Hammer |  | translated |
| 54 | Goron City | location | GC Maze Left Chest | boulder | already Hammer |  | translated |
| 55 | Goron City | location | GC Maze Center Chest | boulder | already Hammer |  | translated |
| 56 | Goron City | location | GC Maze Right Chest | boulder | already Hammer |  | translated |
| 57 | Goron City | location | GC Rolling Goron as Child | NPC (rolling Goron) | child only (no change) |  | translated |
| 58 | Goron City | location | GC Medigoron | boulder | already Hammer |  | translated |
| 59 | Goron City | location | GC Medigoron Pot | boulder | already Hammer |  | translated |
| 60 | Goron City | location | GC Boulder Maze Crate | boulder | already Hammer |  | translated |
| 61 | Goron City | location | GC GS Boulder Maze | boulder/lift rock | child only (no change) |  | translated |
| 62 | Goron City | location | GC Maze Gossip Stone | boulder | already Hammer |  | translated |
| 63 | Goron City | location | GC Medigoron Gossip Stone | boulder | already Hammer |  | translated |
| 64 | Goron City | event | GC Woods Warp Open | boulder | already Hammer |  | translated |
| 65 | Goron City | event | Stop GC Rolling Goron as Adult | NPC (rolling Goron) | kept | no Goron damage data; Kareem already stopped him in his save, so not testable | translated |
| 66 | Goron City | event | Fairy | boulder | already Hammer |  | translated |
| 67 | Goron City | event | Bugs | boulder | already Hammer |  | translated |
| 68 | Goron City | exit | GC Shop | NPC | child only (no change) |  | translated |
| 69 | Goron City | exit | GC Spinning Pot | bomb-flower toss | child only (no change) |  | child_goron_city.toml |
| 70 | GC Woods Warp | event | GC Woods Warp Open | boulder | already Hammer |  | translated |
| 71 | DMC Upper Nearby | exit | DMC Upper Grotto | boulder | already Hammer |  | translated |
| 72 | DMC Upper Local | location | DMC Gossip Stone | cracked wall | widened | WallCrack 18030667990041421780 around the stone | hammer.toml |
| 73 | DMC Upper Local | event | Fairy | cracked wall | widened | same wall (fairy at the stone) | hammer.toml |
| 74 | DMC Ladder Area Nearby | exit | DMC Lower Nearby | Hammer | no change |  | translated |
| 75 | DMC Lower Nearby | exit | DMC Great Fairy Fountain | Hammer | no change |  | translated |
| 76 | DMC Lower Nearby | exit | DMC Hammer Grotto | Hammer | no change |  | translated |
| 77 | ZR Front | exit | Zora River | boulder | already Hammer | Zora River rocks (r14) | child_zora_river.toml |
| 78 | Zora River | exit | ZR Fairy Grotto | boulder | already Hammer |  | translated |
| 79 | Zoras Fountain | exit | ZF Great Fairy Fountain | cracked wall | widened | WallCrack 15706960959866666216 | hammer.toml |
| 80 | Deku Tree Lobby | location | Deku Tree Upper Lobby Recovery Heart | enemy | child only (no change) | Deku Tree: child only | master_sword.toml |
| 81 | Deku Tree Lobby | event | Deku Stick Drop | enemy | child only (no change) |  | master_sword.toml |
| 82 | Deku Tree Lobby | event | Deku Nut Drop | enemy | child only (no change) |  | master_sword.toml |
| 83 | Deku Tree Basement | location | Deku Tree GS Basement Gate | enemy | child only (no change) |  | master_sword.toml |
| 84 | Deku Tree Basement Back Room | location | Deku Tree GS Basement Back Room | cracked wall | child only (no change) |  | translated |
| 85 | Dodongos Cavern Beginning | exit | Dodongos Cavern Lobby | cracked wall | already Hammer |  | translated |
| 86 | Dodongos Cavern Lobby | location | Dodongos Cavern Map Chest | cracked wall | already Hammer |  | translated |
| 87 | Dodongos Cavern Lobby | location | Dodongos Cavern Gossip Stone | cracked wall | already Hammer |  | translated |
| 88 | Dodongos Cavern Lobby | location | Dodongo Cavern Room 1 Chest (TBox_Rupee_Blue) | cracked wall | widened | WallCrack 14106977092420306644 | extra_dodongo_cavern.toml |
| 89 | Dodongos Cavern Lobby | event | Fairy | cracked wall | already Hammer |  | translated |
| 90 | Dodongos Cavern Lobby | exit | Dodongos Cavern Lower Right Side | unresolved | kept | lobby wall not tied to one actor (Strength alternative stays) | translated |
| 91 | Dodongos Cavern Lobby | exit | Dodongos Cavern Staircase Room | torches | no change | sword guard on Fire Arrows; not a fight | child_dodongos_cavern.toml |
| 92 | Dodongos Cavern Lobby | exit | Dodongos Cavern Mouth | eye switch (trick) | no change |  | translated |
| 93 | Dodongos Cavern Lower Right Side | location | Dodongos Cavern GS Side Room Near Lower Lizalfos | enemy | widened | Gold Skulltula | master_sword.toml |
| 94 | Dodongos Cavern Lower Right Side | location | Dodongo Cavern Room 5 Chest (TBox_Rupee_Red) | enemy | widened | Lizalfos | extra_dodongo_cavern.toml |
| 95 | Dodongos Cavern Lower Right Side | exit | Dodongos Cavern Torch Room | unresolved | kept | N64 rule names only child weapons or Bombs; target not identified | translated |
| 96 | Dodongos Cavern Torch Room | location | Dodongos Cavern Deku Scrub Side Room Near Dodongos | cracked wall | already Hammer |  | translated |
| 97 | Dodongos Cavern Staircase Room | location | Dodongos Cavern Compass Chest | cracked wall | already Hammer |  | translated |
| 98 | Dodongos Cavern Staircase Room | exit | Dodongos Cavern Climb | bomb-flower chain | kept | staircase: Bomb Flowers; no Hammer evidence | translated |
| 99 | Dodongos Cavern Climb | location | Dodongos Cavern Deku Scrub Near Bomb Bag Right | cracked wall | already Hammer |  | translated |
| 100 | Dodongos Cavern Climb | location | Dodongos Cavern Deku Scrub Near Bomb Bag Left | cracked wall | already Hammer |  | translated |
| 101 | Dodongos Cavern Climb | location | Dodongo Cavern Room 10 Chest (Item_ScrubBusinessSeed) | cracked wall | widened | WallCrack 13980282214128670992 | extra_dodongo_cavern.toml |
| 102 | Dodongos Cavern Climb | exit | Dodongos Cavern Before Upper Lizalfos | cracked wall | already Hammer |  | translated |
| 103 | Dodongos Cavern Upper Lizalfos | location | Dodongo Cavern Room 16 Chest (Item_ScrubBusinessSeed) | enemy | widened | Lizalfos | extra_dodongo_cavern.toml |
| 104 | Dodongos Cavern Upper Lizalfos | exit | Dodongos Cavern Bomb Bag Ledge | enemy | widened | Lizalfos | child_dodongos_cavern.toml |
| 105 | Dodongos Cavern Far Bridge | location | Dodongos Cavern End of Bridge Chest | cracked wall | already Hammer |  | translated |
| 106 | Dodongos Cavern Far Bridge | location | Dodongos Cavern GS Alcove Above Stairs | cracked wall | widened | WallCrack 1823997448213534774 | child_dodongos_cavern.toml |
| 107 | Dodongos Cavern Far Bridge | exit | Dodongos Cavern Mouth | eye switch | kept | bombs dropped into the skull eyes | translated |
| 108 | Dodongos Cavern Far Bridge | exit | Dodongos Cavern Bomb Bag Ledge | cracked wall | widened | WallCrack 13202633467597206724 | child_dodongos_cavern.toml |
| 109 | Dodongos Cavern Mouth | location | Dodongos Cavern GS Back Room | cracked wall | already Hammer |  | translated |
| 110 | King Dodongo Boss Room | event | Defeat King Dodongo | boss | kept | King Dodongo (Kareem) | translated |
| 111 | Jabu Jabus Belly Before Boss | exit | Barinade Boss Room | trick | no change |  | translated |
| 112 | Forest Temple Lobby | location | Forest Temple GS First Room | projectile | no change | ranged kill of a high GS | translated |
| 113 | Forest Temple Lobby | exit | Forest Temple Central Area | enemy | widened |  | adult_forest_temple.toml |
| 114 | Forest Temple Central Area | location | Forest Temple First Stalfos Chest | enemy | widened | Stalfos | master_sword.toml |
| 115 | Forest Temple NW Outdoors | event | Deku Stick Drop | enemy | widened | Deku Babas | master_sword.toml |
| 116 | Forest Temple NW Outdoors | event | Deku Nut Drop | enemy | widened |  | master_sword.toml |
| 117 | Forest Temple NE Outdoors | event | Deku Stick Drop | enemy | widened |  | master_sword.toml |
| 118 | Forest Temple NE Outdoors | event | Deku Nut Drop | enemy | widened |  | master_sword.toml |
| 119 | Phantom Ganon Boss Room | event | Defeat Phantom Ganon | boss | kept | Phantom Ganon | master_sword.toml |
| 120 | Fire Temple Lower | exit | Fire Temple Lower Locked Door | Hammer | no change |  | adult_fire_temple.toml |
| 121 | Fire Temple Lower Locked Door | location | Fire Temple GS Boss Key Loop | Hammer | no change |  | remake.toml |
| 122 | Fire Temple Big Lava Room | location | Fire Temple Big Lava Room Blocked Door Chest | cracked wall | widened | Obj_FireTemple_CrackWall_A_01 3450708986142730000 | hammer.toml |
| 123 | Fire Temple Elevator Room | exit | Fire Temple Boulder Maze Lower | ranged switch | kept | Bow/Hookshot/bomb switch | adult_fire_temple.toml |
| 124 | Fire Temple Boulder Maze Lower | location | Fire Temple GS Boulder Maze | cracked wall | widened | Obj_FireTemple_CrackWall_A_01 3767799004117692338 | hammer.toml |
| 125 | Fire Temple Boulder Maze Upper | location | Fire Temple Boulder Maze Shortcut Chest | cracked floor | widened | Obj_FireTemple_CrackFloor_A_01 5036984609780716265 | hammer.toml |
| 126 | Fire Temple Flame Maze | exit | Fire Temple Upper | unresolved | kept | "Bomb exposes Flare Dancer": no WallCrack-family actor there | adult_fire_temple.toml |
| 127 | Fire Temple Upper | location | Fire Temple Highest Goron Chest | trick | no change |  | translated |
| 128 | Fire Temple Upper | location | Fire Temple Megaton Hammer Chest | unresolved | kept | Flare Dancer room: explosives target not identified | master_sword.toml |
| 129 | Fire Temple Upper | location | Fire Temple Hammer Staircase Small Wooden Crate 1 | Hammer | no change |  | translated |
| 130 | Fire Temple Upper | location | Fire Temple Hammer Staircase Small Wooden Crate 2 | Hammer | no change |  | translated |
| 131 | Fire Temple Upper | event | Fire Temple Pillar Lowered | Hammer | no change |  | adult_fire_temple.toml |
| 132 | Volvagia Boss Room | event | Defeat Volvagia | Hammer | no change |  | translated |
| 133 | Water Temple Lowered Water Levels | exit | Water Temple South Basement | cracked wall | widened | Obj_WaterTemple_CrackWall_A_01 8886778375471620346 | adult_water_temple.toml |
| 134 | Water Temple Lowered Water Levels | exit | Water Temple Dragon Statue | trick | no change |  | translated |
| 135 | Water Temple Middle Water Level | exit | Water Temple East Geyser Room | cracked wall | widened | Obj_WaterTemple_CrackWall_A_01 16397907331581633827 | adult_water_temple.toml |
| 136 | Water Temple Cracked Wall | location | Water Temple GS Falling Platform Room | cracked wall | widened | Obj_WaterTemple_CrackWall_A_01 8260753825821756465 | adult_water_temple.toml |
| 137 | Water Temple North Basement | exit | Water Temple Boss Key Chest Room | cracked wall | widened | three Obj_WaterTemple_CrackWall_A_01 | adult_water_temple.toml |
| 138 | Water Temple Falling Platform Room | exit | Water Temple Dark Link Region | enemy | widened | Dark Link | adult_water_temple.toml |
| 139 | Water Temple River | location | Water Temple GS River | trick | no change |  | translated |
| 140 | Morpha Boss Room | event | Defeat Morpha | boss | kept | Morpha | master_sword.toml |
| 141 | Shadow Temple Beginning | location | Shadow Temple Hover Boots Chest | enemy | widened | Dead Hand | master_sword.toml |
| 142 | Shadow Temple First Beamos | exit | Shadow Temple Huge Pit | cracked wall | widened | Obj_ShadowTemple_CrackWall_A_03 17091353075401231102 | hammer.toml |
| 143 | Shadow Temple Invisible Spikes | location | Shadow Temple Freestanding Key | skull pot | kept | Obj_ShadowTemple_SkullPot_A_01 Hammer 0.0 | adult_shadow_temple.toml |
| 144 | Shadow Temple After Wind | location | Shadow Temple After Wind Hidden Chest | cracked wall | widened | WallCrack 9285626040364164957 | hammer.toml |
| 145 | Shadow Temple Beyond Boat | location | Shadow Temple Invisible Floormaster Chest | spider web | kept | web Hammer 0.0 | adult_shadow_temple.toml |
| 146 | Shadow Temple Beyond Boat | location | Shadow Temple Invisible Floormaster Pot 1 | spider web | kept |  | adult_shadow_temple.toml |
| 147 | Shadow Temple Beyond Boat | location | Shadow Temple Invisible Floormaster Pot 2 | spider web | kept |  | adult_shadow_temple.toml |
| 148 | Shadow Temple Beyond Boat | location | Shadow Temple GS Triple Giant Pot | skull pot | kept | Hammer 0.0 | adult_shadow_temple.toml |
| 149 | Shadow Temple Beyond Boat | location | Shadow Temple 3 Spinning Pots Wonderitem | spider web | kept |  | adult_shadow_temple.toml |
| 150 | Shadow Temple Beyond Boat | exit | Shadow Temple 3 Spinning Pots Rupees | skull pot | kept | Hammer 0.0 | adult_shadow_temple.toml |
| 151 | Shadow Temple Beyond Boat | exit | Shadow Temple Before Boss | pillar to bridge | kept | Obj_ShadowTemple_CrackWall_A_02 likely; the bridge chain is untraced and no natural save reaches it | adult_shadow_temple.toml |
| 152 | Bongo Bongo Boss Room | event | Defeat Bongo Bongo | boss | kept | Bongo Bongo | master_sword.toml |
| 153 | Spirit Temple Lobby | exit | Child Spirit Temple Beyond Metal Bridges | child side | child only (no change) |  | translated |
| 154 | Child Spirit Temple Beyond Metal Bridges | location | Spirit Temple GS Metal Fence | child side | child only (no change) |  | translated |
| 155 | Early Adult Spirit Temple | exit | Spirit Temple Boulder Room | ranged switch | kept |  | translated |
| 156 | Child Spirit Temple Climb | exit | Spirit Temple Central Chamber | cracked wall | child only (no change) | child climb wall | translated |
| 157 | Spirit Temple Central Chamber | location | Spirit Temple Map Chest | age-unknown child access | kept | has_explosives models the child route; the Hammer is the adult's | translated |
| 158 | Spirit Temple Central Chamber | location | Spirit Temple Sun Block Room Chest | age-unknown child access | kept |  | adult_spirit_temple.toml |
| 159 | Spirit Temple Central Chamber | location | Spirit Temple Silver Gauntlets Chest | age-unknown child access | kept |  | translated |
| 160 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Pot 1 | age-unknown child access | kept |  | translated |
| 161 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Pot 2 | age-unknown child access | kept |  | translated |
| 162 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Pot 3 | age-unknown child access | kept |  | translated |
| 163 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Pot 4 | age-unknown child access | kept |  | translated |
| 164 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Pot 5 | age-unknown child access | kept |  | translated |
| 165 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Pot 6 | age-unknown child access | kept |  | translated |
| 166 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Flying Pot 1 | age-unknown child access | kept |  | translated |
| 167 | Spirit Temple Central Chamber | location | Spirit Temple Central Chamber Flying Pot 2 | age-unknown child access | kept |  | translated |
| 168 | Spirit Temple Central Chamber | location | Spirit Temple Hall After Sun Block Room Pot 1 | age-unknown child access | kept |  | translated |
| 169 | Spirit Temple Central Chamber | location | Spirit Temple Hall After Sun Block Room Pot 2 | age-unknown child access | kept |  | translated |
| 170 | Spirit Temple Central Chamber | location | Spirit Temple Sun Block Room Silver Rupee Left | age-unknown child access | kept |  | translated |
| 171 | Spirit Temple Central Chamber | location | Spirit Temple Sun Block Room Silver Rupee Center Front | age-unknown child access | kept |  | translated |
| 172 | Spirit Temple Central Chamber | location | Spirit Temple Sun Block Room Silver Rupee Center Back | age-unknown child access | kept |  | translated |
| 173 | Spirit Temple Central Chamber | location | Spirit Temple Sun Block Room Silver Rupee Right Front | age-unknown child access | kept |  | translated |
| 174 | Spirit Temple Central Chamber | location | Spirit Temple Sun Block Room Silver Rupee Right Back | age-unknown child access | kept |  | translated |
| 175 | Spirit Temple Central Chamber | location | Spirit Temple GS Lobby | age-unknown child access | kept |  | adult_spirit_temple.toml |
| 176 | Spirit Temple Central Chamber | location | Spirit Temple GS Hall After Sun Block Room | age-unknown child access | kept |  | translated |
| 177 | Spirit Temple Central Chamber | exit | Desert Colossus Hands | unresolved | kept | Spirit CrackWall_A_02: which of three rules it serves is not identified | translated |
| 178 | Spirit Temple Anubis Room | exit | Spirit Temple Beyond Anubis Room | Beamos (S1) | widened | Enemy_Beamos pair in the hall; Kareem's check 2026-11-23 | hammer.toml |
| 179 | Spirit Temple Anubis Room | exit | Spirit Temple Big Mirror Room | already Hammer | already Hammer |  | translated |
| 180 | Spirit Temple Big Mirror Room | exit | Spirit Temple Before Boss | unresolved | kept | as above | translated |
| 181 | Twinrova Boss Room | event | Defeat Twinrova | boss | kept | Twinrova | master_sword.toml |
| 182 | Bottom of the Well Main Area | location | Bottom of the Well Front Center Bombable Chest | cracked wall/boulder | child only (no change) | Bottom of the Well: child only | translated |
| 183 | Bottom of the Well Main Area | location | Bottom of the Well Map Chest | boulder | child only (no change) |  | child_bottom_of_the_well.toml |
| 184 | Bottom of the Well Main Area | location | Bottom of the Well Underwater Pot | projectile | child only (no change) |  | translated |
| 185 | Bottom of the Well Behind Fake Walls | location | Bottom of the Well Back Left Bombable Chest | cracked wall | child only (no change) |  | translated |
| 186 | Ice Cavern Beginning | exit | Ice Cavern Spinning Scythe Room | enemy | widened | Freezards | master_sword.toml |
| 187 | Ice Cavern End | location | Ice Cavern Iron Boots Chest | enemy | widened | White Wolfos | master_sword.toml |
| 188 | Ice Cavern End | location | Sheik in Ice Cavern | enemy | widened |  | song_lessons.toml |
| 189 | Ice Cavern End | event | Ice Cavern End Chest Access | enemy | widened |  | adult_lake_hylia.toml |
| 190 | Gerudo Training Ground Lobby | location | Gerudo Training Ground Stalfos Chest | enemy | widened | Stalfos | master_sword.toml |
| 191 | Gerudo Training Ground Lobby | location | Gerudo Training Ground Beamos Chest | Beamos + enemy | widened | fight and Beamos (G1, Kareem's check 2026-11-23) | master_sword.toml |
| 192 | Gerudo Training Ground Lobby | exit | Gerudo Training Ground Lava Room Front | Beamos + enemy | widened | fight and Beamos (G2, Kareem's check 2026-11-23) | adult_gerudo_training_ground.toml |
| 193 | Gerudo Training Ground Lobby | exit | Gerudo Training Ground Boulder Room | enemy | widened |  | master_sword.toml |
| 194 | Gerudo Training Ground Like Like Room | location | Gerudo Training Ground Heavy Block First Chest | cracked wall | already Hammer |  | adult_gerudo_training_ground.toml |
| 195 | Gerudo Training Ground Like Like Room | location | Gerudo Training Ground Heavy Block Second Chest | cracked wall | already Hammer |  | adult_gerudo_training_ground.toml |
| 196 | Gerudo Training Ground Hammer Room | location | Gerudo Training Ground Hammer Room Switch Chest | Hammer | no change |  | translated |
| 197 | Gerudo Training Ground Hammer Room | exit | Gerudo Training Ground Eye Statue Lower | Hammer | no change |  | translated |
| 198 | Ganons Castle Forest Trial | location | Ganons Castle Forest Trial Chest | enemy | widened | Wolfos | master_sword.toml |
| 199 | Ganons Castle Water Trial | location | Ganons Castle Water Trial Fairy Pot Drop | enemy | widened | Freezards | master_sword.toml |
| 200 | Ganons Castle Water Trial | event | Blue Fire | enemy | widened |  | master_sword.toml |
| 201 | Ganons Castle Water Trial | event | Fairy | enemy | widened |  | master_sword.toml |
| 202 | Ganons Castle Water Trial | exit | Ganons Castle Water Trial Ending | Hammer | no change |  | translated |
| 203 | Ganons Castle Spirit Trial Second Room Front | location | Ganons Castle Spirit Trial Crystal Switch Chest | crystal switch | already Hammer | can_jumpslash names the Hammer | translated |
| 204 | Ganons Castle Spirit Trial Second Room Front | exit | Ganons Castle Spirit Trial Second Room Back | Bombchu hole | kept |  | translated |
| 205 | Ganons Castle Tower | location | Ganons Tower Boss Key Chest | enemy | widened | tower fights | master_sword.toml |
| 206 | Ganons Castle Tower | exit | Ganons Castle Tower Below Boss | enemy | widened |  | master_sword.toml |
| 207 | Deku Tree Top Floor | location | Deku Tree GS Compass Room | enemy | child only (no change) |  | child_deku_tree.toml |
| 208 | Deku Tree Top Floor | exit | Deku Tree Basement | enemy | child only (no change) |  | child_deku_tree.toml |
| 209 | Dodongos Cavern Bomb Bag Ledge | exit | Dodongos Cavern Far Bridge | cracked wall | widened | WallCrack 13202633467597206724 | child_dodongos_cavern.toml |
| 210 | Graveyard Fairy Grave | event | Fairy | cracked wall | widened | WallCrack 9366825990748670811 | child_graveyard.toml |
