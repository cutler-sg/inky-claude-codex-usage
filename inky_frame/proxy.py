"""CLIProxyAPI management adapter; vendor OAuth credentials stay on the proxy."""

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from urllib.parse import urlsplit

CLAUDE_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
CODEX_USAGE_URL = "https://chatgpt.com/backend-api/wham/usage"
CLAUDE_HEADERS = {
    "Authorization": "Bearer $TOKEN$",
    "Content-Type": "application/json",
    "anthropic-beta": "oauth-2025-04-20",
}
CODEX_HEADERS = {
    "Authorization": "Bearer $TOKEN$",
    "Content-Type": "application/json",
    "User-Agent": "codex_cli_rs/0.76.0 (Debian 13.0.0; x86_64) WindowsTerminal",
}
MISSING_KEY_ERROR = "CLI_PROXY_API_MANAGEMENT_KEY is not configured"
MAX_RESPONSE = 1024 * 1024


def proxy_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or any(char.isspace() for char in value)
    ):
        raise ValueError("CLI_PROXY_API_BASE_URL must be an HTTPS URL without credentials or query")
    return value.rstrip("/")


def get_management_key() -> str | None:
    return os.environ.get("CLI_PROXY_API_MANAGEMENT_KEY", "").strip() or None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the management Authorization header to a redirected endpoint.
        return None


def management_call(
    key: str, path: str, payload: dict | None = None
) -> tuple[dict | None, str | None]:
    try:
        base = proxy_url(os.environ.get("CLI_PROXY_API_BASE_URL", ""))
        request = urllib.request.Request(
            base + path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST" if payload is not None else "GET",
        )
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=10) as response:
            body = response.read(MAX_RESPONSE + 1)
        if len(body) > MAX_RESPONSE:
            return None, "Management API response exceeds 1 MiB"
        data = json.loads(body)
        if not isinstance(data, dict):
            return None, "Management API returned an invalid object"
        return data, None
    except urllib.error.HTTPError as error:
        return None, f"Management API HTTP {error.code}"
    except (urllib.error.URLError, OSError):
        return None, "Management API connection failed"
    except (ValueError, UnicodeError):
        return None, "Invalid management API configuration or JSON response"


def list_auth_indexes(key: str) -> tuple[dict[str, str], str | None]:
    data, error = management_call(key, "/v0/management/auth-files")
    if error:
        return {}, error
    files = data.get("files")
    if not isinstance(files, list):
        return {}, "Management API returned invalid auth-file metadata"
    indexes = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        provider = entry.get("provider") or entry.get("type")
        index = entry.get("auth_index")
        if (
            provider in ("claude", "codex")
            and provider not in indexes
            and not entry.get("disabled")
            and isinstance(index, str)
            and index
        ):
            indexes[provider] = index
    return indexes, None


def fetch_usage(key, indexes, provider, url, headers):
    index = indexes.get(provider)
    if not index:
        return None, f"No enabled {provider} account on proxy"
    envelope, error = management_call(
        key,
        "/v0/management/api-call",
        {"auth_index": index, "method": "GET", "url": url, "header": headers},
    )
    if error:
        return None, error
    status = envelope.get("status_code")
    if isinstance(status, bool) or not isinstance(status, int) or not 200 <= status < 300:
        return None, f"{provider} upstream HTTP {status if isinstance(status, int) else 'invalid'}"
    body = envelope.get("body")
    try:
        data = json.loads(body) if isinstance(body, str) else body
    except ValueError:
        return None, f"Invalid {provider} usage JSON"
    if not isinstance(data, dict):
        return None, f"Invalid {provider} usage object"
    return data, None


def normalize_claude(data: dict) -> list[dict]:
    entries = data.get("limits")
    if not isinstance(entries, list) or not entries:
        entries = []
        for kind, key in (("session", "five_hour"), ("weekly_all", "seven_day")):
            window = data.get(key) or {}
            if not isinstance(window, dict):
                raise ValueError("Invalid Claude usage window")
            if window.get("utilization") is not None:
                entries.append(
                    {
                        "kind": kind,
                        "percent": window["utilization"],
                        "resets_at": window.get("resets_at"),
                    }
                )
    result = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Invalid Claude limit")
        if entry.get("percent") is None:
            continue
        kind = entry.get("kind")
        if kind == "session":
            label = "5-Hour Window"
        elif kind == "weekly_all":
            label = "7-Day · All models"
        elif kind == "weekly_scoped":
            model = (entry.get("scope") or {}).get("model") or {}
            label = "7-Day · " + (model.get("display_name") or "Scoped")
        else:
            label = str(kind or "Usage").replace("_", " ").title()
        reset = entry.get("resets_at")
        result.append(
            {
                "label": label,
                "percent": entry["percent"],
                "reset_epoch": datetime.fromisoformat(reset.replace("Z", "+00:00")).timestamp()
                if reset
                else None,
            }
        )
    return result


def normalize_codex(data: dict) -> list[dict]:
    limits = data.get("rate_limit") or {}
    if not isinstance(limits, dict):
        raise ValueError("Invalid Codex rate limit")
    result = []
    for slot in ("primary_window", "secondary_window"):
        window = limits.get(slot)
        if window is None:
            continue
        if not isinstance(window, dict):
            raise ValueError("Invalid Codex usage window")
        if window.get("used_percent") is None:
            continue
        seconds = window.get("limit_window_seconds")
        if not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or seconds <= 0:
            raise ValueError("Missing Codex window duration")
        label = (
            "5-Hour Window"
            if seconds <= 6 * 3600
            else "Daily"
            if seconds <= 26 * 3600
            else "7-Day"
            if seconds <= 8 * 86400
            else f"{int(seconds // 86400)}-Day"
        )
        reset = window.get("reset_at")
        if not reset and window.get("reset_after_seconds") is not None:
            reset = time.time() + window["reset_after_seconds"]
        result.append({"label": label, "percent": window["used_percent"], "reset_epoch": reset})
    return result
