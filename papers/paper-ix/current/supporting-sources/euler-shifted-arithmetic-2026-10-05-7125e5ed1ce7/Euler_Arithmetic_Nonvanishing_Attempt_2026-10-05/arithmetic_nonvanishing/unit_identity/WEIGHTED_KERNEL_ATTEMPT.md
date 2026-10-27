# Actual-unit nonvanishing attempt: weighted kernel identities

Base checkpoint: `Euler-coupled-stationarity-20261005`. The checkpoint sources
are unchanged. This attempt targets actual Bernoulli arithmetic rather than
additional parameter digits or stationary geometry.

## Result

An exact weighted Bernoulli convolution does contain the required nonunit
factor4^r. Its complete tail identity also contains a finite cross-boundary
polynomial. The first coefficient of that polynomial cancels the putative
4^r forcing exactly. Omitting that polynomial would create a false
nonvanishing proof.

The identities below are proved. They do not establish that the actual
critical value Phi_r(2^(2r-25)) is nonzero. The precise missing implication is
given at the end.

## 1. Two exact generating-kernel identities

Use t=z^2 and define

    g(t)=z coth z=sum_(n>=0) a_n t^n,
    f(t)=(z/sinh z)^2=sum_(n>=0) beta_n t^n.

Here a_0=beta_0=1 and

    beta_n=(1-2n)a_n.

Differentiation and coth doubling give

    f=g-2t g'=g^2-t,                                         (1)
    g(t)g(4t)=f(t)+2t.                                       (2)

For example, (2) follows directly from
2 coth(z)coth(2z)=coth(z)^2+1.

For n>=2, coefficient comparison proves

    sum_(i=1)^(n-1) beta_i beta_(n-i)/[(2i-1)(2n-2i-1)]
       =[(2n+1)/(2n-1)] beta_n,                              (3)

and, crucially,

    sum_(i=1)^(n-1) 4^i beta_i beta_(n-i)/[(2i-1)(2n-2i-1)]
       =[(2n+4^n)/(2n-1)] beta_n.                            (4)

The weighted term4^n is the same nonunit mode that appears in undepletion.
This is an exact constraint on actual Bernoulli coefficients, not a generic
analytic-unit assumption.

## 2. Complete weighted tail identity

Fix an ordinary integer r>=2 and write

    p_r(t)=sum_(n<r) a_n t^n,
    R_r(t)=sum_(q>=0) a_(r+q)t^q,
    b_r(t)=sum_(n<r) beta_n t^n,
    B_r(t)=sum_(q>=0) beta_(r+q)t^q.

Define the finite polynomial

    C_r(t)=t^-r[p_r(t)p_r(4t)-b_r(t)-2t].                    (5)

The coefficients below degree r vanish by (2), so C_r is a polynomial of
degree at most r-2. Its coefficients are explicitly

    [t^q] C_r=sum_(i=q+1)^(r-1) 4^(r+q-i) a_i a_(r+q-i),
    0<=q<=r-2.                                              (6)

Substituting g=p_r+t^r R_r in (2), and keeping every cross-boundary term,
gives

    B_r(t)=R_r(t)g(4t)+4^r p_r(t)R_r(4t)+C_r(t).             (7)

In particular,

    C_r(0)=[(2r+4^r)/(2r-1)] beta_r,
    [t^(r-2)]C_r=4^(r-1)a_(r-1)^2.                          (8)

Both are nonzero rational numbers. But nonzero forcing is not the same as
uncancelled forcing. At t=0, the allegedly decisive4^r contribution in (7)
is

    4^r a_r=-4^r beta_r/(2r-1),

whereas C_r(0) contains exactly

    +4^r beta_r/(2r-1).

They cancel identically. The surviving constant identity is simply

    beta_r=-beta_r/(2r-1)+2r beta_r/(2r-1).

Thus the candidate stronger lemma "the4^r term is a unique leading
arithmetic forcing term" fails by an exact identity, at its first packet.

## 3. Exact Riccati tail identity

The same kernel satisfies

    2t g'=g-g^2+t.

Define the finite polynomial

    F_r(t)=t^-r[p_r-p_r^2+t-2t p_r'],                        (9)

again of degree at most r-2. The complete equation for the shifted tail is

    2t R_r'=(1-2r-2p_r)R_r-t^r R_r^2+F_r.                  (10)

The factor t^r in the quadratic term is essential: R_r is the shifted tail,
not the unshifted difference g-p_r. At its constant coefficient,

    F_r(0)=-[(2r+1)/(2r-1)] beta_r,

which exactly cancels (1-2r-2p_r(0))a_r. Thus this Riccati forcing also
does not produce a contradiction by isolating its constant term.

## 4. The Newton transfer is an exact operator algebra

For an integral coefficient series A(t)=sum a_q t^q, define the operator

    (T_A h)(x)=sum_(q>=0)8^q a_q P_q(x)h(x-q).

These sums converge in the integral Tate algebra for h in Z_2<x>, because
every coefficient a_q is integral and8^q supplies uniform decay. The
falling-packet identity

    P_i(x)P_j(x-i)=P_(i+j)(x)

and convergent rearrangement prove the exact composition law

    T_A T_B=T_(AB).                                         (11)

Consequently (7) has the exact analytic translation

    T_(B_r) A_source
       =T_(R_r) T_(g(4t)) A_source
         +4^r T_(p_r) T_(R_r(4t)) A_source
         +T_(C_r) A_source.                                (12)

The left side is beta_r H_r. All cross-boundary information survives as
T_(C_r) A_source. Equation (10) translates similarly, including the term

    T_(t^r R_r^2)h
      =8^r P_r(x) [T_(R_r)T_(R_r)h](x-r).                   (13)

These are operator products, not pointwise products. Even an invertible
Newton transfer need not preserve zeros. A minimal exact discriminator is

    h(x)=(x-1)^2,
    h(1)=h'(1)=0,
    (T_g h)(1)=8/3.

Only q=1 contributes: a_1=1/3, P_1(1)=1, h(0)=1, and all q>=2 packets
vanish at1. Thus zero descent cannot follow merely from kernel factorization
or from invertibility of T_g. This example refutes that implication only;
it is not an actual Euler counterexample.

## 5. Index multiplication is a half-shift, not a derivative

The exact identity

    s[P_q(s)-P_q(s-1/2)]=q P_q(s)

does turn coefficient index into an operator. Define

    N h=s[h(s)-h(s-1/2)].

This half-shift is used only on the source-eliminated series, where its
convergence follows from their packet decay. It is not an operator on an
arbitrary integral Tate series defined only on Z_2.

After cancelling the source denominators, N acts diagonally on P_(q-1)
with eigenvalue q-1. Therefore it can translate (1) and (10), but it does
not turn them into an ordinary differential equation in s. Here s is the
global Euler interpolation argument, whereas x in Sections4 and6 is the
residual argument.

The half-shift also has an indispensable branch sign:

    exp(log9/2)=-3,
    9^(s-1/2)=-9^s/3.

Indeed the exponential belongs to1+4Z_2, selecting -3 as the square root
of9. For lambda(s)=9^(s+1), the commutator is

    N(lambda h)-lambda N h=(4/3)s lambda h(s-1/2).            (14)

The parallel source-resummation derivation is written in
`../structural/WEIGHTED_TAIL_TRANSLATION.md`. With its source-eliminated
g-tail numerators u_r,v_r and M_r=(lambda u_r-v_r)/8, the actual Euler
tail satisfies

    Ecal-S_r=-(2N+1)M_r+(s lambda/3)u_r(s-1/2).              (15)

The surviving half-shift term is exact. Dropping it, or selecting the +3
branch, would incorrectly replace the true arithmetic relation by a false
local differential closure.

## 6. Two proposed shortcuts fail on actual admitted families

First, the new root discriminator constructs the actual parameter

    T=22831001499602523078606181325.

A separate actual packet rebuild at320 global bits verifies true terminal
161 and a critical value of exact valuation91 with odd part56399 modulo65536,
hence15 modulo32. The depleted critical value agrees through142 normalized
bits. Evidence is in `../root/unit_filter_run/results.json` and its manifest.
Thus actual Bernoulli arithmetic does not forbid odd valuation together with
leading unit15. This is a nonsingular member:91 is vastly smaller than2r-25.
It does not test the crucial equality between the cancellation depth and r.

Second, the proposed ordinary input x=r+10363 lies on the deep chart with

    Z=(17659+2^18T)2^625.

In this square test, Phi means the actual chart critical value K(c), not the
depleted value Phi_r(0). Every critical center satisfies c=20 mod128, so
v2(Z-c)=2. The exact Morse
normal form gives K(Z)=Phi+w(Z)^2, with v2(w(Z))=2. Whenever v2(Phi)>=7,

    K(Z)=w(Z)^2 [1+Phi/w(Z)^2]

is a nonzero Q_2 square because the bracket lies in1+8Z_2. Thus this natural
r-dependent square test is provably blind on the surviving critical cylinders,
including the actual parameter just displayed. More generally any nonsquare
witness must satisfy

    2v2(Z-c)>=v2(Phi)-2.

It must resolve the critical center to approximately half the unknown
cancellation depth. Merely tying an integer argument to r supplies no such
approximation.

## Exact remaining implication

The kernel identities now retain the arithmetic factor4^r, the finite
cross-boundary forcing, the shifted quadratic term, and the half-shift
commutator. None has yet proved that a hypothetical actual simultaneous
zero violates its prescribed unit filtration.

The missing step is a value/derivative identity for the *actual transformed
tail* whose remaining terms have a strict valuation separation under
G_r=G_r'=0. Kernel identities before transfer do not supply that separation:
(8) exhibits an exact cancellation of the nonunit forcing, and (11)-(15)
retain additional shifted values instead of a smaller actual tail singularity.

Therefore actual nonintersection

    eta_r^* !=2^(2r-25)

remains open. This attempt identifies two concrete invalid proof steps and
provides the exact identities a subsequent cancellation argument must use.
