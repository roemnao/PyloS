"""GeminiAgent gửi ảnh/video/tin thoại: nhúng thẳng nếu nhỏ, tải lên Files API nếu lớn hoặc là video."""

from __future__ import annotations

import time
from types import SimpleNamespace

from test_agent import CTX, FakeModels, response

from pylos.residential.residents.pylos import GeminiAgent, ToolRegistry, Turn
from pylos.residential.residents.pylos.gemini_agent import MediaRef


class FakeFiles:
    def __init__(self, states=("ACTIVE",)):
        self.states = list(states)
        self.uploads = []
        self.gets = 0

    async def upload(self, *, file, config):
        self.uploads.append((file, config))
        return SimpleNamespace(name="files/abc", uri="https://gen/files/abc", state=SimpleNamespace(name=self.states.pop(0)))

    async def get(self, *, name):
        self.gets += 1
        return SimpleNamespace(name=name, uri="https://gen/files/abc", state=SimpleNamespace(name=self.states.pop(0)))


def make(tmp_path, files=None, **kwargs):
    models = FakeModels([response("xong")])
    files = files or FakeFiles()
    client = SimpleNamespace(aio=SimpleNamespace(models=models, files=files))
    agent = GeminiAgent("key", "gemini-test", ToolRegistry(), client=client, **kwargs)
    return agent, models, files


def media_file(tmp_path, name, size, kind="photo", mime="image/jpeg"):
    path = tmp_path / name
    path.write_bytes(b"\x01" * size)
    return MediaRef(path, mime, kind, msg_id=name)


async def test_small_photo_is_inlined(tmp_path):
    agent, models, files = make(tmp_path)
    ref = media_file(tmp_path, "a.jpg", 1000)
    await agent.reply("sys", [Turn("user", "ảnh gì", "An", (ref,))], CTX)
    parts = models.requests[0][1][0].parts
    assert parts[0].text == "An: ảnh gì"
    assert parts[1].inline_data.mime_type == "image/jpeg" and len(parts[1].inline_data.data) == 1000
    assert files.uploads == []


async def test_voice_is_inlined_with_its_mime(tmp_path):
    agent, models, _ = make(tmp_path)
    ref = media_file(tmp_path, "v.aac", 500, "voice", "audio/aac")
    await agent.reply("sys", [Turn("user", "(gửi tin nhắn thoại)", "An", (ref,))], CTX)
    assert models.requests[0][1][0].parts[1].inline_data.mime_type == "audio/aac"


async def test_video_is_uploaded_and_uri_is_reported_back(tmp_path):
    agent, models, files = make(tmp_path)
    ref = media_file(tmp_path, "v.mp4", 1000, "video", "video/mp4")
    await agent.reply("sys", [Turn("user", "video gì", "An", (ref,))], CTX)
    assert len(files.uploads) == 1 and files.uploads[0][1] == {"mime_type": "video/mp4"}
    part = models.requests[0][1][0].parts[1]
    assert part.file_data.file_uri == "https://gen/files/abc" and part.file_data.mime_type == "video/mp4"
    assert ref.file_uri == "https://gen/files/abc" and ref.file_uri_expires > time.time()
    config = models.requests[0][2]
    assert config.media_resolution.name == "MEDIA_RESOLUTION_LOW"


async def test_large_photo_is_uploaded(tmp_path):
    agent, models, files = make(tmp_path, media_inline_max_mb=1)
    ref = media_file(tmp_path, "big.jpg", 2 * 1024 * 1024)
    await agent.reply("sys", [Turn("user", "x", "An", (ref,))], CTX)
    assert len(files.uploads) == 1


async def test_inline_budget_is_shared_across_turns(tmp_path):
    agent, models, files = make(tmp_path, media_inline_max_mb=1)
    first = media_file(tmp_path, "1.jpg", 700 * 1024)
    second = media_file(tmp_path, "2.jpg", 700 * 1024)
    turns = [Turn("user", "một", "An", (first,)), Turn("model", "ok"), Turn("user", "hai", "An", (second,))]
    await agent.reply("sys", turns, CTX)
    assert len(files.uploads) == 1  # ảnh thứ hai vượt hạn mức nhúng chung


async def test_unexpired_file_uri_is_reused_without_upload(tmp_path):
    agent, models, files = make(tmp_path)
    ref = media_file(tmp_path, "v.mp4", 1000, "video", "video/mp4")
    ref.file_uri, ref.file_uri_expires = "https://gen/files/old", time.time() + 3600
    await agent.reply("sys", [Turn("user", "hỏi tiếp", "An", (ref,))], CTX)
    assert files.uploads == []
    assert models.requests[0][1][0].parts[1].file_data.file_uri == "https://gen/files/old"


async def test_expired_file_uri_uploads_again(tmp_path):
    agent, models, files = make(tmp_path)
    ref = media_file(tmp_path, "v.mp4", 1000, "video", "video/mp4")
    ref.file_uri, ref.file_uri_expires = "https://gen/files/old", time.time() - 10
    await agent.reply("sys", [Turn("user", "hỏi tiếp", "An", (ref,))], CTX)
    assert len(files.uploads) == 1


async def test_upload_waits_until_active(tmp_path, monkeypatch):
    async def no_sleep(_):
        return None

    monkeypatch.setattr("pylos.residential.residents.pylos.gemini_agent.asyncio.sleep", no_sleep)
    agent, models, files = make(tmp_path, files=FakeFiles(["PROCESSING", "PROCESSING", "ACTIVE"]))
    ref = media_file(tmp_path, "v.mp4", 1000, "video", "video/mp4")
    await agent.reply("sys", [Turn("user", "x", "An", (ref,))], CTX)
    assert files.gets == 2 and ref.file_uri


async def test_text_only_turns_unchanged(tmp_path):
    agent, models, _ = make(tmp_path)
    await agent.reply("sys", [Turn("user", "chào", "An")], CTX)
    assert len(models.requests[0][1][0].parts) == 1
    assert models.requests[0][2].media_resolution is None


# ---------- tìm web (agent.search) ----------


def grounded(text, uris):
    chunks = [SimpleNamespace(web=SimpleNamespace(title=f"T{i}", uri=u)) for i, u in enumerate(uris)]
    resp = response(text, tokens=40)
    resp.candidates[0].grounding_metadata = SimpleNamespace(grounding_chunks=chunks)
    return resp


async def test_search_uses_only_google_search_tool_and_returns_sources():
    models = FakeModels([grounded("Vàng SJC 80 triệu", ["https://a.example", "https://b.example", "https://a.example"])])
    client = SimpleNamespace(aio=SimpleNamespace(models=models))
    agent = GeminiAgent("key", "gemini-test", ToolRegistry(), client=client)
    result, tokens = await agent.search("giá vàng hôm nay")
    assert result["answer"] == "Vàng SJC 80 triệu" and tokens == 40
    assert [s["uri"] for s in result["sources"]] == ["https://a.example", "https://b.example"]  # bỏ trùng
    model, contents, config = models.requests[0]
    assert contents[0].parts[0].text == "giá vàng hôm nay"
    assert len(config.tools) == 1 and config.tools[0].google_search is not None
    assert not config.tools[0].function_declarations  # không trộn với function calling


async def test_search_without_grounding_metadata():
    models = FakeModels([response("không có nguồn")])
    client = SimpleNamespace(aio=SimpleNamespace(models=models))
    agent = GeminiAgent("key", "gemini-test", ToolRegistry(), client=client)
    result, _ = await agent.search("x")
    assert result["sources"] == [] and result["answer"] == "không có nguồn"
