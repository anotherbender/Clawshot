from dataclasses import replace

import pytest

from clawshot.census.gifts import DIRECT, Gift
from clawshot.generate import Settings, generate
from clawshot.generate.fill import allowed
from clawshot.patch import gifts, items
from clawshot.world.load import build_world


def song_spec():
    names = {
        "Storms": "Song",
        "Lullaby": "Song",
        "Fairy Ocarina": "Item",
        "Letter": "Item",
        "Coin": "Item",
        "Sword": "Item",
    }
    places = {
        "Song A": ("Song", "Storms"),
        "Song B": ("Song", "Lullaby"),
        "Gift A": ("NPC", "Fairy Ocarina"),
        "Gift B": ("NPC", "Letter"),
        "Chest A": ("Chest", "Coin"),
        "Chest B": ("Chest", "Sword"),
    }
    return {
        "start": "Root",
        "goal": "Sword",
        "items": {name: {"type": kind} for name, kind in names.items()},
        "regions": [{"name": "Root", "locations": {name: "True" for name in places}}],
        "locations": {name: {"type": kind, "vanilla": item} for name, (kind, item) in places.items()},
    }


@pytest.mark.parametrize("mode", ["song", "anywhere"])
def test_song_mode_respects_observed_chest_allowlist_in_actual_fills(mode):
    spec = song_spec()
    world = build_world(spec)
    actors = items.loads("""[items]
Storms = { actor = "Item_Melody_StormSong" }
Lullaby = { actor = "Item_Melody_ZeldaLullaby" }
"Fairy Ocarina" = { actor = "Item_Ocarina_Fairy" }
Letter = { actor = "Item_ZeldaLetter" }
Coin = { actor = "TBox_Rupee_Blue" }
Sword = { actor = "Item_Sword_Kokiri" }
""")
    held = gifts.held_items(world, world.items, actors, {"TBox_Rupee_Blue", "Item_Sword_Kokiri"}, songs=mode)
    settings = Settings(
        shuffle=("Chest", "NPC", "Song"),
        songs=mode,
        item_location_types=held,
        exclusive_location_types=("Song",) if mode == "song" else (),
    )
    assert Settings.from_string(settings.to_string()) == settings
    assert allowed(world, settings, "Chest A", "Fairy Ocarina")
    assert not allowed(world, settings, "Chest A", "Letter")
    assert allowed(world, settings, "Chest A", "Lullaby") == (mode == "anywhere")
    assert allowed(world, settings, "Chest A", "Storms") == (mode == "anywhere")
    seen = set()
    for number in range(30):
        seed = generate(spec, number, settings)
        for location, item in seed.placements.items():
            kind = seed.world.locations[location].type
            assert allowed(seed.world, settings, location, item)
            seen.add((item, kind))
            if mode == "song" and (kind == "Song" or item in ("Storms", "Lullaby")):
                assert kind == "Song" and item in ("Storms", "Lullaby")
    assert ("Fairy Ocarina", "Chest") in seen
    assert (("Storms", "Chest") in seen) == (mode == "anywhere")

    assert (("Lullaby", "Chest") in seen) == (mode == "anywhere")


def test_unknown_songs_mode_is_rejected():
    with pytest.raises(ValueError):
        replace(Settings(), songs="random")


def gift_step(call):
    return Gift("Test/Event0", "npc_gift", "Test", "Test.bfevfl.zs", ("Talk",), "Event0", call, "Actor", "", "")


@pytest.mark.parametrize("item", ["Fairy Ocarina", "Ocarina of Time"])
@pytest.mark.parametrize("mode", ["song", "anywhere"])
def test_ocarina_fill_may_use_reachable_chests_or_hand_overs(item, mode):
    spec = {
        "start": "Root",
        "goal": repr(item),
        "items": {item: {}, "Boomerang": {}, "Rupees (20)": {"class": "normal"}},
        "regions": [
            {
                "name": "Root",
                "locations": {
                    "Early Chest": {"type": "Chest", "vanilla": "Rupees (20)", "rule": "True"},
                    "Locked Chest": {"type": "Chest", "vanilla": "Boomerang", "rule": repr(item)},
                    "Gift": {"type": "NPC", "vanilla": item, "rule": "True"},
                },
            }
        ],
    }
    spec["locations"] = {name: {"type": info["type"]} for name, info in spec["regions"][0]["locations"].items()}
    spec = gifts.restrict_spec(
        spec, ["Gift"], {"Gift": (gift_step("NpcCommon:NpcCommon_HandOver_NpcToPlayer_NoDisplay"),)}
    )
    world = build_world(spec)
    held = gifts.held_items(world, world.items, items.load(), {"TBox_Rupee_Red", "Item_Boomerang"}, songs=mode)
    settings = Settings(
        shuffle=("Chest", *gifts.GIFT_TYPES),
        songs=mode,
        item_location_types=held,
        exclusive_location_types=("Song",) if mode == "song" else (),
    )
    seed = generate(spec, 1, settings, attempts=1)
    source = next(name for name, placed in seed.placements.items() if placed == item)
    assert source in ("Early Chest", "Gift")
    sphere_of = {name: index for index, sphere in enumerate(seed.spheres) for name in sphere}
    assert sphere_of[source] < sphere_of["Locked Chest"]
    for kind in gifts.GIFT_TYPES:
        world.locations["Gift"] = replace(world.locations["Gift"], type=kind)
        assert allowed(world, settings, "Gift", item) is (kind != "Song" or mode == "anywhere")


@pytest.mark.parametrize("item", ["Fairy Ocarina", "Ocarina of Time"])
@pytest.mark.parametrize("call", [DIRECT, "GetPouchContent:GetPouchContentByActorName"])
def test_direct_story_and_hand_over_destinations_have_distinct_model_requirements(item, call):
    places = {
        "Story Scene": {"type": "NPC", "vanilla": item, "rule": "True"},
        "Hand Over": {"type": "NPC", "vanilla": "Rupees (20)", "rule": "True"},
    }
    spec = {
        "start": "Root",
        "goal": repr(item),
        "items": {item: {}, "Rupees (20)": {"class": "normal"}},
        "regions": [{"name": "Root", "locations": places}],
        "locations": {name: {"type": info["type"]} for name, info in places.items()},
    }
    steps = {
        "Story Scene": (gift_step(call),),
        "Hand Over": (gift_step("Dm_SY_GetInEvent:GetInEvent_NotTurn_NotNpc"),),
    }
    spec = gifts.restrict_spec(spec, places, steps)
    world = build_world(spec)
    held = gifts.held_items(world, world.items, items.load(), set(), songs="anywhere")
    settings = Settings(shuffle=("NPC",), item_location_types=held)
    assert not gifts.is_hand_over("NPC", steps["Story Scene"])
    assert gifts.is_hand_over("NPC", steps["Hand Over"])
    for name in places:
        assert allowed(world, settings, name, item)


@pytest.mark.parametrize("kind", ["Scrub", "GrottoScrub"])
def test_ocarina_scrub_sales_are_model_requiring_destinations(kind):
    places = {
        "Chest": {"type": "Chest", "vanilla": "Rupees (20)", "rule": "True"},
        "Sale": {"type": kind, "vanilla": "Fairy Ocarina", "rule": "True"},
    }
    spec = {
        "start": "Root",
        "goal": "Fairy_Ocarina",
        "items": {"Fairy Ocarina": {}, "Rupees (20)": {"class": "normal"}},
        "regions": [{"name": "Root", "locations": places}],
        "locations": {name: {"type": info["type"]} for name, info in places.items()},
    }
    spec = gifts.restrict_spec(spec, ())
    world = build_world(spec)
    settings = Settings(shuffle=("Chest", kind))
    assert gifts.is_hand_over(kind, ())
    assert allowed(world, settings, "Sale", "Fairy Ocarina")


@pytest.mark.parametrize(
    "item,chest_safe",
    [
        ("Bottle", True),
        ("Bottle with Milk", False),
        ("Double Defense", True),
        ("Stone of Agony", True),
        ("Rupees (200)", True),
    ],
)
def test_token_grants_keep_unplayed_chest_variants_held(item, chest_safe):
    token = "Gold Skulltula Token"
    places = {
        "Gift": {"type": "NPC", "vanilla": item, "rule": "True", "excluded_items": [item]},
        "Chest": {"type": "Chest", "vanilla": "Fairy Ocarina", "rule": "True"},
        "Skulltula": {"type": "GS Token", "vanilla": token, "rule": "True"},
    }
    spec = {
        "start": "Root",
        "goal": f"{item!r} and Gold_Skulltula_Token",
        "items": {
            item: {"class": "normal" if item in ("Double Defense", "Rupees (200)") else "progression"},
            "Fairy Ocarina": {},
            token: {"type": "Token"},
        },
        "regions": [{"name": "Root", "locations": places}],
    }
    world = build_world(spec)
    actors = items.load()
    held = gifts.held_items(world, [item], actors, set(), token_shuffle=True)
    legacy = gifts.held_items(world, [item], actors, set())
    if not chest_safe:
        assert "Token" not in legacy[item] and "Chest" not in held[item]
        assert set(held[item]) == {*legacy[item], "Token"}
    settings = Settings(shuffle=("Chest", "NPC", "Token"), item_location_types=held)
    assert allowed(world, settings, "Skulltula", item)
    assert allowed(world, settings, "Chest", item) is chest_safe
    seed = generate(spec, 7, settings, attempts=1)
    assert seed.placements["Gift"] == "Fairy Ocarina"
    assert seed.placements["Skulltula"] in (item, token)
    assert generate(spec, 7, Settings.from_string(seed.settings.to_string()), attempts=1).placements == seed.placements


def test_unplayed_gift_grant_does_not_gain_token_destinations():
    world = build_world({"start": "Root", "goal": "True", "items": {"Letter": {}}, "regions": [{"name": "Root"}]})
    actors = items.loads('[items]\nLetter = { actor = "Item_ZeldaLetter" }\n')
    held = gifts.held_items(world, ["Letter"], actors, set(), token_shuffle=True)
    assert "Token" not in held["Letter"] and "Chest" not in held["Letter"]
