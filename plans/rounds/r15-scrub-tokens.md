# Round 15 Track D: scrub softlock and clean-room tokens (cs15d)

Branch: `r15/scrub-tokens`, starting main `1db6e63` (0.2.1).

## Contracts

- Issue #26 first. This is a stranger's 0.2.0 seed 1057962893, hash D92DD1D0CC9D, Hookshot 2.1.0; **not Kareem's seed**.
- Required repository/round architecture, world format, decisions, scrub/shop evidence and issue read. No issue comment posted.
- Historical checkout: `E:/OOTRemake/work/r15-scrub/v0.2.0`, detached tag `v0.2.0` (`9f67400`). All research/output under `E:/OOTRemake/work/r15-scrub/`.
- No game started, no game/Longshot directory written, no community seed output inspected. No merge/push/version bump.
- Token clean room: only Claude's accepted Track C specification, our repository and dump. No prohibited source read or search. Claude accepted main `eff7dab`; section 9 amendments were read first while scrub gates queued. No token implementation starts before scrub commit/rebase.
- Standing player-check rule (Claude, 2026-11-14): Noclip is allowed for movement/access, never as logic-route proof. Inventory, flag and age cheats remain forbidden unless a checklist declares an exception; none is declared for the token core packet. Its checklist records Map Teleport to Kokiri Forest, ivy beside Mido's house, the cover at (-51.934,121.575,-62.823), and the shaft landing at y≈104.07. These access coordinates were independently read from the real child Bancs; traversal remains unplayed.
- Read-only access preflight of accepted `2026-11-07_llr-tower-before-pickup/slot_01/progress.sav`: Deku Shield, Kokiri Sword, Slingshot and Fairy Ocarina owned; Hylian Shield stock 0 / IsGet false; Song of Storms not learned. The checkpoint supplies native scrub combat equipment without an inventory cheat, and the tower can prove a new shield grant. This adds access prerequisites absent from the specification; it does not repeat or relabel a played result.

## #26: reproduction and cause

### Exact reported seed

Historical CLI with the issue's raw `CS1...` payload (strip the app's `Clawshot-0.2.0:` envelope for the CLI), seed 1057962893, and the supplied r14 native fixture:

- 250 shuffled locations, 17 spheres; generated output `work/r15-scrub/stranger-1057962893-v020`.
- `tree_digest`: **d92dd1d0cc9d74d632f14fa0b93ab1415109501016793f36a833901a981f840a**. Exact match to the reporter's short hash.
- Left/once-only family `LW Deku Scrub Grotto Front` actually has **Song of Storms**, fee 10. The report's observed bag wording is retained as an observation, not treated as proof of actual inventory grant.
- Right/repeat seller was given **no shuffled item at all**. Child Hash 2214083465643671502 retains `Shop_DekuSeedBundle_02`, `Shop_DekuSeedBundle_01`, `Obj_MagicJar_Small` (10 seeds/15 rupees, 30 seeds/30, small magic/10). Adult Hash 14619830301496284497 retains its arrow/magic alternatives. Both full placement actors equal vanilla.
- The reporter's attached runtime log confirms `Enemy_Scrub_Business_Common.bfevfl.zs` was loaded from their seed mod. It provides no event-level trace of the hang.

The 0.2.1 equivalent uses the same raw player settings with **current** defaults/logic, not a promise to import the old app share string. Output `stranger-1057962893-v021-before`: 255 shuffled, 23 spheres, digest `4fb000804ebb5c3d8e01044e086f77da9426f0891345ee9878a48c68efddbee4`. Left becomes Deku Nut Capacity; right actors, offer filters, initial menus and complete Leave/cleanup graph remain native and equal 0.2.0. Thus 0.2.1 retains the data-level problematic state; no new in-game reproduction is claimed.

`diagnose.py` independently checked both outputs against `E:/Games/Hookshot/romfs`; `probe.py` checked all 21 scrub actors and native forks/cleanup. Research/decoded data stays external.

### Native empty-offer state

`Enemy_Scrub_Business_Common:Unopened_Check` filters seeds on `IsGet.Weapon_Range_SlingShot` (Event180). Magic is filtered on native magic-source acquisition flags (Event435/179/84/95/128). A bag capacity does **not** supply the weapon. With neither Slingshot nor a magic source, all three child grotto offers are hidden. This is native behavior reachable in randomized inventory orders, not an empty randomizer placement.

The 12 repeat/rotating actors all use the common selection machinery (ledger `r6-tokens.md`, all Hashes reconfirmed from the real dump). The four saved once-only families use a different two-choice purchase path; they cannot have an empty actor because patch/fill validation requires an actual item. The fix must cover common menus independent of shuffle settings, item order, age and whether offers are hidden or actually blank; it must not make unavailable refills purchasable.

Initial diagnosis considered Event47's `IsCloseDialog=False`. **Rejected as a sufficient explanation:** Event47 is the *return-after-refusal* menu, not the initial menu on the second conversation. Both initial conversations reach Event44. The first candidate changed that Bool; its preliminary synthetic regression (1 failure, then scoped 45 passing tests) and v2 diagnostic mods are **superseded**, not final acceptance evidence. Do not ship a normal-menu lifecycle change on that inference.

Native Leave clears stock updates, message-log section, `UI_IsPlayingShopEvent` and recovery notice; Event587 forks rupee close and `EventCloseMessageDialog`, then joins to native goodbye/finish. **[INFERENCE]** the reported invisible dialog is the native lifecycle of the degenerate, all-offers-hidden menu. No event-level game trace establishes which engine wait stalls. The durable data-side repair is to avoid entering that menu: after native filtering, before shop UI opens, use the existing closed-dialog no-goods goodbye/finish path if no actual offer remains. Normal menus, purchases/refusals, rupees and saved flags must stay native.

### Offer wording is already known; not fixed here

- `03-game-data.md` section 34, line 2398: native flavour still names the vanilla item.
- `rounds/r6-tokens.md`, Purchase and patch contract, line 51: merchant flavour unchanged and may mention original reward.
- `rounds/r8-shops.md`, quote audit, line 90: original item-flavour unchanged; prices are dynamic.
- `docs/settings.md` lacked the user-facing warning; added it, without changing game text or expanding #26.

This was posted to `cs-r15` following Claude's request. No new text-patching feature is being slipped into this repair.

## Gates and coordination

Claude allowed the two single reproduction seeds without gate.lock. At their stage starts tasklist showed neither executable, so workers=3. Later staging found Longshot running and selected workers=1. Every subsequent stage selects workers dynamically from exact tasklist names. One initial staging attempt had set 3 before inspecting its displayed tasklist; it stopped at a printed native event-contract assertion before writing outputs, then the corrected runner chose 1 dynamically.

The superseded candidate's synthetic attempt was deliberately stopped after the corrected trace invalidated it; it is **not a pass**. Its runner released gate.lock and posted B next. Final corrected runtime/tests stayed frozen through both full gates: synthetic passed after B's release, then the ordered dump passed. Both runners released gate.lock; B dump is next.

## Final guard and verification

- Added six pure GameData queries after native filtering: for each of three slots, blank string OR native exclusion flag means unavailable. Only if all three are unavailable does the conversation take existing Event395 (closed no-goods message) -> Event140 (finish), before Event119 opens shop UI. Any visible slot follows the unchanged native UI/purchase path.
- Two incoming links change (`Event192`, `Event334`); no new saved flag, reward, price, availability bypass, or normal menu/close change. Every seed gets this, including defaults without Scrub shuffle.
- Failing-before synthetic scenario printed all three hidden flags followed by **Event119**, where **Event395** was expected. Final permanent coverage checks all 27 blank/hidden/visible combinations through both initializers (54 cases).
- Scoped synthetic `tests/test_scrubs.py tests/test_shop_settings.py`: **98 passed**. Initial iterator deprecation warning was corrected by making parameter cases a tuple.
- Real dump `pytest -m dump tests/test_scrubs_dump.py -k unshuffled -q`: **1 passed, 2 deselected**. Actual native graph reaches no-goods before UI for empty/hidden cases, native UI for visible offers; inverse restores the whole original graph.
- Actual CLI regeneration of the stranger's 0.2.1 equivalent: **exit 0**, 255 shuffled, 23 spheres. Spoiler is **identical** to before; emitted common flow has six guard nodes and is **identical after inverse guard removal**. Original menus, purchases/refusals and flags unchanged. Output `stranger-1057962893-v021-guard`.
- Actual default/no-Scrub CLI seed 26: **exit 0**, 165 shuffled, 26 spheres; emitted common flow independently read back with all six guards. Output `default26-guard`.
- Initial smoke readback used the layered dump container as a raw RomFS and printed the missing `Pack/ZsDic.pack.zs` path. CLI generation itself succeeded. Readback alone was corrected to use the real RomFS; no seed was regenerated to hide that failure.
- No fixture extension: this changes only a common flow already present in the supplied r14 working set.
- Final serialized gates: `uv run ruff format --check` **369 files already formatted**; `uv run ruff check` **All checks passed**; `uv run pytest` **2385 passed, 189 skipped in 687.57s**. Each stage saw neither game executable and selected workers=3; dump variables were unset for the synthetic run. Logs: `work/r15-scrub/gate-final-{format,lint,synthetic}.log`.
- Full serialized dump gate with the instructed real `OOT_ROMFS`, `OOT_NUP` and r14 `OOT_DUMP`: `uv run pytest -m dump` **186 passed, 2388 deselected in 6795.14s (1:53:15)**. Stage tasklist found neither game executable; workers=3. No fixture extension or skipped dump test. Runner exited 0, released gate.lock and posted B next. Complete log: `work/r15-scrub/gate-final-dump.log`.

## Final Longshot staging — v3 only


`work/r15-scrub/ingame/CHECKLIST.md` includes both empty-menu behavior and normal seed purchase, decline, native prices/ammo, repeat stock, re-entry, full Save-and-Continue, and once-only song persistence. Time estimate 17–26 minutes total. Claude boot-checks after the game is closed; Kareem plays. A staged progress.sav cannot safely be created without launching the game; isolated fresh empty profiles are supplied instead.

Use **only** `Test - scrub-dialog-control-v3-next.bat` and `Test - scrub-dialog-fixed-v3-next.bat` under `E:/OOTRemake/work/r15-scrub/ingame/`. Both were built through the common writer (nine resources), with independent chest/grant readback. Inverse comparison proves six guard nodes/two redirects are the only common-flow difference; every normal menu, including Event47's native Bool, is identical. Both dry-run batches exited 0 with installed Longshot rc.3, unique empty profiles, one mod each, unset overlay. No boot/play.

The fixed no-items conversation must now say the native no-goods goodbye and return control **without a shop or Leave menu**. Control retains the native empty menu to reproduce the reported failure. For the populated case, far-right Mido chest supplies Deku Shield, third from left 50 rupees, and far left (left closed until after empty-state checks) Slingshot. Once-only seller gives the reproduced Song of Storms for 10 rupees. Native repeat purchase/refusal/restock/reload checklist is in the external file. v1/v2 candidates are superseded and must not be handed to Kareem.

Claude's live report (2026-11-14): Kareem reached this grotto by **Noclip through the covering rock from the Lost Woods side**. Debug Teleport has only whole-map entrances, not a grotto/coordinate destination. Corrected the external checklist to use Lost Woods Teleport plus this explicit access-only Noclip exception, then turn Noclip off. No rebuild, inventory/flag/age cheats or no-glitches logic claim. Remaining control/repair/purchase/reload results are not inferred from this access report.

### Played acceptance — PASS (Kareem, Longshot rc.3, 2026-11-14; Claude's report)

- Both logs show this packet's `Event/EventFlow/Enemy_Scrub_Business_Common.bfevfl.zs` and KokiriForest Banc loaded from each corresponding mod.
- **Control:** first right-scrub conversation worked; second stuck. The reported second-talk failure is reproduced on Longshot, not merely assumed from Hookshot.
- **Fixed:** several conversations without Slingshot or magic never stuck.
- Left once-only scrub sold **Song of Storms for 10 rupees**, balance **50 -> 40**, then left; no second sale.
- After obtaining Slingshot, right seller offered 10/30 seeds. Purchase charged **15 rupees** and added **10 seeds**; final rupees/seeds **25/25**. These values survived **Save and Continue**.
- **Not exercised:** decline-then-Leave and full-capacity refusal. Do not label those played; native inverse-flow proof preserves them.
- Test saves retained under `work/save-backups/2026-11-14_14*-r15-scrub-{control,fixed}-*` as reported by Claude. No agent reread/replayed the reported result to confirm it.
- This establishes the named child grotto control/repair, one shuffled song sale and native refill/reload. It does not certify all vendor/item/age combinations. No game was started by this agent.

Claude accepted #26 played PASS and ordered final queued gates, then a `Fixes #26` commit and READY/head post before token Phase 1.

**Token staging path (resolved):** cs15d proposed independent `work/r15-token-impl/ingame`; Claude approved it in the current conversation and superseded section 6's path for this implementer. `work/r15-tokens` remains forbidden. No prohibited path was opened.

## Pending

All four final scrub gates and the named played acceptance passed. Next: scrub commit with `Fixes #26`, READY/head, then rebase onto main containing accepted `eff7dab` and implement **Phase 1 only** (delivery mechanism plus core diagnostic packet/save checker); section 9 was read first. Fill integration waits for Kareem's result. All new token game behavior remains **unplayed** by this agent.
