# Graph Report - pylosSever  (2026-11-06)

## Corpus Check
- 162 files · ~104,184 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 9, (none) 4, .css 2)

## Summary
- 1860 nodes · 4478 edges · 144 communities (74 shown, 70 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 544 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef005d13`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tray_icon.py
- handover_job.py
- test_assign_events.py
- event
- test_admin.py
- InstanceLock
- auto_update.py
- Bot
- JsonLinesFile
- Settings
- test_desktop.py
- PyloS — Kế hoạch dựng "Thành chính"
- JsonObjectFile
- QrLogin
- PyloS — rules for Claude Code
- conftest.py
- handover.py
- ActivityStore
- admin_page.js
- create_app
- GeminiAgent
- test_handover.py
- Settings
- userdata_paths.py
- 4. Các bước
- now_ms
- command_line.py
- pytest
- residents/pylos/__init__.py
- AdminDevices
- ZaloClient
- local
- zalo/mention_tags.py
- Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết
- owner_commands.py
- PersonalZalo
- Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc
- 3. Phần A — sửa code Python (`region_map.py`)
- Desktop
- config.py
- GroupStore
- test_filter.py
- PromptBuilder
- test_memorydata.py
- httpx
- test_no_web_coupling.py
- HistoryStore
- message_handler.py
- _is_transient
- .__init__
- dataclasses
- agent_tools/__init__.py
- test_schedule_tool.py
- ZaloError
- to_incoming
- MemoryDataStore
- steps
- 1. Hiện trạng (đọc trước khi sửa)
- Cách dùng bot trên Zalo
- zalo/__init__.py
- main
- 4. Web (quanlythoigian)
- test_remote_proxy.py
- test_messages_in_same_chat_are_processed_in_order
- load_session
- test_google_login.py
- .decide
- pair
- FailedStore
- check_secrets.py
- Ba vai trò: basic-user, leader, owner
- test_vps_supervisor.py
- FakeWeb
- Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động
- test_config_client_webhook.py
- gateway (bot chạy nền)
- _log_path
- SYSTEM.md
- zalo-assistant-bot
- 5. Phần C — kiểm thử
- PromptBuilder
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- test_zalo_qr_login_saves_session_and_enables_personal
- ToolContext
- AdminSessions
- test_polling_delivers_updates_and_survives_errors
- split_message

## God Nodes (most connected - your core abstractions)
1. `Settings` - 103 edges
2. `create_app()` - 90 edges
3. `event()` - 53 edges
4. `now_ms()` - 44 edges
5. `send()` - 42 edges
6. `ToolContext` - 41 edges
7. `main()` - 37 edges
8. `Desktop` - 37 edges
9. `Bot` - 36 edges
10. `GroupStore` - 35 edges

## Surprising Connections (you probably didn't know these)
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py
- `P2. Đăng nhập Google riêng của PyloS` --references--> `id_token()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/management/owner/test_google_login.py
- `7. Bảng lỗi chung có thể gặp (ngoài các bảng ở từng giai đoạn)` --references--> `base_url()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → src/pylos/gate/main_gate/external_apps/server_client.py
- `test_logging_without_console()` --calls--> `setup_logging()`  [INFERRED]
  tests/gate/side_gate/test_desktop.py → src/pylos/gate/main_gate/logs/log_files.py

## Import Cycles
- None detected.

## Communities (144 total, 70 thin omitted)

### Community 0 - "tray_icon.py"
Cohesion: 0.10
Nodes (8): make_icon(), write_ico(), Tray, command(), is_enabled(), migrate(), set_enabled(), test_icons()

### Community 1 - "handover_job.py"
Cohesion: 0.07
Nodes (41): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+33 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.21
Nodes (12): basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team(), test_list_shows_who_has_it_in_their_app() (+4 more)

### Community 3 - "event"
Cohesion: 0.12
Nodes (45): event(), send(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks(), test_allow_all_off_by_default(), test_assign_allowed_all_still_opens_everyone(), test_bare_trigger_asks_what_to_do(), test_budget_exceeded_turns_all_into_default_and_notifies_once() (+37 more)

### Community 4 - "test_admin.py"
Cohesion: 0.07
Nodes (10): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders(), test_memorydata_api_shows_filter_result_and_respects_history_switch(), test_page_and_every_asset_it_links_are_served(), test_session_tokens_expire_and_are_capped() (+2 more)

### Community 5 - "InstanceLock"
Cohesion: 0.24
Nodes (7): run_gui(), gui_running(), AlreadyRunning, InstanceLock, _old_version_running(), test_skips_while_old_version_still_running(), test_instance_lock_blocks_second_instance()

### Community 6 - "auto_update.py"
Cohesion: 0.05
Nodes (39): _mark_good(), _rollback(), code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory() (+31 more)

### Community 7 - "Bot"
Cohesion: 0.14
Nodes (4): _console(), Bot, Job, test_tagging_personal_account_answers_and_strips_tag()

### Community 8 - "JsonLinesFile"
Cohesion: 0.13
Nodes (9): SeenStore, JsonLinesFile, test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist(), test_group_teams_and_leader_added_by(), test_jsonl_append_rewrite_and_utf8(), test_jsonl_skips_broken_lines(), test_lone_surrogate_does_not_crash_write() (+1 more)

### Community 9 - "Settings"
Cohesion: 0.16
Nodes (11): _run(), request_stop(), watch_stop_flag(), set_standby(), standby_path(), stop_flag(), Settings, 13. Điều khiển bot trên VPS từ ứng dụng ở máy này (+3 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.08
Nodes (10): _free_port(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_env_template_keeps_data_inside_userdata(), test_external_tools_are_loaded_and_broken_ones_skipped(), test_free_port_skips_busy_port(), test_frozen_child_gets_its_own_unpack_dir(), test_logging_without_console() (+2 more)

### Community 11 - "PyloS — Kế hoạch dựng "Thành chính""
Cohesion: 0.13
Nodes (8): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload(), test_overhead_per_message_is_far_below_one_second()

### Community 12 - "JsonObjectFile"
Cohesion: 0.10
Nodes (12): ready(), ready(), today_vn(), StateStore, StatsStore, UsageStore, JsonObjectFile, test_object_file_recovers_from_corruption() (+4 more)

### Community 13 - "QrLogin"
Cohesion: 0.06
Nodes (23): _zalo_login(), on_update(), apply_session(), Cancelled, cookies_for(), make_imei(), QrLogin, QrLoginError (+15 more)

### Community 14 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 15 - "conftest.py"
Cohesion: 0.14
Nodes (14): W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng), agent(), FakeAgent, FakeZalo, make_bot(), factory(), make_settings(), web() (+6 more)

### Community 16 - "handover.py"
Cohesion: 0.10
Nodes (15): now_vn(), backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip() (+7 more)

### Community 17 - "ActivityStore"
Cohesion: 0.15
Nodes (11): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+3 more)

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (72): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+64 more)

### Community 19 - "create_app"
Cohesion: 0.09
Nodes (34): create_app(), auth_options(), _base_url(), config_error(), devices(), google_begin(), google_callback(), google_poll() (+26 more)

### Community 20 - "GeminiAgent"
Cohesion: 0.20
Nodes (3): GeminiAgent, _usage_tokens(), test_gemini_classify_requests_json_and_counts_tokens()

### Community 21 - "test_handover.py"
Cohesion: 0.15
Nodes (14): make_side(), run_job(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_checks_data_layout_version(), test_import_endpoint_streams_and_refuses_running(), test_import_refused_while_bot_running(), test_import_rejects_non_bundle() (+6 more)

### Community 22 - "Settings"
Cohesion: 0.15
Nodes (23): clear_pid(), clear_standby(), _end_task(), follow_log(), _kill(), pid_path(), read_pid(), Result (+15 more)

### Community 23 - "userdata_paths.py"
Cohesion: 0.19
Nodes (9): _prepare_home(), app_home(), _clean_env(), is_frozen(), migrate_legacy(), _move(), needs_migration(), _restore_git_defaults() (+1 more)

### Community 24 - "4. Các bước"
Cohesion: 0.14
Nodes (14): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+6 more)

### Community 25 - "now_ms"
Cohesion: 0.21
Nodes (8): _health(), format_status(), ago(), _registry_autostart(), standby_info(), status_info(), now_ms(), status()

### Community 26 - "command_line.py"
Cohesion: 0.12
Nodes (4): setup_logging(), _message_box(), safe_name(), atomic_write_text()

### Community 27 - "pytest"
Cohesion: 0.06
Nodes (25): AccessDenied, Actor, check_access(), _inside(), folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports() (+17 more)

### Community 28 - "residents/pylos/__init__.py"
Cohesion: 0.19
Nodes (6): _build_agent(), Agent, AgentReply, EchoAgent, done(), ToolStep

### Community 30 - "ZaloClient"
Cohesion: 0.05
Nodes (36): ConsoleZalo, _zalo_call(), ZaloClient, run_polling(), _sleep_or_stop(), 0. Quyết định đã chốt, 10. Tiến độ, 12.10 Cần bạn xác nhận trước khi làm (+28 more)

### Community 31 - "local"
Cohesion: 0.22
Nodes (6): clean_env(), local(), no_web(), test_exchange_uses_pkce_and_checks_audience(), handler(), run()

### Community 32 - "zalo/mention_tags.py"
Cohesion: 0.19
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "owner_commands.py"
Cohesion: 0.20
Nodes (9): CommandHandler, describe_mode(), help_text(), parse_command(), ParsedCommand, _pick_people(), allows(), required_role() (+1 more)

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.25
Nodes (8): 0. Luật đã chốt, 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại, 2. Chuẩn bị, 6. Lỗi có thể xảy ra, 7. Thứ tự làm và điều kiện xong, Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 38 - "Desktop"
Cohesion: 0.13
Nodes (5): Desktop, watch(), work(), work(), update_flag_file()

### Community 39 - "config.py"
Cohesion: 0.13
Nodes (14): _bool(), ConfigError, _csv(), _int(), read_settings(), remote_logout(), write_secret(), write_settings() (+6 more)

### Community 40 - "GroupStore"
Cohesion: 0.09
Nodes (17): GroupState, GroupStore, change(), change(), change(), _mtime(), 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22) (+9 more)

### Community 41 - "test_filter.py"
Cohesion: 0.24
Nodes (19): agent(), decide(), _gemini(), make_filter(), factory(), msg(), _Ok, test_ai_error_budget_and_disabled_in_mode_all() (+11 more)

### Community 42 - "PromptBuilder"
Cohesion: 0.33
Nodes (5): playground(), PromptBuilder, test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role()

### Community 43 - "test_memorydata.py"
Cohesion: 0.53
Nodes (5): lines(), send(), test_every_message_logged_but_only_passed_ones_reach_session(), test_not_allowed_chat_is_not_logged(), test_store_trims_when_over_keep()

### Community 44 - "httpx"
Cohesion: 0.12
Nodes (3): create_app(), webhook(), test_webhook_checks_secret_and_forwards_payload()

### Community 46 - "HistoryStore"
Cohesion: 0.27
Nodes (5): HistoryStore, 11.5 Bảo mật (quan trọng nhất của phần này), clear_history(), test_history_tail_trim_and_safe_filename(), test_history_view_and_toggle()

### Community 47 - "message_handler.py"
Cohesion: 0.16
Nodes (7): is_chatter(), role_of(), strip_name_prefix(), role(), test_allows(), test_required_role(), test_role_of()

### Community 51 - "agent_tools/__init__.py"
Cohesion: 0.19
Nodes (6): discover(), _load_external(), Tool, ToolRegistry, test_discover_skips_example_template(), test_registry_owner_only_unknown_and_errors()

### Community 55 - "to_incoming"
Cohesion: 0.27
Nodes (6): _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming(), test_to_incoming_maps_fields_and_marks_own_messages()

### Community 56 - "MemoryDataStore"
Cohesion: 0.23
Nodes (3): _clean_map(), _clean_teams(), MemoryDataStore

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 58 - "1. Hiện trạng (đọc trước khi sửa)"
Cohesion: 0.50
Nodes (4): 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa)

### Community 59 - "Cách dùng bot trên Zalo"
Cohesion: 0.05
Nodes (35): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+27 more)

### Community 60 - "zalo/__init__.py"
Cohesion: 0.31
Nodes (5): parse_event(), parse_updates(), _to_ms(), test_dedupe_key_without_message_id_is_stable(), test_parse_updates_docs_sample()

### Community 61 - "main"
Cohesion: 0.17
Nodes (12): _admin(), _attach_parent_console(), main(), _update(), _utf8_console(), is_running(), lock_for(), restart() (+4 more)

### Community 62 - "4. Web (quanlythoigian)"
Cohesion: 0.40
Nodes (5): 4. Web (quanlythoigian), W0. Chuẩn bị (bắt buộc trước khi sửa code), W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền, W3. Google Lịch tự động: đăng nhập là xin quyền, cho phép là chạy mãi, W5. Dọn dẹp sau khi PyloS mới đã chạy ổn ≥ 7 ngày

### Community 63 - "test_remote_proxy.py"
Cohesion: 0.10
Nodes (11): health(), 4b. Lưu trữ `.txt` và workspace `.md`, AdminContext, history(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host(), client(), seen() (+3 more)

### Community 66 - "load_session"
Cohesion: 0.14
Nodes (5): _import_zlapi(), _is_network_error(), load_session(), test_load_session_reads_qr_file_and_manual_cookies(), test_network_errors_are_detected_through_zlapi_wrapping()

### Community 68 - "test_google_login.py"
Cohesion: 0.16
Nodes (14): approve(), fake_google(), exchange(), id_token(), make_client(), test_bad_state_expired_code_and_invalid_tokens(), test_connect_vps_with_google_saves_key_without_showing_it(), test_default_remote_url_and_off() (+6 more)

### Community 71 - ".decide"
Cohesion: 0.21
Nodes (3): Decision, MessageFilter, IncomingMessage

### Community 76 - "pair"
Cohesion: 0.22
Nodes (3): clean_env(), pair(), running()

### Community 80 - "FailedStore"
Cohesion: 0.25
Nodes (5): FailedStore, done_file(), _failed(), test_stats_activity_and_failed_stores(), test_failed_list_and_dismiss()

### Community 82 - "check_secrets.py"
Cohesion: 0.36
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "test_vps_supervisor.py"
Cohesion: 0.24
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 94 - "Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động"
Cohesion: 0.15
Nodes (12): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 5. Thứ tự đưa lên production, 6. Kiểm thử toàn hệ thống (sau bước 8 của mục 5) (+4 more)

### Community 103 - "test_config_client_webhook.py"
Cohesion: 0.16
Nodes (5): RedactFilter, _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_redact_filter_hides_secrets()

### Community 105 - "_log_path"
Cohesion: 0.40
Nodes (5): path(), _log_path(), logs(), stream_logs(), tail()

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 116 - "PromptBuilder"
Cohesion: 0.26
Nodes (11): Turn, FakeModels, make_agent(), response(), test_empty_reply_falls_back(), test_function_calling_loop(), test_plain_reply_and_history_conversion(), test_tool_round_limit() (+3 more)

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 129 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 134 - "ToolContext"
Cohesion: 0.08
Nodes (37): fold(), base_url(), configured(), env_values(), request(), server_config(), _assign(), _cancel() (+29 more)

### Community 159 - "AdminSessions"
Cohesion: 0.17
Nodes (5): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối, AdminSessions

### Community 273 - "split_message"
Cohesion: 0.23
Nodes (9): _max_prefix(), split_message(), to_plain_text(), utf16_len(), test_split_counts_emoji_as_two_units(), test_split_prefers_paragraph_boundaries(), test_split_short_message_unchanged(), test_split_without_spaces_hard_cuts() (+1 more)

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 643 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **70 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `handover_job.py`, `InstanceLock`, `auto_update.py`, `Bot`, `QrLogin`, `conftest.py`, `handover.py`, `create_app`, `test_handover.py`, `Settings`, `now_ms`, `command_line.py`, `residents/pylos/__init__.py`, `ZaloClient`, `AdminSessions`, `PersonalZalo`, `Desktop`, `config.py`, `GroupStore`, `httpx`, `message_handler.py`, `.__init__`, `dataclasses`, `to_incoming`, `main`, `test_remote_proxy.py`, `test_google_login.py`, `.decide`, `test_vps_supervisor.py`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tray_icon.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09655172413793103 - nodes in this community are weakly interconnected._
- **Why does `create_app()` connect `create_app` to `handover_job.py`, `test_admin.py`, `ToolContext`, `auto_update.py`, `Settings`, `QrLogin`, `handover.py`, `split_message`, `GeminiAgent`, `test_handover.py`, `now_ms`, `command_line.py`, `residents/pylos/__init__.py`, `AdminDevices`, `ZaloClient`, `AdminSessions`, `local`, `Desktop`, `config.py`, `PromptBuilder`, `httpx`, `HistoryStore`, `agent_tools/__init__.py`, `main`, `test_remote_proxy.py`, `test_google_login.py`, `pair`, `FailedStore`, `test_vps_supervisor.py`, `_log_path`, `PromptBuilder`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07075873827791987 - nodes in this community are weakly interconnected._