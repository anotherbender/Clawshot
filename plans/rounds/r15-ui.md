# Round 15 Track B — tracker OBS and app free time travel (cs15b)

Started from `1db6e63`; rebased onto `eff7dab`, then onto `d66d35f` (#26) as Claude directed. Final code and both full suites use clean HEAD `33aefb203cca7ef3d6b7cdda1097a5a973ef0ade`. Branch `r15/ui`. Issues #28 and #29. No version bump.

## Scope and choices

- OBS groups stack vertically instead of sharing two wide columns. `columns=1..8` in the URL fragment controls item grids; missing/invalid values use four. Proposed by cs15b under Kareem's request to pick a default: four keeps labelled items in a roughly 337-pixel side overlay rather than stretching across gameplay. Labels default on for discoverability; users can turn them off for denser icons.
- Tracker-tab controls change the copied OBS URL (`columns`, `labels`, existing `icons` and `transparent`). OBS-only settings do not change the tab's six-column dungeon table, 40-pixel icons or item labels.
- `labels=0` hides names/detail text once a real local item icon loads. Tier badges at top-left and count badges at bottom-right preserve values; bottle count, ammo/rupees/magic stock and unknown holdings remain represented. Heart/piece/token counters remain visible. Names/details remain in accessible labels/tooltips. Missing item images keep text fallback; the reviewed compact quest display is described below.
- Dungeon rows retain the dungeon name plus small key, boss key, map and compass. The small-key badge is held/spendable; the number below the icon is found/seed total. Missing holdings remain greyed out; unknowns remain dashed and show `?`. The four native icon IDs already existed in the runtime decoder allowlist. HTTP controller now admits them only with configured dungeon state. No save parsing or collection contract changes.
- Existing free time travel is an experimental World switch, off by default, projected onto `logic.free_time_travel`; no generator field/default, serialized key or gameplay patch changes. The schema reads the world's default. Explicit CLI values (including false) survive unrelated edits byte-for-byte. The established `clears` metadata replaces the old override when the switch is edited. Advanced JSON edits resynchronize the switch; only an edited projected switch is posted as an override edit, avoiding stale duplicate state.

## Sources and safety

Read `AGENTS.md`, README, CONTRIBUTING, roadmap Round 15, architecture, orchestration rules, world format, decisions, game-data sections 22 and 44, tracker/UI/settings docs and UI plan. Dungeon icon file identifiers come from the requested `UI/Tex/Icon/Item_Dungeon_*` names and the existing `tracker/icons.py` inventory. No GPL implementation copied, no NX2navi used.

Kareem's supplied screenshot was viewed in place, not copied. All synthetic saves, runtime-decoded PNGs, scripts and screenshots stay under `E:/OOTRemake/work/r15-ui/` (the first embedded smoke also used the existing private OS icon cache). No game folder writes, game launches, community-seed output reads, merge/push, or version changes. No added generation working-set file; the supplied r14 fixture remains applicable.

## Browser / HTTP smoke evidence

Actual app launched with `LOCALAPPDATA=E:/OOTRemake/work/r15-ui/localappdata uv run --extra ui python -m clawshot.ui --no-open`. Native Browse/Open/Play remain disabled. A synthetic seed and synthetic save were configured over authenticated HTTP; the real read-only `E:/Games/Hookshot/romfs` passed supported-build detection and supplied icons.

Headless Chromium screenshots under `E:/OOTRemake/work/r15-ui/shots/` (never committed):

- Twelve fresh navigations: columns 2, 4, 6 × labels on/off × icons on/off (`obs-cN-labelsN-iconsN.png`), plus `metrics.json`.
- Each asserted the requested column count, expected label visibility, no root horizontal overflow, and 48 decoded dungeon images with icons on / none with icons off. Four-column labelled width 337 px; compact width 280 px (dungeon rows set the minimum); compact item cells 42 px border-box versus 78 px labelled. Local images were eagerly completed for full-page captures.
- `tracker-tab.png`: changing OBS labels/columns leaves the existing six-column table, 40-pixel icons and all tab labels intact; no compact badges in tab. Browse disabled.
- `obs-missing-icon-transparent.png`: deliberately aborted the Hookshot image in the headless browser; its label stayed visible, failed image was removed, transparent body's computed background was transparent. This tests failure fallback, not a fabricated replacement image.
- Synthetic fixture warnings (low saved-Bool count, version mismatch, unknown synthetic locations) remain visible in the tab and labelled OBS captures. The reviewed compact OBS intentionally hides their paragraphs, per Claude's request; its short abnormal-status line still reports waiting/unavailability.
- Boundary smoke: columns 1 and 8 render exactly; 0, 9, fractional 2.5 and nonnumeric input fall back to four. `tracker-tab-items.png` separately captures the unchanged inventory layout.

Initial smoke harness assertion failed because same-document fragment navigation does not rerun page initialization; printed URL/state showed the previous options still active. The capture harness now makes fresh document navigations. An initial tab assertion ran before the poll rendered inventory; observed state had no JS errors, and waiting for the actual populated table resolved the race. Neither required a production workaround.

App smoke (`free-time-travel-setting.png`): actual On output matched `uv run python -m clawshot --logic free_time_travel=true --print-settings` exactly; Off returned to CS1. Importing explicit CLI false and changing another switch off/on retained the exact CLI false string. Typing true in Advanced JSON turned the visible switch On; deleting that key turned it Off/CS1. Checked checkbox, ARIA and chosen-button states, not only the settings string.

Through the actual authenticated HTTP server, all six Door of Time/free-travel combinations were validated: closed with either value and both early modes with free travel accepted; Chest-only song_only/open without free travel returned the existing detailed return-guarantee refusal. The permanent app test additionally runs fill and beatability on each of the four accepted combinations under the serialized full suite.

Integration rejected a lossy projection (explicit false became implicit false after unrelated edits) and a new duplicate-key restriction; preserving raw logic plus the existing clears convention avoids both. The two raw-JSON/switch resynchronization cases required the generic frontend update described above. No new arbitrary validation policy.

Rapid-edit regression: synchronously clicking Free time travel On then another switch reproduced lost travel state (`free=false`, `cheap=false`, raw logic `{}`). Publishing the projected edit into the logic textarea before awaiting HTTP fixes the race: same sequence retained `free=true`, `cheap=false`, raw true; rapid Off then the other switch restored `free=false`, `cheap=true`, CS1. A smoke-harness timeout came from waiting on the preset's eagerly assigned string rather than its completed response; printed `Defaults preset applied` identified the readiness boundary, and the corrected harness waits for that completion first.

## OBS review — Claude, 2026-11-14

Claude accepted the revised four-column compact shot on 2026-11-14: chips, circles and dungeon icon rows correct; no broken words, stray tiers or long paragraphs. Revision committed as `3ea7d6f`.

- Compact songs use fixed, unbroken `ZL`, `Ep`, `Sa`, `Su`, `SoT`, `SoS`, `Min`, `Bol`, `Ser`, `Req`, `Noc`, `Pre`, `Scr` CSS chips; stones use `Kok`, `Gor`, `Zor`. Six medallions are plain colored circles (forest green, fire red, water blue, shadow purple, spirit orange, light yellow). Colors are semantic tokens in the existing palette root, not game art; no font or image assets added.
- All 22 cells retain full title/ARIA names, grey-out for missing holdings, and visible `?` badges for unknowns. Chip bounds are at most 32×32 inside the normal compact cell; circles are 24×24. Single-tier items, songs and rewards never show a tier in either surface; 60 such entries checked in the app.
- Compact OBS hides the heading paragraph, warning paragraphs and Checks by area; following normally has no status line. Actual empty synthetic save-folder smoke showed one short “Waiting for a saved game” line and 22 unknown quest badges. Tab status/warnings/areas, six-column dungeon table and 40-pixel icons remain unchanged.
- Re-shot all twelve matrix files and `metrics.json` at their original paths, plus both tab captures, missing-icon transparent fallback and `obs-waiting-compact.png`. Every matrix case checked no horizontal overflow, exact columns, 22 compact quest cells, no single-tier tier text, no wrapped/overflowing chip labels, six distinct circle colors, full accessible names, and the intended clutter visibility. Reviewed app launched with both APPDATA and LOCALAPPDATA under the track scratch folder and `--no-open`.
- Optional bounded native-texture lookup: `UI/Tex` has only `Icon` and `IconSh`; filename globs for Quest, Medal, Melody and Spiritual returned no matches. No native quest atlas investigation or extraction was attempted; CSS chips do not depend on one. No working-set addition.

Current compact native-icon matrix geometry (CSS pixels):

| Columns | Width | Height |
|---|---:|---:|
| 4 | 280 | 1834 |
| 6 | 283 | 1588 |

## Split browser sources — Kareem via Claude, 2026-11-14

- Added `sections=items,quest,dungeons` filtering. Quest owns collection counts, songs, stones and medallions; items owns inventory/equipment. Missing, empty or any unknown member falls back to all. Duplicate/reordered selections do not reorder the original groups. Partial views omit area checks. No server/save/seed contract changes.
- Tracker-tab OBS items/quest/dungeons checkboxes update only the copied URL. A single click clearing the last checked group restores all three. Actual app smoke retained all six tab groups and the six-column table while the copied URL selected only dungeons or items/quest.
- Both independent headless browser sources were opened simultaneously from the actual copied URLs (including encoded comma), followed synthetic seed 73 and showed their distinct groups without changing each other. `shots/two-source-live.json` records the result.
- Added `tests/test_tracker_options.py`: two Node-backed tests exercise the actual shipped JS parser through missing/empty/unknown/mixed-invalid and valid/encoded/reordered/duplicate selections. **2 passed in 0.48s**, with tasklist selecting 3 workers (neither game running). Node is optional for these frontend tests, not an app/runtime/build dependency.
- First test-harness attempt passed multiline code through Volta's Windows `node -e` shim and got no JSON output. Printed executable/version/argv/stdout/stderr isolated quoting failure (`node: -e requires an argument` for a minimal multiline diagnostic). The harness now executes a temporary `.cjs` file; production parsing needed no workaround.
- HTTP/browser scenarios checked single groups, items/quest, missing/empty/unknown/mixed-invalid fallback, and preserved order. Requested files: `shots/obs-c4-labels0-icons1-sections-dungeons.png` and `shots/obs-c4-labels0-icons1-sections-items-quest.png`; new control capture `shots/tracker-tab-sections.png`. `docs/tracker.md` contains the two-source recipe.
- Initial burst capture received two TCP `ERR_CONNECTION_REFUSED` image requests (Bomb Bag and Bullet Bag), while the server's icon-provider warning list stayed empty; later captures showed the source files available. No production retry/server workaround was added. Final image-complete captures bound the capture harness to two concurrent real icon requests, retain real HTTP/native art, and record that condition in `shots/split-source-metrics.json`; original fallback metrics remain in `shots/sections-metrics.json`.

Four-column compact sources, local icons on (CSS pixels; both fit 1080 high without cropping):

| Sections | Width | Height |
|---|---:|---:|
| dungeons | 280 | 845 |
| items,quest | 280 | 1029 |

The earlier queued runner was cancelled before this edit, as Claude directed. The sections change was committed as `b0df7b9` with a clean tree before re-queueing. That waiting runner was subsequently cancelled before the requested rebase onto `d66d35f`; no obsolete-head result is claimed. The replacement runner pins the full expected HEAD, refuses changes before/after every stage, and records HEAD/clean status in `gate-results.json`.

## Gates and handoff

Final code is ready for review/merge: format, lint, full synthetic and real-dump suites passed on the same clean rebased HEAD, detailed below. Only this round evidence changed afterward. No new in-game check claimed: tracker reads are unchanged, and app exposure uses the existing free-time-travel patch. Prior played behavior is documented in settings/roadmap; this round does not certify unplayed early-door returns.

- Targeted `CLAWSHOT_WORKERS=3 uv run pytest tests/test_tracker_http.py tests/test_tracker_icons.py -m "not dump" -q`: **75 passed in 3.35s**. Synthetic HTTP coverage includes all four distinct decoded textures, absent/current-state icon authorization, wrong token/foreign Origin refusal, no source/seed writes, true/false/unknown flags, separate held/found counts, replaced-save polling and permanent OBS spoiler stripping.
- Final queue (Claude): rebase onto `d66d35f`, B synthetic first, then B dump immediately once Kareem closed Longshot. The runner checks unfiltered CSV tasklist at every stage start and selects one worker while either game executable runs, otherwise three. No full-suite supervisor deadline. The synthetic reservation error and corrected exclusive dump acquisition are disclosed below.
- Initial global format check: 369 files formatted. Lint printed I001 because the new tracker constant had two blank lines after imports; reduced to one. The final gate reruns both checks after that printed-cause correction.
- Process-check correction: the targeted command's two `tasklist /FI` image filters were combined as AND, so that prefix alone cannot prove both games absent. The earlier unfiltered list showed neither; a process could still have started between checks. Subsequent independent checks found Longshot, and every full gate uses a fresh unfiltered CSV parse matching either exact executable, choosing one worker while present.
- Pre-review final gates on `eff7dab` plus `ca8ecfa`/`4bf3432`: `uv run ruff format --check` **370 files already formatted**; `uv run ruff check` **all checks passed**; `uv run pytest` **2354 passed, 187 skipped in 1433.40s**. Every stage saw `longshot.exe` and used `CLAWSHOT_WORKERS=1`. Logs: `work/r15-ui/gate-{format,lint,synthetic}.log`; results in `gate-results.json`. The lock was released before D acquired it. Review rerun uses separate `gate-reviewed-*` logs so this evidence is retained.

### Final rebased gates

- Tested code HEAD: `33aefb203cca7ef3d6b7cdda1097a5a973ef0ade`, based on `d66d35f`. Snapshot guard confirmed exact HEAD and clean tree before and after every stage. No runtime/source edits followed these runs.
- `uv run ruff format --check`: **372 files already formatted**. `uv run ruff check`: **all checks passed**.
- `uv run pytest`: **2415 passed, 188 skipped in 1797.25s**. Every stage started with `longshot.exe` present and `CLAWSHOT_WORKERS=1`. Logs: `work/r15-ui/gate-reviewed-{format,lint,synthetic}.log`.
- Reservation error, cs15b: at 16:47 I removed an empty `gate.lock` I had not created, incorrectly treating it as released. It was A's freshly created reservation, so B's synthetic overlapped A's suite. Claude explicitly accepted the unchanged-code results and directed no rerun. This was not an exclusively serialized synthetic run. Never remove another agent's lock, even empty; ask on the thread instead.
- Dump waited for A's explicit 17:24 cancellation/release; A removed its own directory. B then acquired its own reservation, confirmed by `owner.txt`, without removing another lock.
- `OOT_ROMFS=E:/Games/Hookshot/romfs OOT_NUP="E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup" OOT_DUMP=E:/OOTRemake/work/rounds/r14/dump-progressive-cs14d-1e6cde0 uv run --extra ui pytest -m dump`: **186 passed, 2417 deselected in 7522.70s**. Stage-start tasklist found neither game; `CLAWSHOT_WORKERS=3`. Log: `work/r15-ui/gate-dump.log`; exact arguments, worker/process snapshots, HEAD and clean status are in `work/r15-ui/gate-results.json`.
- Dump exited 0 and its own reservation was released at 19:29. No working-set additions or new fixture needed. Headless browser/HTTP evidence and requested split-source screenshots are above. No merge or push performed; B merges first in Claude's queue, then castle rebases onto B.
