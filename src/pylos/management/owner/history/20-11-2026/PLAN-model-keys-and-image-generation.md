# PyloS — Kế hoạch: đổi model + key, tạo ảnh, gửi ảnh Zalo

> Viết ngày 20-11-2026. File kế hoạch viết tiếng Việt để chủ hệ thống đọc; mọi thư mục, file và tài liệu **thuộc PyloS**
> tạo ra theo kế hoạch đều bằng **tiếng Anh, snake_case** (theo CLAUDE.md).
> Chưa có dòng code nào được sửa. Mỗi giai đoạn là **một PR**; merge vào `main` là deploy lên VPS, nên chạy `pytest -q`
> trước mỗi lần merge.

---

## 0. Quyết định đã chốt

| # | Câu hỏi | Chốt | Ghi chú |
|---|---------|------|---------|
| 1 | Danh sách key → model nằm đâu, có chứa giá trị key không? | `src/pylos/lobby/office/model_calls/model_keys.md`, **có trong git**, chỉ ghi **tên biến**; giá trị key nằm trong `management/owner/secrets/settings.env` | Chủ hệ thống đồng ý 20-11-2026 |
| 2 | Ảnh bot tạo ra lưu ở đâu? | Thư mục `media/` của túp lều chat (`gate/guest_house/huts/<chat_id>/media/`), tự xoá sau `MEDIA_KEEP_HOURS` như ảnh người dùng gửi | Mặc định tạm theo đề xuất; đổi sang `office/warehouse` thì chỉ sửa bước B4 |
| 3 | Hạn mức tạo ảnh tính bằng gì? | **Số ảnh** (mỗi ngày + mỗi người mỗi giờ), không tính vào `DAILY_TOKEN_BUDGET` | Mặc định tạm; Cloudflare không trả số token |
| 4 | Gửi ảnh ở chế độ nào? | Chỉ **tài khoản Zalo cá nhân** (`RECEIVE_MODE=personal`); chế độ Zalo Bot tạm báo bằng chữ | Mặc định tạm; API gửi ảnh của Zalo Bot chưa xác minh |

Model dùng cho việc tạo ảnh: `@cf/black-forest-labs/flux-1-schnell`. Model `@cf/leonardo/phoenix-1.0` chỉ được thêm vào
danh sách của key Cloudflare, **chưa** gán cho nhiệm vụ nào (chủ hệ thống hướng dẫn sau).

---

## 1. Hiện trạng (đã đọc code)

- **Đổi model**: bot lọc chọn hồ sơ (`routine` / `reflective` / `coding`) theo bảng trong
  `residential/residents/filter/workspace/modelShift.md`. Bảng được đọc bởi `residential/residents/filter/instructions.py`
  (`parse_profiles`, tự nạp lại khi file đổi). `pylos/message_handler.py::_model_for` giữ hồ sơ cho từng chat trong
  `ActiveModelStore` (`huts/<chat_id>/active_model.txt`).
- **Chỉ có một key**: `GEMINI_API_KEY`. `GeminiAgent.__init__` tạo **một** `genai.Client` duy nhất
  (`residential/residents/pylos/gemini_agent.py:124`). Chuỗi dự phòng (`chain()`) chỉ đổi tên model, luôn dùng cùng client.
- **Gửi Zalo**: chỉ gửi chữ. `gate/main_gate/zalo/personal_account.py::send_message` dùng `self._api.send(...)` của zlapi.
  zlapi đang cài có `sendLocalImage(imagePath, thread_id, thread_type, width=2560, height=2560, message=None, ...)`
  (đã kiểm tra trên máy). `bot_platform_api.py` chỉ có `sendMessage`.
- **Hạn mức**: `UsageStore` (`token_usage.txt`) đếm token Gemini mỗi ngày, `DailyCounter` đếm lượt `tim_web`.
  Không có hạn mức nào cho ảnh.
- **Tool của agent**: tự nạp mọi module có biến `TOOLS` trong `lobby/office/agent_tools/`. `ToolContext` là dataclass
  frozen, đã có các callback như `web_search`, `video_reader`.
- `residential/residents/filter/workspace/filter.py` là code mẫu không được gọi ở đâu: **giữ nguyên, không đụng**.
- Lưu ý: bot lọc đọc **mọi** `.md/.txt` trong căn hộ của nó làm chỉ dẫn (tối đa 20.000 ký tự), nên **không** đặt
  danh sách key vào đó.

---

## 2. Giai đoạn A — Danh sách key → model (PR 1)

Mục tiêu: model nào cũng tìm được đúng key để gọi; thêm nhà cung cấp mới dễ dàng. Hành vi trả lời chat **không đổi**.

### A1. Tạo căn hộ `src/pylos/lobby/office/model_calls/`

Không thêm toà mới (nằm trong `lobby/office`), nên **không cần sửa `regions.json`**.

```
model_calls/
├── __init__.py        # ModelCalls: cửa chung cho mọi lệnh gọi model
├── model_keys.md      # danh sách key -> model (chỉ tên biến, không có bí mật)
├── catalog.py         # đọc model_keys.md, resolve(model) -> KeyEntry
└── providers/
    ├── __init__.py    # PROVIDERS = {"gemini": GeminiProvider, "cloudflare": CloudflareProvider}
    ├── gemini.py      # tạo và giữ genai.Client theo từng key
    └── cloudflare.py  # gọi Cloudflare Workers AI (giai đoạn B mới dùng)
```

### A2. `model_keys.md` (định dạng)

```markdown
<!-- Danh sách key -> model. KHÔNG ghi giá trị key ở đây: chỉ ghi tên biến trong settings.env. -->
# Model keys

## gemini-main
provider: gemini
key: GEMINI_API_KEY
models: gemini-3.1-flash-lite, gemini-3.5-flash-lite, gemini-4-hydrogen

## cloudflare-main
provider: cloudflare
key: CLOUDFLARE_API_TOKEN
account: CLOUDFLARE_ACCOUNT_ID
models: @cf/black-forest-labs/flux-1-schnell, @cf/leonardo/phoenix-1.0
```

- Mỗi `## <tên key>` là một mục. Trường bắt buộc: `provider`, `key`, `models`. Trường riêng theo nhà cung cấp
  (ví dụ `account` của Cloudflare) cũng là **tên biến**.
- Thêm key Gemini thứ hai: thêm `GEMINI_API_KEY_2=` vào `settings.env` và một mục `## gemini-backup` liệt kê model của key đó.

### A3. `catalog.py`

- `KeyEntry(name, provider, secret, extras: dict, models: tuple)`.
- `ModelCatalog(path, env)`:
  - Đọc file, tự nạp lại khi `mtime` đổi (giống `FilterInstructions._read`).
  - Bỏ ghi chú `<!-- -->`.
  - Mục sai (thiếu trường, `provider` lạ, biến chưa điền trong env) → bỏ qua + `log.warning` (**không** in giá trị key).
  - Một model nằm ở hai key → dùng key đầu tiên + cảnh báo.
  - `resolve(model) -> KeyEntry | None`; `models(provider=None) -> list[str]`; `entries()` cho trang quản lý (không có giá trị bí mật).
- Thiếu file hoặc file hỏng → mặc định: một mục `gemini` dùng `GEMINI_API_KEY` cho **mọi** model Gemini
  (giữ nguyên hành vi hiện nay để bot không chết).

### A4. `providers/`

- `providers/__init__.py`: `PROVIDERS` dict + giao diện `Provider` (Protocol). Thêm nhà cung cấp = một file + một dòng.
- `providers/gemini.py`: `client_for(entry)` → `genai.Client(api_key=entry.secret)`, giữ cache theo tên key; key đổi giá trị
  (sửa trên trang Cài đặt) thì tạo client mới.
- `providers/cloudflare.py`: chỉ khung ở PR 1, nội dung ở giai đoạn B.

### A5. `ModelCalls` (`__init__.py`)

- `ModelCalls(catalog, tasks)`, trong đó `tasks` là bảng nhiệm vụ đọc từ `modelShift.md` (A6).
- PR 1 có: `gemini_client(model)` (cho `GeminiAgent`), `resolve(model)`.
- PR 2 thêm: `generate_image(prompt, *, task="image", model=None) -> ImageResult(data: bytes, mime: str, model: str)`.

### A6. Bảng nhiệm vụ trong `modelShift.md`

Thêm một mục mới, **bảng hồ sơ hiện có giữ nguyên**:

```markdown
## Task models (read by the code)

Some work is not answering in chat but making something else. The code reads this table; you do not pick it.
When the assistant needs to create an image, it uses the model on the `image` row.

| task  | model                                | fallbacks |
|-------|--------------------------------------|-----------|
| image | @cf/black-forest-labs/flux-1-schnell | -         |
```

- `instructions.py`: thêm `TaskModel(task, model, fallbacks)`, `parse_tasks(text)` và `FilterInstructions.tasks()`.
  `parse_profiles` hiện chỉ nhận dòng có tên hồ sơ nên không bị bảng mới làm hỏng. Vẫn thêm test để chắc chắn.
- Mặc định khi thiếu dòng: `image -> @cf/black-forest-labs/flux-1-schnell`.

### A7. Nối `GeminiAgent` với danh sách key

- `GeminiAgent.__init__` nhận thêm `clients: Callable[[str], Any] | None` (mặc định `None` = hành vi cũ, client duy nhất).
- `_generate(...)` dùng `self._client_for(name)` thay cho `self._client`. Việc tải tệp lên Files API vẫn dùng client
  của model chính (tệp Files API gắn với key; ghi rõ trong docstring).
- Model trong chuỗi mà `resolve` trả về nhà cung cấp khác `gemini` → bỏ khỏi chuỗi + cảnh báo
  (chat hiện chỉ trả lời bằng Gemini).
- `message_handler.py` (chỗ tạo agent, dòng ~142), `bot/command_line.py` (dòng ~60) và `admin_web_server.py`
  (dòng ~866, "Chat thử") truyền `clients=model_calls.gemini_client`.

### A8. Cấu hình

- `lobby/dispatch/shared/config.py`: thêm `cloudflare_account_id`, `cloudflare_api_token` vào `Settings`; thêm vào
  `secrets` (để che trong log).
- `lobby/dispatch/shared/templates/env.example`: thêm hai biến, kèm chú thích tiếng Việt.
- `management/owner/admin_web/settings_file.py`: nhóm "Cloudflare" với hai trường (token là trường bí mật).
- `catalog` đọc biến qua `os.environ` sau khi `Settings.from_env` đã nạp `settings.env`, nên không cần thêm trường
  `Settings` cho mỗi key mới.

### A9. Test (PR 1)

- `tests/lobby/office/test_model_calls.py`: đọc catalog (mục đúng, thiếu trường, provider lạ, biến chưa điền, model trùng,
  file thiếu → mặc định), tự nạp lại khi file đổi, `entries()` không lộ bí mật.
- `tests/residential/residents/test_filter_tasks.py`: `parse_tasks`, và `parse_profiles` vẫn đúng khi có bảng nhiệm vụ.
- `tests/residential/residents/test_agent.py`: thêm ca "model dự phòng nằm ở key khác thì dùng client của key đó",
  "model của provider khác bị bỏ khỏi chuỗi".
- `pytest -q` toàn bộ phải xanh.

### A10. Hoàn tất PR 1

- `city.md`: dòng toà `office` thêm `model_calls` (danh sách key → model, cửa chung gọi model).
- `graphify update .`
- Commit + PR. Sau khi merge: VPS chạy như cũ (chưa có key Cloudflare cũng không sao).

---

## 3. Giai đoạn B — Tạo ảnh (PR 2, gồm cả giai đoạn D)

### B1. `providers/cloudflare.py`

- `POST https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}`, header `Authorization: Bearer <token>`,
  body `{"prompt": ..., "steps": 4}` cho flux-1-schnell (steps 1–8).
- Phản hồi: `Content-Type: image/*` → dữ liệu ảnh; JSON → `result.image` (base64). Hỗ trợ cả hai.
- Lỗi: 401/403 (token sai hoặc thiếu quyền), 429 hoặc hết Neurons, 5xx, hết giờ → `ModelCallError` với thông báo tiếng Việt
  rõ ràng, **không** chứa token.
- Dùng `httpx` (đã có trong dự án), timeout lấy từ `LLM_TIMEOUT_SECONDS`.
- **Chưa xác minh** bằng tài liệu chính thức: tên tham số `steps`, vị trí `result.image`. Kiểm tra lại trên trang model
  Cloudflare trước khi code, ghi nguồn vào docstring.

### B2. `ModelCalls.generate_image`

- `task="image"` → tra bảng nhiệm vụ → model → `catalog.resolve` → provider → gọi.
- Lỗi 429/5xx/hết giờ ở model chính → thử lần lượt `fallbacks` của dòng nhiệm vụ (hiện `-`, tức không có).
- Ghi log INFO mỗi lần tạo: chat, model, kích thước, thời gian (không ghi prompt đầy đủ, chỉ 80 ký tự đầu).

### B3. Tool `tao_anh` — `lobby/office/agent_tools/create_image.py`

- `Tool(name="tao_anh", parameters={"prompt": str (bắt buộc, tiếng Anh), "caption": str (tuỳ chọn, tiếng Việt)})`.
- Mô tả cho model: khi người dùng nhờ vẽ/tạo ảnh thì gọi tool này; viết `prompt` tiếng Anh chi tiết; sau khi tool trả `ok`
  thì chỉ trả lời một câu ngắn vì ảnh được gửi kèm.
- `enabled`: `IMAGE_GEN` bật **và** catalog tìm được key cho model của nhiệm vụ `image`. Thiếu key → tool ẩn khỏi model.
- Handler:
  1. Kiểm tra hạn mức (D2). Hết → `{"error": "Hôm nay đã tạo đủ N ảnh..."}`.
  2. `ctx.image_maker(prompt)` (callback mới trong `ToolContext`, Bot gắn vào, giống `web_search`).
  3. Thành công → `{"ok": true, "sent": "ảnh sẽ được gửi kèm câu trả lời"}`.

### B4. Lưu ảnh và hàng chờ gửi

- Lưu `huts/<chat_id>/media/gen_<timestamp>.png` bằng `media_store` hiện có (tự xoá sau `MEDIA_KEEP_HOURS`).
- `ToolContext` thêm `outbox: list[OutgoingImage]` (`field(default_factory=list)`; dataclass frozen nhưng list vẫn thêm
  được phần tử). `OutgoingImage(path, caption)`.
- Ghi vào `ToolStep` để xem lại trong session.

### B5. Cấu hình

- `IMAGE_GEN` (mặc định `true`), `IMAGE_STEPS` (mặc định 4, 1–8). Thêm vào `Settings`, `env.example`, trang Cài đặt
  (nhóm "Tạo ảnh").

### B6. Test

- `tests/lobby/office/test_cloudflare_provider.py`: phản hồi JSON, phản hồi ảnh trực tiếp, 401, 429, hết giờ, lỗi không lộ token
  (dùng `httpx.MockTransport`).
- `tests/lobby/office/test_create_image.py`: tool ẩn khi thiếu key, gọi đúng model của nhiệm vụ, thêm vào `outbox`,
  hết hạn mức thì báo lỗi.

---

## 4. Giai đoạn D — Hạn mức riêng cho tạo ảnh (trong PR 2)

### D1. Cấu hình

- `IMAGE_PER_DAY` (mặc định 50; flux-1-schnell miễn phí khoảng 170 ảnh/ngày trên Cloudflare, để dư).
- `USER_IMAGES_PER_HOUR` (mặc định 5). `0` = không giới hạn (giống các giới hạn khác).

### D2. Code — `gate/fence/token_limit/image_limit.py`

- `ImageLimit(counter: DailyCounter, per_day, per_user_hour, clock)`:
  - `check(user_id) -> str | None` (None = được tạo, chuỗi = lý do từ chối).
  - `record(user_id)` sau khi tạo **thành công** (lỗi không bị trừ lượt).
- Bộ đếm ngày: `DailyCounter` mới trên file `image_usage.txt`, đặt cạnh `token_usage.txt` / `web_search_usage.txt`
  (cùng thư mục, không đổi nơi lưu dữ liệu). Bộ đếm mỗi người mỗi giờ: cửa sổ trượt trong bộ nhớ (như `RateLimiter`).
- **Không** cộng vào `DAILY_TOKEN_BUDGET`.

### D3. Hiển thị

- `StatsStore.incr("images")` mỗi ảnh. Trang Tổng quan hiện "Ảnh hôm nay: x / IMAGE_PER_DAY".

### D4. Test

- `tests/gate/fence/test_image_limit.py`: hết lượt ngày, hết lượt giờ của một người (người khác vẫn tạo được),
  sang ngày mới (giờ Việt Nam) thì đặt lại, `0` = không giới hạn.

### D5. Hoàn tất PR 2

- `city.md`: `office` có tool `tao_anh`; `fence/token_limit` có hạn mức ảnh.
- `graphify update .`, `pytest -q`.
- **Trước khi merge**: điền `CLOUDFLARE_ACCOUNT_ID` và `CLOUDFLARE_API_TOKEN` vào `settings.env` trên VPS (trang Cài đặt).
  Chưa điền thì tool tự ẩn, bot vẫn chạy bình thường.

---

## 5. Giai đoạn C — Gửi ảnh vào Zalo (PR 3)

### C1. `personal_account.send_image(chat_id, path, caption="")`

- Chạy `self._api.sendLocalImage(str(path), chat_id, thread_type, width=w, height=h, message=Message(text=caption))`
  trong `asyncio.to_thread`.
- `w, h` đọc từ header PNG (24 byte đầu), khỏi thêm thư viện.
- Lỗi → `ZaloError(..., network=...)` như `send_message`.

### C2. Chế độ Zalo Bot

- `bot_platform_api.send_image` → `raise ZaloError("Chế độ Zalo Bot chưa hỗ trợ gửi ảnh")`.
- `message_handler` bắt lỗi này và gửi chữ: "Ảnh đã tạo nhưng chế độ Zalo Bot chưa gửi được ảnh."

### C3. `message_handler._reply`

- Sau `agent.reply(...)`: với mỗi ảnh trong `ctx.outbox` → `await self._send_image(chat_id, img)` dưới **cùng khoá gửi**
  của chat (`self._send_locks`), rồi mới gửi phần chữ.
- `_send_image` lỗi → log + `self.failed.add(chat_id, "(ảnh) <tên file>", lỗi)` + báo người dùng một câu.
- Lịch sử: `history.append(chat_id, "model", text + "\n(đã gửi 1 ảnh)")` để lượt sau model biết đã gửi ảnh.
- `ToolContext` tạo ở `_reply` (dòng ~530) gắn `image_maker=self._image_maker()` và `outbox=[]`.

### C4. Test

- `tests/residential/residents/test_image_reply.py` với Zalo giả: ảnh gửi trước chữ, gửi ảnh lỗi thì báo người dùng và
  ghi danh sách gửi lỗi, chế độ Zalo Bot gửi câu thay thế, không có ảnh thì hành vi như cũ.
- `tests/gate/main_gate/test_personal_media.py`: thêm ca `send_image` gọi `sendLocalImage` đúng tham số và kích thước.

### C5. Hoàn tất PR 3

- `city.md`: `main_gate/zalo` gửi được ảnh (tài khoản cá nhân).
- `graphify update .`, `pytest -q`, kiểm tra `python -m bot run` và `python -m bot gui` vẫn khởi động.
- Thử thật trên máy admin: chat riêng với bot "vẽ con mèo phi hành gia" → nhận ảnh.

---

## 6. Thứ tự và nhánh

1. Tạo nhánh mới từ `main`, ví dụ `claude/model-keys` (không dùng `claude/fix-model-shift`: nhánh đó đang có thay đổi
   chưa commit ở các file bản đồ).
2. PR 1 (A) → merge → VPS chạy như cũ.
3. Điền key Cloudflare trên VPS.
4. PR 2 (B + D) → merge → tool có mặt nhưng chưa gửi được ảnh (model chỉ báo "đã tạo").
   *Có thể gộp PR 2 và PR 3 nếu chủ hệ thống muốn tránh khoảng giữa này.*
5. PR 3 (C) → merge → bot gửi ảnh vào Zalo.

---

## 7. Rủi ro và điểm chưa xác minh

- **Tham số và phản hồi của Cloudflare** (`steps`, `result.image`): kiểm tra trên trang model trước khi code B1.
- **Hạn mức miễn phí của Cloudflare** (10.000 Neurons/ngày, khoảng 170–230 ảnh flux 512×512): nguồn là trang giá Cloudflare
  và một trang ước tính bên thứ ba. `IMAGE_PER_DAY=50` để dư.
- **Model Partner** (`phoenix-1.0`, Leonardo): chưa biết có được tính vào phần miễn phí không. Chưa dùng ở kế hoạch này.
- **Files API của Gemini gắn với key**: tệp tải lên bằng key A không dùng được với key B. A7 giữ việc tải tệp ở client của
  model chính; dự phòng sang key khác thì tải lại tệp (ghi nhận, xử lý nếu gặp).
- **`sendLocalImage` của zlapi**: đã thấy hàm có trong thư viện đang cài, chưa chạy thử với tài khoản thật.
- **Nội dung ảnh**: model có thể tạo ảnh không phù hợp. Prompt đi qua model chính (đã có quy tắc trong `SYSTEM.md`);
  cân nhắc thêm một kiểm tra ở `gate/fence/ethics` sau.
