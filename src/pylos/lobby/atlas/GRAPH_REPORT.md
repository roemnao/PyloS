# Graph Report - pylosSever  (2026-11-08)

## Corpus Check
- 166 files · ~108,394 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 9, (none) 4, .css 2)

## Summary
- 1933 nodes · 4488 edges · 159 communities (77 shown, 82 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 529 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f20d17a8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- FailedStore
- handover_job.py
- test_assign_events.py
- event
- test_admin.py
- userdata_paths.py
- auto_update.py
- Bot
- MemoryDataStore
- remote_server.py
- test_desktop.py
- Envelope
- UsageStore
- google_login.py
- PyloS — rules for Claude Code
- settings_file.py
- handover.py
- JsonObjectFile
- admin_page.js
- create_app
- agent_tools/__init__.py
- test_handover.py
- Settings
- desktop_app.py
- 4. Các bước
- json
- QrLogin
- test_entrypoints.py
- mention_tags.py
- test_personal.py
- ZaloClient
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
- windows_autostart.py
- residents/pylos/__init__.py
- HistoryStore
- InstanceLock
- .settings_now
- GeminiAgent
- test_regions_file.py
- Turn
- FakeWeb
- test_qrlogin.py
- RedactFilter
- status_info
- steps
- AdminSessions
- Cách dùng bot trên Zalo
- Natural chat as Lila
- _log_path
- 4. Web (quanlythoigian)
- test_remote_proxy.py
- make_icon
- 11. Kế hoạch: giao diện quản lý bot (web dashboard)
- qr_login.py
- test_google_login.py
- is_running
- PromptBuilder
- .decide
- _zalo_login
- pair
- check_secrets.py
- test_schedule_tool.py
- _is_transient
- Ba vai trò: basic-user, leader, owner
- pytest
- fence/SYSTEM.md
- Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động
- admin_web_server.py
- gateway (bot chạy nền)
- SYSTEM.md
- zalo-assistant-bot
- 5. Phần C — kiểm thử
- ZaloError
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- test_zalo_qr_login_saves_session_and_enables_personal
- ToolContext

## God Nodes (most connected - your core abstractions)
1. `Settings` - 103 edges
2. `create_app()` - 82 edges
3. `event()` - 53 edges
4. `now_ms()` - 44 edges
5. `send()` - 42 edges
6. `ToolContext` - 38 edges
7. `main()` - 36 edges
8. `GroupStore` - 34 edges
9. `Desktop` - 33 edges
10. `Bot` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Hard rules` --references--> `migrate_to_city()`  [INFERRED]
  CLAUDE.md → src/pylos/lobby/dispatch/shared/userdata_paths.py
- `4b. Lưu trữ `.txt` và workspace `.md`` --references--> `seen()`  [INFERRED]
  src/pylos/management/managers/plans/PLAN.md → tests/management/owner/test_remote_proxy.py
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py
- `test_logging_without_console()` --calls--> `setup_logging()`  [INFERRED]
  tests/gate/side_gate/test_desktop.py → src/pylos/gate/main_gate/logs/log_files.py

## Import Cycles
- None detected.

## Communities (159 total, 82 thin omitted)

### Community 0 - "FailedStore"
Cohesion: 0.10
Nodes (15): FailedStore, change(), change(), SeenStore, JsonLinesFile, done_file(), test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist() (+7 more)

### Community 1 - "handover_job.py"
Cohesion: 0.13
Nodes (22): _bundle_path(), current(), Job, JobError, precheck(), _rollback_local(), work(), _rollback_remote() (+14 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.27
Nodes (11): basic(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team(), test_list_shows_who_has_it_in_their_app(), test_my_upcoming_events() (+3 more)

### Community 3 - "event"
Cohesion: 0.11
Nodes (48): event(), lines(), send(), test_every_message_logged_but_only_passed_ones_reach_session(), test_not_allowed_chat_is_not_logged(), send(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks() (+40 more)

### Community 4 - "test_admin.py"
Cohesion: 0.08
Nodes (6): client(), env_path(), test_bot_control_uses_gateway(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host()

### Community 5 - "userdata_paths.py"
Cohesion: 0.15
Nodes (14): atomic_write_text(), app_home(), _backup_userdata(), _clean_env(), migrate_all(), migrate_legacy(), migrate_to_city(), _move() (+6 more)

### Community 6 - "auto_update.py"
Cohesion: 0.16
Nodes (18): _mark_good(), _rollback(), _find_uv(), _git(), hold_state(), install_libs(), last_good(), mark_good() (+10 more)

### Community 7 - "Bot"
Cohesion: 0.06
Nodes (21): RateLimiter, IncomingMessage, parse_event(), parse_updates(), _to_ms(), _max_prefix(), split_message(), to_plain_text() (+13 more)

### Community 8 - "MemoryDataStore"
Cohesion: 0.23
Nodes (4): MemoryDataStore, memorydata(), test_store_trims_when_over_keep(), test_memorydata_api_shows_filter_result_and_respects_history_switch()

### Community 9 - "remote_server.py"
Cohesion: 0.14
Nodes (18): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+10 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.08
Nodes (13): _free_port(), make_settings(), test_require_personal_needs_qr_session(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_ensure_admin_token_writes_once(), test_env_template_keeps_data_inside_the_city(), test_free_port_skips_busy_port() (+5 more)

### Community 11 - "Envelope"
Cohesion: 0.07
Nodes (18): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), a(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload() (+10 more)

### Community 12 - "UsageStore"
Cohesion: 0.17
Nodes (4): today_vn(), UsageStore, test_usage_store_rolls_over_by_day(), test_usage_store_shared_between_processes()

### Community 13 - "google_login.py"
Cohesion: 0.18
Nodes (5): auth_url(), challenge(), decode_id_token(), exchange(), PendingLogins

### Community 14 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 15 - "settings_file.py"
Cohesion: 0.22
Nodes (7): read_settings(), remote_login_poll(), remote_logout(), write_secret(), write_settings(), read_values(), update()

### Community 16 - "handover.py"
Cohesion: 0.09
Nodes (20): code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state(), _uptime_seconds() (+12 more)

### Community 17 - "JsonObjectFile"
Cohesion: 0.13
Nodes (7): ready(), ready(), StateStore, JsonObjectFile, test_object_file_recovers_from_corruption(), test_groups_list_includes_seen_but_not_allowed_chats(), test_status_reports_alerts_and_stats()

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (72): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+64 more)

### Community 19 - "create_app"
Cohesion: 0.09
Nodes (34): create_app(), auth_options(), _base_url(), config_error(), devices(), _failed(), failed_action(), google_begin() (+26 more)

### Community 20 - "agent_tools/__init__.py"
Cohesion: 0.16
Nodes (9): discover(), _load_external(), Tool, ToolRegistry, tools(), test_external_tools_are_loaded_and_broken_ones_skipped(), test_tools_list_has_only_builtin_tools_by_default(), test_discover_skips_example_template() (+1 more)

### Community 21 - "test_handover.py"
Cohesion: 0.18
Nodes (14): make_side(), run_job(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_checks_data_layout_version(), test_import_endpoint_streams_and_refuses_running(), test_import_refused_while_bot_running(), test_import_rejects_non_bundle() (+6 more)

### Community 22 - "Settings"
Cohesion: 0.12
Nodes (28): clear_pid(), clear_standby(), _end_task(), follow_log(), _kill(), pid_path(), read_pid(), Result (+20 more)

### Community 23 - "desktop_app.py"
Cohesion: 0.07
Nodes (9): is_chatter(), setup_logging(), run_gui(), ensure_admin_token(), ensure_home(), FieldSpec, strip_name_prefix(), test_bot_never_calls_web_on_plain_message() (+1 more)

### Community 24 - "4. Các bước"
Cohesion: 0.15
Nodes (13): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+5 more)

### Community 25 - "json"
Cohesion: 0.21
Nodes (8): legacy_home(), test_city_migration_keeps_what_is_already_in_the_new_place(), test_city_migration_waits_for_the_old_version(), test_migrates_everything_to_userdata(), test_migrates_userdata_into_the_city_with_a_backup_and_drops_the_old_workspace(), test_restores_git_tracked_defaults(), test_skips_while_old_version_still_running(), userdata_home()

### Community 26 - "QrLogin"
Cohesion: 0.24
Nodes (5): Cancelled, QrLogin, QrLoginError, QrStatus, test_declined_and_expired()

### Community 27 - "test_entrypoints.py"
Cohesion: 0.09
Nodes (12): folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports(), test_settings_rejects_bad_or_forbidden_values(), test_console_script_targets_exist(), test_every_module_imports(), test_every_top_level_package_is_bundled_into_the_exe() (+4 more)

### Community 28 - "mention_tags.py"
Cohesion: 0.19
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 29 - "test_personal.py"
Cohesion: 0.12
Nodes (12): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+4 more)

### Community 30 - "ZaloClient"
Cohesion: 0.05
Nodes (33): ZaloClient, run_polling(), _sleep_or_stop(), 0. Quyết định đã chốt, 10. Tiến độ, 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu (+25 more)

### Community 31 - "conftest.py"
Cohesion: 0.16
Nodes (8): agent(), FakeAgent, FakeZalo, make_bot(), factory(), zalo(), test_bot_adds_missing_at_sign_end_to_end(), test_bot_tells_model_member_names()

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "owner_commands.py"
Cohesion: 0.11
Nodes (15): CommandHandler, describe_mode(), help_text(), parse_command(), ParsedCommand, _pick_people(), allows(), required_role() (+7 more)

### Community 35 - "personal_account.py"
Cohesion: 0.30
Nodes (5): _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming()

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.17
Nodes (12): 0. Luật đã chốt, 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa), 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại (+4 more)

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 39 - "Settings"
Cohesion: 0.15
Nodes (14): load_session(), _bool(), ConfigError, _csv(), _int(), Settings, clean_value(), validate() (+6 more)

### Community 40 - "GroupStore"
Cohesion: 0.13
Nodes (8): _clean_map(), _clean_teams(), GroupState, GroupStore, change(), _mtime(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders()

### Community 41 - "test_filter.py"
Cohesion: 0.24
Nodes (19): agent(), decide(), _gemini(), make_filter(), factory(), msg(), _Ok, test_ai_error_budget_and_disabled_in_mode_all() (+11 more)

### Community 42 - "command_line.py"
Cohesion: 0.11
Nodes (17): _attach_parent_console(), _build_agent(), _console(), ConsoleZalo, _health(), main(), _prepare_home(), _run() (+9 more)

### Community 44 - "windows_autostart.py"
Cohesion: 0.19
Nodes (6): Tray, command(), is_enabled(), migrate(), set_enabled(), is_frozen()

### Community 45 - "residents/pylos/__init__.py"
Cohesion: 0.17
Nodes (7): playground(), Agent, AgentReply, EchoAgent, done(), ToolStep, slow_reply()

### Community 46 - "HistoryStore"
Cohesion: 0.12
Nodes (12): create_app(), health(), webhook(), HistoryStore, 11.5 Bảo mật (quan trọng nhất của phần này), 4. Cấu trúc thư mục, 4a. Cấu hình và bí mật để trống, 4b. Lưu trữ `.txt` và workspace `.md` (+4 more)

### Community 47 - "InstanceLock"
Cohesion: 0.23
Nodes (6): gui_running(), AlreadyRunning, InstanceLock, _city_old_running(), _old_version_running(), test_instance_lock_blocks_second_instance()

### Community 48 - ".settings_now"
Cohesion: 0.22
Nodes (3): watch(), work(), update_flag_file()

### Community 49 - "GeminiAgent"
Cohesion: 0.20
Nodes (3): GeminiAgent, _usage_tokens(), test_gemini_classify_requests_json_and_counts_tokens()

### Community 50 - "test_regions_file.py"
Cohesion: 0.28
Nodes (4): B6. Phía PyloS, region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions()

### Community 51 - "Turn"
Cohesion: 0.26
Nodes (11): Turn, FakeModels, make_agent(), response(), test_empty_reply_falls_back(), test_function_calling_loop(), test_plain_reply_and_history_conversion(), test_tool_round_limit() (+3 more)

### Community 52 - "FakeWeb"
Cohesion: 0.17
Nodes (3): FakeWeb, calbot(), test_unlinked_sender_gets_a_helpful_message()

### Community 53 - "test_qrlogin.py"
Cohesion: 0.22
Nodes (4): FakeResponse, FakeZalo, test_cancel_stops_before_next_request(), test_full_qr_flow_returns_session_with_chat_cookies()

### Community 56 - "status_info"
Cohesion: 0.22
Nodes (6): _registry_autostart(), standby_info(), status_info(), StatsStore, server(), status()

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 59 - "Cách dùng bot trên Zalo"
Cohesion: 0.05
Nodes (35): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+27 more)

### Community 60 - "Natural chat as Lila"
Cohesion: 0.17
Nodes (11): Habits, Humor, Layout of each reply, Natural chat as Lila, Nox, Patterns (from Vietnamese news-site comments, Nov 2026), Real examples from this person (read these first), Rules (+3 more)

### Community 61 - "_log_path"
Cohesion: 0.40
Nodes (5): path(), _log_path(), logs(), stream_logs(), tail()

### Community 62 - "4. Web (quanlythoigian)"
Cohesion: 0.29
Nodes (7): 4. Web (quanlythoigian), W0. Chuẩn bị (bắt buộc trước khi sửa code), W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền, W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng), W3. Google Lịch tự động: đăng nhập là xin quyền, cho phép là chạy mãi, W5. Dọn dẹp sau khi PyloS mới đã chạy ổn ≥ 7 ngày, web()

### Community 63 - "test_remote_proxy.py"
Cohesion: 0.12
Nodes (7): AdminContext, test_api_server_returns_info_without_secrets(), client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 64 - "make_icon"
Cohesion: 0.22
Nodes (3): make_icon(), write_ico(), test_icons()

### Community 66 - "11. Kế hoạch: giao diện quản lý bot (web dashboard)"
Cohesion: 0.18
Nodes (11): 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22), 11.1 Mục tiêu, 11.2 Kiến trúc, 11.3 Các trang, 11.4 API (JSON, dưới `/api`), 11.6 Việc phải bổ sung vào bot hiện có, 11.7 Thư mục dự kiến (+3 more)

### Community 67 - "qr_login.py"
Cohesion: 0.25
Nodes (3): cookies_for(), make_imei(), test_cookies_for_prefers_specific_domain()

### Community 68 - "test_google_login.py"
Cohesion: 0.07
Nodes (25): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối, AdminDevices, approve(), clean_env(), fake_google() (+17 more)

### Community 69 - "is_running"
Cohesion: 0.36
Nodes (8): _admin(), _update(), is_running(), lock_for(), restart(), rollback_app(), update_app(), work()

### Community 70 - "PromptBuilder"
Cohesion: 0.12
Nodes (9): _CachedFile, PromptBuilder, test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role(), build(), test_prompt_picks_up_a_new_file_and_falls_back_without_system(), test_prompt_reads_every_document_in_the_workspace() (+1 more)

### Community 72 - "_zalo_login"
Cohesion: 0.36
Nodes (6): _zalo_login(), on_update(), apply_session(), save_qr_png(), ZaloSession, test_apply_session_saves_file_and_enables_personal_mode()

### Community 73 - "pair"
Cohesion: 0.22
Nodes (3): clean_env(), pair(), running()

### Community 78 - "check_secrets.py"
Cohesion: 0.43
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "pytest"
Cohesion: 0.07
Nodes (27): AccessDenied, Actor, check_access(), _inside(), _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_webhook_checks_secret_and_forwards_payload() (+19 more)

### Community 93 - "fence/SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 94 - "Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động"
Cohesion: 0.17
Nodes (11): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 5. Thứ tự đưa lên production, 6. Kiểm thử toàn hệ thống (sau bước 8 của mục 5) (+3 more)

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 117 - "ZaloError"
Cohesion: 0.14
Nodes (4): ZaloError, _import_zlapi(), _is_network_error(), test_network_errors_are_detected_through_zlapi_wrapping()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 129 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 134 - "ToolContext"
Cohesion: 0.09
Nodes (38): fold(), base_url(), configured(), env_values(), request(), server_config(), _assign(), _cancel() (+30 more)

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 688 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **82 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `handover_job.py`, `auto_update.py`, `Bot`, `remote_server.py`, `test_desktop.py`, `handover.py`, `create_app`, `test_handover.py`, `Settings`, `desktop_app.py`, `test_personal.py`, `ZaloClient`, `PersonalZalo`, `personal_account.py`, `Desktop`, `command_line.py`, `InstanceLock`, `.settings_now`, `status_info`, `test_remote_proxy.py`, `11. Kế hoạch: giao diện quản lý bot (web dashboard)`, `test_google_login.py`, `is_running`, `.decide`, `_zalo_login`, `pytest`, `admin_web_server.py`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `FailedStore` be split into smaller, more focused modules?**
  _Cohesion score 0.0967741935483871 - nodes in this community are weakly interconnected._
- **Why does `4. Web (quanlythoigian)` connect `4. Web (quanlythoigian)` to `admin_page.js`, `Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12941176470588237 - nodes in this community are weakly interconnected._