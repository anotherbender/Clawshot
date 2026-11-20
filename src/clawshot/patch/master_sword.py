"""Opt-in pedestal item and owned-only Master Sword equipment.

Native anchors and Boolean pins: plans/rounds/r18-master-sword-design.md.
Unowned cinematic weapons are never created, rather than creating a prop and
hoping its native cleanup removes it. Travel, scene history and era writes stay.
"""

from collections.abc import Callable, Mapping
from dataclasses import replace

from clawshot.formats import evfl
from clawshot.patch import equipment
from clawshot.patch.items import load as item_actors
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

MASTER = "Weapon_Sword_Master"
PEDESTAL = "Master Sword Pedestal"
DOOR = "Event/EventFlow/DoorOfTime.bfevfl.zs"
CANDIDATE = "PlayerStatus.AnotherEraEquipWeapon"
STASH = "PlayerWeaponBeforeForceEquipMasterSword"
ADULT_BLADES = (MASTER, "Weapon_Sword_Biggoron", "Weapon_Sword_Giant", "Weapon_Sword_BrokenGiant")
PREFIX = "ClawshotMasterSword"


def _chart(data: bytes, name: str) -> tuple[evfl.EventFlowFile, evfl.Flowchart, dict[str, int]]:
    doc = evfl.read(data)
    fc = doc.flowchart
    if fc is None or fc.name != name:
        raise PatchError(f"Master Sword: expected {name} flowchart")
    if any(event.name.startswith(PREFIX) for event in fc.events):
        raise PatchError(f"Master Sword: {name} already patched")
    return doc, fc, {event.name: i for i, event in enumerate(fc.events)}


def _write(doc: evfl.EventFlowFile) -> bytes:
    result = evfl.write(doc)
    if evfl.read(result) != doc:
        raise PatchError("Master Sword: edited flow does not read back")
    return result


def _operation(fc: evfl.Flowchart, actor: str, operation: str, *, query: bool = False) -> tuple[int, int]:
    index = next((i for i, entry in enumerate(fc.actors) if entry.name == actor and not entry.secondary_name), None)
    if index is None:
        index = len(fc.actors)
        fc.actors.append(evfl.Actor(actor))
    names = fc.actors[index].queries if query else fc.actors[index].actions
    if operation not in names:
        names.append(operation)
    return index, names.index(operation)


def _owned(fc: evfl.Flowchart, name: str, blade: str, yes: int, no: int) -> int:
    actor, query = _operation(fc, "GameDataActor", "EventQueryIsGameDataBool", query=True)
    _, stock_query = _operation(fc, "GameDataActor", "EventQueryIsGameDataInt", query=True)
    stock, flag = len(fc.events), len(fc.events) + 1
    # Native Int comparison: 0=equal, 1=less, 2=greater (progressive magic's MPMax guard).
    # Giant/BrokenGiant can be removed during trade; historical IsGet alone is insufficient.
    fc.events.extend(
        [
            evfl.SwitchEvent(
                f"{name}Stock",
                actor,
                stock_query,
                [(0, no), (1, no), (2, yes)],
                {"GameDataName": f"PouchData.{blade}.StockNum", "Index": -1, "Value": 0},
            ),
            evfl.SwitchEvent(
                name,
                actor,
                query,
                [(0, stock), (1, no)],
                {"GameDataName": f"IsGet.{blade}", "Index": -1},
            ),
        ]
    )
    return flag


def _validate_blade(fc: evfl.Flowchart, field: str, yes: int, no: int, label: str) -> int:
    """An empty or unrelated field stays native; each actual adult blade needs its own ownership."""
    actor, query = _operation(fc, "GameDataActor", "EventQueryIsGameDataString64", query=True)
    onward = yes
    for blade in reversed(ADULT_BLADES):
        owned = _owned(fc, f"{PREFIX}{label}Owned{blade}", blade, yes, no)
        at = len(fc.events)
        fc.events.append(
            evfl.SwitchEvent(
                f"{PREFIX}{label}Is{blade}",
                actor,
                query,
                [(0, owned), (1, onward)],
                {"GameDataName": field, "Index": -1, "Value": blade},
            )
        )
        onward = at
    return onward


def era_transform(data: bytes) -> bytes:
    """Compose after the round-18 child guard; keep its pre-wait ordering and native shield handling."""
    doc, fc, named = _chart(data, "ReplaceEquipmentForEraChange")
    if "ClawshotChildSwordCandidate" not in named:
        raise PatchError("Master Sword: round-18 child ownership guard must run first")
    default = fc.events[named["Event5"]]
    age = fc.events[named["Event10"]]
    empty = fc.events[named["Event4"]]
    restore = fc.events[named["Event7"]]
    era = fc.events[named["Event6"]]
    if (
        equipment._op(fc, default) != ("action", "GameDataActor", "EventTriggerSetGameDataString64")
        or default.params != {"GameDataName": CANDIDATE, "Value": MASTER, "Index": -1}
        or dict(age.cases).get(0) != named["Event5"]
        or equipment._op(fc, restore) != ("action", "GameDataActor", "EventTriggerCopyGameDataString64")
        or restore.params != {"DstGameDataName": CANDIDATE, "Index": -1, "SrcIndex": -1, "SrcGameDataName": STASH}
        or dict(era.cases).get(1) != named["Event7"]
    ):
        raise PatchError(f"Master Sword: changed native defaults/restore: {default!r}, {restore!r}, {era!r}")
    actor, action = _operation(fc, "GameDataActor", "EventTriggerSetGameDataString64")
    clear_candidate = len(fc.events)
    fc.events.append(
        evfl.ActionEvent(
            f"{PREFIX}ClearCandidate",
            actor,
            action,
            named["Event13"],
            {"GameDataName": CANDIDATE, "Index": -1, "Value": ""},
        )
    )
    old_candidate = dict(empty.cases)[1]
    candidate_guard = _validate_blade(fc, CANDIDATE, old_candidate, clear_candidate, "Candidate")
    default_guard = _owned(fc, f"{PREFIX}DefaultOwned", MASTER, named["Event5"], named["Event13"])
    clear_stash_candidate = len(fc.events)
    fc.events.append(
        evfl.ActionEvent(
            f"{PREFIX}ClearRestoredCandidate",
            actor,
            action,
            restore.next,
            {"GameDataName": CANDIDATE, "Index": -1, "Value": ""},
        )
    )
    stash_guard = _validate_blade(fc, STASH, named["Event7"], clear_stash_candidate, "Stash")
    empty.cases = [(pin, candidate_guard if pin == 1 else target) for pin, target in empty.cases]
    age.cases = [(pin, default_guard if pin == 0 else target) for pin, target in age.cases]
    era.cases = [(pin, stash_guard if pin == 1 else target) for pin, target in era.cases]
    return _write(doc)


def pedestal_transform(actor: str) -> Callable[[bytes], bytes]:
    def apply(data: bytes) -> bytes:
        doc, fc, named = _chart(data, "DoorOfTime")
        at = named["Event115"]
        grant = fc.events[at]
        if (
            equipment._op(fc, grant) != ("action", "PouchSystemActor", "EventTriggerAddOrRemovePouchContent")
            or grant.params
            != {
                "Num": 1,
                "IsSetMessageTargetActorName": True,
                "Actor": MASTER,
                "IsEquipDIrect": True,
                "IsGetEvent": False,
            }
            or not isinstance(fc.events[grant.next], evfl.SubFlowEvent)
            or fc.events[grant.next].flowchart != "ReplaceEquipmentForEraChange"
        ):
            raise PatchError(f"Master Sword: changed first-pull grant: {grant!r}")
        # This is still the white-faded first-pull boot handoff, before the age
        # write and Rauru reservation. Do not hold it on a get-window/dialog wait.
        # Keep the native nonblocking receipt; only its reward/equip policy changes.
        fc.events[at] = replace(grant, params={**grant.params, "Actor": actor, "IsEquipDIrect": False})
        return _write(doc)

    return apply


def pose_transform(flow: str, before: str, target: str) -> Callable[[bytes], bytes]:
    def apply(data: bytes) -> bytes:
        doc, fc, named = _chart(data, flow)
        event = fc.events[named[before]]
        if not isinstance(event, evfl.ActionEvent) or event.next != named[target]:
            raise PatchError(f"Master Sword: changed {flow} pose boundary: {event!r}")
        equipped = fc.events[named[target]]
        if (
            equipment._op(fc, equipped) != ("query", "Player_Event", "EventQueryPlayerIsEquipWeapon")
            or equipped.params != {"ArmorName": MASTER, "WeaponSlot": 0}
            or set(dict(equipped.cases)) != {0, 1}
        ):
            raise PatchError(f"Master Sword: changed {flow} equipment predicate: {equipped!r}")
        # Never replace another selected blade with a cinematic Master Sword,
        # even when both are owned. An already-selected Master keeps its native pose.
        equipped.cases = [(pin, evfl.NONE if pin == 1 else onward) for pin, onward in equipped.cases]
        # Both static-equipment demos stash the real weapon before entering this
        # sub-entry's force-and-poll chain. False returns only from that setup,
        # leaving the caller's animation and real age transition intact.
        event.next = _owned(fc, f"{PREFIX}PoseOwned", MASTER, named[target], evfl.NONE)
        return _write(doc)

    return apply


def arrival_transform(data: bytes) -> bytes:
    doc, fc, named = _chart(data, "Dm_TimeTemple_0085")
    create = fc.events[named["Event37"]]
    wait = fc.events[named["Event0"]]
    restore = fc.events[named["Event5"]]
    finished = fc.events[named["Event19"]]
    if (
        not isinstance(create, evfl.SwitchEvent)
        or dict(create.cases) != {1: named["Event9"]}
        or equipment._op(fc, create) != ("query", "Player_Event", "EventQueryPlayerIsEquipWeapon")
        or equipment._op(fc, wait) != ("action", "EventSystemActor", "EventWait")
        or wait.next != named["Event10"]
        or equipment._op(fc, restore) != ("action", "Player_Event", "EventTriggerPlayerEquipDynamicEquipmentFromPouch")
        or restore.next != named["Event19"]
        or equipment._op(fc, finished) != ("action", "Player_Event", "EventWaitCreationFinishedEquipment")
        or finished.next != evfl.NONE
    ):
        raise PatchError(f"Master Sword: changed adult arrival equipment boundaries: {create!r}, {wait!r}, {restore!r}")
    # Era replacement has already validated the incoming selected blade against
    # canonical IsGet and StockNum. Use this movie's native selected-weapon query:
    # no new actor or cross-flow dependency while its screen is white.
    first = len(fc.events)
    for name, yes in (("ArrivalSelected", named["Event9"]), ("RestoreSelected", named["Event10"])):
        fc.events.append(
            evfl.SwitchEvent(
                f"{PREFIX}{name}",
                create.actor,
                create.query,
                [(0, yes), (1, evfl.NONE)],
                {"ArmorName": MASTER, "WeaponSlot": 0},
            )
        )
    create.cases = [(1, first)]
    # Preserve the native animation wait, fade, camera and fork join. Only the
    # sword cleanup (including restore + creation wait) ends early when unarmed.
    wait.next = first + 1
    return _write(doc)


def finale_transform(data: bytes) -> bytes:
    """Refuse before the first safety/temporary-save action, not after the free finale sword."""
    doc, fc, named = _chart(data, "Defeat_Ganon")
    donor = fc.events[named["Event42"]]
    if (
        equipment._op(fc, donor) != ("action", "GameSystemActor", "EventReserveBancChange")
        or donor.params.get("NextBanc") != "CrumblingGanonCastle"
    ):
        raise PatchError(f"Master Sword: changed finale transition donor: {donor!r}")
    retreat = len(fc.events)
    # GanonCastle_Dynamic StartPos GanonCastleEntrance, Hash16478939697790907191;
    # GameBancInfo GanonCastle. Outside the bridge, no quest/arena state is written.
    fc.events.append(
        evfl.ActionEvent(
            f"{PREFIX}RefuseFinale",
            donor.actor,
            donor.action,
            evfl.NONE,
            {
                **donor.params,
                "NextBanc": "GanonCastle",
                "NextStartPos": "GanonCastleEntrance",
                "BootEventName": "",
                "EventStarterName": "",
                "FadePattern": 2,
            },
        )
    )
    for node, absent in (("Event170", "Event43"), ("Event771", "Event727")):
        branch = fc.events[named[node]]
        if (
            equipment._op(fc, branch) != ("query", "GameSystemActor", "EventQueryIsDreamWorld")
            or dict(branch.cases).get(1) != named[absent]
        ):
            raise PatchError(f"Master Sword: changed finale admission {branch!r}")
        guard = _owned(fc, f"{PREFIX}FinaleOwned{node}", MASTER, named[absent], retreat)
        # Dream rematches retain their temporary-inventory native path.
        branch.cases = [(pin, guard if pin == 1 else target) for pin, target in branch.cases]
    return _write(doc)


def force_transform(flow: str, node: str) -> Callable[[bytes], bytes]:
    """Guard a story prop at its existing action index, preserving every continuation."""

    def apply(data: bytes) -> bytes:
        doc, fc, named = _chart(data, flow)
        at = named[node]
        original = fc.events[at]
        if (
            equipment._op(fc, original)
            != ("action", "Player_Event", "EventTriggerEquipmentUserRequestCreateStaticEquipment")
            or original.params.get("EquipmentActorName") != MASTER
        ):
            raise PatchError(f"Master Sword: changed {flow}/{node} force action: {original!r}")
        clone = len(fc.events)
        fc.events.append(replace(original, name=f"{PREFIX}OwnedProp{node}"))
        owned = _owned(fc, f"{PREFIX}PropOwned{node}", MASTER, clone, original.next)
        actor, query = _operation(fc, "Player_Event", "EventQueryPlayerIsEquipWeapon", query=True)
        fc.events[at] = evfl.SwitchEvent(
            original.name,
            actor,
            query,
            [(0, owned), (1, original.next)],
            {"ArmorName": MASTER, "WeaponSlot": 0},
        )
        return _write(doc)

    return apply


def changes(placements: Mapping[str, str]) -> FileChanges:
    if PEDESTAL not in placements:
        raise PatchError("Master Sword: shuffled pedestal has no placement")
    return {
        DOOR: pedestal_transform(item_actors().actor(placements[PEDESTAL])),
        equipment.FLOW: era_transform,
        "Event/EventFlow/Dm_TimeTemple_0070.bfevfl.zs": pose_transform("Dm_TimeTemple_0070", "Event3", "Event13"),
        "Event/EventFlow/Dm_TimeTemple_0088.bfevfl.zs": pose_transform("Dm_TimeTemple_0088", "Event35", "Event29"),
        "Event/EventFlow/Dm_TimeTemple_0085.bfevfl.zs": arrival_transform,
        "Event/EventFlow/Defeat_Ganon.bfevfl.zs": finale_transform,
        "Event/EventFlow/AllSage.bfevfl.zs": force_transform("AllSage", "Event175"),
        "Event/EventFlow/Dm_SY_BancChangeArrive.bfevfl.zs": force_transform("Dm_SY_BancChangeArrive", "Event37"),
    }
