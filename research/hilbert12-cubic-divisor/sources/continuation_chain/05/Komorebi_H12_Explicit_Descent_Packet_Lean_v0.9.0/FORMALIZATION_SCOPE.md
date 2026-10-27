# Formalization boundary: 41 newly verified theorem constants

* H12ExplicitDescent: 20 universal integral action/carry identities, bilinear
  cocycle algebra, cover-cochain numerator identities, and exact Hodge residues.
* H12DescentPacket: 21 common fixed-residue, primitive-orbit, Weyl phase,
  quadratic lift, and three-class coherence identities.

The integer identities for arbitrary input variables are kernel-checked, not
inferred from bounded numerical tests. The common F3 fixed classification is
a complete finite theorem on 27 residue triples. The projective matrix formulas
are certified by their universal integer exponents; their evaluation at an
actual primitive complex root of unity is an ordinary mathematical implication.

All 41 are compiled with Lean 4.34.0-rc2 and bundled Std, one worker, warnings as
errors. Every theorem's transitive axiom list is inspected. Only propext,
Classical.choice and Quot.sound are permitted where needed. No admitted proof,
custom axiom, native_decide, or unsafe declaration is permitted. The deliberately
false arithmetic statement must fail.

NOT FORMALIZED: holomorphic sheaf cohomology, gerbes, Azumaya descent, analytic
exponentiation, actual gamma cochains, or the main reality/power equality. The
interpretations of the explicit coefficient identities are ordinary proofs.
No claim equates this model with the actual normalized gamma descent.

The 267 inherited declarations and prior evidence remain byte-for-byte in the
predecessor ZIP. They were not freshly replayed. The cumulative source inventory
is 308; 41 is the fresh verification count for this block.
