# Graph Report - pylosSever  (2026-11-20)

## Corpus Check
- 231 files · ~162,945 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .woff2 9, (none) 5, .css 2)

## Summary
- 2836 nodes · 6515 edges · 211 communities (120 shown, 91 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 735 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `abef56cf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- JsonLinesFile
- handover_job.py
- test_assign_events.py
- event
- test_admin.py
- userdata_paths.py
- auto_update.py
- IncomingMessage
- ConfigError
- split_message
- test_desktop.py
- Envelope
- JsonObjectFile
- qr_login.py
- os
- Desktop
- test_model_calls.py
- message_handler.py
- admin_page.js
- create_app
- agent_tools/__init__.py
- handover.py
- Settings
- steps
- 4. Các bước
- test_media_fetch.py
- common.ps1
- pytest
- mention_tags.py
- test_personal.py
- json
- test_send_image.py
- PersonalZalo
- Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết
- Tasks: [FEATURE NAME]
- check_url
- Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc
- 3. Phần A — sửa code Python (`region_map.py`)
- speckit-analyze/SKILL.md
- command_line.py
- GroupStore
- test_web_reader.py
- test_config_client_webhook.py
- test_agent.py
- filter.py
- Turn
- AdminContext
- _is_network_error
- Kế hoạch: Server Bot Zalo chạy Agent (AI)
- GeminiAgent
- ZaloClient
- test_web_fallback.py
- admin_web_server.py
- json
- Bot
- ZaloError
- httpx
- steps
- test_handover.py
- test_vps_supervisor.py
- Natural chat as Lila
- incoming_message.py
- conftest.py
- test_paths.py
- windows_autostart.py
- discover
- FailedStore
- Execution Steps
- test_google_login.py
- README (Bot trợ lý Zalo Gemini)
- PromptBuilder
- test_filter.py
- Feature Specification: [FEATURE NAME]
- now_ms
- Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)
- check_secrets.py
- receive_webhook.py
- test_media_flow.py
- test_web_fixes.py
- Ba vai trò: basic-user, leader, owner
- ModelCalls
- fence/SYSTEM.md
- ImageAgent
- web_reader.py
- speckit-plan/SKILL.md
- 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)
- HistoryStore
- gateway (bot chạy nền)
- local
- SYSTEM.md
- zalo-assistant-bot
- 5. Phần C — kiểm thử
- test_transient_errors_are_retried_but_others_are_not
- AdminDevices
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- google_login.py
- DailyCounter
- pair
- ToolContext
- speckit-specify/SKILL.md
- speckit-tasks/SKILL.md
- Core Principles
- Core Principles
- 11. Kế hoạch: giao diện quản lý bot (web dashboard)
- PyloS — rules for Claude Code
- Implementation Plan: [FEATURE]
- Cách dùng bot trên Zalo
- test_regions_file.py
- speckit-checklist/SKILL.md
- settings_file.py
- P2. Đăng nhập Google riêng của PyloS
- speckit-clarify/SKILL.md
- speckit-implement/SKILL.md
- speckit-constitution/SKILL.md
- test_entrypoints.py
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- Model keys
- instructions.py
- backends
- test_bot_split.py
- _TextExtractor
- run_polling
- _log_path
- cdn
- test_system_commands_never_open_a_console_window
- ._turns
- Model shift: which kind of work is this, and which model runs it?
- _zalo_login
- test_tavily.py
- make_icon
- status
- re
- ActiveModelStore
- rate_limiter.py
- path_guard.py
- test_polling_delivers_updates_and_survives_errors
- _attach_parent_console
- test_desktop_bot_actions_report_to_tray
- .reply

## God Nodes (most connected - your core abstractions)
1. `Settings` - 102 edges
2. `create_app()` - 85 edges
3. `event()` - 79 edges
4. `send()` - 53 edges
5. `now_ms()` - 51 edges
6. `ToolContext` - 49 edges
7. `Bot` - 43 edges
8. `Desktop` - 37 edges
9. `Turn` - 36 edges
10. `main()` - 36 edges

## Surprising Connections (you probably didn't know these)
- `Hard rules` --references--> `migrate_to_city()`  [INFERRED]
  CLAUDE.md → src/pylos/lobby/dispatch/shared/userdata_paths.py
- `4b. Lưu trữ `.txt` và workspace `.md`` --references--> `seen()`  [INFERRED]
  src/pylos/management/managers/plans/PLAN.md → tests/management/owner/test_remote_proxy.py
- `W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng)` --references--> `web()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/conftest.py
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py

## Import Cycles
- None detected.

## Communities (211 total, 91 thin omitted)

### Community 0 - "JsonLinesFile"
Cohesion: 0.09
Nodes (13): MemoryDataStore, SeenStore, JsonLinesFile, memorydata(), test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist(), test_group_teams_and_leader_added_by(), test_instance_lock_blocks_second_instance() (+5 more)

### Community 1 - "handover_job.py"
Cohesion: 0.07
Nodes (40): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+32 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.06
Nodes (16): _describe(), FakeWeb, basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events() (+8 more)

### Community 3 - "event"
Cohesion: 0.11
Nodes (52): event(), send(), shift_bot(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks(), test_allow_all_off_by_default(), test_assign_allowed_all_still_opens_everyone(), test_bare_trigger_asks_what_to_do() (+44 more)

### Community 4 - "test_admin.py"
Cohesion: 0.05
Nodes (14): AdminSessions, client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx() (+6 more)

### Community 5 - "userdata_paths.py"
Cohesion: 0.11
Nodes (24): gui_running(), InstanceLock, app_home(), _backup_for_huts(), _backup_userdata(), _city_old_running(), _clean_env(), _locks_held() (+16 more)

### Community 6 - "auto_update.py"
Cohesion: 0.16
Nodes (18): _mark_good(), _rollback(), _find_uv(), _git(), hold_state(), install_libs(), last_good(), mark_good() (+10 more)

### Community 7 - "IncomingMessage"
Cohesion: 0.18
Nodes (3): Decision, MessageFilter, IncomingMessage

### Community 8 - "ConfigError"
Cohesion: 0.12
Nodes (17): load_session(), _bool(), ConfigError, _csv(), _int(), make_settings(), test_fallback_models_setting(), test_defaults_and_validation() (+9 more)

### Community 9 - "split_message"
Cohesion: 0.12
Nodes (19): _blocks(), _max_prefix(), _merge(), split_message(), split_reply(), to_plain_text(), utf16_len(), test_code_block_and_list_stay_together() (+11 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.11
Nodes (7): _free_port(), test_ensure_admin_token_writes_once(), test_env_template_keeps_data_inside_the_city(), test_free_port_skips_busy_port(), test_frozen_child_gets_its_own_unpack_dir(), test_logging_without_console(), test_no_visible_subprocess_calls_left_in_source()

### Community 11 - "Envelope"
Cohesion: 0.08
Nodes (18): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), a(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload() (+10 more)

### Community 12 - "JsonObjectFile"
Cohesion: 0.07
Nodes (16): ready(), ready(), today_vn(), _clean_map(), _clean_teams(), _mtime(), StateStore, StatsStore (+8 more)

### Community 13 - "qr_login.py"
Cohesion: 0.09
Nodes (14): apply_session(), Cancelled, cookies_for(), QrLogin, QrLoginError, QrStatus, ZaloSession, FakeResponse (+6 more)

### Community 14 - "os"
Cohesion: 0.18
Nodes (9): run_hidden(), code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state() (+1 more)

### Community 15 - "Desktop"
Cohesion: 0.12
Nodes (6): Desktop, watch(), work(), work(), update_flag_file(), run()

### Community 16 - "test_model_calls.py"
Cohesion: 0.07
Nodes (21): env_lookup(), KeyEntry, ModelCatalog, parse_keys(), _Raw, _split(), settings_lookup(), lookup() (+13 more)

### Community 17 - "message_handler.py"
Cohesion: 0.09
Nodes (9): hut_media_dir(), ZaloUnsupported, hut_file(), safe_name(), atomic_write_text(), _create(), ready(), OutgoingImage (+1 more)

### Community 18 - "admin_page.js"
Cohesion: 0.06
Nodes (92): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 4. Web (quanlythoigian), 5. Thứ tự đưa lên production (+84 more)

### Community 19 - "create_app"
Cohesion: 0.10
Nodes (31): create_app(), auth_options(), _base_url(), config_error(), devices(), _failed(), failed_action(), google_begin() (+23 more)

### Community 20 - "agent_tools/__init__.py"
Cohesion: 0.13
Nodes (9): Tool, ToolRegistry, test_gemini_classify_requests_json_and_counts_tokens(), test_tools_hidden_when_disabled(), make_agent(), test_function_calling_loop(), test_registry_owner_only_unknown_and_errors(), test_reply_sends_thinking_level() (+1 more)

### Community 21 - "handover.py"
Cohesion: 0.15
Nodes (13): backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip(), _sources() (+5 more)

### Community 22 - "Settings"
Cohesion: 0.11
Nodes (41): _admin(), _health(), main(), _update(), _utf8_console(), _zalo_call(), clear_pid(), clear_standby() (+33 more)

### Community 23 - "steps"
Cohesion: 0.06
Nodes (30): args, inputs, integration, spec, default, prompt, type, any (+22 more)

### Community 24 - "4. Các bước"
Cohesion: 0.15
Nodes (13): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+5 more)

### Community 25 - "test_media_fetch.py"
Cohesion: 0.10
Nodes (26): fetch_attachment(), Limits, MediaError, MediaFile, pick_mime(), sniff_mime(), MediaStore, _read_rows() (+18 more)

### Community 26 - "common.ps1"
Cohesion: 0.16
Nodes (19): Find-SpecifyRoot(), Format-SpecKitCommand(), Get-CurrentBranch(), Get-FeaturePathsEnv(), Get-InvokeSeparator(), Get-NormalizedPriority(), Get-Python3Command(), Get-RepoRoot() (+11 more)

### Community 27 - "pytest"
Cohesion: 0.25
Nodes (11): AccessDenied, city(), ok(), test_case_tricks_do_not_work_on_windows(), test_closed_places_are_refused_for_bots(), test_hut_only_for_the_person_being_served(), test_in_a_group_only_the_group_hut_is_open(), test_open_places_and_own_apartment_are_allowed() (+3 more)

### Community 28 - "mention_tags.py"
Cohesion: 0.18
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 29 - "test_personal.py"
Cohesion: 0.18
Nodes (10): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+2 more)

### Community 30 - "json"
Cohesion: 0.20
Nodes (9): attachment_of(), _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming(), _to_int(), test_text_unchanged() (+1 more)

### Community 31 - "test_send_image.py"
Cohesion: 0.18
Nodes (9): image_size(), ThreadType, ImageApi, jpeg(), png(), test_image_size_reads_png_and_jpeg_headers(), test_personal_send_image_unknown_format_and_errors(), test_personal_send_image_uses_real_size_caption_and_chat_type() (+1 more)

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 35 - "check_url"
Cohesion: 0.12
Nodes (6): check_url(), _forbidden(), fake_dns(), test_internal_or_odd_urls_are_blocked(), test_public_urls_are_allowed(), test_unresolvable_host_is_reported()

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.17
Nodes (12): 0. Luật đã chốt, 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa), 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại (+4 more)

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 38 - "speckit-analyze/SKILL.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 39 - "command_line.py"
Cohesion: 0.13
Nodes (7): _prepare_home(), setup_logging(), _message_box(), run_gui(), AlreadyRunning, ensure_admin_token(), ensure_home()

### Community 40 - "GroupStore"
Cohesion: 0.17
Nodes (3): GroupState, GroupStore, change()

### Community 41 - "test_web_reader.py"
Cohesion: 0.12
Nodes (24): html_response(), public_dns(), read(), search_call(), serve(), test_disabled_tool_cannot_be_called(), test_http_error_is_reported(), test_huge_page_is_cut_not_loaded_whole() (+16 more)

### Community 42 - "test_config_client_webhook.py"
Cohesion: 0.16
Nodes (5): RedactFilter, _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_redact_filter_hides_secrets()

### Community 43 - "test_agent.py"
Cohesion: 0.30
Nodes (18): api_error(), chain_agent(), keyed_agent(), PerModel, response(), test_classify_uses_fallback_models(), test_each_model_is_called_with_the_client_of_its_own_key(), test_empty_reply_falls_back() (+10 more)

### Community 44 - "filter.py"
Cohesion: 0.24
Nodes (3): BotContext, detect_category(), ensure_correct_model()

### Community 45 - "Turn"
Cohesion: 0.24
Nodes (14): Turn, FakeFiles, grounded(), make(), media_file(), test_expired_file_uri_uploads_again(), test_inline_budget_is_shared_across_turns(), test_large_photo_is_uploaded() (+6 more)

### Community 46 - "AdminContext"
Cohesion: 0.13
Nodes (6): AdminContext, client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 47 - "_is_network_error"
Cohesion: 0.22
Nodes (5): _is_network_error(), _fails_over(), _is_transient(), _rejects_thinking(), test_network_errors_are_detected_through_zlapi_wrapping()

### Community 48 - "Kế hoạch: Server Bot Zalo chạy Agent (AI)"
Cohesion: 0.11
Nodes (18): 0. Quyết định đã chốt, 10. Tiến độ, 1. Chọn kênh Zalo, 1a. Zalo Bot Platform: các sự kiện đã xác minh, 2. Kiến trúc, 3. Công nghệ, 3a. Nhận tin khi chạy local, chưa có domain, 3b. Chạy 24/7 khi chưa có VPS (+10 more)

### Community 49 - "GeminiAgent"
Cohesion: 0.12
Nodes (7): GeminiAgent, _usage_tokens(), FakeModels, test_search_uses_only_google_search_tool_and_returns_sources(), test_search_without_grounding_metadata(), test_a_client_given_directly_ignores_the_key_book(), test_watch_video_sends_youtube_uri_at_low_resolution()

### Community 51 - "test_web_fallback.py"
Cohesion: 0.16
Nodes (10): brave(), GroundingDownAgent, private(), QuotaError, test_brave_only_provider_never_calls_gemini(), test_gemini_only_provider_ignores_brave_key(), test_search_falls_back_to_brave_and_rests_gemini(), test_search_without_brave_key_explains_quota() (+2 more)

### Community 52 - "admin_web_server.py"
Cohesion: 0.06
Nodes (7): _as_dict(), make_imei(), now_vn(), _current_time(), write_workspace(), FieldSpec, ToolStep

### Community 53 - "json"
Cohesion: 0.43
Nodes (6): make(), test_link_card_becomes_text(), test_media_without_url_is_not_media(), test_photo_keeps_url_and_caption(), test_sticker_file_and_unknown_are_not_media(), test_voice_and_video()

### Community 55 - "ZaloError"
Cohesion: 0.12
Nodes (5): ZaloError, _import_zlapi(), send(), path(), flaky()

### Community 56 - "httpx"
Cohesion: 0.15
Nodes (16): ctx_for(), FakeCalls, ok_json(), provider(), test_cloudflare_accepts_a_raw_image_response(), test_cloudflare_errors_are_clear_and_never_leak_the_token(), test_cloudflare_sends_prompt_steps_and_token_and_decodes_base64(), handler() (+8 more)

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 58 - "test_handover.py"
Cohesion: 0.18
Nodes (14): make_side(), run_job(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_checks_data_layout_version(), test_import_endpoint_streams_and_refuses_running(), test_import_refused_while_bot_running(), test_import_rejects_non_bundle() (+6 more)

### Community 59 - "test_vps_supervisor.py"
Cohesion: 0.24
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 60 - "Natural chat as Lila"
Cohesion: 0.17
Nodes (11): Habits, Humor, Layout of each reply, Natural chat as Lila, Nox, Patterns (from Vietnamese news-site comments, Nov 2026), Real examples from this person (read these first), Rules (+3 more)

### Community 61 - "incoming_message.py"
Cohesion: 0.48
Nodes (3): parse_event(), parse_updates(), _to_ms()

### Community 62 - "conftest.py"
Cohesion: 0.09
Nodes (19): agent(), FakeAgent, FakeZalo, make_bot(), factory(), zalo(), test_bot_adds_missing_at_sign_end_to_end(), test_bot_tells_model_member_names() (+11 more)

### Community 63 - "test_paths.py"
Cohesion: 0.22
Nodes (10): legacy_home(), old_chat_data(), test_chat_data_moves_into_one_hut_per_person_or_group(), test_city_migration_keeps_what_is_already_in_the_new_place(), test_hut_migration_keeps_a_hut_file_that_already_exists(), test_migrates_everything_to_userdata(), test_migrates_userdata_into_the_city_with_a_backup_and_drops_the_old_workspace(), test_restores_git_tracked_defaults() (+2 more)

### Community 64 - "windows_autostart.py"
Cohesion: 0.09
Nodes (12): Tray, command(), is_enabled(), migrate(), set_enabled(), format_status(), _registry_autostart(), _spawn() (+4 more)

### Community 65 - "discover"
Cohesion: 0.14
Nodes (8): discover(), _load_external(), playground(), tools(), EchoAgent, test_external_tools_are_loaded_and_broken_ones_skipped(), test_tools_list_has_only_builtin_tools_by_default(), test_discover_skips_example_template()

### Community 66 - "FailedStore"
Cohesion: 0.18
Nodes (5): FailedStore, change(), change(), done_file(), test_failed_list_and_dismiss()

### Community 67 - "Execution Steps"
Cohesion: 0.12
Nodes (15): 1. Initialize Convergence Context, 2. Load Artifacts (Progressive Disclosure), 3. Build the Intent Inventory, 4. Assess the Codebase and Classify Findings, 5. Assign Severity, 6. Present the In-Session Findings Summary, 7. Append Convergence Tasks (or report converged), 8. Provide Next Actions (Handoff) (+7 more)

### Community 68 - "test_google_login.py"
Cohesion: 0.15
Nodes (14): approve(), fake_google(), exchange(), id_token(), make_client(), test_bad_state_expired_code_and_invalid_tokens(), test_connect_vps_with_google_saves_key_without_showing_it(), test_default_remote_url_and_off() (+6 more)

### Community 69 - "README (Bot trợ lý Zalo Gemini)"
Cohesion: 0.13
Nodes (14): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+6 more)

### Community 70 - "PromptBuilder"
Cohesion: 0.13
Nodes (9): _CachedFile, PromptBuilder, test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role(), build(), test_prompt_picks_up_a_new_file_and_falls_back_without_system(), test_prompt_reads_every_document_in_the_workspace() (+1 more)

### Community 71 - "test_filter.py"
Cohesion: 0.18
Nodes (27): agent(), decide(), decide_with(), _gemini(), make_filter(), factory(), msg(), _Ok (+19 more)

### Community 72 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 76 - "now_ms"
Cohesion: 0.14
Nodes (10): _build_agent(), _console(), ConsoleZalo, _run(), request_stop(), watch_stop_flag(), ago(), now_ms() (+2 more)

### Community 77 - "Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)"
Cohesion: 0.13
Nodes (13): Cấu hình `settings.env` (máy Windows và VPS), Lỗi thường gặp, Tạo OAuth client (một lần, ~10 phút), Đăng nhập trang quản lý PyloS bằng Google, 1. Service cho bot, 2. Cho user `pylos` điều khiển đúng 2 service (chọn MỘT cách), 3. Bật chế độ systemd cho bot trên VPS, 4. nginx (+5 more)

### Community 78 - "check_secrets.py"
Cohesion: 0.43
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 80 - "receive_webhook.py"
Cohesion: 0.22
Nodes (6): create_app(), health(), webhook(), 4b. Lưu trữ `.txt` và workspace `.md`, history(), test_webhook_checks_secret_and_forwards_payload()

### Community 82 - "test_media_flow.py"
Cohesion: 0.13
Nodes (26): media_msg(), push(), SearchingAgent, test_download_failure_gets_notice(), test_followup_disabled_by_zero_turns(), test_followup_reattaches_recent_media_only(), test_group_caption_with_trigger_passes(), test_group_media_from_someone_else_after_call_is_ignored() (+18 more)

### Community 84 - "test_web_fixes.py"
Cohesion: 0.18
Nodes (14): oembed(), public_dns(), read(), serve(), test_blocked_site_gets_clear_message(), test_brave_search_errors(), test_brave_search_parses_results(), test_user_agent_carries_contact_only_when_set() (+6 more)

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "ModelCalls"
Cohesion: 0.10
Nodes (9): ModelCalls, CloudflareProvider, ImageResult, ModelCallError, sniff_image_mime(), calls(), test_generate_image_reports_models_without_a_key_or_without_image_support(), test_generate_image_tries_fallbacks_only_for_retryable_errors() (+1 more)

### Community 93 - "fence/SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 94 - "ImageAgent"
Cohesion: 0.21
Nodes (8): image_bot(), ImageAgent, ImageZalo, pictures(), test_generated_images_are_sent_before_the_text_and_counted(), test_image_send_failure_is_retried_dead_lettered_and_the_user_is_told(), test_replies_without_images_are_unchanged(), test_zalo_without_image_support_gets_a_clear_notice_without_retries()

### Community 98 - "web_reader.py"
Cohesion: 0.08
Nodes (16): is_chatter(), brave_search(), configure(), extract_basic(), extract_main(), fetch_page(), FetchError, _read_page() (+8 more)

### Community 99 - "speckit-plan/SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, Key rules, Mandatory Post-Execution Hooks, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases (+2 more)

### Community 101 - "12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)"
Cohesion: 0.17
Nodes (12): 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu, 12.2 Chọn cách làm, 12.3 Kiến trúc, 12.4 Biểu tượng khay (system tray), 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được, 12.6 Đóng gói (+4 more)

### Community 103 - "HistoryStore"
Cohesion: 0.21
Nodes (5): HistoryStore, 11.5 Bảo mật (quan trọng nhất của phần này), clear_history(), test_history_tail_trim_and_safe_filename(), test_history_view_and_toggle()

### Community 105 - "local"
Cohesion: 0.22
Nodes (6): clean_env(), local(), no_web(), test_exchange_uses_pkce_and_checks_audience(), handler(), run()

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 122 - "google_login.py"
Cohesion: 0.18
Nodes (5): auth_url(), challenge(), decode_id_token(), exchange(), PendingLogins

### Community 128 - "DailyCounter"
Cohesion: 0.21
Nodes (6): ImageLimit, DailyCounter, configure(), ImageConfig, test_image_limit_per_day_and_per_user_hour(), test_image_limit_zero_means_unlimited_and_failed_runs_cost_nothing()

### Community 129 - "pair"
Cohesion: 0.22
Nodes (3): clean_env(), pair(), running()

### Community 134 - "ToolContext"
Cohesion: 0.06
Nodes (53): fold(), base_url(), configured(), env_values(), request(), server_config(), CommandHandler, describe_mode() (+45 more)

### Community 145 - "speckit-specify/SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, For AI Generation, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, Quick Guidelines, Section Requirements (+2 more)

### Community 157 - "speckit-tasks/SKILL.md"
Cohesion: 0.18
Nodes (10): Checklist Format (REQUIRED), Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Phase Structure, Pre-Execution Checks, Task Generation Rules (+2 more)

### Community 158 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Governance, [PRINCIPLE_1_NAME], [PRINCIPLE_2_NAME], [PRINCIPLE_3_NAME], [PRINCIPLE_4_NAME], [PRINCIPLE_5_NAME], [PROJECT_NAME] Constitution (+2 more)

### Community 159 - "Core Principles"
Cohesion: 0.18
Nodes (10): Core Principles, Governance, [PRINCIPLE_1_NAME], [PRINCIPLE_2_NAME], [PRINCIPLE_3_NAME], [PRINCIPLE_4_NAME], [PRINCIPLE_5_NAME], [PROJECT_NAME] Constitution (+2 more)

### Community 160 - "11. Kế hoạch: giao diện quản lý bot (web dashboard)"
Cohesion: 0.18
Nodes (11): 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22), 11.1 Mục tiêu, 11.2 Kiến trúc, 11.3 Các trang, 11.4 API (JSON, dưới `/api`), 11.6 Việc phải bổ sung vào bot hiện có, 11.7 Thư mục dự kiến (+3 more)

### Community 161 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 162 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 163 - "Cách dùng bot trên Zalo"
Cohesion: 0.25
Nodes (8): Ba vai trò, Các file trong thư mục này, Cách dùng bot trên Zalo, Giao lịch cho người khác (web iforgotmywayhome), Gọi bot ở chế độ default, Hạn mức token, Lấy ID của bạn lần đầu, Lệnh

### Community 164 - "test_regions_file.py"
Cohesion: 0.28
Nodes (4): B6. Phía PyloS, region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions()

### Community 165 - "speckit-checklist/SKILL.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 166 - "settings_file.py"
Cohesion: 0.23
Nodes (9): read_settings(), remote_login_poll(), remote_logout(), write_secret(), write_settings(), clean_value(), read_values(), update() (+1 more)

### Community 167 - "P2. Đăng nhập Google riêng của PyloS"
Cohesion: 0.33
Nodes (4): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối

### Community 168 - "speckit-clarify/SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 170 - "speckit-implement/SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 171 - "speckit-constitution/SKILL.md"
Cohesion: 0.33
Nodes (5): Outline, Post-Execution Checks, Pre-Execution Checks, Scope Guard, User Input

### Community 172 - "test_entrypoints.py"
Cohesion: 0.10
Nodes (11): folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports(), test_console_script_targets_exist(), test_every_module_imports(), test_every_top_level_package_is_bundled_into_the_exe(), test_exe_bundles_every_package_data_pattern_of_pylos() (+3 more)

### Community 173 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 174 - "Model keys"
Cohesion: 0.50
Nodes (3): cloudflare-main, gemini-main, Model keys

### Community 176 - "instructions.py"
Cohesion: 0.12
Nodes (12): _fallbacks(), FilterInstructions, parse_profiles(), parse_tasks(), Profile, TaskModel, test_shipped_model_shift_has_the_image_task_and_still_all_profiles(), test_tasks_fall_back_to_defaults_when_missing_or_broken() (+4 more)

### Community 178 - "test_bot_split.py"
Cohesion: 0.43
Nodes (5): send(), test_failed_part_stops_and_keeps_the_rest(), test_multiline_reply_goes_as_separate_messages(), test_reply_split_off_sends_one_message(), test_two_sends_to_one_chat_do_not_interleave()

### Community 181 - "_log_path"
Cohesion: 0.50
Nodes (4): _log_path(), logs(), stream_logs(), tail()

### Community 187 - "Model shift: which kind of work is this, and which model runs it?"
Cohesion: 0.29
Nodes (6): How to choose (your job), Keep or switch, Model shift: which kind of work is this, and which model runs it?, Profile table (read by the code), Task models (read by the code), Things you do not decide

### Community 188 - "_zalo_login"
Cohesion: 1.00
Nodes (3): _zalo_login(), on_update(), save_qr_png()

### Community 189 - "test_tavily.py"
Cohesion: 0.23
Nodes (6): fresh_config(), serve(), test_tavily_errors(), test_tavily_network_error(), test_tavily_sends_bearer_key_and_parses_results(), test_tavily_without_answer_has_no_answer_key()

### Community 192 - "make_icon"
Cohesion: 0.22
Nodes (3): make_icon(), write_ico(), test_icons()

### Community 193 - "status"
Cohesion: 0.67
Nodes (3): body(), status(), handler()

### Community 197 - "path_guard.py"
Cohesion: 0.43
Nodes (3): Actor, check_access(), _inside()

### Community 203 - ".reply"
Cohesion: 0.14
Nodes (10): Agent, AgentReply, done(), test_reply_drops_thinking_when_model_rejects_it(), generate_content(), test_reply_retries_once_on_timeout(), generate_content(), test_transient_errors_are_retried_but_others_are_not() (+2 more)

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1058 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **91 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `JsonLinesFile`, `handover_job.py`, `userdata_paths.py`, `auto_update.py`, `IncomingMessage`, `ConfigError`, `os`, `Desktop`, `message_handler.py`, `create_app`, `handover.py`, `11. Kế hoạch: giao diện quản lý bot (web dashboard)`, `settings_file.py`, `command_line.py`, `P2. Đăng nhập Google riêng của PyloS`, `AdminContext`, `admin_web_server.py`, `test_handover.py`, `test_vps_supervisor.py`, `_zalo_login`, `test_paths.py`, `windows_autostart.py`, `rate_limiter.py`, `test_google_login.py`, `now_ms`, `web_reader.py`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 77 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `JsonLinesFile` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._
- **Why does `create_app()` connect `create_app` to `JsonLinesFile`, `handover_job.py`, `pair`, `test_admin.py`, `auto_update.py`, `ConfigError`, `split_message`, `test_model_calls.py`, `handover.py`, `Settings`, `settings_file.py`, `command_line.py`, `AdminContext`, `admin_web_server.py`, `_log_path`, `test_handover.py`, `test_vps_supervisor.py`, `windows_autostart.py`, `discover`, `status`, `test_google_login.py`, `now_ms`, `receive_webhook.py`, `ModelCalls`, `HistoryStore`, `local`, `AdminDevices`, `google_login.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07219662058371736 - nodes in this community are weakly interconnected._