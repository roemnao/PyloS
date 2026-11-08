# PyloS City

The source of truth for how PyloS is organised. Every folder, file and data flow has a place in "the city".
Which building a file belongs to: [regions.json](regions.json). How to change it: [Changing the city](#changing-the-city).

> **Status: migration under way (phases 3–5 and 8.1 done on branch `claude/g3-city-skeleton`).** Code moved into
> `src/pylos/`: dispatch (clock, lock, roles, handover, updater, bus), office agent tools, the whole gate zone except
> `message_handler`/storage, and the admin web UI. Each moved module leaves a signpost in `src/bot/` (an alias to the new
> module) until the last phase. Still in `src/bot/`: entry point, config, `userdata_paths`, `storage`, `message_handler`, `agent`. The migration plan is in `src/pylos/management/owner/history/5-11-2026/PyloS-PLAN-thanh-chinh.md` (Vietnamese, owner's working copy).

---

## 1. Levels

The whole of PyloS is **the citadel** (`PyloS`). Everything inside it is **the inner city**. Everything outside it is **the outer city**.

The inner city has exactly three folder levels. All three are real folders; inside an apartment, anything goes.

```
<zone>/<building>/<apartment>/...
```

| Level | Vietnamese | English | Meaning |
|---|---|---|---|
| 1 | Khu vực | **zone** | A large area with one job (manage, connect to the outside, route, live) |
| 2 | Toà | **building** | One responsibility inside a zone |
| 3 | Căn hộ | **apartment** | One unit inside a building. Its meaning depends on the zone (see below) |

What an apartment is, per zone:

| Zone | One apartment is |
|---|---|
| `management` | one topic |
| `gate` | one module (one connection, one kind of limit…); in `guest_house`, one person or one Zalo group (a *hut*) |
| `lobby` | one function |
| `residential` | one bot |

**Outer city** = anything not in the citadel: Zalo (users and accounts), bots running outside PyloS, users' folders,
machines and GitHub repos, third-party apps and APIs.

---

## 2. Zones and buildings

### 2.1 `management` — Khu quản lý
Guidance, build plans, project management.

| Building | Vietnamese | Holds | Access |
|---|---|---|---|
| `owner` | Toà Owner | `admin_web` (admin web UI), `owner_log` (what the owner did), `private_plans` | **Bots may not enter.** Owner only |
| `managers` | Toà quản lý | `guidelines`, `bot_commands`, `plans` (public plans), `evaluations` (weekly bot scores), `reports`, `bot_list` (bots + on/off) | Manager bots read. Ordinary bots do not need it |

Plans are split: public plans in `managers/plans`, private plans in `owner/private_plans`.

### 2.2 `gate` — Khu cổng
Receives data from Zalo and outer-city bots; sends data out.

| Building | Vietnamese | Holds |
|---|---|---|
| `main_gate` | Cổng chính | `zalo` (personal account, Bot Platform, QR login, polling, webhook), `external_apps`, `external_bots`, `sessions`, `logs` |
| `fence` | Hàng rào | `token_limit`, `speech_limit`, `ethics` — the rules **and** the code that enforces them |
| `side_gate` | Cổng phụ | `vps`, `mcp`, `owner_commands`, `shell`, `emergency`, `desktop` — technical entry: receives commands from the owner, the VPS and MCP |
| `guest_house` | Toà khách | one **hut** per person (Zalo uid) or per Zalo group |

**Fence** filters both directions: inbound (length, spam) and outbound (speech, ethics). A violation is **blocked** and
the sender is told. The token limit counts the whole system per month.

**Side gate** only *receives* commands; the lobby's `dispatch` *executes* them (scheduling, start/stop).

**Hut** (túp lều) holds everything that belongs to one person or group: the repos they asked PyloS to work on and the
GitHub connection details, their schedule/tasks, the profile/preferences the bot noted, files they sent or the bot made
for them. Chat sessions stay in `main_gate/sessions`. A hut is created automatically on the first message.
Groups get their own hut, separate from their members' huts.

Work on a user's repo: create a separate branch, push to it, open a PR to `main` for the user to merge.

### 2.3 `lobby` — Khu đại sảnh
Connects bots to each other, bots to the gate, and zones to each other. **Every flow from one zone to another passes
through the lobby.**

| Building | Vietnamese | Holds | Access |
|---|---|---|---|
| `library` | Toà thư viện | knowledge and skills written or vetted by the owner | All bots read; managers and owner write |
| `atlas` | Toà bản đồ | the city description, the zoning file and the map drawer (see below) | All bots read; managers and owner write |
| `dispatch` | Toà điều phối | message bus, shared clock (Vietnam time), bot registry, job queue, envelope log, permissions (roles), scheduler, start/stop | Owner only |
| `office` | Toà văn phòng | plugins (drawing, documents, code), agent tools, and the `warehouse` where generated files are stored by type | Bots use; only the owner adds or changes plugins |

**The map has two layers.**
- *Detailed map* — the graphify knowledge graph (`graphify-out/graph.json`): every symbol of the code and the links
  between them, rebuilt automatically after each commit. Nobody draws small maps by hand.
- *Zoning* — [`regions.json`](regions.json): the only zoning file, path prefix -> building.
- This folder IS the map: all graphify output lands here (`graph.html` to look at, `GRAPH_REPORT.md` for bots, `graph.json`),
  drawn by `/graphify` on the admin machine (the region add-on lives in the graphify skill). A bot reads `GRAPH_REPORT.md`
  or asks `graphify query` for the region it needs instead of reading everything.
- Keeping the map right is the job of the **manager bot and the owner**.

The lobby reads only the **envelope** of a message (who sent it, to whom, what kind), never its content.

**Library → bookshelf.** Bots pick documents from the library themselves and copy them to the `bookshelf` in their
own apartment. The copy records the library version; the bot is warned when the library has a newer one.
Anything from an outside source is read by the owner before it enters the library.
A skill may carry a script; a plugin is a standalone tool.

### 2.4 `residential` — Khu dân cư
Where bots live: work when called, run scheduled activities or wait when not.

| Building | Vietnamese | Holds |
|---|---|---|
| `residents` | Toà nhà dân | one apartment per bot |

Inside a bot's apartment:

| Folder | Holds |
|---|---|
| `workspace/` | the bot's own documents (`SOUL.md`: who it is and how it answers, `MEMORY.md`: long-term notes, anything else you drop in). The bot reads **every** `.md`/`.txt` file here (hidden folders such as `.backup/` excluded); `MEMORY.md` is read as data, the rest as instructions. Tracked by git |
| `persona/` | voice and habits (the bot may tune these); the bot's *rules* are not editable by the bot |
| `bookshelf/` | versioned copies of library documents |
| `memory/muscle/` | skills distilled from the bookshelf or written by the bot; retuned weekly from the manager's score, rolled back if the score drops |
| `memory/short_term/` | fresh material from recent activity and reading, kept until the next *dream* |
| `memory/long_term/` | knowledge used or met many times, restructured by the *dream* |
| `memory/archive/` | long-term items no longer in use (never deleted) |

**Dream** (mơ): restructures short-term memory into long-term. Runs nightly, when the bot is idle, or when short-term
memory reaches a threshold. A script filters first; the LLM handles the rest. An item moves to long-term when it has
been met N times or the bot rates it important.

**Nobody else enters a bot's apartment** except the owner.

---

## 3. Data flows

A Zalo message and its reply:

```
Zalo → main_gate → fence → lobby (dispatch) → residents/<bot> → lobby → fence → main_gate → Zalo
```

- Bot ↔ bot inside the same residential zone: decided when there are two or more bots.
- **Emergency** (kill switch, isolating an abusive bot, broken Zalo connection, special owner command):
  `main_gate → side_gate` directly, skipping the lobby and the fence, with a parallel log entry in the lobby.
- Sharing one user's data between two bots: through the lobby (decided when there are two or more bots).

---

## 4. Access rules

Default: **open** inside the inner city. Closed:

| Place | Who may enter |
|---|---|
| `management/owner` | owner |
| `residential/residents/<bot>` | that bot, owner |
| `gate/guest_house/<hut>` | owner, manager bots, the bot currently serving that person (only while serving) |
| `lobby/dispatch` | owner |

Enforcement: an instruction in the bot's prompt **plus** a path filter in the bot's file tools, which refuses reads and
writes into closed places.

These rules apply to **bots** — file access an LLM asks for through a tool. They do not apply to PyloS's own system
code (the gate must read Zalo credentials, dispatch must start bots).

**Private data.** Anything tied to one person lives **only** in that person's hut. A bot's memory holds no information
tied to a specific person.

**Manager bot.** One fixed manager bot (plus ordinary bots the owner temporarily promotes). It may read status and
reports, assign work, and start/stop/restart other bots. It may **not** edit another bot's memory or workspace, and may
**not** create or delete bots. It scores bots from user reactions and behaviour, and tells each bot so it can retune.

Commands: *manager commands* act on bots (assign, start/stop); *owner commands* act on the system (VPS, cron, restart).

---

## 5. Naming

- English for every folder, file and document in the city.
- `snake_case` for every folder (Python can import them).
- City metaphor names (`lobby`, `gate`, `hut`…), not plain function names.
- Package names are lower case (`pylos`, never `PyloS`): Windows ignores case, the VPS (Linux) does not.

| Vietnamese | English |
|---|---|
| Thành chính / Nội thành / Ngoại thành | citadel / inner city / outer city |
| Khu vực / Toà / Căn hộ | zone / building / apartment |
| Khu quản lý · Toà Owner · Toà quản lý | `management` · `owner` · `managers` |
| Khu cổng · Cổng chính · Hàng rào · Cổng phụ · Toà khách | `gate` · `main_gate` · `fence` · `side_gate` · `guest_house` |
| Khu đại sảnh · Toà thư viện · Toà bản đồ · Toà điều phối · Toà văn phòng | `lobby` · `library` · `atlas` · `dispatch` · `office` |
| Khu dân cư · Toà nhà dân | `residential` · `residents` |
| Túp lều · Kệ sách · Nhà kho | hut · `bookshelf` · `warehouse` |
| Trí nhớ cơ bắp / ngắn hạn / dài hạn · Mơ | `memory/muscle` / `short_term` / `long_term` · dream |

---

## 6. Changing the city

- **New building**: allowed when needed (owner, or whoever edits the repo, Claude Code included). Add it to the
  `regions.json` (one line in `rules`) and tell the owner.
- **New zone**: **ask the owner first.** Never add one on your own.
- **New or moved file**: nothing to do under `src/pylos/<zone>/<building>/`. A new top-level folder or building needs one line in
  [`regions.json`](regions.json) `rules` (the tests fail when a tracked file would land in the unplaced region by accident).

---

## 7. Decisions

Settled in owner Q&A rounds 1–2 (2026-11). Round 3 is **open**; until it is answered, the defaults below are
working assumptions, not decisions.

| Open question (round 3) | Working assumption |
|---|---|
| Start/stop code: `dispatch` or `side_gate` | `dispatch` decides; OS operations (systemctl, processes) stay in `side_gate` |
| `side_gate/cron` apartment | system schedule in `dispatch`, per-bot schedule in the bot's apartment, no `side_gate/cron` |
| Who counts as a "stranger" for spam limits | hut created at once, marked "not approved", rate-limited until the owner approves |
| Can other bots enter a hut | postponed until there are two or more bots |
| In a group, can the bot read members' personal huts | no — only the group's hut |
| Short-term memory vs. personal data | personal parts go straight to the hut; short-term keeps only de-identified material |
| Where secrets live | `src/pylos/management/owner/secrets/settings.env` as today; `owner/` only documents them |
| Bus technology | a bus interface with an in-process implementation; SQLite once there are several processes |
| Bot entry point | `python -m bot run` / `python -m bot gui` stay (the VPS systemd unit depends on them) |
| Root package | `src/pylos/` |
| Where data lives | moved into the city (2026-11): secrets and runtime files in `management/owner/{secrets,runtime}`, chat data in huts `gate/guest_house/huts/<chat_id>/` (one hut per person or group: `memorydata.txt`, `session_history.txt`) plus shared settings in `gate/guest_house/data`, custom tools in `lobby/office/agent_tools/custom` (all git-ignored); the bot's own `workspace/` in its apartment `residential/residents/pylos/` and its general rules `gate/fence/SYSTEM.md` (the bot cannot edit them) are tracked by git. No `userdata/` any more |
| Dangerous commands over Zalo | `shell` and destructive commands only from the admin web UI |
| Scripts inside skills | muscle memory is text only; scripts run only from vetted library skills, through `office` |
| Persona rules | kept outside the bot's apartment, loaded into the prompt at run time |
| Temporary promotion | tied to one task, revoked when it is done |
| Tests | `tests/` at the top, mirroring the city |
