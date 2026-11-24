"""Keep Dampé's first race available until its chest is opened.

Native ownership queries select dialogue, race mode, finish counting and timer
presentation. All use the chest's permanent opened Bool instead; admission still
requires a Hookshot/Longshot in ``dampe_safety``. Result also bypasses the clear
counter for an unopened chest, recovering saves that already ran the second race.
The spawn-history Bool is not a collection flag. No new saved state is introduced.

Native trigger chain and query polarity: plans/rounds/r22-dampe.md.
"""

from copy import deepcopy

from clawshot.formats import evfl
from clawshot.patch.dampe_safety import FLOW
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

CHEST_OPEN = "IsTreasureBoxOpen.16041366920820397198"
SPAWNED = "HaveTalked_Special.MiniGame_DampeRace_HookShot_Event63"
# Only native item-dependent race selectors, never the safety patch's admission gates.
_POUCH = ("Event0", "Event18", "Event61", "Event260", "Event262", "Event442", "Event443", "Event444")
_HISTORY = ("Event98", "Event129", "Event157")


def patch(data: bytes) -> bytes:
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "MiniGame_DampeRace":
        raise PatchError("Dampe first race: expected MiniGame_DampeRace flowchart")
    named = {event.name: i for i, event in enumerate(fc.events)}
    if "ClawshotDampeResult" in named:
        raise PatchError("Dampe first race: already patched")
    game_data = next(i for i, actor in enumerate(fc.actors) if actor.name == "GameDataActor")
    queries = fc.actors[game_data].queries
    read_bool = queries.index("EventQueryIsGameDataBool")
    read_expression = queries.index("EventQueryIsGameDataBoolExp")

    def opened(name: str, actor: str, query: str, params: dict) -> None:
        event = fc.events[named[name]]
        if (
            not isinstance(event, evfl.SwitchEvent)
            or fc.actors[event.actor].name != actor
            or fc.actors[event.actor].queries[event.query] != query
            or event.params != params
        ):
            raise PatchError(f"Dampe first race: unexpected {name}: {event!r}")
        event.actor, event.query = game_data, read_bool
        event.params = {"GameDataName": CHEST_OPEN, "Index": -1}

    for name in _POUCH:
        actor = "Item_Longshot" if name in ("Event18", "Event262") else "Item_Hookshot"
        opened(name, "PouchSystemActor", "EventQueryIsExistInPouch", {"Actor": actor, "Num": 1})
    for name in _HISTORY:
        opened(name, "GameDataActor", "EventQueryCheckIsGet", {"ActorName": "Item_Hookshot"})
    opened("Event277", "GameDataActor", "EventQueryIsGameDataBool", {"GameDataName": SPAWNED, "Index": -1})

    # A save which already ran PlayingSecond retains this mode Bool. Its first-race
    # finish must use the first-race presentation too, without resetting the saved win count.
    first_finish = deepcopy(fc.events[named["Event188"]])
    if (
        not isinstance(first_finish, evfl.ActionEvent)
        or first_finish.actor != game_data
        or fc.actors[game_data].actions[first_finish.action] != "EventTriggerSetGameDataBool"
        or first_finish.params
        != {"GameDataName": "UnderTheGrave_DampeRace_SecondRace_More", "Value": True, "Index": -1}
    ):
        raise PatchError(f"Dampe first race: unexpected mode writer: {first_finish!r}")
    first_finish.name, first_finish.next = "ClawshotDampeFirstFinish", named["Event187"]
    first_finish.params["Value"] = False
    first_finish_index = len(fc.events)
    fc.events.append(first_finish)

    # Re-entering the first race with an early item must not roll a later Forest quest back.
    # Retain the native actions for early/equal steps; native strict-after expressions skip only regressions.
    for name, step in (("Event97", "Step02"), ("Event132", "Step03")):
        index = named[name]
        event = fc.events[index]
        if (
            not isinstance(event, evfl.ActionEvent)
            or fc.actors[event.actor].name != "ChallengeSystemActor"
            or fc.actors[event.actor].actions[event.action] != "EventExecuteProgressChallengeStep"
            or event.params.get("ChallengeName") != "SageOfForest"
            or event.params.get("StepName") != step
        ):
            raise PatchError(f"Dampe first race: unexpected Forest writer {name}: {event!r}")
        writer = deepcopy(event)
        writer.name = f"ClawshotDampe{name}Write"
        continuation = first_finish_index if name == "Event132" else event.next
        writer.next = continuation
        fc.events[index] = evfl.SwitchEvent(
            name,
            game_data,
            read_expression,
            [(0, continuation), (1, len(fc.events))],
            {"GameDataName": f"SageOfForest_IsAfter_{step}_Exp"},
        )
        fc.events.append(writer)

    result = fc.entry_point("Result")
    if result.main_event != named["Event275"]:
        raise PatchError(f"Dampe first race: unexpected Result entry: {result!r}")
    gate = evfl.SwitchEvent(
        "ClawshotDampeResult",
        game_data,
        read_bool,
        [(0, result.main_event), (1, named["Event277"])],
        {"GameDataName": CHEST_OPEN, "Index": -1},
    )
    result.main_event = len(fc.events)
    fc.events.append(gate)
    output = evfl.write(document)
    if evfl.read(output) != document:
        raise PatchError("Dampe first race: read-back differs")
    return output


def changes() -> FileChanges:
    return {FLOW: patch}
