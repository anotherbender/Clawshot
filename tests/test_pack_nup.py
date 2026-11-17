"""Synthetic NUPs: package selection, compressed reads, integrity and preflight ordering."""

import hashlib
import json
import random
import struct
import tracemalloc

import pytest
import zstandard

from clawshot.pack import VERSION_FILES, PackError, build, runtime, tree_digest, version_digest
from clawshot.pack._nup import read as nup
from clawshot.pack._nup.format import NupError
from clawshot.pack._nup.read import NupReader
from clawshot.pack.source import local_romfs, open_nup


def write_nup(path, packages, *, compressor=None, raw=False):
    """Build v1 records from the public format; all contents are invented by tests."""
    dirs, files, roots = [], [], []
    for version, kind, contents, *title in packages:
        root = {}
        for name, data in contents.items():
            node = root
            parts = name.split("/")
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = data

        def directory(name, children):
            index = len(dirs)
            dirs.append([name.encode(), []])
            for child, data in sorted(children.items()):
                if isinstance(data, dict):
                    dirs[index][1].append((True, directory(child, data)))
                else:
                    fi = len(files)
                    files.append((child.encode(), data))
                    dirs[index][1].append((False, fi))
            return index

        ri = directory("", {"romfs": root})
        roots.append((version, kind, ri, ri + 1, title[0] if title else 0x0400486024DEC000))
    pool, records, children = bytearray(), bytearray(), []

    def name_ref(name):
        off = len(pool)
        pool.extend(name)
        return off, len(name)

    for name, refs in dirs:
        records.extend(struct.pack("<IIIIQ", *name_ref(name), len(children), len(refs), 0))
        children.extend(i if is_dir else len(dirs) + i for is_dir, i in refs)
    file_names = [name_ref(name) for name, _ in files]
    toc_size = 48 + 64 * len(roots) + len(records) + 80 * len(files) + 4 * len(children) + len(pool)
    blob_offset = (128 + toc_size + 15) & ~15
    blob, file_records = bytearray(), bytearray()
    for i, (_, data) in enumerate(files):
        compressed = (compressor or zstandard.ZstdCompressor()).compress(data)
        codec = int(not raw and len(compressed) < len(data))
        payload = compressed if codec else data
        offset = blob_offset + len(blob) if data else 0
        file_records.extend(
            struct.pack(
                "<IIQQQ32sBBH12x",
                *file_names[i],
                len(data),
                offset,
                len(payload),
                hashlib.sha256(data).digest(),
                codec,
                0,
                0,
            )
        )
        blob.extend(payload)
        blob.extend(b"\0" * (-len(blob) % 16))
    toc = bytearray(
        struct.pack("<4sIQQQQQ", b"TOC\x01", len(roots), len(dirs), len(files), toc_size - len(pool), len(pool), 0)
    )
    for version, kind, ri, romfs, title_id in roots:
        toc.extend(
            struct.pack("<QIIIIBBHIQI20x", title_id, ri, 0xFFFFFFFF, romfs, version, kind, int(kind == 1), 0, 0, 0, 0)
        )
    toc.extend(records)
    toc.extend(file_records)
    toc.extend(struct.pack(f"<{len(children)}I", *children))
    toc.extend(pool)
    header = struct.pack(
        "<4sHHQQ32sQQII16s32s",
        b"NUP\x01",
        128,
        1,
        128,
        len(toc),
        hashlib.sha256(toc).digest(),
        blob_offset,
        blob_offset + len(blob),
        len(roots),
        0,
        b"\0" * 16,
        b"\0" * 32,
    )
    path.write_bytes(header + toc + b"\0" * (blob_offset - 128 - len(toc)) + blob)
    return path


def version_files(label=b"supported"):
    return {name: label + str(i).encode() for i, name in enumerate(VERSION_FILES)}


def test_nup_and_folder_have_identical_fingerprints_and_reads(tmp_path):
    contents = version_files() | {"nested/compressed": b"synthetic" * 1000, "empty": b""}
    path = write_nup(tmp_path / "game.nup", [(131072, 1, contents)])
    root = tmp_path / "folder"
    for name, data in contents.items():
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
    assert version_digest(path) == version_digest(root)
    with open_nup(path) as source:
        assert {name: source.read(name) for name in source.files} == contents
        assert source.reader.file_info(source.files["nested/compressed"])[-1] == 1
    path.rename(tmp_path / "closed.nup")  # no leaked mmap/file handle on Windows


def test_newest_update_is_used_without_base_fallback(tmp_path, monkeypatch):
    path = write_nup(tmp_path / "game.nup", [(0, 0, version_files()), (131072, 1, version_files(b"new"))])
    expected = version_digest(write_nup(tmp_path / "base.nup", [(0, 0, version_files())]))
    monkeypatch.setattr("clawshot.pack.ROMFS_SHA256", expected)
    with pytest.raises(PackError, match="fingerprint"):
        build(path, 8, "never-decoded", tmp_path / "pack.zip")
    assert not (tmp_path / "pack.zip").exists()
    with pytest.raises(PackError, match="fingerprint"), local_romfs(path, tmp_path):
        pytest.fail("wrong update reached generation")
    assert not list(tmp_path.glob(".romfs-*"))


def test_incomplete_newest_update_does_not_borrow_base_files(tmp_path):
    path = write_nup(tmp_path / "game.nup", [(0, 0, version_files()), (131072, 1, {VERSION_FILES[0]: b"new"})])
    with pytest.raises(PackError, match="missing romfs"):
        version_digest(path)


def test_update_with_its_own_title_id_is_the_same_game(tmp_path):
    """Dumps that keep base and update apart give the update the base's title ID plus 0x800."""
    base, update = 0x0400486024DEC000, 0x0400486024DEC800
    path = write_nup(
        tmp_path / "game.nup", [(65536, 0, version_files(b"old"), base), (131072, 1, version_files(), update)]
    )
    expected = version_digest(write_nup(tmp_path / "update.nup", [(131072, 1, version_files())]))
    assert version_digest(path) == expected
    with open_nup(path) as source:
        assert source.package.title_id == update
        assert source.read(VERSION_FILES[0]) == version_files()[VERSION_FILES[0]]


def test_packages_of_two_games_are_refused(tmp_path):
    path = write_nup(
        tmp_path / "game.nup",
        [(65536, 0, version_files(), 0x0400486024DEC000), (131072, 1, version_files(), 0x0100000000011800)],
    )
    with pytest.raises(PackError, match="one game"):
        version_digest(path)


@pytest.mark.parametrize("damage", ["toc", "payload", "truncated"])
def test_corrupt_nup_is_rejected_before_output(tmp_path, damage):
    path = write_nup(tmp_path / "game.nup", [(131072, 1, version_files())])
    data = bytearray(path.read_bytes())
    if damage == "toc":
        data[150] ^= 1
    elif damage == "payload":
        offset = struct.unpack_from("<Q", data, 56)[0]
        data[offset] ^= 1
    else:
        data = data[:100]
    path.write_bytes(data)
    with pytest.raises(PackError):
        build(path, 8, "never-decoded", tmp_path / "out" / "pack.zip")
    assert not (tmp_path / "out").exists()
    path.unlink()  # failed parse also closes the handle


def test_malformed_compressed_extent_is_reported_as_pack_error(tmp_path):
    contents = version_files() | {VERSION_FILES[0]: b"synthetic compressed bytes" * 1000}
    path = write_nup(tmp_path / "game.nup", [(131072, 1, contents)])
    with open_nup(path) as source:
        info = source.reader.file_info(source.files[VERSION_FILES[0]])
        assert info[-1] == 1
        offset = info[3]
    data = bytearray(path.read_bytes())
    data[offset] ^= 1  # break the zstd frame magic, not the independently hashed TOC
    path.write_bytes(data)
    with pytest.raises(PackError):
        version_digest(path)
    path.unlink()


@pytest.mark.parametrize("name", ["../escape", "C:/escape", "nested/back\\slash", "A/file", "bad./file"])
def test_unsafe_nup_names_never_reach_disk(tmp_path, name):
    contents = version_files() | {name: b"unsafe", "a/file": b"case collision"}
    path = write_nup(tmp_path / "game.nup", [(131072, 1, contents)])
    with pytest.raises(PackError):
        version_digest(path)
    assert not (tmp_path / "escape").exists()


def test_existing_nup_seed_is_verified_without_cache_or_hookshot(tmp_path, monkeypatch):
    path = write_nup(tmp_path / "game.nup", [(131072, 1, version_files())])
    monkeypatch.setattr("clawshot.pack.ROMFS_SHA256", version_digest(path))
    root = tmp_path / "pack"
    seed = root / "seed"
    seed.mkdir(parents=True)
    note = seed / "play-note.md"
    note.write_text("already generated")
    (root / "pack.json").write_text(json.dumps({"format": 1, "seed": 8, "output_sha256": tree_digest(seed)}))
    (root / "folders.json").write_text(json.dumps({"romfs": str(path), "game": ""}))
    before = note.stat().st_mtime_ns
    runtime.make(root.resolve())
    assert note.read_text() == "already generated"
    assert note.stat().st_mtime_ns == before
    assert sorted(p.name for p in root.iterdir()) == ["folders.json", "pack.json", "seed"]


def _rewrite_file(path, index=0, *, size=None, extent_size=None):
    data = bytearray(path.read_bytes())
    toc_start, toc_size = struct.unpack_from("<QQ", data, 8)
    packages = struct.unpack_from("<I", data, toc_start + 4)[0]
    directories = struct.unpack_from("<Q", data, toc_start + 8)[0]
    record = toc_start + 48 + packages * 64 + directories * 24 + index * 80
    if size is not None:
        struct.pack_into("<Q", data, record + 8, size)
    if extent_size is not None:
        struct.pack_into("<Q", data, record + 24, extent_size)
    data[24:56] = hashlib.sha256(data[toc_start : toc_start + toc_size]).digest()
    path.write_bytes(data)


def test_oversized_declared_file_is_refused_before_payload_allocation(tmp_path):
    path = write_nup(tmp_path / "expanded.nup", [(131072, 1, {"repeat": b"x" * 1024})])
    _rewrite_file(path, size=2 << 30)
    assert path.stat().st_size < 1024
    tracemalloc.start()
    try:
        with pytest.raises(PackError, match="file limit"), open_nup(path):
            pytest.fail("oversized metadata reached member access")
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 1 << 20, f"2 GiB declaration allocated {peak} bytes"
    path.unlink()  # rejection closes the mmap and handle


def test_direct_read_cannot_bypass_file_limit(tmp_path):
    path = write_nup(tmp_path / "direct.nup", [(131072, 1, {"file": b"x"})])
    with NupReader(str(path)) as reader:
        name, _, sha, offset, stored, codec = reader.files[0]
        reader.files[0] = (name, (512 << 20) + 1, sha, offset, stored, codec)
        with pytest.raises(NupError, match="file limit"):
            reader.read_file(0)


def test_file_limit_boundary(tmp_path, monkeypatch):
    payload = b"boundary" * 1024
    path = write_nup(tmp_path / "boundary.nup", [(131072, 1, {"file": payload})])
    monkeypatch.setattr(nup, "MAX_FILE_SIZE", len(payload))
    with open_nup(path) as source:
        assert source.read("file") == payload
    monkeypatch.setattr(nup, "MAX_FILE_SIZE", len(payload) - 1)
    with pytest.raises(PackError, match="file limit"), open_nup(path):
        pass


@pytest.mark.parametrize("compressed", [False, True])
def test_tampered_file_is_hashed_before_assembly(tmp_path, compressed):
    payload = b"x" * (8 << 20) if compressed else bytes(range(256)) * (32 << 10)
    path = write_nup(tmp_path / "tampered.nup", [(131072, 1, {"file": payload})], raw=not compressed)
    with open_nup(path) as source:
        assert source.read("file") == payload
        _, _, _, offset, stored, _ = source.reader.file_info(source.files["file"])
    data = bytearray(path.read_bytes())
    if compressed:
        replacement = zstandard.ZstdCompressor().compress(b"y" * len(payload))
        assert len(replacement) == stored
        data[offset : offset + stored] = replacement
    else:
        data[offset + stored - 1] ^= 1
    path.write_bytes(data)
    with NupReader(str(path)) as reader:
        tracemalloc.start()
        try:
            with pytest.raises(NupError, match="SHA"):
                reader.read_file(0)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
    # The decoded chunks fit; joining them before rejecting would need another 8 MiB.
    assert peak < 12 << 20, f"tampered file allocated {peak} bytes"


@pytest.mark.parametrize("content_size", [False, True])
def test_frame_expansion_cannot_exceed_declared_file_size(tmp_path, content_size):
    path = write_nup(
        tmp_path / "hidden-size.nup",
        [(131072, 1, {"file": b"x" * (8 << 20)})],
        compressor=zstandard.ZstdCompressor(write_content_size=content_size),
    )
    _rewrite_file(path, size=1024)
    tracemalloc.start()
    try:
        with pytest.raises(PackError, match="size mismatch"), open_nup(path) as source:
            source.read("file")
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 1 << 20, f"1 KiB declaration expanded to {peak} bytes"


def test_truncated_frame_checksum_is_refused(tmp_path):
    path = write_nup(
        tmp_path / "truncated.nup",
        [(131072, 1, {"file": b"x" * 1024})],
        compressor=zstandard.ZstdCompressor(write_checksum=True),
    )
    with NupReader(str(path)) as reader:
        assert reader.read_file(0) == b"x" * 1024
        stored = reader.files[0][4]
    _rewrite_file(path, extent_size=stored - 1)
    with pytest.raises(PackError), open_nup(path) as source:
        source.read("file")


@pytest.mark.parametrize("content_size", [False, True])
@pytest.mark.parametrize("checksum", [False, True])
def test_streamed_frames_preserve_raw_and_compressed_blocks(tmp_path, content_size, checksum):
    payload = random.Random(31).randbytes(128 << 10) + b"repeated" * (32 << 10)
    path = write_nup(
        tmp_path / "blocks.nup",
        [(131072, 1, {"file": payload})],
        compressor=zstandard.ZstdCompressor(write_content_size=content_size, write_checksum=checksum),
    )
    with open_nup(path) as source:
        assert source.read("file") == payload
