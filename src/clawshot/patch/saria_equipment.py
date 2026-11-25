"""Apply bridge Saria's stowed equipment state before the farewell prop binds.

Before Gohma the WarpDone schedule holds Npc_Equipment_009 on Weapon_R.
Changing the schedule variable alone does not update event-driven equipment.
Apply that state through her native event-AI command; leave the authored prop.
"""

from clawshot.census.gifts import _successors
from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Dm_Kokiri_0155"
PATH = f"Event/EventFlow/{FLOW}.bfevfl.zs"
ACTOR = "Npc_Kokiri_Saria_Child"
INSTANCE = "KokiriForest_ArriveLostWood"
ACTION = "EventTriggerChangeAIScheduleEquipState"
EVENT = "ClawshotSariaStowEquipment"
APPLY = "EventAIScheduleSetEquipmentState"
APPLY_EVENT = "ClawshotSariaApplyEquipment"


def patch(data: bytes) -> bytes:
    file = evfl.read(data)
    fc = file.flowchart
    if fc is None or fc.name != FLOW:
        raise PatchError(f"Saria equipment: expected {FLOW} flowchart")
    events = {event.name: i for i, event in enumerate(fc.events)}
    if EVENT in events or APPLY_EVENT in events:
        raise PatchError("Saria equipment: already patched")
    if not {"Event18", "Event3", "Event7"} <= events.keys():
        raise PatchError("Saria equipment: missing native prop setup")
    look, participate, bind = (fc.events[events[name]] for name in ("Event18", "Event3", "Event7"))
    if not all(isinstance(event, evfl.ActionEvent) for event in (look, participate, bind)):
        raise PatchError(f"Saria equipment: changed native setup: {look!r}, {participate!r}, {bind!r}")
    saria = fc.actors[look.actor]
    prop = fc.actors[participate.actor]
    inbound = [event.name for event in fc.events if events["Event3"] in _successors(event)]
    if (
        (saria.name, saria.secondary_name) != (ACTOR, INSTANCE)
        or saria.actions[look.action] != "EventLookAtObjectImmediate"
        or look.next != events["Event3"]
        or participate.next != events["Event7"]
        or prop.name != "Dm_Item_Ocarina_Fairy_Saria"
        or prop.actions[participate.action] != "EventTriggerParticipateEvent"
        or bind.actor != participate.actor
        or prop.actions[bind.action] != "EventTriggerModelBind"
        or (bind.params or {}).get("ActorName") != ACTOR
        or (bind.params or {}).get("InstanceName") != INSTANCE
        or (bind.params or {}).get("BoneName") != "Weapon_R"
        or inbound != ["Event18"]
        or any(entry.main_event in (events["Event3"], events["Event7"]) for entry in fc.entry_points)
    ):
        raise PatchError(f"Saria equipment: changed native setup: {saria!r}, {look!r}, {bind!r}, {inbound!r}")
    for action in (ACTION, APPLY):
        if action not in saria.actions:
            saria.actions.append(action)
    stow = len(fc.events)
    fc.events.extend(
        [
            evfl.ActionEvent(EVENT, look.actor, saria.actions.index(ACTION), stow + 1, {"EquipState": 0}),
            evfl.ActionEvent(APPLY_EVENT, look.actor, saria.actions.index(APPLY), look.next),
        ]
    )
    look.next = stow
    result = evfl.write(file)
    if evfl.read(result) != file:
        raise PatchError("Saria equipment: read-back differs")
    return result


def changes() -> FileChanges:
    return {PATH: patch}
