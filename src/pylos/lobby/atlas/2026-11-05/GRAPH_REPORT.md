# Graph Report - pylosSever  (2026-11-05)

## Corpus Check
- 177 files · ~108,480 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 9, (none) 3, .css 2)

## Summary
- 1911 nodes · 4553 edges · 157 communities (82 shown, 75 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 542 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2fd1dec5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tray_icon.py
- handover_job.py
- auto_update.py
- Bot Tests
- test_vps_supervisor.py
- userdata_paths.py
- Admin Devices
- Bot
- MemoryDataStore
- conftest.py
- message_handler.py
- PyloS — Kế hoạch dựng "Thành chính"
- JsonObjectFile
- google_login.py
- PyloS City
- test_desktop.py
- Admin App Tests
- test_personal.py
- admin_page.js
- create_app
- .handle
- test_handover.py
- bot_process.py
- command_line.py
- desktop_app.py
- main
- time
- message_handler.py
- discover
- test_entrypoints.py
- Kế hoạch: Server Bot Zalo chạy Agent (AI)
- atlas.py
- zalo/mention_tags.py
- JsonLinesFile
- .handle
- PersonalZalo
- test_assign_events.py
- test_filter.py
- Desktop
- _console
- GroupStore
- test_remote_proxy.py
- ConfigError
- residents/pylos/__init__.py
- receive_webhook.py
- region_map.py
- HistoryStore
- handover/handover.py
- ConsoleZalo
- admin_web_server.py
- _is_transient
- dispatch (Toà điều phối)
- FailedStore
- office (Toà văn phòng)
- clock/vietnam_time.py
- Settings
- steps
- `gate` — Khu cổng
- Cách dùng bot trên Zalo
- now_ms
- ToolRegistry
- .__init__
- ZaloClient
- fence (Hàng rào)
- guest_house (Toà khách)
- load_session
- side_gate (Cổng phụ)
- AdminDevices
- atlas (Toà bản đồ)
- library (Toà thư viện)
- .decide
- owner (Toà Owner)
- residents (Toà nhà dân)
- test_schedule_tool.py
- personal_account.py
- Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động
- 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)
- check_secrets.py
- test_city_skeleton.py
- Ba vai trò: basic-user, leader, owner
- pytest
- test_paths.py
- receive_polling.py
- test_region_map.py
- crossings
- test_memorydata.py
- test_polling.py
- gateway (bot chạy nền)
- test_zalo_qr_login_saves_session_and_enables_personal
- SYSTEM.md
- zalo-assistant-bot
- ToolContext
- AdminSessions
- managers (Toà quản lý)
- zalo/reply_formatting.py
- GeminiAgent
- test_atlas.py

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
- ``gate/main_gate` — Cổng chính` --references--> `zalo()`  [INFERRED]
  src/pylos/lobby/atlas/maps/atlas.md → tests/conftest.py
- `4b. Lưu trữ `.txt` và workspace `.md`` --references--> `seen()`  [INFERRED]
  src/pylos/management/managers/plans/PLAN.md → tests/test_remote_proxy.py
- `W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng)` --references--> `web()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/conftest.py
- `Apartments` --references--> `zalo()`  [INFERRED]
  src/pylos/gate/main_gate/README.md → tests/conftest.py
- `2.2 `gate` — Khu cổng` --references--> `zalo()`  [INFERRED]
  src/pylos/lobby/atlas/maps/city.md → tests/conftest.py

## Import Cycles
- None detected.

## Communities (157 total, 75 thin omitted)

### Community 0 - "tray_icon.py"
Cohesion: 0.21
Nodes (4): command(), migrate(), set_enabled(), is_frozen()

### Community 1 - "handover_job.py"
Cohesion: 0.07
Nodes (41): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+33 more)

### Community 2 - "auto_update.py"
Cohesion: 0.19
Nodes (16): _mark_good(), _rollback(), _git(), hold_state(), last_good(), mark_good(), pending_commits(), python_for_pip() (+8 more)

### Community 3 - "Bot Tests"
Cohesion: 0.12
Nodes (45): event(), send(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks(), test_allow_all_off_by_default(), test_assign_allowed_all_still_opens_everyone(), test_bare_trigger_asks_what_to_do(), test_budget_exceeded_turns_all_into_default_and_notifies_once() (+37 more)

### Community 4 - "test_vps_supervisor.py"
Cohesion: 0.20
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 5 - "userdata_paths.py"
Cohesion: 0.15
Nodes (12): _prepare_home(), run_gui(), gui_running(), AlreadyRunning, InstanceLock, _clean_env(), migrate_legacy(), needs_migration() (+4 more)

### Community 6 - "Admin Devices"
Cohesion: 0.11
Nodes (19): approve(), clean_env(), fake_google(), exchange(), id_token(), local(), make_client(), no_web() (+11 more)

### Community 7 - "Bot"
Cohesion: 0.14
Nodes (3): _console(), Bot, Job

### Community 8 - "MemoryDataStore"
Cohesion: 0.20
Nodes (5): MemoryDataStore, _read(), memorydata(), test_memorydata_api_shows_filter_result_and_respects_history_switch(), test_tool_reads_only_own_chat_and_filters_keyword()

### Community 9 - "conftest.py"
Cohesion: 0.12
Nodes (11): agent(), FakeAgent, FakeWeb, FakeZalo, make_bot(), factory(), web(), zalo() (+3 more)

### Community 10 - "message_handler.py"
Cohesion: 0.22
Nodes (4): is_chatter(), strip_name_prefix(), test_bot_never_calls_web_on_plain_message(), test_server_client_paths_are_only_scheduling_paths()

### Community 11 - "PyloS — Kế hoạch dựng "Thành chính""
Cohesion: 0.08
Nodes (15): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), a(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload() (+7 more)

### Community 12 - "JsonObjectFile"
Cohesion: 0.09
Nodes (13): ready(), ready(), today_vn(), StateStore, StatsStore, UsageStore, JsonObjectFile, test_groups_list_includes_seen_but_not_allowed_chats() (+5 more)

### Community 13 - "google_login.py"
Cohesion: 0.06
Nodes (22): on_update(), apply_session(), Cancelled, cookies_for(), make_imei(), QrLogin, QrLoginError, QrStatus (+14 more)

### Community 14 - "PyloS City"
Cohesion: 0.05
Nodes (39): Conventions, Finding things: one map, two layers, graphify, Hard rules, PyloS — rules for Claude Code, Tests, health(), City tree (+31 more)

### Community 15 - "test_desktop.py"
Cohesion: 0.08
Nodes (10): make_settings(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_ensure_admin_token_writes_once(), test_env_template_keeps_data_inside_userdata(), test_frozen_child_gets_its_own_unpack_dir(), test_gateway_stops_bot_gracefully_with_flag(), test_logging_without_console() (+2 more)

### Community 16 - "Admin App Tests"
Cohesion: 0.07
Nodes (10): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host() (+2 more)

### Community 17 - "test_personal.py"
Cohesion: 0.13
Nodes (14): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_load_session_reads_qr_file_and_manual_cookies(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags() (+6 more)

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (72): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+64 more)

### Community 19 - "create_app"
Cohesion: 0.11
Nodes (32): create_app(), auth_options(), _base_url(), config_error(), devices(), google_begin(), google_callback(), google_poll() (+24 more)

### Community 20 - ".handle"
Cohesion: 0.19
Nodes (7): required_role(), role_of(), groups(), role(), test_allows(), test_required_role(), test_role_of()

### Community 21 - "test_handover.py"
Cohesion: 0.11
Nodes (17): clean_env(), make_side(), pair(), run_job(), running(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_checks_data_layout_version() (+9 more)

### Community 22 - "bot_process.py"
Cohesion: 0.16
Nodes (17): clear_pid(), _end_task(), _kill(), lock_for(), pid_path(), read_pid(), run_hidden(), Service (+9 more)

### Community 23 - "command_line.py"
Cohesion: 0.13
Nodes (3): _attach_parent_console(), setup_logging(), _message_box()

### Community 24 - "desktop_app.py"
Cohesion: 0.19
Nodes (5): ensure_admin_token(), ensure_home(), app_home(), _move(), _writable()

### Community 25 - "main"
Cohesion: 0.17
Nodes (18): _admin(), main(), _update(), _utf8_console(), _zalo_login(), follow_log(), is_running(), restart() (+10 more)

### Community 26 - "time"
Cohesion: 0.18
Nodes (10): _free_port(), code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state() (+2 more)

### Community 28 - "discover"
Cohesion: 0.20
Nodes (6): discover(), _load_external(), tools(), test_tools_list_has_only_builtin_tools_by_default(), test_discover_skips_example_template(), test_external_tools_are_loaded_and_broken_ones_skipped()

### Community 29 - "test_entrypoints.py"
Cohesion: 0.15
Nodes (6): test_console_script_targets_exist(), test_every_module_imports(), test_every_top_level_package_is_bundled_into_the_exe(), test_package_data_patterns_match_files(), test_python_dash_m_bot_still_works(), top_packages()

### Community 30 - "Kế hoạch: Server Bot Zalo chạy Agent (AI)"
Cohesion: 0.12
Nodes (16): 0. Quyết định đã chốt, 10. Tiến độ, 1. Chọn kênh Zalo, 1a. Zalo Bot Platform: các sự kiện đã xác minh, 2. Kiến trúc, 3. Công nghệ, 3a. Nhận tin khi chạy local, chưa có domain, 3b. Chạy 24/7 khi chưa có VPS (+8 more)

### Community 31 - "atlas.py"
Cohesion: 0.20
Nodes (16): assign(), build(), file_targets(), Graph, graph_age(), load_graph(), load_map(), main() (+8 more)

### Community 32 - "zalo/mention_tags.py"
Cohesion: 0.19
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 33 - "JsonLinesFile"
Cohesion: 0.12
Nodes (10): SeenStore, atomic_write_text(), JsonLinesFile, test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist(), test_history_tail_trim_and_safe_filename(), test_jsonl_append_rewrite_and_utf8(), test_jsonl_skips_broken_lines() (+2 more)

### Community 34 - ".handle"
Cohesion: 0.21
Nodes (9): CommandHandler, describe_mode(), help_text(), parse_command(), ParsedCommand, _pick_people(), allows(), test_pick_people_prefers_real_tags_and_skips_bot() (+1 more)

### Community 36 - "test_assign_events.py"
Cohesion: 0.21
Nodes (12): basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team(), test_list_shows_who_has_it_in_their_app() (+4 more)

### Community 37 - "test_filter.py"
Cohesion: 0.24
Nodes (19): agent(), decide(), _gemini(), make_filter(), factory(), msg(), _Ok, test_ai_error_budget_and_disabled_in_mode_all() (+11 more)

### Community 38 - "Desktop"
Cohesion: 0.07
Nodes (10): Desktop, watch(), work(), work(), update_flag_file(), make_icon(), write_ico(), Tray (+2 more)

### Community 39 - "_console"
Cohesion: 0.33
Nodes (5): parse_event(), parse_updates(), _to_ms(), test_dedupe_key_without_message_id_is_stable(), test_parse_updates_docs_sample()

### Community 40 - "GroupStore"
Cohesion: 0.09
Nodes (18): _clean_map(), _clean_teams(), GroupState, GroupStore, change(), _mtime(), 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22) (+10 more)

### Community 41 - "test_remote_proxy.py"
Cohesion: 0.13
Nodes (6): AdminContext, client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 42 - "ConfigError"
Cohesion: 0.12
Nodes (17): _bool(), ConfigError, _csv(), _int(), read_settings(), remote_logout(), write_secret(), write_settings() (+9 more)

### Community 43 - "residents/pylos/__init__.py"
Cohesion: 0.17
Nodes (7): playground(), Agent, AgentReply, EchoAgent, done(), ToolStep, slow_reply()

### Community 44 - "receive_webhook.py"
Cohesion: 0.10
Nodes (8): RedactFilter, create_app(), webhook(), _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_redact_filter_hides_secrets(), test_webhook_checks_secret_and_forwards_payload()

### Community 45 - "region_map.py"
Cohesion: 0.19
Nodes (5): build(), main(), pack_region(), plan_regions(), region_of()

### Community 46 - "HistoryStore"
Cohesion: 0.23
Nodes (5): HistoryStore, safe_name(), 11.5 Bảo mật (quan trọng nhất của phần này), clear_history(), test_history_view_and_toggle()

### Community 47 - "handover/handover.py"
Cohesion: 0.18
Nodes (12): backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip(), _sources() (+4 more)

### Community 52 - "dispatch (Toà điều phối)"
Cohesion: 0.50
Nodes (3): Apartments, dispatch (Toà điều phối), Rules

### Community 53 - "FailedStore"
Cohesion: 0.14
Nodes (7): fold(), FailedStore, change(), change(), done_file(), _failed(), test_failed_list_and_dismiss()

### Community 54 - "office (Toà văn phòng)"
Cohesion: 0.50
Nodes (3): Apartments, office (Toà văn phòng), Rules

### Community 55 - "clock/vietnam_time.py"
Cohesion: 0.17
Nodes (5): now_vn(), _current_time(), _CachedFile, PromptBuilder, test_tagging_personal_account_answers_and_strips_tag()

### Community 56 - "Settings"
Cohesion: 0.21
Nodes (10): _build_agent(), _run(), request_stop(), watch_stop_flag(), clear_standby(), set_standby(), standby_path(), Settings (+2 more)

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 58 - "`gate` — Khu cổng"
Cohesion: 0.14
Nodes (13): Apartments, main_gate (Cổng chính), Rules, `gate/fence` — Hàng rào, `gate/guest_house` — Toà khách, `gate` — Khu cổng, `gate/main_gate` — Cổng chính, `gate/side_gate` — Cổng phụ (+5 more)

### Community 59 - "Cách dùng bot trên Zalo"
Cohesion: 0.05
Nodes (35): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+27 more)

### Community 60 - "now_ms"
Cohesion: 0.19
Nodes (9): _health(), format_status(), ago(), _registry_autostart(), standby_info(), status_info(), now_ms(), server() (+1 more)

### Community 61 - "ToolRegistry"
Cohesion: 0.20
Nodes (13): Tool, ToolRegistry, Turn, make_agent(), response(), test_empty_reply_falls_back(), test_function_calling_loop(), test_plain_reply_and_history_conversion() (+5 more)

### Community 64 - "fence (Hàng rào)"
Cohesion: 0.50
Nodes (3): Apartments, fence (Hàng rào), Rules

### Community 65 - "guest_house (Toà khách)"
Cohesion: 0.50
Nodes (3): Apartments, guest_house (Toà khách), Rules

### Community 66 - "load_session"
Cohesion: 0.15
Nodes (4): _import_zlapi(), _is_network_error(), load_session(), test_network_errors_are_detected_through_zlapi_wrapping()

### Community 67 - "side_gate (Cổng phụ)"
Cohesion: 0.50
Nodes (3): Apartments, Rules, side_gate (Cổng phụ)

### Community 69 - "atlas (Toà bản đồ)"
Cohesion: 0.50
Nodes (3): Apartments, atlas (Toà bản đồ), Rules

### Community 70 - "library (Toà thư viện)"
Cohesion: 0.40
Nodes (4): Apartments, library (Toà thư viện), Rules, Vetting rule

### Community 71 - ".decide"
Cohesion: 0.23
Nodes (3): Decision, MessageFilter, IncomingMessage

### Community 72 - "owner (Toà Owner)"
Cohesion: 0.50
Nodes (3): Apartments, owner (Toà Owner), Rules

### Community 73 - "residents (Toà nhà dân)"
Cohesion: 0.50
Nodes (3): Apartments, residents (Toà nhà dân), Rules

### Community 77 - "personal_account.py"
Cohesion: 0.30
Nodes (5): _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming()

### Community 78 - "Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động"
Cohesion: 0.11
Nodes (18): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 4. Web (quanlythoigian), 5. Thứ tự đưa lên production (+10 more)

### Community 80 - "12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)"
Cohesion: 0.17
Nodes (12): 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu, 12.2 Chọn cách làm, 12.3 Kiến trúc, 12.4 Biểu tượng khay (system tray), 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được, 12.6 Đóng gói (+4 more)

### Community 82 - "check_secrets.py"
Cohesion: 0.36
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 84 - "test_city_skeleton.py"
Cohesion: 0.24
Nodes (4): folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports()

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 87 - "pytest"
Cohesion: 0.25
Nodes (5): FakeModels, test_transient_errors_are_retried_but_others_are_not(), generate_content(), __init__(), test_gemini_classify_requests_json_and_counts_tokens()

### Community 88 - "test_paths.py"
Cohesion: 0.36
Nodes (4): legacy_home(), test_migrates_everything_to_userdata(), test_restores_git_tracked_defaults(), test_settings_read_migrated_env()

### Community 98 - "crossings"
Cohesion: 0.33
Nodes (3): crossings(), district(), in_region()

### Community 99 - "test_memorydata.py"
Cohesion: 0.53
Nodes (5): lines(), send(), test_every_message_logged_but_only_passed_ones_reach_session(), test_not_allowed_chat_is_not_logged(), test_store_trims_when_over_keep()

### Community 105 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 134 - "ToolContext"
Cohesion: 0.10
Nodes (34): base_url(), configured(), env_values(), request(), server_config(), _assign(), _cancel(), _event_fields() (+26 more)

### Community 159 - "AdminSessions"
Cohesion: 0.25
Nodes (4): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối

### Community 261 - "managers (Toà quản lý)"
Cohesion: 0.50
Nodes (3): Apartments, managers (Toà quản lý), Rules

### Community 273 - "zalo/reply_formatting.py"
Cohesion: 0.23
Nodes (9): _max_prefix(), split_message(), to_plain_text(), utf16_len(), test_split_counts_emoji_as_two_units(), test_split_prefers_paragraph_boundaries(), test_split_short_message_unchanged(), test_split_without_spaces_hard_cuts() (+1 more)

### Community 326 - "test_atlas.py"
Cohesion: 0.24
Nodes (3): _city(), test_region_shows_links_crossing_the_border_and_hides_tests_by_default(), test_where_finds_files_and_symbols()

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 665 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **75 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `create_app` to `handover_job.py`, `auto_update.py`, `test_vps_supervisor.py`, `ToolContext`, `Admin Devices`, `MemoryDataStore`, `google_login.py`, `PyloS City`, `Admin App Tests`, `zalo/reply_formatting.py`, `GeminiAgent`, `test_handover.py`, `bot_process.py`, `command_line.py`, `main`, `discover`, `test_remote_proxy.py`, `ConfigError`, `residents/pylos/__init__.py`, `HistoryStore`, `admin_web_server.py`, `FailedStore`, `clock/vietnam_time.py`, `Settings`, ``gate` — Khu cổng`, `now_ms`, `ToolRegistry`, `ZaloClient`, `AdminDevices`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07075873827791987 - nodes in this community are weakly interconnected._
- **Why does `Settings` connect `Settings` to `handover_job.py`, `auto_update.py`, `test_vps_supervisor.py`, `userdata_paths.py`, `Bot`, `MemoryDataStore`, `test_desktop.py`, `create_app`, `test_handover.py`, `bot_process.py`, `command_line.py`, `desktop_app.py`, `main`, `time`, `message_handler.py`, `AdminSessions`, `PersonalZalo`, `Desktop`, `GroupStore`, `test_remote_proxy.py`, `ConfigError`, `handover/handover.py`, `ConsoleZalo`, `admin_web_server.py`, `now_ms`, `.__init__`, `.decide`, `personal_account.py`, `test_paths.py`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Bot Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.11840888066604996 - nodes in this community are weakly interconnected._