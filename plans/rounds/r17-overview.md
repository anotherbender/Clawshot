# Round 17 — index summary (2026-11-17–18)

The pre-split roadmap contained no Round 17 section. This summary combines its existing track records
with Claude's Round 18 intake and Kareem's played reports supplied to Track H. It does not replace
Claude's round outcome. Read the [roadmap index](../00-roadmap.md) plus this round's files.
Baseline: main `2ba2f9a`, released version 0.2.2 plus Round 17 work.

- [Track A: bugs](r17-bugs.md): child Bolero/Requiem return guards, child Kokiri Sword equipment guard,
  Longshot options copy and tracker Skulltula source counts. [Sword investigation](r17-child-sword.md).
- [Track B: dungeon items](r17-dungeon-items.md): experimental `dungeon_items=all_anywhere`, small-key
  family audit and reward/bridge plans. Defaults and presets remain own-dungeon.
- [Track C: chests and tokens](r17-chests-tokens.md): three hunted chests and independently admitted
  Token destinations for gift-held items. Token weighting was dropped, not shipped.

## Played follow-up supersedes earlier built-only claims

Kareem's reports on 2026-11-18 are ground truth; no seed contents or saves were opened for this summary.

- The child Sword guard **FAILED in play**: returning from adult equipped an unowned Kokiri Sword even
  though the patched equipment flow loaded. A passing native-data test/full gate did not certify it.
- Off-area Forest boss-key credit opened the normal boss door. Off-area map/compass state did not make
  the pause map available; visit and era controls did not resolve it. Track C in Round 18 owns the repair.
- `all_anywhere` exhausted generation under Kareem's broad settings. Its one successful packet did not
  establish broad-recipe compatibility; Round 18 owns the fix and sweep.
- A no-ocarina Minuet lesson softlocked; the same play-along completed with an ocarina. Dampé's race
  also exposed a one-way escape requirement. These are Round 18 work, not Round 17 acceptance claims.

Source: Claude's `E:/OOTRemake/work/rounds/r18/_intake.txt` and the Round 18 Track H prompt.
Earlier track handoffs remain historical evidence, not a claim these later failures were fixed.
