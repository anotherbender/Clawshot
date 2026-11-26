"""The always-loaded effect file ``static`` takes the three song-effect clones (S5) and keeps every native effect."""

import pytest

from clawshot.formats import byml, vfx, zsdic

STATIC = "Effect/static.Nin_Ounce_NVN2.vsetb.byml.zs"
SOURCE = "Ply_ChargeLv3_Loop_02"
CLONES = {
    "Clawshot_ChargeSpark": ["Spark_Small"],
    "Clawshot_ChargeAura": ["Glow_L", "Glow_Long_00"],
    "Clawshot_ChargeLight": ["LineLight"],
}


@pytest.mark.dump
def test_dump_static_takes_three_clones(romfs):
    data = zsdic.Dictionaries.from_romfs(romfs).decompress(STATIC, (romfs / STATIC).read_bytes())
    document = byml.load(data)
    blob = document.root["PtclBin"].data
    native = vfx.effect_names(blob)
    assert len(native) == 569
    assert sorted(vfx.emitters(blob, SOURCE)) == sorted(e for keep in CLONES.values() for e in keep)
    vfx.check(blob, {})
    out = blob
    for name, keep in CLONES.items():
        out = vfx.clone(out, SOURCE, name, keep)
    vfx.check(out, dict.fromkeys(CLONES, SOURCE))
    document.root["PtclBin"] = byml.Binary(out, document.root["PtclBin"].alignment)
    written = byml.dump(document)
    again = byml.read(written)
    assert byml.difference(document.root, again) is None
    result = again["PtclBin"].data
    assert vfx.effect_names(result) == native + list(CLONES)
    for name, keep in CLONES.items():
        assert vfx.emitters(result, name) == keep
    changed = [name for name in native if vfx.effect_bytes(result, name) != vfx.effect_bytes(blob, name)]
    assert changed == []
    assert again["Esets"] == byml.read(data)["Esets"]  # the new names need not be listed (record)
