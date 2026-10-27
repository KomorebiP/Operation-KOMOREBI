# Self-review

Primary verdict: proved as written in the scoped Lean statements.
This is author self-review plus Lean checking, not independent specialist review.

| Obligation | Result |
| --- | --- |
| Quantified objects are genuine PadicInt scalars and residue rings | Passed |
| d>0, m>=1 and unit prefix enforced | Passed |
| Scalar derivative norm is v_p(d), not assumed invertible mod p | Passed |
| Hensel's strict squared-derivative inequality derived | Passed |
| Smaller closed-ball membership derived from exact local norm scaling | Passed |
| Finite witness is lifted from its actual least representative | Passed |
| Unit status follows from the prescribed positive prefix | Passed |
| Root retains prefix m through the stronger prefix k | Passed |
| No all-depth hypothesis used to prove the effective horizon | Passed |
| Existence and unique existence distinguished | Passed |
| A horizon witness may die above H | Passed, explicit formal control |
| Matrix consequence reaches actual matrix-ring Units | Passed |
| Arbitrary matrix image criterion | Not addressed |
| Simultaneous arithmetic local conditions and automorphy | Out of scope |

Dependencies: integral scalar polynomial expansion and p-adic norm laws -> local
scaling -> Mathlib Hensel theorem -> exact deep-prefix image -> uniform scalar
horizon -> coordinatewise diagonal matrix units. No circular dependency on the
v0.36 compactness statement occurs. The all-depth corollary follows after the
effective existence theorem.

The finite tests compare all declared target-prefix pairs, including absent
roots. The optimized certificate is compared with a separate full finite-ring
enumeration. Integer digit lifts are deterministic examples, not exhaustive
coverage at the higher precision. Python is not Lean-extracted code.

The manuscript was proofread in self-review mode for matching exponents,
quantifiers, coefficient domains and declaration names. No universal matrix
claim or optimal-horizon claim is made. The exact next missing implication is
the noncommutative integral local-image estimate stated in RESEARCH_BOUNDARY.md.
