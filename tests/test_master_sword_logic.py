"""Master Sword shuffle logic and pool (Round 19 cs19c; ``plans/rounds/r18-master-sword-design.md`` sections 7-9).

Off, every sword rewrite folds to the rule before it; on, an adult fights only with an owned blade, child weapons never
arm him, the alternatives a rule names still work, and the pool holds one Master Sword: in a chest, never on its own
pedestal. Built, not played."""

import itertools
import random
import re
import tomllib
from collections import Counter
from pathlib import Path

import pytest

from clawshot.generate import FillError, Settings, generate, prepare, swords
from clawshot.generate.fill import shuffled_locations
from clawshot.progressive import CHAINS, FAMILY_BY_ITEM
from clawshot.world import ADULT, CHILD, Search, build_world, load_spec
from clawshot.world.load import WorldError
from clawshot.world.rules import DAY, NIGHT

OVERRIDES = Path(swords.__file__).resolve().parents[1] / "data" / "world" / "remake" / "master_sword.toml"
FREE = "free_time_travel"
ON = Settings(shuffle_master_sword=True, logic={FREE: True})
LOGIC_ON = {swords.SETTING: True}
BLADES = ("Master Sword", "Biggoron Sword")
KNIFE = "Giants Knife"  # breakable (r18-master-sword-design.md section 8): logic never counts it as a sword
HAMMER = "Megaton Hammer"
BOSSES = {"Defeat Phantom Ganon", "Defeat Morpha", "Defeat Twinrova", "Defeat Bongo Bongo"}
# Every count a child-only weapon is read through (Kokiri Sword, Slingshot, Boomerang, sticks, Deku Shield).
CHILD_WEAPONS = frozenset(
    {
        "Kokiri Sword",
        "Slingshot",
        "Boomerang",
        "Buy Deku Stick (1)",
        "Buy Deku Stick (5)",
        "Deku Stick (1)",
        "Deku Stick Drop",
        "Buy Deku Shield",
        "Deku Shield",
        "Deku Shield Drop",
    }
)
ICE_END = (
    "(is_adult or Slingshot or Sticks or Kokiri_Sword or can_use(Dins_Fire)) and Ocarina and (is_child or (Ocarina, 2))"
)
LIZALFOS = "is_adult or Sticks or Slingshot or Bombs or Kokiri_Sword"
# Rewritten entries owned by other override files, as they stood before Round 19 (base d9deb65).
BEFORE = {
    ("exits", "Forest Temple Lobby", "Forest Temple Central Area"): (
        "(Small_Key_Forest_Temple, 1) and (is_adult or can_child_attack or Nuts)"
    ),
    ("exits", "Gerudo Training Ground Lobby", "Gerudo Training Ground Lava Room Front"): (
        "here(has_explosives and (is_adult or Kokiri_Sword)) and can_use(Goron_Tunic)"
    ),
    ("events", "Ice Cavern End", "Ice Cavern End Chest Access"): ICE_END,
    ("exits", "Water Temple Falling Platform Room", "Water Temple Dark Link Region"): "can_use(Hookshot)",
    ("exits", "Deku Tree Top Floor", "Deku Tree Basement"): "here(is_adult or can_child_attack or Nuts)",
    ("locations", None, "Deku Tree GS Compass Room"): "is_adult or can_child_attack",
    ("exits", "Dodongos Cavern Upper Lizalfos", "Dodongos Cavern Bomb Bag Ledge"): (
        f"({LIZALFOS}) and (can_use(Slingshot) or can_use(Bow))"
    ),
    ("locations", None, "Kak Redead Grotto Chest"): "is_adult or Sticks or Kokiri_Sword or can_use(Dins_Fire)",
    ("locations", None, "Dodongo Cavern Room 5 Chest (TBox_Rupee_Red)"): LIZALFOS,
    ("locations", None, "Dodongo Cavern Room 16 Chest (Item_ScrubBusinessSeed)"): LIZALFOS,
    ("locations", None, "Sheik in Ice Cavern"): ICE_END,
    ("locations", None, "Song from Royal Familys Tomb"): (
        "(is_adult or Slingshot or Boomerang or Sticks or has_explosives or Kokiri_Sword) and Ocarina "
        "and (is_child or (Ocarina, 2))"
    ),
    ("locations", None, "HF GS Lone Tree"): "can_bonk and (is_adult or can_child_attack)",
    ("locations", None, "Spirit Temple Mirror Shield Chest"): "True",
}
# The played Beamos alternatives widened after the sword rewrite (Hammer r21, reflected Mirror beam r22).
# Compare the sword guard against that current kill contract, not the older explosives-only predicate.
BEAMOS_WIDENED = frozenset(
    {
        "Gerudo Training Ground Beamos Chest",
        "Gerudo Training Ground Lobby -> Gerudo Training Ground Lava Room Front",
    }
)
# OoT Randomizer's True (or weaponless) rules that gained a fight: they agree off for the adult, the only age there.
ADULT_ONLY = frozenset(
    {
        "Forest Temple Bow Chest",
        "Forest Temple Floormaster Chest",
        "Shadow Temple Map Chest",
        "Shadow Temple Compass Chest",
        "Fire Temple Megaton Hammer Chest",
        "Shadow Temple Hover Boots Chest",
        "Shadow Temple After Wind Enemy Chest",
        "Spirit Temple Mirror Shield Chest",
        "Gerudo Training Ground Before Heavy Block Chest",
        "Gerudo Training Ground Hammer Room Clear Chest",
    }
)


def _on(**fields):
    return Settings(shuffle_master_sword=True, logic={FREE: True}, **fields)


@pytest.fixture(scope="module")
def spec():
    return load_spec()


def _entries(spec):
    """``(label, current rule, rule before, adult only)`` for every sword rewrite: master_sword.toml's against its
    ``was``, the other files' against :data:`BEFORE`."""
    with OVERRIDES.open("rb") as stream:
        data = tomllib.load(stream)
    regions = {region["name"]: region for region in spec["regions"]}
    holder = {name: region for region in spec["regions"] for name in region.get("locations", {})}

    def current(kind, region, name):
        table = holder[name]["locations"] if kind == "locations" else regions[region][kind]
        value = table[name]
        return value["rule"] if isinstance(value, dict) else value

    out = []
    for name, fields in data["helpers"].items():
        assert spec["helpers"][name]["rule"] == fields["rule"], name
        out.append((f"helper {name}", fields["rule"], fields["was"], False))
    for name, fields in data["locations"].items():
        assert current("locations", None, name) == fields["rule"], name
        out.append((name, fields["rule"], fields["was"], name in ADULT_ONLY))
    for kind in ("exits", "events"):
        for region, table in data[kind].items():
            for name, fields in table.items():
                assert current(kind, region, name) == fields["rule"], (region, name)
                out.append((f"{region} -> {name}", fields["rule"], fields["was"], False))
    for (kind, region, name), before in BEFORE.items():
        rule = current(kind, region, name)
        assert any(word in rule for word in ("adult_sword", "adult_weapon", "can_kill_")), (region, name, rule)
        out.append((name if region is None else f"{region} -> {name}", rule, before, name in ADULT_ONLY))
    widened = {label for label, *_ in out} & BEAMOS_WIDENED
    assert widened == BEAMOS_WIDENED, widened
    return [
        (
            label,
            new,
            old.replace("has_explosives", "(can_blast_or_smash or can_use(Mirror_Shield))")
            if label in widened
            else old,
            adult_only,
        )
        for label, new, old, adult_only in out
    ]


def _unwrap(text):
    """here(rule) and at(region, rule) as the rule itself: compared as text in one probe region."""
    return re.sub(r"\bhere\(", "(", re.sub(r"\bat\('[^']*',\s*", "(", text))


def _probe(spec, texts, logic=None):
    """The compiled rules of ``texts``, each a probe location of one extra region."""
    names = {f"Probe {index}": _unwrap(text) for index, text in enumerate(texts)}
    probe = {
        **spec,
        "regions": [*spec["regions"], {"name": "Probe", "locations": names}],
        "locations": {**spec["locations"], **{name: {"type": "Probe"} for name in names}},
    }
    world = build_world(probe, logic)
    return [world.locations[name].rule for name in names]


def _inventories(names, seed):
    """Every subset of ``names`` (held 9 times) up to ten names, else 512 seeded random subsets plus none and all."""
    names = sorted(names)
    if len(names) <= 10:
        subsets = itertools.product((0, 1), repeat=len(names))
        return [{n: 9 for n, bit in zip(names, bits, strict=True) if bit} for bits in subsets]
    rng = random.Random(seed)
    return [{}, dict.fromkeys(names, 9), *({n: 9 for n in names if rng.random() < 0.5} for _ in range(512))]


def test_off_every_sword_rewrite_folds_to_the_rule_before_it(spec):
    entries = _entries(spec)
    rules = _probe(spec, [text for _, new, old, _ in entries for text in (new, old)])
    for index, (label, *_, adult_only) in enumerate(entries):
        new, old = rules[2 * index], rules[2 * index + 1]
        ages = (ADULT,) if adult_only else (CHILD, ADULT)
        for counts in _inventories(new.reads | old.reads, label):
            for age, tod in itertools.product(ages, (DAY, NIGHT)):
                assert new(counts, age, tod) == old(counts, age, tod), (label, age, tod, counts)


def test_adult_only_rewrites_are_in_rooms_no_child_reaches(spec):
    world = build_world(spec, {FREE: True})
    search = Search(world, [loc.vanilla for loc in world.locations.values() if loc.vanilla and loc.n64_only is None])
    for name in ADULT_ONLY:
        assert not search.can_reach(world.locations[name].region, CHILD), name


def test_child_weapons_never_arm_a_swordless_adult(spec):
    entries = _entries(spec)
    rules = _probe(spec, [new for _, new, _, _ in entries], LOGIC_ON)
    for (label, *_), rule in zip(entries, rules, strict=True):
        for counts in _inventories(rule.reads - set(BLADES), label):
            without = {name: count for name, count in counts.items() if name not in CHILD_WEAPONS}
            for tod in (DAY, NIGHT):
                assert rule(counts, ADULT, tod) == rule(without, ADULT, tod), (label, tod, counts)


SWORD_ONLY = (
    "can_jumpslash",
    "can_kill_stalfos",
    "can_kill_skulltula",
    "can_kill_withered_deku_baba",
    "can_mow_the_lawn",
)


@pytest.mark.parametrize("text", SWORD_ONLY)
def test_a_swordless_adult_with_the_child_arsenal_cannot_strike(spec, text):
    [rule] = _probe(spec, [text], LOGIC_ON)
    everything = {name: 9 for name in rule.reads if name not in (*BLADES, HAMMER)}
    assert CHILD_WEAPONS & set(everything), text
    assert not rule(everything, ADULT, DAY), text
    assert not rule({**everything, KNIFE: 1}, ADULT, DAY), text
    for blade in BLADES:
        assert rule({**everything, blade: 1}, ADULT, DAY), (text, blade)
    assert rule(everything, CHILD, DAY), text  # the same arsenal still arms the child


@pytest.mark.parametrize(
    "text, alternative",
    [
        ("can_jumpslash", {HAMMER: 1}),
        ("can_kill_stalfos", {HAMMER: 1}),
        ("can_kill_iron_knuckle", {HAMMER: 1}),
        ("can_kill_biri", {"Progressive Hookshot": 1}),
        ("can_kill_bari", {"Bow": 1}),
        ("can_kill_blue_bubble", {HAMMER: 1}),
        ("can_kill_flare_dancer", {HAMMER: 1}),
        ("can_cut_shrubs", {HAMMER: 1}),
        ("can_stun_deku", {"Deku Nut Drop": 1}),
    ],
)
def test_named_alternatives_still_arm_a_swordless_adult(spec, text, alternative):
    [rule] = _probe(spec, [text], LOGIC_ON)
    assert set(alternative) <= rule.reads, (text, sorted(rule.reads))
    assert rule(alternative, ADULT, DAY), text


def test_assists_alone_do_not_replace_the_sword(spec):
    biri, bubble = _probe(spec, ["can_kill_biri", "can_kill_blue_bubble"], LOGIC_ON)
    assert not biri({"Magic Meter": 1}, ADULT, DAY)
    assert biri({"Magic Meter": 1, "Biggoron Sword": 1}, ADULT, DAY)
    assert not bubble({"Mirror Shield": 1}, ADULT, DAY)
    assert not bubble({"Mirror Shield": 1, KNIFE: 1}, ADULT, DAY)
    assert bubble({"Mirror Shield": 1, "Master Sword": 1}, ADULT, DAY)


@pytest.fixture(scope="module")
def on_world(spec):
    return build_world(spec, {**LOGIC_ON, FREE: True})


@pytest.mark.parametrize(
    "where",
    [
        "Forest Temple First Stalfos Chest",
        "Forest Temple Bow Chest",
        "Shadow Temple Hover Boots Chest",
        "Gerudo Training Ground Stalfos Chest",
        "Ganons Tower Boss Key Chest",
    ],
)
def test_sword_fights_at_checks_need_an_owned_blade(on_world, where):
    rule = on_world.locations[where].rule
    everything = {name: 9 for name in rule.reads if name not in (*BLADES, HAMMER)}
    assert not rule(everything, ADULT, DAY), where
    assert not rule({**everything, KNIFE: 1}, ADULT, DAY), where
    assert rule({**everything, "Biggoron Sword": 1}, ADULT, DAY), where


@pytest.mark.parametrize("event", sorted(BOSSES))
def test_sword_bosses_need_an_owned_blade(on_world, event):
    rule = next(e.rule for e in on_world.events if e.name == event)
    everything = {name: 9 for name in rule.reads if name not in BLADES}  # the Megaton Hammer too
    assert not rule(everything, ADULT, DAY), event
    assert not rule({**everything, KNIFE: 1}, ADULT, DAY), event
    assert rule({**everything, "Master Sword": 1}, ADULT, DAY), event


def _finale(world):
    exits = world.regions["Ganons Castle Tower Below Boss"].exits
    entrance = next(e.rule for e in exits if e.target == "Ganondorf Boss Room")
    triforce = next(e.rule for e in world.events if e.name == "Triforce")
    return entrance, triforce


def test_ganondorf_admits_only_an_owned_master_sword(spec, on_world):
    entrance, triforce = _finale(on_world)
    key = {"Boss Key (Ganons Castle)": 1}
    arrows = {"Bow": 1, "Light Arrows": 1, "Magic Meter": 1}
    for blade in ("Biggoron Sword", KNIFE):
        assert not entrance({**key, blade: 1}, ADULT, DAY)
        assert not triforce({**arrows, blade: 1}, ADULT, DAY)
    assert entrance({**key, "Master Sword": 1}, ADULT, DAY)
    assert triforce({**arrows, "Master Sword": 1}, ADULT, DAY)
    entrance, triforce = _finale(build_world(spec))
    assert entrance(key, ADULT, DAY) and triforce(arrows, ADULT, DAY)  # off: the native, always-armed finale


def _pool(world, blade=None):
    items = [loc.vanilla for loc in world.locations.values() if loc.vanilla and loc.n64_only is None]
    return [item for item in items if item not in (*BLADES, KNIFE)] + ([blade] if blade else [])


def test_off_world_needs_no_sword_item(spec):
    world = build_world(spec, {FREE: True})
    search = Search(world, _pool(world))
    assert {name for name, count in search.inventory(ADULT).items() if count} >= BOSSES
    assert search.won()


@pytest.mark.parametrize("blade", [None, "Biggoron Sword", KNIFE, "Master Sword"])
def test_every_item_beats_ganon_only_with_the_master_sword(on_world, blade):
    search = Search(on_world, _pool(on_world, blade))
    held = {name for name in BOSSES if search.inventory(ADULT).get(name)}
    assert held == (BOSSES if blade in BLADES else set()), (blade, held)
    assert search.won() is (blade == "Master Sword")


def test_off_prepare_leaves_the_spec_and_world_unchanged(spec):
    assert swords.prepare_spec(spec, Settings()) is spec
    effective, world = prepare(spec, Settings())
    assert swords.PEDESTAL not in world.locations
    assert not any(loc.type == swords.TYPE or loc.vanilla == swords.ITEM for loc in world.locations.values())
    assert world.settings[swords.SETTING] is False
    assert swords.ITEM not in effective.item_location_types and swords.TYPE not in effective.location_type_items


@pytest.fixture(scope="module")
def prepared(spec):
    return prepare(spec, ON)


def test_on_pool_has_one_master_sword_from_its_own_pedestal_check(prepared):
    effective, world = prepared
    pedestal = world.locations[swords.PEDESTAL]
    assert (pedestal.type, pedestal.vanilla, pedestal.region) == (swords.TYPE, swords.ITEM, "Beyond Door of Time")
    assert pedestal.rule.always  # the first-pull event's own rule
    assert [name for name, loc in world.locations.items() if loc.vanilla == swords.ITEM] == [swords.PEDESTAL]
    shuffled = shuffled_locations(world, effective)
    assert swords.PEDESTAL in shuffled
    assert Counter(world.locations[name].vanilla for name in shuffled)[swords.ITEM] == 1
    assert world.settings[swords.SETTING] is True
    # Time travel, Rauru's reward and the first-arrival song stay their own checks and event.
    assert world.locations["ToT Reward from Rauru"].vanilla == "Light Medallion"
    assert any(event.name == "Time Travel" and event.region == "Beyond Door of Time" for event in world.events)


def test_on_master_sword_goes_only_to_chests_and_the_pedestal_takes_only_plain_grants(prepared):
    effective, world = prepared
    assert effective.item_location_types[swords.ITEM] == ("Chest",)
    palette = set(effective.location_type_items[swords.TYPE])
    assert palette == set(swords.pedestal_items(world))
    assert {"Biggoron Sword", HAMMER, "Kokiri Sword", "Rupees (20)"} <= palette
    for name in palette:
        item = world.items[name]
        assert item.type == "Item" and item.dungeon is None and not item.tier, name
        assert name not in CHAINS and name not in FAMILY_BY_ITEM and name not in world.progressive, name
        assert not name.startswith("Buy "), name
    excluded = {swords.ITEM, "Gold Skulltula Token", "Small Key (Forest Temple)", "Progressive Hookshot", "Bow"}
    assert not palette & excluded


def test_seed_places_the_master_sword_in_a_chest_and_a_plain_grant_on_the_pedestal(spec):
    seed = generate(spec, 19, ON)
    assert Counter(seed.placements[name] for name in seed.shuffled)[swords.ITEM] == 1
    [where] = [name for name in seed.shuffled if seed.placements[name] == swords.ITEM]
    assert seed.world.locations[where].type == "Chest"
    assert seed.placements[swords.PEDESTAL] in seed.settings.location_type_items[swords.TYPE]


@pytest.mark.parametrize(
    "settings, message",
    [
        (Settings(logic={swords.SETTING: True}), "must agree"),
        (Settings(shuffle_master_sword=True, logic={FREE: True, swords.SETTING: False}), "must agree"),
        (_on(item_location_types={swords.ITEM: ["Shop"]}), "only to"),
        (_on(location_type_items={swords.TYPE: [swords.ITEM]}), "cannot grant"),
        (_on(location_type_items={swords.TYPE: ["Progressive Hookshot"]}), "cannot grant"),
        (_on(location_type_items={swords.TYPE: ["Small Key (Forest Temple)"]}), "cannot grant"),
        (_on(item_location_types={"Gold Skulltula Token": ["Chest", swords.TYPE]}), "cannot give"),
    ],
)
def test_impossible_combinations_are_refused(spec, settings, message):
    with pytest.raises(FillError, match=message):
        prepare(spec, settings)


def test_explicit_settings_may_narrow_the_holds_and_agreeing_logic_is_kept(spec):
    narrow = Settings(
        shuffle_master_sword=True,
        logic={FREE: True, swords.SETTING: True},
        location_type_items={swords.TYPE: [HAMMER, "Rupees (20)"]},
    )
    effective, world = prepare(spec, narrow)
    assert effective.location_type_items[swords.TYPE] == (HAMMER, "Rupees (20)")
    assert effective.item_location_types[swords.ITEM] == ("Chest",)
    assert world.settings[swords.SETTING] is True


def test_the_world_own_setting_must_stay_false(spec):
    tampered = {**spec, "settings": {**spec["settings"], swords.SETTING: True}}
    with pytest.raises(WorldError, match="must be false"):
        swords.prepare_spec(tampered, Settings())


@pytest.mark.parametrize(
    "where",
    ["Forest Temple Floormaster Chest", "Shadow Temple Map Chest", "Shadow Temple Compass Chest"],
)
def test_native_enemy_counter_chests_need_a_usable_clearance_weapon(on_world, where):
    rule = on_world.locations[where].rule
    child_arsenal = dict.fromkeys(CHILD_WEAPONS, 9)
    assert not rule(child_arsenal, ADULT, DAY), (where, child_arsenal)
    assert rule({**child_arsenal, "Biggoron Sword": 1}, ADULT, DAY), where
    assert rule({**child_arsenal, "Megaton Hammer": 1}, ADULT, DAY), where
