"""UI-neutral presentation metadata around the generator's single settings contract."""

import tomllib
from dataclasses import asdict, fields, replace
from functools import cache
from pathlib import Path

from clawshot.generate import FillError, Settings, hints, prepare
from clawshot.generate.fill import DUNGEON_ITEM_CHOICES, return_guarantee_conflict
from clawshot.patch import gamedata, gifts
from clawshot.settings import CATALOG, validate_logic_overrides
from clawshot.world.load import WorldError, load_spec

METADATA_PATH = Path(__file__).with_name("settings.toml")


@cache
def _world_logic_default(name: str):
    """The bundled world's value for a logic setting; world data does not change while the app runs."""
    spec = load_spec()
    return {**spec.get("settings", {}), **spec.get("tricks", {}), **spec.get("flags", {})}.get(name)


def _row(key: str, metadata: dict, default, choices: list, names: set[str]) -> dict:
    info = dict(metadata)
    for part in ("label", "kind", "group", "help"):
        if not info.get(part):
            raise ValueError(f"Settings metadata missing {key}.{part}")
    info.update(key=key, default=default, choices=choices)
    labels = info.pop("labels", {})
    unavailable = info.pop("unavailable", {})
    choice_help = info.pop("choice_help", {})
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
        }
        for choice in info["choices"]
    ]
    return info


def schema() -> list[dict]:
    """One row per Settings field, then one per ``logic_override`` switch: a presentation of one supported
    boolean logic override (``Settings.logic``), not a generator setting of its own."""
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
    known = {item["key"]: item for item in schema()}
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
        if kind == "multi" and (not isinstance(value, (list, tuple)) or any(v not in info["choices"] for v in value)):
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
    except (FillError, WorldError) as error:
        raise ValueError(str(error)) from error
    return settings


def settings_payload(settings: Settings) -> dict:
    """Form values include derived logic switches and preserve explicit overrides in ``logic``.
    Editing a switch clears its old override through the metadata's existing ``clears`` convention."""
    values = asdict(settings)
    rows = schema()
    for info in rows:
        if "logic_override" in info:
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
