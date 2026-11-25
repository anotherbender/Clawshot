"""Native healing for the two split story grants; post-add moat heart-piece text.

Heart upgrades have already been added by the scene. Replaying CheckHeart's
SpecialDeal-coupled cure duplicated the played moat piece; use the native
HP-only full heal instead (DoorOfTime/Event70). Other cure actors retain their
native CheckHeart path. The moat's post-add caption is a private native clone.
"""

from collections.abc import Mapping
from copy import deepcopy
from functools import partial

from clawshot.census.gifts import reachable
from clawshot.formats import byml, evfl
from clawshot.patch import gifts
from clawshot.patch.items import ItemActors
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges

MOAT = "HF Ocarina of Time Item"
SARIA = "LW Gift from Saria"
POUCH = "GetPouchContent"
ANALYZED = "RSDB/GameAnalyzedEventInfo.Product.111.rstbl.byml.zs"
DISPLAY = "ClawshotDisplayHeartPieceAfterGrant"
HEAL = "ClawshotStoryGiftHeal"
FULL_HEAL = "EventTriggerHealLifeMax"
HEART_ACTORS = ("Obj_Heart_Piece", "Obj_Heart_Container")
# check -> (flow, vanilla logic item, grant, display, heal anchor)
SOURCES = {
    MOAT: ("Dm_MelodyGet_Time", "Ocarina of Time", "Event70", "Event229", "Event229"),
    SARIA: ("Dm_Kokiri_0155", "Fairy Ocarina", "Event68", "Event77", "Event68"),
}


def path(flow: str) -> str:
    return f"Event/EventFlow/{flow}.bfevfl.zs"


def _encode(file: evfl.EventFlowFile) -> bytes:
    result = evfl.write(file)
    if evfl.read(result) != file:
        raise PatchError("story gift: written flow does not read back")
    return result


def _scene(data: bytes, *, flow: str, grant: str, display: str, anchor: str) -> bytes:
    file = evfl.read(data)
    fc = file.flowchart
    if fc is None or fc.name != flow:
        raise PatchError(f"story gift: expected {flow} flowchart")
    events = {event.name: i for i, event in enumerate(fc.events)}
    if HEAL in events or not {grant, display, anchor} <= events.keys():
        raise PatchError(f"story gift {flow}: missing source events or already patched")
    give, window = fc.events[events[grant]], fc.events[events[display]]
    # Consume the gift writer's native actor identity (including tunic projections).
    item = (getattr(give, "params", None) or {}).get("Actor")
    if (
        not isinstance(give, evfl.ActionEvent)
        or fc.actors[give.actor].name != "PouchSystemActor"
        or fc.actors[give.actor].actions[give.action] != "EventTriggerAddOrRemovePouchContent"
        or not isinstance(item, str)
        or isinstance(item, evfl.Argument)
        or not item
        or give.params.get("Num") != 1
        or give.params.get("IsGetEvent") is not False
        or not isinstance(window, evfl.SubFlowEvent)
        or (window.flowchart, window.entry_point) != (POUCH, "DisplayGetByActorName")
        or window.params != {"ActorName": item}
    ):
        raise PatchError(f"story gift {flow}: changed grant/display: {give!r}, {window!r}")
    source = fc.events[events[anchor]]
    if (flow == SOURCES[MOAT][0] and (source.next == evfl.NONE or fc.events[source.next].name != "Event242")) or (
        flow == SOURCES[SARIA][0] and source.next != evfl.NONE
    ):
        raise PatchError(f"story gift {flow}: changed healing continuation: {source!r}")
    if flow == SOURCES[MOAT][0] and item == "Obj_Heart_Piece":
        window.entry_point = DISPLAY
    added = len(fc.events)
    if item in HEART_ACTORS:
        players = [i for i, actor in enumerate(fc.actors) if (actor.name, actor.secondary_name) == ("Player_Event", "")]
        if len(players) != 1:
            raise PatchError(f"story gift {flow}: expected one native Player_Event for healing")
        player = fc.actors[players[0]]
        if FULL_HEAL not in player.actions:
            player.actions.append(FULL_HEAL)
        fc.events.append(evfl.ActionEvent(HEAL, players[0], player.actions.index(FULL_HEAL), source.next))
    else:
        fc.events.append(evfl.SubFlowEvent(HEAL, "Dm_SY_Get", "CheckHeart", source.next, {"ActorName": item}))
    source.next = added
    owners = [entry for entry in fc.entry_points if added in reachable(fc, entry.main_event)]
    if not owners:
        raise PatchError(f"story gift {flow}: healing anchor is unreachable")
    if isinstance(fc.events[added], evfl.SubFlowEvent):
        for entry in owners:
            entry.sub_flow_events.append(added)
    return _encode(file)


def _post_add_piece_display(data: bytes) -> bytes:
    file = evfl.read(data)
    fc = file.flowchart
    if fc is None or fc.name != POUCH:
        raise PatchError("story gift: expected GetPouchContent flowchart")
    events = {event.name: i for i, event in enumerate(fc.events)}
    if not {"Event56", "Event15", "Event14", "Event114"} <= events.keys():
        raise PatchError("story gift: missing native heart-piece display")
    query, target = (fc.events[events[name]] for name in ("Event56", "Event15"))
    open_window, open_piece = (fc.events[events[name]] for name in ("Event14", "Event114"))
    if (
        not isinstance(query, evfl.SwitchEvent)
        or fc.actors[query.actor].name != "PouchSystemActor"
        or fc.actors[query.actor].queries[query.query] != "EventQueryHeartPieceNum"
        or [value for value, _ in query.cases] != [0, 1, 2, 3]
        or fc.entry_point("OpenGetWindow_HeartPiece").main_event != events["Event56"]
        or not isinstance(target, evfl.ActionEvent)
        or fc.actors[target.actor].name != "PouchSystemActor"
        or fc.actors[target.actor].actions[target.action] != "EventTriggerSetForGetWindow"
        or target.params != {"Actor": evfl.Argument("ActorName")}
        or fc.entry_point("DisplayGetByActorName").main_event != events["Event15"]
        or target.next != events["Event14"]
        or not isinstance(open_window, evfl.SubFlowEvent)
        or (open_window.flowchart, open_window.entry_point) != ("", "OpenGetWindow")
        or not isinstance(open_piece, evfl.SubFlowEvent)
        or (open_piece.flowchart, open_piece.entry_point) != ("", "OpenGetWindow_HeartPiece")
    ):
        raise PatchError(f"story gift: changed heart-piece display: {query!r}, {target!r}")
    rotated = deepcopy(query)
    cases = dict(query.cases)
    rotated.cases = [(count, cases[(count - 1) % 4]) for count in range(4)]
    caption = DISPLAY + "Caption"
    window = DISPLAY + "Window"
    gifts._clone_entry(fc, "OpenGetWindow_HeartPiece", {query.name: rotated}, name=caption)
    piece_call = deepcopy(open_piece)
    piece_call.entry_point = caption
    gifts._clone_entry(fc, "OpenGetWindow", {open_piece.name: piece_call}, name=window)
    window_call = deepcopy(open_window)
    window_call.entry_point = window
    # Retain the native close-dialog and post-window history/caption-save tail.
    gifts._clone_entry(fc, "DisplayGetByActorName", {open_window.name: window_call}, name=DISPLAY)
    return _encode(file)


def _register(data: bytes, *, flows: tuple[str, ...]) -> bytes:
    document = byml.load(data)
    for flow in flows:
        rows = [row for row in document.root if row.get("__RowId") == flow]
        if len(rows) != 1:
            raise PatchError(f"story gift: expected one analyzed event row for {flow}, got {rows!r}")
        row = rows[0]
        row["SubFlowList"] = sorted(set(row.get("SubFlowList", ())) | {"Dm_SY_Get"})
    result = byml.dump(document)
    if byml.difference(document.root, byml.read(result)) is not None:
        raise PatchError("story gift: written analysis does not read back")
    return result


def changes(placements: Mapping[str, str], actors: ItemActors) -> FileChanges:
    out = {}
    flows = []
    for check, (flow, vanilla, grant, display, anchor) in SOURCES.items():
        item = placements.get(check, vanilla)
        if item == vanilla:
            continue
        actor = actors.actor(item)
        out[path(flow)] = partial(_scene, flow=flow, grant=grant, display=display, anchor=anchor)
        if actor not in HEART_ACTORS:
            flows.append(flow)
        if check == MOAT and actor == "Obj_Heart_Piece":
            out[path(POUCH)] = _post_add_piece_display
    if flows:
        out[ANALYZED] = partial(_register, flows=tuple(flows))
    return out
