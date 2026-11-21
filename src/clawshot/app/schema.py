"""UI-neutral presentation metadata around the generator's single settings contract."""

import tomllib
from dataclasses import asdict, fields, replace
from functools import cache
from pathlib import Path

from clawshot.generate import FillError, Settings, hints, prepare
from clawshot.generate.exclusions import validate_exclusions
from clawshot.generate.fill import DUNGEON_ITEM_CHOICES, return_guarantee_conflict, shuffled_locations
from clawshot.generate.names import load as load_names
from clawshot.patch import gamedata, gifts
from clawshot.settings import CATALOG, validate_logic_overrides
from clawshot.world.load import WorldError, build_world, load_spec
from clawshot.world.model import World

METADATA_PATH = Path(__file__).with_name("settings.toml")


@cache
def _world_logic_default(name: str):
    """The bundled world's value for a logic setting; world data does not change while the app runs."""
    spec = load_spec()
    return {**spec.get("settings", {}), **spec.get("tricks", {}), **spec.get("flags", {})}.get(name)


@cache
def _location_metadata() -> dict[str, dict]:
    """Live item checks with readable labels/areas, omitting permanently fixed progression sources.

    Use the same preparation/eligibility predicates as generation with every supported shuffle enabled. This is
    only an upper bound without a dump; recipe-dependent capacity and unshuffled progression remain validated.
    """
    from clawshot.tracker import location_index  # the tracker's logic view imports this module

    catalog, places = load_names(), location_index()
    spec = load_spec()
    world = build_world(spec)
    all_settings = Settings(
        shuffle=("Chest", "Shop", *gifts.GIFT_TYPES, "Scrub", "BossHeart", "Freestanding", "Token"),
        dungeon_items="all_anywhere",
        dungeon_rewards=True,
        shuffle_hideout_keys=True,
        shuffle_master_sword=True,
        logic={"free_time_travel": True},
    )
    preview = gifts.logic_spec(spec, all_settings)
    _, possible = prepare(preview, all_settings)
    all_settings, possible = prepare(
        gifts.restrict_spec(preview, gifts.movable_checks(possible, gifts.load())), all_settings
    )
    moving = set(shuffled_locations(possible, all_settings))
    live = [
        loc
        for loc in world.locations.values()
        if loc.n64_only is None
        and loc.vanilla is not None
        and not (possible.items[possible.locations[loc.name].vanilla].progression and loc.name not in moving)
    ]
    labels, choice_help, option_info = {}, {}, {}
    for loc in sorted(live, key=lambda check: check.name not in catalog):
        readable, area = catalog.get(loc.name), places[loc.name].area
        labels[loc.name] = readable.name if readable else loc.name
        undescribed = f"{loc.type} check in {area}. No player description yet: shown by its world name."
        choice_help[loc.name] = readable.where if readable else undescribed
        option_info[loc.name] = {"area": area, "type": loc.type}
    return {"labels": labels, "choice_help": choice_help, "option_info": option_info}


def _row(key: str, metadata: dict, default, choices: list, names: set[str]) -> dict:
    info = dict(metadata)
    for part in ("label", "kind", "group", "help"):
        if not info.get(part):
            raise ValueError(f"Settings metadata missing {key}.{part}")
    info.update(key=key, default=default, choices=choices)
    labels = info.pop("labels", {})
    unavailable = info.pop("unavailable", {})
    choice_help = info.pop("choice_help", {})
    option_info = info.pop("option_info", {})
    if set(choice_help) != set(info["choices"]) or any(not text.strip() for text in choice_help.values()):
        raise ValueError(f"Choice help missing/stale for {key}")
    for condition in info.get("enabled_when", []):
        operations = {"contains", "equals", "greater_than"} & condition.keys()
        if condition.get("key") not in names or len(operations) != 1 or not condition.get("reason"):
            raise ValueError(f"Invalid dependency metadata for {key}")
    if set(labels) != set(info["choices"]):
        raise ValueError(f"Choice labels missing/stale for {key}: {set(info['choices']) ^ set(labels)}")
    info["options"] = [
        {
            "value": choice,
            "label": labels[choice],
            "help": choice_help[choice],
            "disabled": choice in unavailable,
            "reason": unavailable.get(choice, ""),
            **option_info.get(choice, {}),
        }
        for choice in info["choices"]
    ]
    return info


def _rows() -> list[dict]:
    """Complete validation metadata, including hidden retired settings."""
    metadata = tomllib.loads(METADATA_PATH.read_text(encoding="utf-8"))
    names = {field.name for field in fields(Settings)}
    switches = [key for key, info in metadata.items() if "logic_override" in info]
    rows = metadata.keys() - set(switches)
    if names != rows:
        raise ValueError(f"Settings metadata mismatch: missing={names - rows}, stale={rows - names}")
    choices = {
        "forest": list(CATALOG["forest"]),
        "dungeon_items": list(DUNGEON_ITEM_CHOICES),
        "hint_distribution": list(hints.distributions()),
        "hints": list(hints.MODES),
        "fast_start": [name for name in gamedata.load() if name not in ("mido", "forest_exit")],
    }
    defaults = asdict(Settings())
    result = []
    for field in fields(Settings):
        info = metadata[field.name]
        if info.get("display") == "locations":
            # The bundled world's checks, labelled from its data at load rather than copied into this metadata.
            info = {**info, **_location_metadata()}
            options = list(info["labels"])
        else:
            options = choices.get(field.name, info.get("choices", []))
        result.append(_row(field.name, info, defaults[field.name], options, names))
    for key in switches:
        override = metadata[key]["logic_override"]
        allowed = CATALOG["logic_overrides"].get(override, []) if isinstance(override, str) else []
        default = _world_logic_default(override) if {repr(value) for value in allowed} == {"False", "True"} else None
        if metadata[key].get("kind") != "boolean" or type(default) is not bool:
            raise ValueError(f"{key}: logic_override must name a supported boolean logic override")
        result.append(_row(key, metadata[key], default, [], names))
    return result


def schema() -> list[dict]:
    """Supported player controls; hidden settings remain recognizable only for validation."""
    return [row for row in _rows() if not row.get("hidden")]


def validate(values: dict | None = None, *, text: str | None = None, spec: dict | None = None) -> Settings:
    """Decode or construct, enforce presentation types, then compile with the actual logic oracle.

    No dump needed. ``spec`` permits a caller's synthetic/custom world without introducing a UI-only world.
    Held modes are refused here; the seed pipeline independently enforces its own physical restrictions.
    A ``logic_override`` switch supplies an override only when ``logic`` does not already name it.
    Existing explicit overrides survive replay; editing the switch clears its old override in the form.
    """
    if text is not None:
        if not isinstance(text, str) or len(text) > 32768:
            raise ValueError("settings string must be text of at most 32768 characters")
        settings = Settings.from_string(text.strip())
        values = asdict(settings)
    elif not isinstance(values, dict):
        raise ValueError("settings must be an object")
    defaults = asdict(Settings())
    known = {item["key"]: item for item in _rows()}
    if unknown := values.keys() - known.keys():
        raise ValueError(f"unknown settings: {sorted(unknown)}")
    switches = {key: info for key, info in known.items() if "logic_override" in info}
    merged = defaults | {key: value for key, value in values.items() if key not in switches}
    shuffle = merged.get("shuffle")
    if (
        isinstance(shuffle, (list, tuple))
        and all(isinstance(kind, str) for kind in shuffle)
        and set(gifts.GIFT_TYPES).issubset(shuffle)
    ):
        merged["shuffle"] = [kind for kind in shuffle if kind not in gifts.GIFT_TYPES] + [gifts.SHUFFLE]
    for key, info in known.items():
        value = values.get(key, info["default"]) if key in switches else merged[key]
        kind = info["kind"]
        if kind == "boolean" and type(value) is not bool:
            raise ValueError(f"{info['label']} must be a boolean")
        if kind == "integer" and (type(value) is not int or not info["min"] <= value <= info["max"]):
            raise ValueError(f"{info['label']} must be an integer from {info['min']} to {info['max']}")
        if kind == "choice" and value not in info["choices"]:
            raise ValueError(f"{info['label']} must be one of {info['choices']}")
        if kind == "multi" and info.get("display") == "locations":
            # Names belong to the selected world, possibly a caller's own: ``prepare`` refuses unknown ones.
            if not isinstance(value, (list, tuple)) or not all(isinstance(v, str) for v in value):
                raise ValueError(f"{info['label']} must be a list of location names")
        elif kind == "multi" and (not isinstance(value, (list, tuple)) or any(v not in info["choices"] for v in value)):
            raise ValueError(f"{info['label']} must select from {info['choices']}")
        selected = value if kind == "multi" else [value] if kind == "choice" else []
        for option in info["options"]:
            if option["disabled"] and option["value"] in selected:
                raise ValueError(f"{option['label']}: {option['reason']}")
    settings = Settings(**merged)
    for key, info in switches.items():
        if key not in values:
            continue
        override = info["logic_override"]
        if override not in settings.logic and values[key] != info["default"]:
            settings = replace(settings, logic=settings.logic | {override: values[key]})
    if settings.areas and not settings.goal:
        raise ValueError("Playtest areas require a goal")
    try:
        selected_spec = load_spec() if spec is None else spec
        validate_logic_overrides(selected_spec, settings.logic)
        effective, world = prepare(selected_spec, settings)
        if conflict := return_guarantee_conflict(world, effective):
            raise FillError(conflict)
        if settings.excluded_locations:
            _validate_exclusions(selected_spec, settings, effective, world)
    except (FillError, WorldError) as error:
        raise ValueError(str(error)) from error
    return settings


def _validate_exclusions(spec: dict, settings: Settings, effective: Settings, world: World) -> None:
    """Refuse exclusions the seed could not honour, under the generator's own capacity check.

    ``Gift`` is a meta-kind that the dump-backed ``gifts.seed_setup`` expands. Without a dump, every gift type stands
    in for it, moving the gifts that setup could move (``gifts.movable_checks``) under its default songs-on-songs hold.
    The dump only keeps more gifts vanilla and holds more items, so nothing is refused here for want of them;
    generation checks again with the gifts it actually moves.
    """
    if gifts.SHUFFLE in settings.shuffle:
        kinds = (kind for name in settings.shuffle for kind in (gifts.GIFT_TYPES if name == gifts.SHUFFLE else (name,)))
        settings = replace(settings, shuffle=tuple(kinds))
        spec = gifts.logic_spec({"locations": {}, **spec}, settings)  # a spec's [locations] table is optional
        _, world = prepare(spec, settings)
        effective, world = prepare(gifts.restrict_spec(spec, gifts.movable_checks(world, gifts.load())), settings)
        if settings.songs == "song":
            songs = {name: (gifts.SONG_TYPE,) for name, item in world.items.items() if item.type == gifts.SONG_TYPE}
            effective = replace(
                effective,
                item_location_types={**effective.item_location_types, **songs},
                exclusive_location_types=(*effective.exclusive_location_types, gifts.SONG_TYPE),
            )
    validate_exclusions(world, effective)


def settings_payload(settings: Settings) -> dict:
    """Form values include derived logic switches and preserve explicit overrides in ``logic``.
    Editing a switch clears its old override through the metadata's existing ``clears`` convention."""
    values = asdict(settings)
    rows = _rows()
    for info in rows:
        if info.get("hidden"):
            values.pop(info["key"], None)
        elif "logic_override" in info:
            value = values["logic"].get(info["logic_override"], info["default"])
            if type(value) is not bool:
                raise ValueError(f"{info['label']} must be a boolean")
            values[info["key"]] = value
    inactive = {}
    for info in rows:
        for condition in info.get("enabled_when", []):
            value = values[condition["key"]]
            if "contains" in condition:
                enabled = condition["contains"] in value
            elif "equals" in condition:
                enabled = value == condition["equals"]
            else:
                enabled = value > condition["greater_than"]
            if not enabled:
                inactive[info["key"]] = condition["reason"]
                break
    return {"values": values, "settings_string": settings.to_string(), "inactive": inactive}


def presets(*, spec: dict | None = None) -> list[dict]:
    data = tomllib.loads(Path(__file__).with_name("presets.toml").read_text(encoding="utf-8"))
    return [
        {
            "id": key,
            "label": info["label"],
            "help": info["help"],
            **settings_payload(validate(info["values"], spec=spec)),
        }
        for key, info in data.items()
    ]


def input_schema() -> dict:
    """Descriptions for application inputs and job stages, without a front-end dependency."""
    return tomllib.loads(Path(__file__).with_name("inputs.toml").read_text(encoding="utf-8"))
