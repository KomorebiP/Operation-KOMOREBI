# Large Signal Model Lean 0.12.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production software PR-LASM 2.3.0 unchanged.

This block proves the strict one-sided-to-full projection bound needed by P32 and connects it to a noisy operator through explicit tail and inverse estimates. It adds 15 named theorems (11 supporting results and four examples), one definition and one proof-rejection control. No new manuscript proposition is marked complete: 38/87 complete, P32 partial, 48 not formalized.

## Exact remaining P32 work

1. Prove sorted singular-value perturbation/rank separation for the actual finite table, including the maximal-rank zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its tail residual bound; equal dimension and the tail are currently supplied hypotheses.
3. Construct the right inverse on the true range with norm at most 1/σ_r(X). The existing pseudoinverse is available, but this exact spectral bridge is still missing.
4. Express the coordinate map in orthonormal bases, prove the minimum-singular-value bound, and derive the explicit decoder U(UhatᵀU)⁻¹.

The full P32 theorem remains incomplete. Nothing here certifies unseen process modes, the adequacy of a finite table, floating-point SVD, learned probability validity, or a known true decoder.

## All unfinished propositions

- P11: Ideal statistical benefit of refinement — not_formalized
- P23: Exact accounting for an enumerated grammar — not_formalized
- P24: Prior-preserving program refinement — not_formalized
- P31: Missing-intervention nonidentifiability — not_formalized
- P32: Finite-table rank separation and subspace stability — partial
- P35: Reset-experiment probability certificate — not_formalized
- P37: Conditional observation-based stochastic completion — not_formalized
- P46: A rational rank-three model with no polyhedral probability-domain certificate — not_formalized
- P47: Polyhedral approximation of the rotation model — not_formalized
- P48: Sequential confidence accounting for certified proposals — not_formalized
- P49: Conditional learning with an all-horizon probability certificate — not_formalized
- P50: Matrix-embedding probability certificate — not_formalized
- P51: Exact rational matrix witness for the rotation model — not_formalized
- P52: Continuous-observation instrument semantics — not_formalized
- P53: Polynomial Gram certificate for interval observations — not_formalized
- P54: Conditional finite-moment identification — not_formalized
- P55: A valid continuous counterexample to finite-moment identification — not_formalized
- P56: Exact bin coarsening and its posterior — not_formalized
- P57: Exact covariance correction for an averaged congruence — not_formalized
- P58: Positive cell-average approximation — not_formalized
- P59: Continuous-record total-variation bound — not_formalized
- P60: Exact recognition of a fixed certified template — not_formalized
- P61: Conditional continuous realization with a finite domain certificate — not_formalized
- P62: Oriented quadratic probability certificate — not_formalized
- P63: Conditional operator-only ellipsoid discovery — not_formalized
- P64: Valid positive polynomial approximation — not_formalized
- P65: Certified coefficient error and approximation bias — not_formalized
- P66: Time-uniform predictable-residual certificate — not_formalized
- P67: Covered adaptive-action evidence — not_formalized
- P68: Sequential evidence gives a lower error certificate — not_formalized
- P69: Observation-law error without a shared state space — not_formalized
- P70: Separate structural acceptance, approximation control and sequential rejection — not_formalized
- P71: Robust oriented margin — not_formalized
- P72: Boundary fragility under mass preserving perturbations — not_formalized
- P73: Interior repair with an explicit error budget — not_formalized
- P74: A posteriori proposal error — not_formalized
- P75: Rational semicircle and Bernstein certificate — not_formalized
- P76: Coefficient boxes and convex uncertainty — not_formalized
- P77: Conditional search for strict rational curved certificates — not_formalized
- P78: Data-selected geometry with honest coverage — not_formalized
- P79: Certified repair with a retained comparison budget — not_formalized
- P80: Convex repair bracketing — not_formalized
- P81: Time-uniform regression confidence — not_formalized
- P82: Sequential observable-moment operator sets — not_formalized
- P83: Structured curved-domain certificate — not_formalized
- P84: Exact rational outer confidence intervals — not_formalized
- P85: Parameter-to-law error without a state-estimation term — not_formalized
- P86: Uniform marginal and rolling-window stability — not_formalized
- P87: Observable structured learning with a covered domain — not_formalized
