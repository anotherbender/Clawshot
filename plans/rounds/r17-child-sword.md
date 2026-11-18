# Round 17: child-return Kokiri Sword equipment fallback

Agent: cs16c (`openai-codex/gpt-6.1-sol`). Branch: `r17/child-sword`.
Docs-only record of the seven read-only findings posted on Bermuda thread `cs-r16`.
No fix is implemented or certified by this document.

## Maintainer decision

**Defer the fix until after 0.2.2.** Claude's decision: this is a logic leak that
only gives the player more capability, not a trap. The proposed ownership guard
below is retained for later implementation; it is not part of the 0.2.2 work.

## Evidence scope

A tester reported completing Forest Temple as adult after an early Door pull,
returning to child, and finding Link holding the Kokiri Sword without opening
KF Kokiri Sword Chest. **The tester's exact version and settings are unknown.**
The observation does not establish their sword ownership before or after return.

The investigation read the supported native dump, build `e0f3ccfa`, and
`E:/OOTRemake/work/r1-research/decoded/evfl_all.json`. The key return/equipment
nodes were independently read from the live, read-only RomFS and matched that
older decoded record. Flow references below mean
`Event/EventFlow/<flow>.bfevfl.zs`, or the corresponding flow key in that JSON.
No game, save, seed output, or gate was run or opened for this investigation.
No implementation code was written. Runtime conclusions not established by the
static data are explicitly marked **[INFERENCE]**.

## 1. Return ordering and the unopened-chest caveat

`Market_Adult_Field_AdultToChild` Event7 calls
`ReplaceEquipmentForEraChange:ReplaceEquipmentForEraChange`; only afterwards
does Event1 set `Sequence_IsChildhood = true`. Thus the equipment subflow runs
while the current age is still adult. The return reserves child Market with
boot event `Dm_TimeTemple_0075` (Event0 of the caller).

An unopened KF Kokiri Sword Chest is not proof that the sword is unowned in a
randomized seed: the sword item can be placed elsewhere. Clawshot maps the item
to `Item_Sword_Kokiri` in `src/clawshot/data/item_actors.toml`, `[items]`.
No tester seed or spoiler was inspected.

## 2. The fallback is conditional, but not ownership-conditional

In `ReplaceEquipmentForEraChange`:

- Event4 queries whether `PlayerStatus.AnotherEraEquipWeapon` is empty.
  Case0 (true) enters Event10; case1 skips the default and enters Event13.
- Event10 queries `EventQueryPlayerIsChild`. On the adult branch, case1 enters
  Event11, which sets `PlayerStatus.AnotherEraEquipWeapon` to
  `Weapon_Sword_Kokiri`. The child branch instead uses the Master Sword default
  at Event5.
- After the intervening shield handling, Event8 waits one frame, and Event0
  copies `PlayerStatus.AnotherEraEquipWeapon` into `PlayerStatus.EquipWeapon`.
- Event6 selects the era's outgoing-weapon bookkeeping. Event7 can copy
  `PlayerWeaponBeforeForceEquipMasterSword` into the other-era weapon field.
  `Dm_TimeTemple_0070` Event3 records that pre-force equipment value.

The Kokiri default is not unconditional on every return: a nonempty other-era
weapon bypasses it. But the empty/adult branch has **no Kokiri Sword ownership
check**. This subflow's pouch-presence queries concern shields only
(Events12, 20, 21 and 23). Boolean/pouch query case0 means true/held; case1
means false/absent (`plans/03-game-data.md`, section 19).

## 3. Explicit equipment writes are not an explicit inventory grant

The equipment subflow writes equipment strings and clears
`PlayerStatus.IsActiveHeadArmor`; it has no pouch-add action, no write to
`IsGet.Weapon_Sword_Kokiri`, and no write to sword stock.
`Dm_TimeTemple_0075` contains no explicit Kokiri Sword inventory grant either.

The native `GameData/GameDataList.Product.110.byml.zs` distinguishes these fields:

| Field | Type | Hash | Native default | Save file index |
|---|---|---|---|---|
| `PlayerStatus.EquipWeapon` | String64 | `0xa95a3521` | empty | 0 |
| `PlayerStatus.AnotherEraEquipWeapon` | String64 | `0xa1f7ee2b` | empty | 0 |
| `PlayerWeaponBeforeForceEquipMasterSword` | String64 | `0x5f670179` | empty | -1 |
| `IsGet.Weapon_Sword_Kokiri` | Bool | `0x405d8a0f` | false | 0 |
| `PouchData.Weapon_Sword_Kokiri.StockNum` | Int | `0xeeb495b9` | 0 | 0 |

The hashed rows were checked in
`E:/OOTRemake/work/r1-research/decoded/gamedatalist.json`.
`RSDB/PouchActorInfo.Product.111.rstbl.byml.zs`, row `Item_Sword_Kokiri`, maps
`ChildEquipment` to `Weapon_Sword_Kokiri`. That distinguishes the pickup actor
from the equipment/ownership identity.

**[INFERENCE]** The fallback can equip the sword while ownership remains absent.
This is not a certified statement about every implicit native actor side effect:
the investigation did not prove the absence of runtime ownership promotion.
A controlled before/after save comparison or watchpoint is needed to settle that
boundary; the tester's report alone does not.

## 4. Consequences for logic and Mido

`Npc_Kokiri_Mido_Child` Event10 checks equipped dynamic-equipment slot0, then
Event12 checks slot4. Its success paths can clear
`KokiriForest_Npc_Kokiri_Mido_Child_Blocker` (Event26) and end blocker AI
(Event32). These are equipment checks, not an `IsGet.Weapon_Sword_Kokiri` check.

Clawshot's effective Mido rules instead require logical `Kokiri_Sword` and either
shield unless Mido is skipped:
`src/clawshot/data/world/remake/extra_fast_start.toml`, the Kokiri Forest and
KF Outside Deku Tree `Showed Mido Sword & Shield` events. Access to the Deku Tree
passes that gate (`src/clawshot/data/world/kokiri_forest.toml`, region exits).
`src/clawshot/data/world/helpers.toml` also uses the sword in
`can_child_attack`, `can_child_damage`, `can_cut_shrubs` and `can_jumpslash`;
`remake/child_deku_tree.toml` retains `can_jumpslash` for defeating Gohma.

**[INFERENCE]** If the unowned equipment is usable, it supplies Mido/Deku access
and sword-combat capabilities that the logical inventory does not contain, even
if `IsGet` stays false. The tester reported holding the sword, not a controlled
attack, unequip/reload, or ownership-flag test. This does not establish that every
seed permits reaching adult return without already obtaining the sword.

## 5. Shuffled pickup consumption, deletion and shadowing

No action in the inspected return flow opens a chest or removes pouch content.
The native KF sword chest is `Obj_TBox_A_02`, Hash `16757992849254467386`, in
`Banc/KokiriForest/KokiriForest_Child_Dynamic.bcett.byml.zs`; its native Dynamic
fields name `Item_Sword_Kokiri` and `Get_StoneOfForest_GetSword`, with no substitute
fields. Reference: the corresponding entry in
`E:/OOTRemake/work/r1-research/decoded/banc_all.json`.

Actual acquisition goes through `GetPouchContent` Event0:
`EventTriggerAddOrRemovePouchContent`, `Num = 1`, `IsEquipDIrect = false`.
Chest-open state is separately stored as `IsTreasureBoxOpen.<actor Hash>`
(`plans/03-game-data.md`, section 44, collection-state correction).

When changing a chest's item, Clawshot removes the vanilla sword-create wrapper
according to `src/clawshot/patch/chest_events.toml`,
`event.Get_StoneOfForest_GetSword`. That wrapper's
`Dm_Kokiri_0063` Event18 explicitly creates dynamic Kokiri Sword equipment with
`EventTriggerPlayerRequestCreateDynamicEquipmentNoRelationPouch`.
For A_06 already-owned branches, `src/clawshot/patch/write.py::patch_tree` sets
`Drop__DropActor_Substitute` to the placed item rather than vanilla ammo/rupees.

**[INFERENCE]** The return fallback does not itself consume/delete the shuffled
sword check. Equipment appearance could obscure the distinction between holding
and owning a sword for the player, but actual duplicate-pickup/menu behavior was
not played. No lost-pickup or runtime ownership-promotion claim is certified.

## 6. Smallest proposed fix shape — not implemented

**[PROPOSAL]** Modify only `ReplaceEquipmentForEraChange`'s incoming-weapon
validation, immediately after its existing Event8 wait and before Event0:

- If the incoming `AnotherEraEquipWeapon` candidate is not `Weapon_Sword_Kokiri`,
  retain it.
- If it is Kokiri Sword, query
  `EventQueryIsExistInPouch(Actor = Weapon_Sword_Kokiri, Num = 1)`.
- If absent, clear that candidate to empty; if held, retain it. Then continue
  through the original equipment-copy and era bookkeeping.

Reuse the existing string and pouch queries. The subflow already validates
saved shield candidates against pouch ownership (Events14/12/18, 20 and 21).
Checking the incoming candidate covers both Event11's fresh default and a
previously saved unowned candidate, rather than fixing only the empty fallback.
Preserve the Master Sword path, legitimate owned weapons, shield handling,
era/quest writes and existing timing. Do not clear real ownership, award a
compensating item, alter the shuffled pool, or teach logic that travel grants a
Kokiri Sword.

## 7. Evidence boundary and later acceptance

**[INFERENCE]** The proposed one-flow ownership guard removes the extra equipped
capability without granting ownership or consuming a shuffled pickup. That is a
proposed correction for a native-data inconsistency, not proof of the tester's
exact inventory or a played fix.

Required evidence before certifying the runtime behavior:

- Obtain the tester's exact Clawshot version and complete settings; both are
  currently unknown.
- On a controlled return, record **before and after** values of
  `PlayerStatus.EquipWeapon`, `PlayerStatus.AnotherEraEquipWeapon`,
  `IsGet.Weapon_Sword_Kokiri`, and `PouchData.Weapon_Sword_Kokiri.StockNum`.
  The transient `PlayerWeaponBeforeForceEquipMasterSword` is useful to inspect
  during the transition, but is not saved.
- Check sword use, unequip/re-equip, reload, and subsequent genuine shuffled
  sword acquisition; distinguish a visual/equipment fallback from an inventory
  grant and from any duplicate-pickup presentation.
- Record the relevant chest-open state independently of item ownership.

These are future maintainer-controlled checks, not checks run by this agent.
The fix remains deferred until after 0.2.2; this commit changes documentation only.
