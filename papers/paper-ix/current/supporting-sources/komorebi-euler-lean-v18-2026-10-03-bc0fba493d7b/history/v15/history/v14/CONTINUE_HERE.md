# Continue after v14

The generic infinite-series bridge is now compiled, not merely planned.

1. Read PROOF_AND_STATUS.md Section 8 before choosing the next target.
2. Use the actual D=mathlib ℤ_[2] and qeval/HasDerivAt construction in
   RestrictedEvaluation, RestrictedCalculus, RestrictedHensel, RestrictedJets.
3. Formalize the Euler-defined source/kernel/residual convergence and exact
   normalized local identities. CollisionAnalytic proves convergence once an
   exact IsHalfCore identity is supplied; it does not derive that identity from
   Euler numbers. Keep those statements separate.
4. Assemble formal coefficient certificates for the actual Euler source. The
   theorems reval_residue_polynomial and rjet_residue_polynomial transfer them
   without discarding the infinite tail. Finite vector samples are insufficient.
5. The full closed-disc last-coefficient preparation and analytic translation
   tree are not finished. Do not substitute local formal first-order preparation.
6. The terminal-129 and terminal-161 critical-scalar question remains research.
   Hensel lifting at a simple residue cannot settle a persistent multiple residue.

Run scripts/replay.py against the pinned portable runtime in a NEW evidence and
build directory. Preserve history/v13. Use no sorry, native_decide, custom axiom,
or invalid change of theorem hypotheses. A standard-axiom audit is necessary but
not sufficient for an end-to-end claim: inspect each conclusion and assumptions.
