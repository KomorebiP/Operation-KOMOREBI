# SF-DISCOVERY-100 finite release verification

All ten frozen scripts passed in **40.35 seconds** under the computation-audit runner. The schema-2 manifest validator passed against the current project. All **25 pinned input files** and **22 byte-identical snapshot files** remained unchanged. All **57 declared result files** were present and hashed; the manifest records 59 hashed outputs including its two logs.

The suite executed **19,871 exact assertion statements**: 19,331 principal checks plus 540 inverse-reconstruction helper checks. It also executed **5,576 numerical assertion statements**. The 61 finite iteration guards are recorded separately.

| Check | Principal exact | Extra exact helpers | Numerical statements |
|---|---:|---:|---:|
| nonlinear_dilation | 1,218 | 0 | 0 |
| asymmetric_dilation | 1,811 | 0 | 0 |
| complex_depth | 301 | 0 | 3 |
| orbit_zeta | 138 | 0 | 0 |
| arithmetic_polynomials | 0 | 0 | 2,273 |
| dilation_type | 6,091 | 0 | 0 |
| arithmetic_inverse | 304 | 540 | 88 |
| multi_prime_sieve | 1,019 | 0 | 3,182 |
| spectral_continuation | 411 | 0 | 30 |
| family_lab_checks | 8,038 | 0 | 0 |
| **Total** | **19,331** | **540** | **5,576** |

Each numerical assertion statement counts once, including grouped positivity and maximum-residual comparisons. Sieve orthogonality and recurrence subcounts are included in its total. Decimal displays and inverse rank tables do not count as assertions. The 540 exact helpers check 180 recovered atoms three times each and are counted once in the actual exact total.

Limits were 600 seconds wall time, 2 GiB address space, 300 CPU seconds, one core and cooperative one-thread settings. CPU and memory caps apply per process, not as a combined budget across descendants. Python 3.12.14 and mpmath 1.3.0 were recorded. The external mpmath tree contains 87 hashed Python source files and remained unchanged.

The full reports preserve prior author histories, including the arithmetic-polynomial absolute-residual failure and the corrected relative-residual criterion. The current aggregate run had no failures. Ordinary high-precision comparisons do not provide interval certificates, and bounded checks do not prove the universal analytic theorems or historical priority. The monograph and figure builders are outside this computational input set.

Artifacts:

- Contract and finite bounds: `evidence/release_contract.json`.
- Reproduction driver and instructions: `checks/run_release.py`, `checks/RELEASE_CHECKS.md`.
- Manifest: `evidence/release-run-001/manifest.json`.
- Full per-script reports: `evidence/release-run-001/reports/`.
- Source snapshots and original-location outputs: `evidence/release-run-001/snapshot/`.
- Per-script stdout and stderr: `evidence/release-run-001/logs/`.
- Current hashes: `evidence/release-run-001/input_hashes.json`.
- Validator result: `evidence/release-run-001/validation.json`.
- Machine-readable release summary: `evidence/release_summary.json`.
