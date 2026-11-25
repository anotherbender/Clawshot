# Round 22 shops — cs22c

Branch `r22/shops`, base `2091387`; model `openai-codex/gpt-6.1-sol`.
Status: implementation, paired staging, focused contracts, full gate and candidate sweep complete. **READY (play-held)**: all behavior changes remain **built, not played** until Kareem's Longshot 3.2.0 checks.
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
- Initial tunic/shared-contract run: **90 passed**, 173.66 s; receipt `work/r22-shops/tunic-focused.log`. Rebased onto current local main **5bc5577**, retaining its deterministic scrub-shield coverage without re-pinning. Final focused run: **148 passed**, 405.95 s, including both potion/tunic suites, shop/gift shared contracts and **tests/test_event_registration.py** in the real-dump tier. Narrow format/lint clean. Receipt `work/r22-shops/focused-rebased.log`. The first format check printed two potion formatting differences; applied those exact differences before the successful run.

## Longshot 3.2.0 staged checks

Private seed **922301**; candidate and main `2091387` control are independently composed by the same recipe (Chest + Shop + Gift, affordable shuffled shelves, forest/door open, free-time-travel logic). Deterministic, pool-preserving cycles put the same four test items on the same potion shelves. Candidate includes both new gift checks; main retains their native tunics, so other random assignments are not claimed identical. Production external-placement validation passes. Full beatability replay restores the spoiler's omitted fixed native rewards: **18 candidate / 23 control spheres**, all six test targets reachable. The first replay mistakenly used shuffled-only spoiler placements; printed its stalled inventory, restored the 1,031 fixed rewards, then proved the complete assignments. No reroll or product-rule change.

Packet root: `E:/OOTRemake/work/r22-shops/ingame/`. Every `*-candidate-v1.bat` has a `*-control-v1.bat`, pins **Longshot 3.2.0** at `builds/stable/v3.2.0/bin/longshot.exe`, unsets `HOS_FS_OVERLAY`, and loads only its arm's mod. Each case/arm has a separate disposable `user-*` save folder. All **eight cmd dry-runs exited 0**, copied-save readback matches its fixture, and binary readback proves both native grant wrappers/continuations plus all-language missing-label difference. Receipts: `stage-proof-{candidate,control}.json`, `launcher-fixtures.json`, `launchers.log`, and `*-dry-run.log`.

Natural saves: the post-Forest adult backup (Temple of Time thumbnail) for cases01/03/04; the after-Jabu child backup (Zora's Domain thumbnail) for case02. Both gift checks are unclaimed, both tunics/Ice Arrows/Mirror Shield absent. Adult has 148 rupees and an empty bottle; child has 58 rupees and 20/20 nuts. **Only case01 has one documented edit**, applied identically to both arms: `PouchData.Weapon_Shield_Deku.StockNum` 1→0 (one changed byte). The scanned natural adult backups had the Deku Shield; this recreates Kareem's no-shield condition without age/story changes. Original backups remain untouched; cases02/03/04 are byte-identical natural copies.

Run control then candidate for each pair; close Longshot between arms. Debug **teleport and clock only**; never debug age change. Do not inspect a map after a teleport. Record visible inventory/rupees and the log proof, not just a correct-looking shelf.

| Pair (each filename ends `-{control,candidate}-v1.bat`) | Estimated total for both arms |
|---|---|
| `01-kak-potions` | 8–12 min |
| `02-market-potion` | 6–8 min |
| `03-goron-gift` | 10–14 min |
| `04-zora-gift` | 14–20 min |

Each launcher is below 30 minutes; four independent natural-break pairs total approximately 38–54 minutes.

1. **Kakariko potion sales:** `01-kak-potions-*`. Continue the adult Temple of Time copy; teleport to Kakariko if desired, set daytime, then walk into the potion shop. Confirm the Deku Shield is absent. Select the shield (vanilla Half Milk, Item3), accept, and inspect inventory and rupees. Candidate: readable adult offer, one shield added, exactly10 rupees charged; main control: the old missing-offer/no-sale behavior, not a claimed played result. Then try the Goron Tunic (Item1) and Zora Tunic (Item2), each10 rupees; candidate should sell and show/equip both normally, control retains missing generic non-bottle dialogue. Retry an owned tunic: candidate must refuse clearly with no additional charge. Do not infer success from a model alone. Keep `mods: Mals/<active-language>.Product.110.sarc.zs <- <candidate/control mod path>` from the arm's `longshot_log.txt`. This also exercises tunics remaining obtainable in potion stock.
2. **Market partial-capacity sale:** `02-market-potion-*`. Continue the child Zora's Domain copy. Outside dialogue, use five nuts so the bag is15/20. Teleport to child Market if desired, set daytime, then walk into the potion shop and select Deku Nuts(10), Item3. Candidate: native partial-capacity confirmation, accept, nuts15→20 and rupees58→48; no empty bottle should be needed. Main control: old missing `Shop_04` confirmation prevents the partial sale. At full capacity, retry: candidate must refuse clearly without charging. Keep the active-language Mals load line. Do not buy bottle contents for this test.
3. **Rolling Goron gift:** `03-goron-gift-*`. Continue the untouched natural adult Temple of Time copy. Teleport to Goron City if desired; let its native arrival scene finish. Stop Darunia Jr with a bomb, talk, and complete the fire-temple/Volvagia conversation until the native hand-over. Candidate: **Ice Arrows**, not the Goron Tunic; control: **Goron Tunic**. Inspect the inventory after control returns, reopen dialogue and re-enter the area: no second grant, doors/story progression intact, no stuck reaction/fade. Keep `mods: Event/EventFlow/SageOfFire.bfevfl.zs <- <arm mod path>`. Do not buy the tunic first or use another shuffled check.
4. **King Zora gift:** `04-zora-gift-*`. Continue the untouched natural adult copy. Use the existing empty bottle: collect Blue Fire in Ice Cavern (teleport to its entrance is allowed; no map check), return to adult Zora's Domain and release it beside King Zora's red ice. Let the complete native thaw/thanks/handover finish. Candidate: **Mirror Shield**, not the Zora Tunic; control: **Zora Tunic**. After control returns, inspect inventory and re-talk/re-enter: no duplicate grant or stuck fade/camera, normal King Zora interaction remains. Keep `mods: Event/EventFlow/SageOfWater.bfevfl.zs <- <arm mod path>`. No injected bottle, ice/story flag or age edit.

Runtime-load lines and observed outcomes are still for Kareem to supply. No agent game launch or boot check was performed; Claude owns boot checks.

## Verification and played limits

Gated frozen head **b5e6eb02edf9850fb115e882246ecd6067045273**, on base `5bc5577`; kept frozen through subsequent MAIN MOVED notices as Claude instructed. The final receipt commit changes this round file only. Staged gameplay control remains release main `2091387`. No new setting or product-scope decision proposed.

### Full gate

Owned lock acquired after Claude's line7 authorization and cs22d's full-gate release. Explicit existing-lock guard exits73 before writing owner.txt; isolated occupied/fresh-lock smoke passed without touching the real lock. Every stage-start player check was off (bootchecks excluded).

| Check | Result |
|---|---|
| `uv run ruff format --check` | PASS |
| `uv run ruff check` | PASS |
| Synthetic, `-n8`, `CLAWSHOT_WORKERS=4`, all `OOT_*` unset | 4,408 passed; 861 skipped; 24 warnings; 463.79s |
| Dump, `-n8`, `CLAWSHOT_WORKERS=3` | 858 passed; 24 warnings; 3,196.61s |

Dump environment: `OOT_ROMFS=E:/Games/Hookshot/romfs`, `OOT_NUP=E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup`, `OOT_DUMP=E:/OOTRemake/work/rounds/r19/sword-layered-dump`. Existing resource patterns cover all changed files; no fixture extension needed. Warnings are pytest's existing iterator-parametrization deprecation.

### Sweep and immutable main comparison

Candidate only, six workers, same exact recipe/seed pairs and effective CS1 strings as the published shared main **5bc5577369d429d426dc2059461918e41b5c5302** baseline at `work/rounds/r22/main-5bc5577-sweep/`. No duplicate main sweep. Production native setup captured before generation; each generated candidate passed the goal oracle and normalized-pool multiset assertion. Placement digests use the producer's sorted item-pair list encoding; comparisons below are counts only.

| Recipe | Seeds per arm | Exhausted main/candidate | First-try failures main/candidate | Max attempts main/candidate | Identical placements / spheres | Tunic gifts replaced / shuffled |
|---|---:|---:|---:|---:|---:|---:|
| Broad | 200 | 0 / 0 | 0 / 0 | 1 / 1 | 0 / 0 | 399 / 400 |
| Defaults | 50 | 0 / 0 | 1 / 1 | 2 / 2 | 50 / 50 | 0 / 0 |
| Recommended | 50 | 0 / 0 | 2 / 2 | 2 / 2 | 0 / 0 | 99 / 100 |

Defaults does not select Gift and is the identical control. Broad and Recommended are binding cohorts for the new gift sources. Potion shelves held native equipment in254 Broad and69 Recommended assignments; this count excludes non-bottle ammo/refills whose names begin `Buy`.

### Receipt recovery and handoff

All measured stages exited0. The wrapper then failed only while looking for `<head>-summary.json`: the external sweep CLI had used the literal `sweep` argument as its output label and correctly written `sweep-summary.json` / `sweep-rows.jsonl`. Printed the cause and complete sweep payload, corrected the external argument dispatch, and finalized only the existing results; **no test or seed was rerun**.

Original rows created03:06:08; rows and summary last modified03:14:43 on2026-11-25, matching this run. Finalization checked all300 recipe/seed pairs, successful final fill attempts, effective-settings equality and binding-source totals; preserved original receipts and copied them to the head-qualified paths. `gate-b5e6eb02edf9/result.json` records the post-processing recovery. Owned lock removed and **LOCK RELEASED** posted03:16.

Receipts under `E:/OOTRemake/work/r22-shops/`: `gate-b5e6eb02edf9/` (format/lint/synthetic/dump/capture/sweep logs and final result), `gate-b5e6eb02-runner.log`, `b5e6eb02edf9-{summary.json,rows.jsonl}`. The packet/checklist above remains play-held; no runtime-load or gameplay pass is claimed. Maintainer merge waits for Kareem's checks.
