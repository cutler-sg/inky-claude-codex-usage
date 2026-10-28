from PIL import Image, ImageDraw, ImageFont, ImageOps

RESOLUTION = (600, 448)
COLORS = ["black", "white", "green", "blue", "red", "yellow", "orange"]


def prepare(image: Image.Image, fit: str = "contain", rotation: int = 0) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGBA")
    background = Image.new("RGBA", image.size, "white")
    background.alpha_composite(image)
    image = background.convert("RGB").rotate(rotation, expand=True)
    if fit == "cover":
        return ImageOps.fit(image, RESOLUTION, method=Image.Resampling.LANCZOS)
    if fit != "contain":
        raise ValueError(f"Unknown fit mode: {fit}")
    image = ImageOps.contain(image, RESOLUTION, method=Image.Resampling.LANCZOS)
    result = Image.new("RGB", RESOLUTION, "white")
    result.paste(image, ((600 - image.width) // 2, (448 - image.height) // 2))
    return result


def sample() -> Image.Image:
    image = Image.new("RGB", RESOLUTION, "white")
    draw = ImageDraw.Draw(image)
    large = ImageFont.load_default(size=64)
    medium = ImageFont.load_default(size=24)
    small = ImageFont.load_default(size=18)
    draw.rectangle((0, 0, 599, 11), fill="black")
    draw.text((32, 36), "Hello, MC.", font=large, fill="black")
    draw.text((34, 118), "A little less screen. A little more ink.", font=medium, fill="black")
    # Geometric mountains use all seven panel colours without photographic dithering.
    draw.ellipse((435, 172, 510, 247), fill="orange")
    draw.polygon([(30, 335), (180, 180), (330, 335)], fill="blue")
    draw.polygon([(170, 335), (350, 213), (570, 335)], fill="green")
    draw.polygon([(135, 227), (180, 180), (225, 227)], fill="white")
    draw.polygon([(368, 335), (430, 267), (492, 335)], fill="red")
    draw.line((30, 336, 570, 336), fill="black", width=3)
    draw.text((32, 353), "INKY / IMPRESSION 5.7", font=small, fill="black")
    draw.text(
        (32, 379), "600 x 448 pixels   /   7 colours   /   pi@inky.local", font=small, fill="black"
    )
    for index, color in enumerate(COLORS):
        x = 32 + index * 77
        draw.rectangle((x, 415, x + 65, 434), fill=color, outline="black", width=1)
    return image
