# Public release preparation

Branch: `chore/public-release`. Updated: 2026-10-28.

## Acceptance criteria

- Preserve the artwork, source, tests, and intended hardware references.
- Commit the reference-directory reorganization and repair its consumers.
- No credentials, environment files, private keys, or live usage state enter the
  release tree or reachable branch history. Keep machine-only caches and previews
  outside the current release tree.
- Separate public instructions from the owner's local collector integration;
  avoid shipping personal machine paths in portable artifacts.
- Include suitable licensing, third-party attribution, and repeatable checks.
- Finish with passing checks, a reviewed secret scan, and a clean committed branch.
- Prepare locally; no public repository creation or upload is implied by preparation.

## Tasks

- [x] Inventory tracked, untracked, and ignored files and scan branch history.
- [x] Clean metadata, fix reference paths, and add public setup/licensing/attribution.
- [x] Run tests, asset validation, link checks, and secret scans.
- [x] Commit the prepared release and record any publication limitations.

## Initial findings

- 140 tracked files. Runtime code matches HEAD; eleven vendor reference files moved
  into `pimoroni-inky-impression/` are byte-identical to their old committed versions.
- `AGENTS.md` and its `CLAUDE.md` pointer are untracked project instructions.
- Four README links and the integrated prompt reference paths still use old locations.
- Developer-local preview HTML and provenance JSON contain absolute home-directory paths.
- No Git remote is configured. Existing Mac sync still depends on an external collector.

## Completed changes

- Preserved all eleven reference files as exact renames and repaired README and
  generation-manifest references. Kept all artwork, fonts, source, and tests.
- Added the project agent instructions, MIT code license, third-party rights notices,
  and a validated empty usage snapshot example.
- Untracked only the two machine-specific generated previews; their local files
  remain available and their builders still regenerate them. Added explicit ignore
  rules for previews, tool cache, key files, and common credential JSON names.
- Replaced absolute home paths in provenance with committed relative master paths
  and retained generation artifact identifiers and exact prompts.
- Required an explicit external collector path and documented its contract. The
  installed owner's launch job already supplies that option, so it remains compatible.

## Validation

- Gitleaks 8.30.1, default rules, fully redacted output, no custom suppressions:
  all 21 reachable local commits/checkpoints, 48.23 MB, zero findings.
- Exact staged export: 144 files; Gitleaks scanned 10.06 MB of text/decoded content,
  zero findings. Both PDF text extractions separately scanned with zero findings;
  their extracted text and metadata have no home/private-network patterns.
- 30 tests pass. Ruff lint/format, shell syntax, and both CLI help paths pass.
- All 77 raster files verify, all six fonts load, JSON/TOML parse, indexed proofs
  use slots 0–6, all local Markdown and provenance references resolve, and the
  current tracked text/PNG metadata contain no absolute home-directory paths.
- Local scan reports remain in ignored `state/audit/`, outside the release.

## Publication notes

- No remote is configured and nothing was uploaded or made public.
- Historical commits retain non-secret local paths and the former generated previews;
  history was scanned but not rewritten. Git author identity remains unchanged.
- Manufacturer references retain third-party rights; this preparation does not
  establish a redistribution license for those original files. See THIRD_PARTY.md.
- The archived manufacturer product PDF requires Poppler cross-reference recovery
  during extraction; the original file was preserved and its text extracted successfully.
