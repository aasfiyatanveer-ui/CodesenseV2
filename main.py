"""
main.py — CodeSense V2
ML-Powered Code Review API with Gamification + Multi-language + Groq/Ollama AI
"""

import json
import subprocess, sys, tempfile, os
from datetime import datetime, date

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from database import create_tables, get_db, User, Review, FixHistory, AskHistory
from auth import hash_password, verify_password, create_access_token, get_current_user
from feature_extractor import extract_features
from ml_model import predict_quality
from complexity_analyzer import analyze_complexity
from code_fixer import fix_code
from code_enhancer import enhance_code
import ai_service
from gamification import (
    get_level, calculate_xp_for_action, check_new_badges,
    get_badge_info, calculate_streak, BADGE_DEFS
)

app = FastAPI(title="CodeSense V2 API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
create_tables()


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterReq(BaseModel):
    username: str; email: str; password: str
    full_name: str = ""; role: str = "student"

class LoginReq(BaseModel):
    username: str; password: str

class ReviewReq(BaseModel):
    code: str; language: str = "python"; student_id: str = ""

class FixReq(BaseModel):
    code: str; language: str = "python"

class EnhanceReq(BaseModel):
    code: str; language: str = "python"

class ComplexityReq(BaseModel):
    code: str; language: str = "python"

class AskReq(BaseModel):
    prompt: str; context_code: str = ""; language: str = "python"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _award_xp(db, user: User, action: str, grade: str = None):
    """Award XP, check new badges, update user stats."""
    import json as _json
    xp = calculate_xp_for_action(action, grade)
    user.xp = (user.xp or 0) + xp

    # Update counters
    if action == "review":
        user.review_count = (user.review_count or 0) + 1
        if grade == "Excellent":
            user.excellent_count = (user.excellent_count or 0) + 1
    elif action == "fix":
        user.fix_count = (user.fix_count or 0) + 1
    elif action == "enhance":
        user.enhance_count = (user.enhance_count or 0) + 1
    elif action == "ask":
        user.ask_count = (user.ask_count or 0) + 1

    # Check new badges
    existing = _json.loads(user.badges or "[]")
    reviews = db.query(Review).filter(Review.username == user.username).all()
    languages_used = len(set(r.language for r in reviews))
    java_count  = sum(1 for r in reviews if r.language == "java")
    js_count    = sum(1 for r in reviews if r.language == "javascript")
    c_count     = sum(1 for r in reviews if r.language == "c")

    stats = {
        "review_count":   user.review_count,
        "fix_count":      user.fix_count,
        "enhance_count":  user.enhance_count,
        "perfect_count":  1 if (grade and grade == "Excellent") else 0,
        "streak":         0,
        "languages_used": languages_used,
        "excellent_count": user.excellent_count,
        "java_count":     java_count,
        "js_count":       js_count,
        "c_count":        c_count,
    }

    new_badges = check_new_badges(stats, existing)
    bonus_xp = sum(get_badge_info(b)["xp_bonus"] for b in new_badges)
    if bonus_xp:
        user.xp += bonus_xp

    all_badges = existing + new_badges
    user.badges = _json.dumps(all_badges)
    db.commit()
    return xp + bonus_xp, new_badges


def _get_user_profile(db, username: str) -> dict:
    import json as _json
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return {}
    level_info = get_level(user.xp or 0)
    badges = _json.loads(user.badges or "[]")
    badge_details = [get_badge_info(b) for b in badges]

    reviews = db.query(Review).filter(Review.username == username).order_by(Review.reviewed_at.desc()).all()
    review_dates = [r.reviewed_at.date() for r in reviews]
    streak = calculate_streak(review_dates)

    return {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "xp": user.xp or 0,
        "level": level_info,
        "badges": badge_details,
        "streak": streak,
        "review_count": user.review_count or 0,
        "fix_count": user.fix_count or 0,
        "enhance_count": user.enhance_count or 0,
        "ask_count": user.ask_count or 0,
        "excellent_count": user.excellent_count or 0,
        "avatar_color": user.avatar_color or "#6366f1",
        "joined": user.created_at.isoformat() if user.created_at else "",
    }


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.post("/api/auth/register")
def register(req: RegisterReq, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(400, "Username taken")
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(400, "Email registered")
    import random
    colors = ["#6366f1","#f43f5e","#10b981","#f59e0b","#3b82f6","#8b5cf6","#ec4899"]
    user = User(username=req.username, email=req.email, full_name=req.full_name,
                hashed_password=hash_password(req.password), role=req.role,
                avatar_color=random.choice(colors), xp=0, badges="[]")
    db.add(user); db.commit(); db.refresh(user)
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer",
            "username": user.username, "role": user.role, "full_name": user.full_name}


@app.post("/api/auth/login")
def login(req: LoginReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer",
            "username": user.username, "role": user.role, "full_name": user.full_name or ""}


# ── Review ────────────────────────────────────────────────────────────────────

@app.post("/api/review")
def review(req: ReviewReq, db: Session = Depends(get_db),
           current_user: dict = Depends(get_current_user)):
    features = extract_features(req.code, req.language)
    try:
        prediction = predict_quality(features)
    except FileNotFoundError:
        raise HTTPException(500, "ML model not found. Run: python train_model.py")

    # Pylint only for Python
    pylint_issues = _run_pylint(req.code) if req.language.lower() == "python" else []

    complexity = analyze_complexity(req.code, req.language)

    # AI review summary (optional)
    ai_summary = ai_service.review_with_ai(
        req.code, req.language, prediction["grade"], pylint_issues
    )

    # Update language counters
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    if user:
        lang = req.language.lower()
        if lang == "java":   user.java_count = (user.java_count or 0) + 1
        elif lang == "javascript": user.js_count = (user.js_count or 0) + 1
        elif lang == "c":    user.c_count = (user.c_count or 0) + 1
        elif lang == "python": user.python_count = (user.python_count or 0) + 1

    # Save review
    r = Review(
        student_id=req.student_id or current_user["sub"],
        username=current_user["sub"],
        code_snippet=req.code[:600],
        language=req.language,
        ml_grade=prediction["grade"],
        quality_score=prediction["quality_score"],
        confidence=prediction["confidence"],
        time_complexity=complexity.time_complexity,
        space_complexity=complexity.space_complexity,
        pylint_issues=json.dumps(pylint_issues),
    )
    db.commit();
    db.add(r); 

    # Award XP
    xp_earned, new_badges = _award_xp(db, user, "review", prediction["grade"])
    r.xp_earned = xp_earned; db.commit()

    return {
        "quality_score": prediction["quality_score"],
        "ml_grade": prediction["grade"],
        "confidence": prediction["confidence"],
        "grade_probabilities": prediction["grade_probabilities"],
        "complexity": {
            "time": complexity.time_complexity,
            "space": complexity.space_complexity,
            "explanation": complexity.explanation,
            "bottlenecks": complexity.bottlenecks,
            "hint": complexity.optimization_hint,
        },
        "pylint_issues": pylint_issues,
        "feature_vector": features,
        "ai_summary": ai_summary,
        "xp_earned": xp_earned,
        "new_badges": [get_badge_info(b) for b in new_badges],
        "reviewed_at": datetime.utcnow().isoformat(),
    }


def _run_pylint(code: str) -> list:
    issues = []
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code); tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pylint", tmp, "--output-format=json",
             "--disable=C0114,C0115,C0116,C0301"],
            capture_output=True, text=True, timeout=30)
        raw = json.loads(result.stdout) if result.stdout.strip().startswith("[") else []
        for item in raw[:15]:
            issues.append({"line": item.get("line", 0), "type": item.get("type", ""),
                           "message": item.get("message", ""), "symbol": item.get("symbol", "")})
    except Exception:
        pass
    finally:
        try: os.unlink(tmp)
        except: pass
    return issues


# ── Fix ───────────────────────────────────────────────────────────────────────

@app.post("/api/fix")
def fix(req: FixReq, db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)):
    result = fix_code(req.code, req.language)
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    fh = FixHistory(username=current_user["sub"], language=req.language,
                    fixes_count=len(result["fixes_applied"]))
    db.add(fh); db.commit()
    xp_earned, new_badges = _award_xp(db, user, "fix")
    fh.xp_earned = xp_earned; db.commit()
    result["xp_earned"] = xp_earned
    result["new_badges"] = [get_badge_info(b) for b in new_badges]
    return result


# ── Enhance ───────────────────────────────────────────────────────────────────

@app.post("/api/enhance")
def enhance(req: EnhanceReq, db: Session = Depends(get_db),
            current_user: dict = Depends(get_current_user)):
    result = enhance_code(req.code, req.language)
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    xp_earned, new_badges = _award_xp(db, user, "enhance")
    result["xp_earned"] = xp_earned
    result["new_badges"] = [get_badge_info(b) for b in new_badges]
    return result


# ── Complexity ────────────────────────────────────────────────────────────────

@app.post("/api/complexity")
def complexity(req: ComplexityReq, current_user: dict = Depends(get_current_user)):
    r = analyze_complexity(req.code, req.language)
    return {"time_complexity": r.time_complexity, "space_complexity": r.space_complexity,
            "explanation": r.explanation, "bottlenecks": r.bottlenecks,
            "optimization_hint": r.optimization_hint}


# ── Ask AI ────────────────────────────────────────────────────────────────────

@app.post("/api/ask")
def ask(req: AskReq, db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)):
    result = ai_service.ask(req.prompt, req.context_code, req.language)
    user = db.query(User).filter(User.username == current_user["sub"]).first()
    ah = AskHistory(username=current_user["sub"], prompt=req.prompt[:200],
                    source=result.get("source", "local_kb"))
    db.add(ah); db.commit()
    xp_earned, new_badges = _award_xp(db, user, "ask")
    ah.xp_earned = xp_earned; db.commit()
    result["xp_earned"] = xp_earned
    result["new_badges"] = [get_badge_info(b) for b in new_badges]
    return result


# ── Profile ───────────────────────────────────────────────────────────────────

@app.get("/api/profile/{username}")
def get_profile(username: str, db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    profile = _get_user_profile(db, username)
    if not profile:
        raise HTTPException(404, "User not found")
    return profile


# ── History ───────────────────────────────────────────────────────────────────

@app.get("/api/history/{username}")
def history(username: str, db: Session = Depends(get_db),
            current_user: dict = Depends(get_current_user)):
    reviews = db.query(Review).filter(Review.username == username)\
        .order_by(Review.reviewed_at.desc()).limit(20).all()
    return {
        "username": username,
        "reviews": [{
            "id": r.id, "language": r.language, "ml_grade": r.ml_grade,
            "quality_score": r.quality_score, "time_complexity": r.time_complexity,
            "space_complexity": r.space_complexity, "xp_earned": r.xp_earned,
            "reviewed_at": r.reviewed_at.isoformat(),
        } for r in reviews]
    }


# ── Professor: all students ───────────────────────────────────────────────────

@app.get("/api/professor/students")
def all_students(db: Session = Depends(get_db),
                 current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "professor":
        raise HTTPException(403, "Professor access required")
    students = db.query(User).filter(User.role == "student").all()
    result = []
    for s in students:
        level = get_level(s.xp or 0)
        result.append({
            "username": s.username, "full_name": s.full_name,
            "xp": s.xp or 0, "level": level["level_name"],
            "level_icon": level["level_icon"],
            "review_count": s.review_count or 0,
            "excellent_count": s.excellent_count or 0,
            "avatar_color": s.avatar_color or "#6366f1",
        })
    result.sort(key=lambda x: x["xp"], reverse=True)
    return {"students": result, "total": len(result)}


# ── Leaderboard ───────────────────────────────────────────────────────────────

@app.get("/api/leaderboard")
def leaderboard(db: Session = Depends(get_db),
                current_user: dict = Depends(get_current_user)):
    users = db.query(User).filter(User.role == "student").all()
    board = []
    for u in users:
        lvl = get_level(u.xp or 0)
        board.append({
            "rank": 0, "username": u.username, "full_name": u.full_name or u.username,
            "xp": u.xp or 0, "level": lvl["level_name"], "icon": lvl["level_icon"],
            "color": lvl["level_color"], "reviews": u.review_count or 0,
            "avatar_color": u.avatar_color or "#6366f1",
        })
    board.sort(key=lambda x: x["xp"], reverse=True)
    for i, entry in enumerate(board):
        entry["rank"] = i + 1
    return {"leaderboard": board[:20]}


# ── AI Status ─────────────────────────────────────────────────────────────────

@app.get("/api/ai-status")
def ai_status():
    return ai_service.get_ai_status()


@app.get("/api/health")
def health():
    return {"status": "running", "version": "2.0.0", "service": "CodeSense V2"}
