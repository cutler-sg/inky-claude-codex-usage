"""Install the ten-minute credential-preserving Mac usage sync job."""

import argparse
import os
import plistlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABEL = "com.cotdp.inky-usage"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="pi@inky.local")
    parser.add_argument(
        "--collector",
        type=Path,
        required=True,
        help="Path to the external usage collector module (see README)",
    )
    args = parser.parse_args()
    agent = Path.home() / "Library/LaunchAgents" / f"{LABEL}.plist"
    state = ROOT / "state"
    state.mkdir(exist_ok=True)
    agent.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "Label": LABEL,
        "ProgramArguments": [
            str(ROOT / ".venv/bin/python"),
            str(ROOT / "scripts/sync-usage.py"),
            "--host",
            args.host,
            "--collector",
            str(args.collector.resolve()),
        ],
        "WorkingDirectory": str(ROOT),
        "StartInterval": 600,
        "RunAtLoad": True,
        "StandardOutPath": str(state / "usage-sync.log"),
        "StandardErrorPath": str(state / "usage-sync-error.log"),
        "EnvironmentVariables": {"PATH": "/opt/homebrew/bin:/usr/bin:/bin"},
        "ProcessType": "Background",
    }
    agent.write_bytes(plistlib.dumps(config))
    domain = f"gui/{os.getuid()}"
    target = f"{domain}/{LABEL}"
    exists = subprocess.run(["launchctl", "print", target], capture_output=True).returncode == 0
    if exists:
        subprocess.run(["launchctl", "bootout", target], check=True)
    subprocess.run(["launchctl", "enable", target], check=True)
    subprocess.run(["launchctl", "bootstrap", domain, str(agent)], check=True)
    print(f"Installed {agent}; sync runs now, every ten minutes, and after login.")


if __name__ == "__main__":
    main()
