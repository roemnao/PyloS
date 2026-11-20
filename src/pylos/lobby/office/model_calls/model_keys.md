<!-- Danh sách key -> model. KHÔNG ghi giá trị key ở đây (file này nằm trong git): chỉ ghi TÊN BIẾN trong settings.env. -->
<!-- Mỗi mục `## tên` là một key. Bắt buộc: provider, key, models. Trường khác (ví dụ account) cũng là tên biến. -->
<!-- Model không có trong danh sách nào thì dùng key Gemini chính (GEMINI_API_KEY). File tự nạp lại khi sửa. -->
# Model keys

## gemini-main
provider: gemini
key: GEMINI_API_KEY
models: gemini-3.1-flash-lite, gemini-3.5-flash-lite, gemini-4-hydrogen

## cloudflare-main
provider: cloudflare
key: CLOUDFLARE_API_TOKEN
account: CLOUDFLARE_ACCOUNT_ID
models: @cf/black-forest-labs/flux-1-schnell, @cf/leonardo/phoenix-1.0
