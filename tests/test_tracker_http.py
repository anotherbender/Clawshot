"""Exercise saved progress through the real token/loopback HTTP boundary; never start a game."""

import json
import os
import struct
from pathlib import Path

import pytest
from test_tracker_icons import icon_file, noise, png_pixels, romfs_with, tree
from test_ui import request, running_server

from clawshot.app.preferences import Preferences
from clawshot.generate import Settings
from clawshot.save import BOOL, BOOL64, INT, MAGIC, key
from clawshot.tracker import icons
from clawshot.tracker.seeds import Place
from clawshot.ui.server import Application

# The HTTP state's presentation contract for dungeon rows (round 15): the generic UI/Tex/Icon dungeon files.
DUNGEON_ICONS = {
    "small_key": "Item_Dungeon_SmallKey",
    "boss_key": "Item_Dungeon_BossKey",
    "map": "Item_Dungeon_Map",
    "compass": "Item_Dungeon_Compass",
}
FOREST_FLAGS = {"IsGetBossKey": False, "IsGetMap": True, "IsGetCompass": False}


def save_bytes(*, opened=False, held=1, found=2, flags=None):
    """A complete synthetic progress.sav. A ``flags`` value of None leaves that Forest Temple Bool out of the save."""
    forest_flags = {
        f"DungeonInfo.ForestTemple.{name}": value
        for name, value in (FOREST_FLAGS | (flags or {})).items()
        if value is not None
    }
    fields = {
        BOOL: {"IsTreasureBoxOpen.123": opened, "IsTreasureBoxOpen.124": False, **forest_flags},
        INT: {
            "DungeonInfo.ForestTemple.SmallKeyNum": held,
            "DungeonInfo.ForestTemple.SmallKeyTotalNum": found,
            "PouchData.Item_Token_Gold.StockNum": 17,
        },
    }
    pairs = []
    for section, values in fields.items():
        pairs.append((0, section))
        pairs.extend((key(name), int(value)) for name, value in values.items())
    pairs.extend(((0, BOOL64), (789, 0)))
    end = 32 + len(pairs) * 8
    pairs[-1] = (789, end)
    # Conflicting raw flag proves HTTP collection uses the named chest Bool, not this raw Hash.
    return (
        struct.pack("<III20x", MAGIC, 1, end)
        + b"".join(struct.pack("<II", *p) for p in pairs)
        + struct.pack("<QQ", 123, 0)
    )


@pytest.fixture
def tracker_seed(tmp_path, monkeypatch):
    import clawshot.tracker.seeds as seeds

    monkeypatch.setattr(
        seeds, "location_index", lambda: {name: Place("Test", None, "Chest") for name in ("Test Chest", "Test Key")}
    )
    root = tmp_path / "output"
    (root / "seed").mkdir(parents=True)
    (root / "seed/spoiler.json").write_text(
        json.dumps(
            {
                "generator": "clawshot 0.2.0",
                "seed": 73,
                "settings": Settings().as_dict(),
                "settings_string": Settings().to_string(),
                "placements": {"Test Chest": "Synthetic secret reward", "Test Key": "Small Key (Forest Temple)"},
                "locations": {
                    "Test Chest": {"name": "Test Chest", "where": "Test", "ids": ["123"]},
                    "Test Key": {"name": "Test Key", "where": "Test", "ids": ["124"]},
                },
                "patch": {
                    "changes": [
                        {"location": name, "id": str(identity), "chest": "Obj_TBox_A_01"}
                        for name, identity in (("Test Chest", 123), ("Test Key", 124))
                    ],
                    "unchanged": [],
                },
            }
        ),
        encoding="utf-8",
    )
    slot = root / "user/save/profile/slot_01/progress.sav"
    slot.parent.mkdir(parents=True)
    slot.write_bytes(save_bytes())
    return root, slot


@pytest.fixture
def icon_cache(tmp_path, monkeypatch):
    """Decoded PNGs go to this private folder instead of the user's real cache."""
    cache = tmp_path / "icon-cache"
    monkeypatch.setattr(icons, "default_cache_dir", lambda: cache)
    return cache


def forest(snapshot):
    return next(d for d in snapshot["state"]["dungeons"] if d["name"] == "Forest Temple")


def icon(server, actor, **options):
    """An icon as the OBS page's <img> loads it: authorised by the token path alone."""
    return request(server, "", path=server.prefix + f"tracker-icons/{actor}.png", token=False, **options)


def test_http_save_refresh_named_chests_keys_and_spoiler_consent(tracker_seed):
    root, slot = tracker_seed
    before = slot.read_bytes(), slot.stat().st_mtime_ns
    app = Application(preferences=Preferences())
    with running_server(app) as server:
        body = {"seed": str(root)}
        assert request(server, "tracker-configure", body, token=False)[0] == 403
        assert request(server, "tracker-browse", {"kind": "save"})[0] == 400
        status, _, first = request(server, "tracker-configure", body)
        assert status == 200, first
        assert first["state"]["areas"][0]["collected"] == 0
        assert forest(first)["small_keys"]["held"] == 1
        assert forest(first)["small_keys"]["found"] == 2
        assert "Synthetic secret reward" not in json.dumps(first)
        assert (slot.read_bytes(), slot.stat().st_mtime_ns) == before
        assert request(server, "tracker-configure", body | {"show_locations": True})[0] == 400
        shown = request(server, "tracker-configure", body | {"show_locations": True, "confirmed": True})[2]
        assert "Synthetic secret reward" in json.dumps(shown)
        obs = request(server, "tracker-obs")[2]
        assert "Synthetic secret reward" not in json.dumps(obs)
        assert all("checks" not in area for area in obs["state"]["areas"])
        assert "save_folder" not in obs
        # Exercise the actual poll endpoint after a save is replaced, without reconfiguring/reloading.
        slot.write_bytes(save_bytes(opened=True, held=0, found=2))
        os.utime(slot, ns=(before[1] + 10_000_000, before[1] + 10_000_000))
        updated = request(server, "tracker")[2]
        assert updated["revision"] != first["revision"]
        assert forest(updated)["small_keys"]["held"] == 0
        assert forest(updated)["small_keys"]["found"] == 2
        assert updated["state"]["areas"][0]["collected"] == 1
        # A game save in flight must not replace good inventory with a blank tracker.
        slot.write_bytes(b"partial")
        incomplete = request(server, "tracker")[2]
        assert incomplete["state"] == updated["state"]
        assert incomplete["warnings"]


def test_tracker_assets_and_icons_keep_transport_guards(tracker_seed):
    root, _ = tracker_seed
    with running_server(Application(preferences=Preferences())) as server:
        assert request(server, "tracker-configure", {"seed": str(root)})[0] == 200
        for asset in ("tracker.html", "tracker.css", "tracker.js"):
            status, headers, _ = request(server, "", path=server.prefix + asset, token=False)
            assert status == 200
            assert headers["Cache-Control"] == "no-store"
            assert "default-src 'none'" in headers["Content-Security-Policy"]
            assert request(server, "", path=server.prefix + asset, headers={"Origin": "https://evil.example"})[0] == 403
        for actor in ("../../progress.sav", "%2e%2e%2fsecret", "Unlisted_Actor"):
            assert request(server, "", path=server.prefix + "tracker-icons/" + actor + ".png")[0] == 404
        assert request(server, "tracker-obs", token=False)[0] == 403
        assert request(server, "", path="/s/wrong/tracker.html")[0] == 403


def test_tracker_folder_picker_is_explicit_and_read_only(tmp_path):
    calls = []

    def chooser(kind, window):
        calls.append((kind, window))
        return tmp_path

    with running_server(Application(preferences=Preferences(), chooser=chooser)) as server:
        assert request(server, "tracker-browse", {"kind": "bad"})[0] == 400
        assert calls == []
        picked = request(server, "tracker-browse", {"kind": "save"})[2]
        assert Path(picked["path"]) == tmp_path
        assert calls == [("tracker-save", None)]
        assert list(tmp_path.iterdir()) == []


def test_dungeon_icons_are_served_only_while_a_configured_state_names_them(tracker_seed, tmp_path, icon_cache):
    root, _ = tracker_seed
    pictures = {actor: noise(5 * 3 * 4, seed) for seed, actor in enumerate(DUNGEON_ICONS.values(), 20)}
    # A decodable file sits behind every refused name: refusal must come from the state, not a missing file.
    files = {actor: icon_file(name=actor, pixels=pixels) for actor, pixels in pictures.items()}
    source = romfs_with(tmp_path / "romfs", files | {"Unlisted_Actor": icon_file(name="Unlisted_Actor")})
    preferences = Preferences()
    preferences.remember("dump", str(source))
    with running_server(Application(preferences=preferences)) as server:
        for route in ("tracker", "tracker-obs"):
            assert request(server, route)[2]["state"] is None
        for actor in DUNGEON_ICONS.values():
            assert icon(server, actor)[0] == 404
        assert not icon_cache.exists()  # nothing is decoded before a state names an icon

        status, _, app = request(server, "tracker-configure", {"seed": str(root)})
        assert status == 200, app
        obs = request(server, "tracker-obs")[2]  # the OBS page polls, then loads the icons its state names
        assert app["state"]["dungeon_icons"] == obs["state"]["dungeon_icons"] == DUNGEON_ICONS
        named = {cell["icon"] for group in ("items", "songs", "rewards") for cell in obs["state"][group]}
        assert not {"Obj_Dungeon_SmallKey", "Unlisted_Actor"} & named
        spare = min(icons.ICON_IDS - named - set(DUNGEON_ICONS.values()))
        romfs_with(source, {spare: icon_file(name=spare)})
        before = tree(source), tree(root)
        for actor, pixels in pictures.items():
            status, headers, body = icon(server, actor)
            assert status == 200, (actor, body)
            assert headers["Content-Type"].startswith("image/png")
            assert png_pixels(body) == (5, 3, pixels)
        # A whitelisted file the state does not name, an alias of a served icon, and an unknown name stay refused.
        for actor in (spare, "Obj_Dungeon_SmallKey", "Unlisted_Actor"):
            assert icon(server, actor)[0] == 404
        assert icon(server, "Item_Dungeon_Map", headers={"Origin": "https://evil.example"})[0] == 403
        assert request(server, "", path="/s/wrong/tracker-icons/Item_Dungeon_Map.png")[0] == 403
        # Decoded copies live only in the private cache; the dump and the seed output are only read.
        assert sorted(p.name.split(".")[0] for p in icon_cache.iterdir()) == sorted(DUNGEON_ICONS.values())
        assert (tree(source), tree(root)) == before

        status, _, failed = request(server, "tracker-configure", {"seed": str(tmp_path / "not-a-seed")})
        assert status == 200, failed
        assert failed["status"] == "error" and failed["state"] is None
        assert request(server, "tracker-obs")[2]["state"] is None
        for actor in DUNGEON_ICONS.values():
            assert icon(server, actor)[0] == 404  # an earlier seed's icons do not outlive its state


def test_dungeon_keys_and_flags_stay_distinct_while_obs_polls_spoiler_free(tracker_seed):
    root, slot = tracker_seed
    first = {"IsGetBossKey": True, "IsGetMap": False, "IsGetCompass": None}
    slot.write_bytes(save_bytes(held=3, found=5, flags=first))
    with running_server(Application(preferences=Preferences())) as server:
        body = {"seed": str(root), "show_locations": True, "confirmed": True}
        status, _, app = request(server, "tracker-configure", body)
        assert status == 200, app
        obs = request(server, "tracker-obs")[2]
        assert app["show_locations"] is True and "Synthetic secret reward" in json.dumps(app)
        assert obs["show_locations"] is False and obs["state"]["show_locations"] is False
        assert obs["state"]["dungeons"] == app["state"]["dungeons"]
        keys = forest(obs)
        # Held (spendable) and found (acquired) stay separate counts; a saved true, a saved false and a missing
        # field stay true, false and unknown instead of collapsing into "not found".
        assert (keys["small_keys"]["held"], keys["small_keys"]["found"]) == (3, 5)
        assert keys["small_keys"]["first_found"] is None
        assert keys["boss_key"] is True and keys["map"] is False and keys["compass"] is None
        others = [d for d in obs["state"]["dungeons"] if d["name"] != "Forest Temple"]
        assert others and all(d["small_keys"]["held"] is None and d["boss_key"] is None for d in others)

        mtime = slot.stat().st_mtime_ns + 10_000_000
        changed = {"IsGetBossKey": None, "IsGetMap": True, "IsGetCompass": False}
        slot.write_bytes(save_bytes(opened=True, held=2, found=5, flags=changed))
        os.utime(slot, ns=(mtime, mtime))
        polled = request(server, "tracker-obs")[2]  # the OBS poll alone re-reads the replaced save
        assert polled["revision"] != obs["revision"]
        keys = forest(polled)
        assert (keys["small_keys"]["held"], keys["small_keys"]["found"]) == (2, 5)
        assert keys["boss_key"] is None and keys["map"] is True and keys["compass"] is False
        assert polled["state"]["areas"][0]["collected"] == 1
        assert all("checks" not in area for area in polled["state"]["areas"])
        assert "Synthetic secret reward" not in json.dumps(polled)
        assert polled["state"]["dungeon_icons"] == DUNGEON_ICONS
        assert request(server, "tracker")[2]["state"]["dungeons"] == polled["state"]["dungeons"]
