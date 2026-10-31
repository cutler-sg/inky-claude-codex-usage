"""Render real usage into the approved artwork's own information-bearing surfaces."""

import math
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont, ImageOps

from .profiles import LEGACY, DisplayProfile
from .usage import provider_state

ROOT = Path(__file__).resolve().parent.parent
SGT = ZoneInfo("Asia/Singapore")
SCALE = 2
INKS = list(LEGACY.inks)
WORK = list(LEGACY.working_inks)
ARTWORKS = {
    "01-pop-comic": "Pop Comic",
    "02-budget-kraken": "Budget Kraken",
    "03-reactor-room": "Reactor Room",
    "04-night-market": "Night Market",
    "05-quota-moth": "Quota Moth",
    "06-cosmic-pinball": "Cosmic Pinball",
}


def abbreviated(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def reset_label(epoch, now):
    if epoch is None:
        return "NOT REPORTED"
    if epoch <= now:
        return "UPDATE PENDING"
    if epoch - now >= 6 * 86400:
        return datetime.fromtimestamp(epoch, SGT).strftime("%d %b %H:%M").lstrip("0").upper()
    return datetime.fromtimestamp(epoch, SGT).strftime("%a %H:%M").upper()


def build_view(snapshot: dict, now: float) -> dict:
    view = {}
    for name in ("claude", "codex"):
        provider = snapshot["providers"][name]
        state = provider_state(provider, now)
        windows = provider["windows"] if state != "UNAVAILABLE" else []
        weekly = next((w for w in windows if w["label"] in ("7-Day", "7-Day · All models")), None)
        headline = weekly or (max(windows, key=lambda w: w["used_percent"]) if windows else None)

        def remaining(window):
            return f"{100 - window['used_percent']:.0f}%" if window else "--"

        view[name] = {
            "name": name.upper() + (f" / {state}" if state != "LIVE" else ""),
            "remaining": remaining(headline),
            "window": "WEEK LEFT"
            if weekly
            else (
                "5H LEFT"
                if headline and headline["label"] == "5-Hour Window"
                else (
                    abbreviated(headline["label"].upper(), 18) + " LEFT" if headline else "NO DATA"
                )
            ),
            "has_weekly": weekly is not None,
            "reset_window": (
                "WEEK"
                if weekly
                else (
                    "5H"
                    if headline and headline["label"] == "5-Hour Window"
                    else (
                        abbreviated(headline["label"].split(" · ")[-1].upper(), 10)
                        if headline
                        else "RESET"
                    )
                )
            ),
            "reset": reset_label(headline["reset_epoch"], now) if headline else "NOT REPORTED",
            "weekly_reset": reset_label(weekly["reset_epoch"], now) if weekly else "NOT REPORTED",
        }
        observed = provider["observed_at"]
        view[name]["stamp"] = (
            datetime.fromtimestamp(observed, SGT).strftime("%d %b %H:%M").upper()
            if observed is not None
            else "NO DATA"
        )
        session = next((w for w in windows if w["label"] == "5-Hour Window"), None)
        view[name]["session"] = remaining(session)
        view[name]["has_session"] = session is not None
        view[name]["session_reset"] = (
            reset_label(session["reset_epoch"], now) if session else "NOT REPORTED"
        )
        scopes = [w for w in windows if w["label"].startswith("7-Day · ") and w != weekly]
        scope = max(scopes, key=lambda w: w["used_percent"]) if scopes else None
        view[name]["scope_name"] = scope["label"].split(" · ", 1)[1].upper() if scope else "SCOPE"
        view[name]["scope_remaining"] = remaining(scope)
        view[name]["scope_more"] = len(scopes) - 1 if scopes else 0
        more = f" +{len(scopes) - 1}" if len(scopes) > 1 else ""
        view[name]["scope"] = (
            f"{abbreviated(view[name]['scope_name'], 12)} {remaining(scope)}{more}"
            if scope
            else "SCOPE NOT REPORTED"
        )
        view[name]["scope_reset"] = reset_label(scope["reset_epoch"], now) if scope else ""
        credits = provider["credits"] if state != "UNAVAILABLE" else None
        view[name]["credits"] = (
            f"{credits['available_count']} BANKED / "
            f"{credits['applicable_available_count']} APPLICABLE"
            if credits is not None
            else "NOT REPORTED"
        )
    observed = [
        p["observed_at"]
        for p in snapshot["providers"].values()
        if p["observed_at"] is not None and p["observed_at"] <= now + 60
    ]
    view["as_of"] = (
        "AS OF " + datetime.fromtimestamp(min(observed), SGT).strftime("%d %b %H:%M SGT").upper()
        if observed
        else "NO USAGE OBSERVATIONS"
    )
    view["as_of_date"] = (
        datetime.fromtimestamp(min(observed), SGT).strftime("%d %b").upper()
        if observed
        else "NO DATA"
    )
    view["as_of_time"] = (
        datetime.fromtimestamp(min(observed), SGT).strftime("%H:%M") if observed else "--"
    )
    return view


@lru_cache(maxsize=128)
def face(name: str, size: int):
    return ImageFont.truetype(str(ROOT / "designs/fonts" / name), size)


def perspective(source, target):
    """Solve the inverse homography: target canvas coordinates -> text patch coordinates."""
    rows = []
    for (x, y), (u, v) in zip(target, source, strict=True):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y, u])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y, v])
    for column in range(8):
        pivot = max(range(column, 8), key=lambda row: abs(rows[row][column]))
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        if abs(divisor) < 1e-12:
            raise ValueError("Degenerate text surface")
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(8):
            if row != column:
                factor = rows[row][column]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[column], strict=True)]
    return tuple(row[-1] for row in rows)


class Canvas:
    def __init__(self, artwork, profile: DisplayProfile = LEGACY):
        self.profile = profile
        with Image.open(ROOT / "assets/live" / f"{artwork}-plate.png") as plate:
            self.image = plate.convert("RGBA")
        self.scale = (SCALE, SCALE)
        self.offset = (0, 0)
        if profile != LEGACY:
            # Small panels retain the existing supersampling budget; large panels
            # render at native size to bound peak memory on a Zero 2 W.
            supersample = max(
                1.0, min(2.0, 1200 / profile.resolution[0], 896 / profile.resolution[1])
            )
            work_size = tuple(round(value * supersample) for value in profile.resolution)
            content = ImageOps.contain(self.image, work_size, Image.Resampling.LANCZOS)
            self.offset = tuple((a - b) // 2 for a, b in zip(work_size, content.size, strict=True))
            self.scale = (content.width / 600, content.height / 448)
            self.image = Image.new("RGBA", work_size, "white")
            self.image.alpha_composite(content, self.offset)

    def panel(self, quad, lines, family="BarlowCondensed-SemiBold.ttf", *, background=None):
        expanded = []
        for value, weight, color in lines:
            if value.endswith((" / UNAVAILABLE", " / STALE")):
                name, state = value.split(" / ", 1)
                expanded.extend([(name, weight, color), (state, weight * 0.8, color)])
            else:
                expanded.append((value, min(weight, 35) if value == "--" else weight, color))
        lines = expanded
        target = [
            (x * self.scale[0] + self.offset[0], y * self.scale[1] + self.offset[1])
            for x, y in quad
        ]
        width = round(max(math.dist(target[0], target[1]), math.dist(target[2], target[3])))
        height = round(max(math.dist(target[0], target[3]), math.dist(target[1], target[2])))
        patch = Image.new("RGBA", (width, height), background)
        draw = ImageDraw.Draw(patch)
        total = sum(size for _, size, _ in lines)
        y = 0.0
        for value, weight, color in lines:
            row_height = height * weight / total
            size = max(1, round(row_height * 1.3))
            stroke = max(1, round(min(self.scale))) if color not in ("black", "white") else 0
            while True:
                row_family = (
                    "BarlowCondensed-SemiBold.ttf" if value in ("STALE", "UNAVAILABLE") else family
                )
                font = face(row_family, size)
                box = draw.textbbox((0, 0), value, font=font, stroke_width=stroke)
                safe_width = (
                    width * 0.86 if value in ("CLAUDE", "CODEX", "STALE", "UNAVAILABLE") else width
                )
                if (
                    box[2] - box[0] <= safe_width - 4 and box[3] - box[1] <= row_height - 2
                ) or size <= 2:
                    break
                size -= 1
            draw.text(
                (
                    (width - box[2] + box[0]) / 2 - box[0],
                    y + (row_height - box[3] + box[1]) / 2 - box[1],
                ),
                value,
                font=font,
                fill=color,
                stroke_width=stroke,
                stroke_fill="black",
            )
            y += row_height
        coefficients = perspective([(0, 0), (width, 0), (width, height), (0, height)], target)
        self.image.alpha_composite(
            patch.transform(
                self.image.size,
                Image.Transform.PERSPECTIVE,
                coefficients,
                resample=Image.Resampling.BICUBIC,
            )
        )

    def line(self, quad, value, color="black", family="BarlowCondensed-SemiBold.ttf"):
        self.panel(quad, [(value, 1, color)], family)

    def headline(self, quad, provider, color, family="Bangers-Regular.ttf"):
        self.panel(
            quad,
            [
                (provider["name"], 27, "black"),
                (provider["remaining"], 75, color),
                (provider["window"], 20, "black"),
            ],
            family,
        )

    def finish(self):
        small = self.image.convert("RGB").resize(self.profile.resolution, Image.Resampling.LANCZOS)
        pixels = bytearray(small.tobytes())
        for offset in range(0, len(pixels), 3):
            channels = pixels[offset : offset + 3]
            if max(channels) - min(channels) <= 28:
                value = 255 if sum(channels) >= 384 else 0
                pixels[offset : offset + 3] = bytes((value, value, value))
        proof = Image.new("P", (1, 1))
        proof.putpalette(
            [c for color in self.profile.working_inks for c in bytes.fromhex(color)]
            + [0] * (768 - 3 * len(self.profile.inks))
        )
        result = (
            Image.frombytes("RGB", small.size, bytes(pixels))
            .quantize(palette=proof, dither=Image.Dither.NONE)
            .point(lambda index: index if index < len(self.profile.inks) else 0)
        )
        result.putpalette(self.profile.palette + [0] * (768 - len(self.profile.palette)))
        return result


def render(artwork: str, view: dict, profile: DisplayProfile = LEGACY) -> Image.Image:
    c, x = view["claude"], view["codex"]
    session = f"CLAUDE 5H {c['session']} / {c['session_reset']}"
    scope = " / ".join(value for value in (c["scope"], c["scope_reset"]) if value)

    def reset_details(provider, name):
        if provider["has_weekly"]:
            if name == "CODEX" and provider["has_session"]:
                return f"CODEX 5H {provider['session']}", f"7D {provider['weekly_reset']}"
            return f"{name} WEEK", provider["weekly_reset"]
        return f"{name} {provider['reset_window']}", provider["reset"]

    ch, cd = reset_details(c, "CLAUDE")
    xh, xd = reset_details(x, "CODEX")
    cr, xr = f"{ch} / {cd}", f"{xh} / {xd}"
    credits = f"CODEX RESETS: {x['credits']}"
    stamp = view["as_of"]
    s = Canvas(artwork, profile)
    scope_name = abbreviated(c["scope_name"], 7)
    if c["scope_more"]:
        scope_name = abbreviated(c["scope_name"], 5) + f" +{c['scope_more']}"
    scope_rows = [(scope_name, 16, "black"), (c["scope_remaining"], 28, "black")]
    if artwork == "01-pop-comic":
        s.headline([(34, 31), (192, 23), (205, 169), (26, 187)], c, "#df3322")
        s.headline([(459, 39), (578, 32), (585, 178), (448, 190)], x, "#174992")
        if c["has_session"]:
            s.line([(19, 242), (212, 230), (210, 251), (16, 264)], session)
        s.line([(16, 280), (179, 267), (177, 287), (14, 302)], scope)
        s.line([(449, 235), (589, 220), (587, 240), (448, 255)], cr)
        s.line([(450, 266), (591, 250), (589, 269), (448, 285)], xr)
        s.line([(16, 400), (338, 398), (335, 426), (16, 428)], credits)
        s.panel(
            [(516, 369), (576, 369), (578, 422), (516, 422)],
            [
                (f"AS OF {view['as_of_date']}", 12, "black"),
                (view["as_of_time"], 24, "black"),
                ("SGT", 10, "black"),
            ],
        )
    elif artwork == "02-budget-kraken":
        s.headline(
            [(50, 43), (217, 46), (220, 154), (44, 158)], c, "#df3322", "DMSerifDisplay-Regular.ttf"
        )
        s.headline(
            [(395, 166), (548, 164), (557, 294), (401, 309)],
            x,
            "#174992",
            "DMSerifDisplay-Regular.ttf",
        )
        if c["has_session"]:
            s.line([(68, 230), (261, 235), (261, 252), (68, 249)], session)
        s.line([(91, 272), (244, 272), (244, 285), (91, 288)], scope)
        s.line([(111, 311), (265, 317), (265, 335), (111, 329)], cr)
        s.line([(146, 347), (280, 375), (280, 389), (146, 362)], xr)
        s.line([(360, 378), (565, 351), (568, 370), (362, 398)], credits)
        s.line([(463, 407), (578, 407), (578, 422), (463, 422)], stamp)
    elif artwork == "03-reactor-room":
        s.headline([(111, 42), (257, 70), (258, 195), (101, 167)], c, "#df3322")
        s.headline([(343, 81), (506, 48), (520, 187), (341, 211)], x, "#174992")
        if c["has_session"]:
            s.line([(34, 324), (100, 325), (100, 340), (34, 339)], "CLAUDE 5H")
            s.line([(35, 345), (85, 346), (85, 373), (34, 372)], c["session"])
        s.line([(197, 344), (238, 346), (237, 356), (196, 354)], scope_name)
        s.line([(193, 356), (228, 358), (227, 382), (192, 380)], c["scope_remaining"])
        if c["has_session"]:
            s.line([(29, 394), (118, 404), (118, 413), (29, 405)], c["session_reset"])
        s.line([(185, 406), (247, 418), (247, 428), (185, 417)], c["scope_reset"])
        s.line([(367, 351), (531, 328), (533, 345), (367, 369)], cr)
        s.line([(367, 377), (534, 354), (535, 370), (367, 394)], xr, "white")
        s.panel(
            [(365, 405), (555, 385), (557, 418), (366, 437)],
            [(credits, 14, "black"), (stamp, 12, "black")],
        )
    elif artwork == "04-night-market":
        s.panel(
            [(92, 22), (297, 122), (297, 232), (92, 131)],
            [(c["name"], 28, "white"), (c["remaining"], 76, "#f2cb19"), (c["window"], 23, "white")],
            "Bangers-Regular.ttf",
        )
        s.panel(
            [(410, 132), (541, 52), (542, 181), (410, 235)],
            [(x["name"], 28, "white"), (x["remaining"], 76, "#df3322"), (x["window"], 23, "white")],
            "Bangers-Regular.ttf",
        )
        if c["has_session"]:
            s.line([(58, 208), (309, 281), (309, 297), (58, 224)], session, "white")
        s.panel(
            [(34, 261), (76, 263), (75, 333), (33, 334)],
            scope_rows
            + [(part, 13, "black") for part in (c["scope_reset"] or "NOT REPORTED").split()],
        )
        s.line([(414, 296), (590, 227), (590, 244), (414, 312)], xr)
        s.panel(
            [(450, 326), (579, 282), (579, 341), (450, 363)],
            [("CODEX RESETS", 16, "black")]
            + [(part, 20, "black") for part in x["credits"].split(" / ")],
            background="white",
        )
        s.panel(
            [(479, 375), (588, 354), (588, 395), (479, 407)],
            [
                (ch, 12, "white"),
                (cd, 17, "white"),
                ("AS OF " + view["as_of_date"], 12, "white"),
                (view["as_of_time"] + " SGT", 17, "white"),
            ],
            background="black",
        )
    elif artwork == "05-quota-moth":
        s.headline(
            [(85, 104), (214, 112), (215, 202), (84, 204)],
            c,
            "#df3322",
            "DMSerifDisplay-Regular.ttf",
        )
        s.headline(
            [(389, 113), (520, 104), (523, 204), (389, 205)],
            x,
            "#174992",
            "DMSerifDisplay-Regular.ttf",
        )
        if c["has_session"]:
            s.line([(63, 307), (215, 287), (216, 302), (64, 322)], session)
        s.line([(87, 343), (222, 331), (222, 345), (87, 358)], scope)
        s.line([(383, 288), (535, 309), (535, 322), (383, 302)], cr)
        s.line([(381, 331), (521, 344), (520, 358), (381, 345)], xr)
        s.line([(184, 384), (416, 384), (416, 398), (184, 398)], credits)
        s.line([(248, 411), (352, 411), (352, 422), (248, 422)], stamp)
    elif artwork == "06-cosmic-pinball":
        s.line([(91, 35), (205, 37), (204, 58), (92, 58)], c["name"], family="Bangers-Regular.ttf")
        s.line(
            [(402, 36), (514, 36), (510, 57), (403, 57)], x["name"], family="Bangers-Regular.ttf"
        )
        s.line(
            [(75, 89), (219, 94), (217, 158), (76, 156)],
            c["remaining"],
            "#df3322",
            "Bangers-Regular.ttf",
        )
        s.line(
            [(397, 93), (528, 92), (526, 160), (397, 160)],
            x["remaining"],
            "#df3322",
            "Bangers-Regular.ttf",
        )
        s.line([(94, 170), (200, 170), (200, 189), (94, 189)], c["window"])
        s.line([(400, 175), (507, 175), (507, 193), (400, 193)], x["window"])
        if c["has_session"]:
            s.panel(
                [(140, 231), (235, 236), (247, 259), (140, 253)],
                [("CLAUDE 5H " + c["session"], 15, "black"), (c["session_reset"], 12, "black")],
            )
        s.panel(
            [(368, 236), (460, 232), (460, 253), (353, 259)],
            [(c["scope"], 15, "black"), (c["scope_reset"], 12, "black")],
        )
        s.panel(
            [(128, 308), (212, 327), (210, 342), (132, 330)],
            [(ch, 12, "black"), (cd, 18, "black")],
        )
        s.panel(
            [(391, 327), (474, 307), (470, 332), (392, 344)],
            [(xh, 12, "black"), (xd, 18, "black")],
        )
        s.line([(17, 395), (226, 418), (224, 431), (17, 414)], credits, "white")
        s.line([(464, 410), (587, 396), (587, 413), (458, 431)], stamp, "white")
    else:
        raise ValueError(f"Unknown artwork: {artwork}")
    return s.finish()
