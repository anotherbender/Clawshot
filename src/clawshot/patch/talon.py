"""Talon's Cucco game stops showing Lon Lon milk and a free bottle as its first prize once that prize is shuffled.

The milk on his table is ``Item_OrnamentalBottle_Milk``: the only ``Item_*`` actor any placement file places and
the only ``Item_Ornamental*`` actor pack; no audited generic table display was found. A moved prize removes that
prop and the beat that turns everyone towards it (Talon's ``Talk_30`` between the two ``SuggestCamera`` calls, and
``Talk_30`` again in the rules recap), whose line praises the milk and its free bottle. The three remaining lines
that name the first prize say neutral English in every language (D26). The repeat prize, the milk sale and their
lines stay native: those still give milk. No item, flag, gate or quest step changes. Evidence: round 22 scenes
(``Minigame_FindOutCucco`` traced from every entry point).
"""

from collections.abc import Mapping
from itertools import takewhile
from pathlib import Path

from clawshot.census.gifts import _successors, reachable
from clawshot.formats import byml, evfl, msbt, sarc
from clawshot.patch import text
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

CHECK = "LLR Talons Chickens"
VANILLA = "Bottle with Milk"  # the world's vanilla item for CHECK; any other placement is a moved prize

FLOW = "Minigame_FindOutCucco"
FLOW_PATH = f"Event/EventFlow/{FLOW}.bfevfl.zs"
TALON = "Npc_Hylia_Talon_Child"
MESSAGES = f"EventFlowMsg/{TALON}.msbt"

BANC_PATH = "Banc/HyruleField/HyruleField_Child_Static.bcett.byml.zs"
TALON_HASH = 13992935491369868918
PROP = "Item_OrnamentalBottle_Milk"
PROP_NAME = "LonLon_Milk"
PROP_HASH = 11457557478267217151

# The prop beat: Event263 (recent talk?) -> Event340 look at the prop -> Event125 Talk_30 -> Event341 look back ->
# Event68 the game's start; the recap: Event315 (cleared?) -> Event413 Talk_30 -> Event325 the start's own check.
RECENT, LOOK, SHOWCASE, LOOK_BACK, START = "Event263", "Event340", "Event125", "Event341", "Event68"
RECAP_GATE, RECAP = "Event315", "Event413"
SKIPPED = (LOOK, SHOWCASE, LOOK_BACK, RECAP)
SHOWCASE_LABEL = "Talk_30"
CLEAR_FLAG = "IsClear_Minigame_FindOutCucco"
# The native milk sale Talk_28's replacement describes: Event58 (rupees?) -> Event61 (empty bottle?) -> Event205
# pays -> Event64 Talk_12 -> Event244 fills the bottle with milk.
SALE = ("Event58", "Event61", "Event205", "Event64", "Event244")
SALE_PRICE = 30
MILK = "Item_Bottle_Milk"

# Each rewritten or skipped label and the only events of the flow that say it; no other flow names them.
USERS = {
    "Talk_29": ("Event124", "Event411"),  # the rules, before and after a clear
    "Talk_09_2": ("Event206",),  # the first prize's hand-over
    "Talk_28": ("Event43",),  # right after the first prize
    SHOWCASE_LABEL: (SHOWCASE, RECAP),
}
NAMED = (RECENT, LOOK, SHOWCASE, LOOK_BACK, START, RECAP_GATE, RECAP, *SALE, *(n for v in USERS.values() for n in v))
WIDTH, ROWS = 40, 2  # conservative NPC envelope, as the Skulltula sons' lines
LINES = {
    "Talk_29": "Find 'em all, and I'll give ya a prize!",
    "Talk_09_2": "It's all yours! Cheers!",
    "Talk_28": f"Bring me an empty bottle, and I'll fill it with Lon Lon milk for {SALE_PRICE} rupees.",
}


def moved(placements: Mapping[str, str]) -> bool:
    """Whether the seed gives another item than the native milk at Talon's Cucco game."""
    return placements.get(CHECK, VANILLA) != VANILLA


def _fail(what: str) -> PatchError:
    return PatchError(f"Talon's Cucco game: changed native {what}")


def _talk(fc: evfl.Flowchart, event: evfl.Event) -> str | None:
    """The Talon label an EventTalk says, else None."""
    if not isinstance(event, evfl.ActionEvent):
        return None
    actor = fc.actors[event.actor]
    message = (event.params or {}).get("MessageId")
    prefix = f"EventFlowMsg/{TALON}:"
    if actor.name != TALON or actor.actions[event.action] != "EventTalk" or not isinstance(message, str):
        return None
    return message.removeprefix(prefix) if message.startswith(prefix) else None


def _call(event: evfl.Event, flowchart: str, entry: str) -> bool:
    return isinstance(event, evfl.SubFlowEvent) and (event.flowchart, event.entry_point) == (flowchart, entry)


def _query(fc: evfl.Flowchart, event: evfl.Event, actor: str, query: str) -> bool:
    return (
        isinstance(event, evfl.SwitchEvent)
        and fc.actors[event.actor].name == actor
        and fc.actors[event.actor].queries[event.query] == query
    )


def _check_beat(fc: evfl.Flowchart, at: Mapping[str, int]) -> None:
    look, showcase, back, start = (fc.events[at[name]] for name in (LOOK, SHOWCASE, LOOK_BACK, START))
    recent, gate, recap = (fc.events[at[name]] for name in (RECENT, RECAP_GATE, RECAP))
    target = (look.params or {}) if isinstance(look, evfl.SubFlowEvent) else {}
    if (
        not _call(look, "NpcCommon", "SuggestCamera_Start_NPCLookOnly")
        or (target.get("TurnTargetActorName"), target.get("TurnTargetInstanceName")) != (PROP, PROP_NAME)
        or look.next != at[SHOWCASE]
        or _talk(fc, showcase) != SHOWCASE_LABEL
        or showcase.next != at[LOOK_BACK]
        or not _call(back, "NpcCommon", "SuggestCamera_Reset_NPCLookOnly")
        or back.next != at[START]
        or not _call(start, "", "Minigame_FindOutCucco_Start")
        or not _query(fc, recent, TALON, "EventQueryIsOnRecentTalkFlag")
        or recent.cases != [(0, at[START]), (1, at[LOOK])]
    ):
        raise _fail(f"prop beat: {recent!r}, {look!r}, {showcase!r}, {back!r}, {start!r}")
    if (
        not _query(fc, gate, "GameDataActor", "EventQueryIsGameDataBool")
        or gate.params != {"GameDataName": CLEAR_FLAG, "Index": -1}
        or _talk(fc, recap) != SHOWCASE_LABEL
        or recap.next == evfl.NONE
        or gate.cases != [(0, recap.next), (1, at[RECAP])]
        or not _query(fc, fc.events[recap.next], "GameDataActor", "EventQueryIsGameDataBool")
    ):
        raise _fail(f"rules recap: {gate!r}, {recap!r}")
    for name in SKIPPED:
        inbound = [event.name for event in fc.events if at[name] in _successors(event)]
        expected = {LOOK: [RECENT], SHOWCASE: [LOOK], LOOK_BACK: [SHOWCASE], RECAP: [RECAP_GATE]}[name]
        if inbound != expected or any(entry.main_event == at[name] for entry in fc.entry_points):
            raise _fail(f"way into {name}: {inbound}")


def _check_sale(fc: evfl.Flowchart, at: Mapping[str, int]) -> None:
    has, empty, pay, thanks, fill = (fc.events[at[name]] for name in SALE)
    if (
        not _query(fc, has, "PouchSystemActor", "EventQueryHasRuppe")
        or has.params != {"Value": SALE_PRICE}
        or dict(has.cases).get(0) != at[SALE[1]]
        or not _query(fc, empty, "PouchSystemActor", "EventQueryIsAnyBottleEmpty")
        or dict(empty.cases).get(0) != at[SALE[2]]
        or not _call(pay, "NpcCommon", "NpcCommon_HandOver_PlayerToNpc")
        or (pay.params or {}).get("PaidRupee") != -SALE_PRICE
        or pay.next != at[SALE[3]]
        or _talk(fc, thanks) != "Talk_12"
        or thanks.next != at[SALE[4]]
        or not _call(fill, "Dm_SY_GetInEvent", "GetInEventInBottle")
        or (fill.params or {}).get("ActorName") != MILK
    ):
        raise _fail(f"milk sale: {has!r}, {pay!r}, {fill!r}")


def _check_lines(fc: evfl.Flowchart) -> None:
    users: dict[str, list[str]] = {label: [] for label in USERS}
    for event in fc.events:
        if (label := _talk(fc, event)) in users:
            users[label].append(event.name)
    if any(sorted(users[label]) != sorted(names) for label, names in USERS.items()):
        raise _fail(f"prize lines: {users}")
    naming = [
        event.name
        for event in fc.events
        if any(value in (PROP, PROP_NAME) for value in (getattr(event, "params", None) or {}).values())
    ]
    if naming != [LOOK]:
        raise _fail(f"prop references: {naming}")


def patch_flow(data: bytes) -> bytes:
    """Go from Event263 straight to the game's start and from Event315 straight to the start's check, so neither
    the look at the removed prop nor ``Talk_30`` runs; every other event, entry and registration stays."""
    file = evfl.read(data)
    fc = file.flowchart
    if fc is None or fc.name != FLOW:
        raise PatchError(f"Talon's Cucco game: expected the {FLOW} flowchart")
    at = {event.name: i for i, event in enumerate(fc.events)}
    if missing := sorted(set(NAMED) - at.keys()):
        raise _fail(f"events: {missing} missing")
    _check_beat(fc, at)
    _check_sale(fc, at)
    _check_lines(fc)
    recent, gate, recap = (fc.events[at[name]] for name in (RECENT, RECAP_GATE, RECAP))
    recent.cases = [(0, at[START]), (1, at[START])]
    gate.cases = [(0, recap.next), (1, recap.next)]
    live = set().union(*(reachable(fc, entry.main_event) for entry in fc.entry_points))
    if shown := sorted(fc.events[i].name for i in live if fc.events[i].name in SKIPPED):
        raise PatchError(f"Talon's Cucco game: still reachable after the patch: {shown}")
    result = evfl.write(file)
    if evfl.read(result) != file:
        raise PatchError("Talon's Cucco game: the written flow does not read back as the changed tree")
    return result


def _mentions(node: object, value: int) -> bool:
    if isinstance(node, dict):
        return any(_mentions(v, value) for v in node.values())
    if isinstance(node, list):
        return any(_mentions(v, value) for v in node)
    return isinstance(node, int) and not isinstance(node, bool) and node == value


def patch_banc(data: bytes) -> bytes:
    """Remove the table's milk prop and Talon's reference to it, as shop shelves drop a quantity board."""
    document = byml.load(data)
    root = document.root
    actors = root.get("Actors") if isinstance(root, dict) else None
    if not isinstance(actors, list):
        raise PatchError(f"{BANC_PATH} has no Actors list")
    props = [a for a in actors if isinstance(a, dict) and a.get("Hash") == PROP_HASH]
    talons = [a for a in actors if isinstance(a, dict) and a.get("Hash") == TALON_HASH]
    if (
        len(props) != 1
        or (props[0].get("Gyaml"), props[0].get("Name")) != (PROP, PROP_NAME)
        or "Presence" in props[0]
        or props[0].get("Links")
    ):
        raise _fail(f"table prop {PROP_HASH}: {props!r}")
    links = talons[0].get("Links", []) if len(talons) == 1 and talons[0].get("Gyaml") == TALON else None
    to_prop = [link for link in links or [] if link.get("Dst") == PROP_HASH]
    shape = [(link.get("Gyaml"), link.get("Name"), link.get("Src")) for link in to_prop]
    if links is None or shape != [("Reference", "Reference", TALON_HASH)]:
        raise _fail(f"Talon {TALON_HASH} reference to the prop: {talons!r}")
    root["Actors"] = [a for a in actors if a is not props[0]]
    talons[0]["Links"] = [link for link in links if link is not to_prop[0]]
    if _mentions(root, PROP_HASH):
        raise _fail(f"references to the prop {PROP_HASH} outside Talon's links")
    result = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(result))) is not None:
        raise PatchError(f"{BANC_PATH}: the written file does not read back as the changed tree: {difference}")
    return result


def _lead(original: list[msbt.Part]) -> list[msbt.Part]:
    """The line's opening tags (voice, expression) without a ruby, which belongs to the first native word."""
    return [
        part
        for part in takewhile(lambda part: not isinstance(part, str), original)
        if not (isinstance(part, msbt.Tag) and (part.group, part.type) == (0, 0))
    ]


def patch_text(data: bytes) -> bytes:
    """One language archive with :data:`LINES` as Talon's prize lines, each in its native line's opening style."""
    files = sarc.read(data)
    if MESSAGES not in files:
        raise PatchError(f"no message file {MESSAGES} in the archive")
    messages = msbt.read(files[MESSAGES]).messages
    if missing := sorted(LINES.keys() - messages.keys()):
        raise PatchError(f"{MESSAGES}: no messages labelled {missing}")
    edits = {
        label: text.stone_line(_lead(messages[label]), line, width=WIDTH, rows=ROWS) for label, line in LINES.items()
    }
    return text.edit_messages({MESSAGES: edits})(data)


def changes(romfs: str | Path, placements: Mapping[str, str]) -> FileChanges:
    """The flow, placement and message transforms for a moved prize (``placements``: location -> logic item); none
    while Talon still gives his milk."""
    if not moved(placements):
        return {}
    return {
        FLOW_PATH: patch_flow,
        BANC_PATH: patch_banc,
        **{text.archive_path(language): patch_text for language in text.languages(romfs)},
    }
