"""Never wait for unplayable shoulder notes when a song lesson has no ocarina.

Only the shared interactive follow-example fork is bypassed without an ocarina.
Demonstration, automatic performance, song grants and caller story continuations remain native.
Evidence: plans/rounds/r18-story.md; build e0f3ccfa.
"""

from clawshot.census.gifts import reachable
from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW = "Event/EventFlow/Dm_SY_Ocarina.bfevfl.zs"


def patch(data: bytes) -> bytes:
    file = evfl.read(data)
    fc = file.flowchart
    if fc is None or fc.name != "Dm_SY_Ocarina":
        raise PatchError("song learning: expected Dm_SY_Ocarina flowchart")
    entry = fc.entry_point("LearningOcarinaFollowExample")
    setup = fc.events[entry.main_event]
    if not isinstance(setup, evfl.ActionEvent):
        raise PatchError(f"song learning: unexpected performer setup {setup!r}")
    if fc.actors[setup.actor].actions[setup.action] != "EventTriggerSetOwnAsInstrumentPlayer":
        raise PatchError(f"song learning: unexpected performer action {setup!r}")
    fork_index = setup.next
    fork = fc.events[fork_index]
    if not isinstance(fork, evfl.ForkEvent) or not isinstance(fc.events[fork.join], evfl.JoinEvent):
        raise PatchError(f"song learning: unexpected follow-example fork {fork!r}")
    if fc.events[fork.join].next != evfl.NONE:
        raise PatchError(f"song learning: unexpected follow-example return {fc.events[fork.join]!r}")
    # Do not bypass only the input leaf: its parallel free-playing pose would
    # still be waiting for completion. No branch of this fork runs without an instrument.
    presentation = {
        "EventWaitOcarinaInputForLearning",
        "EventTalk",
        "EventTriggerPlayerRequestLookAtTheFrontLock",
        "EventPlayerPlayOcarinaFree",
    }
    for index in reachable(fc, fork_index):
        event = fc.events[index]
        if isinstance(event, evfl.ActionEvent):
            if fc.actors[event.actor].actions[event.action] not in presentation:
                raise PatchError(f"song learning: unsafe effect inside interactive fork {event!r}")
        elif not isinstance(event, evfl.ForkEvent | evfl.JoinEvent):
            raise PatchError(f"song learning: unexpected interactive branch {event!r}")
    game_data = next(i for i, actor in enumerate(fc.actors) if actor.name == "GameDataActor")
    query = fc.actors[game_data].queries.index("EventQueryIsGameDataBool")
    tail = len(fc.events)
    fc.events.extend(
        [
            evfl.SwitchEvent(
                "ClawshotFairyOcarinaLearning",
                game_data,
                query,
                [(0, tail + 1), (1, fork_index)],
                {"GameDataName": "IsGet.Item_Ocarina_Fairy", "Index": -1},
            ),
            evfl.SwitchEvent(
                "ClawshotTimeOcarinaLearning",
                game_data,
                query,
                [(0, fork.join), (1, fork_index)],
                {"GameDataName": "IsGet.Item_Ocarina_Time", "Index": -1},
            ),
        ]
    )
    setup.next = tail
    result = evfl.write(file)
    if evfl.read(result) != file:
        raise PatchError("song learning: read-back differs")
    return result


def changes() -> FileChanges:
    return {FLOW: patch}
