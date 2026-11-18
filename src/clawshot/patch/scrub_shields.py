"""Finish a scrub shield hand-over without requiring the shield to equip (issue #33).

The native helper grants with ``IsEquipDIrect=false`` but then polls equipment forever.
Its Mirror check also names the grant actor instead of the equipment actor. Neither a
wrong-age shield nor inventory-only receipt can satisfy that contract. Keep the native
grant and its one-frame yield, then return to the native ActionGuide and cleanup.
No forced equip, ownership change, retry budget or extra grant is introduced.
"""

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Dm_SY_GetInEvent"
PATH = f"Event/EventFlow/{FLOW}.bfevfl.zs"
# RSDB PouchActorInfo rows with PouchCategory Shield (build e0f3ccfa): the rewards that take the helper.
SHIELDS = frozenset(
    {
        "Item_Shield_Mirror",
        "Obj_Shield_Deku",
        "Obj_Shield_Hylian",
        "Shop_Weapon_Shield_Deku",
        "Shop_Weapon_Shield_Hylian",
        "TBox_Shield_Deku",
        "TBox_Shield_Hylian",
        "Weapon_Shield_Deku",
        "Weapon_Shield_Hylian",
        "Weapon_Shield_Mirror",
    }
)
SLOT = 4


def _equip_check(fc: evfl.Flowchart, event: evfl.Event, armor: str, then: int) -> bool:
    return (
        isinstance(event, evfl.SwitchEvent)
        and fc.actors[event.actor].name == "Player_Event"
        and fc.actors[event.actor].queries[event.query] == "EventQueryPlayerIsEquipWeapon"
        and event.params == {"WeaponSlot": SLOT, "ArmorName": armor}
        and event.cases == [(1, then)]
    )


def patch_flowchart(fc: evfl.Flowchart) -> None:
    """Validate before mutation; replace the equipment prerequisite with the native one-frame yield."""
    if fc.name != FLOW:
        raise PatchError(f"{FLOW}: wrong flowchart")
    names = ("Event442", "Event514", "Event537", "Event509", "Event513")
    if any(sum(event.name == name for event in fc.events) != 1 for name in names):
        raise PatchError(f"{FLOW}: missing or duplicate shield helper events")
    index = {event.name: i for i, event in enumerate(fc.events)}
    add, hylian, mirror, deku, wait = (fc.events[index[name]] for name in names)
    if not (
        isinstance(add, evfl.ActionEvent)
        and fc.actors[add.actor].name == "PouchSystemActor"
        and fc.actors[add.actor].actions[add.action] == "EventTriggerAddOrRemovePouchContent"
        and (add.params or {}).get("Actor") == evfl.Argument("ActorName")
        and add.params.get("Num") == 1
        and add.params.get("IsEquipDIrect") is False
        and add.next == index["Event514"]
        and _equip_check(fc, hylian, "Weapon_Shield_Hylian", index["Event537"])
        and _equip_check(fc, mirror, "Item_Shield_Mirror", index["Event509"])
        and _equip_check(fc, deku, "Weapon_Shield_Deku", index["Event513"])
        and hylian.actor == mirror.actor == deku.actor
        and hylian.query == mirror.query == deku.query
        and isinstance(wait, evfl.ActionEvent)
        and fc.actors[wait.actor].name == "EventSystemActor"
        and fc.actors[wait.actor].actions[wait.action] == "EventWait"
        and wait.params == {"IsWaitEnd": True, "Frames": 1}
        and wait.next == index["Event509"]
    ):
        raise PatchError(f"{FLOW}: stale shield equip wait {add!r}, {hylian!r}, {mirror!r}, {deku!r}, {wait!r}")
    add.next = index["Event513"]
    wait.next = evfl.NONE


def transform(data: bytes) -> bytes:
    document = evfl.read(data)
    if document.flowchart is None:
        raise PatchError(f"{PATH}: no flowchart")
    patch_flowchart(document.flowchart)
    out = evfl.write(document)
    if evfl.read(out) != document:
        raise PatchError(f"{PATH}: changed flow does not read back")
    return out


def changes() -> FileChanges:
    return {PATH: transform}
