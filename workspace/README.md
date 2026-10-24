# Cách dùng bot trên Zalo

## Lệnh của chủ bot

Chỉ người có ID trùng `OWNER_ZALO_ID` mới dùng được. Người khác gõ lệnh thì bot im lặng bỏ qua.

| Lệnh | Tác dụng |
|---|---|
| `/allow` | Cho phép nhóm hiện tại dùng bot (gõ ngay trong nhóm đó) |
| `/deny` | Chặn nhóm hiện tại |
| `/mode` | Xem chế độ của nhóm |
| `/mode all` | Bộ lọc AI: trả lời khi được gọi, **hoặc** khi Gemini thấy tin đang nhờ bot (dù không gọi tên) |
| `/mode default` | Chỉ trả lời khi **được gọi**: tin bắt đầu bằng `/bot` (`BOT_TRIGGERS`), @tag acc bot, hoặc gọi tên bot (`BOT_NAMES`) |
| `/status` | Xem nhóm có được phép không, chế độ, số token đã dùng hôm nay |
| `/reset` | Xóa lịch sử hội thoại của nhóm |
| `/id` | Xem `chat_id` và `user_id` của bạn |
| `/help` | Danh sách lệnh |

Nhóm mới thêm luôn ở chế độ `default`.

## Gọi bot ở chế độ default

```
/bot thủ đô của Úc là gì?
```

## Lấy ID của bạn lần đầu

Khi `OWNER_ZALO_ID` còn trống, bất kỳ ai gõ `/id` cũng được bot trả lời, và log in `from_id` của mọi người nhắn tới. Lấy `user_id` của bạn, điền vào `.env`, rồi khởi động lại bot. Sau đó `/id` chỉ còn chủ bot dùng được.

## Hạn mức token

Khi tổng token trong ngày (giờ Việt Nam) vượt `DAILY_TOKEN_BUDGET`, nhóm ở chế độ `all` tạm hoạt động như `default` (không hỏi bộ lọc AI) đến hết ngày, và bot báo một lần trong nhóm.

## Các file trong thư mục này

- `SYSTEM.md`: tính cách và quy tắc trả lời của trợ lý. Sửa xong bot tự nạp lại.
- `MEMORY.md`: điều trợ lý cần nhớ lâu dài, được đưa vào prompt như dữ liệu tham khảo.
