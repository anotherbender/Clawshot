# Round 19, cows — fresh saved-Bool persistence diagnostic

cs19e; branch `r19/cows`; research/packet source main
`d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`; model `openai-codex/gpt-6.1-sol`.

**READY (play-held), research only: silent v2 staged below.** Kareem played the
v1 control (milk only); v1 candidate froze during its added get, before rupees.
V2 is built, not played. No cow locations, option, logic, fill, production patch
or version change. Only this research record enters the branch. Scripts, decoded
research, profiles and mods stay outside the repository under
`E:/OOTRemake/work/r19-cows/`. The agent started no game, opened no player seed
and wrote no original save, dump or runtime folder.

Claude's follow-up explicitly exempts this diagnostic from a full gate and lock:
it will not merge as a game-behavior implementation. Focused tests and paired
staging only. No sweep is applicable: no locations, destinations, logic or fill
changed. No `.nup` working-set/resource-list change; production input reads and
output are unchanged.

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

**Current boot-check packet:** `E:/OOTRemake/work/r19-cows/v2/ingame/`.
Use `01-main-control.bat`, then `02-candidate.bat` **in that new directory**.
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
milk only second, milk only after Continue. No in-game v2 result, saved true
value or persistence pass is claimed. No full gate/lock: research-only exemption
still applies; the earlier 41-test receipt is historical, not a new test run.

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

The **v2** launcher paths and checklist are posted on `cs-r19` for Claude's
boot-check. The repository handoff is documentation only; neither external
diagnostic is an ordinary seed patch. V1's item-get failure is played evidence;
v2 saved-key persistence remains play-held. A passing check resolves only
prerequisite (a). Cow shuffle remains held until independent physical identities,
regions/ages/access rules, per-cow routing, item delivery and the required
200 broad + 50 Defaults + 50 Recommended sweep are implemented and verified.
