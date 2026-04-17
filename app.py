"""
app.py — CodeSense V2 Streamlit Frontend
Gaming + Glassmorphism UI | Login | Student Dashboard | Professor View
"""

import streamlit as st
import requests
import json
import time
from dotenv import load_dotenv
load_dotenv()
# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="CodeSense V2", page_icon="🧠", layout="wide",
                   initial_sidebar_state="collapsed")

API = "http://127.0.0.1:8000/api"
LANGUAGES = ["python", "java", "javascript", "c"]
LANG_ICONS = {"python": "🐍", "java": "☕", "javascript": "🟨", "c": "⚡"}

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 70%, #0f3460 100%);
    min-height: 100vh;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 1400px; }

/* Glass card */
.glass {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 24px;
    margin: 8px 0;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.glass-bright {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(30px);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 16px;
    padding: 20px;
    margin: 6px 0;
}

/* Neon text */
.neon-title {
    font-size: 2.8rem !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #00f5ff, #a855f7, #f43f5e, #f59e0b);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 4s ease infinite;
    text-align: center;
    margin: 0 !important;
}

@keyframes gradientShift {
    0% { background-position: 0%; }
    50% { background-position: 100%; }
    100% { background-position: 0%; }
}

.sub-title {
    text-align: center;
    color: rgba(255,255,255,0.5);
    font-size: 1rem;
    margin-top: -4px;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* XP Bar */
.xp-bar-container {
    background: rgba(255,255,255,0.08);
    border-radius: 50px;
    height: 12px;
    overflow: hidden;
    margin: 6px 0;
}
.xp-bar-fill {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #00f5ff, #a855f7);
    box-shadow: 0 0 10px #00f5ff88;
    transition: width 0.5s ease;
}

/* Grade badges */
.grade-Excellent { background: linear-gradient(135deg,#065f46,#059669); color:#6ee7b7; }
.grade-Good      { background: linear-gradient(135deg,#1e3a5f,#2563eb); color:#93c5fd; }
.grade-Average   { background: linear-gradient(135deg,#451a03,#d97706); color:#fde68a; }
.grade-Poor      { background: linear-gradient(135deg,#450a0a,#dc2626); color:#fca5a5; }
.grade-badge {
    display: inline-block; padding: 6px 18px; border-radius: 50px;
    font-weight: 700; font-size: 14px; letter-spacing: 1px;
}

/* Metric card */
.metric-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 800; color: #fff; }
.metric-label { font-size: 0.75rem; color: rgba(255,255,255,0.5);
                text-transform: uppercase; letter-spacing: 1px; }

/* Badge */
.badge-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,215,0,0.3);
    border-radius: 12px;
    padding: 10px 14px;
    display: inline-block;
    margin: 4px;
    text-align: center;
    box-shadow: 0 0 12px rgba(255,215,0,0.1);
}

/* Pylint issue */
.issue-error     { border-left: 3px solid #f43f5e; padding: 8px 12px; margin: 4px 0;
                   background: rgba(244,63,94,0.08); border-radius: 0 8px 8px 0; }
.issue-warning   { border-left: 3px solid #f59e0b; padding: 8px 12px; margin: 4px 0;
                   background: rgba(245,158,11,0.08); border-radius: 0 8px 8px 0; }
.issue-convention{ border-left: 3px solid #6366f1; padding: 8px 12px; margin: 4px 0;
                   background: rgba(99,102,241,0.08); border-radius: 0 8px 8px 0; }

/* Complexity box */
.complexity-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.15));
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}
.complexity-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #00f5ff, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Enhancement item */
.enh-item {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 0;
    color: rgba(255,255,255,0.85);
}

/* Leaderboard row */
.lb-row {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 12px 16px;
    margin: 4px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    border: 1px solid rgba(255,255,255,0.08);
}
.lb-rank-1 { border-color: rgba(255,215,0,0.4); background: rgba(255,215,0,0.06); }
.lb-rank-2 { border-color: rgba(192,192,192,0.4); }
.lb-rank-3 { border-color: rgba(205,127,50,0.4); }

/* XP toast */
.xp-toast {
    background: linear-gradient(135deg, #065f46, #059669);
    border: 1px solid #6ee7b7;
    border-radius: 12px;
    padding: 12px 20px;
    color: #6ee7b7;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(16,185,129,0.4);
}

/* Login form */
.login-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(40px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 24px;
    padding: 40px;
    max-width: 460px;
    margin: 0 auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}

/* Streamlit overrides */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: monospace !important;
}
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #a855f7) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    padding: 0.6rem 1.8rem !important; font-size: 0.95rem !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.6) !important;
}
label, .stSelectbox label { color: rgba(255,255,255,0.7) !important; }
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(255,255,255,0.5) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,#6366f1,#a855f7) !important;
    color: white !important;
}
.stProgress > div > div { background: linear-gradient(90deg,#00f5ff,#a855f7) !important;
                           border-radius: 50px !important; }
h1,h2,h3,h4 { color: #fff !important; }
p, .stMarkdown p { color: rgba(255,255,255,0.8) !important; }
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
for key, val in {
    "token": None, "username": None, "role": None,
    "full_name": None, "page": "login"
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_post(endpoint, data):
    try:
        r = requests.post(f"{API}{endpoint}", json=data,
                          headers=auth_headers(), timeout=300)
        return r.json(), r.status_code
    except requests.ConnectionError:
        return {"error": "API not running — start uvicorn first"}, 503


def api_get(endpoint):
    try:
        r = requests.get(f"{API}{endpoint}", headers=auth_headers(), timeout=15)
        return r.json(), r.status_code
    except requests.ConnectionError:
        return {"error": "API not running"}, 503


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN / REGISTER PAGE
# ─────────────────────────────────────────────────────────────────────────────

def show_login():
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='neon-title'>CodeSense V2</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>AI · ML · Code Review · Gamified</p>", unsafe_allow_html=True)
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Login", "🚀 Register"])

        with tab_login:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="Enter username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("🎮 Enter CodeSense", use_container_width=True):
                if username and password:
                    try:
                        r = requests.post(f"{API}/auth/login",
                            json={"username": username, "password": password}, timeout=10)
                        if r.status_code == 200:
                            d = r.json()
                            st.session_state.token = d["access_token"]
                            st.session_state.username = d["username"]
                            st.session_state.role = d["role"]
                            st.session_state.full_name = d.get("full_name", username)
                            st.session_state.page = "dashboard"
                            st.rerun()
                        else:
                            st.error(f"❌ {r.json().get('detail', 'Login failed')}")
                    except:
                        st.error("❌ Cannot connect to API")
                else:
                    st.warning("Fill in all fields")

        with tab_register:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            full_name = st.text_input("Full Name", key="reg_name", placeholder="Your name")
            reg_user = st.text_input("Username", key="reg_user", placeholder="Choose username")
            reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            reg_role = st.selectbox("Role", ["student", "professor"], key="reg_role")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("🚀 Create Account", use_container_width=True):
                if reg_user and reg_email and reg_pass:
                    try:
                        r = requests.post(f"{API}/auth/register", json={
                            "username": reg_user, "email": reg_email,
                            "password": reg_pass, "full_name": full_name,
                            "role": reg_role}, timeout=10)
                        if r.status_code == 200:
                            d = r.json()
                            st.session_state.token = d["access_token"]
                            st.session_state.username = d["username"]
                            st.session_state.role = d["role"]
                            st.session_state.full_name = full_name
                            st.session_state.page = "dashboard"
                            st.success("🎉 Account created!")
                            time.sleep(0.8)
                            st.rerun()
                        else:
                            st.error(r.json().get("detail", "Registration failed"))
                    except:
                        st.error("❌ Cannot connect to API")
                else:
                    st.warning("Fill in all fields")

    # Demo hint
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;color:rgba(255,255,255,0.3);font-size:0.8rem'>
    🔒 Secure JWT Auth · 🎮 Earn XP · 🏆 Climb the Leaderboard · 🌐 Python · Java · JS · C
    </p>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR (when logged in)
# ─────────────────────────────────────────────────────────────────────────────

def show_sidebar():
    with st.sidebar:
        # Profile
        profile, _ = api_get(f"/profile/{st.session_state.username}")
        xp = profile.get("xp", 0)
        lvl = profile.get("level", {})
        streak = profile.get("streak", 0)

        st.markdown(f"""
        <div style='text-align:center;padding:16px 0'>
            <div style='width:64px;height:64px;border-radius:50%;
                 background:linear-gradient(135deg,{profile.get("avatar_color","#6366f1")},#a855f7);
                 display:flex;align-items:center;justify-content:center;
                 font-size:24px;margin:0 auto 10px;
                 box-shadow:0 0 20px {profile.get("avatar_color","#6366f1")}66'>
                {lvl.get("level_icon","🐣")}
            </div>
            <div style='color:#fff;font-weight:700;font-size:1rem'>
                {profile.get("full_name") or st.session_state.username}
            </div>
            <div style='color:rgba(255,255,255,0.5);font-size:0.75rem'>
                @{st.session_state.username}
            </div>
            <div style='margin:8px 0;padding:4px 12px;border-radius:20px;
                 background:rgba(255,255,255,0.08);display:inline-block;
                 color:{lvl.get("level_color","#fff")};font-weight:600;font-size:0.8rem'>
                {lvl.get("level_icon","🐣")} {lvl.get("level_name","Beginner")}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # XP bar
        progress = lvl.get("progress_pct", 0)
        st.markdown(f"""
        <div style='padding:0 8px'>
            <div style='display:flex;justify-content:space-between;
                 color:rgba(255,255,255,0.5);font-size:0.7rem;margin-bottom:4px'>
                <span>⚡ {xp} XP</span>
                <span>→ {lvl.get("next_level","MAX")}</span>
            </div>
            <div class='xp-bar-container'>
                <div class='xp-bar-fill' style='width:{progress}%'></div>
            </div>
            <div style='text-align:right;color:rgba(255,255,255,0.3);font-size:0.65rem'>
                {lvl.get("xp_to_next",0)} XP to next level
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)

        # Streak
        if streak > 0:
            st.markdown(f"""
            <div style='text-align:center;color:#f59e0b;font-size:0.85rem;margin:8px 0'>
                🔥 {streak}-day streak!
            </div>""", unsafe_allow_html=True)

        # Nav
        st.markdown("**Navigation**")
        pages = ["📊 Dashboard", "💻 Code Review", "🔧 Fix Code",
                 "✨ Enhance", "⏱ Complexity", "💬 Ask AI",
                 "🏆 Leaderboard", "📈 My Progress"]
        if st.session_state.role == "professor":
            pages.append("👨‍🏫 Professor View")

        for page in pages:
            if st.button(page, use_container_width=True, key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)

        # AI Status
        ai_s, _ = api_get("/ai-status")
        active = ai_s.get("active", "local_kb")
        ai_color = {"groq": "#10b981", "ollama": "#3b82f6", "local_kb": "#f59e0b"}.get(active, "#fff")
        ai_icon = {"groq": "⚡", "ollama": "🖥️", "local_kb": "📚"}.get(active, "❓")
        st.markdown(f"""
        <div style='text-align:center;font-size:0.75rem;color:{ai_color}'>
            {ai_icon} AI: {active.upper()}
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["token","username","role","full_name","page"]:
                st.session_state[k] = None
            st.session_state.page = "login"
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# XP TOAST
# ─────────────────────────────────────────────────────────────────────────────

def show_xp_toast(xp_earned, new_badges=None):
    if xp_earned > 0:
        st.markdown(f"""
        <div class='xp-toast'>⚡ +{xp_earned} XP earned!</div>
        """, unsafe_allow_html=True)
    if new_badges:
        for b in new_badges:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,rgba(255,215,0,0.1),rgba(255,165,0,0.1));
                 border:1px solid rgba(255,215,0,0.4);border-radius:12px;padding:10px 16px;
                 margin:4px 0;text-align:center;color:#fde68a;font-weight:700'>
                🎖️ New Badge Unlocked: {b.get("icon","")} {b.get("name","")} — {b.get("desc","")}
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def show_dashboard():
    profile, _ = api_get(f"/profile/{st.session_state.username}")

    name = profile.get("full_name") or st.session_state.username
    st.markdown(f"""
    <div style='margin-bottom:24px'>
        <h1 style='font-size:2rem;margin:0'>
            Welcome back, <span style='background:linear-gradient(90deg,#00f5ff,#a855f7);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent'>{name}</span>! 🎮
        </h1>
        <p style='color:rgba(255,255,255,0.5);margin:0'>Ready to level up your code today?</p>
    </div>""", unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    lvl = profile.get("level", {})
    c1, c2, c3, c4, c5 = st.columns(5)

    metrics = [
        (c1, "⚡", str(profile.get("xp", 0)), "Total XP", "#00f5ff"),
        (c2, lvl.get("level_icon", "🐣"), lvl.get("level_name", "Beginner"), "Level", lvl.get("level_color", "#fff")),
        (c3, "📊", str(profile.get("review_count", 0)), "Reviews", "#a855f7"),
        (c4, "🔥", str(profile.get("streak", 0)), "Day Streak", "#f59e0b"),
        (c5, "💯", str(profile.get("excellent_count", 0)), "Excellent", "#10b981"),
    ]
    for col, icon, val, label, color in metrics:
        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='font-size:1.5rem'>{icon}</div>
                <div class='metric-value' style='color:{color}'>{val}</div>
                <div class='metric-label'>{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── XP Progress ───────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        progress = lvl.get("progress_pct", 0)
        xp_to_next = lvl.get("xp_to_next", 0)
        st.markdown(f"""
        <div style='margin-bottom:12px'>
            <span style='font-size:1.1rem;font-weight:700;color:#fff'>
                {lvl.get("level_icon","🐣")} Level Progress
            </span>
            <span style='float:right;color:rgba(255,255,255,0.5);font-size:0.85rem'>
                {xp_to_next} XP to {lvl.get("next_level","MAX")}
            </span>
        </div>
        <div class='xp-bar-container' style='height:18px'>
            <div class='xp-bar-fill' style='width:{progress}%'></div>
        </div>
        <div style='margin-top:8px;color:rgba(255,255,255,0.4);font-size:0.75rem'>
            {profile.get("xp",0)} / {profile.get("xp",0) + xp_to_next} XP  •  {progress}% to {lvl.get("next_level","MAX")}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Quick actions
        st.markdown("<div class='glass' style='text-align:center'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#fff;font-weight:700;margin-bottom:12px'>🚀 Quick Start</div>", unsafe_allow_html=True)
        if st.button("💻 Review Code", use_container_width=True):
            st.session_state.page = "💻 Code Review"; st.rerun()
        if st.button("💬 Ask AI", use_container_width=True):
            st.session_state.page = "💬 Ask AI"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Badges ────────────────────────────────────────────────────────────────
    badges = profile.get("badges", [])
    if badges:
        st.markdown("### 🎖️ Your Badges")
        badge_html = "".join([
            f"<div class='badge-card'><div style='font-size:1.5rem'>{b.get('icon','🏅')}</div>"
            f"<div style='font-size:0.7rem;color:#fde68a;font-weight:600'>{b.get('name','')}</div></div>"
            for b in badges
        ])
        st.markdown(badge_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='glass' style='text-align:center;color:rgba(255,255,255,0.4)'>
            🎖️ No badges yet — start reviewing code to earn your first badge!
        </div>""", unsafe_allow_html=True)

    # ── Recent reviews ────────────────────────────────────────────────────────
    history, _ = api_get(f"/history/{st.session_state.username}")
    reviews = history.get("reviews", [])
    if reviews:
        st.markdown("### 📜 Recent Reviews")
        for r in reviews[:5]:
            lang_icon = LANG_ICONS.get(r["language"], "💻")
            grade = r["ml_grade"]
            st.markdown(f"""
            <div class='glass-bright' style='display:flex;justify-content:space-between;align-items:center'>
                <span>{lang_icon} <b>{r["language"].upper()}</b></span>
                <span class='grade-badge grade-{grade}'>{grade}</span>
                <span style='color:rgba(255,255,255,0.5);font-size:0.8rem'>Score: {r["quality_score"]}</span>
                <span style='color:#a855f7;font-size:0.8rem'>⏱ {r["time_complexity"]}</span>
                <span style='color:#10b981;font-size:0.8rem'>+{r.get("xp_earned",0)} XP</span>
                <span style='color:rgba(255,255,255,0.3);font-size:0.75rem'>{r["reviewed_at"][:10]}</span>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CODE REVIEW TAB
# ─────────────────────────────────────────────────────────────────────────────

def show_review():
    st.markdown("## 💻 ML Code Review")
    st.markdown("<p style='color:rgba(255,255,255,0.5)'>Random Forest ML Model · Pylint · Complexity · AI Summary</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        lang = st.selectbox("Language", LANGUAGES,
                            format_func=lambda x: f"{LANG_ICONS[x]} {x.title()}")
        student_id = st.text_input("Student ID", value=st.session_state.username)
        run_btn = st.button("🔍 Analyze", use_container_width=True)

    with col1:
        try:
            from streamlit_ace import st_ace
            code = st_ace(
                placeholder=f"// Paste your {lang} code here...",
                language=lang if lang != "c" else "c_cpp",
                theme="monokai",
                font_size=14,
                height=320,
                key=f"ace_review_{lang}",
                auto_update=True,
            )
        except ImportError:
            code = st.text_area("Paste your code here", height=320,
                                placeholder=f"// {lang} code here...",
                                key="fallback_review")

    if run_btn:
        if not code or not code.strip():
            st.warning("⚠️ Paste some code first!")
            return
        with st.spinner("🧠 Analyzing with ML..."):
            data, status = api_post("/review", {"code": code, "language": lang, "student_id": student_id})

        if status == 200:
            # XP toast
            show_xp_toast(data.get("xp_earned", 0), data.get("new_badges", []))

            # Metrics
            grade = data["ml_grade"]
            score = data["quality_score"]
            conf = int(data["confidence"] * 100)
            c1, c2, c3, c4 = st.columns(4)
            for col, label, value, color in [
                (c1, "Quality Score", f"{score}/100", "#00f5ff"),
                (c2, "ML Grade", grade, {"Excellent":"#10b981","Good":"#3b82f6","Average":"#f59e0b","Poor":"#f43f5e"}.get(grade,"#fff")),
                (c3, "Confidence", f"{conf}%", "#a855f7"),
                (c4, "Time", data["complexity"]["time"], "#f59e0b"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-value' style='color:{color}'>{value}</div>
                        <div class='metric-label'>{label}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.progress(score / 100)

            # Complexity
            comp = data["complexity"]
            c1, c2 = st.columns(2)
            for col, label, val in [(c1, "⏱ Time Complexity", comp["time"]),
                                     (c2, "💾 Space Complexity", comp["space"])]:
                with col:
                    st.markdown(f"""
                    <div class='complexity-box'>
                        <div class='complexity-value'>{val}</div>
                        <div style='color:rgba(255,255,255,0.5);font-size:0.75rem'>{label}</div>
                    </div>""", unsafe_allow_html=True)

            if comp.get("explanation"):
                st.info(f"📖 {comp['explanation']}")
            if comp.get("hint"):
                st.success(f"💡 {comp['hint']}")

            # Grade probabilities
            with st.expander("📊 Grade Probabilities"):
                for g, p in data["grade_probabilities"].items():
                    st.markdown(f"`{g}`  {int(p*100)}%")
                    st.progress(p)

            # Pylint
            issues = data.get("pylint_issues", [])
            if issues:
                st.markdown(f"**🔎 {len(issues)} Pylint Issues Found**")
                for issue in issues:
                    css = f"issue-{issue['type']}"
                    icon = {"error":"❌","warning":"⚠️","convention":"💡","refactor":"🔄"}.get(issue["type"],"ℹ️")
                    st.markdown(
                        f"<div class='{css}'>{icon} <b>Line {issue['line']}</b>: {issue['message']}</div>",
                        unsafe_allow_html=True)
            else:
                st.success("✅ No Pylint issues found!")

            # AI Summary
            if data.get("ai_summary"):
                st.markdown("**🤖 AI Review Summary**")
                st.markdown(f"""
                <div class='glass-bright' style='color:rgba(255,255,255,0.85);font-style:italic'>
                {data["ai_summary"]}
                </div>""", unsafe_allow_html=True)

            with st.expander("🔬 ML Feature Vector"):
                st.json(data["feature_vector"])
        else:
            st.error(f"❌ {data.get('error') or data.get('detail', 'Error')}")


# ─────────────────────────────────────────────────────────────────────────────
# FIX CODE TAB
# ─────────────────────────────────────────────────────────────────────────────

def show_fix():
    st.markdown("## 🔧 Auto Code Fixer")
    st.markdown("<p style='color:rgba(255,255,255,0.5)'>autopep8 · AST Analysis · Language-specific rules</p>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 1])
    with col_r:
        lang = st.selectbox("Language", LANGUAGES,
                            format_func=lambda x: f"{LANG_ICONS[x]} {x.title()}", key="fix_lang")
        fix_btn = st.button("🔧 Fix Code", use_container_width=True)
    with col_l:
        try:
            from streamlit_ace import st_ace
            code_input = st_ace(placeholder="// Paste buggy code here...",
                               language=lang if lang != "c" else "c_cpp",
                               theme="monokai", font_size=14, height=280,
                               key=f"ace_fix_{lang}", auto_update=True)
        except ImportError:
            code_input = st.text_area("Buggy code", height=280, key="fallback_fix")

    if fix_btn:
        if not code_input or not code_input.strip():
            st.warning("Paste some code first!"); return
        with st.spinner("🔧 Fixing..."):
            data, status = api_post("/fix", {"code": code_input, "language": lang})

        if status == 200:
            show_xp_toast(data.get("xp_earned", 0), data.get("new_badges", []))

            # Side-by-side diff
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**🔴 Original Code**")
                st.code(data["original_code"], language=lang)
            with c2:
                st.markdown("**🟢 Fixed Code**")
                st.code(data["fixed_code"], language=lang)

            if data["fixes_applied"]:
                st.markdown("**✅ Fixes Applied**")
                for f in data["fixes_applied"]:
                    st.markdown(f"<div class='enh-item'>✅ {f}</div>", unsafe_allow_html=True)
            if data["remaining_issues"]:
                st.markdown("**⚠️ Remaining Issues (manual fix needed)**")
                for i in data["remaining_issues"]:
                    st.markdown(f"<div class='enh-item'>⚠️ {i}</div>", unsafe_allow_html=True)
        else:
            st.error(data.get("error") or data.get("detail", "Error"))


# ─────────────────────────────────────────────────────────────────────────────
# ENHANCE TAB
# ─────────────────────────────────────────────────────────────────────────────

def show_enhance():
    st.markdown("## ✨ Code Enhancer")
    st.markdown("<p style='color:rgba(255,255,255,0.5)'>AST pattern detection · List comprehensions · f-strings · Docstrings</p>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 1])
    with col_r:
        lang = st.selectbox("Language", LANGUAGES,
                            format_func=lambda x: f"{LANG_ICONS[x]} {x.title()}", key="enh_lang")
        enh_btn = st.button("✨ Enhance", use_container_width=True)
    with col_l:
        try:
            from streamlit_ace import st_ace
            code_input = st_ace(placeholder="// Paste working code to enhance...",
                               language=lang if lang != "c" else "c_cpp",
                               theme="monokai", font_size=14, height=280,
                               key=f"ace_enh_{lang}", auto_update=True)
        except ImportError:
            code_input = st.text_area("Working code", height=280, key="fallback_enh")

    if enh_btn:
        if not code_input or not code_input.strip():
            st.warning("Paste some code first!"); return
        with st.spinner("✨ Analyzing for improvements..."):
            data, status = api_post("/enhance", {"code": code_input, "language": lang})

        if status == 200:
            show_xp_toast(data.get("xp_earned", 0), data.get("new_badges", []))
            enhs = data.get("enhancements", [])
            st.markdown(f"""
            <div class='glass' style='text-align:center'>
                <span style='font-size:1.5rem;font-weight:800;color:#00f5ff'>
                {data.get("improvement_score","0 points")}
                </span>
                <span style='color:rgba(255,255,255,0.5)'> improvement potential</span>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Original**")
                st.code(data["original_code"], language=lang)
            with c2:
                st.markdown("**Enhanced**")
                st.code(data["enhanced_code"], language=lang)

            type_icons = {"list_comprehension":"⚡","fstring_upgrade":"🔤",
                         "docstring_added":"📝","redundant_variable":"🧹",
                         "magic_number":"🔢","long_function":"✂️",
                         "string_builder":"🏗️","arrow_function":"➡️","null_check":"🛡️"}
            if enhs:
                st.markdown(f"**💡 {len(enhs)} Suggestions**")
                for e in enhs:
                    icon = type_icons.get(e.get("type",""), "💡")
                    st.markdown(
                        f"<div class='enh-item'>{icon} <b>Line {e.get('line','?')}</b> — {e.get('description','')}</div>",
                        unsafe_allow_html=True)
            else:
                st.success("✅ Code looks clean — no enhancements needed!")
        else:
            st.error(data.get("error") or data.get("detail", "Error"))


# ─────────────────────────────────────────────────────────────────────────────
# COMPLEXITY TAB
# ─────────────────────────────────────────────────────────────────────────────

def show_complexity():
    st.markdown("## ⏱ Complexity Analyzer")
    st.markdown("<p style='color:rgba(255,255,255,0.5)'>AST traversal for Python · Regex patterns for Java/JS/C</p>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 1])
    with col_r:
        lang = st.selectbox("Language", LANGUAGES,
                            format_func=lambda x: f"{LANG_ICONS[x]} {x.title()}", key="comp_lang")
        comp_btn = st.button("⏱ Analyze", use_container_width=True)
    with col_l:
        try:
            from streamlit_ace import st_ace
            code_input = st_ace(placeholder="// Paste code to analyze complexity...",
                               language=lang if lang != "c" else "c_cpp",
                               theme="monokai", font_size=14, height=260,
                               key=f"ace_comp_{lang}", auto_update=True)
        except ImportError:
            code_input = st.text_area("Code", height=260, key="fallback_comp")

    if comp_btn:
        if not code_input or not code_input.strip():
            st.warning("Paste some code first!"); return
        with st.spinner("⏱ Analyzing..."):
            data, status = api_post("/complexity", {"code": code_input, "language": lang})

        if status == 200:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class='complexity-box'>
                    <div class='complexity-value'>{data["time_complexity"]}</div>
                    <div style='color:rgba(255,255,255,0.5)'>⏱ Time Complexity</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class='complexity-box'>
                    <div class='complexity-value' style='background:linear-gradient(90deg,#10b981,#3b82f6);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
                    {data["space_complexity"]}</div>
                    <div style='color:rgba(255,255,255,0.5)'>💾 Space Complexity</div>
                </div>""", unsafe_allow_html=True)

            st.info(f"📖 {data['explanation']}")
            if data.get("bottlenecks"):
                st.markdown("**🚨 Bottlenecks**")
                for b in data["bottlenecks"]:
                    st.markdown(f"<div class='enh-item'>⚠️ <b>Line {b['line']}</b>: {b['issue']}</div>",
                               unsafe_allow_html=True)
            if data.get("optimization_hint"):
                st.success(f"💡 {data['optimization_hint']}")
        else:
            st.error(data.get("error") or data.get("detail", "Error"))


# ─────────────────────────────────────────────────────────────────────────────
# ASK AI TAB
# ─────────────────────────────────────────────────────────────────────────────

def show_ask():
    st.markdown("## 💬 Ask AI")
    st.markdown("<p style='color:rgba(255,255,255,0.5)'>⚡ Groq (primary) → 🖥️ Ollama (offline) → 📚 Local KB</p>", unsafe_allow_html=True)

    # AI status pill
    ai_s, _ = api_get("/ai-status")
    active = ai_s.get("active", "local_kb")
    ai_color = {"groq":"#10b981","ollama":"#3b82f6","local_kb":"#f59e0b"}.get(active,"#fff")
    ai_label = {"groq":"⚡ Groq Active","ollama":"🖥️ Ollama Active","local_kb":"📚 Local KB Only"}.get(active, active)
    st.markdown(f"""
    <div style='display:inline-block;padding:4px 14px;border-radius:20px;
         background:rgba(255,255,255,0.06);border:1px solid {ai_color}44;
         color:{ai_color};font-size:0.8rem;margin-bottom:12px'>
        {ai_label}
    </div>""", unsafe_allow_html=True)

    if active == "local_kb":
        st.warning("🔑 **Enable AI:** Add `GROQ_API_KEY=your_key` to `.env` (free at console.groq.com) then restart the API")

    lang = st.selectbox("Language context", LANGUAGES,
                        format_func=lambda x: f"{LANG_ICONS[x]} {x.title()}", key="ask_lang")
    prompt = st.text_input("Ask anything about coding...",
                           placeholder="How do I sort a list in Python? / Explain binary search")

    try:
        from streamlit_ace import st_ace
        ctx = st_ace(placeholder="// Optional: paste code for context...",
                    language=lang if lang != "c" else "c_cpp",
                    theme="monokai", font_size=13, height=150,
                    key="ace_ask", auto_update=True)
    except ImportError:
        ctx = st.text_area("Optional context code", height=150, key="fallback_ask")

    ask_btn = st.button("💬 Ask AI", use_container_width=False)

    if ask_btn:
        if not prompt.strip():
            st.warning("Enter a question!"); return
        with st.spinner(f"Thinking via {active}..."):
            data, status = api_post("/ask", {"prompt": prompt, "context_code": ctx or "", "language": lang})

        if status == 200:
            show_xp_toast(data.get("xp_earned", 0))

            src = data.get("source", "local_kb")
            src_label = {"groq":"⚡ Groq","ollama":"🖥️ Ollama","local_kb":"📚 Local KB"}.get(src, src)
            st.caption(f"Source: {src_label}")

            st.markdown(f"""
            <div class='glass'>
            <div style='color:rgba(255,255,255,0.9)'>{data.get("answer","")}</div>
            </div>""", unsafe_allow_html=True)

            if data.get("solution_code"):
                st.markdown("**💻 Solution Code**")
                st.code(data["solution_code"], language=lang)

            if data.get("time_complexity") or data.get("space_complexity"):
                c1, c2 = st.columns(2)
                if data.get("time_complexity"):
                    with c1:
                        st.metric("⏱ Time", data["time_complexity"])
                if data.get("space_complexity"):
                    with c2:
                        st.metric("💾 Space", data["space_complexity"])
        else:
            st.error(data.get("error") or data.get("detail","Error"))


# ─────────────────────────────────────────────────────────────────────────────
# LEADERBOARD
# ─────────────────────────────────────────────────────────────────────────────

def show_leaderboard():
    st.markdown("## 🏆 Leaderboard")
    data, status = api_get("/leaderboard")
    if status != 200:
        st.error("Could not load leaderboard"); return

    board = data.get("leaderboard", [])
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}

    for entry in board:
        r = entry["rank"]
        cls = f"lb-rank-{r}" if r <= 3 else ""
        rank_medal = medal.get(r, f"#{r}")
        st.markdown(f"""
        <div class='lb-row {cls}'>
            <span style='font-size:1.3rem;min-width:36px'>{rank_medal}</span>
            <div style='width:38px;height:38px;border-radius:50%;
                 background:{entry["avatar_color"]};display:flex;align-items:center;
                 justify-content:center;font-size:16px;flex-shrink:0'>{entry["icon"]}</div>
            <div style='flex:1'>
                <div style='color:#fff;font-weight:600'>{entry["full_name"]}</div>
                <div style='color:rgba(255,255,255,0.4);font-size:0.75rem'>@{entry["username"]}</div>
            </div>
            <div style='text-align:right'>
                <div style='color:{entry["color"]};font-weight:700'>{entry["level"]}</div>
                <div style='color:#00f5ff;font-size:0.85rem'>⚡ {entry["xp"]} XP</div>
            </div>
            <div style='text-align:right;color:rgba(255,255,255,0.4);font-size:0.8rem'>
                📊 {entry["reviews"]} reviews
            </div>
        </div>""", unsafe_allow_html=True)

    if not board:
        st.markdown("""
        <div class='glass' style='text-align:center;color:rgba(255,255,255,0.4)'>
            🏆 No students yet — be the first to review code!
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MY PROGRESS
# ─────────────────────────────────────────────────────────────────────────────

def show_progress():
    st.markdown("## 📈 My Progress")
    history, _ = api_get(f"/history/{st.session_state.username}")
    reviews = history.get("reviews", [])
    profile, _ = api_get(f"/profile/{st.session_state.username}")

    c1, c2, c3 = st.columns(3)
    lang_counts = {}
    grade_counts = {"Excellent":0,"Good":0,"Average":0,"Poor":0}
    for r in reviews:
        lang_counts[r["language"]] = lang_counts.get(r["language"], 0) + 1
        grade_counts[r["ml_grade"]] = grade_counts.get(r["ml_grade"], 0) + 1

    with c1:
        st.markdown("**📊 Reviews by Language**")
        for lang, count in lang_counts.items():
            icon = LANG_ICONS.get(lang, "💻")
            pct = count / len(reviews) if reviews else 0
            st.markdown(f"{icon} {lang.title()}: **{count}**")
            st.progress(pct)
    with c2:
        st.markdown("**🎯 Grade Distribution**")
        colors = {"Excellent":"#10b981","Good":"#3b82f6","Average":"#f59e0b","Poor":"#f43f5e"}
        for grade, count in grade_counts.items():
            pct = count / len(reviews) if reviews else 0
            st.markdown(f"<span style='color:{colors[grade]}'>{grade}</span>: **{count}**", unsafe_allow_html=True)
            st.progress(pct)
    with c3:
        st.markdown("**⚡ XP Earned per Review**")
        xp_list = [r.get("xp_earned", 0) for r in reviews[:10]]
        if xp_list:
            for i, xp in enumerate(reversed(xp_list)):
                st.markdown(f"Review {len(xp_list)-i}: **+{xp} XP**")

    # All badges
    badges = profile.get("badges", [])
    all_badges_available = [
        ("first_review","🚀","First Steps","1st review"),
        ("review_10","👁️","Code Watcher","10 reviews"),
        ("review_50","⚙️","Review Machine","50 reviews"),
        ("perfect_score","💯","Perfectionist","Score 95+"),
        ("streak_3","🔥","On Fire","3-day streak"),
        ("streak_7","⚔️","Week Warrior","7-day streak"),
        ("multilingual","🌐","Polyglot","3+ languages"),
        ("bug_slayer","🐛","Bug Slayer","Fix 10 times"),
        ("excellent_grade","⭐","Excellence","5x Excellent"),
        ("java_master","☕","Java Dev","5 Java reviews"),
        ("js_ninja","🟨","JS Ninja","5 JS reviews"),
        ("c_hacker","⚡","C Hacker","5 C reviews"),
    ]
    earned_keys = [b.get("name","") for b in badges]

    st.markdown("### 🎖️ Badge Progress")
    cols = st.columns(4)
    for i, (key, icon, name, desc) in enumerate(all_badges_available):
        with cols[i % 4]:
            earned = any(b.get("icon","") == icon for b in badges)
            opacity = "1" if earned else "0.3"
            glow = "box-shadow:0 0 12px rgba(255,215,0,0.4);" if earned else ""
            st.markdown(f"""
            <div style='text-align:center;padding:12px;border-radius:12px;
                 background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
                 margin:4px;opacity:{opacity};{glow}'>
                <div style='font-size:1.5rem'>{icon}</div>
                <div style='color:#fff;font-size:0.75rem;font-weight:600'>{name}</div>
                <div style='color:rgba(255,255,255,0.4);font-size:0.65rem'>{desc}</div>
                {'<div style="color:#fde68a;font-size:0.65rem">✅ Earned</div>' if earned else ''}
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PROFESSOR VIEW
# ─────────────────────────────────────────────────────────────────────────────

def show_professor():
    st.markdown("## 👨‍🏫 Professor Dashboard")
    data, status = api_get("/professor/students")
    if status == 403:
        st.error("⛔ Professor access required"); return
    if status != 200:
        st.error("Could not load student data"); return

    students = data.get("students", [])
    st.markdown(f"**{len(students)} students enrolled**")

    # Summary stats
    if students:
        avg_xp = sum(s["xp"] for s in students) // len(students)
        top = students[0]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#00f5ff'>{len(students)}</div><div class='metric-label'>Total Students</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#a855f7'>⚡{avg_xp}</div><div class='metric-label'>Avg XP</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><div class='metric-value' style='color:#10b981'>{top['level_icon']} {top['username']}</div><div class='metric-label'>Top Student</div></div>", unsafe_allow_html=True)

        st.markdown("---")
        for s in students:
            bar = min(s["xp"] / 1500 * 100, 100)
            st.markdown(f"""
            <div class='glass-bright' style='display:flex;align-items:center;gap:16px'>
                <div style='width:40px;height:40px;border-radius:50%;background:{s["avatar_color"]};
                     display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0'>
                    {s["level_icon"]}
                </div>
                <div style='flex:1'>
                    <div style='display:flex;justify-content:space-between'>
                        <span style='color:#fff;font-weight:600'>{s["full_name"] or s["username"]}</span>
                        <span style='color:#a855f7'>⚡ {s["xp"]} XP</span>
                    </div>
                    <div style='color:rgba(255,255,255,0.4);font-size:0.75rem'>
                        @{s["username"]} · {s["level"]} · {s["review_count"]} reviews · {s["excellent_count"]} excellent
                    </div>
                    <div class='xp-bar-container' style='height:6px;margin-top:6px'>
                        <div class='xp-bar-fill' style='width:{bar}%'></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.token:
    show_login()
else:
    show_sidebar()
    page = st.session_state.get("page", "📊 Dashboard")

    # Header
    st.markdown(f"""
    <div style='margin-bottom:8px'>
        <span style='background:linear-gradient(90deg,#6366f1,#a855f7);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        font-size:0.75rem;font-weight:700;letter-spacing:2px;text-transform:uppercase'>
        🧠 CODESENSE V2</span>
    </div>""", unsafe_allow_html=True)

    route_map = {
        "📊 Dashboard":     show_dashboard,
        "💻 Code Review":   show_review,
        "🔧 Fix Code":      show_fix,
        "✨ Enhance":       show_enhance,
        "⏱ Complexity":    show_complexity,
        "💬 Ask AI":        show_ask,
        "🏆 Leaderboard":   show_leaderboard,
        "📈 My Progress":   show_progress,
        "👨‍🏫 Professor View": show_professor,
    }

    fn = route_map.get(page, show_dashboard)
    fn()
