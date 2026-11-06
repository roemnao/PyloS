# Graph Report - pylosSever  (2026-11-06)

## Corpus Check
- 162 files · ~104,272 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 9, (none) 4, .css 2)

## Summary
- 1865 nodes · 4478 edges · 139 communities (68 shown, 71 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 545 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `17223f5a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Tray
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
- qr_login.py
- handover.py
- server_info.py
- admin_page.js
- create_app
- ToolRegistry
- test_handover.py
- Settings
- ZaloClient
- 4. Các bước
- 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)
- command_line.py
- pytest
- message_handler.py
- make_icon
- Kế hoạch: Server Bot Zalo chạy Agent (AI)
- create_app
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
- now_ms
- test_paths.py
- validate
- HistoryStore
- message_handler.py
- PendingLogins
- 11. Kế hoạch: giao diện quản lý bot (web dashboard)
- test_regions_file.py
- _zalo_call
- FakeWeb
- test_schedule_tool.py
- ZaloError
- _CachedFile
- MemoryDataStore
- steps
- Cách dùng bot trên Zalo
- parse_updates
- is_running
- 4. Web (quanlythoigian)
- test_remote_proxy.py
- test_google_login.py
- .decide
- FailedStore
- check_secrets.py
- Ba vai trò: basic-user, leader, owner
- test_vps_supervisor.py
- .on
- Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động
- gateway (bot chạy nền)
- SYSTEM.md
- zalo-assistant-bot
- 5. Phần C — kiểm thử
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- test_zalo_qr_login_saves_session_and_enables_personal
- ToolContext
- test_polling_delivers_updates_and_survives_errors
- split_message

## God Nodes (most connected - your core abstractions)
1. `Settings` - 103 edges
2. `create_app()` - 90 edges
3. `event()` - 53 edges
4. `now_ms()` - 44 edges
5. `send()` - 42 edges
6. `ToolContext` - 41 edges
7. `Desktop` - 37 edges
8. `main()` - 37 edges
9. `Bot` - 36 edges
10. `GroupStore` - 35 edges

## Surprising Connections (you probably didn't know these)
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py
- `4b. Lưu trữ `.txt` và workspace `.md`` --references--> `seen()`  [INFERRED]
  src/pylos/management/managers/plans/PLAN.md → tests/management/owner/test_remote_proxy.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py
- `test_logging_without_console()` --calls--> `setup_logging()`  [INFERRED]
  tests/gate/side_gate/test_desktop.py → src/pylos/gate/main_gate/logs/log_files.py
- `test_object_file_recovers_from_corruption()` --calls--> `JsonObjectFile`  [INFERRED]
  tests/lobby/dispatch/test_storage.py → src/pylos/lobby/dispatch/shared/text_files.py

## Import Cycles
- None detected.

## Communities (139 total, 71 thin omitted)

### Community 0 - "Tray"
Cohesion: 0.16
Nodes (7): Tray, command(), is_enabled(), migrate(), set_enabled(), _registry_autostart(), is_frozen()

### Community 1 - "handover_job.py"
Cohesion: 0.05
Nodes (44): RedactFilter, blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain() (+36 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.27
Nodes (11): basic(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team(), test_list_shows_who_has_it_in_their_app(), test_my_upcoming_events() (+3 more)

### Community 3 - "event"
Cohesion: 0.06
Nodes (58): agent(), event(), FakeAgent, FakeZalo, make_bot(), factory(), make_settings(), zalo() (+50 more)

### Community 4 - "test_admin.py"
Cohesion: 0.07
Nodes (11): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders(), test_memorydata_api_shows_filter_result_and_respects_history_switch(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx() (+3 more)

### Community 5 - "InstanceLock"
Cohesion: 0.14
Nodes (12): _prepare_home(), run_gui(), AlreadyRunning, InstanceLock, app_home(), _clean_env(), migrate_legacy(), needs_migration() (+4 more)

### Community 6 - "auto_update.py"
Cohesion: 0.19
Nodes (16): _mark_good(), _rollback(), _git(), hold_state(), last_good(), mark_good(), pending_commits(), python_for_pip() (+8 more)

### Community 7 - "Bot"
Cohesion: 0.15
Nodes (4): IncomingMessage, Bot, Job, test_tagging_personal_account_answers_and_strips_tag()

### Community 8 - "JsonLinesFile"
Cohesion: 0.13
Nodes (11): SeenStore, JsonLinesFile, test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist(), test_group_teams_and_leader_added_by(), test_history_tail_trim_and_safe_filename(), test_jsonl_append_rewrite_and_utf8(), test_jsonl_skips_broken_lines() (+3 more)

### Community 9 - "Settings"
Cohesion: 0.12
Nodes (15): _health(), _zalo_login(), on_update(), ready(), ready(), status_info(), _statuses(), _csv() (+7 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.08
Nodes (9): _free_port(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_env_template_keeps_data_inside_userdata(), test_free_port_skips_busy_port(), test_frozen_child_gets_its_own_unpack_dir(), test_logging_without_console(), test_no_visible_subprocess_calls_left_in_source() (+1 more)

### Community 11 - "PyloS — Kế hoạch dựng "Thành chính""
Cohesion: 0.09
Nodes (15): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), a(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload() (+7 more)

### Community 12 - "JsonObjectFile"
Cohesion: 0.10
Nodes (11): today_vn(), ActivityStore, StatsStore, UsageStore, JsonObjectFile, playground(), status(), test_usage_store_rolls_over_by_day() (+3 more)

### Community 13 - "QrLogin"
Cohesion: 0.11
Nodes (10): Cancelled, cookies_for(), QrLogin, QrLoginError, QrStatus, FakeResponse, FakeZalo, test_cancel_stops_before_next_request() (+2 more)

### Community 14 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 15 - "qr_login.py"
Cohesion: 0.16
Nodes (10): apply_session(), make_imei(), save_qr_png(), ZaloSession, atomic_write_text(), auth_url(), challenge(), decode_id_token() (+2 more)

### Community 16 - "handover.py"
Cohesion: 0.15
Nodes (13): backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip(), _sources() (+5 more)

### Community 17 - "server_info.py"
Cohesion: 0.20
Nodes (9): code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state(), _uptime_seconds() (+1 more)

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (72): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+64 more)

### Community 19 - "create_app"
Cohesion: 0.09
Nodes (36): path(), create_app(), auth_options(), _base_url(), config_error(), devices(), google_begin(), google_callback() (+28 more)

### Community 20 - "ToolRegistry"
Cohesion: 0.05
Nodes (34): discover(), _load_external(), Tool, ToolRegistry, 11.11 Tiến độ (2026-10-22), 11.3 Các trang, tools(), Agent (+26 more)

### Community 21 - "test_handover.py"
Cohesion: 0.10
Nodes (18): AdminContext, clean_env(), make_side(), pair(), run_job(), running(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions() (+10 more)

### Community 22 - "Settings"
Cohesion: 0.10
Nodes (27): _admin(), _attach_parent_console(), main(), _utf8_console(), clear_pid(), clear_standby(), _end_task(), follow_log() (+19 more)

### Community 24 - "4. Các bước"
Cohesion: 0.15
Nodes (13): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+5 more)

### Community 25 - "12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)"
Cohesion: 0.17
Nodes (12): 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu, 12.2 Chọn cách làm, 12.3 Kiến trúc, 12.4 Biểu tượng khay (system tray), 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được, 12.6 Đóng gói (+4 more)

### Community 26 - "command_line.py"
Cohesion: 0.09
Nodes (5): setup_logging(), _message_box(), ensure_admin_token(), ensure_home(), _move()

### Community 27 - "pytest"
Cohesion: 0.06
Nodes (25): AccessDenied, Actor, check_access(), _inside(), folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports() (+17 more)

### Community 28 - "message_handler.py"
Cohesion: 0.08
Nodes (13): is_chatter(), safe_name(), EchoAgent, ToolStep, strip_name_prefix(), FakeMessage, test_require_personal_needs_qr_session(), test_send_in_group_attaches_mentions_but_not_in_private() (+5 more)

### Community 29 - "make_icon"
Cohesion: 0.22
Nodes (3): make_icon(), write_ico(), test_icons()

### Community 30 - "Kế hoạch: Server Bot Zalo chạy Agent (AI)"
Cohesion: 0.12
Nodes (16): 0. Quyết định đã chốt, 10. Tiến độ, 1. Chọn kênh Zalo, 1a. Zalo Bot Platform: các sự kiện đã xác minh, 2. Kiến trúc, 3. Công nghệ, 3a. Nhận tin khi chạy local, chưa có domain, 3b. Chạy 24/7 khi chưa có VPS (+8 more)

### Community 31 - "create_app"
Cohesion: 0.18
Nodes (8): create_app(), health(), webhook(), 4. Cấu trúc thư mục, 4a. Cấu hình và bí mật để trống, 4b. Lưu trữ `.txt` và workspace `.md`, history(), test_webhook_checks_secret_and_forwards_payload()

### Community 32 - "zalo/mention_tags.py"
Cohesion: 0.19
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "owner_commands.py"
Cohesion: 0.19
Nodes (9): CommandHandler, describe_mode(), help_text(), parse_command(), ParsedCommand, _pick_people(), allows(), test_parse_command() (+1 more)

### Community 35 - "PersonalZalo"
Cohesion: 0.06
Nodes (14): _is_network_error(), _log_failure(), mention_names(), PersonalZalo, send(), to_incoming(), FakeApi, make_personal() (+6 more)

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.17
Nodes (12): 0. Luật đã chốt, 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa), 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại (+4 more)

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 38 - "Desktop"
Cohesion: 0.14
Nodes (5): Desktop, watch(), work(), work(), update_flag_file()

### Community 39 - "config.py"
Cohesion: 0.14
Nodes (10): _import_zlapi(), load_session(), _mention_ids(), _mention_list(), _bool(), ConfigError, _int(), clean_value() (+2 more)

### Community 40 - "GroupStore"
Cohesion: 0.17
Nodes (4): GroupState, GroupStore, change(), _mtime()

### Community 41 - "test_filter.py"
Cohesion: 0.24
Nodes (19): agent(), decide(), _gemini(), make_filter(), factory(), msg(), _Ok, test_ai_error_budget_and_disabled_in_mode_all() (+11 more)

### Community 42 - "now_ms"
Cohesion: 0.11
Nodes (9): _build_agent(), _console(), _run(), request_stop(), watch_stop_flag(), now_ms(), now_vn(), _current_time() (+1 more)

### Community 43 - "test_paths.py"
Cohesion: 0.25
Nodes (5): legacy_home(), test_migrates_everything_to_userdata(), test_restores_git_tracked_defaults(), test_settings_read_migrated_env(), test_skips_while_old_version_still_running()

### Community 45 - "validate"
Cohesion: 0.25
Nodes (8): read_settings(), remote_login_poll(), remote_logout(), write_secret(), write_settings(), read_values(), update(), validate()

### Community 46 - "HistoryStore"
Cohesion: 0.21
Nodes (4): RateLimiter, HistoryStore, clear_history(), test_history_view_and_toggle()

### Community 47 - "message_handler.py"
Cohesion: 0.24
Nodes (6): required_role(), role_of(), role(), test_allows(), test_required_role(), test_role_of()

### Community 49 - "11. Kế hoạch: giao diện quản lý bot (web dashboard)"
Cohesion: 0.20
Nodes (10): 11.10 Cần bạn xác nhận trước khi làm, 11.1 Mục tiêu, 11.2 Kiến trúc, 11.4 API (JSON, dưới `/api`), 11.5 Bảo mật (quan trọng nhất của phần này), 11.6 Việc phải bổ sung vào bot hiện có, 11.7 Thư mục dự kiến, 11.8 Lộ trình (+2 more)

### Community 50 - "test_regions_file.py"
Cohesion: 0.28
Nodes (4): B6. Phía PyloS, region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions()

### Community 54 - "ZaloError"
Cohesion: 0.16
Nodes (4): ZaloError, run_polling(), _sleep_or_stop(), test_listener_thread_dispatches_to_event_loop()

### Community 56 - "MemoryDataStore"
Cohesion: 0.23
Nodes (4): _clean_map(), _clean_teams(), MemoryDataStore, test_store_trims_when_over_keep()

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 59 - "Cách dùng bot trên Zalo"
Cohesion: 0.05
Nodes (35): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+27 more)

### Community 60 - "parse_updates"
Cohesion: 0.18
Nodes (6): parse_event(), parse_updates(), _to_ms(), ZaloSender, test_dedupe_key_without_message_id_is_stable(), test_parse_updates_docs_sample()

### Community 61 - "is_running"
Cohesion: 0.16
Nodes (17): _update(), gui_running(), is_running(), restart(), Result, run_update_service(), _start_systemd(), stop() (+9 more)

### Community 62 - "4. Web (quanlythoigian)"
Cohesion: 0.29
Nodes (7): 4. Web (quanlythoigian), W0. Chuẩn bị (bắt buộc trước khi sửa code), W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền, W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng), W3. Google Lịch tự động: đăng nhập là xin quyền, cho phép là chạy mãi, W5. Dọn dẹp sau khi PyloS mới đã chạy ổn ≥ 7 ngày, web()

### Community 63 - "test_remote_proxy.py"
Cohesion: 0.14
Nodes (5): client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 68 - "test_google_login.py"
Cohesion: 0.06
Nodes (26): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối, AdminDevices, AdminSessions, approve(), clean_env() (+18 more)

### Community 80 - "FailedStore"
Cohesion: 0.17
Nodes (7): FailedStore, change(), change(), done_file(), _failed(), test_stats_activity_and_failed_stores(), test_failed_list_and_dismiss()

### Community 82 - "check_secrets.py"
Cohesion: 0.43
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

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 129 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 134 - "ToolContext"
Cohesion: 0.09
Nodes (37): fold(), base_url(), configured(), env_values(), request(), server_config(), _assign(), _cancel() (+29 more)

### Community 273 - "split_message"
Cohesion: 0.23
Nodes (9): _max_prefix(), split_message(), to_plain_text(), utf16_len(), test_split_counts_emoji_as_two_units(), test_split_prefers_paragraph_boundaries(), test_split_short_message_unchanged(), test_split_without_spaces_hard_cuts() (+1 more)

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 648 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **71 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `handover_job.py`, `event`, `InstanceLock`, `auto_update.py`, `Bot`, `JsonObjectFile`, `handover.py`, `server_info.py`, `create_app`, `test_handover.py`, `Settings`, `command_line.py`, `message_handler.py`, `PersonalZalo`, `Desktop`, `config.py`, `now_ms`, `test_paths.py`, `httpx`, `validate`, `HistoryStore`, `11. Kế hoạch: giao diện quản lý bot (web dashboard)`, `_zalo_call`, `is_running`, `test_google_login.py`, `.decide`, `test_vps_supervisor.py`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053998632946001365 - nodes in this community are weakly interconnected._
- **Why does `create_app()` connect `create_app` to `handover_job.py`, `test_admin.py`, `ToolContext`, `auto_update.py`, `Settings`, `JsonObjectFile`, `handover.py`, `split_message`, `server_info.py`, `ToolRegistry`, `test_handover.py`, `Settings`, `ZaloClient`, `command_line.py`, `message_handler.py`, `create_app`, `config.py`, `now_ms`, `httpx`, `validate`, `HistoryStore`, `PendingLogins`, `is_running`, `test_remote_proxy.py`, `test_google_login.py`, `FailedStore`, `test_vps_supervisor.py`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `event` be split into smaller, more focused modules?**
  _Cohesion score 0.061621621621621624 - nodes in this community are weakly interconnected._