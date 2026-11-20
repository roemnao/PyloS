"""to_incoming: giữ lại tệp đính kèm của tin ảnh/video/tin thoại, đổi thẻ link thành tin chữ."""

import json

from pylos.gate.main_gate.zalo.personal_account import to_incoming


def make(msg_type, content, **extra):
    obj = {"msgType": msg_type, "dName": "An", "ts": "1700000000000", **extra}
    return to_incoming("m1", "u1", content, obj, "t1", False, "bot")


def test_text_unchanged():
    msg = to_incoming("m1", "u1", "xin chào", {"msgType": "webchat"}, "t1", False, "bot")
    assert msg.kind == "text" and msg.is_text and msg.attachments == () and not msg.has_media


def test_photo_keeps_url_and_caption():
    content = {"href": "https://cdn.zalo/a.jpg", "thumb": "https://cdn.zalo/t.jpg", "title": "ảnh mèo",
               "params": json.dumps({"fileSize": "1234"})}
    msg = make("chat.photo", content)
    assert msg.kind == "photo" and msg.has_media and not msg.is_text
    assert msg.text == "ảnh mèo"
    att = msg.attachments[0]
    assert att.url == "https://cdn.zalo/a.jpg" and att.size == 1234


def test_voice_and_video():
    voice = make("chat.voice", {"href": "https://cdn.zalo/v.aac", "params": {"duration": 4000}})
    assert voice.kind == "voice" and voice.has_media and voice.text is None
    assert voice.attachments[0].duration == 4000
    assert make("chat.video.msg", {"href": "https://cdn.zalo/v.mp4"}).kind == "video"


def test_media_without_url_is_not_media():
    assert not make("chat.photo", {"thumb": "x"}).has_media


def test_link_card_becomes_text():
    msg = make("chat.recommended", {"href": "https://news.example/x", "title": "Tin", "description": "Mô tả"})
    assert msg.kind == "text" and msg.is_text and msg.attachments == ()
    assert msg.text.splitlines() == ["https://news.example/x", "Tin", "Mô tả"]


def test_sticker_file_and_unknown_are_not_media():
    assert make("chat.sticker", {"id": 1}).kind == "sticker"
    assert make("share.file", {"href": "https://x/f.pdf"}).kind == "file"
    assert make("chat.weird", {"href": "https://x"}).kind == "other"
    assert not make("chat.sticker", {"id": 1}).has_media
