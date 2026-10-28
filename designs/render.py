"""Render the design study; no network access, credentials, or display writes."""

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, PngImagePlugin

ROOT = Path(__file__).resolve().parent
SCALE = 2
INKS = ["#000000", "#ffffff", "#00ff00", "#0000ff", "#ff0000", "#ffff00", "#ff8c00"]
WORK = ["#000000", "#ffffff", "#16603d", "#174992", "#df3322", "#f2cb19", "#eb821b"]
PAPER = ["#393039", "#ffffff", "#3a5b46", "#3d3b5e", "#9c484b", "#d0be47", "#b16a49"]
FONTS = {
    "sans": "Barlow-Medium.ttf",
    "bold": "Barlow-SemiBold.ttf",
    "condensed": "BarlowCondensed-SemiBold.ttf",
    "serif": "DMSerifDisplay-Regular.ttf",
    "mono": "SpaceMono-Regular.ttf",
}
NAMES = [
    ("harbour-almanac", "Harbour Almanac", "A journal spread for the long view.", (1, 2)),
    ("mission-control", "Mission Control", "An instrument rail for the next expedition.", (3, 4)),
    ("conservatory", "The Conservatory", "A botanical plate with room to breathe.", (5, 6)),
    ("departure-board", "Departure Board", "Every allowance has a departure time.", (7, 8)),
    ("balance", "The Balance", "An abstract print built around two clear balances.", (9, 10)),
    ("studio-companion", "Studio Companion", "A small companion for the working day.", (11, 12)),
]


def palette(colors):
    channels = [int(c[i : i + 2], 16) for c in colors for i in (1, 3, 5)]
    return channels + channels[:3] * (256 - len(colors))


@lru_cache
def font(size, family="sans"):
    return ImageFont.truetype(str(ROOT / "fonts" / FONTS[family]), size * SCALE)


class Sheet:
    def __init__(self):
        self.image = Image.new("RGB", (600 * SCALE, 448 * SCALE), WORK[1])
        self.draw = ImageDraw.Draw(self.image)

    def box(self, bounds, ink=0, outline=None, width=1):
        self.draw.rectangle(
            tuple(round(v * SCALE) for v in bounds),
            fill=WORK[ink] if ink is not None else None,
            outline=WORK[outline] if outline is not None else None,
            width=width * SCALE,
        )

    def line(self, points, ink=0, width=1):
        self.draw.line(tuple(v * SCALE for v in points), fill=WORK[ink], width=width * SCALE)

    def text(self, x, y, value, size=18, family="sans", ink=0, max_width=None):
        face = font(size, family)
        bounds = self.draw.textbbox((0, 0), value, font=face, anchor="lt")
        if max_width is not None and bounds[2] / SCALE > max_width:
            raise ValueError(f"Text too wide ({bounds[2] / SCALE:.1f}>{max_width}): {value}")
        if x + bounds[2] / SCALE > 600 or y + bounds[3] / SCALE > 448:
            raise ValueError(f"Text outside canvas: {value}")
        self.draw.text((x * SCALE, y * SCALE), value, font=face, fill=WORK[ink], anchor="lt")

    def art(self, number, bounds, centering=(0.5, 0.5)):
        x, y, width, height = bounds
        with Image.open(ROOT / "artwork" / f"{number:02d}-original.png") as source:
            fitted = ImageOps.fit(
                source.convert("RGB"),
                (width * SCALE, height * SCALE),
                method=Image.Resampling.LANCZOS,
                centering=centering,
            )
        self.image.paste(fitted, (x * SCALE, y * SCALE))

    def meter(self, x, y, width, remaining, ink, height=8):
        self.box((x, y, x + width, y + height), 1, outline=0)
        if remaining > 0:
            self.box((x, y, x + width * remaining / 100, y + height), ink)

    def finish(self):
        proof = Image.new("P", (1, 1))
        proof.putpalette(palette(WORK))
        small = self.image.resize((600, 448), Image.Resampling.LANCZOS)
        pixels = bytearray(small.tobytes())
        for offset in range(0, len(pixels), 3):
            channels = pixels[offset : offset + 3]
            if max(channels) - min(channels) <= 28:
                value = 255 if sum(channels) >= 384 else 0
                pixels[offset : offset + 3] = bytes((value, value, value))
        small = Image.frombytes("RGB", small.size, bytes(pixels))
        result = small.quantize(palette=proof, dither=Image.Dither.NONE)
        # Duplicate black entries in Pillow's 256-entry palette are normalized to slot 0.
        result = result.point(lambda value: value if value < 7 else 0)
        result.putpalette(palette(INKS))
        return result


def snapshot():
    data = json.loads((ROOT / "data" / "snapshot.json").read_text())
    claude = data["providers"]["claude"]["windows"]
    codex = data["providers"]["codex"]["windows"]
    session = next(w for w in claude if w["label"] == "5-Hour Window")
    weekly = next(w for w in claude if "All models" in w["label"])
    scoped = next(w for w in claude if "Fable" in w["label"])
    week_codex = next(w for w in codex if w["label"] == "7-Day")
    credits = data["providers"]["codex"]["reset_credits"]
    return {
        "claude": f"{weekly['remaining_percent']:.0f}%",
        "codex": f"{week_codex['remaining_percent']:.0f}%",
        "session": f"{session['remaining_percent']:.0f}%",
        "fable": f"{scoped['remaining_percent']:.0f}%",
        "c_pct": weekly["remaining_percent"],
        "x_pct": week_codex["remaining_percent"],
        "session_reset": datetime.fromisoformat(session["resets_local"]).strftime("%H:%M"),
        "claude_reset": datetime.fromisoformat(weekly["resets_local"]).strftime("%a %H:%M"),
        "codex_reset": datetime.fromisoformat(week_codex["resets_local"])
        .strftime("%d %b %H:%M")
        .lstrip("0"),
        "stamp": datetime.fromisoformat(data["as_of"]).strftime("%H:%M"),
        "date": datetime.fromisoformat(data["as_of"]).strftime("%a %d %b").upper(),
        "full_date": datetime.fromisoformat(data["as_of"]).strftime("%d %b %Y").upper(),
        "credits": str(credits["available_count"]),
        "applicable": str(credits["applicable_available_count"]),
    }


def footer(s, d, y=426):
    s.line((20, y - 9, 580, y - 9))
    s.text(20, y, f"AS OF {d['stamp']} SGT   /   {d['full_date']}", 13, "mono")
    # An honest ink registration mark; also checks that all seven inks reach the screen.
    for index in range(7):
        s.box((505 + index * 11, y + 1, 512 + index * 11, y + 8), index)


def harbour(s, d, art):
    s.text(20, 18, "The allowance almanac", 30, "serif")
    s.text(439, 27, d["date"], 14, "condensed")
    s.line((20, 57, 580, 57), width=2)
    s.art(art, (20, 73, 300, 224))
    s.text(342, 76, "CLAUDE", 22, "bold")
    s.text(342, 106, d["claude"], 68, "serif")
    s.text(343, 182, "weekly left", 17)
    s.text(343, 204, f"Reset {d['claude_reset']}", 15)
    s.text(342, 239, "CODEX", 22, "bold")
    s.text(342, 267, d["codex"], 68, "serif")
    s.text(343, 343, "weekly left", 17)
    s.text(343, 365, f"Reset {d['codex_reset']}", 15)
    s.text(20, 312, f"Claude 5h  {d['session']} left", 19, "bold")
    s.text(20, 339, f"Next reset today {d['session_reset']}", 17)
    s.text(20, 369, f"Fable {d['fable']} left · {d['claude_reset']}", 17)
    s.text(20, 394, f"Codex: {d['credits']} resets banked · {d['applicable']} applicable", 16)
    footer(s, d, 429)


def mission(s, d, art):
    s.box((0, 0, 238, 448), 0)
    s.text(18, 18, "MISSION CONTROL", 28, "condensed", ink=1)
    s.text(18, 57, "WEEKLY ALLOWANCE LEFT", 15, "condensed", ink=5)
    s.line((18, 82, 219, 82), ink=1)
    s.text(18, 99, "CLAUDE", 23, "bold", ink=1)
    s.text(16, 132, d["claude"], 87, "condensed", ink=1)
    s.box((18, 225, 58, 233), 6)
    s.text(18, 247, f"Reset {d['claude_reset']}", 17, ink=1)
    s.text(18, 285, "CODEX", 23, "bold", ink=1)
    s.text(16, 317, d["codex"], 87, "condensed", ink=1)
    s.text(18, 418, f"Reset {d['codex_reset']}", 15, ink=1)
    s.art(art, (254, 16, 330, 233))
    s.text(260, 266, "NEXT RESET", 17, "bold")
    s.text(258, 291, d["session_reset"], 49, "condensed")
    s.text(260, 349, f"Claude 5h · {d['session']} left", 18)
    s.text(260, 376, f"Fable {d['fable']} left · {d['claude_reset']}", 16)
    s.text(260, 400, f"{d['credits']} Codex resets banked / {d['applicable']} applicable", 16)
    s.text(260, 427, f"AS OF {d['stamp']} SGT · CODEX ALLOWED", 13, "condensed")


def conservatory(s, d, art):
    s.text(20, 18, "Room to grow.", 35, "serif")
    s.text(415, 35, "THE CONSERVATORY", 16, "condensed")
    s.line((20, 66, 580, 66))
    s.art(art, (20, 83, 200, 294))
    s.text(244, 84, "Claude", 25, "serif")
    s.text(240, 121, d["claude"], 77, "condensed")
    s.text(397, 133, "weekly left", 20)
    s.text(397, 165, d["claude_reset"], 17)
    s.text(244, 213, f"5h {d['session']} left · next {d['session_reset']}", 18)
    s.text(244, 243, f"Fable {d['fable']} left · {d['claude_reset']}", 17)
    s.line((244, 275, 580, 275))
    s.text(244, 287, "Codex", 25, "serif")
    s.text(240, 325, d["codex"], 70, "condensed")
    s.text(397, 335, "weekly left", 20)
    s.text(397, 368, d["codex_reset"], 16)
    s.text(
        20,
        395,
        f"Codex {d['credits']} resets banked · {d['applicable']} applicable · 5h not reported",
        16,
    )
    footer(s, d, 429)


def departures(s, d, art):
    s.art(art, (0, 0, 600, 180), centering=(0.5, 0.3) if art == 8 else (0.5, 0.5))
    s.box((18, 17, 312, 62), 1)
    s.text(30, 27, "NEXT DEPARTURES", 30, "condensed")
    s.box((0, 180, 600, 213), 0)
    s.text(20, 189, "PROVIDER / WINDOW", 16, "condensed", ink=1)
    s.text(316, 189, "LEFT", 16, "condensed", ink=1)
    s.text(419, 189, "RESET / SGT", 16, "condensed", ink=1)
    rows = [
        ("Claude", "5 hour", d["session"], f"Today {d['session_reset']}", 2),
        ("Claude", "Weekly", d["claude"], d["claude_reset"], 6),
        ("Fable", "Weekly scope", d["fable"], d["claude_reset"], 3),
        ("Codex", "Weekly", d["codex"], d["codex_reset"], 2),
    ]
    for index, (provider, window, left, reset, ink) in enumerate(rows):
        y = 222 + index * 39
        s.box((20, y + 5, 26, y + 11), ink)
        s.text(36, y, provider, 22, "condensed")
        s.text(145, y + 3, window, 17)
        s.text(316, y - 1, left, 25, "condensed")
        s.text(419, y + 3, reset, 17)
        s.line((20, y + 30, 580, y + 30))
    s.text(
        20,
        386,
        f"Codex: {d['credits']} resets banked / {d['applicable']} applicable; 5h not reported",
        17,
    )
    footer(s, d, 429)


def balance(s, d, art):
    s.art(art, (225, 15, 355, 275))
    s.text(20, 22, "CLAUDE", 21, "bold")
    s.text(16, 51, d["claude"], 95, "condensed")
    s.text(20, 153, f"weekly left · {d['claude_reset']}", 16)
    s.text(20, 202, "CODEX", 21, "bold")
    s.text(16, 230, d["codex"], 95, "condensed")
    s.text(20, 333, f"weekly left · {d['codex_reset']}", 16)
    s.line((250, 307, 580, 307))
    s.text(250, 324, f"NEXT RESET  {d['session_reset']}", 22, "condensed")
    s.text(250, 355, f"Claude 5h · {d['session']} left", 17)
    s.text(20, 382, f"Fable {d['fable']} left · {d['claude_reset']}", 17)
    s.text(311, 382, f"Codex: {d['credits']} banked / {d['applicable']} applicable", 16)
    footer(s, d, 429)


def studio(s, d, art):
    s.text(20, 19, "A good day to build.", 31, "serif")
    s.text(462, 32, d["date"], 15, "condensed")
    s.line((20, 62, 580, 62))
    s.art(art, (20, 82, 277, 235))
    s.text(322, 81, "CLAUDE", 22, "bold")
    s.text(318, 112, d["claude"], 66, "serif")
    s.text(322, 187, f"weekly left · {d['claude_reset']}", 17)
    s.line((322, 221, 580, 221))
    s.text(322, 240, "CODEX", 22, "bold")
    s.text(318, 270, d["codex"], 66, "serif")
    s.text(322, 345, f"weekly left · {d['codex_reset']}", 16)
    s.text(20, 333, f"5h {d['session']} left / next {d['session_reset']}", 18, "bold")
    s.text(20, 362, f"Fable {d['fable']} left · {d['claude_reset']}", 17)
    s.text(
        20,
        393,
        f"Codex: {d['credits']} resets banked; {d['applicable']} applicable. More weekly room.",
        16,
    )
    footer(s, d, 429)


RENDERERS = [harbour, mission, conservatory, departures, balance, studio]


def main():
    data = snapshot()
    prompts = {item["id"]: item for item in json.loads((ROOT / "prompts/artwork.json").read_text())}
    manifest = []
    for (slug, name, description, artworks), render in zip(NAMES, RENDERERS, strict=True):
        editions = []
        for edition, art in enumerate(artworks, start=1):
            sheet = Sheet()
            render(sheet, data, art)
            image = sheet.finish()
            assert image.size == (600, 448)
            used = set(image.tobytes())
            assert used == set(range(7)), (slug, used)
            meta = PngImagePlugin.PngInfo()
            meta.add_text(
                "Description", f"{name}, edition {edition}; frozen data; deterministic UI"
            )
            meta.add_text(
                "Source", f"ImageGen artwork {art}; data/snapshot.json; designs/render.py"
            )
            meta.add_text("Prompt", prompts[art]["prompt"])
            meta.add_text("impeccable:prompt", prompts[art]["prompt"])
            ink_path = ROOT / "mockups" / f"{slug}-{edition}-inks.png"
            image.save(ink_path, pnginfo=meta, optimize=True)
            paper_path = ROOT / "mockups" / f"{slug}-{edition}-paper.png"
            image.putpalette(palette(PAPER))
            image.save(paper_path, pnginfo=meta, optimize=True)
            editions.append(
                {
                    "artwork": art,
                    "inks": str(ink_path.relative_to(ROOT)),
                    "paper": str(paper_path.relative_to(ROOT)),
                }
            )
        manifest.append(
            {"id": slug, "name": name, "description": description, "editions": editions}
        )
    (ROOT / "mockups/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Rendered {len(manifest)} layouts × 2 artwork editions × 2 palette proofs.")


if __name__ == "__main__":
    main()
