# Round 22 shops — cs22c

Branch `r22/shops`, base `2091387`; model `openai-codex/gpt-6.1-sol`.
Status: potion repair and both tunic gift sources implemented and focused-tested. Staging, sweep and gate pending. All behavior changes are **built, not played** until Kareem's Longshot 3.2.0 checks.
Research/output root: `E:/OOTRemake/work/r22-shops/` (outside this repository).

## Scope and order

1. Repair native potion-shop sale dispatch for the full existing shop palette, including Kakariko's vanilla Half Milk shelf (Item 3), every other potion shelf, and Market.
2. Only after that repair, enable GC Rolling Goron as Adult and ZD King Zora Thawed as shuffled gifts. Preserve native scene-safe grants and cite their complete native trigger chains.
3. Stage private-seed candidate/control launchers on Longshot 3.2.0; control from main. Focused tests, production event-registration coverage, the 200 broad / 50 Defaults / 50 Recommended sweep, and serialized full gate on the frozen merge head.

No game started; no personal seed, game folder or original save is modified. Natural backup saves are read-only. Research facts from GPL documentation are cited, not copied code: sloperinaGZ `docs/FINDINGS.md` (local `work/refs/sloperina-FINDINGS.md`), sections 1 (typed GameData, saved flags, quest enums, save layout) and 2 (flow/actor investigation).

## Initial evidence

- Kareem, Longshot 3.2.0, Clawshot 0.2.6, adult: Kakariko Potion Shop Item 3 (vanilla Half Milk) could not sell its shuffled Deku Shield with no shield owned; no refusal text. Goron Shop's shield sold afterwards. User report is the repro; no game rerun by the agent.
- `patch/gifts.seed_checks` requires every native grant actor to match the mapped logic actor after existing aliases. `SageOfFire/Event18` gives `Obj_Armor_Goron`, `SageOfWater/Event242` gives `Obj_Armor_Zora`, while `item_actors.toml` maps tunics to `Shop_Armor_*`; unsupported gifts are dynamically kept vanilla by `restrict_spec`. The static `remake/gifts.toml` currently has no tunic rows. This explains the silent gift exclusion, not yet a complete native-trigger audit.
- `patch/gift_rules.toml` already classifies both checks as swap; King Zora has a provisional native completion-flag read. Existing source ledger: `plans/03-game-data.md` section 19.

## Potion shops: traced failure and repair

- Both potion sellers call `DisplayShop:Root_Buy`: Market `Npc_Hylia_020_Shop_Child/Event19`, Kakariko `Npc_Hylia_020_Shop_Adult/Event1`. Their shelf instances have only `ShopItemIndex`; the seller's `ShopRef` retains the original stock/release fields. All three Kakariko/Market placement copies are covered by stable shelf Hash.
- `DisplayShop/Event318` checks the selected item's native purchase requirements; its bottle-content arm alone reaches `Event325` (empty bottle). Equipment uses the ordinary capacity/purchase checks. No bottle requirement is removed.
- A concrete non-bottle dialogue gap: the adult Deku Shield offer `DisplayShop/Event554` requests `Shop_01_Shield_Adult` with `ChangeMstxtForActor=true`. The potion sellers' `ActorNameRef` names `Npc_Hylia_020_Shop_Child`; its message file lacks that label in every language. Other missing consumer paths include `Event78` (`Shop_04`, partial-capacity confirmation), `Event98` (`Shop_06`, partial-heart confirmation), `Event45` (`Shop_16`, magic confirmation), full-capacity and ownership refusals. **Inference:** the missing remapped offer accounts for the silent no-purchase report; the repaired runtime path still needs the paired play check. The Goron sale is user-confirmed, not an agent replay or proof of every shared-message branch.
- `patch/shops.py` fills those missing potion labels from the player's native same-language message tables, preserving every existing potion line byte-for-byte. The equipment repeat refusal uses an item-neutral native line, not a false claim about a specific tunic. The common no-quiver label uses the native first no-bow refusal. No added get window, scene, payment, stock or bottle logic.
- Applied whenever a selected potion shelf has a non-bottle sale, regardless of shelf index or normal/Alternative copy. No fill restriction or palette change; native child-tunic and Blue Fire holds remain.
- Inputs/output are already covered by `pack/resources.toml`'s existing `Mals/*.Product.110.sarc.zs` pattern. No new native input or event writer. No new working-set fixture needed.
- Focused command: `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run --with pytest-xdist pytest -n 2 -q tests/test_potion_shops.py tests/test_potion_shops_dump.py tests/test_shops.py tests/test_shop_settings.py`: **62 passed**, 17.52 s pytest time; no game process at stage start. Receipt `work/r22-shops/potion-focused.log`.

## Tunic gifts: native trigger and grant contract

Proposed by cs22c from build `e0f3ccfa`; no reachability rule is loosened. Source-only location citations are in `data/world/remake/gifts.toml`. Decoded native evidence stays outside the repo in `work/r22-shops/tunic-trace/`.

- **Goron:** adult GoronCity Static/Alternative Static bind Prefab118a's `Npc_Goron_DaruniaJr_Adult_a893`; the module reads `SageOfFire_GenerateDaruniaJr`, bomb-hit and quest progress, not tunic ownership. `RSDB/Challenge`'s `SageOfFire` Ready/StopDaruniaJr/TalkDaruniaJr steps select their participant schedules in `Pack/AIScheduleParam.pack.zs`. The TalkDaruniaJr schedule's default `…_C1_T` event row resolves through `RSDB/EventSetting` to `Step02_Npc_Goron_DaruniaJr_Adult_Talk`; conditional slots use native talked/crying Bools. `Event320` routes first versus repeat dialogue; choices and Navi interludes reach `Event38` (Handover_Child dialogue in parallel with a wait), join36, then **Event18**, the existing `Dm_SY_GetInEvent:GetInEvent_NotTurn` grant. Its continuation calls local `Step02_DoorOpen` and `Step02_Npc_Goron_DaruniaJr_Adult_AfterTalk`, reaching **Event13**, which advances the quest to `MoveStatue`. `FirstTalked` is set by pre-grant crying dialogue and is not completion. Keep the existing `Stop GC Rolling Goron as Adult` event requirement; stopping-method changes belong to cs22d.
- **King Zora:** adult ZoraDomain Static/Alternative Static bind Common1b33's red ice and `EventRequestActor_9be2`, Hash `11896564388441894476`, `RequestEventName=SageOfWater_KingZora_IsMelted_Ice`. Graph nodes0/7/8/9 require `isHitBlueFire` and an unplayed melt event. EventSetting resolves to `SageOfWater:KingZora_IsMelted_Ice`; Event209 ends frozen state, the native thanks dialogue reaches fork156 (Handover animation / wait), join158, then **Event242**, `Dm_SY_GetInEvent:GetInEvent_NotTurn_PosCamera`. Event198 dialogue is followed by **Event69**, saving `SageOfWater_KingZora_adult_Talk_Event198`. The existing adult + Blue Fire thaw requirement is retained.
- **Early vanilla-item audit (rule m):** Goron tunic reads in SageOfFire Events185/215 are the Navi heat hint only. Zora tunic reads in SageOfWater Events136/243 affect hint/BGM; the NPC flow's Event184 is separate adult-trade dialogue. None gates either native grant or its trigger. Moving a tunic early does not bypass the source's quest state writes; patching the actor parameter leaves all those writes intact.
- **Native scene contract (rule f):** retain these existing NPC get-item wrappers and continuations; insert no window or scene. GiftChange/plan projects the two `Shop_Armor_*` identities to their native `Obj_Armor_*` gift actors. Native `PouchActorInfo` rows are identical except `__RowId`, verified by the dump test. Shelf actors stay unchanged. Tunics remain admitted at their existing shop/chest destinations rather than acquiring the generic gift-only hold.
- No new event writer, flag or resource input. King Zora's existing tracker completion flag remains; Goron's pre-grant dialogue flag is not promoted to completion.
- Focused tunic/shared-contract run: **90 passed**, 173.66 s; receipt `work/r22-shops/tunic-focused.log`. Metadata citation additions and post-rebase registration proof still require the final focused run.

## Verification and played limits

Tunic focused checks, staged paired launchers, sweep and gate pending. No played claim is made. No product decision or new option proposed.
