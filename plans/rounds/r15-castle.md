# Round 15 — castle PRs (cs15a)

Base: `1db6e63` (0.2.1). Owner: cs15a, `openai-codex/gpt-6.1-sol`.
Read AGENTS, README, CONTRIBUTING, architecture, round rules, world format,
decisions and native story/progressive/quest-step evidence (§46–48).
Read all four PR descriptions, discussion comments and inline-review endpoints
before changing code (inline endpoints were empty).

## Scope and provenance

Rebase order: #5, #4, #20, #6. Stacks: `r15/castle-5` →
`r15/castle-6`, and `r15/castle-4` → `r15/castle-20`.
Castle's author, messages and trailers stay intact. New-main adaptations are
separate assisted commits. No push, merge, GitHub comment/review or game launch.
No version bump. Scratch code, outputs and evidence: `E:/OOTRemake/work/r15-castle/`.

## Decisions and questions

- cs15a: #5's moved preparation must carry main's `prepare_spec` and
  `restrict_settings`; this is a move of the current functions, not a return
  to the old fixed-item world. Keep main's return-guarantee check in solo fill.
- **Maintainer confirmation requested (castle's original #5 question): external
  placements deliberately skip the local beatability/return search. The external
  placer must prove its whole multiworld; this is not a verified solo seed API.**
  No new CLI/slot protocol/network bridge is introduced.
- Claude, current conversation: a handful of baseline comparisons need no gate
  lock. Full gates take `E:/OOTRemake/work/rounds/r15/gate.lock` atomically;
  queue arbitration only if agents contend.

## Verification (in progress)

- #5 original tests after rebase: `uv run pytest tests/test_from_placements.py -q`
  → 3 passed, 0.81 s.
- Added integration boundary: external copies are chest-only and unshuffled
  Darunia remains the native Bracelet. Targeted suite: 4 passed, 2.22 s.
  First assertion mistakenly shuffled NPC Darunia then expected him unchanged;
  printed his prepared location (eligible NPC, native Bracelet), corrected the
  check to use Chest-only settings, and reran once. Not a production failure.
- Main source archived outside the worktree for actual before/after generation;
  seed 1505 Defaults and seed 1506 Chest/Shop/Gift. Compare every output file's
  relative path and SHA-256, including spoiler and play note, not only placements.

## In-game boundary

No game was started by cs15a. #6 pickup windows and receive event remain unplayed
on this rebased code until Kareem performs the staged Longshot checklist.
