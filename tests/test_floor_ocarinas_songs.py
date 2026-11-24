"""Ocarinas and songs on BossHeart and Freestanding floors (ocarina-song-drops-everywhere 1.4, 2.4, A8.1, A8.2).

Synthetic worlds, census rows and placement trees built in code: the floor palette is built from settings and the
world, each item maps to its world actor, and the floor writers swap a saved heart's ``Gyaml`` to it.
"""

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.scan import Location
from clawshot.formats import byml
from clawshot.formats.byml import F32, U64
from clawshot.generate import Settings, prepare
from clawshot.patch import drops, freestanding, getitem, ocarina_pickup, songs
from clawshot.patch import items as item_actors
from clawshot.patch.plan import PatchError
from clawshot.world.load import build_world

ACTORS = item_actors.load()
SONG_ITEMS = {item: actor for item, actor in ACTORS.actors.items() if actor in getitem.SONG_MODELS}
OCARINAS = {"Ocarina of Time": "Obj_Clawshot_Ocarina_Time", "Fairy Ocarina": ocarina_pickup.PICKUP}
SONG_PICKUPS = {item: songs.pickup_name(actor) for item, actor in SONG_ITEMS.items()}
NEW_PICKUPS = sorted({*OCARINAS.values(), *SONG_PICKUPS.values()})


def world(*items):
    places = {"Chest": {"type": "Chest", "vanilla": "Heart Container", "rule": "True"}}
    names = {"Heart Container": {"class": "normal"}}
    names |= {item: {"type": "Song"} if item in SONG_ITEMS else {} for item in items}
    return build_world(
        {"start": "Root", "goal": "True", "items": names, "regions": [{"name": "Root", "locations": places}]}
    )


def test_twelve_songs_map_to_their_floor_actors():
    assert len(SONG_ITEMS) == 12
    assert set(SONG_PICKUPS.values()) == {songs.pickup_name(actor) for actor in getitem.SONG_MODELS}


@pytest.fixture
def floor_ocarinas(monkeypatch):
    """Both ocarinas admitted to floors, as plan 16.4 will do once their arrow-based actors pass in game."""
    monkeypatch.setattr(drops, "FLOOR_OCARINAS", frozenset(OCARINAS))


def test_the_ocarinas_floor_actors_are_the_generated_ones():
    assert drops.OCARINA_PICKUPS == OCARINAS
    assert "Obj_Ocarina_Time" not in drops.PICKUPS  # its moat Box body is an invisible box on a floor (F1-c)


def test_both_ocarinas_are_admitted_to_floors_after_their_runs():
    """Plan 16.1 gated them after run F1; 16.4 lifted the gate after runs G1 and TG2 (BBender, 2026-11-24)."""
    assert frozenset(OCARINAS) == drops.FLOOR_OCARINAS
    found = drops.floor_items(world(*OCARINAS, *SONG_ITEMS), Settings(songs="anywhere"), ACTORS)
    assert found == {**drops.NATIVE_ITEMS, **OCARINAS, **SONG_PICKUPS}


def test_a_gated_ocarina_stays_off_floors(monkeypatch):
    monkeypatch.setattr(drops, "FLOOR_OCARINAS", frozenset())
    found = drops.floor_items(world(*OCARINAS, *SONG_ITEMS), Settings(songs="anywhere"), ACTORS)
    assert found == {**drops.NATIVE_ITEMS, **SONG_PICKUPS}


@pytest.mark.parametrize("mode", ["song", "anywhere"])
def test_the_floor_palette_takes_admitted_ocarinas_and_songs_only_anywhere(mode, floor_ocarinas):
    found = drops.floor_items(world(*OCARINAS, *SONG_ITEMS), Settings(songs=mode), ACTORS)
    expected = {**drops.NATIVE_ITEMS, **OCARINAS, **(SONG_PICKUPS if mode == "anywhere" else {})}
    assert found == expected


def test_items_outside_the_world_stay_out_of_the_palette(floor_ocarinas):
    assert drops.floor_items(world(), Settings(songs="anywhere"), ACTORS) == drops.NATIVE_ITEMS


def test_the_native_palette_itself_is_unchanged():
    assert drops.NATIVE_ITEMS == {
        "Heart Container": "Obj_Heart_Container",
        "Piece of Heart": "Obj_Heart_Piece",
        "Deku Shield": "Obj_Shield_Deku",
        "Hylian Shield": "Obj_Shield_Hylian",
        "Rupees (20)": "Obj_Rupee_Red",
    }
    assert freestanding.NATIVE_ITEMS is drops.NATIVE_ITEMS


def boss_heart():
    files = ("Banc/Test/Static.bcett.byml.zs",)
    return Location(42, "heart_container", "Test", 7, files, "both", (1, 2, 3), drops.HEART, drops.HEART, None, True)


def boss_tree():
    return {
        "Actors": [
            {"Hash": U64(42), "Gyaml": drops.HEART, "Translate": [F32(1.0), F32(2.0), F32(3.0)]},
            {"Hash": U64(43), "Gyaml": "Enemy_Boss"},
        ],
        "AiGroups": [{"References": [{"Id": "Obj_Heart_Container_1", "Reference": U64(42)}]}],
        "SimultaneousGroups": [[U64(42), U64(43)]],
        "FarDeleteGroups": [[U64(42), U64(43)]],
    }


def floor_heart():
    files = ("Banc/Test/Static.bcett.byml.zs",)
    return Location(
        44, "freestanding", "Test", 0, files, "both", (0, 0, 0), "Obj_Heart_Piece", "Obj_Heart_Piece", None, True
    )


def floor_tree():
    return {
        "Actors": [
            {
                "Hash": U64(44),
                "Gyaml": "Obj_Heart_Piece",
                "Phive": {"Placement": {"ID": U64(44)}},
                "Translate": [F32(-4.0), F32(111.5), F32(-34.25)],
            }
        ]
    }


@pytest.mark.parametrize("pickup", NEW_PICKUPS)
def test_both_floor_writers_swap_a_saved_heart_to_an_ocarina_or_song_actor(pickup):
    for writer, loc, tree in ((drops, boss_heart(), boss_tree()), (freestanding, floor_heart(), floor_tree())):
        (transform,) = writer.changes({loc.id: pickup}, [loc]).values()
        after = byml.read(transform(byml.write(tree)))
        assert after["Actors"][0]["Gyaml"] == pickup
        x, y, z = tree["Actors"][0]["Translate"]
        lifted = after["Actors"][0]["Translate"]
        assert lifted[0] == x and lifted[2] == z and isinstance(lifted[1], F32)
        assert float(lifted[1]) == pytest.approx(float(y) + drops.FLOOR_LIFT)
        after["Actors"][0]["Gyaml"] = tree["Actors"][0]["Gyaml"]
        after["Actors"][0]["Translate"] = tree["Actors"][0]["Translate"]
        assert byml.same(after, tree)  # Hash, groups, logic binding and placement identity stay


def test_generated_floor_actors_are_lifted_and_native_ones_are_not():
    assert frozenset(NEW_PICKUPS) == drops.LIFTED
    assert 0 < drops.FLOOR_LIFT <= 0.62  # at most the songs' Temple of Time float height (BBender, TS4)
    for writer, loc, tree in ((drops, boss_heart(), boss_tree()), (freestanding, floor_heart(), floor_tree())):
        (transform,) = writer.changes({loc.id: "Obj_Heart_Piece"}, [loc]).values()
        after = byml.read(transform(byml.write(tree)))
        assert byml.same(after["Actors"][0]["Translate"], tree["Actors"][0]["Translate"])


def test_a_lifted_pickup_without_a_position_is_refused():
    tree = floor_tree()
    del tree["Actors"][0]["Translate"]
    (transform,) = freestanding.changes({44: ocarina_pickup.PICKUP}, [floor_heart()]).values()
    with pytest.raises(PatchError, match="Translate"):
        transform(byml.write(tree))


@pytest.mark.parametrize("pickup", ["Obj_Arrow_Fire", "Item_Ocarina_Fairy", "Item_Melody_ZeldaLullaby"])
def test_the_bare_donors_and_inventory_actors_stay_refused(pickup):
    with pytest.raises(PatchError):
        drops.changes({42: pickup}, [boss_heart()])
    with pytest.raises(PatchError):
        freestanding.changes({44: pickup}, [floor_heart()])


def boss_setup(*items):
    spec = {
        "start": "Root",
        "goal": "True",
        "settings": {"starting_age": "child"},
        "items": {
            "Heart Container": {"class": "normal"},
            **{item: {"type": "Song"} if item in SONG_ITEMS else {} for item in items},
        },
        "regions": [{"name": "Root", "locations": {"Heart A": "True", "Chest": "True"}}],
        "locations": {
            "Heart A": {"type": "BossHeart", "vanilla": "Heart Container"},
            "Chest": {"type": "Chest", "vanilla": items[0] if items else "Heart Container"},
        },
    }
    definitions = [Definition(42, "heart_container", "Test", "Heart A", drops.HEART, "Heart A")]
    return spec, [boss_heart()], definitions


@pytest.mark.parametrize("mode", ["song", "anywhere"])
def test_boss_heart_setup_holds_the_settings_palette_and_writes_its_actor(mode, floor_ocarinas):
    spec, census, definitions = boss_setup("Fairy Ocarina", "Zeldas Lullaby")
    settings = Settings(shuffle=("Chest", "BossHeart"), songs=mode)
    _, prepared = prepare(spec, settings)
    effective, step = drops.seed_setup(prepared, settings, census, definitions, {})
    palette = effective.location_type_items["BossHeart"]
    assert "Fairy Ocarina" in palette and ("Zeldas Lullaby" in palette) == (mode == "anywhere")
    (transform,) = step({"Heart A": "Fairy Ocarina"}).values()
    assert byml.read(transform(byml.write(boss_tree())))["Actors"][0]["Gyaml"] == ocarina_pickup.PICKUP
    if mode == "song":
        with pytest.raises(PatchError):
            step({"Heart A": "Zeldas Lullaby"})


def test_a_replayed_palette_without_the_new_items_stays_native():
    spec, census, definitions = boss_setup("Ocarina of Time")
    native = Settings(shuffle=("Chest", "BossHeart"), location_type_items={"BossHeart": tuple(drops.NATIVE_ITEMS)})
    _, prepared = prepare(spec, native)
    effective, _ = drops.seed_setup(prepared, native, census, definitions, {})
    assert set(effective.location_type_items["BossHeart"]) == set(drops.NATIVE_ITEMS)


def test_freestanding_setup_holds_the_same_palette(floor_ocarinas):
    spec, census, definitions = boss_setup("Ocarina of Time", "Prelude of Light")
    spec["locations"]["Heart A"] = {"type": "Collectable", "vanilla": "Piece of Heart"}
    spec["items"]["Piece of Heart"] = {"class": "normal"}
    spec["regions"][0]["area"] = "Test"
    census = [floor_heart()]
    definitions = [Definition(44, "freestanding", "Test", "Heart A", "Obj_Heart_Piece", "Heart A")]
    settings = Settings(shuffle=("Chest", "Freestanding"), songs="anywhere")
    restricted = freestanding.restrict_spec(spec, definitions)
    _, prepared = prepare(restricted, settings)
    effective, step = freestanding.seed_setup(prepared, settings, census, definitions, {})
    assert {"Ocarina of Time", "Prelude of Light"} <= set(effective.location_type_items["Freestanding"])
    (transform,) = step({"Heart A": "Prelude of Light"}).values()
    gyaml = byml.read(transform(byml.write(floor_tree())))["Actors"][0]["Gyaml"]
    assert gyaml == songs.pickup_name("Item_Melody_LightPrelude")


@pytest.mark.parametrize("item", [*OCARINAS, *SONG_ITEMS])
def test_a_seed_with_an_ocarina_or_song_on_a_floor_also_writes_that_actor(item, floor_ocarinas):
    """A8.2: the actor the floor writer names is one the seed's own steps create."""
    places = {"Floor": {"type": "BossHeart", "vanilla": "Heart Container", "rule": "True"}}
    spec_world = build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {"Heart Container": {}, item: {"type": "Song"} if item in SONG_ITEMS else {}},
            "regions": [{"name": "Root", "locations": places}],
        }
    )
    placements = {"Floor": item}
    actor = drops.floor_items(spec_world, Settings(songs="anywhere"), ACTORS)[item]
    if item in SONG_ITEMS:
        assert songs.moved_songs(placements, spec_world, ACTORS) == ["Floor"]  # songs.build runs in this seed
        assert actor in {songs.pickup_name(song) for song in getitem.SONG_MODELS}  # one of its new packs
    else:
        ocarina = ACTORS.actors[item]
        assert ocarina_pickup.needed(placements, spec_world, ACTORS) == [ocarina]  # ocarina_pickup.build runs
        assert actor == ocarina_pickup.PICKUPS[ocarina]  # its new pack
