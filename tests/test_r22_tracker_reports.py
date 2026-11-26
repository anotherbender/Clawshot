"""Round 22 tracker reports (plans/rounds/r22-tracker-2.md) through the tracker's own seams: the save's logic
inventory, ``SeedLogic.search`` and ``SeedLogic.annotate``. Saves are synthetic; worlds are tiny synthetic ones or the
dump-free seed-world builder's. No seed is generated and nothing is read from the game."""

import pytest
from test_tracker_logic_inventory import seed, stock
from test_tracker_state import parse

from clawshot.generate import Settings
from clawshot.patch.logic_world import logic_world
from clawshot.tracker.logic import LogicWorld, SeedLogic, inventory, load_mapping, search_items
from clawshot.tracker.seeds import Check
from clawshot.world import Search, build_world
from clawshot.world.rules import ADULT, CHILD

OPEN = {"child": True, "adult": True, "either": True}
CLOSED = {"child": False, "adult": False, "either": False}
ADULT_ONLY = {"child": False, "adult": True, "either": True}

GOHMA, GATE = "Defeat Queen Gohma", "Kakariko Village Gate Open"
# Their native saved Bools (GameDataList Product110, default false): the Gohma outro and the Kakariko guard's gate.
GOHMA_FLAG, GATE_FLAG = "HavePlayedEvent.Dm_Deku_BossOut", "Npc_Hylia_Soldier_003_GateOpen"
GUARD_STEP = "Show Zelda's Letter to the Kakariko guard"
DARUNIA = "HavePlayedEvent.Dm_Goron_0030"
BRACELET = "Armor_Child_Gauntlet_Goron"  # Goron's Bracelet's pouch actor (tracker.state strength tier 1)


def tracker(world, settings=None):
    return SeedLogic(LogicWorld(True, None, settings or Settings(), world))


def report(logic, areas, bools=None, ints=None, run_seed=None):
    """``logic.annotate`` on a state whose areas (name -> check ids) list each check as not collected."""
    state = {
        "areas": [
            {"name": name, "checks": [{"id": check, "collected": False} for check in checks]}
            for name, checks in areas.items()
        ]
    }
    logic.annotate(state, run_seed or seed(), parse(bools or {}, ints or {}))
    return state


def rows(state):
    return {check["id"]: check for area in state["areas"] for check in area["checks"]}


def heads(state):
    return {area["name"]: area for area in state["areas"]}


def vanilla(state):
    return {check["id"]: check for area in state["vanilla_areas"] for check in area["checks"]}


@pytest.fixture(scope="module")
def closed_world():
    """The default seed world's (settings, world): closed forest and Kakariko gate, unshuffled shops and gifts."""
    return logic_world(Settings())


# --- 1. Saved-only story gates: Queen Gohma's outro and the guard shown Zelda's Letter.
GEAR = stock("Weapon_Sword_Kokiri") | stock("Weapon_Shield_Deku") | stock("Item_ZeldaLetter")
GATE_AREAS = {"Forest": ["Forest Chest"], "Field": ["Field Chest"], "Behind Gate": ["Mask Shop Check"]}


def gate_world():
    """Both events under their exact logic names, each derivable from :data:`GEAR`."""
    return build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {"Kokiri Sword": {}, "Deku Shield": {}, "Zeldas Letter": {}},
            "regions": [
                {
                    "name": "Root",
                    "events": {GATE: "age == 'child' and Zeldas_Letter"},
                    "exits": {"Deku Tree": "True", "Hyrule Field": f"'{GOHMA}'", "Kak Behind Gate": f"'{GATE}'"},
                    "locations": {"Forest Chest": {"type": "Chest", "rule": "True"}},
                },
                {"name": "Deku Tree", "events": {GOHMA: "Kokiri_Sword and Deku_Shield"}},
                {"name": "Hyrule Field", "locations": {"Field Chest": {"type": "Chest", "rule": "True"}}},
                {"name": "Kak Behind Gate", "locations": {"Mask Shop Check": {"type": "NPC", "rule": "True"}}},
            ],
        }
    )


def test_gear_that_could_earn_a_saved_only_event_does_not_open_its_checks():
    world = gate_world()
    unplayed = {GOHMA_FLAG: False, GATE_FLAG: False}
    state = report(tracker(world), GATE_AREAS, unplayed, GEAR)
    found, areas = rows(state), heads(state)
    assert found["Forest Chest"]["in_logic"] == OPEN
    assert found["Field Chest"]["in_logic"] == CLOSED
    assert found["Mask Shop Check"]["in_logic"] == CLOSED
    # Each closed area names the one undone saved step that would open it; an open area names none.
    assert areas["Field"]["after_events"] == dict.fromkeys(("child", "adult", "either"), [GOHMA])
    assert areas["Behind Gate"]["after_events"] == dict.fromkeys(("child", "adult", "either"), [GUARD_STEP])
    assert "after_events" not in areas["Forest"]
    # The generator's world keeps both events, and its own search still derives them from the same inventory.
    assert {GOHMA, GATE} <= {event.name for event in world.events}
    inv = inventory(seed(), parse(unplayed, GEAR), world)
    assert {"Kokiri Sword", "Deku Shield", "Zeldas Letter"} <= set(inv.counts)
    direct = Search(world, search_items(inv, world))
    assert direct.holds(GOHMA) and direct.holds(GATE)
    assert direct.can_access(world.locations["Field Chest"]) and direct.can_access(world.locations["Mask Shop Check"])


def test_a_saved_flip_reopens_its_checks_and_unsetting_it_closes_them_again():
    logic = tracker(gate_world())  # one session's logic across save polls
    for gohma, gate in ((False, False), (True, False), (True, True), (False, False)):
        state = report(logic, GATE_AREAS, {GOHMA_FLAG: gohma, GATE_FLAG: gate}, GEAR)
        found, areas = rows(state), heads(state)
        assert found["Field Chest"]["in_logic"] == (OPEN if gohma else CLOSED), (gohma, gate)
        assert found["Mask Shop Check"]["in_logic"] == (OPEN if gate else CLOSED), (gohma, gate)
        assert areas["Field"].get("after_events", {}).get("child") == (None if gohma else [GOHMA])
        assert areas["Behind Gate"].get("after_events", {}).get("child") == (None if gate else [GUARD_STEP])


def test_unreadable_saved_gates_stay_conservative():
    state = report(tracker(gate_world()), GATE_AREAS, {}, GEAR)
    found = rows(state)
    assert found["Field Chest"]["in_logic"] == CLOSED
    assert found["Mask Shop Check"]["in_logic"] == CLOSED
    assert {f"story: {GOHMA}", f"story: {GATE}"} <= set(state["logic"]["unknown_items"])
    # A hint names only a step the save shows undone; an unread one is not claimed either way.
    assert not any("after_events" in area for area in state["areas"])


CHILD_GEAR = stock("Weapon_Sword_Kokiri") | stock("Weapon_Shield_Deku") | stock("Weapon_Range_SlingShot")


def test_the_closed_forest_waits_for_the_saved_gohma_outro_in_a_seed_world(closed_world):
    settings, world = closed_world
    logic = tracker(world, settings)
    malon = world.locations["HC Malon Egg"]  # outside the closed forest, open to a child once out
    areas = {"Hyrule Castle": [malon.name]}
    before = report(logic, areas, {GOHMA_FLAG: False, GATE_FLAG: False}, CHILD_GEAR)
    assert rows(before)[malon.name]["in_logic"]["child"] is False
    assert heads(before)["Hyrule Castle"]["after_events"]["child"] == [GOHMA]
    # Sword, shield and Slingshot are what the generator's search derives the fight from.
    inv = inventory(seed(), parse({GOHMA_FLAG: False}, CHILD_GEAR), world)
    direct = Search(world, search_items(inv, world))
    assert direct.holds(GOHMA) and direct.can_access(malon, CHILD)
    done = report(logic, areas, {GOHMA_FLAG: True, GATE_FLAG: False}, CHILD_GEAR)
    assert rows(done)[malon.name]["in_logic"]["child"] is True
    assert "after_events" not in heads(done)["Hyrule Castle"]
    unread = report(logic, areas, {GATE_FLAG: False}, CHILD_GEAR)
    assert rows(unread)[malon.name]["in_logic"]["child"] is False


def test_keaton_waits_for_the_saved_guard_letter_show_not_the_held_letter(closed_world):
    settings, world = closed_world
    logic = tracker(world, settings)
    keaton = world.locations["Market Mask Shop Item 6"]
    assert keaton.vanilla == "Keaton Mask"
    areas = {"Market": [keaton.name]}
    held = CHILD_GEAR | stock("Item_ZeldaLetter")
    out_of_forest = {GOHMA_FLAG: True}
    before = report(logic, areas, out_of_forest | {GATE_FLAG: False}, held)
    assert rows(before)[keaton.name]["in_logic"]["child"] is False
    assert heads(before)["Market"]["after_events"]["child"] == [GUARD_STEP]
    inv = inventory(seed(), parse(out_of_forest | {GATE_FLAG: False}, held), world)
    assert inv.counts["Zeldas Letter"] == 1
    direct = Search(world, search_items(inv, world))
    assert direct.holds(GATE) and direct.can_access(keaton, CHILD)
    shown = report(logic, areas, out_of_forest | {GATE_FLAG: True}, held)
    assert rows(shown)[keaton.name]["in_logic"]["child"] is True
    unread = report(logic, areas, out_of_forest, held)
    assert rows(unread)[keaton.name]["in_logic"]["child"] is False


# --- 2. Vanilla shops with Shop shuffle off: a shelf's own item is a priced purchase.
SHIELD_SHOP = "KF Shop Item 7"  # shops.toml: KF Shop, Shop_Weapon_Shield_Deku, 40 rupees in each seller copy
SHIELD_AREAS = {"Kokiri Forest": ["Shield Check", "Shield Chest"]}
RUPEES = "PlayerStatus.CurrentRupee"


def shop_world():
    """The real Kokiri shield shelf in a tiny world, beside a check that needs a Deku Shield and a reachable chest whose
    vanilla item is one (a fixed pick-up the tracker must not credit)."""
    return build_world(
        {
            "start": "Root",
            "goal": "True",
            "items": {"Deku Shield": {}},
            "regions": [
                {
                    "name": "Root",
                    "exits": {"KF Kokiri Shop": "True"},
                    "locations": {
                        "Shield Check": {"type": "Chest", "rule": "'Deku Shield'"},
                        "Shield Chest": {"type": "Chest", "rule": "True", "vanilla": "Deku Shield"},
                    },
                },
                {
                    "name": "KF Kokiri Shop",
                    "locations": {SHIELD_SHOP: {"type": "Shop", "rule": "True", "vanilla": "Deku Shield"}},
                },
            ],
        }
    )


def shield_rows(logic, ints, bools=None):
    return rows(report(logic, SHIELD_AREAS, bools, ints))


def purchase(world, price, budget):
    sources = [
        {
            "item": "Deku Shield",
            "sources": [
                {
                    "region": "KF Kokiri Shop",
                    "ages": [CHILD, ADULT],
                    "rule": world.locations[SHIELD_SHOP].rule.text,
                    "purchase": {"location": SHIELD_SHOP, "shop": "KF Shop", "price": price, "budget": budget},
                }
            ],
        }
    ]
    return {"child": sources, "adult": sources, "either": sources}


SHIELD_PRICES = [pytest.param(True, 10, id="cheap-shield"), pytest.param(False, 40, id="vanilla-price")]


@pytest.mark.parametrize(("cheap", "price"), SHIELD_PRICES)
def test_an_unshuffled_shield_shelf_is_bought_within_the_saved_rupees(cheap, price):
    world = shop_world()
    logic = tracker(world, Settings(shuffle=("Chest",), cheap_deku_shield=cheap))
    short = shield_rows(logic, {RUPEES: price - 1})
    assert short["Shield Chest"]["in_logic"] == OPEN  # its vanilla shield is never credited
    assert short["Shield Check"]["in_logic"] == CLOSED and "assumed_sources" not in short["Shield Check"]
    enough = shield_rows(logic, {RUPEES: price})["Shield Check"]
    assert enough["in_logic"] == OPEN
    assert enough["assumed_sources"] == purchase(world, price, "saved rupees")


@pytest.mark.parametrize(("cheap", "price"), SHIELD_PRICES)
def test_without_saved_rupees_the_purchase_is_judged_by_wallet_capacity(cheap, price):
    world = shop_world()
    check = shield_rows(tracker(world, Settings(shuffle=("Chest",), cheap_deku_shield=cheap)), {})["Shield Check"]
    assert check["in_logic"] == OPEN
    assert check["assumed_sources"] == purchase(world, price, "wallet capacity")


def test_shuffled_shops_give_no_vanilla_purchase_and_no_fixed_pick_up_is_credited():
    logic = tracker(shop_world(), Settings(shuffle=("Chest", "Shop")))
    for ints in ({RUPEES: 999}, {}):
        found = shield_rows(logic, ints)
        assert found["Shield Chest"]["in_logic"] == OPEN
        assert found["Shield Check"]["in_logic"] == CLOSED and "assumed_sources" not in found["Shield Check"], ints


@pytest.mark.parametrize("shuffle", [("Chest",), ("Chest", "Shop")])
def test_a_physical_shield_counts_whatever_the_shop_setting_and_rupees(shuffle):
    logic = tracker(shop_world(), Settings(shuffle=shuffle))
    held = shield_rows(logic, stock("Weapon_Shield_Deku") | {RUPEES: 0})["Shield Check"]
    eaten = shield_rows(logic, stock("Weapon_Shield_Deku", 0) | {RUPEES: 0}, {"IsGet.Weapon_Shield_Deku": True})
    for check in (held, eaten["Shield Check"]):  # held now, or acquired once and since eaten or burnt
        assert check["in_logic"] == OPEN and "assumed_sources" not in check


# --- 3. Darunia's vanilla bonus gives nothing once Goron's Bracelet is owned: shown empty, reversibly.
def darunia(logic, ints, bools, run_seed=None):
    return vanilla(report(logic, {}, bools, ints, run_seed)).get("GC Darunias Joy")


def test_an_owned_bracelet_shows_the_unshuffled_darunia_bonus_empty_and_reverses(closed_world):
    settings, world = closed_world
    logic = tracker(world, settings)
    unplayed = {DARUNIA: False}
    for count in (1, 0, 1):  # one session: the empty state follows the save, nothing sticks
        row = darunia(logic, stock(BRACELET, count), unplayed)
        assert row["item"] == "Goron Bracelet"
        assert row["kind"] == "gift"
        if count:
            assert (row["collected"], row.get("empty"), row["basis"]) == (True, True, "empty_bonus")
            assert "in_logic" not in row
        else:
            assert (row["collected"], row["basis"]) == (False, "inventory") and "empty" not in row
    unread = darunia(logic, {}, unplayed)
    assert unread["collected"] is False and "empty" not in unread


@pytest.mark.parametrize("gauntlets", ["Armor_Adult_Gauntlet_Silver", "Armor_Adult_Gauntlet_Gold"])
def test_adult_gauntlets_alone_do_not_empty_darunias_bonus(closed_world, gauntlets):
    settings, world = closed_world
    logic = tracker(world, settings)
    for child_stock in (stock(BRACELET, 0), {}):  # no Bracelet, or its stock unreadable
        row = darunia(logic, child_stock | stock(gauntlets), {DARUNIA: False})
        assert row["collected"] is False and "empty" not in row, child_stock


def test_the_saved_darunia_flag_is_the_actual_completion_not_an_empty_bonus(closed_world):
    settings, world = closed_world
    logic = tracker(world, settings)
    for ints in (stock(BRACELET), stock(BRACELET, 0)):
        row = darunia(logic, ints, {DARUNIA: True})
        assert (row["collected"], row["basis"]) == (True, "inventory") and "empty" not in row, ints


def test_a_shuffled_darunia_reward_is_never_inferred_empty(closed_world):
    settings, world = closed_world
    # Were the gift ever shuffled (normal seeds anchor it), its reward could be anything but the Bracelet.
    gift = Check("GC Darunias Joy", "Darunia", "", "Goron City", None, "gift", "x", "x", "named_bool", (DARUNIA,))
    state = report(
        tracker(world, settings), {"Goron City": [gift.location]}, {DARUNIA: False}, stock(BRACELET), seed([gift])
    )
    entry = rows(state)[gift.location]
    assert entry["collected"] is False and "empty" not in entry and "basis" not in entry
    assert gift.location not in vanilla(state)


# --- 4. Dodongo's Cavern: held Bracelet, no Bomb Bag, through the tracker's inventory and search.
@pytest.fixture(scope="module")
def two_age_world():
    """A seed world's (settings, world) both ages reach without combat: open forest and Door of Time, free time travel;
    Master Sword shuffle so an adult has no implicit sword."""
    return logic_world(
        Settings(
            shuffle=("Chest",),
            forest="open",
            door_of_time="open",
            shuffle_master_sword=True,
            logic={"free_time_travel": True},
        )
    )


STORY = load_mapping().story
# The saved story Bools the open Door of Time reads ('Met Child Zelda' and 'Field Owl Arrival').
TIME = {STORY[name].flag: True for name in ("Met Child Zelda", "Field Owl Arrival")}
NO_BAG = {f"PouchData.Item_BombBag_{size}.StockNum": 0 for size in ("Small", "Medium", "Large")}
# Behind the entrance and lobby Bomb Flower walls (dc_bomb_flower, Progressive_Strength_Upgrade).
FLOWER_CHECKS = (
    "Dodongos Cavern Map Chest",
    "Dodongo Cavern Room 1 Chest (TBox_Rupee_Blue)",
    "Dodongos Cavern Deku Scrub Lobby",
    "Dodongos Cavern Deku Scrub Side Room Near Dodongos",
    "Dodongos Cavern Lower Lizalfos Hidden Recovery Heart",
)
# Past the torch-lit staircase and the Lizalfos and eye switches: plain arrows, then flowers again.
BOW_CHECKS = (
    "Dodongos Cavern Compass Chest",
    "Dodongos Cavern Bomb Flower Platform Chest",
    "Dodongo Cavern Room 5 Chest (TBox_Rupee_Red)",
    "Dodongo Cavern Room 16 Chest (Item_ScrubBusinessSeed)",
    "Dodongos Cavern Bomb Bag Chest",
)
# Walls no flower reaches: explosives or the Hammer only.
BLAST_CHECKS = ("Dodongo Cavern Room 10 Chest (Item_ScrubBusinessSeed)", "Dodongos Cavern End of Bridge Chest")
DC_AREAS = {"Dodongos Cavern": [*FLOWER_CHECKS, *BOW_CHECKS, *BLAST_CHECKS]}


@pytest.mark.parametrize(
    ("weapons", "opened"),
    [
        pytest.param({}, FLOWER_CHECKS, id="bracelet"),
        pytest.param(stock("Weapon_Range_Bow"), FLOWER_CHECKS + BOW_CHECKS, id="bracelet-and-bow"),
    ],
)
def test_an_adult_bracelet_without_a_bag_uses_the_cavern_flowers(two_age_world, weapons, opened):
    settings, world = two_age_world
    logic = tracker(world, settings)
    saved, ints = TIME | {DARUNIA: False}, NO_BAG | stock(BRACELET) | weapons
    inv = inventory(seed(), parse(saved, ints), world)
    assert inv.counts["Progressive Strength"] == 1
    assert "Goron Bracelet" not in inv.counts and "Progressive Bomb Bag" not in inv.counts
    found = rows(report(logic, DC_AREAS, saved, ints))
    for name in DC_AREAS["Dodongos Cavern"]:
        assert found[name]["in_logic"] == (ADULT_ONLY if name in opened else CLOSED), name
    # No tracker-only route: the generator's search on the same world and items agrees with every row.
    direct = Search(world, search_items(inv, world))
    for name, entry in found.items():
        for age in (CHILD, ADULT):
            assert entry["in_logic"][age] == direct.can_access(world.locations[name], age), (name, age)
    assert not logic.search(inv).holds("Defeat King Dodongo")


def test_child_cavern_lift_comes_from_darunias_gift_not_a_bracelet_copy(two_age_world):
    """R14's approved exception (plans/rounds/r14-progressive.md), kept in round 22: a chest Bracelet lifts for a child
    in game, but the closed-door return kit keeps strength copies adult-only, so child logic credits only Darunia's
    native gift."""
    settings, world = two_age_world
    logic = tracker(world, settings)
    saved, ints = TIME | {GATE_FLAG: True}, NO_BAG | stock(BRACELET)  # Death Mountain's gate is open
    copy = inventory(seed(), parse(saved | {DARUNIA: False}, ints), world)
    assert "Goron Bracelet" not in copy.counts
    search = logic.search(copy)
    assert search.can_reach("Death Mountain", CHILD) and not search.can_reach("Dodongos Cavern Beginning", CHILD)
    copied = rows(report(logic, DC_AREAS, saved | {DARUNIA: False}, ints))
    gift = rows(report(logic, DC_AREAS, saved | {DARUNIA: True}, ints))
    for name in FLOWER_CHECKS:
        assert copied[name]["in_logic"] == ADULT_ONLY, name
        assert gift[name]["in_logic"]["child"] is True, name
