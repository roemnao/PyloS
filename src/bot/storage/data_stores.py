"""Các kho dữ liệu của bot (tên file: xem bot/userdata_paths.py), nằm trong userdata/data và userdata/system.

Bot và giao diện quản lý (tiến trình riêng) cùng đọc/ghi các file này. Kho nào
cả hai bên cùng ghi thì luôn đọc lại file ngay trước khi sửa (đọc-sửa-ghi),
thay vì tin vào bản đang giữ trong RAM.
"""

from __future__ import annotations

import os
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from bot.userdata_paths import done_file
from bot.storage.text_files import JsonLinesFile, JsonObjectFile
from bot.core.text_fold import fold
from bot.core.vietnam_time import now_ms, today_vn

MODE_ALL = "all"
MODE_DEFAULT = "default"
MODES = (MODE_ALL, MODE_DEFAULT)


@dataclass
class GroupState:
    chat_id: str
    allowed: bool = False
    mode: str = MODE_DEFAULT
    label: str = ""
    blocked: bool = False  # bị /deny rõ ràng: vẫn bị chặn cả khi ALLOW_ALL_CHATS=true
    leaders: list[str] = field(default_factory=list)  # Zalo ID được nhờ bot giao lịch trong nhóm (/leader)
    leaders_all: bool = False  # /leader all: ai trong nhóm cũng giao lịch được
    leader_added_by: dict[str, str] = field(default_factory=dict)  # {leader: người đã thêm}
    teams: dict[str, dict[str, Any]] = field(default_factory=dict)  # {tên đội đã fold: {"name": tên hiển thị, "members": [uid]}}


def _clean_map(value: Any) -> dict[str, str]:
    return {str(k): str(v) for k, v in value.items()} if isinstance(value, dict) else {}


def _clean_teams(value: Any) -> dict[str, dict[str, Any]]:
    teams: dict[str, dict[str, Any]] = {}
    if isinstance(value, dict):
        for key, team in value.items():
            if isinstance(team, dict) and isinstance(team.get("members"), list):
                teams[str(key)] = {"name": str(team.get("name") or key), "members": [str(m) for m in team["members"] if m]}
    return teams


def _mtime(path: Path) -> float | None:
    try:
        return os.stat(path).st_mtime_ns
    except FileNotFoundError:
        return None


class GroupStore:
    """group_settings.txt: mỗi dòng một nhóm {chat_id, allowed, mode, label, updated_at}.

    Tự nạp lại khi file bị sửa từ bên ngoài (giao diện quản lý), và đọc lại
    trước mỗi lần ghi để không ghi đè thay đổi của tiến trình kia.
    """

    def __init__(self, path: Path, seed_allowed: tuple[str, ...] = ()) -> None:
        self._file = JsonLinesFile(path)
        self._groups: dict[str, GroupState] = {}
        self._loaded_mtime: float | None = None
        self._load()
        self.allow_seed(seed_allowed)

    def allow_seed(self, chat_ids: tuple[str, ...]) -> None:
        """Cho phép các chat trong ALLOWED_CHAT_IDS (lúc khởi động, hoặc khi danh sách đổi trên web)."""
        if any(not self.get(chat_id).allowed for chat_id in chat_ids):
            self._update(chat_ids, lambda s: setattr(s, "allowed", True))

    def _load(self) -> None:
        groups: dict[str, GroupState] = {}
        for record in self._file.read_all():
            chat_id = str(record.get("chat_id", ""))
            if not chat_id:
                continue
            mode = record.get("mode") if record.get("mode") in MODES else MODE_DEFAULT
            leaders = record.get("leaders")
            groups[chat_id] = GroupState(
                chat_id, bool(record.get("allowed")), mode, str(record.get("label") or ""), bool(record.get("blocked")),
                [str(x) for x in leaders if x] if isinstance(leaders, list) else [], bool(record.get("leaders_all")),
                _clean_map(record.get("leader_added_by")), _clean_teams(record.get("teams")),
            )
        self._groups = groups
        self._loaded_mtime = _mtime(self._file.path)

    def _refresh(self) -> None:
        if _mtime(self._file.path) != self._loaded_mtime:
            self._load()

    def get(self, chat_id: str) -> GroupState:
        self._refresh()
        return self._groups.get(chat_id) or GroupState(chat_id)

    def all(self) -> list[GroupState]:
        self._refresh()
        return list(self._groups.values())

    def _update(self, chat_ids: tuple[str, ...] | list[str], change) -> None:
        self._load()  # luôn đọc bản mới nhất trước khi sửa
        for chat_id in chat_ids:
            change(self._groups.setdefault(chat_id, GroupState(chat_id)))
        stamp = now_ms()
        self._file.rewrite([
            {"chat_id": g.chat_id, "allowed": g.allowed, "mode": g.mode, "label": g.label, "blocked": g.blocked,
             "leaders": g.leaders, "leaders_all": g.leaders_all,
             "leader_added_by": g.leader_added_by, "teams": g.teams, "updated_at": stamp}
            for g in self._groups.values()
        ])
        self._loaded_mtime = _mtime(self._file.path)

    def set_allowed(self, chat_id: str, allowed: bool) -> GroupState:
        def change(state: GroupState) -> None:
            state.allowed = allowed
            state.blocked = not allowed  # /deny = chặn hẳn; /allow = bỏ chặn

        self._update([chat_id], change)
        return self._groups[chat_id]

    def is_allowed(self, chat_id: str, allow_all: bool) -> bool:
        """Được phép khi nằm trong danh sách cho phép, hoặc (ALLOW_ALL_CHATS) khi chưa bị chặn."""
        state = self.get(chat_id)
        return state.allowed or (allow_all and not state.blocked)

    def set_mode(self, chat_id: str, mode: str) -> GroupState:
        if mode not in MODES:
            raise ValueError(mode)
        self._update([chat_id], lambda s: setattr(s, "mode", mode))
        return self._groups[chat_id]

    def set_label(self, chat_id: str, label: str) -> GroupState:
        self._update([chat_id], lambda s: setattr(s, "label", label.strip()[:60]))
        return self._groups[chat_id]

    def set_leaders(self, chat_id: str, *, add: tuple[str, ...] | list[str] = (),
                    remove: tuple[str, ...] | list[str] = (), all_: bool | None = None,
                    clear: bool = False, by: str = "") -> GroupState:
        """Danh sách người được nhờ bot giao lịch trong nhóm (lệnh /add leader, /remove leader, /leader)."""
        def change(state: GroupState) -> None:
            if clear:
                state.leaders, state.leaders_all, state.leader_added_by = [], False, {}
            if all_ is not None:
                state.leaders_all = all_
            leaders = [uid for uid in state.leaders if uid not in remove]
            added = [uid for uid in dict.fromkeys(add) if uid and uid not in leaders]
            leaders += added
            state.leaders = leaders
            state.leader_added_by = {u: b for u, b in state.leader_added_by.items() if u in leaders}
            for uid in added:
                if by:
                    state.leader_added_by[uid] = by

        self._update([chat_id], change)
        return self._groups[chat_id]

    def set_team(self, chat_id: str, name: str, *, add: tuple[str, ...] | list[str] = (),
                 remove: tuple[str, ...] | list[str] = ()) -> GroupState:
        """Tạo đội hoặc thêm / bớt người (lệnh /team). Tên đội không phân biệt hoa thường và dấu."""
        key = fold(name).strip()
        if not key:
            raise ValueError(name)

        def change(state: GroupState) -> None:
            team = state.teams.setdefault(key, {"name": name.strip()[:40], "members": []})
            members = [uid for uid in team["members"] if uid not in remove]
            members += [uid for uid in dict.fromkeys(add) if uid and uid not in members]
            team["members"] = members

        self._update([chat_id], change)
        return self._groups[chat_id]

    def delete_team(self, chat_id: str, name: str) -> bool:
        key = fold(name).strip()
        existed = key in self.get(chat_id).teams
        if existed:
            self._update([chat_id], lambda s: s.teams.pop(key, None))
        return existed

    def team_members(self, chat_id: str, name: str) -> list[str] | None:
        """Thành viên đội, hoặc None nếu không có đội tên đó."""
        team = self.get(chat_id).teams.get(fold(name).strip())
        return list(team["members"]) if team else None

    def can_assign(self, chat_id: str, user_id: str) -> bool:
        state = self.get(chat_id)
        return state.leaders_all or user_id in state.leaders


class SeenStore:
    """processed_message_ids.txt (userdata/system): khóa các tin đã xử lý, chỉ giữ `keep` khóa gần nhất."""

    def __init__(self, path: Path, keep: int = 2000) -> None:
        self._file = JsonLinesFile(path)
        self._keep = keep
        records = self._file.tail(keep)
        self._order: deque[str] = deque((str(r.get("id")) for r in records if r.get("id")), maxlen=keep)
        self._set = set(self._order)
        self._appended = 0

    def __contains__(self, key: str) -> bool:
        return key in self._set

    def add(self, key: str) -> None:
        if key in self._set:
            return
        if len(self._order) == self._keep:
            self._set.discard(self._order[0])
        self._order.append(key)
        self._set.add(key)
        self._file.append({"id": key, "t": now_ms()})
        self._appended += 1
        if self._appended >= self._keep:
            self._file.rewrite([{"id": k} for k in self._order])
            self._appended = 0


_SAFE_NAME = re.compile(r"[^A-Za-z0-9_-]")


def safe_name(chat_id: str) -> str:
    """Tên file an toàn từ chat_id (chặn ../ và ký tự lạ)."""
    return _SAFE_NAME.sub("_", chat_id)[:120] or "_"


class HistoryStore:
    """session_history/<chat_id>.txt: mỗi lượt một dòng {role, uid, name, text, t}."""

    def __init__(self, directory: Path, keep: int = 200) -> None:
        self._dir = directory
        self.keep = keep

    def _file(self, chat_id: str) -> JsonLinesFile:
        return JsonLinesFile(self._dir / f"{safe_name(chat_id)}.txt")

    def append(self, chat_id: str, role: str, text: str, uid: str = "", name: str = "") -> None:
        f = self._file(chat_id)
        f.append({"role": role, "uid": uid, "name": name, "text": text, "t": now_ms()})
        if f.count_lines() > self.keep * 2:
            f.trim(self.keep)

    def recent(self, chat_id: str, n: int) -> list[dict[str, Any]]:
        return self._file(chat_id).tail(n)

    def clear(self, chat_id: str) -> None:
        self._file(chat_id).rewrite([])


class MemoryDataStore:
    """memorydata/<chat_id>.txt: MỌI tin của hội thoại (kể cả tin bộ lọc chặn), mỗi dòng một JSON.

    {"t", "role": "user"|"model", "msg_id", "uid", "name", "type": "text"|"other", "text",
     "filter": {"passed", "stage", "reason"}}   (câu trả lời của bot không có "filter")

    Khác HistoryStore (session gửi cho Gemini, chỉ có tin qua lọc). Bot đọc file này qua tool doc_memorydata.
    """

    def __init__(self, directory: Path, keep: int = 5000) -> None:
        self._dir = directory
        self.keep = keep

    def path(self, chat_id: str) -> Path:
        return self._dir / f"{safe_name(chat_id)}.txt"

    def _append(self, chat_id: str, record: dict[str, Any]) -> None:
        f = JsonLinesFile(self.path(chat_id))
        f.append(record)
        if self.keep and f.count_lines() > self.keep * 2:
            f.trim(self.keep)

    def add_user(self, chat_id: str, *, msg_id: str | None, uid: str, name: str, text: str | None,
                 is_text: bool, decision: dict[str, Any]) -> None:
        self._append(chat_id, {
            "t": now_ms(), "role": "user", "msg_id": msg_id, "uid": uid, "name": name,
            "type": "text" if is_text else "other", "text": text or "", "filter": decision,
        })

    def add_model(self, chat_id: str, text: str) -> None:
        self._append(chat_id, {"t": now_ms(), "role": "model", "text": text})

    def recent(self, chat_id: str, n: int) -> list[dict[str, Any]]:
        return JsonLinesFile(self.path(chat_id)).tail(n) if n > 0 else []


class StateStore:
    """bot_status.txt (userdata/system): thời điểm khởi động, lần poll cuối, tin cuối (để healthcheck)."""

    def __init__(self, path: Path) -> None:
        self._file = JsonObjectFile(path)
        self.data = self._file.read()

    def update(self, **fields: Any) -> None:
        self.data.update(fields)
        self._file.write(self.data)


class UsageStore:
    """token_usage.txt: số token Gemini đã dùng trong ngày (giờ Việt Nam).

    Không giữ số trong RAM: mỗi lần đọc/ghi đều đọc file, để bot và trang
    "Chat thử" của giao diện cùng cộng token mà không mất số của nhau.
    """

    def __init__(self, path: Path) -> None:
        self._file = JsonObjectFile(path)

    def _read(self) -> dict[str, Any]:
        data = self._file.read()
        if data.get("day") != today_vn():
            return {"day": today_vn(), "tokens": 0, "notified": []}
        return {"day": data["day"], "tokens": int(data.get("tokens") or 0), "notified": list(data.get("notified") or [])}

    def add(self, tokens: int) -> int:
        data = self._read()
        data["tokens"] += max(0, tokens)
        self._file.write(data)
        return data["tokens"]

    def used_today(self) -> int:
        return self._read()["tokens"]

    def mark_notified(self, chat_id: str) -> bool:
        """Trả về True nếu đây là lần đầu báo cho chat này trong ngày."""
        data = self._read()
        if chat_id in data["notified"]:
            return False
        data["notified"].append(chat_id)
        self._file.write(data)
        return True


class StatsStore:
    """daily_stats.txt: số liệu theo ngày {"2026-10-22": {"received", "replied", "errors", "tokens", ...}}."""

    # filter_pass / filter_block: số tin trong nhóm bộ lọc cho qua / chặn
    FIELDS = ("received", "replied", "errors", "tokens", "filter_pass", "filter_block")

    def __init__(self, path: Path, keep_days: int = 90) -> None:
        self._file = JsonObjectFile(path)
        self._keep_days = keep_days

    def incr(self, field: str, amount: int = 1) -> None:
        if field not in self.FIELDS or amount <= 0:
            return
        data = self._file.read()
        day = data.setdefault(today_vn(), {})
        day[field] = int(day.get(field) or 0) + amount
        for old in sorted(data)[:-self._keep_days]:
            del data[old]
        self._file.write(data)

    def days(self, n: int = 14) -> list[dict[str, Any]]:
        data = self._file.read()
        return [
            {"day": day, **{f: int((data.get(day) or {}).get(f) or 0) for f in self.FIELDS}}
            for day in sorted(data)[-n:]
        ]

    def today(self) -> dict[str, int]:
        day = self._file.read().get(today_vn()) or {}
        return {f: int(day.get(f) or 0) for f in self.FIELDS}


class ActivityStore:
    """chat_activity.txt: lần nhắn cuối của mỗi chat {chat_id: {type, last_seen, last_name}}.

    Zalo không gửi tên nhóm, nên giao diện dùng thông tin này (cùng nhãn tự đặt)
    để bạn nhận ra nhóm nào là nhóm nào, kể cả nhóm chưa được cho phép.
    """

    def __init__(self, path: Path) -> None:
        self._file = JsonObjectFile(path)

    def touch(self, chat_id: str, chat_type: str, name: str) -> None:
        data = self._file.read()
        data[chat_id] = {"type": chat_type, "last_seen": now_ms(), "last_name": name}
        self._file.write(data)

    def all(self) -> dict[str, dict[str, Any]]:
        return self._file.read()


class FailedStore:
    """failed_replies.txt: tin không gửi được sau khi đã thử lại (dead-letter).

    Chỉ nối thêm (bot ghi). Tin đã gửi lại/bỏ qua được ghi id vào failed_replies_done.txt
    (giao diện ghi), nên hai tiến trình không bao giờ ghi đè file của nhau.
    """

    def __init__(self, path: Path) -> None:
        self._file = JsonLinesFile(path)
        self._done = JsonLinesFile(path.with_name(done_file(path.name)))

    def add(self, chat_id: str, text: str, error: str) -> None:
        stamp = now_ms()
        self._file.append({"id": f"{stamp}-{os.urandom(3).hex()}", "chat_id": chat_id, "text": text, "error": error, "t": stamp})

    def pending(self) -> list[dict[str, Any]]:
        done = {str(r.get("id")) for r in self._done.read_all()}
        records = []
        for index, record in enumerate(self._file.read_all()):
            record.setdefault("id", f"legacy-{index}-{record.get('t', 0)}")
            if record["id"] not in done:
                records.append(record)
        return records

    def mark_done(self, failed_id: str, how: str) -> None:
        self._done.append({"id": failed_id, "how": how, "t": now_ms()})
