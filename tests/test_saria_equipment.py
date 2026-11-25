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


def test_suspended_schedule_is_applied_before_the_authored_prop_binds():
    before = fixture()
    after = evfl.read(saria.patch(evfl.write(before)))
    fc = after.flowchart
    # A schedule-variable write alone was the played v1 failure: the field brain
    # is paused, leaving the accessory visible until equipment is applied now.
    scheduled, visible_accessory = 1, True
    index = fc.entry_point("ready").main_event
    bound = False
    for _ in range(10):
        if index == evfl.NONE:
            break
        event = fc.events[index]
        actor = fc.actors[event.actor]
        action = actor.actions[event.action]
        if action == "EventTriggerChangeAIScheduleEquipState" and event.actor == 0:
            scheduled = event.params["EquipState"]
        elif action == "EventAIScheduleSetEquipmentState" and event.actor == 0:
            visible_accessory = scheduled != 0
        elif action == "EventTriggerModelBind":
            assert not visible_accessory, "the scheduled red accessory must not overlap the authored prop"
            bound = True
        index = event.next
    else:
        raise AssertionError("farewell setup did not finish")
    assert bound
    assert fc.events[1:3] == before.flowchart.events[1:3]
    assert evfl.read(evfl.write(after)) == after
    with pytest.raises(PatchError):
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
