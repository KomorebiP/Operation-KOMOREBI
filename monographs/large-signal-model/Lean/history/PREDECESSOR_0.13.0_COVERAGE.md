# Large Signal Model Lean 0.13.0

Komorebi P. — 2026-10-15. Theory baseline 1.0.0; production PR-LASM 2.3.0 unchanged.

This block proves the exact spectral norm of the existing orthogonal pseudoinverse and constructs the bounded right inverse on the actual column space. It removes the inverse and inverse-norm hypotheses from the previous noisy-subspace theorem. It adds 20 named Lean theorems (16 supporting and four examples), four definitions and two rejection controls. P32 remains partial; coverage remains 38/87 complete, one partial and 48 not formalized.

## Exact remaining P32 obligations

1. Prove sorted singular-value perturbation and rank separation for the actual finite table, including the maximal-rank tail-zero convention.
2. Construct the actual leading-r left singular subspace of Y and prove its observed tail bound. The current strongest gap theorem still takes the candidate subspace's dimension and observed tail as inputs.
3. Prove the orthonormal-basis matrix minimum-singular-value bound and the explicit decoder U(UhatᵀU)⁻¹.

The right inverse on the true range and its bound from σ_r(X) are now proved. The earlier one-sided-to-full projection argument and basis-free coordinate conditioning are already proved. None of these results certifies unseen process modes or the adequacy of a chosen finite table.

## Proposition register

- P1: Exact realization and consistency — complete
- P2: Coherent transport and operator realization — complete
- P3: Complete refinement preserves reconstruction — complete
- P4: Transfer reconstruction and refinement — complete
- P5: Polynomial packet interactions — complete
- P6: Exact quotient criterion — complete
- P7: Closure defect and compositional defect — complete
- P8: Minimal linear predictive completion — complete
- P9: Coarsest joint finite closure — complete
- P10: Exact projected memory and a conditional tail bound — complete
- P11: Ideal statistical benefit of refinement — not_formalized
- P12: Bayesian closure and its exact defect — complete
- P13: Strong fixed-horizon refinement limit — complete
- P14: Exact causal delay closure — complete
- P15: Data-span identification and its boundary — complete
- P16: Fixed-space identification bound — complete
- P17: Finite-prefix indistinguishability — complete
- P18: Compositional defect propagation — complete
- P19: Uniform prediction bound for a stable finite-memory truncation — complete
- P20: Packet-interaction truncation bound — complete
- P21: Coherent reconciliation and coordinate-stable transport — complete
- P22: The upward-lift obstruction — complete
- P23: Exact accounting for an enumerated grammar — not_formalized
- P24: Prior-preserving program refinement — not_formalized
- P25: Observationally grounded finite linear realization — complete
- P26: Finite instrument closure — complete
- P27: Minimal finite behavior realization — complete
- P28: Observable table reconstruction — complete
- P29: Canonical probability cone — complete
- P30: Positive packet decomposition and its boundary — complete
- P31: Missing-intervention nonidentifiability — not_formalized
- P32: Finite-table rank separation and subspace stability — partial
- P33: Noisy core-block realization — complete
- P34: Normalization-aware filtering stability — complete
- P35: Reset-experiment probability certificate — not_formalized
- P36: Exact normalized closure defect — complete
- P37: Conditional observation-based stochastic completion — not_formalized
- P38: Test-cone hierarchy and a finite stopping certificate — complete
- P39: Finite positive-lift certificate — complete
- P40: Robust finite-domain certificate — complete
- P41: Certified correction and its error budget — complete
- P42: Instrument contraction before normalization — complete
- P43: Observation-tree total-variation bound — complete
- P44: Sharp event-probability dependence of conditioning — complete
- P45: Rational finite-certificate search — complete
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
