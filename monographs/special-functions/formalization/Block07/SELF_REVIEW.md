# Focused self-review: SF-LEAN-B07

Primary verdict: **proved as written**, for the characteristic-exponent and
matrix prerequisites in CoupledCharacteristic.lean, at the source digest bound
by declarations.json and the pinned replay receipt. This is self-review at
base `ac74a88377d7c5a4daa8bc463d3f45629277e192`, not independent review or
a verdict on the whole analytic growth theorem.

## Claim card and dependency graph

Objects: labeled real scales 0<q,r,a,b<1, positive real exponents, the real
matrix P(t) with rows (q^t,r^t) and (a^t,b^t), and its entrywise extension to
complex scalars. Conclusions: unique positive determinant-balance root;
positive right and left eigenvectors; max-normalized right vector; exact
complex spectrum at the root; spectral radius one iff the determinant equation
for positive t; uniqueness of the spectral exponent. Powers are real powers.

Positive-base power bounds -> continuous balance, strict monotonicity on
[0,infinity), endpoint values -> IVT and unique positive root. The balance
equation -> explicit right/left identities -> normalized right identity.
Determinant algebra -> exact spectrum {1,q^t+b^t-1} at a root -> radius one.
For the converse: positive off-diagonal product -> reality of eigenvalues;
finite nonempty complex spectrum -> attained norm maximum; radius one ->
real eigenvalue +/-1; strict contractions exclude -1 -> determinant equation.
No root-existence result is used to assume the converse spectral identity.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Real exponent convention | passed | Real-valued balance/matrix; explicit real-to-complex scalar extension |
| Exact domain | passed | Strictly positive scales below one; uniqueness only among positive exponents |
| Boundary t=0 | passed | H(0)=-1; IVT endpoint excluded explicitly |
| Product monotonicity | passed | Both factors nonnegative on t>=0; strictness supplied by the subtracted decreasing power |
| Limit and existence | passed | Three real-power limits; an actual finite sign-change interval; IVT |
| Matrix orientation | passed | Right vector uses r^t; left vector uses a^t and the transposed matrix |
| Normalization | passed | Positive maximum, positive inverse factor, max exactly one; not sum normalization |
| All eigenvalues accounted for | passed | Matrix spectrum iff characteristic polynomial root; explicit quadratic factorization |
| Second eigenvalue signs | passed | Absolute value below one, allowing negative values; rational fixture gives -1/10 |
| Converse spectrum reality | passed | Imaginary-part equation and positive off-diagonal product rule out nonreal roots |
| Norm attainment | passed | Nonzero characteristic polynomial gives a finite spectrum; complex algebraic closure supplies nonemptiness |
| Exclusion of -1 | passed | Positive diagonals and off-diagonal product below one contradict its determinant equation |
| Actual spectral-radius API | passed | Mathlib spectralRadius over the complex matrix, with its ENNReal codomain |
| Dependency/I/O freshness | passed | Nine package revisions, source hashes before/after replay, exact logs and I/O inventory |
| Additional axioms/placeholders | passed | Source guard, exact axiom inventories and kernel replay; placeholder only in rejected control |
| Analytic order/type bounds and Perron type proportions | out of scope | These remain unformalized, despite the now-checked exponent and matrix prerequisites |

The positive root is obtained on [0,T], not on an unspecified connected
domain. No use of monotonicity extends it to negative exponents. All inverse
factors in the normalized vector have an explicit positive normalizer. The
left vector is not accidentally claimed to satisfy the untransposed right
equation; a control rejects that error for the nonsymmetric rational tuple.

The exact spectrum is over complex scalars, so the finite maximum argument
does not silently substitute the real spectrum. Algebraic closure is supplied
by the pinned complex-polynomial instance. Reality of the two eigenvalues is
then proved from positivity, rather than assumed from a positive real matrix.
The conversion from nonnegative norms/ENNReal radius to real modulus is made
explicit before the +/-1 argument.

External leaves are exact pinned Mathlib proof APIs for real powers and their
limits, IVT, polynomial roots and characteristic polynomials, complex
algebraic closure, finite compact sets, and the spectral-radius supremum.
The actual types are consumed by checked proof terms. Cache preparation did
not change their Git revision; cached imports are not freshly replayed. No
load-bearing numerical computation or unchecked external citation is used.

No implication is missing in the stated characteristic-section target.
The strongest safe result is that section's complete exponent/vector/spectrum
contract. It does not identify rho with the growth order of U or V. The next
check is the positive-real lower comparison used in Theorem F.2.
