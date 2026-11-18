# Logic reference for ports and trackers

Clawshot's access model is reusable data, not a claim that N64 rules match this remake. This guide
maps the data and contracts for a tracker or a possible Archipelago world. Paths below are relative
to the repository root. The detailed specification is [world format](../plans/04-world-format.md);
licences and exact upstream revisions are in [NOTICE](../NOTICE).

## Data map

| Path | Contract |
|---|---|
| `src/clawshot/data/world/world.toml` | Start region, goal, file list, overrides, local settings/items/helpers and progressive tiers. |
| `src/clawshot/data/world/port.toml` | Translation inputs, Banc area mapping and pinned OoT Randomizer commit. |
| `src/clawshot/data/world/*.toml` region files named by `port.toml` | Translated regions, exits, events and location metadata. Do not hand-edit these generated files. |
| `src/clawshot/data/world/helpers.toml` | Named and parameterized rule helpers, translated from OoT Randomizer. |
| `src/clawshot/data/world/items.toml` | Item types/classes, aliases and properties used by search. |
| `src/clawshot/data/world/settings.toml` | Translated settings, tricks and world flags used by rules. Not the generator's user-facing defaults. |
| `src/clawshot/data/world/remake.toml`, `src/clawshot/data/world/remake/*.toml` | Sourced remake corrections, exclusions, new regions/checks, items and helpers. |
| `src/clawshot/data/settings.toml` | Generator defaults and placement restrictions; distinct from translated logic defaults. |
| `src/clawshot/data/locations.toml` | Placement identity definitions and links to world location names. |
| `src/clawshot/data/location_names.toml` | Player-facing labels, directions, physical IDs and map-floor descriptions. Presentation is not a new identity or access rule. |
| `src/clawshot/patch/gift_rules.toml` | Event grant identities and patch policies for supported gifts. |

Sources: `plans/04-world-format.md` sections Files, Overrides, Items/helpers/settings and Replayable
generator settings; `plans/03-game-data.md` sections Readable location names and Event gifts;
`NOTICE` for the provenance of translated data and algorithms. The world translation tool is
`src/clawshot/world/translate.py`; its inputs must match `port.toml`'s pinned commit, and the
translation comparison is in `tests/test_world_translate.py`.

### Overrides and evidence

`src/clawshot/world/load.py` applies `remake.toml` first, then `remake/*.toml` in sorted name order.
A location, exit, event, region, key count or item cannot be set in two override files. New regions
are added before their contents are resolved. A changed rule states `was` as well as `rule`; upstream
changes must not silently invalidate the correction. Overrides carry a `source` explaining the
ported file/line or remake evidence. See `plans/04-world-format.md`, Overrides.

The same specification defines `n64_only` (not a remake check), `keep_vanilla` (present but not
shuffled), `vanilla_fixed` (a concrete tier), and `new = true` (a remake addition). Preserve those
meanings in a port. Do not turn a held check into a randomized check just because it has a rule.
The current acceptance boundary is in [settings](settings.md), with observations in
`plans/playtest/answers.md` and the [roadmap index](../plans/00-roadmap.md) plus its linked round files.

**Water Temple source gate (0.2.2): confirmed by a played save-edit control.** Entry requires
access to the real Ice Cavern end chest as well as Hookshot and Iron Boots, independent of where
Boots or Serenade are shuffled. Claude chose the r16 precaution on 2026-11-17; Kareem was informed.
Kareem tested rc.7 unmodded, Debug-made adult with Hookshot and Iron Boots at adult Lake Hylia.
With the quest at `Ready` and `SageOfWater_GetWaterSerenade=false`, the Hookshot did not latch.
On the same save, setting the Ice end-chest wrapper's writes, `SageOfWater_GetWaterSerenade=true`
and `Step_SageOfWater=Step05`, made the switch work and the door open. This confirms that the
Ice end-chest state enables entry; which of the two values matters was not separated. It is a
played save-edit control, not a normal-progression or modded Clawshot certification. See
[the Water gate evidence](../plans/rounds/r16-water-gate.md).

## Rule language

Rules are parsed expressions, **not Python to execute**. The compiler validates and folds settings
once; the remaining predicate reads items, events, age and time. Implementation:
`src/clawshot/world/rules.py`; syntax/lookup/unsupported branches:
`plans/04-world-format.md`, The rule language.

| Form | Meaning |
|---|---|
| `True`, `False`, `and`, `or`, `not`, parentheses | Boolean requirements. |
| `Kokiri_Sword`, `'Kokiri Sword'` | Item identifier; quoted names can also name events. Identifier normalization follows the compiler, not a new port-specific naming scheme. |
| `(Progressive_Hookshot, 2)` | Required count. Counts can also refer to a setting. |
| `is_child`, `can_use(Bow)`, `can_play(Song_of_Time)` | Helpers resolved from helper data and remake overrides, not hard-coded N64 assumptions. |
| `open_forest == 'open'`, `'Deku Tree' in dungeon_shortcuts` | Setting comparisons/membership; tables use their declared data shape. |
| `age == 'child'`, `at_day`, `at_night` | Age/time predicates; time semantics depend on settings. |
| `here(rule)`, `at('Region', rule)` | Region-scoped subrules represented as persistent events; not arbitrary teleports. |
| `has_bottle`, `has_stones(n)`, `has_medallions(n)` | Built-in inventory predicates. The specification lists all supported built-ins. |

Names resolve through built-ins, helpers, items, settings and events as specified by the compiler;
unknown names, helper recursion and unsupported live features fail rather than becoming true.
An inactive constant-folded branch can contain an unsupported name; do not eagerly evaluate it in a
port. N64 tricks default false and cannot be enabled without remake verification.
Sources: `src/clawshot/world/rules.py`, `src/clawshot/world/load.py`, and the rule-language and
Items/helpers/settings sections of `plans/04-world-format.md`.

Items have types and classes (progression, priority, normal), aliases and optional properties such
as bottle/stone/medallion. Dungeon items belong to their declared dungeon. Fixed tiers count toward
the progressive names read by imported rules. Starting items and event grants also participate in
search; the remake has no free starting Fire Temple key. Sources: `plans/04-world-format.md`, Fixed
or progressive items, Items/helpers/settings and Reachability; `src/clawshot/world/load.py`.

**Progressive copies (Kareem, 2026-11-13; `plans/03-game-data.md` section 47).** Generated seeds
always place the eight native chains of `src/clawshot/progressive.py` (`CHAINS`) as counted
copies, with no setting: Progressive Hookshot, Strength, Scale, Wallet, Bomb Bag, Quiver,
Slingshot and Magic. Only chests may hold a copy (other kinds cannot select a tier). Wherever a
native fixed-tier source stays vanilla, the pool holds the full set of copies (N copies for N
tiers, extras replacing ordinary filler) and **logic counts only the copies**: the Nth copy is
tier N. The native reward is a bonus outside that count, so no order between it and the chests
is assumed; it never downgrades, and a copy that finds no tier left is a harmless leftover. The
fixed-tier placement rule applies only to items that stay fixed.

**Deliberate child-strength exception (Claude, 2026-11-13):** child capability requires Darunia's
native source via his door, Lullaby and Saria's Song, never a copy Bracelet. The gift adds no
copy tier; all three copies remain, adult strength stays copy-only, and Darunia stays native even
with free time travel. An early copy Bracelet
can physically work out of logic. The first adult copy is not assumed in the return-kit lower
bound; the kit must place it. See the [round dependency](../plans/rounds/r14-progressive.md)
for E's unplayed post-boulder Darunia source-lock finding.
Progressive Quiver and Slingshot establish the weapon before any capacity; a fixed bag upgrade is not the weapon.
A spell, the Lens or magic arrows open the native meter; at run time that makes the first magic copy give the
double meter, never an extra copy. A port must model these as counted chain items, not as their
first tier's fixed item.

Fixed strength levels **MAX-combine**, never add: Bracelet plus Silver is strength 2, not 3.
**Played evidence (Kareem, 2026-11-12, 21:15):** switching ages with Silver/Golden Gauntlets
does not replace child Link's Goron Bracelet; the child keeps it. The Bracelet is separate
child equipment, not an adult downgrade predecessor. `downgrade_tier_exemptions` therefore
excludes it from both the placement screen and finished-seed order replay.
The conservative **adult Silver → Golden** and **Silver Scale → Golden Scale** restrictions
remain; actual downgrade behavior within those pairs is not game-proven.
[INFERENCE] Adult use of Bracelet strength follows vanilla's Forest-before-Spirit order;
the played age-switch check did not test that ability directly.


## Identity: model names are not physical IDs

A placement is identified by **source file and actor `Hash`**, never its array index, position or
translated N64 actor number. Child/adult/Alternative copies of one check must receive the same patch.
Event gifts use **flow and grant node**. Keep the world key, physical identity and player label distinct.
Sources: `AGENTS.md` rules 4–6; `plans/01-architecture.md`; `plans/03-game-data.md`, How collected
checks are recorded; `src/clawshot/data/locations.toml`; `src/clawshot/patch/gift_rules.toml`.

`oot_randomizer_name` links a known corresponding check; an empty link is not permission to infer
one by list order or distance. Remake-only checks use sourced additions. Floor labels come from map
metadata and describe directions, not identity. Pots and other age-dependent actors can have distinct
Hashes at matching positions. Sources: `plans/04-world-format.md`, Overrides;
`plans/03-game-data.md`, Readable location names, Pause-map floors and Pots/crates/ground rupees.

For a tracker, preserve world keys for placements/rules and use `location_names.toml` for display.
Do not allocate Archipelago network IDs from mutable array order; an eventual port needs an explicit
stable mapping from these identities. That network-ID mapping is a port requirement, not an existing
Clawshot feature (architecture: `plans/01-architecture.md`; current scope: the roadmap index plus your round's file).

## Search and seed acceptance

The search repeatedly collects every reachable reward, updates events/inventory and explores exits
until nothing changes. Child/adult reachability is separate, with time tracked when enabled. The
configured goal must hold before a generated seed can be written. Sources:
`src/clawshot/world/search.py`, `src/clawshot/generate/__init__.py`,
`plans/01-architecture.md`, The beatability search, and `plans/04-world-format.md`, Reachability.

Before adult return unlocks, child reachability uses an independent pre-pull inventory/event view;
it cannot borrow later adult finds. Native return follows Forest **quest completion**, not owning
a shuffled medallion. The default first-pull guarantee separately proves adult return from mandatory
pull prerequisites and adult checks, without assuming optional child errands. Free travel changes
both logic and native patches; do not copy the search assumption without that patch contract.
Sources: `plans/04-world-format.md`, Ages; `src/clawshot/world/search.py`;
`src/clawshot/data/world/remake/sheik.toml`; `plans/playtest/answers.md`, R9-FREE-TRAVEL and
R10-FIRST-PULL-FIXED. Open-mode early return and preserved escape/moat rewards passed on rc.7; the clock-state fixes passed the v4/v5 play checks on rc.7 (2026-11-17). See [settings](settings.md).

**No save warp (Round 16).** The remake autosaves room changes; an older manual save is not a logic escape.
The Slingshot Room's entry now requires its existing usable Slingshot/Boomerang/Bow exit condition as well
as the scrub's shield condition. Neither room chest can supply its own first escape tool. A Slingshot copy
may still be there when another usable exit tool is already available.

`world/softlocks.py` checks returns at the initial frontier and each full collection sphere, preserving
age-specific inventory and arrival time. Targets are physical safe anchors: child Link's House or Kokiri
Forest, adult Temple of Time, never the abstract `Root`. Generated and external placements are refused
when the data's `softlock_verified_regions` certificate fails. **This first slice certifies the played
Slingshot trap only**, not the whole world. Unscoped `audit(world, placements)` reports unresolved graph
returns for triage; absent ordinary edges are not physical-trap proof. Held warp songs now count as
returns indoors too (Kareem, played 2026-11-17), through the same age/instrument rules as normal travel.
Farore's Wind ownership alone still does not prove a previously set escape point.

**Child warp arrivals (Round 17).** Bolero's crater landing has no child walking escape (Kareem,
played). Requiem's child Colossus walking return is untested. Both require an already playable Minuet,
Serenade, Nocturne or Prelude before logic counts their child destinations; neither hazardous arrival
rescues the other, and a reward there cannot provide its own first escape song. Adult arrival rules
are unchanged. This safety policy affects all new seeds, including Defaults, without changing settings.
[Round 17 evidence and short play checks](../plans/rounds/r17-bugs.md).

New seeds also validate the incoming native era-change Kokiri Sword equipment candidate against pouch
ownership before equipping it. An absent sword clears only that candidate; no item is granted and logic
does not gain a sword from time travel. Built/native-data-tested, not yet played in game.

Imported Gerudo Fortress rules treat `Gerudo_Membership_Card` as friendly access. In the remake the guards,
desert gate, Training Ground entrance and horseback archery check Spirit quest progress, which the
captain's native hand-over writes after giving the card. D39 keeps `Hideout Gerudo Membership Card`
`keep_vanilla` under every preset and setting, so the card is never in the pool and owning it implies all
four carpenter rescues and that hand-over; the card rules stay unchanged. A port that moves the card
must model completing the captain's source instead: a moved card writes no quest progress. The arrest
route that accepts Longshot where the game checks the Hookshot itself is a separate open review.
Sources: `src/clawshot/data/world/remake/gifts.toml`; D39 in `plans/decisions.md`;
`plans/rounds/r13-gerudo-card.md` (static data trace, not a played route check).

The persistent `Met Child Zelda` event models the **whole courtyard/Impa lesson and accepted
send-off through DoorOfTime Step02**, not first courtyard contact. Both moat rewards, Saria's
song source and **every** Door mode require it; shuffled items do not advance native quests.
Its route is Malon's fixed Egg / Chicken, Talon, the courtyard and Impa. `Field Owl Arrival`
models the saved arrival effect, not literal owl history: native owl play or the real send-off's
missing-arrival restoration supplies it. `Time Flows` and both early Door rules require both events.
The temporary first-adult clock hold is clearable at the native adult Market exit or a genuine
Temple return to child; it is not a persistent search prerequisite. The Market Bombchu Shop also
requires Dodongo's completion and available night. Sources: `remake/child_hyrule_castle.toml`,
`remake/child_hyrule_field.toml`, `remake/child_sacred_forest_meadow.toml`,
`remake/child_market.toml`, `remake/child_temple_of_time.toml`;
[native trace](../plans/03-game-data.md#46-round-14-child-story-and-field-music) and
[clock audit](../plans/rounds/r16-time.md#rc7-played-results-and-clock-follow-up-2026-11-17).
Kareem verified Saria before Darunia and the Step03 escape/reload controls on Longshot on
2026-11-13; Bombchu Shop's entrance correction remains native-data evidence.

The independent adult-return proof retains compulsory child story events using the same
count-cap test as items; optional history is excluded. Both early-door construction bounds include
`Met Child Zelda` and `Field Owl Arrival`; the closed kit retains its native inventory/story minimum.

The fill uses seeded assumed fill, placement restrictions and safe swaps, then an independent
collection search on the completed placement. Item pool preparation uses actual remake identities,
not the untranslated N64 vanilla pool. Shops, floor pickups and gifts have destination restrictions;
held/excluded checks remain fixed sources for logic where applicable. Sources:
`src/clawshot/generate/fill.py`, `src/clawshot/generate/__init__.py`,
`plans/04-world-format.md`, Generating a seed and Replayable generator settings; attribution: `NOTICE`.

Determinism requires the same source/world data, seed and effective settings. Tests include changed
Python hash seeds; unordered placement iteration and timestamps are forbidden. A passing search is
proof of **this model**, not of unplayed remake routes. The earlier Slingshot-room softlock exposed an
N64/remake mismatch; player answers remain essential. Sources: `AGENTS.md` rule 4;
`plans/04-world-format.md`, Generating a seed; [Round 3](../plans/rounds/r3-overview.md), recorded mini-seed result;
`plans/playtest/answers.md`, DT01/DT02.

## Spoiler contract

The JSON is local generated output: **do not upload or distribute it**. The producer is
`src/clawshot/generate/__init__.py` (`spoiler`, `spoiler_json`); metadata specification:
`plans/04-world-format.md`, Generating a seed; physical descriptions:
`src/clawshot/data/location_names.toml`. Consumers should handle nullable/optional descriptive data.

| Top-level field | Meaning |
|---|---|
| `generator` | Generator name and package version; not an exact source revision by itself. |
| `seed` | Seed number. |
| `settings` | Effective settings mapping. |
| `settings_string` | Replayable CS1 representation, requiring the same source/world data. |
| `placements` | World-location key → item for shuffled checks only, not a complete list of fixed rewards. |
| `locations` | Descriptions keyed by those world keys, with catalogue fields and applicable shop/scrub metadata. Custom worlds can lack physical IDs. |
| `opening_route` | A proved child-only opening witness (`name`, `event`, `region`, `steps`), or null. Steps carry kind, location, requirements and alternatives. Not the entire game's route; adult-first seeds can lack this guide while remaining beatable. |
| `opening_route_unavailable` | Null, or `name`, `event`, `region`, `reason` explaining why no child-only opening is listed. No invented pre-pull purchases; the full beatability search remains the seed-validity oracle. |
| `age_locked_pickups` | Wrong-age first-frontier item information, including ties. Not a required play order or a complete pickup-timing analysis. |
| `spheres` | World-keyed progression pickups grouped by search collection sphere; empty progression spheres omitted. Not every collected filler item. |
| `hints` | Stone, where, message label, kind, rendered text, area, location and item; some target fields can be null. |
| `item_names` | Logic item → the name the player sees, for placed items (and the tiers of placed progressive families) whose name differs. A progressive family always keeps its own label. |
| `progressive_grants` | `note` (the route disclaimer) and `locations`: world key → `family`, `possible_tiers` (in order), `canonical_sphere`, `given_in_canonical_sphere_replay` and `leftover_in_canonical_replay` (that tier was already owned); the last three are null where the search never collects it. |

Age-usability source: `src/clawshot/generate/itembar.py`, `plans/03-game-data.md`, Item-bar assignment.
Older-save child Bow failure/recovery: `plans/playtest/answers.md`, R8-SEED8-BOWLOCK/R9-LICHII.
New-game prevention passed Kareem's Bow-first/Boomerang check on 2026-11-12
(`plans/rounds/r13-item-grants.md`); existing saves are unchanged.
Do not reconstruct the complete search using only the progression-filtered `spheres`: include fixed
rewards and the actual world/settings instead (`plans/04-world-format.md`, Reachability).

`progressive_grants` replays the full search spheres in order (native bonuses included as owned
tiers, `clawshot.progressive.next_tier` for each copy, no randomness); `canonical_sphere` counts every
full-search sphere, as the play note does, so it can exceed the length of `spheres`. The tier is
**route dependent**: the child view before return is an independent search prefix, and another
collection order gives other tiers. It is a labelled witness, not a play order or gameplay proof.
Unshuffled ownership-dependent capacity prizes replay their native Medium/Large choice from
that ownership state; a shuffled fixed reward remains its literal assignment.

## What a multiworld port still needs

Clawshot currently generates a static RomFS mod, not a live multiworld client. Archipelago remains
future scope ([roadmap index](../plans/00-roadmap.md), Milestones; decision D8 in `plans/decisions.md`). Reusing the logic does not
automatically provide a playable multiworld integration.

An integration would still need a stable network item/location mapping, check-completion reporting,
connection/session handling, and **items delivered during play**, including durable receipt/reconnect
semantics. A static RomFS mod cannot receive arbitrary items from a network by itself: delivery needs
a hook/API in the runtime plus a client. Runtime code hooks are explicitly a separate future layer in
`plans/01-architecture.md`; these requirements are not shipped interfaces. Keep data licensing
attribution from `NOTICE`, and verify remake routes/grants rather than assuming another runtime or
N64 behavior supplies them. A read-only tracker likewise needs its own observation/import mechanism;
the spoiler is an offline description, not a live state feed.
