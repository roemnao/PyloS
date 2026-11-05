"""Biển chỉ đường: mã thật đã dời sang pylos.gate.fence.speech_limit.text_fold (import cũ vẫn chạy; gỡ ở giai đoạn cuối)."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.gate.fence.speech_limit.text_fold")
