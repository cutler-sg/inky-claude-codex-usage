"""Collect through the built-in proxy adapter or a compatible external collector."""

import importlib.util
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .usage import PROVIDERS, validate_snapshot


def collect(collector_path: Path | None = None, previous: dict | None = None) -> dict:
    if collector_path is None:
        from . import proxy as collector
    else:
        spec = importlib.util.spec_from_file_location("existing_usage_collector", collector_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load collector: {collector_path}")
        collector = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(collector)
    # Never call main(): it also accesses unrelated OpenRouter credentials.
    key = collector.get_management_key()
    indexes, index_error = (
        collector.list_auth_indexes(key)
        if key
        else ({}, getattr(collector, "MISSING_KEY_ERROR", "Keychain unavailable"))
    )

    def fetch(name):
        prior = (previous or {}).get("providers", {}).get(name, {})
        result = {
            "observed_at": prior.get("observed_at"),
            "windows": prior.get("windows", []),
            "credits": prior.get("credits"),
            "error": None,
        }
        try:
            if index_error:
                raise ValueError(index_error)
            data, error = collector.fetch_usage(
                key,
                indexes,
                name,
                getattr(collector, f"{name.upper()}_USAGE_URL"),
                getattr(collector, f"{name.upper()}_HEADERS"),
            )
            if error or not isinstance(data, dict):
                raise ValueError(error or "Empty provider response")
            windows = getattr(collector, f"normalize_{name}")(data)
            if not windows:
                raise ValueError("Provider returned no usage windows")
            fresh = {
                "observed_at": time.time(),
                "error": None,
                "windows": [
                    {
                        "label": window["label"],
                        "used_percent": window["percent"],
                        "reset_epoch": window["reset_epoch"],
                    }
                    for window in windows
                ],
                "credits": data.get("rate_limit_reset_credits") if name == "codex" else None,
            }
            # Validate providers independently so a malformed payload preserves last-good data.
            stub = {"observed_at": None, "error": "Not fetched", "windows": []}
            checked = validate_snapshot(
                {
                    "version": 1,
                    "collected_at": time.time(),
                    "providers": {
                        provider: fresh if provider == name else stub for provider in PROVIDERS
                    },
                }
            )
            return name, checked["providers"][name]
        except (ValueError, TypeError, KeyError, AttributeError, OSError) as error:
            # Error text comes only from the collector's fixed messages or our validator.
            result["error"] = str(error)[:200] or type(error).__name__
            return name, result

    with ThreadPoolExecutor(max_workers=2) as pool:
        providers = dict(pool.map(fetch, PROVIDERS))
    return validate_snapshot({"version": 1, "collected_at": time.time(), "providers": providers})
