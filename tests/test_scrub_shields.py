"""The scrub shield get's equip wait ends (clawshot.patch.scrub_shields, issue #33), on a synthetic helper."""

import copy

import pytest

from clawshot.formats import evfl
from clawshot.patch import bags, scrub_shields
from clawshot.patch.plan import PatchError

ENTRY = "DekuShield_GetAndEquipCheck"
LIMIT = 600  # frames: ten seconds of the get pose counts as the reported freeze


def document():
    """The native helper's shape: category gate, non-equipping add, three slot-4 checks, Deku-only back edge."""
    check = {"WeaponSlot": 4}
    fc = evfl.Flowchart(
        scrub_shields.FLOW,
        actors=[
            evfl.Actor(
                "PouchSystemActor",
                actions=["EventTriggerAddOrRemovePouchContent"],
                queries=["EventQueryCheckPouchContentCategory"],
            ),
            evfl.Actor("Player_Event", queries=["EventQueryPlayerIsEquipWeapon"]),
            evfl.Actor("EventSystemActor", actions=["EventWait"]),
        ],
        events=[
            evfl.SwitchEvent("Event444", 0, 0, [(3, 1)], {"ActorName": evfl.Argument("ActorName")}),
            evfl.ActionEvent(
                "Event442",
                0,
                0,
                2,
                {
                    "Num": 1,
                    "IsEquipDIrect": False,
                    "IsSetMessageTargetActorName": True,
                    "IsGetEvent": False,
                    "Actor": evfl.Argument("ActorName"),
                },
            ),
            evfl.SwitchEvent("Event514", 1, 0, [(1, 3)], {**check, "ArmorName": "Weapon_Shield_Hylian"}),
            evfl.SwitchEvent("Event537", 1, 0, [(1, 4)], {**check, "ArmorName": "Item_Shield_Mirror"}),
            evfl.SwitchEvent("Event509", 1, 0, [(1, 5)], {**check, "ArmorName": "Weapon_Shield_Deku"}),
            evfl.ActionEvent("Event513", 2, 0, 4, {"IsWaitEnd": True, "Frames": 1}),
        ],
        entry_points=[evfl.EntryPoint(ENTRY, 0)],
    )
    return evfl.EventFlowFile(scrub_shields.FLOW, flowchart=fc)


def run(fc, content, equipped):
    """Frames until the helper returns (None: still in the get pose at LIMIT) and the pouch adds made.

    ``equipped`` maps a frame to the slot-4 equipment actor from that frame on. A switch value without a case
    ends the helper, as the native Hylian/Deku exits do; case 0 is "yes", as the game's own gates."""
    index = fc.entry_point(ENTRY).main_event
    frames, adds, strings, held = 0, [], {}, set()
    while index != evfl.NONE:
        event = fc.events[index]
        actor = fc.actors[event.actor]
        if isinstance(event, evfl.SwitchEvent):
            query = actor.queries[event.query]
            if query == "EventQueryCheckPouchContentCategory":
                value = 3
            elif query == "EventQueryPlayerIsEquipWeapon":
                assert event.params["WeaponSlot"] == 4
                now = max((frame for frame in equipped if frame <= frames), default=None)
                value = 0 if now is not None and equipped[now] == event.params["ArmorName"] else 1
            elif query == "EventQueryIsGameDataString64":
                value = 0 if strings.get(event.params["GameDataName"]) == event.params["Value"] else 1
            else:
                assert query == "EventQueryIsExistInPouch"
                value = 0 if event.params["Actor"] in held else 1
            index = dict(event.cases).get(value, evfl.NONE)
            continue
        action = actor.actions[event.action]
        if action == "EventWait":
            frames += event.params["Frames"]
            if frames > LIMIT:
                return None, adds
        elif action == "EventTriggerSetGameDataString64":
            value = event.params["Value"]
            strings[event.params["GameDataName"]] = content if isinstance(value, evfl.Argument) else value
        else:
            assert action == "EventTriggerAddOrRemovePouchContent"
            value = event.params["Actor"]
            adds.append((content if isinstance(value, evfl.Argument) else value, event.params["IsEquipDIrect"]))
            held.add(adds[-1][0])
        index = event.next
    return frames, adds


def patched():
    return evfl.read(scrub_shields.transform(evfl.write(document()))).flowchart


OUTCOMES = {
    "Hylian held": ({0: "Weapon_Shield_Hylian"}, 1),
    "Deku held": ({0: "Weapon_Shield_Deku"}, 1),
    "Mirror held (issue 33 if equipped)": ({0: "Weapon_Shield_Mirror"}, 1),
    "nothing usable (issue 33 otherwise)": ({}, 1),
    "Mirror a frame late": ({2: "Weapon_Shield_Mirror"}, 1),
    "Hylian a frame late": ({2: "Weapon_Shield_Hylian"}, 1),
    "Deku late": ({5: "Weapon_Shield_Deku"}, 1),
    "Mirror never equips during the event": ({1000: "Weapon_Shield_Mirror"}, 1),
}


def test_native_back_edge_rechecks_only_the_deku_shield():
    fc = document().flowchart
    content = "Item_Shield_Mirror"
    assert run(fc, content, {0: "Weapon_Shield_Hylian"})[0] == 0
    assert run(fc, content, {3: "Weapon_Shield_Deku"})[0] == 3
    for equipped in ({0: "Weapon_Shield_Mirror"}, {}, {2: "Weapon_Shield_Hylian"}, {2: "Weapon_Shield_Mirror"}):
        assert run(fc, content, equipped) == (None, [(content, False)])


@pytest.mark.parametrize("content", ["Item_Shield_Mirror", "TBox_Shield_Deku", "TBox_Shield_Hylian"])
@pytest.mark.parametrize("outcome", OUTCOMES)
def test_every_shield_outcome_returns_with_the_native_grant_once(content, outcome):
    equipped, frames = OUTCOMES[outcome]
    assert run(patched(), content, equipped) == (frames, [(content, False)])


@pytest.mark.parametrize("broken", ["mirror_named", "back_edge", "equip_direct", "frames", "missing", "twice"])
def test_stale_helper_refuses_before_mutation(broken):
    doc = document()
    fc = doc.flowchart
    events = {event.name: event for event in fc.events}
    if broken == "mirror_named":
        events["Event537"].params["ArmorName"] = "Weapon_Shield_Mirror"
    elif broken == "back_edge":
        events["Event513"].next = 2
    elif broken == "equip_direct":
        events["Event442"].params["IsEquipDIrect"] = True
    elif broken == "frames":
        events["Event513"].params["Frames"] = 2
    elif broken == "missing":
        events["Event509"].name = "Event510"
    else:
        scrub_shields.patch_flowchart(fc)
    before = copy.deepcopy(doc)
    with pytest.raises(PatchError):
        scrub_shields.patch_flowchart(fc)
    assert doc == before


@pytest.mark.parametrize("bags_first", [False, True])
def test_bag_guards_compose_in_either_order(bags_first):
    data = evfl.write(document())
    steps = (bags.handover_transform, scrub_shields.transform)
    for step in steps if bags_first else reversed(steps):
        data = step(data)
    fc = evfl.read(data).flowchart
    assert any(event.name.startswith(bags.PREFIX) for event in fc.events)
    for content in ("Item_Shield_Mirror", "TBox_Shield_Deku"):
        for equipped, frames in OUTCOMES.values():
            assert run(fc, content, equipped) == (frames, [(content, False)])
