import pytest

from pylos.gate.main_gate.zalo.reply_formatting import SPLIT_MODES, split_reply, utf16_len
from pylos.lobby.dispatch.shared.config import ConfigError, Settings


def test_line_paragraph_off():
    text = "A\nB\n\nC"
    assert split_reply(text, "line") == ["A", "B", "C"]
    assert split_reply(text, "paragraph") == ["A\nB", "C"]
    assert split_reply(text, "off") == ["A\nB\n\nC"]


def test_no_empty_parts_and_empty_text():
    assert split_reply("  \n\n  x  \n\n\n  y \n") == ["x", "y"]
    assert split_reply("") == []


def test_more_lines_than_max_parts_are_merged_in_order():
    lines = [str(i) for i in range(10)]
    parts = split_reply("\n".join(lines), "line", max_parts=4)
    assert len(parts) == 4
    assert "\n".join(parts).split("\n") == lines


def test_code_block_and_list_stay_together():
    text = "Xin chào\n```\nx = 1\n\ny = 2\n```\nDanh sách:\n• a\n• b\n1. c\nHết"
    assert split_reply(text) == ["Xin chào", "```\nx = 1\n\ny = 2\n```", "Danh sách:\n• a\n• b\n1. c", "Hết"]


def test_long_line_still_respects_limit():
    parts = split_reply("😀" * 1500 + "\nngắn")
    assert len(parts) == 3 and parts[-1] == "ngắn"
    assert all(utf16_len(p) <= 2000 for p in parts)


def test_config_modes_match_gate_modes(tmp_path):
    for mode in SPLIT_MODES:
        assert Settings.from_env({"REPLY_SPLIT": mode}, base_dir=tmp_path).reply_split == mode
    with pytest.raises(ConfigError):
        Settings.from_env({"REPLY_SPLIT": "xyz"}, base_dir=tmp_path)
    with pytest.raises(ConfigError):
        Settings.from_env({"REPLY_MAX_PARTS": "0"}, base_dir=tmp_path)
    s = Settings.from_env({}, base_dir=tmp_path)
    assert (s.reply_split, s.reply_max_parts, s.reply_part_delay_ms) == ("line", 6, 700)
