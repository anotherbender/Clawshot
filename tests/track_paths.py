"""The path checker for gift_rules.toml ``track`` entries (spec tracker-auto-checks 5.1-5.3, plan P9.a): does a
flow set a gift's native flag on exactly the paths that run its grant? Shared by the synthetic test and the dump
test; the evidence it re-checks is ``plans/tracker-auto-checks-audit.md``.

A walk starts at an entry the game or another flow can start, expands local sub-flow calls with a call stack (a
callee returns to its caller; call parameters bind the callee's ``Argument`` values), runs every branch of a Fork
before its Join, and follows a Bool query only on the branch that agrees with what the walk already read or set
(case 0 is true). Two walks are faults:

- ``grant without flag``: it runs a grant and ends with the flag not set;
- ``flag without grant``: it sets the flag from not set and ends without running a grant.

A grant is a census step; when the step calls a local entry with the item as an argument, the grant is the callee's
event that hands that argument over (a minigame call that can fail hands nothing over). ``invariants`` prune walks
the game cannot take: ``(a, va, b, vb)`` says flag ``a`` equal to ``va`` implies flag ``b`` equal to ``vb``."""

from collections import deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from clawshot.census.gifts import _successors, reachable
from clawshot.formats import evfl

SET_BOOL = "EventTriggerSetGameDataBool"
QUERY_BOOL = "EventQueryIsGameDataBool"
QUEST_STEP = "EventExecuteProgressChallengeStep"
TRANSITION = "EventTransition"
MAX_DEPTH = 8


@dataclass(frozen=True)
class Flag:
    """What a track entry reads: ``kind`` bool or quest, ``name`` the Bool or quest, ``step`` the quest's step."""

    kind: str
    name: str
    step: str | None = None

    @property
    def key(self) -> str:
        return self.name if self.kind == "bool" else f"Step_{self.name}=={self.step}"


def _op(fc: evfl.Flowchart, event) -> str | None:
    if isinstance(event, evfl.ActionEvent):
        return fc.actors[event.actor].actions[event.action]
    if isinstance(event, evfl.SwitchEvent):
        return fc.actors[event.actor].queries[event.query]
    return None


def _resolve(fc: evfl.Flowchart, value, stack: tuple) -> object:
    """A parameter's value with ``Argument``s bound by the calls on ``stack`` (innermost last)."""
    depth = len(stack)
    while isinstance(value, evfl.Argument) and depth:
        depth -= 1
        value = (fc.events[stack[depth][1]].params or {}).get(str(value))
    return None if isinstance(value, evfl.Argument) else value


def _writes(fc: evfl.Flowchart, event, stack: tuple, flag: Flag) -> bool | None:
    """True when ``event`` sets ``flag``, False when it unsets it (a reset, or the quest moving to another step)."""
    params = getattr(event, "params", None) or {}
    op = _op(fc, event)
    if flag.kind == "bool" and op == SET_BOOL and _resolve(fc, params.get("GameDataName"), stack) == flag.name:
        value = _resolve(fc, params.get("Value"), stack)
        return value if isinstance(value, bool) else None
    if flag.kind == "quest" and op == QUEST_STEP and _resolve(fc, params.get("ChallengeName"), stack) == flag.name:
        return _resolve(fc, params.get("StepName"), stack) == flag.step
    return None


def writers(fc: evfl.Flowchart, flag: Flag) -> list[str]:
    """Names of the events that set ``flag``, directly or through a call argument."""
    out = []
    for event in fc.events:
        params = getattr(event, "params", None) or {}
        if _writes(fc, event, (), flag):
            out.append(event.name)
        elif any(v == flag.name for v in params.values() if not isinstance(v, evfl.Argument)) and isinstance(
            event, evfl.SubFlowEvent
        ):
            out.append(event.name)  # passes the flag to a callee that sets it (checked by the walk)
    return out


def starts(fc: evfl.Flowchart, external: Iterable[str] = ()) -> list[int]:
    """Entry events a walk starts from: entries in ``external`` (EventSetting rows, other flows' calls) and entries
    no local call uses."""
    called = {e.entry_point for e in fc.events if isinstance(e, evfl.SubFlowEvent) and not e.flowchart}
    names = set(external)
    return [
        ep.main_event
        for ep in fc.entry_points
        if ep.main_event != evfl.NONE and (ep.name in names or ep.name not in called)
    ]


def _grant_events(fc: evfl.Flowchart, grants: Iterable[str], param: Mapping[str, str]) -> dict[int, str | None]:
    """Grant event index -> the item argument its callee hands over (None: the event itself is the grant)."""
    index = {e.name: i for i, e in enumerate(fc.events)}
    entry = {ep.name: ep.main_event for ep in fc.entry_points}
    out: dict[int, str | None] = {}
    for name in grants:
        i = index[name]
        event = fc.events[i]
        arg = param.get(name)
        local = isinstance(event, evfl.SubFlowEvent) and not event.flowchart and event.entry_point in entry
        if (
            local
            and arg
            and any(
                evfl.Argument(arg) in (getattr(fc.events[k], "params", None) or {}).values()
                for k in reachable(fc, entry[event.entry_point])
            )
        ):
            out[i] = arg
        else:
            out[i] = None
    return out


def check(
    fc: evfl.Flowchart,
    flag: Flag,
    grants: Iterable[str],
    *,
    external: Iterable[str] = (),
    param: Mapping[str, str] | None = None,
    invariants: Iterable[tuple[str, bool, str, bool]] = (),
) -> list[str]:
    """Faults of ``flag`` against the grant events ``grants`` in one flowchart, each with the offending walk."""
    grant = _grant_events(fc, grants, param or {})
    entry = {ep.name: ep.main_event for ep in fc.entry_points}
    rules = tuple(invariants)
    key = flag.key

    def consistent(known: dict) -> bool:
        return not any(known.get(a) == va and known.get(b) == (not vb) for a, va, b, vb in rules)

    def grant_hit(i: int, stack: tuple) -> bool:
        if grant.get(i, "") is None:
            return True
        params = getattr(fc.events[i], "params", None) or {}
        for depth in range(len(stack) - 1, -1, -1):  # an event handing over a grant call's item argument
            call = stack[depth][1]
            arg = grant.get(call)
            if arg and evfl.Argument(arg) in params.values() and _resolve(fc, evfl.Argument(arg), stack[: depth + 1]):
                return True
        return False

    def enter(i: int, stack: tuple, granted: bool, fresh: bool, known: tuple):
        """The walk state after running event ``i`` (and, for a Fork, all of its branches)."""
        known_d = dict(known)
        event = fc.events[i]
        body = [i, *sorted(_fork_body(fc, event))] if isinstance(event, evfl.ForkEvent) else [i]
        for k in body:
            ek = fc.events[k]
            granted = granted or grant_hit(k, stack)
            w = _writes(fc, ek, stack, flag)
            if w is True and known_d.get(key) is not True:
                fresh = True
            if w is not None:
                known_d[key] = w
            if _op(fc, ek) == SET_BOOL:
                p = ek.params or {}
                name, value = _resolve(fc, p.get("GameDataName"), stack), _resolve(fc, p.get("Value"), stack)
                if isinstance(name, str) and isinstance(value, bool):
                    known_d[name] = value
        return granted, fresh, tuple(sorted(known_d.items()))

    def moves(state):
        i, stack, granted, fresh, known = state
        event = fc.events[i]
        if isinstance(event, evfl.ForkEvent):
            yield event.join, stack, known
            return
        local = isinstance(event, evfl.SubFlowEvent) and not event.flowchart
        if local and entry.get(event.entry_point, evfl.NONE) != evfl.NONE and len(stack) < MAX_DEPTH:
            yield entry[event.entry_point], stack + ((event.next, i),), known
            return
        if isinstance(event, evfl.SwitchEvent) and _op(fc, event) == QUERY_BOOL:
            name = _resolve(fc, (event.params or {}).get("GameDataName"), stack)
            if isinstance(name, str):
                have = dict(known).get(name)
                for value, j in event.cases:
                    v = value == 0
                    if have is None or have == v:
                        yield j, stack, tuple(sorted({**dict(known), name: v}.items()))
                return
        nxt = _successors(event)
        if nxt:
            for j in nxt:
                yield j, stack, known
            return
        while stack:
            (ret, _), stack = stack[-1], stack[:-1]
            if ret != evfl.NONE:
                yield ret, stack, known
                return
        yield None

    faults: dict[str, list[str]] = {}
    prev: dict = {}
    queue: deque = deque()
    for s in starts(fc, external):
        state = (s, (), *enter(s, (), False, False, ()))
        if consistent(dict(state[4])) and state not in prev:
            prev[state] = None
            queue.append(state)
    while queue and len(faults) < 2:
        state = queue.popleft()
        for move in moves(state):
            if move is None:
                _, _, granted, fresh, known = state
                kind = None
                if granted and dict(known).get(key) is not True:
                    kind = "grant without flag"
                elif fresh and not granted:
                    kind = "flag without grant"
                if kind and kind not in faults:
                    walk, cur = [], state
                    while cur is not None:
                        walk.append(fc.events[cur[0]].name)
                        cur = prev[cur]
                    faults[kind] = walk[::-1]
                continue
            j, stack, known = move
            nxt = (j, stack, *enter(j, stack, state[2], state[3], known))
            if consistent(dict(nxt[4])) and nxt not in prev:
                prev[nxt] = state
                queue.append(nxt)
    return [f"{fc.name}: {kind} for {key} (grants {sorted(grants)}): {' > '.join(w)}" for kind, w in faults.items()]


def cut_reaches(fc: evfl.Flowchart, grants: Iterable[str]) -> list[str]:
    """For a cutscene's flow (``played`` entries): faults unless every walk of each entry holding a grant reaches
    one. The entry is the timeline cut that runs it; HavePlayedEvent is the engine's, set when the event ends."""
    index = {e.name: i for i, e in enumerate(fc.events)}
    targets = {index[g] for g in grants if g in index}
    if len(targets) != len(set(grants)):
        return [f"{fc.name}: grant step(s) {sorted(set(grants) - set(index))} are gone"]
    holders = [ep for ep in fc.entry_points if ep.main_event != evfl.NONE and reachable(fc, ep.main_event) & targets]
    if not holders:
        return [f"{fc.name}: no entry reaches a grant {sorted(grants)}"]
    entry = {e.name: e.main_event for e in fc.entry_points}
    out = []
    for ep in holders:
        seen, todo, end = set(), [(ep.main_event, ())], None
        while todo and end is None:  # a walk that ends without passing a grant
            k, stack = todo.pop()
            if (k, stack) in seen or k in targets:
                continue
            seen.add((k, stack))
            event = fc.events[k]
            if isinstance(event, evfl.ForkEvent):  # every branch runs, then the join
                if not _fork_body(fc, event) & targets:
                    todo.append((event.join, stack))
                continue
            callee = entry.get(event.entry_point, evfl.NONE) if isinstance(event, evfl.SubFlowEvent) else evfl.NONE
            if not getattr(event, "flowchart", "x") and callee != evfl.NONE and len(stack) < MAX_DEPTH:
                todo.append((callee, (*stack, event.next)))
                continue
            succ = _successors(event)
            while not succ and stack:
                ret, stack = stack[-1], stack[:-1]
                succ = [] if ret == evfl.NONE else [ret]
            if not succ:
                end = event.name
            todo += [(j, stack) for j in succ]
        if end is not None:
            out.append(f"{fc.name}: cut {ep.name} can end at {end} without a grant {sorted(grants)}")
    return out


def _fork_body(fc: evfl.Flowchart, fork: evfl.ForkEvent) -> set[int]:
    """Events a Fork's branches run before its Join (nested Forks included)."""
    seen: set[int] = set()
    todo = list(fork.forks)
    while todo:
        k = todo.pop()
        if k in seen or k == fork.join or k == evfl.NONE:
            continue
        seen.add(k)
        todo += _successors(fc.events[k])
    return seen
