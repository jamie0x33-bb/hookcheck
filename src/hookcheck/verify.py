from __future__ import annotations

import json
import ssl
import time
import urllib.request
import urllib.error


def check_endpoint(
    url: str,
    *,
    method: str = "POST",
    timeout: int = 10,
    verify_tls: bool = True,
) -> dict:
    payload = json.dumps({"type": "ping", "ts": int(time.time())}).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "hookcheck/0.4"}

    req = urllib.request.Request(url, data=payload, method=method, headers=headers)

    ctx = None
    if not verify_tls:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            elapsed = (time.monotonic() - start) * 1000
            body = resp.read()
            return {
                "reachable": True,
                "status": resp.status,
                "latency_ms": round(elapsed, 1),
                "content_type": resp.headers.get("Content-Type", ""),
                "body_length": len(body),
            }
    except urllib.error.HTTPError as exc:
        elapsed = (time.monotonic() - start) * 1000
        return {
            "reachable": True,
            "status": exc.code,
            "latency_ms": round(elapsed, 1),
            "error": exc.reason,
        }
    except urllib.error.URLError as exc:
        return {"reachable": False, "error": str(exc.reason)}
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}
