"""Synthetic merchants played through their NPC callers: one shuffled reward, then the pristine native sale.

Every flow is built here from labels, never from a decoded game fixture, and written through the seed's gift
step. A small interpreter plays one conversation through local and cross-flow calls and changes only what a
player sees in a save: rupees, bottle slots, pouch stock and saved Bools. Reloading serializes the save, so
runtime prices and unsaved Bools do not survive it.
"""

import json
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from functools import cache
from typing import NamedTuple

import pytest

from clawshot.census import definitions
from clawshot.census.gifts import Gift, reachable
from clawshot.formats import byml, evfl
from clawshot.patch import gifts
from clawshot.patch.items import ItemActors

GRANNY, MEDIGORON, CARPET = gifts.GRANNY_CHECK, "GC Medigoron", "Wasteland Bombchu Salesman"
GRANNY_FLOW, MEDIGORON_FLOW, CARPET_FLOW = "Npc_Hylia_053_Adult", "Npc_Goron_Medigoron_Adult", "Npc_Hylia_044_Adult"
BAZAAR_FLOW = "Npc_Synthetic_Bazaar"  # an untouched caller of the shared native sale
TRADE = "SubEvent_GetSwordBigGoron_IsAfter_Step05_01_Exp"  # Granny's trade unlock
BOUGHT = "Npc_Hylia_044_Buy"  # native dialogue Bool set by every SimpleShop sale; not saved (gift_rules.toml)
UNSAVED = {BOUGHT}
GIANT, BROKEN, BIGGORON = "Weapon_Sword_Giant", "Weapon_Sword_BrokenGiant", "Weapon_Sword_Biggoron"


class Merchant(NamedTuple):
    flow: str
    event: str  # the sale step
    stock: str  # native stock actor
    item: str  # its logic item
    call: str  # the native sale the step calls
    entries: tuple[str, ...]


MERCHANTS = {
    GRANNY: Merchant(
        GRANNY_FLOW,
        "Event12",
        "Item_Bottle_BluePotion",
        "Blue Potion",
        "Dm_SY_GetInEvent:GetInEventInBottle_BlueBottleShop",
        ("Buy_BluePotion", "Talk"),
    ),
    MEDIGORON: Merchant(
        MEDIGORON_FLOW,
        "Event11",
        "Shop_Sword_Giant",
        "Giants Knife",
        "SimpleShop:SimpleShopRoot_Npc_Goron_Medigoron_Adult",
        ("Talk",),
    ),
    CARPET: Merchant(
        CARPET_FLOW, "Event3", "Shop_BombchuBundle_01", "Bombchus (10)", "SimpleShop:SimpleShopRoot", ("Talk",)
    ),
}
PATHS = {name: f"synthetic/{name}.bfevfl" for name in (GRANNY_FLOW, MEDIGORON_FLOW, CARPET_FLOW, "SimpleShop")}
ACTORS = ItemActors(
    {
        **{merchant.item: merchant.stock for merchant in MERCHANTS.values()},
        "Megaton Hammer": "Item_Hammer",
        "Iron Boots": "Item_HeavyBoot",
        "Hover Boots": "Item_HoverBoot",
        "Bottle": "Item_Bottle",
        "Bottle with Milk": "Item_Bottle_Milk",
    },
    {},
)
# What a granted actor adds: a new bottle holding something, or pouch stock (capped by a capacity, if any).
POUCH = {
    "Item_Bottle": ("bottle", "Empty"),
    "Item_Bottle_Milk": ("bottle", "Milk"),
    "Item_Bottle_BluePotion": ("bottle", "BluePotion"),
    "Item_Hammer": ("stock", "Item_Hammer", 1),
    "Item_HeavyBoot": ("stock", "Item_HeavyBoot", 1),
    "Item_HoverBoot": ("stock", "Item_HoverBoot", 1),
    "Shop_Sword_Giant": ("stock", GIANT, 1),
    "Shop_BombchuBundle_01": ("stock", "Bombchu", 10),
    "Shop_Arrow_10": ("stock", "Arrow", 10),
}
BOTTLE_ITEMS = {2: "BluePotion"}  # the BottleItem value of Granny's native refill


# --- synthetic flows ----------------------------------------------------------------------------------------------


def chart(name, rows, entries):
    """Rows by label: ``(event, "do", "Actor.Action", next, params)``, ``(event, "ask", "Actor.Query", {case:
    target}, params)``, ``(event, "call", "flow:entry", next, params)``, ``(event, "fork", [branches], join)`` and
    ``(event, "join", next)``; a ``None`` target ends the entry."""
    index = {row[0]: i for i, row in enumerate(rows)}
    actors: dict[str, tuple[list[str], list[str]]] = {}

    def to(label):
        return evfl.NONE if label is None else index[label]

    def slot(spec, kind):
        actor, operation = spec.split(".")
        names = actors.setdefault(actor, ([], []))[kind]
        if operation not in names:
            names.append(operation)
        return list(actors).index(actor), names.index(operation)

    events = []
    for label, kind, *rest in rows:
        if kind == "do":
            spec, target, params = rest
            events.append(evfl.ActionEvent(label, *slot(spec, 0), to(target), params))
        elif kind == "ask":
            spec, cases, params = rest
            events.append(evfl.SwitchEvent(label, *slot(spec, 1), [(c, to(t)) for c, t in cases.items()], params))
        elif kind == "call":
            spec, target, params = rest
            flow, entry = spec.split(":")
            events.append(evfl.SubFlowEvent(label, flow, entry, to(target), params))
        elif kind == "fork":
            branches, join = rest
            events.append(evfl.ForkEvent(label, index[join], [index[b] for b in branches]))
        else:
            events.append(evfl.JoinEvent(label, to(rest[0])))
    fc = evfl.Flowchart(name, [evfl.Actor(a, actions=act, queries=ask) for a, (act, ask) in actors.items()], events, [])
    for entry, label in entries.items():
        calls = sorted(i for i in reachable(fc, index[label]) if isinstance(events[i], evfl.SubFlowEvent))
        fc.entry_points.append(evfl.EntryPoint(entry, index[label], calls))
    return fc


def say(label, message, target=None):
    return (label, "do", "Npc_EventStarter.EventTalk", target, {"MessageId": message})


def price(label, rupees, target):
    params = {"GameDataName": "SimpleShop_Price", "Index": -1, "Value": rupees}
    return (label, "do", "GameDataActor.EventTriggerSetGameDataInt", target, params)


def sale(actor, rupees, npc):
    return {
        "ActorName": actor,
        "Price": rupees,
        "Payment_MessageId": f"{npc}: here you are",
        "ShopCancel_MessageId": f"{npc}: another time",
        "LackRupee_MessageId": f"{npc}: too few rupees",
        "FullofPouche_MessageId": f"{npc}: you cannot carry it",
    }


def mask(npc):
    worn = {"GameDataName": "Synthetic_MaskWorn", "Index": -1}
    return [
        ("Event48", "ask", "GameDataActor.EventQueryIsGameDataBool", {0: "Event49", 1: None}, worn),
        say("Event49", f"{npc}: nice mask"),
    ]


def granny():
    return chart(
        GRANNY_FLOW,
        [
            (
                "Event3",
                "ask",
                "GameDataActor.EventQueryIsGameDataBoolExp",
                {0: "Event31", 1: "Event33"},
                {"GameDataName": TRADE},
            ),
            ("Event31", "call", ":Buy_BluePotion", None, None),
            say("Event33", "Granny: come back later"),
            ("Event7", "ask", "GameSystemActor.EventQueryTalkChoice2", {0: "Event11", 1: "Event9"}, None),
            say("Event9", "Granny: maybe next time"),
            ("Event11", "ask", "PouchSystemActor.EventQueryHasRuppe", {0: "Event15", 1: "Event14"}, {"Value": 100}),
            say("Event14", "Granny: not enough rupees"),
            ("Event15", "ask", "PouchSystemActor.EventQueryIsAnyBottleEmpty", {0: "Event179", 1: "Event16"}, None),
            say("Event16", "Granny: bring an empty bottle"),
            price("Event179", 100, "Event12"),
            (
                "Event12",
                "call",
                "Dm_SY_GetInEvent:GetInEventInBottle_BlueBottleShop",
                "Event20",
                {"ActorName": "Item_Bottle_BluePotion", "BottleItem": 2, "PriceGameData": "SimpleShop_Price"},
            ),
            say("Event20", "Granny: thank you"),
        ],
        {"Talk": "Event3", "Buy_BluePotion": "Event7"},
    )


def medigoron():
    def owns(label, actor, yes, no):
        params = {"Num": 1, "Actor": actor}
        return (label, "ask", "PouchSystemActor.EventQueryIsExistInPouch", {0: yes, 1: no}, params)

    return chart(
        MEDIGORON_FLOW,
        [
            ("Event54", "call", ":Mask_All", "Event19", None),
            owns("Event19", BIGGORON, "Event25", "Event6"),
            say("Event25", "Medigoron: my brother forged a finer sword"),
            owns("Event6", GIANT, "Event36", "Event7"),
            say("Event36", "Medigoron: you already carry my knife"),
            owns("Event7", BROKEN, "Event23", "Event17"),
            say("Event23", "Medigoron: broken? I will sell you another", "Event29"),
            say("Event17", "Medigoron: my finest knife", "Event29"),
            price("Event29", 200, "Event11"),
            (
                "Event11",
                "call",
                "SimpleShop:SimpleShopRoot_Npc_Goron_Medigoron_Adult",
                "Event45",
                sale("Shop_Sword_Giant", 200, "Medigoron"),
            ),
            say("Event45", "Medigoron: come again"),
            *mask("Medigoron"),
        ],
        {"Talk": "Event54", "Mask_All": "Event48"},
    )


def carpet():
    bought = {"GameDataName": BOUGHT, "Index": -1}
    return chart(
        CARPET_FLOW,
        [
            ("Event14", "call", ":Mask_All", "Event5", None),
            price("Event5", 90, "Event1"),
            ("Event1", "ask", "GameDataActor.EventQueryIsGameDataBool", {0: "Event16", 1: "Event15"}, bought),
            say("Event15", "Carpet: Bombchus, 90 rupees", "Event3"),
            say("Event16", "Carpet: more Bombchus?", "Event3"),
            ("Event3", "call", "SimpleShop:SimpleShopRoot", None, sale("Shop_BombchuBundle_01", 90, "Carpet")),
            *mask("Carpet"),
        ],
        {"Talk": "Event14", "Mask_All": "Event48"},
    )


def bazaar():
    return chart(
        BAZAAR_FLOW,
        [
            price("Event1", 20, "Event2"),
            ("Event2", "call", "SimpleShop:SimpleShopRoot", None, sale("Shop_Arrow_10", 20, "Bazaar")),
        ],
        {"Talk": "Event1"},
    )


def simple_shop():
    choice, funds = "GameSystemActor.EventQueryTalkChoice2", "PouchSystemActor.EventQueryHasRuppe"
    room, owns = "PouchSystemActor.EventQueryCanAddToPorch", "PouchSystemActor.EventQueryIsExistInPouch"
    charge = "PouchSystemActor.EventTriggerAddGameDataIntToRupee"
    cost, actor = {"Value": evfl.Argument("Price")}, {"Actor": evfl.Argument("ActorName")}
    paid = {"IsSignInverse": True, "GameDataName": "SimpleShop_Price"}
    payment = {"MessageId": evfl.Argument("Payment_MessageId")}

    def cancel(label, message):
        return (label, "call", ":Sub_ShopCancel", None, {"MessageId": evfl.Argument(message)})

    return chart(
        "SimpleShop",
        [
            ("Event5", "do", "Npc_EventStarter.EventTalk", None, {"MessageId": evfl.Argument("MessageId")}),
            # SimpleShopRoot
            ("Event18", "ask", choice, {0: "Event19", 1: "Event26"}, None),
            ("Event19", "ask", funds, {0: "Event17", 1: "Event28"}, cost),
            ("Event17", "ask", room, {0: "Event124", 1: "Event20", 2: "Event27"}, actor),
            say("Event20", "Shop: not all of it will fit", "Event72"),
            ("Event72", "ask", choice, {0: "Event124", 1: "Event26"}, None),
            cancel("Event26", "ShopCancel_MessageId"),
            cancel("Event27", "FullofPouche_MessageId"),
            cancel("Event28", "LackRupee_MessageId"),
            (
                "Event124",
                "call",
                ":Sub_SimpleShop_Buy",
                None,
                {"ActorName": evfl.Argument("ActorName"), "Payment_MessageId": evfl.Argument("Payment_MessageId")},
            ),
            # SimpleShopRoot_Npc_Goron_Medigoron_Adult: a replacement takes the broken Knife after the sale
            ("Event112", "ask", choice, {0: "Event113", 1: "Event116"}, None),
            ("Event113", "ask", funds, {0: "Event120", 1: "Event118"}, cost),
            ("Event120", "ask", room, {0: "Event157", 1: "Event121", 2: "Event117"}, actor),
            say("Event121", "Shop: not all of it will fit", "Event122"),
            ("Event122", "ask", choice, {0: "Event157", 1: "Event116"}, None),
            cancel("Event116", "ShopCancel_MessageId"),
            cancel("Event117", "FullofPouche_MessageId"),
            cancel("Event118", "LackRupee_MessageId"),
            ("Event157", "do", charge, "Event119", paid),
            (
                "Event119",
                "call",
                "Dm_SY_GetInEvent:GetInEventItemSwordMedigoron",
                "Event169",
                {"ActorName": evfl.Argument("ActorName")},
            ),
            ("Event169", "do", "Npc_EventStarter.EventTalk", "Event25", payment),
            ("Event25", "ask", owns, {0: "Event115", 1: "Event62"}, {"Num": 1, "Actor": BROKEN}),
            (
                "Event115",
                "do",
                "PouchSystemActor.EventTriggerAddOrRemovePouchContent",
                "Event62",
                {"Actor": BROKEN, "Num": -1},
            ),
            ("Event62", "do", "GameSystemActor.EventTriggerRequestAutoSave", None, None),
            # Sub_SimpleShop_Buy: payment and charge overlap, then the hand-over
            ("Event160", "fork", ["Event159", "Event153"], "Event161"),
            ("Event159", "do", "Npc_EventStarter.EventTalk", None, payment),
            ("Event153", "do", charge, None, paid),
            ("Event161", "join", "Event150"),
            (
                "Event150",
                "call",
                "NpcCommon:NpcCommon_HandOver_NpcToPlayer_NoTurn_NoWaitAS",
                "Event155",
                {"ReceiveItem": evfl.Argument("ActorName")},
            ),
            say("Event155", "Shop: thank you", "Event222"),
            (
                "Event222",
                "do",
                "GameDataActor.EventTriggerSetGameDataBool",
                "Event135",
                {"GameDataName": BOUGHT, "Index": -1, "Value": True},
            ),
            ("Event135", "do", "GameSystemActor.EventTriggerRequestAutoSave", None, None),
        ],
        {
            "Sub_ShopCancel": "Event5",
            "SimpleShopRoot": "Event18",
            "SimpleShopRoot_Npc_Goron_Medigoron_Adult": "Event112",
            "Sub_SimpleShop_Buy": "Event160",
        },
    )


def get_in_event():
    grant = "GetPouchContent:GetPouchContentByActorName_ForGetInEvent"
    by_actor = {"IsGetInEvent": True, "ActorName": evfl.Argument("ActorName")}
    charge = {"IsSignInverse": True, "GameDataName": evfl.Argument("PriceGameData")}
    return chart(
        "Dm_SY_GetInEvent",
        [
            # Granny's refill fills the selected owned empty bottle, then charges the given price.
            (
                "Event646",
                "call",
                "GetPouchContent:PushToSelectedBottle",
                "Event657",
                {"Item": evfl.Argument("BottleItem")},
            ),
            ("Event657", "do", "PouchSystemActor.EventTriggerAddGameDataIntToRupee", None, charge),
            # The ordinary gift and Medigoron's sword scene grant the actor's pouch content, containers included.
            ("Event313", "call", grant, None, by_actor),
            ("Event90", "call", grant, None, by_actor),
        ],
        {
            "GetInEventInBottle_BlueBottleShop": "Event646",
            "GetInEvent_NotTurn_NotNpc": "Event313",
            "GetInEventItemSwordMedigoron": "Event90",
        },
    )


def native():
    """The unpatched synthetic game."""
    return {fc.name: fc for fc in (granny(), medigoron(), carpet(), bazaar(), simple_shop(), get_in_event())}


@cache
def census():
    return definitions.load()


def gift_steps():
    out = {}
    for check, m in MERCHANTS.items():
        step = f"{m.flow}/{m.event}"
        out[check] = Gift(step, "npc_gift", m.flow, PATHS[m.flow], m.entries, m.event, m.call, "ActorName", m.stock, "")
    return out


@cache
def flag(check):
    """The saved Bool a completed check leaves in the save."""
    return gifts.GiftChange(gifts.load()[check], (gift_steps()[check],), MERCHANTS[check].stock).flag


def transforms(placements):
    """The seed's gift step for all three merchants; ``placements``: check -> logic item, vanilla by default."""
    vanilla = {check: merchant.item for check, merchant in MERCHANTS.items()}
    rules = gifts.load()
    step = gifts.seed_step(
        list(MERCHANTS),
        gift_steps().values(),
        census(),
        {check: rules[check] for check in MERCHANTS},
        ACTORS,
        vanilla,
        PATHS,
    )
    return step({**vanilla, **placements})


def seed(placements=None):
    """The patched synthetic game, every flow written and read back."""
    changed = transforms(placements or {})
    charts = {}
    for name, fc in native().items():
        data = evfl.write(evfl.EventFlowFile(name, flowchart=fc))
        if PATHS.get(name) in changed:
            data = changed[PATHS[name]](data)
        charts[name] = evfl.read(data).flowchart
    return charts


# --- the player ---------------------------------------------------------------------------------------------------


@dataclass
class Save:
    rupees: int
    bottles: list = field(default_factory=lambda: [None, None, None, None])  # None: no bottle in the slot
    pouch: dict = field(default_factory=dict)
    capacity: dict = field(default_factory=dict)
    flags: dict = field(default_factory=dict)

    @property
    def valid_bottles(self):
        return sum(slot is not None for slot in self.bottles)

    def reload(self):
        """Write every saved field out and read it back: unsaved Bools and runtime Ints are gone."""
        data = json.loads(json.dumps(asdict(self)))
        data["flags"] = {name: value for name, value in data["flags"].items() if name not in UNSAVED}
        return Save(**data)


class Visit:
    """One conversation. Native query ABI: Bool, pouch and choice true/accept = 0; room 0 fits, 1 partly, 2 full."""

    def __init__(self, charts, save, accept):
        self.charts, self.save, self.accept = charts, save, accept
        self.prices = {}  # runtime GameData Ints
        self.said = []
        self.budget = 10_000

    def call(self, flow, entry, args):
        if flow in self.charts:
            fc = self.charts[flow]
            self.walk(fc, fc.entry_point(entry).main_event, args, evfl.NONE)
        elif (flow, entry) == ("GetPouchContent", "PushToSelectedBottle"):
            bottles = self.save.bottles
            bottles[bottles.index("Empty")] = BOTTLE_ITEMS[args["Item"]]  # an owned bottle, refilled
        elif (flow, entry) == ("GetPouchContent", "GetPouchContentByActorName_ForGetInEvent"):
            self.give(args["ActorName"])
        elif (flow, entry) == ("NpcCommon", "NpcCommon_HandOver_NpcToPlayer_NoTurn_NoWaitAS"):
            self.give(args["ReceiveItem"])
        else:
            raise AssertionError(f"no synthetic {flow}:{entry}")

    def walk(self, fc, index, args, stop):
        while index not in (evfl.NONE, stop):
            self.budget -= 1
            assert self.budget > 0, "the conversation never ends"
            event = fc.events[index]
            params = {
                key: args[value] if isinstance(value, evfl.Argument) else value
                for key, value in (getattr(event, "params", None) or {}).items()
            }
            if isinstance(event, evfl.ForkEvent):
                for branch in event.forks:
                    self.walk(fc, branch, args, event.join)
                index = fc.events[event.join].next
            elif isinstance(event, evfl.JoinEvent):
                index = event.next
            elif isinstance(event, evfl.SwitchEvent):
                index = dict(event.cases)[self.ask(fc.actors[event.actor], event.query, params)]
            elif isinstance(event, evfl.SubFlowEvent):
                self.call(event.flowchart or fc.name, event.entry_point, params)
                index = event.next
            else:
                self.do(fc.actors[event.actor], event.action, params)
                index = event.next

    def ask(self, actor, query, params):
        name, save = f"{actor.name}.{actor.queries[query]}", self.save
        if name in ("GameDataActor.EventQueryIsGameDataBool", "GameDataActor.EventQueryIsGameDataBoolExp"):
            return 0 if save.flags.get(params["GameDataName"], False) else 1
        if name == "GameSystemActor.EventQueryTalkChoice2":
            return 0 if self.accept else 1
        if name == "PouchSystemActor.EventQueryHasRuppe":
            return 0 if save.rupees >= params["Value"] else 1
        if name == "PouchSystemActor.EventQueryIsAnyBottleEmpty":
            return 0 if "Empty" in save.bottles else 1
        if name == "PouchSystemActor.EventQueryIsExistInPouch":
            return 0 if save.pouch.get(params["Actor"], 0) >= params["Num"] else 1
        if name == "PouchSystemActor.EventQueryCanAddToPorch":
            kind, *content = POUCH[params["Actor"]]
            if kind == "bottle":
                return 0 if None in save.bottles else 2
            stock, amount = content
            if stock not in save.capacity:
                return 0
            left = save.capacity[stock] - save.pouch.get(stock, 0)
            return 0 if left >= amount else 1 if left > 0 else 2
        raise AssertionError(name)

    def do(self, actor, action, params):
        name, save = f"{actor.name}.{actor.actions[action]}", self.save
        if name == "GameDataActor.EventTriggerSetGameDataBool":
            save.flags[params["GameDataName"]] = params["Value"]
        elif name == "GameDataActor.EventTriggerSetGameDataInt":
            self.prices[params["GameDataName"]] = params["Value"]
        elif name == "PouchSystemActor.EventTriggerAddGameDataIntToRupee":
            assert params["IsSignInverse"] is True
            save.rupees -= self.prices[params["GameDataName"]]
            assert save.rupees >= 0, "charged more rupees than the player had"
        elif name == "PouchSystemActor.EventTriggerAddOrRemovePouchContent":
            count = save.pouch.get(params["Actor"], 0) + params["Num"]
            assert count >= 0, params
            save.pouch.pop(params["Actor"], None)
            if count:
                save.pouch[params["Actor"]] = count
        elif name == "Npc_EventStarter.EventTalk":
            self.said.append(params["MessageId"])
        elif name != "GameSystemActor.EventTriggerRequestAutoSave":
            raise AssertionError(name)

    def give(self, actor):
        kind, *content = POUCH[actor]
        if kind == "bottle":
            self.save.bottles[self.save.bottles.index(None)] = content[0]  # a new container
        else:
            stock, amount = content
            total = self.save.pouch.get(stock, 0) + amount
            self.save.pouch[stock] = min(total, self.save.capacity.get(stock, total))


def talk(charts, flow, save, *, accept=True):
    """Talk to ``flow``'s NPC once; ``save`` changes in place. Returns the dialogue the player saw."""
    visit = Visit(charts, save, accept)
    visit.call(flow, "Talk", {})
    return visit.said


def assert_native_sale(charts, check, save, *, accept=True):
    """A completed check plays exactly as the unpatched game plays the same save, and stays completed."""
    assert save.flags[flag(check)] is True
    expected = deepcopy(save)
    del expected.flags[flag(check)]
    expected_said = talk(native(), MERCHANTS[check].flow, expected, accept=accept)
    expected.flags[flag(check)] = True
    said = talk(charts, MERCHANTS[check].flow, save, accept=accept)
    assert (save, said) == (expected, expected_said)


def assert_refused(charts, check, save, *, accept=True):
    """Nothing is charged, given or completed."""
    before = deepcopy(save)
    if save.flags.get(flag(check)):
        assert_native_sale(charts, check, save, accept=accept)
    else:
        talk(charts, MERCHANTS[check].flow, save, accept=accept)
    assert save == before


def granny_save(rupees=100, bottles=("Bug", "Empty", None, None)):
    return Save(rupees, list(bottles), flags={TRADE: True})


def drink(save, slot):
    """Drinking empties the potion; the bottle stays."""
    assert save.bottles[slot] == "BluePotion"
    save.bottles[slot] = "Empty"


def break_knife(save):
    """The Knife breaks in ordinary play: the intact sword becomes the broken one."""
    assert save.pouch.pop(GIANT) == 1
    save.pouch[BROKEN] = 1


# --- Granny -------------------------------------------------------------------------------------------------------


def test_granny_identity_potion_refills_the_owned_empty_bottle_and_completes_once():
    charts = seed()
    save = granny_save()
    talk(charts, GRANNY_FLOW, save)
    # Not a new bottle C: the generic container grant fails here with three bottles.
    assert save == Save(0, ["Bug", "BluePotion", None, None], flags={TRADE: True, flag(GRANNY): True})
    assert save.valid_bottles == 2


@pytest.mark.parametrize("reward", ["Blue Potion", "Iron Boots", "Bottle"])
@pytest.mark.parametrize(
    ("accept", "setup"),
    [
        pytest.param(False, {}, id="decline"),
        pytest.param(True, {"rupees": 99}, id="99 rupees"),
        pytest.param(True, {"bottles": ("Bug", "BluePotion", None, None)}, id="no empty bottle"),
    ],
)
def test_granny_refusals_charge_nothing_and_never_complete_the_check(reward, accept, setup):
    charts = seed({GRANNY: reward})
    assert_refused(charts, GRANNY, granny_save(**setup), accept=accept)
    completed = granny_save(**setup)
    completed.flags[flag(GRANNY)] = True
    assert_refused(charts, GRANNY, completed, accept=accept)


def test_granny_identity_check_then_native_refills_after_reload_and_drinking():
    charts = seed()
    save = granny_save()
    talk(charts, GRANNY_FLOW, save)
    for _ in range(2):
        save = save.reload()
        drink(save, 1)
        save.rupees = 100  # rupees only, on a copy
        assert_native_sale(charts, GRANNY, save)
        assert save == Save(0, ["Bug", "BluePotion", None, None], flags={TRADE: True, flag(GRANNY): True})
        assert save.valid_bottles == 2


def test_granny_shuffled_reward_once_then_a_funded_reload_buys_the_native_refill():
    charts = seed({GRANNY: "Iron Boots"})
    save = granny_save()
    talk(charts, GRANNY_FLOW, save)
    completed = {TRADE: True, flag(GRANNY): True}
    assert save == Save(0, ["Bug", "Empty", None, None], {"Item_HeavyBoot": 1}, flags=completed)
    save = save.reload()
    save.rupees = 100
    assert_native_sale(charts, GRANNY, save)
    assert save == Save(0, ["Bug", "BluePotion", None, None], {"Item_HeavyBoot": 1}, flags=completed)
    assert save.valid_bottles == 2


@pytest.mark.parametrize(("reward", "contents"), [("Bottle", "Empty"), ("Bottle with Milk", "Milk")])
def test_genuine_bottle_rewards_still_add_a_new_bottle(reward, contents):
    charts = seed({GRANNY: reward, CARPET: reward})
    save = granny_save()
    talk(charts, GRANNY_FLOW, save)
    assert save == Save(0, ["Bug", "Empty", contents, None], flags={TRADE: True, flag(GRANNY): True})
    assert save.valid_bottles == 3
    shopper = Save(90, ["Bug", "Bug", "Bug", "Bug"])
    assert_refused(charts, CARPET, shopper)  # no room for a fifth bottle
    shopper.bottles[3] = None
    talk(charts, CARPET_FLOW, shopper)
    assert shopper == Save(0, ["Bug", "Bug", "Bug", contents], flags={flag(CARPET): True, BOUGHT: True})


# --- carpet seller ------------------------------------------------------------------------------------------------


def test_carpet_shuffled_reward_once_then_native_bombchu_sales_and_refusals():
    charts = seed({CARPET: "Hover Boots"})
    bag = {"Bombchu": 20}
    save = Save(89, capacity=bag)
    assert_refused(charts, CARPET, save)
    assert_refused(charts, CARPET, save, accept=False)
    save.rupees = 90
    talk(charts, CARPET_FLOW, save)
    assert save == Save(0, pouch={"Item_HoverBoot": 1}, capacity=bag, flags={flag(CARPET): True, BOUGHT: True})
    save = save.reload()
    # Both native dialogue branches (first sale, repeat sale) reach the real sale.
    for bombchus in (10, 20):
        save.rupees = 90
        assert_native_sale(charts, CARPET, save)
        expected = {"Item_HoverBoot": 1, "Bombchu": bombchus}
        assert save == Save(0, pouch=expected, capacity=bag, flags={flag(CARPET): True, BOUGHT: True})
    save = save.reload()
    for rupees, accept in ((90, True), (89, True), (90, False)):  # full, too few rupees, declined
        save.rupees = rupees
        assert_refused(charts, CARPET, save, accept=accept)


def test_carpet_identity_bombchus_complete_the_check_once_then_sell_natively():
    charts = seed()
    bag = {"Bombchu": 20}
    full = Save(90, pouch={"Bombchu": 20}, capacity=bag)
    assert_refused(charts, CARPET, full)
    save = Save(90, capacity=bag)
    talk(charts, CARPET_FLOW, save)
    assert save == Save(0, pouch={"Bombchu": 10}, capacity=bag, flags={flag(CARPET): True, BOUGHT: True})
    save = save.reload()
    save.rupees = 90
    assert_native_sale(charts, CARPET, save)
    assert save == Save(0, pouch={"Bombchu": 20}, capacity=bag, flags={flag(CARPET): True, BOUGHT: True})


def test_untouched_simple_shop_callers_keep_native_repeat_sales():
    charts = seed({MEDIGORON: "Megaton Hammer", CARPET: "Hover Boots"})
    patched, unpatched = Save(40, capacity={"Arrow": 30}), Save(40, capacity={"Arrow": 30})
    for _ in range(3):
        said = talk(charts, BAZAAR_FLOW, patched)
        assert said == talk(native(), BAZAAR_FLOW, unpatched)
        assert patched == unpatched
    assert patched == Save(0, pouch={"Arrow": 20}, capacity={"Arrow": 30}, flags={BOUGHT: True})


# --- Medigoron ----------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("swords", [{GIANT: 1, BIGGORON: 1}, {BROKEN: 1}, {BIGGORON: 1, BROKEN: 1}])
def test_medigoron_first_reward_ignores_sword_ownership_and_keeps_a_broken_knife(swords):
    charts = seed({MEDIGORON: "Megaton Hammer"})
    save = Save(199, pouch=dict(swords))
    assert_refused(charts, MEDIGORON, save)
    assert_refused(charts, MEDIGORON, save, accept=False)
    save.rupees = 200
    talk(charts, MEDIGORON_FLOW, save)
    assert save == Save(0, pouch={**swords, "Item_Hammer": 1}, flags={flag(MEDIGORON): True})


def test_medigoron_completed_check_keeps_native_knife_rules_and_sells_a_replacement():
    charts = seed({MEDIGORON: "Megaton Hammer"})
    save = Save(200, pouch={GIANT: 1})
    talk(charts, MEDIGORON_FLOW, save)
    assert save == Save(0, pouch={GIANT: 1, "Item_Hammer": 1}, flags={flag(MEDIGORON): True})
    save = save.reload()
    save.rupees = 200
    for swords in ({}, {BIGGORON: 1}):  # an intact Knife, and also Biggoron's Sword
        assert_refused(charts, MEDIGORON, Save(200, pouch={**save.pouch, **swords}, flags=dict(save.flags)))
    break_knife(save)
    assert_refused(charts, MEDIGORON, Save(200, pouch={**save.pouch, BIGGORON: 1}, flags=dict(save.flags)))
    for rupees, accept in ((199, True), (200, False)):
        refused = deepcopy(save)
        refused.rupees = rupees
        assert_refused(charts, MEDIGORON, refused, accept=accept)
    assert_native_sale(charts, MEDIGORON, save)
    # The replacement takes the broken Knife; the shuffled Hammer is not given again.
    assert save == Save(0, pouch={GIANT: 1, "Item_Hammer": 1}, flags={flag(MEDIGORON): True})


def test_medigoron_identity_knife_is_the_check_once_then_native_replacements():
    charts = seed()
    owner = Save(200, pouch={BIGGORON: 1})
    talk(charts, MEDIGORON_FLOW, owner)  # an uncollected check is never Biggoron's refusal
    assert owner == Save(0, pouch={BIGGORON: 1, GIANT: 1}, flags={flag(MEDIGORON): True})
    save = Save(200)
    talk(charts, MEDIGORON_FLOW, save)
    assert save == Save(0, pouch={GIANT: 1}, flags={flag(MEDIGORON): True})
    save = save.reload()
    save.rupees = 200
    assert_refused(charts, MEDIGORON, save)  # the intact Knife
    break_knife(save)
    assert_native_sale(charts, MEDIGORON, save)
    assert save == Save(0, pouch={GIANT: 1}, flags={flag(MEDIGORON): True})


# --- preload registration -----------------------------------------------------------------------------------------


def test_granny_preload_registers_the_get_scene_only_for_a_non_refill_reward():
    rows = [
        {"__RowId": "Npc_Hylia_053_Adult_D_T", "SubFlowList": ["Dm_SY_GetInEvent"]},
        {"__RowId": "Npc_Hylia_053_Adult_Near_D_T", "SubFlowList": ["Dm_SY_GetInEvent"]},
    ]
    assert gifts.ANALYZED not in transforms({})
    out = byml.read(transforms({GRANNY: "Iron Boots"})[gifts.ANALYZED](byml.write(rows)))
    assert out == [{**rows[0], "SubFlowList": ["Dm_SY_Get", "Dm_SY_GetInEvent"]}, rows[1]]
