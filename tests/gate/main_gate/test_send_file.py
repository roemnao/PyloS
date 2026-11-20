"""Gửi tệp vào Zalo bằng acc cá nhân: upload -> chờ file_done qua websocket -> gửi tin tệp (file_upload.py)."""

import hashlib
import json

import pytest

from pylos.gate.main_gate.zalo import ZaloError, ZaloUnsupported, file_upload
from test_personal import FakeApi, ThreadType, make_personal
from pylos.lobby.dispatch.shared.storage import ActivityStore


class Resp:
    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


class FileApi(FakeApi):
    _imei = "imei-1"

    def __init__(self, upload=None, message=None):
        super().__init__()
        self.posts = []
        self.upload = {"fileId": 123, "clientFileId": 77, "chunkId": 1, "finished": 0} if upload is None else upload
        self.message = {"error_code": 0, "data": "{}"} if message is None else message

    def _encode(self, params):
        return "enc:" + json.dumps(params)

    def _decode(self, text):
        return json.loads(text) if isinstance(text, str) else text

    def _post(self, url, params=None, data=None, files=None):
        self.posts.append((url, params, data, files))
        if "asyncfile/upload" in url:
            return Resp({"error_code": 0, "data": {"error_code": 0, "data": self.upload}})
        return Resp(self.message)

    def sent_params(self, index):
        _, _, data, _ = self.posts[index]
        return json.loads(data["params"].removeprefix("enc:"))


def done(file_id=123, url="https://f.zalo/x.docx"):
    file_upload.WATCHER.feed({"data": {"controls": [{"content": {"act_type": "file_done", "fileId": file_id, "data": {"url": url}}}]}})


@pytest.fixture(autouse=True)
def clean_watcher():
    file_upload.WATCHER._urls.clear()
    yield
    file_upload.WATCHER._urls.clear()


@pytest.fixture
def doc(tmp_path):
    path = tmp_path / "Báo cáo.docx"
    path.write_bytes(b"PK-fake-docx" * 50)
    return path


async def test_private_chat_uploads_waits_for_file_done_then_sends(tmp_path, doc):
    api = FileApi()
    zalo = make_personal(tmp_path, api)
    done()
    await zalo.send_file("u1", doc, "Của bạn")
    upload, message = api.posts
    assert upload[0].endswith("/api/message/asyncfile/upload") and upload[1]["type"] == 2
    assert upload[3][0][0] == "chunkContent" and upload[3][0][1][0] == "Báo cáo.docx" and upload[3][0][1][1] == doc.read_bytes()
    sent = json.loads(upload[1]["params"].removeprefix("enc:"))
    assert sent["toid"] == "u1" and sent["totalChunk"] == 1 and sent["totalSize"] == doc.stat().st_size and sent["imei"] == "imei-1"

    assert message[0].endswith("/api/message/asyncfile/msg")
    body = api.sent_params(1)
    assert body["fileId"] == "123" and body["fileUrl"] == "https://f.zalo/x.docx" and body["clientId"] == 77
    assert body["extention"] == "docx" and body["fileName"] == "Báo cáo.docx" and body["toid"] == "u1" and "grid" not in body
    assert body["checksum"] == hashlib.md5(doc.read_bytes()).hexdigest() and body["zsource"] == -1
    assert api.sent == [("u1", "Của bạn", ThreadType.USER)]  # chú thích gửi thành tin chữ


async def test_group_chat_uses_group_endpoints_and_grid(tmp_path, doc):
    api = FileApi()
    zalo = make_personal(tmp_path, api)
    ActivityStore(zalo.settings.data_dir / "chat_activity.txt").touch("g1", "GROUP", "An")
    done()
    await zalo.send_file("g1", doc)
    assert "/api/group/asyncfile/upload" in api.posts[0][0] and api.posts[0][1]["type"] == 11
    assert "/api/group/asyncfile/msg" in api.posts[1][0]
    assert api.sent_params(1)["grid"] == "g1" and "toid" not in api.sent_params(1) and api.sent == []


async def test_file_done_arriving_during_the_wait_is_picked_up(tmp_path, doc):
    import threading

    api = FileApi()
    zalo = make_personal(tmp_path, api)
    timer = threading.Timer(0.05, done)
    timer.start()
    await zalo.send_file("u1", doc)
    timer.join()
    assert len(api.posts) == 2


async def test_no_file_done_means_unsupported_so_the_bot_falls_back_to_text(tmp_path, doc, monkeypatch):
    monkeypatch.setattr(file_upload, "FILE_DONE_TIMEOUT", 0.05)
    api = FileApi()
    with pytest.raises(ZaloUnsupported, match="file_done|tải tệp xong"):
        await make_personal(tmp_path, api).send_file("u1", doc)
    assert len(api.posts) == 1  # đã upload nhưng không gửi tin tệp


async def test_too_large_empty_and_rejected_files(tmp_path, monkeypatch):
    big = tmp_path / "big.docx"
    big.write_bytes(b"x" * (file_upload.MAX_FILE_BYTES + 1))
    api = FileApi()
    with pytest.raises(ZaloUnsupported):
        await make_personal(tmp_path, api).send_file("u1", big)
    empty = tmp_path / "empty.md"
    empty.write_bytes(b"")
    with pytest.raises(ZaloError, match="rỗng"):
        await make_personal(tmp_path, api).send_file("u1", empty)
    assert api.posts == []

    small = tmp_path / "a.md"
    small.write_text("x", encoding="utf-8")
    with pytest.raises(ZaloError, match="không nhận tệp"):
        await make_personal(tmp_path, FileApi(upload={"fileId": -1})).send_file("u1", small)

    done()
    refused = FileApi(message={"error_code": 114, "error_message": "blocked"})
    with pytest.raises(ZaloError, match="blocked"):
        await make_personal(tmp_path, refused).send_file("u1", small)


async def test_unexpected_exceptions_become_network_zalo_errors(tmp_path, doc):
    class Boom(FileApi):
        def _post(self, *a, **k):
            raise RuntimeError("boom")

    with pytest.raises(ZaloError, match="Gửi tệp Zalo cá nhân lỗi") as error:
        await make_personal(tmp_path, Boom()).send_file("u1", doc)
    assert error.value.network


def test_watcher_reads_file_done_in_both_payload_shapes_and_ignores_the_rest():
    watcher = file_upload.FileDoneWatcher()
    watcher.feed(None)
    watcher.feed({"data": "x"})
    watcher.feed({"data": {"controls": [{"content": {"act_type": "group"}}, "junk", {"content": {"act_type": "file_done", "fileId": 5, "data": "{bad"}}]}})
    assert watcher.wait("5", 0.01) is None
    watcher.feed({"data": {"controls": [{"content": {"act_type": "file_done", "fileId": 6, "data": json.dumps({"url": "https://u"})}}]}})
    assert watcher.wait("6", 0.01) == "https://u" and watcher.wait("6", 0.01) is None


def test_install_hook_wraps_zws_decode_once_and_keeps_its_result(monkeypatch):
    from zlapi import _util

    monkeypatch.setattr(file_upload, "_installed", False)
    monkeypatch.setattr(_util, "zws_decode", lambda parsed, key: parsed)
    original = _util.zws_decode
    file_upload.install_hook()
    wrapped = _util.zws_decode
    file_upload.install_hook()
    assert wrapped is not original and _util.zws_decode is wrapped  # chỉ bọc một lần
    packet = {"data": {"controls": [{"content": {"act_type": "file_done", "fileId": 9, "data": {"url": "https://z"}}}]}}
    assert wrapped(packet, "key") is packet
    assert file_upload.WATCHER.wait("9", 0.01) == "https://z"
