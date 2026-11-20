from __future__ import annotations

from types import SimpleNamespace

import pytest

from pylos.residential.residents.pylos import GeminiAgent, PromptBuilder, Tool, ToolContext, ToolRegistry, Turn, discover
from pylos.residential.residents.pylos.gemini_agent import EMPTY_REPLY, TOO_MANY_STEPS

CTX = ToolContext("g", "u", "An", is_owner=False)


def response(text=None, calls=None, tokens=7):
    from google.genai import types

    content = types.Content(role="model", parts=[types.Part.from_text(text=text or "...")])
    return SimpleNamespace(
        text=text,
        function_calls=calls,
        usage_metadata=SimpleNamespace(total_token_count=tokens),
        candidates=[SimpleNamespace(content=content)],
    )


class FakeModels:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    async def generate_content(self, *, model, contents, config):
        self.requests.append((model, list(contents), config))
        return self.responses.pop(0)


def make_agent(responses, tools=None, max_rounds=4):
    models = FakeModels(responses)
    client = SimpleNamespace(aio=SimpleNamespace(models=models))
    agent = GeminiAgent("key", "gemini-test", tools or ToolRegistry(), max_tool_rounds=max_rounds, client=client)
    return agent, models


async def test_plain_reply_and_history_conversion():
    agent, models = make_agent([response("Canberra", tokens=12)])
    turns = [Turn("user", "câu 1", "An"), Turn("model", "đáp 1"), Turn("user", "thủ đô Úc?", "Bình")]
    reply = await agent.reply("system", turns, CTX)
    assert reply.text == "Canberra" and reply.tokens == 12
    model, contents, config = models.requests[0]
    assert model == "gemini-test"
    assert [c.role for c in contents] == ["user", "model", "user"]
    assert contents[2].parts[0].text == "Bình: thủ đô Úc?"
    assert config.system_instruction == "system"
    assert config.tools is None
    assert config.automatic_function_calling.disable is True


async def test_transient_errors_are_retried_but_others_are_not():
    import httpx

    class Flaky(FakeModels):
        def __init__(self, failures, responses):
            super().__init__(responses)
            self.failures = list(failures)

        async def generate_content(self, *, model, contents, config):
            if self.failures:
                raise self.failures.pop(0)
            return await super().generate_content(model=model, contents=contents, config=config)

    server_error = RuntimeError("503")
    server_error.code = 503
    models = Flaky([httpx.ReadError("cut"), server_error], [response("ok")])
    agent = GeminiAgent("k", "m", ToolRegistry(), client=SimpleNamespace(aio=SimpleNamespace(models=models)))
    agent.retry_delay = 0
    assert (await agent.reply("s", [Turn("user", "x")], CTX)).text == "ok"

    bad_request = RuntimeError("400")
    bad_request.code = 400
    models = Flaky([bad_request], [response("never")])
    agent = GeminiAgent("k", "m", ToolRegistry(), client=SimpleNamespace(aio=SimpleNamespace(models=models)))
    agent.retry_delay = 0
    with pytest.raises(RuntimeError):
        await agent.reply("s", [Turn("user", "x")], CTX)

    models = Flaky([httpx.ReadError("1"), httpx.ReadError("2"), httpx.ReadError("3")], [response("never")])
    agent = GeminiAgent("k", "m", ToolRegistry(), client=SimpleNamespace(aio=SimpleNamespace(models=models)))
    agent.retry_delay = 0
    with pytest.raises(httpx.ReadError):
        await agent.reply("s", [Turn("user", "x")], CTX)


async def test_reply_retries_once_on_timeout():
    import asyncio

    class Slow(FakeModels):
        async def generate_content(self, *, model, contents, config):
            if not self.requests:
                self.requests.append((model, list(contents), config))
                await asyncio.sleep(1)
            return await super().generate_content(model=model, contents=contents, config=config)

    models = Slow([response("ok")])
    agent = GeminiAgent("k", "m", ToolRegistry(), timeout_seconds=0.05,
                        client=SimpleNamespace(aio=SimpleNamespace(models=models)))
    assert (await agent.reply("s", [Turn("user", "x")], CTX)).text == "ok"
    assert len(models.requests) == 2

    class AlwaysSlow:
        async def generate_content(self, *, model, contents, config):
            await asyncio.sleep(1)

    agent = GeminiAgent("k", "m", ToolRegistry(), timeout_seconds=0.05,
                        client=SimpleNamespace(aio=SimpleNamespace(models=AlwaysSlow())))
    with pytest.raises(TimeoutError, match="không trả lời sau"):
        await agent.reply("s", [Turn("user", "x")], CTX)


@pytest.mark.parametrize("level", ["low", "medium", "high"])
async def test_reply_sends_thinking_level(level):
    agent, models = make_agent([response("ok")])
    agent.configure(model="gemini-test", max_tool_rounds=4, max_output_tokens=1024, timeout_seconds=60,
                    thinking_level=level)
    await agent.reply("s", [Turn("user", "x")], CTX)
    thinking = models.requests[0][2].thinking_config
    assert str(thinking.thinking_level.value).lower() == level


async def test_reply_drops_thinking_when_model_rejects_it():
    class Rejects(FakeModels):
        async def generate_content(self, *, model, contents, config):
            if config.thinking_config is not None:
                self.requests.append((model, list(contents), config))
                error = RuntimeError("Thinking level is not supported")
                error.code = 400
                raise error
            return await super().generate_content(model=model, contents=contents, config=config)

    models = Rejects([response("ok")])
    agent = GeminiAgent("k", "m", ToolRegistry(), client=SimpleNamespace(aio=SimpleNamespace(models=models)))
    assert (await agent.reply("s", [Turn("user", "x")], CTX)).text == "ok"
    assert len(models.requests) == 2 and models.requests[1][2].thinking_config is None
    assert agent._no_thinking == {"m"}


class PerModel(FakeModels):
    """Mỗi model một kịch bản: {model: [lỗi hoặc None, ...]}; hết danh sách thì trả lời bình thường."""

    def __init__(self, script, responses):
        super().__init__(responses)
        self.script = {k: list(v) for k, v in script.items()}
        self.tried = []

    async def generate_content(self, *, model, contents, config):
        self.tried.append(model)
        queue = self.script.get(model)
        if queue:
            err = queue.pop(0)
            if err is not None:
                raise err
        return await super().generate_content(model=model, contents=contents, config=config)


def api_error(code, text="err"):
    error = RuntimeError(f"{code} {text}")
    error.code = code
    return error


def chain_agent(models, **kwargs):
    agent = GeminiAgent("k", "main", ToolRegistry(), fallback_models=("fb1", "fb2"),
                        client=SimpleNamespace(aio=SimpleNamespace(models=models)), **kwargs)
    agent.retry_delay = 0
    return agent


async def test_overloaded_model_falls_over_to_next_after_one_retry():
    models = PerModel({"main": [api_error(503)] * 5}, [response("từ dự phòng")])
    reply = await chain_agent(models).reply("s", [Turn("user", "x")], CTX)
    assert reply.text == "từ dự phòng" and reply.model == "fb1"
    assert models.tried == ["main", "main", "fb1"]  # 1 lần thử lại cùng model rồi sang dự phòng, không chờ 2 lần như trước


async def test_quota_and_missing_models_switch_immediately_and_404_is_remembered():
    models = PerModel({"main": [api_error(429)], "fb1": [api_error(404)]}, [response("ok"), response("lần hai")])
    agent = chain_agent(models)
    reply = await agent.reply("s", [Turn("user", "x")], CTX)
    assert reply.model == "fb2" and models.tried == ["main", "fb1", "fb2"]  # 429 và 404 không thử lại
    models.tried.clear()
    await agent.reply("s", [Turn("user", "y")], CTX)
    assert models.tried == ["fb2"]  # fb1 báo 404 nên bị bỏ khỏi chuỗi; main vừa lỗi 429 nên đang nghỉ
    agent.configure(model="main", max_tool_rounds=4, max_output_tokens=1024, timeout_seconds=60)
    assert "fb1" in agent.chain()  # đổi cấu hình thì cho thử lại


async def test_last_model_keeps_the_old_retry_behaviour_and_errors_surface():
    models = PerModel({m: [api_error(503)] * 9 for m in ("main", "fb1", "fb2")}, [response("never")])
    with pytest.raises(RuntimeError, match="503"):
        await chain_agent(models).reply("s", [Turn("user", "x")], CTX)
    assert models.tried == ["main", "main", "fb1", "fb1", "fb2", "fb2", "fb2"]  # model cuối: 1 lần + 2 lần thử lại

    models = PerModel({"main": [api_error(400)]}, [response("never")])
    with pytest.raises(RuntimeError, match="400"):
        await chain_agent(models).reply("s", [Turn("user", "x")], CTX)
    assert models.tried == ["main"]  # lỗi do yêu cầu sai: không đổi model


async def test_profile_chain_order_and_tool_rounds_stay_on_answering_model():
    registry = ToolRegistry([Tool("noop", "không làm gì", lambda a, c: "ok")])
    call = SimpleNamespace(name="noop", args={})
    models = PerModel({"big": [api_error(503)] * 3}, [response(calls=[call]), response("xong")])
    agent = GeminiAgent("k", "main", registry, fallback_models=("fb1",), client=SimpleNamespace(aio=SimpleNamespace(models=models)))
    agent.retry_delay = 0
    assert agent.chain("big", ("pf",)) == ["big", "pf", "main", "fb1"]
    reply = await agent.reply("s", [Turn("user", "x")], CTX, model="big", fallbacks=("pf",))
    assert reply.text == "xong" and reply.model == "pf"
    assert models.tried == ["big", "big", "pf", "pf"]  # vòng tool thứ hai ở lại pf, không quay về big


async def test_thinking_is_remembered_per_model_and_reported():
    class Picky(PerModel):
        async def generate_content(self, *, model, contents, config):
            if model == "main" and config.thinking_config is not None:
                self.tried.append(model)
                raise api_error(400, "thinking_level is not supported")
            return await super().generate_content(model=model, contents=contents, config=config)

    models = Picky({}, [response("a"), response("b")])
    agent = chain_agent(models)
    first = await agent.reply("s", [Turn("user", "x")], CTX, thinking_level="medium")
    assert first.thinking == "" and agent._no_thinking == {"main"}  # main không nhận: gọi lại không có thinking
    await agent.reply("s", [Turn("user", "y")], CTX, model="fb1", thinking_level="high")
    assert models.requests[-1][2].thinking_config.thinking_level.value.lower() == "high"  # model khác vẫn có thinking


async def test_failed_model_rests_for_a_while_instead_of_being_retried_every_message():
    models = PerModel({"main": [api_error(503)] * 2}, [response("a"), response("b"), response("c")])
    agent = chain_agent(models)
    await agent.reply("s", [Turn("user", "x")], CTX)
    assert models.tried == ["main", "main", "fb1"]
    models.tried.clear()
    await agent.reply("s", [Turn("user", "y")], CTX)
    assert models.tried == ["fb1"]  # main đang nghỉ: khỏi chờ nó lỗi lại
    assert agent.chain() == ["fb1", "fb2", "main"]  # bị đẩy xuống cuối, không bị bỏ
    agent._cooling["main"] = 0  # hết thời gian nghỉ
    models.tried.clear()
    await agent.reply("s", [Turn("user", "z")], CTX)
    assert models.tried == ["main"] and "main" not in agent._cooling  # main chạy lại được thì hết nghỉ


async def test_classify_uses_fallback_models():
    ok = response('{"reply": true}')
    ok.text = '{"reply": true}'
    models = PerModel({"main": [api_error(503)] * 3}, [ok])
    data, _ = await chain_agent(models).classify("s", "t")
    assert data == {"reply": True} and models.tried == ["main", "main", "fb1"]


async def test_empty_reply_falls_back():
    agent, _ = make_agent([response(None)])
    assert (await agent.reply("s", [Turn("user", "x")], CTX)).text == EMPTY_REPLY


async def test_function_calling_loop():
    seen = []

    def add(args, ctx):
        seen.append((args, ctx.user_id))
        return args["a"] + args["b"]

    registry = ToolRegistry([Tool("add", "cộng hai số", add, {"type": "object", "properties": {
        "a": {"type": "number"}, "b": {"type": "number"}}})])
    call = SimpleNamespace(name="add", args={"a": 2, "b": 3})
    agent, models = make_agent([response(calls=[call], tokens=5), response("Kết quả là 5", tokens=6)], registry)
    reply = await agent.reply("s", [Turn("user", "2+3?")], CTX)
    assert reply.text == "Kết quả là 5" and reply.tokens == 11
    assert seen == [({"a": 2, "b": 3}, "u")]
    _, contents, config = models.requests[1]
    assert contents[-1].parts[0].function_response.response == {"result": 5}
    assert config.tools[0].function_declarations[0].name == "add"


async def test_tool_round_limit():
    registry = ToolRegistry([Tool("noop", "không làm gì", lambda a, c: "ok")])
    call = SimpleNamespace(name="noop", args={})
    agent, models = make_agent([response(calls=[call])] * 3, registry, max_rounds=2)
    reply = await agent.reply("s", [Turn("user", "x")], CTX)
    assert reply.text == TOO_MANY_STEPS and len(models.requests) == 3


async def test_registry_owner_only_unknown_and_errors():
    def boom(args, ctx):
        raise RuntimeError("hỏng")

    registry = ToolRegistry([
        Tool("secret", "chỉ chủ", lambda a, c: "ok", owner_only=True),
        Tool("boom", "lỗi", boom),
    ])
    assert "error" in await registry.call("secret", {}, CTX)
    owner = ToolContext("g", "o", "Chủ", is_owner=True)
    assert await registry.call("secret", {}, owner) == {"result": "ok"}
    assert "hỏng" in (await registry.call("boom", {}, CTX))["error"]
    assert "error" in await registry.call("missing", {}, CTX)
    with pytest.raises(ValueError):
        registry.register(Tool("boom", "trùng", boom))


def test_discover_skips_example_template():
    assert "current_time" not in discover().names()


def test_prompt_builder_reads_workspace_and_strips_comments(tmp_path):
    (tmp_path / "SYSTEM.md").write_text("Bạn là trợ lý thử.", encoding="utf-8")
    (tmp_path / "MEMORY.md").write_text("<!-- ghi chú -->\nAn thích cà phê.", encoding="utf-8")
    prompt = PromptBuilder(tmp_path).build(is_group=True, tool_names=[])
    assert prompt.startswith("Bạn là trợ lý thử.")
    assert "An thích cà phê." in prompt and "ghi chú" not in prompt
    assert "nhóm Zalo" in prompt


def test_prompt_builder_without_files(tmp_path):
    prompt = PromptBuilder(tmp_path).build(is_group=False, tool_names=["a"])
    assert "trợ lý" in prompt and "Ghi nhớ" not in prompt and "a" in prompt


def test_prompt_tells_model_the_sender_role(tmp_path):
    tools = ["giao_lich"]
    basic = PromptBuilder(tmp_path).build(is_group=True, tool_names=tools, sender_role="basic")
    assert "basic-user" in basic and "CHÍNH HỌ" in basic
    leader = PromptBuilder(tmp_path).build(is_group=True, tool_names=tools, sender_role="leader", team_names=["Thiết kế"])
    assert "basic-user" not in leader and "Thiết kế" in leader and "nhom" in leader
    assert "basic-user" not in PromptBuilder(tmp_path).build(is_group=True, tool_names=[], sender_role="basic")


# ---------- danh sách key -> model (lobby/office/model_calls) ----------

class KeyBook:
    """Giả ModelCalls: `owners` = {model: (nhà cung cấp, client)}; model không có trong đó dùng client chính."""

    def __init__(self, owners):
        self.owners = owners

    def provider_of(self, model):
        return self.owners[model][0] if model in self.owners else None

    def gemini_client(self, model):
        provider, client = self.owners.get(model, (None, None))
        return client if provider == "gemini" else None


def keyed_agent(owners, main_models, **kwargs):
    agent = GeminiAgent("k", "main", ToolRegistry(), model_calls=KeyBook(owners), **kwargs)
    agent._client = SimpleNamespace(aio=SimpleNamespace(models=main_models))  # client chính (không gọi mạng)
    agent.retry_delay = 0
    return agent


async def test_each_model_is_called_with_the_client_of_its_own_key():
    main, other = PerModel({}, [response("từ key chính")]), PerModel({}, [response("từ key phụ")])
    owners = {"alt": ("gemini", SimpleNamespace(aio=SimpleNamespace(models=other)))}
    agent = keyed_agent(owners, main)
    assert (await agent.reply("s", [Turn("user", "x")], CTX)).text == "từ key chính"
    reply = await agent.reply("s", [Turn("user", "x")], CTX, model="alt")
    assert reply.text == "từ key phụ" and main.tried == ["main"] and other.tried == ["alt"]


async def test_fallback_on_another_key_uses_that_keys_client():
    main, other = PerModel({"main": [api_error(429)]}, []), PerModel({}, [response("dự phòng key phụ")])
    owners = {"alt": ("gemini", SimpleNamespace(aio=SimpleNamespace(models=other)))}
    reply = await keyed_agent(owners, main, fallback_models=("alt",)).reply("s", [Turn("user", "x")], CTX)
    assert reply.text == "dự phòng key phụ" and reply.model == "alt"
    assert main.tried == ["main"] and other.tried == ["alt"]


async def test_models_of_other_providers_are_dropped_from_the_chain(caplog):
    main = PerModel({}, [response("ok")])
    owners = {"@cf/flux": ("cloudflare", object())}
    agent = keyed_agent(owners, main, fallback_models=("@cf/flux",))
    assert agent.chain() == ["main"]
    assert agent.chain("@cf/flux") == ["main"]  # hồ sơ chọn model không phải Gemini: dùng model chính
    assert "@cf/flux" in caplog.text
    assert (await agent.reply("s", [Turn("user", "x")], CTX, model="@cf/flux")).model == "main"


def test_a_client_given_directly_ignores_the_key_book():
    agent = GeminiAgent("k", "main", ToolRegistry(), client=object(), model_calls=KeyBook({"x": ("cloudflare", None)}))
    assert agent.model_calls is None and agent.chain("x") == ["x", "main"]
