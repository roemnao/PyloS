"""Biển chỉ đường: mã thật đã dời sang pylos.lobby.dispatch.lifecycle (giữ để import cũ còn chạy)."""

from pylos.lobby.dispatch.lifecycle.process_lock import *  # noqa: F401,F403
from pylos.lobby.dispatch.lifecycle.process_lock import AlreadyRunning, InstanceLock  # noqa: F401
