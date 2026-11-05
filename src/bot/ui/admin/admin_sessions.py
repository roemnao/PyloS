"""Biển chỉ đường: mã thật đã dời sang pylos.management.owner.admin_web.admin_sessions (import cũ vẫn chạy; gỡ ở giai đoạn cuối)."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.management.owner.admin_web.admin_sessions")
