# Round 19 — Track audit (cs19h)

Agent/model: `cs19h`, `openai-codex/gpt-6.1-sol`; branch `r19/audit`.
Baseline: `d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`, the supplied 0.2.3 candidate.
**Documentation only; READY (merge).** No product code, test, setting, placement or game behavior changes.

## Method, provenance and limits

- Read the supplied AGENTS rules, README, CONTRIBUTING, roadmap index, architecture, orchestration,
  game-data/world-format plans, decisions, and relevant round-18 logic/story/equipment/rewards/keys/Mido/docs
  records. The round-19 overview and this track file did not exist at intake; followed the supplied brief.
- External evidence is **only ootrr public release bodies, changelog text, and issue/PR titles/descriptions**.
  Repository moved from REALAZK to [ootrando/ootrr](https://github.com/ootrando/ootrr), GPL-3.0 per intake.
  No source file, diff, patch, attachment, seed download, release binary or issue comment was opened.
  Root API metadata was used only to discover the changelog filename. An unrelated web-search result
  was discarded; it supplies no finding here. No GPL implementation is copied or proposed for porting.
- Retrieved all 16 available release notes and 50 available issue/PR descriptions (one page each, limit100).
  Latest returned release: **0.7.3**. The standalone `CHANGELOG-0.6.2.md` describes changes since0.6.1,
  including work beyond its filename; it is not proof that every listed change shipped in0.6.2.
  PR descriptions are separate reports, not independently verified implementation or play results.
- Allowed-source snapshot: `E:/OOTRemake/work/r19-audit/public-descriptions.json` (external, not committed).
  Some release bodies end mid-sentence; no omitted content was reconstructed.
- Every local file:line below refers to this baseline, not to another round-19 worktree. Existing tests were
  **read, not run**. Native-data facts are cited through our committed evidence; this audit did not open a dump.
  A matching feature is exposure, not proof of the same root cause. `[INFERENCE]` marks cross-project risk.
  No game was started; no seeds, saves, game folders or runtime installations were opened or modified.

## Ranked shortlist for maintainers

| Rank | Risk / disposition | Proposed owner and next proof |
|---|---|---|
| 1 | **Known physical lesson freeze remains.** Instrument-gated logic does not stop a player entering an automatic scene without one. | Scenes: whole caller/pose/input/cleanup repair, control from main, then Longshot 3.0.0 play. See1b. |
| 2 | **Three newly identified logic discrepancies**: DMT PoH damage/Hover route, DC Longshot-only Scarecrow token, adult DC torch progression. | Later logic track: native/route evidence and negative-access regressions before changing overrides; sweep if changed. See8. |
| 3 | **Fire blue-warp → Kakariko → reload** is a published immobility/save-hang report, not certified absent here. Our reward edits are narrower. | Scenes/rewards: preserve native landing, weather/Nocturne and sage completion; test actual output, then paired play including reload. See3a. |
| 4 | **Standard item-get replacements can grant nothing or freeze** despite valid item/logic. Sheik/Fairy scene animation context, NPC bindings and preload relationships matter. | Scenes/lacs: no palette expansion on generic-grant similarity alone; add caller-context regression and paired play before admission. See1c–d. |
| 5 | **Cow and merchant expansion must not release repeatable/missable progression.** Current holds avoid these new exposures. | Cows: per-source saved identity and reload recovery; later commerce: successful-payment-only completion, prices and wallet logic together. See5–6. |

No new product choice is made. D39 still holds the card at the captain. Nothing overnight needs Kareem.
All proposals below are **nothing**, **test to add**, or **fix for a later track**; no fix is implemented here.

## 1. Ocarina/NPC and scene crashes

### 1a. Anju crash and ocarina-from-NPC notes

**Their symptom/feature:** [changelog, Bug fixes / Crashes and Item pool and placement][C] names an
ocarina hand-over at Anju crashing, and says NPC ocarinas now use pickup-style delivery with equipment
selection. It explicitly labels that broader delivery unplayed. [PR24, Tested in the game / Known problem][P24]
reports Fairy Ocarina crashing the generic held-item get; songs/rewards are only suspected there.
Do not infer Anju's age or a detailed native crash cause from the short changelog bullet.

**Clawshot exposure:** this failure family already occurred at the child gallery, not Anju:
`plans/rounds/r11-ocarina.md:12-37` records the reproduced Time-ocarina crash and controls.
Both instruments are excluded from actual show-item hand-overs and scrubs in
`src/clawshot/data/settings.toml:61-63` and `src/clawshot/patch/gifts.py:983-1014`.
Anju's child gift remains eligible (`src/clawshot/patch/gift_rules.toml:152-154`), but her adult Egg and
Cucco hand-in are held vanilla (`src/clawshot/data/world/remake/gifts.toml:15-28`). Thus **not an exposed
newly generated Anju-ocarina placement under current policy**; old generated seeds are not repaired.
The regression fills place either ocarina in an early reachable chest instead, preserve direct-story gift
routes, and refuse scrub destinations (`tests/test_settings_songs.py:86-163`).

**Proposal: nothing** to widen admission. Preserve the exclusions. A future NPC pickup adapter needs a
**test to add** on the actual Anju child path, not just a synthetic generic gift: correct item, no crash,
active instrument, once-only completion and reload. Do not port their GPL implementation.

### 1b. Ocarina ownership is not physical lesson safety

**Their symptom/feature:** [PR11, Tutorials][P11] reports the first Field guide starting a lesson even
without an ocarina after moving Saria's gift. [C, Cutscenes and Bug fixes][C] also names a Bolero-trigger
crash and replaces several lessons with standard gets; no Bolero-specific cause is given there.

**Clawshot exposure: YES, a known unclosed physical risk.** `plans/rounds/r18-story.md:357-409` records
Kareem's failed Minuet, the earlier pose preceding the shared lesson, and withdrawal of **all** no-usable-
ocarina bypasses. Earlier positive counts in that file are historical, not current safety proof.
`plans/rounds/r18-logic.md:50-86` separates lesson access from automatic physical entry.
`tests/test_song_lessons.py:79-119` checks the twelve logical lessons' instrument/age prerequisites;
`tests/test_dungeon_rewards.py:129-143` preserves those prerequisites with rewards/bridge options.
Those cannot prevent an out-of-logic walk into a scene. This is not fixed by #34's selector repair:
`plans/rounds/r18-equipment.md:213-215` reports adult Sun's Song working with the control's Fairy selection,
so claiming every adult Fairy use fails would exceed the evidence.

**Proposal: fix for later/owning scenes track.** Include Saria/first-Field guide, forced Sheik triggers
(including Bolero), no instrument, Fairy-selected adult, and Time-selected controls. Audit the entire
parallel pose/fork/join, camera/music restoration, caller continuation, and exactly-once grant/history.
A new standard get is not safe merely because it ends at the same pouch action.

### 1c. Sheik/Fairy standard gets gave nothing; fountain refused to start

**Their symptom/feature:** [PR32, Cause and Changes][P32] says generic item gets inside Sheik/Fairy
scene-animation contexts did not animate or grant; stale preload relationships also prevented a fountain
event from loading. Its play report covers representative songs/fairies, not every individual song.

**Clawshot exposure:** current lesson replacement was withdrawn (1b); our gift mechanism edits source
rewards/once gates rather than wholesale scene removal (`src/clawshot/patch/gifts.py:7-18`).
The current delivery audit distinguishes41 show-item and15 direct routes and identifies no gift reaching
the scrub shield-wait helper (`plans/rounds/r18-equipment.md:39-69`). That rules out that helper, not all
animation-context failures. **[INFERENCE]** this is high-risk for the requested round-19 scene cutover,
not proof of a present all-Sheik/no-reward defect.

**Proposal: test to add** when changing scenes: exercise emitted caller plus callee and its preloads,
source flag writes and reward acquisition under scene versus ordinary actor binding. **Fix for later
track** only if that proof fails; native cleanup/quests must survive. See the common play contract below.

### 1d. Dungeon item from a hand-over freezes with raised hands

**Their symptom/feature:** [0.7.2][R72] describes a Rolling Goron small-key freeze; [0.7.3][R73]
extends the repair to boss keys/maps/compasses and says the copied get scene needed its giving NPC bound.
This is distinct from both ocarina actor lifecycle and the Mirror Shield equipment polling bug.

**Clawshot exposure:** the named outside-dungeon item requires a **Chest** destination
(`src/clawshot/generate/fill.py:360-368`); Rolling Goron is not such a source. Fortress keys are additionally
limited to chest/native-key-source types. Current bound chest tests exercise native ownership fields,
source lifecycle and named target credit (`tests/test_dungeon_items.py:50-100,140-151,320-332`).
No evidence justifies extending those chest bindings to generic NPC grants. The existing adult Mirror
scrub report and its two-edge repair are separate (`plans/rounds/r18-equipment.md:81-91`).

**Proposal: nothing** for current NPC admission; **test to add** before any expansion: actual NPC-bound
caller, correct target count/text, pose termination, spending and reload. Keep the current chest/source
restrictions until such an adapter is proved.

## 2. Gerudo Card working alone; fortress load crash

**Their symptom/feature:** [PR26][P26] says a moved card did not pacify guards because they read quest
progress, and deliberately did not declare entry NPCs fixed. [C, Cutscenes][C] later claims card-alone
membership for gates/talk/Training Ground/archery. [PR44][P44] then identifies archery's separately packed
schedule still refusing card-only Link; its description explicitly says archery was not played.
[PR41][P41] reports played open/fast Fortress modes, separate from ordinary card-only clearance.
[C, Crashes][C] also names a Fortress-load crash but gives no reproduction or cause.

**Clawshot exposure:** new seeds avoid the moved-card discrepancy by policy, not by making the card
sufficient. `src/clawshot/data/world/remake/gifts.toml:11-13` and
`src/clawshot/patch/gift_rules.toml:115-118` pin it; `tests/test_gerudo_card.py:46-97,134-148` covers presets,
manual Gift choices, patch refusal and fill-around behavior. `plans/rounds/r18-keys.md:7-23,44-50`
separates card, SpiritStep02, Training Ground admission and carpenter rescue. Shuffled jail keys must
not clear guards. Older moved-card outputs remain outside that protection (`README.md:148-151`).
The short Fortress-load bullet is **unattributed**, not evidence that our new keys cause or fix it.

**Proposal: nothing** to D39; do not advance the Spirit quest merely on card receipt. If card shuffle is
revisited, **fix for later track** must cover guard modules AND loose/packed schedules, desert gate,
Training Ground, archery with Epona present, all four rescues and reload independently. For loading,
**test to add** to future Fortress packets: cold entry and reload before/after rescue with keys on/off;
seek a main-control reproduction before asserting the same crash.

## 3. Saves, reloads and skipped transitions

### 3a. Fire clear → Kakariko immobility and saved-scene hang

**Their symptom/feature:** [issue13 description][I13] reports a medallion-shuffled Fire clear skipping the
Sacred Realm, landing in rainy Kakariko unable to move, and a save/reload hanging. Rain/Shadow state is
reporter context, not an established cause. [C, Fire Temple][C] says fixed without explaining how.
[PR42][P42] describes later boss-room grants and shortened dungeon landings, but does not establish that
it is the fix for13.

**Clawshot exposure: comparable path exists; same defect NOT established.** Volvagia's current grant is
`Dm_Awake_Fire_Get.110/Event13` (`src/clawshot/data/dungeon_rewards.toml:34-40`). Our reward transformer
changes only grant identity and Notes target (`src/clawshot/patch/rewards.py:16-45`), retaining the native
sages/blue-warp/landing sequence, unlike the reported skipped sequence. Completion and Nocturne eligibility
remain distinct from medal ownership (`plans/rounds/r18-rewards.md:19-38`;
`tests/test_dungeon_rewards.py:92-117,129-143`). These structural tests cannot certify a live landing.

**Proposal: test to add** to scenes/rewards acceptance: Fire clear with a different medal, Kakariko before
and at Nocturne readiness/rain, movement and control return, actual saved scene and Continue/cold reload.
Use the same main packet as control. **Fix for later track** only after state/caller evidence identifies
which transition is wrong; do not infer a medal requirement or globally skip scenes from the report.

### 3b. Navi room returns break saving; skipped map intros lose visit state

**Their symptom/feature:** [C, Maps][C] names boss/miniboss Navi returns breaking saving without giving
its cause or exact save fields. [PR25][P25] separately attributes missing pause/minimaps to skipped title
cards not writing visited-area flags. Those are two distinct claims, not a demonstrated shared bug.

**Clawshot exposure:** no corresponding shipped Return-with-Navi option was found in the scoped source
search. Our logic explicitly assumes **no save warp** (`src/clawshot/world/softlocks.py:21-39`;
`tests/test_softlocks.py:67-87`). First-visit/map side effects are relevant to our intro/owl skips;
round18 retained the castle title action and visit state (`plans/rounds/r18-story.md:75-93,372-395`).
That castle observation does not certify every dungeon/miniboss save return.

**Proposal: nothing** to add Navi warps. **Test to add** for future skips/returns: visit flag, map availability,
real checkpoint/stage/entrance, reload and movement from the saved slot. Do not pre-mark all areas visited
just because another project chose that tradeoff; it can alter owl presence (PR25 describes that side effect).

### 3c. Loading-screen hotfix and older outputs

**Their symptom/feature:** [0.2.1][R21] says0.2.0 could stall on Loading, without cause. [0.3.0][R30] and
[0.5.0][R50] warn old seeds may not build; these are generation compatibility notes, not proof of save repair.

**Clawshot exposure:** generic loading failures remain possible; no same-cause match is established.
The writer checks changed trees/compression and resource allocations before writing
(`src/clawshot/patch/write.py:232-237,248-298,324-336`). This is resource integrity, not a live boot guarantee.
`README.md:141-159` explicitly preserves old-save/output limitations, including opened chests that cannot
re-award repaired dungeon items. Rebuilding must not be sold as migrating an old save.

**Proposal: nothing** based on the opaque loading note. Keep per-change boot/load-line proof and fresh
output isolation. A diagnosed loading regression needs a **test to add** around its actual resource/caller.

## 4. Once-only gifts and trade-slot loss

**Their symptom/feature:** [PR22][P22] reports a shuffled fairy paying out repeatedly while its vanilla
item remained unowned; [C][C] also lists fountain refusal. [0.3.0][R30] says trade items overwrote one
another; it does not document a mechanism that makes our shared slot safe.

**Clawshot exposure:** the fairy failure family is already addressed through check-specific saved flags,
not reward possession (`src/clawshot/patch/gifts.py:7-18,105-111,191-205`); D22's persisted fairy reward was
played (`plans/decisions.md:59-62`).
Saved Bool defaults/reset/save-index and post-grant writes have synthetic coverage
(`tests/test_gifts.py:76-90,221-239`); that is not a new six-fountain live reload proof.

Trade progression is separately conservative:
`src/clawshot/data/world/remake/gifts.toml:3-48` holds Egg/Letter and adult hand-ins; its documented native
shared-slot behavior can hide the Cucco needed for Talon even when both ownership bits exist.
`README.md:145-147` warns older shuffled trade outputs are not repaired by Continue.

**Proposal: nothing** to loosen either hold. A later trade feature needs separate display/hand-in
availability evidence, not just additive ownership bits. Reuse the existing fairy once-only contract;
new receipt paths need a **test to add** for declined/failed give, success, re-entry, reload and no duplicate.

## 5. Cows and collection persistence

**Their symptom/feature:** [0.6.0][R60] reports cow-plus-holder shuffles failing a build audit;
[0.6.1][R61] says fixed. [0.6.2][R62], [PR16][P16] and [C][C] combine eight cow checks under one switch.
Those notes do not establish each cow's saved identity or reload behavior. Separately [issue14][I14]
reports rock/grass rewards reappearing after re-entry. [C, Duplicated items][C] changes breakables to
permanently used, explicitly admitting that an uncollected reward can then be lost; [0.5.0][R50] had instead
described pot restoration until collection. These are different persistence contracts.

**Clawshot exposure:** cows/pots/crates/loose rupees are not shipped shuffle kinds (`README.md:70-76,118`).
Our census finds14 cow actor placements, global milk flags and no per-cow completion flag
(`plans/03-game-data.md:169-187`); do not equate placements to ootrr's eight logical checks.
D11 keeps cows out (`plans/decisions.md:28-29`). Current floor hearts deliberately keep native saved Hash
and all copies (`src/clawshot/patch/freestanding.py:1-5,50-66`), with a five-item palette
(`src/clawshot/patch/drops.py:23-29`; `src/clawshot/patch/freestanding.py:120-133`). Floor/jail keys have a
separate recovery/once-only contract (`plans/rounds/r18-keys.md:36-50,143-173`).
All nine translated cow checks are explicitly excluded as non-one-time sources
(`src/clawshot/data/world/remake.toml:211-247`), not just hidden by a UI toggle.

The [0.4.0 note][R40] separately ties Skulltula retirement to collecting its dropped reward, not merely
killing it. Our generated pickup retains the native collection graph/source-Hash contract
(`src/clawshot/patch/tokens.py:549-587`). `tests/test_tokens.py:681-704` asserts the pickup waits for its
completion callback while enemy death saves no permanent collection. This is structural evidence, not an
audit-run save/reload experiment. **Proposal: nothing** to replace it with destruction-time retirement;
future donor families need the same callback proof plus uncollected/collected reload play.

**Proposal: fix for later/owning cows track**, not an admission change here: persist each logical cow
independently; separate empty-bottle/song refusal from a successful one-time grant; preserve subsequent
vanilla milk; verify both-age copies, reload and all new GameData/resource inputs. For any future holder,
**test to add** abandoned-drop recovery across leave/reload, then no duplicate after collection. Never
admit progression to a source that permanently retires on destruction rather than completed collection.

## 6. Shop prices and merchants

**Their symptom/feature:** [0.6.2][R62], [PR16][P16] and [C, Shopsanity][C] add wallet-banded shop prices,
Medigoron/Bean Merchant shuffle, scrub/merchant price controls and offer hints. [C, Shop upgrades][C]
replaces top-tier grants with next-owned-tier, once per shelf, explicitly unplayed there. [PR21][P21]
fixes shop-deal/holder item-count accounting causing builds to fail. [C, Builds][C] also names menu-scrub
one-time price/hint failures. [PR45][P45] adds fairy price controls but says that part is not played.

**Clawshot exposure:** native display-only shelves are an intentional narrower contract, not support
for arbitrary majors or progressive deal shelves (`src/clawshot/generate/fill.py:333-358`;
`plans/decisions.md:56-58`). Price selection is shared between logic and overlay, affordable10 or native
with a cheap Kokiri Deku Shield exception (`src/clawshot/settings.py:38-53`).
Wallet predicates use the native 200/500/1000 capacities (`src/clawshot/data/shops.toml:1765-1775`) and
recompile the price clause without removing stock/story rules (`src/clawshot/world/shops.py:55-59,75-91`).
`tests/test_settings_prices.py:13-65` covers exact prices removing conditional discounts, shuffled-only
affordability, retained child/story/refill restrictions and item-scoped cheap shields. Our current
once-scrub fixed prices span0–1000, default vanilla, not arbitrary merchant prices
(`src/clawshot/data/settings.toml:13-17`); wallet boundaries and unchanged payment/once flow have coverage
(`tests/test_shop_settings.py:92-128`). Those tests already cover existing policy; no duplicate test is proposed.
Merchant experiments remain held: Medigoron, Wasteland Bombchu seller and Granny potion
(`src/clawshot/data/world/remake/gifts.toml:86-100`). Cow/holder composition from PR21 is not offered here.
Merchant success flags are deliberately inside native sale-success paths
(`src/clawshot/patch/gifts.py:98-102,128-129`), not a receipt inferred from money/stock ownership.
The held merchant prototype already has semantic refusal/shortfall/capacity, successful charge and
saved-state repeat tests (`tests/test_gifts_merchants.py:179-234`). Its simulated reload copies interpreter
state, not a serialized save or played acceptance; do not mistake the prototype for enabled shuffle.

**Proposal: nothing** to adopt their pricing/defaults/palette. Reuse the merchant tests already present.
**Test to add** only for new price/shelf contracts before later commerce release: offered price = charged
price = logic wallet requirement, purchase-time tier/stock persistence and item counts across fill stages.
Progressive shelf support needs an actual purchase-time tier adapter, not existing chest progressives.
Keep fairy prices native unless a separately approved feature pairs offer text, charge and logic.

## 7. Quest order, closed forests and adult return

### 7a. Darunia's lost dance and backwards quest writes

**Their symptom/feature:** [PR23][P23] reports losing the dance/gift after opening or finishing Dodongo,
and four late events rewinding Fire quest progress; it explicitly leaves Rolling Goron crater-first and
Impa send-off to other work. A song or strength reward moved elsewhere can expose the ordering.

**Clawshot exposure:** our native Darunia/Bracelet source stays fixed for child bomb/return guarantees
(`plans/04-world-format.md:172-179`), and our own source latch plus monotone writers already address the
ordering family (`src/clawshot/patch/darunia.py:9-17,243-264`). Synthetic coverage includes room, meadow,
Letter, mountain and Impa-sendoff writers (`tests/test_story_steps_fire.py:19-24,81-117`); written-native
tests cover late dance/source-once, wrong song, room meeting and late meadow
(`tests/test_story_steps_darunia_dump.py:90-137,189-203`). The latter explicitly excludes engine timing
and actual late NPC availability from its claim (`tests/test_story_steps_darunia_dump.py:1-4`).

**Proposal: nothing** to duplicate these guards/tests or borrow their implementation. Retain our broader
Impa-continuation protection. Any future source release must preserve those regressions and obtain actual
late-source availability/grant/reload play evidence; a passing state interpreter is not that observation.

### 7b. Open Kakariko plus closed forest; open Door loses moat checks

**Their symptom/feature:** [0.7.2][R72] refuses an open Kakariko gate with either closed-forest choice.
The release does not fully explain the trap; do not invent one. [PR48, Fix][P48] describes an open-Door
catch-up jumping over the exact escape/moat quest steps although logic still counted their checks.

**Clawshot exposure:** unsupported unpaired native-access overrides are refused
(`src/clawshot/settings.py:15-35`; `src/clawshot/data/settings.toml:65-80`); an ootrr-style independent open
Kakariko mode is not among the paired choices. Mido's different completed-castle schedule problem was
played and fixed (`plans/rounds/r18-mido.md:81-88`). Our earlier-Door repair explicitly preserves late
escape/moat sources and monotone steps (`plans/rounds/r18-rewards.md:222-245`), with owned stones only
for the shuffled closed Door (`tests/test_dungeon_rewards.py:92-109`).

**Proposal: nothing** to copy their feature coupling. Keep native validation and independent Door/story
contracts. **Test to add** to any new early-Door mode: late DC/Jabu completion cannot skip escape,
moat item, lesson or latch; Continue must retain reachable checks. A beating-the-model seed alone cannot
prove that exact-step physical triggers survived.

### 7c. Adult stranded behind Forest completion; lost Malon lesson

**Their symptom/feature:** [issue35][I35] and [issue39][I39] report inaccessible Deku checks and inability to return
child for a Forest tool. [PR43][P43] reports Malon's uncollected child lesson lost when Epona's quest had
already completed; [PR47][P47] separately changes skip-race logic/quest completion, unplayed there.

**Clawshot exposure:** chronological child-prefix inventory and the default early-pull return guarantee
already distinguish beatability from safe optional pulling (`tests/test_age_travel.py:153-194,227-234`).
D20 requires adult return (`plans/decisions.md:52-55`); free travel is separate from merely opening the Door.
Native Epona progress requires clearing Malon's actual source, not remotely finding the song
(`src/clawshot/data/world/remake/child_lon_lon_ranch.toml:19-34`;
`tests/test_story_steps_epona.py:18-48`). That makes the reported complete-before-source order unavailable
in the modeled native race chain; no shipped skip-race patch was found. Out-of-logic/debug/old states are
not certified by that argument. The current setting can explicitly disable the return guarantee
(`src/clawshot/data/settings.toml:69-70`); **[INFERENCE]** a user choosing that opt-out can retain the
unsafe-early-pull class even if the final seed is beatable.

**Proposal: nothing** to merge Door-open and free-travel semantics. For a future race skip, **test to add**
for child Malon uncollected after Complete, persistent once-only source and challenge completion.
Retain the return guarantee by default; do not describe an explicit opt-out as softlock-safe.

## 8. Reported logic mismatches that may falsely certify progression

These are **new audit candidates**, not freshly played Clawshot failures. No rule is changed here.
The native claim comes from permitted ootrr prose; independent remake evidence is still required.

| Reported correction / feature | Current Clawshot evidence and possible exposure | Proposal |
|---|---|---|
| [PR38][P38]: DMT PoH no longer reachable by child damage-jump or Hover Boots; needs adult bean route. | `src/clawshot/data/world/death_mountain_trail.toml:19` still has both alternatives; no matching remake override or targeted test was found. With optional floor shuffle the palette still admits shields (`src/clawshot/patch/drops.py:23-29`), so the mismatch is not made irrelevant by excluding arbitrary majors. `[INFERENCE]` can falsely advance a sphere/return kit if an admitted useful reward is placed there. | **Test to add**, then **fix for later logic track** after physical/native route evidence: child damage and adult Hover-only must not be accepted if PR38's remake claim holds; keep the legitimate bean path. |
| [C, Logic / Dodongo][C]: Scarecrow GS needs the song. | `src/clawshot/data/world/dodongos_cavern.toml:57` still allows Longshot alone, without a matching remake override/test found. Token shuffle admits useful rewards (`README.md:94-99`). `[INFERENCE]` false Longshot-only reach can strand required progression, even though Longshot itself is owned. | **Test to add** for no-song Longshot versus playable Scarecrow; **later fix** only with source-location/route evidence. |
| [C, Logic / Dodongo][C]: adult torch room needs Bow/Fire Arrows/Din's Fire. | `src/clawshot/data/world/dodongos_cavern.toml:33-34` allows adult entry and onward Staircase progression solely by age; no matching remake override/test found. `[INFERENCE]` can place an opening tool behind the route it falsely opens. Entering a room and solving its exit must not be conflated. | **Test to add** for adult without a fire/ranged solution and for each real alternative; **later fix** the actual progression boundary, not necessarily room admission. |
| [Issue35][I35] and [C, Deku][C]: basement/Compass access overestimated. | Already stronger here: `src/clawshot/data/world/remake/child_deku_tree.toml:19-41` requires usable Slingshot/Boomerang before3F/basement; `:57-65` also requires an escape tool before Slingshot-room entry. `tests/test_softlocks.py:17-42` covers self-supplied escape. | **Nothing** to relax. The precise large-Skulltula combat clause in C is not independently established here; a **test to add** should separate reaching3F from opening each Compass-room reward if new native evidence requires more. |
| [C, Dodongo][C]: far bridge is not a direct upper-Lizalfos route. | Already explicit: `src/clawshot/data/world/remake/child_dodongos_cavern.toml:38-76` splits the Bomb Bag ledge and closes the direct edge, retaining explosive-wall prerequisites. | **Nothing**; do not restore the translated edge. |
| [PR38][P38]: submerged lab rupee lacked a diving requirement; [PR28][P28] and [PR29][P29]: rocks could hide or retire checks with story changes. | Loose rupees and rocks are not shuffled (`README.md:70-76,118`); current floor adapter admits only linked saved heart sources (`src/clawshot/patch/freestanding.py:26-51`). | **Nothing** for current sources; **test to add** for exact age/story spawn and retrieval before any future source admission. |

Our certificate is deliberately limited to evidenced physical regions, not an all-game softlock proof
(`src/clawshot/world/softlocks.py:21-39`; `plans/rounds/r18-logic.md:98-205`). The strongest confirmed
remaining issue is the automatic lesson path in1b. The three table discrepancies are potential logic
false positives; the Fire reload report is an unconfirmed same-feature hazard. Keep those labels distinct.

## Follow-through contract and verification

- Proposed priorities and dispositions: cs19h, for maintainer triage; no behavior/default decision made.
- Requests posted on `cs-r19`: scene-context/withdrawn-guard risk; three local logic discrepancies.
- A behavior track owns any later code/test edit. Before READY, placement/logic/destination/source changes
  need the required locked200 broad +50 Defaults +50 Recommended sweep, zero exhausted, and exact-head gate.
  New output inputs must enter `pack/resources.toml` and the NUP dump check.
- Any changed gameplay remains **built, not played** until Kareem's staged **Longshot 3.0.0 stable** check.
  Use the current Longshot template, one isolated mod/profile per arm, unset overlay, the same main-built
  control packet, natural save preference and exact-slot named chest-open flags. No new packet was staged
  here; no checklist estimate or control reproduction is fabricated. Future acceptance includes source
  loading lines, actual item/control outcome, refusal, leave/re-entry and Save/Continue/cold reload.
- This track ran **no Ruff, pytest, gate, sweep, generation or game command**. Documentation/reference
  validation only; existing suite counts in cited historical records are not re-reported as this audit's checks.
- Handoff: commit this file only, then post resulting head and ranked shortlist on `cs-r19`.
  Remaining work is the explicitly proposed behavior-track research/tests/play, not a blocker to this docs merge.

## Public source references

All links below were used only for their displayed description/changelog/release text. External symptoms
are paraphrased; no implementation source or diff is linked as evidence.

[C]: https://github.com/ootrando/ootrr/blob/main/CHANGELOG-0.6.2.md
[R21]: https://github.com/ootrando/ootrr/releases/tag/v0.2.1
[R30]: https://github.com/ootrando/ootrr/releases/tag/v0.3.0
[R40]: https://github.com/ootrando/ootrr/releases/tag/v0.4.0
[R50]: https://github.com/ootrando/ootrr/releases/tag/v0.5.0
[R60]: https://github.com/ootrando/ootrr/releases/tag/v0.6.0
[R61]: https://github.com/ootrando/ootrr/releases/tag/v0.6.1
[R62]: https://github.com/ootrando/ootrr/releases/tag/v0.6.2
[R72]: https://github.com/ootrando/ootrr/releases/tag/v0.7.2
[R73]: https://github.com/ootrando/ootrr/releases/tag/v0.7.3
[I13]: https://github.com/ootrando/ootrr/issues/13
[I14]: https://github.com/ootrando/ootrr/issues/14
[I35]: https://github.com/ootrando/ootrr/issues/35
[I39]: https://github.com/ootrando/ootrr/issues/39
[P11]: https://github.com/ootrando/ootrr/pull/11
[P16]: https://github.com/ootrando/ootrr/pull/16
[P21]: https://github.com/ootrando/ootrr/pull/21
[P22]: https://github.com/ootrando/ootrr/pull/22
[P23]: https://github.com/ootrando/ootrr/pull/23
[P24]: https://github.com/ootrando/ootrr/pull/24
[P25]: https://github.com/ootrando/ootrr/pull/25
[P26]: https://github.com/ootrando/ootrr/pull/26
[P28]: https://github.com/ootrando/ootrr/pull/28
[P29]: https://github.com/ootrando/ootrr/pull/29
[P32]: https://github.com/ootrando/ootrr/pull/32
[P38]: https://github.com/ootrando/ootrr/pull/38
[P41]: https://github.com/ootrando/ootrr/pull/41
[P42]: https://github.com/ootrando/ootrr/pull/42
[P43]: https://github.com/ootrando/ootrr/pull/43
[P44]: https://github.com/ootrando/ootrr/pull/44
[P45]: https://github.com/ootrando/ootrr/pull/45
[P47]: https://github.com/ootrando/ootrr/pull/47
[P48]: https://github.com/ootrando/ootrr/pull/48
