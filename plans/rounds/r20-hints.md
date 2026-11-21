# Round 20 — static hints (cs20a)

Agent `openai-codex/gpt-6.1-sol`; branch `r20/hints`, base main `acbb903`.
Scope: static text only, no new saved flags, grants, item windows, fill/logic/destination changes.
Research and staging: `E:/OOTRemake/work/r20-hints/`; dump and natural save backups read-only.
No game or boot check started. Status: tracing; not READY and nothing played.

## Contract and coordination

- Priority order: shuffled scrub/merchant names; altar reward regions and Door/bridge conditions;
  Ganondorf Light Arrows; House children; five Din's-Fire-gated Fairies. Extra distributions stretch.
- English custom hints in all message languages (D26); location hints never name junk (D29).
- Claude approved the small `patch/__init__.py` static-text hook after placement fill.
- cs20d's bridge contract, relayed by Claude: `bridge="tokens"`, integer `bridge_count` 0–100;
  native `PouchData.Item_Token_Gold.StockNum >= count`, no spending. Defaults unchanged.
- **Preview policy confirmed by Claude, 2026-11-20:** sale and House reward previews name
  the actual reward, including junk, matching normal get text. They describe the item,
  not a location; D29 remains strict for Gossip Stone and Light Arrow location hints.

Prerequisites read: repository rules, README, CONTRIBUTING, roadmap, round20 overview,
architecture, orchestration, game-data and world-format specs, decisions, round19 overview,
LACS and tokens records, and the public-docs feature comparison. GPL facts-only source:
`work/refs/sloperina-FINDINGS.md` (PracticeROM/sloperina `docs/FINDINGS.md`), sections1,
5.7 and5.8: typed hashed save fields, upgrades use pouch identities, dungeon map/compass
flags. No source code from that project, OoTR or SoH was opened.

## Message trace (before implementation)

All archives enumerated by `patch.text.languages`:
`CNzh, EUde, EUen, EUes, EUfr, EUit, EUnl, EUpl, EUru, JPja, KRko, TWzh, USen, USes, USfr, USpt`.
Archive path: `Mals/<language>.Product.110.sarc.zs`.

| Group | Native file / label | Routing and limits |
|---|---|---|
| HF and DMC once-sales | `EventFlowMsg/Enemy_Event.msbt`, `Enemy_Scrub_Business_Heart_01` | SHARED label: flow `Enemy_Scrub_Business_Common` Event645/HF and Event293/DMC pass `SellerMessageId` to Event289. Must split per-check message IDs; replacing the common label would make one sale lie. |
| Stick capacity once-sale | same member, `Enemy_Scrub_Business_DekuStickPouch_01`, `_02` | Event317/322 use01; Event555 uses02; all are one saved reward family. |
| Nut capacity once-sale | same member, `Enemy_Scrub_Business_DekuNutsPouch_01` | Event318/326; one saved reward family. |
| Ordinary shops | `DisplayShop` selected-actor text | Existing native selected actor drives names; no new rewrite needed for already-correct shelf names. Medigoron/carpet/Granny experiments stay held, not newly admitted. |

All four scrub labels exist in every archive. Native English sale rows reach50 visible
characters; the longer stick introduction uses3 rows/page and native page breaks. These
are observed formatting envelopes, **not proven engine hard limits**. MSBT has no box-length
metadata. New wording conservatively uses40 characters/row and2 rows/page.
No game play has certified a new box length.

External evidence: `trace_merchants.py`, `merchant-trace.json`, `scrub_labels.py`.
Existing baseline worth preserving: `gifts.skulltula_hint_changes` already rewrites father's
10–50 threshold previews; the requested children's dialogue is a separate trace.

## Implemented: one-time scrub offers

`patch.text.scrub_hint_changes` appends one unique message per selected once-sale and
`patch.scrubs.offer_changes` changes only the seven existing `SellerMessageId` arguments.
HF and DMC can now name different rewards despite sharing the original heart-piece label.
All original messages remain byte-identical; no saved fields, grants, windows, payment,
completion, tier/copy routing or repeat-vendor text changes. Prices come from the same
`sale_prices(settings)` decision as the actual sale writer. Names come from the player's
USen item names, not copied descriptions or spoiler instructions.

Focused command (no game process at start):
`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2
tests/test_static_hints_dump.py tests/test_hints_lines.py tests/test_gifts_rewards_dump.py -q`:
**7 passed in3.15s**. Native inverse proof covers all four offers, distinct HF/DMC rewards,
all16 languages, a junk reward, fixed17 price, unchanged existing messages/members and
unchanged whole flow after restoring only its message IDs. This is built, not played.

Stretch investigation: generator already accepts `strong` and `useless` (verified through
actual `Settings` construction); app currently exposes only `balanced`. `very_strong`
would be the only new generator distribution. Higher-priority static groups come first.

## Verification / staging

Pending focused synthetic/native checks and paired main/candidate Longshot 3.0.0 packet.
Each changed message must have a checklist row, load-log proof and observation; split
checklists above30 minutes at natural breaks. Prefer natural saves; any unavoidable single
fixture edit must be documented and applied identically to both arms.

No sweep is required unless this track changes fill, destinations, locations or logic.
Full gate and any seed generation serialize under `work/rounds/r20/gate.lock`; focused
checks use `CLAWSHOT_WORKERS=1` and at most2 pytest workers. Rebase current local main and
rerun focus before the one exact-head full gate. No merge, push, version bump or personal
seed/save access.
