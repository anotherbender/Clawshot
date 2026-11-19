"""The public kept-Mido overlay must retain his equipment gate after early Zelda."""

import pytest
from test_door_stage import evaluate, indexed

from clawshot.formats import byml, rstb, zsdic
from clawshot.generate import Settings
from clawshot.patch import make_seed, write_seed
from clawshot.patch import mido_schedule as patch
from clawshot.save import key

pytestmark = pytest.mark.dump
SCHEDULE = "Component/AIScheduleParam/Npc_Kokiri_Mido_Child.game__component__AIScheduleParam.bgyml"
GAME_DATA = "GameData/GameDataList.Product.110.byml.zs"
BLOCKER = "KokiriForest_Npc_Kokiri_Mido_Child_Blocker"
CASTLE_STEP = "Step_Goto_HyruleCastle"


@pytest.fixture(scope="module")
def kept_overlay(romfs, tmp_path_factory):
    out = tmp_path_factory.mktemp("mido-castle") / "out"
    settings = Settings(forest="closed_deku", fast_start=("intro", "saria", "deku_tree", "kaepora"))
    generated = make_seed(romfs, 35, settings)
    written = write_seed(generated, romfs, out)
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)

    def resource(path):
        # The runtime uses a mod resource when present and the original otherwise.
        source = out / "romfs" / path
        data = (source if source.is_file() else romfs / path).read_bytes()
        return dictionaries.decompress(path, data) if path.endswith(".zs") else data

    return resource, {file.path: file for file in written}


def test_early_zelda_cannot_select_the_nonclearing_late_talk_while_mido_blocks(kept_overlay):
    resource, _ = kept_overlay
    schedule = byml.read(resource(SCHEDULE))
    [late] = [
        row
        for row in schedule["ConditionalSchedule"]
        if any("Npc_Kokiri_Mido_Child_C5_T." in event.get("EventName", "") for event in row.get("EventEntry", ()))
    ]
    state = {CASTLE_STEP: "Complete", BLOCKER: True}
    assert not evaluate(indexed(byml.read(resource(GAME_DATA))), key(late["ConditionFlag"]), state), late


def test_native_schedule_round_trip_changes_only_the_castle_predicate(romfs):
    original = (romfs / SCHEDULE).read_bytes()
    document = byml.load(original)
    assert byml.same(byml.read(byml.dump(document)), document.root)
    changed = byml.load(patch.guard_schedule(original))
    assert changed.byte_order == document.byte_order
    [late] = [row for row in changed.root["ConditionalSchedule"] if row.get("ConditionFlag") == patch.AFTER_CLEAR]
    late["ConditionFlag"] = patch.CASTLE_COMPLETE
    assert byml.same(changed.root, document.root)


def test_native_expression_preserves_all_saved_rows_and_layout(romfs):
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    original = dictionaries.decompress(GAME_DATA, (romfs / GAME_DATA).read_bytes())
    before = byml.read(original)
    changed = byml.read(patch.add_expression(original))
    rows = indexed(changed)
    for castle in before["Data"]["Enum"]:
        if castle["Hash"] == key(CASTLE_STEP):
            for step in castle["RawValues"]:
                for blocked in (False, True):
                    state = {CASTLE_STEP: step, BLOCKER: blocked}
                    assert evaluate(rows, key(patch.AFTER_CLEAR), state) is (step == "Complete" and not blocked)
    [added] = [row for row in changed["Data"]["BoolExp"] if row["Hash"] == key(patch.AFTER_CLEAR)]
    changed["Data"]["BoolExp"].remove(added)
    assert byml.same(changed, before)


def test_public_writer_keeps_native_schedule_allocation_and_accounts_for_game_data(kept_overlay):
    resource, written = kept_overlay
    schedule = written[SCHEDULE]
    assert schedule.new_size <= schedule.size <= schedule.entry
    assert schedule.new_entry == schedule.entry
    table = rstb.read(resource(rstb.TABLE_PATH))
    assert table.get(SCHEDULE) == schedule.entry
    game_data = written[GAME_DATA]
    assert table.get(GAME_DATA) == game_data.new_entry
    assert game_data.new_entry >= rstb.required_size(GAME_DATA, game_data.new_size)


def test_public_open_forest_keeps_the_native_schedule_and_bypassed_wall(romfs, tmp_path):
    out = tmp_path / "open"
    generated = make_seed(romfs, 35, Settings(forest="open", fast_start=("deku_tree",)))
    written = write_seed(generated, romfs, out)
    assert SCHEDULE not in {file.path for file in written}
    assert not (out / "romfs" / SCHEDULE).exists()
    dictionaries = zsdic.Dictionaries.from_romfs(romfs)
    tree = byml.read(dictionaries.decompress(GAME_DATA, (out / "romfs" / GAME_DATA).read_bytes()))
    assert indexed(tree)["Bool"][key(BLOCKER)]["DefaultValue"] is False
    assert key(patch.AFTER_CLEAR) not in indexed(tree)["BoolExp"]
