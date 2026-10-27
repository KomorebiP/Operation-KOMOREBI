# Changelog

## [2.1.0] - 2026-08-18

### Added

- Stable `komorebi_pr_lasm` public import facade.
- Cross-platform GitHub Actions matrix for Python 3.12 and 3.13.
- Tag-triggered release automation and a release audit ledger.
- Isolated wheel build and installation certificate.
- GitHub issue forms, pull-request template, Dependabot configuration,
  citation metadata, security policy, contribution policy, and release guide.
- Minimal exact-reconstruction and adaptive-refinement examples.
- Explicit optional `local_suite` test layer.

### Changed

- Reorganized release-bundle documentation into a navigable repository.
- Separated immutable benchmark references from generated runtime outputs.
- Consolidated Windows commands under `pr-lasm.ps1`.
- Moved historical PowerShell wrappers and 2.0.0 handoff records under
  `scripts/legacy` and `docs/reference`.

### Security and distribution

- Removed downloaded ARC environment sources from the public repository.
- Added an ignored `environment_files/` installation location and a separate
  optional local-fixtures archive.

## [2.0.0] - 2026-07-29

Original complete PR-LASM handoff with exact multi-atlas reconstruction,
typed operator posterior, active planning, controlled benchmarks, paper,
wheel, and a private 25-environment local suite.
