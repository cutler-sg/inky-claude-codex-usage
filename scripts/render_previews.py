"""Render synthetic usage at every supported size, without network or hardware.

Run from the repository root: uv run python -m scripts.render_previews
"""

import argparse
import base64
import html
import io
import json
import resource
import sys
import time
from pathlib import Path

from PIL import Image, __version__

from inky_frame.live import ARTWORKS, build_view, render
from inky_frame.profiles import PROFILES
from inky_frame.usage import validate_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures", type=Path, default=Path("tests/fixtures/render-snapshots.json")
    )
    parser.add_argument("--output", type=Path, default=Path("state/multi-display/previews"))
    parser.add_argument("--all-states", action="store_true")
    args = parser.parse_args()
    bundle = json.loads(args.fixtures.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    records, cards = [], []
    for scenario, snapshot in bundle["scenarios"].items():
        if scenario != "normal" and not args.all_states:
            continue
        view = build_view(validate_snapshot(snapshot), bundle["now"])
        for artwork, title in ARTWORKS.items():
            for profile in PROFILES.values():
                started = time.monotonic()
                image = render(artwork, view, profile)
                profile.validate_frame(image)
                filename = f"{scenario}-{artwork}-{profile.name}.png"
                image.save(args.output / filename)
                records.append({"file": filename, "seconds": round(time.monotonic() - started, 3)})
                if scenario == "normal":
                    thumb = image.convert("RGB")
                    thumb.thumbnail((300, 224), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    thumb.save(buffer, format="PNG")
                    encoded = base64.b64encode(buffer.getvalue()).decode()
                    cards.append(
                        f'<figure><a href="{filename}">'
                        f'<img src="data:image/png;base64,{encoded}" '
                        f'alt="{html.escape(title)} on {profile.name}"></a>'
                        f"<figcaption>{html.escape(title)} · {profile.name}<br>"
                        f"{profile.resolution[0]} × {profile.resolution[1]} · "
                        f"{len(profile.inks)} inks</figcaption></figure>"
                    )
    report = {
        "pillow": __version__,
        "now": bundle["now"],
        "renders": records,
        "peak_rss_mib": round(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            / (1024**2 if sys.platform == "darwin" else 1024),
            1,
        ),
    }
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    document = (
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>Inky display previews</title><style>"
        "body{margin:24px;background:#eee9df;color:#201e1a;font:15px system-ui}"
        "h1{font-size:26px}main{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));"
        "gap:16px}figure{margin:0;background:white;padding:10px;border:1px solid #c7c1b5}"
        "img{display:block;width:100%;height:auto}figcaption{margin-top:8px;font-size:12px}"
        "p{max-width:80ch}@media(max-width:750px){main{"
        "grid-template-columns:repeat(2,minmax(0,1fr))}}</style>"
        "<h1>Six artworks · four displays</h1><p>Synthetic readings. "
        "Seven-colour 5.7-inch and six-colour Spectra 6 previews. "
        "Colours illustrate the indexed file, not calibrated physical panels. "
        "Open a PNG to inspect native pixels.</p><main>" + "".join(cards) + "</main></html>"
    )
    (args.output / "index.html").write_text(document)
    print(
        json.dumps(
            {
                "images": len(records),
                "peak_rss_mib": report["peak_rss_mib"],
                "gallery": str(args.output / "index.html"),
            }
        )
    )


if __name__ == "__main__":
    main()
