"""Require an escape tool before either race start, returning refusals to the surface.

The descent itself is one-way. Merely refusing to open the starting shutter would
leave Link in the lower lobby. Reuse native fade/anchor-warp actions to the existing
surface StartPos instead; no timer, race step, prize or inventory write is performed.
"""

from copy import deepcopy

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Event/EventFlow/MiniGame_DampeRace.bfevfl.zs"
SURFACE = "GraveYard_KakarikoSide"
ENTRIES = ("MiniGame_DampeRace_Ready", "MiniGame_DampeRace_Start")


def patch(data: bytes) -> bytes:
    file = evfl.read(data)
    fc = file.flowchart
    if fc is None or fc.name != "MiniGame_DampeRace":
        raise PatchError("Dampe safety: expected MiniGame_DampeRace flowchart")
    by_name = {event.name: event for event in fc.events}
    if "ClawshotDampeSurfaceFadeOut" in by_name:
        raise PatchError("Dampe safety: already patched")
    pouch = next(i for i, actor in enumerate(fc.actors) if actor.name == "PouchSystemActor")
    query = fc.actors[pouch].queries.index("EventQueryIsExistInPouch")
    # These donors are native race reset actions, not a new transition protocol.
    fade_out = deepcopy(by_name["Event92"])
    warp = deepcopy(by_name["Event90"])
    fade_in = deepcopy(
        next(
            event
            for event in fc.events
            if isinstance(event, evfl.ActionEvent)
            and fc.actors[event.actor].actions[event.action] == "EventEventFadeIn"
        )
    )
    if not isinstance(fade_out, evfl.ActionEvent) or not isinstance(warp, evfl.ActionEvent):
        raise PatchError("Dampe safety: missing native reset actions")
    if fc.actors[fade_out.actor].actions[fade_out.action] != "EventEventFadeOut":
        raise PatchError(f"Dampe safety: unexpected fade donor {fade_out!r}")
    if fc.actors[warp.actor].actions[warp.action] != "EventPlayerWarpToStarterLinkAnchor":
        raise PatchError(f"Dampe safety: unexpected warp donor {warp!r}")
    if warp.params.get("ActorName") != "StartPos" or warp.params.get("InstanceName") != "4":
        raise PatchError(f"Dampe safety: changed native race reset anchor {warp.params!r}")
    tail = len(fc.events)
    fade_out.name, fade_out.next = "ClawshotDampeSurfaceFadeOut", tail + 1
    warp.name, warp.next = "ClawshotDampeSurfaceWarp", tail + 2
    fade_in.name, fade_in.next = "ClawshotDampeSurfaceFadeIn", evfl.NONE
    for action in (fade_out, warp, fade_in):
        action.params = {**action.params, "IsWaitEnd": True}
    warp.params["InstanceName"] = SURFACE
    fc.events.extend([fade_out, warp, fade_in])
    for name in ENTRIES:
        entry = fc.entry_point(name)
        original = entry.main_event
        if not isinstance(fc.events[original], evfl.ActionEvent):
            raise PatchError(f"Dampe safety: unexpected {name} entry {fc.events[original]!r}")
        gate = len(fc.events)
        fc.events.extend(
            [
                evfl.SwitchEvent(
                    f"ClawshotDampeHookshot{name}",
                    pouch,
                    query,
                    [(0, gate + 1), (1, original)],
                    {"Actor": "Item_Hookshot", "Num": 1},
                ),
                evfl.SwitchEvent(
                    f"ClawshotDampeLongshot{name}",
                    pouch,
                    query,
                    [(0, tail), (1, original)],
                    {"Actor": "Item_Longshot", "Num": 1},
                ),
            ]
        )
        entry.main_event = gate
    result = evfl.write(file)
    if evfl.read(result) != file:
        raise PatchError("Dampe safety: read-back differs")
    return result


def changes() -> FileChanges:
    return {FLOW: patch}
