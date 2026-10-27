# Adversarial self-review

This is self-review by the same assistant, not independent human or agent review.

1. Convention check: F=Gamma(5(z+t);5t,5s)/Gamma(z+t;t,s)^5.
   Positive gamma has zero order +1 in the strictly positive cone and pole order
   -1 in the nonpositive cone. These signs give +4 at tau and -4 at s for F.
2. The complete principal divisor computation tests all seven shifts independently
   in Fraction coordinates; its unique integral lift agrees with the ceiling
   formula for negative and positive coordinates.
3. The scalar period shift is beta=-15s-2, NOT 2-15s. The integer -2 disappears
   by periodicity, but is retained in the algebraic checks.
4. The R7 zero anchor uses a ratio of pole leading coefficients and the exact
   midpoint gamma value. It does not infer a scalar from identical divisors.
5. The conjugate-field argument uses actual complex conjugation. It is not a
   statement about the involution fixing beta in the ray field. Its obstruction
   applies to the global meromorphic quotient, not to the rational point 1/3.
6. The regularity condition for the prior Fourier theorem remains unproved for
   the actual relative comparison. The finite model has not been assigned a
   meromorphic section just to force the desired identity.
7. No high-precision residual is treated as zero. The exact orders have ordinary
   proofs and universal integer Lean certificates; numerical probes are labelled
   asymptotic diagnostics with their own 1e-3 threshold.
8. Twenty new Lean statements and their full axiom dependencies are freshly
   checked. The inherited chain remains historical evidence in the unchanged ZIP.
