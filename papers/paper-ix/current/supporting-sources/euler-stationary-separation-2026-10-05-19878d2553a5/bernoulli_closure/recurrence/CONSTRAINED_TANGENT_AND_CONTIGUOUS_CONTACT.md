# Actual Bernoulli tangent and contiguous contact

Base: `Euler-radix-audit-20261005`, archive SHA256
`d48a4386afa295176756f795b1a0abdd696df37a10ecba7a15b7f0ec7b69a7e6`.
The source checkpoint is immutable. This route uses the actual Bernoulli
recurrence and an independently rebuilt neighboring index. It does not
claim universal simplicity or nonvanishing of the actual critical value.

## 1. The constrained coefficient tangent

Write g(t)=sqrt(t)coth(sqrt(t))=sum a_n t^n and
beta_n=(1-2n)a_n. The exact Riccati equation with variable scale v is

    2t g_v'=g_v-g_v^2+v t,   g_v(0)=1.

Coefficient comparison gives 3a_1(v)=v and, for n>=2,

    (2n+1)a_n(v)=-sum_(i=1)^(n-1) a_i(v)a_(n-i)(v).

Induction proves the unique formal solution a_n(v)=v^n a_n(1), hence
beta_n(v)=v^n beta_n. In particular a first-order deformation preserving
both this equation and the prescribed beta_1=-1/3 is zero in every
coefficient. Allowing the scale to vary leaves exactly the tangent
dot(beta_n)=n beta_n dot(v). This is an actual coefficient constraint,
not a free change of packet units.

For a fixed admitted r=(17659+2^18 T)2^640-161, normalize the scaled
residual by its scaled beta_r. Its coefficients are then gamma_q v^q.
Take v=1+2^24 xi and define

    K(Z,xi)=2^-178 sum_(q>=0) gamma_q(1+2^24 xi)^q
                   P_q(x)A(x-q),  x=10202+2^15 Z.

The actual Euler member is xi=0. Put V=sum q gamma_q P_q A and
W=sum q(q-1)gamma_q P_q A. At xi=0,

    K_xi=2^-154 V,  K_(Z xi)=2^-139 V_x,
    K_(xi xi)=2^-130 W.                                  (1)

## 2. Exact nonzero tangent certificate on the actual chart

At the actual stationary point c, the following hold uniformly in every
admitted ordinary T:

    K_xi = 3 (mod8),
    K_(Z xi)/2^16 = 7 (mod8),
    K_(xi xi)/2^29 = 7 (mod8).                            (2)

Here are the packet computations, including the stationary cancellation.
The inherited actual units are gamma_0=2^154,
gamma_1/2^153=43 mod64, and gamma_161=7 mod8. In addition

    gamma_2/2^157=1 (mod8).                               (3)

To verify (3), put M=r+161, divisible by2^640. The odd parts of
(2r+1)...(2r+4) have product
(-321)(-5)(-319)(-159)=5 mod8 after removing the 2^7 factor.
The factor (2r+3)/(2r-1) is5 mod8. Both 2B_(2r+4) and 2B_(2r)
are5 mod8 by the Bernoulli midpoint congruence, so their ratio is1.
The exact gamma formula therefore gives5*5=1 mod8.

On the chart, x=10 mod16, P_1(x)/2=7 mod8,
A(x-1)=7 mod8, P_2(x)/2=7 mod8, and A(x-2)=1 mod8.
The source congruences follow coefficientwise from
A(X)=1+2X+12X^2+8X^3 mod16, which also gives A'(x)/2=1 mod8.
Thus packet1 uniquely gives V/2^154=3 mod8. Packet2 uniquely gives
W/2^159=7 mod8. Packets q>=4 have scalar bound149+3q below161;
packet3 gains v2(P_3(x))=4. Upper packets have the factorial and carry
bounds recorded in the base, so they cannot affect either displayed unit.

For the mixed derivative, one must use the actual stationary equation:

    V_x=G_x+sum(q-1)gamma_q(P_q A(x-q))_x.

At c, G_x=0. Packet0 contributes -2^154 A'(x), where
A'(x)/2=1 mod8 on this chart. Packet2 contributes 2^157 times an odd
unit. Packet161 acquires the extra factor160 and has valuation at least158.
Packet162 has scalar valuation4 and derivative valuation153 on this chart:
the nearest skeleton point is90, with factorial valuation
v2(90!)+v2(71!)=153, and separation exponent7. Since q-1=161 is odd,
packet162 supplies a second 2^157 times an odd unit. Upper packets q>=163
have scalar valuation at least7 and factorial derivative valuation at least152,
until the remote carry range where factorial bounds alone are sufficient.
Packet3 in the lower part has valuation at least159 after q-1. Consequently

    V_x/2^155 = -1+4+4 = 7 (mod8).

Together these give (2). Treating packet1 alone as dominant in V_x would
give the wrong answer: its valuation153 derivative is cancelled by the
leading upper packet in the stationary equation.

The inherited quadratic chart has K_ZZ/2=1 mod8. The implicit critical
point c(xi) therefore satisfies

    v2(c'(0))=15,  c'(0)/2^15=1 mod8.

For Phi(xi)=K(c(xi),xi), the exact Schur-complement formula gives

    Phi'(0)=3 mod8,
    Phi''(0)=K_(xi xi)-K_(Z xi)^2/K_ZZ,
    v2(Phi''(0))=29,  Phi''(0)/2^29=3 mod8.               (4)

The direct second derivative has valuation29 and the motion correction
has valuation31. They do not cancel the leading term. Formula (4) is a
nonzero certificate for the actual recurrence-compatible normal direction.
Fixing beta_1 sets that direction to zero; it supplies no equation asserting
that Phi'(0) vanishes, nor that Phi(0) is nonzero. Thus the coefficient
rigidity and normal certificate alone do not close the target.

## 3. Exact adjacent-index contact, including its remaining scalar

The neighbor r+1=M-160 has regular terminal160 and normalization -153.
Put u=gamma_1/2^153, a unit. Exact splitting at the first packet gives

    G_r(x)=2^154 A(x)+u P_1(x) G_(r+1)(x-1).              (5)

Write F(x)=G_(r+1)(x-1). On the current chart v2(P_1)=1,
v2(F)=153, and at a stationary point v2(F')=152. These follow both from
the neighboring regular chamber and directly from (5), since
v2(G_r)>=178 and v2(A')=1. In particular the neighbor is nonzero at
every possible double contact. Its root simplicity is not a contact bound.

The relevant logarithmic mismatch is

    L(x)=A'(x)/A(x)-P_1'(x)/P_1(x)-F'(x)/F(x).

At any stationary point of G_r, exact differentiation of (5) gives

    L(x)=[A'(x)/A(x)] G_r(x)/(G_r(x)-2^154 A(x)).          (6)

The denominator has valuation154 and is nonzero on this chart. Thus

    v2(L(c))=25+v2(Phi(0)),                              (7)

with infinity on both sides if the critical value vanishes. This identifies
exactly why the proposed neighboring contact inequality did not produce
an independent invariant: its unknown valuation is the original critical
valuation plus25. Its leading value and derivative units already match
the prescribed double-contact data.

The checker independently reconstructs the actual r+1 packets, rather than
defining the neighbor by (5). It verifies (5)-(7) and the nonzero tangent
certificates at three previously fixed actual indices. No parameter search
or additional candidate digits are performed.

## 4. First failed implication and remaining obligation

The first tentative derivative estimate treated the q=1 tangent derivative
as dominant. It failed because the actual stationary equation forces a
same-order upper-packet cancellation. Keeping that equation gives the
correct mixed valuation16 and curvature valuation29 in (2)-(4).
A second preliminary mod8 calculation omitted packet162; retaining it
changes the mixed unit from3 to7 and the center-motion unit from5 to1.
Both corrections were made before the recorded run. The successful
`DEVELOPMENT_CHECK.json` is exploratory; the current recorded evidence
is the separately pinned run below.

The attempted adjacent-index closure then fails at an exact mathematical
implication: regularity of the neighbor does not give a strict bound on
L(c). Equation (6) retains precisely the unknown critical value. No value
has been set to zero because a finite residue vanished.

What remains is a genuinely new constraint forcing Phi(0)!=0 for the
actual fixed beta_1 and ordinary index r. The Riccati-compatible tangent
certificate does not provide that equation, and the contiguous logarithmic
contact is not an independent exclusion test. No Lean compilation was run.

## 5. Bounded reconstruction and precision

The checker uses Python 3.12.14 and exact integers and fractions. It checks
the coefficient recurrence through degree24 at three rational scales, then
reconstructs actual packets at the previously fixed T values0,718787533,
and22831001499602523078606181325. This is not a parameter search.
Their critical-value valuations are respectively0,30,91; their adjacent
logarithmic-contact valuations are25,55,116. Each has the units in (2)-(4).
The neighboring packets are rebuilt from Bernoulli ratios and their true
terminal160 and normalization-153 are checked independently.

All global computations use modulus2^320. For r, the scalar cutoff is
Q=floor((320+s2(r)-156)/3); every omitted coefficient has valuation at
least320 because v2(gamma_q)=3q+s2(r+q)-s2(r)+154 and s2(r+q)>=1.
Integer weights q and q(q-1) preserve this omission bound. For r+1 the
analogous cutoff is floor((320+s2(r+1)-155)/3). The inherited local
assembly retains all affine degrees through floor(319/15). Assertions
check divisibility before all normalization shifts used for the jets.

K is known modulo2^142. Solving K_Z/2 gives c modulo2^141, hence the
physical x error has valuation at least156. The normal-direction output
is restricted to100 bits; adjacent ratios are restricted to140 bits.
The critical-value center-substitution error has valuation at least282
in K because the first derivative vanishes at the true center.
For V, V_x has valuation155 at that center, so V_Z has valuation170;
the resulting value error after division by2^154 is at least157 bits.
The general second-derivative factorial bound gives V_ZZ valuation at
least174; thus substitution in V_Z retains at least161 normalized bits.
For W_Z the same first-derivative bound gives valuation at least171,
so W/2^130 retains at least182 bits under center substitution. These
exceed the stated100-bit output. K_ZZ is computed to120 bits and its
center-substitution error also exceeds that precision.

For the neighbor, its value has derivative valuation152 and center error
156, retaining at least155 bits after normalization by2^153. Its second
derivative has valuation at least144: for upper indices160<=q<=255 use
v2(q!)-2 floor(log2 q)>=144, and later factorial bounds are stronger;
the lower packet bounds are stronger as well. The derivative therefore
retains at least148 bits after normalization by2^152. Computing it from
the affine Z derivative loses15 global bits, leaving305, which still
exceeds the needed precision. Consequently140-bit adjacent-ratio
comparisons refer to the true stationary point, not just its representative.

The derivative factorial bound used here follows by differentiating
the binomial generating series j times: each derivative inserts a factor
log(1+z), whose coefficient denominators have valuation at most
floor(log2 q). Thus
v2((d/dx)^j (x)_fallq)>=v2(q!)-j floor(log2 q), and multiplication by
the integral odd-factor polynomial and by A preserves this lower bound.

Recorded evidence: `frozen_run/manifest.json` and
`frozen_run/results.json`, governed by `contract.json`. Bounded output
corroborates the displayed identities; the uniform statements in Sections1-3
depend on the explicit arithmetic derivations, not on those three cases.

## 6. Inherited source locators

- `shifted_obstruction/weighted/RECIPROCAL_CUTOFF_AND_ACTUAL_COMMUTATOR.md`,
  Section3, gives the actual normalized packet bounds, gamma161 unit,
  and factorial derivative estimates.
- `coupled/critical_dynamics/COUPLED_CANCELLATION_DYNAMICS.md`,
  Section2, gives gamma1/2^153=43 mod64 and the source expansion.
- `radix_closure/TARGET.md` fixes the actual arithmetic target and chart.
- The recorded run pins `fast_parameter_certificate.py`,
  `build_parameter_certificate.py`, and their imported
  `check_critical_value.py`, in addition to this proof and the new checker.
