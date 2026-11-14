"""Native get-window text at both runtime-selected Hookshot tiers; no game launch."""

import pytest

from clawshot.formats import msbt, sarc, zsdic
from clawshot.generate import Seed, Settings, prepare
from clawshot.patch import custom_step
from clawshot.patch.items import load as item_actors
from clawshot.patch.plan import Links
from clawshot.patch.text import POUCH_TEXT, archive_path, text_key
from clawshot.world.load import load_spec


@pytest.mark.dump
def test_possessive_get_text_covers_both_runtime_selected_hookshot_tiers(romfs):
    settings, world = prepare(load_spec(), Settings())
    seed = Seed(world, 1, settings, {"early chest": "Progressive Hookshot"}, ["early chest"], [])
    custom = custom_step(romfs, seed, Links({}, {}, []), item_actors(), {}, possessive_text=True)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    path = archive_path("USen")
    raw = dictionaries.decompress(path, (romfs / path).read_bytes())
    changed = custom.changes[path](raw) if path in custom.changes else raw
    pouch = msbt.read(sarc.read(changed)[POUCH_TEXT])
    for actor, name in (("Item_Hookshot", "Hookshot"), ("Item_Longshot", "Longshot")):
        pack = f"Pack/Actor/{actor}.pack.zs"
        key = text_key(sarc.read(dictionaries.decompress(pack, (romfs / pack).read_bytes())), actor)
        assert f"your {name}" in msbt.plain(pouch.messages[key + "_GetMessage"])
