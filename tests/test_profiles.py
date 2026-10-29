import json
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
from PIL import Image

from inky_frame import __main__ as cli
from inky_frame.profiles import LEGACY, PROFILES, resolve_profile


@pytest.mark.parametrize("profile", PROFILES.values(), ids=PROFILES)
def test_identity_and_button_contracts(profile):
    for variant in profile.variants:
        assert resolve_profile(*profile.resolution, variant) == profile
        with pytest.raises(ValueError, match="requires"):
            resolve_profile(1, 1, variant)
    display_pins = (
        {10, 11, 22, 27, 17, 26, 16} if profile.name == "spectra6-13.3" else {10, 11, 22, 27, 17, 8}
    )
    assert set(profile.buttons).isdisjoint(display_pins)
    assert list(profile.buttons.values()) == list(LEGACY.buttons.values())


@pytest.mark.parametrize("variant", [0, 15, 20, 999])
def test_unknown_and_legacy_other_size_panels_are_not_guessed(variant):
    with pytest.raises(ValueError, match="Unsupported"):
        resolve_profile(800, 480, variant)


def install_vendor_double(monkeypatch, identity, profile=LEGACY, wrong_driver=False):
    package = ModuleType("inky")
    package.eeprom = SimpleNamespace(read_eeprom=lambda: identity)
    module = ModuleType("inky.auto")
    driver = type("Inky", (), {"__module__": "wrong" if wrong_driver else profile.driver})()
    driver.resolution = profile.resolution
    module.auto = Mock(return_value=driver)
    monkeypatch.setitem(sys.modules, "inky", package)
    monkeypatch.setitem(sys.modules, "inky.auto", module)
    return module.auto


@pytest.mark.parametrize("profile", PROFILES.values(), ids=PROFILES)
def test_hardware_detection_checks_metadata_before_driver_creation(monkeypatch, profile):
    identity = SimpleNamespace(
        width=profile.resolution[0],
        height=profile.resolution[1],
        display_variant=profile.variants[0],
    )
    auto = install_vendor_double(monkeypatch, identity, profile)
    assert cli.read_identity() == (profile, identity)
    auto.assert_not_called()
    driver, detected = cli.read_display()
    assert detected is identity
    assert driver.resolution == profile.resolution
    auto.assert_called_once_with(ask_user=False)


def test_missing_or_unknown_eeprom_does_not_create_driver(monkeypatch):
    for identity in (None, SimpleNamespace(width=800, height=480, display_variant=20)):
        auto = install_vendor_double(monkeypatch, identity)
        with pytest.raises((ValueError, cli.DisplayError)):
            cli.read_display()
        auto.assert_not_called()


def test_driver_mismatch_is_rejected(monkeypatch):
    install_vendor_double(
        monkeypatch, SimpleNamespace(width=600, height=448, display_variant=14), wrong_driver=True
    )
    with pytest.raises(cli.DisplayError, match="driver/resolution"):
        cli.read_display()


def test_digest_covers_palette_mode_and_profile():
    image = Image.new("P", LEGACY.resolution)
    image.putpalette(LEGACY.palette)
    original = cli.frame_digest(image, 0.5, LEGACY)
    image.putpalette(list(reversed(LEGACY.palette)))
    assert cli.frame_digest(image, 0.5, LEGACY) != original
    assert cli.frame_digest(image.convert("RGB"), 0.5, LEGACY) != original
    assert cli.frame_digest(image, 0.5, PROFILES["spectra6-4.0"]) != original


def test_wrong_profile_cannot_force_a_hardware_write(monkeypatch, tmp_path):
    display = Mock()
    monkeypatch.setattr(cli, "STATE", tmp_path)
    monkeypatch.setattr(
        cli,
        "read_display",
        lambda: (display, SimpleNamespace(width=600, height=448, display_variant=14)),
    )
    with pytest.raises(cli.DisplayError, match="Frame targets"):
        cli.show(Image.new("P", (600, 400)), 0.5, False, expected_profile=PROFILES["spectra6-4.0"])
    display.set_image.assert_not_called()


@pytest.mark.parametrize("profile", PROFILES.values(), ids=PROFILES)
def test_one_shot_image_is_prepared_for_detected_panel(monkeypatch, tmp_path, profile):
    display = Mock()
    monkeypatch.setattr(cli, "STATE", tmp_path)
    identity = SimpleNamespace(
        width=profile.resolution[0],
        height=profile.resolution[1],
        display_variant=profile.variants[0],
    )
    monkeypatch.setattr(cli, "read_display", lambda: (display, identity))
    cli.show(Image.new("RGBA", (30, 20), (255, 0, 0, 128)), 0.5, False, fit="cover")
    prepared = display.set_image.call_args.args[0]
    assert prepared.size == profile.resolution
    assert prepared.getpixel((0, 0)) == (255, 127, 127)
    assert json.loads((tmp_path / "status.json").read_text())["profile"] == profile.name


def test_same_size_frame_with_wrong_palette_is_rejected(monkeypatch, tmp_path):
    profile = PROFILES["spectra6-7.3"]
    display = Mock()
    monkeypatch.setattr(cli, "STATE", tmp_path)
    identity = SimpleNamespace(width=800, height=480, display_variant=26)
    monkeypatch.setattr(cli, "read_display", lambda: (display, identity))
    image = Image.new("P", profile.resolution)
    image.putpalette(LEGACY.palette)
    with pytest.raises(ValueError, match="Frame must match"):
        cli.show(image, 0.5, False, expected_profile=profile)
    display.set_image.assert_not_called()
