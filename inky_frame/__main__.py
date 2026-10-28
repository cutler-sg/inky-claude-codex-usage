import argparse
import hashlib
import json
import math
import sys
import time
from contextlib import contextmanager
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .images import RESOLUTION, prepare, sample

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"


class DisplayError(RuntimeError):
    pass


def saturation_value(value: str) -> float:
    result = float(value)
    if not math.isfinite(result) or not 0 <= result <= 1:
        raise argparse.ArgumentTypeError("saturation must be between 0 and 1")
    return result


def load_image(path: str, fit: str, rotation: int) -> Image.Image:
    source = sys.stdin.buffer if path == "-" else Path(path)
    with Image.open(source) as image:
        return prepare(image, fit, rotation)


@contextmanager
def display_lock(directory: Path):
    import fcntl

    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "display.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise DisplayError(
                "A display update is already running; retry after it completes"
            ) from error
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def read_display():
    from inky import eeprom
    from inky.auto import auto

    identity = eeprom.read_eeprom()
    if identity is None:
        raise DisplayError("No display EEPROM at I2C 0x50; check I2C and the 40-pin connection")
    if (identity.width, identity.height, identity.display_variant) != (600, 448, 14):
        raise DisplayError(f"Expected a 600x448 UC8159 panel; detected {identity!r}")
    return auto(), identity


def show(image: Image.Image, saturation: float, force: bool) -> None:
    with display_lock(STATE):
        display, _ = read_display()
        digest = hashlib.sha256(image.tobytes() + str(saturation).encode()).hexdigest()
        status_path = STATE / "status.json"
        previous = json.loads(status_path.read_text()) if status_path.exists() else {}
        if previous.get("sha256") == digest and not force:
            print(json.dumps({"event": "unchanged", "sha256": digest}))
            return
        started = time.monotonic()
        print(json.dumps({"event": "refresh_started", "resolution": RESOLUTION}), flush=True)
        display.set_image(image, saturation=saturation)
        display.show()
        image.save(STATE / "current.tmp.png")
        (STATE / "current.tmp.png").replace(STATE / "current.png")
        status = {
            "event": "refresh_completed",
            "sha256": digest,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "duration_seconds": round(time.monotonic() - started, 2),
            "saturation": saturation,
        }
        temporary = STATE / "status.tmp.json"
        temporary.write_text(json.dumps(status, indent=2) + "\n")
        temporary.replace(status_path)
        print(json.dumps(status), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Control the 600x448 Inky Impression over SSH")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("info", help="Read display EEPROM without refreshing")
    sample_parser = commands.add_parser("sample", help="Generate the sample image without hardware")
    sample_parser.add_argument("output", type=Path)
    for command in ("prepare", "show"):
        sub = commands.add_parser(command)
        sub.add_argument("image", help="Image path, or - for stdin")
        sub.add_argument("--fit", choices=("contain", "cover"), default="contain")
        sub.add_argument("--rotate", choices=(0, 90, 180, 270), type=int, default=0)
        if command == "prepare":
            sub.add_argument("output", type=Path)
        else:
            sub.add_argument("--saturation", type=saturation_value, default=0.5)
            sub.add_argument(
                "--force", action="store_true", help="Refresh even if image is unchanged"
            )
    args = parser.parse_args()
    try:
        if args.command == "sample":
            sample().save(args.output)
        elif args.command == "info":
            with display_lock(STATE):
                display, identity = read_display()
                print(
                    json.dumps(
                        {
                            "resolution": display.resolution,
                            "driver": type(display).__module__,
                            "variant": identity.get_variant(),
                            "pcb_revision": identity.pcb_variant / 10,
                            "eeprom_written_at": identity.eeprom_write_time.decode(
                                "ascii", errors="replace"
                            ),
                        }
                    )
                )
        else:
            image = load_image(args.image, args.fit, args.rotate)
            if args.command == "prepare":
                image.save(args.output)
            else:
                show(image, args.saturation, args.force)
    except (OSError, ValueError, RuntimeError, ImportError, UnidentifiedImageError) as error:
        parser.exit(1, f"inky: {error}\n")


if __name__ == "__main__":
    main()
