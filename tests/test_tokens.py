"""Gold Skulltula reward delivery and the Token shuffle writer (Round 15) over a synthetic dump built in code.

The synthetic packs, death tables and registries copy the native *shapes* that tokens.build validates (names,
references, inheritance), never game bytes. The two AI graphs are opaque synthetic bytes whose digests stand in for
the pinned native ones: their behaviour is the accepted specification's, not something these tests derive. The
Token seed tests run the real fill on a synthetic world and the real common writer on the synthetic dump.
"""

import hashlib

import pytest

from clawshot.census.definitions import Definition
from clawshot.census.scan import GAME_DATA_LIST, Location
from clawshot.formats import byml, rstb, sarc, zsdic
from clawshot.formats.byml import F32, I32, U32, U64
from clawshot.patch import actor_packs, tokens
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import write

TREE, TOWER, LONE = 1000, 2000, 3000  # synthetic source Hashes; companions are Hash xor 2
CHEST = 77
CHILD = "Banc/Test/Test_Child_Static.bcett.byml.zs"
ADULT = "Banc/Test/Test_Adult_Static.bcett.byml.zs"
CORE = {TREE: "Item_Boomerang", TOWER: "Obj_Shield_Hylian", LONE: "Item_Token_Gold"}
ALLOWED = {"Item_Boomerang": "fixed_major", "Obj_Shield_Hylian": "equipment", "Item_Token_Gold": "token"}
TOKEN_GRAPH_BYTES = b"AIB synthetic token graph, opaque"
ENEMY_GRAPH_BYTES = b"AIB synthetic enemy utility graph, opaque"
NATIVE_ENTRY = 4096
BOOMERANG_PICKUP = tokens.pickup_name("Item_Boomerang")
SHIELD_PICKUP = tokens.pickup_name("Obj_Shield_Hylian")
CANONICAL = {"Item_Boomerang": "Item_Boomerang", "Obj_Shield_Hylian": "Weapon_Shield_Hylian"}


def actor(name):
    return actor_packs.actor_member(name)


def work(member):
    return actor_packs.work_path(member)


def ref(member):
    return actor_packs.component_ref(member)


def member(reference):
    return actor_packs.reference(reference)


def w(tree):
    return byml.write(tree)


PERFORMER = "Component/EventPerformerParam/PouchContent_PickUpItem.engine__component__EventPerformerParam.bgyml"
BASE_GPT = "GameParameter/GameParameterTable/Obj_Item_Base.engine__actor__GameParameterTable.bgyml"
MENU = "GameParameter/MenuActorParam/ItemMenuActorBase.game__ui__MenuActorParam.bgyml"
BASE_LIFT = "Component/LiftableParam/Obj_Item_Base.game__component__LiftableParam.bgyml"
ITEM_OBJ = "Component/ASInfo/Item_Obj.engine__component__ASInfo.bgyml"
BASE_COMPONENTS = {
    "AIInfoRef": ref("AI/AIInfo/DropItem.engine__actor__AIInfo.bgyml"),
    "ActorGameDataSetting": ref(tokens.NO_RESPAWN),
    "ActorNameRef": ref("ActorSystem/ActorName/Obj_Item_Base.engine__actor__ActorName.bgyml"),
    "BlackboardRef": ref("Component/Blackboard/BlackboardInfo/Obj_Item_Base.engine__component__BlackboardInfo.bgyml"),
    "DeathRef": ref("Component/DeathParam/DropItem.game__component__DeathParam.bgyml"),
    "EventPerformerRef": ref(PERFORMER),
    "GameParameterTableRef": ref(BASE_GPT),
    "LiftableRef": ref(BASE_LIFT),
    "PouchContentRef": ref("Component/PouchContentParam/Obj_Item_Base.game__component__PouchContentParam.bgyml"),
}
TOKEN_COMPONENTS = {
    "AIInfoRef": ref("AI/AIInfo/Item_Token_Gold.engine__actor__AIInfo.bgyml"),
    "ASInfoRef": ref("Component/ASInfo/Obj_Token_Gold.engine__component__ASInfo.bgyml"),
    "ASRef": "?AS/Obj_Token_Gold.root.asb",
    "ActorNameRef": "?ActorSystem/ActorName/Item_Token_Gold.engine__actor__ActorName.bgyml",
    "AnimationRef": ref("Component/AnimationParam/Obj_Token_Gold.engine__component__AnimationParam.bgyml"),
    "AttentionSenderRef": ref(
        "Component/AttentionSenderParam/AutoPickUpItemLockOn_Token_Gold.game__component__AttentionSenderParam.bgyml"
    ),
    "BlackboardRef": ref("Component/Blackboard/BlackboardInfo/Item_Token_Gold.engine__component__BlackboardInfo.bgyml"),
    "DeathRef": ref("Component/DeathParam/Item_Token_Gold.game__component__DeathParam.bgyml"),
    "ELinkRef": ref("Component/ELink/Obj_Token_Gold.engine__component__ELinkParam.bgyml"),
    "GameLifeConditionRef": "?ActorSystem/GameLifeCondition/Landmark300m.game__actor__LifeCondition.bgyml",
    "GameParameterTableRef": ref(
        "GameParameter/GameParameterTable/Obj_Token_Gold.engine__actor__GameParameterTable.bgyml"
    ),
    "LiftableRef": ref("Component/LiftableParam/Obj_Item_Token_Gold.game__component__LiftableParam.bgyml"),
    "ModelInfoRef": ref("Component/ModelInfo/Obj_Token_Gold.engine__component__ModelInfo.bgyml"),
    "PhysicsRef": ref("Component/Physics/Obj_Token_Gold.engine__component__PhysicsParam.bgyml"),
    "PouchContentRef": ref("Component/PouchContentParam/Obj_Token_Gold.game__component__PouchContentParam.bgyml"),
    "SLinkRef": ref("Component/SLink/Obj_Token_Gold.engine__component__SLinkParam.bgyml"),
}
TOKEN_BLACKBOARD = (
    "Component/Blackboard/BlackboardParamTable/Item_Token_Gold.engine__component__BlackboardParamTable.bgyml"
)
TOKEN_CONTROLLER = "Phive/ControllerSetParam/Obj_Token_Gold.phive__ControllerSetParam.bgyml"
BOOMERANG_COMPONENTS = {
    "ASInfoRef": ref("Component/ASInfo/Item_GetDemo.engine__component__ASInfo.bgyml"),
    "ASRef": "?AS/Item_Common.root.asb",
    "ActorNameRef": "?ActorSystem/ActorName/Item_Boomerang.engine__actor__ActorName.bgyml",
    "AnimationRef": ref("Component/AnimationParam/Item_Boomerang.engine__component__AnimationParam.bgyml"),
    "GameParameterTableRef": ref(
        "GameParameter/GameParameterTable/Item_Boomerang.engine__actor__GameParameterTable.bgyml"
    ),
    "ModelInfoRef": ref("Component/ModelInfo/Item_Boomerang.engine__component__ModelInfo.bgyml"),
    "PouchContentRef": ref("Component/PouchContentParam/Item_Boomerang.game__component__PouchContentParam.bgyml"),
}
SHIELD_COMPONENTS = {
    "ASInfoRef": ref(ITEM_OBJ),
    "ASRef": "?AS/Item_Common.root.asb",
    "ActorNameRef": "?ActorSystem/ActorName/Weapon_Shield_Hylian.engine__actor__ActorName.bgyml",
    "AnimationRef": ref("Component/AnimationParam/Obj_Shield_Hylian.engine__component__AnimationParam.bgyml"),
    "ELinkRef": ref("Component/ELink/Obj_Shield_Hylian.engine__component__ELinkParam.bgyml"),
    "GameParameterTableRef": ref(
        "GameParameter/GameParameterTable/Obj_Shield_Hylian.engine__actor__GameParameterTable.bgyml"
    ),
    "LiftableRef": ref("Component/LiftableParam/Obj_Item_Shield_Hylian.game__component__LiftableParam.bgyml"),
    "ModelInfoRef": ref("Component/ModelInfo/Obj_Shield_Hylian.engine__component__ModelInfo.bgyml"),
    "PhysicsRef": ref("Component/Physics/Obj_Shield_Hylian.engine__component__PhysicsParam.bgyml"),
    "PouchContentRef": ref("Component/PouchContentParam/Obj_Shield_Hylian.game__component__PouchContentParam.bgyml"),
    "SLinkRef": ref("Component/SLink/Obj_Shield_Hylian.engine__component__SLinkParam.bgyml"),
}
AUTO_PICK = "Component/PouchContentParam/AutoPickShield.game__component__PouchContentParam.bgyml"


def shared():
    """Members every Obj_Item_Base pack holds, with one content per path (as in the game)."""
    return {
        actor("Obj_Item_Base"): w({"Components": BASE_COMPONENTS}),
        PERFORMER: w({"Performer": "PickUpItem"}),
        BASE_GPT: w({"Components": {"MenuActorParam": ref(MENU)}}),
        MENU: w({"Menu": "Item"}),
        BASE_LIFT: w({"LiftPosOffset": {"X": F32(0.0)}}),
    }


def token_pack():
    c = TOKEN_COMPONENTS
    return {
        **shared(),
        actor(tokens.TOKEN): w({"$parent": work(actor("Obj_Item_Base")), "Components": c}),
        member(c["AIInfoRef"]): w({"RootAIRef": "Work/AI/Root/Item_Token_Gold.root.ain"}),
        tokens.TOKEN_GRAPH: TOKEN_GRAPH_BYTES,
        member(c["ASInfoRef"]): w({"AutoPlayASName": "Rotate_Obj"}),
        member(c["AnimationRef"]): w({"AnimationResources": [{"ModelProjectName": "Obj_Token_Gold_Animation"}]}),
        member(c["AttentionSenderRef"]): w({"ClientList": ["LookOnly_High_Large"]}),
        member(c["BlackboardRef"]): w({"BlackboardParamTables": [work(TOKEN_BLACKBOARD)]}),
        TOKEN_BLACKBOARD: w(
            {
                "BlackboardParamBoolArray": [
                    {"BBKey": tokens.ATTENTION_KEY, "InitVal": True, "IsInstanceParam": False}
                ],
                "BlackboardParamU64Array": [
                    {"BBKey": tokens.SOURCE_HASH_KEY, "InitVal": U64(0), "IsInstanceParam": False}
                ],
            }
        ),
        member(c["DeathRef"]): w(
            {"$parent": work(tokens.DEATH_DEFAULT), "DeathProcedures": work(tokens.death_table(tokens.TOKEN_ITEM))}
        ),
        member(c["ELinkRef"]): w({"UserName": "Obj_Token_Gold"}),
        member(c["GameParameterTableRef"]): w({"$parent": work(BASE_GPT)}),
        member(c["LiftableRef"]): w(
            {"$parent": work(BASE_LIFT), "AdditionalLiftablePositionsList": {"Shootable_Hook": {"Bone": "Skl_Root"}}}
        ),
        member(c["ModelInfoRef"]): w({"FmdbName": "Obj_Token_Gold", "ModelProjectName": "Obj_Token_Gold"}),
        member(c["PhysicsRef"]): w({"ControllerSetPath": work(TOKEN_CONTROLLER)}),
        TOKEN_CONTROLLER: w(
            {"ControllerEntityNamePathAry": [{"Name": "Body"}], "RigidBodyEntityNamePathAry": [{"Name": "Body"}]}
        ),
        member(c["PouchContentRef"]): w(
            {
                "$parent": work(tokens.POUCH_DEFAULT),
                "DefaultAutoGet": True,
                "FixedMaxNum": I32(100),
                "PlayGetEventManyTimes": True,
                "PouchActor": work(actor(tokens.TOKEN_ITEM)),
                "SpecialDeal": U32(2855325032),
            }
        ),
        member(c["SLinkRef"]): w({"UserName": "Obj_Token_Gold"}),
    }


def boomerang_pack():
    c = BOOMERANG_COMPONENTS
    base = actor("Item_EventObject_Base")
    performer = "Component/EventPerformerParam/PouchContent.engine__component__EventPerformerParam.bgyml"
    weapon = "GameParameter/Boomerang/Item_Boomerang.game__player__Boomerang.bgyml"
    return {
        base: w({"Components": {"EventPerformerRef": ref(performer), "PouchContentRef": ref(tokens.POUCH_DEFAULT)}}),
        performer: w({"Performer": "Inventory"}),
        actor("Item_Boomerang"): w({"$parent": work(base), "Components": c}),
        member(c["ASInfoRef"]): w({"AutoPlayASName": ""}),
        member(c["AnimationRef"]): w({"AnimationResources": [{"ModelProjectName": "Item_Boomerang_Animation"}]}),
        member(c["GameParameterTableRef"]): w({"Components": {"Boomerang": ref(weapon)}}),
        weapon: w({"Range": F32(10.0)}),
        member(c["ModelInfoRef"]): w({"FmdbName": "Item_Boomerang", "ModelProjectName": "Item_Boomerang"}),
        member(c["PouchContentRef"]): w(
            {
                "$parent": work(tokens.POUCH_DEFAULT),
                "Category": U32(957554845),
                "GetType": U32(1746592023),
                "PouchActor": work(actor("Item_Boomerang")),
            }
        ),
    }


def shield_pack():
    c = SHIELD_COMPONENTS
    blackboard = "Component/Blackboard/BlackboardParamTable/DropItem.engine__component__BlackboardParamTable.bgyml"
    equipment = "GameParameter/PlayerEquipmentActor/Obj_Shield_Hylian.game__actor__PlayerEquipmentActor.bgyml"
    controller = "Phive/ControllerSetParam/Obj_Shield_Hylian.phive__ControllerSetParam.bgyml"
    return {
        **shared(),
        actor("Obj_Shield_Hylian"): w({"$parent": work(actor("Obj_Item_Base")), "Components": c}),
        member(BASE_COMPONENTS["AIInfoRef"]): w({"RootAIRef": "Work/AI/Root/DropItem.root.ain"}),
        member(BASE_COMPONENTS["BlackboardRef"]): w({"BlackboardParamTables": [work(blackboard)]}),
        blackboard: w({"BlackboardParamBoolArray": [{"BBKey": "IsCreateByDrop", "InitVal": False}]}),
        member(BASE_COMPONENTS["DeathRef"]): w({"DeathProcedures": work(tokens.death_table("DropItem"))}),
        ITEM_OBJ: w({"AutoPlayASName": ""}),
        member(c["AnimationRef"]): w({"AnimationResources": [{"ModelProjectName": "Weapon_Shield_Hylian_Animation"}]}),
        member(c["ELinkRef"]): w({"UserName": "Obj_Shield_Hylian"}),
        member(c["GameParameterTableRef"]): w(
            {"$parent": work(BASE_GPT), "Components": {"PlayerEquipmentActor": ref(equipment)}}
        ),
        equipment: w({"Adult": work(actor("Weapon_Shield_Hylian")), "Child": work(actor("Weapon_Shield_Hylian"))}),
        member(c["LiftableRef"]): w({"$parent": work(BASE_LIFT)}),
        member(c["ModelInfoRef"]): w({"FmdbName": "Weapon_Shield_Hylian", "ModelProjectName": "Weapon_Shield_Hylian"}),
        member(c["PhysicsRef"]): w({"ControllerSetPath": work(controller)}),
        controller: w({"Body": "Shield"}),
        member(c["PouchContentRef"]): w(
            {
                "$parent": work(AUTO_PICK),
                "GetType": U32(1746592023),
                "PlayGetEventManyTimes": True,
                "PouchActor": work(actor("Weapon_Shield_Hylian")),
            }
        ),
        AUTO_PICK: w({"$parent": work(tokens.POUCH_DEFAULT), "Category": U32(3520794636), "DefaultAutoGet": True}),
        member(c["SLinkRef"]): w({"UserName": "Obj_Shield_Hylian"}),
    }


def enemy_pack():
    drop_blackboard = "Component/Blackboard/BlackboardParamTable/Drop.engine__component__BlackboardParamTable.bgyml"
    drop_default = "Component/DropParam/Default.game__component__DropParam.bgyml"
    drop = "Component/DropParam/Enemy_Skulltula_Gold.game__component__DropParam.bgyml"
    subtable = "Drop/DropSubTable/DropTable_Token_Gold.game__drop__DropSubTable.bgyml"
    death_common = "Component/DeathParam/EnemyCommon.game__component__DeathParam.bgyml"
    death = "Component/DeathParam/Enemy_Skulltula_Gold.game__component__DeathParam.bgyml"
    wall = actor("Enemy_Skullwalltula")
    return {
        wall: w(
            {
                "Components": {
                    "ActorGameDataSetting": ref(tokens.NO_RESPAWN),
                    "DeathRef": ref(death_common),
                    "DropRef": ref(drop_default),
                }
            }
        ),
        actor(tokens.ENEMY): w({"$parent": work(wall), "Components": {"DeathRef": ref(death), "DropRef": ref(drop)}}),
        drop_default: w({"BlackboardTableRef": work(drop_blackboard)}),
        drop: w({"$parent": work(drop_default), "DropTableResourceList": [tokens.TOKEN_DROP_TABLE]}),
        member(tokens.TOKEN_DROP_TABLE): w({"SubTableList": [work(subtable)]}),
        subtable: w(
            {
                "Items": [
                    {"DropActorName": work(actor(tokens.TOKEN)), "DropCreateCount": I32(1), "DropProbability": I32(100)}
                ]
            }
        ),
        drop_blackboard: w(
            {
                "BlackboardParamStringArray": [
                    {"BBKey": "Drop__DropTable", "IsInstanceParam": True},
                    {"BBKey": tokens.DROP, "IsInstanceParam": True},
                    {"BBKey": "Drop__DropTableOverWrite", "IsInstanceParam": False},
                ]
            }
        ),
        death_common: w(
            {"$parent": work(tokens.DEATH_DEFAULT), "DeathProcedures": work(tokens.death_table("EnemyCommon"))}
        ),
        death: w({"$parent": work(death_common), "DeathProcedures": work(tokens.death_table(tokens.ENEMY))}),
        tokens.ENEMY_GRAPH: ENEMY_GRAPH_BYTES,
    }


def death_tables():
    table = tokens.death_table
    kind = tokens.DEATH_TABLE_TYPE
    return {
        table("Default"): {
            "TableType": kind,
            "CellList": {
                "LifeDepleted___Data": {"IsDropItem": True, "IsSetRespawnFlagToFalse": True, "IsWaitForSignal": False},
                "PickedUp___Data": {"IsSetRespawnFlagToFalse": True},
            },
        },
        table("Default_AlwaysRespawn"): {
            "$parent": work(table("Default")),
            "CellList": {"PickedUp___Data": {"IsSetRespawnFlagToFalse": False}},
        },
        table(tokens.TOKEN_ITEM): {
            "$parent": work(table("Default_AlwaysRespawn")),
            "TableType": kind,
            "CellList": {"PickedUp___Data": {"IsSetRespawnFlagToFalse": True, "IsWaitForSignal": True}},
        },
        table("EnemyCommon"): {
            "$parent": work(table("Default")),
            "CellList": {"LifeDepleted___Data": {"IsWaitForSignal": True}},
        },
        table(tokens.ENEMY): {
            "$parent": work(table("EnemyCommon")),
            "TableType": kind,
            "CellList": {"LifeDepleted___Data": {"IsSetGmdRespawnFlagToFalse": False}},
        },
    }


AABB = {"X": F32(0.25), "Y": F32(0.5), "Z": F32(0.75)}


def actor_rows():
    return [
        {"ClassName": "GameActor", "__RowId": "Aaa_Unrelated"},
        {
            "ActorName": "Item_Boomerang",
            "AnimationResources": [{"ModelProjectName": "Item_Boomerang_Animation"}],
            "CalcRadius": F32(40.0),
            "ClassName": "GameActor",
            "DisplayRadius": F32(40.0),
            "FmdbName": "Item_Boomerang",
            "InstanceHeapSize": I32(114848),
            "ModelAabbMax": AABB,
            "ModelAabbMin": AABB,
            "ModelProjectName": "Item_Boomerang",
            "PreActorRenderInfoHeapSize": I32(29192),
            "__RowId": "Item_Boomerang",
        },
        {
            "ActorName": "Weapon_Shield_Hylian",
            "AnimationResources": [{"ModelProjectName": "Weapon_Shield_Hylian_Animation"}],
            "CalcRadius": F32(45.0),
            "ClassName": "GameActor",
            "DisplayRadius": F32(45.0),
            "ELinkUserName": "Obj_Shield_Hylian",
            "FmdbName": "Weapon_Shield_Hylian",
            "InstanceHeapSize": I32(138376),
            "ModelAabbMax": {"X": F32(0.4), "Y": F32(0.2), "Z": F32(0.3)},
            "ModelAabbMin": AABB,
            "ModelProjectName": "Weapon_Shield_Hylian",
            "PreActorRenderInfoHeapSize": I32(7816),
            "SLinkUserName": "Obj_Shield_Hylian",
            "__RowId": "Obj_Shield_Hylian",
        },
        {
            "ActorName": "Item_Token_Gold",
            "AnimationResources": [{"ModelProjectName": "Obj_Token_Gold_Animation"}],
            "ApplyScaleType": "ScaleMax",
            "CalcRadius": F32(20.0),
            "ClassName": "GameActor",
            "DisplayRadius": F32(300.0),
            "ELinkUserName": "Obj_Token_Gold",
            "FmdbName": "Obj_Token_Gold",
            "InstanceHeapSize": I32(139576),
            "LoadRadius": F32(400.0),
            "ModelAabbMax": AABB,
            "ModelAabbMin": AABB,
            "ModelProjectName": "Obj_Token_Gold",
            "PreActorRenderInfoHeapSize": I32(7608),
            "SLinkUserName": "Obj_Token_Gold",
            "__RowId": "Obj_Token_Gold",
        },
        {"ClassName": "GameActor", "__RowId": "Zzz_Unrelated"},
    ]


def game_actor_rows():
    rows = [{"__RowId": row["__RowId"]} for row in actor_rows()]
    rows[3] = {"IsRespawn": True, "MainRigidBodyLayer": "SmallObject", "__RowId": "Obj_Token_Gold"}
    return rows


def pouch_rows():
    """The grant fields each family shape reads, as the dump's rows carry them (I32 counts, string enums)."""
    return [
        {
            "AssignableItem": "Boomerang",
            "BundleActorNum": I32(1),
            "PouchCategory": "Material",
            "PouchGetType": "Large",
            "PouchSpecialDeal": "None",
            "PouchTabCategory": "Item",
            "__RowId": "Item_Boomerang",
        },
        {
            "BundleActorNum": I32(1),
            "FixedMaxNum": I32(100),
            "PouchCategory": "KeyItem",
            "PouchGetType": "Medium",
            "PouchSpecialDeal": "TokenGold",
            "PouchStockable": True,
            "PouchTabCategory": "KeyItem",
            "__RowId": "Item_Token_Gold",
        },
        {
            "AdultEquipment": work(actor("Weapon_Shield_Hylian")),
            "BundleActorNum": I32(1),
            "ChildEquipment": work(actor("Weapon_Shield_Hylian")),
            "PouchCategory": "Shield",
            "PouchGetType": "Large",
            "PouchSpecialDeal": "None",
            "PouchTabCategory": "Equipment",
            "__RowId": "Obj_Shield_Hylian",
        },
        {"FixedMaxNum": I32(100), "PouchSpecialDeal": "TokenGold", "__RowId": "Obj_Token_Gold"},
    ]


def game_data(sources=(TREE, TOWER, LONE)):
    rows = []
    for source in sources:
        for key in (source, source ^ tokens.COMPANION_XOR):
            rows.append({"Hash": U64(key), "ResetTypeValue": I32(24), "SaveFileIndex": I32(0)})
    return {"Data": {"Bool64bitKey": rows}}


def banc_tree(*, reverse=False):
    actors = [
        {
            "Dynamic": {"Enemy_Skulltula_Gold_AppearPopOut": True},
            "Gyaml": tokens.ENEMY,
            "Hash": U64(TREE),
            "Links": [{"Dst": U64(CHEST)}],
            "Translate": [F32(1.0), F32(2.0), F32(3.0)],
        },
        {
            "Dynamic": {"Enemy_Skulltula_Gold_Nocturnal": True},
            "Gyaml": tokens.ENEMY,
            "Hash": U64(TOWER),
            "Translate": [F32(4.0), F32(5.0), F32(6.0)],
        },
        {"Gyaml": tokens.ENEMY, "Hash": U64(LONE), "Translate": [F32(7.0), F32(8.0), F32(9.0)]},
        {
            "Dynamic": {tokens.DROP: "Obj_Rupee_Blue"},
            "Gyaml": "Obj_TBox_A_01",
            "Hash": U64(CHEST),
            "Translate": [F32(0.0), F32(0.0), F32(0.0)],
        },
    ]
    return {
        "Actors": actors[::-1] if reverse else actors,
        "AiGroups": [{"Hash": U64(80), "References": [{"Reference": U64(TOWER)}]}],
    }


def census(*sources):
    return [
        Location(
            source,
            "gold_skulltula",
            "Test",
            None,
            (ADULT, CHILD),
            "both",
            (0.0, 0.0, 0.0),
            tokens.ENEMY,
            tokens.TOKEN,
            None,
            True,
        )
        for source in (sources or (TREE, TOWER, LONE))
    ]


def native_packs():
    return {
        tokens.ENEMY: enemy_pack(),
        tokens.TOKEN: token_pack(),
        "Item_Boomerang": boomerang_pack(),
        "Obj_Shield_Hylian": shield_pack(),
    }


def put(root, path, data):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    dictionaries = zsdic.Dictionaries.from_romfs(root)
    target.write_bytes(dictionaries.compress(path, data) if path.endswith(".zs") else data)


def raw(root, path, dictionaries_root=None):
    data = (root / path).read_bytes()
    if not path.endswith(".zs"):
        return data
    return zsdic.Dictionaries.from_romfs(dictionaries_root or root).decompress(path, data)


def edit_pack(root, owner, name, change):
    path = tokens.pack_path(owner)
    pack = sarc.read(raw(root, path))
    tree = byml.read(pack[name])
    change(tree)
    pack[name] = byml.write(tree)
    put(root, path, sarc.write(pack))


def edit_byml(root, path, change, byte_order="little"):
    tree = byml.read(raw(root, path))
    change(tree)
    put(root, path, byml.write(tree, byte_order))


@pytest.fixture
def world(tmp_path, zsdic_pack, monkeypatch):
    monkeypatch.setattr(tokens, "TOKEN_GRAPH_SHA256", hashlib.sha256(TOKEN_GRAPH_BYTES).hexdigest())
    monkeypatch.setattr(tokens, "ENEMY_GRAPH_SHA256", hashlib.sha256(ENEMY_GRAPH_BYTES).hexdigest())
    root = tmp_path / "romfs"
    (root / "Pack").mkdir(parents=True)
    (root / "Pack/ZsDic.pack.zs").write_bytes(zsdic_pack)
    table = rstb.ResourceSizeTable()
    for owner, pack in native_packs().items():
        put(root, tokens.pack_path(owner), sarc.write(pack))
        table.set(tokens.pack_path(owner), 1 << 20)
        for name in pack:
            table.set(name, NATIVE_ENTRY)
    for path, tree in death_tables().items():
        put(root, path, byml.write(tree))
    for path, rows in zip(tokens.REGISTRIES, (actor_rows(), game_actor_rows(), pouch_rows()), strict=True):
        put(root, path, byml.write(rows))
        table.set(path, 1 << 20)
    put(root, GAME_DATA_LIST, byml.write(game_data(), "big"))
    for path in (ADULT, CHILD):
        put(root, path, byml.write(banc_tree()))
        table.set(path, 1 << 20)
    put(root, rstb.TABLE_PATH, rstb.write(table))
    return root


def test_reward_changes_only_the_drop_selector_on_every_copy(world):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    assert delivery.drops == {TREE: BOOMERANG_PICKUP, TOWER: SHIELD_PICKUP}
    assert delivery.pickups == {"Item_Boomerang": BOOMERANG_PICKUP, "Obj_Shield_Hylian": SHIELD_PICKUP}
    assert set(delivery.changes) == {ADULT, CHILD, *tokens.REGISTRIES}
    for path in (ADULT, CHILD):
        after = byml.read(delivery.changes[path](raw(world, path)))
        selected = {}
        for placed in after["Actors"]:
            if int(placed["Hash"]) in CORE and tokens.DROP in placed.get("Dynamic", {}):
                selected[int(placed["Hash"])] = placed["Dynamic"].pop(tokens.DROP)
        assert selected == delivery.drops
        assert byml.same(after, banc_tree())  # Hash, transform, links, groups, appearance fields: all native


def test_a_reward_on_a_source_without_dynamic_parameters_adds_only_the_selector(world):
    delivery = tokens.build(world, {LONE: "Obj_Shield_Hylian"}, census(), rewards=ALLOWED)
    after = byml.read(delivery.changes[CHILD](raw(world, CHILD)))
    lone = next(placed for placed in after["Actors"] if placed["Hash"] == LONE)
    assert lone.pop("Dynamic") == {tokens.DROP: SHIELD_PICKUP}
    assert byml.same(after, banc_tree())


def test_token_assignments_keep_the_native_drop_and_change_nothing(world):
    delivery = tokens.build(world, {LONE: "Item_Token_Gold", TREE: "Item_Token_Gold"}, census(), rewards=ALLOWED)
    assert (dict(delivery.changes), dict(delivery.new_files), dict(delivery.pickups), dict(delivery.drops)) == (
        {},
        {},
        {},
        {},
    )


def test_no_global_token_pack_ai_global_or_enemy_change(world):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    touched = set(delivery.changes) | set(delivery.new_files)
    assert not touched & {tokens.TOKEN_PACK, tokens.ENEMY_PACK, "Pack/AI.Global.Product.111.pack.zs"}
    assert set(delivery.new_files) == {
        tokens.pack_path(BOOMERANG_PICKUP),
        tokens.pack_path(SHIELD_PICKUP),
    }


def test_generated_pickups_take_token_mechanism_and_reward_identity(world):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    natives = native_packs()
    token = actor_packs.closure([natives[tokens.TOKEN]], tokens.TOKEN).components
    mechanism = set(token) - set(tokens.IDENTITY) - set(tokens.WORLD_DISPLAY)
    for path, file in delivery.new_files.items():
        pack = sarc.read(file.data)
        item = next(item for item, pickup in delivery.pickups.items() if tokens.pack_path(pickup) == path)
        pickup = delivery.pickups[item]
        for name, source in file.copied.items():
            assert sarc.read(raw(world, source))[name] == pack[name], name
        derived = f"Component/PouchContentParam/{pickup}.game__component__PouchContentParam.bgyml"
        assert set(pack) - set(file.copied) == {actor(pickup), derived}  # neither native pouch has the full policy
        found = actor_packs.closure([pack], pickup)
        assert set(found.members) == set(pack)  # closed: nothing unreferenced, nothing missing that natives pack
        effective = found.components
        donor = actor_packs.closure([natives[item]], item).components
        assert {key: effective.get(key) for key in mechanism} == {key: token[key] for key in mechanism}
        for name in (tokens.TOKEN_GRAPH, TOKEN_BLACKBOARD, TOKEN_CONTROLLER, member(token["DeathRef"])):
            assert pack[name] == natives[tokens.TOKEN][name]
        assert tokens.canonical(effective) == CANONICAL[item]
        assert (effective["ModelInfoRef"], effective["AnimationRef"]) == (donor["ModelInfoRef"], donor["AnimationRef"])
        if item == "Item_Boomerang":  # no native world pickup: generic item display, no effect/sound user
            assert (effective["ASInfoRef"], effective["ASRef"]) == (ref(ITEM_OBJ), "?AS/Item_Common.root.asb")
            assert "ELinkRef" not in effective and "SLinkRef" not in effective
            assert effective["GameParameterTableRef"] == token["GameParameterTableRef"]
        else:
            assert {key: effective.get(key) for key in tokens.WORLD_DISPLAY} == {
                key: donor.get(key) for key in tokens.WORLD_DISPLAY
            }


def test_pickup_pouch_grants_the_reward_not_a_token(world):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    grants = {BOOMERANG_PICKUP: "Item_Boomerang", SHIELD_PICKUP: "Weapon_Shield_Hylian"}
    for path, file in delivery.new_files.items():
        pack = sarc.read(file.data)
        pickup = next(name for name in grants if tokens.pack_path(name) == path)
        effective = actor_packs.closure([pack], pickup).components
        derived = byml.read(pack[member(effective["PouchContentRef"])])
        native_pouch = {BOOMERANG_PICKUP: BOOMERANG_COMPONENTS, SHIELD_PICKUP: SHIELD_COMPONENTS}[pickup]
        assert derived == {"$parent": work(member(native_pouch["PouchContentRef"])), **tokens.POLICY}
        pouch = actor_packs.resolve_node([pack], member(effective["PouchContentRef"]), builtin=tokens.POUCH_DEFAULT)
        assert pouch["PouchActor"] == work(actor(grants[pickup]))
        assert "SpecialDeal" not in pouch and "FixedMaxNum" not in pouch  # no token stock or special deal
        assert all(pouch[key] == value for key, value in tokens.POLICY.items())
        assert pouch["IsPlayGetEventPouchMax"] is True  # get events for full-pouch acquisitions (section 10.3)


def test_a_reward_granting_its_own_identity_gets_a_pouch_naming_its_canonical_actor(world):
    """Item_Hammer-like donors name no PouchActor; the pickup names its grant explicitly, as the played pickups do: the
    donor's canonical ActorName, the identity native implicit grants record (IsGet.<canonical>)."""
    for owner, components in (("Item_Boomerang", BOOMERANG_COMPONENTS), ("Obj_Shield_Hylian", SHIELD_COMPONENTS)):
        edit_pack(world, owner, member(components["PouchContentRef"]), lambda tree: tree.pop("PouchActor"))
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    for pickup, components, grant in (
        (BOOMERANG_PICKUP, BOOMERANG_COMPONENTS, "Item_Boomerang"),
        (SHIELD_PICKUP, SHIELD_COMPONENTS, "Weapon_Shield_Hylian"),  # canonical, not the Obj_ row
    ):
        pack = sarc.read(delivery.new_files[tokens.pack_path(pickup)].data)
        effective = actor_packs.closure([pack], pickup).components
        derived = byml.read(pack[member(effective["PouchContentRef"])])
        assert derived == {
            "$parent": work(member(components["PouchContentRef"])),
            **tokens.POLICY,
            "PouchActor": work(actor(grant)),
        }


def test_a_bundle_naming_no_grant_keeps_naming_none_and_one_naming_its_contents_keeps_them(world):
    """Obj_Rupee_Red-like bundles name no PouchActor: like every native bundle naming none (TBox_Rupee_Red), the
    pickup's pouch names none and keeps the bundle; one naming its BundleActor (Obj_Bombchu) keeps naming it."""
    bundle = {"IsBundle": True, "BundleActor": work(actor("Obj_Rupee_Green")), "BundleActorNum": I32(20)}
    pouch_member = member(BOOMERANG_COMPONENTS["PouchContentRef"])

    def pickup_pouch():
        delivery = tokens.build(world, {TREE: "Item_Boomerang"}, census(), rewards=ALLOWED)
        pack = sarc.read(delivery.new_files[tokens.pack_path(BOOMERANG_PICKUP)].data)
        effective = actor_packs.closure([pack], BOOMERANG_PICKUP).components
        assert byml.read(pack[member(effective["PouchContentRef"])]) == {"$parent": work(pouch_member), **tokens.POLICY}
        pouch = actor_packs.resolve_node([pack], member(effective["PouchContentRef"]), builtin=tokens.POUCH_DEFAULT)
        assert {key: pouch[key] for key in bundle} == bundle
        return pouch.get("PouchActor")

    def make_bundle(tree):
        tree.pop("PouchActor")
        tree.update(bundle)

    edit_pack(world, "Item_Boomerang", pouch_member, make_bundle)
    assert pickup_pouch() is None
    edit_pack(world, "Item_Boomerang", pouch_member, lambda tree: tree.update(PouchActor=bundle["BundleActor"]))
    assert pickup_pouch() == bundle["BundleActor"]


def test_pickups_keep_the_token_source_hash_and_reason_10_completion_contract(world):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    native = tokens.Romfs(world)
    token_pack_members = native.pack(tokens.TOKEN)
    token = actor_packs.closure([token_pack_members], tokens.TOKEN).components
    token_death = tokens.death_procedures(native, token_pack_members, token["DeathRef"])
    for path, file in delivery.new_files.items():
        pack = sarc.read(file.data)
        pickup = next(name for name in delivery.pickups.values() if tokens.pack_path(name) == path)
        effective = actor_packs.closure([pack], pickup).components
        keys = tokens.source_hash_keys([pack], effective)
        assert keys == [{"BBKey": tokens.SOURCE_HASH_KEY, "InitVal": 0, "IsInstanceParam": False}]
        attention = tokens.blackboard_entries([pack], effective, "BlackboardParamBoolArray", tokens.ATTENTION_KEY)
        assert attention == [{"BBKey": tokens.ATTENTION_KEY, "InitVal": True, "IsInstanceParam": False}]
        assert tokens.physics_bodies([pack], effective) == (["Body"], ["Body"])
        death = tokens.death_procedures(native, pack, effective["DeathRef"])
        assert death == token_death
        assert death["PickedUp___Data"]["IsWaitForSignal"] is True  # collection waits for the Hash callback
        root = byml.read(pack[member(effective["AIInfoRef"])])["RootAIRef"]
        assert member(root) == tokens.TOKEN_GRAPH and pack[tokens.TOKEN_GRAPH] == TOKEN_GRAPH_BYTES
    enemy = native.pack(tokens.ENEMY)
    components = actor_packs.resolve([enemy], actor(tokens.ENEMY))[0]["Components"]
    life = tokens.death_procedures(native, enemy, components["DeathRef"])["LifeDepleted___Data"]
    assert (life["IsSetGmdRespawnFlagToFalse"], life["IsSetRespawnFlagToFalse"]) == (False, True)  # kill saves nothing


def test_registry_rows_share_one_index_and_leave_every_native_row(world):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    tables = {path: byml.read(delivery.changes[path](raw(world, path))) for path in tokens.REGISTRIES}
    native = dict(zip(tokens.REGISTRIES, (actor_rows(), game_actor_rows(), pouch_rows()), strict=True))
    names = set(delivery.pickups.values())
    ids = {path: [row["__RowId"] for row in table] for path, table in tables.items()}
    assert ids[tokens.ACTOR_INFO] == ids[tokens.GAME_ACTOR_INFO]
    assert ids[tokens.ACTOR_INFO].index(BOOMERANG_PICKUP) == 2 and ids[tokens.ACTOR_INFO].index(SHIELD_PICKUP) == 3
    for path, table in tables.items():
        assert ids[path] == sorted(ids[path], key=lambda name: name.encode())
        assert byml.same([row for row in table if row["__RowId"] not in names], native[path])
    rows = {path: {row["__RowId"]: row for row in table} for path, table in tables.items()}
    token_row, boomerang, shield = (rows[tokens.ACTOR_INFO][name] for name in ("Obj_Token_Gold", *sorted(names)))
    assert (boomerang["ActorName"], boomerang["FmdbName"], boomerang["ModelProjectName"]) == ("Item_Boomerang",) * 3
    assert boomerang["AnimationResources"] == [{"ModelProjectName": "Item_Boomerang_Animation"}]
    assert "ELinkUserName" not in boomerang and "SLinkUserName" not in boomerang
    assert (boomerang["DisplayRadius"], boomerang["ApplyScaleType"]) == (token_row["DisplayRadius"], "ScaleMax")
    assert (boomerang["InstanceHeapSize"], boomerang["PreActorRenderInfoHeapSize"]) == (139576 + 114848, 29192)
    assert (shield["ActorName"], shield["ELinkUserName"], shield["SLinkUserName"]) == (
        "Weapon_Shield_Hylian",
        "Obj_Shield_Hylian",
        "Obj_Shield_Hylian",
    )
    for name in names:
        game = dict(rows[tokens.GAME_ACTOR_INFO][name])
        assert game.pop("__RowId") == name and game == {"IsRespawn": True, "MainRigidBodyLayer": "SmallObject"}
    pouch = {row["__RowId"]: row for row in pouch_rows()}
    for name, item in ((BOOMERANG_PICKUP, "Item_Boomerang"), (SHIELD_PICKUP, "Obj_Shield_Hylian")):
        assert byml.same(rows[tokens.POUCH_ACTOR_INFO][name], {**pouch[item], "__RowId": name})


def test_one_pickup_per_reward_and_identity_survives_actor_reordering(world):
    delivery = tokens.build(world, {TREE: "Obj_Shield_Hylian", TOWER: "Obj_Shield_Hylian"}, census(), rewards=ALLOWED)
    assert list(delivery.new_files) == [tokens.pack_path(SHIELD_PICKUP)]
    after = byml.read(delivery.changes[ADULT](byml.write(banc_tree(reverse=True))))
    selected = {
        int(a["Hash"]): a.get("Dynamic", {}).get(tokens.DROP) for a in after["Actors"] if a["Gyaml"] == tokens.ENEMY
    }
    assert selected == {TREE: SHIELD_PICKUP, TOWER: SHIELD_PICKUP, LONE: None}


def test_build_is_deterministic(world):
    first, second = (tokens.build(world, dict(reversed(CORE.items())), census(), rewards=ALLOWED) for _ in range(2))
    assert [(path, f.data, dict(f.copied)) for path, f in first.new_files.items()] == [
        (path, f.data, dict(f.copied)) for path, f in second.new_files.items()
    ]
    for path in first.changes:
        assert first.changes[path](raw(world, path)) == second.changes[path](raw(world, path))


@pytest.mark.parametrize(
    ("placements", "sources", "message"),
    [
        ({TREE: "Item_Hookshot"}, None, "not an allowed reward"),
        ({TREE: "Obj_Token_Gold"}, None, "not an allowed reward"),
        ({TREE: ""}, None, "not an allowed reward"),
        ({99: "Item_Boomerang"}, None, "not a saved"),
        ({TREE: "Item_Boomerang"}, "unsaved", "not a saved"),
    ],
)
def test_unadmitted_rewards_and_non_sources_are_refused_before_reading(world, placements, sources, message):
    locations = census()
    if sources == "unsaved":
        locations = [Location(**{**vars(location), "has_save_flag": False}) for location in locations]
    with pytest.raises(PatchError, match=message):
        tokens.build(world / "absent", placements, locations, rewards=ALLOWED)


@pytest.mark.parametrize(
    ("rewards", "message"),
    [
        ({"Item_Boomerang": "boomerangs"}, "unknown grant families"),
        ({"Obj_Token_Gold": "token"}, "only Item_Token_Gold"),
        ({"Item_Token_Gold": "fixed_major"}, "only Item_Token_Gold"),
    ],
)
def test_an_allowed_set_with_unknown_or_misplaced_families_is_refused_before_reading(world, rewards, message):
    with pytest.raises(PatchError, match=message):
        tokens.build(world / "absent", {}, census(), rewards=rewards)


def test_a_declared_family_must_be_the_dump_rows_native_shape(world):
    with pytest.raises(PatchError, match="native grant family 'fixed_major', not the declared 'equipment'"):
        tokens.build(world, {TREE: "Item_Boomerang"}, census(), rewards={"Item_Boomerang": "equipment"})
    with pytest.raises(PatchError, match="native grant family 'equipment', not the declared 'fixed_major'"):
        tokens.build(world, {TOWER: "Obj_Shield_Hylian"}, census(), rewards={"Obj_Shield_Hylian": "fixed_major"})
    # The native token row classifies as the token family: a token placement passes and writes nothing.
    assert tokens.build(world, {TREE: "Item_Token_Gold"}, census(), rewards=ALLOWED).drops == {}


def test_a_changed_grant_row_is_refused_with_its_values(world):
    edit_byml(world, tokens.POUCH_ACTOR_INFO, lambda rows: rows[0].update(BundleActor="Work/Actor/Item_Arrow.gyml"))
    with pytest.raises(PatchError, match=r"native grant family None, not the declared 'fixed_major'.*BundleActor"):
        tokens.build(world, CORE, census(), rewards=ALLOWED)
    edit_byml(world, tokens.POUCH_ACTOR_INFO, lambda rows: rows.pop(0))
    with pytest.raises(PatchError, match="Item_Boomerang: no native"):
        tokens.build(world, CORE, census(), rewards=ALLOWED)


def test_a_grant_family_needs_an_explicit_declaration_and_the_matching_native_shape(world):
    """A rupee-shaped row (as Obj_Rupee_Red's) builds only when the caller declares that family: the allowed set is
    the only gate. The core set here (:data:`ALLOWED`) declares no 'rupee'; production declares a family only through
    the members ``clawshot.generate.tokens.REWARDS`` admits."""
    rupee = {
        "BundleActor": "Work/Actor/Obj_Rupee_Green.engine__actor__ActorParam.gyml",
        "BundleActorNum": I32(20),
        "PouchCategory": "Rupee",
        "PouchGetType": "Small",
        "PouchSpecialDeal": "None",
        "PouchTabCategory": "KeyItem",
        "__RowId": "Obj_Shield_Hylian",
    }
    edit_byml(world, tokens.POUCH_ACTOR_INFO, lambda rows: rows.__setitem__(2, rupee))
    with pytest.raises(PatchError, match="native grant family 'rupee', not the declared 'equipment'"):
        tokens.build(world, {TOWER: "Obj_Shield_Hylian"}, census(), rewards=ALLOWED)
    delivery = tokens.build(world, {TOWER: "Obj_Shield_Hylian"}, census(), rewards={"Obj_Shield_Hylian": "rupee"})
    assert delivery.drops == {TOWER: SHIELD_PICKUP}
    rows = byml.read(delivery.changes[tokens.POUCH_ACTOR_INFO](raw(world, tokens.POUCH_ACTOR_INFO)))
    assert byml.same(next(row for row in rows if row["__RowId"] == SHIELD_PICKUP), {**rupee, "__RowId": SHIELD_PICKUP})


def _row(**fields):
    return {"BundleActorNum": I32(1), "PouchSpecialDeal": "None", **fields}


def _item(**fields):
    return _row(**{"PouchTabCategory": "Item", "PouchGetType": "Large", **fields})


def _gear(**fields):
    return _row(**{"PouchTabCategory": "Equipment", "PouchGetType": "Large", **fields})


def _key(**fields):
    return _row(**{"PouchTabCategory": "KeyItem", "PouchCategory": "KeyItem", **fields})


def _small(**fields):
    return _item(**{"PouchGetType": "Small", **fields})


def _rupee(get="Small", **fields):
    return _row(PouchTabCategory="KeyItem", PouchCategory="Rupee", PouchGetType=get, **fields)


MAGIC = {"ExpansionAvility": "MPMaxUP", "MPMax": I32(24)}
BOTH = {"AdultEquipment": "A", "ChildEquipment": "C"}
CURE = {"PouchCategory": "CureItem", "PouchSpecialDeal": "NotPushToPouch", "IsUsable": True}
# One row per approved table family, each with the fields of its native rows (RSDB/PouchActorInfo, build e0f3ccfa).
GRANT_ROWS = {
    "boomerang": (_item(PouchCategory="Material", AssignableItem="B"), "fixed_major"),
    "kokiri sword (child only)": (_gear(PouchCategory="Weapon", ChildEquipment="W"), "equipment"),
    "boots (adult only)": (_gear(PouchCategory="Boot", AdultEquipment="A"), "equipment"),
    "token": (
        _key(PouchGetType="Medium", PouchSpecialDeal="TokenGold", PouchStockable=True, FixedMaxNum=I32(100)),
        "token",
    ),
    "green rupee": (_rupee(PouchStockable=True, SmallBagActor="W", MaxNumGameData="Rupee"), "rupee"),
    "red rupee": (_rupee(BundleActor="G", BundleActorNum=I32(20)), "rupee"),
    "gold rupee": (_rupee("Medium", BundleActor="G", BundleActorNum=I32(200)), "gold_rupee"),
    "heart piece": (_key(PouchGetType="Medium", PouchSpecialDeal="HeartPiece", PouchStockable=True), "heart_piece"),
    "heart container": (
        _key(PouchGetType="Heart", PouchSpecialDeal="HeartContainer", PouchStockable=True),
        "heart_container",
    ),
    "bottle": (_item(PouchCategory="Material", PouchSpecialDeal="Bottle", AssignableItem="BottleA"), "bottle"),
    "bottle with milk": (
        _item(PouchCategory="Material", PouchSpecialDeal="Bottle", AssignableItem="BottleA", BottleItem="MaxMilk"),
        "bottle",
    ),
    "arrows (5)": (
        _gear(PouchCategory="Arrow", PouchGetType="Small", BundleActor="A", BundleActorNum=I32(5)),
        "refill",
    ),
    "deku nuts": (_small(PouchCategory="Material", BundleActor="N", BundleActorNum=I32(3)), "refill"),
    "bombchus (5)": (_item(PouchCategory="Material", BundleActor="C", BundleActorNum=I32(5)), "bombchu"),
    "deku nut capacity": (
        _key(PouchGetType="Large", ExpansionMaxNumActor="N", AfterExpansionMaxNum=I32(30), MaxNumGameData="DekuNut"),
        "fixed_capacity",
    ),
    "magic jar": (_small(**CURE, MPRecover=I32(120)), "magic_recovery"),
    "dins fire": (_item(PouchCategory="Material", PouchGetType="Heart", AssignableItem="D", **MAGIC), "spell"),
    "ice arrows": (
        _item(PouchCategory="Bow", AssignableItem="I", WeaponType="Bow", ShootableActor="N", **MAGIC),
        "magic_arrow",
    ),
    "lens": (_gear(PouchCategory="HeadArmor", PouchSpecialDeal="GlassTruth", **BOTH, **MAGIC), "lens"),
    "stone of agony": (_gear(PouchCategory="KeyItem", PouchSpecialDeal="AgonyStone", **BOTH), "agony_stone"),
    "double defense": (_key(PouchGetType="Heart", PouchSpecialDeal="FairyBlessDefenseDouble"), "double_defense"),
    "scrub business seed": (
        _small(PouchCategory="Material", PouchStockable=True, FixedMaxNum=I32(30), AssignableItem="S"),
        "scrub_seed",
    ),
    "ocarina of time": (_key(PouchGetType="Large", PouchSpecialDeal="Ocarina"), "ocarina"),
    # No shape: bought goods, policy-excluded grants and departures from a family's native fields.
    "bought bottle content": (
        _item(PouchCategory="Material", PouchSpecialDeal="NotPushToPouch", AssignableItem="BottleA", BottleItem="F"),
        None,
    ),
    "bought heart": (_small(**CURE, HitPointRecover=I32(4)), None),
    "boss key": (_key(PouchGetType="Large", PouchSpecialDeal="NotPushToPouch"), None),
    "song": (_key(PouchGetType="Small", PouchSpecialDeal="Melody"), None),
    "magic meter": (_key(PouchGetType="Heart", PouchSpecialDeal="FairyBlessMP", **MAGIC), None),
    "bow": (_gear(PouchCategory="Bow"), None),
    "shield without an equipment target": (_gear(PouchCategory="Shield"), None),
    "assignable bombchus": (_item(PouchCategory="Material", BundleActor="C", AssignableItem="C"), None),
    "magic upgrade on a major": (_item(PouchCategory="Material", AssignableItem="M", **MAGIC), None),
    "spell without magic": (_item(PouchCategory="Material", PouchGetType="Heart", AssignableItem="D"), None),
    "gold rupee without its bundle": (_rupee("Medium"), None),
    "stockable ammo": (_small(PouchCategory="Material", BundleActor="N", PouchStockable=True), None),
}


@pytest.mark.parametrize("name", sorted(GRANT_ROWS))
def test_grant_families_are_native_pouch_shapes(name):
    row, family = GRANT_ROWS[name]
    assert tokens.grant_family({**row, "__RowId": name}) == family


def test_every_family_has_a_classified_row_and_no_row_matches_two():
    assert {family for _, family in GRANT_ROWS.values()} - {None} == set(tokens.FAMILIES)
    for name, (row, _) in GRANT_ROWS.items():
        assert sum(family.matches(row) for family in tokens.FAMILIES.values()) <= 1, name


def test_native_inputs_add_each_rewards_own_pack_once_and_no_token_pack():
    rewards = ["Obj_Shield_Hylian", "Item_Hammer", "Item_Token_Gold", "Item_Boomerang", "Item_Hammer"]
    inputs = tokens.native_inputs(rewards)
    assert inputs[: len(tokens.NATIVE_INPUTS)] == tokens.NATIVE_INPUTS
    assert inputs[len(tokens.NATIVE_INPUTS) :] == (tokens.pack_path("Item_Boomerang"), tokens.pack_path("Item_Hammer"))


def test_a_zero_source_hash_is_refused_it_is_the_transfer_default(world):
    with pytest.raises(PatchError, match="source Hash 0"):
        tokens.build(world, {0: "Item_Boomerang"}, census(0), rewards=ALLOWED)


def _drop_items(tree):
    tree["Items"][0]["DropActorName"] = work(actor("Obj_Rupee_Red"))


STALE_INPUTS = {
    "companion row missing": (
        lambda root: edit_byml(root, GAME_DATA_LIST, lambda t: t["Data"]["Bool64bitKey"].pop(1), byte_order="big"),
        "saved collection row 1002",
    ),
    "companion row not permanent": (
        lambda root: edit_byml(
            root,
            GAME_DATA_LIST,
            lambda t: t["Data"]["Bool64bitKey"][1].update(ResetTypeValue=I32(8)),
            byte_order="big",
        ),
        "saved collection row 1002",
    ),
    "enemy graph changed": (
        lambda root: put(
            root, tokens.ENEMY_PACK, sarc.write({**enemy_pack(), tokens.ENEMY_GRAPH: b"AIB another graph"})
        ),
        "SHA256",
    ),
    "kill would save the source": (
        lambda root: edit_byml(
            root,
            tokens.death_table(tokens.ENEMY),
            lambda t: t["CellList"]["LifeDepleted___Data"].update(IsSetGmdRespawnFlagToFalse=True),
        ),
        "LifeDepleted",
    ),
    "drop table names another actor": (
        lambda root: edit_pack(
            root, tokens.ENEMY, "Drop/DropSubTable/DropTable_Token_Gold.game__drop__DropSubTable.bgyml", _drop_items
        ),
        "drop items",
    ),
    "token graph changed": (
        lambda root: put(
            root, tokens.TOKEN_PACK, sarc.write({**token_pack(), tokens.TOKEN_GRAPH: b"AIB a different graph"})
        ),
        "SHA256",
    ),
    "source hash became an instance parameter": (
        lambda root: edit_pack(
            root,
            tokens.TOKEN,
            TOKEN_BLACKBOARD,
            lambda t: t["BlackboardParamU64Array"][0].update(IsInstanceParam=True),
        ),
        "GoldTokenGmdHash",
    ),
    "pickup no longer waits for the callback": (
        lambda root: edit_byml(
            root,
            tokens.death_table(tokens.TOKEN_ITEM),
            lambda t: t["CellList"]["PickedUp___Data"].update(IsWaitForSignal=False),
        ),
        "PickedUp",
    ),
    "global token pouch experiment applied": (
        lambda root: edit_pack(
            root,
            tokens.TOKEN,
            member(TOKEN_COMPONENTS["PouchContentRef"]),
            lambda t: t.update(PouchActor=work(actor("Item_Boomerang"))),
        ),
        "not the native token",
    ),
    "token pack holds an unreferenced member": (
        lambda root: put(root, tokens.TOKEN_PACK, sarc.write({**token_pack(), "AI/Hidden.module.ainb": b"AIB"})),
        "outside its closure",
    ),
    "token attention disabled": (
        lambda root: edit_pack(
            root,
            tokens.TOKEN,
            TOKEN_BLACKBOARD,
            lambda t: t["BlackboardParamBoolArray"][0].update(InitVal=False),
        ),
        "IsEnableAttention",
    ),
    "graph's physics body renamed": (
        lambda root: edit_pack(
            root, tokens.TOKEN, TOKEN_CONTROLLER, lambda t: t["RigidBodyEntityNamePathAry"][0].update(Name="Main")
        ),
        "physics controllers",
    ),
    "pickup name already registered": (
        lambda root: [
            edit_byml(root, path, lambda t: t.insert(2, {**t[2], "__RowId": SHIELD_PICKUP}))
            for path in (tokens.ACTOR_INFO, tokens.GAME_ACTOR_INFO)
        ],
        "already exists",
    ),
    "registries out of step": (
        lambda root: edit_byml(root, tokens.GAME_ACTOR_INFO, lambda t: t.pop(0)),
        "same rows",
    ),
}


@pytest.mark.parametrize("stale", sorted(STALE_INPUTS))
def test_stale_native_inputs_fail_before_output_with_values(world, stale):
    change, message = STALE_INPUTS[stale]
    change(world)
    with pytest.raises(PatchError, match=message):
        tokens.build(world, CORE, census(), rewards=ALLOWED)


def _banc_with(change):
    tree = banc_tree()
    change(tree)
    return byml.write(tree)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda t: t["Actors"][0]["Dynamic"].update({tokens.DROP: "Obj_Token_Gold"}), "drop fields"),
        (lambda t: t["Actors"][0]["Dynamic"].update({"Drop__DropTable": "Other"}), "drop fields"),
        (lambda t: t["Actors"][0].update(Gyaml="Enemy_Skulltula"), "stale source"),
        (lambda t: t["Actors"].pop(0), "0 actors"),
        (lambda t: t["Actors"].append(dict(t["Actors"][0])), "2 actors"),
    ],
)
def test_placement_transform_refuses_a_stale_or_duplicated_source(world, change, message):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    with pytest.raises(PatchError, match=message):
        delivery.changes[CHILD](_banc_with(change))


def test_registry_transforms_refuse_inserted_rows_and_changed_donors(world):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    grown = actor_rows() + [{"ClassName": "GameActor", "__RowId": "Zzzz_Other_Patch"}]
    with pytest.raises(PatchError, match="not the dump's"):
        delivery.changes[tokens.ACTOR_INFO](byml.write(grown))
    changed = actor_rows()
    changed[3]["InstanceHeapSize"] = I32(1)
    with pytest.raises(PatchError, match="changed since"):
        delivery.changes[tokens.ACTOR_INFO](byml.write(changed))
    other_fields = actor_rows()
    other_fields[0]["ClassName"] = "Patched"  # unrelated rows may carry another step's field changes
    assert byml.read(delivery.changes[tokens.ACTOR_INFO](byml.write(other_fields)))[0]["ClassName"] == "Patched"


def test_common_writer_creates_the_packs_with_measured_entries(world, tmp_path):
    delivery = tokens.build(world, CORE, census(), rewards=ALLOWED)
    out = tmp_path / "out"
    written = write(Plan([], [], []), world, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)
    created = set(delivery.new_files)
    assert {info.path for info in written} == {ADULT, CHILD, *tokens.REGISTRIES, rstb.TABLE_PATH, *created}
    assert all(info.entry is None and info.size == 0 for info in written if info.path in created)
    table = rstb.read(raw(out / "romfs", rstb.TABLE_PATH, world))
    for path, file in delivery.new_files.items():
        assert raw(out / "romfs", path, world) == file.data
        assert table.get(path) == rstb.required_size(path, len(file.data))
        for name, content in sarc.read(file.data).items():
            if name in file.copied:
                assert table.get(name) == NATIVE_ENTRY
            elif name.endswith(rstb.ACTOR_PARAM):
                components = len(byml.read(content)["Components"])
                assert table.get(name) == rstb.required_size(name, len(content), components)
            else:
                assert table.get(name) == rstb.required_size(name, len(content))


TOKEN_ITEM = "Gold Skulltula Token"
GS_NAMES = {TREE: "Test GS Tree", TOWER: "Test GS Tower", LONE: "Test GS Lone"}
CHEST_NAME = "Test Token Chest"
DEFINITIONS = [
    # A source with an OoT Randomizer name links by it; the remake-only ones by their own names.
    Definition(TREE, "gold_skulltula", "Test", "Test Tree Skulltula", tokens.TOKEN, GS_NAMES[TREE]),
    Definition(TOWER, "gold_skulltula", "Test", GS_NAMES[TOWER], tokens.TOKEN, ""),
    Definition(LONE, "gold_skulltula", "Test", GS_NAMES[LONE], tokens.TOKEN, ""),
    Definition(CHEST, "chest", "Test", "Test Chest", "Obj_Rupee_Blue", CHEST_NAME),
]
SEED_REWARDS = {
    TOKEN_ITEM: ("Item_Token_Gold", "token"),
    "Boomerang": ("Item_Boomerang", "fixed_major"),
    "Hylian Shield": ("Obj_Shield_Hylian", "equipment"),
}


def token_spec():
    """Three Skulltulas and one chest, all reachable: the pool is three tokens (one per source) and a Boomerang."""
    checks = {name: {"type": "GS Token", "vanilla": TOKEN_ITEM} for name in GS_NAMES.values()}
    checks[CHEST_NAME] = {"type": "Chest", "vanilla": "Boomerang"}
    return {
        "start": "Root",
        "goal": "True",
        "items": {TOKEN_ITEM: {"type": "Token"}, "Boomerang": {}, "Hylian Shield": {}},
        "locations": checks,
        "regions": [{"name": "Root", "locations": {name: "True" for name in checks}}],
    }


def mixed_seed():
    """The first real fill that moves the Boomerang to a Skulltula and so a token into the chest."""
    from clawshot.generate import Settings, generate

    for number in range(32):
        seed = generate(token_spec(), number, Settings(shuffle=("Chest", "Token")))
        if seed.placements[CHEST_NAME] == TOKEN_ITEM:
            return seed
    raise AssertionError("no fill in 32 moved a token into the chest")


def test_a_real_token_fill_writes_a_moved_reward_and_a_chest_token_through_the_common_writer(world, tmp_path):
    from clawshot.patch import SeedOutput
    from clawshot.patch import items as item_actors
    from clawshot.patch.plan import Links, make_plan

    seed = mixed_seed()
    sources = [name for name in seed.shuffled if seed.world.locations[name].type == "Token"]
    assert sorted(sources) == sorted(GS_NAMES.values())
    assert sorted(seed.placements[name] for name in seed.shuffled) == ["Boomerang", *[TOKEN_ITEM] * 3]  # no bonus
    linked = tokens.link_sources(sources, DEFINITIONS, census())
    assert {name: location.id for name, location in linked.items()} == {name: h for h, name in GS_NAMES.items()}
    names = {definition.id: definition.name for definition in DEFINITIONS}
    delivery, rows = tokens.seed_delivery(world, seed.placements, linked, names, census(), rewards=SEED_REWARDS)
    moved = next(name for name in sources if seed.placements[name] == "Boomerang")
    assert delivery.drops == {linked[moved].id: BOOMERANG_PICKUP}
    assert list(delivery.new_files) == [tokens.pack_path(BOOMERANG_PICKUP)]

    box = ("Obj_TBox_A_01", "Obj_Rupee_Blue", None, True)  # Gyaml, drop, event, saved
    chest = Location(CHEST, "chest", "Test", None, (ADULT, CHILD), "both", (0.0, 0.0, 0.0), *box)
    links = Links({CHEST_NAME: [chest]}, names, [])
    plan = make_plan(seed, links, item_actors.load(), {})
    assert [(change.item, change.new_actor) for change in plan.changes] == [(TOKEN_ITEM, "Item_Token_Gold")]
    out = tmp_path / "seed"
    written = write(plan, world, out, extra_changes=(delivery.changes,), new_files=delivery.new_files)
    created = set(delivery.new_files)
    assert {info.path for info in written} == {ADULT, CHILD, *tokens.REGISTRIES, rstb.TABLE_PATH, *created}
    for path in (ADULT, CHILD):  # every copy: the chest names the token, only the moved source names its pickup
        actors = {int(placed["Hash"]): placed for placed in byml.read(raw(out / "romfs", path, world))["Actors"]}
        assert actors[CHEST]["Dynamic"][tokens.DROP] == "Item_Token_Gold"
        selected = {h: actors[h].get("Dynamic", {}).get(tokens.DROP) for h in GS_NAMES}
        assert selected == {h: BOOMERANG_PICKUP if h == linked[moved].id else None for h in GS_NAMES}

    expected = [
        {
            "location": name,
            "id": str(linked[name].id),
            "name": names[linked[name].id],
            "files": [ADULT, CHILD],
            "item": seed.placements[name],
            "pickup": SEED_REWARDS[seed.placements[name]][0],
            "drop_actor": BOOMERANG_PICKUP if name == moved else None,
        }
        for name in sorted(sources)
    ]
    log = SeedOutput(seed, links, plan, (delivery.changes,), (), {}, delivery.new_files, rows).spoiler()
    assert log["patch"]["tokens"] == expected
    assert [row["id"] for row in log["patch"]["changes"]] == [str(CHEST)]  # Skulltulas are never chest rows


def test_token_off_keeps_skulltulas_native_and_the_spoiler_without_token_rows():
    from clawshot.generate import Settings, generate
    from clawshot.patch import SeedOutput
    from clawshot.patch.plan import Links

    seed = generate(token_spec(), 1, Settings(shuffle=("Chest",)))
    assert seed.shuffled == [CHEST_NAME]
    assert all(seed.placements[name] == TOKEN_ITEM for name in GS_NAMES.values())
    assert "tokens" not in SeedOutput(seed, Links({}, {}, []), Plan([], [], [])).spoiler()["patch"]


@pytest.mark.parametrize(
    ("names", "definitions", "locations", "message"),
    [
        (["Test Tree Skulltula"], DEFINITIONS, None, "Test Tree Skulltula: 0 Gold Skulltula definitions"),
        (["Test GS Nowhere"], DEFINITIONS, None, "Test GS Nowhere: 0"),
        (list(GS_NAMES.values()), DEFINITIONS, (TREE, TOWER), "definitions with no census source: \\[3000\\]"),
        (list(GS_NAMES.values()), DEFINITIONS[1:], None, "census sources with no definition: \\[1000\\]"),
        (["Test GS Tower"], DEFINITIONS, "unsaved", "not a saved native Enemy_Skulltula_Gold"),
        (
            ["Test GS Tower"],
            [*DEFINITIONS, Definition(9, "gold_skulltula", "Test", "Twin", tokens.TOKEN, "Test GS Tower")],
            None,
            "Test GS Tower: 2 Gold Skulltula definitions",
        ),
    ],
)
def test_token_locations_link_only_to_agreeing_native_identities(names, definitions, locations, message):
    if locations == "unsaved":
        census_rows = [Location(**{**vars(location), "has_save_flag": location.id != TOWER}) for location in census()]
    else:
        census_rows = census(*(locations or ()))
    with pytest.raises(PatchError, match=message):
        tokens.link_sources(names, definitions, census_rows)


def test_seed_delivery_refuses_an_unadmitted_item_or_a_twice_declared_actor(world):
    linked = tokens.link_sources([GS_NAMES[TREE]], DEFINITIONS, census())
    with pytest.raises(PatchError, match="'Rupees \\(200\\)' is not an admitted Token reward"):
        tokens.seed_delivery(world, {GS_NAMES[TREE]: "Rupees (200)"}, linked, {}, census(), rewards=SEED_REWARDS)
    twice = {**SEED_REWARDS, "Shield Again": ("Obj_Shield_Hylian", "fixed_major")}
    with pytest.raises(PatchError, match="Obj_Shield_Hylian is declared in two grant families"):
        tokens.seed_delivery(world, {GS_NAMES[TREE]: "Boomerang"}, linked, {}, census(), rewards=twice)
