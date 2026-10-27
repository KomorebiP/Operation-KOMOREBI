# PRSC VIII — Checked Third Block v0.3.0

**Author: Komorebi P.**

## Status

**40/56 named manuscript-proved items checked. 16 remain. Four classical inputs are tracked separately.**

This cumulative release contains **197 theorem declarations across 18 modules**: 68 new declarations, 110 earlier Paper VIII declarations, and 19 unchanged reused Paper VII declarations. Twelve separately audited constructions are not included in the theorem count. All 18 modules passed a fresh cumulative Lean run. Both deliberately invalid controls were rejected, and the verifier's 17 regression tests passed.

## New work

| Area | Source items | New declarations |
|---|---|---:|
| Actual product-chain errors, additive recompression errors, mixed-precision propagation | 5.8, 5.9, 8.3 | 13 |
| Explicit variable-rank product factors and actual correction-rank bound | 5.2 | 5 |
| Exact packet Krylov decomposition and approximate-power distance bound | 7.2, 7.3 | 11 |
| Min-plus core, quantized tree compiler, discrete precision, cached arrays and work bound | 8.7, 9.8, 9.9 | 39 |

`notes/COVERAGE_LEDGER.md` and `verification/coverage_ledger.json` give every manuscript item, exact formal scope, and named Lean witnesses. `notes/Paper_VIII_Third_Lean_Block_Supplement.pdf` explains the mathematics. The original manuscript and the previous supplements remain unchanged. The earlier positive-budget amendment to item 8.4 remains in force.

## Reproduction

Use the existing Linux x86-64/WSL portable **Lean 4.34.0-rc2** kit, with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The runtime is not duplicated in this source ZIP.

From this release directory:

```bash
python3 scripts/verify_integrity.py
python3 scripts/test_verifier.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/recheck --timeout 240
python3 scripts/run_budget_examples.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --build verification/recheck/build --out verification/recheck_budget_execution
python3 scripts/run_compiler_examples.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --build verification/recheck/build --out verification/recheck_compiler_execution
```

In a host with short command limits, invoke the verifier repeatedly with `--max-checks 2 --resume` and the same output directory. An incomplete checkpoint is not a successful verification. The launcher uses one Lean worker and the pinned project environment, with warnings treated as errors. It does not impose a RAM cap or weaken proof checking.

## Evidence

`verification/final/SUMMARY.json` records the fresh cumulative compilation, source hashes, dependency hashes, theorem and construction audits, and both negative controls.

`verification/budget_execution/SUMMARY.json` records 384 finite tree instances, 4,992 exact-weight comparisons and 4,992 budget comparisons against 19,152 independently enumerated legal cuts. It also records 288 discrete-precision instances, 3,744 exact-weight comparisons and 3,744 budget comparisons against 1,453 independently enumerated assignments. There are 1,440 additional comparisons to the functional tree specification and five explicit boundary regressions. Tests use exact rational costs and are not additional theorem declarations.

`verification/execution/SUMMARY.json` records a fresh rerun of the preceding block's 600 exact-rational compiler cases, 85,320 exhaustively enumerated pruning scores, and 600 cached-update comparisons.

**11 of 18 captured development checks failed before correction.** Their source snapshots and diagnostics remain in `verification/development/`, separate from the successful cumulative run. Historical evidence and earlier verifiers are retained under `verification/prior/`.

## Boundaries

The quantized compiler optimizes a finite tree with additive declared costs and integer error weights. The implementation returns an optimum cost or `none`, with formal proofs of attainment and exact infeasibility. It does not yet return backtracking metadata for a selected cut or precision assignment. Universal packet discovery and optimal CUDA scheduling are not claimed.

The array-backed implementation is proved equal to the mathematical recurrence. Its tabulation work has a separately declared unit-cost model of table cells and min-plus candidate trials. The bound is polynomial in the numeric budget, not its binary input length. Exact-arithmetic bit complexity, compiler overhead, allocation overhead, memory traffic, and GPU timing are outside that model. A root minimum scan adds a linear pass. This is not a verified hardware operation count.

The error theorems are deterministic operator-norm certificates for stated local residuals. They do not prove a floating-point kernel's rounding model. Product-chain proofs use a norm-one identity, covering operators on nonzero normed spaces. The separate power-difference estimate does not need that restriction. The exact Krylov result proves inclusion in a direct sum of local spaces, not equality with that sum.

The third block did not rerun the original 37,392-check CPU numerical suite or any GPU measurements, rebuild Papers I–VII in full, or independently recheck imported Mathlib proofs. Historical benchmark records remain historical evidence.

## Preservation

The original manuscript PDF, TeX, bibliography, register, and source package, both earlier supplements and their TeX sources, and all 11 upstream Lean source modules match v0.2.0 byte for byte. See `verification/preservation.json`.

The distributed manifest verifies file integrity, not external authorship or a cryptographic signature of truth.
