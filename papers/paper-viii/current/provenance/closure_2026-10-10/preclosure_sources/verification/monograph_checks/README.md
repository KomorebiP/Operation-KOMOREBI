# Paper VIII current computation review

All completed fresh gates pass within their stated finite contracts. The raw
scientific source trees retain 1,062 files and match both original ZIP payloads.
The formal compiler result remains inherited from September 6. No Lean, Lake,
pytest session, CUDA implementation or device timing was executed in this pass.

| Gate | Fresh result |
|---|---|
| Raw source / ZIP preservation | 930 complete and 132 strengthened files match; 928 / 723 / 131 overlapping archived manifest entries match |
| Inherited formal record comparison | 40 modules, 392 theorem declarations, 66 construction audits and 458 audited names match source, inventory, dependency and saved log bytes |
| Verifier software | 43 actual unittest methods pass |
| Archival Python tests | 23 baseline + 11 strengthened unchanged functions pass by direct invocation; 18 historical PDF/PNG chart pairs regenerated |
| Original deterministic suite | 37,392 assertions in nine groups pass; 778 corpus and 26 source checks are metadata |
| Structured mirror | 180 Kronecker, 120 tensor, 96 Walsh, 240 Toeplitz, 600 clipped cases; 1,800 infeasible budgets rejected; 96 complex Fourier cases |
| Fifth mirror | 820 band, 200 staged DAG, 125 exhaustive schedule, 60 inverse, 50 Schur, 72 exact noncoordinate, 64 complex discovery, 120 Jacobi cases |
| Sixth mirror | 182 factor pairs, 638 truncations, 3,190 sampled competitors; nine invalid inputs and two assumption-removal controls |
| Original SymPy worked models | Fresh 190 exact positive assertions and 11 shortcut controls |
| Independent final portable guide | 208 integer/rational/Gaussian-rational assertions and 15 controls |
| Original Python vector generator | 30 plates regenerated; 28 exact and two documented header-position repairs |
| New traditional finite models | 74 independent rational assertions and five false controls |
| Historical corpus arithmetic | 264 stored ratios and 146 logical-throughput fields recalculated across 154 stored rows |

The tests and examples overlap. Their counts are not added as unique results,
theorems, or discoveries. `COMPUTATIONAL_REVIEW.json` links each current bounded
manifest and hashes its scientific result. `ENVIRONMENT_CURRENT.json` records
actual available dependency versions.

## What failed

Pytest import raised `ModuleNotFoundError`. Offline dependency resolution also
failed because there was no cached pytest package. Neither failure ran a
scientific test session. The unchanged 34 source test functions were then
executed directly with the required real temporary `Path` fixture. This is
reported as direct execution, never as pytest. No mathematical assertion
failed in the completed gates. No package was installed.

Final current-root manifest validation also detected that the navigation helper
`source/update_crosswalk.py` changed after the two early guide runs. The math
code did not change. The original SymPy and vector gates were rerun against
the frozen final helper; the current review uses those new manifests. The
earlier records remain as superseded historical executions and are not counted
as current validated evidence. This stale-pin catch was a provenance check,
not a mathematical failure.

## Arithmetic and finite ranges

The structured and graph mirrors use exact `Fraction` rational calculations.
The Fourier, complex discovery, whitening and recompression mirrors use NumPy
binary64/complex128. The original suite keeps its original `allclose` and
`isclose` tolerances, including default relative tolerances where the source
uses them. A pass is not a uniform machine-epsilon certificate.

Fourier dimensions are 1 through 24, four complex samples each, seed 20260906,
absolute threshold 1e-10. The maximum application residual was
2.0388725187405107e-13. The fifth mirror uses seed 202609065 with band packet
counts at most 40, DAG vertices at most seven, inverse packets at most six,
noncoordinate dimensions at most six, complex discovery and Jacobi dimensions
at most eight. Jacobi coupling values are 0, .05, .2, .6 and .95.

The sixth mirror uses seed 60606 and dimensions 0 through 10. It includes empty,
zero, rectangular, rank-deficient and repeated-singular-value factors, with
retained ranks 0, 1, near full, full and above full. The column-space threshold
is 1e-11 times max(1, largest singular value), the output rank threshold is
1e-9 times max(1, Frobenius norm), and normalized comparison tolerance is 2e-9.
Its maximum compact reconstruction residual is 1.2730256604370022e-15;
spectral and Frobenius tail residuals are 3.556141234775559e-15 and
3.660976558279377e-15. This is a finite numerical mirror, not exact rank
certification or an independent implementation of a numerical SVD library.

The new independent traditional model checker uses rational Gaussian
elimination for a 4 by 4 BDLR inverse, three complete prunings of a five-node
tree, seven sampled Lagrange values plus an exact empty supporting interval,
tree budgets 0 through 6, and all eight precision assignments with every prefix
table and budgets 0 through 8. The output is (5, 6, 15, 20), the Woodbury core
is 3/2, and the exact budget-three precision optimum is AFF with cost 6 and
error 3. These costs and errors are declared illustrative models.

## Evidence boundaries

The 56 completed formal coverage records and four separate classical inputs
remain the inherited contract. The saved accepted compiler run completed
2026-09-06T22:38:55.838919+00:00. The source/log check is fresh; compilation and
kernel checking are not. The two false/admitted-proof controls were compared
with saved recorded rejection logs, not recompiled. The reused Paper VII
foundation is byte-identical at SHA-256
92e49bb023877ed1f1c2bb34968aa81ee7724fa3a8e1801a831cfc70f1de3595.

The original SymPy models now genuinely run with SymPy 1.14.0. The independent
standard-library portable models remain a second exact implementation of
overlapping displayed examples. Both preserve their original code. The vector
generation reproduces all 30 formulas and math labels. Two authored header
locations move upward to avoid title crowding: complex_core from (0,3) to
(0,3.4), and quantization from (0,2.7) to (0,3.2). The original generated files
and current authored plate hashes are retained separately.

The 154-row historical corpus labels itself measured. This audit recalculates
the arithmetic in 264 recorded ratios and 146 logical-throughput fields using
actual stored fields and unique same-case recorded dense baseline rows. It
does not recover or authenticate same-device outputs or correctness-reference
provenance. 130 ratio fields cross recorded timing scopes. Matching metadata
labels do not establish matching precision or hardware execution contracts.
Generated historical charts are replots, not measurements.

The retrieved old outer manifest has 1,549 entries, zero missing files, ten
preexisting hash/size mismatches, and 13 unindexed publication additions from
later formatting. `RETRIEVED_INTEGRITY.json` lists them. The protected original
source trees and ZIPs match exactly. Root-level metadata reconciliation handles
outdated PDF page counts and hashes separately. No source mathematics was
rewritten to force a test pass.

The legacy prototype reports stored block keys, which may include zero blocks;
the mathematics uses exact nonzero projector support. Thresholded numerical
support is a third representation. The older reduced-QR prototype also does
not certify exact actual-rank compact ranges. Fresh finite passes do not erase
these representation boundaries.

## Reproduction

Run from the extracted edition root. Each run requires a new output suffix:

```bash
python verification/monograph_checks/run_current_checks.py --suffix NEW_RUN
python verification/monograph_checks/run_current_checks.py --modes portable vectors --suffix NEW_GUIDE_RUN
```

The current exact auxiliary checks can also be run to new output files:

```bash
python verification/monograph_checks/check_corpus_arithmetic.py --corpus source/strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package/verification/benchmark_results_sanitized.json --out NEW_CORPUS_RESULT.json
python verification/monograph_checks/check_traditional_models.py --data editable/traditional/monograph_data/exact_examples.json --out NEW_MODEL_RESULT.json
```

All accepted current records use the supplied version2 bounded runner. Every
manifest records actual argv, UTC start, runtime, exit code, declared inputs
before and after execution, scientific result hashes, logs and resource caps.
Validate a record against the current extracted root with:

```bash
python verification/checks/validate_manifest.py verification/monograph_checks/run_original_20261009/manifest.json --root .
```

The caps are 240 seconds wall time, 210 CPU seconds per process, two GiB address
space, one CPU affinity core, four MiB logs and cooperative one-thread numerical
library settings. The cooperative thread request is not proof that every
library honors it. This archive tree has no project Git commit. The isolated
replays copy original scientific files, verify copy hashes, execute unchanged
code there and confirm that delivered source bytes remain unchanged.
