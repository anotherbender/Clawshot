# Songs as ocarinas: get models, effects and floor pickups

Investigation by Claude with BBender, 2026-11-22 to 2026-11-23. Clawshot `feature/ocarina-get-model` (on `b3d0ad1`),
dump 1.1.1 (update v131072), Longshot v3.1.1. BBender reviewed every visual in game; Claude built the test mods.
Observations marked *(BBender)* are BBender's; every other claim comes from the dump (research scripts outside the
repository) or a run's log. **Implemented in `src/` on `feature/song-get-effects` (spec and plan:
`docs/specs/song-get-effects/`); not committed yet.** This file records the final visuals, how the research build
made them, and the results of the implementation (oracle, in-game checks). The experiment history (runs SA1 to T16, dead ends, the light-arrow ring and
the near-camera fade) is archived outside the repository in `ocarina-qa/_archive/song-effects/`.

## The goal

A song found in a chest, at a gift or lying on the floor should look like a song, not like the green rupee songs
natively show (`Item_Melody_*` ModelInfo is `Obj_Rupee`). The ocarina model, made distinct per song by an effect
(E1).

## Final visuals *(BBender, confirmed in game 2026-11-23, runs SONGS and SONGS3)*

- Models (`getitem.SONG_MODELS`): non-warp songs use the Fairy Ocarina, warp songs the Ocarina of Time. It spins and
  lies flat (the chest-ocarina recipe, `chest-ocarina-model.md` run O).
- Non-warp songs: their own `Ply_Ocarina_Correct_{ZeldaLullaby,EponaSong,SariaSong,SunSong,TimeSong,StormSong}_00`,
  scale 0.3, on the pickup (`Wait`) and in the get pose (`GetDemo`). Both calls use **bone `Root`, `PositionY` 0**.
  The copied heart-container `GetDemo` call carries `Bone: Skl_Root` and `PositionY: -0.21`; left as it is, the
  get-pose effect leans with the held ocarina (Storms and Sun visibly crooked) and sits off the ocarina (Saria's ring
  below and beside it) *(BBender, run SONGS2)*. Overriding both on `GetDemo` stands them upright and centred
  *(BBender, run SONGS3)*.
- Warp songs: the player's sword-charge effect `Ply_ChargeLv3_Loop_02` split into three effects of its own, each
  tinted separately: **sparks** (emitter `Spark_Small`), **aura** (`Glow_L` + `Glow_Long_00`) and **light**
  (`LineLight`, the light cast on the ocarina, floor and Link).
  - Shape, same for every song: 4 sparks and 4 aura copies on a circle of radius **0.12** m around the ocarina's
    vertical axis (0, 90, 180, 270 deg), plus **1** light in the centre. All spray straight up (`RotationX`
    **-1.5708**: ELink rotations are radians), `LifeScale` **0.5**, bone `Root`, spinning with the ocarina.
  - Floor pickup: `Scale` **0.6**, starting **0.15** m below the ocarina. Get pose: `Scale` **1.0**, **0.3** m below.
  - Colours: ELink R, G, B multipliers on the effect's own colours (the sparks are light blue and the aura strongly
    blue-green, so red needs large values; the light starts near white and needs small values):

    | Song | Where | Sparks | Aura | Light |
    |---|---|---|---|---|
    | Minuet | floor | 0.1, 1.5, 0.1 | 0.05, 0.75, 0.05 | 0.015, 0.225, 0.015 |
    | Minuet | get pose | 0.08, 1.2, 0.08 | 0.065, 0.975, 0.065 | as aura |
    | Bolero | floor | 12, 0.03, 0 | 12, 0.03, 0 | 3.6, 0.009, 0 |
    | Bolero | get pose | 7, 0.02, 0 | 7, 0.02, 0 | as aura |
    | Serenade | floor | 0.025, 0.1, 2.5 | 0.015, 0.06, 1.5 | 0.0045, 0.018, 0.45 |
    | Serenade | get pose | 0.025, 0.1, 2.5 | 0.015, 0.06, 1.5 | as aura |
    | Requiem | floor | 5, 0.08, 0 | 3, 0.048, 0 | as aura |
    | Requiem | get pose | 2.8, 0.045, 0 | 1.68, 0.027, 0 | as aura |
    | Nocturne | floor | 0.8, 0, 2 | 12, 0, 0.6 | 3.6, 0, 0.18 |
    | Nocturne | get pose | 0.8, 0, 2 | 12, 0, 0.6 | as aura |
    | Prelude | both | 3.5, 0.40, 0.15 | 15, 0.0875, 0.04 | 0.6, 0.5, 0.35 |

    The floor light of Minuet, Bolero, Serenade and Nocturne is the aura colour times **0.3**: at the aura colour it
    lit the floor too brightly *(BBender, run SONGS2)*; at 0.3 it is right *(BBender, run SONGS3)*. Requiem and
    Prelude keep theirs. The get-pose light is unchanged.

    Exact values, as built: `ocarina-qa/song-gallery/warp_sparks.json`.
- Floor pickups float 0.62 m above the floor (no pedestals).

## How it is built (the gallery, `ocarina-qa/song-gallery/`)

`build.sh` builds the whole state from the dump and the seed base `S/mod/qa`, deterministically (two builds are
byte-identical); `launch.sh` launches it windowed at the title (load the `at-tot` save: Temple of Time, row L of the
carpet the warp songs, row R the others). Steps, each a research script in `ocarina-qa/tools/`:

1. **Effect file** (`vfx_tool.py clone`): three clones of `Ply_ChargeLv3_Loop_02` in `static`, each with the other
   emitters dropped: `Clawshot_ChargeSpark`, `Clawshot_ChargeAura`, `Clawshot_ChargeLight`.
2. **Effect table** (`gallery.py` `Elink.add_clone`): one user `Clawshot_Song_<Song>` per song, a copy of
   `Obj_Heart_Container`'s. `elink_tint.py`: `Wait` and `GetDemo` get `RuntimeAssetName` (non-warp: the song's
   effect, `Scale` 0.3, and on `GetDemo` also `Bone: Root`, `PositionY: 0`; warp: `Ply_ChargeLv3_Loop_02`,
   `Bone: Root`). The calls of the copied user, after these overrides:

   | Call | Inherited from `Obj_Heart_Container` | Set |
   |---|---|---|
   | `Wait` | `BitFlag` 4, `Bone: Root`, `ModelAlphaLink` 1 | `RuntimeAssetName`, `Scale` |
   | `GetDemo` | `BitFlag` 4, `Bone: Skl_Root`, `PositionY` -0.21 | `RuntimeAssetName`, `Scale`, `Bone: Root`, `PositionY` 0 |

   (`Item_Appear_Amiibo`, `Item_Drop`, `Item_Land` stay as copied.) Warp children copy their call's record and
   override position, rotation, scale, life scale and colour (`warp_sparks.json`), so they keep `Bone: Root`. `elink_container.py` with `warp_sparks.json`:
   the warp songs' `Wait` and `GetDemo` become play-all containers of the nine children above.
3. **Song actors** (`song_aura.py`, `ASINFO_FROM=Obj_Heart_Container`): pack with the ocarina's ModelInfo,
   `ASRef: AS/Item_Common.root.asb`, own AnimationParam `[Item_Common_Animation, <ocarina>_Animation]`, ELinkParam,
   ASInfo, `XLinkRef`; ActorInfo row with the ocarina's model fields and `ELinkUserName`.
4. **Floor pickups** (`song_pickup.py`): new actor `Obj_Clawshot_Melody_<Song>` from `Obj_Arrow_Fire` (below).
5. **Placement** (`tot_chests.py`, slots in `tot_slots.json`). Test only; seeds place nothing new.

`elink_params.py BELNK` prints every `Clawshot_*` call with all its parameters, for comparing builds.

## How an effect reaches an actor

- **Effect user.** `Component/ELink/<x>.engine__component__ELinkParam.bgyml` = `{"UserName": U}` in the pack, and
  `ELinkUserName: U` in the ActorInfo row. The row makes the game load the user's effect file; with only the row the
  file is loaded and nothing plays.
- **`XLinkRef: ?Component/XLink/ActorBasic.engine__component__XLinkParam.bgyml`** (a resident resource; no pack
  member) runs the triggers. Songs lack it natively; without it nothing fires.
- **`ASInfoRef`** (`Item_GetDemo` or `Item_Obj`, native member, native size entry) and `ASRef: AS/Item_Common.root.asb`:
  get-pose triggers wait for `Rotate_GetDemo` in slot `Skl[Lower]` or `AS[Lower]`; floor triggers for `Rotate_Obj`.
- **Which actor shows the get pose.** For a floor pickup the game holds up the granted item (the song actor
  `Item_Melody_*`), not the pickup, so the song actor needs the user too. One user per song serves both: the pickup
  (`Wait`) and the song actor (`GetDemo`). Chests and gifts show the song actor as well.
- **Bones.** The ocarinas have `Root` and `Skl_Root` only.
- **Which file an effect comes from.** A user's effects must be in the always-loaded `static` set or in the effect
  file `EffectFileInfo` maps the user's name to. Everything used here is in `static`, so no mapping is needed.
- **Colour.** `Red`/`Green`/`Blue` on a call multiply the effect's own colours; some effects ignore them. The charge
  effect takes them.

## The effect table (`ELink2/elink2.Product.110.belnk`)

The game loads `.110`. XLNK version 36, decoded from the file itself (`elink_dump.py`; no other tool's code read).

- Header 0x60: absolute positions (u64) of the trigger-overwrite table (0x18), local property names (0x20), first user
  (0x40), condition table (0x50), name table (0x58); counts: direct values 0x30, users 0x48.
- Users: u32 CRC32(name), sorted, at 0x60; then (8-aligned) u64 absolute offsets. User data is self-relative (calls,
  triggers, parameter positions are relative), so a user's bytes can be copied as a new user.
- Parameter definitions: 4 user, 58 asset, 14 trigger parameters. Asset parameter index = define index - 4:
  AssetName 0, RuntimeAssetName 1, Matrix 10, Bone 12, Scale 13, PositionX/Y/Z 14-16, RotationX/Y/Z 17-19,
  Red/Green/Blue/Alpha 20-23, LifeScale 28, BitFlag 29, UseCalcFrustumCulling 41, ShaderParam0-7 42-49.
- Asset parameter records: u64 bit mask + one u32 per set bit, `(type << 24) | value`; type 1 = name-table offset,
  type 0 = direct-value index (4-byte floats). Records are shared between calls.
- A user: +0x04 low u16 local property count (u64 names each, before four u32 user params), +0x08 call count, +0x0C
  asset count, trigger counts, +0x30 trigger table position (user-relative), u16 call indices sorted by key name
  (4-aligned), then 0x30-byte calls {u64 key name, s16 asset id (-1 = container), u16 flag (1 = container), s32
  duration, s32 parent, u32 guid, u32 CRC32(key), pad, u64 parameter record (relative to the asset parameter table),
  u64 condition}.
- **Containers.** A container call's param field is the **byte offset** of its 16-byte record `{3, first child, last
  child, 0}` in the container block after the calls (type 3 plays every child). New children are appended after the
  existing calls: trigger entries name calls by byte offset from the first call, so they stay valid; only the trigger
  table position moves. **Asset ids are renumbered 0, 1, 2 ... in call order** (all native users do this). Child
  conditions: get pose `0x4FC0` (tests `UICaptureScene`; from `Item_FairyBless_MP`), floor `0xF20` (constant, type 2,
  value 1.0; from `Obj_Rupee_Red`'s `Wait` container).
- Writing: append direct values, parameter records and names (shifting the header positions and user offsets), point
  calls at them; new users are inserted in hash order. Every build checked: all native users decode unchanged and
  every other section is byte-identical.

## The effect files (`Effect/*.Nin_Ounce_NVN2.vsetb.byml`)

Decoded from the files themselves (`vfx_tool.py`).

- Outer BYML **version 5** (the repo's reader handles 7 only): root `{Esets: [names], PtclBin: binary node 0xA2
  (u32 size, u32 alignment, data at the next aligned offset), Textures: [dicts]}`; in `static` the root dict and the
  arrays come after the blob.
- `PtclBin` = `BFFH` (header size 0xA8, alignment 0x1000), sections `BFSI`: `Default` (0x1000..) and `StringPool` (to
  the end). Pointers are u64 offsets from the blob start; **the loader fixes them up by walking references, so an
  object referenced twice crashes the game**.
- Root object at 0x1000: +0x30 u64 effect table, +0x38 u32 count (569 in `static`), entries 0x68 bytes: +0x00 name,
  +0x08 the emitter pointer list `{u64 pointer, u32 count, u32 element size}`, more descriptor vectors after it.
  Effects' data regions lie in table order; an emitter's block holds only pointers into itself or into the string
  pool.
- **Clone**: copy the effect's data region to the blob end (pointers shifted, none outside), drop emitters from the
  copy's pointer list, write a new effect table (count + 1) with the renamed copy, point the root at it, grow the
  blob, the `StringPool` section and the outer BYML (blob node size; every node after the blob shifted). The new name
  need not be added to `Esets`.

## Floor pickups

New actor `Obj_Clawshot_Melody_<Song>` built from `Obj_Arrow_Fire`: the arrow's pack with its ActorParam renamed;
`ActorNameRef` to the song's ActorName; the song's ModelInfo (ocarina); own AnimationParam `[Item_Common_Animation,
<ocarina>_Animation]`; own PouchContentParam `{$parent: song's KeyItemMelody, PouchActor: the song,
GetDemoOffsetPos}`; own ELinkParam; the arrow's GameParameterTable/SLink/Capture refs dropped. Rows: ActorInfo and
GameActorInfo from the arrow (ocarina model fields, `ELinkUserName`, `ActorName` = the song), PouchActorInfo from the
song. Collected with A: the song is learned and listed *(BBender)*.

## Size entries (measured on dump 1.1.1)

- `*.engine__component__ELinkParam.bgyml`: size rounded to 32 + 5064 (1309 of 1309 unique pack members).
- ELink file: size + 272 (both files). `EffectFileInfo`: size rounded to 32 + 264 (both files).
- `static` effect file: native entry = size + 4160; the grown file used size rounded to 32 + 4160 + 0x10000 (a margin,
  not a measurement).
- Effect files, all 1432 native `Effect/*.vsetb.byml` (measured by Claude 2026-11-23, dump 1.1.1, research script
  outside the repository): **no one constant fits** (spec S7, plan 5.6). Entry − size takes 9 values (264 to 288, and
  4160); entry − size rounded to 32 takes 2: **264 for 1431 files**, 4136 for `static` alone (size 52,401,096,
  entry 52,405,256). Stopped here for BBender's call before any `static` entry is written. BBender: "try to find a
  formula". What sets `static` apart (Claude, same script): 569 effects (the others at most 114), 393 textures (at
  most 108), its blob at 0x9000 (the others at 0x1000, 0x2000 or 0x3000; those at 0x2000/0x3000 fit +264). The 1431
  others keep +264 whatever their size (up to 34,933,832 bytes), effect, texture or string count, so nothing
  measured on them predicts the extra 3872 (0xF20); it rests on `static` alone. A formula of `static`'s own,
  rounded + 4136, equals its native entry plus its rounded growth.
- ELink files: entry − size = 272 and entry − size rounded to 32 = 264 for both `.100` and `.110`: both formulas fit
  both files. They differ for a grown file: size + 272 is up to 16 bytes below rounded + 264 when the size is 8 or
  16 more than a multiple of 32.

## Decisions

| # | Decision | By |
|---|---|---|
| E1 | Effects instead of recoloured textures; per-song colours | BBender |
| E2 | Test in the Temple of Time; floor pickups floating, no pedestals | BBender |
| E3 | Close any running Longshot automatically before each launch | BBender |
| E4 | Warp songs: four charge sparks, colours and sizes above (supersedes the light-arrow ring, which is faded out near the camera in the get pose) | BBender |
| E5 | Non-warp songs: their own song effect, scale 0.3 | BBender |
| E6 | Non-warp get pose: effect upright and centred on the ocarina (`Bone: Root`, `PositionY` 0) | BBender |
| E7 | Warp floor light: Minuet, Bolero, Serenade, Nocturne at 0.3 of the aura colour | BBender |
| E8 | Warp get-pose light: every warp song at 0.3 of its SONGQA1 value (Minuet, Bolero, Serenade, Requiem, Nocturne: the aura colour x 0.3; Prelude its own light x 0.3); `data/song_effects.toml`. The gallery and the oracle above predate it | BBender |

## Open

- For the maintainers: whether songs may become free-standing pickups in seeds, and whether every seed gets the song
  models and effects or only seeds that move songs.
- Not checked in game yet: a song from a chest and from a gift with the final effects, and the sparks with a turned
  camera (the effect sits on the ocarina, so it should not depend on the camera).
- The get-pose light is dimmed to 0.3 too (E8); not seen in game yet. Requiem's and Prelude's floor lights stay as they were (E7).

## Oracle: `src/` against the gallery (plan task 10)

Claude, 2026-11-23, dump 1.1.1, branch `feature/song-get-effects` (uncommitted, on `566c159`). Seed 4242,
`--shuffle Chest Gift --songs anywhere`, written to `ocarina-qa/song-seed-feature`; compared with
`song-gallery/mod/qa/romfs` (decompressed) by `ocarina-qa/tools/oracle_songs.py`:

- **Byte-identical: 25 of 26 files**: `static` (52,746,792 bytes), all twelve `Item_Melody_*` packs and all twelve
  `Obj_Clawshot_Melody_*` packs.
- **`.110` differs, as expected** (plan decision "ELink names"): 2,442,344 bytes against the gallery's 2,442,368. All
  1279 users decode the same (every call, parameter, container, trigger table and local property); the header
  sections, definitions, direct values and condition table are identical. Only the name table differs (the gallery's
  research script appended `Clawshot_ChargeSpark` twice and kept 4 padding bytes between its build stages) and with
  it the name offsets inside the new parameter records.
- Not compared: size entries (the gallery used a margin for `static`, `src/` the measured formulas, S7).

Accepted by BBender, 2026-11-23. (Since E8 the `.110` also differs from the gallery in the dimmed get-pose light
values, as intended.)

## In-game checks (plan task 11): seed for BBender

BBender runs every in-game check himself. QA seed (Claude, 2026-11-23, same uncommitted branch): seed 4242,
`--shuffle Chest Gift --songs anywhere`, songs forced into early spots by `ocarina-qa/tools/song_qa_seed.py` (a normal
fill, the songs swapped in, the displaced items moved to chests that held rupees, then `make_seed(placements=...)`,
which checked beatability). Output: `ocarina-qa/song-qa-seed` (mod romfs, spoiler.json).

| Spot | Song | Kind | Check |
|---|---|---|---|
| KF Kokiri Sword Chest (big, `Obj_TBox_A_02`) | Sun's Song | non-warp | 4.1 |
| Deku Tree Map Chest (big) | Bolero of Fire | warp | 4.1 |
| KF Mido's House top left chest (small) | Zelda's Lullaby | non-warp | 4.1 |
| KF Mido's House top right chest (small) | Minuet of Forest | warp | 4.1 |
| KF Shopkeeper Gift | Prelude of Light | warp | 4.2 |

Run **SONGQA1** (BBender, 2026-11-23, Longshot v3.1.1, the QA seed from a fresh game; log
`ocarina-qa/runs/SONGQA1/log.txt`): `mods:` lines for `ELink2/elink2.Product.110.belnk.zs`,
`Effect/static.Nin_Ounce_NVN2.vsetb.byml.zs` and the packs of Sun's Song, Bolero, Zelda's Lullaby, Minuet and Prelude,
each `<- song-qa-mods\qa
omfs\...`. *(BBender)* "playtest went well": the five songs from the big and small
chests and the gift show as intended, no crash with the measured `static` entry. One change asked for: the warp get
pose lit the surroundings and Link too much, so its light goes to 0.3 (E8).

Known: the QA seed's forced placements were not run through the beatability search (`from_placements` leaves it to
the placer), so its logic may be broken and its spoiler has no spheres (the tracker shows no in-logic checks). The
swapped spots are all reachable in Kokiri Forest and the Deku Tree, so the visual checks stand.

## In-game checks 4.3 and 4.4: lesson seed for BBender

Claude, 2026-11-23, same uncommitted branch (with E8). Seed 4242, settings as the CLI builds them for
`--shuffle Chest Gift --skip intro saria deku_tree kaepora --forest open`, made by `ocarina-qa/tools/song_lesson_seed.py`:
every song at its vanilla lesson except Sun's Song and Song of Storms, swapped (Windmill and Royal Family's Tomb), so
the seed has a moved song and gets the song step; the placements **passed the beatability search** (23 spheres, in the
spoiler). Floor pickups added by `tot_chests.py` (test only, not a seed feature) in the Temple of Time, floating 0.62 m:
`Obj_Clawshot_Melody_ForestMinuet` (warp) at slot L1 (91, -39), `Obj_Clawshot_Melody_SariaSong` (non-warp) at R1
(91, -29). Output: `ocarina-qa/song-lesson-seed` (mod romfs, spoiler.json).

- 4.3: BBender plays Impa's lesson (Zelda's Lullaby) only; the other lessons need saves he does not have.
- 4.4: the two pickups in the Temple of Time: floor effect in the song's colours, A collects it, get pose with the
  get-pose effect, song learned and listed.

Results *(BBender, 2026-11-23, Longshot v3.1.1, started from the app with `ocarina-qa/song-lesson-app`, the same seed
in the app's layout)*: "everything worked as expected". Impa's lesson plays through and Zelda's Lullaby is learned
(4.3); the Royal Family's Tomb (Composer brothers' grave) lesson, which in this seed teaches Song of Storms (moved),
plays through and the song is learned; both Temple of Time floor pickups show their floor effect, are collected with
A, show the get pose with its effect (Minuet with the E8 light) and teach the song (4.4); the Fairy Ocarina from the
Kokiri Sword chest plays them; no crash with the measured `static` entry (4.5). This run was not started by Claude's
launcher, so its `mods:` lines are not on record; the SONGQA1 lines above show the same files loading.

## In `src/`

`formats/byml.py` (version 5), `formats/elink.py`, `formats/vfx.py`, `formats/rstb.py` (section 51 formulas),
`patch/songs.py` with `data/song_effects.toml`, wired in `patch/__init__.py` for seeds with a moved song. Decisions
made while implementing: `docs/specs/song-get-effects/plan.md`, "Decisions made during implementation".
