"""
Disor v2 — ذاكرة المحادثة
- بتخزن آخر رسائل كل مستخدم (سياق الشات)
- وسجل آخر طلبات المستخدم (سياق الـ Parser عشان يفهم الإشارات للرسائل السابقة)
"""
import time
from collections import deque


class Memory:
    def __init__(self, maxlen: int = 12, requests: int = 4, ttl: int = 1800):
        self.maxlen = maxlen          # أقصى عدد رسائل محفوظة لكل مستخدم
        self.requests = requests      # عدد طلبات المستخدم المحفوظة
        self.ttl = ttl                # انتهاء صلاحية الذاكرة بالثواني
        self._data: dict = {}         # user_id -> {"time": ts, "messages": deque, "requests": deque}
        self._last_cleanup = time.time()

    def _cleanup(self):
        now = time.time()
        if now - self._last_cleanup < 300:
            return
        self._last_cleanup = now
        expired = [uid for uid, e in self._data.items() if now - e["time"] > self.ttl]
        for uid in expired:
            self._data.pop(uid, None)

    def _entry(self, user_id: int) -> dict:
        self._cleanup()
        now = time.time()
        entry = self._data.get(user_id)
        if entry is None or now - entry["time"] > self.ttl:
            entry = {"time": now,
                     "messages": deque(maxlen=self.maxlen),
                     "requests": deque(maxlen=self.requests)}
            self._data[user_id] = entry
        entry["time"] = now
        return entry

    # ---------- سجل محادثة الشات ----------
    def get(self, user_id: int) -> list:
        return list(self._entry(user_id)["messages"])

    def add(self, user_id: int, role: str, content: str):
        self._entry(user_id)["messages"].append({"role": role, "content": content})

    # ---------- سجل طلبات المستخدم (للسياق) ----------
    def get_requests(self, user_id: int) -> list:
        return list(self._entry(user_id)["requests"])

    def add_request(self, user_id: int, content: str):
        self._entry(user_id)["requests"].append(content)

    def clear(self, user_id: int):
        self._data.pop(user_id, None)
