"""BYML version 5 (the effect files' outer format): the binary node 0xA2 and a root placed after the blob.

Every document here is built in code (hard rule 1)."""

import struct

import pytest

from clawshot.formats import byml
from clawshot.formats.byml import U64, Binary


def effect_like() -> dict:
    """The shape of an effect file: names, an aligned blob, then an array of dicts (one with a 64-bit value)."""
    return {
        "Esets": ["Alpha", "Beta"],
        "PtclBin": Binary(b"BFFH" + bytes(range(256)) * 3, 0x1000),
        "Textures": [{"Name": "tex0", "Hash": U64(0x1122334455667788)}, {"Name": "tex1", "Hash": U64(7)}],
    }


def test_v5_round_trip_keeps_version_tree_and_bytes():
    data = byml.write(effect_like(), version=5)
    assert struct.unpack_from("<H", data, 2)[0] == 5
    document = byml.load(data)
    assert document.version == 5
    assert byml.difference(effect_like(), document.root) is None
    assert byml.dump(document) == data


def test_binary_node_sits_right_before_its_aligned_data():
    tree = effect_like()
    data = byml.write(tree, version=5)
    root = struct.unpack_from("<I", data, 12)[0]
    entries = {}
    for i in range(3):
        kv, raw = struct.unpack_from("<II", data, root + 4 + 8 * i)
        entries[kv >> 24] = raw
    node = entries[0xA2]
    assert node % 8 == 0
    size, alignment = struct.unpack_from("<II", data, node)
    assert (size, alignment) == (len(tree["PtclBin"].data), 0x1000)
    start = node + 8
    assert start % 0x1000 == 0
    assert data[start : start + size] == tree["PtclBin"].data
    values_end = data.index(struct.pack("<Q", 7)) + 8  # the last 8-byte value
    assert data[values_end:node] == bytes(node - values_end)  # zero padding up to the alignment


def test_root_and_containers_come_after_the_blob():
    tree = effect_like()
    data = byml.write(tree, version=5)
    keys, strings, root = struct.unpack_from("<III", data, 4)
    blob_end = data.index(tree["PtclBin"].data) + len(tree["PtclBin"].data)
    assert keys < strings < blob_end <= root
    assert root == (blob_end + 3) & ~3
    assert data[blob_end:root] == bytes(root - blob_end)


def test_reader_follows_a_root_placed_after_the_blob():
    data = byml.write(effect_like(), version=5)
    assert struct.unpack_from("<I", data, 12)[0] > data.index(b"BFFH")
    assert byml.read(data)["Esets"] == ["Alpha", "Beta"]


def test_binary_keeps_its_alignment_as_a_distinct_value():
    a, b = Binary(b"xy", 0x1000), Binary(b"xy", 0x10)
    assert byml.node_type(a) == 0xA2
    assert byml.difference({"b": a}, {"b": b}) is not None
    assert byml.same({"b": a}, {"b": Binary(b"xy", 0x1000)})
    back = byml.read(byml.write({"b": b}, version=5))["b"]
    assert isinstance(back, Binary) and back == b


def test_a_grown_blob_moves_the_containers_after_it():
    tree = effect_like()
    small = byml.write(tree, version=5)
    tree["PtclBin"] = Binary(tree["PtclBin"].data + bytes(0x123), 0x1000)
    big = byml.write(tree, version=5)
    assert struct.unpack_from("<I", big, 12)[0] > struct.unpack_from("<I", small, 12)[0]
    assert byml.difference(tree, byml.read(big)) is None


def test_version_7_stays_the_default():
    data = byml.write({"a": 1})
    assert struct.unpack_from("<H", data, 2)[0] == 7
    assert byml.load(data).version == 7


def test_unsupported_version_is_named():
    data = bytearray(byml.write({"a": 1}))
    for version in (4, 6, 8):
        data[2] = version
        with pytest.raises(byml.BymlError, match=f"version {version}"):
            byml.read(bytes(data))
    with pytest.raises(byml.BymlError, match="version 6"):
        byml.write({"a": 1}, version=6)


def test_unsupported_node_type_names_offset_and_type():
    data = bytearray(byml.write({"a": 1}, version=5))
    root = struct.unpack_from("<I", data, 12)[0]
    data[root + 4 + 3] = 0xA3
    with pytest.raises(byml.BymlError, match=rf"0xa3.*0x{root:x}"):
        byml.read(bytes(data))


def test_binary_alignment_must_be_a_power_of_two():
    with pytest.raises(byml.BymlError, match="alignment"):
        Binary(b"x", 3)
