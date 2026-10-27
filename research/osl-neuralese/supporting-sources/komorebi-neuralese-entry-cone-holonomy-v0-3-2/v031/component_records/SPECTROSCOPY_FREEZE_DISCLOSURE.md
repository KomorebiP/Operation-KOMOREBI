# Exploratory Endpoint Disclosure

The initial task requested inspection of the v0.3.0 checkpoints. Before the
parent task imposed the v0.3.1 pre-registration boundary, the following old
v0.3.0 learned quantities were inspected. They are exploratory design context
and must not be presented as pre-registered v0.3.1 evidence.

- Both v0.3.0 checkpoints and all sixteen registered v0.3.0 episodes were
  loaded.
- For each of 64 primitive composites (2 checkpoint seeds × 8 episodes × 4
  relators), the relation product, Frobenius-best nonnegative scalar identity,
  relative residual, eigenvalues and moduli, dominant-to-second modulus ratio,
  and maximum imaginary component were computed and printed to the execution
  log.
- For all 336 old v0.3.0 episode/configuration records and 172,032 base-case
  configurations, generator-wise repeated relation execution was compared at
  the loop endpoint with positive-rescaled composite-power execution. All
  endpoint argmaxes agreed. The maximum unit-state discrepancy was
  `1.5838753028799055e-14`.
- An unscaled high-power attempt reached norm
  `2.2353635009057133e-23` and triggered the existing `1e-12` state-norm
  guard. This is why the prototype normalizes after each relation block rather
  than using raw high powers.
- An independent exploratory reconstruction of the already-published earliest
  depth-38 witness obtained: primitive `alpha+=0.00128675244589`, primitive
  relative scalar defect `0.5350502137`, leading modulus `0.00159132214`,
  second/first modulus ratio `0.9302401`, eight-power defect `0.6601083134`, and
  raw eight-power Frobenius norm `7.43e-23`. Its loop endpoint angle and margin
  were `0.432599` radians and `+2.590676`; after suffix `F,F,R` they were
  `0.692030` radians and `-0.0469179292`, with predicted class 1 and target
  class 7. Composite and generator execution agreed to `1.66e-15` there.

No endpoint values were computed for the proposed fresh v0.3.1 episode seeds
`940000` or `941000`. All implementation and testing after the boundary was
restricted to transparent synthetic matrices and already-published result
fields.
