# Development failure ledger

All rejected Lean attempts are retained in development/ as logs, JSON records, and source snapshots. They are not proof evidence. The accepted active sources are in src/.

28 logged development compiler invocations: 11 passed, 17 rejected. Rejections involved unused-section/simp lint, function coercion unfolding, a missing explicit matrix completeness instance, finite index normalization, and dependent-module imports attempted before compilation succeeded.

| Rejected record | Exit code |
|---|---:|
| EffectiveMatrixControls_1789241901782398754.json | 1 |
| EffectiveMatrixControls_1789241942259062155.json | 1 |
| EffectiveMatrixControls_1789242017463091546.json | 1 |
| EffectiveMatrixControls_1789242063032312526.json | 1 |
| EffectiveMatrixRoot_1789241740245145865.json | 1 |
| EffectiveMatrixRoot_1789241881666197432.json | 1 |
| FiniteMatrixCriterion_1789241956776265438.json | 1 |
| MatrixInverseCertificate_1789241683418703896.json | 1 |
| MatrixInverseCertificate_1789241860067354280.json | 1 |
| MatrixInverseCertificate_1789241971382202327.json | 1 |
| NCPowerEstimates_1789241386811633323.json | 1 |
| NCPowerLocalImage_1789241444563005609.json | 1 |
| NCPowerLocalImage_1789241463365696762.json | 1 |
| NCPowerLocalImage_1789241484203378327.json | 1 |
| NCPowerLocalImage_1789241537601833141.json | 1 |
| PadicMatrixNorm_1789241514462695807.json | 1 |
| PadicMatrixNorm_1789241582784615682.json | 1 |

Additional non-proof development failures: an exploratory SymPy import failed because that package was not installed; the implemented computations use only Python standard-library exact fractions. The first computation-runner invocation used a contract path relative to the wrong directory and returned code 2 before execution. The corrected invocation completed and its manifest validates.

The final clean replay passed all seven modules and the axiom audit. A separate extracted-archive replay is recorded outside the archive after extraction.
