import pytest
from PIL import Image

from inky_frame.__main__ import load_image
from inky_frame.images import prepare


def test_contain_preserves_image_with_white_margins():
    result = prepare(Image.new("RGB", (100, 100), "red"))
    assert result.size == (600, 448)
    assert result.getpixel((0, 224)) == (255, 255, 255)
    assert result.getpixel((300, 224)) == (255, 0, 0)


def test_cover_fills_the_screen():
    result = prepare(Image.new("RGB", (100, 100), "red"), "cover")
    assert result.getextrema() == ((255, 255), (0, 0), (0, 0))


def test_transparency_is_composited_before_resizing():
    result = prepare(Image.new("RGBA", (600, 448), (255, 0, 0, 128)))
    assert result.mode == "RGB"
    assert result.getpixel((300, 224)) == (255, 127, 127)


def test_exif_orientation_is_applied():
    image = Image.new("RGB", (600, 448), "red")
    image.getexif()[274] = 6
    result = prepare(image)
    assert result.getpixel((0, 224)) == (255, 255, 255)


def test_explicit_rotation_is_applied():
    image = Image.new("RGB", (600, 448), "red")
    image.paste("blue", (0, 0, 300, 448))
    result = prepare(image, rotation=180)
    assert result.getpixel((0, 224)) == (255, 0, 0)
    assert result.getpixel((599, 224)) == (0, 0, 255)


def test_unknown_fit_fails():
    with pytest.raises(ValueError, match="Unknown fit"):
        prepare(Image.new("RGB", (1, 1)), "stretch")


def test_corrupt_input_fails_before_hardware_access(tmp_path):
    source = tmp_path / "invalid.png"
    source.write_bytes(b"not an image")
    with pytest.raises(Image.UnidentifiedImageError):
        load_image(str(source), "contain", 0)
