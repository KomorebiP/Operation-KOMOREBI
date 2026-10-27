# B62.2. Correctly twisted Frobenius values and actual good-reduction traces

## Complete conductor and descent

First stipulate that all beta ramification lies over

    S={197,883,1373,1667}.

Each rational prime is inert in K/Q and1 mod7. The inherited inertia-injectivity
and split-at-seven condition therefore descend beta uniquely AS A COHOMOLOGY
CLASS to gamma in H^1(Q,k(chi^-1)), exactly as in B61.2. That proof has no
hypothesis n=2. It uses the stated complete conductor and the class-group input,
not descent of the underlying Frey representation or its natural class alpha.

Over M=Q(zeta7) this is an additive ray character with covariance chi^-1.
Index conductor primes by zeta7 -> r_q^b for b=1,...,6. Their coefficients are
b*s_q, not constant coefficients or b^-1*s_q. With residue logarithms base2
at the four support primes, an integral generator pi_ell of a prime of norm ell
gives the arithmetic Frobenius row

    R_ell,q = -sum_(b=1)^6 b*log_2(pi_ell(r_q^b)) mod7.     (4)

The sign is the principal-idele convention. Reversing it consistently merely
negates all inertia coordinates. The residue root used to evaluate the natural
Kummer class is the root of pi_ell in F_ell. Thus (4) and the natural logarithms
use compatible roots of unity, not independent arbitrary local scales.

At ell=43, which is inert in K, beta(Frob_K)=2 gamma(Frob_Q), because chi(ell)=1
mod7. The natural Kummer values also use the norm ell^2, not ell. Both factors
are included, rather than cancelling or omitting one of them.

## Integral prime generators

In the basis 1,zeta,...,zeta^5, in addition to Block61's seven generators use

    norm43:  (-1,-1,-1,-1,-1,1)
    norm211: (-2,-2,-2,-2,1,-1)
    norm239: (-2,-2,0,-1,-2,1).

The norms are checked as exact positive integers. The primary uses multiplication
determinants. The independent program substitutes theta=zeta^-1 and multiplies
all six conjugates in the cyclic group ring. No numerical norm is used.

Columns below are197,883,1373,1667. The six Frobenius rows are

    29:  (4,2,6,1)
    43:  (4,3,4,3)
    71:  (6,2,0,5)
    211: (2,4,1,5)
    239: (3,3,1,2)
    491: (3,6,1,6).

At71, beta is locally zero:71 divides C in the inherited reducible branch at
EVERY depth, and both phi residues fail seventh powering. B61.1 with eta_1=1
therefore supplies R_71*s=0. We do NOT impose R_29*s=0 or R_491*s=0 without
checking their good/bad alternatives. Those primes are not forced bad at n1.

The natural rows for coordinates(phi,3,sqrt5) are

    29:  (4,1,5), (3,1,5)
    43:  (0,2,4)
    71:  (5,6,0), (2,6,0)
    211: (1,4,5), (6,4,5)
    239: (5,4,6), (2,4,6)
    491: (6,4,2), (1,4,2).

The single inert43 row already evaluates residues in F_(43^2). Its beta
Frobenius factor2 is imposed separately. The coefficient-field symbol w is
never substituted for the base-field sqrt5 in these calculations.

## Actual finite curve counts

The counted untwisted Frey family is

    z^2=x^6+10 B x^3+12 A x+5 B^2.

At a good rational prime ell, every integer solution supplies a pair(a,b) with
a^3+b^5 a NONZERO seventh power modulo ell. This complete necessary locus is
counted member by member. Weighted curve isomorphisms do not in general preserve
seventh-power admissibility; every member is checked separately.

For the complete curve counts N1,N2, including the two points at infinity,
put s1=ell+1-N1, s2=(s1^2-ell^2-1+N2)/2. The rational polynomial is
X^4-s1X^3+s2X^2-ell*s1X+ell^2. At43 its roots are squared before twisting.
At split29,211,239 the twist is positive; at inert43 and split491 it is negative.
The independent program derives these signs from delta=9-3phi and uses Newton
identities for the base extension.

|ell|all good equation pairs|degree1 counts|degree2 counts|full residual pairs|
|---|---:|---:|---:|---:|
|29|116|29|7|8|
|43|258|45|45|36|
|211|6330|217|31|210|
|239|8126|239|36|170|
|491|34370|495|69|490|

These are49200 pairs,1025 degree1 counts and188 degree2 counts in EACH
implementation. The new primes211,239 account for14456 pairs; the other34744
are fresh reproductions of earlier data. At split primes a failure of the
necessary degree1 trace test modulo7 needs no degree2 count. Such N2 entries
are explicitly null, not represented as completed counts.

With w^2=5 in the coefficient residue field, the complete possible correction
sets on the residual locus are

    G29  = {2}
    G43  = {3,4,5}
    G491 = {5, 5+/-w, 5+/-2w, 5+/-3w, 6+/-w}
    G211 = {0,6, 3+/-w, 1+/-3w, 3+/-3w}
    G239 = {+/-w, 1+/-w, 2+/-w, 3+/-3w}.

In particular G491 intersects F7 in {5}, G211 intersects F7 in {0,6},
and G239 has NO F7 elements.

All coefficients, rows, residues and orbit members are in verification/pointcounts.json
and trace_product.json. The independent program uses different quadratic fields,
direct square-root multiplicity tables, discrete-log canonical curves, and49-element
trace/norm enumeration. It verifies all49200 smoothness gcds and every member's
assignment. It imports no primary arithmetic.
