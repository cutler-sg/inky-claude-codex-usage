import json
import urllib.error
from unittest.mock import MagicMock

import pytest

from inky_frame import proxy
from inky_frame.collect import collect


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://user:password@example.com",
        "https://example.com?key=value",
        "",
        "https://example.com/#x",
    ],
)
def test_proxy_requires_https_without_embedded_credentials(url):
    with pytest.raises(ValueError):
        proxy.proxy_url(url)


def test_management_request_uses_bearer_key_and_does_not_follow_redirects(monkeypatch):
    monkeypatch.setenv("CLI_PROXY_API_BASE_URL", "https://proxy.example.com:9443/")
    response = MagicMock()
    response.__enter__.return_value.read.return_value = b'{"files": []}'
    opener = MagicMock()
    opener.open.return_value = response
    factory = MagicMock(return_value=opener)
    monkeypatch.setattr(proxy.urllib.request, "build_opener", factory)
    assert proxy.management_call("test-only", "/v0/management/auth-files") == ({"files": []}, None)
    request = opener.open.call_args.args[0]
    assert request.full_url == "https://proxy.example.com:9443/v0/management/auth-files"
    assert request.get_header("Authorization") == "Bearer test-only"
    assert request.get_method() == "GET"
    assert opener.open.call_args.kwargs["timeout"] == 10
    handler = factory.call_args.args[0]
    assert handler.redirect_request(None, None, 302, "", {}, "https://elsewhere.test") is None


def test_upstream_call_keeps_oauth_token_placeholder_on_proxy(monkeypatch):
    call = MagicMock(return_value=({"status_code": 200, "body": '{"rate_limit": {}}'}, None))
    monkeypatch.setattr(proxy, "management_call", call)
    data, error = proxy.fetch_usage(
        "test-only",
        {"codex": "account-index"},
        "codex",
        proxy.CODEX_USAGE_URL,
        proxy.CODEX_HEADERS,
    )
    assert error is None and data == {"rate_limit": {}}
    assert call.call_args.args[1] == "/v0/management/api-call"
    envelope = call.call_args.args[2]
    assert envelope["method"] == "GET"
    assert envelope["auth_index"] == "account-index"
    assert envelope["header"]["Authorization"] == "Bearer $TOKEN$"


def test_auth_selection_skips_disabled_and_never_exports_account_metadata(monkeypatch):
    files = [
        {"provider": "claude", "disabled": True, "auth_index": "disabled"},
        {"provider": "claude", "auth_index": "first", "private": "not exported"},
        {"provider": "claude", "auth_index": "second"},
        {"type": "codex", "auth_index": "codex-index"},
    ]
    monkeypatch.setattr(proxy, "management_call", lambda *args: ({"files": files}, None))
    assert proxy.list_auth_indexes("test-only") == (
        {"claude": "first", "codex": "codex-index"},
        None,
    )


def test_error_response_does_not_include_credentials_or_server_body(monkeypatch):
    monkeypatch.setenv("CLI_PROXY_API_BASE_URL", "https://proxy.example.com")
    opener = MagicMock()
    opener.open.side_effect = urllib.error.HTTPError("", 401, "private server message", {}, None)
    monkeypatch.setattr(proxy.urllib.request, "build_opener", lambda *args: opener)
    data, error = proxy.management_call("test-only", "/v0/management/auth-files")
    assert data is None and error == "Management API HTTP 401"


@pytest.mark.parametrize("body", [b"not json", b"[]", b"x" * (proxy.MAX_RESPONSE + 1)])
def test_management_rejects_invalid_or_oversized_payload(monkeypatch, body):
    monkeypatch.setenv("CLI_PROXY_API_BASE_URL", "https://proxy.example.com")
    response = MagicMock()
    response.__enter__.return_value.read.return_value = body
    opener = MagicMock()
    opener.open.return_value = response
    monkeypatch.setattr(proxy.urllib.request, "build_opener", lambda *args: opener)
    data, error = proxy.management_call("test-only", "/v0/management/auth-files")
    assert data is None and error
    assert "test-only" not in error


def test_direct_collection_preserves_failed_provider_and_normalizes_success(monkeypatch):
    monkeypatch.setenv("CLI_PROXY_API_MANAGEMENT_KEY", "test-only")
    monkeypatch.setattr(
        proxy, "list_auth_indexes", lambda key: ({"claude": "c", "codex": "x"}, None)
    )

    def fetch(key, indexes, name, url, headers):
        if name == "claude":
            return None, "claude upstream HTTP 429"
        return {
            "rate_limit": {
                "primary_window": {
                    "limit_window_seconds": 604800,
                    "used_percent": 7,
                    "reset_at": 2000000,
                }
            },
            "rate_limit_reset_credits": {"available_count": 2, "applicable_available_count": 0},
        }, None

    monkeypatch.setattr(proxy, "fetch_usage", fetch)
    previous = {
        "providers": {
            "claude": {
                "observed_at": 1000000,
                "windows": [
                    {"label": "7-Day · All models", "used_percent": 81, "reset_epoch": 2000000}
                ],
                "credits": None,
            }
        }
    }
    result = collect(previous=previous)
    assert result["providers"]["claude"]["observed_at"] == 1000000
    assert result["providers"]["claude"]["error"] == "claude upstream HTTP 429"
    assert result["providers"]["codex"]["windows"][0]["used_percent"] == 7
    assert result["providers"]["codex"]["credits"]["available_count"] == 2
    assert "test-only" not in json.dumps(result)


def test_claude_session_weekly_scoped_and_legacy_windows():
    windows = proxy.normalize_claude(
        {
            "limits": [
                {"kind": "session", "percent": 3, "resets_at": "2026-10-28T14:50:00Z"},
                {"kind": "weekly_all", "percent": 81},
                {
                    "kind": "weekly_scoped",
                    "percent": 43,
                    "scope": {"model": {"display_name": "Fable"}},
                },
            ]
        }
    )
    assert [w["label"] for w in windows] == ["5-Hour Window", "7-Day · All models", "7-Day · Fable"]
    assert windows[0]["reset_epoch"] == 1793199000
    assert proxy.normalize_claude({"seven_day": {"utilization": 81}})[0]["percent"] == 81


def test_codex_duration_and_relative_reset(monkeypatch):
    monkeypatch.setattr(proxy.time, "time", lambda: 1000000)
    result = proxy.normalize_codex(
        {
            "rate_limit": {
                "primary_window": {
                    "limit_window_seconds": 18000,
                    "used_percent": 2,
                    "reset_after_seconds": 100,
                }
            }
        }
    )
    assert result == [{"label": "5-Hour Window", "percent": 2, "reset_epoch": 1000100}]
    with pytest.raises(ValueError, match="duration"):
        proxy.normalize_codex({"rate_limit": {"primary_window": {"used_percent": 2}}})


@pytest.mark.parametrize(
    "weekly_only",
    [
        {"seven_day": {"utilization": 20}},
        {"five_hour": None, "seven_day": {"utilization": 20}},
        {"five_hour": {"utilization": None}, "seven_day": {"utilization": 20}},
        {"limits": [{"kind": "weekly_all", "percent": 20}]},
        {"limits": [{"kind": "session", "percent": None}, {"kind": "weekly_all", "percent": 20}]},
    ],
)
def test_session_disappearance_and_reappearance_replace_last_good_windows(monkeypatch, weekly_only):
    monkeypatch.setattr(proxy, "get_management_key", lambda: "test-only")
    monkeypatch.setattr(proxy, "list_auth_indexes", lambda key: ({"claude": "c"}, None))
    payload = {"five_hour": {"utilization": 0}, "seven_day": {"utilization": 20}}

    def fetch(key, indexes, name, url, headers):
        return (payload, None) if name == "claude" else (None, "Not configured")

    monkeypatch.setattr(proxy, "fetch_usage", fetch)
    first = collect()
    assert first["providers"]["claude"]["windows"][0]["used_percent"] == 0
    payload = weekly_only
    second = collect(previous=first)
    claude = second["providers"]["claude"]
    assert claude["error"] is None
    assert [w["label"] for w in claude["windows"]] == ["7-Day · All models"]
    assert claude["windows"][0]["used_percent"] == 20

    payload = {"limits": [{"kind": "session", "percent": 0}, {"kind": "weekly_all", "percent": 20}]}
    third = collect(previous=second)
    assert third["providers"]["claude"]["windows"][0]["label"] == "5-Hour Window"
    monkeypatch.setattr(proxy, "fetch_usage", lambda *args: (None, "Rate limited"))
    failed = collect(previous=third)["providers"]["claude"]
    assert failed["windows"] == third["providers"]["claude"]["windows"]
    assert failed["observed_at"] == third["providers"]["claude"]["observed_at"]
    assert failed["error"] == "Rate limited"
