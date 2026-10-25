# Cách dùng bot trên Zalo

## Ba vai trò

| Vai trò | Là ai | Được làm |
|---|---|---|
| **basic-user** | Mọi người trong chat đã được phép | Nhận việc, dùng lệnh xem, tự thêm lịch vào Google Lịch của chính mình. Không giao việc cho người khác |
| **leader** | Do owner hoặc leader khác thêm, theo từng nhóm | Thêm: giao việc cho người khác (`@a @b`) hoặc cho cả đội, tạo đội, cho người khác lên leader |
| **owner** | ID trùng `OWNER_ZALO_ID` | Thêm: lệnh về bộ lọc và chỉnh bot, gỡ leader |

Gõ `/help` để xem các lệnh bạn dùng được, `/vaitro` để xem vai trò của mình. Gõ lệnh không đủ quyền trong chat đã được phép thì bot báo "cần quyền …"; ở chat chưa được phép bot im lặng.

## Lệnh

| Lệnh | Vai trò tối thiểu | Tác dụng |
|---|---|---|
| `/help`, `/id`, `/vaitro` | basic | Danh sách lệnh bạn dùng được; xem `chat_id` và `user_id`; xem vai trò |
| `/leader` | basic | Xem ai là leader của nhóm |
| `/team`, `/team tên` | basic | Xem các đội, hoặc thành viên một đội |
| `/add leader @a @b` | leader | Cho a, b làm leader trong nhóm này (gõ tên hoặc Zalo ID nếu không tag được) |
| `/team tên @a @b` | leader | Tạo đội hoặc thêm người vào đội |
| `/team tên bo @a`, `/team xoa tên` | leader | Bỏ người khỏi đội, xoá đội |
| `/remove leader @a` | owner | Gỡ leader |
| `/leader all`, `/leader off` | owner | Cả nhóm là leader, hoặc xoá hết leader |
| `/allow`, `/deny` | owner | Cho phép nhóm hiện tại dùng bot (gõ ngay trong nhóm đó), hoặc chặn |
| `/mode` | owner | Xem chế độ của nhóm |
| `/mode all` | owner | Bộ lọc AI: trả lời khi được gọi, **hoặc** khi Gemini thấy tin đang nhờ bot (dù không gọi tên) |
| `/mode default` | owner | Chỉ trả lời khi **được gọi**: tin bắt đầu bằng `/bot` (`BOT_TRIGGERS`), @tag acc bot, hoặc gọi tên bot (`BOT_NAMES`) |
| `/status` | owner | Xem nhóm có được phép không, chế độ, số token đã dùng hôm nay |
| `/reset` | owner | Xóa lịch sử hội thoại của nhóm |

Dạng cũ vẫn chạy: `/leader @a` = `/add leader @a`; `/leader bo @a` = `/remove leader @a`. Tên đội không phân biệt hoa thường và dấu.

Nhóm mới thêm luôn ở chế độ `default`.

## Gọi bot ở chế độ default

```
/bot thủ đô của Úc là gì?
```

## Giao lịch cho người khác (web iforgotmywayhome)

Cần `SCHEDULE_API_KEY` (xem README, mục "Nối với web iforgotmywayhome").

**Mỗi người nhận lịch làm một lần:** mở web app (link chủ hệ thống gửi, vd `https://iforgotmywayhome.vercel.app/`), đăng nhập Gmail, bấm *Lấy mã liên kết*, rồi **nhắn riêng** cho acc bot đúng mã 6 số đó (hoặc `/lienket 123456`). Bot trả lời "Đã liên kết…". Sau đó bấm *Kết nối Google Lịch* trong app.

**Basic-user** tự thêm lịch cho mình (cần đã liên kết Zalo như trên):

```
roemnao nhắc tôi nộp báo cáo 9h sáng mai
roemnao lịch sắp tới của tôi?
```

**Leader / owner** giao cho người khác hoặc cho đội (đội đặt bằng `/team`):

```
roemnao giao @An @Bình họp kế hoạch 9h sáng mai ở phòng 301
roemnao giao cho nhóm thiết kế họp 9h sáng mai
roemnao dời cuộc họp lúc nãy sang 10h, thêm @Chi, bỏ Bình
roemnao huỷ cuộc họp lúc nãy
roemnao các lịch đã giao trong nhóm?
```

Basic-user nhờ giao cho người khác thì bot từ chối và bảo nhờ leader.

Bot báo ai đã nhận, ai chưa liên kết app. Lịch vào Google Lịch của từng người khi app của họ đang mở.

## Lấy ID của bạn lần đầu

Khi `OWNER_ZALO_ID` còn trống, bất kỳ ai gõ `/id` cũng được bot trả lời, và log in `from_id` của mọi người nhắn tới. Lấy `user_id` của bạn, điền vào `userdata/config/settings.env` (hoặc trang Cài đặt), rồi khởi động lại bot. Sau đó `/id` chỉ còn chủ bot dùng được.

## Hạn mức token

Khi tổng token trong ngày (giờ Việt Nam) vượt `DAILY_TOKEN_BUDGET`, nhóm ở chế độ `all` tạm hoạt động như `default` (không hỏi bộ lọc AI) đến hết ngày, và bot báo một lần trong nhóm.

## Các file trong thư mục này

- `SYSTEM.md`: tính cách và quy tắc trả lời của trợ lý. Sửa xong bot tự nạp lại.
- `MEMORY.md`: điều trợ lý cần nhớ lâu dài, được đưa vào prompt như dữ liệu tham khảo.
