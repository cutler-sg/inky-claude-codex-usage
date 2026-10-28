from inky_frame.collect import collect


def test_provider_failure_preserves_its_observation_without_blocking_other_provider(tmp_path):
    collector = tmp_path / "collector.py"
    collector.write_text("""
CLAUDE_USAGE_URL = CODEX_USAGE_URL = "unused"
CLAUDE_HEADERS = CODEX_HEADERS = {}
def get_management_key(): return "test-only"
def list_auth_indexes(key): return {"claude": "c", "codex": "x"}, None
def fetch_usage(key, indexes, name, url, headers):
    if name == "claude": return None, "Rate limited"
    return {"secret": "do not export", "rate_limit_reset_credits": {
        "available_count": 2, "applicable_available_count": 0}}, None
def normalize_codex(data):
    return [{"label": "7-Day", "percent": 9, "reset_epoch": 2000000}]
""")
    previous = {
        "providers": {
            "claude": {
                "observed_at": 1000000,
                "error": None,
                "credits": None,
                "windows": [{"label": "7-Day", "used_percent": 81, "reset_epoch": 2000000}],
            }
        }
    }
    result = collect(collector, previous)
    claude, codex = (result["providers"][p] for p in ("claude", "codex"))
    assert claude["observed_at"] == 1000000
    assert claude["error"] == "Rate limited"
    assert claude["windows"] == previous["providers"]["claude"]["windows"]
    assert codex["error"] is None
    assert codex["windows"][0]["used_percent"] == 9
    assert codex["observed_at"] > 1000000
    assert "secret" not in str(result)


def test_missing_key_does_not_call_provider_or_synthesize_usage(tmp_path):
    collector = tmp_path / "collector.py"
    collector.write_text("""
def get_management_key(): return None
def list_auth_indexes(key): raise AssertionError("No credential")
def fetch_usage(*args): raise AssertionError("No credential")
""")
    result = collect(collector)
    for provider in result["providers"].values():
        assert provider["observed_at"] is None
        assert provider["windows"] == []
        assert provider["error"] == "Keychain unavailable"
