# Round 19 — Tokens (cs19d)

Agent `openai-codex/gpt-6.1-sol`; branch `r19/tokens`; base main `d9deb65`.
Issue #12: opt-in progression at the first 100-token House reward; default stays junk.
All new game behavior is **built, not played** until Kareem's paired Longshot 3.0.0 check.
No game launched, user seed/save modified, runtime folder written, version bumped, merge or push.

## Prerequisite: the missing three

The issue predates round 15's completed repair. Current `remake/token_routes.toml` and
`tests/test_world_token_routes.py` already admit all 100 unique native sources. This was
missing remake-specific data/logic, not three absent actors or an unsolved physical gap:

| Removed N64 identity | Actual remake source | Native enemy Hash | Required route |
|---|---|---|---|
| HF GS Cow Grotto | HF GS Lone Tree | 2177746409373494991 | Field tree roll, attack and low-drop touch; day permitted |
| LLR GS Rain Shed | HF GS Wetland Grotto Crate | 9047381233010434881 | Explosive grotto; child Skullwalltula kill persists; adult crate |
| LLR GS Back Wall | LLR GS Tower | 2730878115209290675 | Night; child Boomerang or adult Hookshot retrieves high reward |

The table accounts for three removed and three added sources; it does **not** assert physical
one-to-one replacements between its N64/remake columns. Census IDs, not names or positions,
identify checks. Route admission was Kareem's rc.3 packet, Claude's 2026-11-14 ruling;
its final revisit was not played and is not claimed here. Historical evidence:
`plans/rounds/r15-tokens-spec.md` section 4, `r15-scrub-tokens.md` native parity/review sections,
and source citations in `remake/token_routes.toml`.

Round 15 explicitly kept issue #12 open: once those three became reachable, a real Gift seed
put Stone of Agony at House100. Maintainer policy therefore became explicit
`nonprogression_only = true`, enforced across fill, swaps and external assignments. This
round implements the requested explicit opt-in rather than weakening reachability or defaults.
Current read-only proof: `uv run python E:/OOTRemake/work/r19-tokens/prove_tokens.py`
collects **100/100**, no missing source, and reaches/collects House100. Omitting only those
three source placements reproduces **97**, exactly those three missing, and House100 inaccessible.
Both arms win. Bootstrap matches the existing vanilla oracle: all native small keys plus
Slingshot/Hookshot for no-save-warp entry guards, **zero upfront tokens**. This is model proof,
not a fresh physical route playtest; no additional route change is justified.
Receipt: `work/r19-tokens/token-collection-proof.json`.

## Implementation contract

Proposed by cs19d from issue #12: `shuffle_100_token_reward = false`; enabling requires
Gift/NPC shuffle and removes only House100's automatic non-progression exclusion before world
compilation. Existing threshold100, NPC route, explicit item exclusions, item/type holds,
native first-reward completion and repeat payout remain. Token shuffle is independent: with it
off, collect native tokens; with it on, collect the same 100 token items from supported chests
and Skulltulas. The existing `GatheringTokenGold.bfevfl.zs` is already covered by the pack's
`Event/EventFlow/*.bfevfl.zs` resource pattern; no new native input/output path is introduced.
`test_pack_nup_dump.py` now includes an explicit option-on all-kinds parity row.
The setting has CLI, CS1 and metadata-driven app exposure; both presets stay off. False is
omitted from effective serialization like the existing Fortress switch, preserving old strings.

### Native first versus repeat

Read-only supported RomFS flow trace (no GPL source used): Event215 is
`GatheringTokenGold:TakenReward_Common_Event_200Rupee`,
`TakenRewardActor = Obj_Rupee_Gold`. The common wrapper ultimately passes that argument to
the native `Dm_SY_GetInEvent` handover; the existing Gift compiler replaces this parameter,
not the shared get flow. The first source is gated by the native quest's completion.
Event471 is the separate repeat call to `Dm_SY_GetInEvent:GetInEvent_NotTurn` with
literal `ActorName = Obj_Rupee_Gold`; it remains native. Exact node/write trace and staged
fixture provenance follow in the external packet report.

### Focused evidence so far

House/default-policy and three-route focus initially gave **36 passed, one failed** in 180.72 s.
The new native inverse test used `ActorName` at Event215; the actual parsed payload printed
`{TakenRewardActor: Obj_Rupee_Gold}`. Corrected only that test field name, not production.
The aimed native plus Settings/CLI/schema/API run is recorded in
`work/r19-tokens/focused-integrated.log`. No unchanged rerun.

Actual isolated browser proof: Recommended starts Off; clicking its native On button checks
the control and produces a CS1 string with the option; Defaults restores Off and disables the
control without Gift. Help states 100-token grind and built/not-played status. Screenshot
observed. Server used in-memory Preferences, no player paths/saves/seeds, then tab/server closed.

## Verification and staging

Pending implementation, focused proof, native prepared sweep, matched-save candidate/control,
and one exact-head locked full gate. Research and receipts stay outside the repo under
`E:/OOTRemake/work/r19-tokens/`. No READY claim yet.
