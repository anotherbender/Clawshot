# ruff: noqa
# fmt: off
"""NUP reader: validated parsing and integrity checking.

Reader conformance (SPEC §6.1): validate superblock, verify TOC SHA-256
before trusting TOC-derived values, bounds-check every offset/size, treat
title_id/version/NPDM/NACP as opaque, reject unknown codecs and flags.
Tree traversal, metadata access, and extraction live in .access.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import mmap
import os
import struct
from typing import TYPE_CHECKING

from . import format as F
from .._limits import MAX_FILE_SIZE

# Zstandard's maximum decoded block size (RFC 8878, section 3.1.1.2.3).
BLOCK_SIZE = 128 << 10

if TYPE_CHECKING:
    from types import TracebackType


@dataclass(frozen=True, slots=True)
class PackageInfo:
    index: int
    title_id: int
    kind: F.Kind
    version: int
    flags: int
    root_dir: int
    exefs_dir: int
    romfs_dir: int
    meta_offset: int
    meta_size: int

    @property
    def kind_name(self) -> str:
        return F.KIND_NAMES.get(self.kind, f"kind{self.kind}")

    @property
    def version_str(self) -> str:
        return f"{self.version >> 16}.{(self.version >> 8) & 0xFF}.{self.version & 0xFF}"


@dataclass(frozen=True, slots=True)
class NodeRef:
    """A child reference: is_dir + index into the respective array."""
    is_dir: bool
    index: int
    name: bytes


class NupReader:
    __slots__ = ("path", "_fh", "_mm", "super", "dir_count", "file_count", "pool", "packages", "files", "dirs", "children")
    def __init__(self, path: str) -> None:
        self.path = path
        self._fh = open(path, "rb")
        self._mm: mmap.mmap | bytes = b""
        try:
            try:
                self._mm = mmap.mmap(self._fh.fileno(), 0, access=mmap.ACCESS_READ)
            except ValueError:  # empty file
                self._mm = b""
            self.super = F.parse_super(self._mm[:F.HEADER_SIZE])
            real_size = os.fstat(self._fh.fileno()).st_size
            if self.super["file_size"] != real_size:
                raise F.NupError(
                    f"file_size {self.super['file_size']} != actual {real_size}")
            if self.super["toc_offset"] < F.HEADER_SIZE:
                raise F.NupError("toc_offset before header end")
            if self.super["blob_offset"] < self.super["toc_offset"] + self.super["toc_size"]:
                raise F.NupError("blob region overlaps TOC")
            if self.super["blob_offset"] % F.EXTENT_ALIGN:
                raise F.NupError("blob_offset not 16-byte aligned")

            toc_start = self.super["toc_offset"]
            raw_toc = self._mm[toc_start:toc_start + self.super["toc_size"]]
            if hashlib.sha256(raw_toc).digest() != self.super["toc_sha256"]:
                raise F.NupError("TOC SHA-256 mismatch - file corrupt or tampered")
            self._parse_toc(raw_toc)
            self._check_bounds()
        except BaseException:
            # Never leak an open handle/mmap: on Windows it locks the file
            # against rename/delete until GC.
            self.close()
            raise

    def close(self) -> None:
        mm = self._mm
        if isinstance(mm, mmap.mmap):
            mm.close()
        self._mm = b""
        self._fh.close()

    def __enter__(self) -> "NupReader":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    # ---- TOC parsing ----

    def _parse_toc(self, toc: bytes) -> None:
        magic, pkg_count, dir_count, file_count, pool_off, pool_size, _r = \
            F._toc_head_s.unpack_from(toc, 0)
        if magic != F.TOC_MAGIC:
            raise F.NupError(f"bad TOC magic {magic!r}")
        if pkg_count != self.super["package_count"]:
            raise F.NupError("package_count mismatch between superblock and TOC")
        need = (F._toc_head_s.size + pkg_count * F.PKG_SIZE
                + dir_count * F.DIR_SIZE + file_count * F.FILE_SIZE)
        if len(toc) < need:
            raise F.NupError("TOC truncated")
        if pool_off + pool_size > len(toc) or pool_off < need:
            raise F.NupError("string pool out of TOC bounds")

        self.dir_count = dir_count
        self.file_count = file_count
        self.pool = toc[pool_off:pool_off + pool_size]

        pos = F._toc_head_s.size
        self.packages: list[PackageInfo] = []
        for i in range(pkg_count):
            p = F.parse_pkg(toc, pos)
            pos += F.PKG_SIZE
            self.packages.append(PackageInfo(
                index=i, title_id=p.title_id, kind=F.Kind(p.kind), version=p.version,
                flags=p.flags, root_dir=p.root_dir, exefs_dir=p.exefs_dir,
                romfs_dir=p.romfs_dir, meta_offset=p.meta_offset,
                meta_size=p.meta_size))

        self.dirs: list[tuple[bytes, int, int]] = []  # (name, first_child, child_count)
        for _ in range(dir_count):
            off, ln, first, count, _r2 = F._dir_s.unpack_from(toc, pos)
            pos += F.DIR_SIZE
            self.dirs.append((self._pool_str(off, ln), first, count))

        # (name, size, sha256, ext_off, ext_size, codec)
        self.files: list[tuple[bytes, int, bytes, int, int, F.Codec]] = []  
        for _ in range(file_count):
            (off, ln), size, sha, eoff, esz, codec = F.parse_file(toc, pos)
            pos += F.FILE_SIZE
            if size > MAX_FILE_SIZE:
                raise F.NupError(
                    f"file {len(self.files)}: declared size {size} exceeds the {MAX_FILE_SIZE}-byte file limit")
            self.files.append((self._pool_str(off, ln), size, sha, eoff, esz, codec))

        slot_end = pool_off
        if (slot_end - pos) % 4:
            raise F.NupError("children array not 4-byte aligned")
        self.children = list(struct.unpack_from(f"<{(slot_end - pos) // 4}I", toc, pos))

    def _pool_str(self, off: int, ln: int) -> bytes:
        if off + ln > len(self.pool):
            raise F.NupError("string reference out of pool bounds")
        return self.pool[off:off + ln]

    def _check_bounds(self) -> None:
        file_size = self.super["file_size"]
        blob_start = self.super["blob_offset"]
        for name, size, sha, eoff, esz, codec in self.files:
            if size == 0:
                continue
            if eoff < blob_start or eoff + esz > file_size:
                raise F.NupError(f"extent out of bounds for file {name!r}")
            if eoff % F.EXTENT_ALIGN:
                raise F.NupError(f"extent not {F.EXTENT_ALIGN}-aligned for {name!r}")
        slot_total = len(self.children)
        used = 0
        for name, first, count in self.dirs:
            if first + count > slot_total:
                raise F.NupError(f"child range out of bounds for dir {name!r}")
            used += count
        if used != slot_total:
            raise F.NupError(f"child slots used {used} != total {slot_total}")
        for p in self.packages:
            if p.root_dir >= self.dir_count:
                raise F.NupError(f"package {p.index}: root_dir out of bounds")
            for d in (p.exefs_dir, p.romfs_dir):
                if d != F.NO_DIR and d >= self.dir_count:
                    raise F.NupError(f"package {p.index}: exefs/romfs dir out of bounds")
            if p.meta_size and (p.meta_offset + p.meta_size > file_size):
                raise F.NupError(f"package {p.index}: meta block out of bounds")
            if p.flags & ~F.PKG_FLAG_STANDALONE_UPDATE:
                raise F.NupError(f"package {p.index}: unknown package flags {p.flags:#x}")
        # SPEC §3.1.2: update packages need a base in the same container, or
        # the standalone_update flag (record flags, offset 0x19, bit 0).
        has_base = any(p.kind == F.KIND_BASE for p in self.packages)
        for p in self.packages:
            if (p.kind == F.KIND_UPDATE and not has_base
                    and not (p.flags & F.PKG_FLAG_STANDALONE_UPDATE)):
                raise F.NupError(
                    f"package {p.index}: update without base in container and "
                    f"standalone_update flag not set")

    # ---- member access ----

    def node_name(self, ref: NodeRef) -> bytes:
        if ref.is_dir:
            return self.dirs[ref.index][0]
        return self.files[ref.index][0]

    def file_info(self, file_index: int) -> tuple[bytes, int, bytes, int, int, F.Codec]:
        return self.files[file_index]

    def _file_chunks(self, size: int, eoff: int, esz: int, codec: F.Codec):
        end = eoff + esz
        if codec == F.CODEC_RAW:
            for pos in range(eoff, end, BLOCK_SIZE):
                yield self._mm[pos:min(pos + BLOCK_SIZE, end)]
        elif codec == F.CODEC_ZSTD:
            import zstandard
            header = self._mm[eoff:min(eoff + 18, end)]
            frame = zstandard.get_frame_parameters(header)
            if frame.content_size not in (size, zstandard.CONTENTSIZE_UNKNOWN):
                raise F.NupError(f"size mismatch: Zstandard frame declares {frame.content_size} != {size}")
            if frame.window_size > MAX_FILE_SIZE:
                raise F.NupError("Zstandard window exceeds the file limit")
            header_size = zstandard.frame_header_size(header)
            decoder = zstandard.ZstdDecompressor().decompressobj()
            decoder.decompress(header[:header_size])
            pos = eoff + header_size
            # Feed one complete block at a time: decompressobj exposes EOF (unlike
            # stream_reader), and a block expands to at most 128 KiB. The native
            # decoder still validates its contents and the optional frame checksum.
            # Framing: https://www.rfc-editor.org/rfc/rfc8878#section-3.1.1.2
            while pos + 3 <= end:
                block = int.from_bytes(self._mm[pos:pos + 3], "little")
                last, kind, length = block & 1, (block >> 1) & 3, block >> 3
                if kind == 3 or length > BLOCK_SIZE:
                    raise F.NupError("invalid Zstandard block header")
                stored = 1 if kind == 1 else length
                stop = pos + 3 + stored + (4 if last and frame.has_checksum else 0)
                if stop > end:
                    raise F.NupError("truncated Zstandard block or checksum")
                yield decoder.decompress(self._mm[pos:stop])
                pos = stop
                if last:
                    if not decoder.eof:
                        raise F.NupError("truncated Zstandard frame")
                    return
            raise F.NupError("truncated Zstandard frame")
        else:
            raise F.NupError(f"unknown codec {codec}")

    def read_file(self, file_index: int) -> bytes:
        name, size, sha, eoff, esz, codec = self.files[file_index]
        if size > MAX_FILE_SIZE:
            raise F.NupError(f"declared file size {size} exceeds the {MAX_FILE_SIZE}-byte file limit")
        if codec == F.CODEC_RAW and esz != size:
            raise F.NupError(f"size mismatch for {name!r}: {esz} != {size}")
        parts = []
        digest = hashlib.sha256()
        total = 0
        for data in self._file_chunks(size, eoff, esz, codec):
            total += len(data)
            if total > size:
                raise F.NupError(f"size mismatch for {name!r}: {total} > {size}")
            digest.update(data)
            parts.append(data)
        if total != size:
            raise F.NupError(f"size mismatch for {name!r}: {total} != {size}")
        if digest.digest() != sha:
            raise F.NupError(f"file SHA256 mismatch for {name!r}")
        return b"".join(parts)
