"""
Disor v2 — إعدادات البوت
بيقرأ كل الإعدادات من ملف data.json (عشان محدش يعدل في الكود)
- التوكن والمفتاح بيترجّعوا من متغيرات البيئة الأول لو موجودة (مهم للاستضافة)
"""
import json
import os
from dataclasses import dataclass

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


@dataclass
class Config:
    token: str
    api_key: str
    model: str
    model_fast: str | None            # موديل سريع للراوتر (رد أسرع) — فاضي = نفس الرئيسي
    allowed_channels: list            # [] = يشتغل في أي قناة
    require_mention: bool             # يرد بس لما يتحط mention
    admin_only: bool                  # يرد بس على المشرفين — العضو العادي ممنوع
    allowed_role: str                 # رول إضافي يعامل كـ مشرف (id أو اسم)
    audit_channel: int | None         # قناة سجل العمليات
    max_history: int                  # عدد رسائل الذاكرة لكل مستخدم
    json_mode: bool                   # استخدام JSON mode من Groq للـ parser
    action_cooldown: float            # ثواني بين كل أمر واللي بعده
    rate_limit_per_min: int           # أقصى عدد رسائل يعالجها البوت لنفس المستخدم في الدقيقة
    prefix: str                       # بريفكس الأوامر النصية (زي !help)
    web_port: int                     # بورت سيرفر الويب (للإبقاء على الحياة على الاستضافة)


def _env_or_file(env_name: str, data: dict, json_key: str, default: str = "") -> str:
    """يجيب القيمة من متغيرات البيئة الأول، وبعدين من data.json."""
    return str(os.environ.get(env_name) or data.get(json_key) or default).strip()


def load_config() -> Config:
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    cfg = data.get("CONFIG", {}) or {}

    def num(key, default):
        try:
            return int(str(cfg.get(key, default)).strip() or default)
        except (TypeError, ValueError):
            return default

    def flt(key, default):
        try:
            return float(str(cfg.get(key, default)).strip() or default)
        except (TypeError, ValueError):
            return default

    def boolean(key, default):
        v = str(cfg.get(key, default)).strip().lower()
        if v in ("1", "true", "yes", "نعم", "صح"):
            return True
        if v in ("0", "false", "no", "لا", "غلط"):
            return False
        return bool(default)

    return Config(
        token=_env_or_file("DISCORD_TOKEN", data, "TOKEN"),
        api_key=_env_or_file("GROQ_API_KEY", data, "KEY"),
        model=str(cfg.get("MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")).strip(),
        model_fast=str(cfg.get("MODEL_FAST", "")).strip() or None,
        allowed_channels=[int(c) for c in (cfg.get("ALLOWED_CHANNELS") or []) if str(c).strip().isdigit()],
        require_mention=boolean("REQUIRE_MENTION", True),
        admin_only=boolean("ADMIN_ONLY", True),
        allowed_role=str(cfg.get("ALLOWED_ROLE", "")).strip(),
        audit_channel=num("AUDIT_CHANNEL", 0) or None,
        max_history=num("MAX_HISTORY", 12),
        json_mode=boolean("JSON_MODE", True),
        action_cooldown=flt("ACTION_COOLDOWN", 3),
        rate_limit_per_min=num("RATE_LIMIT_PER_MIN", 8),
        prefix=str(cfg.get("PREFIX", "!")).strip() or "!",
        web_port=num("WEB_PORT", 8080),
    )
