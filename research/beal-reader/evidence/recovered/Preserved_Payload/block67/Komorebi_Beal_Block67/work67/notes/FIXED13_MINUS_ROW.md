# B67.5. A correctly twisted fixed13 relation for the minus component

## Scope and normalization

Use the two rational classes supplied by the all-depth semilinear theorem:

    beta=res gamma_+ + w res gamma_-,
    gamma_- inH1(Q,F7(chi^-1 epsilon5)).

For this note additionally REQUIRE actual local beta-zero at13. It is known
at n1,n2 and when the earlier full eta_n=1 argument applies. It is NOT deduced
for arbitrary n>=3 with nontrivial eta by the new all-depth theorem.

Then gamma_- is locally zero at13: restriction toK at this inert place has
degree2 and is injective on seven-primary cohomology. Its unramified rational
Frobenius action on the coefficient module is(+1), so the zero value is an
actual condition, unlike the automatically zero plus unramified cohomology.

Let L=Q(sqrt5,zeta7). The restriction of gamma_- toG_L is an additive character
with covariance epsilon5*chi^-1. It is unramified at inert variable primes,
and actual possible ramification is at split rational q=1 modulo7. The inherited
fixed-prime conditions allow no omitted seven-primary inertia at2,3,5,7.

## An explicit integral prime generator

Put phi=(1+sqrt5)/2 and

    pi13=1+phi+zeta7^2.

Its relative norm toQ(zeta7) is1+3zeta7^2+zeta7^4, of absolute norm169. At13,
L has residue degree2. In F169 using phi^2=phi+1, zeta7=8phi is a primitive
seventh root and pi13 vanishes. The two embedding labels(s,b)=(+,1),(-,6)
are Frobenius conjugate and define ONE prime ideal of norm169. Since the
principal ideal has norm169, it is that prime, not a product with hidden factors.

Both algorithms check the norm and residue zero. The independent algorithm
multiplies all12 conjugates in an integral cyclic group ring; no floating
algebraic norm, numerical factorization or class-group guess is used.

## The row and its twist

At every allowed split q choose the least primitive rational generator g_q,
put z_q=g_q^((q-1)/7), and order the two roots ofphi^2-phi-1 as p_+<p_-.
For the prime indexed by phi->p_s, zeta7->z_q^b, the minus inertia coefficient
is s*b*t_q. Under(epsilon,a), the prime label moves to(epsilon*s,b/a), and
this coefficient changes by epsilon*a^-1, as required. Neither constant
weights nor inverse-b weights give the stipulated covariance.

Principal-idele reciprocity for pi13, whose components are units at every
conductor place, therefore gives the necessary equation

    sum_q R13^-(q)t_q=0,
    R13^-(q)=-sum_(s=+,-)sum_(b=1)^6
                   s*b*log_(g_q)(1+p_s+z_q^(2b)) modulo7.             (1)

It is an equation for the MINUS class alone. Adding arbitrary plus-component
ramification cannot change it. Adding a new minus ramification prime DOES add
a column. No claim that(1) is sufficient for the other local conditions or an
actual Frey representation is made.

Conjugating pi13 by(epsilon,a) multiplies the whole row by epsilon*a^-1.
The code checks all12 conjugates at every displayed conductor prime. The
independent code uses inverse zeta roots and direct seventh-power symbols,
not the primary logarithm table.

## Exact bounded table

Every split prime q<=10000 withq=1mod7 and phi a seventh power is in this table.
The natural row is(phi,3,sqrt5), in the SAME residue logarithm normalization.
At ramified beta, alpha=(v*w,r,1), v,r nonzero inF7, so the row must annihilate
that same vector. Its first entry is0 here.

|q|R13^-|natural row|permitted r|
|---:|---:|---|---|
|2269|3|(0,1,1)|6|
|2521|3|(0,2,2)|6|
|2731|5|(0,1,2)|5|
|2969|6|(0,1,4)|3|
|3571|5|(0,1,4)|3|
|3739|4|(0,6,5)|5|
|4481|5|(0,1,6)|1|
|4831|6|(0,1,4)|3|
|5741|5|(0,4,2)|3|
|6091|4|(0,0,3)|none|
|6329|0|(0,1,0)|none|
|6581|1|(0,6,6)|6|
|9521|2|(0,1,6)|1|

No arbitrary coefficient-field descent is used; the nonzero prime-field ratio
is the new actual all-depth theorem. Every minus-ramified split prime is also
beta-ramified: the combined coefficients are inF7 plus wF7, so a nonzero minus
coefficient cannot be canceled by the plus coefficient at both conjugate places.

All11 ratio-compatible columns in the bounded table have nonzeroR13^-. Thus a
nonzero minus character with its COMPLETE ramification bounded by10000 requires
at least two such rational primes, all consistent with the same r. In particular
its complete ramification cannot be a singleton from this table. Absence of all
variable inertia would kill the class by the inherited inertia injectivity.

The first geometrically eligible split prime is2269. If all minus ramification
were below2521, only2269 could occur, which(1) kills. Therefore under the actual
local13zero hypothesis a nonzero minus requires a ramification prime q>=2521.
This is a small LOWER bound, not an upper bound or a nonexistence theorem.

## A necessary-system survivor

The two-place data

    r=6, t2269=1, t2521=6

satisfy(1), since3+3*6=0 modulo7, and both natural rows vanish. They are a
nonzero solution to this NECESSARY row/Kummer system. They have NOT been
proved to satisfy all fixed-prime conditions or realized by one global Frey
Jacobian. Their preservation prevents declaring that the new row always
annihilates the entire minus character.
