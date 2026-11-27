# Round22 PR42 integration — cs22c

Authorized by Claude: line21, relay `claude-21-after-029`, after release0.2.9 and explicit line20 LOCK RELEASED. Branch `r22/pr42-integration`, worktree `E:/OOTRemake/clawshot-r22/pr42-integration`. Contributor head `ceab0744c00a325c80de46a7c6df6f2f24388778`; main `5dcb21b5e29b78e96e8c254d0106647267ad4d87` (tag `v0.2.9`). Main is merged INTO the contributor branch; none of Bender's commits is rebased or rewritten.

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

