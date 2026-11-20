"""Đọc/ghi file .env cho trang Cài đặt.

- Giữ nguyên chú thích và thứ tự dòng; chỉ thay dòng KEY=... cần đổi (hoặc thêm vào cuối).
- Lưu bản cũ vào .env.bak trước khi ghi, ghi nguyên tử.
- Chỉ cho sửa các khóa trong danh sách cho phép; khóa bí mật chỉ được ghi, không bao giờ đọc ra.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

from pylos.lobby.dispatch.shared.config import ConfigError, Settings
from pylos.lobby.dispatch.shared.storage import atomic_write_text


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    help: str = ""
    kind: str = "text"  # text | int | bool | choice
    choices: tuple[str, ...] = field(default_factory=tuple)
    group: str = "Chung"


FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec("OWNER_ZALO_ID", "ID Zalo của chủ bot", "Người được dùng /mode, /allow... Xem bằng lệnh /id."),
    FieldSpec("ALLOW_ALL_CHATS", "Cho phép mọi cuộc trò chuyện",
              "Bật: bot trả lời ở mọi nhóm và chat riêng, không cần /allow (chat bị /deny vẫn bị chặn). "
              "Tắt: chỉ các chat đã /allow.", kind="bool"),
    FieldSpec("BOT_TRIGGERS", "Từ gọi bot", "Tin trong nhóm bắt đầu bằng một trong các từ này thì bot trả lời (cách nhau dấu phẩy)."),
    FieldSpec("BOT_NAMES", "Tên gọi bot",
              "Tin trong nhóm có nhắc tới một trong các tên này (hoặc @tag acc bot) thì bot trả lời, "
              "không cần /bot. Tên acc Zalo của bot được tự thêm. Cách nhau dấu phẩy; để trống để tắt."),
    FieldSpec("FILTER_AI", "Bộ lọc AI",
              "Bật: ở nhóm chế độ all (/mode all), tin không gọi tên bot được Gemini xét xem có đang nhờ bot không. "
              "Nhóm chế độ default luôn chỉ trả lời khi được gọi. Tắt: mọi nhóm chỉ trả lời khi có /bot, @tag hoặc gọi tên.",
              kind="bool", group="Bộ lọc & memorydata"),
    FieldSpec("FILTER_MODEL", "Model cho bộ lọc", "Nên dùng model rẻ, nhanh. Để trống = GEMINI_MODEL.",
              group="Bộ lọc & memorydata"),
    FieldSpec("FILTER_CONTEXT_LINES", "Số tin gần nhất đưa cho bộ lọc",
              "Giúp bộ lọc hiểu câu hỏi tiếp nối. 0 = chỉ xét tin mới.", kind="int", group="Bộ lọc & memorydata"),
    FieldSpec("MEMORYDATA_KEEP", "Số tin giữ lại mỗi hội thoại",
              "Tối đa số dòng trong mỗi file data/memorydata/<chat>.txt. 0 = không giới hạn.",
              kind="int", group="Bộ lọc & memorydata"),
    FieldSpec("MEDIA_INPUT", "Cho bot xem ảnh, video, nghe tin thoại",
              "Bật: chat riêng gửi ảnh/video/tin thoại thì Gemini xem hoặc nghe và trả lời; trong nhóm chỉ khi gọi bot (chú thích có /bot, @tag, tên bot) hoặc vừa gọi bot trong 2 phút. Tốn token hơn tin chữ.",
              kind="bool", group="Ảnh, video & web"),
    FieldSpec("MEDIA_MAX_MB_PHOTO", "Ảnh tối đa (MB)",
              "Lớn hơn thì bot báo file quá lớn.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("MEDIA_MAX_MB_AUDIO", "Tin thoại tối đa (MB)",
              "Lớn hơn thì bot báo file quá lớn.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("MEDIA_MAX_MB_VIDEO", "Video tối đa (MB)",
              "Video luôn được tải lên Files API của Gemini; lớn hơn mức này thì bot báo file quá lớn.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("MEDIA_INLINE_MAX_MB", "Mức nhúng thẳng (MB)",
              "Ảnh/tin thoại nhỏ hơn mức này (tổng mỗi lượt) gửi thẳng trong request; lớn hơn thì tải lên Files API.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("MEDIA_UPLOAD_TIMEOUT", "Chờ Files API xử lý (giây)",
              "Quá thời gian này thì lượt trả lời lỗi.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("MEDIA_KEEP_HOURS", "Giữ tệp (giờ)",
              "Tệp người dùng gửi lưu trong túp lều, tự xoá sau từng này giờ.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("MEDIA_FOLLOWUP_TURNS", "Hỏi tiếp về tệp: số lượt",
              "Bot xem lại tệp trong N lượt gần nhất của người dùng. 0 = chỉ lượt gửi tệp.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("MEDIA_FOLLOWUP_MINUTES", "Hỏi tiếp về tệp: số phút",
              "Và chỉ khi tệp được gửi chưa quá từng này phút.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("USER_MEDIA_PER_HOUR", "Số tệp tối đa mỗi người mỗi giờ",
              "Vượt thì bot im lặng bỏ qua tệp. 0 = không giới hạn.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("WEB_TOOLS", "Cho bot đọc link",
              "Bật: bot đọc nội dung trang web từ link người dùng gửi (tool doc_trang_web). Link tới máy nội bộ luôn bị chặn.",
              kind="bool", group="Ảnh, video & web"),
    FieldSpec("WEB_SEARCH", "Cho bot tìm trên web",
              "Bật: bot tìm Google qua Gemini khi cần thông tin mới (tool tim_web). Cần WEB_TOOLS bật.",
              kind="bool", group="Ảnh, video & web"),
    FieldSpec("WEB_SEARCH_PROVIDER", "Nguồn tìm web",
              "auto: Google Search của Gemini, lỗi/hết hạn mức thì Tavily rồi Brave (nguồn nào có khoá). "
              "gemini / tavily / brave: chỉ dùng nguồn đó. API key Gemini miễn phí thường KHÔNG có hạn mức Google Search; "
              "Tavily miễn phí khoảng 1.000 lượt/tháng (tavily.com).",
              kind="choice", choices=("auto", "gemini", "tavily", "brave"), group="Ảnh, video & web"),
    FieldSpec("WEB_CONTACT", "Liên hệ khi đọc trang",
              "URL hoặc email của chủ bot, gửi kèm khi bot đọc trang web. Wikipedia và vài trang khác chặn bot không có thông tin này. "
              "Để trống nếu không muốn gửi.",
              group="Ảnh, video & web"),
    FieldSpec("WEB_SEARCH_PER_DAY", "Số lượt tìm web mỗi ngày",
              "Hết lượt thì bot nói mai thử lại. 0 = không giới hạn. Google tính phí theo lượt sau hạn mức miễn phí.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("WEB_MAX_CHARS", "Số ký tự tối đa đọc từ một trang",
              "Phần dài hơn bị cắt (đưa vào Gemini nên tốn token).",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("WEB_FETCH_TIMEOUT", "Chờ tải trang (giây)",
              "Trang phản hồi chậm hơn thì bỏ.",
              kind="int", group="Ảnh, video & web"),
    FieldSpec("GEMINI_MODEL", "Model Gemini", "Ví dụ gemini-3.1-flash-lite.", group="Gemini"),
    FieldSpec("MAX_OUTPUT_TOKENS", "Token tối đa mỗi câu trả lời", kind="int", group="Gemini"),
    FieldSpec("LLM_TIMEOUT_SECONDS", "Thời gian chờ Gemini (giây)", kind="int", group="Gemini"),
    FieldSpec("THINKING_LEVEL", "Mức suy nghĩ của Gemini",
              "low (thấp): nhanh, rẻ, ít hết giờ. medium (vừa): cân bằng. high (cao): kỹ nhất nhưng chậm, tốn token. "
              "Model không hỗ trợ thì tự bỏ qua.",
              kind="choice", choices=("low", "medium", "high"), group="Gemini"),
    FieldSpec("FALLBACK_MODELS", "Model dự phòng",
              "Cách nhau dấu phẩy, thử lần lượt khi model đang dùng quá tải (503), hết hạn mức (429), không tồn tại (404) "
              "hoặc hết giờ. Ví dụ gemini-3.5-flash-lite. Để trống = không dự phòng. Mỗi loại việc còn có danh sách "
              "dự phòng riêng trong modelShift.md (căn hộ bot lọc).", group="Gemini"),
    FieldSpec("MODEL_SHIFT", "Bot lọc được đổi model theo loại việc",
              "Bật: bot lọc phân loại tin (việc thường / triết lý, cảm nhận / code) và đổi model + mức suy nghĩ theo bảng hồ sơ "
              "trong modelShift.md; chat giữ model đó cho tới lần đổi sau. Trong chat dùng /model fixed để khóa riêng chat đó. "
              "Tắt: luôn dùng model và mức suy nghĩ chung ở trên.", kind="bool", group="Gemini"),
    FieldSpec("HISTORY_TURNS", "Số lượt hội thoại đưa vào prompt", kind="int", group="Gemini"),
    FieldSpec("REPLY_SPLIT", "Tách câu trả lời nhiều dòng",
              "line: mỗi dòng một tin. paragraph: mỗi đoạn một tin. off: gửi một tin.",
              kind="choice", choices=("line", "paragraph", "off"), group="Gemini"),
    FieldSpec("REPLY_MAX_PARTS", "Số tin tối đa mỗi câu trả lời", "Nhiều dòng hơn thì gộp lại.", kind="int", group="Gemini"),
    FieldSpec("REPLY_PART_DELAY_MS", "Nghỉ giữa các tin (mili giây)", "0 = không nghỉ.", kind="int", group="Gemini"),
    FieldSpec("MAX_TOOL_ROUNDS", "Số vòng gọi tool tối đa", kind="int", group="Gemini"),
    FieldSpec("DAILY_TOKEN_BUDGET", "Hạn mức token mỗi ngày", "0 = không giới hạn.", kind="int", group="Giới hạn"),
    FieldSpec("USER_RATE_PER_MIN", "Số tin mỗi phút / người", "0 = không giới hạn.", kind="int", group="Giới hạn"),
    FieldSpec("CHAT_RATE_PER_MIN", "Số tin mỗi phút / nhóm", "0 = không giới hạn.", kind="int", group="Giới hạn"),
    FieldSpec("RECEIVE_MODE", "Cách nhận tin",
              "polling: không cần domain. webhook: cần URL HTTPS công khai. "
              "personal: chạy trên acc Zalo cá nhân (không chính thức, acc có thể bị khoá).",
              kind="choice", choices=("polling", "webhook", "personal"), group="Kết nối"),
    FieldSpec("WEBHOOK_HOST", "Webhook: địa chỉ lắng nghe", group="Kết nối"),
    FieldSpec("WEBHOOK_PORT", "Webhook: cổng", kind="int", group="Kết nối"),
    FieldSpec("SCHEDULE_API_URL", "Địa chỉ web bot lịch",
              "Ví dụ https://iforgotmywayhome.vercel.app. Chỉ dùng để giao lịch và liên kết Zalo (cần thêm khoá SCHEDULE_API_KEY bên dưới).",
              group="Bot lịch (giao lịch qua web)"),
    FieldSpec("SCHEDULE_OWNER_ONLY", "Chỉ chủ bot được thêm/xem lịch riêng",
              "Lịch riêng trên web (them_lich_hen, xem_lich...). Bật: chỉ OWNER_ZALO_ID. Tắt: ai nhắn bot cũng được.",
              kind="bool", group="Bot lịch (giao lịch qua web)"),
    FieldSpec("ASSIGN_ALLOWED", "Ai được giao lịch cho người khác",
              "owner: chỉ owner và các leader (đặt bằng /add leader trong từng nhóm) giao lịch cho người khác; basic-user chỉ thêm lịch cho chính mình. all: ai cũng giao được (coi mọi người là leader).",
              kind="choice", choices=("owner", "all"), group="Bot lịch (giao lịch qua web)"),
    FieldSpec("BOT_SUPERVISOR", "Ai bật/tắt bot",
              "process: ứng dụng tự bật tiến trình nền (máy Windows). systemd: dùng service pylos-bot (chỉ VPS Linux).",
              kind="choice", choices=("process", "systemd"), group="Kết nối"),
    FieldSpec("ADMIN_PUBLIC_URL", "Địa chỉ công khai của trang này",
              "Chỉ đặt trên VPS (trang quản lý chạy sau nginx), ví dụ https://unousgrowth.com. Để trống ở máy Windows.",
              group="Máy chủ VPS"),
    FieldSpec("REMOTE_URL", "Địa chỉ trang quản lý trên VPS",
              "Để trống = https://unousgrowth.com; off = không dùng VPS. Kết nối ở trang Máy chủ → Kết nối VPS bằng Gmail.",
              group="Máy chủ VPS"),
    FieldSpec("ADMIN_GOOGLE_CLIENT_ID", "Google Client ID của trang quản lý",
              "OAuth client riêng của PyloS (Google Cloud). Redirect URI: <địa chỉ trang quản lý>/api/auth/google/callback.",
              group="Đăng nhập"),
    FieldSpec("ADMIN_EMAIL", "Gmail của chủ hệ thống",
              "Đúng một Gmail được vào bằng Google. PyloS không phân quyền.", group="Đăng nhập"),
    FieldSpec("CLOUDFLARE_ACCOUNT_ID", "Cloudflare Account ID",
              "Dùng cho model Cloudflare Workers AI (ví dụ tạo ảnh). Lấy ở dash.cloudflare.com > Workers & Pages > Overview. "
              "Key nào dùng được model nào ghi ở model_keys.md (lobby/office/model_calls).", group="Cloudflare"),
    FieldSpec("IMAGE_GEN", "Cho bot tạo ảnh",
              "Bật: bot tạo ảnh khi được nhờ (tool tao_anh). Cần key Cloudflare và model nhiệm vụ image trong modelShift.md.",
              kind="bool", group="Tạo ảnh"),
    FieldSpec("IMAGE_STEPS", "Số bước tạo ảnh", "1-8. Nhiều bước hơn thì tốn hạn mức Cloudflare hơn.", kind="int", group="Tạo ảnh"),
    FieldSpec("IMAGE_PER_DAY", "Số ảnh tối đa mỗi ngày",
              "Hạn mức riêng cho ảnh, không tính vào hạn mức token. Hết thì bot nói mai thử lại. 0 = không giới hạn.",
              kind="int", group="Tạo ảnh"),
    FieldSpec("USER_IMAGES_PER_HOUR", "Số ảnh mỗi người mỗi giờ", "0 = không giới hạn.", kind="int", group="Tạo ảnh"),
    FieldSpec("DOC_TOOLS", "Cho bot làm việc với tài liệu",
              "Bật: bot đọc, tạo, sửa tệp .docx / .md / .txt (tool ds_tai_lieu, doc_tai_lieu, tao_tai_lieu, sua_tai_lieu) và nhận tệp người dùng gửi.",
              kind="bool", group="Tài liệu"),
    FieldSpec("DOCS_PER_DAY", "Số lần tạo / sửa tài liệu mỗi ngày", "Đọc không tính. 0 = không giới hạn.", kind="int", group="Tài liệu"),
    FieldSpec("USER_DOCS_PER_HOUR", "Số lần tạo / sửa mỗi người mỗi giờ", "0 = không giới hạn.", kind="int", group="Tài liệu"),
    FieldSpec("DOC_MAX_MB", "Cỡ tối đa tệp người dùng gửi (MB)", "Tệp lớn hơn bị từ chối.", kind="int", group="Tài liệu"),
    FieldSpec("DOC_KEEP_DAYS", "Giữ tệp bao nhiêu ngày", "Tệp không đụng tới quá số ngày này thì tự xoá. 0 = giữ mãi.", kind="int", group="Tài liệu"),
    FieldSpec("LOG_LEVEL", "Mức log", kind="choice", choices=("DEBUG", "INFO", "WARNING", "ERROR"), group="Kết nối"),
    FieldSpec("ADMIN_SHOW_HISTORY", "Hiện trang Hội thoại", kind="bool", group="Giao diện"),
)
FIELD_KEYS = {f.key for f in FIELDS}

SECRETS: dict[str, str] = {
    "ZALO_BOT_TOKEN": "Bot token Zalo",
    "GEMINI_API_KEY": "API key Gemini",
    "CLOUDFLARE_API_TOKEN": "API token Cloudflare (quyền Workers AI)",
    "WEBHOOK_SECRET": "Webhook secret (8–256 ký tự)",
    "SCHEDULE_API_KEY": "Khoá agent của web bot lịch (chỉ để giao lịch)",
    "TAVILY_API_KEY": "Khoá Tavily (tìm web miễn phí khoảng 1.000 lượt/tháng, lấy ở tavily.com)",
    "BRAVE_API_KEY": "Khoá Brave Search API (tìm web khi Gemini không có hạn mức Google Search)",
    "ADMIN_GOOGLE_CLIENT_SECRET": "Google Client secret của trang quản lý",
    "REMOTE_ADMIN_TOKEN": "Khoá kết nối VPS (tự đặt khi Kết nối VPS bằng Gmail; hoặc dán ADMIN_TOKEN của VPS)",
}

_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
# Ký tự làm sai cách python-dotenv đọc giá trị không có ngoặc, hoặc chèn thêm dòng.
_FORBIDDEN = re.compile(r"[\r\n\"'#\\\x00]")


def read_values(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return {k: (v or "") for k, v in dotenv_values(path).items()}


def clean_value(key: str, value: str) -> str:
    value = str(value).strip()
    if _FORBIDDEN.search(value):
        raise ConfigError(f"{key}: không được chứa xuống dòng, dấu nháy, # hoặc \\")
    if len(value) > 4096:
        raise ConfigError(f"{key}: quá dài")
    return value


def validate(path: Path, changes: dict[str, str], base_dir: Path) -> dict[str, str]:
    """Làm sạch và kiểm tra thay đổi bằng chính quy tắc của bot (Settings.from_env)."""
    cleaned = {key: clean_value(key, value) for key, value in changes.items()}
    for spec in FIELDS:
        if spec.key in cleaned and spec.kind == "choice" and cleaned[spec.key] and cleaned[spec.key] not in spec.choices:
            raise ConfigError(f"{spec.label}: phải là một trong {', '.join(spec.choices)}")
    if "WEBHOOK_SECRET" in cleaned and cleaned["WEBHOOK_SECRET"] and not 8 <= len(cleaned["WEBHOOK_SECRET"]) <= 256:
        raise ConfigError("WEBHOOK_SECRET phải dài 8–256 ký tự")
    Settings.from_env({**read_values(path), **cleaned}, base_dir=base_dir)  # ném ConfigError nếu sai
    return cleaned


def update(path: Path, changes: dict[str, str]) -> None:
    """Ghi các thay đổi đã kiểm tra vào .env, giữ chú thích, sao lưu bản cũ vào .env.bak."""
    old_text = path.read_text(encoding="utf-8") if path.is_file() else ""
    lines = old_text.splitlines()
    pending = dict(changes)
    for index, line in enumerate(lines):
        match = _LINE.match(line)
        if match and match.group(1) in pending:
            key = match.group(1)
            lines[index] = f"{key}={pending.pop(key)}"
    lines.extend(f"{key}={value}" for key, value in pending.items())
    if old_text:
        atomic_write_text(path.with_name(path.name + ".bak"), old_text)
    atomic_write_text(path, "\n".join(lines) + "\n")
