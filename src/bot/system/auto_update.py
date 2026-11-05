"""Biển chỉ đường: mã thật đã dời sang pylos.lobby.dispatch.updater.auto_update (import cũ vẫn chạy; gỡ ở giai đoạn cuối)."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.lobby.dispatch.updater.auto_update")
