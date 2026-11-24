"""Refuse races without an escape tool, explain why, and return Link to the surface.

The descent is one-way. Check after InitTalk, before race/talk state or positioning;
keep Ready/Start guards as backup. Native dialogue precedes the existing safe return.
No timer, race step, prize or inventory write is performed on a refusal.
"""

from copy import deepcopy

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Event/EventFlow/MiniGame_DampeRace.bfevfl.zs"
SURFACE = "GraveYard_KakarikoSide"
ENTRIES = ("MiniGame_DampeRace_Ready", "MiniGame_DampeRace_Start")
REFUSAL_MESSAGE = "EventFlowMsg/Npc_Hylia_Dampe_002:ClawshotNoEscapeTool"


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
    named = {event.name: i for i, event in enumerate(fc.events)}
    talk = by_name["Event109"]
    if (
        not isinstance(talk, evfl.SubFlowEvent)
        or (talk.flowchart, talk.entry_point) != ("InitTalk", "InitTalk")
        or talk.next != named["Event59"]
    ):
        raise PatchError(f"Dampe safety: unexpected talk initialization {talk!r}")
    refusal = deepcopy(by_name["Event3"])
    if (
        not isinstance(refusal, evfl.ActionEvent)
        or fc.actors[refusal.actor].actions[refusal.action] != "EventTalk"
        or refusal.params.get("MessageId") != "EventFlowMsg/Npc_Hylia_Dampe_002:Talk_01"
        or refusal.params.get("ChoiceNumber") != 0
    ):
        raise PatchError(f"Dampe safety: unexpected dialogue donor {refusal!r}")
    # Native pouch queries return 0 when held and 1 when absent.
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
    refusal.name, refusal.next = "ClawshotDampeNoToolTalk", tail + 1
    refusal.params["MessageId"] = REFUSAL_MESSAGE
    fade_out.name, fade_out.next = "ClawshotDampeSurfaceFadeOut", tail + 2
    warp.name, warp.next = "ClawshotDampeSurfaceWarp", tail + 3
    fade_in.name, fade_in.next = "ClawshotDampeSurfaceFadeIn", evfl.NONE
    for action in (refusal, fade_out, warp, fade_in):
        action.params = {**action.params, "IsWaitEnd": True}
    warp.params["InstanceName"] = SURFACE
    fc.events.extend([refusal, fade_out, warp, fade_in])

    def admission(name: str, original: int) -> int:
        gate = len(fc.events)
        fc.events.extend(
            [
                evfl.SwitchEvent(
                    f"ClawshotDampeHookshot{name}",
                    pouch,
                    query,
                    [(0, original), (1, gate + 1)],
                    {"Actor": "Item_Hookshot", "Num": 1},
                ),
                evfl.SwitchEvent(
                    f"ClawshotDampeLongshot{name}",
                    pouch,
                    query,
                    [(0, original), (1, tail)],
                    {"Actor": "Item_Longshot", "Num": 1},
                ),
            ]
        )
        return gate

    # Refuse before reset, offer-history writes, either acceptance speech or positioning.
    # A later visit with a naturally acquired tool sees the untouched native race state.
    talk.next = admission("Talk", talk.next)
    for name in ENTRIES:
        entry = fc.entry_point(name)
        original = entry.main_event
        if not isinstance(fc.events[original], evfl.ActionEvent):
            raise PatchError(f"Dampe safety: unexpected {name} entry {fc.events[original]!r}")
        entry.main_event = admission(name, original)
    result = evfl.write(file)
    if evfl.read(result) != file:
        raise PatchError("Dampe safety: read-back differs")
    return result


def changes() -> FileChanges:
    return {FLOW: patch}
