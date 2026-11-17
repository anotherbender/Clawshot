"""Door of Time: native closed; both early modes wait for the Field clock (the owl arrival and Impa's send-off).

No stone quest, inventory grant, saved default/history or first-adult scene is forged.
Early modes keep the escape/moat sources available after first pull; late callbacks cannot
undo Complete. The pre-send-off courtyard reset stays native. Audit: plans/rounds/r16-time.md.
"""

import argparse
import sys
from collections.abc import Mapping
from pathlib import Path

from clawshot.formats import byml, evfl
from clawshot.patch import age, door_stage, door_story
from clawshot.patch.gamedata import GAME_DATA_LIST, BuiltFile
from clawshot.patch.plan import PatchError, Plan
from clawshot.patch.write import FileChanges, WrittenFile
from clawshot.patch.write import write as write_patch
from clawshot.save import key

MODES = ("closed", "song_only", "open")
FLOW = "Event/EventFlow/DoorOfTime.bfevfl.zs"
PLACEMENT = "Banc/Market/Market_Child_Static.bcett.byml.zs"
DRAW_GROUP = 11738513547087641325
DRAW_LOGIC = "Logic/Module/Market_Child_Prefab/Market_Child_Prefab_e700.logic.module.ain"
DRAW_BINDINGS = {
    "EventRequestActor_7fe2": (17385100471140562353, "EventRequestActor"),
    "EventRequestActor_0b2e": (2548516804884289836, "EventRequestActor"),
    "Obj_TimeTemple_MasterSword_A_01_e482": (1016238122178870176, "Obj_TimeTemple_MasterSword_A_01"),
}
OPENED = "Market_Child_TimeTempleDoor_Opened"
REACTION = "Market_Child_TimeTempleDoor_OcarinaReacts"
TIME_SONG = "IsGet.Item_Melody_TimeSong"
SENDOFF = "HavePlayedEvent.Dm_HrlField_0020"
_STORY_CHANGES = door_story.changes()
_ORDER_CHANGES = door_story.changes(early=False)


def _altar_reaction(data: bytes, values: list[list[byml.U64]]) -> bytes:
    """Change the non-saved altar reaction and add the early-mode story predicates."""
    document = byml.load(data)
    found = [row for row in document.root["Data"]["BoolExp"] if row.get("Hash") == key(REACTION)]
    expected = [
        [byml.U64(1), byml.U64(key("Step_DoorOfTime"))],
        [byml.U64(2), byml.U64(key("Step05"))],
        [byml.U64(5)],
        [byml.U64(0), byml.U64(key(OPENED))],
        [byml.U64(4)],
    ]
    if len(found) != 1 or found[0].get("Values") != expected or found[0].get("SaveFileIndex") != -1:
        raise PatchError(f"early door: changed altar reaction expression: {found!r}")
    found[0]["Values"] = values
    door_stage.add_expressions(document.root)
    result = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(result))) is not None:
        raise PatchError(f"early door: written GameData does not read back: {difference}")
    return result


def song_reaction(data: bytes) -> bytes:
    """React once the Field clock may run, before Step05; never replace songs once the door is opened."""
    return _altar_reaction(
        data,
        [
            [byml.U64(0), byml.U64(key(OPENED))],
            [byml.U64(10), byml.U64(key(door_stage.CLOCK_READY))],
            [byml.U64(5)],
            [byml.U64(4)],
        ],
    )


def open_reaction(data: bytes) -> bytes:
    """Disable the song-driven door scene, including after the automatic opening.

    Native BoolExp has proven Bool/NOT/OR operators, but no audited literal-true opcode.
    `opened or not opened` is always invalid, without writing the saved opened/history flags.
    """
    return _altar_reaction(
        data,
        [
            [byml.U64(0), byml.U64(key(OPENED))],
            [byml.U64(0), byml.U64(key(OPENED))],
            [byml.U64(5)],
            [byml.U64(4)],
        ],
    )


def song_flow(data: bytes) -> bytes:
    """Bypass the stone quest gate, retaining the Field clock gate, learned song and native play/once/scene."""
    document = evfl.read(data)
    fc = document.flowchart
    if fc is None or fc.name != "DoorOfTime":
        raise PatchError("song_only: expected DoorOfTime flowchart")
    events = {event.name: (index, event) for index, event in enumerate(fc.events)}
    required = ("Event92", "Event60", "Event69", "Event18")
    if any(name not in events for name in required):
        raise PatchError("song_only: missing native door gate events")
    gate_index, gate = events["Event60"]
    opened_index, opened = events["Event69"]
    _, predecessor = events["Event92"]
    entries = [entry for entry in fc.entry_points if entry.name == "DoorOfTime_OpenDoor"]
    if (
        not isinstance(gate, evfl.SwitchEvent)
        or fc.actors[gate.actor].name != "GameDataActor"
        or fc.actors[gate.actor].queries[gate.query] != "EventQueryIsGameDataBoolExp"
        or gate.params != {"GameDataName": "DoorOfTime_IsAfter_Step04_Exp"}
        or gate.cases != [(0, opened_index)]
        or not isinstance(opened, evfl.SwitchEvent)
        or opened.params != {"GameDataName": OPENED, "Index": -1}
        or not isinstance(predecessor, evfl.ActionEvent)
        or predecessor.next != gate_index
        or len(entries) != 1
        or entries[0].main_event != events["Event18"][0]
    ):
        raise PatchError(f"song_only: changed native door chain: {gate!r}, {opened!r}, {predecessor!r}")
    actor = fc.actors[opened.actor]
    query = actor.queries.index("EventQueryIsGameDataBool")
    first = entries[0].main_event
    entries[0].main_event = len(fc.events)
    fc.events.append(
        evfl.SwitchEvent(
            "ClawshotDoorLearnedTime",
            opened.actor,
            query,
            [(0, len(fc.events) + 1)],
            {"GameDataName": TIME_SONG, "Index": -1},
        )
    )
    # The stone gate's own BoolExp query, asking for the Field clock instead.
    fc.events.append(
        evfl.SwitchEvent(
            "ClawshotDoorClockReady", gate.actor, gate.query, [(0, first)], {"GameDataName": door_stage.CLOCK_READY}
        )
    )
    predecessor.next = opened_index
    result = evfl.write(document)
    if evfl.read(result) != document:
        raise PatchError("song_only: written flow does not read back")
    return result


def _song_story(data: bytes) -> bytes:
    return _STORY_CHANGES[FLOW](song_flow(data))


def open_pedestal(data: bytes) -> bytes:
    """Use the ungated native attention module; Draw itself selects first-pull versus repeat travel."""
    document = byml.load(data)
    tree = document.root
    found = [group for group in tree["AiGroups"] if group.get("Hash") == DRAW_GROUP]
    if len(found) != 1 or found[0].get("Logic") != DRAW_LOGIC:
        raise PatchError(f"open door: changed child pedestal group: {found!r}")
    group = found[0]
    refs = group.get("References", [])
    if len(refs) != len(DRAW_BINDINGS) or {r.get("Id") for r in refs} != DRAW_BINDINGS.keys():
        raise PatchError(f"open door: changed child pedestal references: {refs!r}")
    for ref in refs:
        actor_hash, actor_type = DRAW_BINDINGS[ref["Id"]]
        actors = [actor for actor in tree["Actors"] if actor.get("Hash") == actor_hash]
        if (
            ref.get("Path") != ref["Id"]
            or ref.get("Reference") != actor_hash
            or len(actors) != 1
            or actors[0].get("Gyaml") != actor_type
        ):
            raise PatchError(f"open door: changed child pedestal identity: {ref!r}, {actors!r}")
        if (
            ref["Id"] == "EventRequestActor_7fe2"
            and actors[0].get("Dynamic", {}).get("RequestEventName") != "Market_Child_DoorOfTime_Draw"
        ):
            raise PatchError(f"open door: changed first-pull request: {actors!r}")
    group["Logic"] = age.UNGATED_LOGIC
    group["References"] = [
        {**ref, "Id": "EventRequestActor_7a32" if ref["Id"] == "EventRequestActor_7fe2" else "CheckAttentionActor_8348"}
        for ref in refs
        if ref["Id"] != "EventRequestActor_0b2e"
    ]
    result = byml.dump(document)
    if (difference := byml.difference(document.root, byml.read(result))) is not None:
        raise PatchError(f"open door: written pedestal does not read back: {difference}")
    return result


def changes(_placements: Mapping[str, str], *, mode: str = "closed") -> FileChanges:
    if mode not in MODES:
        raise PatchError(f"unknown door_of_time mode {mode!r}")
    if mode == "closed":
        return dict(_ORDER_CHANGES)
    if mode == "song_only":
        return {**_STORY_CHANGES, FLOW: _song_story, GAME_DATA_LIST: song_reaction}
    return {**_STORY_CHANGES, PLACEMENT: open_pedestal, GAME_DATA_LIST: open_reaction}


def build(romfs: str | Path, *, mode: str = "closed") -> list[BuiltFile]:
    """Early modes: the story stage's modules; open also the Temple door module, which opens on the clock gate."""
    if mode not in MODES:
        raise PatchError(f"unknown door_of_time mode {mode!r}")
    if mode == "closed":
        return []
    return door_stage.build(romfs, gate=mode == "open")


def write(romfs: str | Path, out: str | Path, *, mode: str = "closed") -> list[WrittenFile]:
    return write_patch(
        Plan([], [], []), romfs, out, extra_changes=[changes({}, mode=mode)], fast_start_files=build(romfs, mode=mode)
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--romfs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--door-of-time", choices=MODES, default="closed")
    args = parser.parse_args(argv)
    try:
        files = write(args.romfs, args.out, mode=args.door_of_time)
    except PatchError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    for file in files:
        print(f"{file.path}: {file.size} -> {file.new_size}; allocation {file.entry} -> {file.new_entry}")
    print(f"door_of_time={args.door_of_time}; wrote {len(files)} resources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
