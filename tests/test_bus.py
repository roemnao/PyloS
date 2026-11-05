"""Bus trong process (bước 4.2): giao tin, cô lập lỗi, log chỉ có siêu dữ liệu, độ trễ nhỏ (B3 < 1 giây)."""

import json
import time

from pylos.lobby.dispatch.bus.bus import InProcessBus
from pylos.lobby.dispatch.bus.envelope import Envelope
from pylos.lobby.dispatch.envelope_log.envelope_log import EnvelopeLog


async def test_delivers_to_sync_and_async_handlers():
    bus, got = InProcessBus(), []

    async def a(env): got.append(("a", env.payload))

    bus.subscribe("bot", lambda env: got.append(("b", env.payload)))
    bus.subscribe("bot", a)
    assert await bus.publish(Envelope("zalo", "bot", "chat.incoming", "xin chào")) == 2
    assert sorted(got) == [("a", "xin chào"), ("b", "xin chào")]


async def test_failing_handler_does_not_block_others():
    bus, got = InProcessBus(), []

    def boom(env): raise RuntimeError("lỗi")

    bus.subscribe("bot", boom)
    bus.subscribe("bot", lambda env: got.append(env.id))
    env = Envelope("zalo", "bot", "chat.incoming")
    assert await bus.publish(env) == 1
    assert got == [env.id]


async def test_log_has_metadata_but_never_the_payload(tmp_path):
    path = tmp_path / "envelopes.jsonl"
    bus = InProcessBus(EnvelopeLog(path))
    bus.subscribe("bot", lambda env: None)
    await bus.publish(Envelope("zalo", "bot", "chat.incoming", "BÍ MẬT"))
    await bus.publish(Envelope("zalo", "nobody", "chat.incoming", "BÍ MẬT"))
    text = path.read_text(encoding="utf-8")
    assert "BÍ MẬT" not in text
    rows = [json.loads(line) for line in text.splitlines()]
    assert [r["outcome"] for r in rows] == ["delivered", "no_recipient"]
    assert rows[0]["sender"] == "zalo" and rows[0]["kind"] == "chat.incoming"


async def test_overhead_per_message_is_far_below_one_second():
    bus = InProcessBus()
    bus.subscribe("bot", lambda env: None)
    start = time.perf_counter()
    for _ in range(200):
        await bus.publish(Envelope("zalo", "bot", "chat.incoming"))
    assert (time.perf_counter() - start) / 200 < 0.01
