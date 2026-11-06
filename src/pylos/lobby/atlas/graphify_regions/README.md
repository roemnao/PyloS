# graphify-regions

Vẽ `graph.html` của graphify thành **bản đồ vùng**: màu theo vùng, hình theo loại code, viền nét đứt theo cộng đồng,
biên lãnh thổ ôm sát nút, đường mặc định mờ, nút `?` mở chú thích. Chạy ngay trong `graphify update .`, `graphify export html`
và hook `post-commit` (cả ba đi qua `to_html`).

## Cài / cài lại (sau mỗi `uv tool upgrade graphifyy`)

    python src/pylos/lobby/atlas/graphify_regions/install.py
    python src/pylos/lobby/atlas/graphify_regions/uninstall.py     # gỡ

Đã thử với graphify **0.9.100**. Phần sửa nằm trong `...\graphifyy\Lib\site-packages\graphify\regions\` và 8 dòng trong
`exporters\html.py`. **Không sửa tay trong site-packages**: sửa ở đây rồi chạy lại `install.py`.

## Cấu hình dự án (`<gốc>/.graphifyrc`)

    regions.mode=off           # không vẽ vùng
    regions.file=path/to.json  # file phân vùng (định dạng dưới đây)
    regions.depth=2            # chia theo n cấp thư mục (mặc định 2)

Thứ tự chọn cách chia: `regions.file` -> `graphify-regions.json` ở gốc dự án -> thư mục -> (dự án phẳng) cộng đồng graphify.
Lỗi ở bất kỳ bước nào: graphify vẫn ghi `graph.html` gốc và in một dòng `[graphify regions] bỏ qua: ...`.

## File phân vùng (version 1)

    {"version": 1,
     "levels": {"group": "Khu", "region": "Toà"},
     "groups":  [{"id": "gate", "name": "Khu cổng"}],
     "regions": [{"id": "gate/fence", "name": "Hàng rào", "group": "gate", "color": [188, 65, 48], "pos": [-1.5, -0.1]}],
     "files":   {"src/x/fence.py": "gate/fence"},
     "unplaced_region": "...", "external_region": "...", "tests_region": "..."}

Thay (hoặc thêm vào) `files` có thể dùng `"rules": [{"prefix": "src/x/fence/", "region": "gate/fence"}]`: tiền tố đường dẫn dài nhất thắng,
`files` (từng file) thắng `rules`. Chỉ `version`, `regions[].id` và `files` hoặc `rules` là bắt buộc. Thiếu `color`/`pos` thì tự tính (màu theo nhóm, vị trí theo luồng gọi).

## Khi graphify đổi mẫu graph.html

chạy bộ test đầy đủ ở `C:\Users\tp\graphify-regions\tests` (cần python của uv tool: `...\uv\tools\graphifyy\Scripts\python.exe -m pytest tests`;
nó giữ mẫu `backup/graph.<phiên bản>.html` của graphify) để biết thiếu mốc nào, rồi sửa bảng mốc trong `regions/inject.py`.
Bản trong PyloS là bản gốc của mã; thư mục `C:\Users\tp\graphify-regions` chỉ còn giữ test nặng và bản sao lưu của graphify.
