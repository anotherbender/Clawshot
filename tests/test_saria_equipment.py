"""Synthetic prop setup: scheduled equipment is stowed, not removed from inventory."""

import pytest

from clawshot.formats import evfl
from clawshot.patch import saria_equipment as saria
from clawshot.patch.plan import PatchError


def fixture():
    return evfl.EventFlowFile(
        saria.FLOW,
        flowchart=evfl.Flowchart(
            saria.FLOW,
            [
                evfl.Actor(saria.ACTOR, saria.INSTANCE, actions=["EventLookAtObjectImmediate"]),
                evfl.Actor(
                    "Dm_Item_Ocarina_Fairy_Saria", actions=["EventTriggerParticipateEvent", "EventTriggerModelBind"]
                ),
            ],
            [
                evfl.ActionEvent("Event18", 0, 0, 1),
                evfl.ActionEvent("Event3", 1, 0, 2),
                evfl.ActionEvent(
                    "Event7",
                    1,
                    1,
                    params={"ActorName": saria.ACTOR, "InstanceName": saria.INSTANCE, "BoneName": "Weapon_R"},
                ),
            ],
            [evfl.EntryPoint("ready", 0)],
        ),
    )


def test_stow_precedes_participation_and_bind_without_changing_the_prop():
    before = fixture()
    after = evfl.read(saria.patch(evfl.write(before)))
    fc = after.flowchart
    assert fc.entry_point("ready").main_event == 0
    look = fc.events[0]
    stow = fc.events[look.next]
    assert (fc.actors[stow.actor].name, fc.actors[stow.actor].secondary_name) == (saria.ACTOR, saria.INSTANCE)
    assert fc.actors[stow.actor].actions[stow.action] == saria.ACTION
    assert stow.params == {"EquipState": 0}
    assert stow.next == 1
    assert fc.events[1:3] == before.flowchart.events[1:3]
    assert evfl.read(evfl.write(after)) == after
    with pytest.raises(PatchError, match="already patched"):
        saria.patch(evfl.write(after))


@pytest.mark.parametrize("fault", ["instance", "bind", "bypass"])
def test_refuses_stale_bridge_instance_or_prop_setup(fault):
    file = fixture()
    fc = file.flowchart
    if fault == "instance":
        fc.actors[0].secondary_name = "NotTheBridgeSaria"
    elif fault == "bind":
        fc.events[2].params["BoneName"] = "OtherBone"
    else:
        fc.entry_points.append(evfl.EntryPoint("BypassStow", 1))
    with pytest.raises(PatchError, match="changed native setup"):
        saria.patch(evfl.write(file))
