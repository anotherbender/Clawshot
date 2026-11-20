# Round 19 — Tokens (cs19d)

Agent `openai-codex/gpt-6.1-sol`; branch `r19/tokens`; base main `d9deb65`.
Issue #12: opt-in progression at the first 100-token House reward; default stays junk.
All new game behavior is **built, not played** until Kareem's paired Longshot 3.0.0 check.
No game launched, user seed/save modified, runtime folder written, version bumped, merge or push.

## Prerequisite: the missing three

The issue predates round 15's completed repair. Current `remake/token_routes.toml` and
`tests/test_world_token_routes.py` already admit all 100 unique native sources. This was
missing remake-specific data/logic, not three absent actors or an unsolved physical gap:

| Removed N64 identity | Actual remake source | Native enemy Hash | Required route |
|---|---|---|---|
| HF GS Cow Grotto | HF GS Lone Tree | 2177746409373494991 | Field tree roll, attack and low-drop touch; day permitted |
| LLR GS Rain Shed | HF GS Wetland Grotto Crate | 9047381233010434881 | Explosive grotto; child Skullwalltula kill persists; adult crate |
| LLR GS Back Wall | LLR GS Tower | 2730878115209290675 | Night; child Boomerang or adult Hookshot retrieves high reward |

The table accounts for three removed and three added sources; it does **not** assert physical
one-to-one replacements between its N64/remake columns. Census IDs, not names or positions,
identify checks. Route admission was Kareem's rc.3 packet, Claude's 2026-11-14 ruling;
its final revisit was not played and is not claimed here. Historical evidence:
`plans/rounds/r15-tokens-spec.md` section 4, `r15-scrub-tokens.md` native parity/review sections,
and source citations in `remake/token_routes.toml`.

Round 15 explicitly kept issue #12 open: once those three became reachable, a real Gift seed
put Stone of Agony at House100. Maintainer policy therefore became explicit
`nonprogression_only = true`, enforced across fill, swaps and external assignments. This
round implements the requested explicit opt-in rather than weakening reachability or defaults.
Current read-only proof: `uv run python E:/OOTRemake/work/r19-tokens/prove_tokens.py`
collects **100/100**, no missing source, and reaches/collects House100. Omitting only those
three source placements reproduces **97**, exactly those three missing, and House100 inaccessible.
Both arms win. Bootstrap matches the existing vanilla oracle: all native small keys plus
Slingshot/Hookshot for no-save-warp entry guards, **zero upfront tokens**. This is model proof,
not a fresh physical route playtest; no additional route change is justified.
Receipt: `work/r19-tokens/token-collection-proof.json`.

## Implementation contract

Proposed by cs19d from issue #12: `shuffle_100_token_reward = false`; enabling requires
Gift/NPC shuffle and removes only House100's automatic non-progression exclusion before world
compilation. Existing threshold100, NPC route, explicit item exclusions, item/type holds,
native first-reward completion and repeat payout remain. Token shuffle is independent: with it
off, collect native tokens; with it on, collect the same 100 token items from supported chests
and Skulltulas. The existing `GatheringTokenGold.bfevfl.zs` is already covered by the pack's
`Event/EventFlow/*.bfevfl.zs` resource pattern; no new native input/output path is introduced.
`test_pack_nup_dump.py` now includes an explicit option-on all-kinds parity row.
The setting has CLI, CS1 and metadata-driven app exposure; both presets stay off. False is
omitted from effective serialization like the existing Fortress switch, preserving old strings.

### Native first versus repeat

Read-only supported RomFS flow trace (no GPL source used): Event215 is
`GatheringTokenGold:TakenReward_Common_Event_200Rupee`,
`TakenRewardActor = Obj_Rupee_Gold`. The common wrapper ultimately passes that argument to
the native `Dm_SY_GetInEvent` handover; the existing Gift compiler replaces this parameter,
not the shared get flow. The first source is gated by the native quest's completion.
Event471 is the separate repeat call to `Dm_SY_GetInEvent:GetInEvent_NotTurn` with
literal `ActorName = Obj_Rupee_Gold`; it remains native. Exact node/write trace and staged
fixture provenance follow in the external packet report.

### Focused evidence so far

House/default-policy and three-route focus initially gave **36 passed, one failed** in 180.72 s.
The new native inverse test used `ActorName` at Event215; the actual parsed payload printed
`{TakenRewardActor: Obj_Rupee_Gold}`. Corrected only that test field name, not production.
The aimed native plus Settings/CLI/schema/API run gave **63 passed in 106.64 s**:
`work/r19-tokens/focused-integrated.log`. No unchanged rerun of the failed parameter test.

Rebase onto current local main `d9deb65` reported up to date. The requested post-rebase
House/routes/option suite gave **54 passed, one HTTP schema-request timeout** in 291.52 s.
CPU evidence printed **100% load**, Defender working set **1,153,789,952 bytes** and concurrent
Python workers while cs19b owned the sweep lock. The isolated HTTP node passed **1/1 in
7.70 s**, without a source change, as the round's load-diagnosis rule requires.
The new transport test unnecessarily compiled the full world behind GET schema; it now
uses the existing `synthetic_spec()` like the other loopback HTTP tests, retaining real
HTTP, Gift-dependency validation and CS1 assertions. No timeout was widened. The separate
production-world form and native House100 tests remain. Receipts:
`rebased-focused.log`, `http-isolated.log`, `http-fixture-focused.log` (**18 passed in 10.07 s**).

Actual isolated browser proof: Recommended starts Off; clicking its native On button checks
the control and produces a CS1 string with the option; Defaults restores Off and disables the
control without Gift. Help states 100-token grind and built/not-played status. Screenshot
observed. Server used in-memory Preferences, no player paths/saves/seeds, then tab/server closed.

## Verification and staging

Implementation, focused proof,400 native-prepared seeds and matched-save candidate/control
are built and checked below. The sole full gate runs after this receipt is committed,
on that exact final head. Authoritative gate results live outside the repo under
`E:/OOTRemake/work/r19-tokens/gate/`; status is posted to `cs-r19` only after all four exits0.
No game/boot/play pass is claimed by that automated acceptance.

### Native trace and fixture

Exact trace: `work/r19-tokens/native/house100-semantics.json`, with read-only probes and
parsed evidence beside it. Native `Reward100` sets `GatheringTokenGold_Father_BacktoHuman`
(Event254) and `KakarikoVillage_GatheringTokenGold_CleanUp` (Event230), grants any unclaimed
10–50 gifts and Event215, then writes `Step_GatheringTokenGold = Complete` (Event232).
There is **no GetReward100 Bool**. The human-father entry tests that quest completion:
incomplete returns to `Reward100`, completed routes to repeat Event471. Thus the existing
quest is the first-check once gate, not rupee/Hammer ownership. Tokens are not spent.
The option changes only Event215's typed `TakenRewardActor`; all that routing stays native.

Read-only scan: **2961** permitted backup/r18 progress files, **zero** natural100/unclaimed,
maximum **48**. The user's one-value fixture edit was therefore necessary. Chosen natural
source is `work/save-backups/2026-11-10_1254-main-fire-temple/save/`
`5a3c9e1f0b7d24680000000000000001/slot_01`: adult, `CollectToken`, father cursed,
10 claimed, 20–50 unclaimed, Hammer absent, 17 rupees, 19 tokens. Only
`PouchData.Item_Token_Gold.StockNum`, key `0x04735978`, offset **89588**, changes
**19 → 100**. Exactly byte89588 differs; source SHA-256 `152d53d2…7d05` and fixture
`b60d3258…dc0a` were independently reread and matched the preparation receipt.
Both arms receive identical copies of this edited fixture; no era/quest/history/ownership edit.

### Staged Longshot 3.0.0 check

Folder: **`E:/OOTRemake/work/r19-tokens/native/ingame/`**.

- **Control:** `Test - house100-main-control-d9deb65.bat`, built from actual main `d9deb65`.
  Production `allowed(House100, Hammer)` is false; the selected junk source emits native Gold200.
- **Candidate:** `Test - house100-candidate.bat`, built from `00c711af0d`, implementation
  `e9f52560ce`. Production eligibility is true with the explicit option; it emits Hammer.

Both builders emitted only `Event/EventFlow/GatheringTokenGold.bfevfl.zs`. The control's
parsed flow is native-identical; restoring only candidate Event215's actor inverse-equals
the complete native tree, including repeats/thresholds/flags/entries. Candidate raw size
301816 → 301808; existing allocation302096 suffices. No GameDataList, message archive or
new resource path. The native100 preview names no reward, and production previews cover10–50.
Receipts: `native/build-{control,candidate}.log`, both packet JSON files in `ingame/`.

Launchers derive from the authoritative template but pin **Longshot 3.0.0 stable**
`builds/stable/v3.0.0/bin/longshot.exe`, with no runtime fallback. They clear
`HOS_FS_OVERLAY`, load exactly one mod, and copy only the fixture's slot/account/options
into separate profiles. Explicit grep found **no `hookshot.exe`** in either launcher.
Real `cmd.exe` dry-run and initial copied-save proof are recorded in
`native/house100-dryruns.log`: both **exit0**, copied trees byte-identical, initial inspector
**PASS** (adult,100 tokens, questCollectToken, father cursed, Hammer0,17 rupees). Neither
game nor launcher real-run was started.

**Claude boot-checks; Kareem plays; estimate 18–22 minutes plus shader warm-up.**
Checklist: `native/ingame/CHECKLIST.md`. Control must give Gold200, candidate usable Hammer,
tokens remain100. Re-enter and Save/Continue: no second Hammer/first reward; the human
father's **native repeat200 is expected** in both arms. Native30 grants the1000-capacity
Giant's Wallet during this fixture's first conversation. Runtime loading proof required:
`mods: Event/EventFlow/GatheringTokenGold.bfevfl.zs <- <this arm>`.
`native/inspect_house100.py --require-played` checks completion/human/claimed thresholds,
100 tokens and candidate-only Hammer stock1. Gameplay, boot and played-save proof remain
unperformed, not inferred from the builder or the dry-run.

### Locked production-pool sweep

Command: `uv run python E:/OOTRemake/work/r19-tokens/sweep.py`.
Exact source/test head **`00c711af0dfd2476b01ed7ee1283000120a21286`**,
21:53:51–22:04:07 on 2026-11-19, after waiting for cs19b's lock. **12 workers** at each
recipe start, neither `longshot.exe` nor `hookshot.exe` running. The owned lock was released
in `finally`; no overlapping heavy job was launched.

| Recipe | Accepted | Attempts | First-attempt failures | Exhausted | Progression at House100 |
|---|---:|---:|---:|---:|---:|
| Broad CS1, `all_anywhere` + Token + option | 200 | 204 | 4 | 0 | 43 |
| Defaults, unchanged | 50 | 50 | 0 | 0 | 0 |
| Defaults + Gift + option | 50 | 51 | 1 | 0 | 16 |
| Recommended + option | 50 | 51 | 1 | 0 | 20 |
| Recommended + Token + small keys anywhere + option | 50 | 85 | 20 | 0 | 16 |

Broad recipe is the supplied `work/r18-fill/settings.txt` with only the new option switched
on; seeds0–197 plus2306988613 and12345. Other cohorts use seeds0–49. Exact canonical strings,
per-seed attempts/rejections, tasklists and timings: `work/r19-tokens/sweep/results.json`;
console: `sweep.log`. Defaults lacks Gift, so it correctly refuses the option; the extra
Defaults+Gift cohort exercises that preset's remaining settings with the option on.

The script captures **canonical `patch.make_seed` arguments immediately before generate**,
including native census/link restrictions and pickup palettes, rather than copying an older
preparation path. Every accepted seed passed production beatability, independent exact
shuffled-stock equality, and a fresh collection search proving **all100 tokens collected
and House100 accessible**. Zero exhausted seeds across all400. Rejections are ordinary
production retries under the unchanged ten-attempt bound, not reseeds or suppressed errors.
No generated game output, player seed or save was opened by the sweep.

### Exact-head gate and handoff contract

Implementation commits: **`e9f52560ce`** (feature), **`00c711af0d`** (isolated HTTP test).
This final receipt changes documentation only; source/test bytes match the successful sweep.
Before the gate: rebase current local main (`E:/OOTRemake/Clawshot`, still `d9deb65`) and
rerun the native first-reward inverse and option consumer focus. Then:

1. `uv run ruff format --check`
2. `uv run ruff check`
3. `CLAWSHOT_WORKERS=12 uv run --with pytest-xdist pytest -n 12`
4. `CLAWSHOT_WORKERS=4 uv run --with pytest-xdist pytest -m dump -n 12`

Gate driver `work/r19-tokens/gate.py` owns `work/rounds/r19/gate.lock`, records its exact
head/commands/tasklists/results in `gate/results.json`, uses no supervisor deadline and
releases only its own lock. At each stage start, a running game changes xdist to4 and
CLAWSHOT_WORKERS to1. Dump uses the requested read-only RomFS/NUP and
`work/r18-issue34/combined-layered-dump`; **no fixture working-set additions** are needed.
The full dump gate includes `test_pack_nup_dump.py` and its new option-on mode.

After all exits0, post **READY (play-held)** with that tested head and observed suite counts.
Do not append a post-gate commit: keep the merge head exactly the gated head. Claude must
rebase/re-gate if main moves before merge. Remaining acceptance is **only Claude's boot
check and Kareem's Longshot 3.0.0 paired play checklist**. Natural100 collection, child
age and every possible reward family are not newly played by this packet.
