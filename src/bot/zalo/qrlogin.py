"""Đăng nhập acc Zalo cá nhân bằng mã QR, giống trang chat.zalo.me.

Luồng (theo zca-js, src/apis/loginQR.ts):
  1. Mở trang id.zalo.me để lấy phiên bản trang đăng nhập (v).
  2. logininfo, verify-client, rồi qr/generate trả về mã QR (ảnh PNG base64).
  3. qr/waiting-scan chờ điện thoại quét; qr/waiting-confirm chờ bấm "Đăng nhập" trên điện thoại.
     Hai lệnh chờ trả error_code 8 khi hết lượt chờ: gọi lại. waiting-confirm trả -13 khi bị từ chối.
  4. checksession theo các chuyển hướng để nhận cookies của chat.zalo.me, rồi jr/userinfo kiểm tra.

IMEI không lấy từ Zalo: tự tạo như Zalo Web (uuid4 + "-" + md5(User-Agent)) và dùng mãi với cookies này.
Tất cả chạy đồng bộ (requests); gọi từ luồng riêng.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import requests

from bot.storage import atomic_write_text
from bot.core.timeutil import now_ms

log = logging.getLogger(__name__)

# Trùng User-Agent mặc định của zlapi: mọi yêu cầu sau khi đăng nhập đều đi với UA này, nên IMEI phải khớp nó.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
QR_LIFETIME_SECONDS = 100
REQUEST_TIMEOUT = 60

_LOGIN_PAGE = "https://id.zalo.me/account?continue=https%3A%2F%2Fchat.zalo.me%2F"
_REFERER_PC = "https://id.zalo.me/account?continue=https%3A%2F%2Fzalo.me%2Fpc"
_VERSION = re.compile(r"https://stc-zlogin\.zdn\.vn/main-([\d.]+)\.js")

# Trạng thái hiển thị trên giao diện / dòng lệnh
STARTING, WAITING_SCAN, SCANNED, SUCCESS, EXPIRED, DECLINED, CANCELLED, ERROR = (
    "starting", "waiting_scan", "scanned", "success", "expired", "declined", "cancelled", "error",
)
FINISHED = (SUCCESS, EXPIRED, DECLINED, CANCELLED, ERROR)


class QrLoginError(Exception):
    pass


class Cancelled(QrLoginError):
    pass


@dataclass
class ZaloSession:
    cookies: dict[str, str]
    imei: str
    user_agent: str = USER_AGENT
    display_name: str = ""
    user_id: str = ""

    def save(self, path: Path) -> None:
        payload = {
            "imei": self.imei, "user_agent": self.user_agent, "display_name": self.display_name,
            "user_id": self.user_id, "saved_at": now_ms(), "cookies": self.cookies,
        }
        atomic_write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))
        try:
            os.chmod(path, 0o600)  # cookies = chìa khoá đăng nhập acc
        except OSError:
            pass


@dataclass
class QrStatus:
    state: str = STARTING
    image: str = ""  # PNG base64 (không có tiền tố data:)
    display_name: str = ""
    message: str = ""
    updated_at: int = field(default_factory=now_ms)


def make_imei(user_agent: str = USER_AGENT) -> str:
    return f"{uuid.uuid4()}-{hashlib.md5(user_agent.encode()).hexdigest()}"


def cookies_for(jar: requests.cookies.RequestsCookieJar, host: str = "wpa.chat.zalo.me") -> dict[str, str]:
    """Cookies trình duyệt sẽ gửi tới `host` (zlapi chỉ nhận dict phẳng, không có domain).

    Bỏ cookies của id.zalo.me; trùng tên thì lấy cookie của domain cụ thể hơn.
    """
    chosen: dict[str, tuple[int, str]] = {}
    for cookie in jar:
        domain = (cookie.domain or "").lstrip(".")
        if not domain or not (host == domain or host.endswith("." + domain)):
            continue
        if cookie.value is None:
            continue
        rank = len(domain)
        if cookie.name not in chosen or rank >= chosen[cookie.name][0]:
            chosen[cookie.name] = (rank, cookie.value)
    return {name: value for name, (_, value) in chosen.items()}


class QrLogin:
    """Một lần đăng nhập bằng QR. `run()` chặn tới khi xong; `cancel()` gọi được từ luồng khác."""

    def __init__(self, on_update: Callable[[QrStatus], None] | None = None,
                 session: requests.Session | None = None) -> None:
        self.status = QrStatus()
        self._on_update = on_update
        self._cancel = threading.Event()
        self._http = session or requests.Session()
        self._http.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.6,en;q=0.5",
            "Origin": "https://chat.zalo.me",
            "Referer": "https://chat.zalo.me/",
        })

    def cancel(self) -> None:
        self._cancel.set()

    def report(self, state: str, message: str = "", **extra: Any) -> None:
        self.status = QrStatus(state=state, message=message, image=extra.get("image", ""),
                               display_name=extra.get("display_name", self.status.display_name))
        if self._on_update:
            try:
                self._on_update(self.status)
            except Exception:  # noqa: BLE001 - lỗi hiển thị không được làm hỏng đăng nhập
                log.exception("Lỗi khi báo trạng thái QR")

    # ---------- HTTP ----------

    def _check_cancel(self) -> None:
        if self._cancel.is_set():
            raise Cancelled("Đã huỷ")

    def _post(self, url: str, form: dict[str, str], referer: str = _REFERER_PC) -> dict[str, Any]:
        self._check_cancel()
        response = self._http.post(url, data=form, timeout=REQUEST_TIMEOUT, headers={
            "Referer": referer, "Content-Type": "application/x-www-form-urlencoded",
            "sec-fetch-site": "same-origin", "sec-fetch-mode": "cors", "sec-fetch-dest": "empty",
        })
        try:
            data = response.json()
        except ValueError:
            raise QrLoginError(f"Zalo trả về dữ liệu lạ (HTTP {response.status_code}) ở {url.rsplit('/', 1)[-1]}") from None
        if not isinstance(data, dict):
            raise QrLoginError("Zalo trả về dữ liệu lạ")
        return data

    def _wait(self, url: str, form: dict[str, str], deadline: float) -> dict[str, Any]:
        """Gọi lệnh chờ (long-poll) lặp lại khi Zalo trả error_code 8, tới khi có kết quả hoặc QR hết hạn."""
        referer = "https://id.zalo.me/account?continue=https%3A%2F%2Fchat.zalo.me%2F"
        while True:
            if time.monotonic() > deadline:
                raise TimeoutError
            try:
                data = self._post(url, form, referer)
            except requests.Timeout:
                continue
            if data.get("error_code") != 8:
                return data

    # ---------- luồng đăng nhập ----------

    def run(self) -> ZaloSession:
        try:
            return self._run()
        except Cancelled:
            self.report(CANCELLED, "Đã huỷ đăng nhập.")
            raise
        except TimeoutError:
            self.report(EXPIRED, "Mã QR đã hết hạn. Bấm tạo mã mới để thử lại.")
            raise QrLoginError("Mã QR đã hết hạn") from None
        except requests.RequestException as exc:
            self.report(ERROR, f"Không kết nối được Zalo: {type(exc).__name__}")
            raise QrLoginError(self.status.message) from None
        except QrLoginError as exc:
            if self.status.state not in FINISHED:
                self.report(ERROR, str(exc))
            raise

    def _run(self) -> ZaloSession:
        self.report(STARTING, "Đang lấy mã QR từ Zalo...")
        page = self._http.get(_LOGIN_PAGE, timeout=REQUEST_TIMEOUT, headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "same-site",
        })
        match = _VERSION.search(page.text)
        if not match:
            raise QrLoginError("Không đọc được trang đăng nhập Zalo (Zalo có thể đã đổi giao diện)")
        version = match.group(1)
        pc = {"continue": "https://zalo.me/pc", "v": version}
        self._post("https://id.zalo.me/account/logininfo", pc)
        self._post("https://id.zalo.me/account/verify-client", {"type": "device", **pc})
        generated = self._post("https://id.zalo.me/account/authen/qr/generate", pc)
        qr = generated.get("data") or {}
        code, image = qr.get("code"), str(qr.get("image") or "")
        if not code or not image:
            raise QrLoginError(f"Zalo không tạo được mã QR: {generated.get('error_message') or generated}")
        image = re.sub(r"^data:image/\w+;base64,", "", image)
        self.report(WAITING_SCAN, "Mở Zalo trên điện thoại (đang đăng nhập acc phụ), bấm biểu tượng quét mã và quét mã này.",
                  image=image)

        deadline = time.monotonic() + QR_LIFETIME_SECONDS
        chat = {"code": code, "continue": "https://chat.zalo.me/", "v": version}
        scanned = self._wait("https://id.zalo.me/account/authen/qr/waiting-scan", chat, deadline)
        if not scanned.get("data"):
            raise QrLoginError(f"Lỗi khi chờ quét mã: {scanned.get('error_message') or scanned}")
        name = str(scanned["data"].get("display_name") or "")
        self.report(SCANNED, f"Đã quét{' bởi ' + name if name else ''}. Bấm \"Đăng nhập\" trên điện thoại để xác nhận.",
                  display_name=name)

        confirmed = self._wait("https://id.zalo.me/account/authen/qr/waiting-confirm",
                               {**chat, "gToken": "", "gAction": "CONFIRM_QR"}, deadline + QR_LIFETIME_SECONDS)
        if confirmed.get("error_code") == -13:
            self.report(DECLINED, "Bạn đã từ chối đăng nhập trên điện thoại.")
            raise QrLoginError("Đăng nhập bị từ chối")
        if confirmed.get("error_code") != 0:
            raise QrLoginError(f"Xác nhận đăng nhập lỗi: {confirmed.get('error_message') or confirmed}")

        self._check_cancel()
        self._http.get("https://id.zalo.me/account/checksession?continue=https%3A%2F%2Fchat.zalo.me%2Findex.html",
                       timeout=REQUEST_TIMEOUT, allow_redirects=True, headers={
                           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                           "Referer": "https://id.zalo.me/",
                       })
        info = self._http.get("https://jr.chat.zalo.me/jr/userinfo", timeout=REQUEST_TIMEOUT,
                              headers={"Referer": "https://chat.zalo.me/"})
        try:
            user = info.json().get("data") or {}
        except ValueError:
            user = {}
        if not user.get("logged"):
            raise QrLoginError("Zalo chưa xác nhận đăng nhập (không lấy được phiên chat.zalo.me)")
        profile = user.get("info") or {}
        cookies = cookies_for(self._http.cookies)
        if not cookies:
            raise QrLoginError("Đăng nhập xong nhưng không nhận được cookies của chat.zalo.me")
        session = ZaloSession(
            cookies=cookies, imei=make_imei(USER_AGENT), user_agent=USER_AGENT,
            display_name=str(profile.get("name") or profile.get("display_name") or name),
            user_id=str(profile.get("uid") or profile.get("userId") or ""),
        )
        self.report(SUCCESS, f"Đã kết nối acc {session.display_name or ''}".strip() + ".", display_name=session.display_name)
        return session


def save_qr_png(image_b64: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(image_b64))


def apply_session(session: ZaloSession, session_path: Path, env_path: Path) -> None:
    """Lưu phiên vừa đăng nhập và bật RECEIVE_MODE=personal trong .env."""
    from bot.ui.admin import envfile

    session.save(session_path)
    if envfile.read_values(env_path).get("RECEIVE_MODE") != "personal":
        envfile.update(env_path, {"RECEIVE_MODE": "personal"})
