# PyloS — Trắc nghiệm làm rõ cấu trúc "Thành chính"

> Mục đích: chỉ để HỎI và LÀM RÕ, chưa quyết định xây gì.
> Cách dùng: đánh dấu `[x]` vào đáp án đúng ý bạn (có thể chọn nhiều nếu câu ghi "chọn nhiều").
> Không có đáp án nào là "đúng sẵn" – mọi lựa chọn đều là một cách hiểu khả dĩ. Nếu không đáp án nào đúng, ghi vào dòng **Khác**.
> Xong thì gửi lại file, mình sẽ chốt thành bản mô tả cấu trúc chính thức.

---

## PHẦN 1 — Khái niệm nền (Thành chính / Nội thành / Ngoại thành / 3 tầng)

**Câu 1. "Ngoại thành" gồm những gì?** (chọn nhiều)
- [ ] A. Zalo (người dùng, tài khoản Zalo)
- [ ] B. Bot chạy ngoài PyloS (không nằm trong thư mục PyloS)
- [ ] C. Thư mục/máy/VPS/repo GitHub của người dùng
- [ ] D. Các app, API, dịch vụ bên thứ ba
- Khác: ______

**Câu 2. Quan hệ giữa "Thành chính" và "Nội thành"?**
- [ ] A. Thành chính = thư mục gốc `PyloS/`; Nội thành = toàn bộ bên trong nó (Thành chính ≡ Nội thành về mặt thư mục)
- [ ] B. Thành chính = `PyloS/`; Nội thành = chỉ 4 khu (không tính file gốc như README, cấu hình chung)
- [ ] C. Nội thành là vùng được bảo vệ, còn Thành chính còn gồm cả "vành đai" (log, cache, tạm) nằm ngoài nội thành
- Khác: ______

**Câu 3. Ba tầng (Khu vực → Toà → Căn hộ) có phải là 3 cấp thư mục cứng?**
- [ ] A. Đúng: `PyloS/<khu>/<toà>/<căn hộ>/` – luôn đủ 3 cấp
- [ ] B. 3 cấp là quy ước khái niệm, thư mục thật có thể nông hơn (vd Toà không cần căn hộ nếu không có gì để chia)
- [ ] C. 3 cấp thư mục nhưng "căn hộ" chỉ tồn tại ở Khu dân cư; các khu khác dùng file trực tiếp trong toà
- Khác: ______

**Câu 4. "Căn hộ" (Tầng 3) là đơn vị gì?**
- [ ] A. 1 căn hộ = 1 bot
- [ ] B. 1 căn hộ = 1 chức năng/module (vd plugin vẽ, kết nối Zalo, cron…)
- [ ] C. 1 căn hộ = 1 người dùng/1 cuộc trò chuyện (vd theo zaloUid)
- [ ] D. Tuỳ toà: ở Khu dân cư là bot, ở Khu cổng là module, ở Khu quản lý là chủ đề
- Khác: ______

**Câu 5. Tên thư mục thật nên đặt thế nào?**
- [ ] A. Tiếng Việt có dấu đúng như trên (`Khu cổng/Cổng chính/…`)
- [ ] B. Tiếng Việt không dấu (`khu-cong/cong-chinh/…`)
- [ ] C. Tên tiếng Anh tương ứng (`gate/main-gate/…`) và giữ tên Việt trong tài liệu
- [ ] D. Mã số + tên (`02-khu-cong/01-cong-chinh/…`) để sắp xếp ổn định
- Khác: ______

---

## PHẦN 2 — Khu quản lý (Toà Owner, Toà quản lý)

**Câu 6. Toà Owner "bot không được truy cập" — cấm ở mức nào?**
- [ ] A. Chỉ là quy ước/lời dặn trong prompt của bot
- [ ] B. Chặn bằng code (đường dẫn bị lọc ở lớp công cụ file của bot)
- [ ] C. Chặn bằng hệ điều hành (user/quyền thư mục riêng cho bot, sandbox)
- [ ] D. Bot thậm chí không được biết toà này tồn tại (không xuất hiện trong bản đồ bot nhìn thấy)
- Khác: ______

**Câu 7. Toà Owner chứa gì là chính?** (chọn nhiều)
- [ ] A. Danh sách bot + cấu hình/bật tắt từng bot
- [ ] B. Khoá bí mật, token (nếu có)
- [ ] C. Quyền hạn của từng bot / từng người dùng
- [ ] D. Nhật ký owner đã làm gì
- [ ] E. Kế hoạch riêng/ghi chú riêng của owner
- Khác: ______

**Câu 8. "Bot quản lý" là loại bot nào và sống ở đâu?**
- [ ] A. Bot đặc biệt, "nhà" nằm ở Toà quản lý, chỉ làm việc quản lý
- [ ] B. Bot bình thường (ở Khu dân cư) nhưng được cấp quyền đọc Toà quản lý
- [ ] C. Có cả hai: bot quản lý cố định + bot thường được nâng quyền tạm thời
- Khác: ______

**Câu 9. Bot quản lý được phép LÀM gì với bot khác?** (chọn nhiều)
- [ ] A. Chỉ đọc trạng thái/báo cáo
- [ ] B. Giao việc/nhắn hướng dẫn
- [ ] C. Bật/tắt/khởi động lại bot khác
- [ ] D. Sửa memory/workspace của bot khác (nếu có, điều này mâu thuẫn "file riêng bot khác không được truy cập" ở Toà nhà dân – xem Câu 27)
- [ ] E. Tạo/xoá bot
- Khác: ______

**Câu 10. "Lệnh quản lý bot" ở Toà quản lý khác gì "lệnh owner" ở Cổng phụ?**
- [ ] A. Lệnh quản lý = bot dùng; lệnh owner = chỉ người owner gõ (qua Zalo/CLI)
- [ ] B. Lệnh quản lý = thao tác lên bot (tạo, giao việc); lệnh owner = thao tác lên hệ thống (VPS, cron, restart)
- [ ] C. Thực chất là một bộ lệnh, chỉ khác quyền người gọi
- Khác: ______

**Câu 11. "Khu quản lý: có kế hoạch xây dựng, quản lý project" – kế hoạch này nằm ở đâu?**
- [ ] A. Toà quản lý (bot quản lý đọc được)
- [ ] B. Toà Owner (chỉ owner)
- [ ] C. Chia đôi: kế hoạch công khai cho bot ở Toà quản lý, kế hoạch riêng ở Toà Owner
- Khác: ______

---

## PHẦN 3 — Khu cổng (Cổng chính, Hàng rào, Cổng phụ)

**Câu 12. Hướng dữ liệu đi qua Hàng rào?**
- [ ] A. Chỉ chiều VÀO (Zalo → nội thành)
- [ ] B. Chỉ chiều RA (nội thành → Zalo)
- [ ] C. Cả hai chiều: lọc đầu vào (độ dài, spam) và lọc đầu ra (phát ngôn, đạo đức)
- [ ] D. Cả hai chiều + cả luồng bot ↔ bot trong nội thành (qua Đại sảnh)
- Khác: ______

**Câu 13. Hàng rào "chứa giới hạn" – chỉ chứa luật hay chứa cả cơ chế thực thi?**
- [ ] A. Chỉ chứa file luật/cấu hình (số liệu, danh sách cấm); code thực thi nằm chỗ khác
- [ ] B. Chứa cả luật lẫn code kiểm tra
- [ ] C. Luật ở Hàng rào, nhưng bot vẫn tự giữ một lớp kiểm tra cuối
- Khác: ______

**Câu 14. Khi vi phạm hàng rào (vượt token limit, phát ngôn xấu…) thì xử lý?**
- [ ] A. Chặn hẳn và báo lỗi cho người gửi
- [ ] B. Cắt/sửa nội dung rồi cho đi tiếp
- [ ] C. Giữ lại chờ owner duyệt
- [ ] D. Tuỳ loại giới hạn (token → cắt; đạo đức → chặn; …)
- Khác: ______

**Câu 15. Token limit áp theo đơn vị nào?** (chọn nhiều)
- [ ] A. Mỗi tin nhắn
- [ ] B. Mỗi người dùng Zalo / ngày
- [ ] C. Mỗi bot / ngày
- [ ] D. Toàn hệ thống / tháng
- Khác: ______

**Câu 16. Cổng chính đang gom nhiều thứ: plugin vẽ/trình bày, code truy cập Zalo/app/ngoại thành, repo người dùng, session, log. Bạn muốn?**
- [ ] A. Giữ nguyên tất cả trong 1 toà Cổng chính, chia bằng căn hộ (Tầng 3)
- [ ] B. Tách plugin "vẽ, trình bày" ra khỏi Cổng chính (vì là công cụ tạo nội dung, không phải cổng)
- [ ] C. Tách log + session ra chỗ riêng (dữ liệu vận hành, không phải code)
- [ ] D. Tách cả B và C
- Khác: ______

**Câu 17. Vì sao plugin vẽ/trình bày văn bản nằm ở Cổng chính chứ không ở Toà thư viện hay nhà bot?**
- [ ] A. Vì chúng là "định dạng đầu ra" trước khi gửi ra ngoài (Zalo hiển thị được)
- [ ] B. Vì mọi bot dùng chung, đặt ở cổng cho đỡ lặp
- [ ] C. Chưa có lý do rõ – cần xem lại vị trí
- Khác: ______

**Câu 18. Repo GitHub "người dùng yêu cầu PyloS dùng/xem/sửa" – lưu thế nào?**
- [ ] A. Chỉ lưu thông tin kết nối (URL, token, nhánh) ở Cổng chính; mã nguồn clone nơi khác
- [ ] B. Clone luôn mã nguồn vào Cổng chính
- [ ] C. Clone vào nơi riêng của người yêu cầu (căn hộ/không gian người dùng)
- Khác: ______

**Câu 19. Việc sửa repo người dùng cần điều kiện gì?**
- [ ] A. Người yêu cầu xác nhận từng lần
- [ ] B. Bot được làm trên nhánh riêng, owner duyệt mới merge
- [ ] C. Chỉ đọc, không cho sửa
- Khác: ______

**Câu 20. Cổng phụ "liên kết với VPS, cron, MCP" khác gì Toà điều phối (Khu đại sảnh) cũng "chứa cron, lệnh khởi động/tắt"?**
- [ ] A. Cổng phụ = giao diện nói chuyện với bên ngoài về kỹ thuật (nhận lệnh, kết nối VPS); Toà điều phối = lõi chạy cron/khởi động bên trong
- [ ] B. Cổng phụ giữ cấu hình cron, Toà điều phối giữ bộ chạy cron
- [ ] C. Đang trùng nhau – nên gom về một nơi (chỉ ra nơi nào ở Câu 21)
- Khác: ______

**Câu 21. Nếu phải gom về một nơi, cron/khởi động/tắt nên ở đâu?**
- [ ] A. Toà điều phối (Đại sảnh)
- [ ] B. Cổng phụ
- [ ] C. Giữ cả hai nhưng đặt ranh giới rõ (ghi ở Câu 20)
- Khác: ______

**Câu 22. "Yêu cầu khẩn cấp từ Cổng chính" gồm những gì?** (chọn nhiều)
- [ ] A. Lệnh dừng khẩn (kill-switch) toàn hệ thống
- [ ] B. Bot bị lạm dụng/spam cần cô lập ngay
- [ ] C. Lỗi nghiêm trọng của kết nối Zalo
- [ ] D. Owner nhắn lệnh đặc biệt qua Zalo
- Khác: ______

**Câu 23. Khẩn cấp có được bỏ qua quy tắc "mọi luồng phải qua Đại sảnh" không?**
- [ ] A. Không, vẫn đi qua Đại sảnh nhưng với làn ưu tiên
- [ ] B. Có, Cổng chính → Cổng phụ đi thẳng (ngoại lệ duy nhất)
- [ ] C. Có, nhưng ghi log song song vào Đại sảnh
- Khác: ______

---

## PHẦN 4 — Khu đại sảnh (Thư viện, Bản đồ, Điều phối)

**Câu 24. "Tất cả luồng dữ liệu muốn đến khu khác đều phải qua đại sảnh" – cơ chế vật lý là gì?**
- [ ] A. Tin nhắn qua hàng đợi/bus nội bộ (Đại sảnh là bộ định tuyến)
- [ ] B. Thư mục hộp thư (file) – mỗi khu có "hòm thư" trong Đại sảnh
- [ ] C. API/HTTP nội bộ
- [ ] D. Chưa chọn cơ chế; chỉ cần quy tắc "đi qua Đại sảnh" trước
- Khác: ______

**Câu 25. Đại sảnh có được đọc NỘI DUNG tin đi qua không?**
- [ ] A. Có, vì cần ghi log/định tuyến theo nội dung
- [ ] B. Chỉ đọc phong bì (ai gửi, tới đâu, loại), không đọc nội dung
- [ ] C. Đọc nội dung nhưng bỏ phần nhạy cảm khi ghi log
- Khác: ______

**Câu 26. Bot ↔ bot trong cùng Khu dân cư cũng phải qua Đại sảnh?**
- [ ] A. Có, không ngoại lệ
- [ ] B. Chỉ khi hai bot khác nhóm/khác quyền
- [ ] C. Không, chỉ luồng liên khu mới qua Đại sảnh
- Khác: ______

**Câu 27. Ba toà của Đại sảnh – ai được đọc/ghi?**

| Toà | Bot thường | Bot quản lý | Owner |
|---|---|---|---|
| Thư viện | ? | ? | ? |
| Bản đồ | ? | ? | ? |
| Điều phối | ? | ? | ? |

Chọn một kiểu chung (hoặc ghi chi tiết ở "Khác"):
- [ ] A. Thư viện: mọi bot đọc; Bản đồ: mọi bot đọc; Điều phối: bot không đụng (chỉ owner + quản lý)
- [ ] B. Thư viện & Bản đồ: mọi bot đọc, chỉ quản lý/owner ghi; Điều phối: chỉ owner
- [ ] C. Bot được ghi thêm vào Thư viện (học được gì thì ghi lại)
- Khác: ______

**Câu 28. Toà bản đồ "lưu bản đồ chi tiết toàn bộ nội thành" – tạo và cập nhật bằng cách nào?**
- [ ] A. Tự sinh bằng script quét thư mục (luôn đúng thực tế)
- [ ] B. Viết tay (dễ sai lệch)
- [ ] C. Script sinh khung + người/bot ghi chú mô tả thêm
- Khác: ______

**Câu 29. Bản đồ có chứa vị trí Toà Owner không (mà bot không được biết)?**
- [ ] A. Có, đầy đủ (một bản duy nhất)
- [ ] B. Hai bản: bản đầy đủ cho owner, bản lược bỏ Toà Owner cho bot
- [ ] C. Không ghi Toà Owner trong bản đồ
- Khác: ______

**Câu 30. Toà thư viện (kiến thức, hướng dẫn) khác gì "Toà quản lý (hướng dẫn quản lý bot)" và "Khu quản lý – nơi hướng dẫn"?**
- [ ] A. Thư viện = kiến thức chung cho mọi bot; Toà quản lý = hướng dẫn riêng cho vai trò quản lý
- [ ] B. Thư viện = kiến thức bên ngoài (tài liệu, FAQ); Toà quản lý = quy trình nội bộ
- [ ] C. Đang chồng chéo, cần gộp
- Khác: ______

---

## PHẦN 5 — Khu dân cư (Toà nhà dân)

**Câu 31. "File riêng từng bot mà bot khác không được truy cập" – người nào ngoài chủ căn hộ được vào?** (chọn nhiều)
- [ ] A. Owner
- [ ] B. Bot quản lý (xem để giám sát)
- [ ] C. Đại sảnh/Điều phối (để sao lưu, khởi động)
- [ ] D. Không ai khác
- Khác: ______

**Câu 32. Trong căn hộ của 1 bot có những gì?** (chọn nhiều)
- [ ] A. Workspace làm việc (file tạm, bản nháp)
- [ ] B. Memory dài hạn
- [ ] C. Cấu hình/tính cách (persona) của bot
- [ ] D. Lịch/việc riêng của bot
- [ ] E. Dữ liệu riêng từng người dùng Zalo mà bot phục vụ
- Khác: ______

**Câu 33. Dữ liệu riêng của từng người Zalo (lịch, việc, sở thích) – lưu ở đâu?**
- [ ] A. Trong căn hộ của bot phục vụ người đó, chia thư mục theo zaloUid
- [ ] B. Ở Khu cổng (vì zaloUid là danh tính ngoại thành)
- [ ] C. Có "căn hộ người dùng" riêng, bot được cấp quyền đọc/ghi khi phục vụ
- Khác: ______

**Câu 34. Nếu 2 bot cùng phục vụ một người dùng, dữ liệu người đó chia sẻ thế nào?**
- [ ] A. Mỗi bot giữ bản riêng, không chia sẻ
- [ ] B. Chia sẻ phần dữ liệu người dùng qua Đại sảnh (xin phép từng lần)
- [ ] C. Lưu chung 1 nơi, hai bot cùng truy cập
- Khác: ______

**Câu 35. "Nghỉ ngơi" của bot nghĩa là gì trong hệ thống?**
- [ ] A. Bot ở trạng thái ngủ (không xử lý), có thể đánh thức
- [ ] B. Bot được lưu/sao lưu trạng thái, process dừng
- [ ] C. Chỉ là cách gọi hình tượng cho "thư mục của bot"
- Khác: ______

**Câu 36. Khu dân cư hiện chỉ có 1 toà (Toà nhà dân). Về sau mở rộng thế nào?**
- [ ] A. Thêm toà theo nhóm bot (vd toà bot công việc, toà bot giải trí)
- [ ] B. Thêm toà theo người dùng/khách hàng
- [ ] C. Giữ 1 toà, chỉ thêm căn hộ
- Khác: ______

---

## PHẦN 6 — Luồng đi, phân quyền, thực thi

**Câu 37. Đường đi một tin nhắn Zalo → trả lời. Đáp án nào đúng nhất?**
- [ ] A. Zalo → Cổng chính → Hàng rào → Đại sảnh → Bot (Khu dân cư) → Đại sảnh → Hàng rào → Cổng chính → Zalo
- [ ] B. Giống A nhưng Hàng rào chỉ kiểm lúc ra, không kiểm lúc vào
- [ ] C. Giống A nhưng bot khi cần công cụ (vẽ, Zalo, repo) gọi Cổng chính qua Đại sảnh
- [ ] D. Khác: ______

**Câu 38. Bot muốn dùng plugin vẽ của Cổng chính thì đi đường nào?**
- [ ] A. Bot → Đại sảnh → Cổng chính (đúng quy tắc, mọi thứ qua Đại sảnh)
- [ ] B. Bot gọi thẳng plugin (plugin là thư viện, không phải "luồng dữ liệu")
- [ ] C. Plugin được "đặt" vào Thư viện để bot gọi, Cổng chính chỉ giữ bản gốc
- Khác: ______

**Câu 39. Ma trận truy cập – bạn muốn mức mặc định nào?**
- [ ] A. Mặc định CẤM, chỉ mở những gì liệt kê (whitelist)
- [ ] B. Mặc định MỞ trong nội thành, chỉ cấm các điểm đã nêu (Toà Owner, nhà dân của bot khác)
- [ ] C. Mặc định theo khu: Quản lý & Cổng đóng, Đại sảnh & Dân cư mở
- Khác: ______

**Câu 40. Quy tắc này được kiểm tra bằng cách nào?**
- [ ] A. Script kiểm cấu trúc (thư mục có đúng 4 khu/9 toà không)
- [ ] B. Test kiểm tra import/đường dẫn chéo khu (vd code Khu dân cư không được `import` thẳng Khu cổng)
- [ ] C. Chỉ tài liệu, chưa tự động kiểm
- [ ] D. A + B
- Khác: ______

**Câu 41. Số liệu đếm: có 4 khu, 9 toà (2 + 3 + 3 + 1). Bạn thấy?**
- [ ] A. Đúng và đủ, không thêm toà
- [ ] B. Thiếu: toà lưu log/sao lưu (nơi nào đó chưa có)
- [ ] C. Thiếu: toà cho dữ liệu người dùng
- [ ] D. Thiếu: toà thử nghiệm/staging
- Khác: ______

---

## PHẦN 7 — Chuyển đổi từ hiện trạng

**Câu 42. Cách áp cấu trúc này lên mã đang chạy trên VPS?**
- [ ] A. Chỉ vẽ lên tài liệu/bản đồ trước, chưa đổi thư mục thật
- [ ] B. Đổi thư mục từng khu một, khu nào xong chạy được mới sang khu tiếp
- [ ] C. Đổi toàn bộ một lần ở nhánh riêng rồi merge
- [ ] D. Làm song song: giữ cấu trúc cũ chạy, dựng "thành mới" bên cạnh rồi chuyển
- Khác: ______

**Câu 43. Khu nào nên làm ĐẦU TIÊN?**
- [ ] A. Khu đại sảnh (xương sống, mọi thứ phụ thuộc)
- [ ] B. Khu cổng (đang chạm Zalo thật)
- [ ] C. Khu dân cư (chuyển workspace/memory bot)
- [ ] D. Khu quản lý (chỉ tài liệu, ít rủi ro)
- Khác: ______

**Câu 44. Điều bạn lo nhất khi làm cấu trúc này?** (chọn nhiều)
- [ ] A. Bot đang chạy bị gián đoạn khi đổi đường dẫn
- [ ] B. Quá phức tạp, khó nhớ/khó tìm file
- [ ] C. Bot truy cập nhầm chỗ cấm
- [ ] D. Chậm vì mọi thứ phải đi vòng qua Đại sảnh
- [ ] E. Rò dữ liệu riêng giữa các người dùng
- Khác: ______

---

## Câu hỏi mở (viết tự do)

1. Một ví dụ cụ thể bạn muốn cấu trúc này giải quyết (một tình huống thật đã gặp): ______
2. Có khu/toà nào bạn đang nghĩ thêm mà chưa ghi trong mô tả: ______
3. Có chỗ nào trong mô tả gốc bạn tự thấy chưa chắc: ______
