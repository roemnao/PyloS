# Kế hoạch: Server Bot Zalo chạy Agent (AI)

> Mục tiêu: một server nhận tin nhắn từ Zalo (webhook), chuyển cho **agent AI** xử lý (có thể gọi công cụ), rồi gửi câu trả lời lại cho người dùng trên Zalo.
> Đã đối chiếu với tài liệu chính thức của **Zalo Bot Platform** (bot.zapps.me/docs) ngày 2026-10-21. Phần **Zalo OA** chưa kiểm chứng được từ nguồn chính thức, được đánh dấu rõ bên dưới.

## 0. Quyết định đã chốt

| Hạng mục | Quyết định | Hệ quả |
|---|---|---|
| Kênh | Zalo Bot Platform (không dùng OA) | Phần OA bên dưới chỉ để tham khảo |
| Mục đích | Trợ lý (hỏi đáp, ghi chú, nhắc việc, tra cứu web...) | Tools nằm ở mục 5b |
| Model | Google Gemini, `gemini-3.1-flash-lite` | Dùng Gemini API + function calling, xem 5b |
| Dữ liệu riêng | Không có | Bỏ RAG/FAQ ở giai đoạn đầu |
| Chạy ở | Máy local, chưa có VPS/domain, nhưng muốn chạy 24/7 | Polling + chạy như dịch vụ nền, xem mục 3a và 3b |
| Phạm vi chat | **Chat nhóm** | Xem mục 5c, đây là phần rủi ro nhất |
| Chế độ trả lời | 2 chế độ, chủ bot bật/tắt | Chế độ `all` và `default`, xem mục 5c |
| Bot token, API key Gemini | **Để trống, thêm sau** | Chỉ có `.env.example`; code phải chạy được phần không cần token (test, mock), xem mục 4a |
| Tools | **Thêm sau** | Dựng khung đăng ký tool rỗng, chưa viết tool cụ thể |
| Nhóm được dùng | **Thêm sau** | Allowlist rỗng khi mới cài; xem 5c |

Lưu ý chưa kiểm chứng được từ nguồn chính thức:
- Tên model: các trang tổng hợp bên thứ ba liệt kê cả `gemini-3.1-flash-lite` và `gemini-3.1-flash-lite-preview`, giá khoảng 0,25 USD / 1M token vào và 1,50 USD / 1M token ra, có function calling. Cần xác nhận ID đúng trong trang model của Google AI Studio trước khi code.
- Hành vi chat nhóm của Zalo Bot: docs chỉ cho biết `chat_type` có `GROUP` (Beta) và `getMe` có trường `can_join_groups`. Chưa rõ bot nhận **mọi** tin trong nhóm hay chỉ tin nhắc tên/trả lời bot.

## 1. Chọn kênh Zalo

| Lựa chọn | Phù hợp khi | Lưu ý |
|---|---|---|
| **Zalo Bot Platform** (tạo bot qua Zalo Bot Creator, có bot token) | Muốn bot chat nhanh, thiết lập đơn giản, ít thủ tục | Đã kiểm chứng, xem mục 1a |
| **Zalo Official Account (OA) API** | Bot cho doanh nghiệp, cần OA đã xác minh | **Chưa kiểm chứng.** Nguồn thứ ba nói endpoint `https://openapi.zalo.me/v3.0/oa/message/cs` chỉ gửi được trong khung thời gian sau lần tương tác cuối của user (một nguồn nói 48 giờ, nguồn khác nói 7 ngày, mâu thuẫn). Cách xác thực webhook OA, thời hạn access/refresh token cần đọc docs chính thức trước khi làm |

Đề xuất: bắt đầu với **Zalo Bot Platform**; thiết kế lớp `ZaloClient` tách biệt để sau này thêm OA mà không đổi phần agent.

### 1a. Zalo Bot Platform: các sự kiện đã xác minh

- **Gọi API**: `https://bot-api.zaloplatforms.com/bot<BOT_TOKEN>/<tênHàm>`, HTTPS bắt buộc, hỗ trợ GET/POST, tham số dạng query, form, JSON hoặc multipart, UTF-8, tên hàm phân biệt hoa thường. Response luôn có `ok`, `result`, `description`, `error_code`.
- **Đăng ký webhook**: `POST .../setWebhook` với `url` (HTTPS, công khai, không phải localhost/IP nội bộ/domain nội bộ của Zalo) và `secret_token` (bắt buộc, 8–256 ký tự). Zalo tự gửi một request kiểm tra khi lưu; URL vẫn được lưu dù kiểm tra thất bại. Có `testWebhook` để kiểm tra lại.
- **Xác thực**: Zalo gửi header `X-Bot-Api-Secret-Token` chứa đúng `secret_token` bạn đặt. Đây là **secret tĩnh**, không phải chữ ký HMAC của payload. Sai ⇒ trả 403.
- **Payload**: `{"ok": true, "result": {"event_name": ..., "message": {"from": {id, display_name, is_bot}, "chat": {id, chat_type}, "text", "message_id", "date"}}}`. Các `event_name`: `message.text.received`, `message.image.received`, `message.sticker.received`, `message.voice.received`, `message.unsupported.received` (ví dụ tài khoản trẻ em). `chat_type` là `PRIVATE` hoặc `GROUP` (nhóm đang Beta). Trả lời bằng `chat.id`.
- **Gửi tin**: `POST .../sendMessage` với `chat_id`, `text` (**1–2000 ký tự**), tùy chọn `parse_mode` (`markdown`/`html`) hoặc `text_styles`. Trả về `message_id`, `date`.
- **getUpdates** (polling): loại trừ với webhook; nếu đã có webhook phải `deleteWebhook` trước. Docs khuyên chỉ dùng khi dev/test.
- **Không có trong docs** (nên coi là chưa biết): timeout của webhook, chính sách retry khi server không trả lời, rate limit.

## 2. Kiến trúc

```
Người dùng Zalo
     │
     ▼
 Zalo Platform ──webhook (HTTPS)──► Server (FastAPI)
                                       │ 1. kiểm tra header X-Bot-Api-Secret-Token
                                       │ 2. trả 200 ngay, đẩy việc vào hàng đợi
                                       ▼
                                 Worker xử lý tin
                                       │
                      ┌────────────────┼─────────────────┐
                      ▼                ▼                 ▼
               Bộ nhớ hội thoại   Agent (LLM + tools)   Rate limiter
               (file .txt)        (Gemini API)          / chống spam
                                       │
                                       ▼
                               ZaloClient.send_message ──► Zalo API
```

Điểm quan trọng: webhook nên **trả lời nhanh**, còn agent chạy nền (LLM có thể mất vài giây). Docs Zalo không nêu timeout hay chính sách retry, nên đây là thiết kế phòng thủ, không phải yêu cầu đã xác nhận; vẫn nên chống xử lý trùng phòng khi có gửi lại.

## 3. Công nghệ

- Python 3.11+, FastAPI + uvicorn.
- Agent: Gemini API (SDK `google-genai`), model `gemini-3.1-flash-lite` (xác nhận ID), function calling cho các công cụ riêng.
- Hàng đợi: `asyncio.Queue` trong tiến trình (một hàng đợi cho mỗi nhóm).
- Lưu trữ: **file `.txt`** tạm thời (xem mục 4b), không dùng SQLite/Redis/Postgres. Lớp `storage/` giấu sau một interface (`get/put/append`) để sau này đổi sang SQLite mà không sửa code khác.
- Cấu hình: biến môi trường (`.env`), không commit bí mật.
- Triển khai: chạy trực tiếp trên máy local (Windows), không cần Docker ở bước đầu.

### 3a. Nhận tin khi chạy local, chưa có domain

Zalo chỉ gọi webhook HTTPS công khai và từ chối localhost/IP nội bộ, nên có 2 cách:

| Cách | Ưu | Nhược |
|---|---|---|
| **A. `getUpdates` (long polling)** | Không cần domain/tunnel/HTTPS, đơn giản nhất cho máy local. Docs Zalo cho phép, nhưng ghi là dành cho dev/test | Docs cảnh báo production có thể sót sự kiện; không dùng chung với webhook (phải `deleteWebhook` trước); máy tắt thì bot ngừng |
| **B. Webhook + Cloudflare Tunnel** | Giống production, có header secret | Quick tunnel (trycloudflare) đổi URL mỗi lần chạy ⇒ phải gọi lại `setWebhook` mỗi lần khởi động; muốn URL cố định cần có domain |

Đề xuất: làm lớp nhận tin trừu tượng (`source`), cài **A (polling) làm mặc định** cho local, giữ **B** sẵn để chuyển sang khi có domain/VPS. Cả hai đều đẩy tin vào cùng một hàng đợi nên phần agent không đổi.

### 3b. Chạy 24/7 khi chưa có VPS

Bot dùng polling là một tiến trình phải sống liên tục. Các lựa chọn, theo thứ tự đề xuất:

| Lựa chọn | Cách làm | Lưu ý |
|---|---|---|
| **1. Máy Windows hiện tại luôn bật** (làm ngay) | Chạy bot như dịch vụ nền: Task Scheduler (chạy khi khởi động, tự chạy lại khi lỗi) hoặc NSSM; tắt Sleep/Hibernate; bật tự đăng nhập nếu cần | Mất điện/mạng/cập nhật Windows thì bot ngừng; phù hợp giai đoạn đầu |
| **2. Thiết bị rẻ chạy riêng** | Laptop cũ, Raspberry Pi hoặc mini PC chạy Python | Tách khỏi máy làm việc, ít bị tắt nhầm |
| **3. Dịch vụ cloud miễn phí** | Một số nhà cung cấp có gói free (ví dụ VM luôn bật) | **Chưa kiểm chứng** điều khoản/hạn mức hiện tại; tránh loại tự "ngủ" khi không có request, vì polling cần tiến trình chạy liên tục; thường cần thẻ thanh toán để đăng ký |
| **4. VPS nhỏ trả phí** (khi sẵn sàng) | Chuyển sang đó, có thể thêm domain để dùng webhook | Ổn định nhất |

Yêu cầu thiết kế để 24/7 đáng tin dù chọn cách nào:
- **Tự phục hồi**: vòng polling bắt mọi lỗi mạng/API, retry với backoff, không bao giờ thoát vì một lỗi.
- **Không mất việc khi khởi động lại**: lưu tin đã xử lý và trạng thái (chế độ trả lời, allowlist, lịch nhắc) trong file `.txt` (mục 4b), không chỉ giữ trong RAM.
- **Dedupe** theo `message_id` để khởi động lại không trả lời lặp.
- **Tin nhận lúc bot tắt thì bỏ qua** (đã chốt): khi khởi động, bot ghi lại thời điểm bắt đầu và loại mọi tin có `date` (mili giây) cũ hơn mốc đó, kể cả tin Zalo còn giữ lại và trả về qua `getUpdates`. Không làm vòng "xả" riêng: `getUpdates` là long polling (chờ tới 30 giây khi không có tin) và không có tham số offset, nên "xả cho hết" sẽ làm chậm khởi động mà không thêm gì so với lọc theo `date`. Code tự đổi `date` dạng giây sang mili giây; vẫn cần kiểm tra thực tế ở giai đoạn 1 rằng `date` của tin dùng cùng đồng hồ với máy chạy bot.
- **Nhắc việc** (khi làm tool sau) phải lưu vào file `.txt` và nạp lại khi khởi động, nếu không sẽ mất khi máy khởi động lại.
- **Healthcheck và log ra file** (xoay vòng) để biết bot chết lúc nào; tùy chọn: tự báo cho chủ bot qua Zalo khi khởi động lại.
- **Di chuyển dễ**: toàn bộ cấu hình ở `.env` + thư mục `data/` và `workspace/`, copy sang VPS là chạy.

## 4. Cấu trúc thư mục

```
pylosSever/
├─ PLAN.md
├─ README.md             # cài đặt và chạy
├─ pyproject.toml
├─ .env.example
├─ src/bot/
│  ├─ cli.py             # python -m bot run|console|me|set-webhook|health...
│  ├─ app.py             # lõi: lọc tin, chế độ all/default, hàng đợi theo chat, gửi trả lời
│  ├─ commands.py        # /mode /allow /deny /status /reset /id /help
│  ├─ config.py          # đọc .env, báo thiếu biến
│  ├─ ratelimit.py       # giới hạn tin/phút theo người và theo chat
│  ├─ text.py            # chia tin <= 2000 ký tự, bỏ markdown
│  ├─ logging_setup.py   # log console + file xoay vòng, che token
│  ├─ zalo/
│  │  ├─ client.py       # gọi Zalo Bot API
│  │  └─ models.py       # phân tích sự kiện/tin nhắn
│  ├─ sources/
│  │  ├─ polling.py      # getUpdates (mặc định)
│  │  └─ webhook.py      # FastAPI endpoint + kiểm tra secret header
│  ├─ agent/
│  │  ├─ runner.py       # Gemini + vòng lặp function calling
│  │  ├─ prompts.py      # system prompt từ workspace/*.md
│  │  └─ tools/          # registry tool (rỗng, thêm file mới để thêm tool)
│  └─ storage/           # file .txt: groups, seen, history, state, usage, failed + khóa phiên bản
├─ data/                 # "database" dạng .txt, không commit
├─ workspace/            # file .md của bot (xem 4b)
├─ logs/                 # bot.log, supervisor.log
├─ tests/
└─ scripts/              # run-forever.ps1, install-task.ps1, uninstall-task.ps1
```

### 4b. Lưu trữ `.txt` và workspace `.md`

Mình hiểu yêu cầu như sau (sửa nếu sai): **dữ liệu/trạng thái** của bot lưu trong file `.txt`; mọi **file workspace** (những gì bot và bạn đọc/viết như văn bản: prompt, ghi chú, bộ nhớ, tài liệu) là `.md`.

`data/` (trạng thái máy đọc, đuôi `.txt`, mỗi dòng một bản ghi JSON, gọi là JSON Lines):

| File | Nội dung |
|---|---|
| `data/groups.txt` | Mỗi nhóm một dòng: `chat.id`, đã cho phép chưa, chế độ `all`/`default` |
| `data/seen.txt` | `message_id` đã xử lý (chỉ giữ N mã gần nhất) |
| `data/state.txt` | Thời điểm khởi động, lần poll cuối, tin cuối (dùng cho `health`) |
| `data/usage.txt` | Số token Gemini đã dùng hôm nay, nhóm đã được báo hết hạn mức |
| `data/failed.txt` | Tin gửi thất bại sau khi đã thử lại (dead-letter) |
| `data/bot.lock` | Khóa để không chạy hai bot cùng lúc |
| `data/history/<chat_id>.txt` | Lịch sử hội thoại của từng nhóm (mỗi lượt một dòng; chỉ nạp N dòng cuối vào prompt) |
| `data/reminders.txt` | Lịch nhắc việc, khi làm tool sau |

`workspace/` (văn bản, đuôi `.md`):

| File | Nội dung |
|---|---|
| `workspace/SYSTEM.md` | System prompt của trợ lý, sửa tay được, nạp lúc khởi động hoặc khi file đổi |
| `workspace/MEMORY.md` | Điều trợ lý cần nhớ lâu dài (sở thích, ghi chú chung) |
| `workspace/notes/<chat_id>.md` | Ghi chú theo nhóm, khi làm tool ghi chú sau |
| `workspace/README.md` | Cách dùng lệnh `/mode`, `/allow`, `/deny` |

Để file `.txt` không hỏng và không mất dữ liệu:
- **Ghi nguyên tử**: file ghi đè (`groups.txt`, `state.txt`, `usage.txt`) ghi ra file tạm rồi `os.replace`, để mất điện giữa chừng không bị file cụt. File chỉ nối thêm (`history`, `seen`) dùng append một dòng mỗi lần.
- **Một tiến trình ghi duy nhất** (một bot chạy); trong tiến trình dùng khóa `asyncio.Lock` cho mỗi file. Không chạy hai bản bot cùng lúc trên cùng `data/`.
- **Bỏ qua dòng hỏng**: khi đọc, dòng không phải JSON hợp lệ (ví dụ dòng cuối bị cụt) thì bỏ qua và ghi log, không làm bot sập.
- **Không phình vô hạn**: `seen.txt` và `history/*.txt` được cắt về N dòng cuối theo định kỳ.
- **Mã hóa UTF-8** (tiếng Việt), ghi `encoding="utf-8"` rõ ràng vì mặc định của Windows có thể khác.
- **Bí mật không ở đây**: token và API key chỉ ở `.env`. Thêm `data/` và `workspace/MEMORY.md`, `workspace/notes/` vào `.gitignore` vì có nội dung cá nhân.
- **Chống prompt injection**: nội dung `.md` do bot ghi (ghi chú, bộ nhớ) có thể chứa chữ do người trong nhóm viết; khi nạp vào prompt phải coi là dữ liệu, không phải chỉ thị.
- **Giới hạn của `.txt`**: tìm kiếm chậm khi dữ liệu lớn và không có giao dịch; với vài nhóm và lịch sử có cắt thì đủ dùng. Khi lớn hơn thì đổi `storage/` sang SQLite.

### 4a. Cấu hình và bí mật để trống

`.env.example` (commit được) liệt kê biến, giá trị để trống; `.env` thật (không commit, thêm vào `.gitignore`) bạn điền sau:

```
ZALO_BOT_TOKEN=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-flash-lite
OWNER_ZALO_ID=
ALLOWED_CHAT_IDS=
RECEIVE_MODE=polling
DATA_DIR=data
WORKSPACE_DIR=workspace
LOG_LEVEL=INFO
```

- Khi `ZALO_BOT_TOKEN` hoặc `GEMINI_API_KEY` trống, bot **báo rõ thiếu biến nào và thoát**, không chạy nửa vời.
- Có chế độ `--dry-run`/mock cho test: giả lập Zalo và Gemini để kiểm thử logic mà không cần token.
- `OWNER_ZALO_ID` là ID Zalo của bạn, cần để cấp quyền bật/tắt chế độ. Chưa biết ID thì lần đầu chạy bot ghi log `from.id` của tin nhắn đầu tiên để bạn lấy.
- `ALLOWED_CHAT_IDS` trống ⇒ không nhóm nào được phục vụ (an toàn mặc định); lệnh của chủ bot có thể thêm/bớt nhóm lúc đang chạy (xem 5c).

## 5. Luồng xử lý một tin nhắn

1. Tin đến từ nguồn nhận (polling `getUpdates`, hoặc `POST /webhook/zalo` nếu dùng webhook).
2. (Chỉ với webhook) Server so sánh header `X-Bot-Api-Secret-Token` với secret đã cấu hình bằng `hmac.compare_digest` (so sánh hằng thời gian); sai ⇒ 403 (đúng như mẫu trong docs).
3. Phân loại theo `event_name`: chỉ xử lý `message.text.received` ở bước đầu; với image/sticker/voice/unsupported thì bỏ qua hoặc trả lời "chưa hỗ trợ". Chỉ trả lời khi `from.is_bot` là false.
4. Chống trùng: lưu `message_id` đã xử lý (file `data/seen.txt`, chỉ giữ N mã gần nhất); trùng ⇒ bỏ qua.
5. Trả `200` ngay, đẩy `{user_id, text, message_id}` vào hàng đợi.
6. Worker nạp lịch sử hội thoại của `user_id`, gọi agent.
7. Agent có thể gọi tool nhiều vòng, rồi ra câu trả lời cuối.
8. Chia câu trả lời thành các đoạn ≤ 2000 ký tự (giới hạn của `sendMessage`), gửi tuần tự bằng `ZaloClient` tới `chat.id`. Dùng `parse_mode` hoặc văn bản thuần, tránh markdown LLM sinh ra mà Zalo không hiển thị đúng.
9. Lưu lượt hội thoại và log.

## 5b. Agent (chi tiết)

- **System prompt**: vai trò bot, giọng điệu, ngôn ngữ mặc định tiếng Việt, những điều không được làm.
- **Tools**: **thêm sau**. Giai đoạn đầu chỉ dựng khung: một registry rỗng (`tools/__init__.py`) cho phép đăng ký hàm kèm mô tả và schema tham số, để về sau thêm tool bằng cách tạo một file mới mà không sửa vòng lặp agent. Khi chưa có tool nào, agent chỉ trò chuyện thường. Ý tưởng cho sau (chưa cam kết): giờ hiện tại, ghi chú, nhắc việc, tìm web, tính toán. Không làm RAG/FAQ vì không có dữ liệu riêng.
- **Gemini cụ thể**: truyền `system_instruction`, khai báo hàm dạng function declarations, tự chạy vòng lặp "model gọi hàm → chạy → trả kết quả" với giới hạn số vòng. Model "flash-lite" rẻ và nhanh nhưng yếu hơn ở suy luận nhiều bước, nên giữ tools đơn giản, mô tả hàm rõ ràng, và test kỹ các tình huống gọi sai tool.
- **Bộ nhớ**: giữ N lượt gần nhất mỗi user, tóm tắt khi quá dài để tiết kiệm token.
- **Giới hạn an toàn**: tối đa số vòng tool/lượt, timeout cho mỗi lần gọi, tool chỉ đọc là mặc định; tool ghi/xóa cần xác nhận.
- **Chống prompt injection**: nội dung người dùng và kết quả tool luôn coi là dữ liệu, không phải lệnh; không đưa bí mật vào prompt.

## 5c. Chat nhóm

Vì dùng trong nhóm, bot phải biết **khi nào được phép trả lời** và **nhớ theo ai/nhóm nào**:

- **Khóa hội thoại**: dùng `chat.id` (nhóm có một lịch sử chung), kèm `from.display_name` trong từng lượt để model biết ai đang nói. Không trộn lịch sử giữa các nhóm.
- **Hai chế độ trả lời** (mỗi nhóm một chế độ, lưu trong `data/groups.txt`, chủ bot bật/tắt bằng lệnh):
  - `all`: trả lời **mọi** tin nhắn văn bản trong nhóm.
  - `default`: **chỉ trả lời những tin gọi bot**, tức tin bắt đầu bằng một từ trong `BOT_TRIGGERS` (mặc định `/bot`, có thể thêm tên bot như `@Trợ lý`); các tin khác bỏ qua. Chưa nhận diện được "trả lời (quote) tin của bot" vì payload trong docs không có trường nào cho việc đó; xem lại khi có payload thật. (Mình hiểu "mặc định trả lời 1 tin" theo nghĩa này; nếu bạn muốn nghĩa khác, nói lại.) Chế độ mặc định khi thêm nhóm mới là `default`, vì an toàn và tiết kiệm token.
  - Lệnh điều khiển (ví dụ `/mode all`, `/mode default`, `/mode` để xem) **chỉ chấp nhận từ `OWNER_ZALO_ID`**; người khác gõ lệnh thì bỏ qua.
  - Cảnh báo chi phí: ở `all`, mỗi tin trong nhóm là một lần gọi Gemini, nên giữ rate limit và hạn mức token mỗi ngày (mục 6); quá hạn mức thì tạm tự về `default` và báo chủ bot.
  - Lưu ý chưa kiểm chứng: nếu hóa ra Zalo chỉ gửi cho bot các tin có nhắc tên bot, thì hai chế độ không khác nhau về dữ liệu nhận được; giai đoạn 1 sẽ cho biết.
- **Allowlist nhóm** (thêm sau): chỉ phục vụ các `chat.id` được cho phép; mới cài thì rỗng. Chủ bot thêm/bớt bằng lệnh (ví dụ `/allow` gõ ngay trong nhóm đó, `/deny`) và lưu trong `data/groups.txt`, không cần sửa tay hay khởi động lại. Nhóm lạ nhắn vào ⇒ bỏ qua, không gọi Gemini.
- **Quyền theo người**: tool nhạy cảm (ghi chú riêng, nhắc việc) gắn với `from.id`; dữ liệu của người này không hiện cho người khác trong nhóm.
- **Rate limit theo nhóm và theo người** để một người spam không làm hết quota.
- **Nhiều người cùng nhắn**: xử lý tuần tự theo từng `chat.id` (một hàng đợi mỗi nhóm) để câu trả lời không lẫn.
- **Chống prompt injection**: trong nhóm, bất kỳ ai cũng có thể viết tin có nội dung "bỏ qua hướng dẫn"; tool ghi/xóa phải kiểm tra người gọi, không chỉ tin vào lời model.

## 6. Bảo mật và vận hành

- Xác thực webhook bằng `X-Bot-Api-Secret-Token` (secret dài, ngẫu nhiên, 8–256 ký tự) và chỉ nhận qua HTTPS. Lưu ý đây là secret tĩnh, lộ là mất tác dụng; nên đổi định kỳ bằng `setWebhook` lại. Nếu muốn chắc hơn, thêm allowlist IP nếu Zalo công bố dải IP (chưa thấy trong docs).
- Token bot nằm trong URL gọi API nên **không được log URL đầy đủ**.
- Bí mật (token Zalo, API key Gemini) chỉ ở biến môi trường/secret manager; không ghi vào log.
- Rate limit theo user (ví dụ N tin/phút) để tránh spam và tốn chi phí.
- Ngân sách chi phí: giới hạn token mỗi lượt, mỗi ngày; cảnh báo khi vượt.
- Lưu dữ liệu cá nhân tối thiểu, có chính sách xóa theo yêu cầu.
- Log có cấu trúc, gắn `message_id`; theo dõi lỗi (Sentry) và số liệu (độ trễ, tỉ lệ lỗi).
- Retry có backoff khi gửi tin Zalo thất bại; đưa vào dead-letter nếu vẫn lỗi.
- (OA) Job refresh access token trước khi hết hạn, lưu refresh token an toàn.

## 7. Lộ trình

| Giai đoạn | Nội dung | Kiểm chứng |
|---|---|---|
| 0. Khởi tạo | Repo, `pyproject`, `.env.example` (trống), `.gitignore`, mock Zalo/Gemini, lint | `pytest` chạy **không cần token** |
| 1. Echo bot *(cần bot token)* | `ZaloClient` + nguồn nhận tin `getUpdates` (polling); gọi `getMe` xem `can_join_groups`; bot lặp lại tin nhắn, thử cả chat riêng và nhóm, **ghi lại payload thật của nhóm** | Nhắn trên Zalo thấy bot echo; biết chắc bot nhận gì trong nhóm |
| 1c. Chế độ + allowlist | Lưu trạng thái nhóm trong `data/groups.txt`; lệnh `/mode`, `/allow`, `/deny` chỉ cho chủ bot; lọc theo chế độ | Test: `default` bỏ qua tin thường, `all` trả lời hết, người lạ không đổi được chế độ |
| 1b. Webhook (tùy chọn) | Endpoint + kiểm tra secret header + Cloudflare Tunnel + `setWebhook` | `verification.ok` |
| 2. Agent cơ bản *(cần API key Gemini)* | Gọi Gemini, system prompt, trả lời văn bản | Hỏi đáp tiếng Việt ổn định |
| 3. Hàng đợi + chống trùng | Trả 200 ngay, worker nền, dedupe | Gửi lại sự kiện không trả lời 2 lần |
| 4. Bộ nhớ hội thoại | Lưu lịch sử theo user, tóm tắt | Bot nhớ ngữ cảnh nhiều lượt |
| 5. Tools *(sau, khi bạn quyết định)* | Registry + vòng lặp tool an toàn trước, rồi từng tool một | Agent gọi đúng tool, có giới hạn vòng |
| 6. Bảo mật và giới hạn | Rate limit, ngân sách token, log, retry | Spam không làm sập/tốn tiền |
| 7. Chạy 24/7 trên máy hiện tại | Dịch vụ nền (Task Scheduler/NSSM), tự khởi động lại, tắt Sleep, log xoay vòng, healthcheck | Khởi động lại máy/ngắt mạng vẫn tự chạy lại, không trả lời trùng, không trả lời tin cũ từ lúc bot tắt |
| 8. Chuyển lên VPS (khi có) | Copy `.env` + `data/` + `workspace/`; tùy chọn domain + webhook | Bot chạy ổn định ngoài máy cá nhân |
| 9. Mở rộng | Ảnh/file, thêm OA, dashboard | Theo nhu cầu |

## 8. Rủi ro

| Rủi ro | Cách xử lý |
|---|---|
| Webhook timeout vì LLM chậm | Trả 200 ngay, xử lý nền |
| Có thể bị gửi lại sự kiện (docs không nói rõ) | Dedupe theo `message_id` |
| Câu trả lời LLM vượt 2000 ký tự | Chia đoạn, hoặc yêu cầu agent trả lời ngắn |
| Chat nhóm còn Beta, hành vi chưa rõ | Giai đoạn 1 thử thực tế và ghi payload; thiết kế theo mục 5c |
| Bot trong nhóm tốn token vì đọc mọi tin | Chỉ gọi LLM khi được gọi tên/trả lời bot (nếu nhận được mọi tin) |
| Model ID Gemini sai hoặc đổi | Cấu hình ID qua biến môi trường, xác nhận trên Google AI Studio |
| Máy local tắt / mất mạng / Windows tự cập nhật khởi động lại | Dịch vụ nền tự chạy lại, lưu trạng thái trong file `.txt`, dedupe; về lâu dài dùng VPS (mục 3b). Tin gửi lúc bot tắt: **đã chốt là bỏ qua**, xem mục 3b |
| Chủ bot bị giả mạo lệnh `/mode` | Chỉ tin `from.id` khớp `OWNER_ZALO_ID`, không tin tên hiển thị |
| Quên điền token/key | Kiểm tra lúc khởi động, báo rõ biến thiếu rồi thoát |
| Log làm lộ bot token (nằm trong URL) | Che token trong log/exception |
| Người dùng spam, tốn chi phí | Rate limit + hạn mức token |
| Prompt injection | Tách dữ liệu/lệnh, tool quyền tối thiểu |
| Token Zalo hết hạn (OA) | Job refresh + cảnh báo khi lỗi |
| API Zalo thay đổi | Gói gọn trong `zalo/client.py`, có test hợp đồng |

## 9. Cần bạn xác nhận

Đã chốt ở mục 0. Việc **bạn sẽ bổ sung sau** (không chặn việc dựng khung):

- Bot token Zalo, API key Gemini (điền vào `.env`).
- `OWNER_ZALO_ID` của bạn (bot ghi log ID ở tin nhắn đầu tiên).
- Danh sách nhóm được dùng (thêm bằng lệnh `/allow`).
- Các tool.

Đã xác nhận: chế độ `default` là "chỉ trả lời tin gọi bot" (mục 5c); tin nhận lúc bot tắt thì bỏ qua (mục 3b).

## 10. Tiến độ

Đã làm (2026-10-22), 61 test qua, chạy được không cần token:

- [x] Giai đoạn 0: khung dự án, `.env.example` trống, mock Zalo/Gemini, `python -m bot console` để chat thử.
- [x] Giai đoạn 1: `ZaloClient`, polling `getUpdates`, `getMe` lúc khởi động (log `can_join_groups`). Đã gọi thử API thật bằng token giả: đúng URL, lỗi `401 Unauthorized` được xử lý (bot thoát mã 2).
- [x] Giai đoạn 1b: webhook FastAPI + kiểm tra `X-Bot-Api-Secret-Token`, lệnh `set-webhook`.
- [x] Giai đoạn 1c: chế độ `all`/`default`, allowlist, lệnh chủ bot.
- [x] Giai đoạn 2: Gemini (`google-genai`), system prompt từ `workspace/SYSTEM.md` + `MEMORY.md`. Chưa gọi thử Gemini thật vì chưa có key.
- [x] Giai đoạn 3–4: hàng đợi theo chat, chống trùng, lịch sử theo nhóm.
- [x] Giai đoạn 5 (khung): registry tool rỗng + vòng lặp function calling có giới hạn; chưa có tool.
- [x] Giai đoạn 6: rate limit, hạn mức token ngày, retry + `failed.txt`, log che token.
- [x] Giai đoạn 7: `scripts/install-task.ps1` (Task Scheduler) + `run-forever.ps1` tự khởi động lại.

Còn lại, cần bạn:

1. Điền `ZALO_BOT_TOKEN`, `GEMINI_API_KEY` vào `.env`; xác nhận model ID.
2. Chạy `python -m bot me` xem `can_join_groups`; thêm bot vào nhóm, chạy bot, nhắn thử. Xem `logs/bot.log` để lấy `OWNER_ZALO_ID` và kiểm tra payload nhóm thật (bot nhận mọi tin hay chỉ tin nhắc tên).
3. Gõ `/allow` trong nhóm, thử `/mode all` và `/mode default`.
4. Cài chạy nền: `scripts/install-task.ps1`, tắt Sleep của máy.
5. Thêm tool khi cần (giai đoạn 5).

## 11. Kế hoạch: giao diện quản lý bot (web dashboard)

### 11.1 Mục tiêu

Một trang web chạy trên máy này để làm bằng chuột những việc hiện phải gõ lệnh hoặc sửa file:

- Bật/tắt/khởi động lại bot (thay cho `gateway start|stop|restart`).
- Xem trạng thái và log (thay cho `gateway status|logs`).
- Quản lý nhóm: cho phép/chặn, đổi chế độ `all`/`default` (thay cho `/allow`, `/deny`, `/mode`).
- Sửa `workspace/SYSTEM.md` và `MEMORY.md`.
- Xem lịch sử hội thoại, mức dùng token, tin gửi lỗi.
- Chat thử với trợ lý mà không cần Zalo.

Không làm ở giai đoạn đầu: đăng nhập nhiều người dùng, truy cập từ Internet, ứng dụng di động.

### 11.2 Kiến trúc

```
Trình duyệt ──HTTP (127.0.0.1:8081)──► Admin server (FastAPI, tiến trình riêng)
                                          │  đọc: data/*.txt, logs/bot.log, workspace/*.md
                                          │  ghi: groups.txt, workspace/*.md, .env (có sao lưu)
                                          │  điều khiển: gateway.start/stop/restart (đã có sẵn)
                                          ▼
                                   Bot (tiến trình riêng, `python -m bot run`)
```

Quyết định thiết kế và lý do:

1. **Admin server là tiến trình riêng**, không nhúng vào bot. Nếu nhúng, bot không thể tự tắt/bật chính nó, và lỗi giao diện có thể làm sập bot. Admin server tái dùng `bot/gateway.py` để bật/tắt bot.
2. **Giao tiếp với bot qua file, không qua API nội bộ.** Bot hiện giữ `groups.txt` trong RAM và ghi đè cả file mỗi lần đổi, nên nếu giao diện ghi file thì bot sẽ ghi đè mất. Cách sửa: `GroupStore` kiểm tra thời gian sửa file (mtime) trước mỗi lần đọc và nạp lại nếu đổi, và mỗi lần ghi phải đọc lại bản mới nhất trước (đọc-sửa-ghi). `SYSTEM.md`/`MEMORY.md` đã tự nạp lại khi file đổi nên không cần sửa gì. Đơn giản hơn một API nội bộ và vẫn dùng được khi bot đang tắt.
3. **Không cần bước build frontend**: một trang HTML + JavaScript thuần, FastAPI phục vụ file tĩnh. Thư viện giao diện (nếu dùng) đặt cục bộ trong `src/bot/admin/static/`, không tải từ CDN, để chạy được khi mất mạng. Cập nhật trạng thái bằng polling 3 giây; log theo dõi bằng Server-Sent Events.
4. **Cổng riêng, mặc định 8081**, chỉ lắng nghe `127.0.0.1`.

### 11.3 Các trang

| Trang | Chức năng | Dữ liệu |
|---|---|---|
| Tổng quan | Chạy/dừng, pid, poll cuối, tin cuối, token hôm nay trên hạn mức, số nhóm; nút Bật / Tắt / Khởi động lại; cảnh báo (token Zalo/Gemini lỗi, tin gửi thất bại) | `state.txt`, `usage.txt`, `groups.txt`, `failed.txt`, `gateway.status()` |
| Nhóm | Bảng nhóm: nhãn tự đặt, `chat_id`, được phép (bật/tắt), chế độ `all`/`default`, lần nhắn cuối; nút xóa lịch sử | `groups.txt`, `history/` |
| Hội thoại | Xem lịch sử từng chat (chỉ đọc), có tên người nói | `history/<chat_id>.txt` |
| Chỉ dẫn | Soạn `SYSTEM.md` và `MEMORY.md`, nút Lưu, tự sao lưu bản trước | `workspace/*.md` |
| Cài đặt | Các giá trị không bí mật của `.env` (model, từ gọi bot, hạn mức, giới hạn tin/phút...); khóa/token chỉ có ô "đặt giá trị mới", không bao giờ hiện lại; sửa xong có nút "Khởi động lại bot" | `.env` |
| Log | Xem `bot.log` theo thời gian thực, lọc theo mức (INFO/WARNING/ERROR) | `logs/bot.log` |
| Tin lỗi | Danh sách tin Zalo gửi thất bại; nút Gửi lại / Bỏ | `failed.txt` |
| Chat thử | Khung chat với trợ lý (dùng cùng `GeminiAgent`, cùng prompt) để thử `SYSTEM.md` trước khi dùng thật; không gửi lên Zalo, không tính vào lịch sử nhóm | `agent/` |
| Tool | Danh sách tool đã nạp (khi có); sau này bật/tắt từng tool | `agent/tools` |

### 11.4 API (JSON, dưới `/api`)

| Phương thức | Đường dẫn | Việc |
|---|---|---|
| GET | `/status` | trạng thái bot, token, cảnh báo |
| POST | `/bot/start`, `/bot/stop`, `/bot/restart` | điều khiển bot qua `gateway` |
| GET | `/groups` | danh sách nhóm |
| PATCH | `/groups/{chat_id}` | `{allowed?, mode?, label?}` |
| DELETE | `/groups/{chat_id}/history` | xóa lịch sử |
| GET | `/history/{chat_id}?n=100` | lịch sử |
| GET, PUT | `/workspace/SYSTEM` và `/workspace/MEMORY` | đọc/ghi file `.md` |
| GET, PUT | `/settings` | đọc/ghi cài đặt không bí mật; PUT riêng `/secrets/{name}` chỉ ghi |
| GET | `/logs?n=200&level=` và `/logs/stream` | log, SSE |
| GET, POST | `/failed` và `/failed/{id}/retry` | tin lỗi |
| POST | `/playground` | gửi một câu cho agent, trả lời |

### 11.5 Bảo mật (quan trọng nhất của phần này)

Giao diện này điều khiển một bot có khóa API và quyền nhắn tin trong nhóm, nên:

- **Chỉ lắng nghe `127.0.0.1`.** Không mở ra mạng LAN hay Internet ở giai đoạn đầu. Muốn truy cập từ điện thoại hoặc từ xa thì làm ở giai đoạn sau, kèm HTTPS và đăng nhập đầy đủ.
- **Bắt buộc mã truy cập**: `ADMIN_TOKEN` trong `.env` (chuỗi ngẫu nhiên dài). Gửi qua header `Authorization`; trang đăng nhập lưu vào bộ nhớ trình duyệt. Không có token thì mọi `/api` trả 401. Nếu `ADMIN_TOKEN` trống, admin server từ chối khởi động (giống cách bot từ chối khi thiếu token Zalo).
- **Chống tấn công từ trang web khác đang mở trên cùng máy** (một trang web độc hại có thể gọi `http://127.0.0.1:8081`): kiểm tra header `Host` (chặn DNS rebinding), kiểm tra `Origin` với các yêu cầu ghi, không bật CORS, token nằm ở header chứ không ở cookie.
- **Bí mật không rời khỏi máy chủ**: API không bao giờ trả `ZALO_BOT_TOKEN`, `GEMINI_API_KEY`, `ADMIN_TOKEN`; chỉ trả "đã đặt / chưa đặt". Log và thông báo lỗi của admin server dùng chung bộ lọc che bí mật đã có.
- **Ghi `.env` an toàn**: ghi nguyên tử, lưu bản `.env.bak` trước khi đổi, chỉ cho sửa các khóa nằm trong danh sách cho phép, kiểm tra giá trị (kiểu số, khoảng hợp lệ) bằng đúng `Settings.from_env`.
- **Chặn đường dẫn lạ**: chỉ đọc/ghi `SYSTEM.md` và `MEMORY.md` trong `workspace/`; `chat_id` trong URL phải qua cùng hàm làm sạch tên file của `HistoryStore`.
- **Quyền riêng tư**: trang Hội thoại cho đọc nội dung chat của người khác trong nhóm. Chỉ chủ máy truy cập được (nhờ ràng buộc ở trên), nhưng cần cân nhắc có bật trang này không; nên có công tắc `ADMIN_SHOW_HISTORY` (mặc định bật).
- **Nội dung hiển thị là dữ liệu không đáng tin**: tin nhắn, tên người dùng, log phải được escape khi hiển thị (chống XSS), không dùng `innerHTML` với dữ liệu thô.

### 11.6 Việc phải bổ sung vào bot hiện có

| Cần thêm | Lý do |
|---|---|
| `GroupStore` nạp lại khi file đổi + đọc-sửa-ghi | để thay đổi từ giao diện có hiệu lực ngay và không bị bot ghi đè |
| `data/usage_daily.txt`: token theo từng ngày | `usage.txt` hiện chỉ giữ ngày hôm nay, không vẽ được biểu đồ |
| Đếm số tin nhận/trả lời/lỗi theo ngày | cho trang Tổng quan |
| Lưu `last_seen` và tên người nhắn gần nhất của mỗi nhóm | Zalo chỉ cho `chat_id`, không có tên nhóm; cần nhãn do bạn tự đặt (`label`) và dấu hiệu nhóm còn hoạt động |
| Cho phép `failed.txt` đánh dấu "đã gửi lại" | nút Gửi lại / Bỏ |
| Hàm gửi tin dùng lại được từ bên ngoài (`Bot.send_to`) | để "Gửi lại" đi qua đúng đường retry |
| Tách `Settings` thành "đọc/ghi từng khóa" | để trang Cài đặt kiểm tra giá trị bằng đúng quy tắc của bot |

### 11.7 Thư mục dự kiến

```
src/bot/admin/
├─ __init__.py
├─ server.py        # create_app(), middleware token/Host/Origin
├─ routes/          # status, groups, workspace, settings, logs, failed, playground
├─ envfile.py       # đọc/ghi .env giữ nguyên chú thích, danh sách khóa cho phép, che bí mật
└─ static/
   ├─ index.html
   ├─ app.js
   └─ style.css      # sáng/tối theo hệ điều hành, dùng được ở màn hình hẹp
tests/test_admin_*.py
```

Lệnh chạy: `python -m bot admin` (cổng `ADMIN_PORT`, mặc định 8081); `python -m bot gateway ...` giữ nguyên. Biến mới trong `.env.example`: `ADMIN_TOKEN=`, `ADMIN_PORT=8081`, `ADMIN_SHOW_HISTORY=true`.

### 11.8 Lộ trình

| Giai đoạn | Nội dung | Kiểm chứng |
|---|---|---|
| A. Nền | Khung FastAPI, middleware token/Host/Origin, `python -m bot admin`, trang Tổng quan chỉ đọc (trạng thái, token, nhóm) | Không token ⇒ 401; Host lạ ⇒ bị chặn; trang hiện đúng số liệu thật |
| B. Điều khiển | Nút Bật/Tắt/Khởi động lại; bổ sung `GroupStore` nạp lại khi đổi; trang Nhóm (cho phép, chế độ, nhãn) | Đổi chế độ trên web ⇒ bot đang chạy áp dụng ở tin kế tiếp mà không cần restart; test hai bên ghi cùng lúc không mất dữ liệu |
| C. Nội dung | Trang Chỉ dẫn (sửa `.md` kèm sao lưu), Log (có SSE), Hội thoại | Sửa `SYSTEM.md` trên web ⇒ bot dùng ngay ở tin sau; log hiện gần như tức thời |
| D. Cài đặt | Trang Cài đặt và `envfile.py`: sửa khóa không bí mật, đặt khóa bí mật chỉ-ghi, nút Khởi động lại | `.env` giữ nguyên chú thích và thứ tự; API không bao giờ trả bí mật (có test); giá trị sai bị từ chối |
| E. Vận hành | Trang Tin lỗi + Gửi lại, biểu đồ token theo ngày, cảnh báo trên Tổng quan | Gửi lại một tin lỗi thành công và biến mất khỏi danh sách |
| F. Chat thử | Trang Chat thử dùng chung agent và prompt | Câu trả lời giống bot thật; không ghi vào lịch sử nhóm |
| G. Chạy nền | Admin server cũng chạy nền được và tự bật cùng bot qua Task Scheduler; cập nhật README | Mở `http://127.0.0.1:8081` sau khi đăng nhập Windows là dùng được |
| H. (sau) Truy cập từ xa | HTTPS, đăng nhập đúng nghĩa, có thể qua Cloudflare Tunnel | Chỉ làm khi bạn cần; xem lại mục 11.5 trước |

Mỗi giai đoạn có test tự động: API (bằng `TestClient`), bảo mật (401/Host/Origin/che bí mật/đường dẫn lạ), và ghi file đồng thời.

### 11.9 Rủi ro

| Rủi ro | Cách xử lý |
|---|---|
| Giao diện và bot cùng ghi một file `.txt` | Nạp lại khi đổi + đọc-sửa-ghi (11.6); phần nào còn xung đột thì chuyển sang "bot là nơi duy nhất ghi, giao diện gửi lệnh qua file hàng đợi" |
| Rò rỉ khóa API qua giao diện | API không trả bí mật, có test chặn hồi quy; che bí mật trong log |
| Trang web ngoài gọi vào cổng quản trị | Token ở header, kiểm tra Host/Origin, không CORS |
| Người dùng sửa `.env` sai làm bot không lên | Kiểm tra giá trị trước khi ghi, giữ `.env.bak`, nút khôi phục |
| Trang Hội thoại lộ chat riêng tư | Công tắc `ADMIN_SHOW_HISTORY`, chỉ localhost |
| Tăng độ phức tạp cho dự án nhỏ | Giai đoạn A–C đã đủ dùng; D–F làm khi thật sự cần |

### 11.10 Cần bạn xác nhận trước khi làm

1. Chỉ dùng trên máy này, hay cần mở ra điện thoại/mạng LAN? (ảnh hưởng đến mục 11.5 và giai đoạn H)
2. Có muốn xem nội dung hội thoại trên giao diện không, hay chỉ cần trạng thái và cài đặt?
3. Trang nào làm trước: mình đề xuất A → B → C (xem và điều khiển cơ bản).
4. Giao diện tiếng Việt là đủ, hay cần thêm tiếng Anh?
5. Bạn có muốn chỉnh `.env` (kể cả đặt khóa) ngay trên web, hay vẫn sửa tay file `.env` cho an toàn?

### 11.11 Tiến độ (2026-10-22)

Đã làm, 90 test qua; đã chạy thật trên máy này và chụp màn hình kiểm tra bằng Edge:

- [x] A. Nền: `python -m bot admin` (cổng 8081, chỉ `127.0.0.1`), token bắt buộc (tự tạo nếu trống), kiểm tra Host/Origin/Sec-Fetch-Site, CSP chặt, trang Tổng quan.
- [x] B. Điều khiển: Bật/Tắt/Khởi động lại qua `gateway`; `GroupStore` nạp lại khi file đổi + đọc-sửa-ghi; trang Nhóm (cho phép, chế độ, nhãn, xóa lịch sử).
- [x] C. Nội dung: trang Chỉ dẫn (sao lưu `workspace/.backup/`, giữ 20 bản), Log (lọc mức, theo dõi trực tiếp bằng fetch stream), Hội thoại.
- [x] D. Cài đặt: `admin/envfile.py` giữ chú thích, `.env.bak`, danh sách khóa cho phép, kiểm tra bằng `Settings.from_env`; khóa bí mật chỉ-ghi.
- [x] E. Vận hành: trang Tin lỗi (Gửi lại/Bỏ qua qua `failed_done.txt`), `data/stats.txt` theo ngày, biểu đồ 14 ngày, cảnh báo.
- [x] F. Chat thử: dùng chung `GeminiAgent` và prompt; tính token vào hạn mức, không ghi lịch sử nhóm.
- [x] G. Chạy nền: `python -m bot admin start|stop|restart|status`; `install-task.ps1` đăng ký thêm task `ZaloAssistantBotAdmin`.
- [ ] H. Truy cập từ xa: chưa làm (cần HTTPS + đăng nhập đúng nghĩa).

Khác với kế hoạch:
- API gom trong một file `admin/server.py` thay vì thư mục `routes/` (dự án nhỏ, dễ đọc hơn).
- Log trực tiếp dùng `fetch` đọc stream thay vì `EventSource`, vì `EventSource` không gửi được header `Authorization`.
- `ADMIN_TOKEN` trống thì tự tạo và ghi vào `.env` thay vì từ chối khởi động (kết quả an toàn như nhau: không bao giờ chạy khi không có mã).
- Khi bật tiến trình con, gateway bỏ các biến đã nạp từ `.env` để tiến trình con đọc `.env` mới nhất (nếu không, "Khởi động lại" sau khi sửa Cài đặt vẫn dùng giá trị cũ).
- Thêm: Gemini tự thử lại 2 lần khi lỗi mạng/5xx (log thật có một lần `httpx.ReadError`); lỗi mạng khi long polling chỉ cảnh báo khi lặp lại 3 lần.

## 12. Kế hoạch: file .exe mở giao diện quản lý bot (Windows)

### 12.1 Mục tiêu

Một file `ZaloBot.exe` để bạn bấm đúp là mở được giao diện quản lý trong một **cửa sổ riêng** (không phải gõ lệnh, không phải mở trình duyệt, không cần cài Python), kèm biểu tượng ở khay hệ thống để bot chạy nền.

Không làm ở giai đoạn đầu: macOS/Linux, tự cập nhật, bản cài đặt có chữ ký số.

### 12.2 Chọn cách làm

| Cách | Mô tả | Ưu | Nhược |
|---|---|---|---|
| A. Trình khởi chạy | exe chỉ bật server giao diện rồi mở trình duyệt mặc định | Đơn giản nhất, ít rủi ro | Không có cửa sổ riêng, không có biểu tượng khay |
| **B. Cửa sổ nhúng (đề xuất)** | exe chạy server giao diện và mở **cửa sổ riêng** hiển thị chính trang web hiện có, dùng WebView2 (có sẵn trên Windows 11, và trên Windows 10 đã cập nhật), thêm biểu tượng khay | Tái dùng 100% giao diện đã làm; trông như ứng dụng thật; đóng cửa sổ thì thu xuống khay | Thêm thư viện `pywebview`, `pystray`; file lớn hơn |
| C. Viết lại giao diện native (Tkinter/Qt) | Làm lại mọi trang bằng widget | Không phụ thuộc WebView2 | Tốn công nhất, phải làm lại và kiểm thử 9 trang, hai giao diện cần bảo trì song song |

Đề xuất **B**. Phương án dự phòng rẻ nếu WebView2 không có: mở bằng `msedge --app=http://127.0.0.1:8081` (cửa sổ không thanh địa chỉ) hoặc trình duyệt mặc định như cách A.

### 12.3 Kiến trúc

```
ZaloBot.exe (một file, nhiều chế độ)
├─ (không tham số) → GUI: [luồng chính] cửa sổ WebView2 + [luồng nền] server giao diện (FastAPI/uvicorn) + biểu tượng khay
├─ run              → bot Zalo chạy nền (không cửa sổ)
└─ admin, gateway, me, console... → giữ nguyên các lệnh hiện có
```

- **Bot vẫn là tiến trình riêng**: GUI bật nó bằng `gateway.start()` như bây giờ, nhưng lệnh khởi chạy khi đã đóng gói là `ZaloBot.exe run` thay vì `python -m bot run`. Nhờ đó đóng cửa sổ hay thoát GUI không làm bot chết.
- **Server giao diện chạy trong cùng tiến trình GUI** (luồng nền) thay vì tiến trình `admin` riêng. Cổng: `ADMIN_PORT`, nếu bận thì tự chọn cổng trống kế tiếp; danh sách Host cho phép đã tính theo cổng thực tế nên không phải sửa bảo mật.
- **Đăng nhập tự động**: GUI biết `ADMIN_TOKEN` (cùng tiến trình) nên mở cửa sổ ở `#token=...` và trang tự xóa khỏi địa chỉ, không phải gõ mã. Cách ràng buộc bảo mật cũ giữ nguyên (chỉ `127.0.0.1`, kiểm tra Host/Origin, CSP).
- **Một bản duy nhất**: chạy lần hai thì không mở bản mới, chỉ đưa cửa sổ đang chạy lên trước (dựa vào khóa `data/gui.lock` đã có cơ chế tương tự).
- **Gắn với giao diện đang chạy**: nếu `python -m bot admin start` đã chạy sẵn thì exe chỉ mở cửa sổ trỏ vào đó, không bật server thứ hai.

### 12.4 Biểu tượng khay (system tray)

Menu: Mở giao diện · Bật bot / Tắt bot (đổi theo trạng thái) · Khởi động cùng Windows (tích) · Thoát.
- Bấm X trên cửa sổ: thu xuống khay, bot vẫn chạy.
- "Thoát": đóng GUI; hỏi có tắt luôn bot không (mặc định: **không**, bot tiếp tục chạy nền như hiện nay).
- Biểu tượng đổi màu theo trạng thái bot (xanh chạy / xám dừng / đỏ có lỗi), lấy từ `gateway.status_info()` đã có.
- "Khởi động cùng Windows" thay cho `scripts/install-task.ps1`: tạo/xóa tác vụ Task Scheduler (hoặc shortcut trong thư mục Startup) trỏ tới `ZaloBot.exe --tray`, khởi động ẩn ở khay.

### 12.5 Những chỗ trong code hiện tại phải sửa để đóng gói được

Đây là phần dễ sai nhất, vì code hiện giả định chạy từ mã nguồn:

| Chỗ hiện tại | Vấn đề khi thành .exe | Cách sửa |
|---|---|---|
| `config.PROJECT_ROOT = parents[2]` của `config.py` | Trong exe, đường dẫn này nằm trong thư mục tạm của PyInstaller | Thêm `APP_HOME`: thư mục chứa `.exe` khi đóng gói, thư mục dự án khi chạy từ mã nguồn; `.env`, `data/`, `workspace/`, `logs/` đều tính từ đó |
| `gateway._spawn` dùng `[sys.executable, "-m", "bot", ...]` | Khi đóng gói, `sys.executable` chính là `ZaloBot.exe`, `-m bot` không hợp lệ | Nếu `sys.frozen` thì dùng `[sys.executable, <lệnh>]`; `cli.main` nhận lệnh trực tiếp |
| `admin/static/` đọc theo `Path(__file__)` | File tĩnh nằm trong gói đã giải nén | Khai báo `--add-data` và tìm bằng `sys._MEIPASS` khi đóng gói |
| `agent/tools/__init__.discover()` dùng `pkgutil.iter_modules` | Trong exe không quét được file `.py` thêm vào sau | Nạp thêm tool từ thư mục **bên ngoài** `tools/` cạnh exe bằng `importlib` theo đường dẫn; tool mẫu `_example.py` đặt ở đó |
| `workspace/SYSTEM.md`, `MEMORY.md` | Người dùng exe không có sẵn các file này | Lần chạy đầu tạo từ bản mẫu nhúng trong exe nếu thiếu |
| `.env` không được có trong exe | Bí mật lộ nếu vô tình đóng gói | `.env` luôn nằm ngoài exe; lần chạy đầu tạo từ `.env.example` nhúng sẵn và mở trang Cài đặt để điền khóa; kiểm tra bản build không chứa chuỗi token |
| `scripts/*.ps1` | Người dùng exe không cần PowerShell | Giữ cho người chạy từ mã nguồn; exe dùng mục "Khởi động cùng Windows" ở khay |
| Lệnh `console`, `me`, `set-webhook`... in ra terminal | Exe dạng cửa sổ không có console | Bản build tách hai exe nhỏ nếu cần: `ZaloBot.exe` (cửa sổ, không console) và `ZaloBotCli.exe` (console), hoặc chỉ giữ GUI + `run` ở bản đầu |
| Ghi log ra `stderr` | `stderr` rỗng khi chạy không console | Luôn ghi vào file log (`logs/gui.log`), kiểm tra `sys.stderr is None` |

### 12.6 Đóng gói

- Công cụ: **PyInstaller**, file `ZaloBot.spec` đặt trong repo, lệnh build `scripts/build-exe.ps1`.
- Hai kiểu:
  - **onefile** (đúng ý "1 file.exe"): một file duy nhất. Nhược: mỗi lần mở phải giải nén vào thư mục tạm nên khởi động chậm (vài giây), và dễ bị Windows Defender/SmartScreen báo nhầm hơn.
  - **onedir + trình cài đặt**: một thư mục, mở nhanh hơn, ít bị báo nhầm; kèm `ZaloBotSetup.exe` tạo bằng Inno Setup nếu muốn một file duy nhất để phát hành.
  - Đề xuất: làm **onefile** trước cho đúng yêu cầu, đo thời gian khởi động; nếu chậm hoặc bị chặn thì chuyển onedir + trình cài đặt.
- Cần khai báo thủ công cho PyInstaller (các thư viện nạp động): `uvicorn` (loops/protocols), `google.genai`, `pydantic`, `webview` (EdgeChromium), `pystray`, file tĩnh `admin/static/*`, mẫu `SYSTEM.md`, `.env.example`, biểu tượng `.ico`.
- Kích thước dự kiến: khoảng 60–120 MB (do `google-genai`, `pydantic`, `uvicorn`, `pywebview`). Chấp nhận được cho dùng cá nhân.
- Biểu tượng, tên sản phẩm và số phiên bản gắn vào exe (version info) để Task Manager hiển thị đúng tên.
- Dữ liệu (`data/`, `workspace/`, `.env`, `logs/`) nằm **cạnh exe** nên nâng cấp chỉ cần thay file exe. Nếu thư mục chứa exe không ghi được (ví dụ `C:\Program Files`) thì dùng `%LOCALAPPDATA%\ZaloAssistantBot`.

### 12.7 Bảo mật khi phát hành exe

- Exe chưa ký số sẽ hiện cảnh báo SmartScreen ("Windows đã bảo vệ PC của bạn") ở lần mở đầu, và đôi khi Defender báo nhầm với các file PyInstaller. Với dùng cá nhân thì chấp nhận được (bấm "Vẫn chạy"); muốn hết cảnh báo cần chứng chỉ ký mã (mất phí).
- Không bao giờ nhúng `.env`, token, `data/` vào exe; bước build có kiểm tra tự động (tìm chuỗi bí mật trong thư mục build).
- Cửa sổ nhúng chỉ được trỏ vào `http://127.0.0.1:<cổng>`, chặn mọi điều hướng ra ngoài (mở liên kết ngoài bằng trình duyệt mặc định).
- Mọi ràng buộc ở mục 11.5 giữ nguyên.

### 12.8 Lộ trình

| Giai đoạn | Nội dung | Kiểm chứng |
|---|---|---|
| 0. Tách đường dẫn | `APP_HOME`; `gateway._spawn` biết chạy khi đã đóng gói; thư mục tool ngoài; tạo file mẫu lần đầu; ghi log khi không có console | Test tự động cho đường dẫn ở hai chế độ (mã nguồn / giả lập `sys.frozen`); test hiện có vẫn qua |
| 1. GUI chạy từ mã nguồn | `python -m bot gui`: cửa sổ WebView2 + server nhúng + đăng nhập tự động + một bản duy nhất | Cửa sổ mở, vào thẳng Tổng quan không hỏi mã; mở lần hai thì chỉ đưa cửa sổ cũ lên trước |
| 2. Khay hệ thống | Biểu tượng + menu, thu xuống khay, đổi màu theo trạng thái, thoát có hỏi tắt bot | Đóng cửa sổ, bot vẫn chạy; "Tắt bot" từ khay tắt được bot |
| 3. Đóng gói onedir | `ZaloBot.spec`, `build-exe.ps1`, chạy thử trên thư mục sạch | Exe chạy trên máy/Windows Sandbox **không có Python**; bot nhận và trả lời được tin thật |
| 4. Onefile + hoàn thiện | Biểu tượng, version info, đo thời gian khởi động, kiểm tra chuỗi bí mật, khởi động cùng Windows | Mở < 10 giây; không có token trong exe; tự bật khi đăng nhập |
| 5. (tùy chọn) Trình cài đặt | Inno Setup, shortcut Start Menu, gỡ cài đặt giữ dữ liệu | Cài / gỡ / nâng cấp không mất `.env` và `data/` |

### 12.9 Rủi ro

| Rủi ro | Cách xử lý |
|---|---|
| Máy không có WebView2 | Tự phát hiện và dùng `msedge --app`, hoặc trình duyệt mặc định |
| Defender/SmartScreen chặn exe | Dùng bản PyInstaller mới, tắt UPX, thử onedir, báo cáo false positive cho Microsoft; chữ ký số nếu cần |
| Quên điều chỉnh một đường dẫn nên exe ghi dữ liệu vào thư mục tạm rồi mất | Test tự động giả lập `sys.frozen`; bước kiểm thử thủ công trên máy sạch ở giai đoạn 3 |
| Người dùng chạy hai bản (exe và `python -m bot run`) cùng thư mục | Khóa `bot.lock` đã chặn; GUI báo "đã có bot chạy" thay vì lỗi |
| `onefile` khởi động chậm | Chuyển onedir; hoặc giữ onefile nhưng GUI hiện màn hình chờ |
| Thêm tool mới không nhận khi đã đóng gói | Thư mục `tools/` ngoài exe (mục 12.5) |
| Hai server giao diện cùng chạy (exe và `admin start`) | GUI kiểm tra khóa `admin.lock`, nếu đang chạy thì chỉ mở cửa sổ trỏ vào |

### 12.10 Cần bạn xác nhận trước khi làm

1. **Một file duy nhất** (onefile, mở chậm hơn vài giây, dễ bị Defender báo nhầm) hay một thư mục kèm bộ cài (onedir, nhanh và êm hơn)?
2. Có cần biểu tượng khay và chạy nền khi đóng cửa sổ không? (đề xuất: có)
3. Khi thoát ứng dụng, bot nên **tiếp tục chạy** (đề xuất, giống hiện nay) hay tắt theo?
4. Để dữ liệu (`.env`, `data/`, `workspace/`) cạnh file exe, hay trong `%LOCALAPPDATA%`?
5. Chỉ chạy trên máy này, hay cần gửi exe cho người khác (nếu có thì cần tính đến chữ ký số và trang nhập khóa lần đầu)?

### 12.11 Tiến độ (2026-10-22)

Đã làm theo các lựa chọn đề xuất ở 12.10 (chưa có câu trả lời): **onefile**, có khay, **thoát ứng dụng thì bot vẫn chạy**, dữ liệu **cạnh exe**, chỉ dùng trên máy này. 110 test qua.

- [x] 0. Tách đường dẫn: `config.APP_HOME` (exe → thư mục chứa exe, không ghi được → `%LOCALAPPDATA%\ZaloAssistantBot`, ghi đè bằng `ZALOBOT_HOME`); `.env` chỉ đọc ở APP_HOME; `gateway.spawn_command` biết chạy từ exe; tool ngoài ở `tools/`; `bootstrap.ensure_home` tạo file mẫu lần đầu; log khi không có console.
- [x] 1. GUI: `python -m bot gui` / bấm đúp exe: cửa sổ WebView2, server giao diện chạy trong ứng dụng (tự chọn cổng trống nếu 8081 bận), đăng nhập tự động, mở trang Cài đặt nếu thiếu khóa, một bản duy nhất (`data/gui.lock` + cờ `data/gui.show`).
- [x] 2. Khay: menu, đổi màu theo trạng thái, bấm X thu xuống khay, "Khởi động cùng Windows" (HKCU\...\Run → `ZaloBot.exe gui --tray --start-bot`).
- [x] 3–4. Đóng gói onefile: `packaging/ZaloBot.spec`, `scripts/build-exe.ps1`, `packaging/check_secrets.py` (đọc cả phần đã nén trong exe), biểu tượng vẽ bằng Pillow, version info. Exe 33 MB.
- [ ] 5. Trình cài đặt: chưa làm.

Đã kiểm tra thật trên máy này:
- Exe trong thư mục trống: tạo `.env` + `ADMIN_TOKEN`, `workspace/`, `tools/_example.py`, mở trang Cài đặt; cổng 8081 bận thì dùng 8082.
- Exe với dữ liệu thật: bật/tắt/khởi động lại bot qua giao diện; bot chạy bằng `ZaloBot.exe run`.
- Bấm X: cửa sổ ẩn, tiến trình còn; mở lần hai: bản mới thoát, cửa sổ cũ hiện lại.
- Thời gian sẵn sàng: 4,6 giây (exe đã quen) đến khoảng 15 giây (exe mới build, lần đầu bị Defender quét).

Lỗi tìm thấy khi chạy thật và đã sửa:
- **PyInstaller ≥ 6.9: exe gọi lại chính nó dùng chung thư mục giải nén** → thoát ứng dụng sẽ xóa thư mục đó và bot chết theo. Sửa: đặt `PYINSTALLER_RESET_ENVIRONMENT=1` cho tiến trình bot (đã xác nhận: 2 thư mục `_MEI` riêng).
- Ép tắt exe onefile (`taskkill /F`) để lại thư mục `_MEI*` ~100 MB trong `%TEMP%` mỗi lần → bot giờ dừng êm qua file cờ `data/bot.stop` (~1 giây), chỉ ép tắt khi không dừng được.

Chưa kiểm chứng / còn rủi ro:
- Menu khay và thông báo khay chưa được bấm thử tự động (chỉ test các hàm phía sau).
- **Smart App Control đang bật trên máy này** và đã chặn một lần chạy exe mới build (Code Integrity event 3077); lần bấm đúp từ Explorer sau đó thì chạy. Mỗi lần build lại có thể bị chặn lại; cách chắc chắn là chữ ký số, hoặc chạy `pythonw -m bot gui` từ mã nguồn.
- Một lần chạy thử exe đầu tiên mở trang Tổng quan thay vì Cài đặt; không tái hiện được ở các lần sau (cả exe lẫn mã nguồn).
- Chưa thử trên máy khác / Windows Sandbox không có Python.
