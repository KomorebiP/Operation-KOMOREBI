# START HERE — Komorebi Cross-Radix Rigidity Continuation v0.7.0

This checkpoint extends certified v0.6.0 by closing the explicit Bell-downstream-interface and uniform all-positive-radix common-hull block.

## Mandatory reading order

1. `CONTINUE_HERE.md`
2. `PROTOCOL.md`
3. `AUDIT.json`
4. `PROOF_BOUNDARIES.md`
5. `BELL_EXTERNAL_INTERFACE.md`
6. `src/CrossRadixBellCommonHull.lean`

The exact v0.6.0 continuation ZIP is retained under `frozen_v0_6/`. All 29 v0.6 source files remain byte-identical.

## Certified v0.7.0 increment

Given an explicit `BellDownstreamInterface a` with transient `N`, period `T>0`, and degree bound `d`, Lean constructs one fixed submodule

`CommonHull N T d ≤ (ℕ → ℂ)`

and proves:

- every positive affine section `n ↦ m*n+r` of `a` lies in this hull;
- therefore every depth/address of every positive radix lies in the same hull;
- the hull is itself invariant under every positive affine section;
- `finrank CommonHull ≤ N + T*(d+1)`.

Bell remains external and is source-audited separately. No naive base-independent integral normal form is revived.

## One-line continuation command

> Open `START_HERE.md`, read `CONTINUE_HERE.md`, `PROTOCOL.md`, `AUDIT.json`, `PROOF_BOUNDARIES.md`, and `BELL_EXTERNAL_INTERFACE.md`, restore certified v0.7.0, preserve every proof boundary, keep Bell external, and continue with the active-shell / shell-jet minimal-hull sharpening; do not re-prove the closed rank/nullity or uniform common-hull blocks and do not revive the rejected naive integral normal form.
