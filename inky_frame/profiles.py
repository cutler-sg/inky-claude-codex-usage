"""Supported panel identities and their image/GPIO contracts; no hardware imports."""

from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True)
class DisplayProfile:
    name: str
    resolution: tuple[int, int]
    variants: tuple[int, ...]
    driver: str
    inks: tuple[str, ...]
    working_inks: tuple[str, ...]
    button_pins: tuple[int, int, int, int] = (5, 6, 16, 24)

    @property
    def palette(self) -> list[int]:
        return [channel for color in self.inks for channel in bytes.fromhex(color)]

    @property
    def buttons(self) -> dict[int, tuple[str, str]]:
        return dict(
            zip(
                self.button_pins,
                zip("ABCD", ("previous", "next", "random", "home"), strict=True),
                strict=True,
            )
        )

    def validate_frame(self, image: Image.Image) -> None:
        if (
            image.size != self.resolution
            or image.mode != "P"
            or image.getpalette()[: len(self.palette)] != self.palette
            or not set(image.tobytes()) <= set(range(len(self.inks)))
        ):
            raise ValueError(
                f"Frame must match {self.name}: {self.resolution}, {len(self.inks)} indexed colours"
            )


LEGACY = DisplayProfile(
    "impression-5.7",
    (600, 448),
    (14,),
    "inky.inky_uc8159",
    ("000000", "ffffff", "00ff00", "0000ff", "ff0000", "ffff00", "ff8c00"),
    ("000000", "ffffff", "16603d", "174992", "df3322", "f2cb19", "eb821b"),
)
SPECTRA_INKS = ("000000", "ffffff", "ffff00", "ff0000", "0000ff", "00ff00")
SPECTRA_WORK = ("000000", "ffffff", "f2cb19", "df3322", "174992", "16603d")
PROFILES = {
    profile.name: profile
    for profile in (
        LEGACY,
        DisplayProfile(
            "spectra6-4.0", (600, 400), (25,), "inky.inky_e640", SPECTRA_INKS, SPECTRA_WORK
        ),
        DisplayProfile(
            "spectra6-7.3", (800, 480), (22, 26), "inky.inky_e673", SPECTRA_INKS, SPECTRA_WORK
        ),
        DisplayProfile(
            "spectra6-13.3",
            (1600, 1200),
            (21, 27),
            "inky.inky_el133uf1",
            SPECTRA_INKS,
            SPECTRA_WORK,
            (5, 6, 25, 24),
        ),
    )
}


def resolve_profile(width: int, height: int, variant: int) -> DisplayProfile:
    for profile in PROFILES.values():
        if variant in profile.variants:
            if (width, height) != profile.resolution:
                raise ValueError(
                    f"EEPROM variant {variant} requires {profile.resolution}; "
                    f"detected {width}x{height}"
                )
            return profile
    raise ValueError(
        f"Unsupported Inky EEPROM variant {variant} ({width}x{height}); "
        f"supported profiles: {', '.join(PROFILES)}"
    )
