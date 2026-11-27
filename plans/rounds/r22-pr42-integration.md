# Round22 PR42 integration — cs22c

Authorized by Claude: line21, relay `claude-21-after-029`, after release0.2.9 and explicit line20 LOCK RELEASED. Branch `r22/pr42-integration`, worktree `E:/OOTRemake/clawshot-r22/pr42-integration`. Contributor head `ceab0744c00a325c80de46a7c6df6f2f24388778`; main `5dcb21b5e29b78e96e8c254d0106647267ad4d87` (tag `v0.2.9`). Main is merged INTO the contributor branch; none of Bender's commits is rebased or rewritten.

Latest played disposition: **child2c Time PASS; both adult Fairy keep-Time rows FAIL on ca62**. The preparation/full-gate/sweep results below do not supersede those played failures. Claude subsequently approved the scoped generated-Fairy Large normalization and line26 retests; that candidate is not a played fix. See the final section and `work/r22-pr42/PLAY.md`.

## Integration choices

Proposed by cs22c under Claude's explicit “keep lifts' safety checks” requirement:

- Keep one settings-selected `getitem.ocarina_get_model_possible` rule. Gift or an expanded Gift kind always supplies the required model, independent of actual placements.
- Keep main's all-shuffled-ocarina coverage refusal, audited Gift receipt refusal and missing-model-input refusal. No native-pack fallback. Main's Gift-only synthetic writer, same-settings direct-pouch output and real native handover regressions remain.
- Keep PR42's generated song/ocarina producers before Token donor composition, its pickup receipt before `ocarina.changes`, and its ordered optional `ocarina_pickups` step. Chest+Gift without a floor/Token kind still writes no song floor actors.
- Keep the eight chest receipts explicitly Chest-scoped, capacities' Chest/Scrub/Token policy and the tunic native-shop/gift-actor exception.
- Remove the superseded PR42 placement-selected `shown_ocarinas_possible`/`get_model_ocarinas`/`chest_ocarinas` helpers, their otherwise unused `Location.hand_over` field/parser path and their obsolete marker/helper tests. The maintained consumer-level native output/safety tests cover the settings-selected contract instead; no old behavior is re-pinned.
- Merge existing tests by behavior: retain song-slot exclusivity, reachable-before-locked-chest proof, scrub fill proof and main's complete writer coverage. Optional-step expectations include generated pickup production for Token-capable Gift recipes.
- Preserve the historical contributor record, with an explicit pointer superseding its pending labels and old helper design. Correct the Token catalogue's immediate-Time-model overclaim rather than silently presenting TB4 as a pass.

Python language-server navigation was attempted before exported helper removal. No Python server is available (`pyright-langserver`, basedpyright, pylsp, ty and ruff missing on PATH); exact caller searches supplied the fallback. No runtime source was researched.

Claude requested an explicit contributor-facing preservation table before final resolution:
`E:/OOTRemake/work/r22-pr42/INTEGRATION.md`. It maps every removed PR test and metadata field to
retained main coverage or explains why a superseded metadata/model-selection assertion no longer
applies. Bender's Gift-only direct-story fill regression is retained/adapted explicitly: the other
source excludes the instrument so the original direct-source assertion is meaningful, not an
incidental seeded placement. No still-existing uncovered behavior is intentionally dropped.


## Acceptance and remaining play

Kareem via Claude accepted the ten unplayed songs **by analogy**, not as ten individual play results. TB4's stale live Fairy model/sound after a Time Skulltula pickup is accepted as cosmetic: both instruments function identically, and Save/Continue refreshes presentation. Source history, saved ownership and selected instrument are not relabelled as a live-model switch pass.

Exactly five new isolated rows are required from `E:/OOTRemake/work/r22-pr42/PLAY.md`:

1.924201: Time from Gohma's boss-heart pickup, immediate manual use, source persistence.
2.924202: Fairy from Impa's cow-shed roof Heart Piece, no previous instrument, normal retrieval and immediate use.
3.924203: Time from the Hyrule Field password GrottoScrub, real advertised fee/password and native once-sale state.
4.924204: Prelude from Gohma's boss-heart pickup, recognized warp to Temple of Time before Continue, then after reload.
5.924205: three Deku Tree Skulltulas, Heart Container/Milk Bottle/red rupee; idle spin, remote/normal retrieval and real life/bottle/rupee/token/source-pair accounting.

No player run or full integration gate is claimed by this initial record. The private builder/checker and all decoded/game/save material remain outside the repository under `work/r22-pr42/integration`. The packet must use production admission and beatability, untouched original saves, independently frozen copied baselines, documented copied-save edits and the current pinned Longshot3.2.0 launcher template. Each seed gets exactly one `bootcheck_when_idle.sh` invocation; boot is not a played pickup result.

## Gate and version boundary

The line21 lock was acquired atomically with owner/relay metadata before merging. Full gate: format, lint, whole synthetic with OOT variables unset, then whole dump with supported read-only RomFS/NUP and **`OOT_DUMP=E:/OOTRemake/work/rounds/r22/layered-dump`**. Player processes must be closed for seed-capable work; no fixture or original dump is modified. Failed values are printed before a cause-directed correction; no unchanged rerun or weakened oracle.

Claude explicitly decided **no version bump** for this private integration: retain0.2.9 and pin the full integration SHA in every packet. Versions move only at a release. This is not a new public release, version-compatibility promise or repair of existing seed folders/saves.

The commit namespace refuses pending merge operations, as it did for the lifts integration. Claude is asked to finalize the resolved pending merge rather than bypass the selective-commit requirement. Gates bind the resulting immutable integration commit. Ordinary subsequent authored commits use the selective commit namespace and `Assisted-by: openai-codex/gpt-6.1-sol`.

No GitHub post or push is authorized. The PR42 review comment remains **HELD**. Final READY FOR PLAY requires successful full gate, all five actual builds/manifests/baselines/launchers, five idle boot checks, then owned-lock release and thread handoff; it is not merge/play acceptance.

## Approved camera-obstructed ocarina receipt fix — 2026-11-26

Claude approved cs22c's copied-save diagnosis and `work/r22-pr42/integration/diagnosis/rows1-2b-played-20261126-125049/fix-proposal.md` as written. This is a new scoped commit on `r22/pr42-integration`, not a rebase or rewrite of `700fc8e` or Bender's commits. Claude explicitly requested the trailer `Assisted-by: Claude Opus 5.5` for this commit. Keep version0.2.9; existing frozen mods and played profiles remain untouched.

- The existing world-own-add receipt now covers both `Dm_SY_Get` and the native camera-space fallback `Dm_SY_Get_WithoutPlayer`, before the shared keep-Time transform. Each file's transform validates its own original flow independently.
- The native no-player flow has no `GameDataActor`; the receipt registers that required identity-query actor when absent. The existing actor/scoping checks otherwise remain strict. No get-model setting, presentation, PouchGetType, physics, admission, inventory grant or source-cleanup policy is changed.
- Behavioral synthetic tests execute the production receipt-plus-keep-Time composition after EVFL serialization/readback. Both paths cover Fairy0 and duplicate Fairy1 after Time1, saved/live selection and autosave, immediate/buffered writes, absent Time despite historical ownership, first Time usability, native reward/history/continuation preservation and changed-source refusal.

### Contributor test-preservation mapping

| Original test | Original assertion | Maintained coverage |
|---|---|---|
| `test_an_ocarina_pickup_is_added_again_by_name_after_its_own_add` | Normal receipt's named add and parameters | `test_first_time_receipt_is_usable_before_autosave`, `test_fairy_after_time_keeps_saved_and_live_time_through_cleanup_and_autosave` and `test_fairy_without_time_stock_never_grants_or_selects_time` execute both receipt paths and assert actual reward/history, live selection and saved selection. Parameter/wiring pinning is replaced by consumer behavior. |
| `test_other_pickups_run_as_before` | Non-ocarina action trace unchanged | `test_other_receipts_preserve_native_rewards_presentation_and_selection` compares complete native/transformed state, presentation, source cleanup and autosave on both paths. |
| `test_the_fairy_add_gets_the_keep_time_helper_and_the_flow_reads_back` | Fairy add is found by `_targets`; EVFL roundtrip | Behavioral Fairy-after-Time tests execute the composed helper on both paths; the fixture retains EVFL write/read equality for the resulting flows. No wiring-only replacement. |
| `test_a_flow_without_one_own_add_or_already_patched_is_refused` | Missing own-add and double patch refuse | Retained, parameterized over both presentation paths. |
| `test_receipt_changes_patch_the_dump_flow` | One-file output, named add and changed-source refusal | Production-composition fixture exercises both transforms in every behavioral case; `test_each_receipt_transform_refuses_a_changed_source` retains refusal for each file. Obsolete one-file output assertion removed. |

### Focused verification only

The first focused run printed the missing-unscoped-`GameDataActor` failure. The native no-player actor table confirmed the cause; registering the required actor and retaining the native pouch actor in the synthetic fixture addressed it. One cause-directed rerun: **54 passed in1.44s**.

Exact pytest arguments: `pytest.main(["-n", "2", "-q", "tests/test_t1a_receipt.py", "tests/test_ocarina.py"])`, launched through `uv run --frozen --with pytest-xdist python` with `CLAWSHOT_WORKERS=1`, `OOT_*` unset and Windows below-normal priority. The launcher used `BELOW_NORMAL_PRIORITY_CLASS`; pytest independently set and printed `PYTEST_PRIORITY_CLASS=0x4000` before creating its two workers. Outputs remain outside the repository: `work/r22-pr42/integration/receipt-fallback-focused-first-failure.log` and `receipt-fallback-focused-corrected.log`.

Per Claude while Kareem's game runs: no formatter/lint/full synthetic/dump gate, seed generation or boots were run. **Built and focused-tested, not played in game.** The new Fairy-after-Time normal/no-player play row and row2c generation/boot remain gated on Claude explicitly saying idle.

## Child summit owl Din's Fire gate — CONFIRMED (2026-11-26)

Claude confirmed that the rule stands; cs22c recorded the source and corrected the private row2c fixture. **No rule, admission or runtime change is applied.** The rule remains `is_child and Dins_Fire`; there is no pending loosening candidate.

- Source of `remake/child_death_mountain_trail.toml:44-47`: native `Event/EventFlow/Npc_Kaepora_DeathMountainTrail.bfevfl.zs`, entry `Talk`. `Event4` (decoded index3) queries `IsGet.Item_DinFire`; true/case0 enters the flight-offer path, whose accepted choice reaches `Event5` (index51), transition `Dm_DeathMtTrail_0030`. The comment also cites the guide's Great-Fairy-before-flight ordering.
- Kareem's **original row2 did own Din's Fire**: its frozen child baseline has `IsGet.Item_DinFire=true`, stock1; all eight preserved save/save-work images also read true/1. Frozen924202 does not replace this owl flow (`fast_start` is empty). His flight is not evidence for flight without the spell.
- Bender's `child-death-mountain-summit-owl` checkpoint has Din's Fire false/0. Standing at the owl does not establish eligibility to fly. **It is not the corrected row2c source.**
- **Corrected row2c, explicitly approved by Claude:** copy the ORIGINAL row2 child baseline byte for byte: Din's Fire owned; both Fairy and Time never owned; Impa heart unset. Travel noclip to the summit is allowed, **off before the owl**; take the owl to Impa's roof, then walk normally into the cow-shed roof pickup. No save, inventory or flag edits.
- Keep Claude's approved private pool-preserving three-cycle: **roof=Time, gallery=Din's Fire, LW GS Above Theater=Fairy**, subject to every beatability, age-return, tier, pool and admission oracle. The original two-way exchange's failed oracle attempt is preserved, not rerun unchanged. The cycle is a test-packet repair, not a logic change.

Read-only ownership and native-flow evidence: `work/r22-pr42/keep-time-ca62f1e6ac/owl-gate-evidence.json`; active corrected contract: `current-cases.json` there. Gated code, builds and the later sweep remain pinned to **`ca62f1e6ac3bcea7f2b9b4d0535e007f2eb11581`**; this note is documentation only.

## Line22 complete; row2c deferred to line22b — 2026-11-26

Claude directed immediate lock release for cs22d's merchants line23 while cs22c finishes low-load diagnosis. **LOCK RELEASED cs22c line22** was posted at16:22 after removing only the matching owned lock. Row2c rebuild and its single boot now require **line23 completion, explicit placement approval and renewed line22b lock ownership**. The line24 sweep remains gated on line23; nothing auto-starts.

- Frozen code `ca62f1e6ac3bcea7f2b9b4d0535e007f2eb11581` passed format/lint,4,961 synthetic and920 native tests. No rebase, version bump or re-freeze.
- Both Fairy-after-Time fix packets are **READY FOR PLAY, not played**: exact adult row2b roof replay, and an open laboratory-roof normal-path control. Each passed production build/oracles, untouched baseline/profile preparation, one idle-wrapper boot and real startup resource-load verification. Both post-boot checkers report BOOTSTRAP_ONLY. Their expected normal/no-player branches remain unproven until runtime evidence.
- Both use independent byte-identical original adult row2b copies: both instruments owned/stock1/history true, Time selected. No inventory, flag, age, model or physics edits. Routes, launchers, hashes and read-only checker commands are in `work/r22-pr42/PLAY.md`.
- The approved private three-cycle **also failed beatability**, with1,100 unreachable placements. No output mod/profile/boot was produced. Its ordinary fill reproduced the frozen hash; admission passed. Failed two-way and three-way attempts remain preserved.
- A pre-fill diagnostic, without generation or mod writing, prints the actual failed frontier: **1,332 placements,232 collected,1,100 unreachable**. Child inventory includes Din's Fire1, Bomb Bag1, Zelda's Letter1, but Ocarina0, Bracelet/Strength0, Magic0, Met Child Zelda0 and Time Flows0. Death Mountain Summit's blast/smash route is blocked; Darunia's chamber needs playable Lullaby; night/clock routes remain shut. This is **not** a missing-letter gate. Time remains behind the roof route and Fairy at an adult-only source.
- Claude approved cs22c's pool-preserving four-cycle: **roof=Time, gallery=Din's Fire, LW GS Above Theater=Piece of Heart, LW Gift from Saria=Fairy** (Fairy's vanilla source). Same original row2 child fixture and owl/no-noclip approach; no rule/settings/admission changes. He authorized diagnostic-only production oracles now, workers1/BelowNormal, **no mod output or boot**; build plus one boot remains line22b after line23 release and renewed lock ownership.

Evidence: `work/r22-pr42/keep-time-ca62f1e6ac/{three-cycle-frontier-native.json,three-cycle-diagnosis-and-proposal.json}` and each ready case's build/baseline/boot receipts. The first diagnostic omitted the production N64-only fixed-location filter; its printed discrepancy and payload are preserved as invalid. One cause-directed diagnostic correction applied the exact production `from_placements` fixed-map rule, at workers1/BelowNormal. No unchanged seed rebuild or oracle bypass.

### Approved four-cycle diagnostic PASS

Production external admission and physical traps, exact settings/pool and screened admission, goal beatability (**23 spheres**), tier order (**zero violations**), child-only Time before adulthood and the configured age-return gate all passed. The child-only search reaches Saria's Fairy and gallery Din's Fire at sphere2, roof Time at sphere5; full search collects the adult Theater Piece of Heart at sphere8 (zero-based indices). No fill, mod output, child profile or boot was performed; no lock was reacquired.

Receipt: `work/r22-pr42/keep-time-ca62f1e6ac/four-cycle-oracles.json`; actual oracle Python independently printed **priority0x4000**, workers1. The first launcher stopped before oracle setup because an untyped Windows pseudo-handle query returned invalid-handle error6; values were printed, HANDLE signatures corrected, then one cause-directed launch passed. Build and one boot still wait for line22b after line23 release. No further cycle is authorized without asking.

Line22b harness preparation, **not execution**: external `line22b-cases.json` pins the approved four-cycle and original child baseline under a fresh `line22b/2c` root and distinct line22b owner. The driver forwards its existing-style `--cases` contract to build/preparation and checks ownership before creating an output directory; the later readback uses the same explicit cases file. The four-cycle validator and existing ready roof/open contracts passed a lightweight smoke. Actual CLI help passed; a nonowner invocation refused before any case stage or output directory. No generation, rebuild or boot started, and no existing failed attempt or adult packet moved.

## Authorized line22b completion and line24 execution

Claude relayed cs22d's explicit19:32 line23 release (`c5625a0` full gate PASS) and authorized line22b then24. cs22c atomically acquired the lock at22:05, without disturbing another owner. Direct thread read confirms the release and queue; future required handoffs are read from the thread by cs22c, not delegated to Claude's watcher.

Line22b **PASS** on frozen code `ca62f1e6ac3bcea7f2b9b4d0535e007f2eb11581`: approved four-cycle full build/oracles201.88s, untouched original row2 child baseline and actual launcher dry-run1.56s, **one** idle-wrapper boot15.59s, exact startup load verifier PASS. Independent postboot typed checker reports BOOTSTRAP_ONLY, all profile progress bytes unchanged. Row2c target-area appearance, pickup and live/Continue use remain **unplayed**; no save/physics/model repair or extra boot. Packet: `work/r22-pr42/keep-time-ca62f1e6ac/line22b/2c`; mod-tree SHA256 `bab732c363d38ec4bc6d0732d57e8c6e6548a524c736128d42e11e434995b60e`.

Ownership transitioned in place to queue24; the lock was not released between authorized stages. Paired measurement is500seeds per arm:200Broad+50Defaults+50Recommended, plus200WorldPickupsAnywhere. Main stays `5dcb21b5e29b78e96e8c254d0106647267ad4d87`, candidate stays ca62. Main's binding songs remain default, labelled nearest main equivalent; candidate anywhere is judged absolutely against zero exhausted, all production pool/goal/age-return/tier oracles and explicit retry/per-seed floor-placement reporting. Detached BelowNormal, four workers, ten-minute progress/thread polling; no generated mods or gameplay proof from this sweep.

The first line24 capture stopped before any seed: the shared play-builder loader imported PR42-only `ocarina_pickup`, absent from main0.2.9. Printed full error and preserved scripts/logs/receipt in `work/r22-pr42/sweep24-ca62f1e6ac/diagnosis/attempt1-main-import`. Corrected only external capture imports to common production APIs with pinned-source/metadata checks. One cause-directed measurement launch uses unchanged heads, recipes and seed lists; no generated seed is repeated.

## Line24 final PASS and owned-lock release

Both frozen arms completed **500recipe/seed cases**,1,000total, with **zero exhausted, rejected or pool/goal/age-return/tier failures**. Candidate absolute acceptance passed; all planned recipe/seed pairs are present. Standard300 = Broad200+Defaults50+Recommended50; binding WorldPickupsAnywhere adds200per arm.

| Cohort | Seeds/arm | First failures main | Candidate | Extra attempts main | Candidate | Max attempts main/candidate |
|---|---:|---:|---:|---:|---:|---|
| Broad | 200 | 0 | 0 | 0 | 0 | 1 / 1 |
| Defaults | 50 | 1 | 1 | 2 | 2 | 3 / 3 |
| Recommended | 50 | 0 | 0 | 0 | 0 | 1 / 1 |
| WorldPickupsAnywhere | 200 | 9 | 8 | 9 | 10 | 2 / 3 |

The binding comparison is **nearest main equivalent**: the same effective kinds and empty fast-start, main songs=`song` versus candidate songs=`anywhere`. No exact placement/sphere equality comparison or improvement claim is made for that cohort; candidate's zero-exhaustion/oracle bar is independent. Defaults and Recommended each have50identical placement/sphere digests; Broad has0of200identical. Production retry attempts are retained per seed, not discarded or manually repeated.

Binding coverage proves the new destinations were exercised:

| Binding source kind | Shuffled/arm | Ocarinas main | Candidate | Songs main | Candidate |
|---|---:|---:|---:|---:|---:|
| BossHeart | 1600 | 0 | 33 | 0 | 206 |
| Freestanding | 2800 | 0 | 63 | 0 | 343 |
| Token | 20000 | 67 | 76 | 0 | 579 |

Every completed seed records each special floor placement's logical item, source location, kind and grant actor in `floor_special_placements`; these are actual generated placement records, not an assumed palette. Primary results are under `E:/OOTRemake/work/r22-pr42/sweep24-ca62f1e6ac/`: `paired-results.json`, `{main,candidate}-rows.jsonl`, arm results/capture records and the driver receipt/log. Main remains full SHA5dcb21b5e29b78e96e8c254d0106647267ad4d87; candidate remains full SHAca62f1e6ac3bcea7f2b9b4d0535e007f2eb11581. This measurement writes no native mod and proves no in-game result.

Detached actual priority0x4000, four workers, two successful ten-minute progress/direct-thread polls; all five capture/sweep/report stages exit0. Total driver time2,250.55s. The owned lock was removed after matching its exact owner, and **LOCK RELEASED cs22c line24** was posted with **@cs22d at22:52**, allowing line25. `lock-released.txt` preserves the posted handoff. Herdr delivery was unavailable, so the CLI explicitly reported the message persisted to the watched thread rather than claiming an agent notification.

**Preparation work complete; gameplay still pending.** `work/r22-pr42/PLAY.md` links the faithful adult roof replay, open-roof normal-path control and original-child row2c Time comparison. Each has its own untouched baseline/profile, pinned ca62 mod and one startup proof. The expected normal/no-player branches and child roof appearance/collection remain unplayed, not inferred from startup. Version remains0.2.9; old failures, saves and outputs stay preserved; GitHub comment/push remains held.

## Played line22 diagnosis — 2026-11-27

Claude relayed Kareem's **2c PASS**, **adult roof FAIL**, **open lab-roof FAIL**; he then confirmed **both** adult Fairy pickups used the small rupee/ammo popup with no item-get animation, including the open-space control. `PLAY.md` records the reports verbatim. The earlier expected camera/IsSpace split did not establish actual branch coverage, and ca62 does **not** keep Time on these pickups.

All three complete played profiles/logs were copied **before interpretation** to `work/r22-pr42/keep-time-ca62f1e6ac/diagnosis/line22-played-20261127-083915/{2c,roof,open}`. All45source/copy file hashes match. No lock, generation, rebuild, test suite, boot, live-profile edit or runtime manipulation.

Actual parent-run typed copied-save checkers, not a raw-string inference, establish:

| Case | Fairy stock/history | Time stock/history | Persisted selector | Source | Life/pieces |
|---|---|---|---|---|---|
| 2c | absent retained | absent -> owned/stock1 | empty -> Time | consumed | 12/0 unchanged |
| Adult roof | owned/stock1 retained | owned/stock1 retained | Time -> Fairy | consumed | 24/0 unchanged |
| Open lab roof | owned/stock1 retained | owned/stock1 retained | Time -> Fairy | consumed | 24/0 unchanged |

Save/save-work pairs agree. Detailed per-image facts/hashes are in `typed-save-facts.json` and the three `*-typed-readback.log` files. No unreported Continue/route observation is invented for2c.

Both Dm_SY_Get flows and GetPouchContent load once in every copied log's startup/pre-map block, from the correct case mod root. No event-execution tracer identifies the pickup branch. Actual written EVFL readback confirms both Fairy receipts continue into KeepTime and the helper entry exists, byte-identically across the three cases (`written-receipts.json`). Resource loads and the checker's coarse LOADED_IN_PLAY label are not execution proof. Late adult Item_Fairy pack loads corroborate a presentation difference but do not establish exact pickup timing or which consumer requested the model.

`ClawshotOcarinaKeepTime` is an EventFlow entry; receipt labels are nodes, **not persistent markers**. Typed GameDataList name-hash lookups find no custom marker/receipt row. Native saved fields **do** exist but are unchanged in every baseline/current image: HavePlayedEvent.Dm_SY_Get=true, WithoutPlayer=false, GetPouchContent=false. Sticky/no-delta fields do not count new invocations or prove subflow execution/bypass. 2c's Time branch does not call the Fairy-only KeepTime helper, so its PASS does not prove that helper executed.

### Native classification finding and proof limit

Claude proposed Small/Large as a hypothesis. Read-only actual resources confirm generated Fairy's PouchActorInfo is Small and Time's Large; both retain Ocarina special deal. **Additional pack-level difference:** generated Fairy inherits its native Fairy PouchContentParam with no explicit GetType override; generated Time inherits an explicit Large GetType. Both wrappers grant the correct native Item_Ocarina actor. A registry-only edit could leave this separate component representation unequal. Evidence: `pouch-metadata.json`, `pouch-components.json`.

All914native EVFL files decoded without errors. The only serialized own-add performer actions found are Dm_SY_Get/Event35 and WithoutPlayer/Event0; no explicit native EquipOcarina write or standalone Small world-grant routine was found in the inspected EVFL/pack data. The data identifies the native Ocarina special-deal target, **not its exact compiled dispatcher/selector-write site**. `dsm.open` rejected the installed Nintendo NSO as unsupported; no existing native-clock ELF/database was found. Small-path bypass is strongly supported, **not proved at an engine instruction**; late overwrite/identity or ownership-dependent routing is not excluded. The old child Fairy disappearance is not declared explained.

### Approval-gated proposal, NOT APPLIED

cs22c recommends normalizing **only the generated world Fairy** to the checked Time/donor Large contract in **both** representations: generated wrapper PouchContentParam.GetType and generated PouchActorInfo.PouchGetType. Preserve native Item_Fairy/Pouch_Fairy rows, grant identity, OcarinaTypeValue policy, Time, songs, receipt guards, physics/model/positions, source flags and every save. This is a candidate experiment, not a claimed fix.

Blast radius is world Fairy on Freestanding/BossHeart and generated Token donor descendants; Token's ocarina family already permits Small/Large, and its composer preserves donor pouch semantics. Prompt/get-pose routing, camera fallback, remote retrieval and cleanup/autosave timing need played proof. After approval, use fresh original-baseline copies for both failed adult cases; retain actual Time selection before/after Continue, stock/history, source-once and life/pieces. Never-owned Fairy/absent-Time and Token/BossHeart delivery must remain correct; the child missing-Fairy actor needs separate play evidence. Existing explicit EVFL simulations do not exercise native classification dispatch.

Safe alternative, separately approved: exclude Fairy from **Freestanding/BossHeart shared floor admission and Token catalogue**, matching0.2.9's Fairy exclusion while retaining Time and songs. Align producer/donor selection and screened external-placement refusal; keep Fairy in its pool and supported other delivery routes, never silently drop/substitute it or repair old outputs/saves. This deliberately reduces Fairy-world scope instead of shipping the demonstrated failure.

Full evidence/proposal: `diagnosis-and-proposal.md` in the preserved snapshot root. Posted to `cs-r22` at09:04. **Awaiting Claude's OK; no implementation, rebuild or lock.** GitHub comment/push remains held.

## Approved generated-Fairy Large normalization — line26

Claude explicitly approved the proposed two-field normalization after the diagnosis: **only** generated Fairy's wrapper PouchContentParam.GetType becomes the native Time/Fire Arrow Large U32 enum, and its inserted PouchActorInfo.PouchGetType becomes Large. Native Item_Fairy/Pouch rows and parent members, Time, grant identity, receipts, physics and saves are unchanged. cs22c implements that contract; no runtime patch or version bump. The0.2.9-style Freestanding/Token/BossHeart Fairy exclusion above remains **written but unapplied**, reserved for a played failure.

Focused synthetic verification at actual BelowNormal0x4000, workers1 / pytest-xdist2: **96 passed in5.81s** (`test_ocarina_pickup.py`, `test_t1a_receipt.py`, `test_ocarina.py`). Serialized generated component and registry assert Large; native parent bytes and canonical native row bytes remain identical. The real-dump composition regression additionally verifies generated floor/Token classification and native rows; it runs with the full dump gate, not claimed here.

Read-only production before/after native proof under `work/r22-pr42/line26-large/verification/{before,after}-native.json`:

- **17,121 canonical native rows byte-identical** across ActorInfo, GameActorInfo and PouchActorInfo. Source table bytes also unchanged.
- The generated Fairy pack changes **only** its own wrapper pouch member, adding typed U32 GetType; every native copied member and every other generated member is identical. Generated Time's entire pack is byte-identical.
- The generated Fairy PouchGetType is the **only** registry-row delta; all native Item_Fairy/Time rows and all ActorInfo/GameActorInfo content remain identical.
- **All five composed receipt EventFlow files are byte-identical** before/after, using production receipt then keep-Time transforms on actual read-only native inputs. Existing normal/no-player behavioral regression tests also pass. This does not prove native dispatch or a played pickup.

Contributor test mapping: `test_pouch_actor_info_rows_are_the_ocarinas_without_their_ocarina_type` is adapted/renamed to `test_pouch_actor_info_uses_large_world_get_and_keeps_native_rows_byte_identical`; it preserves the original no-OcarinaTypeValue/native-row guarantees and updates only generated Fairy's approved Small->Large contract. No behavior coverage is dropped.

Next approved order: commit this focused change; compare several existing Broad and WorldPickupsAnywhere placement digests against the line24 ca62 controls (no new sweep if identical); atomically acquire line26 lock or exit73 and check player absence; full format/lint/synthetic/dump gate; then one build and one boot per adult roof, open roof and **original row2 child Fairy** (not the later Time four-cycle). Child baseline remains original Din's Fire-owned/both-instruments-never-owned; owl or travel noclip allowed, off before pickup. A cheap existing-baseline Token Fairy row is conditional on a verified candidate. Fresh independent profiles only; never reset/repair old played profiles. Release with @cs22d and launchers. Pickup animation/text/Time selection/Continue are **future player expectations**, not boot acceptance.

## Line26 shipping merge and faithful controls

Claude then directed merging pushed main **a4d474bb** (merchants) before focused/full-gate work. **7968343e54508d909c47ab32b37d55b57d0d3db7** merges it into the PR42 branch without rebase, with Assisted-by trailer. The only conflict was `test_event_registration.py`'s import: retain the union `FillError, allowed, with_screens`, preserving both consumers' assertions. No test/metadata field removed. The original Large fix is179600d7d3; test-only2d614eae42 resolves effective inherited Token GetType rather than requiring a flattened component.

No full gate had started on either pre-main head, so no old-head gate was killed or relabelled. The Large-only digest proof is retained as Claude directed: five Broad and five WorldPickupsAnywhere cases reproduce actual pre-fill inputs, placements and spheres exactly versus line24 ca62. It is not a merged-tree fill claim.

Merged focused verification: **139 passed,5native skips in5.09s**, actual priority0x4000, two pytest workers and CLAWSHOT_WORKERS1; pickup/receipt/keep-Time/event-registration/merchant/fill consumer suites. Full gate then started detached, no tool deadline, on clean `pr42-line26-merged` at7968343 after atomic mkdir-or-exit73 ownership and actual players[]. Gate owner relay=claude-26-large-fairy/queue26; direct thread and dump-log polling every10minutes. Format/lint/synthetic pass; the native tier has setup-error markers and is still running for actual tracebacks. **No full-gate PASS, row build or boot is claimed.**

### Explicit merchant and baseline rulings

Claude: preserve the rows' original settings and frozen placements, no reroll; Gift-off leaves merchant checks absent, Gift-on pins all three native sales with production keep_vanilla/identity semantics. The line26 contract enables Gift and pins **GC Medigoron=Giants Knife, Kak Granny Buy Blue Potion=Blue Potion, Wasteland Bombchu Salesman=Bombchus10** in the spec, not in settings. Every original map/settings hash, admission/screens, pool, goal/age-return and tier oracle stays intact. If an intentional main logic change prevents the old ordinary hash reproducing, print that cause rather than relaxing a guard or rerolling.

cs22c discovered the ca62 helper's three-file copy omitted the original option.sav, although the original row2/row2b baselines supplied it. Those old profiles are not complete byte-identical original controls; their account/caption/progress were identical and all reported failures remain valid. **Line26 uses all four original files unchanged**, including each source's own option.sav (adult59f91fe6..., child77f27330...), not unrelated options. New explicit case opt-ins preserve old historical readback contracts. Actual read-only source-contract proof passes all four cases' typed baseline requirements and four-file hashes; no profile/mod was created.

Mandatory rows remain adult roof, adult open-roof exchange and **original child Fairy roof**, not the later Time four-cycle. Child retains Din's Fire and both never-owned instruments; travel noclip off before owl/pickup. Under Claude's optional Token-row authorization, cs22c selected **Kak GS Near Gate Guard**, source11629189455828560791/companion11629189455828560789 bothfalse in the same original child. It owns native Small/Medium Bomb Bags, bombs30/capacity30; token stock4. The verified pool-preserving cycle is Fairy roof→GS, Token GS→ZD Chest, ZD Rupees20→roof. An earlier scout incorrectly borrowed Wasteland Chest's item from924205; that cycle is discarded, not used. Normal night/combat/retrieval only, no state repair; all production oracles still precede any output. Real native producer→Token composition readback independently succeeds with typed Large and the native Fairy grant (7.06s); it does not explain the unresolved native-tier setup errors or prove play.

Every new row requires full item-get animation and correct Fairy text, not the small popup; Time must remain selected/shown/played and persist after Continue **where owned**. Never-Time child rows must select/play Fairy and retain never-owned Time. Token replacement must not grant a Gold Skulltula Token. Boot is startup only. The exclusion fallback remains written and unapplied pending a played failure.

### Combined sweep assessment for Claude, not authorization

Recommend one **200-seed merged-tree Gift-on WorldPickupsAnywhere** cohort with empty fast-start and all three merchants genuinely shuffled, **not** the play rows' native pins. Line25 Broad already requested songs=anywhere: the missing coverage is not that string. Its actual BossHeart/Freestanding palette has only five native items; line24's PR42 binding palette adds both instruments and all12songs, before merchants merged. The new combined destination/check policy has not been swept.

Measured line24 binding200 totals1,989.40seed-seconds, ideal8.29minutes at4workers; capture45.59s, whole500candidate arm1,081.77s. Estimate **10–15minutes for the new single binding200**, or20–25minutes for a whole single-arm500, BelowNormal/four workers, plus queue/player waits and possibly extra retry cost. Absolute production pool/admission/goal/age-return/tier/retry acceptance, not false exact placement equality across changed policy. The assessment will accompany the gate result; **Claude decides, no sweep auto-start**.

## Line26 stale layered fixture and authorized resumption

The first full gate on7968343 completed with format/lint PASS, synthetic **4995 passed/925 skipped**
and native **891 passed/1 skipped/31 setup errors in2935.77s**. Every setup error is the same missing
`Pack/Actor/Item_BombchuBundle_Medium.pack.zs` in the old `work/rounds/r22/layered-dump`, not a
failed placement assertion. Failed logs/receipt remain in `work/r22-pr42/integration/gate26-7968343e54508d909c47ab32b37d55b57d0d3db7`.
The read-only canonical RomFS has that file. No oracle, admission, placement or save was changed.

Claude directed asking cs22d for the passing gate23 inputs. Its `run_line23_gate.sh` lines64–66
and cs22d's10:30 confirmation agree: OOT_ROMFS=`E:/Games/Hookshot/romfs`,
OOT_NUP=`E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup`,
OOT_DUMP=`E:/OOTRemake/work/r22-merchants/layered-dump-main-b98fb9b`.
Claude's final instruction is **use that layered cache directly, read-only; dump tier only**.
The rerun started at BelowNormal on the same immutable7968343 snapshot, n8/workers3,
under the retained line26 lock; original format/lint/synthetic passes stand. `local_romfs`
materializes its disposable output elsewhere and the native fixture asserts source size/mtime unchanged.
No dump PASS or row readiness is claimed while it runs.

Before the final direct-use instruction, cs22c had already made the then-authorized fresh owned
`work/rounds/r22/line26-layered-7968343` copy. It is **unused, not the rerun input**. The current1299
required resources all match canonical RomFS bytes and none was missing from cs22d's cache.
Both prior layered inputs and canonical working members retain size/mtime; proof is
`work/r22-pr42/line26-large/verification/complete-layered-cache.json`.

Claude now **approves** the combined **200 WorldPickupsAnywhere seeds on7968343**, only after
dump PASS: Gift on, all three merchants genuinely shuffled (no play-row identity pins),
songs anywhere, PR42 expanded floor palettes, four BelowNormal workers. Bar: **zero exhausted**;
report first-fail seeds and retry attempts. Same fixed line24 binding seed list2026112600–2026112799;
absolute pool/screened admission/goal/age-return/tier acceptance, not cross-policy placement equality.
Prepared single-arm measurement reuses the unchanged line24 backend and additionally asserts all three
merchant checks are shuffled in every completed seed and both instruments/all12songs remain admitted
at Token/BossHeart/Freestanding. It does not execute capture or fill before the dump-pass guard.
After that sweep passes, build and boot rows a–d (adult roof, open roof, original child Fairy, Token)
as already specified, keeping the lock throughout; release explicitly with @cs22d and launchers.

