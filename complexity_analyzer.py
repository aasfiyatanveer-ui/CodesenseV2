"""
complexity_analyzer.py — CodeSense V2
Time & Space complexity for Python (AST) + Java/JS/C (regex patterns).
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ComplexityResult:
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    explanation: str = ""
    bottlenecks: List[dict] = field(default_factory=list)
    optimization_hint: str = ""


def analyze_complexity(code: str, language: str = "python") -> ComplexityResult:
    lang = language.lower()
    if lang == "python":
        return _python_complexity(code)
    return _generic_complexity(code, lang)


# ── Python (full AST analysis) ────────────────────────────────────────────────

def _python_complexity(code: str) -> ComplexityResult:
    result = ComplexityResult()
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        result.explanation = f"Syntax error: {e}"
        return result

    loop_depth   = _max_loop_nesting(tree)
    has_rec      = _has_recursion(tree)
    has_exp_rec  = _has_exponential_recursion(tree)
    has_sort     = _uses_sorting(tree)
    has_bin      = _has_binary_search(tree)
    has_graph    = _has_bfs_dfs(tree)
    bottlenecks  = _find_bottlenecks(tree)

    if has_exp_rec:
        result.time_complexity = "O(2ⁿ)"
        result.explanation = "Exponential recursion (e.g. naive Fibonacci). Each call branches into two."
        result.optimization_hint = "Use memoization (@lru_cache) to reduce to O(n)."
    elif has_rec:
        result.time_complexity = "O(n)"
        result.explanation = "Linear recursion detected. Depth scales with input size."
        result.optimization_hint = "Consider iterative or memoized approach."
    elif has_graph:
        result.time_complexity = "O(V + E)"
        result.explanation = "Graph traversal (BFS/DFS). Visits every vertex and edge once."
        result.optimization_hint = "Already optimal for graph traversal."
    elif has_bin:
        result.time_complexity = "O(log n)"
        result.explanation = "Binary search pattern — search space halves each step."
        result.optimization_hint = "Consider using Python's bisect module."
    elif has_sort and loop_depth >= 1:
        result.time_complexity = f"O(n log n + {_loop_big_o(loop_depth)})"
        result.explanation = f"Sort O(n log n) + {loop_depth} loop(s) O({_loop_big_o(loop_depth)})."
        result.optimization_hint = "Avoid sorting inside loops."
    elif has_sort:
        result.time_complexity = "O(n log n)"
        result.explanation = "Sorting (Python Timsort). Optimal comparison-based sort."
        result.optimization_hint = "Already efficient. Avoid re-sorting in loops."
    else:
        result.time_complexity = _loop_big_o(loop_depth)
        result.explanation = _loop_explanation(loop_depth)
        result.optimization_hint = _loop_hint(loop_depth)

    result.space_complexity = _python_space(tree, loop_depth, has_rec)
    result.bottlenecks = bottlenecks
    return result


def _loop_big_o(depth):
    return {0: "O(1)", 1: "O(n)", 2: "O(n²)", 3: "O(n³)"}.get(depth, f"O(n^{depth})")


def _loop_explanation(depth):
    if depth == 0: return "No loops — constant time operations only."
    if depth == 1: return "Single loop over input of size n → O(n)."
    if depth == 2: return "Two nested loops over n elements → O(n²)."
    return f"{depth} levels of nested loops → O(n^{depth})."


def _loop_hint(depth):
    if depth == 0: return "Code is already O(1) — optimal!"
    if depth == 1: return "Good. Avoid adding nested loops."
    if depth == 2: return "Use a hash map (dict) to reduce one loop → O(n)."
    return "Refactor using DP, hash maps, or sorting to reduce complexity."


def _python_space(tree, loop_depth, has_rec):
    if has_rec: return "O(n)"
    if _grows_structure_in_loop(tree): return "O(n)"
    return "O(1)"


def _max_loop_nesting(node, depth=0):
    m = depth
    for c in ast.iter_child_nodes(node):
        if isinstance(c, (ast.For, ast.While)):
            m = max(m, _max_loop_nesting(c, depth + 1))
        else:
            m = max(m, _max_loop_nesting(c, depth))
    return m


def _has_recursion(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = node.name
            for c in ast.walk(node):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == fn:
                    return True
    return False


def _has_exponential_recursion(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = node.name
            cnt = sum(1 for c in ast.walk(node)
                      if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == fn)
            if cnt >= 2:
                return True
    return False


def _uses_sorting(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "sorted": return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == "sort": return True
    return False


def _has_binary_search(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            for c in ast.walk(node):
                if isinstance(c, ast.BinOp) and isinstance(c.op, ast.FloorDiv):
                    return True
    return False


def _has_bfs_dfs(tree):
    methods = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    return {"append", "popleft"}.issubset(methods) or {"append", "pop"}.issubset(methods)


def _grows_structure_in_loop(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            for c in ast.walk(node):
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute):
                    if c.func.attr in ("append", "add", "update", "extend"):
                        return True
    return False


def _find_bottlenecks(tree):
    bottlenecks = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            for c in ast.walk(node):
                if c is node: continue
                if isinstance(c, (ast.For, ast.While)):
                    bottlenecks.append({"line": getattr(c, "lineno", "?"),
                                        "issue": "Inner loop → O(n²) or worse"})
                    break
    return bottlenecks


# ── Generic (Java / JavaScript / C) — regex ───────────────────────────────────

def _generic_complexity(code: str, lang: str) -> ComplexityResult:
    result = ComplexityResult()

    # Count loop nesting via indentation / brace depth
    max_loop_depth = _count_nested_loops_regex(code)

    # Recursion detection — function calls itself
    has_recursion = _detect_recursion_regex(code)

    # Sort calls
    has_sort = bool(re.search(r'\bsort\b|Arrays\.sort|Collections\.sort|\.sort\(', code))

    # Binary search
    has_bin = bool(re.search(r'\b(lo|low|left)\b.*\b(hi|high|right)\b', code, re.IGNORECASE))

    if has_recursion:
        result.time_complexity = "O(n)"
        result.explanation = "Recursive call detected. Depth scales with input."
        result.optimization_hint = "Verify recursion depth. Consider iterative solution."
    elif has_bin:
        result.time_complexity = "O(log n)"
        result.explanation = "Binary search pattern (lo/hi pointers) detected."
        result.optimization_hint = "Already optimal for sorted search."
    elif has_sort and max_loop_depth >= 1:
        result.time_complexity = "O(n log n)"
        result.explanation = "Sort + loops detected. Sort dominates."
        result.optimization_hint = "Avoid sorting inside loops."
    elif has_sort:
        result.time_complexity = "O(n log n)"
        result.explanation = "Sort operation detected — O(n log n)."
        result.optimization_hint = "Standard sort is already optimal."
    else:
        result.time_complexity = _loop_big_o(max_loop_depth)
        result.explanation = _loop_explanation(max_loop_depth)
        result.optimization_hint = _loop_hint(max_loop_depth)

    # Space complexity
    creates_arrays = bool(re.search(r'new\s+(int|String|char|double|ArrayList|List)\[', code))
    result.space_complexity = "O(n)" if creates_arrays or has_recursion else "O(1)"
    result.bottlenecks = _find_bottlenecks_regex(code)
    return result


def _count_nested_loops_regex(code: str) -> int:
    lines = code.splitlines()
    max_depth = cur = 0
    for line in lines:
        stripped = line.strip()
        if re.match(r'\b(for|while)\b', stripped):
            cur += 1
            max_depth = max(max_depth, cur)
        if '}' in stripped and cur > 0:
            cur -= 1
    return max_depth


def _detect_recursion_regex(code: str) -> bool:
    # Find function names then check if they call themselves
    func_names = re.findall(r'(?:function|void|int|String|def)\s+(\w+)\s*\(', code)
    for fn in func_names:
        calls = re.findall(rf'\b{fn}\s*\(', code)
        if len(calls) > 1:
            return True
    return False


def _find_bottlenecks_regex(code: str) -> list:
    bottlenecks = []
    lines = code.splitlines()
    depth = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r'\b(for|while)\b', stripped):
            depth += 1
            if depth >= 2:
                bottlenecks.append({"line": i, "issue": f"Nested loop depth {depth} → O(n^{depth})"})
        if '}' in stripped and depth > 0:
            depth -= 1
    return bottlenecks
