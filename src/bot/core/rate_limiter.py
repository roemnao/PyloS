"""Biển chỉ đường: mã thật đã dời sang pylos.gate.fence.token_limit.rate_limiter (import cũ vẫn chạy; gỡ ở giai đoạn cuối)."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.gate.fence.token_limit.rate_limiter")
