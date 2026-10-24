from __future__ import annotations

import json

import httpx
import pytest

from bot.agent import ToolContext
from bot.agent.tools import schedule

CTX = ToolContext("g1", "u1", "An", True)


@pytest.fixture
def api(monkeypatch):
    """Giả lập /api/agent của web quanlythoigian, ghi lại các yêu cầu."""
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if request.headers.get("authorization") != "Bearer k3y":
            return httpx.Response(401, json={"error": "Sai khoá"})
        path = request.url.path
        if path.endswith("/events"):
            return httpx.Response(200, json={"id": "e1", **json.loads(request.content)})
        if path.endswith("/tasks") and request.method == "POST":
            return httpx.Response(200, json={"id": "t1", **json.loads(request.content)})
        if path.endswith("/tasks"):
            return httpx.Response(200, json=[{"id": "t1", "title": "Nộp báo cáo"}])
        if "/tasks/" in path:
            return httpx.Response(200, json={"id": path.rsplit("/", 1)[-1], "done": True})
        if path.endswith("/agenda"):
            return httpx.Response(200, json={"date": request.url.params["date"], "text": "Không có lịch"})
        return httpx.Response(404, json={"error": "không có"})

    real = httpx.AsyncClient
    monkeypatch.setattr(schedule.httpx, "AsyncClient", lambda **kw: real(transport=httpx.MockTransport(handler), **kw))
    monkeypatch.setenv("SCHEDULE_API_URL", "https://web.example/")
    monkeypatch.setenv("SCHEDULE_API_KEY", "k3y")
    return calls


def test_base_url_accepts_site_or_api_address():
    assert schedule.base_url("") == schedule.DEFAULT_URL
    assert schedule.base_url("https://x.vercel.app/") == "https://x.vercel.app/api/agent"
    assert schedule.base_url("https://x.vercel.app/api/agent/") == "https://x.vercel.app/api/agent"


def test_tools_only_registered_with_key(monkeypatch, tmp_path):
    monkeypatch.setattr("bot.config.APP_HOME", tmp_path)
    monkeypatch.delenv("SCHEDULE_API_KEY", raising=False)
    assert schedule._tools() == []
    monkeypatch.setenv("SCHEDULE_API_KEY", "k")
    tools = {t.name: t for t in schedule._tools()}
    assert set(tools) == {"them_lich_hen", "them_viec", "xem_lich", "danh_sach_viec", "xong_viec"}
    assert all(t.owner_only for t in tools.values())
    monkeypatch.setenv("SCHEDULE_OWNER_ONLY", "false")
    assert not any(t.owner_only for t in schedule._tools())


async def test_create_event_and_task_send_bearer_and_note(api):
    res = await schedule._create_event({"title": "Họp", "start": "2026-10-30T14:00:00+07:00"}, CTX)
    assert res["ok"] and res["event"]["title"] == "Họp"
    sent = json.loads(api[-1].content)
    assert str(api[-1].url) == "https://web.example/api/agent/events"
    assert sent["start"] == "2026-10-30T14:00:00+07:00" and "An" in sent["note"] and "end" not in sent

    res = await schedule._create_task({"title": "Nộp báo cáo", "deadline": "2026-10-31T17:00:00+07:00", "quadrant": 1}, CTX)
    assert res["ok"] and json.loads(api[-1].content)["quadrant"] == 1


async def test_read_and_complete(api):
    assert (await schedule._agenda({"date": "tomorrow"}, CTX))["date"] == "tomorrow"
    assert (await schedule._list_tasks({}, CTX))["tasks"][0]["id"] == "t1"
    assert (await schedule._complete_task({"id": "t1"}, CTX))["task"]["done"] is True
    assert "error" in await schedule._complete_task({}, CTX)


async def test_errors_are_returned_to_model(api, monkeypatch):
    monkeypatch.setenv("SCHEDULE_API_KEY", "sai")
    res = await schedule._create_event({"title": "x", "start": "2026-10-30T14:00:00+07:00"}, CTX)
    assert "401" in res["error"]
