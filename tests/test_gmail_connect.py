from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from bot.system import remote_server
from bot.ui.admin import settings_file
from bot.ui.admin.admin_sessions import AdminDevices
from bot.ui.admin.admin_web_server import AdminContext, create_app

CODE = "b2" * 16
BASE = "http://127.0.0.1:8081"
VPS_ADMIN = "vps-admin-token-123"
LOCAL_ADMIN = "local-admin-token-123"


# ---------- khoá thiết bị trên VPS ----------

def test_device_keys_survive_restart_and_are_stored_hashed(tmp_path):
    path = tmp_path / "admin_devices.json"
    token = AdminDevices(path).issue("chu@gmail.com", "ZaloBot trên PC")
    assert token.startswith("dev_") and token not in path.read_text(encoding="utf-8")
    assert AdminDevices(path).valid(token)  # đối tượng mới = sau khi khởi động lại
    assert not AdminDevices(path).valid(token + "x") and not AdminDevices(path).valid("")
    [entry] = AdminDevices(path).list()
    assert entry["email"] == "chu@gmail.com" and "dev_" not in str(entry)
    assert AdminDevices(path).revoke(entry["id"]) and not AdminDevices(path).valid(token)


def test_device_keys_expire_and_same_machine_replaces_old_key(tmp_path):
    path = tmp_path / "d.json"
    now = [1000.0]
    devices = AdminDevices(path, ttl=100, clock=lambda: now[0])
    old = devices.issue("a@gmail.com", "PC")
    new = devices.issue("a@gmail.com", "PC")
    assert not devices.valid(old) and devices.valid(new) and len(devices.list()) == 1
    now[0] += 101
    assert not devices.valid(new)


# ---------- VPS: đăng nhập Gmail có device -> khoá dài hạn ----------

class FakeWeb:
    """Giả web iforgotmywayhome (server_client)."""

    def __init__(self) -> None:
        self.routes: dict[tuple[str, str], dict] = {}

    def on(self, method: str, path: str, result: dict) -> None:
        self.routes[(method, path)] = result

    async def request(self, method, path, **kwargs):
        return self.routes.get((method, path), {"error": "không có", "status": 404, "message": ""})


@pytest.fixture
def vps(tmp_path, monkeypatch):
    for key in ("ADMIN_TOKEN", "REMOTE_URL", "REMOTE_ADMIN_TOKEN", "DATA_DIR", "LOG_DIR", "WORKSPACE_DIR", "SYSTEM_DIR"):
        monkeypatch.delenv(key, raising=False)
    root = tmp_path / "vps"
    root.mkdir()
    env = root / ".env"
    env.write_text(f"ADMIN_TOKEN={VPS_ADMIN}\nDATA_DIR=data\nLOG_DIR=logs\nSYSTEM_DIR=system\nWORKSPACE_DIR=ws\n", encoding="utf-8")
    web = FakeWeb()
    web.on("POST", "/device-login", {"code": CODE, "url": f"https://app.example/?device={CODE}", "expiresIn": 600})
    monkeypatch.setattr("bot.system.server_client.request", web.request)
    return TestClient(create_app(AdminContext(env, root), 8081), base_url=BASE), web


def test_vps_issues_device_key_that_outlives_sessions(vps):
    client, web = vps
    web.on("GET", f"/device-login/{CODE}", {"status": "approved", "email": "chu@gmail.com", "isAdmin": True})
    done = client.post("/api/auth/gmail/poll", json={"code": CODE, "device": "ZaloBot trên PC"}).json()
    assert done["status"] == "ok" and done["token"].startswith("dev_")
    auth = {"Authorization": f"Bearer {done['token']}"}
    assert client.get("/api/status", headers=auth).status_code == 200
    devices = client.get("/api/devices", headers=auth).json()["devices"]
    assert [d["name"] for d in devices] == ["ZaloBot trên PC"]
    assert client.delete(f"/api/devices/{devices[0]['id']}", headers=auth).json()["ok"]
    assert client.get("/api/status", headers=auth).status_code == 401


def test_vps_refuses_device_key_for_non_admin_gmail(vps):
    client, web = vps
    web.on("GET", f"/device-login/{CODE}", {"status": "approved", "email": "khac@gmail.com", "isAdmin": False})
    res = client.post("/api/auth/gmail/poll", json={"code": CODE, "device": "PC"}).json()
    assert res["status"] == "denied" and "token" not in res


# ---------- máy local: Kết nối VPS bằng Gmail ----------

@pytest.fixture
def local(tmp_path, monkeypatch, vps):
    """Server local thật; VPS là server admin thật ở fixture vps (gọi qua MockTransport)."""
    vps_client, web = vps
    root = tmp_path / "local"
    root.mkdir()
    env = root / ".env"
    env.write_text(f"ADMIN_TOKEN={LOCAL_ADMIN}\nREMOTE_URL=https://vps.example\nDATA_DIR=data\nLOG_DIR=logs\n"
                   "SYSTEM_DIR=system\nWORKSPACE_DIR=ws\n", encoding="utf-8")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        res = vps_client.request(request.method, request.url.path, content=request.read(),
                                 headers={k: v for k, v in request.headers.items() if k != "host"})
        return httpx.Response(res.status_code, content=res.content, headers={"content-type": res.headers["content-type"]})

    monkeypatch.setattr(remote_server, "transport", httpx.MockTransport(handler))
    client = TestClient(create_app(AdminContext(env, root), 8081), base_url=BASE)
    return client, env, web, seen


LOCAL_AUTH = {"Authorization": f"Bearer {LOCAL_ADMIN}"}


def test_connect_vps_with_gmail_saves_key_without_showing_it(local):
    client, env, web, seen = local
    assert client.get("/api/remote-status", headers=LOCAL_AUTH).json()["configured"] is False
    started = client.post("/api/remote-login/start", headers=LOCAL_AUTH).json()
    assert started["code"] == CODE and started["url"].endswith(CODE)
    assert "authorization" not in seen[-1].headers  # chưa có khoá: không gửi gì

    web.on("GET", f"/device-login/{CODE}", {"status": "pending"})
    assert client.post("/api/remote-login/poll", json={"code": CODE}, headers=LOCAL_AUTH).json() == {"status": "pending"}

    web.on("GET", f"/device-login/{CODE}", {"status": "approved", "email": "chu@gmail.com", "isAdmin": True})
    res = client.post("/api/remote-login/poll", json={"code": CODE}, headers=LOCAL_AUTH)
    assert res.json() == {"status": "ok", "email": "chu@gmail.com"} and "dev_" not in res.text
    token = settings_file.read_values(env)["REMOTE_ADMIN_TOKEN"]
    assert token.startswith("dev_")

    status = client.get("/api/remote-status", headers=LOCAL_AUTH).json()
    assert status["configured"] and status["ok"] and "dev_" not in str(status)
    assert seen[-1].headers["authorization"] == f"Bearer {token}"

    assert client.delete("/api/remote-login", headers=LOCAL_AUTH).json()["ok"]
    assert settings_file.read_values(env)["REMOTE_ADMIN_TOKEN"] == ""


def test_connect_requires_local_login_and_valid_code(local):
    client, *_ = local
    assert client.post("/api/remote-login/start").status_code == 401
    assert client.post("/api/remote-login/poll", json={"code": "../x"}, headers=LOCAL_AUTH).status_code == 400


def test_revoked_key_is_reported_as_auth_failed(local):
    client, env, *_ = local
    settings_file.update(env, {"REMOTE_ADMIN_TOKEN": "dev_khoa-da-bi-thu-hoi"})
    status = client.get("/api/remote-status", headers=LOCAL_AUTH).json()
    assert status["configured"] and not status["ok"] and status["auth_failed"]


def test_default_remote_url_and_off(tmp_path):
    from bot.config import DEFAULT_REMOTE_URL, Settings

    assert Settings.from_env({}, base_dir=tmp_path).remote_url == DEFAULT_REMOTE_URL
    off = Settings.from_env({"REMOTE_URL": "off", "REMOTE_ADMIN_TOKEN": "x"}, base_dir=tmp_path)
    assert not remote_server.configured(off)
