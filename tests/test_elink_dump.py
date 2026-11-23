"""The game's two ELink tables decode, re-encode byte for byte, and keep every native user through the song edits."""

import pytest

from clawshot.formats import elink, zsdic

TABLES = ("ELink2/elink2.Product.100.belnk.zs", "ELink2/elink2.Product.110.belnk.zs")


def load(romfs, rel: str) -> bytes:
    return zsdic.Dictionaries.from_romfs(romfs).decompress(rel, (romfs / rel).read_bytes())


def decoded_users(table: elink.Elink, names: list[str]) -> dict:
    out = {}
    for name in names:
        calls = []
        for k, call in enumerate(table.calls(name)):
            detail = table.container(name, k) if call.is_container else table.call_params(name, k)
            calls.append((call.key, call.asset, call.flag, call.parent, call.guid, call.condition, detail))
        out[name] = (calls, table.trigger_table(name), table.local_properties(name))
    return out


@pytest.mark.dump
@pytest.mark.parametrize("rel", TABLES)
def test_dump_table_round_trips(romfs, rel):
    data = load(romfs, rel)
    table = elink.decode(data)
    assert len(table.users) > 1000
    assert table.encode() == data


@pytest.mark.dump
def test_dump_edits_keep_every_native_user(romfs):
    """A user copied from Obj_Heart_Container, call parameters set, and a call turned into a container: every native
    user decodes as before (calls, parameters, containers, triggers, local properties)."""
    data = load(romfs, TABLES[1])
    table = elink.decode(data)
    native = [n for n in table.user_names() if not n.startswith("#")]
    assert len(native) == len(table.users), "every native user's name is in the name table"
    before = decoded_users(table, native)
    table.add_user_copy("Obj_Heart_Container", "Clawshot_Test_A")
    table.add_user_copy("Obj_Heart_Container", "Clawshot_Test_B")
    table.set_call_params("Clawshot_Test_A", "Wait", {"RuntimeAssetName": "Ply_ChargeLv3_Loop_02", "Scale": 0.3})
    table.set_call_params("Clawshot_Test_B", "GetDemo", {"Bone": "Root", "PositionY": 0.0})
    table.make_container("Clawshot_Test_A", "GetDemo", [{"PositionX": 0.12}, {"PositionX": -0.12}], condition=0x4FC0)
    again = elink.decode(table.encode())
    assert decoded_users(again, native) == before
    assert again.call_params("Clawshot_Test_A", "Wait")["RuntimeAssetName"] == "Ply_ChargeLv3_Loop_02"
    assert again.call_params("Clawshot_Test_B", "GetDemo")["Bone"] == "Root"
    assert again.container("Clawshot_Test_A", "GetDemo")[0] == 3
    heart = before["Obj_Heart_Container"][0]
    assert [c.key for c in again.calls("Clawshot_Test_A")][: len(heart)] == [c[0] for c in heart]
