import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PIL import Image

from inky_frame import __main__ as cli


def test_concurrent_refresh_is_rejected(tmp_path):
    with (
        cli.display_lock(tmp_path),
        pytest.raises(cli.DisplayError, match="already running"),
        cli.display_lock(tmp_path),
    ):
        pytest.fail("Second process acquired the display")
    with cli.display_lock(tmp_path):
        pass


def test_failed_refresh_does_not_replace_successful_state(tmp_path, monkeypatch):
    previous = {"sha256": "previous-image"}
    (tmp_path / "status.json").write_text(json.dumps(previous))
    display = Mock()
    display.show.side_effect = OSError("SPI transfer failed")
    monkeypatch.setattr(cli, "STATE", tmp_path)
    monkeypatch.setattr(
        cli,
        "read_display",
        lambda: (display, SimpleNamespace(width=600, height=448, display_variant=14)),
    )
    with pytest.raises(OSError, match="SPI transfer failed"):
        cli.show(Image.new("RGB", (600, 448)), 0.5, False)
    assert json.loads((tmp_path / "status.json").read_text()) == previous
    assert not (tmp_path / "current.png").exists()


def test_identical_image_skips_hardware_refresh(tmp_path, monkeypatch):
    display = Mock()
    monkeypatch.setattr(cli, "STATE", tmp_path)
    monkeypatch.setattr(
        cli,
        "read_display",
        lambda: (display, SimpleNamespace(width=600, height=448, display_variant=14)),
    )
    image = Image.new("RGB", (600, 448))
    cli.show(image, 0.5, False)
    cli.show(image, 0.5, False)
    assert display.show.call_count == 1
    cli.show(image, 0.5, True)
    assert display.show.call_count == 2
