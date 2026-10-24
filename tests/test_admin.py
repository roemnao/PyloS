from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from bot import gateway
from bot.admin import envfile
from bot.admin.server import AdminContext, create_app
from bot.storage import FailedStore, GroupStore, HistoryStore, JsonObjectFile
from bot.timeutil import today_vn

ADMIN_TOKEN = "admin-token-123456"
ZALO_TOKEN = "999:zalo-secret-token"
BASE = "http://127.0.0.1:8081"
AUTH = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

ENV_TEXT = f"""# Chú thích đầu file
ZALO_BOT_TOKEN={ZALO_TOKEN}
GEMINI_API_KEY=
# Hạn mức
DAILY_TOKEN_BUDGET=1000
ADMIN_TOKEN={ADMIN_TOKEN}
DATA_DIR=data
WORKSPACE_DIR=workspace
LOG_DIR=logs
OWNER_ZALO_ID=owner
"""


@pytest.fixture
def env_path(tmp_path, monkeypatch):
    for key in ("DATA_DIR", "WORKSPACE_DIR", "LOG_DIR", "ADMIN_TOKEN", "ZALO_BOT_TOKEN", "GEMINI_API_KEY",
                "ADMIN_SHOW_HISTORY", "DAILY_TOKEN_BUDGET", "OWNER_ZALO_ID"):
        monkeypatch.delenv(key, raising=False)
    path = tmp_path / ".env"
    path.write_text(ENV_TEXT, encoding="utf-8")
    (tmp_path / "workspace").mkdir()
    (tmp_path / "workspace" / "SYSTEM.md").write_text("Bạn là trợ lý.", encoding="utf-8")
    return path


@pytest.fixture
def client(env_path, tmp_path):
    app = create_app(AdminContext(env_path, tmp_path), 8081)
    return TestClient(app, base_url=BASE)


# ---------- bảo mật ----------

def test_api_requires_token(client):
    assert client.get("/api/status").status_code == 401
    assert client.get("/api/status", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/api/status", headers={"Authorization": ADMIN_TOKEN}).status_code == 401
    assert client.get("/api/status", headers=AUTH).status_code == 200


def test_rejects_foreign_host(env_path, tmp_path):
    app = create_app(AdminContext(env_path, tmp_path), 8081)
    for base in ("http://evil.example:8081", "http://127.0.0.1:9999"):
        assert TestClient(app, base_url=base).get("/api/status", headers=AUTH).status_code == 400
    assert TestClient(app, base_url="http://localhost:8081").get("/api/status", headers=AUTH).status_code == 200


def test_rejects_cross_origin_writes(client):
    body = {"allowed": True}
    bad = client.patch("/api/groups/g1", json=body, headers={**AUTH, "Origin": "http://evil.example"})
    assert bad.status_code == 403
    cross = client.patch("/api/groups/g1", json=body, headers={**AUTH, "Sec-Fetch-Site": "cross-site"})
    assert cross.status_code == 403
    ok = client.patch("/api/groups/g1", json=body, headers={**AUTH, "Origin": BASE})
    assert ok.status_code == 200


def test_static_page_has_security_headers(client):
    page = client.get("/")
    assert page.status_code == 200 and "Quản lý Bot Zalo" in page.text
    assert "script-src 'self'" in page.headers["content-security-policy"]
    assert page.headers["x-frame-options"] == "DENY"
    assert client.get("/static/app.js").status_code == 200


def test_secrets_never_leave_the_server(client):
    for path in ("/api/status", "/api/settings", "/api/groups", "/api/tools"):
        text = client.get(path, headers=AUTH).text
        assert ZALO_TOKEN not in text and ADMIN_TOKEN not in text, path
    secrets = {s["key"]: s["set"] for s in client.get("/api/settings", headers=AUTH).json()["secrets"]}
    assert secrets == {"ZALO_BOT_TOKEN": True, "GEMINI_API_KEY": False, "WEBHOOK_SECRET": False, "SCHEDULE_API_KEY": False}


# ---------- cài đặt / .env ----------

def test_settings_update_keeps_comments_and_backs_up(client, env_path):
    res = client.put("/api/settings", json={"values": {"DAILY_TOKEN_BUDGET": "5000", "BOT_TRIGGERS": "/bot,@Trợ lý"}}, headers=AUTH)
    assert res.status_code == 200, res.text
    text = env_path.read_text(encoding="utf-8")
    assert "DAILY_TOKEN_BUDGET=5000" in text and "# Hạn mức" in text and text.startswith("# Chú thích đầu file")
    assert text.index("DAILY_TOKEN_BUDGET") < text.index("ADMIN_TOKEN")  # giữ thứ tự dòng
    assert "BOT_TRIGGERS=/bot,@Trợ lý" in text
    assert env_path.with_name(".env.bak").read_text(encoding="utf-8") == ENV_TEXT
    fields = {f["key"]: f["value"] for f in client.get("/api/settings", headers=AUTH).json()["fields"]}
    assert fields["DAILY_TOKEN_BUDGET"] == "5000"


@pytest.mark.parametrize("values", [
    {"DAILY_TOKEN_BUDGET": "abc"},
    {"HISTORY_TURNS": "0"},
    {"RECEIVE_MODE": "pigeon"},
    {"GEMINI_MODEL": "x\nADMIN_TOKEN=hacked"},
    {"GEMINI_MODEL": "x # comment"},
    {"ADMIN_TOKEN": "hacked"},
    {"DATA_DIR": "C:/Windows"},
])
def test_settings_rejects_bad_or_forbidden_values(client, env_path, values):
    assert client.put("/api/settings", json={"values": values}, headers=AUTH).status_code == 400
    assert env_path.read_text(encoding="utf-8") == ENV_TEXT


def test_secret_is_write_only(client, env_path):
    res = client.put("/api/secrets/GEMINI_API_KEY", json={"value": "new-gemini-key"}, headers=AUTH)
    assert res.status_code == 200
    assert "GEMINI_API_KEY=new-gemini-key" in env_path.read_text(encoding="utf-8")
    assert "new-gemini-key" not in client.get("/api/settings", headers=AUTH).text
    assert client.put("/api/secrets/ADMIN_TOKEN", json={"value": "x"}, headers=AUTH).status_code == 404
    assert client.put("/api/secrets/WEBHOOK_SECRET", json={"value": "short"}, headers=AUTH).status_code == 400


def test_envfile_appends_missing_keys(tmp_path):
    path = tmp_path / ".env"
    path.write_text("# a\nA=1\n", encoding="utf-8")
    envfile.update(path, {"B": "2", "A": "3"})
    assert path.read_text(encoding="utf-8") == "# a\nA=3\nB=2\n"
    fresh = tmp_path / "new.env"
    envfile.update(fresh, {"ADMIN_TOKEN": "t"})
    assert fresh.read_text(encoding="utf-8") == "ADMIN_TOKEN=t\n"


# ---------- nhóm: giao diện và bot cùng ghi groups.txt ----------

def test_group_changes_reach_running_bot_without_clobbering(client, tmp_path):
    bot_store = GroupStore(tmp_path / "data" / "groups.txt")  # bản bot đang giữ trong RAM
    assert not bot_store.get("g1").allowed

    res = client.patch("/api/groups/g1", json={"allowed": True, "mode": "all", "label": "Nhà mình"}, headers=AUTH)
    assert res.json() == {"chat_id": "g1", "allowed": True, "mode": "all", "label": "Nhà mình"}
    state = bot_store.get("g1")
    assert state.allowed and state.mode == "all" and state.label == "Nhà mình"

    bot_store.set_mode("g2", "all")  # bot ghi sau: không được làm mất thay đổi của giao diện
    again = GroupStore(tmp_path / "data" / "groups.txt")
    assert again.get("g1").label == "Nhà mình" and again.get("g2").mode == "all"

    assert client.patch("/api/groups/g1", json={"mode": "loud"}, headers=AUTH).status_code == 400


def test_groups_list_includes_seen_but_not_allowed_chats(client, tmp_path):
    JsonObjectFile(tmp_path / "data" / "activity.txt").write({
        "new-group": {"type": "GROUP", "last_seen": 2, "last_name": "An"},
        "owner": {"type": "PRIVATE", "last_seen": 1, "last_name": "Chủ"},
    })
    rows = {r["chat_id"]: r for r in client.get("/api/groups", headers=AUTH).json()["groups"]}
    assert not rows["new-group"]["allowed"] and rows["new-group"]["last_name"] == "An"
    assert rows["owner"]["owner_private"]


# ---------- hội thoại ----------

def test_history_view_and_toggle(client, env_path, tmp_path):
    HistoryStore(tmp_path / "data" / "history").append("g1", "user", "xin chào", uid="u", name="An")
    data = client.get("/api/history/g1", headers=AUTH).json()
    assert data["messages"][0]["text"] == "xin chào" and data["messages"][0]["name"] == "An"
    for evil in ("..%2F..%2F.env", "..%5C..%5C.env", "....env"):
        res = client.get(f"/api/history/{evil}", headers=AUTH)
        assert res.status_code == 404 or res.json()["messages"] == [], evil
        assert ZALO_TOKEN not in res.text
    assert client.delete("/api/groups/g1/history", headers=AUTH).json() == {"ok": True}
    assert client.get("/api/history/g1", headers=AUTH).json()["messages"] == []

    env_path.write_text(ENV_TEXT + "ADMIN_SHOW_HISTORY=false\n", encoding="utf-8")
    assert client.get("/api/history/g1", headers=AUTH).status_code == 403


# ---------- chỉ dẫn ----------

def test_workspace_edit_with_backup(client, tmp_path):
    assert client.get("/api/workspace/SYSTEM", headers=AUTH).json()["content"] == "Bạn là trợ lý."
    res = client.put("/api/workspace/SYSTEM", json={"content": "Trợ lý mới\r\n"}, headers=AUTH)
    assert res.status_code == 200
    assert (tmp_path / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "Trợ lý mới\n"
    backups = list((tmp_path / "workspace" / ".backup").glob("SYSTEM-*.md"))
    assert len(backups) == 1 and backups[0].read_text(encoding="utf-8") == "Bạn là trợ lý."
    assert client.get("/api/workspace/MEMORY", headers=AUTH).json()["content"] == ""
    for name in ("README", "..%2F..%2F.env", "system"):
        assert client.get(f"/api/workspace/{name}", headers=AUTH).status_code == 404


# ---------- log, tin lỗi, chat thử, tool, điều khiển ----------

def test_logs_group_tracebacks_and_filter(client, tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "bot.log").write_text(
        "2026-10-22 07:00:00,001 INFO bot: khởi động\n"
        "2026-10-22 07:00:01,001 ERROR bot.app: hỏng\nTraceback (most recent call last):\n  File x\n"
        "2026-10-22 07:00:02,001 WARNING bot: cảnh báo\n",
        encoding="utf-8",
    )
    entries = client.get("/api/logs?n=10", headers=AUTH).json()["entries"]
    assert [e["level"] for e in entries] == ["INFO", "ERROR", "WARNING"]
    assert "Traceback" in entries[1]["text"]
    errors = client.get("/api/logs?level=ERROR", headers=AUTH).json()["entries"]
    assert [e["level"] for e in errors] == ["ERROR"]
    assert client.get("/api/logs?source=../../.env", headers=AUTH).status_code == 404


def test_failed_list_and_dismiss(client, tmp_path):
    store = FailedStore(tmp_path / "data" / "failed.txt")
    store.add("g1", "câu trả lời", "[500] lỗi")
    [item] = client.get("/api/failed", headers=AUTH).json()["items"]
    assert item["text"] == "câu trả lời"
    res = client.post(f"/api/failed/{item['id']}/dismiss", headers=AUTH).json()
    assert res["ok"]
    assert client.get("/api/failed", headers=AUTH).json()["items"] == []
    assert client.post(f"/api/failed/{item['id']}/dismiss", headers=AUTH).status_code == 404


def test_playground_uses_echo_without_key_and_keeps_group_history_clean(client, tmp_path):
    res = client.post("/api/playground", json={"messages": [{"role": "user", "text": "chào bot"}]}, headers=AUTH).json()
    assert res["ok"] and res["echo"] and "chào bot" in res["reply"]
    assert not (tmp_path / "data" / "history").exists()
    assert client.post("/api/playground", json={"messages": []}, headers=AUTH).status_code == 400


def test_tools_list_is_empty_by_default(client):
    assert client.get("/api/tools", headers=AUTH).json() == {"tools": []}


def test_bot_control_uses_gateway(client, monkeypatch):
    calls = []

    def fake_start(settings, service):
        calls.append(service.name)
        return gateway.Result(0, "Đã bật bot")

    monkeypatch.setattr(gateway, "start", fake_start)
    assert client.post("/api/bot/start", headers=AUTH).json() == {"ok": True, "message": "Đã bật bot"}
    assert calls == ["bot"]
    assert client.post("/api/bot/explode", headers=AUTH).status_code == 404


def test_status_reports_alerts_and_stats(client, tmp_path):
    JsonObjectFile(tmp_path / "data" / "stats.txt").write({today_vn(): {"received": 3, "replied": 2, "tokens": 1500}})
    JsonObjectFile(tmp_path / "data" / "usage.txt").write({"day": today_vn(), "tokens": 1500})
    data = client.get("/api/status", headers=AUTH).json()
    assert data["today"]["received"] == 3 and data["tokens_today"] == 1500
    assert any("GEMINI_API_KEY" in a for a in data["alerts"])
    assert any("hạn mức" in a for a in data["alerts"])
    assert data["running"] is False


# ---------- đăng nhập acc Zalo cá nhân bằng QR ----------

def test_zalo_qr_login_saves_session_and_enables_personal(client, env_path, tmp_path, monkeypatch):
    import time

    from bot.zalo import qrlogin

    class FakeLogin:
        def __init__(self, *args, **kwargs):
            self.status = qrlogin.QrStatus(state=qrlogin.WAITING_SCAN, image="UE5H", message="Quét mã")

        def report(self, state, message="", **extra):
            self.status = qrlogin.QrStatus(state=state, message=message, display_name=extra.get("display_name", ""))

        def run(self):
            self.report(qrlogin.SUCCESS, "Đã kết nối acc An.", display_name="An")
            return qrlogin.ZaloSession(cookies={"zpw_sek": "x"}, imei="imei-1", display_name="An")

        def cancel(self):
            pass

    monkeypatch.setattr(qrlogin, "QrLogin", FakeLogin)
    assert client.get("/api/zalo-login", headers=AUTH).json()["state"] == "idle"
    assert client.post("/api/zalo-login/start", headers=AUTH).status_code == 200
    for _ in range(50):
        data = client.get("/api/zalo-login", headers=AUTH).json()
        if data["state"] == "success" and "RECEIVE_MODE" in data["message"]:
            break
        time.sleep(0.05)
    assert data["state"] == "success" and data["session"]["exists"] and data["session"]["display_name"] == "An"
    assert "imei-1" not in str(data) and "zpw_sek" not in str(data)  # không lộ phiên đăng nhập ra API
    assert "RECEIVE_MODE=personal" in env_path.read_text(encoding="utf-8")
    assert json.loads((tmp_path / "data" / "zalo_session.json").read_text(encoding="utf-8"))["imei"] == "imei-1"


def test_update_button_asks_gui_to_update_and_shows_pending(client, tmp_path, monkeypatch):
    from bot import updater

    (tmp_path / "data").mkdir(exist_ok=True)
    (tmp_path / "data" / "update.txt").write_text("3", encoding="utf-8")
    assert client.get("/api/status", headers=AUTH).json()["updates_pending"] == 3

    monkeypatch.setattr(updater, "unavailable_reason", lambda: None)
    monkeypatch.setattr(gateway, "gui_running", lambda settings: True)
    res = client.post("/api/update", headers=AUTH).json()
    assert res["ok"] and (tmp_path / "data" / "gui.update").exists()

    monkeypatch.setattr(updater, "unavailable_reason", lambda: "Đang chạy ZaloBot.exe")
    assert client.post("/api/update", headers=AUTH).json() == {"ok": False, "message": "Đang chạy ZaloBot.exe"}
