"""Check pinned vendor image conversion on the Pi without constructing GPIO drivers.

Run: .venv/bin/python -m scripts.check_driver_palettes
"""

import importlib
import json

import numpy as np
from PIL import Image

from inky_frame.profiles import LEGACY, PROFILES


def main():
    for profile in PROFILES.values():
        module = importlib.import_module(profile.driver)
        # Bypass __init__: this check must never initialize SPI/GPIO or read EEPROM.
        driver = module.Inky.__new__(module.Inky)
        driver.width, driver.height = profile.resolution
        driver.cols, driver.rows = module._RESOLUTION[profile.resolution][:2]
        indices = np.arange(driver.width * driver.height, dtype=np.uint32) % len(profile.inks)
        image = Image.frombytes("P", profile.resolution, indices.astype("uint8").tobytes())
        image.putpalette(profile.palette)
        driver.set_image(image)
        mapping = np.arange(7) if profile == LEGACY else np.array([0, 1, 2, 3, 5, 6])
        np.testing.assert_array_equal(driver.buf.ravel(), mapping[indices])
        print(
            json.dumps(
                {"profile": profile.name, "native_mapping": mapping.tolist(), "passed": True}
            )
        )


if __name__ == "__main__":
    main()
