"""Validate the incoming Kokiri Sword candidate at the native era equipment copy.

Native contracts and evidence: plans/rounds/r17-child-sword.md. No ownership grant,
quest/age write, timing change or new equipment fallback; shield handling stays native.
"""

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Event/EventFlow/ReplaceEquipmentForEraChange.bfevfl.zs"
_CANDIDATE = "PlayerStatus.AnotherEraEquipWeapon"
_PREFIX = "ClawshotChildSword"


def transform(data: bytes) -> bytes:
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "ReplaceEquipmentForEraChange":
        raise PatchError(f"child sword: {FLOW} has the wrong flowchart: {fc!r}")
    if any(event.name.startswith(_PREFIX) for event in fc.events):
        raise PatchError("child sword: equipment flow is already patched")
    named = {event.name: i for i, event in enumerate(fc.events)}
    if "Event8" not in named or "Event0" not in named:
        raise PatchError(f"child sword: equipment flow lacks wait/copy events: {list(named)!r}")
    wait, copy = fc.events[named["Event8"]], fc.events[named["Event0"]]
    if (
        not isinstance(wait, evfl.ActionEvent)
        or fc.actors[wait.actor].name != "EventSystemActor"
        or fc.actors[wait.actor].actions[wait.action] != "EventWait"
        or wait.params != {"Frames": 1, "IsWaitEnd": True}
        or wait.next != named["Event0"]
        or not isinstance(copy, evfl.ActionEvent)
        or fc.actors[copy.actor].name != "GameDataActor"
        or fc.actors[copy.actor].actions[copy.action] != "EventTriggerCopyGameDataString64"
        or copy.params
        != {
            "SrcGameDataName": _CANDIDATE,
            "DstGameDataName": "PlayerStatus.EquipWeapon",
            "Index": -1,
            "SrcIndex": -1,
        }
    ):
        raise PatchError(f"child sword: changed native wait/copy: {wait!r}, {copy!r}")
    game = fc.actors[copy.actor]
    pouches = [i for i, actor in enumerate(fc.actors) if actor.name == "PouchSystemActor"]
    if (
        game.secondary_name
        or game.entry_point != evfl.NONE
        or "EventQueryIsGameDataString64" not in game.queries
        or "EventTriggerSetGameDataString64" not in game.actions
        or len(pouches) != 1
    ):
        raise PatchError(f"child sword: changed native equipment actors: {fc.actors!r}")
    pouch = fc.actors[pouches[0]]
    if pouch.secondary_name or pouch.entry_point != evfl.NONE or "EventQueryIsExistInPouch" not in pouch.queries:
        raise PatchError(f"child sword: changed native pouch actor: {pouch!r}")
    candidate, owned, clear = range(len(fc.events), len(fc.events) + 3)
    onward = named["Event0"]
    fc.events.extend(
        [
            evfl.SwitchEvent(
                f"{_PREFIX}Candidate",
                copy.actor,
                game.queries.index("EventQueryIsGameDataString64"),
                [(0, owned), (1, onward)],
                {"GameDataName": _CANDIDATE, "Index": -1, "Value": "Weapon_Sword_Kokiri"},
            ),
            evfl.SwitchEvent(
                f"{_PREFIX}Owned",
                pouches[0],
                pouch.queries.index("EventQueryIsExistInPouch"),
                [(0, onward), (1, clear)],
                {"Actor": "Weapon_Sword_Kokiri", "Num": 1},
            ),
            evfl.ActionEvent(
                f"{_PREFIX}Clear",
                copy.actor,
                game.actions.index("EventTriggerSetGameDataString64"),
                onward,
                {"GameDataName": _CANDIDATE, "Index": -1, "Value": ""},
            ),
        ]
    )
    wait.next = candidate
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError("child sword: equipment flow does not read back as edited")
    return result


def changes() -> FileChanges:
    return {FLOW: transform}
