# Round 19, Track F: key families (cs19f)

Branch `r19/keys`, starting main `d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`.
Model: `openai-codex/gpt-6.1-sol`. External research and diagnostic packets:
`E:/OOTRemake/work/r19-keys/`. No personal seed opened, original save changed,
game started, version bumped or runtime folder written.

## Scope and baseline

1. Investigate a natural Shadow room-13 path; admit its existing floor adapter
   only if a reasonable played-check route can be staged. Otherwise preserve
   round 18's vanilla hold. Replacement intentionally retains the key model,
   gives 20 rupees, and must retire only after native pickup, including return
   and Continue. A structural test is not play evidence.
2. Fortress remains experimental/default off. Still unplayed: all-four rescue
   completion, captain's unchanged Gerudo card scene, and Training Ground entry.
   Stage a short natural-save completion check where possible. The carpenter
   boss's **Yes in the Valley tent** starts Step01 and activates jailed
   carpenters; four remotely credited keys alone do not start or clear the quest.

Prior played evidence is only the scope recorded in `r18-keys.md`: boss Yes,
pre-rescue talk, guard appearance and DMT-key cell opening; check11's repaired
Fortress +20 pickup once across return/Continue; Well +20 once across return.
No claim that every guard identity or all four rescues/card/entry was played.

## Investigation

The requested round overview and track file did not exist at intake; this file
records the supplied round brief. Existing adapter and family contracts read.
Language-server references were attempted for `FLOOR_SOURCES`; no Python server
was available. Shadow/Fortress natural-save investigations are restricted to
allowed read-only backup/copy roots. No flag, inventory or era edits selected.

### Public evidence correction

`README.md` incorrectly advertised active Well/Shadow floor sources while the
superseding round-18 hold and generation allowlist admit only the Well. README,
settings help and the floor adapter's evidence docstring now distinguish:
Well's short played pickup/re-entry result; one Fortress identity's played
once-only result; unplayed all-four rescue/card/Training Ground; held Shadow.
No pickup algorithm, settings default, palette or source allowlist changed.

Actual isolated browser proof used in-memory preferences, an empty external
library and disabled play/open capabilities. Hovering Fortress showed the
specific unplayed checks and boss-Yes prerequisite; Dungeon items showed the
held Shadow source and narrow Well evidence. Screenshots:
`work/r19-keys/fortress-settings-ui.webp` and
`work/r19-keys/floor-hold-settings-ui.webp`. Own tab/server closed; disposable
harness deleted. No personal seed library or preference file was read.

`pack.source.working_files` already includes both `floor_keys.native_inputs()`
and `jail_keys.native_inputs()`. The former includes both room modules, native
key pack and Shadow reveal flow. No game file was added to generation or the
working set; the supplied read-only r18 combined-layered dump remains the fixture.

## Shadow: hold retained, no staged play check

**Decision proposed by cs19f:** the only defensible natural route needs
**45–75 minutes of preparation once**, then **10–20 minutes per arm** for the
pickup check. That is not a short pickup acceptance check. Keep Shadow vanilla
in all three dungeon-item modes, preserving the existing adapter/structural
tests and the Well's admitted family. No new palette, hold or fill stage added.
No Shadow launcher, mod or test profile is handed to Kareem.

Read-only scan: **2,804 progress files / 730 distinct contents, zero parse
errors** across `work/save-backups/` and the authorized
`work/r18-equipment/kareem-seed-saves/` copies. **Zero** natural adult saves have
the untouched room-13 source with door 8, door 9→12 and the room-12 silver-rupee
shutter open. All natural saves lack the Lens. The 22 door-8-open records are
old test snapshots with the source already collected; they cannot test pickup.
Natural Shadow visits only show room-0 gate/sign/wind state, not room 13.

**Correction to round 18:** `ShadowTemple_Arrive` / `Entrance` lands **before**
the room-0 Din's Fire gate, not beyond it. Native Banc/start and
`Dm_ShadowTemple_0000` agree. The earlier after-Forest slot has neither Din's
Fire nor magic (`MPMax=0`), so its quoted 30–45-minute route was not usable.
No Lens-less traversal is proposed: it would rely on unverified remake tricks.

Best natural preparation start, **not a ready fixture**:
`E:/OOTRemake/work/save-backups/2026-11-13_084401-longshot-transferred/slot_01/`.
Caption: child, Bottom of the Well, 2026-11-13 07:29:02. Progress SHA256:
`aa3dc0fa101a49d73bec15530c192d8c8b4cf5f92f459ece6081f98b026eb1ca`.
It has Longshot, Din's Fire, magic, eight bombs, Bracelet, Lullaby, Prelude and
Nocturne; Shadow's gate is open, but its source, boots and two path-key chests,
doors and room-12 rupees are untouched. The River grotto remote chest
`8838426083116998768` reads `IsTreasureBoxOpen.<Hash>=false` in this exact slot.
Parent additionally read the actual **String64** selector:
`PlayerStatus.EquipOcarina=Item_Ocarina_Time`, Time stock 1; Forest is Complete.
The natural pedestal route therefore does not borrow an age cheat or merely
assume an instrument from IsGet history.

All estimates below are **unplayed**, based on native room order/actors and
the remake guides, not measured traversal:

| Preparation leg | Minutes | Natural actions |
|---|---:|---|
| Child Well | 12–20 | Silver-rupee/water path, Lullaby, Dead Hand, obtain Lens |
| Age/entry | 3–6 | Prelude, real pedestal adult change, Nocturne or entrance teleport |
| Shadow to door 8 | 12–20 | Hidden-wall/Dead Hand route, Hover Boots, statue, room-6 rupees/key |
| Door 8 to room 13 | 18–30 | Guillotines/platforms, room-11 key, second lock, room-12 rupees/shutter; save before bombing pot |

Sources (facts only): [Shadow remake walkthrough](https://www.eurogamer.net/shadow-temple-walkthrough-zelda-ocarina-of-time),
[Well remake walkthrough](https://www.eurogamer.net/bottom-of-the-well-walkthrough-zelda-ocarina-of-time),
read-only native Banc/`Dm_ShadowTemple_0000`, and the retained r18 room-module
contracts. Full measured evidence/scripts:
`E:/OOTRemake/work/r19-keys/shadow/shadow-natural-findings.{md,json}`,
`shadow_scan.json`, `shadow_select.py`, `parent-route-prerequisites.json`.

**Maintainer question, not an overnight blocker:** approve that separate
45–75-minute natural preparation on Longshot 3.0.0, or wait for a natural
near-room-13 snapshot? Shadow remains held either way until that fixture exists.
A future pair must credit its remote Shadow key before candidate door-spending:
the replacement intentionally keeps the key model but grants 20 rupees, not a key.

## Fortress: staged four-rescue continuation, unplayed

The same 2,804-file/730-content search found **no natural 2/4 or 3/4 rescue
save**. The nearest unedited continuation is Kareem's r18 v2 diagnostic play:
`work/save-backups/2026-11-19_130612-r18-fortress-cand-b-9/5a3c9e1f0b7d24680000000000000001/slot_04/`.
Caption: Fortress, **2026-11-19 13:06:00**. Progress SHA256:
`5c92630a89c1aae545dc59fa6dd36ee7844730d06521d5e427eeb412f8c0dc69`.

- Adult, **Step01**: boss Yes is already complete. Carpenter016 rescued and
  its guard defeated; 013/014/015 untouched. Found/helped counters **1/1**,
  remaining-to-help **3**. The spent DMT key leaves Fortress **0 held / 1 found**.
- Card false/stock 0; captain/card history false; both Training Ground gates false.
  Rupees **168**, six hearts, Hookshot, Bow/30 arrows, nine bombs.
  Parent checked active **EquipOcarina=Item_Ocarina_Time**, Time stock 1,
  Storm Song learned; the adult grotto route does not rely on IsGet alone.
- Old-v2 caveat: source04's pickup Bool is still **false** although carpenter016
  is rescued. Avoid its room for this continuation; do not mistake a restored
  legacy reward for a new once-only regression. Its state is not edited.

Both independent packet-owned profiles copy only this natural slot, its
account/options and runtime controls byte-identically; **no copy edits**.
All **184** native chest Bools were read in the exact slot: 39 open, 145 closed,
zero missing. The packet pins only these three closed chests:

| Hash | Location | Exact-slot `IsTreasureBoxOpen.<Hash>` |
|---|---|---|
| `17750686910716887133` | Valley tent Storms grotto, green | false |
| `18413589940135955604` | Same grotto, invisible red | false |
| `16619432200060282313` | Fortress grounds uncovered grotto, red | false |

Their routes (including the invisible chest without Lens) have r18 chest-hunt
evidence, `r18-chests.md:29,63`; **their named Fortress-key grants are unplayed**.
Three keys, not four: the fixture already found/spent one. All four guard
source packs use main's check11 once-only red-rupee adapter.

### Paired packet and launcher proof

Base directory: `E:/OOTRemake/work/r19-keys/fortress/`.

- Main control: `ingame/Test - fortress four - main-control.bat`.
- Candidate: `ingame/Test - fortress four - candidate.bat`.
- Detailed landmarks/evidence: `fortress-handoff.md`.

Control was built from frozen main **d9deb65**; the same builder produced the
candidate. **31/31 output files are byte-identical**: Fortress runtime behavior
does not change on this track. This control demonstrates the same old behavior,
**not a fabricated bug reproduction or candidate-only fix**. Played check11's
four source packs, registries, grant flows and 16 message archives also match.
Only the packet's three chest bindings and size table differ from check11.
Inverse Banc readback preserves every guard, source, door and other field.

Launchers derive from the supplied Longshot template, require exactly one real
mod and a pre-staged profile, clear `HOS_FS_OVERLAY`, and hard-pin
`builds/stable/v3.0.0/bin/longshot.exe`. Neither contains `hookshot.exe`.
Both real **cmd.exe dry runs exit 0**, even with a poisoned incoming overlay,
selecting the expected profile/mod and **Longshot 3.0.0**. No boot/game run.
Receipts: `packet-compare.json`, `fixture-copy-proof.json`,
`banc-inverse.json`, `check11-compare.json`, `launcher-dryruns.json`,
`stage-readback.json`, `parent-route-prerequisites.json`.

### Longshot 3.0.0 checklist — built, not played

Claude boot-checks first. Run control first, then candidate from its independent
copy; **Continue the only Fortress save**, never reuse control progress.
Teleport/clock only; no inventory, age, guard, quest or source cheats.
This is a diagnostic packet, not a generated/beatable seed.

| Segment | Estimated minutes per arm | Actions and required saved outcome |
|---|---:|---|
| A: three remote keys | 5–8 | Open Fortress-grotto red, then Valley tent Storms-grotto green/invisible-red. Save. Fortress **3 held / 4 found / once true**; all three named chest Bools true. Still one rescued, Step01, no card; guards remain hostile. |
| B: two rescues | 8–12 | Fight guards013/015, collect each key-shaped **+20 rupee** get window, spend chest keys at their real cell doors, rescue each. Save. Helped **3**, remaining-to-help **1**, keys **1/4**, source01/03 true; no captain. |
| C: fourth rescue/card | 8–12 | Fight guard014, collect +20, spend last key, rescue. Captain runs once, unchanged card is usable/owned, Spirit advances Step02; only then ordinary guards clear. Save → Continue and revisit: no repeated source reward/card scene, all four rescues retained, keys **0/4**, card stock **1**, source01/02/03 true. Record legacy source04 separately; do not require it true without its optional pickup. |
| D: Training Ground entry | 2–4 | After completion, pay gate guard 30 rupees and enter only. Both native Training Ground gate Bools true, balance decreases by 30; no exploration required. |

**A–C total: 21–32 minutes per arm**, plus D. Each segment is short, but there
is no honest immediate-fourth-rescue snapshot; the pair is roughly 45–70 minutes.
Landmarks and Continue's spawn position remain unplayed. Stop if a pinned chest
cannot be found, a guard fails to appear, a key is missing, a reward repeats or
the fourth rescue does not trigger the captain; do not patch the save.

Require the **Longshot 3.0.0** header and `mods: <resource> <- <packet path>` for
the GerudoValley/GerudoFortress Bancs, four jail actor packs, EventSetting,
ActorInfo, PouchActorInfo and GetPouchContent. Check packet-owned saved counters,
collection Bools, carpenter Bools, card stock and Spirit step, not just HUD/text.

**Still unplayed:** guards/drops/doors/rescues013–015, all-four rescue completion,
captain/card scene, Training Ground entry, these three remote key grants and
post-completion Continue. The r18 one-source persistence pass proves none of
those missing checks. Fortress remains experimental/default off.

## Verification and handoff

Local main remained `d9deb65`; `git rebase main` reported the branch up to date.
On evidence head `911b3db03a`, focused retained contracts:

```sh
OOT_ROMFS=E:/Games/Hookshot/romfs CLAWSHOT_WORKERS=1 uv run pytest \
  tests/test_key_families.py tests/test_floor_keys.py \
  tests/test_jail_keys.py tests/test_key_bindings.py -q
```

**84 passed, 35.95 s.** Includes actual-dump floor/jail lifecycle graph, source,
registry/writer contracts, held Shadow in exposed modes, and inventory-only
Fortress named grants. It does not prove the game traverses or retires a source.

Sweep and full gate serialize under `work/rounds/r19/gate.lock`. The first
acquisition was refused while cs19d held the lock; no keys sweep started and no
foreign lock was changed. Driver: `E:/OOTRemake/work/r19-keys/checks.py`.

The single full-gate receipt is
`E:/OOTRemake/work/r19-keys/final-gate-proof.json`: it records the exact tested
head/main, commands, tasklist/worker policy, per-stage logs/results and overall
status. **Only `status=passed` on the handoff head permits READY.** No code or
round-file change may follow that gate; the final thread post carries observed
test totals and the same head. Gate commands:

```sh
uv run ruff format --check
uv run ruff check
CLAWSHOT_WORKERS=12 uv run --with pytest-xdist pytest -n 12
CLAWSHOT_WORKERS=4 uv run --with pytest-xdist pytest -m dump -n 12
```

Dump environment: read-only `OOT_ROMFS=E:/Games/Hookshot/romfs`,
`OOT_NUP=E:/Games/Hookshot/The Legend of Zelda Ocarina of Time [0400486024DEC000][v131072].nup`,
`OOT_DUMP=E:/OOTRemake/work/r18-issue34/combined-layered-dump`.
At each stage start, tasklist is checked; a running `longshot.exe` or
`hookshot.exe` reduces xdist to 4 and `CLAWSHOT_WORKERS` to 1. Full commands have
no supervisor deadline. No game has been launched.

Any staged check remains **built, not played** until Kareem plays on
**Longshot 3.0.0**, after Claude's boot-check. Intended handoff:
**READY (play-held)** for the Fortress completion check; Shadow remains vanilla.
