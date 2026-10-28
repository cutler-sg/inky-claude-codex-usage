"""Fetch sanitized subscription usage on the Mac and atomically send it to the Pi."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from inky_frame.__main__ import ROOT, display_lock
from inky_frame.collect import collect
from inky_frame.usage import atomic_json, load_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="pi@inky.local")
    parser.add_argument(
        "--collector",
        type=Path,
        default=Path.home() / "workspaces/scripts/claude/claude_usage.py",
    )
    parser.add_argument("--local-only", action="store_true")
    args = parser.parse_args()
    if args.host.startswith("-"):
        parser.error("Invalid SSH host")
    state = ROOT / "state"
    with display_lock(state / "sync"):
        path = state / "usage.json"
        previous = load_snapshot(path) if path.exists() else None
        snapshot = collect(args.collector, previous)
        atomic_json(path, snapshot)
        print(
            json.dumps({"event": "usage_collected", "providers": snapshot["providers"]}), flush=True
        )
        if not args.local_only:
            subprocess.run(
                [
                    "ssh",
                    "-4",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=15",
                    args.host,
                    "cd /home/pi/inky && .venv/bin/python -m inky_frame.gallery receive",
                ],
                input=json.dumps(snapshot),
                text=True,
                check=True,
                timeout=45,
            )


if __name__ == "__main__":
    main()
