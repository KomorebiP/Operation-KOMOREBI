# Bounded performance and verification cost

The cache reduces work compared with recomputing every output packet. In this
seven-case test it does not establish an overall advantage over an efficient full
Richardson baseline. This is a negative result for a broad speedup claim, not a
failure of the certified mathematical algorithm.

All modes use exact Fraction arithmetic, the same zero-skipping matrix backend,
exact-score stopping at epsilon^2/4, common requested epsilon/delta, a final
rounded certificate, and parameter output. Cached and recomputed selective runs
return identical candidates. The full baseline maintains its complete residual
by recurrence and does not waste time computing packet scores or scanning labels.

One warmup precedes five repetitions, with rotating method order. Dimensions are
at most eight. Cases include concentrated residuals, dense residuals, a singular
rotated prior, rectangular observations and sigma=1/10. These are controlled
reference measurements, not benchmarks against optimized BLAS, GPU or GP packages.

Producer time includes setup, iteration, final certificate calculation and output
evaluation. Times in the next table are milliseconds and exclude export/Lean.

| Case | Cached / full updates | Cached ms | Recomputed ms | Full ms | Iteration speed ratio, recomputed/cached |
|---|---:|---:|---:|---:|---:|
| coordinate | 6 / 3 | 2.38 | 2.46 | 2.33 | 1.94× |
| rotated | 4 / 4 | 4.38 | 4.45 | 4.28 | 2.16× |
| sparse4 | 8 / 4 | 13.84 | 14.52 | 13.79 | 2.51× |
| dense4 | 18 / 5 | 16.34 | 17.96 | 16.34 | 3.11× |
| sparse8 | 16 / 8 | 171.98 | 174.30 | 169.87 | 4.62× |
| dense8 | 67 / 9 | 200.69 | 235.15 | 195.44 | 5.61× |
| conditioned4 | 36 / 10 | 19.16 | 21.36 | 17.46 | 3.08× |

## Export and Lean checking

Every method/case also exported an explicit final-candidate certificate. All 21
exports compiled in separate pinned Lean processes during the clean build. The
posterior tolerance is therefore checked for every benchmark output gain. These
static certificates do not certify the Python timing trace or numeric output arrays;
array arithmetic is timed here, tested independently, and covered by the universal
output theorem and two separately checked full-program examples.

| Case / mode | Producer ms | Export ms | Lean check seconds | Combined seconds |
|---|---:|---:|---:|---:|
| coordinate / cached | 2.38 | 0.53 | 3.173 | 3.176 |
| coordinate / recompute | 2.46 | 0.46 | 3.174 | 3.177 |
| coordinate / full | 2.33 | 0.41 | 3.893 | 3.896 |
| rotated / cached | 4.38 | 0.77 | 3.428 | 3.433 |
| rotated / recompute | 4.45 | 0.83 | 3.125 | 3.130 |
| rotated / full | 4.28 | 0.78 | 3.526 | 3.531 |
| sparse4 / cached | 13.84 | 3.37 | 4.740 | 4.757 |
| sparse4 / recompute | 14.52 | 3.35 | 3.878 | 3.896 |
| sparse4 / full | 13.79 | 3.39 | 4.359 | 4.376 |
| dense4 / cached | 16.34 | 3.59 | 4.130 | 4.150 |
| dense4 / recompute | 17.96 | 3.67 | 3.940 | 3.962 |
| dense4 / full | 16.34 | 3.52 | 4.490 | 4.510 |
| sparse8 / cached | 171.98 | 62.92 | 32.367 | 32.602 |
| sparse8 / recompute | 174.30 | 64.74 | 35.311 | 35.550 |
| sparse8 / full | 169.87 | 62.84 | 35.896 | 36.129 |
| dense8 / cached | 200.69 | 64.60 | 33.996 | 34.261 |
| dense8 / recompute | 235.15 | 71.84 | 35.478 | 35.785 |
| dense8 / full | 195.44 | 72.49 | 34.474 | 34.742 |
| conditioned4 / cached | 19.16 | 3.84 | 4.300 | 4.323 |
| conditioned4 / recompute | 21.36 | 3.60 | 4.904 | 4.929 |
| conditioned4 / full | 17.46 | 5.06 | 4.315 | 4.338 |

Per-instance checks include a fresh Lean process, import, elaboration and kernel
checking with common dependencies already compiled. The one-time clean dependency
build is recorded separately in FINAL_VERIFICATION_RECEIPT.json. A single check
measurement per export is insufficient to rank small differences reliably. The
combined column is median producer time plus one export/check measurement.

## What changed and what did not

Cached execution forms the full residual once at initialization, refreshes one
packet energy per update, and updates total energy by a difference. Selection still
scans stored scalar energies. The final rounded evaluator and independent exported
candidate checker still examine the complete model/residual obligations. The cache
adds storage proportional to the number of represented packet matrices.

The counters in the raw report cover iterative scalar matrix kernels and selection.
They exclude preprocessing, final verification arithmetic, output arithmetic,
integer bit growth and allocation cost. No formal bit-complexity theorem is claimed.

## Decision

The exact cached branch is suitable for the declared checked reference release.
These measurements do not justify making a new rounded selective solver a release
gate, nor presenting the method as a fast practical alternative to established GP
solvers. Further performance work should first address final certification and
certificate-checking cost, then test substantially larger structured problems.
The general rounded-cache proof remains open; its naive center-only variant has
a checked counterexample.
