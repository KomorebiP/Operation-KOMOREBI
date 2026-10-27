# START HERE — Komorebi Cross-Radix Rigidity Continuation v0.9.0

This checkpoint extends certified v0.8.0 by closing the explicit shell–jet transition and invariant-mask classification block.

## Mandatory reading order

1. `CONTINUE_HERE.md`
2. `PROTOCOL.md`
3. `AUDIT.json`
4. `PROOF_BOUNDARIES.md`
5. `BELL_EXTERNAL_INTERFACE.md`
6. `src/CrossRadixExplicitShellJetClosure.lean`
7. `src/CrossRadixShellJetTransition.lean`
8. `src/CrossRadixShellJetNecessity.lean`
9. `src/CrossRadixShellJetClassification.lean`

The exact v0.8.0 continuation ZIP is retained under `frozen_v0_8/`. All 36 v0.8 source files remain byte-identical.

## Certified v0.9.0 increment

Lean now proves the exact affine DFT transition law, polynomial Hasse-jet transition law, sufficiency of divisor-upward / jet-downward shell closure, necessity of both closure directions for invariant shell masks, and the equality

`InvariantShellJetSet hT H = ExplicitShellJetClosure (ActiveShellJetSet hT H)`.

Thus a shell/jet block `(g',q)` belongs to the canonical invariant mask exactly when some active block `(g,j)` satisfies `g ∣ g'` and `q ≤ j`.

This is a classification theorem for the minimal positive-affine-invariant **shell/jet zero-mask envelope**. It is not identified with the generally smaller absolute linear orbit hull.

## One-line continuation command

> Open `START_HERE.md`, read `CONTINUE_HERE.md`, `PROTOCOL.md`, `AUDIT.json`, `PROOF_BOUNDARIES.md`, and `BELL_EXTERNAL_INTERFACE.md`, restore certified v0.9.0, preserve every v0.8 source hash, and continue from the orbit-hull versus explicit invariant shell–jet envelope gap: characterize equality and strictness and seek a finite effective active-support criterion; keep Bell external and do not revive the rejected naive integral normal form.
