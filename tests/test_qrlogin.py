from __future__ import annotations

import base64
import hashlib
import json

import pytest
import requests

from bot.zalo import qrlogin
from bot.zalo.qrlogin import QrLogin, QrLoginError, ZaloSession, apply_session, cookies_for

PNG = base64.b64encode(b"\x89PNG fake").decode()


class FakeResponse:
    def __init__(self, payload=None, text="", status=200):
        self._payload = payload
        self.text = text
        self.status_code = status

    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload


class FakeZalo(requests.Session):
    """Giả lập id.zalo.me / jr.chat.zalo.me theo đúng thứ tự gọi của luồng QR."""

    def __init__(self, confirm_code=0, scans_before=1):
        super().__init__()
        self.calls: list[str] = []
        self.confirm_code = confirm_code
        self.scans_before = scans_before  # số lần waiting-scan trả error_code 8 trước khi có người quét

    def get(self, url, **kwargs):
        self.calls.append("GET " + url.split("?")[0])
        if url.startswith("https://id.zalo.me/account?"):
            return FakeResponse(text='<script src="https://stc-zlogin.zdn.vn/main-2.44.7.js"></script>')
        if "checksession" in url:
            self.cookies.set("zpw_sek", "SEK", domain=".chat.zalo.me")
            self.cookies.set("zpsid", "SID", domain=".zalo.me")
            self.cookies.set("zpsid", "ID-ONLY", domain="id.zalo.me")
            return FakeResponse(text="")
        if "jr/userinfo" in url:
            return FakeResponse({"data": {"logged": True, "info": {"name": "Acc Phụ", "uid": "42"}}})
        raise AssertionError(url)

    def post(self, url, data=None, **kwargs):
        name = url.rsplit("/", 1)[-1]
        self.calls.append("POST " + name)
        assert data["v"] == "2.44.7"
        if name in ("logininfo", "verify-client"):
            return FakeResponse({"error_code": 0})
        if name == "generate":
            return FakeResponse({"error_code": 0, "data": {"code": "C1", "image": "data:image/png;base64," + PNG}})
        if name == "waiting-scan":
            assert data["code"] == "C1"
            if self.scans_before > 0:
                self.scans_before -= 1
                return FakeResponse({"error_code": 8})
            return FakeResponse({"error_code": 0, "data": {"display_name": "Acc Phụ"}})
        if name == "waiting-confirm":
            assert data["gAction"] == "CONFIRM_QR"
            return FakeResponse({"error_code": self.confirm_code})
        raise AssertionError(url)


def test_full_qr_flow_returns_session_with_chat_cookies():
    updates = []
    http = FakeZalo()
    session = QrLogin(lambda st: updates.append((st.state, bool(st.image))), session=http).run()

    assert session.cookies == {"zpw_sek": "SEK", "zpsid": "SID"}  # bỏ cookie riêng của id.zalo.me
    assert session.display_name == "Acc Phụ" and session.user_id == "42"
    assert session.imei.endswith("-" + hashlib.md5(qrlogin.USER_AGENT.encode()).hexdigest())
    assert [s for s, _ in updates] == ["starting", "waiting_scan", "scanned", "success"]
    assert updates[1] == ("waiting_scan", True)
    assert http.calls.count("POST waiting-scan") == 2  # error_code 8 thì gọi lại


def test_declined_and_expired():
    login = QrLogin(session=FakeZalo(confirm_code=-13))
    with pytest.raises(QrLoginError):
        login.run()
    assert login.status.state == "declined"

    login = QrLogin(session=FakeZalo(scans_before=10**6))
    login_deadline = qrlogin.QR_LIFETIME_SECONDS
    qrlogin.QR_LIFETIME_SECONDS = 0
    try:
        with pytest.raises(QrLoginError, match="hết hạn"):
            login.run()
    finally:
        qrlogin.QR_LIFETIME_SECONDS = login_deadline
    assert login.status.state == "expired"


def test_cancel_stops_before_next_request():
    login = QrLogin(session=FakeZalo())
    login.cancel()
    with pytest.raises(QrLoginError):
        login.run()
    assert login.status.state == "cancelled"


def test_cookies_for_prefers_specific_domain():
    jar = requests.cookies.RequestsCookieJar()
    jar.set("a", "broad", domain=".zalo.me")
    jar.set("a", "specific", domain="chat.zalo.me")
    jar.set("b", "other", domain="example.com")
    assert cookies_for(jar) == {"a": "specific"}


def test_apply_session_saves_file_and_enables_personal_mode(tmp_path):
    env = tmp_path / ".env"
    env.write_text("# chú thích\nRECEIVE_MODE=polling\nGEMINI_API_KEY=k\n", encoding="utf-8")
    path = tmp_path / "data" / "zalo_session.json"
    apply_session(ZaloSession(cookies={"zpw_sek": "x"}, imei="i", display_name="An"), path, env)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["imei"] == "i" and saved["cookies"] == {"zpw_sek": "x"} and saved["display_name"] == "An"
    text = env.read_text(encoding="utf-8")
    assert "RECEIVE_MODE=personal" in text and "# chú thích" in text
