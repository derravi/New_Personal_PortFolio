"""
rate_limit.py — Minimal in-memory sliding-window rate limiter.

No Redis/extra service required (fine for a single-process portfolio site).
For a multi-worker/multi-instance deployment, swap this for Flask-Limiter
backed by Redis — this is intentionally simple to avoid a new dependency.
"""

import time
from collections import defaultdict
from functools import wraps
from flask import request, jsonify

_hits = defaultdict(list)


def rate_limit(max_requests=10, window_seconds=60):
    """Decorator: limits a route to `max_requests` per `window_seconds` per IP."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
            key = f"{view_func.__name__}:{ip}"
            now = time.time()
            recent = [t for t in _hits[key] if now - t < window_seconds]
            if len(recent) >= max_requests:
                return jsonify({"error": "Too many requests — please slow down and try again shortly."}), 429
            recent.append(now)
            _hits[key] = recent
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
