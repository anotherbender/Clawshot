import copy
from collections import Counter

import pytest

from clawshot.generate import Settings, generate
from clawshot.patch import scrubs
from clawshot.world.load import load_spec


def test_only_four_once_families_join_pool_and_repeat_vendors_stay_vanilla():
    spec = load_spec()
    before = copy.deepcopy(spec)
    prepared, settings, _ = scrubs.seed_setup(spec, Settings(shuffle=("Chest", "Scrub")))
    assert spec == before
    changed_types = {
        name
        for name, info in prepared["locations"].items()
        if info.get("type") == "Scrub" and not info.get("keep_vanilla") and not info.get("n64_only")
    }
    assert changed_types == set(scrubs.SALES)
    for name, info in prepared["locations"].items():
        if info.get("type") in ("Scrub", "GrottoScrub") and name not in scrubs.SALES:
            assert info.get("keep_vanilla")
    assert settings.item_location_types["Deku Stick Capacity"] == ("Scrub",)
    assert settings.item_location_types["Deku Nut Capacity"] == ("Scrub",)


def test_fixed_capacity_pool_cannot_leak_to_chests_or_repeat_vendors():
    vanilla = dict(zip(scrubs.SALES, ["Piece of Heart", "Piece of Heart", *scrubs.CAPACITIES], strict=True))
    vanilla.update({"Chest": "Boomerang", "Repeat": "Rupees (5)"})
    locations = {name: {"type": "GrottoScrub", "vanilla": item} for name, item in vanilla.items()}
    locations["Chest"]["type"] = "Chest"
    spec = {
        "start": "Root",
        "goal": "Boomerang",
        "settings": {"starting_age": "child"},
        "items": {name: {"class": "normal"} for name in set(vanilla.values())},
        "regions": [{"name": "Root", "locations": {name: "True" for name in vanilla}}],
        "locations": locations,
    }
    prepared, settings, _ = scrubs.seed_setup(spec, Settings(shuffle=("Chest", "Scrub")))
    expected = Counter(item for name, item in vanilla.items() if name != "Repeat")
    for n in range(20):
        seed = generate(prepared, n, settings)
        assert seed.placements["Repeat"] == "Rupees (5)"
        assert set(seed.shuffled) == {*scrubs.SALES, "Chest"}
        assert Counter(seed.placements[name] for name in seed.shuffled) == expected
        for name, item in seed.placements.items():
            if item in scrubs.CAPACITIES:
                assert name in scrubs.SALES
        assert seed.placements["Chest"] not in scrubs.CAPACITIES


@pytest.mark.parametrize("item", scrubs.CAPACITIES)
@pytest.mark.parametrize("prior", [None, ("Token",), ("Chest", "Scrub")])
def test_capacity_token_hold_preserves_chest_barrier_and_prior_restrictions(item, prior):
    from clawshot.generate import prepare
    from clawshot.generate.fill import allowed

    holds = {} if prior is None else {item: prior}
    spec, settings, _ = scrubs.seed_setup(
        load_spec(), Settings(shuffle=("Chest", "Scrub", "Token"), item_location_types=holds)
    )
    _, world = prepare(spec, settings)
    expected = ("Scrub", "Token") if prior is None else tuple(t for t in prior if t in ("Scrub", "Token"))
    assert settings.item_location_types[item] == expected
    for name in ("LW Deku Scrub Near Bridge", "HF GS Lone Tree", "KF Midos Top Left Chest", "Kak Anju as Child"):
        assert allowed(world, settings, name, item) is (world.locations[name].type in expected)
