import json, os, threading, secrets, string, hashlib
from datetime import datetime, date
from typing import Optional

_lock    = threading.Lock()
DB_PATH  = "/tmp/db.json"
LOG_PATH = "/tmp/logs.json"
SES_PATH = "/tmp/sessions.json"


def _load(path):
    if not os.path.exists(path):
        return {} if path != LOG_PATH else []
    with open(path, "r") as f:
        try:    return json.load(f)
        except: return {} if path != LOG_PATH else []


def _save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def gen_key(name: str) -> str:
    rand = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
    return f"{name.lower().replace(' ','_')[:20]}_{rand}"


# ── Keys ──────────────────────────────────────────────────────────────────────

def get_all_keys() -> dict:
    with _lock:
        return _load(DB_PATH).get("keys", {})


def get_key_with_reset(api_key: str) -> Optional[dict]:
    with _lock:
        data = _load(DB_PATH)
        keys = data.get("keys", {})
        rec  = keys.get(api_key)
        if not rec: return None
        today = str(date.today())
        if rec.get("last_reset") != today:
            rec["used_today"] = 0
            rec["last_reset"] = today
            data["keys"] = keys
            _save(DB_PATH, data)
        return rec


def create_key(api_key, name, nick="", daily_limit=10, total_limit=300) -> dict:
    with _lock:
        data = _load(DB_PATH)
        keys = data.get("keys", {})
        rec  = {
            "name": name, "nick": nick or name,
            "daily_limit": daily_limit, "total_limit": total_limit,
            "total_used": 0, "used_today": 0,
            "last_reset": str(date.today()),
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        keys[api_key] = rec
        data["keys"]  = keys
        _save(DB_PATH, data)
        return rec


def update_key(api_key: str, **fields) -> bool:
    with _lock:
        data = _load(DB_PATH)
        keys = data.get("keys", {})
        if api_key not in keys: return False
        keys[api_key].update(fields)
        data["keys"] = keys
        _save(DB_PATH, data)
        return True


def delete_key(api_key: str) -> bool:
    with _lock:
        data = _load(DB_PATH)
        keys = data.get("keys", {})
        if api_key not in keys: return False
        del keys[api_key]
        data["keys"] = keys
        _save(DB_PATH, data)
        # Also remove session
        _remove_session_by_key(api_key)
        return True


def increment_usage(api_key: str, cut: int):
    with _lock:
        data = _load(DB_PATH)
        keys = data.get("keys", {})
        if api_key not in keys: return
        keys[api_key]["used_today"] = keys[api_key].get("used_today", 0) + cut
        keys[api_key]["total_used"] = keys[api_key].get("total_used", 0) + cut
        data["keys"] = keys
        _save(DB_PATH, data)


def reset_daily_all():
    with _lock:
        data  = _load(DB_PATH)
        keys  = data.get("keys", {})
        today = str(date.today())
        for rec in keys.values():
            rec["used_today"] = 0
            rec["last_reset"] = today
        data["keys"] = keys
        _save(DB_PATH, data)


# ── Sessions (1 device login) ─────────────────────────────────────────────────

def _load_sessions() -> dict:
    return _load(SES_PATH) if isinstance(_load(SES_PATH), dict) else {}


def _save_sessions(sessions: dict):
    _save(SES_PATH, sessions)


def _remove_session_by_key(api_key: str):
    """Remove any existing session for this api_key"""
    sessions = _load_sessions()
    to_del = [tok for tok, info in sessions.items() if info.get("api_key") == api_key]
    for tok in to_del:
        del sessions[tok]
    _save_sessions(sessions)


def create_session(api_key: str, ip: str) -> str:
    """
    Create new session token for api_key.
    Removes any previous session (1 device rule).
    """
    with _lock:
        sessions = _load_sessions()
        # Remove old sessions for this key
        to_del = [t for t, i in sessions.items() if i.get("api_key") == api_key]
        for t in to_del:
            del sessions[t]
        # Create new token
        token = secrets.token_urlsafe(32)
        sessions[token] = {
            "api_key":    api_key,
            "ip":         ip,
            "created_at": datetime.utcnow().isoformat(),
        }
        _save_sessions(sessions)
        return token


def validate_session(token: str) -> Optional[dict]:
    """Returns session info if valid, else None"""
    with _lock:
        sessions = _load_sessions()
        return sessions.get(token)


def delete_session(token: str):
    with _lock:
        sessions = _load_sessions()
        sessions.pop(token, None)
        _save_sessions(sessions)


# ── Logs ──────────────────────────────────────────────────────────────────────

def write_log(entry: dict):
    with _lock:
        logs = _load(LOG_PATH)
        if not isinstance(logs, list): logs = []
        entry["timestamp"] = datetime.utcnow().isoformat()
        logs.append(entry)
        if len(logs) > 500: logs = logs[-500:]
        _save(LOG_PATH, logs)


def get_logs(limit: int = 50) -> list:
    with _lock:
        logs = _load(LOG_PATH)
        if not isinstance(logs, list): return []
        return list(reversed(logs))[:limit]
