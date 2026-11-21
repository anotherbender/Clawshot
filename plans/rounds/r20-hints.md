# Round 20 — static hints (cs20a)

Agent `openai-codex/gpt-6.1-sol`; branch `r20/hints`, base main `acbb903`.
Scope: static text only, no new saved flags, grants, item windows, fill/logic/destination changes.
Research and staging: `E:/OOTRemake/work/r20-hints/`; dump and natural save backups read-only.
No game or boot check started. Implementation focused proofs pass; staging/gate pending. Nothing played.

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

Generator-only stretch: existing `strong`/`useless` retained; added `very_strong` with
original Clawshot weights (woth8, barren4, item4, sometimes1, random1; no weighted junk;
dungeon caps6). Balanced/default and fill RNG stay unchanged; app remains Balanced-only.
Selector, D29 and settings focus: **28 passed in3.50s**. Actual CLI accepted
`--hint-distribution very_strong --print-settings` and emitted a CS1 string.

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

## Completed native message trace and implementation

The table was posted in short parts on `cs-r20` before each group's implementation;
all labels below were resolved in **all16** language archives listed above.
These are native message identifiers, not copied game dialogue.

| Group | Member / labels | Source and formatting envelope |
|---|---|---|
| Altar | `EventFlowMsg/SignboardWood.msbt:TempleOfTime_000` | Both-age `Obj_TimeTemple_SpiritStoneBase_A_01`, Name `TempleOfTime_000`; `Check_SpiritStoneBase` registration → `DoorOfTime` Event172 → sign camera → Event35/36 `EventTalk`. Native3 rows, max48 characters; new40×2 paginated. |
| Ganondorf | `EventFlowMsg/Dm_InsideGanonCastle_BossIn.msbt:Dm_InsideGanonCastle_BossIn_Text_013_b` | Actual Ganondorf speaker, `VoicePlayActor.EventStartVoice` clip38, start4703/duration296 native frames. Native2 rows/max35; new text hard-bounded to2×35 with no page break. Timeline unchanged. |
| House10 / extra30 advice | `EventFlowMsg/Npc_Hylia_029.msbt:Talk_12,13,14,15,16,17,18,19` | 12–14 describe10;15/16 describe30;17–19 describe both selected rewards rather than wallet spending/capacity. |
| House20 | `EventFlowMsg/Npc_Hylia_028.msbt:Talk_11,14,08,02,03,01,09,10,07` | Removes stale Echo Gem/equip/use advice. |
| House30 | `EventFlowMsg/Npc_Hylia_027.msbt:Talk_06,14,05,03,04` | Removes stale1000-rupee wallet claims. |
| House40 | `EventFlowMsg/Npc_Hylia_026.msbt:Talk_09,14,06,05,12,10` | Removes stale Bombchu tutorial text; native yes/no branches unchanged. |
| House50 | `EventFlowMsg/Npc_Hylia_025.msbt:Talk_00,01,11` | Appends reward name to otherwise-correct curse/family dialogue. |
| Five Fairy refusals | `EventFlowMsg/Dm_FairyFountain_Power.msbt:Talk_00,01,02` | `TriForcePoint` Event132 ability2 bypasses; abilities1/3/4/5/6 → Event8 `IsGet.Item_DinFire`; absent → Event150/144 → Event9/145(00/01) after Fire completion, Event147(02) before it. One shared text surface for all five, not five invented Fairy talks. |

Altar correction: round6's `Dm_TimeTemple_0020` lead is the Master Sword reveal
timeline, **not** the readable altar. Parent printed its parsed `EventFlowFile` after
the first `read_flow` probe rejected a timeline; the helper was corrected to read
timelines, then the actual sign's native registration/actor/action chain was traced.
Research: `altar-search.json`, `altar-native.json`, `altar-dispatch.json`.

**Ganondorf availability risk:** no interactive pre-finale talk surface was found.
cs20a chose the existing battle-intro subtitle requested by speaker, not a new event.
It is late (the native trials normally require Light Arrows already), and it does
not change that logic. No pretend earlier hint or barrier-message takeover.
`Dm_InsideGanonCastle_0003_Text_002_b` stays cs20d's. Audio/timing remain native;
subtitle legibility and audio mismatch are player-check limits, not automated claims.

House limits: native relevant lines reach3 rows/page and52 characters in some
languages; new child text uses40×2. Existing father10–50 previews keep their60×2
format and are not replaced by a second writer. Pending generic child lines and
House50's generic lines retain native English content plus the preview; reward-specific
vanilla effects are replaced. Leading voice/emotion tags are retained. Native choices
ask whether to hear the reward again and keep the same branches. Cursed
`Npc_SkullChild_001..005` messages and father's100/repeat text remain untouched.
No child corresponds to the100 reward. Thirty-one child labels change.

Fairy limits: the shared native01 refusal reaches2 pages/3 rows/max51 characters
across languages; new text uses40×2. Only selected Gift fairy sources enable this
correction. Death Mountain Trail's ability2 bypass and all gift gating stay native.
The refusal is Navi speaking before a Fairy appears, not a new Fairy event.
Research: `house-fairy-native.json`, `children-native.json`.

No MSBT box-limit metadata exists in these archives; observed native envelopes are
not a proven engine hard character limit. The timed Ganondorf clue is explicitly
bounded; other new text conservatively paginates and remains play-held.

### Focused implementation proof

`OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run --with pytest-xdist
pytest -n2 tests/test_static_hints_dump.py tests/test_gifts_rewards_dump.py
tests/test_hints_lines.py -q`: **10 passed in3.23s**.
This covers all16 languages, all31 son labels, mixed10/30 wallet-source identity,
junk previews, retained generic/emotion text, unchanged unrelated messages/archive
members, nine shuffled reward regions, no check-level/junk location disclosure,
bounded Ganondorf subtitle, Gift-only Fairy changes and DMT exclusion.
Restoring only the selected message labels inverse-equals the native MSBT/archive.
New static-hint outputs are Mals archives only; the scrub writer additionally edits
only seven existing message-ID arguments. No native registration dependency changes.

External `condition-proof.json`: **18 actual USen Door/bridge combinations** passed
(all3 Door modes; vanilla, stones0/1/3, medals6, rewards9), default altar unchanged,
starting Light Arrow truthful. First smoke recipe incorrectly paired vanilla bridge
with count4; Settings printed its native supported range0..0. Changed only that
recipe to0 and the aimed rerun passed. No production validation was weakened.
Scoped Ruff printed five overlong new lines; applied its exact formatting diffs
through the edit tool. Final format/lint proof belongs to the full gate.

### Natural-save staging evidence

Read-only backup survey: **735 distinct contents**, **73 classified natural**,
natural maximum **50 tokens** (not100). No path component containing `seed` was read.
`late-save-survey.json` records hashes/flags. Natural early backup
`2026-11-08_1114-main-dodongo`, slot01: child, active Fairy Ocarina, Lullaby,
no Din's Fire/stock0,103 rupees,10 tokens, all five House rewards unclaimed,
Fire quest incomplete. Natural fire-temple backup slot01: adult19 tokens,10 claimed,
20–50 unclaimed, no Din's Fire, Fire complete. These cover both Fairy refusal arms.

Latest natural profile copy `2026-11-20_real-longshot-profile-copy`, slot00:
adult, active Time Ocarina,50 tokens,350 rupees,10–40 claimed/50 unclaimed,
Castle boss key owned, battle-intro history false, native Ganon Step04.
This is also an unedited pending-battle candidate: enter the Tower normally from
the hub so its native progression runs, not by teleporting into the boss trigger.
To cover father-human child variants promptly, one documented token-stock edit
50→100 in a separate fixture is necessary; applied identically to both arms.
Original backups remain read-only. No story/era/key/item edit is authorized.
