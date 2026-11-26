"""Vfx3 effect binaries: the ``BFFH`` blob in an effect file's ``PtclBin`` node (``Effect/*.vsetb.byml``, read with
:mod:`clawshot.formats.byml` version 5). Lists effects and emitters and clones an effect under a new name with a
subset of its emitters. Written from the layout in plans/song-get-effects.md, decoded from the files themselves.

Layout (pointers are u64 offsets from the blob start):

- header: ``BFFH``, +0x08 u32 blob size, +0x18 u32 section count; from +0xA8 one 0x28-byte ``BFSI`` record per
  section: +0x08 u32 size, +0x10 u64 offset, +0x18 the name (``Default``, ``StringPool``).
- the root object at the start of ``Default``: +0x30 the effect table, +0x38 u32 effect count, +0x3C u32 entry size.
- an effect entry (0x68 bytes): +0x00 its name (in the string pool), +0x08 its emitter pointer list ``{u64 pointer,
  u32 count, u32 element size}``, further ``{pointer, count, size}`` vectors at +0x18, +0x28, +0x38, +0x48.
- an emitter object: +0x00 its name. Effects' data regions lie in table order, each from its emitter list to the
  next effect's, and hold only pointers into themselves or into the string pool.

The loader fixes the pointers up by walking references, so an object referenced twice crashes the game; a clone
therefore copies its source's whole region (:func:`clone`), and :func:`check` verifies a result.
"""

import struct
from collections.abc import Iterable, Mapping

MAGIC = b"BFFH"
SECTIONS = 0xA8
SECTION = 0x28
ENTRY = 0x68
VECTORS = (0x08, 0x18, 0x28, 0x38, 0x48)  # pointer vectors of an effect entry; +0x08 is the emitter list
PAGE = 0x1000
# 8-aligned values at least this large are taken for pointers when scanning a region; smaller ones are data (no
# effect region lies this low: the root and the effect table do).
LOWEST_POINTER = 0x10000


class VfxError(ValueError):
    pass


def _u32(b, at: int) -> int:
    return struct.unpack_from("<I", b, at)[0]


def _u64(b, at: int) -> int:
    return struct.unpack_from("<Q", b, at)[0]


def _cstr(b, at: int) -> str:
    return bytes(b[at : b.index(b"\0", at)]).decode("utf-8")


def _align(n: int, a: int) -> int:
    return (n + a - 1) // a * a


class _Blob:
    def __init__(self, data: bytes):
        if data[:4] != MAGIC:
            raise VfxError(f"not a Vfx3 binary: magic {bytes(data[:4])!r}, expected BFFH")
        if (size := _u32(data, 8)) != len(data):
            raise VfxError(f"BFFH size {size} but {len(data)} bytes")
        self.b = data
        self.sections: dict[str, tuple[int, int, int]] = {}  # name -> (record, offset, size)
        for k in range(_u32(data, 0x18)):
            rec = SECTIONS + SECTION * k
            if data[rec : rec + 4] != b"BFSI":
                raise VfxError(f"section record {k} at 0x{rec:x} is not BFSI")
            name = data[rec + 0x18 : rec + 0x28].split(b"\0")[0].decode()
            self.sections[name] = (rec, _u64(data, rec + 0x10), _u32(data, rec + 8))
        for name in ("Default", "StringPool"):
            if name not in self.sections:
                raise VfxError(f"no {name} section")
        self.root = self.sections["Default"][1]
        self.table, self.count = _u64(data, self.root + 0x30), _u32(data, self.root + 0x38)
        if (size := _u32(data, self.root + 0x3C)) != ENTRY:
            raise VfxError(f"effect entries of 0x{size:x} bytes, expected 0x{ENTRY:x}")
        self.entries = {}
        for i in range(self.count):
            entry = self.table + ENTRY * i
            self.entries[_cstr(data, _u64(data, entry))] = entry
        self.starts = sorted(_u64(data, e + 8) for e in self.entries.values())

    def entry(self, name: str) -> int:
        if name not in self.entries:
            raise VfxError(f"no effect {name!r}")
        return self.entries[name]

    def region(self, name: str) -> tuple[int, int]:
        """From the effect's emitter list to the next effect's, the effect table, the end of ``Default`` or the end
        of the blob, whichever comes first after it."""
        r0 = _u64(self.b, self.entry(name) + 8)
        _, d0, dsize = self.sections["Default"]
        ends = [s for s in self.starts if s > r0] + [len(self.b)]
        if self.table > r0:
            ends.append(self.table)
        if r0 < d0 + dsize:
            ends.append(d0 + dsize)
        return r0, min(ends)

    def emitter_list(self, name: str) -> tuple[int, list[int]]:
        entry = self.entry(name)
        at, n = _u64(self.b, entry + 8), _u32(self.b, entry + 0x10)
        return at, list(struct.unpack_from(f"<{n}Q", self.b, at))

    def emitter_names(self, name: str) -> list[str]:
        return [_cstr(self.b, _u64(self.b, obj)) for obj in self.emitter_list(name)[1]]


def effect_names(blob: bytes) -> list[str]:
    """Every effect's name, in table order."""
    return list(_Blob(blob).entries)


def emitters(blob: bytes, effect: str) -> list[str]:
    """The names of an effect's emitters, in list order."""
    return _Blob(blob).emitter_names(effect)


def region(blob: bytes, effect: str) -> tuple[int, int]:
    """An effect's data region ``(start, end)``."""
    return _Blob(blob).region(effect)


def effect_bytes(blob: bytes, effect: str) -> bytes:
    """An effect's entry and data region, to compare an effect across two blobs."""
    v = _Blob(blob)
    entry = v.entry(effect)
    r0, r1 = v.region(effect)
    return blob[entry : entry + ENTRY] + blob[r0:r1]


def _pointers(b: bytes, r0: int, r1: int) -> list[tuple[int, int]]:
    """(offset, value) of every 8-aligned word in ``[r0, r1)`` that looks like a pointer."""
    out = []
    for at in range(_align(r0, 8), r1 - 7, 8):
        value = _u64(b, at)
        if value >= LOWEST_POINTER and value % 8 == 0 and value < len(b):
            out.append((at, value))
    return out


def clone(blob: bytes, source: str, name: str, keep: Iterable[str]) -> bytes:
    """``blob`` with a new effect ``name``: a copy of ``source``'s data region at the blob's end (on a page offset
    equal to the source's, pointers into the region shifted), its emitter list holding only the emitters named in
    ``keep`` (native order; the others stay in the copy, after the count), a new effect table with the entry
    appended, the root pointing at it, the name in the string pool, the blob and the ``StringPool`` section grown
    to the new end. Every native byte past the header stays where it was."""
    v = _Blob(blob)
    if name in v.entries:
        raise VfxError(f"effect {name!r} already exists")
    entry = v.entry(source)
    have = v.emitter_names(source)
    keep = list(keep)
    for em in keep:
        if em not in have:
            raise VfxError(f"{source} has no emitter {em!r} (it has {have})")
    r0, r1 = v.region(source)
    pool0 = v.sections["StringPool"][1]
    old = len(blob)
    new_r0 = _align(old, PAGE) + r0 % PAGE
    delta = new_r0 - r0
    chunk = bytearray(blob[r0:r1])
    stray = []
    for at, value in _pointers(blob, r0, r1):
        if r0 <= value < r1:
            struct.pack_into("<Q", chunk, at - r0, value + delta)
        elif value < pool0:
            stray.append(f"0x{at:x} -> 0x{value:x}")
    if stray:
        raise VfxError(f"{source}: its region points outside itself: {stray[:8]}")
    ent = bytearray(blob[entry : entry + ENTRY])
    for k in range(8, ENTRY, 8):
        value = _u64(ent, k)
        if r0 <= value < r1:
            struct.pack_into("<Q", ent, k, value + delta)
    table_at = _align(new_r0 + len(chunk), 0x100)
    table = bytearray(blob[v.table : v.table + ENTRY * v.count]) + ent
    name_at = table_at + len(table)
    text = name.encode("utf-8") + b"\0"
    end = _align(name_at + len(text), 0x10)
    struct.pack_into("<Q", table, ENTRY * v.count, name_at)
    out = bytearray(blob)
    out += bytes(new_r0 - old) + chunk
    out += bytes(table_at - len(out)) + table
    out += text + bytes(end - name_at - len(text))
    struct.pack_into("<QI", out, v.root + 0x30, table_at, v.count + 1)
    struct.pack_into("<I", out, 8, end)
    rec, _, pool_size = v.sections["StringPool"]
    struct.pack_into("<I", out, rec + 8, pool_size + end - old)
    new_entry = table_at + ENTRY * v.count
    list_at, n = _u64(out, new_entry + 8), _u32(out, new_entry + 0x10)
    objects = list(struct.unpack_from(f"<{n}Q", out, list_at))
    kept = [o for o, em in zip(objects, have, strict=True) if em in keep]
    dropped = [o for o, em in zip(objects, have, strict=True) if em not in keep]
    struct.pack_into(f"<{n}Q", out, list_at, *kept, *dropped)
    struct.pack_into("<I", out, new_entry + 0x10, len(kept))
    return bytes(out)


def check(blob: bytes, clones: Mapping[str, str]) -> None:
    """Raise :class:`VfxError` naming the offsets when an object is referenced twice (any effect's entry vectors and
    listed emitters) or when a clone (``{clone: its source}``) has a pointer outside its own region and the string
    pool. A clone's region is as long as its source's (the effect tables earlier clones left behind follow it)."""
    v = _Blob(blob)
    seen: dict[int, str] = {}
    twice = []
    for name, entry in v.entries.items():
        refs = [_u64(blob, entry + k) for k in VECTORS]
        refs += v.emitter_list(name)[1]
        for ref in refs:
            if not ref:
                continue
            if ref in seen:
                twice.append(f"0x{ref:x} ({seen[ref]}, {name})")
            seen[ref] = name
    # Clones lie past the start of the StringPool section (it grows over them), so "in the string pool" means in
    # that section and in no effect's region.
    pool0, pool_size = v.sections["StringPool"][1:]
    extents = {name: v.region(name) for name in v.entries}
    for name, source in clones.items():
        s0, s1 = extents[source]
        extents[name] = (extents[name][0], extents[name][0] + s1 - s0)
    regions = list(extents.values())
    stray = []
    for name in clones:
        r0, r1 = extents[name]
        for at, value in _pointers(blob, r0, r1):
            if r0 <= value < r1:
                continue
            in_pool = pool0 <= value < pool0 + pool_size and not any(a <= value < b for a, b in regions)
            if not in_pool:
                stray.append(f"{name}: 0x{at:x} -> 0x{value:x}")
    problems = []
    if twice:
        problems.append(f"objects referenced twice: {twice[:8]}")
    if stray:
        problems.append(f"pointers outside their region and the string pool: {stray[:8]}")
    if problems:
        raise VfxError("; ".join(problems))
