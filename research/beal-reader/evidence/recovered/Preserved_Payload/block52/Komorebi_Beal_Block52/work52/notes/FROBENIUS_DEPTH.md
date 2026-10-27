# Frobenius orders and the actual stable-lattice depth

This note proves B52.1--B52.4. Arithmetic applications use the input contract
H in `../TARGET_CONTRACT.md`.

## 1. An integral determinant obstruction

Let O be the ring of integers of an unramified quadratic extension E/Q_7.
Suppose an integral matrix is

    M = [[a,b],[7^n c,d]],    a = d = 1 mod7,    n>=2.

Then

    det_E(I-M) = (1-a)(1-d)-7^n b c in 49 O.                 (1)

This is an ideal-membership identity, not a test of a trace modulo49.
Restriction of scalars gives

    det_Q7(I-M) = Norm_E/Q7(det_E(I-M)) in 7^4 Z_7.          (2)

Indeed, write det_E(I-M)=49z. Its norm is 49^2 Norm(z), with
Norm(z) in Z_7. In the integral basis 1,phi, phi^2=phi+1, the norm is
Norm(u+v phi)=u^2+uv-v^2. Equations (1)--(2) prove B52.1 uniformly.

At n=1 the conclusion need not hold. The invertible matrix
[[1,1],[7,1]] has det_E(I-M)=-7 and rational norm49, not divisible2401.
The matrix [[1,1],[49,1]] attains equality in (2). These are algebraic
boundary controls, not Frey representations.

## 2. Passing to an actual good reduction

Let v be a good place of J outside the ramification of nu, and write Q=Nv.
If Q=1 mod7, both residual diagonal entries of rho(Frob_v) are 1. Under
H3, n>=2 therefore gives

    7^4 divides #J^nu(F_Q),                                (3)

where J^nu denotes the local unramified quadratic twist. The identity
#J^nu(F_Q)=det_Q7(1-rho(Frob_v)) follows from the usual Frobenius
cardinality theorem. It is essential to use the norm of the rank-two
determinant: J is an abelian surface, not an elliptic curve. This proves
B52.2 under H2--H3 and good reduction.

For a split rational prime q, Q=q. For an inert rational prime q, Q=q^2:
one must square rational Frobenius before applying the quadratic twist.
Both implementations check this convention separately.

## 3. The prime 29: a proof without a finite search

The prime29 splits in K, nu(Frob_v)=+1, and Q=29=1 mod7. If 29 does not
divide C, the actual curve has good reduction. The Weil bound for an
abelian surface gives

    0 < #J^nu(F_29) <= (1+sqrt29)^4 < 7^4,

since sqrt29<6. This contradicts (3). Consequently

    n>=2  implies  29|C.                                   (4)

This implication does not assume ordinary multiplicities or a bound on n.
It also does not assert that 29|C implies n>=2. Good29 forces n=1.

The genus-two Weil bound used here is a classical source input, not a new
result. Its exact source and the Frobenius convention are recorded in
`../source_records/SOURCE_CHECK.md`.

## 4. The exact finite reduction at 43 and 71

For each q, the complete set of good equation residues is

    R_q = {(a,b) in F_q^2 : a^3+b^5 in (F_q^*)^7}.           (5)

This is a necessary condition for the integer equation with q not dividing
C. It is not sufficient for a global solution. All pairs in (5) are checked
for squarefreeness of the sextic by an independent polynomial gcd.

For a smooth monic sextic let N1 and N2 count the smooth complete curve over
F_q and F_q^2, including its two rational points at infinity. Set

    s1=q+1-N1,
    s2=(s1^2-q^2-1+N2)/2,
    Pq(T)=T^4-s1 T^3+s2 T^2-q s1 T+q^2.

At an inert prime the squared-root polynomial has first two coefficients

    s1'=s1^2-2s2,
    s2'=s2^2-2q s1^2+2q^2.

Write s1',s2' for s1,s2 in the split case as well, and Q=q^f. The order of
the twist is

    #J^nu(F_Q) = Q^2+1+s2' - nu(v)(Q+1)s1'.                (6)

The residual semisimplification under H2 requires the twisted polynomial
modulo7 to be (T-1)^2(T-Q)^2. At all four primes here Q=1 mod7, so the
required polynomial is (T-1)^4.

The complete certificate gives the following histogram. Each entry counts
pairs, not orbits or representations.

| q | f | nu | pairs in R_q | v7(order)=0 | v7(order)=2 | v7(order)=4 |
|---:|---:|---:|---:|---:|---:|---:|
| 13 | 2 | -1 | 156 | 152 | 0 | 4 |
| 29 | 1 | +1 | 116 | 108 | 8 | 0 |
| 43 | 2 | -1 | 258 | 222 | 36 | 0 |
| 71 | 1 | -1 | 710 | 710 | 0 | 0 |

At43 no good admissible pair satisfies (3), hence

    n>=2 implies 43|C.                                    (7)

At71 no good admissible pair even has order divisible by7. The required
residual eigenvalue1 is therefore absent, contradicting H2. Thus

    71|C                                                   (8)

on the inherited reducible branch, for every depth n.

Together (4), (7), and (8) give

    283290 | C,
    n>=2 implies 353262630 | C,                            (9)

where 283290=3990*71 and 353262630=3990*71*29*43. These are branch-conditional
necessary divisibilities. They do not bound C above and do not exclude a
solution with those divisors.

## 5. Why the finite certificate is exhaustive

The change X -> uX, Z -> u^3 Z gives an isomorphism between parameters
(A,B) and (u^5 A,u^3 B). It permits computing Pq once per weighted orbit.
However A^3+B^5 scales by u^15, which need not be a seventh power.
Equation-admissibility is consequently tested separately for EVERY member.

The first implementation counts 164 curve orbits and records all 1240
admissible members. It checks that their disjoint union equals the direct
set (5). Its quadratic character over F_q^2 is computed through the norm.

The independent implementation does not enumerate orbits. It starts with
(5), counts all1240 pairs directly, uses explicit square-root tables in a
different quadratic-field model, and checks every curve's smoothness.
It also computes squared Frobenius by Newton identities rather than the
closed formula, and nu from the defining radicand rather than the
cyclotomic character formula. The two results agree for every pair.

The reduction (5), point-count formula, exhaustive loops, and exact integer
comparisons supply the finite part of the proof. A success count alone
would not supply those logical reductions.

There is no good-reduction assertion at q|C. The primitive residues
(A,B,C)=(-1,1,0) survive at every auxiliary q. This is why the conclusions
are divisibility restrictions rather than contradictions for arbitrary C.
