"""
gamification.py
XP system, levels, badges, streaks for CodeSense V2.
"""

from datetime import datetime, date, timedelta
from typing import List

# ── Level Thresholds ──────────────────────────────────────────────────────────
LEVELS = [
    {"name": "Beginner",      "min_xp": 0,    "icon": "🐣", "color": "#94a3b8"},
    {"name": "Novice",        "min_xp": 100,  "icon": "🌱", "color": "#4ade80"},
    {"name": "Apprentice",    "min_xp": 300,  "icon": "⚡", "color": "#60a5fa"},
    {"name": "Intermediate",  "min_xp": 600,  "icon": "🔥", "color": "#f97316"},
    {"name": "Advanced",      "min_xp": 1000, "icon": "💎", "color": "#a78bfa"},
    {"name": "Expert",        "min_xp": 1500, "icon": "🏆", "color": "#fbbf24"},
    {"name": "Master",        "min_xp": 2500, "icon": "👑", "color": "#f43f5e"},
]

# ── Badge Definitions ─────────────────────────────────────────────────────────
BADGE_DEFS = {
    "first_review":     {"name": "First Steps",      "icon": "🚀", "desc": "Complete your first review",       "xp_bonus": 20},
    "review_10":        {"name": "Code Watcher",     "icon": "👁️",  "desc": "Complete 10 reviews",              "xp_bonus": 50},
    "review_50":        {"name": "Review Machine",   "icon": "⚙️",  "desc": "Complete 50 reviews",              "xp_bonus": 150},
    "perfect_score":    {"name": "Perfectionist",    "icon": "💯", "desc": "Score 95+ on a review",            "xp_bonus": 75},
    "streak_3":         {"name": "On Fire 🔥",        "icon": "🔥", "desc": "3-day coding streak",              "xp_bonus": 30},
    "streak_7":         {"name": "Week Warrior",     "icon": "⚔️",  "desc": "7-day coding streak",              "xp_bonus": 100},
    "multilingual":     {"name": "Polyglot",         "icon": "🌐", "desc": "Review code in 3+ languages",      "xp_bonus": 60},
    "bug_slayer":       {"name": "Bug Slayer",        "icon": "🐛", "desc": "Fix code 10 times",                "xp_bonus": 40},
    "enhancer":         {"name": "Optimizer",        "icon": "✨", "desc": "Enhance code 10 times",            "xp_bonus": 40},
    "excellent_grade":  {"name": "Excellence",       "icon": "⭐", "desc": "Get Excellent grade 5 times",      "xp_bonus": 80},
    "java_master":      {"name": "Java Dev",         "icon": "☕", "desc": "Review 5 Java programs",           "xp_bonus": 30},
    "js_ninja":         {"name": "JS Ninja",         "icon": "🟨", "desc": "Review 5 JavaScript programs",     "xp_bonus": 30},
    "c_hacker":         {"name": "C Hacker",         "icon": "⚡", "desc": "Review 5 C programs",              "xp_bonus": 30},
}

# ── XP per Action ─────────────────────────────────────────────────────────────
XP_REWARDS = {
    "review":   15,
    "fix":      10,
    "enhance":  10,
    "ask":       5,
    "Excellent": 25,
    "Good":      15,
    "Average":    8,
    "Poor":       3,
}


def get_level(xp: int) -> dict:
    """Returns current level info for given XP."""
    current = LEVELS[0]
    for lvl in LEVELS:
        if xp >= lvl["min_xp"]:
            current = lvl
        else:
            break
    # Find next level
    idx = LEVELS.index(current)
    next_lvl = LEVELS[idx + 1] if idx + 1 < len(LEVELS) else None

    xp_for_next = next_lvl["min_xp"] - current["min_xp"] if next_lvl else 0
    xp_in_level = xp - current["min_xp"]
    progress = (xp_in_level / xp_for_next * 100) if xp_for_next else 100

    return {
        "level_name": current["name"],
        "level_icon": current["icon"],
        "level_color": current["color"],
        "level_index": idx + 1,
        "total_levels": len(LEVELS),
        "xp_to_next": max(0, (next_lvl["min_xp"] - xp) if next_lvl else 0),
        "progress_pct": round(min(progress, 100), 1),
        "next_level": next_lvl["name"] if next_lvl else "MAX",
    }


def calculate_xp_for_action(action: str, grade: str = None) -> int:
    """Returns XP to award for a given action."""
    base = XP_REWARDS.get(action, 5)
    bonus = XP_REWARDS.get(grade, 0) if grade else 0
    return base + bonus


def check_new_badges(stats: dict, existing_badges: List[str]) -> List[str]:
    """
    Checks which new badges the student has earned.
    stats: dict with review_count, fix_count, enhance_count,
           perfect_count, streak, languages_used, excellent_count,
           java_count, js_count, c_count
    Returns list of newly earned badge keys.
    """
    earned = []

    def check(key, condition):
        if condition and key not in existing_badges:
            earned.append(key)

    check("first_review",    stats.get("review_count", 0) >= 1)
    check("review_10",       stats.get("review_count", 0) >= 10)
    check("review_50",       stats.get("review_count", 0) >= 50)
    check("perfect_score",   stats.get("perfect_count", 0) >= 1)
    check("streak_3",        stats.get("streak", 0) >= 3)
    check("streak_7",        stats.get("streak", 0) >= 7)
    check("multilingual",    stats.get("languages_used", 0) >= 3)
    check("bug_slayer",      stats.get("fix_count", 0) >= 10)
    check("enhancer",        stats.get("enhance_count", 0) >= 10)
    check("excellent_grade", stats.get("excellent_count", 0) >= 5)
    check("java_master",     stats.get("java_count", 0) >= 5)
    check("js_ninja",        stats.get("js_count", 0) >= 5)
    check("c_hacker",        stats.get("c_count", 0) >= 5)

    return earned


def get_badge_info(badge_key: str) -> dict:
    return BADGE_DEFS.get(badge_key, {"name": badge_key, "icon": "🏅", "desc": "", "xp_bonus": 0})


def calculate_streak(review_dates: List[date]) -> int:
    """Calculate current daily streak from list of review dates."""
    if not review_dates:
        return 0
    unique_dates = sorted(set(review_dates), reverse=True)
    today = date.today()
    streak = 0
    expected = today
    for d in unique_dates:
        if d == expected or d == expected - timedelta(days=1):
            streak += 1
            expected = d - timedelta(days=1)
        else:
            break
    return streak
