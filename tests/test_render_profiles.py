import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image, __version__

from inky_frame.images import prepare, sample
from inky_frame.live import ARTWORKS, build_view, render
from inky_frame.profiles import LEGACY, PROFILES

FIXTURES = Path(__file__).parent / "fixtures"
SNAPSHOTS = json.loads((FIXTURES / "render-snapshots.json").read_text())
BASELINE = json.loads((FIXTURES / "reviewed-render-hashes.json").read_text())


@pytest.mark.skipif(
    __version__ != BASELINE["pillow"],
    reason="Golden hashes require recorded Pillow; compare on-device before/after separately",
)
@pytest.mark.parametrize("scenario", SNAPSHOTS["scenarios"])
@pytest.mark.parametrize("artwork", ARTWORKS)
def test_reviewed_original_profile_pixels_and_palette(artwork, scenario):
    image = render(artwork, build_view(SNAPSHOTS["scenarios"][scenario], SNAPSHOTS["now"]))
    hashes = BASELINE["hashes"][f"{scenario}/{artwork}"]
    assert hashlib.sha256(image.tobytes()).hexdigest() == hashes["pixels"]
    assert hashlib.sha256(bytes(image.getpalette())).hexdigest() == hashes["palette"]


@pytest.mark.parametrize("profile", PROFILES.values(), ids=PROFILES)
@pytest.mark.parametrize("artwork", ARTWORKS)
def test_all_artworks_match_target_palette_and_dimensions(profile, artwork):
    image = render(artwork, build_view(SNAPSHOTS["scenarios"]["normal"], SNAPSHOTS["now"]), profile)
    profile.validate_frame(image)
    assert image.mode == "P"
    assert len(image.palette.colors) == len(profile.inks)
    if profile != LEGACY:
        assert "#ff8c00" not in ["#" + c for c in profile.inks]
    bad = image.copy()
    bad.putpixel((0, 0), 7)
    with pytest.raises(ValueError, match="Frame must match"):
        profile.validate_frame(bad)


@pytest.mark.parametrize("profile", PROFILES.values(), ids=PROFILES)
def test_preparation_rotation_transparency_and_sample_use_target(profile):
    rgba = Image.new("RGBA", (120, 80), (255, 0, 0, 128))
    fitted = prepare(rgba, rotation=90, profile=profile)
    assert fitted.size == profile.resolution
    assert fitted.getpixel((profile.resolution[0] // 2, profile.resolution[1] // 2)) == (
        255,
        127,
        127,
    )
    covered = prepare(rgba, "cover", profile=profile)
    assert covered.getextrema() == ((255, 255), (127, 127), (127, 127))
    indexed = Image.new("P", (10, 10))
    indexed.putpalette([255, 0, 0])
    assert prepare(indexed, "cover", profile=profile).getpixel((0, 0)) == (255, 0, 0)
    assert sample(profile).size == profile.resolution
