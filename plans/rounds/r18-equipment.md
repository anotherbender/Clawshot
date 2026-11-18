# Round 18 Track B: equipment and get-item paths

Agent cs18b (`openai-codex/gpt-6.1-sol`), branch `r18/equipment`; initial main `2ba2f9a`.
Built and staged, **not played**. Exact-head full-gate acceptance is recorded in the external ledger/thread below. Adult pedestal Master Sword is native and out of scope.

## Ground truth and safety

- Kareem returned through the pedestal without finding the Kokiri Sword; the round-17 patched equipment flow loaded, yet child Link held it with ownership false. The supplied report is the repro, not a reason to rerun the failed check.
- Issue #33's reporter explicitly says the Mirror Shield purchase was **ADULT**, in the issue's final comment. The intake's child hypothesis is superseded. An age-only scrub restriction would not fix this reported failure.
- Read-only source: supported native dump `e0f3ccfa`; copied saves under `work/r18-equipment/kareem-seed-saves`, and the historical save-backup library authorized by Claude for natural fixture selection. No played seed or live save opened; no game started. Reporter log paths/user name are never quoted or committed.
- Research scripts, decoded data, regenerated outputs and staged users live outside the repository at `E:/OOTRemake/work/r18-equipment/`.

## Printed evidence before any fix

### Shared shield hand-over

Native `Dm_SY_GetInEvent:DekuShield_GetAndEquipCheck` begins at Event444, dispatches Shield category3 to Event442 (pouch add, `IsEquipDIrect=false`), then waits for an equipped shield. The three queried identities are:

| Node | `ArmorName` | False continuation |
|---|---|---|
| Event514 | `Weapon_Shield_Hylian` | Event537 |
| Event537 | **`Item_Shield_Mirror`** | Event509 |
| Event509 | `Weapon_Shield_Deku` | Event513, one-frame wait back to Event509 |

The actual Mirror equipment identity in native PouchActorInfo is `Weapon_Shield_Mirror` for both age equipment references; the UI marks it adult-usable, child-unusable. The grant actor `Item_Shield_Mirror` is not the equipped identity. **[INFERENCE]** this mismatched predicate and mandatory equipment wait explain an adult Mirror purchase remaining in the pose. The final Deku-only polling loop also makes changing the Mirror spelling alone insufficient for asynchronous or wrong-age equipment.

Claude's reporter-state correction: the boot inventory probe has Deku Shield1, Hylian0, Mirror0; the reporter confirms adult. **[INFERENCE]** he owned no adult-usable shield. The read-only backup scan found a natural matching fixture: `2026-11-09_1022-main-adult-first/save/<save-id>/slot_01`, SHA256 `e63eba9d8173c7c03e1e5338c48ec2dc90cbd2f9b2cad1e487022d5cb46c761c`: adult, equipped shield empty, other-era shield Deku, Deku stock1, Hylian/Mirror stock0, all four scrub once flags false. No staged shield-clear fallback is needed.

**Kareem: should a received Mirror Shield auto-equip, or only land in inventory?** Native Event442 and the ordinary GetPouchContent grant both request `IsEquipDIrect=false`, yet this helper waits for some recognized equipped shield. The fix preserves those grant flags and requests **no forced auto-equip**: it returns after the existing one-frame yield even if receipt only changes inventory. Native incidental auto-selection is not disabled. The played check must record what actually equips; no new auto-equip policy is silently chosen.

### Age metadata inventory

`age_audit.py` reads the live UI PouchTable, PouchActorInfo and inherited actor roots; complete external evidence is `age-audit-native.json`. Printed rows exposed Work/Actor equipment references rather than short names; adding those, canonical ActorNameRef and bundle identities completed the census at **40 mappings**, including shop refills and vanilla-held trade/card items. This does not admit held items. Canonical references name Kokiri→Weapon_Sword_Kokiri, Bow/Slingshot→their Weapon_Range identities and boots/tunics→Armor identities independently of age-use metadata. Resident reference members need not be packed locally.

Child-only UI identities: Kokiri Sword, Deku Shield, Slingshot, Boomerang, Fairy Ocarina, sticks/beans and the child trade cell. Adult-only: Bow/arrows, Hammer, Hookshot/Longshot, Biggoron Sword, Mirror Shield, tunics, Iron/Hover Boots, gauntlets and adult trade/card UI entries. A UI use restriction alone is not evidence that acquisition hangs.

## Delivery-path audit

Existing evidence is separated from native-data inference and unplayed combinations:

| Path | Actual delivery and existing evidence | Cross-age boundary |
|---|---|---|
| Scrub | Successful common-flow purchase calls `GetInEvent_NotTurn_2DShop`; cancellation/shortfall precede it; completion follows return | Adult Mirror hang reported #33; native helper also cannot finish wrong-age Mirror/Deku without recognized equipment. Fixed by removing that prerequisite, not by adult-only placement. Native-data-tested; runtime acceptance held. |
| Shop | Native display allowlist and DisplayShop buy/refusal flow; source `03-game-data` section24 | Adult tunics retain native child refusal and adult-accessible placement; Mirror/swords/boots have no admitted shop display. Live `DisplayShop:Root_Buy` traversal has no shield helper or equipment-query wait. Child-only Deku Shield can be owned by adult without adult use. |
| Chest | Native small/big treasure-box events, grant through GetPouchContent; progressive copies chest-only | Child Bow followed by Boomerang use passed after empty Nut Bag new-game initialization (2026-11-12). Old saves can jam the item bar; Save and Continue workaround. Not every equipment/age pair played. |
| Gift | Live census/patch traversal: **56 admitted checks, 41 show-item, 15 direct/GetPouch-only** | **Zero** admitted gift paths reach `DekuShield_GetAndEquipCheck`. This rules out that specific scrub wait, not every show-item risk. Ocarinas remain excluded from show-item hand-overs after reproduced gallery crash; direct story/chest paths remain allowed. |
| Token | Generated native own-item pickup preserves completion callback; each member structurally checked, family admission by played representative | Child Boomerang/Hylian and adult Ice Arrows passed on rc.3. Family admission is not an exhaustive opposite-age equipment proof. Fairy Ocarina excluded; Time uses native world donor. |
| Freestanding | Fourteen anchored floor hearts; five native pickups only | Palette: hearts, red rupee, Deku/Hylian Shield. Adult-only majors cannot reach this path. Ranch Hylian pickup played; other members/ages are not all played. |
| Boss heart | Same five-pickup palette, native floor pickup | Adult-only majors cannot reach it; King Dodongo Hylian Shield played. Do not infer all native floor get combinations from that representative. |

References: `rounds/r11-ocarina.md` (ocarina lifecycle/native null ShowItem correlation and gift wrapper census), `rounds/r13-item-grants.md` (first-bag/new-game repair), `rounds/r15-scrub-tokens.md` and `data/token_rewards.toml` (played family admission), `03-game-data` sections23–24,33,36–37. Further audit/fix/staging/gate results will be appended here.

`delivery_audit.py` traverses actual current native flow entry points and patched gift wrappers, not the older round11 location count. Both chest flows avoid the scrub shield helper. Small-chest traversal's equipment query belongs only to `NaviHint_Shield_Hylian_FlagCheck`, whose true **and** false branches exist; it is not the one-arm equipment polling loop. Native `Dm_SY_Get` pickup entries contain no equipment query or scrub shield helper. External complete evidence: `delivery-audit-native.json`.

The same audit separates the Ocarina failure: its native Common/Accessory presentation differs from ordinary PouchContent performers, and round11 correlated the crash with a null ShowItem actor getter. No evidence makes that crash an age-only problem or the same shield-polling defect. Existing hard exclusions remain necessary.

### Both-direction item coverage

| Class | Adult-only→child / child-only→adult evidence and policy |
|---|---|
| Mirror / Deku Shield | Scrub polling is a definite structural deadlock; the actual report is adult Mirror. Both opposite-age directions are staged. Chest/gift/shop/pickup graphs avoid this helper. Wrong-age ownership must persist without wrong-age use. |
| Kokiri / Biggoron Sword, Iron/Hover Boots | Canonical identity and ordinary grants preserved; non-Shield categories avoid the scrub wait. The separate Kokiri-return defect is fixed below. Opposite-age acquisition is structurally supported, not individually played on every path. |
| Goron/Zora Tunic | Native shop destination/refusal policy retained; the separately admitted Skulltula variant uses a world donor/canonical armor identity. No child shop purchase bypass. |
| Bow/Slingshot, Hookshot/Longshot, gauntlets | Progressive copies remain chest-only; fixed native bonuses retain existing paths. Child Bow→working Boomerang passed after new-game Nut Bag initialization. Adult-first Slingshot and every other reverse pair are not separately played. |
| Boomerang/Hammer, sticks/arrows/refills | No scrub shield wait. Old-save item-bar misuse is distinct; first-container screens and empty-nut initialization stay. No automatic first-refill container inference. |
| Ocarinas | Both forbidden at show-item hand-overs before fill; Fairy also forbidden at Skulltulas. Time's native world donor has played evidence. Fairy's adult-use restriction is separate from its unsafe presentation lifecycle. |
| Trade cell, captain's card, beans/masks | Existing vanilla/out-of-pool holds remain. Metadata is not admission; shared trade-cell display trouble stays avoided by policy. |

Absence of the scrub helper proves absence of **this** deadlock, not universal runtime certification. No further unsafe age-specific grant was established, so no blanket matching-age restriction is invented. Existing ocarina, display, container, progressive and floor restrictions remain mandatory; `docs/settings.md` distinguishes them and the unplayed limits.

## Sword return: failed timing and replacement guard

`save_probe.py` printed the six copied progress slots in mtime order. All are already child: Kokiri equipped, IsGet false/stock0, other-era Master. There is no earlier adult sample in that copy. The real return still calls ReplaceEquipment before changing age.

**[INFERENCE: frame-buffered GameData visibility]** Native Event0/Event1 and Event2/Event3 preserve their intended equipment swaps only if reads see pre-write values until a yield. A native census found waits separating62/64 same-name write/read pairs; the exceptions are those swaps. The old clear ran **after Event8's wait**: Event0 could copy stale Kokiri, then Event7 overwrite the pending clear with Master, reproducing the supplied saves. No native commit implementation/watchpoint was proved. The new guard is tested under both immediate and frame-buffered visibility.

`patch/equipment.py` now reads explicit saved `IsGet.Weapon_Sword_Kokiri`, not an ambiguous pouch-presence answer. An empty candidate receives the native Kokiri default only when owned; a saved unowned Kokiri candidate is cleared. All guard writes precede the original Event8 wait. Native wait, shields, swaps, adult Master fallback, quests and era writes stay; no ownership, fallback weapon or extra frame.

Natural first-return fixture: `2026-11-17_182507-r16-time-walk-songonly-v5-12/<save-id>/slot_00`: adult Temple, Master owned/equipped, Kokiri IsGet false/stock0, other-era sword empty, sword chest closed, first return not done. Forest incomplete: both control and candidate use the same existing free-time-travel patch. No save/history edit.

## Issue33 exact reconstruction and correction

Detached checkout `work/r18-equipment/v021-src`, tag `v0.2.1` (`5e16847`). The whole1090-character issue string is intact and round-trips exactly. `regen_issue33_v021.sh` ran with workers2 under Claude's explicit one-seed lock exemption.

**Seed866244357, hash DF4F40D3DA55 exactly;311 checks,17 spheres,165 resources.** Bridge scrub holds Mirror Shield; Event317/322/555 all grant Item_Shield_Mirror for40; Event4 calls GetInEvent_NotTurn_2DShop. Output stays external at `issue33-v021-seed866244357/`.

Executing that actual helper in a flow interpreter: Mirror already equipped, no equipment, late Mirror and late Hylian all poll beyond600 frames. Existing Hylian/Deku return; late Deku can return. This matches the reported adult/Deku-only ownership but is **not a game replay**.

`patch/scrub_shields.py` changes two edges: Event442→Event513 (native non-direct-equipping add→native one-frame yield), Event513→return. No arbitrary timeout/retry chain, extra action, forced equipment, removal or compensation. `scrubs.changes` includes it only for a native Shield-category once-sale reward. Real-dump callers are ordinary/Dream scrub flows; emission is for ordinary shuffled sales. Gifts/shops/chests do not newly use it.

No fill, location, destination, logic, pool, RNG or offered setting changes. **No placement sweep required for this patch-only track.** The old seed reconstruction is not migration of a played output.

## Combined staged packet

Root `E:/OOTRemake/work/r18-equipment/ingame/`; exact instructions/stop conditions `CHECKLIST.md`.

- `Test - sword {main,candidate}.bat`; `Test - {mirror,deku,hylian} {child,adult} {main,candidate}.bat`:14 isolated launchers.
- Main controls from2ba2f9a, same forced sale/price/fixture as candidates, not vanilla launchers. Candidate manifests record actual source hashes; staged before import-order cleanup, which changes no generated bytes. No mod/profile is replaced during rebase/gating.
- Unedited natural adult Deku-only and child no-shield copies; no shield-clear fallback or cheats. Forced sale0 rupees; offer text still describes capacity. Each launcher has one independent single-slot profile.
- All14 dry-ran to installed **Longshot rc.7**, one mod, overlay unset; source/copy progress hashes match. No game start. Main/candidate purchase flows byte-identical; actual candidate presentation differs only at the two intended edges. Actually written sword flows reproduce control/candidate divergence under the stated buffered interpreter.
- **40–65 minutes complete**, not timed; **12–20 minutes** primary sword+adult-Mirror subset only. Child/reverse-age/Hylian controls are additional. Require real load proof, pickup result, decline, re-entry, reload, ownership/completion and usable inventory. Claude boot-checks; Kareem plays.
- External proof: `packet-proof.json`, `shields-{main,candidate}-manifest.json`, `sword-{main,candidate}-manifest.json`.

## Verification and diagnoses

- Focused real-dump run: `OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest tests/test_child_sword.py tests/test_scrub_shields.py tests/test_scrubs.py tests/test_scrubs_dump.py -q -x`: **205 passed in98.49s**. Covers both visibility models, ownership versus equipment, repeated return, every shield equipment outcome, native caller scope and bag-transform composition.
- Focused format:6 files formatted. Lint printed import ordering and nested-if simplification; both corrected from those diagnostics before gate.
- Initial reproduction shell was Windows system32 bash (WSL), unable to see E: paths. Printed executable/cwd/failure; explicit Git Bash then reconstructed the exact hash.
- First launcher dry-run exposed the older template's missing channel subdirectory search. Corrected only control launchers from the current template; all14 dry runs/output proofs then passed. No mod/save rebuilt for this.
- Both affected flows already exist in the r16 working-set dump's base/romfs; **no fixture extension**.

### Exact-head full gate

This file is committed before the full gate so the tested head stays the head offered for merge. Final observed counts/head/timings/exits are recorded without further tracked edits in `work/r18-equipment/gate-results.json`, `gate-{format,lint,synthetic,dump}.log` and the cs-r18 handoff. **No READY until all four exits zero.**

`gate.py` rebases current main before acquiring r18 gate.lock, reruns focused checks on the rebased head, then serializes format, lint, synthetic and dump. Stage tasklist checks select synthetic -n12/workers12 and dump -n12/workers4 when closed, -n4/workers1 if either game runs. Exact commands: `uv run ruff format --check`; `uv run ruff check`; `uv run --with pytest-xdist pytest -n 12`; then `uv run --with pytest-xdist pytest -m dump -n 12`, with the round's exact RomFS/NUP/r16 OOT_DUMP. No suite deadline, no unchanged failure rerun, no foreign-lock removal.

Remaining acceptance: **Kareem's staged play**, including Mirror auto-equip observation/question. No game start, merge, push or version bump by this track.
