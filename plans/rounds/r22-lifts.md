# Round 22: cheap placement lifts (cs22g)

Branch `r22/lifts`, base/main `4f4ff42` (0.2.7 + round records). Added mid-round with Kareem's OK,
2026-11-24. Model `openai-codex/gpt-6.1-sol`. Audit scope: `r21-placement-audit.md` section 5 row 2;
section 3 rows 6, 7, 12, 14. Research/staged output only under `E:/OOTRemake/work/r22-lifts/`.

## Acceptance boundaries

- Each unplayed lift stays held in the merge head. A passed item gets its own final commit citing Kareem's
  Longshot 3.2.0 evidence. Failures retain their hold and recorded reason. No new setting, no version bump.
- Token fixed-capacity admission now cites both individual plays: Nut native30 on rc.3 and Stick native20
  on R22 packet05b, including uncollected-drop recovery, one pickup and persistence as child.
  Each member still passes the production native structural validator.
- Chest and hand-over packets are private diagnostics, not playable/goal-certified solo seeds.
- Controls come from main `4f4ff42`. Longshot 3.2.0 only. No agent starts the game or writes to an installed
  game, a played seed or an original save. Source backups remain read-only.

## Evidence and staging investigation

Read the required architecture/world/game-data/round records, the placement audit, round-21 outcome and PR #40
record, Kareem's track-relevant 0.2.6 notes (not its seed spoiler), and the public-docs-only feature comparison.
GameData reference: `work/refs/sloperina-FINDINGS.md`, sections 1, 2, 5.7 (GPL documentation, facts only);
no implementation copied. Chest collection uses `IsTreasureBoxOpen.<Hash>`, not raw actor flags.

`probe_saves.py` read natural adult backups and printed all candidate item flags and named chest states.
`2026-11-09_1347-main-after-forest`, manual save: adult, Bow owned; all six permanent gift items under test
unowned, medium Nut/Stick bags unowned, magic0, six hearts, wallet capacity500. Eight easy overworld chests
are closed; no save edit needed. The chest packet uses these rather than resetting Mido/Deku chests.
The probe's first numeric-field call used nonexistent `Save.int`; printed AttributeError, then corrected
only that accessor to `int_value` and printed the values. Missing numeric names are not treated as zero.

## Staged packet A: eight gift-only chest actors

**PLAYED PASS: Kareem, Longshot 3.2.0.** All eight now have reported model/text/usability passes and
saved collection/load corroboration. Farore was confirmed separately in the correct Crater grotto after
resolving a Trail/Crater location mix-up (typed receipts below). Private seed `922701`,
main control built from `4f4ff42`, both arms use Chest-only `CS1` and the same base placements; only the eight
target contents differ. `placements=` is a diagnostic, not a solo goal proof. Gift shuffle is deliberately
off in the private packet. Builders did not relax production policy; the successor adds eight sourced
Chest-only receipts after play. Other chests remain randomized: open only the listed checks.

Launchers: `E:/OOTRemake/work/r22-lifts/ingame/01 - chest vanilla control.bat`, then
`02 - eight chest items candidate.bat`, both **Longshot 3.2.0**. Separate copies of the same natural adult
manual save during the Forest quest (`2026-11-09_1347-main-after-forest`, six hearts/Bow, no save edits).
Baseline: magic0, wallet148/500, arrows27, bombs10; BottleA Bug and BottleB Empty, C-E unowned;
all six permanent test items unowned and every target's named chest-open flag false.

**Estimate: 28 minutes total** (control8 + candidate20; target25, not timed). Each launcher is below30.
Teleport to each area's normal entrance and walk to the chest; clock is allowed. No inventory, flag,
age-change or invincibility cheats. For maps/minimaps always enter through the actual entrance.
Exit the runtime between arms. The candidate's existing empty bottle can buy Green Potion for magic refill;
do not count that bottle or a refill as the new Bottle reward.

For each row record separately: the rising model (including wrong/invisible/stand-in), correct get window,
the usable grant, and ownership/use after Save and Continue. A text-only success is not a pass. Leave/re-enter
the area and verify the chest stays open; after all pickups Save, quit and Continue, then repeat the use checks.
Do not kill the watchtower Skulltula before checking the Echo Gem.

| Item / chest (native model) | Main control content | Model/get window | Immediate ownership and use | After Save and Continue | Result |
|---|---|---|---|---|---|
| Light Arrows — left-end Graveyard grave, nearest row leftmost when facing out from Royal Tomb (`A_02`, large) | Piece of Heart | Record rising actor and Light Arrows name/text | Owned, magic appears, select with Bow and fire a light shot; arrow stock falls | Still owned; select/fire another light shot | PASS per Kareem; saved ownership/open chest/load corroborated |
| Nayru's Love — DMT cracked-wall chest between Kakariko and DC (`A_01`, small) | Scrub Business Seed | Record model (native spells can share a model) and Nayru get text | Owned, cast visible protective barrier with magic cost; wait for it to expire before damage comparison | Still owned; cast again | PASS per Kareem; saved ownership/open chest/load corroborated |
| Farore's Wind — DMC upper-rim rock grotto (`A_01`, small) | Scrub Business Seed | Record model and Farore get text | Owned; **walk into Forest Temple**, cast to set a return point, move away and cast Return successfully | Still owned; set/return again inside dungeon (not a promised persisted warp point) | PASS on correct Crater play; chest open/IsGet true/stock1 and own override saved |
| Stone of Agony / Echo Gem — GC top-floor maze, blast middle corridor into Gossip Stone pocket, chest ahead (`A_01`, small) | Rupees (5) | Record Gem model and get text | Owned/equippable; at night approach **uncollected Kakariko watchtower Skulltula** and observe rumble/indicator | Gem still owned/equipped; repeat cue at same uncollected source | PASS per Kareem; saved ownership/open chest/load corroborated |
| Double Defense — same GC pocket, chest right of previous (`A_01`, small) | Rupees (5) | Record model and halved-damage get text | Owned, MaxLife unchanged; before opening record one stationary unshielded bomb blast, then same blast afterwards with Nayru expired; loss should halve | Still owned, MaxLife unchanged; comparable blast still reduced | PASS per Kareem; saved ownership/open chest/load, MaxLife24 unchanged |
| Biggoron's Sword — ZR uncovered high-ground grotto just upstream of first bridge (`A_01`, small) | Scrub Business Seed | Record sword model and correct get text | Adult sword owned, equip and swing; not Giant's Knife/broken knife | Still equipped/owned and swings | PASS per Kareem; saved ownership/open chest/load corroborated |
| Bottle — HF Storms-cover grotto at foot of Kakariko steps, beat two ReDeads (`A_01_NoBake`, small) | Rupees (50) | Record bottle model and new-bottle get text | **Third bottle** added, original Bug/Empty slots retained; select new slot, catch/release bugs or fill/empty water | Third slot still owned and can fill/empty; original slots retained | PASS per Kareem; BottleC added, original A/B retained, chest/load corroborated |
| Rupees (200) — SFM entrance Storms-cover grotto, beat two Wolfos (`A_01_NoBake`, small) | Rupees (50) | Record gold model and 200-rupee get text | Note wallet immediately before/after, exactly+200 within500; no other pickup during count | Wallet retained (allow only recorded spending); chest open, no second+200 | PASS per Kareem; saved154→354 and chest closed→open |

Required loading evidence: candidate `mods: Banc/<area>/<...> <- <private candidate path>` for each of the
eight areas/files in `packet-readback.json`, plus its resource table and relevant get flows. Control proves
the same chests grant the native column. Log lives in each launcher's private `user-<name>/longshot_log.txt`.
Report each row PASS/FAIL and reason; a failure does not admit the actor or block independently passing rows.

## Staged packet B: fixed capacities

Private diagnostic seed `922702`; **Longshot 3.2.0**, natural **Forest Complete adult autosave**, seven
hearts, from the same backup folder as A; no save edits. **Use replacement launchers03b/04b/05b only:**
`03b - capacity vanilla control natural return.bat`, `04b - capacity chest candidate natural return.bat`,
`05b - Stick Token candidate natural return.bat` under `ingame/`. **Estimate: 15 minutes total**
(control4 + chests6 + Token5). Each is an independent profile: the Stick chest cannot mask the Token grant.
Native capacity10 sticks/20 nuts; medium items absent. Field lone-tree source pair is uncollected.

| Check | Control | Candidate / expected checks | Result |
|---|---|---|---|
| Graveyard left-end grave large chest, Hash `9622128545943056087` | Piece of Heart; cap10 retained | `Item_StickBag_Medium`: model/window, medium item owned and native20 cap/refill; return to child **naturally at the pedestal**, select/use a Stick. After Save/Continue cap20/item/use persist, chest open | PASS per Kareem; cap20/medium owned, adult and child saved |
| ZR open-grotto small chest, Hash `8838426083116998768` | Scrub Business Seed; cap20 retained | `Item_NutBag_Medium`: model/window, medium item owned and native30 cap/refill; throw a Nut. After Save/Continue cap30/item/use persist, chest open | PASS report; saved Nut cap30/medium owned, not a Bullet Bag upgrade |
| HF lone tree near forest entrance, source `2177746409373494991` | Roll, kill with sword, native token:18→19; no cap upgrade | Stick native20 instead, token18 unchanged; before pickup leave/re-enter to recover drop, collect, use as natural child, Save/Continue; medium item/cap20 retained and source does not respawn | PASS: clarified one pickup after uncollected-drop recovery; cap20/token18/collection pair saved |

Loading proof: Graveyard Adult Static, ZoraRiver Adult Dynamic; for Token, HyruleField Adult Static,
generated Stick-capacity pickup pack, all three RSDB tables and resource table. `packet-resources.json`
lists exact paths. The Token writer retains native source/collection mechanics and passes its existing
native structural guard. This is not a newly invented grant path.

## Staged packet C: ocarinas at the Market gallery hand-over

Private diagnostic seed `922703`, **Longshot 3.2.0**. This is the original crashing hand-over, first:
Market child Shooting Gallery. No other hand-over is certified by this packet. Native crash evidence remains
`r11-ocarina.md` Reported failure / Native crash-address correlation: Ocarina of Time crashed on
Hookshot 2.0.14 in German and English; Fairy was excluded by analogy, not by a played failure.

**Original control boundary:** at staging, PR40 ran only for an ocarina placed in a chest. A single
PR40-active PASS could not justify native-pack hand-overs. Each instrument therefore had active and
native-pack arms, not merely a cosmetic control. Active arms include an unvisited, already-open Mido
far-right chest holding Time, activating the exact production pack/ActorInfo transform without granting
anything there. Native arms leave it vanilla. **Do not visit/open other chests or take Saria's gift.**
The successor now enforces PR40 independently of an ocarina chest.

The builder clears `hand_over.excluded_items` **in memory only**, proves both instruments fail `allowed`
at the gallery under main and pass the candidate policy, then uses the production gift planner, all gallery
tier branches and the production ocarina receipt compiler. No normal get window is appended to the running
scene. The main control normalizes the gallery to its existing fixed-medium capacity prize. These are
minimal writer diagnostics, not normal fills or goal-certified seeds; public policy was unchanged at staging.

All five profiles copy the natural child save just before Saria's farewell, from
`2026-11-09_1558-seed8-gatehouse-crash`. It has neither instrument (both IsGet=false, stock0), an empty
`PlayerStatus.EquipOcarina`, the child-gallery first-win flag=false, and78 rupees. D-pad is enabled, all12
learned-song flags are false, and the remote activation chest's named open flag=true. No save edit.
On Continue **immediately teleport to Market before walking across the forest bridge**: taking Saria's
Fairy Ocarina first invalidates the first-instrument test.

**Estimate: 20 minutes total**, five short launchers, all below30; English first. Each win needs the normal
gallery fee; its own fresh copy has78 rupees. Teleport/clock only; never a debug age/inventory/flag cheat.

| Launcher in `E:/OOTRemake/work/r22-lifts/ingame/` | Expected reward / pack state | Result |
|---|---|---|
| `06 - gallery main native reward control.bat` | Main's fixed-medium Bullet Bag40; PR40 active through the remote chest. Gallery returns control normally | NOT PLAYED |
| `07 - gallery Time PR40 active.bat` | Ocarina of Time; chest-model packs and ActorInfo active | PLAYED PASS; saved Time stock1/active Time, correct model/text |
| `08 - gallery Fairy PR40 active.bat` | Fairy Ocarina; chest-model packs and ActorInfo active | PLAYED PASS; saved Fairy stock1/active Fairy, correct model/text |
| `09 - gallery Time native packs.bat` | Ocarina of Time; original dump packs/ActorInfo | PLAYED CRASH during hand-over; null read at guest0x270; unchanged rerun forbidden |
| `10 - gallery Fairy native packs.bat` | Fairy Ocarina; original dump packs/ActorInfo | NOT PLAYED; unnecessary for Claude-approved PR40-enforced path |

For each candidate: win, record hand-over model and get window, no crash/freeze, movement restored; pause
inventory owns the actual instrument and D-pad plays audible manual notes (this checkpoint has no learned
songs; do not claim a learned-song pass). **Do not count IsGet alone:**
read `PlayerStatus.EquipOcarina` in the private saved copy and observe the instrument played. Leave/re-enter,
verify the first prize does not repeat, Save/quit/Continue, verify the instrument remains playable and the
first prize remains consumed. On failure stop that arm, preserve its log, report exactly where it failed;
do not rerun unchanged. Any German follow-up is separate evidence, not assumed from English.

Loading proof: all arms load `Event/EventFlow/MiniGame_HitTarget.bfevfl.zs` from their private mod and the
production receipt flows/resource table. Active arms additionally load both ocarina packs and ActorInfo;
native arms supply neither pack nor ActorInfo. `ocarina-packet.json` lists exact resources.
An item is not admitted to hand-overs until its necessary arms pass.

**Approved by Claude after07/08 PASS and09 crash:** the successor must enforce the PR40 packs and
ActorInfo for ocarina hand-overs in code, with regression coverage; native-pack hand-over output is
forbidden. Removing the exclusions without that requirement is not approved. Arm10 is unnecessary.

## Fairy Ocarina at Skulltulas after PR #40

**Hold still justified for today's production path; no lift and no played Fairy Token result.**
The old blanket phrase “Item_ ocarinas lack AnimationRef” is stale for PR40-generated packs, but remains
true of the unmodified dump packs actually read by the Token composer. There is still no native
`Obj_Ocarina_Fairy` world donor. Main composes Tokens at `patch/__init__.py:172-180` from `tokens.Romfs`
before appending `getitem.ocarina_changes` at274-277. `tokens.compose` requires the donor AnimationRef
and `_check_pickup` verifies it; it does not consume the generated chest pack. The existing real-dump
test `test_fairy_ocarina_is_excluded_for_want_of_its_own_animation` describes that native donor boundary.
`token_rewards.toml` now states this narrower reason. PR40 makes a composed donor a research possibility
[INFERENCE], not an existing or played Token grant.

## Packet time and merge boundary

Total estimate **63 minutes**, split A28 / B15 / C20 across ten launchers (longest20). These are estimates,
not timed play. A's target was25; its full usability/reload/control checks are estimated at28 rather than
silently omitting them. Kareem can batch A, B and C independently. No original save or installed game file
changes. Each new chest/hand-over admission is a separate post-play change; the successor scope and its
remaining verification are recorded below.

Staging choices proposed by **cs22g, 2026-11-24**: natural adult checkpoints rather than reopening chests
in a save; independent capacity profiles; both conditional PR40 states before any global hand-over lift.
These do not change product policy.

## Verification so far

- Focused synthetic: `CLAWSHOT_WORKERS=1 uv run --with pytest-xdist pytest tests/test_scrub_seed.py
  tests/test_scrubs.py tests/test_settings_songs.py tests/test_generate_tokens.py -n 2 -q` — **174 passed**.
- `build_chests.py`: main control106 resources, candidate115; `build_capacities.py`: control4, chests5,
  Token11. First capacity lookup printed StopIteration; printed source definition showed the remake-only
  name in `name`, not `oot_randomizer_name`; fixed lookup to verified Hash and reran once.
- `verify_packets.py`: all eight chest grants and both capacity grants read back at their original Hashes,
  both ages; controls read back native contents; every selected chest closed, capacity items absent,
  source pair unset, wallet room and third bottle room verified. `packet-readback.json`.
- `make_launchers.py`: all five launchers cmd dry-run exit0, stable/v3.2.0/bin/longshot.exe, one private mod
  each, `save/` layout, HOS_FS_OVERLAY unset, source backup hashes unchanged. `launcher-dry-runs.json`.
- Gallery packet: control/active arms10 resources each, native arms7; both original reward branches checked.
  All five gallery launchers cmd dry-run exit0, stable3.2.0, private `save/`, original backup hashes unchanged.
- First native focused run:5 passed and one broad coverage failure, solely the pinned scrub-shield writer
  absent after placements moved. No new registration gap. Claude's priority correction (2026-11-24):
  no further seed searches; deterministic compatible shield/scrub swap in the broad test recipe instead.
  The first swap rebuild covered the shield but external placements intentionally dropped hints, losing
  `patch.text`'s GossipStone writer; its printed writer-set failure led to preserving the original generated
  hint selection through the validated rebuild. No assertion/allowance was weakened. Final test-only base
  commit **`5bc5577369d429d426dc2059461918e41b5c5302`** (all earlier own intermediate heads superseded):
  four unchanged dump cases passed in the whole-file run; corrected broad isolated **1 passed in243.23s**,
  `-n 2`, workers1, no lock (Claude's explicit one-file exception). Formatter/lint pass; the last change
  was formatter-required whitespace only. Posted **READY (merge)** for this test-only commit.
- Explicit-main provenance: rebuilt all three controls using imports from
  `E:/OOTRemake/Clawshot/src` at main **`5bc5577369d429d426dc2059461918e41b5c5302`** into fresh
  `work/r22-lifts/main-control-provenance/` folders. All staged RomFS bytes match those explicit-main
  builds: chest106, capacity4, gallery10 files. No staged arm/profile was rewritten.
  `main-control-provenance.json` records source path, head and counts.
- Capacity checkpoint correction: the backup folder's manual save is still ForestStep4030607474, not
  Complete. This is safe for adult chest packet A but cannot do B's natural child return. Replaced only
  B's launchers with fresh03b/04b/05b profiles using the natural autosave: ForestStep=`Complete`1275749364,
  adult, seven hearts, caps10/20, both medium bags absent, both chests closed, lone-tree pair unset.
  All three replacement cmd dry-runs exit0; original backup hashes unchanged; same immutable mods.
  `capacity-baseline-v2.json`. Old03/04/05 profiles are superseded; no staged folder/save was rewritten.
- Rebase onto main **`5bc5577`** after Claude's MAIN MOVED: already up to date (the exact test-only base
  is this branch's ancestor). Required post-rebase rerun: focused synthetic **174 passed in30.84s**;
  full `tests/test_event_registration.py -m dump -n 2` **5 passed in319.82s**, workers1. No seed re-pin.
- No game was started. Boot checks are Claude's. No play pass inferred from writer/readback/dry-run.

## Ordered gate and sweep: PASS

Tested source head **`32994910938709151649c9c95fdfa65edf2256ca`**, unchanged throughout the gate.
Per Claude, later MAIN MOVED notices did not trigger a rebase/refreeze; the comparison remains against
**`5bc5577369d429d426dc2059461918e41b5c5302`**. No product changes followed the focused run.

- `uv run ruff format --check` and `uv run ruff check`: PASS.
- Synthetic, with `OOT_ROMFS`, `OOT_NUP`, `OOT_DUMP` unset: `CLAWSHOT_WORKERS=4 uv run --with
  pytest-xdist pytest -n 8` — **4403 passed, 839 skipped, 24 warnings in504.64s**.
- Dump: `CLAWSHOT_WORKERS=3 uv run --with pytest-xdist pytest -m dump -n 8` — **836 passed,
  24 warnings in3405.24s**. Standard `OOT_ROMFS`/`OOT_NUP`; read-only
  `OOT_DUMP=E:/OOTRemake/work/rounds/r19/sword-layered-dump`. No new working-set file required.
- Game checked at every heavy-stage start; both completed suites used eight workers. Sweeps used six
  workers. cs22g ran no overlapping heavy job, started no game, and wrote no source save or game directory.

**Paired350/arm: all accepted, zero exhausted.** Reused cs22b's published standard300 main arm from
`work/rounds/r22/main-5bc5577-sweep/` after reading its README and validating revision, exact seed
pairs and input settings. Only the additional50 main seeds ran locally, importing a pinned source
export of5bc5577. Broad seeds22220000–22220199; all other cohorts22220000–22220049.
Binding recipe: `Settings(shuffle=('Chest','Scrub','Token'))`.

| Cohort | Seeds per arm | Placement digests identical | Sphere digests identical | First-try failures candidate/main | Candidate capacity placements at Token |
| --- | ---: | ---: | ---: | ---: | ---: |
| Broad | 200 | 0 | 0 | 0/0 | 389 |
| Defaults | 50 | 50 | 50 | 1/1 | 0 |
| Recommended | 50 | 50 | 50 | 2/2 | 0 |
| Capacity-binding | 50 | 0 | 0 | 2/3 | 95 |

Binding main has **0 Token /100 Scrub** capacity placements; candidate has **95 Token /5 Scrub**.
These are modeled placements, not new in-game grant evidence. All first-try failures recovered through
the existing generator retry path. Full per-seed placement/sphere hashes and counts, without placements
or spoiler contents: `work/r22-lifts/sweep-{candidate,main-binding}.json`,
`sweep-{candidate,main-binding}-summary.json`, and `sweep-comparison.json`.

cs22g's harness-only corrections, with printed causes retained outside the repository:

- The first effective-CS1 assertion failed before filling (`attempts=0`): the intended admission itself
  derives `item_location_types` entries changing only Stick/Nut `('Scrub',)` to `('Scrub','Token')`.
  The next parent preflight showed Recommended has Token off and must retain Scrub-only. The final
  predicate permits exactly those two derived changes only with Token enabled; all other effective
  fields and every input setting/seed pair remain equal. Both recorded payloads passed before resuming.
  Preparation now happens before the worker pool, so a setup error cannot masquerade as exhausted seeds.
  `sweep-candidate-setup-failure.log` and `sweep-recommended-setup-failure.log` preserve both causes.
- Synthetic environment isolation follows cs21i's reported OOT-variable contamination; the passed
  synthetic stage was not repeated. Failed-mkdir fault injection also caught `set -e`'s `&&` exception:
  splitting acquisition into sequential commands proved immediate exit73 instead of fall-through92,
  without touching a real lock or starting tests/seeds.
- The successful resume did not execute its EXIT cleanup. After observing the completed dump result,
  cs22g checked the exact own owner record, removed only that lock, and posted **LOCK RELEASED at00:37**.
  Submitted `report_issue` for the missing successful EXIT trap. No verification rerun was needed.

Full-gate logs remain under `work/r22-lifts/gate-{format,lint,synthetic,dump}.log`; no game data or logs
were added to this repository. This receipt is documentation only above the tested source head.
`resume_gate.sh` is retained outside the repository as execution evidence for that tooling report.

## Frozen successor and remaining gates

The earlier merge head8488bdc56c and tested source3299491 remain the historical Token-only receipt.
**FROZEN test-only successor `461f68d67318190265284fd9a6460b406e615e69`** of product source
`da1fb784`. All eight scoped chest lifts, Stick/Nut chest capacities and PR40-enforced ocarina hand-overs
are unchanged. No version bump or rebase. Snapshot: `work/r22-lifts/successor-src-461f68d6/`.

Queue13a is **PASS**: full synthetic and native production-output proof, below; lock released18:28.
Not READY until queue14 after shops13: format/lint, fresh paired350 and full dump. Claude approved reusing
the same-SHA13a full-synthetic receipt. Every seed-capable stage requires game closed. Fairy-at-Token held.

## Typed played receipts and corrected Farore chronology

Reporter: **Kareem**, forwarded/clarified by **Claude**, Longshot3.2.0. Read-only evidence copied to
`work/r22-lifts/played-20261125-133632/`:132 files, every source hash stable across copying.
`chest-receipts.json`, `capacity-receipts.json` and `ocarina-receipts.json` separate player reports from
saved/logged facts. No original profile, save or installed-game directory was written.

### A: eight chest items

Seven original collections are supported by open chest flags and saved ownership (BottleC adds the third
slot, retaining Bug/Empty in A/B). Rupees progress154→354 while that chest changes closed→open; MaxLife
stays24 with Double Defense owned. Original log override lines: Graveyard3295, Trail11717, GoronCity15305,
ZoraRiver20047, HyruleField11461, SacredForestMeadow26547. These are mod-load proofs, not substitutes
for Kareem's model/text/usability observations. A separate post-reload usability sequence for each row
was not individually described in the forwarded report.

Farore's initial absence was **not a chest-grant defect**. Both preserved earlier sessions visited
Death Mountain Trail, not Crater. The Trail chest is Nayru's (`9809508929088891725`, already open);
the intended Farore chest is `1158729434763801603` in both Crater Bancs. Its original false opened flag
and Farore false/stock0 were valid readings of an uncollected target. The interim FAIL instruction was
superseded by UNPLAYED pending the correct location, then by this PASS:

- Kareem opened the correct **Crater upper-rim rock-grotto** chest and reported Farore received without issue.
- New immutable evidence: `work/r22-lifts/farore-pass-20261125-140010/farore-receipt.json`.
- Latest manual slot01 at13:56:30: Crater chest open, `IsGet.Item_FaroreWind=true`,
  `PouchData.Item_FaroreWind.StockNum=1`; Nayru remains true/1.
- `PlayerStatus.MPMax=240`, `PlayerStatus.MP=180`, before and after: lack of magic is not an explanation
  here. A missing spell in the earlier saved inventory was real, not merely an inferred hidden menu entry.
- `save/` and `save-work/` have identical SHA256
  `f5b748f347c58e8e8b3e08c2d7f0e19e6fdcbce2c5ccde7216e35ce3a2e55c91`.
- Current log2409 loads the candidate's Crater Adult Dynamic Banc; map2519 enters Crater.
- Talon's independently successful scenes07 uses the **same** `Item_FaroreWind` key, through
  `GetPouchContent`'s pouch add with Num1. No alias/key workaround or Farore fix was needed.

### B: expected capacities and the once-state per retained slot

**04b confirms Stick20 and Nut30**, not a Bullet Bag reward. DekuSeed capacity stays40; the actual
Nut medium flag/stock becomes true/1. **05b PASS:** Kareem clarified that he left the first drop
**uncollected**, reset the area, and collected the second drop **once**. This is recovery, not duplication.
He reports persistence after reload/as child; the saved child states agree.

H=`2177746409373494991`, H xor2=`2177746409373494989`. **Both are permanent collection records**,
not separate spawn/death flags. Killing the enemy leaves no saved collection mark (`tokens.py:346-391`);
pickup writes both (`tokens.py:12-13`, tracker `_source_pair`). All corresponding save/save-work slot
hashes match in the snapshot. Medium-bag stock is1 where owned.

| Arm / slot | Age | Stick/Nut caps | Medium Stick/Nut owned | Tokens | Collection H/Hxor2 | Stick/Nut chests open |
| --- | --- | --- | --- | ---: | --- | --- |
| 04b 00 baseline | adult | 10/20 | false/false | 18 | false/false | false/false |
| 04b 01 | adult | 20/20 | true/false | 18 | false/false | true/false |
| 04b 02 | adult | 20/20 | true/false | 18 | false/false | true/false |
| 04b 03 | adult | 20/30 | true/true | 18 | false/false | true/true |
| 04b 04 | child | 20/30 | true/true | 18 | false/false | true/true |
| 04b 05 | child | 20/30 | true/true | 18 | false/false | true/true |
| 05b 00 baseline | adult | 10/20 | false/false | 18 | false/false | false/false |
| 05b 01 | adult | 10/20 | false/false | 18 | false/false | false/false |
| 05b 02 | adult | 20/20 | true/false | 18 | true/true | false/false |
| 05b 04 | child | 20/20 | true/false | 18 | true/true | false/false |
| 05b 03 | child | 20/20 | true/false | 18 | true/true | false/false |

Cap20/stock1 alone cannot prove a unique pickup; that comes from Kareem's explicit clarification.
Rotating saves cannot reconstruct every kill/reset between saves. No duplicate-grant FAIL is inferred.

### C: PR40-active passes, native Time crashes

07 saved Time IsGet/stock true/1 and `PlayerStatus.EquipOcarina` String64=`Item_Ocarina_Time`;
08 saved Fairy true/1 and active=`Item_Ocarina_Fairy`, Time stock0. Their logs load ActorInfo at73,
both model packs at1856/2105 (07) and2040/2280 (08), and their gallery override at1537/1755.
Both completed without a crash. Saved persistence is corroborated; neither log separately proves a
same-process Continue sequence or learned-song play.

09's preserved `user-r22-lifts-ocarina-time-native/longshot_log.txt:5055-5066` shows:
`0xc0000005`, read guest`0x270`, host`longshot.exe+0xe3ca5ed`, x0=0, return address`0x829630ac`.
Gallery override loaded at1258; no PR40 packs/ActorInfo were supplied. This matches the documented
round11 null-ShowItem getter signature (`r11-ocarina.md:295-310`). **[INFERENCE]** missing native get-model
actor is the immediate cause; exact EVFL action and in-RAM pouch-grant timing are not certified.
Only baseline ownership/stock0 was saved. No unchanged rerun was performed.

Claude's approved shipping variant is **PR40 mandatory for ocarina hand-overs**, not incidental activation
by an unrelated chest. Production now enforces that boundary; the new native regression covers produced
hand-over output with no ocarina chest and missing-donor refusal. Both passed in queue13a.
Native Fairy10 remains unplayed and outside the shipped path; no native-pack safety is claimed.

### Destination-scoped catalog decision

The existing `gifts.held_items` removed its whole type hold when `chest_verified` gained an actor, which
would also admit the eight packet02 items at unplayed Scrub checks. **Claude, 2026-11-25: CONSTRAIN.**
Only Chest joins the existing Gift/Token destinations; no Scrub lift without a separate played packet.

Small generalisation: optional `destinations` on a catalog receipt adds only its listed kinds to the
existing Gift/Token baseline. The eight packet02 records explicitly list `["Chest"]`. Other unscoped
records retain their existing behavior; no other item admission changes.

Requested consumer-level regression: all eight accepted at Chest and refused at Scrub, Token on/off;
Gift and prior Token eligibility retained, plus an unscoped legacy control — **17 passed in3.04s**,
n2/W1. These tests call `allowed`, never fill a seed. Source formatter/lint pass. Both requested native
boundaries and whole event registration subsequently passed on the test-only successor, below.

Prepared runners: `work/r22-lifts/focused-successor13a.sh` and `successor14.sh`; both default to
non-executing `--plan` and require the assigned predecessor-release marker before one guarded acquisition.
Success cleanup explicitly checks/removes only the owned lock and posts a phase-specific release rather
than relying on the earlier broken EXIT trap. The initial focus was n2/workers1; Claude subsequently
approved full caps: synthetic n8/workers4 and native n8/workers3, with CIM checks at stage starts.

`successor_sweep.py --plan` validated the prepared source module, exact350 main rows and the four expected
settings strings without preparing native contexts or filling. It reuses the existing fill/oracle/retry
engine, shared main300 and previously generated immutable5bc binding50, preserving the old receipt files.
Its whitelist adds only Chest to the eight existing Gift/Token holds and Chest/conditional Token to the
two capacity holds; other effective fields must match. A fresh candidate350 is still required at line14.

### Queue13a receipt: PASS on the test-only successor

Claude12b released at18:07 after main moved1fc1c54→63fa85e. Frozen product stayed unchanged, no rebase.
The owned watcher made one guarded acquisition, only after the new explicit release and CIM players0.

Initial synthetic focus:233 passed/5 failed. Printed values showed the fixture's raw `GS Token` kind,
while the correct derived holds contained canonical `Token`. A direct kind substitution passed admission
but then correctly failed the generator's raw-source clash guard. Final test-only correction uses public
`prepare` before admission checks and retains raw `GS Token` for generation; every assertion remains.
Aimed five cases **passed in3.36s**, formatter/lint clean. Claude approved test-only successor461f68d6
and required a full synthetic rerun.

- Full synthetic: **4426 passed,845 skipped,24 warnings in477.93s**, n8/workers4; all three OOT variables
  unset. Native stage started only after its successful exit.
- Native focus: complete `test_getitem_ocarina_dump.py` plus complete `test_event_registration.py`:
  **17 passed in464.88s**, n8/workers3, `--dist loadfile`. This proves produced hand-over model output
  without an ocarina chest and refusal without the model donor, not merely policy wiring.
- Both stage-start CIM checks found0 players; imports proved the immutable461f68d6 source snapshot.
  Logs: `work/r22-lifts/focus13a-461f68d67318190265284fd9a6460b406e615e69/`.
- Explicit own-lock cleanup and **LOCK RELEASED cs22g13a at18:28** completed successfully.

**Claude approved line14 reuse** of this exact-SHA full-synthetic result, recorded in
`work/r22-lifts/full-synthetic-461f68d6.json`. The14 runner checks the receipt SHA and successful exit
before acquisition; its observed `--plan` now lists only format/lint, candidate350 versus own-parent
immutable main350, and full dump. The one-attempt14 watcher waits for a new explicit cs22c13 release;
no directory disappearance or acquisition retry authorizes a turn.
