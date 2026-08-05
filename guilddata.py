"""
Disor v2 — إعدادات السيرفرات (ملف guild_settings.json)
بتخزن لكل سيرفر: قناة الترحيب + رسالة الترحيب + الرول التلقائي للأعضاء الجدد
"""
import json
import os

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guild_settings.json")
_data = None


def _load() -> dict:
    global _data
    if _data is None:
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            _data = {}
    return _data


def _save():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(_load(), f, ensure_ascii=False, indent=2)


def get(guild_id: int) -> dict:
    return _load().get(str(guild_id), {})


def set_welcome(guild_id: int, channel_id: int | None, text: str | None):
    g = _load().setdefault(str(guild_id), {})
    g["welcome_channel"] = channel_id
    g["welcome_text"] = text
    _save()


def set_autorole(guild_id: int, role_id: int | None):
    g = _load().setdefault(str(guild_id), {})
    g["autorole"] = role_id
    _save()
