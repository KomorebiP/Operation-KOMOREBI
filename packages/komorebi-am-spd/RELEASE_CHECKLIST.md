# AM-SPD 1.0.0 release checklist

Check an item only after its current-release evidence is available. Archived 0.3.0 verification is provenance, not a substitute for testing the 1.0.0 artifact. Preparing this checklist does not confirm repository visibility, publishing, or hosted CI results.

## Local release validation

- [x] Package, CLI, citation, and current documentation report version 1.0.0.
- [x] License text and package/citation metadata agree with the selected public-use license.
- [x] All package tests pass, including schema-1 compatibility, normalized input handling, archive validation, continuation, parameter caps, tiling, tuning, and batch restart behavior.
- [x] Ruff checks and source compilation pass for public code, tests, and examples.
- [x] Full installed-package integration verification passes.
- [x] The four bundled paper cases replay with the required reference invariants.
- [x] The preserved research checksum ledger passes with no archival source changes.
- [x] Historical core, SPD, intermediate, and final suites pass, or an explicitly documented failure remains open.
- [x] Wheel and source distribution build successfully with correct resources and license metadata.
- [x] The wheel passes verification outside the source checkout.
- [x] A clean source-distribution installation passes extracted tests and full package verification.
- [x] Offline instructions and wheelhouse preparation have been checked; any dependency or platform gaps are recorded.
- [x] Standalone and monorepo workflow templates have been checked for syntax and package paths.
- [x] Final source bundle and distribution checksums are recorded.

## Current-release evidence

| Check | Evidence | Result |
|---|---|---|
| Python/environment | `validation/source-release-final/summary.json` | Linux CPython 3.12.14; exact dependency versions recorded |
| Package tests | `validation/source-release-final/pytest.xml` | 240 passed |
| Ruff and compilation | `validation/source-release-final/*` | Passed; frozen historical modules remain byte-preserved and excluded from lint |
| Full package verification | `validation/source-release-final/integration.json` | 20 checks passed |
| Paper replay | `validation/wheel-release/paper/paper_reproduction_summary.json` | All four required comparisons passed; optional historical diagnostics retained |
| Historical source integrity | `validation/historical/historical_summary.json` | 292 files unchanged; core, SPD, multiscale and final suites passed |
| Wheel installation | `validation/wheel-release/summary.json` | Clean offline install; full verification and strict four-case replay passed outside checkout |
| Source distribution | `validation/sdist-release/` | Passed: clean offline install, 240 extracted tests, 20 integration checks and unchanged archive hash |
| Offline installation | `validation/offline-linux/summary.json`, `validation/windows_offline_preflight.json` | Linux execution passed; 19 Windows wheels/31 dependency edges passed metadata checks; Windows native execution is delegated to gated hosted release workflow |
| Script/workflow validation | Workflows use pinned actions; Bash and YAML checked | PowerShell reviewed, not executed on this host |
| Deliverable integrity | `RELEASE_SHA256SUMS.txt` and release audit | Frozen distribution hashes recorded; source import records Git blob hashes |

## Remote publication

- [ ] Confirm the actual destination and access for `KomorebiP/Operation-KOMOREBI`, including the intended `packages/komorebi-am-spd` path.
- [ ] Review and push the stable release branch.
- [ ] Merge the reviewed changes and confirm hosted GitHub Actions pass on the declared platforms.
- [ ] Create and push `am-spd-v1.0.0` after review.
- [ ] Download and retest the hosted build artifact.
- [ ] Publish a GitHub Release or package-index release only when that destination is intended.

Remote steps remain unfulfilled until their actual repository/run/release evidence is recorded.
