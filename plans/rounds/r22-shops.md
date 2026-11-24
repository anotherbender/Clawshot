# Round 22 shops — cs22c

Branch `r22/shops`, base `2091387`; model `openai-codex/gpt-6.1-sol`.
Status: potion repair built and focused-tested; tunic gift implementation in progress. All behavior changes are **built, not played** until Kareem's Longshot 3.2.0 checks.
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

## Verification and played limits

Tunic focused checks, staged paired launchers, sweep and gate pending. No played claim is made. No product decision or new option proposed.
