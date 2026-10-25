from __future__ import annotations

import pytest

from bot.agent import ToolContext
from bot.agent.tools import assign_events

MEMBERS = {"u-an": "Nguyễn Văn An", "u-binh": "Trần Thị Bình", "u-anh": "Hoàng Anh", "u-binh2": "Bình Lê", "bot": "roemnao"}


def ctx(tmp_path, **kw) -> ToolContext:
    base = dict(chat_id="g1", user_id="u-boss", user_name="Sếp", is_owner=True, data_dir=tmp_path, is_group=True,
                chat_name="Nhóm dự án", message_id="m1", members=MEMBERS, self_id="bot", can_assign=True)
    base.update(kw)
    return ToolContext(**base)


def test_people_from_tags_first_then_names_without_diacritics(tmp_path):
    c = ctx(tmp_path, mentions=("u-binh", "bot"))
    people, missing = assign_events.resolve_people(c, ["an", "Bình", "Châu"])
    assert people == [{"zaloUid": "u-binh", "name": "Trần Thị Bình"}, {"zaloUid": "u-an", "name": "Nguyễn Văn An"}]
    assert missing == ["Châu"]  # "Bình" trùng hai người nhưng đã có người được @tag tên Bình → không báo thiếu
    # Không @tag ai, tên trùng nhiều người thì phải hỏi lại; chính bot không bao giờ nhận lịch.
    people, missing = assign_events.resolve_people(ctx(tmp_path), ["binh", "roemnao", "Anh"], include_sender=True)
    assert [p["zaloUid"] for p in people] == ["u-anh", "u-boss"]
    assert missing == ["binh (trùng tên nhiều người, hãy @tag)"]
    assert assign_events.match_member("an", MEMBERS) == ["u-an"]  # "an" là một từ trong "Nguyễn Văn An", không khớp "Hoàng Anh"


@pytest.fixture
def calbot(web):
    store = {}

    def assign(body):
        eid = f"e{len(store) + 1}"
        store[eid] = body
        linked = [a for a in body["assignees"] if a["zaloUid"] != "u-binh"]
        return {"eventId": eid, "event": {"title": body["title"], "start": "2026-10-30T02:00:00.000Z"},
                "assigned": [{**a, "op": "create"} for a in linked],
                "unlinked": [a for a in body["assignees"] if a["zaloUid"] == "u-binh"], "appUrl": "https://web.example/app/"}

    web.on("POST", "/assign", assign)
    web.on("PATCH", "/assign/e1", lambda body: {"eventId": "e1", "event": {"title": "Họp", "start": "2026-10-30T03:00:00.000Z"},
                                               "assigned": [{"zaloUid": "u-an", "name": "An", "op": "update"},
                                                            {"zaloUid": "u-anh", "name": "Hoàng Anh", "op": "create"}],
                                               "unlinked": [], "appUrl": "https://web.example/app/"})
    web.on("DELETE", "/assign/e1", {"eventId": "e1", "event": {"title": "Họp"}, "assigned": [{"name": "An", "op": "delete"}], "unlinked": []})
    web.on("GET", "/assign/e2", {"eventId": "e2", "assignees": [{"zaloUid": "u-an", "name": "An", "linked": True, "fetchedAt": "2026-10-24T10:00:00Z"},
                                                                {"zaloUid": "u-binh", "name": "Bình", "linked": False, "fetchedAt": None}]})
    return web


async def test_assign_sends_people_and_source_and_reports_unlinked(tmp_path, calbot):
    c = ctx(tmp_path, mentions=("u-an", "u-binh"))
    res = await assign_events._assign({"tieu_de": "Họp", "bat_dau": "2026-10-30T09:00:00+07:00", "ghi_chu": "P301",
                                       "nguoi_nhan": ["An", "Bình"]}, c)
    sent = calbot.bodies("POST", "/assign")[0]
    assert sent["assignees"] == [{"zaloUid": "u-an", "name": "Nguyễn Văn An"}, {"zaloUid": "u-binh", "name": "Trần Thị Bình"}]
    assert sent["title"] == "Họp" and sent["start"] == "2026-10-30T09:00:00+07:00" and sent["note"] == "P301"
    assert sent["source"] == {"chatId": "g1", "chatName": "Nhóm dự án", "senderId": "u-boss", "senderName": "Sếp", "messageId": "m1"}
    assert res["ok"] and res["ma_lich"] == "e1" and res["da_giao"] == ["Nguyễn Văn An"]
    assert res["chua_lien_ket"] == ["Trần Thị Bình"] and "https://web.example/app/" in res["huong_dan_chua_lien_ket"]
    assert assign_events.recent_in_chat(c)[0]["eventId"] == "e1"

    # Cả ngày; không có ai để giao thì báo lỗi, không gọi web.
    await assign_events._assign({"tieu_de": "Nghỉ", "bat_dau": "2026-11-02", "ca_ngay": True, "nguoi_nhan": ["Hoàng Anh"]}, ctx(tmp_path))
    assert calbot.bodies("POST", "/assign")[1]["allDay"] is True
    res = await assign_events._assign({"tieu_de": "X", "bat_dau": "2026-10-30T09:00:00+07:00", "nguoi_nhan": ["Châu"]}, ctx(tmp_path))
    assert "@tag" in res["error"] and "Châu" in res["error"]
    assert len(calbot.bodies("POST", "/assign")) == 2


async def test_update_and_cancel_the_latest_event_by_default(tmp_path, calbot):
    c = ctx(tmp_path, mentions=("u-an",))
    await assign_events._assign({"tieu_de": "Họp", "bat_dau": "2026-10-30T09:00:00+07:00"}, c)
    res = await assign_events._update({"bat_dau": "2026-10-30T10:00:00+07:00", "them_nguoi": ["Hoàng Anh"], "bo_nguoi": ["Châu"]}, ctx(tmp_path))
    assert calbot.bodies("PATCH", "/assign/e1")[0] == {"start": "2026-10-30T10:00:00+07:00", "add": [{"zaloUid": "u-anh", "name": "Hoàng Anh"}]}
    assert res["da_giao"] == ["An (cập nhật lịch)", "Hoàng Anh (thêm vào lịch)"] and res["khong_tim_thay"] == ["Châu"]
    assert [p["zaloUid"] for p in assign_events.recent_in_chat(c)[0]["assignees"]] == ["u-an", "u-anh"]
    assert "error" in await assign_events._update({}, ctx(tmp_path))  # không có gì để sửa

    res = await assign_events._cancel({}, ctx(tmp_path))
    assert res["ok"] and res["da_huy"] == "Họp" and res["xoa_khoi_lich_cua"] == ["An"]
    assert assign_events.recent_in_chat(c) == []
    assert "Chưa có lịch" in (await assign_events._cancel({}, ctx(tmp_path)))["error"]
    assert "Chưa có lịch" in (await assign_events._update({"tieu_de": "x"}, ctx(tmp_path, chat_id="g2")))["error"]


async def test_list_shows_who_has_it_in_their_app(tmp_path, calbot):
    await assign_events._assign({"tieu_de": "Họp 1", "bat_dau": "2026-10-30T09:00:00+07:00", "nguoi_nhan": ["An"]}, ctx(tmp_path))
    await assign_events._assign({"tieu_de": "Họp 2", "bat_dau": "2026-10-31T09:00:00+07:00", "nguoi_nhan": ["An", "Trần Thị Bình"]}, ctx(tmp_path))
    res = await assign_events._list({}, ctx(tmp_path))
    first = res["lich_da_giao"][0]
    assert first["ma_lich"] == "e2" and first["da_vao_app"] == ["An"] and first["chua_lien_ket"] == ["Bình"]
    assert res["lich_da_giao"][1]["ma_lich"] == "e1" and "da_vao_app" not in res["lich_da_giao"][1]  # web không trả tình trạng


async def test_only_allowed_people_can_assign(tmp_path, calbot):
    res = await assign_events._assign({"tieu_de": "Họp", "bat_dau": "2026-10-30T09:00:00+07:00", "nguoi_nhan": ["An"]},
                                      ctx(tmp_path, is_owner=False, can_assign=False))
    assert "chính mình" in res["error"] and calbot.bodies("POST", "/assign") == []


def test_tools_need_web_key(monkeypatch, tmp_path):
    monkeypatch.setattr("bot.config.APP_HOME", tmp_path)
    monkeypatch.delenv("SCHEDULE_API_KEY", raising=False)
    assert assign_events._tools() == []
    monkeypatch.setenv("SCHEDULE_API_KEY", "k")
    tools = {t.name: t for t in assign_events._tools()}
    assert set(tools) == {"giao_lich", "sua_lich", "huy_lich", "lich_da_giao", "lich_cua_toi"}
    assert not any(t.owner_only for t in tools.values())  # quyền kiểm tra theo ASSIGN_ALLOWED (đổi được trên web)


# ---------- vai trò basic / leader, đội ----------

def basic(tmp_path, **kw) -> ToolContext:
    base = dict(user_id="u-an", user_name="Nguyễn Văn An", is_owner=False, can_assign=False, role="basic")
    return ctx(tmp_path, **{**base, **kw})


async def test_basic_can_only_assign_to_self(tmp_path, calbot):
    ev = {"tieu_de": "Nộp báo cáo", "bat_dau": "2026-10-30T09:00:00+07:00"}
    res = await assign_events._assign(ev, basic(tmp_path))
    assert res["ok"] and calbot.bodies("POST", "/assign")[0]["assignees"] == [{"zaloUid": "u-an", "name": "Nguyễn Văn An"}]
    # "tôi", "mình" hoặc chính tên mình vẫn là chính mình.
    res = await assign_events._assign({**ev, "nguoi_nhan": ["tôi", "Nguyễn Văn An"]}, basic(tmp_path))
    assert res["ok"] and len(calbot.bodies("POST", "/assign")) == 2
    # @tag người khác, nêu tên người khác, đội, hoặc tên không có: đều bị từ chối và không gọi web.
    for extra in ({"nguoi_nhan": ["Bình"]}, {"nhom": ["thietke"]}, {"nguoi_nhan": ["Châu"]}):
        res = await assign_events._assign({**ev, **extra}, basic(tmp_path))
        assert "chính mình" in res["error"], extra
    res = await assign_events._assign(ev, basic(tmp_path, mentions=("u-binh",)))
    assert "chính mình" in res["error"]
    assert len(calbot.bodies("POST", "/assign")) == 2


async def test_basic_edits_only_own_events(tmp_path, calbot):
    boss = ctx(tmp_path)
    await assign_events._assign({"tieu_de": "Họp", "bat_dau": "2026-10-30T09:00:00+07:00", "nguoi_nhan": ["An"]}, boss)  # e1: sếp giao An
    me = basic(tmp_path)
    assert "chính bạn" in (await assign_events._cancel({"ma_lich": "e1"}, me))["error"]  # lịch do sếp tạo
    assert "Chưa có lịch" in (await assign_events._cancel({}, me))["error"]  # chưa có lịch nào của mình
    await assign_events._assign({"tieu_de": "Việc riêng", "bat_dau": "2026-10-31T09:00:00+07:00"}, me)  # e2
    assert "chính mình" in (await assign_events._update({"ma_lich": "e2", "them_nguoi": ["Bình"]}, me))["error"]
    assert calbot.bodies("PATCH", "/assign/e1") == []


async def test_leader_assigns_to_team(tmp_path, calbot):
    teams = {"thiet ke": ["u-an", "u-anh"]}
    c = ctx(tmp_path, teams=teams)
    res = await assign_events._assign({"tieu_de": "Họp", "bat_dau": "2026-10-30T09:00:00+07:00", "nhom": ["Thiết kế"]}, c)
    assert [a["zaloUid"] for a in calbot.bodies("POST", "/assign")[0]["assignees"]] == ["u-an", "u-anh"]
    res = await assign_events._assign({"tieu_de": "Họp", "bat_dau": "2026-10-30T09:00:00+07:00", "nhom": ["Nhóm marketing"], "nguoi_nhan": ["An"]}, c)
    assert res["khong_tim_thay"] == ["đội Nhóm marketing"] and len(calbot.bodies("POST", "/assign")) == 2


async def test_my_upcoming_events(tmp_path):
    boss = ctx(tmp_path)

    def remember(eid, title, start, people, all_day=False):
        assign_events._remember(boss, eid, {"title": title, "start": start, "allDay": all_day},
                                [{"zaloUid": u, "name": u} for u in people])

    remember("e1", "Quá khứ", "2020-01-01T09:00:00+07:00", ["u-an"])
    remember("e2", "Sau", "2099-12-31T09:00:00+07:00", ["u-an"])
    remember("e3", "Trước", "2099-01-01", ["u-an", "u-binh"], all_day=True)
    remember("e4", "Của Bình", "2099-06-01T09:00:00+07:00", ["u-binh"])
    remember("e5", "Đã huỷ", "2099-02-01T09:00:00+07:00", ["u-an"])
    assign_events._forget(boss, "e5")
    mine = await assign_events._mine({}, basic(tmp_path))
    assert [i["tieu_de"] for i in mine["lich_cua_toi"]] == ["Trước", "Sau"]
    assert (await assign_events._mine({"so_luong": 1}, basic(tmp_path)))["lich_cua_toi"][0]["tieu_de"] == "Trước"
    assert (await assign_events._mine({}, basic(tmp_path, user_id="u-khac")))["lich_cua_toi"] == []
