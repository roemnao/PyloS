# Bản đồ vùng — hướng dẫn sửa lại cho dễ đọc

> Bản hướng dẫn làm một lần từ đầu đến cuối, không cần hỏi lại owner giữa chừng.
> Phạm vi: `src/pylos/lobby/atlas/generator/region_map.py` (code vá file HTML) và phần JavaScript/CSS nó chèn vào
> `graphify-out/graph.html` (file graphify sinh ra). **Không sửa mã nguồn của skill graphify** (gói `graphifyy` trong uv):
> nâng cấp graphify sẽ xoá mọi chỉnh sửa trong đó. Mọi thay đổi đi qua bước "vá" của `region_map.py`.
> Ngày viết: 2026-11-05. Số liệu lấy từ `graphify-out/graph.json` lúc viết (1984 nút, 4562 cạnh, 179 cộng đồng).

---

## 0. Luật đã chốt

| Kênh nhìn | Mang ý nghĩa | Ghi chú |
|---|---|---|
| **Vị trí** | nút nằm trong vòng tròn của **toà** nó thuộc; trong toà, mỗi **file** là một cụm tròn; các file **chung cộng đồng** đứng cạnh nhau; trong một cụm, nút cùng cộng đồng nằm liền nhau | không gộp nút, không làm nhiều tầng |
| **Màu nút** | **khu/toà** (mỗi khu một họ màu, mỗi toà một sắc độ) | thay cho màu cộng đồng của graphify |
| **Hình nút** | **loại code**: hàm, lớp, file, tên import, tài liệu, lời giải thích, khái niệm | **kích thước nút giữ nguyên** như graphify tính |
| **Cộng đồng** | **viền nét đứt** bao các nút cùng cộng đồng trong một toà + tên nhóm; bấm một nút thì cả cộng đồng sáng lên trên toàn bản đồ | không dùng màu, không dùng hình |
| **Đường nối** | mặc định **mờ, xám**; đường đi **sang toà khác** đậm hơn một chút, nhuốm màu toà đích; bấm nút/toà thì đường của nó sáng hẳn | đường cấu trúc, đường tới thư viện ngoài, đường của test **ẩn mặc định**, bật lại được |
| **Nét đứt của đường** | giữ nghĩa của graphify: quan hệ graphify **suy đoán** (INFERRED), nét liền là **đọc thẳng từ code** (EXTRACTED) | |
| **Nút chú thích** | nút nhỏ góc **trên bên trái** bản đồ, bấm mở bảng giải thích màu, hình, viền, đường và thao tác | |

---

## 1. Hiện trạng (đọc trước khi sửa)

### 1.1 Hai file liên quan

- `region_map.py` (bản trong cây làm việc, chưa commit) **vá thẳng** `graphify-out/graph.html`:
  chèn khối `PYLOS_LAYOUT` (vị trí nút + vòng toà), tắt vật lý, vẽ vòng tròn toà trong `beforeDrawing`.
  Mọi đoạn chèn nằm giữa `/* pylos-layout:begin */` và `/* pylos-layout:end */`; hàm `unpatch()` gỡ ra được, chạy lại không chồng (idempotent).
- Bản đã commit (`2fd1dec`) lại sinh trang riêng `graphify-out/pylos_map.html` từ mẫu `region_map.html` (mẫu này đang bị xoá trong cây làm việc).
  `CLAUDE.md` vẫn ghi `pylos_map.html`. **Bước 2.2 chốt một cách**: hướng dẫn này theo cách "vá `graph.html`".

### 1.2 Vì sao bản đồ hiện tại rối

| Nguyên nhân | Chỗ trong `graph.html` |
|---|---|
| Màu nút = màu cộng đồng, chỉ 10 màu cho 179 cộng đồng, dùng lặp | `RAW_NODES[i].color` do graphify tính |
| Màu đường **kế thừa màu nút nguồn** (vis-network mặc định `color.inherit = 'from'`), nên 4562 đường thành cầu vồng | `edgesDS`: `color: e.color` chỉ có `{opacity: 0.7}` |
| Mọi loại đường vẽ như nhau | 1527 đường cấu trúc (`contains`, `method`, `rationale_for`), 826 đường trong cùng một file, 764 đường tới thư viện ngoài, 490 đường của test. Chỉ **652** đường thật sự đi giữa hai toà, và 303 đường giữa hai file cùng toà |
| Cụm "Thư viện ngoài" nhận đường từ khắp nơi; toà cách xa nên các đường dài chạy song song, dính thành chùm | vị trí toà trong `REGIONS` + `gap` của `plan_regions` |
| Trong toà, các cụm file xếp theo **kích thước**, không theo quan hệ | `pack_region()`: sắp file theo số nút, xoắn ốc từ tâm ra |

### 1.3 Cấu trúc `graph.html` của graphify (mẫu hiện tại, vis-network 9.1.6)

Các mốc dùng để vá (tìm đúng chuỗi, không tìm theo số dòng):

| Mốc | Dùng để |
|---|---|
| `</style>` | chèn CSS của nút chú thích |
| `<div id="graph"></div>` | chèn nút + bảng chú thích ngay sau |
| `const nodesDS = new vis.DataSet(` | chèn khối dữ liệu `PYLOS_LAYOUT` ngay trước |
| `  id: n.id, label: n.label, color: n.color, size: n.size,` | thay màu + thêm hình cho nút (giữ `size: n.size`) |
| `  color: e.color,` (trong `edgesDS`) | thay màu đường, thêm `hidden` |
| `  physics: {\n    enabled: true,` | tắt vật lý (đã có) |
| `// Theme toggle` | chèn phần vẽ vòng, viền cộng đồng, xử lý bấm |
| `html += \`<div class="field">Community: ` | thêm dòng "Toà", "Loại" vào khung thông tin nút |
| `<div class="legend-dot" style="background:${c.color}">` | đổi chấm màu trong danh sách cộng đồng bên phải |

Dữ liệu sẵn có trong từng nút `RAW_NODES`: `id, label, color, size, font, title, community, community_name, source_file, file_type, degree`.
Trong `graph.json` có thêm: `_callable`, `_callable_class`, `type` (`external`, `package`), `node_kind` (`heading`, `page`).

---

## 2. Chuẩn bị

### 2.1 Trả khoảng cách về như cũ

Lượt trước đã nới bốn con số trong `region_map.py` (chưa commit). Đặt lại đúng bản gốc trước, rồi bước A4 mới chỉnh:

| Chỗ | Đang là | Đặt lại |
|---|---|---|
| `plan_regions(..., gap=...)` | `200.0` | `90.0` |
| `scale = max(radius.values()) * ...` | `1.35` | `1.05` |
| `blobs = [(... * math.sqrt(len(f)) + ...)` | `15.0`, `16.0` | `9.0`, `10.0` |
| khoảng cách giữa hai cụm `rf + blobs[j] + ...` | `16.0` | `6.0` |

### 2.2 Chốt file đầu ra

- Giữ cách **vá `graphify-out/graph.html`** (bản trong cây làm việc).
- Sửa dòng trong `CLAUDE.md`: `python -m pylos.lobby.atlas.generator.region_map — ... written to graphify-out/pylos_map.html` → `... patches graphify-out/graph.html`.
- Xác nhận `region_map.html` (mẫu cũ) bị xoá hẳn và gỡ khỏi `atlas_map.toml` nếu có dòng riêng cho nó.

### 2.3 Tự vá lại sau mỗi lần graphify dựng lại

Hook `post-commit` của graphify ghi đè `graph.html` mới tinh, nên phần vá mất sau mỗi commit.
Thêm vào **cuối** `.git/hooks/post-commit`, sau đoạn `# graphify-hook-end` (hook nằm trên máy, không vào git):

```sh
# pylos: xếp lại bản đồ theo khu/toà sau khi graphify dựng lại graph.html
[ "${GRAPHIFY_SKIP_HOOK:-0}" = "1" ] || .venv/Scripts/python.exe -m pylos.lobby.atlas.generator.region_map >/dev/null 2>&1 || true
```

Ghi chú: hook graphify chạy nền. Nếu dòng trên chạy trước khi graphify ghi xong `graph.html`, phần vá bị ghi đè.
Cách chắc: cho `region_map` so `graph.html` mtime với `graph.json`, đợi tối đa 60 giây cho tới khi `graph.html` mới hơn, rồi mới vá.

---

## 3. Phần A — sửa code Python (`region_map.py`)

Python chỉ **tính và đưa dữ liệu** vào `PYLOS_LAYOUT`. Mọi quyết định "vẽ thế nào" nằm ở JavaScript (Phần B), để đổi giao diện không phải tính lại vị trí.

### A1. Bảng màu theo toà

Thêm cột màu vào `REGIONS` (`hue`, `sat`, `light`); vòng tròn toà dùng **đúng màu này** (bỏ `ZONE_HUE` cho vòng).

| Vùng | Màu (HSL, nền tối) | Ý |
|---|---|---|
| `management/owner` | 265, 55%, 64% | Khu quản lý: tím |
| `management/managers` | 290, 50%, 68% | |
| `gate/main_gate` | 205, 70%, 56% | Khu cổng: xanh dương |
| `gate/side_gate` | 225, 60%, 64% | |
| `gate/fence` | 188, 65%, 48% | |
| `gate/guest_house` | 240, 45%, 72% | |
| `lobby/dispatch` | 36, 90%, 56% | Khu đại sảnh: vàng cam |
| `lobby/office` | 18, 80%, 60% | |
| `lobby/atlas` | 70, 70%, 46% | |
| `lobby/library` | 96, 50%, 48% | |
| `residential/residents` | 150, 55%, 50% | Khu dân cư: xanh lá |
| `outside/entry` | 330, 50%, 62% | Lối vào bot (file chưa xếp chỗ): hồng, để thấy ngay |
| `outside/tests` | 0, 0%, 66% | Ngoài Thành: xám |
| `outside/repo_root` | 0, 0%, 55% | |
| `outside/tooling` | 0, 0%, 44% | |
| `outside/external` | 0, 0%, 33% | thư viện ngoài: xám đậm nhất |

Nền sáng: giảm `light` 12 điểm (làm ở JS, xem B8).
Kiểm tra: hai toà cùng khu phải khác nhau rõ (hue cách ≥ 15 hoặc light cách ≥ 8).

### A2. Loại nút → hình dạng

Viết hàm `kind_of(node) -> str`, đọc từ `graph.json` (không đọc từ `RAW_NODES` vì thiếu trường):

| Loại | Điều kiện (theo thứ tự) | Hình vis-network | Số nút lúc viết |
|---|---|---|---|
| `external` | `node.type == "external"` hoặc không có `source_file` | `triangleDown` | 80 |
| `class` | `_callable_class` | `square` | 81 |
| `function` | `_callable` (hàm, method) | `dot` | 1037 |
| `module` | `file_type == "code"` và nhãn kết thúc `.py`/`.js` hoặc `type == "package"` | `diamond` | 148 |
| `symbol` | `file_type == "code"` còn lại (tên import, hằng, kiểu: `Path`, `Any`…) | `triangleDown` | 154 |
| `document` | `file_type == "document"` (tiêu đề, trang tài liệu) | `triangle` | 186 |
| `rationale` | `file_type == "rationale"` (docstring/lời giải thích gắn vào code) | `star` | 277 |
| `concept` | `file_type == "concept"` (khái niệm graphify rút ra từ tài liệu) | `hexagon` | 101 |

- `kind` không bao giờ thay đổi giữa các lần dựng lại, khác với cộng đồng.
- **Kích thước giữ nguyên `n.size`** của graphify. Với cùng `size`, tam giác và sao trông nhỏ hơn chấm tròn một chút: chấp nhận, không bù.

### A3. Xếp trong toà: file chung cộng đồng đứng cạnh nhau

Sửa `pack_region(files, degree)` thành `pack_region(files, degree, community)`:

1. **Thứ tự các cụm file** (thay cho "to trước, nhỏ sau"):
   - Mỗi file có `C(f)` = đếm số nút theo cộng đồng.
   - Độ gần hai file: `affinity(a, b) = Σ_c min(C(a)[c], C(b)[c])` (số nút "chung cộng đồng").
   - Bắt đầu bằng file nhiều nút nhất. Lần lượt chọn file chưa đặt có `affinity` lớn nhất với **hai file vừa đặt gần nhất**; hoà thì chọn file nhiều nút hơn; mọi `affinity = 0` thì lấy file nhiều nút nhất còn lại.
   - Đặt theo thứ tự đó lên vòng xoắn như hiện nay (vòng xoắn đặt file kế tiếp sát file trước, nên file chung cộng đồng nằm cạnh nhau).
2. **Trong một cụm file**, chia hình tròn thành **các múi** theo cộng đồng (múi rộng tỉ lệ số nút), cộng đồng lớn nhất trước:
   - Nút của một cộng đồng chỉ nằm trong múi của nó; trong múi, nút nối nhiều nhất gần tâm.
   - Vị trí: góc = giữa múi ± độ lệch đều; bán kính = `rf * sqrt((k + 0.5) / n_múi)`.
   - Cụm chỉ có một cộng đồng thì giữ cách cũ (xoắn hoa hướng dương, nút nối nhiều ở giữa).
3. Bán kính cụm giữ công thức cũ `9 * sqrt(n) + 10` (bước 2.1): không giãn thêm.
4. Thứ tự phải **ổn định**: khi hoà, so theo `source_file` rồi `id`, để chạy hai lần ra cùng một bố cục.

### A4. Vị trí toà theo luồng chạy và khoảng cách

Vị trí tương đối mới trong `REGIONS`, xếp theo đường đi của một tin nhắn (trái → phải):
`Zalo → main_gate → fence → dispatch → residents`, quản lý ở trên, ngoài Thành ở dưới.

| Vùng | Vị trí mới (x, y) | Lý do |
|---|---|---|
| `gate/main_gate` | (-3.0, -0.6) | cửa vào, bên trái |
| `gate/fence` | (-1.5, -0.1) | **giữa** cổng chính và điều phối (tin đi qua hàng rào) |
| `gate/side_gate` | (-2.9, 1.5) | dưới cổng chính, gần điều phối |
| `gate/guest_house` | (-3.6, 2.9) | cạnh cổng |
| `lobby/dispatch` | (0.0, 0.0) | tâm |
| `lobby/office` | (1.6, -1.3) | cạnh điều phối, phía dân cư |
| `lobby/library` | (1.4, 1.6) | |
| `lobby/atlas` | (-0.2, 2.2) | |
| `residential/residents` | (3.3, 0.0) | cuối đường đi, bên phải |
| `management/owner` | (-1.2, -2.4) | trên |
| `management/managers` | (1.2, -2.4) | trên |
| `outside/entry` | (3.4, 1.9) | cạnh dân cư (lối vào gọi bot) |
| `outside/tests` | (-1.6, 4.2) | dưới |
| `outside/repo_root` | (0.6, 4.2) | dưới |
| `outside/tooling` | (2.2, 4.2) | dưới |
| `outside/external` | (4.6, 3.8) | **góc xa nhất**, vì đường tới nó ẩn mặc định |

- `plan_regions(gap=60.0)`, `scale = max(radius) * 1.0`: các khu gần nhau hơn bản gốc (gap 90).
- `plan_regions` vẫn đẩy các vòng ra cho tới khi không chồng nhau, nên toạ độ trên chỉ là điểm xuất phát.

### A5. Dữ liệu cộng đồng cho viền nét đứt

Tính sẵn danh sách nhóm để JS vẽ viền:

```python
groups = [{"region": rid, "cid": cid, "name": community_name, "nodes": [node_id, ...]}
          for (rid, cid), ids in by_region_community.items() if len(ids) >= 3]
```

- Chỉ nhóm **≥ 3 nút trong cùng một toà** (nhóm 1–2 nút không vẽ viền, vẫn sáng khi bấm).
- Bỏ vùng `outside/external` (86 cộng đồng lẻ tẻ, vẽ viền chỉ thêm rối).
- Tên nhóm: `community_name` của graphify. Nếu tên có dạng `Community N`, thay bằng nhãn của nút có `degree` lớn nhất trong nhóm, để tooltip luôn có chữ.

### A6. Cấu trúc `PYLOS_LAYOUT` mới

```js
PYLOS_LAYOUT = {
  regions: [{id, name, zone, zoneName, h, s, l, x, y, r, n}, ...],   // vòng toà, màu theo A1
  pos:     {nodeId: [x, y], ...},                                     // như hiện nay
  node:    {nodeId: [regionIndex, kindCode], ...},                    // toà + loại của từng nút
  kinds:   ["function","class","module","symbol","external","document","rationale","concept"],
  groups:  [{region, cid, name, nodes: [...]}, ...],                  // A5
}
```

Giữ JSON gọn (`separators=(",", ":")`, chỉ số thay cho chuỗi lặp). Dữ liệu hiện ~1984 nút: thêm khoảng 60–80 KB, chấp nhận được.

### A7. Dữ liệu cho bot (không đụng hình)

Bot không xem hình, chỉ đọc dữ liệu. Ghi thêm `graphify-out/pylos_nodes.json` cùng lúc vá:

```json
{"built_at_commit": "...", "nodes": {"<id>": {"district": "gate/fence", "region": "gate/fence", "kind": "function",
                                           "community": 12, "community_name": "rate_limiter.py"}}}
```

- Lệnh `atlas region <toà>` (`src/pylos/lobby/atlas/generator/atlas.py`) thêm mục **"Communities in this region"**: mỗi cộng đồng có bao nhiêu nút ở đây, và có nút ở toà nào khác. Đọc `graph.json` trực tiếp, không cần `pylos_nodes.json`.
- Cộng đồng trải ≥ 3 toà (lúc viết: 44/179) in thêm dòng `spans N buildings` để bot thấy ranh giới đang cắt ngang chức năng.

### A8. Vá HTML: các điểm chèn

Giữ quy ước hiện có. Mọi đoạn chèn bọc trong `BEGIN`/`END`; mọi chuỗi thay thế có bản "đã vá" riêng để `unpatch()` trả về được:

| Điểm | Thay/chèn | `unpatch()` |
|---|---|---|
| `</style>` | chèn CSS (B6) **trước** nó, bọc `/* pylos-layout:begin */ ... end */` | xoá khối |
| `<div id="graph"></div>` | thêm HTML nút + bảng chú thích **sau** nó, bọc `<!-- pylos-layout:begin -->`/`<!-- ...end -->` | xoá khối (thêm cặp mốc HTML vào `unpatch`) |
| `const nodesDS = new vis.DataSet(` | chèn `PYLOS_LAYOUT` + hàm trợ giúp **trước** nó (như nay) | như nay |
| dòng `id: n.id, label: n.label, color: n.color, size: n.size,` | thay `color: n.color` bằng `color: PYLOS.nodeColor(n.id), shape: PYLOS.nodeShape(n.id),` (giữ `size: n.size`) | đổi ngược chuỗi |
| dòng `x: 30 * Math.sqrt(i)...` | như nay (vị trí cố định) | như nay |
| `  color: e.color,` trong `edgesDS` | thay bằng `  color: PYLOS.edgeColor(e), hidden: PYLOS.edgeHidden(e), pylosClass: PYLOS.edgeClass(e),` | đổi ngược |
| `physics enabled: true` | như nay | như nay |
| `// Theme toggle` | chèn vẽ vòng + viền + xử lý bấm (B3–B7) **trước** nó | như nay |
| `html += \`<div class="field">Community: ` | chèn trước nó hai dòng "Toà", "Loại" | đổi ngược |
| `<div class="legend-dot" style="background:${c.color}"></div>` | `style="background:transparent;border:1.5px dashed var(--text-2)"` (chấm cộng đồng thành vòng nét đứt, khớp viền trên bản đồ) | đổi ngược |

Nếu **thiếu bất kỳ mốc nào**: dừng với lỗi rõ ràng ("graphify đổi mẫu graph.html, mốc X không còn") và **không ghi file**. Không vá một nửa.

---

## 4. Phần B — phần JavaScript/CSS chèn vào `graph.html`

Tất cả đặt trong một đối tượng `PYLOS` (khai báo cùng `PYLOS_LAYOUT`), không tạo biến toàn cục rải rác.

### B1. Màu và hình nút

```js
const PYLOS = {
  light: () => document.documentElement.getAttribute('data-theme') === 'light',
  regionOf: id => PYLOS_LAYOUT.regions[(PYLOS_LAYOUT.node[id] || [0])[0]],
  kindOf: id => PYLOS_LAYOUT.kinds[(PYLOS_LAYOUT.node[id] || [0, 0])[1]],
  hsl(r, dl = 0, a = 1) { const l = r.l - (PYLOS.light() ? 12 : 0) + dl; return `hsla(${r.h},${r.s}%,${l}%,${a})`; },
  SHAPE: {function:'dot', class:'square', module:'diamond', symbol:'triangleDown', external:'triangleDown',
          document:'triangle', rationale:'star', concept:'hexagon'},
  nodeColor(id) { const r = PYLOS.regionOf(id);
    return { background: PYLOS.hsl(r), border: PYLOS.hsl(r, -15),
             highlight: { background: PYLOS.hsl(r, 15), border: '#ffffff' },
             hover:     { background: PYLOS.hsl(r, 10), border: PYLOS.hsl(r, -15) } }; },
  nodeShape: id => PYLOS.SHAPE[PYLOS.kindOf(id)] || 'dot',
};
```

- **Không đổi `size`**. Không đặt `shape` trong `options.nodes` (giữ `shape: 'dot'` làm mặc định của graphify).
- `searchResults` của graphify tô viền theo `n.color.background` của `RAW_NODES` (màu cũ): đổi thành `nodesDS.get(n.id).color.background` ở bước vá (một chỗ duy nhất trong ô tìm kiếm).

### B2. Đường nối: phân loại và màu

```js
STRUCT: new Set(['contains', 'method', 'rationale_for']),
edgeClass(e) {
  const a = PYLOS_LAYOUT.node[e.from], b = PYLOS_LAYOUT.node[e.to];
  if (PYLOS.STRUCT.has(e.label)) return 'struct';
  if (!a || !b) return 'external';
  const ra = PYLOS_LAYOUT.regions[a[0]].id, rb = PYLOS_LAYOUT.regions[b[0]].id;
  if (ra === 'outside/external' || rb === 'outside/external') return 'external';
  if (ra === 'outside/tests' || rb === 'outside/tests') return 'tests';
  if (ra !== rb) return 'cross';
  return RAW_FILE[e.from] === RAW_FILE[e.to] ? 'same_file' : 'same_building';
},
```

`RAW_FILE` là bảng `id → source_file` dựng một lần từ `RAW_NODES`.

| Lớp | Số lúc viết | Mặc định | Kiểu vẽ |
|---|---|---|---|
| `cross` (sang toà khác) | 652 | **hiện** | màu toà **đích**, độ trong 0.30, rộng 1.5 |
| `same_building` (khác file, cùng toà) | 303 | **hiện** | xám, độ trong 0.18, rộng 1 |
| `same_file` | 826 | ẩn | xám, 0.12 |
| `struct` (`contains`, `method`, `rationale_for`) | 1527 | ẩn | xám, 0.10 |
| `external` (tới thư viện ngoài) | 764 | ẩn | xám, 0.10 |
| `tests` | 490 | ẩn | xám, 0.12 |

- Mọi màu đường đặt `inherit: false` (bỏ việc kế thừa màu nút nguồn, đây là nguồn gốc "cầu vồng").
- Giữ `dashes: e.dashes` và `width` của graphify cho đường được chọn; với đường thường dùng độ rộng ở bảng trên.
- Mặc định hiện ~955 đường thay cho 4562.

### B3. Vòng toà

Trong `beforeDrawing` hiện có: đổi `hsla(r.hue, 60%, ...)` thành `PYLOS.hsl(r, 0, 0.10)` cho nền và `PYLOS.hsl(r, 0, 0.65)` cho viền. Chữ tên toà giữ cỡ như cũ.
Dòng phụ dưới tên: `zoneName · n nút` (như nay).

### B4. Viền cộng đồng

Vẽ trong `beforeDrawing`, **sau** vòng toà, **dưới** nút:

1. Với mỗi `group` trong `PYLOS_LAYOUT.groups`: lấy vị trí hiện tại `network.getPositions(group.nodes)` (người dùng kéo nút thì viền đi theo).
2. Bao lồi bằng hàm `convexHull` **có sẵn** trong `graph.html` (graphify dùng cho hyperedges), nới ra 12px quanh mỗi điểm (thêm 4 điểm phụ ±12 cho mỗi nút trước khi bao, để viền không cắt qua tâm nút).
3. Nét: `setLineDash([6, 5])`, rộng 1.5, màu `PYLOS.hsl(region, 25, 0.45)`, **không tô nền**.
4. Tên nhóm ở mép trên viền, chữ 11px, màu `var(--text-2)`.
5. Chỉ vẽ khi `network.getScale() >= 0.45` (đủ gần để đọc) **hoặc** nhóm đang được chọn; nhóm đang chọn: nét đậm 2.5, độ trong 0.9.
6. Bật/tắt bằng ô "Viền cộng đồng" trong bảng chú thích.

### B5. Bấm để làm sáng

| Thao tác | Kết quả |
|---|---|
| Bấm **một nút** | sáng: mọi nút **cùng cộng đồng** (mọi toà) + mọi đường của nút đó (kể cả lớp đang ẩn, hiện tạm); các nút khác `opacity: 0.15`, các đường khác ẩn tạm. Khung thông tin bên phải như graphify, thêm dòng Toà/Loại |
| Bấm **vào vòng toà** (chỗ không có nút) | sáng: mọi nút của toà + mọi đường `cross` vào/ra toà (tô màu toà đầu kia, độ trong 0.8) |
| Bấm **chỗ trống** ngoài mọi vòng, hoặc phím **Esc** | về mặc định |
| Bấm **tên cộng đồng** trong danh sách bên phải | như bấm một nút của cộng đồng đó (giữ ô tick ẩn/hiện của graphify) |

Cách làm:
- Dùng `network.on('click', params => ...)` **thêm vào**, không xoá handler của graphify. `params.nodes[0]` có giá trị là bấm nút; không có thì dùng `params.pointer.canvas` để tìm vòng toà chứa điểm bấm (khoảng cách tới tâm < `r`).
- Đổi trạng thái bằng **một lần** `nodesDS.update([...])` và **một lần** `edgesDS.update([...])` (gom mảng, không gọi từng phần tử): 1984 nút + 4562 đường cập nhật trong < 100 ms.
- Lưu trạng thái gốc của đường (`hidden`, `color`) trong `Map` lúc khởi tạo để trả về chính xác.
- Dùng thuộc tính `opacity` của nút (vis-network ≥ 9.0 có). Không đổi `size`.

### B6. Nút chú thích góc trên bên trái

HTML chèn sau `<div id="graph"></div>`:

```html
<!-- pylos-layout:begin -->
<button id="pylos-legend-btn" type="button" aria-expanded="false" aria-controls="pylos-legend"
        title="Chú thích: màu, hình, viền, đường">?</button>
<div id="pylos-legend" role="dialog" aria-label="Chú thích bản đồ" hidden> ... </div>
<!-- pylos-layout:end -->
```

CSS (dùng biến màu của graphify để theo nền sáng/tối):

```css
#pylos-legend-btn { position: fixed; top: 10px; left: 10px; z-index: 10; width: 26px; height: 26px; border-radius: 50%;
  border: 1px solid var(--input-border); background: var(--panel); color: var(--text-2); font: bold 13px sans-serif;
  cursor: pointer; opacity: .85; }
#pylos-legend-btn:hover, #pylos-legend-btn[aria-expanded="true"] { color: var(--text); opacity: 1; }
#pylos-legend { position: fixed; top: 44px; left: 10px; z-index: 10; width: 300px; max-height: calc(100vh - 60px);
  overflow-y: auto; padding: 12px 14px; background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
  color: var(--text-3); font-size: 12px; line-height: 1.5; box-shadow: 0 6px 24px rgba(0,0,0,.35); }
#pylos-legend h4 { font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--text-2); margin: 10px 0 6px; }
#pylos-legend .row { display: flex; align-items: center; gap: 8px; padding: 2px 0; }
#pylos-legend svg { flex-shrink: 0; }
```

Nội dung bảng (dựng bằng JS từ `PYLOS_LAYOUT` để màu luôn khớp với bản đồ, không viết tay màu):

1. **Màu = toà** — nhóm theo khu, mỗi toà một ô màu + tên tiếng Việt + tên thư mục (`gate/fence`) + số nút.
2. **Hình = loại code** — mỗi hình vẽ bằng SVG nhỏ 14px, cùng màu xám trung tính:
   chấm tròn = hàm/method · vuông = lớp · thoi = file/module · tam giác ngược = tên import, hằng, thư viện ngoài ·
   tam giác = tài liệu · sao = lời giải thích trong code (docstring) · lục giác = khái niệm rút từ tài liệu.
   Ghi chú: "Kích thước nút = số liên kết của nút (graphify tính)".
3. **Viền nét đứt = cộng đồng** — "nhóm hàm hay đi cùng nhau do graphify tự chia theo liên kết; một cộng đồng có thể trải qua nhiều toà".
4. **Đường** — mẫu đường màu = sang toà khác (màu của toà đích) · đường xám = cùng toà · nét đứt = graphify suy đoán, nét liền = đọc thẳng từ code.
5. **Bật/tắt** (ô tick, nhớ lựa chọn trong `localStorage`, bọc `try/catch`):
   đường trong cùng file · đường cấu trúc · đường tới thư viện ngoài · đường của test · viền cộng đồng.
6. **Thao tác** — bấm nút: sáng cả cộng đồng · bấm vòng toà: sáng toà và đường ra/vào · Esc hoặc bấm chỗ trống: bỏ chọn · lăn chuột: phóng to (viền cộng đồng hiện khi đủ gần).

Hành vi nút `?`:
- Bấm: mở/đóng bảng, đổi `aria-expanded`, nhớ trạng thái mở trong `localStorage` (`pylos-legend-open`).
- Esc: đóng bảng nếu đang mở (trước khi bỏ chọn trên bản đồ).
- Bảng không che thanh bên phải của graphify; trên màn hẹp (< 700px) bảng rộng `calc(100vw - 20px)`.

### B7. Danh sách cộng đồng bên phải (của graphify)

- Chấm màu cộng đồng đổi thành **vòng tròn nét đứt** (A8), khớp viền trên bản đồ.
- Bấm tên → làm sáng cộng đồng (B5); ô tick vẫn ẩn/hiện như graphify.
- Tiêu đề "Communities" giữ nguyên (thuộc graphify).

### B8. Nền sáng/tối

- Hàm `applyTheme` của graphify chạy khi đổi nền. Thêm một lần gọi `PYLOS.recolor()` sau nó (chèn `PYLOS.recolor && PYLOS.recolor();` vào cuối `applyTheme` bằng một điểm vá riêng, hoặc nghe `MutationObserver` trên thuộc tính `data-theme`; chọn `MutationObserver` để khỏi vá thêm hàm của graphify).
- `recolor()` cập nhật màu nút, màu đường và vẽ lại; bảng chú thích tự theo vì dùng biến CSS.

---

## 5. Phần C — kiểm thử

### C1. Test tự động (`tests/lobby/atlas/test_region_map.py`, thêm)

1. `kind_of`: mỗi loại trong bảng A2 ra đúng hình; thứ tự điều kiện đúng (lớp không bị nhận là hàm).
2. Màu toà: đủ 16 vùng, hai toà cùng khu khác nhau rõ (luật ở A1).
3. `pack_region` với dữ liệu giả: hai file chung cộng đồng đứng cạnh nhau hơn file không chung; nút cùng cộng đồng trong một cụm nằm cùng múi; **mọi nút vẫn có vị trí riêng, không chồng** (giữ test cũ); chạy hai lần cùng kết quả.
4. `groups`: chỉ nhóm ≥ 3 nút, không có `outside/external`, tên `Community N` được thay.
5. Vá + gỡ: `unpatch(patch(mẫu)) == mẫu` với một `graph.html` mẫu nhỏ đặt trong `tests/` (đủ các mốc ở 1.3); thiếu một mốc thì báo lỗi và không ghi file.
6. Vá hai lần liên tiếp cho ra cùng nội dung (idempotent).
7. `pylos_nodes.json`: có đủ nút, `district` khớp `atlas.py where`.

### C2. Kiểm tra bằng mắt (mở `graphify-out/graph.html`)

- [ ] Mỗi toà một màu, cùng khu cùng họ màu; vòng tròn cùng màu với nút trong nó.
- [ ] Hình nút đúng loại (thử bấm vài lớp, vài hàm, vài file); kích thước nút giống bản graphify gốc.
- [ ] Mặc định chỉ còn đường sang toà khác (có màu) và đường cùng toà (xám); không còn "cầu vồng".
- [ ] Đi theo luồng trái → phải thấy được: cổng chính → hàng rào → điều phối → nhà dân.
- [ ] Phóng to: viền nét đứt quanh cộng đồng, có tên; thu nhỏ: viền ẩn.
- [ ] Bấm một nút: cộng đồng sáng ở mọi toà, phần khác mờ; Esc trở lại.
- [ ] Bấm vòng toà: toà sáng, đường ra/vào sáng.
- [ ] Nút `?` góc trên trái mở/đóng bảng; ô bật/tắt chạy và được nhớ sau khi tải lại.
- [ ] Đổi Light/Dark/System: màu nút, đường, bảng chú thích đổi theo.
- [ ] Kéo một nút: viền cộng đồng đi theo.
- [ ] Ô tìm kiếm của graphify vẫn chạy, viền kết quả theo màu toà.

### C3. Hiệu năng

- Mở trang < 3 giây trên máy này; bấm nút đổi trạng thái < 200 ms; kéo/phóng to không giật.
- Viền cộng đồng vẽ lại mỗi khung hình: nếu giật, tính sẵn bao lồi một lần, chỉ tính lại khi có sự kiện `dragEnd`.

---

## 6. Lỗi có thể xảy ra

| Lỗi | Dấu hiệu | Phòng / xử lý |
|---|---|---|
| graphify nâng cấp, đổi mẫu `graph.html` | `region_map` báo thiếu mốc | Dừng, không vá nửa vời (A8). Cập nhật bảng mốc ở 1.3 rồi chạy lại |
| Hook graphify ghi đè sau khi đã vá | mở ra thấy lại bản cầu vồng | Bước 2.3: đợi `graph.html` mới hơn `graph.json` rồi mới vá; chạy tay `python -m pylos.lobby.atlas.generator.region_map` |
| Cộng đồng đổi sau mỗi commit | viền, thứ tự cụm trong toà nhảy chỗ | Chấp nhận (vị trí **toà** và **file** vẫn cố định). Giữ thứ tự hoà ổn định (A3.4) để không đổi khi cộng đồng không đổi |
| Cộng đồng trải nhiều file trong một toà | viền bao lồi rộng, đè cụm khác | Viền chỉ nét đứt, không tô nền. Nếu một viền phủ > 50% diện tích vòng toà: vẽ viền **theo từng cụm file** thay vì cả nhóm |
| Kéo đường màu theo toà đích khi đích là `outside/*` | màu xám lẫn với đường thường | Đường `cross` tới `outside/entry` dùng màu hồng (A1); `tests`/`external` ẩn mặc định |
| `opacity` của nút không có tác dụng | bấm không thấy phần khác mờ | Kiểm phiên bản vis-network trong `<script src>` (hiện 9.1.6, có `opacity`). Nếu graphify hạ phiên bản: dùng màu `hsla(..., 0.15)` thay cho `opacity` |
| Màu nút đổi nhưng chữ trong khung thông tin vẫn màu cũ | viền danh sách hàng xóm sai màu | `showInfo` đọc `nb.color.background` từ `nodesDS` (đã là màu mới): không cần sửa. Ô tìm kiếm đọc `RAW_NODES`: sửa theo B1 |
| `localStorage` bị chặn (chế độ riêng tư, mở file cục bộ) | lỗi JS, bảng chú thích không mở | Mọi đọc/ghi bọc `try/catch`, mặc định khi không đọc được: bảng đóng, ô bật/tắt theo bảng B2 |
| Bản đồ chậm vì vẽ viền mỗi khung hình | kéo/phóng to giật | C3: tính sẵn bao lồi, chỉ tính lại sau `dragEnd` |
| Tên cộng đồng dài | chữ đè lên viền khác | Cắt 32 ký tự + "…", tên đầy đủ ở tooltip |
| Nhãn tiếng Việt lỗi mã hoá trên Windows khi chạy lệnh | `UnicodeEncodeError` trong console | Ghi file bằng `encoding="utf-8"`, không `print` dữ liệu nút; chỉ in số đếm |
| Dữ liệu chèn chứa `</script>` | trang vỡ | Giữ `.replace("</", "<\\/")` khi nhúng JSON (đang có) |
| `atlas --check` đỏ sau khi thêm file | test đỏ | File mới (mẫu `graph.html` thu nhỏ cho test, file hướng dẫn này) phải có dòng trong `atlas_map.toml` và được `git add` |

---

## 7. Thứ tự làm và điều kiện xong

1. Bước 2.1–2.3 (chuẩn bị).
2. A1, A2, A4 (màu, hình, vị trí toà) + B1, B3 → mở thử: đã đỡ rối phần lớn.
3. B2 (đường) → mở thử: hết cầu vồng.
4. A3 (xếp trong toà theo cộng đồng) + A5 + B4 (viền).
5. B5 (bấm để làm sáng) + B7.
6. B6 (nút `?` + bảng chú thích) + B8 (nền sáng/tối).
7. A7 (dữ liệu cho bot, lệnh `region` thêm mục cộng đồng).
8. Phần C: test tự động, kiểm bằng mắt, hiệu năng.
9. Cập nhật `atlas_map.toml` (file test mẫu mới), `CLAUDE.md` (bước 2.2), chạy `atlas --check` và `pytest -q`, một PR.

**Xong khi:** mở `graph.html` nhìn thấy ngay luồng cổng → hàng rào → điều phối → nhà dân; màu cho biết toà, hình cho biết loại code; bấm một nút thấy cả cộng đồng; nút `?` giải thích mọi thứ; kích thước nút không đổi so với graphify; test xanh.

> **Cap nhat 2026-11-06:** phan ve da chuyen vao graphify-regions (xem graphify_regions_plan.md); doi tuong JS PYLOS -> GREG; PyloS chi con xuat regions.json.
