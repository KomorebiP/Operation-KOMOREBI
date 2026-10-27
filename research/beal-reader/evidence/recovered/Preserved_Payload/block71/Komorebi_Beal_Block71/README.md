# Beal research — Block 71
## Fixed-seven period comparison and a Fermat-quotient constraint

Version 7.1.0, 21 September 2026. The exact Block70 ZIP in predecessor/ is the
sole execution predecessor. Earlier checkpoints remain inside it unchanged.

This block replaces another homogeneous prime sieve by a local comparison at the
fixed prime seven. Under the explicitly inherited actual-model, natural integral
RM, Kummer-normalization and all-depth coefficient hypotheses, write
alpha=(v*w,r,1), v,r in F7*, w^2=5 in the coefficient field. Then

    (2*r+1)^2 = v^2*(3*q7(A)+5)^2 in F7,
    q7(A) = (A^6-1)/7 mod7.

The new proof identifies the actual RM action on the marked local Tate sequence
modulo7 from the period intertwiner, rather than assuming the formal matrix R is
that action. It applies without a conductor bound or a depth-one restriction.
It is NOT a global semilinear Tate-lattice comparison or a proof of Beal.

The eight Block70 coefficient/character patterns all remain possible, but their
previously unspecified A mod49 now lies in twelve residues per pattern. There are
96 augmented (pattern,A mod49) possibilities. Local 7-adic positive families exist.
No new Frobenius point counts, Lean compilation, or independent mathematical
review are claimed. A second finite-arithmetic implementation is included.

Read work71/REPORT.md, TARGET_CONTRACT.md, PROOF_BOUNDARY.md and the notes.
Reproduce new checks (Python standard library only):

    python -B verify.py --report ../Block71_Replay.json

Use --replay-predecessor to additionally rerun the immediate Block70 verifier.
That option is not a fresh replay of all older historical blocks.
