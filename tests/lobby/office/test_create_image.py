"""Tạo ảnh: nhà cung cấp Cloudflare, ModelCalls.generate_image, tool tao_anh và hạn mức ảnh."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from conftest import make_settings
from pylos.gate.fence.token_limit.image_limit import ImageLimit
from pylos.lobby.dispatch.shared.data_stores import DailyCounter
from pylos.lobby.office.agent_tools import ToolContext, ToolRegistry, create_image
from pylos.lobby.office.model_calls import ModelCalls, ModelCallError
from pylos.lobby.office.model_calls.catalog import KeyEntry
from pylos.lobby.office.model_calls.providers.cloudflare import CloudflareProvider
from pylos.lobby.office.model_calls.results import ImageResult

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 20
JPEG = b"\xff\xd8\xff\xe0" + b"0" * 20
SECRET = "cf-super-secret"
ENTRY = KeyEntry("cf", "cloudflare", "CF_TOKEN", ("@cf/flux",), SECRET, {"account": "acc-1"})


def provider(handler):
    return CloudflareProvider(client_factory=lambda **kw: httpx.AsyncClient(transport=httpx.MockTransport(handler), **kw))


def ok_json(data=PNG):
    return httpx.Response(200, json={"success": True, "result": {"image": base64.b64encode(data).decode()}})


# ---------- Cloudflare ----------

async def test_cloudflare_sends_prompt_steps_and_token_and_decodes_base64():
    seen = {}

    def handler(request):
        seen.update(url=str(request.url), auth=request.headers["authorization"], body=json.loads(request.content))
        return ok_json(PNG)

    result = await provider(handler).generate_image(ENTRY, "@cf/flux", "a cat", steps=6)
    assert seen["url"].endswith("/accounts/acc-1/ai/run/@cf/flux") and seen["auth"] == f"Bearer {SECRET}"
    assert seen["body"] == {"prompt": "a cat", "steps": 6}
    assert result == ImageResult(PNG, "image/png", "@cf/flux") and result.extension == ".png"


async def test_cloudflare_steps_are_clamped_and_jpeg_is_recognised():
    bodies = []

    def handler(request):
        bodies.append(json.loads(request.content)["steps"])
        return ok_json(JPEG)

    result = await provider(handler).generate_image(ENTRY, "@cf/flux", "x", steps=99)
    assert bodies == [8] and result.mime == "image/jpeg" and result.extension == ".jpg"


async def test_cloudflare_accepts_a_raw_image_response():
    result = await provider(lambda r: httpx.Response(200, content=PNG, headers={"content-type": "image/png"})) \
        .generate_image(ENTRY, "@cf/flux", "x")
    assert result.data == PNG


@pytest.mark.parametrize("status,retryable,text", [
    (401, False, "từ chối token"), (403, False, "từ chối token"),
    (429, True, "hết hạn mức"), (503, True, "máy chủ"), (400, False, "từ chối yêu cầu"),
])
async def test_cloudflare_errors_are_clear_and_never_leak_the_token(status, retryable, text):
    body = {"success": False, "errors": [{"message": "bad things"}]}
    with pytest.raises(ModelCallError) as info:
        await provider(lambda r: httpx.Response(status, json=body)).generate_image(ENTRY, "@cf/flux", "x")
    assert text in str(info.value) and info.value.retryable is retryable
    assert SECRET not in str(info.value)


async def test_cloudflare_timeout_garbage_and_non_image_data():
    def slow(request):
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(ModelCallError, match="không trả lời") as timeout:
        await provider(slow).generate_image(ENTRY, "@cf/flux", "x", timeout=5)
    assert timeout.value.retryable
    with pytest.raises(ModelCallError, match="không có ảnh"):
        await provider(lambda r: httpx.Response(200, json={"success": True, "result": {}})).generate_image(ENTRY, "m", "x")
    with pytest.raises(ModelCallError, match="không phải ảnh"):
        await provider(lambda r: ok_json(b"not an image at all")).generate_image(ENTRY, "m", "x")


# ---------- ModelCalls.generate_image ----------

KEYS = "## cf\nprovider: cloudflare\nkey: CF_TOKEN\naccount: CF_ACCOUNT\nmodels: m-main, m-backup\n"


def calls(tmp_path, outcomes):
    """ModelCalls với nhà cung cấp giả: outcomes = {model: ImageResult hoặc ModelCallError}."""
    path = tmp_path / "model_keys.md"
    path.write_text(KEYS, encoding="utf-8")
    mc = ModelCalls(lambda name: {"CF_TOKEN": "t", "CF_ACCOUNT": "a"}.get(name, ""), path)
    tried = []

    class Fake:
        async def generate_image(self, entry, model, prompt, *, steps, timeout):
            tried.append(model)
            outcome = outcomes[model]
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

    mc._providers["cloudflare"] = Fake()
    return mc, tried


async def test_generate_image_tries_fallbacks_only_for_retryable_errors(tmp_path):
    good = ImageResult(PNG, "image/png", "m-backup")
    mc, tried = calls(tmp_path, {"m-main": ModelCallError("hết hạn mức", retryable=True), "m-backup": good})
    assert await mc.generate_image("p", "m-main", fallbacks=("m-backup", "m-main")) == good
    assert tried == ["m-main", "m-backup"]

    mc, tried = calls(tmp_path, {"m-main": ModelCallError("token sai"), "m-backup": good})
    with pytest.raises(ModelCallError, match="token sai"):
        await mc.generate_image("p", "m-main", fallbacks=("m-backup",))
    assert tried == ["m-main"]


async def test_generate_image_reports_models_without_a_key_or_without_image_support(tmp_path):
    mc, _ = calls(tmp_path, {})
    with pytest.raises(ModelCallError, match="chưa có key"):
        await mc.generate_image("p", "unknown-model")
    path = tmp_path / "gem.md"
    path.write_text("## g\nprovider: gemini\nkey: G\nmodels: gm\n", encoding="utf-8")
    gem = ModelCalls(lambda name: "x", path)
    with pytest.raises(ModelCallError, match="chưa tạo ảnh được"):
        await gem.generate_image("p", "gm")


# ---------- hạn mức ảnh ----------

def test_image_limit_per_day_and_per_user_hour(tmp_path):
    now = [0.0]
    limit = ImageLimit(DailyCounter(tmp_path / "image_usage.txt"), per_day=3, per_user_hour=2, clock=lambda: now[0])
    assert limit.check("a") is None
    limit.record("a"); limit.record("a")
    assert "1 giờ" in limit.check("a") and limit.check("b") is None  # người khác vẫn tạo được
    now[0] = 3601
    assert limit.check("a") is None  # qua một giờ thì người đó tạo lại được
    limit.record("a")
    assert "đủ 3 ảnh" in limit.check("b")  # hết hạn mức ngày cho mọi người


def test_image_limit_zero_means_unlimited_and_failed_runs_cost_nothing(tmp_path):
    limit = ImageLimit(DailyCounter(tmp_path / "u.txt"), per_day=0, per_user_hour=0)
    for _ in range(20):
        limit.record("a")
    assert limit.check("a") is None
    limit = ImageLimit(DailyCounter(tmp_path / "v.txt"), per_day=1, per_user_hour=1)
    assert limit.check("a") is None and limit.check("a") is None  # check không ghi


# ---------- tool tao_anh ----------

class FakeCalls:
    def __init__(self, result=None, error=None, known=("@cf/flux",)):
        self.result, self.error, self.known, self.requests = result, error, known, []

    def resolve(self, model):
        return object() if model in self.known else None

    async def generate_image(self, prompt, model, **kwargs):
        self.requests.append((prompt, model, kwargs))
        if self.error:
            raise self.error
        return self.result


@pytest.fixture
def tool(tmp_path):
    saved = (create_image.CONFIG.enabled, create_image.CONFIG.calls, create_image.CONFIG.task,
             create_image.CONFIG.limit, create_image.CONFIG.limit_path)

    def setup(calls, **overrides):
        settings = make_settings(tmp_path, **overrides)
        create_image.configure(settings, model_calls=calls, task=lambda: ("@cf/flux", ("@cf/fb",)))
        registry = ToolRegistry(create_image.TOOLS)
        return settings, registry

    yield setup
    (create_image.CONFIG.enabled, create_image.CONFIG.calls, create_image.CONFIG.task,
     create_image.CONFIG.limit, create_image.CONFIG.limit_path) = saved


def ctx_for(tmp_path):
    return ToolContext("chat-1", "user-1", "An", is_owner=False, huts_dir=tmp_path / "huts")


async def test_tool_creates_saves_and_queues_the_image(tmp_path, tool):
    calls = FakeCalls(ImageResult(PNG, "image/png", "@cf/flux"))
    settings, registry = tool(calls, IMAGE_STEPS="5")
    assert registry.names() == ["tao_anh"]
    ctx = ctx_for(tmp_path)
    reply = await registry.call("tao_anh", {"prompt": "  a cat  ", "caption": "Mèo nè"}, ctx)
    assert reply["ok"] is True
    prompt, model, kwargs = calls.requests[0]
    assert (prompt, model) == ("a cat", "@cf/flux") and kwargs["steps"] == 5 and kwargs["fallbacks"] == ("@cf/fb",)
    (image,) = ctx.outbox
    assert image.caption == "Mèo nè" and image.path.suffix == ".png" and image.path.read_bytes() == PNG
    assert image.path.parent == tmp_path / "huts" / "chat-1" / "media"
    assert DailyCounter(settings.data_dir / "image_usage.txt").today() == 1


async def test_tool_is_hidden_when_off_or_without_a_usable_key(tmp_path, tool):
    _, registry = tool(FakeCalls(), IMAGE_GEN="false")
    assert registry.names() == []
    _, registry = tool(FakeCalls(known=()))  # model của nhiệm vụ image chưa có key
    assert registry.names() == []
    _, registry = tool(FakeCalls())
    assert registry.names() == ["tao_anh"]


async def test_tool_reports_errors_and_limits_without_queueing_or_counting(tmp_path, tool):
    calls = FakeCalls(error=ModelCallError("hết hạn mức"))
    settings, registry = tool(calls, USER_IMAGES_PER_HOUR="1")
    ctx = ctx_for(tmp_path)
    assert "hết hạn mức" in (await registry.call("tao_anh", {"prompt": "x"}, ctx))["error"]
    assert not ctx.outbox and DailyCounter(settings.data_dir / "image_usage.txt").today() == 0
    assert (await registry.call("tao_anh", {"prompt": ""}, ctx))["error"] == "Thiếu prompt."

    calls.error, calls.result = None, ImageResult(PNG, "image/png", "@cf/flux")
    assert (await registry.call("tao_anh", {"prompt": "x"}, ctx))["ok"] is True
    refused = await registry.call("tao_anh", {"prompt": "y"}, ctx)
    assert "1 giờ" in refused["error"] and len(ctx.outbox) == 1 and len(calls.requests) == 2


def test_image_settings_have_defaults_and_validation(tmp_path):
    s = make_settings(tmp_path)
    assert (s.image_gen, s.image_steps, s.image_per_day, s.user_images_per_hour) == (True, 4, 50, 5)
    from pylos.lobby.dispatch.shared.config import ConfigError

    with pytest.raises(ConfigError):
        make_settings(tmp_path, IMAGE_STEPS="0")
