from __future__ import annotations

from bot.storage import GroupStore, HistoryStore, JsonLinesFile, JsonObjectFile, SeenStore, UsageStore
from bot.storage.process_lock import AlreadyRunning, InstanceLock

import pytest


def test_jsonl_skips_broken_lines(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text('{"a": 1}\n{"b": 2\n[1,2]\n\n{"c": "tiếng Việt"}\n', encoding="utf-8")
    assert JsonLinesFile(path).read_all() == [{"a": 1}, {"c": "tiếng Việt"}]


def test_jsonl_append_rewrite_and_utf8(tmp_path):
    f = JsonLinesFile(tmp_path / "sub" / "x.txt")
    f.append({"text": "xin chào"})
    f.append({"text": "tạm biệt"})
    assert "xin chào" in f.path.read_text(encoding="utf-8")
    f.rewrite([{"n": 1}])
    assert f.read_all() == [{"n": 1}]
    assert not (tmp_path / "sub" / "x.txt.tmp").exists()


def test_lone_surrogate_does_not_crash_write(tmp_path):
    f = JsonLinesFile(tmp_path / "x.txt")
    f.append({"text": "a\udc8fb"})
    f.rewrite([{"text": "c\udc8fd"}])
    assert f.read_all() == [{"text": "c?d"}]


def test_object_file_recovers_from_corruption(tmp_path):
    path = tmp_path / "bot_status.txt"
    path.write_text("{not json", encoding="utf-8")
    store = JsonObjectFile(path)
    assert store.read() == {}
    store.write({"k": "v"})
    assert store.read() == {"k": "v"}


def test_group_store_seed_and_persist(tmp_path):
    path = tmp_path / "group_settings.txt"
    store = GroupStore(path, seed_allowed=("g1",))
    assert store.get("g1").allowed and store.get("g1").mode == "default"
    assert not store.get("g2").allowed
    store.set_mode("g1", "all")
    store.set_allowed("g2", True)
    again = GroupStore(path)
    assert again.get("g1").mode == "all" and again.get("g2").allowed
    with pytest.raises(ValueError):
        store.set_mode("g1", "loud")


def test_seen_store_is_bounded_and_persistent(tmp_path):
    path = tmp_path / "processed_message_ids.txt"
    store = SeenStore(path, keep=3)
    for key in "abcde":
        store.add(key)
    assert "a" not in store and "b" not in store and "e" in store
    assert JsonLinesFile(path).count_lines() <= 6
    again = SeenStore(path, keep=3)
    assert "e" in again and "c" in again and "a" not in again


def test_history_tail_trim_and_safe_filename(tmp_path):
    store = HistoryStore(tmp_path / "session_history", keep=5)
    for i in range(12):
        store.append("../evil/chat", "user", str(i))
    files = list((tmp_path / "session_history").iterdir())
    assert len(files) == 1 and files[0].parent == tmp_path / "session_history"
    assert [r["text"] for r in store.recent("../evil/chat", 3)] == ["9", "10", "11"]
    assert JsonLinesFile(files[0]).count_lines() <= 10


def test_usage_store_rolls_over_by_day(tmp_path):
    path = tmp_path / "token_usage.txt"
    JsonObjectFile(path).write({"day": "2000-01-01", "tokens": 999, "notified": ["g"]})
    usage = UsageStore(path)
    assert usage.used_today() == 0
    assert usage.add(5) == 5
    assert usage.mark_notified("g") and not usage.mark_notified("g")


def test_usage_store_shared_between_processes(tmp_path):
    a, b = UsageStore(tmp_path / "token_usage.txt"), UsageStore(tmp_path / "token_usage.txt")
    a.add(10)
    b.add(5)
    assert a.used_today() == 15


def test_stats_activity_and_failed_stores(tmp_path):
    from bot.storage import ActivityStore, FailedStore, StatsStore

    stats = StatsStore(tmp_path / "daily_stats.txt")
    stats.incr("received")
    stats.incr("tokens", 30)
    stats.incr("bogus")
    assert stats.today() == {"received": 1, "replied": 0, "errors": 0, "tokens": 30, "filter_pass": 0, "filter_block": 0}
    assert stats.days(14)[-1]["tokens"] == 30

    activity = ActivityStore(tmp_path / "chat_activity.txt")
    activity.touch("g1", "GROUP", "An")
    assert activity.all()["g1"]["last_name"] == "An"

    (tmp_path / "failed_replies.txt").write_text('{"chat_id": "old", "text": "cũ", "t": 1}\n', encoding="utf-8")
    failed = FailedStore(tmp_path / "failed_replies.txt")
    failed.add("g1", "mới", "err")
    items = failed.pending()
    assert [i["chat_id"] for i in items] == ["old", "g1"]
    failed.mark_done(items[0]["id"], "dismissed")
    assert [i["chat_id"] for i in failed.pending()] == ["g1"]


def test_instance_lock_blocks_second_instance(tmp_path):
    first = InstanceLock(tmp_path / "bot.lock")
    first.acquire()
    try:
        with pytest.raises(AlreadyRunning):
            InstanceLock(tmp_path / "bot.lock").acquire()
    finally:
        first.release()
    with InstanceLock(tmp_path / "bot.lock"):
        pass
