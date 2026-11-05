"""Biển chỉ đường: mã thật đã dời sang pylos.gate.main_gate.zalo.receive_polling (import cũ vẫn chạy; gỡ ở giai đoạn cuối)."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.gate.main_gate.zalo.receive_polling")
