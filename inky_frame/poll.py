"""Fetch usage directly on the Pi and atomically update its local gallery snapshot."""

import argparse
import json

from .__main__ import STATE, display_lock
from .collect import collect
from .usage import atomic_json, load_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        with display_lock(STATE / "sync"):
            path = STATE / "usage.json"
            previous = load_snapshot(path) if path.exists() else None
            snapshot = collect(previous=previous)
            atomic_json(path, snapshot)
            providers = {
                name: {
                    "observed_at": provider["observed_at"],
                    "error": provider["error"],
                    "windows": len(provider["windows"]),
                }
                for name, provider in snapshot["providers"].items()
            }
            print(json.dumps({"event": "usage_polled", "providers": providers}), flush=True)
            if any(provider["error"] for provider in snapshot["providers"].values()):
                parser.exit(1, "inky poll: one or more providers could not be refreshed\n")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"inky poll: {error}\n")


if __name__ == "__main__":
    main()
