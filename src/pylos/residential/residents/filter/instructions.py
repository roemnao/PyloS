"""Căn hộ của bot lọc: chỉ dẫn lấy từ mọi tài liệu .md/.txt trong workspace/ (SOUL.md...), tự nạp lại khi file đổi."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

SHIFT_DOC = "modelShift.md"  # trong căn hộ: bảng hồ sơ (profile -> model, thinking, dự phòng) và cách nhận biết loại việc
PROFILE_NAMES = ("routine", "reflective", "coding", "documents")
THINKING_LEVELS = ("low", "medium", "high")


@dataclass(frozen=True)
class Profile:
    name: str
    model: str
    thinking: str
    fallbacks: tuple[str, ...] = ()


# Dùng khi modelShift.md thiếu, hỏng hoặc thiếu dòng của hồ sơ nào đó.
DEFAULT_PROFILES: dict[str, Profile] = {
    "routine": Profile("routine", "gemini-3.1-flash-lite", "low", ("gemini-3.5-flash-lite",)),
    "reflective": Profile("reflective", "gemini-3.1-flash-lite", "medium", ("gemini-3.5-flash-lite",)),
    "coding": Profile("coding", "gemini-4-hydrogen", "medium", ("gemini-3.5-flash-lite", "gemini-3.1-flash-lite")),
    "documents": Profile("documents", "gemini-3.5-flash-lite", "medium", ("gemini-3.1-flash-lite",)),
}


TASK_NAMES = ("image",)


@dataclass(frozen=True)
class TaskModel:
    """Model cho một loại việc không phải trả lời chat (bảng `| task | model | fallbacks |` trong modelShift.md)."""
    task: str
    model: str
    fallbacks: tuple[str, ...] = ()


DEFAULT_TASKS: dict[str, TaskModel] = {
    "image": TaskModel("image", "@cf/black-forest-labs/flux-1-schnell"),
}


def _fallbacks(cell: str) -> tuple[str, ...]:
    items = (f.strip().strip("`").strip() for f in cell.split(","))
    return tuple(f for f in items if f and f != "-")


def parse_tasks(text: str) -> dict[str, TaskModel]:
    """Đọc bảng `| task | model | fallbacks |`. Dòng thiếu model bị bỏ; nhiệm vụ không có dòng hợp lệ dùng DEFAULT_TASKS."""
    found: dict[str, TaskModel] = {}
    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() not in TASK_NAMES:
            continue  # tiêu đề, dòng kẻ ---, hoặc bảng hồ sơ
        task, model = cells[0].lower(), cells[1]
        if not model or model == "-":
            log.warning("modelShift.md: bỏ dòng nhiệm vụ %s vì thiếu model", task)
            continue
        found[task] = TaskModel(task, model, _fallbacks(cells[2] if len(cells) > 2 else ""))
    for task, default in DEFAULT_TASKS.items():
        found.setdefault(task, default)
    return found


def parse_profiles(text: str) -> dict[str, Profile]:
    """Đọc bảng markdown `| profile | model | thinking | fallbacks |` trong modelShift.md.

    Dòng sai (tên lạ, thiếu model, thinking không phải low/medium/high) bị bỏ qua và ghi cảnh báo;
    hồ sơ không có dòng hợp lệ thì dùng DEFAULT_PROFILES."""
    found: dict[str, Profile] = {}
    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() not in PROFILE_NAMES:
            continue  # tiêu đề, dòng kẻ ---, hoặc bảng khác
        name, model, thinking = cells[0].lower(), cells[1], cells[2].lower()
        if not model or thinking not in THINKING_LEVELS:
            log.warning("modelShift.md: bỏ dòng hồ sơ %s vì thiếu model hoặc thinking không phải low/medium/high", name)
            continue
        fallbacks = tuple(f.strip().strip("`").strip() for f in (cells[3] if len(cells) > 3 else "").split(",")
                          if f.strip().strip("`").strip() and f.strip() != "-")
        found[name] = Profile(name, model, thinking, fallbacks)
    for name, default in DEFAULT_PROFILES.items():
        found.setdefault(name, default)
    return found

# Ghi chú <!-- ... --> trong file là cho người đọc, không đưa vào chỉ dẫn.
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
DOC_SUFFIXES = {".md", ".txt"}
MAX_CHARS = 20_000  # tổng chỉ dẫn; quá thì bỏ phần sau và ghi cảnh báo


class FilterInstructions:
    """`text(names)`: chỉ dẫn của bot lọc, `{names}` được thay bằng tên gọi của bot chính. Rỗng nếu workspace trống."""

    def __init__(self, workspace_dir: Path) -> None:
        self._workspace = workspace_dir
        self._cache: dict[Path, tuple[float, str]] = {}

    def _read(self, path: Path) -> str:
        mtime = path.stat().st_mtime
        cached = self._cache.get(path)
        if cached is None or cached[0] != mtime:
            cached = (mtime, _HTML_COMMENT.sub("", path.read_text(encoding="utf-8")).strip())
            self._cache[path] = cached
            log.info("Đã nạp %s của bot lọc", path.name)
        return cached[1]

    def docs(self) -> list[tuple[str, str]]:
        if not self._workspace.is_dir():
            return []
        found, used = [], 0
        for path in sorted(self._workspace.rglob("*"), key=lambda p: p.relative_to(self._workspace).as_posix().lower()):
            rel = path.relative_to(self._workspace)
            if not path.is_file() or path.suffix.lower() not in DOC_SUFFIXES or any(part.startswith(".") for part in rel.parts):
                continue
            try:
                text = self._read(path)
            except OSError as exc:
                log.warning("Không đọc được %s của bot lọc: %s", rel, exc)
                continue
            if not text:
                continue
            if used + len(text) > MAX_CHARS:
                log.warning("Chỉ dẫn của bot lọc quá dài: bỏ %s và các file sau (tối đa %d ký tự)", rel, MAX_CHARS)
                break
            used += len(text)
            found.append((rel.as_posix(), text))
        return found

    def doc(self, name: str) -> str:
        """Nội dung một file trong căn hộ (ví dụ modelShift.md); rỗng nếu thiếu hoặc không đọc được."""
        path = self._workspace / name
        try:
            return self._read(path) if path.is_file() else ""
        except OSError as exc:
            log.warning("Không đọc được %s của bot lọc: %s", name, exc)
            return ""

    def profiles(self) -> dict[str, Profile]:
        """Bảng hồ sơ hiện hành (tự nạp lại khi modelShift.md đổi); hỏng hoặc thiếu thì dùng mặc định."""
        return parse_profiles(self.doc(SHIFT_DOC))

    def tasks(self) -> dict[str, TaskModel]:
        """Bảng model theo nhiệm vụ (ví dụ tạo ảnh); tự nạp lại khi modelShift.md đổi, hỏng hoặc thiếu thì dùng mặc định."""
        return parse_tasks(self.doc(SHIFT_DOC))

    def text(self, names: str) -> str:
        docs = self.docs()
        body = docs[0][1] if len(docs) == 1 else "\n\n".join(f"## {name}\n{text}" for name, text in docs)
        return body.replace("{names}", names)
