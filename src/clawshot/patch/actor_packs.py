"""Read-only composition rules for native actor packs, measured on build ``e0f3ccfa`` (Round 15).

An actor pack ``Pack/Actor/<Actor>.pack.zs`` holds ``Actor/<Actor>.engine__actor__ActorParam.bgyml``, the actor
parameter files of its ``$parent`` chain, and every member reached from the chain's *effective* components (a child's
component replaces its parent's), following each member's own references and ``$parent`` transitively. References to
other actors' parameters (a pouch's ``PouchActor``, an equipment actor) name actors loaded from their own packs and are
not packed. Everything else a pack references and lacks is a shared resident or loose resource. This reproduces the
member set of 7508 of 8373 native actor packs exactly, including ``Obj_Token_Gold``, ``Obj_Shield_Hylian``,
``Item_Boomerang`` and ``Obj_Ocarina_Time`` even when several packs are offered as sources; the other 865 also pack AI
modules that only their binary AINB graphs reference, which this BYML walk does not read. A member path has the same
bytes in every native pack that holds it.
"""

import copy
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath

from clawshot.formats import byml
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import actor_path, member_path

Sources = Sequence[Mapping[str, bytes]]
"""Packs (member name -> bytes) to take members from, in order."""

AI_ROOT = "Work/AI/Root/"
ACTOR_DIR = "Actor/"


def actor_member(actor: str) -> str:
    """``Obj_X`` -> ``Actor/Obj_X.engine__actor__ActorParam.bgyml``, the member holding its parameters."""
    return member_path(actor_path(actor))


def work_path(member: str) -> str:
    """A member name in the ``Work/...gyml`` form that ``$parent`` and pouch/drop references use."""
    return "Work/" + member.removesuffix(".bgyml") + ".gyml"


def component_ref(member: str) -> str:
    """A member name in the ``?...bgyml`` form actor parameter components use."""
    return "?" + member


def reference(value: object) -> str | None:
    """The pack member (or loose resource) a reference string names; None for an ordinary string.

    ``?Component/X.bgyml`` names its member as is; ``Work/Component/X.gyml`` names ``Component/X.bgyml``; an AI root
    ``Work/AI/Root/.../X.root.ain`` is the graph ``AI/X.root.ainb`` (as ``Item_Token_Gold``'s is packed)."""
    if not isinstance(value, str):
        return None
    path = value.removeprefix("?")
    if path.startswith(AI_ROOT) and path.endswith(".root.ain"):
        return f"AI/{PurePosixPath(path).name}b"
    if path.startswith("Work/"):
        path = path.removeprefix("Work/")
        return path.removesuffix(".gyml") + ".bgyml" if path.endswith(".gyml") else path
    return path if value.startswith("?") else None


def strings(node: object):
    """Every string value in a parsed BYML tree, depth first."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, Mapping):
        for value in node.values():
            yield from strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from strings(value)


def find(sources: Sources, name: str) -> bytes | None:
    """A member's bytes from the first source holding it; sources that disagree are refused."""
    found = [source[name] for source in sources if name in source]
    if any(data != found[0] for data in found[1:]):
        raise PatchError(f"{name}: the source packs hold different bytes under one member path")
    return found[0] if found else None


def resolve(sources: Sources, path: str, _below: tuple[str, ...] = ()) -> tuple[dict, list[str]]:
    """An actor parameter (``Work/Actor/X...gyml`` or its member name) merged down its ``$parent`` chain, and the
    chain's members, root first. ``Components`` merge per component; any other field is replaced."""
    name = reference(path) or path
    if name in _below:
        raise PatchError(f"{name}: its $parent chain loops")
    data = find(sources, name)
    if data is None:
        raise PatchError(f"{name}: missing from the source packs")
    node = byml.read(data)
    resolved, chain = resolve(sources, node["$parent"], (*_below, name)) if "$parent" in node else ({}, [])
    for key, value in node.items():
        if key == "Components":
            resolved[key] = {**resolved.get(key, {}), **value}
        elif key != "$parent":
            resolved[key] = copy.deepcopy(value)
    return resolved, [*chain, name]


def resolve_node(sources: Sources, name: str, *, builtin: str = "") -> dict:
    """A component member merged down its ``$parent`` chain (fields replaced, not merged). ``builtin`` names the
    one parent allowed to be absent: the engine's own default, which is no file in the game."""
    data = find(sources, name)
    if data is None:
        raise PatchError(f"{name}: missing from the source packs")
    node = byml.read(data)
    parent = node.get("$parent")
    resolved = {}
    if parent is not None and not (reference(parent) == builtin and find(sources, builtin) is None):
        resolved = resolve_node(sources, reference(parent) or parent, builtin=builtin)
    resolved.update({k: copy.deepcopy(v) for k, v in node.items() if k != "$parent"})
    return resolved


@dataclass(frozen=True)
class Closure:
    members: dict[str, bytes]  # the pack's members
    external: frozenset[str]  # referenced resources the sources lack (residents, loose files, built-in defaults)
    actors: frozenset[str]  # other actors' parameter members referenced (loaded from their own packs)
    components: dict[str, str]  # the effective components


def closure(sources: Sources, actor: str) -> Closure:
    """The members a native-style pack for ``actor`` holds, taken from ``sources`` (see the module docstring)."""
    resolved, chain = resolve(sources, actor_member(actor))
    members = {name: find(sources, name) for name in chain}
    external: set[str] = set()
    actors: set[str] = set()
    components = dict(resolved.get("Components", {}))
    todo = [ref for ref in map(reference, components.values()) if ref]
    while todo:
        name = todo.pop()
        if name in members:
            continue
        if name.startswith(ACTOR_DIR) and name.endswith(".engine__actor__ActorParam.bgyml"):
            actors.add(name)
            continue
        data = find(sources, name)
        if data is None:
            external.add(name)
            continue
        members[name] = data
        if name.endswith(".bgyml"):
            todo.extend(ref for ref in map(reference, strings(byml.read(data))) if ref)
    return Closure(members, frozenset(external), frozenset(actors), components)


def combination_table(read: Callable[[str], bytes], path: str, table_type: str) -> dict[str, dict]:
    """A ``CombinationDataTableData`` (such as death procedures) by cell key, each cell's fields merged over the same
    cell of its ``$parent`` chain. ``read`` gives a loose romfs file's bytes. The ``TableType`` the chain resolves to
    (a level may inherit it) must be ``table_type``."""

    def level(path: str) -> tuple[object, dict[str, dict]]:
        name = reference(path) or path
        node = byml.read(read(name))
        kind, table = level(node["$parent"]) if "$parent" in node else (None, {})
        for key, cell in node.get("CellList", {}).items():
            table[key] = {**table.get(key, {}), **cell}
        return node.get("TableType", kind), table

    kind, table = level(path)
    if kind != table_type:
        raise PatchError(f"{path}: table type {kind!r}, expected {table_type!r}")
    return table
