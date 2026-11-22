import pytest

from clawshot.formats import byml, rstb, sarc, zsdic


@pytest.fixture(scope="module")
def table_bytes(romfs):
    dicts = zsdic.Dictionaries.from_romfs(romfs)
    return dicts, dicts.decompress(rstb.TABLE_PATH, (romfs / rstb.TABLE_PATH).read_bytes())


@pytest.mark.dump
def test_dump_size_table_round_trips(table_bytes):
    _, data = table_bytes
    table = rstb.read(data)
    print(f"{len(table.hashes)} hash entries, {len(table.names)} name entries")
    assert rstb.write(table) == data


@pytest.mark.dump
@pytest.mark.parametrize(
    "pattern",
    [
        "Banc/*/*.bcett.byml.zs",
        "Event/EventFlow/*.bfevfl.zs",
        "Mals/*.sarc.zs",
        "Pack/Actor/*.pack.zs",
        "GameData/GameDataList.Product.110.byml.zs",
        "RSDB/ActorInfo.Product.111.rstbl.byml.zs",
        "RSDB/EventSetting.Product.111.rstbl.byml.zs",
        "RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml.zs",
        "RSDB/GameActorInfo.Product.111.rstbl.byml.zs",
        "RSDB/PouchActorInfo.Product.111.rstbl.byml.zs",
    ],
)
def test_dump_size_formula_fits_every_file(romfs, table_bytes, pattern):
    dicts, data = table_bytes
    table = rstb.read(data)
    paths = sorted(p.relative_to(romfs).as_posix() for p in romfs.glob(pattern))
    assert paths
    misfits = []
    for path in paths:
        size = len(dicts.decompress(path, (romfs / path).read_bytes()))
        entry, needed = table.get(path), rstb.required_size(path, size)
        if entry != needed:
            misfits.append((path, size, entry, needed))
    print(f"{pattern}: {len(paths) - len(misfits)} of {len(paths)} fit")
    assert misfits == []


@pytest.mark.dump
def test_dump_pack_member_formulas_fit_every_member_of_their_type(romfs, table_bytes):
    """Round 15's member formulas: every unique actor parameter and pouch component in every actor pack."""
    dicts, data = table_bytes
    table = rstb.read(data)
    members: dict[str, bytes] = {}
    for path in sorted(romfs.glob("Pack/Actor/*.pack.zs")):
        relative = path.relative_to(romfs).as_posix()
        for name, content in sarc.read(dicts.decompress(relative, path.read_bytes())).items():
            if name.endswith((rstb.ACTOR_PARAM, ".game__component__PouchContentParam.bgyml")):
                assert members.setdefault(name, content) == content, f"{name} differs between packs"
    misfits, counts = [], {rstb.ACTOR_PARAM: 0, "PouchContentParam": 0}
    for name, content in sorted(members.items()):
        if name.endswith(rstb.ACTOR_PARAM):
            counts[rstb.ACTOR_PARAM] += 1
            needed = rstb.required_size(name, len(content), len(byml.read(content).get("Components", {})))
        else:
            counts["PouchContentParam"] += 1
            needed = rstb.required_size(name, len(content))
        if table.get(name) != needed:
            misfits.append((name, len(content), table.get(name), needed))
    print(f"{counts}: {len(members) - len(misfits)} of {len(members)} fit")
    assert counts[rstb.ACTOR_PARAM] > 8000 and counts["PouchContentParam"] > 100
    assert misfits == []


@pytest.mark.dump
def test_dump_animation_parameter_formula_fits_every_member(romfs, table_bytes):
    """Every unique AnimationParam in every actor pack: 5096 + 88 per own AnimationResources entry (section 50)."""
    dicts, data = table_bytes
    table = rstb.read(data)
    members: dict[str, bytes] = {}
    for path in sorted(romfs.glob("Pack/Actor/*.pack.zs")):
        relative = path.relative_to(romfs).as_posix()
        for name, content in sarc.read(dicts.decompress(relative, path.read_bytes())).items():
            if name.endswith(rstb.ANIMATION_PARAM):
                assert members.setdefault(name, content) == content, f"{name} differs between packs"
    misfits = []
    for name, content in sorted(members.items()):
        resources = len(byml.read(content).get("AnimationResources", []))
        needed = rstb.required_size(name, len(content), resources=resources)
        if table.get(name) != needed:
            misfits.append((name, len(content), resources, table.get(name), needed))
    print(f"AnimationParam: {len(members) - len(misfits)} of {len(members)} fit")
    assert len(members) > 500
    assert misfits == []
