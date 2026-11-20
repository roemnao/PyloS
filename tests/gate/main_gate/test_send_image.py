"""Gửi ảnh vào Zalo: đọc kích thước ảnh, acc cá nhân (sendLocalImage), chế độ Zalo Bot (chưa hỗ trợ)."""

import struct

import pytest

from conftest import make_settings
from pylos.gate.main_gate.media.image_size import image_size
from pylos.gate.main_gate.zalo import ZaloClient, ZaloError, ZaloUnsupported
from pylos.lobby.dispatch.shared.storage import ActivityStore
from test_personal import FakeApi, ThreadType, make_personal


def png(width, height):
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x08\x02\x00\x00\x00"


def jpeg(width, height):
    app0 = b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    sof = b"\xff\xc0" + struct.pack(">HBHHB", 11, 8, height, width, 1) + b"\x01\x11\x00"
    return b"\xff\xd8" + app0 + sof + b"\xff\xd9"


def test_image_size_reads_png_and_jpeg_headers():
    assert image_size(png(640, 480)) == (640, 480)
    assert image_size(jpeg(1024, 768)) == (1024, 768)
    assert image_size(b"not an image") is None and image_size(b"") is None
    assert image_size(png(0, 5)) is None


class ImageApi(FakeApi):
    def __init__(self, result=None, error=None):
        super().__init__(result)
        self.images, self.error = [], error

    def sendLocalImage(self, path, thread_id, thread_type, width=2560, height=2560, message=None, **kw):  # noqa: N802
        if self.error:
            raise self.error
        self.images.append((path, thread_id, thread_type, width, height, getattr(message, "text", None)))
        return self.result


async def test_personal_send_image_uses_real_size_caption_and_chat_type(tmp_path):
    api = ImageApi()
    zalo = make_personal(tmp_path, api)
    ActivityStore(zalo.settings.data_dir / "chat_activity.txt").touch("g1", "GROUP", "An")
    picture = tmp_path / "gen.png"
    picture.write_bytes(png(1024, 768) + b"0" * 100)
    await zalo.send_image("g1", picture, "Mèo nè")
    await zalo.send_image("u9", picture)
    assert api.images == [(str(picture), "g1", ThreadType.GROUP, 1024, 768, "Mèo nè"),
                          (str(picture), "u9", ThreadType.USER, 1024, 768, None)]


async def test_personal_send_image_unknown_format_and_errors(tmp_path):
    api = ImageApi()
    zalo = make_personal(tmp_path, api)
    odd = tmp_path / "odd.bin"
    odd.write_bytes(b"???")
    await zalo.send_image("u1", odd)
    assert api.images[0][3:5] == (1024, 1024)  # không đọc được kích thước: dùng mặc định

    with pytest.raises(ZaloError, match="Gửi ảnh Zalo cá nhân lỗi") as network:
        await make_personal(tmp_path, ImageApi(error=RuntimeError("boom"))).send_image("u1", odd)
    assert network.value.network
    with pytest.raises(ZaloError):
        await make_personal(tmp_path, ImageApi(result={"error_code": 114, "error_message": "blocked"})).send_image("u1", odd)


async def test_zalo_bot_mode_says_images_are_unsupported():
    with pytest.raises(ZaloUnsupported, match="Zalo Bot"):
        await ZaloClient("token").send_image("u1", "x.png")
    assert issubclass(ZaloUnsupported, ZaloError)
