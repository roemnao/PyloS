"""Nhận tin bằng getUpdates (long polling): không cần domain hay HTTPS.

Docs Zalo: getUpdates và webhook loại trừ nhau, phải deleteWebhook trước.
Vòng lặp không bao giờ thoát vì lỗi mạng/API; lỗi thì chờ tăng dần rồi thử lại.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

from bot.storage import StateStore
from bot.core.vietnam_time import now_ms
from bot.zalo import ZaloClient, ZaloError

log = logging.getLogger(__name__)

MAX_BACKOFF = 60.0


async def run_polling(
    client: ZaloClient,
    handle: Callable[[Any], Awaitable[None]],
    state: StateStore,
    stop: asyncio.Event,
    poll_timeout: int = 30,
) -> None:
    try:
        await client.delete_webhook()
        log.info("Đã gỡ webhook (nếu có) để dùng getUpdates")
    except ZaloError as exc:
        # Zalo trả 400 khi chưa đăng ký webhook nào: bình thường, không cần cảnh báo.
        log.log(logging.INFO if exc.error_code == 400 else logging.WARNING, "deleteWebhook: %s (vẫn dùng polling)", exc)

    backoff = 1.0
    last_error = ""
    network_errors = 0
    log.info("Bắt đầu nhận tin bằng getUpdates")
    while not stop.is_set():
        try:
            result = await client.get_updates(timeout=poll_timeout)
        except ZaloError as exc:
            if not exc.network and exc.error_code == 408:
                # Hết thời gian chờ mà không có tin: bình thường với long polling.
                state.update(last_poll_at=now_ms())
                backoff = 1.0
                continue
            if exc.network:
                # Long polling thỉnh thoảng bị ngắt/quá giờ đọc: thử lại ngay, chỉ cảnh báo khi lặp lại nhiều lần.
                network_errors += 1
                if network_errors < 3:
                    log.info("getUpdates bị ngắt (%s), thử lại", exc)
                    await _sleep_or_stop(stop, 1)
                    continue
            message = str(exc)
            # Cùng một lỗi lặp lại thì không spam log ở mức WARNING.
            log.log(logging.DEBUG if message == last_error else logging.WARNING, "getUpdates lỗi: %s", message)
            last_error = message
            await _sleep_or_stop(stop, backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)
            continue
        except Exception:
            log.exception("Lỗi không mong đợi khi poll")
            await _sleep_or_stop(stop, backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)
            continue

        if last_error:
            log.info("getUpdates hoạt động lại")
        backoff, last_error, network_errors = 1.0, "", 0
        state.update(last_poll_at=now_ms())
        if result:
            await handle(result)


async def _sleep_or_stop(stop: asyncio.Event, seconds: float) -> None:
    try:
        await asyncio.wait_for(stop.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        pass
