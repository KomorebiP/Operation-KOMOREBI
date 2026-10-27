# START HERE — Komorebi Cross-Radix Rigidity Continuation v0.8.0

This checkpoint extends certified v0.7.0 by closing the active shell–jet / minimal invariant-hull block.

## Mandatory reading order

1. `CONTINUE_HERE.md`
2. `PROTOCOL.md`
3. `AUDIT.json`
4. `PROOF_BOUNDARIES.md`
5. `BELL_EXTERNAL_INTERFACE.md`
6. `src/CrossRadixProfileOrbitHull.lean`
7. `src/CrossRadixActiveShellJetHull.lean`
8. `src/CrossRadixInvariantShellJetHull.lean`
9. `src/CrossRadixMinimalCommonHull.lean`

The exact v0.7.0 continuation ZIP is retained under `frozen_v0_7/`. All 31 v0.7 source files remain byte-identical.

## Certified v0.8.0 increment

For a bounded period-`T`, degree-`d` profile `P`, Lean now constructs:

- `ProfileOrbitHull T d P`: the absolute smallest complex-linear tail-profile subspace containing `P` and invariant under every positive affine section;
- `ShellJetEnvelope hT H`: the smallest Fourier-shell / polynomial-jet zero-mask subspace containing `H`;
- `InvariantShellJetEnvelope hT H`: the smallest positive-affine-invariant shell/jet mask subspace containing `H`;
- `OrbitCommonHull N T d P`: the transient-prefix plus minimal-tail-orbit sequence hull.

For a `BellDownstreamInterface a`, the last hull contains every positive affine/radix section of `a`, is itself positive-affine invariant, and is minimal among such sequence subspaces once the full transient prefix space is retained.

The refined bound is

`finrank OrbitCommonHull ≤ N + finrank ProfileOrbitHull`

and also

`finrank OrbitCommonHull ≤ N + active Fourier-frequency/jet coordinate count ≤ N + T*(d+1)`.

If the active coordinate count is strictly smaller than `T*(d+1)`, Lean proves a strict improvement over the v0.7 coarse bound.

## One-line continuation command

> Open `START_HERE.md`, read `CONTINUE_HERE.md`, `PROTOCOL.md`, `AUDIT.json`, `PROOF_BOUNDARIES.md`, and `BELL_EXTERNAL_INTERFACE.md`, restore certified v0.8.0, preserve every proof boundary and all v0.7 source hashes, and continue from the explicit invariant shell–jet closure problem: derive a computable divisor-upward / jet-downward closure formula for `InvariantShellJetSet` and prove it equivalent to the abstract minimal invariant mask; keep Bell external and do not revive the rejected naive integral normal form.
