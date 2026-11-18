"""Nine reward slots, distinct from native dungeon/story completion."""

import tomllib
from collections.abc import Mapping
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from clawshot.generate.fill import Settings

TYPE = "DungeonReward"


@cache
def catalog() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "data" / "dungeon_rewards.toml"
    with path.open("rb") as stream:
        return tomllib.load(stream)


def prepare_spec(spec: Mapping[str, Any], settings: "Settings") -> Mapping[str, Any]:
    if not settings.dungeon_rewards and settings.bridge == "vanilla":
        return spec
    data = catalog()
    locations = dict(spec["locations"])
    if settings.dungeon_rewards:
        for name, slot in data["slots"].items():
            if name not in locations:
                continue  # Partial/synthetic worlds need not contain every source.
            info = locations[name]
            if info.get("vanilla") != slot["item"]:
                raise ValueError(f"{name}: reward source changed: {info!r}")
            locations[name] = {key: value for key, value in info.items() if key != "keep_vanilla"} | {"type": TYPE}
    completion = data["completion"]
    helpers = {**spec["helpers"], **completion.get("helpers", {})}
    helpers["can_build_rainbow_bridge"] = data["bridge"][settings.bridge]
    regions = []
    story = data["story_event"]
    world_settings = dict(spec.get("settings", {}))
    if settings.door_of_time == "closed":
        inventory = world_settings.get("age_return_fill_inventory")
        if inventory is not None:
            world_settings["age_return_fill_inventory"] = {**inventory, **completion["closed_pull_inventory"]}
    for region in spec["regions"]:
        rules = dict(region.get("locations", {}))
        for name, rule in completion.get("locations", {}).items():
            if name in rules:
                rules[name] = rule
        events = dict(region.get("events", {}))
        if region["name"] == story["region"]:
            events[story["name"]] = {"rule": story["rule"], "source": story["source"]}
        regions.append({**region, "locations": rules, "events": events})
    return {
        **spec,
        "locations": locations,
        "regions": regions,
        "helpers": helpers,
        "settings": {**world_settings, "clawshot_bridge_count": settings.bridge_count},
    }
