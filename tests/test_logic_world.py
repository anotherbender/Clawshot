"""The shared, dump-free builder of a seed's logic world (``clawshot.patch.logic_world``, spec D15)."""

import copy
from dataclasses import replace

import pytest

from clawshot.generate import Settings, prepare
from clawshot.patch import gifts, logic_world, scrubs
from clawshot.world.load import load_spec

SHUFFLES = {
    "chest": ("Chest",),
    "gift": ("Chest", "Gift"),
    "npc": ("Chest", "NPC"),
    "scrub": ("Chest", "Scrub"),
    "gift_scrub": ("Chest", "Gift", "Scrub"),
}


def signature(world):
    """Everything about a world that decides reachability, in a comparable form."""
    return {
        "regions": sorted(world.regions),
        "exits": sorted((e.parent, e.target, e.rule.text) for r in world.regions.values() for e in r.exits),
        "events": sorted((e.name, e.region, e.rule.text) for e in world.events),
        "locations": sorted((n, loc.region, loc.type, loc.rule.text) for n, loc in world.locations.items()),
        "items": sorted(world.items.items()),
        "start_items": world.start_items,
        "start": world.start,
        "goal": world.goal.text,
        "settings": sorted((k, repr(v)) for k, v in world.settings.items()),
    }


@pytest.fixture(scope="module")
def spec():
    return load_spec()


def no_dump(monkeypatch):
    """Any read of a romfs fails the test."""
    monkeypatch.delenv("OOT_ROMFS", raising=False)

    def fail(*args, **kwargs):
        raise AssertionError("the logic world read the dump")

    import importlib

    from clawshot.formats import zsdic

    census_gifts = importlib.import_module("clawshot.census.gifts")
    census_scan = importlib.import_module("clawshot.census.scan")

    monkeypatch.setattr(census_scan, "scan", fail)
    monkeypatch.setattr(census_scan, "read_romfs_byml", fail)
    monkeypatch.setattr(census_gifts, "scan_gifts", fail)
    monkeypatch.setattr(zsdic.Dictionaries, "from_romfs", fail)
    monkeypatch.setattr(gifts, "scan_gifts", fail)
    monkeypatch.setattr(gifts, "scan", fail)
    monkeypatch.setattr(gifts, "read_romfs_byml", fail)


# 2.1 (P2.a)
@pytest.mark.parametrize("prices", ["vanilla", "fixed"])
def test_scrub_logic_spec_is_seed_setups_spec_change(spec, prices):
    settings = Settings(shuffle=("Chest", "Scrub"), scrub_prices=prices)
    before = copy.deepcopy(spec)
    changed = scrubs.logic_spec(spec, settings)
    assert spec == before
    prepared, _, _ = scrubs.seed_setup(spec, settings)
    assert changed == prepared
    for name in scrubs.SALES:
        assert changed["locations"][name]["type"] == scrubs.SHUFFLE


# 2.2
@pytest.mark.parametrize("label", SHUFFLES)
def test_logic_world_needs_no_dump(monkeypatch, spec, label):
    no_dump(monkeypatch)
    settings = Settings(shuffle=SHUFFLES[label])
    _, world = logic_world.logic_world(settings, spec)
    gift = "Gift" in settings.shuffle or "NPC" in settings.shuffle
    assert (gifts.SHOPKEEPER_CHECK in world.locations) is gift
    shop_events = {e.name for e in world.regions[gifts.SHOPKEEPER_REGION].events}
    assert ("Deku Shield" not in shop_events) is gift
    _, plain = prepare(spec, settings)
    for name in scrubs.SALES:
        changed = world.locations[name].rule.text != plain.locations[name].rule.text
        assert changed is ("Scrub" in settings.shuffle)


def test_logic_world_loads_the_spec_when_none_is_given(monkeypatch, spec):
    no_dump(monkeypatch)
    calls = []
    monkeypatch.setattr(logic_world, "load_spec", lambda: calls.append(1) or spec)
    logic_world.logic_world(Settings())
    assert calls == [1]


def test_logic_world_takes_both_steps_from_their_modules(monkeypatch, spec):
    calls = []
    real_gift, real_scrub = gifts.logic_spec, scrubs.logic_spec
    monkeypatch.setattr(gifts, "logic_spec", lambda s, st: calls.append("gift") or real_gift(s, st))
    monkeypatch.setattr(scrubs, "logic_spec", lambda s, st: calls.append("scrub") or real_scrub(s, st))
    logic_world.logic_world(Settings(shuffle=("Chest", "Gift", "Scrub")), spec)
    assert calls == ["gift", "scrub"]


# 2.3
def test_scrub_seed_setup_uses_the_shared_step(monkeypatch, spec):
    calls = []
    real = scrubs.logic_spec
    monkeypatch.setattr(scrubs, "logic_spec", lambda s, st: calls.append(1) or real(s, st))
    scrubs.seed_setup(spec, Settings(shuffle=("Chest", "Scrub")))
    assert calls == [1]


def test_gift_logic_spec_is_the_shopkeeper_step_only_for_gift_or_npc(spec):
    assert gifts.logic_spec(spec, Settings(shuffle=("Chest",))) == spec
    shop = gifts.shopkeeper_spec(spec)
    for shuffle in (("Gift",), ("NPC",), gifts.GIFT_TYPES):
        assert gifts.logic_spec(spec, Settings(shuffle=shuffle)) == shop


@pytest.mark.dump
def test_gift_seed_setup_uses_the_shared_step(monkeypatch, romfs, spec):
    calls = []
    real = gifts.logic_spec
    monkeypatch.setattr(gifts, "logic_spec", lambda s, st: calls.append(1) or real(s, st))
    gifts.seed_setup(romfs, spec, Settings(shuffle=("Chest", "Gift")))
    assert calls == [1]


# 2.4: synthetic-spec variant (no dump): the pipeline's spec steps in its own order, then prepare.
@pytest.mark.parametrize("label", SHUFFLES)
def test_pipeline_spec_steps_give_the_logic_world(spec, label):
    settings = Settings(shuffle=SHUFFLES[label])
    piped = gifts.logic_spec(spec, settings)
    effective = replace(
        settings,
        shuffle=tuple(dict.fromkeys(t for s in settings.shuffle for t in (gifts.GIFT_TYPES if s == "Gift" else (s,)))),
    )
    if "Scrub" in settings.shuffle:
        piped, effective, _ = scrubs.seed_setup(piped, effective)
    _, piped_world = prepare(piped, effective)
    _, world = logic_world.logic_world(settings, spec)
    assert signature(world) == signature(piped_world)


class _Captured(Exception):
    pass


# 2.4: the world make_seed hands to generate, on the player's dump.
@pytest.mark.dump
@pytest.mark.parametrize("label", SHUFFLES)
def test_make_seed_searches_the_logic_world(monkeypatch, romfs, spec, label):
    import clawshot.patch as patch

    captured = {}

    def capture(spec, seed, settings, **kwargs):
        captured.update(spec=spec, settings=settings)
        raise _Captured

    monkeypatch.setattr(patch, "generate", capture)
    settings = Settings(shuffle=SHUFFLES[label])
    given, steps = spec, ()
    if "Gift" in settings.shuffle or "NPC" in settings.shuffle:
        given, settings, step = gifts.seed_setup(romfs, spec, settings)
        steps = (step,)
    with pytest.raises(_Captured):
        patch.make_seed(romfs, 1, settings, given, extra_steps=steps)
    _, searched = prepare(captured["spec"], captured["settings"])
    _, world = logic_world.logic_world(captured["settings"], spec)
    assert signature(world) == signature(searched)


# 2.5 (P2.b)
@pytest.mark.parametrize("label", ["gift", "gift_scrub"])
def test_user_and_effective_gift_settings_give_the_same_world(spec, label):
    user = Settings(shuffle=SHUFFLES[label])
    effective = replace(
        user, shuffle=tuple(dict.fromkeys(t for s in user.shuffle for t in (gifts.GIFT_TYPES if s == "Gift" else (s,))))
    )
    assert "Gift" not in effective.shuffle
    assert signature(logic_world.logic_world(user, spec)[1]) == signature(logic_world.logic_world(effective, spec)[1])
