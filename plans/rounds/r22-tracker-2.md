# Round 22 overnight tracker — cs22b

Base: main `874f30a`; branch `r22/tracker-2`; worktree `E:/OOTRemake/clawshot-r22/tracker-2`.
Plan posted on `cs-r22` before implementation. No seeds or game launch; ask Claude before seed generation.

## Requested scope

1. Ruto's Letter: trace exact saved holdings/history and refresh/reload behavior; correct only a proved cause.
2. Closed forest: respect the actual saved Gohma completion gate in the tracker.
3. Dodongo's Cavern: audit held Bracelet/no-Bag access for both ages against current adult flower rules.
4. Keaton Mask: require the saved Kakariko guard letter-show completion, not possession of Zelda's Letter alone.
5. Vanilla shops: model purchases with Shop shuffle off; preserve shuffled-stock secrecy and native prerequisites.
6. Darunia: initial instruction was to hold changes for cs22d. Superseded by Claude's follow-up below.
7. UI: mark an area whose remaining checks are all in logic; prioritize open/in-logic checks within each area.

## Maintainer follow-up

Claude explicitly chose saved completion for readable event gates (Gohma and letter-show), overriding projected
possible-action reachability for these tracker gates only. Generator reachability stays unchanged. Missing saved
fields remain conservative, not derived from gear or owned stones. Cheap area hints may say which undone event
would open checks.

Claude relayed cs22d's Darunia audit: normal seeds anchor GC Darunias Joy; the vanilla bonus gives nothing while
the child Bracelet is already owned. Show that vanilla check as done/empty from actual ownership. This is a
**reversible tracker presentation policy**: no game flag, permanent mark or runtime change; removing/unreading
that ownership must remove the inferred empty state. Never apply it to a shuffled non-Bracelet reward.

## Evidence collected before implementation

- Closed-forest world with an empty inventory already blocks Field/Kakariko/Market. The All checks view lists
  out-of-logic rows deliberately. Sword+shield+Slingshot lets the generic search derive Gohma and leave the forest
  before the fight is played. The approved tracker-only saved-event filter removes that projection.
- Actual owned Deku/Hylian Shields already satisfy Mido with Shop shuffle on or off in direct world evaluation.
  The distinct missing purchase path is being audited; no broad vanilla reward closure is approved or added.
- Native saved Bools (GameDataList default false/reset8/save0): `HavePlayedEvent.Dm_Deku_BossOut` Hash1484945036
  and `Npc_Hylia_Soldier_003_GateOpen` Hash428444948. `Get_StoneOfForest` Event78 transitions to the Gohma outro;
  `Dm_Kakariko_0010` Event18 and `Npc_Hylia_Soldier_003` Event3 set the guard Bool. Native Mask Shop
  `Npc_Hylia_018_Shop_Child` Event5/76/97 and DisplayShop Event468 read that same guard Bool. Owning the letter
  is not that flag; neither is a later Fire quest step (which can advance by another route).
- Existing acquired/stock/bottle mappings and DC child/adult source distinctions are being traced independently.
- Python navigation server was unavailable on PATH; source navigation uses scoped find/grep after that failed
  capability check. New worktree dependencies installed once with `uv sync --frozen`.

## Verification and acceptance

Only focused tests for the changed paths, at `-n 8` while the player is closed or `-n 2`/one generator worker while
open; one test run per track. No seed generation without permission. New UI gets deterministic headless tests
and actual-browser screenshots. Tightenings need no play. Any new capability loosening stays labelled play-held
with a precise maintainer check. Exact changes/results/commits and remaining boundaries will be recorded here.

## Investigation and decisions

- **Letter:** no mapping change justified. The tracker reads current BottleA-E content `Letter` and the persistent
  `IsGet.Item_Bottle_Letter`. Read-only evidence from the documented natural
  `work/save-backups/2026-11-09_0954-main-after-jabu/.../slot_05/progress.sav`:
  acquisition flag true, current bottles Bug/Empty, tracker logic `Rutos Letter = 1`.
  `Get_StoneOfWater_GetRutoLetter` is also true there, but no speculative fallback was added.
  Polling watches `(path, mtime, size)` and follows newest slots unless pinned. Save/Continue can update it;
  restarting Clawshot against unchanged saved bytes cannot. This is a code/native-copy finding, not a claimed
  new Bender play result. A fresh saved-pickup/session-reload regression covers the refresh seam.
- **DC:** the actual physical actor is `Armor_Child_Gauntlet_Goron`; its stock grants a Progressive Strength copy.
  Adult flower routes already consume that counter. Bracelet alone does not defeat the Lizalfos/projectile
  route; Bow supplies that separate path. Child copy-only strength remains blocked by the generator's explicit
  R14 policy until Darunia's saved gift supplies `Goron Bracelet`. No rule/mapping loosening was made.
  Older-generator seeds still deliberately lack in-logic entirely; the page shows that version reason.
  **For Bender:** a chest Bracelet works for child Link, but logic only counts Darunia's.
  Claude reaffirmed the deliberate R14 exception (`r14-progressive.md:110-122`): crediting a child copy
  deadlocked the closed-door return kit. Out-of-logic DC rows remain listed; no generator change.
- **Vanilla purchases:** Claude approved catching up to an assumption the generator already makes, not a new
  play-held loosening. Evidence: `generate/fill.py:1164-1170` includes fixed non-N64 Shop stock in placements;
  `:497-498` replays it for assumed fill and `:1278-1279` for the final oracle, via
  `world/search.py:435-441`. A direct no-generation replay with held Sword changed Mido false→true on collecting
  `KF Shop Item 7`'s vanilla Deku Shield. Price uses `shop_price()` and the maximum native-copy base price;
  saved `PlayerStatus.CurrentRupee` (`wallet.count`) when present, wallet capacity otherwise.
  Only native unshuffled Shop locations become availability events; other fixed progression is not collected.
  A source annotation names shop, price and budget, never a shuffled reward or permanent shelf completion.
  Existing play accepted by Claude: Kareem's vanilla Deku Shield purchase in 06-kak and shield/tunics in 4a.
- **Saved completion:** tracker-local event filtering prevents gear from projecting Gohma or letter-show;
  original world objects/generator events stay unchanged. The counterfactual hint credits exactly one known
  undone saved event, per age, and only when that area's remaining checks are otherwise all closed.
- **Darunia:** infer empty only for the anchored vanilla `Goron Bracelet` bonus while exact child-Bracelet
  stock is positive. Already saved completion stays collected. Stock removal/unreadability removes the
  inference; adult gauntlets do not trigger it. No event credit, mark, game writer or generator change.
- **UI:** stable priority is open/in-logic → other open → finished; each tier preserves original ordering.
  The non-vacuous **All in logic** badge compares all remaining listed checks before the Show filter and uses
  the selected age. Vanilla rows participate when shown. An already finished area never receives the badge.


## Browser proof

Shipped HTML/JS/CSS, real headless Chromium, isolated synthetic backend fixture and scratch preferences:
`E:/OOTRemake/work/r22-tracker-2/shots/metrics.json`. No player files changed or game launched.
At 1280×860 and 1920×1080: reachable-open rows sort before other-open/finished rows; age changes switch
readiness badges; the Gohma after-event hint appears; purchase details name shop, 40-rupee price and saved
rupees; Darunia's empty state is distinct from saved collection and explains reversibility.
No page errors or non-local requests. Screenshots inspected: `purchases-child-1280.png`,
`ready-either-1920.png`, `empty-child-1280.png` under that directory. Badge approximately 57×18 px.
The throwaway runner was deleted after proof. These are renderer observations, not in-game acceptance.


## Focused verification receipt

- `uv run ruff format --check`: **612 files already formatted**. The first check printed only this change's
  multiline-comprehension/call formatting; corrected with anchored edits before the successful check.
- `uv run ruff check`: **All checks passed**.
- Fresh CIM player count **0**; `CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest -m 'not dump' -n 8 -q
  tests/test_tracker*.py tests/test_r22_tracker_reports.py`: **342 passed, 1 skipped in 26.93 s**.
  Logs: `E:/OOTRemake/work/r22-tracker-2/{format-final,lint,focused}.log`.
  Covers saved-event tightening/cache reversal/unknown flags, native closed forest and Keaton, purchase
  thresholds/fallback/Shop-on secrecy/held shields, reversible Darunia inference, both DC ages, saved Letter
  polling/reload, readiness/filter/sorting/hints/empty/source rendering and existing tracker contracts.
- Real Chromium renderer proof and inspected screenshots are above. No seed generation, game launch,
  native save modification, dump/census change or generator/world-rule change. No lock acquired.
  Per Claude's task, QA was focused; whole-repository synthetic/dump gates were not run for this tracker-only change.
- Claude explicitly retained the R14 child-strength exception; no open product decision or new play hold remains.

