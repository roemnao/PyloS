"""Chữ JavaScript / CSS / HTML chèn vào graph.html (chuyển từ PyloS region_map.py).

Các dấu @region@ / @Region@ được thay bằng từ cấp vùng của dự án (mặc định "vùng"; PyloS: "toà")."""

from __future__ import annotations

# ---- JavaScript: dữ liệu + hàm trợ giúp (chạy trước khi tạo nodesDS, chưa có `network`) ----
JS_DATA = r"""
const GREG_LAYOUT = __DATA__;
const GREG = {
  SHAPE: {function: 'dot', class: 'square', module: 'diamond', symbol: 'triangleDown', external: 'triangleDown',
          document: 'triangle', rationale: 'star', concept: 'hexagon'},
  KIND_NAME: {function: 'hàm / method', class: 'lớp', module: 'file / module', symbol: 'tên import, hằng, kiểu',
              external: 'thư viện ngoài', document: 'tài liệu', rationale: 'lời giải thích trong code', concept: 'khái niệm'},
  STRUCT: new Set(['contains', 'method', 'rationale_for']),
  KEY: 'greg-legend-show', OPEN_KEY: 'greg-legend-open',
  show: {same_file: false, struct: false, external: false, tests: false, outline: true},
  sel: null,  // cộng đồng đang sáng: {cid}
  light: () => document.documentElement.getAttribute('data-theme') === 'light',
  idx: id => GREG_LAYOUT.node[id] || [GREG_LAYOUT.regions.length - 1, 0],
  regionOf: id => GREG_LAYOUT.regions[GREG.idx(id)[0]],
  kindOf: id => GREG_LAYOUT.kinds[GREG.idx(id)[1]],
  regionLabel(id) { const r = GREG.regionOf(id); return r.name + ' (' + r.id + ')'; },
  kindLabel: id => GREG.KIND_NAME[GREG.kindOf(id)] || '',
  // độ sáng theo nền: nền tối giữ 50-72; nền sáng hạ về 38-54 (vàng/cam tối thiểu 45 để không thành nâu); xám nền sáng 40-62
  baseL(r) {
    if (!GREG.light()) return r.s === 0 ? r.l : Math.max(50, Math.min(72, r.l + 4));
    if (r.s === 0) return Math.max(40, Math.min(62, r.l));
    const warm = r.h >= 25 && r.h <= 60;
    return Math.max(warm ? 45 : 38, Math.min(54, r.l - 8));
  },
  hsl(r, dl = 0, a = 1) { const l = Math.max(8, Math.min(92, GREG.baseL(r) + dl)); return `hsla(${r.h},${r.s}%,${l}%,${a})`; },
  gray(a) { return GREG.light() ? `rgba(70,70,90,${a})` : `rgba(160,160,180,${a})`; },
  rawColors: null,
  ring(id) {  // viền đặc biệt của graphify (vòng "learning" xanh/vàng/xám): màu viền khác màu nền thì giữ
    if (!GREG.rawColors) { GREG.rawColors = {}; RAW_NODES.forEach(n => { const c = n.color || {}; if (c.border && c.border !== c.background) GREG.rawColors[n.id] = c.border; }); }
    return GREG.rawColors[id] || null;
  },
  nodeColor(id, alpha = 1) {
    const r = GREG.regionOf(id), ring = GREG.ring(id), border = ring || GREG.hsl(r, -15, alpha);
    return { background: GREG.hsl(r, 0, alpha), border: border,
             highlight: { background: GREG.hsl(r, 15), border: ring || (GREG.light() ? '#000000' : '#ffffff') },
             hover: { background: GREG.hsl(r, 10), border: border } };
  },
  nodeShape: id => GREG.SHAPE[GREG.kindOf(id)] || 'dot',
  edgeClass(e) {
    if (e.pc) return e.pc;
    const a = GREG_LAYOUT.node[e.from], b = GREG_LAYOUT.node[e.to];
    let c;
    if (GREG.STRUCT.has(e.label)) c = 'struct';
    else if (!a || !b) c = 'external';
    else {
      const ra = GREG_LAYOUT.regions[a[0]].id, rb = GREG_LAYOUT.regions[b[0]].id;
      if (ra === GREG_LAYOUT.external || rb === GREG_LAYOUT.external) c = 'external';
      else if (ra === GREG_LAYOUT.tests || rb === GREG_LAYOUT.tests) c = 'tests';
      else if (ra !== rb) c = 'cross';
      else c = GREG.file(e.from) === GREG.file(e.to) ? 'same_file' : 'same_building';
    }
    return (e.pc = c);
  },
  files: null,
  file(id) {
    if (!GREG.files) { GREG.files = {}; RAW_NODES.forEach(n => { GREG.files[n.id] = n.source_file || ''; }); }
    return GREG.files[id];
  },
  ALPHA: {cross: 0.30, same_building: 0.18, same_file: 0.12, struct: 0.10, external: 0.10, tests: 0.12},
  edgeWidth(e) { return GREG.edgeClass(e) === 'cross' ? 1.5 : 1; },
  edgeHidden(e) { const c = GREG.edgeClass(e); return c !== 'cross' && c !== 'same_building' && !GREG.show[c]; },
  edgeColor(e, alpha) {
    const c = GREG.edgeClass(e), a = alpha || GREG.ALPHA[c];
    const col = c === 'cross' ? GREG.hsl(GREG.regionOf(e.to), 0, a) : GREG.gray(a);
    const strong = c === 'cross' ? GREG.hsl(GREG.regionOf(e.to), 10, 0.9) : GREG.gray(0.8);
    return { color: col, highlight: strong, hover: strong, inherit: false };
  },
};
(function () {
  try {
    const saved = JSON.parse(localStorage.getItem(GREG.KEY) || 'null');
    if (saved) Object.keys(GREG.show).forEach(k => { if (typeof saved[k] === 'boolean') GREG.show[k] = saved[k]; });
  } catch (err) {}
})();
"""

# ---- JavaScript: vẽ, bấm, chú thích (chạy sau khi có `network`, trước phần Theme toggle) ----
JS_BEHAVIOR = r"""
(function () {
  const L = GREG_LAYOUT;
  const byId = {}; RAW_NODES.forEach(n => { byId[n.id] = n; });
  const members = {};  // cid -> [id]
  const origCid = {};  // cộng đồng gốc của graphify (RAW_NODES.community bị đổi cho nhóm lẻ bên dưới)
  RAW_NODES.forEach(n => { origCid[n.id] = n.community; (members[n.community] = members[n.community] || []).push(n.id); });
  const eachEdge = fn => RAW_EDGES.forEach((e, i) => fn(e, i));

  // ---- danh sách cộng đồng bên phải: xếp theo @region@ (thứ tự trên bản đồ), trong @region@ nhóm lớn trước ----
  LEGEND.forEach(c => {
    const here = {}; (members[c.cid] || []).forEach(id => { const k = GREG.idx(id)[0]; here[k] = (here[k] || 0) + 1; });
    const main = Object.keys(here).sort((a, b) => here[b] - here[a])[0];
    c.gregRegion = main === undefined ? L.regions.length : +main;
    if (main !== undefined && !c.gregTagged) { c.label = L.regions[main].name + ' · ' + c.label; c.gregTagged = true; }
  });
  LEGEND.sort((a, b) => (a.gregRegion - b.gregRegion) || (b.count - a.count) || (a.cid - b.cid));
  // cộng đồng dưới 3 nút gom thành một dòng "Nhóm lẻ" (ô tick và bấm sáng chạy cho cả nhóm)
  const SMALL = -1000, small = LEGEND.filter(c => (members[c.cid] || []).length < 3);
  if (small.length > 1) {
    members[SMALL] = [];
    small.forEach(c => (members[c.cid] || []).forEach(id => { members[SMALL].push(id); byId[id].community = SMALL; }));
    for (let k = LEGEND.length - 1; k >= 0; k--) if (small.includes(LEGEND[k])) LEGEND.splice(k, 1);
    LEGEND.push({ cid: SMALL, color: '#888888', label: 'Nhóm lẻ (' + small.length + ' cộng đồng 1–2 nút)', count: members[SMALL].length });
  }

  // ---- trạng thái hiển thị ----
  function paintAll(litNodes) {
    nodesDS.update(RAW_NODES.map(n => ({ id: n.id, color: GREG.nodeColor(n.id, litNodes && !litNodes.has(n.id) ? 0.15 : 1) })));
  }
  function reset() {
    GREG.sel = null;
    paintAll(null);
    const up = []; eachEdge((e, i) => up.push({ id: i, hidden: GREG.edgeHidden(e), color: GREG.edgeColor(e), width: GREG.edgeWidth(e) }));
    edgesDS.update(up);
    try { network.unselectAll(); } catch (err) {}
    network.redraw();
  }
  function light(litNodes, edgeTest, cid) {
    GREG.sel = cid == null ? null : { cid };
    paintAll(litNodes);
    const up = []; eachEdge((e, i) => { const on = edgeTest(e);
      up.push({ id: i, hidden: !on, color: on ? GREG.edgeColor(e, 0.8) : GREG.edgeColor(e), width: on ? 2 : GREG.edgeWidth(e) }); });
    edgesDS.update(up);
    network.redraw();
  }
  function lightNode(id) {
    const cid = origCid[id];
    light(new Set(members[cid]), e => e.from === id || e.to === id, cid);
  }
  function lightCommunity(cid) {
    const set = new Set(members[cid]);
    light(set, e => set.has(e.from) && set.has(e.to), cid);
  }
  function lightRegion(ri) {
    const ids = new Set(); RAW_NODES.forEach(n => { if (GREG.idx(n.id)[0] === ri) ids.add(n.id); });
    GREG.sel = null; paintAll(ids);
    const up = []; eachEdge((e, i) => {
      const inA = ids.has(e.from), inB = ids.has(e.to), on = inA !== inB && GREG.edgeClass(e) === 'cross';
      let col = GREG.edgeColor(e);
      if (on) { const other = GREG.regionOf(inA ? e.to : e.from); col = { color: GREG.hsl(other, 0, 0.8), highlight: GREG.hsl(other, 10, 1), hover: GREG.hsl(other, 10, 1), inherit: false }; }
      up.push({ id: i, hidden: !on, color: col, width: on ? 2 : GREG.edgeWidth(e) }); });
    edgesDS.update(up);
    network.redraw();
  }

  // ---- vẽ: vòng @region@, viền cộng đồng ----
  let hulls = null;
  function buildHulls() {
    const seen = {};
    hulls = L.groups.slice().sort((a, b) => b.nodes.length - a.nodes.length).map(g => {
      const pos = network.getPositions(g.nodes), pts = [];
      g.nodes.forEach(id => { const p = pos[id]; if (!p) return;
        [[-12, 0], [12, 0], [0, -12], [0, 12]].forEach(d => pts.push({ x: p.x + d[0], y: p.y + d[1] })); });
      if (pts.length < 3) return null;
      const hull = convexHull(pts);
      const rank = seen[g.region] = (seen[g.region] || 0) + 1;
      return { g, rank: rank - 1, hull, top: hull.reduce((m, p) => (p.y < m.y ? p : m), hull[0]) };
    }).filter(Boolean);
  }
  network.on('dragEnd', () => { hulls = null; });
  network.on('beforeDrawing', ctx => {
    const dark = !GREG.light();
    const scale = network.getScale();
    L.regions.forEach(r => {
      ctx.beginPath(); r.poly.forEach((q, k) => (k ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]))); ctx.closePath();
      ctx.fillStyle = GREG.hsl(r, 0, GREG.light() ? 0.12 : 0.15); ctx.fill();
      ctx.lineJoin = 'round'; ctx.lineWidth = 2; ctx.strokeStyle = GREG.hsl(r, 0, 0.65); ctx.stroke();
    });
    // nhãn vùng: cỡ chữ cố định trên màn hình (15px / 11px), vùng lớn vẽ trước, nhãn đè nhau thì bỏ dòng phụ rồi bỏ tên
    const placed = [];
    const free = b => !placed.some(p => b.x < p.x + p.w && p.x < b.x + b.w && b.y < p.y + p.h && p.y < b.y + b.h);
    const halo = dark ? 'rgba(12,12,22,0.9)' : 'rgba(255,255,255,0.9)';
    ctx.textAlign = 'center'; ctx.lineJoin = 'round';
    const text = (t, x, y, fs, bold) => {
      ctx.font = (bold ? 'bold ' : '') + fs + 'px sans-serif';
      ctx.lineWidth = fs / 4; ctx.strokeStyle = halo; ctx.strokeText(t, x, y);
      ctx.fillStyle = dark ? '#e8e8f0' : '#222'; ctx.fillText(t, x, y);
    };
    L.regions.slice().sort((a, b) => b.n - a.n).forEach(r => {
      const f1 = Math.min(15 / scale, 90), f2 = Math.min(11 / scale, 66);
      const sub = r.zoneName + ' · ' + r.n + ' nút';
      ctx.font = 'bold ' + f1 + 'px sans-serif'; const w1 = ctx.measureText(r.name).width;
      ctx.font = f2 + 'px sans-serif'; const w2 = ctx.measureText(sub).width;
      const yb = r.ly - f2 * 0.6;  // đường chân dòng phụ
      const subBox = { x: r.x - w2 / 2, y: yb - f2, w: w2, h: f2 * 1.2 };
      const nameBox = { x: r.x - w1 / 2, y: yb - f2 * 1.5 - f1, w: w1, h: f1 * 1.2 };
      const nameOnly = { x: nameBox.x, y: yb - f1, w: w1, h: f1 * 1.2 };
      if (free(nameBox) && free(subBox)) {
        placed.push(nameBox, subBox); text(r.name, r.x, yb - f2 * 1.5, f1, true); text(sub, r.x, yb, f2, false);
      } else if (free(nameOnly)) {
        placed.push(nameOnly); text(r.name, r.x, yb, f1, true);
      }
    });
    if (!GREG.show.outline) return;
    if (scale < 0.45 && !GREG.sel) return;
    if (!hulls) buildHulls();
    ctx.save(); ctx.lineJoin = 'round'; ctx.textAlign = 'center';
    const keep = scale < 0.7 ? 1 : scale < 1.2 ? 3 : 99;  // thu nhỏ: mỗi vùng chỉ ghi tên nhóm lớn nhất
    hulls.forEach(h => {
      const selected = GREG.sel && GREG.sel.cid === h.g.cid;
      if (scale < 0.45 && !selected) return;
      const r = L.regions[h.g.region];
      ctx.setLineDash([6, 5]); ctx.lineWidth = selected ? 2.5 : 1.5; ctx.strokeStyle = GREG.hsl(r, 25, selected ? 0.9 : 0.45);
      ctx.beginPath(); h.hull.forEach((p, k) => (k ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y))); ctx.closePath(); ctx.stroke();
      if (h.rank < keep || selected) {
        ctx.setLineDash([]);
        const name = h.g.name.length > 32 ? h.g.name.slice(0, 32) + '…' : h.g.name, fs = Math.min(12 / scale, 40);
        ctx.font = fs + 'px sans-serif'; ctx.lineWidth = fs / 4; ctx.strokeStyle = halo; ctx.strokeText(name, h.top.x, h.top.y - 5);
        ctx.fillStyle = dark ? 'rgba(210,210,230,0.95)' : 'rgba(30,30,50,0.95)'; ctx.fillText(name, h.top.x, h.top.y - 5);
      }
    });
    ctx.restore();
  });
  network.once('afterDrawing', () => network.fit());

  // ---- bấm ----
  network.on('click', params => {
    if (params.nodes.length) { lightNode(params.nodes[0]); return; }
    const p = params.pointer.canvas;
    const inside = r => { let c = false; const q = r.poly; for (let i = 0, j = q.length - 1; i < q.length; j = i++) { if ((q[i][1] > p.y) !== (q[j][1] > p.y) && p.x < (q[j][0] - q[i][0]) * (p.y - q[i][1]) / (q[j][1] - q[i][1]) + q[i][0]) c = !c; } return c; };
    const ri = L.regions.findIndex(inside);
    if (ri >= 0) { lightRegion(ri); return; }
    reset();
  });
  // bấm tên cộng đồng ở danh sách bên phải: sáng cộng đồng (ô tick vẫn ẩn/hiện như graphify)
  document.addEventListener('click', e => {
    const label = e.target.closest && e.target.closest('#legend .legend-label, #legend .legend-count');
    if (!label) return;
    const item = label.closest('.legend-item');
    const k = Array.prototype.indexOf.call(document.querySelectorAll('#legend .legend-item'), item);
    if (k < 0 || !LEGEND[k]) return;
    e.stopPropagation();
    lightCommunity(LEGEND[k].cid);
  }, true);

  // ---- nền sáng/tối ----
  new MutationObserver(() => { paintAll(null); const up = []; eachEdge((e, i) => up.push({ id: i, color: GREG.edgeColor(e) })); edgesDS.update(up); network.redraw(); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  // ---- nút ? và bảng chú thích ----
  const btn = document.getElementById('greg-legend-btn'), panel = document.getElementById('greg-legend');
  const svg = (inner) => `<svg width="14" height="14" viewBox="-7 -7 14 14"><g fill="var(--text-2)">${inner}</g></svg>`;
  const SHAPES = {
    function: svg('<circle r="5"/>'), class: svg('<rect x="-5" y="-5" width="10" height="10"/>'),
    module: svg('<polygon points="0,-6 6,0 0,6 -6,0"/>'), symbol: svg('<polygon points="-6,-5 6,-5 0,6"/>'),
    document: svg('<polygon points="0,-6 6,5 -6,5"/>'),
    rationale: svg('<polygon points="0,-6.5 1.8,-2 6.5,-2 2.8,1 4.2,5.8 0,3 -4.2,5.8 -2.8,1 -6.5,-2 -1.8,-2"/>'),
    concept: svg('<polygon points="-3,-5.2 3,-5.2 6,0 3,5.2 -3,5.2 -6,0"/>'),
  };
  const line = (css, dash) => `<svg width="26" height="10"><line x1="1" y1="5" x2="19" y2="5" stroke="${css}" stroke-width="2" ${dash ? 'stroke-dasharray="4 3"' : ''}/><polygon points="19,1 25,5 19,9" fill="${css}"/></svg>`;
  function legendHtml() {
    const zones = []; L.regions.forEach(r => { if (!zones.includes(r.zone)) zones.push(r.zone); });
    const swatch = r => `<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:${GREG.hsl(r)}"></span>`;
    let h = '<h4>Màu = @region@</h4>';
    zones.forEach(z => {
      h += `<div><b>${esc(L.regions.find(r => r.zone === z).zoneName)}</b></div>`;
      L.regions.filter(r => r.zone === z).forEach(r => {
        h += `<div class="row">${swatch(r)}<span>${esc(r.name)} <span style="opacity:.6">${esc(r.id)} · ${r.n}</span></span></div>`;
      });
    });
    h += '<h4>Hình = loại code</h4>';
    L.kinds.forEach(k => { h += `<div class="row">${SHAPES[k] || SHAPES.symbol}<span>${esc(GREG.KIND_NAME[k])}</span></div>`; });
    h += '<div style="opacity:.7">Kích thước nút = số liên kết của nút (graphify tính).</div>';
    h += '<h4>Viền nét đứt = cộng đồng</h4><div>Nhóm hàm hay đi cùng nhau do graphify tự chia theo liên kết; một cộng đồng có thể trải qua nhiều @region@. Phóng to để thấy viền và tên.</div>';
    const dispatch = L.regions.find(r => r.id === L.hub) || L.regions[0];
    h += '<h4>Đường nối</h4><div>Một đường = nút này gọi, import hoặc nhắc tới nút kia. Mũi tên chỉ về phía <b>được gọi</b>.</div>';
    h += '<div style="margin-top:6px"><b>Màu đường: đi đâu</b></div>';
    h += `<div class="row">${line(GREG.hsl(dispatch, 0, 0.9))}<span>có màu: <b>sang @region@ khác</b>. Màu là màu của @region@ ở đầu mũi tên (ví dụ: ô màu này là đi vào ${esc(dispatch.name)})</span></div>`;
    h += `<div class="row">${line(GREG.gray(0.6))}<span>xám: giữa hai file <b>trong cùng một @region@</b></span></div>`;
    h += '<div style="margin-top:6px"><b>Kiểu nét: chắc tới đâu</b></div>';
    h += `<div class="row">${line(GREG.gray(0.8))}<span>nét liền: graphify <b>thấy thẳng trong code</b> (lệnh gọi, import có thật)</span></div>`;
    h += `<div class="row">${line(GREG.gray(0.8), true)}<span>nét đứt: graphify <b>đoán ra</b>, không thấy trực tiếp trong code (ví dụ gọi gián tiếp). Nên kiểm lại trước khi tin</span></div>`;
    h += '<h4>Bật / tắt</h4>';
    [['same_file', 'đường trong cùng file'], ['struct', 'đường cấu trúc (chứa, method, giải thích)'], ['external', 'đường tới thư viện ngoài'],
     ['tests', 'đường của test'], ['outline', 'viền cộng đồng']].forEach(([k, t]) => {
      h += `<label class="row"><input type="checkbox" data-greg-show="${k}" ${GREG.show[k] ? 'checked' : ''}> ${t}</label>`;
    });
    h += '<h4>Thao tác</h4><div>Bấm nút: sáng cả cộng đồng · bấm vòng @region@: sáng @region@ và đường ra/vào · Esc hoặc bấm chỗ trống: bỏ chọn · lăn chuột: phóng to.</div>';
    return h;
  }
  function setOpen(open) {
    panel.hidden = !open; btn.setAttribute('aria-expanded', String(open));
    if (open) panel.innerHTML = legendHtml();
    try { localStorage.setItem(GREG.OPEN_KEY, open ? '1' : '0'); } catch (err) {}
  }
  btn.addEventListener('click', () => setOpen(panel.hidden));
  panel.addEventListener('change', e => {
    const k = e.target.getAttribute && e.target.getAttribute('data-greg-show');
    if (!k) return;
    GREG.show[k] = e.target.checked;
    try { localStorage.setItem(GREG.KEY, JSON.stringify(GREG.show)); } catch (err) {}
    hulls = null; reset();
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    if (!panel.hidden) setOpen(false); else reset();
  });
  try { if (localStorage.getItem(GREG.OPEN_KEY) === '1') setOpen(true); } catch (err) {}
})();
"""

CSS = r"""
#greg-legend-btn { position: fixed; top: 10px; left: 10px; z-index: 10; width: 26px; height: 26px; border-radius: 50%;
  border: 1px solid var(--input-border); background: var(--panel); color: var(--text-2); font: bold 13px sans-serif;
  cursor: pointer; opacity: .85; padding: 0; }
#greg-legend-btn:hover, #greg-legend-btn[aria-expanded="true"] { color: var(--text); opacity: 1; }
#greg-legend { position: fixed; top: 44px; left: 10px; z-index: 10; width: 300px; max-height: calc(100vh - 60px);
  overflow-y: auto; padding: 12px 14px; background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
  color: var(--text-3); font-size: 12px; line-height: 1.5; box-shadow: 0 6px 24px rgba(0,0,0,.35); }
#greg-legend[hidden] { display: none; }
#greg-legend h4 { font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-2); margin: 10px 0 6px; }
#greg-legend .row { display: flex; align-items: center; gap: 8px; padding: 2px 0; }
#greg-legend svg { flex-shrink: 0; }
@media (max-width: 700px) { #greg-legend { width: calc(100vw - 20px); } }
"""

HTML = """<button id="greg-legend-btn" type="button" aria-expanded="false" aria-controls="greg-legend"
        title="Chú thích: màu, hình, viền, đường">?</button>
<div id="greg-legend" role="dialog" aria-label="Chú thích bản đồ" hidden></div>"""


def fill(text: str, levels: dict) -> str:
    word = str(levels.get("region") or "vùng")
    return text.replace("@region@", word.lower()).replace("@Region@", word[:1].upper() + word[1:])
