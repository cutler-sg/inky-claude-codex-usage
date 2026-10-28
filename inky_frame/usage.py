"""The credential-free usage contract shared by the Mac collector and Pi renderer."""

import json
import math
from pathlib import Path

PROVIDERS = ("claude", "codex")
STALE_SECONDS = 20 * 60
EXPIRED_SECONDS = 24 * 3600


def number(value, name: str, *, minimum=0, maximum=10**12) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f"{name} is out of range")
    return float(value)


def text(value, name: str, maximum=100) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError(f"Invalid {name}")
    if any(ord(char) < 32 for char in value):
        raise ValueError(f"Control character in {name}")
    return value


def validate_snapshot(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Expected usage snapshot version 1")
    result = {
        "version": 1,
        "collected_at": number(data.get("collected_at"), "collected_at"),
        "providers": {},
    }
    providers = data.get("providers")
    if not isinstance(providers, dict):
        raise ValueError("Missing usage providers")
    for name in PROVIDERS:
        provider = providers.get(name)
        if not isinstance(provider, dict):
            raise ValueError(f"Missing {name} usage")
        observed = provider.get("observed_at")
        error = provider.get("error")
        windows = provider.get("windows")
        if not isinstance(windows, list) or len(windows) > 16:
            raise ValueError(f"Invalid {name} windows")
        clean = {
            "observed_at": number(observed, "observed_at") if observed is not None else None,
            "error": text(error, "error", 200) if error is not None else None,
            "windows": [],
            "credits": None,
        }
        if windows and observed is None:
            raise ValueError(f"{name} windows require an observation time")
        for window in windows:
            if not isinstance(window, dict):
                raise ValueError(f"Invalid {name} window")
            reset = window.get("reset_epoch")
            clean["windows"].append(
                {
                    "label": text(window.get("label"), "window label", 80),
                    "used_percent": number(window.get("used_percent"), "used_percent", maximum=100),
                    "reset_epoch": number(reset, "reset_epoch") if reset is not None else None,
                }
            )
        credits = provider.get("credits")
        if credits is not None:
            if name != "codex" or not isinstance(credits, dict):
                raise ValueError("Invalid reset credits")
            clean["credits"] = {}
            for key in ("available_count", "applicable_available_count"):
                count = number(credits.get(key), key, maximum=10000)
                if not count.is_integer():
                    raise ValueError(f"{key} must be an integer")
                clean["credits"][key] = int(count)
        result["providers"][name] = clean
    return result


def load_snapshot(path: Path) -> dict:
    return validate_snapshot(json.loads(path.read_text()))


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.json")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def provider_state(provider: dict, now: float) -> str:
    observed = provider["observed_at"]
    if observed is None or now - observed >= EXPIRED_SECONDS or observed > now + 60:
        return "UNAVAILABLE"
    if provider["error"] or now - observed >= STALE_SECONDS:
        return "STALE"
    return "LIVE"
