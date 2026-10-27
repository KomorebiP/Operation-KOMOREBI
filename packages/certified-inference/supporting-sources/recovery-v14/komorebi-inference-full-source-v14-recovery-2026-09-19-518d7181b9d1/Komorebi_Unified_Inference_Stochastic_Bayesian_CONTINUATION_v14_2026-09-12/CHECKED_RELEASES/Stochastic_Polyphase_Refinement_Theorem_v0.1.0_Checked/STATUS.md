# Stochastic Polyphase Refinement Theorem — v0.1.0 Checked

## Verification

- Lean: 4.34.0-rc2
- mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
- full source check: PASS (RC=0)
- representative axiom audit: PASS (RC=0)
- `sorry`: 0
- `admit`: 0
- custom `axiom` declarations: 0

## New block inventory

- 15 new theorem declarations
- 3 new definitions

## Main checked statements

1. Exact coarse-to-fine coordinate block refinement.
2. No-cancellation: a coarse block is zero iff every fine descendant block is zero.
3. Adaptive trigger: a coarse block is nonzero iff some fine descendant block is nonzero.
4. Literal polyphase refinement from modulus `m` to `m*k`.
5. Arbitrary-depth dyadic refinement `m -> m*2^r`.
6. Off-coarse stochastic covariance tangent equals residual forcing block.
7. Off-coarse covariance creation is exactly the sum of fine residual descendants.
8. Stochastic no-cancellation and adaptive refinement criteria.
9. Arbitrary-depth dyadic stochastic leakage trigger.

## Boundary

The refinement/no-cancellation theorem is currently proved for coordinate packet blocks, including literal residue/polyphase lanes. It does not yet claim the corresponding no-cancellation statement for arbitrary overlapping/non-coordinate projector systems.
