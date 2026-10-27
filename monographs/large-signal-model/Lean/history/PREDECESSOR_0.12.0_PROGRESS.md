# Large Signal Model Lean 0.12.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production software PR-LASM 2.3.0 unchanged.

This block proves the strict one-sided-to-full projection bound needed by P32 and connects it to a noisy operator through explicit tail and inverse estimates. It adds 15 named theorems (11 supporting results and four examples), one definition and one proof-rejection control. No new manuscript proposition is marked complete: 38/87 complete, P32 partial, 48 not formalized.

PASS: 250 cumulative verification stages; 82 metadata/tooling checks.

## Source map

| Module | Contents |
|---|---|
| `OneSidedSubspace.lean` | Seven theorems: coordinate lower bound, injection, inverse bound, reverse lower bound and residual, reverse operator bound, full projection gap; one constructed equivalence. |
| `NoisySubspaceResidual.lean` | Four theorems: true residual, residual on the range, conditional noisy projection gap, conditional 2ε/s gap. |
| `Block12Examples.lean` | Zero residual at equal rank forces equal projections; unequal-rank zero one-sided residual; its full gap equals one; a half-gap specialization. |

The unequal-rank example uses P={0}, Q=ℝ. Every x∈P has zero residual, yet ‖P−Q‖=1. The new negative control attempts the false bound ≤0 and must be rejected. This is a boundary check, not an additional positive theorem.

## Exact remaining P32 work

1. Prove sorted singular-value perturbation/rank separation for the actual finite table, including the maximal-rank zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its tail residual bound; equal dimension and the tail are currently supplied hypotheses.
3. Construct the right inverse on the true range with norm at most 1/σ_r(X). The existing pseudoinverse is available, but this exact spectral bridge is still missing.
4. Express the coordinate map in orthonormal bases, prove the minimum-singular-value bound, and derive the explicit decoder U(UhatᵀU)⁻¹.

The full P32 theorem remains incomplete. Nothing here certifies unseen process modes, the adequacy of a finite table, floating-point SVD, learned probability validity, or a known true decoder.

## Development and failures

9 compiler invocations: 5 successful, 4 failed. Every invocation has a source snapshot and diagnostic JSON in `verification/development_block12/`.

Failures were: the initial dependency lookup did not fall through a new namespace build directory; copying the already verified predecessor objects repaired development imports. An overly broad simplification failed to prove complement-projection idempotence; a direct membership theorem fixed it. Simplifying a vector residual identity left an additive goal; explicit linearity plus additive normalization fixed it. The first boundary-example compile needed the explicit top-projection identity. No failure was hidden by a placeholder or weaker final theorem.

Development compilation used predecessor objects; accepted cumulative verification rebuilds the project from scratch. The first coordinate module was extended while its earlier development invocation was awaiting collection; that exploratory invocation is not final-source evidence. Final cumulative source verification holds the inventoried files fixed.
