"""Export exact-size concept/proof PNGs and a self-contained comparison page."""

import base64
import json
from pathlib import Path

from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parent
WORK = ["000000", "ffffff", "16603d", "174992", "df3322", "f2cb19", "eb821b"]
INKS = ["000000", "ffffff", "00ff00", "0000ff", "ff0000", "ffff00", "ff8c00"]
TITLES = {
    "01-pop-comic": ("Pop Comic", "The balances are the dialogue. Reset details become narration."),
    "02-budget-kraken": (
        "Budget Kraken",
        "Tentacles shape the numbers; the engraving carries the rest.",
    ),
    "03-reactor-room": (
        "Reactor Room",
        "Allowance is painted onto the power cores and gauge faces.",
    ),
    "04-night-market": (
        "Night Market",
        "The city is the interface: signs, awnings, lanterns, shutters.",
    ),
    "05-quota-moth": (
        "Quota Moth",
        "The balances are wing markings, framed by a living engraving.",
    ),
    "06-cosmic-pinball": (
        "Cosmic Pinball",
        "The statistics become part of the playfield's machinery.",
    ),
}


def palette(colors):
    channels = [int(color[i : i + 2], 16) for color in colors for i in (0, 2, 4)]
    return channels + [0, 0, 0] * (256 - len(colors))


def data_url(path, kind="image/png"):
    return f"data:{kind};base64," + base64.b64encode(path.read_bytes()).decode()


def main():
    manifest = json.loads((ROOT / "prompts.json").read_text())
    proof = Image.new("P", (1, 1))
    proof.putpalette(palette(WORK))
    for item in manifest:
        stem = item["id"]
        with Image.open(ROOT / f"{stem}-master.png") as source:
            image = source.convert("RGB").resize((600, 448), Image.Resampling.LANCZOS)
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("impeccable:prompt", item["prompt"])
        metadata.add_text(
            "Description", "Integrated concept; frozen illustrative numbers; not live"
        )
        image.save(ROOT / f"{stem}-concept.png", pnginfo=metadata, optimize=True)
        pixels = bytearray(image.tobytes())
        for offset in range(0, len(pixels), 3):
            channels = pixels[offset : offset + 3]
            if max(channels) - min(channels) <= 28:
                value = 255 if sum(channels) >= 384 else 0
                pixels[offset : offset + 3] = bytes((value, value, value))
        neutral = Image.frombytes("RGB", image.size, bytes(pixels))
        indexed = neutral.quantize(palette=proof, dither=Image.Dither.NONE)
        indexed = indexed.point(lambda value: value if value < 7 else 0)
        indexed.putpalette(palette(INKS))
        assert set(indexed.tobytes()) == set(range(7)), stem
        indexed.save(ROOT / f"{stem}-inks.png", pnginfo=metadata, optimize=True)
    views = [
        {
            "id": item["id"],
            "title": TITLES[item["id"]][0],
            "description": TITLES[item["id"]][1],
            "concept": str(ROOT / f"{item['id']}-concept.png"),
            "inks": str(ROOT / f"{item['id']}-inks.png"),
        }
        for item in manifest
    ]
    template = (ROOT / "template.html").read_text()
    font = data_url(ROOT.parent / "fonts/Barlow-Medium.ttf", "font/ttf")
    html = template.replace("__FONT__", font)
    html = html.replace("__INITIAL__", views[1]["concept"])
    html = html.replace("__VIEWS__", json.dumps(views))
    (ROOT / "preview.html").write_text(html)
    for item in views:
        for kind in ("concept", "inks"):
            path = Path(item[kind])
            html = html.replace(str(path), data_url(path))
    (ROOT / "index.html").write_text(html)
    print("Exported 12 exact-size concept/proof images and comparison HTML.")


if __name__ == "__main__":
    main()
