# Round 22, track logic (cs22d)

Branch `r22/logic`, base `2091387` (0.2.7 plus round records). Work/research and staged packets:
`E:/OOTRemake/work/r22-logic/`. No game or boot check run by this agent. Runtime for every new checklist:
**Longshot 3.2.0**, stable `builds/stable/v3.2.0/bin/longshot.exe`.

## Scope and acceptance

1. Audit every Dodongo's Cavern explosives rule against adult-accessible Bomb Flowers and its target's damage/material
   and trigger chain. Loosen only with an end-to-end native chain or played check (rule h). Include round 21's two
   Hammer-on-growing-flower candidates. Stage unresolved routes, preferring a natural adult pre-Bomb-Bag backup.
2. Mirror the upstream Zora's River wall predicate downstream. Tightening; no new play needed.
3. Stage an Ice Cavern compass from Sheik's lesson, with Gift and songs anywhere. Keep the round-21 chest hold until
   Kareem plays it; any loosening is a separate final commit after the pass.
4. Before READY: rule-2 sweep (200 broad, 50 Defaults, 50 Recommended; paired placement/sphere digests, plus binding
   cohort if standard placements are unchanged), then ordered exact-head gate. Results pending.

## Played facts, not new certifications

- Kareem, Longshot 3.2.0, Clawshot 0.2.6, 2026-11-24: entered Dodongo's Cavern as adult, progressed with Goron's
  Bracelet and Bomb Flowers until finding the Bomb Bag, then finished. The tracker credited none before the bag.
  This does not itemize every chest, side route or Hammer-chain puzzle.
- Kareem, Longshot 3.0.0, 2026-11-23: a Hammer hit explodes a Bomb Flower where it grows. It does not establish
  carrying one, reaching the staircase's flower, or opening either candidate chain (`r21-hammer.md:227-243`).
- Kareem, Longshot 3.2.0, 0.2.6: coming downstream from Domain/Lost Woods, met the invisible wall and bomb rocks.
  He could return through Lost Woods/Field. No additional play requested for this tightening.

## Zora's River downstream

`remake/child_zora_river.toml` adds `Zora River -> ZR Front`, `was = "True"`, matching upstream:
`can_blast_or_smash or 'Zora River Domain Arrival'`. Generated `zora_river.toml` stays untouched.

Evidence: `03-game-data.md` section 48; native `ZoraRiver_Common_08f0` nodes 1/3/4/10/11/12/13 create their walls iff
NOT (`Zorariver_BrokenRock_Broken` OR Water == Step03 OR Water > Step03). Both entrance rocks' deaths set that Bool.
The common geometry is not directional. Existing source event models the real river-to-Domain transition, not mere
Domain reachability or a former reward. Existing paired adult check showed Ready/false blocked, Step03/false open,
including reload. This change mirrors that condition and Kareem's downstream failure; no new gameplay patch.

Regression coverage extends `tests/test_story_steps_river.py`: start inside the river at each age, reject no tool,
Bag without strength and child Hammer; accept age-usable bomb kit, adult Hammer, or saved Domain-arrival event.
Existing upstream, Lost Woods and reverse Domain tests retained. Focused command:
`CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -n 2 tests/test_story_steps_river.py`:
**24 passed in 5.96 s**. No game running at stage start.

## Ice Cavern hold and staging boundary

Round 21's `fill.CHEST_HELD_DUNGEON_TYPES` rejects generic non-chest dungeon grants, including Sheik's lesson.
The generic compass actor is not a source-bound `DungeonInfo.<target>.IsGetCompass` write. Test the actual gift,
not a chest masquerading as a lesson, with the chest's own grant separately controlled. A successful compass check
would justify only the admitted source/type(s), not keys or unrelated gifts. Shared-file notice posted before any
`fill.py` change; no permanent hold change made yet.

Fact source read before save/game-file tracing: sloperinaGZ `docs/FINDINGS.md`, local factual reference
`work/refs/sloperina-FINDINGS.md`, sections 1 (GameData, Save files, Useful name patterns) and 2 (Game files).
Facts only; no GPL code copied into the repository. Natural-save census pending.

## Decisions and open work

Proposed by cs22d: keep uncertain chains conservative; stage them rather than infer physical flower reach from a
nearby coordinate. No settings, runtime changes or new game resource planned. No version bump.

Audit, packet manifests/checklists, exact commands, gate and sweep numbers will be recorded here as completed.
