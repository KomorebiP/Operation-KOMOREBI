# Large Signal Model Lean 0.12.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production software PR-LASM 2.3.0 unchanged.

This block proves the strict one-sided-to-full projection bound needed by P32 and connects it to a noisy operator through explicit tail and inverse estimates. It adds 15 named theorems (11 supporting results and four examples), one definition and one proof-rejection control. No new manuscript proposition is marked complete: 38/87 complete, P32 partial, 48 not formalized.

PASS: 250 cumulative verification stages; 82 metadata/tooling checks.

## New theorem and proof

Let P and Q be subspaces of a finite-dimensional real inner-product space, with equal finite dimension. Suppose 0≤δ<1 and

\[\|x-Qx\|\leq\delta\|x\|\quad\text{for every }x\in P.\]

Then \(\|P-Q\|\leq\delta\). Here P and Q in operator expressions denote actual orthogonal projections; the Lean statements use `Submodule.starProjection`.

Put c=√(1−δ²)>0. Pythagoras gives ‖Qx‖≥c‖x‖ on P, so Q restricted to P is injective. Equal finite dimensions make it surjective onto Q, with inverse norm at most 1/c. For y∈Q take x∈P with Qx=y. Self-adjointness gives ⟨Py,x⟩=⟨y,x⟩=‖y‖². Combining Cauchy–Schwarz and c‖x‖≤‖y‖ yields ‖Py‖≥c‖y‖, treating y=0 separately. Pythagoras yields ‖y−Py‖≤δ‖y‖.

Thus ‖(I−P)Q‖≤δ. Adjoint norm preservation gives ‖Q(I−P)‖≤δ. Write v=Pv+(I−P)v and

\[(P-Q)v=(I-Q)Pv-Q(I-P)v.\]

The two right-hand terms are orthogonal. Their squared norms sum to at most δ²(‖Pv‖²+‖(I−P)v‖²)=δ²‖v‖². This proves the operator norm estimate. The Lean proof uses no principal-angle decomposition and proves the bound in the strict regime; it does not claim the unrestricted global projection-norm identity.

For operators X,N:F→E, let Y=X+N and let R:P→F satisfy X(Rx)=x. If ‖(I−Q)Y‖≤η, ‖N‖≤ε and ‖R‖≤κ, with nonnegative budgets, then

\[\|(I-Q)x\|\leq(\eta+\varepsilon)\kappa\|x\|.\]

The proof transfers the observed residual to X by the triangle inequality, then applies R. If (η+ε)κ<1 and P,Q have equal dimension, the previous theorem proves the full gap. Substituting η=ε, κ=1/s and ε<s/2 gives \(\|P-Q\|\leq2\varepsilon/s<1\). The tail estimate and inverse estimate are explicit premises, not derived singular-value conclusions.

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

## Development and failures

9 compiler invocations: 5 successful, 4 failed. Every invocation has a source snapshot and diagnostic JSON in `verification/development_block12/`.

Failures were: the initial dependency lookup did not fall through a new namespace build directory; copying the already verified predecessor objects repaired development imports. An overly broad simplification failed to prove complement-projection idempotence; a direct membership theorem fixed it. Simplifying a vector residual identity left an additive goal; explicit linearity plus additive normalization fixed it. The first boundary-example compile needed the explicit top-projection identity. No failure was hidden by a placeholder or weaker final theorem.

Development compilation used predecessor objects; accepted cumulative verification rebuilds the project from scratch. The first coordinate module was extended while its earlier development invocation was awaiting collection; that exploratory invocation is not final-source evidence. Final cumulative source verification holds the inventoried files fixed.
