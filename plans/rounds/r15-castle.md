# Round 15 — castle PRs (cs15a)

Current linear-series base `d66d35f` (includes #26), pending cs15b's merge.
Earlier comparisons used `1db6e63` / docs-only `eff7dab`; version remains 0.2.1.
Agent/model `cs15a`, `openai-codex/gpt-6.1-sol`.
Read required plans, README/CONTRIBUTING, decisions, native §46–48, and all four
PR descriptions, comments and review-thread endpoints before editing.
Review endpoints had no inline comments. No push, merge, GitHub writes or game launch.
Scratch/evidence: `E:/OOTRemake/work/r15-castle/`. No version bump.

## Branches and ownership

Current series: main → #5 → #6 + adaptations → #4 → #20 + adaptations.
Refs: `r15/castle-series-5`, `r15/castle-series-6`, `r15/castle-series-4`,
and top `r15/castle-series`. Earlier two-stack branches are historical.
All ten castle author names/emails/dates and complete messages/trailers were
compared with the original PR commits and match. Claude reviews/pushes/merges.

## Decisions and findings

- #5 move carries main's `prepare_spec`, copies-only destination restrictions,
  and return-kit setup intact. Main solo `return_guarantee_conflict` retained.
- **External-placements API exception requires maintainer confirmation (castle's
  original question): no local beatability/return search; the external placer
  proves its multiworld. Not a verified solo-seed API.** Posted to cs-r15.
- #4 conflicts retain `game`/`detect_game`, all Longshot launcher/build protected
  folders, old-preference migration, tracker routes/assets and carried options.
- `src/clawshot/app/paths.py:67`: new `_source_path` had lost main's moved-dump
  message. Own adaptation restores explicit Not found / choose-again refusal
  for both dump and update.
- `src/clawshot/ui/server.py:254`: separate input roots were protected only at
  selected layer paths during Copy to emulator. A copy beside `base/` succeeded
  (HTTP 200, path printed by failing synthetic regression). Own adaptation also
  protects `dump_root()` and installation parents of dump/update, matching output.
  No real dump was written. Regression now refuses before creating destination.
- No feature redesign or new network/slot/sync protocol. No new dependencies in #4/#5.

## Verification

- #5 target tests: original 3 passed; progressive copy/gift and retained native
  Darunia-source integration boundary added, 4 passed (2.22 s). Initial test
  mistakenly shuffled NPC Darunia before expecting vanilla; printed the prepared
  location, corrected that assertion to Chest-only settings, reran once.
- Main source archived outside repo. Actual full-output comparisons:
  - seed1505 Defaults: 102 files, manifest SHA256
    `65e1e4c6451034789177089ff0757b719dc8c91326ab86d1c1d79d4fe70e5123`;
  - seed1506 Chest/Shop/Gift: 152 files, manifest SHA256
    `796469949802d5ac3b86690046a58abb25a94f8b736d80b268cf1b1690f04f02`.
  #5, #4, #20 and #6 exactly match both main manifests, every relative path and file hash,
  including spoiler/play-note. No output normalization or ignored metadata.
- #4 targeted `test_ui`, `test_app`, `test_pack_dump_folder`, `test_ui_games`,
  `test_ui_dialogs`: 54 passed (14.96 s).
- New emulator layered-source regression: failed before (HTTP200 and copied
  destination), passes after (1 passed, 1.46 s). First setup lacked library
  registration and was corrected before demonstrating the production failure.
- Real browser smoke, isolated LocalServer/in-memory preferences/no native actions:
  real read-only RomFS check displays Verified Version1.1.1 / build e0f3ccfa;
  separate-update toggle exposes its field; moved input reports Not found and
  choose-again guidance; screenshot inspected; browser errors empty; tab/server closed.
- NX generation also matches the same-commit #20 folder outputs for both seeds.
  Those comparisons preceded the current linear series. A handful of baseline
  seeds need no gate.lock (Claude in conversation); full gates require ownership.
- #20 original reader/release/UI/source tests: 20 passed (3.61 s).
- Real NX: 25,511,029,796 bytes, size/mtime unchanged after read-only checking.
  Detected Version 1.1.1 / build e0f3ccfa. NX and RomFS fingerprints both
  `fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`.
- `src/clawshot/pack/_nx/read.py:165`: unchecked top-level seek/read sizes
  produced ValueError/OverflowError for authenticated malformed header values
  (offset/size 18446744073709551615; count ×24 442721857769029238760).
  Own adaptation checks declared archive boundaries before file APIs/allocation.
- `src/clawshot/pack/_nx/read.py:297`: Windows-invalid and case-colliding sibling
  names were accepted, unlike NUP. Own adaptation rejects them before extraction.
  Nine invalid-name cases and one case-collision failed before and pass after.
- `src/clawshot/pack/_nx/read.py:340`: Zstandard accepted trailing bytes.
  Reproduced with a valid file/hash followed by eight unwanted bytes; now exactly
  one frame, declared size, no dictionary and <=1 MiB window/decoded block are
  required before decoding. Encoded block limit 1 MiB + 64 KiB; total mount metadata
  budget 256 MiB. Native metadata about40 MiB; no supported-dump cutoff.
  Scope: input safety, no format writer or new dependency.
- Safety regressions: 18 passed (0.33 s); ruff check passes.
  One frame test first put pytest.raises inside the archive wrapper; moved it
  outside so it catches the public PackError after generator-context unwinding.
- Sources: [NX SPEC 1.0.3 §1/§6/§7](https://github.com/fab918/nxformat/blob/208b815dc21fd92e8bd1c596c708c908b467a457/docs/SPEC.md)
  and [SECURITY](https://github.com/fab918/nxformat/blob/208b815dc21fd92e8bd1c596c708c908b467a457/docs/SECURITY.md),
  MIT. NOTICE and shipped `_nx/LICENSE.txt` retained beside tracker/NUP credits.
- Worker correction: Longshot appeared at #4 comparison stage after the earlier
  no-game check. That one sequential two-seed script had WORKERS=3 but spawns
  no pool. All subsequent stages use fresh tasklist checks (currently WORKERS=1);
  full-gate runner recalculates before every command.
- Independent read-only reviews confirmed Longshot/tracker integration and MIT
  licence parity. NX review identified reserved-field and entry-order leniency:
  authenticated unknown Catalog flags reproduced as accepted; now rejected.
  Parsed Catalog/Manifest/directory/entry/file/block reserved fields, extension
  payload ranges and flags, file-reference spans, entry sorting and depth are
  checked. Presentation metadata is not interpreted or used for version proof.
  `_nx/__init__.py` now says written from specification, not vendored-by-port.
  Final focused safety suite: 19 passed (0.34 s); real NX fingerprint unchanged.
- Actual #20 browser smoke: checked the real NX, observed the blocking modal,
  cancelled a live check, then retried successfully (Version1.1.1 / nx / e0f3ccfa).
  Final modal closed, Check enabled, active check cleared. Only expected
  ERR_ABORTED for cancellation; observed request hosts were loopback only.
  Screenshot inspected; tab and isolated in-memory server closed.
- First #20 full gates: format and lint passed; synthetic 2349 passed,
  188 skipped, two stale refusal-message expectations in
  `tests/test_ui_first_run.py:30`. Claude identified these as released
  moved-dump/wrong-kind boundary coverage (#23/#24), not disposable wording.
  Replaced the deletion commit `8fe6714` with `581fa0e`: keep the test, update
  only #4's expected wrong-kind message. #20's separate `a163380` adaptation
  extends both expected messages for NX. Exact distinct messages, HTTP refusal,
  remembered-dump assertions all retained; targeted suite 3 passed on each branch.
  The earlier B → D → #6 → #20 queue is superseded by the linear-series plan
  and explicit gate stop below.
  Initial #6 gate attempts saw gate.lock held and started no suite.

## Linear-series adaptation and gate stop

- Claude changed the plan: build one series in #5/#6/#4/#20 order, wait for
  cs15b's merge, rebase onto main, then run full gates only when Claude says so.
  Top head gets synthetic + dump; the interior #6 head gets synthetic.
- The old background watchers incorrectly continued under the superseded order.
  Their empty lock directory let another agent treat it as stale, overlapping
  full suites. The #6 diagnostic run recorded 2346 passed, 189 skipped and two
  failures: the invented `make_plan` lambda rejected the new `overrides` keyword.
  No pass is claimed from that overlapping run. #20 was cancelled without a verdict.
- On STOP: cancelled bg_20 and checked both reported PIDs (135284/165980) gone.
  No matching owned Python/uv gate runner remained; bg_19 had finished.
  Removed only the empty owned lock and posted RELEASED at 17:24 for cs15b.
  Deleted the watcher script; no gate job is queued or waiting.
- Separate adaptation explicitly accepts `overrides=None` in the invented-plan
  stand-in. All named-key credit, first-weapon bag and Navi assertions remain.
  On the new series' #6 head, `CLAWSHOT_WORKERS=1 uv run pytest
  tests/test_key_bindings.py tests/test_scrubs.py -q`: **77 passed (1.09 s)**.
  #26's unshuffled Business Scrub guard merged intact; no source conflict occurred.
  On the top head, focused external-placement/custom-text/receive-event/NX/
  moved-dump suites: **44 passed (8.26 s)**. These are local targeted runs,
  not full gates; no lock was taken.
- Future helper stages a populated `owner.txt` in a private claim directory and
  publishes it with one Windows rename; there is no observable empty lock.
  Release verifies ownership and renames away before deleting private files.
  Explicit per-label authorization is required; an unauthorized smoke invocation
  returned 78 before creating any lock or running any suite.
- Main ancestry and all four PR-head boundaries were checked. **No full gate on
  the linear series has run.** After cs15b merges and Claude authorizes: rebase
  with intermediate refs updated, then run the requested head-specific gates.
  Use the expanded r15 layered fixture for the top dump gate; it includes #6's
  ActorInfo/GameActorInfo resources as well as the supplied r14 contents.


## Independent-review adaptations (Claude, after `dba2d8a`)

Six separate adaptation commits; no castle commit amended:

1. `9c20c03`: cap NX file declarations and direct reads at **512 MiB**, above
   the largest of the real archive's 188,284 members (**404,285,906 bytes**).
   Hash chunks incrementally and check the digest before assembling the result.
   Synthetic tests cover authenticated tiny-archive/2-GiB repeated references,
   exact-boundary acceptance, one-byte-over refusal and direct-record bypass.
2. `31a3c3c`: preserve the reader's refusal through dump inspection and HTTP.
   Tests cover decrypted-NSP NX guidance and damaged-file SHA refusal, with
   unchanged remembered dump. Missing-file version guidance still takes priority.
   Only failed, otherwise-complete checks re-read fingerprints for reader diagnosis.
3. `277c23b`: tracker archives use shared `open_source`, including NX and the
   remembered separate update. Folder/archived overlays, cache invalidation,
   newest-snapshot non-fallback, closed handles and HTTP update switches are tested.
4. `05831ba`: cart-only refusal keeps the new separate-update guidance and names
   the missing update resources; the removed fingerprint-filename assertion is restored.
5. `5a32f96`: missing update says **Update not found** and asks for the update.
   Exact missing/wrong-kind HTTP errors and unchanged dump/update preferences tested;
   existing missing-game-dump messages stay unchanged.
6. `0a89114`: notices are controlled by each request's `ShowNotice`, not an
   installed saved toggle. Correct the docstring and remove the unused constant.
   The serialized-flow interpreter now reads its actual Bool argument; both
   notice values deliver the same item, with only the requested window differing.

- Targeted integration (not full gates): **216 passed, 1 skipped (21.40 s)**.
  Suites: `test_pack_nx`, `test_ui_first_run`, `test_pack_dump_folder`,
  `test_tracker_icons`, `test_tracker_http`, `test_receive_event`, `test_ui`,
  `test_key_bindings`, `test_scrubs`; workers 1. Scoped format and lint pass.
  After installing that locked UI extra, the previously skipped decoder regression
  (`test_compressed_texture_pixels_keep_channels_block_order_and_partial_edges`)
  passed: **1 passed (0.15 s)**.
- Installed the already-locked UI extra for native visual verification; no dependency
  metadata changed. Actual NX Bottle icon decoded with texture2ddecoder 1.0.6,
  served through the real tracker icon HTTP route and visually inspected in Chromium:
  **341×341**, complete image. NX + separate real RomFS update gives identical PNG bytes.
  Isolated in-memory server/tab closed and throwaway server script removed.
  No seed or normal save opened for this smoke.
- Bounded NX reader still detects Version1.1.1/build e0f3ccfa; fingerprint remains
  `fc09c4af707a0ca092188cf014f6fdf3d40514def773f097b798f52f9f28bc93`.
  Archive size/mtime unchanged. No game launched.
- Fresh main `d66d35f` versus the fully adapted series code head `0a89114`:
  **zero differences** for all three recipes, including every relative path,
  resource, spoiler and play note. Both sides generated anew, workers 1.
  The verified `src` tree is `9dc59684ce904fff87c5cb26d3eaa7afdd5c2a95`;
  the following round-record-only commit does not change that source tree.
  Manifests: `work/r15-castle/review-main-d66d35f-manifest.json` and
  `work/r15-castle/review-series-0a89114-manifest.json` (outside the repo).

  | Recipe | Files | Matching manifest SHA-256 |
  |---|---:|---|
  | 1505 Defaults | 103 | `90c3916bd00713fabcd2288582806e3b714302ebbdbc8bff928311a997f625f7` |
  | 1506 Chest/Shop/Gift | 153 | `28d9a7767b6eb19363c5a253b54f0b97fce67fc5b8e89b41d5ad8d60343d62e3` |
  | 1507 Defaults + `dungeon_items="anywhere"` | 102 | `bbe445d44e1e78c7d87520824df12e5aa6b901a229ccf6c91706070c2570dc0a` |

- Full gates remain stopped: no lock, runner or watcher has been created.

## In-game boundary

No game started. #6 pickup windows/receive event remain unplayed on rebased code.
The staged Longshot checklist and launcher are below; Claude boot-checks, Kareem
plays. No contents of community seed24 opened or named.


## #6 integration and native evidence

- Castle's four commits follow the rebased #5. The custom actor item stays under
  `[items]`, before main's native-strength helper; main's eight chains, copy-only
  logic and Darunia exception remain intact. Custom flags/flow changes compose
  before main's Darunia source repair, bonus guard, key compiler, progressive
  compiler and bag guards. Fast-start flow edits use main's `gamedata.changes`.
- The appended research is now §49, preserving main's §46–48. Original commit
  messages/trailers remain unchanged (their historical §46 reference is original).
- `src/clawshot/patch/__init__.py:206`: native progressive family names had no
  literal entry in `table.actors`, so `possessive_text` omitted every runtime-selected
  tier of a family. Real-dump packet printed `You were given the Hookshot!`.
  Own adaptation includes all catalog tiers. Failing-before/passing-after native
  regression and 22 existing targeted tests: **23 passed, 3.10 s**.
- Custom placement validation now runs before gift/shop transforms, so unsupported
  non-chest custom items get their explicit refusal rather than an actor-table error.
  Solo calls avoid reading actor dictionaries for an empty possessive actor set.
  Removed the duplicate EventInfo working-set entry, no functional selection change.
- Fresh native fixture: `E:/OOTRemake/work/rounds/r15/dump-castle-cs15a-layered`.
  Copied the supplied r14 layered fixture and added **ActorInfo** and
  **GameActorInfo** to its newest update. All **1,250** selected native resources
  match the read-only real RomFS by SHA256. ZeldaLetter donor was already present.
  The authorized top-of-series dump gate will use this expanded fixture.
  A scratch flat copy was detected as the wrong OOT_DUMP layout before any suite;
  no fixture-only production failure is claimed.
- Actual `make_seed(placements=..., foreign=..., possessive_text=True,
  receive_event=True)` + writer: **106 resources** written/read back, all **16**
  language archives contain the new messages. USen prints Nothing, Castle's Morph
  Ball, your Progressive Wallet, your Hookshot and your Longshot. Both age copies
  of all four chests have the planned actors; the native Hookshot chest has a
  compiled progressive entry. `castle-pickups-v1-manifest.json` records output hashes.
- No new network code/dependency/runtime patch. New actor packs are derived locally
  from the player's donor; neither data nor generated output is in the repository.

## Kareem check: R15-CASTLE-PICKUPS (staged, NOT boot-checked or played)

Launcher: `E:/OOTRemake/work/r15-castle/Play castle pickups.bat`.
Derived from the required Longshot template, CRLF, **empty isolated new-game user**,
no normal-save copies. Only mod root:
`E:/OOTRemake/work/r15-castle/ingame/mods/castle-pickups-v1`.
User: `E:/OOTRemake/work/r15-castle/ingame/user-castle-pickups-v1`.
Dry run passed and selected Longshot **v3.0.0-rc.3** under the launcher; no process
started. `HOS_FS_OVERLAY` is unset; `HOS_MODS` points at exactly one real mod.
Claude must boot-check after Kareem closes his current game, before handing it over.

**Diagnostic external-placement seed, not a beatability-certified solo seed.**
Seed1505 Defaults is the starting recipe; four early rewards deliberately replaced.
No bridge/client runs. Other-player and own-placeholder chests give no native item.
Estimated **8–12 minutes**, including new game, four windows, re-entry and reload.
English acceptance only; other 15 archives are parsed/read-back, not played/localization-reviewed.

1. Claude: confirm the log names this mod alone and shows `mods: <file> <- <path>`
   for KokiriForest child placements, GetPouchContent, ActorInfo/GameActorInfo/
   PouchActorInfo, USen message archive and the custom actor packs. Confirm the
   progressive chest entry/registries and no crash. Mounting alone is not a pass.
2. Kareem: start **New Game**, child Link, no acquired inventory. Walk into Mido's
   house. Only Teleport/clock debug tools permitted; no inventory/flag/age cheats.
   Facing its four chests (physical mapping is the played location catalog):

   | Chest | Hash | Expected window / grant |
   |---|---|---|
   | Far left | 4555665598794293658 | `You found Castle's Morph Ball!`; Letter stand-in model, no native inventory gain |
   | Middle left | 12786193094758345086 | `You found your Hookshot!`; actual progressive first tier, base Hookshot model; child cannot use it |
   | Middle right | 10831981390482426294 | `You found your Progressive Wallet!`; Letter stand-in, **no wallet increase** (own placeholder, external delivery absent) |
   | Far right | 9725242744547055868 | `You found Nothing.`; Letter stand-in, no Zelda's Letter / pouch item gained |

3. Each window should close normally after one box; regain movement, no invisible
   dialog/softlock/crash. Native quest/item-specific windows elsewhere retain their
   dedicated branches; the opt-in custom seed intentionally shortens the default
   shared GetMessage/GetCaption path for all default items (castle's design).
4. Leave/re-enter: all four stay open, no repeat reward. Save and Continue: same.
   Claude reads the test save: Hookshot canonical ownership persists; no Letter or
   Wallet upgrade was awarded by the three placeholders. Do not infer usability
   from the child-greyed Hookshot slot. Continue only this isolated test profile.
5. Record expected/actual text, model, inventory, re-entry and reload, plus loading
   lines. **Unplayed:** receive event invocation/sub-event timing/notice, other
   languages, other custom destinations, all custom/native-item combinations.
   The staged receive-event file is registration/read-back proof only.
