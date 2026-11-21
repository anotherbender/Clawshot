"""The tracker's cell -> logic item mapping (``data/tracker_logic.toml``) against the generator's own world data."""

import tomllib
from pathlib import Path

import pytest

from clawshot.generate import Settings
from clawshot.patch.logic_world import logic_world
from clawshot.progressive import CHAINS
from clawshot.tracker import logic as tracker_logic
from clawshot.tracker import state as tracker_state
from clawshot.tracker.seeds import DUNGEON_INFO

REMAKE = Path(tracker_logic.__file__).resolve().parents[1] / "data" / "world" / "remake"
# Every shuffle the settings allow, so every item a seed's world can hold is in it.
ALL = Settings(shuffle=("Chest", "Gift", "Scrub", "Shop", "Token"))


@pytest.fixture(scope="module")
def world():
    return logic_world(ALL)[1]


@pytest.fixture(scope="module")
def mapping():
    return tracker_logic.load_mapping()


def cell_ids():
    out = {spec[0] for spec in tracker_state.TIERS}
    out |= {spec[0] for spec in tracker_state.SINGLES}
    out |= {cell_id for cell_id, _, _ in tracker_state.SONGS}
    out |= {cell_id for cell_id, _, _ in tracker_state.REWARDS}
    return out | {"magic", "bottles"}


# 4.1, 4.2
def test_every_progression_item_is_mapped_or_unmapped_with_a_reason(world, mapping):
    mapped = mapping.logic_names()
    missing = sorted(
        name
        for name, item in world.items.items()
        if item.progression and name not in mapped and name not in mapping.unmapped
    )
    assert missing == []
    assert all(isinstance(reason, str) and reason.strip() for reason in mapping.unmapped.values())


def test_mapping_lives_in_the_data_file():
    assert tracker_logic.MAPPING_TOML.name == "tracker_logic.toml"
    data = tomllib.loads(tracker_logic.MAPPING_TOML.read_text(encoding="utf-8"))
    assert {"cells", "bottles", "hearts", "tokens", "dungeon_items", "story", "unmapped"} <= data.keys()


# 4.3
def test_tier_cells_grant_their_chain_copies(mapping):
    tiers = {cell_id: tiers for cell_id, _, tiers, _ in tracker_state.TIERS}
    tiers["magic"] = (("Magic Meter", "Item_FairyBless_MP"), ("Double Magic", "Item_FairyBless_MPDouble"))
    tiers["slingshot"] = (("Fairy Slingshot", "Weapon_Range_SlingShot"),)
    tiers["bow"] = (("Fairy Bow", "Weapon_Range_Bow"),)
    checked = set()
    for chain, chain_tiers in CHAINS.items():
        for n, tier in enumerate(chain_tiers, start=1):
            # The cell and cell tier whose save actor is this chain tier's owned pouch identity.
            [(cell_id, index)] = [
                (cell_id, i)
                for cell_id, cell_tiers in tiers.items()
                for i, (_, actor) in enumerate(cell_tiers, start=1)
                if actor == tier.owned
            ]
            grants = mapping.cells[cell_id].grants(index)
            assert grants.get(chain) == n, (chain, tier.item, cell_id, index, grants)
            checked.add(chain)
    assert checked == set(CHAINS)
    # Longshot = two Progressive Hookshot.
    assert mapping.cells["hookshot"].grants(2) == {"Progressive Hookshot": 2}


# 4.4 (P4.a)
def test_every_logic_name_exists_in_the_world(world, mapping):
    events = {event.name for event in world.events}
    names = set(mapping.logic_names()) | set(mapping.story) | set(mapping.unmapped)
    for dungeon in DUNGEON_INFO:
        for template in mapping.dungeon_items.values():
            names.discard(template.format(dungeon=dungeon))
    assert sorted(n for n in names if n not in world.items and n not in events) == []
    small = mapping.dungeon_items["small_key"]
    assert any(small.format(dungeon=d) in world.items for d in DUNGEON_INFO)


def test_every_cell_id_exists_in_the_tracker_state(mapping):
    assert set(mapping.cells) <= cell_ids()
    for cell in mapping.cells.values():
        assert cell.requires is None or cell.requires in cell_ids()


# 4.5
def test_story_steps_map_to_save_flags_or_are_unmapped(mapping):
    added = set()
    for path in sorted(REMAKE.glob("*.toml")):
        for events in tomllib.loads(path.read_text(encoding="utf-8")).get("events", {}).values():
            added |= {name for name, fields in events.items() if fields.get("new")}
    assert {"Met Child Zelda", "Field Owl Arrival"} <= added
    assert sorted(added - mapping.logic_names() - set(mapping.unmapped)) == []
    assert mapping.story["Met Child Zelda"].flag == "HavePlayedEvent.Dm_HrlField_0020"
    assert mapping.story["Field Owl Arrival"].flag == "HyruleField_ArriveEntrance"
    assert all(step.source for step in mapping.story.values())
