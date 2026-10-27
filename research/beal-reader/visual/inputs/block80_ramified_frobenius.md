# B80.4. Correctly normalized beta-values at its own conductor primes

The inherited beta descends to gamma in H1(Q,F7(chi^-1)) in the frozen all-inert
regime. Let M=Q(zeta7). Its additive restriction has inverse-cyclotomic covariance.
The complete beta conductor is fixed. All extra rational divisors of C unramified
in beta remain allowed, but new beta ramification would add columns everywhere.

## Normalization

At a conductor r, put f_r=1 for r=1 mod7 and f_r=2 for r=-1 mod7. The old primitive
residue generator gives z_r=g_r^((r^f_r-1)/7) and ell_r(g_r)=1 mod7. Residue primes
are indexed by zeta7 -> z_r^b. Coefficients at those primes are b*s_r. At degree2,
use b in{1,2,3}, one representative per Frobenius pair; using all six requires a
factor1/2. Both implementations retain that orbit convention.

For a rational conductor q=1 mod7, choose an integral generator pi_q of norm q
that vanishes at z_q. The coefficient vectors in1,zeta,...,zeta^5 are:

|q|pi_q coefficients|
|---:|---|
|197|0,1,2,0,2,0|
|337|-1,1,-1,3,-1,1|
|547|-2,-2,0,0,-2,1|
|673|-1,3,-1,1,-1,1|
|743|-3,1,-1,-3,1,-3|
|883|0,3,0,2,0,4|
|1933|-1,2,3,0,1,0|

Exact norm=q proves the principal ideal is ONE prime, not an unspecified product.
The primary checks multiplication determinants. The separate program multiplies
all six conjugates in the cyclic group ring.

## The self-conductor contribution cannot be dropped

At the chosen q-place, write pi_q=q*u_q with u_q a unit, using q as uniformizer.
Norm(pi_q)=q implies

    ell_q(u_q)=-sum_(b=2)^6 ell_q(pi_q(z_q^b)).             (12)

Principal reciprocity on pi_q therefore gives its self-column, for the value on
the rational local uniformizer,

    D_(q,q)=sum_(b=2)^6 (1-b)ell_q(pi_q(z_q^b)).           (13)

For r!=q the column is

    D_(q,r)=-sum_(b in reps_r) b*ell_r(pi_q(z_r^b)).       (14)

Together these determine gamma at the local q-Frobenius in the abelianized
cyclotomic local group with uniformizer q. They are not a good-reduction test.
Every conductor component is included, including q itself. The sign is the
same principal-idele convention as the inherited Frobenius rows.

The independent check constructs an actual root ztilde of Phi7 modulo q^2 by
one Hensel step. It then computes u_q=pi_q(ztilde)/q modq DIRECTLY. This verifies
(12)-(13) without using the norm relation to assign the missing local unit.

## Transfer to K and conversion of inertia coordinates

Since q is inert in K/Q, at q=1 mod7 the K-Frobenius value is

    b_q=beta(F_(K,q))=2 sum_r D_(q,r)s_r.                 (15)

The factor2 belongs to unramified quadratic restriction. At q=-1 mod7 the
compatible squared rational Frobenius has beta-value0, by the cocycle identity
(1+chi(q)^-1)gamma(F_q)=0. The rational uniformizer labels are used consistently.

The ordinary-character inertia generator g_q used in Block79 differs from the
frozen twisted convention. Its beta-value is

    c_q=s_q*ell_q(Norm_(Fq2/Fq)(g_q))     if q=1 mod7,
    c_q=s_q*ell_q(g_q)                   if q=-1 mod7.     (16)

The exact conversion factors, in increasing prime order, are

    197:5,307:2,337:5,547:4,673:1,743:1,797:4,883:3,1483:1,1933:1.

Setting c_q=s_q without this conversion would mix local Artin normalizations.
Both programs reproduce the factors and every b_q in primary80.json.

The constraint c_q*z(F_q)-b_q*z(I_q) is invariant when a Frobenius lift is changed
by T^m, since both b_q and z(F_q) change by the corresponding inertia terms.
The exact Frobenius-lift identity is tested in12348 prime-field cases. This
invariance does NOT allow discarding the self-conductor unit or changing only
one of the conventions.
