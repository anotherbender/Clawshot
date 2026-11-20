"""Equipment/ownership effects, with native pin0=true and both GameData visibility models."""

from copy import deepcopy

import pytest
from test_child_sword import BEFORE_FORCE, CANDIDATE, EQUIPPED, KOKIRI, MASTER, equipment_fixture, initial, run

from clawshot.formats import byml, evfl, zsdic
from clawshot.patch import equipment, master_sword


def synthetic_era():
    doc = equipment_fixture()
    fc = doc.flowchart
    fc.events[6].next = 7
    fc.events.extend(
        [
            evfl.SwitchEvent("Event6", 0, 2, [(0, 8), (1, 9)], {"GameDataName": "Sequence_IsChildhood", "Index": -1}),
            evfl.ActionEvent(
                "Event1",
                0,
                0,
                10,
                {"SrcGameDataName": EQUIPPED, "DstGameDataName": CANDIDATE, "Index": -1, "SrcIndex": -1},
            ),
            evfl.ActionEvent(
                "Event7",
                0,
                0,
                10,
                {"SrcGameDataName": BEFORE_FORCE, "DstGameDataName": CANDIDATE, "Index": -1, "SrcIndex": -1},
            ),
            evfl.ActionEvent(
                "Event2",
                0,
                0,
                evfl.NONE,
                {
                    "SrcGameDataName": "PlayerStatus.AnotherEraEquipShield",
                    "DstGameDataName": "PlayerStatus.EquipShield",
                    "Index": -1,
                    "SrcIndex": -1,
                },
            ),
        ]
    )
    return evfl.write(doc)


@pytest.mark.parametrize("visibility", ["immediate", "buffered"])
@pytest.mark.parametrize("child", [False, True])
@pytest.mark.parametrize("owned", [False, True])
@pytest.mark.parametrize("blade", master_sword.ADULT_BLADES)
@pytest.mark.parametrize("candidate", ["", "saved"])
def test_era_never_creates_ownership_or_equips_an_unowned_adult_blade(visibility, child, owned, blade, candidate):
    chart = evfl.read(master_sword.era_transform(equipment.transform(synthetic_era()))).flowchart
    state = initial(candidate=blade if candidate else "", owned=False, child=child)
    state[BEFORE_FORCE] = blade
    state[f"IsGet.{blade}"] = owned
    state[f"PouchData.{blade}.StockNum"] = int(owned)
    pouch = {blade: int(owned)}
    run(chart, state, pouch, child=child, visibility=visibility)
    assert state[f"IsGet.{blade}"] is owned
    assert pouch == {blade: int(owned)}
    if child:
        expected = blade if candidate and owned else MASTER if not candidate and blade == MASTER and owned else ""
        assert state[EQUIPPED] == expected, state
    else:
        assert state[CANDIDATE] == (blade if owned else ""), state


def native(romfs, flow):
    path = f"Event/EventFlow/{flow}.bfevfl.zs"
    return zsdic.Dictionaries.from_romfs(romfs).decompress(path, (romfs / path).read_bytes())


def execute(fc, entry, state, *, owned, dream=False, charts=None, stop=None):
    """Execute native setup effects; resolve the actual shared ownership helper too."""

    def query_pin(chart, event):
        params = event.params or {}
        actor = chart.actors[event.actor]
        op = actor.queries[event.query]
        if op == "EventQueryIsGameDataBool":
            answer = state.get(params["GameDataName"], owned if params["GameDataName"] == f"IsGet.{MASTER}" else False)
        elif op == "EventQueryIsGameDataInt":
            value = state.get(params["GameDataName"], int(owned))
            return 0 if value == params["Value"] else 1 if value < params["Value"] else 2
        elif op == "EventQueryPlayerIsEquipWeapon":
            answer = state.get(EQUIPPED, "") == params["ArmorName"]
        elif op == "EventQueryIsEventSkipedMostRecent":
            answer = False  # This run exercises the native non-skipped dream entry.
        elif op == "EventQueryIsDreamWorld":
            answer = dream
        else:
            raise AssertionError((event, op, state))
        return 0 if answer else 1

    active = [fc.entry_point(entry).main_event]
    effects = []
    for _ in range(300):
        if not active:
            return effects
        at = active.pop()
        if at == stop:
            return effects
        if at == evfl.NONE:
            continue
        e = fc.events[at]
        p = getattr(e, "params", None) or {}
        if isinstance(e, evfl.ForkEvent):
            active.extend([fc.events[e.join].next, *reversed(e.forks)])
            continue
        if isinstance(e, evfl.JoinEvent):
            active.append(e.next)
            continue
        if isinstance(e, evfl.SubFlowSwitchEvent):
            shared = charts[e.flowchart]
            target = shared.entry_point(e.entry_point).main_event
            for _ in range(10):
                event = shared.events[target]
                if isinstance(event, evfl.ReturnEvent):
                    active.append(dict(e.cases)[event.value])
                    break
                assert isinstance(event, evfl.SwitchEvent), event
                target = dict(event.cases)[query_pin(shared, event)]
            else:
                raise AssertionError(("shared ownership query did not return", e))
            continue
        if isinstance(e, evfl.SubFlowEvent):
            if e.flowchart in ("", fc.name):
                active.extend([e.next, fc.entry_point(e.entry_point).main_event])
            else:
                active.append(e.next)
            continue
        if isinstance(e, evfl.ReturnEvent):
            continue
        if isinstance(e, evfl.SwitchEvent):
            active.append(dict(e.cases).get(query_pin(fc, e), evfl.NONE))
            continue
        op = fc.actors[e.actor].actions[e.action]
        effects.append((op, deepcopy(p)))
        if op == "EventTriggerCopyGameDataString64":
            state[p["DstGameDataName"]] = state.get(p["SrcGameDataName"], "")
        elif op in (
            "EventTriggerEquipmentUserRequestCreateStaticEquipment",
            "EventTriggerPlayerRequestCreateDynamicEquipmentNoRelationPouch",
        ):
            state[EQUIPPED] = p["EquipmentActorName"]
        elif op in ("EventEnterGameSafetySection", "EventReserveBancChange"):
            return effects
        active.append(e.next)
    raise AssertionError(("flow did not finish", entry, state, effects))


@pytest.mark.dump
@pytest.mark.parametrize(
    "flow,entry,patch",
    [
        ("Dm_TimeTemple_0070", "other", master_sword.pose_transform("Dm_TimeTemple_0070", "Event3", "Event13")),
        ("Dm_TimeTemple_0088", "other", master_sword.pose_transform("Dm_TimeTemple_0088", "Event35", "Event29")),
        ("Dm_TimeTemple_0085", "other", master_sword.arrival_transform),
    ],
)
@pytest.mark.parametrize("owned", [False, True])
@pytest.mark.parametrize("selected", ["", "Weapon_Sword_Biggoron"])
def test_actual_pose_never_creates_unowned_equipment(romfs, flow, entry, patch, owned, selected):
    before = native(romfs, flow)
    after = patch(before)
    state = {EQUIPPED: selected}
    shared = evfl.read(
        master_sword.era_transform(equipment.transform(native(romfs, "ReplaceEquipmentForEraChange")))
    ).flowchart
    effects = execute(evfl.read(after).flowchart, entry, state, owned=owned, charts={shared.name: shared})
    expected = MASTER if owned and flow == "Dm_TimeTemple_0085" and not selected else selected
    assert state[EQUIPPED] == expected, (flow, state, effects)
    if not owned and not selected:
        control = {EQUIPPED: selected}
        execute(evfl.read(before).flowchart, entry, control, owned=False)
        assert control[EQUIPPED] == MASTER
    assert not any(op == "EventTriggerAddOrRemovePouchContent" for op, _ in effects)


@pytest.mark.dump
@pytest.mark.parametrize("owned", [False, True])
def test_actual_age_round_trip_neither_loses_nor_creates_master(romfs, owned):
    visibility = "buffered"  # Native swaps read outgoing values until their frame boundary.
    fc = evfl.read(
        master_sword.era_transform(equipment.transform(native(romfs, "ReplaceEquipmentForEraChange")))
    ).flowchart
    state = initial(candidate="", child=True)
    state[f"IsGet.{MASTER}"] = owned
    state[f"PouchData.{MASTER}.StockNum"] = int(owned)
    pouch = {MASTER: int(owned), KOKIRI: 0}
    for _ in range(3):
        run(fc, state, pouch, child=True, visibility=visibility)
        assert state[EQUIPPED] == (MASTER if owned else ""), state
        # Native adult departure records the true weapon before its cinematic prop.
        state[BEFORE_FORCE] = state[EQUIPPED]
        state["Sequence_IsChildhood"] = False
        run(fc, state, pouch, child=False, visibility=visibility)
        assert state[EQUIPPED] == "", state
        assert state[CANDIDATE] == (MASTER if owned else ""), state
        assert state[f"IsGet.{MASTER}"] is owned
        assert pouch == {MASTER: int(owned), KOKIRI: 0}
        state["Sequence_IsChildhood"] = True


@pytest.mark.dump
@pytest.mark.parametrize("owned,dream", [(False, False), (True, False), (False, True), (True, True)])
def test_finale_refuses_before_safety_save_without_sword_but_preserves_dream(romfs, owned, dream):
    data = native(romfs, "Defeat_Ganon")
    fc = evfl.read(master_sword.finale_transform(data)).flowchart
    effects = execute(fc, "InsideGanonCastle_Dungeon_BossAppear_1", {}, owned=owned, dream=dream)
    if not dream and not owned:
        assert len(effects) == 1, effects
        op, params = effects[0]
        assert op == "EventReserveBancChange"
        assert params["NextBanc"] == "GanonCastle"
        assert params["NextStartPos"] == "GanonCastleEntrance"
        assert params["BootEventName"] == ""
    else:
        assert effects == execute(
            evfl.read(data).flowchart, "InsideGanonCastle_Dungeon_BossAppear_1", {}, owned=owned, dream=dream
        )


@pytest.mark.dump
@pytest.mark.parametrize("visibility", ["immediate", "buffered"])
@pytest.mark.parametrize("owned", [False, True])
def test_first_pull_credits_reward_and_reaches_adult_rauru_without_waiting_for_ui(romfs, visibility, owned):
    door = evfl.read(master_sword.pedestal_transform("Item_Boomerang")(native(romfs, "DoorOfTime"))).flowchart
    era = evfl.read(master_sword.era_transform(equipment.transform(native(romfs, "ReplaceEquipmentForEraChange"))))
    get = evfl.read(native(romfs, "GetPouchContent")).flowchart
    charts = {door.name: door, get.name: get}
    state = initial("", owned=True, child=True)
    state.update({f"IsGet.{MASTER}": owned, f"PouchData.{MASTER}.StockNum": int(owned)})
    pouch = {KOKIRI: 1, MASTER: int(owned)}

    def drive(entry):
        pending = [(door, door.entry_point(entry).main_event)]
        for _ in range(100):
            if not pending:
                return None
            fc, at = pending.pop()
            if at == evfl.NONE:
                continue
            event = fc.events[at]
            params = getattr(event, "params", None) or {}
            if isinstance(event, evfl.SubFlowEvent):
                pending.append((fc, event.next))
                if event.flowchart == era.flowchart.name:
                    run(era.flowchart, state, pouch, child=True, visibility=visibility)
                else:
                    child = charts[event.flowchart or fc.name]
                    pending.append((child, child.entry_point(event.entry_point).main_event))
                continue
            actor = fc.actors[event.actor]
            if isinstance(event, evfl.SwitchEvent):
                assert actor.queries[event.query] == "EventQueryHavePlayedEvent", event
                pin = 0 if state.get("HavePlayedEvent." + params["EventName"], False) else 1
                pending.append((fc, dict(event.cases)[pin]))
                continue
            op = actor.actions[event.action]
            if op == "EventTransition":
                state["HavePlayedEvent." + params["EventName"]] = True
            elif op == "EventTriggerAddOrRemovePouchContent":
                item = params["Actor"]
                pouch[item] = pouch.get(item, 0) + params["Num"]
                state[f"IsGet.{item}"] = True
                state[f"PouchData.{item}.StockNum"] = pouch[item]
                if params["IsEquipDIrect"]:
                    state[EQUIPPED] = item
            elif op == "EventTriggerSetGameDataBool":
                state[params["GameDataName"]] = params["Value"]
            elif op == "EventReserveBancChange":
                return params
            else:
                # The pull movie deliberately leaves a white fade for the next boot event.
                # Resolve native GetPouchContent calls too: its get-window setup must not
                # hold this handoff on dialog input before the grant, age write and reserve.
                assert op in ("EventWait", "EventTriggerBancRequestBeforehandLoad"), (fc.name, op, params, state)
            pending.append((fc, event.next))
        raise AssertionError(("first-pull handoff did not finish", state, pouch))

    destination = drive("SageRoom_MeetGanondorf")
    assert (destination["NextBanc"], destination["BootEventName"]) == ("SageRoom", "SageRoom_MeetRauru")
    assert state["Sequence_IsChildhood"] is False
    assert state["IsGet.Item_Boomerang"] is True
    assert state["PouchData.Item_Boomerang.StockNum"] == 1
    assert state[f"IsGet.{MASTER}"] is owned
    assert pouch[MASTER] == int(owned)
    assert state[EQUIPPED] == (MASTER if owned else "")
    # A real repeat draw takes the existing era-travel scene, not the first-pull reward.
    drive("DoorOfTime_Draw")
    assert pouch["Item_Boomerang"] == 1


@pytest.mark.dump
def test_finale_refusal_anchor_is_real_and_outside_bridge(romfs):
    path = "Banc/GanonCastle/GanonCastle_Dynamic.bcett.byml.zs"
    data = zsdic.Dictionaries.from_romfs(romfs).decompress(path, (romfs / path).read_bytes())
    tree = byml.load(data).root
    anchors = [a for a in tree["Actors"] if a.get("Name") == "GanonCastleEntrance" and a["Gyaml"] == "StartPos"]
    assert [(int(a["Hash"]), float(a["Translate"][2])) for a in anchors] == [(16478939697790907191, 367.3228454589844)]


@pytest.mark.parametrize("blade", master_sword.ADULT_BLADES)
def test_historical_sword_flag_without_stock_is_not_an_owned_blade(blade):
    fc = evfl.read(master_sword.era_transform(equipment.transform(synthetic_era()))).flowchart
    state = initial(candidate=blade, child=True)
    state[f"IsGet.{blade}"] = True
    state[f"PouchData.{blade}.StockNum"] = 0
    run(fc, state, {blade: 0}, child=True)
    assert state[EQUIPPED] == "", state
    assert state[f"IsGet.{blade}"] is True


@pytest.mark.dump
@pytest.mark.parametrize("flow,node", [("AllSage", "Event175"), ("Dm_SY_BancChangeArrive", "Event37")])
@pytest.mark.parametrize("selected", ["", "Weapon_Sword_Biggoron", MASTER])
@pytest.mark.parametrize("owned", [False, True])
def test_story_prop_cannot_create_an_unowned_sword_or_replace_selected_blade(romfs, flow, node, selected, owned):
    data = native(romfs, flow)
    control = evfl.read(data).flowchart
    at = next(i for i, e in enumerate(control.events) if e.name == node)
    onward = control.events[at].next
    candidate = evfl.read(master_sword.force_transform(flow, node)(data)).flowchart
    candidate.entry_points.append(evfl.EntryPoint("TestProp", at))
    state = {EQUIPPED: selected}
    effects = execute(candidate, "TestProp", state, owned=owned, stop=onward)
    created = [
        params["EquipmentActorName"]
        for op, params in effects
        if op == "EventTriggerEquipmentUserRequestCreateStaticEquipment"
    ]
    assert created == ([MASTER] if owned and selected == MASTER else []), effects
    assert state[EQUIPPED] == selected
