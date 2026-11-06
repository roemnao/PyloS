"""Compat: tool tự viết trong userdata/data/custom_tools vẫn `from bot.core.vietnam_time import now_vn`. Mã thật ở pylos.lobby.dispatch.clock.vietnam_time."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.lobby.dispatch.clock.vietnam_time")
