"""ELink tables (XLNK version 36): decode, re-encode, add a user, set call parameters, make a play-all container.

Every file here is built in code (hard rule 1): a minimal XLNK 36 table with three users."""

import struct
import zlib

import pytest
from synthetic_effects import ASSET_PARAMS, CONDITIONS, TRIGGERS, build_table

from clawshot.formats import elink


def snapshot(table: elink.Elink, skip: str | None = None) -> dict:
    """Every user's calls with their decoded parameters (or container records)."""
    out = {}
    for name in table.user_names():
        if name == skip:
            continue
        calls = []
        for call in table.calls(name):
            entry = (call.key, call.asset, call.flag, call.duration, call.parent, call.guid, call.condition)
            detail = table.container(name, call.key) if call.is_container else table.call_params(name, call.key)
            calls.append((entry, detail))
        out[name] = (calls, table.trigger_table(name))
    return out


@pytest.fixture
def data() -> bytes:
    return build_table()


def test_decode_reads_users_calls_and_parameters(data):
    table = elink.decode(data)
    assert sorted(table.user_names()) == ["Obj_Donor", "Obj_Other", "Obj_Third"]
    assert table.asset_params == ASSET_PARAMS
    assert [c.key for c in table.calls("Obj_Donor")] == ["Wait", "Get"]
    assert table.call_params("Obj_Donor", "Wait") == {"AssetName": "Wait", "Bone": "Root", "BitFlag": 0x05000004}
    assert table.call_params("Obj_Donor", "Get")["Scale"] == 1.0  # direct value 1
    assert table.call_params("Obj_Donor", "Get")["RuntimeAssetName"] == "Fx_A"
    assert table.local_properties("Obj_Donor") == ["LocalProp"]
    assert table.trigger_table("Obj_Donor").rstrip(b"\0") == TRIGGERS  # the user's padding follows it
    assert table.direct_values() == pytest.approx([0.5, 1.0, -0.21, 1.0])
    assert table.conditions == CONDITIONS


def test_encode_is_byte_identical(data):
    assert elink.decode(data).encode() == data


def test_add_user_copy_inserts_in_hash_order(data):
    table = elink.decode(data)
    before = snapshot(table)
    table.add_user_copy("Obj_Donor", "Clawshot_New")
    out = table.encode()
    again = elink.decode(out)
    assert snapshot(again, skip="Clawshot_New") == before
    hashes = struct.unpack_from("<4I", out, 0x60)
    assert list(hashes) == sorted(hashes) and zlib.crc32(b"Clawshot_New") in hashes
    assert struct.unpack_from("<I", out, 0x48)[0] == 4
    assert struct.unpack_from("<I", out, 4)[0] == len(out) and len(out) % 8 == 0
    copied = snapshot(again)["Clawshot_New"]
    assert copied == before["Obj_Donor"]  # the bytes are self-relative: the copy decodes as its source
    assert again.user_data("Clawshot_New").rstrip(b"\0") == table.user_data("Obj_Donor").rstrip(b"\0")


def test_set_call_params_appends_values_records_and_names(data):
    table = elink.decode(data)
    before = snapshot(table)
    n_direct = len(table.direct_values())
    table.set_call_params("Obj_Donor", "Wait", {"RuntimeAssetName": "Fx_New", "Scale": 0.3, "Bone": "Root"})
    again = elink.decode(table.encode())
    params = again.call_params("Obj_Donor", "Wait")
    assert params["RuntimeAssetName"] == "Fx_New"
    assert params["Bone"] == "Root"
    assert params["Scale"] == pytest.approx(0.3)
    assert params["AssetName"] == "Wait" and params["BitFlag"] == 0x05000004  # the rest of the record is kept
    values = again.direct_values()
    assert len(values) == n_direct + 2  # one float, padded to 8 bytes with 1.0
    assert values[-1] == 1.0
    names = again.names
    assert names.count(b"\0Root\0") + names.startswith(b"Root\0") == 1  # an existing name is reused
    assert b"\0Fx_New\0" in names
    after = snapshot(again)
    assert after["Obj_Other"] == before["Obj_Other"]  # shares the old record, which stays
    assert after["Obj_Third"] == before["Obj_Third"]
    assert after["Obj_Donor"][0][1] == before["Obj_Donor"][0][1]  # the other call unchanged


def test_set_call_params_overrides_an_existing_value(data):
    table = elink.decode(data)
    table.set_call_params("Obj_Donor", "Get", {"PositionY": 0.0, "Bone": "Root", "Scale": 2.5})
    params = elink.decode(table.encode()).call_params("Obj_Donor", "Get")
    assert params["Scale"] == 2.5 and params["PositionY"] == 0.0 and params["Bone"] == "Root"


def test_make_container_appends_children(data):
    table = elink.decode(data)
    before = snapshot(table)
    old_trigger_pos = struct.unpack_from("<Q", table.user_data("Obj_Donor"), 0x30)[0]
    children = [
        {"RuntimeAssetName": "Fx_A", "PositionX": 0.12, "Red": 2.0},
        {"RuntimeAssetName": "Fx_B", "PositionX": -0.12, "Red": 3.0},
        {"RuntimeAssetName": "Fx_B", "PositionX": 0.0},
    ]
    table.make_container("Obj_Donor", "Wait", children, condition=0x30)
    again = elink.decode(table.encode())
    calls = again.calls("Obj_Donor")
    assert [c.key for c in calls] == ["Wait", "Get", "Wait_00", "Wait_01", "Wait_02"]
    wait = calls[0]
    assert wait.is_container and wait.asset == -1 and wait.flag == 1
    assert again.container("Obj_Donor", "Wait") == (3, 2, 4)  # play all, children 2..4
    assert [c.asset for c in calls] == [-1, 0, 1, 2, 3]  # renumbered in call order
    for i, child in enumerate(calls[2:]):
        assert child.parent == 0 and child.condition == 0x30 and child.flag == 0
        assert child.guid == zlib.crc32(f"Obj_Donor/Wait_{i:02d}".encode())
        params = again.call_params("Obj_Donor", child.key)
        assert params["AssetName"] == child.key
        assert params["Bone"] == "Root" and params["BitFlag"] == 0x05000004  # copied from the call's record
        assert params["RuntimeAssetName"] == children[i]["RuntimeAssetName"]
        assert params["PositionX"] == pytest.approx(children[i]["PositionX"])
    assert "Red" not in again.call_params("Obj_Donor", "Wait_02")
    assert again.call_params("Obj_Donor", "Get") == before["Obj_Donor"][0][1][1]
    assert again.trigger_table("Obj_Donor").rstrip(b"\0") == TRIGGERS  # entries still name the same calls
    new_pos = struct.unpack_from("<Q", again.user_data("Obj_Donor"), 0x30)[0]
    assert new_pos == old_trigger_pos + 3 * 0x30 + 16 + 8  # three calls, one container record, ids 4 -> 12 bytes
    after = snapshot(again)
    assert after["Obj_Other"] == before["Obj_Other"] and after["Obj_Third"] == before["Obj_Third"]


def test_two_containers_in_one_user(data):
    table = elink.decode(data)
    table.make_container("Obj_Donor", "Wait", [{"PositionX": 1.0}], condition=0x30)
    table.make_container("Obj_Donor", "Get", [{"PositionX": 2.0}, {"PositionX": 3.0}], condition=0x38)
    again = elink.decode(table.encode())
    assert again.container("Obj_Donor", "Wait") == (3, 2, 2)
    assert again.container("Obj_Donor", "Get") == (3, 3, 4)
    assert [c.asset for c in again.calls("Obj_Donor")] == [-1, -1, 0, 1, 2]
    assert again.call_params("Obj_Donor", "Get_01")["PositionX"] == 3.0


def test_errors_name_what_is_wrong(data):
    bad = bytearray(data)
    struct.pack_into("<I", bad, 8, 35)
    with pytest.raises(elink.ElinkError, match="version 35"):
        elink.decode(bytes(bad))
    with pytest.raises(elink.ElinkError, match="magic"):
        elink.decode(b"XLNQ" + data[4:])
    table = elink.decode(data)
    with pytest.raises(elink.ElinkError, match="Obj_Other.*already"):
        table.add_user_copy("Obj_Donor", "Obj_Other")
    with pytest.raises(elink.ElinkError, match="no user 'Obj_Missing'"):
        table.add_user_copy("Obj_Missing", "Clawshot_X")
    with pytest.raises(elink.ElinkError, match="Obj_Donor.*no call 'Nope'"):
        table.set_call_params("Obj_Donor", "Nope", {"Scale": 1.0})
    with pytest.raises(elink.ElinkError, match="unknown asset parameter 'Wobble'"):
        table.set_call_params("Obj_Donor", "Wait", {"Wobble": 1.0})
    table.make_container("Obj_Donor", "Wait", [{"Scale": 1.0}], condition=0)
    with pytest.raises(elink.ElinkError, match="Obj_Donor/Wait is a container"):
        table.make_container("Obj_Donor", "Wait", [{"Scale": 1.0}], condition=0)
