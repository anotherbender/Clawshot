# R23 R07 — canonical tunic pickup actors

cs22d (`openai-codex/gpt-6.1-sol`), 2026-11-27. Branch `r23/r07-tunic-model`, original base main
`a4d474bb92e5a6350012e8a1f9b90015942a0513`. **Source implementation complete; in-game model acceptance pending.**
Claude accepted the design and authorized this scoped implementation on 2026-11-27; Kareem's product
constraints are unchanged. No new shuffle admission, logic, pool, native shop price/service or runtime change.

## Evidence and decision

Kareem relayed Bender's Claude's data finding: chest tunics resolved to shelf actors. This was not a played
missing-model observation. The private read-only pack probe against supported build `e0f3ccfa` resolved the
complete parent chains: `Shop_Armor_Goron` and `Shop_Armor_Zora` inherit the shop base and have no effective
EventPerformerRef; `Obj_Armor_Goron` and `Obj_Armor_Zora` inherit the item base and provide the native
`PouchContent_PickUpItem` performer. Native pouch/equipment identity was already established by
[r22-shops.md](r22-shops.md). No pack graft, ActorInfo edit or runtime hook is proposed by analogy with
[the ocarina fix](../chest-ocarina-model.md).

cs22d proposed canonical Obj forwards plus Shop reverse aliases; Claude accepted this on 2026-11-27,
including preserving `held_items` by logical tunic identity and leaving Freestanding/BossHeart admission
unchanged. Detailed private evidence/design: `E:/OOTRemake/work/rounds/r23/r07-tunic-design.md`,
`r07-tunic-native.json`, and `r07-tunic-mapping-proof.json` beside it; no extracted game data is committed.

## Cutover

- The two item-table forwards now select `Obj_Armor_Goron` / `Obj_Armor_Zora` for chests and gifts.
- Existing backward-only aliases resolve each native Shop spelling to its canonical Obj spelling. Both
  actor spellings reverse to the same logical tunic; native census/source hashes and shelf actors remain native.
- Removed the gift-only Shop-to-Obj remap and migrated its callers/tests. General source aliases and
  merchant-source normalization remain. `held_items` still returns no tunic-specific restriction, preserving
  existing Chest/Shop/gift destinations rather than tightening them to gifts only.
- `shops.toml`, `locations.toml`, tracker icon aliases, token rewards and floor/boss-heart pickup palettes
  are unchanged. Shop sale/display actor resolution remains independent of the chest table.
- Synthetic regressions exercise both forwards/reverse spellings, whole-tree chest output (including
  unchanged Hash, event and other fields), gift grant behavior/destinations, and census/shop/tracker identity.

## Initial verification on a4d474bb — scoped authorization, not a full gate

All checks below ran at **BelowNormal**, with all `OOT_*` variables removed. Pytest used **`-n 2`**,
with the UI extra installed and no separate Clawshot generation worker launched. No dump was opened,
seed generated, full gate run or r22 gate lock acquired. Claude expressly requested focused checks only.

```text
uv run --extra ui --with pytest-xdist pytest -n 2 -q \
  tests/test_tunic_models.py tests/test_tunic_gifts.py tests/test_patch.py \
  tests/test_scene_gifts.py tests/test_shops.py tests/test_patch_chests.py tests/test_seed.py \
  tests/test_item_display_names.py \
  tests/test_tracker_icons.py::test_only_whitelisted_names_resolve_to_icon_files \
  tests/test_tunic_gifts_dump.py tests/test_gifts_dump.py
58 passed, 12 skipped in 30.48s
```

The 12 skipped checks require the read-only dump. Their obsolete remap expectations were migrated;
no dump result or full synthetic-suite result is claimed.

`uv run ruff format --check` and `uv run ruff check`, scoped to the seven changed Python files:
**7 files already formatted; all checks passed.** Python navigation was attempted before the exported
remap removal; the configured ruff LSP does not implement references, so explicit literal callers were traced.

## Play hold

**Both R07 rows are staged offline; no R07 game was booted or launched.** Claude accepted the paired
design and separately authorized staging after the refresh below. Matched profiles, source eligibility,
the visible selector and entrance-facing source identities are qualified; see the final receipt below.

A maintainer must observe each actual held-up model/text/credit and persistence, with the runtime's
`mods: <changed file> <- <arm path>` proof. Source tests establish the actor choice, not visible in-game
success. Keep the control's predicted missing model distinct from an observation. No separate release for
merchant work plus PR #42 alone; these changes belong to the round23 release per Kareem/Claude.

## Post-PR42 refresh — 2026-11-27

Claude authorized rebasing the owned, unpushed fix903dcb426b onto main **5ea1c585**. Clean replay,
no conflicts; rebased **code commit bcad1546e700fa06b969494d26b9c6565bfd20a9**. No source change was
needed after rebase. The identical focused command above reran: **58 passed,12 dump-skipped in2.87s**;
the same seven-file scoped Ruff format/check passed. BelowNormal, UI extra, all OOT_* unset and -n2.

cs22c posted **LOCK RELEASED at19:17** before cs22d acquired the physical gate lock. It was released
immediately after these focused checks; no full gate, dump run, sweep, native boot or launch.

Updated paired design (not staged): `E:/OOTRemake/work/rounds/r23/r07-paired-play-design.md`.
Main5ea1c585 control versus the rebased fix; both tunics in two nearby Mido sources, matched INI/options,
normal openings and persistence reloads. Qualification issue disclosed: historical R14 calls the two
Hash IDs a left pair; current location definitions call them top/bottom right. Hashes, not that ambiguous
side label, govern; identify the actual pair before any future staging. The backup timestamp is not a
verified on-screen save selector. No original save, spoiler or seed placements were read for this design.

## Authorized offline paired staging — 2026-11-27

Claude accepted `E:/OOTRemake/work/rounds/r23/r07-paired-play-design.md` and authorized both rows under
`E:/OOTRemake/work/rounds/r23/r07-tunic`, explicitly forbidding native boot/launch tonight. **READY OFFLINE,
UNPLAYED.** Real detached checkouts main5ea1c585 and fixbcad1546 each generated/wrote the same constrained
production play seed at BelowNormal, one worker, with fail-closed CIM/tasklist guards before each generation
stage. Both beatability searches passed,23 spheres and180 runtime resources each; exact shuffled pools and
identical logical placements. Full182-file comparison:179 byte-identical. Only child/adult Kokiri Bancs'
two `Drop__DropActor` leaves differ (Shop_Armor_Goron/Zora → Obj_Armor_Goron/Zora), plus those two strings in
our new seed's plan metadata. Entire remaining decoded Banc trees and all other files are equal.

The complete copied R14 rebased-4 family is unmodified: **13 November2026,2:33p.m., Kokiri Forest,
AUTOSAVE,3full hearts**, stored14:33:43, photo child Link outdoors on the ground path. Another2:33 autosave
shows the treehouse platform/ladder: do not choose it. Child age, both tunics unowned/stock0 and both chest
flags clear. Native child/adult placements resolve the previously ambiguous Right names: entering the
house and facing its chests, Hash4555665598794293658 is near-left (Goron) and12786193094758345086 far-left
(Zora). Names and hashes unchanged; no chest moved. This is data/caption qualification, not new human play.

Independent profile copies match all nine bytesets, including the frozen common G1–G3 INI and R14
account/options. HOS_CONTROL/MEMro safe-default no-pause launchers, private paths, explicit live flag/gate.
Six actual Python/batch/default/live+dry plans passed without starting anything, even with an inherited live
gate. Output/profile hashes, guard receipts, provenance, literal selector, complete diff explanation and
future model/text/credit/persistence checklist are in the private packet's `PLAY.md`, `arms.json`,
`qualification.json`, `profiles.json`, `output-comparison.json`, `dry-runs.json` and per-arm generation receipts.
Gate lock released after generation/comparison. **Zero native boots/launches; all runtime acceptance remains
pending.** No generated output, game data or extracted native table is committed here.
