"""Kaepora skip, his later child scenes: his spoken lines go, every other action of the scene stays.

The ``kaepora`` fast start marks his first Hyrule Field talk and his Lost Woods talk as played. His other child
scenes still start natively, and they keep their state by still playing: only the owl's non-choice ``EventTalk``
actions are left out (whole-dump audit, plans/rounds/r18-story.md). None of these scenes writes the clock inputs
(``HyruleField_ArriveEntrance`` is written only by the first Field talk; ``HavePlayedEvent.Dm_HrlField_0020`` is
Impa's send-off), a quest step, an item or a map visit flag. The castle arrival's location banner (the
``IsVisitLocation.HyruleCastle`` map visit), the owl-met flags and each scene's own played history stay native.

- Demos started by placement and logic, not by a flow: ``Dm_HrlCastle_0000`` (first child arrival at the castle,
  Market ``FieldAndDungeonEntranceEventRequestActor``), ``Dm_HrlField_0030`` (Kakariko approach before
  ``DoorOfTime`` Step01), ``Dm_HrlField_0040`` (Gerudo Valley approach), ``Dm_HrlField_0050`` (Lake Hylia approach),
  ``Dm_LostWood_0000`` (Lost Woods after Zelda's courtyard), ``Dm_ZoraRiver_0000`` (``Get_StoneOfWater``'s owl talk)
  and ``Dm_ZoraRiver_0005``: every owl line goes.
- Talk NPCs ``Npc_Kaepora_DeathMountainTrail`` and ``Npc_Kaepora_LakeHylia``: each yes/no flight offer stays, as
  the flow's own shorter offer; the flights (``Dm_DeathMtTrail_0030`` to Kakariko, the ``DMT Owl Flight`` logic
  exit, and ``Dm_LakeHrl_0010``/``_0011``) and every flag write stay native. The mask and Lens of Truth reactions
  (spoken through ``Npc_EventStarter``) stay native.

An omitted line's predecessors continue at its native successor; a fork branch or switch case that held only
omitted lines is dropped, so it ends as it did after the line (native flows hold one-branch forks and switches
without cases). The lines are removed from the event list, as native flows hold no unreachable events. Every
other event reachable from each entry, with its parameters and its order on each path, is unchanged.
"""

from dataclasses import dataclass
from functools import partial

from clawshot.formats import evfl
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

FLOW_DIR = "Event/EventFlow"
TALK = "EventTalk"
MESSAGE = "MessageId"
CHOICES = "ChoiceNumber"


@dataclass(frozen=True)
class OwlScene:
    flow: str
    speaker: str
    """The owl's actor in this flow; only its ``EventTalk`` actions are classified."""
    lines: tuple[str, ...]
    """Native event names of the owl's non-choice talks, all omitted."""
    offers: tuple[str, ...] = ()
    """Native event names of the owl's choice talks (flight offers), all kept."""
    shorter: tuple[tuple[str, str], ...] = ()
    """(offer, donor offer): the offer takes the donor's message, a shorter prompt with the same choices."""

    @property
    def path(self) -> str:
        return f"{FLOW_DIR}/{self.flow}.bfevfl.zs"


_OWL = "Npc_Kaepora"
_DMT = "Npc_Kaepora_DeathMountainTrail"
_LAKE = "Npc_Kaepora_LakeHylia"


def _scene(flow: str, speaker: str, lines: str, offers: str = "", shorter: tuple[tuple[str, str], ...] = ()):
    return OwlScene(flow, speaker, tuple(lines.split()), tuple(offers.split()), shorter)


SCENES: tuple[OwlScene, ...] = (
    _scene("Dm_HrlCastle_0000", _OWL, "Event11 Event12 Event15 Event33 Event34"),
    _scene("Dm_HrlField_0030", _OWL, "Event92 Event66 Event31 Event41 Event16 Event57"),
    _scene(
        "Dm_HrlField_0040",
        _OWL,
        "Event65 Event38 Event18 Event32 Event22 Event24 Event26 Event36 Event67 Event69 Event80",
    ),
    _scene(
        "Dm_HrlField_0050",
        _OWL,
        "Event31 Event30 Event56 Event23 Event18 Event28 Event24 Event39 Event47 Event69 Event71 Event96",
    ),
    _scene(
        "Dm_LostWood_0000",
        _OWL,
        "Event151 Event152 Event153 Event154 Event155 Event156 Event166 Event200 Event201 Event202 Event203 Event210"
        " Event1 Event2",
    ),
    _scene("Dm_ZoraRiver_0000", _OWL, "Event4 Event5 Event7 Event19 Event21 Event59"),
    _scene("Dm_ZoraRiver_0005", _OWL, "Event11 Event16 Event28 Event25 Event10"),
    # The first flight offer (Talk_01) takes the repeat offer's prompt (Talk_04); both ask the same yes/no.
    _scene(
        _DMT,
        _DMT,
        "Event1 Event10 Event12 Event15 Event16 Event29 Event30 Event31 Event32 Event40 Event43 Event44 Event46",
        "Event2 Event13",
        (("Event2", "Event13"),),
    ),
    # The offer after a flight (_0005) takes the first offer's prompt (_0008).
    _scene(
        _LAKE,
        _LAKE,
        "Event4 Event5 Event6 Event7 Event9 Event11 Event16 Event17 Event33 Event38",
        "Event8 Event13",
        (("Event13", "Event8"),),
    ),
)


def _successors(event: evfl.Event) -> list[int]:
    """Every event index ``event`` may continue to, a fork's join included."""
    if isinstance(event, evfl.SwitchEvent | evfl.SubFlowSwitchEvent):
        targets = [target for _, target in event.cases]
    elif isinstance(event, evfl.ForkEvent):
        targets = [*event.forks, event.join]
    elif isinstance(event, evfl.ActionEvent | evfl.JoinEvent | evfl.SubFlowEvent):
        targets = [event.next]
    else:
        targets = []
    return [target for target in targets if target != evfl.NONE]


def reachable(fc: evfl.Flowchart, start: int) -> set[int]:
    """The event indices an entry starting at ``start`` can run."""
    seen: set[int] = set()
    stack = [start]
    while stack:
        index = stack.pop()
        if index == evfl.NONE or index in seen:
            continue
        seen.add(index)
        stack.extend(_successors(fc.events[index]))
    return seen


def _owl_talks(fc: evfl.Flowchart, speaker: str) -> dict[str, int]:
    return {
        event.name: index
        for index, event in enumerate(fc.events)
        if isinstance(event, evfl.ActionEvent)
        and fc.actors[event.actor].name == speaker
        and not fc.actors[event.actor].secondary_name
        and fc.actors[event.actor].actions[event.action] == TALK
    }


def _reachable_names(fc: evfl.Flowchart) -> dict[str, set[str]]:
    return {entry.name: {fc.events[i].name for i in reachable(fc, entry.main_event)} for entry in fc.entry_points}


def omit_lines(data: bytes, scene: OwlScene) -> bytes:
    """``scene``'s flow (decompressed) without the owl's non-choice lines, its offers shortened as listed."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != scene.flow:
        raise PatchError(f"owl skip: {scene.path} holds no {scene.flow} flowchart")
    talks = _owl_talks(fc, scene.speaker)
    classified = {*scene.lines, *scene.offers}
    if set(talks) != classified or len(classified) != len(scene.lines) + len(scene.offers):
        raise PatchError(f"owl skip: {scene.flow}: owl talks {sorted(talks)}, classified {sorted(classified)}")
    choices = {name: (fc.events[index].params or {}).get(CHOICES) for name, index in talks.items()}
    if [name for name in scene.lines if choices[name] != 0] or [name for name in scene.offers if not choices[name]]:
        raise PatchError(f"owl skip: {scene.flow}: changed native talk choices {choices}")
    before = _reachable_names(fc)
    if unreached := sorted(classified - set().union(*before.values())):
        raise PatchError(f"owl skip: {scene.flow}: talks {unreached} are unreachable natively")

    omitted = {talks[name] for name in scene.lines}

    def resolve(index: int) -> int:
        while index in omitted:
            index = fc.events[index].next
        return index

    kept = [index for index in range(len(fc.events)) if index not in omitted]
    renumber = {old: new for new, old in enumerate(kept)}

    def target(index: int) -> int:
        index = resolve(index)
        return evfl.NONE if index == evfl.NONE else renumber[index]

    for index in kept:
        event = fc.events[index]
        if isinstance(event, evfl.ActionEvent | evfl.JoinEvent | evfl.SubFlowEvent):
            event.next = target(event.next)
        elif isinstance(event, evfl.SwitchEvent | evfl.SubFlowSwitchEvent):
            # A case holding only omitted lines ended after them: without its case the value ends here.
            cases = [(value, target(case)) for value, case in event.cases]
            event.cases = [(value, case) for value, case in cases if case != evfl.NONE]
        elif isinstance(event, evfl.ForkEvent):
            forks = [new for new in map(target, event.forks) if new != evfl.NONE]
            if not forks:
                raise PatchError(f"owl skip: {scene.flow}/{event.name}: every fork branch is an owl line")
            event.forks, event.join = forks, renumber[event.join]
    for entry in fc.entry_points:
        main = target(entry.main_event)
        if main == evfl.NONE or any(index in omitted for index in entry.sub_flow_events):
            raise PatchError(f"owl skip: {scene.flow}: entry {entry.name} would start empty or lose a sub flow")
        entry.main_event = main
        entry.sub_flow_events = [renumber[index] for index in entry.sub_flow_events]
    fc.events = [fc.events[index] for index in kept]

    offers = {event.name: event for event in fc.events if event.name in scene.offers}
    for name, donor in scene.shorter:
        offer, source = offers[name], offers[donor]
        mine = {k: v for k, v in offer.params.items() if k != MESSAGE}
        theirs = {k: v for k, v in source.params.items() if k != MESSAGE}
        if mine != theirs or offer.params[MESSAGE] == source.params[MESSAGE]:
            raise PatchError(f"owl skip: {scene.flow}: offer {name} cannot take {donor}'s prompt: {offer!r} {source!r}")
        offer.params = {**offer.params, MESSAGE: source.params[MESSAGE]}

    after = _reachable_names(fc)
    expected = {entry: names - set(scene.lines) for entry, names in before.items()}
    everything = set().union(*(reachable(fc, entry.main_event) for entry in fc.entry_points))
    if after != expected or everything != set(range(len(fc.events))):
        raise PatchError(f"owl skip: {scene.flow}: reachable events changed beyond the owl lines: {after} {expected}")
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError(f"owl skip: {scene.path} does not read back as the edited flow")
    return result


def changes() -> FileChanges:
    """The Kaepora skip's flow transforms, one per scene; compose with the ``kaepora`` initial values."""
    return {scene.path: partial(omit_lines, scene=scene) for scene in SCENES}
