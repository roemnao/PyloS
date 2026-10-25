from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from bot.system import remote_server
from bot.ui.admin.admin_web_server import AdminContext, create_app

LOCAL_TOKEN = "local-token-123456"
VPS_TOKEN = "vps-token-abcdef"
BASE = "http://127.0.0.1:8081"
AUTH = {"Authorization": f"Bearer {LOCAL_TOKEN}"}


@pytest.fixture
def seen():
    return []


@pytest.fixture
def client(tmp_path, monkeypatch, seen):
    for key in ("ADMIN_TOKEN", "REMOTE_URL", "REMOTE_ADMIN_TOKEN", "DATA_DIR", "LOG_DIR", "WORKSPACE_DIR"):
        monkeypatch.delenv(key, raising=False)
    env = tmp_path / ".env"
    env.write_text(f"ADMIN_TOKEN={LOCAL_TOKEN}\nREMOTE_URL=https://vps.example\nREMOTE_ADMIN_TOKEN={VPS_TOKEN}\n"
                   "DATA_DIR=data\nWORKSPACE_DIR=ws\nLOG_DIR=logs\n", encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/api/status":
            return httpx.Response(200, json={"running": True, "standby": None})
        if request.url.path == "/api/denied":
            return httpx.Response(401, json={"error": "no"})
        if request.url.path == "/api/boom":
            raise httpx.ConnectError("down")
        return httpx.Response(200, json={"echo": request.url.path, "q": dict(request.url.params)})

    monkeypatch.setattr(remote_server, "transport", httpx.MockTransport(handler))
    return TestClient(create_app(AdminContext(env, tmp_path), 8081), base_url=BASE)


def test_proxy_adds_vps_token_not_local_one(client, seen):
    res = client.get("/api/remote/groups?x=1", headers=AUTH)
    assert res.status_code == 200 and res.json() == {"echo": "/api/groups", "q": {"x": "1"}}
    assert seen[-1].headers["authorization"] == f"Bearer {VPS_TOKEN}"
    assert LOCAL_TOKEN not in str(seen[-1].headers)


def test_proxy_requires_local_login(client):
    assert client.get("/api/remote/groups").status_code == 401


@pytest.mark.parametrize("path", ["remote/groups", "auth/gmail/start", "secrets/GEMINI_API_KEY"])
def test_proxy_blocks_sensitive_paths(client, seen, path):
    assert client.put(f"/api/remote/{path}", json={"value": "x"}, headers=AUTH).status_code == 403
    assert not seen


def test_vps_401_does_not_log_the_page_out(client):
    res = client.get("/api/remote/denied", headers=AUTH)
    assert res.status_code == 502 and "REMOTE_ADMIN_TOKEN" in res.json()["error"]


def test_network_error_is_502(client):
    res = client.get("/api/remote/boom", headers=AUTH)
    assert res.status_code == 502 and "Không kết nối được VPS" in res.json()["error"]


def test_remote_status(client):
    data = client.get("/api/remote-status", headers=AUTH).json()
    assert data["configured"] and data["ok"] and data["running"] is True and VPS_TOKEN not in str(data)


def test_not_configured(tmp_path, monkeypatch):
    for key in ("ADMIN_TOKEN", "REMOTE_URL", "REMOTE_ADMIN_TOKEN"):
        monkeypatch.delenv(key, raising=False)
    env = tmp_path / ".env"
    env.write_text(f"ADMIN_TOKEN={LOCAL_TOKEN}\n", encoding="utf-8")
    c = TestClient(create_app(AdminContext(env, tmp_path), 8081), base_url=BASE)
    assert c.get("/api/remote-status", headers=AUTH).json()["configured"] is False
    assert c.get("/api/remote/status", headers=AUTH).status_code == 502


def test_http_remote_url_is_refused(tmp_path, monkeypatch):
    for key in ("ADMIN_TOKEN", "REMOTE_URL", "REMOTE_ADMIN_TOKEN"):
        monkeypatch.delenv(key, raising=False)
    env = tmp_path / ".env"
    env.write_text(f"ADMIN_TOKEN={LOCAL_TOKEN}\nREMOTE_URL=http://vps.example\nREMOTE_ADMIN_TOKEN={VPS_TOKEN}\n", encoding="utf-8")
    c = TestClient(create_app(AdminContext(env, tmp_path), 8081), base_url=BASE)
    res = c.get("/api/remote/status", headers=AUTH)
    assert res.status_code == 502 and "https" in res.json()["error"]
