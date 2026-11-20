"""Tài liệu .docx / .md: lõi đọc-ghi-sửa và bốn tool của bot."""

from __future__ import annotations

import os
import time

import pytest
from conftest import make_settings
from docx import Document

from pylos.lobby.dispatch.shared.data_stores import DailyCounter
from pylos.lobby.office.agent_tools import OutgoingFile, ToolContext, ToolRegistry, documents
from pylos.lobby.office.documents import editor, files, reader, writer
from pylos.lobby.office.documents.files import DocError

MD = (
    "# Báo cáo\n\nĐoạn **đậm** và *nghiêng*.\n\n- một\n- hai\n  - con\n\n"
    "| Tên | Số |\n|---|---|\n| A | 1 |\n| B | 2 |\n\n> trích dẫn\n"
)


# ---------- files ----------

def test_resolve_blocks_traversal_and_bad_extensions(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    assert files.resolve(folder, "../../etc/passwd.md") == (folder / "passwd.md").resolve()
    assert files.resolve(folder, "a\\b\\c.docx").parent == folder.resolve()
    assert files.resolve(folder, "Báo cáo: Q4?.DOCX").name == "Báo cáo_ Q4_.docx"
    for bad in ("x.exe", "x", ".md", "   .txt", ""):
        with pytest.raises(DocError):
            files.resolve(folder, bad)


def test_unique_path_and_existing(tmp_path):
    (tmp_path / "a.md").write_text("x")
    assert files.unique_path(tmp_path, "a.md").name == "a-2.md"
    assert files.existing(tmp_path, "a.md").name == "a.md"
    with pytest.raises(DocError):
        files.existing(tmp_path, "nope.md")


def test_prune_removes_only_old_files(tmp_path):
    old, new = tmp_path / "old.md", tmp_path / "new.md"
    old.write_text("x")
    new.write_text("x")
    os.utime(old, (time.time() - 40 * 86400,) * 2)
    assert files.prune(tmp_path, 30) == 1
    assert not old.exists() and new.exists()
    assert files.prune(tmp_path, 0) == 0


# ---------- reader / writer / editor ----------

def test_markdown_round_trips_through_docx(tmp_path):
    path = tmp_path / "a.docx"
    writer.markdown_to_docx(MD, path)
    text = reader.read_text(path)
    assert "# Báo cáo" in text
    assert "**đậm**" in text and "*nghiêng*" in text
    assert "- một" in text and "  - con" in text
    assert "| Tên | Số |" in text and "| B | 2 |" in text
    assert "> trích dẫn" in text


def test_replace_text_keeps_formatting_and_handles_split_runs(tmp_path):
    path = tmp_path / "a.docx"
    doc = Document()
    par = doc.add_paragraph()
    par.add_run("Xin chào A").bold = True
    par.add_run("n, hôm nay trời đẹp. An")
    cell = doc.add_table(rows=1, cols=1).cell(0, 0)
    cell.paragraphs[0].add_run("Gửi An")
    doc.save(str(path))

    assert editor.replace_text(path, "An", "Bình") == 3  # "An" đầu bị cắt giữa hai run
    saved = Document(str(path))
    assert saved.paragraphs[0].text == "Xin chào Bình, hôm nay trời đẹp. Bình"
    assert saved.paragraphs[0].runs[0].bold and saved.paragraphs[0].runs[0].text == "Xin chào Bình"
    assert saved.tables[0].cell(0, 0).text == "Gửi Bình"
    assert editor.replace_text(path, "không có chữ này", "x") == 0

    assert editor.replace_text(path, "Bình, hôm", "Lan, hôm") == 1  # cắt giữa run đậm và run thường
    assert Document(str(path)).paragraphs[0].text == "Xin chào Lan, hôm nay trời đẹp. Bình"


def test_append_and_overwrite_keep_a_backup(tmp_path):
    path = tmp_path / "a.docx"
    writer.markdown_to_docx("# Một", path)
    editor.append_markdown(path, "Thêm đoạn")
    assert "Thêm đoạn" in reader.read_text(path)
    editor.overwrite_markdown(path, "# Hai")
    assert reader.read_text(path).strip() == "# Hai"
    editor.restore(path)
    assert "Thêm đoạn" in reader.read_text(path)  # bản trước lần ghi đè


def test_markdown_files_edit_in_place(tmp_path):
    path = tmp_path / "n.md"
    path.write_text("# Việc\n- a\n", encoding="utf-8")
    assert editor.replace_text(path, "- a", "- b") == 1
    editor.append_markdown(path, "- c")
    assert path.read_text(encoding="utf-8") == "# Việc\n- b\n\n- c\n"
    assert (tmp_path / "n.md.bak").read_text(encoding="utf-8") == "# Việc\n- b\n"


def test_read_slice_pages_long_text(tmp_path):
    path = tmp_path / "long.txt"
    path.write_text("x" * 30, encoding="utf-8")
    first = reader.read_slice(path, 0, 12)
    assert first["noi_dung"] == "x" * 12 and first["con_lai"] == 18 and first["doc_tiep_tu_vi_tri"] == 12
    last = reader.read_slice(path, 12, 100)
    assert "con_lai" not in last


def test_broken_docx_gives_a_readable_error(tmp_path):
    path = tmp_path / "bad.docx"
    path.write_bytes(b"not a zip")
    with pytest.raises(DocError):
        reader.read_text(path)


# ---------- tools ----------

@pytest.fixture
def tool(tmp_path):
    saved = (documents.CONFIG.enabled, documents.CONFIG.keep_days, documents.CONFIG.limit, documents.CONFIG.limit_path)

    def setup(**overrides):
        settings = make_settings(tmp_path, **overrides)
        documents.configure(settings)
        return settings, ToolRegistry(documents.TOOLS)

    yield setup
    (documents.CONFIG.enabled, documents.CONFIG.keep_days, documents.CONFIG.limit, documents.CONFIG.limit_path) = saved


def ctx_for(tmp_path, chat="chat-1", user="user-1"):
    return ToolContext(chat, user, "An", is_owner=False, huts_dir=tmp_path / "huts")


async def test_tools_hidden_when_off(tool):
    _, registry = tool(DOC_TOOLS="false")
    assert registry.names() == []
    _, registry = tool()
    assert registry.names() == ["ds_tai_lieu", "doc_tai_lieu", "tao_tai_lieu", "sua_tai_lieu"]


async def test_create_read_edit_flow_queues_files_and_counts_limit(tmp_path, tool):
    settings, registry = tool()
    ctx = ctx_for(tmp_path)
    made = await registry.call("tao_tai_lieu", {"ten": "bao-cao", "noi_dung": MD, "chu_thich": "Của bạn"}, ctx)
    assert made["ok"] and made["ten"] == "bao-cao.docx"
    (queued,) = ctx.outbox
    assert isinstance(queued, OutgoingFile) and queued.caption == "Của bạn"
    assert queued.path == tmp_path / "huts" / "chat-1" / "docs" / "bao-cao.docx"

    assert (await registry.call("ds_tai_lieu", {}, ctx))["tai_lieu"][0]["ten"] == "bao-cao.docx"
    read = await registry.call("doc_tai_lieu", {"ten": "bao-cao.docx"}, ctx)
    assert "# Báo cáo" in read["noi_dung"]

    edited = await registry.call("sua_tai_lieu", {"ten": "bao-cao.docx", "thao_tac": "thay_the", "tim": "Báo cáo", "thay": "Tổng kết"}, ctx)
    assert edited["ok"] and edited["so_cho_da_thay"] == 1 and len(ctx.outbox) == 2
    assert "# Tổng kết" in (await registry.call("doc_tai_lieu", {"ten": "bao-cao.docx"}, ctx))["noi_dung"]
    assert DailyCounter(settings.data_dir / "doc_usage.txt").today() == 2  # đọc không tính

    await registry.call("sua_tai_lieu", {"ten": "bao-cao.docx", "thao_tac": "hoan_tac", "gui_lai": False}, ctx)
    assert "# Báo cáo" in (await registry.call("doc_tai_lieu", {"ten": "bao-cao.docx"}, ctx))["noi_dung"]
    assert len(ctx.outbox) == 2 and DailyCounter(settings.data_dir / "doc_usage.txt").today() == 2


async def test_create_never_overwrites_and_supports_markdown(tmp_path, tool):
    _, registry = tool()
    ctx = ctx_for(tmp_path)
    first = await registry.call("tao_tai_lieu", {"ten": "ghi-chu", "dinh_dang": "md", "noi_dung": "# a"}, ctx)
    second = await registry.call("tao_tai_lieu", {"ten": "ghi-chu.md", "noi_dung": "# b"}, ctx)
    assert first["ten"] == "ghi-chu.md" and second["ten"] == "ghi-chu-2.md"
    assert (tmp_path / "huts" / "chat-1" / "docs" / "ghi-chu.md").read_text(encoding="utf-8") == "# a"


async def test_chats_are_isolated_and_names_cannot_escape(tmp_path, tool):
    _, registry = tool()
    a, b = ctx_for(tmp_path, "chat-a"), ctx_for(tmp_path, "chat-b")
    await registry.call("tao_tai_lieu", {"ten": "rieng", "noi_dung": "bí mật"}, a)
    assert "error" in await registry.call("doc_tai_lieu", {"ten": "rieng.docx"}, b)
    assert (await registry.call("ds_tai_lieu", {}, b))["tai_lieu"] == []
    secret = tmp_path / "secret.md"
    secret.write_text("x")
    assert "error" in await registry.call("doc_tai_lieu", {"ten": "../../../secret.md"}, a)
    assert "error" in await registry.call("doc_tai_lieu", {"ten": "x.py"}, a)


async def test_limits_and_errors_do_not_queue_or_count(tmp_path, tool):
    settings, registry = tool(USER_DOCS_PER_HOUR="1")
    ctx = ctx_for(tmp_path)
    assert "error" in await registry.call("tao_tai_lieu", {"ten": "x", "noi_dung": "   "}, ctx)
    assert "error" in await registry.call("sua_tai_lieu", {"ten": "khong-co.docx", "thao_tac": "ghi_de", "noi_dung": "x"}, ctx)
    assert not ctx.outbox and DailyCounter(settings.data_dir / "doc_usage.txt").today() == 0

    assert (await registry.call("tao_tai_lieu", {"ten": "x", "noi_dung": "a"}, ctx))["ok"]
    refused = await registry.call("tao_tai_lieu", {"ten": "y", "noi_dung": "b"}, ctx)
    assert "1 giờ" in refused["error"] and len(ctx.outbox) == 1

    missing = await registry.call("sua_tai_lieu", {"ten": "x.docx", "thao_tac": "thay_the", "tim": "không có", "thay": ""}, ctx_for(tmp_path, user="user-2"))
    assert "Không thấy" in missing["error"]
