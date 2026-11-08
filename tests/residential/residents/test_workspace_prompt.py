"""PromptBuilder: quy tắc chung ở hàng rào, mọi tài liệu trong workspace của bot, MEMORY.md là dữ liệu."""

from pylos.residential.residents.pylos import PromptBuilder


def build(workspace, system):
    return PromptBuilder(workspace, system).build(is_group=False, tool_names=[])


def test_prompt_reads_every_document_in_the_workspace(tmp_path):
    ws, system = tmp_path / "workspace", tmp_path / "fence" / "SYSTEM.md"
    (ws / "persona").mkdir(parents=True)
    (ws / ".backup").mkdir()
    system.parent.mkdir()
    system.write_text("QUY TẮC CHUNG", encoding="utf-8")
    (ws / "SOUL.md").write_text("<!-- ghi chú -->\nTôi là Lila", encoding="utf-8")
    (ws / "persona" / "giong.txt").write_text("nói ngắn", encoding="utf-8")
    (ws / "MEMORY.md").write_text("nhớ: mèo tên Mun", encoding="utf-8")
    (ws / ".backup" / "SOUL-old.md").write_text("BẢN CŨ KHÔNG ĐƯA VÀO", encoding="utf-8")
    (ws / "anh.png").write_bytes(b"\x89PNG")
    prompt = build(ws, system)
    assert prompt.startswith("QUY TẮC CHUNG")
    assert "## SOUL.md\nTôi là Lila" in prompt and "ghi chú" not in prompt
    assert "## persona/giong.txt\nnói ngắn" in prompt
    assert "BẢN CŨ" not in prompt and "PNG" not in prompt
    assert prompt.index("Tôi là Lila") < prompt.index("## Bối cảnh") < prompt.index("mèo tên Mun")
    assert "DỮ LIỆU tham khảo" in prompt  # MEMORY.md vẫn là dữ liệu, không phải chỉ thị


def test_prompt_picks_up_a_new_file_and_falls_back_without_system(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    builder = PromptBuilder(ws, tmp_path / "khong_co" / "SYSTEM.md")
    assert "trợ lý hữu ích" in builder.build(is_group=False, tool_names=[])  # chưa có SYSTEM.md: câu mặc định
    (ws / "SOUL.md").write_text("Tôi là Lila", encoding="utf-8")
    assert "Tôi là Lila" in builder.build(is_group=False, tool_names=[])


def test_workspace_without_a_system_file_argument_still_reads_its_own_system_md(tmp_path):
    ws = tmp_path / "workspace"
    ws.mkdir()
    (ws / "SYSTEM.md").write_text("luật cũ", encoding="utf-8")
    prompt = PromptBuilder(ws).build(is_group=False, tool_names=[])
    assert prompt.startswith("luật cũ") and prompt.count("luật cũ") == 1  # không bị đưa hai lần


def test_tracked_system_rules_match_the_template_used_to_seed_new_installs():
    from pathlib import Path

    root = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file())
    tracked = (root / "src" / "pylos" / "gate" / "fence" / "SYSTEM.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    template = (root / "src" / "pylos" / "lobby" / "dispatch" / "shared" / "templates" / "SYSTEM.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert tracked == template  # sửa một nơi thì sửa cả hai
