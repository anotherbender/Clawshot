"""Departed browsers must not turn response writes into another HTTP error."""

import io
import json
from types import SimpleNamespace

import pytest

from clawshot.ui.server import Handler


class Socket:
    def __init__(self, error=None, fail_on=1):
        self.error = error
        self.fail_on = fail_on
        self.writes = []

    def makefile(self, *_):
        return io.BytesIO(
            b"GET /s/test/api/settings HTTP/1.1\r\nHost: 127.0.0.1:1234\r\nX-Clawshot-Token: test\r\n\r\n"
        )

    def settimeout(self, _):
        pass

    def sendall(self, data):
        self.writes.append(bytes(data))
        if self.error is not None and len(self.writes) == self.fail_on:
            raise self.error("browser disconnected")


def dispatch(sock, app_error=None):
    calls = []

    def call(method, route, body):
        calls.append((method, route, body))
        if app_error is not None:
            raise app_error("application failed")
        return {"ok": True}

    server = SimpleNamespace(
        origin="http://127.0.0.1:1234", prefix="/s/test/", token="test", app=SimpleNamespace(call=call)
    )
    Handler(sock, ("127.0.0.1", 12345), server)
    return calls


@pytest.mark.parametrize("error", [ConnectionAbortedError, ConnectionResetError, BrokenPipeError])
@pytest.mark.parametrize("fail_on", [1, 2], ids=["headers", "body"])
def test_disconnected_reply_never_attempts_a_second_response(error, fail_on, capsys):
    sock = Socket(error, fail_on)
    assert dispatch(sock) == [("GET", "settings", {})]
    assert len(sock.writes) == fail_on
    assert sock.writes[0].startswith(b"HTTP/1.0 200 ")
    assert b"400 Bad Request" not in b"".join(sock.writes)
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("app_error", [OSError, ConnectionResetError])
def test_application_oserror_still_returns_bad_request(app_error):
    sock = Socket()
    assert dispatch(sock, app_error) == [("GET", "settings", {})]
    headers, body = b"".join(sock.writes).split(b"\r\n\r\n", 1)
    assert headers.startswith(b"HTTP/1.0 400 ")
    assert json.loads(body) == {"error": "application failed"}
