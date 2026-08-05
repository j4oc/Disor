"""
Disor v2 — سيرفر ويب صغير (keep-alive)
أهميته على الاستضافات اللي بتتوقع إن في ويب سيرفر شغال (زي Replit وخلافه):
بيفتح صفحة status بسيطة و endpoint صحة عشان ينفع تشيك عليه من أي مكان.

مش بيحتاج Flask — مكتبات قياسية بس.
"""
import json
import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

log = logging.getLogger("disor.web")

_started = time.time()
_status = {"online": False, "guilds": 0, "latency_ms": 0.0}


def set_status(online: bool, guilds: int = 0, latency_ms: float = 0.0):
    _status["online"] = online
    _status["guilds"] = guilds
    _status["latency_ms"] = round(latency_ms, 1)


def _page():
    uptime = int(time.time() - _started)
    h, rem = divmod(uptime, 3600)
    m, s = divmod(rem, 60)
    color = "✅" if _status["online"] else "🛑"
    state = "شغال" if _status["online"] else "متوقف"
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Disor v2 — Status</title>
<style>
body{{font-family:Tahoma,Arial,sans-serif;background:#1e1f29;color:#e8e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}
.card{{background:#2b2d3b;border-radius:16px;padding:32px 40px;box-shadow:0 8px 30px rgba(0,0,0,.4);text-align:center;max-width:420px}}
.big{{font-size:56px}}h1{{margin:12px 0 4px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:20px}}
.box{{background:#22232f;border-radius:10px;padding:14px}}
.box .v{{font-size:22px;font-weight:bold;color:#7ee787}}
.tag{{display:inline-block;margin-top:12px;padding:4px 14px;border-radius:999px;background:#3a3d52;font-size:13px;color:#a9acd0}}
</style></head>
<body><div class="card">
<div class="big">{color}</div><h1>Disor v2</h1>
<div class="tag">حالة البوت: {state}</div>
<div class="grid">
<div class="box"><div class="v">{_status['guilds']}</div>سيرفرات</div>
<div class="box"><div class="v">{_status['latency_ms']}ms</div>البنق</div>
</div>
<div class="tag">مدة التشغيل: {h}h {m}m {s}s</div>
</div></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = json.dumps(_status).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        body = _page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # مش عايزين سبام في اللوج


def start_web(port: int = 8080):
    try:
        server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
        t = threading.Thread(target=server.serve_forever, daemon=True, name="keepalive-web")
        t.start()
        log.info("🌐 سيرفر الويب شغال على البورت %d (صفحة الحالة: / — صحة: /health)", port)
        return server
    except OSError as e:
        log.warning("مقدرتش أشغل سيرفر الويب على البورت %d: %s", port, e)
        return None
