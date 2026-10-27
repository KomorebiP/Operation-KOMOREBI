# PRSC VIII — Checked Fourth Block v0.4.0

**Author: Komorebi P.**

## Status

**46 of 56 named manuscript-proved items checked. Ten remain. Four classical inputs are tracked separately.**

This cumulative release contains **247 theorem declarations across 23 modules**: 50 new declarations, 178 earlier Paper VIII declarations, and 19 unchanged reused Paper VII declarations. Twenty-two separately audited constructions are not included in the theorem count. Every module passed a fresh cumulative Lean run. Both deliberately invalid controls were rejected, and all 17 verifier regression tests passed.

## New work

| Module | Source items | New declarations |
|---|---|---:|
| CirculantFourier | 4.3: actual normalized Fourier matrix, unitarity, convolution, circulant diagonalization and application | 13 |
| ToeplitzEmbedding | 4.4: actual doubled circulant, modular wrap, padding, and cropped action | 6 |
| StructuredTensor | 4.5, 4.6: column-major Kronecker action, arbitrary tensor contractions, modeled arithmetic and storage | 7 |
| WalshTransform | 4.7: actual recursively constructed matrices, butterfly action, orthogonality and arithmetic count | 7 |
| ClippedPrecision | 8.5: existence, global optimality, unique minimizing vector and interior multiplier uniqueness | 17 |

Supporting lemmas are included in these declaration counts. This is not a claim of 50 new manuscript results or novel classical theorems.

The authoritative coverage map is `verification/coverage_ledger.json`, with a readable version in `notes/COVERAGE_LEDGER.md`. Exact assumptions, conventions and new proof explanations appear in `notes/Paper_VIII_Fourth_Lean_Block_Supplement.pdf`. All three earlier supplements and the original manuscript are preserved.

## Reproduction

Use the existing Linux x86-64/WSL portable **Lean 4.34.0-rc2** kit, with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The runtime is supplied separately and is not duplicated in this source ZIP.

From this release directory:

```bash
python3 scripts/verify_integrity.py
python3 scripts/test_verifier.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/recheck --timeout 240
python3 scripts/run_structured_regressions.py
```

The independent regression script needs NumPy for its explicitly floating-point Fourier checks. Its rational checks use Python's standard-library `Fraction`. It writes `verification/fourth_examples/SUMMARY.json`, replacing the packaged example report on rerun. Archive the existing report first when preserving the original run matters.

In a host with short command limits, the Lean verifier can be resumed with `--max-checks 2 --resume` and the same output directory. An incomplete checkpoint is not a successful verification. The launcher uses one Lean worker and the pinned project environment, with warnings treated as errors. It does not impose a RAM cap or weaken proof checking. Compiled interfaces are regenerated from sources; they are not distributed in this package.

The earlier exact-rational compiler execution scripts remain available. They were not rerun in this fourth block. To use them after the cumulative rebuild, see their `--help` output and point `--build` to `verification/recheck/build`.

## Verification evidence

**Current cumulative proof evidence:** `verification/fourth_final/SUMMARY.json`. It records the actual toolchain and Mathlib revision, all module commands and exit codes, source hashes, transitive dependency source and compiled-interface hashes, 247 theorem audits, 22 construction audits, and both expected negative controls. Axiom dependencies are confined to `propext`, `Classical.choice`, and `Quot.sound`, or subsets thereof. Active sources contain no admitted proofs or added axiom declarations.

**Verifier regression evidence:** `verification/fourth_verifier_regressions.log`, containing 17 passing tests.

**Independent finite regression evidence:** `verification/fourth_examples/SUMMARY.json`. Exact-rational checks cover 180 Kronecker cases, 120 tensor cases, 96 Walsh cases, 240 Toeplitz cases, and 600 clipped-allocation cases, including 60 maximal-budget instances and 1,800 infeasible-budget rejections. These are independent Python mirrors, not execution of the compiled Lean definitions. A separate complex128 Fourier regression covers 96 cases at lengths 1 through 24. All errors were below the declared absolute threshold of 1e-10. These numerical regressions are not proofs or GPU benchmarks.

**Development failures:** 12 of 20 captured fourth-block checks failed before correction; eight passed. Source snapshots, failed diagnostics, and successful development checks are retained in `verification/development/`, with the fourth-block list in `verification/fourth_development_summary.json`. Failures included incomplete development lemmas, visibility errors, finite-index instance reduction and warnings. These drafts are not active proof sources. Both intentionally invalid controls also remain in their separately labeled directory.

Earlier reports remain as historical evidence. `verification/final/SUMMARY.json` is the prior third-block run, not the current release result. Source-preservation evidence is in `verification/fourth_preservation.json`. The current provenance record is `verification/provenance.json`.

## Exact scope and limitations

The Fourier theorem constructs the normalized negative-exponential transform on `ZMod n` for `n > 0`, proves its unitarity, and proves the actual circulant factorization. It does not prove an O(n log n) FFT implementation or benchmark. The Toeplitz theorem uses positive size and a length-2n padded circulant; no symmetry is assumed. The Kronecker vectorization identity uses the ordinary transpose, not the adjoint, on the right factor.

The tensor and Walsh functions specify exact complex-valued mathematical actions. The operation-count theorems use separately declared finite event types for the modewise and butterfly algorithms. The tensor count assumes each intermediate slice is computed once and reused. These are not instrumented execution traces or verified runtime-cost bounds for an arbitrary evaluation strategy of the raw functional definitions. Scalar arithmetic, index operations, cache management, allocation, data movement, complex arithmetic lowering and fused hardware instructions are distinct models.

Clipped precision assumes a nonempty finite edge set, strictly positive sensitivities, costs and caps, and budget in (0, sum s_e*m_e]. Existence follows from continuity and the intermediate value theorem. The minimizing tolerance vector is unique over the whole feasible range. The positive multiplier is unique strictly below maximal budget; at maximal budget, distinct multipliers may produce the same unique vector. This is not a verified numerical root solver. The independent exact-rational allocation routine is not extracted from the Lean proof.

The prior positive-budget amendment to item 8.4 remains in force. The original manuscript has not been silently rewritten. See `notes/MANUSCRIPT_AMENDMENTS.md` for the exact conventions.

This block did not rerun the original CPU numerical corpus, any GPU measurements, or the earlier compiler execution suites. It did not rebuild Papers I–VII in full or independently recheck all imported Mathlib proofs. Historical measurements are not claimed as newly reproduced performance evidence.

## Remaining manuscript-proved items

| Items | Remaining work |
|---|---|
| 4.1 | Equal block banded count |
| 5.6 | Optimal small-core recompression |
| 6.5, 6.6 | Triangular level solve and sequential depth |
| 6.7, 6.8 | Inverse and Schur support inclusion |
| 7.4, 7.6 | Block-Jacobi condition bound and certified preconditioning |
| 9.2 | Exact block-discovery certificate |
| 10.3 | Acyclic schedule depth |

## Preservation and integrity

All 18 upstream Lean modules, the original manuscript PDF/TeX/bibliography/register/source ZIP, and all three earlier supplement PDFs and TeX sources are preserved byte for byte from v0.3.0. Root manifests cover distributed regular files, excluding the manifest and its checksum listing. Checksum verification detects changes relative to the packaged manifest; it is not an external authenticity signature. Local build products and Python caches are deliberately omitted.
