"""
code_enhancer.py — CodeSense V2
Enhancements for Python (AST) and Java/JS/C (regex patterns).
"""

import ast
import re


def enhance_code(code: str, language: str = "python") -> dict:
    lang = language.lower()
    if lang == "python":
        return _enhance_python(code)
    return _enhance_generic(code, lang)


# ── Python ────────────────────────────────────────────────────────────────────

def _enhance_python(code: str) -> dict:
    enhancements = []
    enhanced = code

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"original_code": code, "enhanced_code": code,
                "enhancements": [], "improvement_score": "0 points"}

    enhanced, doc_enhancements = _add_docstrings(enhanced, tree)
    enhancements.extend(doc_enhancements)
    enhancements.extend(_detect_list_comprehension(tree))
    enhancements.extend(_detect_fstring(tree))
    enhancements.extend(_detect_redundant_var(tree))
    enhancements.extend(_detect_magic_numbers(tree))
    enhancements.extend(_detect_long_functions(tree))

    score = f"+{min(len(enhancements) * 5, 45)} points"
    return {"original_code": code, "enhanced_code": enhanced,
            "enhancements": enhancements, "improvement_score": score}


def _add_docstrings(code, tree):
    enhancements = []
    lines = code.splitlines()
    insertions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            has_doc = (node.body and isinstance(node.body[0], ast.Expr)
                       and isinstance(node.body[0].value, ast.Constant)
                       and isinstance(node.body[0].value.value, str))
            if not has_doc:
                indent = " " * (node.col_offset + 4)
                insertions.append((node.lineno, f'{indent}"""TODO: Add description for {node.name}."""'))
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                enhancements.append({"type": "docstring_added", "line": node.lineno,
                                     "description": f"Added docstring stub to {kind} '{node.name}'"})
    for line_no, text in sorted(insertions, reverse=True):
        lines.insert(line_no, text)
    return "\n".join(lines), enhancements


def _detect_list_comprehension(tree):
    hints = []
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and len(node.body) == 1:
            expr = node.body[0]
            if isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Call):
                call = expr.value
                if isinstance(call.func, ast.Attribute) and call.func.attr == "append":
                    hints.append({"type": "list_comprehension", "line": node.lineno,
                                  "description": f"For-loop with .append() → replace with list comprehension"})
    return hints


def _detect_fstring(tree):
    hints = []
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            if isinstance(node.left, ast.Constant) and isinstance(node.left.value, str):
                hints.append({"type": "fstring_upgrade", "line": getattr(node, "lineno", "?"),
                              "description": "String concatenation with '+' → use f-string for readability"})
    return hints


def _detect_redundant_var(tree):
    hints = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stmts = node.body
            if len(stmts) >= 2:
                last, second = stmts[-1], stmts[-2]
                if (isinstance(second, ast.Assign) and isinstance(last, ast.Return)
                        and isinstance(last.value, ast.Name)
                        and isinstance(second.targets[0], ast.Name)
                        and second.targets[0].id == last.value.id):
                    hints.append({"type": "redundant_variable", "line": second.lineno,
                                  "description": f"Variable '{last.value.id}' assigned then immediately returned → return directly"})
    return hints


def _detect_magic_numbers(tree):
    seen, hints = set(), []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            v = node.value
            if v not in (0, 1, -1, 2, 100) and v not in seen:
                seen.add(v)
                hints.append({"type": "magic_number", "line": getattr(node, "lineno", "?"),
                              "description": f"Magic number '{v}' → define as named constant"})
    return hints[:3]


def _detect_long_functions(tree):
    hints = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "end_lineno"):
                length = node.end_lineno - node.lineno
                if length > 40:
                    hints.append({"type": "long_function", "line": node.lineno,
                                  "description": f"Function '{node.name}' is {length} lines → split into helpers (<20 lines each)"})
    return hints


# ── Generic (Java / JS / C) ───────────────────────────────────────────────────

def _enhance_generic(code: str, lang: str) -> dict:
    enhancements = []

    if lang == "java":
        enhancements.extend(_java_enhancements(code))
    elif lang == "javascript":
        enhancements.extend(_js_enhancements(code))
    elif lang == "c":
        enhancements.extend(_c_enhancements(code))

    score = f"+{min(len(enhancements) * 5, 45)} points"
    return {"original_code": code, "enhanced_code": code,
            "enhancements": enhancements, "improvement_score": score}


def _java_enhancements(code):
    hints = []
    if re.search(r'for\s*\(.*:\s*\w+\)', code) is None and re.search(r'for\s*\(int\s+\w+\s*=\s*0', code):
        hints.append({"type": "enhanced_for", "line": "?",
                      "description": "Traditional for-loop → consider enhanced for-each loop when iterating collections"})
    if re.search(r'String\s+\w+\s*=\s*""', code) and re.search(r'\+=', code):
        hints.append({"type": "string_builder", "line": "?",
                      "description": "String concatenation in loop → use StringBuilder for O(n) instead of O(n²)"})
    if not re.search(r'private|public|protected', code):
        hints.append({"type": "access_modifiers", "line": "?",
                      "description": "Add access modifiers (private/public) to fields and methods"})
    return hints


def _js_enhancements(code):
    hints = []
    if re.search(r'\.forEach\(|\.map\(|\.filter\(|\.reduce\(', code) is None and re.search(r'for\s*\(', code):
        hints.append({"type": "array_methods", "line": "?",
                      "description": "Traditional loop → consider Array methods (map/filter/reduce) for cleaner code"})
    if re.search(r'function\s+\w+\s*\(', code):
        hints.append({"type": "arrow_function", "line": "?",
                      "description": "Regular function → consider arrow function syntax for conciseness"})
    if re.search(r'\.then\(', code) and not re.search(r'async|await', code):
        hints.append({"type": "async_await", "line": "?",
                      "description": "Promise chains → consider async/await for more readable async code"})
    return hints


def _c_enhancements(code):
    hints = []
    if re.search(r'#define\s+\w+\s+\d+', code) is None and re.search(r'\b\d{2,}\b', code):
        hints.append({"type": "constants", "line": "?",
                      "description": "Magic numbers detected → use #define or const for named constants"})
    if not re.search(r'/\*\*|\/\/', code):
        hints.append({"type": "documentation", "line": "?",
                      "description": "No comments found → add /* */ comments to explain logic"})
    if re.search(r'\*\w+\s*=\s*malloc', code) and not re.search(r'if\s*\(\s*\w+\s*==\s*NULL', code):
        hints.append({"type": "null_check", "line": "?",
                      "description": "malloc() result not checked for NULL → always verify allocation success"})
    return hints
