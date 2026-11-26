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
