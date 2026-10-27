# Large Signal Model Lean 0.12.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production software PR-LASM 2.3.0 unchanged.

This block proves the strict one-sided-to-full projection bound needed by P32 and connects it to a noisy operator through explicit tail and inverse estimates. It adds 15 named theorems (11 supporting results and four examples), one definition and one proof-rejection control. No new manuscript proposition is marked complete: 38/87 complete, P32 partial, 48 not formalized.

## Exact remaining P32 work

1. Prove sorted singular-value perturbation/rank separation for the actual finite table, including the maximal-rank zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its tail residual bound; equal dimension and the tail are currently supplied hypotheses.
3. Construct the right inverse on the true range with norm at most 1/σ_r(X). The existing pseudoinverse is available, but this exact spectral bridge is still missing.
4. Express the coordinate map in orthonormal bases, prove the minimum-singular-value bound, and derive the explicit decoder U(UhatᵀU)⁻¹.

The full P32 theorem remains incomplete. Nothing here certifies unseen process modes, the adequacy of a finite table, floating-point SVD, learned probability validity, or a known true decoder.

Start from `source/FOUNDATIONS_1.0.0.md` §33, lines 1388–1426, and the P32 record in COVERAGE.json. The earlier written one-sided route is now formalized in OneSidedSubspace.lean. Preserve all predecessor proofs and completed coverage. Do not replace remaining spectral obligations by assumed fields and mark P32 complete.

## Reproduce

Use the existing portable Lean 4.34.0-rc2 runtime. Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; all nine package pins are in `lake-manifest.json`. The runtime is supplied separately in the previously saved seven-part kit.

From a fresh project extraction, before generating files:

```bash
python3 scripts/verify_hashes.py
python3 scripts/build_inventory.py
python3 scripts/check_metadata.py
LD_PRELOAD=/absolute/kit/compat/app_path.so python3 scripts/verify.py --kit /absolute/kit --out /absolute/run-directory
```

The supplied compatibility preload is needed on this host. Keep `.olean.server` files when restoring the runtime. Verification deletes and rebuilds local project objects, checks compiler/dependency pins, compiles every module with warnings as errors, runs the rational examples, audits all named declarations, replays every project module through LeanChecker, and checks the rejection controls. Allowed logical axioms are only `propext`, `Classical.choice`, `Quot.sound`.

The pinned upstream environment is not exhaustively rebuilt or replayed. This is a self-review and kernel check, not an independent referee or a second proof assistant.
