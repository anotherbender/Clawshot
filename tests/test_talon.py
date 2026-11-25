"""Talon's Cucco game presentation for a moved first prize, on synthetic flows, placements and messages."""

import pytest

from clawshot.census.gifts import reachable
from clawshot.formats import byml, evfl, msbt, sarc
from clawshot.formats.byml import U64
from clawshot.formats.msbt import Msbt, Tag
from clawshot.patch import talon, text
from clawshot.patch.plan import PatchError

NONE = evfl.NONE
TALK, CLEAR, POUCH = 0, 1, 2  # actor indices in the fixture


def say(name, label, next_event=NONE):
    return evfl.ActionEvent(name, TALK, 0, next_event, {"MessageId": f"EventFlowMsg/{talon.TALON}:{label}"})


def flow():
    clear = {"GameDataName": talon.CLEAR_FLAG, "Index": -1}
    look = {"TurnTarget": 3, "TurnTargetActorName": talon.PROP, "TurnTargetInstanceName": talon.PROP_NAME}
    return evfl.EventFlowFile(
        talon.FLOW,
        flowchart=evfl.Flowchart(
            talon.FLOW,
            [
                evfl.Actor(talon.TALON, actions=["EventTalk"], queries=["EventQueryIsOnRecentTalkFlag"]),
                evfl.Actor("GameDataActor", queries=["EventQueryIsGameDataBool"]),
                evfl.Actor("PouchSystemActor", queries=["EventQueryHasRuppe", "EventQueryIsAnyBottleEmpty"]),
            ],
            [
                evfl.SwitchEvent("Event263", TALK, 0, [(0, 4), (1, 1)]),  # 0
                evfl.SubFlowEvent("Event340", "NpcCommon", "SuggestCamera_Start_NPCLookOnly", 2, look),
                say("Event125", "Talk_30", 3),
                evfl.SubFlowEvent("Event341", "NpcCommon", "SuggestCamera_Reset_NPCLookOnly", 4, {"TurnTarget": 2}),
                evfl.SubFlowEvent("Event68", "", "Minigame_FindOutCucco_Start"),
                say("Event124", "Talk_29", 0),  # 5
                say("Event411", "Talk_29", 7),
                evfl.SwitchEvent("Event315", CLEAR, 0, [(0, 9), (1, 8)], dict(clear)),
                say("Event413", "Talk_30", 9),
                evfl.SwitchEvent("Event325", CLEAR, 0, [(0, 10), (1, 15)], dict(clear)),
                evfl.SwitchEvent("Event58", POUCH, 0, [(0, 11), (1, 17)], {"Value": talon.SALE_PRICE}),  # 10
                evfl.SwitchEvent("Event61", POUCH, 1, [(0, 12), (1, 17)]),
                evfl.SubFlowEvent(
                    "Event205", "NpcCommon", "NpcCommon_HandOver_PlayerToNpc", 13, {"PaidRupee": -talon.SALE_PRICE}
                ),
                say("Event64", "Talk_12", 14),
                evfl.SubFlowEvent(
                    "Event244", "Dm_SY_GetInEvent", "GetInEventInBottle", NONE, {"ActorName": talon.MILK}
                ),
                say("Event206", "Talk_09_2", 16),  # 15
                evfl.SubFlowEvent(
                    "Event23", "NpcCommon", "NpcCommon_HandOver_NpcToPlayer_NoDisplay", 17, {"ReveiveItem": "Item_X"}
                ),
                say("Event43", "Talk_28"),
            ],
            [
                evfl.EntryPoint("Ready", 5, [1, 3, 4]),
                evfl.EntryPoint("Recap", 6),
                evfl.EntryPoint("Minigame_FindOutCucco_Start", 9),
                evfl.EntryPoint("Sale", 10),
            ],
        ),
    )


def index(fc, name):
    return next(i for i, event in enumerate(fc.events) if event.name == name)


def live(fc):
    return {fc.events[i].name for entry in fc.entry_points for i in reachable(fc, entry.main_event)}


def test_moved_prize_skips_the_prop_beat_and_the_recap_line_and_nothing_else():
    source = evfl.write(flow())
    old = evfl.read(source).flowchart
    after = evfl.read(talon.patch_flow(source))
    fc = after.flowchart
    assert fc.events[index(fc, "Event263")].cases == [(0, index(fc, "Event68")), (1, index(fc, "Event68"))]
    assert fc.events[index(fc, "Event315")].cases == [(0, index(fc, "Event325")), (1, index(fc, "Event325"))]
    assert [o.name for o, n in zip(old.events, fc.events, strict=True) if o != n] == ["Event263", "Event315"]
    assert (fc.actors, fc.entry_points) == (old.actors, old.entry_points)
    assert live(fc) == live(old) - set(talon.SKIPPED)
    assert {"Event68", "Event325", "Event244", "Event43"} <= live(fc)
    assert evfl.read(evfl.write(after)) == after
    with pytest.raises(PatchError, match="prop beat"):
        talon.patch_flow(evfl.write(after))


def _fault(fc, fault):
    if fault == "instance":
        fc.events[1].params["TurnTargetInstanceName"] = "Other_Milk"
    elif fault == "second look":
        fc.events[3].params["TurnTargetActorName"] = talon.PROP
    elif fault == "talk elsewhere":
        fc.events[17].params["MessageId"] = f"EventFlowMsg/{talon.TALON}:Talk_30"
    elif fault == "price":
        fc.events[12].params["PaidRupee"] = -20
    elif fault == "sale item":
        fc.events[14].params["ActorName"] = "Item_Bottle_Fairy"
    elif fault == "entry":
        fc.entry_points.append(evfl.EntryPoint("Showcase", 8))
    elif fault == "recap target":
        fc.events[7].cases = [(0, 10), (1, 8)]
    else:
        fc.events[3].name = "Event999"


@pytest.mark.parametrize(
    ("fault", "match"),
    [
        ("instance", "prop beat"),
        ("second look", "prop references"),
        ("talk elsewhere", "prize lines"),
        ("price", "milk sale"),
        ("sale item", "milk sale"),
        ("entry", "way into Event413"),
        ("recap target", "rules recap"),
        ("renamed", r"events: \['Event341'\] missing"),
    ],
)
def test_refuses_a_changed_native_shape(fault, match):
    file = flow()
    _fault(file.flowchart, fault)
    with pytest.raises(PatchError, match=match):
        talon.patch_flow(evfl.write(file))


def _link(dst):
    return {"Dst": U64(dst), "Gyaml": "Reference", "Name": "Reference", "Src": U64(talon.TALON_HASH)}


def banc():
    anchor = {"Gyaml": "DestinationAnchor", "Hash": U64(7), "Name": "Synthetic_Anchor"}
    host = {"Gyaml": talon.TALON, "Hash": U64(talon.TALON_HASH), "Links": [_link(7), _link(talon.PROP_HASH)]}
    prop = {"Gyaml": talon.PROP, "Hash": U64(talon.PROP_HASH), "Name": talon.PROP_NAME, "IsPhysicsStable": True}
    for actor in (anchor, host, prop):
        actor["Phive"] = {"Placement": {"ID": actor["Hash"]}}
    return {"Actors": [anchor, host, prop], "AiGroups": [], "FarDeleteGroups": [], "SimultaneousGroups": []}


def test_banc_removes_only_the_prop_and_talons_reference():
    tree = banc()
    after = byml.read(talon.patch_banc(byml.write(tree)))
    anchor, host, _ = tree["Actors"]
    assert after["Actors"] == [anchor, {**host, "Links": [_link(7)]}]
    assert {k: v for k, v in after.items() if k != "Actors"} == {k: v for k, v in tree.items() if k != "Actors"}
    with pytest.raises(PatchError, match="table prop"):
        talon.patch_banc(byml.write(after))


@pytest.mark.parametrize(
    ("fault", "match"),
    [
        ("twice", "table prop"),
        ("other model", "table prop"),
        ("presence", "table prop"),
        ("unlinked", "reference to the prop"),
        ("other linker", "outside Talon's links"),
        ("group", "outside Talon's links"),
    ],
)
def test_banc_refuses_a_changed_prop_or_other_references(fault, match):
    tree = banc()
    anchor, host, prop = tree["Actors"]
    if fault == "twice":
        tree["Actors"].append(dict(prop))
    elif fault == "other model":
        prop["Gyaml"] = "Item_Bottle_Milk"
    elif fault == "presence":
        prop["Presence"] = {"FlagName": "Synthetic", "IsCheckLazy": False, "IsNegation": False}
    elif fault == "unlinked":
        host["Links"] = [_link(7)]
    elif fault == "other linker":
        anchor["Links"] = [_link(talon.PROP_HASH)]
    else:
        tree["AiGroups"] = [{"References": [{"Id": "Synthetic", "Reference": U64(talon.PROP_HASH)}]}]
    with pytest.raises(PatchError, match=match):
        talon.patch_banc(byml.write(tree))


VOICE, FACE, RUBY = Tag(3, 0, b"\x0f\x00\x00"), Tag(4, 0, b"\x08\x00Happy_00\x00"), Tag(0, 0, b"\x01\x00\x03\x00x")


def archive(labels=("Talk_29", "Talk_09_2", "Talk_28", "Talk_30", "Talk_11")):
    lines = {
        "Talk_29": [Tag(3, 0, b"\x00\x00\x00"), "Synthetic rules, a milky prize"],
        "Talk_09_2": [VOICE, FACE, "Synthetic milk", Tag(5, 1), " hand-over"],
        "Talk_28": [VOICE, RUBY, "Synthetic", " refill"],
        "Talk_30": [VOICE, "Synthetic free bottle"],
        "Talk_11": [VOICE, "Synthetic repeat milk"],
    }
    messages = Msbt({label: lines[label] for label in labels}, buckets=5)
    return sarc.write({talon.MESSAGES: msbt.write(messages), "Other.bin": b"unrelated"})


def test_text_says_neutral_english_in_the_native_opening_style():
    source = archive()
    files = sarc.read(talon.patch_text(source))
    messages = msbt.read(files[talon.MESSAGES]).messages
    native = msbt.read(sarc.read(source)[talon.MESSAGES]).messages
    assert messages["Talk_29"][0] == Tag(3, 0, b"\x00\x00\x00")
    assert messages["Talk_09_2"][:2] == [VOICE, FACE]
    assert messages["Talk_28"][0] == VOICE
    assert RUBY not in messages["Talk_28"]
    for label, line in talon.LINES.items():
        said = msbt.plain(messages[label])
        assert said.replace("\n", " ") == line
        assert all(len(row) <= talon.WIDTH for row in said.split("\n"))
        assert said.count("\n") < talon.ROWS
        assert text.PAGE_BREAK not in messages[label]
    for label in ("Talk_30", "Talk_11"):
        assert messages[label] == native[label]
    assert files["Other.bin"] == b"unrelated"
    assert "milk" not in " ".join(msbt.plain(messages[label]) for label in ("Talk_29", "Talk_09_2")).lower()
    assert str(talon.SALE_PRICE) in msbt.plain(messages["Talk_28"])


def test_text_refuses_a_missing_line_or_file():
    with pytest.raises(PatchError, match="no messages labelled"):
        talon.patch_text(archive(("Talk_29", "Talk_09_2", "Talk_30")))
    with pytest.raises(PatchError, match="no message file"):
        talon.patch_text(sarc.write({"Other.bin": b"unrelated"}))


def test_changes_only_for_a_moved_prize_on_every_language(tmp_path):
    (tmp_path / "Mals").mkdir()
    for language in ("SynA", "SynB"):
        (tmp_path / text.archive_path(language)).touch()
    out = talon.changes(tmp_path, {talon.CHECK: "Boomerang", "Other Check": "Bottle with Milk"})
    assert out == {
        talon.FLOW_PATH: talon.patch_flow,
        talon.BANC_PATH: talon.patch_banc,
        text.archive_path("SynA"): talon.patch_text,
        text.archive_path("SynB"): talon.patch_text,
    }
    assert talon.changes(tmp_path, {talon.CHECK: talon.VANILLA}) == {}
    assert talon.changes(tmp_path, {"Other Check": "Boomerang"}) == {}
