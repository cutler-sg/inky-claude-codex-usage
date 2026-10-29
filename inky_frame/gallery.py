"""Refresh-driven artwork rotation with persistent button selection and locking."""

import argparse
import hashlib
import json
import math
import random
import signal
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

from . import __main__ as display_cli
from .live import ARTWORKS, build_view, render
from .profiles import LEGACY, PROFILES, DisplayProfile
from .usage import atomic_json, load_snapshot, validate_snapshot

ROOT = display_cli.ROOT
STATE = ROOT / "state"
GALLERY_STATE = STATE / "gallery"
HOME = "02-budget-kraken"


def log(event: str, **values):
    print(json.dumps({"event": event, **values}), flush=True)


def selection_state() -> dict:
    path = GALLERY_STATE / "selection.json"
    data = json.loads(path.read_text()) if path.exists() else {"artwork": HOME}
    if not isinstance(data, dict):
        raise ValueError("Artwork selection must be an object")
    chosen, mode, key = data.get("artwork"), data.get("mode", "rotate"), data.get("refresh_key")
    if not isinstance(chosen, str) or chosen not in ARTWORKS:
        raise ValueError(f"Unknown artwork selection: {chosen}")
    if mode not in ("rotate", "locked"):
        raise ValueError(f"Unknown artwork mode: {mode}")
    if key is not None and (
        not isinstance(key, str) or len(key) != 64 or any(c not in "0123456789abcdef" for c in key)
    ):
        raise ValueError("Invalid artwork refresh key")
    return {"artwork": chosen, "mode": mode, "refresh_key": key}


def selection() -> str:
    return selection_state()["artwork"]


def choose(action: str) -> str:
    with display_cli.display_lock(GALLERY_STATE / "selection-lock"):
        current = selection()
        ids = list(ARTWORKS)
        if action == "home":
            chosen = HOME
        elif action == "random":
            chosen = random.choice([art for art in ids if art != current])
        elif action in ("previous", "next"):
            chosen = ids[(ids.index(current) + (1 if action == "next" else -1)) % len(ids)]
        elif action in ARTWORKS:
            chosen = action
        else:
            raise ValueError(f"Unknown gallery action: {action}")
        mode = "rotate" if action == "random" else "locked"
        # Forget the prior update so resuming rotation displays this choice first.
        atomic_json(GALLERY_STATE / "selection.json", {"artwork": chosen, "mode": mode})
    log("artwork_selected", artwork=chosen, action=action, mode=mode)
    return chosen


def commit_selection(expected: dict, artwork: str, update_key: str) -> bool:
    with display_cli.display_lock(GALLERY_STATE / "selection-lock"):
        # A concurrent CLI/button selection takes precedence over this tick.
        if selection_state() != expected:
            return False
        atomic_json(
            GALLERY_STATE / "selection.json",
            {"artwork": artwork, "mode": expected["mode"], "refresh_key": update_key},
        )
    return True


def show_frame(path: Path, profile: DisplayProfile | None = None):
    with Image.open(path) as source:
        source.load()
        image = source.copy()
    if profile is None:
        profile, _ = display_cli.read_identity()
    profile.validate_frame(image)
    display_cli.show(image, 0.5, False, expected_profile=profile)


class Player:
    def __init__(self, profile: DisplayProfile = LEGACY):
        self.profile = profile
        self.process = None
        self.wanted = None
        self.wanted_at = 0.0
        self.completed = None
        self.running = None
        self.running_artwork = None
        self.next_refresh = 0.0
        self.displayed = None
        self.error = None
        self.control = None

    def status(self):
        selected = selection_state()
        atomic_json(
            GALLERY_STATE / "status.json",
            {
                "selected": selected["artwork"],
                "mode": selected["mode"],
                "displayed": self.displayed,
                "refreshing": self.running_artwork if self.process else None,
                "error": self.error,
                "updated_at": time.time(),
                "profile": self.profile.name,
            },
        )

    def tick(self, snapshot: dict, now: float, monotonic: float):
        view = build_view(snapshot, now)
        update_key = hashlib.sha256(
            json.dumps([snapshot["collected_at"], view], sort_keys=True).encode()
        ).hexdigest()
        selected = selection_state()
        control = (selected["artwork"], selected["mode"])
        chosen = selected["artwork"]
        if selected["mode"] == "rotate" and selected["refresh_key"] not in (None, update_key):
            ids = list(ARTWORKS)
            chosen = ids[(ids.index(chosen) + 1) % len(ids)]
        wanted = json.dumps([self.profile.name, chosen, view], sort_keys=True)
        if wanted != self.wanted:
            self.wanted = wanted
            self.wanted_at = monotonic
            self.status()
        elif control != self.control:
            self.status()
        self.control = control
        if self.process is not None:
            result = self.process.poll()
            if result is None:
                return
            if result == 0:
                self.completed = self.running
                self.displayed = self.running_artwork
                self.error = None
            else:
                self.error = f"Display worker exited {result}; retry in 60 seconds"
                self.next_refresh = monotonic + 60
            log("gallery_refresh_finished", artwork=self.running_artwork, exit_code=result)
            self.process = None
            self.status()
        if wanted == self.completed:
            if selected["refresh_key"] != update_key and commit_selection(
                selected, chosen, update_key
            ):
                self.status()
            return
        if monotonic < self.next_refresh or monotonic - self.wanted_at < 0.8:
            return
        if not commit_selection(selected, chosen, update_key):
            return
        frame = GALLERY_STATE / "frame.png"
        render(chosen, view, self.profile).save(frame)
        self.running = wanted
        self.running_artwork = chosen
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "inky_frame.gallery",
                "show",
                str(frame),
                "--profile",
                self.profile.name,
            ],
            cwd=ROOT,
        )
        self.next_refresh = monotonic + 40
        log("gallery_refresh_started", artwork=chosen, mode=selected["mode"])
        self.status()


def run():
    import gpiod
    import gpiodevice
    from gpiod.line import Bias, Direction, Edge

    stopping = False

    def stop(signum, frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    profile, _ = display_cli.read_identity()
    player = Player(profile)
    with display_cli.display_lock(GALLERY_STATE / "service-lock"):
        chip = gpiodevice.find_chip_by_platform()
        offsets = {chip.line_offset_from_id(pin): action for pin, action in profile.buttons.items()}
        settings = gpiod.LineSettings(
            direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.FALLING
        )
        with chip.request_lines(
            consumer="inky-gallery-buttons", config=dict.fromkeys(offsets, settings)
        ) as buttons:
            selected = selection_state()
            log(
                "gallery_ready",
                buttons=profile.buttons,
                artwork=selected["artwork"],
                mode=selected["mode"],
                profile=profile.name,
            )
            last_press = {}
            last_error = None
            try:
                while not stopping:
                    if buttons.wait_edge_events(0.2):
                        for event in buttons.read_edge_events():
                            prior = last_press.get(event.line_offset, 0)
                            if event.timestamp_ns - prior < 200_000_000:
                                continue
                            last_press[event.line_offset] = event.timestamp_ns
                            label, action = offsets[event.line_offset]
                            log("button_pressed", button=label)
                            choose(action)
                    try:
                        data = load_snapshot(STATE / "usage.json")
                        player.tick(data, time.time(), time.monotonic())
                        last_error = None
                    except (OSError, ValueError, KeyError, display_cli.DisplayError) as error:
                        message = str(error)
                        if message != last_error:
                            log("gallery_error", error=message)
                            last_error = message
            finally:
                if player.process is not None:
                    log("waiting_for_refresh_before_exit")
                    player.process.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("run")
    commands.add_parser("receive", help="Read a sanitized usage snapshot from stdin")
    commands.add_parser("status")
    commands.add_parser("list")
    select = commands.add_parser("select")
    select.add_argument("action", choices=["previous", "next", "random", "home", *ARTWORKS])
    show = commands.add_parser("show")
    show.add_argument("image", type=Path)
    show.add_argument("--profile", choices=PROFILES)
    preview = commands.add_parser("render", help="Render a usage fixture without hardware")
    preview.add_argument("artwork", choices=ARTWORKS)
    preview.add_argument("snapshot", type=Path)
    preview.add_argument("output", type=Path)
    preview.add_argument("--profile", choices=PROFILES, default=LEGACY.name)
    preview.add_argument("--now", type=float, required=True, help="Fixed Unix timestamp")
    args = parser.parse_args()
    try:
        if args.command == "run":
            run()
        elif args.command == "receive":
            payload = sys.stdin.read(65537)
            if len(payload) > 65536:
                raise ValueError("Usage snapshot exceeds 64 KiB")
            data = validate_snapshot(json.loads(payload))
            with display_cli.display_lock(STATE / "receive-lock"):
                atomic_json(STATE / "usage.json", data)
            log("usage_received", collected_at=data["collected_at"])
        elif args.command == "select":
            choose(args.action)
        elif args.command == "show":
            show_frame(args.image, PROFILES[args.profile] if args.profile else None)
        elif args.command == "render":
            if not math.isfinite(args.now):
                raise ValueError("--now must be a finite Unix timestamp")
            render(
                args.artwork,
                build_view(load_snapshot(args.snapshot), args.now),
                PROFILES[args.profile],
            ).save(args.output)
        elif args.command == "list":
            print(json.dumps(ARTWORKS, indent=2))
        else:
            path = GALLERY_STATE / "status.json"
            status = json.loads(path.read_text()) if path.exists() else {}
            selected = selection_state()
            status.update(selected=selected["artwork"], mode=selected["mode"])
            print(json.dumps(status, indent=2))
    except (OSError, ValueError, RuntimeError, ImportError, KeyError) as error:
        parser.exit(1, f"inky gallery: {error}\n")


if __name__ == "__main__":
    main()
