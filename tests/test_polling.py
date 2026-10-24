from __future__ import annotations

import asyncio

import httpx

from bot.zalo import polling
from bot.storage import StateStore
from bot.zalo import ZaloClient


async def test_polling_delivers_updates_and_survives_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(polling, "MAX_BACKOFF", 0.01)
    stop = asyncio.Event()
    received = []
    calls = {"getUpdates": 0, "deleteWebhook": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        method = request.url.path.rsplit("/", 1)[-1]
        calls[method] = calls.get(method, 0) + 1
        if method == "deleteWebhook":
            return httpx.Response(200, json={"ok": True, "result": True})
        n = calls["getUpdates"]
        if n == 1:
            raise httpx.ConnectError("offline")
        if n == 2:
            return httpx.Response(200, json={"ok": False, "error_code": 408, "description": "timeout"})
        if n == 3:
            return httpx.Response(200, json={"ok": True, "result": {"event_name": "message.text.received"}})
        stop.set()
        return httpx.Response(200, json={"ok": True, "result": None})

    async def handle(payload):
        received.append(payload)

    client = ZaloClient("tok", http=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    state = StateStore(tmp_path / "state.txt")
    polling_task = polling.run_polling(client, handle, state, stop, poll_timeout=1)
    await asyncio.wait_for(polling_task, timeout=5)

    assert calls["deleteWebhook"] == 1
    assert calls["getUpdates"] == 4
    assert received == [{"event_name": "message.text.received"}]
    assert state.data["last_poll_at"] > 0
