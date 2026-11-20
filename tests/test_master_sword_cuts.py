"""Every native cut of both child-to-adult arrival movies, run frame by frame against the registered runtime.

Dm_TimeTemple_0085 (EntryPoint0, C01, other, C01_B) and Dm_TimeTemple_0088 (EntryPoint0, Gauntlet_Silver_First,
other) are booted by Market_Child_Field_ChildToAdult after its ReplaceEquipmentForEraChange call. Their inputs here
come from that actual era chain (round-18 child guard + Master Sword era guard), never from assumed values.

Model ([INFERENCE] where the game is not observable from data):
- Saved state: ``PlayerStatus.EquipWeapon`` (the selected blade) is separate from canonical ``IsGet.*`` and
  ``PouchData.*.StockNum``; a cut must never write either. The held actor (weapon slot 0) starts as the selected
  blade and changes only when a creation request resolves at the next frame boundary.
- ``EventQueryPlayerIsEquipWeapon`` reads the held actor (``live``, which lets 0088's native static-prop poll end)
  or the selected blade (``selected``); the runtime must be right under both.
- Creation requests: NoRelationPouch dynamic (``prop``), a static story prop (``static``), or the pouch restore of
  the selected blade (``pouch``, only with stock). Any created blade without stock is an unowned creation.
  ``EventWaitCreationFinishedEquipment`` consumes one valid request and blocks until it resolves; with none left it
  fails instead of being treated as success.
- Forks run concurrently until their join; local subflows return; the movie's own native external camera calls,
  animation, camera, fade and ``IsWaitEnd`` actions are finite (one frame), ``EventWait`` takes its frames.
"""

from dataclasses import dataclass, field

import pytest
from test_child_sword import BEFORE_FORCE, EQUIPPED, KOKIRI, MASTER, initial, run
from test_master_sword import native

from clawshot.formats import evfl
from clawshot.patch import equipment, master_sword

pytestmark = pytest.mark.dump

ARRIVAL = "Dm_TimeTemple_0085"
GAUNTLET = "Dm_TimeTemple_0088"
ERA = "ReplaceEquipmentForEraChange"
FLOWS = {
    ARRIVAL: ("EntryPoint0", "C01", "other", "C01_B"),
    GAUNTLET: ("EntryPoint0", "Gauntlet_Silver_First", "other"),
}
CUTS = [(flow, entry) for flow, entries in FLOWS.items() for entry in entries]
LARGE = master_sword.ADULT_BLADES[1:]
BIGGORON, GIANT, BROKEN = LARGE
READINGS = ("live", "selected")
SAVED = ("IsGet.", "PouchData.")
# (IsGet, StockNum): only both make a canonically owned blade.
STATES = {"absent": (False, 0), "flag-only": (True, 0), "stock-only": (False, 1), "owned": (True, 1)}
ABSENT, TRADED, OWNED = STATES["absent"], STATES["flag-only"], STATES["owned"]
# Child-side inputs (the adult candidate left by the previous adult visit, canonical blades) of real departures.
CASES = {
    "unowned-repeat-draw": ("", {}),
    "unowned-stale-master-candidate": (MASTER, {}),
    "owned-empty-candidate": ("", {MASTER: OWNED}),
    "owned-repeat-draw": (MASTER, {MASTER: OWNED}),
    "biggoron-unowned-master": (BIGGORON, {BIGGORON: OWNED}),
    "biggoron-owned-master": (BIGGORON, {BIGGORON: OWNED, MASTER: OWNED}),
    "giant-owned-master": (GIANT, {GIANT: OWNED, MASTER: OWNED}),
    "broken-giant-unowned-master": (BROKEN, {BROKEN: OWNED}),
    "traded-giant-owned-master": (GIANT, {GIANT: TRADED, MASTER: OWNED}),
}
# Native nodes an unarmed/other-blade arrival may skip; every other node (fade, camera, animation, waits) stays.
# 0085: other's Master creation + wait; C01's sheath, wait, restore and creation wait after its 300-frame wait.
# 0088: the existing owned-and-selected-only pose (slot-0 draw, slot-4 state).
GUARDED = {
    ARRIVAL: {"Event9", "Event14", "Event10", "Event12", "Event5", "Event19"},
    GAUNTLET: {"Event30", "Event27"},
}
FINITE = {
    "EventCamera",
    "UISystemActor",
    "Npc_Navi",
    "DevelopEventSystemActor",
    "EventWorldManagerController",
    "PostProcessingActor",
    "GameSystemActor",
}
PLAYER_FINITE = {
    "EventPlayerPlayASForFlowchart",
    "EventPlayerWarpToTargetPosAndRot",
    "EventTriggerPlayerSetTimerInvalidDoAction",
    "EventTriggerEmitXLink",
    "EventTriggerXLinkFadeByKey",
    "EventTriggerEquipmentUserRequestChangeState",  # the state of the held actor, never its identity
}
FRAMES, STEPS = 5000, 20000


class UnsatisfiedEquipmentWait(AssertionError):
    """``EventWaitCreationFinishedEquipment`` reached with no valid create/restore request left to wait for."""


@dataclass
class Request:
    actor: str
    source: str  # "prop", "static" or "pouch"
    done: bool = False
    waited: bool = False


@dataclass
class Thread:
    at: int
    join: int = evfl.NONE  # a fork branch ends at its own JoinEvent or at NONE
    parent: "Thread | None" = None
    calls: list[int] = field(default_factory=list)  # local subflow continuations
    resume: int = evfl.NONE  # the JoinEvent this thread waits on after a fork
    branches: int = 0
    wake: int = 0
    request: Request | None = None
    finished: bool = False


class Cut:
    """One entry of one movie, frame-stepped; ``data`` is the saved GameData the movie boots with."""

    def __init__(self, fc, calls, data, *, reading="live"):
        self.fc, self.calls, self.data, self.reading = fc, calls, data, reading
        selected = data[EQUIPPED]
        self.held = (selected, "pouch") if selected else None
        self.frame = 0
        self.trace, self.entries, self.created, self.unowned, self.invalid = [], [], [], [], []
        self.requests, self.ready, self.sleeping, self.creating = [], [], [], []

    def play(self, entry):
        root = Thread(self.fc.entry_point(entry).main_event)
        self.ready.append(root)
        steps = 0
        while True:
            while self.ready:
                steps += self._advance(self.ready.pop(0))
                assert steps < STEPS, ("cut loops without waiting", self.fc.name, entry, self.trace[-5:])
            if root.finished:
                self._resolve()
                return self
            assert self.sleeping or self.creating, ("cut deadlocked", self.fc.name, entry, self.trace[-5:])
            self._tick()
            assert self.frame < FRAMES, ("cut did not finish", self.fc.name, entry, self.held, self.trace[-5:])

    def _tick(self):
        if any(not request.done for request in self.requests):
            self.frame += 1  # creation resolves at the next frame boundary
        else:
            self.frame = min(thread.wake for thread in self.sleeping)
        self._resolve()
        woken = [thread for thread in self.sleeping if thread.wake <= self.frame]
        self.sleeping = [thread for thread in self.sleeping if thread.wake > self.frame]
        created = [thread for thread in self.creating if thread.request.done]
        self.creating = [thread for thread in self.creating if not thread.request.done]
        self.ready.extend(woken + created)

    def _resolve(self):
        for request in self.requests:
            if not request.done:
                request.done = True
                self.held = (request.actor, request.source)

    def _sleep(self, thread, frames, step):
        thread.wake = self.frame + frames
        self.sleeping.append(thread)
        return step

    def _finish(self, thread):
        thread.finished = True
        parent = thread.parent
        if parent is not None:
            parent.branches -= 1
            if not parent.branches:
                parent.at = self.fc.events[parent.resume].next
                self.ready.append(parent)

    def _advance(self, thread):
        fc = self.fc
        for step in range(1, 200):
            if thread.at == evfl.NONE and thread.calls:
                thread.at = thread.calls.pop()
                continue
            if thread.at == evfl.NONE or (thread.at == thread.join and not thread.calls):
                self._finish(thread)
                return step
            event = fc.events[thread.at]
            if isinstance(event, evfl.ForkEvent):
                thread.resume, thread.branches = event.join, len(event.forks)
                self.ready.extend(Thread(fork, join=event.join, parent=thread) for fork in event.forks)
                return step
            if isinstance(event, evfl.SubFlowEvent):
                if event.flowchart in ("", fc.name):
                    self.entries.append(event.entry_point)
                    thread.calls.append(event.next)
                    thread.at = fc.entry_point(event.entry_point).main_event
                    continue
                call = (event.flowchart, event.entry_point)
                assert call in self.calls, ("call target the native movie never uses", fc.name, event)
                self.trace.append((event.name, "SubFlow", call))
                thread.at = event.next
                return self._sleep(thread, 1, step)
            if isinstance(event, evfl.SwitchEvent):
                thread.at = dict(event.cases).get(self._query(event), evfl.NONE)
                continue
            assert isinstance(event, evfl.ActionEvent), ("unmodeled event in a native cut", fc.name, event)
            thread.at = event.next
            wait = self._act(event)
            if isinstance(wait, Request):
                thread.request = wait
                self.creating.append(thread)
                return step
            if wait:
                return self._sleep(thread, wait, step)
        raise AssertionError(("cut loops without waiting", fc.name, self.trace[-5:]))

    def _query(self, event):
        actor = self.fc.actors[event.actor]
        op = actor.queries[event.query]
        params = event.params or {}
        if (actor.name, op) == ("Player_Event", "EventQueryPlayerIsEquipWeapon"):
            assert params["WeaponSlot"] == 0, event
            weapon = self.data[EQUIPPED] if self.reading == "selected" else held(self)
            return 0 if weapon == params["ArmorName"] else 1
        assert actor.name == "GameDataActor", ("unmodeled query", actor.name, op, event)
        value = self.data[params["GameDataName"]]
        if op == "EventQueryIsGameDataBool":
            return 0 if value else 1
        assert op == "EventQueryIsGameDataInt", ("unmodeled query", op, event)
        return 0 if value == params["Value"] else 1 if value < params["Value"] else 2

    def _act(self, event):
        """None to continue, frames to sleep, or the request a creation wait blocks on."""
        actor = self.fc.actors[event.actor]
        op = actor.actions[event.action]
        params = event.params or {}
        self.trace.append((event.name, op, params))
        if op == "EventWait":
            assert actor.name in ("EventSystemActor", "GameSystemActor"), (actor.name, event)
            return params["Frames"]
        if actor.name == "GameDataActor":
            if op == "EventTriggerSetGameDataBool":
                name, value = params["GameDataName"], params["Value"]
            else:
                assert op == "EventTriggerCopyGameDataString64", (op, event)
                name, value = params["DstGameDataName"], self.data[params["SrcGameDataName"]]
            assert name != EQUIPPED and not name.startswith(SAVED), ("cut rewrites saved equipment", event)
            self.data[name] = value
            return None
        if actor.name != "Player_Event":
            assert actor.name in FINITE, ("unmodeled actor", actor.name, op, event)
            return 1 if params.get("IsWaitEnd") else None
        if op == "EventTriggerPlayerRequestCreateDynamicEquipmentNoRelationPouch":
            self._request(params["EquipmentActorName"], "prop")
        elif op == "EventTriggerEquipmentUserRequestCreateStaticEquipment":
            self._request(params["EquipmentActorName"], "static")
        elif op == "EventTriggerPlayerEquipDynamicEquipmentFromPouch":
            selected = self.data[EQUIPPED]
            if selected and self.data.get(f"PouchData.{selected}.StockNum", 0) >= 1:
                self._request(selected, "pouch")
            else:
                self.invalid.append(("pouch", selected))
        elif op == "EventWaitCreationFinishedEquipment":
            request = next((request for request in self.requests if not request.waited), None)
            if request is None:
                raise UnsatisfiedEquipmentWait(
                    f"{self.fc.name}/{event.name}: creation wait without a valid create/restore request; "
                    f"selected {self.data[EQUIPPED]!r}, held {self.held!r}, created {self.created!r}"
                )
            request.waited = True
            return None if request.done else request
        else:
            assert op in PLAYER_FINITE, ("unmodeled player action", op, event)
            return 1 if params.get("IsWaitEnd") else None
        return None

    def _request(self, actor, source):
        if not actor:
            self.invalid.append((source, actor))
            return
        self.created.append((source, actor))
        if self.data.get(f"PouchData.{actor}.StockNum", 0) < 1:
            self.unowned.append((source, actor))
        self.requests.append(Request(actor, source))


@pytest.fixture(scope="module")
def charts(romfs):
    """(native, registered runtime) per arrival movie, the registered era chain, and both boot sources."""
    registered = master_sword.changes({master_sword.PEDESTAL: "Boomerang"})
    out = {}
    for flow in FLOWS:
        data = native(romfs, flow)
        patched = registered[f"Event/EventFlow/{flow}.bfevfl.zs"](data)
        out[flow] = evfl.read(data).flowchart, evfl.read(patched).flowchart
    era = native(romfs, "ReplaceEquipmentForEraChange")
    for step in (equipment.changes(), registered):
        era = step[equipment.FLOW](era)
    out["era"] = evfl.read(era).flowchart
    out["door"] = evfl.read(registered[master_sword.DOOR](native(romfs, "DoorOfTime"))).flowchart
    out["boot"] = evfl.read(native(romfs, "Market_Child_Field_ChildToAdult")).flowchart
    return out


def arrival(era, candidate, ownership):
    """The saved state either movie boots with: a child-to-adult departure through the registered era chain."""
    state = initial(candidate, owned=True, child=True)
    state[f"PouchData.{KOKIRI}.StockNum"] = 1
    for blade in master_sword.ADULT_BLADES:
        state[f"IsGet.{blade}"], state[f"PouchData.{blade}.StockNum"] = ownership.get(blade, ABSENT)
    run(era, state, {KOKIRI: 1}, child=True)
    return state


def owns(state, blade):
    return state[f"IsGet.{blade}"] is True and state[f"PouchData.{blade}.StockNum"] >= 1


def saved(data):
    return {name: value for name, value in data.items() if name == EQUIPPED or name.startswith(SAVED)}


def external(fc):
    return {
        (event.flowchart, event.entry_point)
        for event in fc.events
        if isinstance(event, (evfl.SubFlowEvent, evfl.SubFlowSwitchEvent)) and event.flowchart not in ("", fc.name)
    }


def operation(fc, event):
    actor = fc.actors[event.actor]
    return actor.queries[event.query] if isinstance(event, evfl.SwitchEvent) else actor.actions[event.action]


def names(cut):
    return [name for name, _, _ in cut.trace]


def held(cut):
    return cut.held[0] if cut.held else ""


def outcome(cut):
    return cut.trace, cut.entries, cut.held, cut.created, cut.data


def retained(flow, entry, selected):
    """Inputs whose native path is already safe, so the runtime must replay it exactly."""
    if entry in ("C01_B", "Gauntlet_Silver_First") or selected == MASTER:
        return True
    # Large-blade arrivals: other leaves the blade alone and EntryPoint0 takes the original C01_B.
    return flow == ARRIVAL and entry in ("EntryPoint0", "other") and selected in LARGE


def test_repeat_draw_boots_both_arrivals_only_after_actual_era_replacement(charts):
    door = charts["door"]
    draw = door.events[door.entry_point("DoorOfTime_Draw").main_event]
    assert operation(door, draw) == "EventQueryHavePlayedEvent", draw
    assert draw.params["EventName"] == "Dm_TimeTemple_0040"
    repeat = door.events[dict(draw.cases)[0]]
    assert operation(door, repeat) == "EventTransition", repeat
    assert repeat.params["EventName"] == "Market_Child_Field_ChildToAdult"
    boot = charts["boot"]
    boots = set()

    def walk(at, replaced):
        while at != evfl.NONE:
            event = boot.events[at]
            if isinstance(event, evfl.SwitchEvent):
                for _, target in event.cases:
                    walk(target, replaced)
                return
            if isinstance(event, evfl.SubFlowEvent):
                replaced |= (event.flowchart, event.entry_point) == (ERA, ERA)
            else:
                assert isinstance(event, evfl.ActionEvent), event
                params = event.params or {}
                assert EQUIPPED not in (params.get("GameDataName"), params.get("DstGameDataName")), event
                if operation(boot, event) == "EventReserveBancChange":
                    boots.add((params["BootEventName"], replaced))
            at = event.next

    walk(boot.entry_point("Market_Child_Field_ChildToAdult").main_event, False)
    assert boots == {(flow, True) for flow in FLOWS}


@pytest.mark.parametrize("blade_state", STATES)
@pytest.mark.parametrize("master_state", STATES)
@pytest.mark.parametrize("candidate", ["", *master_sword.ADULT_BLADES])
def test_actual_era_selects_a_blade_only_with_canonical_ownership(charts, candidate, master_state, blade_state):
    other = candidate if candidate not in ("", MASTER) else BIGGORON
    ownership = {MASTER: STATES[master_state], other: STATES[blade_state]}
    state = arrival(charts["era"], candidate, ownership)
    chosen = candidate or MASTER
    assert state[EQUIPPED] == (chosen if ownership[chosen] == OWNED else ""), state
    for blade in master_sword.ADULT_BLADES:
        assert (state[f"IsGet.{blade}"], state[f"PouchData.{blade}.StockNum"]) == ownership.get(blade, ABSENT)


@pytest.mark.parametrize("flow", FLOWS)
def test_runtime_keeps_every_native_cut_actor_and_call_target(charts, flow):
    control, patched = charts[flow]
    assert {entry.name for entry in control.entry_points} == set(FLOWS[flow])  # every cut is covered below
    assert [entry.name for entry in patched.entry_points] == [entry.name for entry in control.entry_points]
    assert external(patched) == external(control)
    if flow == ARRIVAL:
        assert patched.actors == control.actors  # its guard reuses the movie's own selected-weapon query


@pytest.mark.parametrize("reading", READINGS)
@pytest.mark.parametrize("case", CASES)
@pytest.mark.parametrize("flow,entry", CUTS)
def test_every_arrival_cut_finishes_with_only_owned_selected_equipment(charts, flow, entry, case, reading):
    control, patched = charts[flow]
    calls = external(control)
    before = arrival(charts["era"], *CASES[case])
    selected = before[EQUIPPED]
    assert not selected or owns(before, selected), before  # the era precondition the local guard relies on
    cut = Cut(patched, calls, dict(before), reading=reading).play(entry)
    assert not cut.unowned and not cut.invalid, (cut.created, cut.invalid)
    assert {actor for _, actor in cut.created} <= {selected}, cut.created
    assert all(request.waited for request in cut.requests if request.source != "static"), cut.requests
    assert saved(cut.data) == saved(before)
    if (flow, entry) == (ARRIVAL, "other"):
        assert held(cut) == selected  # native leaves its owned prop for C01's restore
    else:
        assert cut.held == ((selected, "pouch") if selected else None), cut.held
    if flow == GAUNTLET and entry in ("EntryPoint0", "other"):
        assert cut.data[BEFORE_FORCE] == selected
    if entry == "EntryPoint0":
        second = "Gauntlet_Silver_First" if flow == GAUNTLET else "C01_B" if selected in LARGE else "C01"
        assert cut.entries == ["other", second]
    if retained(flow, entry, selected):
        original = Cut(control, calls, dict(before), reading=reading).play(entry)
        assert outcome(cut) == outcome(original)
    else:
        armed = arrival(charts["era"], MASTER, {MASTER: OWNED})
        original = Cut(control, calls, armed, reading=reading).play(entry)
        assert sorted(names(cut)) == sorted(name for name in names(original) if name not in GUARDED[flow])


def test_oracle_rejects_native_unowned_arrival_hazards(charts):
    """Non-vacuity. v3 changed only 0085's other, so C01 ran natively: restore + Event19 with nothing selected."""
    unarmed = arrival(charts["era"], "", {})
    assert unarmed[EQUIPPED] == ""
    control = charts[ARRIVAL][0]
    calls = external(control)
    # EntryPoint0's other already consumed its own (unowned) creation at Event14; Event19 gets no second request.
    for entry in ("C01", "EntryPoint0"):
        with pytest.raises(UnsatisfiedEquipmentWait, match="Event19"):
            Cut(control, calls, dict(unarmed)).play(entry)
    other = Cut(control, calls, dict(unarmed)).play("other")
    assert other.unowned == [("prop", MASTER)]
    assert saved(other.data) == saved(unarmed)
    gauntlet = charts[GAUNTLET][0]
    calls = external(gauntlet)
    for entry in ("other", "EntryPoint0"):
        cut = Cut(gauntlet, calls, dict(unarmed)).play(entry)
        assert cut.unowned == [("static", MASTER)] and cut.held == (MASTER, "static")
        assert saved(cut.data) == saved(unarmed)  # a static story prop is never an ownership grant
    biggoron = arrival(charts["era"], BIGGORON, {BIGGORON: OWNED, MASTER: OWNED})
    cut = Cut(gauntlet, calls, dict(biggoron)).play("other")
    # Native 0088 replaces the selected large blade with an owned static Master; the runtime keeps the blade.
    assert cut.created == [("static", MASTER)] and not cut.unowned
    assert cut.held == (MASTER, "static") and cut.data[EQUIPPED] == BIGGORON
