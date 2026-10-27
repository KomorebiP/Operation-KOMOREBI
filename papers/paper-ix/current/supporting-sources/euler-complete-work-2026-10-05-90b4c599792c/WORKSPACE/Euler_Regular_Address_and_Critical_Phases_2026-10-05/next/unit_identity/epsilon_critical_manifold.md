# Exact epsilon critical manifold for terminal 161

Base: `Euler-address-one-20261005-recenter917`. This note is a new mathematical
reduction, not a proof of Euler simplicity and not a Lean compilation.

## Quantified hypotheses

Fix an ordinary positive integer Euler index `r` with true terminal 161 and
normalization `mu=-154`. Let `gammahat_q` be its depleted normalized packet
scalars. Assume the certified terminal-161 bounds

* `v2(gammahat_0)=154`, with `gammahat_0=2^154`;
* `v2(gammahat_q)>=153` for `1<=q<161`;
* `v2(gammahat_q)>=0` for `q>=161`;

and restricted convergence of the packet series. Put `x=10202+2^15 Z` and
assume the inherited deep quadratic chart, now for the depleted residual,

    Khat(Z)=2^-178 Ghat(x)=a+2 l Z+u Z^2+4 Z^3 R(Z),
    a,l in Z_2, u in Z_2^times, R in Z_2<Z>.

For the certified actual chart at a fixed `r`, this depleted hypothesis follows
from the exact undepletion estimate because `2r-1` is vastly greater than 180.
It is not silently assumed for every terminal-161 multiplier.

Define an independent epsilon family by the actual Bernoulli undepletion law:

    Gtilde(x,epsilon)
      =(1-epsilon) sum_(q>=0)
        gammahat_q P_q(x) A(x-q)/(1-epsilon 4^q).

At epsilon=0 it is Ghat. At epsilon=2^(2r-1) it is the actual G_r.
All denominators are units for epsilon in 2 Z_2.

## Theorem

On the entire parameter disc `epsilon=2^24 eta`, `eta in Z_2`, define

    K_eta(Z)=2^-178 Gtilde(10202+2^15 Z,2^24 eta).

Then:

1. Every K_eta belongs to the same quadratic class as Khat, with odd quadratic
   coefficient. It has a unique critical point c(eta) in Z_2.
2. The critical value Phi(eta)=K_eta(c(eta)) is a bijective isometry of Z_2.
3. There is exactly one eta_* in Z_2 for which K_eta has a multiple root in
   this chart. That root is c(eta_*), and has multiplicity exactly two.
4. The actual Euler chart has a multiple root if and only if

       eta_* = 2^(2r-25).

5. The exact valuation identity is

       v2(Phi(eta))=v2(eta-eta_*),

   including infinity at equality. In particular v2(eta_*)=v2(Phi(0)).

Thus the resolved ambient family always contains one singular member on this
epsilon disc. Proving ambient smoothness or a unit derivative in epsilon cannot
by itself prove simplicity on the discrete Euler sheet.

## Proof

Set

    S(x)=sum_q 4^q gammahat_q P_q(x) A(x-q),
    W(x)=S(x)/2^154.

The q=0 term is `2^154 A`. The terms 1<=q<161 have scalar valuation at least
155. For q>=161 the scalar valuation is at least 322. Therefore

    W belongs to Z_2<x>,  W=A+2 R_W,  W=1 mod 2 coefficientwise.

Expand each rational undepletion factor exactly:

    (1-epsilon)/(1-epsilon 4^q)
      =1+epsilon(4^q-1)
         +epsilon^2 4^q(4^q-1)/(1-epsilon 4^q).

The last coefficient vanishes for q=0. For 1<=q<161 its normalized packet
valuation is at least 155. For q>=161 it is at least 322. Consequently

    Gtilde=(1-epsilon) Ghat + epsilon S + 2^155 epsilon^2 R_0(x,epsilon),

where R_0 is an integral restricted series jointly in x and epsilon on the
specified parameter disc. Termwise convergence follows from the original
restricted packet bounds and the additional powers of 4^q. After localization,

    K_eta=(1-2^24 eta) Khat
           +eta W(10202+2^15 Z)+2^25 eta^2 R_1(Z,eta).             (1)

Here R_1 is integral restricted. In fact R_1 is the substitution into an
integral series in x and eta, so its Z derivative is divisible by 2^15.
The same is true of W's Z derivative. Formula (1) proves integrality and the
quadratic class: the nonconstant coefficients of W after localization are
divisible by 2^15, and the last summand is divisible by 2^25.

Let `F_eta=K_eta'/2`. Each F_eta has the form

    constant + odd*Z + 2 Z^2 T_eta(Z),

and hence is a bijective isometry: its divided difference is odd. Binary
lifting gives its unique zero c(eta). From (1), for all eta,theta,Z,

    v2(F_eta(Z)-F_theta(Z)) >= v2(eta-theta)+14.                  (2)

The terms give bounds 24,14,and at least39 respectively after half
differentiation; these are uniform coefficientwise bounds. Evaluate (2) at
c(theta), and use the isometry of F_eta to obtain

    v2(c(eta)-c(theta)) >= v2(eta-theta)+14.                     (3)

At a fixed Z, (1) also gives

    K_eta(Z)-K_theta(Z)=(eta-theta)*unit,

because the quotient reduces to W=1 modulo two. At the critical point
c(theta), the exact Taylor expansion has no linear term, so

    v2(K_theta(c(eta))-K_theta(c(theta)))
        >=2 v2(c(eta)-c(theta)).                               (4)

Combining (3) and (4), this critical-point motion is strictly smaller in
2-adic norm than the fixed-Z parameter difference. The ultrametric inequality
therefore gives

    v2(Phi(eta)-Phi(theta))=v2(eta-theta).

The map is consequently an isometry. Modulo each 2^n it is injective, hence
surjective on the finite residue ring. Compatible lifting and completeness
give a unique eta_* with Phi(eta_*)=0.

Every K_eta has a unique critical point, so eta_* is exactly the unique
singular member. At that point its quadratic Taylor coefficient is odd:
the original odd quadratic coefficient stays odd under translation and the
4-divisible tail contributes an even correction. The multiplicity is two.
Substitution of the actual epsilon gives eta=2^(2r-25), proving (4) and (5).

## Consequences and remaining arithmetic gap

The earlier first-order correction now follows from an exact metric identity:

    v2(Phi(2^(2r-25))-Phi(0))=2r-25.

If the depleted critical value is zero, the actual one is nonzero. If its
valuation differs from 2r-25, the actual one is also nonzero. Only equality
of the normalized parameter with eta_* can produce a tangency.

This does not prove that eta_* is never a positive power of two, and the
Bernoulli formula alone has not supplied that missing assertion. The new
result does prove why merely resolving the nonunit direction cannot close
the problem: the singular locus is present and transverse, and the actual
Euler arithmetic must avoid it.

## Exact source elimination and its limitation

For q>=1 the exact cancellation is

    P_q(x) A(x-q)=P_(q-1)(x)*(9^(x-q+1)-1)/8.

Set D=(x+1)(2x+1) and, using the actual normalized scalars gamma_q, define

    U=gamma_0+D sum_(q>=1) 9^-q gamma_q P_(q-1),
    V=gamma_0+D sum_(q>=1) gamma_q P_(q-1).

Then exactly

    8 D G=9^(x+1) U-V.                                        (5)

On the deep chart D is a unit. A repeated root satisfies the two exact
equations

    9^(x+1) U=V,
    9^(x+1)(U'+log(9) U)=V'.

Elimination implies

    U V'-U' V-log(9) U V=0.                                  (6)

When U is nonzero, (5) and (6) are equivalent to the simultaneous value and
derivative equations. In general, when U=V=0, (6) is automatic and is
insufficient. On the actual terminal-161 chart that common-zero issue can be
excluded exactly, as follows.

The q=1 contribution to U or V has valuation153 on every even x, since D is
odd. The q=0 contribution has valuation154. Because the last lower minimizing
address is1, every 2<=q<161 has gamma_q of valuation at least154, and
P_(q-1)(x) contains x, so these terms have valuation at least155. Finally,
for q>=161 the normalized gamma_q is integral and

    v2(P_(q-1)(x))>=v2(160!)=158.

The inequality follows from x-underlined-160=160! binom(x,160), with the
binomial taking integral values on Z_2; the remaining odd factors and extra
integer factors are integral. Therefore

    v2(U(x))=v2(V(x))=153  for every even x.                   (7)

On the deep chart, the needed bounds also hold coefficientwise: its lower
packets have the divisibility just stated, and P_160 has coefficient content
159. Indeed the closest skeleton point is90, its separation exponent is7,
the other factors have total valuation
v2(90!)+v2(69!)=152, and x-90=2^7(79+2^8 Z). Extra factors beyond P_160
are integral. Thus U_0=2^-153 U and V_0=2^-153 V, restricted to this chart,
are restricted analytic units. Define

    F(x)=9^(x+1) U_0(x)/V_0(x)-1.

Then

    G(x)=2^150 [V_0(x)/D(x)] F(x),                          (8)

and on the deep chart G and F have exactly the same multiplicities. The
actual simultaneous-root obstruction is exactly

    F(x)=0,
    log9+U_0'(x)/U_0(x)-V_0'(x)/V_0(x)=0.                 (9)

No common-zero or extraneous denominator qualification remains in (9).
This normalized logarithmic derivative is the concrete Bernoulli-unit
quantity a closure proof must control. It has not been proved nonzero.

The same dominance applies to an address-one critical stratum with t>=5:
write k=2^t c and let nu=v2 binom(c-1,b) specify the critical scale. Then

    v2(k!)=k-1-s2(c-1)=delta+4+nu,

while gamma_1 has valuation delta, gamma_0 has valuation delta+(t-4),
and every other lower scalar has valuation at least delta+1. At a possible
multiple root x is even. Hence v2(U)=v2(V)=delta there. The case t=4 has
odd x and is not covered by this source-coordinate argument.

## Finite actual-Euler corroboration

`epsilon_certificate.py` constructs the joint epsilon/Z coefficient jet at
272 global bits for T=0 and T=718787533, with B=17659+2^18 T. Chart content
178 leaves94 coefficient bits and93 bits after half differentiation. The
computed eta degrees0 through4 suffice: every omitted degree m>=5 has
valuation at least26m-27>=103 after chart normalization.

The joint binary lift has exactly one successor at each of93 bits. The
eta_* valuations are respectively0 and30, matching the separately computed
depleted critical-value valuations. For each fixed integer input, direct
rational undepletion at eta=0,1,2,and the computed eta_* representative agrees
with every coefficient of the jet. This is an orthogonal rational identity
check using the same underlying Bernoulli evaluator, not an independent
implementation of that evaluator.

Authoritative execution: `run_272/results.json` and `run_272/manifest.json`.
The bounded runner completed successfully and the manifest validator passed.
These finite checks corroborate the theorem's normalization and arithmetic
implementation. The universal epsilon statement is supplied by the proof
above, and no universal Euler nonintersection follows from the finite run.
