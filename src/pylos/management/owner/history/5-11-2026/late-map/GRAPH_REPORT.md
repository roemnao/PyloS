# Graph Report - pylosSever  (2026-11-05)

## Corpus Check
- 180 files · ~118,920 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: .woff2 9, (none) 3, .css 2)

## Summary
- 1817 nodes · 4372 edges · 157 communities (83 shown, 74 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 497 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9930db24`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Admin Web UI (JS)
- Handover Jobs
- Google Login
- Bot Tests
- Handover Export
- Assign Events
- Admin Devices
- Bot Queue & Chat
- Bot Process Control
- remote_server.py
- Command Handler
- Failed/Processed Stores
- Token Usage & Time
- ZaloClient
- PyloS Atlas
- Bot Package & Desktop Tests
- Admin App Tests
- Test Fakes
- typing
- Admin API Routes
- PersonalZalo
- test_handover.py
- Activity & Personal
- command_line.py
- now_ms
- ConfigError
- test_filter.py
- vietnam_time.py
- owner_commands.py
- Desktop
- admin_web_server.py
- atlas.py
- mention_tags.py
- tools/__init__.py
- userdata_paths.py
- PyloS — Kế hoạch dựng "Thành chính"
- test_assign_events.py
- auto_update.py
- GeminiAgent
- zalo
- to_incoming
- test_remote_proxy.py
- read_chat_memory.py
- FailedStore
- PyloS — Trắc nghiệm làm rõ cấu trúc "Thành chính"
- split_message
- MessageFilter
- time
- _is_network_error
- test_vps_supervisor.py
- PyloS — Trắc nghiệm vòng 3 (chốt chỗ vênh, VPS, bảo mật)
- FakeWeb
- city.md
- PyloS City
- test_city_skeleton.py
- conftest.py
- is_running
- message_handler.py
- pair
- incoming_message.py
- PyloS — rules for Claude Code
- test_zalo_qr_login_saves_session_and_enables_personal
- _log_path
- AdminSessions
- fence (Hàng rào)
- guest_house (Toà khách)
- Giao diện quản lý web (127.0.0.1:8081)
- side_gate (Cổng phụ)
- HistoryStore
- atlas (Toà bản đồ)
- library (Toà thư viện)
- office (Toà văn phòng)
- owner (Toà Owner)
- residents (Toà nhà dân)
- PyloS (bot Zalo + trang quản lý + VPS)
- README (Bot trợ lý Zalo Gemini)
- check_secrets.py
- google_begin
- Điều khiển bot trên VPS từ ZaloBot.exe
- Đăng nhập trang quản lý PyloS bằng Google
- Ba vai trò basic/leader/owner
- Ba vai trò: basic-user, leader, owner
- Tách PyloS khỏi web (P1)
- Giao diện quản lý bot (admin dashboard)
- Agent Gemini + function calling
- PyloS — Trắc nghiệm vòng 2 (đào sâu)
- Template SYSTEM.md (system prompt)
- Google Lịch tự động phía máy chủ (W3)
- Chống prompt injection
- gateway (bot chạy nền)
- zalo-assistant-bot

## God Nodes (most connected - your core abstractions)
1. `Settings` - 101 edges
2. `create_app()` - 96 edges
3. `event()` - 53 edges
4. `now_ms()` - 43 edges
5. `ToolContext` - 42 edges
6. `send()` - 42 edges
7. `GroupStore` - 37 edges
8. `Desktop` - 37 edges
9. `Bot` - 36 edges
10. `main()` - 35 edges

## Surprising Connections (you probably didn't know these)
- `PHẦN A — Chỗ vòng 2 vênh nhau` --references--> `systemctl()`  [INFERRED]
  PyloS-trac-nghiem-vong-3.md → src/bot/system/bot_process.py
- `3. Nguyên tắc làm (áp cho mọi giai đoạn)` --references--> `migrate_legacy()`  [INFERRED]
  PyloS-PLAN-thanh-chinh.md → src/bot/userdata_paths.py
- ``gate/main_gate` — Cổng chính` --references--> `logs()`  [INFERRED]
  docs/architecture/atlas.md → src/bot/ui/admin/admin_web_server.py
- ``gate/main_gate` — Cổng chính` --references--> `zalo()`  [INFERRED]
  docs/architecture/atlas.md → tests/conftest.py
- `2.2 `gate` — Khu cổng` --references--> `logs()`  [INFERRED]
  docs/architecture/city.md → src/bot/ui/admin/admin_web_server.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hệ thống chuyển bot giữa máy này và VPS** — docs_vps_dieu_khien_proxy, docs_vps_dieu_khien_standby, docs_vps_dieu_khien_handover, docs_vps_dieu_khien_device_key, docs_vps_dieu_khien_systemd [EXTRACTED 0.95]
- **Kế hoạch tách PyloS và web bot lịch (P1-P3, W0-W5)** — docs_ke_hoach_cap_nhat_2026_11_01_decoupling, docs_ke_hoach_cap_nhat_2026_11_01_google_login, docs_ke_hoach_cap_nhat_2026_11_01_theme, docs_ke_hoach_cap_nhat_2026_11_01_roles, docs_ke_hoach_cap_nhat_2026_11_01_userstore, docs_ke_hoach_cap_nhat_2026_11_01_gcal_sync, docs_ke_hoach_cap_nhat_2026_11_01_unified_ui, docs_ke_hoach_cap_nhat_2026_11_01_cleanup [EXTRACTED 1.00]
- **Bộ file chỉ dẫn của trợ lý (SYSTEM.md, MEMORY.md)** — src_bot_templates_system_doc, src_bot_templates_memory_doc, workspace_system_doc [INFERRED 0.85]

## Communities (157 total, 74 thin omitted)

### Community 0 - "Admin Web UI (JS)"
Cohesion: 0.10
Nodes (71): ago(), api(), ApiError, applyTarget(), boot(), buildNav(), bytesText(), connectVps() (+63 more)

### Community 1 - "Handover Jobs"
Cohesion: 0.13
Nodes (23): _bundle_path(), current(), Job, JobError, precheck(), _rollback_local(), work(), _rollback_remote() (+15 more)

### Community 2 - "Google Login"
Cohesion: 0.06
Nodes (24): _zalo_login(), on_update(), auth_url(), challenge(), decode_id_token(), exchange(), PendingLogins, apply_session() (+16 more)

### Community 3 - "Bot Tests"
Cohesion: 0.10
Nodes (50): event(), send(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks(), test_allow_all_off_by_default(), test_assign_allowed_all_still_opens_everyone(), test_bare_trigger_asks_what_to_do(), test_budget_exceeded_turns_all_into_default_and_notifies_once() (+42 more)

### Community 4 - "Handover Export"
Cohesion: 0.06
Nodes (22): backup_dir(), export_bundle(), HandoverError, import_bundle(), _prune_backups(), read_manifest(), _skip(), _sources() (+14 more)

### Community 5 - "Assign Events"
Cohesion: 0.21
Nodes (19): _assign(), _cancel(), _event_fields(), _event_id(), _forget(), _is_own(), _list(), _mine() (+11 more)

### Community 6 - "Admin Devices"
Cohesion: 0.09
Nodes (21): AdminDevices, approve(), clean_env(), fake_google(), exchange(), id_token(), local(), make_client() (+13 more)

### Community 7 - "Bot Queue & Chat"
Cohesion: 0.13
Nodes (4): _console(), Bot, Job, IncomingMessage

### Community 8 - "Bot Process Control"
Cohesion: 0.13
Nodes (22): clear_pid(), clear_standby(), _end_task(), _kill(), pid_path(), read_pid(), Result, run_hidden() (+14 more)

### Community 9 - "remote_server.py"
Cohesion: 0.14
Nodes (18): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+10 more)

### Community 10 - "Command Handler"
Cohesion: 0.15
Nodes (5): role_of(), GroupState, GroupStore, change(), _mtime()

### Community 11 - "Failed/Processed Stores"
Cohesion: 0.13
Nodes (11): MemoryDataStore, SeenStore, JsonLinesFile, test_memorydata_api_shows_filter_result_and_respects_history_switch(), test_group_leaders_persist_and_old_records_load(), test_group_teams_and_leader_added_by(), test_history_tail_trim_and_safe_filename(), test_jsonl_append_rewrite_and_utf8() (+3 more)

### Community 12 - "Token Usage & Time"
Cohesion: 0.08
Nodes (13): today_vn(), _clean_map(), _clean_teams(), safe_name(), StatsStore, UsageStore, atomic_write_text(), JsonObjectFile (+5 more)

### Community 13 - "ZaloClient"
Cohesion: 0.11
Nodes (7): ConsoleZalo, _zalo_call(), failed_action(), ZaloClient, run_polling(), _sleep_or_stop(), test_polling_delivers_updates_and_survives_errors()

### Community 14 - "PyloS Atlas"
Cohesion: 0.12
Nodes (16): City tree, `lobby/atlas` — Toà bản đồ, `lobby/dispatch` — Toà điều phối, `lobby` — Khu đại sảnh, `lobby/library` — Toà thư viện, `lobby/office` — Toà văn phòng, `management` — Khu quản lý, `management/managers` — Toà quản lý (+8 more)

### Community 15 - "Bot Package & Desktop Tests"
Cohesion: 0.08
Nodes (13): _free_port(), make_settings(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_ensure_admin_token_writes_once(), test_env_template_keeps_data_inside_userdata(), test_free_port_skips_busy_port(), test_frozen_child_gets_its_own_unpack_dir() (+5 more)

### Community 16 - "Admin App Tests"
Cohesion: 0.07
Nodes (10): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_includes_seen_but_not_allowed_chats(), test_groups_list_shows_leaders(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host() (+2 more)

### Community 17 - "Test Fakes"
Cohesion: 0.16
Nodes (8): agent(), FakeAgent, FakeZalo, make_bot(), factory(), web(), test_bot_adds_missing_at_sign_end_to_end(), test_bot_tells_model_member_names()

### Community 18 - "typing"
Cohesion: 0.22
Nodes (14): _agenda(), _complete_task(), _config(), _create_event(), _create_task(), _list_tasks(), _note(), _owner_only() (+6 more)

### Community 19 - "Admin API Routes"
Cohesion: 0.10
Nodes (29): create_app(), config_error(), devices(), google_poll(), _groups(), guard(), handover_clear_standby(), handover_export() (+21 more)

### Community 21 - "test_handover.py"
Cohesion: 0.22
Nodes (13): make_side(), run_job(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_endpoint_streams_and_refuses_running(), test_import_refused_while_bot_running(), test_import_rejects_non_bundle(), test_import_rejects_unsafe_names() (+5 more)

### Community 22 - "Activity & Personal"
Cohesion: 0.16
Nodes (11): ActivityStore, FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error() (+3 more)

### Community 23 - "command_line.py"
Cohesion: 0.08
Nodes (10): _build_agent(), _run(), request_stop(), watch_stop_flag(), ensure_admin_token(), ensure_home(), RedactFilter, setup_logging() (+2 more)

### Community 24 - "now_ms"
Cohesion: 0.13
Nodes (20): _attach_parent_console(), _health(), main(), _utf8_console(), now_ms(), StateStore, follow_log(), format_status() (+12 more)

### Community 25 - "ConfigError"
Cohesion: 0.12
Nodes (15): _bool(), ConfigError, _csv(), _int(), Settings, clean_value(), FieldSpec, read_values() (+7 more)

### Community 26 - "test_filter.py"
Cohesion: 0.24
Nodes (19): agent(), decide(), _gemini(), make_filter(), factory(), msg(), _Ok, test_ai_error_budget_and_disabled_in_mode_all() (+11 more)

### Community 27 - "vietnam_time.py"
Cohesion: 0.13
Nodes (8): _CachedFile, PromptBuilder, _current_time(), now_vn(), test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role(), _current_time()

### Community 28 - "owner_commands.py"
Cohesion: 0.13
Nodes (11): CommandHandler, help_text(), parse_command(), ParsedCommand, allows(), required_role(), groups(), role() (+3 more)

### Community 29 - "Desktop"
Cohesion: 0.05
Nodes (14): AdminContext, Desktop, watch(), work(), work(), update_flag_file(), make_icon(), write_ico() (+6 more)

### Community 30 - "admin_web_server.py"
Cohesion: 0.06
Nodes (9): ZaloError, _import_zlapi(), create_app(), webhook(), _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_redact_filter_hides_secrets() (+1 more)

### Community 31 - "atlas.py"
Cohesion: 0.20
Nodes (10): assign(), build(), load_map(), main(), places(), problems(), render(), Rule (+2 more)

### Community 32 - "mention_tags.py"
Cohesion: 0.19
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 33 - "tools/__init__.py"
Cohesion: 0.10
Nodes (21): Agent, ToolStep, Turn, discover(), _load_external(), Tool, ToolRegistry, tools() (+13 more)

### Community 34 - "userdata_paths.py"
Cohesion: 0.12
Nodes (14): _prepare_home(), AlreadyRunning, InstanceLock, app_home(), _clean_env(), is_frozen(), migrate_legacy(), _move() (+6 more)

### Community 35 - "PyloS — Kế hoạch dựng "Thành chính""
Cohesion: 0.11
Nodes (17): 10. Giai đoạn 6 — Toà khách và túp lều (chuyển dữ liệu — rủi ro cao nhất), 11. Giai đoạn 7 — Khu dân cư, 12. Giai đoạn 8 — Khu quản lý, dọn dẹp, chốt, 13. Sau khi có cấu trúc (backlog tính năng, chưa lên lịch), 14. Thứ tự và điểm dừng, 15. Việc cần bạn làm, 1. Đích đến (tóm tắt cấu trúc đã chốt), 2. Những thứ đang buộc vào đường dẫn hiện tại (đọc từ repo) (+9 more)

### Community 36 - "test_assign_events.py"
Cohesion: 0.21
Nodes (12): basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team(), test_list_shows_who_has_it_in_their_app() (+4 more)

### Community 37 - "auto_update.py"
Cohesion: 0.26
Nodes (9): _git(), pending_commits(), python_for_pip(), _run(), unavailable_reason(), update(), UpdateError, UpdateResult (+1 more)

### Community 38 - "GeminiAgent"
Cohesion: 0.09
Nodes (10): AgentReply, EchoAgent, GeminiAgent, done(), _is_transient(), _rejects_thinking(), _usage_tokens(), playground() (+2 more)

### Community 39 - "zalo"
Cohesion: 0.19
Nodes (12): `gate/fence` — Hàng rào, `gate/guest_house` — Toà khách, `gate` — Khu cổng, `gate/main_gate` — Cổng chính, `gate/side_gate` — Cổng phụ, 2.2 `gate` — Khu cổng, PHẦN D — Căn hộ (Tầng 3) trong từng toà, logs() (+4 more)

### Community 40 - "to_incoming"
Cohesion: 0.24
Nodes (7): _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming(), test_tagging_personal_account_answers_and_strips_tag(), test_to_incoming_maps_fields_and_marks_own_messages()

### Community 41 - "test_remote_proxy.py"
Cohesion: 0.14
Nodes (5): client(), seen(), test_http_remote_url_is_refused(), test_not_configured(), test_proxy_blocks_sensitive_paths()

### Community 43 - "FailedStore"
Cohesion: 0.17
Nodes (6): FailedStore, change(), change(), _failed(), done_file(), test_failed_list_and_dismiss()

### Community 44 - "PyloS — Trắc nghiệm làm rõ cấu trúc "Thành chính""
Cohesion: 0.20
Nodes (9): Câu hỏi mở (viết tự do), PHẦN 1 — Khái niệm nền (Thành chính / Nội thành / Ngoại thành / 3 tầng), PHẦN 2 — Khu quản lý (Toà Owner, Toà quản lý), PHẦN 3 — Khu cổng (Cổng chính, Hàng rào, Cổng phụ), PHẦN 4 — Khu đại sảnh (Thư viện, Bản đồ, Điều phối), PHẦN 5 — Khu dân cư (Toà nhà dân), PHẦN 6 — Luồng đi, phân quyền, thực thi, PHẦN 7 — Chuyển đổi từ hiện trạng (+1 more)

### Community 45 - "split_message"
Cohesion: 0.18
Nodes (12): _max_prefix(), split_message(), to_plain_text(), utf16_len(), test_dedupe_key_without_message_id_is_stable(), test_parse_command(), test_parse_updates_docs_sample(), test_split_counts_emoji_as_two_units() (+4 more)

### Community 47 - "time"
Cohesion: 0.21
Nodes (8): code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory(), _systemd_state(), _uptime_seconds()

### Community 49 - "test_vps_supervisor.py"
Cohesion: 0.24
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 50 - "PyloS — Trắc nghiệm vòng 3 (chốt chỗ vênh, VPS, bảo mật)"
Cohesion: 0.20
Nodes (9): Câu hỏi mở, Mình đã hiểu gì từ vòng 2 (sai chỗ nào sửa ngay ở đây), PHẦN A — Chỗ vòng 2 vênh nhau, PHẦN B — Đại sảnh làm đầu tiên: bus, PHẦN C — VPS (mình vừa đọc `docs/vps-dieu-khien.md` và `src/bot/system/`), PHẦN D — Bot quản lý duy nhất, PHẦN E — Bảo mật (mình đánh dấu vì các lựa chọn cộng lại tạo lỗ hổng), PHẦN F — Kiểm thử (+1 more)

### Community 52 - "city.md"
Cohesion: 0.20
Nodes (6): Apartments, dispatch (Toà điều phối), Rules, Apartments, managers (Toà quản lý), Rules

### Community 53 - "PyloS City"
Cohesion: 0.18
Nodes (11): 1. Levels, 2.1 `management` — Khu quản lý, 2.3 `lobby` — Khu đại sảnh, 2.4 `residential` — Khu dân cư, 2. Zones and buildings, 3. Data flows, 4. Access rules, 5. Naming (+3 more)

### Community 54 - "test_city_skeleton.py"
Cohesion: 0.24
Nodes (4): folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports()

### Community 55 - "conftest.py"
Cohesion: 0.12
Nodes (8): match_member(), is_chatter(), describe_mode(), _pick_people(), fold(), test_pick_people_prefers_real_tags_and_skips_bot(), test_bot_never_calls_web_on_plain_message(), test_server_client_paths_are_only_scheduling_paths()

### Community 56 - "is_running"
Cohesion: 0.27
Nodes (8): _admin(), _update(), gui_running(), is_running(), lock_for(), restart(), control(), work()

### Community 57 - "message_handler.py"
Cohesion: 0.15
Nodes (3): strip_name_prefix(), ZaloSender, RateLimiter

### Community 58 - "pair"
Cohesion: 0.22
Nodes (3): clean_env(), pair(), running()

### Community 59 - "incoming_message.py"
Cohesion: 0.48
Nodes (3): parse_event(), parse_updates(), _to_ms()

### Community 60 - "PyloS — rules for Claude Code"
Cohesion: 0.33
Nodes (6): Conventions, Finding things: one map, two layers, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 61 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 62 - "_log_path"
Cohesion: 0.50
Nodes (4): path(), _log_path(), stream_logs(), tail()

### Community 64 - "fence (Hàng rào)"
Cohesion: 0.50
Nodes (3): Apartments, fence (Hàng rào), Rules

### Community 65 - "guest_house (Toà khách)"
Cohesion: 0.50
Nodes (3): Apartments, guest_house (Toà khách), Rules

### Community 66 - "Giao diện quản lý web (127.0.0.1:8081)"
Cohesion: 0.20
Nodes (10): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, settings.env, userdata (config, data, system) (+2 more)

### Community 67 - "side_gate (Cổng phụ)"
Cohesion: 0.50
Nodes (3): Apartments, Rules, side_gate (Cổng phụ)

### Community 68 - "HistoryStore"
Cohesion: 0.31
Nodes (4): HistoryStore, clear_history(), history(), test_history_view_and_toggle()

### Community 69 - "atlas (Toà bản đồ)"
Cohesion: 0.50
Nodes (3): Apartments, atlas (Toà bản đồ), Rules

### Community 70 - "library (Toà thư viện)"
Cohesion: 0.50
Nodes (3): Apartments, library (Toà thư viện), Rules

### Community 71 - "office (Toà văn phòng)"
Cohesion: 0.50
Nodes (3): Apartments, office (Toà văn phòng), Rules

### Community 72 - "owner (Toà Owner)"
Cohesion: 0.50
Nodes (3): Apartments, owner (Toà Owner), Rules

### Community 73 - "residents (Toà nhà dân)"
Cohesion: 0.50
Nodes (3): Apartments, residents (Toà nhà dân), Rules

### Community 76 - "PyloS (bot Zalo + trang quản lý + VPS)"
Cohesion: 0.32
Nodes (8): API agent (SCHEDULE_API_KEY, zaloUid), Kế hoạch cập nhật 01/11/2026, PyloS (bot Zalo + trang quản lý + VPS), Phân quyền Owner/Technician/User (W1), Giao diện PyloS vàng-đen (P3), Giao diện web gộp (W4), Dữ liệu riêng từng người UserStore (W2), Web bot lịch quanlythoigian (Vercel)

### Community 77 - "README (Bot trợ lý Zalo Gemini)"
Cohesion: 0.25
Nodes (8): Quyết định đã chốt (Bot Platform, Gemini, local, chat nhóm), PLAN: Server Bot Zalo chạy Agent AI, Zalo Bot Platform API, Zalo OA API (chưa kiểm chứng), README (Bot trợ lý Zalo Gemini), Chạy trên acc Zalo cá nhân (zlapi, QR), Chế độ webhook, Zalo Bot Platform

### Community 78 - "check_secrets.py"
Cohesion: 0.43
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 80 - "google_begin"
Cohesion: 0.32
Nodes (8): auth_options(), _base_url(), google_begin(), google_callback(), _google_ready(), google_start(), _page(), email_allowed()

### Community 82 - "Điều khiển bot trên VPS từ ZaloBot.exe"
Cohesion: 0.33
Nodes (7): Điều khiển VPS và chuyển bot (handover, standby), Điều khiển bot trên VPS từ ZaloBot.exe, Gói chuyển bot (zip, hoàn tác khi lỗi), Cấu hình nginx cho trang quản lý, polkit / sudoers cho user pylos, Chế độ chờ standby.txt, Service systemd pylos-bot

### Community 84 - "Đăng nhập trang quản lý PyloS bằng Google"
Cohesion: 0.33
Nodes (6): Đăng nhập trang quản lý PyloS bằng Google, ADMIN_GOOGLE_CLIENT_ID / SECRET / ADMIN_EMAIL, Lỗi thường gặp (redirect_uri_mismatch...), OAuth client project PyloS Admin, Khoá thiết bị dev_ (REMOTE_ADMIN_TOKEN), Proxy /api/remote/* tới VPS

### Community 85 - "Ba vai trò basic/leader/owner"
Cohesion: 0.33
Nodes (6): Giao lịch cho người khác và liên kết Zalo (/lienket), Bảng lệnh Zalo, Cách dùng bot trên Zalo, Chế độ default và all, Ba vai trò basic/leader/owner, Hạn mức token DAILY_TOKEN_BUDGET

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "Tách PyloS khỏi web (P1)"
Cohesion: 0.40
Nodes (5): Dọn dẹp API cũ (W5), Quyết định đã chốt ngày 01/11/2026, Tách PyloS khỏi web (P1), Đăng nhập Google riêng của PyloS (P2), Thứ tự đưa lên production và rollback

### Community 89 - "Giao diện quản lý bot (admin dashboard)"
Cohesion: 0.40
Nodes (4): Giao diện quản lý bot (admin dashboard), Bảo mật admin: 127.0.0.1, ADMIN_TOKEN, Host/Origin, CSP, ZaloBot.exe (PyInstaller, WebView2, khay hệ thống), Smart App Control chặn exe chưa ký

### Community 90 - "Agent Gemini + function calling"
Cohesion: 0.40
Nodes (5): Agent Gemini + function calling, Kiến trúc: nguồn nhận tin, hàng đợi, agent, ZaloClient, Chat nhóm: chế độ all/default, allowlist, Polling getUpdates vs Webhook + Cloudflare Tunnel, Chạy 24/7 khi chưa có VPS

### Community 93 - "PyloS — Trắc nghiệm vòng 2 (đào sâu)"
Cohesion: 0.18
Nodes (10): Câu hỏi mở, Mình đã hiểu gì từ vòng 1 (sai chỗ nào thì sửa ngay ở đây), PHẦN A — Chỗ vòng 1 chưa khớp nhau, PHẦN B — Đặt tên tiếng Anh, PHẦN C — Toà khách, túp lều, Toà văn phòng, PHẦN E — Hệ trí nhớ của bot, PHẦN F — Thư viện và kệ sách, PHẦN G — Quyền, khẩn cấp, mở rộng (+2 more)

### Community 94 - "Template SYSTEM.md (system prompt)"
Cohesion: 0.40
Nodes (5): Template MEMORY.md, Template SYSTEM.md (system prompt), Giới hạn: không lộ prompt/khoá, chống injection, Quy tắc trả lời: tiếng Việt, văn bản thuần, ngắn gọn, workspace/SYSTEM.md (system prompt)

### Community 97 - "Google Lịch tự động phía máy chủ (W3)"
Cohesion: 0.50
Nodes (3): Google Lịch tự động phía máy chủ (W3), gtoken (refresh token mã hoá, TOKEN_ENC_KEY), W0 chuẩn bị (sao lưu, Publish app, cron-job.org)

### Community 101 - "Chống prompt injection"
Cohesion: 0.67
Nodes (3): Chống prompt injection, Bảo mật và vận hành (rate limit, ngân sách token, che token), Lưu trữ .txt (JSON Lines) và workspace .md

## Knowledge Gaps
- **34 isolated node(s):** `zalo-assistant-bot`, `Bảo mật và vận hành (rate limit, ngân sách token, che token)`, `Lưu trữ .txt (JSON Lines) và workspace .md`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 636 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **74 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_app()` connect `Admin API Routes` to `Handover Jobs`, `Google Login`, `Assign Events`, `Admin Devices`, `Bot Process Control`, `remote_server.py`, `Command Handler`, `Failed/Processed Stores`, `Token Usage & Time`, `ZaloClient`, `Admin App Tests`, `test_handover.py`, `Activity & Personal`, `command_line.py`, `now_ms`, `ConfigError`, `vietnam_time.py`, `Desktop`, `admin_web_server.py`, `tools/__init__.py`, `PyloS — Kế hoạch dựng "Thành chính"`, `auto_update.py`, `GeminiAgent`, `zalo`, `test_remote_proxy.py`, `FailedStore`, `split_message`, `test_vps_supervisor.py`, `is_running`, `pair`, `_log_path`, `AdminSessions`, `HistoryStore`, `google_begin`?**
  _High betweenness centrality (0.098) - this node is a cross-community bridge._
- **Are the 76 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 76 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `Bảo mật và vận hành (rate limit, ngân sách token, che token)`, `Lưu trữ .txt (JSON Lines) và workspace .md` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Admin Web UI (JS)` be split into smaller, more focused modules?**
  _Cohesion score 0.09546165884194054 - nodes in this community are weakly interconnected._
- **Why does `Settings` connect `ConfigError` to `Handover Jobs`, `Google Login`, `Handover Export`, `Bot Queue & Chat`, `Bot Process Control`, `remote_server.py`, `Command Handler`, `Failed/Processed Stores`, `ZaloClient`, `Bot Package & Desktop Tests`, `Admin API Routes`, `PersonalZalo`, `test_handover.py`, `command_line.py`, `now_ms`, `Desktop`, `admin_web_server.py`, `MessageFilter`, `time`, `test_vps_supervisor.py`, `is_running`, `message_handler.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Handover Jobs` be split into smaller, more focused modules?**
  _Cohesion score 0.1253968253968254 - nodes in this community are weakly interconnected._