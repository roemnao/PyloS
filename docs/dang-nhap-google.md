# Đăng nhập trang quản lý PyloS bằng Google

PyloS không phân quyền: chỉ chủ hệ thống truy cập, bằng **một** Gmail. Không dùng web bot lịch.

## Tạo OAuth client (một lần, ~10 phút)

1. https://console.cloud.google.com → tạo **project mới** tên `PyloS Admin` (tách khỏi project của web bot lịch).
2. Google Auth Platform → **Branding**: App name `PyloS`, email hỗ trợ. **Audience**: External. Không thêm scope nào (chỉ dùng `openid email`, không cần Google xác minh). Để *Testing* thì thêm Gmail của bạn vào *Test users*, hoặc bấm **Publish app**.
3. **Clients → Create client → Web application**. *Authorized redirect URIs*:
   - `http://127.0.0.1:8081/api/auth/google/callback`
   - `http://localhost:8081/api/auth/google/callback`
   - `https://unousgrowth.com/api/auth/google/callback` (VPS, đúng `ADMIN_PUBLIC_URL`)
4. Chép Client ID và Client secret.

## Cấu hình `settings.env` (máy Windows và VPS)

```
ADMIN_GOOGLE_CLIENT_ID=xxxx.apps.googleusercontent.com
ADMIN_GOOGLE_CLIENT_SECRET=GOCSPX-xxxx
ADMIN_EMAIL=gmail.cua.ban@gmail.com
```

Có thể đặt trong trang Cài đặt (Client secret ở mục Khóa bí mật). Khởi động lại trang quản lý.

## Lỗi thường gặp

| Hiện tượng | Xử lý |
|---|---|
| `redirect_uri_mismatch` | Chép đúng URI Google báo vào *Authorized redirect URIs* (đúng cổng, `127.0.0.1` khác `localhost`, `https` trên VPS). Chờ ~5 phút. |
| `Access blocked` | Gmail chưa nằm trong *Test users*, hoặc Publish app. |
| Poll mãi `pending` | Trang quản lý khởi động lại giữa chừng (mã nằm trong bộ nhớ). Bấm đăng nhập lại. |
| `invalid_client` | Dán nhầm secret hoặc client của project khác. |
| Nút Google ẩn | Thiếu một trong ba biến, hoặc `ADMIN_EMAIL` có nhiều hơn một email. |
