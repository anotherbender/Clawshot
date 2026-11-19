"""Optional native skip-button regions around speech, never around story state.

The native Great Fairy and Water Temple flows use SpecialEventActionType 3/4
(SkipAcceptStart/SkipEnd). Here each region contains only a linear chain of
non-choice EventTalk actions. Grants, writes, choices, cuts and encounters remain
outside it. This deliberately does not make a whole encounter disappear.
"""

from copy import deepcopy
from functools import partial

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

# Effective supported-build paths: Talon's active flow is the version-110 copy.
FLOWS = {
    "Dm_HrlCastle_0020": "Dm_HrlCastle_0020.110",
    "Dm_HrlCastle_0035": "Dm_HrlCastle_0035",
    "Dm_HrlCastle_0050": "Dm_HrlCastle_0050",
    "Dm_MelodyGet_Zelda": "Dm_MelodyGet_Zelda",
    "Dm_HrlField_0020": "Dm_HrlField_0020",
}
TALK_ACTIONS = frozenset({"EventTalk", "EventTalkIgnoreSameTalkAS"})
START = "EventTriggerSkipAcceptStart"
END = "EventTriggerSkipEnd"


def patch(data: bytes, *, flow: str) -> bytes:
    file = evfl.read(data)
    fc = file.flowchart
    if fc is None or fc.name != flow:
        raise PatchError(f"story dialogue: expected {flow} flowchart")
    talks = {
        i
        for i, event in enumerate(fc.events)
        if isinstance(event, evfl.ActionEvent)
        and fc.actors[event.actor].actions[event.action] in TALK_ACTIONS
        and (event.params or {}).get("ChoiceNumber") == 0
    }
    if not talks:
        raise PatchError(f"story dialogue: {flow} has no non-choice speech")
    if any(event.name.startswith("ClawshotSpeech") for event in fc.events):
        raise PatchError(f"story dialogue: {flow} is already patched")
    system = next(i for i, actor in enumerate(fc.actors) if actor.name == "EventSystemActor")
    actor = fc.actors[system]
    for action in (START, END):
        if action not in actor.actions:
            actor.actions.append(action)
    start_action, end_action = actor.actions.index(START), actor.actions.index(END)
    # Only merge a following speech node if no other path can enter it. The
    # skip region cannot swallow a choice, a side effect or a subflow boundary.
    incoming = {i: 0 for i in talks}
    for event in fc.events:
        targets = [getattr(event, "next", evfl.NONE), *[target for _, target in getattr(event, "cases", ())]]
        if isinstance(event, evfl.ForkEvent):
            targets += [*event.forks, event.join]
        for target in targets:
            if target in incoming:
                incoming[target] += 1
    for entry in fc.entry_points:
        if entry.main_event in incoming:
            incoming[entry.main_event] += 1
    remaining = set(talks)
    for first in sorted(talks):
        if first not in remaining:
            continue
        chain = [first]
        remaining.remove(first)
        while (target := fc.events[chain[-1]].next) in remaining and incoming[target] == 1:
            chain.append(target)
            remaining.remove(target)
        original = deepcopy(fc.events[first])
        final = fc.events[chain[-1]]
        continuation = final.next
        tail = len(fc.events)
        original.name = f"ClawshotSpeech{first}Talk"
        original.next = tail + 1 if len(chain) == 1 else original.next
        fc.events.extend(
            [
                original,
                evfl.ActionEvent(
                    f"ClawshotSpeech{first}End",
                    system,
                    end_action,
                    continuation,
                    {"SpecialEventActionType": 4, "FadeInType": 0},
                ),
            ]
        )
        if len(chain) > 1:
            final.next = tail + 1
        fc.events[first] = evfl.ActionEvent(
            fc.events[first].name,
            system,
            start_action,
            tail,
            {"SpecialEventActionType": 3},
        )
    result = evfl.write(file)
    if evfl.read(result) != file:
        raise PatchError(f"story dialogue: {flow} read-back differs")
    return result


def changes(*, enabled: bool) -> FileChanges:
    if not enabled:
        return {}
    return {f"Event/EventFlow/{path}.bfevfl.zs": partial(patch, flow=flow) for flow, path in FLOWS.items()}
