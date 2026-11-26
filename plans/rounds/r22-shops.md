# Round 22 shops — cs22c

Branch `r22/shops`, base `2091387`; model `openai-codex/gpt-6.1-sol`.
Status: **READY (merge)**, gifts-only. Code freeze `13bc4b27e4`: 4c/4d played PASS, 60 focused contracts passed, replacement full gate passed. Lock released19:35 on2026-11-25 after the assigned Claude12b/cs22g13a turns. No rebase/re-freeze or repeated sweep. Potion hunt closed; the unproven fill remains absent from the tip and retained on `r22/shops-potion-held` at `1cfbb7c4da`. Subsequent receipt changes are documentation only.
Research/output root: `E:/OOTRemake/work/r22-shops/` (outside this repository).

## Scope and order

1. Merge the two played tunic gifts independently: GC Rolling Goron as Adult and ZD King Zora Thawed. Their production code and native grant contracts are unchanged from gated `b5e6eb0`.
2. Hold the potion-label hypothesis on `r22/shops-potion-held`, with no dormant helper, registration or exclusive tests in the gifts-only tree. Investigate and reproduce the seller-specific shield refusal before choosing a fix.
3. Keep seed 922301's existing staged mods and every played profile immutable. Use a fresh, identically edited candidate/control save pair for the never-owned Deku Shield with Mirror equipped. No rebase, new settings decision or repeated sweep.

No interactive game or headless boot started by cs22c; no personal seed, game folder or original save is modified. Claude waived the new fixture's boot because it reuses the played v1 mods. Natural backups are read-only. Research facts from GPL documentation are cited, not copied code: sloperinaGZ `docs/FINDINGS.md` (local `work/refs/sloperina-FINDINGS.md`), sections 1 (typed GameData, saved flags, quest enums, save layout) and 2 (flow/actor investigation).

## Initial evidence

- Kareem, Longshot 3.2.0, Clawshot 0.2.6, adult: Kakariko Potion Shop Item3 (vanilla Half Milk) could not sell its shuffled Deku Shield; no prompt. His corrected history below establishes no **Deku** Shield ever owned, with Hylian and Mirror owned and Mirror equipped. Goron City then sold the Deku Shield. User report is the repro.
- `patch/gifts.seed_checks` requires every native grant actor to match the mapped logic actor after existing aliases. `SageOfFire/Event18` gives `Obj_Armor_Goron`, `SageOfWater/Event242` gives `Obj_Armor_Zora`, while `item_actors.toml` maps tunics to `Shop_Armor_*`; unsupported gifts are dynamically kept vanilla by `restrict_spec`. The static `remake/gifts.toml` currently has no tunic rows. This explains the silent gift exclusion, not yet a complete native-trigger audit.
- `patch/gift_rules.toml` already classifies both checks as swap; King Zora has a provisional native completion-flag read. Existing source ledger: `plans/03-game-data.md` section 19.

## Potion shops: original hypothesis (withdrawn 2026-11-25)

- Both potion sellers call `DisplayShop:Root_Buy`: Market `Npc_Hylia_020_Shop_Child/Event19`, Kakariko `Npc_Hylia_020_Shop_Adult/Event1`. Their shelf instances have only `ShopItemIndex`; the seller's `ShopRef` retains the original stock/release fields. All three Kakariko/Market placement copies are covered by stable shelf Hash.
- `DisplayShop/Event318` checks the selected item's native purchase requirements; its bottle-content arm alone reaches `Event325` (empty bottle). Equipment uses the ordinary capacity/purchase checks. No bottle requirement is removed.
- A concrete non-bottle dialogue gap exists: adult Deku Shield offer `DisplayShop/Event554` requests `Shop_01_Shield_Adult` with `ChangeMstxtForActor=true`; the potion seller's own table lacks it. **Withdrawn inference:** that absence explains the silent no-sale. The control successfully sold the shield and both tunics, so the missing labels do not establish the cause. The original Kokiri table contains the requested offer in both staged archives; actual fallback/rendered wording is not logged. The held fill also omits `Shop_33`, used on the first adult Deku-capacity refusal.
- The original held `patch/shops.py` implementation filled missing potion labels from native same-language tables, preserving existing potion lines. It added no get window, payment, stock or bottle logic. The equipment repeat refusal was item-neutral; the no-quiver line came from the native no-bow refusal.
- That held implementation applied to non-bottle sales at every selected potion index/copy. It is now removed from the gifts-only tip, not left disabled. Native child-tunic and Blue Fire holds are unchanged.
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

## Played receipts and approved split — 2026-11-25

Claude accepted these receipts and approved a gifts-only head. Human no-repeat/door observations remain
distinct from typed saved inventory. All 11 gift-profile saves equal their `save-work` counterparts;
no live profile, mod, natural backup or personal seed was modified.

| Candidate | Typed saved result | Native continuation/once state | Own-arm load proof |
|---|---|---|---|
| 4c / 03 Goron | Ice Arrows stock 0->1 and IsGet false->true in slots03/04; Goron Tunic remains 0 | FirstTalked false->true is pre-grant, not independently completion. Step_SageOfFire advances Ready -> StopDaruniaJr -> MoveStatue. Kareem: doors open, no repeated grant. | log5481, `Event/EventFlow/SageOfFire.bfevfl.zs`, candidate-v1 |
| 4d / 04 Zora | Mirror Shield stock 0->1 and IsGet false->true in slots04/05; Zora Tunic remains 0 | `SageOfWater_KingZora_adult_Talk_Event198` and `HavePlayedEvent.SageOfWater_KingZora_IsMelted_Ice` false->true. Kareem: no repeated grant. | log9946, `Event/EventFlow/SageOfWater.bfevfl.zs`, candidate-v1 |

Both logs identify Longshot 3.2.0 source `1f0bf123` and end normally. Typed receipt:
`work/r22-shops/played-tunics-20261125.json`. Controls 03/04 were not played.
01 candidate did launch and load its own USen archive (log79), but its only progress save remains the
Nov24 fixture: 148 rupees, all three tested gear stocks 0, Deku IsGet true. No saved purchase is evidenced.
4b candidate passed the reported partial sale/refusal: its tutorial bottle check correctly gave the seed's
Rupees (20), with its native present flag set; nuts then filled 15->20 for 10 rupees.

The split removes only potion-specific constants/helper/message registration and their two exclusive test
files. Gift code, gift definitions/rules, fill, pool and settings are untouched. Thus the binding 200/50/50
sweep and comparison against 5bc5577 remain applicable to the gift placement change; no new sweep is proposed.
The earlier combined full gate is historical, not a substitute for the gifts-only replacement gate.

## Potion trigger hunt and final reproduction fixture

Kareem's corrected 0.2.6 history: natural adult play, Hylian and Mirror shields owned, **Mirror equipped**,
Deku never acquired; he left a shuffled Deku pickup at Zora's River. Daytime after the shop opened,
English, affordable price10 and sufficient rupees. Selecting the Kakariko shelf produced **no prompt**;
the Goron City shop then sold the same Deku Shield. This argues against a purely global inventory-capacity
refusal, but does not expose the context-sensitive engine query's inputs.

| Candidate difference | Dump evidence and limit |
|---|---|
| Never-owned versus removed shield | Old fixture retained Deku IsGet and HavePlayedGetEvent true with StockNum0. Native defaults are false/false/0. Its PouchData Struct has only StockNum; no extra saved counter. DisplayShop has no explicit Deku IsGet query. CheckBuyResult, CanAddToPorch and CheckIsSoldOut are opaque engine queries, so history-sensitive behavior is plausible, not established. HavePlayedGetEventAtShop is reset at each Root_Buy and must not be assumed to mean lifetime ownership. |
| Stronger shield ownership/equip | Old fixture had Hylian stock1/equipped, Mirror stock0. No explicit Mirror/rank/equipped-shield comparison appears in the purchase flow or PouchActorInfo. Shield category/subtype and era usability exist, not a visible rank predicate. The new fixture matches Mirror ownership and equip; Goron success limits any global-only explanation. |
| Alternative/night | Alternative is the post-burning story scene, not night. Normal and Alternative sellers share the same ShopRef; both Item3 copies are patched. Time checks restrict the door, not the purchase. No Alternative/night branch in the buy path. |
| Price/rupees | Affordable is10 in the test, matching Kareem. Original destination Half Milk price is20; cheap-shield applies only at Kokiri. CheckBuyResult has an insufficient-rupees path with an existing potion refusal line, not the reported silent selection. |
| Language | Kareem and staged play use English/USen. No language predicate occurs in the event flow; language selects the message archive externally. The held fill covered all16 archives, not proof that labels caused the failure. |
| Child/adult seller | Kakariko adult and child Market are separate actors/packs; adult inherits the child actor's message/ShopRef identity. Both call DisplayShop. PlayerIsChild selects shield dialogue; no child Kakariko seller placement exists. Both original and fixture are adult. |
| Shelf index/links | Item3 is native index2, not index3. Both copies link to the correct seller. Native Half Milk GoodsList[2] has StockNum -1 and **no Release**; replacement preserves that and adds only price offset. No vanilla empty-bottle release remains there; only DisplayShop's selected bottle category checks empty bottles. |
| Shuffle setting | No Shop shuffle keeps Half Milk native, so cannot yield this shuffled shelf shield. Settings change placement/price, not DisplayShop. Bender's separately reported no-shuffle logic gap is not established as this runtime failure. |

Specific silent paths: `DisplayShop/NormalFlow/Event216` handles sold-out query results1/2, but has no
case0, a plausible silent path if that result is returned. A capacity refusal through Event560 first requests `Shop_33`,
missing from **both** staged potion tables. The held candidate adds later `Shop_32`, not that first line.
Neither query's actual return value or the engine's unhandled-case behavior is exposed by the dump.

After a no-sale attempt, explicitly Save: `KokiriForest_Shop_SelectActor_Shield_Deku` starts false.
Event141 sets it after the first capacity refusal; Event558 also sets it on an adult purchase.
A true flag **with no sale** therefore distinguishes that refusal path from the unhandled Event216 result.
Do not replay the same failed select merely to get a different line.

Claude requested reproduction before flag isolation. Final paired launchers:
`05-kak-never-owned-{control,candidate}-v4.bat` under `work/r22-shops/ingame`; older v2/v3 drafts are unused.
Both use the existing seed922301 mods and fresh, byte-identical users. From the natural adult copy:
Deku StockNum1->0, IsGet true->false, HavePlayedGetEvent true->false; Mirror StockNum0->1 and both
history flags false->true; clear stale stored Deku String64 `0x2342b619`; equip Hylian->Mirror.
Eight fields, 30 changed bytes. Hylian ownership, age, quest, bottle and rupees unchanged.
All native per-item Struct namespaces were checked; the one additional per-item Bool is unsaved
and absent from the source save, so no invented field is written.

Both launcher dry-runs exit0 and copied saves match SHA256
`1a761c3dea89e7485bb58c84dc679fa6481b4047d890f0cd07752ec1614a5c7b`.
Manifest `work/r22-shops/repro-pair-v4.json` records every edit. PLAY.md 4e is a five-minute,
control-first diagnostic; candidate only if control fails. Claude waived the line12 boot: the existing mods
already booted and played; a startup check does not load the fixture. Queued boot worker cancelled before
acquisition; no new boot or boot-lock claim. Line13's gifts-only gate now waits **Claude's line12b `LOCK RELEASED claude`**, not cs22e directly; source stays frozen at 13bc4b2 on its own parent.

## Gifts-only replacement freeze

Focused proof after removing the potion implementation: **60 passed in 268.83s**, `-n2`,
`CLAWSHOT_WORKERS=1`, `OOT_ROMFS=E:/Games/Hookshot/romfs`; receipt `work/r22-shops/gifts-only-focused.log`.
Command: `uv run --with pytest-xdist pytest -n2 -q tests/test_tunic_gifts.py tests/test_tunic_gifts_dump.py tests/test_shops.py tests/test_shop_settings.py tests/test_event_registration.py`.
This includes real-dump event registration and both native tunic contracts. Gift production/placement
code is unchanged from b5e6eb0; retain its binding sweep. The gifts-only withdrawal commit is the new
code freeze **13bc4b27e40a6de4d42719aa0483bc7c6397e6ea**; full format/lint/synthetic/dump gate is line13, after Claude's line12b release. Subsequent receipt notes are documentation only, not a new code freeze.

## Final potion disposition — 2026-11-25

Kareem's 0.2.6 report remains valid but **unreproduced**: natural adult, Mirror equipped and Hylian owned,
Deku never acquired; daytime, English, affordable10, enough rupees; Kakariko selection had no prompt,
then Goron City sold a Deku Shield. All four exercised comparison states (the child one is a separate capacity check):
1. 01 control: adult, Hylian equipped/Mirror absent, Deku stock removed but both history flags retained;
   shield and both tunics sold. This did not reproduce the silent selection.
2. 02 candidate: child, nuts15/20, partial non-bottle sale succeeded and full-bag repeat refused.
   This is a separate capacity-path comparison, **not** an unpatched Deku Shield reproduction.
3. 05 control v4: adult, Mirror equipped, Hylian owned, Deku stock0 and both history flags false;
   Deku stock0->1, rupees148->138, both history flags false->true; Mirror stayed equipped.
   `KokiriForest_Shop_SelectActor_Shield_Deku` false->true accompanies the successful adult confirm.
4. 06 historical control v5: adult, Mirror equipped/Hylian owned, Deku never acquired, **no bottle ever acquired**
   (all five slots invalid/Empty, all26 bottle history flags false), unchanged seed1942692550 mod.
   It sold the Deku Shield: stock0->1, rupees148->138, Deku IsGet/HavePlayedGetEvent and SelectActor
   false->true; Mirror remained equipped. Zero valid bottles and all bottle history flags remained false.

01 candidate launch alone has no saved purchase witness and is not counted as another shield sale.
The v4 control's four saves equal save-work. Own-control USen loads at log79, adult seller pack at5217;
Longshot3.2.0 source1f0bf123, normal close7997. Receipt: `work/r22-shops/played-4e-control-v4-20261125.json`.
Kareem skipped the v4 candidate as instructed. Leads only: Event216 has no case0; Event560's first
`Shop_33` is missing from both staged potion tables. Neither lead establishes the failure's cause.
**Claude's final decision:** hunt over, no more fixtures or speculative candidate. Potion fill stays on
`r22/shops-potion-held`, unmerged. Gifts-only line13 proceeds unchanged; the original report is not dismissed.

## Authorized historical seed and v5 control — 2026-11-25

Kareem authorized his abandoned 0.2.6 seed1942692550 for this investigation only. First copied its mod,
manifest, log and saves into `work/r22-shops/repro-1942692550/snapshot`; all content reads use that copy.
No write in the original folder, no unrelated placements reported, no regenerated historical seed.

Static comparison against922301 control: Item3 is identical in both Kakariko copies (Deku Shield,
index2, price10, unlimited stock, no Release). Seller ActorParam/ShopRef, both potion USen tables,
DisplayShop/adult seller/ShopGet are identical. Neighbours1/2/4 are Bug/Fish/Nuts10 instead of
GoronTunic/ZoraTunic/Bug. The child flow differs only in the tutorial reward; the common get graph's
generated bindings differ, with no demonstrated pre-offer cause.

All six save slots and all six save-work slots already own the Deku Shield; no adult pre-purchase slot
survives. The copied log proves the correct mod's USen at80, normal adult Kakariko Banc at123995/123996,
and adult potion seller at124013, but logs no selected-item/query result. Every retained save has zero
valid bottles and false bottle acquisition flags: a new lead, not failure-moment proof.

Claude requested **one faithful control**, no candidate/boot yet. Final launcher:
`work/r22-shops/repro-1942692550/ingame/06-kak-never-bottle-control-v5.bat`.
Its246 mod files match the copied historical mod byte-for-byte. The v4 fallback save keeps Mirror
equipped, Hylian owned, Deku stock/history false and148rupees. All five bottle slots are invalid/Empty;
all26 IsGet/HavePlayedGetEvent bottle-form flags match the historical saves (false).
Relative to v4, eleven fields change: BottleA/B validity, BottleA Bug->Empty, and both history flags
for Item_Bottle, Item_Bottle_Letter, Item_Bottle_Fish and Item_Bottle_Bug. Fourteen bytes change;
the manifest records field hashes, offsets and before/after values. Other bottle fields already matched.

Dry-run exit0, copied-save readback matches SHA256
`2a48f6afae8da6488a174681463b3797a213e9a7b3936eb02a03da48344052b1`.
Receipts: `repro-1942692550/{static-and-save-potion-facts.json,v5-never-bottle-control.json,v5-never-bottle-control-dry-run.log}`.
PLAY.md4f: five minutes, select once, Save even on no prompt, read SelectActor afterwards. If it sells,
stop hunting; if it reproduces, derive the fix/test from that result before building a candidate.
The unused slot-only draft is not a second play arm. No boot performed or required for this unchanged mod.

### v5 played result: sold; hunt closed

Kareem bought the shield and saved. All three persisted profile slots equal save-work. Own historical-control
USen loaded at log80 and adult potion seller pack at2873; Longshot3.2.0 source1f0bf123, normal close5038.
Typed receipt: `repro-1942692550/played-v5-never-bottle-control-20261125.json`.
The four comparisons and the two still-unproven silent-path leads are consolidated above. No state tried
reproduced the reported failure; this is not a proof about every possible runtime state. No production
fix or regression test is claimed for the potion report. No more fixtures; held fill remains unmerged.




## Gifts-only full gate and final handoff — 2026-11-25

Gated **13bc4b27e40a6de4d42719aa0483bc7c6397e6ea** on its own parent, without rebasing to moved main.
Acquired only after Claude's explicit12b release (18:07) and cs22g's explicit13a release (18:28);
both posts are preserved in `gifts-only-gate-13bc4b27e40a/release-witness.txt`.

| Check | Result |
|---|---|
| `uv run ruff format --check` | PASS |
| `uv run ruff check` | PASS |
| Whole synthetic, `--extra ui`, `-n8`, workers4, all OOT variables unset | 4,402 passed,842 skipped,24 existing warnings;462.79s |
| Full dump, `--extra ui`, `-n8`, workers3 | 840 passed,24 existing warnings;3,568.53s |

Exact-image CIM player count was0 at every stage start. Dump inputs remain the read-only supported
romfs/NUP/r19 layered dump recorded above. No failure, retry, fixture weakening or new sweep.
The unchanged gift production/placement code retains b5e6eb0's binding200/50/50 comparison against5bc5577.
All logs and the successful machine receipt are in `work/r22-shops/gifts-only-gate-13bc4b27e40a/`.
The runner removed only its own lock and posted **LOCK RELEASED19:35**.

**READY (merge): tunic gifts only.** Both native grant/play receipts are accepted; the potion report is
unreproduced, its label fill is not shipped, and no more fixtures or speculative fix are proposed.
This final documentation commit records the investigation and gate; it does not change or re-freeze
the tested code. Claude owns the later merged-tree check on main.

