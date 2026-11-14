# Round 15, Track C: Gold Skulltula shuffle specification

Author: cs15c, openai-codex/gpt-6.1-sol. Issue [#30](https://github.com/hiKareeem/Clawshot/issues/30).
Base: `1db6e63`, Clawshot 0.2.1. **Review candidate; Claude must accept this specification before Track D implements it.**
This track changes documentation only, not Clawshot code, settings, tests or version.

## 1. Clean-room boundary and evidence vocabulary

This is a behavioural contract, not a port or instructions for reconstructing another project's implementation.
Track D may read this file, Clawshot's own sources and the player's dump. It must not open ootrr, the earlier
comparison report, or this researcher's external source checkout. No third-party source, generated actor naming
scheme, helper names, implementation structure or algorithm is supplied here. Native game names below identify
resources and observable contracts, not third-party identifiers. Credit the independent lead as **ootrr (REALAZK)**.

The GPL checkout `E:/OOTRemake/work/refs/ootrr-azk` was pinned by `git rev-parse HEAD` to
`b7d9c86a0897c0423a1b63bc5ea7ac281bb98ea7`. Citations into that revision are fact sources only.
The earlier `E:/OOTRemake/work/refs/ootrr-azk-FINDINGS.md` was read as a lead, not handed to the implementer.
No GPL code was copied into Clawshot or into the research scripts. The unmodified external `ainb` decoder was
used outside the repository to inspect native game graphs; its code is not an implementation dependency.

Evidence labels throughout:

- **Native/static:** directly read on supported build `e0f3ccfa`, not an observed game session.
- **Played/ours:** an existing named Kareem result, not repeated by this agent.
- **Reported/ootrr:** REALAZK's observation, not Clawshot or Longshot acceptance.
- **[INFERENCE]:** a deduction whose runtime boundary remains to be tested.
- **Required/proposed:** the requested Clawshot behaviour, not a claim that it exists today.

### Source register

All `N` inputs are read-only below `E:/Games/Hookshot/romfs/`, unless the executable path is given.
All new scripts and decoded results are below `E:/OOTRemake/work/r15-tokens/` (abbreviated `work/` below).
The JSON files are local evidence only and must never enter the repository or a public issue.

| Source | Reproducible evidence / exact native resource |
|---|---|
| N1 | `work/native_facts.py` -> `native-facts.json`: `Pack/Actor/Enemy_Skulltula_Gold.pack.zs`, its `Drop/DropSubTable/DropTable_Token_Gold.game__drop__DropSubTable.bgyml`, `AI/Enemy_Skulltula_Gold.utility.root.ainb`, and `Component/Blackboard/BlackboardParamTable/Drop.engine__component__BlackboardParamTable.bgyml` |
| N2 | Same probe: `Pack/Actor/Obj_Token_Gold.pack.zs`, `Actor/Obj_Token_Gold.engine__actor__ActorParam.bgyml`, `Component/PouchContentParam/Obj_Token_Gold.game__component__PouchContentParam.bgyml`, `AI/Item_Token_Gold.root.ainb`, and `Component/Blackboard/BlackboardParamTable/Item_Token_Gold.engine__component__BlackboardParamTable.bgyml` |
| N3 | Same probe: `System/CombinationDataTableData/{Enemy_Skulltula_Gold,EnemyCommon,Default,Item_Token_Gold,DropItem}_game__death__DeathReasonProcedures.pp__CombinationDataTableData.bgyml`; resolve `$parent` and individual `CellList` fields, not just one local row |
| N4 | `work/native_evidence.py` -> `native-callback.txt`: read-only `E:/Games/Hookshot/.hookshot_exefs/main`, SHA256 `2591fb99008d0814f8056c3f36b36790048ed857ff0ae2bb3a4c1e37b960a4de`; native callback range `0x028e2040..0x028e20ec`, Boolean-by-64-bit-key write `0x00f07130..0x00f07244` |
| N5 | `work/native_facts.py`, `work/route_facts.py` -> both JSON reports: `GameData/GameDataList.Product.110.byml.zs`, `Data.Bool64bitKey`, `Data.Bool`, `Data.Int`, `Data.Struct` |
| N6 | Same probes: `RSDB/{ActorInfo,GameActorInfo,PouchActorInfo}.Product.111.rstbl.byml.zs`, native rows for `Obj_Token_Gold`, `Item_Token_Gold`, `Obj_Item_Base`, `Obj_Shield_Hylian`, `Item_Boomerang`; target actor packs in N2 / `Pack/Actor/{Item_Token_Gold,Item_Boomerang,Obj_Shield_Hylian}.pack.zs` |
| N7 | `work/native_facts.py`: `Event/EventFlow/{GetPouchContent,Dm_SY_Treasurebox,Dm_SY_TreasureboxSmall,GatheringTokenGold}.bfevfl.zs`; event names below are names, not list indices |
| N8 | `work/decode_graphs.py` decodes the two N1/N2 graphs; `work/graph_facts.py` decodes native `PouchContent.event.root.ainb` extracted from `Pack/AI.Global.Product.111.pack.zs` and the four route graphs below |
| N9 | `work/route_facts.py`: only `Banc/HyruleField/HyruleField_{Child,Adult}_{Static,Dynamic}.bcett.byml.zs`; per-Hash actors, bindings and surrounding actors in `route-facts.json` |
| N10 | Native `Logic/HyruleField_Child_Level_Prefab_29fc.logic.module.ainb` and `Logic/HyruleField_Adult_Level_Prefab_c022.logic.module.ainb`; child decoded separately with the same external decoder; adult decoded by `graph_facts.py` |
| N11 | Native `Logic/{Gimmick_SwayingTree_Skulltula_Gold_00_8dca,Gimmick_Nighttime_Skulltula_Gold_Appear_05a9,Gimmick_BoxBroken_Skulltula_ed23}.logic.module.ainb`; `graph_facts.py` |
| W1 | Own executable experiment `work/native_facts.py`: `load_world()` and vanilla `Search.collect_spheres`, with the existing vanilla-test starting small keys; definitions from `src/clawshot/data/locations.toml`; output in `native-facts.json` |
| S1 | `work/checkpoint_facts.py` -> `checkpoint-facts.json`: read-only historical backup `E:/OOTRemake/work/save-backups/2026-11-07_llr-tower-before-pickup/slot_01/progress.sav`; SHA256 `450eaf011b5654ce5f6e4a2bf7dc1d79feb68efaae5153203fb0339e11e4b8b7` |
| P11/P23/P27/P35 | Our `plans/03-game-data.md` sections 11, 23, 27 (especially “Gold Skulltulas: keep the native pickup”), and 35 “Skulltula House” |
| R1 | [REALAZK's 2026-11-14 gameplay report](https://github.com/REALAZK/ootrr/issues/6#issuecomment-6879825257). No build, runtime, specific Skulltula, non-token reward, chest-token or save/reload case is identified there. Kareem's unanswered follow-up asks about reload recovery and House counting. |
| R2 | ootrr at the pinned revision, `crates/core/src/pickup_pack/kit.rs:28-42,264-295,368-410,418-435`: native resource/field names, collected-reason distinction and environmental constraints; corroborated independently by N1–N5/N8. No construction procedure is transferred. |

## 2. What the native game does

### 2.1 A kill is not a collected location

**Native/static:** the census has 100 distinct `Enemy_Skulltula_Gold` Hashes and 114 placement copies.
The native drop definition chooses one `Obj_Token_Gold` with probability 100 and count 1. An enemy instance can
select a different spawned actor through `Dynamic.Drop__DropActor`; `Drop__DropTable` is also instance-settable,
whereas `Drop__DropTableOverWrite` is not. That selector names a world actor, not an inventory grant. [P23; N1]

**Native/static:** the enemy utility graph carries its no-respawn game-data Hash into the drop's
`GoldTokenGmdHash`. The token blackboard declares that U64 with default zero, not an instance parameter.
The native token graph observes `QueryDeathIsDead`, and only death reason **10** reaches
`OneShotGoldTokenDeadAfter` and `ExecuteDeathSignalDeathProcedure`. Other reasons do not run that completion
branch. The native token's `PickedUp` death procedure waits for that signal. [N1/N2/N3/N8; P23; R2]

**Native/static:** the callback reads `GoldTokenGmdHash`; for a nonzero Hash H it submits true writes for
**H and H xor 2**. This is XOR, not universally H+2: for Lone Tree the companion is `2177746409373494989`,
while the placement is `2177746409373494991`. All 100 primary rows and all 100 companion rows exist in
`Data.Bool64bitKey`, each `ResetTypeValue=24`, `SaveFileIndex=0`. These are collection records, not token stock.
The callback's inspected body contains no pouch-add/count increment. [N4/N5]

**Native/static:** the enemy's `LifeDepleted` death procedure explicitly leaves
`IsSetGmdRespawnFlagToFalse=false`; its inherited `IsSetRespawnFlagToFalse=true` retires the current enemy
instance. Do not confuse transient actor retirement with the saved game-data row. [N3]

**[INFERENCE]:** when the drop is abandoned and the area is recreated, the source can appear again because its
saved completion pair was not set at death. Collection, not killing, is the permanent commit point. This agrees
with R1 but is not a played reload test on our build. A source may also require night, a tree roll, a crate or a
soil trigger again; “comes back” does not mean it must rematerialize immediately in the same loaded area. [N1–N5/N11]

### 2.2 What determines the reward

**Played/ours:** changing only the native token component's `PouchActor` to Boomerang still produced a token,
increased tokens and gave no Boomerang (Kareem, 2026-11-08, Hookshot 2.0.1, `native-token-boomerang`).
The old experiment retained the token's canonical identity and token-specific grant classification. It does not
refute a different pickup actor that grants another item while retaining collection reporting. [P27]

**Native/static:** the following are different identities/behaviours, not interchangeable strings:

| Concern | Native token fact |
|---|---|
| Spawned world object | `Obj_Token_Gold` |
| Canonical actor identity | `ActorInfo` row `Obj_Token_Gold` has `ActorName=Item_Token_Gold`; its actor parameter's `ActorNameRef` likewise names `Item_Token_Gold` |
| Inventory actor | `Item_Token_Gold`, stocked to a fixed maximum 100; `PouchActorInfo` calls its category `KeyItem`, get type `Medium`, special deal `TokenGold` |
| World pickup's pouch component | Has its own `PouchContentRef`, `PouchActor`, `GetType`, `SpecialDeal`, auto-get/event policy; not a single per-location reward blackboard |
| Get-event payout | `GetPouchContent` Event0 adds one of its **ActorName argument**, independently of the model; Event11/Event15 select get-window identity. Native chest flows pass their `ContentName` into that family |
| Location completion | The separate Hash-carrying reason-10 callback above, not the granted item's name |

Sources: N2/N6/N7; P27. `PouchContent.event.root` also distinguishes own-item addition, canonical ActorName
queries, category/special-deal queries and actor retirement; these are separate native operations. [N8]

**[INFERENCE]:** a valid substitute needs the selected reward's effective grant identity and native grant
semantics, not merely a token-shaped model or a changed pouch pointer. Neither the negative P27 experiment nor
R1 isolates one component field as sufficient to redirect every grant path. In particular, this research does
**not** certify `ActorName`, `GetType`, `SpecialDeal` or `PouchActor` changed alone as a universal fix. The
implementer must demonstrate the event's resolved ActorName/payout and usable saved inventory for each admitted
reward family. That is the acceptance boundary, not a prescribed actor-construction algorithm. [N2/N6–N8; P27]

### 2.3 Independent count and House state

**Native/static:** `PouchData.Item_Token_Gold.StockNum` is the saved integer stock count (key `74668408`,
default 0, reset type 32, save file 0). `PouchData` and `PouchData.Item_Token_Gold` are Struct routing records,
not additional counts. `IsGet.Item_Token_Gold` is saved Boolean history, not a count or a list of completed
Skulltulas. The source-Hash pairs are independent of all of those. [N5/N6; P23]

**Native/static:** House `GatheringTokenGold` tests that stock count, not the number of dead enemies.
Its five ordinary rewards and completion records are:

| Tokens | Grant call | Vanilla item | Saved once-only record |
|---|---|---|---|
| 10 | Event398 | `Item_Wallet_Medium` | `KakarikoVillage_GatheringTokenGold_GetReward10` |
| 20 | Event75 | `Item_AgonyStone` (Echo Gem) | `KakarikoVillage_GatheringTokenGold_GetReward20` |
| 30 | Event194 | `Item_Wallet_Large` | `KakarikoVillage_GatheringTokenGold_GetReward30` |
| 40 | Event200 | `Item_BombchuBundle_Large`, **20 Bombchus** | `KakarikoVillage_GatheringTokenGold_GetReward40` |
| 50 | Event219 | `Obj_Heart_Piece` | `KakarikoVillage_GatheringTokenGold_GetReward50` |
| 100, first | Event215 | `Obj_Rupee_Gold` | native `GatheringTokenGold` quest completion |

Sources: N7; P23/P35. The five `GetReward` Bools default false, reset type 8, save file 0. Event471 is the
father's repeat 200-rupee payout, not another once-only location. Event232 advances the quest to `Complete`;
`GatheringTokenGold_IsCompleted_Exp` is a completion query, not a replacement per-token flag. [N5/N7; P35]

**Played/ours:** only the 10-token substituted reward and a 20-token preview are recorded as accepted; the
corrected 40-token grant remains held. Do not relabel all thresholds played because their event structures
match. [P35; `docs/settings.md`, “Unaccepted checks”; issue #11]

## 3. Required shuffle behaviour

These are requirements proposed by cs15c for maintainer review, not new product decisions made by this track.

### 3.1 Locations, items and completion

1. Offer **Tokens** as an explicit shuffle kind, using the existing CLI `Token` spelling and the same settings
   representation in app/CLI/replay. Proposed default: **off**, no preset changes. Off leaves Skulltula drops,
   persistence, token pool and grants native; it must not globally modify the native token pack. Existing seed
   folders and saves are never migrated. [Required: #30; compatibility policy in `04-world-format.md`]
2. On includes **all 100 physical Skulltulas**, each identified by source Banc family and stable enemy Hash.
   Every age/Alternative copy is one check with one assigned item; preserve transforms, appearance conditions,
   bindings and source identity. No index-based identities or duplicate pool items for 114 copies. [N1/N9; P11/P23]
3. Supply exactly **100 individual Gold Skulltula Token items** from those 100 checks. Tokens can move away
   from enemies, including into ordinary shuffled **chests**. Do not also count the native token as a bonus when
   another item occupies the source. No extra grant on killing, no compensation token, no stock=kill-count rule.
   A token item received anywhere increments native stock by one up to its native cap. [Required: #30; N5–N7]
4. A Skulltula with a different item drops one reachable world pickup that gives **that item**, with its real
   name/text and usable inventory effect, and **does not** increase token stock. It permanently completes only
   that source on successful collection. A missing, despawned or uncollected drop must be recoverable by
   revisiting/reloading and retriggering the source. Already-owned and full-capacity outcomes must still retire
   the check exactly once after the native pickup interaction finishes. [Required; N1–N5/N8; P27; R1]
5. A token in a chest completes only that chest. It must not set an arbitrary Skulltula Hash or complete a second
   location through a stale `GoldTokenGmdHash`. A token received at any source counts for the House and tracker.
   Reloading either source must not duplicate stock or the item. [Required; N4–N7]
6. Keep count, check completion and quest advancement separate. No fake saved flags, forced House completion,
   max-count initialisation in production, replacement of collection by enemy death, or global redirection of
   every token. Preserve the native source/callback lifecycle; prove recovery and once-only behaviour in game.
   [Required; P23/P27; N3–N5]

### 3.2 Destination compatibility is part of fill, not a late writer failure

The feature must support actual non-token rewards at Skulltulas, including a **major-item control such as
Boomerang**, as well as tokens in chests. Otherwise it has not demonstrated a mechanism beyond P27's failed
pointer experiment. Build independent reward delivery from native game facts; no construction design is mandated
here. The chosen admitted families and their proofs belong in D's round file. [Required: #30; P27]

| Destination / item family | Required compatibility rule |
|---|---|
| Token item in Chest | Supported; native inventory identity `Item_Token_Gold`. Prove ordinary small and large chest event paths, count, text/model and reload. Do not spawn an enemy-bound pickup inside the chest grant |
| Token item in Token location | Supported, including more than the first token and native max-count handling |
| Other items in Token locations | Admit only independently verified pickup/grant families. Ordinary fixed majors must include the control above. Reachability includes killing **and retrieving** the reward, not just touching the enemy's room |
| Progressive copies | Remain **chest-only**, all eight chains; Token does not silently turn fixed floor rewards into progressive grants |
| Small keys anywhere | Remain in shuffled **chests** only; no cross-dungeon key grant at a Skulltula. Boss keys/maps/compasses retain existing own-dungeon/destination rules |
| Shop / repeat vendor | Preserve native display and restock rules. A repeatable sale must never supply limitless tokens. Token shuffle does not authorize new shop displays or scrub conversions |
| Gift / one-time Scrub | Token can be admitted only through a proven exact-one native grant with that source's existing once-only gate; otherwise hold tokens away from those kinds during fill. Existing wrapper/item exclusions still apply |
| BossHeart / Freestanding | Existing D27 native five-pickup palette stays unchanged. Generated Token pickups do not authorize those surfaces or Fire Arrows on an unsafe floor |
| Songs, trade items, Gerudo Pass | Existing song placement policy, shared trade-cell holds and native captain hand-over hold remain; no scope expansion |

Sources for existing policies: `03-game-data.md` sections 27, 35–37, 44, 47; `docs/settings.md`; D27, D39.
D27 actually specifies the **BossHeart palette**; the Token refusal and failed experiment are in P27, rather
than an explicit Token decision in D27's text. This specification does not override BossHeart safety.

Every app/CLI/settings-string combination must either generate a complete compatible seed or fail validation
clearly **before writing output**. Intersect source and item restrictions in every fill/filler/swap stage. Do not
fix an invalid assignment after the beatability proof, silently drop Token, silently reenable Chest, lower token
thresholds, change goal/logic, or change a requested option. A restricted destination palette is valid only when
those item/location constraints remain explicit and the requested source set is still all 100. [Required]

The current always-progressive contract requires shuffled chests (`04-world-format.md:137-151`). Therefore
**Token-only, or any selection without Chest, is currently a validation-refusal case**, not a promised new
playable mode. Preserve that clear refusal; changing the progressive policy is outside #30.

### 3.3 Skulltula House and issues #11 / #12

House rewards remain **Gift checks**, not Token checks. Token on/Gift off moves token items but leaves House
rewards native. Token off/Gift on retains native Skulltula drops and existing accepted Gift behaviour. Both on
must compose the two independently. Thresholds remain **10, 20, 30, 40, 50, 100**. Tokens are not spent. [P23/P35; required]

For #11, the 40-token pool contribution must be the existing **Bombchus (20)** / `Item_BombchuBundle_Large`,
not the imported ten-Bombchu value. A substituted 40-token reward uses the native successful hand-over and
`GetReward40` gate, preserving all other thresholds and the father's repeats. Replace the current hold only after
the specific Longshot reward/revisit check passes. This is independent of whether Token shuffle is enabled.
Existing 10–50 previews must name the assigned reward and compose with hints; every supported language archive
keeps its existing handling. A replacement at 20 must not misleadingly teach use of an Echo Gem it did not grant;
verify the native help continuation, not only the final item string. [N7; P35; #11]

For #12, preserve the maintainer policy: **100-token reward is junk by default**, so ordinary players need not
collect all tokens. Proposed separate opt-in permits the **first** 100 reward to hold a real progression item;
it must not be coupled implicitly to Tokens or Gift, and it must not shuffle Event471. Before exposing that
opt-in, prove all 100 actual token items obtainable without the 100 reward, in every accepted seed using it.
Merely reaching Ganon is insufficient. Never put the last token behind that reward, fabricate three tokens,
reduce the threshold to 97, or count the absent N64 checks. If that proof is unavailable, refuse the opt-in
with a specific explanation. Native quest completion and later repeat rupees must survive. [#12; N7; required]

**Kareem: approve default-off Tokens with unchanged presets, and the separate default-off 100-token progression
opt-in described here? Proposed by cs15c; the existing default-junk policy stays unless you change it.**

### 3.4 Tracker

Keep the existing tracker token count source **`PouchData.Item_Token_Gold.StockNum`**. It must grow for a chest
or gift token, and stay constant for a non-token Skulltula reward. Do not substitute kills, collected source
count or `IsGet.Item_Token_Gold`. No save loaded means unknown, not zero. [N5/N7; own `tracker/state.py:577`]

Add source completion interpretation for the new Token check kind using its audited native Hash contract;
show a collected non-token source as collected without increasing the token counter. The current tracker would
classify an unrecognised kind as unknown, and its generic floor-Hash path deliberately does not certify an unset
row as uncollected. Decide Token-specific false/unknown from the proved save layout; do not weaken that policy
for all floor pickups. Missing records/wrong-build saves stay unknown, not “available”. Source status and earned
token count can legitimately differ. [Own `tracker/seeds.py:248-271`, `tracker/state.py:459-478`; N4/N5]

## 4. Logic: the missing three are missing definitions

**Executable result W1:** the current world has **97 live GS Token locations**, all 97 collected by the existing
vanilla search, native token count in the model 97, Ganon goal true. The census has 100. The following three
census definitions have no world location at all, not an unsatisfied rule. Three different imported N64 rows
(`HF GS Cow Grotto`, `LLR GS Rain Shed`, `LLR GS Back Wall`) are correctly `n64_only`; do not resurrect them.
[P11; W1; `remake.toml:157-167`]

| New live check / stable Hash | Native evidence and required conservative access |
|---|---|
| HF GS Lone Tree — `2177746409373494991` | Both age Static files; tree-roll binding, near `(71,167,264)`. No Nocturnal field. In Hyrule Field, require the existing roll/bonk capability and ability to kill/retrieve the low drop. N11's tree graph and the old guide-backed route support either age; day availability remains a recorded conflicting-guide question, so retain a night requirement pending its observation rather than infer day solely from absence of a field. [N9/N11; `r3-census.md:52-58`, `r4-logic-child.md:363-374`] |
| HF GS Wetland Grotto Crate — `9047381233010434881` | Adult Static only, at `(57,126,343)`; adult token-bearing crate appears only after the child's Skullwalltula has died. Entrance near `(40,145,342)` needs the existing supported explosive-opening capability; include actual bomb usability/child strength. Child must reach the grotto and kill `Enemy_Skullwalltula` Hash `8266046215447170481`; adult must revisit and break the crate, kill and retrieve the source. Model a **persistent child event**, not merely adult combat inventory or adult presence. [N9/N10; `r3-census.md:57`, `r4-logic-child.md:372-374`] |
| LLR GS Tower — `2730878115209290675` | Both age Static files, Nocturnal, nighttime-appearance binding, tower vines near `(-147,159,268)`. Accessible ranch/tower region; child Boomerang or adult Hookshot to retrieve it, night, and existing child clock-unlock condition. No requirement for the unrelated tower chest's unresolved upper ledge. [N9/N11; `r3-census.md:58`, `r4-logic-child.md:421-423`] |

**Native/static corroboration of the wetlands cross-age event:** the child's bound
`HyruleField_Child_Level_Prefab_29fc` graph sets `HaveReadHrlField_Note12_Enemy` true from that Skullwalltula's
Dead output. The adult `HyruleField_Adult_Level_Prefab_c022` graph reads that Bool to create the token-bearing
`Obj_BrokenBox_A_06` Hash `4392858802949544986`, while deleting the ordinary `Obj_BrokenBox_A_01` alternative.
The adult Gold Skulltula is created from the token-bearing crate's Dead output. The child's flag is named like a
note but is **not a requirement to read a note or own the Echo Gem**. Preserve both alternative crates, their
sync link and the native event; do not permanently consume the location on breaking its crate. [N9/N10]

The 97 existing rules, regions and source citations remain authoritative unless stronger remake evidence changes
one. `work/native-facts.json` records each current token's region, age reachability, rule and override provenance.
Use the source rule text from the world data, not this report's full-inventory result as a rule. [W1]

Important retained distinctions:

- Child night needs the existing **Time Flows** story event (the clock starts after meeting Zelda); with
  `ensure_tod_access=false`, `at_night` alone folds to true and does not replace that prerequisite.
  Keep the sourced Kokiri/Kakariko/ranch/lake/river overrides. Native Nocturnal marks 24/100, not a licence to
  remove every other conservative night condition. [P11; `04-world-format.md`, Time of day;
  `remake/child_kokiri_forest.toml:40-46`, `child_lon_lon_ranch.toml:11-17`]
- Soil checks need child bugs and attack, tree checks need roll, crate checks need crate access; high checks
  need reward retrieval. `ZR GS Tree` is the bean-seller **soft soil**, not a roll tree. The Echo Gem reaction
  area at the wetlands crate indicates a hint, not proof of an item gate. [P11; N9/N10; `child_zora_river.toml:26-30`]
- Keep remake Hammer requirements, including Fire Temple Boss Key Loop; the moved Spirit Sun-on-Floor check
  is the adult statue-hand Scarecrow/Longshot route. Dungeon doors, combat, ages and source-region access still
  apply even when the reward is no longer a token. [P11; `remake.toml:137-144`; `adult_spirit_temple.toml:15-19`]
- The ranch tree is physically present for both ages, but today's world rule conservatively uses child. Do not
  relax that rule merely because both placements exist. The new tower check's age-specific retrieval rule is
  independently sourced. [N9; W1; `r3-census.md:180`]

All three new rules/events need normal sourced world-data entries, not Python branches. First prove 100 native
identity links, then full-inventory reachability and an ordinary collect-from-start proof that includes the
child-before-adult wetlands event. Preserve temporal return and optional free-time-travel behaviour. A full-
inventory proof alone cannot certify that cross-age ordering. [Required; `04-world-format.md`; #12]

**Kareem: may the three new sourced routes above enter the shuffled world with the conservative Lone Tree night
restriction? Please include the wetlands child-kill/adult-crate route in acceptance; its native flag trace is
stronger than our previous sketch, but no Clawshot gameplay result establishes it yet. Proposed by cs15c.**

## 5. Implementer's proof obligations

No test below has been added or run by Track C. These specify required evidence, not a copied test suite.

### Synthetic tests (construct fixtures in code, no game-derived fixture bytes)

- One physical source represented twice by age/Alternative copies gives one location/pool contribution;
  collection of either copy cannot pay the other again. Stable identity survives actor list reordering.
- Pool conservation: exactly 100 token items with Token on, no synthetic bonus, no change with Token off.
  Demonstrate a non-token source and a token chest in the same seed; restrict both progression **and normal
  filler** before every fill/swap. Include Chest+Token with Gift independently on/off, and the existing
  no-Chest refusal when Token is selected alone.
- Boundary behaviour for native stock and House gates: 9/10, 19/20, 29/30, 39/40, 49/50 and 99/100; first/repeat,
  threshold before/after a token received elsewhere, each once-only flag independent, no token consumption.
  Default 100 holds junk; opt-in cannot prove itself with token #100 behind its own reward. Forty contributes
  twenty Bombchus, not ten. Exercise real event interpretation/grants, not source-text snapshots or mock echoes.
- Persistence semantics: only successful collection commits the source; kill, timeout, culling, water/abyss or
  other destruction cannot commit it. Model separate source records and stock. Parse the selected native-style
  graph/death contracts semantically; an occurrence of a callback name in a byte string is not a proof.
- False/unknown tracker states: non-token source completed/count unchanged, chest token/count increased/source
  still available, already-collected token source, absent save records, wrong-build/missing save. Count is stock,
  not the number of checked locations. Exercise real tracker state construction with synthetic save records.
- Logic counterexamples: child pre-clock night unavailable; wrong age/high-drop retrieval missing; soil without
  bugs; Hammer route without Hammer; wetlands adult-only inventory without the earlier child kill. Verify the
  three new identities, no absent N64 checks, no self-locked threshold progression and no duplicate collection
  across the age-return boundary.
- Settings validation/replay: default/off, Token only, Chest+Token, Gift/Scrub/Shop/BossHeart/Freestanding combined,
  both song modes, own-dungeon/anywhere keys and both time-travel modes. Unsupported item/surface combinations
  fail or are excluded before fill as the compatibility contract says. Replay must retain effective constraints;
  raw unsupported logic overrides (including ignoring night without a native patch) remain refused.

### Dump oracles and executable output smoke

1. Validate all 100 enemy identities/114 copies and all 200 saved collection rows against the **real** supported
   dump. Resolve inherited death/component settings. Demonstrate source-Hash transfer, collected-reason-only
   completion, waiting death signal, and no saved-row write at enemy death. Wrong/stale source data must fail
   before output, with the actual field values printed. Do not create a permanently-dead enemy as a workaround.
2. Read/write/read all affected placement and event formats using the existing dump oracles. For emitted changes,
   inverse only the intended source/grant edits and compare the rest of each tree, including appearance, links,
   room/group membership, threshold tests, gates, story steps and repeat House payouts. Off must not emit a
   global token replacement. Check preservation against the original dump, not a previously patched fixture.
3. If adding actor resources, prove that their effective canonical actor/grant identity, pouch category/special
   behaviour, display identity and dependency references resolve consistently from the **player's** dump. Native
   `ActorInfo` and `GameActorInfo` token rows share index 7895; inventory token rows share index 1281. Both use
   `__RowId`; `ActorInfo.ActorName` differs from the world token's row id. Treat registration, object physics,
   falling/touch and Hookshot/Boomerang retrieval as runtime contracts, not assumptions from a changed filename.
   New rows/resources need independently justified heap/size entries and dependency closure. No copied GPL
   construction, guessed component allocations or duplicate registrations. [N2/N6; P11/P27]
4. Native-token chest payout must be checked through both ordinary chest event families and the native
   `GetPouchContent` grant; confirm the resolved item and count rather than just `Drop__DropActor` text.
   The source-bound callback is not a chest grant requirement. Existing progressive/named-key event changes
   and all 16 language/hint compositions must survive Token/House composition.
5. Run the actual CLI to produce a full Chest+Token seed and the accepted combined options; exercise the
   Token-only/no-Chest validation refusal and observe that it creates no output. Read successful outputs back
   and prove expected placements, complete token pool, beatability/temporal-return
   invariants and 100-reward proof when selected. Reproduce in a second process/PYTHONHASHSEED and compare every
   canonical output byte. Do not call a synthetic graph or a successful fill gameplay evidence.
6. The implementation must run its required four full gates under the round's serialized queue/worker policy.
   Set `OOT_ROMFS=E:/Games/Hookshot/romfs`,
   `OOT_NUP=E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup` and
   `OOT_DUMP=E:/OOTRemake/work/rounds/r14/dump-progressive-cs14d-1e6cde0` as instructed. Token resources may extend
   that fixture's working set: if so build a **new** fixture under `work/rounds/r15/`, name it and verify it against
   the real dump. Never mislabel a failure fixture-only without that comparison. Track C adds no working-set file
   and needs no new fixture. No high-volume seed sweep is necessary for this research specification.

## 6. Kareem's Longshot proof design

### Preparation by implementer and Claude, not Kareem's playing seed

Stage **after specification acceptance**, from
`E:/OOTRemake/tools/test-launcher-template-longshot.bat`. No launchers or game outputs are produced by Track C.
The implementer must supply real output paths, seed/settings/source revision, changed-file manifest and a
read-only resulting-save checker before asking Claude to boot-check. Use a new uniquely named mod/profile under
`E:/OOTRemake/work/r15-tokens/ingame/`, real folders, only that mod under its `HOS_MODS` root, with
`HOS_FS_OVERLAY` unset. Never install in the game folder. Claude alone boot-checks while Kareem's game is closed.

Suitable existing core checkpoint S1: the **ranch/tower-before-pickup** backup has 9 tokens, no Boomerang,
`GetReward10=false`, and unset primary/companion records for ranch tree, ranch tower and Field lone tree.
The Market guard-house Skulltula is already collected in this checkpoint: do **not** use it as a fresh control.
`KF Storms Grotto Chest`, Hash `14818888396401495482`, is unopened. Copy only that described checkpoint plus
account/options into the test's isolated user, as the template does; do not edit the backup. [S1]

For the controlled diagnostic assignment, place Boomerang at **LLR GS Tree** (`341792603838029977`), a native
Hylian-Shield pickup at **LLR GS Tower** (`2730878115209290675`), leave **HF GS Lone Tree**
(`2177746409373494991`) as the token control, and give the unopened **KF Storms Grotto Chest** a token. The 10
House reward should be an obvious non-wallet/non-token item whose actual inventory can be inspected. Make the
full seed/diagnostic distinction explicit; never claim this forced assignment proves ordinary randomized fill.
The core checkpoint is historical and tests mechanisms, not a compatible continued playthrough of a new seed.

### Core packet — estimated 15–18 minutes, not timed or played by this agent

Use only Teleport and the clock; teleport into the Storms grotto bypasses its entrance **for payout testing**,
not as proof of its logic. Stage/check that destination before handoff. Start child in the described checkpoint.
Keep each step's resulting isolated save and log; never replace a profile while Longshot is running.

| Time | Action | Required observation |
|---|---|---|
| 0–2 min | Continue isolated ranch checkpoint; check menu/tracker at 9. Roll the ranch tree, kill the Skulltula, **leave Boomerang uncollected**, leave/re-enter and roll again | Recoverable same reward, not a token; count still 9; source pair not committed in the intervening save |
| 2–5 min | Leave the recovered reward uncollected again; Save and Continue, retrigger tree, then collect | Reward is still recoverable after reload; actual Boomerang inventory/use; tokens remain 9. Both source records set only after collection |
| 5–7 min | Use Boomerang on tower-vine Skulltula at night and retrieve Hylian Shield | Pickup reachable from original high source; shield equips/exists, count stays 9. No native token bonus. Menu closes and Boomerang remains usable |
| 7–9 min | Field lone tree by Kokiri Forest, roll/kill/collect native token | Count 9 -> 10, usable token notice; no Boomerang/shield grant; its source pair sets independently |
| 9–11 min | Teleport into KF Storms Grotto, open designated chest | Count 10 -> 11; only that chest's named open flag changes, no extra Skulltula completion. Correct token text/model and tracker 11 |
| 11–14 min | Teleport to House, talk for 10 reward, talk again, leave/re-enter | Assigned non-token reward exactly once, native threshold satisfied by chest+source token total, no wallet or token bonus; repeat conversation does not pay it again |
| 14–18 min | Save and Continue; revisit ranch tree/tower, Field tree, chest and House | Collected sources stay gone, chest stays open, stock remains 11, House reward remains claimed; no item-bar/dialogue lock |

Require native Longshot loading evidence `mods: <file> <- <path>` for each changed Banc visited, replacement
actor pack(s), changed House/get flow(s) if any, registry/size tables, and native resource closure. A boot log
alone does not prove a lazy-loaded pickup pack was used; if the first-200-resource log cap hides one, obtain the
runtime's resource-load trace for it before accepting. Record the runtime version, actual observations and
read-only save differences (count, all three source pairs, named chest open flag, `GetReward10`). Require
post-reload usable inventory, not only a model/caption. Stop on a lost reward, incorrect count or crash; retain
values and log instead of retrying unchanged.

This short packet does not prove every item, dungeon/soil source, all age-copy transitions or all House
thresholds. The following are **separate bounded packets**, each under 20 minutes, not hidden extra steps in
that estimate:

- **House matrix (estimate 12–18 min with prepared checkpoints):** independently prepared isolated checkpoints
  just below 20/30/40/50, and below 100 for an approved opt-in. One designated token chest crosses each threshold;
  record count, preview, actual reward, once gate, repeat/reload, and the father's repeat rupees after 100. The
  40 case must substitute a reward visibly different from Bombchus. Without suitable checkpoints do not promise
  this time or quietly use a live save. **Kareem: approve test-only count/flag setup on scratch profiles if no
  suitable historical threshold checkpoints exist? Such setup must be declared and cannot count as proof of
  obtaining those tokens through a normal seed.** No original save is edited and no setup ships in seeds.
- **New-route packet (estimate 12–18 min with prepared child/adult checkpoints):** Field lone tree at day/night;
  tower at child/night and adult/night, leaving/collecting one source through the opposite-age copy; wetlands
  adult-before-child-kill gives the ordinary crate, child kills the identified wall Skullwalltula, then adult
  breaks the token-bearing crate and collects its assigned reward. Abandon/reload once before collecting to
  ensure the crate/source can recover. These require a properly staged cross-age profile; no age/flag cheat is
  counted as proof of the child-before-adult transition. Verify `HaveReadHrlField_Note12_Enemy` and both source
  records. If the route differs from N10, stop admission of that rule rather than lower the 100 threshold.

## 7. Verification actually exercised by Track C

No game, launcher, boot-check, game-folder write, save edit, seed generation, suite or sweep was performed.
The real dump and named historical backup were read only. Only the specification enters the repository.

| Command / investigation | Observed result |
|---|---|
| `git -C E:/OOTRemake/work/refs/ootrr-azk rev-parse HEAD` | Pinned revision above |
| `tasklist.exe /FI 'IMAGENAME eq longshot.exe'` and Hookshot equivalent at research start | Neither executable listed; no game started |
| `uv run python E:/OOTRemake/work/r15-tokens/native_facts.py` | Five actor packs, five death tables, saved fields, pouch rows and four real event flows read; world 97/97, count 97, goal true; missing-three definitions printed |
| External decoder Python + `work/decode_graphs.py` | Two current native token/enemy graphs decoded successfully |
| `uv run python E:/OOTRemake/work/r15-tokens/route_facts.py` | Four Field Bancs and three registry/save resources read; all 100 primary and 100 XOR companion rows permanent; source bindings recorded |
| External decoder Python + `work/graph_facts.py`, plus child `29fc` decode | Four current route graphs, current pouch event graph, and child prerequisite graph decoded successfully |
| `uv run --with capstone python E:/OOTRemake/work/r15-tokens/native_evidence.py` | Native callback and Boolean writer inspected; H / H xor 2 writes separated from payout; provenance/hash retained |
| `uv run python E:/OOTRemake/work/r15-tokens/checkpoint_facts.py` | Historical checkpoint suitability/unsuitability observations in S1 |
| Required ruff/full synthetic/full dump gates | **Not run by instruction from Claude in this conversation: documentation-only Track C runs no Clawshot suites and skips the queue** |

Diagnostics, not suppressed failures: the first route probe indexed native Translate as a dictionary and failed;
printed actual Hash/vector/type payloads (`Translate` is a list), corrected that single indexing error and reran
successfully. The old external decoder environment has `ainb` but no `capstone`; printed import failure, then
used isolated `uv run --with capstone` for native analysis. No dependency/lock-file change. A guessed token-specific
flow filename was absent; no such flow is asserted here (the actual shared get/chest flows were inspected).
Initial `~/go/bin/bermuda` command did not resolve on this Windows shell; the discovered `bermuda.exe` path works.

## 8. Handoff and review boundary

- Deliverable: this clean-room specification; no Clawshot implementation or staged game output.
- Review questions are bold above. Claude accepts/revises policy and route admission before Track D starts.
- Known evidence gap: R1 proves only its stated generated token pickup/recovery on an unspecified runtime.
  There is **no new Longshot gameplay acceptance**, no played arbitrary-major substitution, chest token,
  reload-recovery, 100-token proof or House matrix from this track. N1–N11 support the mechanism on our build,
  not an assertion that the whole feature works in game.
- Outstanding for the implementer: independently design delivery/registration from native facts; implement
  all100 source integration and constraints, count/tracker/House behaviour, tests/output smoke and the staged
  packets; retain refusals for anything not safely deliverable. Keep Track C's GPL checkout/report out of that
  implementation context. No code or algorithm from it is licensed by this specification.
- Specification commit and thread-review notification are recorded in the final handoff message.

## 9. Claude's review: accepted with amendments (2026-11-14)

Reviewed by Claude (Opus 5.5) against the clean-room boundary: the specification states game facts, required
behaviour and proofs; it carries no ootrr code, structure or non-game identifiers, and cites ootrr only as a fact
source. Accepted as Track D's only token input, with these amendments, which take precedence over sections 3 to 6:

1. **Phased, production-proof first.** Phase 1 builds only the reward-delivery mechanism and the section 6 core
   diagnostic packet (forced assignments: Boomerang at LLR GS Tree, Hylian Shield at LLR GS Tower, Lone Tree as the
   token control, a token in KF Storms Grotto Chest, a non-token House 10 reward), plus the read-only save checker.
   Fill integration waits for Kareem's result on that packet. Phase 2 is the option itself: all 100 sources, the
   three new locations, fill restrictions, settings, tracker, tests, gates, and the new-route packet. Phase 3, the
   House matrix and #11, may move to a later round.
2. **Decisions taken provisionally (Kareem may change them):** Tokens default off with presets unchanged; the
   100-token progression opt-in (#12) is not in this round and the 100 reward stays junk; the three new locations
   enter the world with the conservative Lone Tree night requirement, admitted only after the new-route packet
   passes; declared test-only count and flag setup on scratch profiles is allowed for the House matrix and never
   counts as proof of obtaining tokens in a normal seed.
3. **Admitted reward families start small.** Phase 1 admits the families its packet proves (a fixed major such as
   Boomerang, a shield, a token). Everything else is excluded at Skulltula locations during fill until proven.
4. **Runtime caution (reported by another project, not tested by us):** an edited `AI.Global` pack crashed Hookshot.
   Prefer a design that needs no `AI.Global` edit; if one is needed, boot-check it on Longshot before anything
   else depends on it.

## 10. Facts amendment for the implementer

cs15c, 2026-11-14, answering Claude's three relayed questions. Based on main `d66d35f`; section 9's phase and
admission decisions are unchanged. This amendment contains native facts and evidence limits, not an actor
construction procedure. No contact with the implementer and no Clawshot code change.

### Additional sources

- **N12 (native/static):** `E:/OOTRemake/work/r15-tokens/amendment_facts.py` ->
  `amendment-facts.json`. Read-only current
  `Event/EventFlow/{Dm_SY_Get,Dm_SY_Get_WithoutPlayer,Dm_SY_GetInEvent,GetPouchContent}.bfevfl.zs`, plus the N8
  native `PouchContent.event.root.ainb` decode. Records named events, resolved actions/queries and branch targets;
  input flow hashes are retained outside the repository.
- **R3 (source-inspected output facts, not played):** ootrr remains pinned to
  `b7d9c86a0897c0423a1b63bc5ea7ac281bb98ea7` (HEAD checked again for this amendment). Exact file/line citations
  below identify factual resource outputs or assumptions only; no third-party helper names, generated naming
  scheme, code or construction sequence are transferred.
- **Relayed/native finding:** Claude's question reports that native `RSDB/Tag.Product.111.rstbl.byml` contains
  binary bit-table data and that only `Obj_Token_Gold` carries `Token_Gold`. This is accepted as the implementer's
  observation, not a new independent Tag-table decode by cs15c. The on-disk compressed resource is
  `RSDB/Tag.Product.111.rstbl.byml.zs`. [R3: `crates/core/src/pickup_pack/tag.rs:6-14`]

### 10.1 Token_Gold is read, but the demonstrated collection callback does not test it

**Native/static — positive consumer:** native `PouchContent.event.root.ainb` implements
`EventQueryCheckTagOnPouchActor`. Its node 138 is `QueryActorIsTagOn` with `TagName=Token_Gold`; a positive result
reaches node 137, returning **3**. If none of that query's recognised tags match, node 123 returns **4**.
This is a tag classification query, separate from the native reason-10 graph and Hash writes. [N8/N12, native
graph nodes 116–123, 126–128, 136–138]

**Native/static — visible effect:** `Dm_SY_Get` Event151 and Event153 call that query; case 3 enters
`GoldTokenFirstTime` through Event152/Event157. That subflow reads native token stock and the father's first-talk
state and requests Navi balloon messages (for example Event13, Event135–140 and Event142). Thus absence of the
tag can omit token-specific first-pickup/threshold advice. It is not accurate to say PouchContent never reads the
tag, nor to equate those advice branches with recording which Skulltula was collected. [N12]

**Native/static — ordinary grant convergence:** in `Dm_SY_Get` Event43, both tag-query case 3 (token) and case 4
(other) reach Event39, then **Event35 `EventTriggerAddOwnToPouch`**. The token tag is not a prerequisite for that
ordinary grant action. Independently, `Dm_SY_Get_WithoutPlayer` Event9 sends case 3 directly to Event3 and case 4
through `Dm_SY_Get:CheckHeart` (Event17) to the same Event3, then Event0 `EventTriggerAddOwnToPouch`. These
observations establish those named paths, not every get-event caller or every possible item. [N12]

**Native/static — collection boundary:** no tag query occurs in native `Item_Token_Gold.root.ainb`'s demonstrated
death-reason-10 completion branch, in the inspected enemy utility Hash-transfer graph, or in the native drop
definition described in section 2.1. The inspected `OneShotGoldTokenDeadAfter` Hash-update body reads the
`GoldTokenGmdHash` blackboard value and writes H/H xor 2; it does not query `Token_Gold`. [N1/N2/N4/N8]

**[INFERENCE / limit]:** once a replacement actually reaches that native reason-10 callback with the right
nonzero Hash, missing `Token_Gold` is not a condition in the demonstrated Hash-update path. The available
evidence does **not** establish the stronger universal negative “no deeper native pickup/drop engine code ever
reads this tag”, or guarantee that an arbitrary replacement reaches reason 10. Those native engine paths were
not exhaustively audited. This is not a played tag-on/tag-off comparison on Longshot. [N4/N8/N12]

**R3 — generated pickup tag facts:** the inspected generated collection-pickup output does **not** assign
`Token_Gold` to its new actor and does **not** add a Tag-table row for that actor. The inspected source also
explicitly disallows assigning `Token_Gold` as an added pickup tag. Its ordinary emitted resource set has new
actor packs, the three actor/pouch registry tables and size-table changes, not a new Token_Gold tag assignment.
An existing Tag table from a previously supplied mod may be retained unchanged; that is not the token feature
editing it. [R3: `crates/core/src/pickup_pack/tag.rs:254-275`;
`crates/core/src/slice/skull_kit.rs:21,70-105`; `crates/core/src/pickup_pack/kit.rs:580-638`;
`crates/core/src/pickup_pack/write.rs:147-159`]

For a source whose assigned reward remains a token, the inspected normal seed output retains the **native**
token drop, including its existing native tag; it does not require a generated token replacement there.
[R3: `crates/core/src/slice/skull_edit.rs:36-42`]

**Reported/ootrr limit:** R1 calls the played object a generated Gold Skulltula token actor, but supplies no
actor name, emitted files, tag dump, build revision or runtime log. The source-output facts above therefore do
not identify the exact artefact used in that reported play. They are not evidence that its tested artefact
carried a tag absent from the inspected output, or that every possible generated token follows the native
token's advice branches. [R1/R3]

### 10.2 New actor pack paths and runtime evidence

**R3 — output facts:** generated non-token collection pickups use **new actor names and new
`Pack/Actor/<new actor>.pack.zs` paths**, rather than globally replacing the existing native token pack.
The inspected standalone output explicitly refuses a destination actor-pack path that already exists in the
base RomFS. The normal seed output likewise writes generated actor packs and corresponding registry entries;
native token assignments remain native as noted above. No third-party generated names or naming scheme are
needed to state this resource distinction. [R3: `crates/core/src/pickup_pack/kit.rs:588-605,631-637`;
`crates/core/src/slice/skull_kit.rs:70-105`]

**R3 — accompanying resource facts:** emitted output registers the new actors in
`RSDB/ActorInfo.Product.111.rstbl.byml.zs`, `RSDB/GameActorInfo.Product.111.rstbl.byml.zs` and
`RSDB/PouchActorInfo.Product.111.rstbl.byml.zs`. Its `ResourceSizeTable` has entries for the new outer pack paths
and newly named parameter resources inside those packs; existing shared native dependencies also need valid
entries. Matching ActorInfo/GameActorInfo row positions are checked by that source. These are output/registration
facts, not proof that the same set is sufficient on another runtime, and not an imported allocation formula.
[R3: `crates/core/src/pickup_pack/kit.rs:455-487,515-536`;
`crates/core/src/pickup_pack/write.rs:103-133,236-257`;
`crates/core/src/slice/skull_kit.rs:88-104`]

**Evidence limit:** R1 is a positive report that a generated actor was used in game. It does not include a
`mods: <new path> <- <path>` line, identify the runtime, or say whether the tested path was absent from the base.
The inspected source's own static tests check registered output and size entries, not a running game's file
opens; none were run by Track C. No new-path runtime-loading experiment or Longshot log was obtained for this
amendment. Consequently, “the source emits new paths with registrations” is established, but **Longshot loading
an arbitrary new path is not certified by this research**. [R1/R3; section 9 runtime caution unchanged]

### 10.3 Other facts relevant to preserving reason-10 completion

| Native fact or evidence boundary | Source |
|---|---|
| Source identity reaches the drop through `GoldTokenGmdHash`; the declared default is zero. The native callback's demonstrated update requires a nonzero transferred value and existing H/H xor 2 saved rows. A generated actor's own new name does not replace that source identity. | N1/N2/N4/N5/N8 |
| The token graph runs its completion callback and death signal only for reason 10, not for every death. Its `PickedUp` death procedure waits for a signal. Enemy death itself does not commit the saved collection pair. | N2/N3/N4/N8 |
| The native graph also asks for physics controller **Body**, rigid body **Body**, and feeds that result to `ExecuteKeepStandingPosture`. A replacement lacking that native resource contract can fail independently of tags or inventory identity. This is a native dependency, not proof that all other physical parameters may be changed safely. | N8, `Item_Token_Gold.root.ainb` nodes 3–4; N2 native controller data |
| Native token blackboard data includes `IsEnableAttention=true` as well as the U64 source Hash. The inspected generated pickups keep get events enabled for repeated acquisition and full-pouch cases (`PlayGetEventManyTimes`, `IsPlayGetEventPouchMax`). | N2/N8; R3 `crates/core/src/pickup_pack/kit.rs:191-200,372-410` |
| The reason for the event-policy precaution is reported by the inspected source, not independently proved by a full-pouch play: an item taken without its get event may miss the completion path. A completed get window, usable reward and both saved source rows after reload are distinct observations. | R3 `crates/core/src/pickup_pack/kit.rs:382-410`; native separation N4/N7/N8 |
| Falling/touch collection and compatibility with high-source retrieval are physical accessibility facts, not substitute completion flags. The inspected generated pickups assume touch collection, falling bodies and an appropriate lifetime; this does not certify every wall, vine, water or abyss case. | R3 `crates/core/src/pickup_pack/kit.rs:203-209,388-410`; N2/N8; section 6's unplayed packet |

These facts do not establish a minimal sufficient list of component edits, new-resource heap sizes, or a
tag-independent guarantee across every native engine entry point. In particular, the evidence supplies no
basis for replacing a missing reason-10 transition by marking the Skulltula collected at death. [N3/N4/N8]

### Amendment verification and handoff boundary

The rebase encountered an add/add conflict because main already contains the accepted specification plus
section 9; the superseded original documentation commit was skipped, retaining main's accepted text.
`git rebase --skip` completed on the requested baseline. Only section 10 is added by this amendment.

`CLAWSHOT_WORKERS=3 uv run python E:/OOTRemake/work/r15-tokens/amendment_facts.py` read the four actual native
flows successfully (187, 17, 783 and 114 events respectively) and recorded the native tag-query branch.
Tasklist showed neither game running at the research-stage start. No game launch, generated actor, output
mod, save edit or native-folder write occurred. No Clawshot gate suite was run, consistent with Claude's
documentation-only Track C instruction. N12 and R3 support the bounded answers above; neither changes the
unplayed status of the phase-1 packet. The commit id is posted to Claude on `cs-r15`, not sent to the implementer.

