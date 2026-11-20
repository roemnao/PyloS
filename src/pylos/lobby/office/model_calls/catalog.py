"""Danh sách key -> model: đọc model_keys.md, cho biết một model dùng key nào và của nhà cung cấp nào.

File chỉ ghi TÊN BIẾN (không có giá trị bí mật). Giá trị lấy qua `lookup(tên biến)`, thường là settings.env.
Tự nạp lại khi file đổi. Mục sai bị bỏ qua và ghi cảnh báo (không bao giờ in giá trị key)."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

log = logging.getLogger(__name__)

KEYS_FILE = Path(__file__).with_name("model_keys.md")
# Trường dùng cho chính mục; mọi trường khác là tên biến phụ của nhà cung cấp (ví dụ account của Cloudflare).
CORE_FIELDS = ("provider", "key", "models")
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
_FIELD = re.compile(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$")

Lookup = Callable[[str], str]


def env_lookup(name: str) -> str:
    return os.environ.get(name, "").strip()


@dataclass(frozen=True)
class KeyEntry:
    """Một key đã đọc xong: `secret` là giá trị thật (đừng ghi log), `extras` là giá trị các biến phụ."""
    name: str
    provider: str
    secret_var: str
    models: tuple[str, ...]
    secret: str = field(default="", repr=False)
    extras: dict[str, str] = field(default_factory=dict, repr=False)
    extra_vars: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class _Raw:
    name: str
    provider: str
    secret_var: str
    models: tuple[str, ...]
    extra_vars: dict[str, str]


def _split(value: str) -> tuple[str, ...]:
    return tuple(item.strip().strip("`").strip() for item in value.split(",") if item.strip().strip("`").strip())


def parse_keys(text: str, known_providers: set[str] | None = None) -> list[_Raw]:
    """Đọc model_keys.md thành các mục; mục thiếu trường, provider lạ hoặc trùng tên bị bỏ (ghi cảnh báo)."""
    entries: list[_Raw] = []
    seen_names: set[str] = set()
    taken: dict[str, str] = {}  # model -> tên key đã giữ nó
    blocks = re.split(r"^##\s+", _HTML_COMMENT.sub("", text), flags=re.M)[1:]
    for block in blocks:
        head, _, body = block.partition("\n")
        name = head.strip()
        fields: dict[str, str] = {}
        for line in body.splitlines():
            match = _FIELD.match(line.strip())
            if match:
                fields[match.group(1).lower()] = match.group(2).strip().strip("`").strip()
        missing = [f for f in CORE_FIELDS if not fields.get(f)]
        if not name or missing:
            log.warning("model_keys.md: bỏ mục %r vì thiếu %s", name or "(không tên)", ", ".join(missing) or "tên")
            continue
        provider = fields["provider"].lower()
        if known_providers is not None and provider not in known_providers:
            log.warning("model_keys.md: bỏ mục %s vì nhà cung cấp %r chưa được hỗ trợ", name, provider)
            continue
        if name in seen_names:
            log.warning("model_keys.md: mục %s bị trùng tên, bỏ mục sau", name)
            continue
        seen_names.add(name)
        models = []
        for model in _split(fields["models"]):
            if model in taken:
                log.warning("model_keys.md: model %s nằm ở cả %s và %s, dùng %s", model, taken[model], name, taken[model])
                continue
            taken[model] = name
            models.append(model)
        extras = {k: v for k, v in fields.items() if k not in CORE_FIELDS}
        entries.append(_Raw(name, provider, fields["key"], tuple(models), extras))
    return entries


class ModelCatalog:
    """`resolve(model)` -> KeyEntry của key được phép dùng model đó, hoặc None (model không có trong danh sách)."""

    def __init__(self, path: Path = KEYS_FILE, lookup: Lookup = env_lookup,
                 known_providers: set[str] | None = None) -> None:
        self.path = path
        self.lookup = lookup
        self._known = known_providers
        self._loaded: tuple[float, list[_Raw]] | None = None
        self._warned: set[str] = set()

    def _raw(self) -> list[_Raw]:
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            if self._loaded is None or self._loaded[0] != -1:
                log.warning("Không đọc được %s: mọi model dùng key Gemini chính", self.path.name)
            self._loaded = (-1, [])
            return []
        if self._loaded is None or self._loaded[0] != mtime:
            try:
                entries = parse_keys(self.path.read_text(encoding="utf-8"), self._known)
            except OSError as exc:
                log.warning("Không đọc được %s: %s", self.path.name, exc)
                entries = []
            self._loaded = (mtime, entries)
            self._warned.clear()
            log.info("Đã nạp %s (%d key)", self.path.name, len(entries))
        return self._loaded[1]

    def _ready(self, raw: _Raw) -> KeyEntry | None:
        secret = self.lookup(raw.secret_var)
        extras = {k: self.lookup(var) for k, var in raw.extra_vars.items()}
        missing = [raw.secret_var] if not secret else []
        missing += [var for k, var in raw.extra_vars.items() if not extras[k]]
        if missing:
            if raw.name not in self._warned:
                self._warned.add(raw.name)
                log.warning("model_keys.md: key %s chưa dùng được vì biến %s chưa điền trong settings.env",
                            raw.name, ", ".join(missing))
            return None
        return KeyEntry(raw.name, raw.provider, raw.secret_var, raw.models, secret, extras, dict(raw.extra_vars))

    def resolve(self, model: str) -> KeyEntry | None:
        for raw in self._raw():
            if model in raw.models:
                return self._ready(raw)
        return None

    def entries(self) -> list[dict[str, object]]:
        """Cho trang quản lý: tên, nhà cung cấp, tên biến, model và đã điền key chưa. Không có giá trị bí mật."""
        out = []
        for raw in self._raw():
            ready = bool(self.lookup(raw.secret_var)) and all(self.lookup(v) for v in raw.extra_vars.values())
            out.append({"name": raw.name, "provider": raw.provider, "key": raw.secret_var,
                        "models": list(raw.models), "ready": ready})
        return out

    def models(self, provider: str | None = None) -> list[str]:
        return [m for raw in self._raw() if provider in (None, raw.provider) for m in raw.models]
