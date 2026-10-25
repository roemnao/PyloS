# Bot trợ lý Zalo (Gemini)

Bot chạy trên **Zalo Bot Platform**, trả lời trong nhóm bằng **Gemini**. Bot nhận tin bằng `getUpdates` (polling), nên chạy được trên máy cá nhân, không cần domain. Bot cũng chạy được trên **một acc Zalo cá nhân** (xem [Chạy trên acc Zalo cá nhân](#chạy-trên-acc-zalo-cá-nhân-acc-phụ)).

Kế hoạch và các quyết định thiết kế nằm trong [docs/PLAN.md](docs/PLAN.md). Cách dùng lệnh trong Zalo nằm trong [docs/lenh-zalo.md](docs/lenh-zalo.md). Xem mục [Thư mục](#thư-mục) để biết file nào nằm ở đâu.

## Thư mục

```
D:\pylosSever\
├─ ZaloBot.cmd                      bấm đúp để mở app
├─ README.md
├─ userdata\                        MỌI THỨ CỦA RIÊNG BẠN (không lên GitHub; chuyển máy chỉ cần chép thư mục này)
│  ├─ config\                       (1) khoá & thông số bạn nhập
│  │  ├─ settings.env               khoá Gemini/Zalo/web lịch và mọi cài đặt (trang Cài đặt ghi vào đây)
│  │  └─ zalo_login_session.json    phiên đăng nhập acc Zalo (quét QR), giữ kín như mật khẩu
│  ├─ data\                         (2) dữ liệu bot
│  │  ├─ memorydata\                mọi tin của từng cuộc trò chuyện, kèm kết quả bộ lọc
│  │  ├─ session_history\           session: tin qua bộ lọc + câu trả lời của bot (gửi cho Gemini)
│  │  ├─ workspace\                 SYSTEM.md (tính cách), MEMORY.md (ghi nhớ), .backup\
│  │  ├─ custom_tools\              tool tự viết (.py)
│  │  ├─ group_settings.txt         nhóm nào được phép, chế độ all/default, nhãn tự đặt
│  │  ├─ chat_activity.txt          lần nhắn cuối của từng cuộc trò chuyện
│  │  ├─ daily_stats.txt            số tin nhận/trả lời/lỗi/token theo ngày
│  │  ├─ token_usage.txt            token Gemini đã dùng mỗi ngày (hạn mức)
│  │  ├─ failed_replies.txt         câu trả lời gửi lên Zalo thất bại (trang Tin lỗi)
│  │  └─ assigned_events.txt        lịch bot đã giao cho người khác (để sửa / huỷ "lịch lúc nãy")
│  └─ system\                       (3) bot tự quản lý, không cần đụng
│     ├─ logs\                      bot.log, admin.log, gui.log, supervisor.log
│     ├─ bot_status.txt             lúc khởi động, lần nhận tin cuối
│     ├─ processed_message_ids.txt  id tin đã xử lý (chống trả lời trùng)
│     ├─ remote_config.json         thông số lấy từ web iforgotmywayhome (bản gần nhất, dùng khi mất mạng)
│     └─ *.lock, *.pid, app_window_profile\, …
├─ src\bot\                         code
│  ├─ command_line.py               lệnh `python -m bot …` (run, gui, admin, zalo-login, update…)
│  ├─ config.py                     đọc settings.env thành cấu hình
│  ├─ userdata_paths.py             tên/đường dẫn mọi file trong userdata + tự chuyển dữ liệu bản cũ
│  ├─ core\                         xử lý tin
│  │  ├─ message_handler.py         nhận tin → lọc → gọi AI → gửi trả lời
│  │  ├─ message_filter.py          bộ lọc "tin này có nhờ bot không"
│  │  ├─ mention_tags.py            tag @người trong nhóm
│  │  ├─ owner_commands.py          lệnh của chủ bot: /allow, /mode, /status…
│  │  ├─ rate_limiter.py            giới hạn số tin mỗi phút
│  │  ├─ reply_formatting.py        cắt tin dài, bỏ markdown
│  │  └─ vietnam_time.py            giờ Việt Nam
│  ├─ agent\                        AI
│  │  ├─ gemini_agent.py            gọi Gemini, chạy tool
│  │  ├─ system_prompt.py           ghép SYSTEM.md, MEMORY.md, bối cảnh thành prompt
│  │  └─ tools\                     tool có sẵn: read_chat_memory.py, schedule_web.py (lịch riêng của chủ web),
│  │                                assign_events.py (giao / sửa / huỷ lịch cho người được tag)
│  ├─ zalo\                         kết nối Zalo
│  │  ├─ bot_platform_api.py        gọi Zalo Bot API (bot có token)
│  │  ├─ personal_account.py        chạy trên acc Zalo cá nhân
│  │  ├─ qr_login.py                đăng nhập acc cá nhân bằng mã QR
│  │  ├─ incoming_message.py        đọc tin nhắn đến
│  │  ├─ receive_polling.py         nhận tin kiểu polling
│  │  └─ receive_webhook.py         nhận tin kiểu webhook
│  ├─ storage\                      data_stores.py (các kho dữ liệu), text_files.py, process_lock.py
│  ├─ system\                       bot_process.py (bật/tắt bot nền), auto_update.py, log_files.py, first_run_setup.py,
│  │                                server_client.py (gọi web iforgotmywayhome), remote_config.py (thông số từ web, nhịp tim),
│  │                                session_upload.py (gửi session lên web)
│  ├─ ui\admin\                     admin_web_server.py, settings_file.py, static\ (trang web quản lý)
│  ├─ ui\desktop\                   desktop_app.py (cửa sổ), tray_icon.py, icon_images.py, windows_autostart.py
│  └─ templates\                    file mẫu tạo userdata lần đầu
├─ tests\
├─ scripts\                         build exe (packaging\), chạy 24/7 bằng Task Scheduler
└─ docs\                            PLAN.md (thiết kế), lenh-zalo.md (lệnh dùng trong Zalo)
```

Lần đầu mở bản mới, bot **tự chuyển** dữ liệu của bản cũ (`.env`, `data/`, `logs/`, `workspace/`, tools tự viết trong `tools/`) vào `userdata\` và đổi sang tên mới ở trên (ví dụ `.env` → `settings.env`, `groups.txt` → `group_settings.txt`, `history/` → `session_history/`). Bạn không phải làm gì. Hai thư mục `workspace/` và `tools/` còn ở gốc chỉ chứa file mẫu, sẽ được gỡ ở bản cập nhật sau.

## Cài đặt (Windows)

Cần Python 3.11 trở lên. Mở PowerShell trong thư mục dự án:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m bot health             # chạy một lệnh bất kỳ để tạo userdata\config\settings.env
```

Sau đó mở `userdata\config\settings.env` (hoặc trang Cài đặt trong app) và điền:

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
- Dữ liệu chat thử lưu riêng trong `userdata/data/console_test`.
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
4. Điền `user_id` của bạn vào `OWNER_ZALO_ID` trong `userdata\config\settings.env`, rồi khởi động lại bot (Ctrl+C rồi chạy lại lệnh ở bước 2).
5. Trong nhóm, gõ `/allow`. Từ đây:
   - Bot trả lời tin bắt đầu bằng `/bot` (chế độ `default`).
   - `/mode all` để bot tự nhận ra cả những câu nhờ nó mà không gọi tên (bộ lọc AI, xem mục "Bộ lọc tin nhóm và memorydata").
6. Xem `userdata/system/logs/bot.log` để biết bot nhận được gì trong nhóm. Zalo chưa ghi rõ bot nhận mọi tin hay chỉ tin nhắc tên.

## Mở ứng dụng bằng ZaloBot.cmd (khuyên dùng)

Bấm đúp **`ZaloBot.cmd`** trong thư mục dự án. Nó mở đúng ứng dụng quản lý như ZaloBot.exe (cửa sổ, biểu tượng **Z** ở khay, menu khay), nhưng **chạy thẳng từ code**:

- **Không cần build lại** khi có code mới.
- **Không bị Smart App Control chặn**, vì nó chạy bằng `pythonw.exe` đã được ký.
- **Lần đầu chạy** (chưa có `.venv`), nó tự tạo môi trường và cài thư viện. Cần cài Python 3.11+ trước, nhớ tick "Add python.exe to PATH".

**Cập nhật code mới** (mỗi lần có thay đổi trên GitHub):
- Chuột phải biểu tượng **Z** → **Cập nhật**. Ứng dụng tự kiểm tra bản mới khi mở và 6 giờ một lần. Khi có bản mới, menu ghi "Cập nhật (N thay đổi mới)" và trang **Tổng quan** hiện nút **Cập nhật ngay**.
- Khi cập nhật, ứng dụng tự `git pull`, cài lại thư viện nếu danh sách thư viện thay đổi, khởi động lại bot, rồi tự đóng và mở lại.
- Dùng dòng lệnh thì chạy `.venv\Scripts\python.exe -m bot update`.
- Nếu bạn đã sửa tay file nào trong code, `git pull` có thể từ chối. Thông báo lỗi sẽ nói rõ file nào.

Đã bật **Khởi động cùng Windows** bằng ZaloBot.exe trước đây? Mở ZaloBot.cmd một lần, mục đó sẽ tự chuyển sang chạy từ code thay cho exe cũ.

Muốn có lối tắt ngoài Desktop: chuột phải `ZaloBot.cmd` → **Show more options** → **Send to** → **Desktop (create shortcut)**.

## Ứng dụng quản lý: ZaloBot.exe

> Bản exe là code đóng gói tại lúc build: mỗi lần có code mới phải build lại, và Smart App Control có thể chặn mỗi bản mới. Nên dùng **ZaloBot.cmd** (mục trên) thay thế.

Bấm đúp `D:\pylosSever\ZaloBot.exe`. Một cửa sổ "Quản lý Bot Zalo" mở ra (tự đăng nhập), kèm biểu tượng chữ **Z** ở khay hệ thống (góc phải thanh tác vụ; có thể nằm trong mũi tên ^).

- **Bấm X**: cửa sổ thu xuống khay, bot vẫn chạy. Bấm biểu tượng khay để mở lại.
- **Menu khay** (chuột phải): Mở giao diện · Bật/Tắt bot · Khởi động lại bot · **Khởi động cùng Windows** · Mở thư mục dữ liệu · Thoát (bot vẫn chạy) · Thoát và tắt bot.
- **Màu chấm trên biểu tượng**: xanh = bot đang chạy, cam = đang chạy nhưng có cảnh báo, xám = đã dừng.
- **Khởi động cùng Windows**: tích trong menu khay. Khi đăng nhập, ứng dụng tự chạy ẩn ở khay và bật bot. Không cần `install-task.ps1`.
- Mở exe lần hai chỉ đưa cửa sổ đang chạy lên, không mở thêm bản mới.
- Lần đầu chạy trong thư mục trống, exe tự tạo `userdata\` và mở trang Cài đặt để bạn điền khóa.
- Dữ liệu nằm trong `userdata\` **cạnh exe**. Muốn chuyển máy: chép thư mục đó.
- Tool tự viết: đặt file `.py` vào `userdata\data\custom_tools\` (xem `_example.py` trong đó), rồi khởi động lại bot.

Exe chưa có chữ ký số, nên **Windows có thể chặn** ("Windows đã bảo vệ PC của bạn" hoặc "An Application Control policy has blocked this file"), nhất là sau mỗi lần build lại. Máy này đang bật **Smart App Control**, cơ chế này chặn exe chưa ký mà không cho bấm "Vẫn chạy". Nếu bị chặn:
- Thử mở lại bằng cách bấm đúp trong Explorer (Windows tra uy tín trên mạng, đôi khi lần sau cho chạy).
- Hoặc chạy cùng ứng dụng đó từ mã nguồn (không bị chặn vì `pythonw.exe` đã được ký): `.venv\Scripts\pythonw.exe -m bot gui`.
- Không nên tắt Smart App Control chỉ vì bot: tắt rồi thì không bật lại được nếu không cài lại Windows.

Build lại exe (sau khi sửa code): `powershell -ExecutionPolicy Bypass -File scripts\build-exe.ps1`. Script build kèm bước kiểm tra exe không chứa token/khóa nào trong `userdata\config\settings.env`. Nếu exe đang chạy, thoát nó ở khay trước để script thay được file.

Lệnh dòng lệnh vẫn dùng được với exe, ví dụ `ZaloBot.exe gateway status` (kết quả in vào cửa sổ cmd).

## Giao diện quản lý (web)

```powershell
.venv\Scripts\python.exe -m bot admin start --open   # chạy nền và mở trình duyệt, đăng nhập sẵn
.venv\Scripts\python.exe -m bot admin                # hoặc chạy trong cửa sổ này (Ctrl+C để dừng)
.venv\Scripts\python.exe -m bot admin stop
```

Mở http://127.0.0.1:8081. Có hai cách vào:

- **Đăng nhập bằng Gmail (khuyên dùng).** Bấm **Đăng nhập bằng Gmail**: trang mở web iforgotmywayhome ở tab mới, bạn đăng nhập Gmail và bấm **Cho phép**, trang quản lý tự vào (phiên 12 giờ). Chỉ Gmail đã liên kết vào **tài khoản quản trị của web** (trang quản trị → Cài đặt → Liên kết Google) được vào; Gmail khác bị từ chối. Cần `SCHEDULE_API_KEY` trong `settings.env` (không có thì nút này ẩn).
- **Mã truy cập (dự phòng).** `ADMIN_TOKEN` trong `userdata\config\settings.env`; nếu còn trống, lần chạy đầu sẽ tự tạo. Quên mã thì chạy `.venv\Scripts\python.exe -m bot admin --open` để mở và tự đăng nhập.

| Trang | Làm được gì |
|---|---|
| Tổng quan | Bật / tắt / khởi động lại bot, xem trạng thái, tin và token hôm nay, biểu đồ 14 ngày, cảnh báo |
| Nhóm | Đặt tên gợi nhớ, cho phép / chặn, đổi chế độ `all` / `default`, xóa lịch sử; có hiệu lực ngay, không cần khởi động lại |
| Hội thoại | Đọc lịch sử bot dùng làm ngữ cảnh (tắt được bằng `ADMIN_SHOW_HISTORY=false`) |
| Chỉ dẫn | Sửa `SYSTEM.md` và `MEMORY.md`, tự sao lưu vào `userdata/data/workspace/.backup/` |
| Chat thử | Nói chuyện với trợ lý mà không qua Zalo (token vẫn được tính) |
| Log | Xem log bot / giao diện, lọc theo mức, theo dõi trực tiếp |
| Tin lỗi | Gửi lại hoặc bỏ qua tin bot không gửi được |
| Cài đặt | Đăng nhập acc Zalo cá nhân bằng mã QR; sửa các giá trị trong `userdata\config\settings.env` (có sao lưu `settings.env.bak`); khóa bí mật chỉ đặt mới, không bao giờ hiện lại |

Bảo mật: giao diện chỉ mở ở `127.0.0.1` (không truy cập được từ máy khác), bắt buộc mã truy cập, chặn yêu cầu từ trang web khác. Đừng đưa cổng 8081 ra Internet.

## Điều khiển bot trên VPS từ ứng dụng ở máy này

Trang **Máy chủ** → **Kết nối VPS bằng Gmail** (đăng nhập Gmail quản trị một lần, không cần chép mã) là có công tắc **Máy này | VPS** trên đầu trang,
trang **Máy chủ** (so sánh hai bên, cập nhật code VPS) và nút **Chuyển bot sang VPS / về máy này** (kèm dữ liệu, tự hoàn tác
nếu lỗi). Chỉ một bên chạy bot tại một thời điểm. Việc cần chủ VPS làm một lần và chi tiết: [docs/vps-dieu-khien.md](docs/vps-dieu-khien.md).

## Quản lý bot chạy nền (gateway)

```powershell
.venv\Scripts\python.exe -m bot gateway start      # bật bot chạy nền, không cần giữ cửa sổ
.venv\Scripts\python.exe -m bot gateway status     # đang chạy hay dừng, poll cuối, token hôm nay, nhóm được phép
.venv\Scripts\python.exe -m bot gateway logs -n 50 # xem 50 dòng log cuối (thêm -f để theo dõi liên tục)
.venv\Scripts\python.exe -m bot gateway restart    # khởi động lại (dùng sau khi sửa settings.env)
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
- Nếu `settings.env` sai (thiếu biến hoặc token sai), script dừng hẳn thay vì khởi động lại mãi. Xem `userdata/system/logs/supervisor.log`.

Để bot không ngừng khi máy ngủ, tắt Sleep (khi cắm sạc):

```powershell
powercfg /change standby-timeout-ac 0
```

Bot chỉ chạy khi bạn đã đăng nhập Windows. Muốn bot tự chạy sau khi máy khởi động lại mà không cần ai đăng nhập, hãy bật tự động đăng nhập Windows hoặc chuyển lên VPS.

Các lệnh khác:
- Gỡ task: `scripts\uninstall-task.ps1`.
- Kiểm tra bot còn chạy: `.venv\Scripts\python.exe -m bot health` (mã thoát 0 = ổn).

## Chuyển sang webhook (khi có domain hoặc VPS)

1. Trong `userdata\config\settings.env`: đặt `RECEIVE_MODE=webhook` và `WEBHOOK_SECRET` (8–256 ký tự ngẫu nhiên).
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
   - **Dòng lệnh**: `python -m bot zalo-login`. Ảnh mã QR được lưu vào `userdata/system/zalo_login_qr.png` và tự mở. Trên máy không có màn hình, thêm `--no-open`.

4. Trong app Zalo của acc phụ, bấm biểu tượng **quét mã**, quét mã QR, rồi bấm **Đăng nhập** để xác nhận. Mã QR hết hạn sau khoảng 100 giây: dòng lệnh tự tạo mã mới, còn trên giao diện thì bấm tạo lại.

5. Xong bước 4, bot tự làm phần còn lại:
   - lưu phiên đăng nhập vào `userdata/config/zalo_login_session.json`;
   - đặt `RECEIVE_MODE=personal` trong `userdata/config/settings.env`;
   - nếu bot đang chạy thì tự khởi động lại.

   Nếu bot chưa chạy, bật bằng `python -m bot run`, `gateway start` hoặc nút Bật bot. `ZALO_BOT_TOKEN` để trống cũng được.

6. Từ **acc chính** của bạn, nhắn riêng `/id` cho acc phụ, điền `user_id` nhận được vào `OWNER_ZALO_ID`, rồi khởi động lại bot. Sau đó dùng `/allow`, `/mode`... như với Zalo Bot.

Lưu ý:
- `userdata/config/zalo_login_session.json` là **chìa khoá đăng nhập acc phụ**, giữ kín như mật khẩu. Thư mục `userdata/` đã nằm trong `.gitignore`. Muốn chuyển bot sang máy khác (VPS...), chép cả file này theo, hoặc quét QR lại trên máy mới.
- Trong app Zalo của acc phụ, mục **Quản lý thiết bị đăng nhập** sẽ hiện một phiên Zalo Web. **Đừng đăng xuất phiên đó**, nếu không bot mất kết nối.
- **Mỗi acc chỉ nghe được ở một nơi.** Nếu mở chat.zalo.me bằng acc phụ, Zalo đóng kết nối của bot và bot tự thoát. Supervisor (Task Scheduler, systemd) sẽ bật lại bot. Dùng app Zalo trên điện thoại cho acc phụ thì không sao.
- Tin acc phụ tự gửi (kể cả gửi từ điện thoại) bị bot bỏ qua, nên bot không tự trả lời chính mình.
- **Bot tag được người trong nhóm.** Ví dụ nhờ "bot nhắc Thái Toàn nộp bài", bot trả lời "@Thái Toàn …" và người đó nhận thông báo như khi được tag thật.
  - Bot lấy danh sách thành viên từ Zalo (làm mới mỗi giờ), cộng thêm những người đã nhắn gần đây, và chỉ tag đúng tên có trong danh sách đó.
  - Bot không tag cả nhóm (@All).
  - Chế độ Zalo Bot không có chức năng này.
- Khi phiên hết hạn, log báo "Đăng nhập Zalo cá nhân thất bại". Lúc đó chỉ cần quét QR lại.
- Các lệnh `me`, `set-webhook`... và nút "Gửi lại" ở trang Tin lỗi chỉ dùng được với Zalo Bot.
- Bot nhắn quá nhiều hoặc quá nhanh dễ bị Zalo khoá acc. Nên giữ `USER_RATE_PER_MIN` và `CHAT_RATE_PER_MIN` ở mức thấp.
- Cũng có thể dùng cookies tự lấy từ trình duyệt thay cho QR: lưu cookies vào `userdata/config/zalo_login_session.json` và điền `ZALO_IMEI` trong `userdata/config/settings.env`.

## Bộ lọc tin nhóm và memorydata

Mỗi cuộc trò chuyện (nhóm hoặc chat riêng) đã được cho phép có **hai lớp dữ liệu**:

| | Nằm ở | Chứa gì | Dùng để |
|---|---|---|---|
| **Memorydata** | `userdata/data/memorydata/<chat>.txt` | **Mọi** tin, kể cả tin bộ lọc chặn, kèm kết quả lọc. Mỗi dòng một JSON. | Lưu trữ; bot đọc khi cần qua tool `doc_memorydata` |
| **Session** | `userdata/data/session_history/<chat>.txt` | Chỉ tin **qua bộ lọc** và câu trả lời của bot | Ngữ cảnh gửi cho Gemini mỗi lần trả lời |

**Bộ lọc** quyết định tin trong nhóm có đang nhờ bot trả lời không (chat riêng thì tin nào cũng qua). Các tầng chạy theo thứ tự:
1. Tin bắt đầu bằng `/bot`, **@tag acc bot**, hoặc **gọi tên bot** (`BOT_NAMES`, mặc định `bot`, cùng tên acc Zalo của bot; không phân biệt hoa thường hay dấu): qua ngay, không tốn token.
2. Sticker, ảnh, tin chỉ là cảm thán ("ok", "haha", emoji…), hoặc tin **chỉ tag người khác** ("@Thái Toàn", "@All …"): chặn ngay.
3. Nhóm ở **`/mode default`**: dừng ở đây, tức là chỉ trả lời khi được gọi.
4. Nhóm ở **`/mode all`**: hỏi Gemini "tin này có đang nhờ trợ lý không?". Gemini được xem thêm `FILTER_CONTEXT_LINES` tin gần nhất, nên hiểu cả câu hỏi tiếp nối ngay sau khi bot vừa trả lời. Gemini được dặn: không chắc thì không trả lời. Token của bước này cũng tính vào hạn mức ngày. Khi hết hạn mức, hoặc `FILTER_AI=false`, chỉ còn tầng 1 cho qua.

Tin không qua lọc vẫn nằm trong memorydata. Khi bạn hỏi "bot tóm tắt nhóm nói gì hôm nay" hay "lúc nãy Bình hẹn mấy giờ?", bot tự gọi tool `doc_memorydata` để đọc lại. Tool chỉ đọc được **chính cuộc trò chuyện đó**.

Kiểm tra bộ lọc: giao diện quản lý → **Hội thoại** → chọn **Memorydata (tất cả tin)**. Mỗi tin có nhãn *qua lọc* hoặc *bị chặn*, kèm tầng và lý do. Trang **Tổng quan** đếm số tin qua và bị chặn trong ngày.

Cấu hình (trang Cài đặt → **Bộ lọc & memorydata**): `FILTER_AI`, `FILTER_MODEL` (nên dùng model rẻ), `FILTER_CONTEXT_LINES`, `MEMORYDATA_KEEP` (số tin giữ lại mỗi file). Muốn thêm tên gọi bot, sửa `BOT_NAMES`, ví dụ `bot,trợ lý,Pylos`.

Nhóm vẫn phải được cho phép trước: gõ `/allow` trong nhóm, hoặc bật `ALLOW_ALL_CHATS=true`. Nhóm chưa được phép thì bot không lưu gì. Chế độ acc Zalo cá nhân nhận được mọi tin trong nhóm. Zalo Bot thì có thể chỉ nhận tin nhắc tới bot (Zalo chưa ghi rõ).

## Nối với web iforgotmywayhome (repo quanlythoigian)

Bot nói chuyện với web [iforgotmywayhome](https://quanlythoigian-azure.vercel.app) (repo `quanlythoigian`) qua API dành cho agent. Một khoá dùng cho tất cả:

1. Trên web, đăng nhập trang quản trị, vào **Cài đặt → Kết nối AI agent → Tạo khoá cho agent** và chép khoá.
2. Trong `userdata\config\settings.env` của bot (hoặc giao diện quản lý → Cài đặt → mục **Web iforgotmywayhome** và **Khóa bí mật**):

   ```
   SCHEDULE_API_URL=https://quanlythoigian-azure.vercel.app
   SCHEDULE_API_KEY=<khoá vừa tạo>
   ```

   `SCHEDULE_API_URL` là tên miền của trang quản trị (bot gọi được cả tên miền app, nhưng tên miền quản trị là chỗ bạn tạo khoá).
3. Khởi động lại bot. Log in `Kết nối web …: nhận cấu hình, nhịp tim mỗi phút…` và `Đã nạp tool: …`.

Khoá chỉ nằm trên máy chạy bot. Web không bao giờ gửi khoá bí mật (Gemini, Zalo, phiên đăng nhập) xuống bot.

### Giao lịch cho người trong nhóm (bot lịch)

Mỗi thành viên mở **web app** (link ở trang quản trị của web → Hệ thống → Thành viên, vd `https://iforgotmywayhome.vercel.app/` khi web app có tên miền riêng) trên điện thoại hoặc máy tính, đăng nhập bằng Gmail (đồng ý điều khoản), rồi:
- **Liên kết Zalo:** bấm *Lấy mã liên kết*, rồi **nhắn riêng mã 6 số cho acc bot** (hoặc `/lienket 123456`). Bot chuyển mã lên web, không tốn token Gemini. Mã dùng một lần, hết hạn sau 10 phút.
- **Kết nối Google Lịch:** bấm nút trong app. Quyền ghi lịch chỉ nằm trong trình duyệt của họ.

Sau đó, trong nhóm:

```
roemnao giao @An @Bình họp kế hoạch 9h sáng mai ở phòng 301
roemnao dời cuộc họp lúc nãy sang 10h, thêm @Chi
roemnao huỷ cuộc họp lúc nãy
roemnao các lịch đã giao trong nhóm?
```

Bot dùng các tool `giao_lich`, `sua_lich`, `huy_lich`, `lich_da_giao`:
- Người nhận lấy từ **@tag thật** trong tin trước, rồi tới tên khớp (không phân biệt dấu) với danh sách thành viên nhóm. Tên trùng nhiều người thì bot nhờ @tag.
- Web (bot lịch) ghi lệnh thêm / sửa / xoá vào hàng của từng người; app của họ tự ghi vào Google Lịch khi đang mở. Người bị bỏ khỏi lịch nhận lệnh xoá.
- Bot trả lời ai đã nhận, ai **chưa liên kết** (kèm link app). Bot nhớ các lịch đã giao trong `userdata\data\assigned_events.txt` để sửa / huỷ "lịch lúc nãy".
- Ai được nhờ giao lịch: `ASSIGN_ALLOWED=owner` (mặc định, chỉ chủ bot) hoặc `all`.

### Thông số chỉnh trên web, nhịp tim, session

- **Cấu hình từ xa:** chủ hệ thống chỉnh model của agent, **model của bộ lọc** và các thông số khác ở trang **Hệ thống → Cấu hình bot** trên web. Bot hỏi lại mỗi phút và áp ngay, không cần khởi động lại. Giá trị từ web đè lên `settings.env`; trang Cài đặt của giao diện quản lý gắn nhãn *Web đang đặt* cho những ô đó. Mất mạng thì bot dùng bản lấy được gần nhất (`userdata\system\remote_config.json`). SYSTEM.md / MEMORY.md cũng đặt được từ web (bản cũ được giữ trong `workspace\.backup`).
- **Nhịp tim:** mỗi phút bot báo đang chạy, phiên bản, model, token hôm nay, lỗi gần nhất. Trang Hệ thống của web hiện trạng thái bot.
- **Session:** mỗi bước tin → bộ lọc → agent → tool → bot lịch → câu trả lời được gửi lên web theo lô (không làm chậm việc trả lời), xem ở **Hệ thống → Session**. Việc này đưa nội dung chat lên web (giữ mặc định 14 ngày); tắt bằng `SESSION_UPLOAD=false` ở đây hoặc trên web.

### Lịch riêng của chủ web

Khi được nhờ "thêm lịch", "nhắc tôi lúc…", "mai có lịch gì?", bot thêm lịch hẹn hoặc việc cần làm vào **lịch riêng của chủ web** (tool `them_lich_hen`, `them_viec`, `xem_lich`, `danh_sach_viec`, `xong_viec`). Lịch hiện trên trang quản trị của web, tự lên Google Lịch của chủ web (nếu đã kết nối), và web nhắc qua Zalo trước giờ hẹn.

Ví dụ: "bot ơi thêm lịch họp nhóm 3h chiều thứ 6", "nhắc tôi 8h sáng mai gọi cho mẹ", "mai tôi có lịch gì?".

- Với `SCHEDULE_OWNER_ONLY=true` (mặc định), chỉ chủ bot (`OWNER_ZALO_ID`) dùng được các tool này. Đặt `false` nếu muốn ai cũng nhờ được.
- Muốn web nhắc việc qua Zalo, cấu hình phía web như trong README của quanlythoigian (mục "Dùng chung bot Zalo với AI agent khác").

## Bảng lệnh

### Dòng lệnh (Windows, trong thư mục dự án)
Viết tắt: `PY` = `.venv\Scripts\python.exe`.

| Lệnh | Tác dụng |
|---|---|
| `PY -m bot run` | Chạy bot ở cửa sổ này (Ctrl+C để dừng) |
| `PY -m bot gateway start` / `stop` / `restart` / `status` | Bật, tắt, khởi động lại, xem tình trạng bot chạy nền |
| `PY -m bot gateway logs -n 50` (thêm `-f` để theo dõi) | Xem log |
| `PY -m bot gui` (`--tray`, `--start-bot`) | Ứng dụng quản lý (cửa sổ và biểu tượng khay) |
| `PY -m bot admin` (`run`, `start`, `stop`, `restart`, `status`, `--open`) | Giao diện web quản lý bot tại `http://127.0.0.1:8081` |
| `PY -m bot console` (`--chat-id`, `--user-id`, `--name`, `--private`) | Chat thử trên terminal, không cần Zalo |
| `PY -m bot health` (`--max-age 180`) | Kiểm tra bot còn chạy |
| `PY -m bot update` | Lấy code mới từ GitHub và khởi động lại bot |
| `PY -m bot zalo-login` (`--no-open`) | Đăng nhập acc Zalo cá nhân bằng mã QR |
| `PY -m bot me` | Gọi `getMe` của Zalo Bot |
| `PY -m bot set-webhook <url>` / `webhook-info` / `delete-webhook` | Đăng ký, xem, gỡ webhook |
| `PY -m pytest` | Chạy toàn bộ test |

### Ba vai trò
| Vai trò | Là ai | Được làm |
|---|---|---|
| **basic-user** | Mọi người trong chat đã được phép | Nhận việc; dùng lệnh xem; tự thêm lịch vào Google Lịch của **chính mình**; sửa / huỷ lịch do mình tạo cho mình. Không giao việc cho người khác |
| **leader** | Do owner hoặc leader khác thêm, **theo từng nhóm Zalo** | Mọi quyền của basic, cộng: giao việc cho người khác (`@a @b`) hoặc cho cả đội; tạo / sửa đội; cho người khác lên leader |
| **owner** | `OWNER_ZALO_ID` (mọi nơi) | Mọi quyền của leader, cộng: lệnh về bộ lọc và chỉnh bot; gỡ leader; `/leader all` |

Người không đủ quyền gõ lệnh trong chat đã được phép thì bot trả lời "cần quyền …". Ở chat chưa được phép bot im lặng như thường. Gõ `/help` để xem đúng các lệnh bạn dùng được, `/vaitro` để xem vai trò của mình.

### Lệnh trên Zalo
| Lệnh | basic | leader | owner | Tác dụng |
|---|:-:|:-:|:-:|---|
| `/help` | ✓ | ✓ | ✓ | Các lệnh bạn dùng được |
| `/id` | ✓ | ✓ | ✓ | Xem `chat_id` và `user_id` của bạn |
| `/vaitro` (`/role`) | ✓ | ✓ | ✓ | Vai trò của bạn trong chat này |
| `/leader` | ✓ | ✓ | ✓ | Xem ai là leader của nhóm |
| `/team`, `/team tên` | ✓ | ✓ | ✓ | Xem các đội, hoặc thành viên một đội |
| `123456` hoặc `/lienket 123456` | ✓ | ✓ | ✓ | Nhắn riêng cho bot mã 6 số lấy từ web app để liên kết Zalo với Gmail |
| `/bot <câu hỏi>` | ✓ | ✓ | ✓ | Gọi bot ở chế độ `default` |
| `/add leader @a @b` | | ✓ | ✓ | Cho a, b làm leader trong nhóm này (cộng dồn) |
| `/team tên @a @b` | | ✓ | ✓ | Tạo đội hoặc thêm người vào đội |
| `/team tên bo @a` | | ✓ | ✓ | Bỏ người khỏi đội |
| `/team xoa tên` | | ✓ | ✓ | Xoá đội |
| `/remove leader @a` | | | ✓ | Gỡ leader (chỉ owner) |
| `/leader all`, `/leader off` | | | ✓ | Cả nhóm là leader, hoặc xoá hết leader |
| `/allow`, `/deny` | | | ✓ | Cho phép hoặc chặn nhóm hiện tại |
| `/mode`, `/mode all`, `/mode default` | | | ✓ | Xem hoặc đổi chế độ nhóm (bộ lọc AI) |
| `/status` | | | ✓ | Nhóm có được phép không, chế độ, token hôm nay |
| `/reset` | | | ✓ | Xoá lịch sử hội thoại của nhóm |

- Tag không được (bot Zalo chính thức không gửi @tag) thì gõ tên (`/add leader An`) hoặc Zalo ID (`/add leader 123456789`).
- Tên đội không phân biệt hoa thường và dấu: `/team Thiết Kế @a` cũng là đội `thiet ke`.
- Dạng cũ vẫn chạy: `/leader @a` = `/add leader @a`, `/leader bo @a` = `/remove leader @a` (chỉ owner).

### Nhờ bot bằng lời (không cần lệnh `/`)
Gọi tên bot rồi nói tự nhiên:

```
roemnao nhắc tôi nộp báo cáo 9h sáng mai                        # basic trở lên: lịch vào Google Lịch của chính người nói
roemnao lịch sắp tới của tôi?                                   # lich_cua_toi (ai cũng dùng được)
roemnao giao @An @Bình họp kế hoạch 9h sáng mai ở phòng 301    # leader / owner: giao_lich
roemnao giao cho nhóm thiết kế họp 9h sáng mai                  # leader / owner: giao cho cả đội thiết kế
roemnao dời cuộc họp lúc nãy sang 10h, thêm @Chi, bỏ Bình       # leader / owner: sua_lich
roemnao huỷ cuộc họp lúc nãy                                    # huy_lich (basic: chỉ lịch do chính mình tạo cho mình)
roemnao các lịch đã giao trong nhóm?                            # lich_da_giao
```

Điều kiện: `SCHEDULE_API_KEY` đã đặt, và người nhận đã liên kết Zalo với app iforgotmywayhome. Quyền được kiểm tra trong code của từng tool, không dựa vào lời của model.

### Ai dùng được gì (cài đặt)
| Cài đặt | Ý nghĩa |
|---|---|
| `OWNER_ZALO_ID` | Zalo ID của owner. Để trống hoặc điền sai thì bạn chỉ là basic-user, bot sẽ nói "chỉ thêm được lịch cho chính mình" |
| `ASSIGN_ALLOWED` | `owner` (mặc định) hoặc `all`: `all` coi **mọi người** là leader ở mọi nhóm |
| `/add leader` (theo nhóm) | Cộng thêm với `ASSIGN_ALLOWED`. Leader nhóm A không tự thành leader nhóm B |
| `SCHEDULE_OWNER_ONLY` | `true` (mặc định): chỉ owner dùng các tool `them_lich_hen`, `them_viec`, `xem_lich`, `danh_sach_viec`, `xong_viec` (lịch riêng của chủ web) |

### Đặt quyền giao lịch (`ASSIGN_ALLOWED`)
Giá trị: `owner` (mặc định, chỉ owner và leader từng nhóm giao lịch được) hoặc `all` (ai cũng giao được). Đặt ở một trong ba chỗ:

| Cách | Thao tác | Hiệu lực |
|---|---|---|
| Trang quản trị web | Hệ thống → nhóm Quyền → *Ai được giao lịch cho người khác* → `owner` hoặc `all` → Lưu | Tự áp dụng sau tối đa 60 giây (nhịp tim), không cần khởi động lại. Cần `SCHEDULE_API_KEY` |
| Cài đặt của app bot | Trang Cài đặt → nhóm *Web iforgotmywayhome* → *Ai được giao lịch cho người khác* | Khởi động lại bot |
| File cấu hình | Thêm dòng `ASSIGN_ALLOWED=all` vào `userdata\config\settings.env` | Khởi động lại bot (`PY -m bot gateway restart`) |

Giá trị đặt trên web ghi đè giá trị trong `settings.env` khi bot đang nối với web. Đi cùng là `SCHEDULE_OWNER_ONLY=true|false` (lịch riêng của chủ web), đặt ở cùng các chỗ trên.

## Thêm tool cho trợ lý

1. Sao chép `userdata\data\custom_tools\_example.py` thành một file mới (trong cùng thư mục) không có dấu `_` ở đầu tên.
2. Sửa hàm và mô tả trong file đó, rồi khởi động lại bot.

(Tool có sẵn của bot nằm trong `src/bot/agent/tools/`.)

Tool chỉ dành cho chủ bot thì đặt `owner_only=True`.

## Dữ liệu

Mọi dữ liệu của bạn nằm trong `userdata\` (xem mục [Thư mục](#thư-mục)). Thư mục này nằm trong `.gitignore`, nên không bao giờ lên GitHub. Muốn chuyển máy, chép cả `userdata\` sang là đủ.

| Ở đâu | Nội dung |
|---|---|
| `userdata/config/settings.env` | Khoá API và mọi cài đặt. |
| `userdata/config/zalo_login_session.json` | Phiên đăng nhập acc Zalo cá nhân. |
| `userdata/data/group_settings.txt` | Nhóm được phép, chế độ, nhãn. |
| `userdata/data/daily_stats.txt`, `token_usage.txt` | Số liệu theo ngày, token đã dùng. |
| `userdata/data/failed_replies.txt` | Câu trả lời gửi lỗi (trang Tin lỗi). |
| `userdata/data/assigned_events.txt` | Lịch bot đã giao cho người khác qua web iforgotmywayhome (mã lịch, người nhận). |
| `userdata/system/remote_config.json` | Thông số chủ hệ thống đặt trên web (bản gần nhất). |
| `userdata/data/session_history/` | Session của từng cuộc trò chuyện: tin qua bộ lọc và câu trả lời của bot. |
| `userdata/data/memorydata/` | Mọi tin của từng cuộc trò chuyện, kèm kết quả bộ lọc. |
| `userdata/data/workspace/SYSTEM.md` | Tính cách của trợ lý. Sửa xong bot tự nạp lại. |
| `userdata/data/workspace/MEMORY.md` | Điều trợ lý cần nhớ lâu dài. |
| `userdata/system/logs/` | `bot.log` (xoay vòng 5 × 1 MB), `admin.log`, `gui.log`, `supervisor.log`. |
