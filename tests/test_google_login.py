"""Đăng nhập trang quản lý bằng Google riêng của PyloS: một Gmail, không phân quyền, không gọi web bot lịch."""

from __future__ import annotations

import base64
import json
import time
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from fastapi.testclient import TestClient

from bot.system import remote_server
from bot.ui.admin import google_login, settings_file
from bot.ui.admin.admin_sessions import AdminDevices
from bot.ui.admin.admin_web_server import AdminContext, create_app

BASE = "http://127.0.0.1:8081"
CLIENT_ID = "123-abc.apps.googleusercontent.com"
OWNER_EMAIL = "chu@gmail.com"
VPS_ADMIN = "vps-admin-token-123"
LOCAL_ADMIN = "local-admin-token-123"
GOOGLE_ENV = (f"ADMIN_GOOGLE_CLIENT_ID={CLIENT_ID}\nADMIN_GOOGLE_CLIENT_SECRET=GOCSPX-secret\n"
              f"ADMIN_EMAIL={OWNER_EMAIL}\nDATA_DIR=data\nLOG_DIR=logs\nSYSTEM_DIR=system\nWORKSPACE_DIR=ws\n")


def id_token(email: str, *, aud: str = CLIENT_ID, exp: float | None = None, verified: bool = True) -> str:
    claims = {"aud": aud, "iss": "https://accounts.google.com", "exp": exp or time.time() + 600, "email": email,
              "email_verified": verified}
    return "x." + base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=") + ".y"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ("ADMIN_TOKEN", "REMOTE_URL", "REMOTE_ADMIN_TOKEN", "ADMIN_PUBLIC_URL", "SCHEDULE_API_KEY", "SCHEDULE_API_URL",
                "DATA_DIR", "LOG_DIR", "WORKSPACE_DIR", "SYSTEM_DIR", "ADMIN_EMAIL", "ADMIN_GOOGLE_CLIENT_ID"):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def no_web(monkeypatch):
    """Mọi lời gọi sang web bot lịch đều làm test hỏng: đăng nhập không được phụ thuộc web."""
    async def boom(*a, **k):
        raise AssertionError("Đăng nhập không được gọi web bot lịch")

    monkeypatch.setattr("bot.system.server_client.request", boom)


def make_client(tmp_path, token=VPS_ADMIN, extra="", name="vps"):
    root = tmp_path / name
    root.mkdir()
    env = root / ".env"
    env.write_text(f"ADMIN_TOKEN={token}\n{GOOGLE_ENV}{extra}", encoding="utf-8")
    return TestClient(create_app(AdminContext(env, root), 8081), base_url=BASE), env


def fake_google(monkeypatch, email):
    async def exchange(code, verifier, redirect_uri, client_id, client_secret, client=None):
        assert code == "google-code" and verifier
        return google_login.decode_id_token(id_token(email), client_id)

    monkeypatch.setattr(google_login, "exchange", exchange)


def approve(client, monkeypatch, email=OWNER_EMAIL):
    """Chạy cả luồng: start → begin (302 sang Google) → callback → trả mã."""
    fake_google(monkeypatch, email)
    started = client.post("/api/auth/google/start").json()
    begin = client.get(f"/api/auth/google/begin?code={started['code']}", follow_redirects=False)
    assert begin.status_code == 302
    query = parse_qs(urlsplit(begin.headers["location"]).query)
    assert begin.headers["location"].startswith("https://accounts.google.com/") and query["code_challenge_method"] == ["S256"]
    assert query["scope"] == ["openid email"] and query["state"][0].startswith(started["code"])
    page = client.get("/api/auth/google/callback", params={"code": "google-code", "state": query["state"][0]})
    return started["code"], page


def test_google_login_gives_session_token_without_calling_web(tmp_path, monkeypatch, no_web):
    client, _ = make_client(tmp_path)
    assert client.get("/api/auth/options").json() == {"google": True}
    code, page = approve(client, monkeypatch)
    assert page.status_code == 200 and "Đã đăng nhập" in page.text
    done = client.post("/api/auth/google/poll", json={"code": code}).json()
    assert done["status"] == "ok" and done["email"] == OWNER_EMAIL and done["token"] != VPS_ADMIN
    session = {"Authorization": f"Bearer {done['token']}"}
    assert client.get("/api/status", headers=session).status_code == 200
    assert client.get("/api/status", headers={"Authorization": f"Bearer {VPS_ADMIN}"}).status_code == 200  # mã dự phòng vẫn dùng
    assert client.post("/api/auth/google/poll", json={"code": code}).json() == {"status": "expired"}  # chỉ đọc một lần


def test_login_works_with_no_schedule_api_key(tmp_path, monkeypatch, no_web):
    client, env = make_client(tmp_path)
    assert "SCHEDULE_API_KEY" not in env.read_text(encoding="utf-8")
    code, _ = approve(client, monkeypatch)
    assert client.post("/api/auth/google/poll", json={"code": code}).json()["status"] == "ok"


def test_other_gmail_is_denied_no_roles(tmp_path, monkeypatch, no_web):
    client, _ = make_client(tmp_path)
    code, page = approve(client, monkeypatch, email="khac@gmail.com")
    assert page.status_code == 403
    denied = client.post("/api/auth/google/poll", json={"code": code}).json()
    assert denied["status"] == "denied" and "khac@gmail.com" in denied["message"] and "token" not in denied


def test_bad_state_expired_code_and_invalid_tokens(tmp_path, monkeypatch, no_web):
    client, _ = make_client(tmp_path)
    started = client.post("/api/auth/google/start").json()
    bad = client.get("/api/auth/google/callback", params={"code": "c", "state": f"{started['code']}.sai"})
    assert bad.status_code == 400
    assert client.get("/api/auth/google/begin?code=../x").status_code == 400
    assert client.post("/api/auth/google/poll", json={"code": "a" * 32}).json() == {"status": "expired"}
    with pytest.raises(ValueError):
        google_login.decode_id_token(id_token(OWNER_EMAIL, aud="khac"), CLIENT_ID)
    with pytest.raises(ValueError):
        google_login.decode_id_token(id_token(OWNER_EMAIL, exp=1), CLIENT_ID)
    with pytest.raises(ValueError):
        google_login.decode_id_token(id_token(OWNER_EMAIL, verified=False), CLIENT_ID)


def test_pending_logins_expire_and_are_capped():
    now = [0.0]
    pending = google_login.PendingLogins(ttl=100, clock=lambda: now[0])
    code = pending.start()
    assert pending.get(code)
    now[0] = 101
    assert pending.get(code) is None
    for _ in range(google_login.MAX_PENDING + 5):
        pending.start()
    assert len(pending._items) <= google_login.MAX_PENDING


def test_exchange_uses_pkce_and_checks_audience():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(parse_qs(request.read().decode()))
        return httpx.Response(200, json={"id_token": id_token(OWNER_EMAIL)})

    import asyncio

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await google_login.exchange("c", "ver", "http://x/cb", CLIENT_ID, "sec", client)

    assert asyncio.run(run())["email"] == OWNER_EMAIL and seen["code_verifier"] == ["ver"]


def test_config_rejects_several_emails_and_bad_client_id(tmp_path):
    from bot.config import ConfigError, Settings

    with pytest.raises(ConfigError):
        Settings.from_env({"ADMIN_EMAIL": "a@x.com, b@x.com"}, base_dir=tmp_path)
    with pytest.raises(ConfigError):
        Settings.from_env({"ADMIN_GOOGLE_CLIENT_ID": "khong-hop-le"}, base_dir=tmp_path)
    assert Settings.from_env({"ADMIN_EMAIL": " Chu@Gmail.com "}, base_dir=tmp_path).admin_email == "chu@gmail.com"
    assert not google_login.email_allowed("a@x.com", "")


# ---------- khoá thiết bị trên VPS ----------

def test_device_keys_survive_restart_and_are_stored_hashed(tmp_path):
    path = tmp_path / "admin_devices.json"
    token = AdminDevices(path).issue("chu@gmail.com", "ZaloBot trên PC")
    assert token.startswith("dev_") and token not in path.read_text(encoding="utf-8")
    assert AdminDevices(path).valid(token)
    assert not AdminDevices(path).valid(token + "x") and not AdminDevices(path).valid("")
    [entry] = AdminDevices(path).list()
    assert entry["email"] == "chu@gmail.com" and "dev_" not in str(entry)
    assert AdminDevices(path).revoke(entry["id"]) and not AdminDevices(path).valid(token)


def test_device_keys_expire_and_same_machine_replaces_old_key(tmp_path):
    now = [1000.0]
    devices = AdminDevices(tmp_path / "d.json", ttl=100, clock=lambda: now[0])
    old = devices.issue("a@gmail.com", "PC")
    new = devices.issue("a@gmail.com", "PC")
    assert not devices.valid(old) and devices.valid(new) and len(devices.list()) == 1
    now[0] += 101
    assert not devices.valid(new)


def test_vps_issues_device_key_that_outlives_sessions(tmp_path, monkeypatch, no_web):
    client, _ = make_client(tmp_path)
    fake_google(monkeypatch, OWNER_EMAIL)
    started = client.post("/api/auth/google/start").json()
    state = parse_qs(urlsplit(client.get(f"/api/auth/google/begin?code={started['code']}", follow_redirects=False)
                              .headers["location"]).query)["state"][0]
    client.get("/api/auth/google/callback", params={"code": "google-code", "state": state})
    done = client.post("/api/auth/google/poll", json={"code": started["code"], "device": "ZaloBot trên PC"}).json()
    assert done["status"] == "ok" and done["token"].startswith("dev_")
    auth = {"Authorization": f"Bearer {done['token']}"}
    assert client.get("/api/status", headers=auth).status_code == 200
    devices = client.get("/api/devices", headers=auth).json()["devices"]
    assert [d["name"] for d in devices] == ["ZaloBot trên PC"]
    assert client.delete(f"/api/devices/{devices[0]['id']}", headers=auth).json()["ok"]
    assert client.get("/api/status", headers=auth).status_code == 401


# ---------- máy Windows: Kết nối VPS bằng Google ----------

@pytest.fixture
def local(tmp_path, monkeypatch, no_web):
    vps_client, _ = make_client(tmp_path)
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
    return TestClient(create_app(AdminContext(env, root), 8081), base_url=BASE), env, vps_client, seen


LOCAL_AUTH = {"Authorization": f"Bearer {LOCAL_ADMIN}"}


def test_connect_vps_with_google_saves_key_without_showing_it(local, monkeypatch):
    client, env, vps_client, seen = local
    assert client.get("/api/remote-status", headers=LOCAL_AUTH).json()["configured"] is False
    started = client.post("/api/remote-login/start", headers=LOCAL_AUTH).json()
    assert "authorization" not in seen[-1].headers
    assert client.post("/api/remote-login/poll", json={"code": started["code"]}, headers=LOCAL_AUTH).json() == {"status": "pending"}

    code, _ = approve(vps_client, monkeypatch)  # người dùng duyệt ở trang Google của VPS
    res = client.post("/api/remote-login/poll", json={"code": code}, headers=LOCAL_AUTH)
    assert res.json() == {"status": "ok", "email": OWNER_EMAIL} and "dev_" not in res.text
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


def test_public_url_origin_is_accepted_only_when_configured(tmp_path):
    client, env = make_client(tmp_path, name="pub")
    public = {"Origin": "https://unousgrowth.com"}
    assert client.post("/api/auth/google/poll", json={"code": "x"}, headers=public).status_code == 403
    env.write_text(env.read_text(encoding="utf-8") + "ADMIN_PUBLIC_URL=https://unousgrowth.com/\n", encoding="utf-8")
    assert client.post("/api/auth/google/poll", json={"code": "x"}, headers=public).status_code == 400
    assert client.post("/api/auth/google/poll", json={"code": "x"}, headers={"Origin": "https://evil.example"}).status_code == 403
    assert client.post("/api/auth/google/poll", json={"code": "x"},
                       headers={"Origin": "https://unousgrowth.com.evil.example"}).status_code == 403
