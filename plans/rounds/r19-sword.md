# Round 19 — sword (cs19c)

Branch `r19/sword`, base `d9deb65cedf841495ef3bbe2fb2d1083fa42bb43`.
Model: `openai-codex/gpt-6.1-sol`. **NOT READY: Kareem played v2 and hit a white-screen freeze.** Initial gate/READY below are historical; the native-receipt repair requires boot-check and replay.

## Contract and questions

Follow `r18-master-sword-design.md`: optional default-off Master Sword shuffle; pedestal remains a real age transition and its first-pull item is separate from Rauru's reward. No sword ownership fabricated by era swaps or cinematic props. Adult combat logic requires a real blade, with native alternate weapons retained. Finale admission requires owned Master Sword before irreversible entry.

**Proposed validation boundary (cs19c): require existing `free_time_travel=true` and Chest shuffle when Master Sword shuffle is enabled, rather than silently enabling free travel or implementing a new post-pull guarantee policy. Awaiting maintainer response on cs-r19; unsupported combinations will have a clear error.**

Round-19 overview/track files were absent at start; this track record is newly created. No roadmap edit. Research, generated files, saves and logs only under `E:/OOTRemake/work/r19-sword/`. Source dump and all original saves remain read-only. No game launch, merge, push or version bump.

## Implementation and evidence

Implementation commit `418780a970c35dd6fb9e6e8338dc3320782cfec2`. Built behavior is not played until Kareem runs staged Longshot 3.0.0 checks with main controls. Gate and sweep receipts pin source heads externally; no READY claim before completion.

### Runtime design / explicit refinements

- `patch/master_sword.py` composes **after** the round-18 `equipment` transform. It guards the adult default, saved incoming blade and outgoing cinematic stash. Each actual adult candidate is checked independently; an owned Biggoron/Giant/BrokenGiant is not rejected merely because Master is missing. Guards require canonical `IsGet` **and positive saved StockNum**, not an equipped model or a stale get-history bit. The native pre-swap one-frame wait and child/shield handling stay.
- Live GameData inspection confirmed Bool/Int rows for all four canonical `Weapon_Sword_{Master,Biggoron,Giant,BrokenGiant}` identities; no corresponding `Item_Sword_*` saved ownership rows. Int comparison pins reuse the existing progressive-magic convention: equal0 / less1 / greater2. Bool/equipment equality uses true0 / false1.
- **Original v2 mechanism, superseded after played failure below:** first-pull `DoorOfTime/Event115` called ordinary `GetPouchContentByActorName`. The180-frame wait did **not** make this a normal visible/UI-safe context: it is still the white-faded boot handoff before the age write. Native first-pull history, age/story chain, Rauru and Door completion must remain.
- **Refinement to design9.2:** do not create an unowned temporary cinematic blade at all. `0070`/`0088` keep a genuinely selected/owned Master pose but skip force-and-poll setup for any other selected weapon, preserving a chosen alternate rather than relying on unverified cleanup. `0085`'s native large-blade exclusions remain; its dynamic Master request additionally requires real ownership. This movie has no GameDataActor, so a registered SubFlowSwitch calls the shared ownership-return entry in the already-used era flow instead of adding a movie actor. Animations/travel remain; visual/runtime acceptance is held.
- AllSage/Event175 and Dm_SY_BancChangeArrive/Event37 get additive selected-and-owned-only prop guards. Lacs/scenes explicitly left these actions to sword on cs-r19; their entry-local changes must compose. No native story action/flag is replaced by a fake grant.
- Finale guard precedes first Ganondorf admission's native GameSafety/temporary-save chain (`Event170` non-dream pin before Event43), and also guards Ganon admission (`Event771` non-dream pin before Event727). Missing Master returns to real exterior StartPos `GanonCastleEntrance` (Hash16478939697790907191), GameBancInfo `GanonCastle`; no quest/inventory writer on refusal. Dream temporary-inventory branches remain native. Native source/destination proved, **not played**.

### Private fixtures and early evidence

- `E:/OOTRemake/work/rounds/r19/sword-layered-dump`: copied the provided read-only combined layered fixture and added only `Pack/Actor/Weapon_Sword_Master.pack.zs` (31321 bytes) from read-only RomFS. Original fixture/dump untouched. Explicit pack manifest entry and option-on cache parity rows added.
- Natural first-pull profile: `work/save-backups/2026-11-09_1022-main-adult-first/save/5a3c9e1f0b7d24680000000000000001/slot_02`; source progress SHA256 `a4afee4dea4b428c1ce77d421042c080593fd6de1f2f5711656bde5fa0d80fa5`. Direct reader proof: child=true, Door Step06, `_0040`/Rauru/Sheik histories=false, Master IsGet=false/stock0, exact pinned River chest `IsTreasureBoxOpen.8838426083116998768=false`. No save edit.
- Main control archived from actual `d9deb65`; candidate archived from `418780a970`. Both v2 diagnostic packets built13 matching resource paths through their respective writers, same pinned River Master chest and existing free-travel patch. Candidate pedestal gives20 rupees; control keeps native first-pull grant. `packet-{main,candidate}-proof.json` records each resource hash; `packet-paired-proof.json` proves matching path sets, untouched profile hashes and both real cmd dry runs exit0 resolving Longshot 3.0.0 stable, one mod, overlay unset, CRLF/no Hookshot launcher. Earlier non-v2 main packet is withdrawn and never played. `report_play.py` read both isolated copies: child=true, Master=false/stock0, current Kokiri/other-era empty, first pull=false, exact pinned chest=false. No boot/play.
- First builder attempt timed out during whole-census scanning, before any packet existed. Printed load: CPU100%, Defender67% process CPU. Cause-directed change scans only the pinned River Banc files; scoped control built successfully. No unchanged timeout rerun.
- One premature runtime pytest attempt failed **collection** because the in-flight logic slice's `generate/swords.py` did not yet exist. No tests executed, no pass claimed; rerun only after integration.
- Checklist: `work/r19-sword/ingame/CHECKLIST.md`, **Longshot3.0.0**, estimated35–55min (unmeasured), main native grant; candidate no-sword first pull; unowned real-pedestal round trip; chest find/manual equip; owned round trip and reload. Claude boot-checks; Kareem plays. Script reads only isolated v2 profiles. No suitable natural swordless finale state is fabricated; short packet does not certify finale or all story prop scenes.

`--print-settings` remains serialization-only for the free-travel dependency; app validation and generation enforce it. Chest/type validation is immediate. Existing defaults and off CS1 omit the new field.

### Logic and completed focused proof

The on-only pedestal source uses `generate/swords.py`; Master is held to Chest, the pedestal to ordinary actor-backed Items (no progressive copy/tier, named dungeon credit, Token, shop refill or Master itself). It uses fill's existing ordered palette/held-item stages, not a new late hold. `SWORD_PEDESTAL_SOURCE` is the shared internal kind. Off, the adapter returns its input unchanged and the serialized setting is absent. Disagreeing derived logic and sliced worlds without the pedestal are refused.

`adult_sword` requires Master or durable Biggoron when on; child-only weapon alternatives are explicitly age-gated. Mixed stun/kill helpers preserve their named sword-free alternatives. Explicit boss strikes, Dark Link and the final entrance are covered. Existing override owners are edited in place, keeping original `was`; translated files remain untouched. **Deviation from r18's counterfactual:** Giant's Knife cannot certify indefinite progression because its break is unmodelled; runtime still preserves a genuinely owned knife. Dormant unverified glitch branches remain unavailable rather than newly admitted.

Native room follow-through (`room-fights.json`, `chest-gates.json`, `room-predicates.json`) replaced two guessed N64 constraints: Forest Map's module has only its ordinary treasure box, and the Light Trial key is a glass chest in room13 without an enemy binding. Neither now acquires a fabricated sword gate. The actual Forest Floormaster and Shadow Map/Compass bind enemy counters and treasure-appearance modules, so their clearance helpers are required only on. Bow/Stalfos, Hover/Dead Hand, GTG Wolfos/Torch Slug/Keese and Shadow after-wind Gibdo bindings support the other guarded fights. GTG's third heavy-block glass chest is behind the already-guarded Wolfos room; the fourth is an unshuffled trap. Shadow Invisible Spikes has no native chest (existing r4 override). Ordinary Light Trial chests and the Wind Hint glass chest have no enemy-counter/chest binding in the examined Banc data; no new defeat gate is invented from their names. These are native-data facts/conservative clearance predicates, **not played combat certification**.

- Native/runtime/settings/child-repair focus: **217 passed in35.99s**. First run printed the interpreter's missing native `EventQueryIsEventSkipedMostRecent` case after80 passes; model corrected, native non-skipped dream path then passed. No production retry/timeout added.
- Logic/settings/naming focus after native corrections: **64 passed in25.54s**. Earlier off-equivalence failure printed Forest Map requiring a Blue Bubble stunner while native old rule was True; all added constraints now explicitly fold off, and the unsupported Map assumption was removed after native audit.
- Actual CLI option-on seed190007: **179 shuffled checks,31 spheres,116 resources written**, external `smoke-defaults/`. First smoke correctly failed the new internal source's old generic preflight; counting the implemented source fixed it. This is file/solver proof, not game play.
- Actual isolated browser: default Off, attempted On without free travel showed the explicit refusal; enabling real Free time travel produced valid On/CS1. Visual `ui-sword-on.webp`; tab/server closed. Discovery was redirected to this track's empty seed root, never personal seeds.
- Scoped formatter changes applied through anchored edits. Scoped lint printed import ordering and one comparison style warning; both fixed from those exact diagnostics. Full format/lint remain part of the gate.

No game started. No save was edited. No version change.

### Mandatory option-on sweep — passed

Source `418780a970c35dd6fb9e6e8338dc3320782cfec2`, atomic owned `gate.lock`, no supervisor deadline. Canonical production `make_seed` preparation (including native Gift/key/source admission) captured immediately before generation, not a copied legacy setup. Seeds190000 onward per cohort; broad recipe from `E:/OOTRemake/work/r18-fill/settings.txt`. All three turn Master Sword shuffle on **and explicitly enable its required free-time-travel prerequisite**; no other recipe change. Tasklist checked at each cohort start: no game,12 workers throughout. Total387.484s.

| Recipe | Accepted | Exhausted | Fill attempts | Maximum attempts |
| --- | ---: | ---: | ---: | ---: |
| Broad | 200 | 0 | 211 | 2 |
| Defaults + option/prerequisite | 50 | 0 | 50 | 1 |
| Recommended + option/prerequisite | 50 | 0 | 53 | 2 |

Every accepted seed passed generation's goal/beatability oracle, contained exactly one Master Sword in a Chest and included the shuffled pedestal. No retry-bound increase or fill-algorithm change. Exact effective CS1 recipes, every per-seed result and wall times: external `sweep-results.json` / `sweep-rows.jsonl`. Lock released by its owner. This proves solver acceptance, not in-game swordless combat.

### Exact-head gate / final handoff protocol

This evidence-only commit freezes the merge candidate; runtime/data remain the swept and staged `418780a970` implementation. **After this commit**, `work/r19-sword/gate.py` rebases current local main, runs the focused native/runtime/logic/settings/child-repair set, acquires its own atomic gate lock and executes exactly one full gate on the frozen HEAD:

1. `uv run ruff format --check`.
2. `uv run ruff check`.
3. `CLAWSHOT_WORKERS=12 uv run --with pytest-xdist pytest -n 12`, dump environment unset.
4. `CLAWSHOT_WORKERS=4 uv run --with pytest-xdist pytest -m dump -n 12`, real `OOT_ROMFS` / `OOT_NUP` and private `OOT_DUMP=E:/OOTRemake/work/rounds/r19/sword-layered-dump`.

At every stage start a running Longshot/Hookshot reduces pytest to4 and CLAWSHOT_WORKERS to1. CPU/Defender load evidence precedes suites. No supervisor deadline. `gate-results.json` is the authoritative exact source HEAD, main HEAD, commands, exits and times; `gate-{focused,format,lint,synthetic,dump}.log` retains output. Final cs-r19 handoff reports actual outcomes/commits only after completion; no source edit after that gate. If main moves before merge, rebase and re-gate per round rule.

**Acceptance left for morning:** Claude boot-checks the paired Longshot 3.0.0 launchers; Kareem plays the control and candidate checklist (35–55min unmeasured), retaining runtime load lines plus first-pull, found/equipped, unowned and owned real-age-round-trip and Save/Continue results. No full playthrough, story-prop animation, arbitrary destination presentation or finale refusal is certified by the short packet. Product validation boundary above remains explicit for maintainer review. Target readiness kind is **READY (play-held)**, never a played/merge-ready claim.

## 2026-11-20 played failure and native handoff repair

Kareem **played** the main control: Light Medallion and Master Sword as expected. Candidate v2 **froze**, white screen after the sword-pull movie and before Ganondorf/Rauru/Sheik. This withdraws READY; the original full gate is not a gate for this repair. No agent reran the game to confirm his report.

Evidence: `work/r19-sword/ingame/user-r19-sword-candidate-v2/longshot_log.txt` proves the actual DoorOfTime and ReplaceEquipmentForEraChange mod loads (2529–2530); last map handoff is `SageRoom (child)` (4798), with no subsequent adult/Rauru handoff. Copied snapshot `work/save-backups/2026-11-20_095745-r19-r19-sword-candidate-v2-1/.../slot_02/progress.sav` has child=true, Master=false/stock0, pull/Rauru/Sheik histories=false and Door Step06. **That persisted snapshot is pre-completion state, not a live suspended VM/event stack.**

Native trace: `SageRoom_MeetGanondorf` → Event94 (`Dm_TimeTemple_0040`, FadeInTypeEventEnd2) → Event186 (180 frames) → Event115 (atomic pouch receipt) → Event98 (era equipment) → Event103 (child=false) → Event144 (adult SageRoom/Rauru boot reservation). V2 replaced the atomic receipt with a dialog-bearing subflow. Its real `GetPouchContentByActorName` immediately enters `GetPouchContent`: get-window setup/dialog occur **before** its pouch-add action. **[INFERENCE]** The new dialog wait under the retained white fade is the freeze mechanism; the log/localized graph support it, but no runtime event-stack trace is available. No evidence supports deleting/changing the native continuation or inventing a sword actor.

Repair preserves the native Event115 **ActionEvent and next edge**, changing only its Actor to the placed reward and `IsEquipDIrect` to false. `IsGetEvent=false`, Num1 and message target remain native. No added dialog, scene, fade, timer, temporary sword or saved flag; age/cutscene continuations unchanged.

**Explicit deviation from r18 design9.1 / v2:** the pedestal reward is credited by the native nonblocking receipt **without a separate get window**. The standard get subflow at this exact boundary was not lifecycle-safe; this is not a silent skip of a stuck dialog or a timeout. The chest-found Master Sword's real window remains part of replay acceptance. Public settings help and v3 checklist state the changed presentation. No READY/feature-complete/play-success claim from this repair.

The old source-wiring assertion was replaced with a real-native first-pull execution regression. It follows the source, actual era transform and age/reservation effects; resolves any inserted native get subflows (so the v2 window setup fails the no-UI handoff contract), checks placed-item credit, unchanged Master ownership, owned/unowned equipment, both write-visibility models and no repeat reward. Focused runtime/child tests: **205 passed in30.11s**. Scoped `ruff format --check` and `ruff check`: passed. No fill, logic, settings or resource-list change; no full gate/sweep rerun for this boot-check request.

V2 mods, played profiles/logs and provided snapshot are preserved. Fresh v3 profiles start from the same untouched natural pre-pull Nov9 save, not an edited/repaired frozen save. Candidate rebuild/real-cmd dry-run receipts and exact source commit are recorded externally as `packet-*-v3-proof.json` and `packet-paired-v3-proof.json`; control resources must match the played main control. **NOT READY until replayed.**

### V3 built and posted for boot-check (not READY)

Repair commit/source `4ab3cc5b4c9bbdf4aec5605170a0dce43d75dacc`; fresh paired launchers are `work/r19-sword/ingame/Test - sword candidate v3.bat` and `Test - sword main v3.bat`. Current `ingame/CHECKLIST.md` is v3; the old checklist is preserved as `CHECKLIST-v2-failed.md`. Both real cmd dry runs exit0 and resolve **Longshot 3.0.0** stable, one mod, overlay unset. Each has13 resources and an independent untouched Nov9 profile with the original SHA256, Master=false/stock0 and the pinned chest's named Bool=false. Fresh main's resource hash map equals the played main control's; candidate differs from failed v2 only in DoorOfTime and its resource-size table. Proof: `packet-paired-v3-proof.json`. No agent boot/play.

**Claude's product steer:** prefer a visible normal window after the scene, but explicitly allow a silent v3 if that is not safe this round. Inspected cs19a's played `scene_handoff.py`: it dispatches a separately registered ordinary FlowchartEvent with no animation resources. It does not simply insert a get subflow later in the old movie. Native adult return here still chains `AllSage/Market_Adult_AllSage_Start` → `_0050` (fade2) → `_0055` (fade0) → player warp → three quest steps. A deferred presentation would need its own audited ordinary-event boundary/registration and must **not grant the already credited item twice**. V3 takes the approved silent fallback, rather than add another unplayed transition to this repair. No separate pedestal window, even after adult control; stated in public settings help and the checklist.

Boot-check/replay estimate: **25–40min candidate**, optional fresh native control8–12min, unmeasured. Existing played control remains valid because the new control resources match. Priority is first-pull handoff through Rauru/Sheik to adult control without Master, then real unowned age round trip, chest get/manual equip, owned age round trip and Save/Continue. `report_play.py --revision v3` reads only the new profiles. V2 failure evidence remains untouched. **NOT READY until replayed; no fresh full-gate claim.**
