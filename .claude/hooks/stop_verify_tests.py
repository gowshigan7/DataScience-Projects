#!/usr/bin/env python3
"""
stop_verify_tests.py
====================
Stop hook — nudges Claude to verify tests still pass before ending a session.

Inspects the stop event. If Claude modified any `.py` file during the session,
it prints a reminder to run the test suite. This does NOT block — it is an
advisory nudge only.

Triggered by: Stop event (Claude Code Stop hook).
"""

import json
import sys


def main() -> None:
    event = json.loads(sys.stdin.read())

    # Check if any Python files were touched in this turn
    tool_uses = event.get("tool_uses", [])
    py_files_touched = any(
        use.get("tool_name") in ("Edit", "Write", "MultiEdit")
        and (
            use.get("tool_input", {}).get("file_path", "").endswith(".py")
            or use.get("tool_input", {}).get("path", "").endswith(".py")
        )
        for use in tool_uses
    )

    if py_files_touched:
        print(
            "\n[hook:verify] Python files were modified this session.\n"
            "  Run: pytest restaurant_scraper/tests/ -v\n"
            "  All 89 tests must pass before committing.",
            flush=True,
        )


if __name__ == "__main__":
    main()
