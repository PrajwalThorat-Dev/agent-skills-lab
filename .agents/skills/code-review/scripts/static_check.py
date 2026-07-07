"""
static_check.py

Optional helper for the code-review skill. Run against a Python file to
surface objective signals that support Step 4 (Readability & Maintainability)
of the review. This script does NOT judge severity or write the review — it
only reports raw facts. The model applies references/severity-levels.md to
decide what matters.

Usage:
    python static_check.py <path_to_file.py>
"""

import ast
import sys
from pathlib import Path


def find_unused_imports(tree: ast.Module, source: str) -> list[str]:
    """Flags imports that never appear again in the source text by name."""
    imported_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.append(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.append(alias.asname or alias.name)

    unused = []
    for name in imported_names:
        # crude but effective: count occurrences of the name in source,
        # more than 1 means it's used somewhere beyond its own import line
        if source.count(name) <= 1:
            unused.append(name)
    return unused


def find_long_functions(tree: ast.Module, max_lines: int = 40) -> list[dict]:
    """Flags functions/methods exceeding max_lines in body length."""
    long_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, "end_lineno") and node.end_lineno:
                length = node.end_lineno - node.lineno
                if length > max_lines:
                    long_funcs.append({"name": node.name, "lines": length})
    return long_funcs


def estimate_nesting_depth(tree: ast.Module) -> list[dict]:
    """
    Estimates max nesting depth per function by walking control-flow nodes
    (if/for/while/try/with). Not a full cyclomatic complexity calculation,
    just a fast structural signal.
    """
    results = []

    def depth_of(node, current=0):
        max_depth = current
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                max_depth = max(max_depth, depth_of(child, current + 1))
            else:
                max_depth = max(max_depth, depth_of(child, current))
        return max_depth

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            depth = depth_of(node)
            if depth >= 3:  # only report when it's notable
                results.append({"name": node.name, "max_nesting_depth": depth})

    return results


def run_checks(filepath: str) -> dict:
    path = Path(filepath)
    if not path.exists():
        return {"error": f"File not found: {filepath}"}

    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"Syntax error, cannot analyze: {e}"}

    return {
        "unused_imports": find_unused_imports(tree, source),
        "long_functions": find_long_functions(tree),
        "deeply_nested_functions": estimate_nesting_depth(tree),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python static_check.py <path_to_file.py>")
        sys.exit(1)

    results = run_checks(sys.argv[1])

    print("=== Static Check Results ===\n")

    if "error" in results:
        print(results["error"])
        sys.exit(1)

    if results["unused_imports"]:
        print(f"Unused imports ({len(results['unused_imports'])}):")
        for name in results["unused_imports"]:
            print(f"  - {name}")
    else:
        print("Unused imports: none detected")

    print()

    if results["long_functions"]:
        print(f"Long functions (>40 lines):")
        for f in results["long_functions"]:
            print(f"  - {f['name']} ({f['lines']} lines)")
    else:
        print("Long functions: none detected")

    print()

    if results["deeply_nested_functions"]:
        print("Deeply nested functions (depth >= 3):")
        for f in results["deeply_nested_functions"]:
            print(f"  - {f['name']} (depth {f['max_nesting_depth']})")
    else:
        print("Deep nesting: none detected")