# Round 22 merchants — cs22d

Branch `r22/merchants`, base `874f30a`, assigned by Claude after the gift-gates audit, 2026-11-25.
Target 0.2.9. Do not merge or lift the three holds without Kareem's play.

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
