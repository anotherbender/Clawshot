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

Implementation475c91b3ab was committed before the full gate; final observed counts/head/timings/exits are recorded in `work/r18-equipment/gate-results.json`, `gate-{format,lint,synthetic,dump}.log` and the cs-r18 handoff. All four exits were zero: format/lint clean, synthetic3380 passed/440 skipped, dump437 passed. The November19 switch audit below adds documentation only; no implementation, test or staged packet changed and no gate was rerun.

`gate.py` rebases current main before acquiring r18 gate.lock, reruns focused checks on the rebased head, then serializes format, lint, synthetic and dump. Stage tasklist checks select synthetic -n12/workers12 and dump -n12/workers4 when closed, -n4/workers1 if either game runs. Exact commands: `uv run ruff format --check`; `uv run ruff check`; `uv run --with pytest-xdist pytest -n 12`; then `uv run --with pytest-xdist pytest -m dump -n 12`, with the round's exact RomFS/NUP/r16 OOT_DUMP. No suite deadline, no unchanged failure rerun, no foreign-lock removal.

Remaining acceptance: **Kareem's staged play**, including Mirror auto-equip observation/question. No game start, merge, push or version bump by this track.

## November19 urgent SwitchEvent audit — CORRECT

Claude's09:37 semantics alert: Boolean/equality/ownership **case0=true/held, case1=false/absent**. Re-read the live read-only RomFS, current implementation, r17 implementation at2ba2f9a, and the actual staged sword main/candidate and all six shield main/candidate outputs. CORRECT posted09:39; no replacement packet needed. This certifies branch polarity, not gameplay acceptance.

Native examples, all from `Event/EventFlow/<flow>.bfevfl.zs`:

- **B:** `Enemy_Scrub_Business_Common` Event554 asks `IsGet.Item_DekuStick`:0→Event319 existing-bag check;1→Event555 first-container grant.
- **S:** `ReplaceEquipmentForEraChange` Event14 compares the saved shield to Deku:0→Event12 Deku ownership check;1→Event17 Hylian comparison.
- **P:** same flow Event12 asks `EventQueryIsExistInPouch(Weapon_Shield_Deku,1)`:0→Event8 wait, preserving equipment;1→Event18 clears the candidate. This is independent native pouch evidence, not an assumed Boolean alias.
- **E:** scrub Event324/325/327 compare each offer to empty:0 advances to the next slot/return;1 enters CanBuy_Check.
- **H:** scrub Event180 asks Slingshot IsGet:0→Event185 sets the offer-hidden argument false;1→Event184 sets it true. Thus an `Unopened` flag's true value means hidden here, despite the misleading name.

Every added/retained guard, with native evidence for its query and interpretation:

| Switch | Case0: true | Case1: false | Native example |
|---|---|---|---|
| Sword DefaultOwned (Bool) | Event11 native Kokiri default | Event13 skip default | B |
| Sword Candidate (string equals Kokiri) | Sword Owned | Event13 preserve other weapon | S |
| Sword Owned (Bool) | Event13 preserve owned sword | Sword Clear | B |
| r17 Candidate, retained in main control (string equals Kokiri) | r17 Owned | Event0 preserve other weapon | S |
| r17 Owned, retained in main control (pouch) | Event0 preserve held sword | Sword Clear | P |
| Scrub OfferEmpty0 | OfferEmpty1 | OfferHidden0 | E |
| Scrub OfferHidden0 | OfferEmpty1 | Event119 native shop UI | B, H |
| Scrub OfferEmpty1 | OfferEmpty2 | OfferHidden1 | E |
| Scrub OfferHidden1 | OfferEmpty2 | Event119 native shop UI | B, H |
| Scrub OfferEmpty2 | Event395 native no-goods goodbye | OfferHidden2 | E |
| Scrub OfferHidden2 | Event395 native no-goods goodbye | Event119 native shop UI | B, H |

The sword's rewired **native** Event4 empty-string branch remains0→Event10 defaults,1→saved-candidate validation, matching native Event13's empty/default versus nonempty/validation split. Native Event10 IsChild remains0→Master default (outgoing child),1→Kokiri ownership guard (outgoing adult); the original native Event10 chooses those same era defaults. Every other native sword SwitchEvent is identical in the staged output.

The shield presentation patch adds/modifies **no SwitchEvent**. Actual candidate outputs preserve every native switch structurally. Native Dm_SY_GetInEvent Event514(Hylian), Event537(Mirror) and Event509(Deku) each have only case1: advance to the next check, next check, and wait respectively. True/case0 has no case and returns. Native Event635(Master)→Event630(Biggoron)→wait uses the same false-only polling shape. The patch changes two ActionEvent successors only, bypassing the equipment prerequisite.

Existing regression assertions already use correct polarity: `tests/test_child_sword.py::run` selects `0 if answer else 1`; the owned/unowned, saved/default, native and repeated-travel tests assert consumer-visible equipment/ownership under both write-visibility models. `tests/test_scrubs.py::guard_destination` uses the same polarity and tests all27 empty/hidden/visible offer combinations through both entrances. `tests/test_scrub_shields.py::run` maps equipped/held/equal to0, otherwise1, with missing cases returning; native-dump tests exercise the actual helper and its two-edge-only delta. No interpreter repair was needed.

Urgent read-only assertions independently checked the actual staged three sword and six-per-flow scrub guard case tables, the r17 main-control tables, every otherwise unchanged native equipment switch and every native shield-presentation switch. All passed. The initial native printer encountered ReturnEvent without params; after printing that exception, only its formatting was corrected to use getattr. No source, save, launcher, mod or test changed; no game was started, no gate rerun.

## Issue34 implementation — r18/ocarina

Claude decision, 2026-11-19: target0.2.3; branch from main `d3ce136`. **Non-demoting Fairy receipt, not progressive.** Every native Fairy add still runs: preserve stock, IsGet, get flags, cleanup and once writes. If Time is already in the pouch, keep `PlayerStatus.EquipOcarina` on Time. Fairy→Time stays native. This supersedes the read-only report's proposed lower-add suppression; that proposal would not satisfy the accepted stock/IsGet contract.

The private issue/log remain external. Complete diagnosis: `work/r18-issue34/findings.md`; no stranger paths or usernames copied. Child Time→Fairy selection is the issue's report. Adult exact-order behavior is still a native-code inference, pending the requested main control; Kareem's earlier adult-Fairy Minuet freeze is separate ground truth.

### Native refresh proof

Native Ocarina grant dispatch `0x011116d4..0x01111704` invokes the equipment setter even with direct equip disabled. Setter `0x00a7b084..0x00a7b12c` writes incoming canonical actor to PlayerStatus member `0x527936b8`, the saved String64 `PlayerStatus.EquipOcarina` (`0xb72cd3fc`). Reader `0x00a76650` reads that selector and its OcarinaTypeValue, Fairy1/Time2.

The live refresh gap is now closed by additional disassembly, not by the sync action's name:

- `UISystemActor.EventTriggerSyncPlayerEquipmentAndPouch` execute `0x02951f50` calls `0x00f201b0` with flag0.
- `0x00f201b0` reapplies equipment slots13 (`0x00f2025c`) and16 (`0x00f202b0`) among the native slots.
- Inside `0x02df6c80`, `0x02df71c8..0x02df71f4` maps **both13/16 explicitly to EquipOcarina**. Therefore this sync includes the instrument, not just wearable armour.
- The helper commits the selector with the already-preloaded `GameSystemActor.EventWait` frame1 **before** sync reads it. Native precedent: GetPouchContent Event61's frame1 before autosave. No new actor, saved flag or scratch field.

This establishes the native mechanism; the staged pickup, held-model and adult-song result remains required.

### Implementation and route coverage

`patch/ocarina.py` composes last, after source gifts, named/progressive chest helpers and bag guards. It never changes a grant's actor, quantity, direct-equip/get/message flags or incoming edges. It inserts only a receipt continuation, then resumes that action's original next node. A shared `GetPouchContent:ClawshotOcarinaKeepTime` checks current Time pouch ownership, sets the selector to Time, waits one native frame and calls native equipment sync.

Argument-driven adds classify the genuine just-received actor through the existing `UI_MessageTargetActorName` identity; their native IsSetMessageTargetActorName=true is validated. Literal Fairy adds need no scratch query. Saria's movie has no GameDataActor: it calls the shared helper rather than adding an actor to the movie.

- GetPouchContent Event0 covers small/big chests and ordinary admitted direct/song/cutscene wrappers.
- Dm_SY_GetInEvent's three positive argument-driven adds retain their own original continuations; unsafe ocarina hand-over exclusions remain in force.
- Native Saria Dm_Kokiri_0155/Event68 is covered when still Fairy, even unshuffled.
- Dm_MelodyGet_Time/Event70 and every earlier-transformed event file are inspected after gift rewrites, so Fairy moved into a direct Time/other admitted source is covered too.
- Non-Fairy rewards, zero/removals and first Fairy without Time keep native inventory/equipment behavior. A historical Time IsGet without stock cannot fabricate ownership. Native Dream's NecessaryActor refund is not an admitted Fairy source; its message-identity-false path is not guessed from a stale UI field.
- Source flag/cleanup continuation runs only after restoration; native autosave therefore observes the corrected selector.

### Switch semantics and logic

| Added switch | Case0 true/held | Case1 false/absent | Native example |
|---|---|---|---|
| IsFairy, on an argument-driven receipt | Shared post-Fairy helper | Original continuation | ReplaceEquipment Event14 string equality0→matching Deku ownership check,1→next comparison |
| KeepTimeOwned, Time pouch query | Set Time→frame1→sync | Return to original continuation | ReplaceEquipment Event12 pouch0→preserve/wait,1→clear |

Regression interpreters explicitly use0-if-true, and compare actual native grant side effects/parameters with the candidate while checking live selection after sync. They cover both immediate and frame-buffered explicit GameData writes.

**No placement change; no sweep.** The new transform is appended after `generate` and plan selection. It changes neither pool/admission, alias/counters, logic, RNG nor item identity. Ocarinas stay fixed Fairy/Time, the current MAX Ocarina tier and adult tier2 rule stay; this repair restores their assumed monotonicity. It is not a new start item, progressive chain, adult-Fairy permission, scene bypass or old-save repair. Public output changes and thus belongs to the maintainer's0.2.3 version bump.

### Verification and packet receipts

Focused request completed, real `OOT_ROMFS`, workers1, no lock: **363 passed in254.20s** across `test_ocarina*`, `test_child_sword`, `test_scrub_shields`, `test_scrubs*`, `test_bags`, `test_getitem*`, `test_gifts*` and `test_census_gifts`. Scoped Ruff format completed (3 formatted,1 unchanged); scoped lint passed. No failed/repeated test run. Implementation/source snapshot: **51828ebccf**.

Packet: **`E:/OOTRemake/work/r18-issue34/ingame/CHECKLIST.md`**. Three launchers only: adult MAIN CONTROL, adult candidate, child candidate. Main source is an archived `d3ce136`; candidate source is archived `51828ebccf`. Forced Fairy chest is Zora's River's open-grotto small chest, Hash8838426083116998768. Both age placement bytes are identical between main/candidate. Main also identity-re-serves native GetPouchContent for its load proof; candidate adds the guarded GetPouchContent, GetInEvent and Saria flows plus size table (3 versus6 resources).

No save edits. Both fixtures are isolated copies of the natural Nov9 main Temple of Time backup: adult beside Sheik/pedestal and child in the Temple. Both initially select Time, have both instruments IsGet/stock1 each, four learned songs including Sun, and the grotto chest unopened. Therefore this is a **repeated Fairy receipt**. No natural adult Fairy-active-after-Time fixture was found; main produces that state through the actual same-chest pickup. The control must reproduce active Fairy before drawing any cosmetic/fixed conclusion. Candidate adult then plays Sun outdoors, saves/continues and checks again; candidate child checks held Time. Teleport/clock only, no inventory reselect/cheats, no warp song.

Honest estimate **10–12 minutes**, unmeasured, target10 and hard stop12. Plain landmarks and source pictures, not slot-number directions, are in the checklist. A failed or incomplete case stays unverified. Claude boot-checks, Kareem plays.

`packet/packet-proof.json`: all three actual cmd dry runs exit0 on installed rc.7, one mod each, overlay unset; native data/output round-trips, source/progress copies hash-identical, old equipment packet118 files unchanged. Parent additionally executed the **actually written** main/candidate GetPouchContent flows in the regression model: main selects Fairy, candidate selector/live model selects Time, with native-identical inventory/IsGet and receipt parameter traces. This is a model, not gameplay or a measurement of native stock caps.

`packet/report_state.py` reads only the three isolated test profiles after play, reporting the five saved instrument fields, chest completion and runtime mod-load lines. No game started here. **No lock or full gate taken; F+G first.** The staged packet and code are built/play-held, not merged or release-certified.

### Check13 acceptance and combined integration

Claude reported Kareem's **check13 PLAYED PASS**: main adult held Fairy, saved selector Fairy, and Sun's Song **played**. Candidate adult held Time, Sun played, and Time persisted through Save/Continue (saved Time); candidate child held Time. The main downgrade is cosmetic **at least for Sun's Song**. This does not certify every adult song or explain the earlier Minuet freeze. No logic/age-permission change is inferred. Claude also accepted check14.

B rebased cleanly onto main2d9ddef as9a88aebd7e72a7332c48842e73fdc30661a55f6f. A stacked/froze3457bf05985976d3af88210450d7ef4763a29bea, with413 focused passes and additive patch composition. B adopted that exact head and acquired/retained its own round18 gate.lock.

First combined full gate on3457bf: format/lint passed; synthetic **8 failed,3783 passed,499 skipped,15 setup errors,36 warnings** (558.28s); dump never started. Original logs: `work/r18-issue34/combined-gate-3457bf059859/`. No unchanged rerun. Two failures print missing synthetic RSTB via `make_seed→mido_schedule.build`: the public named-key/first-bag fixture predates required kept-Mido resources. B extended that fixture with the existing synthetic Mido GameData/schedule builders and an actual synthetic size table; settings and original inventory/credit assertions remain unchanged.

The other six failures and15 setup errors print existing20-second app-spawn waits or10-second Node deadlines. Post-gate diagnostics showed16 logical CPUs,100% CPU, about32GiB free RAM, Defender at188% process CPU plus multiple omp processes. These snapshots do not prove load at each failure: contention is an inference. B proposed isolated cause-directed verification followed by bounded4×4 full-gate fanout instead of12×12 nested fanout; **no timeout increase, test exclusion or production change**.

Cause-directed follow-through: all21 formerly failing/erroring app/Node cases passed with isolated scheduling and unchanged deadlines (the23-case diagnostic took29.74s, with the remaining2 key cases printing further absent native flow inputs). Complete dependency printing exposed unrelated native quest scenes that were never in this invented world's written-resource set. The fixture now supplies synthetic ocarina charts/UI actor and scopes the **real** receipt compiler's prior inputs to exactly the resources the existing writer loop applies; real key, bag, Mido and ocarina compilers all remain active. Both chest-size public grant cases then passed in2.20s; scoped Ruff passed. No production-code or placement change.

B's corrected freeze includes only `tests/test_key_bindings.py` and this receipt after3457bf. The corrected combined gate will cover **every** synthetic and dump test at `-n4/CLAWSHOT_WORKERS=4`, with full RomFS, NUP and a private layered fixture for the dump stage. No timeout increases, exclusions, sweep or further edits after freeze. The failed first receipt is retained, not reclassified as a pass; the final exact head and gate results will be posted externally so the verified head does not move afterward.
