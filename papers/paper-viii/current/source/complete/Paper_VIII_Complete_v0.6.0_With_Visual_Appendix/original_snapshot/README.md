# PRSC VIII — Checked Sixth Block v0.6.0

**Author: Komorebi P.**

## Status

**All 56 registered manuscript-proved items are covered under their recorded hypotheses.** Theorem 5.6, small-core optimal recompression, is completed in this block. Four classical inputs remain separately tracked, not silently promoted to independent formalizations.

The release adds **79 named theorem declarations in ten modules**. The cumulative corpus contains **392 declarations in 40 modules**: 373 Paper VIII declarations and 19 in the unchanged reused quantum-packet foundation. **66 construction audits are counted separately.** Supporting lemmas and specializations are included in the theorem count, not presented as independent discoveries.

All 40 modules passed a fresh cumulative Lean build with warnings treated as errors. Every theorem and construction audit matched the inventory and allowed-axiom policy. Both invalid-proof controls were rejected. The 43 current unit tests passed.

## The completed theorem

For original finite complex factors `L` and `R`, the source constructs orthonormal bases of their actual column spaces, giving `L = QL RL`, `R = QR RR` and core `G = RL RR*`. The core dimensions are proved to equal the two input matrix ranks, including zero and rank-deficient factors.

Given an ordered thin SVD `G = W diag(sigma) Z*`, the source constructs factors with exactly `min(d,k)` columns. Their product has rank at most `k`, minimizes both the spectral and Frobenius errors against **every ambient rank-bounded competitor**, and has exactly the stated singular-tail errors. Zero singular values are never inverted. Rank zero and full retention are checked separately.

**The SVD input consists only of orthonormality, nonnegative ordered values and exact reconstruction. No optimality or tail-error conclusion is assumed.** The diagonal spectral lower bound is proved with an actual prefix-supported kernel witness. The Frobenius lower bound is proved with an actual orthonormal kernel basis and a finite weighted-tail inequality. Isometric compression then transfers the result to arbitrary rectangular factors and arbitrary ambient competitors.

**Scope:** general SVD existence, a floating-point SVD/QR algorithm and identification with the canonical Mathlib `singularValues` API are not independently formalized here. This follows the manuscript's explicit instruction to take an SVD. Compact orthonormal range factorization is constructed, but no numerical triangular QR procedure is claimed. The exact algebraic SVD equations are mathematical hypotheses, not an assertion that arbitrary numerical outputs satisfy them exactly.

Principal target: `KomorebiPaperVIII.SmallCore.small_core_optimal_recompression` in `formalization/SmallCoreRecompression.lean`.

## Read the release

- `notes/Paper_VIII_Sixth_Lean_Block_Supplement.pdf`: eight-page proof and verification supplement.
- `notes/COVERAGE_LEDGER.md` and `verification/coverage_ledger.json`: all 56 items, targets and boundaries.
- `verification/sixth_final/SUMMARY.json`: the fresh cumulative proof report and per-module log hashes.
- `verification/sixth_release_audit.json`: current tests, preservation, PDF checks and declared limitations.
- `notes/SIXTH_BLOCK_REPORT.md`: concise actual-results record.

The original manuscript and its source package remain under `manuscript/`. All 30 upstream proof sources and all five earlier PDF/TeX supplements remain byte-identical. Earlier supplements and reports retain their historical counts. The current ledger and sixth supplement supersede their remaining-work lists. The proof additions have not yet been integrated into a rewritten primary manuscript.

## Reproduce

The separately supplied portable Linux x86-64/WSL kit is pinned to **Lean 4.34.0-rc2** and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Its large runtime is not duplicated in this source archive. Python 3.10 or later is required. Tests and numerical mirrors also need NumPy. Run from the extracted release root:

```bash
python3 scripts/verify_integrity.py
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/recheck --timeout 240
python3 scripts/run_sixth_regressions.py --out verification/recheck_numerical.json
```

The Lean runner accepts `--max-checks 2 --resume` with the same output directory on hosts with short command limits. A partial checkpoint is not a pass. Source, dependency, interface and log hashes govern resume. The source archive excludes local compiled interfaces, so the first run regenerates them. The pinned Mathlib cache is reused, not independently rebuilt or rechecked.

To rebuild the supplement with TeX, run `pdflatex` twice on `notes/Paper_VIII_Sixth_Lean_Block_Supplement.tex`, using a separate output directory. The original manuscript is not rewritten by that operation.

## New source map

| Module | Named theorems |
|---|---:|
| SmallCoreNorms | 19 |
| CompactRangeFactors | 7 |
| SmallCoreTransfer | 7 |
| KernelFrame | 8 |
| DiagonalTruncation | 9 |
| FrobeniusOptimality | 5 |
| SpectralOptimality | 7 |
| CompactTruncation | 5 |
| SmallCoreRecompression | 6 |
| RecompressionEndpoints | 6 |
| **Added** | **79** |

## Evidence and failures

**Lean:** all 40 modules and all 392 named theorem / 66 construction audits passed in a newly created output directory. Allowed transitive dependencies are `propext`, `Classical.choice` and `Quot.sound`, or subsets thereof. Both the deliberately false equality and admitted-proof controls were rejected.

**Unit tests:** 17 verifier tests, 12 fifth-block compatibility tests updated for this release, and 14 new sixth-block tests passed. The original fixed-count fifth-block test file is preserved under `verification/provenance/`. These tests guard metadata and the verification harness; they do not replace kernel checking.

**Independent numerical mirror:** 182 factor pairs, 638 truncation cases, 3,190 arbitrary rank-bounded competitors, nine invalid-input controls and two mathematical assumption-removal controls passed. The mirror uses NumPy complex128 and numerical rank thresholds. It is not compiled or extracted Lean and makes no hardware-performance claim. Results and script hashes are in `verification/sixth_numerical_regressions.json`.

**Development:** 21 of 31 captured checks failed before correction. Their source snapshots and diagnostics are retained in `verification/development_sixth/`, separate from active sources and the clean accepted build. An initial interactive runtime launch was unsupported. Noninteractive assembly succeeded, verifying all seven part hashes and the combined hash. The runtime log is retained.

**Provenance:** the base is the second same-named fifth-block upload, the 313-declaration release, with exact input file ID and SHA-256 in `verification/sixth_preservation.json`. The earlier 298-declaration branch is not merged. All 30 upstream modules and 15 original manuscript/supplement assets are checked unchanged.

## Remaining boundaries

The four classical entries are still tracked separately: Eckart–Young–Mirsky (5.5), CG convergence (7.5), floating-point product model (8.2), and simultaneous spectral decomposition (9.1). Ordered-SVD-data optimality now has a checked supporting proof, but general SVD existence or the full canonical singular-values API theorem is not newly claimed. The other classical algorithm/model inputs are not independently reproved in this release.

The original CPU/GPU benchmarks, historical numerical corpus, earlier compiler execution suites and Papers I–VII in full were not rerun. No imported Mathlib proof corpus was independently rechecked. No new generic dense-matrix exponent, CUDA implementation correctness, floating-point stability or quantum-spacetime conjecture is established. Manuscript-to-Lean correspondence is a mathematical review, not an automated semantic-equivalence theorem.
