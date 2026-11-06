# PyloS — Kế hoạch dựng "Thành chính"

> Tổng hợp từ trắc nghiệm vòng 1, vòng 2 và những gì đã đọc trong repo (`src/bot/`, `docs/vps-dieu-khien.md`, `pyproject.toml`, `scripts/packaging/`, `tests/`).
> Vòng 3 **chưa trả lời**, nên các chỗ đó ghi rõ ở **Giai đoạn 0** kèm "mặc định tạm" mà kế hoạch đang dùng. Bạn trả lời vòng 3 xong thì mình sửa lại các bước bị ảnh hưởng.
> File kế hoạch này viết tiếng Việt để bạn đọc. Mọi tài liệu và thư mục **thuộc PyloS** tạo ra theo kế hoạch đều bằng **tiếng Anh, snake_case** (vòng 1 câu 5, vòng 2 B2).

---

## 1. Đích đến (tóm tắt cấu trúc đã chốt)

```
src/pylos/                         ← Thành chính (tên gói: xem C2 ở Giai đoạn 0)
├── management/                    Khu quản lý
│   ├── owner/                     Toà Owner — bot không được vào (lọc đường dẫn bằng code)
│   │   ├── admin_web/             trang quản trị web (đang là ui/admin)
│   │   ├── owner_log/  private_plans/
│   └── managers/                  Toà quản lý — bot quản lý đọc
│       ├── guidelines/  bot_commands/  plans/  evaluations/  reports/  bot_list/
├── gate/                          Khu cổng
│   ├── main_gate/                 zalo/  external_apps/  external_bots/  sessions/  logs/
│   ├── fence/                     token_limit/  speech_limit/  ethics/
│   ├── side_gate/                 vps/  cron?/  mcp/  owner_commands/  shell/  emergency/  desktop/
│   └── guest_house/               hut/<zaloUid hoặc groupId>/  (repo, kết nối GitHub, lịch/việc, hồ sơ, file)
├── lobby/                         Khu đại sảnh
│   ├── library/                   tài liệu/skill owner duyệt
│   ├── atlas/                     bản đồ (script sinh khung + ghi chú tay)
│   ├── dispatch/                  bus, đồng hồ, sổ đăng ký bot, hàng đợi, log phong bì, quyền hạn, lập lịch, start/stop
│   └── office/                    plugin (vẽ, docx, code) + warehouse/ (nhà kho file tạo ra)
└── residential/                   Khu dân cư
    └── residents/<bot>/           workspace/  persona/  bookshelf/  memory/{muscle,short_term,long_term,archive}/
```

Luật nền đã chốt:
- Mọi luồng **liên khu** đi qua Đại sảnh (bus). Đại sảnh chỉ đọc phong bì. Bot ↔ bot cùng khu dân cư: tính sau khi có ≥2 bot.
- Khẩn cấp (Cổng chính → Cổng phụ) được đi tắt, ghi log song song vào Đại sảnh, không qua Hàng rào.
- Mặc định MỞ trong nội thành; cấm: Toà Owner, nhà bot khác, túp lều không phải của người đang được phục vụ.
- Thông tin gắn với một người **chỉ** nằm trong túp lều của người đó, không nằm trong trí nhớ bot.
- Toà mới: người/Claude Code tạo được, ghi vào Bản đồ, báo owner. **Khu mới: phải hỏi owner.**
- Hiện chỉ **1 bot**, chừa sẵn chỗ cho nhiều bot (mỗi bot một process về sau).

---

## 2. Những thứ đang buộc vào đường dẫn hiện tại (đọc từ repo)

Đây là các điểm sẽ **gãy** nếu dời code mà không cẩn thận:

| # | Chỗ buộc | Ở đâu | Gãy thế nào |
|---|---|---|---|
| P1 | VPS chạy `python -m bot run`, `PYTHONPATH=/opt/pylos/src` | `pylos-bot.service` (root cài, `em`/`pylos` không sửa được) | Đổi tên gói `bot` → bot không lên sau lần cập nhật tự động |
| P2 | `pylos-update` (+ `.timer`) = `git pull` từ `main` + khởi động lại | VPS | **Merge vào `main` = triển khai lên VPS ngay**, không có bước duyệt |
| P3 | Windows chạy `python -m bot gui`, cài `pip install -e` | `ZaloBot.cmd`, `auto_update.py` | Gói mới có thể không import được nếu bản cài editable cũ chưa cài lại |
| P4 | ZaloBot.exe: `collect_submodules("bot")`, `collect_data_files("bot")`, điểm vào `bot.command_line` | `scripts/packaging/ZaloBot.spec`, `zalobot_entry.py` | Gói mới không được đóng vào exe → exe lỗi thiếu module |
| P5 | `package-data`: `bot = ["ui/admin/static/*", "templates/*"]` | `pyproject.toml` | Dời `ui/admin/static` hoặc `templates` → trang quản trị/mẫu thiếu file khi cài |
| P6 | `zalo-bot = "bot.cli:main"` nhưng repo **không có** `bot/cli.py` (chỉ có `command_line.py`) | `pyproject.toml` | Lỗi sẵn có: lệnh `zalo-bot` không chạy được |
| P7 | Bố cục `userdata/` (config, data, system), file chờ `standby.txt`, khoá tiến trình, gói chuyển máy↔VPS | `userdata_paths.py`, `handover.py`, `bot_process.py` | Đổi đường dẫn dữ liệu → mất dữ liệu, chạy 2 bot cùng lúc, chuyển máy lỗi |
| P8 | Test ghi cứng đường dẫn (`src/bot/system/...`) và `monkeypatch` theo tên module (`"bot.core.x..."`) | `tests/` | Dời module → test sai/bỏ sót mà vẫn xanh |

---

## 3. Nguyên tắc làm (áp cho mọi giai đoạn)

1. **Mỗi bước = một nhánh + một PR.** Chỉ merge vào `main` khi test qua hết, vì merge `main` là VPS tự kéo về ngay (P2).
2. **Dời module kiểu "để lại biển chỉ đường"**: dời file sang chỗ mới, chỗ cũ để một file mỏng `from pylos... import *`. Import cũ vẫn chạy. Gỡ biển chỉ đường ở giai đoạn cuối.
3. **Không đổi lối vào `python -m bot run` / `python -m bot gui`** cho đến khi có quyết định khác (C1). Như vậy không cần root sửa service.
4. **Không đổi vị trí dữ liệu thật trong `userdata/`** nếu bước đó không phải bước chuyển dữ liệu. Bước chuyển dữ liệu luôn sao lưu trước, chạy lại được nhiều lần không hỏng (kiểu `migrate_legacy()` đang có).
5. Tên gói **chữ thường** (`pylos`), vì Windows không phân biệt hoa thường còn Linux (VPS) thì có.
6. Mỗi lần thêm/dời file: cập nhật Bản đồ (`atlas`). Có test kiểm Bản đồ khớp thư mục thật.

---

## 4. Giai đoạn 0 — Chốt các quyết định còn mở (vòng 3)

Kế hoạch đang dùng "mặc định tạm" ở cột 3. Đổi đáp án thì các bước ở cột 4 phải sửa.

| Câu | Nội dung | Mặc định tạm | Ảnh hưởng bước |
|---|---|---|---|
| A1 | Mã start/stop ở `dispatch` hay `side_gate` | `dispatch` quyết định; thao tác hệ điều hành (systemctl, process) ở `side_gate` | 5.4, 6.3 |
| A2 | Căn hộ `cron` ở Cổng phụ? | Lịch hệ thống ở `dispatch`; lịch riêng bot ở căn hộ bot; bỏ `side_gate/cron` | 3.1, 5.3 |
| A3 | "Người lạ" là ai | Túp lều tạo ngay, đánh dấu "chưa duyệt", bị giới hạn tin/phút đến khi owner duyệt | 9 (backlog) |
| A4 | Bot khác vào túp lều | Hoãn đến khi có ≥2 bot | 7.3 |
| A5 | Trong nhóm có đọc túp lều cá nhân | Không; trong nhóm chỉ dùng túp lều nhóm | 6.5, 7.3 |
| A6 | Ngắn hạn và dữ liệu gắn người | Phần gắn người ghi thẳng vào túp lều; ngắn hạn chỉ giữ phần đã bỏ danh tính | 7.2, 9 |
| A7 | Khoá bí mật | Giữ `userdata/config/settings.env` như cũ; `owner/` chỉ chứa mô tả | 8.1 |
| B1 | Công nghệ bus | Giao diện bus + bản chạy trong cùng process; SQLite khi có ≥2 process | 5.2 |
| B2 | Bước sau tài liệu | Dời Khu đại sảnh trước | thứ tự giai đoạn |
| B3 | Trễ chấp nhận được | < 1 giây | 5.2 |
| C1 | Lối vào bot | Giữ `python -m bot run` (biển chỉ đường) | 4.x, toàn bộ |
| C2 | Tên/vị trí gói gốc | `src/pylos/` | 4.1 |
| C3 | `userdata/` | Để nguyên chỗ, ánh xạ qua lớp đường dẫn | 6.5, 7.x |
| C4 | Chuyển máy khác phiên bản | Chặn nếu khác phiên bản cấu trúc | 3.4 |
| C5 | Kiểm trước khi lên VPS | Chạy thử Windows + test mô phỏng khởi động lại + owner duyệt | mọi PR |
| C6 | Cập nhật làm bot không lên | `pylos-update` tự quay về commit trước + báo owner qua Zalo | 3.3 |
| D1/D2 | Bot quản lý | Làm sau khi cấu trúc xong, trước bot dân cư thứ 2 | 9 |
| E1 | Lệnh nguy hiểm qua Zalo | `shell`/lệnh phá huỷ chỉ chạy từ trang quản trị web | 6.3 |
| E2 | Script trong skill | Cơ bắp chỉ chứa văn bản; script chỉ chạy nếu thuộc Thư viện đã duyệt, qua Toà văn phòng | 9 |
| E3 | Khoá phần quy tắc persona | Quy tắc nằm ngoài căn hộ bot, nạp vào prompt khi chạy | 7.1 |
| E4 | Hạn nâng quyền tạm | Gắn với nhiệm vụ, xong thì thu hồi | 9 |
| F1 | Vị trí test | `tests/` ngoài cùng, cấu trúc phản chiếu Thành | 8.3 |

**Xong khi:** bạn trả lời vòng 3, mình sửa bảng này và các bước bị ảnh hưởng.

**Lỗi có thể xảy ra**
- Bắt tay làm khi chưa chốt A1/C1/C2 → phải dời code hai lần. *Phòng:* Giai đoạn 1 (chỉ tài liệu) và 2 (lưới an toàn) không phụ thuộc các câu này, làm trước được; từ Giai đoạn 3 trở đi chờ chốt.

---

## 5. Giai đoạn 1 — Chỉ tài liệu (không dời code)

Theo vòng 1 câu 42-A, vòng 2 H6-A, H5-A (ưu tiên "tìm file dễ").

| Bước | Việc | Ai làm |
|---|---|---|
| 1.1 | Viết `docs/architecture/city.md` (tiếng Anh): khu, toà, căn hộ, luật truy cập, luồng dữ liệu, bảng thuật ngữ Việt ↔ Anh | Claude |
| 1.2 | Viết `docs/architecture/atlas.md`: bảng **"file hiện tại → toà đích"** cho toàn bộ `src/bot/` (theo bảng gán vòng 2 H3), đánh dấu file chưa có chỗ | Claude |
| 1.3 | Script `scripts/atlas.py`: quét repo, sinh khung bản đồ, giữ phần ghi chú tay (vòng 1 câu 28-C); lệnh `--check` báo file chưa có trong bản đồ | Claude |
| 1.4 | Viết `CLAUDE.md` ở gốc repo (Claude Code luôn đọc): file mới đặt ở đâu, phải cập nhật Bản đồ, snake_case + tiếng Anh, không đổi lối vào `python -m bot`, không tự thêm khu, merge `main` = lên VPS | Claude |
| 1.5 | Owner đọc và duyệt 1.1–1.4 | Owner |

**Xong khi:** mở `atlas.md` tìm được mọi file `src/bot/` sẽ về toà nào; `python scripts/atlas.py --check` không báo thiếu.

**Lỗi có thể xảy ra**
- **Bản đồ lệch thực tế** sau vài lần sửa code. *Phòng:* test gọi `atlas.py --check` chạy cùng `pytest`, lệch là đỏ.
- **`CLAUDE.md` quá dài**, Claude đọc lướt bỏ sót luật. *Phòng:* giữ dưới ~80 dòng, luật quan trọng nhất ở đầu, chi tiết để ở `city.md`.
- **Mâu thuẫn với tài liệu cũ** (`docs/PLAN.md`, `KE-HOACH-...` tiếng Việt). *Phòng:* `city.md` ghi rõ là nguồn chuẩn cho cấu trúc; tài liệu cũ giữ nguyên làm lịch sử, chuyển dần vào `managers/plans` ở Giai đoạn 8.
- File chưa có chỗ trong bảng gán (vd `command_line.py`, `config.py`, `roles.py`, `log_files.py`, `first_run_setup.py`, `remote_server` vs `server_client`). *Phòng:* liệt kê ở mục "chưa xếp" trong `atlas.md` để owner chọn, không tự đoán.
- Merge PR tài liệu vào `main` cũng kích hoạt cập nhật VPS. *Phòng:* vô hại (không đổi code), nhưng vẫn kiểm VPS lên lại bình thường sau merge.

---

## 6. Giai đoạn 2 — Lưới an toàn (trước khi động vào code)

Mục tiêu: bất kỳ bước dời code nào làm gãy VPS/Windows/exe thì **test đỏ trước khi merge**, và nếu lọt lên VPS thì **tự quay về**.

| Bước | Việc | Ai làm |
|---|---|---|
| 2.1 | Ghi mốc: chạy `pytest` đầy đủ (`pip install -e ".[dev,desktop,personal]"`), ghi số test qua/bỏ qua; ghi commit đang chạy trên VPS | Claude |
| 2.2 | Test "lối vào còn sống": `python -m bot run --help`/`gui --help` chạy được trong process con; `import bot.command_line`; mọi module dưới `src/` import được | Claude |
| 2.3 | Test "đóng gói": file trong `package-data` (static, templates) tồn tại; mọi gói con nằm trong vùng `collect_submodules` của `ZaloBot.spec` | Claude |
| 2.4 | Sửa lỗi sẵn có P6: `zalo-bot = "bot.cli:main"` → `bot.command_line:main` | Claude |
| 2.5 | **Đọc** (không sửa) unit `pylos-update.service`/`.timer` trên VPS qua SSH user `em` để biết nó chạy script nào | Claude, cần bạn cho phép |
| 2.6 | Thêm kiểm sức khoẻ sau cập nhật: bot không lên trong N giây → quay về commit trước + báo owner (C6). Nếu script cập nhật nằm trong repo thì làm qua git; nếu nằm cứng trong unit thì cần root | Claude (+ root nếu cần) |
| 2.7 | Ghi "phiên bản cấu trúc" vào manifest gói chuyển máy↔VPS; bên nhận khác phiên bản thì từ chối (C4) | Claude |
| 2.8 | Test Windows editable: cài `pip install -e` trên bản cũ, thêm một gói mới dưới `src/`, kiểm import được không; nếu không, sửa `auto_update.py` cài lại khi `pyproject.toml` đổi | Claude |

**Xong khi:** các test mới chạy xanh trên bản hiện tại; thử cố ý đổi tên một module → test đỏ; VPS có cơ chế tự quay về (hoặc ghi rõ việc root phải làm).

**Lỗi có thể xảy ra**
- **`pylos-update` nằm hẳn trong file unit** (root sở hữu) → không thêm kiểm sức khoẻ qua git được. *Xử lý:* viết sẵn đoạn unit mới + hướng dẫn cho root, giống `docs/vps-dieu-khien.md` đang làm.
- **Tự quay về chạy vòng lặp**: commit cũ cũng lỗi (vd do cấu hình), quay qua quay lại mãi. *Phòng:* chỉ quay về một lần, ghi cờ, lần sau dừng hẳn và báo owner.
- **Quay về nhưng dữ liệu đã đổi bố cục** (bước chuyển dữ liệu chạy rồi) → bản cũ không đọc được dữ liệu mới. *Phòng:* bước chuyển dữ liệu luôn giữ bản sao lưu và chỉ chạy sau khi bot đã lên ổn định; bản cũ gặp phiên bản dữ liệu mới thì vào chế độ chờ thay vì ghi đè.
- **Test `--help` khởi động thật** (đụng Zalo, mở cổng mạng). *Phòng:* kiểm bằng import + phân tích tham số, không gọi vòng chạy chính.
- **Máy chạy test thiếu nhóm thư viện** (`desktop`, `personal`) → test đỏ giả (đã gặp với `pillow`). *Phòng:* test cần thư viện tuỳ chọn thì tự bỏ qua khi thiếu, ghi lý do.
- **SSH vào VPS đụng chỗ không được đụng.** *Phòng:* chỉ đọc file unit, không sửa, đúng phạm vi user `em`.

---

### Kết quả bước 2.5 (đã đọc VPS qua `ssh pylos-vps`, 2026-11-05)

- `pylos-update.service` chỉ gọi `/usr/local/bin/pylos-update` (root sở hữu, **nằm ngoài repo**): `git fetch` → `merge --ff-only` → cài lại thư viện **chỉ khi `pyproject.toml` đổi** → restart `pylos-admin`/`pylos-bot` nếu đang chạy. **Không có kiểm sức khoẻ, không có tự quay về.** Timer 10 phút.
- Hệ quả cho 2.6: không thêm được tự quay về qua git; cần root sửa script. Việc phải làm của chủ VPS, mình sẽ viết sẵn đoạn script mới.
- `pylos-admin` chạy `python -m bot admin run` (PYTHONPATH `/opt/pylos/src`) → lối vào `bot` đúng là thứ VPS đang dùng, giữ nguyên (C1).
- `pylos-bot.service` **chưa cài** trên VPS, bot đang tắt; `userdata/system` có `bot.lock`, `bot.pid`, `handover_backups/`.
- Sửa `pyproject.toml` (lệnh `zalo-bot`) sẽ làm lần cập nhật kế tiếp chạy `uv pip install -e` một lần: vô hại nhưng là tác động thật khi merge.

## 7. Giai đoạn 3 — Dựng khung rỗng của Thành

| Bước | Việc |
|---|---|
| 3.1 | Tạo `src/pylos/` với đủ khu/toà/căn hộ như mục 1 (mỗi thư mục là gói Python có `__init__.py` rỗng) |
| 3.2 | Mỗi toà có `README.md` tiếng Anh: chứa gì, không chứa gì, ai được đọc/ghi |
| 3.3 | Thêm `pylos` vào `ZaloBot.spec` (`collect_submodules`/`collect_data_files`) và `package-data` nếu toà có file không phải `.py` |
| 3.4 | Cập nhật `atlas.md` (khung thật đã có), test kiểm cấu trúc: đủ 4 khu, các toà đã chốt, tên snake_case |

**Xong khi:** `import pylos.lobby.dispatch` chạy được trên Windows, VPS (Linux) và trong exe; mọi test cũ vẫn xanh.

**Lỗi có thể xảy ra**
- **Hoa/thường**: đặt `PyloS` thì Windows import được, Linux không → VPS gãy. *Phòng:* chữ thường + test kiểm tên.
- **Exe build xong thiếu `pylos`** vì quên spec. *Phòng:* bước 2.3 bắt lỗi; build thử exe một lần ở bước này.
- **Thư mục rỗng không vào git** (git không lưu thư mục rỗng). *Phòng:* mỗi căn hộ có `__init__.py` hoặc `README.md`.
- **Đường dẫn quá dài trên Windows** (giới hạn 260 ký tự) khi lồng sâu `residential/residents/<bot>/memory/short_term/...` cộng thêm đường dẫn cài đặt. *Phòng:* tên căn hộ ngắn, kiểm độ dài đường dẫn dài nhất trong test.
- **Trùng tên với gói khác**: `pylos` trùng thư viện ngoài nào đó. *Phòng:* kiểm `pip show pylos` / PyPI trước khi chốt.

---

## 8. Giai đoạn 4 — Khu đại sảnh (làm đầu tiên)

| Bước | Việc | Rủi ro |
|---|---|---|
| 4.1 | Dời `core/vietnam_time.py` → `lobby/dispatch/clock`, `storage/process_lock.py` → `lobby/dispatch/` (để biển chỉ đường ở chỗ cũ) | thấp |
| 4.2 | Dựng **bus**: kiểu `Envelope` (người gửi, người nhận, loại, mã, thời gian) + giao diện `Bus`; bản đầu chạy trong cùng process; log phong bì (không log nội dung) | trung bình |
| 4.3 | Sổ đăng ký bot (bot nào đang chạy/ngủ, ở căn hộ nào) + quyền hạn (dời `core/roles.py`) vào `dispatch` | trung bình |
| 4.4 | Dời `agent/tools/*` → `lobby/office/`; tạo `office/warehouse/` cho file tạo ra (vòng 2 C6) | trung bình |
| 4.5 | Dời script bản đồ vào `lobby/atlas/`; tạo `lobby/library/` (README + quy tắc owner duyệt nguồn ngoài) | thấp |
| 4.6 | **Cuối cùng** mới dời `system/handover*.py`, `system/auto_update.py` vào `dispatch` | **cao** (đụng VPS, chuyển máy) |
| 4.7 | Cho luồng tin Zalo → bot → Zalo đi qua bus (lúc này vẫn một process) | trung bình |

**Xong khi:** tin nhắn thật đi qua bus và trả lời bình thường; log phong bì có ở Đại sảnh; cập nhật tự động VPS + chuyển máy↔VPS vẫn chạy.

**Lỗi có thể xảy ra**
- **Khoá tiến trình đổi chỗ** giữa hai phiên bản → lúc cập nhật, bản cũ và bản mới không thấy khoá của nhau → **2 bot cùng chạy một tài khoản Zalo**. *Phòng:* dời code nhưng giữ nguyên đường dẫn file khoá trong `userdata/system/`.
- **`monkeypatch` trong test trỏ vào biển chỉ đường** chứ không phải module thật → test vẫn xanh mà không kiểm gì. *Phòng:* mỗi lần dời, tìm `"bot.` trong `tests/` và đổi mục tiêu patch sang chỗ mới trong cùng PR.
- **Vòng import** (dispatch ↔ core ↔ agent) khi tách. *Phòng:* `dispatch` không import ngược từ khu khác; thứ dùng chung đặt ở `dispatch`.
- **Tool không được agent nhận** sau khi dời `agent/tools` (agent tìm tool theo đường dẫn/tên module, kèm `custom_tools` người dùng tự viết trong `userdata`). *Phòng:* test "danh sách tool agent thấy" trước/sau phải giống nhau; tool tự viết vẫn đọc ở chỗ cũ.
- **Bus nuốt tin hoặc gửi trùng** khi lỗi giữa chừng. *Phòng:* mỗi phong bì có mã; giữ cơ chế `processed_message_ids.txt` để chặn trả lời lặp; test lỗi giữa chừng.
- **Chậm** vì thêm lớp bus. *Phòng:* đo thời gian thêm vào mỗi tin, đặt ngưỡng (B3) trong test.
- **Dời `handover`/`auto_update` làm hỏng chuyển máy hoặc cập nhật** (thứ bạn lo nhất). *Phòng:* làm sau cùng trong giai đoạn, PR riêng, chạy thử chuyển máy↔VPS thật trước khi merge, có 2.6 để tự quay về.
- **Tên logger đổi** (`logging.getLogger(__name__)` theo tên module mới) → trang Log/bộ lọc log theo tên cũ không thấy dòng. *Phòng:* kiểm trang Log sau mỗi lần dời.

---

## 9. Giai đoạn 5 — Khu cổng

| Bước | Việc |
|---|---|
| 5.1 | `zalo/*` → `gate/main_gate/zalo/`; `system/log_files.py` → `main_gate/logs/` (dữ liệu log vẫn ở `userdata/system/logs`) |
| 5.2 | `core/message_filter.py`, `rate_limiter.py`, `text_fold.py` → `gate/fence/` chia `token_limit/ speech_limit/ ethics/`; Hàng rào kiểm **cả chiều vào lẫn chiều ra**, vi phạm thì chặn + báo |
| 5.3 | `core/owner_commands.py`, `system/remote_server.py`, `server_client.py` → `gate/side_gate/`; tạo căn hộ `vps/ mcp/ owner_commands/ shell/ emergency/` |
| 5.4 | Phần thao tác hệ điều hành của `bot_process.py` (systemctl, chạy/dừng process) → `side_gate`; phần quyết định → `dispatch` (theo A1) |
| 5.5 | `ui/desktop` → `side_gate/desktop` (vòng 2 H4) |
| 5.6 | Đường khẩn cấp: Cổng chính → Cổng phụ đi tắt, ghi log song song vào Đại sảnh |

**Xong khi:** Zalo cá nhân + Bot Platform + polling + webhook chạy như cũ; lệnh owner qua Zalo chạy; Hàng rào chặn được ở cả hai chiều.

**Lỗi có thể xảy ra**
- **Phiên Zalo cá nhân mất** (đường dẫn `zalo_login_session.json` đổi) → phải quét QR lại, trên VPS phiền vì Zalo có thể đòi đăng nhập lại khi đổi IP. *Phòng:* không đổi đường dẫn file phiên.
- **Webhook** gắn với một địa chỉ cố định; đổi đường dẫn route → Zalo gửi vào chỗ không tồn tại. *Phòng:* giữ nguyên URL route, chỉ dời code xử lý.
- **Hàng rào chiều ra chặn nhầm** câu trả lời bình thường → người dùng nhận lỗi thay vì câu trả lời. *Phòng:* chạy ở chế độ "chỉ ghi log, không chặn" một thời gian, xem log rồi mới bật chặn.
- **Lệnh owner/khẩn cấp đi tắt bị ai đó giả** — hiện chỉ dựa vào đúng tài khoản Zalo (vòng 2 G1-A). *Phòng:* xem E1 ở Giai đoạn 0; ít nhất `shell` không chạy từ Zalo.
- **Trang quản trị VPS (proxy `/api/remote/*`) gãy** vì `remote_server`/`server_client` đổi chỗ. *Phòng:* test proxy đang có (`test_remote_proxy.py`) phải xanh; thử thật công tắc "Máy này | VPS".
- **Test `test_no_web_coupling.py` ghi cứng `src/bot/system/...`** → đỏ hoặc mất tác dụng. *Phòng:* sửa test quét cả `src/pylos/`.

---

## 10. Giai đoạn 6 — Toà khách và túp lều (chuyển dữ liệu — rủi ro cao nhất)

| Bước | Việc |
|---|---|
| 6.1 | Lớp đường dẫn `hut_path(zalo_uid | group_id)` ánh xạ vào `userdata/data/huts/<id>/` (C3: dữ liệu vẫn trong `userdata`) |
| 6.2 | Liệt kê dữ liệu nào là của từng người: lịch/việc, hồ sơ, `memorydata` theo cuộc trò chuyện, file gửi/tạo, repo + kết nối GitHub |
| 6.3 | Viết bước chuyển dữ liệu: sao lưu → chép vào túp lều → kiểm đủ → mới xoá chỗ cũ; chạy lại nhiều lần không hỏng; ghi phiên bản dữ liệu |
| 6.4 | Túp lều tự tạo ở tin nhắn đầu tiên; nhóm có túp lều riêng |
| 6.5 | Lọc quyền: bot chỉ vào túp lều của người đang được phục vụ (trong nhóm: chỉ túp lều nhóm — A5) |
| 6.6 | Cập nhật gói chuyển máy↔VPS để mang theo `huts/` |

**Xong khi:** mọi người dùng cũ còn nguyên lịch/việc/ghi nhớ; chuyển máy↔VPS mang theo túp lều; bot ở chat của A không đọc được dữ liệu của B.

**Lỗi có thể xảy ra**
- **Mất dữ liệu người dùng** khi chuyển. *Phòng:* sao lưu trước (như `handover_backups/`), chỉ xoá chỗ cũ sau khi kiểm đủ, có lệnh khôi phục.
- **Gán nhầm dữ liệu sang túp lều người khác** (mã cuộc trò chuyện ≠ zaloUid, nhất là nhóm và chat riêng trộn lẫn). *Phòng:* test với dữ liệu mẫu có cả nhóm và chat riêng; mục không xác định được chủ thì để riêng chờ owner xem, không đoán.
- **Hai máy (Windows và VPS) khác phiên bản dữ liệu** khi chuyển bot. *Phòng:* 2.7 chặn chuyển khi khác phiên bản.
- **Web bot lịch** đang gửi kèm `zaloUid` (commit `a705ae9`) — đổi chỗ lưu lịch/việc mà quên phía web → lịch hiển thị trống. *Phòng:* giữ nguyên định dạng API với web, chỉ đổi chỗ lưu phía PyloS.
- **Rò dữ liệu**: lớp lọc chỉ chặn công cụ file của bot, còn code hệ thống vẫn đọc được tất cả (đúng thiết kế). *Phòng:* `city.md` ghi rõ luật áp cho **bot (công cụ do LLM gọi)**, không áp cho code hệ thống; test lọc quyền cho từng loại truy cập.
- **Repo người dùng clone vào túp lều** nặng, đầy ổ VPS. *Phòng:* giới hạn dung lượng mỗi túp lều; không đưa repo vào gói chuyển máy.

---

## 11. Giai đoạn 7 — Khu dân cư

| Bước | Việc |
|---|---|
| 7.1 | `agent/*` (gemini_agent, system_prompt) → `residential/residents/<bot>/`; persona chia **giọng văn/thói quen** (bot tự sửa được, trong căn hộ) và **quy tắc** (nằm ngoài căn hộ, nạp vào prompt — E3) |
| 7.2 | Tạo `memory/{muscle,short_term,long_term,archive}/`, `bookshelf/`, `workspace/`; chuyển `workspace/SYSTEM.md`, `MEMORY.md` hiện có vào đúng chỗ; dữ liệu gắn người → túp lều (A6) |
| 7.3 | Lọc đường dẫn ở lớp công cụ file của bot: chặn `management/owner`, nhà bot khác, túp lều không phải người đang phục vụ (vòng 2 A3-B) |
| 7.4 | Bot vẫn là **một process** như hiện nay; tách process riêng khi có bot thứ 2 (vòng 2 H2-B) |

**Xong khi:** bot trả lời như cũ, tính cách và ghi nhớ cũ còn nguyên; thử bảo bot đọc file trong `owner/` thì bị từ chối bằng code.

**Lỗi có thể xảy ra**
- **Bot "mất trí nhớ" hoặc đổi tính cách** vì `SYSTEM.md`/`MEMORY.md` không được nạp từ chỗ mới. *Phòng:* so prompt hệ thống trước/sau dời phải giống hệt.
- **Tách quy tắc ra khỏi persona làm prompt khác thứ tự** → bot cư xử khác. *Phòng:* như trên, so prompt.
- **Lọc đường dẫn bị lách** bằng `..`, symlink, đường dẫn tuyệt đối, chữ hoa/thường trên Windows. *Phòng:* chuẩn hoá đường dẫn (`resolve()`) trước khi so; test các kiểu lách.
- **Dữ liệu gắn người lọt vào `MEMORY.md` cũ** (đang chứa ghi nhớ chung, có thể lẫn thông tin cá nhân). *Phòng:* owner xem lại `MEMORY.md` trước khi chuyển; phần cá nhân tách sang túp lều bằng tay.

---

## 12. Giai đoạn 8 — Khu quản lý, dọn dẹp, chốt

| Bước | Việc |
|---|---|
| 8.1 | `ui/admin` → `management/owner/admin_web/` (sửa `package-data` cho static); `owner/` thêm `owner_log/`, `private_plans/`; khoá bí mật theo A7 |
| 8.2 | `managers/`: `guidelines/ bot_commands/ plans/ evaluations/ reports/ bot_list/`; chuyển `docs/` cũ vào `managers/plans` (kế hoạch) và `lobby/library` (hướng dẫn) |
| 8.3 | Sắp `tests/` phản chiếu cấu trúc Thành (F1) |
| 8.4 | Gỡ toàn bộ biển chỉ đường; giữ duy nhất lối vào `bot` (`python -m bot run/gui`) nếu C1-A |
| 8.5 | `atlas.md` bản cuối; `CLAUDE.md` cập nhật; build thử exe; chạy thử chuyển máy↔VPS lần cuối |

**Xong khi:** `src/bot/` chỉ còn lối vào mỏng; mọi file có trong Bản đồ; test, exe, VPS, chuyển máy đều chạy.

**Lỗi có thể xảy ra**
- **Trang quản trị thiếu CSS/JS/font** sau khi dời `static/` (P5). *Phòng:* test 2.3; mở trang thật trên cả máy này và VPS (sau nginx).
- **Gỡ biển chỉ đường quá sớm** → import cũ còn sót ở chỗ ít chạy (vd lệnh hiếm dùng, exe). *Phòng:* tìm toàn repo import cũ trước khi gỡ; test 2.2 import mọi module.
- **Đăng nhập Google của trang quản trị gãy** (đường dẫn callback, `ADMIN_PUBLIC_URL`). *Phòng:* không đổi route, chỉ dời code; thử đăng nhập thật.
- **Liên kết trong tài liệu cũ chết** sau khi dời `docs/`. *Phòng:* để lại `docs/README.md` trỏ sang chỗ mới.

---

## 13. Sau khi có cấu trúc (backlog tính năng, chưa lên lịch)

Không thuộc việc dựng cấu trúc, nhưng đã bàn trong trắc nghiệm. Mỗi mục làm thành kế hoạch riêng khi tới lượt.

| Tính năng | Phụ thuộc | Lỗi đáng lo nhất |
|---|---|---|
| Hạn mức token toàn hệ thống/tháng, cảnh báo 80%/100%, chạm 100% dừng trừ lệnh owner + khẩn cấp | Hàng rào (5.2) | Đếm sai token → dừng nhầm giữa tháng hoặc vượt hạn mức |
| Chống spam cho người "chưa duyệt" (A3) | Túp lều (6.4) | Chặn nhầm người dùng thật |
| Hệ trí nhớ: ngắn hạn → "mơ" (đêm / khi rảnh / đầy ngưỡng; script + LLM) → dài hạn → kho lưu trữ | Khu dân cư (7.2) | "Mơ" tốn token, chạy chồng lên giờ cao điểm; gộp nhầm làm sai kiến thức |
| Cơ bắp tự sửa hàng tuần, quản lý chấm, điểm giảm thì hoàn lại | Bot quản lý | Tự sửa làm bot kém đi mà điểm chưa kịp phản ánh |
| Kệ sách: bản sao có phiên bản, cảnh báo khi Thư viện có bản mới | Thư viện (4.5) | Skill ngoài chứa chỉ dẫn độc hại (owner phải đọc trước — vòng 2 F3-A) |
| Bot quản lý (1 bot: quản lý file + các bot khác) | Cấu trúc xong | Quyền quá rộng; nó cũng bị lọc đường dẫn như bot khác trừ Toà quản lý |
| Bus thật giữa nhiều process (SQLite) | Bot thứ 2 | Tin lạc/trùng giữa process |
| Nâng quyền tạm gắn nhiệm vụ | Sổ đăng ký (4.3) | Quên thu hồi |

---

## 14. Thứ tự và điểm dừng

```
G0 chốt vòng 3 ─┐
G1 tài liệu ────┼─► G2 lưới an toàn ─► G3 khung rỗng ─► G4 Đại sảnh ─► G5 Cổng ─► G6 Túp lều ─► G7 Dân cư ─► G8 Quản lý + dọn
(G1, G2 làm được ngay, không chờ G0)
```

Điểm dừng bắt buộc (cần owner gật đầu trước khi đi tiếp):
1. Sau G1: duyệt tài liệu + bản đồ.
2. Sau G2: xác nhận cơ chế tự quay về trên VPS (hoặc việc root phải làm).
3. Trước 4.6 (dời `handover`/`auto_update`), trước G6 (chuyển dữ liệu người dùng): thử chuyển máy↔VPS thật.
4. Sau G8: chốt bản đồ cuối.

## 15. Việc cần bạn làm

- Trả lời vòng 3 (`PyloS-trac-nghiem-vong-3.md`), hoặc gật đầu với "mặc định tạm" ở Giai đoạn 0.
- Cho phép mình SSH bằng user `em` **chỉ để đọc** unit `pylos-update` (bước 2.5).
- Nếu bước 2.6 cần root: chạy đoạn lệnh mình viết sẵn.
