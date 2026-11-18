"""Actual UI Gift presets: native preparation, not the unexpanded overlay alias."""

import pytest

from clawshot.app import presets, validate
from clawshot.generate import Settings
from clawshot.patch import gifts, make_seed
from clawshot.world import load_spec
from clawshot.world.softlocks import audit

pytestmark = pytest.mark.dump


@pytest.fixture(scope="module", params=["Recommended", "Gift", "open Door"])
def native_preset(romfs, request):
    recommended = next(preset["values"] for preset in presets() if preset["id"] == "recommended")
    if request.param == "Gift":
        settings = Settings(shuffle=("Chest", "Gift"))
    else:
        values = recommended | ({"door_of_time": "open"} if request.param == "open Door" else {})
        settings = validate(values)
    spec, settings, step = gifts.seed_setup(romfs, load_spec(), settings)
    return request.param, spec, settings, step


@pytest.mark.parametrize("number", [0, 7, 42])
def test_native_gift_presets_have_no_evidenced_reachable_traps(romfs, native_preset, number):
    name, spec, settings, step = native_preset
    seed = make_seed(romfs, number, settings, spec, extra_steps=[step]).seed
    assert (
        audit(
            seed.world,
            seed.placements,
            regions=(
                "Deku Tree Slingshot Room",
                "Graveyard Dampes Grave",
                "Wasteland Near Colossus",
                "Desert Colossus",
            ),
        )
        == []
    ), (name, number)
