# Large Signal Model Lean 0.13.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production PR-LASM 2.3.0 unchanged.

This block proves the exact spectral norm of the existing orthogonal pseudoinverse and constructs the bounded right inverse on the actual column space. It removes the inverse and inverse-norm hypotheses from the previous noisy-subspace theorem. It adds 20 named Lean theorems (16 supporting and four examples), four definitions and two rejection controls. P32 remains partial; coverage remains 38/87 complete, one partial and 48 not formalized.

PASS: 260 cumulative verification stages; 84 metadata/tooling checks.

## Source map

| Module | Contents |
|---|---|
| `SpectralLowerBound.lean` | Six theorems and two definitions: ordered Gram basis, spectral norm expansion, zero modes, actual least positive singular value and lower bound on the kernel complement. |
| `SpectralPseudoinverse.lean` | Five theorems and one definition: pointwise/operator inverse bounds, constructed range inverse, right-inverse law and noisy gap with derived inverse premises. |
| `SpectralSharpness.lean` | Five theorems: basis image norm, positive-mode orthogonality, unit minimizer and exact norms for the full and restricted pseudoinverse. |
| `Block13Examples.lean` | Four theorems and one definition: scalar factor two has s=2 and inverse norm 1/2; zero map has s=0; a rank-one projection disproves a global-domain lower bound. |

The counterexample uses the actual first-coordinate projection from Euclidean ℝ² and the second unit vector. The two negative controls deliberately attempt inverse norm ≤1/4 for scalar factor two and strict positivity of the zero map's least singular value. They must fail in isolation.

## Exact remaining P32 obligations

1. Prove sorted singular-value perturbation and rank separation for the actual finite table, including the maximal-rank tail-zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its observed tail bound. The current strongest gap theorem still takes the candidate subspace's dimension and observed tail as inputs.
3. Prove the orthonormal-basis matrix minimum-singular-value bound and the explicit decoder U(UhatᵀU)⁻¹.

The right inverse on the true range and its bound from σ_r(X) are now proved. The earlier one-sided-to-full projection argument and basis-free coordinate conditioning are already proved. None of these results certifies unseen process modes or the adequacy of a chosen finite table.

## Development record

8 compiler invocations: 4 successful and 4 failed. Source snapshots and diagnostics are retained in `verification/development_block13/`.

The failures were a missing unfolding/rewrite for the named eigenbasis in the inner-product identity; a continuous-map versus linear-map coercion blocking a norm rewrite; scalar examples needing explicit quotient arithmetic and inverse notation; and an attempted simplification with deprecated or unused arguments, rejected by warnings-as-errors. Direct typed equalities and the appropriate algebraic rewrites resolved them. No statement was weakened, and no proof placeholder was accepted.

Development used previously checked predecessor objects. The accepted cumulative runs rebuild all project objects. Inventoried sources are frozen during accepted runs.
