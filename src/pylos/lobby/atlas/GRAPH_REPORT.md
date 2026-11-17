# Graph Report - pylosSever  (2026-11-09)

## Corpus Check
- 172 files · ~111,301 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 9, (none) 4, .css 2)

## Summary
- 1966 nodes · 4565 edges · 158 communities (70 shown, 88 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 541 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `208e819d`
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
- split_message
- test_desktop.py
- Envelope
- UsageStore
- qr_login.py
- PyloS — rules for Claude Code
- test_vps_supervisor.py
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
- IncomingMessage
- test_entrypoints.py
- mention_tags.py
- test_personal.py
- Kế hoạch: Server Bot Zalo chạy Agent (AI)
- AdminDevices
- PersonalZalo
- Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết
- owner_commands.py
- personal_account.py
- Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc
- 3. Phần A — sửa code Python (`region_map.py`)
- test_config_client_webhook.py
- config.py
- GroupStore
- test_filter.py
- command_line.py
- tray_icon.py
- residents/pylos/__init__.py
- HistoryStore
- ZaloClient
- GeminiAgent
- 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)
- Turn
- receive_webhook.py
- FailedStore
- ._maybe_link
- storage.py
- steps
- incoming_message.py
- Cách dùng bot trên Zalo
- Natural chat as Lila
- receive_polling.py
- path_guard.py
- test_remote_proxy.py
- ZaloError
- .apply_settings
- 1. Hiện trạng (đọc trước khi sửa)
- test_google_login.py
- test_polling.py
- PromptBuilder
- .decide
- check_secrets.py
- test_schedule_tool.py
- _is_transient
- Ba vai trò: basic-user, leader, owner
- pytest
- fence/SYSTEM.md
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
4. `now_ms()` - 45 edges
5. `send()` - 42 edges
6. `ToolContext` - 38 edges
7. `Bot` - 36 edges
8. `main()` - 36 edges
9. `GroupStore` - 34 edges
10. `Desktop` - 33 edges

## Surprising Connections (you probably didn't know these)
- `Hard rules` --references--> `migrate_to_city()`  [INFERRED]
  CLAUDE.md → src/pylos/lobby/dispatch/shared/userdata_paths.py
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py
- `4b. Lưu trữ `.txt` và workspace `.md`` --references--> `seen()`  [INFERRED]
  src/pylos/management/managers/plans/PLAN.md → tests/management/owner/test_remote_proxy.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py
- `P2. Đăng nhập Google riêng của PyloS` --references--> `id_token()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/management/owner/test_google_login.py

## Import Cycles
- None detected.

## Communities (158 total, 88 thin omitted)

### Community 0 - "FailedStore"
Cohesion: 0.16
Nodes (9): SeenStore, JsonLinesFile, test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist(), test_group_teams_and_leader_added_by(), test_jsonl_append_rewrite_and_utf8(), test_jsonl_skips_broken_lines(), test_lone_surrogate_does_not_crash_write() (+1 more)

### Community 1 - "handover_job.py"
Cohesion: 0.07
Nodes (41): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+33 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.05
Nodes (33): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 4. Web (quanlythoigian), 5. Thứ tự đưa lên production (+25 more)

### Community 3 - "event"
Cohesion: 0.05
Nodes (59): is_chatter(), strip_name_prefix(), agent(), event(), FakeZalo, make_bot(), factory(), zalo() (+51 more)

### Community 4 - "test_admin.py"
Cohesion: 0.08
Nodes (8): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host()

### Community 5 - "userdata_paths.py"
Cohesion: 0.11
Nodes (23): gui_running(), AlreadyRunning, InstanceLock, app_home(), _backup_for_huts(), _backup_userdata(), _city_old_running(), _clean_env() (+15 more)

### Community 6 - "auto_update.py"
Cohesion: 0.08
Nodes (29): _mark_good(), _rollback(), _free_port(), code_version(), collect(), _git(), last_update_run(), _latest_remote() (+21 more)

### Community 7 - "Bot"
Cohesion: 0.13
Nodes (5): _console(), ConsoleZalo, Bot, Job, test_tagging_personal_account_answers_and_strips_tag()

### Community 8 - "MemoryDataStore"
Cohesion: 0.17
Nodes (4): RateLimiter, MemoryDataStore, memorydata(), test_memorydata_api_shows_filter_result_and_respects_history_switch()

### Community 9 - "split_message"
Cohesion: 0.19
Nodes (11): _max_prefix(), split_message(), to_plain_text(), utf16_len(), parse_command(), test_parse_command(), test_split_counts_emoji_as_two_units(), test_split_prefers_paragraph_boundaries() (+3 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.07
Nodes (13): make_settings(), test_bot_adds_missing_at_sign_end_to_end(), test_bot_tells_model_member_names(), test_require_personal_needs_qr_session(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_ensure_admin_token_writes_once(), test_env_template_keeps_data_inside_the_city() (+5 more)

### Community 11 - "Envelope"
Cohesion: 0.13
Nodes (8): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload(), test_overhead_per_message_is_far_below_one_second()

### Community 12 - "UsageStore"
Cohesion: 0.12
Nodes (8): today_vn(), _clean_map(), _clean_teams(), StatsStore, UsageStore, test_stats_activity_and_failed_stores(), test_usage_store_shared_between_processes(), test_status_reports_alerts_and_stats()

### Community 13 - "qr_login.py"
Cohesion: 0.06
Nodes (22): on_update(), apply_session(), Cancelled, cookies_for(), make_imei(), QrLogin, QrLoginError, QrStatus (+14 more)

### Community 14 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 15 - "test_vps_supervisor.py"
Cohesion: 0.20
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 16 - "handover.py"
Cohesion: 0.14
Nodes (14): now_vn(), backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip() (+6 more)

### Community 17 - "JsonObjectFile"
Cohesion: 0.17
Nodes (4): JsonObjectFile, test_object_file_recovers_from_corruption(), test_usage_store_rolls_over_by_day(), test_groups_list_includes_seen_but_not_allowed_chats()

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (72): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+64 more)

### Community 19 - "create_app"
Cohesion: 0.08
Nodes (39): path(), create_app(), auth_options(), _base_url(), config_error(), devices(), _failed(), failed_action() (+31 more)

### Community 20 - "agent_tools/__init__.py"
Cohesion: 0.14
Nodes (10): discover(), _load_external(), Tool, ToolRegistry, tools(), _gemini(), test_external_tools_are_loaded_and_broken_ones_skipped(), test_tools_list_has_only_builtin_tools_by_default() (+2 more)

### Community 21 - "test_handover.py"
Cohesion: 0.10
Nodes (18): AdminContext, clean_env(), make_side(), pair(), run_job(), running(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions() (+10 more)

### Community 22 - "Settings"
Cohesion: 0.05
Nodes (59): _admin(), _health(), main(), _run(), request_stop(), watch_stop_flag(), _update(), _zalo_call() (+51 more)

### Community 23 - "desktop_app.py"
Cohesion: 0.11
Nodes (4): RedactFilter, setup_logging(), atomic_write_text(), test_redact_filter_hides_secrets()

### Community 24 - "4. Các bước"
Cohesion: 0.14
Nodes (14): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+6 more)

### Community 25 - "json"
Cohesion: 0.15
Nodes (11): load_session(), test_load_session_reads_qr_file_and_manual_cookies(), legacy_home(), test_city_migration_keeps_what_is_already_in_the_new_place(), test_city_migration_waits_for_the_old_version(), test_migrates_everything_to_userdata(), test_migrates_userdata_into_the_city_with_a_backup_and_drops_the_old_workspace(), test_restores_git_tracked_defaults() (+3 more)

### Community 26 - "IncomingMessage"
Cohesion: 0.24
Nodes (5): IncomingMessage, CommandHandler, ParsedCommand, _pick_people(), test_pick_people_prefers_real_tags_and_skips_bot()

### Community 27 - "test_entrypoints.py"
Cohesion: 0.05
Nodes (25): folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports(), region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions(), a() (+17 more)

### Community 28 - "mention_tags.py"
Cohesion: 0.19
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 29 - "test_personal.py"
Cohesion: 0.15
Nodes (11): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+3 more)

### Community 30 - "Kế hoạch: Server Bot Zalo chạy Agent (AI)"
Cohesion: 0.11
Nodes (18): 0. Quyết định đã chốt, 10. Tiến độ, 1. Chọn kênh Zalo, 1a. Zalo Bot Platform: các sự kiện đã xác minh, 2. Kiến trúc, 3. Công nghệ, 3a. Nhận tin khi chạy local, chưa có domain, 3b. Chạy 24/7 khi chưa có VPS (+10 more)

### Community 31 - "AdminDevices"
Cohesion: 0.27
Nodes (5): 3. PyloS, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối, AdminDevices, test_device_keys_expire_and_same_machine_replaces_old_key()

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "owner_commands.py"
Cohesion: 0.13
Nodes (11): fold(), describe_mode(), help_text(), allows(), required_role(), role_of(), match_member(), role() (+3 more)

### Community 35 - "personal_account.py"
Cohesion: 0.27
Nodes (6): _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming(), test_to_incoming_maps_fields_and_marks_own_messages()

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.25
Nodes (8): 0. Luật đã chốt, 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại, 2. Chuẩn bị, 6. Lỗi có thể xảy ra, 7. Thứ tự làm và điều kiện xong, Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 38 - "test_config_client_webhook.py"
Cohesion: 0.18
Nodes (4): _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_webhook_checks_secret_and_forwards_payload()

### Community 39 - "config.py"
Cohesion: 0.12
Nodes (16): run_gui(), _bool(), ConfigError, _csv(), _int(), read_settings(), remote_logout(), write_secret() (+8 more)

### Community 40 - "GroupStore"
Cohesion: 0.11
Nodes (15): GroupState, GroupStore, change(), _mtime(), 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22), 11.1 Mục tiêu, 11.2 Kiến trúc (+7 more)

### Community 41 - "test_filter.py"
Cohesion: 0.09
Nodes (28): FilterInstructions, FakeAgent, agent(), decide(), make_filter(), factory(), msg(), _Ok (+20 more)

### Community 42 - "command_line.py"
Cohesion: 0.11
Nodes (6): _attach_parent_console(), _prepare_home(), _utf8_console(), _message_box(), ensure_admin_token(), ensure_home()

### Community 44 - "tray_icon.py"
Cohesion: 0.09
Nodes (9): make_icon(), write_ico(), Tray, command(), is_enabled(), migrate(), set_enabled(), is_frozen() (+1 more)

### Community 45 - "residents/pylos/__init__.py"
Cohesion: 0.15
Nodes (8): _build_agent(), playground(), Agent, AgentReply, EchoAgent, done(), ToolStep, slow_reply()

### Community 46 - "HistoryStore"
Cohesion: 0.27
Nodes (5): HistoryStore, 11.5 Bảo mật (quan trọng nhất của phần này), clear_history(), test_history_tail_trim_and_safe_filename(), test_history_view_and_toggle()

### Community 49 - "GeminiAgent"
Cohesion: 0.20
Nodes (3): GeminiAgent, _usage_tokens(), test_gemini_classify_requests_json_and_counts_tokens()

### Community 50 - "12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)"
Cohesion: 0.17
Nodes (12): 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu, 12.2 Chọn cách làm, 12.3 Kiến trúc, 12.4 Biểu tượng khay (system tray), 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được, 12.6 Đóng gói (+4 more)

### Community 51 - "Turn"
Cohesion: 0.26
Nodes (11): Turn, FakeModels, make_agent(), response(), test_empty_reply_falls_back(), test_function_calling_loop(), test_plain_reply_and_history_conversion(), test_tool_round_limit() (+3 more)

### Community 52 - "receive_webhook.py"
Cohesion: 0.20
Nodes (5): create_app(), health(), webhook(), 4b. Lưu trữ `.txt` và workspace `.md`, history()

### Community 53 - "FailedStore"
Cohesion: 0.18
Nodes (5): FailedStore, change(), change(), done_file(), test_failed_list_and_dismiss()

### Community 56 - "storage.py"
Cohesion: 0.24
Nodes (4): ready(), ready(), safe_name(), StateStore

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 58 - "incoming_message.py"
Cohesion: 0.33
Nodes (5): parse_event(), parse_updates(), _to_ms(), test_dedupe_key_without_message_id_is_stable(), test_parse_updates_docs_sample()

### Community 59 - "Cách dùng bot trên Zalo"
Cohesion: 0.05
Nodes (35): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+27 more)

### Community 60 - "Natural chat as Lila"
Cohesion: 0.17
Nodes (11): Habits, Humor, Layout of each reply, Natural chat as Lila, Nox, Patterns (from Vietnamese news-site comments, Nov 2026), Real examples from this person (read these first), Rules (+3 more)

### Community 62 - "path_guard.py"
Cohesion: 0.43
Nodes (3): Actor, check_access(), _inside()

### Community 63 - "test_remote_proxy.py"
Cohesion: 0.13
Nodes (5): client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 67 - "1. Hiện trạng (đọc trước khi sửa)"
Cohesion: 0.50
Nodes (4): 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa)

### Community 68 - "test_google_login.py"
Cohesion: 0.11
Nodes (19): approve(), clean_env(), fake_google(), exchange(), id_token(), local(), make_client(), no_web() (+11 more)

### Community 70 - "PromptBuilder"
Cohesion: 0.12
Nodes (9): _CachedFile, PromptBuilder, test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role(), build(), test_prompt_picks_up_a_new_file_and_falls_back_without_system(), test_prompt_reads_every_document_in_the_workspace() (+1 more)

### Community 78 - "check_secrets.py"
Cohesion: 0.43
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "pytest"
Cohesion: 0.25
Nodes (11): AccessDenied, city(), ok(), test_case_tricks_do_not_work_on_windows(), test_closed_places_are_refused_for_bots(), test_hut_only_for_the_person_being_served(), test_in_a_group_only_the_group_hut_is_open(), test_open_places_and_own_apartment_are_allowed() (+3 more)

### Community 93 - "fence/SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 117 - "ZaloError"
Cohesion: 0.20
Nodes (3): _import_zlapi(), _is_network_error(), test_network_errors_are_detected_through_zlapi_wrapping()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 129 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 134 - "ToolContext"
Cohesion: 0.10
Nodes (35): base_url(), configured(), env_values(), request(), server_config(), _assign(), _cancel(), _event_fields() (+27 more)

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 699 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **88 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `handover_job.py`, `event`, `userdata_paths.py`, `auto_update.py`, `Bot`, `MemoryDataStore`, `test_desktop.py`, `test_vps_supervisor.py`, `handover.py`, `create_app`, `test_handover.py`, `desktop_app.py`, `json`, `PersonalZalo`, `personal_account.py`, `config.py`, `GroupStore`, `command_line.py`, `residents/pylos/__init__.py`, `.apply_settings`, `.decide`, `admin_web_server.py`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07033248081841433 - nodes in this community are weakly interconnected._
- **Why does `4. Web (quanlythoigian)` connect `test_assign_events.py` to `admin_page.js`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_assign_events.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05187074829931973 - nodes in this community are weakly interconnected._