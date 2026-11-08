"""Compat: tool tự viết trong src/pylos/lobby/office/agent_tools/custom vẫn `from bot.agent.tools import Tool, ToolContext`. Mã thật ở pylos.lobby.office.agent_tools."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.lobby.office.agent_tools")
