# Round 19, cows — fresh saved-Bool persistence diagnostic

cs19e; branch `r19/cows`; research/packet source main
`d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`; model `openai-codex/gpt-6.1-sol`.

Branch rebased onto release-candidate main `f5c679d` after Claude's MAIN MOVED
notice; no conflicts. The staged diagnostic packets remain frozen from the
documented `d9deb65` source, not newly generated 0.2.3 seeds. No settings files
were changed or withdrawn story fields restored. Claude's research-only
full-gate/lock exemption remains applicable; no gate or sweep was run on rebase.

**STOPPED: research-only handoff for r20.** V1 control gave milk; v1 candidate
froze. Kareem then played v2: milk only, no +20, no crash/freeze. No post-milk
Save was made, so the Bool remains unknown. No speculative v3 is staged.
No cow locations, option, logic, fill, production patch or version change.
Only this research record enters the branch.
Scripts, decoded research, profiles and mods stay outside the repository under
`E:/OOTRemake/work/r19-cows/`. The agent started no game, opened no player seed
and wrote no original save, dump or runtime folder.

Claude's follow-up explicitly exempts this diagnostic from a full gate and lock:
it will not merge as a game-behavior implementation. Focused tests and paired
staging only. No sweep is applicable: no locations, destinations, logic or fill
changed. No `.nup` working-set/resource-list change; production input reads and
output are unchanged.

## Final outcome: v2 played, path localized statically, cause unresolved

Kareem played `Cows v2 - candidate.bat` at **11:13–11:16**. **Milk only, no +20,
no crash/freeze.** Its log proves `Animal_Cow`, GameDataList and RSTB served from
`cow-persistence-candidate-silent-v2`; relevant lines **12–13, 75, 83, 1983**.
It contains no event/node execution trace identifying the branch or action.
He did not Save after milking; Claude reports slot_05 unchanged since 11-13.
The original missing key therefore says nothing about the in-memory Bool.

**Exact static source trace, supported native data:**

1. Impa's child placement is `Animal_Cow`, Hash `3581309213670406493`.
   In `Animal_Cow.pack.zs`,
   `GameParameter/ReplaceEventParam/Animal_Cow.game__ocarina__ReplaceEventParam.bgyml`
   selects `Animal_Cow_GiveMilk` for the ocarina interaction.
2. `RSDB/EventSetting.Product.111` maps that event to `Animal_Cow:GiveMilk`.
   Event72 calls `Cow_GiveMilk`, passing `Animal_Cow_PushToBottleMilk`.
   Its recommended-Epona branch reaches Event3's native `EventTransition`.
3. That EventSetting maps to `Animal_Cow:PushToBottleMilk`, not a Link-house or
   Gerudo entry. Event141 queries `BottleItem=-1`; the successful bottle case
   is **0**. The following equipped-mask alternatives converge on Event6,
   which continues to Event20, then Event4's native milk subflow.
   No-mask specifically takes false cases through Event25/31/32/33/34/35/36/38
   before Event6. The other bottle case ends without milk.
4. V2's **sole modified edge is Event20 → appended gate → Event4**. False flag
   gives the native wallet action, sets the Bool, then Event4; true flag goes
   straight to Event4. Candidate readback confirms that edge and false-default
   saved row. Thus the static data does **not** support claiming that a day or
   bottle variant bypasses the probe while reaching this ordinary milk call.
5. The two other milk calls are Event74 (`PushToBottleMilk_LinkHouse`) and
   Event114 (Gerudo/shared LinkHouse0 routes). Neither belongs to the ordinary
   actor's registered ocarina entry. No runtime node trace establishes that
   either ran on the played attempt; resource loading alone cannot do so.

Reproduction: external `trace_cow_path.py` → `cow-path-proof.json`,
`cow-path-trace.log`, plus printed candidate Event20/appended nodes/Bool row.
The native registry, actor pack and EVFL were read directly; no game launched.
The earlier static executor entered the probe **assuming false**, so it did
not establish what the new-key query actually returns at runtime. Whether the
gate skipped, the action had no effect, or the runtime used another route remains
unresolved without a post-milk Save or node-level execution evidence.

**Claude's stop condition applies:** the failure cannot be localized to a
specific runtime branch/action from the available evidence. No guessed third
packet, new get window, borrowed native flag or unrelated save mutation is made.
Cows remains research-only for r20; saved-Bool persistence is **not proven**.
V1/v2 mods, launchers, profiles and logs are preserved. The retained v2 checklist
now says **SAVE IMMEDIATELY AFTER THE FIRST MILK, EVEN IF NO +20 APPEARS** and
retain inspector output even on a failed expectation. It is not a request to
replay unchanged v2. No further play is requested in this handoff.

## Played v1 failure and silent v2 replacement (2026-11-20)

**Kareem's result, relayed by Claude:** control gave milk only. Candidate froze
during the extra item-get after Epona's Song and the cow's response; no rupees.
This is the failure reproduction; v1 was not replayed to confirm it. It proves
neither successful grant nor saved-Bool persistence.

Read-only evidence:

- `ingame/user-cow-persistence-candidate/longshot_log.txt` lines 75, 83 and 1982
  confirm candidate size-table merge, GameDataList and cow flow loads. Rendering
  continues in the log; no event-node exception/stall backtrace is present.
- `work/save-backups/2026-11-20_093147-r19-cow-persistence-candidate-1/`
  contains the pre-grant save: rupees **99**, new key **missing**. A snapshot of
  the still-old save is not evidence that the new row cannot save.
- Flow trace: v1's appended call to
  `GetPouchContent:GetPouchContentByActorName` enters Event53 with
  `IsShowNumDisplay=true`, then `GetPouchContent/Event82` →
  `OpenRupeeUIIfNeed` → `Event80/UISystemActor.EventOpenRupeeDisplay`, waiting
  for open animation **before** `Event0` performs the pouch add. The wrapper is
  not a silent grant. **[INFERENCE]** this extra blocking presentation in the
  cow scene accounts for the observed pre-credit freeze; the log cannot identify
  the exact blocked node. Do not blame saved-Bool layout from this result.
- A second v1 construction defect: appended subflow index 160 was not registered
  in `PushToBottleMilk.sub_flow_events` (native list still `[6]`). The EVFL
  writer preserves that explicit table, it does not discover added calls.
  Its contribution to the played freeze is unproved. V2 removes the new call
  entirely rather than attempting another item-get wrapper.

**Historical v2 packet (played: milk only, no +20):** `E:/OOTRemake/work/r19-cows/v2/ingame/`.
Historical launchers are `Cows v2 - main-control.bat` and `Cows v2 - candidate.bat`; no replay is requested.
Checklist: `v2/ingame/CHECKLIST.md`, Longshot 3.0.0; same one-cow first/repeat/
Save/Continue acceptance, estimate **8–12 minutes both arms / 4–6 candidate**.
The original v1 mods, launchers, frozen log and profiles are unchanged.
Both v2 profiles are fresh, identical copies of the original natural fixture
documented below; no save edits, chests or extra player preparation added.

V2 changes only the probe's reward node to native
`PouchSystemActor.EventTriggerIncreaseRupee {Value: 20}`, then writes the same
saved Bool and proceeds to the original milk call. Native positive-20 precedent:
`Dm_LonLon_0030/Event40`; the existing cow PouchSystemActor's member settings
match that donor. No added subflow, get window, pickup notice, model, animation,
rupee-counter opening/closing or UI wait. Native milk presentation remains.
All native entries and their subflow lists remain exact. One cow / one global
latch, not independent cow checks. GameData bytes are identical to v1; only
the unsafe grant context is changed.

**Focused v2 proof:** `uv run python E:/OOTRemake/work/r19-cows/stage_silent_v2.py`
passed against the real dump: native action/parameters and actor settings,
first **99 → 119 / flag true**, repeat **119 → 119 / flag true** in the static
executor, no added UI/subflows, exact native inverse/EVFL roundtrip, unchanged
GameData, adequate allocations, native control, identical natural save copies
and both real `cmd.exe` dry runs exit 0 on Longshot 3.0.0. V1 mod/log and source
save preservation are asserted. Cow raw size **104712**, allocation **105008**;
GameData raw/allocation unchanged from v1. `v2/proof.json`,
`silent-v2-stage.log`, `native-getpouchcontent.json`, `native-wallet-actions.json`
and `survey_silent.py` retain the external evidence.

Both v2 pre-play save inspections passed with new key **missing**:
`check_save.py candidate --packet v2 --expect missing` and its control equivalent.
Inspector now defaults to v2; `--packet v1` explicitly inspects historical v1.
After first milk, Save and run:
`uv run python E:/OOTRemake/work/r19-cows/check_save.py candidate --packet v2 --expect true`;
repeat after Continue and third milking. Expect silent +20 and milk first,
milk only second, milk only after Continue. Those were staging expectations;
the later played v2 no-credit result is recorded above. No saved true value or
persistence pass is claimed. Research-only full-gate/lock exemption still applies.

Claude later confirmed the “crashed, then froze” report used OLD v1 (11:05 log),
not v2; v2 was never launched. To disambiguate, he renamed v1 launchers
`OLD v1 (froze) - ...bat` and v2 launchers `Cows v2 - ...bat`. Both external
checklists use those names. At that correction v2 was unplayed; the later
11:13–11:16 v2 result is recorded above and must not be confused with v1.

## Public reference and scope decision

OoT Randomizer Wiki, [Readme, Main Rules → Shuffle → Shuffle Cows](https://wiki.ootrandomizer.com/index.php?title=Readme#Shuffle),
read 2026-11-19: Epona's Song gives an item first, then milk on subsequent uses;
nine N64 cows, plus the MQ Jabu cow when enabled. Public documentation only; no
other randomizer's source or diffs used. These counts do not establish remake
locations or access rules.

**Proposed by cs19e; accepted by Claude in the follow-up:** stop at the smallest
fresh saved-Bool experiment, not an unproved default-off cow shuffle. Option (b),
borrowing allegedly unused native saved flags, was not pursued: absence from a
string scan alone would not prove they are never written or safe to borrow.

## Evidence and remaining blocker

- Native `Animal_Cow` has 159 events. Ordinary milk is
  `Animal_Cow/Event4`, calling `Dm_SY_GetInEvent:GetInEventInBottle` with
  `Item_Bottle_Milk`; `Event20` is its sole incoming edge. Song/bottle/camera
  handling remains native.
- `Cow_IsGetMilkFromCow` is runtime-only (save index -1); the saved
  `HaveTalked_Special.Animal_Cow_PushToBottleMilk_Event5` is shared dialogue
  history, not one completion per cow. Neither supplies per-cow once-only state.
- Existing `patch/gifts.py:add_flags` already appends saved Bools and grows the
  progress/all-data entry-table layout. It is reused, not replaced by a second
  schema. Native/synthetic gift tests exercise that implementation.
- Historical `plans/03-game-data.md` section 19, `r5-gifts.md` and D22 report a
  saved fairy Bool surviving quit/Continue. Round 18 Mido instead adds only an
  unsaved BoolExp. Those older fairy records are not claimed as a newly observed
  cow proof; this track follows the current instruction to stage a fresh key and
  leave its persistence **play-held**.
- The read-only Banc survey finds **14 actor rows / 14 distinct Hashes**, of
  which 11 use `Animal_Cow` and three specialized actors. Several age/alternative
  rows occupy matching positions with different Hashes. This is NOT a census of
  14 independent physical checks, nor a settled cross-age identity policy.

External reproduction: `survey.py`, `native-flows.json`, `cow-census.json`,
`select_fixture.py`, `fixture-candidates.json`. No decoded data is committed.

## Paired packet — v1 historical, candidate failed in play

Directory: `E:/OOTRemake/work/r19-cows/ingame/`.

| Arm | Launcher | Behavior expected, not observed |
|---|---|---|
| Main control | `01-main-control.bat` | Native milk every successful milking; no diagnostic rupees or new flag. |
| Candidate | `02-candidate.bat` | First successful ordinary milking adds 20 rupees and native milk; later successful milkings give milk only, including after Save/Continue. |

Both built with the unchanged main `patch.write` API and empty chest plan.
Control serves the native flow and GameDataList, **decompressed byte-identical**
to the read-only dump; compression is regenerated by the writer. Candidate uses
the same packet and adds just:

- `Clawshot.Research.CowPersistence.R19` (hash **1928482073**), saved Bool,
  default false, reset type 8, save index 0. The four layout fields grow by 8
  bytes each through the existing gift helper.
- One edge into three appended events: test flag; when false, plain
  `GetPouchContent:GetPouchContentByActorName` gives `Obj_Rupee_Red`, then set the
  flag true; continue into untouched native milk. True goes straight to milk.
  No ordinary event, refusal, song gate, actor binding or original entry changes
  beyond that one edge. The inverse edit reconstructs the exact native tree.
- Normal writer allocation updates: cow flow raw **103928 → 104736**, RSTB
  **104208 → 105008**; GameData raw **1462888 → 1462932**, RSTB
  **1463176 → 1463224**. Candidate emits the two resources and size table.

**Coverage: ONE cow in the play checklist, ONE GLOBAL diagnostic latch.** The
chosen cow is Impa's cow in Kakariko, native child actor Hash
`3581309213670406493` in
`Banc/KakarikoVillage/KakarikoVillage_Child_Dynamic.bcett.byml.zs`.
Other cows reaching the same shared Event4 would share the latch; no independent
per-cow rewards or complete source-family coverage is claimed. Link's House,
Gerudo variants, age deduplication, bottle-independent checks and arbitrary-item
admission remain outside this experiment.

## Natural fixture and isolation

Read-only source:
`E:/OOTRemake/work/save-backups/2026-11-13_084401-longshot-transferred/slot_05/`.
Provenance/landmark: `r18-keys.md`, Natural Well fixture; caption
2026-11-12 14:57:43, **child Link in Kakariko after draining the Well**. Nearby
Impa's house supplies the cow; do not enter the Well or use the roof/heart-piece
route. This is a natural transferred save, not a generated diagnostic seed.

Re-read directly: Epona's Song learned; Fairy and Time ocarina stocks 1 each;
99 rupees; BottleA Blue Fire, BottleB Fairy, remaining bottles invalid. No saved
entry for the new key. Active `PlayerStatus.EquipOcarina` must be checked/equipped
normally in game; ownership history alone is not an active-instrument proof.

Progress SHA256:
`9da25b865f91f8ca53eab3a899685c8a56e34763d84b05b97865aa097f0fdeac`.
Both arms contain identical copies of just this progress/caption pair, account
and options, in separate packet-owned user profiles. File hashes and parsed save
objects match the source. **Save edits: zero. Pinned chests: zero.**

## Historical v1 checklist — use silent v2 above instead

Full checklist: `E:/OOTRemake/work/r19-cows/ingame/CHECKLIST.md`.
Claude boot-checks before Kareem plays. Launchers derive from
`E:/OOTRemake/tools/test-launcher-template-longshot.bat`, with the executable
pinned to `builds/stable/v3.0.0/bin/longshot.exe` (**Longshot 3.0.0**), their own
single mod/profile, CRLF, `HOS_FS_OVERLAY` unset. No game or boot was run by cs19e.

Run control first, candidate from its independent original copy second:

1. Continue the Kakariko thumbnail. Equip an ocarina normally; use only
   Teleport/clock if needed, no inventory/age/flag cheats. At Impa's cow, first
   try Epona's Song with both bottles still full: native refusal, no rupees;
   candidate's latch must not be consumed.
2. Pour out Blue Fire normally, leaving the Fairy. Note balance. Milk once with
   Epona's Song: control **milk only**; candidate **+20 and milk**. Expected
   99 → 119 only if no route pickup/spend changed the initial balance.
3. Save immediately to inspect the first grant, before repeating. From this
   worktree run:
   `uv run python E:/OOTRemake/work/r19-cows/check_save.py candidate --expect true`.
   The newest newly written progress save must show
   `save.flag('Clawshot.Research.CowPersistence.R19') == true`. This intermediate
   Save measures the first grant; it is not the later reload acceptance.
4. Drink both milk portions to empty the bottle; milk the **same cow** again:
   milk only, no additional 20. Save, quit to title, Continue on the same arm,
   empty its milk bottle again, then milk the same cow a third time: milk only.
   Save and repeat the inspector: candidate true. Control uses
   `check_save.py main-control --expect missing` throughout.
5. Retain load evidence in each packet profile's `longshot_log.txt`:
   `mods: Event/EventFlow/Animal_Cow.bfevfl.zs <- <arm path>` and
   `mods: GameData/GameDataList.Product.110.byml.zs <- <arm path>`, plus candidate
   size-table load/merge evidence. Stop if native control fails to milk, the
   flag is not saved true, the rupees repeat, or the cow route is inaccessible;
   do not edit state to make it pass.

`check_save.py` reads only the two packet-owned profiles, prints every progress
slot plus newest-by-file-mtime values, rupees and bottle contents, and optionally
asserts missing/false/true. Before v1 play the source copies reported **missing**
in both arms. **No saved true value or in-game persistence has been observed.**
The test requires both saved true after first milk and milk-only after Continue;
a static graph simulation is not the persistence proof.

## Verification receipt

- `CLAWSHOT_WORKERS=1 OOT_ROMFS=E:/Games/Hookshot/romfs uv run pytest
  tests/test_gifts.py tests/test_gifts_dump.py -q --tb=short`:
  **41 passed in 160.90 seconds**. Existing saved-Bool schema, layout and native
  gift writer coverage. Log: `E:/OOTRemake/work/r19-cows/gifts-focused.log`.
- `uv run python E:/OOTRemake/work/r19-cows/stage_packet.py`: **PASS** on actual
  dump; control native bytes, candidate exact inverse/roundtrip, fresh-key hash
  availability, four layout deltas, first/repeat branch simulation, original
  refusal unchanged, real native rupee actor/wrapper, identical unedited saves
  and sufficient written allocations. Receipt: `packet-proof.json`, `stage.log`.
- `uv run python E:/OOTRemake/work/r19-cows/verify_packet.py`: **PASS**, both real
  `cmd.exe` dry runs exit 0; stable **Longshot 3.0.0** executable, isolated mod
  roots, CRLF and no `hookshot.exe` references. Receipt: `launcher-proof.json`.
- `check_save.py candidate --expect missing` and
  `check_save.py main-control --expect missing`: **PASS** before play. Receipts:
  `candidate-before-play.json`, `control-before-play.json`.
- Initial research-only failures were diagnosed, not unchanged-rerun:
  `Save.get` does not exist (use typed entries/read-only accessors); native
  PouchActorInfo is Product.111, not guessed Product.110 (resolved by filename
  listing before correction). Neither failure changed production code or tests.
- No full suite, gate lock or sweep: explicitly waived by Claude for this
  non-merging research diagnostic. No runtime result inferred from dry runs.

## Handoff / next decision

**Research-only r20 handoff; no further play requested.** V1 froze during its
extra get; v2 gave milk without the diagnostic rupees. Static native tracing
puts the v2 probe on the ordinary cow's milk path, but no execution trace or
post-milk Save localizes its runtime failure. Claude's stop condition applies:
no speculative v3. Both packets remain evidence, not ordinary seed patches.
Saved-Bool persistence and per-cow once-only grants are unproved. The retained
checklist explicitly requires SAVE immediately after first milk, even without
the visible signal, and retaining the inspector's observed value on failure.
