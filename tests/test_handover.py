from __future__ import annotations

import io
import zipfile
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from bot.config import Settings
from bot.system import bot_process, handover, handover_job, remote_server
from bot.ui.admin.admin_web_server import AdminContext, create_app

LOCAL_TOKEN = "local-token-123456"
VPS_TOKEN = "vps-token-abcdef12"
BASE = "http://127.0.0.1:8081"
ENV_KEYS = ("ADMIN_TOKEN", "REMOTE_URL", "REMOTE_ADMIN_TOKEN", "DATA_DIR", "LOG_DIR", "WORKSPACE_DIR", "SYSTEM_DIR",
            "ZALO_BOT_TOKEN", "GEMINI_API_KEY", "RECEIVE_MODE")


def make_side(root: Path, token: str, extra: str = "") -> tuple[Path, Settings]:
    root.mkdir(parents=True)
    env = root / ".env"
    env.write_text(f"ADMIN_TOKEN={token}\nZALO_BOT_TOKEN=1:abc\nGEMINI_API_KEY=key\nDATA_DIR=data\n"
                   f"WORKSPACE_DIR=data/workspace\nLOG_DIR=logs\nSYSTEM_DIR=system\n{extra}", encoding="utf-8")
    return env, AdminContext(env, root).settings()


@pytest.fixture
def clean_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def running(monkeypatch):
    """Giả lập tiến trình bot: mỗi bên (theo system_dir) có cờ chạy/dừng; start tôn trọng chế độ chờ."""
    state: dict[Path, bool] = {}
    fail_start: set[Path] = set()

    monkeypatch.setattr(bot_process, "is_running", lambda s, service=bot_process.BOT: state.get(s.system_dir, False))

    def start(settings, service=bot_process.BOT, *, force=False):
        if force:
            bot_process.clear_standby(settings)
        if bot_process.standby_info(settings):
            return bot_process.Result(1, "đang chờ")
        if settings.system_dir in fail_start:
            return bot_process.Result(1, "không bật được")
        state[settings.system_dir] = True
        return bot_process.Result(0, "đã bật")

    def stop(settings, service=bot_process.BOT):
        state[settings.system_dir] = False
        return bot_process.Result(0, "đã dừng")

    monkeypatch.setattr(bot_process, "start", start)
    monkeypatch.setattr(bot_process, "stop", stop)
    state["fail_start"] = fail_start  # type: ignore[assignment]
    return state


def write(settings: Settings, rel: str, text: str) -> Path:
    path = settings.data_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------- gói dữ liệu ----------

def test_export_import_roundtrip_and_exclusions(tmp_path, clean_env, running):
    _, src = make_side(tmp_path / "a", LOCAL_TOKEN)
    _, dst = make_side(tmp_path / "b", VPS_TOKEN)
    write(src, "group_settings.txt", "nhom-a")
    write(src, "memorydata/c1.txt", "tin 1")
    write(src, "workspace/SYSTEM.md", "tính cách")
    write(src, "workspace/.backup/old.md", "bản cũ")  # không được đi theo
    write(src, "console_test/x.txt", "thử")
    write(src, "bot.lock", "x")
    src.system_dir.mkdir(parents=True, exist_ok=True)
    (src.system_dir / "processed_message_ids.txt").write_text("id1\n", encoding="utf-8")
    (src.system_dir / "bot.log").write_text("log", encoding="utf-8")
    write(dst, "stale.txt", "chỉ có ở bên nhận")

    bundle = tmp_path / "bundle.zip"
    manifest = handover.export_bundle(src, bundle, origin="test")
    with zipfile.ZipFile(bundle) as zf:
        names = set(zf.namelist())
    assert "data/group_settings.txt" in names and "data/memorydata/c1.txt" in names
    assert "system/processed_message_ids.txt" in names and "manifest.json" in names
    assert not any(".backup" in n or "console_test" in n or n.endswith((".lock", ".log")) for n in names)
    assert not any("settings.env" in n or n.endswith(".env") for n in names)
    assert manifest["files"] == len(names) - 1

    result = handover.import_bundle(dst, bundle)
    assert result["origin"] == "test"
    assert (dst.data_dir / "group_settings.txt").read_text(encoding="utf-8") == "nhom-a"
    assert (dst.data_dir / "workspace" / "SYSTEM.md").read_text(encoding="utf-8") == "tính cách"
    assert (dst.system_dir / "processed_message_ids.txt").read_text(encoding="utf-8") == "id1\n"
    assert not (dst.data_dir / "stale.txt").exists()  # bản sao giống hệt nơi gửi
    backups = list((dst.system_dir / "handover_backups").glob("*.zip"))
    assert len(backups) == 1
    with zipfile.ZipFile(backups[0]) as zf:
        assert "data/stale.txt" in zf.namelist()  # dữ liệu cũ vẫn lấy lại được


def test_import_refused_while_bot_running(tmp_path, clean_env, running):
    _, src = make_side(tmp_path / "a", LOCAL_TOKEN)
    _, dst = make_side(tmp_path / "b", VPS_TOKEN)
    bundle = tmp_path / "bundle.zip"
    handover.export_bundle(src, bundle)
    running[dst.system_dir] = True
    with pytest.raises(handover.HandoverError, match="đang chạy"):
        handover.import_bundle(dst, bundle)


@pytest.mark.parametrize("name", ["../evil.txt", "data/../../evil.txt", "/etc/passwd", "config/settings.env",
                                  "data/.backup/a.md", "userdata/config/settings.env", "data/a.lock"])
def test_import_rejects_unsafe_names(tmp_path, clean_env, running, name):
    _, dst = make_side(tmp_path / "b", VPS_TOKEN)
    bundle = tmp_path / "bad.zip"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("manifest.json", "{}")
        zf.writestr(name, "x")
    write(dst, "keep.txt", "giữ")
    with pytest.raises(handover.HandoverError):
        handover.import_bundle(dst, bundle)
    assert (dst.data_dir / "keep.txt").read_text(encoding="utf-8") == "giữ"  # chưa đụng gì
    assert not (tmp_path / "evil.txt").exists()


def test_import_rejects_non_bundle(tmp_path, clean_env, running):
    _, dst = make_side(tmp_path / "b", VPS_TOKEN)
    junk = tmp_path / "junk.zip"
    junk.write_bytes(b"not a zip")
    with pytest.raises(handover.HandoverError):
        handover.import_bundle(dst, junk)
    no_manifest = tmp_path / "nm.zip"
    with zipfile.ZipFile(no_manifest, "w") as zf:
        zf.writestr("data/a.txt", "x")
    with pytest.raises(handover.HandoverError, match="hợp lệ"):
        handover.import_bundle(dst, no_manifest)


# ---------- điều phối local <-> VPS ----------

@pytest.fixture
def pair(tmp_path, clean_env, running, monkeypatch):
    """Hai server admin thật (local và 'VPS'); VPS được gọi qua MockTransport chuyển thẳng vào app của nó."""
    vps_env, vps = make_side(tmp_path / "vps", VPS_TOKEN)
    _, local = make_side(tmp_path / "local", LOCAL_TOKEN,
                               f"REMOTE_URL=https://vps.example\nREMOTE_ADMIN_TOKEN={VPS_TOKEN}\n")
    vps_client = TestClient(create_app(AdminContext(vps_env, tmp_path / "vps"), 8081), base_url=BASE)

    def handler(request: httpx.Request) -> httpx.Response:
        res = vps_client.request(request.method, request.url.path, content=request.read(),
                                 headers={k: v for k, v in request.headers.items() if k != "host"}, params=dict(request.url.params))
        return httpx.Response(res.status_code, content=res.content, headers={"content-type": res.headers["content-type"]})

    monkeypatch.setattr(remote_server, "sync_transport", httpx.MockTransport(handler))
    handover_job._current = None
    return local, vps


def run_job(local: Settings, to: str):
    return handover_job.start(lambda: local, to, run_in_thread=False)


def test_move_to_vps_and_back(pair, running):
    local, vps = pair
    write(local, "group_settings.txt", "nhom-local")
    running[local.system_dir] = True

    job = run_job(local, "vps")
    assert job.state == "done", job.public()
    assert [s["status"] for s in job.steps] == ["ok"] * 5
    assert not running.get(local.system_dir) and running[vps.system_dir] is True
    assert bot_process.standby_info(local)["reason"].startswith("Bot đang chạy ở VPS")
    assert (vps.data_dir / "group_settings.txt").read_text(encoding="utf-8") == "nhom-local"

    # Cờ chờ giữ máy này không tự bật lại bot.
    assert bot_process.start(local).code == 1

    write(vps, "group_settings.txt", "nhom-vps-moi")
    job = run_job(local, "local")
    assert job.state == "done", job.public()
    assert not running.get(vps.system_dir) and running[local.system_dir] is True
    assert bot_process.standby_info(local) is None
    assert bot_process.standby_info(vps) is not None
    assert (local.data_dir / "group_settings.txt").read_text(encoding="utf-8") == "nhom-vps-moi"


def test_rollback_when_vps_cannot_start(pair, running):
    local, vps = pair
    running[local.system_dir] = True
    running["fail_start"].add(vps.system_dir)  # type: ignore[index]

    job = run_job(local, "vps")
    assert job.state == "error" and "VPS không bật được bot" in job.message
    assert job.steps[-1]["label"].startswith("Hoàn tác") and job.steps[-1]["status"] == "ok"
    assert running[local.system_dir] is True  # máy này chạy lại, không bị gián đoạn
    assert bot_process.standby_info(local) is None


def test_precheck_blocks_mismatched_modes_and_busy_target(pair, running):
    local, vps = pair
    running[vps.system_dir] = True
    job = run_job(local, "vps")
    assert job.state == "error" and "đang chạy ở VPS rồi" in job.message and len(job.steps) == 1
    assert bot_process.standby_info(local) is None  # chưa đụng gì tới bên đang chạy

    with pytest.raises(handover_job.JobError):
        handover_job.precheck("vps", {"receive_mode": "polling"}, {"receive_mode": "personal"})
    with pytest.raises(handover_job.JobError, match="webhook"):
        handover_job.precheck("vps", {"receive_mode": "webhook"}, {"receive_mode": "webhook"})
    with pytest.raises(handover_job.JobError, match="GEMINI"):
        handover_job.precheck("vps", {"receive_mode": "polling"}, {"receive_mode": "polling", "zalo_token_set": True})


def test_start_rejects_bad_target_and_parallel_jobs(pair):
    local, _ = pair
    with pytest.raises(handover_job.JobError):
        handover_job.start(lambda: local, "mars", run_in_thread=False)
    handover_job._current = handover_job.Job("vps")
    with pytest.raises(handover_job.JobError, match="chưa xong"):
        handover_job.start(lambda: local, "vps", run_in_thread=False)


def test_import_endpoint_streams_and_refuses_running(tmp_path, clean_env, running):
    env, dst = make_side(tmp_path / "b", VPS_TOKEN)
    _, src = make_side(tmp_path / "a", LOCAL_TOKEN)
    write(src, "x.txt", "dữ liệu")
    bundle = tmp_path / "bundle.zip"
    handover.export_bundle(src, bundle)
    client = TestClient(create_app(AdminContext(env, tmp_path / "b"), 8081), base_url=BASE)
    auth = {"Authorization": f"Bearer {VPS_TOKEN}", "Content-Type": "application/zip"}
    running[dst.system_dir] = True
    assert client.post("/api/handover/import", content=bundle.read_bytes(), headers=auth).status_code == 409
    running[dst.system_dir] = False
    res = client.post("/api/handover/import", content=bundle.read_bytes(), headers=auth)
    assert res.status_code == 200 and res.json()["ok"]
    assert (dst.data_dir / "x.txt").read_text(encoding="utf-8") == "dữ liệu"
    assert client.post("/api/handover/import", content=b"junk", headers=auth).status_code == 400
    assert client.post("/api/handover/import", content=b"x").status_code == 401


def test_export_endpoint_returns_zip(tmp_path, clean_env, running):
    env, dst = make_side(tmp_path / "b", VPS_TOKEN)
    write(dst, "x.txt", "dữ liệu")
    client = TestClient(create_app(AdminContext(env, tmp_path / "b"), 8081), base_url=BASE)
    res = client.get("/api/handover/export", headers={"Authorization": f"Bearer {VPS_TOKEN}"})
    assert res.status_code == 200
    assert "data/x.txt" in zipfile.ZipFile(io.BytesIO(res.content)).namelist()


def test_target_rejects_backslash_names(tmp_path, clean_env):
    _, dst = make_side(tmp_path / "b", VPS_TOKEN)
    assert handover._target(dst, r"data\x.txt") is None
    assert handover._target(dst, "data/x.txt") == dst.data_dir / "x.txt"
