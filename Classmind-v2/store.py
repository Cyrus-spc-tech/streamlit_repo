"""
store.py  —  ClassMind in-memory data store
All session state lives here. Structure is Redis-ready (flat dicts).
Adds optional JSON persistence: load on startup, auto-save on change.
"""
import json
import logging
import os
import random
import string
import time
import uuid
from pathlib import Path
from typing import Dict, Optional

log = logging.getLogger("classmind.store")

# ── global store ──────────────────────────────────────────────────
sessions: Dict[str, dict] = {}   # session_code -> session dict
teacher_sessions: Dict[str, str] = {}  # teacher_id (email) -> session_code

# ── persistence config (set by main.py after loading .env) ────────
_persistence_mode: str = "none"   # "none" | "json"
_data_dir: Path = Path("data")


def configure_persistence(mode: str, data_dir: str) -> None:
    """Called once from main.py lifespan after reading .env."""
    global _persistence_mode, _data_dir
    _persistence_mode = mode.lower().strip()
    _data_dir = Path(data_dir)
    if _persistence_mode == "json":
        _data_dir.mkdir(parents=True, exist_ok=True)
        log.info("Persistence: JSON -> %s", _data_dir.resolve())
    else:
        log.info("Persistence: in-memory only (sessions reset on restart)")


# ── id helpers ────────────────────────────────────────────────────
def gen_code() -> str:
    for _ in range(20):
        c = "".join(random.choices(string.digits, k=6))
        if c not in sessions:
            return c
    raise RuntimeError("Cannot generate unique code")


def gen_id(prefix="") -> str:
    return prefix + uuid.uuid4().hex[:8]


def now() -> float:
    return time.time()


# ── JSON persistence helpers ──────────────────────────────────────

def _session_path(code: str) -> Path:
    return _data_dir / f"session_{code}.json"


def _serialize_session(s: dict) -> dict:
    """Convert non-serialisable types (sets, WebSockets) before JSON dump."""
    def _convert(obj):
        if isinstance(obj, set):
            return {"__set__": list(obj)}
        if hasattr(obj, "send_text"):          # WebSocket — never serialise
            return None
        raise TypeError(f"Cannot serialise {type(obj)}")

    return json.loads(json.dumps(s, default=_convert))


def _deserialize_session(d: dict) -> dict:
    """Restore sets from the __set__ sentinel; reinit runtime-only fields."""
    def _restore(obj):
        if isinstance(obj, dict):
            if "__set__" in obj and len(obj) == 1:
                return set(obj["__set__"])
            return {k: _restore(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_restore(i) for i in obj]
        return obj

    s = _restore(d)
    # Runtime WebSocket fields are never stored — reinit to None / empty dict
    s["teacher_ws"] = None
    s.setdefault("ws_clients", {})
    return s


def save_session(code: str) -> None:
    """Persist one session to disk (JSON mode only)."""
    if _persistence_mode != "json":
        return
    s = sessions.get(code)
    if s is None:
        return
    try:
        path = _session_path(code)
        tmp  = path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(_serialize_session(s), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(path)
    except Exception as exc:
        log.warning("Failed to save session %s: %s", code, exc)


def delete_session_file(code: str) -> None:
    """Remove a persisted session file."""
    if _persistence_mode != "json":
        return
    try:
        _session_path(code).unlink(missing_ok=True)
    except Exception as exc:
        log.debug("Could not delete session file %s: %s", code, exc)


def load_all_sessions() -> int:
    """Load all session files from disk into memory. Returns count loaded."""
    if _persistence_mode != "json":
        return 0
    loaded = 0
    if not _data_dir.exists():
        return 0
    for path in sorted(_data_dir.glob("session_*.json")):
        code = path.stem.replace("session_", "")
        try:
            raw = path.read_text(encoding="utf-8")
            s   = _deserialize_session(json.loads(raw))
            sessions[code] = s
            # Rebuild teacher_sessions mapping
            t_id = s.get("teacher_email") or s.get("teacher_id")
            if t_id and s.get("status") != "ended":
                teacher_sessions[t_id] = code
            loaded += 1
            log.info("Loaded session %s (%s)", code, s.get("status", "?"))
        except Exception as exc:
            log.warning("Skipped corrupt session file %s: %s", path.name, exc)
    return loaded


# ── session factory ───────────────────────────────────────────────
def new_session(code: str, teacher_name: str) -> dict:
    return {
        "code":             code,
        "teacher_name":     teacher_name,
        "teacher_id":       None,        # Linked to Google email
        "status":           "waiting",   # waiting|active|paused|ended
        "mode":             "live",      # live|test
        "created_at":       now(),
        "last_activity_at": now(),
        # websockets (runtime only — never persisted)
        "teacher_ws":       None,
        "ws_clients":       {},          # student_id -> WebSocket
        # roster
        "students":         {},          # student_id -> student dict
        "waiting_room":     [],          # [student_id, ...]
        "kicked":           set(),
        "allowed_students": set(),        # optional CSV admission list
        "active_rolls":     set(),        # duplicate login guard
        # tasks
        "tasks":            [],
        "current_task_idx": -1,
        "responses":        {},          # task_id -> {student_id -> response}
        "delivery_seq":     0,
        "task_deliveries":  {},          # delivery_id -> delivery metadata
        "student_current_task": {},      # student_id -> latest task_id assigned
        # groups
        "groups":           [],
        # communication
        "chat_messages":    [],
        "doubts":           [],
        "raised_hands":     [],
        # content
        "content_files":    {},          # filename -> {name,data,content_type,size}
        "quiz":             None,
        # test mode
        "test_state": {
            "active":        False,
            "start_time":    None,
            "duration_secs": 0,
            "task_ids":      [],
            "submitted":     set(),
            "scores":        {},          # student_id -> int
            "leaderboard":   [],
            "quiz":          None,
            "answers":       {},          # student_id -> {answers, submitted_at, student_name}
        },
    }


# ── student factory ───────────────────────────────────────────────
def new_student(name: str, anonymous: bool = True) -> dict:
    sid = gen_id()
    return {
        "id":             sid,
        "name":           name,
        "real_name":      name,
        "anonymous":      anonymous,
        "status":         "waiting",
        "score":          0,
        "correct":        0,
        "total_answered": 0,
        "hint_requests":  0,
        "joined_at":      now(),
        "last_seen":      now(),
        "allowed_students": set(),
        "active_rolls":   set(),
        # coding analytics
        "coding_score":       0,
        "coding_submitted":   False,
        "test_cases_passed":  0,
        "total_test_cases":   0,
        "coding_time_taken":  0,
    }


# ── task factory ──────────────────────────────────────────────────
def new_task(d: dict) -> dict:
    return {
        "id":              gen_id("t"),
        "question":        d.get("question", ""),
        "type":            d.get("type", "mcq"),         # mcq|short|coding
        "options":         d.get("options", []),
        "correct_answer":  d.get("correct_answer", d.get("answer", "")),
        "topic":           d.get("topic", "General"),
        "difficulty":      d.get("difficulty", "medium"),
        "hint":            d.get("hint"),
        "hint_visibility": d.get("hint_visibility", "on_request"),
        "time_limit":      d.get("time_limit"),
        "long_answer":     bool(d.get("long_answer", False)),
        "content_file":    d.get("content_file"),
        "created_at":      now(),
    }


# ── helpers ───────────────────────────────────────────────────────
DIFF_SCORE = {"easy": 5, "medium": 10, "hard": 20}


def score_for(task: dict) -> int:
    return DIFF_SCORE.get(task.get("difficulty", "medium"), 10)


def safe_task(task: dict) -> dict:
    """Strip correct_answer and hide hint unless visibility=always."""
    t = {k: v for k, v in task.items() if k != "correct_answer"}
    t["id"]              = str(t.get("id") or "")
    t["question"]        = str(t.get("question") or "")
    t["type"]            = str(t.get("type") or "mcq")
    t["options"]         = t.get("options") or []
    t["topic"]           = str(t.get("topic") or "General")
    t["difficulty"]      = str(t.get("difficulty") or "medium")
    t["hint_visibility"] = str(t.get("hint_visibility") or "on_request")
    if t.get("hint_visibility") != "always":
        t["hint"] = None
    return t


def get_session(code: str) -> Optional[dict]:
    """Return session or None."""
    return sessions.get(code)
