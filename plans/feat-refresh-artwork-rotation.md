# Refresh-driven artwork rotation

Branch: `feat/refresh-artwork-rotation`

## Behavior and acceptance

- [x] Default to sequential rotation on usage-update/freshness refreshes; preserve the current artwork on migration and unchanged restarts.
- [x] A/B select previous/next and lock. C immediately chooses a different random artwork and resumes rotation. D and explicit artwork selection lock the chosen artwork.
- [x] Persist mode and the last scheduled update key. Do not rotate on every polling tick or every retry; coalesce data updates while busy into one next artwork.
- [x] Preserve one refresh worker, 40-second start spacing, settle/debounce behavior, retry behavior, and latest button selection.
- [x] Test controls, migration/restart, unchanged polls, new snapshots, freshness changes, failures, and inputs during a refresh.
- [ ] Update documentation, deploy to the Pi, verify rotation/locking using the same control path as buttons, and leave rotation enabled.
- [ ] Commit, scan, push and merge with clean repository state.

## Implementation

1. [x] Add persisted rotation state and schedule one advance when a data-driven refresh starts.
2. [x] Add focused scheduler/control tests and update user-facing button documentation.
3. [ ] Validate and deploy with state/source rollback, exercise real refresh behavior, publish revisions.

Automatic rotation uses the normal data refresh cadence, not a separate fast slideshow timer. Legacy artwork-only selection files default to rotating without changing their selected artwork immediately.
