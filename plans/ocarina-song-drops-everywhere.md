# Ocarinas and songs at every shuffle kind but shops

Record of feature `ocarina-song-drops-everywhere` (spec and plan: `docs/specs/ocarina-song-drops-everywhere/`, kept
local). Branch `feature/ocarina-song-drops-everywhere`, made off `feature/song-get-effects` (PR #41). Builds on
`plans/chest-ocarina-model.md` (PR #40, D6 left this open) and `plans/song-get-effects.md` (PR #41, S3 built the song
floor actors but placed none).

## Before and after

| Location kind | Fairy Ocarina | Ocarina of Time | Songs (`--songs anywhere`) | State on this branch |
|---|---|---|---|---|
| Chest | allowed (PR #40) | allowed (PR #40) | allowed (PR #41) | unchanged |
| Gift, direct pouch grant / `GetPouchContent` | allowed | allowed | allowed | unchanged |
| Gift, show-item hand-over | excluded -> **pending 4.1, 4.2** | excluded -> **pending 4.1, 4.2** | allowed | get-model patch now goes into such seeds (task 4); `[hand_over]` lifted only after 4.2 (task 6.1) |
| Scrub / GrottoScrub | excluded -> **pending 4.2** | excluded -> **pending 4.2** | allowed | as above |
| Token | excluded -> **pending 4.3** | allowed | excluded -> **pending 4.3** | writer support done (generated donors, `song` family); members admitted only after 4.3 (task 13.2) |
| BossHeart | **allowed** (`Obj_Clawshot_Ocarina_Fairy`) | **allowed** (`Obj_Ocarina_Time`) | **allowed** (`Obj_Clawshot_Melody_*`) | in the palette now; 4.4 decides (O4) |
| Freestanding | **allowed** | **allowed** | **allowed** | in the palette now; 4.5 decides (O4) |
| Shop | out of scope | out of scope | out of scope | unchanged (pinned by a test) |

Songs reach the new kinds only with `songs = anywhere`. With `songs = song` nothing changes (pinned by a test).

## Representatives (O5)

Confirmed by BBender, 2026-11-24: **Fairy Ocarina**, **Ocarina of Time**, **Prelude of Light** (warp song) and
**Zelda's Lullaby** (non-warp song). The other ten songs are inferred from these two, not played one by one.

## Code against the spec (plan task 1.2, Claude, 2026-11-24)

Read: `plans/chest-ocarina-model.md`, `plans/song-get-effects.md`, `plans/rounds/r11-ocarina.md`, `patch/getitem.py`,
`patch/songs.py`, `patch/tokens.py`, `patch/drops.py`, `patch/freestanding.py`, `patch/gifts.py:restrict_spec`,
`generate/tokens.py`, and their neighbours in `patch/__init__.py`, `generate/fill.py:allowed`, `data/settings.toml` and
`data/token_rewards.toml`.

### Raised with BBender before coding

1. **The song floor actors are built from `Obj_Arrow_Fire`, and that actor crashed on a floor.**
   `patch/songs.py:pickup_pack` makes `Obj_Clawshot_Melody_<Song>` from `Obj_Arrow_Fire`'s pack (PICKUP_DONOR).
   `plans/03-game-data.md` section 10 (Kareem, round 2, Hookshot `foliage-linux-updater`/`main-ba594da`) records a
   freestanding heart piece swapped to `Obj_Arrow_Fire` crashing 3 out of 3 times (`OptimizeChangeBanc`, the Hookshot
   #287 signature). The only native `Obj_Arrow_Fire` belongs to an `AiGroups` logic module. `patch/drops.py`'s
   docstring and `plans/rounds/r7-drops.md` exclude it from the floor palette for that reason. PR #41's two Temple of
   Time pickups (Longshot v3.1.1, `tot_chests.py`, test only) did not crash, but they were added actors, not a
   saved heart's `Gyaml` swapped by Hash as spec 2.4 does. The spec (O8, 2.4) uses these actors on BossHeart and
   Freestanding without mentioning the crash.
   **Decision (BBender, 2026-11-24, proposed by Claude): keep PR #41's actors** as O8 says. In-game checks 4.4 and
   4.5 decide, and a crash there is a stop-and-report (O4).
2. **The token writer reads every donor from the dump.** `patch/tokens.build` reads each reward actor's pack with
   `Romfs.pack` and needs its native `PouchActorInfo` row. It checks the three tables against the native row snapshot
   before custom rows are inserted. `Obj_Clawshot_Ocarina_Fairy` and `Obj_Clawshot_Melody_*` are generated (not in the
   dump), and `songs.build` adds their rows after the token step (`patch/__init__.py`). So spec 2.3 needs the token
   writer to take generated donors: their packs, their rows, and the size entries of the members it copies from them
   (`NewFile.copied` names a source pack, which for these is not in the dump). Implementation, not a product call.
3. **`generate/tokens.restrict_settings` refuses songs.** It raises for any `REWARDS` item whose world type is not
   `Item` or `Token` ("keeps its own holds"), and songs are type `Song`. `REWARDS` is a fixed module constant, while
   spec 1.3 wants songs in the Token palette only with `songs = anywhere`. Planned: songs join `REWARDS` and
   `restrict_settings` drops them from the palette unless `songs = anywhere`. With `songs = song`, `gifts.held_items`
   already holds songs to `Song` locations, so `fill.allowed` would refuse them at a Token anyway.
4. **An entry in an admitted family is admitted at once.** `data/token_rewards.toml` admits by family, and `ocarina`
   is admitted, so a Fairy Ocarina entry would be placeable as soon as it is written. Plan 7.2 wants it held back
   until 4.3 passes. Planned: the Fairy Ocarina and song entries are not written into `token_rewards.toml` until
   BBender's run. The writer support and the tests use an explicit `rewards` set (as diagnostics already do), and
   the in-game seeds for 4.3 are built in a scratch copy with the entries added there.
5. **Plan 8.4 wording.** The plan says PR #41 writes the song floor actors "into every seed". The code writes them
   only into seeds with a moved song (`songs.moved_songs`). A song on a floor or at a Skulltula is a moved song, so
   the actor is there whenever it is needed. The test 8.4 asks for still pins this.

## Decisions taken during implementation

| # | Decision | Proposed by |
|---|---|---|
| I1 | `gifts.restrict_spec` marks every location whose grant creates the item actor (`hand_over = true`: shuffled show-item gifts and every scrub sale), the same test it uses to apply `[hand_over]`. The world keeps it as `Location.hand_over`, so the mark survives when the exclusion list empties. `getitem.get_model_ocarinas` asks for the get model when a chest or a marked location holds an ocarina (replaces the chest-only call in `make_seed`; `chest_ocarinas` stays as its helper). | Claude |

| I2 | The token writer takes **generated donors** (`tokens.GeneratedDonor`: the pack as the seed writes it plus its three rows) for reward actors named `Obj_Clawshot_*` (`tokens.GENERATED_PREFIX`). Their rows are not expected in the native tables (their own step inserts them later). Each pickup member copied from such a pack is declared copied from that member's own source, or left new (sized by formula). `native_inputs` never asks the dump for them. | Claude |
| I4 | The floor palette is `drops.floor_items(world, settings, actors)`: the native five, both ocarinas, and the twelve songs only with `songs = anywhere`, each only if the world has the item. `NATIVE_ITEMS` stays the native five. The writers accept `drops.PICKUPS` (native actors, `Obj_Ocarina_Time`, `Obj_Clawshot_Ocarina_Fairy`, the twelve `Obj_Clawshot_Melody_*`), never the bare `Obj_Arrow_Fire` or an `Item_*`. A replayed settings string keeps its own palette (intersection, as before). | Claude |
| I5 | `generate/tokens.restrict_settings` accepts `Song` items in `REWARDS` and keeps them out of the Token palette unless `songs = anywhere`. | Claude |
| I3 | A new grant family `song` (KeyItem/KeyItem, Small, deal `Melody`, one per get) in `patch/tokens.FAMILIES`. It is **not admitted** (`generate/tokens.ADMITTED_FAMILIES`) until 4.3. Admitted 2026-11-24 (I10). | Claude |
| I6 | Floor ocarinas: both get a generated actor (`Obj_Clawshot_Ocarina_Fairy`, `Obj_Clawshot_Ocarina_Time`) built on `Obj_Arrow_Fire`'s pickup body, never `Obj_Ocarina_Time`'s moat `Box` body (F1-a/F1-c); gated off floors until runs G1/TG2, then admitted (`drops.FLOOR_OCARINAS`). | Claude, BBender ("sounds good") |
| I7 | Generated floor actors (ocarinas, songs) float `drops.FLOOR_LIFT` = 0.3 m above the heart's spot (`drops.place` lifts `Translate` Y). Asked by BBender (clipping into the cow-pen roof); it also fixed F1-b (the arrow body spawning inside a cliff prop). | BBender (ask), Claude (value) |
| I8 | Ocarina floor glow: the songs' light clone alone, warm white (0.6, 0.55, 0.45), at -0.3 m (the floor), none in the get pose; `static` gets the clones from the song step's own function when no song step adds them (option A). | BBender (glow, A, warm white), Claude (values) |
| I9 | T1-a: an ocarina from a world pickup is added again by name in `Dm_SY_Get` right after its own add (`ocarina_pickup.patch_receipt`), as the native moat pickup's movie does; the Ocarina of Time's Skulltula donor moved from the native `Obj_Ocarina_Time` to `Obj_Clawshot_Ocarina_Time` (TB3-a), changing the rc.3-played `token_rewards.toml` entry. | T1-a agent (research), BBender (donor switch) |
| I10 | Admitted at Skulltulas: the Fairy Ocarina and all twelve songs (`song` family), citing runs T1 and TB3; Prelude of Light and Zeldas Lullaby played, the other ten inferred. `[hand_over]` lifted (empty), citing runs 4.1/4.2. | BBender, 2026-11-24 |
| I11 | T1-b: a Skulltula drop of an `Obj_Ocarina_Time` or `Obj_Clawshot_*` donor takes the token's own ASInfo (autoplay `Rotate_Obj`), so it spins and shows the song's floor effect; Boomerang and Hylian Shield drops unchanged (open for BBender). | T1-b agent |
| I12 | **Rebased onto PR #41 at `e0156b7`** (BBender, 2026-11-24), whose maintainers' decision (option 2) runs get-display steps by setting, lists them in the spoiler's `patch.steps`, and refuses a placement the rule does not cover (S8). Applied here: the ocarina get model runs whenever a Gift kind is on (`getitem.shown_ocarinas_possible`; wider than #41's Chest+Gift, because hand-overs and scrub sales show the item actor and crashed without it: R11, run 4.1); the ocarina world actors, glow and receipt run when a Gift kind and Token/BossHeart/Freestanding are on (`ocarina_pickup.pickups_possible`, new step `ocarina_pickups` in `patch.steps`); the song step uses #41's `songs.songs_can_move`; each refuses uncovered placements. Docs: Saria's doubled ocarina is the remake's own pre-Gohma farewell glitch (Kareem, #41), no longer listed as a cost of this feature. | maintainers (#41), Claude (applying it) |

## Edits to existing tests (plan 9.4, for BBender's approval)

| Test | Edit | Why |
|---|---|---|
| `tests/test_tokens.py` `GRANT_ROWS["song"]` | Expected family `None` -> `"song"`; the entry moves from the "no shape" group to the families. | The writer now has a `song` family (I3, spec 2.3). The row is the same. |
| `tests/test_tokens_dump.py:247` | `set(PRODUCTION.values()) == ADMITTED_FAMILIES == set(tokens.FAMILIES)` split into `PRODUCTION == ADMITTED` and `FAMILIES - ADMITTED == {"song"}`. **Back to the three-way equality after 13.2 (2026-11-24).** The dump-row checks now run on `NATIVE_PRODUCTION` (members whose donor is in the dump); the generated donors (`Obj_Clawshot_*`) have no dump row and are checked by `test_ocarina_song_drops_dump.py`. | `song` is a writer family but not admitted before 4.3 (plan 7.2); after the admission the Ocarina of Time and all `song` members give generated donors. |

| `tests/test_settings_songs.py` `test_ocarina_fill_uses_reachable_chests_instead_of_hand_over_gifts` (renamed `..._may_use_hand_over_gifts_and_keeps_the_assumed_fill_proof`) and `test_ocarina_restriction_covers_scrub_sales_in_a_mixed_pool` (renamed `test_ocarinas_may_be_scrub_sales_in_a_mixed_pool`) | Now assert the ocarinas **are** allowed at a show-item gift and a scrub sale, and that the fill still places them before the chest that needs them. | `[hand_over]` lifted (6.1/6.2, I10). Approved by BBender 2026-11-24. |
| `tests/test_generate_tokens.py`: `cannot_widen...` (2 cases), `whole_world_holds...`, `a_skulltula_reward_and_a_chest_token...`, `small_keys_and_unadmitted_items...` and the other synthetic-world tests | Their example of an item a Skulltula cannot give moves from the Fairy Ocarina to the Keaton Mask (`UNADMITTED`; the goal strings too); `EXCLUDED` loses the Fairy Ocarina and the whole world's expected givers gain it. | The Fairy Ocarina is admitted (I10). Same assertions, other example. |
| `tests/test_getitem_ocarina_dump.py` `chest_ocarina_seed` | (Dropped at the rebase: the base's own fixture already moves a displaced item through a chest that may take it, main `7694c08`.) | - |
| `tests/test_event_registration.py` recipe `broad` | Keeps the base's seed 22 and adds `FORCED`: a Deku Shield swapped onto the first one-time scrub sale whose swap fits, so the scrub-shield writer always runs. | With ocarinas and songs in the floor and Skulltula pools, no seed from 24 to 90 put a shield on a sale (printed); the base pinned 22, main has since pinned 46. Maintainers' call: keep `FORCED` or re-pin. |
| `tests/test_tokens.py` `test_spoiler_names_the_optional_steps_that_ran` (from #41) | `OPTIONAL_STEPS` also holds `ocarina_pickups`. | The new optional step (I12). |

## `Obj_Clawshot_Ocarina_Fairy`: copy plan (plan 5.1)

Read by Claude, 2026-11-24, from dump 1.1.1 (update v131072) with a scratch script; values stay out of the repo.

What the dump shows:

- `Obj_Ocarina_Time` (43 members) is a direct `Obj_Item_Base` child. Its ActorParam names `ASInfoRef` (`Item_Obj`),
  `ASRef` (`AS/Item_Common.root.asb`), `ActorNameRef` (`Item_Ocarina_Time`, so it grants its canonical item), its
  own `AnimationRef` (`[Item_Common_Animation, Item_Ocarina_Time_Animation]`), its own `GameParameterTableRef`
  (`MenuActorParam` only), `PhysicsRef` (`ObjectDefault`), and **`Item_Ocarina_Time`'s own `ModelInfo` and
  `PouchContentParam` members, byte for byte** (same paths and contents as in the Item pack). It has no ELink,
  SLink or XLink, and no `PouchActor` (the grant is the canonical name).
- Rows: its `ActorInfo` row has no `CalcPriority`, the Time model fields and `AnimationResources`, and its own heaps.
  `GameActorInfo` is `{IsRespawn: true, MainRigidBodyLayer: GroundObject}`. Its `PouchActorInfo` row is exactly
  `Item_Ocarina_Time`'s **without `OcarinaTypeValue`** (Item: 2; Fairy's Item row: 1, GetType Small).
- `Item_Ocarina_Fairy` (19 members) is equipment: Common performer, Accessory, Capture, ELink/SLink, OcarinaParam,
  `GameActorAfter`. Its `ModelInfo` (`Item_Ocarina_Fairy`, with `DebugModelScale`) and `PouchContentParam`
  (no `GetType`, no `IsPickedUpEmitXlinkKey`) are the members to copy.

The plan: build the Fairy pickup the way the game pairs `Obj_Ocarina_Time` with `Item_Ocarina_Time`.

- Pack: `Obj_Ocarina_Time`'s pack. Its ActorParam is renamed to `Obj_Clawshot_Ocarina_Fairy`, and `ActorNameRef`,
  `ModelInfoRef` and `PouchContentRef` point at `Item_Ocarina_Fairy`'s (members copied unchanged from its pack).
  `AnimationRef` points at a new `Component/AnimationParam/Obj_Clawshot_Ocarina_Fairy...` built in code as
  `[Item_Common_Animation, Item_Ocarina_Fairy_Animation]` (`getitem.animation_param`). The three Time-only members
  (`AnimationParam/Obj_Ocarina_Time`, `ModelInfo/Item_Ocarina_Time`, `PouchContentParam/Item_Ocarina_Time`) are
  dropped. Everything else is copied unchanged, `GameParameterTableRef` included.
- `ActorInfo`: `Obj_Ocarina_Time`'s row, renamed, with `ActorName` `Item_Ocarina_Fairy`, the Fairy model fields
  (`getitem.MODEL_FIELDS`) and the Fairy `AnimationResources`; the heaps stay `Obj_Ocarina_Time`'s.
  `GameActorInfo`: `Obj_Ocarina_Time`'s row, renamed. `PouchActorInfo`: `Item_Ocarina_Fairy`'s row, renamed, without
  `OcarinaTypeValue` (the native Obj/Item pairing).
- Sizes: the renamed ActorParam and the new AnimationParam get the measured formulas (`rstb.ACTOR_PARAM*`,
  `rstb.ANIMATION_PARAM*`). Every other member is declared copied from its source pack (`NewFile.copied`), so it
  keeps its native entry. The pack's own entry comes from the pack formula.
- Equip rule: `patch/ocarina.py` restores `EquipOcarina` after any Fairy pouch add in the common pouch flows,
  argument-driven grants (pickups) included. Whether a floor or Skulltula Fairy keeps the Time equipped is one more
  thing to watch in 4.3 to 4.5.

## Results

- **Fill failure baseline (plan 2, spec 1.8; Claude, 2026-11-24):** seeds 1 to 200 on `6d83c32` (clean `src/`),
  dump 1.1.1, settings as `--shuffle Chest Gift Scrub Token BossHeart Freestanding --songs anywhere` (each seed:
  `gifts.seed_setup` then `make_seed`, nothing written; `ocarina-qa/tools/fill_rate.py`, per-seed rows in
  `ocarina-qa/drops-everywhere/fill-baseline.json`, 12 worker
  processes that loaded the generator at the start, before any change on this branch). **0 of 200 failed.** 88 seeds
  put the Ocarina of Time at a Skulltula (allowed before this feature); no other ocarina or song can reach Token,
  BossHeart or Freestanding on this commit.
- **Wiring probe (task 4, Claude, 2026-11-24, not a game run):** base seed 1, `--shuffle Chest Gift --forest open
  --skip intro`, Fairy Ocarina at KF Shopkeeper Gift and Ocarina of Time at Market Shooting Gallery Reward, the
  `[hand_over]` exclusion lifted in the build process only (`ocarina-qa/tools/handover_ocarina_seed.py`). On `6d83c32`
  the output holds neither ocarina pack (`drops-everywhere/R11-nopatch`, the 4.1 seed). With task 4's change it holds
  both (`drops-everywhere/wiring-probe`).

- **Fill failure rate with the feature (spec 1.8, plan 11; Claude, 2026-11-24):** the same seeds 1 to 200 and
  settings as the baseline, on this branch (uncommitted, on `6d83c32`), with the **end state** applied in the
  build processes (`fill_rate.py --final`: hand-over exclusion lifted, Fairy Ocarina and songs admitted as Token
  rewards); per-seed rows in `ocarina-qa/drops-everywhere/fill-final.json`. **0 of 200 failed (baseline: 0 of 200).**
  Every seed put an ocarina or a song at a Token, BossHeart or Freestanding location. Placements over the 200 seeds
  (one count per item per seed):

  | Item | Token | BossHeart | Freestanding | Scrub | NPC gift* |
  |---|---|---|---|---|---|
  | Fairy Ocarina | 54 | 16 | 22 | 7 | 36 |
  | Ocarina of Time | 53 | 17 | 34 | 4 | 37 |
  | the twelve songs | 693 | 184 | 371 | 23 | 385 |

  \* NPC counts every NPC gift, direct story grants included (those were allowed before).
- **Dump checks (plan 10.3, Claude, 2026-11-24):** `tests/test_ocarina_song_drops_dump.py` (10 tests) builds
  `Obj_Clawshot_Ocarina_Fairy`, a Skulltula drop per group (Fairy, Time, Zelda's Lullaby) and a boss heart and a
  free-standing heart swapped to each group's actor, writes them with the common writer and reads every file back:
  10 passed. Whole `pytest -m dump` (8 workers): 799 passed, 60 skipped, 1 failed
  (`test_event_registration` broad recipe, fixed by the seed edit listed above; the file's 5 dump tests then passed).
- **Full checks (spec 3.3, Claude, 2026-11-24, after every change above):** `ruff format --check` (584 files) and
  `ruff check` clean; `pytest -n auto` 4558 passed, 862 skipped; `OOT_ROMFS=... pytest -m dump -n 8` 800 passed,
  60 skipped.
- **Determinism (spec 1.9, Claude, 2026-11-24):** one seed with Ocarina of Time at KF Shopkeeper Gift (hand-over),
  Fairy Ocarina at Deku Tree GS Compass Room (Token), Zelda's Lullaby at Queen Gohma's heart (BossHeart), Prelude of
  Light at Kak Impa's House PoH (Freestanding) and Song of Storms at LW Deku Scrub Near Bridge (scrub), built twice in
  two processes (`ocarina-qa/tools/twice.sh`, end state applied in the build process): all 229 output files
  byte-identical (`ocarina-qa/drops-everywhere/determinism/A.sha`, `B.sha`).
- **In-game seeds and sheets (plan 12.1, Claude, 2026-11-24)** in `ocarina-qa/drops-everywhere/`, each with its
  `sheet.json` (seed, settings string, commit, changed files, forced placements, spheres):
  - `R11-nopatch/SHEET.md`: 4.1 (on `6d83c32`, no get-model patch).
  - `SHEET-4.2.md`: seeds `H1`, `H2` (both ocarinas at KF Shopkeeper Gift and LW Deku Scrub Near Bridge).
  - `SHEET-4.3-4.6.md`: `T1` (four Deku Tree Skulltulas), `F1` to `F4` (Queen Gohma's heart and child-reachable
    free-standing hearts), and 4.6 in `H1`.
  These seeds are built by `ocarina-qa/tools/drops_qa_seed.py --final`, which lifts the hand-over exclusion and admits
  the new Token members in its own process only (the end state tasks 6.1 and 13.2 wait on), and refuses placements
  that fail the beatability search.

- **4.1 R11 reproduction (BBender played, Claude read the log, 2026-11-24): reproduced.** Seed `R11-nopatch`
  (`6d83c32`, no ocarina get-model patch, Fairy Ocarina at KF Shopkeeper Gift), Longshot stable v3.1.1, new game; the
  Kokiri Sword was given with debug tools (the seed had it in Bottom of the Well). Proof:
  `mods: Event/EventFlow/Npc_Kokiri_001_Shop_Child.bfevfl.zs <- ...R11-nopatch-mods\qa
omfs\...`. Talking to the
  shopkeeper for his gift crashed the game: `CRASH: exception 0xc0000005 (read 0x100000000270, guest 0x270)` on
  `BaseProcExecutor4`, `x0 = 0`, which is R11's crash. Log: `ocarina-qa/runs/R11-nopatch/log.txt` (crash from line
  32170). Step 2 (Ocarina of Time at the Slingshot Gallery) was not played; the crash is shown by step 1.
- **4.2 seed H1 (BBender played, Claude read the log, 2026-11-24): pass.** Longshot stable v3.1.1, new game, H1 as
  the only mod; sword, shield and rupees given with debug tools (not under test). Ocarina of Time at KF Shopkeeper
  Gift (show-item hand-over): no crash, the model looked correct. Fairy Ocarina at LW Deku Scrub Near Bridge (scrub
  sale): no crash, it works. Both owned afterwards; the Ocarina of Time stayed the equipped one (as native). Proof (`ocarina-qa/runs/H1/log.txt`, no `CRASH:` lines): `mods:` lines for
  `RSDB/ActorInfo.Product.111.rstbl.byml.zs`, `Event/EventFlow/Enemy_Scrub_Business_Common.bfevfl.zs`,
  `Event/EventFlow/Npc_Kokiri_001_Shop_Child.bfevfl.zs`, `Pack/Actor/Item_Ocarina_Time.pack.zs` and
  `Pack/Actor/Item_Ocarina_Fairy.pack.zs`, each `<- ...runs\H1-mods\qa
omfs\...`.
- **4.2 seed H2 (BBender played, Claude read the log, 2026-11-24): pass.** Same setup as H1, ocarinas swapped: Fairy
  Ocarina at KF Shopkeeper Gift (hand-over), then Ocarina of Time at LW Deku Scrub Near Bridge (scrub): no crash at
  either, both work, both owned, and the Ocarina of Time became the equipped one (as native). Proof
  (`ocarina-qa/runs/H2/log.txt`, no `CRASH:` lines): the same five `mods:` lines as H1, each
  `<- ...runs\H2-mods\qa
omfs\...`. With H1 this passes 4.2 for both ocarinas at both grant paths.
- **4.6 Saria's farewell, seed H1 (BBender played, 2026-11-24): the known D5 glitch, nothing worse.** Same run as
  H1's 4.2 (`ocarina-qa/runs/H1`, ocarina get-model patch in the seed, `mods: RSDB/ActorInfo.Product.111.rstbl.byml.zs
  <- ...runs\H1-mods\qa
omfs\...`). Saria showed the ocarina-in-hand glitch (D5); no crash or softlock. Recorded
  as the known issue (O9).
- **4.3 seed T1, in progress (BBender played, Claude read flags and log, 2026-11-24).** Longshot stable v3.1.1, new
  game (relaunched once on a fresh user folder so nothing comes from sequence breaks), T1 as the only mod; debug tools
  for sword/shield. Proof: `mods: Pack/Actor/Obj_GoldSkulltulaDrop_Obj_Clawshot_Ocarina_Fairy.pack.zs`,
  `Banc/InsideTheDekuTree/InsideTheDekuTree_{Static,Dynamic}.bcett.byml.zs` and the three RSDB tables, each
  `<- ...runs\T1-mods\qa
omfs\...`; no `CRASH:` lines.
  - Fairy Ocarina (GS Compass Room): drop shows the Fairy Ocarina model, does not spin or glow; normal pickup.
    Ocarina of Time (GS Basement Gate): the same. Zelda's Lullaby (GS Basement Vines): Fairy Ocarina model (by
    design, PR #41 `SONG_MODELS`), **no song effect** on the drop, no spin; wall pickup, so no get pose to see.
  - Flags after the three: `IsGet.Item_Ocarina_Fairy` 1, `IsGet.Item_Ocarina_Time` 1, `IsGet.Item_Melody_ZeldaLullaby`
    1, `PlayerStatus.EquipOcarina` `Item_Ocarina_Time` (Time stays equipped after the Fairy, as native).
  - **Finding T1-a: the ocarina cannot be played right after a Skulltula ocarina** (left arrow does nothing), though
    the flags say owned and equipped. **After Save and Continue it plays** (BBender), flags unchanged. The hand-over
    and scrub grants (H1/H2) played at once; they run an event flow, the drop grants without one. Working cause: the
    HUD/equipment sync (`EventTriggerSyncPlayerEquipmentAndPouch`) that the event grants end with never runs.
  - **Finding T1-b: the song's floor effect does not show on its Skulltula drop**, while PR #41's floor pickup shows
    it. No drop spins (C4 noted the same for `Obj_GoldSkulltulaDrop_Obj_Ocarina_Time`), so the drop probably never
    plays the state the effect is attached to. Not yet investigated.
  - Zelda's Lullaby plays after the reload (BBender). Prelude of Light (GS Basement Back Room): the floating drop
    shows the Ocarina of Time model (warp song, by design) with no effect, as T1-b. **Brought in with the boomerang it
    showed the get animation correctly: spinning, with the Prelude sparks** (BBender), and Prelude played at once,
    without a reload (the ocarina already worked after the earlier reload). `IsGet.Item_Melody_LightPrelude` 1,
    `EquipOcarina` still `Item_Ocarina_Time`. So T1-b concerns the floating drop only; the pickup itself carries the
    song's effect. All four drop packs loaded (`mods:` lines for
    `Obj_GoldSkulltulaDrop_Obj_{Clawshot_Ocarina_Fairy,Ocarina_Time,Clawshot_Melody_ZeldaLullaby,Clawshot_Melody_LightPrelude}.pack.zs`).
  - Save and Continue: all four Skulltulas stayed dead (BBender). The ocarinas and Zelda's Lullaby were read owned
    after the earlier reload; after the last one the bridge stopped answering flag reads (status still answered), so
    Prelude's `IsGet` after the reload is not read. **4.3: pass on the grant, collection and persistence; findings
    T1-a (ocarina unplayable until a reload) and T1-b (no spin/effect on the floating drop) open for BBender's call.**
- **4.4 seed F1, Queen Gohma's heart = Fairy Ocarina (BBender played, Claude read flags and log, 2026-11-24):
  finding F1-a.** Seed `F1-fast` (as F1, rebuilt with every untested skip on, full wallet, Kokiri Sword and Slingshot
  forced early; `drops_qa_seed.py --final --fast`). Proof: `mods: Pack/Actor/Obj_Clawshot_Ocarina_Fairy.pack.zs <-
  ...runs\F1-mods\qa
omfs\...`; no `CRASH:` lines. The Fairy Ocarina showed on the floor and **rotated**, but
  **Link could not pick it up: an invisible box (four sides and a floor) around it, which Link grabs and hangs on
  ("Let Go")** (BBender's screenshot). After noclipping into the box, the pickup was normal and looked correct.
  `IsGet.Item_Ocarina_Fairy` 1, `EquipOcarina` `Item_Ocarina_Fairy`; not playable until a reload (as T1-a). Back in
  the room: no item and no box (stays collected). Working cause, unverified: `Obj_Ocarina_Time`'s pack (the base of
  `Obj_Clawshot_Ocarina_Fairy`) carries a physics body of its own, which the floor pickup keeps; the native
  `Obj_Ocarina_Time` at Kakariko (F1) will show whether the base has it too. Dump (Claude, 2026-11-24): the
  `Obj_Ocarina_Time` pack's physics are `Component/Physics/ObjectDefault` with a **`Phive/ShapeParam/Box`** body
  (`RigidBodyEntityParam/Box`, `Ptm_ObjDynamicLarge_*`), a large dynamic object's; the floor pickups use pickup
  bodies instead: `Obj_Heart_Piece` (`HeartPiece` physics, `Heart_Body`, `Item_Pouch_Tgt`), `Obj_Heart_Container`
  (`Heart` physics) and `Obj_Arrow_Fire` (its own physics, `Item_Pouch` controller, `Rupee_Tgt` sensor: the song
  floor actors' base, which BBender collected normally in PR #41). Saves copied to
  `ocarina-qa/saves/F1-gohma` (slots 00-04) for F2 to F4.
- **4.5 seed F1, ZR Near Domain Freestanding PoH = Zelda's Lullaby (BBender played, Claude read log and files,
  2026-11-24): finding F1-b, nothing there.** BBender on the waterfall ledge: no model, nothing collectable when walking
  the ledge (screenshot); no crash. The log shows `mods:` for `Banc/ZoraRiver/ZoraRiver_Child_{Static,Dynamic}` and
  `Pack/Actor/Obj_Clawshot_Melody_{ZeldaLullaby,LightPrelude}.pack.zs`. The seed's `ZoraRiver_Child_Static` has the
  placement at Hash 4189391771527808272 with `Gyaml` `Obj_Clawshot_Melody_ZeldaLullaby` and the native heart piece's
  Translate/Rotate unchanged. Working cause, unverified: the `Obj_Arrow_Fire` base (code-vs-spec finding 4): the game's
  only `Obj_Arrow_Fire` is spawned from an `AiGroups` logic module, and a plain placement of it crashed three times out
  of three in round 2 (`03-game-data.md` section 10). Here it loads but never appears.
- **4.5 seed F1, ZR Near Open Grotto = Prelude of Light: pass** (BBender, screenshot): the model and its effect
  showed, the pickup worked, the song played; `IsGet.Item_Melody_LightPrelude` 1. Same scene and same base as the
  missing Lullaby (F1-b), and both heart pieces have the same native shape (each linked from its own
  `HeartPieceAnchor`, in no group), so the files do not explain F1-b. BBender's idea: only one such pickup per loading
  zone. Open.
- **4.5 seed F1, Kak Impas House Freestanding PoH = Ocarina of Time (native `Obj_Ocarina_Time`): finding F1-c, the
  same invisible box as F1-a**; picked up normally after noclipping in. So the box is the native `Obj_Ocarina_Time`'s
  own (its `Box` physics), not the Fairy build's: neither ocarina can sit on a floor with that body. The HUD kept
  the Fairy Ocarina after the pickup; after Save and Continue the Ocarina of Time is equipped (BBender) and the flags
  read `IsGet` 1 for both, `EquipOcarina` `Item_Ocarina_Time`: the stored value was right, the HUD stale (T1-a).
  Saves copied to `ocarina-qa/saves/F1-cow`.
- F1-b, second look (2026-11-24): BBender on the ledge after Prelude was collected, still nothing; Link read at
  (101.95, 119.82, -60.92), 2.6 m from the placement (99.49, 120.10, -61.73), so the right spot. So it is not "only
  one at a time" in the sense of the collected Prelude blocking it. The log has no line about the Lullaby actor beyond
  its pack opening (no missing file); its ActorInfo/GameActorInfo rows have the same shape as Prelude's (Arrow_Fire
  radii and heaps, the Fairy model fields). Open causes: the actor's Arrow_Fire body falls through the ledge or into
  the river after spawning (the heart piece's model sits on its origin, the arrow's is centred), or a per-scene limit
  on Arrow_Fire-based pickups. Not verified. Saves: `ocarina-qa/saves/F1-zr-ledge`.
- **4.4 seed F3, Queen Gohma's heart = Prelude of Light (BBender played, 2026-11-24): pass on what was seen.**
  `F3-fast`, started from F1's post-Gohma save (`saves/F1-gohma`, slot 03) so the room spawns F3's item. Proof:
  `mods: Pack/Actor/Obj_Clawshot_Melody_LightPrelude.pack.zs` and
  `Banc/InsideTheDekuTree/InsideTheDekuTree_{Static,Dynamic}.bcett.byml.zs`, each `<- ...runs\F3-mods\qa
omfs\...`;
  no `CRASH:` lines. It looked right, no invisible box, the pickup worked, and it stayed gone after re-entering the
  room. The save has no ocarina, so playing the song is not checked; the bridge did not answer the flag read at the
  time; read later in normal play: `IsGet.Item_Melody_LightPrelude` 1 (`IsGet.Item_Ocarina_Fairy` 0, so the save was
  from before F1's Fairy pickup).
- **4.4 seed F4, Queen Gohma's heart = Zelda's Lullaby (BBender played, 2026-11-24): pass on what was seen.** Same
  start as F3 (`saves/F1-gohma`, slot 03). Proof: `mods: Pack/Actor/Obj_Clawshot_Melody_ZeldaLullaby.pack.zs <-
  ...runs\F4-mods\qa
omfs\...`; no `CRASH:` lines. It appeared and looked right, the pickup was clean, and it stayed
  gone after re-entering. So the same actor that never appeared on Zora's River's ledge (F1-b) works at the boss
  heart: F1-b is tied to that placement or scene, not to the Lullaby actor. The flag read did not answer at the time.
- **16.4 seed G1, Queen Gohma's heart = Fairy Ocarina on the new arrow-based `Obj_Clawshot_Ocarina_Fairy`
  (BBender played, Claude read flags and log, 2026-11-24): no box.** `G1` (`drops_qa_seed.py --final --fast`, floor
  ocarinas admitted in the build process only), started from `saves/F1-gohma` slot 03. Proof: `mods:
  Pack/Actor/Obj_Clawshot_Ocarina_Fairy.pack.zs <- ...runs\G1-mods\qa
omfs\...`; no `CRASH:` lines. It looked
  good on the floor and the pickup was fine (BBender). `IsGet.Item_Ocarina_Fairy` 1, `EquipOcarina`
  `Item_Ocarina_Fairy`; not playable at once (G1 was built before the T1-a sync fix).
- **16.4 seed G1, Kak Impas House Freestanding PoH = Ocarina of Time on the new `Obj_Clawshot_Ocarina_Time`
  (BBender, 2026-11-24): no box,** looked as the Fairy did, normal pickup, still gone after coming back. BBender's
  cosmetic notes for all floor pickups: the ocarinas sit very low (on the cow-pen roof the model clips into the roof);
  asked for the model and effects raised a bit so they float, and a slight floor glow for the two ocarina pickups (like
  the songs' light, without sparks or aura).
- **17 T1-a, first fix attempt (Claude, 2026-11-24): did not help.** `patch/ocarina.py`'s helper in
  `GetPouchContent` now ends with `EventTriggerSyncPlayerEquipmentAndPouch` after every ocarina receipt, and runs for
  argument-driven Time receipts too. Seed `G1s` (with it, and the 0.3 m floor lift), from `saves/F1-gohma` slot 03:
  the Fairy at Gohma floats nicely and the pickup works, **but still cannot be played** (BBender). Printed: `mods:
  Event/EventFlow/GetPouchContent.bfevfl.zs` (the patched flow loaded), `IsGet.Item_Ocarina_Fairy` 1, `EquipOcarina`
  `Item_Ocarina_Fairy`, `UI_MessageTargetActorName` `Item_Ocarina_Fairy`. So either the pickup's grant does not pass
  the patched event (an entry of `GetPouchContent` that skips the add, or a grant in code), or the sync is not what
  makes the instrument playable. Native: the sync appears in four flows only (`DreamBossStage`, `Npc_Dream`,
  `SubEvent_AllBossBattle`); both native first ocarinas come inside a movie (`Dm_Kokiri_0155`, `Dm_MelodyGet_Time`),
  whose grants are literal adds with no extra step. Kept for now (harmless, tested); open.
  BBender: the HUD **does** show the ocarina icon after the pickup, and has since the first run; only the button does
  nothing. So the HUD is not stale: what is missing is the player's ability to use the instrument (likely the
  player's ocarina equipment actor, created at scene load or at an event's end), not the HUD sync.
- **17 T1-a, what was ruled out (BBender played, Claude, 2026-11-24).** In `G1s` after the Fairy at Gohma: opening
  and closing the pause menu, a loading zone, and an event (talking to the Kakariko gate guard) do **not** make the
  ocarina playable; only Save and Continue does. Second attempt, seed `G1t`: the pickup's `PouchActorInfo` row with
  `OcarinaTypeValue` kept: **no change**. Both attempts reverted (the sync change and its three test edits, and the
  row field); the code keeps the native pattern. BBender's hint: after the native first ocarina the game opens a
  window saying to press the arrow button. Found: `ActionGuide.bfevfl` entry `OpenActionGuideSceenForOcarina` (opens
  the action guide, then, if `ActionGuide_IsRequestOcarina`, transitions to `Dm_SY_Ocarina` and clears the flag),
  called only from `Dm_SY_BancChangeArrive`'s `Dm_SY_BancChangeArrive_HyruleField` branch (`EntryPoint_1stHyruleField`,
  wait 70 frames, the guide, autosave): the first arrival in Hyrule Field after Saria's farewell.
  `ActionGuide_IsRequestOcarina` read 0 in G1t. Whether that guide or `Dm_SY_Ocarina` is what enables the button is
  not shown; a loaded save evidently derives the ability from the inventory. Open: plan 17.1.
- **17 T1-a, third probe (test only, 2026-11-24): seed `G1u`** = `G1s` with `ocarina-qa/tools/ocarina_guide_probe.py`
  applied: after both argument-driven adds of the seed's `GetPouchContent` (events `Event0` and
  `Clawshot_Content__content_Event0`), an ocarina (message target Fairy or Time) calls
  `ActionGuide:OpenActionGuideSceenForOcarina`; RSTB entry updated (979504 -> 982192). BBender: Fairy at Gohma, **no
  window, still not playable.** Not conclusive on its own: the guide entry's `OpenActionGuideSceen` checks
  `HaveOpenedActionGuide` with an `ActionGuideType` argument the probe did not pass. Stopped here (rule 9) after three
  attempts; next needs a way to see what runs at a world pickup (an event-flow trace in Longshot, or a guest-memory
  comparison of the pouch/player state before and after Save and Continue). Longshot has no event-flow trace option
  documented (searched `docs`, `host`).
- **18 F1-b: cause and pass (agent research; BBender played, Claude read flags and log, 2026-11-24).** Research
  (`ocarina-qa/f1b/`): both Zora's River ledges have the same native shape; the bodies differ: `Obj_Heart_Piece`'s
  body has `EnableLayerHitMask: HitOnlyPlayer` (mass 1200), the `Obj_Arrow_Fire` body the generated floor actors use
  collides with everything (layer Object, mass 25). At the waterfall ledge the heart's origin (Y 120.10) is up to
  0.106 m inside the top of the cliff prop `Land_ZoraRiver_Cliff_B_16`, so the arrow body spawned in the rock and was
  lost; the grotto ledge is open terrain. The 0.3 m lift (`drops.FLOOR_LIFT`) puts the body's bottom 0.19 m above the
  prop. Seed `F1B-1` (Lullaby there, lifted to Y 120.401), from `saves/F1-zr-ledge` slot 02: **"perfect"**
  (BBender); `IsGet.Item_Melody_ZeldaLullaby` 1; `mods:` `Banc/ZoraRiver/ZoraRiver_Child_Static.bcett.byml.zs` and
  `Pack/Actor/Obj_Clawshot_Melody_ZeldaLullaby.pack.zs` `<- ...runs\F1B-1-mods\...`; no `CRASH:` lines. No code
  change beyond the lift. The control seed `F1B-0` (no lift) was not run. The audit (bounding boxes, coarse) lists other
  spots with props near the origin (e.g. Gerudo Valley's `SmallShrine`), which may need a larger lift: open.
- **17 T1-a: cause and fix (agent research; BBender played, Claude read flags and log, 2026-11-24).** A world
  pickup is granted in `Dm_SY_Get` by `PouchContentGuestPerformer.EventTriggerAddOwnToPouch`, never by
  `GetPouchContent`'s add (why the three earlier attempts changed nothing). The instrument's equipment actor
  (`Item_Ocarina_*.pack.zs`) is created on a hand-over's grant, but for a pickup only on a game load
  (`Sequence/AfterLoadSaveData`: `SeqOneShotPouchTargetSyncEquipmentIndex`, `WaitEquip`); natively the moat pickup is
  followed by `Dm_MelodyGet_Time`, which adds `Item_Ocarina_Time` again by name. Fix (`ocarina_pickup.patch_receipt`,
  `receipt_changes`, wired in `make_seed` when `picked_up`): right after the own add in `Dm_SY_Get`, if
  `UI_MessageTargetActorName` is an ocarina, that ocarina is added again by name (Num 1, `IsEquipDIrect` False,
  `IsGetEvent` False, as `Dm_Kokiri_0155`); `ocarina.patch_grants` binds its keep-Time helper to the new literal
  Fairy add. Tests: `tests/test_t1a_receipt.py`. Seed `TG1` (with the glow and lift), from `saves/F1-gohma` slot 03:
  Fairy at Gohma **played right away** (BBender; the pause menu was opened once first, which alone did not help in
  G1s; to be confirmed without it in TG2). `IsGet.Item_Ocarina_Fairy` 1, `EquipOcarina` `Item_Ocarina_Fairy`,
  `PouchData.Item_Ocarina_Fairy.StockNum` 1 (the second add does not double it); `Item_Ocarina_Fairy.pack.zs` opened
  at log line 15396, in play, with no load; `mods:` `Event/EventFlow/Dm_SY_Get.bfevfl.zs`; no `CRASH:` lines.
- **Glow, first look (TG1):** the warm white light at Prelude's -0.15 m lit the ocarina harshly from close below, on
  the floor and in the get pose (BBender's screenshot). Changed: floor light at -0.3 m (the floor the pickup was
  lifted from), get pose unlit (`GET_POSE_GLOW`). Seeds `TG2`, `TB3` carry it.
- **16.4 and 17 on floors, seed TG2 (BBender played, Claude read flags and log, 2026-11-24): pass, "no notes".**
  Same placements as TG1, with the glow at -0.3 m and none in the get pose, from `saves/F1-gohma` slot 03. Fairy at
  Gohma and Time at the Kakariko cow pen: glow fine, both played at once without opening a menu, Time equipped after.
  Flags: `IsGet` 1 for both, `StockNum` 1 for both, `EquipOcarina` `Item_Ocarina_Time`. `mods:`
  `Effect/static.Nin_Ounce_NVN2.vsetb.byml.zs`, `ELink2/elink2.Product.110.belnk.zs`,
  `Event/EventFlow/Dm_SY_Get.bfevfl.zs`, `Pack/Actor/Obj_Clawshot_Ocarina_{Fairy,Time}.pack.zs`, each
  `<- ...runs\TG2-mods\...`; no `CRASH:` lines. `drops.FLOOR_OCARINAS` now admits both (runs G1, TG2 cited). Not
  played: Time at a boss heart, Fairy at a free-standing heart (same actors and writers as the played pairs).
- **19 T1-b: cause and fix (agent research; BBender played, 2026-11-24).** The native token spins because
  `Obj_Token_Gold`'s ASInfo has `AutoPlayASName: 'Rotate_Obj'`; the ocarina and song pickups' `Item_Obj` ASInfo has
  none (on a floor their `DropItem` AI starts `Rotate_Obj`), and a Skulltula drop pairs the donor's `Item_Obj` with the
  token's AI, so nothing played `Rotate_Obj`, the state the song effects wait for. Fix (`tokens.py`, `spins`): the drop
  of an `Obj_Ocarina_Time` or `Obj_Clawshot_*` donor takes the token's own ASInfo member (copied byte-identical); the
  build refuses a donor ASInfo that differs from the token's in anything but the autoplay. Played Boomerang and
  Hylian Shield drops unchanged (they do not spin either; BBender's call). Tests: `tests/test_t1b_drop_spin.py`.
- **4.3/17.3/19.3 seed TB3 (BBender played, Claude read flags and log, 2026-11-24): pass apart from one finding.**
  New game, all skips; Deku Tree Skulltulas: Compass Room = Prelude, Basement Vines = Zelda's Lullaby, Basement Gate
  = Fairy Ocarina, Basement Back Room = Ocarina of Time. BBender: every check as expected (drops spin, songs show
  their effect while floating, the Fairy plays at once) except: **finding TB3-a**, after the Ocarina of Time drop the
  HUD shows Time but the instrument played is still the Fairy; after Save and Continue it is Time. Log: the Fairy
  drop's pickup (line 29764) opens `Item_Ocarina_Fairy.pack.zs` at once (29768); the Time drop
  (`Obj_GoldSkulltulaDrop_Obj_Ocarina_Time`, 33812/33893) never opens `Item_Ocarina_Time.pack.zs`: the receipt in
  `Dm_SY_Get` does not fire for the drop built on the native `Obj_Ocarina_Time`. Flags: `IsGet` 1 for both ocarinas
  and both songs, `EquipOcarina` `Item_Ocarina_Time`, Time `StockNum` 1. No `CRASH:` lines. Proposed: make
  `Obj_Clawshot_Ocarina_Time` the Time Skulltula donor too (pending BBender).
  **Finding TB3-b:** first-time green/blue rupee and recovery-heart pickups showed only the text, no get animation;
  Deku Sticks and Nuts were normal. `Dm_SY_Get` differs from native only on the ocarina branch (native round-trip
  byte-identical; events 187 -> 192, event 7's next and one helper call). Likely cause: the QA seeds' full wallet
  (`--fast` sets `starting_full_wallet`; a full wallet or full health has no room, so no get pose). Not verified.
- **TB3-b settled, seed NS1 (BBender played, 2026-11-24): the missing first-pickup animations come from the QA
  skips, not from this feature.** `NS1` = TB3's placements with every change of this branch but no skips and no full
  wallet (`drops_qa_seed.py --final --noskip`; built at idle priority on one core). New game: the first rupee and
  recovery-heart pickups played their get animation normally (BBender). Which skip (full wallet or a fast-start
  scene) suppresses it was not narrowed down; it is a QA-seed artefact.
- **17.3 seed TB4 (BBender played on Longshot v3.2.0, Claude read flags and log, 2026-11-24): known issue
  TB3-a remains for a second ocarina at a Skulltula.** TB3's placements with the Ocarina of Time donor switched to
  `Obj_Clawshot_Ocarina_Time`. Fairy Ocarina (Basement Gate) first: the instrument loads at once
  (`Item_Ocarina_Fairy.pack.zs`, its holder and models, line 26161) and plays. Then the Ocarina of Time (Basement Back
  Room, `Obj_GoldSkulltulaDrop_Obj_Clawshot_Ocarina_Time`, line 29819): flags right (`IsGet` 1, `StockNum` 1,
  `EquipOcarina` `Item_Ocarina_Time`, `UI_MessageTargetActorName` `Item_Ocarina_Time`), the HUD icon loads, but
  **`Item_Ocarina_Time.pack.zs` never loads and Link still plays the Fairy Ocarina**; leaving the Deku Tree through a
  loading zone does not change it; Save and Continue does (TB3). On floors (TG2: Fairy at Gohma, then Time at
  Kakariko) the Time instrument loaded at once. So the donor switch was not the cause; the runtime does not swap an
  instrument that already exists after a Skulltula grant. **BBender's call: accepted as a known, temporary cosmetic
  state** ("i can live with it"), not investigated further. The donor switch stays (the arrow-based drop also spins
  and glows like the Fairy's).

### Other things noticed (no disagreement)

- O7 bases `Obj_Clawshot_Ocarina_Fairy` on `Obj_Ocarina_Time`, while PR #41's song pickups are based on
  `Obj_Arrow_Fire`. The two new actors will differ in their world-pickup base.
- `Obj_Ocarina_Time` is already a native world pickup with its own AnimationRef (the played Token donor), so the
  Ocarina of Time needs no new actor on floors.
- The `ocarina` family shape (`patch/tokens.FAMILIES`) accepts GetType Small or Large with deal `Ocarina`, so the
  Fairy Ocarina's row should already match it. Songs need a new `song` family shape (deal `Melody`, R11 audit).
