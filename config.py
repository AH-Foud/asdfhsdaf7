# -*- coding: utf-8 -*-
# تنظیمات ربات بله + وب سرور
# ⚠️ مقادیر BOT_TOKEN و ADMIN_ID از طریق پنل مدیریت (settings.json) تنظیم می‌شوند

import json, os

# مسیر فایل تنظیمات (از طریق پنل وب قابل ویرایش)
SETTINGS_FILE = "settings.json"

# مقادیر پیش‌فرض - پس از اولین اجرا از طریق پنل ست کنید
DEFAULT_BOT_TOKEN = ""
DEFAULT_ADMIN_ID = ""

# ===================== بارگذاری تنظیمات =====================

def load_settings():
    """بارگذاری تنظیمات از فایل settings.json"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_settings(data):
    """ذخیره تنظیمات در فایل settings.json"""
    current = load_settings()
    current.update(data)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    # ری‌لود متغیرهای ماژول
    reload_config()

_settings = load_settings()

# ===================== تنظیمات ربات =====================
BOT_TOKEN = _settings.get("bot_token", DEFAULT_BOT_TOKEN)
ADMIN_ID = _settings.get("admin_id", DEFAULT_ADMIN_ID)

# آدرس پایه API بله (سازگار با Telegram Bot API)
BASE_URL = ""  # بعد از لود BOT_TOKEN در reload_config ست می‌شود

def _build_base_url():
    global BASE_URL
    if BOT_TOKEN:
        BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"
    else:
        BASE_URL = ""

def reload_config():
    """ری‌لود تنظیمات از فایل (بعد از تغییر از طریق پنل)"""
    global BOT_TOKEN, ADMIN_ID, BASE_URL
    s = load_settings()
    BOT_TOKEN = s.get("bot_token", DEFAULT_BOT_TOKEN)
    ADMIN_ID = s.get("admin_id", DEFAULT_ADMIN_ID)
    _build_base_url()

_build_base_url()

# ===================== مسیر فایل‌های ذخیره‌سازی =====================
DATA_DIR = "data"
REQUESTS_FILE = f"{DATA_DIR}/requests.json"
STATES_FILE = f"{DATA_DIR}/states.json"
LOG_FILE = f"{DATA_DIR}/messages_log.json"
FORWARD_MAP_FILE = f"{DATA_DIR}/forward_map.json"
REGISTERED_FILE = f"{DATA_DIR}/registered_users.json"
SOPS_FILE = f"{DATA_DIR}/sops.json"

# ===================== تنظیمات وب سرور =====================
WEB_HOST = "0.0.0.0"   # گوش دادن روی همه اینترفیس‌ها (VPS-ready)
WEB_PORT = 5000

# ===================== همگام‌سازی با سایت =====================
SYNC_BASE_URL = ""
SYNC_API_KEY = ""

# ===================== هوش مصنوعی برای تطبیق SOP =====================
AI_BASE_URL = ""
AI_API_KEY = ""
AI_MODEL = "gpt-4o-mini"

# تنظیمات ویس (voice message)
VOICE_DIR = f"{DATA_DIR}/voices"

AI_PROMPT = (
    "تو یه دستیار هوشمندی. لیست SOPهای تعریف شده:\n{sops}\n\n"
    "پیام کاربر:\n{message}\n\n"
    "کدام SOP最适合 این سواله؟ فقط اسم دقیق SOP رو بنویس. "
    "اگر هیچکدوم مناسب نبود، بنویس: none"
)
