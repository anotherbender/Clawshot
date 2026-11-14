"""A checked game path persists outside the checkout; invalid replacement paths do not replace it."""

import pytest
from test_app import app_source as app_source
from test_app import synthetic_run, synthetic_spec
from test_app_play import made_ui_seed as made_ui_seed
from test_pack_nx import write_nx
from test_ui import request, running_server

from clawshot.app import Jobs
from clawshot.app.preferences import Preferences
from clawshot.pack import VERSION_FILES, PackError, check_version
from clawshot.ui.server import Application


def test_only_a_verified_dump_replaces_the_remembered_game(made_ui_seed, tmp_path):
    _, _, source = made_ui_seed
    config = tmp_path / "user-config/paths.json"
    first = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config))
    with running_server(first) as server:
        assert request(server, "detect", {"dump": str(source)})[0] == 200
    before = config.read_bytes(), config.stat().st_mtime_ns
    (source / VERSION_FILES[1]).write_bytes(b"unsupported synthetic game version")
    second = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=Preferences(config))
    with running_server(second) as server:
        assert request(server, "schema")[2]["paths"]["dump"] == str(source)
        assert request(server, "detect", {"dump": str(source)})[0] == 400
    assert before == (config.read_bytes(), config.stat().st_mtime_ns)


@pytest.mark.parametrize("exists", [False, True])
def test_missing_dump_and_existing_wrong_kind_have_distinct_http_errors(made_ui_seed, tmp_path, exists):
    _, _, source = made_ui_seed
    bad = tmp_path / ("existing.txt" if exists else "missing.nup")
    if exists:
        bad.write_bytes(b"synthetic wrong file kind")
    preferences = Preferences()
    preferences.remember("dump", str(source))
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    with running_server(app) as server:
        status, _, response = request(server, "detect", {"dump": str(bad)})
        assert status == 400
        expected = (
            "Game dump: choose an extracted romfs folder, a .nup or an .nx file"
            if exists
            else f"Not found: {bad}. Choose your romfs folder, .nup or .nx again."
        )
        assert response["error"] == expected
        assert request(server, "schema")[2]["paths"]["dump"] == str(source)


@pytest.mark.parametrize("exists", [False, True])
def test_missing_update_and_existing_wrong_kind_have_distinct_http_errors(tmp_path, exists):
    dump = tmp_path / "cart/romfs"
    dump.mkdir(parents=True)
    bad = tmp_path / ("existing.txt" if exists else "moved-update.nx")
    if exists:
        bad.write_bytes(b"synthetic wrong file kind")
    preferences = Preferences()
    preferences.remember("dump", str(dump))
    preferences.remember("update", str(tmp_path / "remembered-update"))
    before = preferences.snapshot()
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    with running_server(app) as server:
        status, _, response = request(server, "detect", {"dump": str(dump), "update": str(bad)})
    assert status == 400
    expected = (
        "Update: choose an extracted romfs folder, a .nup or an .nx file"
        if exists
        else f"Update not found: {bad}. Choose the update's romfs folder, .nup or .nx again."
    )
    assert response["error"] == expected
    assert preferences.snapshot() == before


@pytest.mark.parametrize("archive", ["no-romfs", "damaged"])
def test_a_refused_nx_shows_the_readers_own_reason_over_http(tmp_path, archive):
    if archive == "no-romfs":  # packed from a decrypted NSP: native NCAs, no romfs/ tree
        nx = write_nx(tmp_path / "nsp.nx", [(0, 0, {"main.nca": b"synthetic native content"})])
    else:  # every fingerprint file is there, but the first stored one no longer matches its SHA-256
        files = {f"romfs/{name}": b"synthetic fingerprint input " * 4 + name.encode() for name in VERSION_FILES}
        nx = write_nx(tmp_path / "game.nx", [(0, 0, files)])
        data = bytearray(nx.read_bytes())
        data[8192 + 20] ^= 0xFF
        nx.write_bytes(bytes(data))
    with pytest.raises(PackError) as reader:
        check_version(nx)
    remembered = str(tmp_path / "remembered-dump")
    preferences = Preferences(tmp_path / "paths.json")
    preferences.remember("dump", remembered)
    app = Application(Jobs(synthetic_run), spec=synthetic_spec(), preferences=preferences)
    with running_server(app) as server:
        status, _, response = request(server, "detect", {"dump": str(nx)})
    assert status == 400
    assert response["error"] == f"These game files cannot be used: {reader.value}."
    reason = "no romfs/ tree (packed from a decrypted NSP?)" if archive == "no-romfs" else "SHA-256"
    assert reason in response["error"]
    assert preferences.snapshot()["dump"] == remembered
