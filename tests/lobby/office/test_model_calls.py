"""Danh sách key -> model (lobby/office/model_calls) và nhiệm vụ trong modelShift.md."""

import logging
from types import SimpleNamespace

from pylos.lobby.office.model_calls import ModelCalls, settings_lookup
from pylos.lobby.office.model_calls.catalog import KEYS_FILE, ModelCatalog, parse_keys
from pylos.lobby.office.model_calls.providers import PROVIDERS
from pylos.lobby.office.model_calls.providers.gemini import GeminiProvider
from pylos.residential.residents.filter.instructions import (
    DEFAULT_PROFILES, DEFAULT_TASKS, FilterInstructions, parse_profiles, parse_tasks,
)

FILE = """<!-- ghi chú -->
# Model keys

## main
provider: gemini
key: KEY_A
models: m1, m2

## backup
provider: gemini
key: KEY_B
models: m3

## cf
provider: cloudflare
key: CF_TOKEN
account: CF_ACCOUNT
models: @cf/flux
"""
ENV = {"KEY_A": "secret-a", "KEY_B": "secret-b", "CF_TOKEN": "cf-secret", "CF_ACCOUNT": "acc-1"}


def catalog(tmp_path, text=FILE, env=None):
    path = tmp_path / "model_keys.md"
    path.write_text(text, encoding="utf-8")
    values = ENV if env is None else env
    return ModelCatalog(path, lambda name: values.get(name, ""), known_providers=set(PROVIDERS))


def test_resolve_gives_key_provider_and_extra_variables(tmp_path):
    cat = catalog(tmp_path)
    assert cat.resolve("m1").name == "main" and cat.resolve("m1").secret == "secret-a"
    assert cat.resolve("m3").secret == "secret-b"
    flux = cat.resolve("@cf/flux")
    assert flux.provider == "cloudflare" and flux.secret == "cf-secret" and flux.extras == {"account": "acc-1"}
    assert cat.resolve("không-có") is None


def test_bad_entries_are_skipped_with_a_warning_and_never_print_secrets(tmp_path, caplog):
    text = FILE + "\n## broken\nprovider: gemini\nmodels: x\n\n## alien\nprovider: openai\nkey: KEY_A\nmodels: y\n"
    with caplog.at_level(logging.WARNING):
        cat = catalog(tmp_path, text)
        assert cat.resolve("x") is None and cat.resolve("y") is None and cat.resolve("m1") is not None
    assert "broken" in caplog.text and "openai" in caplog.text
    assert "secret-a" not in caplog.text


def test_key_with_unset_variable_is_unusable_and_warns_once(tmp_path, caplog):
    cat = catalog(tmp_path, env={"KEY_A": "secret-a"})  # thiếu CF_TOKEN, CF_ACCOUNT, KEY_B
    with caplog.at_level(logging.WARNING):
        assert cat.resolve("@cf/flux") is None and cat.resolve("@cf/flux") is None
    assert caplog.text.count("chưa dùng được") == 1 and "CF_TOKEN" in caplog.text
    assert cat.resolve("m1") is not None


def test_model_in_two_keys_uses_the_first(tmp_path, caplog):
    text = FILE + "\n## dup\nprovider: gemini\nkey: KEY_B\nmodels: m1\n"
    with caplog.at_level(logging.WARNING):
        assert catalog(tmp_path, text).resolve("m1").name == "main"
    assert "m1" in caplog.text


def test_catalog_reloads_when_the_file_changes(tmp_path):
    import os

    cat = catalog(tmp_path)
    assert cat.resolve("m9") is None
    cat.path.write_text(FILE + "\n## more\nprovider: gemini\nkey: KEY_B\nmodels: m9\n", encoding="utf-8")
    stat = cat.path.stat()
    os.utime(cat.path, (stat.st_atime, stat.st_mtime + 5))
    assert cat.resolve("m9").name == "more"


def test_missing_file_means_every_model_uses_the_default_key(tmp_path):
    cat = ModelCatalog(tmp_path / "nope.md", lambda name: "x")
    assert cat.resolve("gemini-anything") is None and cat.entries() == []


def test_entries_for_the_admin_page_hold_no_secret_values(tmp_path):
    entries = catalog(tmp_path, env={"KEY_A": "secret-a"}).entries()
    assert {e["name"]: e["ready"] for e in entries} == {"main": True, "backup": False, "cf": False}
    assert "secret-a" not in str(entries)
    assert entries[0]["key"] == "KEY_A" and entries[0]["models"] == ["m1", "m2"]


def test_shipped_model_keys_file_parses_and_lists_the_image_models():
    entries = parse_keys(KEYS_FILE.read_text(encoding="utf-8"), set(PROVIDERS))
    by_name = {e.name: e for e in entries}
    assert by_name["gemini-main"].secret_var == "GEMINI_API_KEY"
    assert "gemini-4-hydrogen" in by_name["gemini-main"].models
    assert {"@cf/black-forest-labs/flux-1-schnell", "@cf/leonardo/phoenix-1.0"} <= set(by_name["cloudflare-main"].models)


def test_gemini_provider_keeps_one_client_per_key_and_renews_it_when_the_key_changes(tmp_path):
    made = []
    provider = GeminiProvider(factory=lambda secret: made.append(secret) or object())
    cat = catalog(tmp_path)
    a1, a2 = provider.client_for(cat.resolve("m1")), provider.client_for(cat.resolve("m2"))
    b = provider.client_for(cat.resolve("m3"))
    assert a1 is a2 and a1 is not b and made == ["secret-a", "secret-b"]
    cat.lookup = lambda name: {**ENV, "KEY_A": "rotated"}.get(name, "")
    assert provider.client_for(cat.resolve("m1")) is not a1 and made[-1] == "rotated"


def test_model_calls_routes_models_to_their_key(tmp_path):
    calls = ModelCalls(lambda name: ENV.get(name, ""), tmp_path / "missing.md")
    calls.catalog.path.write_text(FILE, encoding="utf-8")
    calls._providers["gemini"] = GeminiProvider(factory=lambda secret: f"client:{secret}")
    assert calls.gemini_client("m1") == "client:secret-a" and calls.gemini_client("m3") == "client:secret-b"
    assert calls.gemini_client("@cf/flux") is None and calls.gemini_client("không-có") is None
    assert calls.provider_of("@cf/flux") == "cloudflare" and calls.provider_of("không-có") is None


def test_settings_lookup_prefers_running_settings_then_environment(monkeypatch):
    monkeypatch.setenv("EXTRA_KEY", "from-env")
    monkeypatch.setenv("GEMINI_API_KEY", "stale-env")
    settings = SimpleNamespace(gemini_api_key=" live ", cloudflare_api_token="cf", cloudflare_account_id="acc")
    lookup = settings_lookup(settings)
    assert lookup("GEMINI_API_KEY") == "live" and lookup("CLOUDFLARE_API_TOKEN") == "cf"
    assert lookup("CLOUDFLARE_ACCOUNT_ID") == "acc" and lookup("EXTRA_KEY") == "from-env" and lookup("NOPE") == ""


# ---------- bảng nhiệm vụ trong modelShift.md ----------

TABLES = """
| profile | model | thinking | fallbacks |
|---------|-------|----------|-----------|
| routine | m-a   | low      | m-b       |

| task  | model        | fallbacks |
|-------|--------------|-----------|
| image | @cf/other    | @cf/fb, - |
"""


def test_tasks_table_is_read_and_does_not_disturb_the_profile_table():
    tasks = parse_tasks(TABLES)
    assert tasks["image"].model == "@cf/other" and tasks["image"].fallbacks == ("@cf/fb",)
    profiles = parse_profiles(TABLES)
    assert profiles["routine"].model == "m-a" and profiles["coding"] == DEFAULT_PROFILES["coding"]


def test_tasks_fall_back_to_defaults_when_missing_or_broken():
    assert parse_tasks("") == DEFAULT_TASKS
    assert parse_tasks("| image | - | - |") == DEFAULT_TASKS
    assert parse_tasks("| image |  | |") == DEFAULT_TASKS


def test_shipped_model_shift_has_the_image_task_and_still_all_profiles():
    from pylos.lobby.dispatch.shared.userdata_paths import FILTER_WORKSPACE_REL
    from pylos.lobby.dispatch.shared.config import PROJECT_ROOT

    inst = FilterInstructions(PROJECT_ROOT / FILTER_WORKSPACE_REL)
    assert inst.tasks()["image"].model == "@cf/black-forest-labs/flux-1-schnell"
    assert inst.profiles()["coding"].model == "gemini-4-hydrogen"
