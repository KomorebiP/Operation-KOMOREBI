# Large Signal Model Lean 0.13.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production PR-LASM 2.3.0 unchanged.

This block proves the exact spectral norm of the existing orthogonal pseudoinverse and constructs the bounded right inverse on the actual column space. It removes the inverse and inverse-norm hypotheses from the previous noisy-subspace theorem. It adds 20 named Lean theorems (16 supporting and four examples), four definitions and two rejection controls. P32 remains partial; coverage remains 38/87 complete, one partial and 48 not formalized.

## Exact remaining P32 obligations

1. Prove sorted singular-value perturbation and rank separation for the actual finite table, including the maximal-rank tail-zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its observed tail bound. The current strongest gap theorem still takes the candidate subspace's dimension and observed tail as inputs.
3. Prove the orthonormal-basis matrix minimum-singular-value bound and the explicit decoder U(UhatᵀU)⁻¹.

The right inverse on the true range and its bound from σ_r(X) are now proved. The earlier one-sided-to-full projection argument and basis-free coordinate conditioning are already proved. None of these results certifies unseen process modes or the adequacy of a chosen finite table.

Resume from `source/FOUNDATIONS_1.0.0.md` §33, lines 1388–1426. Use `gap_from_observed_tail` as the strongest current endpoint. Prove the spectral-tail inputs from the actual leading-left subspace before claiming P32 complete. Preserve zero-based indexing and rectangular/maximal-rank cases.

## Verification and reproduction

The release has 89 proof modules, 90 compilation targets including the root, 1,378 named declarations and 1,063 named theorems. Of those theorems, 324 occur in example modules and 739 are supporting results. There are 79 isolated rejection controls. These counts are not manuscript-proposition counts.

Use the separately saved portable Lean 4.34.0-rc2 runtime. Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. All nine package pins remain unchanged.

From a fresh project extraction, run the file check before creating build files:

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
LD_PRELOAD=/absolute/kit/compat/app_path.so python3 scripts/verify.py --kit /absolute/kit --out /absolute/run-directory
```

The verifier rebuilds project objects, compiles with warnings as errors, runs inherited exact rational examples, audits all named declarations, replays every project proof module with LeanChecker and checks all rejection controls. Allowed logical axioms are only `propext`, `Classical.choice`, `Quot.sound`. Keep `.olean.server` files in the runtime. The supplied path compatibility preload is required on this host.

The upstream pinned libraries are not exhaustively rebuilt/replayed. This is a self-review and Lean kernel verification, not an independent referee or second proof assistant. The external verification JSON links the exact delivered archive hash to its fresh extraction run.
