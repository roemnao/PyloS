# Đưa bản đồ vùng vào thẳng graphify — kế hoạch chi tiết

> Làm một lần từ đầu đến cuối, không cần hỏi owner giữa chừng.
> Ngày viết: 2026-11-05. Máy: máy admin (Windows), graphify **0.9.100** cài bằng `uv tool`.
> Quyết định của owner: graphify không thuộc PyloS, bản đồ do máy admin cập nhật, nên **sửa thẳng bản graphify đã tải về**.
> Thiết kế hình (màu, hình, viền, đường, nút `?`) giữ nguyên như [region_map_redesign.md](region_map_redesign.md) và bản đang chạy trong
> `src/pylos/lobby/atlas/generator/region_map.py`. Kế hoạch này chỉ chuyển **chỗ chạy**: từ "PyloS vá lại graph.html sau khi
> graphify dựng" sang "graphify tự vẽ như vậy ngay lúc dựng", và làm cho nó chạy được với **mọi** dự án, kể cả dự án không có cấu trúc khu/toà.

---

## 0. Kết quả cần đạt

1. Chạy `graphify update .`, `/graphify`, `graphify export html`, hoặc để hook `post-commit` / `watch` tự dựng: `graph.html` ra **luôn** dạng bản đồ vùng. Không còn bước vá sau, không còn bị ghi đè.
2. Dự án nào cũng ra bản đồ vùng:
   - có file phân vùng (PyloS): vẽ đúng 4 khu, 16 vùng, tên tiếng Việt, vị trí theo luồng tin nhắn như hiện nay;
   - không có file phân vùng: **tự chia theo thư mục**;
   - dự án phẳng (mọi file một thư mục): **tự chia theo cộng đồng graphify**.
3. ~~Lệnh `/ban-do`~~ — owner quyết định bỏ (2026-11-06). Muốn dựng lại thì chạy `graphify update .`.
4. Lỗi trong phần vùng **không bao giờ** làm hỏng graphify: lỗi thì ghi `graph.html` gốc của graphify và in một dòng cảnh báo.
5. Nâng cấp graphify xong, chạy **một lệnh** là cài lại phần sửa.

---

## 1. Hiện trạng đã kiểm (không cần dò lại)

| Việc | Kết quả |
|---|---|
| Thư mục cài | `C:\Users\tp\AppData\Roaming\uv\tools\graphifyy\` — mã ở `Lib\site-packages\graphify\` (gọi tắt `GPKG`) |
| Lệnh `graphify` | `C:\Users\tp\.local\bin\graphify.exe` → gói `graphifyy` 0.9.100 (repo gốc `github.com/Graphify-Labs/graphify`) |
| Skill | `C:\Users\tp\.claude\skills\graphify\SKILL.md` (+ `references/`) — chỉ là hướng dẫn cho Claude, không phải code |
| Chỗ sinh `graph.html` | **một hàm duy nhất** `to_html()` trong `GPKG\exporters\html.py` (781 dòng). `graphify.export.to_html` chỉ re-export nó (`export.py:188`) |
| Ai gọi `to_html` | `cli.py:2859` (`graphify update` / dựng đầy đủ), `cli.py:3591` (`graphify export html`), `watch.py:1927` (hook `post-commit` và `graphify watch` qua `_rebuild_code`). Cả ba đều đi qua `to_html` → **cắm một chỗ là đủ** |
| Ghi file | dòng cuối `to_html`: `write_text_atomic(output_path, html)` (`html.py:780`) |
| Kích thước nút | `size = 10 + 30 * deg / max_deg` (`html.py:625`). Với PyloS max_deg = 103 nên ≈ `10 + 0.29·deg` — đúng công thức ước lượng trong `region_map.py`; vào trong graphify thì **dùng thẳng `size` đã tính**, bỏ ước lượng |
| Chế độ gộp | đồ thị > 5000 nút: `to_html` tự gọi lại chính nó với đồ thị cộng đồng (`member_counts` khác `None`). Bản đồ vùng **bỏ qua** trường hợp này |
| Vòng sáng "learning" | nút có `learning_status` được tô viền xanh/vàng (`html.py:660-671`). Bản đồ vùng phải **giữ viền này** |
| Thuộc tính nút có sẵn trong `G` | `_callable`, `_callable_class`, `type`, `file_type`, `source_file`, `community`, `community_name`, `node_kind`… (đủ cho `kind_of`) |
| Cấu hình dự án | `<gốc dự án>/.graphifyrc`, `key=value`; **khoá lạ bị bỏ qua** (`rcfile.py:116`) → thêm khoá `regions.*` không làm hỏng graphify bản khác |
| Mẫu HTML | các mốc mà `region_map.py` đang vá đều nằm trong `_html_script()` / `_html_styles()` / thân `to_html` của chính file này |

---

## 2. Kiến trúc sau khi sửa

```
C:\Users\tp\graphify-regions\            ← NGUỒN THẬT của phần sửa (ngoài site-packages, ngoài PyloS), có git riêng
  regions\__init__.py                    apply_regions(html, G, ...) — điểm vào duy nhất
  regions\config.py                      đọc .graphifyrc (regions.*) + file phân vùng
  regions\zoning.py                      3 cách chia vùng: file / thư mục / cộng đồng
  regions\layout.py                      xếp nút, xếp vùng, biên lãnh thổ (chuyển từ region_map.py)
  regions\assets.py                      JS + CSS + HTML chèn vào trang (chuyển từ region_map.py)
  regions\inject.py                      chèn vào chuỗi HTML theo mốc (chuyển apply_patch, bỏ unpatch)
  tests\                                 pytest cho mọi phần trên
  install.py                             chép regions\ vào GPKG\regions\ + chèn 1 đoạn vào to_html (idempotent)
  uninstall.py                           gỡ đoạn chèn + xoá GPKG\regions\ (trả graphify về như cũ)
  README.md

GPKG\exporters\html.py                   + 6 dòng trước write_text_atomic (bọc try/except)
GPKG\regions\                            bản chép, do install.py tạo — KHÔNG sửa tay ở đây

D:\pylosSever\.graphifyrc                regions.file=src/pylos/lobby/atlas/maps/regions.json
D:\pylosSever\src\pylos\lobby\atlas\maps\regions.json      sinh từ atlas_map.toml (file → vùng, bảng vùng)
D:\pylosSever\src\pylos\lobby\atlas\generator\region_map.py  rút gọn: chỉ còn XUẤT regions.json

C:\Users\tp\.claude\skills\ban-do\SKILL.md     lệnh /ban-do
```

Vì sao có thư mục nguồn riêng `C:\Users\tp\graphify-regions\` dù owner chọn "sửa bản tải về": `uv tool upgrade graphifyy` (hoặc cài lại)
**xoá sạch** mọi thứ trong `GPKG`. Có nguồn riêng thì sau nâng cấp chỉ chạy `python C:\Users\tp\graphify-regions\install.py`. Phần sửa vẫn
nằm **trong** graphify đã tải về, đúng ý owner; thư mục nguồn chỉ để không mất.

Vì sao PyloS vẫn giữ một file nhỏ: luật "file nào thuộc toà nào" nằm trong `atlas_map.toml` (glob, thứ tự ưu tiên, trạng thái) và code đọc nó
thuộc PyloS (`atlas.py`). graphify không nên biết luật của PyloS; PyloS **xuất sẵn** kết quả ra `regions.json` theo một định dạng chung (mục 3),
graphify chỉ đọc định dạng chung đó. Dự án khác không cần file này.

---

## 3. Định dạng chung: file phân vùng (`regions.json`)

```json
{
  "version": 1,
  "levels": {"group": "Khu", "region": "Toà"},
  "groups": [
    {"id": "gate", "name": "Khu cổng", "hue": 213}
  ],
  "regions": [
    {"id": "gate/fence", "name": "Hàng rào", "group": "gate", "color": [188, 65, 48], "pos": [-1.5, -0.1]}
  ],
  "files": {"src/pylos/gate/fence/rate_limiter.py": "gate/fence"},
  "unplaced_region": "outside/entry",
  "external_region": "outside/external",
  "tests_region": "outside/tests"
}
```

- Bắt buộc: `version`, `regions[].id`, `files`. Mọi thứ khác tuỳ chọn, thiếu thì tự tính (mục B4): tên = id, nhóm = phần trước dấu `/`,
  màu theo nhóm, vị trí theo luồng.
- `levels`: chữ hiển thị trong bảng chú thích và thanh bên ("Toà: …", "Màu = toà"). Mặc định `{"group": "Nhóm", "region": "Vùng"}`.
- File có trong đồ thị mà không có trong `files` → `unplaced_region` (mặc định: tự tạo vùng `(chưa xếp)` màu hồng, để thấy ngay).
- Nút không có `source_file` (thư viện ngoài) → `external_region` (mặc định: vùng `Thư viện ngoài`, xám đậm).
- `tests_region`: vùng mà đường nối tới nó bị ẩn mặc định (lớp `tests`). Không khai thì nhận theo đường dẫn: `tests/`, `test_*.py`, `*_test.*`, `*.spec.*`.

---

## 4. Các bước

Ký hiệu: `GPKG` = `C:\Users\tp\AppData\Roaming\uv\tools\graphifyy\Lib\site-packages\graphify`, `SRC` = `C:\Users\tp\graphify-regions`.

### B0. Sao lưu và chốt phiên bản

1. Chép `GPKG\exporters\html.py` thành `SRC\backup\html.py.0.9.100` (bản gốc để so và gỡ).
2. Ghi vào `SRC\README.md`: phiên bản graphify đã thử (`graphify --version` hoặc `dist-info`), ngày.
3. Chạy `graphify update .` trong PyloS một lần **trước khi sửa**, lưu `graphify-out\graph.html` thành `SRC\backup\graph.0.9.100.html` —
   mẫu thật cho test mốc (B9).

Xong khi: có 2 file sao lưu.

### B1. Tạo thư mục nguồn `SRC`

1. `git init` trong `SRC`, `.gitignore` (`__pycache__`, `.pytest_cache`).
2. Tạo khung `regions\` như mục 2, `tests\`, `install.py`, `uninstall.py`, `README.md`.
3. Không dùng thư viện ngoài graphify chưa có: chỉ thư viện chuẩn + `networkx` (graphify đã có). Không cần `tomllib` (file phân vùng là JSON).

### B2. Chuyển code từ `region_map.py` sang `SRC\regions\` (giữ nguyên hành vi)

Chuyển gần như nguyên văn, chỉ bỏ phần dính PyloS:

| Từ `region_map.py` | Sang | Sửa gì |
|---|---|---|
| `kind_of`, `KINDS` | `layout.py` | giữ nguyên |
| `_affinity`, `order_files`, `_pack_file`, `pack_region` | `layout.py` | `size` lấy **thẳng** từ `vis_nodes[*].size` của graphify, bỏ `node_size()` |
| `plan_regions`, `convex_hull`, `region_polygons` | `layout.py` | `plan_regions` nhận danh sách vùng (id, vị trí) làm tham số thay cho hằng `REGIONS` |
| `JS_DATA`, `JS_BEHAVIOR`, `CSS`, `HTML` | `assets.py` | chữ "toà/khu" lấy từ `levels` (mục 3) thay vì viết cứng; `dispatch` trong chú thích đường → vùng có nhiều đường vào nhất |
| `REPLACEMENTS`, `INSERT_*`, `apply_patch`, `missing_anchors` | `inject.py` | bỏ `unpatch` (HTML luôn mới tinh); thiếu mốc → ném `RegionsSkip` |
| `layout()` (đọc atlas) | `zoning.py` + `__init__.py` | thay bằng đọc file phân vùng / thư mục / cộng đồng (B3) |
| ghi `pylos_nodes.json` | `__init__.py` | đổi tên chung `graphify-out\graph_regions.json` (nút → vùng, loại, cộng đồng) |

Viền "learning": trong `PYLOS.nodeColor`, nếu nút có `learning_status` thì **giữ** `border` graphify đã đặt (xanh/vàng/xám), chỉ đổi `background`.

Đổi tên đối tượng JS `PYLOS` / `PYLOS_LAYOUT` → `GREG` / `GREG_LAYOUT`, mốc bọc `/* graphify-regions:begin */…end */` (không còn chữ PyloS trong graphify).

Xong khi: `pytest SRC\tests` chạy các test đã có trong `tests\lobby\atlas\test_region_map.py` (chép sang, sửa import) và xanh.

### B3. Ba cách chia vùng (`zoning.py`)

Hàm `zone(G, root, cfg) -> Zoning` trả về: danh sách vùng (id, tên, nhóm, màu?, vị trí?), `node → vùng`, chữ `levels`.
Chọn cách theo thứ tự:

1. **`regions.mode=off`** trong `.graphifyrc` → không làm gì (trả `None`, `to_html` ghi HTML gốc).
2. **File phân vùng** (`regions.file=<đường dẫn tương đối gốc dự án>`, hoặc có sẵn `<gốc>/graphify-regions.json`): đọc theo mục 3.
   Kiểm: mọi giá trị trong `files` phải là một `regions[].id`; sai thì `RegionsSkip("regions.json: vùng lạ X")`.
3. **Theo thư mục** (mặc định khi không có file): `regions.depth=<n>` (mặc định **2**).
   - Bỏ tiền tố chung của mọi `source_file` (ví dụ `src/` hoặc `src/<tên gói>/`) để cấp 1 là thư mục có nghĩa.
   - Vùng = `n` cấp thư mục đầu; nhóm (họ màu) = cấp 1. File nằm nông hơn `n` cấp → vùng theo đường dẫn ngắn hơn.
   - File ở gốc dự án → vùng `(gốc)`; thư mục `tests`/`test`/`spec` → vùng test (nhóm `ngoài`).
   - Quá nhiều vùng (> 24): giảm `depth` đi 1 và chia lại; vẫn quá → gộp các vùng nhỏ nhất (< 1% số nút) thành `(khác)` của nhóm đó.
   - Chỉ ra **1** vùng (dự án phẳng) → sang cách 4.
4. **Theo cộng đồng** (dự án phẳng): gộp các cộng đồng graphify thành ≤ 12 vùng.
   - Mỗi file thuộc cộng đồng chiếm nhiều nút nhất của nó.
   - Gộp tham lam hai cộng đồng có nhiều đường nối giữa chúng nhất, tới khi còn ≤ 12; nhóm 1–2 nút gộp vào `(lẻ)`.
   - Tên vùng = nhãn nút có bậc lớn nhất trong vùng; tất cả cùng một nhóm.

Ghi cách đã dùng vào dòng in ra: `graph.html: bản đồ vùng (thư mục, depth 2): 9 vùng, 4 nhóm`.

### B4. Màu và vị trí tự động (`layout.py`)

- **Màu** (khi vùng không có `color`): chia vòng màu đều cho các nhóm (bỏ khoảng 330–30 dành cho "chưa xếp"); trong một nhóm, các vùng
  lệch hue ±18 và light ±8 xen kẽ, sao cho hai vùng cùng nhóm luôn khác rõ (luật A1 cũ: hue cách ≥ 15 hoặc light cách ≥ 8 — giữ test).
  Vùng ngoài (test, thư viện ngoài, gốc) màu xám bậc 66/55/44/33.
- **Vị trí** (khi vùng không có `pos`): theo luồng gọi.
  1. Đếm đường nối giữa các vùng (bỏ `struct`, `external`, `tests`).
  2. `x` = (đi ra − đi vào) / (đi ra + đi vào), đảo dấu: vùng gọi đi nhiều (lối vào) bên **trái**, vùng bị gọi nhiều (thư viện dùng chung) bên **phải**.
  3. `y` = thứ tự nhóm (nhóm cùng hàng dọc gần nhau); vùng ngoài (test, gốc, thư viện ngoài) xuống **dưới**.
  4. Đưa vào `plan_regions` để đẩy cho hết chồng (như hiện nay).
- PyloS có `pos` + `color` trong `regions.json` nên ra **y hệt** bản hiện tại.

### B5. Cắm vào graphify (`install.py`)

Đoạn chèn vào `GPKG\exporters\html.py`, ngay **trước** `    write_text_atomic(output_path, html)` (dòng cuối `to_html`):

```python
    # graphify-regions:begin (C:\Users\tp\graphify-regions — gỡ bằng uninstall.py)
    if not member_counts:
        try:
            from graphify.regions import apply_regions
            html = apply_regions(html, G, communities, community_labels, vis_nodes, output_path)
        except Exception as exc:  # không bao giờ làm hỏng graph.html gốc
            print(f"[graphify regions] bỏ qua: {exc}")
    # graphify-regions:end
```

`install.py`:
1. Tìm `GPKG` bằng `uv tool dir` (+ `\graphifyy\Lib\site-packages\graphify`); không thấy → dừng, in hướng dẫn.
2. Đọc phiên bản trong `graphifyy-*.dist-info`. Khác `0.9.100` → vẫn cài, nhưng in cảnh báo "chưa thử với bản X, chạy `pytest SRC\tests`".
3. Xoá khối `graphify-regions:begin…end` cũ nếu có (idempotent), tìm đúng **một** dòng `    write_text_atomic(output_path, html)`
   **sau** `def to_html(`; không thấy hoặc thấy nhiều → dừng, **không ghi gì**.
4. Chép `SRC\regions\` → `GPKG\regions\` (xoá bản cũ trước).
5. Xoá `GPKG\exporters\__pycache__\html*.pyc` để Python nạp bản mới.
6. Kiểm: `python -c "import graphify.regions"` bằng python của uv tool (`...\graphifyy\Scripts\python.exe`).

`uninstall.py`: xoá khối chèn + `GPKG\regions\`; so `html.py` với `SRC\backup\html.py.<phiên bản>` khi trùng phiên bản, báo khớp hay không.

### B6. Phía PyloS

1. `region_map.py` rút gọn thành **xuất** `src/pylos/lobby/atlas/maps/regions.json`:
   - bảng `REGIONS` (tên, khu, vị trí, màu) giữ ở đây — đây là phần riêng của PyloS;
   - `files`: mọi file được atlas gán, `file → zone/building` (đã quy về 16 vùng hiển thị bằng `region_of` hiện có);
   - `levels = {"group": "Khu", "region": "Toà"}`, `unplaced_region = "outside/entry"`, `external_region`, `tests_region`.
   - Bỏ toàn bộ phần vá HTML, JS, CSS (đã sang graphify).
2. Lệnh `python -m pylos.lobby.atlas.generator.atlas` (đang chạy sau mỗi lần thêm/dời file, luật 4 của CLAUDE.md) **ghi luôn** `regions.json`;
   `--check` báo lỗi nếu `regions.json` cũ hơn `atlas_map.toml` (khác nội dung) — test sẵn có sẽ bắt.
3. Tạo `D:\pylosSever\.graphifyrc`:
   ```
   # bản đồ vùng (graphify-regions trên máy admin): file → khu/toà sinh từ atlas_map.toml
   regions.file=src/pylos/lobby/atlas/maps/regions.json
   ```
4. Thêm `.graphifyrc` và `maps/regions.json` vào `atlas_map.toml` (`outside/repo_root` và `lobby/atlas/maps`), `git add`.
5. `CLAUDE.md` mục "Finding things": thay dòng `region_map` bằng: bản đồ vùng do graphify-regions trên máy admin vẽ khi dựng đồ thị;
   PyloS chỉ giữ `regions.json` (sinh từ atlas). Máy không cài graphify-regions vẫn ra `graph.html` thường, không lỗi.
6. Bot: `atlas region` không đổi (đọc `graph.json` trực tiếp). `pylos_nodes.json` → đổi chỗ đọc (nếu có) sang `graphify-out/graph_regions.json`.
7. Xoá dòng hook `region_map --wait` khỏi kế hoạch cũ (không cần nữa). Không đụng hook `post-commit` của graphify.

### B7. (bỏ) Lệnh `/ban-do`

Owner quyết định không làm (2026-11-06). Bản đồ vẫn tự ra khi chạy `graphify update .` hoặc khi hook dựng lại;
nâng cấp graphify thì chạy `install.py` (B11).

---

**Đã làm (2026-11-06):** B0–B6 và B8–B10. `C:\Users\tp\graphify-regions` (44 test xanh, chạy bằng python của uv tool) đã cài vào graphify 0.9.100;
`graphify update .` trong PyloS ra bản đồ đúng 16 toà; PyloS xuất `regions.json` + `.graphifyrc`, `pytest -q` PyloS xanh.

### B8. Dọn bản cũ

1. `graphify-out\graph.html` không còn được `region_map.py` vá; lần dựng đầu sau B5 ghi đè bằng bản mới. Không cần `unpatch`.
2. Xoá `graphify-out\pylos_nodes.json` cũ sau khi B6.6 xong.
3. Ghi một dòng vào cuối `region_map_redesign.md`: "Phần vẽ đã chuyển vào graphify-regions (graphify_regions_plan.md)."

### B9. Kiểm thử tự động

Trong `SRC\tests\` (chạy bằng python của uv tool để có `networkx` và `graphify`):

1. Mọi test cũ của `test_region_map.py` (kind, màu, xếp nút không đè, múi cộng đồng, ổn định, biên ôm nút, lãnh thổ) — chép sang.
2. `inject`: chèn vào `backup\graph.0.9.100.html` (mẫu thật, đã gỡ phần vùng nếu có): đủ mốc, chèn hai lần ra một kết quả, thiếu một mốc → `RegionsSkip`.
3. `zoning`:
   - file phân vùng: vùng lạ → lỗi rõ; file thiếu trong `files` → vùng chưa xếp;
   - thư mục: cây giả `src/app/{api,db,ui}/…` + `tests/` → 3 vùng + test, tiền tố chung `src/app/` bị bỏ; > 24 vùng → giảm depth;
   - cộng đồng: dự án phẳng 40 file → ≤ 12 vùng, tên không rỗng.
4. Màu tự động: 30 vùng trong 5 nhóm vẫn qua luật khác rõ.
5. Vị trí tự động: vùng chỉ gọi đi nằm trái vùng chỉ bị gọi.
6. Cắm vào graphify: dựng `G` nhỏ bằng networkx, gọi `graphify.exporters.html.to_html` thật → HTML có `GREG_LAYOUT`; làm `apply_regions` ném lỗi (monkeypatch) → vẫn ghi HTML gốc, in cảnh báo; `member_counts` khác `None` → không chèn.
7. `install.py` / `uninstall.py` trên một bản chép `GPKG` giả trong `tmp_path`: cài hai lần = một lần; gỡ xong `html.py` trùng bản gốc.

Trong PyloS: `tests/lobby/atlas/test_region_map.py` thu lại còn test **xuất** `regions.json` (đủ 16 vùng, mọi file atlas có vùng, màu/vị trí có mặt,
khớp định dạng mục 3) + `atlas --check` bắt `regions.json` cũ. `pytest -q` toàn bộ phải xanh.

### B10. Kiểm bằng mắt

1. PyloS: `graphify update .` → mở `graphify-out\graph.html`: phải **giống** bản hiện tại (khu, màu, biên lãnh thổ, hình, viền cộng đồng, "Nhóm lẻ",
   danh sách xếp theo toà, nút `?`, chú thích đường mới). Commit thử một thay đổi nhỏ → đợi hook xong → mở lại: **vẫn** là bản đồ vùng.
2. Một dự án khác có thư mục (ví dụ chính repo `SRC`, hoặc một repo nhỏ bất kỳ): `graphify update .` → vùng theo thư mục, tên thư mục, màu tự động.
3. Một dự án phẳng (một thư mục vài chục file `.py`): vùng theo cộng đồng.
4. `.graphifyrc` có `regions.mode=off` → `graph.html` gốc graphify.
5. Đổi Light/Dark, bấm nút/vùng/Esc, ô bật/tắt, tìm kiếm — như checklist C2 của `region_map_redesign.md`.

### B11. Khi nâng cấp graphify

1. `uv tool upgrade graphifyy` (hoặc cài lại) → phần sửa **mất** (bình thường).
2. Lưu mẫu `graph.html` mới (B0.3) vào `SRC\backup\`, chạy `pytest SRC\tests` với mẫu mới.
3. `python C:\Users\tp\graphify-regions\install.py`.
4. Mốc đổi (test 2 đỏ, hoặc dòng `[graphify regions] bỏ qua: thiếu mốc …`) → sửa bảng mốc trong `inject.py`, chạy lại 2–3.
   Trong lúc chưa sửa, graphify vẫn chạy bình thường, chỉ ra bản đồ gốc.

### B12. Hoàn tất

1. Commit trong `SRC` (git riêng).
2. PyloS: một commit/PR gồm B6 + B8 + test; chạy `python -m pylos.lobby.atlas.generator.atlas --check` và `pytest -q` trước.
3. Ghi vào memory của Claude (máy admin): graphify-regions nằm ở `C:\Users\tp\graphify-regions`, cài lại bằng `install.py` sau mỗi lần nâng cấp graphify.

---

## 5. Lỗi có thể xảy ra

| Lỗi | Dấu hiệu | Phòng / xử lý |
|---|---|---|
| Nâng cấp graphify xoá phần sửa | `graph.html` về bản cầu vồng, không có nút `?` | B11: chạy `install.py`. `/ban-do` tự kiểm và cài lại (B7.1) |
| graphify bản mới đổi mẫu HTML | dòng `[graphify regions] bỏ qua: thiếu mốc …` | Không hỏng gì (ghi HTML gốc). Sửa `inject.py` theo mẫu mới (B11.4) |
| graphify bản mới đổi `to_html` (bỏ `write_text_atomic`, đổi tên biến `vis_nodes`) | `install.py` dừng "không tìm thấy chỗ chèn" | `install.py` không ghi gì; sửa đoạn chèn trong `install.py` theo mã mới |
| Python của uv tool khác Python của PyloS | `import graphify.regions` lỗi khi chạy test bằng `.venv` PyloS | Test của `SRC` chạy bằng `...\graphifyy\Scripts\python.exe`; PyloS không import graphify |
| Thiếu `pytest` trong môi trường uv tool | không chạy được test `SRC` | `uv tool install graphifyy --with pytest` **hoặc** chạy test bằng `uv run --with pytest --with networkx` và `PYTHONPATH=GPKG\..` |
| `regions.json` của PyloS cũ so với `atlas_map.toml` | file mới dời rơi vào "(chưa xếp)" màu hồng | `atlas --check` (trong `pytest`) đỏ; chạy `python -m pylos.lobby.atlas.generator.atlas` |
| Máy khác (VPS) không có graphify-regions | `graph.html` trên đó là bản gốc | Đúng thiết kế: bản đồ do máy admin dựng. `.graphifyrc` có khoá lạ không làm hỏng graphify ở đó |
| Hook graphify chạy nền, `apply_regions` chậm làm commit chậm | — | Hook đã chạy nền (`Popen`, `hooks.py:376`); `apply_regions` đo ~0.5 s với 2000 nút. Đặt giới hạn: > 5000 nút đã là chế độ gộp, bỏ qua |
| Chia theo thư mục ra vùng vô nghĩa (repo lộn xộn) | vùng `src`, `lib`, `utils` lẫn lộn | Đặt `regions.depth`, hoặc viết `graphify-regions.json` cho repo đó (định dạng mục 3, có thể chỉ khai `files` theo thư mục) |
| Dự án quá nhiều vùng | bản đồ rộng, chữ nhỏ | B3.3: > 24 vùng giảm depth / gộp `(khác)` |
| Viền "learning" của graphify bị màu vùng đè | mất vòng xanh/vàng | B2: `nodeColor` giữ `border` khi có `learning_status`; test 6 kiểm |
| Đổi tên `PYLOS` → `GREG` sót một chỗ | lỗi JS, trang trắng | Test 2 chạy `node --check` trên khối script (bỏ qua nếu máy không có node) + test 6 |
| Windows: `UnicodeEncodeError` khi in tiếng Việt từ hook | hook chết im lặng, không có bản đồ | `apply_regions` không in dữ liệu nút; dòng tóm tắt in bằng `errors="replace"` (bọc `try` quanh `print`) |
| `__pycache__` cũ của `html.py` | sửa xong vẫn chạy bản cũ | `install.py` xoá `.pyc` (B5.5) |
| Hai bản `regions` lệch nhau (`SRC` và `GPKG`) | sửa `SRC` mà bản đồ không đổi | Luôn sửa ở `SRC` rồi chạy `install.py`; không sửa tay `GPKG\regions\` (README ghi rõ) |

---

## 6. Thứ tự làm và điều kiện xong

1. B0 → B1 → B2 (test cũ xanh trong `SRC`).
2. B3 + B4 (test zoning/màu/vị trí xanh).
3. B5 (`install.py`), cài vào graphify thật, test cắm vào graphify xanh.
4. B6 (PyloS xuất `regions.json`, `.graphifyrc`, atlas, CLAUDE.md), `pytest -q` PyloS xanh.
5. B7 (`/ban-do`), B8 (dọn).
6. B10 kiểm bằng mắt trên PyloS + một repo có thư mục + một repo phẳng.
7. B12 commit.

**Xong khi:** `graphify update .` trong PyloS ra đúng bản đồ hiện tại mà không cần bước vá nào; commit xong hook dựng lại vẫn ra bản đồ vùng;
một repo khác không có cấu hình vẫn ra bản đồ chia theo thư mục; `regions.mode=off` trả về graphify gốc; gỡ bằng `uninstall.py` thì `html.py`
trùng bản sao lưu; nâng cấp graphify rồi chạy `install.py` là có lại.
