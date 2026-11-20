"""Incoming child sword equipment must be owned, not granted by the era fallback."""

from copy import deepcopy

import pytest

from clawshot.formats import evfl, zsdic
from clawshot.generate import Settings
from clawshot.patch import equipment, make_seed
from clawshot.patch.plan import PatchError

FLOW = "Event/EventFlow/ReplaceEquipmentForEraChange.bfevfl.zs"
CANDIDATE = "PlayerStatus.AnotherEraEquipWeapon"
EQUIPPED = "PlayerStatus.EquipWeapon"
BEFORE_FORCE = "PlayerWeaponBeforeForceEquipMasterSword"
KOKIRI = "Weapon_Sword_Kokiri"
MASTER = "Weapon_Sword_Master"
OWNED = "IsGet.Weapon_Sword_Kokiri"
EQUIPMENT = (EQUIPPED, CANDIDATE, "PlayerStatus.EquipShield", "PlayerStatus.AnotherEraEquipShield")
VISIBILITY = ["immediate", "buffered"]
READING = ["stock", "equipped"]
DEFAULT = ("EventTriggerSetGameDataString64", {"GameDataName": CANDIDATE, "Index": -1, "Value": KOKIRI})
CLEAR = ("EventTriggerSetGameDataString64", {"GameDataName": CANDIDATE, "Index": -1, "Value": ""})


def run(fc, state, pouch, *, child, visibility="buffered", reading="stock"):
    """Execute the flow's operations; ownership (``IsGet``, pouch stock) stays separate from equipment.

    ``visibility``: ``immediate`` reads a GameData write back at once; ``buffered`` reads the committed values and
    commits writes at the next ``EventWait`` or at the end (the [INFERENCE] in patch/equipment.py). The guard must be
    right under both. ``reading``: ``EventQueryIsExistInPouch`` counts stock, or also any merely equipped item.
    ``child`` is the player's age (``EventQueryPlayerIsChild``); ``Sequence_IsChildhood`` is the saved flag.
    """
    at = fc.entry_point("ReplaceEquipmentForEraChange").main_event
    pending, trace = {}, []

    def commit():
        state.update(pending)
        pending.clear()

    for _ in range(100):
        if at == evfl.NONE:
            commit()
            return trace
        event = fc.events[at]
        actor = fc.actors[event.actor]
        params = event.params or {}
        view = state if visibility == "buffered" else {**state, **pending}
        if isinstance(event, evfl.SwitchEvent):
            op = actor.queries[event.query]
            if op == "EventQueryIsGameDataString64":
                answer = view.get(params["GameDataName"], "") == params["Value"]
            elif op == "EventQueryIsEmptyGameDataString64":
                answer = view.get(params["GameDataName"], "") == ""
            elif op == "EventQueryIsGameDataBool":
                answer = view.get(params["GameDataName"], False)
            elif op == "EventQueryIsGameDataInt":
                value = view.get(params["GameDataName"], 0)
                comparison = 0 if value == params["Value"] else 1 if value < params["Value"] else 2
                at = dict(event.cases)[comparison]
                continue
            elif op == "EventQueryPlayerIsChild":
                answer = child
            elif op == "EventQueryIsExistInPouch":
                answer = pouch.get(params["Actor"], 0) >= params["Num"]
                if reading == "equipped":
                    answer = answer or params["Actor"] in (view.get(name, "") for name in EQUIPMENT)
            else:
                raise AssertionError((actor, event, state, pouch))
            at = dict(event.cases)[0 if answer else 1]
            continue
        assert isinstance(event, evfl.ActionEvent), event
        op = actor.actions[event.action]
        trace.append((op, deepcopy(params)))
        if op in ("EventTriggerSetGameDataString64", "EventTriggerSetGameDataBool"):
            pending[params["GameDataName"]] = params["Value"]
        elif op == "EventTriggerCopyGameDataString64":
            pending[params["DstGameDataName"]] = view.get(params["SrcGameDataName"], "")
        elif op == "EventWait":
            commit()
        else:
            assert op == "EventTriggerPlayerClearNayruLoveCount", (op, params)
        if visibility == "immediate":
            commit()
        at = event.next
    raise AssertionError(("equipment flow did not finish", state, trace))


def initial(candidate=KOKIRI, *, owned=False, child=False):
    """The state on entry: adult-to-child after Dm_TimeTemple_0070 recorded the Master Sword, or child-to-adult."""
    return {
        CANDIDATE: candidate,
        EQUIPPED: (KOKIRI if owned else "") if child else MASTER,
        BEFORE_FORCE: "" if child else MASTER,
        "PlayerStatus.AnotherEraEquipShield": "",
        "PlayerStatus.EquipShield": "",
        "Sequence_IsChildhood": child,
        OWNED: owned,
    }


def native_flow(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    return dictionaries.decompress(FLOW, (romfs / FLOW).read_bytes())


@pytest.mark.dump
def test_new_seed_child_return_does_not_equip_an_unowned_kokiri_sword(romfs):
    output = make_seed(romfs, 170031, Settings())
    data = native_flow(romfs)
    for changes in output.extra_changes:
        if FLOW in changes:
            data = changes[FLOW](data)
    fc = evfl.read(data).flowchart
    for visibility in VISIBILITY:
        for reading in READING:
            state, pouch = initial(""), {KOKIRI: 0}
            trace = run(fc, state, pouch, child=False, visibility=visibility, reading=reading)
            assert state[EQUIPPED] == "", {"state": state, "trace": trace}
            assert state[CANDIDATE] == MASTER
            assert state[OWNED] is False
            assert pouch == {KOKIRI: 0}


def equipment_fixture():
    """An invented minimal flow with the native candidate, wait and copy interface, not a dump excerpt."""
    game = evfl.Actor(
        "GameDataActor",
        actions=["EventTriggerCopyGameDataString64", "EventTriggerSetGameDataString64"],
        queries=["EventQueryIsEmptyGameDataString64", "EventQueryIsGameDataString64", "EventQueryIsGameDataBool"],
    )

    def set_candidate(name, value):
        return evfl.ActionEvent(name, 0, 1, 4, {"GameDataName": CANDIDATE, "Index": -1, "Value": value})

    fc = evfl.Flowchart(
        "ReplaceEquipmentForEraChange",
        actors=[
            game,
            evfl.Actor("EventSystemActor", actions=["EventWait"]),
            evfl.Actor("Player_Event", queries=["EventQueryPlayerIsChild"]),
        ],
        events=[
            evfl.SwitchEvent("Event4", 0, 0, [(0, 1), (1, 4)], {"GameDataName": CANDIDATE, "Index": -1}),
            evfl.SwitchEvent("Event10", 2, 0, [(0, 2), (1, 3)]),
            set_candidate("Event5", MASTER),
            set_candidate("Event11", KOKIRI),
            evfl.SwitchEvent(
                "Event13", 0, 0, [(0, 5), (1, 5)], {"GameDataName": "PlayerStatus.AnotherEraEquipShield", "Index": -1}
            ),
            evfl.ActionEvent("Event8", 1, 0, 6, {"Frames": 1, "IsWaitEnd": True}),
            evfl.ActionEvent(
                "Event0",
                0,
                0,
                evfl.NONE,
                {"SrcGameDataName": CANDIDATE, "DstGameDataName": EQUIPPED, "Index": -1, "SrcIndex": -1},
            ),
        ],
        entry_points=[evfl.EntryPoint("ReplaceEquipmentForEraChange", 0)],
    )
    return evfl.EventFlowFile("ReplaceEquipmentForEraChange", fc)


@pytest.mark.parametrize("visibility", VISIBILITY)
@pytest.mark.parametrize("child", [False, True])
@pytest.mark.parametrize("owned", [False, True])
@pytest.mark.parametrize("candidate", [KOKIRI, MASTER, "Weapon_Sword_Biggoron", ""])
def test_only_an_unowned_kokiri_candidate_is_not_equipped(candidate, owned, child, visibility):
    fc = evfl.read(equipment.transform(evfl.write(equipment_fixture()))).flowchart
    state = initial(candidate, owned=owned, child=child)
    pouch = {KOKIRI: int(owned)}
    effects = run(fc, state, pouch, child=child, visibility=visibility)
    if candidate == "":
        expected = MASTER if child else KOKIRI if owned else ""
    else:
        expected = "" if candidate == KOKIRI and not owned else candidate
    assert state == {**initial(candidate, owned=owned, child=child), CANDIDATE: expected, EQUIPPED: expected}
    assert pouch == {KOKIRI: int(owned)}
    # Every guard write precedes the one native wait; nothing new runs between it and the copy.
    waits = [i for i, (op, _) in enumerate(effects) if op == "EventWait"]
    assert len(waits) == 1 and effects[waits[0] :] == [
        ("EventWait", {"Frames": 1, "IsWaitEnd": True}),
        (
            "EventTriggerCopyGameDataString64",
            {"SrcGameDataName": CANDIDATE, "DstGameDataName": EQUIPPED, "Index": -1, "SrcIndex": -1},
        ),
    ]


@pytest.mark.parametrize("visibility", VISIBILITY)
def test_ownership_is_the_isget_record_not_equipment_or_pouch_answers(visibility):
    """A merely equipped sword, even one a pouch query would call held, is not owned."""
    fc = evfl.read(equipment.transform(evfl.write(equipment_fixture()))).flowchart
    for candidate in (KOKIRI, ""):
        state = {**initial(candidate), EQUIPPED: KOKIRI}
        run(fc, state, {KOKIRI: 1}, child=False, visibility=visibility, reading="equipped")
        assert (state[EQUIPPED], state[CANDIDATE], state[OWNED]) == ("", "", False), (candidate, state)


def test_changed_native_contract_and_double_patch_are_refused():
    def refused(edit, match):
        source = equipment_fixture()
        edit(source.flowchart.events)
        with pytest.raises(PatchError, match=match):
            equipment.transform(evfl.write(source))

    refused(lambda events: setattr(events[5], "next", evfl.NONE), "changed native wait/copy")
    refused(lambda events: events[3].params.update(Value=MASTER), "changed native candidate branches")
    refused(lambda events: setattr(events[0], "cases", [(0, 1), (1, 5)]), "changed native candidate branches")
    refused(lambda events: events[4].params.update(GameDataName=CANDIDATE), "shield handling")
    once = equipment.transform(evfl.write(equipment_fixture()))
    with pytest.raises(PatchError, match="already patched"):
        equipment.transform(once)


@pytest.mark.dump
@pytest.mark.parametrize("visibility", VISIBILITY)
@pytest.mark.parametrize("reading", READING)
@pytest.mark.parametrize("child", [False, True])
@pytest.mark.parametrize("candidate", ["", KOKIRI, MASTER, "Weapon_Sword_Biggoron"])
@pytest.mark.parametrize("owned", [False, True])
def test_native_effects_are_kept_except_an_unowned_kokiri_sword(romfs, owned, candidate, child, reading, visibility):
    data = native_flow(romfs)
    native = evfl.read(data).flowchart
    patched = evfl.read(equipment.transform(data)).flowchart
    state, old = initial(candidate, owned=owned, child=child), initial(candidate, owned=owned, child=child)
    pouch = {KOKIRI: int(owned)}
    model = {"child": child, "visibility": visibility, "reading": reading}
    effects = run(patched, state, pouch, **model)
    old_effects = run(native, old, pouch, **model)
    if old[EQUIPPED] == KOKIRI and not owned:
        # The native fallback or saved candidate equips a sword never got; the guard leaves the slot empty instead.
        assert state[EQUIPPED] == ""
        old = {name: "" if name in (EQUIPPED, CANDIDATE) and value == KOKIRI else value for name, value in old.items()}
        old_effects = [effect for effect in old_effects if effect != DEFAULT]
        effects = [effect for effect in effects if effect != CLEAR]
    assert state == old
    assert effects == old_effects
    assert pouch == {KOKIRI: int(owned)}


@pytest.mark.dump
@pytest.mark.parametrize("owned", [False, True])
def test_round_trip_reproduces_the_saved_failure_and_keeps_an_owned_sword(romfs, owned):
    """Child -> first pull -> return, under buffered visibility (immediate visibility cannot reach the saved state).

    Round 18's copied saves of a never-got sword: EquipWeapon Kokiri, other era Master. The native flow, which
    round 17's late clear did not change, gives exactly that; the guard gives an empty slot. An owned sword returns.
    """
    data = native_flow(romfs)
    results = {}
    flows = {"native": evfl.read(data).flowchart, "patched": evfl.read(equipment.transform(data)).flowchart}
    for name, fc in flows.items():
        state, pouch = initial("", owned=owned, child=True), {KOKIRI: int(owned)}
        history = []
        for _ in range(2):
            run(fc, state, pouch, child=True)
            state["Sequence_IsChildhood"] = False  # the caller's write after the sub flow
            history.append((state[EQUIPPED], state[CANDIDATE]))
            state[BEFORE_FORCE] = state[EQUIPPED]  # Dm_TimeTemple_0070 Event3, before the return
            run(fc, state, pouch, child=False)
            state["Sequence_IsChildhood"] = True
            history.append((state[EQUIPPED], state[CANDIDATE]))
        assert state[OWNED] is owned and pouch == {KOKIRI: int(owned)}
        results[name] = history
    child_sword = KOKIRI if owned else ""
    assert results["native"][1] == (KOKIRI, MASTER)
    assert results["patched"] == [(MASTER, child_sword), (child_sword, MASTER)] * 2
