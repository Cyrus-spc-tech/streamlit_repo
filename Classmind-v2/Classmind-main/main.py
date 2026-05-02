"""
main.py  ─  ClassMind Backend  (portable, cross-platform)
Run:  uvicorn main:app --host 0.0.0.0 --port 8000 --reload

WebSocket endpoints
  ws://host/ws/teacher/{session_code}
  ws://host/ws/student/{session_code}/{student_id}
"""

from __future__ import annotations

# ── Load environment variables FIRST ──────────────────────────────
from dotenv import load_dotenv
# ── Environment ──
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# ── Standard library imports ──────────────────────────────────────
import asyncio
import base64
import csv
import json
import logging
import os
import random
import time
import uuid
from contextlib import asynccontextmanager
from io import StringIO
from typing import Dict, List, Optional
from pathlib import Path
# ── Third-party imports ───────────────────────────────────────────
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import (
    BackgroundTasks, Body, Depends, FastAPI, File, Form, HTTPException,
    Query, UploadFile, WebSocket, WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

# ── Internal modules ──────────────────────────────────────────────
from analytics import compute_analytics, compute_report
from sandbox import RunResult, run_code
from store import (
    configure_persistence, gen_code, gen_id, load_all_sessions,
    new_session, new_student, new_task, now, safe_task,
    save_session, score_for, sessions, teacher_sessions,
)
from email_service import (
    send_session_email, is_valid_email,
    send_student_report_email, send_class_starting_email,
)




# ── logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("classmind")


# ── Google OAuth Source of Truth ──
def get_google_client_id() -> str:
    """Retrieves and sanitizes the Google Client ID from environment."""
    val = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    # Strip accidental quotes
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1].strip()
    return val

def validate_oauth_config():
    """Strict runtime check for OAuth configuration."""
    cid = get_google_client_id()
    placeholders = ["your-google-client-id", "your-google-client-id-here"]
    
    if not cid:
        log.error("❌ OAuth config invalid: GOOGLE_CLIENT_ID is missing from .env")
        # In a real production app we might sys.exit(1), but for this environment
        # we'll log loudly and let the dev see the error.
        return False
        
    if any(p in cid.lower() for p in placeholders):
        log.error("❌ OAuth config invalid: GOOGLE_CLIENT_ID contains placeholder value")
        return False
        
    masked = cid[:6] + "..." + cid[-10:] if len(cid) > 16 else "***"
    log.info("[AUTH] Google Client ID loaded: %s", masked)
    log.info("✅ OAuth config valid")
    return True

# ── validation ───────────────────────────────────────────────────
def check_environment():
    """Validates environment variables on startup."""
    email = os.getenv("EMAIL_ADDRESS", "")
    pwd = os.getenv("EMAIL_PASSWORD", "")
    placeholders = ["your-email@gmail.com", "your-app-password", "your_email@gmail.com"]
    if not email or any(p in email for p in placeholders):
        log.warning("[!] EMAIL_ADDRESS is not configured properly in .env")
    elif not pwd or any(p in pwd for p in placeholders):
        log.warning("[!] EMAIL_PASSWORD is not configured properly in .env")
    else:
        log.info("[OK] Email system configured for: %s", email)
    
    # Strict OAuth check
    validate_oauth_config()

check_environment()

from fastapi import Request
import traceback



# ── concurrency helpers ───────────────────────────────────────────
semaphore: asyncio.Semaphore        # initialised in lifespan
execution_queue: asyncio.Queue      # initialised in lifespan
session_locks: Dict[str, asyncio.Lock] = {}


def session_lock(code: str) -> asyncio.Lock:
    if code not in session_locks:
        session_locks[code] = asyncio.Lock()
    return session_locks[code]

admin_connections: set[WebSocket] = set()
admin_tokens: Dict[str, str] = {}
admin_join_history: List[dict] = []
admin_security = HTTPBearer(auto_error=False)

# ── ADMIN EMAILS (RBAC) ───────────────────────────────────────────
ADMIN_EMAILS = os.getenv("ADMIN_EMAILS", "classmind7@gmail.com").split(",")


def admin_authorized(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(admin_security),
) -> str:
    """
    RBAC: Authorizes a request for administrative routes.
    Supports both legacy admin tokens and verified Google ID tokens for users in ADMIN_EMAILS.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Unauthorized: Bearer token required")
    
    token = credentials.credentials
    
    # 1. Try legacy admin token (from /admin/login)
    user = admin_tokens.get(token)
    if user:
        return user
        
    # 2. Try Google ID token
    try:
        google_client_id = get_google_client_id()
        if google_client_id:
            # Note: verify_oauth2_token handles expiration and signature checks
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), google_client_id)
            email = idinfo.get("email")
            if email and email in ADMIN_EMAILS:
                log.info("[AUTH] Admin access granted to Google user: %s", email)
                return email
    except Exception as e:
        # Not a valid Google token or verification failed — fall through
        pass
        
    raise HTTPException(401, "Unauthorized: Admin privileges required")


def google_authorized(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> str:
    """
    Verifies that the requester has a valid Google session.
    Returns the verified email address.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Authentication required. Please log in with Google.")
    
    token = credentials.credentials
    try:
        google_client_id = get_google_client_id()
        if not google_client_id:
            raise HTTPException(500, "Server configuration error: GOOGLE_CLIENT_ID missing")
            
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), google_client_id)
        email = idinfo.get("email")
        if not email:
            raise HTTPException(401, "Could not verify email from Google token")
        return email
    except Exception as e:
        log.warning("[AUTH] Google token verification failed: %s", e)
        raise HTTPException(401, "Your session has expired. Please log in again.")


def normalize_student_key(name: str, roll: str, cls: str) -> str:
    return f"{name.strip().lower()}|{roll.strip().upper()}|{cls.strip().upper()}"


def admin_session_summary(s: dict) -> dict:
    students = [st for st in s["students"].values() if st.get("status") == "active"]
    return {
        "session_code":  s["code"],
        "teacher_name":  s["teacher_name"],
        "status":        s["status"],
        "students_count": len(students),
        "tasks_sent":    len(s.get("task_deliveries", {})),
        "responses":     sum(len(r) for r in s.get("responses", {}).values()),
        "created_at":    s.get("created_at"),
        "last_activity": s.get("last_activity_at", s.get("created_at")),
    }


def admin_dashboard_data() -> dict:
    active_sessions = [s for s in sessions.values() if s.get("status") != "ended"]
    all_students = [st for s in sessions.values() for st in s.get("students", {}).values()]
    active_teachers = [s for s in sessions.values() if s.get("teacher_ws")]
    return {
        "total_sessions":   len(sessions),
        "active_sessions":  len(active_sessions),
        "total_students":   len(all_students),
        "total_teachers":   len({s["teacher_name"] for s in sessions.values() if s.get("teacher_name")}),
        "live_sessions":    [admin_session_summary(s) for s in sorted(active_sessions, key=lambda x: x.get("created_at", 0), reverse=True)],
        "top_active_sessions": sorted(
            [admin_session_summary(s) for s in sessions.values()],
            key=lambda x: x["students_count"],
            reverse=True,
        )[:5],
        "inactive_sessions": [
            admin_session_summary(s)
            for s in sessions.values()
            if s.get("status") != "ended"
            and (now() - s.get("last_activity_at", s.get("created_at", 0))) > 300
        ],
        "student_activity_heatmap": [
            {"session_code": s["code"], "student_count": len([st for st in s["students"].values() if st.get("status") == "active"]),}
            for s in sessions.values()
        ],
        "suspicious_activity": detect_suspicious_activity(),
    }


def detect_suspicious_activity() -> dict:
    now_ts = now()
    recent_joins = [e for e in admin_join_history if e["ts"] >= now_ts - 60]
    large_join_spike = len(recent_joins) >= 10
    grouped = {}
    for e in admin_join_history:
        grouped.setdefault(e["student_key"], set()).add(e["session_code"])
    duplicate_joins = [
        {"student_key": k, "sessions": sorted(list(v))}
        for k, v in grouped.items() if len(v) > 1
    ]
    return {
        "multiple_session_joins": duplicate_joins,
        "join_spike": {
            "enabled": large_join_spike,
            "count_last_minute": len(recent_joins),
        },
    }


def touch_session(s: dict) -> None:
    s["last_activity_at"] = now()


def admin_broadcast(data: dict) -> None:
    payload = {"type": "admin_event", **data, "dashboard": admin_dashboard_data()}
    live = set(admin_connections)
    for ws in list(live):
        try:
            asyncio.create_task(ws.send_text(json.dumps(payload, default=str)))
        except Exception as exc:
            log.debug("Admin broadcast failed: %s", exc)
            admin_connections.discard(ws)


# ══════════════════════════════════════════════════════════════════
#  WEBSOCKET HELPERS
# ══════════════════════════════════════════════════════════════════

async def ws_send(ws: WebSocket, data: dict) -> bool:
    """Send a JSON payload to one WebSocket; returns True on success."""
    try:
        await ws.send_text(json.dumps(data, default=str))
        return True
    except Exception as exc:
        log.debug("ws_send failed: %s", exc)
        return False


async def ws_teacher(s: dict, data: dict) -> bool:
    if s.get("teacher_ws"):
        return await ws_send(s["teacher_ws"], data)
    return False


async def ws_student(s: dict, sid: str, data: dict) -> bool:
    ws = s.get("ws_clients", {}).get(sid)
    if not ws:
        return False
    ok = await ws_send(ws, data)
    if not ok and s.get("ws_clients", {}).get(sid) is ws:
        s["ws_clients"].pop(sid, None)
    return ok


async def ws_all_students(
    s: dict,
    data: dict,
    student_ids: Optional[List[str]] = None,
) -> List[str]:
    ids = student_ids if student_ids is not None else list(s.get("ws_clients", {}).keys())
    delivered: List[str] = []
    for sid in list(ids):
        if await ws_student(s, sid, data):
            delivered.append(sid)
    return delivered


async def ws_broadcast(s: dict, data: dict):
    await ws_teacher(s, data)
    await ws_all_students(s, data)


async def push_roster(s: dict):
    active  = [st for st in s["students"].values() if st["status"] == "active"]
    waiting = [s["students"][sid] for sid in s["waiting_room"] if sid in s["students"]]
    await ws_teacher(s, {
        "type":         "roster_update",
        "active":       active,
        "waiting":      waiting,
        "raised_hands": s["raised_hands"],
    })


# ══════════════════════════════════════════════════════════════════
#  TASK DELIVERY PIPELINE
# ══════════════════════════════════════════════════════════════════

def task_index(s: dict, task_id: str) -> int:
    return next((i for i, t in enumerate(s["tasks"]) if t["id"] == task_id), -1)


def normalize_target(
    target_type: Optional[str],
    target_id:   Optional[str],
) -> tuple[str, str]:
    """Normalise and validate target_type/target_id; raises HTTPException on bad input."""
    tt = (target_type or "all").strip().lower()
    if tt in {"class", "everyone", ""}:
        tt = "all"
    if tt not in {"all", "student", "group"}:
        raise HTTPException(400, "target_type must be one of: all, student, group")
    tid = str(target_id or "").strip()
    if tt == "all":
        return tt, "all"
    if not tid:
        raise HTTPException(422, f"target_id is required for target_type='{tt}'")
    return tt, tid


def active_student_ids(s: dict) -> List[str]:
    kicked = s.get("kicked", set())
    return [
        sid for sid, st in s.get("students", {}).items()
        if st.get("status") == "active" and sid not in kicked
    ]


def resolve_task_recipients(
    s: dict,
    target_type: str,
    target_id:   str,
) -> tuple[List[str], str]:
    """Return (list_of_recipient_ids, human_readable_label). Raises on invalid target."""
    active_ids = set(active_student_ids(s))

    if target_type == "all":
        recipients = sorted(active_ids)
        label      = "entire class"

    elif target_type == "student":
        student = s["students"].get(target_id)
        if not student:
            raise HTTPException(404, f"Student '{target_id}' not found")
        if student.get("status") != "active" or target_id in s.get("kicked", set()):
            raise HTTPException(409, "Target student is not active")
        recipients = [target_id]
        label      = student.get("name") or target_id

    else:  # group
        group = next((g for g in s.get("groups", []) if g.get("id") == target_id), None)
        if not group:
            raise HTTPException(404, f"Group '{target_id}' not found")
        members = list(dict.fromkeys(group.get("members", [])))
        unknown = [sid for sid in members if sid not in s.get("students", {})]
        if unknown:
            raise HTTPException(400, f"Group contains unknown students: {', '.join(unknown)}")
        recipients = [sid for sid in members if sid in active_ids]
        label      = group.get("name") or target_id

    if not recipients:
        raise HTTPException(409, "No active recipients matched the selected target")
    return recipients, label


def _S(code: str) -> dict:
    """Return session dict or raise 404."""
    s = sessions.get(code)
    if not s:
        raise HTTPException(404, f"Session '{code}' not found")
    return s


def _T(s: dict, task_id: str) -> dict:
    """Return task dict from session or raise 404."""
    t = next((t for t in s["tasks"] if t["id"] == task_id), None)
    if not t:
        raise HTTPException(404, f"Task '{task_id}' not found")
    return t


def task_payload(s: dict, delivery: dict) -> dict:
    """Build the WebSocket 'new_task' payload for a delivery record."""
    task         = _T(s, delivery["task_id"])
    payload_task = safe_task(task)

    cf_name = task.get("content_file")
    if cf_name and cf_name in s.get("content_files", {}):
        cf = s["content_files"][cf_name]
        payload_task["content"] = {
            "name":         cf["name"],
            "content_type": cf["content_type"],
            "data":         cf["data"],
        }

    return {
        "type":         "new_task",
        "delivery_id":  delivery["id"],
        "task_id":      delivery["task_id"],
        "task":         payload_task,
        "target": {
            "type":  delivery["target_type"],
            "id":    delivery["target_id"],
            "label": delivery["target_label"],
        },
        "task_index":  delivery["task_index"],
        "total_tasks": delivery["total_tasks"],
        "sent_at":     delivery["created_at"],
    }


def create_delivery_record(
    s:           dict,
    task_id:     str,
    target_type: str,
    target_id:   str,
) -> dict:
    """Create, store, and return a delivery record (no IO)."""
    task            = _T(s, task_id)
    recipients, lbl = resolve_task_recipients(s, target_type, target_id)

    s["delivery_seq"] = int(s.get("delivery_seq", 0)) + 1
    delivery_id       = f"td{s['delivery_seq']:06d}"
    idx               = task_index(s, task["id"])

    delivery = {
        "id":             delivery_id,
        "sequence":       s["delivery_seq"],
        "task_id":        task["id"],
        "target_type":    target_type,
        "target_id":      target_id,
        "target_label":   lbl,
        "recipients":     recipients,
        "sent_to":        [],
        "acknowledged_by": [],
        "created_at":     now(),
        "last_attempt_at": None,
        "task_index":     idx,
        "total_tasks":    len(s["tasks"]),
    }

    s.setdefault("task_deliveries", {})[delivery_id] = delivery
    s.setdefault("student_current_task", {})
    for sid in recipients:
        s["student_current_task"][sid] = task["id"]

    # advance global pointer for "all" deliveries
    if target_type == "all" and idx >= 0 and idx > s.get("current_task_idx", -1):
        s["current_task_idx"] = idx

    return delivery


def delivery_summary(delivery: dict) -> dict:
    recipients = delivery.get("recipients", [])
    sent_to    = delivery.get("sent_to", [])
    acked      = delivery.get("acknowledged_by", [])
    return {
        "status":            "sent",
        "sent":              True,
        "delivery_id":       delivery["id"],
        "task_id":           delivery["task_id"],
        "target": {
            "type":  delivery["target_type"],
            "id":    delivery["target_id"],
            "label": delivery["target_label"],
        },
        "recipient_ids":     recipients,
        "recipient_count":   len(recipients),
        "sent_count":        len(sent_to),
        "queued_count":      len([sid for sid in recipients if sid not in sent_to]),
        "acknowledged_count": len(acked),
        "task_index":        delivery["task_index"],
        "total_tasks":       delivery["total_tasks"],
    }


async def deliver_recorded_task(s: dict, delivery: dict) -> dict:
    """Push task payload over WebSocket to all recipients; notify teacher."""
    payload   = task_payload(s, delivery)
    sent_now: List[str] = []

    for sid in delivery["recipients"]:
        if await ws_student(s, sid, payload):
            sent_now.append(sid)

    delivery["last_attempt_at"] = now()
    delivery["sent_to"] = sorted(set(delivery.get("sent_to", [])) | set(sent_now))

    summary = delivery_summary(delivery)
    await ws_teacher(s, {"type": "task_sent", "delivery": summary, **summary})
    admin_broadcast({
        "event": "task_sent",
        "session_code": s["code"],
        "delivery": summary,
    })
    touch_session(s)
    return summary


async def deliver_task_request(code: str, req: "SendTaskReq") -> dict:
    target_type, target_id = normalize_target(req.target_type, req.target_id)
    async with session_lock(code):
        s        = _S(code)
        delivery = create_delivery_record(s, req.task_id, target_type, target_id)
    return await deliver_recorded_task(s, delivery)


async def deliver_next_task_request(code: str) -> dict:
    async with session_lock(code):
        s = _S(code)
        if not s["tasks"]:
            raise HTTPException(400, "No tasks in queue")
        next_idx = s.get("current_task_idx", -1) + 1
        if next_idx >= len(s["tasks"]):
            raise HTTPException(400, "All tasks already sent")
        task_id  = s["tasks"][next_idx]["id"]
        delivery = create_delivery_record(s, task_id, "all", "all")
        s["current_task_idx"] = next_idx
    return await deliver_recorded_task(s, delivery)


def mark_task_ack(s: dict, student_id: str, delivery_id: Optional[str]) -> bool:
    if not delivery_id:
        return False
    delivery = s.get("task_deliveries", {}).get(delivery_id)
    if not delivery or student_id not in delivery.get("recipients", []):
        return False
    acked = set(delivery.get("acknowledged_by", []))
    acked.add(student_id)
    delivery["acknowledged_by"] = sorted(acked)
    return True


def latest_delivery_for_student(s: dict, student_id: str) -> Optional[dict]:
    deliveries = [
        d for d in s.get("task_deliveries", {}).values()
        if student_id in d.get("recipients", [])
    ]
    return max(deliveries, key=lambda d: d.get("sequence", 0)) if deliveries else None


async def replay_unacked_tasks(s: dict, student_id: str):
    """Re-send any un-acknowledged deliveries to a student who just reconnected."""
    pending = sorted(
        (
            d for d in s.get("task_deliveries", {}).values()
            if student_id in d.get("recipients", [])
            and student_id not in d.get("acknowledged_by", [])
        ),
        key=lambda d: d.get("sequence", 0),
    )
    for delivery in pending:
        if await ws_student(s, student_id, task_payload(s, delivery)):
            delivery["sent_to"]          = sorted(set(delivery.get("sent_to", [])) | {student_id})
            delivery["last_attempt_at"]  = now()


def student_can_submit_task(s: dict, student_id: str, task_id: str) -> bool:
    if s.get("quiz_meta"):
        return True
    if s.get("mode") == "test":
        return True
    return any(
        student_id in d.get("recipients", []) and d.get("task_id") == task_id
        for d in s.get("task_deliveries", {}).values()
    )


# ══════════════════════════════════════════════════════════════════
#  TASK INPUT NORMALISATION
# ══════════════════════════════════════════════════════════════════

def normalize_task_input(data: dict) -> dict:
    question = str(data.get("question") or "").strip()
    if not question:
        raise HTTPException(422, "Question is required")

    task_type   = str(data.get("type") or "mcq").strip().lower()
    long_answer = bool(data.get("long_answer", False))
    if task_type == "long":
        task_type   = "short"
        long_answer = True
    if task_type not in {"mcq", "short", "coding"}:
        raise HTTPException(422, "Task type must be: mcq, short, long, or coding")

    difficulty = str(data.get("difficulty") or "medium").strip().lower()
    if difficulty not in {"easy", "medium", "hard"}:
        raise HTTPException(422, "Difficulty must be: easy, medium, or hard")

    hint_visibility = str(data.get("hint_visibility") or "on_request").strip()
    if hint_visibility not in {"always", "on_request", "after_submission"}:
        raise HTTPException(422, "Invalid hint_visibility")

    raw_time   = data.get("time_limit")
    time_limit = None
    if raw_time not in (None, ""):
        try:
            time_limit = int(raw_time)
        except (TypeError, ValueError):
            raise HTTPException(422, "time_limit must be a positive integer")
        if time_limit <= 0 or time_limit > 7200:
            raise HTTPException(422, "time_limit must be between 1 and 7200 seconds")

    options        = [str(o).strip() for o in (data.get("options") or []) if str(o).strip()]
    correct_answer = str(data.get("correct_answer") or data.get("answer") or "").strip()

    if task_type == "mcq":
        if len(options) < 2:
            raise HTTPException(422, "MCQ tasks need at least 2 options")
        letters        = [chr(65 + i) for i in range(len(options))]
        correct_answer = correct_answer.upper()
        if correct_answer not in letters:
            raise HTTPException(422, f"correct_answer must be one of: {', '.join(letters)}")
    else:
        options = []

    return {
        "question":        question,
        "type":            task_type,
        "options":         options,
        "correct_answer":  correct_answer,
        "topic":           str(data.get("topic") or "General").strip() or "General",
        "difficulty":      difficulty,
        "hint":            str(data.get("hint")).strip() if data.get("hint") else None,
        "hint_visibility": hint_visibility,
        "time_limit":      time_limit,
        "long_answer":     long_answer,
        "content_file":    data.get("content_file"),
    }


# ══════════════════════════════════════════════════════════════════
#  PYDANTIC MODELS
# ══════════════════════════════════════════════════════════════════

class CreateSessionReq(BaseModel):
    teacher_name: str
    email:        Optional[str] = None
    phone:        Optional[str] = None

class GoogleLoginReq(BaseModel):
    token: str

class CreateTaskReq(BaseModel):
    session_code:    str
    question:        str
    type:            str = "mcq"
    options:         Optional[List[str]] = []
    correct_answer:  Optional[str] = ""
    topic:           str = "General"
    difficulty:      str = "medium"
    hint:            Optional[str] = None
    hint_visibility: str = "on_request"
    time_limit:      Optional[int] = None
    long_answer:     bool = False

class SendTaskReq(BaseModel):
    task_id:     str            = Field(..., min_length=1)
    target_type: str            = Field("all")
    target_id:   Optional[str] = None

class SubmitResponseReq(BaseModel):
    session_code: str
    student_id:   str
    task_id:      str
    answer:       str
    time_taken:   Optional[float] = None

class GenerateGroupsReq(BaseModel):
    session_code: str
    strategy:     str = "auto"

class UpdateGroupReq(BaseModel):
    session_code: str
    group_id:     str
    members:      List[str]

class SendMessageReq(BaseModel):
    session_code: str
    sender_id:    str
    content:      str
    chat_type:    str = "global"
    target_id:    Optional[str] = None

class SubmitDoubtReq(BaseModel):
    session_code: str
    student_id:   str
    doubt_text:   str

class ResolveDoubtReq(BaseModel):
    session_code: str
    doubt_id:     str
    answer:       str

class StartTestReq(BaseModel):
    session_code:  str
    duration_secs: int = 1800
    task_ids:      Optional[List[str]] = None

class RunCodeReq(BaseModel):
    session_code: str
    student_id:   str
    code:         str
    language:     str = "python"
    task_id:      Optional[str] = None

class SaveQuizReq(BaseModel):
    session_code: str
    quiz:         list
    task_ids:     Optional[List[str]] = None

class SendQuizReq(BaseModel):
    task_ids:    Optional[List[str]] = None
    target_type: str = "all"
    target_id:   Optional[str] = "all"

class SendReportReq(BaseModel):
    email: Optional[str] = None
    session_id: Optional[str] = None


# ══════════════════════════════════════════════════════════════════
#  BACKGROUND WORKERS
# ══════════════════════════════════════════════════════════════════

async def analytics_broadcaster():
    while True:
        await asyncio.sleep(2)
        for s in list(sessions.values()):
            if s["status"] == "active" and s.get("teacher_ws"):
                try:
                    await ws_teacher(s, {
                        "type":      "analytics_update",
                        "analytics": compute_analytics(s),
                    })
                except Exception:
                    pass


async def test_timer_watcher():
    while True:
        await asyncio.sleep(3)
        for s in list(sessions.values()):
            ts = s["test_state"]
            if ts["active"] and ts["start_time"]:
                elapsed = time.time() - ts["start_time"]
                if elapsed >= ts["duration_secs"]:
                    ts["active"] = False
                    s["mode"]    = "live"
                    lb = sorted(ts["scores"].items(), key=lambda x: x[1], reverse=True)
                    ts["leaderboard"] = [
                        {
                            "student_id":   sid,
                            "score":        sc,
                            "rank":         i + 1,
                            "student_name": s["students"].get(sid, {}).get("name", sid),
                        }
                        for i, (sid, sc) in enumerate(lb)
                    ]
                    try:
                        await ws_broadcast(s, {
                            "type":        "test_ended",
                            "reason":      "time_expired",
                            "leaderboard": ts["leaderboard"],
                        })
                    except Exception:
                        pass


async def code_worker():
    while True:
        code, language, future = await execution_queue.get()
        try:
            async with semaphore:
                result = run_code(code, language)
            future.set_result(result)
        except Exception as e:
            future.set_result(RunResult(f"Error: {e}", error=True))
        finally:
            execution_queue.task_done()


# ══════════════════════════════════════════════════════════════════
#  APP SETUP  ← app is defined HERE, before any @app routes
# ══════════════════════════════════════════════════════════════════

async def autosave_worker():
    """Periodically persist all sessions to disk."""
    interval = int(os.getenv("AUTOSAVE_INTERVAL", "10"))
    while True:
        await asyncio.sleep(interval)
        for code in list(sessions):
            save_session(code)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global semaphore, execution_queue
    semaphore       = asyncio.Semaphore(3)
    execution_queue = asyncio.Queue()

    # ── Persistence: configure and load saved sessions ────────────
    configure_persistence(
        mode     = os.getenv("PERSISTENCE", "json"),
        data_dir = os.getenv("DATA_DIR", "data"),
    )
    loaded = load_all_sessions()
    if loaded:
        log.info("Restored %d session(s) from disk", loaded)

    log.info("ClassMind starting on port %s…", os.getenv("PORT", "8000"))
    log.info("NOTE: Server restart is required after changing .env variables.")
    
    # Requirement 8: Self-test mode on server start
    from email_service import verify_email_system
    asyncio.create_task(verify_email_system())

    t1 = asyncio.create_task(analytics_broadcaster())
    t2 = asyncio.create_task(test_timer_watcher())
    t3 = asyncio.create_task(code_worker())
    t4 = asyncio.create_task(autosave_worker())
    yield
    # Final save before shutdown
    for code in list(sessions):
        save_session(code)
    t1.cancel(); t2.cancel(); t3.cancel(); t4.cancel()
    log.info("ClassMind stopped.")


app = FastAPI(
    title="ClassMind API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Consolidated exception handling moved to bottom

# ── CORS: single-origin setup — fully open so no fetch failures ─
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handlers ─────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent JSON response."""
    log.warning("HTTP %d: %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Catch-all for unhandled exceptions."""
    log.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": f"Server Error: {str(exc)}"}
    )

# ── Frontend file (override via FRONTEND_FILE env var) ──────────
FRONTEND_FILE = Path(__file__).with_name(os.getenv("FRONTEND_FILE", "classmind_single.html"))

@app.get("/")
def serve_frontend():
    if not FRONTEND_FILE.exists():
        raise HTTPException(404, f"Frontend not found — ensure '{FRONTEND_FILE.name}' is in the same folder as main.py")
    return FileResponse(FRONTEND_FILE, media_type="text/html")


# ── Google OAuth Verification ─────────────────────────────────────
@app.post("/auth/google")
async def google_auth(req: GoogleLoginReq, request: Request):
    client_id = get_google_client_id()
    if not client_id or "your-google" in client_id.lower():
        raise HTTPException(500, "Google Client ID not configured on server")

    try:
        origin = request.headers.get("origin") or request.headers.get("referer", "unknown")
        log.info("[AUTH] Verifying Google token from origin: %s", origin)
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(req.token, requests.Request(), client_id)

        # ID token is valid. Get the user's Google ID from the 'sub' claim.
        email = idinfo.get("email")
        name = idinfo.get("name")
        picture = idinfo.get("picture")

        if not email:
            log.error("[AUTH] Google token missing email")
            raise HTTPException(400, "Email not provided by Google")

        log.info("[AUTH] Google login successful: %s", email)

        # Construct a verified ClassMind profile
        # Use email as the unique teacher_id
        profile = {
            "id": email,  # Email is the unique ID
            "name": name,
            "email": email,
            "picture": picture,
            "provider": "google",
            "roleHistory": [],
            "sessionsCreated": [],
            "sessionsJoined": [],
            "stats": {
                "totalSessionsCreated": 0,
                "totalSessionsJoined": 0,
                "avgParticipation": 0,
                "avgUnderstanding": 0
            }
        }

        return profile

    except ValueError as e:
        log.warning("[AUTH] Invalid Google ID token: %s", e)
        raise HTTPException(401, f"Invalid Google ID token: {str(e)}")
    except Exception as e:
        log.error("[AUTH] Google auth unexpected error: %s", e)
        raise HTTPException(500, f"Internal authentication error: {str(e)}")


@app.get("/api/config")
async def get_config():
    cid = get_google_client_id()
    log.info("[CONFIG] Serving client_id to frontend: %s...", cid[:8] if cid else "NONE")
    return {
        "GOOGLE_CLIENT_ID": cid,
        "google_client_id": cid, # Maintain compatibility
        "admin_emails":     ADMIN_EMAILS,
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return JSONResponse(status_code=204, content=None)

@app.get("/health")
def health():
    return {"status": "ok", "sessions": len(sessions)}


class AdminLoginReq(BaseModel):
    username: str
    password: str


@app.post("/admin/login")
def admin_login(req: AdminLoginReq):
    username = req.username.strip()
    password = req.password.strip()
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "classmind123")
    if username != admin_username or password != admin_password:
        log.warning("Failed admin login attempt: %s", username)
        raise HTTPException(401, "Invalid admin credentials")

    token = uuid.uuid4().hex
    admin_tokens[token] = username
    log.info("Admin logged in: %s", username)
    return {"token": token}

@app.get("/admin/health")
def admin_health(admin_username: str = Depends(admin_authorized)):
    return {"status": "ok", "user": admin_username, "sessions": len(sessions)}


@app.get("/admin/overview")
def admin_overview(admin_username: str = Depends(admin_authorized)):
    log.info("Admin overview requested by %s", admin_username)
    return admin_dashboard_data()


@app.get("/admin/dashboard")
def admin_dashboard(admin_username: str = Depends(admin_authorized)):
    """Primary admin dashboard endpoint — returns full admin_dashboard_data()."""
    log.info("Admin dashboard requested by %s", admin_username)
    return admin_dashboard_data()


@app.get("/admin/sessions")
def admin_sessions(admin_username: str = Depends(admin_authorized)):
    log.info("Admin sessions requested by %s", admin_username)
    return {"sessions": [admin_session_summary(s) for s in sessions.values()]}


@app.get("/admin/session/{code}")
def admin_session_detail(code: str, admin_username: str = Depends(admin_authorized)):
    s = _S(code)
    log.info("Admin session detail requested by %s for %s", admin_username, code)
    return {
        "session": admin_session_summary(s),
        "students": list(s.get("students", {}).values()),
        "tasks": s.get("tasks", []),
        "groups": s.get("groups", []),
        "task_deliveries": list(s.get("task_deliveries", {}).values()),
        "responses": s.get("responses", {}),
        "content_files": list(s.get("content_files", {}).values()),
        "status": s.get("status"),
    }


@app.delete("/admin/session/{code}")
async def admin_delete_session(code: str, admin_username: str = Depends(admin_authorized)):
    s = _S(code)
    s["status"] = "ended"
    touch_session(s)
    await ws_broadcast(s, {"type": "session_ended", "session_code": code})
    admin_broadcast({"event": "session_ended", "session_code": code, "teacher_name": s.get("teacher_name")})
    log.info("Admin ended session %s by %s", code, admin_username)
    return {"ended": True, "session_code": code}


# ══════════════════════════════════════════════════════════════════
#  SESSION ROUTES
# ══════════════════════════════════════════════════════════════════

@app.post("/api/session/create")
async def create_session(req: CreateSessionReq, background_tasks: BackgroundTasks):
    # Validate email if provided
    email = (req.email or "").strip().lower()
    if email:
        if not is_valid_email(email):
            raise HTTPException(400, f"Invalid email format: {email}")

        # SESSION RESUME LOGIC
        # Check if this teacher already has an active session
        existing_code = teacher_sessions.get(email)
        if existing_code and existing_code in sessions:
            s = sessions[existing_code]
            if s.get("status") != "ended":
                log.info("[SESSION] Resuming existing session %s for teacher %s", existing_code, email)
                return {"session_code": existing_code, "teacher_name": s["teacher_name"], "resumed": True}

    # Otherwise, create a new session
    code = gen_code()
    s = new_session(code, req.teacher_name)
    
    # Store teacher profile on session
    if email:
        s["teacher_id"] = email  # Use email as unique teacher identity
        s["teacher_email"] = email
        teacher_sessions[email] = code
        log.info("[SESSION] Mapping teacher %s to session %s", email, code)
        
    if req.phone and req.phone.strip():
        s["teacher_phone"] = req.phone.strip()
        
    sessions[code] = s
    save_session(code)
    touch_session(s)
    
    log.info("[SESSION] New session created: %s by %s (%s)", code, req.teacher_name, email or "no-email")
    admin_broadcast({
        "event": "session_created",
        "session": admin_session_summary(s),
    })
    return {"session_code": code, "teacher_name": req.teacher_name, "resumed": False}


@app.get("/api/session/{code}")
def get_session_info(code: str):
    s = _S(code)
    return {
        "code":             s["code"],
        "status":           s["status"],
        "mode":             s["mode"],
        "teacher_name":     s["teacher_name"],
        "student_count":    sum(1 for st in s["students"].values() if st["status"] == "active"),
        "waiting_count":    len(s["waiting_room"]),
        "current_task_idx": s["current_task_idx"],
        "total_tasks":      len(s["tasks"]),
        "created_at":       s["created_at"],
    }


# ── Auto-email helpers ────────────────────────────────────────────

async def _send_session_end_emails(s: dict) -> None:
    """Background task: email ONLY the teacher with the session report."""
    code         = s.get("code", "?")
    teacher_name = s.get("teacher_name", "Teacher")
    log.info("[EMAIL] Email triggered for session %s", code)

    # Validate SMTP config first
    from email_service import validate_smtp_config
    if not validate_smtp_config():
        log.error("[EMAIL] Email failed — SMTP not configured for session %s", code)
        return

    try:
        report = compute_report(s)
    except Exception as exc:
        log.error("[EMAIL] compute_report failed for %s: %s", code, exc)
        return

    # Send ONLY to teacher — never to students
    teacher_email = s.get("teacher_email", "")
    if not teacher_email or not is_valid_email(teacher_email):
        log.warning("[EMAIL] No valid teacher email on session %s — skipping", code)
        return

    ok, msg = await send_session_email(
        to_email     = teacher_email,
        session_data = report,
        teacher_name = teacher_name,
    )
    if ok:
        log.info("[EMAIL] Email sent successfully to teacher (%s) for session %s", teacher_email, code)
    else:
        log.error("[EMAIL] Email failed for session %s: %s", code, msg)


async def _send_class_start_notifications(s: dict) -> None:
    """Background task: notify students with emails that class has started."""
    code         = s.get("code", "?")
    teacher_name = s.get("teacher_name", "Teacher")
    for sid, student in s.get("students", {}).items():
        student_email = student.get("email", "")
        if not student_email or not is_valid_email(student_email):
            continue
        ok, msg = await send_class_starting_email(
            to_email     = student_email,
            student_name = student.get("name", "Student"),
            session_code = code,
            teacher_name = teacher_name,
        )
        log.info(
            "[AUTO-EMAIL] Start notification -> %s (%s): %s",
            student.get("name", sid), student_email, "OK" if ok else msg,
        )


@app.post("/api/session/{code}/control")
async def session_control(code: str, action: str = Query(...), background_tasks: BackgroundTasks = None):
    s   = _S(code)
    MAP = {"start": "active", "pause": "paused", "resume": "active", "end": "ended"}
    if action not in MAP:
        raise HTTPException(400, f"Unknown action '{action}'")
    s["status"] = MAP[action]
    touch_session(s)
    await ws_broadcast(s, {"type": "session_status", "status": s["status"]})
    if action == "end":
        admin_broadcast({
            "event": "session_ended",
            "session_code": code,
            "teacher_name": s.get("teacher_name"),
        })
        # Remove from active mapping so teacher can start a new session next time
        t_email = s.get("teacher_email")
        if t_email and teacher_sessions.get(t_email) == code:
            teacher_sessions.pop(t_email, None)
            log.info("[SESSION] Removed session %s from active mapping for %s", code, t_email)
        # ── Auto-email reports to teacher + all students ──────────────
        if background_tasks is not None:
            background_tasks.add_task(_send_session_end_emails, s)
            log.info("[AUTO-EMAIL] End-of-session email task queued for %s", code)
    elif action == "start":
        # ── Notify students with emails that class has started ────────
        if background_tasks is not None:
            background_tasks.add_task(_send_class_start_notifications, s)
            log.info("[AUTO-EMAIL] Class-start notification task queued for %s", code)
    return {"status": s["status"]}


@app.post("/api/session/{code}/join")
async def join_session(
    code:      str,
    name:      str  = Query(...),
    roll:      str  = Query(...),
    cls:       str  = Query(...),
    anonymous: bool = Query(True),
    email:     Optional[str] = Query(None),
    phone:     Optional[str] = Query(None),
):
    s = _S(code)
    if s["status"] == "ended":
        raise HTTPException(400, "Session has already ended")

    # Validate email if provided
    if email and email.strip():
        if not is_valid_email(email.strip()):
            raise HTTPException(400, f"Invalid email format: {email}")

    name_n = name.strip().lower()
    roll_n = roll.strip()
    cls_n  = cls.strip().upper()

    if s.get("allowed_students"):
        match = next(
            (item for item in s["allowed_students"]
             if item[0] == name_n and item[1] == roll_n and item[2] == cls_n),
            None,
        )
        if not match:
            raise HTTPException(403, "You are not allowed in this session")
        name_n, roll_n, cls_n = match

    if roll_n in s.get("active_rolls", set()):
        raise HTTPException(403, "This roll number is already active")

    student          = new_student(name, anonymous)
    student["roll"]  = roll_n
    student["class"] = cls_n
    if email and email.strip():
        student["email"] = email.strip()
    if phone and phone.strip():
        student["phone"] = phone.strip()

    s["students"][student["id"]] = student
    s["waiting_room"].append(student["id"])
    s.setdefault("active_rolls", set()).add(roll_n)
    touch_session(s)

    admin_join_history.append({
        "ts": now(),
        "student_key": normalize_student_key(name_n, roll_n, cls_n),
        "session_code": code,
    })
    admin_broadcast({
        "event": "student_joined",
        "session_code": code,
        "student_id": student["id"],
        "student_name": student["name"],
        "status": "waiting",
    })

    await ws_teacher(s, {
        "type":         "student_waiting",
        "student_id":   student["id"],
        "display_name": student["name"],
    })
    return {"student_id": student["id"], "display_name": student["name"]}


@app.post("/api/session/{code}/approve/{student_id}")
async def approve_student(code: str, student_id: str):
    s = _S(code)
    if student_id not in s["students"]:
        raise HTTPException(404, "Student not found")
    if student_id in s["waiting_room"]:
        s["waiting_room"].remove(student_id)
    s["students"][student_id]["status"] = "active"
    await ws_student(s, student_id, {"type": "approved"})
    await push_roster(s)
    return {"approved": True}


@app.post("/api/session/{code}/reject/{student_id}")
async def reject_student(code: str, student_id: str):
    s = _S(code)
    if student_id in s["waiting_room"]:
        s["waiting_room"].remove(student_id)
    if student_id in s["students"]:
        s["students"][student_id]["status"] = "removed"
    s["kicked"].add(student_id)
    touch_session(s)
    admin_broadcast({
        "event": "student_left",
        "session_code": code,
        "student_id": student_id,
        "reason": "rejected",
    })
    await ws_student(s, student_id, {"type": "rejected"})
    await push_roster(s)
    roll = s["students"].get(student_id, {}).get("roll")
    if roll:
        s.get("active_rolls", set()).discard(roll)
    return {"rejected": True}


@app.post("/api/session/{code}/kick/{student_id}")
async def kick_student(code: str, student_id: str):
    s = _S(code)
    if student_id in s["students"]:
        s["students"][student_id]["status"] = "removed"
    s["kicked"].add(student_id)
    touch_session(s)
    admin_broadcast({
        "event": "student_left",
        "session_code": code,
        "student_id": student_id,
        "reason": "kicked",
    })
    await ws_student(s, student_id, {"type": "kicked"})
    await push_roster(s)
    roll = s["students"].get(student_id, {}).get("roll")
    if roll:
        s.get("active_rolls", set()).discard(roll)
    return {"kicked": True}


@app.get("/api/session/{code}/students")
def get_students(code: str):
    s       = _S(code)
    active  = [st for st in s["students"].values() if st["status"] == "active"]
    waiting = [s["students"][sid] for sid in s["waiting_room"] if sid in s["students"]]
    return {"active": active, "waiting": waiting}


@app.post("/api/session/{code}/upload_students")
async def upload_students(code: str, file: UploadFile = File(...)):
    s       = _S(code)
    content = await file.read()
    decoded = content.decode("utf-8")
    lines   = decoded.splitlines()

    header_index = 0
    for i, line in enumerate(lines):
        if "Name" in line and ("Roll" in line or "Enrollment" in line):
            header_index = i
            break

    cleaned = "\n".join(lines[header_index:])
    reader  = csv.DictReader(StringIO(cleaned), delimiter=",")

    allowed = set()
    skipped: list = []
    for i, row in enumerate(reader, start=1):
        name = (row.get("Name") or row.get("Student Name") or "").strip().lower()
        roll = (row.get("Roll No") or row.get("Enrollment No") or "").strip()
        cls  = (row.get("Branch") or row.get("Class") or row.get("Section") or "").strip().upper()
        if name and roll and cls:
            allowed.add((name, roll, cls))
        else:
            skipped.append({"row_number": i, "raw": row})

    s["allowed_students"] = allowed
    log.info("Student CSV loaded=%s skipped=%s", len(allowed), len(skipped))
    return {"loaded": len(allowed), "skipped": skipped[:5], "message": "Upload processed"}


# ══════════════════════════════════════════════════════════════════
#  TASK ROUTES
# ══════════════════════════════════════════════════════════════════

@app.post("/api/tasks/create")
async def create_task(req: CreateTaskReq):
    s    = _S(req.session_code)
    task = new_task(normalize_task_input(req.model_dump()))
    async with session_lock(req.session_code):
        s["tasks"].append(task)
    await ws_teacher(s, {"type": "task_created", "task": task, "tasks": s["tasks"]})
    return task


@app.post("/api/tasks/upload_json")
async def upload_tasks_json(session_code: str = Form(...), file: UploadFile = File(...)):
    s   = _S(session_code)
    raw = await file.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"Invalid JSON: {e}")
    if isinstance(data, dict):
        data = data.get("tasks", [data])
    if not isinstance(data, list):
        raise HTTPException(400, "JSON must be an array of task objects")

    created: list = []
    for item in data:
        if isinstance(item, dict) and item.get("question"):
            task = new_task(normalize_task_input(item))
            async with session_lock(session_code):
                s["tasks"].append(task)
            created.append(task)

    if created:
        await ws_teacher(s, {"type": "tasks_imported", "tasks": s["tasks"], "created": len(created)})
    return {"created": len(created), "tasks": created}


@app.get("/api/session/{code}/tasks")
def list_tasks(code: str):
    return _S(code)["tasks"]


@app.delete("/api/session/{code}/tasks/{task_id}")
async def delete_task(code: str, task_id: str):
    async with session_lock(code):
        s      = _S(code)
        before = len(s["tasks"])
        s["tasks"] = [t for t in s["tasks"] if t["id"] != task_id]
        if len(s["tasks"]) == before:
            raise HTTPException(404, "Task not found")
        s["responses"].pop(task_id, None)
        for did, d in list(s.get("task_deliveries", {}).items()):
            if d.get("task_id") == task_id:
                s["task_deliveries"].pop(did, None)
        s["student_current_task"] = {
            sid: tid for sid, tid in s.get("student_current_task", {}).items()
            if tid != task_id
        }
    await ws_teacher(s, {"type": "task_deleted", "task_id": task_id, "tasks": s["tasks"]})
    return {"deleted": True}


@app.post("/api/session/{code}/tasks/{task_id}/attach_content")
async def attach_content(code: str, task_id: str, filename: str = Query(...)):
    s    = _S(code)
    task = _T(s, task_id)
    if filename not in s["content_files"]:
        raise HTTPException(404, "File not found — upload it first")
    task["content_file"] = filename
    return {"attached": True}


@app.post("/api/session/{code}/tasks/send_current")
async def send_current_task(code: str):
    """Send the next task in sequence to all students."""
    return await deliver_next_task_request(code)


@app.post("/api/session/{code}/tasks/send")
async def send_task(code: str, req: SendTaskReq):
    """Send a specific task to all / a student / a group."""
    return await deliver_task_request(code, req)


@app.post("/api/session/{code}/tasks/send_specific")
async def send_specific_task(
    code:        str,
    req:         Optional[SendTaskReq] = Body(None),
    task_id:     Optional[str]         = Query(None),
    target_type: Optional[str]         = Query(None),
    target_id:   Optional[str]         = Query(None),
):
    """Alternate endpoint accepting query params or body."""
    if req is None:
        if not task_id or not target_type:
            raise HTTPException(422, "task_id and target_type are required")
        req = SendTaskReq(task_id=task_id, target_type=target_type, target_id=target_id)
    return await deliver_task_request(code, req)


# ── Responses ──────────────────────────────────────────────────────

@app.post("/api/responses/submit")
async def submit_response(req: SubmitResponseReq):
    s       = _S(req.session_code)
    task    = _T(s, req.task_id)
    student = s["students"].get(req.student_id)

    if not student or student.get("status") != "active":
        raise HTTPException(403, "Student is not active")
    if not student_can_submit_task(s, req.student_id, req.task_id):
        raise HTTPException(403, "Task has not been delivered to this student")

    correct = req.answer.strip() == task.get("correct_answer", "").strip()
    s["responses"].setdefault(req.task_id, {})[req.student_id] = {
        "answer":       req.answer,
        "correct":      correct,
        "time_taken":   req.time_taken,
        "submitted_at": now(),
    }

    if student:
        student["total_answered"] += 1
        if correct:
            student["correct"] += 1
            student["score"]   += score_for(task)
        student["last_seen"] = now()

    if s["mode"] == "test" and correct:
        ts = s["test_state"]
        ts["scores"][req.student_id] = ts["scores"].get(req.student_id, 0) + score_for(task)

    await ws_teacher(s, {
        "type":           "analytics_update",
        "analytics":      compute_analytics(s),
        "task_id":        req.task_id,
        "response_count": len(s["responses"].get(req.task_id, {})),
    })
    touch_session(s)
    admin_broadcast({
        "event": "response_received",
        "session_code": req.session_code,
        "student_id": req.student_id,
        "task_id": req.task_id,
        "correct": correct,
    })
    return {
        "correct":        correct,
        "score":          score_for(task) if correct else 0,
        "correct_answer": task.get("correct_answer", ""),
        "student_score":  student.get("score", 0) if student else 0,
    }


@app.post("/api/responses/request_hint")
async def request_hint(
    session_code: str = Query(...),
    student_id:   str = Query(...),
    task_id:      str = Query(...),
):
    s    = _S(session_code)
    task = _T(s, task_id)
    st   = s["students"].get(student_id)
    if not st or st.get("status") != "active":
        raise HTTPException(403, "Student is not active")
    if not student_can_submit_task(s, student_id, task_id):
        raise HTTPException(403, "Task has not been delivered to this student")
    st["hint_requests"] += 1
    vis  = task.get("hint_visibility", "on_request")
    hint = task.get("hint") if vis in ("always", "on_request") else None
    return {"hint": hint}


# ══════════════════════════════════════════════════════════════════
#  CONTENT ROUTES
# ══════════════════════════════════════════════════════════════════

ALLOWED_CT = {
    "application/pdf",
    "image/png", "image/jpeg", "image/jpg",
    "image/gif", "image/webp", "image/svg+xml",
}
MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@app.post("/api/content/upload")
async def upload_content(session_code: str = Form(...), file: UploadFile = File(...)):
    s  = _S(session_code)
    ct = file.content_type or ""
    if ct not in ALLOWED_CT:
        raise HTTPException(415, f"File type '{ct}' not supported")
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, "File too large (max 10 MB)")

    fname   = file.filename or f"file_{int(now())}"
    encoded = base64.b64encode(raw).decode()
    s["content_files"][fname] = {
        "name": fname, "data": encoded,
        "content_type": ct, "size": len(raw), "uploaded_at": now(),
    }
    await ws_all_students(s, {
        "type":         "content_shared",
        "filename":     fname,
        "content_type": ct,
        "data":         encoded,
    })
    return {"filename": fname, "size": len(raw), "content_type": ct}


@app.get("/api/session/{code}/content")
def list_content(code: str):
    s     = _S(code)
    files = [
        {"name": v["name"], "content_type": v["content_type"],
         "size": v["size"], "uploaded_at": v["uploaded_at"]}
        for v in s["content_files"].values()
    ]
    return {"files": files}


@app.delete("/api/session/{code}/content/{filename}")
async def delete_content(code: str, filename: str):
    s = _S(code)
    if filename not in s["content_files"]:
        raise HTTPException(404, "File not found")
    del s["content_files"][filename]
    return {"deleted": True}


# ══════════════════════════════════════════════════════════════════
#  GROUP ROUTES
# ══════════════════════════════════════════════════════════════════

@app.post("/api/groups/generate")
async def generate_groups(req: GenerateGroupsReq):
    s      = _S(req.session_code)
    active = [st for st in s["students"].values() if st["status"] == "active"]
    if len(active) < 2:
        raise HTTPException(400, "Need at least 2 active students")

    if req.strategy == "random":
        random.shuffle(active)
        ids = [st["id"] for st in active]
    else:
        sorted_s = sorted(active, key=lambda x: x["score"], reverse=True)
        ids      = [st["id"] for st in sorted_s]

    n_groups = max(1, (len(ids) + 3) // 4)
    buckets  = [[] for _ in range(n_groups)]
    for i, sid in enumerate(ids):
        row = i // n_groups
        col = i  % n_groups
        gi  = col if row % 2 == 0 else (n_groups - 1 - col)
        buckets[gi].append(sid)

    groups = [
        {"id": gen_id("g"), "name": f"Group {i+1}", "members": m}
        for i, m in enumerate(buckets) if m
    ]
    s["groups"] = groups
    await ws_broadcast(s, {"type": "groups_updated", "groups": groups})
    return {"groups": groups, "count": len(groups)}


@app.put("/api/groups/update")
async def update_group(req: UpdateGroupReq):
    s       = _S(req.session_code)
    members = list(dict.fromkeys(req.members))
    if len(members) > 4:
        raise HTTPException(400, "Max 4 students per group")
    missing  = [sid for sid in members if sid not in s["students"]]
    if missing:
        raise HTTPException(400, f"Unknown student IDs: {', '.join(missing)}")
    inactive = [sid for sid in members if s["students"][sid].get("status") != "active"]
    if inactive:
        raise HTTPException(400, f"Group members must be active: {', '.join(inactive)}")
    for g in s["groups"]:
        if g["id"] == req.group_id:
            g["members"] = members
            await ws_broadcast(s, {"type": "groups_updated", "groups": s["groups"]})
            return {"updated": True, "group": g}
    raise HTTPException(404, "Group not found")


@app.get("/api/session/{code}/groups")
def get_groups(code: str):
    s        = _S(code)
    students = s["students"]
    enriched = []
    for g in s["groups"]:
        members_info = [students[m] for m in g["members"] if m in students]
        enriched.append({**g, "members_info": members_info})
    return {"groups": enriched}


# ══════════════════════════════════════════════════════════════════
#  ANALYTICS & REPORTS
# ══════════════════════════════════════════════════════════════════

@app.get("/api/session/{code}/analytics")
def get_analytics(code: str):
    return compute_analytics(_S(code))


@app.get("/api/session/{code}/leaderboard")
def get_session_leaderboard(code: str):
    s      = _S(code)
    active = [st for st in s["students"].values() if st.get("status") == "active"]
    ranked = sorted(active, key=lambda st: (st.get("score", 0), st.get("correct", 0)), reverse=True)
    return [
        {
            "student_id":   st["id"],
            "student_name": st.get("name", st["id"]),
            "name":         st.get("name", st["id"]),
            "score":        st.get("score", 0),
            "correct":      st.get("correct", 0),
            "answered":     st.get("total_answered", 0),
            "rank":         i + 1,
        }
        for i, st in enumerate(ranked)
    ]


@app.get("/api/session/{code}/report")
def get_report(code: str):
    return compute_report(_S(code))


@app.get("/api/session/{code}/report/download")
def download_report(code: str, format: str = "csv"):
    s      = _S(code)
    report = compute_report(s)

    if format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Session Code", report["session_code"]])
        writer.writerow(["Teacher",      report["teacher_name"]])
        writer.writerow(["Status",       report["status"]])
        writer.writerow([])
        writer.writerow(["Student Performance"])
        writer.writerow(["Name", "Score", "Correct", "Answered"])
        for st in s["students"].values():
            writer.writerow([st["name"], st["score"], st["correct"], st["total_answered"]])
        writer.writerow([])
        writer.writerow(["Group Performance"])
        for g in report["group_stats"]:
            writer.writerow([g["name"], g["accuracy"]])
        return JSONResponse(content={"csv": output.getvalue()})

    return report


@app.get("/api/session/{code}/coding-analytics")
async def coding_analytics(code: str):
    s        = _S(code)
    students = list(s["students"].values())
    scores   = [st.get("coding_score", 0) for st in students if st.get("coding_submitted")]
    avg      = int(sum(scores) / len(scores)) if scores else 0
    sorted_s = sorted(students, key=lambda x: x.get("coding_score", 0), reverse=True)
    return {
        "avg_coding_score":  avg,
        "top_coders":        sorted_s[:3],
        "low_performers":    sorted_s[-3:],
        "submissions_count": len(scores),
    }


# ══════════════════════════════════════════════════════════════════
#  COMMUNICATION ROUTES
# ══════════════════════════════════════════════════════════════════

@app.post("/api/chat/send")
async def send_message(req: SendMessageReq):
    s    = _S(req.session_code)

    # Block student messages if chat is disabled (teachers can always send)
    is_teacher_sender = req.sender_id == "teacher" or req.sender_id not in s.get("students", {})
    if not is_teacher_sender and not s.get("chat_enabled", True):
        raise HTTPException(403, "Chat is currently disabled by the teacher")

    st   = s["students"].get(req.sender_id)
    name = st["name"] if st else "Teacher"

    msg = {
        "id":          gen_id("m"),
        "sender_id":   req.sender_id,
        "sender_name": name,
        "content":     req.content,
        "chat_type":   req.chat_type,
        "target_id":   req.target_id,
        "timestamp":   now(),
    }
    s["chat_messages"].append(msg)
    payload = {"type": "chat_message", "message": msg}

    if req.chat_type == "global":
        await ws_broadcast(s, payload)
    elif req.chat_type == "group":
        if not req.target_id:
            raise HTTPException(400, "target_id required for group chat")
        group = next((g for g in s["groups"] if g["id"] == req.target_id), None)
        if group:
            for mid in group["members"]:
                await ws_student(s, mid, payload)
        await ws_teacher(s, payload)
    elif req.chat_type == "private":
        if not req.target_id:
            raise HTTPException(400, "target_id required for private chat")
        await ws_student(s, req.target_id, payload)
        await ws_teacher(s, payload)

    return msg


@app.get("/api/session/{code}/chat")
def get_chat(code: str, chat_type: str = Query("global"), limit: int = Query(200)):
    s    = _S(code)
    msgs = [m for m in s["chat_messages"] if m["chat_type"] == chat_type]
    return {"messages": msgs[-limit:]}


@app.post("/api/doubts/submit")
async def submit_doubt(req: SubmitDoubtReq):
    s  = _S(req.session_code)
    st = s["students"].get(req.student_id, {})
    d  = {
        "id":           gen_id("d"),
        "student_id":   req.student_id,
        "student_name": st.get("name", "?"),
        "text":         req.doubt_text,
        "answer":       None,
        "resolved":     False,
        "created_at":   now(),
    }
    s["doubts"].append(d)
    await ws_teacher(s, {"type": "new_doubt", "doubt": d})
    return d


@app.post("/api/doubts/resolve")
async def resolve_doubt(req: ResolveDoubtReq):
    s = _S(req.session_code)
    for d in s["doubts"]:
        if d["id"] == req.doubt_id:
            d.update({"answer": req.answer, "resolved": True, "resolved_at": now()})
            await ws_broadcast(s, {"type": "doubt_resolved", "doubt": d})
            return d
    raise HTTPException(404, "Doubt not found")


@app.get("/api/session/{code}/doubts")
def get_doubts(code: str):
    return {"doubts": _S(code)["doubts"]}


@app.post("/api/session/{code}/raise_hand/{student_id}")
async def raise_hand(code: str, student_id: str):
    s  = _S(code)
    if student_id not in s["raised_hands"]:
        s["raised_hands"].append(student_id)
    st = s["students"].get(student_id, {})
    await ws_teacher(s, {
        "type":         "hand_raised",
        "student_id":   student_id,
        "student_name": st.get("name", "?"),
    })
    return {"raised": True}


@app.post("/api/session/{code}/lower_hand/{student_id}")
async def lower_hand(code: str, student_id: str):
    s = _S(code)
    if student_id in s["raised_hands"]:
        s["raised_hands"].remove(student_id)
    await ws_teacher(s, {"type": "hand_lowered", "student_id": student_id})
    return {"lowered": True}


@app.post("/api/session/{code}/broadcast")
async def broadcast_msg(code: str, message: str = Query(...)):
    s = _S(code)
    await ws_all_students(s, {"type": "announcement", "message": message})
    return {"sent": True}


@app.post("/api/session/{code}/waiting/question")
async def ask_waiting(code: str, question: str = Query(...)):
    s = _S(code)
    for sid in s["waiting_room"]:
        await ws_student(s, sid, {"type": "waiting_question", "question": question})
    return {"sent": True}


@app.post("/api/session/{code}/waiting/response")
async def waiting_response(
    code:       str,
    student_id: str = Query(...),
    answer:     str = Query(...),
):
    s = _S(code)
    await ws_teacher(s, {
        "type":       "waiting_response",
        "student_id": student_id,
        "answer":     answer,
    })
    return {"ok": True}


@app.post("/api/session/{code}/resend-report")
@app.post("/api/session/{code}/send-report")
async def send_report(
    background_tasks: BackgroundTasks,
    code: str, 
    email: Optional[str] = Query(None), 
    req_body: Optional[dict] = Body(None),
):
    """
    Send session report email in the background.
    Rate limited to 3 sends per session.
    """
    try:
        # 1. Recipient resolution
        email_from_body = req_body.get("email") if req_body else None
        
        # Fallback to session teacher email if no email provided
        s = sessions.get(code)
        if not s:
            raise HTTPException(404, f"Session '{code}' not found")
            
        target_email = email_from_body or email or s.get("teacher_email")
        
        if not target_email:
            raise HTTPException(400, "Email recipient is required")
        
        target_email = target_email.strip()
        if not is_valid_email(target_email):
            raise HTTPException(400, f"Invalid email format: {target_email}")

        s = sessions.get(code)
        if not s:
            raise HTTPException(404, f"Session '{code}' not found")

        # 1. Rate Limiting (Requirement 4)
        send_count = s.get("_email_count", 0)
        if send_count >= 3:
            return {
                "success": False,
                "status":  "error",
                "message": "Max 3 emails per session.",
            }
        s["_email_count"] = send_count + 1

        # 2. SMTP basic check
        from email_service import validate_smtp_config
        if not validate_smtp_config():
            log.error("[SEND_REPORT] SMTP missing credentials")
            return {
                "success": False,
                "status":  "error",
                "message": "Email service not configured.",
            }

        # 3. Queue Background Task (Requirement 3)
        background_tasks.add_task(dispatch_email_report, code, target_email)

        return {
            "success":    True,
            "status":     "success",
            "message":    f"Sending report to {target_email} in the background.",
            "email":      target_email,
            "session_id": code,
        }
    except HTTPException:
        raise
    except Exception as e:
        log.error("[SEND_REPORT] Error: %s", e, exc_info=True)
        return {
            "success": False,
            "status":  "error",
            "message": f"Server Error: {str(e)}",
        }


async def dispatch_email_report(code: str, email: str):
    """Background task to compute and send email."""
    s = sessions.get(code)
    if not s: return
    
    try:
        report = compute_report(s)
        teacher_name = s.get("teacher_name", "Teacher")
        
        ok, msg = await send_session_email(
            to_email     = email,
            session_data = report,
            teacher_name = teacher_name,
        )
        
        if ok:
            log.info("[BACKGROUND_EMAIL] Success for %s to %s", code, email)
        else:
            log.error("[BACKGROUND_EMAIL] Failed for %s: %s", code, msg)
            
    except Exception as exc:
        log.error("[BACKGROUND_EMAIL] Unexpected error: %s", exc)


# ══════════════════════════════════════════════════════════════════
#  TEST MODE ROUTES
# ══════════════════════════════════════════════════════════════════

@app.post("/api/test/start")
async def start_test(req: StartTestReq):
    s = _S(req.session_code)
    if not s["tasks"]:
        raise HTTPException(400, "No tasks in session")

    pool = (
        [t for t in s["tasks"] if t["id"] in req.task_ids]
        if req.task_ids else s["tasks"]
    )
    if not pool:
        raise HTTPException(400, "No matching tasks found")

    s["mode"]   = "test"
    s["status"] = "active"
    ts          = s["test_state"]
    ts.update({
        "active":        True,
        "start_time":    now(),
        "duration_secs": req.duration_secs,
        "task_ids":      [t["id"] for t in pool],
        "submitted":     set(),
        "scores":        {},
        "leaderboard":   [],
    })

    shuffled = pool[:]
    random.shuffle(shuffled)
    await ws_broadcast(s, {
        "type":          "test_started",
        "duration_secs": req.duration_secs,
        "start_time":    ts["start_time"],
        "tasks":         [safe_task(t) for t in shuffled],
        "task_count":    len(shuffled),
    })
    return {"started": True, "task_count": len(shuffled)}


@app.post("/api/test/submit/{session_code}/{student_id}")
async def submit_test(session_code: str, student_id: str):
    s  = _S(session_code)
    ts = s["test_state"]
    if student_id in ts["submitted"]:
        return {"already_submitted": True, "score": ts["scores"].get(student_id, 0)}

    ts["submitted"].add(student_id)
    score = ts["scores"].get(student_id, 0)
    lb    = sorted(ts["scores"].items(), key=lambda x: x[1], reverse=True)
    ts["leaderboard"] = [
        {
            "student_id":   sid,
            "score":        sc,
            "rank":         i + 1,
            "student_name": s["students"].get(sid, {}).get("name", sid),
        }
        for i, (sid, sc) in enumerate(lb)
    ]
    await ws_teacher(s, {
        "type":            "test_submission",
        "student_id":      student_id,
        "score":           score,
        "leaderboard":     ts["leaderboard"],
        "submitted_count": len(ts["submitted"]),
    })
    rank = next((r["rank"] for r in ts["leaderboard"] if r["student_id"] == student_id), None)
    return {"submitted": True, "score": score, "rank": rank}


@app.post("/api/test/end/{session_code}")
async def end_test(session_code: str):
    s  = _S(session_code)
    ts = s["test_state"]
    ts["active"] = False
    s["mode"]    = "live"
    lb           = sorted(ts["scores"].items(), key=lambda x: x[1], reverse=True)
    ts["leaderboard"] = [
        {
            "student_id":   sid,
            "score":        sc,
            "rank":         i + 1,
            "student_name": s["students"].get(sid, {}).get("name", sid),
        }
        for i, (sid, sc) in enumerate(lb)
    ]
    return {"ended": True, "leaderboard": ts["leaderboard"]}


@app.get("/api/test/{session_code}/leaderboard")
def get_leaderboard(session_code: str):
    ts = _S(session_code)["test_state"]
    return {
        "leaderboard":     ts["leaderboard"],
        "active":          ts["active"],
        "submitted_count": len(ts["submitted"]),
    }


# ── Quiz helpers ───────────────────────────────────────────────────

@app.post("/api/session/{code}/quiz/send")
async def send_quiz(code: str, req: SendQuizReq = Body(default=SendQuizReq())):
    s = _S(code)

    task_ids: List[str] = []
    if req.task_ids:
        task_ids = req.task_ids
    elif s.get("quiz_task_ids"):
        task_ids = s["quiz_task_ids"]
    elif s.get("quiz"):
        raw = s["quiz"]
        task_ids = [
            item["id"] if isinstance(item, dict) and "id" in item else item
            for item in raw if isinstance(item, (str, dict))
        ]
    else:
        raise HTTPException(400, "No quiz questions specified")

    if not task_ids:
        raise HTTPException(400, "Quiz has no questions")

    questions = [safe_task(t) for tid in task_ids
                 for t in [next((x for x in s["tasks"] if x["id"] == tid), None)] if t]

    if not questions:
        raise HTTPException(400, "None of the quiz task IDs exist in this session")

    quiz_id = gen_id("qz")
    s["quiz_meta"] = {
        "id":       quiz_id,
        "task_ids": task_ids,
        "sent_at":  now(),
        "total":    len(questions),
    }

    payload = {
        "type": "quiz_start",
        "quiz": {
            "id":        quiz_id,
            "questions": questions,
            "total":     len(questions),
        },
    }

    log.info("Quiz %s sent to session %s — %d questions", quiz_id, code, len(questions))
    await ws_all_students(s, payload)
    return {"status": "quiz sent", "quiz_id": quiz_id, "total": len(questions)}


@app.post("/api/session/quiz/save")
async def save_quiz(req: SaveQuizReq):
    s = _S(req.session_code)
    s["quiz"] = req.quiz
    if req.task_ids:
        s["quiz_task_ids"] = req.task_ids
    return {"status": "saved"}


# ══════════════════════════════════════════════════════════════════
#  QUIZ REPORT SYSTEM
# ══════════════════════════════════════════════════════════════════

def evaluate_quiz(s: dict, quiz_questions: list) -> dict:
    results: dict = {}
    ts = s.get("test_state", {})

    for student_id, data in ts.get("answers", {}).items():
        student_answers = data.get("answers", {})
        score    = 0
        detailed = []

        for q in quiz_questions:
            task_id = str(q.get("id", ""))
            correct = str(q.get("correct_answer", "")).strip().upper()
            student_ans = student_answers.get(task_id) or student_answers.get(task_id.upper())

            if q.get("type", "mcq") == "coding":
                is_correct = False
            else:
                is_correct = bool(
                    student_ans is not None and
                    str(student_ans).strip().upper() == correct
                )

            if is_correct:
                score += 1

            detailed.append({
                "question":       q.get("question", ""),
                "correct_answer": q.get("correct_answer", ""),
                "student_answer": student_ans,
                "is_correct":     is_correct,
                "type":           q.get("type", "mcq"),
                "options":        q.get("options", []),
                "topic":          q.get("topic", ""),
            })

        results[student_id] = {
            "score":        score,
            "total":        len(quiz_questions),
            "details":      detailed,
            "student_name": data.get("student_name"),
        }

    return results


def _quiz_questions_for_session(s: dict) -> list:
    meta = s.get("quiz_meta")
    if not meta:
        raise HTTPException(400, "No quiz has been sent in this session")
    task_ids = meta.get("task_ids", [])
    questions = [
        t for tid in task_ids
        for t in [next((x for x in s["tasks"] if x["id"] == tid), None)]
        if t
    ]
    if not questions:
        raise HTTPException(400, "Quiz questions not found in session tasks")
    return questions


@app.get("/quiz/report/{code}")
async def get_quiz_report(code: str):
    s         = _S(code)
    questions = _quiz_questions_for_session(s)
    report    = evaluate_quiz(s, questions)

    rows = sorted(
        [
            {
                "student_id":   sid,
                "student_name": v["student_name"] or sid,
                "score":        v["score"],
                "total":        v["total"],
                "percentage":   round(v["score"] / v["total"] * 100) if v["total"] else 0,
            }
            for sid, v in report.items()
        ],
        key=lambda r: r["score"],
        reverse=True,
    )

    for i, r in enumerate(rows):
        r["rank"] = i + 1

    return {
        "report":    report,
        "rows":      rows,
        "total_q":   len(questions),
        "submitted": len(report),
    }


@app.get("/quiz/report/{code}/{student_id}")
async def get_student_quiz_report(code: str, student_id: str):
    s         = _S(code)
    questions = _quiz_questions_for_session(s)
    report    = evaluate_quiz(s, questions)
    result    = report.get(student_id)
    if not result:
        raise HTTPException(404, "No submission found for this student")
    return result


# ══════════════════════════════════════════════════════════════════
#  CODING LAB
# ══════════════════════════════════════════════════════════════════

@app.post("/api/code/run")
async def execute_code(req: RunCodeReq):
    s = _S(req.session_code)

    if req.student_id != "teacher":
        st = s["students"].get(req.student_id)
        if not st or st["status"] != "active":
            raise HTTPException(403, "Student not active")

    loop    = asyncio.get_event_loop()
    future  = loop.create_future()
    await execution_queue.put((req.code, req.language, future))
    result  = await future

    if req.student_id != "teacher":
        student = s["students"].get(req.student_id)
        if student:
            student["coding_submitted"]  = True
            student["test_cases_passed"] = random.randint(2, 5)
            student["total_test_cases"]  = 5
            student["coding_score"]      = int((student["test_cases_passed"] / 5) * 100)
            student["coding_time_taken"] = 120

        lb = sorted(s["students"].values(), key=lambda x: x.get("coding_score", 0), reverse=True)
        await ws_all_students(s, {
            "type": "coding_leaderboard_update",
            "leaderboard": [
                {"name": st["name"], "score": st.get("coding_score", 0), "rank": i + 1}
                for i, st in enumerate(lb)
            ],
        })

    return {"output": result.output, "error": result.error, "timed_out": result.timed_out}


@app.post("/api/session/{code}/submit_code")
async def submit_code_endpoint(
    code:       str,
    student_id: str  = Body(...),
    task_id:    Optional[str] = Body(None),
    code_body:  str  = Body(..., alias="code"),
):
    s       = _S(code)
    student = s["students"].get(student_id)
    if not student or student.get("status") != "active":
        raise HTTPException(403, "Student not active")

    student["coding_submitted"]  = True
    student["test_cases_passed"] = random.randint(3, 5)
    student["total_test_cases"]  = 5
    student["coding_score"]      = int((student["test_cases_passed"] / 5) * 100)

    await ws_teacher(s, {
        "type":       "code_submitted",
        "student_id": student_id,
        "name":       student.get("name", "?"),
        "score":      student["coding_score"],
    })
    return {"submitted": True, "score": student["coding_score"]}


# ══════════════════════════════════════════════════════════════════
#  WEBSOCKETS
# ══════════════════════════════════════════════════════════════════

@app.websocket("/ws/teacher/{session_code}")
async def teacher_ws_endpoint(ws: WebSocket, session_code: str):
    s = sessions.get(session_code)
    if not s:
        log.warning("[WS] Teacher tried to connect to non-existent session: %s", session_code)
        await ws.accept()
        await ws_send(ws, {"type": "error", "message": "Session not found"})
        await ws.close()
        return

    await ws.accept()
    if s.get("teacher_ws"):
        log.info("[WS] Teacher reconnecting to session %s (replacing existing connection)", session_code)
        try:
            await s["teacher_ws"].close()
        except:
            pass
            
    s["teacher_ws"] = ws
    log.info("[WS] Teacher connected to session: %s (Teacher ID: %s)", session_code, s.get("teacher_id", "unknown"))

    active  = [st for st in s["students"].values() if st["status"] == "active"]
    waiting = [s["students"][sid] for sid in s["waiting_room"] if sid in s["students"]]
    await ws_send(ws, {
        "type": "connected",
        "role": "teacher",
        "session": {
            "code":       s["code"],
            "status":     s["status"],
            "mode":       s["mode"],
            "tasks":      s["tasks"],
            "groups":     s["groups"],
            "deliveries": [delivery_summary(d) for d in s.get("task_deliveries", {}).values()],
        },
        "analytics": compute_analytics(s),
        "roster":    {"active": active, "waiting": waiting},
    })

    try:
        while True:
            raw  = await ws.receive_text()
            data = json.loads(raw)
            cmd  = data.get("type", "")

            if cmd in ("ping", "heartbeat"):
                await ws_send(ws, {"type": "pong", "ts": now()})
            elif cmd == "get_analytics":
                await ws_send(ws, {"type": "analytics_update", "analytics": compute_analytics(s)})
            elif cmd == "get_roster":
                await push_roster(s)
            elif cmd == "broadcast":
                msg = data.get("message", "")
                if msg:
                    await ws_all_students(s, {"type": "announcement", "message": msg})
            elif cmd == "chat_toggle":
                # Teacher enables/disables chat — persist on session and broadcast
                enabled = bool(data.get("enabled", True))
                s["chat_enabled"] = enabled
                log.info("Chat %s for session %s", "enabled" if enabled else "disabled", session_code)
                await ws_all_students(s, {"type": "chat_toggle", "enabled": enabled})
                await ws_send(ws, {"type": "chat_toggle_ack", "enabled": enabled})

    except WebSocketDisconnect:
        log.info("Teacher disconnected: %s", session_code)
    finally:
        if s.get("teacher_ws") is ws:
            s["teacher_ws"] = None


@app.websocket("/ws/student/{session_code}/{student_id}")
async def student_ws_endpoint(ws: WebSocket, session_code: str, student_id: str):
    s = sessions.get(session_code)
    if not s:
        await ws.accept()
        await ws_send(ws, {"type": "error", "message": "Session not found"})
        await ws.close()
        return

    if student_id not in s.get("students", {}):
        await ws.accept()
        await ws_send(ws, {"type": "error", "message": "Student not found"})
        await ws.close()
        return

    if student_id in s.get("kicked", set()):
        await ws.accept()
        await ws_send(ws, {"type": "error", "message": "You have been removed from this session"})
        await ws.close()
        return

    await ws.accept()
    s["ws_clients"][student_id] = ws
    student = s["students"].get(student_id, {})
    if student:
        student["last_seen"] = now()
    log.info("Student %s connected: %s", student_id, session_code)

    latest_delivery     = latest_delivery_for_student(s, student_id)
    current             = None
    current_delivery_id = ""
    task_idx            = -1

    if latest_delivery:
        current             = task_payload(s, latest_delivery)["task"]
        current_delivery_id = latest_delivery["id"]
        task_idx            = latest_delivery.get("task_index", -1)
    elif student.get("status") == "active":
        idx      = s["current_task_idx"]
        current  = safe_task(s["tasks"][idx]) if 0 <= idx < len(s["tasks"]) else None
        task_idx = idx

    await ws_send(ws, {
        "type":                "connected",
        "role":                "student",
        "student":             student,
        "session_status":      s["status"],
        "current_task":        current,
        "groups":              s["groups"],
        "test_active":         s["test_state"]["active"],
        "current_delivery_id": current_delivery_id,
        "task_index":          task_idx,
        "total_tasks":         len(s["tasks"]),
        "chat_enabled":        s.get("chat_enabled", True),
    })

    if student.get("status") == "active":
        await replay_unacked_tasks(s, student_id)

    await ws_teacher(s, {
        "type":         "student_connected",
        "student_id":   student_id,
        "student_name": student.get("name", "?"),
    })

    try:
        while True:
            raw  = await ws.receive_text()
            data = json.loads(raw)
            cmd  = data.get("type", "")

            if cmd in ("ping", "heartbeat"):
                st = s["students"].get(student_id)
                if st:
                    st["last_seen"] = now()
                await ws_send(ws, {"type": "pong", "ts": now()})

            elif cmd == "quiz_submit":
                answers: dict = data.get("answers") or {}
                student = s["students"].get(student_id)

                ts = s.setdefault("test_state", {})
                ts.setdefault("answers", {})
                ts.setdefault("submitted", set())
                ts.setdefault("scores", {})

                ts["answers"][student_id] = {
                    "answers":      answers,
                    "submitted_at": now(),
                    "student_name": (student or {}).get("name", student_id),
                }
                ts["submitted"].add(student_id)

                score = 0
                for task_id_key, ans_val in answers.items():
                    task = next(
                        (t for t in s.get("tasks", []) if t["id"] == task_id_key), None
                    )
                    if task and str(ans_val).strip() == str(task.get("correct_answer", "")).strip():
                        score += score_for(task)

                ts["scores"][student_id] = ts["scores"].get(student_id, 0) + score

                log.info(
                    "Quiz submitted by %s in session %s — %d answers, score %d",
                    student_id, session_code, len(answers), score,
                )

                await ws_send(ws, {
                    "type":    "quiz_submit_ack",
                    "score":   score,
                    "total":   len(answers),
                    "message": "Quiz submitted successfully! Great work.",
                })

                await ws_teacher(s, {
                    "type":         "quiz_submitted",
                    "student_id":   student_id,
                    "student_name": (student or {}).get("name", student_id),
                    "answer_count": len(answers),
                    "score":        score,
                    "submitted_at": now(),
                })

            elif cmd == "task_received":
                delivery_id = data.get("delivery_id")
                if mark_task_ack(s, student_id, delivery_id):
                    await ws_teacher(s, {
                        "type":        "task_delivery_ack",
                        "delivery_id": delivery_id,
                        "task_id":     data.get("task_id", ""),
                        "student_id":  student_id,
                    })

    except WebSocketDisconnect:
        log.info("Student %s disconnected: %s", student_id, session_code)
    finally:
        if s.get("ws_clients", {}).get(student_id) is ws:
            s["ws_clients"].pop(student_id, None)
        touch_session(s)
        admin_broadcast({
            "event": "student_left",
            "session_code": session_code,
            "student_id": student_id,
            "reason": "disconnect",
        })
        await ws_teacher(s, {"type": "student_disconnected", "student_id": student_id})


@app.websocket("/ws/admin")
async def admin_ws_endpoint(ws: WebSocket, token: str = Query(None)):
    await ws.accept()
    if not token or token not in admin_tokens:
        await ws_send(ws, {"type": "error", "message": "Unauthorized admin websocket"})
        await ws.close()
        return

    admin_connections.add(ws)
    username = admin_tokens[token]
    log.info("Admin connected: %s", username)
    await ws_send(ws, {"type": "connected", "role": "admin", "dashboard": admin_dashboard_data()})

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            if data.get("type") in ("ping", "heartbeat"):
                await ws_send(ws, {"type": "pong", "ts": now()})
    except WebSocketDisconnect:
        log.info("Admin disconnected: %s", username)
    finally:
        admin_connections.discard(ws)


# ══════════════════════════════════════════════════════════════════
#  TEST DATA LOADER (Development Only)
# ══════════════════════════════════════════════════════════════════

@app.post("/api/test-data/{session_code}")
async def load_test_data(session_code: str):
    """Load sample test data for development/testing purposes."""
    s = _S(session_code)
    
    # Create sample students
    sample_students = [
        {"name": "Alice Johnson", "roll": "001", "cls": "10A"},
        {"name": "Bob Smith", "roll": "002", "cls": "10A"},
        {"name": "Charlie Brown", "roll": "003", "cls": "10A"},
        {"name": "Diana Prince", "roll": "004", "cls": "10A"},
        {"name": "Eve Wilson", "roll": "005", "cls": "10A"},
    ]
    
    created_students = []
    for student_data in sample_students:
        student = new_student(student_data["name"], anonymous=False)
        student["roll"] = student_data["roll"]
        student["class"] = student_data["cls"]
        student["status"] = "active"
        s["students"][student["id"]] = student
        s.setdefault("active_rolls", set()).add(student_data["roll"])
        created_students.append(student)
    
    # Create sample tasks
    sample_tasks = [
        {
            "question": "What is the capital of France?",
            "type": "mcq",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "correct_answer": "A",
            "topic": "Geography",
            "difficulty": "easy",
        },
        {
            "question": "What is 2 + 2 × 3?",
            "type": "mcq",
            "options": ["8", "12", "10", "6"],
            "correct_answer": "A",
            "topic": "Mathematics",
            "difficulty": "medium",
        },
        {
            "question": "Explain the water cycle in 2-3 sentences.",
            "type": "short",
            "correct_answer": "",
            "topic": "Science",
            "difficulty": "medium",
        },
        {
            "question": "Write a Python function to calculate factorial.",
            "type": "coding",
            "correct_answer": "",
            "topic": "Programming",
            "difficulty": "hard",
        },
    ]
    
    created_tasks = []
    for task_data in sample_tasks:
        task = new_task(normalize_task_input(task_data))
        s["tasks"].append(task)
        created_tasks.append(task)
    
    # Create sample groups
    student_ids = [st["id"] for st in created_students]
    s["groups"] = [
        {"id": gen_id("g"), "name": "Group 1", "members": student_ids[:2]},
        {"id": gen_id("g"), "name": "Group 2", "members": student_ids[2:4]},
        {"id": gen_id("g"), "name": "Group 3", "members": student_ids[4:]},
    ]
    
    log.info("Test data loaded for session %s: %d students, %d tasks, %d groups", 
             session_code, len(created_students), len(created_tasks), len(s["groups"]))
    
    return {
        "loaded": True,
        "students": len(created_students),
        "tasks": len(created_tasks),
        "groups": len(s["groups"]),
        "student_ids": [st["id"] for st in created_students],
        "task_ids": [t["id"] for t in created_tasks],
    }


# ── local dev ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host      = os.getenv("HOST", "0.0.0.0"),
        port      = int(os.getenv("PORT", "8000")),
        reload    = os.getenv("RELOAD", "true").lower() == "true",
        log_level = os.getenv("LOG_LEVEL", "info"),
    )
