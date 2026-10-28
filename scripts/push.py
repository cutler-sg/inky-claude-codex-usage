"""Stream an image to the Pi, retaining SSH's existing authentication."""

import argparse
import shlex
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--host", default="pi@inky.local")
    args, options = parser.parse_known_args()
    if args.host.startswith("-"):
        parser.error("host cannot start with -")
    command = shlex.join(
        ["/home/pi/inky/.venv/bin/python", "-m", "inky_frame", "show", "-", *options]
    )
    with args.image.open("rb") as source:
        result = subprocess.run(
            [
                "ssh",
                "-4",
                "-o",
                "BatchMode=yes",
                "-o",
                "ConnectTimeout=15",
                args.host,
                f"cd /home/pi/inky && {command}",
            ],
            stdin=source,
            check=False,
        )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
