# Round 18 — outcome draft for Claude's review

2026-11-18–19. Started from main `2ba2f9a` (0.2.2 plus Round 17); release-documentation
baseline is main `d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`. Target release: **0.2.3**;
this draft does not bump the version or claim publication. Claude reviews the outcome and release decision.

Read the [roadmap index](../00-roadmap.md) plus this file and the relevant track record.
Kareem's play reports are the acceptance evidence; passing native-data tests alone is not a game pass.

## What landed

SHAs below are from `git log 2ba2f9a..d9deb65`. The history is linear: landing heads identify the
reviewed stack, not invented merge commits. Staging/receipt commits can follow implementation commits.

| Track | Landed work | Main-history commits / landing heads | Record |
|---|---|---|---|
| A — logic | Require real escape before Dampé/Colossus entry; require an instrument for native song lessons; retain conservative one-way audit questions. | `b349fca`, `1e0ce14`; A+D stack `e241a85` | [Logic](r18-logic.md) |
| B — equipment | Repair child sword return and the scrub shield wait without matching-age placement restrictions or forced auto-equip. | `b9d88ed`, audit `06b4e10` | [Equipment](r18-equipment.md) |
| C — dungeon items | Place priority maps/compasses before ordinary shop filler; diagnose the debug-adult map UI prerequisite without inventing grant flags. | `ab6b66d`, receipt `3a7d9e3` | [Dungeon items](r18-dungeon-items.md) |
| D — chests/gifts | Admit ten canonical checks (178/184 ordinary chests); finish attribution; keep expert gallery rupees repeatable; enable the forty-token gift. | `ce8d1e3`, `688a313`, `c7db527`; landing `d3ce136` | [Chests and gifts](r18-chests.md) |
| E — rewards/bridge | Nine-slot dungeon reward shuffle, owned-Stones closed Door and unique-owned-reward bridge modes; stage rewards before held progression. | `743c71b`, `47c625b`, `3bca02d`; landing `2d9ddef` | [Rewards](r18-rewards.md) |
| F — key families | Well floor replacement, separate Fortress jail-key option and tracker support; repair native jail collection completion; hold Shadow floor vanilla. | `fea6d72`, `22cb420`, `91ec1b6`, `d64f048`; F+G landing `8fadebf` | [Keys](r18-keys.md) |
| G — story | Dampé race refusal without a tool and experimental owl skips. Unsafe no-instrument lesson bypasses were removed after failed play. Talon/Zelda/Impa dialogue skipping is withdrawn for 0.2.3 by cs18g (hidden/refused), not a shipping option. | Original work `de36c43`, lesson withdrawal `623c434`; F+G landing `8fadebf`; dialogue withdrawal follow-up owned by cs18g, SHA not yet supplied | [Story](r18-story.md) |
| H — documentation | Roadmap index plus verbatim round histories; staged Claude skill split outside installed skills. Release docs now align with the reported played scope. | `0582338`; this release-docs branch follows `d9deb65` | [Documentation](r18-docs.md) |
| A+B follow-ups | Preserve Time selection after Fairy receipt; keep Mido at his equipment gate after early Zelda; include the raw schedule in packed-input caches. | `3dc13fb`, `e81180e`, fixture `fc0a03d`; landing `d9deb65` | [Ocarina](r18-equipment.md#issue34-implementation--r18ocarina), [Mido](r18-mido.md) |

No runtime fork, game files, version bump, new retry limit or token weighting belongs to this documentation work.
Defaults retain own-dungeon items, Fortress keys off, reward shuffle off and the vanilla bridge.

## Played on Longshot rc.7 — Kareem, 2026-11-19

The following is Claude's supplied release intake, supplemented only by the corresponding track records.
It is not agent-run gameplay and is not a claim that the later Longshot stable 3.0.0 was played.

| Change | Observed result | Coverage limit |
|---|---|---|
| Child sword return | Returning to child no longer equips an unowned Kokiri Sword. | The Round 17 guard failed in a real seed; this acceptance belongs to the replacement. |
| Mirror Shield scrub (#33) | The adult purchase finishes instead of leaving Link in the get-item pose. | No blanket certification of every shield/age/delivery combination. |
| Forty-token reward (#11) | The shuffled reward check passed. | Not every House threshold or replacement item. |
| Dungeon map/compass | The display check passed. | The earlier debug-adult UI failure does not justify fake quest/history writes; not every source/target pair was played. |
| Well floor key | Left uncollected, recovered, collected once; absent after leaving/returning and Continue. | Shadow floor is not admitted. |
| Fortress jail keys | After the Valley carpenter boss's Yes, the guard appears; one rescue and the repaired 20-rupee drop passed, once-only after return/Continue. | All four rescues, captain/card and Training Ground **UNPLAYED** with the option; keep it experimental. |
| Dungeon rewards | First sword pull gives the shuffled reward. | Other boss rewards and a full shuffled playthrough remain unplayed. |
| Medallion bridge | Stays closed below the configured count and opens at the count. | Stones/combined-count modes and late Light Arrow/trial order not newly played. |
| Owned-Stones Door | Opens with all three Stones while Dodongo/Jabu are unfinished; stays open; no escape/moat scene. With only Emerald+Ruby, stays closed with no opening scene; saved state confirms both Stones and closed Door. | Not an escape/moat completion check or a full shuffled playthrough. |
| Dampé, no Hookshot | Refuses the race; fades back in front of Dampé, normal control, existing warp back up usable. | Not a surface return; do not describe it as one. |
| Castle owl | No speech; short stop/fly-away retained. | Experimental; not blanket acceptance of every owl scene. |
| Field owls (Kakariko/Lake approach) | No speech; short look-and-fly-away works. | Experimental; only these encounters played. |
| Summit/Lake travel owls | Short offer; flight works. | Experimental; not blanket acceptance of every owl route. |
| Ocarina (#34) | Fairy after Time keeps Time selected as child/adult; adult Sun's Song works and Time persists after Continue. Control's adult Sun's Song also works with Fairy. | Cosmetic downgrade **for Sun's Song** only; no broader adult-song or lesson-safety inference. |
| Mido (#35) | Sword-only refusal, shield clears the passage, tree mouth open; reload retains the clear and normal late Mido position. | The fixture's declared castle-step edit is in the track record; not a complete early-Zelda playthrough. |

## Withdrawn or still unplayed

- **Talon/Zelda/Impa dialogue skipping is withdrawn for 0.2.3.** cs18g owns hiding the option and
  refusing attempts to enable it. Talon's earlier partial pass is historical, not a shipping feature.
- Later Woods/Zora owl additions have no new played acceptance. The played Field/summit/Lake
  skips above still remain default-off experimental options.

Claude's follow-up supersedes the initial pending list: two-Stone refusal and the named owl checks passed.
A staged launcher or dry run is not a played pass; no wider acceptance follows from these results.

## Engineering evidence already recorded by the owning tracks

This is a receipt index, not a claim that Track H reran those gates.

- C: **500 broad + 50 Defaults + 50 Recommended**, all with `all_anywhere`, zero exhausted;
  exact-head format/lint, 3322 synthetic passes and 375 dump passes ([receipt](r18-dungeon-items.md#ready-merge-frozen-verification-head)).
- A+D: **200 broad + 50 Defaults + 50 Recommended**, zero exhausted; stack `e241a85`
  recorded format/lint, 3467 synthetic passes and 375 dump passes ([receipt](r18-chests.md#frozen-ad-acceptance)).
- Issue #11: separate **300/300**, zero exhausted ([receipt](r18-chests.md#play-held-acceptance-receipt));
  its old play-held wording is historical, superseded by Claude's current played-pass intake and its presence in main.
- F+G: **300/300**, zero exhausted on `623c434`; corrected landing `8fadebf` recorded
  format/lint, 3606 synthetic passes and 465 dump passes. No placement change in the accepted contract correction.
- E on F+G: final counting **300/300**, zero exhausted on `3a33864`; format/lint,
  3768 synthetic passes (489 skipped) and 486 dump passes; landing `2d9ddef` ([receipt](r18-rewards.md#ready--final-counting-and-one-full-gate-passed)).
- Final ocarina/Mido stack: Claude's thread handoff records exact head `d9deb65`, format 481 files,
  lint pass, **3806 synthetic passed / 499 skipped**, **496 dump passed**, 24 warnings in each pytest stage;
  both used `-n8` / internal workers4 after measuring Defender load. Full cache matrix covers 1293 inputs.
  Earlier failed gate receipts remain in `work/r18-issue34/combined-gate-*/`; the accepted final receipt is
  `E:/OOTRemake/work/r18-issue34/combined-gate-d9deb65cedf8/`.
- H's original preservation scripts proved all moved roadmap/skill lines survive; installed skill unchanged.
  Paths and exact counts are in [Track H](r18-docs.md#preservation-proof). The release-docs follow-up records its own focused checks there.

## Deferrals and carry-forward for Round 19

Already deferred by Claude, rather than invented new release scope:

- **Physical song-lesson safety.** A native lesson without a usable instrument can still freeze. The attempted
  bypass failed Minuet and was completely removed, child/Impa included. Keep the logic instrument guards;
  they do not prevent a player walking into an automatic scene out of logic.
- **Saria bridge farewell skip.** The unrelated Saria speech patch was removed; the actual bridge timeline/gift
  needs its own safe design and played check ([story record](r18-story.md#check12-played-decision--supersedes-the-earlier-play-hold)).
- **Talon/Zelda/Impa dialogue skip.** Withdrawn for 0.2.3 (hidden and refused by cs18g).
  Reconsider only with a safe design and played acceptance; the earlier Talon partial pass does not ship.
- **Shadow floor key.** Keep vanilla until a natural pre-room save permits the required recovery/once-only check.
- **Held progression ordering.** Measure the proposed most-constrained-first ordering within shared progression,
  using preserved matched cohorts. Attribution found gift holds, not the three chest admissions, increased
  failures; do not add token weighting, broaden unsafe grants or increase retries ([attribution](r18-chests.md#generation-attribution)).
- **Whole-world return debt.** The residual one-way ledger needs real route evidence; missing graph returns alone
  are not proven physical traps ([questions](r18-logic.md#unresolved-region-questions)).
- **Master Sword shuffle stays design-only.** No setting or implementation ships; ownership, forced equipment,
  finale admission and the explicit free-travel/return-guarantee product choice remain to resolve
  ([design](r18-master-sword-design.md)).

Additional coverage to schedule, not silently accepted: all-four Fortress rescues/card/Training Ground,
other reward slots/bridge modes, and the unplayed Woods/Zora owl additions.
No change here repairs a played seed or save; never regenerate over one.
