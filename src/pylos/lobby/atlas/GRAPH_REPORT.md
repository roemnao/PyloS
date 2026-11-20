# Graph Report - pylosSever  (2026-11-20)

## Corpus Check
- 218 files · ~156,367 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .woff2 9, (none) 5, .css 2)

## Summary
- 2614 nodes · 6065 edges · 185 communities (117 shown, 68 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 713 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `676dcadf`
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
- IncomingMessage
- message_handler.py
- split_message
- test_desktop.py
- Envelope
- UsageStore
- google_login.py
- os
- Desktop
- residents/pylos/__init__.py
- command_line.py
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
- .__init__
- PersonalZalo
- Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết
- Tasks: [FEATURE NAME]
- check_url
- Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc
- 3. Phần A — sửa code Python (`region_map.py`)
- speckit-analyze/SKILL.md
- config.py
- GroupStore
- test_web_reader.py
- desktop_app.py
- test_agent.py
- filter.py
- Turn
- AdminContext
- ZaloClient
- Kế hoạch: Server Bot Zalo chạy Agent (AI)
- GeminiAgent
- 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)
- test_web_fallback.py
- receive_webhook.py
- schedule_web.py
- Bot
- .login
- validate
- steps
- test_handover.py
- test_vps_supervisor.py
- Natural chat as Lila
- incoming_message.py
- FakeAgent
- InstanceLock
- subprocess
- data_stores.py
- MemoryDataStore
- Execution Steps
- test_google_login.py
- Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)
- PromptBuilder
- test_filter.py
- Feature Specification: [FEATURE NAME]
- Settings
- test_paths.py
- check_secrets.py
- owner_commands.py
- test_media_flow.py
- test_web_fixes.py
- Ba vai trò: basic-user, leader, owner
- FakeModels
- fence/SYSTEM.md
- .__init__
- web_reader.py
- speckit-plan/SKILL.md
- Cách dùng bot trên Zalo
- AdminSessions
- gateway (bot chạy nền)
- Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động
- SYSTEM.md
- zalo-assistant-bot
- 5. Phần C — kiểm thử
- make_icon
- AdminDevices
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- is_running
- local
- test_zalo_qr_login_saves_session_and_enables_personal
- ToolContext
- speckit-specify/SKILL.md
- speckit-tasks/SKILL.md
- Core Principles
- Core Principles
- 11. Kế hoạch: giao diện quản lý bot (web dashboard)
- PyloS — rules for Claude Code
- Implementation Plan: [FEATURE]
- _fails_over
- test_regions_file.py
- speckit-checklist/SKILL.md
- storage.py
- Giao diện quản lý web (127.0.0.1:8081)
- speckit-clarify/SKILL.md
- speckit-implement/SKILL.md
- speckit-constitution/SKILL.md
- 4. Web (quanlythoigian)
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- run_polling
- ConsoleZalo
- _log_path
- backends
- test_bot_split.py
- _TextExtractor
- test_memorydata.py
- brave
- cdn
- Model shift: which kind of work is this, and which model runs it?

## God Nodes (most connected - your core abstractions)
1. `Settings` - 104 edges
2. `create_app()` - 90 edges
3. `event()` - 75 edges
4. `Bot` - 53 edges
5. `now_ms()` - 51 edges
6. `ToolContext` - 49 edges
7. `send()` - 49 edges
8. `main()` - 37 edges
9. `Desktop` - 37 edges
10. `IncomingMessage` - 36 edges

## Surprising Connections (you probably didn't know these)
- `Hard rules` --references--> `migrate_to_city()`  [INFERRED]
  CLAUDE.md → src/pylos/lobby/dispatch/shared/userdata_paths.py
- `W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng)` --references--> `web()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/conftest.py
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py
- `P2. Đăng nhập Google riêng của PyloS` --references--> `id_token()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/management/owner/test_google_login.py

## Import Cycles
- None detected.

## Communities (185 total, 68 thin omitted)

### Community 0 - "FailedStore"
Cohesion: 0.09
Nodes (17): FailedStore, change(), change(), SeenStore, JsonLinesFile, done_file(), _failed(), test_group_leaders_persist_and_old_records_load() (+9 more)

### Community 1 - "handover_job.py"
Cohesion: 0.07
Nodes (41): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+33 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.06
Nodes (15): FakeWeb, basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team() (+7 more)

### Community 3 - "event"
Cohesion: 0.11
Nodes (53): event(), send(), shift_bot(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks(), test_allow_all_off_by_default(), test_assign_allowed_all_still_opens_everyone(), test_bare_trigger_asks_what_to_do() (+45 more)

### Community 4 - "test_admin.py"
Cohesion: 0.07
Nodes (11): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_includes_seen_but_not_allowed_chats(), test_groups_list_shows_leaders(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx() (+3 more)

### Community 5 - "userdata_paths.py"
Cohesion: 0.12
Nodes (19): _prepare_home(), ensure_home(), app_home(), _backup_for_huts(), _backup_userdata(), _city_old_running(), _clean_env(), migrate_all() (+11 more)

### Community 6 - "auto_update.py"
Cohesion: 0.16
Nodes (18): _mark_good(), _rollback(), _find_uv(), _git(), hold_state(), install_libs(), last_good(), mark_good() (+10 more)

### Community 7 - "IncomingMessage"
Cohesion: 0.18
Nodes (3): Decision, is_chatter(), MessageFilter

### Community 8 - "message_handler.py"
Cohesion: 0.11
Nodes (15): CommandHandler, describe_mode(), describe_model(), help_text(), parse_command(), ParsedCommand, allows(), required_role() (+7 more)

### Community 9 - "split_message"
Cohesion: 0.13
Nodes (17): _blocks(), _max_prefix(), _merge(), split_message(), split_reply(), to_plain_text(), utf16_len(), test_code_block_and_list_stay_together() (+9 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.08
Nodes (9): _free_port(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_env_template_keeps_data_inside_the_city(), test_free_port_skips_busy_port(), test_frozen_child_gets_its_own_unpack_dir(), test_logging_without_console(), test_no_visible_subprocess_calls_left_in_source() (+1 more)

### Community 11 - "Envelope"
Cohesion: 0.07
Nodes (18): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), a(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload() (+10 more)

### Community 12 - "UsageStore"
Cohesion: 0.09
Nodes (15): ready(), ready(), today_vn(), _clean_map(), _clean_teams(), DailyCounter, StateStore, StatsStore (+7 more)

### Community 13 - "google_login.py"
Cohesion: 0.06
Nodes (20): apply_session(), Cancelled, cookies_for(), make_imei(), QrLogin, QrLoginError, QrStatus, ZaloSession (+12 more)

### Community 14 - "os"
Cohesion: 0.21
Nodes (9): code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state(), _uptime_seconds() (+1 more)

### Community 15 - "Desktop"
Cohesion: 0.14
Nodes (5): Desktop, watch(), work(), work(), update_flag_file()

### Community 16 - "residents/pylos/__init__.py"
Cohesion: 0.22
Nodes (5): Agent, AgentReply, done(), ToolStep, slow_reply()

### Community 17 - "command_line.py"
Cohesion: 0.08
Nodes (6): _build_agent(), _message_box(), now_vn(), ensure_admin_token(), _current_time(), EchoAgent

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (73): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+65 more)

### Community 19 - "create_app"
Cohesion: 0.09
Nodes (34): body(), create_app(), auth_options(), _base_url(), config_error(), devices(), google_begin(), google_callback() (+26 more)

### Community 20 - "agent_tools/__init__.py"
Cohesion: 0.11
Nodes (11): discover(), _load_external(), Tool, ToolRegistry, tools(), test_gemini_classify_requests_json_and_counts_tokens(), test_external_tools_are_loaded_and_broken_ones_skipped(), test_tools_hidden_when_disabled() (+3 more)

### Community 21 - "handover.py"
Cohesion: 0.18
Nodes (12): backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip(), _sources() (+4 more)

### Community 22 - "Settings"
Cohesion: 0.13
Nodes (24): clear_standby(), _end_task(), follow_log(), _kill(), Result, run_hidden(), run_update_service(), Service (+16 more)

### Community 23 - "steps"
Cohesion: 0.06
Nodes (30): args, inputs, integration, spec, default, prompt, type, any (+22 more)

### Community 24 - "4. Các bước"
Cohesion: 0.15
Nodes (13): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+5 more)

### Community 25 - "test_media_fetch.py"
Cohesion: 0.09
Nodes (27): fetch_attachment(), Limits, MediaError, MediaFile, pick_mime(), sniff_mime(), hut_media_dir(), MediaStore (+19 more)

### Community 26 - "common.ps1"
Cohesion: 0.16
Nodes (19): Find-SpecifyRoot(), Format-SpecKitCommand(), Get-CurrentBranch(), Get-FeaturePathsEnv(), Get-InvokeSeparator(), Get-NormalizedPriority(), Get-Python3Command(), Get-RepoRoot() (+11 more)

### Community 27 - "pytest"
Cohesion: 0.05
Nodes (31): AccessDenied, Actor, check_access(), _inside(), folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports() (+23 more)

### Community 28 - "mention_tags.py"
Cohesion: 0.19
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 29 - "test_personal.py"
Cohesion: 0.15
Nodes (12): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+4 more)

### Community 30 - "json"
Cohesion: 0.12
Nodes (18): _as_dict(), attachment_of(), load_session(), _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming() (+10 more)

### Community 31 - ".__init__"
Cohesion: 0.12
Nodes (13): FilterInstructions, parse_profiles(), Profile, test_parse_profiles_table_and_defaults(), ask(), CapturingAgent, msg(), test_filter_uses_apartment_instructions_else_default() (+5 more)

### Community 32 - "PersonalZalo"
Cohesion: 0.13
Nodes (4): ZaloError, PersonalZalo, send(), flaky()

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

### Community 39 - "config.py"
Cohesion: 0.13
Nodes (12): _bool(), ConfigError, _csv(), _int(), FieldSpec, _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token() (+4 more)

### Community 40 - "GroupStore"
Cohesion: 0.17
Nodes (4): GroupState, GroupStore, change(), _mtime()

### Community 41 - "test_web_reader.py"
Cohesion: 0.13
Nodes (24): html_response(), public_dns(), read(), search_call(), serve(), test_disabled_tool_cannot_be_called(), test_http_error_is_reported(), test_huge_page_is_cut_not_loaded_whole() (+16 more)

### Community 42 - "desktop_app.py"
Cohesion: 0.12
Nodes (3): RedactFilter, setup_logging(), test_redact_filter_hides_secrets()

### Community 43 - "test_agent.py"
Cohesion: 0.25
Nodes (18): api_error(), chain_agent(), make_agent(), PerModel, response(), test_classify_uses_fallback_models(), test_empty_reply_falls_back(), test_failed_model_rests_for_a_while_instead_of_being_retried_every_message() (+10 more)

### Community 44 - "filter.py"
Cohesion: 0.15
Nodes (5): BotContext, detect_category(), ensure_correct_model(), test_bot_never_calls_web_on_plain_message(), test_server_client_paths_are_only_scheduling_paths()

### Community 45 - "Turn"
Cohesion: 0.23
Nodes (15): Turn, FakeFiles, grounded(), make(), media_file(), test_expired_file_uri_uploads_again(), test_inline_budget_is_shared_across_turns(), test_large_photo_is_uploaded() (+7 more)

### Community 46 - "AdminContext"
Cohesion: 0.12
Nodes (8): health(), 4b. Lưu trữ `.txt` và workspace `.md`, history(), client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 47 - "ZaloClient"
Cohesion: 0.28
Nodes (3): _zalo_call(), ZaloClient, failed_action()

### Community 48 - "Kế hoạch: Server Bot Zalo chạy Agent (AI)"
Cohesion: 0.11
Nodes (18): 0. Quyết định đã chốt, 10. Tiến độ, 1. Chọn kênh Zalo, 1a. Zalo Bot Platform: các sự kiện đã xác minh, 2. Kiến trúc, 3. Công nghệ, 3a. Nhận tin khi chạy local, chưa có domain, 3b. Chạy 24/7 khi chưa có VPS (+10 more)

### Community 49 - "GeminiAgent"
Cohesion: 0.17
Nodes (3): GeminiAgent, _usage_tokens(), test_search_without_grounding_metadata()

### Community 50 - "12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)"
Cohesion: 0.17
Nodes (12): 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu, 12.2 Chọn cách làm, 12.3 Kiến trúc, 12.4 Biểu tượng khay (system tray), 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được, 12.6 Đóng gói (+4 more)

### Community 51 - "test_web_fallback.py"
Cohesion: 0.12
Nodes (18): SearchingAgent, private(), test_all_sources_failing_lists_reasons(), test_auto_falls_through_to_brave_when_tavily_fails(), test_auto_uses_tavily_after_gemini_quota(), test_gemini_working_never_touches_tavily(), test_no_key_and_tavily_provider_means_no_search_function(), test_tavily_counts_toward_daily_limit() (+10 more)

### Community 52 - "receive_webhook.py"
Cohesion: 0.22
Nodes (3): create_app(), webhook(), test_webhook_checks_secret_and_forwards_payload()

### Community 53 - "schedule_web.py"
Cohesion: 0.21
Nodes (15): base_url(), configured(), env_values(), server_config(), _agenda(), _complete_task(), _config(), _create_event() (+7 more)

### Community 54 - "Bot"
Cohesion: 0.09
Nodes (7): _console(), IncomingMessage, ago(), now_ms(), Bot, Job, test_tagging_personal_account_answers_and_strips_tag()

### Community 55 - ".login"
Cohesion: 0.20
Nodes (3): _import_zlapi(), _is_network_error(), test_network_errors_are_detected_through_zlapi_wrapping()

### Community 56 - "validate"
Cohesion: 0.23
Nodes (9): read_settings(), remote_login_poll(), remote_logout(), write_secret(), write_settings(), clean_value(), read_values(), update() (+1 more)

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 58 - "test_handover.py"
Cohesion: 0.09
Nodes (18): AdminContext, clean_env(), make_side(), pair(), run_job(), running(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions() (+10 more)

### Community 59 - "test_vps_supervisor.py"
Cohesion: 0.24
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 60 - "Natural chat as Lila"
Cohesion: 0.17
Nodes (11): Habits, Humor, Layout of each reply, Natural chat as Lila, Nox, Patterns (from Vietnamese news-site comments, Nov 2026), Real examples from this person (read these first), Rules (+3 more)

### Community 61 - "incoming_message.py"
Cohesion: 0.31
Nodes (5): parse_event(), parse_updates(), _to_ms(), test_dedupe_key_without_message_id_is_stable(), test_parse_updates_docs_sample()

### Community 62 - "FakeAgent"
Cohesion: 0.15
Nodes (14): agent(), FakeAgent, FakeZalo, make_bot(), factory(), make_settings(), web(), zalo() (+6 more)

### Community 63 - "InstanceLock"
Cohesion: 0.21
Nodes (10): run_gui(), gui_running(), AlreadyRunning, InstanceLock, _locks_held(), _old_version_running(), test_city_migration_waits_for_the_old_version(), test_hut_migration_waits_for_the_running_bot() (+2 more)

### Community 64 - "subprocess"
Cohesion: 0.17
Nodes (7): Tray, command(), is_enabled(), migrate(), set_enabled(), _registry_autostart(), is_frozen()

### Community 65 - "data_stores.py"
Cohesion: 0.12
Nodes (6): ActiveModelStore, HistoryStore, hut_file(), clear_history(), test_group_model_mode_and_held_model_are_exposed(), test_history_view_and_toggle()

### Community 66 - "MemoryDataStore"
Cohesion: 0.17
Nodes (5): MemoryDataStore, _read(), memorydata(), test_tool_reads_only_own_chat_and_filters_keyword(), test_memorydata_api_shows_filter_result_and_respects_history_switch()

### Community 67 - "Execution Steps"
Cohesion: 0.12
Nodes (15): 1. Initialize Convergence Context, 2. Load Artifacts (Progressive Disclosure), 3. Build the Intent Inventory, 4. Assess the Codebase and Classify Findings, 5. Assign Severity, 6. Present the In-Session Findings Summary, 7. Append Convergence Tasks (or report converged), 8. Provide Next Actions (Handoff) (+7 more)

### Community 68 - "test_google_login.py"
Cohesion: 0.17
Nodes (14): approve(), fake_google(), exchange(), id_token(), make_client(), test_bad_state_expired_code_and_invalid_tokens(), test_connect_vps_with_google_saves_key_without_showing_it(), test_default_remote_url_and_off() (+6 more)

### Community 69 - "Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)"
Cohesion: 0.13
Nodes (13): Cấu hình `settings.env` (máy Windows và VPS), Lỗi thường gặp, Tạo OAuth client (một lần, ~10 phút), Đăng nhập trang quản lý PyloS bằng Google, 1. Service cho bot, 2. Cho user `pylos` điều khiển đúng 2 service (chọn MỘT cách), 3. Bật chế độ systemd cho bot trên VPS, 4. nginx (+5 more)

### Community 70 - "PromptBuilder"
Cohesion: 0.13
Nodes (9): _CachedFile, PromptBuilder, test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role(), build(), test_prompt_picks_up_a_new_file_and_falls_back_without_system(), test_prompt_reads_every_document_in_the_workspace() (+1 more)

### Community 71 - "test_filter.py"
Cohesion: 0.19
Nodes (26): agent(), decide(), decide_with(), _gemini(), make_filter(), factory(), msg(), _Ok (+18 more)

### Community 72 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 76 - "Settings"
Cohesion: 0.11
Nodes (18): _admin(), _attach_parent_console(), _health(), main(), _run(), request_stop(), watch_stop_flag(), _utf8_console() (+10 more)

### Community 77 - "test_paths.py"
Cohesion: 0.18
Nodes (10): legacy_home(), old_chat_data(), test_chat_data_moves_into_one_hut_per_person_or_group(), test_city_migration_keeps_what_is_already_in_the_new_place(), test_hut_migration_keeps_a_hut_file_that_already_exists(), test_migrates_everything_to_userdata(), test_migrates_userdata_into_the_city_with_a_backup_and_drops_the_old_workspace(), test_restores_git_tracked_defaults() (+2 more)

### Community 78 - "check_secrets.py"
Cohesion: 0.43
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 80 - "owner_commands.py"
Cohesion: 0.20
Nodes (5): fold(), _pick_people(), match_member(), resolve_people(), test_pick_people_prefers_real_tags_and_skips_bot()

### Community 82 - "test_media_flow.py"
Cohesion: 0.22
Nodes (17): media_msg(), push(), test_download_failure_gets_notice(), test_followup_disabled_by_zero_turns(), test_followup_reattaches_recent_media_only(), test_group_caption_with_trigger_passes(), test_group_media_from_someone_else_after_call_is_ignored(), test_group_media_without_call_is_ignored() (+9 more)

### Community 84 - "test_web_fixes.py"
Cohesion: 0.18
Nodes (14): oembed(), public_dns(), read(), serve(), test_blocked_site_gets_clear_message(), test_brave_search_errors(), test_brave_search_parses_results(), test_user_agent_carries_contact_only_when_set() (+6 more)

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "FakeModels"
Cohesion: 0.17
Nodes (9): FakeModels, test_reply_drops_thinking_when_model_rejects_it(), generate_content(), test_reply_retries_once_on_timeout(), generate_content(), test_transient_errors_are_retried_but_others_are_not(), generate_content(), __init__() (+1 more)

### Community 93 - "fence/SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 94 - ".__init__"
Cohesion: 0.09
Nodes (6): RateLimiter, MediaRef, run(), run(), ZaloSender, test_rate_limiter_window()

### Community 98 - "web_reader.py"
Cohesion: 0.10
Nodes (14): brave_search(), configure(), extract_basic(), extract_main(), fetch_page(), FetchError, _read_page(), _read_youtube() (+6 more)

### Community 99 - "speckit-plan/SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, Key rules, Mandatory Post-Execution Hooks, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases (+2 more)

### Community 101 - "Cách dùng bot trên Zalo"
Cohesion: 0.14
Nodes (12): README (Bot trợ lý Zalo Gemini), Chạy trên acc Zalo cá nhân (zlapi, QR), Chế độ webhook, Zalo Bot Platform, Ba vai trò, Các file trong thư mục này, Cách dùng bot trên Zalo, Giao lịch cho người khác (web iforgotmywayhome) (+4 more)

### Community 103 - "AdminSessions"
Cohesion: 0.17
Nodes (5): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối, AdminSessions

### Community 105 - "Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động"
Cohesion: 0.17
Nodes (11): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 5. Thứ tự đưa lên production, 6. Kiểm thử toàn hệ thống (sau bước 8 của mục 5) (+3 more)

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 116 - "make_icon"
Cohesion: 0.22
Nodes (3): make_icon(), write_ico(), test_icons()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 122 - "is_running"
Cohesion: 0.31
Nodes (9): _update(), _zalo_login(), on_update(), save_qr_png(), is_running(), restart(), rollback_app(), update_app() (+1 more)

### Community 128 - "local"
Cohesion: 0.22
Nodes (6): clean_env(), local(), no_web(), test_exchange_uses_pkce_and_checks_audience(), handler(), run()

### Community 129 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 134 - "ToolContext"
Cohesion: 0.23
Nodes (18): request(), _assign(), _cancel(), _event_fields(), _event_id(), _forget(), _is_own(), _list() (+10 more)

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
Cohesion: 0.17
Nodes (12): 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22), 11.1 Mục tiêu, 11.2 Kiến trúc, 11.3 Các trang, 11.4 API (JSON, dưới `/api`), 11.5 Bảo mật (quan trọng nhất của phần này), 11.6 Việc phải bổ sung vào bot hiện có (+4 more)

### Community 161 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 162 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 163 - "_fails_over"
Cohesion: 0.33
Nodes (3): _fails_over(), _is_transient(), _rejects_thinking()

### Community 164 - "test_regions_file.py"
Cohesion: 0.28
Nodes (4): B6. Phía PyloS, region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions()

### Community 165 - "speckit-checklist/SKILL.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 166 - "storage.py"
Cohesion: 0.17
Nodes (3): safe_name(), atomic_write_text(), test_polling_delivers_updates_and_survives_errors()

### Community 167 - "Giao diện quản lý web (127.0.0.1:8081)"
Cohesion: 0.20
Nodes (10): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, settings.env, userdata (config, data, system) (+2 more)

### Community 168 - "speckit-clarify/SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 170 - "speckit-implement/SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 171 - "speckit-constitution/SKILL.md"
Cohesion: 0.33
Nodes (5): Outline, Post-Execution Checks, Pre-Execution Checks, Scope Guard, User Input

### Community 172 - "4. Web (quanlythoigian)"
Cohesion: 0.33
Nodes (6): 4. Web (quanlythoigian), W0. Chuẩn bị (bắt buộc trước khi sửa code), W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền, W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng), W3. Google Lịch tự động: đăng nhập là xin quyền, cho phép là chạy mãi, W5. Dọn dẹp sau khi PyloS mới đã chạy ổn ≥ 7 ngày

### Community 173 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 176 - "_log_path"
Cohesion: 0.40
Nodes (5): path(), _log_path(), logs(), stream_logs(), tail()

### Community 178 - "test_bot_split.py"
Cohesion: 0.39
Nodes (5): send(), test_failed_part_stops_and_keeps_the_rest(), test_multiline_reply_goes_as_separate_messages(), test_reply_split_off_sends_one_message(), test_two_sends_to_one_chat_do_not_interleave()

### Community 180 - "test_memorydata.py"
Cohesion: 0.53
Nodes (5): lines(), send(), test_every_message_logged_but_only_passed_ones_reach_session(), test_not_allowed_chat_is_not_logged(), test_store_trims_when_over_keep()

### Community 187 - "Model shift: which kind of work is this, and which model runs it?"
Cohesion: 0.33
Nodes (5): How to choose (your job), Keep or switch, Model shift: which kind of work is this, and which model runs it?, Profile table (read by the code), Things you do not decide

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `Chạy trên acc Zalo cá nhân (zlapi, QR)`, `Chế độ webhook`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 976 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **68 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `handover_job.py`, `userdata_paths.py`, `auto_update.py`, `IncomingMessage`, `message_handler.py`, `os`, `Desktop`, `command_line.py`, `create_app`, `handover.py`, `Settings`, `json`, `PersonalZalo`, `11. Kế hoạch: giao diện quản lý bot (web dashboard)`, `config.py`, `desktop_app.py`, `ZaloClient`, `Bot`, `validate`, `test_handover.py`, `test_vps_supervisor.py`, `FakeAgent`, `InstanceLock`, `MemoryDataStore`, `test_google_login.py`, `test_paths.py`, `.__init__`, `AdminSessions`, `is_running`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 79 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 79 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `Chạy trên acc Zalo cá nhân (zlapi, QR)`, `Chế độ webhook` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `FailedStore` be split into smaller, more focused modules?**
  _Cohesion score 0.0944741532976827 - nodes in this community are weakly interconnected._
- **Why does `create_app()` connect `create_app` to `FailedStore`, `handover_job.py`, `local`, `test_admin.py`, `ToolContext`, `auto_update.py`, `split_message`, `UsageStore`, `google_login.py`, `os`, `command_line.py`, `agent_tools/__init__.py`, `Settings`, `config.py`, `desktop_app.py`, `Turn`, `AdminContext`, `ZaloClient`, `_log_path`, `GeminiAgent`, `Bot`, `validate`, `test_handover.py`, `test_vps_supervisor.py`, `data_stores.py`, `MemoryDataStore`, `test_google_login.py`, `PromptBuilder`, `Settings`, `AdminSessions`, `AdminDevices`, `is_running`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07327001356852103 - nodes in this community are weakly interconnected._