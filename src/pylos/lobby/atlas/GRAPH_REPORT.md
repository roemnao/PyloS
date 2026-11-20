# Graph Report - pylosSever  (2026-11-20)

## Corpus Check
- 242 files · ~170,399 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: .woff2 9, (none) 5, .css 2)

## Summary
- 3021 nodes · 7081 edges · 202 communities (130 shown, 72 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 771 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `63ac2c49`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- JsonLinesFile
- handover_job.py
- schedule_web.py
- event
- test_admin.py
- userdata_paths.py
- DocError
- IncomingMessage
- Settings
- split_message
- test_desktop.py
- Envelope
- JsonObjectFile
- qr_login.py
- os
- Desktop
- catalog.py
- MediaStore
- admin_page.js
- create_app
- agent_tools/__init__.py
- test_personal.py
- Settings
- steps
- 4. Các bước
- test_media_fetch.py
- common.ps1
- pytest
- mention_tags.py
- test_send_file.py
- personal_account.py
- test_documents_flow.py
- PersonalZalo
- Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết
- Tasks: [FEATURE NAME]
- check_url
- Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc
- 3. Phần A — sửa code Python (`region_map.py`)
- speckit-analyze/SKILL.md
- auto_update.py
- GroupStore
- test_web_reader.py
- config.py
- test_agent.py
- re
- Turn
- AdminContext
- gemini_agent.py
- ZaloClient
- GeminiAgent
- MemoryDataStore
- test_web_fallback.py
- httpx
- push
- Bot
- cloudflare.py
- httpx
- steps
- test_handover.py
- test_vps_supervisor.py
- Natural chat as Lila
- reader.py
- google_login.py
- test_paths.py
- tray_icon.py
- message_handler.py
- conftest.py
- Execution Steps
- test_google_login.py
- test_documents.py
- PromptBuilder
- test_filter.py
- Feature Specification: [FEATURE NAME]
- ConsoleZalo
- Cách dùng bot trên Zalo
- check_secrets.py
- writer.py
- test_assign_events.py
- test_web_fixes.py
- Ba vai trò: basic-user, leader, owner
- cloudflare.py
- fence/SYSTEM.md
- editor.py
- web_reader.py
- speckit-plan/SKILL.md
- data_stores.py
- HistoryStore
- gateway (bot chạy nền)
- ModelCalls
- SYSTEM.md
- zalo-assistant-bot
- test_send_image.py
- test_transient_errors_are_retried_but_others_are_not
- ImageAgent
- 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`
- instructions.py
- DailyCounter
- model_calls/__init__.py
- ToolContext
- documents.py
- speckit-specify/SKILL.md
- speckit-tasks/SKILL.md
- Core Principles
- Core Principles
- send_file
- PyloS — rules for Claude Code
- Implementation Plan: [FEATURE]
- 11. Kế hoạch: giao diện quản lý bot (web dashboard)
- test_regions_file.py
- speckit-checklist/SKILL.md
- apply_session
- incoming_message.py
- speckit-clarify/SKILL.md
- speckit-implement/SKILL.md
- speckit-constitution/SKILL.md
- test_entrypoints.py
- [CHECKLIST TYPE] Checklist: [FEATURE NAME]
- Model keys
- test_model_calls.py
- AdminDevices
- rate_limiter.py
- clock/vietnam_time.py
- test_personal_media.py
- test_city_skeleton.py
- path_guard.py
- AdminSessions
- 5. Phần C — kiểm thử
- asyncio
- admin_web_server.py
- test_classify_retries_once_on_timeout_then_reports_clearly
- Model shift: which kind of work is this, and which model runs it?
- test_zalo_qr_login_saves_session_and_enables_personal
- test_tavily.py
- cdn
- cdn
- backends
- brave
- city
- ActiveModelStore
- owner_commands.py
- .login

## God Nodes (most connected - your core abstractions)
1. `Settings` - 104 edges
2. `create_app()` - 92 edges
3. `event()` - 84 edges
4. `ToolContext` - 60 edges
5. `send()` - 53 edges
6. `Bot` - 52 edges
7. `now_ms()` - 52 edges
8. `Turn` - 38 edges
9. `IncomingMessage` - 37 edges
10. `Desktop` - 37 edges

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

## Communities (202 total, 72 thin omitted)

### Community 0 - "JsonLinesFile"
Cohesion: 0.09
Nodes (17): FailedStore, change(), change(), SeenStore, JsonLinesFile, done_file(), test_group_leaders_persist_and_old_records_load(), test_group_store_seed_and_persist() (+9 more)

### Community 1 - "handover_job.py"
Cohesion: 0.05
Nodes (52): blocked(), call_sync(), _check_status(), _client(), configured(), download_sync(), _explain(), json_request() (+44 more)

### Community 2 - "schedule_web.py"
Cohesion: 0.21
Nodes (15): base_url(), configured(), env_values(), server_config(), _agenda(), _complete_task(), _config(), _create_event() (+7 more)

### Community 3 - "event"
Cohesion: 0.10
Nodes (55): event(), send(), shift_bot(), test_agent_error_sends_apology(), test_allow_all_chats_answers_everywhere_but_deny_still_blocks(), test_allow_all_off_by_default(), test_assign_allowed_all_still_opens_everyone(), test_bare_trigger_asks_what_to_do() (+47 more)

### Community 4 - "test_admin.py"
Cohesion: 0.07
Nodes (10): client(), env_path(), test_bot_control_uses_gateway(), test_group_changes_reach_running_bot_without_clobbering(), test_groups_list_shows_leaders(), test_page_and_every_asset_it_links_are_served(), test_public_url_host_allowed_behind_nginx(), test_rejects_foreign_host() (+2 more)

### Community 5 - "userdata_paths.py"
Cohesion: 0.13
Nodes (19): _prepare_home(), app_home(), _backup_for_huts(), _backup_userdata(), _city_old_running(), _clean_env(), is_frozen(), migrate_all() (+11 more)

### Community 6 - "DocError"
Cohesion: 0.17
Nodes (14): _folder(), clean_name(), DocError, DocInfo, docs_dir(), existing(), folder_size(), list_docs() (+6 more)

### Community 7 - "IncomingMessage"
Cohesion: 0.15
Nodes (3): Decision, MessageFilter, IncomingMessage

### Community 8 - "Settings"
Cohesion: 0.07
Nodes (18): _attach_parent_console(), _mark_good(), _utf8_console(), RedactFilter, setup_logging(), _message_box(), run_gui(), gui_running() (+10 more)

### Community 9 - "split_message"
Cohesion: 0.12
Nodes (19): _blocks(), _max_prefix(), _merge(), split_message(), split_reply(), to_plain_text(), utf16_len(), test_code_block_and_list_stay_together() (+11 more)

### Community 10 - "test_desktop.py"
Cohesion: 0.07
Nodes (16): make_settings(), test_fallback_models_setting(), test_require_personal_needs_qr_session(), test_autostart_registry_roundtrip(), test_desktop_bot_actions_report_to_tray(), test_ensure_admin_token_writes_once(), test_env_template_keeps_data_inside_the_city(), test_frozen_child_gets_its_own_unpack_dir() (+8 more)

### Community 11 - "Envelope"
Cohesion: 0.07
Nodes (18): Bus, InProcessBus, Envelope, EnvelopeLog, test_delivers_to_sync_and_async_handlers(), a(), test_failing_handler_does_not_block_others(), test_log_has_metadata_but_never_the_payload() (+10 more)

### Community 12 - "JsonObjectFile"
Cohesion: 0.09
Nodes (12): ready(), ready(), today_vn(), ActivityStore, StateStore, StatsStore, UsageStore, JsonObjectFile (+4 more)

### Community 13 - "qr_login.py"
Cohesion: 0.11
Nodes (10): Cancelled, cookies_for(), QrLogin, QrLoginError, QrStatus, FakeResponse, FakeZalo, test_cancel_stops_before_next_request() (+2 more)

### Community 14 - "os"
Cohesion: 0.14
Nodes (12): _free_port(), run_hidden(), code_version(), collect(), _git(), last_update_run(), _latest_remote(), _memory() (+4 more)

### Community 15 - "Desktop"
Cohesion: 0.10
Nodes (7): Desktop, watch(), work(), work(), update_flag_file(), AdminContext, run()

### Community 16 - "catalog.py"
Cohesion: 0.17
Nodes (6): ModelCatalog, parse_keys(), _Raw, _split(), test_missing_file_means_every_model_uses_the_default_key(), test_shipped_model_keys_file_parses_and_lists_the_image_models()

### Community 17 - "MediaStore"
Cohesion: 0.20
Nodes (10): MediaFile, MediaStore, _read_rows(), _write_rows(), store_file(), test_chat_id_cannot_escape_huts(), test_prune_removes_old_files_and_empty_dir(), test_save_prunes_expired_siblings() (+2 more)

### Community 18 - "admin_page.js"
Cohesion: 0.06
Nodes (91): 0. Mốc ban đầu (đã kiểm tra ngày 01/11/2026), 1.1 PyloS đang phụ thuộc web ở những chỗ không liên quan tới giao lịch, 1.2 Web có hai tên miền và hai kiểu tài khoản, 1.3 Vì sao đồng bộ Google Lịch "mỗi giờ phải bấm lại, một lúc lại out", 1. Hiện trạng: những chỗ đang dính nhau và đang lỗi, 2. Quyết định đã chốt (hỏi lại người yêu cầu ngày 01/11/2026), 4. Web (quanlythoigian), 5. Thứ tự đưa lên production (+83 more)

### Community 19 - "create_app"
Cohesion: 0.09
Nodes (34): create_app(), auth_options(), _base_url(), config_error(), devices(), google_begin(), google_callback(), google_poll() (+26 more)

### Community 20 - "agent_tools/__init__.py"
Cohesion: 0.10
Nodes (11): discover(), _load_external(), ToolRegistry, tools(), _gemini(), test_gemini_classify_requests_json_and_counts_tokens(), test_external_tools_are_loaded_and_broken_ones_skipped(), test_tools_hidden_when_disabled() (+3 more)

### Community 21 - "test_personal.py"
Cohesion: 0.17
Nodes (9): FakeApi, FakeMessage, make_personal(), test_listener_thread_dispatches_to_event_loop(), test_members_merge_group_list_and_recent_speakers(), test_names_learned_from_incoming_tags(), test_send_error_becomes_zalo_error(), test_send_in_group_attaches_mentions_but_not_in_private() (+1 more)

### Community 22 - "Settings"
Cohesion: 0.11
Nodes (44): _admin(), _health(), main(), _update(), clear_pid(), clear_standby(), _end_task(), follow_log() (+36 more)

### Community 23 - "steps"
Cohesion: 0.06
Nodes (30): args, inputs, integration, spec, default, prompt, type, any (+22 more)

### Community 24 - "4. Các bước"
Cohesion: 0.15
Nodes (13): 4. Các bước, B0. Sao lưu và chốt phiên bản, B10. Kiểm bằng mắt, B11. Khi nâng cấp graphify, B12. Hoàn tất, B1. Tạo thư mục nguồn `SRC`, B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi), B3. Ba cách chia vùng (`zoning.py`) (+5 more)

### Community 25 - "test_media_fetch.py"
Cohesion: 0.12
Nodes (19): fetch_document(), fetch_attachment(), Limits, MediaError, pick_mime(), sniff_mime(), Attachment, body() (+11 more)

### Community 26 - "common.ps1"
Cohesion: 0.16
Nodes (19): Find-SpecifyRoot(), Format-SpecKitCommand(), Get-CurrentBranch(), Get-FeaturePathsEnv(), Get-InvokeSeparator(), Get-NormalizedPriority(), Get-Python3Command(), Get-RepoRoot() (+11 more)

### Community 27 - "pytest"
Cohesion: 0.30
Nodes (10): AccessDenied, ok(), test_case_tricks_do_not_work_on_windows(), test_closed_places_are_refused_for_bots(), test_hut_only_for_the_person_being_served(), test_in_a_group_only_the_group_hut_is_open(), test_open_places_and_own_apartment_are_allowed(), test_owner_and_manager_rules() (+2 more)

### Community 28 - "mention_tags.py"
Cohesion: 0.18
Nodes (11): add_tags(), build_mentions(), _find(), _fold_char(), fold_same_length(), _is_boundary(), _names(), utf16_len() (+3 more)

### Community 29 - "test_send_file.py"
Cohesion: 0.14
Nodes (10): clean_watcher(), doc(), done(), FileApi, Resp, test_file_done_arriving_during_the_wait_is_picked_up(), test_group_chat_uses_group_endpoints_and_grid(), test_no_file_done_means_unsupported_so_the_bot_falls_back_to_text() (+2 more)

### Community 30 - "personal_account.py"
Cohesion: 0.19
Nodes (10): _as_dict(), attachment_of(), _log_failure(), _mention_ids(), _mention_list(), mention_names(), to_incoming(), _to_int() (+2 more)

### Community 31 - "test_documents_flow.py"
Cohesion: 0.19
Nodes (14): docs(), DocZalo, file_msg(), make(), NoFileZalo, push(), RecordingAgent, test_documents_off_means_files_are_ignored_like_before() (+6 more)

### Community 32 - "PersonalZalo"
Cohesion: 0.12
Nodes (5): PersonalZalo, send(), send(), path(), tail()

### Community 33 - "Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết"
Cohesion: 0.22
Nodes (7): 0. Kết quả cần đạt, 1. Hiện trạng đã kiểm (không cần dò lại), 2. Kiến trúc sau khi sửa, 3. Định dạng chung: file phân vùng (`regions.json`), 5. Lỗi có thể xảy ra, 6. Thứ tự làm và điều kiện xong, Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

### Community 34 - "Tasks: [FEATURE NAME]"
Cohesion: 0.07
Nodes (26): Dependencies & Execution Order, Format: `[ID] [P?] [Story] Description`, Implementation for User Story 1, Implementation for User Story 2, Implementation for User Story 3, Implementation Strategy, Incremental Delivery, MVP First (User Story 1 Only) (+18 more)

### Community 35 - "check_url"
Cohesion: 0.18
Nodes (4): fake_dns(), test_internal_or_odd_urls_are_blocked(), test_public_urls_are_allowed(), test_unresolvable_host_is_reported()

### Community 36 - "Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc"
Cohesion: 0.17
Nodes (12): 0. Luật đã chốt, 1.1 Hai file liên quan, 1.2 Vì sao bản đồ hiện tại rối, 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6), 1. Hiện trạng (đọc trước khi sửa), 2.1 Trả khoảng cách về như cũ, 2.2 Chốt file đầu ra, 2.3 Tự vá lại sau mỗi lần graphify dựng lại (+4 more)

### Community 37 - "3. Phần A — sửa code Python (`region_map.py`)"
Cohesion: 0.22
Nodes (9): 3. Phần A — sửa code Python (`region_map.py`), A1. Bảng màu theo toà, A2. Loại nút → hình dạng, A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau, A4. Vị trí toà theo luồng chạy và khoảng cách, A5. Dữ liệu cộng đồng cho viền nét đứt, A6. Cấu trúc `PYLOS_LAYOUT` mới, A7. Dữ liệu cho bot (không đụng hình) (+1 more)

### Community 38 - "speckit-analyze/SKILL.md"
Cohesion: 0.08
Nodes (25): 1. Initialize Analysis Context, 2. Load Artifacts (Progressive Disclosure), 3. Build Semantic Models, 4. Detection Passes (Token-Efficient Analysis), 5. Severity Assignment, 6. Produce Compact Analysis Report, 7. Provide Next Actions, 8. Offer Remediation (+17 more)

### Community 39 - "auto_update.py"
Cohesion: 0.16
Nodes (18): _rollback(), _find_uv(), _git(), hold_state(), install_libs(), last_good(), mark_good(), pending_commits() (+10 more)

### Community 40 - "GroupStore"
Cohesion: 0.17
Nodes (4): GroupState, GroupStore, change(), _mtime()

### Community 41 - "test_web_reader.py"
Cohesion: 0.13
Nodes (24): html_response(), public_dns(), read(), search_call(), serve(), test_disabled_tool_cannot_be_called(), test_http_error_is_reported(), test_huge_page_is_cut_not_loaded_whole() (+16 more)

### Community 42 - "config.py"
Cohesion: 0.13
Nodes (15): _build_agent(), _run(), request_stop(), watch_stop_flag(), _zalo_login(), on_update(), save_qr_png(), _bool() (+7 more)

### Community 43 - "test_agent.py"
Cohesion: 0.16
Nodes (29): Turn, api_error(), chain_agent(), FakeModels, keyed_agent(), make_agent(), PerModel, response() (+21 more)

### Community 44 - "re"
Cohesion: 0.12
Nodes (7): is_chatter(), BotContext, detect_category(), ensure_correct_model(), strip_name_prefix(), test_bot_never_calls_web_on_plain_message(), test_server_client_paths_are_only_scheduling_paths()

### Community 45 - "Turn"
Cohesion: 0.24
Nodes (12): FakeFiles, make(), media_file(), test_expired_file_uri_uploads_again(), test_inline_budget_is_shared_across_turns(), test_large_photo_is_uploaded(), test_small_photo_is_inlined(), test_text_only_turns_unchanged() (+4 more)

### Community 46 - "AdminContext"
Cohesion: 0.11
Nodes (10): health(), 4. Cấu trúc thư mục, 4a. Cấu hình và bí mật để trống, 4b. Lưu trữ `.txt` và workspace `.md`, history(), client(), seen(), test_http_remote_url_is_refused() (+2 more)

### Community 47 - "gemini_agent.py"
Cohesion: 0.12
Nodes (9): playground(), Agent, AgentReply, EchoAgent, _fails_over(), done(), _is_transient(), _rejects_thinking() (+1 more)

### Community 48 - "ZaloClient"
Cohesion: 0.06
Nodes (34): ZaloClient, run_polling(), _sleep_or_stop(), 0. Quyết định đã chốt, 10. Tiến độ, 12.10 Cần bạn xác nhận trước khi làm, 12.11 Tiến độ (2026-10-22), 12.1 Mục tiêu (+26 more)

### Community 49 - "GeminiAgent"
Cohesion: 0.12
Nodes (7): GeminiAgent, MediaRef, _usage_tokens(), grounded(), test_search_uses_only_google_search_tool_and_returns_sources(), test_search_without_grounding_metadata(), test_a_client_given_directly_ignores_the_key_book()

### Community 50 - "MemoryDataStore"
Cohesion: 0.17
Nodes (6): _clean_map(), _clean_teams(), MemoryDataStore, memorydata(), test_store_trims_when_over_keep(), test_memorydata_api_shows_filter_result_and_respects_history_switch()

### Community 51 - "test_web_fallback.py"
Cohesion: 0.12
Nodes (18): SearchingAgent, private(), test_all_sources_failing_lists_reasons(), test_auto_falls_through_to_brave_when_tavily_fails(), test_auto_uses_tavily_after_gemini_quota(), test_gemini_working_never_touches_tavily(), test_no_key_and_tavily_provider_means_no_search_function(), test_tavily_counts_toward_daily_limit() (+10 more)

### Community 52 - "httpx"
Cohesion: 0.12
Nodes (9): create_app(), webhook(), _client(), test_client_builds_url_and_returns_result(), test_client_raises_on_not_ok_and_hides_token(), test_redact_filter_hides_secrets(), test_webhook_checks_secret_and_forwards_payload(), ok_json() (+1 more)

### Community 53 - "push"
Cohesion: 0.22
Nodes (17): media_msg(), push(), test_download_failure_gets_notice(), test_followup_disabled_by_zero_turns(), test_followup_reattaches_recent_media_only(), test_group_caption_with_trigger_passes(), test_group_media_from_someone_else_after_call_is_ignored(), test_group_media_without_call_is_ignored() (+9 more)

### Community 54 - "Bot"
Cohesion: 0.07
Nodes (5): _console(), Bot, run(), Job, test_tagging_personal_account_answers_and_strips_tag()

### Community 55 - "cloudflare.py"
Cohesion: 0.18
Nodes (3): _describe(), ModelCallError, sniff_image_mime()

### Community 56 - "httpx"
Cohesion: 0.18
Nodes (14): ctx_for(), FakeCalls, provider(), test_cloudflare_accepts_a_raw_image_response(), test_cloudflare_errors_are_clear_and_never_leak_the_token(), test_cloudflare_nsfw_false_positive_asks_the_model_to_rephrase(), test_cloudflare_sends_prompt_steps_and_token_and_decodes_base64(), handler() (+6 more)

### Community 57 - "steps"
Cohesion: 0.13
Nodes (14): jobs, test, name, on, pull_request, push, branches, run (+6 more)

### Community 58 - "test_handover.py"
Cohesion: 0.10
Nodes (17): clean_env(), make_side(), pair(), run_job(), running(), test_export_endpoint_returns_zip(), test_export_import_roundtrip_and_exclusions(), test_import_checks_data_layout_version() (+9 more)

### Community 59 - "test_vps_supervisor.py"
Cohesion: 0.24
Nodes (10): make_settings(), test_api_server_returns_info_without_secrets(), test_collect_skips_systemd_on_non_systemd(), test_run_command_exits_in_standby(), test_standby_blocks_start_until_forced(), test_supervisor_value_is_validated(), test_systemctl_falls_back_to_sudo(), test_systemd_failure_is_reported() (+2 more)

### Community 60 - "Natural chat as Lila"
Cohesion: 0.17
Nodes (11): Habits, Humor, Layout of each reply, Natural chat as Lila, Nox, Patterns (from Vietnamese news-site comments, Nov 2026), Real examples from this person (read these first), Rules (+3 more)

### Community 61 - "reader.py"
Cohesion: 0.19
Nodes (9): _read(), _cell(), docx_to_markdown(), _is_item(), _paragraph_md(), read_slice(), read_text(), _runs_md() (+1 more)

### Community 62 - "google_login.py"
Cohesion: 0.22
Nodes (3): decode_id_token(), exchange(), PendingLogins

### Community 63 - "test_paths.py"
Cohesion: 0.13
Nodes (12): _spawn(), spawn_command(), legacy_home(), old_chat_data(), test_chat_data_moves_into_one_hut_per_person_or_group(), test_city_migration_keeps_what_is_already_in_the_new_place(), test_hut_migration_keeps_a_hut_file_that_already_exists(), test_migrates_everything_to_userdata() (+4 more)

### Community 64 - "tray_icon.py"
Cohesion: 0.10
Nodes (8): make_icon(), write_ico(), Tray, command(), is_enabled(), migrate(), set_enabled(), test_icons()

### Community 65 - "message_handler.py"
Cohesion: 0.09
Nodes (9): hut_media_dir(), _create(), ImageConfig, ready(), OutgoingImage, Tool, FieldSpec, ask() (+1 more)

### Community 66 - "conftest.py"
Cohesion: 0.14
Nodes (10): agent(), FakeAgent, FakeZalo, make_bot(), factory(), zalo(), test_bot_adds_missing_at_sign_end_to_end(), test_bot_tells_model_member_names() (+2 more)

### Community 67 - "Execution Steps"
Cohesion: 0.12
Nodes (15): 1. Initialize Convergence Context, 2. Load Artifacts (Progressive Disclosure), 3. Build the Intent Inventory, 4. Assess the Codebase and Classify Findings, 5. Assign Severity, 6. Present the In-Session Findings Summary, 7. Append Convergence Tasks (or report converged), 8. Provide Next Actions (Handoff) (+7 more)

### Community 68 - "test_google_login.py"
Cohesion: 0.11
Nodes (20): approve(), clean_env(), fake_google(), exchange(), id_token(), local(), make_client(), no_web() (+12 more)

### Community 69 - "test_documents.py"
Cohesion: 0.15
Nodes (9): ctx_for(), test_broken_docx_gives_a_readable_error(), test_chats_are_isolated_and_names_cannot_escape(), test_create_never_overwrites_and_supports_markdown(), test_create_read_edit_flow_queues_files_and_counts_limit(), test_limits_and_errors_do_not_queue_or_count(), test_tools_hidden_when_off(), tool() (+1 more)

### Community 70 - "PromptBuilder"
Cohesion: 0.13
Nodes (9): _CachedFile, PromptBuilder, test_prompt_builder_reads_workspace_and_strips_comments(), test_prompt_builder_without_files(), test_prompt_tells_model_the_sender_role(), build(), test_prompt_picks_up_a_new_file_and_falls_back_without_system(), test_prompt_reads_every_document_in_the_workspace() (+1 more)

### Community 71 - "test_filter.py"
Cohesion: 0.27
Nodes (20): agent(), decide(), decide_with(), make_filter(), factory(), msg(), test_ai_error_budget_and_disabled_in_mode_all(), test_ai_stage_returns_profile_in_same_call() (+12 more)

### Community 72 - "Feature Specification: [FEATURE NAME]"
Cohesion: 0.15
Nodes (12): Assumptions, Edge Cases, Feature Specification: [FEATURE NAME], Functional Requirements, Key Entities *(include if feature involves data)*, Measurable Outcomes, Requirements *(mandatory)*, Success Criteria *(mandatory)* (+4 more)

### Community 77 - "Cách dùng bot trên Zalo"
Cohesion: 0.05
Nodes (35): Giao diện quản lý web (127.0.0.1:8081), Tool tự viết (custom_tools), README (Bot trợ lý Zalo Gemini), Gemini agent, Đăng nhập Google trang quản lý (ADMIN_EMAIL), Memorydata và Session, Bộ lọc tin nhóm, Chạy trên acc Zalo cá nhân (zlapi, QR) (+27 more)

### Community 78 - "check_secrets.py"
Cohesion: 0.43
Nodes (4): check_dir(), check_exe(), main(), secrets_from_env()

### Community 80 - "writer.py"
Cohesion: 0.24
Nodes (7): add_markdown(), flush(), _cells(), _inline(), _rule(), _style(), _table()

### Community 82 - "test_assign_events.py"
Cohesion: 0.06
Nodes (15): FakeWeb, basic(), calbot(), ctx(), test_assign_sends_people_and_source_and_reports_unlinked(), test_basic_can_only_assign_to_self(), test_basic_edits_only_own_events(), test_leader_assigns_to_team() (+7 more)

### Community 84 - "test_web_fixes.py"
Cohesion: 0.18
Nodes (14): oembed(), public_dns(), read(), serve(), test_blocked_site_gets_clear_message(), test_brave_search_errors(), test_brave_search_parses_results(), test_user_agent_carries_contact_only_when_set() (+6 more)

### Community 86 - "Ba vai trò: basic-user, leader, owner"
Cohesion: 0.40
Nodes (6): ASSIGN_ALLOWED / SCHEDULE_OWNER_ONLY, Giao lịch cho người trong nhóm (giao_lich, sua_lich, huy_lich), Lịch riêng của chủ web (them_lich_hen, xem_lich...), Ba vai trò: basic-user, leader, owner, Web bot lịch iforgotmywayhome (SCHEDULE_API_KEY), Lệnh trên Zalo (/allow, /mode, /team...)

### Community 88 - "cloudflare.py"
Cohesion: 0.18
Nodes (4): KeyEntry, CloudflareProvider, GeminiProvider, _genai_client()

### Community 93 - "fence/SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 94 - "editor.py"
Cohesion: 0.32
Nodes (8): append_markdown(), backup(), _open(), overwrite_markdown(), _paragraphs(), _replace_in_paragraph(), replace_text(), restore()

### Community 98 - "web_reader.py"
Cohesion: 0.06
Nodes (17): check_url(), _forbidden(), brave_search(), configure(), extract_basic(), extract_main(), fetch_page(), FetchError (+9 more)

### Community 99 - "speckit-plan/SKILL.md"
Cohesion: 0.18
Nodes (10): Completion Report, Done When, Key rules, Mandatory Post-Execution Hooks, Outline, Phase 0: Outline & Research, Phase 1: Design & Contracts, Phases (+2 more)

### Community 101 - "data_stores.py"
Cohesion: 0.19
Nodes (3): hut_file(), safe_name(), atomic_write_text()

### Community 103 - "HistoryStore"
Cohesion: 0.24
Nodes (5): HistoryStore, 11.5 Bảo mật (quan trọng nhất của phần này), clear_history(), test_history_tail_trim_and_safe_filename(), test_history_view_and_toggle()

### Community 105 - "ModelCalls"
Cohesion: 0.20
Nodes (6): ModelCalls, ImageResult, calls(), test_generate_image_reports_models_without_a_key_or_without_image_support(), test_generate_image_tries_fallbacks_only_for_retryable_errors(), test_model_calls_routes_models_to_their_key()

### Community 107 - "SYSTEM.md"
Cohesion: 0.50
Nodes (3): Cách trả lời, Giới hạn, Vai trò

### Community 114 - "test_send_image.py"
Cohesion: 0.17
Nodes (9): image_size(), ThreadType, ImageApi, jpeg(), png(), test_image_size_reads_png_and_jpeg_headers(), test_personal_send_image_unknown_format_and_errors(), test_personal_send_image_uses_real_size_caption_and_chat_type() (+1 more)

### Community 116 - "test_transient_errors_are_retried_but_others_are_not"
Cohesion: 0.25
Nodes (4): KeyBook, test_transient_errors_are_retried_but_others_are_not(), generate_content(), __init__()

### Community 117 - "ImageAgent"
Cohesion: 0.19
Nodes (8): image_bot(), ImageAgent, ImageZalo, pictures(), test_generated_images_are_sent_before_the_text_and_counted(), test_image_send_failure_is_retried_dead_lettered_and_the_user_is_told(), test_replies_without_images_are_unchanged(), test_zalo_without_image_support_gets_a_clear_notice_without_retries()

### Community 118 - "4. Phần B — phần JavaScript/CSS chèn vào `graph.html`"
Cohesion: 0.22
Nodes (9): 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`, B1. Màu và hình nút, B2. Đường nối: phân loại và màu, B3. Vòng toà, B4. Viền cộng đồng, B5. Bấm để làm sáng, B6. Nút chú thích góc trên bên trái, B7. Danh sách cộng đồng bên phải (của graphify) (+1 more)

### Community 122 - "instructions.py"
Cohesion: 0.10
Nodes (15): _fallbacks(), FilterInstructions, parse_profiles(), parse_tasks(), Profile, TaskModel, test_parse_profiles_table_and_defaults(), test_shipped_model_shift_has_the_image_task_and_still_all_profiles() (+7 more)

### Community 128 - "DailyCounter"
Cohesion: 0.16
Nodes (6): ImageLimit, DailyCounter, configure(), P1. Tách PyloS khỏi web: chỉ còn API bot lịch, test_image_limit_per_day_and_per_user_hour(), test_image_limit_zero_means_unlimited_and_failed_runs_cost_nothing()

### Community 129 - "model_calls/__init__.py"
Cohesion: 0.19
Nodes (4): env_lookup(), settings_lookup(), lookup(), test_settings_lookup_prefers_running_settings_then_environment()

### Community 134 - "ToolContext"
Cohesion: 0.14
Nodes (23): fold(), request(), _assign(), _cancel(), _event_fields(), _event_id(), _forget(), _is_own() (+15 more)

### Community 135 - "documents.py"
Cohesion: 0.13
Nodes (11): DocLimit, _check(), configure(), _create(), DocConfig, _edit(), _guard(), _list() (+3 more)

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

### Community 160 - "send_file"
Cohesion: 0.12
Nodes (6): ZaloError, ZaloUnsupported, _decoded(), FileDoneWatcher, send_file(), flaky()

### Community 161 - "PyloS — rules for Claude Code"
Cohesion: 0.29
Nodes (6): Conventions, Finding things: one map, graphify, Hard rules, PyloS — rules for Claude Code, Tests

### Community 162 - "Implementation Plan: [FEATURE]"
Cohesion: 0.22
Nodes (8): Complexity Tracking, Constitution Check, Documentation (this feature), Implementation Plan: [FEATURE], Project Structure, Source Code (repository root), Summary, Technical Context

### Community 163 - "11. Kế hoạch: giao diện quản lý bot (web dashboard)"
Cohesion: 0.18
Nodes (11): 11.10 Cần bạn xác nhận trước khi làm, 11.11 Tiến độ (2026-10-22), 11.1 Mục tiêu, 11.2 Kiến trúc, 11.3 Các trang, 11.4 API (JSON, dưới `/api`), 11.6 Việc phải bổ sung vào bot hiện có, 11.7 Thư mục dự kiến (+3 more)

### Community 164 - "test_regions_file.py"
Cohesion: 0.28
Nodes (4): B6. Phía PyloS, region_of(), test_every_file_under_a_building_lands_in_that_building(), test_tests_and_root_files_have_their_regions()

### Community 165 - "speckit-checklist/SKILL.md"
Cohesion: 0.25
Nodes (7): Anti-Examples: What NOT To Do, Checklist Purpose: "Unit Tests for English", Example Checklist Types & Sample Items, Execution Steps, Post-Execution Checks, Pre-Execution Checks, User Input

### Community 166 - "apply_session"
Cohesion: 0.16
Nodes (12): apply_session(), ZaloSession, read_settings(), remote_login_poll(), remote_logout(), write_secret(), write_settings(), clean_value() (+4 more)

### Community 167 - "incoming_message.py"
Cohesion: 0.48
Nodes (3): parse_event(), parse_updates(), _to_ms()

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
Cohesion: 0.19
Nodes (7): test_console_script_targets_exist(), test_every_module_imports(), test_every_top_level_package_is_bundled_into_the_exe(), test_exe_bundles_every_package_data_pattern_of_pylos(), test_package_data_patterns_match_files(), test_python_dash_m_bot_still_works(), top_packages()

### Community 173 - "[CHECKLIST TYPE] Checklist: [FEATURE NAME]"
Cohesion: 0.40
Nodes (4): [Category 1], [Category 2], [CHECKLIST TYPE] Checklist: [FEATURE NAME], Notes

### Community 174 - "Model keys"
Cohesion: 0.50
Nodes (3): cloudflare-main, gemini-main, Model keys

### Community 175 - "test_model_calls.py"
Cohesion: 0.31
Nodes (8): catalog(), test_bad_entries_are_skipped_with_a_warning_and_never_print_secrets(), test_catalog_reloads_when_the_file_changes(), test_entries_for_the_admin_page_hold_no_secret_values(), test_gemini_provider_keeps_one_client_per_key_and_renews_it_when_the_key_changes(), test_key_with_unset_variable_is_unusable_and_warns_once(), test_model_in_two_keys_uses_the_first(), test_resolve_gives_key_provider_and_extra_variables()

### Community 177 - "rate_limiter.py"
Cohesion: 0.22
Nodes (3): RateLimiter, ZaloSender, test_rate_limiter_window()

### Community 179 - "test_personal_media.py"
Cohesion: 0.43
Nodes (6): make(), test_link_card_becomes_text(), test_media_without_url_is_not_media(), test_photo_keeps_url_and_caption(), test_sticker_file_and_unknown_are_not_media(), test_voice_and_video()

### Community 180 - "test_city_skeleton.py"
Cohesion: 0.18
Nodes (4): folders(), test_every_zone_has_its_agreed_buildings(), test_four_zones_exactly(), test_lobby_dispatch_imports()

### Community 181 - "path_guard.py"
Cohesion: 0.43
Nodes (3): Actor, check_access(), _inside()

### Community 182 - "AdminSessions"
Cohesion: 0.29
Nodes (4): 3. PyloS, P2. Đăng nhập Google riêng của PyloS, P3. Giao diện PyloS: vàng sáng + đen khối, AdminSessions

### Community 183 - "5. Phần C — kiểm thử"
Cohesion: 0.33
Nodes (5): 5. Phần C — kiểm thử, C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm), C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`), C3. Hiệu năng, groups()

### Community 184 - "asyncio"
Cohesion: 0.43
Nodes (5): send(), test_failed_part_stops_and_keeps_the_rest(), test_multiline_reply_goes_as_separate_messages(), test_reply_split_off_sends_one_message(), test_two_sends_to_one_chat_do_not_interleave()

### Community 185 - "admin_web_server.py"
Cohesion: 0.12
Nodes (10): load_session(), make_imei(), auth_url(), challenge(), test_load_session_reads_qr_file_and_manual_cookies(), test_full_qr_flow_returns_session_with_chat_cookies(), lines(), send() (+2 more)

### Community 186 - "test_classify_retries_once_on_timeout_then_reports_clearly"
Cohesion: 0.40
Nodes (5): _Ok, test_classify_drops_thinking_when_model_rejects_it(), generate_content(), test_classify_retries_once_on_timeout_then_reports_clearly(), generate_content()

### Community 187 - "Model shift: which kind of work is this, and which model runs it?"
Cohesion: 0.29
Nodes (6): How to choose (your job), Keep or switch, Model shift: which kind of work is this, and which model runs it?, Profile table (read by the code), Task models (read by the code), Things you do not decide

### Community 188 - "test_zalo_qr_login_saves_session_and_enables_personal"
Cohesion: 0.50
Nodes (3): test_zalo_qr_login_saves_session_and_enables_personal(), report(), run()

### Community 189 - "test_tavily.py"
Cohesion: 0.23
Nodes (6): fresh_config(), serve(), test_tavily_errors(), test_tavily_network_error(), test_tavily_sends_bearer_key_and_parses_results(), test_tavily_without_answer_has_no_answer_key()

### Community 196 - "owner_commands.py"
Cohesion: 0.12
Nodes (15): CommandHandler, describe_mode(), describe_model(), help_text(), parse_command(), ParsedCommand, _pick_people(), allows() (+7 more)

### Community 208 - ".login"
Cohesion: 0.17
Nodes (5): install_hook(), wrapped(), _import_zlapi(), _is_network_error(), test_network_errors_are_detected_through_zlapi_wrapping()

## Knowledge Gaps
- **10 isolated node(s):** `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler`, `Tool tự viết (custom_tools)`, `Đăng nhập Google trang quản lý (ADMIN_EMAIL)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1121 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **72 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `web()` connect `admin_page.js` to `message_handler.py`, `GeminiAgent`, `test_assign_events.py`, `conftest.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 79 inferred relationships involving `Settings` (e.g. with `_admin()` and `_build_agent()`) actually correct?**
  _`Settings` has 79 INFERRED edges - model-reasoned connections that need verification._
- **What connects `zalo-assistant-bot`, `gateway (bot chạy nền)`, `Chạy 24/7 bằng Task Scheduler` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `JsonLinesFile` be split into smaller, more focused modules?**
  _Cohesion score 0.09269162210338681 - nodes in this community are weakly interconnected._
- **Are the 14 inferred relationships involving `create_app()` (e.g. with `ConfigError` and `Settings`) actually correct?**
  _`create_app()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `handover_job.py` be split into smaller, more focused modules?**
  _Cohesion score 0.051893408134642355 - nodes in this community are weakly interconnected._
- **Are the 2 inferred relationships involving `ToolContext` (e.g. with `test_tool_reads_only_own_chat_and_filters_keyword()` and `test_registry_owner_only_unknown_and_errors()`) actually correct?**
  _`ToolContext` has 2 INFERRED edges - model-reasoned connections that need verification._