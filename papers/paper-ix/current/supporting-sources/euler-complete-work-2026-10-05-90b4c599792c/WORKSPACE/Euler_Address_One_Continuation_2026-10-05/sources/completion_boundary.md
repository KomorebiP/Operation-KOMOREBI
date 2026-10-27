# Euler closure attempt: exact preparation and the all-precision parameter boundary

## Status

This is a mathematical derivation and a reproducible exact/modular audit. It is
NOT a new Lean release. No Lean compiler was run in this continuation, and no
new declaration count is claimed. The original v26 code and fixed-input evidence
are retained unchanged as the numerical source. Universal Euler simplicity is
not proved here.

Two substantive conclusions:

1. A digitwise construction gives the exact fixed-degree Weierstrass polynomial,
   not the discriminant of an increasing-degree truncation. Its modular
   implementation passes planted-factor tests and actual Euler-core checks.
2. The proposed all-precision Mahler interpolation of the **actual undepleted**
   critical values has an obstruction. The raw Bernoulli units are discontinuous
   along natural-number sequences converging 2-adically to a fixed index. The
   same defect survives the constructed terminal-161 deep critical value, under
   the inherited fixed-input quadratic chart certificate.

The latter does not refute Euler simplicity. It refutes an attempted route that
identified a finite-precision depleted model with the actual arithmetic family
at arbitrary precision.

## 1. Exact fixed-degree preparation

Let A=Z_2<X> with its Gauss norm. Suppose f is integral restricted, and its last
odd coefficient has index d. Then its full reduction pbar in F_2[X] is monic of
degree d. Choose its 0/1 lift W_1 and put U_1=1.

Assume f-U_k W_k belongs to 2^k A, W_k is monic of degree d, and U_k reduces to 1.
The reduction

    e_k = (f-U_k W_k)/2^k mod 2

is a finite polynomial because the quotient is restricted. Divide in F_2[X]:

    e_k = q_k pbar + r_k,       deg(r_k)<d.

Choose 0/1 coefficient lifts and set

    U_(k+1)=U_k+2^k q_k,
    W_(k+1)=W_k+2^k r_k.

Modulo 2^(k+1), the product correction is

    2^k(q_k W_k+U_k r_k) = 2^k(q_k pbar+r_k).

Thus the invariant holds one bit deeper. Each increment has Gauss norm at most
2^-k, so U_k converges in A and W_k converges to a degree-d monic polynomial W.
The limit satisfies f=UW, and U=1+2V is an analytic unit by the convergent
geometric series. To prove uniqueness, reduce the difference between two
factorizations at its first unequal bit. It has the form pbar*q+r=0 with deg r<d;
Euclidean division forces q=r=0. Induction proves uniqueness.

This proves both existence and precision stability: a COMPLETE coefficient
certificate f mod 2^N determines W mod 2^N. Merely checking values at finitely
many points does not suffice.

The construction is a specialized presentation of classical 2-adic Weierstrass
preparation. It is not a novelty claim for that theorem.

### Multiple-root obstruction

At a zero alpha of W,

    f'(alpha)=U(alpha) W'(alpha).

Hence analytic multiplicities agree. For degree 2 or 3, a repeated irreducible
factor of degree at least 2 is impossible: its square would already have degree
at least 4. Therefore, in these degrees,

    Disc(W)=0  iff  f has a repeated root in Z_2.

Monicity and integral coefficients place a Q_2 root in Z_2. For larger degrees,
Disc(W)!=0 is still sufficient for all roots to be simple, but Disc(W)=0 may
only detect a repeated root in an extension. Dyadic simplicity must not be
identified with algebraic squarefreeness in those larger degrees.

## 2. Fixed-input execution

The saved v26 cubic on x=90+128Y has content 162 and 62 coefficient bits. Its
unique prepared cubic has discriminant of valuation 18. A fresh reconstruction
at global precision 272 supplies 110 cubic coefficient bits and agrees with
all 62 previously available bits of the prepared polynomial and discriminant.

Modulo 2^24 the prepared cubic is

    W(Y)=Y^3+6944102 Y^2+8014313 Y+7544708.

Its discriminant modulo 2^24 is 15466496=2^18*59. In particular its valuation is
exactly 18. The full 110-bit record is in prepared_cubic_110.json.

On the deeper chart x=10202+2^15 Z the removed content is 178. Fresh 272-bit
original-index calculations give:

    T=0:          local precision 94, critical-value valuation 0,
                  prepared quadratic discriminant valuation 2, odd part 3 mod 8.
    T=718787533:  local precision 94, critical-value valuation 30,
                  prepared quadratic discriminant valuation 32, odd part 5 mod 8.

Both discriminants are nonzero. These fixed deep discs are in fact root-free
by the dyadic square criterion. This does NOT classify all multipliers in the
progression B=17659+2^18 T.

The preparation implementation was additionally tested on 240 random planted
unit-times-monic factorizations and 20 planted repeated-root controls. It retained
the repeated factors rather than turning them into spurious simple factors.

## 3. The finite Mahler pattern reproduces

Reconstruct the actual deep quadratic for T=0,...,6 at global precision 256.
Let Phi(T) be its critical value after dividing the original G by 2^178.
The local values are known modulo 2^78. Exact forward differences give

    v_2(Delta^n Phi(0)):  0, 0, 15, 30, 45, 60, 75   (n=0,...,6).

These are finite, resolved valuations. They do not prove an all-order Mahler
coefficient bound or a continuous parameter extension.

An additional logical distinction: even a proved isometry does not imply the
specific slope 15(n-1). For example T+8*binom(T,4) is an isometry, because the
nonlinear divided difference is even, but its fourth Mahler coefficient has
valuation 3, not 45.

## 4. An exact continuity obstruction already appears in the source coefficients

Use B_1=-1/2. Define the continuous function

    D(z)=sum_(k>=0) 2^k B_k binom(2z,k),       z in Z_2.

For k>=2 nonzero Bernoulli terms have v_2(2^k B_k)=k-1. Binomial polynomials
are Z_2-valued. Thus this sum converges uniformly. Bernoulli polynomial
expansion and duplication give, at nonnegative integers m,

    D(m)=(2-2^(2m)) B_(2m)
        =(1-2^(2m-1))*2B_(2m),              m>=1,
    D(0)=1.

All D(m) are units, and continuity/density show D(z) is a unit on Z_2.

Fix m>=1 and take m_h=m+2^h. Then m_h tends to m 2-adically while tending to
infinity in the ordinary sense. Hence

    2B_(2m_h) = D(m_h)/(1-2^(2m_h-1))  -->  D(m),

not to 2B_(2m). The difference at the fixed index is exactly

    2B_(2m)-D(m)=2^(2m-1)*2B_(2m),

whose valuation is 2m-1. Therefore the ordinary Bernoulli-unit sequence has no
continuous extension agreeing at every positive integer index.

The source definition and duplication identities are classical. This limit
calculation explains why the depleted model can agree through a vast number
of digits without agreeing exactly with the original arithmetic.

### Small exact/modular control

At m=3, 2B_6=1/21 and D(3)=-31/21. Their difference is 32/21, of valuation 5.
At precision 40, h=4,8,12,16,24,36 give distances to 1/21 of valuation exactly 5;
the distances to -31/21 have valuations 6,10,14,18,26,38. The infinite conclusion
comes from the preceding proof, not this finite table.

## 5. How the defect reaches the terminal-161 critical value

This section is a mathematical consequence of the inherited packet construction,
source-unit theorem, and the fixed-input quadratic chart certificate. It has
NOT been translated into Lean in this continuation. The large original-index
coefficient certificate is supplied by exact/modular reconstruction, not a new
kernel arithmetic proof.

Fix

    r0=17659*2^640-161,   mu=-154,  E=2r0-1,  epsilon=2^E.

Let gamma_q be the actual normalized packet scalar and let gammahat_q be its
depleted counterpart. With A the integral analytic Euler source, define

    Ghat(x)=sum_q gammahat_q P_q(x) A(x-q),
    S(x)=sum_q 4^q gammahat_q P_q(x) A(x-q).

The scalar undepletion identity gives the exact restricted-series expansion

    G=Ghat+epsilon*(S-Ghat)+epsilon^2 R_G,

where R_G is integral restricted. Indeed the remainder weight is

    4^q(4^q-1)/(1-epsilon*4^q),

which is integral; geometric packet bounds justify the sums. All normalized
packet scalars are integral and have the same valuations before/after depletion.

For this terminal label:

    v_2(gammahat_0)=154,
    v_2(gammahat_q)>=153 for 1<=q<161,
    v_2(gammahat_q)>=0   for q>=161.

The first two follow from the finite lower carry minimum -1; the third from
the actual global carry minimum. Consequently

    S = 2^154 A + 2^155 R_S,    R_S integral restricted.

At every dyadic argument, v_2(S)=154.

On x=10202+2^15 Z put

    K=2^-178 G(x),    Khat=2^-178 Ghat(x),
    D_K=2^-178(S-Ghat)(x).

The actual K is in the quadratic class a+2lZ+uZ^2+4Z^3R with u a unit. Since
K-Khat has Gauss valuation at least E-178, Khat is in the same class. In
particular Ghat has value valuation at least 178 throughout the deep disc, so

    v_2(D_K(z))=-24  for every z in Z_2.

Let c and chat be the unique critical points of K and Khat. Their integral half
derivatives are isometries. Gauss control gives

    v_2(c-chat)>=E-179.

The exact stationary quadratic estimate then gives

    v_2(Khat(c)-Khat(chat))>=2E-358.

Since D_K is 2^-178 times an integral restricted function, its divided difference
has valuation at least -178. Also R_G/2^178 is bounded below by -178. Therefore

    K(c)-Khat(chat) = epsilon*D_K(chat) + R,
    v_2(R)>=2E-358.

The leading term has valuation E-24, and E>334. Thus the strict margin proves

    v_2(K(c)-Khat(chat))=E-24=2r0-25.

This is a NONZERO exact undepletion correction after critical-point motion.
The integer E is enormous, but the proof does not compute E digits.

Two useful corollaries are immediate. If the depleted critical value is exactly
zero, the actual critical value is nonzero. If the actual critical value is
zero, the depleted value must be nonzero with valuation exactly 2r0-25. The
same argument applies to any other actual member for which the terminal-161
carry bounds and this normalized deep quadratic chart hold. It does not silently
assert those chart hypotheses for every integer in an arithmetic progression.


### The sparse high-bit parameter limit

Take T_h=2^h, so r_h=r0+2^(658+h). The bit counts are 646 and 647 respectively;
the carry cutoff is 215 for both. For q<=215 the added high bit is disjoint
from r0+q, so their entire carry tables coincide. Hence every r_h still has
terminal label 161 and mu=-154.

For each fixed q, the actual packet scalar at r_h tends to the depleted scalar
at r0: the Bernoulli part tends to D, and the finite factorial ratios are
continuous at the positive index r0. The packet tails converge uniformly in
Gauss norm because the bit counts along this sequence are bounded. Therefore

    G_(r_h) --> Ghat_(r0)

on the whole argument disc. On the deep disc the critical points and critical
values converge as well, by the half-derivative isometry.

Thus the actual normalized critical values satisfy

    lim_(h->infinity) Phi(T_h)=Khat(chat) != K(c)=Phi(0).

The discrepancy has exact valuation 2r0-25. In particular the actual critical
values cannot be the restriction of a continuous function on Z_2, even when
only this admissible subsequence and T=0 are requested. An all-order decaying
Mahler expansion for the actual family is therefore not a valid target.

This does not rule out useful analytic depleted/finite-precision models. Those
models must be kept separate from the physical integer-index values, with the
undepletion correction retained.

## 6. What remains of a universal closure argument

Exact preparation finishes the analytic reduction, not the arithmetic
nonvanishing. A nonzero prepared discriminant can be certified at finite
precision. A zero residue cannot certify an exact zero.

Even a genuine depleted parameter isometry with one root tau would not prove
that no admissible ordinary integer equals tau. Nor would it prove that an
actual undepletion correction cannot cancel a nonzero depleted critical value.
The latter requires a strict relative valuation margin.

For general terminal labels, the small-degree collision theorem still assumes
simple lower residue roots. It must not be extended to all labels by omitting
that hypothesis. Exact global preparation exists at degree j, but algebraic
squarefreeness and dyadic simplicity are distinct once j>=4.

There is an unconditional structural consequence of preparation: each fixed
nonzero restricted G_r admits a finite valuation atlas with local root laws
c+m*v_2(x-alpha), m a positive finite multiplicity. The sum of root multiplicities
is at most j_r. On the root-free compact complement the valuation is locally
constant and has a finite clopen partition. This is an existence theorem;
it is not a terminating finite-precision decision procedure for exact multiple
roots, and it does not prove m=1.

The original universal-simplicity target remains precisely the assertion that
all those multiplicities are one.

## 7. Reproducibility and failures

- prepare_probe.py: exact binary preparation; 260 planted controls; saved core.
- fresh_euler_tests.py: original-index packet reconstruction, quadratic critical
  lifting and fixed-degree preparation.
- continuity_checks.py: small Bernoulli control and exact finite carry checks.
- verify_results.py: replay all retained factorization and cross-precision checks.
- Fresh original-index cases: T=0,...,6 at 256 global bits; T=0 and 718787533 at
  272 bits; full cubic at T=0 also reconstructed at 272 global bits.
- The independent preparation algorithm is separate from v26 numerical code.
  Bernoulli evaluation and the underlying Euler source routine are shared with
  v26; these are not wholly independent Euler implementations.
- One seven-input batch hit its 45-second execution limit after completing and
  saving T=0,1,2,3. The remaining T=4,5,6 were rerun successfully in a separate
  batch. No interrupted run is counted as completed.
- No Lean run was attempted. These results must not be described as newly
  kernel-checked declarations.

Reference inputs: the v26 archive and its retained checks/check_critical_value.py;
DLMF 24.4 (Bernoulli expansion, duplication and midpoint value), DLMF 24.10
(denominator valuation); Keith Conrad, Hensel's Lemma, Remark 8.3 (analytic-unit
Weierstrass factorization). The digitwise argument above is included explicitly.
