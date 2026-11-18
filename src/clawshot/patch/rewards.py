"""Replace only nine native reward grants, never boss/warp/sage completion.

The native animated emblem belongs to the source sage/stone scene and is retained.
The acquisition window and Zelda Notes target name the actual shuffled reward.
"""

from collections.abc import Callable, Mapping
from pathlib import Path

from clawshot.formats import evfl, zsdic
from clawshot.generate.rewards import catalog
from clawshot.patch.plan import PatchError
from clawshot.patch.write import FileChanges


def transform(slot: Mapping[str, str], actor: str) -> Callable[[bytes], bytes]:
    def apply(data: bytes) -> bytes:
        doc = evfl.read(data)
        chart = doc.flowchart
        if chart is None or chart.name != slot["flow"]:
            raise PatchError(f"reward {slot['flow']}: expected flowchart")
        events = {event.name: event for event in chart.events}
        grant = events.get(slot["event"])
        if (
            not isinstance(grant, evfl.SubFlowEvent)
            or grant.flowchart != "GetPouchContent"
            or grant.entry_point != "GetPouchContentByActorName"
            or grant.params != {"ActorName": slot["actor"]}
        ):
            raise PatchError(f"reward {slot['flow']}/{slot['event']}: unexpected grant {grant!r}")
        notes = events.get(slot["notes"])
        if (
            not isinstance(notes, evfl.ActionEvent)
            or chart.actors[notes.actor].actions[notes.action] != "EventTriggerZeldaNotesRequestSendDailyScreenShot"
            or notes.params is None
            or notes.params.get("TargetID") != slot["actor"]
            or notes.params.get("TypeID") != "get_item"
        ):
            raise PatchError(f"reward {slot['flow']}/{slot['notes']}: unexpected Notes target {notes!r}")
        grant.params = {"ActorName": actor}
        notes.params = {**notes.params, "TargetID": actor}
        result = evfl.write(doc)
        if evfl.read(result) != doc:
            raise PatchError(f"reward {slot['flow']}: readback differs")
        return result

    return apply


def changes(romfs: str | Path, placements: Mapping[str, str]) -> FileChanges:
    """Validate all sources before output; both active .110 and dormant base grant copies agree."""
    slots = catalog()["slots"]
    actors = {slot["item"]: slot["actor"] for slot in slots.values()}
    root = Path(romfs)
    dictionaries = zsdic.Dictionaries.from_romfs(root)
    out = {}
    for name, slot in slots.items():
        if name not in placements:
            continue
        item = placements[name]
        if item not in actors:
            raise PatchError(f"{name}: {item!r} is not one of the nine dungeon rewards")
        versions = ("", "." + slot["version"]) if "version" in slot else ("",)
        for version in versions:
            path = f"Event/EventFlow/{slot['flow']}{version}.bfevfl.zs"
            change = transform(slot, actors[item])
            # Even a same-item source must satisfy the native one-grant contract.
            change(dictionaries.decompress(path, (root / path).read_bytes()))
            if item != slot["item"]:
                out[path] = change
    return out
