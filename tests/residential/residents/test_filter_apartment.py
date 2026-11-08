"""Căn hộ của bot lọc (residential/residents/filter): chỉ dẫn lấy từ workspace/."""

from __future__ import annotations

from conftest import FakeAgent, make_settings

from pylos.gate.fence.speech_limit.message_filter import FILTER_SYSTEM, MessageFilter
from pylos.gate.main_gate.zalo.personal_account import to_incoming
from pylos.lobby.dispatch.clock.vietnam_time import now_ms
from pylos.lobby.dispatch.shared.config import PROJECT_ROOT
from pylos.residential.residents.filter.instructions import FilterInstructions


def test_reads_every_doc_skips_hidden_and_comments(tmp_path):
    ws = tmp_path / "workspace"
    (ws / ".backup").mkdir(parents=True)
    (ws / ".backup" / "old.md").write_text("CŨ", encoding="utf-8")
    (ws / "a.md").write_text("<!-- ghi chú -->\nMột {names}", encoding="utf-8")
    (ws / "b.txt").write_text("Hai", encoding="utf-8")
    (ws / "x.json").write_text("{}", encoding="utf-8")
    text = FilterInstructions(ws).text("Bot")
    assert "Một Bot" in text and "Hai" in text and "CŨ" not in text and "ghi chú" not in text and "{}" not in text


def test_single_doc_is_used_as_is_and_missing_workspace_is_empty(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "SOUL.md").write_text('Tên "{names}" {"reply": true}', encoding="utf-8")
    assert FilterInstructions(ws).text("Bot") == 'Tên "Bot" {"reply": true}'
    assert FilterInstructions(tmp_path / "none").text("Bot") == ""


def test_reloads_when_file_changes(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    f = ws / "SOUL.md"
    f.write_text("v1", encoding="utf-8")
    inst = FilterInstructions(ws)
    assert inst.text("") == "v1"
    f.write_text("v2 dài hơn", encoding="utf-8")
    import os
    os.utime(f, (f.stat().st_mtime + 5, f.stat().st_mtime + 5))
    assert inst.text("") == "v2 dài hơn"


def msg(text):
    return to_incoming(f"m{now_ms()}", "u1", text, {"dName": "An", "ts": str(now_ms())}, "g1", True, "me-1")


class CapturingAgent(FakeAgent):
    systems: list[str]

    async def classify(self, system, text, **kwargs):
        self.systems = [*getattr(self, "systems", []), system]
        return await super().classify(system, text, **kwargs)


async def ask(filter_):
    return await filter_.decide(msg("hôm nay ăn gì mọi người"), mode="all", over_budget=False, recent=[])


async def test_filter_uses_apartment_instructions_else_default(tmp_path):
    agent = CapturingAgent()
    settings = make_settings(tmp_path, FILTER_AI="true")
    custom = MessageFilter(settings, agent, lambda: ("", "Bot"), lambda names: f"RIÊNG {names}")
    await ask(custom)
    assert agent.systems == ["RIÊNG bot, Bot"]
    for instructions in (None, lambda names: ""):  # chưa có căn hộ / workspace trống -> chỉ dẫn mặc định trong code
        agent.systems = []
        await ask(MessageFilter(settings, agent, lambda: ("", "Bot"), instructions))
        assert agent.systems == [FILTER_SYSTEM.format(names="bot, Bot")]


def test_shipped_soul_matches_default_prompt():
    soul = FilterInstructions(PROJECT_ROOT / "src/pylos/residential/residents/filter/workspace").text("bot")
    assert soul == FILTER_SYSTEM.format(names="bot")  # file mẫu giữ đúng chỉ dẫn mặc định
