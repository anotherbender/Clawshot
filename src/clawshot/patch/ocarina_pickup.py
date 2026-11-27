"""The ocarinas' world actors ``Obj_Clawshot_Ocarina_Fairy`` and ``Obj_Clawshot_Ocarina_Time``
(ocarina-song-drops-everywhere, O7 and plan task 16).

The game's only ocarina world pickup, ``Obj_Ocarina_Time``, floats in the castle moat: its physics are a large dynamic
object's ``Box`` body, which on a floor is an invisible box Link grabs and hangs on (BBender, runs F1, 2026-11-24:
findings F1-a and F1-c). These actors are built instead on ``Obj_Arrow_Fire``, the native free-standing item pickup
the song floor actors use (``songs.pickup_pack``; played at floors, boss hearts and Skulltulas):

- the pack: the arrow's, its ActorParam renamed and pointing at the ocarina (ActorName, the ocarina's ModelInfo
  member, an AnimationParam of its own built in code, a PouchContentParam of its own ``{$parent: the ocarina's,
  PouchActor: the ocarina, GetDemoOffsetPos: the arrow's}``, an ELinkParam of its own naming its glow user); the
  arrow's GameParameterTable, SLink and Capture references dropped; every other member, the pickup body included,
  copied unchanged;
- the glow (BBender, 2026-11-24: a slight floor glow like the songs' light, without sparks or aura, warm white): an
  ELink user per ocarina copied from the heart container, as the song users are, whose floor and get-pose calls play
  only the songs' light clone (``songs.LIGHT``); ``static`` gets the clones from ``songs.patch_static`` when the
  seed's song step does not already add them;
- the rows: the arrow's ``ActorInfo`` row with the ocarina's model fields, ``ActorName``, animations and glow user;
  the arrow's ``GameActorInfo`` row; the ocarina's ``PouchActorInfo`` row without ``OcarinaTypeValue`` (as the
  native ``Obj_Ocarina_Time`` row is ``Item_Ocarina_Time``'s without it; keeping it did not make the picked-up
  ocarina playable, run G1t).

One actor per ocarina serves the boss heart and free-standing floors and the Skulltula drop (as the Token donor; the
native ``Obj_Ocarina_Time`` donor left the Fairy as the instrument until a reload, run TB3). A seed gets them only
when the settings could place that ocarina where one is needed (:func:`pickups_for`).
"""

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from clawshot.formats import byml, elink, evfl, sarc, zsdic
from clawshot.patch import bags, getitem, keys, songs
from clawshot.patch.items import ItemActors
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import actor_path, member_path
from clawshot.patch.songs import PICKUP_DONOR, PICKUP_DROPPED, _insert, _need, _rows, elink_member
from clawshot.patch.write import FileChanges, NewFile
from clawshot.world.model import World

FAIRY = getitem.FAIRY
TIME = getitem.TIME
PICKUPS = {FAIRY: "Obj_Clawshot_Ocarina_Fairy", TIME: "Obj_Clawshot_Ocarina_Time"}
PICKUP = PICKUPS[FAIRY]  # the Fairy's, also its Skulltula donor
ACTOR_INFO = getitem.ACTOR_INFO
GAME_ACTOR_INFO = "RSDB/GameActorInfo.Product.111.rstbl.byml.zs"
POUCH_ACTOR_INFO = "RSDB/PouchActorInfo.Product.111.rstbl.byml.zs"
POUCH_ROW_DROPPED = "OcarinaTypeValue"
FLOOR_KINDS = ("BossHeart", "Freestanding")
# Fairy's Freestanding first acquisition failed; BossHeart retains the Gohma PASS. Token awaits d-prime's ruling.
KINDS = {FAIRY: ("Token", "BossHeart"), TIME: ("Token", *FLOOR_KINDS)}
DROPPED = PICKUP_DROPPED
ROW_DROPPED = ("SLinkUserName",)
USERS = {FAIRY: "Clawshot_Ocarina_Fairy", TIME: "Clawshot_Ocarina_Time"}  # the glow's ELink users
# The glow: the songs' light clone alone, sized as Prelude of Light's floor light (song_effects.toml, played), in warm
# white (BBender, 2026-11-24). At Prelude's -0.15 m it lit the ocarina harshly from close below (BBender, run TG1), so
# it sits at the floor the pickup was lifted from (drops.FLOOR_LIFT) to light the ground, and the get pose has none.
GLOW_COLOUR = (0.6, 0.55, 0.45)
GLOW_HEIGHT = -0.3
GLOW = {
    "RuntimeAssetName": songs.LIGHT,
    "PositionX": 0.0,
    "PositionZ": 0.0,
    "RotationX": -1.5708,
    "Scale": 0.6,
    "LifeScale": 0.5,
    "PositionY": GLOW_HEIGHT,
    "Red": GLOW_COLOUR[0],
    "Green": GLOW_COLOUR[1],
    "Blue": GLOW_COLOUR[2],
}
GET_POSE_GLOW = {**GLOW, "Red": 0.0, "Green": 0.0, "Blue": 0.0}  # no light while held up


def pack_path(actor: str) -> str:
    return getitem.pack_path(actor)


def _ref_member(ref: str) -> str:
    return member_path(ref.removeprefix("?"))


def pickup_pack(ocarina: str, *, arrow: bytes, ocarina_pack: bytes) -> NewFile:
    """``PICKUPS[ocarina]``'s pack from ``Obj_Arrow_Fire``'s (``arrow``) and the ocarina's own (``ocarina_pack``),
    both decompressed."""
    if ocarina not in PICKUPS:
        raise PatchError(f"{ocarina}: not an ocarina with a world pickup")
    pickup = PICKUPS[ocarina]
    donor = sarc.read(arrow)
    old_param = member_path(actor_path(PICKUP_DONOR))
    if old_param not in donor:
        raise PatchError(f"{PICKUP_DONOR}: the pack has no {old_param}")
    members = sarc.read(ocarina_pack)
    own_param = member_path(actor_path(ocarina))
    if own_param not in members:
        raise PatchError(f"{ocarina}: the pack has no {own_param}")
    own = byml.read(members[own_param])["Components"]
    model_member, pouch_parent = _ref_member(own["ModelInfoRef"]), _ref_member(own["PouchContentRef"])
    for member in (model_member, pouch_parent):
        if member not in members:
            raise PatchError(f"{ocarina}: {member!r} is not a member of its pack")
    pack = dict(donor)
    document = byml.load(pack.pop(old_param))
    components = document.root["Components"]
    for key in ("ModelInfoRef", "PouchContentRef", "AnimationRef"):
        if key not in components:
            raise PatchError(f"{PICKUP_DONOR}: its ActorParam has no {key}")
    donor_pouch = byml.read(donor[_ref_member(components["PouchContentRef"])])
    if "GetDemoOffsetPos" not in donor_pouch:
        raise PatchError(f"{PICKUP_DONOR}: its pouch component has no GetDemoOffsetPos")
    for key in DROPPED:
        components.pop(key, None)
    param, animation = member_path(actor_path(pickup)), getitem.animation_member(pickup)
    pouch = f"Component/PouchContentParam/{pickup}.game__component__PouchContentParam.bgyml"
    link = elink_member(pickup)
    for member in (param, animation, pouch, link, model_member, pouch_parent):
        if member in pack:
            raise PatchError(f"{PICKUP_DONOR}: the pack already holds {member}")
    components["ActorNameRef"] = f"?ActorSystem/ActorName/{ocarina}.engine__actor__ActorName.bgyml"
    components["ModelInfoRef"] = "?" + model_member
    components["AnimationRef"] = "?" + animation
    components["PouchContentRef"] = "?" + pouch
    components["ELinkRef"] = "?" + link
    pack[link] = byml.write({"UserName": USERS[ocarina]})
    pack[model_member] = members[model_member]
    pack[pouch_parent] = members[pouch_parent]
    pack[animation] = getitem.animation_param(ocarina)
    pack[pouch] = byml.write(
        {
            "$parent": "Work/" + pouch_parent.replace(".bgyml", ".gyml"),
            "GetDemoOffsetPos": donor_pouch["GetDemoOffsetPos"],
            "PouchActor": actor_path(ocarina),
        }
    )
    pack[param] = byml.dump(document)
    data = sarc.write(pack)
    if sarc.read(data) != pack:
        raise PatchError(f"{pickup}: the pickup pack does not read back")
    copied = {name: pack_path(PICKUP_DONOR) for name in donor if name != old_param}
    copied[model_member] = copied[pouch_parent] = pack_path(ocarina)
    return NewFile(data, copied=copied)


def patch_actor_info(data: bytes, ocarinas: Iterable[str] = tuple(PICKUPS)) -> bytes:
    """Insert ``Obj_Arrow_Fire``'s row as each pickup's, with the ocarina's model fields, ``ActorName`` and
    animations and glow user (no SLink user); heaps stay the arrow's. Works on a table earlier steps changed."""
    document, rows = _rows(data, ACTOR_INFO)
    ocarinas = list(ocarinas)
    _need(rows, ACTOR_INFO, PICKUP_DONOR, *ocarinas)
    new = []
    for ocarina in ocarinas:
        pickup = {k: copy.deepcopy(v) for k, v in rows[PICKUP_DONOR].items() if k not in ROW_DROPPED}
        pickup["__RowId"] = PICKUPS[ocarina]
        for field in getitem.MODEL_FIELDS:
            pickup[field] = copy.deepcopy(rows[ocarina][field])
        pickup["ActorName"] = ocarina
        pickup["ELinkUserName"] = USERS[ocarina]
        pickup["AnimationResources"] = byml.read(getitem.animation_param(ocarina))["AnimationResources"]
        new.append(pickup)
    return _insert(document, ACTOR_INFO, new)


def patch_game_actor_info(data: bytes, ocarinas: Iterable[str] = tuple(PICKUPS)) -> bytes:
    """Insert ``Obj_Arrow_Fire``'s row (world behaviour), renamed, for each pickup."""
    document, rows = _rows(data, GAME_ACTOR_INFO)
    _need(rows, GAME_ACTOR_INFO, PICKUP_DONOR)
    new = [{**copy.deepcopy(rows[PICKUP_DONOR]), "__RowId": PICKUPS[ocarina]} for ocarina in ocarinas]
    return _insert(document, GAME_ACTOR_INFO, new)


def patch_pouch_actor_info(data: bytes, ocarinas: Iterable[str] = tuple(PICKUPS)) -> bytes:
    """Insert each ocarina's row, renamed and without ``OcarinaTypeValue``."""
    document, rows = _rows(data, POUCH_ACTOR_INFO)
    ocarinas = list(ocarinas)
    _need(rows, POUCH_ACTOR_INFO, *ocarinas)
    new = []
    for ocarina in ocarinas:
        pickup = {k: copy.deepcopy(v) for k, v in rows[ocarina].items() if k != POUCH_ROW_DROPPED}
        new.append({**pickup, "__RowId": PICKUPS[ocarina]})
    return _insert(document, POUCH_ACTOR_INFO, new)


def patch_elink(data: bytes, ocarinas: Iterable[str] = tuple(PICKUPS), *, effects: songs.SongEffects) -> bytes:
    """The ``.110`` ELink table with each ocarina's glow user: the heart container's user copied (as the song users
    are), its ``Wait`` (floor) call a container of :data:`GLOW` alone and its ``GetDemo`` call one of the unlit
    :data:`GET_POSE_GLOW`, under the songs' floor and get-pose conditions. Every other user decodes as before."""
    ocarinas = [o for o in PICKUPS if o in set(ocarinas)]
    try:
        table = elink.decode(data)
        for ocarina in ocarinas:
            if table.has_user(USERS[ocarina]):
                raise PatchError(f"{songs.ELINK}: already has the user {USERS[ocarina]}")
            table.add_user_copy(songs.EFFECT_DONOR, USERS[ocarina])
        for ocarina in ocarinas:
            for key in ("Wait", "GetDemo"):  # the child copies these records: bone Root
                table.set_call_params(USERS[ocarina], key, {"RuntimeAssetName": songs.CHARGE, "Bone": "Root"})
        for ocarina in ocarinas:
            table.make_container(USERS[ocarina], "GetDemo", [dict(GET_POSE_GLOW)], effects.get_pose_condition)
            table.make_container(USERS[ocarina], "Wait", [dict(GLOW)], effects.floor_condition)
        out = table.encode()
        again = elink.decode(out)
    except elink.ElinkError as error:
        raise PatchError(f"{songs.ELINK}: {error}") from error
    if again.encode() != out or sorted(again.user_names()) != sorted(table.user_names()):
        raise PatchError(f"{songs.ELINK}: the ocarina glow users do not read back")
    return out


@dataclass(frozen=True)
class Delivery:
    """``changes`` (the three tables) for the common writer's ``extra_changes`` and ``new_files`` (the packs)."""

    changes: FileChanges
    new_files: Mapping[str, NewFile]


def pickups_for(shuffle: Iterable[str]) -> list[str]:
    """Native ocarina identities whose world actors the settings can need, in stable policy order.

    Keep PR #41's settings-selected rule: a Gift kind plus an admitted destination, not actual placements.
    A Freestanding-only recipe builds Time, while BossHeart can still build Fairy.
    """
    shuffle = set(shuffle)
    if not getitem.gift_kinds(shuffle):
        return []
    return [ocarina for ocarina, kinds in KINDS.items() if shuffle.intersection(kinds)]


def needed(placements: Mapping[str, str], world: World, actors: ItemActors) -> list[str]:
    """The ocarinas (in :data:`PICKUPS` order) whose world actor this seed needs: one placed at a kind of
    :data:`KINDS`. A seed gets :func:`build` only when the list is not empty."""
    found = {
        actors.actors.get(placements.get(name, ""))
        for name, location in world.locations.items()
        if location.type in KINDS.get(actors.actors.get(placements.get(name, ""), ""), ())
    }
    return [ocarina for ocarina in PICKUPS if ocarina in found]


def native_inputs() -> tuple[str, ...]:
    """Every romfs file :func:`build` and its transforms read, the dictionaries' pack included."""
    return (
        zsdic.PACK_PATH,
        ACTOR_INFO,
        GAME_ACTOR_INFO,
        POUCH_ACTOR_INFO,
        songs.ELINK,
        songs.STATIC,
        pack_path(PICKUP_DONOR),
        *(pack_path(ocarina) for ocarina in PICKUPS),
    )


def build(romfs: str | Path, ocarinas: Iterable[str], *, with_static: bool = True) -> Delivery:
    """The pickup packs of ``ocarinas`` as new files, the three table changes and the glow (the ELink table, and
    ``static``'s light clone unless ``with_static`` is false because the seed's song step adds it). Raises
    :class:`PatchError` when a native input is missing or a pack already exists."""
    romfs, ocarinas = Path(romfs), [o for o in PICKUPS if o in set(ocarinas)]
    if not ocarinas:
        raise PatchError("no ocarina pickup to build")
    for path in native_inputs():
        if not (romfs / path).is_file():
            raise PatchError(f"the dump has no {path}, which the ocarina pickups read")
    for ocarina in ocarinas:
        if (romfs / pack_path(PICKUPS[ocarina])).exists():
            raise PatchError(f"the dump already has {pack_path(PICKUPS[ocarina])}")
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def read(path: str) -> bytes:
        return dictionaries.decompress(path, (romfs / path).read_bytes())

    arrow = read(pack_path(PICKUP_DONOR))
    packs = {pack_path(PICKUPS[o]): pickup_pack(o, arrow=arrow, ocarina_pack=read(pack_path(o))) for o in ocarinas}

    def actor_info(data: bytes) -> bytes:
        return patch_actor_info(data, ocarinas)

    def game_actor_info(data: bytes) -> bytes:
        return patch_game_actor_info(data, ocarinas)

    def pouch_actor_info(data: bytes) -> bytes:
        return patch_pouch_actor_info(data, ocarinas)

    try:
        effects = songs.load_effects()
    except songs.SongEffectsError as error:
        raise PatchError(f"{songs.EFFECTS_TOML.name}: {error}") from error

    def glow(data: bytes) -> bytes:
        return patch_elink(data, ocarinas, effects=effects)

    changes = {
        ACTOR_INFO: actor_info,
        GAME_ACTOR_INFO: game_actor_info,
        POUCH_ACTOR_INFO: pouch_actor_info,
        songs.ELINK: glow,
    }
    if with_static:
        changes[songs.STATIC] = partial(songs.patch_static, effects=effects)
    return Delivery(changes, packs)


# ---------------------------------------------------------------------------------------------------------------
# The receipt (plan 17, finding T1-a)

RECEIPT_FLOWS = ("Dm_SY_Get", "Dm_SY_Get_WithoutPlayer")
RECEIPT_PREFIX = "ClawshotOcarinaReceipt_"
_OWN_ADD = ("PouchContentGuestPerformer", "EventTriggerAddOwnToPouch")


def patch_receipt(chart: evfl.Flowchart) -> None:
    """After the pickup's own add, an ocarina (the message target its ``EventTriggerSetOwnNameToMessage`` just set) is
    added again by name, as every grant that plays at once adds it and as the native moat pickup's movie does
    (``Dm_MelodyGet_Time``). A world pickup grants only through ``EventTriggerAddOwnToPouch``, which left the instrument
    owned and shown but unplayable until a reload (BBender, runs T1, F1, G1s, 2026-11-24). Other pickups run as
    before."""
    if any(event.name.startswith(RECEIPT_PREFIX) for event in chart.events):
        raise PatchError(f"{chart.name}: ocarina receipt already patched")
    adds = [
        index
        for index, event in enumerate(chart.events)
        if isinstance(event, evfl.ActionEvent)
        and (chart.actors[event.actor].name, chart.actors[event.actor].actions[event.action]) == _OWN_ADD
    ]
    if len(adds) != 1:
        raise PatchError(f"{chart.name}: expected one {_OWN_ADD[1]}, found {len(adds)}")
    own = chart.events[adds[0]]
    onward = own.next
    # The native no-player flow has no GameDataActor until the receipt needs its identity query.
    if not any(actor.name == "GameDataActor" for actor in chart.actors):
        chart.actors.append(evfl.Actor("GameDataActor"))
    game, is_string = keys._operation(chart, "GameDataActor", "queries", "EventQueryIsGameDataString64")
    pouch, add = keys._operation(chart, "PouchSystemActor", "actions", "EventTriggerAddOrRemovePouchContent")
    test = onward
    for ocarina in reversed(tuple(PICKUPS)):
        grant = len(chart.events)
        chart.events.append(
            evfl.ActionEvent(
                RECEIPT_PREFIX + ocarina,
                pouch,
                add,
                onward,
                {
                    "Actor": ocarina,
                    "Num": 1,
                    "IsEquipDIrect": False,
                    "IsSetMessageTargetActorName": True,
                    "IsGetEvent": False,
                },
            )
        )
        chart.events.append(
            evfl.SwitchEvent(
                RECEIPT_PREFIX + "Is" + ocarina,
                game,
                is_string,
                [(0, grant), (1, test)],
                {"GameDataName": bags.MESSAGE_TARGET, "Index": -1, "Value": ocarina},
            )
        )
        test = len(chart.events) - 1
    own.next = test


def receipt_changes(romfs: str | Path) -> FileChanges:
    """Patch both normal and camera-obstructed world receipts, preserving their native presentation and cleanup.

    Compose before ``ocarina.changes``, which keeps Time selected after either flow's added Fairy grant.
    """
    romfs = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    changes = {}
    for name in RECEIPT_FLOWS:
        path = keys.flow_path(name)
        if not (romfs / path).is_file():
            raise PatchError(f"the dump has no {path}, which the ocarina receipt patches")
        original = evfl.read(dictionaries.decompress(path, (romfs / path).read_bytes()))
        if original.flowchart is None:
            raise PatchError(f"{path}: not a flowchart")
        changed = copy.deepcopy(original)
        patch_receipt(changed.flowchart)
        encoded = evfl.write(changed)
        if evfl.read(encoded) != changed:
            raise PatchError(f"{path}: the ocarina receipt does not read back")

        # Bind each flow's source and output independently, not the loop's final values.
        def transform(data: bytes, *, expected=original, replacement=encoded, source=path) -> bytes:
            if evfl.read(data) != expected:
                raise PatchError(f"{source}: the ocarina receipt source changed after binding")
            return replacement

        changes[path] = transform
    return changes
