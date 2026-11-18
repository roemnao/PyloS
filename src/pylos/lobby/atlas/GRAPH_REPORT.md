# Graph Report - pylosSever  (2026-11-17)

## Corpus Check
- 202 files · ~142,345 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .woff2 9, (none) 5, .css 2)

## Summary
- 2235 nodes · 4912 edges · 190 communities (104 shown, 86 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 573 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `71e47c3b`
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
- QrLogin
- PyloS — rules for Claude Code
- Desktop
- clock/vietnam_time.py
- storage.py
- admin_page.js
- create_app
- agent_tools/__init__.py
- handover.py
- Settings
- steps
- 4. Các bước
- json
- common.ps1
- test_entrypoints.py
- mention_tags.py
- test_personal.py
- Kế hoạch: Server Bot Zalo chạy Agent (AI)
- AdminDevices
- PersonalZalo
- Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết
- Tasks: [FEATURE NAME]
- personal_account.py
- Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc
- 3. Phần A — sửa code Python (`region_map.py`)
- speckit-analyze/SKILL.md
- Settings
- GroupStore
- .__init__
- command_line.py
- Tray
- gemini_agent.py
- HistoryStore
- server_info.py
- ZaloClient
- GeminiAgent
- 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)
- Turn
- receive_webhook.py
- FailedStore
- status_info
- steps
- test_handover.py
- README (Bot trợ lý Zalo Gemini)
- Natural chat as Lila
- test_polling_delivers_updates_and_survives_errors
- FakeAgent
- test_remote_proxy.py
- config.py
- qr_login.py
- Execution Steps
- test_google_login.py
- Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)
- PromptBuilder
- test_filter.py
- Feature Specification: [FEATURE NAME]
- check_secrets.py
- PendingLogins
- owner_commands.py
- Ba vai trò: basic-user, leader, owner
- pytest
- fence/SYSTEM.md
- message_handler.py
- speckit-plan/SKILL.md
- P2. Đăng nhập Google riêng của PyloS
- gateway (bot chạy nền)
- SYSTEM.md
- zalo-assistant-bot
- 5. Phần C — kiểm thử
- ZaloError
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- test_zalo_qr_login_saves_session_and_enables_personal
- ToolContext
- speckit-specify/SKILL.md
- speckit-tasks/SKILL.md
- Core Principles
- Core Principles
- 11. Kế hoạch: giao diện quản lý bot (web dashboard)
- Implementation Plan: [FEATURE]
- InstanceLock
- test_regions_file.py
- speckit-checklist/SKILL.md
- Cách dùng bot trên Zalo
- FakeZalo
- speckit-clarify/SKILL.md
- speckit-implement/SKILL.md
- speckit-constitution/SKILL.md
- test_updater.py
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- test_vps_supervisor.py
- test_config_client_webhook.py
- Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động
- validate
- is_running
- local
- pair
- make_settings
- path_guard.py
- RedactFilter
- 4. Web (quanlythoigian)
- AdminSessions
- Model shift: which kind of work is this?

## God Nodes (most connected - your core abstractions)
1. `Settings` - 104 edges
2. `create_app()` - 82 edges
3. `event()` - 55 edges
4. `now_ms()` - 45 edges
5. `send()` - 44 edges
6. `ToolContext` - 38 edges
7. `Bot` - 37 edges
8. `main()` - 36 edges
9. `GroupStore` - 34 edges
10. `Desktop` - 33 edges

## Surprising Connections (you probably didn't know these)
- `Hard rules` --references--> `migrate_to_city()`  [INFERRED]
  CLAUDE.md → src/pylos/lobby/dispatch/shared/userdata_paths.py
- `W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng)` --references--> `web()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/conftest.py
- `W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền` --references--> `role()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/lobby/dispatch/test_roles.py
- `B6. Phía PyloS` --references--> `region_of()`  [INFERRED]
  src/pylos/management/owner/private_plans/graphify_regions_plan.md → tests/lobby/atlas/test_regions_file.py
- `P2. Đăng nhập Google riêng của PyloS` --references--> `id_token()`  [INFERRED]
  src/pylos/management/managers/plans/KE-HOACH-CAP-NHAT-2026-11-01.md → tests/management/owner/test_google_login.py

## Import Cycles
- None detected.

## Communities (190 total, 86 thin omitted)

### Community 0 - "FailedStore"
Cohesion: 0.14
Nodes (10): SeenStore, JsonLinesFile, test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist(), test_group_teams_and_leader_added_by(), test_jsonl_append_rewrite_and_utf8(), test_jsonl_skips_broken_lines(), test_lone_surrogate_does_not_crash_write() (+2 more)

### Community 1 - "handover_job.py"
Cohesion: 0.07
Nodes (40): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+32 more)

### Community 2 - "test_assign_events.py"
Cohesion: 0.06
Nodes (15): FakeWeb, basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team() (+7 more)

### Community 3 - "event"
Cohesion: 0.10
Nodes (52): event(), lines(), send(), test_every_message_logged_but_only_passed_ones_reach_session(), test_not_allowed_chat_is_not_logged(), send(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks() (+44 more)

### Community 4 - "test_admin.py"
Cohesion: 0.08
Nodes (6): client(), env_path(), test_bot_control_uses_gateway(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host()

### Community 5 - "userdata_paths.py"
Cohesion: 0.13
Nodes (19): _prepare_home(), app_home(), _backup_for_huts(), _backup_userdata(), _city_old_running(), _clean_env(), is_frozen(), migrate_all() (+11 more)

### Community 6 - "auto_update.py"
Cohesion: 0.17
Nodes (16): _find_uv(), _git(), hold_state(), install_libs(), last_good(), mark_good(), pending_commits(), python_for_pip() (+8 more)

### Community 7 - "Bot"
Cohesion: 0.07
Nodes (7): Decision, MessageFilter, IncomingMessage, Bot, Job, ZaloSender, test_tagging_personal_account_answers_and_strips_tag()

### Community 8 - "MemoryDataStore"
Cohesion: 0.17
Nodes (8): _clean_map(), _clean_teams(), MemoryDataStore, _read(), memorydata(), test_store_trims_when_over_keep(), test_tool_reads_only_own_chat_and_filters_keyword(), test_memorydata_api_shows_filter_result_and_respects_history_switch()

### Community 9 - "split_message"
Cohesion: 0.14
Nodes (14): parse_event(), parse_updates(), _to_ms(), _max_prefix(), split_message(), to_plain_text(), utf16_len(), test_dedupe_key_without_message_id_is_stable() (+6 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.09
Nodes (8): _free_port(), test_autostart_registry_roundtrip(), test_env_template_keeps_data_inside_the_city(), test_free_port_skips_busy_port(), test_frozen_child_gets_its_own_unpack_dir(), test_logging_without_console(), test_no_visible_subprocess_calls_left_in_source(), test_system_commands_never_open_a_console_window()

### Community 11 - "Envelope"
Cohesion: 0.13
Nodes (8): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload(), test_overhead_per_message_is_far_below_one_second()

### Community 12 - "UsageStore"
Cohesion: 0.09
Nodes (8): today_vn(), StatsStore, UsageStore, JsonObjectFile, test_object_file_recovers_from_corruption(), test_usage_store_rolls_over_by_day(), test_groups_list_includes_seen_but_not_allowed_chats(), test_status_reports_alerts_and_stats()

### Community 13 - "QrLogin"
Cohesion: 0.22
Nodes (6): Cancelled, QrLogin, QrLoginError, QrStatus, test_cancel_stops_before_next_request(), test_declined_and_expired()

### Community 14 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 15 - "Desktop"
Cohesion: 0.13
Nodes (5): Desktop, watch(), work(), work(), update_flag_file()

### Community 17 - "storage.py"
Cohesion: 0.18
Nodes (4): is_chatter(), fold(), safe_name(), atomic_write_text()

### Community 18 - "admin_page.js"
Cohesion: 0.09
Nodes (72): W4. Giao diện web gộp: phần sử dụng đầy đủ + mục Tài khoản riêng + Quản trị theo quyền, ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText() (+64 more)

### Community 19 - "create_app"
Cohesion: 0.08
Nodes (39): path(), create_app(), auth_options(), _base_url(), config_error(), devices(), _failed(), failed_action() (+31 more)

### Community 20 - "agent_tools/__init__.py"
Cohesion: 0.13
Nodes (11): discover(), _load_external(), Tool, ToolRegistry, tools(), _gemini(), test_gemini_classify_requests_json_and_counts_tokens(), test_external_tools_are_loaded_and_broken_ones_skipped() (+3 more)

### Community 21 - "handover.py"
Cohesion: 0.18
Nodes (12): backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip(), _sources() (+4 more)

### Community 22 - "Settings"
Cohesion: 0.12
Nodes (27): clear_pid(), clear_standby(), _end_task(), follow_log(), _kill(), pid_path(), read_pid(), Result (+19 more)

### Community 23 - "steps"
Cohesion: 0.06
Nodes (30): args, inputs, integration, spec, default, prompt, type, any (+22 more)

### Community 24 - "4. Các bước"
Cohesion: 0.15
Nodes (13): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+5 more)

### Community 25 - "json"
Cohesion: 0.15
Nodes (11): load_session(), test_load_session_reads_qr_file_and_manual_cookies(), legacy_home(), test_city_migration_keeps_what_is_already_in_the_new_place(), test_city_migration_waits_for_the_old_version(), test_migrates_everything_to_userdata(), test_migrates_userdata_into_the_city_with_a_backup_and_drops_the_old_workspace(), test_restores_git_tracked_defaults() (+3 more)

### Community 26 - "common.ps1"
Cohesion: 0.16
Nodes (19): Find-SpecifyRoot(), Format-SpecKitCommand(), Get-CurrentBranch(), Get-FeaturePathsEnv(), Get-InvokeSeparator(), Get-NormalizedPriority(), Get-Python3Command(), Get-RepoRoot() (+11 more)

### Community 27 - "test_entrypoints.py"
Cohesion: 0.09
Nodes (12): folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports(), test_settings_rejects_bad_or_forbidden_values(), test_console_script_targets_exist(), test_every_module_imports(), test_every_top_level_package_is_bundled_into_the_exe() (+4 more)

### Community 28 - "mention_tags.py"
Cohesion: 0.18
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 29 - "test_personal.py"
Cohesion: 0.15
Nodes (11): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+3 more)

### Community 30 - "Kế hoạch: Server Bot Zalo chạy Agent (AI)"
Cohesion: 0.12
Nodes (16): 0. Quyết định đã chốt, 10. Tiến độ, 1. Chọn kênh Zalo, 1a. Zalo Bot Platform: các sự kiện đã xác minh, 2. Kiến trúc, 3. Công nghệ, 3a. Nhận tin khi chạy local, chưa có domain, 3b. Chạy 24/7 khi chưa có VPS (+8 more)

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 35 - "personal_account.py"
Cohesion: 0.27
Nodes (6): _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming(), test_to_incoming_maps_fields_and_marks_own_messages()

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.17
Nodes (12): 0. Luật đã chốt, 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa), 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại (+4 more)

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 38 - "speckit-analyze/SKILL.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 39 - "Settings"
Cohesion: 0.16
Nodes (11): _bool(), ConfigError, _csv(), _int(), Settings, _shift_profile(), 13. Điều khiển bot trên VPS từ ứng dụng ở máy này, test_defaults_and_validation() (+3 more)

### Community 40 - "GroupStore"
Cohesion: 0.15
Nodes (6): GroupState, GroupStore, change(), _mtime(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders()

### Community 41 - ".__init__"
Cohesion: 0.27
Nodes (4): FilterInstructions, test_reloads_when_file_changes(), test_shipped_model_shift_guide_covers_every_profile(), test_shipped_soul_matches_default_prompt()

### Community 42 - "command_line.py"
Cohesion: 0.09
Nodes (22): _admin(), _attach_parent_console(), _build_agent(), _console(), ConsoleZalo, _health(), main(), _mark_good() (+14 more)

### Community 44 - "Tray"
Cohesion: 0.10
Nodes (9): make_icon(), write_ico(), Tray, command(), is_enabled(), migrate(), set_enabled(), _registry_autostart() (+1 more)

### Community 45 - "gemini_agent.py"
Cohesion: 0.17
Nodes (6): playground(), Agent, AgentReply, EchoAgent, done(), ToolStep

### Community 46 - "HistoryStore"
Cohesion: 0.27
Nodes (5): HistoryStore, 11.5 Bảo mật (quan trọng nhất của phần này), clear_history(), test_history_tail_trim_and_safe_filename(), test_history_view_and_toggle()

### Community 47 - "server_info.py"
Cohesion: 0.15
Nodes (9): code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state(), _uptime_seconds() (+1 more)

### Community 48 - "ZaloClient"
Cohesion: 0.22
Nodes (5): ZaloClient, run_polling(), _sleep_or_stop(), 5. Luồng xử lý một tin nhắn, 7. Lộ trình

### Community 49 - "GeminiAgent"
Cohesion: 0.16
Nodes (4): GeminiAgent, _is_transient(), _rejects_thinking(), _usage_tokens()

### Community 50 - "12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)"
Cohesion: 0.17
Nodes (12): 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu, 12.2 Chọn cách làm, 12.3 Kiến trúc, 12.4 Biểu tượng khay (system tray), 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được, 12.6 Đóng gói (+4 more)

### Community 51 - "Turn"
Cohesion: 0.21
Nodes (16): Turn, FakeModels, make_agent(), response(), test_empty_reply_falls_back(), test_function_calling_loop(), test_plain_reply_and_history_conversion(), test_reply_drops_thinking_when_model_rejects_it() (+8 more)

### Community 53 - "FailedStore"
Cohesion: 0.18
Nodes (6): FailedStore, change(), change(), done_file(), test_stats_activity_and_failed_stores(), test_failed_list_and_dismiss()

### Community 56 - "status_info"
Cohesion: 0.22
Nodes (6): standby_info(), ready(), ready(), status_info(), StateStore, status()

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 58 - "test_handover.py"
Cohesion: 0.15
Nodes (14): make_side(), run_job(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_checks_data_layout_version(), test_import_endpoint_streams_and_refuses_running(), test_import_refused_while_bot_running(), test_import_rejects_non_bundle() (+6 more)

### Community 59 - "README (Bot trợ lý Zalo Gemini)"
Cohesion: 0.20
Nodes (10): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, settings.env, userdata (config, data, system) (+2 more)

### Community 60 - "Natural chat as Lila"
Cohesion: 0.17
Nodes (11): Habits, Humor, Layout of each reply, Natural chat as Lila, Nox, Patterns (from Vietnamese news-site comments, Nov 2026), Real examples from this person (read these first), Rules (+3 more)

### Community 62 - "FakeAgent"
Cohesion: 0.14
Nodes (13): agent(), FakeAgent, FakeZalo, make_bot(), factory(), web(), zalo(), ask() (+5 more)

### Community 63 - "test_remote_proxy.py"
Cohesion: 0.11
Nodes (9): health(), 4b. Lưu trữ `.txt` và workspace `.md`, AdminContext, history(), client(), seen(), test_http_remote_url_is_refused(), test_not_configured() (+1 more)

### Community 66 - "qr_login.py"
Cohesion: 0.16
Nodes (9): on_update(), apply_session(), cookies_for(), make_imei(), save_qr_png(), ZaloSession, test_apply_session_saves_file_and_enables_personal_mode(), test_cookies_for_prefers_specific_domain() (+1 more)

### Community 67 - "Execution Steps"
Cohesion: 0.12
Nodes (15): 1. Initialize Convergence Context, 2. Load Artifacts (Progressive Disclosure), 3. Build the Intent Inventory, 4. Assess the Codebase and Classify Findings, 5. Assign Severity, 6. Present the In-Session Findings Summary, 7. Append Convergence Tasks (or report converged), 8. Provide Next Actions (Handoff) (+7 more)

### Community 68 - "test_google_login.py"
Cohesion: 0.15
Nodes (13): approve(), fake_google(), exchange(), id_token(), make_client(), test_bad_state_expired_code_and_invalid_tokens(), test_connect_vps_with_google_saves_key_without_showing_it(), test_device_keys_survive_restart_and_are_stored_hashed() (+5 more)

### Community 69 - "Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)"
Cohesion: 0.13
Nodes (13): Cấu hình `settings.env` (máy Windows và VPS), Lỗi thường gặp, Tạo OAuth client (một lần, ~10 phút), Đăng nhập trang quản lý PyloS bằng Google, 1. Service cho bot, 2. Cho user `pylos` điều khiển đúng 2 service (chọn MỘT cách), 3. Bật chế độ systemd cho bot trên VPS, 4. nginx (+5 more)

### Community 70 - "PromptBuilder"
Cohesion: 0.10
Nodes (11): _CachedFile, PromptBuilder, test_bot_adds_missing_at_sign_end_to_end(), test_bot_tells_model_member_names(), test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role(), build() (+3 more)

### Community 71 - "test_filter.py"
Cohesion: 0.21
Nodes (22): agent(), decide(), make_filter(), factory(), msg(), _Ok, test_ai_error_budget_and_disabled_in_mode_all(), test_ai_stage_returns_profile_in_same_call() (+14 more)

### Community 72 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 78 - "check_secrets.py"
Cohesion: 0.43
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 80 - "PendingLogins"
Cohesion: 0.18
Nodes (5): auth_url(), challenge(), decode_id_token(), exchange(), PendingLogins

### Community 82 - "owner_commands.py"
Cohesion: 0.14
Nodes (11): CommandHandler, describe_mode(), help_text(), parse_command(), ParsedCommand, _pick_people(), allows(), required_role() (+3 more)

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "pytest"
Cohesion: 0.25
Nodes (11): AccessDenied, city(), ok(), test_case_tricks_do_not_work_on_windows(), test_closed_places_are_refused_for_bots(), test_hut_only_for_the_person_being_served(), test_in_a_group_only_the_group_hut_is_open(), test_open_places_and_own_apartment_are_allowed() (+3 more)

### Community 93 - "fence/SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 94 - "message_handler.py"
Cohesion: 0.10
Nodes (8): RateLimiter, role_of(), strip_name_prefix(), role(), test_allows(), test_role_of(), test_bot_never_calls_web_on_plain_message(), test_server_client_paths_are_only_scheduling_paths()

### Community 99 - "speckit-plan/SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, Key rules, Mandatory Post-Execution Hooks, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases (+2 more)

### Community 103 - "P2. Đăng nhập Google riêng của PyloS"
Cohesion: 0.25
Nodes (4): 3. PyloS, P1. Tách PyloS khỏi web: chỉ còn API bot lịch, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 117 - "ZaloError"
Cohesion: 0.12
Nodes (4): ZaloError, _import_zlapi(), _is_network_error(), test_network_errors_are_detected_through_zlapi_wrapping()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 129 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 134 - "ToolContext"
Cohesion: 0.11
Nodes (34): base_url(), configured(), env_values(), request(), server_config(), _assign(), _cancel(), _event_fields() (+26 more)

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

### Community 162 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 163 - "InstanceLock"
Cohesion: 0.21
Nodes (6): gui_running(), AlreadyRunning, InstanceLock, _locks_held(), _old_version_running(), test_instance_lock_blocks_second_instance()

### Community 164 - "test_regions_file.py"
Cohesion: 0.28
Nodes (4): B6. Phía PyloS, region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions()

### Community 165 - "speckit-checklist/SKILL.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 166 - "Cách dùng bot trên Zalo"
Cohesion: 0.14
Nodes (12): README (Bot trợ lý Zalo Gemini), Chạy trên acc Zalo cá nhân (zlapi, QR), Chế độ webhook, Zalo Bot Platform, Ba vai trò, Các file trong thư mục này, Cách dùng bot trên Zalo, Giao lịch cho người khác (web iforgotmywayhome) (+4 more)

### Community 168 - "speckit-clarify/SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 170 - "speckit-implement/SKILL.md"
Cohesion: 0.29
Nodes (6): Completion Report, Done When, Mandatory Post-Execution Hooks, Outline, Pre-Execution Checks, User Input

### Community 171 - "speckit-constitution/SKILL.md"
Cohesion: 0.33
Nodes (5): Outline, Post-Execution Checks, Pre-Execution Checks, Scope Guard, User Input

### Community 172 - "test_updater.py"
Cohesion: 0.18
Nodes (10): a(), git(), push_change(), repos(), test_install_libs_explains_when_nothing_can_install(), test_install_libs_falls_back_to_uv_when_the_venv_has_no_pip(), fake_run(), test_local_changes_conflict_is_reported() (+2 more)

### Community 173 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 174 - "test_vps_supervisor.py"
Cohesion: 0.22
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 175 - "test_config_client_webhook.py"
Cohesion: 0.18
Nodes (4): _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_webhook_checks_secret_and_forwards_payload()

### Community 177 - "Kế hoạch cập nhật 01/11/2026: tách PyloS, giao diện mới, web người dùng đầy đủ, phân quyền, Google Lịch tự động"
Cohesion: 0.15
Nodes (12): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 5. Thứ tự đưa lên production, 6. Kiểm thử toàn hệ thống (sau bước 8 của mục 5) (+4 more)

### Community 178 - "validate"
Cohesion: 0.23
Nodes (9): read_settings(), remote_login_poll(), remote_logout(), write_secret(), write_settings(), clean_value(), read_values(), update() (+1 more)

### Community 179 - "is_running"
Cohesion: 0.31
Nodes (9): _rollback(), _update(), _zalo_login(), is_running(), lock_for(), restart(), rollback_app(), update_app() (+1 more)

### Community 180 - "local"
Cohesion: 0.22
Nodes (6): clean_env(), local(), no_web(), test_exchange_uses_pkce_and_checks_audience(), handler(), run()

### Community 181 - "pair"
Cohesion: 0.22
Nodes (3): clean_env(), pair(), running()

### Community 182 - "make_settings"
Cohesion: 0.25
Nodes (6): make_settings(), test_shift_profile_settings(), test_require_personal_needs_qr_session(), test_desktop_bot_actions_report_to_tray(), test_ensure_admin_token_writes_once(), test_gateway_stops_bot_gracefully_with_flag()

### Community 183 - "path_guard.py"
Cohesion: 0.43
Nodes (3): Actor, check_access(), _inside()

### Community 185 - "4. Web (quanlythoigian)"
Cohesion: 0.33
Nodes (6): 4. Web (quanlythoigian), W0. Chuẩn bị (bắt buộc trước khi sửa code), W1. Một kiểu đăng nhập (Gmail) + phân quyền Owner / Technician / User + gộp về một tên miền, W2. Dữ liệu riêng cho từng người (nền cho Lịch / Công việc / Đề xuất / Nguồn trên web người dùng), W3. Google Lịch tự động: đăng nhập là xin quyền, cho phép là chạy mãi, W5. Dọn dẹp sau khi PyloS mới đã chạy ổn ≥ 7 ngày

### Community 187 - "Model shift: which kind of work is this?"
Cohesion: 0.50
Nodes (3): Model shift: which kind of work is this?, Profiles, Tie-breaks

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 875 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **86 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Settings` to `handover_job.py`, `Bot`, `MemoryDataStore`, `Desktop`, `storage.py`, `create_app`, `handover.py`, `Settings`, `json`, `PersonalZalo`, `11. Kế hoạch: giao diện quản lý bot (web dashboard)`, `InstanceLock`, `.__init__`, `command_line.py`, `test_vps_supervisor.py`, `server_info.py`, `validate`, `is_running`, `receive_webhook.py`, `make_settings`, `status_info`, `test_handover.py`, `test_remote_proxy.py`, `config.py`, `message_handler.py`, `P2. Đăng nhập Google riêng của PyloS`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `FailedStore` be split into smaller, more focused modules?**
  _Cohesion score 0.1383399209486166 - nodes in this community are weakly interconnected._
- **Why does `create_app()` connect `create_app` to `handover_job.py`, `test_admin.py`, `auto_update.py`, `MemoryDataStore`, `split_message`, `Desktop`, `clock/vietnam_time.py`, `agent_tools/__init__.py`, `Settings`, `AdminDevices`, `Settings`, `command_line.py`, `gemini_agent.py`, `HistoryStore`, `server_info.py`, `validate`, `is_running`, `receive_webhook.py`, `pair`, `local`, `status_info`, `AdminSessions`, `test_handover.py`, `test_remote_proxy.py`, `config.py`, `test_google_login.py`, `PendingLogins`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07199297629499561 - nodes in this community are weakly interconnected._