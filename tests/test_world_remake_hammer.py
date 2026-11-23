"""Round 21 (plans/rounds/r21-hammer.md): the Megaton Hammer opens what the remake's data and Kareem's play say it
opens, per object class, and nothing else: cracked walls, cracked floors, grotto covers and the ground Beamos widen;
King Dodongo, the Shadow Temple skull pots and the webs keep their explosives; with Master Sword shuffle on, ordinary
enemy fights take the Hammer while the bosses keep the sword."""

import pytest

from clawshot.world import ADULT, CHILD, load_world
from clawshot.world.rules import DAY

HAMMER = {"Megaton Hammer": 1}
BOMBS = {"Bomb Bag": 1, "Progressive Strength Upgrade": 1}

# (kind, region, name, the other items the rule asks for): explosives there break a WallCrack-family wall or floor, a
# BrokenBomb grotto cover or a ground Beamos (Kareem, Longshot 3.0.0, 2026-11-23: one Hammer hit destroys one).
WIDENED = [
    ("stone", None, "DMC Gossip Stone", {}),
    ("exit", "Zoras Fountain", "ZF Great Fairy Fountain", {}),
    ("exit", "Hyrule Field", "HF Wetland Grotto", {}),
    ("location", None, "Fire Temple Big Lava Room Blocked Door Chest", {}),
    ("location", None, "Fire Temple GS Boulder Maze", {}),
    ("location", None, "Fire Temple Boulder Maze Shortcut Chest", {}),
    ("location", None, "Shadow Temple After Wind Hidden Chest", {}),
    ("exit", "Shadow Temple First Beamos", "Shadow Temple Huge Pit", {"Small Key (Shadow Temple)": 5}),
    ("location", None, "Dodongo Cavern Room 10 Chest (Item_ScrubBusinessSeed)", {}),
    ("location", None, "Dodongos Cavern GS Alcove Above Stairs", {}),
    ("location", None, "Water Temple GS Falling Platform Room", {}),
    (
        "exit",
        "Water Temple Lowered Water Levels",
        "Water Temple South Basement",
        {"Iron Boots": 1, "Progressive Hookshot": 1},
    ),
    (
        "exit",
        "Water Temple North Basement",
        "Water Temple Boss Key Chest Room",
        {"Iron Boots": 1, "Progressive Strength Upgrade": 1},
    ),
    ("exit", "Spirit Temple Anubis Room", "Spirit Temple Beyond Anubis Room", {}),
    ("location", None, "Gerudo Training Ground Beamos Chest", {}),
    # The Lava Room Front exit's here(): the Beamos room, compiled into the lobby's third subrule event.
    ("event", "Gerudo Training Ground Lobby", "Gerudo Training Ground Lobby Subrule 3", {}),
]

# Explosives the data says the Hammer cannot replace (Hammer 0.0 on the skull pots and webs) or that Kareem keeps.
KEPT = [
    ("location", None, "Shadow Temple GS Triple Giant Pot"),
    ("location", None, "Shadow Temple Freestanding Key"),
    ("location", None, "Shadow Temple Invisible Floormaster Chest"),
    ("event", "King Dodongo Boss Room", "Defeat King Dodongo"),
    ("exit", "Dodongos Cavern Far Bridge", "Dodongos Cavern Mouth"),
]


def _rule(world, kind, region, name):
    if kind == "location":
        return world.locations[name].rule
    if kind == "stone":
        return world.hint_stones[name].rule
    if kind == "exit":
        return next(e.rule for e in world.regions[region].exits if e.target == name)
    return next(e.rule for e in world.events if e.name == name and e.region == region)


@pytest.fixture(scope="module")
def world():
    return load_world()


@pytest.fixture(scope="module")
def sword_world():
    return load_world({"shuffle_master_sword": True})


@pytest.mark.parametrize(("kind", "region", "name", "base"), WIDENED, ids=[w[2] for w in WIDENED])
def test_the_hammer_opens_what_bombs_open(world, kind, region, name, base):
    rule = _rule(world, kind, region, name)
    assert not rule(base, ADULT, DAY), name
    assert rule({**base, **HAMMER}, ADULT, DAY), name
    assert rule({**base, **BOMBS}, ADULT, DAY), name  # bombs still open it
    assert not rule({**base, **HAMMER}, CHILD, DAY), name  # the Hammer is the adult's


@pytest.mark.parametrize(("kind", "region", "name"), KEPT, ids=[k[2] for k in KEPT])
def test_the_hammer_does_not_replace_explosives_the_data_or_kareem_keeps(world, kind, region, name):
    rule = _rule(world, kind, region, name)
    base = {item: 9 for item in rule.reads if item.startswith("Silver Rupee")}  # the Freestanding Key's spikes room
    assert rule({**base, **BOMBS}, ADULT, DAY), name  # explosives open it
    assert not rule({**base, **HAMMER}, ADULT, DAY), name
    assert not rule({**base, **HAMMER, "Progressive Hookshot": 2, "Bow": 1}, ADULT, DAY), name


ENEMY_FIGHTS = [
    ("location", None, "HF GS Lone Tree"),
    ("location", None, "Kak Redead Grotto Chest"),
    ("location", None, "Gerudo Training Ground Stalfos Chest"),
    ("location", None, "Ganons Tower Boss Key Chest"),
    ("event", "Hideout 1 Torch Jail", "Hideout 1 Torch Jail Gerudo"),
    ("exit", "Water Temple Falling Platform Room", "Water Temple Dark Link Region"),
]
BOSSES = [
    ("Phantom Ganon Boss Room", "Defeat Phantom Ganon"),
    ("Morpha Boss Room", "Defeat Morpha"),
    ("Bongo Bongo Boss Room", "Defeat Bongo Bongo"),
    ("Twinrova Boss Room", "Defeat Twinrova"),
]


@pytest.mark.parametrize(("kind", "region", "name"), ENEMY_FIGHTS, ids=[e[2] for e in ENEMY_FIGHTS])
def test_a_swordless_adult_fights_enemies_with_the_hammer(sword_world, world, kind, region, name):
    rule = _rule(sword_world, kind, region, name)
    others = {"Progressive Hookshot": 1, "Small Key (Ganons Castle)": 9}
    assert not rule(others, ADULT, DAY), name
    assert rule({**others, **HAMMER}, ADULT, DAY), name
    assert _rule(world, kind, region, name)(others, ADULT, DAY), name  # off: any adult, as before


@pytest.mark.parametrize(("region", "name"), BOSSES)
def test_bosses_still_need_a_blade(sword_world, region, name):
    rule = _rule(sword_world, "event", region, name)
    everything = {item: 9 for item in rule.reads if item not in ("Master Sword", "Biggoron Sword")}
    assert not rule({**everything, **HAMMER}, ADULT, DAY), name
    assert rule({**everything, "Master Sword": 1}, ADULT, DAY), name
