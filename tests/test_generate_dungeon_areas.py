"""Generic dungeon rewards must be collected inside the dungeon they credit, unless a chest's grant names it."""

import pytest
from test_generate import chest, dungeon_world

from clawshot.generate import FillError, Settings, generate
from clawshot.generate.fill import allowed, check_beatable, is_restricted
from clawshot.patch import gifts, make_seed
from clawshot.world import build_world, load_spec, load_world

OWN, ANYWHERE, ALL = Settings(), Settings(dungeon_items="anywhere"), Settings(dungeon_items="all_anywhere")
CHEST_FAMILIES = ["SmallKey", "BossKey", "GanonBossKey", "Map", "Compass"]
"""The families ``all_anywhere`` lets out; ``anywhere`` lets out only the first."""
NON_CHEST = ["Freestanding", "NPC", "Scrub", "BossHeart", "Token"]


@pytest.mark.parametrize("kind", CHEST_FAMILIES)
def test_logical_dungeon_location_outside_its_area_cannot_receive_dungeon_item(kind):
    item = f"{kind} (Temple)"
    spec = {
        "start": "Temple Lobby",
        "goal": f"'{item}'",
        "items": {item: {"type": kind}, "Coin": {"class": "normal"}},
        "regions": [
            {
                "name": "Temple Lobby",
                "area": "TempleArea",
                "dungeon": "Temple",
                "locations": {
                    "Inside": {"type": "Chest", "vanilla": item, "rule": "True"},
                    "Outside": {
                        "type": "Chest",
                        "vanilla": "Coin",
                        "rule": "True",
                        "area": "OverworldArea",
                    },
                },
            }
        ],
    }
    world = build_world(spec)
    assert not allowed(world, OWN, "Outside", item), (kind, world.locations["Outside"])
    assert allowed(world, OWN, "Inside", item)
    # Small keys anywhere names only small keys; all dungeon items anywhere names every chest family.
    assert allowed(world, ANYWHERE, "Outside", item) is (kind == "SmallKey")
    assert allowed(world, ALL, "Outside", item)
    for settings in (ANYWHERE, ALL):
        assert allowed(world, settings, "Inside", item)
    result = generate(spec, 0, Settings(), attempts=1)
    assert result.placements == {"Inside": item, "Outside": "Coin"}
    check_beatable(result.world, result.placements)


def contract_world() -> dict:
    """Two dungeons, each with a chest and a floor pick-up, and an overworld with a chest and other check kinds."""
    families = [*CHEST_FAMILIES, "SmallKeyRing", "SilverRupee"]
    items = {f"{kind} (Temple)": {"type": kind} for kind in families}
    floor = {"type": "Freestanding", "vanilla": "Coin", "rule": "True"}
    return {
        "start": "Field",
        "goal": "True",
        "items": {**items, "Coin": {"class": "normal"}},
        "regions": [
            {
                "name": "Field",
                "area": "FieldArea",
                "locations": {
                    "Field Chest": chest("Coin"),
                    **{f"Field {kind}": {**floor, "type": kind} for kind in NON_CHEST},
                },
            },
            {
                "name": "Temple",
                "area": "TempleArea",
                "dungeon": "Temple",
                "locations": {"Temple Chest": chest("Coin"), "Temple Floor": floor},
            },
            {
                "name": "Cave",
                "area": "CaveArea",
                "dungeon": "Cave",
                "locations": {"Cave Chest": chest("Coin"), "Cave Floor": floor},
            },
        ],
    }


def test_all_anywhere_releases_every_chest_family_and_only_into_chests():
    world = build_world(contract_world())
    outside_chests = ("Field Chest", "Cave Chest")  # the overworld and another dungeon
    outside_others = (*(f"Field {kind}" for kind in NON_CHEST), "Cave Floor")
    for kind in CHEST_FAMILIES:
        item = f"{kind} (Temple)"
        assert is_restricted(world, OWN, item)
        assert is_restricted(world, ANYWHERE, item) is (kind != "SmallKey")
        assert not is_restricted(world, ALL, item)
        for settings in (OWN, ANYWHERE, ALL):
            # Its own dungeon takes it at any kind of check, as before; elsewhere never at a non-chest check.
            assert allowed(world, settings, "Temple Chest", item) and allowed(world, settings, "Temple Floor", item)
            assert not any(allowed(world, settings, name, item) for name in outside_others), (kind, settings)
        assert not any(allowed(world, OWN, name, item) for name in outside_chests)
        assert all(allowed(world, ANYWHERE, name, item) is (kind == "SmallKey") for name in outside_chests)
        assert all(allowed(world, ALL, name, item) for name in outside_chests), kind
    # Key rings and silver rupees have no chest grant: they stay in every mode.
    for kind in ("SmallKeyRing", "SilverRupee"):
        item = f"{kind} (Temple)"
        for settings in (OWN, ANYWHERE, ALL):
            assert is_restricted(world, settings, item)
            assert not any(allowed(world, settings, name, item) for name in (*outside_chests, *outside_others))
    assert not is_restricted(world, ALL, "Coin")


@pytest.mark.parametrize("chest_name", ["Spirit Temple Silver Gauntlets Chest", "Spirit Temple Mirror Shield Chest"])
def test_spirit_hands_take_named_small_keys_and_with_all_anywhere_every_chest_family(chest_name):
    world = load_world()
    for item in (
        "Small Key (Spirit Temple)",
        "Boss Key (Spirit Temple)",
        "Map (Spirit Temple)",
        "Compass (Spirit Temple)",
    ):
        assert not allowed(world, OWN, chest_name, item), (chest_name, item, world.locations[chest_name])
        assert allowed(world, OWN, "Spirit Temple Map Chest", item)
        assert allowed(world, ANYWHERE, chest_name, item) is (world.items[item].type == "SmallKey")
        assert allowed(world, ALL, chest_name, item)


@pytest.mark.parametrize(
    "item",
    ["Boss Key (Ganons Castle)", "Boss Key (Fire Temple)", "Map (Deku Tree)", "Compass (Water Temple)"],
)
def test_world_dungeon_items_leave_only_with_all_anywhere_and_only_for_chests(item):
    world = load_world()
    home = {
        "Boss Key (Ganons Castle)": "Ganons Tower Boss Key Chest",
        "Boss Key (Fire Temple)": "Fire Temple Map Chest",
        "Map (Deku Tree)": "Deku Tree Map Chest",
        "Compass (Water Temple)": "Water Temple Compass Chest",
    }[item]
    chests = ("KF Midos Top Left Chest", "Forest Temple First Room Chest")  # overworld, another dungeon
    # Another kind of check: a gift, a Skulltula, a floor heart piece, a boss heart in a dungeon's own Banc folder
    # (outside its logical dungeon) and another dungeon's scrub.
    others = (
        "LW Skull Kid",
        "KF GS Know It All House",
        "LLR Freestanding PoH",
        "Deku Tree Queen Gohma Heart",
        "Dodongos Cavern Deku Scrub Side Room Near Dodongos",
    )
    for settings in (OWN, ANYWHERE, ALL):
        assert allowed(world, settings, home, item)
        assert not any(allowed(world, settings, name, item) for name in others), settings
    for name in chests:
        assert not allowed(world, OWN, name, item)
        assert not allowed(world, ANYWHERE, name, item)  # small keys anywhere leaves every other family home
        assert allowed(world, ALL, name, item), name


def two_dungeon_world() -> dict:
    """``dungeon_world`` with a second dungeon and its compass, and floor pick-ups in the village and the temple."""
    spec = dungeon_world()
    spec["items"] = {**spec["items"], "Compass (Cave)": {"type": "Compass", "class": "priority"}}
    floor = {"type": "Freestanding", "rule": "True"}
    regions = spec["regions"]
    village = next(region for region in regions if region["name"] == "Village")
    village["locations"] = {**village["locations"], "Village Floor": {**floor, "vanilla": "Recovery Heart"}}
    village["exits"] = {**village["exits"], "Cave": "True"}
    hall = next(region for region in regions if region["name"] == "Dungeon Hall")
    hall["locations"] = {**hall["locations"], "Hall Floor": {**floor, "vanilla": "Rupees (5)"}}
    regions.append(
        {
            "name": "Cave",
            "dungeon": "Cave",
            "locations": {"Cave Chest": chest("Rupees (5)"), "Cave Compass Chest": chest("Compass (Cave)")},
        }
    )
    return spec


def breaks_and_moves(seed) -> tuple[list[tuple[str, str]], set[str]]:
    """Dungeon items outside their dungeon (its logical regions within its physical Banc folder) at a non-chest
    check; the families found outside their dungeon."""
    world, breaks, moved = seed.world, [], set()
    for name in seed.shuffled:
        item, location = seed.placements[name], world.locations[name]
        info, region = world.items[item], world.regions[location.region]
        if info.dungeon is None or (region.dungeon == info.dungeon and location.area == region.area):
            continue
        moved.add(info.type)
        if location.type != "Chest":
            breaks.append((name, item))
    return breaks, moved


def test_all_anywhere_seeds_move_every_family_through_chests_and_old_anywhere_moves_only_small_keys():
    spec = two_dungeon_world()
    shuffle = ("Chest", "Freestanding")
    moved = {"anywhere": set(), "all_anywhere": set()}
    for mode in moved:
        for number in range(60):
            seed = generate(spec, number, Settings(shuffle=shuffle, dungeon_items=mode))
            breaks, families = breaks_and_moves(seed)
            assert breaks == [], (mode, number)
            moved[mode] |= families
            check_beatable(seed.world, seed.placements)
    assert moved["anywhere"] == {"SmallKey"}
    assert moved["all_anywhere"] == {"SmallKey", "BossKey", "Map", "Compass"}


def test_an_all_anywhere_seed_of_the_whole_world_keeps_foreign_dungeon_items_in_chests():
    seed = generate(load_spec(), 0, ALL)
    assert seed.settings.logic["keysanity"] is True
    assert breaks_and_moves(seed)[0] == []


def test_all_anywhere_enables_keysanity_and_both_anywhere_modes_require_chests():
    spec = dungeon_world()
    spec["settings"] = {**spec["settings"], "keysanity": False}
    assert generate(spec, 1, ALL).settings.logic == {"keysanity": True}
    with pytest.raises(FillError, match="'all_anywhere' needs the logic setting keysanity = true"):
        generate(spec, 1, Settings(dungeon_items="all_anywhere", logic={"keysanity": False}))
    for mode in ("anywhere", "all_anywhere"):
        with pytest.raises(ValueError):
            Settings(dungeon_items=mode, shuffle=("Freestanding",))
    restored = Settings.from_string(ALL.to_string())
    assert restored == ALL and restored.to_string() != ANYWHERE.to_string()


def test_new_mode_normalizes_native_keysanity_metadata_without_changing_released_anywhere():
    spec = dungeon_world()
    spec["flags"] = {"keysanity": False}
    old = generate(spec, 1, ANYWHERE)
    assert "keysanity" not in old.settings.logic
    assert old.world.settings["keysanity"] is False
    seed = generate(spec, 1, ALL)
    assert seed.settings.logic["keysanity"] is True
    assert seed.world.settings["keysanity"] is True
    with pytest.raises(FillError, match="keysanity = true"):
        generate(spec, 1, Settings(dungeon_items="all_anywhere", logic={"keysanity": False}))


@pytest.mark.dump
def test_community_seed_eleven_keeps_spirit_dungeon_items_off_both_hands(romfs):
    settings = Settings(shuffle=("Chest", "Shop", "Gift", "Scrub", "BossHeart"))
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
    result = make_seed(romfs, 11, settings, spec, extra_steps=(step,)).seed
    for name in ("Spirit Temple Silver Gauntlets Chest", "Spirit Temple Mirror Shield Chest"):
        assert result.world.items[result.placements[name]].dungeon is None, (name, result.placements[name])
    check_beatable(result.world, result.placements)
