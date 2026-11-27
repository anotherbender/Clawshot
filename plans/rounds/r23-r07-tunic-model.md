# R23 R07 — canonical tunic pickup actors

cs22d (`openai-codex/gpt-6.1-sol`), 2026-11-27. Branch `r23/r07-tunic-model`, base main
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

## Verification — scoped authorization, not a full gate

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

## Play hold / next authorized stage

**No R07 play rows, profiles, mods or launchers were staged; no R07 game was launched.** Claude's order:
wait for PR #42 to merge, then rebase onto that new main before building the paired main-control and fix
rows with the same early tunic chests and independent starting profiles. Both rows need HOS_CONTROL/MEMro,
quiet no-pause launchers and the mandatory safe dry-run/live gate. Qualify the existing test-save family,
unopened source flags and unowned tunics first; never alter a real player's save or manufacture eligibility.

A maintainer must observe each actual held-up model/text/credit and persistence, with the runtime's
`mods: <changed file> <- <arm path>` proof. Source tests establish the actor choice, not visible in-game
success. Keep the control's predicted missing model distinct from an observation. No separate release for
merchant work plus PR #42 alone; these changes belong to the round23 release per Kareem/Claude.
