import json

import pytest

from inky_frame import poll


def test_failed_provider_still_publishes_snapshot_before_nonzero_exit(tmp_path, monkeypatch):
    snapshot = {
        "version": 1,
        "collected_at": 1234567,
        "providers": {
            "claude": {
                "observed_at": 1000000,
                "error": "claude upstream HTTP 429",
                "windows": [{"label": "7-Day", "used_percent": 81, "reset_epoch": 2000000}],
            },
            "codex": {"observed_at": 1234567, "error": None, "windows": []},
        },
    }
    monkeypatch.setattr(poll, "STATE", tmp_path)
    monkeypatch.setattr(poll, "collect", lambda **kwargs: snapshot)
    monkeypatch.setattr("sys.argv", ["inky_frame.poll"])
    with pytest.raises(SystemExit) as result:
        poll.main()
    assert result.value.code == 1
    saved = json.loads((tmp_path / "usage.json").read_text())
    assert saved == snapshot
