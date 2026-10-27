# Current local Lean status

**SF-LEAN-B01: 29 new named declarations checked, plus the unchanged 39-declaration finite core.** The sum of 68 names is not a count of independent discoveries or a claim of full formalization of the monograph.

The new module proves recurrence existence and uniqueness, strict coefficient positivity, a geometric majorant, local complex absolute convergence, an explicit local tail bound, the exceptional-locus factorization, and generic recovery from the six coefficients through degree seven. It also checks a boundary collision and the worked rational example.

See `formalization/Block01/REPORT.md` for mathematics and limitations, `CLAIM_MAP.json` for exact status, and `evidence/` for current execution receipts. Only propext, Classical.choice and Quot.sound appear in the theorem axiom reports. All five negative controls fail as expected. Kernel replay uses the same Lean kernel against cached imported dependencies, not a separate external verifier.

The locally restored compiler is Lean 4.34.0-rc2 with Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. This run used the five compact stored parts. Their combined archive digest is f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7. The prior seven-part bundle is an alternative packaging of the same pinned runtime.

The analytic-solution-to-recurrence bridge, holomorphic differentiation, entire continuation, global Perron growth law and full component-rescaling equivalence remain formalization obligations. The three books are unchanged and their evidence pages retain the earlier snapshot. This file and the block companion report the newer scope.

```bash
python tools/verify_coupled_block.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --work /tmp/sf-block01
```

The work directory must be outside the pristine release. No downloads are used. On Windows, use the Linux kit in WSL; native Windows execution has not been tested. The previous runtime/core-only checker remains available as `tools/check_local_lean.py`.
