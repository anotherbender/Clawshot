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
