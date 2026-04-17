
"""
ai_service.py — CodeSense V2
Primary: Groq API (ultra-fast, free)
Fallback: Ollama (100% offline, local)
Last resort: local_kb.json
"""

import os
import re
import json
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-8b-8192"   # Free, fast model on Groq

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama")

_KB_PATH = os.path.join(os.path.dirname(__file__), "local_kb.json")
try:
    with open(_KB_PATH) as f:
        LOCAL_KB = json.load(f)
except FileNotFoundError:
    LOCAL_KB = []


SYSTEM_PROMPT = """You are CodeSense AI — an expert coding mentor for students.
You teach with enthusiasm and clarity.
Always respond with:
1. A clear explanation (2-3 sentences)
2. Working code example with proper formatting
3. Time complexity: O(?)
4. Space complexity: O(?)
5. One pro tip

Format the code inside ```language ... ``` blocks.
Be encouraging and concise."""


def ask(prompt: str, context_code: str = "", language: str = "python") -> dict:
    """Try Groq → Ollama → Local KB in order."""

    full_prompt = prompt
    if context_code:
        full_prompt += f"\n\nContext code ({language}):\n```{language}\n{context_code}\n```"

    # ── 1. Groq ───────────────────────────────────────────────────────────────
    if GROQ_API_KEY:
        try:
            return _ask_groq(full_prompt)
        except Exception as e:
            print(f"[Groq error] {type(e).__name__}: {e}")

    # ── 2. Ollama ─────────────────────────────────────────────────────────────
    try:
        return _ask_ollama(full_prompt)
    except Exception as e:
        print(f"[Ollama error — falling back to local KB] {type(e).__name__}: {e}")

    # ── 3. Local KB ───────────────────────────────────────────────────────────
    return _ask_local_kb(prompt)


def review_with_ai(code: str, language: str, ml_grade: str, pylint_issues: list) -> str:
    """
    Uses AI to generate a human-readable review summary.
    Called only from /api/review if AI is available.
    """
    issues_text = "\n".join([f"- Line {i.get('line')}: {i.get('message')}" for i in pylint_issues[:5]])
    prompt = (
        f"Review this {language} code. ML grade: {ml_grade}.\n"
        f"Issues found:\n{issues_text or 'None'}\n\n"
        f"Code:\n```{language}\n{code[:800]}\n```\n\n"
        "Give a 2-sentence constructive review mentioning 1 strength and 1 improvement. "
        "Be encouraging for a student."
    )

    if GROQ_API_KEY:
        try:
            result = _ask_groq(prompt)
            return result.get("answer", "")
        except Exception:
            pass
    try:
        result = _ask_ollama(prompt)
        return result.get("answer", "")
    except Exception:
        pass
    return ""


# ── Groq ──────────────────────────────────────────────────────────────────────

def _ask_groq(prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1024,
        "temperature": 0.3,
    }
    resp = httpx.post(GROQ_URL, json=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["message"]["content"]
    return _parse_ai_response(text, source="groq")


# ── Ollama ────────────────────────────────────────────────────────────────────

def _ask_ollama(prompt: str) -> dict:
    # Verify the model is actually available before generating
    try:
        tags_resp = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        tags_resp.raise_for_status()
        available = [m["name"] for m in tags_resp.json().get("models", [])]
        # Accept both "codellama" and "codellama:latest" etc.
        model_ok = any(OLLAMA_MODEL in m for m in available)
        if not model_ok:
            raise RuntimeError(
                f"Model '{OLLAMA_MODEL}' not found in Ollama. "
                f"Available: {available}. "
                f"Run: ollama pull {OLLAMA_MODEL}"
            )
    except RuntimeError:
        raise
    except Exception as e:
        print(f"[Ollama tags check error] {e}")

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nUser: {prompt}",
        "stream": False,
    }
    print(f"[Ollama] Sending request to {OLLAMA_URL} with model={OLLAMA_MODEL} (timeout=300s)...")
    resp = httpx.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=300)
    resp.raise_for_status()
    text = resp.json().get("response", "")
    print(f"[Ollama] Response received ({len(text)} chars)")
    return _parse_ai_response(text, source="ollama")


# ── Parse response ────────────────────────────────────────────────────────────

def _parse_ai_response(text: str, source: str) -> dict:
    code_match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    solution_code = code_match.group(1).strip() if code_match else None

    time_match = re.search(r"[Tt]ime.*?O\([^)]+\)", text)
    space_match = re.search(r"[Ss]pace.*?O\([^)]+\)", text)

    def extract_complexity(m):
        if not m:
            return None
        s = m.group(0)
        o_match = re.search(r"O\([^)]+\)", s)
        return o_match.group(0) if o_match else None

    return {
        "answer": text,
        "solution_code": solution_code,
        "time_complexity": extract_complexity(time_match),
        "space_complexity": extract_complexity(space_match),
        "source": source,
    }


# ── Local KB ──────────────────────────────────────────────────────────────────

def _ask_local_kb(prompt: str) -> dict:
    prompt_lower = prompt.lower()
    best, best_score = None, 0
    for entry in LOCAL_KB:
        score = sum(1 for kw in entry.get("keywords", []) if kw.lower() in prompt_lower)
        if score > best_score:
            best_score, best = score, entry
    if best and best_score > 0:
        return {
            "answer": best.get("answer", ""),
            "solution_code": best.get("code"),
            "time_complexity": best.get("time_complexity"),
            "space_complexity": best.get("space_complexity"),
            "source": "local_kb",
        }
    return {
        "answer": (
            "⚡ No answer found locally.\n\n"
            "**To enable AI answers:**\n"
            "- **Groq (free, fast):** Get key at console.groq.com → add `GROQ_API_KEY=your_key` to `.env`\n"
            "- **Ollama (offline):** Install from ollama.ai → run `ollama pull codellama`"
        ),
        "solution_code": None,
        "time_complexity": None,
        "space_complexity": None,
        "source": "local_kb",
    }


def get_ai_status() -> dict:
    """Returns which AI backends are available."""
    groq_ok = bool(GROQ_API_KEY)
    ollama_ok = False
    try:
        r = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        ollama_ok = r.status_code == 200
    except Exception:
        pass
    return {
        "groq": groq_ok,
        "ollama": ollama_ok,
        "active": "groq" if groq_ok else ("ollama" if ollama_ok else "local_kb"),
    }