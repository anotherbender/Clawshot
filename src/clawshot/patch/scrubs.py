"""Saved one-time scrub rewards; repeat/rotating vendors remain vanilla.

Keep the Banc offer selectors: the common flow dispatches known names, not arbitrary
items. Rewrite every grant of a logical check, including both capacity tiers, and
its explicit selection identity. When native gates hide every repeat offer, finish
before opening the shop UI. Puzzle, cancel/shortfall paths, ordinary menus and
success-only saved flags stay native; optional fees cover only shuffled families.
"""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from clawshot.formats import evfl
from clawshot.generate import Settings, prepare
from clawshot.patch import items as item_actors
from clawshot.patch.plan import PatchError
from clawshot.patch.shops import SHOPS_TOML
from clawshot.patch.write import FileChanges

FLOW = "Enemy_Scrub_Business_Common"
PATH = f"Event/EventFlow/{FLOW}.bfevfl.zs"
SHUFFLE = "Scrub"
CAPACITIES = ("Deku Stick Capacity", "Deku Nut Capacity")


@dataclass(frozen=True)
class Sale:
    ids: tuple[int, ...]
    flag: str
    price: int
    grants: tuple[tuple[str, str], ...]
    selection: str | None = None


SALES = {
    "HF Deku Scrub Grotto": Sale(
        (1888007325063123154, 10364468093017215295),
        "HyruleField_Enemy_Scrub_Business_HeartPiece_01",
        100,
        (("Event645", "Obj_Heart_Piece"),),
        "Event653",
    ),
    "DMC Deku Scrub": Sale(
        (2518138296199711695,),
        "DeathMountain_Enemy_Scrub_Business_HeartPiece_01",
        100,
        (("Event293", "Obj_Heart_Piece"),),
        "Event144",
    ),
    "LW Deku Scrub Near Bridge": Sale(
        (182031956235860994, 7488448334396031424, 5406759280757349546, 11192313919554167152),
        "LostWood_Enemy_Scrub_Business_DekuStickPouch_01",
        40,
        (
            ("Event317", "Item_StickBag_Large"),
            ("Event322", "Item_StickBag_Medium"),
            ("Event555", "Item_StickBag_Medium"),
        ),
    ),
    "LW Deku Scrub Grotto Front": Sale(
        (4328741615941752705, 5764461665617243979),
        "Lostwood_Enemy_Scrub_Business_DekuNutsPouch_01",
        40,
        (("Event318", "Item_NutBag_Large"), ("Event326", "Item_NutBag_Medium")),
    ),
}


def patch_flowchart(
    fc: evfl.Flowchart, placements: Mapping[str, str], *, prices: Mapping[str, int] | None = None
) -> None:
    """Validate before mutation; guard empty menus and preserve purchase/flag gates."""
    if fc.name != FLOW or set(placements) - SALES.keys():
        raise PatchError(f"{FLOW}: invalid flow or unsupported scrub checks {sorted(placements)}")
    prices = dict(prices or {})
    if prices.keys() - placements.keys() or any(type(p) is not int or not 0 <= p <= 1000 for p in prices.values()):
        raise PatchError(f"{FLOW}: invalid fixed scrub prices {prices!r}")
    edits = []
    for check, item in placements.items():
        if not isinstance(item, str) or not item:
            raise PatchError(f"{check}: empty or invalid reward")
        sale = SALES[check]
        for name, old in sale.grants:
            found = [e for e in fc.events if e.name == name]
            if len(found) != 1:
                raise PatchError(f"{FLOW}/{name}: expected one grant, found {len(found)}")
            event = found[0]
            if not (
                isinstance(event, evfl.SubFlowEvent)
                and event.flowchart in ("", FLOW)
                and event.entry_point == "SimpleShopSub_Scrub_Business_OneTime"
                and (event.params or {}).get("ActorName") == old
                and event.params.get("Price") == sale.price
            ):
                raise PatchError(f"{FLOW}/{name}: stale sale {event!r}")
            edits.append((event.params, "ActorName", item))
            if check in prices:
                edits.append((event.params, "Price", prices[check]))
        if sale.selection:
            found = [e for e in fc.events if e.name == sale.selection]
            if len(found) != 1:
                raise PatchError(f"{FLOW}/{sale.selection}: expected one selection event")
            event = found[0]
            if not (
                isinstance(event, evfl.ActionEvent)
                and fc.actors[event.actor].name == "GameDataActor"
                and fc.actors[event.actor].actions[event.action] == "EventTriggerSetGameDataString64"
                and (event.params or {}).get("GameDataName") == "Shop_SelectItemName"
                and event.params.get("Value") == "Obj_Heart_Piece"
            ):
                raise PatchError(f"{FLOW}/{sale.selection}: stale selection {event!r}")
            edits.append((event.params, "Value", item))
    # Both repeat-vendor initializers finish their native offer filtering here,
    # before Event119 opens the shop UI. A degenerate Leave-only menu can strand
    # the dialog (#26); reuse the native no-goods goodbye instead. Do not alter
    # the normal initial/return menus or the purchase/cancel cleanup.
    index = {event.name: i for i, event in enumerate(fc.events)}
    required = ("Event192", "Event334", "Event119", "Event395", "Event140")
    if any(sum(event.name == name for event in fc.events) != 1 for name in required):
        raise PatchError(f"{FLOW}: missing or duplicate empty-offer guard anchors")
    incoming = [fc.events[index[name]] for name in required[:2]]
    target, goodbye, finish = (fc.events[index[name]] for name in required[2:])
    if not all(
        isinstance(event, evfl.SubFlowEvent)
        and event.flowchart in ("", FLOW)
        and event.entry_point == "Unopened_Check"
        and event.next == index["Event119"]
        and (event.params or {}).get("GameData_Item") == "Scrub_Business_TempItemName_02"
        and event.params.get("GameDate_Unopend") == "Enemy_Scrub_Business_Unopened03"
        for event in incoming
    ):
        raise PatchError(f"{FLOW}: stale offer-filter completion {incoming!r}")
    if not (
        isinstance(target, evfl.ActionEvent)
        and fc.actors[target.actor].name == "UISystemActor"
        and fc.actors[target.actor].actions[target.action] == "EventTriggerSetDisplayHeartGauge"
        and (target.params or {}).get("IsDisplayHeartGauge") is True
        and isinstance(goodbye, evfl.ActionEvent)
        and fc.actors[goodbye.actor].name == "Enemy_Scrub_Business"
        and fc.actors[goodbye.actor].actions[goodbye.action] == "EventTalk"
        and (goodbye.params or {}).get("IsCloseDialog") is True
        and goodbye.params.get("ChoiceNumber") == 0
        and goodbye.params.get("MessageId") == "EventFlowMsg/Enemy_Event:Enemy_Scrub_Business_Common_018"
        and goodbye.next == index["Event140"]
        and isinstance(finish, evfl.ActionEvent)
        and fc.actors[finish.actor].name == "Enemy_Scrub_Business"
        and fc.actors[finish.actor].actions[finish.action] == "EventScrubBusinessOnIsFinishDoEvent"
        and finish.next == evfl.NONE
    ):
        raise PatchError(f"{FLOW}: stale no-goods exit {target!r}, {goodbye!r}, {finish!r}")
    actors = [(i, actor) for i, actor in enumerate(fc.actors) if actor.name == "GameDataActor"]
    if len(actors) != 1 or not {"EventQueryIsGameDataBool", "EventQueryIsGameDataString64"}.issubset(
        actors[0][1].queries
    ):
        raise PatchError(f"{FLOW}: missing offer-gate queries")
    actor_id, actor = actors[0]
    start = len(fc.events)
    guards = []
    for slot in range(3):
        unavailable = start + 2 * (slot + 1) if slot < 2 else index["Event395"]
        guards.extend(
            (
                evfl.SwitchEvent(
                    f"ClawshotScrubOfferEmpty{slot}",
                    actor_id,
                    actor.queries.index("EventQueryIsGameDataString64"),
                    [(0, unavailable), (1, start + 2 * slot + 1)],
                    {"GameDataName": f"Scrub_Business_TempItemName_{slot:02}", "Value": "", "Index": -1},
                ),
                evfl.SwitchEvent(
                    f"ClawshotScrubOfferHidden{slot}",
                    actor_id,
                    actor.queries.index("EventQueryIsGameDataBool"),
                    [(0, unavailable), (1, index["Event119"])],
                    {"GameDataName": f"Enemy_Scrub_Business_Unopened{slot + 1:02}", "Index": -1},
                ),
            )
        )
    for params, key, value in edits:
        params[key] = value
    for event in incoming:
        event.next = start
    fc.events.extend(guards)


def changes(placements: Mapping[str, str], *, prices: Mapping[str, int] | None = None) -> FileChanges:
    """One-time rewards plus the no-offers guard, even without Scrub shuffle."""
    if unknown := set(placements) - SALES.keys():
        raise PatchError(f"unsupported scrub checks: {sorted(unknown)}")
    placements = dict(placements)
    prices = dict(prices or {})

    def transform(data: bytes) -> bytes:
        tree = evfl.read(data)
        if tree.flowchart is None:
            raise PatchError(f"{PATH}: no flowchart")
        patch_flowchart(tree.flowchart, placements, prices=prices)
        out = evfl.write(tree)
        if evfl.read(out) != tree:
            raise PatchError(f"{PATH}: changed flow does not read back")
        return out

    return {PATH: transform}


def seed_setup(spec: Mapping[str, Any], settings: Settings):
    """Four reviewed once-sale families; one pool reward per shared saved flag.

    Public Scrub covers the two translated scrub types without exposing an internal
    alias in the settings string. Capacities use fixed Medium actors (D16), held to
    these destinations until their grants have been tested in chests.
    """
    locations = {}
    for name, info in spec["locations"].items():
        if name in SALES:
            info = {**info, "type": SHUFFLE}
        elif info.get("type") in ("Scrub", "GrottoScrub") and not info.get("keep_vanilla"):
            info = {**info, "keep_vanilla": "scrub shuffle: repeat/rotating vendor, not a saved one-time family"}
        locations[name] = info
    prices = {
        name: settings.scrub_price if settings.scrub_prices == "fixed" else sale.price for name, sale in SALES.items()
    }
    with SHOPS_TOML.open("rb") as stream:
        wallets = tomllib.load(stream)["wallet"]
    regions = []
    for region in spec["regions"]:
        rules = dict(region.get("locations", {}))
        for name in rules:
            if name not in prices:
                continue
            old = rules[name]
            rule = old if isinstance(old, str) else old["rule"]
            source = spec["locations"][name].get("source", "") if isinstance(old, str) else old.get("source", "")
            wallet = next((tier["rule"] for tier in wallets if prices[name] <= tier["capacity"]), "False")
            rules[name] = {
                "rule": f"({rule}) and ({wallet})",
                "source": (
                    f"scrub_prices={settings.scrub_prices}: {prices[name]} rupees; "
                    f"native puzzle/once gate retained; {source}"
                ),
            }
        regions.append({**region, "locations": rules})
    spec = {
        **spec,
        "regions": regions,
        "locations": locations,
        "settings": {
            **spec.get("settings", {}),
            "scrub_sale_prices": prices,
        },
    }
    held = dict(settings.item_location_types)
    for item in CAPACITIES:
        held[item] = (SHUFFLE,) if item not in held else tuple(t for t in held[item] if t == SHUFFLE)
    settings = replace(settings, item_location_types=held)
    _, world = prepare(spec, settings)
    checks = tuple(
        name
        for name, loc in world.locations.items()
        if name in SALES and loc.vanilla is not None and not loc.n64_only and not loc.keep_vanilla
    )
    actors = item_actors.load()

    def step(placements: Mapping[str, str]) -> FileChanges:
        # Even an unchanged capacity placement must normalize both native tier
        # branches to the single fixed item represented in the pool.
        return changes(
            {name: actors.actor(placements[name]) for name in checks}, prices={name: prices[name] for name in checks}
        )

    return spec, settings, step
