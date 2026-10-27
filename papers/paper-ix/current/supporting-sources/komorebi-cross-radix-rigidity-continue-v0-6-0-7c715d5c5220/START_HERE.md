# START HERE — Komorebi Cross-Radix Rigidity Continuation v0.6.0

This checkpoint extends certified v0.5.0 by closing the finite degree-bounded rank/nullity block for the saved projector-factorized affine section normal form.

## Mandatory reading order

1. `CONTINUE_HERE.md`
2. `PROTOCOL.md`
3. `AUDIT.json`
4. `PROOF_BOUNDARIES.md`
5. `README.md`
6. `src/CrossRadixRankNullity.lean`

The exact v0.5.0 continuation ZIP is retained under `frozen_v0_5/`. All 27 v0.5 source files remain byte-identical.

## Certified v0.6.0 increment

For period `T>0`, degree bound `d`, and positive radix `m`, the new module proves for the finite complex degree-bounded profile model

`rank A_(m,r) = (T / gcd(T,m)) * (d+1)`

and

`nullity A_(m,r) = (T - T/gcd(T,m)) * (d+1)`.

The proof gives an explicit `Fin (T/g)` parametrization of the retained Fourier support, computes the bounded polynomial and profile dimensions, proves the DFT-conjugated projector has the predicted range dimension, and proves reversible affine bookkeeping does not change the range.

The characteristic boundary is also explicit: over any field with `CharP K p`, if `p | m`, affine substitution collapses to evaluation at `r`; if `p ∤ m`, the radix scalar is nonzero.

Bell remains external. No base-independent integral normal form is revived.

## One-line continuation command

> Open `START_HERE.md`, read `CONTINUE_HERE.md`, `PROTOCOL.md`, `AUDIT.json`, and `PROOF_BOUNDARIES.md`, restore certified v0.6.0, preserve every proof boundary, keep Bell explicitly external, and continue with the precise Bell-conclusion interface followed by the uniform all-radix common-hull theorem; do not re-prove the closed rank/nullity block or revive the rejected naive integral normal form.
