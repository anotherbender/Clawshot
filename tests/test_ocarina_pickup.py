"""The ocarinas' world actors ``Obj_Clawshot_Ocarina_Fairy`` / ``Obj_Clawshot_Ocarina_Time``
(``patch/ocarina_pickup.py``, O7, plan task 16) on synthetic packs and tables built in code (hard rule 1): built on
``Obj_Arrow_Fire``'s pickup body like the song floor actors, never on ``Obj_Ocarina_Time``'s ``Box`` body (F1-a,
F1-c), and written only into seeds that place an ocarina where it needs one."""

import pytest
from synthetic_effects import HEART_USERS, build_table
from test_songs import arrow_pack, static_doc

from clawshot.formats import byml, elink, sarc, vfx
from clawshot.patch import drops, freestanding, getitem, ocarina_pickup, songs
from clawshot.patch.items import ItemActors
from clawshot.patch.plan import PatchError
from clawshot.world.load import build_world

FAIRY, TIME = getitem.FAIRY, getitem.TIME
ARROW_PARAM = "Actor/Obj_Arrow_Fire.engine__actor__ActorParam.bgyml"
ARROW_ANIMATION = "Component/AnimationParam/Obj_Arrow_Fire.engine__component__AnimationParam.bgyml"
ARROW_ELINK = "Component/ELink/Obj_Arrow_Fire.engine__component__ELinkParam.bgyml"
ARROW_POUCH = "Component/PouchContentParam/ArrowFire.game__component__PouchContentParam.bgyml"
PHYSICS = "Component/Physics/Obj_Arrow_Fire.engine__component__PhysicsParam.bgyml"
BOX = "Phive/ShapeParam/Box.phive__ShapeParam.bgyml"


def doc(tree) -> bytes:
    return byml.write(tree)


def model(ocarina: str) -> str:
    return f"Component/ModelInfo/{ocarina}.engine__component__ModelInfo.bgyml"


def pouch(ocarina: str) -> str:
    return f"Component/PouchContentParam/{ocarina}.game__component__PouchContentParam.bgyml"


def arrow_members() -> dict[str, bytes]:
    members = arrow_pack()
    param = byml.read(members[ARROW_PARAM])
    param["Components"]["PhysicsRef"] = "?" + PHYSICS
    members[ARROW_PARAM] = doc(param)
    members[PHYSICS] = doc({"RigidBody": "Item_Pouch"})
    return members


def ocarina_members(ocarina: str) -> dict[str, bytes]:
    return {
        f"Actor/{ocarina}.engine__actor__ActorParam.bgyml": doc(
            {"Components": {"ModelInfoRef": "?" + model(ocarina), "PouchContentRef": "?" + pouch(ocarina)}}
        ),
        model(ocarina): doc({"FmdbName": ocarina, "ModelProjectName": ocarina, "Scale": 1}),
        pouch(ocarina): doc({"SpecialDeal": 7, **({"GetType": byml.U32(0x681AE117)} if ocarina == TIME else {})}),
        "Component/Other/Equipment.bgyml": doc({"Equip": True}),
        BOX: doc({"Box": "the moat body"}),
    }


def built(ocarina: str) -> tuple[dict[str, bytes], dict[str, str]]:
    file = ocarina_pickup.pickup_pack(
        ocarina, arrow=sarc.write(arrow_members()), ocarina_pack=sarc.write(ocarina_members(ocarina))
    )
    return sarc.read(file.data), dict(file.copied)


def names(ocarina: str) -> tuple[str, str, str, str]:
    pickup = ocarina_pickup.PICKUPS[ocarina]
    return (
        f"Actor/{pickup}.engine__actor__ActorParam.bgyml",
        getitem.animation_member(pickup),
        pouch(pickup),
        songs.elink_member(pickup),
    )


def test_each_ocarina_has_its_own_generated_floor_actor():
    assert ocarina_pickup.PICKUPS == {FAIRY: "Obj_Clawshot_Ocarina_Fairy", TIME: "Obj_Clawshot_Ocarina_Time"}
    assert ocarina_pickup.PICKUP == "Obj_Clawshot_Ocarina_Fairy"
    assert "Obj_Ocarina_Time" not in ocarina_pickup.PICKUPS.values()


@pytest.mark.parametrize("ocarina", [FAIRY, TIME])
def test_pickup_is_the_arrow_pointing_at_the_ocarina(ocarina):
    members, _ = built(ocarina)
    param_name, animation, own_pouch, link = names(ocarina)
    param = byml.read(members[param_name])
    native = byml.read(arrow_members()[ARROW_PARAM])
    assert param["$parent"] == native["$parent"]
    expected = {k: v for k, v in native["Components"].items() if k not in ocarina_pickup.DROPPED}
    expected |= {
        "ActorNameRef": f"?ActorSystem/ActorName/{ocarina}.engine__actor__ActorName.bgyml",
        "ModelInfoRef": "?" + model(ocarina),
        "AnimationRef": "?" + animation,
        "PouchContentRef": "?" + own_pouch,
        "ELinkRef": "?" + link,
    }
    assert param["Components"] == expected
    assert byml.read(members[link]) == {"UserName": ocarina_pickup.USERS[ocarina]}
    assert byml.read(members[own_pouch]) == {
        "$parent": "Work/" + pouch(ocarina).replace(".bgyml", ".gyml"),
        "GetDemoOffsetPos": byml.read(arrow_members()[ARROW_POUCH])["GetDemoOffsetPos"],
        "PouchActor": f"Work/Actor/{ocarina}.engine__actor__ActorParam.gyml",
    }


@pytest.mark.parametrize("ocarina", [FAIRY, TIME])
def test_world_ocarina_inherits_its_native_get_without_changing_pouch_or_grant(ocarina):
    from clawshot.patch.actor_packs import resolve_node

    members, _ = built(ocarina)
    native = ocarina_members(ocarina)
    own_pouch = names(ocarina)[2]
    resolved = resolve_node([members], own_pouch)
    assert byml.same(resolved.get("GetType"), byml.read(native[pouch(ocarina)]).get("GetType"))
    assert resolved["PouchActor"] == f"Work/Actor/{ocarina}.engine__actor__ActorParam.gyml"
    assert resolved["SpecialDeal"] == 7
    assert members[pouch(ocarina)] == native[pouch(ocarina)]


@pytest.mark.parametrize("ocarina", [FAIRY, TIME])
def test_pickup_keeps_the_arrow_body_and_never_the_moat_box(ocarina):
    """F1-a/F1-c: the body is the arrow's pickup body, copied unchanged; no Box member comes along."""
    members, copied = built(ocarina)
    param = byml.read(members[names(ocarina)[0]])
    assert param["Components"]["PhysicsRef"] == "?" + PHYSICS
    assert members[PHYSICS] == arrow_members()[PHYSICS]
    assert copied[PHYSICS] == "Pack/Actor/Obj_Arrow_Fire.pack.zs"
    assert not [name for name in members if "Box" in name or "Phive" in name and "Ptm_ObjDynamicLarge" in name]


@pytest.mark.parametrize("ocarina", [FAIRY, TIME])
def test_pickup_has_its_glow_instead_of_the_fire_arrow_effects(ocarina):
    members, _ = built(ocarina)
    components = byml.read(members[names(ocarina)[0]])["Components"]
    for key in ("SLinkRef", "GameParameterTableRef", "CaptureRef"):
        assert key not in components
    assert components["ELinkRef"] == "?" + names(ocarina)[3]
    assert ARROW_PARAM not in members
    assert members[ARROW_ELINK] == arrow_members()[ARROW_ELINK]  # the arrow's own member stays, unused


@pytest.mark.parametrize("ocarina", [FAIRY, TIME])
def test_pickup_animation_lays_the_ocarina_flat_and_spinning(ocarina):
    members, _ = built(ocarina)
    assert members[names(ocarina)[1]] == getitem.animation_param(ocarina)


@pytest.mark.parametrize("ocarina", [FAIRY, TIME])
def test_pickup_copies_only_the_model_and_pouch_from_the_ocarina(ocarina):
    members, copied = built(ocarina)
    own = ocarina_members(ocarina)
    for member in (model(ocarina), pouch(ocarina)):
        assert members[member] == own[member]
        assert copied[member] == f"Pack/Actor/{ocarina}.pack.zs"
    assert "Component/Other/Equipment.bgyml" not in members
    for member, data in arrow_members().items():
        if member != ARROW_PARAM:
            assert members[member] == data
            assert copied[member] == "Pack/Actor/Obj_Arrow_Fire.pack.zs"
    assert set(members) - set(copied) == set(names(ocarina))


def test_an_unknown_ocarina_or_a_broken_arrow_is_refused():
    with pytest.raises(PatchError, match="not an ocarina"):
        ocarina_pickup.pickup_pack("Item_Bow", arrow=sarc.write(arrow_members()), ocarina_pack=sarc.write({}))
    members = arrow_members()
    del members[ARROW_PARAM]
    with pytest.raises(PatchError, match="Obj_Arrow_Fire"):
        ocarina_pickup.pickup_pack(FAIRY, arrow=sarc.write(members), ocarina_pack=sarc.write(ocarina_members(FAIRY)))


def row(name: str, **fields) -> dict:
    return {"__RowId": name, **fields}


def actor_info() -> list[dict]:
    rows = [
        row(
            ocarina,
            ActorName=ocarina,
            CalcPriority="After",
            FmdbName=ocarina,
            ModelProjectName=ocarina,
            ModelAabbMin=[byml.F32(-2.0)],
            ModelAabbMax=[byml.F32(2.0)],
            InstanceHeapSize=byml.I32(50),
        )
        for ocarina in (FAIRY, TIME)
    ]
    rows.append(
        row(
            "Obj_Arrow_Fire",
            ActorName="Item_Arrow_Fire",
            FmdbName="Item_Arrow_Fire",
            ModelProjectName="Item_Arrow_Fire",
            ModelAabbMin=[byml.F32(-1.0)],
            ModelAabbMax=[byml.F32(1.0)],
            InstanceHeapSize=byml.I32(130),
            ELinkUserName="Obj_Arrow_Fire",
            SLinkUserName="Obj_Arrow_Fire",
            AnimationResources=[{"ModelProjectName": "Item_Arrow_Fire_Animation"}],
        )
    )
    return sorted(rows, key=lambda r: r["__RowId"].encode())


def test_actor_info_rows_are_the_arrow_with_the_ocarina_model():
    out = {r["__RowId"]: r for r in byml.read(ocarina_pickup.patch_actor_info(byml.write(actor_info())))}
    assert list(out) == sorted(out, key=str.encode)
    before = {r["__RowId"]: r for r in actor_info()}
    for ocarina, pickup in ocarina_pickup.PICKUPS.items():
        new = out[pickup]
        assert new["ActorName"] == ocarina
        for field in getitem.MODEL_FIELDS:
            assert byml.same(new[field], before[ocarina][field])
        assert new["AnimationResources"] == byml.read(getitem.animation_param(ocarina))["AnimationResources"]
        assert new["InstanceHeapSize"] == before["Obj_Arrow_Fire"]["InstanceHeapSize"]
        assert new["ELinkUserName"] == ocarina_pickup.USERS[ocarina]
        assert not {"CalcPriority", "SLinkUserName"} & set(new)
    for name, original in before.items():
        assert byml.same(out[name], original)


def test_game_actor_info_rows_are_the_arrow_renamed():
    rows = [row("Obj_Arrow_Fire", IsRespawn=True, MainRigidBodyLayer="Object"), row("Zzz")]
    out = {r["__RowId"]: r for r in byml.read(ocarina_pickup.patch_game_actor_info(byml.write(rows)))}
    for pickup in ocarina_pickup.PICKUPS.values():
        assert out[pickup] == {"__RowId": pickup, "IsRespawn": True, "MainRigidBodyLayer": "Object"}


def test_pouch_actor_info_keeps_native_classification_and_rows_byte_identical():
    rows = [
        row(FAIRY, PouchGetType="Small", PouchSpecialDeal="Ocarina", OcarinaTypeValue=byml.I32(1)),
        row(TIME, PouchGetType="Large", PouchSpecialDeal="Ocarina", OcarinaTypeValue=byml.I32(2)),
    ]
    out = {r["__RowId"]: r for r in byml.read(ocarina_pickup.patch_pouch_actor_info(byml.write(rows)))}
    fairy, time = ocarina_pickup.PICKUPS[FAIRY], ocarina_pickup.PICKUPS[TIME]
    assert out[fairy] == {"__RowId": fairy, "PouchGetType": "Small", "PouchSpecialDeal": "Ocarina"}
    assert out[time] == {"__RowId": time, "PouchGetType": "Large", "PouchSpecialDeal": "Ocarina"}
    for native in rows:
        assert byml.write(out[native["__RowId"]]) == byml.write(native)


def test_the_rows_can_be_limited_to_one_ocarina():
    out = {r["__RowId"] for r in byml.read(ocarina_pickup.patch_actor_info(byml.write(actor_info()), [TIME]))}
    assert ocarina_pickup.PICKUPS[TIME] in out and ocarina_pickup.PICKUP not in out


@pytest.mark.parametrize(
    "patch",
    [ocarina_pickup.patch_actor_info, ocarina_pickup.patch_game_actor_info, ocarina_pickup.patch_pouch_actor_info],
)
def test_a_table_already_holding_the_pickup_is_refused(patch):
    rows = [*actor_info(), row(ocarina_pickup.PICKUP)]
    rows = sorted({r["__RowId"]: r for r in rows}.values(), key=lambda r: r["__RowId"].encode())
    with pytest.raises(PatchError, match=ocarina_pickup.PICKUP):
        patch(byml.write(rows))


ACTORS = ItemActors(actors={"Fairy Ocarina": FAIRY, "Ocarina of Time": TIME, "Bow": "Item_Bow"}, sources={})


def kinds_world():
    places = {
        "Chest": {"type": "Chest", "vanilla": "Bow", "rule": "True"},
        "Skulltula": {"type": "Token", "vanilla": "Bow", "rule": "True"},
        "Boss Heart": {"type": "BossHeart", "vanilla": "Bow", "rule": "True"},
        "Floor": {"type": "Freestanding", "vanilla": "Bow", "rule": "True"},
        "Gift": {"type": "NPC", "vanilla": "Bow", "rule": "True"},
    }
    return build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {"Fairy Ocarina": {}, "Ocarina of Time": {}, "Bow": {}},
            "regions": [{"name": "Root", "locations": places}],
        }
    )


def test_the_world_pickup_kinds_are_the_shuffle_kinds():
    from clawshot.generate import tokens

    assert set(ocarina_pickup.KINDS[FAIRY]) == {tokens.SHUFFLE, drops.SHUFFLE, freestanding.SHUFFLE}
    assert set(ocarina_pickup.KINDS[TIME]) == {tokens.SHUFFLE, drops.SHUFFLE, freestanding.SHUFFLE}


@pytest.mark.parametrize(
    "place, item, wanted",
    [
        ("Skulltula", "Fairy Ocarina", [FAIRY]),
        ("Boss Heart", "Fairy Ocarina", [FAIRY]),
        ("Floor", "Fairy Ocarina", [FAIRY]),
        ("Boss Heart", "Ocarina of Time", [TIME]),
        ("Floor", "Ocarina of Time", [TIME]),
        ("Skulltula", "Ocarina of Time", [TIME]),  # its own donor since run TB3 (finding TB3-a)
        ("Chest", "Fairy Ocarina", []),
        ("Gift", "Ocarina of Time", []),
    ],
)
def test_a_seed_needs_the_actor_of_an_ocarina_where_one_is_needed(place, item, wanted):
    placements = {name: "Bow" for name in kinds_world().locations}
    placements[place] = item
    assert ocarina_pickup.needed(placements, kinds_world(), ACTORS) == wanted


def test_both_ocarinas_are_listed_in_a_fixed_order():
    placements = {name: "Bow" for name in kinds_world().locations}
    placements |= {"Floor": "Ocarina of Time", "Skulltula": "Fairy Ocarina"}
    assert ocarina_pickup.needed(placements, kinds_world(), ACTORS) == [FAIRY, TIME]


def test_build_writes_only_the_needed_packs_and_rows(tmp_path, zsdic_pack):
    from test_songs import write_romfs

    tables = {
        ocarina_pickup.ACTOR_INFO: byml.write(actor_info()),
        ocarina_pickup.GAME_ACTOR_INFO: byml.write([row("Obj_Arrow_Fire", IsRespawn=True)]),
        ocarina_pickup.POUCH_ACTOR_INFO: byml.write(
            [row(FAIRY, OcarinaTypeValue=byml.I32(1)), row(TIME, OcarinaTypeValue=byml.I32(2))]
        ),
    }
    files = {
        **tables,
        songs.ELINK: build_table(HEART_USERS),
        songs.STATIC: static_doc(),
        "Pack/Actor/Obj_Arrow_Fire.pack.zs": sarc.write(arrow_members()),
        f"Pack/Actor/{FAIRY}.pack.zs": sarc.write(ocarina_members(FAIRY)),
        f"Pack/Actor/{TIME}.pack.zs": sarc.write(ocarina_members(TIME)),
    }
    write_romfs(tmp_path, zsdic_pack, files)
    time_pack = f"Pack/Actor/{ocarina_pickup.PICKUPS[TIME]}.pack.zs"
    delivery = ocarina_pickup.build(tmp_path, [TIME])
    assert list(delivery.new_files) == [time_pack]
    assert sarc.read(delivery.new_files[time_pack].data) == built(TIME)[0]
    assert set(delivery.changes) == {*tables, songs.ELINK, songs.STATIC}
    for path in tables:
        ids = {r["__RowId"] for r in byml.read(delivery.changes[path](tables[path]))}
        assert ocarina_pickup.PICKUPS[TIME] in ids and ocarina_pickup.PICKUP not in ids
    users = elink.decode(delivery.changes[songs.ELINK](files[songs.ELINK])).user_names()
    assert ocarina_pickup.USERS[TIME] in users and ocarina_pickup.USERS[FAIRY] not in users
    grown = byml.read(delivery.changes[songs.STATIC](files[songs.STATIC]))["PtclBin"].data
    assert songs.LIGHT in vfx.effect_names(grown)
    # A seed whose song step already grows static leaves it to that step.
    assert songs.STATIC not in ocarina_pickup.build(tmp_path, [TIME], with_static=False).changes
    both = ocarina_pickup.build(tmp_path, [TIME, FAIRY])
    assert list(both.new_files) == [f"Pack/Actor/{ocarina_pickup.PICKUP}.pack.zs", time_pack]
    with pytest.raises(PatchError, match="no ocarina"):
        ocarina_pickup.build(tmp_path, [])
    # A dump already holding a pack is refused.
    write_romfs(tmp_path, zsdic_pack, {time_pack: sarc.write({})})
    with pytest.raises(PatchError, match="already has"):
        ocarina_pickup.build(tmp_path, [TIME])


def test_the_app_working_set_holds_the_pickup_inputs():
    from types import SimpleNamespace

    from clawshot.pack.source import resource_spec, working_files

    wanted = working_files(SimpleNamespace(files=[]), resource_spec())
    assert set(ocarina_pickup.native_inputs()) <= wanted, sorted(set(ocarina_pickup.native_inputs()) - wanted)


def test_glow_users_play_only_the_songs_light_in_warm_white():
    native = build_table(HEART_USERS)
    effects = songs.load_effects()
    before = elink.decode(native)
    table = elink.decode(ocarina_pickup.patch_elink(native, effects=effects))
    assert sorted(table.user_names()) == sorted([*before.user_names(), *ocarina_pickup.USERS.values()])
    for user in ocarina_pickup.USERS.values():
        calls = table.calls(user)
        for key, condition in (("Wait", effects.floor_condition), ("GetDemo", effects.get_pose_condition)):
            kind, first, last = table.container(user, key)
            assert kind == 3 and first == last  # one child: the light, no sparks or aura
            child = table.call_params(user, first)
            assert child["RuntimeAssetName"] == songs.LIGHT and child["Bone"] == "Root"
            colour = ocarina_pickup.GLOW_COLOUR if key == "Wait" else (0.0, 0.0, 0.0)  # TG1: none when held up
            assert (child["Red"], child["Green"], child["Blue"]) == pytest.approx(colour)
            assert child["Scale"] == pytest.approx(ocarina_pickup.GLOW["Scale"])
            assert calls[first].condition == condition


def test_the_glow_is_warm_white_on_the_floor_and_sized_as_preludes_floor_light():
    red, green, blue = ocarina_pickup.GLOW_COLOUR
    assert red >= green >= blue > 0  # warm white: no channel missing, red leading
    prelude = songs.load_effects().songs["Item_Melody_LightPrelude"]
    assert ocarina_pickup.GLOW["Scale"] == prelude.floor.scale
    assert ocarina_pickup.GLOW["PositionY"] == -drops.FLOOR_LIFT  # at the floor, not close under the model (TG1)
    assert ocarina_pickup.GLOW["RotationX"] == prelude.rotation_x
    assert ocarina_pickup.GLOW["LifeScale"] == prelude.life_scale


def test_a_table_already_holding_a_glow_user_is_refused():
    effects = songs.load_effects()
    once = ocarina_pickup.patch_elink(build_table(HEART_USERS), [FAIRY], effects=effects)
    with pytest.raises(PatchError, match="already has the user"):
        ocarina_pickup.patch_elink(once, [FAIRY], effects=effects)


@pytest.mark.parametrize(
    "shuffle, expected",
    [
        (("Chest", "Gift", "Token"), True),
        (("Gift", "BossHeart"), True),
        (("NPC", "Freestanding"), True),  # a Gift kind counts as Gift (getitem.gift_kinds)
        (("Chest", "Token", "BossHeart", "Freestanding"), False),  # no Gift kind: the ocarinas cannot move
        (("Chest", "Gift", "Scrub"), False),  # no world-pickup kind
    ],
)
def test_the_pickups_run_by_setting_as_the_get_display_steps(shuffle, expected):
    """PR #41's rule (the maintainers' option 2): a step runs when the settings could produce what it shows."""
    assert ocarina_pickup.pickups_possible(shuffle) is expected


def test_the_pickup_step_is_named_in_the_spoiler_steps():
    from clawshot.patch import OCARINA_PICKUPS, OPTIONAL_STEPS

    assert OCARINA_PICKUPS == "ocarina_pickups" and OCARINA_PICKUPS in OPTIONAL_STEPS
