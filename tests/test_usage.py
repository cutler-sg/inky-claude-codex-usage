import copy
import json
from pathlib import Path

import pytest

from inky_frame.live import ARTWORKS, build_view, render
from inky_frame.usage import EXPIRED_SECONDS, STALE_SECONDS, validate_snapshot


@pytest.fixture
def snapshot():
    frozen = json.loads((Path(__file__).parents[1] / "designs/data/snapshot.json").read_text())
    providers = {}
    for name, provider in frozen["providers"].items():
        providers[name] = {
            "observed_at": 1000000,
            "error": None,
            "windows": [
                {"label": w["label"], "used_percent": w["percent"], "reset_epoch": 2000000}
                for w in provider["windows"]
            ],
            "credits": provider.get("reset_credits"),
        }
    return validate_snapshot({"version": 1, "collected_at": 1000000, "providers": providers})


def test_contract_strips_unrecognized_fields(snapshot):
    snapshot["oauth_token"] = "must-not-be-transmitted"
    snapshot["providers"]["codex"]["account_email"] = "private"
    clean = validate_snapshot(snapshot)
    assert "oauth_token" not in clean
    assert "account_email" not in clean["providers"]["codex"]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, 101, True, "81"])
def test_invalid_usage_is_rejected(snapshot, value):
    snapshot["providers"]["claude"]["windows"][0]["used_percent"] = value
    with pytest.raises(ValueError):
        validate_snapshot(snapshot)


def test_provider_freshness_is_independent_and_expired_values_disappear(snapshot):
    snapshot["providers"]["claude"]["error"] = "Rate limited"
    view = build_view(snapshot, 1000001)
    assert view["claude"]["name"] == "CLAUDE / STALE"
    assert view["claude"]["remaining"] == "20%"
    assert view["codex"]["name"] == "CODEX"
    assert build_view(snapshot, 1000000 + STALE_SECONDS)["codex"]["name"] == "CODEX / STALE"
    expired = build_view(snapshot, 1000000 + EXPIRED_SECONDS)
    assert expired["claude"]["remaining"] == "--"
    assert expired["codex"]["credits"] == "NOT REPORTED"


def test_missing_session_and_passed_reset_do_not_imply_replenishment(snapshot):
    snapshot["providers"]["claude"]["windows"][1]["reset_epoch"] = 999999
    view = build_view(snapshot, 1000001)
    assert view["codex"]["session"] == "--"
    assert view["claude"]["remaining"] == "20%"
    assert view["claude"]["reset"] == "UPDATE PENDING"


@pytest.mark.parametrize("artwork", ARTWORKS)
def test_every_artwork_renders_live_changes_in_seven_inks(snapshot, artwork):
    before = render(artwork, build_view(snapshot, 1000001))
    changed = copy.deepcopy(snapshot)
    changed["providers"]["claude"]["windows"][1]["used_percent"] = 91
    after = render(artwork, build_view(changed, 1000001))
    assert before.size == (600, 448)
    assert before.mode == "P"
    assert set(before.tobytes()) <= set(range(7))
    assert before.tobytes() != after.tobytes()
