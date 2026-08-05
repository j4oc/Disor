"""
اختبارات Disor v2 — بتشتغل بدون توكن أو إنترنت (مفيش اتصالات حقيقية)
تشغيل: python -m pytest tests/ -v
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai import SKILL_SCHEMA, extract_json            # noqa: E402
from memory import Memory                            # noqa: E402
from skills import (                                 # noqa: E402
    SKILL_PERM_MAP, HANDLERS, pget, sanitize_perms, add_warning,
    remove_last_warning, list_warnings, guard,
)


# --------------------------------------------------------------------------
# المهارات
# --------------------------------------------------------------------------
def test_all_skills_in_schema():
    """كل مهارة في خريطة الصلاحيات لازم تكون معرفة في شارت الـ LLM."""
    missing = [s for s in SKILL_PERM_MAP if s not in SKILL_SCHEMA]
    assert not missing, f"مهارات مش في الـ schema: {missing}"
    assert len(SKILL_PERM_MAP) >= 120, f"مفروض 120+ مهارة، الموجود: {len(SKILL_PERM_MAP)}"


def test_all_skills_have_handler():
    """كل مهارة لازم ليها دالة تنفيذ في جدول التوزيع."""
    missing = [s for s in SKILL_PERM_MAP if s not in HANDLERS]
    assert not missing, f"مهارات من غير دالة تنفيذ: {missing}"
    assert len(HANDLERS) == len(SKILL_PERM_MAP)


def test_skill_prefix_uniqueness():
    """مفيش مهارة تكون prefix لمهارة تانية (عشان التوزيع يشتغل صح)."""
    names = sorted(SKILL_PERM_MAP)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            assert not b.startswith(a), f"تداخل في الأسماء: {a} ← {b}"


def test_all_skills_have_permission():
    """كل مهارة ليها صلاحية مطلوبة من الطالب."""
    for skill, perm in SKILL_PERM_MAP.items():
        assert isinstance(perm, str) and perm, f"{skill} من غير صلاحية"


def test_sanitize_perms_removes_administrator():
    clean = sanitize_perms({"administrator": True, "kick_members": True, "فايك": True, "add_reactions": "no"})
    assert "administrator" not in clean
    assert clean["kick_members"] is True
    assert "فايك" not in clean and "add_reactions" not in clean


def test_sanitize_perms_non_dict():
    assert sanitize_perms(None) == {}
    assert sanitize_perms("x") == {}


def test_pget_flexible_keys():
    assert pget({"category": "General"}, "Category", "category") == "General"
    assert pget({"Category": "General"}, "Category", "category") == "General"
    assert pget({}, "Category", "category", default="X") == "X"
    assert pget("not a dict", "k", default=5) == 5


# --------------------------------------------------------------------------
# JSON extraction
# --------------------------------------------------------------------------
def test_extract_json_with_fences():
    obj = extract_json('```json\n{"CreateChannel0": {"Name": "chat", "Type": "text", "Category": null}}\n```')
    assert obj["CreateChannel0"]["Name"] == "chat"


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_invalid():
    with pytest.raises(Exception):
        extract_json("no json here")


# --------------------------------------------------------------------------
# الذاكرة
# --------------------------------------------------------------------------
def test_memory_maxlen():
    mem = Memory(maxlen=3)
    for i in range(5):
        mem.add(1, "user", f"msg{i}")
    hist = mem.get(1)
    assert len(hist) == 3
    assert hist[0]["content"] == "msg2"


def test_memory_requests_context():
    mem = Memory(requests=3)
    mem.add_request(1, "اعمل روم اسمه chat")
    mem.add_request(1, "حطه في Generals")
    reqs = mem.get_requests(1)
    assert reqs == ["اعمل روم اسمه chat", "حطه في Generals"]


def test_memory_separate_users():
    mem = Memory()
    mem.add(1, "user", "أ")
    mem.add(2, "user", "ب")
    assert mem.get(1)[0]["content"] == "أ"
    assert mem.get(2)[0]["content"] == "ب"


# --------------------------------------------------------------------------
# نظام التحذيرات
# --------------------------------------------------------------------------
@pytest.fixture()
def warns_file(tmp_path, monkeypatch):
    import skills
    monkeypatch.setattr(skills, "WARN_FILE", str(tmp_path / "warnings.json"))
    monkeypatch.setattr(skills, "_warn_data", None)


def test_warnings_roundtrip(warns_file):
    add_warning(111, 222, "سبام", "أدمن")
    add_warning(111, 222, "إهانة", "أدمن")
    assert len(list_warnings(111, 222)) == 2
    removed = remove_last_warning(111, 222)
    assert removed["reason"] == "إهانة"
    assert len(list_warnings(111, 222)) == 1


def test_warnings_empty(warns_file):
    assert remove_last_warning(111, 999) is None
    assert list_warnings(111, 999) == []


# --------------------------------------------------------------------------
# حماية ترتيب الرتب (guard)
# --------------------------------------------------------------------------
class FakeRole:
    def __init__(self, pos):
        self.position = pos

    def __ge__(self, o):
        return self.position >= o.position

    def __gt__(self, o):
        return self.position > o.position


class FakeMember:
    def __init__(self, name, top=None):
        self.name = name
        self.top_role = top or FakeRole(0)
        self.mention = f"@{name}"


class FakeGuild:
    def __init__(self):
        self.owner = FakeMember("owner", FakeRole(10))
        self.me = FakeMember("bot", FakeRole(5))


def test_guard_blocks_owner_and_bot_and_above():
    g = FakeGuild()
    invoker = FakeMember("admin", FakeRole(4))
    assert guard(g.owner, invoker, g, "تطرد") is not None
    assert guard(g.me, invoker, g, "تطرد") is not None
    assert guard(FakeMember("x", FakeRole(6)), invoker, g, "تطرد") is not None


def test_guard_allows_below():
    g = FakeGuild()
    invoker = FakeMember("admin", FakeRole(4))
    assert guard(FakeMember("y", FakeRole(3)), invoker, g, "تطرد") is None


def test_guard_blocks_self():
    g = FakeGuild()
    invoker = FakeMember("admin", FakeRole(4))
    assert guard(invoker, invoker, g, "تطرد") is not None


# --------------------------------------------------------------------------
# الإعدادات
# --------------------------------------------------------------------------
def test_settings_no_token(tmp_path, monkeypatch):
    import settings as settings_mod
    settings_mod.DATA_FILE = str(tmp_path / "data.json")
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    c = settings_mod.load_config()
    assert c.token == ""
    assert c.api_key == ""


def test_settings_env_vars(tmp_path, monkeypatch):
    import settings as settings_mod
    settings_mod.DATA_FILE = str(tmp_path / "data.json")
    monkeypatch.setenv("DISCORD_TOKEN", "t123")
    monkeypatch.setenv("GROQ_API_KEY", "k456")
    c = settings_mod.load_config()
    assert c.token == "t123"
    assert c.api_key == "k456"
    assert c.admin_only is True
    assert c.web_port == 8080
