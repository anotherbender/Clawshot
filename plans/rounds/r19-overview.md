# Round 19 overview (2026-11-19 21:30 to 2026-11-20)

Eight tracks on `openai-codex/gpt-6.1-sol`, launched on main `d9deb65`, rebased onto the 0.2.3 release commit
`f5c679d` once it was published. Merges were held until 0.2.3 shipped. Integrated main `6b5a5f2`; release
candidate 0.2.4 at `d1895c4`.

| Track | Outcome | Played (Longshot 3.0.0 stable) | Round file |
|---|---|---|---|
| scenes | Merged. One table-driven scene handoff: Minuet, Impa and Saria's Song lessons hand over the item directly only when Link has no ocarina at all; either ocarina keeps the native lesson at either age. Optional `skip_saria_farewell` (experimental, off). | Minuet, Impa, Saria farewell candidates PASS (morning); Minuet stock v2, both arms, PASS 14:16 | [r19-scenes](r19-scenes.md) |
| lacs | Merged. Light Arrows cutscene logic follows the game's own trigger (Shadow and Spirit awakening scenes), in every mode; vanilla bridge follows the Temple story. | Not played: static event-data evidence only | [r19-lacs](r19-lacs.md) |
| tokens | Merged. `shuffle_100_token_reward` (experimental, off; needs Gift) lets the first 100-token reward hold progression (#12). | PASS (Hammer at 100, then the repeating gold rupee) | [r19-tokens](r19-tokens.md) |
| sword | Merged. Master Sword shuffle (experimental, off; needs Chest and free time travel). v2 white screen and v3 second-pull freeze fixed in v4 by not waiting on unowned equipment. Event-registration guard test across all modified flows (suspected risk, not a proven cause; played market bottle allowed). | v4 candidate PASS and v4 control PASS (16:21) | [r19-sword](r19-sword.md) |
| keys | Merged. Help and docs wording only; Shadow floor key stays in its usual place until a natural pre-room save exists. | Fortress four-rescue packet unplayed (optional) | [r19-keys](r19-keys.md) |
| ui-startup (audit track) | Merged. Saved-seed tests no longer spawn a process; only the real job tests keep a 60 s wait. Ended the round's startup-timeout flake. Also the crash-comparison audit and the integration gate. | n/a | [r19-ui-startup](r19-ui-startup.md), [r19-audit](r19-audit.md) |
| cows | Research only. v1 froze at the item window; v2 silent probe gave plain milk, no +20; branch traced to the only milk edge, cause not localized. Save-only check still open. | v1 froze; v2 no freeze, no signal | [r19-cows](r19-cows.md) |
| fill | Rejected. Gift-hold fill candidate raised first-attempt failures from 2.5% to 11.5% (zero exhausted). Code stays on `r19/fill`; record on main. | n/a | [r19-fill](r19-fill.md) |

**Integration gate** on combined main `4717a16`: format, lint, synthetic 4038 passed; 300-seed sweep with all
three new opt-ins on (Broad 200/200, Defaults 50/50, Recommended 50/50, zero exhausted); dump 788 passed and 3
failed because the new registration test did not list `scene_handoff`. Test-only fix `6b5a5f2`; those tests
then passed on the dump.

**Lessons recorded** (skill `game-recomp-modding`, `references/clawshot-ingame-checks.md`): no normal get window
inside a running scene; don't let a scene wait on equipment the player may not own and test every cut;
registration gaps are a suspected risk, check played evidence before "fixing" a shipped flow; version every
launcher name and rename superseded ones `OLD`.

**Process:** a fixed gate order (`work/rounds/r19/gate-order.txt`) replaced racing for the lock; tracks whose
tooling cannot commit merges were integrated by Claude on `*-int` branches and fast-forwarded.
