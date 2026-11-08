# Graph Report - pylosSever  (2026-11-08)

## Corpus Check
- 162 files · ~105,653 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 9, (none) 4, .css 2)

## Summary
- 1902 nodes · 4473 edges · 165 communities (78 shown, 87 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 517 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a4d03048`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- FailedStore
- handover_job.py
- test_assign_events.py
- event
- test_admin.py
- InstanceLock
- auto_update.py
- Bot
- MemoryDataStore
- server_info.py
- test_desktop.py
- Envelope
- UsageStore
- qr_login.py
- PyloS — rules for Claude Code
- settings_file.py
- handover.py
- test_storage.py
- admin_page.js
- create_app
- agent_tools/__init__.py
- test_handover.py
- Settings
- re
- 4. Các bước
- json
- ZaloClient
- pytest
- storage.py
- test_personal.py
- Kế hoạch: Server Bot Zalo chạy Agent (AI)
- conftest.py
- PersonalZalo
- Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết
- owner_commands.py
- personal_account.py
- Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc
- 3. Phần A — sửa code Python (`region_map.py`)
- Desktop
- Settings
- GroupStore
- test_filter.py
- command_line.py
- admin_web_server.py
- residents/pylos/__init__.py
- HistoryStore
- Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)
- make_settings
- .classify
- test_regions_file.py
- Turn
- FakeWeb
- google_begin
- pathlib
- status_info
- steps
- admin_web_server.py
- README (Bot trợ lý Zalo Gemini)
- zalo/__init__.py
- _log_path
- 4. Web (quanlythoigian)
- test_remote_proxy.py
- AdminSessions
- test_google_login.py
- AdminDevices
- clock/vietnam_time.py
- .decide
- local
- pair
- test_config_client_webhook.py
- test_schedule_tool.py
- ZaloSender
- Ba vai trò: basic-user, leader, owner
- 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)
- test_vps_supervisor.py
- zalo/__init__.py
- Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động
- roles.py
- ._process
- clock/vietnam_time.py
- gateway (bot chạy nền)
- Cách dùng bot trên Zalo
- SYSTEM.md
- zalo-assistant-bot
- AdminContext
- 5. Phần C — kiểm thử
- _error
- .login
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- 4b. Lưu trữ `.txt` và workspace `.md`
- _is_network_error
- test_zalo_qr_login_saves_session_and_enables_personal
- ToolContext
- run_polling
- test_gemini_classify_requests_json_and_counts_tokens
- test_polling_delivers_updates_and_survives_errors
- .generate_content
- split_message

## God Nodes (most connected - your core abstractions)
1. `Settings` - 103 edges
2. `create_app()` - 86 edges
3. `event()` - 53 edges
4. `now_ms()` - 44 edges
5. `send()` - 42 edges
6. `ToolContext` - 40 edges
7. `main()` - 36 edges
8. `GroupStore` - 34 edges
9. `Desktop` - 33 edges
10. `Bot` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Hard rules` --references--> `migrate_to_city()`  [INFERRED]
  CLAUDE.md → src/pylos/lobby/dispatch/shared/userdata_paths.py
- `4b. Lưu trữ `.txt` và workspace `.md`` --references--> `seen()`  [INFERRED]
  src/pylos/management/managers/plans/PLAN.md → tests/management/owner/test_remote_proxy.py
- `W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng)` --references--> `web()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/conftest.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py

## Import Cycles
- None detected.

## Communities (165 total, 87 thin omitted)

### Community 0 - "FailedStore"
Cohesion: 0.13
Nodes (7): FailedStore, change(), change(), done_file(), _failed(), test_stats_activity_and_failed_stores(), test_failed_list_and_dismiss()

### Community 1 - "handover_job.py"
Cohesion: 0.07
Nodes (41): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+33 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.21
Nodes (12): basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team(), test_list_shows_who_has_it_in_their_app() (+4 more)

### Community 3 - "event"
Cohesion: 0.10
Nodes (49): event(), lines(), send(), test_every_message_logged_but_only_passed_ones_reach_session(), test_not_allowed_chat_is_not_logged(), send(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks() (+41 more)

### Community 4 - "test_admin.py"
Cohesion: 0.08
Nodes (7): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders(), test_page_and_every_asset_it_links_are_served(), test_settings_rejects_bad_or_forbidden_values()

### Community 5 - "InstanceLock"
Cohesion: 0.11
Nodes (19): gui_running(), AlreadyRunning, InstanceLock, app_home(), _backup_userdata(), _city_old_running(), _clean_env(), migrate_all() (+11 more)

### Community 6 - "auto_update.py"
Cohesion: 0.17
Nodes (17): _rollback(), _find_uv(), _git(), hold_state(), install_libs(), last_good(), mark_good(), pending_commits() (+9 more)

### Community 7 - "Bot"
Cohesion: 0.16
Nodes (3): _console(), Bot, test_tagging_personal_account_answers_and_strips_tag()

### Community 8 - "MemoryDataStore"
Cohesion: 0.19
Nodes (6): _clean_map(), _clean_teams(), MemoryDataStore, memorydata(), test_store_trims_when_over_keep(), test_memorydata_api_shows_filter_result_and_respects_history_switch()

### Community 9 - "server_info.py"
Cohesion: 0.15
Nodes (9): code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state(), _uptime_seconds() (+1 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.09
Nodes (8): _free_port(), test_autostart_registry_roundtrip(), test_env_template_keeps_data_inside_the_city(), test_external_tools_are_loaded_and_broken_ones_skipped(), test_free_port_skips_busy_port(), test_frozen_child_gets_its_own_unpack_dir(), test_no_visible_subprocess_calls_left_in_source(), test_system_commands_never_open_a_console_window()

### Community 11 - "Envelope"
Cohesion: 0.07
Nodes (18): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), a(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload() (+10 more)

### Community 12 - "UsageStore"
Cohesion: 0.11
Nodes (8): today_vn(), StatsStore, UsageStore, JsonObjectFile, test_object_file_recovers_from_corruption(), test_usage_store_rolls_over_by_day(), test_groups_list_includes_seen_but_not_allowed_chats(), test_status_reports_alerts_and_stats()

### Community 13 - "qr_login.py"
Cohesion: 0.06
Nodes (23): _zalo_login(), on_update(), apply_session(), Cancelled, cookies_for(), make_imei(), QrLogin, QrLoginError (+15 more)

### Community 14 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 15 - "settings_file.py"
Cohesion: 0.19
Nodes (9): read_settings(), remote_logout(), write_secret(), write_settings(), clean_value(), FieldSpec, read_values(), update() (+1 more)

### Community 16 - "handover.py"
Cohesion: 0.18
Nodes (12): backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip(), _sources() (+4 more)

### Community 17 - "test_storage.py"
Cohesion: 0.14
Nodes (11): SeenStore, JsonLinesFile, test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist(), test_group_teams_and_leader_added_by(), test_history_tail_trim_and_safe_filename(), test_jsonl_append_rewrite_and_utf8(), test_jsonl_skips_broken_lines() (+3 more)

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (72): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+64 more)

### Community 19 - "create_app"
Cohesion: 0.16
Nodes (19): create_app(), devices(), google_poll(), _groups(), guard(), handover_clear_standby(), handover_export(), list_devices() (+11 more)

### Community 20 - "agent_tools/__init__.py"
Cohesion: 0.18
Nodes (5): discover(), _load_external(), tools(), test_tools_list_has_only_builtin_tools_by_default(), test_discover_skips_example_template()

### Community 21 - "test_handover.py"
Cohesion: 0.15
Nodes (14): make_side(), run_job(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_checks_data_layout_version(), test_import_endpoint_streams_and_refuses_running(), test_import_refused_while_bot_running(), test_import_rejects_non_bundle() (+6 more)

### Community 22 - "Settings"
Cohesion: 0.10
Nodes (37): _admin(), _mark_good(), _update(), clear_pid(), clear_standby(), _end_task(), follow_log(), is_running() (+29 more)

### Community 23 - "re"
Cohesion: 0.16
Nodes (4): is_chatter(), strip_name_prefix(), test_bot_never_calls_web_on_plain_message(), test_server_client_paths_are_only_scheduling_paths()

### Community 24 - "4. Các bước"
Cohesion: 0.15
Nodes (13): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+5 more)

### Community 25 - "json"
Cohesion: 0.22
Nodes (9): legacy_home(), test_city_migration_keeps_what_is_already_in_the_new_place(), test_city_migration_waits_for_the_old_version(), test_migrates_everything_to_userdata(), test_migrates_userdata_into_the_city_with_a_backup_and_drops_the_old_workspace(), test_restores_git_tracked_defaults(), test_settings_read_migrated_env(), test_skips_while_old_version_still_running() (+1 more)

### Community 27 - "pytest"
Cohesion: 0.06
Nodes (29): check_dir(), check_exe(), main(), secrets_from_env(), AccessDenied, Actor, check_access(), _inside() (+21 more)

### Community 29 - "test_personal.py"
Cohesion: 0.12
Nodes (12): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+4 more)

### Community 30 - "Kế hoạch: Server Bot Zalo chạy Agent (AI)"
Cohesion: 0.12
Nodes (16): 0. Quyết định đã chốt, 10. Tiến độ, 1. Chọn kênh Zalo, 1a. Zalo Bot Platform: các sự kiện đã xác minh, 2. Kiến trúc, 3. Công nghệ, 3a. Nhận tin khi chạy local, chưa có domain, 3b. Chạy 24/7 khi chưa có VPS (+8 more)

### Community 31 - "conftest.py"
Cohesion: 0.27
Nodes (7): agent(), FakeAgent, FakeZalo, make_bot(), factory(), web(), zalo()

### Community 32 - "PersonalZalo"
Cohesion: 0.09
Nodes (13): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+5 more)

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "owner_commands.py"
Cohesion: 0.19
Nodes (9): IncomingMessage, CommandHandler, describe_mode(), help_text(), parse_command(), ParsedCommand, _pick_people(), allows() (+1 more)

### Community 35 - "personal_account.py"
Cohesion: 0.30
Nodes (5): _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming()

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.17
Nodes (12): 0. Luật đã chốt, 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa), 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại (+4 more)

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 38 - "Desktop"
Cohesion: 0.06
Nodes (14): Desktop, watch(), work(), work(), update_flag_file(), make_icon(), write_ico(), Tray (+6 more)

### Community 39 - "Settings"
Cohesion: 0.10
Nodes (16): load_session(), _message_box(), run_gui(), _bool(), ConfigError, _csv(), _int(), Settings (+8 more)

### Community 40 - "GroupStore"
Cohesion: 0.11
Nodes (15): GroupState, GroupStore, change(), _mtime(), 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22), 11.1 Mục tiêu, 11.2 Kiến trúc (+7 more)

### Community 41 - "test_filter.py"
Cohesion: 0.24
Nodes (19): agent(), decide(), _gemini(), make_filter(), factory(), msg(), _Ok, test_ai_error_budget_and_disabled_in_mode_all() (+11 more)

### Community 42 - "command_line.py"
Cohesion: 0.12
Nodes (14): _attach_parent_console(), _build_agent(), ConsoleZalo, _health(), main(), _prepare_home(), _run(), request_stop() (+6 more)

### Community 45 - "residents/pylos/__init__.py"
Cohesion: 0.21
Nodes (9): playground(), AgentReply, EchoAgent, GeminiAgent, done(), ToolStep, Turn, test_transient_errors_are_retried_but_others_are_not() (+1 more)

### Community 46 - "HistoryStore"
Cohesion: 0.31
Nodes (4): HistoryStore, 11.5 Bảo mật (quan trọng nhất của phần này), clear_history(), test_history_view_and_toggle()

### Community 47 - "Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)"
Cohesion: 0.13
Nodes (13): Cấu hình `settings.env` (máy Windows và VPS), Lỗi thường gặp, Tạo OAuth client (một lần, ~10 phút), Đăng nhập trang quản lý PyloS bằng Google, 1. Service cho bot, 2. Cho user `pylos` điều khiển đúng 2 service (chọn MỘT cách), 3. Bật chế độ systemd cho bot trên VPS, 4. nginx (+5 more)

### Community 48 - "make_settings"
Cohesion: 0.18
Nodes (7): make_settings(), test_bot_adds_missing_at_sign_end_to_end(), test_bot_tells_model_member_names(), test_require_personal_needs_qr_session(), test_desktop_bot_actions_report_to_tray(), test_ensure_admin_token_writes_once(), test_gateway_stops_bot_gracefully_with_flag()

### Community 49 - ".classify"
Cohesion: 0.21
Nodes (3): _is_transient(), _rejects_thinking(), _usage_tokens()

### Community 50 - "test_regions_file.py"
Cohesion: 0.28
Nodes (4): B6. Phía PyloS, region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions()

### Community 51 - "Turn"
Cohesion: 0.24
Nodes (10): Tool, ToolRegistry, FakeModels, make_agent(), response(), test_empty_reply_falls_back(), test_function_calling_loop(), test_plain_reply_and_history_conversion() (+2 more)

### Community 53 - "google_begin"
Cohesion: 0.32
Nodes (8): auth_options(), _base_url(), google_begin(), google_callback(), _google_ready(), google_start(), _page(), email_allowed()

### Community 54 - "pathlib"
Cohesion: 0.18
Nodes (4): RedactFilter, setup_logging(), test_redact_filter_hides_secrets(), test_logging_without_console()

### Community 56 - "status_info"
Cohesion: 0.18
Nodes (7): _registry_autostart(), standby_info(), ready(), ready(), status_info(), StateStore, status()

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 59 - "README (Bot trợ lý Zalo Gemini)"
Cohesion: 0.13
Nodes (14): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+6 more)

### Community 60 - "zalo/__init__.py"
Cohesion: 0.33
Nodes (5): parse_event(), parse_updates(), _to_ms(), test_dedupe_key_without_message_id_is_stable(), test_parse_updates_docs_sample()

### Community 61 - "_log_path"
Cohesion: 0.40
Nodes (5): path(), _log_path(), logs(), stream_logs(), tail()

### Community 62 - "4. Web (quanlythoigian)"
Cohesion: 0.33
Nodes (6): 4. Web (quanlythoigian), W0. Chuẩn bị (bắt buộc trước khi sửa code), W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền, W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng), W3. Google Lịch tự động: đăng nhập là xin quyền, cho phép là chạy mãi, W5. Dọn dẹp sau khi PyloS mới đã chạy ổn ≥ 7 ngày

### Community 63 - "test_remote_proxy.py"
Cohesion: 0.15
Nodes (5): client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 67 - "AdminSessions"
Cohesion: 0.25
Nodes (4): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối

### Community 68 - "test_google_login.py"
Cohesion: 0.16
Nodes (13): approve(), fake_google(), exchange(), id_token(), make_client(), test_bad_state_expired_code_and_invalid_tokens(), test_connect_vps_with_google_saves_key_without_showing_it(), test_device_keys_survive_restart_and_are_stored_hashed() (+5 more)

### Community 70 - "clock/vietnam_time.py"
Cohesion: 0.22
Nodes (5): _CachedFile, PromptBuilder, test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role()

### Community 72 - "local"
Cohesion: 0.22
Nodes (6): clean_env(), local(), no_web(), test_exchange_uses_pkce_and_checks_audience(), handler(), run()

### Community 73 - "pair"
Cohesion: 0.22
Nodes (3): clean_env(), pair(), running()

### Community 78 - "test_config_client_webhook.py"
Cohesion: 0.18
Nodes (4): _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_webhook_checks_secret_and_forwards_payload()

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 87 - "12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)"
Cohesion: 0.17
Nodes (12): 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu, 12.2 Chọn cách làm, 12.3 Kiến trúc, 12.4 Biểu tượng khay (system tray), 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được, 12.6 Đóng gói (+4 more)

### Community 88 - "test_vps_supervisor.py"
Cohesion: 0.22
Nodes (9): make_settings(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported(), test_systemd_start_and_stop_call_sudo_systemctl() (+1 more)

### Community 94 - "Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động"
Cohesion: 0.15
Nodes (12): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 5. Thứ tự đưa lên production, 6. Kiểm thử toàn hệ thống (sau bước 8 của mục 5) (+4 more)

### Community 99 - "roles.py"
Cohesion: 0.24
Nodes (6): required_role(), role_of(), role(), test_allows(), test_required_role(), test_role_of()

### Community 105 - "Cách dùng bot trên Zalo"
Cohesion: 0.25
Nodes (8): Ba vai trò, Các file trong thư mục này, Cách dùng bot trên Zalo, Giao lịch cho người khác (web iforgotmywayhome), Gọi bot ở chế độ default, Hạn mức token, Lấy ID của bạn lần đầu, Lệnh

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 109 - "AdminContext"
Cohesion: 0.29
Nodes (4): AdminContext, test_api_server_returns_info_without_secrets(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host()

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 116 - "_error"
Cohesion: 0.33
Nodes (5): config_error(), handover_import(), remote_login_poll(), remote_login_start(), _error()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 122 - "4b. Lưu trữ `.txt` và workspace `.md`"
Cohesion: 0.40
Nodes (5): health(), 4. Cấu trúc thư mục, 4a. Cấu hình và bí mật để trống, 4b. Lưu trữ `.txt` và workspace `.md`, history()

### Community 129 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 134 - "ToolContext"
Cohesion: 0.09
Nodes (37): fold(), base_url(), configured(), env_values(), request(), server_config(), _assign(), _cancel() (+29 more)

### Community 273 - "split_message"
Cohesion: 0.21
Nodes (10): _max_prefix(), split_message(), to_plain_text(), utf16_len(), test_parse_command(), test_split_counts_emoji_as_two_units(), test_split_prefers_paragraph_boundaries(), test_split_short_message_unchanged() (+2 more)

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 665 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **87 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `handover_job.py`, `InstanceLock`, `auto_update.py`, `Bot`, `server_info.py`, `qr_login.py`, `settings_file.py`, `handover.py`, `create_app`, `test_handover.py`, `Settings`, `re`, `json`, `test_personal.py`, `PersonalZalo`, `personal_account.py`, `Desktop`, `GroupStore`, `command_line.py`, `make_settings`, `status_info`, `admin_web_server.py`, `AdminSessions`, `.decide`, `ZaloSender`, `test_vps_supervisor.py`, `AdminContext`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `FailedStore` be split into smaller, more focused modules?**
  _Cohesion score 0.1286549707602339 - nodes in this community are weakly interconnected._
- **Why does `4. Web (quanlythoigian)` connect `4. Web (quanlythoigian)` to `admin_page.js`, `Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07075873827791987 - nodes in this community are weakly interconnected._