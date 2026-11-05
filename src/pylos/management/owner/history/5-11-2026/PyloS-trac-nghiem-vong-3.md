# PyloS — Trắc nghiệm vòng 3 (chốt chỗ vênh, VPS, bảo mật)

> Cách dùng: như hai vòng trước. Vòng này **ít câu hơn**, chỉ hỏi chỗ vòng 2 còn vênh nhau, hoặc chỗ mình vừa đọc code/tài liệu VPS và thấy có rủi ro. Xong vòng này mình đủ dữ kiện để viết bản mô tả cấu trúc chính thức.

## Mình đã hiểu gì từ vòng 2 (sai chỗ nào sửa ngay ở đây)

- Tên: ẩn dụ thành phố, **snake_case** toàn bộ (`main_gate`, `side_gate`, `guest_house`, `short_term`, `long_term`), tiếng Anh cả thư mục lẫn tài liệu.
- Cổng phụ chỉ **nhận lệnh**; Toà điều phối **thi hành** (lập lịch, start/stop). Điều phối chứa: bus, đồng hồ chung, sổ đăng ký bot, hàng đợi + log phong bì, **quyền hạn (vai trò)**. Danh sách bot + bật/tắt ở Toà quản lý. Khoá bí mật ở Toà Owner.
- Toà Owner và nhà bot khác: lời dặn **+ lọc đường dẫn bằng code**.
- Túp lều: tự tạo ở tin nhắn đầu tiên; chứa repo, kết nối GitHub, lịch/việc, hồ sơ, file (**không** chứa session). Nhóm Zalo có túp lều riêng. Vào được: owner, bot đang phục vụ người đó, bot quản lý.
- Toà văn phòng: có "nhà kho" (thư mục lưu file phân loại); chỉ owner thêm plugin.
- Trí nhớ: kệ sách = tài liệu gốc; cơ bắp = kỹ năng; "mơ" chạy đêm / khi rảnh / khi ngắn hạn đầy, script lọc sơ + LLM; lên dài hạn khi gặp ≥N lần hoặc bot tự chấm; dài hạn không xoá (đưa vào kho lưu trữ); **thông tin gắn với người chỉ ghi vào túp lều**.
- Cơ bắp tự sửa hàng tuần, quản lý chấm (phản ứng người dùng, lỗi công cụ, token, mẫu hội thoại), điểm giảm thì hoàn lại. Persona tự sửa ở mục được phép.
- Kệ sách: bot tự chọn, bản sao có phiên bản; owner đọc nguồn ngoài trước; skill có thể kèm script.
- Owner qua Zalo chỉ cần đúng tài khoản; khẩn cấp không qua Hàng rào; nâng quyền tạm do owner cấp; toà mới do người/Claude Code tạo rồi ghi Bản đồ + báo owner.
- Hiện 1 bot, mỗi bot một process riêng; làm tài liệu trước; viết file luật cho Claude ngay giai đoạn tài liệu; ưu tiên "tìm file dễ".
- Bảng gán code vòng 2 đồng ý; trang quản trị web → `management/owner`, desktop → `side_gate`.
- 1 bot quản lý duy nhất lo quản lý file + các bot khác. **Hiện không có đầu việc nào đang chạy; điều quan trọng nhất là không làm gãy cập nhật tự động/chủ động trên VPS.**

---

## PHẦN A — Chỗ vòng 2 vênh nhau

**A1. Mã khởi động/tắt bot nằm ở đâu?** Vòng 2 bạn chọn "Điều phối thi hành start/stop" (A1-B) nhưng bỏ trống ô "bộ khởi động/tắt" của Điều phối (A2-E), còn bảng gán code lại đặt `bot_process.py` (chạy/dừng tiến trình, gọi `systemctl`) vào `side_gate`.
- [ ] A. Toàn bộ vào `dispatch`; `side_gate` chỉ nhận lệnh rồi chuyển vào
- [ ] B. `dispatch` ra quyết định (lịch, trạng thái, sổ đăng ký); thao tác hệ điều hành (systemctl, process) giữ ở `side_gate`
- [ ] C. Giữ như bảng gán vòng 2 (`bot_process.py` ở `side_gate`), `dispatch` chỉ lập lịch
- Khác: ______

**A2. Căn hộ `cron` ở Cổng phụ (bạn đã tick) hay chỉ ở Điều phối?** Bạn tick `cron` cho Cổng phụ, nhưng điều kiện ghi kèm là "nếu cron về Cổng phụ" mà bạn đã chọn hướng khác.
- [ ] A. Bỏ căn hộ `cron` ở Cổng phụ; lịch nằm ở `dispatch`
- [ ] B. Giữ `side_gate/cron` để **định nghĩa** lịch (nhận từ owner); `dispatch` chạy theo lịch đó
- [ ] C. Lịch hệ thống ở `dispatch`; lịch riêng của từng bot ở căn hộ bot, `dispatch` gom lại
- Khác: ______

**A3. "Người lạ" là ai?** Bạn chọn chống spam chỉ cho người lạ "chưa có túp lều" (A7-C), nhưng túp lều tự tạo ngay tin nhắn đầu (C3-A) nên sẽ không bao giờ có người nào chưa có túp lều.
- [ ] A. Người lạ = người mới nhắn trong N giờ đầu (túp lều vẫn tạo, nhưng bị giới hạn tin/phút trong khoảng đó)
- [ ] B. Người lạ = chưa nằm trong danh sách owner duyệt (túp lều tạo ngay, đánh dấu "chưa duyệt", giới hạn đến khi duyệt)
- [ ] C. Bỏ khái niệm người lạ: giới hạn tin/phút áp đều cho mọi người
- Khác: ______

**A4. Bot khác vào túp lều?** Vòng 1 (câu 34-B) bạn chọn "chia sẻ dữ liệu người dùng qua Đại sảnh, xin phép từng lần", nhưng vòng 2 bạn không tick "bot khác xin qua Đại sảnh" (C4-C).
- [ ] A. Bỏ hẳn: bot khác **không bao giờ** vào túp lều của người X (chỉ owner, bot đang phục vụ X, bot quản lý)
- [ ] B. Giữ câu 34-B: được, qua Đại sảnh, có X cho phép
- [ ] C. Hoãn đến khi có ≥2 bot (như A5-D), tạm ghi là "chưa dùng"
- Khác: ______

**A5. Trong nhóm Zalo, bot có đọc túp lều cá nhân của các thành viên không?** (nhóm có túp lều riêng)
- [ ] A. Không. Trong nhóm chỉ dùng túp lều của nhóm; túp lều cá nhân chỉ mở khi chat riêng với người đó
- [ ] B. Chỉ đọc phần "công khai" của từng người (vd tên gọi), không đọc lịch/việc/hồ sơ
- [ ] C. Được đọc của người đang nói (người vừa nhắn trong nhóm)
- Khác: ______

**A6. Trí nhớ ngắn hạn lấy dữ liệu từ hội thoại, nhưng thông tin gắn với người chỉ được ghi vào túp lều (E8-A). Khi "mơ" xử lý thì sao?**
- [ ] A. Ngắn hạn **chỉ chứa phần đã bỏ danh tính** ngay lúc ghi ("khách hay hỏi giờ giao hàng"); phần gắn người ghi thẳng vào túp lều, không qua ngắn hạn
- [ ] B. Ngắn hạn tạm giữ cả phần gắn người; khi "mơ", phần gắn người đẩy vào túp lều, phần chung lên dài hạn
- [ ] C. Ngắn hạn giữ tạm, nhưng có nhãn chủ nhân và bị xoá hẳn khi "mơ" xong
- Khác: ______

**A7. Khoá bí mật ở Toà Owner (D5-B), nhưng hiện chúng nằm trong `userdata/config/settings.env`, và gói chuyển máy↔VPS cố ý loại file này.** Sau khi đổi:
- [ ] A. Chuyển nội dung sang `owner/` (vẫn gitignore, vẫn loại khỏi gói chuyển)
- [ ] B. Giữ `settings.env` ở chỗ cũ (ngoài cây Thành); `owner/` chỉ chứa phần mô tả/hướng dẫn về các khoá
- [ ] C. `owner/` chứa bản mẫu; file thật tạo trên từng máy, không đồng bộ
- Khác: ______

---

## PHẦN B — Đại sảnh làm đầu tiên: bus

**B1. Mỗi bot một process (H2-B) và bus giữa các khu. Công nghệ bus?**
- [ ] A. Hàng đợi bằng SQLite (không cần dịch vụ thêm, sống sót khi khởi động lại)
- [ ] B. HTTP cục bộ (127.0.0.1) giữa các process
- [ ] C. Redis/dịch vụ hàng đợi riêng (cần cài thêm trên VPS)
- [ ] D. Thư mục hộp thư (file)
- [ ] E. Chưa chọn; giai đoạn tài liệu chỉ ghi "giao diện bus", mình đề xuất khi tới giai đoạn code
- Khác: ______

**B2. Sau giai đoạn "chỉ làm tài liệu" (42-A), bước kế tiếp là gì?**
- [ ] A. Đổi tên/dời thư mục thật **chỉ Khu đại sảnh** trước
- [ ] B. Thêm code bus nhưng giữ nguyên cấu trúc thư mục cũ
- [ ] C. Dời thư mục thật từng khu theo thứ tự đại sảnh → cổng → dân cư → quản lý
- [ ] D. Tuỳ lúc đó, mình đề xuất rồi bạn duyệt
- Khác: ______

**B3. Bạn lo "chậm vì đi vòng qua Đại sảnh" (câu 44-D). Mức trễ chấp nhận được thêm?**
- [ ] A. Dưới 100 ms (gần như không cảm nhận)
- [ ] B. Dưới 1 giây (so với vài giây bot gọi LLM thì không đáng kể)
- [ ] C. Không quan tâm miễn đúng, chưa đo
- Khác: ______

---

## PHẦN C — VPS (mình vừa đọc `docs/vps-dieu-khien.md` và `src/bot/system/`)

Những điều đang buộc vào đường dẫn hiện tại:
- Service `pylos-bot.service` (do **root** cài) chạy `python -m bot run` với `PYTHONPATH=/opt/pylos/src`. User `em`/`pylos` không sửa được file service.
- `pylos-update.service` = `git pull` + khởi động lại. Chuyển bot máy↔VPS dùng gói zip từ `userdata/data`, `processed_message_ids.txt`, phiên Zalo cá nhân.
- Chế độ chờ dùng file `userdata/system/standby.txt` (exit code 5).

→ Nếu đổi tên/dời gói `bot` khi chưa sửa service bằng root, bot trên VPS **không lên lại được sau lần cập nhật tự động đầu tiên**.

**C1. Lối vào của bot khi cấu trúc mới xuất hiện?**
- [ ] A. Giữ gói `bot` và lệnh `python -m bot run` làm lối vào cố định (một file mỏng gọi sang cấu trúc mới); service trên VPS **không phải đổi**
- [ ] B. Đổi tên lối vào (vd `python -m pylos run`); có kế hoạch cho root sửa service một lần, kèm cách quay về
- [ ] C. Giữ lối vào cũ vĩnh viễn, chỉ code bên trong được dời
- Khác: ______

**C2. Tên và vị trí gói gốc của Thành chính?**
- [ ] A. `src/pylos/` (import `pylos.gate.main_gate…`)
- [ ] B. Thư mục `PyloS/` ở gốc repo, cạnh `docs/`, `tests/`
- [ ] C. Giữ `src/bot/` làm gốc, các khu nằm bên trong
- Khác: ______

**C3. `userdata/` (dữ liệu, cấu hình, standby, gói chuyển) khi cấu trúc đổi?**
- [ ] A. Để nguyên ngoài cây Thành; một lớp đường dẫn (kiểu `userdata_paths.py` hiện có) ánh xạ vào túp lều/căn hộ
- [ ] B. Dời hẳn vào các toà (túp lều, căn hộ bot…)
- [ ] C. Để nguyên giờ, dời sau khi bản đồ ổn định
- Khác: ______

**C4. Chuyển bot máy↔VPS khi hai bên khác phiên bản cấu trúc (một bên đã cập nhật, một bên chưa)?**
- [ ] A. Chặn chuyển khi khác phiên bản (ghi phiên bản cấu trúc vào gói chuyển và so khớp)
- [ ] B. Tự chuyển đổi dữ liệu khi nhận
- [ ] C. Không xử lý, người dùng tự đảm bảo hai bên cùng bản
- Khác: ______

**C5. Trước khi đẩy thay đổi cấu trúc lên VPS, cần kiểm bằng gì?** (chọn nhiều)
- [ ] A. Chạy thử đầy đủ ở máy Windows trước
- [ ] B. Test tự động mô phỏng việc "cập nhật xong khởi động lại" (kiểm `python -m bot run` còn lên, đường dẫn còn đúng)
- [ ] C. Một bản thử riêng trên VPS (cổng/service khác) trước khi động vào bản thật
- [ ] D. Owner xem kế hoạch từng bước rồi mới cho đẩy
- Khác: ______

**C6. Nếu bản cập nhật làm bot không lên trên VPS?**
- [ ] A. `pylos-update` tự kiểm sau khi khởi động lại (bot lên không), không lên thì tự quay về commit trước
- [ ] B. Owner xử lý tay (trang quản trị, SSH)
- [ ] C. A và có cảnh báo cho owner qua Zalo
- Khác: ______

---

## PHẦN D — Bot quản lý duy nhất

**D1. "Quản lý file" gồm những việc nào?** (chọn nhiều)
- [ ] A. Biên tập Thư viện (thêm/sắp xếp/báo bản mới)
- [ ] B. Sinh và cập nhật Bản đồ (`atlas`)
- [ ] C. Dọn nhà kho Toà văn phòng (file quá hạn)
- [ ] D. Dọn/nén kho lưu trữ trí nhớ dài hạn
- [ ] E. Theo dõi kệ sách lệch phiên bản
- [ ] F. Kế hoạch/báo cáo ở Toà quản lý
- Khác: ______

**D2. Hiện chỉ có 1 bot (bot trò chuyện). Bot quản lý khi nào xuất hiện?**
- [ ] A. Làm sau khi cấu trúc xong, **trước** khi có bot dân cư thứ hai; đến lúc đó owner/script đóng vai quản lý
- [ ] B. Bot hiện tại tạm kiêm quản lý
- [ ] C. Chưa có bot quản lý cho đến khi thật sự có ≥2 bot dân cư
- Khác: ______

---

## PHẦN E — Bảo mật (mình đánh dấu vì các lựa chọn cộng lại tạo lỗ hổng)

**E1. Lệnh nguy hiểm qua Zalo chỉ cần đúng tài khoản owner (G1-A) và khẩn cấp đi tắt Hàng rào (G2-A), trong khi Cổng phụ có căn hộ `shell` (lệnh cmd) và `vps`. Nghĩa là ai chiếm được tài khoản Zalo của owner thì chạy được lệnh shell trên VPS.** Bạn muốn?
- [ ] A. Chấp nhận như đã chọn
- [ ] B. Lệnh `shell` và các lệnh phá huỷ (xoá dữ liệu, tắt hệ thống) **chỉ chạy từ trang quản trị web** (đăng nhập Google), không chạy từ Zalo; Zalo chỉ cho lệnh nhẹ (trạng thái, khởi động lại bot)
- [ ] C. Zalo vẫn chạy được, nhưng lệnh nguy hiểm cần mã phụ (PIN)
- Khác: ______

**E2. Skill có thể kèm script (F4-B), cơ bắp là kỹ năng bot tự sửa hàng tuần (E7-A), mà chỉ owner được thêm plugin (C7-A). Script nằm trong skill có đi vòng được luật plugin không?**
- [ ] A. Cơ bắp (do bot tự sửa) chỉ chứa **văn bản**; script chỉ chạy nếu thuộc Thư viện đã được owner duyệt, và chạy qua Toà văn phòng
- [ ] B. Script trong skill chạy trực tiếp trong căn hộ bot (không cần qua Toà văn phòng)
- [ ] C. Script cần owner duyệt từng cái, kể cả skill từ Thư viện
- Khác: ______

**E3. Persona tự sửa "ở mục được phép" (E9-C). Khoá phần quy tắc bằng cách nào?**
- [ ] A. Phần quy tắc nằm **ngoài** căn hộ bot (ở Toà quản lý/Toà Owner), nạp vào prompt khi chạy; trong căn hộ chỉ có phần giọng văn/thói quen
- [ ] B. Cùng căn hộ nhưng tách file; lớp lọc đường dẫn chặn ghi vào file quy tắc
- [ ] C. Chỉ dựa vào lời dặn trong prompt
- Khác: ______

**E4. Nâng quyền tạm do owner cấp (G3-A) nhưng bạn không chọn hạn hay nhiệm vụ gắn kèm. Mặc định?**
- [ ] A. Hết hạn tự động sau N giờ (N = ____)
- [ ] B. Gắn với một nhiệm vụ, xong thì thu hồi
- [ ] C. Không hết hạn; owner thu hồi khi muốn (hiện trong sổ đăng ký để dễ thấy)
- Khác: ______

---

## PHẦN F — Kiểm thử

**F1. Test (hiện ở `tests/` ngoài cùng) sau khi có Thành chính nằm ở đâu?**
- [ ] A. Thư mục `tests/` bên trong từng toà (test nằm cạnh code nó kiểm)
- [ ] B. `tests/` ngoài cùng, nhưng cấu trúc thư mục phản chiếu cấu trúc Thành
- [ ] C. Giữ nguyên `tests/` phẳng như hiện nay
- Khác: ______

---

## Câu hỏi mở

1. Còn chỗ nào trong bản "Mình đã hiểu" ở đầu file mà bạn thấy sai hoặc thiếu? ______
2. Sau vòng này, bạn muốn mình làm gì tiếp: viết **bản mô tả cấu trúc chính thức** (tài liệu + bảng bản đồ + file luật cho Claude), hay hỏi thêm vòng nữa? ______
