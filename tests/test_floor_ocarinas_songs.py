"""Ocarinas and songs on BossHeart and Freestanding floors (ocarina-song-drops-everywhere 1.4, 2.4, A8.1, A8.2).

Synthetic worlds, census rows and placement trees built in code: the floor palette is built from settings and the
world, each item maps to its world actor, and the floor writers swap a saved heart's ``Gyaml`` to it.
"""

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.scan import Location
from clawshot.formats import byml
from clawshot.formats.byml import F32, U64
from clawshot.generate import FillError, Settings, from_placements, prepare
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


def test_the_ocarinas_floor_actors_are_the_generated_ones():
    assert drops.OCARINA_PICKUPS == OCARINAS
    assert "Obj_Ocarina_Time" not in drops.PICKUPS  # its moat Box body is an invisible box on a floor (F1-c)


@pytest.mark.parametrize("kind", ["BossHeart", "Freestanding"])
def test_each_floor_kind_keeps_its_admitted_ocarinas(kind):
    found = drops.floor_items(world(*OCARINAS, *SONG_ITEMS), Settings(songs="anywhere"), ACTORS, kind=kind)
    ocarinas = OCARINAS if kind == "BossHeart" else {"Ocarina of Time": OCARINAS["Ocarina of Time"]}
    assert found == {**drops.NATIVE_ITEMS, **ocarinas, **SONG_PICKUPS}


def test_a_gated_ocarina_stays_off_floors(monkeypatch):
    monkeypatch.setattr(ocarina_pickup, "KINDS", {ocarina_pickup.FAIRY: (), ocarina_pickup.TIME: ()})
    found = drops.floor_items(world(*OCARINAS, *SONG_ITEMS), Settings(songs="anywhere"), ACTORS, kind="BossHeart")
    assert found == {**drops.NATIVE_ITEMS, **SONG_PICKUPS}


@pytest.mark.parametrize("kind", ["BossHeart", "Freestanding"])
@pytest.mark.parametrize("mode", ["song", "anywhere"])
def test_the_floor_palette_takes_admitted_ocarinas_and_songs_only_anywhere(mode, kind):
    found = drops.floor_items(world(*OCARINAS, *SONG_ITEMS), Settings(songs=mode), ACTORS, kind=kind)
    ocarinas = OCARINAS if kind == "BossHeart" else {"Ocarina of Time": OCARINAS["Ocarina of Time"]}
    expected = {**drops.NATIVE_ITEMS, **ocarinas, **(SONG_PICKUPS if mode == "anywhere" else {})}
    assert found == expected


@pytest.mark.parametrize("kind", ["BossHeart", "Freestanding"])
def test_items_outside_the_world_stay_out_of_the_palette(kind):
    assert drops.floor_items(world(), Settings(songs="anywhere"), ACTORS, kind=kind) == drops.NATIVE_ITEMS


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
        if writer is freestanding and pickup == OCARINAS["Fairy Ocarina"]:
            with pytest.raises(PatchError, match="not a supported floor pickup"):
                writer.changes({loc.id: pickup}, [loc])
            continue
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
    (transform,) = freestanding.changes({44: OCARINAS["Ocarina of Time"]}, [floor_heart()]).values()
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
def test_boss_heart_setup_holds_the_settings_palette_and_writes_its_actor(mode):
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


@pytest.mark.parametrize("item", [*OCARINAS, *SONG_ITEMS])
def test_freestanding_setup_refuses_fairy_and_writes_time_and_every_song(item):
    spec, census, definitions = boss_setup(item)
    spec["locations"]["Heart A"] = {"type": "Collectable", "vanilla": "Piece of Heart"}
    spec["items"]["Piece of Heart"] = {"class": "normal"}
    spec["regions"][0]["area"] = "Test"
    census = [floor_heart()]
    definitions = [Definition(44, "freestanding", "Test", "Heart A", "Obj_Heart_Piece", "Heart A")]
    settings = Settings(
        shuffle=("Chest", "Freestanding"),
        songs="anywhere",
        location_type_items={"Freestanding": (item, "Piece of Heart")},
    )
    restricted = freestanding.restrict_spec(spec, definitions)
    _, prepared = prepare(restricted, settings)
    effective, step = freestanding.seed_setup(prepared, settings, census, definitions, {})
    if item == "Fairy Ocarina":
        assert item not in effective.location_type_items["Freestanding"]
        with pytest.raises(PatchError, match="no floor pickup"):
            step({"Heart A": item})
        with pytest.raises(FillError, match="may not hold"):
            from_placements(restricted, 1, effective, {"Heart A": item, "Chest": "Piece of Heart"})
        safe = from_placements(restricted, 1, effective, {"Heart A": "Piece of Heart", "Chest": item})
        assert safe.placements["Chest"] == item
    else:
        assert item in effective.location_type_items["Freestanding"]
        (transform,) = step({"Heart A": item}).values()
        gyaml = byml.read(transform(byml.write(floor_tree())))["Actors"][0]["Gyaml"]
        expected = OCARINAS[item] if item in OCARINAS else SONG_PICKUPS[item]
        assert gyaml == expected


@pytest.mark.parametrize("item", [*OCARINAS, *SONG_ITEMS])
@pytest.mark.parametrize("kind", ["BossHeart", "Freestanding"])
def test_each_admitted_floor_item_is_written_with_source_identity_intact(item, kind):
    pickups = drops.floor_items(world(item), Settings(songs="anywhere"), ACTORS, kind=kind)
    writer, loc, tree = (
        (drops, boss_heart(), boss_tree()) if kind == "BossHeart" else (freestanding, floor_heart(), floor_tree())
    )
    if item == "Fairy Ocarina" and kind == "Freestanding":
        assert item not in pickups
        with pytest.raises(PatchError, match="not a supported floor pickup"):
            writer.changes({loc.id: OCARINAS[item]}, [loc])
        return
    (transform,) = writer.changes({loc.id: pickups[item]}, [loc]).values()
    after = byml.read(transform(byml.write(tree)))
    actor = after["Actors"][0]
    assert actor["Gyaml"] == pickups[item]
    assert actor["Hash"] == loc.id
    actor["Gyaml"], actor["Translate"] = tree["Actors"][0]["Gyaml"], tree["Actors"][0]["Translate"]
    assert byml.same(after, tree)
