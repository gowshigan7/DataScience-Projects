"""
main.py
=======
CLI entry point for the Hermes Village.

Description :
    Loads Hermes state (or the simulated demo), builds a VillageSnapshot and
    prints it as a terminal village or as JSON. With --watch it redraws
    every N seconds. Read-only: nothing under ~/.hermes is ever written.

Use cases :
    python -m hermes_bridge.main --demo
    python -m hermes_bridge.main --watch 5
    python -m hermes_bridge.main --json > snapshot.json   # for the 3D step

Input  : CLI arguments, ~/.hermes (or --hermes-home)
Output : Terminal village or snapshot JSON on stdout
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from hermes_bridge import config
from hermes_bridge.demo_data import demo_hermes
from hermes_bridge.village_state import build_snapshot, load_hermes_home
from hermes_bridge.village_tui import render_village


def parse_args(argv=None):
    """Parse CLI arguments.

    Args:
        argv (list[str] | None): Arguments; defaults to sys.argv.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Hermes Village: your agents as a little town.")
    parser.add_argument("--hermes-home", type=Path, default=config.HERMES_HOME,
                        help="Hermes home directory (default: ~/.hermes or $HERMES_HOME)")
    parser.add_argument("--demo", action="store_true", help="Use simulated Hermes data")
    parser.add_argument("--json", action="store_true", help="Print the snapshot as JSON")
    parser.add_argument("--watch", type=float, nargs="?", const=config.WATCH_DEFAULT_SECONDS,
                        metavar="SECONDS", help="Redraw every N seconds (Ctrl-C to stop)")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    return parser.parse_args(argv)


def snapshot_for(args):
    """Build a snapshot from the demo or the real Hermes home.

    Args:
        args (argparse.Namespace): Parsed CLI arguments.

    Returns:
        dict: VillageSnapshot.
    """
    now = datetime.now().astimezone()
    jobs, gateway = demo_hermes(now) if args.demo else load_hermes_home(args.hermes_home)
    return build_snapshot(jobs, gateway, now)


def main(argv=None):
    """Run the CLI.

    Args:
        argv (list[str] | None): Arguments; defaults to sys.argv.

    Returns:
        None
    """
    args = parse_args(argv)
    while True:
        snapshot = snapshot_for(args)
        if args.json:
            out = json.dumps(snapshot, indent=2, ensure_ascii=False)
        else:
            out = render_village(snapshot, color=not args.no_color)
        if args.watch:
            print(config.ANSI_CLEAR + out, flush=True)
            try:
                time.sleep(args.watch)
            except KeyboardInterrupt:
                return
        else:
            print(out)
            return


if __name__ == "__main__":
    main()
