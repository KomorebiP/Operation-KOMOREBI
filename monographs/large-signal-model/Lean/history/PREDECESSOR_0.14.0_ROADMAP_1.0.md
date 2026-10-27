# Large Signal Model Lean 0.14.0

Komorebi P. — 2026-10-15. Frozen theory 1.0.0; PR-LASM production software 2.3.0 unchanged.

P32 is complete in its stated finite-table scope. This block constructs the leading singular subspace, proves singular-value perturbation and the exact observed residual, and proves the ordinary matrix inverse decoder and its conditioning. It adds 54 named Lean theorems (47 supporting and seven examples), nine definitions, ten proof modules and two rejection controls. Coverage is now 39/87 complete, zero partial and 48 not formalized.

## Continuation

No P32 implication remains open in the stated finite-table theorem. The broader program has 48 unformalized propositions; see ROADMAP_1.0.json for the exhaustive disjoint list.

Next bounded target: P31, missing-intervention nonidentifiability, in frozen Foundations §32. The exact manuscript construction uses one hidden state and two observations. Both models give (1/2,1/2) under action a; they give (1,0) and (0,1) under b. Formalize actual stochastic models, prove every a-only word has common probability 2^(-length), and exhibit the one-step b disagreement. Existing instrument and word-probability APIs should supply the construction. P31 is not counted as proved by this handoff.

P35's reset-experiment probability certificate and P37's conditional observation-based completion remain further parts of the learning chain. P32 does not silently supply their statistical or coverage assumptions.

## Unformalized propositions

- P11: Ideal statistical benefit of refinement
- P23: Exact accounting for an enumerated grammar
- P24: Prior-preserving program refinement
- P31: Missing-intervention nonidentifiability
- P35: Reset-experiment probability certificate
- P37: Conditional observation-based stochastic completion
- P46: A rational rank-three model with no polyhedral probability-domain certificate
- P47: Polyhedral approximation of the rotation model
- P48: Sequential confidence accounting for certified proposals
- P49: Conditional learning with an all-horizon probability certificate
- P50: Matrix-embedding probability certificate
- P51: Exact rational matrix witness for the rotation model
- P52: Continuous-observation instrument semantics
- P53: Polynomial Gram certificate for interval observations
- P54: Conditional finite-moment identification
- P55: A valid continuous counterexample to finite-moment identification
- P56: Exact bin coarsening and its posterior
- P57: Exact covariance correction for an averaged congruence
- P58: Positive cell-average approximation
- P59: Continuous-record total-variation bound
- P60: Exact recognition of a fixed certified template
- P61: Conditional continuous realization with a finite domain certificate
- P62: Oriented quadratic probability certificate
- P63: Conditional operator-only ellipsoid discovery
- P64: Valid positive polynomial approximation
- P65: Certified coefficient error and approximation bias
- P66: Time-uniform predictable-residual certificate
- P67: Covered adaptive-action evidence
- P68: Sequential evidence gives a lower error certificate
- P69: Observation-law error without a shared state space
- P70: Separate structural acceptance, approximation control and sequential rejection
- P71: Robust oriented margin
- P72: Boundary fragility under mass preserving perturbations
- P73: Interior repair with an explicit error budget
- P74: A posteriori proposal error
- P75: Rational semicircle and Bernstein certificate
- P76: Coefficient boxes and convex uncertainty
- P77: Conditional search for strict rational curved certificates
- P78: Data-selected geometry with honest coverage
- P79: Certified repair with a retained comparison budget
- P80: Convex repair bracketing
- P81: Time-uniform regression confidence
- P82: Sequential observable-moment operator sets
- P83: Structured curved-domain certificate
- P84: Exact rational outer confidence intervals
- P85: Parameter-to-law error without a state-estimation term
- P86: Uniform marginal and rolling-window stability
- P87: Observable structured learning with a covered domain
