"""
code_fixer.py — CodeSense V2
Auto-fix for Python (autopep8 + AST) and basic fixes for Java/JS/C.
"""

import ast
import re
import subprocess
import sys
import tempfile
import os


def fix_code(code: str, language: str = "python") -> dict:
    lang = language.lower()
    if lang == "python":
        return _fix_python(code)
    return _fix_generic(code, lang)


# ── Python ────────────────────────────────────────────────────────────────────

def _fix_python(code: str) -> dict:
    fixes_applied = []
    remaining = []

    fixed, pep8_fixes = _run_autopep8(code)
    fixes_applied.extend(pep8_fixes)

    try:
        tree = ast.parse(fixed)
        ast_fixes, ast_remaining = _ast_checks(fixed, tree)
        fixes_applied.extend(ast_fixes)
        remaining.extend(ast_remaining)
    except SyntaxError as e:
        remaining.append(f"Syntax error at line {e.lineno}: {e.msg}")

    return {"original_code": code, "fixed_code": fixed,
            "fixes_applied": fixes_applied, "remaining_issues": remaining}


def _run_autopep8(code: str):
    fixes = []
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "autopep8", "--aggressive", "--aggressive", tmp],
            capture_output=True, text=True, timeout=15
        )
        fixed = result.stdout if result.stdout else code
        if fixed.strip() != code.strip():
            fixes.append("PEP8 auto-formatting applied (indentation, spacing, blank lines)")
        return fixed, fixes
    except Exception:
        return code, []
    finally:
        try: os.unlink(tmp)
        except: pass


def _ast_checks(code, tree):
    fixes, issues = [], []
    # Unused imports
    imported, used = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported.add((a.asname or a.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for a in node.names:
                imported.add((a.asname or a.name, node.lineno))
        elif isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            used.add(node.value.id)
    for name, lineno in imported:
        if name not in used and name != "*":
            issues.append(f"Unused import '{name}' at line {lineno}")

    # Bare except
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            issues.append(f"Bare 'except:' at line {node.lineno} — use 'except Exception as e:'")
        if isinstance(node, ast.Compare):
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant) and comp.value is None:
                    issues.append(f"Use 'is None' instead of '== None' at line {node.lineno}")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in node.args.defaults:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    issues.append(f"Mutable default arg in '{node.name}' at line {node.lineno}")
    return fixes, issues


# ── Generic (Java / JS / C) ───────────────────────────────────────────────────

def _fix_generic(code: str, lang: str) -> dict:
    fixes_applied = []
    remaining = []
    fixed = code

    # Fix: trailing whitespace
    lines = fixed.splitlines()
    cleaned = [l.rstrip() for l in lines]
    if cleaned != lines:
        fixes_applied.append("Removed trailing whitespace from all lines")
    fixed = "\n".join(cleaned)

    # Fix: multiple blank lines → single
    new_fixed = re.sub(r'\n{3,}', '\n\n', fixed)
    if new_fixed != fixed:
        fixes_applied.append("Collapsed multiple blank lines")
    fixed = new_fixed

    # Language-specific checks
    if lang == "java":
        remaining.extend(_java_checks(code))
    elif lang == "javascript":
        remaining.extend(_js_checks(code))
    elif lang == "c":
        remaining.extend(_c_checks(code))

    if not fixes_applied:
        fixes_applied.append("No automatic formatting issues found")

    return {"original_code": code, "fixed_code": fixed,
            "fixes_applied": fixes_applied, "remaining_issues": remaining}


def _java_checks(code: str) -> list:
    issues = []
    if re.search(r'catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}', code):
        issues.append("Empty catch block detected — handle or log the exception")
    if re.search(r'==\s*null|null\s*==', code):
        issues.append("Use Objects.isNull() or != null check — be explicit")
    if not re.search(r'@Override', code) and re.search(r'public\s+\w+\s+toString\s*\(', code):
        issues.append("Missing @Override annotation on toString()")
    if re.search(r'System\.out\.print', code):
        issues.append("Replace System.out.print with a logger in production code")
    return issues


def _js_checks(code: str) -> list:
    issues = []
    if re.search(r'\bvar\b', code):
        issues.append("Use 'const' or 'let' instead of 'var' (modern JS)")
    if re.search(r'==(?!=)', code):
        issues.append("Use '===' instead of '==' for strict equality in JavaScript")
    if re.search(r'console\.log', code):
        issues.append("Remove console.log statements before production")
    if not re.search(r"'use strict'|\"use strict\"", code) and not re.search(r'\bimport\b|\bexport\b', code):
        issues.append("Consider adding 'use strict' at the top of your file")
    return issues


def _c_checks(code: str) -> list:
    issues = []
    if re.search(r'\bgets\s*\(', code):
        issues.append("DANGEROUS: Replace gets() with fgets() — buffer overflow risk")
    if re.search(r'\bscanf\s*\(\s*"%s"', code):
        issues.append("RISKY: Use scanf(\"%Ns\") with width limit to prevent overflow")
    if re.search(r'\bmalloc\b', code) and not re.search(r'\bfree\b', code):
        issues.append("malloc() detected without free() — potential memory leak")
    if not re.search(r'#include\s*<stdio\.h>', code) and re.search(r'\bprintf\b|\bscanf\b', code):
        issues.append("Missing #include <stdio.h> for printf/scanf")
    return issues
