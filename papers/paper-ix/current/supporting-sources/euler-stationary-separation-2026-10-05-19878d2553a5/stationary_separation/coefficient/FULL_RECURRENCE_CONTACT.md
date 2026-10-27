# Full Bernoulli recurrence at actual double contact

Base: Euler-Bernoulli-structure-20261005, archive SHA256
b1dd12d9e0904b7d9a0b999e961fd1b12b4e3afde71995da4064d7849cdfacf7.
All ordinary parameters have r=(17659+2^18 T)2^640-161, T>=0, with
true terminal161. No prior proof is modified and no parameter digits are added.

This continuation retains the whole prescribed Bernoulli recurrence, its
finite prefix defect, and ordinary derivatives after source transformation.
It proves fixed nonzero valuations for a genuine nonlinear tail square and
for both forcing jets. Neither forces a nonzero stationary value: the exact
contact equations balance the forcing against an index derivative, which
ordinary stationarity does not annihilate.

## 1. The beta-only differential identity and its exact cutoff

Put theta=t d/dt and

    g(t)=sqrt(t)coth(sqrt(t)),
    f(t)=(sqrt(t)/sinh(sqrt(t)))^2=sum beta_n t^n.

The actual identities theta f=f(1-g) and g^2=f+t give

    (theta f-f)^2-t f^2-f^3=0.                           (1)

This uses every prescribed coefficient; beta_1=-1/3 fixes the unique
Riccati solution. Write

    p=sum_(n<r) beta_n t^n,   f=p+t^r B,
    a=theta p-p,             W=(r-1)B+theta B,
    F_r=t^-r[a^2-t p^2-p^3].

All coefficients below degree r in the numerator defining F_r vanish by
(1). Thus F_r is an actual finite rational polynomial. Exact expansion,
without discarding any cross-boundary coefficient, gives

    F_r+2aW-(2tp+3p^2)B
        +t^r[W^2-(t+3p)B^2]-t^(2r)B^3=0.               (2)

Set A_p=2a and C_p=2(r-1)a-2tp-3p^2. The linear part is
A_p theta B+C_p B. Since r>=3 and beta_2=1/15,

    A_p=-2+(2/15)t^2+O(t^3),
    C_p=-(2r+1)+((2r-3)/15)t^2+O(t^3).                  (3)

Both degree-one coefficients cancel exactly. All coefficients in these
polynomials are dyadic integers. The first nonconstant coefficient of C_p
is a unit, but it acts on a shifted tail and is not a local forcing term.

## 2. Transfer with the complete source and ordinary derivative

For a coefficient kernel k, define

    T_k h(x)=sum_j 8^j k_j P_j(x)h(x-j),
    P_j(x)=product_(0<=i<j)(x-i)(2x-2i-1),
    A(x)=(9^(x+1)-1)/(8(x+1)(2x+1)).

The exact product law is T_k T_l=T_(kl), by
P_i(x)P_j(x-i)=P_(i+j)(x). Products are operator compositions.
They are not products of values of T_k A. No half-shifted source value
or ordinary differential closure is required below.

Let sigma=2^154/beta_r and put

    H=sigma T_B,       G=HA=sum_q gamma_q P_q(x)A(x-q),
    V=sigma T_(theta B)A=sum_q q gamma_q P_q(x)A(x-q),
    E=sigma T_(F_r)A,
    R=T_(A_p+2)V+T_(C_p+2r+1)G,
    N=sigma T_( t^r[W^2-(t+3p)B^2]-t^(2r)B^3 )A.

Equation (2) is precisely

    E=2V+(2r+1)G-R-N.                                    (4)

Ordinary differentiation gives the equally exact second equation

    E_x=2V_x+(2r+1)G_x-R_x-N_x.                          (5)

In particular, differentiating a summand of T_k h means

    8^j k_j[P_j'(x)h(x-j)+P_j(x)h'(x-j)].                (6)

No commutator term in (6) has been omitted. The multiplier q defining V
is coefficient differentiation; it is not differentiation in x.

## 3. Uniform actual forcing jets on the terminal chart

Use x=10202+2^15 Z, Z in Z_2. The inherited actual packet bounds are

    gamma_0=2^154, v2(gamma_1)=153,
    gamma_1/2^153=43 mod64, v2(gamma_2)=157,
    v2(gamma_q)>=149+3q for3<=q<161,
    v2(gamma_161)=0,
    v2(gamma_(161+t))=3t+s2(t) for1<=t<2^640.

Every gamma_q is integral, by the true-terminal hypothesis. The established
source congruences on this chart imply, uniformly,

    V/2^154=3 mod8.                                      (7)

At any stationary point of G, retaining the upper-packet cancellation,

    V_x/2^155=7 mod8.                                    (8)

These are the actual packet evaluations proved in
`bernoulli_closure/recurrence/CONSTRAINED_TANGENT_AND_CONTIGUOUS_CONTACT.md`.
In particular (8) is not the incorrect estimate from packet1 alone.

Here are bounds sufficient to control every remainder in (4)-(5).
On all of Z_2,

    G,V in2^153 Z_2,      G_x,V_x in2^151 Z_2.            (9)

For the upper packets this follows from
v2(P_q)>=v2(q!) and v2(P_q')>=v2(q!)-floor(log2 q): at q=161
the derivative lower bound is158-7=151. The following coefficients gain
at least4 before the next carry. Beyond that carry, factorial divisibility
alone is enormous. The finitely many lower packets have stronger bounds.
Source A is integral restricted, a unit, and A' is even.

Both operators in R start at degree2, by (3). Their coefficients are
integral. Thus (9) gives R in2^159 pointwise. Applying the full rule (6),
the degree2 term has derivative valuation at least
6+min(153,v2(P_2)+151)=158, because v2(P_2(x))=1 on the chart.
Every degree j>=3 contributes at least3j+151>=160. Consequently

    v2(R)>=159,        v2(R_x)>=158.                    (10)

For N, put lambda=sigma^-1=beta_r/2^154. Its valuation is positive for
every admitted r (the final640 binary digits of r already supply more
than154 ones). Normalize B and W by sigma inside (2). All resulting
coefficient kernels have integral coefficients after the8^q weighting.
The quadratic term then has factor lambda 8^r P_r(x), and the cubic
term factor lambda^2 8^(2r)P_(2r)(x). Their ordinary derivatives are
integral after the displayed scalars are removed, since differentiation
preserves integrality of the restricted series and of P_r. In particular,

    v2(N),v2(N_x)>=3r>159.                               (11)

Since G is coefficientwise divisible by2^178 on the chart, equations
(4), (7), and (10)-(11) prove the actual uniform forcing theorem

    E/2^155=3 mod8.                                      (12)

At any stationary point, equations (5), (8), and (10)-(11) also prove

    v2(E_x)=156,       E_x/2^156=3 mod4.                  (13)

The derivative was not discarded: its forcing and index derivative have
matching, strictly determined nonzero valuations.

## 4. The genuine nonlinear tail square has its own fixed unit

The source evaluation H^2 A is an actual prescribed nonlinear quantity.
Write delta_q=sum_(i+j=q)gamma_i gamma_j. Operator composition gives

    H^2 A=sum_q delta_q P_q(x)A(x-q).

On the entire terminal chart,

    (H^2 A)/2^307=5 mod8,      v2((H^2 A)_x)=306.         (14)

Here is a direct proof including the infinite tail. The first coefficient
valuations are delta_0:308, delta_1:308, delta_2:306. In delta_2 the
summand gamma_1^2 is the unique leading term; 2gamma_0 gamma_2 has
valuation312. Since P_1 and P_2 both have valuation1, packet2 uniquely
has value valuation307. Modulo2^310, the normalized contributions of
packets0,1,2 are respectively2,4,7; their sum is5 modulo8.
This uses A(x)=1 mod4, P_1(x)/2=7 mod8, A(x-1)=7 mod8,
P_2(x)/2=7 mod8, A(x-2)=1 mod8, and gamma_1/2^153=3 mod8.

For3<=q<=160, the only exceptional lower convolution is q=3, whose
coefficient valuation is at least311 and whose P_3 valuation is4.
For q>=4 in this lower range the coefficient valuation is at least312
and P_q valuation at least4. At q=161,162 the coefficient valuations
are155,154 and the packet valuations are160,160. For163<=q<=321,
a mixed lower/upper term has coefficient valuation at least158, while
P_q has valuation at least163. Lower/lower terms are more divisible.
For q>=322, all delta_q are integral and v2(P_q)>=v2(q!)>=319.
Thus every q>=3 has value valuation at least314, as required.

For derivatives, packet2 has exact valuation306 because P_2' is odd.
Packets0,1 have valuations at least309,308. The q=3,...,160 derivative
terms have valuations at least311; at q=161,162 they have valuations
at least308,307, using the unique nearest factor of valuation7.
For163<=q<=321 the factorial derivative bound gives at least158+152=310.
For q>=322 it gives at leastv2(322!)-floor(log2 322)=319-8=311. Derivatives
of A have stronger bounds. Packet2 therefore uniquely gives valuation306.

This is not a substitute for G^2. Indeed G^2 is divisible by2^356 on
the chart, whereas H^2 A has exact valuation307. The difference is already
visible on the actual prescribed coefficient family; no free perturbation
or generic analytic countermodel is used in (14).

## 5. Exact outcome at double contact

If an actual double contact G=G_x=0 existed, the full equations would read

    E=2V-R-N,
    E_x=2V_x-R_x-N_x.                                    (15)

The proven forcing units (12)-(13) agree with (15). They do not contradict
it. The first forcing has valuation155 and is balanced by 2V; the second
has valuation156 and is balanced by2V_x. Treating stationarity as V=0 or
V_x=0 would replace ordinary differentiation by coefficient differentiation
and contradict the actual unit calculations (7)-(8).

Likewise, replacing H^2 A by G^2 would discard the actual nonzero term
(14). The finite prefix defect and its ordinary derivative retain precisely
the nonlocal index jets needed for the complete recurrence. This explains
why the previous nonzero scale tangent did not exclude the fixed Euler
member, and why adjacent-cutoff logarithmic mismatch merely retained the
unknown critical scalar. No rational height or local resultant estimate is
inferred from the infinite source-transformed equation.

The universal nonvanishing target remains open. A further argument must
control a combination of the actual shifted terms and finite prefix defect
that is independent of the unknown stationary scalar. The fixed units
proved here do not provide such a combination: their cancellation is
explicit in (15). This rules out the specified local reduction of the full
cubic, not every possible use of the prescribed recurrence.

## 6. Evidence and development boundary

The companion checker verifies (1)-(3) and the complete finite-cutoff identity
with exact rational arithmetic at small ordinary cutoffs, then checks the
actual square and forcing-jet estimates at the three already fixed controls.
The forcing is evaluated through the proved identity (4); it is not presented
as an independent expansion of a polynomial of astronomical degree.
Uniform statements above have separate valuation proofs, not extrapolations
from those controls. No new multiplier digits or approximation ranks occur.

The run uses384 global bits and lifts the critical Z to205 bits, hence x
to220 bits. Reported value and derivative valuations are below311. For G,V
the factorial argument gives global second derivatives divisible by2^144.
For H^2 A the same argument gives second derivative divisibility at least
2^290 (the mixed range starts at q=161, and the upper/upper range at322).
Thus center substitution changes G_x,V_x by multiples of2^364 and the
square derivative by multiples of2^510. The weaker global first derivative
bounds suffice for the reported forcing values. These errors exceed every
reported valuation and unit precision; no exact center is inferred from a
finite residue. Coefficients past the scalar cutoff or degree25 in the local
variable vanish at the stated global precision. Kernels of degree at least
129 in R carry8^129, so are also omitted only with a proved precision bound.
