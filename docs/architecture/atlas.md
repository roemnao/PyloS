# PyloS Atlas

> **Generated** by `scripts/atlas.py` from [`atlas_map.toml`](atlas_map.toml). Do not edit by hand:
> edit the TOML, then run `python scripts/atlas.py`. What the city is and why: [city.md](city.md).
>
> Phase 1: the code has **not** moved yet. "Current path" is where a file is today, "Goes to" is its place in the city.

Status: **agreed** = owner agreed · **proposed** = suggested by Claude, not reviewed by the owner yet · **correction** = differs from what the owner agreed; see the note · **open** = not decided.

## City tree

```
src/pylos/
├── management/  (Khu quản lý)
│   ├── owner/  (Toà Owner)
│   │   ├── admin_web/
│   │   ├── owner_log/
│   │   ├── private_plans/
│   │   ├── history/  [proposed]
│   │   └── secrets/  [open]
│   └── managers/  (Toà quản lý)
│       ├── guidelines/
│       ├── bot_commands/
│       ├── plans/
│       ├── evaluations/
│       ├── reports/
│       └── bot_list/
├── gate/  (Khu cổng)
│   ├── main_gate/  (Cổng chính)
│   │   ├── zalo/
│   │   ├── external_apps/
│   │   ├── external_bots/
│   │   ├── sessions/
│   │   └── logs/
│   ├── fence/  (Hàng rào)
│   │   ├── token_limit/
│   │   ├── speech_limit/
│   │   └── ethics/
│   ├── side_gate/  (Cổng phụ)
│   │   ├── vps/
│   │   ├── cron/  [open]
│   │   ├── mcp/
│   │   ├── owner_commands/
│   │   ├── shell/
│   │   ├── emergency/
│   │   └── desktop/
│   └── guest_house/  (Toà khách)
│       └── <hut_id>/
├── lobby/  (Khu đại sảnh)
│   ├── library/  (Toà thư viện)
│   │   ├── skills/  [proposed]
│   │   └── knowledge/  [proposed]
│   ├── atlas/  (Toà bản đồ)
│   │   ├── maps/  [proposed]
│   │   └── generator/  [proposed]
│   ├── dispatch/  (Toà điều phối)
│   │   ├── bus/
│   │   ├── clock/
│   │   ├── registry/
│   │   ├── queue/
│   │   ├── envelope_log/
│   │   ├── permissions/
│   │   ├── scheduler/
│   │   ├── lifecycle/  [open]
│   │   ├── handover/
│   │   ├── updater/
│   │   └── shared/  [proposed]
│   └── office/  (Toà văn phòng)
│       ├── drawing/
│       ├── documents/
│       ├── code/
│       ├── agent_tools/
│       └── warehouse/
└── residential/  (Khu dân cư)
    └── residents/  (Toà nhà dân)
        └── <bot_name>/
```

## Where every file goes

### `management` — Khu quản lý

Guidance, build plans, project management.

#### `management/owner` — Toà Owner

The owner's own tools and notes. Bots may not enter.

| Apartment | Holds | Status |
|---|---|---|
| `admin_web` | admin web UI | agreed |
| `owner_log` | what the owner did | agreed |
| `private_plans` | plans and notes only the owner sees | agreed |
| `history` | dated snapshots: plans, Q&A rounds, maps (data only, e.g. 5-11-2026/) | 🟡 proposed |
| `secrets` | secrets/tokens, or only a description of where they live (round 3 A7) | 🔴 open |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/management/owner/README.md` | `management/owner` | 🟡 proposed |  |
| `src/pylos/management/owner/__init__.py` | `management/owner` | 🟡 proposed |  |
| `src/bot/ui/__init__.py` | `management/owner/admin_web` | 🟡 proposed | Package marker; dissolves when ui/ is split. |
| `src/bot/ui/admin/__init__.py` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/admin_sessions.py` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/admin_web_server.py` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/google_login.py` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/settings_file.py` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/admin_page.css` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/admin_page.js` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/OFL.txt` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-latin-400-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-latin-500-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-latin-600-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-latin-ext-400-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-latin-ext-500-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-latin-ext-600-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-vietnamese-400-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-vietnamese-500-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/fonts/be-vietnam-pro-vietnamese-600-normal.woff2` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/index.html` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/theme.css` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/bot/ui/admin/static/theme.js` | `management/owner/admin_web` | agreed | static/ is package-data in pyproject.toml: update it when moving. |
| `src/pylos/management/owner/admin_web/__init__.py` | `management/owner/admin_web` | 🟡 proposed |  |
| `src/pylos/management/owner/history/5-11-2026/PyloS-PLAN-thanh-chinh.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/PyloS-trac-nghiem-lam-ro-cau-truc.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/PyloS-trac-nghiem-vong-2.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/PyloS-trac-nghiem-vong-3.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/GRAPH_REPORT.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/graph.html` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/graph.json` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/manifest.json` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/__init__.py` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/owner_log/__init__.py` | `management/owner/owner_log` | 🟡 proposed |  |
| `src/pylos/management/owner/private_plans/__init__.py` | `management/owner/private_plans` | 🟡 proposed |  |
| `src/bot/templates/env.example` | `management/owner/secrets` | 🟡 proposed | Template for settings.env (round 3 A7). |

#### `management/managers` — Toà quản lý

What manager bots read to manage other bots.

| Apartment | Holds | Status |
|---|---|---|
| `guidelines` | principles for manager bots | agreed |
| `bot_commands` | commands that act on bots | agreed |
| `plans` | public plans | agreed |
| `evaluations` | weekly bot scores | agreed |
| `reports` | reports | agreed |
| `bot_list` | list of bots and their on/off switch | agreed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/management/managers/README.md` | `management/managers` | 🟡 proposed |  |
| `src/pylos/management/managers/__init__.py` | `management/managers` | 🟡 proposed |  |
| `src/pylos/management/managers/bot_commands/__init__.py` | `management/managers/bot_commands` | 🟡 proposed |  |
| `src/pylos/management/managers/bot_list/__init__.py` | `management/managers/bot_list` | 🟡 proposed |  |
| `src/pylos/management/managers/evaluations/__init__.py` | `management/managers/evaluations` | 🟡 proposed |  |
| `src/pylos/management/managers/guidelines/__init__.py` | `management/managers/guidelines` | 🟡 proposed |  |
| `docs/KE-HOACH-CAP-NHAT-2026-11-01.md` | `management/managers/plans` | agreed | Plans go to managers/plans; how-to guides (dang-nhap-google, lenh-zalo, vps-dieu-khien) may go to lobby/library/knowledge instead. |
| `docs/PLAN.md` | `management/managers/plans` | agreed | Plans go to managers/plans; how-to guides (dang-nhap-google, lenh-zalo, vps-dieu-khien) may go to lobby/library/knowledge instead. |
| `docs/dang-nhap-google.md` | `management/managers/plans` | agreed | Plans go to managers/plans; how-to guides (dang-nhap-google, lenh-zalo, vps-dieu-khien) may go to lobby/library/knowledge instead. |
| `docs/lenh-zalo.md` | `management/managers/plans` | agreed | Plans go to managers/plans; how-to guides (dang-nhap-google, lenh-zalo, vps-dieu-khien) may go to lobby/library/knowledge instead. |
| `docs/vps-dieu-khien.md` | `management/managers/plans` | agreed | Plans go to managers/plans; how-to guides (dang-nhap-google, lenh-zalo, vps-dieu-khien) may go to lobby/library/knowledge instead. |
| `src/pylos/management/managers/plans/__init__.py` | `management/managers/plans` | 🟡 proposed |  |
| `src/pylos/management/managers/reports/__init__.py` | `management/managers/reports` | 🟡 proposed |  |

### `gate` — Khu cổng

Receives data from Zalo and outer-city bots; sends data out.

#### `gate/main_gate` — Cổng chính

Connections to the outer city, sessions, outside logs.

| Apartment | Holds | Status |
|---|---|---|
| `zalo` | personal account, Bot Platform, QR login, polling, webhook | agreed |
| `external_apps` | third-party apps and APIs | agreed |
| `external_bots` | bots outside PyloS | agreed |
| `sessions` | sessions between bots and the outside | agreed |
| `logs` | logs of outside traffic | agreed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/gate/main_gate/README.md` | `gate/main_gate` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/__init__.py` | `gate/main_gate` | 🟡 proposed |  |
| `src/bot/system/server_client.py` | `gate/main_gate/external_apps` | 🟠 correction | Round 2 put it in side_gate, but it talks to the calendar web app (iforgotmywayhome /api/agent/*), not the VPS. |
| `src/pylos/gate/main_gate/external_apps/__init__.py` | `gate/main_gate/external_apps` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/external_apps/server_client.py` | `gate/main_gate/external_apps` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/external_bots/__init__.py` | `gate/main_gate/external_bots` | 🟡 proposed |  |
| `src/bot/system/log_files.py` | `gate/main_gate/logs` | 🟡 proposed | Log setup (console + rotating file, secrets masked). Log data stays in userdata/system/logs. |
| `src/pylos/gate/main_gate/logs/__init__.py` | `gate/main_gate/logs` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/logs/log_files.py` | `gate/main_gate/logs` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/sessions/__init__.py` | `gate/main_gate/sessions` | 🟡 proposed |  |
| `src/bot/core/mention_tags.py` | `gate/main_gate/zalo` | 🟡 proposed | @mention tags in Zalo groups. |
| `src/bot/core/reply_formatting.py` | `gate/main_gate/zalo` | 🟡 proposed | Formats text for Zalo before sending. |
| `src/bot/zalo/__init__.py` | `gate/main_gate/zalo` | agreed |  |
| `src/bot/zalo/bot_platform_api.py` | `gate/main_gate/zalo` | agreed |  |
| `src/bot/zalo/incoming_message.py` | `gate/main_gate/zalo` | agreed |  |
| `src/bot/zalo/personal_account.py` | `gate/main_gate/zalo` | agreed |  |
| `src/bot/zalo/qr_login.py` | `gate/main_gate/zalo` | agreed |  |
| `src/bot/zalo/receive_polling.py` | `gate/main_gate/zalo` | agreed |  |
| `src/bot/zalo/receive_webhook.py` | `gate/main_gate/zalo` | agreed |  |
| `src/pylos/gate/main_gate/zalo/__init__.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/bot_platform_api.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/incoming_message.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/mention_tags.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/personal_account.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/qr_login.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/receive_polling.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/receive_webhook.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/reply_formatting.py` | `gate/main_gate/zalo` | 🟡 proposed |  |

#### `gate/fence` — Hàng rào

Limits, inbound and outbound: the rules and the code that enforces them.

| Apartment | Holds | Status |
|---|---|---|
| `token_limit` | token limit (whole system, per month) and rate limits | agreed |
| `speech_limit` | what may be said / what is a request to the bot | agreed |
| `ethics` | ethics rules | agreed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/gate/fence/README.md` | `gate/fence` | 🟡 proposed |  |
| `src/pylos/gate/fence/__init__.py` | `gate/fence` | 🟡 proposed |  |
| `src/pylos/gate/fence/ethics/__init__.py` | `gate/fence/ethics` | 🟡 proposed |  |
| `src/bot/core/message_filter.py` | `gate/fence/speech_limit` | agreed | Decides whether a message is asking the bot to reply. |
| `src/bot/core/text_fold.py` | `gate/fence/speech_limit` | agreed | Name matching without case/diacritics; used by the filter. Could be lobby/dispatch/shared if others need it. |
| `src/pylos/gate/fence/speech_limit/__init__.py` | `gate/fence/speech_limit` | 🟡 proposed |  |
| `src/pylos/gate/fence/speech_limit/message_filter.py` | `gate/fence/speech_limit` | 🟡 proposed |  |
| `src/pylos/gate/fence/speech_limit/text_fold.py` | `gate/fence/speech_limit` | 🟡 proposed |  |
| `src/bot/core/rate_limiter.py` | `gate/fence/token_limit` | agreed |  |
| `src/pylos/gate/fence/token_limit/__init__.py` | `gate/fence/token_limit` | 🟡 proposed |  |
| `src/pylos/gate/fence/token_limit/rate_limiter.py` | `gate/fence/token_limit` | 🟡 proposed |  |

#### `gate/side_gate` — Cổng phụ

Technical entry: receives commands from the owner, the VPS and MCP.

| Apartment | Holds | Status |
|---|---|---|
| `vps` | VPS connection and control | agreed |
| `cron` | schedule definitions; may move to dispatch (round 3 A2) | 🔴 open |
| `mcp` | MCP connections | agreed |
| `owner_commands` | commands only the owner may run | agreed |
| `shell` | cmd/shell commands | agreed |
| `emergency` | emergency requests from the main gate | agreed |
| `desktop` | Windows desktop app (window + tray) | agreed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/gate/side_gate/README.md` | `gate/side_gate` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/__init__.py` | `gate/side_gate` | 🟡 proposed |  |
| `src/bot/ui/desktop/__init__.py` | `gate/side_gate/desktop` | agreed |  |
| `src/bot/ui/desktop/desktop_app.py` | `gate/side_gate/desktop` | agreed |  |
| `src/bot/ui/desktop/icon_images.py` | `gate/side_gate/desktop` | agreed |  |
| `src/bot/ui/desktop/tray_icon.py` | `gate/side_gate/desktop` | agreed |  |
| `src/bot/ui/desktop/windows_autostart.py` | `gate/side_gate/desktop` | agreed |  |
| `src/pylos/gate/side_gate/desktop/__init__.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/desktop_app.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/icon_images.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/tray_icon.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/windows_autostart.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/emergency/__init__.py` | `gate/side_gate/emergency` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/mcp/__init__.py` | `gate/side_gate/mcp` | 🟡 proposed |  |
| `src/bot/core/owner_commands.py` | `gate/side_gate/owner_commands` | agreed |  |
| `src/pylos/gate/side_gate/owner_commands/__init__.py` | `gate/side_gate/owner_commands` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/owner_commands/owner_commands.py` | `gate/side_gate/owner_commands` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/shell/__init__.py` | `gate/side_gate/shell` | 🟡 proposed |  |
| `src/bot/system/bot_process.py` | `gate/side_gate/vps` | agreed | Start/stop processes, systemctl, standby. Round 3 A1 may split the decisions out to lobby/dispatch/lifecycle. |
| `src/bot/system/remote_server.py` | `gate/side_gate/vps` | agreed | This machine's app -> admin page on the VPS. |
| `src/bot/system/server_info.py` | `gate/side_gate/vps` | 🟡 proposed | Machine info (RAM, disk, commit, services) for the Server page. |
| `src/pylos/gate/side_gate/vps/__init__.py` | `gate/side_gate/vps` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/vps/bot_process.py` | `gate/side_gate/vps` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/vps/remote_server.py` | `gate/side_gate/vps` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/vps/server_info.py` | `gate/side_gate/vps` | 🟡 proposed |  |

#### `gate/guest_house` — Toà khách

One hut per person or Zalo group: their repos, connections, schedule, profile, files.

| Apartment | Holds | Status |
|---|---|---|
| `<hut_id>` | a hut, named by Zalo uid or group id; created on the first message | agreed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/gate/guest_house/README.md` | `gate/guest_house` | 🟡 proposed |  |
| `src/pylos/gate/guest_house/__init__.py` | `gate/guest_house` | 🟡 proposed |  |

### `lobby` — Khu đại sảnh

Connects bots, the gate and the zones. Every flow between zones passes through here.

#### `lobby/library` — Toà thư viện

Knowledge and skills written or vetted by the owner. All bots read.

| Apartment | Holds | Status |
|---|---|---|
| `skills` | skills (may carry scripts) | 🟡 proposed |
| `knowledge` | documents, guides | 🟡 proposed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/lobby/library/README.md` | `lobby/library` | 🟡 proposed |  |
| `src/pylos/lobby/library/__init__.py` | `lobby/library` | 🟡 proposed |  |
| `src/pylos/lobby/library/knowledge/__init__.py` | `lobby/library/knowledge` | 🟡 proposed |  |
| `src/pylos/lobby/library/skills/__init__.py` | `lobby/library/skills` | 🟡 proposed |  |

#### `lobby/atlas` — Toà bản đồ

Map of the whole inner city: detailed map (graphify graph) + zoning (this file). Manager bot and owner keep it right.

| Apartment | Holds | Status |
|---|---|---|
| `maps` | city description, zoning, the generated atlas, the graphify graph | 🟡 proposed |
| `generator` | atlas script: render, check, look at one region over the graph | 🟡 proposed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/lobby/atlas/README.md` | `lobby/atlas` | 🟡 proposed |  |
| `src/pylos/lobby/atlas/__init__.py` | `lobby/atlas` | 🟡 proposed |  |
| `scripts/atlas.py` | `lobby/atlas/generator` | 🟡 proposed |  |
| `src/pylos/lobby/atlas/generator/__init__.py` | `lobby/atlas/generator` | 🟡 proposed |  |
| `.graphifyignore` | `lobby/atlas/maps` | 🟡 proposed | What graphify leaves out of the detailed map. |
| `docs/architecture/atlas.md` | `lobby/atlas/maps` | 🟡 proposed |  |
| `docs/architecture/atlas_map.toml` | `lobby/atlas/maps` | 🟡 proposed |  |
| `docs/architecture/city.md` | `lobby/atlas/maps` | 🟡 proposed |  |
| `src/pylos/lobby/atlas/maps/__init__.py` | `lobby/atlas/maps` | 🟡 proposed |  |

#### `lobby/dispatch` — Toà điều phối

Core of PyloS: bus, clock, registry, queue, permissions, scheduling. Owner only.

| Apartment | Holds | Status |
|---|---|---|
| `bus` | message bus / router between zones | agreed |
| `clock` | shared clock (Vietnam time) | agreed |
| `registry` | which bots exist, which are running or asleep | agreed |
| `queue` | job queue | agreed |
| `envelope_log` | log of envelopes (never message content) | agreed |
| `permissions` | roles of each bot and each person | agreed |
| `scheduler` | runs scheduled jobs | agreed |
| `lifecycle` | start/stop, single-instance lock; split with side_gate is round 3 A1 | 🔴 open |
| `handover` | moving the bot between this machine and the VPS | agreed |
| `updater` | self-update from git | agreed |
| `shared` | code every zone uses (config, data paths, file formats) | 🟡 proposed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/bot/system/__init__.py` | `lobby/dispatch` | 🟡 proposed | Package marker; dissolves when system/ is split. |
| `src/pylos/lobby/dispatch/README.md` | `lobby/dispatch` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/__init__.py` | `lobby/dispatch` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/bus/__init__.py` | `lobby/dispatch/bus` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/bus/bus.py` | `lobby/dispatch/bus` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/bus/envelope.py` | `lobby/dispatch/bus` | 🟡 proposed |  |
| `src/bot/core/vietnam_time.py` | `lobby/dispatch/clock` | agreed | Signpost: the code moved to src/pylos/lobby/dispatch/clock/vietnam_time.py (step 4.1). Remove in the last phase. |
| `src/pylos/lobby/dispatch/clock/__init__.py` | `lobby/dispatch/clock` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/clock/vietnam_time.py` | `lobby/dispatch/clock` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/envelope_log/__init__.py` | `lobby/dispatch/envelope_log` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/envelope_log/envelope_log.py` | `lobby/dispatch/envelope_log` | 🟡 proposed |  |
| `src/bot/system/handover.py` | `lobby/dispatch/handover` | agreed | Move last in phase 4 (high risk: machine <-> VPS transfer). |
| `src/bot/system/handover_job.py` | `lobby/dispatch/handover` | agreed | Move last in phase 4 (high risk: machine <-> VPS transfer). |
| `src/pylos/lobby/dispatch/handover/__init__.py` | `lobby/dispatch/handover` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/handover/handover.py` | `lobby/dispatch/handover` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/handover/handover_job.py` | `lobby/dispatch/handover` | 🟡 proposed |  |
| `src/bot/storage/process_lock.py` | `lobby/dispatch/lifecycle` | agreed | Signpost: the code moved to src/pylos/lobby/dispatch/lifecycle/process_lock.py (step 4.1). Keep the lock FILE path unchanged when moving the code, or two bots can run on one Zalo account during an update. |
| `src/pylos/lobby/dispatch/lifecycle/__init__.py` | `lobby/dispatch/lifecycle` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/lifecycle/process_lock.py` | `lobby/dispatch/lifecycle` | 🟡 proposed |  |
| `src/bot/core/roles.py` | `lobby/dispatch/permissions` | agreed |  |
| `src/pylos/lobby/dispatch/permissions/__init__.py` | `lobby/dispatch/permissions` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/permissions/roles.py` | `lobby/dispatch/permissions` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/queue/__init__.py` | `lobby/dispatch/queue` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/registry/__init__.py` | `lobby/dispatch/registry` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/scheduler/__init__.py` | `lobby/dispatch/scheduler` | 🟡 proposed |  |
| `src/bot/config.py` | `lobby/dispatch/shared` | 🟡 proposed | Settings read by every zone. Holds secrets in memory, but the file only reads them (round 3 A7). |
| `src/bot/storage/text_files.py` | `lobby/dispatch/shared` | 🟡 proposed | JSON Lines file format used by every store. |
| `src/bot/system/first_run_setup.py` | `lobby/dispatch/shared` | 🟡 proposed |  |
| `src/bot/userdata_paths.py` | `lobby/dispatch/shared` | 🟡 proposed | The path layer that will map userdata/ into huts and apartments (round 3 C3). |
| `src/pylos/__init__.py` | `lobby/dispatch/shared` | 🟡 proposed | The root package of the city (empty; code is moved in step by step). |
| `src/pylos/lobby/dispatch/shared/__init__.py` | `lobby/dispatch/shared` | 🟡 proposed |  |
| `src/bot/system/auto_update.py` | `lobby/dispatch/updater` | agreed | Move last in phase 4 (high risk: self-update). |
| `src/pylos/lobby/dispatch/updater/__init__.py` | `lobby/dispatch/updater` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/updater/auto_update.py` | `lobby/dispatch/updater` | 🟡 proposed |  |

#### `lobby/office` — Toà văn phòng

Plugins and agent tools, plus the warehouse for generated files. Only the owner adds plugins.

| Apartment | Holds | Status |
|---|---|---|
| `drawing` | drawing plugin | agreed |
| `documents` | docx / text presentation plugins | agreed |
| `code` | code plugin | agreed |
| `agent_tools` | tools the agent can call | agreed |
| `warehouse` | generated files, stored by type | agreed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/lobby/office/README.md` | `lobby/office` | 🟡 proposed |  |
| `src/pylos/lobby/office/__init__.py` | `lobby/office` | 🟡 proposed |  |
| `src/bot/agent/tools/__init__.py` | `lobby/office/agent_tools` | agreed |  |
| `src/bot/templates/tool_example.py.tmpl` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/__init__.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/_example.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/assign_events.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/read_chat_memory.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/schedule_web.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `tools/_example.py` | `lobby/office/agent_tools` | 🟡 proposed | Example for user-written tools (real ones live in userdata/data/custom_tools). |
| `src/pylos/lobby/office/code/__init__.py` | `lobby/office/code` | 🟡 proposed |  |
| `src/pylos/lobby/office/documents/__init__.py` | `lobby/office/documents` | 🟡 proposed |  |
| `src/pylos/lobby/office/drawing/__init__.py` | `lobby/office/drawing` | 🟡 proposed |  |
| `src/pylos/lobby/office/warehouse/__init__.py` | `lobby/office/warehouse` | 🟡 proposed |  |

### `residential` — Khu dân cư

Where bots live.

#### `residential/residents` — Toà nhà dân

One apartment per bot: workspace, persona, bookshelf, memory. Only that bot and the owner enter.

| Apartment | Holds | Status |
|---|---|---|
| `<bot_name>` | workspace/ persona/ bookshelf/ memory/{muscle,short_term,long_term,archive}/ | agreed |

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/pylos/residential/residents/README.md` | `residential/residents` | 🟡 proposed |  |
| `src/pylos/residential/residents/__init__.py` | `residential/residents` | 🟡 proposed |  |
| `src/bot/agent/__init__.py` | `residential/residents/<bot_name>` | agreed |  |
| `src/bot/agent/gemini_agent.py` | `residential/residents/<bot_name>` | agreed |  |
| `src/bot/agent/system_prompt.py` | `residential/residents/<bot_name>` | agreed |  |
| `src/bot/templates/MEMORY.md` | `residential/residents/<bot_name>` | agreed |  |
| `src/bot/templates/SYSTEM.md` | `residential/residents/<bot_name>` | agreed | Persona. Rules part moves outside the apartment if round 3 E3 is accepted. |
| `workspace/SYSTEM.md` | `residential/residents/<bot_name>` | agreed |  |

## Outside the citadel

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `.gitattributes` | `outside/repo_root` | agreed |  |
| `.github/workflows/tests.yml` | `outside/repo_root` | agreed | CI: runs the tests on every PR (main deploys to the VPS). |
| `.gitignore` | `outside/repo_root` | agreed |  |
| `CLAUDE.md` | `outside/repo_root` | agreed | Rules Claude Code reads on every session. |
| `README.md` | `outside/repo_root` | agreed |  |
| `ZaloBot.cmd` | `outside/repo_root` | agreed |  |
| `pyproject.toml` | `outside/repo_root` | agreed |  |
| `tests/conftest.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_admin.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_agent.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_assign_events.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_atlas.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_bot.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_bus.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_city_skeleton.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_config_client_webhook.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_desktop.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_entrypoints.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_filter.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_google_login.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_handover.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_memorydata.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_no_web_coupling.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_paths.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_personal.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_polling.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_qrlogin.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_remote_proxy.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_roles.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_schedule_tool.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_storage.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_text_and_models.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_updater.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `tests/test_vps_supervisor.py` | `outside/tests` | agreed | Mirror the city later (round 3 F1). |
| `scripts/build-exe.ps1` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |
| `scripts/install-task.ps1` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |
| `scripts/packaging/ZaloBot.spec` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |
| `scripts/packaging/check_secrets.py` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |
| `scripts/packaging/version_info.txt` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |
| `scripts/packaging/zalobot_entry.py` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |
| `scripts/run-forever.ps1` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |
| `scripts/uninstall-task.ps1` | `outside/tooling` | agreed | Build, packaging, Windows task scripts. |

## Undecided (`open`)

These files have no place yet; the owner decides.

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `src/bot/__init__.py` | `open` | 🔴 open | Stays as the thin `bot` entry package if round 3 C1 keeps `python -m bot run`. |
| `src/bot/__main__.py` | `open` | 🔴 open | `python -m bot` entry used by the VPS systemd unit and ZaloBot.cmd; must keep working (round 3 C1). |
| `src/bot/command_line.py` | `open` | 🔴 open | CLI (run, gui, admin...). Candidates: stay in the `bot` entry package, or side_gate/owner_commands. |
| `src/bot/core/__init__.py` | `open` | 🔴 open | Package marker; dissolves when core/ is split. |
| `src/bot/core/message_handler.py` | `open` | 🔴 open | Core reply pipeline: decide, queue per chat, send. Candidates: queue -> lobby/dispatch/queue, decision/reply -> residential/residents/<bot_name>. |
| `src/bot/storage/__init__.py` | `open` | 🔴 open | Re-exports data_stores; follows it. |
| `src/bot/storage/data_stores.py` | `open` | 🔴 open | All data stores in one file. Per-person stores -> gate/guest_house/<hut_id>; bot stores -> residential; system stores -> lobby/dispatch. Split in phase 6. |

## Waiting for owner review

132 file(s) placed as `proposed` or `correction`.

| Current path | Goes to | Status | Note |
|---|---|---|---|
| `.graphifyignore` | `lobby/atlas/maps` | 🟡 proposed | What graphify leaves out of the detailed map. |
| `docs/architecture/atlas.md` | `lobby/atlas/maps` | 🟡 proposed |  |
| `docs/architecture/atlas_map.toml` | `lobby/atlas/maps` | 🟡 proposed |  |
| `docs/architecture/city.md` | `lobby/atlas/maps` | 🟡 proposed |  |
| `scripts/atlas.py` | `lobby/atlas/generator` | 🟡 proposed |  |
| `src/bot/config.py` | `lobby/dispatch/shared` | 🟡 proposed | Settings read by every zone. Holds secrets in memory, but the file only reads them (round 3 A7). |
| `src/bot/core/mention_tags.py` | `gate/main_gate/zalo` | 🟡 proposed | @mention tags in Zalo groups. |
| `src/bot/core/reply_formatting.py` | `gate/main_gate/zalo` | 🟡 proposed | Formats text for Zalo before sending. |
| `src/bot/storage/text_files.py` | `lobby/dispatch/shared` | 🟡 proposed | JSON Lines file format used by every store. |
| `src/bot/system/__init__.py` | `lobby/dispatch` | 🟡 proposed | Package marker; dissolves when system/ is split. |
| `src/bot/system/first_run_setup.py` | `lobby/dispatch/shared` | 🟡 proposed |  |
| `src/bot/system/log_files.py` | `gate/main_gate/logs` | 🟡 proposed | Log setup (console + rotating file, secrets masked). Log data stays in userdata/system/logs. |
| `src/bot/system/server_client.py` | `gate/main_gate/external_apps` | 🟠 correction | Round 2 put it in side_gate, but it talks to the calendar web app (iforgotmywayhome /api/agent/*), not the VPS. |
| `src/bot/system/server_info.py` | `gate/side_gate/vps` | 🟡 proposed | Machine info (RAM, disk, commit, services) for the Server page. |
| `src/bot/templates/env.example` | `management/owner/secrets` | 🟡 proposed | Template for settings.env (round 3 A7). |
| `src/bot/templates/tool_example.py.tmpl` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/bot/ui/__init__.py` | `management/owner/admin_web` | 🟡 proposed | Package marker; dissolves when ui/ is split. |
| `src/bot/userdata_paths.py` | `lobby/dispatch/shared` | 🟡 proposed | The path layer that will map userdata/ into huts and apartments (round 3 C3). |
| `src/pylos/__init__.py` | `lobby/dispatch/shared` | 🟡 proposed | The root package of the city (empty; code is moved in step by step). |
| `src/pylos/gate/__init__.py` | `gate` | 🟡 proposed |  |
| `src/pylos/gate/fence/README.md` | `gate/fence` | 🟡 proposed |  |
| `src/pylos/gate/fence/__init__.py` | `gate/fence` | 🟡 proposed |  |
| `src/pylos/gate/fence/ethics/__init__.py` | `gate/fence/ethics` | 🟡 proposed |  |
| `src/pylos/gate/fence/speech_limit/__init__.py` | `gate/fence/speech_limit` | 🟡 proposed |  |
| `src/pylos/gate/fence/speech_limit/message_filter.py` | `gate/fence/speech_limit` | 🟡 proposed |  |
| `src/pylos/gate/fence/speech_limit/text_fold.py` | `gate/fence/speech_limit` | 🟡 proposed |  |
| `src/pylos/gate/fence/token_limit/__init__.py` | `gate/fence/token_limit` | 🟡 proposed |  |
| `src/pylos/gate/fence/token_limit/rate_limiter.py` | `gate/fence/token_limit` | 🟡 proposed |  |
| `src/pylos/gate/guest_house/README.md` | `gate/guest_house` | 🟡 proposed |  |
| `src/pylos/gate/guest_house/__init__.py` | `gate/guest_house` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/README.md` | `gate/main_gate` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/__init__.py` | `gate/main_gate` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/external_apps/__init__.py` | `gate/main_gate/external_apps` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/external_apps/server_client.py` | `gate/main_gate/external_apps` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/external_bots/__init__.py` | `gate/main_gate/external_bots` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/logs/__init__.py` | `gate/main_gate/logs` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/logs/log_files.py` | `gate/main_gate/logs` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/sessions/__init__.py` | `gate/main_gate/sessions` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/__init__.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/bot_platform_api.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/incoming_message.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/mention_tags.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/personal_account.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/qr_login.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/receive_polling.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/receive_webhook.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/main_gate/zalo/reply_formatting.py` | `gate/main_gate/zalo` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/README.md` | `gate/side_gate` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/__init__.py` | `gate/side_gate` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/__init__.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/desktop_app.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/icon_images.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/tray_icon.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/desktop/windows_autostart.py` | `gate/side_gate/desktop` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/emergency/__init__.py` | `gate/side_gate/emergency` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/mcp/__init__.py` | `gate/side_gate/mcp` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/owner_commands/__init__.py` | `gate/side_gate/owner_commands` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/owner_commands/owner_commands.py` | `gate/side_gate/owner_commands` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/shell/__init__.py` | `gate/side_gate/shell` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/vps/__init__.py` | `gate/side_gate/vps` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/vps/bot_process.py` | `gate/side_gate/vps` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/vps/remote_server.py` | `gate/side_gate/vps` | 🟡 proposed |  |
| `src/pylos/gate/side_gate/vps/server_info.py` | `gate/side_gate/vps` | 🟡 proposed |  |
| `src/pylos/lobby/__init__.py` | `lobby` | 🟡 proposed |  |
| `src/pylos/lobby/atlas/README.md` | `lobby/atlas` | 🟡 proposed |  |
| `src/pylos/lobby/atlas/__init__.py` | `lobby/atlas` | 🟡 proposed |  |
| `src/pylos/lobby/atlas/generator/__init__.py` | `lobby/atlas/generator` | 🟡 proposed |  |
| `src/pylos/lobby/atlas/maps/__init__.py` | `lobby/atlas/maps` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/README.md` | `lobby/dispatch` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/__init__.py` | `lobby/dispatch` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/bus/__init__.py` | `lobby/dispatch/bus` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/bus/bus.py` | `lobby/dispatch/bus` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/bus/envelope.py` | `lobby/dispatch/bus` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/clock/__init__.py` | `lobby/dispatch/clock` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/clock/vietnam_time.py` | `lobby/dispatch/clock` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/envelope_log/__init__.py` | `lobby/dispatch/envelope_log` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/envelope_log/envelope_log.py` | `lobby/dispatch/envelope_log` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/handover/__init__.py` | `lobby/dispatch/handover` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/handover/handover.py` | `lobby/dispatch/handover` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/handover/handover_job.py` | `lobby/dispatch/handover` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/lifecycle/__init__.py` | `lobby/dispatch/lifecycle` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/lifecycle/process_lock.py` | `lobby/dispatch/lifecycle` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/permissions/__init__.py` | `lobby/dispatch/permissions` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/permissions/roles.py` | `lobby/dispatch/permissions` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/queue/__init__.py` | `lobby/dispatch/queue` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/registry/__init__.py` | `lobby/dispatch/registry` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/scheduler/__init__.py` | `lobby/dispatch/scheduler` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/shared/__init__.py` | `lobby/dispatch/shared` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/updater/__init__.py` | `lobby/dispatch/updater` | 🟡 proposed |  |
| `src/pylos/lobby/dispatch/updater/auto_update.py` | `lobby/dispatch/updater` | 🟡 proposed |  |
| `src/pylos/lobby/library/README.md` | `lobby/library` | 🟡 proposed |  |
| `src/pylos/lobby/library/__init__.py` | `lobby/library` | 🟡 proposed |  |
| `src/pylos/lobby/library/knowledge/__init__.py` | `lobby/library/knowledge` | 🟡 proposed |  |
| `src/pylos/lobby/library/skills/__init__.py` | `lobby/library/skills` | 🟡 proposed |  |
| `src/pylos/lobby/office/README.md` | `lobby/office` | 🟡 proposed |  |
| `src/pylos/lobby/office/__init__.py` | `lobby/office` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/__init__.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/_example.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/assign_events.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/read_chat_memory.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/agent_tools/schedule_web.py` | `lobby/office/agent_tools` | 🟡 proposed |  |
| `src/pylos/lobby/office/code/__init__.py` | `lobby/office/code` | 🟡 proposed |  |
| `src/pylos/lobby/office/documents/__init__.py` | `lobby/office/documents` | 🟡 proposed |  |
| `src/pylos/lobby/office/drawing/__init__.py` | `lobby/office/drawing` | 🟡 proposed |  |
| `src/pylos/lobby/office/warehouse/__init__.py` | `lobby/office/warehouse` | 🟡 proposed |  |
| `src/pylos/management/__init__.py` | `management` | 🟡 proposed |  |
| `src/pylos/management/managers/README.md` | `management/managers` | 🟡 proposed |  |
| `src/pylos/management/managers/__init__.py` | `management/managers` | 🟡 proposed |  |
| `src/pylos/management/managers/bot_commands/__init__.py` | `management/managers/bot_commands` | 🟡 proposed |  |
| `src/pylos/management/managers/bot_list/__init__.py` | `management/managers/bot_list` | 🟡 proposed |  |
| `src/pylos/management/managers/evaluations/__init__.py` | `management/managers/evaluations` | 🟡 proposed |  |
| `src/pylos/management/managers/guidelines/__init__.py` | `management/managers/guidelines` | 🟡 proposed |  |
| `src/pylos/management/managers/plans/__init__.py` | `management/managers/plans` | 🟡 proposed |  |
| `src/pylos/management/managers/reports/__init__.py` | `management/managers/reports` | 🟡 proposed |  |
| `src/pylos/management/owner/README.md` | `management/owner` | 🟡 proposed |  |
| `src/pylos/management/owner/__init__.py` | `management/owner` | 🟡 proposed |  |
| `src/pylos/management/owner/admin_web/__init__.py` | `management/owner/admin_web` | 🟡 proposed |  |
| `src/pylos/management/owner/history/5-11-2026/PyloS-PLAN-thanh-chinh.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/PyloS-trac-nghiem-lam-ro-cau-truc.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/PyloS-trac-nghiem-vong-2.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/PyloS-trac-nghiem-vong-3.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/GRAPH_REPORT.md` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/graph.html` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/graph.json` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/5-11-2026/late-map/manifest.json` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/history/__init__.py` | `management/owner/history` | 🟡 proposed | Data only. Subfolders are dates (d-m-yyyy); late-map is a copy of graphify-out (without the cache). |
| `src/pylos/management/owner/owner_log/__init__.py` | `management/owner/owner_log` | 🟡 proposed |  |
| `src/pylos/management/owner/private_plans/__init__.py` | `management/owner/private_plans` | 🟡 proposed |  |
| `src/pylos/residential/__init__.py` | `residential` | 🟡 proposed |  |
| `src/pylos/residential/residents/README.md` | `residential/residents` | 🟡 proposed |  |
| `src/pylos/residential/residents/__init__.py` | `residential/residents` | 🟡 proposed |  |
| `tools/_example.py` | `lobby/office/agent_tools` | 🟡 proposed | Example for user-written tools (real ones live in userdata/data/custom_tools). |
