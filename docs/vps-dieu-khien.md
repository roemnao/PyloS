# Điều khiển bot trên VPS từ ZaloBot.exe

Ứng dụng quản lý ở máy Windows xem được trạng thái VPS, bấm cập nhật code VPS, và **chuyển bot** qua lại giữa máy này
và VPS (kèm dữ liệu). Cùng một tài khoản Zalo không được chạy ở hai nơi, nên mỗi lúc chỉ một bên chạy bot.

## Cách hoạt động

```
Cửa sổ ZaloBot.exe ──► server giao diện ở máy này ──/api/remote/*──► https://unousgrowth.com/api/*
                         (thêm REMOTE_ADMIN_TOKEN)                      (pylos-admin trên VPS)
```

- Trình duyệt chỉ nói chuyện với server ở máy này; mã truy cập VPS nằm trong `settings.env` của máy này, không xuống trang web.
- Công tắc **Máy này | VPS** trên đầu trang: chọn VPS thì mọi trang (Nhóm, Hội thoại, Chỉ dẫn, Cài đặt, Log…) làm việc trên VPS.
  Đặt khoá bí mật (`/api/secrets`) và đăng nhập Gmail bị chặn qua proxy; muốn đặt thì mở trang quản lý ngay trên VPS.
- Trang **Máy chủ**: hai thẻ cạnh nhau (máy này, VPS) gồm RAM, ổ đĩa, commit đang chạy, trạng thái service, nút Bật / Tắt / Khởi động
  lại / Cập nhật code; phía trên có nút **Chuyển bot sang VPS / về máy này**.
- **Chế độ chờ:** file `userdata/system/standby.txt`. Bên có file này không chạy bot (`bot run` thoát mã 5, ứng dụng không tự bật),
  kể cả khi máy khởi động lại hay systemd/Task Scheduler muốn bật.
- **Gói chuyển** (zip): toàn bộ `userdata/data` (nhóm, lịch sử, memorydata, tool tự viết, chỉ dẫn), `processed_message_ids.txt`
  và phiên Zalo cá nhân. Không có `settings.env`, log, file khoá. Bên nhận sao lưu dữ liệu cũ vào
  `userdata/system/handover_backups/` (giữ 3 bản gần nhất) rồi thay bằng gói.
- Chuyển lỗi giữa chừng thì tự **hoàn tác**: bật lại bot ở bên cũ.
- Chỉ chuyển được khi cả hai bên cùng `RECEIVE_MODE` là `polling` hoặc `personal` (webhook gắn với một địa chỉ cố định).
  Acc Zalo cá nhân đổi IP có thể bị Zalo đòi đăng nhập lại: quét QR ở trang Cài đặt của VPS (công tắc VPS).

## Kết nối từ máy Windows: đăng nhập Gmail

Trang **Máy chủ** → thẻ VPS → **Kết nối VPS bằng Gmail** → đăng nhập Gmail quản trị của web iforgotmywayhome, bấm Cho phép.
Xong là máy này nhớ kết nối, không cần chép mã nào.

- VPS cấp cho máy này một **khoá thiết bị** (`dev_…`), lưu vào `REMOTE_ADMIN_TOKEN` trong `settings.env` ở máy này. Khoá không bao giờ
  xuống trang web. Trên VPS chỉ lưu SHA-256 của khoá (`userdata/system/admin_devices.json`), nên khoá vẫn còn sau khi VPS khởi động lại
  hay tự cập nhật.
- Khoá hết hạn sau 180 ngày không dùng. Cùng một máy đăng nhập lại thì khoá cũ bị thay. Xem và thu hồi các máy đã kết nối bằng
  `GET /api/devices` và `DELETE /api/devices/{id}`. Ở máy này có nút **Ngắt kết nối** trên thẻ VPS.
- Chỉ Gmail có quyền quản trị trên web iforgotmywayhome mới được cấp khoá (web trả `isAdmin`).
- `REMOTE_URL` để trống thì dùng `https://unousgrowth.com`. Đặt `off` để tắt hẳn phần VPS.
- Vẫn dán `ADMIN_TOKEN` của VPS vào `REMOTE_ADMIN_TOKEN` được, nếu không muốn dùng Gmail.

**Điều kiện:** VPS phải đặt `SCHEDULE_API_KEY` (khoá agent của web iforgotmywayhome) thì mới đăng nhập Gmail được. Hiện VPS chưa có khoá này.

## Việc chủ VPS làm một lần (user `em` và `pylos` không tự làm được)

Nội dung dưới đây chạy bằng root.

### 1. Service cho bot

`/etc/systemd/system/pylos-bot.service`:

```ini
[Unit]
Description=PyloS Zalo bot
After=network-online.target

[Service]
User=pylos
WorkingDirectory=/opt/pylos
Environment=PYTHONPATH=/opt/pylos/src
ExecStart=/opt/pylos/.venv/bin/python -m bot run
Restart=on-failure
RestartSec=10
# Mã 5 = đang ở chế độ chờ (bot đã chuyển sang máy khác): không bật lại. Mã 2 = lỗi cấu hình.
RestartPreventExitStatus=2 3 5
NoNewPrivileges=true
PrivateTmp=true
MemoryMax=1G

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable pylos-bot      # chưa start: bot chỉ chạy khi có chủ định (đủ GEMINI_API_KEY, ZALO_BOT_TOKEN trong settings.env)
```

### 2. Cho user `pylos` điều khiển đúng 2 service (chọn MỘT cách)

`pylos-admin.service` đang đặt `NoNewPrivileges=true` nên `sudo` từ trong nó không chạy được. Cách khuyên dùng là **polkit**
(giữ nguyên NoNewPrivileges). `/etc/polkit-1/rules.d/50-pylos.rules`:

```js
polkit.addRule(function (action, subject) {
  if (subject.user == "pylos" &&
      action.id == "org.freedesktop.systemd1.manage-units" &&
      (action.lookup("unit") == "pylos-bot.service" || action.lookup("unit") == "pylos-update.service")) {
    return polkit.Result.YES;
  }
});
```

Cách khác (nếu VPS không có polkit): bỏ dòng `NoNewPrivileges=true` khỏi `pylos-admin.service` rồi thêm sudoers
(`visudo -f /etc/sudoers.d/pylos-bot`):

```
pylos ALL=(root) NOPASSWD: /usr/bin/systemctl start pylos-bot, /usr/bin/systemctl stop pylos-bot, /usr/bin/systemctl restart pylos-bot, /usr/bin/systemctl start --no-block pylos-update.service
```

Code thử `systemctl` thường (polkit) trước, không được thì `sudo -n systemctl`.

### 3. Bật chế độ systemd cho bot trên VPS

```bash
sudo -u pylos sh -c 'grep -q ^BOT_SUPERVISOR= /opt/pylos/userdata/config/settings.env || echo BOT_SUPERVISOR=systemd >> /opt/pylos/userdata/config/settings.env'
systemctl restart pylos-admin
```

### 4. nginx

Gói chuyển có thể vài chục MB: với `location` của trang quản lý thêm `client_max_body_size 200m;`,
`proxy_read_timeout 300s;` và `proxy_request_buffering off;`, không cache `/api/*`. Log trực tiếp cần `proxy_buffering off;`
cho `/api/logs/stream`.

### Kiểm tra

```bash
sudo -u pylos systemctl start pylos-bot && sudo -u pylos systemctl stop pylos-bot   # không bị hỏi mật khẩu
curl -s -H "Authorization: Bearer <ADMIN_TOKEN>" https://unousgrowth.com/api/server | head -c 300
```
