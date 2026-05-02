"""
analytics.py  —  ClassMind analytics engine
Pure functions only — no FastAPI/WebSocket imports.
"""
from __future__ import annotations
import time
from typing import Dict, List


# ─────────────────────── LIVE SNAPSHOT ───────────────────────────

def compute_analytics(session: dict) -> dict:
    """
    Lightweight snapshot pushed to teacher every 2 seconds.
    Returns understanding%, participation%, at_risk list, topic_confusion.
    """
    active = [s for s in session["students"].values() if s["status"] == "active"]
    total  = len(active)

    if total == 0:
        return {
            "understanding": 0, "participation": 0,
            "at_risk": [], "topic_confusion": {},
            "total_students": 0, "answered": 0,
        }

    answered_students = [s for s in active if s["total_answered"] > 0]
    participation     = round(len(answered_students) / total * 100)

    all_correct  = sum(s["correct"]        for s in active)
    all_answered = sum(s["total_answered"] for s in active)
    understanding = round(all_correct / all_answered * 100) if all_answered else 0

    at_risk = [
        {"id": s["id"], "name": s["name"]} for s in active
        if s["total_answered"] > 0 and (s["correct"] / s["total_answered"]) < 0.40
    ]

    return {
        "understanding":   understanding,
        "participation":   participation,
        "at_risk":         at_risk,
        "topic_confusion": _topic_confusion(session),
        "total_students":  total,
        "answered":        len(answered_students),
    }


def _topic_confusion(session: dict) -> Dict[str, dict]:
    result: Dict[str, dict] = {}
    for task in session["tasks"]:
        topic       = task.get("topic", "General")
        correct_ans = task.get("correct_answer", "")
        responses   = session["responses"].get(task["id"], {})

        if topic not in result:
            result[topic] = {"wrong": 0, "total": 0}

        for r in responses.values():
            result[topic]["total"] += 1
            if r.get("answer") != correct_ans:
                result[topic]["wrong"] += 1
    return result


# ─────────────────────── FULL REPORT ─────────────────────────────

def compute_report(session: dict) -> dict:
    """
    Full report — only called from Reports page, not pushed in real-time.
    """
    # ── Feature 3: coding performance summary ────────────────────────
    _students = list(session["students"].values())
    coding_scores = [s.get("coding_score", 0) for s in _students if s.get("coding_submitted")]
    coding_avg = int(sum(coding_scores) / len(coding_scores)) if coding_scores else 0
    top_coder  = max(_students, key=lambda x: x.get("coding_score", 0), default=None)

    return {
        "session_code":   session["code"],
        "teacher_name":   session["teacher_name"],
        "analytics":      compute_analytics(session),
        "question_stats": _question_stats(session),
        "group_stats":    _group_stats(session),
        "leaderboard":    session["test_state"].get("leaderboard", []),
        "total_tasks":    len(session["tasks"]),
        "duration_secs":  round(time.time() - (session.get("created_at") or time.time())),
        "status":         session["status"],
        "students":       _student_reports(session),
        # ── new ──────────────────────────────────────────────────────
        "coding_summary": {
            "avg_score":  coding_avg,
            "top_coder":  top_coder,
        },
    }


def _question_stats(session: dict) -> List[dict]:
    stats = []
    for i, task in enumerate(session["tasks"]):
        responses   = session["responses"].get(task["id"], {})
        total_resp  = len(responses)
        correct_ans = task.get("correct_answer", "")
        correct_cnt = sum(1 for r in responses.values() if r.get("answer") == correct_ans)

        # MCQ option frequency map
        option_freq: Dict[str, int] = {}
        if task.get("type") == "mcq":
            for r in responses.values():
                ans = r.get("answer", "?")
                option_freq[ans] = option_freq.get(ans, 0) + 1

        # Hint requests for this task specifically
        hint_reqs = sum(
            s.get("hint_requests", 0)
            for s in session["students"].values()
        )

        stats.append({
            "index":           i + 1,
            "task_id":         task["id"],
            "question":        task.get("question", ""),
            "type":            task.get("type", "mcq"),
            "topic":           task.get("topic", ""),
            "difficulty":      task.get("difficulty", ""),
            "total_responses": total_resp,
            "correct":         correct_cnt,
            "accuracy":        round(correct_cnt / total_resp * 100) if total_resp else 0,
            "option_freq":     option_freq,
            "hint_requests":   hint_reqs,
        })
    return stats


def _group_stats(session: dict) -> List[dict]:
    students = session["students"]
    stats    = []
    for g in session["groups"]:
        members  = [students[m] for m in g.get("members", []) if m in students]
        scores   = [m["score"]          for m in members]
        corrects = [m["correct"]        for m in members]
        answered = [m["total_answered"] for m in members]
        total_ans = sum(answered)
        stats.append({
    "id":        g["id"],
    "name":      g["name"],
    "members":   g.get("members", []),

    "avg_score": round(sum(scores) / len(scores)) if scores else 0,

    "accuracy":  round(sum(corrects) / total_ans * 100) if total_ans else 0,

    "participation": (
        round(len([m for m in members if m["total_answered"] > 0]) / len(members) * 100)
        if members else 0
    ),
})
    return stats
def _student_reports(session: dict) -> List[dict]:
    result = []

    for sid, student in session["students"].items():
        attempts = []

        for task in session["tasks"]:
            task_id = task["id"]
            response = session["responses"].get(task_id, {}).get(sid)

            if not response:
                continue

            attempts.append({
                "question": task.get("question", ""),
                "your_answer": response.get("answer"),
                "correct_answer": task.get("correct_answer"),
                "is_correct": response.get("answer") == task.get("correct_answer"),
                "topic": task.get("topic", ""),
            })

        result.append({
            "student_id": sid,
            "name": student.get("name"),
            "total_attempts": len(attempts),
            "correct": sum(1 for a in attempts if a["is_correct"]),
            "attempts": attempts
        })

    return result