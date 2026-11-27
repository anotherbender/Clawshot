"""The limits ocarina-song-drops-everywhere leaves unchanged (1.5, 1.6, 1.7): songs stay on song lessons by default,
shops never take an ocarina or a song, ``Missable`` refuses progression and dungeon rewards stay pinned.

Synthetic worlds run the real fill; the whole world runs the real ``prepare`` and the fill's own predicate.
"""

from types import MappingProxyType

import pytest

from clawshot.generate import Settings, generate, prepare
from clawshot.generate import tokens as token_policy
from clawshot.generate.fill import allowed
from clawshot.patch import drops, gifts
from clawshot.patch import items as item_actors
from clawshot.world.load import build_world, load_spec

OCARINAS = ("Fairy Ocarina", "Ocarina of Time")
SONGS = ("Zeldas Lullaby", "Prelude of Light")
KINDS = ("Chest", "Token", "BossHeart", "Freestanding", "NPC", "Scrub")


def every_kind_spec() -> dict:
    places = {f"{kind} Check": {"type": kind, "vanilla": "Rupees (20)", "rule": "True"} for kind in KINDS}
    places["Token Check"] = {"type": token_policy.SOURCE_TYPE, "vanilla": token_policy.TOKEN_ITEM, "rule": "True"}
    places |= {f"Lesson {i}": {"type": "Song", "vanilla": song, "rule": "True"} for i, song in enumerate(SONGS)}
    places["Ocarina Chest"] = {"type": "Chest", "vanilla": "Fairy Ocarina", "rule": "True"}
    places["Time Chest"] = {"type": "Chest", "vanilla": "Ocarina of Time", "rule": "True"}
    return {
        "start": "Root",
        "goal": "True",
        "items": {
            "Rupees (20)": {"class": "normal"},
            token_policy.TOKEN_ITEM: {"type": "Token"},
            **{item: {} for item in OCARINAS},
            **{song: {"type": "Song"} for song in SONGS},
        },
        "regions": [{"name": "Root", "locations": places}],
    }


@pytest.fixture
def new_members(monkeypatch):
    """The Token policy and floor palette as they will be once the new members are admitted (plans 13.2, 16.4)."""
    members = {
        "Fairy Ocarina": ("Obj_Clawshot_Ocarina_Fairy", "ocarina"),
        **{song: ("Obj_Clawshot_Melody_" + song.replace(" ", ""), "song") for song in SONGS},
    }
    monkeypatch.setattr(token_policy, "REWARDS", MappingProxyType({**token_policy.REWARDS, **members}))


def seed_settings(spec: dict, songs: str) -> Settings:
    world = build_world(spec)
    actors = item_actors.load()
    floors = {
        kind: tuple(drops.floor_items(world, Settings(songs=songs), actors, kind=kind))
        for kind in ("BossHeart", "Freestanding")
    }
    held = gifts.held_items(world, (*OCARINAS, *SONGS), actors, set(), songs=songs, token_shuffle=True)
    return Settings(
        shuffle=KINDS + ("Song",),
        songs=songs,
        item_location_types=held,
        exclusive_location_types=("Song",) if songs == "song" else (),
        location_type_items=floors,
    )


def test_with_songs_on_song_lessons_no_song_reaches_another_kind(new_members):
    spec = every_kind_spec()
    settings = seed_settings(spec, "song")
    _, world = prepare(spec, settings)
    for name, location in world.locations.items():
        for song in SONGS:
            assert allowed(world, settings, name, song) == (location.type == "Song"), (name, song)
    for number in range(20):
        seed = generate(spec, number, settings, attempts=1)
        for name in seed.shuffled:
            if seed.placements[name] in SONGS:
                assert seed.world.locations[name].type == "Song", (number, name)


def test_with_songs_anywhere_the_kind_matrix_holds_for_songs_and_ocarinas(new_members):
    spec = every_kind_spec()
    settings = seed_settings(spec, "anywhere")
    _, world = prepare(spec, settings)
    for kind in ("Token", "BossHeart", "Freestanding"):
        for item in (*OCARINAS, *SONGS):
            if kind == "Token" and item == "Ocarina of Time":
                continue  # admitted long before this feature; in the world palette as in the real one
            assert allowed(world, settings, f"{kind} Check", item) == (
                kind != "Freestanding" or item != "Fairy Ocarina"
            ), (kind, item)


def test_shops_never_take_an_ocarina_or_a_song():
    settings = Settings(shuffle=("Chest", "Shop", "NPC", "Song", "Cutscene", "Boss", "Scrub"), songs="anywhere")
    _, world = prepare(load_spec(), settings)
    shelves = [name for name, location in world.locations.items() if location.type == "Shop"]
    songs = [name for name, item in world.items.items() if item.type == "Song"]
    assert shelves and len(songs) == 12
    for shelf in shelves:
        for item in (*OCARINAS, *songs):
            assert not allowed(world, settings, shelf, item), (shelf, item)


@pytest.mark.parametrize("item", [*OCARINAS, *SONGS])
def test_missable_checks_still_refuse_ocarinas_and_songs(item):
    spec = every_kind_spec()
    spec["regions"][0]["locations"]["Missable Check"] = {"type": "Missable", "vanilla": "Rupees (20)", "rule": "True"}
    world = build_world(spec)
    assert world.items[item].progression
    assert not allowed(world, Settings(shuffle=("Chest", "Missable"), songs="anywhere"), "Missable Check", item)


@pytest.mark.parametrize("item", [*OCARINAS, *SONGS])
def test_dungeon_rewards_stay_pinned_to_their_checks(item):
    spec = every_kind_spec()
    spec["items"]["Kokiri Emerald"] = {"stone": True}
    spec["regions"][0]["locations"]["Reward"] = {"type": "DungeonReward", "vanilla": "Kokiri Emerald", "rule": "True"}
    world = build_world(spec)
    settings = Settings(shuffle=("Chest", "BossHeart"), songs="anywhere", dungeon_rewards=True)
    assert not allowed(world, settings, "Reward", item)
    assert not allowed(world, settings, "BossHeart Check", "Kokiri Emerald")
