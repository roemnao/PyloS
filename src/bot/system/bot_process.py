"""Biển chỉ đường: mã thật đã dời sang pylos.gate.side_gate.vps.bot_process (import cũ vẫn chạy; gỡ ở giai đoạn cuối)."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.gate.side_gate.vps.bot_process")
