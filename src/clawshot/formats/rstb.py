"""The resource size table (``System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs``).

The game sizes a file's load buffer from this table, as Tears of the Kingdom's RESTBL does. The file is plain zstd
around, little-endian:

- header (22 bytes): magic ``RESTBL``, u32 version (1), u32 name field size (160), u32 hash entry count, u32 name
  entry count;
- hash entries, sorted by hash: u32 CRC32 of the resource path, u32 size;
- name entries, sorted by name: the resource path, NUL-padded to the name field size, u32 size. These hold paths
  whose CRC32 collides with another path's.

The resource path is the romfs path without ``.zs`` (:func:`resource_path`). A path in the name entries is looked up
by name, any other by CRC32.
"""

import struct
import zlib
from dataclasses import dataclass, field

TABLE_PATH = "System/Resource/ResourceSizeTable.Product.111.Nin_Ounce_NVN2.rsizetable.zs"
MAGIC = b"RESTBL"
_HEADER = struct.Struct("<6sIIII")
_HASH_ENTRY = struct.Struct("<II")

# Resource path suffix -> what an entry adds to the file size rounded up to 32 bytes, for the types checked against
# every such file in the game (build e0f3ccfa; plans/03-game-data.md, section 11). Other types are not covered.
OVERHEAD: dict[str, int] = {
    ".bcett.byml": 264,  # placement files (160 of 160)
    ".bfevfl": 272,  # event flows (914 of 914)
    ".sarc": 312,  # message archives (16 of 16)
    ".pack": 312,  # packs (8384 of 8384 that have an entry; Pack/ZsDic.pack.zs has none)
    # Round 15: pouch components inside actor packs; a constant parsed size whatever fields they set (166 of 166).
    ".game__component__PouchContentParam.bgyml": 5216,
    # Effect-user components inside actor packs (1309 of 1309 unique members, dump 1.1.1; section 51).
    ".engine__component__ELinkParam.bgyml": 5064,
    # Effect files (1431 of 1432, dump 1.1.1; section 51): ``static`` has its own formula (OWN_FORMULA).
    ".vsetb.byml": 264,
}
ELINK_PARAM = ".engine__component__ELinkParam.bgyml"
# ELink tables (``ELink2/elink2.Product.*.belnk``): both native tables fit size + 272 and size rounded to 32 + 264
# (dump 1.1.1; section 51). The two differ for other sizes, so an entry takes the larger (BBender, 2026-11-23).
ELINK_TABLE = ".belnk"
ELINK_TABLE_OVERHEAD = 272
ALIGNMENT = 32

# Actor parameter files inside actor packs (Round 15): 5144 plus 48 per entry of the file's own ``Components`` map,
# whether or not it has a ``$parent`` (8374 of 8374 unique ``*.engine__actor__ActorParam.bgyml`` members).
ACTOR_PARAM = ".engine__actor__ActorParam.bgyml"
ACTOR_PARAM_OVERHEAD = 5144
ACTOR_PARAM_PER_COMPONENT = 48

# Animation parameter files inside actor packs: 5096 plus 88 per entry of the file's own ``AnimationResources`` list,
# whether or not it has a ``$parent`` (544 of 544 unique ``*.engine__component__AnimationParam.bgyml`` members, dump
# 1.1.1; plans/03-game-data.md, section 50).
ANIMATION_PARAM = ".engine__component__AnimationParam.bgyml"
ANIMATION_PARAM_OVERHEAD = 5096
ANIMATION_PARAM_PER_RESOURCE = 88

# Files with a formula of their own: resource path -> (alignment, overhead). GameDataList is one file: its entry
# (1,463,176) is its size (1,462,888, a multiple of 8) + 288, which rounding to 32 would overshoot.
OWN_FORMULA: dict[str, tuple[int, int]] = {
    "GameData/GameDataList.Product.110.byml": (8, 288),
    # Round 22: bag-bomb lift component, native 992 -> 7168 (6176 parsed overhead). The private clone changes
    # only its U32 LiftGrade; no generic LiftableParam rule (36 native members have shape-dependent overhead).
    # Same-shape native/private paths only; audit and provenance in plans/rounds/r22-games.md.
    "Component/LiftableParam/Item_Bomb.game__component__LiftableParam.bgyml": (32, 6176),
    "Component/LiftableParam/Clawshot_BagBomb.game__component__LiftableParam.bgyml": (32, 6176),
    # ActorInfo: 1,934,492 raw -> 1,937,560; Round 7 same-shape model/heap field substitutions, and Round 15's
    # inserted generated-pickup rows (structural growth with the same native formula; unplayed).
    "RSDB/ActorInfo.Product.111.rstbl.byml": (32, 3064),
    # GameActorInfo 574,824 -> 575,112 and PouchActorInfo 49,380 -> 49,672: rounded + 264, the placement files'
    # overhead (build e0f3ccfa, read 2026-11-12). [Inference] the same holds when custom_items adds rows.
    "RSDB/GameActorInfo.Product.111.rstbl.byml": (32, 264),
    "RSDB/PouchActorInfo.Product.111.rstbl.byml": (32, 264),
    # Round 12: EventSetting 509212 -> 509480; same +264 observed in 19/19
    # non-ActorInfo RSDB tables; growth is enabled for these two event registries.
    "RSDB/EventSetting.Product.111.rstbl.byml": (32, 264),
    # The matching analyzed-event registry: 247276 raw -> 247560 allocated.
    "RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml": (32, 264),
    # R13 native new-game Sequence: 5916 raw -> 6296 allocated, rounded32 +376.
    # 107/108 native Sequence AINBs share this overhead; not a generic AINB rule.
    "Sequence/SetPouchAndStatusForGameStart.module.ainb": (32, 376),
    # The always-loaded effect file: 52,401,096 raw -> 52,405,256, rounded + 4136, where every other effect file is
    # rounded + 264; nothing measured on them predicts the difference (section 51). Measured on this one file, so
    # it equals the native entry plus the rounded growth (BBender, 2026-11-23).
    "Effect/static.Nin_Ounce_NVN2.vsetb.byml": (32, 4136),
}


class RstbError(ValueError):
    pass


@dataclass
class ResourceSizeTable:
    hashes: dict[int, int] = field(default_factory=dict)  # CRC32 of the resource path -> size
    names: dict[str, int] = field(default_factory=dict)  # resource path -> size, for paths whose CRC32 collides
    version: int = 1
    name_size: int = 160

    def get(self, path: str) -> int | None:
        """The entry for a resource path (or a romfs path with ``.zs``), or None when the table has none."""
        path = resource_path(path)
        if path in self.names:
            return self.names[path]
        return self.hashes.get(path_hash(path))

    def set(self, path: str, size: int) -> None:
        """Set the entry for a resource path (or a romfs path with ``.zs``); a new path gets a hash entry."""
        if not 0 <= size <= 0xFFFFFFFF:
            raise RstbError(f"size {size} for {path} does not fit in 32 bits")
        path = resource_path(path)
        if path in self.names:
            self.names[path] = size
        else:
            self.hashes[path_hash(path)] = size


def resource_path(path: str) -> str:
    """``Banc/A/A_Static.bcett.byml.zs`` -> ``Banc/A/A_Static.bcett.byml``: the key the table uses."""
    return path.removesuffix(".zs")


def path_hash(path: str) -> int:
    return zlib.crc32(resource_path(path).encode("utf-8"))


def read(data: bytes) -> ResourceSizeTable:
    """Parse a decompressed table."""
    if len(data) < _HEADER.size:
        raise RstbError(f"too short for a RESTBL header: {len(data)} bytes")
    magic, version, name_size, hash_count, name_count = _HEADER.unpack_from(data, 0)
    if magic != MAGIC:
        raise RstbError(f"not a RESTBL: magic {magic!r}")
    if version != 1:
        raise RstbError(f"RESTBL version {version} is not supported (only 1)")
    name_entry = struct.Struct(f"<{name_size}sI")
    expected = _HEADER.size + hash_count * _HASH_ENTRY.size + name_count * name_entry.size
    if len(data) != expected:
        raise RstbError(
            f"RESTBL of {hash_count} hash and {name_count} name entries is {expected} bytes, not {len(data)}"
        )
    table = ResourceSizeTable(version=version, name_size=name_size)
    offset = _HEADER.size
    for _ in range(hash_count):
        crc, size = _HASH_ENTRY.unpack_from(data, offset)
        if crc in table.hashes:
            raise RstbError(f"hash 0x{crc:08x} appears twice")
        table.hashes[crc] = size
        offset += _HASH_ENTRY.size
    for _ in range(name_count):
        raw_name, size = name_entry.unpack_from(data, offset)
        name = raw_name.split(b"\0", 1)[0].decode("utf-8")
        if name in table.names:
            raise RstbError(f"name {name!r} appears twice")
        table.names[name] = size
        offset += name_entry.size
    return table


def write(table: ResourceSizeTable) -> bytes:
    """The decompressed table, entries sorted (hashes by value, names by UTF-8 bytes) as the game's are."""
    name_entry = struct.Struct(f"<{table.name_size}sI")
    out = bytearray(_HEADER.pack(MAGIC, table.version, table.name_size, len(table.hashes), len(table.names)))
    for crc in sorted(table.hashes):
        out += _HASH_ENTRY.pack(crc, table.hashes[crc])
    for name in sorted(table.names, key=lambda n: n.encode("utf-8")):
        encoded = name.encode("utf-8")
        if len(encoded) >= table.name_size:
            raise RstbError(f"name {name!r} does not fit the {table.name_size}-byte name field with its NUL")
        out += name_entry.pack(encoded, table.names[name])
    return bytes(out)


def required_size(path: str, size: int, components: int | None = None, *, resources: int | None = None) -> int:
    """The entry a file at ``path`` (resource or romfs path) needs when its decompressed size is ``size``:
    ``size`` rounded up to 32 bytes plus the overhead of its type (:data:`OVERHEAD`), or a file's own formula
    (:data:`OWN_FORMULA`). An actor parameter file (:data:`ACTOR_PARAM`) also needs ``components``, the number of
    entries in its own ``Components`` map, and an animation parameter file (:data:`ANIMATION_PARAM`) ``resources``,
    the number of entries in its own ``AnimationResources`` list; no other type takes either.

    Raises :class:`RstbError` for a type whose formula has not been checked against the game.
    """
    path = resource_path(path)
    rounded = (size + ALIGNMENT - 1) // ALIGNMENT * ALIGNMENT
    if path.endswith(ANIMATION_PARAM):
        if components is not None:
            raise RstbError(f"{path}: a component count only applies to actor parameter files")
        if resources is None or resources < 0:
            raise RstbError(f"{path}: an animation parameter's entry needs its own AnimationResources count")
        return rounded + ANIMATION_PARAM_OVERHEAD + ANIMATION_PARAM_PER_RESOURCE * resources
    if resources is not None:
        raise RstbError(f"{path}: an AnimationResources count only applies to animation parameter files")
    if path.endswith(ACTOR_PARAM):
        if components is None or components < 0:
            raise RstbError(f"{path}: an actor parameter's entry needs its own component count, not {components}")
        return rounded + ACTOR_PARAM_OVERHEAD + ACTOR_PARAM_PER_COMPONENT * components
    if components is not None:
        raise RstbError(f"{path}: a component count only applies to actor parameter files")
    if path in OWN_FORMULA:
        alignment, overhead = OWN_FORMULA[path]
        return (size + alignment - 1) // alignment * alignment + overhead
    if path.startswith("ELink2/") and path.endswith(ELINK_TABLE):
        return max(size + ELINK_TABLE_OVERHEAD, rounded + OVERHEAD[".bcett.byml"])
    for suffix, overhead in OVERHEAD.items():
        if path.endswith(suffix):
            return rounded + overhead
    raise RstbError(
        f"no size formula for {path}: only {', '.join([*OVERHEAD, ACTOR_PARAM, ANIMATION_PARAM, ELINK_TABLE])} "
        "are checked against the game"
    )
