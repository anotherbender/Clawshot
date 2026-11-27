"""Ocarinas and songs at Skulltulas and on floors, on the player's dump (ocarina-song-drops-everywhere 3.2, 2.5).

The real steps build both ocarinas' floor actors (``Obj_Clawshot_Ocarina_*``), a Skulltula drop for each new item
group (Fairy Ocarina, Ocarina of Time, a song) and a boss-heart and a free-standing heart swapped to each group's floor
actor; the common writer
writes them all, and every written file reads back with the expected contents and size entry.
"""

import pytest

from clawshot.census.scan import FREESTANDING, GOLD_SKULLTULA, HEART_CONTAINER, scan
from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.patch import drops, freestanding, getitem, ocarina_pickup, songs, tokens
from clawshot.patch.actor_packs import closure, resolve_node
from clawshot.patch.plan import Plan
from clawshot.patch.write import write

pytestmark = pytest.mark.dump

SONG = songs.pickup_name("Item_Melody_ZeldaLullaby")
GROUPS = {  # item group -> its Skulltula donor
    "fairy": ocarina_pickup.PICKUP,
    "time": ocarina_pickup.PICKUPS[getitem.TIME],
    "song": SONG,
}
FLOORS = {  # item group -> its floor actor
    "fairy": ocarina_pickup.PICKUP,
    "time": ocarina_pickup.PICKUPS[getitem.TIME],
    "song": SONG,
}
FAMILIES = {ocarina_pickup.PICKUP: "ocarina", ocarina_pickup.PICKUPS[getitem.TIME]: "ocarina", SONG: "song"}


@pytest.fixture(scope="module")
def written(romfs, tmp_path_factory):
    census = scan(romfs)
    skulltulas = sorted(loc.id for loc in census if loc.kind == GOLD_SKULLTULA and loc.has_save_flag and loc.files)
    hearts = sorted(
        (loc for loc in census if loc.kind == HEART_CONTAINER and loc.actor == drops.HEART and loc.has_save_flag),
        key=lambda loc: loc.id,
    )
    pieces = sorted(
        (loc for loc in census if loc.kind == FREESTANDING and freestanding._saved_heart(loc)), key=lambda loc: loc.id
    )
    fairy, song = (
        ocarina_pickup.build(romfs, ocarina_pickup.PICKUPS, with_static=False),
        songs.build(romfs, pickups=True),
    )
    generated = tokens.generated_donors(romfs, [(song.changes, song.new_files), (fairy.changes, fairy.new_files)])
    sources = dict(zip(skulltulas, GROUPS.values(), strict=False))
    delivery = tokens.build(romfs, sources, census, rewards=FAMILIES, generated=generated)
    boss = {loc.id: actor for loc, actor in zip(hearts, FLOORS.values(), strict=False)}
    floor = {loc.id: actor for loc, actor in zip(pieces, FLOORS.values(), strict=False)}
    floor_changes = (drops.changes(boss, census), freestanding.changes(floor, census))
    changes = (delivery.changes, song.changes, fairy.changes, *floor_changes)
    new_files = {**delivery.new_files, **song.new_files, **fairy.new_files}
    out = tmp_path_factory.mktemp("drops-everywhere")
    files = write(Plan([], [], []), romfs, out, extra_changes=changes, new_files=new_files)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path):
        return dictionaries.decompress(path, (out / "romfs" / path).read_bytes())

    def dump(path):
        return dictionaries.decompress(path, (romfs / path).read_bytes())

    return {
        "files": {info.path: info for info in files},
        "read": read,
        "dump": dump,
        "delivery": delivery,
        "boss": boss,
        "floor": floor,
        "census": {loc.id: loc for loc in census},
        "new_files": new_files,
    }


@pytest.mark.parametrize("ocarina", list(ocarina_pickup.PICKUPS))
def test_dump_ocarina_pickup_pack_and_rows_read_back(written, ocarina):
    read, pickup = written["read"], ocarina_pickup.PICKUPS[ocarina]
    path = getitem.pack_path(pickup)
    pack = sarc.read(read(path))
    assert pack == sarc.read(written["new_files"][path].data)
    components = closure([pack], pickup).components
    assert components["ActorNameRef"].endswith(f"/{ocarina}.engine__actor__ActorName.bgyml")
    # F1-a/F1-c: the arrow's pickup body, not Obj_Ocarina_Time's moat Box.
    assert not [name for name in pack if "/Box." in name or "Ptm_ObjDynamicLarge" in name]
    arrow = closure([sarc.read(read_dump(written, "Obj_Arrow_Fire"))], "Obj_Arrow_Fire").components
    assert components["PhysicsRef"] == arrow["PhysicsRef"]
    own_pouch = components["PouchContentRef"].removeprefix("?")
    native = sarc.read(read_dump(written, ocarina))
    parent_pouch = closure([native], ocarina).components["PouchContentRef"].removeprefix("?")
    assert pack[parent_pouch] == native[parent_pouch]
    builtin = "Component/PouchContentParam/Default.game__component__PouchContentParam.bgyml"
    inherited = resolve_node([native], parent_pouch, builtin=builtin)
    resolved = resolve_node([pack], own_pouch, builtin=builtin)
    assert byml.same(resolved.get("GetType"), inherited.get("GetType"))
    table = rstb.read(read(rstb.TABLE_PATH))
    assert table.get(path) == rstb.required_size(path, len(read(path)))
    for registry in tokens.REGISTRIES:
        rows = {row["__RowId"]: row for row in byml.read(read(registry))}
        assert list(rows) == sorted(rows, key=str.encode) and pickup in rows
        if registry == ocarina_pickup.POUCH_ACTOR_INFO:
            originals = {row["__RowId"]: row for row in byml.read(written["dump"](registry))}
            assert rows[pickup]["PouchGetType"] == originals[ocarina]["PouchGetType"]
            for native_ocarina in ocarina_pickup.PICKUPS:
                assert byml.write(rows[native_ocarina]) == byml.write(originals[native_ocarina])


def read_dump(written, actor):
    return written["dump"](getitem.pack_path(actor))


@pytest.mark.parametrize("group", GROUPS)
def test_dump_a_skulltula_drop_per_group_reads_back(written, group):
    read, delivery = written["read"], written["delivery"]
    donor = GROUPS[group]
    pickup = delivery.pickups[donor]
    (source,) = [hash_ for hash_, actor in delivery.drops.items() if actor == pickup]
    pack = sarc.read(read(tokens.pack_path(pickup)))
    assert tokens.TOKEN_GRAPH in pack
    if group == "fairy":
        components = closure([pack], pickup).components
        own_pouch = components["PouchContentRef"].removeprefix("?")
        pouch = resolve_node(
            [pack], own_pouch, builtin="Component/PouchContentParam/Default.game__component__PouchContentParam.bgyml"
        )
        native = sarc.read(read_dump(written, getitem.FAIRY))
        parent = closure([native], getitem.FAIRY).components["PouchContentRef"].removeprefix("?")
        inherited = resolve_node(
            [native], parent, builtin="Component/PouchContentParam/Default.game__component__PouchContentParam.bgyml"
        )
        assert byml.same(pouch.get("GetType"), inherited.get("GetType"))
        rows = {row["__RowId"]: row for row in byml.read(read(ocarina_pickup.POUCH_ACTOR_INFO))}
        assert rows[pickup]["PouchGetType"] == rows[getitem.FAIRY]["PouchGetType"]
    for path in written["census"][source].files:
        actors = byml.read(read(path))["Actors"]
        assert [a["Dynamic"][tokens.DROP] for a in actors if a.get("Hash") == source] == [pickup]
    for registry in tokens.REGISTRIES:
        assert pickup in {row["__RowId"] for row in byml.read(read(registry))}


@pytest.mark.parametrize("group", GROUPS)
@pytest.mark.parametrize("kind", ["boss", "floor"])
def test_dump_a_floor_heart_per_group_is_swapped_and_keeps_its_wiring(written, romfs, group, kind):
    read = written["read"]
    (heart,) = [hash_ for hash_, actor in written[kind].items() if actor == FLOORS[group]]
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    for path in written["census"][heart].files:
        before = byml.read(dictionaries.decompress(path, (romfs / path).read_bytes()))
        after = byml.read(read(path))
        (changed,) = [a for a in after["Actors"] if a.get("Hash") == heart]
        assert changed["Gyaml"] == FLOORS[group]
        original = next(a for a in before["Actors"] if a.get("Hash") == heart)
        assert float(changed["Translate"][1]) == pytest.approx(float(original["Translate"][1]) + drops.FLOOR_LIFT)
        changed["Gyaml"], changed["Translate"] = original["Gyaml"], original["Translate"]
        if kind == "floor":
            # Only Gyaml changes on its copies; a Skulltula source in the same file has this test's own token drop.
            for tree in (before, after):
                tree["Actors"] = [a for a in tree["Actors"] if a.get("Hash") not in written["delivery"].drops]
            assert byml.same(after, before), byml.difference(before, after)
        else:
            assert byml.same(after["AiGroups"], before["AiGroups"])
            for key in ("SimultaneousGroups", "FarDeleteGroups"):
                assert byml.same(after.get(key), before.get(key))
