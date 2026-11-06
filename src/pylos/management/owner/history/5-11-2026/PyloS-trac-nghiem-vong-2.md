# PyloS — Trắc nghiệm vòng 2 (đào sâu)

> Cách dùng: như vòng 1 — đánh dấu `[x]`, ghi vào **Khác** nếu không đáp án nào đúng. Chọn nhiều khi câu ghi "(chọn nhiều)".
> Vòng này chỉ hỏi những chỗ **vòng 1 để lộ ra**: chỗ mâu thuẫn, thứ mới phát sinh (Toà khách, túp lều, Toà văn phòng, kệ sách, hệ trí nhớ), và chỗ chưa nói.

## Mình đã hiểu gì từ vòng 1 (sai chỗ nào thì sửa ngay ở đây)

- Tên thư mục và tài liệu: **toàn bộ tiếng Anh**. Ba tầng là 3 cấp thư mục thật `PyloS/<khu>/<toà>/<căn hộ>/`, bên trong căn hộ tuỳ ý.
- Căn hộ: Khu dân cư = bot; Khu cổng = module; Khu quản lý = chủ đề.
- Toà Owner: chỉ cấm bằng lời dặn trong prompt; chứa nhật ký owner + kế hoạch riêng. Kế hoạch chia đôi (công khai ở Toà quản lý, riêng ở Toà Owner).
- Bot quản lý: cố định + bot thường được nâng quyền tạm. Được đọc trạng thái, giao việc, bật/tắt/khởi động lại; **không** sửa memory bot khác, **không** tạo/xoá bot.
- Hàng rào: lọc 2 chiều, có cả code kiểm tra, vi phạm thì chặn + báo lỗi; token limit tính toàn hệ thống/tháng.
- Plugin vẽ/docx/code chuyển sang **Toà văn phòng** (mới) ở Khu đại sảnh. Log/session/Zalo... giữ ở Cổng chính nhưng chia nhiều căn hộ.
- **Toà khách** (mới) ở Khu cổng: mỗi người một căn hộ gọi là **túp lều** (repo, kết nối, dữ liệu riêng của người đó). Khẩn cấp được đi tắt nhưng ghi log song song vào Đại sảnh.
- Đại sảnh: bus nội bộ, chỉ đọc "phong bì". Thư viện/Bản đồ: mọi bot đọc, chỉ quản lý/owner ghi. Bot ↔ bot cùng khu dân cư không cần qua Đại sảnh.
- Căn hộ bot có: workspace, memory (3 loại), persona, và **kệ sách** (lấy từ Thư viện). Chỉ owner được vào căn hộ bot.
- Mặc định MỞ trong nội thành. Chỉ tài liệu, chưa tự kiểm. Làm tài liệu/bản đồ trước, Đại sảnh làm đầu tiên.
- Thêm toà khi cần thì được; **thêm khu phải hỏi owner**.

---

## PHẦN A — Chỗ vòng 1 chưa khớp nhau

**A1. Cron / khởi động / tắt: vòng 1 bạn chọn hai thứ khó khớp nhau.**
Câu 20 chọn "Toà điều phối = lõi chạy cron/khởi động", nhưng câu 21 chọn gom cron/khởi động/tắt về **Cổng phụ**. Chốt lại:
- [ ] A. Tất cả (cấu hình + bộ chạy cron + lệnh khởi động/tắt) nằm ở Cổng phụ; Toà điều phối làm việc khác (trả lời ở A2)
- [ ] B. Cổng phụ chỉ **nhận lệnh** từ ngoài (owner, VPS, MCP), rồi giao Toà điều phối **thi hành** (bộ lập lịch, start/stop)
- [ ] C. Cổng phụ giữ cấu hình + lịch; Toà điều phối giữ bộ chạy
- Khác: ______

**A2. Toà điều phối còn chứa gì chắc chắn?** (chọn nhiều)
- [ ] A. Bus/bộ định tuyến tin nhắn giữa các khu
- [ ] B. Đồng hồ chung (giờ Việt Nam, đồng bộ thời gian)
- [ ] C. Sổ đăng ký bot (bot nào đang sống/ngủ, ở căn hộ nào)
- [ ] D. Hàng đợi việc và log phong bì
- [ ] E. Bộ khởi động/tắt (nếu A1 chọn B hoặc C)
- Khác: ______

**A3. Toà Owner chỉ cấm bằng lời dặn (câu 6), nhưng bạn lại lo "bot truy cập nhầm chỗ cấm" (câu 44).** Mức cấm bạn muốn:
- [ ] A. Giữ nguyên: chỉ lời dặn trong prompt
- [ ] B. Lời dặn + lọc đường dẫn ở lớp công cụ file (bot gọi đọc/ghi vào Toà Owner hoặc nhà bot khác sẽ bị code từ chối)
- [ ] C. B + sau này tách user hệ điều hành cho từng bot
- Khác: ______

**A4. Bot quản lý không vào được căn hộ bot khác (câu 31), mà phải chấm điểm bot hàng tuần (để chỉnh trí nhớ cơ bắp). Nó lấy dữ liệu chấm từ đâu?**
- [ ] A. Bot tự nộp báo cáo định kỳ (qua Đại sảnh)
- [ ] B. Đọc log (phong bì + kết quả công việc, phản hồi của người dùng)
- [ ] C. Mỗi căn hộ có một thư mục "cửa sổ" (vd `public/`) cho bot quản lý đọc, phần còn lại khoá
- [ ] D. A + C
- Khác: ______

**A5. Bot ↔ bot cùng Khu dân cư không qua Đại sảnh (câu 26). Vậy kênh nhắn của họ là gì?**
- [ ] A. Gọi hàm trực tiếp trong cùng chương trình
- [ ] B. Hộp thư (file) đặt trong Toà nhà dân, ngoài căn hộ
- [ ] C. Vẫn dùng bus nhưng đi "đường tắt" không ghi log
- [ ] D. Chưa cần, đến khi có ≥2 bot sẽ tính
- Khác: ______

**A6. Token limit toàn hệ thống/tháng (câu 15) — khi gần chạm hoặc đã chạm thì?**
- [ ] A. Cảnh báo owner ở 80% và 100%; chạm 100% thì dừng mọi bot trừ lệnh owner + khẩn cấp
- [ ] B. Chạm 100% chỉ dừng bot thường, bot quản lý vẫn chạy
- [ ] C. Tự chuyển sang model rẻ hơn
- Khác: ______

**A7. Có giới hạn chống spam theo từng người dùng (vd tin/phút) không?** (câu 15 chỉ chọn mức toàn hệ thống)
- [ ] A. Có, tin/phút theo người, nằm ở Hàng rào
- [ ] B. Không, chỉ dựa token toàn hệ thống
- [ ] C. Có, nhưng chỉ cho người lạ (chưa có túp lều)
- Khác: ______

---

## PHẦN B — Đặt tên tiếng Anh

**B1. Phong cách đặt tên?** (nhớ nỗi đau: "tìm file mà không biết nó ở đâu")
- [ ] A. Giữ ẩn dụ thành phố (`lobby`, `gate`, `residential`, `hut`…) — đẹp, nhất quán với tài liệu
- [ ] B. Tên chức năng thẳng (`hub`, `edge`, `agents`, `user-space`…) — nhìn là đoán được chứa gì
- [ ] C. Khu dùng ẩn dụ, toà/căn hộ dùng tên chức năng
- Khác: ______

**B2. Kiểu viết tên thư mục?** (Python chỉ `import` được thư mục dạng snake_case)
- [ ] A. snake_case toàn bộ (`main_gate`), code import thẳng được
- [ ] B. kebab-case cho tài liệu/dữ liệu, snake_case cho thư mục chứa code
- [ ] C. kebab-case hết (`main-gate`), code không import theo đường dẫn thư mục
- Khác: ______

**B3. Bảng tên đề xuất (theo B1-A, B2-C). Bạn đồng ý?**

| Việt | Đề xuất |
|---|---|
| Thành chính | `PyloS/` |
| Khu quản lý / Toà Owner / Toà quản lý | `management/` · `owner/` · `managers/` |
| Khu cổng / Cổng chính / Hàng rào / Cổng phụ / **Toà khách** | `gate/` · `main-gate/` · `fence/` · `side-gate/` · `guest-house/` |
| Khu đại sảnh / Thư viện / Bản đồ / Điều phối / **Văn phòng** | `lobby/` · `library/` · `atlas/` · `dispatch/` · `office/` |
| Khu dân cư / Toà nhà dân | `residential/` · `residents/` |
| Túp lều / Kệ sách | `hut/` · `bookshelf/` |
| Trí nhớ cơ bắp / ngắn hạn / dài hạn / "mơ" | `memory/muscle/` · `memory/short-term/` · `memory/long-term/` · `dream` |

- [ ] A. Đồng ý toàn bộ
- [ ] B. Đồng ý trừ chỗ ghi ở **Khác**
- Khác: ______

---

## PHẦN C — Toà khách, túp lều, Toà văn phòng

**C1. Bạn nói "toà khách trong khu cổng chính" (câu 18) rồi "Khu khách" (câu 33). Toà khách thuộc đâu?**
- [ ] A. Toà thứ 4 của Khu cổng (Khu cổng: Cổng chính, Hàng rào, Cổng phụ, Toà khách)
- [ ] B. Một **khu mới** (nhớ: thêm khu phải hỏi owner — đây là hỏi)
- [ ] C. Chỉ là căn hộ trong Cổng chính
- Khác: ______

**C2. Một túp lều chứa gì?** (chọn nhiều)
- [ ] A. Mã nguồn repo người đó yêu cầu
- [ ] B. Thông tin kết nối GitHub (URL, token, nhánh)
- [ ] C. Lịch/việc riêng của người đó
- [ ] D. Hồ sơ/sở thích do bot ghi nhận
- [ ] E. File người đó gửi hoặc bot tạo cho người đó
- [ ] F. Lịch sử chat/session (hiện đang đặt ở Cổng chính theo câu 16 — có chuyển sang đây không?)
- Khác: ______

**C3. Túp lều sinh ra khi nào?**
- [ ] A. Tự động ngay lần người đó nhắn đầu tiên
- [ ] B. Chỉ khi owner duyệt/thêm người đó vào danh sách
- [ ] C. Tự tạo, nhưng người lạ chưa duyệt chỉ có túp lều "tạm" bị giới hạn
- Khác: ______

**C4. Ai được vào túp lều của người X?** (chọn nhiều)
- [ ] A. Owner
- [ ] B. Bot đang xử lý tin của chính X (chỉ trong lúc đó)
- [ ] C. Bot khác xin qua Đại sảnh, có X đồng ý/cấu hình cho phép (khớp câu 34-B)
- [ ] D. Bot quản lý
- Khác: ______

**C5. Nhóm Zalo (nhiều người) có túp lều không?**
- [ ] A. Mỗi nhóm một túp lều riêng, tách với túp lều từng người
- [ ] B. Nhóm không có túp lều, chỉ lưu theo từng người trong nhóm
- [ ] C. Bot hiện chưa hỗ trợ nhóm / chưa cần quyết
- Khác: ______

**C6. Plugin ở Toà văn phòng tạo ra file (ảnh, docx…). File đó nằm ở đâu trước khi gửi ra Zalo?**
- [ ] A. Trong túp lều của người yêu cầu
- [ ] B. Workspace của bot đã gọi plugin
- [ ] C. Thư mục tạm của Toà văn phòng, tự xoá sau N ngày
- Khác: ______

**C7. Ai được thêm/sửa plugin trong Toà văn phòng?**
- [ ] A. Chỉ owner
- [ ] B. Bot đề xuất, owner duyệt
- [ ] C. Bot quản lý được thêm
- Khác: ______

---

## PHẦN D — Căn hộ (Tầng 3) trong từng toà

**D1. Cổng chính — các căn hộ?** (chọn nhiều; câu 16 bạn muốn chia nhiều căn hộ)
- [ ] A. `zalo` (kết nối Zalo cá nhân / Bot Platform / QR)
- [ ] B. `external-apps` (app, API bên thứ ba)
- [ ] C. `external-bots` (bot ngoại thành)
- [ ] D. `external-folders` (thư mục/máy ngoài)
- [ ] E. `sessions`
- [ ] F. `logs`
- Khác: ______

**D2. Hàng rào — căn hộ chia theo gì?**
- [ ] A. Theo loại giới hạn: `token-limit`, `speech-limit`, `ethics`
- [ ] B. Theo chiều: `inbound`, `outbound`
- [ ] C. Một căn hộ duy nhất, chia file bên trong
- Khác: ______

**D3. Cổng phụ — các căn hộ?** (chọn nhiều)
- [ ] A. `vps`
- [ ] B. `cron` (nếu A1 chọn A hoặc C)
- [ ] C. `mcp`
- [ ] D. `owner-commands`
- [ ] E. `shell` (lệnh cmd)
- [ ] F. `emergency`
- Khác: ______

**D4. Toà quản lý — các căn hộ (chủ đề)?** (chọn nhiều)
- [ ] A. `guidelines` (nguyên tắc cho bot quản lý)
- [ ] B. `bot-commands` (lệnh quản lý bot)
- [ ] C. `plans` (kế hoạch công khai)
- [ ] D. `evaluations` (chấm điểm bot hàng tuần)
- [ ] E. `reports`
- Khác: ______

**D5. Câu 7 bạn **không** chọn: danh sách/cấu hình bot, khoá bí mật/token, quyền hạn. Vậy 3 thứ đó nằm ở đâu?**

*Khoá bí mật / token:*
- [ ] A. Căn hộ tương ứng ở Cổng chính (mỗi dịch vụ giữ khoá của nó)
- [ ] B. Toà Owner
- [ ] C. File `.env` nằm ngoài cây thư mục, không commit
- Khác: ______

*Quyền hạn từng bot / từng người (vai trò):*
- [ ] D. Hàng rào
- [ ] E. Toà quản lý
- [ ] F. Toà điều phối
- [ ] G. Toà Owner
- Khác: ______

*Danh sách bot + bật/tắt:*
- [ ] H. Sổ đăng ký ở Toà điều phối, owner/quản lý bật tắt qua lệnh
- [ ] I. Toà quản lý
- [ ] J. Mỗi căn hộ bot tự có cờ bật/tắt
- Khác: ______

---

## PHẦN E — Hệ trí nhớ của bot

**E1. Kệ sách và trí nhớ cơ bắp khác nhau thế nào?**
- [ ] A. Kệ sách = tài liệu gốc chép từ Thư viện; cơ bắp = kỹ năng đã rút ra/luyện từ tài liệu đó
- [ ] B. Skill lấy từ Thư viện vào thẳng cơ bắp; kệ sách chỉ chứa tài liệu tham khảo
- [ ] C. Gộp làm một
- Khác: ______

**E2. Trí nhớ ngắn hạn sống bao lâu nếu "mơ" chưa kịp xử lý?**
- [ ] A. 24 giờ
- [ ] B. 7 ngày
- [ ] C. Đến lần "mơ" kế tiếp, không giới hạn thời gian
- Khác: ______

**E3. Chức năng "mơ" (cấu trúc lại ngắn hạn → dài hạn) chạy khi nào?** (chọn nhiều)
- [ ] A. Mỗi đêm vào giờ vắng (do cron)
- [ ] B. Khi bot rảnh (khớp câu 35)
- [ ] C. Khi ngắn hạn đầy ngưỡng
- Khác: ______

**E4. "Mơ" do ai làm?**
- [ ] A. Chính bot, gọi LLM để tóm tắt/cấu trúc lại (tốn token — tính vào hạn mức A6)
- [ ] B. Script theo luật (đếm, gộp trùng), không dùng LLM
- [ ] C. Script lọc sơ + LLM chỉ xử lý phần còn lại
- Khác: ______

**E5. Điều gì đủ để một mục từ ngắn hạn lên dài hạn?** (bạn nói "gặp nhiều lần")
- [ ] A. Gặp ≥ N lần (N = ____)
- [ ] B. Bot tự chấm mức quan trọng
- [ ] C. Bot quản lý duyệt
- [ ] D. A hoặc B, không cần quản lý
- Khác: ______

**E6. Trí nhớ dài hạn có "quên" không?**
- [ ] A. Không xoá, chỉ gộp/nén lại
- [ ] B. Xoá mục lâu không dùng (N tháng)
- [ ] C. Đưa vào kho lưu trữ, không xoá
- Khác: ______

**E7. Chỉnh trí nhớ cơ bắp hàng tuần: quy trình và dựa trên gì?**
Quy trình:
- [ ] A. Bot tự sửa; quản lý chấm; điểm giảm thì tự hoàn về bản cũ (có lưu phiên bản)
- [ ] B. Bot đề xuất, quản lý duyệt từng thay đổi
- [ ] C. Bot đề xuất, owner duyệt
- Khác: ______

Điểm chấm dựa trên (chọn nhiều):
- [ ] D. Phản hồi/phàn nàn của người dùng
- [ ] E. Tỷ lệ lỗi khi dùng công cụ
- [ ] F. Chi phí token
- [ ] G. Quản lý đọc mẫu hội thoại
- Khác: ______

**E8. Quan trọng — chống rò dữ liệu riêng (câu 44-E).** Khi bot trích xuất từ chat ("Nam thích cà phê") thì ghi ở đâu?
- [ ] A. Chỉ ghi vào túp lều của Nam; trí nhớ của bot không chứa thông tin gắn với từng người
- [ ] B. Được ghi vào trí nhớ bot, nhưng gắn nhãn chủ nhân và chỉ dùng khi phục vụ đúng người đó
- [ ] C. Ghi tự do vào trí nhớ bot
- Khác: ______

**E9. Persona/cấu hình của bot (câu 32-C) — bot có tự sửa được không?**
- [ ] A. Không, chỉ owner sửa
- [ ] B. Bot đề xuất, owner duyệt
- [ ] C. Tự sửa trong một số mục cho phép (giọng văn, thói quen), không sửa quy tắc
- Khác: ______

---

## PHẦN F — Thư viện và kệ sách

**F1. Bot lấy tài liệu từ Thư viện về kệ sách theo cách nào?**
- [ ] A. Tự chọn khi thấy cần
- [ ] B. Bot quản lý phân phối
- [ ] C. Owner chỉ định
- [ ] D. A nhưng có giới hạn dung lượng/số lượng kệ
- Khác: ______

**F2. Kệ sách là bản sao hay liên kết?**
- [ ] A. Bản sao riêng (bot được ghi chú thêm)
- [ ] B. Liên kết/tham chiếu, luôn là bản mới nhất
- [ ] C. Bản sao có ghi phiên bản, tự cảnh báo khi Thư viện có bản mới
- Khác: ______

**F3. Tài liệu/skill lấy từ nguồn ngoài vào Thư viện — ai kiểm trước? (skill ngoài có thể chứa chỉ dẫn độc hại)**
- [ ] A. Owner tự đọc trước khi cho vào
- [ ] B. Quét tự động + owner duyệt
- [ ] C. Bot quản lý kiểm, owner duyệt phần có code chạy được
- Khác: ______

**F4. Skill (Thư viện) khác plugin (Toà văn phòng) thế nào?**
- [ ] A. Skill = hướng dẫn bằng văn bản bot đọc; plugin = code chạy được
- [ ] B. Skill có thể kèm script; plugin là công cụ độc lập
- [ ] C. Chưa phân biệt, tách sau
- Khác: ______

---

## PHẦN G — Quyền, khẩn cấp, mở rộng

**G1. Lệnh owner qua Zalo — xác thực thế nào?**
- [ ] A. Chỉ cần đúng tài khoản Zalo của owner
- [ ] B. A + mã phụ cho lệnh nguy hiểm (tắt hệ thống, xoá…)
- [ ] C. A + xác nhận qua trang quản trị web
- Khác: ______

**G2. Đường khẩn cấp (đi tắt Đại sảnh) có qua Hàng rào không?**
- [ ] A. Không — lệnh owner chỉ bị chặn bởi xác thực
- [ ] B. Có, chỉ kiểm đầu vào
- Khác: ______

**G3. Nâng quyền tạm cho bot thường (câu 8-C):** (chọn nhiều)
- [ ] A. Owner cấp
- [ ] B. Bot quản lý cấp
- [ ] C. Hết hạn tự động sau khoảng thời gian
- [ ] D. Gắn với một nhiệm vụ, xong là thu hồi
- Khác: ______

**G4. Ai được tạo toà mới (câu 41: toà được thêm khi cần, khu phải hỏi owner)?**
- [ ] A. Người/Claude Code sửa repo tự tạo, ghi vào Bản đồ và báo owner
- [ ] B. Bot quản lý đề xuất, owner duyệt
- [ ] C. Chỉ owner
- Khác: ______

---

## PHẦN H — Hiện trạng code và cách làm việc

Hiện repo là **một bot** (`src/bot/`, agent Gemini, Zalo, trang quản trị web, ứng dụng desktop, bộ cập nhật, VPS). Các câu dưới đây nối cấu trúc mới với code đang có.

**H1. Số bot dự kiến?**
- [ ] A. Vẫn 1 bot; cấu trúc chỉ chừa sẵn chỗ cho nhiều bot
- [ ] B. Sắp có 2–3 bot
- [ ] C. Nhiều (≥5)
- Khác: ______

**H2. Các bot chạy thế nào?**
- [ ] A. Một chương trình, mỗi bot là một module
- [ ] B. Mỗi bot một process riêng
- [ ] C. Chưa quyết, mình đề xuất sau
- Khác: ______

**H3. Gán code hiện có vào toà mới (đề xuất). Đồng ý?**

| Code hiện có | Toà đề xuất |
|---|---|
| `zalo/*` (nhận/gửi Zalo, QR, polling, webhook) | `gate/main-gate` |
| `core/message_filter.py`, `rate_limiter.py`, `text_fold.py` | `gate/fence` |
| `core/owner_commands.py`, `system/remote_server.py`, `server_client.py`, `bot_process.py` | `gate/side-gate` |
| `system/auto_update.py`, `handover*.py`, `core/vietnam_time.py`, `storage/process_lock.py` | `lobby/dispatch` |
| `agent/*` (gemini_agent, system_prompt) | `residential/residents/<bot>` |
| `agent/tools/*` (assign_events, schedule_web…) | `lobby/office` |
| `templates/MEMORY.md`, `SYSTEM.md`, `workspace/` | `residential/residents/<bot>` |
| `userdata/` (dữ liệu người dùng) | `gate/guest-house/<hut>` |
| `docs/` (kế hoạch, hướng dẫn) | `management/managers` + `lobby/library` |

- [ ] A. Đồng ý toàn bộ
- [ ] B. Đồng ý trừ dòng ghi ở **Khác**
- Khác: ______

**H4. Hai thứ chưa có chỗ rõ: trang quản trị web (`ui/admin`) và ứng dụng desktop (`ui/desktop`). Đặt ở đâu?**
- [ ] A. Trang quản trị → `management/owner` (là công cụ của owner); desktop → `gate/side-gate`
- [ ] B. Cả hai → `gate/side-gate` (cửa kỹ thuật cho owner)
- [ ] C. Cả hai → một toà mới trong Khu quản lý
- Khác: ______

**H5. Trong 3 nỗi đau bạn kể, cái nào cấu trúc này phải giải quyết **trước**?**
- [ ] A. Tìm file dễ (đặt tên + Bản đồ)
- [ ] B. Thêm tính năng mà không phải sửa lan nhiều nơi (ranh giới rõ giữa các toà)
- [ ] C. Giảm bug lan (mỗi khu/toà có test riêng)
- Khác: ______

**H6. Để mỗi lần Claude thêm tính năng không phải mò lại từ đầu, có nên viết một file luật gắn vào repo (Claude luôn đọc: "file mới đặt ở toà nào, phải cập nhật Bản đồ, muốn thêm khu thì hỏi owner")?**
- [ ] A. Có, và đặt ngay trong giai đoạn "chỉ làm tài liệu" (câu 42-A)
- [ ] B. Có, nhưng sau khi đã đổi thư mục thật
- [ ] C. Không
- Khác: ______

---

## Câu hỏi mở

1. Bot/đầu việc thật nào hiện đang chạy mà bạn sợ bị gián đoạn nhất khi đổi cấu trúc (câu 44-A)? ______
2. "Bot quản lý cố định" — dự định bao nhiêu bot, mỗi bot phụ trách gì (vd một bot chấm điểm, một bot giám sát)? ______
3. Có điều gì trong vòng 1 bạn đã chọn nhưng giờ muốn đổi? ______
