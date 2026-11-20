"""Tải tệp đính kèm và kho tệp trong túp lều."""

import httpx
import pytest

from pylos.gate.fence.token_limit.rate_limiter import RateLimiter
from pylos.gate.main_gate.media import media_fetch
from pylos.gate.main_gate.media.media_fetch import Limits, MediaError, MediaFile, fetch_attachment
from pylos.gate.main_gate.media.media_store import MediaStore
from pylos.gate.main_gate.zalo.incoming_message import Attachment

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100
AAC = b"\xff\xf1" + b"0" * 100


@pytest.fixture
def serve(monkeypatch):
    def install(handler):
        monkeypatch.setattr(media_fetch, "transport", httpx.MockTransport(handler))

    return install


def reply(body, content_type="image/jpeg", status=200, headers=None):
    def handler(request):
        return httpx.Response(status, content=body, headers={"content-type": content_type, **(headers or {})})

    return handler


async def test_downloads_photo(serve, tmp_path):
    serve(reply(JPEG))
    att = Attachment(kind="photo", url="https://cdn.zalo/a.jpg")
    out = await fetch_attachment(att, tmp_path, "m1", Limits())
    assert isinstance(out, MediaFile)
    assert out.mime == "image/jpeg" and out.path.name == "m1.jpg" and out.path.read_bytes() == JPEG
    assert not list(tmp_path.glob("*.part"))


async def test_voice_without_content_type_is_guessed(serve, tmp_path):
    serve(reply(AAC, content_type="application/octet-stream"))
    out = await fetch_attachment(Attachment(kind="voice", url="https://cdn.zalo/v"), tmp_path, "m2", Limits())
    assert isinstance(out, MediaFile) and out.mime == "audio/aac" and out.path.suffix == ".aac"


async def test_too_large_stops_while_streaming(serve, tmp_path):
    serve(reply(b"x" * (2 * 1024 * 1024), content_type="image/jpeg"))
    out = await fetch_attachment(Attachment(kind="photo", url="https://cdn.zalo/a.jpg"), tmp_path, "m3",
                                 Limits(photo_mb=1))
    assert out == MediaError("too_large", out.detail)
    assert not list(tmp_path.iterdir())


async def test_too_large_by_declared_size_never_downloads(serve, tmp_path):
    called = []
    serve(lambda request: called.append(1) or httpx.Response(200, content=JPEG))
    att = Attachment(kind="photo", url="https://cdn.zalo/a.jpg", size=50 * 1024 * 1024)
    out = await fetch_attachment(att, tmp_path, "m4", Limits(photo_mb=10))
    assert isinstance(out, MediaError) and out.reason == "too_large" and not called


async def test_unsupported_type(serve, tmp_path):
    serve(reply(b"<html>no</html>", content_type="text/html"))
    out = await fetch_attachment(Attachment(kind="photo", url="https://x/a"), tmp_path, "m5", Limits())
    assert isinstance(out, MediaError) and out.reason == "unsupported"


async def test_file_kind_is_unsupported(tmp_path):
    out = await fetch_attachment(Attachment(kind="file", url="https://x/a.pdf"), tmp_path, "m6", Limits())
    assert isinstance(out, MediaError) and out.reason == "unsupported"


async def test_http_error_and_network_error(serve, tmp_path):
    serve(reply(b"", status=404))
    out = await fetch_attachment(Attachment(kind="photo", url="https://x/a"), tmp_path, "m7", Limits())
    assert isinstance(out, MediaError) and out.reason == "download_failed"

    def boom(request):
        raise httpx.ConnectError("down")

    serve(boom)
    out = await fetch_attachment(Attachment(kind="photo", url="https://x/a"), tmp_path, "m8", Limits())
    assert isinstance(out, MediaError) and out.reason == "download_failed"


def make_file(tmp_path, name="m1.jpg"):
    path = tmp_path / "scratch" / name
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(JPEG)
    return MediaFile(path, "image/jpeg", "photo", len(JPEG))


def store_file(store, chat, msg_id, tmp_path):
    media_dir = store.dir_for(chat)
    media_dir.mkdir(parents=True, exist_ok=True)
    dest = media_dir / f"{msg_id}.jpg"
    dest.write_bytes(JPEG)
    return store.save(chat, msg_id, MediaFile(dest, "image/jpeg", "photo", len(JPEG)), uid="u1", caption="mèo")


def test_store_recent_filters_by_age(tmp_path):
    now = [1000.0]
    store = MediaStore(tmp_path / "huts", keep_hours=1, clock=lambda: now[0])
    store_file(store, "chat", "a", tmp_path)
    now[0] += 1800
    store_file(store, "chat", "b", tmp_path)
    rows = store.recent("chat", ["a", "b", "zzz"])
    assert [r["msg_id"] for r in rows] == ["a", "b"]
    assert rows[0]["full_path"].is_file() and rows[0]["caption"] == "mèo"
    # a đã 30 phút, b mới lưu: giới hạn 20 phút chỉ còn b
    assert [r["msg_id"] for r in store.recent("chat", ["a", "b"], max_age=1200)] == ["b"]


def test_prune_removes_old_files_and_empty_dir(tmp_path):
    now = [1000.0]
    store = MediaStore(tmp_path / "huts", keep_hours=1, clock=lambda: now[0])
    row = store_file(store, "chat", "a", tmp_path)
    media_dir = store.dir_for("chat")
    assert (media_dir / row["path"]).is_file()
    now[0] += 3601
    assert store.prune() == 1
    assert not media_dir.exists()
    assert store.get("chat", "a") is None


def test_save_prunes_expired_siblings(tmp_path):
    now = [1000.0]
    store = MediaStore(tmp_path / "huts", keep_hours=1, clock=lambda: now[0])
    old = store_file(store, "chat", "old", tmp_path)
    now[0] += 7200
    store_file(store, "chat", "new", tmp_path)
    assert not (store.dir_for("chat") / old["path"]).exists()
    assert store.get("chat", "new") is not None


def test_set_file_uri_roundtrip(tmp_path):
    store = MediaStore(tmp_path / "huts")
    store_file(store, "chat", "a", tmp_path)
    store.set_file_uri("chat", "a", "files/abc", 5e12)
    row = store.get("chat", "a")
    assert row["file_uri"] == "files/abc" and row["file_uri_expires"] == 5e12


def test_chat_id_cannot_escape_huts(tmp_path):
    store = MediaStore(tmp_path / "huts")
    assert (tmp_path / "huts") in store.dir_for("../../evil").parents


def test_rate_limiter_window():
    now = [0.0]
    limiter = RateLimiter(2, clock=lambda: now[0], window=3600)
    assert limiter.allow("u") and limiter.allow("u") and not limiter.allow("u")
    now[0] = 3601
    assert limiter.allow("u")
