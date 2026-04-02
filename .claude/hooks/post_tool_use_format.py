#!/usr/bin/env python3
"""
post_tool_use_format.py
=======================
PostToolUse hook — auto-formats Python files after Edit or Write tool calls.

Runs `python -m py_compile` to catch syntax errors immediately, so CI never
fails on a trivially broken file. If pyflakes is available it also runs a
quick lint pass.

Triggered by: Edit, Write tool use events (Claude Code PostToolUse hook).
"""

import json
import subprocess
import sys


def main() -> None:
    event = json.loads(sys.stdin.read())

    tool_name = event.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        return

    file_path = (
        event.get("tool_input", {}).get("file_path")
        or event.get("tool_input", {}).get("path", "")
    )

    if not file_path or not file_path.endswith(".py"):
        return

    # Syntax check — fast, always available
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", file_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[hook:format] Syntax error in {file_path}:\n{result.stderr}", flush=True)
        sys.exit(1)

    # Optional: pyflakes lint pass
    lint = subprocess.run(
        [sys.executable, "-m", "pyflakes", file_path],
        capture_output=True,
        text=True,
    )
    if lint.returncode != 0 and lint.stdout.strip():
        # Print warnings but don't block — linting is advisory only
        print(f"[hook:format] pyflakes {file_path}:\n{lint.stdout}", flush=True)


if __name__ == "__main__":
    main()
