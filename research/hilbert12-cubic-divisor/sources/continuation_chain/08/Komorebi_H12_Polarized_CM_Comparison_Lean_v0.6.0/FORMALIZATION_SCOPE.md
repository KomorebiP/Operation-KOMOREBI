# Formalization scope: 18 new theorems actually verified

The current run freshly compiles and audits:

| Module | New theorem constants | Scope |
|---|---:|---|
| H12CMNormCertificate | 8 | Five denominator-free polynomial reductions, the actual normalized candidate cube identity, its rational scale, and a quotient formula under nonzero denominators |
| H12LineNorms | 4 | Four-line F3 incidence in a commutative ring, norm reconstruction, and a field polarization identity |
| H12PolarizedReality | 6 | Equality of positive-real complex numbers with equal norms, conditional cube and original-value implications, conjugate norm product, and positivity |

The inherited H12CubicBranch dependency is also recompiled. The auditor checks all 18 new declarations and their transitive axiom dependencies, so those inherited branch facts enter only through an actually compiled, audited dependency.

The cumulative source inventory is 172 declarations: 154 inherited plus 18 new. **A full fresh replay of all inherited modules did not complete.** The old evidence remains in the predecessor ZIP and is not claimed as newly reproduced. Verification of the new block succeeds independently of the signed module where the full replay stalled.

The main arithmetic Lean statement assumes only beta^3=7, xi^3=2+3omega, omega^2+omega+1=0 for an explicitly displayed integer polynomial normal form U21. Conversion from the original Gauss/rational formula to U21 is independently checked in Fraction arithmetic and SymPy, not formally derived in this release. No gamma quantity appears in that arithmetic theorem.

The specific involution interpretation, the number-field/subfield interpretation, and the inherited CM and Stark analytic results remain ordinary mathematics. The exact reality of C*U_Gamma^3 is NOT proved. In the formal comparison lemma it is a visible hypothesis alongside modulus, sign, nonzero conditions and a branch bound.

Only propext, Classical.choice and Quot.sound are permitted transitive dependencies. No sorry/admit, custom axioms, unsafe declarations or native_decide appear in the accepted formal sources. Interval routines and the conversion of their data into Lean hypotheses are not formalized.
