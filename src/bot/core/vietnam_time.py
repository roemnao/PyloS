"""Compat: tool tự viết trong src/pylos/lobby/office/agent_tools/custom vẫn `from bot.core.vietnam_time import now_vn`. Mã thật ở pylos.lobby.dispatch.clock.vietnam_time."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.lobby.dispatch.clock.vietnam_time")
