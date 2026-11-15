"""From a seed to a mod folder: the item-to-actor table, the patch plan and the writer.

    out = make_seed(romfs, 12345, Settings())     # census, remake pool, fill, beatability search, plan
    write_seed(out, romfs, Path("seed-12345"))     # romfs overlay, spoiler.json and play-note.md

The chest pool uses ``remake_vanilla``; opt-in Shop locations use the native shop
catalog; opt-in Token checks keep their native token pool and are written by
``clawshot.patch.tokens`` (new pickup packs, spoiler ``patch.tokens``). The fill and
beatability search are ``clawshot.generate``'s.
"""

import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from clawshot.census import definitions as census_definitions
from clawshot.census.scan import scan
from clawshot.generate import Seed, Settings, from_placements, generate, play_note, prepare, spoiler
from clawshot.generate import hints as stone_hints
from clawshot.generate import names as location_names
from clawshot.generate import tokens as token_policy
from clawshot.generate.fill import shuffled_locations
from clawshot.patch import bags, custom_items, darunia, drops, freestanding, gamedata, scrubs, shops, text, tokens
from clawshot.patch import events as chest_events
from clawshot.patch import items as item_actors
from clawshot.patch import receive_event as receive_event_patch
from clawshot.patch.custom_items import Foreign
from clawshot.patch.plan import Links, PatchError, Plan, link, make_plan, remake_vanilla, restrict_event_openings
from clawshot.patch.write import FileChanges, NewFile, WrittenFile, write
from clawshot.settings import CATALOG, validate_logic_overrides
from clawshot.world.load import load_spec

__all__ = ["PatchError", "PatchStep", "SeedOutput", "make_seed", "write_seed"]

# A kind-specific step closes over its census/romfs context. File transforms receive decompressed bytes;
# multiple steps touching one file compose in registration order, after the chest changes.
PatchStep = Callable[[Mapping[str, str]], FileChanges]


@dataclass(frozen=True)
class SeedOutput:
    seed: Seed
    links: Links
    plan: Plan
    extra_changes: tuple[FileChanges, ...] = ()
    fast_start_files: tuple[gamedata.BuiltFile, ...] = ()
    item_names: dict[str, str] = field(default_factory=dict)
    """The game's (English) names of the items the hints name, as the stones say them."""
    new_files: dict[str, NewFile] = field(default_factory=dict)
    """Files the dump does not hold: custom item/Skulltula actor packs and receive-event flow."""
    token_sources: tuple[tokens.SourceChange, ...] = ()
    """Every shuffled Token location's source and grant, for the spoiler's ``patch.tokens``."""

    def spoiler(self) -> dict[str, Any]:
        patch = self.plan.as_dict()
        if self.token_sources:
            patch["tokens"] = [source.as_dict() for source in self.token_sources]
        return spoiler(self.seed, self.item_names) | {"patch": patch}

    def spoiler_json(self) -> str:
        return json.dumps(self.spoiler(), indent=2, ensure_ascii=False) + "\n"


def make_seed(
    romfs: str | Path,
    seed: int,
    settings: Settings,
    spec: Mapping[str, Any] | None = None,
    *,
    extra_steps: Sequence[PatchStep] = (),
    placements: Mapping[str, str] | None = None,
    foreign: Mapping[str, Foreign] | None = None,
    possessive_text: bool = False,
    receive_event: bool = False,
) -> SeedOutput:
    """Fill a seed; kind-specific steps turn placements into decompressed file transforms.

    With ``placements`` the shuffled locations take those items instead of Clawshot's fill (another placer's, such
    as an Archipelago multiworld's; see ``generate.from_placements``), and no Gossip Stone hints are chosen.
    ``foreign`` names the player and item of each location placed ``Archipelago Item``; ``possessive_text`` makes
    the get line of every item the seed holds say "your" (``clawshot.patch.custom_items``); ``receive_event`` adds
    the event a runtime module requests to give an item with the game's own notice (``patch.receive_event``).
    A solo seed places neither custom item and sets neither switch, so none of this changes its output."""
    spec = load_spec() if spec is None else spec
    validate_logic_overrides(spec, settings.logic)
    definitions = census_definitions.load()
    if scrubs.SHUFFLE in settings.shuffle:
        spec, settings, step = scrubs.seed_setup(spec, settings)
        extra_steps = (*extra_steps, step)
    if freestanding.SHUFFLE in settings.shuffle:
        spec = freestanding.restrict_spec(spec, definitions)
    fast_settings = gamedata.load()
    names = [*settings.fast_start, *CATALOG["forest"][settings.forest]["fast_start"]]
    chosen = [*gamedata.load_always(), *gamedata.select(fast_settings, names)]
    _, world = prepare(spec, settings)
    table = item_actors.load()
    table.check(world.items)
    shuffled = shuffled_locations(world, settings)
    chests = [name for name in shuffled if world.locations[name].type == "Chest"]
    shop_locations = tuple(name for name in shuffled if world.locations[name].type == "Shop")
    floor_pickups = sum(world.locations[name].type in (drops.SHUFFLE, freestanding.SHUFFLE) for name in shuffled)
    token_locations = [name for name in shuffled if world.locations[name].type == token_policy.SHUFFLE]
    if len(chests) + len(shop_locations) + floor_pickups + len(token_locations) != len(shuffled) and not extra_steps:
        raise PatchError("non-chest shuffle needs a kind-specific extra patch step")
    token_rewards = token_policy.REWARDS if token_locations else {}
    if unadmitted := sorted({family for _, family in token_rewards.values()} - token_policy.ADMITTED_FAMILIES):
        raise PatchError(f"Token rewards name grant families production does not admit: {unadmitted}")
    if shop_locations or settings.cheap_deku_shield:
        extra_steps = (
            *extra_steps,
            shops.patch_step(
                romfs,
                shop_locations,
                shop_prices=settings.shop_prices,
                cheap_deku_shield=settings.cheap_deku_shield,
            ),
        )
    census = scan(romfs)
    links = link(world, chests, definitions, census)
    token_sources = tokens.link_sources(token_locations, definitions, census) if token_locations else {}
    vanilla = remake_vanilla(world, links, table)
    spec = restrict_event_openings(spec, world, links, chest_events.load())
    if freestanding.SHUFFLE in settings.shuffle:
        settings, step = freestanding.seed_setup(world, settings, census, definitions, vanilla)
        extra_steps = (*extra_steps, step)
    if drops.SHUFFLE in settings.shuffle:
        settings, step = drops.seed_setup(world, settings, census, definitions, vanilla)
        extra_steps = (*extra_steps, step)
    if placements is None:
        out = generate(spec, seed, settings, vanilla=vanilla)
    else:
        out = from_placements(spec, seed, settings, placements, vanilla=vanilla)
    custom = custom_step(romfs, out, links, table, foreign or {}, possessive_text=possessive_text)
    changes = tuple(step(out.placements) for step in extra_steps)
    flags = list(custom.flags)
    new_files = dict(custom.new_files)
    token_rows: tuple[tokens.SourceChange, ...] = ()
    if token_sources:
        # Token insertion validates the original dump row snapshot; custom rows then insert by name.
        delivery, token_rows = tokens.seed_delivery(
            romfs, out.placements, token_sources, links.names, census, rewards=token_rewards
        )
        changes += (delivery.changes,)
        if overlap := sorted(new_files.keys() & delivery.new_files.keys()):
            raise PatchError(f"custom items and Skulltula pickups both create {overlap}")
        new_files.update(delivery.new_files)
    if custom.changes:
        changes += (custom.changes,)
    if receive_event:
        event_changes, event_files = receive_event_patch.changes(romfs)
        changes += (event_changes,)
        new_files.update(event_files)
        flags.append(receive_event_patch.FLAG)
    if flags:
        from clawshot.patch.gifts import game_data_transform

        changes += ({gamedata.GAME_DATA_LIST: game_data_transform(flags)},)
    # Fast-start initial values compose before gift flag additions; its flow edits run before other flow steps.
    if scrubs.SHUFFLE not in settings.shuffle:
        changes += (scrubs.changes({}),)
    changes = (gamedata.changes(chosen), *changes)
    if world.settings.get("free_time_travel", False):
        from clawshot.patch.age import changes as age_changes

        changes += (age_changes(out.placements, free_time_travel=True),)
    from clawshot.patch import door, start_items

    changes += (door.changes(out.placements, mode=settings.door_of_time), start_items.changes())
    item_names: dict[str, str] = {}
    if out.hints:
        item_names, hint_changes = hint_step(romfs, out, table)
        changes += (hint_changes,)
    catalog = location_names.load()
    hookshot_locations = [
        catalog[name].name if name in catalog else name
        for name, item in sorted(out.placements.items())
        if item in ("Hookshot", "Progressive Hookshot")
    ]
    changes += (text.sheik_hint_changes(romfs, hookshot_locations),)
    fast_files = tuple(door.build(romfs, mode=settings.door_of_time))
    plan = make_plan(out, links, table, chest_events.load(), overrides=custom.actors)
    from clawshot.patch import keys, progressive, progressive_bonus

    # Darunia's source flag and forward-only Fire step precede Event127's bonus wrapper, which keeps its next.
    changes += (darunia.changes(),)
    # Bonus guards and source-bound selections precede bag guards; unrelated native callers stay unchanged.
    changes += (progressive_bonus.changes(romfs, out, prior_changes=changes),)
    plan, key_changes = keys.changes(romfs, plan, prior_changes=changes)
    changes += (key_changes,)
    plan, progressive_changes = progressive.changes(romfs, plan, prior_changes=changes)
    changes += (progressive_changes, bags.changes(romfs))
    return SeedOutput(out, links, plan, changes, fast_files, item_names, new_files, token_rows)


def custom_step(
    romfs: str | Path,
    seed: Seed,
    links: Links,
    table: item_actors.ItemActors,
    foreign: Mapping[str, Foreign],
    *,
    possessive_text: bool,
) -> custom_items.CustomItems:
    """The custom items the seed places (Nothing, other players' items) and the "your" get lines."""
    by_item: dict[str, list[str]] = {item: [] for item in custom_items.CUSTOM_ITEMS}
    for name in seed.shuffled:
        if seed.placements.get(name) in by_item:
            by_item[seed.placements[name]].append(name)
    placed = [name for names in by_item.values() for name in names]
    not_chests = sorted(name for name in placed if name not in links.chests)
    if not_chests:
        raise PatchError(f"Nothing and other players' items go only to chests so far, not {not_chests[:5]}")
    unnamed = sorted(set(by_item[custom_items.FOREIGN_ITEM]) - set(foreign))
    if unnamed:
        raise PatchError(f"no player and item named for the Archipelago items at {unnamed[:5]}")
    stray = sorted(set(foreign) - set(by_item[custom_items.FOREIGN_ITEM]))
    if stray:
        raise PatchError(f"other players' items named for locations that do not hold one: {stray[:5]}")
    own = [table.actors[item] for item in seed.placements.values() if item in table.actors] if possessive_text else []
    if possessive_text:
        from clawshot.progressive import CHAINS

        own.extend(tier.actor for item in seed.placements.values() if item in CHAINS for tier in CHAINS[item])
    return custom_items.changes(
        romfs, nothing_locations=by_item[custom_items.NOTHING_ITEM], foreign=foreign, own_actors=own
    )


def hint_step(romfs: str | Path, seed: Seed, table: item_actors.ItemActors) -> tuple[dict[str, str], FileChanges]:
    """The seed's hints as text changes: every language archive's stone lines (English: D26) and, with
    ``hints = "always"``, the flow that lets stones speak without the Mask of Truth. Returns the item names used."""
    names = text.item_names(romfs, [hint.item for hint in seed.hints if hint.item], table)
    catalog = location_names.load()
    lines = {
        hint.label: stone_hints.text(
            hint,
            lambda item: names.get(item, item),
            lambda name: catalog[name].name if name in catalog else name,
            marked=True,
        )
        for hint in seed.hints
    }
    changes = text.hint_changes(romfs, lines, text.languages(romfs), without_mask=seed.settings.hints == "always")
    return names, changes


def write_seed(output: SeedOutput, romfs: str | Path, out: str | Path) -> list[WrittenFile]:
    """Write changed romfs files, ``spoiler.json`` and the readable ``play-note.md``."""
    out = Path(out)
    log = output.spoiler()
    spoiler_text = json.dumps(log, indent=2, ensure_ascii=False) + "\n"
    note_text = play_note(output.seed, log)
    written = write(
        output.plan,
        romfs,
        out,
        extra_changes=output.extra_changes,
        fast_start_files=output.fast_start_files,
        new_files=output.new_files,
    )
    (out / "spoiler.json").write_text(spoiler_text, encoding="utf-8", newline="\n")
    (out / "play-note.md").write_text(note_text, encoding="utf-8", newline="\n")
    return written
