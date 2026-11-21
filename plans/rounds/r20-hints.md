# Round 20 — static hints (cs20a)

Agent `openai-codex/gpt-6.1-sol`; branch `r20/hints`, rebased onto main `5ed31bc` (original base `acbb903`).
Scope: static text only, no new saved flags, grants, item windows, fill/logic/destination changes.
Research and staging: `E:/OOTRemake/work/r20-hints/`; dump and natural save backups read-only.
All hints play PASS, including cumulative altar v3 and the consolidated three-scrub packet02; cs20a never launched the game. Final merged-head gate evidence: `E:/OOTRemake/work/r20-hints/merge-gate-receipt.json`.

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

Stretch: existing `strong`/`useless` retained; added `very_strong` with original
Clawshot weights (woth8, barren4, item4, sometimes1, random1; no weighted junk;
dungeon caps6). Balanced/default and fill RNG stay unchanged. All four are normal
app choices per Claude's superseding04:30 decision, not generator-only controls.
Selector, D29 and settings focus: **28 passed in3.50s**. Actual CLI accepted
`--hint-distribution very_strong --print-settings` and emitted a CS1 string.

## Verification / staging

Every changed message has a checklist row and a required candidate load-log/visual check.
**Claude's play-budget decision, 2026-11-20:** candidates required; controls optional
only if the candidate result is unclear. Priority: scrubs, Great Fairies, altar, House,
Ganondorf. Per-stage times below; nothing over30 minutes. Natural saves preferred;
the sole unavoidable token-stock fixture is documented below and identical in both arms.

No sweep is required unless this track changes fill, destinations, locations or logic.
Full gates, sweeps and many-seed jobs serialize under `work/rounds/r20/gate.lock`;
one private packet seed, like focused checks, uses `CLAWSHOT_WORKERS=1`. Focused
checks use at most2 pytest workers. Rebase current local main and
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
Natural50 stays **unedited**. The sole shipped fixture copies the natural19 fire-temple
save and changes only `PouchData.Item_Token_Gold.StockNum`19→100, at byte89588
(`0x04735978`, Int section2). Exactly that byte changes; source SHA-256
`152d53d2…d05`, fixture `b60d3258…0a`. Both arms use the identical fixture.
An initial unshipped50→100 draft was deleted before any launcher was created;
the19→100 source also exposes the unclaimed20/30/40 previews before talking to Dad.
Original backups remain read-only. No story/era/key/item edit is authorized.

Claude challenged necessity because all sons are freed at50. That is correct;
the edit is for **father-human-only** dialogue, not freeing sons. Native Talk graph
walk, overapproximating every unrelated switch both ways, proves these changed
labels unreachable with `GatheringTokenGold_Father_BacktoHuman=false`:

| Child | Changed father-human-only labels | Example native path |
|---|---|---|
| `Npc_Hylia_025` | `Talk_01` | Event29→34→2→0→7→14 |
| `Npc_Hylia_026` | `Talk_14`, `Talk_12` | Event11→36→38→41; then42→40→39 for12 |
| `Npc_Hylia_027` | `Talk_14` | Event3→21→23→38 |
| `Npc_Hylia_028` | `Talk_14`, `Talk_01` | Event4→47→48→7→28→21→37; then17 for01 |

`GatheringTokenGold:Reward100` Event254 sets that Bool true. It is false in the
natural50 source. The fixture does not force it: Kareem talks to Dad at100 and the
native sequence sets it. Research `father-human-proof.json` records both reachable
label sets and paths. The fixed-state witness `child-coverage.json` covers **31/31**
changed son labels across natural10, natural29 after Dad20, natural50, fixture100
before Dad and fixture100 after Dad. Unknown recent-talk/random/mask switches are
overapproximated, not claimed played. The first staging witness missed028 Talk09/10
because50 skips those under50 lines; adding the **unedited** natural29 plus an ordinary
Dad20 visit reaches them. No second fixture edit.

### Rebase and focused refresh

Rebased cleanly onto local main `479ed443` (kept the additive gift helper).
Post-rebase `-n2`, `CLAWSHOT_WORKERS=1` focus: **38 passed in5.86s**, covering the
three native static-text files and selector/D29/settings tests above. Scoped Ruff:
**4 files already formatted; all checks passed**. No game process at stage start.
An initial private placement preparation overlapped that rebase; its receipt is
superseded, not evidence for the final packet. Final packet preparation pins and
rechecks the source head before recording its oracle receipt.

### Paired packet and reduced play budget

Private seed **20200121** prepared on source `398e0c006e`: **248 shuffled checks,
22 solo-oracle spheres**. Both actual-source arms reconstruct that identical map
through the production external-placement API; these reconstructions are diagnostic
outputs, not two newly certified solo fills. Control source is real local main
`479ed44360`; candidate source `398e0c006e`. **177 resources per arm**.

Native comparison: **40 message identities ×16 archives =640 language-message
deltas**. After restoring just those messages, every other Mals member is identical.
After restoring the seven scrub `SellerMessageId` fields, the entire flow is
identical. All other game resources are identical except the required size table.
The first comparison attempt assumed every file was Zstandard: it printed the
uncompressed `Logic/GanonCastle_Level_Field_00_Prefab_14ba.logic.module.ainb` path.
Fix: decompress only `.zs`, otherwise compare raw bytes. The cause-targeted run passes.

Packet root: `E:/OOTRemake/work/r20-hints/ingame/`.
Start with **`Check - START HERE.md`**. Ten candidate launchers required;
ten paired controls optional only for unclear results, per Claude. Actual texts and
all40 message IDs are in the per-stage checklists. Candidate-only estimate
**60–95 minutes including loading/travel**, rather than the rejected2–4h paired plan:

| Priority / stage | Candidate estimate |
|---|---|
| 01 Scrubs, Lost Woods | 5–8min |
| 02 Scrubs, Crater and Field | 8–15min |
| 03 Great Fairy, before Fire quest | 3–5min |
| 04 Great Fairy, after Fire quest | 5–8min |
| 05 Altar | 3–5min |
| 06 House,10 tokens pending | 2–3min |
| 07 House, natural29 plus normal Dad20 visit | 5–8min |
| 08 House, unedited natural50 | 6–10min |
| 09 House, one stock100 fixture before/after Dad | 8–12min |
| 10 Ganondorf intro | 8–12min |

All **20 template-based launchers dry-run successfully**; copied progress bytes
equal their specified source in every arm. Longshot **3.0.0 stable** is pinned,
only the selected arm mod loads, `HOS_FS_OVERLAY` is empty; launcher grep finds
no `hookshot.exe`. No game or boot check. No original save, seed or game folder written.
Required proof remains the runtime's own `mods: <file> <- <candidate path>` plus
the visible result. Identical randomized029 endings17/18/19 cannot be individually
distinguished on screen; native per-label readback covers all three. Ganondorf's
native pending-intro route is inferred, not played; never force story flags to repair it.

### Ordered final gate

Claude assigned **turn5, after cs20c** in
`E:/OOTRemake/work/rounds/r20/gate-order.txt`. Acquire **only after cs20c explicitly
posts LOCK RELEASED**, not merely when the directory disappears. No waiter can
acquire it, and no sweep is required for this text-only track. Before that turn:
rebase current local main and refresh the focused checks. Freeze the evidence commit
before the full gate; the newly requested packet receipt follows separately. Gate receipt:
`E:/OOTRemake/work/r20-hints/gate/<head-first10>/results.json`; readiness requires
all four stages passing on that head. Final counts will also be posted on the thread.

### Final frozen-head gate preparation

Observed **cs20c's explicit04:17 LOCK RELEASED**, then rebased cleanly onto
current local main **`df6214b35f`**, as Claude directed. Rebased implementation/evidence
head before this receipt commit: `8a25acc5a0`. No production or test edits after that
rebase. Fresh required focus (`-n2`, `CLAWSHOT_WORKERS=1`, real RomFS):
**38 passed in5.47s**; no game process at the stage start.

Claude's supervisor boot checks for **both staged v1 arms** pass on Longshot3.0.0:
**218 RomFS entries, one mod, save mounted, zero crashes/fatals**; both USen message
archives load. Evidence `E:/OOTRemake/work/r20-hints/bootcheck-results.txt` is linked
from `ingame/Check - START HERE.md`. This is load proof, not dialogue play proof.
cs20a did not boot the game.

The staged packet currently retains its disclosed control `479ed44360` and
candidate `398e0c006e` heads. **Claude's final packet requirement:** after the full
gate passes and before READY, rebuild the candidate from that exact gated head,
same seed/placements, `CLAWSHOT_WORKERS=1`, no lock needed. Hash **every output
file** against staged `r20-hints-candidate-v1`. Identical: record equality in
START HERE and this round file. Different: restage the gated candidate, report
the differing paths and request Claude's new boot check. No gameplay claim.
No sweep: this track changes no fill, destination, location or logic.

This gate-preparation receipt is committed before the owned turn5 full gate.
`gate/<gated-head-first10>/results.json` is the authoritative exact-head status;
the four recorded commands must all exit0. The newly requested after-gate packet
comparison requires a subsequent **round-only receipt**; publish its head separately
from the gated code head, with source/tests unchanged. Final evidence and READY
(play-held) follow only after the full gate and packet comparison pass.

### Printed gate cause and narrow metadata correction

Initial gate `30173d8282`: format/lint pass; synthetic **303 failed,31 errors,
3845 passed,805 skipped** in427.15s; dump not started. The owned lock was released.
Printed schema cause, not a fixture/deadline issue (recorded CPU load38%):
generator choices were `balanced,strong,very_strong,useless`; label/help keys were
only `balanced,strong,useless`. `app.schema._rows` derives live distribution choices
from the generator, so the earlier "app Balanced-only" note was wrong.

**Claude's superseding decision:** Very strong is a normal app choice, like the three
shipped choices; no disabled/unavailable/refusal metadata. The04:29 refusal proposal
was stopped **before any refusal edit was applied**. Fix adds its label and plain
"new this round" help, and aligns the TOML choices list. No schema validation weakened.
Consumer regression: CLI Very strong CS1 is accepted by app validation.

Before retaking the lock, expanded focus:
`CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n2 tests/test_settings.py
tests/test_app*.py tests/test_ui*.py -q`: **149 passed in62.23s**.
This includes `tests/test_app_schema.py`; these files are now part of this track's
focus set alongside the six hint/native files above.
Actual **Chrome headless** surface proof: all four choices enabled; selected
`very_strong` through the real dropdown; backend returned a validated CS1.
Screenshot `work/r20-hints/ui-very-strong.png` inspected, proof JSON retained,
browser/server closed. Only the seed-library root was isolated to an empty folder;
no personal seed read, no DOM state mutation or game launch.

Very strong uses the existing hint writer. The staged packet stays Balanced to keep
the required identical seed/settings/placement comparison; a distribution-specific
stone read is **built, not played**, not claimed covered by that packet.
Claude retained turn5; one corrected frozen full gate, including dump, follows
these cause-targeted proofs. No unchanged rerun and no sweep.

### Native inverse contracts repaired on the real dump

Gate `89d31ae476`: format/lint pass; synthetic **4180 passed,805 skipped,24 warnings
in433.57s**. Native dump: **800 passed,2 failed,24 warnings in2930.73s**.
Printed first difference: native Event293's shared `Enemy_Scrub_Business_Heart_01`
message ID versus the intended per-sale `Clawshot_Scrub_DMC` ID. The two old whole-flow
inverse tests restored item/price/offer-guard edits but not the new message IDs.

Claude approved a narrow **test-contract update**, not a production change:
`tests/test_scrubs_dump.py` and `tests/test_shop_settings_dump.py` explicitly assert
the correct selected message ID for every grant/tier/copy, then restore that event's
exact native ID before retaining the **entire whole-flow equality**. No saved gate,
payment/cancellation branch or unrelated field is permitted to differ.
Ruff format diff: both files already formatted.

The **two exact failed nodes**, isolated against the **real**
`OOT_ROMFS=E:/Games/Hookshot/romfs`, `-n2`, `CLAWSHOT_WORKERS=1`:
**2 passed in69.70s**. No fixture-only claim and no unchanged rerun.
These files join the focused set. Production remains unchanged from `89d31ae476`.
Per Claude, freeze this test/round receipt and run **all four full-gate stages again**,
including the complete native dump tier, before the final packet rebuild/hash.

### Final full gate and exact gated-packet identity

**PASS on frozen code/test head `50a17ff465340a3e5dfe57bca3a68dd518c5f381`**:

| Stage | Result |
|---|---|
| `uv run ruff format --check` | exit0 |
| `uv run ruff check` | exit0 |
| Synthetic, `-n8`, `CLAWSHOT_WORKERS=4` | 4180 passed,805 skipped,24 warnings;444.61s |
| Complete dump, `-n8`, `CLAWSHOT_WORKERS=3` | 802 passed,24 warnings;2951.18s |

All stages saw no game process. No failures/reruns in this final gate; no sweep.
`work/r20-hints/gate/50a17ff465/results.json` records `passed=true`, all exits0.
Owned lock released; explicit **LOCK RELEASED** posted at06:31.

**After the passed full gate**, rebuilt from that exact gated head at one worker,
same private seed20200121, identical requested CS1 and placements. Compared
**every output file** to staged `r20-hints-candidate-v1`: **179/179 SHA-256 and
size identical**, including all177 RomFS resources and both non-RomFS files;
**zero added, removed or changed paths**. No normalization, exclusions or metadata
exceptions. Complete dual manifests:
`work/r20-hints/ingame/gated-packet-hashes.json`; gated build receipt:
`ingame/r20-hints-gated-50a17ff465-build.json`.

START HERE now states the identity and links those receipts. No candidate restage
was needed; Claude's existing Longshot3.0.0 v1 boot proof covers the byte-identical
gated output. No changed dialogue or Very strong distribution was played.

**READY (play-held)**: candidate checklists required in priority order; controls
optional only for unclear results. All40 changed message identities are staged.
The sole19→100-token House fixture remains identical across both arms; natural50
is unedited. Ganondorf's native pending-intro route remains inferred until played.

Per Claude's after-gate documentation request, this final commit changes **only
this round receipt**, not production or tests. The gated code head above and the
separate receipt head are both disclosed in the handoff; do not describe a new
code/test revision as gated.

### Altar readability follow-up

Claude reported staged width wrapping split reward/region names across lines and
pages. Fixed with a dedicated atomic-line formatter: one complete reward/region
pair per row, page breaks only between rows, at most2 rows/page. Door and Bridge
requirements each occupy their own complete lines, with no word wrapping.
Rows are checked against the **observed native48-character envelope** (native3
rows/page; new2). This is a character/row proof, not measured engine-pixel clipping.
All16 language archives retain their native opening/style tags.

The exhaustive pair probe printed49 for
`Forest Medallion: the land outside Ganon's Castle`. Removed only the optional
leading article from altar region names, preserving the complete region identity;
the aimed proof then checks all reward/region combinations without splitting names.
Revised existing all-language regression requires each complete reward/region pair
on one row, within the native envelope; archive inverse proof stays.
First focused native run:5 passed in5.82s (`-n2`, internal1), before article trimming.

Only stage05 will point to the rebuilt candidate, private seed20200121 and the same
placement map. Other stages keep their already boot-checked v1 candidate. The new
stage05 needs Claude's boot check and Kareem's readability check; no game launched
by cs20a and no original save/game folder written.

**Morning gate rule (Claude):** no full-gate stage starts while exact image
`longshot.exe` or `hookshot.exe` exists. Check before every stage; if present, wait
**600 seconds** and check again. The external driver now waits instead of using the
old reduced-worker fallback. Both Longshot processes were present at follow-up start;
focused native work uses at most2 processes/internal1. No sweep.

After article trimming: **5 native tests passed in11.31s**. Exhaustive proof:
**324 reward/region pairs ×16 native styles**, maximum **45 characters**;
**288 actual native archive Door/Bridge readbacks** (18 cases per language),
each row atomic and every page1–2 rows. Evidence `work/r20-hints/altar-layout-proof.json`.

### Altar v2 final gate, boot and provenance

Stage05 v2 was rebuilt from **`7ed1eafc861cded497b284b5060f6066e1402251`**,
same private seed20200121, settings and placement map. Native delta proof across
all16 archives permits only `SignboardWood:TempleOfTime_000` and the required size
table to differ from v1; every other file is identical. Actual staged text:
**7 pages, at most2 atomic rows/page, maximum36 characters/row**. The existing
stage05 candidate launcher alone now selects `r20-hints-altar-v2` and a fresh v2
private profile; dry-run passed and copied progress bytes equal the natural source.
Other nine stage launchers remain unchanged.

**Claude boot PASS** on Longshot3.0.0: crash0/fatal0, save mounted, one mod,
177 RomFS files/218 entries, modded USen archive loaded. Evidence
`work/r20-hints/bootcheck-altar-v2.txt` is cited in START HERE and the05 checklist.
No played readability/pixel-clipping acceptance is claimed.

**Full exact-head gate `7ed1eafc86` PASS**:

| Stage | Result |
|---|---|
| Ruff format / lint | both exit0 |
| Synthetic, `-n8`, internal4 | 4180 passed,805 skipped,24 warnings;547.12s |
| Complete native dump, `-n8`, internal3 | 802 passed,24 warnings;3407.50s |

Every stage began with `game_running=false`. Driver honored **four600-second
waits**: three before format, one before dump. No failures/reruns, no sweep.
Owned lock released and explicit LOCK RELEASED posted; gate receipt
`work/r20-hints/gate/7ed1eafc86/results.json` records all exits0 and `passed=true`.

**After the passed gate**, rebuilt again from that exact head at one worker.
Every file compared to Claude-booted stage05 v2: **179/179 SHA-256 and sizes
identical**, no added/removed/changed paths and no exclusions. Complete manifests:
`work/r20-hints/ingame/gated-altar-v2-hashes.json`. No restage or repeat boot needed.
START HERE and05 checklist cite this identity. This final receipt changes only this
round file; gated production/tests remain unchanged.

**READY (play-held), altar follow-up:** one reward/region per whole line, Door/Bridge
on their own lines. Stage05 only updated; in-game readability acceptance still
belongs to Kareem. cs20a did not start the game or write to original saves/game folders.

### Kareem's hints01–10 played results and cumulative-conditions follow-up

Reported by Kareem through Claude; treated as ground truth, not rerun:

| Check | Played result / decision |
|---|---|
| 01 bridge scrub | PASS: Green Rupee for17, paid17 and received1 rupee. |
| 01 two-scrub grotto | NOT FOUND, not a text/grant failure. Directions and copied-save access being verified. |
| 02 HF and DMC scrub offers | NOT FOUND: locations/route unclear; no pass claimed. |
| 03 Fairy before Fire | Perfect. |
| 04 Fairy after Fire | Perfect. |
| 05 altar | Reward rows readable; repeated `Door:` lines confusing as alternatives. Revise only conditions. |
| 06 House pending10 | Correct. |
| 07 House29 | Correct. |
| 08 House50 | Correct. |
| 09 House100 / cure | Correct; sons repeating rewards after cure is fine. **Keep unchanged.** |
| 10 Ganondorf | Legible, during skippable voiced scene like Rauru. **Keep unchanged.** |

**Claude's required correction:** one cumulative Door sentence across pages,
generated from the selected Door mode; Rainbow Bridge gets its own generated
sentence. Every condition row is at most36 characters, with explicit conjunctions
and then/play wording, not repeated `Door:` labels. Each condition block starts
on a fresh page; the accepted atomic reward/region rows are unchanged.
Closed mode still distinguishes owned shuffled stones from completed fixed stone
quests, and still requires Time Ocarina/Song, Impa's send-off and playing the song.
Song-only/open and vanilla/zero/count bridge variants retain their actual conditions.

Real-RomFS focus: **5 passed in22.90s**. All16 native styles checked,324 atomic
reward/region pairs/style, plus **576 settings/language cases**:528 generated
condition rewrites and48 unchanged-default cases. Generated condition rows<=36;
reward/region envelope unchanged at48 (exhaustive maximum45).
Scoped Ruff: both files already formatted, all checks passed.

Stage05 alone will use the same seed20200121/settings/placement map with the new
condition paragraph. New candidate needs Claude's boot proof and Kareem's clarity
check. Other accepted text, post-cure repetition and Ganondorf timeline stay unchanged.
Directions for the three not-found offers are native/save-backed work in01/02
checklists, not a logic loosening or a new save edit. No sweep. Full gate remains
game-idle-only with600-second waits before every stage and starts only under the
free owned gate lock.

### Verified Lost Woods route and source-access blocker

Native placements/music crossings, with public-guide cross-check, locate the
two-scrub grotto under the cracked boulder in the final clearing before Sacred
Forest Meadow. From Kokiri's Lost Woods entrance: **Right, Left, Right, Left,
Straight, Left**; boulder in the final clearing's far-right corner. The01 checklist
now distinguishes the Goron-shortcut grotto, blue-rupee rock and Deku Theater pit.
Inside, the nearer left scrub is the one-time nut-capacity seller targeted by the
packet, not the farther right repeat seller. Directions are data-backed, not played.

Read-only source-save proof: **all Bomb Bags0/never obtained, Bombs0, Bombchus0,
Hammer0, child Link**. Native rock accepts Bomb/Hammer damage; there are no Lost
Woods bomb flowers. Thus current01 copy cannot open this entrance as equipped.
The passed bridge purchase stands; this is an access blocker, not a text failure.
No save edit or Noclip permission added. Existing02 copy is being checked for a
natural child-return alternative, including one-time reward completion state.
Evidence stays outside the repository: `work/r20-hints/lw-directions/`; walking
landmarks and source values are in `ingame/Check - 01-scrubs-forest.md`.

Stage05 v3 is staged on `c786100799`, fresh identical natural save copy. Claude's
`work/r20-hints/bootcheck-altar-v3.txt` confirms Longshot3.0.0,218 RomFS entries,
one mod, mounted save, zero crashes/fatals and modded USen loaded; cited in START
HERE and05. Boot-only: new cumulative wording clarity remains unplayed.

### Verified02 directions and natural-access resolution

**Catalog conflict escalated to Claude:** `location_names.toml:2915` and old HF06
notes say fenced/Gerudo-side/password fight. Native placements/flows instead put
the password scrub at the **Castle Town gate**, east of the drawbridge, with no
nearby fence; Nintendo Life's remake password guide independently agrees.
The Gerudo-side Fairy Note chest is a different target. No frozen catalog/logic
change made in this text-only track; maintainers were told the exact conflict.

Adult walks out the town gate, turns left before the drawbridge, follows the wall
about40m to the cracked ground cover; the glowing Note07 tree is about14m farther
north-east. Read as adult (first note auto-reads; if prompted, first answer).
Return at the Master Sword pedestal normally; Forest completion allows this on
the source save. Child bombs the hole and selects the **third** password answer,
`Sell somethin', will ya?`. Adult gets native sold-out dialogue, not the sale.

DMC's ledge scrub exists **only in child placements**. Child climbs the summit
trail, enters the crater beside the owl, turns left/downhill past the upper-grotto
boulder, then drops onto the ledge. It is not the adult Hammer grotto. Child heat
damage and walking topology remain unplayed; directions distinguish observations
from placement-derived inference.

Existing02 source/copies are identical: adult,17 rupees,7 hearts,Small Bomb Bag
with5 bombs,Slingshot8,Nuts20,both shields,Prelude/Time songs. All four once-sale
flags are false. Thus use this **already-staged02 copy after native child return**
for the remaining01 grotto too: no new launcher, copied save, inventory edit,
fixture or Noclip exception. Budget1 bomb HF +1 LW +up to3 summit; preview/decline
all three offers before choosing at most one purchase with the initial17 rupees.
Do not repeat the accepted bridge sale. This resolves original01's access blocker
by an existing natural profile, not a claimed in-game pass.

01/02 checklists and START HERE now give landmarks, normal return, password,
age restrictions and bomb/money budget.02 is20–30min with a natural break;
remaining01 is a separate5–8min from Kokiri's woods entrance. Research evidence:
`work/r20-hints/field-crater-directions/findings.txt` and `lw-directions/`.
Neither route was played by cs20a. Only05 candidate was restaged; all other mods,
launchers and accepted dialogue stay unchanged.

### Altar v3 played acceptance and main-base update

Kareem, reported via Claude: **05 v3 PASS, "much better"**. Cumulative conditions
are accepted; no further05 replay requested. START HERE/05 record the played
acceptance separately from Claude's boot proof. Other passed text stays unchanged.
The01 confusion included expecting every grotto to have a boulder; directions now
explicitly distinguish the exact final-clearing rock, decoy rocks and open pit.

Claude reports main moved to `5ed31bc` (start merged). Finish the running old-base
gate on `c786100799` first; then rebase onto `5ed31bc` and re-check the merge before
the final receipt. This is not yet a merged-base gate claim. Existing02 natural
copy, with five bombs and unsold targets, is the reachable source for all three
remaining offers after normal child return; native/save-backed, still unplayed.

### Maintainer-approved wording correction and single remaining packet

Claude confirms the **logic is already correct**: HF -> HF Inside Fence Grotto
uses `can_blast_or_smash`, citing the cracked spot right of the castle gate by the
river. Only player-facing text is wrong. Approved one separate commit: HF scrub
`where` in `location_names.toml`, plus HF06 wording in playtest `questions.md`,
`session-10.md` and `answers.md`. Preserve logic, IDs and unplayed HF06 status.
Apply/commit after the old-head gate finishes so its production inputs stay frozen.

02 is now the **single remaining hints packet**, on the existing02 save: adult
reads Note07 -> native child return at Temple -> HF password sale -> child DMC
ledge sale -> child LW two-scrub-grotto front sale.01 bridge stays PASS; its old
grotto step is retired, not a second pending test. Exact LW walking/decoy/seller
directions moved into02. START HERE directs only to02, with natural breaks,
five-bomb budget and17-rupee single-purchase limit. Only external checklists
changed for consolidation; no mod/launcher/save change and no new boot required.

### All hints play complete — packet02 accepted

Kareem, reported via Claude: **02 PASS, every offer and text as expected**:
HF password scrub, DMC child ledge scrub, LW grotto front seller. All hints play
is complete, including the former01 grotto check in the reachable02 copy.
05 v3's "much better" acceptance and all previous passes stand; no replays.
START HERE/01/02 now record completion. No mod change or new boot needed.

Claude's final sequence: finish old-base native stage; commit the separate
four-file HF/HF06 wording correction; rebase onto `5ed31bc`; full game-free gate
on the final head; then READY for Claude to merge. **cs20d/trials waits behind
this turn**, so retain the cooperative gate turn through the final-head gate,
not just the old-base run. No final receipt before that gate.

### Superseding gate order: old native cancelled, final head only

Claude changed the plan for Kareem's40–65-minute Fortress play: **stop the old
eight-worker native stage now**, not finish it. cs20a terminated the owned
gate process tree (root82368), including all eight pytest worker trees:
23 processes terminated successfully. Old `c786100799` native is cancelled and
cannot count toward the final merge gate. Its earlier4,180 synthetic pass is
historical only. Physical/cooperative lock retained; cs20d/trials follows.

Separate wording commit **`9f94b2e787`** (pre-rebase `303614b474`) changes only HF `where` and the three
HF06 playtest descriptions. It identifies the castle-gate tree note and child
password sale while keeping the distinct Gerudo-side chest age question and
unplayed HF06 ledger status. No logic, IDs or staged mod changed.

Rebase onto `5ed31bc` immediately; focused tests use at most two workers.
Then **one full gate on the final rebased head**, driver waiting600s while
either game image exists before each stage. No final READY claim until it passes.

### Rebased integration and final source freeze

Clean twelve-commit rebase onto `5ed31bc`; no conflicts. Separate HF/HF06 wording
commit is `9f94b2e787`. Focused merged tests: **12 passed in8.05s**, using exactly
two pytest workers and one internal Clawshot worker: names catalog, presentation
and native static-hints contracts. No sweep, generated mod change or new boot.

The old native run is explicitly cancelled in its results JSON. Retained gate
ownership is transferred by the existing owner token, without dropping the lock.
The final full driver checks HEAD and waits600s for game idle before each stage.
This round-record commit is included in the final source head; no later source
mutation is planned. Successful exact-head evidence/counts are published in the
external `merge-gate-receipt.json` and final cs-r20 READY message, not inferred
from old-base results. cs20d/trials takes the next turn after that full gate.
