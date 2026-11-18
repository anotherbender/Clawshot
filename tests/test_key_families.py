"""Settings-to-pool contracts for new native key sources and canonical Fortress chest grants."""

from collections import Counter
from dataclasses import replace

import pytest

from clawshot.__main__ import main
from clawshot.app.schema import settings_payload, validate
from clawshot.census import definitions
from clawshot.census.scan import CHEST, Location
from clawshot.generate import FillError, Seed, Settings, prepare
from clawshot.generate import key_families as families
from clawshot.generate.fill import allowed, shuffled_locations
from clawshot.patch import items
from clawshot.patch.key_targets import HIDEOUT
from clawshot.patch.plan import Links, make_plan
from clawshot.world.load import load_spec
from clawshot.world.rules import ADULT, DAY


@pytest.fixture(scope="module")
def spec():
    return load_spec()


def test_jail_setting_roundtrips_and_cli_explicit_off_overrides_it(capsys):
    settings = Settings(shuffle_hideout_keys=True)
    assert Settings.from_string(settings.to_string()) == settings
    assert Settings.from_string("CS1").shuffle_hideout_keys is False
    assert main(["--settings", settings.to_string(), "--no-shuffle-hideout-keys", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).shuffle_hideout_keys is False
    assert main(["--shuffle-hideout-keys", "--print-settings"]) == 0
    assert Settings.from_string(capsys.readouterr().out.strip()).shuffle_hideout_keys is True


@pytest.mark.parametrize("mode", ["anywhere", "all_anywhere"])
def test_moving_keys_without_a_named_chest_destination_is_refused(mode):
    with pytest.raises(ValueError, match="shuffle Chest"):
        Settings(shuffle=("Gift",), dungeon_items=mode)
    with pytest.raises(ValueError, match="shuffle Chest"):
        Settings(shuffle=("Gift",), shuffle_hideout_keys=True)


@pytest.mark.parametrize("kind", [families.FLOOR_KEY_SOURCE, families.HIDEOUT_KEY_SOURCE])
def test_internal_key_source_types_cannot_be_used_to_bypass_settings(kind):
    with pytest.raises(ValueError, match="not shuffle kinds"):
        Settings(shuffle=("Chest", kind))


@pytest.mark.parametrize(
    "mode,hideout,floors,jails",
    [
        ("own_dungeon", False, 0, 0),
        ("own_dungeon", True, 0, 4),
        ("anywhere", False, 2, 0),
        ("anywhere", True, 2, 4),
        ("all_anywhere", True, 2, 4),
    ],
)
def test_settings_release_exactly_one_check_per_native_source(spec, mode, hideout, floors, jails):
    settings, world = prepare(spec, Settings(dungeon_items=mode, shuffle_hideout_keys=hideout))
    shuffled = shuffled_locations(world, settings)
    assert len(set(shuffled) & families.FLOOR_SOURCES.keys()) == floors
    assert len(set(shuffled) & families.HIDEOUT_SOURCES.keys()) == jails
    native = [loc for loc in world.locations.values() if loc.vanilla == families.HIDEOUT_KEY and not loc.n64_only]
    assert {loc.name for loc in native} == set(families.HIDEOUT_SOURCES)
    assert "Hideout Gerudo Membership Card" not in shuffled
    assert world.locations["Hideout Gerudo Membership Card"].keep_vanilla
    assert "Gerudo Membership Card" not in [world.locations[name].vanilla for name in shuffled]
    assert spec["locations"][next(iter(families.FLOOR_SOURCES))]["type"] == "Collectable"


def test_resting_census_hashes_link_four_sources_and_event_copies_are_not_checks():
    rows = definitions.load()
    linked = [row for row in rows if (row.oot_randomizer_name or row.name) in families.HIDEOUT_SOURCES]
    assert {row.oot_randomizer_name or row.name for row in linked} == set(families.HIDEOUT_SOURCES)
    assert Counter(row.vanilla_item for row in linked) == Counter(families.HIDEOUT_SOURCES.values())
    assert len({row.id for row in linked}) == 4
    assert all(
        not row.oot_randomizer_name
        for row in rows
        if row.vanilla_item in families.HIDEOUT_SOURCES.values() and row not in linked
    )


def test_native_source_palettes_and_remote_key_destinations_cannot_be_widened(spec):
    settings, world = prepare(spec, Settings(dungeon_items="anywhere", shuffle_hideout_keys=True))
    for source, own_key in families.FLOOR_SOURCES.items():
        assert allowed(world, settings, source, own_key)
        assert allowed(world, settings, source, families.REPLACEMENT)
        for other in [
            "Bow",
            "Progressive Hookshot",
            families.HIDEOUT_KEY,
            *(set(families.FLOOR_SOURCES.values()) - {own_key}),
        ]:
            assert not allowed(world, settings, source, other)
    for source in families.HIDEOUT_SOURCES:
        assert allowed(world, settings, source, families.HIDEOUT_KEY)
        assert allowed(world, settings, source, families.REPLACEMENT)
        assert not allowed(world, settings, source, "Bow")
    assert allowed(world, settings, "KF Midos Top Left Chest", families.HIDEOUT_KEY)
    assert not allowed(world, settings, "Song from Saria", families.HIDEOUT_KEY)
    assert not allowed(
        world, replace(settings, shuffle_hideout_keys=False), "KF Midos Top Left Chest", families.HIDEOUT_KEY
    )
    with pytest.raises(FillError, match="cannot give"):
        prepare(spec, replace(settings, location_type_items={families.FLOOR_KEY_SOURCE: ("Bow",)}))


def test_remote_jail_keys_do_not_stand_in_for_native_guard_and_carpenter_completion(spec):
    _, world = prepare(spec, Settings(shuffle_hideout_keys=True))
    counts = Counter({families.HIDEOUT_KEY: 4})
    card = world.locations["Hideout Gerudo Membership Card"]
    assert not card.rule(counts, ADULT, DAY)
    guards = [event for event in world.events if event.name.startswith("Hideout ") and event.name.endswith(" Gerudo")]
    carpenters = [
        event for event in world.events if event.name.startswith("Hideout ") and event.name.endswith(" Carpenter")
    ]
    assert len(guards) == len(carpenters) == 4
    for guard in guards:
        counts[guard.name] = 1
    for event in carpenters:
        assert event.rule(counts, ADULT, DAY)
        counts[event.name] = 1
    assert card.rule(counts, ADULT, DAY)
    counts[families.HIDEOUT_KEY] = 3
    for event in carpenters:
        assert not event.rule(counts, ADULT, DAY)


def test_fortress_chest_uses_canonical_credit_even_inside_fortress(spec):
    settings, world = prepare(spec, Settings(shuffle_hideout_keys=True))
    chest = Location(
        id=901,
        kind=CHEST,
        area="GerudoFortress",
        room=None,
        files=("Banc/GerudoFortress/Synthetic_Static.bcett.byml.zs",),
        ages="adult",
        position=(0.0, 0.0, 0.0),
        actor="Obj_TBox_A_01",
        vanilla_item="Item_Dungeon_SmallKey",
        event=None,
        has_save_flag=True,
    )
    name = "GF Chest"
    seed = Seed(world, 18, settings, {name: families.HIDEOUT_KEY}, [name], [[name]])
    plan = make_plan(seed, Links({name: [chest]}, {}, []), items.load(), {})
    assert len(plan.changes) == 1 and not plan.unchanged
    assert plan.changes[0].named_key == HIDEOUT.id
    assert plan.changes[0].old_actor == plan.changes[0].new_actor == "Item_Dungeon_SmallKey"


def test_app_exposes_jail_setting_and_refuses_a_replayed_no_chest_recipe(spec):
    payload = settings_payload(validate({"shuffle_hideout_keys": True}, spec=spec))
    assert payload["values"]["shuffle_hideout_keys"] is True
    assert Settings.from_string(payload["settings_string"]).shuffle_hideout_keys is True
    with pytest.raises(ValueError, match="shuffle Chest"):
        validate({"shuffle": ["Gift"], "shuffle_hideout_keys": True}, spec=spec)
