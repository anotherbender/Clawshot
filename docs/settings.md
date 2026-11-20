# Settings and restrictions

This is the command-line and developer reference. Start with the [README](../README.md) or
[seed-pack guide](seed-pack.md) to play. Status below distinguishes in-game observations from
implementation tests; an enabled option is not proof that every combination has been played.
Evidence: [the roadmap index](../plans/00-roadmap.md) plus the linked round files,
[player answers](../plans/playtest/answers.md) and [decisions](../plans/decisions.md).

## Settings strings and reproducibility

```sh
uv run python -m clawshot --shuffle Chest Shop Gift --print-settings
uv run python -m clawshot --romfs C:/Games/OoT/romfs --seed 7 --settings CS1 --out C:/Clawshot/seed-7
```

`--print-settings` prints a shareable `CS1` string and exits without opening the dump. `CS1` alone
means defaults; replace it with the complete printed string to replay custom choices. Explicit
command-line options override its fields, and `--logic name=value` overrides individual logic values.
The spoiler records both effective settings and their replay string. Use `--help` for the full CLI.

Native seeds accept only supported `--logic` overrides. Unchanged world defaults
remain valid; supported non-default values cover free time travel, the return
guarantee, and the derived key/forest/Mido/door modes and return-kit tables.
Prefer `--dungeon-items`, `--forest` and `--door-of-time` for those modes.
Conflicting forest/door fields are still refused. Effective return-kit fields
are regenerated from the selected mode; stored copies cannot override the world.
Versioned share-prefix checks are unchanged; this adds no cross-version import support.

OoT-only access overrides such as `open_kakariko=open`, `gerudo_fortress=open`,
`scarecrow_behavior=free` and `skip_child_zelda=true` are refused: no native patch
makes them true. The same policy applies to CLI settings strings, app validation
and native seed generation; new imported OoT keys are not implicitly supported.
The CS1 codec and standalone logic-model APIs remain generic for research.

Reproduction needs the same seed, settings, generator source/version and world data. Generator
defaults are in `src/clawshot/data/settings.toml`; logic defaults are in `src/clawshot/data/world/`.
A version label alone does not identify the exact source. The generator reads an extracted RomFS;
the pack workflow additionally accepts `.nup` and `.nx` input. Output is changed files under `romfs/`, plus
`spoiler.json` and `play-note.md`, never a copy of the whole game.

## What enters the shuffle

`--shuffle` selects kinds; default is `Chest`. Checks excluded for unresolved access or unsafe
grants stay unchanged even when their kind is selected. Upgrade chains are always progressive,
in chests only; see [Progressive items](#progressive-items).

| Kind | Scope and acceptance |
|---|---|
| `Chest` | 178 of 184 ordinary chests; changed chest grants work in game. Includes the played bridge bean, ranch Hookshot, late windmill Longshot, Field/Lake, four-torch Lake grotto, Valley grottos, Fortress underground, Fountain scarecrow, Well hidden-hole and sign-puzzle routes. The Well requires the Lens conservatively. Duplicate/failure copies and repeat chests stay unchanged. Treasure Chest Game reward swap is built but untested and held; its 11 game boxes stay unchanged. |
| `Shop` | Ordinary shop shelves, native-display items only; slot swaps, restock and Castle Town purchases have in-game evidence. Bought goods (refills, ammo, Bombchus, bottle contents, hearts and magic jars) go only to shop shelves in every seed; no setting moves one to a chest, gift, scrub, floor pickup or Skulltula. Mask loans stay unchanged. |
| `Gift` | Eligible NPC and song gifts, including Great Fairies, Kokiri shopkeeper and all seven frog checks. These families have in-game evidence, not every individual swap. The shopkeeper's late window passed. See the unaccepted checks below. |
| `Scrub` | Four kinds of one-time Deku Scrub sale; repeat vendors unchanged. The adult Mirror Shield purchase that previously froze now finishes; other item/age combinations are not all played. |
| `BossHeart` | Eight boss-heart checks, off by default. Limited to the five native floor pickups below. King Dodongo's Hylian Shield grant/no-respawn was observed; not every combination. |
| `Freestanding` | Fourteen anchored floor Heart Pieces, off by default; same five-pickup palette. Ranch tower Hylian Shield collected/equipped with its saved Hash set; other surfaces, underwater pickup and complete reload coverage are not all verified. |
| `Token` | All 100 native Gold Skulltulas, off in both presets; needs `Chest` (Token alone is refused). Admitted rewards: native tokens, fixed Boomerang/Hammer, shields/swords/boots/tunics, new empty/Milk bottles, all rupee colours, Heart Pieces/Containers, fixed Nut/Stick capacity, ordinary arrow/bomb/nut/stick bundles, Bombchus, magic jars/spells/arrows, Lens, Echo Gem, Double Defense, Scrub Business Seed and Ocarina of Time. Core, packets1–3 and the separate first-Time-ocarina part passed on rc.3; each catalogue member still needs its own native structural check, not every member/boundary was played. See `src/clawshot/data/token_rewards.toml`. Tokens spill only into shuffled chests; non-token grants add no token. The Field tree works by day, the ranch tower needs night/retrieval, and wetlands needs the child wall kill before the adult crate. |

With Gift and Token selected, played bottles, Double Defense, the Echo Gem and gold rupees may also reach
Skulltulas; this does not allow their unverified chest grants. Fixed Nut/Stick upgrades remain Scrub-only.
Token placement retains the existing seeded random ordering; there is no target percentage or weighting.
Reachability, container requirements, pool composition and earlier fill stages still limit the result.

Skulltula ammo requires its existing container before the source; refills never grant a bag or weapon.
**D25:** Bombs and Bombchus require an independent Bomb Bag at every shuffled destination, not only Skulltulas.
Arrow and stick bundles retain their container screens; the native new game already has an empty Nut Bag.
The legacy labels **Deku Nuts (5)** and **Deku Stick (1)** each deliver the native bundle of **3**.
Scrub Business Seed is not an ammo bundle or N64 Magic Bean: the played pickup added one seed; using it
without buying anything **does not consume it**, which is native behavior.

**Excluded at Skulltulas:** Fairy Ocarina; songs; progressive copies and their fixed tiers; keys, maps and
compasses; every `Buy*`/shop-stock item (including refills and bottle contents); trade items; and Gerudo Pass
(Gerudo Membership Card). Their existing destination/pool holds remain unchanged. Fire Arrows and other
out-of-pool items are not silently added.

The 100-token House reward accepts only non-progression items in every seed, including Gift shuffle with
Token off. This is an explicit placement rule, not a consequence of which Skulltulas are reachable.
There is no progression-at-100 opt-in this round; #12 remains open.

Cows, pots, crates, loose rupees, recovery hearts, Treasure Chest Game keys and
silver-rupee puzzles stay unchanged. Dungeon rewards have their own default-off
option below. Pot and ground-rupee
experiments are not seed options: grants were observed, but a thrown pot stranded and lost its
reward. Completion and recovery are not solved by a destruction flag.

The Round 15 forced diagnostics are not shuffle options or beatable seeds. Their core, reward-family,
route and first-Time-ocarina parts provide the played evidence for this explicit catalogue; they do not
establish every item, full-capacity case or route combination.

Maintainer packet/checker tools live in `tools/token_packets/`, outside the release package.
From the repository root, run `uv run python -m tools.token_packets.token_family_packet`
with `--manifest`, `--baseline`, `--save` and `--phase` to check a staged family or route packet read-only.

**Fairy Ocarina stays excluded at Skulltulas:** its native actor has no AnimationRef and there is no native
world-pickup donor. **Ocarina of Time is admitted** using its native `Obj_Ocarina_Time` donor: a fresh S1
pickup, Sun's Song on the new instrument and saved ownership after reload all passed. No animation/common
adapter or Fairy Ocarina admission is implied.

The floor palette is **Heart Container, Piece of Heart, Deku Shield, Hylian Shield and red rupee**.
Major items on the floor can crash. Heart Containers from chests have no recorded in-game acceptance.

### Progressive items

Every upgrade chain is progressive, OoT Randomizer style, and there is **no setting** to turn it
off (Kareem, 2026-11-13):

| Family | Tiers, in order |
|---|---|
| Progressive Hookshot | Hookshot, Longshot |
| Progressive Strength | Goron Bracelet, Silver Gauntlets, Golden Gauntlets |
| Progressive Scale | Silver Scale, Golden Scale |
| Progressive Wallet | Adult Wallet (500), Giant Wallet (1000); the 200-rupee wallet is starting equipment |
| Progressive Bomb Bag | Bomb Bag, Bomb Bag (30), Bomb Bag (40) |
| Progressive Quiver | Bow, Quiver (40), Quiver (50) |
| Progressive Slingshot | Slingshot, Bullet Bag (40), Bullet Bag (50) |
| Progressive Magic | Magic Meter (Single), Magic Meter (Double) |

**Chests only.** A copy's chest event reads what Link owns and chooses the next tier before the
get window, so the window's name and text and the granted item are that tier; the model rising
from the chest stays the family's first tier ([section 47](../plans/03-game-data.md)). Gifts,
shops, scrubs and floor pickups cannot choose a tier, so the fill never places a copy there.
Every physical chest linked to a check must have a supported source-bound opening.
Unreviewed variants remain eligible for ordinary fixed rewards, but not progressive
copies; the generator applies that exclusion before fill rather than failing at write time.


**Native upgrades are bonuses.** Wherever a native check still gives a fixed upgrade (Darunia's
Bracelet, a Great Fairy's magic, a Skulltula wallet, a minigame bag or scale), the chests also
hold the full set of copies, one per tier, each replacing an ordinary filler item, and the logic
counts only the copies. No play order between native rewards and chests is assumed or needed.
A native reward never downgrades: where the native grant would not keep a higher tier, it is
skipped when that tier or a higher one is already owned.

**Child-strength exception.** Logic requires Darunia's native Bracelet route: his door, Zelda's
Lullaby and Saria's Song. That gift adds no copy tier; all three strength copies remain in chests
and adult strength stays copy-only. An early copy Bracelet physically works out of logic, but
logic never relies on it for child strength. Darunia stays unshuffled even with free time travel.


**Which tier.** The next tier above the highest one owned. A copy opened when its family has no
tier left (for example after a native bonus) is a **harmless leftover**: it gives the last tier
again and no tier becomes unobtainable. Progressive Strength gives child Link's Goron Bracelet
first whenever it is missing, even to adult Link, because adult gauntlets do not supersede it
across time travel (Kareem, 2026-11-12). Progressive Quiver and Slingshot give their weapon first,
then capacity; a fixed bag upgrade alone is not the weapon. Progressive Magic gives the double
meter once Link has any magic, including the meter a spell, the Lens of Truth or magic arrows
open. Logic counts only copies: the Nth copy is tier N ([logic reference](logic.md)).

**Names.** Hints, `spoiler.json` and `play-note.md` name the family ("Progressive Hookshot"),
never a tier. The spoiler's `progressive_grants` and the note's Progressive items table list each
copy's tiers in order and the tier it gives in one canonical replay of the seed's search spheres,
marking leftovers. That depends on collection order: it is not a play order and not a promise for
another route.

Status: played on Longshot (Kareem, 2026-11-13). Mido's chests gave Hookshot then Longshot and
Silver then Golden Scale; separate chests gave every remaining top tier (Bomb Bag 40, Quiver 50,
Bullet Bag 50, Golden Gauntlets, Giant Wallet, double magic); Darunia's dance with the Bracelet
already held kept Silver Gauntlets and gave no duplicate. Get windows name the tier received;
the rising chest model still shows the base item. A seed puts one copy in a chest; several copies
granted inside one chest event read stale ownership, so that is not supported.

### Gifts: enabled versus held

`Gift` includes five frog song prizes contributing **Rupees (20)** each, the Storms prize and the
bug game. All seven passed the frog experiment. The two deterministic Bombchu Bowling
prizes (first win, second win, then the usual rupees) and both normal shooting-gallery prizes
are confirmed in game (`R10-MINIGAMES-CHILD-JABU`, `R10-MINIGAMES-ADULT`).
Rental weapons do not become inventory rewards. Both expert galleries remain unshuffled:
native expert wins pay repeatable wallet rupees, with no separate first-win prize.

With `Gift` selected, the child Market Potion Shop bottle tutorial and Dampé's graveyard
digging prize give shuffled rewards. Both passed their in-game checks on 2026-11-10
(`R10-MARKET-BOTTLE-FIX`, `R10-DIGGING`). Accept the shop owner's offer by day; the shuffled
gift skips the bug-catching lesson. Without `Gift`, the free bottle and lesson stay unchanged,
and logic still counts that bottle. Digging still shows a heart prize but awards the shuffled item.
Market expert wins pay 30 rupees and Kakariko expert wins 70, including the first win. Clawshot's
held first-expert-check experiment would add a new once-only prize; it is off under every setting.

Merchant sale experiments (Medigoron, Granny, desert carpet) remain held. The Skulltula House's
10- and 40-token reward swaps passed; the 20-token preview was observed, not every later threshold.
With `Gift`, the 40-token reward contributes **Bombchus (20)** to the pool and gives its
assigned item, using the usual forty-token requirement and collected state. Without `Gift`,
it stays the usual twenty-Bombchu bundle. Kareem passed the changed reward on Longshot rc.7
on 2026-11-19; this does not certify every House reward or every possible replacement.
The Weird Egg, Zelda's Letter and the adult trading items stay at their native checks.
All fourteen share one trade inventory cell that shows a single owned item,
adult items first (a child sees an owned adult item instead of the Cucco Talon must be shown), and every
adult trade hand-in shows the item the previous native trade gave, as the logic assumes. Biggoron's
final sword reward is still shuffled behind the native Claim Check.

The Gerudo Membership Card stays at the captain under every preset and setting, never in the
shuffled pool (D39). Free all four carpenters and receive it from her: the native hand-over advances
Spirit Step02, which the guards and desert gate, Training Ground and horseback archery entry NPCs
check. The logic's card rules stay unchanged. Evidence is the [static game-data trace](../plans/rounds/r13-gerudo-card.md),
not a played D39 acceptance test.

Older Gift seeds could move the card without clearing the guards. Finishing their carpenter/captain
sequence still advances the quest even if its reward differs (same static trace). Existing seed
folders and saves are not retroactively repaired.

### First ammo containers

Newly generated seed mods add a missing small bag before the shared item grant: 10-stick capacity
for Deku Sticks, 20-nut capacity for Deku Nuts, a 30-seed Bullet Bag for the Slingshot and a
30-arrow Quiver for the Bow. The ranged bags use their native full-stock grant; sticks and nuts
keep the original bundle quantity. A bag already owned, including a larger tier, is not replaced
or refilled. A bag upgrade does not grant its weapon.

This covers shared chest/shopkeeper grants, direct NPC hand-overs, successful scrub purchases and
literal source gifts; refused or cancelled purchases grant nothing. Chest Deku Sticks and the Kokiri
counter-gift Slingshot passed pickup, use and Save and Quit → Continue (Kareem, 2026-11-12).
Scrub/Goron and other companion paths have native-data/test coverage, not individual played acceptance.
Older seed folders and saves are not retroactively changed. New-game empty nut-slot initialization remains 0/20.

### Songs and chest-only evidence

With `--shuffle Chest Gift`, `--songs song` (default) keeps songs on song checks;
`--songs anywhere` releases all twelve for chest placement, subject to other destination restrictions.
Storms, Minuet and Epona have been played from chests; the rest use the shared grant path but are
**inferred, not individually verified**. Songs can show a stand-in model. Both chest ocarinas work
but show no model; the Ocarina of Time plays songs. Din's Fire and Adult's Wallet have chest evidence.
Other gift actors remain subject to the sourced chest allowlist and destination holds, not blanket
permission for every gift to go in a chest. Authoritative restrictions: `data/settings.toml`.

Shuffled ocarinas avoid show-item hand-overs: ordinary gifts, minigame prizes, frog rewards,
digging rewards and Deku Scrub purchases exclude both instruments before fill, including external
placements. Chests and direct story grants remain allowed; Ocarina of Time also has its separately
played Skulltula pickup. The show-item crash is not established to be age-specific.

Ocarinas remain separate fixed items, **not progressive copies**. Newly generated seeds still give the
Fairy Ocarina when found, but keep the Ocarina of Time selected if it is already owned, at either age.
Kareem passed the child and adult checks on Longshot rc.7 on 2026-11-19: adult Sun's Song worked,
and Time stayed selected after Continue. In the unchanged adult check, Sun's Song also worked while
holding Fairy. That result covers Sun's Song, not every adult song or the automatic song lessons.
Logic still requires Time for adult songs and lessons. Existing seed folders and saves are not repaired;
this is not a no-instrument song-lesson bypass.

### Cross-age equipment receipts

Age restrictions govern **use**, not ownership. There is no blanket matching-age placement rule.
Native shops still refuse child tunic purchases; unsupported shelf displays and the five-item
boss-heart/floor palette remain restricted. Trade-cell items stay vanilla.

Newly generated scrub shield sales keep the native inventory grant and one-frame yield, then
finish without requiring any shield to equip. This covers an adult owning only the unusable Deku
Shield, as in issue #33, and opposite-age Mirror/Deku receipts. The patch does **not request forced
auto-equip** or enable wrong-age shield use. Inventory, native auto-selection and equipment are
separate; manual equipment remains available at the usable age. Kareem passed the adult Mirror Shield
purchase on Longshot rc.7 on 2026-11-19. Other shield/age combinations are not all played;
old generated folders are not repaired.

Other chest/gift/pickup paths do not use that scrub-only equipment wait. They retain their existing
native grants and admission rules, not a claim that every item/age pair has been played.
The [round18 audit](../plans/rounds/r18-equipment.md) separates played results, native-data evidence
and unverified boundaries. Wrong-age item-bar precautions remain [below](#hints-models-and-age-warnings).

Lessons retain main's native ocarina sequence. Round18's attempted no-usable-ocarina bypass was withdrawn
after Kareem's adult/Fairy-only Minuet check froze following the demonstration (2026-11-19).
This includes every child/Impa and adult bypass; the physical repair is deferred.
Logic requires an ocarina for lessons: either as child, Ocarina of Time as adult. Walking into an automatic
lesson without the required instrument can still freeze the game, even though logic avoids that route.

## Shops and scrub prices

| Option | Behavior |
|---|---|
| `--shop-prices vanilla` | Default: original slot prices. |
| `--shop-prices affordable` | Exactly 10 rupees for each selected shuffled shelf. |
| `--cheap-deku-shield` | Provisionally on: an actual Deku Shield in Kokiri shop costs 10 even without Shop shuffle. |
| `--no-cheap-deku-shield` | Disables that independent discount. |
| `--shop-slots 0..8` | Default 8: first N native shelf indices in each ordinary shop; remaining stock unchanged. |
| `--scrub-prices vanilla` | Default: retain the supported one-time sales' 40/100-rupee fees. |
| `--scrub-prices fixed --scrub-price 10` | Exact selected fee, range 0–1000, for the four supported shuffled once-sales only. |

Exact prices replace conditional discounts. Affordable prices affect selected shelves only; the
independent cheap shield rule still applies with zero shuffled shelves. Logic uses the patched wallet
requirement and the native 200/500/1000 wallet capacities, retaining release, refill and adult-only
gates. These fields replay through CS1. The 10-rupee Kokiri shield/nuts purchase and restock were
observed (R6-PRICES); partial shelves and fixed scrub fees are built/tested, not independently
certified in game by that observation.

**Scrub offer wording:** shuffled one-time sales still describe their vanilla item, even
when their actual reward differs. Check the get window/inventory or spoiler, not that sales
pitch ([recorded since round 6](../plans/rounds/r6-tokens.md#purchase-and-patch-contract)).
Repeat vendors are not shuffled; their native weapon/magic/bottle gates can hide every offer.
The no-offers guard for [#26](https://github.com/hiKareeem/Clawshot/issues/26) ends that
conversation before opening an empty shop menu. It applies even without Scrub shuffle.
Kareem reproduced the control's second-talk softlock on Longshot rc.3 and passed the repair:
repeated empty-offer talks, Song of Storms for 10 rupees, normal seed refill and Save/Continue
(2026-11-14). Decline-then-Leave and full-capacity refusal were not exercised.
Existing seed folders are not changed.

## Forest and fast start

`--forest closed` is the vanilla-like default: Mido guards the Deku Tree and the bridge exit stays
closed until Gohma. `closed_deku` opens just the bridge; `open` also bypasses Mido. The bridge-only
option has in-game evidence with Mido still blocking (R6-CLOSEDDEKU). Mido skip and fast start also
have recorded in-game results. Legacy `--skip mido` aliases `--forest open`; conflicting explicit
forest choices are refused. Forest flags compose with gift save flags.

With Mido kept, his post-Zelda schedule waits until his saved wall blocker has actually cleared.
This preserves the native sword-and-shield conversation after an early castle visit instead of moving
him beyond a still-closed wall ([#35](https://github.com/hiKareeem/Clawshot/issues/35)).
Only that completed-castle schedule is guarded; open/Mido-skipped mode is unchanged.
Kareem passed the repair on Longshot rc.7 on 2026-11-19: sword-only Link was refused, adding the shield
opened the passage and tree mouth, and both stayed open after reloading. Do not regenerate a played seed
or reset story quests to repair it.

The opening-movie skip is on by default. It removes the movie entirely, not just its skip-button
restriction; Navi waking Link and normal new-game initialization still run. Movie removal
**passed Kareem's new-game check on 2026-11-12**. `--skip intro saria deku_tree kaepora`
selects fast-start skips; `--skip` alone disables them. These are separate from shuffled kinds.

**Story-dialogue skipping is not available yet.** It is withdrawn for 0.2.3: the option is hidden
and requests to enable it are refused.

The Kaepora skip also marks the skipped first-field panorama complete, ending its native
music-suppression window. The previous preset could leave Hyrule Field silent during the day.
This changes **new games only**, not existing saves. Kareem verified the repaired field
music and the story/escape checks on Longshot on 2026-11-13
([section 46](../plans/03-game-data.md#46-round-14-child-story-and-field-music)).
The skip now also preserves `IsVisitLocation.HyruleField`, normally supplied by the panorama's
location UI and required for the Field map. Like the Saria skip's Kokiri Forest visit flag, this
also reveals the area's pause map before the first visit. This new-game minimap/full-map correction
still awaits in-game verification; existing saved visit state is not migrated.

The optional, default-off `kaepora` fast-start selection remains **experimental**, including under
Recommended. It omits later owl speech while preserving scene flags and travel.
On Longshot 3.0.0 stable (2026-11-19/20), Kareem played the castle arrival: no speech, a short
stop/fly-away, with banner/map/Malon preserved. The Field owls near Kakariko and the Lake approach
also passed: no speech, a short look-and-fly-away. The summit and Lake travel owls kept a short offer and working flights.
These results do not cover every owl scene; later Woods/Zora owl additions remain unplayed.

Every new seed also refuses to start Dampé's race without an owned Hookshot or Longshot.
Kareem accepted the no-tool candidate (2026-11-19): no race, fade out/in at the **same spot before Dampé**,
normal control, and the existing warp back up remains usable. The intended surface return was **not**
observed; no further behavior change was requested. Both prizes remain shuffled.

Every new seed enables the D-pad HUD shortcuts from the start, independently of fast-start
choices (including `--skip` with no selections): **Navi, Ocarina, Boots and Masks**.
This sets the saved `ActionGuide_IsEnd.Navi` initial value; it does not grant an item or
complete a story quest. Intro/Saria/Deku-talk skips alone do not set it. Kareem verified
the HUD after the first Boomerang pickup, before entering the Deku Tree, and after
Save → title → Continue on 2026-11-12. Boomerang and ordinary items use the right-bumper
item menu, not these D-pad shortcuts. Existing saves are not migrated.

Skipping the Deku Tree's talk does **not** bypass kept Mido: equip the Kokiri Sword and
a shield, then talk to him. His early quest state, idle schedule, Talk initialization and
blocker clear remain native; only that clear applies the skipped tree-talk state. Bypassed
Mido instead keeps the initial completed-meeting preset. Saria's skip preserves the forest
visit flag normally set by her area banner; the forest pause map opens in the same played check.
The first Mido repair **hung in game and was replaced**. Kareem verified the native-clear
replacement: normal middle position, sword-only refusal, clear after adding a shield, and
no Deku Tree talk with its mouth open. Reload also passed: after Continue, Mido's dialogue
finished normally and the Deku Tree's mouth was open. Shuffled own-dungeon map/compass
credit is a separate bug, not a failure of this map-access correction.

## Dungeon rewards and Ganon's Castle bridge

`--dungeon-rewards` (app: **Dungeon reward shuffle**) is experimental and off by default.
It shuffles the three Spiritual Stones and six medallions only among their nine reward
slots, including Rauru's Light Medallion on the first sword pull. Rewards cannot go
to chests, gifts, shops or Skulltulas, and other items cannot occupy reward slots.
The first pull still grants the sword and retains the native song/story sequence.
Placement obeys reachability: in a normal closed-Door seed the three Stones must
come from Gohma, King Dodongo and Barinade, in a seeded order, before adult rewards.

With reward shuffle on, the **closed Door needs the three owned Spiritual Stones**,
not child dungeon completions, plus its existing Ocarina of Time, learned Song of Time
and real Impa send-off requirements. Open and song-only keep their existing clock/send-off
gates. An early opening cannot strand the later native escape or moat rewards.
Boss deaths, blue warps, sage scenes, world restoration, carpenters/card and reverse
time travel remain completion-driven. Prelude follows Forest completion; Light Arrows
follow the Shadow and Spirit awakening scenes, not their medallions. Logic matches
these separate ownership and completion predicates.
Song lessons still require an age-usable ocarina even when their rewards are shuffled.
The moat item precedes its Time-song lesson, so the item check itself needs no instrument.
The native animated emblem in each sage/stone scene remains its source symbol;
the acquisition window, owned reward and Zelda Notes target follow the shuffled item.

`--bridge vanilla` is the default native story route. The experimental count modes
`--bridge stones --bridge-count N`, `--bridge medallions --bridge-count N`, and
`--bridge rewards --bridge-count N` count unique owned rewards, respectively 0–3,
0–6 (including Light), and 0–9. Vanilla requires count zero. Invalid combinations
are refused. These settings open **only the bridge**: they give no Light Arrows,
complete no sages and skip none of the six native Light Arrow trial cores.
With Gift shuffle, the native Light Arrow story still runs even if its gift moved.

Kareem's Longshot rc.7 checks on 2026-11-19 confirmed the shuffled first-pull reward, a medallion-count
bridge staying closed below its count and opening at the count, and the closed Door opening with all
three Stones owned while Dodongo and Jabu were unfinished. The Door stayed open; no escape or moat
scene played. On Longshot 3.0.0 stable (2026-11-19/20), with only Emerald and Ruby owned, the Door
stayed closed and no opening scene played; the saved state confirmed both Stones and the closed Door.
Other shuffled boss rewards, stones/combined bridge counts, late story order and a full playthrough
are not certified by those checks. Both options remain experimental.
Detailed evidence: [dungeon rewards and bridge](../plans/rounds/r18-rewards.md).

The Temple of Time Light Arrows scene is an ordinary `Gift` check, already included
when Gift shuffle is selected. It may give another eligible gift item; without Gift
shuffle it still gives Light Arrows. In every mode its trigger remains the completed
Shadow and Spirit awakening scenes, not owned medallions. The vanilla bridge follows
that Temple story even when its reward is not Light Arrows; the six trials and finale
still require usable Light Arrows. Ganon's boss key is never awarded by this scene:
it follows the ordinary boss-key placement rules below. Round19 corrects the default
logic to these native readers, without changing the scene or its saved writes.

## Door of Time and returning to child

| Option | Requirement / effect |
|---|---|
| `--door-of-time closed` | Default: meet Zelda and Impa, then Ocarina of Time and playable Song of Time. With vanilla rewards, keep the native completed-stone route. With reward shuffle, require all three **owned** Spiritual Stones instead; finding stones never completes their dungeons. |
| `--door-of-time song_only` | Field-arrival clock state and Impa's real field send-off, then either child ocarina and the learned Song of Time. No stones needed to open the Door. |
| `--door-of-time open` | The Door waits for Field-arrival clock state and Impa's real field send-off, then opens without songs or stones; the first-pull pedestal has no extra item gate. |
| `--logic free_time_travel=true` | Experimental, default off: adult return before Forest completion. The app's **Free time travel (experimental)** switch is the same override. |

Door mode and reverse travel are independent. The default return guarantee proves an adult can
unlock return from the minimum mandatory first-pull inventory and adult checks; optional child
errands are not assumed. Early-door settings can be refused with unshuffled child-only prerequisites.
There is no automatic free-travel override. Both early modes keep the escape and both moat rewards
available after an early sword pull: finish the required stone route, return as child, then approach the
Market from Hyrule Field and collect the moat pickup. Logic still assumes all three stone quests; the
native repair follows the Fire/Water counter and adds no Forest condition. All Door modes defer that
counter until the real Impa send-off, recount there, and ignore calls after escape. This also covers
closed mode when shuffled songs allow stones before Zelda. The native courtyard Step01 reset remains;
early-mode post-pull callbacks do not roll the completed Door quest back.
Kareem passed the open-mode send-off gate, early-pull escape/moat order repair and immediate
child-return clock clear on Longshot rc.7. The first-arrival lighting repair below awaits v5 play checks.

**For new seeds; no save-repair pass.** Both early modes read the
arrival flag and the real send-off history. Kaepora fast start now preserves the skipped owl's
arrival effect; the actual send-off restores it if a different route missed the owl. Independently,
that send-off clears a leftover first-arrival environment, waits one frame and rebuilds its palette.
The Forest exit does not re-enable that environment once the Field panorama or real send-off has played.
Returning to child through the Temple clears the pending first-adult clock hold without changing
the native first-adult scenes or the adult Market exit.
An adult who warps out before walking Market → Hyrule Field keeps the native first-night hold; walk that exit or return to child through the Temple to clear it.
Rebuilding an old seed can change output; do not replace a played seed or assume save compatibility.

**The three stones alone do not trigger Zelda's escape.** Visit the child castle courtyard and
finish Impa's send-off too: Malon's fixed Weird Egg / Chicken wakes Talon to reach that route.
Both moat rewards, Saria's song source and every Door mode require the completed
courtyard/Impa sequence in logic, even if ocarinas or songs were shuffled elsewhere
(`Met Child Zelda` models the completed send-off). Zelda's Letter stays at Zelda (D31); no child-Zelda
skip or quest-precompletion patch is offered. The native-data trace is
[section 46](../plans/03-game-data.md#46-round-14-child-story-and-field-music).
Kareem passed the staged Longshot story controls on 2026-11-13, including Saria before Darunia and escape/reload.

With the return guarantee enabled, this generator cannot build Chest-only seeds with
`song_only` or `open`: its return-kit bound needs movable ocarinas and Saria's Song, but those
remain at child gifts. Validation names the fixed checks and offers a closed door or Gift
shuffle. This is a construction limitation, not proof that no physical route exists;
in particular, the logic for the unshuffled Time-song gift already requires all three stones.
Free time travel replaces that return proof, so with it on all three door modes are accepted
with Chest only. Early open-mode return, preserved moat rewards and the immediate-child-return
clock clear passed on rc.7.

An open-bridge, early-door seed can validly require adult Link before Gohma. Its play note
explains when no child-only opening guide exists instead of rejecting the beatable seed.

Free travel keeps Temple Sheik through both first-arrival scenes, then hides him until Forest quest
completion. Forest completion, not its medallion, controls Prelude even when rewards are shuffled.
Early return, repeated age changes, the post-Forest Prelude and the fixed first adult arrival have
recorded in-game acceptance (R9-FREE-TRAVEL, R9-PRELUDE-PATCHED, R10-FIRST-PULL-FIXED). Default stays off.
Adult song logic still requires the Ocarina of Time. Adult Sun's Song worked with Fairy in the
2026-11-19 check; that does not establish other adult songs or safe Fairy-only lessons.

The app shows this override as the **Free time travel (experimental)** switch under World, not as a
separate generator setting. On writes the same settings string as `--logic free_time_travel=true`;
turning it Off removes the override (the default meaning). Importing a CLI or spoiler string sets
the switch from its value. Explicit overrides, including `free_time_travel=false`, keep their exact
settings string through unrelated form edits. Editing the switch replaces its old override; editing
the advanced logic JSON resynchronizes the switch from that explicit value.

`--dungeon-items own_dungeon` keeps dungeon items in their dungeon and is the default; both UI
presets keep it. While it is set, the two chests on the Desert Colossus statue's hands cannot
hold Spirit Temple keys, maps or compasses: a generic grant there would credit the wrong
dungeon or nothing.

`--dungeon-items anywhere` (the UI choice **Small keys anywhere**) moves **small keys only**,
into shuffled chests whose access and native opening contracts permit it, including other dungeons
and the overworld. An off-dungeon key is delivered as a named chest grant; no other shuffled kind can grant one.
Both release modes include the Well floor key and require Chest shuffle.
Its floor source keeps its own key or gives a red rupee; the replacement retains a key-shaped
model and native room retirement wiring. Other dungeons' keys, majors, hearts and shields
are not floor-key rewards. On Longshot rc.7 on 2026-11-19, Kareem left the Well replacement,
recovered it, collected its silent +20 rupees, and confirmed it stayed collected after leaving,
returning and Continue. This proves the checked Well pickup, not every scripted floor key.
Own-dungeon mode leaves it untouched. The Shadow Temple floor key stays vanilla under every setting:
**built, held until a natural pre-room save exists**. Its adapter is not admitted to generation.

`--shuffle-hideout-keys` (UI: **Fortress jail keys (experimental)**) separately releases the four
Fortress guard floor keys into supported shuffled chests. Default **off** in both presets;
`--no-shuffle-hideout-keys` overrides a settings string. Chest shuffle is required. Each guard's
drop, staged event pickup and resting pickup remain one check. Replacement rewards are red rupees
with the native key-shaped floor display and the key's get-event/window, not silent rupee collection.
That completion writes the source's native once-only Bool; the initial silent candidate repeated
after re-entry and is superseded. Kareem passed one guard/rescue and the repaired 20-rupee drop,
including leaving/returning and Continue, on Longshot rc.7 on 2026-11-19. Chest keys credit only
Fortress inventory, not guard defeat, source collection, carpenter rescues or Spirit progress.
Talk to the Valley carpenter boss and answer Yes before the jailed carpenters; this enabled the
guard in the played check. All four rescues, the captain's unchanged card (D39) and Training Ground
remain **unplayed with this option**, so it stays experimental. The card alone does not clear guards.

The four jail sources use stable native actor/Hash identities, not a guessed torch-room match.
Until that correspondence is verified, logic conservatively requires access to all four guard
fights before relying on any shuffled jail-floor reward. Native jail-door spending remains unchanged.

The experimental `--dungeon-items all_anywhere` (UI: **All dungeon items anywhere**) also
releases maps, compasses and boss keys, including Ganon's Castle's boss key, into supported
shuffled chests. It is off in defaults and both presets. Source-bound grants write only the
intended dungeon's saved ownership flag, never the standing dungeon's. Both pickup messages
name the item and its target dungeon in English in every language. An off-area boss key
does not animate the standing dungeon's boss-key indicator. Map/compass display passed Kareem's
Longshot rc.7 check on 2026-11-19; an earlier remote Forest boss key opened its normal door.
These checks do not cover every source/target combination or a whole playthrough. The option remains
experimental; it does not shuffle dungeon-completion rewards or change the bridge.

In either anywhere mode, the statue's two hand chests may hold a named small key.
Only `all_anywhere` allows named maps, compasses and boss keys there.

Dungeon-item delivery uses the native grant where it already works: own-dungeon small keys
in small chests and all four families in big chests. Moved small-chest maps and compasses
use source-bound ownership writes; own-dungeon boss keys reuse the native boss-key action
and pickup indicator on existing actors. A get message or HUD icon alone does not prove
saved ownership. Native pickup text and unchanged placements are preserved.
Map/compass saves and pause menus, and boss-key credit, pickup indicator and normal boss-door
opening passed in-game. Boss-door reload persistence is untested: the arena prevents saving.

Previously generated seeds can lose these three items from small chests. Rebuilding a mod
does not re-award a chest already opened in an existing save.

Every physical copy of a destination must support its source-bound opening. The Hyrule Field
heart-piece chest lacks that contract, so it cannot hold off-dungeon keys, maps or compasses.
It remains shuffled for other eligible rewards; no new opening is assumed.

A key found outside its dungeon names that dungeon in both pickup messages — for example
"Small Key (Forest Temple)" and the caption "Opens one locked door." / "Dungeon: Forest Temple" —
in English in all 16 language archives; dungeon names are read from your dump, not bundled with Clawshot.
There is no new in-game key list: the standing HUD, pause-map counters and floating notices show only the
dungeon you are in. A key credited to another dungeon can show no notice or no counter change
where you stand (in the played gates an overworld pickup showed no increment and an Ice Cavern
one no notice, both with the saved count correct); the notices do not track the key's target
dungeon. The [Tracker tab](tracker.md) shows per-dungeon held and found keys from that seed's own
save, with a compact OBS view; it is separate from the game's current-dungeon counters.

Acceptance: Gates 1–4 passed in game — native and named key chests of both sizes, in-dungeon
and out, child and adult, correct remote credit, door spending and reload persistence, ending
with a whole generated anywhere seed ([round 12](../plans/rounds/r12-keys.md)). That is not every
source/target combination or a complete playthrough.

## Hints, models and age warnings

Gossip Stones give English hints in all 16 language archives. `--hints always` is the default;
`--hints mask` restores the Mask of Truth requirement. The balanced distribution includes required-route,
barren-area and item hints. Location hints never name junk. The no-mask lines and corrected highlight
reset were observed in game; that is not certification of every distribution. Both native Sheik
Hookshot-direction lines are replaced with a seed location holding the Hookshot or a Progressive
Hookshot (any copy is the Hookshot while none is owned), or omit the tool if none exists in a
partial world. This text is built/read-back-tested, not separately player-accepted.

**Wrong-age pickups:** the note lists shuffled age-locked rewards reachable by the wrong age at their
first search frontier, including ties. Optional later pickups can differ from that order. Progressive
Hookshot, Quiver and Slingshot warn like their weapon, which any copy can give.
New games initialize the native small Nut Bag and zero Deku Nuts (0/20); Kareem verified a child
Bow-first pickup followed by working Boomerang use without reloading on 2026-11-12.
Existing saves are unchanged: in saves started with older builds, Save and Continue before using
other items after an age-unusable reward. Changing areas does not clear that older item-bar jam.

Changed rewards omit the old item's acquisition-only Navi reaction. Where that reaction
shares a wrapper with room or quest progress, a source-bound clone removes only the stale
comment and retains the story writes. Native unchanged rewards retain their original event.

On Hookshot 2.0.12+, clear `HOS_FS_OVERLAY` and load through mods; the old overlay route crashes.
The game's Switch button icons then appear in ordinary text; the separately drawn ocarina note
interface keeps its own controller prompts. See [loading instructions](seed-pack.md).

## Developer layout

Python 3.12+ with uv; rationale and product choices: [decisions](../plans/decisions.md).

| Path | Responsibility |
|---|---|
| `src/clawshot/formats/` | BYML, SARC, zstd dictionaries, EVFL, MSBT and resource size table |
| `src/clawshot/census/` | Finds locations in the player's dump |
| `src/clawshot/world/` | World loader, rule language and search |
| `src/clawshot/data/world/` | Regions, items, helpers, settings and remake overrides |
| `src/clawshot/generate/` | Fill, spoiler and play-note generation |
| `src/clawshot/patch/` | Changed-resource plans and writer |
| `src/clawshot/pack/` | Source-only seed packs and local dump handling |
| `tests/` | Synthetic fixtures; tests marked `dump` need `OOT_ROMFS` |
| `plans/` | Architecture, format specification, evidence and decisions |

For porting, see [logic reference](logic.md). Credits: [NOTICE](../NOTICE), including OoT Randomizer
`526b4c8d` and Archipelago `Fill.py` at `1041167c` (`generate/fill.py` safe swap). Licence: [MIT](../LICENSE).
