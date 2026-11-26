"""Castle custom items (Nothing, another player's item) and generated Gold Skulltula pickups in one seed output, on a
synthetic romfs: both producers' new packs and actor rows reach the common writer together, with no row, file or
size-table entry of one lost to the other.

The seed is a real Archipelago-style seed (``generate.from_placements``) with Chest and Token shuffled; the producers
are the real ones (``patch.custom_step``, ``tokens.seed_delivery``) and the output goes through ``write_seed``. The
transforms and new files are combined as ``make_seed`` combines them (Token delivery first, then the custom items, one
path-to-file mapping). ``make_seed`` itself needs every always-on step's native files; a combined native seed covers
its wiring."""

from dataclasses import dataclass
from pathlib import Path

import pytest
from test_custom_items import MODEL, PARAM, donor_pack
from test_tokens import (
    ADULT,
    BOOMERANG_PICKUP,
    CHEST,
    CHEST_NAME,
    CHILD,
    DEFINITIONS,
    GS_NAMES,
    LONE,
    SHIELD_PICKUP,
    TOWER,
    TREE,
    banc_tree,
    census,
    edit_byml,
    put,
    raw,
)
from test_tokens import world as world

from clawshot.census.definitions import Definition
from clawshot.census.gifts import FLOW_VERSIONS
from clawshot.census.scan import Location
from clawshot.formats import byml, evfl, msbt, rstb, sarc
from clawshot.formats.byml import F32, I32, U64
from clawshot.generate import Settings, from_placements
from clawshot.generate import tokens as token_policy
from clawshot.patch import SeedOutput, custom_items, custom_step, text, tokens, write_seed
from clawshot.patch import items as item_actors
from clawshot.patch.custom_items import Foreign
from clawshot.patch.plan import link, make_plan
from clawshot.patch.write import WrittenFile

LETTER = "Item_ZeldaLetter"  # the custom items' donor (``PARAM`` and ``MODEL`` are its pack's members)
LETTER_PACK = f"Pack/Actor/{LETTER}.pack.zs"
LETTER_PARAM_ENTRY, LETTER_MODEL_ENTRY = 5000, 6000
AP_CHEST, AP_CHEST_ID = "Test Archipelago Chest", 78
NOTHING = "Item_Clawshot_Nothing"
FOREIGN_ACTOR = "Item_Clawshot_AP_000"
CUSTOM_ACTORS = (FOREIGN_ACTOR, NOTHING)
PICKUPS = (BOOMERANG_PICKUP, SHIELD_PICKUP)
GET_FLOW = "Event/EventFlow/GetPouchContent.bfevfl.zs"
ARCHIVE = text.archive_path("USen")
FOREIGN = {AP_CHEST: Foreign("Kareem", "Morph Ball")}
PLACEMENTS = {
    GS_NAMES[TREE]: "Boomerang",
    GS_NAMES[TOWER]: "Hylian Shield",
    GS_NAMES[LONE]: token_policy.TOKEN_ITEM,
    CHEST_NAME: "Nothing",
    AP_CHEST: "Archipelago Item",
}
LETTER_ROWS = {
    tokens.ACTOR_INFO: {
        "ActorName": LETTER,
        "ClassName": "GameActor",
        "FmdbName": LETTER,
        "InstanceHeapSize": I32(40960),
        "ModelProjectName": LETTER,
        "__RowId": LETTER,
    },
    tokens.GAME_ACTOR_INFO: {"IsRespawn": False, "__RowId": LETTER},
    tokens.POUCH_ACTOR_INFO: {
        "BundleActorNum": I32(1),
        "PouchCategory": "KeyItem",
        "PouchGetType": "Large",
        "PouchSpecialDeal": "None",
        "PouchTabCategory": "KeyItem",
        "__RowId": LETTER,
    },
}
# The dungeon map's kind of content: given without entering the pouch (custom_items module docstring).
CUSTOM_POUCH = {
    "BundleActorNum": I32(1),
    "PouchCategory": "KeyItem",
    "PouchGetType": "Large",
    "PouchSpecialDeal": "NotPushToPouch",
    "PouchTabCategory": "KeyItem",
}


def by_id(row):
    return row["__RowId"].encode("utf-8")


def pack_path(actor):
    return f"Pack/Actor/{actor}.pack.zs"


def actor_param(actor):
    return f"Actor/{actor}.engine__actor__ActorParam.bgyml"


def rounded(size):
    return (size + 31) // 32 * 32


def chest(hash_):
    box = ("Obj_TBox_A_01", "Obj_Rupee_Blue", None, True)  # Gyaml, drop, event, saved
    return Location(hash_, "chest", "Test", None, (ADULT, CHILD), "both", (0.0, 0.0, 0.0), *box)


def get_flow():
    flowchart = evfl.Flowchart(
        "GetPouchContent",
        actors=[evfl.Actor("SystemTextNPC", actions=["EventTalk"])],
        events=[
            evfl.ActionEvent("Event16", 0, 0, 1, {"MessageId": custom_items.GET_MESSAGE}),
            evfl.ActionEvent("Event18", 0, 0, evfl.NONE, {"MessageId": custom_items.GET_CAPTION}),
        ],
        entry_points=[evfl.EntryPoint("DefaultGetMessage", 0)],
    )
    return evfl.write(evfl.EventFlowFile("GetPouchContent", flowchart=flowchart))


def combined_spec():
    """Three Skulltulas and two chests, all reachable."""
    checks = {name: {"type": "GS Token", "vanilla": token_policy.TOKEN_ITEM} for name in GS_NAMES.values()}
    checks[CHEST_NAME] = {"type": "Chest", "vanilla": "Boomerang"}
    checks[AP_CHEST] = {"type": "Chest", "vanilla": "Hylian Shield"}
    return {
        "start": "Root",
        "goal": "True",
        "items": {
            token_policy.TOKEN_ITEM: {"type": "Token"},
            "Boomerang": {},
            "Hylian Shield": {},
            "Nothing": {"class": "normal"},
            "Archipelago Item": {"class": "normal"},
        },
        "locations": checks,
        "regions": [{"name": "Root", "locations": {name: "True" for name in checks}}],
    }


def _insert_sorted(rows, row):
    rows.append(row)
    rows.sort(key=by_id)


@pytest.fixture
def combined(world):
    """The Skulltula romfs plus what the custom items read: the letter's pack and rows, a second chest, the get flow
    and one language archive."""
    put(world, LETTER_PACK, donor_pack())
    for path, row in LETTER_ROWS.items():
        edit_byml(world, path, lambda rows, row=row: _insert_sorted(rows, row))
    tree = banc_tree()
    tree["Actors"].append(
        {
            "Dynamic": {tokens.DROP: "Obj_Rupee_Blue"},
            "Gyaml": "Obj_TBox_A_01",
            "Hash": U64(AP_CHEST_ID),
            "Translate": [F32(9.0), F32(0.0), F32(0.0)],
        }
    )
    for path in (ADULT, CHILD):
        put(world, path, byml.write(tree))
    put(world, FLOW_VERSIONS, byml.write({"Versions": {}}))
    put(world, GET_FLOW, get_flow())
    pouch = msbt.Msbt({"Item_Boomerang_Name": ["Boomerang"], "Item_Boomerang_GetMessage": ["You got it!"]}, 7)
    put(world, ARCHIVE, sarc.write({text.POUCH_TEXT: msbt.write(pouch)}))
    sizes = rstb.read(raw(world, rstb.TABLE_PATH))
    sizes.set(LETTER_PACK, 1 << 20)
    sizes.set(PARAM, LETTER_PARAM_ENTRY)
    sizes.set(MODEL, LETTER_MODEL_ENTRY)
    sizes.set(GET_FLOW, 1 << 16)
    sizes.set(ARCHIVE, 1 << 16)
    put(world, rstb.TABLE_PATH, rstb.write(sizes))
    return world


def files_of(root):
    return {path.relative_to(root).as_posix(): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


@dataclass(frozen=True)
class Written:
    root: Path  # the synthetic dump
    dump: dict[str, bytes]  # its every file, before the seed
    output: SeedOutput
    custom: custom_items.CustomItems
    delivery: tokens.Delivery
    files: dict[str, WrittenFile]  # what write_seed reported, by path
    out: Path

    def read(self, path):
        return raw(self.out / "romfs", path, self.root)

    def native(self, path):
        return raw(self.root, path)


@pytest.fixture
def written(combined, tmp_path):
    """The seed, both producers' output combined as ``make_seed`` combines it, and ``write_seed``'s result."""
    return write_combined(combined, tmp_path / "seed")


def write_combined(combined, out, later_steps=(), later_files=None):
    """Both producers' output combined as ``make_seed`` combines it, then ``later_steps`` (and their new files,
    ``later_files``), through ``write_seed``."""
    dump = files_of(combined)
    seed = from_placements(combined_spec(), 7, Settings(shuffle=("Chest", "Token")), PLACEMENTS)
    locations = [*census(), chest(CHEST), chest(AP_CHEST_ID)]
    second = Definition(AP_CHEST_ID, "chest", "Test", "Test Second Chest", "Obj_Rupee_Blue", AP_CHEST)
    definitions = [*DEFINITIONS, second]
    kinds = {name: seed.world.locations[name].type for name in seed.shuffled}
    links = link(seed.world, [name for name, kind in kinds.items() if kind == "Chest"], definitions, locations)
    table = item_actors.load()
    custom = custom_step(combined, seed, links, table, FOREIGN, possessive_text=False)
    token_checks = [name for name, kind in kinds.items() if kind == token_policy.SHUFFLE]
    sources = tokens.link_sources(token_checks, definitions, locations)
    delivery, token_rows = tokens.seed_delivery(
        combined, seed.placements, sources, links.names, locations, rewards=token_policy.REWARDS
    )
    assert not custom.new_files.keys() & delivery.new_files.keys()
    output = SeedOutput(
        seed,
        links,
        make_plan(seed, links, table, {}, overrides=custom.actors),
        # Token rows first: they insert over the dump's own rows
        extra_changes=(delivery.changes, custom.changes, *later_steps),
        new_files={**custom.new_files, **delivery.new_files, **(later_files or {})},
        token_sources=token_rows,
    )
    files = {info.path: info for info in write_seed(output, combined, out)}
    return Written(combined, dump, output, custom, delivery, files, out)


def test_both_producers_packs_and_placements_are_written_and_the_dump_is_untouched(written):
    packs = {pack_path(actor) for actor in (*CUSTOM_ACTORS, *PICKUPS)}
    assert set(written.files) == {ADULT, CHILD, *tokens.REGISTRIES, GET_FLOW, ARCHIVE, rstb.TABLE_PATH, *packs}
    for path, file in written.output.new_files.items():
        info = written.files[path]
        assert (info.size, info.entry, info.new_size) == (0, None, len(file.data))
        assert written.read(path) == file.data
    for actor in (*CUSTOM_ACTORS, *PICKUPS):  # each pack holds its own actor's parameters
        assert actor_param(actor) in sarc.read(written.output.new_files[pack_path(actor)].data)
    for path in (ADULT, CHILD):  # every copy: each chest and Skulltula names its new actor
        actors = byml.read(written.read(path))["Actors"]
        placed = {int(actor["Hash"]): actor.get("Dynamic", {}).get(tokens.DROP) for actor in actors}
        assert placed == {
            TREE: BOOMERANG_PICKUP,
            TOWER: SHIELD_PICKUP,
            LONE: None,
            CHEST: NOTHING,
            AP_CHEST_ID: FOREIGN_ACTOR,
        }
    labels = msbt.read(sarc.read(written.read(ARCHIVE))[text.POUCH_TEXT]).messages
    assert {f"{actor}_GetMessage" for actor in CUSTOM_ACTORS} <= set(labels) and "Item_Boomerang_Name" in labels
    tokens_log = written.output.spoiler()["patch"]["tokens"]
    assert {row["location"]: row["drop_actor"] for row in tokens_log} == {
        GS_NAMES[TREE]: BOOMERANG_PICKUP,
        GS_NAMES[TOWER]: SHIELD_PICKUP,
        GS_NAMES[LONE]: None,
    }
    assert files_of(written.root) == written.dump  # the dump is read, never written


def test_registries_keep_every_native_row_and_add_both_producers_rows_sorted_and_unique(written):
    tables = {path: byml.read(written.read(path)) for path in tokens.REGISTRIES}
    natives = {path: byml.read(written.native(path)) for path in tokens.REGISTRIES}
    ids = {path: [row["__RowId"] for row in table] for path, table in tables.items()}
    for path, table in tables.items():
        assert ids[path] == sorted(set(ids[path]), key=lambda name: name.encode("utf-8")), path
        native_ids = {row["__RowId"] for row in natives[path]}
        assert set(ids[path]) == native_ids | set(CUSTOM_ACTORS) | set(PICKUPS), path
        assert byml.same([row for row in table if row["__RowId"] in native_ids], natives[path]), path
    assert ids[tokens.ACTOR_INFO] == ids[tokens.GAME_ACTOR_INFO]  # one index per actor in both tables
    rows = {path: {row["__RowId"]: row for row in table} for path, table in tables.items()}
    native = {path: {row["__RowId"]: row for row in table} for path, table in natives.items()}
    for actor in CUSTOM_ACTORS:  # the letter's rows under the new name; the content is given without the pouch
        letter = {**LETTER_ROWS[tokens.ACTOR_INFO], "ActorName": actor, "__RowId": actor}
        assert byml.same(rows[tokens.ACTOR_INFO][actor], letter)
        letter_life = {**LETTER_ROWS[tokens.GAME_ACTOR_INFO], "__RowId": actor}
        assert byml.same(rows[tokens.GAME_ACTOR_INFO][actor], letter_life)
        assert byml.same(rows[tokens.POUCH_ACTOR_INFO][actor], {**CUSTOM_POUCH, "__RowId": actor})
    rewards = {
        BOOMERANG_PICKUP: ("Item_Boomerang", "Item_Boomerang"),
        SHIELD_PICKUP: ("Obj_Shield_Hylian", "Weapon_Shield_Hylian"),
    }
    for actor, (item, name) in rewards.items():  # the reward's identity and grant, the token's lifecycle
        assert rows[tokens.ACTOR_INFO][actor]["ActorName"] == name
        token_life = {**native[tokens.GAME_ACTOR_INFO][tokens.TOKEN], "__RowId": actor}
        assert byml.same(rows[tokens.GAME_ACTOR_INFO][actor], token_life)
        grant = {**native[tokens.POUCH_ACTOR_INFO][item], "__RowId": actor}
        assert byml.same(rows[tokens.POUCH_ACTOR_INFO][actor], grant)


def test_size_table_sizes_every_new_pack_and_member_and_keeps_native_entries(written):
    sizes = rstb.read(written.read(rstb.TABLE_PATH))
    native = rstb.read(written.native(rstb.TABLE_PATH))
    letter = sarc.read(donor_pack())
    created = set()
    for path, file in written.output.new_files.items():
        assert sizes.get(path) == written.files[path].new_entry == rstb.required_size(path, len(file.data))
        members = sarc.read(file.data)
        new = {name for name in members if native.get(name) is None}
        for name in members.keys() - new:  # copied from a native pack or kept from the donor: the native entry
            assert sizes.get(name) == native.get(name), (path, name)
        if path in written.custom.new_files:
            renamed = actor_param(path.removeprefix("Pack/Actor/").removesuffix(".pack.zs"))
            assert new == {renamed} and members[MODEL] == letter[MODEL]
            growth = max(0, rounded(len(members[renamed])) - rounded(len(letter[PARAM])))
            assert sizes.get(renamed) == LETTER_PARAM_ENTRY + growth  # the letter's parameter entry plus growth
        else:
            assert new, path
            for name in new:  # measured on every native file of its type
                content = members[name]
                own = len(byml.read(content)["Components"]) if name.endswith(rstb.ACTOR_PARAM) else None
                assert sizes.get(name) == rstb.required_size(name, len(content), own), (path, name)
        created |= {path, *new}
    changed = {rstb.path_hash(path) for path, info in written.files.items() if info.entry is not None}
    for crc, entry in native.hashes.items():  # changed files may only grow; no other native entry moves
        if crc in changed:
            assert sizes.hashes[crc] >= entry, f"0x{crc:08x}"
        else:
            assert sizes.hashes[crc] == entry, f"0x{crc:08x}"
    created_hashes = {rstb.path_hash(path) for path in created}
    assert len(created_hashes) == len(created) and not created_hashes & native.hashes.keys()
    assert set(sizes.hashes) == set(native.hashes) | created_hashes and sizes.names == native.names
    assert (sizes.get(PARAM), sizes.get(MODEL)) == (LETTER_PARAM_ENTRY, LETTER_MODEL_ENTRY)


def test_token_off_possessive_text_leaves_unshuffled_native_token_message_unchanged(combined):
    # Both actors have native get-text keys; only Boomerang is in the shuffled assignment.
    for actor in ("Item_Boomerang", "Item_Token_Gold"):
        parameter = {
            "Components": {
                "ActorNameRef": f"?ActorSystem/ActorName/{actor}.engine__actor__ActorName.bgyml",
            }
        }
        put(combined, pack_path(actor), sarc.write({actor_param(actor): byml.write(parameter)}))
    messages = {
        "Item_Boomerang_Name": ["Boomerang"],
        "Item_Boomerang_GetMessage": ["You found the Boomerang!"],
        "Item_Token_Gold_Name": ["Gold Skulltula Token"],
        "Item_Token_Gold_GetMessage": ["You found the Gold Skulltula Token!"],
    }
    put(combined, ARCHIVE, sarc.write({text.POUCH_TEXT: msbt.write(msbt.Msbt(messages, 7))}))
    seed = from_placements(
        combined_spec(), 7, Settings(shuffle=("Chest",)), {CHEST_NAME: "Boomerang", AP_CHEST: "Boomerang"}
    )
    definitions = [
        *DEFINITIONS,
        Definition(AP_CHEST_ID, "chest", "Test", "Test Second Chest", "Obj_Rupee_Blue", AP_CHEST),
    ]
    links = link(seed.world, seed.shuffled, definitions, [*census(), chest(CHEST), chest(AP_CHEST_ID)])
    changes = custom_step(combined, seed, links, item_actors.load(), {}, possessive_text=True).changes
    after = msbt.read(sarc.read(changes[ARCHIVE](raw(combined, ARCHIVE)))[text.POUCH_TEXT]).messages
    assert msbt.plain(after["Item_Boomerang_GetMessage"]) == "You found your Boomerang!"
    assert after["Item_Token_Gold_GetMessage"] == messages["Item_Token_Gold_GetMessage"]
