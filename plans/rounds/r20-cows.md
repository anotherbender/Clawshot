# Round 20 — cows and Fortress four-rescue staging (cs20f)

Branch `r20/cows`; intake main `acbb903df111bb30609baedac35316b22d43700e`
(0.2.4 plus tracker PR #36). Model `openai-codex/gpt-6.1-sol`.
Research/staging only: no product code, cow locations, setting, palette, fill,
logic, pack resource list or version change. External artifacts:
`E:/OOTRemake/work/r20-cows/`. No game/boot/runtime build started, original save
or runtime folder written, or personal seed opened. No gates or sweeps: the
round explicitly excludes them for research-only tracks.

## Cow evidence found after the round-19 record

The user-reported v2 milk/no-crash result remains ground truth, not replayed.
The retained packet now contains a later **newly written** save:
`E:/OOTRemake/work/r19-cows/v2/ingame/user-cow-persistence-candidate-silent-v2/save/5a3c9e1f0b7d24680000000000000001/slot_00/progress.sav`.
Read-only observation on 2026-11-20:

- File mtime **2026-11-20 16:33:02 UTC**; SHA256
  `6af03481ce109fe1cdd8d42fb3f39c95fb27b8469d5d1c9a3515ae6141b839be`.
- `Clawshot.Research.CowPersistence.R19` (hash `1928482073`) **true**;
  **119 rupees**, BottleA Lon Lon Milk, BottleB Fairy; active
  `PlayerStatus.EquipOcarina=Item_Ocarina_Time`, child.
- The older slot_05 remains **99 rupees / key missing / Blue Fire**. The read-out
  enumerates both and selects by file mtime, not slot number. Receipt:
  `legacy-v2-readout.json`.

This proves the new Bool exists true in an actual saved progress file. It does
not by itself prove a Continue traversal, once-only behavior, per-cow identity,
or the precise cause of the earlier missing visible signal. **[INFERENCE]**
99→119 is consistent with the silent grant; rupees have other sources.

**Claude's steer, 2026-11-20:** before a new build, copy the existing v2 candidate
and this slot_00, Continue, milk the same cow, record HUD rupees before/after,
Save/quit and inspect. The fresh visible-edge probe is fallback only if that
result is ambiguous. No old profile or mod is rebuilt/reset.

## Primary cows packet — unchanged v2 continuation

Directory: `E:/OOTRemake/work/r20-cows/cows/ingame/`.
Private diagnostic recipe **2011200601**; not a full shuffled/playthrough seed.

- `01 - Continue control.bat`
- `02 - Continue candidate.bat`
- `03 - Read candidate save.bat`
- `04 - Read control save.bat`
- `CHECKLIST.md` beside them; **Longshot 3.0.0**, estimate **4–6 minutes both arms**.

Both mods are copied byte-identically from frozen round-19 v2, originally built
from main `d9deb65`; no new build. The main control's cow flow and GameDataList
are decompressed byte-identical to the current native dump, so it retains the
old/native behavior. Candidate's existing true branch goes straight to native
milk, without another wallet action or flag write. Each arm gets a separate,
byte-identical unedited copy of the new slot_00, account/options and runtime
controls. Both therefore **start true/119/milk**; the native control's next save
is expected to omit the custom key, unlike candidate. Do not confuse a starting
true value in this copied control with a native-schema persistence proof.

Checklist: drink both milk portions, record numeric HUD **before song and after
milk**, expect no +20 in either arm, Save even on failure, quit and read out.
Candidate must retain true in **new progress content**, not just re-read the
staged starting file. No extra get window is expected: v2 intentionally grants
silently. Preserve load log plus game observation. Main control has its own
profile, never candidate progress. Only Teleport/clock permitted.

Verification, not play evidence:

- `PYTHONDONTWRITEBYTECODE=1 CLAWSHOT_WORKERS=1 uv run python
  E:/OOTRemake/work/r20-cows/stage_continue.py`: **PASS**. Exact mod copies,
  native control raw bytes, candidate true-branch readback, saved schema,
  matching unedited source/profile hashes; two real `cmd.exe` dry runs exit **0**.
- `check_save.py cows candidate --phase before --expect true` and control
  equivalent: **PASS**. Read-out writes JSON receipts only outside profiles;
  no arbitrary-path option or personal-save access. Original read-out adapted
  from `work/r19-cows/check_save.py`.
- Intentional negative smoke: real `03 - Read candidate save.bat` on the unplayed
  staging baseline exited **1**, printing the actual TRUE/119/milk values and
  `No newly written progress content`. This prevents a copied starting TRUE
  from being reported as a newly played persistence pass. Receipt:
  `cows/inspector-freshness-refusal.json`. Read-out launchers use the stable
  main checkout for Python, not a disposable round worktree.
- Launchers derive from the supplied Longshot template, hard-pin stable
  `builds/stable/v3.0.0/bin/longshot.exe`, leave `HOS_FS_OVERLAY` unset, one real
  packet mod and pre-staged profile each, never reset at launch. No
  `hookshot.exe` reference.

## Fresh visible-edge fallback — held behind the cheaper proof

Per Claude's steer, **do not build/run a fresh probe before the unchanged-v2
Continue result**. The staged primary check above is the next morning action.
Native marker design is being retained as fallback research only; if the
primary is ambiguous, its next build must visibly identify edge entry before
any Bool query, distinguish preexisting true from a new write/readback, and
observe that preexisting true after Continue without rewriting it. No new
get window or rupee-only diagnostic is acceptable.

Concrete design: `E:/OOTRemake/work/r20-cows/FALLBACK.md`; private identity
2011200603 reserved, **not built**. Fresh R20 Bool hash2604187271 on the
original99/Blue-Fire natural copy, not the new119/TRUE continuation. Seven
appended nodes on Event20→Event4: native EventTalk marker **before** query;
prior-true says KEPT TRUE and never writes; prior-false sets true, queries
readback, and says WRITE TRUE/FALSE. Native Event6/index8 is the talk donor,
Event20/index83 the setter, Event66 the query; PushToBottleMilk keeps
main135/subflows[6]. No new subflow/actor/action/query or get window.

`inspect_fallback.py` read the actual native donors and all16 cow message
archives: **PASS**; receipt `fallback-donor-proof.json`. USen Talk_04 has no
leading style tag; JPja begins with a ruby annotation, not generic style.
The fallback therefore specifies short plain English labels in every language,
not blind reuse of local ruby tags. Additional sequential dialogues and
same-frame readback remain unplayed risks, not an implemented fix.

## Fortress four-rescue packet

Directory: `E:/OOTRemake/work/r20-cows/fortress/ingame/`.
Private diagnostic recipe **2011200602**; **not a generated/full beatable seed**.
No production placement/logic/default change. **Proposed by cs20f:** retain
the minimal r19 pinned-source experiment, but choose a game-written near-Fortress
**0/4** snapshot and add the played DMT chest as the fourth remote key.

### Exact unedited fixture

Read-only source:
`E:/OOTRemake/work/save-backups/2026-11-19_130041-r18-fortress-cand-b-3/5a3c9e1f0b7d24680000000000000001/slot_04/`.
Caption: **Fortress, 2026-11-19 13:00:25**. Progress SHA256:
`304af3239c800389de3c8c4f5ee125d9049d9daab29ceaebcccbed7501fff7b4`.
Natural r18 diagnostic continuation of Kareem's after-Forest save: boss **Yes**
already performed in game, **Step01**, not a flag edit. Zero rescues, defeats,
source collections, keys held/found and card stock; both Training gates false.
Unlike r19's 1/4 fixture, all four sources are untouched; no stale collected
guard04 exception is needed.

Parent re-read actual saved fields, not only the historical scan:
active **EquipOcarina=Item_Ocarina_Time**, Time stock1, Storms learned,
Master Sword/Hookshot/Bow,27 arrows,10 bombs,six hearts,148 rupees. Medium
wallet stock1 (500 capacity) gives headroom for four20-rupee drops; no copied
currency edit is needed. Each arm copies just this progress/caption pair,
account/options and identical runtime controls. **Save edits0**.
Receipt: `fortress-initial-readout.json`; selection: `fortress-selection.json`.

All four chests read **false** using `save.flag('IsTreasureBoxOpen.<Hash>')`:

| Hash | Landmark / route evidence |
|---|---|
| `9809508929088891725` | DMT cracked wall, bomb; named Fortress credit, cell spending and rescue played r18 |
| `17750686910716887133` | Valley tent Storms grotto, visible chest; route played in chest hunt |
| `18413589940135955604` | SAME grotto, invisible adult chest four metres beside visible; no Lens route played |
| `16619432200060282313` | Fortress curtained-doorway/open-hole grotto, behind Skulltula; route played |

The latter three **named Fortress-key grants remain unplayed**, as do the
complete four-source/captain/card/Training chain. The checklist puts all FOUR
chests before fights and states prominently that guard drops give20rupees,
**not keys**. Valley/DMT HUD is not the Fortress inventory counter.

### Longshot 3.0.0 checklist and duration

`CHECKLIST.md` is beside the launchers, not hidden in a separate research note.
`01A`–`01D`: main control; `02A`–`02D`: candidate. Each arm's four launchers
resume **the same persistent profile**; no fabricated advanced snapshots or
resets. Natural breaks:

| Segment | Estimated minutes | Required outcome |
|---|---:|---|
| A: four remote keys | 8–12 | held4/found4, rescued0; Save |
| B: central lower013 and middle016 | 12–20 | two guarded rescues, held2/found4; Save |
| C: front upper015 and far upper014 | 12–20 | four rescued, held0/found4, native captain/card once; Save |
| D: Continue/revisit/Training entry | 8–12 | all four drops retired, no repeated scene, card retained; pay30 and enter |

**40–65 minutes per full arm**, unmeasured conservative estimate; every
segment under30. Both full arms **80–130 minutes**. Control and candidate
are byte-identical existing experimental behavior, not a candidate fix:
the checklist offers an **8–12-minute single-key/guard/rescue control baseline**;
a second full run is only needed if Claude requests it. All four candidate
rescues can be played in one sitting, or resumed at the natural breaks.
Cell landmarks are placement-derived, not a walked route. A two-minute
fruitless search is a route blocker, not a key-grant failure; stop/report it.

The saved-state inspector prints every slot and newest-by-mtime actual values,
including failures; optional phase assertions cover keys, two rescues, complete,
Continue and Training. `03 - Read candidate fortress save.bat` and
`04 - Read control fortress save.bat` run without starting a game. HUD+20
per guard, leave/re-enter recovery before pickup, no repeat after Continue,
card/guard clearance and native30-rupee gate entry remain manual requirements.
No inventory/age/quest/source cheats, original seed/save writes, or game start.

### Verification receipt

- `PYTHONDONTWRITEBYTECODE=1 CLAWSHOT_WORKERS=1 uv run python
  E:/OOTRemake/work/r20-cows/stage_fortress.py
  E:/OOTRemake/work/r20-cows/fortress-selection.json`: **PASS** in47.39s.
  Main source **acbb903**; **33/33 resource files byte-identical** across arms;
  four named GerudoFortress bindings/helper arguments/registries read back;
  exact Banc inverse outside the four chest edits; four production jail packs;
  original rescue/card flows and GameData unmodified; allocation checks; profiles
  byte-identical to source and each other. `fortress/proof.json`,
  `fortress-stage.log`.
- All **eight** segment launchers' real `cmd.exe` dry runs exited **0**, with
  stable **Longshot 3.0.0**, one own mod/profile and overlay cleared. Together
  with the two primary-cow launchers, **ten game-launch dry runs**, no boot.
- Actual candidate/control Fortress **read-out batch programs** run with
  `before`: both exit **0**, report0/0 keys,0 rescued,0 card and all four
  named chest flags false. Updated cow inspector baseline also exits **0**.
  All **14** batch files checked CRLF and zero `hookshot.exe` references.
  Receipt: `readout-smoke.json`.
- The first read-out smoke harness parsed JSON at column1 and encountered uv's
  printed `VIRTUAL_ENV` mismatch warning. The captured payload was printed and
  showed the correct0/0/Step01 fixture. Fixed the **harness** to clear the inherited
  environment and locate the JSON object; one cause-directed rerun passed.
  No packet rebuild, changed save or repeated game attempt.

Only external diagnostic output adds these resources. No production writer,
recipe registration or pack working-set change; `test_pack_nup_dump.py`,
full gates and fill sweep are not applicable and were **not run**, per scope.

## Source policy and handoff status

Read the round-19 cows/keys records and required architecture/format/round
context. Public OoTR/SoH feature facts: `work/r20-planning/feature-compare.md`,
public documentation only; neither project's code opened. GPL facts-only
reference read before native tracing: sloperinaGZ `docs/FINDINGS.md`, local
`work/refs/sloperina-FINDINGS.md`, **§1 GameData / Saved or not / Save files**,
**§5.7 upgrades**, **§5.8 maps/compasses**. These distinguish saved schema,
pouch stock, active String64 equips and runtime-only cow state; no GPL code
copied. `plans/03-game-data.md` §19 and D22 record historical fairy persistence;
that is not a newly played cow Continue check.

## Handoff — READY (play-held)

Only this round record enters the repository. All packets, profiles, decoded
research, logs and scripts remain outside it. No browser or screenshot was used;
Claude's headless-only UI steer is satisfied without opening Chrome.

Order: Claude boot-checks; Kareem runs the **unchanged cow Continue** pair first
(4–6minutes), then the optional longer Fortress packet when he has40–65minutes.
The fresh visible-edge build is **held pending an ambiguous primary result**,
as directed. Cow saved TRUE is observed; cow Continue and the complete Fortress
chain are **not newly played**. No cow locations admitted; Fortress remains
experimental/default off. Preserve actual HUD readings, new saves and load logs;
never repeat an unchanged failed game check or edit state to force a pass.
