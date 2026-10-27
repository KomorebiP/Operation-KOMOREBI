# B70.1. A complete certificate for specified Frobenius pairs

Fix the inherited depth-one finite cover of18 tuples. At a new split test prime
ell>2000, beta is unramified. Write beta(F)=b and the two natural residue rows as
(x,y,z). A tuple alpha=(vw,r,1) requires products

    p_plus, p_minus = b*(v*w*x+r*y+z).

Here w belongs to the coefficient field, not the base residue field. The shared
normalization of mu7 is fixed by the chosen integral cyclotomic prime generator.
All28 inverse-cyclotomic conductor columns are evaluated, with the factor1/2 at
the degree-two primes307,797,1483. Both natural rows and every conductor column are
recomputed independently, including generator norms and Galois covariance.

If BOTH products are zero, bad reduction is a valid alternative. This is true
whether beta(F) is zero or nonzero. We do not need to decide good reduction for
such a tuple. If the products are nonzero, they are coefficient-conjugate in the
present regime. Their unordered pair is completely determined by its F7 trace t
and norm n. For equal scalar products the same statement holds with a double root.

For a good actual pair(A,B), define N1 and N2 to count all rational points on the
smooth projective Frey curve, including its two points at infinity. The reconstructed
quartic is P(T)=T^4-S*T^3+B2*T^2-ell*S*T+ell^2 after the actual twist. Its possible
rank-two correction pair has trace and norm

    t=(S-2(ell+1))/7 mod7,
    n=(B2-2ell-(ell+1)S+(ell+1)^2)/49 mod7.

The integer divisions are checked, not rounded. The needed full residual polynomial
condition is tested before extracting the norm. Both split-place products must
come from ONE actual quartic, never separate members of a union.

## Target-specific algorithm and proof of completeness

Form the set of nonzero target signatures from ALL18 frozen tuples. Keep each
unwitnessed signature active. Generate every residue pair with A^3+B^5 a NONZERO
seventh power. A weighted curve isomorphism is used only to avoid recounting the
same curve. Equation admissibility is checked for every orbit member separately.

For every admissible curve class compute N1 exactly. If its resulting correction
trace matches no active target, N2 cannot refute any required absence claim and is
omitted. Otherwise compute N2 and the full quartic. If an actual quartic realizes
an active signature, retain the curve as an explicit positive witness and remove
that signature from the active set. Subsequent curves need not witness it again.

At the end a target is attainable if it has a witness. For any target left active,
EVERY admissible curve whose N1 trace could match it has been counted to degree2.
The other curves cannot have the required signature because of their exact trace.
Thus an active target's absence is exhaustive, not a failed search. No omitted N2
is claimed computed. The record explicitly labels every omission and null field.

The separate checker regenerates the full equation locus and uses an independent
discrete-log curve canonicalization. It recomputes every N1 using square-root
multiplicities, every required N2 in another quadratic basis, every smoothness gcd,
and the whole active-target schedule. It rejects unjustified omissions, duplicate
or incomplete curve assignments, false witnesses, and incorrect zero-product cases.
No primary arithmetic is imported by that checker.

Primary counting uses norm characters. Secondary counting uses explicit square-root
tables. Coefficient corrections are independently reconstructed by trace/norm root
enumeration in a different F49 basis. The natural phi is never replaced by w.

## Limits

This proves target-specific good existence/absence for the frozen18 tuples. It is
NOT a complete list of all good Frobenius polynomials or all residual-locus pairs
at these primes. It does not construct one global(A,B,C) from separate local
witnesses. The old complete-cover theorem and actual trace-product identity remain
independent inherited mathematical dependencies.
