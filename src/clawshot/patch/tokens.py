"""Gold Skulltula reward delivery and the Token shuffle writer (``plans/rounds/r15-tokens-spec.md``; sections 9 and 10
first).

Clean room: built only from the accepted specification, this repository and the player's dump. The independent
gameplay lead is ootrr (REALAZK); no source was copied.

A Skulltula keeps everything native: its drop table, lifecycle, permanent Hash on every age/Alternative copy,
appearance, links, groups, and the global ``Obj_Token_Gold`` pack (``AI.Global`` is not touched). A token assignment
changes nothing. A non-token reward changes only the instance ``Dynamic.Drop__DropActor`` of the source's copies, which
names a generated pickup actor made of:

- the token mechanism, byte-identical from ``Obj_Token_Gold`` (section 10.3): its AI graph (only death reason 10 runs
  the callback that saves the nonzero source Hash H and H xor 2), its blackboard (``GoldTokenGmdHash``, which the
  enemy's utility graph overwrites with its no-respawn Hash, and ``IsEnableAttention`` true), its death procedures
  (``PickedUp`` waits for that callback's signal), and its physics (the graph asks for controller ``Body``, rigid body
  ``Body``), attention, lift, position and life components;
- the reward's identity, from its native actor: canonical ``ActorName``, pouch component (grant identity, category,
  get type, special deal), model and animations, plus the world display of its native world pickup
  (``Obj_Shield_Hylian``) or, for an inventory-only reward (``Item_Boomerang``), of the native generic item pickups
  (``Item_Obj`` over ``Item_Common``, no effect/sound user, as ``Obj_Ocarina_Time``);
- the pickup policy :data:`POLICY`: touch collection, and get events for repeated and full-pouch acquisitions
  (section 10.3; 44 native pouch components set ``IsPlayGetEventPouchMax`` as a top-level Bool). A reward's own pouch
  component that lacks any of it gets a pouch component of its own deriving from the native one, as ``Obj_Bombchu``
  derives from ``Item_Bombchu``. Where the native component names no ``PouchActor`` (an actor granting its own
  identity), that component names the reward's canonical ``ActorName``: each of the 138 such native actors whose
  canonical name differs from its row (``Item_HeavyBoot`` -> ``Armor_Adult_HeavyBoot``) has an ``IsGet`` record under
  its canonical name only, and the played ``Item_Boomerang`` and ``Obj_Shield_Hylian`` name their canonical actors.
  A bundle (``Obj_Rupee_Red``: 20 of ``Obj_Rupee_Green``) naming none keeps naming none: no native bundle names an
  actor other than its own ``BundleActor``, and the 35 that name none include ``TBox_Rupee_Red``, whose canonical
  ``Obj_Rupee_Red`` alone has the ``IsGet`` record, as the pickup's canonical name does.

Registration: one new row each in ``ActorInfo`` and ``GameActorInfo`` at the same sorted index, and one in
``PouchActorInfo`` (385 of the 391 concrete native pouch actors have one); no existing row changes. Saved records stay
those of the granted item (``IsGet.Item_Boomerang``, ...), as for native world pickups. The pack, and each member new
to the game, get size entries from formulas measured on every native file of their type (:mod:`clawshot.formats.rstb`).

``RSDB/Tag`` stays unchanged (section 10.1): it gives ``Token_Gold`` only to ``Obj_Token_Gold``; the native pouch event
uses that tag to choose token-specific Navi advice, both tagged and untagged ordinary get paths reach the same pouch
grant, and the reason-10 completion, Hash transfer and callback do not query it. Generated pickups get no Tag entry,
so token first-pickup advice is not expected from them. Deeper engine code was not exhaustively audited.

Which rewards may stand at a source: a grant family (:data:`FAMILIES`) is a native ``PouchActorInfo`` shape, read from
the dump for every placed actor; :func:`build` takes the explicit allowed set (actor -> family). Production Token
seeds (:func:`seed_delivery`) pass only the members ``clawshot.generate.tokens`` admits; diagnostics pass their own,
from every family of the approved table that is not bought goods. A shape fixes the pouch semantics only: a pickup
keeps the token's event performer, so a family whose natives use another (heart pieces and containers: Utuwa) is a
substitution its own play must prove.

Played evidence (Kareem, Longshot v3.0.0-rc.3, 2026-11-14, Phase 1 core packet; ``rounds/r15-scrub-tokens.md``):
Longshot loaded both new pickup packs from the mod; an uncollected ``Item_Boomerang`` pickup at LLR GS Tree recovered
after leaving and after reload, then granted a usable Boomerang with token stock unchanged and the source completed;
the ``Obj_Shield_Hylian`` pickup at LLR GS Tower granted the shield from the high source without a token; the native
Lone Tree token and a token in KF Storms Grotto Chest each added one token; Save and Continue kept every grant and
completion. That proves these two generated pickups and the native token paths, not every member of their families:
each further member rests on this module's structural checks until its own play.
"""

import copy
import hashlib
from bisect import bisect_left
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path, PurePosixPath

from clawshot.census.definitions import Definition
from clawshot.census.scan import GAME_DATA_LIST, GOLD_SKULLTULA, Location
from clawshot.formats import byml, sarc, zsdic
from clawshot.patch import actor_packs
from clawshot.patch.actor_packs import actor_member, component_ref, reference, work_path
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges, NewFile

ENEMY = "Enemy_Skulltula_Gold"
TOKEN = "Obj_Token_Gold"  # the native world token the enemy's drop table creates
TOKEN_ITEM = "Item_Token_Gold"  # its inventory item: a token assignment keeps the native drop
ITEM_BASE = "Obj_Item_Base"
DROP = "Drop__DropActor"
DROP_FIELDS = "Drop__"  # Drop__DropActor, Drop__DropTable: a native source sets none of them


def pack_path(actor: str) -> str:
    return f"Pack/Actor/{actor}.pack.zs"


ENEMY_PACK = pack_path(ENEMY)
TOKEN_PACK = pack_path(TOKEN)
ACTOR_INFO = "RSDB/ActorInfo.Product.111.rstbl.byml.zs"
GAME_ACTOR_INFO = "RSDB/GameActorInfo.Product.111.rstbl.byml.zs"
POUCH_ACTOR_INFO = "RSDB/PouchActorInfo.Product.111.rstbl.byml.zs"
REGISTRIES = (ACTOR_INFO, GAME_ACTOR_INFO, POUCH_ACTOR_INFO)

GENERIC_DISPLAY = "Obj_Shield_Hylian"  # holds the generic item pickups' Item_Obj AS info
PICKUP_PREFIX = "Obj_GoldSkulltulaDrop_"


@dataclass(frozen=True)
class Family:
    """A native grant shape over a ``PouchActorInfo`` row: every ``fields`` entry has one of its values, every
    ``required`` field is set, at least one ``any_of`` field is set, and no ``unset`` field is
    (absent, false or zero)."""

    fields: Mapping[str, frozenset]
    required: tuple[str, ...] = ()
    any_of: tuple[str, ...] = ()
    unset: tuple[str, ...] = ()

    def matches(self, row: Mapping) -> bool:
        return (
            all(row.get(field) in values for field, values in self.fields.items())
            and all(row.get(field) for field in self.required)
            and (not self.any_of or any(row.get(field) for field in self.any_of))
            and not any(row.get(field) for field in self.unset)
        )


def _shape(tab: str | frozenset, category: str | frozenset, get: str | frozenset, deal: str, **fields) -> dict:
    """The four pouch classification fields every family states, plus any further exact values."""
    values = {"PouchTabCategory": tab, "PouchCategory": category, "PouchGetType": get, "PouchSpecialDeal": deal}
    return {
        key: value if isinstance(value, frozenset) else frozenset({value})
        for key, value in {**values, **fields}.items()
    }


# Fields that make a grant more than one owned thing: bundles, stock, caps, capacity or magic side effects, contents.
SINGLE_GRANT_UNSET = (
    "BundleActor",
    "PouchStockable",
    "FixedMaxNum",
    "ExpansionAvility",
    "ExpansionMaxNumActor",
    "SmallBagActor",
    "MaxNumGameData",
    "BottleItem",
    "MPMax",
)
# A bundle of stock (ammo, chus): N of its BundleActor, and nothing it owns, caps, expands, assigns or fills.
BUNDLE_UNSET = (
    "PouchStockable",
    "FixedMaxNum",
    "AssignableItem",
    "ExpansionAvility",
    "ExpansionMaxNumActor",
    "SmallBagActor",
    "MPMax",
    "BottleItem",
)
# Grant families by native pouch semantics (build e0f3ccfa), never by actor-name pattern; the shapes are disjoint over
# all 391 native rows. Which members a seed may place is clawshot.generate.tokens' policy; a family here only states
# the shape the dump must show. "token" is the native source drop itself. Claude's approved family table (Round 15,
# 2026-11-14) gives one family per distinct native grant: every family after "equipment" exists for explicit
# diagnostics and is never admitted by production policy before its representative plays. Bought goods (existing-
# bottle contents, Buy Heart) have no family: they stay on shop shelves. Shape is not the whole grant path: every
# pickup keeps the token's event performer (PouchContent_PickUpItem), where native heart pieces and containers use
# PouchContentUtuwa, native rupees PouchContent_PickUpItem_EnableWarp and the Item_ ocarinas Common.
FAMILIES = {
    "token": Family(_shape("KeyItem", "KeyItem", "Medium", "TokenGold", PouchStockable=True), ("FixedMaxNum",)),
    "fixed_major": Family(
        _shape("Item", "Material", "Large", "None", BundleActorNum=1), ("AssignableItem",), unset=SINGLE_GRANT_UNSET
    ),
    "equipment": Family(
        _shape("Equipment", frozenset({"Shield", "Weapon", "Boot", "Armor"}), "Large", "None", BundleActorNum=1),
        any_of=("AdultEquipment", "ChildEquipment"),
        unset=SINGLE_GRANT_UNSET,
    ),
    # Green 1 (stock, wallet cap) and Blue/Red/Purple bundles of 5/20/50 Green; the wallet clamps.
    "rupee": Family(_shape("KeyItem", "Rupee", "Small", "None")),
    "gold_rupee": Family(_shape("KeyItem", "Rupee", "Medium", "None"), ("BundleActor",)),  # 200, a Medium get
    "heart_piece": Family(_shape("KeyItem", "KeyItem", "Medium", "HeartPiece", PouchStockable=True)),
    "heart_container": Family(_shape("KeyItem", "KeyItem", "Heart", "HeartContainer", PouchStockable=True)),
    # A new bottle, empty or with its BottleItem content (Milk: MaxMilk); never a refill of an owned bottle.
    "bottle": Family(_shape("Item", "Material", "Large", "Bottle", BundleActorNum=1), ("AssignableItem",)),
    # Small ammo bundles (arrows, bombs, nuts, sticks, seeds); their bag rules stay the native pouch's.
    "refill": Family(
        _shape(frozenset({"Equipment", "Item"}), frozenset({"Arrow", "Material"}), "Small", "None"),
        ("BundleActor",),
        unset=BUNDLE_UNSET,
    ),
    "bombchu": Family(_shape("Item", "Material", "Large", "None"), ("BundleActor",), unset=BUNDLE_UNSET),
    # A fixed capacity tier: AfterExpansionMaxNum of ExpansionMaxNumActor's stock (MaxNumGameData).
    "fixed_capacity": Family(
        _shape("KeyItem", "KeyItem", "Large", "None", BundleActorNum=1),
        ("ExpansionMaxNumActor", "AfterExpansionMaxNum", "MaxNumGameData"),
        unset=("BundleActor", "PouchStockable", "FixedMaxNum", "ExpansionAvility", "SmallBagActor", "MPMax"),
    ),
    # Restores MPRecover magic; not pushed to the pouch.
    "magic_recovery": Family(_shape("Item", "CureItem", "Small", "NotPushToPouch", IsUsable=True), ("MPRecover",)),
    # An assignable spell or magic arrow that also raises the magic meter to MPMax (MPMaxUP).
    "spell": Family(
        _shape("Item", "Material", "Heart", "None", ExpansionAvility="MPMaxUP"), ("MPMax", "AssignableItem")
    ),
    "magic_arrow": Family(
        _shape("Item", "Bow", "Large", "None", ExpansionAvility="MPMaxUP", WeaponType="Bow"),
        ("MPMax", "AssignableItem", "ShootableActor"),
    ),
    "lens": Family(
        _shape("Equipment", "HeadArmor", "Large", "GlassTruth", ExpansionAvility="MPMaxUP"),
        ("MPMax", "AdultEquipment", "ChildEquipment"),
    ),
    "agony_stone": Family(_shape("Equipment", "KeyItem", "Large", "AgonyStone"), ("AdultEquipment", "ChildEquipment")),
    "double_defense": Family(_shape("KeyItem", "KeyItem", "Heart", "FairyBlessDefenseDouble")),
    # Capped stock that is not a bundle (Scrub Business Seed, FixedMaxNum 30).
    "scrub_seed": Family(
        _shape("Item", "Material", "Small", "None", PouchStockable=True),
        ("FixedMaxNum",),
        unset=("BundleActor", "SmallBagActor", "MaxNumGameData", "ExpansionMaxNumActor", "MPMax", "BottleItem"),
    ),
    # Only a donor that carries its own AnimationRef composes: Obj_Ocarina_Time, not the Item_ ocarinas.
    "ocarina": Family(_shape("KeyItem", "KeyItem", frozenset({"Small", "Large"}), "Ocarina")),
}


def grant_family(row: Mapping) -> str | None:
    """The one :data:`FAMILIES` shape a native ``PouchActorInfo`` row has, or None."""
    found = [name for name, family in FAMILIES.items() if family.matches(row)]
    if len(found) > 1:
        raise PatchError(f"PouchActorInfo {row.get('__RowId')}: matches several grant families {found}: {row!r}")
    return found[0] if found else None


# The graphs whose behaviour the accepted specification establishes (N1/N8). Their bytes are pinned, not parsed.
TOKEN_GRAPH = "AI/Item_Token_Gold.root.ainb"
TOKEN_GRAPH_SHA256 = "772aef26355f2998b0ba8afac3e6da43bccbb13303acd0e12d3eb365911c3fb7"
ENEMY_GRAPH = "AI/Enemy_Skulltula_Gold.utility.root.ainb"
ENEMY_GRAPH_SHA256 = "4c621fa4c247f8054f6239c8cc8497bd4bd719c2cf2dee6d27848ba6f4fddc9f"
SOURCE_HASH_KEY = "GoldTokenGmdHash"
COMPANION_XOR = 2  # the callback saves H and H xor 2
PERMANENT, SAVE_FILE = 24, 0

DEATH_TABLE_TYPE = "Work/System/CombinationDataTable/game__death__DeathReasonProcedures.pp__CombinationDataTable.gyml"
DEATH_DEFAULT = "Component/DeathParam/Default.game__component__DeathParam.bgyml"  # built in: no file in the game
POUCH_DEFAULT = "Component/PouchContentParam/Default.game__component__PouchContentParam.bgyml"  # built in
NO_RESPAWN = "Component/ActorGameDataSetting/NoRespawn.game__component__ActorGameDataSetting.bgyml"
TOKEN_DROP_TABLE = "Work/Drop/DropTable/DropTable_Token_Gold.game__drop__DropTable.gyml"


def death_table(name: str) -> str:
    return (
        f"System/CombinationDataTableData/{name}_game__death__DeathReasonProcedures.pp__CombinationDataTableData.bgyml"
    )


# Every romfs file build() reads whatever it delivers, the dictionaries' pack included; a generator working set must
# hold them all, plus each reward's own pack (:func:`native_inputs`). The source placement files are read later, by
# the writer, and are already in every working set.
NATIVE_INPUTS = (
    "Pack/ZsDic.pack.zs",
    GAME_DATA_LIST,
    ENEMY_PACK,
    death_table(ENEMY),
    death_table("EnemyCommon"),
    death_table("Default"),
    TOKEN_PACK,
    death_table(TOKEN_ITEM),
    death_table("Default_AlwaysRespawn"),
    *REGISTRIES,
    pack_path(GENERIC_DISPLAY),
)


def native_inputs(rewards: Iterable[str]) -> tuple[str, ...]:
    """Every romfs file build() may read for these reward actors (a token keeps the native drop: no pack of its own)."""
    packs = {pack_path(actor) for actor in rewards if actor != TOKEN_ITEM} - set(NATIVE_INPUTS)
    return (*NATIVE_INPUTS, *sorted(packs))


IDENTITY = ("ActorNameRef", "PouchContentRef", "ModelInfoRef", "AnimationRef")
WORLD_DISPLAY = ("ASInfoRef", "ASRef", "ELinkRef", "SLinkRef", "GameParameterTableRef")
GENERIC_WORLD_DISPLAY = ("ASInfoRef", "ASRef")
# Touch collection, and get events for repeated and full-pouch acquisitions (section 10.3).
POLICY = {"DefaultAutoGet": True, "PlayGetEventManyTimes": True, "IsPlayGetEventPouchMax": True}
GRANT_KEY = "PouchActor"  # the inventory actor a pouch component grants (see pouch_grant)
BUNDLE_KEY = "IsBundle"  # a bundle grants BundleActorNum of its BundleActor
ATTENTION_KEY = "IsEnableAttention"
PHYSICS_BODY = "Body"  # the token graph asks for controller Body and rigid body Body (section 10.3)
ROW_DISPLAY = ("ActorName", "AnimationResources", "FmdbName", "ModelProjectName", "ModelAabbMin", "ModelAabbMax")
LINK_USERS = (("ELinkRef", "ELinkUserName"), ("SLinkRef", "SLinkUserName"))


@dataclass(frozen=True)
class Delivery:
    """``changes`` for the common writer's ``extra_changes`` and ``new_files`` for its ``new_files``."""

    changes: FileChanges
    new_files: Mapping[str, NewFile]  # generated pickup pack path -> its pack, in reward order
    pickups: Mapping[str, str]  # reward item -> generated pickup actor
    drops: Mapping[int, str]  # Skulltula Hash -> the pickup it now drops (token sources are absent: native)
    inputs: tuple[str, ...]  # romfs files read, in order


@dataclass(frozen=True)
class Pickup:
    item: str
    actor: str
    file: NewFile
    rows: Mapping[str, dict]  # registry path -> its new row


def pickup_name(item: str) -> str:
    return PICKUP_PREFIX + item


class Romfs:
    """Read-only, cached access to the player's dump; a missing file names itself (a working-set gap)."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.dicts = zsdic.Dictionaries.from_romfs(self.root)
        self.inputs: list[str] = []
        self._files: dict[str, bytes] = {}
        self._packs: dict[str, dict[str, bytes]] = {}

    def read(self, path: str) -> bytes:
        if path not in self._files:
            file = self.root / PurePosixPath(path)
            if not file.is_file():
                raise PatchError(f"Gold Skulltula delivery needs {path}, which {self.root} lacks")
            data = file.read_bytes()
            self._files[path] = self.dicts.decompress(path, data) if path.endswith(".zs") else data
            self.inputs.append(path)
        return self._files[path]

    def pack(self, actor: str) -> dict[str, bytes]:
        if actor not in self._packs:
            self._packs[actor] = sarc.read(self.read(pack_path(actor)))
        return self._packs[actor]


def _sha256(data: bytes | None) -> str | None:
    return None if data is None else hashlib.sha256(data).hexdigest()


def _cell(table: Mapping[str, dict], reason: str) -> dict:
    return table.get(f"{reason}___Data", {})


def death_procedures(romfs: Romfs, pack: Mapping[str, bytes], death_ref: str) -> dict[str, dict]:
    """The death procedures a ``DeathRef`` resolves to, by cell key (``PickedUp___Data``, ...)."""
    death = actor_packs.resolve_node([pack], reference(death_ref) or death_ref, builtin=DEATH_DEFAULT)
    if "DeathProcedures" not in death:
        raise PatchError(f"{death_ref}: no DeathProcedures: {death!r}")
    return actor_packs.combination_table(romfs.read, death["DeathProcedures"], DEATH_TABLE_TYPE)


def check_save_rows(game_data_list: Mapping, sources: Sequence[int]) -> None:
    """Every source Hash is nonzero (the callback skips zero, the blackboard default) and its collection pair, H and
    H xor 2, is a permanent saved ``Bool64bitKey`` row (not token stock)."""
    rows = {int(row["Hash"]): row for row in game_data_list["Data"]["Bool64bitKey"]}
    for source in sorted(sources):
        if not source:
            raise PatchError("source Hash 0 cannot be transferred: it is the GoldTokenGmdHash default")
        for key in (source, source ^ COMPANION_XOR):
            row = rows.get(key)
            if row is None or (row.get("ResetTypeValue"), row.get("SaveFileIndex")) != (PERMANENT, SAVE_FILE):
                raise PatchError(
                    f"{source}: saved collection row {key} is {row!r}; expected ResetTypeValue {PERMANENT}, "
                    f"SaveFileIndex {SAVE_FILE}"
                )


def check_source(romfs: Romfs) -> None:
    """The enemy creates one native token, may name another actor per instance, passes its Hash through the pinned
    utility graph, and saves nothing at death (``LifeDepleted`` keeps the saved flag; it only retires the instance)."""
    pack = romfs.pack(ENEMY)
    if (sha := _sha256(pack.get(ENEMY_GRAPH))) != ENEMY_GRAPH_SHA256:
        raise PatchError(f"{ENEMY_PACK}: {ENEMY_GRAPH} SHA256 {sha}, not the specified graph {ENEMY_GRAPH_SHA256}")
    components = actor_packs.resolve([pack], actor_member(ENEMY))[0].get("Components", {})
    if components.get("ActorGameDataSetting") != component_ref(NO_RESPAWN):
        raise PatchError(f"{ENEMY}: game-data setting {components.get('ActorGameDataSetting')!r}, not NoRespawn")
    drop = actor_packs.resolve_node([pack], reference(components.get("DropRef")) or "")
    tables = drop.get("DropTableResourceList")
    if tables != [TOKEN_DROP_TABLE]:
        raise PatchError(f"{ENEMY}: drop tables {tables!r}, expected [{TOKEN_DROP_TABLE!r}]")
    subtables = byml.read(pack[reference(TOKEN_DROP_TABLE)]).get("SubTableList", [])
    items = [item for sub in subtables for item in byml.read(pack[reference(sub)]).get("Items", [])]
    token = work_path(actor_member(TOKEN))
    selected = [(i.get("DropActorName"), i.get("DropProbability"), i.get("DropCreateCount")) for i in items]
    if selected != [(token, 100, 1)]:
        raise PatchError(f"{ENEMY}: drop items {items!r}; expected one {token} at probability 100, count 1")
    blackboard = byml.read(pack[reference(drop.get("BlackboardTableRef"))])
    selectors = [p for p in blackboard.get("BlackboardParamStringArray", []) if p.get("BBKey") == DROP]
    if len(selectors) != 1 or selectors[0].get("IsInstanceParam") is not True:
        raise PatchError(f"{ENEMY}: {DROP} blackboard entries {selectors!r}; expected one instance parameter")
    life = _cell(death_procedures(romfs, pack, components.get("DeathRef", "")), "LifeDepleted")
    contract = (life.get("IsSetGmdRespawnFlagToFalse"), life.get("IsSetRespawnFlagToFalse"), life.get("IsDropItem"))
    if contract != (False, True, True):
        raise PatchError(
            f"{ENEMY}: LifeDepleted resolves to {life!r}; expected the saved flag kept "
            "(IsSetGmdRespawnFlagToFalse false), the instance retired and the drop created"
        )


def check_token(romfs: Romfs) -> dict[str, bytes]:
    """The native token pack: its pinned graph, the source-Hash and attention blackboard, the graph's physics bodies,
    ``PickedUp`` waiting for the callback's signal, its own identity, and a member set equal to its reference closure
    (no member only a graph references)."""
    pack = romfs.pack(TOKEN)
    found = actor_packs.closure([pack], TOKEN)
    if set(found.members) != set(pack):
        raise PatchError(f"{TOKEN_PACK}: members outside its closure {sorted(set(pack) - set(found.members))}")
    components = found.components
    root = byml.read(pack[reference(components.get("AIInfoRef"))]).get("RootAIRef")
    graph = _sha256(pack.get(TOKEN_GRAPH))
    if reference(root) != TOKEN_GRAPH or graph != TOKEN_GRAPH_SHA256:
        raise PatchError(
            f"{TOKEN}: AI root {root!r} with SHA256 {graph}; expected {TOKEN_GRAPH}, the specified graph "
            f"{TOKEN_GRAPH_SHA256}"
        )
    keys = source_hash_keys([pack], components)
    if keys != [{"BBKey": SOURCE_HASH_KEY, "InitVal": 0, "IsInstanceParam": False}]:
        raise PatchError(
            f"{TOKEN}: {SOURCE_HASH_KEY} blackboard entries {keys!r}; expected one U64, default 0, "
            "not an instance parameter"
        )
    attention = blackboard_entries([pack], components, "BlackboardParamBoolArray", ATTENTION_KEY)
    if attention != [{"BBKey": ATTENTION_KEY, "InitVal": True, "IsInstanceParam": False}]:
        raise PatchError(f"{TOKEN}: {ATTENTION_KEY} blackboard entries {attention!r}; expected one Bool, default true")
    controllers, bodies = physics_bodies([pack], components)
    if PHYSICS_BODY not in controllers or PHYSICS_BODY not in bodies:
        raise PatchError(
            f"{TOKEN}: physics controllers {controllers!r}, rigid bodies {bodies!r}; the graph needs {PHYSICS_BODY!r}"
        )
    picked = _cell(death_procedures(romfs, pack, components.get("DeathRef", "")), "PickedUp")
    if picked.get("IsWaitForSignal") is not True or picked.get("IsIgnoreThisDeathReason") is True:
        raise PatchError(f"{TOKEN}: PickedUp resolves to {picked!r}; expected it to wait for the callback's signal")
    pouch = actor_packs.resolve_node([pack], reference(components.get("PouchContentRef")) or "", builtin=POUCH_DEFAULT)
    identity = (canonical(components), pouch.get("PouchActor"))
    if identity != (TOKEN_ITEM, work_path(actor_member(TOKEN_ITEM))):
        raise PatchError(f"{TOKEN_PACK}: identity {identity!r} is not the native token's; the dump is modified")
    return pack


def _member(sources: actor_packs.Sources, ref: str | None) -> dict:
    """The parsed member a reference names; a missing one names itself."""
    name = reference(ref) or ""
    data = actor_packs.find(sources, name)
    if data is None:
        raise PatchError(f"{ref!r}: no such member in the source packs")
    return byml.read(data)


def blackboard_entries(sources: actor_packs.Sources, components: Mapping[str, str], array: str, key: str) -> list[dict]:
    """One key's declarations in an actor's blackboard tables (name, default, instance flag)."""
    info = actor_packs.resolve_node(sources, reference(components.get("BlackboardRef")) or "")
    found = []
    for table in info.get("BlackboardParamTables", []):
        for param in _member(sources, table).get(array, []):
            if param.get("BBKey") == key:
                found.append({k: param.get(k) for k in ("BBKey", "InitVal", "IsInstanceParam")})
    return found


def source_hash_keys(sources: actor_packs.Sources, components: Mapping[str, str]) -> list[dict]:
    """The U64 ``GoldTokenGmdHash`` declarations of an actor's blackboard tables (name, default, instance flag)."""
    return blackboard_entries(sources, components, "BlackboardParamU64Array", SOURCE_HASH_KEY)


def physics_bodies(sources: actor_packs.Sources, components: Mapping[str, str]) -> tuple[list[str], list[str]]:
    """The controller entity names and rigid body entity names of an actor's physics controller set."""
    physics = _member(sources, components.get("PhysicsRef"))
    if "ControllerSetPath" not in physics:
        raise PatchError(f"{components.get('PhysicsRef')!r}: no ControllerSetPath: {physics!r}")
    controller_set = _member(sources, physics["ControllerSetPath"])
    controllers = [entry.get("Name") for entry in controller_set.get("ControllerEntityNamePathAry", [])]
    bodies = [entry.get("Name") for entry in controller_set.get("RigidBodyEntityNamePathAry", [])]
    return controllers, bodies


def canonical(components: Mapping[str, str]) -> str:
    """The canonical actor name an ``ActorNameRef`` gives (``?ActorSystem/ActorName/<Name>.engine__...``)."""
    return PurePosixPath(reference(components.get("ActorNameRef")) or "").name.split(".", 1)[0]


def pouch_grant(effective: Mapping, components: Mapping[str, str]) -> str | None:
    """The ``PouchActor`` a pickup's pouch names for a native pouch component: the one it names; none for a bundle
    naming none (of the 45 native bundles, 35 name none and 10 their own ``BundleActor``); otherwise the canonical
    ``ActorName``'s actor, which the actor's own-identity grant would record (``IsGet.<canonical>``)."""
    if effective.get(GRANT_KEY):
        return effective[GRANT_KEY]
    if effective.get(BUNDLE_KEY):
        return None
    return work_path(actor_member(canonical(components)))


def _is_world_pickup(sources: actor_packs.Sources, actor: str) -> bool:
    return actor_member(ITEM_BASE) in actor_packs.resolve(sources, actor_member(actor))[1]


def compose(
    item: str,
    token_pack: Mapping[str, bytes],
    donor_pack: Mapping[str, bytes],
    generic_pack: Mapping[str, bytes],
    registries: Mapping[str, Mapping[str, dict]],
) -> Pickup:
    """The generated pickup for one reward and its three registry rows (see the module docstring)."""
    actor = pickup_name(item)
    token_node = byml.read(token_pack[actor_member(TOKEN)])
    if set(token_node) != {"$parent", "Components"} or token_node["$parent"] != work_path(actor_member(ITEM_BASE)):
        raise PatchError(f"{TOKEN}: actor parameter is not a direct {ITEM_BASE} child: {token_node!r}")
    token = actor_packs.closure([token_pack], TOKEN)
    donor = actor_packs.closure([donor_pack], item)
    generic = actor_packs.closure([generic_pack], GENERIC_DISPLAY)
    components = dict(token_node["Components"])
    for key in IDENTITY:
        if key not in donor.components:
            raise PatchError(f"{item}: no {key} to give the pickup")
        components[key] = donor.components[key]
    world = _is_world_pickup([donor_pack], item)
    if world:
        for key in WORLD_DISPLAY:
            if key in donor.components:
                components[key] = donor.components[key]
            else:
                components.pop(key, None)
    else:
        for key in GENERIC_WORLD_DISPLAY:
            components[key] = generic.components[key]
        components.pop("ELinkRef", None)
        components.pop("SLinkRef", None)
    new_members: dict[str, bytes] = {}
    pouch = reference(components["PouchContentRef"])
    effective = actor_packs.resolve_node([donor_pack], pouch, builtin=POUCH_DEFAULT)
    fields = dict(POLICY)
    if (grant := pouch_grant(effective, donor.components)) and effective.get(GRANT_KEY) != grant:
        fields[GRANT_KEY] = grant  # an actor granting its own identity: named explicitly
    if any(effective.get(key) != value for key, value in fields.items()):
        derived = f"Component/PouchContentParam/{actor}.game__component__PouchContentParam.bgyml"
        new_members[derived] = byml.write({"$parent": work_path(pouch), **fields})
        components["PouchContentRef"] = component_ref(derived)
    new_members[actor_member(actor)] = byml.write({"$parent": token_node["$parent"], "Components": components})
    sources = [new_members, token_pack, donor_pack, generic_pack]
    packed = actor_packs.closure(sources, actor)
    _check_pickup(item, actor, sources, packed, token, donor, generic, world)
    owners = ((TOKEN, token_pack), (item, donor_pack), (GENERIC_DISPLAY, generic_pack))
    copied = {
        name: next(pack_path(owner) for owner, pack in owners if name in pack)
        for name in packed.members
        if name not in new_members
    }
    data = sarc.write(dict(packed.members))
    if sarc.read(data) != packed.members:
        raise PatchError(f"{actor}: generated pack does not read back")
    rows = _rows(item, actor, sources, packed.components, donor.components, registries)
    return Pickup(item, actor, NewFile(data, copied=copied), rows)


def _check_pickup(item, actor, sources, packed, token, donor, generic, world) -> None:
    """Mechanism equals the token's, identity the reward's, pickup policy holds, nothing new is depended on."""
    mechanism = set(token.components) - set(IDENTITY) - set(WORLD_DISPLAY)
    for key in sorted(mechanism):
        if packed.components.get(key) != token.components[key]:
            raise PatchError(
                f"{actor}: {key} {packed.components.get(key)!r} is not the token's {token.components[key]!r}"
            )
    if canonical(packed.components) != canonical(donor.components):
        raise PatchError(f"{actor}: canonical name {canonical(packed.components)!r}, not {item}'s")
    for key in ("ModelInfoRef", "AnimationRef"):
        if packed.components[key] != donor.components[key]:
            raise PatchError(f"{actor}: {key} is not {item}'s")
    if world:
        expected = {key: donor.components.get(key) for key in WORLD_DISPLAY}
    else:
        expected = {key: generic.components[key] for key in GENERIC_WORLD_DISPLAY}
        expected |= {"ELinkRef": None, "SLinkRef": None}
        expected["GameParameterTableRef"] = token.components.get("GameParameterTableRef")
    for key, value in expected.items():
        if packed.components.get(key) != value:
            raise PatchError(f"{actor}: {key} {packed.components.get(key)!r}, expected {value!r}")
    pouch = actor_packs.resolve_node(sources, reference(packed.components["PouchContentRef"]), builtin=POUCH_DEFAULT)
    native = actor_packs.resolve_node(sources, reference(donor.components["PouchContentRef"]), builtin=POUCH_DEFAULT)
    grant = pouch_grant(native, donor.components)
    if (pouch.get(GRANT_KEY) or None) != grant:
        raise PatchError(f"{actor}: pouch grants {pouch.get(GRANT_KEY)!r}, not {item}'s grant {grant!r}")
    ignored = {*POLICY, GRANT_KEY}
    if {k: v for k, v in pouch.items() if k not in ignored} != {k: v for k, v in native.items() if k not in ignored}:
        raise PatchError(f"{actor}: pouch {pouch!r} differs from {item}'s {native!r} beyond the pickup policy")
    if any(pouch.get(key) != value for key, value in POLICY.items()):
        raise PatchError(f"{actor}: pouch {pouch!r} lacks the pickup policy {POLICY!r}")
    if TOKEN_GRAPH not in packed.members or _sha256(packed.members[TOKEN_GRAPH]) != TOKEN_GRAPH_SHA256:
        raise PatchError(f"{actor}: the token graph is not packed byte-identical")
    for array, key in (("BlackboardParamU64Array", SOURCE_HASH_KEY), ("BlackboardParamBoolArray", ATTENTION_KEY)):
        if blackboard_entries(sources, packed.components, array, key) != blackboard_entries(
            sources, token.components, array, key
        ):
            raise PatchError(f"{actor}: blackboard {key} is not the token's")
    if physics_bodies(sources, packed.components) != physics_bodies(sources, token.components):
        raise PatchError(f"{actor}: physics bodies are not the token's {physics_bodies(sources, token.components)!r}")
    allowed = token.external | donor.external | generic.external
    if extra := sorted(packed.external - allowed):
        raise PatchError(f"{actor}: references resources no native source depends on: {extra}")


def _rows(item, actor, sources, components, donor_components, registries) -> dict[str, dict]:
    """New registry rows: lifecycle from the token's, display from the reward's, pouch from the reward's."""
    actor_rows, game_rows, pouch_rows = (registries[path] for path in REGISTRIES)
    for path, name in ((ACTOR_INFO, TOKEN), (ACTOR_INFO, item), (GAME_ACTOR_INFO, TOKEN), (POUCH_ACTOR_INFO, item)):
        if name not in registries[path]:
            raise PatchError(f"{path}: no native row {name}")
    donor = actor_rows[item]
    _check_display_row(item, donor, sources, donor_components)
    row = copy.deepcopy(actor_rows[TOKEN])
    for field in ROW_DISPLAY:
        if field in donor:
            row[field] = copy.deepcopy(donor[field])
        else:
            row.pop(field, None)
    for component, field in LINK_USERS:
        if component in components:
            row[field] = _member(sources, components[component]).get("UserName")
        else:
            row.pop(field, None)
    # Instance budgets cover more than model bytes; reserve both natives' (patch.getitem's precedent) rather than
    # assume an unmeasured component/mesh heap delta. An upper reservation, not a measured minimum.
    token_row = actor_rows[TOKEN]
    row["InstanceHeapSize"] = type(token_row["InstanceHeapSize"])(
        int(token_row["InstanceHeapSize"]) + int(donor["InstanceHeapSize"])
    )
    row["PreActorRenderInfoHeapSize"] = type(token_row["PreActorRenderInfoHeapSize"])(
        max(int(token_row["PreActorRenderInfoHeapSize"]), int(donor["PreActorRenderInfoHeapSize"]))
    )
    row["__RowId"] = actor
    _check_display_row(actor, row, sources, components)
    game = {**copy.deepcopy(game_rows[TOKEN]), "__RowId": actor}
    pouch = {**copy.deepcopy(pouch_rows[item]), "__RowId": actor}
    return {ACTOR_INFO: row, GAME_ACTOR_INFO: game, POUCH_ACTOR_INFO: pouch}


def _check_display_row(actor: str, row: Mapping, sources, components: Mapping[str, str]) -> None:
    """An ActorInfo row agrees with the actor's components: canonical name, model, animations, effect/sound users."""
    model = _member(sources, components["ModelInfoRef"])
    animation = _member(sources, components["AnimationRef"])
    expected = {
        "ActorName": canonical(components),
        "FmdbName": model.get("FmdbName"),
        "ModelProjectName": model.get("ModelProjectName"),
        "AnimationResources": animation.get("AnimationResources"),
    }
    for component, field in LINK_USERS:
        expected[field] = _member(sources, components[component]).get("UserName") if component in components else None
    actual = {field: row.get(field) for field in expected}
    if not byml.same(actual, expected):
        raise PatchError(f"ActorInfo {actor}: {actual!r} disagrees with its components {expected!r}")


def _ids_digest(ids: Sequence[str]) -> str:
    return hashlib.sha256("\0".join(ids).encode("utf-8")).hexdigest()


def _sorted_index(ids: Sequence[str], name: str) -> int:
    return bisect_left(ids, name.encode("utf-8"), key=lambda i: i.encode("utf-8"))


def _insert_rows(
    data: bytes, *, path: str, rows: Sequence[dict], digest: str, count: int, donors: Mapping[str, dict]
) -> bytes:
    """Insert new rows at their sorted places, over the dump's exact row list; existing rows stay as they are."""
    document = byml.load(data)
    table = document.root
    if not isinstance(table, list):
        raise PatchError(f"{path}: not a row table")
    ids = [row.get("__RowId") for row in table]
    if (len(ids), _ids_digest(ids)) != (count, digest):
        raise PatchError(f"{path}: {len(ids)} rows that are not the dump's {count}; refusing to insert by index")
    for name, native in donors.items():
        if not byml.same(table[ids.index(name)], native):
            raise PatchError(f"{path}: row {name} changed since the pickup was composed: {table[ids.index(name)]!r}")
    for row in sorted(rows, key=lambda r: r["__RowId"].encode("utf-8")):
        ids = [r.get("__RowId") for r in table]
        if row["__RowId"] in ids:
            raise PatchError(f"{path}: row {row['__RowId']} already exists")
        table.insert(_sorted_index(ids, row["__RowId"]), copy.deepcopy(row))
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{path}: changed table does not read back: {difference}")
    return out


def _set_drops(data: bytes, *, path: str, drops: Mapping[int, str]) -> bytes:
    """Name the generated pickup on each source copy in this placement file; nothing else changes."""
    document = byml.load(data)
    actors = document.root.get("Actors") if isinstance(document.root, dict) else None
    if not isinstance(actors, list):
        raise PatchError(f"{path} has no Actors list")
    found = []
    for source, pickup in sorted(drops.items()):
        matches = [a for a in actors if isinstance(a, dict) and a.get("Hash") == source]
        if len(matches) != 1:
            raise PatchError(f"{path}: {len(matches)} actors have Hash {source}, expected one {ENEMY}")
        actor = matches[0]
        drop_fields = {k: v for k, v in (actor.get("Dynamic") or {}).items() if str(k).startswith(DROP_FIELDS)}
        if actor.get("Gyaml") != ENEMY or drop_fields:
            raise PatchError(
                f"{path}: stale source {source}: Gyaml {actor.get('Gyaml')!r}, drop fields {drop_fields!r}; "
                f"expected a native {ENEMY} with none"
            )
        found.append((actor, pickup))
    for actor, pickup in found:
        actor.setdefault("Dynamic", {})[DROP] = pickup
    out = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(out))) is not None:
        raise PatchError(f"{path}: changed placement does not read back: {difference}")
    return out


def build(
    romfs: str | Path, placements: Mapping[int, str], census: Sequence[Location], *, rewards: Mapping[str, str]
) -> Delivery:
    """Delivery for explicit Skulltula assignments: source Hash -> native grant actor (``Item_Token_Gold`` keeps the
    native drop).

    ``rewards`` is this build's explicit allowed set, grant actor -> :data:`FAMILIES` name: production passes the
    members ``clawshot.generate.tokens`` admits, a diagnostic its own. A placed actor outside it, or whose native
    ``PouchActorInfo`` row does not have the declared family's shape, is refused. Validates the census identities,
    both saved collection rows of every assigned source, the native enemy and token contracts, and each generated
    pickup, before any output; the returned transforms re-check their inputs."""
    if unknown := sorted({family for family in rewards.values() if family not in FAMILIES}):
        raise PatchError(f"unknown grant families {unknown}; known: {sorted(FAMILIES)}")
    if stray := sorted(actor for actor, family in rewards.items() if (family == "token") != (actor == TOKEN_ITEM)):
        raise PatchError(f"only {TOKEN_ITEM}, the native drop, is the token family: {stray}")
    locations = {location.id: location for location in census}
    generated: dict[int, str] = {}
    for source, actor in sorted(placements.items()):
        location = locations.get(source)
        if (
            location is None
            or location.kind != GOLD_SKULLTULA
            or location.actor != ENEMY
            or not location.has_save_flag
            or not location.files
        ):
            raise PatchError(f"{source}: not a saved {ENEMY} census location: {location!r}")
        if actor not in rewards:
            raise PatchError(
                f"{source}: {actor!r} is not an allowed reward of this build ({', '.join(sorted(rewards))})"
            )
        if actor != TOKEN_ITEM:
            generated[source] = actor
    native = Romfs(romfs)
    check_save_rows(byml.read(native.read(GAME_DATA_LIST)), list(placements))
    check_source(native)
    token_pack = check_token(native)
    tables = {path: byml.read(native.read(path)) for path in REGISTRIES}
    registries = {path: {row["__RowId"]: row for row in table} for path, table in tables.items()}
    for actor in sorted(set(placements.values())):
        row = registries[POUCH_ACTOR_INFO].get(actor)
        if row is None:
            raise PatchError(f"{actor}: no native {POUCH_ACTOR_INFO} row to classify its grant")
        if (family := grant_family(row)) != rewards[actor]:
            raise PatchError(f"{actor}: native grant family {family!r}, not the declared {rewards[actor]!r}: {row!r}")
    if not generated:
        return Delivery({}, {}, {}, {}, tuple(native.inputs))
    ids = {path: [row["__RowId"] for row in table] for path, table in tables.items()}
    for path, names in ids.items():
        if names != sorted(names, key=lambda name: name.encode("utf-8")) or len(set(names)) != len(names):
            raise PatchError(f"{path}: rows are not uniquely sorted by __RowId")
    if ids[ACTOR_INFO] != ids[GAME_ACTOR_INFO]:
        raise PatchError(f"{ACTOR_INFO} and {GAME_ACTOR_INFO} do not list the same rows in the same order")
    actors = sorted(set(generated.values()))
    pickups = []
    for item in actors:
        pickup = compose(item, token_pack, native.pack(item), native.pack(GENERIC_DISPLAY), registries)
        for path in REGISTRIES:
            if pickup.actor in registries[path]:
                raise PatchError(f"{path}: {pickup.actor} already exists")
        pickups.append(pickup)
    drops = {source: pickup_name(item) for source, item in generated.items()}
    per_file: dict[str, dict[int, str]] = {}
    for source, pickup in drops.items():
        for path in locations[source].files:
            per_file.setdefault(path, {})[source] = pickup
    changes: dict = {path: partial(_set_drops, path=path, drops=targets) for path, targets in sorted(per_file.items())}
    donors = {
        ACTOR_INFO: (TOKEN, *actors),
        GAME_ACTOR_INFO: (TOKEN,),
        POUCH_ACTOR_INFO: tuple(actors),
    }
    for path in REGISTRIES:
        changes[path] = partial(
            _insert_rows,
            path=path,
            rows=tuple(pickup.rows[path] for pickup in pickups),
            digest=_ids_digest(ids[path]),
            count=len(ids[path]),
            donors={name: copy.deepcopy(registries[path][name]) for name in donors[path]},
        )
    return Delivery(
        changes,
        {pack_path(pickup.actor): pickup.file for pickup in pickups},
        {pickup.item: pickup.actor for pickup in pickups},
        dict(sorted(drops.items())),
        tuple(native.inputs),
    )


@dataclass(frozen=True)
class SourceChange:
    """One shuffled Token location, for the spoiler's ``patch.tokens``: its source and what collecting there grants.
    Its completion records are always the source's H and H xor 2, whatever the reward."""

    location: str  # the world location
    id: int  # the enemy Hash, the same on every copy
    name: str  # the census definition's name
    files: tuple[str, ...]  # every placement file holding the Hash (age/Alternative copies)
    item: str  # the logic item placed here
    pickup: str  # its native grant actor; Item_Token_Gold keeps the source's native drop
    drop_actor: str | None  # the generated pickup every copy now names; None: native, placement unchanged

    def as_dict(self) -> dict:
        return {
            "location": self.location,
            "id": str(self.id),
            "name": self.name,
            "files": list(self.files),
            "item": self.item,
            "pickup": self.pickup,
            "drop_actor": self.drop_actor,
        }


def link_sources(
    names: Sequence[str], definitions: Sequence[Definition], census: Sequence[Location]
) -> dict[str, Location]:
    """Each Token location's census source, by stable Hash: the one Gold Skulltula definition whose OoT Randomizer
    name, or remake name where it has none, is the location's. First every Gold Skulltula identity must agree: each
    definition a saved native enemy in the census, with its copies, and each census source defined. Copies share
    their Hash, so a location's one assignment reaches every age/Alternative copy."""
    sources = [location for location in census if location.kind == GOLD_SKULLTULA]
    by_id = {location.id: location for location in sources}
    defined = [definition for definition in definitions if definition.kind == GOLD_SKULLTULA]
    problems = []
    if len(by_id) != len(sources):
        problems.append(f"the census lists a source Hash twice: {sorted(location.id for location in sources)}")
    if missing := sorted({d.id for d in defined} - by_id.keys(), key=str):
        problems.append(f"definitions with no census source: {missing}")
    if undefined := sorted(by_id.keys() - {d.id for d in defined}):
        problems.append(f"census sources with no definition: {undefined}")
    for location in sources:
        if location.actor != ENEMY or not location.has_save_flag or not location.files:
            problems.append(f"{location.id}: not a saved native {ENEMY} with placement copies: {location!r}")
    named: dict[str, list[Definition]] = {}
    for definition in defined:
        named.setdefault(definition.oot_randomizer_name or definition.name, []).append(definition)
    linked: dict[str, Location] = {}
    for name in names:
        found = named.get(name, [])
        if len(found) != 1 or found[0].id not in by_id:
            problems.append(f"{name}: {len(found)} Gold Skulltula definitions {[d.id for d in found]}, expected one")
            continue
        linked[name] = by_id[found[0].id]
    shared = sorted({source.id for source in linked.values() if list(linked.values()).count(source) > 1})
    if shared:
        problems.append(f"several Token locations name the same source: {shared}")
    if problems:
        raise PatchError("cannot link the Token locations to the remake's Gold Skulltulas:\n  " + "\n  ".join(problems))
    return linked


def seed_delivery(
    romfs: str | Path,
    placements: Mapping[str, str],
    sources: Mapping[str, Location],
    names: Mapping[int, str],
    census: Sequence[Location],
    *,
    rewards: Mapping[str, tuple[str, str]],
) -> tuple[Delivery, tuple[SourceChange, ...]]:
    """A Token seed's delivery and spoiler rows: each linked location's placed logic item, through ``rewards`` (logic
    item -> native grant actor and its family, the policy's admitted members), at its source."""
    families: dict[str, str] = {}
    for _, (actor, family) in sorted(rewards.items()):
        if families.setdefault(actor, family) != family:
            raise PatchError(f"{actor} is declared in two grant families: {families[actor]!r} and {family!r}")
    assignments: dict[int, str] = {}
    for name, source in sorted(sources.items()):
        item = placements.get(name)
        if item not in rewards:
            raise PatchError(f"{name}: {item!r} is not an admitted Token reward ({', '.join(sorted(rewards))})")
        assignments[source.id] = rewards[item][0]
    delivery = build(romfs, assignments, census, rewards=families)
    rows = tuple(
        SourceChange(
            name,
            source.id,
            names.get(source.id, ""),
            source.files,
            placements[name],
            assignments[source.id],
            delivery.drops.get(source.id),
        )
        for name, source in sorted(sources.items(), key=lambda pair: (pair[0], pair[1].id))
    )
    return delivery, rows
