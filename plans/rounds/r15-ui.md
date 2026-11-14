# Round 15 Track B — tracker OBS and app free time travel (cs15b)

Baseline: `1db6e63`, branch `r15/ui`. Issues #28 and #29. No version bump.

## Scope and choices

- OBS groups stack vertically instead of sharing two wide columns. `columns=1..8` in the URL fragment controls item grids; missing/invalid values use four. Proposed by cs15b under Kareem's request to pick a default: four keeps labelled items in a roughly 337-pixel side overlay rather than stretching across gameplay. Labels default on for discoverability; users can turn them off for denser icons.
- Tracker-tab controls change the copied OBS URL (`columns`, `labels`, existing `icons` and `transparent`). OBS-only settings do not change the tab's six-column dungeon table, 40-pixel icons or item labels.
- `labels=0` hides names/detail text only once a real local icon loads. Tier badges at top-left and count badges at bottom-right preserve values; bottle count, ammo/rupees/magic stock and unknown holdings remain represented. Heart/piece/token counters remain visible. Names/details remain in accessible labels/tooltips. Songs/rewards without local icons retain text, as does any failed image.
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
- Synthetic fixture warnings remain visible in screenshots: low saved-Bool count, version mismatch and unknown synthetic locations. These are intentional evidence limits, not hidden or patched out.
- Boundary smoke: columns 1 and 8 render exactly; 0, 9, fractional 2.5 and nonnumeric input fall back to four. `tracker-tab-items.png` separately captures the unchanged inventory layout.

Initial smoke harness assertion failed because same-document fragment navigation does not rerun page initialization; printed URL/state showed the previous options still active. The capture harness now makes fresh document navigations. An initial tab assertion ran before the poll rendered inventory; observed state had no JS errors, and waiting for the actual populated table resolved the race. Neither required a production workaround.

App smoke (`free-time-travel-setting.png`): actual On output matched `uv run python -m clawshot --logic free_time_travel=true --print-settings` exactly; Off returned to CS1. Importing explicit CLI false and changing another switch off/on retained the exact CLI false string. Typing true in Advanced JSON turned the visible switch On; deleting that key turned it Off/CS1. Checked checkbox, ARIA and chosen-button states, not only the settings string.

Through the actual authenticated HTTP server, all six Door of Time/free-travel combinations were validated: closed with either value and both early modes with free travel accepted; Chest-only song_only/open without free travel returned the existing detailed return-guarantee refusal. The permanent app test additionally runs fill and beatability on each of the four accepted combinations under the serialized full suite.

Integration rejected a lossy projection (explicit false became implicit false after unrelated edits) and a new duplicate-key restriction; preserving raw logic plus the existing clears convention avoids both. The two raw-JSON/switch resynchronization cases required the generic frontend update described above. No new arbitrary validation policy.

## Gates and handoff

Serialized full suites pending. No in-game check required: tracker reads are unchanged, and app exposure uses the existing free-time-travel patch. Prior played behavior is documented in settings/roadmap; this round does not claim new in-game evidence or certify unplayed early-door returns.

- Targeted `CLAWSHOT_WORKERS=3 uv run pytest tests/test_tracker_http.py tests/test_tracker_icons.py -m "not dump" -q`: **75 passed in 3.35s**. Synthetic HTTP coverage includes all four distinct decoded textures, absent/current-state icon authorization, wrong token/foreign Origin refusal, no source/seed writes, true/false/unknown flags, separate held/found counts, replaced-save polling and permanent OBS spoiler stripping.
- Claude's queue: cs15d synthetic first, cs15b synthetic next; dump gates after both synthetics, cs15d first. Longshot appeared in a subsequent independent tasklist check; future stages use one worker while present. The runner checks CSV tasklist at each stage start and reserves/releases `gate.lock` atomically. No full-suite supervisor deadline.
- Initial global format check: 369 files formatted. Lint printed I001 because the new tracker constant had two blank lines after imports; reduced to one. The final gate reruns both checks after that printed-cause correction.
