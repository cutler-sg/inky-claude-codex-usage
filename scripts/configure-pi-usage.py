"""Transfer CLIProxyAPI configuration from macOS Keychain over SSH, without logging it."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from inky_frame.proxy import proxy_url

INSTALL = """
import json, os, pathlib, sys
data = json.load(sys.stdin)
def quoted(value):
    if not isinstance(value, str) or not value or any(c in value for c in "\\n\\r\\0"):
        raise ValueError("Invalid configuration value")
    return '"' + value.replace('\\\\', '\\\\\\\\').replace('"', '\\\\"') + '"'
content = "".join(name + "=" + quoted(data[name]) + "\\n" for name in (
    "CLI_PROXY_API_BASE_URL", "CLI_PROXY_API_MANAGEMENT_KEY"))
directory = pathlib.Path("/etc/inky")
directory.mkdir(mode=0o700, exist_ok=True)
os.chmod(directory, 0o700)
temporary = directory / "usage.env.tmp"
descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
os.fchmod(descriptor, 0o600)
with os.fdopen(descriptor, "w") as output:
    output.write(content)
temporary.replace(directory / "usage.env")
print("Installed protected CLIProxyAPI configuration (root-owned, mode 0600).")
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="pi@inky.local")
    parser.add_argument("--proxy-url", required=True, type=proxy_url)
    parser.add_argument("--keychain-service", default="cliproxyapi-management")
    args = parser.parse_args()
    if args.host.startswith("-"):
        parser.error("Invalid SSH host")
    if sys.platform != "darwin":
        parser.error(
            "This helper reads macOS Keychain; configure /etc/inky/usage.env on other hosts"
        )
    result = subprocess.run(
        ["security", "find-generic-password", "-s", args.keychain_service, "-w"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    key = result.stdout.strip()
    if result.returncode != 0 or not key:
        parser.exit(1, "Cannot read the management credential from Keychain\n")
    if any(char in key for char in "\n\r\0"):
        parser.exit(1, "The management credential must be a single line\n")
    payload = {"CLI_PROXY_API_BASE_URL": args.proxy_url, "CLI_PROXY_API_MANAGEMENT_KEY": key}
    subprocess.run(
        [
            "ssh",
            "-4",
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=15",
            args.host,
            shlex.join(["sudo", "-n", "python3", "-c", INSTALL]),
        ],
        input=json.dumps(payload),
        text=True,
        check=True,
        timeout=45,
    )


if __name__ == "__main__":
    main()
