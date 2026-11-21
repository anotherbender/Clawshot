"""New-game-only item-bar initialization, using native sequence pouch pushes.

The supported AINB is spliced, not reserialized: existing nodes, parameters and
strings retain their identities. Only absolute section/link offsets move. Native
format observations and the independent decoder oracle: r13-item-grants.md.
"""

import hashlib
import struct
import uuid
from bisect import bisect_right
from functools import partial

from clawshot import starting
from clawshot.formats import evfl
from clawshot.patch import gamedata, items
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

PATH = "Sequence/SetPouchAndStatusForGameStart.module.ainb"
SHA256 = "63ddeaa34e4839eceea2509e20b27b6f3c19f15cd72daf308c799bdfdb6e87b0"
PUSH = "SeqOneShotPushToPouch"
START_PUSHES = (("Item_NutBag_Small", 1), ("Item_DekuNut", 0))
_HEADER = 0x74
_NODE = 0x3C
_BODY = 0xA4
# Absolute file offsets in the v0x408 header; other words are counts/IDs.
_OFFSETS = (0x20, 0x24, 0x28, 0x2C, 0x30, 0x34, 0x38, 0x3C, 0x40, 0x48, 0x4C, 0x50, 0x5C, 0x68, 0x6C, 0x70)


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _splice(
    data: bytes,
    pushes: tuple[tuple[str, int], ...] = START_PUSHES,
    *,
    after_setup: bool = False,
    wallet: str = "Item_Wallet_Small",
) -> bytes:
    """Append literal pushes, optionally after the entire original setup.

    Production callers fingerprint the sole native input. This separate structural
    operation also permits wholly synthetic fixtures and an independent oracle.
    """
    push_count = len(pushes)
    child_total = push_count + int(after_setup)
    if not 1 <= child_total < 255:
        raise PatchError("start items: unsupported initial inventory size")
    if len(data) < _HEADER or data[:8] != b"AIB \x08\x04\x00\x00":
        raise PatchError("start items: expected AINB v0x408")
    count, commands = _u32(data, 0x10), _u32(data, 0x0C)
    nodes = _HEADER + commands * 0x18
    node_end = nodes + count * _NODE
    pool = _u32(data, 0x24)
    props, inputs = _u32(data, 0x2C), _u32(data, 0x34)
    if commands != 1 or node_end != _u32(data, 0x20) or not node_end < props < inputs < pool < len(data):
        raise PatchError("start items: unsupported sequence section layout")

    def string(offset: int) -> str:
        return data[pool + offset : data.index(b"\0", pool + offset)].decode("utf-8")

    headers = [nodes + i * _NODE for i in range(count)]
    push = [h for h in headers if string(_u32(data, h + 8)) == PUSH]
    # All native pushes have identical literal parameter shapes. Reuse their
    # action/property identity, never an extracted node or a generated game blob.
    if not push:
        raise PatchError("start items: no native pouch push template")
    template = push[0]
    body = _u32(data, template + 0x14)
    shape = struct.unpack_from("<36I", data, body)
    if shape[3] != 1 or shape[13] != 1 or shape[25] != 1 or any(data[body + 0x90 : body + _BODY]):
        raise PatchError(f"start items: unsupported pouch push parameter shape {shape!r}")
    root = _u32(data, _HEADER + 0x14)
    if root >= count or struct.unpack_from("<H", data, headers[root])[0] != 3:
        raise PatchError("start items: expected simultaneous new-game root")
    root_body = _u32(data, headers[root] + 0x14)
    plugs = data[root_body + 0x90 : root_body + _BODY]
    child_count = plugs[4]
    if child_count >= 255 or any(plugs[i] for i in range(0, 20, 2) if i != 4):
        raise PatchError("start items: unsupported root plug shape")
    link_end = root_body + _BODY + child_count * 4
    root_end = link_end + child_count * 8
    if [_u32(data, root_body + _BODY + i * 4) for i in range(child_count)] != [
        link_end + i * 8 for i in range(child_count)
    ]:
        raise PatchError("start items: noncontiguous root child links")

    prop_offsets = list(struct.unpack_from("<6I", data, props))
    io_offsets = list(struct.unpack_from("<12I", data, inputs))
    int_props = (prop_offsets[1] - prop_offsets[0]) // 12
    bool_props = (prop_offsets[2] - prop_offsets[1]) // 12
    int_inputs = (io_offsets[1] - io_offsets[0]) // 16
    string_inputs = (io_offsets[7] - io_offsets[6]) // 16
    if not all(node_end <= p <= pool for p in (*prop_offsets, *io_offsets)):
        raise PatchError("start items: invalid parameter table offsets")

    strings = bytearray()
    interned = {}

    def intern(text: str) -> int:
        if text in interned:
            return interned[text]
        encoded = text.encode("utf-8") + b"\0"
        found = pool
        while (found := data.find(encoded, found)) != -1:
            if found == pool or data[found - 1] == 0:
                interned[text] = found - pool
                return found - pool
            found += 1
        offset = len(data) - pool + len(strings)
        interned[text] = offset
        strings.extend(encoded)
        return offset

    empty = intern("")
    int_values = b"".join(
        struct.pack("<III", intern(name), 0, 0) for name in ("BusyPolicy", "NumLoop", "PlayPolicy", "ResultPolicy")
    )
    bool_values = b"".join(
        struct.pack("<III", intern(name), 0, value)
        for name, value in (("IsDelayJudge", 0), ("IsLoop", 0), ("IsUpdateNextInFrame", 1))
    )
    int_values_in = b"".join(
        struct.pack("<IHHiI", intern("Num"), 0xFFFF, 0, 0x01800000, number) for _, number in pushes
    )
    string_values_in = b"".join(
        struct.pack(
            "<IHHiI",
            intern("ActorName"),
            0xFFFF,
            0,
            0x00800000,
            intern(f"Work/Actor/{actor}.engine__actor__ActorParam.gyml"),
        )
        for actor, _ in pushes
    )
    wallet_input = None
    if wallet != "Item_Wallet_Small":
        native_wallet = "Work/Actor/Item_Wallet_Small.engine__actor__ActorParam.gyml"
        found = [
            offset + 12
            for offset in range(io_offsets[6], io_offsets[7], 16)
            if string(_u32(data, offset + 12)) == native_wallet
        ]
        if len(found) != 1:
            raise PatchError(f"start items: expected one native initial wallet, got {found}")
        wallet_input = (found[0], intern(f"Work/Actor/{wallet}.engine__actor__ActorParam.gyml"))
    # Insertions are after their original section's final element. Equal-address
    # inserts preserve order (e.g. an empty parameter table in a synthetic input).
    additions = [
        (node_end, bytearray((push_count + 1) * _NODE), "headers"),
        *(
            []
            if after_setup
            else [
                (link_end, bytearray(4), "root pointer"),
                (root_end, bytearray(8), "root child"),
            ]
        ),
        (props, bytearray((push_count + 1) * _BODY + child_total * 12), "bodies"),
        (prop_offsets[1], bytearray(int_values), "integer properties"),
        (prop_offsets[2], bytearray(bool_values), "boolean properties"),
        (io_offsets[1], bytearray(int_values_in), "integer inputs"),
        (io_offsets[7], bytearray(string_values_in), "string inputs"),
    ]
    additions.sort(key=lambda row: row[0])
    positions, offsets, delta = {}, [], 0
    for offset, content, name in additions:
        positions[name] = offset + delta
        delta += len(content)
        offsets.append((offset, delta))
    boundaries = [p for p, _ in offsets]

    def moved(offset: int) -> int:
        index = bisect_right(boundaries, offset) - 1
        return offset + (offsets[index][1] if index >= 0 else 0)

    out, previous = bytearray(), 0
    for offset, content, _ in additions:
        out.extend(data[previous:offset])
        out.extend(content)
        previous = offset
    out.extend(data[previous:])
    out.extend(strings)

    def put(offset: int, value: int) -> None:
        struct.pack_into("<I", out, offset, value)

    for offset in _OFFSETS:
        old = _u32(data, offset)
        if old:
            put(offset, moved(old))
    put(0x10, count + push_count + 1)
    # Existing bodies and every existing plug target remain otherwise unchanged.
    for header in headers:
        old_body = _u32(data, header + 0x14)
        put(header + 0x14, moved(old_body))
        total = sum(data[old_body + 0x90 : old_body + _BODY : 2])
        for i in range(total):
            pointer = old_body + _BODY + i * 4
            put(moved(pointer), moved(_u32(data, pointer)))
    for table, pointers in ((props, prop_offsets), (inputs, io_offsets)):
        for i, pointer in enumerate(pointers):
            put(moved(table) + 4 * i, moved(pointer))
    # A boundary's insertion belongs to the preceding parameter type, not to
    # the following one. Their start pointers therefore move past the insert.
    if after_setup:
        put(_HEADER + 0x14, count)
        out[headers[root] + 6] &= ~4
    else:
        out[moved(root_body) + 0x94] = child_count + 1
        for i in range(7, 20, 2):
            out[moved(root_body) + 0x90 + i] = child_count + 1
        put(positions["root pointer"], positions["root child"])
        struct.pack_into("<II", out, positions["root child"], count, empty)
    if wallet_input is not None:
        put(moved(wallet_input[0]), wallet_input[1])

    sequential = positions["bodies"]
    bodies = [sequential] + [sequential + _BODY + child_total * 12 + i * _BODY for i in range(push_count)]
    for i, node_body in enumerate(bodies):
        kind = 2 if not i else 0
        header = positions["headers"] + i * _NODE
        if i:
            out[header : header + _NODE] = data[template : template + _NODE]
            out[node_body : node_body + _BODY] = data[body : body + _BODY]
        struct.pack_into("<HH", out, header, kind, count + i)
        put(header + 8, empty if not i else _u32(data, template + 8))
        put(header + 0x14, node_body)
        if not i and after_setup:
            out[header + 6] = 4
        out[header + 0x2C : header + _NODE] = uuid.uuid5(
            uuid.NAMESPACE_URL, f"clawshot/{PATH}/start-items/{i}"
        ).bytes_le
        if i:
            put(node_body + 0x30, int_inputs + i - 1)
            put(node_body + 0x60, string_inputs + i - 1)
    struct.pack_into("<4I", out, sequential, int_props, 4, bool_props, 3)
    out[sequential + 0x94] = child_total
    for i in range(7, 20, 2):
        out[sequential + 0x90 + i] = child_total
    children = ([root] if after_setup else []) + list(range(count + 1, count + push_count + 1))
    for i, child in enumerate(children):
        target = sequential + _BODY + child_total * 4 + i * 8
        put(sequential + _BODY + i * 4, target)
        struct.pack_into("<II", out, target, child, empty)
    return bytes(out)


def patch_sequence(
    data: bytes,
    *,
    pushes: tuple[tuple[str, int], ...] = START_PUSHES,
    hearts: int = 0,
    wallet: str = "Item_Wallet_Small",
    after_setup: bool = False,
) -> bytes:
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise PatchError("start items: native new-game sequence fingerprint changed")
    if hearts:
        out = bytearray(data)
        for offset in (0x11C8, 0x11E8):
            if _u32(data, offset) != 12:
                raise PatchError(f"start items: native health literal changed at {offset:#x}")
            struct.pack_into("<I", out, offset, 4 * (3 + hearts))
        data = bytes(out)
    return _splice(data, pushes, after_setup=after_setup, wallet=wallet)


def changes(settings=None) -> FileChanges:
    if settings is None or not (settings.starting_items or settings.starting_hearts or settings.starting_full_wallet):
        return {PATH: patch_sequence}
    actors = items.load()
    pushes = list(START_PUSHES)
    wallet, _ = starting.wallet(settings.starting_items)
    if wallet != "Item_Wallet_Small":
        pushes.append(("Item_Wallet_Small", 1))
    for item in starting.prefixes(settings.starting_items):
        if item in starting.MAP_FLAGS:
            continue
        if item == "Slingshot":
            pushes.append(("Item_BulletBag_Small", 1))
        elif item == "Bow":
            pushes.append(("Item_Quiver_Small", 1))
        pushes.append((actors.actor(item), 1))
    out = {
        PATH: partial(
            patch_sequence,
            pushes=tuple(pushes),
            hearts=settings.starting_hearts,
            wallet=wallet,
            after_setup=True,
        )
    }
    if "Song of Storms" in settings.starting_items:
        out["Event/EventFlow/Npc_Hylia_009_Adult.bfevfl.zs"] = storms_lesson
    return out


def initial_values(settings) -> list[gamedata.FastStartSetting]:
    starting_sword = "Kokiri Sword" in settings.starting_items
    values = {starting.MAP_FLAGS[item]: True for item in settings.starting_items if item in starting.MAP_FLAGS}
    if starting_sword:
        # The native house door treats Sword ownership as a completed Saria greeting.
        # Keep the same skipped-scene state as the explicit Saria option, including its map visit.
        values.update(gamedata.load()["saria"].game_data)
    if settings.starting_full_wallet:
        values["PlayerStatus.CurrentRupee"] = starting.wallet(settings.starting_items)[1]
    if selected := starting.ocarina(settings.starting_items):
        values["PlayerStatus.EquipOcarina"] = selected
    if not values:
        return []
    return [
        gamedata.FastStartSetting(
            name="starting_inventory",
            default=False,
            skips=("Saria's initial greeting; later lessons stay native" if starting_sword else "No story or lesson"),
            state=(
                "Selected native New Game inventory and its implied opening state"
                if starting_sword
                else "Selected native New Game inventory"
            ),
            source="plans/rounds/r20-start.md",
            logic=None,
            game_data=values,
            flow_edits=(),
        )
    ]


def storms_lesson(data: bytes) -> bytes:
    """A prelearned song is not the Windmill's completed teaching encounter."""
    document = evfl.read(data)
    chart = document.flowchart
    if chart is None or chart.name != "Npc_Hylia_009_Adult":
        raise PatchError("start items: expected Windmill adult flow")
    for name in ("Event9", "Event17", "Event31", "Event69"):
        matches = [event for event in chart.events if event.name == name]
        if len(matches) != 1:
            raise PatchError(f"start items: missing Windmill lesson guard {name}")
        event = matches[0]
        if (
            not isinstance(event, evfl.SwitchEvent)
            or chart.actors[event.actor].name != "GameDataActor"
            or chart.actors[event.actor].queries[event.query] != "EventQueryIsGameDataBool"
            or (event.params or {}).get("GameDataName")
            not in ("IsGet.Item_Melody_StormSong", "HavePlayedEvent.Dm_MelodyGet_Storm")
        ):
            raise PatchError(f"start items: changed Windmill lesson guard {event!r}")
        event.params["GameDataName"] = "HavePlayedEvent.Dm_MelodyGet_Storm"
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError("start items: Windmill lesson failed read-back")
    return result
