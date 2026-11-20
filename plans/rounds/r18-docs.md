# Round 18 — Track H: documentation (cs18h)

Agent `cs18h`, model `openai-codex/gpt-6.1-sol`; branch `r18/docs`, base main
`2ba2f9a5076dbe95a8233a7e01f9bb77782d980b`. Documentation only: **run NO tests or gates**.
No gate lock, generation, game start, version bump, merge or push. No seeds or saves opened;
no writes to game/runtime installations or the installed Hermes skill.

## Roadmap split

Read **the roadmap index plus your round's file**: [index](../00-roadmap.md), the linked
`r<N>-overview.md`, and your own `r<N>-<track>.md`. Claude owns round outcomes; tracks own their records.

- Original roadmap: 1,475 lines. Full historical round material moved verbatim into previously absent
  `r1-overview.md` through `r11-overview.md`, then `r14-overview.md` through `r16-overview.md`.
- Milestones and the standing Settings backlog remain in the index. The backlog was nested after Round 8;
  its text is retained verbatim and its heading promoted from h3 to h2. Round 8's history stops before it.
- Existing track filenames were inventoried first; none was overwritten. One historical citation in
  `r4-logic-child.md` now points through the index to Round 3. Other track evidence is unchanged.
- The original roadmap had no sections for rounds 12, 13 or 17, and no consolidated Round 11 outcome.
  New navigation summaries for 12/13 cite existing track files, not an invented merge sequence. Round 17
  additionally records the supplied intake's played failures; earlier built-only handoffs stay historical.
- One table row per round, including Round 18 in progress. No Round 18 outcome is asserted here.
- Updated AGENTS, README, CONTRIBUTING, plans index, orchestration read/spec lists and public logic/settings
  references to the index plus round files. Literal historical paths in moved briefs remain verbatim;
  the index explains their original `plans/` context. Source-code comments still naming the roadmap are
  index citations, not direct links to deleted anchors; no product source was changed.

Proposed layout/edge-case choices above: cs18h, implementing Kareem/Claude's Track H request.
No product behavior was decided.

## Round 18 evidence boundary

Read Claude's external `_intake.txt` plus the supplied prompt. Main is 0.2.2 plus Round 17;
Kareem's 2026-11-18 play exposed the failed sword guard, the no-ocarina lesson softlock,
Dampé's one-way trap, broad-settings `all_anywhere` exhaustion and off-area map display failure.
This track neither reproduces nor certifies a fix for them.

The prompt's two lessons apply to behavior tracks: a behavior change stays **built, not played** until
Kareem plays a staged check, with the same packet built from main as its bug-reproducing control;
fill/destination/location/logic changes sweep at least 200 broad-recipe seeds plus 50 Defaults and
50 Recommended, zero exhausted, under the gate lock before READY. This docs-only track runs neither.
No action is required from Kareem overnight. Handoff deadline: 2026-11-19 08:00.

## Claude skill: staging only

Source (read-only): `C:/Users/hi/AppData/Local/hermes/skills/software-development/game-recomp-modding/`.
Proposal: `E:/OOTRemake/work/r18-docs/skill-split/`, same layout including all references, templates and scripts.

- Standing rules, build troubleshooting, contribution procedure and mods/randomizer principles stay in
  `SKILL.md`; a linked topic index routes detailed procedures and facts to references.
- Extended existing `hookshot.md`, `randomizer-design.md`, `clawshot-ingame-checks.md`,
  `clawshot-release-checklist.md` and `clawshot-contributor-prs.md` with verbatim blocks.
- New `references/clawshot-rounds.md` holds the former inline round/orchestration material.
- Existing Lantern/Bloodborne, clean-room, save-format and runtime reference content is retained, not rewritten.
  Dated hypotheses and stale instructions stay verbatim for Claude's review; this is a structural proposal,
  not a factual refresh or installation. Added headings identify each original source-line span.
- Claude reviews and installs. Nothing from the skill staging area is committed to Clawshot.

## Preservation proof

Frozen inputs and standalone proof script live under `E:/OOTRemake/work/r18-docs/`:

- `before/00-roadmap.md`, `roadmap-manifest.json` and `roadmap-proof.json`.
- `before/game-recomp-modding/`, `skill-manifest.json` and `skill-proof.json`.
- `prove_preservation.py`: standard-library text proof only, no Clawshot imports, tests or gates.

The script checks exact ordered source spans and multisets of **all non-heading lines, including blank
and duplicate lines**. Newly authored index/scaffolding lines are explicitly excluded; original bodies
are not normalized except CRLF/LF. It also checks index links, copied assets and hashes of the installed
skill against the frozen source. This is preservation evidence, not in-game or generator acceptance.

Command: `python E:/OOTRemake/work/r18-docs/prove_preservation.py E:/OOTRemake/clawshot-r18/docs`.
Observed proof: **PASS**. Roadmap 1,475 lines becomes a 68-line index with 1,438 lines relocated;
the moved multiset contains 1,349 non-heading lines, and all 1,383 original non-heading lines survive.
Skill: 862 lines relocated (860 non-heading); all 3,112 original skill/reference non-heading lines survive.
`SKILL.md` shrinks from 100,991 bytes / 1,050 lines to **17,603 bytes / 213 lines**, below 40,000 bytes.
Zero missing or extra original lines; index links and copied scripts/templates pass; installed source hashes unchanged.

First proof attempt printed a staged reference blank-line mismatch: append inserted a blank at the first
new heading and omitted the source block's final blank. Printed the exact unified diff, moved that blank
back with an anchored edit, then reran once; both proofs passed. No source prose was changed.
No tests or gates were run.

## Handoff

Repository documentation is committed on this branch; READY (docs) posts the resulting head and both
external proof paths to `cs-r18`. Remaining: Claude reviews/merges item 1, reviews/installs item 2,
and writes the overall Round 18 outcome. No play check belongs to this documentation track.

## Release-documentation follow-up — 0.2.3

Claude's new request, 2026-11-19: branch `r18/docs-release` from main
`d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`. The original no-tests instruction above belongs
to the preservation job; this follow-up explicitly authorizes focused help/docs tests, not full gates.

Updated README, settings/logic guides and app setting help from Claude's supplied Longshot rc.7
played results: child sword return, adult Mirror Shield scrub, forty-token gift, map/compass display,
Well recovery/once-only pickup, one Fortress rescue/drop, first-pull reward, medallion bridge,
owned-three-Stones Door, Dampé refusal, partial Talon skip, castle owl, Time-after-Fairy and Mido.
The generator's `data/settings.toml` has no help fields; added evidence comments only, leaving every
parsed default, destination policy and source string unchanged.

Limits retained: Fortress stays experimental (all four rescues/card/Training Ground unplayed);
Shadow floor remains vanilla; the physical no-instrument lesson freeze remains, with no bypass shipped.
Adult Sun's Song worked with Fairy in the control, not proof of every adult song or lesson.
Zelda, Impa, Field/summit/Lake owls and two-Stone refusal stay pending until Claude reports results.
No version bump, game, generation, sweep, gate lock, full gate, merge or push.

Drafted `r18-overview.md` for Claude's review and linked it from the roadmap. It identifies linear-history
implementation/landing SHAs from `git log 2ba2f9a..d9deb65`, distinguishes played evidence from receipts,
and lists Round 19 deferrals without deciding new product scope. Earlier track handoff prose remains
historical, not rewritten into a false played pass.

Focused command:

```sh
CLAWSHOT_WORKERS=1 uv run pytest tests/test_app_schema.py \
  tests/test_app.py::test_schema_is_exhaustive_and_replay_preserves_values tests/test_settings.py -q --tb=short
```

**45 passed in 58.99 s.** No stale help-text assertion failed, so no expectation changes or new
wording-pinning tests were needed.

Final standalone smoke used the real local UI in **Chrome headless**, an empty external seed library
and in-memory preferences. Six help rows rendered their actual schema text: dungeon items, Fortress
keys, rewards, bridge, free time travel and story dialogue. Screenshots of Fortress and reward help
were inspected; both panels show the partial acceptance and pending limits without clipping.
No DOM/app-state edits, game, generation or personal-seed access. Server/browser closed normally.
It also checked **84 local document links/anchors**, all passing, including the outcome's track links.
Receipt: `E:/OOTRemake/work/r18-docs/release-proof/result.json`; screenshots alongside.
The throwaway `release_help_smoke.py` was removed after proof. No permanent tests or product code added.
