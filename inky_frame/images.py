from PIL import Image, ImageDraw, ImageFont, ImageOps

from .profiles import LEGACY, DisplayProfile

RESOLUTION = LEGACY.resolution
COLORS = ["black", "white", "green", "blue", "red", "yellow", "orange"]


def prepare(
    image: Image.Image,
    fit: str = "contain",
    rotation: int = 0,
    profile: DisplayProfile = LEGACY,
) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGBA")
    background = Image.new("RGBA", image.size, "white")
    background.alpha_composite(image)
    image = background.convert("RGB").rotate(rotation, expand=True)
    if fit == "cover":
        return ImageOps.fit(image, profile.resolution, method=Image.Resampling.LANCZOS)
    if fit != "contain":
        raise ValueError(f"Unknown fit mode: {fit}")
    image = ImageOps.contain(image, profile.resolution, method=Image.Resampling.LANCZOS)
    result = Image.new("RGB", profile.resolution, "white")
    result.paste(
        image,
        ((profile.resolution[0] - image.width) // 2, (profile.resolution[1] - image.height) // 2),
    )
    return result


def sample(profile: DisplayProfile = LEGACY) -> Image.Image:
    image = Image.new("RGB", RESOLUTION, "white")
    draw = ImageDraw.Draw(image)
    large = ImageFont.load_default(size=64)
    medium = ImageFont.load_default(size=24)
    small = ImageFont.load_default(size=18)
    draw.rectangle((0, 0, 599, 11), fill="black")
    draw.text((32, 36), "Hello, MC.", font=large, fill="black")
    draw.text((34, 118), "A little less screen. A little more ink.", font=medium, fill="black")
    # Geometric mountains use all seven panel colours without photographic dithering.
    draw.ellipse((435, 172, 510, 247), fill="orange" if profile == LEGACY else "yellow")
    draw.polygon([(30, 335), (180, 180), (330, 335)], fill="blue")
    draw.polygon([(170, 335), (350, 213), (570, 335)], fill="green")
    draw.polygon([(135, 227), (180, 180), (225, 227)], fill="white")
    draw.polygon([(368, 335), (430, 267), (492, 335)], fill="red")
    draw.line((30, 336, 570, 336), fill="black", width=3)
    draw.text(
        (32, 353),
        "INKY / IMPRESSION 5.7" if profile == LEGACY else "INKY / " + profile.name.upper(),
        font=small,
        fill="black",
    )
    draw.text(
        (32, 379),
        f"{profile.resolution[0]} x {profile.resolution[1]} pixels   /   "
        f"{len(profile.inks)} colours   /   pi@inky.local",
        font=small,
        fill="black",
    )
    for index, color in enumerate(COLORS if profile == LEGACY else ["#" + c for c in profile.inks]):
        x = 32 + index * 77
        draw.rectangle((x, 415, x + 65, 434), fill=color, outline="black", width=1)
    return image if profile == LEGACY else prepare(image, profile=profile)
