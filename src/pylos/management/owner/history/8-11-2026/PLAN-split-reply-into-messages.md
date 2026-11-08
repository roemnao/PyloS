# Kế hoạch: tách câu trả lời nhiều dòng thành nhiều tin Zalo

Ngày lập: 2026-11-08. Phạm vi: `gate/main_gate` (cách cắt tin) + chỗ gọi gửi tin của bot. Không đổi nơi lưu dữ liệu.
Làm hết các bước theo thứ tự, không cần hỏi chủ sau từng bước. Chỉ dừng lại hỏi nếu gặp điều ghi ở mục "Khi nào phải dừng".

## 1. Hiện trạng (đã đọc code)

| Chỗ | Việc đang làm |
|---|---|
| `src/pylos/residential/residents/pylos/message_handler.py` `Bot._reply()` | Gọi Gemini, làm sạch (`to_plain_text`, `strip_name_prefix`, `add_tags`), ghi session, rồi `_say()` |
| `Bot._say()` | Ghi **một** bản vào memorydata, rồi `_send()` |
| `Bot._send()` | `for chunk in split_message(text): await self._send_chunk(...)` |
| `Bot._send_chunk()` | Gửi, thử lại 3 lần (chờ 1s, 2s…), hỏng thì lưu `failed.txt` |
| `src/pylos/gate/main_gate/zalo/reply_formatting.py` `split_message()` | Chỉ cắt khi tin **dài hơn 2000** ký tự (UTF-16), ưu tiên cắt ở `\n\n`, `\n`, `. `, khoảng trắng |
| `src/pylos/gate/main_gate/zalo/personal_account.py` `send_message()` | Với nhóm: tìm `@Tên` trong **chính tin đó** để tạo mention (vị trí tính theo tin) |
| `src/pylos/management/owner/admin_web/admin_web_server.py` ~dòng 814 | Gửi lại tin hỏng: dùng `split_message` |

Vì vậy hôm nay một câu trả lời 5 dòng đi thành **1** tin.

## 2. Hành vi muốn có

- Câu trả lời có nhiều dòng → gửi thành nhiều tin, theo thứ tự, như người gõ từng tin.
- Có 3 kiểu, chủ chọn trong trang quản lý:
  - `line` (mặc định): mỗi dòng không rỗng một tin.
  - `paragraph`: mỗi đoạn (ngăn bởi dòng trống) một tin; các dòng trong cùng đoạn đi chung.
  - `off`: như cũ, một tin.
- Không thành "spam": tối đa `REPLY_MAX_PARTS` tin (mặc định 6). Nhiều dòng hơn thì **gộp các dòng liền nhau** cho vừa số tin (không cắt bỏ nội dung).
- Giữ nguyên khối liền mạch, không tách bên trong:
  - khối code giữa hai dòng ```` ``` ````;
  - một danh sách gạch đầu dòng liền nhau (`• `, `- `, `1. `) đi cùng dòng tiêu đề ngay trước nó nếu dòng đó kết thúc bằng `:`.
- Mỗi tin vẫn ≤ 2000 ký tự: tin nào dài hơn thì `split_message` cắt tiếp như hiện nay.
- Giữa các tin: chờ `REPLY_PART_DELAY_MS` (mặc định 700 ms) và gửi "đang gõ…", để Zalo không chặn vì gửi dồn và trông tự nhiên.
- Tag `@Tên`: không cần đổi gì. `personal_account.send_message` tính mention theo từng tin, nên tin nào có `@Tên` thì tag đúng trong tin đó.
- memorydata và session vẫn lưu **một** bản đầy đủ của câu trả lời (như hiện nay), không lưu từng mảnh.
- Hai câu trả lời cho cùng một chat không được xen kẽ mảnh vào nhau.

## 3. Các bước

### Bước 1 — Hàm cắt theo dòng trong `gate/main_gate` (không đụng chỗ khác)

File: `src/pylos/gate/main_gate/zalo/reply_formatting.py`

1. Thêm hằng: `SPLIT_OFF = "off"`, `SPLIT_LINE = "line"`, `SPLIT_PARAGRAPH = "paragraph"`, `SPLIT_MODES = (...)`.
2. Thêm hàm nội bộ `_blocks(text) -> list[str]`: tách văn bản thành các "khối không được cắt":
   - đi qua từng dòng; gặp ```` ``` ```` thì gom tới ```` ``` ```` đóng (thiếu dấu đóng: gom tới hết);
   - dòng gạch đầu dòng liền nhau gom thành một khối; nếu dòng ngay trước kết thúc bằng `:` thì dòng đó vào chung khối;
   - các dòng còn lại: mỗi dòng một khối; dòng trống là ranh giới đoạn (giữ thông tin này cho kiểu `paragraph`).
3. Thêm hàm công khai:
   ```python
   def split_reply(text: str, mode: str = SPLIT_LINE, max_parts: int = 6,
                   limit: int = ZALO_TEXT_LIMIT) -> list[str]:
       """Chia câu trả lời thành các tin Zalo (docstring tiếng Việt như code xung quanh)."""
   ```
   - `mode == off` hoặc `max_parts <= 1` → `split_message(text, limit)` (giữ y hệt hôm nay).
   - `line` → đơn vị là khối của `_blocks`; `paragraph` → gộp khối trong cùng đoạn.
   - Nếu số đơn vị > `max_parts`: gộp các đơn vị liền nhau thành đúng `max_parts` nhóm, cân theo độ dài (thuật toán đơn giản: chia tham lam theo tổng độ dài / `max_parts`), nối bằng `\n` (kiểu `paragraph` nối bằng `\n\n`).
   - Mỗi nhóm cho qua `split_message(nhóm, limit)` rồi nối các kết quả; bỏ mảnh rỗng; giữ thứ tự.
   - Văn bản rỗng → `[]`.
4. Không đổi `split_message` (trang quản lý và các test đang dùng nó).

### Bước 2 — Cài đặt mới

1. `src/pylos/lobby/dispatch/shared/config.py`:
   - `Settings` thêm 3 trường có mặc định (đặt cạnh các trường có mặc định, giữ chú thích tiếng Việt):
     `reply_split: str = "line"`, `reply_max_parts: int = 6`, `reply_part_delay_ms: int = 700`.
   - Trong hàm đọc env: `REPLY_SPLIT` (chỉ nhận `off|line|paragraph`, sai thì về `line` và ghi log cảnh báo — làm giống cách `assign_allowed` / `bot_supervisor` đang kiểm), `REPLY_MAX_PARTS` (`_int`, minimum=1), `REPLY_PART_DELAY_MS` (`_int`, minimum=0).
   - Import `SPLIT_MODES` từ `reply_formatting` có thể kéo `gate` vào `lobby`: **không** import; tự viết tuple `("off", "line", "paragraph")` trong config, và test ở bước 6 kiểm hai tuple bằng nhau.
2. `src/pylos/lobby/dispatch/shared/templates/env.example`: thêm khối có chú thích tiếng Việt, gần `HISTORY_TURNS`:
   ```
   # Câu trả lời nhiều dòng: line = mỗi dòng một tin, paragraph = mỗi đoạn một tin, off = một tin
   REPLY_SPLIT=line
   # Tối đa bao nhiêu tin cho một câu trả lời (nhiều dòng hơn thì gộp lại)
   REPLY_MAX_PARTS=6
   # Nghỉ giữa hai tin (mili giây)
   REPLY_PART_DELAY_MS=700
   ```
3. `src/pylos/management/owner/admin_web/settings_file.py`: thêm 3 `FieldSpec` vào nhóm hiển thị phù hợp (nhóm "Zalo" nếu có, không thì nhóm của `HISTORY_TURNS`). `REPLY_SPLIT` dùng kiểu lựa chọn nếu `FieldSpec` hỗ trợ (xem cách `RECEIVE_MODE`/`ASSIGN_ALLOWED` khai báo), không thì kiểu chữ có mô tả `off / line / paragraph`.
4. Bot đã nạp lại `Settings` khi file cài đặt đổi (xem chỗ `self.history.keep = ...` ~dòng 103): kiểm tra bot dùng `self.settings` mới ở `_send`, không cần khởi động lại.

### Bước 3 — Bot gửi theo mảnh

File: `src/pylos/residential/residents/pylos/message_handler.py`

1. Import `split_reply` thay cho (hoặc cùng) `split_message`.
2. `Bot.__init__`: thêm `self._send_locks: dict[str, asyncio.Lock] = {}`.
3. Viết lại `_send`:
   ```python
   async def _send(self, chat_id: str, text: str) -> None:
       s = self.settings
       parts = split_reply(text, s.reply_split, s.reply_max_parts)
       lock = self._send_locks.setdefault(chat_id, asyncio.Lock())
       async with lock:  # hai câu trả lời cùng chat không xen kẽ mảnh
           for index, part in enumerate(parts):
               if index:
                   await self._pause_between_parts(chat_id)
               if not await self._send_chunk(chat_id, part):
                   rest = parts[index + 1:]
                   if rest:
                       self.failed.add(chat_id, "\n".join(rest), "bỏ dở vì mảnh trước gửi lỗi")
                   return
   ```
4. `_send_chunk` trả về `bool` (`True` gửi được, `False` đã lưu vào failed) — các nơi gọi khác (nếu có) vẫn chạy vì trước đây giá trị trả về bị bỏ qua.
5. Thêm `_pause_between_parts(chat_id)`: gửi `send_chat_action(chat_id, "typing")` (bỏ qua lỗi như trong `_reply`), rồi `await asyncio.sleep(self.settings.reply_part_delay_ms / 1000)`.
6. Không đổi `_say`, `_reply`, việc ghi memorydata/session: vẫn một bản đầy đủ.
7. Các tin hệ thống ngắn (`ERROR_REPLY`, `BUDGET_NOTICE`, trả lời lệnh của chủ) cũng đi qua `_send`: chúng một dòng nên không bị ảnh hưởng. Kiểm bằng grep `_say(` / `_send(` và đọc từng chỗ có văn bản nhiều dòng (ví dụ danh sách nhóm, trợ giúp lệnh); nếu chỗ nào là bảng/danh sách dài nên đi chung một tin, gọi một hàm `_send(..., split=False)` (thêm tham số `split: bool = True`, `False` thì dùng `split_message`).

### Bước 4 — Trang quản lý gửi lại tin hỏng

`admin_web_server.py` ~dòng 814: giữ `split_message` (tin hỏng đã là một mảnh hoặc phần còn lại; gửi lại nguyên khối là đúng). Chỉ thêm chú thích một dòng vì sao không dùng `split_reply`.

### Bước 5 — Chế độ console thử bot

`src/bot/command_line.py` `_console()`: bot chạy với Zalo giả in ra màn hình. Đặt `reply_part_delay_ms` = 0 cho console (dùng `dataclasses.replace(settings, reply_part_delay_ms=0)` ở chỗ dựng settings console) để thử nhanh; mỗi mảnh in thành một tin riêng là đủ thấy kết quả.

### Bước 6 — Test

1. `tests/gate/main_gate/test_text_and_models.py` (hoặc file mới `tests/gate/main_gate/test_split_reply.py`):
   - 3 dòng, `line` → 3 tin; `paragraph` với 2 đoạn → 2 tin; `off` → 1 tin.
   - dòng trống thừa, khoảng trắng đầu/cuối → không có tin rỗng.
   - 10 dòng, `max_parts=4` → đúng 4 tin, nối lại bằng `\n` ra đúng văn bản gốc (bỏ dòng trống), thứ tự giữ nguyên.
   - khối ```` ``` ```` có dòng bên trong → nằm trọn trong một tin.
   - "Danh sách:" + 3 dòng `• ` → một tin.
   - một dòng 4500 ký tự → 3 tin, mỗi tin ≤ 2000 (UTF-16, có emoji).
   - `""` → `[]`.
2. `tests/residential/residents/test_bot.py` (dùng `FakeZalo` trong `tests/conftest.py`):
   - Gemini giả trả "A\nB\nC" → `FakeZalo` nhận 3 tin theo thứ tự; memorydata và session chỉ có **một** bản "A\nB\nC".
   - `REPLY_SPLIT=off` → 1 tin.
   - mảnh thứ 2 luôn lỗi `ZaloError` → mảnh 1 đi, mảnh 2 vào failed, mảnh 3 vào failed (phần còn lại), không gửi mảnh 3.
   - hai `_send` chạy đồng thời cùng chat → tin không xen kẽ.
   - Đặt `retry_delay=0` và `reply_part_delay_ms=0` trong test để chạy nhanh.
3. `tests/gate/main_gate/test_config_client_webhook.py`: đọc 3 biến mới, giá trị sai của `REPLY_SPLIT` về `line`, `REPLY_MAX_PARTS=0` về 1; tuple chế độ trong config bằng `SPLIT_MODES`.
4. `tests/management/owner/test_admin.py`: trang cài đặt có 3 ô mới (nếu test hiện có kiểm danh sách trường).
5. Chạy toàn bộ: `pytest -q` — phải xanh hết trước khi mở PR.

### Bước 7 — Tài liệu và bản đồ

1. `README.md`: bảng cài đặt thêm 3 dòng `REPLY_SPLIT`, `REPLY_MAX_PARTS`, `REPLY_PART_DELAY_MS`.
2. `src/pylos/lobby/atlas/city.md`: một dòng ở mục `gate/main_gate` ("cắt câu trả lời thành nhiều tin: `reply_formatting.split_reply`"). Không thêm toà nhà mới nên **không** sửa `regions.json`.
3. `graphify update .` để cập nhật bản đồ.

### Bước 8 — PR và triển khai

1. Nhánh mới từ `origin/main` mới nhất: `git fetch origin && git switch -c claude/split-reply origin/main`.
2. Commit theo từng bước (hàm cắt + test; cài đặt; bot; tài liệu), message tiếng Việt như các commit trước.
3. Mở PR với **base = `main`**, head = `claude/split-reply` (lần trước PR #26 bị đảo chiều nên không lên VPS).
4. Chờ CI xanh. Chủ gộp PR → VPS tự cập nhật trong ~10 phút (hoặc nút "Cập nhật code").
5. Sau khi lên VPS: nhắn bot một câu cần trả lời nhiều dòng trong một nhóm thử, xem đi thành nhiều tin, tag `@` vẫn đúng, không bị Zalo chặn. Nếu thấy dồn quá, tăng `REPLY_PART_DELAY_MS` trong trang quản lý (không cần sửa code).

## 4. Rủi ro và cách tránh

| Rủi ro | Cách tránh |
|---|---|
| Zalo chặn / giới hạn vì gửi nhiều tin liên tiếp | Tối đa 6 tin, nghỉ 700 ms + "đang gõ" giữa các tin; chỉnh được trong trang quản lý |
| Danh sách / code bị xé lẻ khó đọc | `_blocks` giữ nguyên khối code và danh sách |
| Mảnh giữa lỗi làm câu trả lời cụt | Dừng, lưu phần còn lại vào failed để gửi lại từ trang quản lý |
| Hai câu trả lời xen kẽ | Khoá theo chat trong `_send` |
| `lobby` import `gate` (sai luật thành) | Config tự khai tuple chế độ, test kiểm khớp |
| Hành vi cũ cần giữ | `REPLY_SPLIT=off` trả lại y hệt hôm nay |

## 5. Khi nào phải dừng hỏi chủ

- Phải thêm zone mới hoặc đổi nơi lưu dữ liệu (không dự kiến).
- `FieldSpec` / trang cài đặt cần đổi cấu trúc lớn để có ô lựa chọn.
- Test cũ nào phải sửa ý nghĩa (không chỉ thêm tham số) mới xanh được.

## 6. Xong là khi

- `pytest -q` xanh, CI xanh, PR vào `main` đã mở.
- Câu trả lời 3 dòng đi thành 3 tin; `REPLY_SPLIT=off` vẫn 1 tin; memorydata/session lưu một bản đầy đủ.
- 3 cài đặt mới có trong `env.example`, trang quản lý và README; bản đồ đã cập nhật.
