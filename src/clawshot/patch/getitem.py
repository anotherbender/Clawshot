"""Get-item display: what an item shows in Link's get pose; no inventory or chest-admission policy changes.

The ocarinas' get model (:func:`ocarina_changes`, when the settings could make an ocarina show its own item actor:
:func:`shown_ocarinas_possible`, in a chest, at a show-item hand-over or a scrub sale): the two ``ActorInfo`` rows lose
``CalcPriority`` and each ocarina pack gets the pouch get-pose performer, the common animation set and its own
AnimationParam (plans/chest-ocarina-model.md, run O). Equipment components stay native.

Songs show these ocarinas (:data:`SONG_MODELS`) with an effect of their own: ``clawshot.patch.songs``. The writer
sizes their changed ModelInfo with :func:`member_growth`.
"""

from collections.abc import Callable, Iterable, Mapping
from functools import partial
from pathlib import Path

from clawshot.formats import byml, sarc, zsdic
from clawshot.patch.items import ItemActors
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import actor_path, member_path, resolve_member
from clawshot.world.model import World

ACTOR_INFO = "RSDB/ActorInfo.Product.111.rstbl.byml.zs"
FAIRY = "Item_Ocarina_Fairy"
TIME = "Item_Ocarina_Time"
SONG_MODELS = {
    "Item_Melody_ZeldaLullaby": FAIRY,
    "Item_Melody_EponaSong": FAIRY,
    "Item_Melody_SariaSong": FAIRY,
    "Item_Melody_SunSong": FAIRY,
    "Item_Melody_TimeSong": FAIRY,
    "Item_Melody_StormSong": FAIRY,
    "Item_Melody_ForestMinuet": TIME,
    "Item_Melody_FireBolero": TIME,
    "Item_Melody_WaterSerenade": TIME,
    "Item_Melody_SpiritRequiem": TIME,
    "Item_Melody_ShadowNocturne": TIME,
    "Item_Melody_LightPrelude": TIME,
}
OCARINAS = (FAIRY, TIME)
PERFORMER = "Component/EventPerformerParam/PouchContent.engine__component__EventPerformerParam.bgyml"
COMMON_PERFORMER = "Component/EventPerformerParam/Common.engine__component__EventPerformerParam.bgyml"
# Saria's own ocarina in her farewell (Dm_Kokiri_0155): shares the Fairy Ocarina's model project.
SARIA_PROP = "Dm_Item_Ocarina_Fairy_Saria"
# A native pack holding the PouchContent performer member (its own actor inherits the reference from a $parent).
DONOR = "Item_Boomerang"
ANIMATION_SET = "AS/Item_Common.root.asb"
COMMON_ANIMATION = "Item_Common_Animation"
# What the ocarina get model names; the game loads them from its own romfs. The generator never reads them, so they
# stay out of the app's working set; tests/test_getitem_ocarina_dump.py checks the dump holds them.
OCARINA_DUMP_FILES = (
    ANIMATION_SET + ".zs",
    f"Model/{COMMON_ANIMATION}.anim.bfres.zs",
    *(f"Model/{actor}_Animation.anim.bfres.zs" for actor in (FAIRY, TIME)),
)
MODEL_FIELDS = ("FmdbName", "ModelProjectName", "ModelAabbMin", "ModelAabbMax")


def pack_path(actor: str) -> str:
    return f"Pack/Actor/{actor}.pack.zs"


def _dump(document: byml.Document) -> bytes:
    result = byml.dump(document)
    if difference := byml.difference(document.root, byml.read(result)):
        raise PatchError(f"get-display BYML failed read-back: {difference}")
    return result


def patch_ocarina_actor_info(data: bytes) -> bytes:
    """Drop ``CalcPriority: After`` from the two ocarina rows and give it to :data:`SARIA_PROP`, all found by
    ``__RowId``; nothing else changes.

    Without the instrument's ``After``, Saria's own ocarina (a prop sharing the ``Item_Ocarina_Fairy`` model project)
    is drawn wrong in her farewell until she takes it from her back; with its own ``After`` it is not
    (plans/chest-ocarina-model.md, runs V1-V3). Works on a table earlier steps already grew (custom items, tokens,
    keys): no row order or native snapshot."""
    document = byml.load(data)
    rows = {row.get("__RowId"): row for row in document.root}
    for actor in (*OCARINAS, SARIA_PROP):
        if actor not in rows:
            raise PatchError(f"{actor}: no ActorInfo row")
    for actor in OCARINAS:
        if (value := rows[actor].get("CalcPriority")) != "After":
            raise PatchError(f"{actor}: CalcPriority is {value!r}, not the native 'After'")
    if (value := rows[SARIA_PROP].get("CalcPriority")) is not None:
        raise PatchError(f"{SARIA_PROP}: CalcPriority is {value!r}, not natively absent")
    for actor in OCARINAS:
        del rows[actor]["CalcPriority"]
    rows[SARIA_PROP]["CalcPriority"] = "After"
    return _dump(document)


def animation_member(actor: str) -> str:
    return f"Component/AnimationParam/{actor}.engine__component__AnimationParam.bgyml"


def animation_param(actor: str) -> bytes:
    """The ocarina's own AnimationParam, built from two animation names: the common get-pose set, then the
    ocarina's native (otherwise unreferenced) animation file, which lays it flat like the inventory view."""
    resources = [{"ModelProjectName": name} for name in (COMMON_ANIMATION, f"{actor}_Animation")]
    return byml.write({"AnimationResources": resources})


def patch_ocarina_pack(data: bytes, *, actor: str, donor: bytes) -> bytes:
    """Give an ocarina the pouch get-pose performer and a spinning, flat animation; equipment stays native.

    ``donor`` is the decompressed :data:`DONOR` pack, whose native ``PouchContent`` performer is copied unchanged."""
    if actor not in OCARINAS:
        raise PatchError(f"no ocarina get-model correction for {actor}")
    pack = sarc.read(data)
    param = member_path(actor_path(actor))
    document = byml.load(pack[param])
    components = document.root["Components"]
    if (performer := components.get("EventPerformerRef")) != "?" + COMMON_PERFORMER:
        raise PatchError(f"{actor}: EventPerformerRef is {performer!r}, not the native Common performer")
    for key in ("ASRef", "AnimationRef"):
        if key in components:
            raise PatchError(f"{actor}: already has {key} {components[key]!r}")
    animation = animation_member(actor)
    for member in (PERFORMER, animation):
        if member in pack:
            raise PatchError(f"{actor}: the pack already holds {member}")
    donor_members = sarc.read(donor)
    if PERFORMER not in donor_members:
        raise PatchError(f"{actor}: the donor {DONOR} has no {PERFORMER}")
    components["EventPerformerRef"] = "?" + PERFORMER
    components["ASRef"] = "?" + ANIMATION_SET
    components["AnimationRef"] = "?" + animation
    pack[param] = _dump(document)
    pack[PERFORMER] = donor_members[PERFORMER]
    pack[animation] = animation_param(actor)
    result = sarc.write(pack)
    if sarc.read(result) != pack:
        raise PatchError(f"{actor}: ocarina get-model pack failed read-back")
    return result


def native_inputs() -> tuple[str, ...]:
    """Every romfs file :func:`ocarina_changes` and its transforms read, the dictionaries' pack included, so the
    app's working set (``clawshot.pack.source.working_files``) holds them."""
    return (
        "Pack/ZsDic.pack.zs",
        ACTOR_INFO,
        pack_path(DONOR),
        *(pack_path(actor) for actor in OCARINAS),
    )


def gift_kinds(shuffle: Iterable[str]) -> set[str]:
    """The gift kinds among ``shuffle`` (``Gift`` or one of the types it expands to, ``patch.gifts.GIFT_TYPES``)."""
    from clawshot.patch.gifts import GIFT_TYPES, SHUFFLE

    return set(shuffle) & {SHUFFLE, *GIFT_TYPES}


def chest_ocarinas_possible(shuffle: Iterable[str]) -> bool:
    """Whether the settings could put an ocarina in a chest (Chest and Gift shuffle both on): a seed gets
    :func:`ocarina_changes` exactly then, so the settings string says which build a seed has (PR #41, the
    maintainers' option 2, 2026-11-23). Other seeds keep these files byte-identical to the dump."""
    shuffle = tuple(shuffle)
    return "Chest" in shuffle and bool(gift_kinds(shuffle))


def shown_ocarinas_possible(shuffle: Iterable[str]) -> bool:
    """Whether the settings could make an ocarina show its own item actor: a Gift kind is on, so the ocarinas can
    move, and each of chests (with Chest), show-item hand-overs (the Gift kinds themselves) and scrub sales shows it
    (ocarina-song-drops-everywhere). Wider than :func:`chest_ocarinas_possible`: without the get model an ocarina at a
    hand-over crashed (R11, reproduced on Longshot 3.1.1 in run 4.1), so it is not cosmetic there."""
    return bool(gift_kinds(shuffle))


def chest_ocarinas(placements: Mapping[str, str], chests: Iterable[str], actors: ItemActors) -> list[str]:
    """The chests (in ``chests`` order) whose placed item is an ocarina. ``make_seed`` refuses a seed that has one
    when :func:`chest_ocarinas_possible` says the settings cannot: the chest would show the wrong model."""
    return [name for name in chests if actors.actors.get(placements.get(name, "")) in OCARINAS]


def get_model_ocarinas(placements: Mapping[str, str], world: World, actors: ItemActors) -> list[str]:
    """The locations (in world order) whose grant shows the ocarina's own item actor and that hold an ocarina: chests
    and the show-item hand-overs and scrub sales ``gifts.restrict_spec`` marks (``Location.hand_over``). A seed gets
    :func:`ocarina_changes` only when there is one (O6: without it a hand-over crashed, r11-ocarina.md). Direct
    story grants and GetPouchContent scenes create no item actor; floor and Skulltula pickups show their own."""
    shown = [name for name, location in world.locations.items() if location.type == "Chest" or location.hand_over]
    return chest_ocarinas(placements, shown, actors)


def ocarina_changes(romfs: str | Path) -> dict[str, Callable[[bytes], bytes]]:
    """The chest-ocarina get model: ActorInfo rows and both ocarina packs (``make_seed`` asks
    :func:`chest_ocarinas_possible`).

    Compose last on these files (after ``ocarina.changes``): it checks only the native fields it changes."""
    romfs = Path(romfs)
    donor_path = pack_path(DONOR)
    if not (romfs / donor_path).is_file():
        raise PatchError(f"the dump has no {donor_path}, which the ocarina get model copies from")
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    donor = dictionaries.decompress(donor_path, (romfs / donor_path).read_bytes())
    out: dict[str, Callable[[bytes], bytes]] = {ACTOR_INFO: patch_ocarina_actor_info}
    for actor in OCARINAS:
        out[pack_path(actor)] = partial(patch_ocarina_pack, actor=actor, donor=donor)
    return out


def member_growth(before: bytes, after: bytes) -> dict[str, int]:
    """Retain original parsed overhead for same-shape song model substitutions (``patch.songs``): a song's ModelInfo
    keeps its native entry plus its rounded growth."""
    original, changed = sarc.read(before), sarc.read(after)
    growth = {}
    for actor in SONG_MODELS:
        member = member_path(actor_path(actor))
        if member not in original:
            continue
        components = resolve_member(original, actor_path(actor))["Components"]
        model_member = member_path(components["ModelInfoRef"])
        editable = (model_member,)
        for name in editable:
            if changed.get(name) == original[name]:
                continue
            if name not in changed:
                raise PatchError(f"{name}: missing get-display member")
            old, new = byml.read(original[name]), byml.read(changed[name])
            for field in ("FmdbName", "ModelProjectName"):
                if old.get(field) != "Obj_Rupee" or new.get(field) != SONG_MODELS[actor]:
                    raise PatchError(f"{name}: unsupported model substitution")
                new[field] = old[field]
            if not byml.same(old, new):
                raise PatchError(f"{name}: structural growth needs a measured allocation")
            delta = ((len(changed[name]) + 31) // 32 - (len(original[name]) + 31) // 32) * 32
            if delta > 0:
                growth[name] = delta
    return growth
