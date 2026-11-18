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
KOKIRI = "Weapon_Sword_Kokiri"


def run(fc, state, owned, start="Event8"):
    """Execute the native equipment operations, with ownership separate from equipment."""
    at = next(i for i, event in enumerate(fc.events) if event.name == start)
    trace = []
    for _ in range(100):
        if at == evfl.NONE:
            return trace
        event = fc.events[at]
        actor = fc.actors[event.actor]
        params = event.params or {}
        if isinstance(event, evfl.SwitchEvent):
            op = actor.queries[event.query]
            if op == "EventQueryIsGameDataString64":
                answer = state.get(params["GameDataName"], "") == params["Value"]
            elif op == "EventQueryIsEmptyGameDataString64":
                answer = state.get(params["GameDataName"], "") == ""
            elif op == "EventQueryIsGameDataBool":
                answer = state.get(params["GameDataName"], False)
            elif op == "EventQueryPlayerIsChild":
                answer = state["Sequence_IsChildhood"]
            elif op == "EventQueryIsExistInPouch":
                answer = owned.get(params["Actor"], 0) >= params["Num"]
            else:
                raise AssertionError((actor, event, state, owned))
            at = dict(event.cases)[0 if answer else 1]
            continue
        assert isinstance(event, evfl.ActionEvent), event
        op = actor.actions[event.action]
        trace.append((op, deepcopy(params)))
        if op == "EventTriggerSetGameDataString64" or op == "EventTriggerSetGameDataBool":
            state[params["GameDataName"]] = params["Value"]
        elif op == "EventTriggerCopyGameDataString64":
            state[params["DstGameDataName"]] = state.get(params["SrcGameDataName"], "")
        else:
            assert op in ("EventWait", "EventTriggerPlayerClearNayruLoveCount"), (op, params)
        at = event.next
    raise AssertionError(("equipment flow did not finish", state, trace))


def initial(candidate=KOKIRI, *, child=False):
    return {
        CANDIDATE: candidate,
        EQUIPPED: "Weapon_Sword_Master",
        "PlayerWeaponBeforeForceEquipMasterSword": "",
        "PlayerStatus.AnotherEraEquipShield": "",
        "PlayerStatus.EquipShield": "",
        "Sequence_IsChildhood": child,
        "IsGet.Weapon_Sword_Kokiri": False,
        "PouchData.Weapon_Sword_Kokiri.StockNum": 0,
    }


@pytest.mark.dump
def test_new_seed_child_return_does_not_equip_an_unowned_kokiri_sword(romfs):
    output = make_seed(romfs, 170031, Settings())
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    data = dictionaries.decompress(FLOW, (romfs / FLOW).read_bytes())
    for changes in output.extra_changes:
        if FLOW in changes:
            data = changes[FLOW](data)
    fc = evfl.read(data).flowchart
    state, owned = initial(), {}
    trace = run(fc, state, owned)
    assert state[EQUIPPED] == "", {"state": state, "owned": owned, "trace": trace}
    assert state["IsGet.Weapon_Sword_Kokiri"] is False
    assert state["PouchData.Weapon_Sword_Kokiri.StockNum"] == 0
    assert owned == {}


def equipment_fixture():
    """An invented minimal flow with the native wait/copy interface, not a dump excerpt."""
    game = evfl.Actor(
        "GameDataActor",
        actions=["EventTriggerCopyGameDataString64", "EventTriggerSetGameDataString64"],
        queries=["EventQueryIsGameDataString64"],
    )
    fc = evfl.Flowchart(
        "ReplaceEquipmentForEraChange",
        actors=[
            game,
            evfl.Actor("EventSystemActor", actions=["EventWait"]),
            evfl.Actor("PouchSystemActor", queries=["EventQueryIsExistInPouch"]),
        ],
        events=[
            evfl.ActionEvent("Event8", 1, 0, 1, {"Frames": 1, "IsWaitEnd": True}),
            evfl.ActionEvent(
                "Event0",
                0,
                0,
                evfl.NONE,
                {
                    "SrcGameDataName": CANDIDATE,
                    "DstGameDataName": EQUIPPED,
                    "Index": -1,
                    "SrcIndex": -1,
                },
            ),
        ],
        entry_points=[evfl.EntryPoint("ReplaceEquipmentForEraChange", 0)],
    )
    return evfl.EventFlowFile("ReplaceEquipmentForEraChange", fc)


@pytest.mark.parametrize("candidate", [KOKIRI, "Weapon_Sword_Master", "Weapon_Sword_Biggoron", ""])
@pytest.mark.parametrize("owned", [False, True])
def test_only_an_unowned_kokiri_candidate_is_cleared(candidate, owned):
    document = equipment_fixture()
    fc = evfl.read(equipment.transform(evfl.write(document))).flowchart
    state = initial(candidate)
    pouch = {KOKIRI: int(owned)}
    before = deepcopy(pouch)
    effects = run(fc, state, pouch)
    expected = "" if candidate == KOKIRI and not owned else candidate
    assert state == {**initial(candidate), CANDIDATE: expected, EQUIPPED: expected}
    assert pouch == before
    assert effects[0] == ("EventWait", {"Frames": 1, "IsWaitEnd": True})


def test_changed_wait_copy_contract_and_double_patch_are_refused():
    source = equipment_fixture()
    source.flowchart.events[0].next = evfl.NONE
    with pytest.raises(PatchError, match="changed native wait/copy"):
        equipment.transform(evfl.write(source))
    once = equipment.transform(evfl.write(equipment_fixture()))
    with pytest.raises(PatchError, match="already patched"):
        equipment.transform(once)


@pytest.mark.dump
@pytest.mark.parametrize("candidate", ["", KOKIRI, "Weapon_Sword_Biggoron"])
@pytest.mark.parametrize("owned", [False, True])
def test_native_fallback_and_saved_candidates_preserve_every_other_effect(romfs, candidate, owned):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    data = dictionaries.decompress(FLOW, (romfs / FLOW).read_bytes())
    native = evfl.read(data).flowchart
    patched = evfl.read(equipment.transform(data)).flowchart
    state, old = initial(candidate), initial(candidate)
    pouch = {KOKIRI: int(owned)}
    # From the real entry, the empty adult-to-child candidate first receives the native fallback.
    entry = native.events[native.entry_point("ReplaceEquipmentForEraChange").main_event].name
    effects = run(patched, state, pouch, entry)
    old_effects = run(native, old, pouch, entry)
    if candidate in ("", KOKIRI) and not owned:
        assert old[EQUIPPED] == KOKIRI
        old[EQUIPPED] = ""
        effects = [
            effect
            for effect in effects
            if effect
            != (
                "EventTriggerSetGameDataString64",
                {"GameDataName": CANDIDATE, "Index": -1, "Value": ""},
            )
        ]
    assert state == old
    assert effects == old_effects
    assert pouch == {KOKIRI: int(owned)}
