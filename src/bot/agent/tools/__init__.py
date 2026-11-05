"""Biển chỉ đường: registry công cụ đã dời sang pylos.lobby.office.agent_tools.

Giữ lại vì tool người dùng tự viết (userdata/data/custom_tools) và mẫu tool vẫn `from bot.agent.tools import Tool, ToolContext`.
"""

from pylos.lobby.office.agent_tools import *  # noqa: F401,F403
from pylos.lobby.office.agent_tools import Tool, ToolContext, ToolRegistry, discover  # noqa: F401
