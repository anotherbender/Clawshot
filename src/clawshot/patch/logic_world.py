"""A seed's logic world, without the dump (spec ``tracker-in-logic`` D15).

The seed pipeline changes the spec before ``prepare``; two of those changes alter reachability: Gift/NPC shuffle
turns the shopkeeper's free Deku Shield into a placed check (:func:`clawshot.patch.gifts.logic_spec`), and Scrub
shuffle adds each once-sale's wallet tier to its rule (:func:`clawshot.patch.scrubs.logic_spec`). The pipeline
(``gifts.seed_setup``, ``make_seed`` through ``scrubs.seed_setup``) and the tracker both take those steps from the
functions named here, so the world the tracker searches is the one the generator searched. The pipeline's other
spec changes only hold checks vanilla, exclude items or set fill palettes.

    settings, world = logic_world(settings)          # the full remake spec
"""

from collections.abc import Mapping
from typing import Any

from clawshot.generate import Settings, prepare
from clawshot.patch import gifts, scrubs
from clawshot.world.load import load_spec
from clawshot.world.model import World

__all__ = ["logic_spec", "logic_world"]


def logic_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """The spec with the pipeline's reachability-changing steps applied, in the pipeline's order."""
    spec = gifts.logic_spec(spec, settings)
    if scrubs.SHUFFLE in settings.shuffle:
        spec = scrubs.logic_spec(spec, settings)
    return spec


def logic_world(settings: Settings, spec: Mapping[str, Any] | None = None) -> tuple[Settings, World]:
    """The settings as the seed uses them and the world its beatability search ran on. Reads no dump."""
    spec = load_spec() if spec is None else spec
    return prepare(logic_spec(spec, settings), settings)
