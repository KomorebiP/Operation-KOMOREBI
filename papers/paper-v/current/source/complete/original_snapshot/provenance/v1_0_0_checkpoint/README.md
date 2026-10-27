# Projector-Resolved Seed Calculus V, v1.0.0

Author: Komorebi P.

**The corrected, scope-explicit formalization contract is complete: all 20 theorem-like results have checked counterparts. The pinned combined build and axiom audit pass for 225 theorem targets in 23 modules and all 827 project-namespace declarations.**

All 133 targets from v0.3.0 remain included. There are 92 added targets, of which 11 adapt the already-proved Paper IV cyclic-series foundation. Supporting Lean declarations are not additional manuscript theorems.

## Read first

- `manuscript/Paper_V_Correction_Supplement.pdf`: the current five-page correction and completion supplement. Read it with the preserved original 31-page manuscript.
- `THEOREM_LEDGER.md`: exact scope of all 20 results.
- `MANUSCRIPT_TARGET_MAP.md`: principal Lean declarations for each result.
- `CUMULATIVE_COUNTS.md`: the Papers I–V proof census, including known-duplicate removal and evidence limits.
- `verification/verification_status.json`: the actual full verification result (`LEAN_CHECKS_PASS`, exit 0, `lean_kernel_checked: true`).

## What was completed

The new sources close the original-signal Haar energy identity, all finite-depth Haar packet energy and true-adjoint reconstruction, measurable-mask perturbations, literal finite antichain sums and operator synthesis, attained finite-objective gaps, stable selectors, a cached optimizer with a specified linear operation bound, the formal-series cyclic product/power formula, the exponential cyclic action on the projective line, convergent channel z-transforms, and concrete FIR filter-bank representation and perfect reconstruction.

## Scope and corrections

Completion is relative to the statements and corrections recorded in the supplement and scope contract. The PDF-to-Lean comparison is manually reviewed; it is not itself a kernel-checked document equivalence.

- The time-domain FIR statement covers every bilateral sequence. Numerical z-transform identities require nonzero z and summable weighted input channel series.
- The concrete filter-bank operator theorem uses finite Laurent/FIR filters. The generic scalar-matrix criterion is also checked; no convergence for arbitrary infinite filters is inferred.
- A channel delay d is N*d original samples.
- Tree selection includes the singleton case and stops on ties. The linear complexity statement counts node visits, comparisons and cached-value additions, with node costs supplied. It does not count arbitrary cost-oracle evaluation or Lean runtime.
- Measurable-mask bounds use extended Lp norms, with finite-measure hypotheses giving the printed finite-valued interpretation. Pointwise and essential supremum statements are distinguished.
- The Smith action is projective, so zero and infinity are treated correctly. Finite-chart identities retain their denominator conditions.
- The cyclic product/power result is a formal-series theorem. Analytic evaluations retain their ordinary convergence requirements.

The two edge-recovery conjectures remain conjectures. Original numerical examples, the manuscript's reported 33-test companion suite, historical priority and publication readiness are outside this formalization contract. The original manuscript is preserved, with this supplement supplying the corrections; the main PDF has not been silently rewritten.

## Checks executed

| Gate | Result |
|---|---|
| Combined pinned Lean build | PASS, 3,296 jobs in the dependency graph |
| 225 direct theorem targets plus all 827 project-namespace declarations | PASS |
| Standard permitted axioms | propext, Classical.choice, Quot.sound only |
| Nine pinned dependency revisions and clean tracked sources | PASS |
| Source integrity, declaration inventory, imports and target coverage | PASS |
| 20-row scope contract and registered principal targets | PASS |
| Independent exact mathematical suites | 20 tests; 305,933 counted assertions |
| Verifier positive/negative controls | 16 tests |
| Optimized-Python static verification | PASS |

The dependency graph is cached; a job count is not a theorem count. The 16 static control tests do not simulate a successful compiler. The separate full verification report records the actual compiler and audit pass. Earlier real-compiler positive and negative controls are retained under verification/runtime.

## Reproduce

Install the toolchain named in formalization/lean/lean-toolchain. From formalization/lean, prepare dependencies with `lake exe cache get`. From the package root, run:

```text
python3 verification/verify.py
```

`VERIFY.ps1` and `bash VERIFY.sh` are wrappers. `python3 -O verification/verify.py --static-only` runs source/scope checks and exact tests without making a kernel claim. Lean is 4.34.0-rc2 and mathlib is pinned to aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

The package excludes toolchain binaries and build caches. First setup requires network access to fetch the pinned dependencies. The environment-specific application-path adapter used here is disclosed, with source, in verification/runtime/RUNTIME.md; normal installations do not need it. Source/configuration hashes and checksum files provide unsigned integrity evidence, not proof checking.

Prior blocks and superseded reports are retained under provenance. Their former incomplete/missing-toolchain statuses are historical.
