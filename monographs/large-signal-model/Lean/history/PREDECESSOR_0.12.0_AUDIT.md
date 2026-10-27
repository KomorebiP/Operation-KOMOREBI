# Large Signal Model Lean 0.12.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production software PR-LASM 2.3.0 unchanged.

This block proves the strict one-sided-to-full projection bound needed by P32 and connects it to a noisy operator through explicit tail and inverse estimates. It adds 15 named theorems (11 supporting results and four examples), one definition and one proof-rejection control. No new manuscript proposition is marked complete: 38/87 complete, P32 partial, 48 not formalized.

## Verdict

The new strict one-sided projection theorem is proved as written in Lean. The noisy 2ε/s corollary is proved under its explicit tail, right-inverse and inverse-norm premises. Full P32: **incomplete, with the smallest missing implication** being derivation of those spectral premises from the actual noisy finite table.

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

## Obligation matrix

| Obligation | Result |
|---|---|
| Actual orthogonal projections and pointwise one-sided hypothesis | Passed |
| Positive c and zero-vector case | Passed |
| Equal dimension used to establish surjectivity | Passed |
| Reverse residual and adjoint norm transfer | Passed |
| Orthogonal decomposition and squared-norm estimate | Passed |
| Noise and tail transfer using actual X,N,R | Passed |
| η=ε, κ=1/s substitution with s>0, ε<s/2 | Passed |
| Equal-dimension necessity counterexample | Passed |
| Sorted singular-value perturbation and leading subspace tail | Not addressed |
| Singular-value bound for constructed right inverse | Not addressed |
| Orthonormal-basis decoder and minimum singular value | Not addressed |
| Independent referee or different prover | Not performed |

Dependency graph: pinned projection/Pythagoras and linear algebra APIs → one-sided coordinate lower bound → constructed equivalence → reverse residual → adjoint operator bound → full gap. Separately: observed tail + perturbation + right inverse → one-sided residual → full gap. No full-gap assumption is used in the new proof. Inherited coordinate results remain unchanged.

No external mathematical citation is required for the new route: its dependencies are imported pinned definitions and kernel-checked lemmas. The frozen P32 source span hash is `062726b8b6d1f04db91faae632eec1d9a0de55eccf12835b3c6591317a5223a7`.

All 82 predecessor proof files, 1,338 declaration records and 76 rejection-control files are unchanged. Metadata tests enforce this against the preserved predecessor ZIP. The source run and fresh ZIP run are separate; consult the external verification JSON for exact archive digest and final counts.

Proofreading self-review covered only the three new Lean modules and current release prose, with P32 context. No mathematical-token corrections were made during proofreading. Remaining mathematical gaps are listed explicitly, not treated as typographical issues.
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
