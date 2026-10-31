# Optional Claude session limit

- [x] Hide Claude session text and reset captions in all six artworks when no session window is reported.
- [x] Test absent/null limits, zero usage, reappearance and failed-fetch retention; inspect renders across display profiles.
- [ ] Document, commit, publish and deploy the verified fix to the Pi.

Acceptance: a successful weekly-only Claude response removes the 5H details;
reported session limits (including zero usage) remain visible. Fetch failures
retain last-good data with its existing stale status. Weekly/scoped limits and
Codex remain unchanged. Full artwork-theme switching remains deferred.

Validation: 183 tests pass; Ruff lint/format and whitespace checks pass. Inspected
24 weekly-only previews (six artworks × four profiles) plus six unavailable-state
previews. Only the six unavailable baseline hashes change; all 24 baselines with
reported Claude sessions remain identical. Synthetic previews are under ignored
`state/optional-claude-session/previews/`.

The Pi's successful sanitized observation already omits the session window,
reporting only All models and Fable weekly limits. No collector or schema change
is needed. Deployment updates only `inky_frame/live.py`, with a previous-version
backup under `state/deployments/optional-claude-session/` on the Pi.
