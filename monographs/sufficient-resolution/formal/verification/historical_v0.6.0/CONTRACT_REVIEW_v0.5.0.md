# Contract review — continuous-time memory

This is a source-level review of the checked declarations, not independent novelty
review. Principal signatures are printed separately in PRINCIPAL_SIGNATURES_v0.5.0.log.

1. The operator flow is `NormedSpace.exp (t • L)`. It is not an abstract family
   carrying the required differential equation as a field.
2. Banach-space completeness and boundedness are explicit. The hidden/visible ODEs
   are consequences of differentiation of the full exponential.
3. The forced variation formula assumes only the actual ODE and continuous forcing.
   Its proof differentiates backward propagation and uses interval FTC. The block
   application supplies these hypotheses from the full dynamics.
4. Operator-valued memory is defined as B exp(tD) G. Continuity and integrability
   of its statewise convolution are derived. No desired Volterra identity is an axiom.
5. Prepared state R(y)=(y,0) and arbitrary hidden initialization are separately stated.
   The initial forcing B exp(tD)z0 is removed only in the prepared theorem.
6. Exponential/power equivalence has both directions. The forward direction uses
   derivative uniqueness at every jet. The reverse maps the convergent exponential
   series. It does not infer an all-time statement from finite sampled times.
7. The finrank stopping result imports the unchanged characteristic-polynomial
   certificate via actual toLinearMap bridges. Zero hidden dimension is included.
8. Iterated derivatives are Mathlib iteratedDeriv, not a custom definition set equal
   to powers. Their identification with powers is proved by induction.
9. The compressed semigroup identity quantifies over real s,t. There is no assertion
   that a finite sample of that identity implies it globally.
10. A general bounded split need not be orthogonal. Its discarded dimension is the
    dimension of ker C. The corresponding algebraic splitting is preserved.
11. The example M(t)=tI is proved from the actual exponential, through a uniquely
    solved nilpotent ODE. Its third derivative discrepancy is not a floating result.
12. Python coefficient controls validate finite implementations only. No data-driven
    inference, formalized Python execution, native_decide or new axioms are used.

Residual boundaries: converse Volterra reconstruction, unbounded/time-varying/nonlinear
or stochastic systems, quantitative continuous error, constrained realizability and
arithmetic existence are outside this block. Historical novelty remains unaudited.
