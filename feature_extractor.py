"""
feature_extractor.py — CodeSense V2
Extracts ML features for Python (AST), Java, JavaScript, C (regex-based).
"""

import ast
import re


SUPPORTED = {"python", "java", "javascript", "c"}


def extract_features(code: str, language: str = "python") -> dict:
    lang = language.lower()
    if lang == "python":
        return _python_features(code)
    elif lang in ("java", "javascript", "c"):
        return _regex_features(code, lang)
    return _regex_features(code, "python")


# ── Python (AST) ──────────────────────────────────────────────────────────────

def _python_features(code: str) -> dict:
    features = {
        "lines_of_code": 0, "num_functions": 0, "num_loops": 0,
        "num_conditionals": 0, "num_classes": 0, "avg_function_length": 0.0,
        "comment_ratio": 0.0, "naming_score": 0.0,
        "import_count": 0, "nested_depth": 0,
    }
    lines = code.splitlines()
    features["lines_of_code"] = len(lines)
    comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
    features["comment_ratio"] = round(comment_lines / max(len(lines), 1), 2)

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return features

    func_lengths = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            features["num_functions"] += 1
            if hasattr(node, "end_lineno"):
                func_lengths.append(node.end_lineno - node.lineno + 1)
        elif isinstance(node, (ast.For, ast.While)):
            features["num_loops"] += 1
        elif isinstance(node, ast.If):
            features["num_conditionals"] += 1
        elif isinstance(node, ast.ClassDef):
            features["num_classes"] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            features["import_count"] += 1

    if func_lengths:
        features["avg_function_length"] = round(sum(func_lengths) / len(func_lengths), 2)

    features["naming_score"] = _python_naming_score(tree)
    features["nested_depth"] = _max_nesting_python(tree)
    return features


def _python_naming_score(tree):
    pattern = re.compile(r"^[a-z_][a-z0-9_]*$")
    names = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
        elif isinstance(node, ast.Name):
            names.append(node.id)
    if not names:
        return 1.0
    return round(sum(1 for n in names if pattern.match(n)) / len(names), 2)


def _max_nesting_python(node, depth=0):
    max_d = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.For, ast.While, ast.If)):
            max_d = max(max_d, _max_nesting_python(child, depth + 1))
        else:
            max_d = max(max_d, _max_nesting_python(child, depth))
    return max_d


# ── Regex-based (Java / JavaScript / C) ──────────────────────────────────────

def _regex_features(code: str, lang: str) -> dict:
    lines = code.splitlines()
    loc = len(lines)

    # Comments
    if lang == "python":
        comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
    elif lang in ("java", "javascript", "c"):
        comment_lines = sum(1 for l in lines if l.strip().startswith("//") or l.strip().startswith("*"))
    else:
        comment_lines = 0

    # Functions/methods
    if lang == "java":
        func_pattern = r'(public|private|protected|static|void|int|String|boolean|double|float)\s+\w+\s*\('
    elif lang == "javascript":
        func_pattern = r'(function\s+\w+|const\s+\w+\s*=\s*(async\s*)?\(|\w+\s*:\s*function|\w+\s*=\s*\()'
    elif lang == "c":
        func_pattern = r'(int|void|char|float|double|long|short)\s+\w+\s*\('
    else:
        func_pattern = r'def\s+\w+'

    num_functions = len(re.findall(func_pattern, code))

    # Loops
    num_loops = len(re.findall(r'\b(for|while)\b\s*\(', code))
    if lang == "python":
        num_loops = len(re.findall(r'\bfor\b|\bwhile\b', code))

    # Conditionals
    num_conditionals = len(re.findall(r'\bif\b\s*[\(\{]?', code))

    # Classes
    if lang == "java":
        num_classes = len(re.findall(r'\bclass\s+\w+', code))
    elif lang == "javascript":
        num_classes = len(re.findall(r'\bclass\s+\w+', code))
    else:
        num_classes = 0

    # Imports / includes
    if lang in ("java",):
        imports = len(re.findall(r'\bimport\b', code))
    elif lang == "javascript":
        imports = len(re.findall(r'\b(import|require)\b', code))
    elif lang == "c":
        imports = len(re.findall(r'#include', code))
    else:
        imports = 0

    # Nested depth — count max consecutive braces indentation
    max_depth = _estimate_nesting_depth(code)

    # Naming score — simplified (camelCase for Java/JS, snake for C/Python)
    naming_score = 0.7  # default reasonable for compiled languages

    return {
        "lines_of_code": loc,
        "num_functions": num_functions,
        "num_loops": num_loops,
        "num_conditionals": num_conditionals,
        "num_classes": num_classes,
        "avg_function_length": round(loc / max(num_functions, 1), 1),
        "comment_ratio": round(comment_lines / max(loc, 1), 2),
        "naming_score": naming_score,
        "import_count": imports,
        "nested_depth": max_depth,
    }


def _estimate_nesting_depth(code: str) -> int:
    max_depth = current = 0
    for ch in code:
        if ch == "{":
            current += 1
            max_depth = max(max_depth, current)
        elif ch == "}":
            current = max(0, current - 1)
    return max_depth
