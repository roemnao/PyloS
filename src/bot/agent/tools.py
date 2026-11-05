"""Compat: tool tự viết trong userdata/data/custom_tools vẫn `from bot.agent.tools import Tool, ToolContext`. Mã thật ở pylos.lobby.office.agent_tools."""

import importlib
import sys

sys.modules[__name__] = importlib.import_module("pylos.lobby.office.agent_tools")
