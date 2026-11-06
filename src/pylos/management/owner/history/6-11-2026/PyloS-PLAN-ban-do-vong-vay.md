# Kế hoạch lần 2: bản đồ theo vòng vây quanh một trung tâm (6-11-2026)

Thay cho phần xếp vị trí của `PyloS-PLAN-ban-do-trung-tam.md` (lần 1). Owner duyệt hướng: một trung tâm, vòng vây
theo đường nối, toà cùng khu nằm gần nhau nhưng giữ thứ bậc vòng, ngoại thành giữ nguyên hàng dưới cùng.
Làm hết các bước theo thứ tự, không cần hỏi owner giữa chừng; cuối cùng báo kết quả và để owner xem bằng mắt.

Mã nguồn: `C:/Users/tp/graphify-regions/regions/` (cài vào graphify bằng `install.py`).
PyloS chỉ đổi `src/pylos/lobby/atlas/generator/region_map.py`, `regions.json` sinh ra, test của nó, và tài liệu.

## Lỗi của lần 1 và nguyên nhân

| Lỗi owner thấy | Nguyên nhân |
|---|---|
| Điều phối không nằm giữa | Chọn tới 2 tâm (Điều phối + Cổng phụ), đặt cạnh nhau; bước "kéo sát" lực tự do làm trôi hết vòng. |
| Toà cùng khu xa nhau (Owner – Quản lý) | Cách xếp không biết khu, chỉ kéo theo đường gọi. |
| Lối vào bot ra tận ngoại thành | `regions.json` cho nó `pos` nên bị coi là ngoại thành, dù nó có 136 đường nối vào nội thành. |
| Danh sách cộng đồng bên phải mất | Lần dựng cuối dùng `graphify export html`, đường này đưa `LEGEND = []`. Không phải lỗi code vẽ. |

## Số liệu thật dùng để kiểm (graph.json lúc lập kế hoạch)

| Toà | Đường ra/vào toà khác | Số nút | Bậc nút lớn nhất |
|---|---|---|---|
| Điều phối | 355 | 296 | 103 |
| Cổng phụ | 244 | 197 | 58 |
| Toà Owner | 154 | 195 | 90 |
| Cổng chính | 146 | 153 | 32 |
| Lối vào bot | 136 | 28 | 66 |
| Toà nhà dân | 128 | 84 | 44 |

Đường nối mạnh nhất với Điều phối: Cổng phụ 149, Owner 62, Lối vào bot 52, Cổng chính 29, Nhà dân 26, Văn phòng 17.

Vòng dự kiến (đã chạy thử quy tắc ở Bước 2 trên dữ liệu thật):
- Vòng 0: Điều phối
- Vòng 1: Cổng phụ, Toà Owner, Lối vào bot, Cổng chính, Toà nhà dân
- Vòng 2: Văn phòng, Hàng rào, Toà quản lý
- Vòng 3: Bản đồ, Thư viện
- Vòng cuối: Toà khách (không có đường nối)

---

## Bước 0: Chuẩn bị
1. Ghi lại trạng thái hiện tại để so sánh: in bảng `id, x, y, r` của `GREG_LAYOUT` trong `graphify-out/graph.html` ra scratchpad.
2. Chạy test hai bên để có mốc: `pytest tests` của graphify-regions (bằng python của uv tool), `pytest -q` của PyloS.

## Bước 1: Chọn một trung tâm (`zoning.py`)
1. Viết `region_stats(region, edges, sizes)` trả về cho mỗi vùng: `flow` (tổng đường nối sang vùng nội thành khác,
   bỏ đường cấu trúc `contains/method/rationale_for`, bỏ thư viện ngoài và test), `nodes` (số nút), `top` (bậc của nút
   lớn nhất trong vùng). Bậc tính trên toàn bộ cạnh, giống graphify tính cỡ nút.
2. Viết `pick_center(inner, stats, override)`:
   - Có `override` (khoá `"center"` trong regions.json, hoặc `regions.center=` trong `.graphifyrc`) và id hợp lệ thì
     lấy **phần tử đầu tiên**.
   - Không thì điểm = `flow/max_flow + nodes/max_nodes + top/max_top` (ba phần bằng trọng số), lấy điểm cao nhất;
     hoà thì lấy `flow` lớn hơn, rồi id theo thứ tự chữ.
   - Luôn trả về **đúng một** id.
3. Bỏ `closeness_order`, `CENTER_RATIO`, `MAX_CENTERS`. `Zoning.centers` giữ nguyên tên trường nhưng chỉ dùng
   phần tử đầu.
4. `build_layout` (`__init__.py`): tính `stats` ngay sau `flows`, gọi `pick_center`, `hub = center`.

## Bước 2: Chia vòng vây (`zoning.py`)
1. Viết `assign_rings(inner, center, w)` với `w[(a, b)]` là số đường nối hai chiều giữa hai vùng nội thành:
   ```
   ring[center] = 0; placed = {center}; k = 0
   lặp khi còn vùng chưa xếp:
       link[x] = tổng w[(x, y)] với y đã xếp (vòng 0..k)
       top = max(link)
       nếu top == 0: mọi vùng còn lại vào vòng k+1, dừng
       vòng k+1 = các x có link[x] >= max(1, RING_SHARE * top)      # RING_SHARE = 0.15
       k += 1
   ```
   Trong một vòng, thứ tự = nối vào vòng ngay trong nó (vòng k) nhiều trước, rồi tới `link`, rồi id.
2. Trả về `ring: dict[id, int]` và `rings: list[list[id]]`.
3. Ghi `ring` của mỗi vùng vào dữ liệu `GREG_LAYOUT.regions[i].ring` (để chú thích và kiểm thử dùng).

## Bước 3: Quạt theo khu (`layout.py`)
1. Mỗi khu nội thành (`group`) có ít nhất một vùng ở vòng >= 1 thì nhận một quạt góc. Khu của trung tâm cũng nhận
   quạt nếu còn toà khác (Văn phòng, Bản đồ, Thư viện).
2. Bề rộng quạt tỉ lệ với tổng `(2r + gap)` của các vùng trong khu (không tính trung tâm), tổng các quạt = 360°.
3. Thứ tự các quạt quanh vòng: khu nối nhiều với nhau thì kề nhau. Cách làm: bắt đầu từ khu có đường nối với trung
   tâm nhiều nhất; lần lượt thêm khu chưa xếp có đường nối nhiều nhất với khu vừa thêm (tham lam, xác định).
4. Góc giữa của khu đầu tiên đặt ở hướng trên (−90°), để hàng ngoại thành ở dưới không đụng quạt lớn nhất.

## Bước 4: Đặt vị trí theo vòng, rồi ép theo bán kính (`layout.py`, thay `plan_city`)
1. Viết `plan_rings(radius, center, rings, group, w, outer, gap=24)`:
   - Trung tâm ở `(0, 0)`, cố định.
   - Vòng k: trong mỗi quạt, các vùng của khu đó thuộc vòng k chia đều góc của quạt (theo `2r + gap`), thứ tự theo
     đường nối với vùng vòng k−1 cùng khu (vùng nối nhiều đứng giữa quạt).
   - Bán kính xuất phát của vòng k = bán kính ngoài của vòng k−1 + gap + bán kính vùng lớn nhất của vòng k.
2. Ép theo bán kính (thay vòng lực tự do):
   - Xử lý từ vòng 1 ra ngoài. Mỗi vùng giữ nguyên góc; tìm khoảng cách tới tâm nhỏ nhất sao cho không đè lên vùng
     nào đã đặt (khoảng hở `gap`), bằng tìm nhị phân trên đoạn `[r_center + r + gap, bán kính xuất phát]`.
   - Ràng buộc vòng: khoảng cách tới tâm của vùng vòng k+1 phải lớn hơn khoảng cách của mọi vùng vòng k **cùng khu**
     và lớn hơn khoảng cách nhỏ nhất của vòng k nói chung.
   - Nếu không tìm được chỗ trong đoạn thì giữ bán kính xuất phát.
3. Sau khi ép, chạy `_resolve` (đẩy khi đè) với trung tâm cố định, tối đa 200 lượt, chỉ đẩy theo hướng ra xa tâm
   để không đảo thứ tự vòng.
4. Bỏ `plan_city` và vòng lực "kéo sát" cũ.
5. Ngoại thành: giữ nguyên đoạn mã xếp hàng dưới cùng hiện tại (sắp theo `pos.x`, xuống dòng khi dài hơn cụm).

## Bước 5: Màu theo vòng (`zoning.py`, `auto_colors`)
1. `t = ring / ring_lớn_nhất`. Hue gốc của vòng = `8 + 232 * t` (vòng 0 đỏ cam, vòng ngoài cùng xanh tím).
2. Trong một vòng, các vùng lệch hue trong dải `±(232 / số vòng) * 0.4` theo thứ tự quạt, và độ sáng theo chu kỳ
   `(0, +10, −8)`.
3. Kiểm: hai vùng nội thành bất kỳ khác nhau ≥ 15° hue hoặc ≥ 8 độ sáng; nếu vi phạm thì tăng lệch độ sáng của vùng sau.
4. Vùng có `color` trong regions.json giữ nguyên; ngoại thành giữ xám.

## Bước 6: PyloS
1. `region_map.py`: `outside/entry` (Lối vào bot) bỏ `pos` và màu, để thành nội thành. 4 vùng ngoại thành
   (`tests`, `repo_root`, `tooling`, `external`) giữ `pos` và xám.
2. Không ghi `center` (tự chọn đã ra Điều phối). Nếu Bước 8 cho kết quả khác thì thêm `"center": ["lobby/dispatch"]`.
3. Sửa `tests/lobby/atlas/test_region_map.py`: chỉ 4 vùng `outside/*` có `pos`; `outside/entry` không có.
4. Chạy `python -m pylos.lobby.atlas.generator.atlas`, rồi `--check`.

## Bước 7: Danh sách cộng đồng bên phải (`assets.py`)
1. Ở đầu `JS_BEHAVIOR`: nếu `LEGEND.length === 0` thì dựng lại từ `RAW_NODES`: mỗi `community` một dòng
   `{cid, color, label: community_name || 'Community ' + cid, count}`, rồi gọi lại hàm vẽ danh sách của graphify
   (tìm tên hàm trong `backup/graph.0.9.100.html`; nếu không gọi được thì tự vẽ `.legend-item` cùng cấu trúc).
2. Test trong `test_inject.py`: trang mẫu có `const LEGEND = [];` thì đoạn chèn vẫn chứa nhánh dựng lại.
3. Dựng lại bản đồ bằng đường thường: `graphify update .`. Nếu báo "No relevant changes" thì xoá
   `graphify-out/graph.html` rồi chạy lại `graphify update .`. **Không** dùng `graphify export html`.
4. Ghi chú vào `README.md` của graphify-regions: `export html` có thể ra danh sách cộng đồng rỗng.

## Bước 8: Kiểm thử
Test mới trong graphify-regions:
1. `pick_center` trả về đúng một id; với số liệu giả kiểu bảng trên thì ra vùng "dispatch"; `override` thắng.
2. `assign_rings` cho đúng vòng trên đồ thị giả; vùng không nối vào vòng cuối.
3. `plan_rings`:
   - trung tâm ở `(0, 0)`;
   - mọi vùng vòng k+1 xa tâm hơn mọi vùng vòng k cùng khu;
   - các vùng cùng khu nằm trong cùng quạt (chênh góc với góc giữa quạt ≤ nửa bề rộng quạt + sai số);
   - không hai vùng nào đè nhau (`dist >= r1 + r2`);
   - ngoại thành nằm dưới đáy cụm nội thành.
4. `auto_colors`: hue tăng theo vòng; điều kiện phân biệt màu ở Bước 5.3.
5. Bỏ hoặc sửa test cũ của `plan_city`, `closeness_order`.

Chạy:
- `pytest tests` (graphify-regions, python của uv tool) — tất cả qua.
- `python install.py`, rồi dựng lại bản đồ PyloS như Bước 7.3.
- `pytest -q` của PyloS và `atlas --check`.
- In bảng `id, ring, x, y, r, khoảng cách tới tâm` từ `GREG_LAYOUT`, so với vòng dự kiến ở đầu file; kiểm
  `LEGEND` trong graph.html khác rỗng.

## Bước 9: Tài liệu và báo cáo
1. `CLAUDE.md` (mục graphify): thay đoạn "centre building(s) ... ring by ring" bằng mô tả: một trung tâm theo luồng +
   số nút + nút lớn nhất, vòng vây theo đường nối, quạt theo khu, ngoại thành hàng dưới.
2. `src/pylos/management/owner/private_plans/region_map_redesign.md`: thêm ghi chú bố cục vòng vây.
3. Cuối file này thêm mục "Đã làm" với bảng vòng thật và kết quả test.
4. Báo owner: bảng vòng, những gì chưa xem bằng mắt. Không commit cho tới khi owner bảo.

## Giả định (owner đã cho phép làm không hỏi)
- Lối vào bot thành nội thành, màu theo vòng (không còn hồng riêng).
- Ngưỡng vòng `RING_SHARE = 0.15`, khoảng hở `gap = 24`.
- Khu của trung tâm (lobby) vẫn có quạt riêng cho các toà còn lại của nó.

## Đã làm (6-11-2026)
- graphify-regions: `pick_center` (đúng một tâm), `assign_rings`, `layout.plan_rings` (quạt theo khu, ép theo bán kính, ngoại thành hàng dưới), `auto_colors` theo vòng, `_fill_empty_legend` (dựng lại danh sách cộng đồng khi graphify đưa rỗng). 50 test qua.
- PyloS: `outside/entry` thành nội thành; chỉ 4 vùng xám ghim vị trí. 430 test qua, `atlas --check` OK.
- Kết quả thật: vòng 0 Điều phối; vòng 1 Owner, Cổng chính, Cổng phụ, Nhà dân, Lối vào bot; vòng 2 Quản lý, Hàng rào, Văn phòng; vòng 3 Bản đồ, Thư viện; vòng 4 Toà khách. Không vùng nào đè nhau, danh sách cộng đồng 157 dòng. Chưa xem bằng mắt.

## Luật tô màu (sửa 6-11-2026, sau khi owner thấy đỏ-xanh lá-vàng bị bẩn)
1. Màu cố định theo vòng, lấy mẫu đều trên dãy `RING_HUES = 8, 32, 175, 205, 235, 270`: đỏ cam → hổ phách → xanh ngọc → xanh lam → chàm → tím. Vòng 0 luôn đỏ cam, vòng cuối luôn tím.
2. Bỏ hẳn dải 60–150° (vàng, vàng chanh, xanh lá): trên nền tối nó ra màu ô liu bẩn.
3. Cùng vòng: cùng họ màu (lệch ±6° xen kẽ), phân biệt bằng độ sáng trải đều 42–76%, xen kẽ để hai vùng đứng cạnh nhau lệch độ sáng xa.
4. Hai vùng bất kỳ phải khác nhau ≥15° hue hoặc ≥8% độ sáng; nếu trùng thì đổi độ sáng.
5. Ngoại thành xám; vùng có `color` trong regions.json giữ nguyên.

## Luật tô màu, bản 2 (owner: "thiếu ấn tượng, nền trắng bị đen")
1. Trung tâm và vòng 1: màu nóng, mỗi toà một màu riêng, tách hai phía của đỏ: đỏ (trung tâm), cam vàng, hồng, vàng nghệ, cam đỏ, hồng đậm...
2. Vòng 2 trở ra: màu lạnh theo thứ tự vòng, xanh ngọc → xanh lam → chàm → tím.
3. Không dùng dải vàng chanh / xanh lá (60–150°).
4. Bão hoà 85% (đậm, nổi); hai toà liên tiếp lệch độ sáng +10; hai toà bất kỳ khác ≥15° hoặc ≥8% sáng.
5. Theo nền: nền tối độ sáng 50–72%; nền sáng 38–54% (vàng/cam ≥45% để không thành nâu); xám nền sáng 40–62% (không đen). Nền vùng đậm hơn (0.15 tối / 0.12 sáng).
