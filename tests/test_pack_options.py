"""Fresh seed users inherit options/account and Longshot's settings file only; synthetic fixtures, no game starts."""

import json
import os
from pathlib import Path

import pytest

from clawshot.pack.runtime import launch_plan, prepare_user


def creation_only(message):
    """Play's result says options go only into a seed save folder it creates, never over the seed's files."""
    return "only when" in message and "never" in message


def snapshot(root):
    return {
        path.relative_to(root): (path.read_bytes(), path.stat().st_mtime_ns)
        for path in root.rglob("*")
        if path.is_file()
    }


def account(user, name, *, option=True, profile=True, modified=100):
    root = user / "save" / name
    root.mkdir(parents=True)
    for filename, present in [("option.sav", option), ("account.sav", profile)]:
        if present:
            (root / filename).write_bytes(("synthetic " + name + filename).encode())
    (root / "slot_01").mkdir()
    (root / "slot_01/progress.sav").write_bytes(b"NEVER import this playthrough")
    os.utime(root, (modified, modified))
    return root


@pytest.mark.parametrize("program", ["hookshot", "longshot"])
def test_fresh_user_inherits_only_newest_accounts_options_once(tmp_path, program):
    game = tmp_path / program
    account(game / "user", "old-id", modified=100)
    newest = account(game / "user", "new-id", modified=200)
    user = tmp_path / "seed-user"
    plan = {"user": str(user), "player_user": str(game / "user"), "player_options": None}
    before = snapshot(game)
    result = prepare_user(plan)
    assert result["copied"] == ["option.sav", "account.sav"] and result["missing"] == []
    assert {path.as_posix(): path.read_bytes() for path in user.rglob("*") if path.is_file()} == {
        (user / "save/new-id/option.sav").as_posix(): (newest / "option.sav").read_bytes(),
        (user / "save/new-id/account.sav").as_posix(): (newest / "account.sav").read_bytes(),
    }
    assert snapshot(game) == before
    seeded = snapshot(user)
    (newest / "option.sav").write_bytes(b"normal options changed after first Play")
    assert prepare_user(plan)["copied"] == []
    assert snapshot(user) == seeded
    assert not list(user.rglob("slot_*"))


@pytest.mark.parametrize("option,profile", [(True, False), (False, True), (False, False)])
def test_missing_newest_files_are_reported_without_older_fallback(tmp_path, option, profile):
    game = tmp_path / "game"
    account(game / "user", "older-complete", modified=100)
    newest = account(game / "user", "newest", option=option, profile=profile, modified=200)
    user = tmp_path / "user"
    result = prepare_user({"user": str(user), "player_user": str(game / "user"), "player_options": None})
    present = [name for name in ("option.sav", "account.sav") if (newest / name).is_file()]
    missing = [name for name in ("option.sav", "account.sav") if name not in present]
    assert result["copied"] == present and result["missing"] == missing
    assert all(name in result["message"] for name in missing)
    assert {path.relative_to(user).as_posix() for path in user.rglob("*") if path.is_file()} == {
        "save/newest/" + name for name in present
    }


def test_no_normal_user_creates_empty_user_and_reports_skipped_options(tmp_path):
    user = tmp_path / "new-user"
    result = prepare_user({"user": str(user), "player_user": str(tmp_path / "game/user"), "player_options": None})
    assert result["missing"] == ["option.sav", "account.sav"] and result["copied"] == []
    assert user.is_dir() and list(user.iterdir()) == []


def test_existing_seed_files_and_progress_are_never_changed(tmp_path):
    game = tmp_path / "game"
    account(game / "user", "source")
    user = tmp_path / "seed/user"
    account(user, "seed-id")
    before = snapshot(user)
    result = prepare_user({"user": str(user), "player_user": str(game / "user"), "player_options": None})
    assert result["copied"] == [] and result["missing"] == []
    assert snapshot(user) == before


def files(user):
    return {path.relative_to(user).as_posix(): path.read_bytes() for path in user.rglob("*") if path.is_file()}


def seed_root(tmp_path):
    root = tmp_path / "pack"
    (root / "seed/romfs/Synthetic.byml.zs").parent.mkdir(parents=True)
    (root / "seed/romfs/Synthetic.byml.zs").write_bytes(b"invented placement")
    return root


def sources(tmp_path):
    return {path: state for path, state in snapshot(tmp_path).items() if path.parts[0] != "pack"}


def build(folder, binary):
    exe = folder / "bin" / binary
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"synthetic image\0HOS_MODS\0")
    # The build's own file (make_game.py writes compile_shaders= there): never the player's settings.
    (folder / "longshot_options.ini").write_bytes(b"compile_shaders=0\n")
    return folder


def launcher_layout(tmp_path, monkeypatch, kind):
    """(folder chosen in Clawshot, the build Play starts, the --user folder that launcher starts every build with).

    LongshotLauncher Core/MakeGameCommand.cs GamePlay.UserFolder, Core/Saves.cs SaveEnvironment.LongshotUser and
    Core/LauncherHome.cs PortableUser (facts only): Windows %APPDATA%\\Longshot or a portable launcher's
    LongshotLauncher-data\\user; Linux ${XDG_DATA_HOME:-$HOME/.local/share}/longshot, where a portable AppImage's
    <AppImage>.home is the launcher's home and $HOME."""
    if kind == "portable":
        data = tmp_path / "LongshotLauncher/LongshotLauncher-data"
        return data.parent, build(data / "builds/rc", "longshot.exe"), data / "user"
    if kind == "installed":
        data = tmp_path / "AppData/Local/LongshotLauncher"
        folder = build(tmp_path / "Games/Longshot/rc", "longshot.exe")
        data.mkdir(parents=True)
        entry = {"folder": str(folder), "version": "v3.0.0-rc.7", "default": True}
        (data / "builds.json").write_text(json.dumps({"format": 1, "builds": [entry]}), encoding="utf-8")
        monkeypatch.setenv("APPDATA", str(tmp_path / "AppData/Roaming"))
        return data, folder, tmp_path / "AppData/Roaming/Longshot"
    if kind == "linux":
        share = tmp_path / "home/.local/share"
        monkeypatch.setenv("XDG_DATA_HOME", str(share))
        return tmp_path / "home", build(share / "longshot/launcher/builds/rc", "longshot"), share / "longshot"
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    home = tmp_path / "apps/LongshotLauncher-v1.0.0-x86_64.AppImage.home"
    return home.parent, build(home / "builds/rc", "longshot"), home / ".local/share/longshot"


@pytest.mark.parametrize("kind", ["portable", "installed", "linux", "appimage"])
def test_launcher_play_inherits_the_launchers_user_folder_once(tmp_path, monkeypatch, kind):
    chosen, folder, shared = launcher_layout(tmp_path, monkeypatch, kind)
    account(shared, "old-id", modified=100)
    newest = account(shared, "new-id", modified=200)
    (shared / "longshot_options.ini").write_bytes(b"synthetic settings every launcher build reads")
    plan = launch_plan(seed_root(tmp_path), chosen)
    assert plan["cwd"] == str(folder)
    user = Path(plan["user"])
    before = sources(tmp_path)
    result = prepare_user(plan)
    assert result["copied"] == ["option.sav", "account.sav", "longshot_options.ini"] and result["missing"] == []
    assert files(user) == {
        "save/new-id/option.sav": (newest / "option.sav").read_bytes(),
        "save/new-id/account.sav": (newest / "account.sav").read_bytes(),
        "longshot_options.ini": b"synthetic settings every launcher build reads",
    }
    assert creation_only(result["message"])
    assert sources(tmp_path) == before
    seeded = snapshot(user)
    (shared / "longshot_options.ini").write_bytes(b"settings changed after first Play")
    again = prepare_user(plan)
    assert again["copied"] == [] and again["missing"] == [] and creation_only(again["message"])
    assert snapshot(user) == seeded


def test_launcher_user_without_settings_file_reports_it_skipped(tmp_path, monkeypatch):
    chosen, _, shared = launcher_layout(tmp_path, monkeypatch, "portable")
    account(shared, "only-id")
    plan = launch_plan(seed_root(tmp_path), chosen)
    result = prepare_user(plan)
    assert result["copied"] == ["option.sav", "account.sav"] and result["missing"] == ["longshot_options.ini"]
    assert "longshot_options.ini" in result["message"] and creation_only(result["message"])
    assert set(files(Path(plan["user"]))) == {"save/only-id/option.sav", "save/only-id/account.sav"}


@pytest.mark.parametrize("binary", ["longshot.exe", "longshot"])
def test_longshot_game_folder_inherits_the_settings_beside_the_game(tmp_path, monkeypatch, binary):
    # Without --user (started by itself) Longshot keeps its saves in <game>/user on Windows and in
    # ${XDG_DATA_HOME:-~/.local/share}/longshot on Linux, its settings beside the game (README, Where the files go;
    # host/options_path.c; facts only).
    folder = build(tmp_path / "Longshot", binary)
    (folder / "longshot_options.ini").write_bytes(b"synthetic settings of a game started by itself")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "share"))
    saves = folder / "user" if binary.endswith(".exe") else tmp_path / "share/longshot"
    newest = account(saves, "game-id")
    plan = launch_plan(seed_root(tmp_path), folder)
    result = prepare_user(plan)
    assert result["copied"] == ["option.sav", "account.sav", "longshot_options.ini"] and result["missing"] == []
    assert files(Path(plan["user"])) == {
        "save/game-id/option.sav": (newest / "option.sav").read_bytes(),
        "save/game-id/account.sav": (newest / "account.sav").read_bytes(),
        "longshot_options.ini": b"synthetic settings of a game started by itself",
    }


@pytest.mark.parametrize("binary", ["hookshot.exe", "hookshot"])
def test_hookshot_play_never_copies_a_settings_file(tmp_path, binary):
    folder = tmp_path / "Hookshot"
    (folder / "bin").mkdir(parents=True)
    (folder / "bin" / binary).write_bytes(b"synthetic image\0HOS_MODS\0")
    account(folder / "user", "hookshot-id")
    for name in ("hookshot_options.ini", "longshot_options.ini", "user/longshot_options.ini"):
        (folder / name).write_bytes(b"not for a Hookshot seed")
    plan = launch_plan(seed_root(tmp_path), folder)
    result = prepare_user(plan)
    assert result["copied"] == ["option.sav", "account.sav"] and result["missing"] == []
    assert set(files(Path(plan["user"]))) == {"save/hookshot-id/option.sav", "save/hookshot-id/account.sav"}
    assert creation_only(result["message"])


def test_existing_seed_user_never_gains_the_launchers_settings(tmp_path, monkeypatch):
    chosen, _, shared = launcher_layout(tmp_path, monkeypatch, "portable")
    account(shared, "launcher-id")
    (shared / "longshot_options.ini").write_bytes(b"synthetic launcher settings")
    plan = launch_plan(seed_root(tmp_path), chosen)
    user = Path(plan["user"])
    account(user, "seed-id")
    before = snapshot(user)
    result = prepare_user(plan)
    assert result["copied"] == [] and result["missing"] == [] and creation_only(result["message"])
    assert snapshot(user) == before and not (user / "longshot_options.ini").exists()
