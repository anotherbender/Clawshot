"""Gold Skulltula sources in the headless tracker (plans/rounds/r15-tokens-spec.md sections 3.4 and 5): synthetic
seeds and saves built here, read through the real seed loader, state builder and polling session."""

import json
import re

import pytest
from test_tracker_options import NODE, render_tracker
from test_tracker_saves import ACCOUNT, SECOND, write_slot
from test_tracker_state import build_save, checks, make_seed

from clawshot import save
from clawshot.tracker import SeedError, TrackerSession, build_state, load_seed, seeds
from clawshot.tracker.seeds import SOURCE_SAVE_TYPE, SOURCE_SAVE_VERSION, Place
from clawshot.ui.server import ASSETS
from clawshot.ui.tracker import TrackerController

TREE, TOWER, FIELD = 341792603838029977, 2730878115209290675, 2177746409373494991
FIELD_COMPANION = 2177746409373494989  # spec section 2.1: H xor 2, which for this Hash is H - 2, not H + 2
HOUSE_WINDOW = 15889002414176907668  # data/locations.toml: LLR GS House Window's census Hash
CHEST = 14818888396401495482
CHEST_FLAG = f"IsTreasureBoxOpen.{CHEST}"
STOCK = "PouchData.Item_Token_Gold.StockNum"
CHILD, ADULT = "Banc/Test/Test_Child_Static.bcett.byml.zs", "Banc/Test/Test_Adult_Static.bcett.byml.zs"
SHIELD_DROP = "Obj_GoldSkulltulaDrop_Test_Shield"
SOURCES = ("Test GS Tree", "Test GS Tower", "Test GS Field")

PLACES = {
    "Test GS Tree": Place("Ranch", None, "Token"),
    "Test GS Tower": Place("Ranch", None, "Token"),
    "Test GS Field": Place("Field", None, "GS Token"),
    "Test Token Chest": Place("Forest", None, "Chest"),
    "Test Boss Heart": Place("Deku Tree", "Deku Tree", "BossHeart"),
}
PLACEMENTS = {
    "Test GS Tree": "Boomerang",
    "Test GS Tower": "Hylian Shield",
    "Test GS Field": "Gold Skulltula Token",
    "Test Token Chest": "Gold Skulltula Token",
    "Test Boss Heart": "Heart Container",
}
LOCATIONS = {
    "Test GS Tree": {"name": "Ranch Tree Skulltula", "where": "Ranch", "oot_randomizer_name": ""},
    "Test GS Tower": {"name": "Ranch Tower Skulltula", "where": "Ranch", "oot_randomizer_name": ""},
    "Test GS Field": {"name": "Field Tree Skulltula", "where": "Field", "oot_randomizer_name": ""},
    "Test Token Chest": {"name": "Grotto Chest", "where": "Forest", "ids": [str(CHEST)]},
    "Test Boss Heart": {"name": "Boss Pickup", "where": "Deku", "ids": ["555"]},
}


def token_row(location, source, item, pickup, drop, files=(CHILD, ADULT)):
    """A ``patch.tokens`` row as the patch writes it; the tracker reads only ``location`` and ``id``."""
    return {
        "location": location,
        "id": str(source),
        "name": location,
        "files": list(files),
        "item": item,
        "pickup": pickup,
        "drop_actor": drop,
    }


PATCH = {
    "changes": [
        {
            "location": "Test Token Chest",
            "id": str(CHEST),
            "chest": "Obj_TBox_A_01",
            "item": "Gold Skulltula Token",
            "drop_actor": ["Item_Rupee_Blue", "Item_Token_Gold"],
        }
    ],
    "unchanged": [],
    "tokens": [
        token_row("Test GS Field", FIELD, "Gold Skulltula Token", "Item_Token_Gold", None),
        token_row("Test GS Tower", TOWER, "Hylian Shield", "Obj_Shield_Hylian", SHIELD_DROP),
        token_row("Test GS Tower", TOWER, "Hylian Shield", "Obj_Shield_Hylian", SHIELD_DROP, (ADULT,)),  # a copy
        token_row("Test GS Tree", TREE, "Boomerang", "Item_Boomerang", "Obj_GoldSkulltulaDrop_Test_Boomerang"),
    ],
}


@pytest.fixture
def token_places(monkeypatch):
    monkeypatch.setattr(seeds, "location_index", lambda: PLACES)
    return PLACES


def pair(source):
    return source, source ^ 2


def token_save(keys=(), stock=9, bools=None, **options) -> save.Save:
    """A save in the audited layout unless ``options`` say otherwise; ``stock`` None leaves out the token stock."""
    options.setdefault("version", SOURCE_SAVE_VERSION)
    options.setdefault("save_type", SOURCE_SAVE_TYPE)
    ints = {} if stock is None else {STOCK: stock}
    return save.read(build_save({CHEST_FLAG: False, **(bools or {})}, ints, keys, **options))


def token_seed(tmp_path, patch=PATCH, name="tokens"):
    return load_seed(make_seed(tmp_path, PLACEMENTS, LOCATIONS, patch, name=name))


def states(state, names=(*SOURCES, "Test Token Chest")):
    found = checks(state)
    return tuple(found[name]["collected"] for name in names)


def test_each_source_is_one_check_by_its_stable_hash(tmp_path, token_places):
    seed = token_seed(tmp_path)
    by_name = {check.location: check for check in seed.checks}
    assert {name: (c.kind, c.method, c.hashes, c.flags) for name, c in by_name.items() if c.kind == "token"} == {
        "Test GS Tree": ("token", "source_pair", (TREE,), ()),
        "Test GS Tower": ("token", "source_pair", (TOWER,), ()),  # two copy rows, one source, one check
        "Test GS Field": ("token", "source_pair", (FIELD,), ()),  # a native-kept token has its row too
    }
    assert len(seed.checks) == len(PLACEMENTS)
    assert by_name["Test Token Chest"].flags == (CHEST_FLAG,)  # a token chest stays a chest
    assert not any(str(h) in flag for c in seed.checks for flag in c.flags for h in (TREE, TOWER, FIELD))
    assert seed.added_flags == ()  # Token shuffle adds no saved flag: seed identity is unchanged
    reordered = {**PATCH, "tokens": PATCH["tokens"][::-1]}
    assert token_seed(tmp_path, reordered, "reordered").checks == seed.checks


def test_source_completion_and_token_stock_are_independent(tmp_path, token_places):
    seed = token_seed(tmp_path)
    tree, tower, field = pair(TREE), pair(TOWER), pair(FIELD)
    steps = (
        # (Bool64bitKey list, chest open, stock) -> (tree, tower, field, chest), tokens
        ((), False, 9, (False, False, False, False), 9),  # nothing collected yet: uncollected, not unknown
        (tree, False, 9, (True, False, False, False), 9),  # Boomerang at a source: done, count unchanged
        ((*tree, *tower), False, 9, (True, True, False, False), 9),  # Hylian Shield: count still unchanged
        ((*tree, *tower), True, 10, (True, True, False, True), 10),  # chest token: +1, no source completes
        ((*tree, *tower, *field), True, 11, (True, True, True, True), 11),  # native source token
    )
    for keys, opened, stock, expected, tokens in steps:
        state = build_state(seed, token_save(keys, stock, {CHEST_FLAG: opened, "IsGet.Item_Token_Gold": True}))
        assert (states(state), state["tokens"]) == (expected, tokens), keys
        found = checks(state)
        assert all(found[name]["basis"] == "source_pair" for name in SOURCES)
        assert not any("Gold Skulltula" in warning for warning in state["warnings"])
    ranch = {area["name"]: area for area in state["areas"]}["Ranch"]
    assert (ranch["collected"], ranch["total"], ranch["unknown"]) == (2, 2, 0)

    # The count is the stock, never the number of collected sources, either way round.
    every = build_state(seed, token_save((*tree, *tower, *field), 0))
    assert (states(every)[:3], every["tokens"]) == ((True, True, True), 0)
    stocked = build_state(seed, token_save((), 100))  # the native maximum, tokens from sources this world lacks too
    assert (states(stocked)[:3], stocked["tokens"]) == ((False, False, False), 100)
    no_stock = build_state(seed, token_save(tree, None))
    assert (states(no_stock)[:3], no_stock["tokens"]) == ((True, False, False), None)


def test_partial_pairs_and_unaudited_layouts_are_unknown(tmp_path, token_places):
    seed = token_seed(tmp_path)
    assert FIELD ^ 2 == FIELD_COMPANION == FIELD - 2
    for keys, name in (([TREE], "Test GS Tree"), ([TREE ^ 2], "Test GS Tree"), ([FIELD, FIELD + 2], "Test GS Field")):
        entry = checks(build_state(seed, token_save(keys)))[name]
        assert entry["collected"] is None and "only one" in entry["reason"], keys
        assert entry["basis"] is None and "item" not in entry
    assert checks(build_state(seed, token_save([FIELD, FIELD_COMPANION])))["Test GS Field"]["collected"] is True

    layouts = {
        "no save": None,
        "another version": token_save(pair(TREE), version=SOURCE_SAVE_VERSION + 1),
        "another list type": token_save(pair(TREE), save_type=SOURCE_SAVE_TYPE ^ 1),
        "no list": token_save(save_type=None),
        "another build": token_save(pair(TREE), bool_total=5),
    }
    for why, value in layouts.items():
        state = build_state(seed, value)
        found = checks(state)
        assert all(found[name]["collected"] is None and found[name]["reason"] for name in SOURCES), why
        assert state["tokens"] == (None if value is None else 9), why  # the stock is still read
        assert any("Gold Skulltula sources show as unknown" in w for w in state["warnings"]) is (value is not None)
    assert "version 0x2d80eb" in checks(build_state(seed, layouts["another version"]))["Test GS Tree"]["reason"]


def test_generic_floor_and_chest_reads_are_unchanged(tmp_path, token_places):
    seed = token_seed(tmp_path)
    audited = checks(build_state(seed, token_save()))
    assert audited["Test Boss Heart"]["collected"] is None  # an unset placement Hash is never "not collected"
    assert audited["Test Token Chest"]["collected"] is False
    assert checks(build_state(seed, token_save([555])))["Test Boss Heart"]["collected"] is True
    elsewhere = checks(build_state(seed, token_save([555], version=1)))  # any layout, as before Token shuffle
    assert (elsewhere["Test Boss Heart"]["collected"], elsewhere["Test Token Chest"]["collected"]) == (True, False)


def test_census_and_spoiler_rows_without_a_world_location(tmp_path, monkeypatch):
    places = {
        "LLR GS House Window": Place("Ranch", None, "GS Token"),
        "Test GS Nowhere": Place("Field", None, "GS Token"),
    }
    monkeypatch.setattr(seeds, "location_index", lambda: places)
    placements = {
        "LLR GS House Window": "Boomerang",  # no patch.tokens row: the census names it
        "Test GS Nowhere": "Hylian Shield",  # neither does: no record
        "HF GS Lone Tree": "Gold Skulltula Token",  # a spoiler row for a source this world does not have
    }
    patch = {"tokens": [{"location": "HF GS Lone Tree", "id": str(FIELD)}]}
    seed = load_seed(make_seed(tmp_path, placements, {}, patch))
    by_name = {check.location: check for check in seed.checks}
    assert (by_name["LLR GS House Window"].method, by_name["LLR GS House Window"].hashes) == (
        "source_pair",
        (HOUSE_WINDOW,),
    )
    assert (by_name["Test GS Nowhere"].kind, by_name["Test GS Nowhere"].method) == ("token", "none")
    lone = by_name["HF GS Lone Tree"]
    assert (lone.kind, lone.hashes, lone.area) == ("token", (FIELD,), "Other")
    assert any("not in this version's world data" in warning for warning in seed.warnings)

    found = checks(build_state(seed, token_save(pair(HOUSE_WINDOW))))
    assert (found["LLR GS House Window"]["collected"], found["HF GS Lone Tree"]["collected"]) == (True, False)
    assert found["Test GS Nowhere"]["collected"] is None and "census" in found["Test GS Nowhere"]["reason"]
    raw = load_seed(make_seed(tmp_path, {"LLR GS House Window": "Boomerang"}, {}, {}, name="raw"))
    assert raw.checks[0].hashes == (HOUSE_WINDOW,)  # a spoiler without the patch's token rows


@pytest.mark.parametrize(
    ("tokens", "message"),
    [
        ({"Test GS Tree": str(TREE)}, "not a list"),
        ([{"id": str(TREE)}], "without a location"),
        ([{"location": "Test GS Tree", "id": "0"}], "valid decimal source Hash"),
        ([{"location": "Test GS Tree", "id": "2"}], "valid decimal source Hash"),
        ([{"location": "Test GS Tree", "id": str(1 << 64)}], "valid decimal source Hash"),
        ([{"location": "Test GS Tree", "id": "\u0661\u0662"}], "valid decimal source Hash"),
        ([{"location": "Test GS Tree", "id": TREE}], "valid decimal source Hash"),
        ([{"location": "Test Token Chest", "id": str(TREE)}], "both a chest and a Gold Skulltula source"),
    ],
)
def test_malformed_token_rows_refuse_the_seed(tmp_path, token_places, tokens, message):
    with pytest.raises(SeedError, match=message):
        token_seed(tmp_path, {**PATCH, "tokens": tokens})


def test_uncollected_source_rewards_stay_hidden(tmp_path, token_places):
    seed = token_seed(tmp_path)
    state = build_state(seed, token_save(pair(TREE)))
    found = checks(state)
    assert (found["Test GS Tree"]["item"], found["Test GS Tree"]["item_label"]) == ("Boomerang", "Boomerang")
    assert all("item" not in found[name] and "item_label" not in found[name] for name in SOURCES[1:])
    text = json.dumps(state)
    assert "Obj_GoldSkulltulaDrop" not in text and str(TOWER) not in text and str(FIELD) not in text
    shown = checks(build_state(seed, token_save(pair(TREE)), show_locations=True))
    assert shown["Test GS Tower"]["item"] == "Hylian Shield" and shown["Test GS Tower"]["collected"] is False


def test_session_follows_sources_and_stock_in_the_seeds_save_folder(tmp_path, token_places):
    root = make_seed(tmp_path, PLACEMENTS, LOCATIONS, PATCH)
    folder = root / "user" / "save" / ACCOUNT

    def write(keys, opened, stock, when, **options):
        options.setdefault("version", SOURCE_SAVE_VERSION)
        write_slot(folder, 1, build_save({CHEST_FLAG: opened}, {STOCK: stock}, keys, **options), when * SECOND)

    write(pair(TREE), False, 9, 10)
    session = TrackerSession()
    first = session.configure(root)
    assert (first["status"], first["selected_slot"]) == ("ok", "slot_01")
    assert (states(first["state"]), first["state"]["tokens"]) == ((True, False, False, False), 9)

    write(pair(TREE), True, 10, 11)
    opened = session.snapshot()
    assert (states(opened["state"]), opened["state"]["tokens"]) == ((True, False, False, True), 10)
    assert opened["revision"] > first["revision"]

    write(pair(TREE), True, 10, 12, version=1)
    other = session.snapshot()
    assert states(other["state"]) == (None, None, None, True) and other["state"]["tokens"] == 10
    assert any("Gold Skulltula sources show as unknown" in w for w in other["state"]["warnings"])


def test_skulltula_check_totals_count_sources_apart_from_the_stock(tmp_path, token_places):
    seed = token_seed(tmp_path)
    cases = {
        "nothing collected": (token_save(), (0, 3, 0)),
        "non-token rewards at two sources": (token_save((*pair(TREE), *pair(TOWER)), 9), (2, 3, 0)),
        "one record of a pair": (token_save((*pair(TREE), FIELD)), (1, 3, 1)),
        "unaudited layout": (token_save(pair(TREE), version=1), (0, 3, 3)),
        "no save": (None, (0, 3, 3)),
    }
    for why, (value, expected) in cases.items():
        found = build_state(seed, value)["skulltula_checks"]
        assert (found["collected"], found["total"], found["unknown"]) == expected, why
    tokens_off = {name: PLACEMENTS[name] for name in ("Test Token Chest", "Test Boss Heart")}
    patch = {key: value for key, value in PATCH.items() if key != "tokens"}
    plain = load_seed(make_seed(tmp_path, tokens_off, LOCATIONS, patch, name="tokens-off"))
    assert build_state(plain, token_save())["skulltula_checks"] == {"collected": 0, "total": 0, "unknown": 0}


@pytest.mark.skipif(NODE is None, reason="Node is needed only for frontend rendering tests")
def test_tab_and_compact_obs_show_skulltula_checks_beside_the_token_count(tmp_path, token_places):
    """Round 17 item 5: each surface's rendered Collection line, from the real session and HTTP snapshots."""
    token = make_seed(tmp_path, PLACEMENTS, LOCATIONS, PATCH)
    tokens_off = {name: PLACEMENTS[name] for name in ("Test Token Chest", "Test Boss Heart")}
    patch = {key: value for key, value in PATCH.items() if key != "tokens"}
    plain = make_seed(tmp_path, tokens_off, LOCATIONS, patch, name="tokens-off")
    ints = {STOCK: 10, "PlayerStatus.MaxLife": 12, "PouchData.Obj_Heart_Piece.StockNum": 1}

    def write(root, keys, when):
        layout = {"version": SOURCE_SAVE_VERSION, "save_type": SOURCE_SAVE_TYPE}
        write_slot(root / "user" / "save" / ACCOUNT, 1, build_save({CHEST_FLAG: True}, ints, keys, **layout), when)

    write(token, (*pair(TREE), *pair(TOWER)), 10 * SECOND)
    write(plain, (), 10 * SECOND)
    controller = TrackerController()
    assert controller.session.configure(token)["status"] == "ok"
    surfaces = {
        "tab": (False, ""),
        "labelled OBS": (True, "#columns=4&labels=1&icons=1"),
        "compact OBS": (True, "#columns=4&labels=0&icons=1&transparent=0&sections=items,quest,dungeons"),
        "compact items and quest": (True, "#labels=0&sections=items,quest"),
    }

    def counts(obs, fragment):
        rendered = render_tracker(tmp_path, controller.snapshot(obs=obs), obs=obs, fragment=fragment)
        assert ("tracker-obs" in rendered["requested"]) is obs
        assert rendered["compact"] is ("labels=0" in fragment)
        return rendered["counts"]

    line = "Hearts 3 · Pieces 1 · Gold Skulltulas 10"
    shown = {name: counts(*surface) for name, surface in surfaces.items()}
    assert shown == {name: [line + " · Skulltula checks 2 / 3"] for name in surfaces}
    write(token, (*pair(TREE), TOWER), 11 * SECOND)  # one of the Tower's two records: unknown, not collected
    assert counts(*surfaces["compact OBS"]) == [line + " · Skulltula checks 1 / 3 (1 unknown)"]
    css = (ASSETS / "tracker.css").read_text(encoding="utf-8")
    hidden = [rule for rule, block in re.findall(r"([^{}]+)\{([^}]*)\}", css) if "display: none" in block]
    assert not [rule for rule in hidden if re.search(r"\.tracker-(counts|group|content)\b", rule)]

    assert controller.session.configure(plain)["status"] == "ok"  # Token off: no Skulltula checks, line unchanged
    assert {name: counts(*surface) for name, surface in surfaces.items()} == {name: [line] for name in surfaces}
