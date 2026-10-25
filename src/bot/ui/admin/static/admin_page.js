"use strict";

// Giao diện quản lý bot. Mọi nội dung lấy từ server được gán bằng textContent
// (không dùng innerHTML) vì tin nhắn, tên người dùng, log là dữ liệu không đáng tin.

const TOKEN_KEY = "zalo-bot-admin-token";
const TARGET_KEY = "zalo-bot-admin-target";
const PAGES = [
  ["overview", "Tổng quan"],
  ["servers", "Máy chủ"],
  ["groups", "Nhóm"],
  ["history", "Hội thoại"],
  ["workspace", "Chỉ dẫn"],
  ["playground", "Chat thử"],
  ["logs", "Log"],
  ["failed", "Tin lỗi"],
  ["settings", "Cài đặt"],
  ["tools", "Tool"],
];

const state = {
  token: null,
  target: "local",    // "local": điều khiển bot ở máy này; "vps": mọi trang đi qua /api/remote tới VPS
  remote: null,       // kết quả /api/remote-status (đã cấu hình VPS chưa, có kết nối được không)
  page: "overview",
  status: null,
  cleanup: [],        // hàm dọn dẹp của trang hiện tại (timer, kết nối log...)
  busy: false,        // đang bật/tắt bot: không vẽ lại trang Tổng quan
  dirty: null,        // hàm trả về true nếu trang có thay đổi chưa lưu
  playground: [],     // lịch sử Chat thử, chỉ giữ trong trình duyệt
  historyChat: null,
};

// ---------- tiện ích ----------

function storageGet(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}
function storageSet(key, value) {
  try { value === null ? localStorage.removeItem(key) : localStorage.setItem(key, value); } catch { /* bỏ qua */ }
}

function h(tag, props = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props || {})) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") el.className = value;
    else if (key === "text") el.textContent = value;
    // CSP chặn thuộc tính style="..." nhưng cho phép gán qua CSSOM.
    else if (key === "style") el.style.cssText = value;
    // textarea không nhận nội dung qua thuộc tính value; luôn gán qua property.
    else if (key === "value") el.value = value;
    else if (key.startsWith("on")) el.addEventListener(key.slice(2), value);
    else if (key in el && typeof value !== "string") el[key] = value;
    else el.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

// Thay nội dung một phần tử; bỏ qua null/false (replaceChildren sẽ in chúng ra thành chữ "null").
function fill(el, ...children) {
  el.replaceChildren(...children.flat().filter((c) => c !== null && c !== undefined && c !== false));
}

function toast(message, kind = "info") {
  const el = h("div", { class: `toast ${kind}`, role: kind === "error" ? "alert" : "status", text: message });
  document.getElementById("toasts").append(el);
  setTimeout(() => el.remove(), kind === "error" ? 9000 : 4500);
}

function ago(ms) {
  if (!ms) return "chưa có";
  const s = Math.max(0, Math.round((Date.now() - ms) / 1000));
  if (s < 60) return `${s} giây trước`;
  if (s < 3600) return `${Math.round(s / 60)} phút trước`;
  if (s < 86400) return `${Math.round(s / 3600)} giờ trước`;
  return `${Math.round(s / 86400)} ngày trước`;
}

function timeText(ms) {
  return ms ? new Date(ms).toLocaleString("vi-VN") : "";
}

function num(n) {
  return Number(n || 0).toLocaleString("vi-VN");
}

class ApiError extends Error {}

// Đường dẫn thật cho bên được chọn: bên VPS đi qua proxy /api/remote của server ở máy này.
function sidePath(path, side = state.target) {
  return side === "vps" && path.startsWith("/api/") ? `/api/remote/${path.slice(5)}` : path;
}

async function api(path, { method = "GET", body, signal, side } = {}) {
  const headers = { Authorization: `Bearer ${state.token}` };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  path = sidePath(path, side);
  const res = await fetch(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), signal });
  if (res.status === 401) {
    showLogin("Mã truy cập không đúng hoặc đã đổi.");
    throw new ApiError("Chưa đăng nhập");
  }
  let data = null;
  try { data = await res.json(); } catch { /* không phải JSON */ }
  if (!res.ok) throw new ApiError((data && (data.error || data.detail)) || `Lỗi HTTP ${res.status}`);
  return data;
}

function reportError(err) {
  if (err instanceof DOMException && err.name === "AbortError") return;
  if (err instanceof ApiError && err.message === "Chưa đăng nhập") return;
  toast(err.message || String(err), "error");
}

// ---------- đăng nhập ----------

function showLogin(message) {
  state.token = null;
  storageSet(TOKEN_KEY, null);
  document.getElementById("app").hidden = true;
  document.getElementById("login").hidden = false;
  const error = document.getElementById("login-error");
  error.hidden = !message;
  error.textContent = message || "";
  document.getElementById("login-token").focus();
  clearInterval(gmailTimer);
  document.getElementById("gmail-btn").disabled = false;
  gmailMessage("");
}

async function tryLogin(token) {
  state.token = token;
  try {
    await api("/api/status");
  } catch (err) {
    if (!(err instanceof ApiError && err.message === "Chưa đăng nhập")) showLogin(err.message);
    return false;
  }
  storageSet(TOKEN_KEY, token);
  document.getElementById("login").hidden = true;
  document.getElementById("app").hidden = false;
  return true;
}

// ---------- điều hướng ----------

function buildNav() {
  const nav = document.getElementById("nav");
  nav.replaceChildren(...PAGES.map(([id, label]) =>
    h("button", { type: "button", "data-page": id, text: label, onclick: () => go(id) })));
}

function go(page) {
  if (state.dirty && state.dirty() && !confirm("Có thay đổi chưa lưu. Rời trang này?")) return;
  location.hash = `#/${page}`;
}

function currentPageFromHash() {
  const id = location.hash.replace(/^#\/?/, "").split("?")[0];
  return PAGES.some(([p]) => p === id) ? id : "overview";
}

function render() {
  for (const fn of state.cleanup.splice(0)) fn();
  state.dirty = null;
  state.page = currentPageFromHash();
  for (const btn of document.querySelectorAll("#nav button")) {
    if (btn.dataset.page === state.page) btn.setAttribute("aria-current", "page");
    else btn.removeAttribute("aria-current");
  }
  const main = document.getElementById("main");
  fill(main, );
  const label = PAGES.find(([p]) => p === state.page)[1];
  document.title = `${label} · iforgotmywayhome · Bot Zalo`;
  Promise.resolve(RENDERERS[state.page](main)).catch(reportError);
}

// ---------- bên được điều khiển: máy này hay VPS ----------

function applyTarget() {
  const vps = state.target === "vps";
  document.body.classList.toggle("target-vps", vps);
  const box = document.getElementById("target-switch");
  box.hidden = !(state.remote && state.remote.configured);
  for (const b of box.querySelectorAll("button")) {
    if (b.dataset.target === state.target) b.setAttribute("aria-pressed", "true");
    else b.removeAttribute("aria-pressed");
  }
}

function setTarget(target) {
  if (target === state.target) return;
  if (state.dirty && state.dirty() && !confirm("Có thay đổi chưa lưu. Rời trang này?")) return;
  state.target = target;
  storageSet(TARGET_KEY, target);
  state.status = null;
  applyTarget();
  render();
  pollStatus();
}

async function pollRemote() {
  try {
    state.remote = await api("/api/remote-status", { side: "local" });
  } catch { return; }
  if (!state.remote.configured && state.target === "vps") {
    state.target = "local";
    storageSet(TARGET_KEY, null);
    render();
  }
  applyTarget();
}

// ---------- trạng thái chung (góc trên) ----------

async function pollStatus() {
  try {
    state.status = await api("/api/status");
  } catch (err) {
    reportError(err);
    return;
  }
  const pill = document.getElementById("status-pill");
  const s = state.status;
  pill.textContent = s.running ? "Đang chạy" : s.standby ? "Đang chờ" : "Đã dừng";
  pill.className = `pill ${s.running ? (s.alerts.length ? "warn" : "ok") : "off"}`;
  if (state.page === "overview" && !state.busy) renderOverview(document.getElementById("main"));
}

// ---------- Tổng quan ----------

async function controlBot(action, label) {
  state.busy = true;
  for (const b of document.querySelectorAll("[data-control]")) b.disabled = true;
  const btn = document.querySelector(`[data-control="${action}"]`);
  if (btn) btn.textContent = `${label}…`;
  try {
    const res = await api(`/api/bot/${action}`, { method: "POST" });
    toast(res.message, res.ok ? "ok" : "error");
  } catch (err) {
    reportError(err);
  } finally {
    state.busy = false;
    await pollStatus();
  }
}

function stat(label, value, extra) {
  return h("div", { class: "card stat" }, h("div", { class: "label", text: label }), h("div", { class: "value", text: value }), extra);
}

function renderOverview(main) {
  const s = state.status;
  if (!s) {
    fill(main, h("p", { class: "muted", text: "Đang tải…" }));
    return pollStatus();
  }
  const budget = s.token_budget || 0;
  const used = s.tokens_today || 0;
  const pct = budget ? Math.min(100, Math.round((used / budget) * 100)) : 0;
  const tokenExtra = budget
    ? h("div", {}, h("div", { class: `progress${pct >= 100 ? " full" : ""}` }, h("div", { style: `width:${pct}%` })),
        h("div", { class: "label", text: `${pct}% của ${num(budget)}` }))
    : h("div", { class: "label", text: "không giới hạn" });

  const controls = h("div", { class: "row" },
    h("button", { class: "btn primary", type: "button", "data-control": "start", disabled: s.running, text: "Bật bot",
      onclick: () => controlBot("start", "Đang bật") }),
    h("button", { class: "btn", type: "button", "data-control": "restart", disabled: !s.running, text: "Khởi động lại",
      onclick: () => controlBot("restart", "Đang khởi động lại") }),
    h("button", { class: "btn danger", type: "button", "data-control": "stop", disabled: !s.running, text: "Tắt bot",
      onclick: () => confirm("Tắt bot? Bot sẽ không trả lời tin nhắn cho đến khi bật lại.") && controlBot("stop", "Đang tắt") }),
  );

  const maxTokens = Math.max(1, ...s.days.map((d) => d.tokens));
  const chart = s.days.length
    ? h("div", { class: "chart", role: "img", "aria-label": "Token theo ngày" },
        s.days.map((d) => h("div", { class: "bar", title: `${d.day}: ${num(d.tokens)} token, ${num(d.replied)} câu trả lời` },
          h("div", { style: `height:${Math.round((d.tokens / maxTokens) * 100)}%` }),
          h("span", { text: d.day.slice(8, 10) + "/" + d.day.slice(5, 7) }))))
    : h("p", { class: "empty", text: "Chưa có số liệu." });

  const updateBanner = s.updates_pending ? h("div", { class: "banner" },
    h("span", { text: `Có ${s.updates_pending} thay đổi mới trên GitHub. ` }),
    h("button", { class: "btn small primary", type: "button", text: "Cập nhật ngay", onclick: async (e) => {
      e.target.disabled = true;
      e.target.textContent = "Đang cập nhật…";
      try {
        const res = await api("/api/update", { method: "POST" });
        toast(res.message, res.ok ? "ok" : "error");
      } catch (err) { reportError(err); }
    } })) : null;

  fill(main, 
    h("h1", { text: "Tổng quan" }),
    updateBanner,
    s.alerts.length ? h("ul", { class: "alerts" }, s.alerts.map((a) => h("li", { text: a }))) : null,
    h("div", { class: "card" },
      h("div", { class: "row between" },
        h("div", { class: "row" },
          h("span", { class: `pill ${s.running ? "ok" : "off"}`, text: s.running ? "Đang chạy" : "Đã dừng" }),
          s.running && s.pid ? h("span", { class: "muted small", text: `pid ${s.pid}` }) : null),
        controls),
      h("dl", { class: "kv", style: "margin-top:.75rem" },
        h("dt", { text: "Chạy từ" }), h("dd", { text: s.running ? ago(s.started_at) : "—" }),
        h("dt", { text: "Zalo phản hồi lần cuối" }), h("dd", { text: ago(s.last_poll_at) }),
        h("dt", { text: "Tin nhắn cuối" }), h("dd", { text: ago(s.last_message_at) }),
        h("dt", { text: "Nhận tin" }), h("dd", { text: s.receive_mode }),
        h("dt", { text: "Model" }), h("dd", { class: "mono", text: s.model }),
        h("dt", { text: "Tự chạy khi đăng nhập" }), h("dd", { text: s.autostart ? "có (ứng dụng ZaloBot)"
          : s.task_installed ? "có (Task Scheduler)" : "chưa bật · bật ở menu khay: Khởi động cùng Windows" }))),
    h("div", { class: "grid" },
      stat("Tin nhận hôm nay", num(s.today.received)),
      stat("Đã trả lời", num(s.today.replied)),
      stat("Bộ lọc (nhóm)", `${num(s.today.filter_pass)} qua · ${num(s.today.filter_block)} chặn`,
        h("div", { class: "label", text: "tin trong nhóm hôm nay" })),
      stat("Lỗi", num(s.today.errors)),
      stat("Token hôm nay", num(used), tokenExtra)),
    h("div", { class: "card" }, h("h2", { text: "Token 14 ngày gần nhất" }), chart),
    h("div", { class: "card" },
      h("div", { class: "row between" }, h("h2", { text: "Nhóm được phép" }),
        h("button", { class: "btn small", type: "button", text: "Quản lý nhóm", onclick: () => go("groups") })),
      s.allowed_groups.length
        ? h("ul", {}, s.allowed_groups.map((g) => h("li", {}, g.label || h("span", { class: "mono", text: g.chat_id }),
            h("span", { class: "muted", text: ` · chế độ ${g.mode}` }))))
        : h("p", { class: "muted", text: "Chưa có nhóm nào. Thêm bot vào nhóm, nhắn một tin, rồi bật ở trang Nhóm." })),
  );
}

// ---------- Máy chủ: so sánh máy này với VPS ----------

function bytesText(n) {
  if (!n) return "—";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let i = 0;
  while (n >= 1024 && i < units.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(n >= 10 || i === 0 ? 0 : 1)} ${units[i]}`;
}

function durationText(seconds) {
  if (seconds === null || seconds === undefined) return "—";
  const d = Math.floor(seconds / 86400), hrs = Math.floor((seconds % 86400) / 3600), min = Math.floor((seconds % 3600) / 60);
  return d ? `${d} ngày ${hrs} giờ` : hrs ? `${hrs} giờ ${min} phút` : `${min} phút`;
}

async function serverAction(side, action, label, button) {
  const old = button.textContent;
  button.disabled = true;
  button.textContent = `${label}…`;
  try {
    const res = await api(action === "update" ? "/api/update" : `/api/bot/${action}`, { method: "POST", side });
    toast(res.message, res.ok ? "ok" : "error");
  } catch (err) { reportError(err); }
  button.textContent = old;
  await loadServers();
}

function serverCard(side, title, data, error) {
  if (error) {
    return h("div", { class: `card server ${side}` }, h("h2", { text: title }),
      h("p", { class: "error", text: error }));
  }
  const bot = data.bot, v = data.version || {}, mem = data.memory;
  const badge = bot.running ? ["ok", "Bot đang chạy"] : bot.standby ? ["warn", "Đang chờ (bot ở máy khác)"] : ["off", "Bot đã dừng"];
  const rows = [
    ["Máy", `${data.hostname} · ${data.os}`],
    ["Máy đã chạy", durationText(data.uptime_seconds)],
    data.load ? ["Tải (1/5/15 phút)", data.load.join(" · ")] : null,
    mem ? ["RAM", `${bytesText(mem.total - mem.available)} / ${bytesText(mem.total)}`] : null,
    data.disk ? ["Ổ đĩa trống", `${bytesText(data.disk.free)} / ${bytesText(data.disk.total)}`] : null,
    ["Code", v.git ? `${(v.head || "").slice(0, 7)} · ${v.subject || ""}` : "không phải bản git (exe)"],
    ["Zalo phản hồi lần cuối", bot.running ? ago(bot.last_poll_at) : "—"],
    ["Nhận tin", `${bot.receive_mode} · ${bot.model}`],
    data.units ? ["Service", Object.entries(data.units).map(([k, val]) => `${k}: ${val || "?"}`).join(" · ")] : null,
    data.last_update && data.last_update.at ? ["Cập nhật tự động cuối", `${data.last_update.at} (${data.last_update.result})`] : null,
    bot.standby ? ["Chế độ chờ", bot.standby.reason] : null,
  ].filter(Boolean);
  const buttons = [];
  const act = (action, label, text, cls = "btn", disabled = false) => buttons.push(
    h("button", { class: cls, type: "button", text, disabled, onclick: (e) => {
      if (action === "stop" && !confirm(`Tắt bot trên ${title}?`)) return;
      serverAction(side, action, label, e.target);
    } }));
  act("start", "Đang bật", "Bật bot", "btn primary", bot.running);
  act("restart", "Đang khởi động lại", "Khởi động lại", "btn", !bot.running);
  act("stop", "Đang tắt", "Tắt bot", "btn danger", !bot.running);
  if (v.git || data.supervisor === "systemd") {
    act("update", "Đang cập nhật", v.behind ? "Cập nhật ngay" : "Cập nhật code", v.behind ? "btn primary" : "btn");
  }
  return h("div", { class: `card server ${side}` },
    h("div", { class: "row between" }, h("h2", { text: title }), h("span", { class: `pill ${badge[0]}`, text: badge[1] })),
    v.behind ? h("div", { class: "banner" }, h("span", { text: "Có code mới hơn trên GitHub." })) : null,
    h("dl", { class: "kv" }, rows.flatMap(([k, val]) => [h("dt", { text: k }), h("dd", { text: val })])),
    h("div", { class: "row" }, buttons));
}

// ---- chuyển bot giữa máy này và VPS ----

function stepIcon(status) {
  return status === "ok" ? "✓" : status === "error" ? "✗" : "…";
}

function drawJob(box, job) {
  fill(box,
    h("ul", { class: "steps" }, job.steps.map((s) => h("li", { class: s.status },
      h("span", { text: `${stepIcon(s.status)} ${s.label}` }),
      s.detail ? h("span", { class: "muted small", text: ` — ${s.detail}` }) : null))),
    job.state === "done" ? h("p", { class: "ok-text", text: job.message }) : null,
    job.state === "error" ? h("p", { class: "error", text: job.message }) : null);
}

async function moveBot(to) {
  const where = to === "vps" ? "VPS" : "máy này";
  if (!confirm(`Chuyển bot sang ${where}?\n\nBot sẽ tắt ở bên kia, dữ liệu (nhóm, lịch sử, ghi nhớ) được chép sang, rồi bật ở ${where}. ` +
    "Bot ngừng trả lời trong khoảng một phút.")) return;
  const box = document.getElementById("handover-progress");
  state.handoverBusy = true;
  for (const b of document.querySelectorAll("[data-move]")) b.disabled = true;
  try {
    await api("/api/handover", { method: "POST", body: { to }, side: "local" });
    for (;;) {
      await new Promise((r) => setTimeout(r, 1500));
      if (!document.getElementById("handover-progress")) return;
      const job = await api("/api/handover/job", { side: "local" });
      state.lastJob = job;
      drawJob(box, job);
      if (job.state !== "running") {
        toast(job.message, job.state === "done" ? "ok" : "error");
        break;
      }
    }
  } catch (err) { reportError(err); }
  state.handoverBusy = false;
  await loadServers();
}

function drawHandover(local, vps) {
  const box = document.getElementById("handover");
  if (!box || state.handoverBusy) return;
  const at = local && local.bot.running ? "máy này" : vps && vps.bot.running ? "VPS" : null;
  const standbyHere = Boolean(local && local.bot.standby);
  const move = (to, text, primary) => h("button", { class: primary ? "btn primary" : "btn", type: "button", "data-move": to, text,
    onclick: () => moveBot(to) });
  fill(box, h("div", { class: "card" },
    h("h2", { text: "Bot đang chạy ở" }),
    h("p", {}, h("strong", { text: at || "không nơi nào" }),
      at === null && standbyHere ? h("span", { class: "muted", text: " (máy này đang chờ, bot được giao cho VPS)" }) : null),
    h("div", { class: "row" },
      at !== "VPS" && vps ? move("vps", "Chuyển bot sang VPS", true) : null,
      at !== "máy này" && vps ? move("local", "Chuyển bot về máy này", at === "VPS") : null),
    h("div", { id: "handover-progress" })));
  if (state.lastJob) drawJob(document.getElementById("handover-progress"), state.lastJob);
}

async function loadServers() {
  if (!document.getElementById("servers-grid")) return;
  const configured = state.remote && state.remote.configured;
  const [local, vps] = await Promise.allSettled([
    api("/api/server", { side: "local" }),
    configured ? api("/api/server", { side: "vps" }) : Promise.reject(new Error("")),
  ]);
  const host = document.getElementById("servers-grid");
  if (!host) return;
  fill(host,
    serverCard("local", "Máy này", local.value, local.status === "rejected" ? local.reason.message : null),
    configured
      ? serverCard("vps", "VPS", vps.value, vps.status === "rejected" ? vps.reason.message : null)
      : h("div", { class: "card server vps" }, h("h2", { text: "VPS" }),
          h("p", { class: "muted", text: "Chưa kết nối VPS. Vào Cài đặt, điền địa chỉ trang quản lý trên VPS (REMOTE_URL) " +
            "và mã truy cập của VPS (REMOTE_ADMIN_TOKEN)." }),
          h("button", { class: "btn", type: "button", text: "Mở Cài đặt", onclick: () => { setTarget("local"); go("settings"); } })));
  drawHandover(local.value, configured ? vps.value : null);
  const bothOn = Boolean(local.value && vps.value && local.value.bot.running && vps.value.bot.running);
  const note = document.getElementById("servers-note");
  if (note) {
    note.hidden = !bothOn;
    note.textContent = bothOn ? "Cảnh báo: bot đang chạy ở cả hai nơi. Cùng một tài khoản Zalo sẽ trả lời trùng. Hãy tắt một bên." : "";
  }
}

async function renderServers(main) {
  fill(main, h("h1", { text: "Máy chủ" }),
    h("p", { class: "muted", text: "Xem và điều khiển bot ở máy này và trên VPS. Chỉ nên bật bot ở một nơi tại một thời điểm." }),
    h("p", { id: "servers-note", class: "error", hidden: true }),
    h("div", { id: "handover" }),
    h("div", { id: "servers-grid", class: "servers" }, h("p", { class: "muted", text: "Đang tải…" })));
  await pollRemote();
  await loadServers();
  const timer = setInterval(() => { if (!document.hidden) loadServers(); }, 10000);
  state.cleanup.push(() => clearInterval(timer));
}

// ---------- Nhóm ----------

async function renderGroups(main) {
  fill(main, h("h1", { text: "Nhóm và cuộc trò chuyện" }), h("p", { class: "muted", text: "Đang tải…" }));
  const data = await api("/api/groups");
  const list = h("div", { class: "card" });

  if (!data.groups.length) {
    list.append(h("p", { class: "empty", text: "Chưa có cuộc trò chuyện nào. Thêm bot vào nhóm (hoặc nhắn riêng cho bot) rồi gửi một tin, cuộc trò chuyện sẽ hiện ở đây." }));
  }
  for (const g of data.groups) {
    const isPrivate = g.type === "PRIVATE";
    const patch = async (body, okText) => {
      try {
        await api(`/api/groups/${encodeURIComponent(g.chat_id)}`, { method: "PATCH", body });
        toast(okText, "ok");
      } catch (err) { reportError(err); }
    };
    const label = h("input", { type: "text", value: g.label, maxLength: 60, placeholder: isPrivate ? `Chat riêng: ${g.last_name || ""}` : "Đặt tên cho nhóm này",
      "aria-label": "Tên gợi nhớ", onchange: (e) => patch({ label: e.target.value }, "Đã đổi tên") });
    const allowed = h("input", { type: "checkbox", checked: g.allowed || g.owner_private, disabled: g.owner_private,
      onchange: (e) => patch({ allowed: e.target.checked }, e.target.checked ? "Đã cho phép" : "Đã chặn") });
    const mode = h("select", { "aria-label": "Chế độ trả lời", disabled: isPrivate,
      onchange: (e) => patch({ mode: e.target.value }, `Chế độ: ${e.target.value}`) },
      h("option", { value: "default", text: "default: khi được gọi", selected: g.mode === "default" }),
      h("option", { value: "all", text: "all: mọi tin nhắn", selected: g.mode === "all" }));

    list.append(h("div", { class: "group-row" },
      h("div", {}, label, h("div", { class: "id", text: `${isPrivate ? "Chat riêng" : "Nhóm"} · ${g.chat_id}` }),
        isPrivate ? null : h("div", { class: "muted small", title: "Đổi bằng lệnh /leader trong nhóm",
          text: g.leaders_all ? "Giao lịch: mọi người (/leader all)"
            : g.leaders.length ? `Leader giao lịch: ${g.leaders.join(", ")}` : "Giao lịch: chỉ chủ bot" }),
        isPrivate || !g.teams.length ? null : h("div", { class: "muted small", title: "Đổi bằng lệnh /team trong nhóm",
          text: `Đội: ${g.teams.map((t) => `${t.name} (${t.members})`).join(", ")}` })),
      h("div", { class: "small" },
        h("div", { text: g.last_name ? `Người nhắn cuối: ${g.last_name}` : "" }),
        h("div", { class: "muted", text: g.last_seen ? ago(g.last_seen) : "chưa nhắn từ khi theo dõi" })),
      h("label", { class: "switch" }, allowed, h("span", { text: g.owner_private ? "Luôn được phép" : "Được phép" })),
      isPrivate ? h("span", { class: "muted small", text: "Chat riêng: luôn trả lời" }) : mode,
      h("div", { class: "row" },
        state.status && state.status.show_history === false ? null
          : h("button", { class: "btn small", type: "button", text: "Hội thoại",
              onclick: () => { state.historyChat = g.chat_id; go("history"); } }),
        h("button", { class: "btn small danger", type: "button", text: "Xóa lịch sử", onclick: async () => {
          if (!confirm("Xóa toàn bộ lịch sử hội thoại của cuộc trò chuyện này? Bot sẽ quên ngữ cảnh trước đó.")) return;
          try { await api(`/api/groups/${encodeURIComponent(g.chat_id)}/history`, { method: "DELETE" }); toast("Đã xóa lịch sử", "ok"); }
          catch (err) { reportError(err); }
        } }))));
  }

  fill(main, 
    h("div", { class: "row between" }, h("h1", { text: "Nhóm và cuộc trò chuyện" }),
      h("button", { class: "btn", type: "button", text: "Tải lại", onclick: () => renderGroups(main).catch(reportError) })),
    data.allow_all ? h("div", { class: "banner", text: "Đang bật \"Cho phép mọi cuộc trò chuyện\" (trang Cài đặt): bot trả lời ở mọi chat, trừ chat bị chặn. Bỏ tích ở đây để chặn riêng một chat." }) : null,
    h("p", { class: "muted", text: "Zalo không gửi tên nhóm, nên hãy đặt tên gợi nhớ. Thay đổi có hiệu lực ngay ở tin nhắn tiếp theo, không cần khởi động lại bot." }),
    list);
}

// ---------- Hội thoại ----------

async function renderHistory(main) {
  fill(main, h("h1", { text: "Hội thoại" }), h("p", { class: "muted", text: "Đang tải…" }));
  const status = state.status || await api("/api/status");
  if (!status.show_history) {
    fill(main, h("h1", { text: "Hội thoại" }),
      h("p", { class: "empty", text: "Trang này đang tắt (ADMIN_SHOW_HISTORY=false). Bật lại ở trang Cài đặt." }));
    return;
  }
  const { groups } = await api("/api/groups");
  if (!groups.length) {
    fill(main, h("h1", { text: "Hội thoại" }), h("p", { class: "empty", text: "Chưa có cuộc trò chuyện nào." }));
    return;
  }
  if (!state.historyChat || !groups.some((g) => g.chat_id === state.historyChat)) state.historyChat = groups[0].chat_id;

  const chat = h("div", { class: "chat", "aria-live": "polite" });
  const select = h("select", { "aria-label": "Chọn cuộc trò chuyện", onchange: (e) => { state.historyChat = e.target.value; load(true); } },
    groups.map((g) => h("option", { value: g.chat_id, selected: g.chat_id === state.historyChat,
      text: `${g.label || (g.type === "PRIVATE" ? `Chat riêng ${g.last_name}` : "Nhóm")} · ${g.chat_id.slice(0, 10)}…` })));

  // Session: tin đã qua bộ lọc (bot dùng làm ngữ cảnh). Memorydata: mọi tin, kèm kết quả bộ lọc.
  const VIEWS = {
    session: { api: "history", note: "Session: lịch sử bot dùng làm ngữ cảnh, chỉ gồm tin đã qua bộ lọc và câu trả lời của bot." },
    memory: { api: "memorydata", note: "Memorydata: mọi tin của cuộc trò chuyện (data/memorydata), kèm kết quả bộ lọc. Tin bị chặn có viền đứt." },
  };
  state.historyView = state.historyView || "session";
  const note = h("p", { class: "muted small" });
  const viewSelect = h("select", { "aria-label": "Chọn loại dữ liệu", onchange: (e) => { state.historyView = e.target.value; load(true); } },
    h("option", { value: "session", text: "Session", selected: state.historyView === "session" }),
    h("option", { value: "memory", text: "Memorydata (tất cả tin)", selected: state.historyView === "memory" }));

  function filterTag(f) {
    if (!f) return null;
    const label = f.passed ? "qua lọc" : "bị chặn";
    return h("span", { class: `pill small ${f.passed ? "ok" : "off"}`, title: f.reason || "", text: `${label} · ${f.stage}${f.reason ? `: ${f.reason}` : ""}` });
  }

  let lastKey = "";
  async function load(force = false) {
    const view = VIEWS[state.historyView] || VIEWS.session;
    note.textContent = view.note + " Tự cập nhật mỗi 5 giây.";
    const data = await api(`/api/${view.api}/${encodeURIComponent(state.historyChat)}?n=200`);
    const key = `${state.historyView}:${data.messages.length}:${data.messages.length ? data.messages[data.messages.length - 1].t : 0}`;
    if (!force && key === lastKey) return;
    lastKey = key;
    const nearBottom = chat.scrollHeight - chat.scrollTop - chat.clientHeight < 60;
    chat.replaceChildren(...(data.messages.length ? data.messages.map((m) =>
      h("div", { class: `bubble ${m.role === "model" ? "model" : "user"}${m.filter && !m.filter.passed ? " blocked" : ""}` },
        h("span", { class: "meta", text: `${m.role === "model" ? "Bot" : (m.name || "Người dùng")} · ${timeText(m.t)}` }),
        m.type === "other" ? "[ảnh/sticker/tệp]" : m.text,
        filterTag(m.filter))) : [h("p", { class: "empty", text: "Chưa có tin nào." })]));
    if (force || nearBottom) chat.scrollTop = chat.scrollHeight;
  }

  fill(main, 
    h("h1", { text: "Hội thoại" }),
    h("div", { class: "row", style: "margin-bottom:.75rem" }, h("div", { style: "flex:1;min-width:220px" }, select), viewSelect,
      h("button", { class: "btn", type: "button", text: "Tải lại", onclick: () => load(true).catch(reportError) })),
    note,
    h("div", { class: "card" }, chat));
  await load(true);
  const timer = setInterval(() => load().catch(reportError), 5000);
  state.cleanup.push(() => clearInterval(timer));
}

// ---------- Chỉ dẫn (SYSTEM.md / MEMORY.md) ----------

async function renderWorkspace(main, which = "SYSTEM") {
  const data = await api(`/api/workspace/${which}`);
  let saved = data.content;
  const area = h("textarea", { rows: 22, spellcheck: false, value: data.content, "aria-label": `Nội dung ${which}.md` });
  const info = h("span", { class: "muted small" });
  const showInfo = (when) => { info.textContent = area.value !== saved ? "Có thay đổi chưa lưu" : (when ? `Đã lưu ${ago(when)}` : "Chưa có file"); };
  showInfo(data.updated_at);
  area.addEventListener("input", () => showInfo(data.updated_at));

  async function save() {
    try {
      const res = await api(`/api/workspace/${which}`, { method: "PUT", body: { content: area.value } });
      saved = area.value;
      data.updated_at = res.updated_at;
      showInfo(res.updated_at);
      toast(`Đã lưu ${which}.md. Bot dùng nội dung mới ngay ở tin nhắn sau.`, "ok");
    } catch (err) { reportError(err); }
  }
  area.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") { e.preventDefault(); save(); }
  });
  state.dirty = () => area.value !== saved;

  const tab = (name, label) => h("button", { class: "btn", type: "button", role: "tab", "aria-selected": String(name === which), text: label,
    onclick: () => {
      if (name === which) return;
      if (state.dirty() && !confirm("Có thay đổi chưa lưu. Chuyển tab?")) return;
      renderWorkspace(main, name).catch(reportError);
    } });

  fill(main, 
    h("h1", { text: "Chỉ dẫn cho trợ lý" }),
    h("div", { class: "tabs", role: "tablist" }, tab("SYSTEM", "SYSTEM.md · Tính cách"), tab("MEMORY", "MEMORY.md · Ghi nhớ")),
    h("p", { class: "muted", text: which === "SYSTEM"
      ? "Vai trò, giọng điệu và quy tắc trả lời. Bản cũ được tự sao lưu vào workspace/.backup mỗi lần lưu."
      : "Điều trợ lý cần nhớ lâu dài. Được đưa vào prompt như dữ liệu tham khảo, không phải mệnh lệnh." }),
    data.managed_by_web
      ? h("div", { class: "banner", text: `${which}.md đang do chủ hệ thống đặt trên web (Hệ thống → Cấu hình bot). `
        + "Sửa ở đây sẽ bị ghi đè khi cấu hình trên web thay đổi." })
      : null,
    h("div", { class: "card stack" }, area,
      h("div", { class: "row between" }, info, h("button", { class: "btn primary", type: "button", text: "Lưu (Ctrl+S)", onclick: save }))));
}

// ---------- Chat thử ----------

function renderPlayground(main) {
  const chat = h("div", { class: "chat", "aria-live": "polite" });
  const input = h("textarea", { rows: 3, placeholder: "Nhập tin nhắn… (Enter để gửi, Shift+Enter xuống dòng)", "aria-label": "Tin nhắn" });
  const groupCtx = h("input", { type: "checkbox" });
  const sendBtn = h("button", { class: "btn primary", type: "button", text: "Gửi" });
  const info = h("span", { class: "muted small" });

  function draw() {
    chat.replaceChildren(...(state.playground.length ? state.playground.map((m) =>
      h("div", { class: `bubble ${m.role === "model" ? "model" : "user"}` },
        h("span", { class: "meta", text: m.role === "model" ? `Bot${m.tokens ? ` · ${m.tokens} token` : ""}` : "Bạn" }), m.text))
      : [h("p", { class: "empty", text: "Thử trợ lý với SYSTEM.md hiện tại. Tin ở đây không gửi lên Zalo và không lưu vào lịch sử nhóm, nhưng token vẫn được tính." })]));
    chat.scrollTop = chat.scrollHeight;
  }

  async function send() {
    const text = input.value.trim();
    if (!text) return;
    state.playground.push({ role: "user", text });
    input.value = "";
    draw();
    sendBtn.disabled = true;
    info.textContent = "Đang trả lời…";
    try {
      const res = await api("/api/playground", { method: "POST", body: {
        messages: state.playground.slice(-40).map(({ role, text: t }) => ({ role, text: t })), is_group: groupCtx.checked } });
      if (!res.ok) throw new ApiError(res.message);
      state.playground.push({ role: "model", text: res.reply, tokens: res.tokens });
      info.textContent = res.echo ? "Chưa có GEMINI_API_KEY: đang dùng chế độ lặp lại (echo)." : "";
    } catch (err) {
      state.playground.pop();
      input.value = text;
      info.textContent = "";
      reportError(err);
    } finally {
      sendBtn.disabled = false;
      draw();
      input.focus();
    }
  }

  sendBtn.addEventListener("click", send);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(); }
  });

  fill(main, 
    h("div", { class: "row between" }, h("h1", { text: "Chat thử" }),
      h("button", { class: "btn", type: "button", text: "Cuộc trò chuyện mới", onclick: () => { state.playground = []; draw(); } })),
    h("div", { class: "card" }, chat),
    h("div", { class: "card stack" }, input,
      h("div", { class: "row between" },
        h("label", { class: "switch" }, groupCtx, h("span", { text: "Giả lập ngữ cảnh nhóm" })),
        h("div", { class: "row" }, info, sendBtn))));
  draw();
  input.focus();
}

// ---------- Log ----------

const LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];
const LOG_LINE = /^\d{4}-\d{2}-\d{2} [\d:,]+ (DEBUG|INFO|WARNING|ERROR|CRITICAL) /;

function renderLogs(main) {
  const box = h("div", { class: "log", role: "log", "aria-live": "off" });
  const source = h("select", { "aria-label": "Nguồn log" }, h("option", { value: "bot", text: "Bot" }), h("option", { value: "admin", text: "Giao diện" }));
  const level = h("select", { "aria-label": "Mức log" },
    h("option", { value: "", text: "Mọi mức" }), h("option", { value: "INFO", text: "INFO trở lên", selected: true }),
    h("option", { value: "WARNING", text: "Cảnh báo trở lên" }), h("option", { value: "ERROR", text: "Chỉ lỗi" }));
  const live = h("input", { type: "checkbox", checked: true });
  let controller = null;

  const minLevel = () => (level.value ? LEVELS.indexOf(level.value) : 0);
  function addEntry(lvl, text) {
    if (LEVELS.indexOf(lvl) < minLevel()) return;
    const nearBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 80;
    box.append(h("div", { class: lvl, text }));
    while (box.childElementCount > 3000) box.firstElementChild.remove();
    if (nearBottom) box.scrollTop = box.scrollHeight;
  }

  function stopLive() {
    if (controller) controller.abort();
    controller = null;
  }

  async function startLive() {
    stopLive();
    if (!live.checked) return;
    controller = new AbortController();
    const signal = controller.signal;
    try {
      const res = await fetch(sidePath(`/api/logs/stream?source=${source.value}`), { headers: { Authorization: `Bearer ${state.token}` }, signal });
      if (!res.ok || !res.body) throw new ApiError(`Không theo dõi được log (HTTP ${res.status})`);
      const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
      let buffer = "";
      let lastLevel = "INFO";
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += value;
        const lines = buffer.split("\n");
        buffer = lines.pop();
        for (const line of lines) {
          if (!line) continue;
          const m = LOG_LINE.exec(line);
          if (m) lastLevel = m[1];
          addEntry(lastLevel, line);
        }
      }
    } catch (err) {
      reportError(err);
    }
  }

  async function load() {
    stopLive();
    const data = await api(`/api/logs?source=${source.value}&n=300&level=${level.value}`);
    box.replaceChildren(...(data.entries.length ? data.entries.map((e) => h("div", { class: e.level, text: e.text }))
      : [h("div", { class: "muted", text: "(chưa có log)" })]));
    box.scrollTop = box.scrollHeight;
    startLive();
  }

  for (const el of [source, level]) el.addEventListener("change", () => load().catch(reportError));
  live.addEventListener("change", () => (live.checked ? startLive() : stopLive()));
  state.cleanup.push(stopLive);

  fill(main, 
    h("h1", { text: "Log" }),
    h("div", { class: "row", style: "margin-bottom:.75rem" },
      h("div", { style: "width:150px" }, source), h("div", { style: "width:190px" }, level),
      h("label", { class: "switch" }, live, h("span", { text: "Theo dõi trực tiếp" })),
      h("button", { class: "btn", type: "button", text: "Tải lại", onclick: () => load().catch(reportError) })),
    box);
  return load();
}

// ---------- Tin lỗi ----------

async function renderFailed(main) {
  const data = await api("/api/failed");
  const act = async (id, action) => {
    try {
      const res = await api(`/api/failed/${encodeURIComponent(id)}/${action}`, { method: "POST" });
      toast(res.message, res.ok ? "ok" : "error");
      if (res.ok) await renderFailed(main);
    } catch (err) { reportError(err); }
  };
  fill(main, 
    h("h1", { text: "Tin gửi lỗi" }),
    h("p", { class: "muted", text: "Câu trả lời bot đã soạn nhưng gửi lên Zalo thất bại sau 3 lần thử." }),
    ...(data.items.length ? data.items.map((item) => h("div", { class: "card stack" },
      h("div", { class: "row between" },
        h("span", { class: "mono small", text: item.chat_id }),
        h("span", { class: "muted small", text: timeText(item.t) })),
      h("div", { class: "error small", text: item.error || "" }),
      h("div", { style: "white-space:pre-wrap", text: (item.text || "").slice(0, 600) + ((item.text || "").length > 600 ? "…" : "") }),
      h("div", { class: "row" },
        h("button", { class: "btn primary small", type: "button", text: "Gửi lại", onclick: () => act(item.id, "retry") }),
        h("button", { class: "btn small", type: "button", text: "Bỏ qua", onclick: () => act(item.id, "dismiss") }))))
      : [h("p", { class: "empty", text: "Không có tin lỗi nào." })]));
}

// ---------- Đăng nhập acc Zalo cá nhân bằng mã QR ----------

function zaloLoginCard() {
  const info = h("p", { class: "muted small" });
  const image = h("img", { class: "qr", alt: "Mã QR đăng nhập Zalo", hidden: true });
  const message = h("p", { role: "status" });
  const startBtn = h("button", { class: "btn primary", type: "button", text: "Đăng nhập bằng mã QR" });
  const cancelBtn = h("button", { class: "btn", type: "button", text: "Huỷ", hidden: true });
  let timer = null;

  function show(data) {
    const s = data.session || {};
    info.textContent = s.exists
      ? `Đang dùng acc: ${s.display_name || "(không rõ tên)"}${s.saved_at ? ` · đăng nhập ${timeText(s.saved_at)}` : ""}`
        + (s.personal ? "" : " · chưa bật (RECEIVE_MODE không phải personal)")
      : "Chưa đăng nhập acc Zalo cá nhân nào.";
    const active = ["starting", "waiting_scan", "scanned"].includes(data.state);
    image.hidden = !data.image;
    if (data.image) image.src = `data:image/png;base64,${data.image}`;
    message.textContent = data.message || "";
    message.className = data.state === "success" ? "ok" : ["error", "declined", "expired"].includes(data.state) ? "error" : "";
    startBtn.hidden = active;
    startBtn.textContent = s.exists ? "Đăng nhập lại / đổi acc bằng mã QR" : "Đăng nhập bằng mã QR";
    cancelBtn.hidden = !active;
    if (!active && timer) { clearInterval(timer); timer = null; }
  }

  async function poll() {
    try { show(await api("/api/zalo-login")); } catch (err) { reportError(err); }
  }

  function watch() {
    if (!timer) timer = setInterval(poll, 1500);
  }

  startBtn.addEventListener("click", async () => {
    try { show(await api("/api/zalo-login/start", { method: "POST" })); watch(); } catch (err) { reportError(err); }
  });
  cancelBtn.addEventListener("click", async () => {
    try { show(await api("/api/zalo-login/cancel", { method: "POST" })); } catch (err) { reportError(err); }
  });
  state.cleanup.push(() => { if (timer) clearInterval(timer); });
  api("/api/zalo-login").then((data) => {
    show(data);
    if (["starting", "waiting_scan", "scanned"].includes(data.state)) watch();
  }).catch(reportError);

  return h("div", { class: "card stack" },
    h("h2", { text: "Acc Zalo cá nhân (đăng nhập bằng mã QR)" }),
    h("p", { class: "muted small", text: "Cho bot chạy trên một acc Zalo cá nhân thay vì Zalo Bot. Trên điện thoại đang đăng nhập "
      + "ACC PHỤ, mở Zalo → biểu tượng quét mã → quét mã bên dưới → bấm Đăng nhập. Cách này không chính thức: "
      + "acc có thể bị Zalo khoá, đừng dùng acc chính." }),
    info, image, message, h("div", { class: "row" }, startBtn, cancelBtn));
}

// ---------- Cài đặt ----------

async function renderSettings(main) {
  const data = await api("/api/settings");
  const inputs = new Map();
  const groups = new Map();
  for (const f of data.fields) {
    let input;
    if (f.kind === "choice") {
      input = h("select", {}, f.choices.map((c) => h("option", { value: c, text: c, selected: c === f.value })));
    } else if (f.kind === "bool") {
      input = h("select", {}, h("option", { value: "true", text: "Bật", selected: f.value === "true" }),
        h("option", { value: "false", text: "Tắt", selected: f.value === "false" }));
    } else {
      input = h("input", { type: f.kind === "int" ? "number" : "text", value: f.value, min: f.kind === "int" ? "0" : undefined });
    }
    input.dataset.initial = input.value;
    inputs.set(f.key, input);
    if (!groups.has(f.group)) groups.set(f.group, []);
    // Thông số chủ hệ thống đặt trên web đè lên giá trị ở đây khi bot chạy.
    const fromWeb = f.remote !== null && f.remote !== undefined
      ? h("span", { class: "pill web", title: "Đặt ở trang Hệ thống của web iforgotmywayhome; sửa ở đây không có tác dụng cho tới khi bỏ trên web",
        text: `Web đang đặt: ${f.remote}` })
      : null;
    groups.get(f.group).push(h("label", { class: "field" }, h("span", {}, f.label, fromWeb), input,
      h("small", {}, h("code", { text: f.key }), f.help ? ` · ${f.help}` : "")));
  }

  const changed = () => Object.fromEntries([...inputs].filter(([, el]) => el.value !== el.dataset.initial).map(([k, el]) => [k, el.value]));
  state.dirty = () => Object.keys(changed()).length > 0;

  const banner = h("div", { class: "banner", hidden: true },
    h("span", { text: "Đã lưu vào userdata/config/settings.env. Khởi động lại bot để áp dụng. " }),
    h("button", { class: "btn small", type: "button", text: "Khởi động lại bot", onclick: async () => {
      await controlBot("restart", "Đang khởi động lại");
      banner.hidden = true;
    } }));

  async function save() {
    const values = changed();
    if (!Object.keys(values).length) { toast("Không có thay đổi."); return; }
    try {
      const res = await api("/api/settings", { method: "PUT", body: { values } });
      for (const el of inputs.values()) el.dataset.initial = el.value;
      banner.hidden = false;
      toast(res.message, "ok");
    } catch (err) { reportError(err); }
  }

  const secrets = data.secrets.map((s) => {
    const input = h("input", { type: "password", autocomplete: "new-password", placeholder: s.set ? "Nhập giá trị mới để thay" : "Chưa đặt" });
    const badge = h("span", { class: `pill ${s.set ? "ok" : "off"}`, text: s.set ? "Đã đặt" : "Chưa đặt" });
    const setBtn = h("button", { class: "btn small", type: "button", text: "Lưu", onclick: async () => {
      if (!input.value.trim()) { toast("Nhập giá trị trước."); return; }
      try {
        const res = await api(`/api/secrets/${s.key}`, { method: "PUT", body: { value: input.value } });
        input.value = "";
        badge.className = "pill ok";
        badge.textContent = "Đã đặt";
        banner.hidden = false;
        toast(res.message, "ok");
      } catch (err) { reportError(err); }
    } });
    return h("div", { class: "field stack" }, h("div", { class: "row" }, h("strong", { text: s.label }), badge, h("code", { class: "muted", text: s.key })),
      h("div", { class: "row" }, h("div", { style: "flex:1;min-width:200px" }, input), setBtn));
  });

  const remote = data.remote;
  const remoteNote = remote && remote.count
    ? h("div", { class: "banner" }, `Bot đang dùng ${remote.count} thông số do chủ hệ thống đặt trên web (bản ${remote.version}`,
      remote.fetched_at ? `, lấy lúc ${new Date(remote.fetched_at).toLocaleString("vi-VN")}` : "",
      "). Các ô có nhãn \"Web đang đặt\" lấy giá trị từ web; sửa trên trang Hệ thống của web.")
    : null;

  fill(main, 
    h("h1", { text: "Cài đặt" }),
    banner,
    remoteNote,
    zaloLoginCard(),
    ...[...groups].map(([name, fields]) => h("div", { class: "card stack" }, h("h2", { text: name }), ...fields)),
    h("div", { class: "row", style: "margin-bottom:1rem" }, h("button", { class: "btn primary", type: "button", text: "Lưu cài đặt", onclick: save })),
    h("div", { class: "card stack" }, h("h2", { text: "Khóa bí mật" }),
      h("p", { class: "muted small", text: "Giá trị hiện tại không bao giờ được hiển thị. Chỉ có thể đặt giá trị mới. ADMIN_TOKEN, cổng giao diện và thư mục dữ liệu chỉ sửa trực tiếp trong file userdata/config/settings.env." }),
      ...secrets));
}

// ---------- Tool ----------

async function renderTools(main) {
  const data = await api("/api/tools");
  fill(main, 
    h("h1", { text: "Tool của trợ lý" }),
    data.tools.length
      ? h("div", { class: "card" }, h("ul", {}, data.tools.map((t) => h("li", {}, h("code", { text: t.name }), ` · ${t.description}`))))
      : h("div", { class: "card" }, h("p", { class: "empty", text: "Chưa có tool nào. Sao chép src/bot/agent/tools/_example.py thành file mới (không có dấu _ ở đầu), sửa rồi khởi động lại bot." })));
}

const RENDERERS = {
  overview: renderOverview,
  servers: renderServers,
  groups: renderGroups,
  history: renderHistory,
  workspace: (main) => renderWorkspace(main, "SYSTEM"),
  playground: renderPlayground,
  logs: renderLogs,
  failed: renderFailed,
  settings: renderSettings,
  tools: renderTools,
};

// ---------- đăng nhập bằng Gmail ----------
// Web iforgotmywayhome làm chứng: mở link ở tab mới, đăng nhập Gmail và bấm Cho phép; trang này hỏi lại mỗi 2 giây.

let gmailTimer = null;

function gmailMessage(text, isError) {
  const el = document.getElementById("gmail-msg");
  el.hidden = !text;
  el.textContent = text || "";
  el.classList.toggle("error", Boolean(isError));
}

async function gmailLogin() {
  const button = document.getElementById("gmail-btn");
  clearInterval(gmailTimer);
  button.disabled = true;
  gmailMessage("Đang xin mã đăng nhập…");
  let started;
  try {
    started = await rawApi("/api/auth/gmail/start", { method: "POST" });
  } catch (err) {
    button.disabled = false;
    gmailMessage(err.message, true);
    return;
  }
  const tab = window.open(started.url, "_blank", "noopener");
  gmailMessage(tab ? "Đã mở web iforgotmywayhome ở tab mới. Đăng nhập Gmail và bấm Cho phép, trang này tự vào."
    : `Trình duyệt chặn tab mới. Mở link này, đăng nhập Gmail và bấm Cho phép: ${started.url}`);
  const deadline = Date.now() + (started.expiresIn || 600) * 1000;
  const finish = (message, isError) => { clearInterval(gmailTimer); button.disabled = false; gmailMessage(message, isError); };
  gmailTimer = setInterval(async () => {
    if (Date.now() > deadline) { finish("Hết thời gian chờ, bấm lại để thử lần nữa.", true); return; }
    let result;
    try { result = await rawApi("/api/auth/gmail/poll", { method: "POST", body: { code: started.code } }); } catch { return; }
    if (result.status === "ok") {
      clearInterval(gmailTimer);
      button.disabled = false;
      gmailMessage("");
      if (await tryLogin(result.token)) start();
    } else if (result.status === "denied") finish(result.message, true);
    else if (result.status === "expired") finish("Mã đã hết hạn, bấm lại để thử lần nữa.", true);
  }, 2000);
}

async function rawApi(path, { method = "GET", body } = {}) {
  const res = await fetch(path, { method, headers: body ? { "Content-Type": "application/json" } : {},
    body: body === undefined ? undefined : JSON.stringify(body) });
  let data = null;
  try { data = await res.json(); } catch { /* không phải JSON */ }
  if (!res.ok) throw new Error((data && (data.error || data.detail)) || `Lỗi HTTP ${res.status}`);
  return data;
}

async function setupGmailLogin() {
  document.getElementById("gmail-btn").addEventListener("click", gmailLogin);
  try {
    const options = await rawApi("/api/auth/options");
    document.getElementById("gmail-login").hidden = !options.gmail;
  } catch { /* không có thì chỉ dùng mã truy cập */ }
}

// ---------- khởi động ----------

async function boot() {
  setupGmailLogin();
  buildNav();
  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const value = document.getElementById("login-token").value.trim();
    if (value && await tryLogin(value)) start();
  });
  document.getElementById("logout").addEventListener("click", () => showLogin(""));
  for (const b of document.querySelectorAll("#target-switch button")) b.addEventListener("click", () => setTarget(b.dataset.target));
  state.target = storageGet(TARGET_KEY) === "vps" ? "vps" : "local";
  document.body.classList.toggle("target-vps", state.target === "vps");
  window.addEventListener("hashchange", () => { if (state.token) render(); });
  window.addEventListener("beforeunload", (e) => {
    if (state.dirty && state.dirty()) { e.preventDefault(); e.returnValue = ""; }
  });

  // Mã có thể được truyền qua #token=... (từ `python -m bot admin --open`); xóa khỏi thanh địa chỉ ngay.
  let token = storageGet(TOKEN_KEY);
  const match = location.hash.match(/token=([^&]+)/);
  if (match) {
    token = decodeURIComponent(match[1]);
    // Ứng dụng desktop có thể mở thẳng một trang, ví dụ Cài đặt ở lần chạy đầu: #token=...&page=settings
    const pageMatch = location.hash.match(/page=([a-z]+)/);
    const page = pageMatch && PAGES.some(([p]) => p === pageMatch[1]) ? pageMatch[1] : "overview";
    history.replaceState(null, "", location.pathname + `#/${page}`);
  }
  if (token && await tryLogin(token)) start();
  else if (!token) showLogin("");
}

let started = false;
function start() {
  if (started) { render(); return; }
  started = true;
  pollRemote().finally(() => { render(); pollStatus(); });
  setInterval(() => { if (state.token && !document.hidden) pollStatus(); }, 4000);
  setInterval(() => { if (state.token && !document.hidden) pollRemote(); }, 30000);
}

boot();
