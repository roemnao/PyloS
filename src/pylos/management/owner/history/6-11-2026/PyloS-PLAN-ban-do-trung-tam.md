# Kế hoạch: bản đồ vùng xếp từ trung tâm ra (6-11-2026)

Phần vẽ nằm trong graphify-regions (`C:/Users/tp/graphify-regions/regions/`, cài vào graphify bằng `install.py`).
PyloS chỉ đổi `region_map.py` (bảng vùng) và `regions.json` sinh ra.

## Vấn đề và nguyên nhân

| Vấn đề | Nguyên nhân |
|---|---|
| Cụm quá xa nhau | `auto_positions` (zoning.py) đặt toạ độ theo luồng gọi rồi nhân tỉ lệ lớn; `plan_regions(gap=60)` đẩy xa thêm; không có bước kéo lại gần. |
| Chữ nhỏ | Tên vùng/dòng phụ/tên nhóm vẽ theo toạ độ thế giới nên thu nhỏ bản đồ là chữ nhỏ theo. |
| Nội thành ngẫu nhiên | Vị trí và màu 12 toà nội thành gán tay; màu theo họ của khu, không theo vai trò của toà. |

## Bước 1: Chữ luôn đọc được (assets.py)
1. Cỡ chữ theo màn hình: `font = px / network.getScale()`: tên vùng 15px, dòng phụ 11px, tên nhóm 11px.
2. Trần 90 đơn vị thế giới để thu nhỏ hết cỡ chữ không to hơn cả vùng.
3. Chống đè chữ: duyệt vùng từ lớn đến nhỏ, nhãn nào đè nhãn đã vẽ thì bỏ dòng phụ trước, rồi mới bỏ tên.
4. Tên nhóm (cộng đồng): thu nhỏ thì chỉ hiện nhóm lớn nhất mỗi vùng, phóng to thì hiện thêm.
5. Chữ có viền tối mỏng (halo).

## Bước 2: Chọn trung tâm (zoning.py, `find_centers`)
1. Độ trung tâm = tổng đường gọi vào + ra giữa các vùng (bỏ đường cấu trúc, thư viện ngoài, test).
2. Trung tâm = vùng điểm cao nhất + vùng có điểm ≥ 60% điểm đó; tối đa 3.
3. Ghi đè được: `"center": [...]` trong regions.json hoặc `regions.center=` trong `.graphifyrc`.
4. Vòng: vòng 0 = trung tâm; vòng k = cách trung tâm k bước trên đồ thị vùng (luồng mạnh = gần).

## Bước 3: Xếp vị trí từ trung tâm ra và kéo gần (layout.py)
1. Thay `auto_positions` bằng xếp theo vòng: vòng k nằm trên đường tròn bán kính ≈ tổng bán kính các vùng vòng trước + hở. Trong vòng, vùng có luồng với nhau xếp kề nhau.
2. Làm mượt bằng lực (100–200 vòng): lò xo theo luồng, đẩy khi đè nhau, hút nhẹ về tâm; dừng khi vừa chạm với khoảng hở `gap`.
3. `gap` 60 → 24.
4. Vùng ngoại thành (`outside/*`) giữ cách xếp cũ (hàng ngang phía dưới) nhưng sát cụm nội thành hơn.
5. regions.json: vùng nội thành bỏ `pos` và `color`; `from_file` vẫn hiểu `pos`/`color` nếu có (ngoại thành, dự án khác).

## Bước 4: Màu nóng ở trung tâm, lạnh ở xa (zoning.py, `auto_colors`)
1. `t = vòng / vòng_xa_nhất`; `hue = 8 + 232 * t` (đỏ cam → vàng → xanh lá → xanh dương → tím).
2. Cùng vòng lệch nhẹ hue ±10° và độ sáng +8/-6; điều kiện "hue ≥15° hoặc sáng ≥8" vẫn giữ.
3. Bỏ "mỗi khu một họ màu"; khu hiện bằng chữ ở dòng phụ.
4. Ngoại thành giữ xám.

## Bước 5: Cập nhật PyloS
1. `region_map.py`: bỏ pos và màu HSL của 12 toà nội thành, giữ 4 vùng ngoại thành; sinh lại regions.json.
2. Sửa `tests/lobby/atlas/test_region_map.py`.
3. Cập nhật `region_map_redesign.md` và mục graphify trong `CLAUDE.md`.

## Bước 6: Kiểm thử
Test mới (44 test cũ phải qua): trung tâm gần tâm khối; hue tăng theo vòng; hai vùng kề cách ≤ gap + 2×margin; không vùng nào đè nhau; cỡ chữ màn hình không đổi theo scale. Rồi `install.py`, `graphify update .`, đo bằng JS (nhìn đẹp hay không do owner xem).

## Giả định
- Màu theo vòng thay màu theo khu.
- Trung tâm tự động theo luồng gọi; nếu lệch ý owner thì ghi cố định bằng `center`.

## Đã làm (6-11-2026)
- graphify-regions: `layout.plan_city` (xếp theo vòng + kéo sát, ngoại thành thành hàng dưới), `zoning.closeness_order`/`auto_colors` (màu nóng→lạnh theo vòng), nhãn vẽ cỡ chữ cố định trên màn hình, 47 test qua.
- PyloS: 11 toà nội thành bỏ `pos`/`color` trong `region_map.py`; `regions.json` sinh lại.
- Kết quả thật: tâm tự chọn là `lobby/dispatch` + `gate/side_gate`. Khoảng hở các vùng 24 (trước 60). Chưa xem bằng mắt.
