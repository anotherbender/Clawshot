"""Vfx3 effect binaries (``BFFH``, the ``PtclBin`` of an effect file): list effects and emitters, clone an effect
under a new name with a subset of its emitters, and check the result has no stray or shared pointers.

Every blob here is built in code (hard rule 1)."""

import struct

import pytest
from synthetic_effects import build_bffh

from clawshot.formats import vfx


def test_lists_effects_and_emitters():
    blob = build_bffh()
    assert vfx.effect_names(blob) == ["Fx_A", "Fx_B"]
    assert vfx.emitters(blob, "Fx_A") == ["Em0", "Em1", "Em2"]
    assert vfx.emitters(blob, "Fx_B") == ["Em0", "Em3"]
    vfx.check(blob, {})


def test_clone_keeps_only_the_named_emitters_under_a_new_name():
    blob = build_bffh()
    out = vfx.clone(blob, "Fx_A", "Fx_A_Copy", ["Em2", "Em0"])
    assert vfx.effect_names(out) == ["Fx_A", "Fx_B", "Fx_A_Copy"]
    assert vfx.emitters(out, "Fx_A_Copy") == ["Em0", "Em2"]  # native order
    assert vfx.emitters(out, "Fx_A") == ["Em0", "Em1", "Em2"]
    assert vfx.emitters(out, "Fx_B") == ["Em0", "Em3"]
    assert struct.unpack_from("<I", out, 8)[0] == len(out) and len(out) % 0x10 == 0
    pool_size = struct.unpack_from("<I", out, 0xA8 + 0x28 + 8)[0]
    pool0 = struct.unpack_from("<Q", out, 0xA8 + 0x28 + 0x10)[0]
    assert pool0 + pool_size == len(out)  # the string pool section grows to the end
    vfx.check(out, {"Fx_A_Copy": "Fx_A"})


def test_clone_leaves_every_original_effect_unchanged():
    blob = build_bffh()
    out = vfx.clone(blob, "Fx_A", "Fx_A_Copy", ["Em1"])
    for name in ("Fx_A", "Fx_B"):
        assert vfx.effect_bytes(out, name) == vfx.effect_bytes(blob, name)
    assert out[0x10000 : len(blob)] == blob[0x10000:]  # regions and pool not moved


def test_clone_copies_and_relocates_the_data_region():
    blob = build_bffh()
    out = vfx.clone(blob, "Fx_A", "Fx_A_Copy", ["Em1"])
    (r0, r1), (c0, c1) = vfx.region(out, "Fx_A"), vfx.region(out, "Fx_A_Copy")
    assert c0 >= len(blob) and (c0 - r0) % 0x1000 == 0 and c1 - c0 == r1 - r0
    delta = c0 - r0
    assert sorted(struct.unpack_from("<3Q", out, c0)) == [v + delta for v in struct.unpack_from("<3Q", out, r0)]
    for k in range(8 * 3, r1 - r0, 8):  # after the emitter list, which the copy reorders
        old, new = struct.unpack_from("<Q", out, r0 + k)[0], struct.unpack_from("<Q", out, c0 + k)[0]
        assert new == (old + delta if r0 <= old < r1 else old)


def test_clones_chain():
    blob = build_bffh()
    one = vfx.clone(blob, "Fx_A", "C1", ["Em0"])
    two = vfx.clone(one, "Fx_A", "C2", ["Em1", "Em2"])
    three = vfx.clone(two, "Fx_B", "C3", ["Em3"])
    assert vfx.effect_names(three) == ["Fx_A", "Fx_B", "C1", "C2", "C3"]
    assert [vfx.emitters(three, n) for n in ("C1", "C2", "C3")] == [["Em0"], ["Em1", "Em2"], ["Em3"]]
    vfx.check(three, {"C1": "Fx_A", "C2": "Fx_A", "C3": "Fx_B"})
    for name in ("Fx_A", "Fx_B"):
        assert vfx.effect_bytes(three, name) == vfx.effect_bytes(blob, name)


def test_check_finds_a_shared_object_and_a_stray_pointer():
    out = bytearray(vfx.clone(build_bffh(), "Fx_A", "Copy", ["Em0", "Em1"]))
    c0, _ = vfx.region(bytes(out), "Copy")
    a0, _ = vfx.region(bytes(out), "Fx_A")
    shared = bytearray(out)
    struct.pack_into("<Q", shared, c0, struct.unpack_from("<Q", shared, a0)[0])  # Copy's emitter 0 = Fx_A's
    with pytest.raises(vfx.VfxError, match="referenced twice"):
        vfx.check(bytes(shared), {"Copy": "Fx_A"})
    stray = bytearray(out)
    struct.pack_into("<Q", stray, c0 + 8 * 3 + 0x40 + 8, a0 + 0x20)  # an emitter's vector into Fx_A's region
    with pytest.raises(vfx.VfxError, match=f"0x{c0 + 8 * 3 + 0x48:x}"):
        vfx.check(bytes(stray), {"Copy": "Fx_A"})


def test_errors_name_what_is_missing():
    blob = build_bffh()
    with pytest.raises(vfx.VfxError, match="no effect 'Fx_Z'"):
        vfx.clone(blob, "Fx_Z", "New", ["Em0"])
    with pytest.raises(vfx.VfxError, match="Fx_A has no emitter 'Em9'"):
        vfx.clone(blob, "Fx_A", "New", ["Em9"])
    with pytest.raises(vfx.VfxError, match="'Fx_B' already exists"):
        vfx.clone(blob, "Fx_A", "Fx_B", ["Em0"])
    with pytest.raises(vfx.VfxError, match="BFFH"):
        vfx.effect_names(b"XXXX" + blob[4:])
