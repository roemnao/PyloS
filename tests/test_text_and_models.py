from __future__ import annotations

from bot.commands import parse_command
from bot.text import split_message, to_plain_text, utf16_len
from bot.zalo import parse_updates


def test_split_short_message_unchanged():
    assert split_message("  xin chào  ") == ["xin chào"]
    assert split_message("") == []


def test_split_prefers_paragraph_boundaries():
    text = "A" * 1500 + "\n\n" + "B" * 1500
    assert split_message(text) == ["A" * 1500, "B" * 1500]


def test_split_counts_emoji_as_two_units():
    text = "😀" * 1500  # 3000 UTF-16 units, không có khoảng trắng
    chunks = split_message(text)
    assert all(utf16_len(c) <= 2000 for c in chunks)
    assert "".join(chunks) == text


def test_split_without_spaces_hard_cuts():
    text = "x" * 4500
    chunks = split_message(text)
    assert [len(c) for c in chunks] == [2000, 2000, 500]


def test_to_plain_text():
    assert to_plain_text("# A\n**b** __c__\n* d\n  - e") == "A\nb c\n• d\n  • e"


def test_parse_command():
    assert parse_command("/mode all").name == "mode"
    assert parse_command("/mode ALL").arg == "all"
    assert parse_command("/MODE@bot default").arg == "default"
    assert parse_command("/bot hello") is None
    assert parse_command("hello /mode") is None
    assert parse_command(None) is None


def test_parse_updates_docs_sample():
    payload = {
        "ok": True,
        "result": {
            "event_name": "message.text.received",
            "message": {
                "from": {"id": "6ede9afa66b88fe6d6a9", "display_name": "Ted", "is_bot": False},
                "chat": {"id": "6ede9afa66b88fe6d6a9", "chat_type": "PRIVATE"},
                "text": "Xin chào",
                "message_id": "2d758cb5e222177a4e35",
                "date": 1750316131602,
            },
        },
    }
    [msg] = parse_updates(payload)
    assert msg.chat_id == "6ede9afa66b88fe6d6a9" and not msg.is_group
    assert msg.is_text and msg.text == "Xin chào"
    assert msg.date_ms == 1750316131602
    assert msg.dedupe_key == "6ede9afa66b88fe6d6a9:2d758cb5e222177a4e35"


def test_dedupe_key_without_message_id_is_stable():
    raw = {"event_name": "message.text.received", "message": {
        "from": {"id": "u"}, "chat": {"id": "c", "chat_type": "GROUP"}, "text": "hi", "date": 1}}
    a, b = parse_updates(raw)[0], parse_updates(dict(raw))[0]
    assert a.message_id is None and a.dedupe_key == b.dedupe_key
