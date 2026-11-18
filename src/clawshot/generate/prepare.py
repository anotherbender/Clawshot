"""Settings as a seed uses them, and the world they build: the part of the generator other placers (an
Archipelago world) share, kept apart from the fill so it imports only the world and the placement rules."""

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from clawshot.generate import key_families, rewards, tokens
from clawshot.generate.fill import SHOP_ONLY_PREFIX, FillError, Settings
from clawshot.generate.progressive import prepare_spec, restrict_settings
from clawshot.world.load import build_world
from clawshot.world.model import World
from clawshot.world.shops import with_shop_prices, with_shop_slots


def world_spec(spec: Mapping[str, Any], settings: Settings) -> Mapping[str, Any]:
    """The spec cut down to ``settings.areas`` (the regions in those census areas and the area-less start regions,
    whose exits elsewhere then dangle) with ``settings.goal``; the spec unchanged when no areas are given."""
    if not settings.areas:
        return spec
    areas = set(settings.areas)
    regions = [r for r in spec["regions"] if r.get("area") is None or r.get("area") in areas]
    if not any(r.get("area") in areas for r in regions):
        raise FillError(f"no region of the world lies in the areas {sorted(areas)}")
    kept = {name for r in regions for name in r.get("locations", {})}
    locations = {name: info for name, info in spec.get("locations", {}).items() if name in kept}
    return {**spec, "regions": regions, "locations": locations, "goal": settings.goal or spec["goal"]}


def prepare(spec: Mapping[str, Any], settings: Settings) -> tuple[Settings, World]:
    """The settings as a seed uses them, and the world they build.

    With ``dungeon_items`` ``anywhere`` or ``all_anywhere`` the logic setting ``keysanity`` is set too, where the
    world has it.
    ``open_forest`` and the legacy ``skip_mido`` rule flag derive from the same forest mode the overlay patches.
    With ``Token`` shuffled, Gold Skulltulas become Token checks held to their admitted reward families.
    Native setup also uses this compilation before its pool overrides are known. The UI checks return-kit
    construction against the spec; :func:`generate` checks it against the effective native pool before filling.
    """
    spec = rewards.prepare_spec(tokens.prepare_spec(prepare_spec(spec), settings), settings)
    spec = key_families.prepare_spec(spec, settings)
    logic = dict(settings.logic)
    if "open_forest" in spec.get("settings", {}):
        if "open_forest" in logic and logic["open_forest"] != settings.forest:
            raise FillError("open_forest logic must agree with the seed's forest setting")
        logic["open_forest"] = settings.forest
    if "skip_mido" in spec.get("settings", {}):
        skipped = settings.forest == "open"
        if "skip_mido" in logic and logic["skip_mido"] != skipped:
            raise FillError("skip_mido logic must agree with the seed's forest setting")
        logic["skip_mido"] = skipped
    if "door_of_time" in spec.get("settings", {}):
        if "door_of_time" in logic and logic["door_of_time"] != settings.door_of_time:
            raise FillError("door_of_time logic must agree with the seed's door_of_time setting")
        logic["door_of_time"] = settings.door_of_time
        for source, target in (
            ("age_return_door_inventory", "age_return_fill_inventory"),
            ("age_return_door_families", "age_return_fill_families"),
        ):
            modes = spec["settings"].get(source, {})
            if source in spec["settings"]:
                logic[target] = modes.get(settings.door_of_time, spec["settings"][target])
    # Preserve released anywhere recipes. Native keysanity is an inert flag after remake overrides;
    # normalize that namespace only for the new mode, not existing small-key seed strings.
    tables = ("settings", "flags") if settings.dungeon_items == "all_anywhere" else ("settings",)
    has_keysanity = any("keysanity" in spec.get(table, {}) for table in tables)
    if settings.dungeon_items in ("anywhere", "all_anywhere") and has_keysanity:
        if logic.get("keysanity") is False:
            raise FillError(f"dungeon_items = {settings.dungeon_items!r} needs the logic setting keysanity = true")
        logic["keysanity"] = True
    settings = replace(settings, logic=logic)
    if "Shop" in settings.shuffle:
        spec = with_shop_slots(spec, settings.shop_slots)
    spec = with_shop_prices(spec, settings.shuffle, settings.shop_prices, settings.cheap_deku_shield)
    settings = _hold_shop_goods(spec, settings)
    world = build_world(world_spec(spec, settings), settings.logic)
    return key_families.restrict_settings(
        world, restrict_settings(world, tokens.restrict_settings(world, settings))
    ), world


def _hold_shop_goods(spec: Mapping[str, Any], settings: Settings) -> Settings:
    """Keep bought goods on shop shelves; explicit item/type restrictions cannot move them elsewhere."""
    given = settings.item_location_types
    if unsafe := sorted(
        name for name, kinds in given.items() if name.startswith(SHOP_ONLY_PREFIX) and kinds != ("Shop",)
    ):
        raise FillError(f"item_location_types holds bought goods {unsafe} outside shops; they go only to shop shelves")
    if unsafe := sorted(
        kind
        for kind, items in settings.location_type_items.items()
        if kind != "Shop" and any(item.startswith(SHOP_ONLY_PREFIX) for item in items)
    ):
        raise FillError(f"location_type_items gives {unsafe} checks bought goods, which go only to shop shelves")
    if "Shop" not in settings.shuffle:
        return settings
    held = {name: ("Shop",) for name in spec.get("items", {}) if name.startswith(SHOP_ONLY_PREFIX)}
    return replace(settings, item_location_types={**given, **held})
