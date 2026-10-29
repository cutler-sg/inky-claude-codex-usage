# Refresh-driven artwork rotation

Branch: `feat/refresh-artwork-rotation`

## Behavior and acceptance

- [x] Default to sequential rotation on usage-update/freshness refreshes; preserve the current artwork on migration and unchanged restarts.
- [x] A/B select previous/next and lock. C immediately chooses a different random artwork and resumes rotation. D and explicit artwork selection lock the chosen artwork.
- [x] Persist mode and the last scheduled update key. Do not rotate on every polling tick or every retry; coalesce data updates while busy into one next artwork.
- [x] Preserve one refresh worker, 40-second start spacing, settle/debounce behavior, retry behavior, and latest button selection.
- [x] Test controls, migration/restart, unchanged polls, new snapshots, freshness changes, failures, and inputs during a refresh.
- [x] Update documentation, deploy to the Pi, verify rotation/locking using the same control path as buttons, and leave rotation enabled.
- [x] Commit, scan and push the validated branch for merge.

## Implementation

1. [x] Add persisted rotation state and schedule one advance when a data-driven refresh starts.
2. [x] Add focused scheduler/control tests and update user-facing button documentation.
3. [x] Validate and deploy with state/source rollback, exercise real refresh behavior, publish revisions.

Automatic rotation uses the normal data refresh cadence, not a separate fast slideshow timer. Legacy artwork-only selection files default to rotating without changing their selected artwork immediately.

## Verification

- 160 tests pass, including 16 gallery/control cases. Ruff check/format and whitespace checks pass; rendered-image baselines remain unchanged.
- Headless candidate on the Pi verifies migration, automatic wraparound, locking and resume without display I/O.
- Live Pi migration preserved Night Market. A fresh real collection advanced automatically to Quota Moth. Previous/next locked the choice, and a later collection retained that locked artwork.
- C selected another random artwork and resumed rotating mode. A service restart preserved both Night Market and rotating mode without advancing again. The tested production gallery file matches the local SHA-256.
- One extra manual collection hit Claude upstream HTTP 429; Codex succeeded and Claude's last-good data remained visibly stale. Further manual API calls were stopped. The normal ten-minute timer remains active; collection/auth code was not changed.
- Source and prior selection rollback are under `/tmp/inky-rotation.lwVKCC/` on the Pi. No credentials or protected configuration were touched.
