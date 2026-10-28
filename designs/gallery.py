"""Build the self-contained comparison page from the rendered screen proofs."""

import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageOps
from render import PAPER, WORK, palette

ROOT = Path(__file__).resolve().parent
NOTES = {
    "harbour-almanac": (
        "Best balance of artwork and information. The two weekly balances read first; "
        "the journal ledger keeps the session and Fable limits close by.",
        "My starting recommendation for the desk. Smaller reset text is the compromise.",
    ),
    "mission-control": (
        "Strongest reading from across the desk. A fixed instrument rail holds weekly "
        "headroom; the next reset gets its own large callout beside the expedition print.",
        "The dark rail needs a real-panel contrast check in your room.",
    ),
    "conservatory": (
        "A quiet specimen sheet: a narrow botanical plate leaves an orderly reading "
        "column for both providers and the scoped weekly limit.",
        "Best if you want the object to feel calm rather than technical.",
    ),
    "departure-board": (
        "A travel print becomes a working timetable. Session, weekly, scoped and Codex "
        "limits have aligned remaining percentages and exact reset destinations.",
        "Best for comparing all the windows. Less dramatic headline numerals.",
    ),
    "balance": (
        "The most graphic object: enormous balances counterweight a kinetic sculpture. "
        "A dedicated lower-right callout carries the next reset.",
        "Best distance readability on a light ground. The artwork is deliberately spare.",
    ),
    "studio-companion": (
        "A cat print and a small working-day ledger. Both weekly balances stay large "
        "while the remaining session, scoped limit and reset credits stay explicit.",
        "Warmest desk companion; the next-reset line is more modest than Mission Control.",
    ),
}
ART_NAMES = [
    "Harbour light",
    "Moon passage",
    "Distant orbit",
    "The observatory",
    "Bird & heliconia",
    "Lotus pond",
    "Alpine express",
    "Above the valley",
    "The mobile",
    "Sunlit arches",
    "Studio morning",
    "Afternoon nap",
]


def image_url(path):
    return "data:image/png;base64," + base64.b64encode((ROOT / path).read_bytes()).decode()


def art_thumbnail(number):
    with Image.open(ROOT / "artwork" / f"{number:02d}-original.png") as source:
        thumb = ImageOps.fit(source.convert("RGB"), (240, 180), Image.Resampling.LANCZOS)
    proof = Image.new("P", (1, 1))
    proof.putpalette(palette(WORK))
    thumb = thumb.quantize(palette=proof, dither=Image.Dither.NONE)
    thumb.putpalette(palette(PAPER))
    out = io.BytesIO()
    thumb.save(out, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode()


def main():
    manifest = json.loads((ROOT / "mockups/manifest.json").read_text())
    preview_replacements = {}
    for item in manifest:
        item["note"], item["tradeoff"] = NOTES[item["id"]]
        for edition in item["editions"]:
            for proof in ("paper", "inks"):
                original = edition[proof]
                edition[proof] = image_url(original)
                preview_replacements[edition[proof]] = str(ROOT / original)
    thumbnails = "".join(
        f'<figure><img src="{art_thumbnail(n)}" width="240" height="180" '
        f'alt="{ART_NAMES[n - 1]}" loading="lazy">'
        f"<figcaption>{ART_NAMES[n - 1]}</figcaption></figure>"
        for n in range(1, 13)
    )
    font_data = base64.b64encode((ROOT / "fonts/Barlow-Medium.ttf").read_bytes()).decode()
    html = TEMPLATE.replace("__DATA__", json.dumps(manifest))
    html = html.replace("__INITIAL_SCREEN__", manifest[0]["editions"][0]["paper"])
    html = html.replace("__THUMBNAILS__", thumbnails).replace("__FONT__", font_data)
    (ROOT / "usage-gallery.html").write_text(html)
    for encoded, original in preview_replacements.items():
        html = html.replace(encoded, original)
    (ROOT / "usage-gallery-preview.html").write_text(html)
    print("Saved self-contained designs/usage-gallery.html")


TEMPLATE = (ROOT / "gallery-template.html").read_text()


if __name__ == "__main__":
    main()
