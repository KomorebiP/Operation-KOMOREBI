# Formalization scope: 11 new universal coefficient theorems

H12CubicDivisorGrowth proves positive ceiling pivot, chamber multiplicity,
all positive-integer zero and pole families, injectivity, disjointness, bounded
integer-coordinate boxes and absence of the origin in these families.

H12PrincipalDivisor has 14 inherited declarations copied without modification;
they are freshly recompiled and included in the transitive axiom audit.
Thus the local clean run checks 25 constants, 11 of them new. No cumulative
whole-program count is claimed as freshly verified.

All are checked with Lean 4.34.0-rc2 and bundled Std, one worker, warnings as
errors. Allowed transitive dependencies: propext, Classical.choice, Quot.sound.
No project axioms, sorry/admit, unsafe or native_decide are permitted. A false
arithmetic control must be rejected.

The identification of these integer coefficients with actual meromorphic
orders is an inherited ordinary analytic theorem. Counting in complex disks,
theta-growth exclusions, canonical products and their convergence, the
fourth logarithmic derivative, reflection normalization and the special-value
cube formula are ordinary proofs, NOT formal Lean analysis in this release.
No original gamma/class-field comparison is asserted or supplied as an axiom.
