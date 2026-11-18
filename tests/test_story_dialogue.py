"""A pressed skip may omit speech, never a choice, grant or flag write."""

from copy import deepcopy

import pytest

from clawshot.formats import evfl
from clawshot.formats.zsdic import Dictionaries
from clawshot.generate import Settings
from clawshot.patch import story_dialogue


def scene():
    return evfl.EventFlowFile(
        "Example",
        evfl.Flowchart(
            "Example",
            actors=[
                evfl.Actor("EventSystemActor", actions=["EventWait"]),
                evfl.Actor("NPC", actions=["EventTalk"]),
                evfl.Actor("GameDataActor", actions=["EventTriggerSetGameDataBool"]),
                evfl.Actor("PouchSystemActor", actions=["EventTriggerAddOrRemovePouchContent"]),
            ],
            events=[
                evfl.ActionEvent("Speech1", 1, 0, 1, {"ChoiceNumber": 0, "MessageId": "invented-1"}),
                evfl.ActionEvent("Speech2", 1, 0, 2, {"ChoiceNumber": 0, "MessageId": "invented-2"}),
                evfl.ActionEvent("Flag", 2, 0, 3, {"GameDataName": "Synthetic.Story", "Value": True}),
                evfl.ActionEvent("Choice", 1, 0, 4, {"ChoiceNumber": 2, "MessageId": "invented-choice"}),
                evfl.ActionEvent("Grant", 3, 0, params={"Actor": "SyntheticItem", "Num": 1}),
            ],
            entry_points=[evfl.EntryPoint("Main", 0)],
        ),
    )


def verify_speech_regions(before, after):
    """Audit every entry/path, including untaken choices, without modeling native story conditions."""
    old, new = before.flowchart, after.flowchart
    assert old.entry_points == new.entry_points
    assert len(old.actors) == len(new.actors)
    for a, b in zip(old.actors, new.actors, strict=True):
        restored = deepcopy(b)
        restored.actions = a.actions
        assert restored == a
    for index, original in enumerate(old.events):
        current = new.events[index]
        is_speech = (
            isinstance(original, evfl.ActionEvent)
            and old.actors[original.actor].actions[original.action] in story_dialogue.TALK_ACTIONS
            and original.params.get("ChoiceNumber") == 0
        )
        if not is_speech:
            assert current == original, (index, original, current)
            continue
        if current == original:
            continue
        action = new.actors[current.actor].actions[current.action]
        if action != story_dialogue.START:
            # The last speech in a merged region has only its continuation
            # routed through SkipEnd. Its original action still executes unskipped.
            end = new.events[current.next]
            assert new.actors[end.actor].actions[end.action] == story_dialogue.END
            restored = deepcopy(current)
            restored.next = end.next
            assert restored == original
            continue
        node = current.next
        speech = []
        while True:
            event = new.events[node]
            kind = new.actors[event.actor].actions[event.action]
            if kind == story_dialogue.END:
                assert event.params["SpecialEventActionType"] == 4
                break
            assert kind in story_dialogue.TALK_ACTIONS
            assert event.params["ChoiceNumber"] == 0
            speech.append(event)
            node = event.next
        assert speech
        # The entire skipped region is speech only. Both normal and skipped
        # execution rejoin the same native continuation after the last speech.
        names = {e.name: e for e in old.events}
        last = speech[-1]
        last_original = original if len(speech) == 1 else names[last.name]
        assert event.next == last_original.next


def test_skip_keeps_choices_and_story_and_reward_actions():
    before = scene()
    after = evfl.read(story_dialogue.patch(evfl.write(before), flow="Example"))
    verify_speech_regions(before, after)
    fc = after.flowchart
    start = fc.events[0]
    end = fc.events[fc.events[1].next]
    assert fc.actors[start.actor].actions[start.action] == story_dialogue.START
    assert end.next == 2
    assert fc.events[2:5] == before.flowchart.events[2:]


def test_opt_in_is_off_and_replays_in_settings():
    assert not Settings().skippable_story
    assert not story_dialogue.changes(enabled=False)
    enabled = Settings(skippable_story=True)
    assert Settings.from_string(enabled.to_string()).skippable_story
    with pytest.raises(ValueError, match="skippable_story must be a boolean"):
        Settings(skippable_story=1)


@pytest.mark.dump
@pytest.mark.parametrize("flow,path", story_dialogue.FLOWS.items())
def test_native_every_skip_region_excludes_all_non_speech_effects(romfs, flow, path):
    relative = f"Event/EventFlow/{path}.bfevfl.zs"
    dictionaries = Dictionaries.from_romfs(romfs)
    data = dictionaries.decompress(relative, (romfs / relative).read_bytes())
    before = evfl.read(data)
    after = evfl.read(story_dialogue.patch(data, flow=flow))
    verify_speech_regions(before, after)
