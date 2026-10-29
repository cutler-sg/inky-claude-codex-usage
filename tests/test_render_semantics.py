import copy
import json
from pathlib import Path

import pytest

from inky_frame import live

FIXTURES = Path(__file__).parent / "fixtures"
EDGE = json.loads((FIXTURES / "render-edge-snapshots.json").read_text())


def view(scenario):
    return live.build_view(EDGE["scenarios"][scenario], EDGE["now"])


def test_restrictive_scope_keeps_its_own_deadline_and_signals_other_scopes():
    claude = view("multiple-scopes")["claude"]
    assert claude["scope_name"] == "OPUS"
    assert claude["scope_remaining"] == "5%"
    assert claude["scope_more"] == 1
    assert claude["scope"] == "OPUS 5% +1"
    assert claude["scope_reset"] == "FRI 05:00"


def test_long_scope_abbreviates_name_without_erasing_percentage():
    snapshot = copy.deepcopy(EDGE["scenarios"]["multiple-scopes"])
    snapshot["providers"]["claude"]["windows"][-1]["label"] = "7-Day · " + "Long name " * 7
    claude = live.build_view(snapshot, EDGE["now"])["claude"]
    assert "…" in claude["scope"]
    assert claude["scope"].endswith("5% +1")


@pytest.mark.parametrize("artwork", live.ARTWORKS)
def test_scope_headline_reset_is_not_mislabeled_as_session(monkeypatch, artwork):
    monkeypatch.setattr(live, "Canvas", TextCapture)
    result = view("scope-without-weekly")
    assert result["claude"]["remaining"] == "5%"
    assert result["claude"]["reset_window"] == "OPUS"
    text = live.render(artwork, result)
    assert "CLAUDE OPUS" in text
    assert "FRI 05:00" in text


def test_future_invalid_observations_do_not_claim_a_future_as_of_time():
    result = view("future-clock")
    assert result["as_of"] == "NO USAGE OBSERVATIONS"
    assert result["as_of_date"] == "NO DATA"
    assert result["claude"]["remaining"] == result["codex"]["remaining"] == "--"


def test_mixed_health_retains_independent_states_and_oldest_real_observation():
    result = view("mixed-health")
    assert result["claude"]["name"] == "CLAUDE / STALE"
    assert result["codex"]["name"] == "CODEX"
    assert result["as_of"].endswith("04:30 SGT")
    result = view("expired-provider")
    assert result["claude"]["remaining"] == "--"
    assert result["codex"]["remaining"] == "25%"


class TextCapture(live.Canvas):
    def __init__(self, artwork, profile):
        self.lines = []

    def panel(self, quad, lines, family=None, **kwargs):
        self.lines.extend(value for value, _, _ in lines)

    def finish(self):
        return "\n".join(self.lines)


@pytest.mark.parametrize("artwork", live.ARTWORKS)
def test_every_scene_exposes_reported_codex_session_exhaustion(monkeypatch, artwork):
    monkeypatch.setattr(live, "Canvas", TextCapture)
    text = live.render(artwork, view("multiple-scopes"))
    assert "CODEX 5H 0%" in text
    assert "7D SAT 05:00" in text
    assert "25%" in text


@pytest.mark.parametrize("artwork", live.ARTWORKS)
def test_nonweekly_headline_keeps_its_actual_reset(monkeypatch, artwork):
    monkeypatch.setattr(live, "Canvas", TextCapture)
    text = live.render(artwork, view("missing-windows"))
    assert "5H LEFT" in text
    assert "40%" in text
    assert "CODEX 5H" in text
    assert "THU 06:00" in text
