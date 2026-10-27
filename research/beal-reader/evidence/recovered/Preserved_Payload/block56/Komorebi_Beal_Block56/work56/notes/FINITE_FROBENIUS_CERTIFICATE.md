# The exact Frey reductions at 197 and 491

## Curve, good locus, and Frobenius convention

The specific inherited genus-two curve is

    Z^2 = X^6 + 10 B X^3 + 12 A X + 5 B^2.

For q not dividing 2*3*5*7*C, its admissible equation residues lie in

    R_q = {(a,b) in F_q^2 : a^3+b^5 is a nonzero seventh power}.

This is a necessary local condition, not a test for global solutions. Both
programs generate this complete set. The independent implementation also
checks that the sextic and its derivative are coprime at every pair.

Let N1,N2 be the complete curve counts over F_q,F_(q^2), including both
points at infinity. For

    s1=q+1-N1,
    s2=(s1^2-q^2-1+N2)/2,

rational Frobenius has polynomial

    T^4-s1 T^3+s2 T^2-q s1 T+q^2.

At an inert prime, square its roots before twisting. The inherited quadratic
twist has value -1 at both 197 and 491. The primary program evaluates this
using the cyclotomic formula. The independent program uses the defining
radicand 3(5-sqrt5)/2. These give the same signs.

The curve/Jacobian trace formula is Milne, Abelian Varieties, III.11.1,
printed page 118. The order formula is II.1.1, printed page 75. Both actual
pages were inspected. The Frey construction and twist identification remain
explicit inherited inputs rather than consequences of these general sources.

## B56.2. Good 197 excludes depth at least three

The prime 197 is inert in K. There are exactly 5,516 pairs in R_197,
partitioned into 197 weighted isomorphism orbits. Every counted curve has
s1=0. Write its rational polynomial as

    P_197(T)=T^4+b T^2+197^2.

After base extension and the negative twist, the local polynomial is

    P_v(T)=(T^2-b T+197^2)^2.

Modulo 49, comparison with the required target forces

    b = Q+1 = 2 mod 49.

Exactly two weighted orbits, comprising 56 admissible pairs, survive. Their
values are

    b=2 or b=296.

Modulo 343, the necessary condition is instead

    b = Q+1 = 51 mod 343.

Neither value qualifies. The coefficient of T^3 already detects the failure,
since 2 is invertible modulo 343. Thus no good equation residue meets the
necessary depth-three congruence. Applying B56.1 gives

    n>=3 implies 197 divides C.

No ordinary-multiplicity or prime-support assumption is used.

## B56.3. Good 491 excludes every depth at least two

The prime 491 splits in K. There are exactly 34,370 pairs in R_491,
partitioned into 495 weighted orbits. First impose the residual polynomial
condition modulo 7. Exactly seven orbits, comprising 490 pairs, survive.
Their rational Frobenius traces lie in

    s1 in {-25,10,24}.

The twist is negative. Thus their twisted rational traces lie in

    {-24,-10,25}.

At depth at least two, B56.1 requires the underlying four-dimensional trace

    2(Q+1)=984=4 mod 49.

The three surviving trace values are 25,39,25 modulo 49, none equal to 4.
Consequently no good equation residue meets the depth-two congruence:

    n>=2 implies 491 divides C.

In particular, the result is not inferred from failure of an abstract ray
presentation. It is an obstruction for the good reductions of this exact
Frey curve, coupled to the actual diagonal congruence.

## Complete certificate summary

The modulus columns count pairs whose complete twisted polynomial agrees
with (T-1)^2(T-Q)^2, not representations or integer solutions.

| q | All good equation pairs | Modulo 7 | Modulo 49 | Modulo 343 |
|---|---:|---:|---:|---:|
| 197 | 5,516 | 840 | 56 | 0 |
| 491 | 34,370 | 490 | 0 | 0 |

## Why the staged enumeration is complete

The transformation (A,B) -> (u^5 A,u^3 B) gives an isomorphism of the curves
by scaling X and Z. The equation sum scales by u^15. It need not preserve
seventh-power admissibility, so admissibility is checked for every member,
not just the curve representative.

For 491, a failure of the degree-one twisted trace condition modulo 7 already
rules out the required polynomial. Such an orbit does not need N2. Exactly
69 of its 495 orbits pass this first filter. All 197 orbits at the inert
prime require N2, because rational trace alone does not determine the trace
of squared Frobenius. The production counts are therefore:

    692 degree-one counts; 266 degree-two counts;
    complete coverage of 39,886 good equation pairs.

A rejected early-stage row has N2=null, not a fictitious point count or a
claimed full-polynomial computation. Every such rejection follows from an
explicit necessary trace condition.

## Independent implementation

The primary uses F_q[w]/(w^2-d), quadratic characters through norms, weighted
orbits chosen by their smallest pair, and the closed squared-root formula.

The independent program imports no primary arithmetic. It uses
F_q[theta]/(theta^2+theta+1), explicit square-root multiplicities, and a
different orbit normalization: cubing is bijective at both primes, so B can
be normalized to 1 when nonzero. B=0 is handled by fifth-power cosets.
It generates all 39,886 admissible pairs directly and compares the resulting
counts and polynomials at every pair through these independently constructed
canonical orbits. It performs 39,886 polynomial-gcd smoothness checks and
uses Newton identities for squared Frobenius and radicands for the twist.

This is independent implementation, not independent mathematical review.

## Necessary controls

The 56 modulo-49 survivors at 197 are retained. They prevent relabeling the
197 result as a depth-two exclusion. The 490 residual survivors at 491 are
also retained. The result does not eliminate depth one.

At either prime, (A,B)=(q-1,1) has A^3+B^5=0. It is outside the good locus.
No point-count exclusion at q is used when q divides C.

Generic Weil polynomials can satisfy the same congruences. For example,
(T^2-2T+491)^2 satisfies the modulo-49 condition and has order 490^2. At
norm 197^2, (T^2-51T+197^2)^2 satisfies the modulo-343 condition. Their roots
have the appropriate absolute values. These are compatible polynomials,
not claimed Frey reductions. Their existence shows why the actual curve
counts, rather than the Weil bound alone, are essential.
