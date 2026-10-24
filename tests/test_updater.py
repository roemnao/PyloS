from __future__ import annotations

import subprocess

import pytest

from bot.system import auto_update


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repos(tmp_path, monkeypatch):
    """origin (bare) + bản ở máy người dùng + một bản khác để đẩy code mới lên origin."""
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "--bare", "-b", "main", str(origin))
    dev = tmp_path / "dev"
    git(tmp_path, "clone", str(origin), str(dev))
    for repo in (dev,):
        git(repo, "config", "user.email", "t@t")
        git(repo, "config", "user.name", "t")
    (dev / "README.md").write_text("v1\n", encoding="utf-8")
    git(dev, "add", ".")
    git(dev, "commit", "-m", "đầu tiên")
    git(dev, "push", "origin", "HEAD:main")
    local = tmp_path / "local"
    git(tmp_path, "clone", str(origin), str(local))
    monkeypatch.setattr(auto_update, "PROJECT_ROOT", local)
    monkeypatch.setattr(auto_update, "is_frozen", lambda: False)
    return dev, local


def push_change(dev, name, text, message):
    (dev / name).write_text(text, encoding="utf-8")
    git(dev, "add", ".")
    git(dev, "commit", "-m", message)
    git(dev, "push", "origin", "HEAD:main")


def test_pending_then_update_pulls_new_commits(repos, monkeypatch):
    dev, local = repos
    assert auto_update.pending_commits() == 0
    assert not auto_update.update().changed

    push_change(dev, "README.md", "v2\n", "Sửa README")
    push_change(dev, "a.txt", "x\n", "Thêm a")
    assert auto_update.pending_commits() == 2

    pip_calls = []
    monkeypatch.setattr(auto_update, "_run", lambda *a, **k: pip_calls.append(a) if "pip" in a else updater_run(*a, **k))
    result = auto_update.update()
    assert result.changed and "2 thay đổi" in result.message and "• Sửa README" in result.message
    assert (local / "README.md").read_text(encoding="utf-8") == "v2\n"
    assert pip_calls == []  # pyproject.toml không đổi thì không cài lại thư viện

    push_change(dev, "pyproject.toml", "[project]\n", "Đổi thư viện")
    auto_update.update()
    assert pip_calls and pip_calls[0][1:4] == ("-m", "pip", "install")


updater_run = auto_update._run


def test_local_changes_conflict_is_reported(repos):
    dev, local = repos
    push_change(dev, "README.md", "v2\n", "Sửa README")
    (local / "README.md").write_text("sửa tay\n", encoding="utf-8")
    with pytest.raises(auto_update.UpdateError):
        auto_update.update()


def test_unavailable_for_exe_and_non_git(tmp_path, monkeypatch):
    monkeypatch.setattr(auto_update, "is_frozen", lambda: True)
    assert "exe" in auto_update.unavailable_reason()
    monkeypatch.setattr(auto_update, "is_frozen", lambda: False)
    monkeypatch.setattr(auto_update, "PROJECT_ROOT", tmp_path)
    assert "git" in auto_update.unavailable_reason()
    with pytest.raises(auto_update.UpdateError):
        auto_update.update()
