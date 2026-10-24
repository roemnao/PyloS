# Bot trợ lý Zalo (Gemini)

Bot chạy trên **Zalo Bot Platform**, trả lời trong nhóm bằng **Gemini**. Bot nhận tin bằng `getUpdates` (polling), nên chạy được trên máy cá nhân, không cần domain. Bot cũng chạy được trên **một acc Zalo cá nhân** (xem [Chạy trên acc Zalo cá nhân](#chạy-trên-acc-zalo-cá-nhân-acc-phụ)).

Kế hoạch và các quyết định thiết kế nằm trong [PLAN.md](PLAN.md). Cách dùng lệnh trong Zalo nằm trong [workspace/README.md](workspace/README.md).

## Cài đặt (Windows)

Cần Python 3.11 trở lên. Mở PowerShell trong thư mục dự án:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Sau đó mở `.env` và điền:

- `ZALO_BOT_TOKEN`: token nhận được khi tạo bot bằng Zalo Bot Creator.
- `GEMINI_API_KEY`: API key lấy từ Google AI Studio.
- `GEMINI_MODEL`: kiểm tra lại đúng ID model trên Google AI Studio.

`OWNER_ZALO_ID` và `ALLOWED_CHAT_IDS` có thể để trống lúc đầu (xem phần "Lần chạy đầu tiên" bên dưới).

## Thử ngay, chưa cần token

```powershell
.venv\Scripts\python.exe -m pytest              # chạy toàn bộ test
.venv\Scripts\python.exe -m bot console         # chat thử trên terminal, giả lập một nhóm
```

Ở chế độ `console`:
- Chưa có `GEMINI_API_KEY` thì bot chỉ lặp lại tin nhắn (echo). Có key thì bot gọi Gemini thật.
- Dữ liệu chat thử lưu riêng trong `data/console`.
- Gõ `/allow`, rồi `/bot xin chào`, `/mode all`, `/status`... để thử các chế độ.

## Lần chạy đầu tiên với Zalo

1. Kiểm tra token và xem bot có vào được nhóm không (trường `can_join_groups`):

   ```powershell
   .venv\Scripts\python.exe -m bot me
   ```

2. Chạy bot (hoặc dùng `gateway start` để chạy nền):

   ```powershell
   .venv\Scripts\python.exe -m bot run
   ```

3. Thêm bot vào nhóm và nhắn `/id` trong nhóm. Khi `OWNER_ZALO_ID` còn trống, bot trả lời cho bất kỳ ai, và log in `from_id` của mọi người nhắn tới.
4. Điền `user_id` của bạn vào `OWNER_ZALO_ID` trong `.env`, rồi khởi động lại bot (Ctrl+C rồi chạy lại lệnh ở bước 2).
5. Trong nhóm, gõ `/allow`. Từ đây:
   - Bot trả lời tin bắt đầu bằng `/bot` (chế độ `default`).
   - `/mode all` để bot trả lời mọi tin.
6. Xem `logs/bot.log` để biết bot nhận được gì trong nhóm. Zalo chưa ghi rõ bot nhận mọi tin hay chỉ tin nhắc tên.

## Ứng dụng quản lý: ZaloBot.exe

Bấm đúp `D:\pylosSever\ZaloBot.exe`. Một cửa sổ "Quản lý Bot Zalo" mở ra (tự đăng nhập), kèm biểu tượng chữ **Z** ở khay hệ thống (góc phải thanh tác vụ; có thể nằm trong mũi tên ^).

- **Bấm X**: cửa sổ thu xuống khay, bot vẫn chạy. Bấm biểu tượng khay để mở lại.
- **Menu khay** (chuột phải): Mở giao diện · Bật/Tắt bot · Khởi động lại bot · **Khởi động cùng Windows** · Mở thư mục dữ liệu · Thoát (bot vẫn chạy) · Thoát và tắt bot.
- **Màu chấm trên biểu tượng**: xanh = bot đang chạy, cam = đang chạy nhưng có cảnh báo, xám = đã dừng.
- **Khởi động cùng Windows**: tích trong menu khay. Khi đăng nhập, ứng dụng tự chạy ẩn ở khay và bật bot. Không cần `install-task.ps1`.
- Mở exe lần hai chỉ đưa cửa sổ đang chạy lên, không mở thêm bản mới.
- Lần đầu chạy trong thư mục trống, exe tự tạo `.env`, `workspace/`, `tools/`, `logs/` và mở trang Cài đặt để bạn điền khóa.
- Dữ liệu nằm **cạnh exe** (`.env`, `data/`, `workspace/`, `logs/`). Muốn chuyển máy: chép cả thư mục.
- Tool tự viết: đặt file `.py` vào `tools/` cạnh exe (xem `tools/_example.py`), rồi khởi động lại bot.

Exe chưa có chữ ký số, nên **Windows có thể chặn** ("Windows đã bảo vệ PC của bạn" hoặc "An Application Control policy has blocked this file"), nhất là sau mỗi lần build lại. Máy này đang bật **Smart App Control**, cơ chế này chặn exe chưa ký mà không cho bấm "Vẫn chạy". Nếu bị chặn:
- Thử mở lại bằng cách bấm đúp trong Explorer (Windows tra uy tín trên mạng, đôi khi lần sau cho chạy).
- Hoặc chạy cùng ứng dụng đó từ mã nguồn (không bị chặn vì `pythonw.exe` đã được ký): `.venv\Scripts\pythonw.exe -m bot gui`.
- Không nên tắt Smart App Control chỉ vì bot: tắt rồi thì không bật lại được nếu không cài lại Windows.

Build lại exe (sau khi sửa code): `powershell -ExecutionPolicy Bypass -File scripts\build-exe.ps1`. Script build kèm bước kiểm tra exe không chứa token/khóa nào trong `.env`. Nếu exe đang chạy, thoát nó ở khay trước để script thay được file.

Lệnh dòng lệnh vẫn dùng được với exe, ví dụ `ZaloBot.exe gateway status` (kết quả in vào cửa sổ cmd).

## Giao diện quản lý (web)

```powershell
.venv\Scripts\python.exe -m bot admin start --open   # chạy nền và mở trình duyệt, đăng nhập sẵn
.venv\Scripts\python.exe -m bot admin                # hoặc chạy trong cửa sổ này (Ctrl+C để dừng)
.venv\Scripts\python.exe -m bot admin stop
```

Mở http://127.0.0.1:8081. Mã đăng nhập là `ADMIN_TOKEN` trong `.env`; nếu còn trống, lần chạy đầu sẽ tự tạo.

| Trang | Làm được gì |
|---|---|
| Tổng quan | Bật / tắt / khởi động lại bot, xem trạng thái, tin và token hôm nay, biểu đồ 14 ngày, cảnh báo |
| Nhóm | Đặt tên gợi nhớ, cho phép / chặn, đổi chế độ `all` / `default`, xóa lịch sử; có hiệu lực ngay, không cần khởi động lại |
| Hội thoại | Đọc lịch sử bot dùng làm ngữ cảnh (tắt được bằng `ADMIN_SHOW_HISTORY=false`) |
| Chỉ dẫn | Sửa `SYSTEM.md` và `MEMORY.md`, tự sao lưu vào `workspace/.backup/` |
| Chat thử | Nói chuyện với trợ lý mà không qua Zalo (token vẫn được tính) |
| Log | Xem log bot / giao diện, lọc theo mức, theo dõi trực tiếp |
| Tin lỗi | Gửi lại hoặc bỏ qua tin bot không gửi được |
| Cài đặt | Đăng nhập acc Zalo cá nhân bằng mã QR; sửa các giá trị trong `.env` (có sao lưu `.env.bak`); khóa bí mật chỉ đặt mới, không bao giờ hiện lại |

Bảo mật: giao diện chỉ mở ở `127.0.0.1` (không truy cập được từ máy khác), bắt buộc mã truy cập, chặn yêu cầu từ trang web khác. Đừng đưa cổng 8081 ra Internet.

## Quản lý bot chạy nền (gateway)

```powershell
.venv\Scripts\python.exe -m bot gateway start      # bật bot chạy nền, không cần giữ cửa sổ
.venv\Scripts\python.exe -m bot gateway status     # đang chạy hay dừng, poll cuối, token hôm nay, nhóm được phép
.venv\Scripts\python.exe -m bot gateway logs -n 50 # xem 50 dòng log cuối (thêm -f để theo dõi liên tục)
.venv\Scripts\python.exe -m bot gateway restart    # khởi động lại (dùng sau khi sửa .env)
.venv\Scripts\python.exe -m bot gateway stop       # tắt bot
```

- `start` chờ bot kiểm tra xong token Zalo rồi mới báo thành công; token sai thì báo lỗi kèm log ngay.
- Nếu đã cài Task Scheduler (mục bên dưới), `stop` cũng dừng task để bot không tự bật lại.
- Bot đang chạy trong một cửa sổ `python -m bot run` riêng thì `stop` không tắt được (không có file PID); bấm Ctrl+C ở cửa sổ đó rồi dùng `gateway start`.

## Chạy 24/7 trên máy này

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-task.ps1
```

- Script đăng ký hai Task Scheduler: `ZaloAssistantBot` (bot) và `ZaloAssistantBotAdmin` (giao diện). Chỉ muốn bot thì thêm `-NoAdmin`.
- Bot tự chạy khi bạn đăng nhập Windows, và tự khởi động lại sau 10 giây nếu thoát.
- Nếu `.env` sai (thiếu biến hoặc token sai), script dừng hẳn thay vì khởi động lại mãi. Xem `logs/supervisor.log`.

Để bot không ngừng khi máy ngủ, tắt Sleep (khi cắm sạc):

```powershell
powercfg /change standby-timeout-ac 0
```

Bot chỉ chạy khi bạn đã đăng nhập Windows. Muốn bot tự chạy sau khi máy khởi động lại mà không cần ai đăng nhập, hãy bật tự động đăng nhập Windows hoặc chuyển lên VPS.

Các lệnh khác:
- Gỡ task: `scripts\uninstall-task.ps1`.
- Kiểm tra bot còn chạy: `.venv\Scripts\python.exe -m bot health` (mã thoát 0 = ổn).

## Chuyển sang webhook (khi có domain hoặc VPS)

1. Trong `.env`: đặt `RECEIVE_MODE=webhook` và `WEBHOOK_SECRET` (8–256 ký tự ngẫu nhiên).
2. Đưa `http://WEBHOOK_HOST:WEBHOOK_PORT` ra Internet qua HTTPS, ví dụ bằng Cloudflare Tunnel hoặc reverse proxy.
3. Đăng ký webhook:

   ```powershell
   .venv\Scripts\python.exe -m bot set-webhook https://ten-mien-cua-ban/webhook/zalo
   ```

4. Chạy `python -m bot run` như bình thường.

Polling và webhook không dùng cùng lúc được. Khi chạy lại ở chế độ polling, bot tự gỡ webhook.

## Chạy trên acc Zalo cá nhân (acc phụ)

Thay vì Zalo Bot, bot có thể đăng nhập vào **một acc Zalo cá nhân** bằng cách **quét mã QR**, giống khi đăng nhập Zalo Web, rồi trả lời dưới tên acc đó. Bạn kết bạn, nhắn riêng hay thêm acc này vào nhóm như với người thật.

> ⚠️ Cách này dùng thư viện **không chính thức** [zlapi](https://pypi.org/project/zlapi/), giả làm Zalo Web. Nó **vi phạm điều khoản của Zalo**: acc có thể bị khoá bất cứ lúc nào. Thư viện cũng có thể ngừng chạy khi Zalo đổi giao thức. **Chỉ dùng acc phụ**, đừng dùng acc chính.

1. Cài thêm thư viện:

   ```powershell
   .venv\Scripts\python.exe -m pip install -e ".[personal]"
   ```

2. Trên điện thoại, đăng nhập Zalo bằng **acc phụ**.

3. Tạo mã QR bằng một trong hai cách sau.
   - **Giao diện quản lý** (khuyên dùng, chạy được cả trên VPS qua SSH tunnel): vào **Cài đặt**, bấm **Đăng nhập bằng mã QR**, mã hiện ngay trên trang.
   - **Dòng lệnh**: `python -m bot zalo-login`. Ảnh mã QR được lưu vào `data/zalo_qr.png` và tự mở. Trên máy không có màn hình, thêm `--no-open`.

4. Trong app Zalo của acc phụ, bấm biểu tượng **quét mã**, quét mã QR, rồi bấm **Đăng nhập** để xác nhận. Mã QR hết hạn sau khoảng 100 giây: dòng lệnh tự tạo mã mới, còn trên giao diện thì bấm tạo lại.

5. Xong bước 4, bot tự làm phần còn lại:
   - lưu phiên đăng nhập vào `data/zalo_session.json`;
   - đặt `RECEIVE_MODE=personal` trong `.env`;
   - nếu bot đang chạy thì tự khởi động lại.

   Nếu bot chưa chạy, bật bằng `python -m bot run`, `gateway start` hoặc nút Bật bot. `ZALO_BOT_TOKEN` để trống cũng được.

6. Từ **acc chính** của bạn, nhắn riêng `/id` cho acc phụ, điền `user_id` nhận được vào `OWNER_ZALO_ID`, rồi khởi động lại bot. Sau đó dùng `/allow`, `/mode`... như với Zalo Bot.

Lưu ý:
- `data/zalo_session.json` là **chìa khoá đăng nhập acc phụ**, giữ kín như mật khẩu. Thư mục `data/` đã nằm trong `.gitignore`. Muốn chuyển bot sang máy khác (VPS...), chép cả file này theo, hoặc quét QR lại trên máy mới.
- Trong app Zalo của acc phụ, mục **Quản lý thiết bị đăng nhập** sẽ hiện một phiên Zalo Web. **Đừng đăng xuất phiên đó**, nếu không bot mất kết nối.
- **Mỗi acc chỉ nghe được ở một nơi.** Nếu mở chat.zalo.me bằng acc phụ, Zalo đóng kết nối của bot và bot tự thoát. Supervisor (Task Scheduler, systemd) sẽ bật lại bot. Dùng app Zalo trên điện thoại cho acc phụ thì không sao.
- Tin acc phụ tự gửi (kể cả gửi từ điện thoại) bị bot bỏ qua, nên bot không tự trả lời chính mình.
- Khi phiên hết hạn, log báo "Đăng nhập Zalo cá nhân thất bại". Lúc đó chỉ cần quét QR lại.
- Các lệnh `me`, `set-webhook`... và nút "Gửi lại" ở trang Tin lỗi chỉ dùng được với Zalo Bot.
- Bot nhắn quá nhiều hoặc quá nhanh dễ bị Zalo khoá acc. Nên giữ `USER_RATE_PER_MIN` và `CHAT_RATE_PER_MIN` ở mức thấp.
- Cũng có thể dùng cookies tự lấy từ trình duyệt thay cho QR: lưu cookies vào `data/zalo_session.json` và điền `ZALO_IMEI` trong `.env`.

## Gọi bot trong nhóm bằng tên hoặc @tag

Ở chế độ `default`, ngoài tin bắt đầu bằng `/bot`, bot còn trả lời khi:
- tin **nhắc tới tên bot**: các tên trong `BOT_NAMES` (mặc định `bot`), không phân biệt hoa thường hay có dấu, ví dụ "Bot ơi mai mấy giờ họp?". Chỉ tính khi đứng thành từ riêng, nên "robot" không làm bot trả lời;
- (acc Zalo cá nhân) tin **@tag acc bot**, hoặc nhắc tới **tên acc Zalo của bot**.

Muốn tắt, để `BOT_NAMES=` trống. Muốn thêm tên gọi khác, ghi cách nhau dấu phẩy, ví dụ `BOT_NAMES=bot,trợ lý,Pylos`.

Với `GROUP_CONTEXT=true` (mặc định), bot **lưu cả những tin không gọi nó** trong nhóm đã được cho phép, làm ngữ cảnh. Nhờ vậy khi được gọi ("bot chốt lại giúp"), bot biết mọi người vừa nói gì. Số tin đưa vào mỗi lần trả lời do `HISTORY_TURNS` quyết định.

Nhóm vẫn phải được cho phép trước: gõ `/allow` trong nhóm, hoặc bật `ALLOW_ALL_CHATS=true`. Chế độ acc Zalo cá nhân nhận được mọi tin trong nhóm. Zalo Bot thì có thể chỉ nhận tin nhắc tới bot (Zalo chưa ghi rõ).

## Nối với web Quản lý thời gian (quanlythoigian)

Khi được nhờ "thêm lịch", "nhắc tôi lúc…", "mai có lịch gì?", bot gọi API của web [quanlythoigian](https://quanlythoigian-azure.vercel.app) để thêm lịch hẹn hoặc việc cần làm. Lịch thêm vào hiện trên web, tự lên Google Lịch (nếu web đã kết nối), và web nhắc qua Zalo trước giờ hẹn.

1. Trên web, vào **Cài đặt → Kết nối AI agent → Tạo khoá cho agent** và chép khoá.
2. Trong `.env` của bot (hoặc giao diện quản lý → Cài đặt → mục Lịch và Khóa bí mật):

   ```
   SCHEDULE_API_URL=https://quanlythoigian-azure.vercel.app
   SCHEDULE_API_KEY=<khoá vừa tạo>
   SCHEDULE_OWNER_ONLY=true
   ```

3. Khởi động lại bot. Log sẽ in `Đã nạp tool: them_lich_hen, them_viec, xem_lich, danh_sach_viec, xong_viec`.

Ví dụ nhắn bot: "bot ơi thêm lịch họp nhóm 3h chiều thứ 6", "nhắc tôi 8h sáng mai gọi cho mẹ", "thêm việc nộp báo cáo trước thứ 2", "mai tôi có lịch gì?", "đánh dấu xong việc nộp báo cáo".

- Với `SCHEDULE_OWNER_ONLY=true` (mặc định), chỉ chủ bot (`OWNER_ZALO_ID`) nhờ thêm hoặc xem lịch được. Người khác nhờ thì bot từ chối. Đặt `false` nếu muốn ai cũng nhờ được.
- Ghi chú của mỗi lịch có tên người nhờ.
- Muốn web nhắc việc qua Zalo, cấu hình phía web như trong README của quanlythoigian (mục "Dùng chung bot Zalo với AI agent khác").

## Thêm tool cho trợ lý

1. Sao chép `src/bot/agent/tools/_example.py` thành một file mới không có dấu `_` ở đầu tên.
2. Sửa hàm và mô tả trong file đó, rồi khởi động lại bot.

Tool chỉ dành cho chủ bot thì đặt `owner_only=True`.

## Dữ liệu

| Thư mục | Nội dung |
|---|---|
| `data/*.txt` | Trạng thái nhóm, lịch sử hội thoại, token đã dùng, tin gửi lỗi. Mỗi dòng là một JSON. |
| `workspace/SYSTEM.md` | Tính cách của trợ lý. Sửa xong bot tự nạp lại. |
| `workspace/MEMORY.md` | Điều trợ lý cần nhớ lâu dài. |
| `logs/` | `bot.log` (xoay vòng 5 × 1 MB) và `supervisor.log`. |

`data/`, `logs/`, `.env` và `workspace/MEMORY.md` nằm trong `.gitignore`. Khi chuyển máy, chép `.env`, `data/` và `workspace/` sang là đủ.
