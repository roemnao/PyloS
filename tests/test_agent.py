from __future__ import annotations

from types import SimpleNamespace

import pytest

from bot.agent import GeminiAgent, PromptBuilder, Tool, ToolContext, ToolRegistry, Turn, discover
from bot.agent.gemini_agent import EMPTY_REPLY, TOO_MANY_STEPS

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
