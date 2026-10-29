"""Render a concept study with the installed OpenSCAD CLI."""

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OPENSCAD = shutil.which("openscad") or "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
VIEWS = {
    "front": ("210,-290,190,0,28,52", True, True),
    "rear": ("235,340,215,0,30,48", True, True),
    "stand": ("180,-230,155,0,33,15", False, False),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rounded", action="store_true", help="Render concepts 5–7")
    group.add_argument("--explorations", action="store_true", help="Render concepts 8–13")
    args = parser.parse_args()
    (ROOT / "renders").mkdir(exist_ok=True)
    concepts = range(8, 14) if args.explorations else range(5, 8) if args.rounded else range(1, 5)
    for concept in concepts:
        for view, (camera, display, cable) in VIEWS.items():
            subprocess.run(
                [
                    OPENSCAD,
                    "-o",
                    str(ROOT / "renders" / f"{concept:02}-{view}.png"),
                    "--imgsize=1200,1000",
                    f"--camera={camera}",
                    "--projection=o",
                    "--colorscheme=Tomorrow",
                    "--hardwarnings",
                    "-D",
                    f"concept={concept}",
                    "-D",
                    f"show_display={str(display).lower()}",
                    "-D",
                    f"show_cable={str(cable).lower()}",
                    str(ROOT / "stand-concepts.scad"),
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
