# Round 22 merchants — cs22d

Branch `r22/merchants`, base `874f30a`, assigned by Claude after the gift-gates audit, 2026-11-25.
0.2.9 shipped the Medigoron tightening only (main `5dcb21b`, merge `9895d54`); merchant admission targets the next release. Do not lift the three holds without Kareem's play and a full paired sweep.

## Requested scope and direction split

Kareem wants Medigoron shuffled. Claude requested all three round-8 merchant checks: GC Medigoron,
Kak Granny Buy Blue Potion and Wasteland Bombchu Salesman. Existing private success-only saved-flag
writers are the implementation, not a second merchant system.

Claude's subsequent ruling splits logic changes by direction:

- Tightening now: remove the unverified standalone strength/flower room alternative for Medigoron.
- Loosening stays with admission and play: remove the imported wallet-upgrade predicates only after
  default-wallet purchases actually grant the native items: Medigoron exactly200 ->0, Giant's Knife;
  Granny exactly100 ->0, Blue Potion, empty bottle. Native default capacity is200 (Kareem/Claude).
- All three `keep_vanilla` reasons remain. No disabled admission setting or placeholder implementation.

## Applied tightening

`data/world/remake/gifts.toml` guards the old imported Medigoron expression and changes it to
`is_adult and Progressive_Wallet and can_blast_or_smash`. Adult and wallet gates remain. No change
for nearby pots, gossip stone, Fairy event or global strength/flower policy.

Native room evidence, read-only supported dump:

- Adult Medigoron: `GoronCity_Adult_Static`, actor17027280679108631710.
- Nearby room barriers are `WallCrack`: static8707685800385094154;
  dynamic13982487283639748188 and13998689331476538657.
- Current actor has6 life and100 damage rates for native `Bomb` and `Hammer` keys.
- Static barrier's `GoronCity_Common_8977` graph reads death-procedure completion, waits60 frames,
  then requests the riddle sound; no item/strength prerequisite in that graph. Current source SHA256
  matches its existing r14 decoded evidence (`db368f02389307bbfc89ea77972eb4f0fe429aae60a66fff3e021eb11c5edcd1`).
- This retains the existing blast/Hammer route. Coordinates do not establish transport/ignition of
  a nearby flower; the strength-only alternative is not newly certified. See `r22-logic.md:53-70`.

## Admission prerequisites found before coding a lift

Deleting the three holds is insufficient:

1. All three effective native pool items currently have no actor-table mapping: `Giants Knife`,
   `Blue Potion`, `Bombchus (10)`. `seed_checks` verifies a check's pool actor against its census
   steps. Native PouchActorInfo contains `Item_Sword_Giant` (equipment `Weapon_Sword_Giant`),
   `Item_Bottle_BluePotion`, and `Item_BombchuBundle_Medium` (10). Shop/census aliases must be
   reconciled rather than adding rupee substitutions or silently excluding a merchant. Bottle
   content/container behavior must be reported by play, not inferred from an actor name.
2. Every merchant rule has `purchase=True`, `once=()`, and is outside `TIERED_GIFTS`/bowling.
   `seed_step` currently does not force purchase normalization for an identical assignment.
   Admission must include the purchase normalization edge plus a consumer-visible saved-repeat
   regression, so native-stock assignments do not silently bypass private saved completion.
3. Existing `_purchase` code redirects Medigoron Event6/Event19 from Giant/Biggoron ownership to
   its collection Bool; keeps funds/capacity/refusal; does not take a broken knife for an unrelated
   prize. Granny retains unlock/empty-bottle checks and100r charge on success. Carpet retains90r
   transaction checks. Current serialized transforms pass the three focused native oracles below;
   no in-game result or additional native state-interpreter run is claimed.

These remain held on this shipping worktree. No mappings, aliases, wallet
relaxation or hold removals have been shipped.

## Play preparation

Checklist: `E:/OOTRemake/work/r22-merchants/PLAY.md`.
Use Longshot3.2.0 with isolated save copies and exactly one experiment mod (or no mod for the
native control). Claude boot-checks after Jabu while the game is closed; agents never launch it.

Read-only source inspection found a default-wallet adult checkpoint without save edits:
`work/save-backups/2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001/slot_01`.
Its actual thumbnail is adult Link facing Sheik beside the Master Sword pedestal in the Temple
of Time. Both wallet-upgrade flags are false; Bomb Bag and bottle owned; Knife/Biggoron Sword,
Hammer, Hookshot and Longshot absent. Normal Granny trade unlock still required. The later
After-Forest backup has a wallet upgrade and Hookshot, so cannot prove those baseline cases.

A native Knife purchase on a private control save can provide an actually owned Knife, with no
new merchant Bool, for the independent shuffled Medigoron test. Never reset a collected Bool to
make an experiment appear to pass. Donor-actor grants need their own controlled generic-get
proof before mappings and admission land.

## Verification observed

Focused synthetic only, allowed outside the lock by `r22-overview.md:50`:

`CLAWSHOT_WORKERS=1`, every `OOT_*` unset; logic venv Python, this branch's `src` on PYTHONPATH:

`python -m pytest tests/test_world_remake_adult_goron_city.py tests/test_gifts_merchants.py -k 'medigoron or private_shop_purchases or granny_preserves' -q`

**8 passed,28 deselected in3.72s.** Six cases cover child rejection, strength-only rejection,
retained wallet requirement, Hammer access and usable bag-bomb access. Two existing synthetic
transaction tests cover refusal, poverty/capacity, successful fee/flag, revisit/reload and Granny's
bottle requirement. They do not prove engine presentation or native writer drift absence.

Packet construction, full repository gates and boot checks remain queued
behind Jabu; the post-Jabu slot was requested on `cs-r22`. No gate lock, generation, full gate,
boot or new gameplay result has occurred. Do not report this branch as fully gated or admitted.

### Focused native writer compatibility

The existing three native gift oracles ran serially, `CLAWSHOT_WORKERS=1`, with this branch's
source and `OOT_ROMFS=E:/Games/Hookshot/romfs`, under the focused-test exception:

- `test_dump_each_changed_flow_round_trips_and_differs_only_where_intended`
- `test_dump_every_step_gives_the_new_item_and_given_reads_read_the_flag`
- `test_dump_game_data_list_differs_only_in_the_added_flags`

**3 passed in16.67s.** Medigoron changes exactly3 original nodes; Granny2 plus3 new;
carpet1. SimpleShop changes0 original nodes and adds57 private nodes for the two merchants.
Current native query assertions, serialization and saved-flag allocation apply without writer
drift; no writer fix was necessary. This did not generate a seed/output or acquire a gate lock.

### Identity ruling and source-alias boundary

Claude explicitly approved on2026-11-25: normalize `purchase=True` sources even when assigned
their own native item; ship that with admission and a persisted-repeat regression, not dormant
scaffolding beforehand. PLAY must include a real identity seed, carpet or Granny buying its native
item once, then reload and no second sale. Reserved seed2211250003 is not generated yet.

Do not redirect `Shop_BombchuBundle_01` globally: it already canonically names `Buy Bombchu (10)`
in the actor table. Raw10 donor equivalence belongs to the gift-source matching context, leaving
shop purchase-access semantics intact. Native actor grant proof remains required before release.

### Active candidate prepared outside the shipping worktree

`work/r22-merchants/candidate-src` is a code-only snapshot of874f30a plus the verified tightening
and the fully active proposed admission: all three holds removed there, candidate wallet rules,
native donor actor mappings, gift-local stock matching, and `purchase=True` identity normalization.
The shipping branch retains the three holds and wallet predicates; no disabled admission scaffolding.

The new serialized synthetic identity regression failed before the selector fix with180 ->0 rupees
and two stock grants after reload. After the cause-aimed fix, candidate focused tests report
**9 passed,28 deselected in3.99s**. Native setup without fill confirms all three sources admitted
and mapped; the ordinary shop actor still resolves to `Buy Bombchu (10)`, not raw10.

`work/r22-merchants/build_play_seed.py` is prepared, not executed for generation. Reserved real seeds:
2211250003 constrains all three merchants to their own native items;2211250002 constrains Hammer
and two `Progressive Hookshot` copies (Granny first, carpet second). Normal fill and beatability
must satisfy those constraints. No forced raw plan is substituted for the identity seed.

Three current-template launchers are prepared and pinned to Longshot3.2.0. Native control uses an
explicitly empty mod root and a copied first-adult save. Its actual CLI dry-run succeeded without
starting a game. Swapped's launcher must not run/dry-run before the native control buys the Knife
and saves: it copies that genuinely owned-Knife result once. No inventory or flag edits are used.
The builder's help surface was exercised without generation. Focused candidate/builder formatting
and lint pass (4 files). Full gates, actual seed/mod outputs and Claude's boot checks still await
the requested post-Jabu slot; no play result or release acceptance is claimed.

### Explicit queue hold

The operator selected `keep_queued` in the authorization form. This is not permission to acquire
the lock after Jabu: obtain a new explicit grant before full gates or test-seed generation.
No game boot or admission shipment is authorized. Purchase identity normalization and its
regression remain in the active external candidate; shipping activation still requires the
merchant PLAY results and must land with admission, not separately as dormant scaffolding.

### Line 18 grant and rebuilt play candidate

Claude explicitly superseded the queue hold with relay `claude-18-after-cs22a-0108`, after
line17 released. Authorized: merge main `b98fb9b` with `--no-ff`, rebuild the active external
candidate, full format/lint/synthetic/dump gate, real identity2211250003 and swapped2211250002
builds, then exactly one `bootcheck_when_idle.sh` call per seed. No product admission is authorized.

Shipping merge: `317f5ddaf0e35fb1aa1ba28fc30a9b178587fb6a`. The shipping three holds and both
wallet predicates remain. The original candidate was preserved as
`work/r22-merchants/candidate-src-874f30a-preserved`; `candidate-src` was rebuilt from the merged
shipping tree and the same five-file merchant proposal was reapplied, retaining main's new
hand-over restrictions and tracker/lift changes. The builder records main and the shipping merge.

The exclusive `gate.lock` was acquired for cs22d line18; CIM reported0 players. Runner:
`work/r22-merchants/run_line18.sh`; evidence: `work/r22-merchants/gate-main-b98fb9b/`.
CIM checks precede every stage. Synthetic uses n8/workers4, or n2/workers1 with Kareem's game
running. Dump uses n8/workers3 and must wait while his game runs; both seed builds and boots
also wait. Longshot3.2.0 is pinned; each boot wrapper retains its default quiet-window protection.
No result is claimed until its log reports it. Full gate and play-build results follow below.

Initial candidate gate: format/lint passed; full synthetic reported4804 passed,912 skipped and
one failed in600.42s. Printed failure: `test_gifts_release.py:44` still required all three merchant
locations to stay vanilla. Only the external candidate's existing release contract was corrected:
all three merchants must be selected without holds; both expert galleries remain held. No runtime
fix or shipping contract change was needed. One cause-aimed full gate rerun uses the distinct
`gate-main-b98fb9b-contract-fixed` evidence directory; initial failure logs remain intact.

First full dump:873 passed,1 skipped,5 failed and31 fixture errors in3045.93s. Causes were printed
before any rerun. The old r21/pr41 layered fixture lacks `Pack/Actor/Item_Bomb.pack.zs` now required
by main. A new merchant-owned fixture extends the complete line16 fixture by the three new native
merchant donor packs; source fixtures and the original RomFS are never modified.

The real admission defect was a missing `Dm_SY_Get` preload for Granny's scheduled Talk event.
Native `EventSetting` binds `Npc_Hylia_053_Adult_D_T` to `Npc_Hylia_053_Adult:Talk`; Near and the
separate trade entries do not gain this dependency. The external candidate now adds the preload
when the purchase rewrite is emitted, using the same sorted-union/readback pattern as story gifts.
The registration oracle remains unchanged: no allowance or suppressed gap was added.

Two LACS cases incorrectly prohibited any GameData transform despite merchant identity
normalization; one fairy case pinned the total appended Bool count to2. Candidate contracts now
compare against an identity-normalized baseline: LACS must add no state, while the fairy's played
Din collection flag and both changed grants are still verified. Shipping tests remain unchanged.
The cause-aimed gate uses `gate-main-b98fb9b-native-fixed`; no seed or boot ran before these fixes.

Recovery full gate: format/lint passed; synthetic4805 passed,912 skipped in482.67s. The complete
fixture verified all1300 required files byte-for-byte against RomFS and added only the three
merchant donor packs. Recovery full dump reported908 passed,1 skipped and one failed in4274.79s:
the native flow oracle counted the new analyzed-table transform as another flow (59 versus60).
All registration and NUP/layered-matrix cases passed.

Claude required retaining exhaustive flow coverage: count only
`Event/EventFlow/*.bfevfl.zs`, and give the analyzed table its own oracle. The candidate retains
that flow count and every original per-flow roundtrip/diff check. A separate native case requires
the analyzed-table output to roundtrip and to differ only in `Npc_Hylia_053_Adult_D_T`, whose
SubFlowList must be its original set plus `Dm_SY_Get`. The count-deletion replay was cancelled
before seed generation. The corrected pair runs in `gate-main-b98fb9b-coverage-fixed`, followed by
the authorized seeds and boots only after PASS; runtime source is unchanged from the full gate.

### Harness diagnosis, ordinary generation and corrected play recipe

The initial identity fill exhausted its normal10 attempts before writing output. Claude requested
actual counts before choosing a harness or product fix. The builder passed no `vanilla=` pins:
it constrained destinations with `excluded_items`, leaving the merchants shuffled.

| Actual production setup | Shuffled locations | Pool items | Copies of each native merchant item in pool |
|---|---:|---:|---:|
| Gift off | 178 | 178 | 0 |
| Plain Gift on | 240 | 240 | 1 |
| One-way merchant constraints | 240 | 240 | 1 |

This is a **HARNESS constraint dead end, not pool overflow or double donation**. An instrumented
single fill printed Knife already placed at OGC's Fairy and Bombchus10 at the child rolling Goron,
with Medigoron/carpet still empty and two rupee items left. The builder now reserves requested
items bidirectionally: merchants accept only their requested reward and every other check excludes
those reserved items. It still uses ordinary fill/beatability, with no preplacements, raw writer
plan, post-fill swaps, extra attempts or production fill edits.

Claude's additional ordinary-generation proof passed:20 unconstrained Gift-on production builds,
seeds2211260100–2211260119, one worker, CIM0 before every seed; all240 shuffled checks include all
three merchants, no exhausted seeds. Records: `work/r22-merchants/plain-gift-20.json` and its log.
**A full paired sweep is still required before merchant admission merges.** This20-seed sample
is not a substitute, and no paired sweep is claimed here.

The prepared swapped reward recipe was also invalid: raw Progressive Hookshot copies are
Chest-only in the existing product. The operator selected `legal_major_items` in the form:
keep Hammer at Medigoron; Granny gives Iron Boots and carpet gives Hover Boots, subject to normal
placement checks. The builder and PLAY rows now use that ordinary-equipment recipe; no progressive
NPC feature is added or tested. Production holds and wallet predicates remain unchanged.

The two-way all-three identity reservation exposed a separate normal ammo-safety constraint:
carpet's Bombchus10 assignment is allowed before screens but forbidden by D25's container screen.
Its source rule is only `can_jumpslash`, so the source is reachable without a Bomb Bag. Printed
`pin-screen.log` confirms this is not a larger pool or an overflow, and no screen was bypassed.
Claude explicitly selected the original identity criterion at Granny: identity2211250003 now
reserves only Medigoron's Knife and Granny's Blue Potion, leaving carpet freely shuffled. PLAY
requires Granny's unchanged potion purchase, Save/Continue, an emptied bottle and no repeat sale.
No fill special case, new pre-placement mechanism or production rule change was added.

### Final line18 evidence — READY for PLAY only

Final runtime source is unchanged from the recovery full gate. Format/lint passed. Full synthetic:
4805 passed,912 skipped. Full dump:908 passed,1 skipped plus the obsolete flow-count failure;
the corrected exhaustive-flow case and new analyzed-table case both passed in9.16s after Claude's
coverage ruling. This is full-run-plus-aimed-replay evidence, not a claimed fresh all-green dump
invocation. The20 ordinary production builds above passed with no constraints or exhausted seeds.

Both real constrained test seeds were written using normal fill and beatability:

| Build | Seed | Controlled merchant rewards | Shuffled checks | Spheres | Written resources |
|---|---:|---|---:|---:|---:|
| Identity | 2211250003 | Medigoron Knife; Granny Blue Potion; carpet free | 240 | 28 | 180 |
| Swapped | 2211250002 | Medigoron Hammer; Granny Iron Boots; carpet Hover Boots | 240 | 20 | 180 |

Manifests and source/builder hashes are under `work/r22-merchants/`, outside the repository.
No output, save or source fixture was overwritten. Final run evidence:
`work/r22-merchants/gate-main-b98fb9b-granny-identity/`.

Exactly one `bootcheck_when_idle.sh` call ran per seed, with the default quiet window and pinned
Longshot3.2.0 (source1f0bf123). Each reported crash0, fatal0, save1, modfiles17 and exactly one mod.
Both logged the modded GameDataList and GameAnalyzedEventInfo table. CIM reported0 player games
before each final build and boot stage. The runtime boot checks used scratch users, not the
interactive launchers or the native-control save.

PLAY: `E:/OOTRemake/work/r22-merchants/PLAY.md`. Native wallet control must precede the swapped
launcher's copy of the genuinely owned-Knife save. Identity's persisted-repeat row is Granny.
No gameplay/purchase result is claimed; startup does not prove merchant-area file loading.
All three shipping holds and wallet predicates remain. Admission, purchase identity normalization
and its regression still land together only after PLAY and a full paired sweep; no admission
or dormant implementation was shipped by this turn. The owned lock release is the final handoff.

## Packet-v2 rebuild — copied, funded, independent rows

Claude reported the original first-adult route unplayable: horse/song/trade work, repeated trade
and money farming were not acceptable. `work/r22-merchants/PLAY.md` now supersedes that route
with the PR42-style launcher/start-state/steps/expected-numbers table. Each row starts with a
debug teleport to its merchant area (Granny at noon); no position/clock save edits or route/quest
grind. Five minutes is a target, not a measured gameplay result.

The read-only backup survey first copied2963 progress files and2963 captions, then parsed only
those copies:777 distinct payloads,217 adult. No default-wallet save was strictly past the
Granny sale gate. Completed-trade sources were Giant's Wallet and therefore rejected. The
chosen genuine main first-adult source is the November9 backup's slot01, SHA256
`e63eba9d8173c7c03e1e5338c48ec2dc90cbd2f9b2cad1e487022d5cb46c761c`:
default wallet,76 rupees, genuine Bomb Bag/bombs6, BottleA Bug and BottleB Empty; no Knife,
Hammer, Iron Boots or Hover Boots. Later `main`-named test copies were not needed as source.

Byte-decoding the existing written Granny flow with cached dictionaries showed Event167 is
the Odd Powder handover, not a quest scalar setter. Event3 reads the strict
`SubEvent_GetSwordBigGoron_IsAfter_Step05_01_Exp`; minimum saved step is Step06.
Claude explicitly authorized only `Step_SubEvent_GetSwordBigGoron` Ready398436934 -> Step06567736888
on Granny copies, plus the separately authorized rupees. No Odd Potion/pouch history is
fabricated; the mismatch is expected and PLAY prohibits visiting Biggoron on these copies.

Native A-Granny is first and uses the same edited starting bytes as B/C Granny. Its real
100->0 Blue Potion purchase is required to establish the vanilla post-trade sale; if it fails,
candidate rows are VOID. The three progress baselines are byte-identical, SHA256
`b5d931ba4f07e208ee4fa7eb783864bfcf3bb23b01ff0d292e496052b38ee725`.

Six profiles are materialized in `work/r22-merchants/packet-v2/ingame/`, each equal to its frozen
baseline. Initial field edits/readbacks are exact:

| Profiles | CurrentRupee | Trade enum | Other saved fields |
|---|---|---|---|
| A/B/C Granny | 76 ->100 | Ready398436934 -> Step06567736888 | unchanged |
| A/C Knife | 76 ->200 | Ready unchanged | unchanged |
| B carpet | 76 ->90 | Ready unchanged | unchanged |
| B Medigoron | actual A-Knife result0 ->200, after play | unchanged | genuine Knife and opened walls inherited, never invented |

`fixtures.py` uses existing `clawshot.save`/PR42 `SaveView` and `table_offsets` tools, typed
entry/whole-save delta checks and separate physical copies. No original save, old profile,
age, position, wallet, inventory, bottle or collection flag was edited. B-Medigoron is the only
true dependency: its complete first-launch copy path requires A's actual saved Knife stock1
and rupees0; it cannot be materialized or certified before that result exists.

Seven current-template, pinned Longshot3.2.0 launchers passed actual cmd dry-runs; all existing
profiles stayed unchanged. The new copy-before-parse inspector read back C-Granny as100,
Step06, Odd Powder stock0/unowned, genuine empty bottle and default wallet. An active-game
guard test refused boot staging with players2 and created no scratch; this is an expected
guard result, not a startup test. Receipts: `packet-v2/verification.json`, `dry-runs.json`,
`rows.json`, `launchers.json`, `survey/` and per-row `receipts/*-before.json`, all outside git.

Claude approved dropping below-price rows and same-launcher funded repetition. On B/C's
R mode, after a real purchase/Save/quit, the tool freezes the actual saves/log first and funds
only CurrentRupee0->price on the copied working profile. It never resets a merchant flag or
grants/removes an item. C-Granny saves the genuine potion before funding, then drinks it in
game before the funded revisit. The readback can establish saved state, not visual/live-use
PASS. No-empty-bottle refusal is not claimed by these one-empty-bottle quick rows.

No gate, sweep, seed generation or boot ran during this rebuild. Existing seeds2211250002/3
and mod trees stand. `packet-v2/boot-queue.json` queues fresh fixture/scratch checks for explicit
idle handoff; native controls expect0 mods, B/C exactly1. B-Medigoron's check waits for A's
genuine result. The old seed startup PASS does not certify the new fixtures.

Production holds/wallet predicates remain. Admission still requires actual PLAY and a full
paired sweep; merge current main into this branch when admission resumes, never rebase.

## Native controls played — 2026-11-26

Claude relayed Kareem's A-Granny: "Offers purchase for 100, Blue Potion filled empty bottle,
persists after reload." A-Knife: "Declining works, buying works, equip/swing okay."
While Kareem was moving to B-Medigoron's first visit, only read-only physical snapshots and
small receipt checks ran. No profile/save edits, seeds, boots, gates or heavy work.

| Row | Result | Saved proof against frozen start |
|---|---|---|
| A-Granny | PASS: native sale/reload gate | Slots00/01: rupees100->0; BottleB Empty->Blue Potion; BottleA Bug unchanged; valid bottles2->2. Default wallet capacity200, Medium/Large unowned. Step06 567736888 retained; Odd Potion stock0/unowned. |
| A-Knife | PASS: native default-wallet Knife control | Slots01/02: rupees200->0; Weapon_Sword_Giant stock0->1, IsGet/HavePlayedGetEvent true; Broken Knife absent. Default wallet capacity200, Medium/Large unowned. Bottles and Ready trade step unchanged. |

Copied snapshots are `packet-v2/receipts/A-Granny/1795717225344007700-read-only-inspection/`
and `A-Knife/1795717225651724500-read-only-inspection/`. Both copied logs identify Longshot
3.2.0, their own row profiles and `mods: none` in `native-empty-mods`.
Full slot facts, hashes, checks and tester quotations are in
`packet-v2/receipts/A-Granny-PLAY-20261126.json` and `A-Knife-PLAY-20261126.json`;
the top of PLAY links these receipts.

A-Knife slot00 is an older pre-purchase200/no-Knife save, not a failed purchase. Bomb ammo is
6 initially,7 in slot01 and6 in slot02; these values do not independently prove pickup/use or
wall-opening method. Granny decline was not explicitly reported and is not certified.
Equip/swing and reload execution remain explicitly attributed to Kareem, not inferred from
static saved stock. Native rows have no Clawshot merchant fields; missing fields remain null.

The Step06-only trade edit now has a played vanilla-sale control, validating B/C-Granny's
starting trade state. This is not a B/C transaction/repeat PASS or an admission approval.
Claude reports B-Medigoron ROW_PREPARED from A's real Knife snapshot, with rupees0->200 as its
only fixture change; its first-visit result is still pending. Holds and the full paired-sweep
requirement remain.

## B play receipts and native repeat-service design issue — 2026-11-26

Kareem via Claude: B-Medigoron "working great", but its post-purchase text references Biggoron's
Sword despite not owning it. B-Granny: decline/purchase/Iron Boots work; funded revisit silently
focuses Granny then exits, retaining100 rupees. No additional use/decline detail is inferred
from Medigoron's general report.

Copied B profiles/logs were inspected without editing them. Frozen real-purchase receipts
prove200->0/Hammer1/own Bool true for Medigoron and100->0/Iron Boots1/own Bool true for Granny.
Existing funding receipts change only CurrentRupee0->price. New copied Medigoron slots00/01
retain200, Hammer1, genuine Knife1, Biggoron0 and own Bool true. Granny slots01/02 retain100,
Iron Boots1, an empty bottle and own Bool true; its slot00 is an older pre-purchase save.
Other merchant Bools are false; both retain default200 wallet and two valid bottles.
Both PASS the existing one-time transaction/persisted funded-state contract, not admission.
Granny also has the design hold below.

Runtime proof in the copied logs: exactly one swapped mod, the actual merchant flow, GameData,
analyzed table and merged resource table; Medigoron also loads SimpleShop. Full hashes, slot
facts, exact checks and quotations: `packet-v2/receipts/B-Medigoron-PLAY-20261126.json` and
`B-Granny-PLAY-20261126.json`, linked from PLAY.

### Medigoron ownership gates and message labels

Cached native inputs and the actual B mod were physically copied, then decoded outside git
in `packet-v2/research-20261126/`. English labels/text are native, unchanged in the candidate:
first Biggoron-owned comment Event26/`EventFlowMsg/Npc_Goron_Medigoron_Adult:Talk_08`;
later Event84/`Talk_30`; Event27 alternatives Event20/`Talk_12` (brother's sword aura) and
Event28/`Talk_13`. His copied Event26 talk-history Bool was false before funding and true
after the revisit, while Biggoron stock remains0. The tester did not quote the exact random
follow-up sentence, so it is not pinned more narrowly. These are specifically the native
Biggoron-owned branch, not neutral already-sold text; Knife-owned text is Talk_07/Talk_19.

Native Talk -> Event19 queries actual `Weapon_Sword_Biggoron`: present routes to dialogue/
return, excluding sale regardless of acquisition source. Absent continues via SageOfFire_Check
to Event6/`Weapon_Sword_Giant`; owned Knife also returns without sale. Event7/BrokenGiant only
selects different introductions: both paths converge on price200 and Event11/SimpleShop.
Native SimpleShop removes a broken Knife after a successful replacement purchase.
The GetSwordBigGoron_IsAfterShowBrokenSword_Medigoron_Adult Bool belongs to the separate
ShowBrokenSword_Medigoron_Adult entry's dialogue history, not a quest-step gate on Talk sales.

Actual B Event19 AND Event6 already read the independent merchant collected Bool. Its private
SimpleShop grant bypasses broken-sword removal. Therefore the traced candidate does not need
not-Biggoron logic: retain the existing ownership-neutralizing patch. This is a static proof,
not a Biggoron-owned first-purchase play row. The inaccurate dialogue is a presentation issue.

Published `5dcb21b` still has Medigoron's keep_vanilla and
`is_adult and Progressive_Wallet and can_blast_or_smash`;0.2.9 shipped room tightening only.
Native Biggoron ownership still suppresses the unshuffled Knife shop, as before. This does
not invalidate that tightening or expose a newly admitted progression check in0.2.9.

### Granny repeat shop: product decision required, no code change

Vanilla eligible Talk -> Event3/after-Step05_01 -> Event31 calls Buy_BluePotion on every visit.
Event143/FirstTalk and Event144/IsAfterFirstTalk_MakeBluePotion only select the introduction,
then still offer the purchase. Accept -> funds100/Event11 -> empty bottle/Event15 ->
price100/Event179 -> Event12/GetInEventInBottle_BlueBottleShop; the native wrapper fills
the bottle and charges, then returns to thanks/close. No sale-completion Bool is tested/set.
Thus native Blue Potion purchases repeat with money and an empty bottle.

Patched Buy_BluePotion starts at ClawshotGift155: collected=true/case0 -> NONE/immediate
return; uncollected -> Event143. Caller Event31 also returns. There is NO done-message node
on the collected branch. The silent focus/exit is our added gate, not a native done branch.
Current once-only normalization has removed a vanilla repeatable Blue Potion service.
This is a DESIGN HOLD despite the technical PASS, not approval of the removed service.

cs22d proposes, for maintainers to choose:
- Recommended: one shuffled reward, then a pristine native Blue Potion sale graph on repeats.
  Keep the collected Bool true; never route back into the mutated randomized-gift Event12.
- Explicitly approve one-time shop closure and intentional done dialogue, accepting loss of
  the native repeat service.
- Keep Granny vanilla/held until the decision is settled.

Preserving repeats would also change C-Granny's current no-second-sale expectation and the
persisted-repeat regression's contract: once-only randomized completion versus subsequent
legitimate native potion purchases. Neither code nor tests were changed.
Full external report: `packet-v2/FLOW-REVIEW-20261126.md`. No original dump, spoilers or
placement files were opened; no source save edits, gates, sweeps, seeds, boots or heavy work.

## Final packet receipts: carpet PASS old contract, Granny identity FAIL — 2026-11-26

Before parsing, B-Carpet/C-Granny profiles and logs were physically copied into
`packet-v2/receipts/B-Carpet/1795718965086250000-read-only-inspection/` and
`C-Granny/1795718965403125700-read-only-inspection/`. Supplied screenshots in
`packet-v2/kareem-evidence/` were read and their hashes recorded. No originals were edited.

B-Carpet PASS under the old once-only randomized contract: real purchase90->0, Hover Boots1,
own Bool true; currency-only funding0->90; copied slots01/02 retain90/Hover1/own Bool true,
other merchant Bools false. Kareem declined/bought and obtained Hover Boots. On funded revisit
the visible90 offer remains, but choosing buy cancels without charging/granting. The screenshot
shows that offer and90 wallet. This misleading offer and loss of repeat merchandise require
the approved redesign, not an admission PASS. Older slot00 is pre-purchase.

Kareem approached from Gerudo Fortress and reports crossing needs Longshot/Hover Boots; he
used approved travel noclip. That makes the merchant transaction usable for testing, not an
access/beatability proof. Hover Boots at the carpet in2211250002 is explicitly user-reported;
no seed/spoiler/placement files were opened to look it up.

C-Granny product FAIL: paid100->0 and collected Bool saved true, but BottleA Bug and BottleB
Empty persist while new BottleC Blue Potion becomes valid. Count2->3 instead of native A's2->2:
free bottle/pool duplication. R correctly rejects the changed count before the currency edit.
The new copied progress hash equals the failed-R snapshot exactly; no successful funding
receipt exists. Guard PASS, not a fixture problem. C-Granny is STOPPED; no R retry, loosening,
repair/drinking away the evidence or revisit before redesign. PLAY's old identity replay
instructions were replaced with this stop; `fixtures.py` is unchanged.

Full per-row evidence/checks/quoted observations/load-log references and hashes are
`packet-v2/receipts/B-Carpet-PLAY-20261126.json` and `C-Granny-PLAY-20261126.json`.
Logs prove the one intended mod and actual merchant flow, GameData/analyzed table/merged
resource table (SimpleShop for carpet, Dm_SY_GetInEvent for both).

Claude's design ruling accepts one shuffled reward followed by pristine native repeat sales:
Granny, carpet, and Medigoron's Knife replacements if native repeats after breakage. The
earlier no-second-purchase product assumption is superseded, not the once-only shuffled check.
`packet-v2/REVISED-CONTRACT.md` records success-only completion, native repeat/refusal behavior,
prices, saved-repeat regression changes and new post-fix play-row specifications. No new
launchers are staged. The Blue Potion fix/test needs explicit OK; no implementation now.

### Packet ends with C-Knife PASS

Kareem via Claude: opened Medigoron, declined first, bought the Knife successfully; funded
repeat showed Biggoron-owned dialogue and no repeat sale. Copied profile/log:
`packet-v2/receipts/C-Knife/1795719389557874700-read-only-inspection/`.
Frozen purchase proves200->0 and Knife0->1 with the merchant Bool true. Currency-only funding
restores200; new slots00/01 retain200/Knife1/own Bool true/other merchant Bools false.
Runtime loads prove the identity mod's Medigoron and SimpleShop plus GameData/analyzed table/
merged table. Receipt `C-Knife-PLAY-20261126.json` PASS old contract. This is not a post-redesign
broken-Knife replacement play. Packet v2's seven rows are now complete; no further replay.

### Blue Potion root cause, published exposure and fix proposal (no code)

Candidate admission adds `Blue Potion -> Item_Bottle_BluePotion` in item_actors.toml. Identity
purchase normalization still calls Granny's `_purchase`, which replaces the native
GetInEventInBottle_BlueBottleShop fill wrapper with GetInEvent_NotTurn_NotNpc. That generic
wrapper calls GetPouchContentByActorName_ForGetInEvent: a filled-bottle/container grant, not a
refill of the selected owned bottle. It allocates C while B stays Empty. The native sale uses
PushToSelectedBottle and preserves the valid count; the identity row directly exposed this
semantic mismatch, not a bad fixture.

Published main0.2.9 was checked directly at git object5dcb21b (not assumed from another tree):
- Plain Blue Potion has one vanilla logic location, Granny's sale, and that location is held.
- item_actors has no Blue Potion or Bottle with Blue Potion mapping. The only bottle-container
  mappings are Bottle and Bottle with Milk. Buy Blue Potion is a shop-type logic definition,
  but no native shelf contributes it; Bottle with Blue Potion is also only a logic definition.
- fill.py pools vanilla items from shuffled_locations, which excludes keep_vanilla checks;
  normalize_pool only expands native progressive chains, none a potion/bottle chain.
Thus the erroneous Blue Potion payload cannot reach the generic grant through supported
0.2.9 seed pools/locations. The generic container machinery is reachable and correct for
genuine Bottle/Milk prizes. Native held Granny still refills normally. No shipping hotfix is
established by this candidate bug.

cs22d's proposed fix, requiring explicit OK: preserve Granny's native Blue Potion wrapper
for a plain Blue Potion assignment, with the existing empty-bottle/funds/decline checks and
the private completion flag written only after success. Let the native wrapper charge once;
do not also append the generic replacement's charge. Other randomized prizes remain gifts.
After completion, route to a pristine native sale graph under the approved repeat contract.
Plain potion refill semantics must remain distinct from an intentional new filled-bottle
item at any admitted destination; do not globally redefine bottle-container grants, silently
drop the identity case, or ban its placement instead of fixing it.

Proposed regression updates the existing merchant state oracle, not a callee-name assertion:
synthetic A Bug/B Empty/C invalid,100,uncollected ->0/A Bug/B Blue Potion/C invalid/count2/
collected; no-empty-bottle or insufficient-funds refusal leaves money/pouch/completion unchanged.
Serialize/reload, normally empty the potion, buy native repeat for100 ->0 with count2 and the
same completion Bool; a non-potion first reward must not be repeated. Preserve real Bottle/
Milk container semantics. The current generic path must fail by adding a third valid bottle.
Existing actor-echo rewards assertions are insufficient and must not be re-pinned to that bug.
No code, test changes or test runs were made; the bottle guard remains unchanged.

### Native repeat applicability and carpet rule settled

Native and actual B Npc_Hylia_044_Adult files were physically copied and decoded by the parent
in `packet-v2/research-20261126/`. Both native Event1/Buy-flag cases lead through offer
Event15/Talk_08 or Event16/Talk_09 to Event3/SimpleShopRoot: the flag changes dialogue, not
availability. SimpleShop tests choice/funds/capacity then buys; native Bombchu sales repeat.
Actual B Event3 calls its private entry after the unchanged offer. Collected ClawshotGift171
routes to ClawshotGift159_Event26/Sub_ShopCancel, explaining the misleading offer/cancel.

Native Medigoron repeats replacement Knife purchases: no intact Giant -> Event7/BrokenGiant
(either outcome) ->200 sale; successful native SimpleShop Event25/Event115 consumes the broken
weapon. Native Biggoron/intact-Knife ownership restrictions remain part of post-check fallback,
not blockers for the first shuffled reward. Granny native repeatability was already traced.
Thus Claude's native-repeat ruling applies to all three merchants, not just Granny.

The effective Fortress-side carpet route retains adult+Membership Card at GF Gate Open
(gerudo_fortress.toml13/52), then GF Outside Gate -> Wasteland Near Fortress. The seller is
inside Haunted Wasteland; its incoming exit is
`logic_wasteland_crossing or can_use(Hover_Boots) or can_use(Longshot)`
(haunted_wasteland.toml17; reverse46). Crossing trick defaults false (world/settings.toml197).
The candidate local override is only can_jumpslash (remake/gifts.toml105-108); no remake gate/
crossing override removes the region prerequisite. Existing jumpslash remains unverified.
So Hover Boots parked at the seller cannot bootstrap this default route. An independently
reachable Longshot can cross; the placement alone does not establish deadlock. Noclip play
does not prove access and no seed search/placement inspection was run.

### Consolidated handoff

`work/r22-merchants/packet-v2/RESULTS.md` is the one complete seven-row summary:
A-Granny PASS native sale/reload; A-Knife PASS native wallet/Knife; B-Medigoron, B-Granny,
B-Carpet and C-Knife PASS the old one-time contract; C-Granny FOUND BUG/FAIL, guard PASS/STOP.
It includes the Blue Potion mapping/wrapper root cause, directly checked main0.2.9 exclusion,
refill/semantic regression proposal, confirmed native repeats and carpet access caveats.
PLAY links it and `REVISED-CONTRACT.md`; all old-packet replay instructions are closed.
No code, tests, fixture guard or original saves were changed. No new seeds, gates, sweeps,
boots or heavy work. Packet complete is not admission; wait for explicit code OK, then the
revised regressions/new human rows and required full paired sweep. Merge main, never rebase.

## Approved implementation: refill and native repeats

Claude authorized implementation while idle, merging published main5dcb21b without rebase.
Merge33a6771 completed cleanly. The requested trailer is `Assisted-by: Claude Opus 5.5`.

The writer preserves a pristine native transaction before mutating the randomized caller.
The saved check dispatches through a local native-entry call after completion; its subflow
registration is retained. Granny's unchanged Blue Potion uses the native fill/charge wrapper,
then the success Bool; non-refill first rewards use a generic grant and one explicit fee.
Medigoron's initial ownership reads remain neutralized; the native fallback preserves sword
ownership and BrokenGiant replacement consumption. Carpet repeats no longer enter a hidden
private cancellation gate after its native offer. Original shared native shop consumers remain.
The Granny Talk preload adds Dm_SY_Get only for a non-refill first reward, not the identity.
Purchase identity normalization is now explicit in seed_step.

Focused proof before admission changes:89 tests passed in5.32s (`test_gifts_merchants`,
`test_gifts`, `test_gifts_bottle`, `test_gifts_release`), all OOT variables unset, UI extra,
xdist-n2/CLAWSHOT_WORKERS1. One helper-only oracle self-test was subsequently discarded;
all88 consumer/contract cases remain. A formatter-reported line wrap was corrected without
changing the expression. Eight transforms of already-copied native flow files also round-tripped
(four flows, both Granny reward forms). No live repeat/potion result is inferred from that proof.

Semantic tests now execute serialized synthetic NPC callers across local/shared subflows,
money, saved completion, bottle contents/counts, stock/capacity, and broken-Knife replacement.
They compare completed visits against pristine native behavior rather than pinning a private
callee or reward echo. The flow-transform count assertion remains; the Granny analyzed-table
transform has a dedicated row-only round-trip oracle. No game fixture is stored in the repo.

Claude's subsequent admission/pool ruling is a separate next commit: port frozen v2 admission
data onto this repair, lift holds on the branch only, then replace shuffled Granny's Blue Potion
pool contribution with one existing junk item. cs22d chooses Rupees(5): already mapped ordinary
junk, no progression or bottle capacity. Native Blue Potion survives only an explicit Granny
identity plan pin; it is never a global actor alias. Final focused proof/gate23/play rows/sweep25
must all bind the final admitted SHA, with no merge before new play plus paired sweep PASS.

## Admitted branch pool policy and final focused proof

Claude authorized the frozen-v2 admission port as its own commit after the refill repair:
repair `31d4fd15acb344a708b4b499dc207d1547df7fae`, admission data
`e6fab017f497a4c228fcbb175dea2e8f0ed691eb`. The latter commit records every ported file
and its candidate-src SHA-256; candidate-src remains untouched provenance. Holds are lifted
on this branch only; main still waits for new human play and the full paired sweep.

Under gift/NPC shuffle, Granny contributes Rupees (5), replacing her plain Blue Potion
one-for-one. It is existing mapped junk, no progression or bottle capacity. The shared
logic_spec conversion preserves source data and is idempotent. There is no Blue Potion actor
alias. An explicit keep_vanilla identity pin retains native Blue Potion at Granny alone;
its separate scoped sale step uses the native refill wrapper and composes saved flags with
the ordinary gift step. Real Bottle and Bottle with Milk prizes remain container grants.

Final focused proof:75 passed in34.29s (`test_gifts_merchants`, `test_gifts_fill`,
`test_gifts_release`, `test_world_remake_adult_goron_city`), all OOT variables unset,
UI extra, xdist-n2/CLAWSHOT_WORKERS1. Consumer cases cover pool-count conservation/no Blue
Potion across ordinary seeds, identity-only refill, serialized repeat sales, funds/capacity/
decline gates, bottle counts and Medigoron's native replacement restrictions. The wallet
contract now reflects the played default-wallet sale; LACS/Great Fairy flag oracles compare
against the normalized identity-merchant baseline rather than asserting no GameData change.
Changed Python files pass the narrow format check. Dump/full-gate and live proof are not
claimed here. Gate23, fresh play rows and sweep25 must bind the final admitted commit.

## Line23 test-infrastructure recovery — 2026-11-26

The first gate on3967848c7f stopped on the old shopkeeper-only spec equality. Per Claude,
the test was narrowed, not deleted: preserve unchanged behavior without Gift/NPC, require
the whole shuffled spec to equal shopkeeper_spec except Granny's Rupees (5), check the
tracker's actual vanilla conversion, and cover keep_vanilla retaining native Blue Potion.
Test-only child `f06f2362bd58135bcee7cfb790e2e870904dce8d` passed19 focused cases.

The full restart onf06 passed format/lint and4835 synthetic cases, then failed only
`test_tracker_logic_ui.py::test_age_control_defaults_to_either`: tracker-render through
`C:/Program Files/Volta/node.EXE` exceeded its10-second subprocess deadline under parallel
load (-n8, BelowNormal). Claude classified this as test infrastructure, not the merchant
change; the case passed in the396 run and cs22c's line22 gate.

Claude required five isolated runs without xdist, with the same shim/deadline. All passed:
pytest-reported seconds9.37,0.32,8.83,0.32,0.32; full-command wall seconds
10.332,1.074,9.568,1.052,1.055. Exact outputs and commands are outside the repo in
`work/r22-merchants/tracker-volta-alone-{1..5}.log` and
`tracker-volta-alone-results.json`. No test timeout, Node resolution or product code changed.

Approved recovery: retain same-SHA f06 format/lint results; rerun only synthetic, then dump,
under the retained line23 lock. Play builds and sweep still bind f06 and wait for the
complete gate. Candidate infrastructure fixes are deferred to main: resolve the real
node.exe once per session, or allow that subprocess more time. Neither lands on this branch.

## Native registration coverage-pair correction

The f06 recovery passed4836 synthetic cases, then native910 passed/1 skipped/1 failed
in3309.73s. The broad event-registration harness moved Bombchus (5) from a scrub to
KF Shop Item2. Its pair selector used allowed() on an unscreened world; production
from_placements correctly applied the D25 container/tier screens and rejected that move.

cs22d corrected only the harness: construct with_screens from the generated shuffled pool
and fixed placements before selecting either side of the pair. Fill rules, the pool-preserving
swap, ordinary replay validation, all writer/dependency/debt assertions and the Dampé-cycle
check remain. Focused native broad recipe passed1 in130.81s, BelowNormal/n2/workers1;
the modified file passes its format check. No whitelist, location or ammo special case.

Test-only child `c5625a0118fe82266d06ebab3bb88ae92799876a` is the new gate/play/sweep
candidate; production code is unchanged. Full gate restarts on that clean frozen checkout.
The first temporary f06 tier-recovery launch used the wrong cwd; its own process tree was
stopped, its log marked ABORTED/not gate evidence, and the driver corrected before the
accepted f06 recovery. All failed and aborted logs remain outside the repository.

## Line23 complete on c5625a0118 — fresh v3 packet boot-only ready

Exact frozen `c5625a0118fe82266d06ebab3bb88ae92799876a` passed the full restart:
format613 clean, lintPASS, synthetic4836 passed/914 skipped in439.70s, native911 passed/
1 skipped in4034.11s. Detached BelowNormal, n8/workers4 synthetic with all OOT variables
unset and the UI extra, then n8/workers3 with all three native layers. No Node/timeout fix
or verification waiver is included in this final gate. Logs: `work/r22-merchants/gate23-c5625a0118`.

Both fresh constrained seeds were built directly from that same clean checkout:
2211250003 identity (Medigoron Giant's Knife; Granny explicit native-refill pin; carpet
unpinned), and2211250002 swapped. Binding verified source/receipt SHA, the composed saved
flags, native refill calls and no plain-Blue new-container alias. All four actual launchers
passed dry-run with profiles byte-identical; exactly one fresh-scratch Longshot3.2.0 boot
per row passed with one bound mod, its GameDataList loaded, mounted scratch save and no
crash/fatal lines. These are startup proofs only, not merchant area-load or transaction play.

`work/r22-merchants/packet-v3/PLAY.md` is ready for Granny-Identity (the fresh C-Granny
case), Granny-Swapped, Carpet-Swapped and Medigoron-Swapped. Every copied profile matches
its frozen baseline. Granny/carpet payloads are byte-identical to their source copies;
Medigoron has exactly one changed Int word: CurrentRupee0->200 at byte offset84164.
No position, clock, flag or inventory edits. Original saves and all packet-v2/failed-C
evidence remain untouched. Build, binding, edit, dry-run and per-row boot receipts are in
packet-v3; driver proof: `play23-c5625a0118/status.json`.

Human play and admission remain pending. Line25 regenerates the full paired sweep on
c5625a0118, Gift-on versus Gift-off, only after line24's explicit release. The updated
queue inserts cs22c's22b after this line23 release and before24. No main merge is authorized.

## Line25 complete — paired merchant sweep on c5625a0118

Started only after cs22c's explicit 22:52 line24 release. The frozen source remained
`c5625a0118fe82266d06ebab3bb88ae92799876a`, not the later documentation-only HEAD.
Detached BelowNormal was asserted as `0x4000`; six workers, one clawshot worker each.
Player count was zero at preflight and every stage boundary. Driver finished at 23:06
with exit0 and stage `paired-sweep-complete`.

| Recipe | Pairs | Gift-off first-attempt failures / attempts | Gift-on first-attempt failures / attempts |
|---|---:|---:|---:|
| Broad | 200 | 1 / 201 | 0 / 200 |
| Defaults | 50 | 0 / 50 | 0 / 50 |
| Recommended | 50 | 0 / 50 | 1 / 51 |

Both arms completed every seed: no exhausted seeds or rejected oracle results. Identical
seed lists and non-shuffle input settings were checked. All three merchants were selected
only in Gift-on; its ordinary pool contained no plain Blue Potion. Pool conservation and
tier checks passed, alongside the generator's goal/age/return verification. Placement and
sphere digests differed for every pair; no placements or spoilers were published.

Evidence: `work/r22-merchants/line25-c5625a0118/{status,comparison}.json`, driver/stage
logs and each arm's settings, seed list and digest-only rows/results. The saved line24
release is alongside them. This completes the ordered automated work; the four v3 human
merchant transactions, persisted repeats and explicit admission decision remain pending.
No live merchant-play result, admission approval or main merge is claimed.

## v3 human play — three repeats confirmed; Medigoron early break approved

Kareem reported declining, buying the shuffled/native identity reward, using R, buying the
native repeat and seeing the repeat offer continue for Granny-Identity, Granny-Swapped
and Carpet-Swapped. With the game closed, `fixtures.py inspect` copied every row's saves
and runtime log before parsing. Latest slots02/03 classify `native_repeat` without failures;
the saved check Bool is true and the bound merchant flow/GameDataList load checks pass.

| Row | First purchase rupees | Repeat rupees | Saved inventory/bottle evidence |
|---|---|---|---|
| Granny-Identity | 100→0 | 100→0 | BottleB Blue Potion; two valid bottles throughout |
| Granny-Swapped | 100→0 | 100→0 | Iron Boots stock1 retained; BottleB Empty→Blue Potion; two bottles |
| Carpet-Swapped | 90→0 | 90→0 | Hover Boots stock1 retained; Bombchu stock0→10 |

Medigoron: Kareem declined and bought Hammer, then broke the genuine Knife normally
before quitting, and saw the replacement Knife offered for200 with Broken Knife in hand.
Claude ruled this order deviation benign; intact-Knife refusal is **UNPLAYED/skipped,
native, not a blocker**. The first operation preserved saves and log in packet-v3
`receipts/Medigoron-Swapped/1795779196332001200-approved-early-knife-break-preserved`.
Copied slot00 contains Hammer1/intact Knife1/rupees0; newer slot01 contains Hammer1,
Knife stock0, Broken Knife stock1, equipped Broken Knife, rupees0, saved check true.
The tracked actor delta is exactly Hammer plus the Knife pair; bottles, wallet and other
merchant checks pass the original purchase guards. Raw scalar/vector drift is preserved
separately, including movement, equipment, Navi and unnamed counter fields; unnamed
fields are not assigned invented meanings.

The original error included Item_Hammer because it prints the entire actor delta, even
though it tests that delta minus the allowed reward. The extra Knife pair caused refusal.
No game patch or general purchase guard was relaxed. The external v3 helper accepts this
exception only for Medigoron, the exact preserved slot SHA, the exact Knife-pair-only
failure and the genuine broken stock values. Approval: `Medigoron-Swapped-approved-early-break.json`.

The launcher's actual `fund_repeat` handler passed on disposable profile copies:
`receipts/R-handler-proof-1795779382031664300`. Each of the two purchased slots changes
only one CurrentRupee word0→200; byte prefixes/suffixes outside that word are identical.
The actual prepared-profile `ensure` also passed. Playable saves remain untouched and R
unconsumed; Kareem was told to run the same launcher, type R, continue the broken-Knife
save and buy the replacement. R records the real edit automatically, linked to its approval.
No agent launched the game. Medigoron's replacement purchase remains pending.
