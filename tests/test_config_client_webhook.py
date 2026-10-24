from __future__ import annotations

import logging

import httpx
import pytest
from fastapi.testclient import TestClient

from bot.config import ConfigError, Settings
from bot.system.log_files import RedactFilter
from bot.zalo.receive_webhook import SECRET_HEADER, WEBHOOK_PATH, create_app
from bot.zalo import ZaloClient, ZaloError

TOKEN = "123456:SECRET-TOKEN"


def test_missing_secrets_are_listed(tmp_path):
    settings = Settings.from_env({}, base_dir=tmp_path)
    with pytest.raises(ConfigError) as err:
        settings.require()
    assert "ZALO_BOT_TOKEN" in str(err.value) and "GEMINI_API_KEY" in str(err.value)
    settings.require(zalo=False, gemini=False)


def test_defaults_and_validation(tmp_path):
    s = Settings.from_env({"BOT_TRIGGERS": "/bot, @Trợ lý ", "ALLOWED_CHAT_IDS": "a,,b"}, base_dir=tmp_path)
    assert s.bot_triggers == ("/bot", "@Trợ lý")
    assert s.allowed_chat_ids == ("a", "b")
    assert s.receive_mode == "polling" and s.data_dir == tmp_path / "userdata" / "data"
    assert s.system_dir == tmp_path / "userdata" / "system" and s.log_dir == tmp_path / "userdata" / "system" / "logs"
    with pytest.raises(ConfigError):
        Settings.from_env({"RECEIVE_MODE": "carrier-pigeon"}, base_dir=tmp_path)
    with pytest.raises(ConfigError):
        Settings.from_env({"HISTORY_TURNS": "abc"}, base_dir=tmp_path)
    webhook = Settings.from_env(
        {"ZALO_BOT_TOKEN": "t", "GEMINI_API_KEY": "k", "RECEIVE_MODE": "webhook", "WEBHOOK_SECRET": "short"},
        base_dir=tmp_path,
    )
    with pytest.raises(ConfigError):
        webhook.require()


def _client(handler) -> ZaloClient:
    return ZaloClient(TOKEN, http=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


async def test_client_builds_url_and_returns_result():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = request.content.decode()
        return httpx.Response(200, json={"ok": True, "result": {"message_id": "m1", "date": 1}})

    result = await _client(handler).send_message("c1", "xin chào")
    assert result == {"message_id": "m1", "date": 1}
    assert seen["url"] == f"https://bot-api.zaloplatforms.com/bot{TOKEN}/sendMessage"
    assert '"chat_id":"c1"' in seen["body"].replace(" ", "")


async def test_client_raises_on_not_ok_and_hides_token():
    def api_error(request):
        return httpx.Response(200, json={"ok": False, "error_code": 401, "description": f"bad token {TOKEN}"})

    with pytest.raises(ZaloError) as err:
        await _client(api_error).get_me()
    assert err.value.error_code == 401 and TOKEN not in str(err.value)

    def network_error(request):
        raise httpx.ConnectError(f"cannot reach {request.url}")

    with pytest.raises(ZaloError) as err:
        await _client(network_error).get_me()
    assert err.value.network and TOKEN not in str(err.value)


def test_redact_filter_hides_secrets():
    record = logging.LogRecord("x", logging.INFO, __file__, 1, "url=%s", (f"https://x/bot{TOKEN}/getMe",), None)
    RedactFilter([TOKEN]).filter(record)
    assert TOKEN not in record.getMessage() and "***" in record.getMessage()


def test_webhook_checks_secret_and_forwards_payload():
    received = []

    async def handle(payload):
        received.append(payload)

    client = TestClient(create_app("s3cret-value", handle))
    assert client.post(WEBHOOK_PATH, json={"a": 1}).status_code == 403
    assert client.post(WEBHOOK_PATH, json={"a": 1}, headers={SECRET_HEADER: "wrong"}).status_code == 403
    ok = client.post(WEBHOOK_PATH, json={"a": 1}, headers={SECRET_HEADER: "s3cret-value"})
    assert ok.status_code == 200 and ok.json() == {"message": "Success"}
    assert received == [{"a": 1}]
    assert client.get("/health").json()["ok"] is True
