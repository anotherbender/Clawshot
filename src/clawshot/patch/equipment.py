"""Equip the child's Kokiri Sword on an era change only once it has been got.

Native contracts: plans/rounds/r17-child-sword.md. Ownership is the explicit saved ``IsGet.Weapon_Sword_Kokiri``
(plans/03-game-data.md section 19: set by the game whenever the sword enters the pouch, however it is got; no native
flow removes the Kokiri Sword), read with this flow's own Bool query. Equipping does not set it (round 18's copied
saves: Kokiri Sword equipped, IsGet false, stock 0), so a merely equipped sword never counts as owned.

[INFERENCE] A flow's GameData writes are visible to its reads only after it yields a frame. No native commit code was
read; the evidence is the data: native flows separate a write and a read of the same name with an ``EventWait`` (62 of
64 such pairs; the other two are this flow's Event0/Event1 and Event2/Event3, which only work as swaps if each reads
the value from before the other), this flow writes its era defaults (Event5/Event11) and shield fixes before its
one-frame wait (Event8), and round 17's clear, placed after that wait, left the saved child with EquipWeapon Kokiri
and other-era Master, as Event0 reading the stale candidate and Event7 replacing the clear predicts.

So the guard writes only before the native wait, correct under either visibility: the adult branch writes its Kokiri
default (Event11) only when the sword is got, and a saved Kokiri candidate (Event4's non-empty branch) is cleared when
it is not. No ownership grant, quest/age write, added frame or other fallback; shields and the swap stay native.
"""

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Event/EventFlow/ReplaceEquipmentForEraChange.bfevfl.zs"
_ENTRY = "ReplaceEquipmentForEraChange"
_CANDIDATE = "PlayerStatus.AnotherEraEquipWeapon"
_KOKIRI = "Weapon_Sword_Kokiri"
_OWNED = f"IsGet.{_KOKIRI}"
_PREFIX = "ClawshotChildSword"


def _op(fc: evfl.Flowchart, event: evfl.Event) -> tuple[str, str, str] | None:
    """(``action`` or ``query``, actor name, operation) of a plain event; None for any other event type."""
    if isinstance(event, evfl.ActionEvent):
        return "action", fc.actors[event.actor].name, fc.actors[event.actor].actions[event.action]
    if isinstance(event, evfl.SwitchEvent):
        return "query", fc.actors[event.actor].name, fc.actors[event.actor].queries[event.query]
    return None


def _reaches_wait_untouched(fc: evfl.Flowchart, start: int, wait: int) -> bool:
    """Every path from ``start`` reaches ``wait`` through plain events none of which names the candidate."""
    seen, stack = set(), [start]
    while stack:
        at = stack.pop()
        if at == wait or at in seen:
            continue
        seen.add(at)
        event = fc.events[at]
        if isinstance(event, evfl.ActionEvent):
            following = [event.next]
        elif isinstance(event, evfl.SwitchEvent):
            following = [target for _, target in event.cases]
        else:
            return False
        if evfl.NONE in following or _CANDIDATE in (event.params or {}).values():
            return False
        stack.extend(following)
    return True


def transform(data: bytes) -> bytes:
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != _ENTRY:
        raise PatchError(f"child sword: {FLOW} has the wrong flowchart: {fc!r}")
    if any(event.name.startswith(_PREFIX) for event in fc.events):
        raise PatchError("child sword: equipment flow is already patched")
    named = {event.name: i for i, event in enumerate(fc.events)}
    anchors = ("Event4", "Event10", "Event11", "Event13", "Event8", "Event0")
    if any(name not in named for name in anchors):
        raise PatchError(f"child sword: equipment flow lacks its native anchors: {list(named)!r}")
    empty, age, default, _shields, wait, copy = (fc.events[named[name]] for name in anchors)
    if (
        fc.entry_point(_ENTRY).main_event != named["Event4"]
        or _op(fc, empty) != ("query", "GameDataActor", "EventQueryIsEmptyGameDataString64")
        or empty.params != {"GameDataName": _CANDIDATE, "Index": -1}
        or dict(empty.cases) != {0: named["Event10"], 1: named["Event13"]}
        or _op(fc, age) != ("query", "Player_Event", "EventQueryPlayerIsChild")
        or dict(age.cases).get(1) != named["Event11"]
        or _op(fc, default) != ("action", "GameDataActor", "EventTriggerSetGameDataString64")
        or default.params != {"GameDataName": _CANDIDATE, "Index": -1, "Value": _KOKIRI}
        or default.next != named["Event13"]
    ):
        raise PatchError(f"child sword: changed native candidate branches: {empty!r}, {age!r}, {default!r}")
    if (
        _op(fc, wait) != ("action", "EventSystemActor", "EventWait")
        or wait.params != {"Frames": 1, "IsWaitEnd": True}
        or wait.next != named["Event0"]
        or _op(fc, copy) != ("action", "GameDataActor", "EventTriggerCopyGameDataString64")
        or copy.params
        != {
            "SrcGameDataName": _CANDIDATE,
            "DstGameDataName": "PlayerStatus.EquipWeapon",
            "Index": -1,
            "SrcIndex": -1,
        }
    ):
        raise PatchError(f"child sword: changed native wait/copy: {wait!r}, {copy!r}")
    # The guard's writes must be committed by the native wait before Event0 reads them.
    if not _reaches_wait_untouched(fc, named["Event13"], named["Event8"]):
        raise PatchError("child sword: native shield handling no longer leads to the wait without the candidate")
    game = fc.actors[copy.actor]
    if (
        game.secondary_name
        or game.entry_point != evfl.NONE
        or any(query not in game.queries for query in ("EventQueryIsGameDataBool", "EventQueryIsGameDataString64"))
        or "EventTriggerSetGameDataString64" not in game.actions
    ):
        raise PatchError(f"child sword: changed native equipment actors: {fc.actors!r}")

    is_bool = game.queries.index("EventQueryIsGameDataBool")
    owned = {"GameDataName": _OWNED, "Index": -1}
    default_owned, saved, saved_owned, clear = range(len(fc.events), len(fc.events) + 4)
    onward = named["Event13"]
    fc.events.extend(
        [
            # Adult branch: write the native Kokiri default only once the sword has been got.
            evfl.SwitchEvent(
                f"{_PREFIX}DefaultOwned", copy.actor, is_bool, [(0, named["Event11"]), (1, onward)], owned
            ),
            # Saved candidate: clear a Kokiri Sword that was never got; anything else stays.
            evfl.SwitchEvent(
                f"{_PREFIX}Candidate",
                copy.actor,
                game.queries.index("EventQueryIsGameDataString64"),
                [(0, saved_owned), (1, onward)],
                {"GameDataName": _CANDIDATE, "Index": -1, "Value": _KOKIRI},
            ),
            evfl.SwitchEvent(f"{_PREFIX}Owned", copy.actor, is_bool, [(0, onward), (1, clear)], dict(owned)),
            evfl.ActionEvent(
                f"{_PREFIX}Clear",
                copy.actor,
                game.actions.index("EventTriggerSetGameDataString64"),
                onward,
                {"GameDataName": _CANDIDATE, "Index": -1, "Value": ""},
            ),
        ]
    )
    age.cases = [(value, default_owned if value == 1 else target) for value, target in age.cases]
    empty.cases = [(value, saved if value == 1 else target) for value, target in empty.cases]
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError("child sword: equipment flow does not read back as edited")
    return result


def changes() -> FileChanges:
    return {FLOW: transform}
